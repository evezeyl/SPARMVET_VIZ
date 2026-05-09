#!/usr/bin/env python3
"""Audit: Persona template flag completeness (strict validation).

Runs the existing PersonaValidator + SidebarValidator against all 8 persona
templates in --strict mode, treating warnings as errors. Produces a structured
markdown report suitable for the audit log.

This wraps `scripts/validate_persona_config.py` behavior using the same validator
classes, but outputs a report to .claude/logs/audits/ with full results.

Usage:
  .venv/bin/python scripts/audit_template_flags.py
  .venv/bin/python scripts/audit_template_flags.py --output .claude/logs/audits/audit_templates_2026-05-12.md
  .venv/bin/python scripts/audit_template_flags.py --project-root /path/to/project --output report.md
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TEMPLATES_GLOB = "config/ui/templates/*_template.yaml"
VALIDATE_SCRIPT = "scripts/validate_persona_config.py"


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def list_templates(project_root: Path) -> list[Path]:
    return sorted((project_root / "config/ui/templates").glob("*_template.yaml"))


def validate_template(python_bin: Path, validate_script: Path, template_path: Path) -> tuple[int, str]:
    """Run validate_persona_config.py for one template; return (exit_code, output)."""
    persona_id = template_path.stem.replace("_template", "")
    result = subprocess.run(
        [str(python_bin), str(validate_script), "--persona", persona_id, "--strict"],
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


def render_report(
    results: list[tuple[str, int, str]],
    project_root: Path,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")

    failures = [(name, code, out) for name, code, out in results if code != 0]
    passes = [(name, code, out) for name, code, out in results if code == 0]

    lines = [
        "# Audit Report: Persona Template Flag Completeness",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Rule: rules_persona_feature_flags.md — Authoritative flag matrix, cascade enforcement",
        f"Validator: PersonaValidator + SidebarValidator (strict mode — warnings treated as errors)",
        "",
        f"- Templates validated: {len(results)}",
        f"- Passed: {len(passes)}",
        f"- Failed: {len(failures)}",
        "",
    ]

    if not failures:
        lines += ["## Result: ✅ PASS", "", "All persona templates pass strict validation.", ""]
    else:
        lines += ["## Result: ❌ FAIL", ""]

    if failures:
        lines += ["## ❌ Template Failures", ""]
        for name, code, output in failures:
            lines += [
                f"### {name} (exit {code})",
                "```",
                output,
                "```",
                "",
            ]

    if passes:
        lines += ["## ✅ Templates Passing", ""]
        for name, _, _ in passes:
            lines += [f"- `{name}`"]
        lines += [""]

    lines += [
        "## References",
        "- `.claude/rules/rules_persona_feature_flags.md` — authoritative flag matrix",
        "- `scripts/validate_persona_config.py` — validator CLI",
        "- `config/ui/templates/` — all persona template files",
        "- Routine 8 (Template flag completeness) in `.claude/workflows/audit_routine_registry.md`",
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

    python_bin = project_root / ".venv" / "bin" / "python"
    validate_script = project_root / VALIDATE_SCRIPT

    if not python_bin.exists():
        print(f"ERROR: .venv not found at {python_bin}", file=sys.stderr)
        return 2
    if not validate_script.exists():
        print(f"ERROR: Validator script not found: {validate_script}", file=sys.stderr)
        return 2

    templates = list_templates(project_root)
    if not templates:
        print("ERROR: No persona templates found in config/ui/templates/", file=sys.stderr)
        return 2

    results = []
    for template_path in templates:
        persona_id = template_path.stem.replace("_template", "")
        exit_code, output = validate_template(python_bin, validate_script, template_path)
        results.append((persona_id, exit_code, output))

    report = render_report(results, project_root)
    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    failures = [name for name, code, _ in results if code != 0]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
