#!/usr/bin/env python3
"""Audit: Phase ordering in implementation_plan_master.md.

Verifies that Phase N headers in implementation_plan_master.md appear in
ascending numeric order within each h2 section. Mixed header levels (##, ###,
####) are all scanned; phase order resets at every `## ` section boundary.
Emoji prefixes and status suffixes are stripped before comparison.

This handles the plan's structure: historical archive sections (Phase A/B/3–18)
and current roadmap sections (Phase 19+) live under separate h2 headers, so
they are checked independently.

Detects within each h2 section:
- Phases listed out of ascending order (e.g. Phase 23 appearing after Phase 27)
- Duplicate phase numbers

Usage:
  .venv/bin/python scripts/audit_phase_order.py
  .venv/bin/python scripts/audit_phase_order.py --output .claude/logs/audits/audit_phase_order_2026-05-12.md
  .venv/bin/python scripts/audit_phase_order.py --project-root /path/to/project --output report.md
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

PLAN_FILE = ".claude/plans/implementation_plan_master.md"

PHASE_HEADER_RE = re.compile(
    r"^(#{2,4})\s+.*?Phase\s+(\d+(?:[.\-][A-Za-z0-9]+)?).*",
    re.IGNORECASE,
)
H2_RE = re.compile(r"^##\s+")
# Completed markers — phases with these in their header are archived and skip ordering checks
COMPLETED_RE = re.compile(r"COMPLETED|DONE|✅|\U0001f7e2", re.IGNORECASE)


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def extract_phases_by_section(
    plan_path: Path,
) -> list[tuple[str, list[tuple[int, str]]]]:
    """Return [(section_title, [(lineno, label)])] — phases grouped by h2 section."""
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    sections: list[tuple[str, list[tuple[int, str]]]] = []
    current_section = "Preamble"
    current_phases: list[tuple[int, str]] = []

    for lineno, line in enumerate(lines, 1):
        if H2_RE.match(line):
            if current_phases:
                sections.append((current_section, current_phases))
            elif sections or current_section != "Preamble":
                sections.append((current_section, []))
            current_section = line.strip()
            current_phases = []
            continue

        m = PHASE_HEADER_RE.match(line)
        if m:
            label = m.group(2)
            # Skip phases already marked complete — they live in archive sections
            if not COMPLETED_RE.search(line):
                current_phases.append((lineno, label))

    if current_phases:
        sections.append((current_section, current_phases))

    return sections


def find_violations(
    sections: list[tuple[str, list[tuple[int, str]]]]
) -> list[dict]:
    violations = []

    for section_title, phases in sections:
        seen: dict[int, tuple[str, int]] = {}
        last_numeric = -1

        for lineno, label in phases:
            try:
                numeric = int(re.match(r"\d+", label).group())
            except (AttributeError, ValueError):
                continue

            full_key = label.upper()
            if full_key in seen:
                violations.append({
                    "type": "DUPLICATE",
                    "label": label,
                    "line": lineno,
                    "section": section_title,
                    "detail": (
                        f"Phase {label} already appeared at line {seen[full_key][1]}"
                    ),
                })
            else:
                seen[full_key] = (label, lineno)

            if numeric < last_numeric:
                violations.append({
                    "type": "OUT_OF_ORDER",
                    "label": label,
                    "line": lineno,
                    "section": section_title,
                    "detail": (
                        f"Phase {numeric} follows Phase {last_numeric} "
                        f"in section '{section_title}' — expected ascending order"
                    ),
                })

            if numeric >= last_numeric:
                last_numeric = numeric

    return violations


def render_report(
    violations: list[dict],
    sections: list[tuple[str, list[tuple[int, str]]]],
    plan_path: Path,
    project_root: Path,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    total_phases = sum(len(phases) for _, phases in sections)

    lines = [
        "# Audit Report: Phase Ordering in implementation_plan_master.md",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Plan file: {plan_path.relative_to(project_root)}",
        "Rule: Within each h2 section, phases must appear in ascending numeric order",
        f"Total phase headers found: {total_phases} across {len(sections)} section(s)",
        "",
    ]

    if not violations:
        lines += ["## Result: ✅ PASS", "", "All phases are in ascending order within each section.", ""]
    else:
        lines += [
            "## Result: ❌ FAIL",
            "",
            f"- Violations found: {len(violations)}",
            "",
            "## ❌ Phase Order Violations",
            "",
        ]
        for v in violations:
            lines += [
                f"### Line {v['line']}: Phase {v['label']} — {v['type']}",
                f"- {v['detail']}",
                "- **Fix:** Move the phase block to its correct chronological position within the section.",
                "",
            ]

    lines += ["## Section Summary", ""]
    for section_title, phases in sections:
        if not phases:
            continue
        phase_labels = ", ".join(f"{label}(L{ln})" for ln, label in phases)
        lines.append(f"**{section_title}**")
        lines.append(f"  Phases: {phase_labels}")
        lines.append("")

    lines += [
        "## References",
        "- `.claude/plans/implementation_plan_master.md` — authoritative roadmap",
        "- Routine 6 (Phase ordering audit) in `.claude/workflows/audit_routine_registry.md`",
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
    if not plan_path.exists():
        print(f"ERROR: Plan file not found: {plan_path}", file=sys.stderr)
        return 2

    sections = extract_phases_by_section(plan_path)
    violations = find_violations(sections)
    report = render_report(violations, sections, plan_path, project_root)

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
