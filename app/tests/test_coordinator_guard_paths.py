"""The NONE-CHECKED path of a brief (hook rule 5, M150 point 4).

A NONE-CHECKED path is the saved scout report: a regular file inside the project folder, other than the ledger itself.
Same helpers as `test_coordinator_guard.py`.
"""
import pytest

from app.tests.test_coordinator_guard import GATED, agent, project  # noqa: F401  (project is a fixture)


@pytest.mark.parametrize("written", ["./tmpAI/scout_report.md", "tmpAI/scout_report.md.", "`tmpAI/scout_report.md`", '"tmpAI/scout_report.md",',
                                     ".claude/scout_report.md", "./.claude/scout_report.md", "tmpAI/../tmpAI/scout_report.md"])
def test_a_leading_dot_is_part_of_the_path_and_only_quotes_and_trailing_punctuation_are_dropped(project, written):
    (project / ".claude" / "scout_report.md").write_text("a scout report")
    assert agent(project, "builder", f"NONE-CHECKED: {written}")[0] == 0


@pytest.mark.parametrize("kind", GATED)
def test_a_path_that_leaves_the_project_is_refused_even_when_the_file_exists(project, kind):
    outside = project.parent / "outside_report.md"
    outside.write_text("not in the project")
    for written in ("../outside_report.md", "../../etc/hostname", str(outside), "/etc/hostname", "tmpAI/../../outside_report.md"):
        code, message = agent(project, kind, f"NONE-CHECKED: {written}")
        assert code == 2 and "outside the project folder" in message, written


def test_the_ledger_is_not_a_scout_report(project):
    for written in (".claude/knowledge/decision_ledger.md", "./.claude/knowledge/decision_ledger.md",
                    str(project / ".claude/knowledge/decision_ledger.md")):
        code, message = agent(project, "builder", f"NONE-CHECKED: {written}")
        assert code == 2 and "the ledger itself" in message, written


def test_a_link_inside_the_project_that_points_outside_is_refused(project):
    outside = project.parent / "linked_target.md"
    outside.write_text("outside")
    (project / "tmpAI" / "link.md").symlink_to(outside)
    assert agent(project, "builder", "NONE-CHECKED: tmpAI/link.md")[0] == 2


def test_a_device_is_refused(project):
    assert agent(project, "builder", "NONE-CHECKED: /dev/null")[0] == 2

