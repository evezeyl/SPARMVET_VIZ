#!/usr/bin/env python3
"""Audit: Manifest structure integrity.

Discovers all pipeline manifests in config/manifests/pipelines/ and runs each
through the assembler (debug_assembler.py) in headless mode. A manifest passes
if the assembler exits 0. Failures indicate broken wrangling, missing fields,
or invalid YAML structure.

Outputs per-manifest PASS/FAIL status and a consolidated markdown report.
Assembler artifacts are written to tmpAI/audit_manifest_integrity/ (agent scratch).

Usage:
  .venv/bin/python scripts/audit_manifest_integrity.py
  .venv/bin/python scripts/audit_manifest_integrity.py --output .claude/logs/audits/audit_manifest_2026-05-12.md
  .venv/bin/python scripts/audit_manifest_integrity.py --project-root /path/to/project
  .venv/bin/python scripts/audit_manifest_integrity.py --manifest config/manifests/pipelines/myfile.yaml
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MANIFESTS_GLOB = "config/manifests/pipelines/*.yaml"
ASSEMBLER_SCRIPT = "libs/transformer/tests/debug_assembler.py"
SCRATCH_DIR = "tmpAI/audit_manifest_integrity"


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def list_manifests(project_root: Path, single: str | None) -> list[Path]:
    if single:
        p = Path(single)
        if not p.is_absolute():
            p = project_root / p
        return [p] if p.exists() else []
    manifests_dir = project_root / "config/manifests/pipelines"
    return sorted(manifests_dir.glob("*.yaml")) if manifests_dir.exists() else []


def run_assembler(
    python_bin: Path, assembler: Path, manifest_path: Path, scratch: Path
) -> tuple[int, str]:
    manifest_scratch = scratch / manifest_path.stem
    manifest_scratch.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            str(python_bin),
            str(assembler),
            "--manifest", str(manifest_path),
            "--tmp", str(manifest_scratch),
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
        "# Audit Report: Manifest Structure Integrity",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Assembler: {ASSEMBLER_SCRIPT}",
        f"Scratch output: {scratch.relative_to(project_root)}",
        f"Rule: All pipeline manifests must assemble without error (ADR-041, ADR-024)",
        "",
        f"- Manifests checked: {len(results)}",
        f"- Passed: {len(passes)}",
        f"- Failed: {len(failures)}",
        "",
    ]

    if not failures:
        lines += ["## Result: ✅ PASS", "", "All pipeline manifests assemble successfully.", ""]
    else:
        lines += [
            "## Result: ❌ FAIL",
            "",
            "## ❌ Failing Manifests",
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
                "- Ensure `final_contract` columns are produced by the recipe.",
                "- See `rules_persona_bioscientist.md §7` error diagnosis table.",
                "",
            ]

    if passes:
        lines += ["## ✅ Passing Manifests", ""]
        for name, _, _ in passes:
            lines += [f"- `{name}`"]
        lines += [""]

    lines += [
        "## References",
        "- `.claude/rules/rules_manifest_structure.md` — canonical YAML format",
        "- `.claude/rules/rules_data_engine.md` — 3-Tier lifecycle, wrangling standards",
        "- `libs/transformer/tests/debug_assembler.py` — assembler debug runner",
        "- Routine 3 (Manifest integrity) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--manifest", default=None, help="Run against a single manifest only")
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

    manifests = list_manifests(project_root, args.manifest)
    if not manifests:
        print("WARNING: No manifests found — nothing to check.", file=sys.stderr)
        return 0

    results = []
    for manifest_path in manifests:
        rel = manifest_path.relative_to(project_root) if manifest_path.is_absolute() else manifest_path
        print(f"Checking {rel} ...", file=sys.stderr)
        exit_code, output = run_assembler(python_bin, assembler, manifest_path, scratch)
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
