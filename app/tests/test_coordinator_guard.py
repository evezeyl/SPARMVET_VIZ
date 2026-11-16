"""The hook `.claude/hooks/coordinator_guard.py` keeps a coordinator session to its role.

The first group pins the rules that existed before the decision rule (edits, Bash, Agent models, who is affected):
they must stay as they are. The second group tests the rule of M150 point 4: a builder or reviewer call is refused
when its brief has neither a "Decisions" block with numbers that exist in the ledger nor a NONE-CHECKED line whose path exists.
The hook runs as the harness runs it: a process that reads one JSON object on stdin; exit 2 is a refusal.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude/hooks/coordinator_guard.py"
SESSION = "11111111-2222-3333-4444-555555555555"

LEDGER = """# test ledger
D-0001 | 2026-11-05 | area | one | src | EVE | DECIDED | - | her words | L01
D-0002 | 2026-11-06 | area | two | src | AGENT | PROVISIONAL | - | words | L02
D-0003 | 2026-11-07 | area | three | src | NOT STATED | NOT-STATED | - | words | L03
"""


@pytest.fixture
def project(tmp_path):
    (tmp_path / "tmpAI" / "coordinator").mkdir(parents=True)
    (tmp_path / "tmpAI" / "coordinator" / SESSION).write_text("")
    (tmp_path / ".claude" / "knowledge").mkdir(parents=True)
    (tmp_path / ".claude" / "knowledge" / "decision_ledger.md").write_text(LEDGER)
    (tmp_path / "tmpAI" / "scout_report.md").write_text("no decision applies")
    return tmp_path


def run(project, tool, tool_input, session=SESSION, agent_id=None, raw=None):
    payload = {"session_id": session, "cwd": str(project), "tool_name": tool, "tool_input": tool_input}
    if agent_id:
        payload["agent_id"] = agent_id
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    result = subprocess.run([sys.executable, str(HOOK)], input=raw if raw is not None else json.dumps(payload),
                            capture_output=True, text=True, env=env)
    return result.returncode, result.stderr


def agent(project, kind, prompt="", **extra):
    return run(project, "Agent", {"subagent_type": kind, "prompt": prompt, **extra})


# --- rules that existed before the decision rule -------------------------------------------------

def test_edit_outside_tmpai_is_refused_and_inside_is_allowed(project):
    assert run(project, "Edit", {"file_path": str(project / "app" / "x.py")})[0] == 2
    assert run(project, "Write", {"file_path": str(project / "tmpAI" / "note.md")})[0] == 0


def test_bash_that_runs_work_or_writes_files_is_refused_and_git_is_allowed(project):
    assert run(project, "Bash", {"command": "./.venv/bin/python -m pytest app/tests"})[0] == 2
    assert run(project, "Bash", {"command": "sed -i 's/a/b/' app/x.py"})[0] == 2
    assert run(project, "Bash", {"command": "echo x > app/x.txt"})[0] == 2
    assert run(project, "Bash", {"command": "git status --short"})[0] == 0


def test_agent_models_the_coordinator_may_start(project):
    brief = "Decisions\n- D-0001: x"
    assert agent(project, "scout")[0] == 0
    assert agent(project, "scribe")[0] == 0
    assert agent(project, "builder", brief)[0] == 0
    assert agent(project, "general-purpose", model="haiku")[0] == 0
    assert agent(project, "general-purpose")[0] == 2          # would run on Fable
    assert agent(project, "fork", brief)[0] == 2
    assert agent(project, "builder", brief, model="opus")[0] == 2


def test_a_session_that_is_not_in_coordinator_mode_is_not_affected(project):
    assert run(project, "Edit", {"file_path": "app/x.py"}, session="another-session")[0] == 0
    assert run(project, "Agent", {"subagent_type": "builder", "prompt": "no block"}, session="another-session")[0] == 0
    assert run(project, "Agent", {"subagent_type": "reviewer", "prompt": "no block"}, session="")[0] == 0


def test_the_coordinator_session_itself_is_gated_where_another_session_is_not(project):
    assert agent(project, "builder", "no block at all")[0] == 2
    assert run(project, "Agent", {"subagent_type": "builder", "prompt": "no block at all"}, session="another-session")[0] == 0


def test_a_call_from_a_worker_passes_and_bad_input_fails_open(project):
    assert run(project, "Edit", {"file_path": "app/x.py"}, agent_id="a1")[0] == 0
    assert run(project, "Agent", {"subagent_type": "builder", "prompt": "no block"}, agent_id="a1")[0] == 0
    assert run(project, "Edit", {}, raw="not json")[0] == 0


# --- the decision rule (M150 point 4) -------------------------------------------------------------

GATED = ["builder", "builder-opus", "reviewer"]


@pytest.mark.parametrize("kind", GATED)
def test_a_brief_with_numbers_that_exist_is_allowed(project, kind):
    brief = 'Goal: do it.\n\nDecisions\n- D-0001: "her words"\n- D-0003: "other words"\n\nFiles: a.py'
    assert agent(project, kind, brief)[0] == 0


@pytest.mark.parametrize("heading", ["Decisions", "DECISIONS", "## Decisions", "**Decisions**", "Decisions:", "DECISIONS (this block quotes)"])
def test_the_heading_may_be_written_in_the_usual_ways(project, heading):
    assert agent(project, "builder", f"Task.\n{heading}\n- D-0001: words\n")[0] == 0


def test_numbers_may_follow_the_heading_on_its_own_line(project):
    assert agent(project, "reviewer", "Decisions: D-0001, D-0002")[0] == 0


@pytest.mark.parametrize("kind", GATED)
def test_a_number_that_does_not_exist_is_refused_and_named(project, kind):
    code, message = agent(project, kind, "Decisions\n- D-0001: ok\n- D-0777: not in the ledger\n")
    assert code == 2
    assert "D-0777" in message and "D-0001, " not in message.split("cites")[1].split("not in")[0]
    assert "NONE-CHECKED" in message and "decision_compliance.md" in message      # says how to write it


def test_a_malformed_number_is_refused(project):
    code, message = agent(project, "builder", "Decisions\n- D-12: short number\n")
    assert code == 2 and "D-12" in message


@pytest.mark.parametrize("kind", GATED)
def test_a_brief_with_no_block_is_refused(project, kind):
    code, message = agent(project, kind, "Please implement the thing. Files: a.py. See D-0001 in the ledger.")
    assert code == 2 and "no Decisions block" in message


def test_a_block_without_any_number_is_refused(project):
    code, message = agent(project, "builder", "Decisions\n- I think it is decided\n")
    assert code == 2 and "no decision number" in message


def test_a_number_outside_the_block_does_not_count(project):
    code, _ = agent(project, "builder", "Decisions\n\nD-0001 is mentioned after the block ended.")
    assert code == 2


@pytest.mark.parametrize("kind", GATED)
def test_none_checked_with_an_existing_file_is_allowed(project, kind):
    assert agent(project, kind, "Goal.\nNONE-CHECKED: tmpAI/scout_report.md\n")[0] == 0
    assert agent(project, kind, f"NONE-CHECKED: {project / 'tmpAI' / 'scout_report.md'}")[0] == 0


def test_none_checked_with_a_missing_file_is_refused_and_the_path_named(project):
    code, message = agent(project, "builder", "NONE-CHECKED: tmpAI/not_there.md")
    assert code == 2 and "tmpAI/not_there.md" in message and "not a file that exists" in message


def test_none_checked_with_a_directory_is_refused(project):
    assert agent(project, "builder", "NONE-CHECKED: tmpAI")[0] == 2


@pytest.mark.parametrize("kind", ["scout", "scribe"])
def test_scouts_and_scribes_need_no_block(project, kind):
    assert agent(project, kind, "find where X is used")[0] == 0


@pytest.mark.parametrize("kind", ["panel-scientist", "panel-architect", "panel-developer", "panel-user"])
def test_panel_agents_are_not_gated_by_this_rule(project, kind):
    assert agent(project, kind, "a question for the panel")[0] == 0


def test_a_missing_ledger_refuses_a_decisions_brief_but_not_none_checked(project):
    (project / ".claude" / "knowledge" / "decision_ledger.md").unlink()
    code, message = agent(project, "builder", "Decisions\n- D-0001: x")
    assert code == 2 and "does not exist" in message
    assert agent(project, "builder", "NONE-CHECKED: tmpAI/scout_report.md")[0] == 0


def test_a_malformed_ledger_refuses(project):
    (project / ".claude" / "knowledge" / "decision_ledger.md").write_text("D-0001 | too | few\n")
    code, message = agent(project, "builder", "Decisions\n- D-0001: x")
    assert code == 2 and "cannot be read" in message


def test_the_decision_rule_does_not_loosen_the_model_rule(project):
    brief = "Decisions\n- D-0001: x"
    assert agent(project, "builder", brief, model="opus")[0] == 2
    assert agent(project, "general-purpose", brief)[0] == 2
    assert agent(project, "reviewer", brief, model="sonnet")[0] == 0


def test_the_refusal_comes_from_the_hook_text_of_this_repository():
    text = HOOK.read_text(encoding="utf-8")
    assert "DECISION_GATED = {\"builder\", \"builder-opus\", \"reviewer\"}" in text
    assert "panel" not in text.split("DECISION_GATED =")[1].split("\n")[0]
