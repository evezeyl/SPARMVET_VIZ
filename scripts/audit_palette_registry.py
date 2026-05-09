#!/usr/bin/env python3
"""Audit: Palette registry format validity (ADR-081).

Verifies that config/palettes.yaml (if present) is valid YAML and that each
palette entry follows the expected format: a mapping of name → list of hex colors.
Also checks that no entry accidentally shadows a built-in palette name.

Rule source: .claude/rules/rules_viz_factory.md §6
ADR reference: ADR-081 (Deployment Palette Registry & VizFactory Palette Injection)

Usage:
  .venv/bin/python scripts/audit_palette_registry.py
  .venv/bin/python scripts/audit_palette_registry.py --output .claude/logs/audits/audit_palette_YYYY-MM-DD.md
  .venv/bin/python scripts/audit_palette_registry.py --palettes config/palettes.yaml --output report.md

Exit codes:
  0  PASS — file absent (INFO) or present and valid
  1  FAIL — file present but malformed or violations found
  2  Script error
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: .venv/bin/pip install pyyaml", file=sys.stderr)
    sys.exit(2)


_BUILTIN_PALETTE_NAMES = {"sparmvet_brand"}

_HEX_RE = re.compile(r'^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$')


def _is_valid_hex(value: str) -> bool:
    return bool(_HEX_RE.match(str(value)))


def audit_palette_file(palette_path: Path) -> tuple[list[str], list[str], list[str]]:
    """Return (violations, warnings, infos)."""
    violations: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []

    if not palette_path.exists():
        infos.append(f"config/palettes.yaml absent — built-in palettes only (this is normal).")
        return violations, warnings, infos

    # Parse YAML
    try:
        raw = yaml.safe_load(palette_path.read_text())
    except yaml.YAMLError as exc:
        violations.append(f"PARSE_ERROR — {palette_path.resolve()} is not valid YAML: {exc}")
        return violations, warnings, infos

    if raw is None:
        infos.append("config/palettes.yaml exists but is empty — built-in palettes only.")
        return violations, warnings, infos

    if not isinstance(raw, dict):
        violations.append(
            f"FORMAT_ERROR — top-level must be a YAML mapping with a 'palettes:' key, got {type(raw).__name__}."
        )
        return violations, warnings, infos

    # File must have a top-level 'palettes:' key (mirrors bootloader.get_palettes logic)
    if "palettes" not in raw:
        violations.append(
            "MISSING_KEY — top-level 'palettes:' key not found. "
            "File must start with 'palettes:' followed by named palette entries."
        )
        return violations, warnings, infos

    project_palettes = raw["palettes"]
    if not isinstance(project_palettes, dict):
        violations.append(
            f"FORMAT_ERROR — 'palettes:' value must be a mapping of name → list[hex], "
            f"got {type(project_palettes).__name__}."
        )
        return violations, warnings, infos

    infos.append(f"Loaded {len(project_palettes)} palette(s) from config/palettes.yaml.")

    for name, colors in project_palettes.items():
        # Name validation
        if not isinstance(name, str) or not name.strip():
            violations.append(f"INVALID_NAME — palette key is not a non-empty string: {name!r}")
            continue

        # Built-in shadow check
        if name in _BUILTIN_PALETTE_NAMES:
            warnings.append(
                f"SHADOWS_BUILTIN — '{name}' shadows a built-in palette. "
                f"The project copy overrides the built-in, which may surprise users."
            )

        # Colors must be a non-empty list
        if not isinstance(colors, list):
            violations.append(
                f"TYPE_ERROR — palette '{name}': colors must be a list of hex strings, "
                f"got {type(colors).__name__}."
            )
            continue

        if len(colors) == 0:
            violations.append(f"EMPTY_PALETTE — palette '{name}' has no colors (empty list).")
            continue

        # Each color must be a valid hex string
        bad = [c for c in colors if not _is_valid_hex(str(c))]
        if bad:
            violations.append(
                f"INVALID_HEX — palette '{name}' contains non-hex values: "
                + ", ".join(repr(b) for b in bad)
                + ". Expected format: #rrggbb or #rgb."
            )
        else:
            infos.append(f"  '{name}': {len(colors)} color(s) — OK")

    return violations, warnings, infos


def build_report(violations: list[str], warnings: list[str], infos: list[str],
                 palette_path: Path) -> tuple[str, int]:
    now = datetime.now().isoformat(timespec="seconds")
    lines = [
        "# Audit: Palette Registry Format Validity",
        f"Generated: {now}",
        f"File checked: `{palette_path}`",
        f"Rule: `.claude/rules/rules_viz_factory.md §6` | ADR-081",
        "",
    ]

    if violations:
        lines.append(f"## ❌ FAIL — {len(violations)} violation(s)")
    elif warnings:
        lines.append(f"## ⚠️  PASS with warnings — {len(warnings)} warning(s)")
    else:
        lines.append("## ✅ PASS")

    lines.append("")

    if infos:
        lines.append("### Info")
        for i in infos:
            lines.append(f"- {i}")
        lines.append("")

    if warnings:
        lines.append("### Warnings")
        for w in warnings:
            lines.append(f"- ⚠️  {w}")
        lines.append("")

    if violations:
        lines.append("### Violations")
        for v in violations:
            lines.append(f"- ❌ {v}")
        lines.append("")

    lines.append("## Summary")
    lines.append(f"- Violations: {len(violations)}")
    lines.append(f"- Warnings: {len(warnings)}")

    lines.append("")
    lines.append("## References")
    lines.append("- `.claude/rules/rules_viz_factory.md §6` — Palette Injection (ADR-081)")
    lines.append("- `app/src/bootloader.py` — `get_palettes()` method (never returns empty)")
    lines.append("- `libs/viz_factory/src/viz_factory/viz_factory.py` — `_BUILTIN_PALETTES`, `_apply_palette()`")

    exit_code = 1 if violations else 0
    return "\n".join(lines), exit_code


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--palettes",
        default="config/palettes.yaml",
        help="Path to the palette registry YAML file (default: config/palettes.yaml)",
    )
    parser.add_argument(
        "--output",
        help="Write report to this file (default: stdout only)",
    )
    args = parser.parse_args()

    palette_path = Path(args.palettes)
    try:
        violations, warnings, infos = audit_palette_file(palette_path)
        report, exit_code = build_report(violations, warnings, infos, palette_path)
    except Exception as exc:
        print(f"SCRIPT ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    print(report)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)
        print(f"\nReport written to: {out}", file=sys.stderr)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
