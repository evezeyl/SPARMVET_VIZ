#!/usr/bin/env python3
"""Audit: Data analysis recipe structure integrity.

Discovers all pipeline data analysis recipes in config/data_analysis_recipes/pipelines/ and runs each
through the assembler (debug_assembler.py) in headless mode. A data analysis recipe passes
if the assembler exits 0. Failures indicate broken wrangling, missing fields,
or invalid YAML structure.

Outputs per-data analysis recipe PASS/FAIL status and a consolidated markdown report.
Assembler artifacts are written to tmpAI/audit_data_analysis_recipe_integrity/ (agent scratch).

Usage:
  .venv/bin/python scripts/audit_data_analysis_recipe_integrity.py
  .venv/bin/python scripts/audit_data_analysis_recipe_integrity.py --output .claude/logs/audits/audit_data_analysis_recipe_2026-05-12.md
  .venv/bin/python scripts/audit_data_analysis_recipe_integrity.py --project-root /path/to/project
  .venv/bin/python scripts/audit_data_analysis_recipe_integrity.py --data-analysis-recipe config/data_analysis_recipes/pipelines/myfile.yaml
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DATA_ANALYSIS_RECIPES_GLOB = "config/data_analysis_recipes/pipelines/*.yaml"
ASSEMBLER_SCRIPT = "libs/transformer/tests/debug_assembler.py"
SCRATCH_DIR = "tmpAI/audit_data_analysis_recipe_integrity"


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def list_data_analysis_recipes(project_root: Path, single: str | None) -> list[Path]:
    if single:
        p = Path(single)
        if not p.is_absolute():
            p = project_root / p
        return [p] if p.exists() else []
    data_analysis_recipes_dir = project_root / "config/data_analysis_recipes/pipelines"
    return sorted(data_analysis_recipes_dir.glob("*.yaml")) if data_analysis_recipes_dir.exists() else []


def run_assembler(
    python_bin: Path, assembler: Path, data_analysis_recipe_path: Path, scratch: Path
) -> tuple[int, str]:
    data_analysis_recipe_scratch = scratch / data_analysis_recipe_path.stem
    data_analysis_recipe_scratch.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            str(python_bin),
            str(assembler),
            "--data-analysis-recipe", str(data_analysis_recipe_path),
            "--tmp", str(data_analysis_recipe_scratch),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


def render_report(
    results: list[tuple[str, int, str]],
    project_root: Path,
    scratch: Path,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    failures = [(name, code, out) for name, code, out in results if code != 0]
    passes = [(name, code, out) for name, code, out in results if code == 0]

    lines = [
        "# Audit Report: Data Analysis Recipe Structure Integrity",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Assembler: {ASSEMBLER_SCRIPT}",
        f"Scratch output: {scratch.relative_to(project_root)}",
        f"Rule: All pipeline data analysis recipes must assemble without error (ADR-041, ADR-024)",
        "",
        f"- Data analysis recipes checked: {len(results)}",
        f"- Passed: {len(passes)}",
        f"- Failed: {len(failures)}",
        "",
    ]

    if not failures:
        lines += ["## Result: ✅ PASS", "", "All pipeline data analysis recipes assemble successfully.", ""]
    else:
        lines += [
            "## Result: ❌ FAIL",
            "",
            "## ❌ Failing Data Analysis Recipes",
            "",
        ]
        for name, code, output in failures:
            lines += [
                f"### {name} (exit {code})",
                "```",
                output[-2000:] if len(output) > 2000 else output,
                "```",
                "",
                "**Fix guidance:**",
                "- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).",
                "- Verify all `action:` names exist in the transformer registry.",
                "- Ensure the columns of the last `polars_select` step are produced by the step list.",
                "- See `rules_agent_role_bioscientist.md §7` error diagnosis table.",
                "",
            ]

    if passes:
        lines += ["## ✅ Passing Data Analysis Recipes", ""]
        for name, _, _ in passes:
            lines += [f"- `{name}`"]
        lines += [""]

    lines += [
        "## References",
        "- `.claude/rules/rules_data_analysis_recipe_structure.md` — canonical YAML format",
        "- `.claude/rules/rules_data_engine.md` — 3-Tier lifecycle, wrangling standards",
        "- `libs/transformer/tests/debug_assembler.py` — assembler debug runner",
        "- Routine 3 (Data analysis recipe integrity) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--data-analysis-recipe", default=None, help="Run against a single data analysis recipe only")
    args = parser.parse_args()

    project_root = (
        Path(args.project_root) if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )

    python_bin = project_root / ".venv" / "bin" / "python"
    assembler = project_root / ASSEMBLER_SCRIPT
    scratch = project_root / SCRATCH_DIR

    if not python_bin.exists():
        print(f"ERROR: .venv not found at {python_bin}", file=sys.stderr)
        return 2
    if not assembler.exists():
        print(f"ERROR: Assembler not found: {assembler}", file=sys.stderr)
        return 2

    data_analysis_recipes = list_data_analysis_recipes(project_root, args.data_analysis_recipe)
    if not data_analysis_recipes:
        print("WARNING: No data analysis recipes found — nothing to check.", file=sys.stderr)
        return 0

    results = []
    for data_analysis_recipe_path in data_analysis_recipes:
        rel = data_analysis_recipe_path.relative_to(project_root) if data_analysis_recipe_path.is_absolute() else data_analysis_recipe_path
        print(f"Checking {rel} ...", file=sys.stderr)
        exit_code, output = run_assembler(python_bin, assembler, data_analysis_recipe_path, scratch)
        results.append((str(rel), exit_code, output))

    report = render_report(results, project_root, scratch)
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
