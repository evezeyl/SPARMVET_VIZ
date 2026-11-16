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


# --- no length limit (Eve, 2026-11-16, D-0154 and D-0160) -----------------------------------------

HER_WORDS_154 = '"try to stay concise but do not sacrify to clarity"'
HER_WORDS_160 = '"should not have strict limits - bypass limits when necessary - but keep precise and upated"'
REVIEW_WORDING = "as long as needed to be clear and complete; no padding; the content stays precise and current"
REVIEW_MARK = "(wording of the review session, not Eve's words)"
OLD_LIMITS = ["aim for 10 lines", "never more than 20", "15 lines or fewer", "20 lines or fewer", "10 lines or fewer",
              "read the 15 lines", "about 25 lines", "300 lines", "2 to 10 lines", "concise handoff", "Keep it short"]
FILES_WITH_THE_RULE = ["CLAUDE.md", ".claude/workflows/agent_dispatch_howto.md", ".claude/workflows/decision_compliance.md",
                       ".claude/rules/rules_agent_channel.md", ".claude/agents/coordinator.md", ".claude/agents/builder.md",
                       ".claude/agents/builder-opus.md", ".claude/agents/reviewer.md", ".claude/agents/scribe.md", ".claude/agents/scout.md"]
# the files where the limit is about a brief or a report (her point 2) and the files where it is about the handoff or the channel (D-0160)
HER_154 = ["CLAUDE.md", ".claude/workflows/agent_dispatch_howto.md", ".claude/workflows/decision_compliance.md", ".claude/agents/coordinator.md",
           ".claude/agents/builder.md", ".claude/agents/builder-opus.md", ".claude/agents/reviewer.md", ".claude/agents/scribe.md", ".claude/agents/scout.md"]
HER_160 = ["CLAUDE.md", ".claude/workflows/decision_compliance.md", ".claude/rules/rules_agent_channel.md"]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def test_no_file_states_an_old_length_limit_of_a_brief_a_report_the_handoff_or_the_channel():
    for rel in FILES_WITH_THE_RULE:
        for old in OLD_LIMITS:
            assert old not in read(rel), f"{rel} still says: {old}"


def test_the_rule_is_her_words_with_their_number_in_every_file_that_used_to_state_a_limit():
    for rel in HER_154:
        text = read(rel)
        assert HER_WORDS_154 in text and "D-0154" in text, rel
    for rel in HER_160:
        text = read(rel)
        assert HER_WORDS_160 in text and "D-0160" in text, rel


def test_the_review_sessions_sentence_is_never_shown_as_eves_unless_marked():
    for rel in FILES_WITH_THE_RULE:
        text = read(rel)
        start = 0
        while True:
            i = text.find(REVIEW_WORDING, start)
            if i < 0:
                break
            after = text[i + len(REVIEW_WORDING):i + len(REVIEW_WORDING) + len(REVIEW_MARK) + 2]
            assert REVIEW_MARK in after, f"{rel}: the review session's sentence is not marked"
            start = i + 1
    # the sentence is not carried by the agent files: they hold her words only
    for rel in [r for r in FILES_WITH_THE_RULE if "/agents/" in r]:
        assert REVIEW_WORDING not in read(rel), rel


def test_the_panels_own_word_limit_is_not_part_of_this_decision():
    for name in ("panel-architect", "panel-developer", "panel-scientist", "panel-user"):
        assert "250 words" in read(f".claude/agents/{name}.md"), name


def test_the_files_say_who_is_gated_and_where_a_scouts_report_is_saved():
    claude = read("CLAUDE.md")
    assert "Every agent except `scout`, `scribe` and the `panel-*` agents is gated" in claude and "`D-0159`" in claude
    assert "saved under `tmpAI/`" in claude
    assert "save it under `tmpAI/`" in COORDINATOR
    assert "except `scout`, `scribe` and the `panel-*` agents" in read(".claude/workflows/agent_dispatch_howto.md")


def test_the_scout_and_scribe_files_do_not_state_the_saving_of_a_scouts_report():
    # D-0155 is reading A (the scout gets no Write tool): the scout and scribe files do not mention the saving
    for name in ("scout", "scribe"):
        text = read(f".claude/agents/{name}.md")
        assert "NONE-CHECKED" not in text and "saves your report" not in text and "save a scout" not in text, name


def test_a_brief_still_holds_decided_facts_in_the_coordinator_file():
    assert "goal, decided facts (ADR numbers), the \"Decisions\" block" in COORDINATOR


def test_what_an_agent_added_to_the_handoff_and_channel_rules_is_marked_as_an_agents():
    claude_line = [l for l in read("CLAUDE.md").split("\n") if l.startswith("| `-handoff`")][0]
    assert "[ADDED by an agent, not Eve's words:" in claude_line and "moved, not deleted" in claude_line
    assert "the open state stays at the top" in claude_line
    channel = read(".claude/rules/rules_agent_channel.md")
    point = [l for l in channel.split("\n") if l.startswith("8. ")][0]
    assert "[ADDED by an agent, not Eve's words:" in point
    for added in ("asks the owners in a message", "the session that wrote the blocks"):
        assert point.index(added) > point.index("[ADDED by an agent")


def test_the_path_of_the_ledger_is_no_longer_called_a_proposal():
    for rel in (".claude/workflows/decision_compliance.md", ".claude/knowledge/decision_ledger.md"):
        text = read(rel)
        assert "is a proposal that Eve confirms" not in text and "is a proposal for Eve to confirm" not in text and "is a proposal for her to confirm" not in text, rel
        assert "D-0158" in text, rel


def test_the_rule_file_list_says_the_decision_is_hers_and_the_wording_an_agents():
    rows = [l for l in read(".claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md").split("\n")
            if l.startswith("| R1") and int(l.split("|")[1].strip()[1:]) >= 145]
    assert len(rows) >= 21
    for row in rows:
        status = row.rsplit("|", 2)[-2]
        assert "decision confirmed by Eve, 2026-11-16 (D-" in status and "the wording is an agent's and she has not read it" in status, row[:40]
    assert "the same commit as this row" not in " ".join(rows)


# --- points 5 and 6 (D-0164, D-0165, D-0166) -------------------------------------------------------

def test_none_checked_means_no_decision_applies_and_none_is_needed_with_her_addition_and_the_mark():
    for rel in (".claude/workflows/decision_compliance.md", ".claude/workflows/agent_dispatch_howto.md"):
        text = read(rel)
        assert '"no decisions that to be reported when one needed"' in text, rel
        assert "D-0165" in text and "no decision applies and none is needed" in text, rel
        assert "open point" in text and "numbered list for her" in text, rel
    assert "[ADDED by an agent, not Eve's words" in read(".claude/workflows/agent_dispatch_howto.md")
    assert "So `NONE-CHECKED` says that no decision applies and none is needed" in read(".claude/workflows/decision_compliance.md")


def test_the_howto_has_the_short_section_on_the_decisions_block():
    text = read(".claude/workflows/agent_dispatch_howto.md")
    section = text.split("## 8. The \"Decisions\" block of a brief", 1)[1]
    for needed in ("D-0164", "D-0165", "D-0166", "`scout`, `scribe` and the `panel-*` agents", "NONE-CHECKED", "The hook checks the form; the reviewer checks the content"):
        assert needed in section, needed


def test_the_definition_of_quoted_words_is_written_with_its_minimums_and_the_hook_uses_the_same_numbers():
    text = read(".claude/workflows/decision_compliance.md")
    definition = text.split("**What \"quoted words that appear in that ledger line\" means", 1)[1].split("## 7.", 1)[0]
    for needed in ("contiguous", "decision field or its evidence field", "`...`", "at least 12 characters", "each piece at least 4", "ignored", "upper and lower case",
                   "runs of spaces", "heading line is no item", "builder's proposal", "A number that is not DECIDED"):
        assert needed in definition, needed
    hook = read(".claude/hooks/coordinator_guard.py")
    assert "MIN_QUOTE = 12" in hook and "MIN_PIECE = 4" in hook


def test_the_points_file_marks_all_nine_points_answered_with_their_numbers():
    text = read(".claude/design/decisions_2026-11-14/decision_rules_points_for_eve.md")
    for needed in ("D-0153", "D-0154", "D-0155", "D-0156", "D-0157", "D-0158", "D-0159", "D-0164", "D-0165", "D-0166"):
        assert needed in text, needed
    assert "NOT ANSWERED" not in text and "answer pending" not in text
    assert "Points 5 and 6 are not answered yet" not in text


def test_sections_5_and_8_of_the_shared_file_list_the_additions_of_every_round():
    text = read(".claude/workflows/decision_compliance.md")
    eight = text.split("## 8. Added by the builder", 1)[1].split("## 9.", 1)[0]
    for needed in ("first round after her answers", "D-0153", "fix round", "round 2", "D-0164", "agent_dispatch_howto.md` section 8"):
        assert needed in eight, needed
    five = text.split("## 5. The ledger of decisions", 1)[1].split("## 6.", 1)[0]
    assert "DECIDED and taken by EVE" in five and "Asked, not decided" in five and "D-0161" in five


def test_the_meaning_of_none_checked_is_marked_as_the_review_sessions_wording_everywhere_it_is_written():
    mark = "(wording of the review session, M158, not Eve's words)"
    assert mark in read(".claude/workflows/agent_dispatch_howto.md")
    assert mark in read("CLAUDE.md")
    assert mark in read(".claude/workflows/decision_compliance.md")
    # the scout, scribe files and the reading A note are not presented as hers
    assert "[ADDED by an agent, not Eve's words: reading A leaves the scout without a Write tool" in read(".claude/workflows/decision_compliance.md")


def test_the_rule_file_list_does_not_name_commits_that_no_longer_exist_and_the_old_open_points_are_dated():
    text = read(".claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md")
    for gone in ("3c875d3d", "1b52680f", "49140d5a", "that adds this row"):
        assert gone not in text, gone
    assert "the two points that were still open then (5 and 6, answered in round 2: D-0164 to D-0166)" in text
    assert "the two points still open (5 and 6)" not in text
    assert "(D-0155: reading A, the scout gets no Write tool)" in text
