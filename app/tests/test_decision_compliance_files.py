"""The decision-compliance text is the same wherever it is written (M150, Eve 2026-11-16).

`.claude/workflows/decision_compliance.md` holds the goal and the rules A to H. `.claude/agents/coordinator.md` holds the
same rules, and every agent file holds one line to read the shared files and one line quoting the goal. These tests fail
when one copy is edited alone, or when a new agent file is added without the lines.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARED = (ROOT / ".claude/workflows/decision_compliance.md").read_text(encoding="utf-8")
COORDINATOR = (ROOT / ".claude/agents/coordinator.md").read_text(encoding="utf-8")
AGENT_FILES = sorted((ROOT / ".claude/agents").glob("*.md"))
READ_LINE = "Read `.claude/workflows/agent_principles.md` and `.claude/workflows/decision_compliance.md` first; read the Decisions block of the brief."


def goal_of_shared_file() -> str:
    match = re.search(r"^> (We deliver .*)$", SHARED, flags=re.M)
    assert match, "the goal is not quoted (as a block quote) in decision_compliance.md"
    return match.group(1)


def rules(text: str) -> dict:
    return {m.group(1): m.group(2) for m in re.finditer(r"^- \*\*([A-H])\.\*\* (.*)$", text, flags=re.M)}


def test_the_goal_starts_the_shared_file_word_for_word():
    goal = goal_of_shared_file()
    assert goal.startswith("We deliver an app that is well developed, architecture-wise,")
    assert goal.endswith("built correctly once, with its consequences understood by everyone who builds it.")
    assert SHARED.index(goal) < SHARED.index("## 2. The rules")


def test_the_rules_a_to_h_are_in_both_files_and_equal():
    shared, coordinator = rules(SHARED), rules(COORDINATOR)
    assert sorted(shared) == list("ABCDEFGH")
    assert shared == coordinator


def test_rule_e_keeps_the_limit_of_checkpoint_4():
    assert "(4) after a merge that CHANGES BEHAVIOUR (not pure test or records merges)" in rules(SHARED)["E"]


def test_the_coordinator_quotes_the_goal():
    assert goal_of_shared_file() in COORDINATOR


def test_every_agent_file_but_the_coordinator_reads_the_shared_files_and_quotes_the_goal():
    workers = [p for p in AGENT_FILES if p.name != "coordinator.md"]
    assert {p.stem for p in workers} >= {"builder", "builder-opus", "reviewer", "scout", "scribe",
                                         "panel-architect", "panel-developer", "panel-scientist", "panel-user"}
    goal = goal_of_shared_file()
    for path in workers:
        text = path.read_text(encoding="utf-8")
        assert READ_LINE in text, path.name
        assert f'Goal (`.claude/workflows/decision_compliance.md`, Eve 2026-11-16): "{goal}"' in text, path.name
        # the lines come right after the front matter, before the role text
        body = text.split("\n---\n", 1)[1].lstrip("\n")
        assert body.startswith(READ_LINE), path.name


def test_what_is_not_her_text_is_marked_and_listed():
    assert "## 8. Added by the builder, 2026-11-16, not Eve's text: she accepts or removes it" in SHARED
    # her sections carry no mark: the goal, the rules A-H, the workers
    for title in ("## 1. The goal", "## 2. The rules", "## 3. The workers"):
        assert "[ADDED]" not in SHARED.split(title, 1)[1].split("\n## ", 1)[0], title
    for title in ("## 4. ", "## 5. ", "## 7. "):
        assert "[ADDED]" in SHARED.split(title, 1)[1].split("\n## ", 1)[0], title
    assert "[ADDED by the builder, 2026-11-16, not Eve's text" in COORDINATOR


def test_the_claude_md_pointer_is_one_line_in_section_2_1():
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    section = claude.split("## 2. Model & Effort", 1)[1].split("## 3. Path Initiation", 1)[0]
    hits = [l for l in section.split("\n") if "decision_compliance.md" in l]
    assert len(hits) == 1 and hits[0].startswith("- **Decision compliance**")
