#!/usr/bin/env python3
"""Audit: Changelog completeness — phases declared in the plan vs changelog entries.

Reads .claude/plans/implementation_plan_master.md to discover all COMPLETED phases
(those marked with COMPLETED, DONE, or [x] tasks), then checks whether
.claude/knowledge/changelog.md has a corresponding entry for each.

A phase is considered "declared complete" if its header contains: COMPLETED, DONE,
or the emoji ✅, 🟢.

A changelog entry exists for a phase if the changelog contains a line or heading
referencing "Phase N" (case-insensitive).

Usage:
  .venv/bin/python scripts/audit_changelog_sync.py
  .venv/bin/python scripts/audit_changelog_sync.py --output .claude/logs/audits/audit_changelog_2026-05-12.md
  .venv/bin/python scripts/audit_changelog_sync.py --project-root /path/to/project --output report.md
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

PLAN_FILE = ".claude/plans/implementation_plan_master.md"
CHANGELOG_FILE = ".claude/knowledge/changelog.md"

PHASE_HEADER_RE = re.compile(r"^#{2,4}\s+.*?Phase\s+(\d+(?:[.-][A-Za-z0-9]+)?)", re.IGNORECASE)
COMPLETED_MARKERS = re.compile(r"COMPLETED|DONE|✅|🟢", re.IGNORECASE)


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def extract_completed_phases(plan_path: Path) -> list[tuple[str, int]]:
    """Return [(label, lineno)] for all phase headers that appear complete."""
    results = []
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    for lineno, line in enumerate(lines, 1):
        m = PHASE_HEADER_RE.match(line)
        if not m:
            continue
        if COMPLETED_MARKERS.search(line):
            results.append((m.group(1), lineno))
    return results


def extract_changelog_phases(changelog_path: Path) -> set[str]:
    """Return set of phase labels mentioned anywhere in the changelog."""
    if not changelog_path.exists():
        return set()
    text = changelog_path.read_text(encoding="utf-8")
    found = set()
    for m in re.finditer(r"Phase\s+(\d+(?:[.-][A-Za-z0-9]+)?)", text, re.IGNORECASE):
        found.add(m.group(1).upper())
    return found


def render_report(
    completed: list[tuple[str, int]],
    changelog_phases: set[str],
    plan_path: Path,
    changelog_path: Path,
    project_root: Path,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")

    missing_entries = [
        (label, lineno)
        for label, lineno in completed
        if label.upper() not in changelog_phases
    ]
    covered = [(label, lineno) for label, lineno in completed if label.upper() in changelog_phases]

    lines = [
        "# Audit Report: Changelog Completeness",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Plan file: {plan_path.relative_to(project_root)}",
        f"Changelog: {changelog_path.relative_to(project_root)}",
        f"Rule: Every completed phase must have a corresponding changelog entry (P1 audit lesson)",
        "",
        f"- Completed phases in plan: {len(completed)}",
        f"- Covered in changelog: {len(covered)}",
        f"- Missing changelog entries: {len(missing_entries)}",
        "",
    ]

    if not missing_entries:
        lines += ["## Result: ✅ PASS", "", "All completed phases have changelog entries.", ""]
    else:
        lines += [
            "## Result: ❌ FAIL",
            "",
            "## ❌ Completed Phases Without Changelog Entry",
            "",
        ]
        for label, lineno in missing_entries:
            lines += [
                f"- **Phase {label}** (plan line {lineno}) — no entry found in changelog",
            ]
        lines += [
            "",
            "**Fix:** Add entries to `.claude/knowledge/changelog.md` for each missing phase.",
            "The changelog is append-only — add at the bottom of the relevant section.",
            "Minimum entry: `## Phase N — [brief description]` with breaking changes and key renames.",
            "",
        ]

    if covered:
        lines += ["## ✅ Covered Phases", ""]
        for label, _ in covered:
            lines += [f"- Phase {label}"]
        lines += [""]

    lines += [
        "## References",
        "- `.claude/knowledge/changelog.md` — breaking changes and notable renames",
        "- Routine 7 (Changelog completeness audit) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    project_root = (
        Path(args.project_root) if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )
    plan_path = project_root / PLAN_FILE
    changelog_path = project_root / CHANGELOG_FILE

    if not plan_path.exists():
        print(f"ERROR: Plan file not found: {plan_path}", file=sys.stderr)
        return 2

    completed = extract_completed_phases(plan_path)
    changelog_phases = extract_changelog_phases(changelog_path)
    report = render_report(completed, changelog_phases, plan_path, changelog_path, project_root)

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    missing = [l for l, _ in completed if l.upper() not in changelog_phases]
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
