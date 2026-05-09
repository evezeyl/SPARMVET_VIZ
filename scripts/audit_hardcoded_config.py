#!/usr/bin/env python3
"""Audit: Hardcoded configuration and path violations (ADR-048, ADR-031, ADR-053).

Detects three classes of hardcoding that make the app fragile or deployment-specific:

  1. ABSOLUTE PATHS in app/ and libs/ Python code — any string literal matching
     /home/, /etc/, /usr/, /var/, /mnt/ etc. will break on a different machine or
     inside a Galaxy/IRIDA container.

  2. DIRECT LOCATION READS bypassing the bootloader — code reading locations directly
     from a profile dict (e.g. `profile["locations"]["raw_data"]`) instead of calling
     `bootloader.get_location("raw_data")`. The bootloader runs connector.resolve_paths()
     which normalises and validates locations; bypassing it silently uses unvalidated paths.

  3. PERSONA NAME STRING COMPARISONS in runtime UI code — if/elif chains like
     `if persona == "developer"` break silently when a custom persona template is deployed.
     All gating must use `bootloader.is_enabled(flag)`. (ADR-053)

  4. HARDCODED ENV VAR READS for deployment config outside bootloader — e.g.
     `os.environ.get("SPARMVET_PERSONA")` in handler files. Bootloader owns this.

  5. HARDCODED INTERPRETER PATH — `python3` or `/usr/bin/python` used as a subprocess
     call in app/ or libs/ code instead of the `.venv` Python. (rules_runtime_environment.md)

Scan scope: app/ and libs/ Python source files. Excludes: scripts/, assets/scripts/,
tests/, tmpAI/, tmp/, config/ (profiles are allowed to have relative paths).

Usage:
  .venv/bin/python scripts/audit_hardcoded_config.py
  .venv/bin/python scripts/audit_hardcoded_config.py --output .claude/logs/audits/audit_hardcoded_2026-05-09.md
  .venv/bin/python scripts/audit_hardcoded_config.py --project-root /path/to/project --output report.md
"""
import argparse
import ast
import re
import sys
from datetime import datetime
from pathlib import Path


# ── Scan scope ────────────────────────────────────────────────────────────────
# Directories to scan (relative to project root)
SCAN_DIRS = ["app", "libs"]
# Subdirectories to skip (matched against any path component)
SKIP_DIRS = {"tests", "tmpAI", "tmp", "__pycache__", ".venv", "archives"}
# Files to skip entirely
SKIP_FILES = {
    "bootloader.py",       # owns profile/persona/env-var reads — intentional
    "connector.py",        # owns location resolution — intentional
    "local_connector.py",  # filesystem connector — reads raw_data etc by design
    "filesystem.py",       # filesystem connector implementation — reads profile locations by design
    "galaxy.py",           # Galaxy connector implementation — reads profile locations by design
    "galaxy_connector.py", # Galaxy connector variant
    "irida.py",            # IRIDA connector implementation
    "base.py",             # connector base class — may read profile dict
}

# ── Detection patterns ────────────────────────────────────────────────────────

# 1. Absolute path patterns — strings that look like absolute filesystem paths
#    Captured as string literals (single or double quoted)
ABSOLUTE_PATH_PATTERNS = [
    (re.compile(r'["\']\/home\/[^"\']+["\']'),   "Absolute /home/ path"),
    (re.compile(r'["\']\/etc\/[^"\']+["\']'),    "Absolute /etc/ path"),
    (re.compile(r'["\']\/usr\/[^"\']+["\']'),    "Absolute /usr/ path"),
    (re.compile(r'["\']\/var\/[^"\']+["\']'),    "Absolute /var/ path"),
    (re.compile(r'["\']\/mnt\/[^"\']+["\']'),    "Absolute /mnt/ path"),
    (re.compile(r'["\']\/opt\/[^"\']+["\']'),    "Absolute /opt/ path"),
    (re.compile(r'["\']\/data\/[^"\']+["\']'),   "Absolute /data/ path"),
    (re.compile(r'["\']\/srv\/[^"\']+["\']'),    "Absolute /srv/ path"),
    (re.compile(r'["\']\/galaxy\/[^"\']+["\']'), "Absolute /galaxy/ path"),
]

# 2. Direct location reads — accessing locations dict without bootloader
DIRECT_LOCATION_PATTERNS = [
    (re.compile(r'profile\s*\[\s*["\']locations["\']'),
     "Direct profile['locations'] read — use bootloader.get_location(key) instead"),
    (re.compile(r'locations\s*\[\s*["\'](?:raw_data|manifests|curated_data|user_sessions|gallery)["\']'),
     "Direct locations[key] read — use bootloader.get_location(key) instead"),
    (re.compile(r'\.get\s*\(\s*["\']locations["\']'),
     "profile.get('locations') read — use bootloader.get_location(key) instead"),
]

# 3. Persona name string comparisons in runtime code (ADR-053)
PERSONA_NAME_PATTERNS = [
    (re.compile(r'\bpersona\s*==\s*["\']'),
     "Persona name string comparison — use bootloader.is_enabled(flag) instead (ADR-053)"),
    (re.compile(r'\bpersona\s+in\s*\('),
     "Persona name in-tuple comparison — use bootloader.is_enabled(flag) instead (ADR-053)"),
    (re.compile(r'\bpersona\s+in\s*\['),
     "Persona name in-list comparison — use bootloader.is_enabled(flag) instead (ADR-053)"),
    (re.compile(r'SPARMVET_PERSONA.*=='),
     "SPARMVET_PERSONA env-var string comparison — bootloader owns persona resolution"),
]

# 4. Env var reads for deployment config outside bootloader
ENV_VAR_PATTERNS = [
    (re.compile(r'os\.environ(?:\.get)?\s*\(\s*["\']SPARMVET_PERSONA["\']'),
     "Direct SPARMVET_PERSONA env-var read — bootloader owns persona resolution"),
    (re.compile(r'os\.environ(?:\.get)?\s*\(\s*["\']SPARMVET_PROFILE["\']'),
     "Direct SPARMVET_PROFILE env-var read — bootloader owns profile resolution"),
]

# 5. Hardcoded Python interpreter in subprocess calls
INTERPRETER_PATTERNS = [
    (re.compile(r'subprocess.*["\']python3["\']'),
     "Hardcoded 'python3' in subprocess — use bootloader.get_python_path() or profile runtime.python_interpreter"),
    (re.compile(r'subprocess.*["\']\/usr\/bin\/python'),
     "Hardcoded /usr/bin/python in subprocess — use venv interpreter path"),
    (re.compile(r'subprocess.*["\']\/usr\/bin\/env python'),
     "Hardcoded /usr/bin/env python in subprocess — use venv interpreter path"),
]

# ── Known-debt exceptions ─────────────────────────────────────────────────────
# File+line fragments that are known acceptable hardcodings or pre-existing debt.
# Format: (file_substring, pattern_description_substring)
KNOWN_DEBT: list[tuple[str, str]] = [
    # Bootloader intentionally reads SPARMVET_PERSONA and SPARMVET_PROFILE
    ("bootloader.py", "SPARMVET_"),
    # Connector legitimately accesses profile['locations']
    ("connector.py", "locations"),
    # local_connector resolves raw_data etc. by design
    ("local_connector.py", "locations"),
]


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def should_skip(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return True
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False


def is_known_debt(filepath: str, reason: str) -> bool:
    for file_frag, reason_frag in KNOWN_DEBT:
        if file_frag in filepath and reason_frag in reason:
            return True
    return False


def scan_file(path: Path, project_root: Path) -> list[dict]:
    violations = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return violations

    rel = str(path.relative_to(project_root))
    lines = text.splitlines()

    all_pattern_groups = [
        ("absolute_path",   ABSOLUTE_PATH_PATTERNS,   "BLOCKER"),
        ("direct_location", DIRECT_LOCATION_PATTERNS, "BLOCKER"),
        ("persona_name",    PERSONA_NAME_PATTERNS,     "BLOCKER"),
        ("env_var",         ENV_VAR_PATTERNS,          "BLOCKER"),
        ("interpreter",     INTERPRETER_PATTERNS,      "BLOCKER"),
    ]

    for category, patterns, default_sev in all_pattern_groups:
        for patt, reason in patterns:
            for lineno, line in enumerate(lines, start=1):
                stripped = line.strip()
                # Skip pure comment lines (Python # comments)
                if stripped.startswith("#"):
                    continue
                if not patt.search(line):
                    continue

                severity = default_sev
                if is_known_debt(rel, reason):
                    severity = "KNOWN_DEBT"

                violations.append({
                    "file": rel,
                    "line": lineno,
                    "category": category,
                    "severity": severity,
                    "reason": reason,
                    "snippet": stripped[:120],
                })

    return violations


def scan(project_root: Path) -> list[dict]:
    violations = []
    for scan_dir in SCAN_DIRS:
        base = project_root / scan_dir
        if not base.exists():
            continue
        for py_file in sorted(base.rglob("*.py")):
            if should_skip(py_file):
                continue
            violations += scan_file(py_file, project_root)
    return violations


def render_report(violations: list[dict], project_root: Path) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    blockers = [v for v in violations if v["severity"] == "BLOCKER"]
    debt = [v for v in violations if v["severity"] == "KNOWN_DEBT"]

    lines = [
        "# Audit Report: Hardcoded Configuration & Path Violations",
        f"Generated: {now}",
        f"Project root: {project_root}",
        "Rule: ADR-048 (deployment profile), ADR-031 (bootloader), ADR-053 (no persona name checks)",
        "",
    ]

    status = "❌ FAIL" if blockers else ("⚠️ PASS (known debt only)" if debt else "✅ PASS")
    lines += [f"## Result: {status}", ""]
    lines += [
        f"- Blockers (must fix): {len(blockers)}",
        f"- Known-debt (tracked): {len(debt)}",
        "",
    ]

    if blockers:
        # Group by category for readability
        categories = {
            "absolute_path":   ("❌ Absolute Path Strings", "Replace with bootloader.get_location(key) or a relative path resolved at runtime."),
            "direct_location": ("❌ Direct Location Dict Reads", "Call bootloader.get_location(key) — never read locations from the profile dict directly."),
            "persona_name":    ("❌ Persona Name String Comparisons", "Replace with bootloader.is_enabled('flag_name'). See ADR-053 and rules_persona_feature_flags.md §Anti-Pattern."),
            "env_var":         ("❌ Direct Env-Var Reads for Deployment Config", "Bootloader owns SPARMVET_PERSONA and SPARMVET_PROFILE resolution. Never read these in handler code."),
            "interpreter":     ("❌ Hardcoded Python Interpreter", "Use the venv Python path from bootloader or subprocess with sys.executable from the active venv."),
        }
        for cat, (heading, fix_advice) in categories.items():
            cat_violations = [v for v in blockers if v["category"] == cat]
            if not cat_violations:
                continue
            lines += [f"## {heading}", "", f"**Fix:** {fix_advice}", ""]
            for v in cat_violations:
                lines += [
                    f"### `{v['file']}:{v['line']}`",
                    f"- **Reason:** {v['reason']}",
                    f"- **Code:** `{v['snippet']}`",
                    "",
                ]

    if debt:
        lines += ["## ⚠️ Known-Debt Violations (expected, tracked)", ""]
        for v in debt:
            lines += [
                f"- `{v['file']}:{v['line']}` [{v['category']}]: {v['reason']}",
            ]
        lines += [""]

    lines += [
        "## Scan Scope",
        f"- Directories scanned: {', '.join(SCAN_DIRS)}",
        f"- Skipped dirs: {', '.join(sorted(SKIP_DIRS))}",
        f"- Skipped files: {', '.join(sorted(SKIP_FILES))}",
        "",
        "## References",
        "- `ADR-048` — Deployment Profile & Connector Abstraction",
        "- `ADR-031` — Bootloader owns path and persona resolution",
        "- `ADR-053` — No persona name string comparisons in runtime code",
        "- `.claude/rules/rules_runtime_environment.md §1` — venv enforcement",
        "- `.claude/rules/rules_persona_feature_flags.md §Anti-Pattern` — is_enabled() pattern",
        "- `config/deployment/local/local_profile.yaml` — reference for allowed location keys",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=None, help="Project root (default: auto-detect)")
    parser.add_argument("--output", default=None, help="Write report to this file (default: stdout)")
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else find_project_root(Path(__file__).resolve().parent)
    violations = scan(project_root)
    report = render_report(violations, project_root)

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
