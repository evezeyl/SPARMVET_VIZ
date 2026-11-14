"""The dependency index generator indexes the project, not the copies of it in agent worktrees.

An agent worktree (.claude/worktrees/<name>/) holds a full copy of the repository; indexing it turned the
index from 935 into 4820 lines (2026-11-14). The skip is decided on the path relative to the project root, so
that the place where the project lives (a path with a `tmp` or `build` folder in it) cannot hide the project.
"""
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "build_dep_graph", Path(__file__).resolve().parents[2] / "assets" / "scripts" / "build_dep_graph.py"
)
dep = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(dep)

ANNOTATED = "# @deps\n# provides: class:Thing\n# consumed_by: app/other.py\n# @end_deps\n"


def _write(root: Path, rel: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ANNOTATED)


def _files(root: Path) -> list[str]:
    return sorted(node["file"] for node in dep.scan_project(root))


def test_a_copy_of_the_project_in_a_worktree_is_not_indexed(tmp_path):
    _write(tmp_path, "libs/x/thing.py")
    _write(tmp_path, ".claude/worktrees/agent-1/libs/x/thing.py")
    assert _files(tmp_path) == ["libs/x/thing.py"]


def test_every_worktree_is_skipped_not_only_the_first(tmp_path):
    _write(tmp_path, "libs/x/thing.py")
    _write(tmp_path, ".claude/worktrees/agent-1/libs/x/thing.py")
    _write(tmp_path, ".claude/worktrees/agent-2/app/modules/y.py")
    assert _files(tmp_path) == ["libs/x/thing.py"]


def test_the_other_files_under_dot_claude_are_still_indexed(tmp_path):
    _write(tmp_path, ".claude/rules/rule.py")
    _write(tmp_path, ".claude/worktrees/agent-1/.claude/rules/rule.py")
    assert _files(tmp_path) == [".claude/rules/rule.py"]


def test_a_folder_named_worktrees_elsewhere_is_not_skipped(tmp_path):
    _write(tmp_path, "docs/worktrees/page.py")
    assert _files(tmp_path) == ["docs/worktrees/page.py"]


def test_a_project_that_lives_under_a_skipped_folder_name_is_still_indexed(tmp_path):
    root = tmp_path / "build" / "tmp" / "project"
    _write(root, "libs/x/thing.py")
    assert _files(root) == ["libs/x/thing.py"]


def test_the_skipped_folders_inside_the_project_are_still_skipped(tmp_path):
    _write(tmp_path, "libs/x/thing.py")
    _write(tmp_path, "tmpAI/scratch.py")
    _write(tmp_path, ".venv/lib/pkg.py")
    assert _files(tmp_path) == ["libs/x/thing.py"]
