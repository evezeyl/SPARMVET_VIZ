"""The hook `.claude/hooks/coordinator_guard.py` keeps a coordinator session to its role.

The first group pins the rules that existed before the decision rule (edits, Bash, Agent models, who is affected):
they must stay as they are. The second group tests the rule of M150 point 4 as Eve changed it on 2026-11-16 (D-0156, D-0157, D-0158, D-0159): an agent call
is refused when its brief has neither a "Decisions" block whose numbers are DECIDED lines of the ledger taken by EVE nor a
NONE-CHECKED line whose path exists; every agent is gated except scout, scribe and the panel agents; empty lines after the
heading are skipped; a missing ledger refuses.
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
D-0001 | 2026-11-05 | area | the first decision of the test ledger | src | EVE | DECIDED | - | "her words of the first line, said on the fifth" | L01
D-0002 | 2026-11-06 | area | an agent chose the second decision here | src | AGENT | PROVISIONAL | - | words of the second line, an agent's | L02
D-0003 | 2026-11-07 | area | who took the third decision is not stated | src | NOT STATED | NOT-STATED | - | words of the third line, nobody's | L03
D-0004 | 2026-11-08 | area | a plan that the review session relayed | src | REVIEW SESSION | RELAYED | split from D-0001 | not her words, the plan of the review session | L04
D-0005 | 2026-11-09 | area | the fifth decision of the test ledger | src | EVE | DECIDED | - | "yes - the fifth rule ... with a cut in the middle of it" | L05
"""
# a decision item of a brief: the number, then words of THAT line between quotation marks (D-0166)
ITEM = {
    "D-0001": '- D-0001: "the first decision of the test ledger"',
    "D-0002": '- D-0002: "an agent chose the second decision here"',
    "D-0003": '- D-0003: "who took the third decision is not stated"',
    "D-0004": '- D-0004: "a plan that the review session relayed"',
    "D-0005": '- D-0005: "the fifth decision of the test ledger"',
}
I1, I5 = ITEM["D-0001"], ITEM["D-0005"]


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
    brief = f"Decisions\n{I1}"
    assert agent(project, "scout")[0] == 0
    assert agent(project, "scribe")[0] == 0
    assert agent(project, "builder", brief)[0] == 0
    assert agent(project, "general-purpose", brief, model="haiku")[0] == 0
    assert agent(project, "general-purpose", brief)[0] == 2   # would run on Fable
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
    brief = f'Goal: do it.\n\nDecisions\n{I1}\n{I5}\n\nFiles: a.py'
    assert agent(project, kind, brief)[0] == 0


@pytest.mark.parametrize("heading", ["Decisions", "DECISIONS", "## Decisions", "**Decisions**", "Decisions:", "DECISIONS (this block quotes)"])
def test_the_heading_may_be_written_in_the_usual_ways(project, heading):
    assert agent(project, "builder", f"Task.\n{heading}\n{I1}\n")[0] == 0


@pytest.mark.parametrize("kind", GATED)
def test_a_number_that_does_not_exist_is_refused_and_named(project, kind):
    code, message = agent(project, kind, f"Decisions\n{I1}\n- D-0777: not in the ledger\n")
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
    code, _ = agent(project, "builder", "Decisions\n- nothing decided is quoted here\n\nD-0001 is mentioned after the block ended.")
    assert code == 2


@pytest.mark.parametrize("kind", GATED)
def test_none_checked_with_an_existing_file_is_allowed(project, kind):
    assert agent(project, kind, "Goal.\nNONE-CHECKED: tmpAI/scout_report.md\n")[0] == 0
    assert agent(project, kind, f"NONE-CHECKED: {project / 'tmpAI' / 'scout_report.md'}")[0] == 0


def test_none_checked_with_a_missing_file_is_refused_and_the_path_named(project):
    code, message = agent(project, "builder", "NONE-CHECKED: tmpAI/not_there.md")
    assert code == 2 and "tmpAI/not_there.md" in message and "not a regular file that exists" in message


def test_none_checked_with_a_directory_is_refused(project):
    assert agent(project, "builder", "NONE-CHECKED: tmpAI")[0] == 2


@pytest.mark.parametrize("kind", ["scout", "scribe"])
def test_scouts_and_scribes_need_no_block(project, kind):
    assert agent(project, kind, "find where X is used")[0] == 0


@pytest.mark.parametrize("kind", ["panel-scientist", "panel-architect", "panel-developer", "panel-user"])
def test_panel_agents_are_not_gated_by_this_rule(project, kind):
    assert agent(project, kind, "a question for the panel")[0] == 0


def test_a_missing_ledger_refuses_a_decisions_brief_and_a_none_checked_brief_too(project):
    (project / ".claude" / "knowledge" / "decision_ledger.md").unlink()
    code, message = agent(project, "builder", f"Decisions\n{I1}")
    assert code == 2 and "does not exist" in message
    code, message = agent(project, "builder", "NONE-CHECKED: tmpAI/scout_report.md")      # D-0158: a check that cannot run must not pass
    assert code == 2 and "does not exist" in message


def test_a_malformed_ledger_refuses(project):
    (project / ".claude" / "knowledge" / "decision_ledger.md").write_text("D-0001 | too | few\n")
    code, message = agent(project, "builder", f"Decisions\n{I1}")
    assert code == 2 and "cannot be read" in message


def test_the_decision_rule_does_not_loosen_the_model_rule(project):
    brief = f"Decisions\n{I1}"
    assert agent(project, "builder", brief, model="opus")[0] == 2
    assert agent(project, "general-purpose", brief)[0] == 2
    assert agent(project, "reviewer", brief, model="sonnet")[0] == 0


def test_the_refusal_comes_from_the_hook_text_of_this_repository():
    text = HOOK.read_text(encoding="utf-8")
    exempt = text.split("DECISION_EXEMPT =")[1].split("\n")[0]
    assert "scout" in exempt and "scribe" in exempt and "builder" not in exempt and "reviewer" not in exempt
    assert "DECISION_GATED" not in text


# --- what Eve changed on 2026-11-16 (D-0156, D-0157, D-0158, D-0159) -----------------------------

BRIEF = f'Decisions\n{I1}\n'
OTHER_AGENTS = ["general-purpose", "Explore", "Plan", "claude-code-guide", "statusline-setup", "claude", "", "panel-evil", "some-new-agent"]


@pytest.mark.parametrize("kind", OTHER_AGENTS)
def test_every_other_agent_that_may_run_needs_a_block(project, kind):
    code, message = agent(project, kind, "do the builder's work, no block", model="sonnet")
    assert code == 2 and "no Decisions block" in message
    assert agent(project, kind, BRIEF, model="sonnet")[0] == 0
    assert agent(project, kind, "NONE-CHECKED: tmpAI/scout_report.md", model="haiku")[0] == 0


def test_the_agent_with_no_type_is_the_general_agent_and_is_gated(project):
    assert run(project, "Agent", {"model": "sonnet", "prompt": "no block"})[0] == 2
    assert run(project, "Agent", {"model": "sonnet", "prompt": BRIEF})[0] == 0
    assert run(project, "Task", {"subagent_type": "general-purpose", "model": "haiku", "prompt": "no block"})[0] == 2


@pytest.mark.parametrize("kind", ["scout", "scribe", "panel-scientist", "panel-architect", "panel-developer", "panel-user"])
def test_exempt_agents_pass_with_every_model_the_rule_allows(project, kind):
    assert agent(project, kind, "no block")[0] == 0
    assert agent(project, kind, "no block", model="haiku")[0] == 0


def test_a_gated_agent_on_fable_is_still_refused_for_its_model_before_the_block_matters(project):
    assert agent(project, "general-purpose", BRIEF)[0] == 2
    assert agent(project, "general-purpose", BRIEF, model="opus")[0] == 2


@pytest.mark.parametrize("blank", ["\n", "\n\n\n", "\n  \n\t\n"])
def test_empty_lines_right_after_the_heading_are_skipped(project, blank):
    assert agent(project, "builder", "Goal.\n\nDecisions" + blank + f'{I1}\n{I5}\n')[0] == 0
    assert agent(project, "builder", "## Decisions:" + blank + I1)[0] == 0


def test_the_block_after_skipped_lines_still_ends_at_the_next_blank_line_or_heading(project):
    code, message = agent(project, "builder", "Decisions\n\n- no number in this paragraph\n\nD-0001 is outside the block")
    assert code == 2 and "no decision number" in message
    code, _ = agent(project, "builder", "Decisions\n\n## Files\nD-0001 is under another heading")
    assert code == 2
    assert agent(project, "builder", "Decisions\n\n")[0] == 2
    assert agent(project, "builder", "Decisions")[0] == 2


@pytest.mark.parametrize("number, status", [("D-0002", "PROVISIONAL"), ("D-0003", "NOT-STATED"), ("D-0004", "RELAYED")])
def test_a_number_that_eve_did_not_decide_is_refused_with_its_status(project, number, status):
    for kind in ("builder", "reviewer", "general-purpose"):
        code, message = agent(project, kind, f'Decisions\n{I1}\n{ITEM[number]}\n', model="sonnet")
        assert code == 2, kind
        assert f"{number} (status {status})" in message and "D-0001 (" not in message
        assert "not in the ledger" not in message


def test_the_refusal_names_both_the_missing_and_the_undecided_numbers(project):
    code, message = agent(project, "builder", "Decisions\n- D-0004: relayed\n- D-0777: nothing\n- D-0005: ok\n")
    assert code == 2
    assert "D-0777, not in the ledger" in message and "D-0004 (status RELAYED)" in message and "D-0005 (" not in message


def test_a_valid_none_checked_line_does_not_make_a_number_that_is_not_decided_pass(project):
    # D-0159: any number cited in a block must be valid whenever a block is present
    for number, status in (("D-0004", "RELAYED"), ("D-0002", "PROVISIONAL"), ("D-0003", "NOT-STATED")):
        code, message = agent(project, "builder", f"Decisions\n- {number}: words\nNONE-CHECKED: tmpAI/scout_report.md")
        assert code == 2 and f"{number} (status {status})" in message
    code, message = agent(project, "builder", "Decisions\n- D-0777: nothing\nNONE-CHECKED: tmpAI/scout_report.md")
    assert code == 2 and "D-0777" in message and "not in the ledger" in message
    code, message = agent(project, "builder", "Decisions\n- D-0004: relayed\nNONE-CHECKED: tmpAI/not_there.md")
    assert code == 2 and "D-0004 (status RELAYED)" in message and "not_there.md" in message


def test_a_valid_none_checked_line_with_a_block_of_valid_numbers_or_with_no_number_still_passes(project):
    assert agent(project, "builder", f"Decisions\n{I1}\nNONE-CHECKED: tmpAI/scout_report.md")[0] == 0
    assert agent(project, "builder", "Decisions\n- no decision applies\nNONE-CHECKED: tmpAI/scout_report.md")[0] == 0
    assert agent(project, "builder", "NONE-CHECKED: tmpAI/scout_report.md")[0] == 0


@pytest.mark.parametrize("cited", ["d-0004", "D-0004", "d-0004,", "(d-0004)"])
def test_numbers_are_read_without_regard_to_case(project, cited):
    code, message = agent(project, "builder", f"Decisions\n- D-0001: ok\n- {cited}: relayed\n")
    assert code == 2 and "D-0004 (status RELAYED)" in message
    code, message = agent(project, "builder", "Decisions\n- d-0777: nothing\n")
    assert code == 2 and "D-0777" in message
    assert agent(project, "builder", "Decisions\n" + I1.replace("D-0001", "d-0001") + "\n" + I5.replace("D-0005", "d-0005") + "\n")[0] == 0


@pytest.mark.parametrize("kind", ["builder", "general-purpose"])
def test_a_missing_or_unreadable_ledger_refuses_every_gated_agent(project, kind):
    ledger = project / ".claude" / "knowledge" / "decision_ledger.md"
    ledger.unlink()
    code, message = agent(project, kind, BRIEF, model="sonnet")
    assert code == 2 and "does not exist" in message
    ledger.write_text("D-0001 | broken\n")
    code, message = agent(project, kind, BRIEF, model="sonnet")
    assert code == 2 and "cannot be read" in message
    ledger.write_bytes(b"\xff\xfe\x00")
    code, message = agent(project, kind, BRIEF, model="sonnet")
    assert code == 2 and "cannot be read" in message
    for broken in (None, "D-0001 | broken\n", b"\xff\xfe\x00"):     # D-0158 also with a valid NONE-CHECKED line
        if broken is None:
            ledger.unlink()
        elif isinstance(broken, bytes):
            ledger.write_bytes(broken)
        else:
            ledger.write_text(broken)
        assert agent(project, kind, "NONE-CHECKED: tmpAI/scout_report.md", model="sonnet")[0] == 2


def test_the_real_ledger_accepts_the_decision_of_this_task_and_refuses_a_relayed_line():
    real = ROOT
    assert (real / ".claude/knowledge/decision_ledger.md").is_file()
    import importlib.util
    spec = importlib.util.spec_from_file_location("coordinator_guard_hook", HOOK)
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    assert hook.brief_problem('Decisions\n- D-0125: "ok - decided"\n- D-0156: "gate every agent except scout, scribe and the panel-* agents"\n', real) == ""
    problem = hook.brief_problem("Decisions\n- D-0151: relayed\n", real)
    assert "D-0151 (status RELAYED)" in problem


# --- point 6, option C (D-0166): each number is followed by quoted words that appear in THAT ledger line ----------

def block(*items):
    return "Goal.\n\nDecisions\n" + "\n".join(items) + "\n"


def test_a_bare_number_is_refused_and_the_message_says_what_to_add_and_shows_the_line(project):
    for kind in ("builder", "reviewer", "general-purpose"):
        code, message = agent(project, kind, block("- D-0001"), model="sonnet")
        assert code == 2, kind
        assert "D-0001 has no quoted words" in message and "bare number is refused" in message
        assert "between quotation marks" in message and "at least 12 characters" in message
        assert "The line starts: D-0001 | 2026-11-05 | area | the first decision of the test ledger" in message
    assert agent(project, "builder", block("- D-0001:"))[0] == 2
    assert agent(project, "builder", block("- D-0001: her words", I5))[0] == 2


def test_a_number_only_on_the_heading_line_is_refused_also_with_a_quote_there(project):
    for brief in ("Decisions: D-0001, D-0005", "Decisions (see D-0001)", 'Decisions: D-0001 "the first decision of the test ledger"'):
        code, message = agent(project, "builder", brief)
        assert code == 2 and "D-0001 stands outside a list item of its own" in message, brief
    assert agent(project, "builder", 'Decisions D-0001 "the first decision of the test ledger"')[0] == 2         # not a heading: no block
    assert agent(project, "builder", 'Decisions: see below\n' + I1)[0] == 0


def test_a_number_plus_a_true_quote_passes_from_the_decision_or_from_her_words(project):
    assert agent(project, "builder", block(I1, I5))[0] == 0
    assert agent(project, "builder", block('- D-0001: "her words of the first line, said on the fifth"'))[0] == 0     # the evidence field
    assert agent(project, "builder", block('- D-0001: "the first decision of the test ledger" and a comment of the coordinator'))[0] == 0
    assert agent(project, "builder", block('- D-0001: the words are\n  "the first decision of the test ledger"'))[0] == 0     # a continuation line
    assert agent(project, "builder", block('- D-0001: “the first decision of the test ledger”'))[0] == 0               # curly marks


@pytest.mark.parametrize("quote", [
    "THE FIRST DECISION OF THE TEST LEDGER", "  the   first    decision of the   test ledger ", "the first decision ... of the test ledger",
    "the first ... test ledger", "...the first decision of the test ledger...", "the first decision of the test ledger…"])
def test_case_runs_of_spaces_and_cuts_do_not_matter(project, quote):
    assert agent(project, "builder", block(f'- D-0001: "{quote}"'))[0] == 0


def test_cuts_must_follow_the_order_of_the_line_and_stay_in_one_field(project):
    assert agent(project, "builder", block('- D-0001: "test ledger ... the first decision"'))[0] == 2          # wrong order
    assert agent(project, "builder", block('- D-0001: "the first decision ... her words of the first line"'))[0] == 2   # two fields
    assert agent(project, "builder", block('- D-0005: "yes - the fifth rule ... with a cut in the middle of it"'))[0] == 0
    assert agent(project, "builder", block('- D-0005: "fifth rule ... cut in the middle"'))[0] == 0
    assert agent(project, "builder", block('- D-0001: "the first decision ... test ... ledger"'))[0] == 0              # pieces of 4 characters or more
    code, message = agent(project, "builder", block('- D-0001: "the first decision ... tes ... ledger"'))          # a piece of 3 characters
    assert code == 2 and "no quoted words" in message


def test_a_quote_that_is_not_in_that_line_is_refused_with_the_line_shown(project):
    code, message = agent(project, "builder", block('- D-0001: "the first decision of some other ledger"'))
    assert code == 2 and "do not appear in that ledger line" in message and "quote that line, not another" in message
    assert "some other ledger" in message and "The line starts: D-0001 | 2026-11-05" in message
    assert agent(project, "builder", block('- D-0001: "the first decision of the test ledger" "something else that is not there"'))[0] == 2


def test_a_quote_of_another_line_is_refused(project):
    code, message = agent(project, "builder", block(f'- D-0001: "the fifth decision of the test ledger"'))
    assert code == 2 and "D-0001" in message and "do not appear" in message
    code, _ = agent(project, "builder", block(I1.replace("D-0001", "D-0005")))
    assert code == 2


def test_a_quote_that_is_too_short_does_not_count(project):
    assert agent(project, "builder", block('- D-0001: "first decision"'))[0] == 0              # 14 characters, counts
    assert agent(project, "builder", block('- D-0005: "fifth rule"'))[0] == 2                    # 10 characters
    code, message = agent(project, "builder", block('- D-0001: "first dec"'))                   # 9 characters, a true piece
    assert code == 2 and "no quoted words" in message
    assert agent(project, "builder", block('- D-0001: "yes"'))[0] == 2
    assert agent(project, "builder", block('- D-0001: "first decision" "x"'))[0] == 0           # a short quote is ignored, not refused


def test_a_number_inside_another_item_has_no_quote_of_its_own(project):
    code, message = agent(project, "builder", block(I1 + " (see also D-0005)"))
    assert code == 2 and "D-0005 stands outside a list item of its own" in message
    assert agent(project, "builder", block(I1 + ' (see also D-0005 "x")'))[0] == 2
    assert agent(project, "builder", block(I1, I5 + " (see also D-0001)"))[0] == 0                # D-0001 has its own item


def test_a_valid_none_checked_line_does_not_excuse_a_bare_number(project):
    assert agent(project, "builder", block("- D-0001") + "NONE-CHECKED: tmpAI/scout_report.md")[0] == 2
    assert agent(project, "builder", block(I1) + "NONE-CHECKED: tmpAI/scout_report.md")[0] == 0


@pytest.mark.parametrize("number", ["D-0002", "D-0003", "D-0004"])
def test_a_number_that_is_not_decided_is_refused_even_with_a_true_quote(project, number):
    code, message = agent(project, "builder", block(I1, ITEM[number]))
    assert code == 2 and f"{number} (status " in message and "which Eve has not decided" in message


def test_the_quote_is_looked_up_in_the_line_of_the_number_of_its_own_item(project):
    # two items: each quote must be of its own number
    assert agent(project, "builder", block(I1, I5))[0] == 0
    assert agent(project, "builder", block(I5.replace("D-0005", "D-0001"), I1.replace("D-0001", "D-0005")))[0] == 2


def test_the_real_ledger_this_rounds_block_and_the_examples_of_the_workflow_file_pass():
    import importlib.util
    spec = importlib.util.spec_from_file_location("coordinator_guard_hook2", HOOK)
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    this_round = ('Decisions\n- D-0125: "ok - decided" (Eve, 2026-11-16, on the decision-compliance rules: every decision has a number, '
                  'a date, her words quoted, who took it; only what she took is DECIDED)\n\nHer answers reached us RELAYED, as messages M158 to M166.\n')
    assert hook.brief_problem(this_round, ROOT) == ""
    # the example block of .claude/workflows/decision_compliance.md section 6
    text = (ROOT / ".claude/workflows/decision_compliance.md").read_text(encoding="utf-8")
    example = text.split("```\n")[1]
    assert example.startswith("Decisions") and "D-0112" in example
    assert hook.brief_problem(example, ROOT) == ""
    # D-0050: a bare number, then a quote that is not in the line, then a true one
    bare = hook.brief_problem("Decisions\n- D-0050\n", ROOT)
    assert "D-0050 has no quoted words" in bare and "The line starts: D-0050 | 2026-11-15 | process" in bare
    wrong = hook.brief_problem('Decisions\n- D-0050: "no silent errors allowed"\n', ROOT)
    assert "do not appear in that ledger line" in wrong and "no silent errors allowed" in wrong
    assert hook.brief_problem('Decisions\n- D-0050: "No silent error that is the rule."\n', ROOT) == ""
    assert hook.brief_problem('Decisions\n- D-0050: "no silent error"\n', ROOT) == ""


# --- fix round 3 -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("content", ["", "# a ledger with text only\n\nD-0001 is mentioned in text, not a line of the ledger.\n", "\n\n"])
@pytest.mark.parametrize("kind", ["builder", "general-purpose"])
def test_an_empty_ledger_refuses_every_gated_agent_also_with_a_valid_none_checked_line(project, kind, content):
    (project / ".claude" / "knowledge" / "decision_ledger.md").write_text(content)       # D-0158: a check that cannot run must not pass
    for brief in ("NONE-CHECKED: tmpAI/scout_report.md", BRIEF, "no block at all"):
        code, message = agent(project, kind, brief, model="sonnet")
        assert code == 2 and "holds no decision line" in message, brief


def test_the_message_for_a_number_outside_an_item_tells_the_writer_what_to_write_with_an_example_that_passes(project):
    for brief in ("Decisions: D-0001", 'Decisions (see D-0001)', "Decisions\n" + I5 + " (see also D-0001)"):
        code, message = agent(project, "builder", brief)
        assert code == 2 and "D-0001 stands outside a list item of its own" in message, brief
        assert "write it as a new line that starts with a dash and the number" in message
        assert 'for example - D-0001: "the first decision of the test ledger"' in message
        assert "at least 12 characters" in message and "the line starts: D-0001 | 2026-11-05" in message
    # the example it gives is accepted
    assert agent(project, "builder", 'Decisions\n- D-0001: "the first decision of the test ledger"')[0] == 0


def test_the_example_of_the_message_is_accepted_for_every_decided_line_of_the_real_ledger():
    import importlib.util
    spec = importlib.util.spec_from_file_location("coordinator_guard_hook3", HOOK)
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    reader = hook._load_ledger_reader()
    entries = reader.read_ledger(ROOT / ".claude/knowledge/decision_ledger.md")
    for number, entry in entries.items():
        if entry["status"] == "DECIDED":
            example = hook._example(number, entry)
            assert hook.brief_problem("Decisions\n" + example + "\n", ROOT) == "", number
