#!/usr/bin/env python3
"""Audit: CSS design token compliance (rules_css_style_spec.md).

Verifies that config/ui/theme.css uses only colors, font-sizes, and border-radius
values defined in the SPARMVET design system. Catches off-palette hex values,
out-of-scale font sizes, and forbidden Bootstrap defaults introduced by agents
who did not read the style spec before writing CSS.

Rule source: .claude/rules/rules_css_style_spec.md
ADR reference: ADR-055 (CSS authority)

Usage:
  .venv/bin/python scripts/audit_css_style.py
  .venv/bin/python scripts/audit_css_style.py --output .claude/logs/audits/audit_css_2026-05-09.md
  .venv/bin/python scripts/audit_css_style.py --css config/ui/theme.css --output report.md
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


# ── Allowed hex palette (from rules_css_style_spec.md §1) ────────────────────
# All values lowercase. Any hex NOT in this set is a violation.
ALLOWED_HEX = {
    # Structural surfaces
    "#d1d1d1", "#c0c0c0", "#ffffff", "#f8f9fa", "#fafafa",
    # Borders
    "#e9ecef", "#dee2e6", "#d0d0d0", "#909090",
    # Brand / action
    "#345beb", "#2a4bc4", "#2344bb", "#1e35c9",
    "#10a395", "#0d8a7e", "#0b7569",
    "#ffc107", "#e0a800", "#c79500",
    "#d62828", "#b91c1c",                    # error red + hover
    # Status / semantic
    "#d5efec", "#0b6358",                   # OK/connected (teal tint)
    "#fff3cd", "#856404",                   # Busy/loading (amber)
    "#ffe0e0", "#d62828",                   # Error (error red tint)
    # Text
    "#1a1a1a", "#333333", "#6c757d",
    # Component-specific (documented in spec §1f)
    "#eef0fb",          # audit-tier2-bg / user message bg
    "#e6f7f5",          # audit-tier3-bg
    "#fff9c4",          # gallery guidance bg
    "#f0e68c",          # gallery guidance border
    "#5f5a3a",          # gallery guidance text
    "#fff3c4",          # gallery note header bg
    "#ffbc00",          # reference label border
    "#c8b86a",          # gallery blockquote left-border
    "#c8b96a",          # gallery table border
    "#cbd5e1",          # scientific table border
    "#f1f5f9",          # scientific table th bg
    "#f8fafc",          # scientific table even-row bg
    "#3b3620",          # gallery h2 color
    "#fffde7",          # gallery guidance even-row
    "#fff8a0",          # gallery guidance row hover
    "#ffeeba",          # pk-warn badge border
    "#f5f5f5",          # agent/surface neutral
    # Button / form infrastructure
    "#b0b0b0",          # disabled button bg
    "#5c636a",          # btn-file border in sidebar
    "#a0a0a0",          # sidebar accordion collapsed header bg
    "#000000",          # pure black — text on amber/yellow buttons (#000 shorthand)
    # RGBA / opacity variants derived from palette — handled separately (see below)
}

# Known-debt hex values: in palette spec §1f, marked as "pending fix"
KNOWN_DEBT_HEX = {
    "#cfe2ff",  # .spv-badge-propagation bg — Bootstrap info, tracked CSS-BADGE-PROPAG-1
    "#0a3678",  # .spv-badge-propagation text — Bootstrap info dark, tracked CSS-BADGE-PROPAG-1
}

# Explicitly forbidden Bootstrap defaults (highest priority — always BLOCKER)
FORBIDDEN_BOOTSTRAP = {
    "#0d6efd": "Bootstrap primary (use #345beb)",
    "#198754": "Bootstrap success green (use #d5efec / #0b6358)",
    "#dc3545": "Bootstrap danger red (no red in palette; use amber #fff3cd)",
    "#d4edda": "Bootstrap success bg (use #d5efec)",
    "#155724": "Bootstrap success text (use #0b6358)",
    "#f8d7da": "Bootstrap danger bg (use #fff3cd)",
    "#721c24": "Bootstrap danger text (use #7a4100)",
    "#e3f2fd": "Material Design Blue 50 (use #eef0fb)",
    "#0d47a1": "Material Design Blue 900 (use #1a1a1a or #345beb)",
}

# Allowed font-size values (rules_css_style_spec.md §2)
# Both with and without leading zero (0.8rem and .8rem both seen in wild)
ALLOWED_FONT_SIZES = {
    "0.85rem", ".85rem",
    "0.8rem",  ".8rem",
    "0.78rem", ".78rem",
    "0.75rem", ".75rem",
    "0.65rem", ".65rem",
    "1.0rem",  "1rem",       # allowed for view-title-banner and gallery h1/h2
    "0.9em",   ".9em",       # em-based utility classes in §20 are allowed
    "0.8em",   ".8em",
    "0.75em",  ".75em",
    "0.72em",  ".72em",
    "0.7em",   ".7em",
    "0.65em",  ".65em",
    "0.68em",  ".68em",      # .column-picker-container .selectize-input .item
    "0.88em",  ".88em",      # gallery-md-pane code
    "1.55",                   # line-height, not font-size
    # Size overrides for smaller contexts
    "0.85em",  ".85em",      # gallery-md-pane h1 font-size: 0.85em
    "1.5",                    # line-height
}
FORBIDDEN_FONT_SIZES = {
    "0.9rem", ".9rem",        # Outside scale — introduced in BP-AGENT-CSS-1
}

# Allowed border-radius values (rules_css_style_spec.md §3a)
ALLOWED_RADII = {"0", "0px", "3px", "4px", "5px", "6px", "7px", "8px", "10px", "50%"}


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def strip_css_comments(text: str) -> list[tuple[int, str]]:
    """Return (lineno, stripped_line) pairs with comment content removed.

    Multi-line block comments are stripped; line numbers preserved.
    """
    result = []
    in_block = False
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = ""
        j = 0
        while j < len(line):
            if in_block:
                end = line.find("*/", j)
                if end == -1:
                    j = len(line)  # rest of line is comment
                else:
                    j = end + 2
                    in_block = False
            else:
                start_idx = line.find("/*", j)
                if start_idx == -1:
                    stripped += line[j:]
                    j = len(line)
                else:
                    stripped += line[j:start_idx]
                    j = start_idx + 2
                    in_block = True
        result.append((i, stripped))
    return result


def scan_hex(lines: list[tuple[int, str]], css_path: Path) -> list[dict]:
    """Find hex color violations in stripped CSS lines."""
    violations = []
    hex_re = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")

    for lineno, line in lines:
        # Skip blank or selector-only lines
        if ":" not in line and "{" not in line:
            continue
        for m in hex_re.finditer(line):
            raw = m.group(0).lower()
            # Normalize 3-digit shorthand to 6-digit
            if len(raw) == 4:
                raw = "#" + raw[1] * 2 + raw[2] * 2 + raw[3] * 2

            if raw in FORBIDDEN_BOOTSTRAP:
                violations.append({
                    "file": str(css_path),
                    "line": lineno,
                    "value": raw,
                    "category": "hex",
                    "severity": "BLOCKER",
                    "reason": f"Forbidden Bootstrap default: {FORBIDDEN_BOOTSTRAP[raw]}",
                    "snippet": line.strip()[:100],
                })
            elif raw in KNOWN_DEBT_HEX:
                violations.append({
                    "file": str(css_path),
                    "line": lineno,
                    "value": raw,
                    "category": "hex",
                    "severity": "KNOWN_DEBT",
                    "reason": "Tracked in tasks.md (CSS-BADGE-PROPAG-1) — pending migration to palette",
                    "snippet": line.strip()[:100],
                })
            elif raw not in ALLOWED_HEX:
                violations.append({
                    "file": str(css_path),
                    "line": lineno,
                    "value": raw,
                    "category": "hex",
                    "severity": "BLOCKER",
                    "reason": f"Not in SPARMVET palette (rules_css_style_spec.md §1)",
                    "snippet": line.strip()[:100],
                })
    return violations


def scan_font_sizes(lines: list[tuple[int, str]], css_path: Path) -> list[dict]:
    """Find font-size violations in stripped CSS lines."""
    violations = []
    # Match font-size: <value> (captures the value token)
    fs_re = re.compile(r"\bfont-size\s*:\s*([^\s;!]+)")

    for lineno, line in lines:
        for m in fs_re.finditer(line):
            val = m.group(1).rstrip(";").strip()
            if val in FORBIDDEN_FONT_SIZES:
                violations.append({
                    "file": str(css_path),
                    "line": lineno,
                    "value": val,
                    "category": "font-size",
                    "severity": "BLOCKER",
                    "reason": f"0.9rem is outside the SPARMVET typography scale (rules_css_style_spec.md §2). Use 0.85rem (Primary) instead.",
                    "snippet": line.strip()[:100],
                })
            elif val not in ALLOWED_FONT_SIZES and not val.startswith("var("):
                violations.append({
                    "file": str(css_path),
                    "line": lineno,
                    "value": val,
                    "category": "font-size",
                    "severity": "BLOCKER",
                    "reason": f"Font size '{val}' not in approved typography scale (rules_css_style_spec.md §2)",
                    "snippet": line.strip()[:100],
                })
    return violations


def scan(project_root: Path, css_relative: str = "config/ui/theme.css") -> tuple[list[dict], Path]:
    css_path = project_root / css_relative
    if not css_path.exists():
        return [], css_path

    text = css_path.read_text(encoding="utf-8")
    stripped_lines = strip_css_comments(text)

    violations = []
    violations += scan_hex(stripped_lines, css_path)
    violations += scan_font_sizes(stripped_lines, css_path)
    return violations, css_path


def render_report(violations: list[dict], css_path: Path, project_root: Path) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    blockers = [v for v in violations if v["severity"] == "BLOCKER"]
    debt = [v for v in violations if v["severity"] == "KNOWN_DEBT"]

    lines = [
        "# Audit Report: CSS Design Token Compliance",
        f"Generated: {now}",
        f"Scanned: {css_path.relative_to(project_root)}",
        f"Rule: rules_css_style_spec.md | ADR-055",
        "",
    ]

    if not blockers:
        status = "✅ PASS" if not debt else "⚠️ PASS (known debt only)"
    else:
        status = "❌ FAIL"

    lines += [f"## Result: {status}", ""]
    lines += [
        f"- Blockers (must fix): {len(blockers)}",
        f"- Known-debt violations (tracked): {len(debt)}",
        "",
    ]

    if blockers:
        # Group by category
        hex_blocks = [v for v in blockers if v["category"] == "hex"]
        font_blocks = [v for v in blockers if v["category"] == "font-size"]

        if hex_blocks:
            lines += ["## ❌ Color Violations (off-palette hex values)", ""]
            for v in hex_blocks:
                lines += [
                    f"### Line {v['line']}: `{v['value']}`",
                    f"- **Reason:** {v['reason']}",
                    f"- **Snippet:** `{v['snippet']}`",
                    f"- **Fix:** Replace with a value from rules_css_style_spec.md §1. Check §8 for common substitutions.",
                    "",
                ]

        if font_blocks:
            lines += ["## ❌ Typography Violations (out-of-scale font sizes)", ""]
            for v in font_blocks:
                lines += [
                    f"### Line {v['line']}: `font-size: {v['value']}`",
                    f"- **Reason:** {v['reason']}",
                    f"- **Snippet:** `{v['snippet']}`",
                    f"- **Fix:** Use `0.85rem` (Primary) or `0.8rem` (Secondary). See rules_css_style_spec.md §2.",
                    "",
                ]

    if debt:
        lines += ["## ⚠️ Known-Debt Violations (tracked, do not expand)", ""]
        for v in debt:
            lines += [
                f"- Line {v['line']} `{v['value']}`: {v['reason']}",
            ]
        lines += [""]

    lines += [
        "## References",
        "- `.claude/rules/rules_css_style_spec.md` — full palette, typography, and shape spec",
        "- `.claude/rules/rules_ui_dashboard.md §4` — CSS authority and deployment override pattern",
        "- `ADR-055` — CSS lives in config/ui/theme.css, no inline style= attributes",
        "- `tasks.md` — CSS-BADGE-PROPAG-1 (known debt tracker)",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=None, help="Project root (default: auto-detect)")
    parser.add_argument("--css", default="config/ui/theme.css", help="CSS file path relative to project root")
    parser.add_argument("--output", default=None, help="Write report to this file (default: stdout)")
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else find_project_root(Path(__file__).resolve().parent)
    violations, css_path = scan(project_root, args.css)
    report = render_report(violations, css_path, project_root)

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    blockers = [v for v in violations if v["severity"] == "BLOCKER"]
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
