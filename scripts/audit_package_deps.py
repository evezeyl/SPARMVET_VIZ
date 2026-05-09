#!/usr/bin/env python3
"""Audit: Package dependency health check.

Reports the health of all installed dependencies from three angles:

  1. Outdated packages — packages installed in .venv that have newer versions
     on PyPI. Grouped by update type (PATCH / MINOR / MAJOR) and cross-
     referenced with which project library declares them.

  2. Conflict detection — runs `pip check` to find installed packages with
     incompatible dependency requirements (dependency hell detection).

  3. Parity mandate alert — for packages governed by parity mandates (Polars
     → ADR-035, Plotnine → ADR-036), flags when an update contains new API
     surface that should be reflected in the transformer/viz_factory action
     registries.

NOTE on false positives: Local editable packages (installed via `pip install -e`)
that share a name with a PyPI package will appear in `pip list --outdated` with
a misleading "latest" version. This script detects editable installs and marks
them as LOCAL (excluded from update recommendations).

This audit is informational — it does not modify anything. Run before a release,
after a dependency freeze review, or after a long period without dependency
updates.

Usage:
  .venv/bin/python scripts/audit_package_deps.py
  .venv/bin/python scripts/audit_package_deps.py --output .claude/logs/audits/audit_package_deps_2026-05-12.md
  .venv/bin/python scripts/audit_package_deps.py --project-root /path/to/project
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Packages governed by parity mandates — updates need an action registry review
PARITY_MANDATE_PACKAGES = {
    "polars": {
        "adr": "ADR-035",
        "registry": "libs/transformer/src/transformer/actions/",
        "rule": "rules_data_engine.md §5 — The Polars Parity Mandate",
        "note": "New Polars release may expose new expressions or functions. "
                "Run a transformer action inventory audit to identify gaps.",
    },
    "plotnine": {
        "adr": "ADR-036",
        "registry": "libs/viz_factory/src/viz_factory/",
        "rule": "rules_viz_factory.md §1 — The Artist Parity Mandate",
        "note": "New Plotnine release may add new geoms, stats, scales, or themes. "
                "Run a VizFactory component inventory audit to identify gaps.",
    },
}

# Packages where updates carry known stability risk for this stack
HIGH_ATTENTION_PACKAGES = {
    "shiny", "shinyswatch", "shinychat",
    "polars", "plotnine",
    "playwright", "pytest-playwright",
}


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


# ── Collect declared dependencies from all pyproject.toml files ───────────────

def collect_declared_deps(project_root: Path) -> dict[str, list[str]]:
    """Return {pkg_name_lower: [declaring_component, ...]} from all pyproject.toml."""
    declared: dict[str, list[str]] = {}
    for toml_path in sorted(project_root.rglob("pyproject.toml")):
        if ".venv" in toml_path.parts or "dist" in toml_path.parts:
            continue
        component = toml_path.parent.name
        try:
            text = toml_path.read_text(encoding="utf-8")
        except OSError:
            continue
        in_deps = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "dependencies = [":
                in_deps = True
                continue
            if in_deps:
                if stripped == "]":
                    in_deps = False
                    continue
                # Extract package name from specifier like "polars>=1.0.0"
                m = re.match(r'"?([A-Za-z0-9_.-]+)', stripped)
                if m:
                    pkg = m.group(1).lower().replace("-", "_").replace(".", "_")
                    declared.setdefault(pkg, [])
                    if component not in declared[pkg]:
                        declared[pkg].append(component)
    return declared


# ── Detect local editable installs ────────────────────────────────────────────

def get_editable_packages(python_bin: Path) -> set[str]:
    """Return set of package names installed as editable (-e) installs."""
    result = subprocess.run(
        [str(python_bin), "-m", "pip", "list", "--editable", "--format=json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return set()
    try:
        pkgs = json.loads(result.stdout)
        return {p["name"].lower().replace("-", "_") for p in pkgs}
    except (json.JSONDecodeError, KeyError):
        return set()


# ── Outdated packages ─────────────────────────────────────────────────────────

def get_outdated(python_bin: Path) -> list[dict]:
    result = subprocess.run(
        [str(python_bin), "-m", "pip", "list", "--outdated", "--format=json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def classify_update(current: str, latest: str) -> str:
    """Return MAJOR / MINOR / PATCH based on semantic version bump."""
    try:
        cur = [int(x) for x in current.split(".")[:3]]
        new = [int(x) for x in latest.split(".")[:3]]
        while len(cur) < 3:
            cur.append(0)
        while len(new) < 3:
            new.append(0)
        if new[0] > cur[0]:
            return "MAJOR"
        if new[1] > cur[1]:
            return "MINOR"
        return "PATCH"
    except (ValueError, AttributeError):
        return "UNKNOWN"


# ── Conflict detection ────────────────────────────────────────────────────────

def get_conflicts(python_bin: Path) -> tuple[int, str]:
    result = subprocess.run(
        [str(python_bin), "-m", "pip", "check"],
        capture_output=True, text=True,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


# ── Report ─────────────────────────────────────────────────────────────────────

def render_report(
    outdated: list[dict],
    editable: set[str],
    conflicts_code: int,
    conflicts_output: str,
    declared: dict[str, list[str]],
    project_root: Path,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")

    # Filter out editable/local packages — they are false positives
    real_outdated = [
        p for p in outdated
        if p["name"].lower().replace("-", "_") not in editable
    ]
    false_positives = [p for p in outdated if p not in real_outdated]

    # Classify
    major = [p for p in real_outdated if classify_update(p["version"], p["latest_version"]) == "MAJOR"]
    minor = [p for p in real_outdated if classify_update(p["version"], p["latest_version"]) == "MINOR"]
    patch = [p for p in real_outdated if classify_update(p["version"], p["latest_version"]) == "PATCH"]

    parity_hits = [
        p for p in real_outdated
        if p["name"].lower() in PARITY_MANDATE_PACKAGES
    ]

    lines = [
        "# Audit Report: Package Dependency Health",
        f"Generated: {now}",
        f"Project root: {project_root}",
        "Rule: ADR-035 (Polars Parity), ADR-036 (Artist Parity), ADR-071 (No CDN — vendored assets)",
        "",
        f"- Outdated packages (real): {len(real_outdated)}",
        f"  - MAJOR updates: {len(major)}",
        f"  - MINOR updates: {len(minor)}",
        f"  - PATCH updates: {len(patch)}",
        f"- Local editable packages (excluded — false positives): {len(false_positives)}",
        f"- Dependency conflicts: {'❌ YES' if conflicts_code != 0 else '✅ None'}",
        f"- Parity mandate packages with updates: {len(parity_hits)}",
        "",
    ]

    # Conflict section — highest priority
    if conflicts_code != 0:
        lines += [
            "## ❌ CRITICAL: Dependency Conflicts Detected",
            "",
            "These must be resolved before any deployment:",
            "```",
            conflicts_output,
            "```",
            "",
            "**Fix:** Run `pip check` interactively, then update conflicting packages one at a time.",
            "Test the app after each update: `python -c 'from app.src.main import app; print(\"OK\")'`",
            "",
        ]
    else:
        lines += ["## ✅ No Dependency Conflicts", "", "`pip check` reports no incompatibilities.", ""]

    # Parity mandate alerts
    if parity_hits:
        lines += ["## ⚠️ Parity Mandate Packages With Updates", ""]
        for p in parity_hits:
            info = PARITY_MANDATE_PACKAGES[p["name"].lower()]
            update_type = classify_update(p["version"], p["latest_version"])
            lines += [
                f"### `{p['name']}` {p['version']} → {p['latest_version']} ({update_type})",
                f"- **ADR:** {info['adr']}",
                f"- **Registry:** `{info['registry']}`",
                f"- **Rule:** `{info['rule']}`",
                f"- **Action required:** {info['note']}",
                f"- Check the [{p['name']} changelog](https://github.com/{'pola-rs/polars' if 'polars' in p['name'] else 'has2k1/plotnine'}/releases) "
                f"for new API additions since {p['version']}.",
                "",
            ]

    # Major updates — require careful review
    if major:
        lines += ["## 🔴 MAJOR Updates (review before upgrading)", ""]
        for p in major:
            key = p["name"].lower().replace("-", "_")
            owners = declared.get(key, ["(root or transitive)"])
            lines += [
                f"- `{p['name']}` **{p['version']} → {p['latest_version']}** "
                f"— declared by: {', '.join(owners)}"
            ]
        lines += [
            "",
            "MAJOR updates may contain breaking API changes. Review the release notes before upgrading.",
            "Test locally: `pip install <package>==<latest>` then run the full test suite.",
            "",
        ]

    # Minor updates — may contain features
    if minor:
        lines += ["## 🟡 MINOR Updates (feature additions — consider upgrading)", ""]
        for p in minor:
            key = p["name"].lower().replace("-", "_")
            owners = declared.get(key, ["(root or transitive)"])
            attention = " ⚠️" if p["name"].lower() in HIGH_ATTENTION_PACKAGES else ""
            lines += [
                f"- `{p['name']}` {p['version']} → {p['latest_version']}{attention} "
                f"— declared by: {', '.join(owners)}"
            ]
        lines += [""]

    # Patch updates — bug fixes and security patches
    if patch:
        lines += ["## 🟢 PATCH Updates (bug fixes — recommended)", ""]
        for p in patch:
            key = p["name"].lower().replace("-", "_")
            owners = declared.get(key, ["(root or transitive)"])
            attention = " ⚠️" if p["name"].lower() in HIGH_ATTENTION_PACKAGES else ""
            lines += [
                f"- `{p['name']}` {p['version']} → {p['latest_version']}{attention} "
                f"— declared by: {', '.join(owners)}"
            ]
        lines += [
            "",
            "Patch updates typically contain only bug fixes and are low-risk to apply.",
            "Upgrade in a batch: `pip install <p1> <p2> ... --upgrade` then re-run tests.",
            "",
        ]

    # False positives (local editable packages)
    if false_positives:
        lines += [
            "## ℹ️ Local Packages (excluded — editable installs)",
            "",
            "These appear in `pip list --outdated` because a PyPI package of the same name exists.",
            "They are local editable installs and do not need updating via pip.",
            "",
        ]
        for p in false_positives:
            lines += [f"- `{p['name']}` (local editable — ignoring PyPI version {p['latest_version']})"]
        lines += [""]

    # Upgrade guidance
    lines += [
        "## Upgrade Protocol",
        "",
        "**For PATCH updates (batch upgrade):**",
        "```bash",
        "# Upgrade low-risk packages together",
        ".venv/bin/pip install --upgrade " + " ".join(
            p["name"] for p in patch[:5]
        ) if patch else "# (no patch updates)",
        "# Verify no regressions",
        ".venv/bin/python -c 'from app.src.main import app; print(\"import OK\")'",
        "PYTHONPATH=. SPARMVET_PERSONA=qa .venv/bin/python -m pytest app/tests/test_filter_operators.py -q",
        "```",
        "",
        "**For MINOR / MAJOR updates (one at a time):**",
        "```bash",
        "# Update one package",
        ".venv/bin/pip install '<package>==<latest>'",
        "# Run full smoke tests",
        "PYTHONPATH=. SPARMVET_PERSONA=qa .venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v",
        "# If parity mandate package: run action/component inventory audit",
        ".venv/bin/python scripts/audit_library_tests.py --lib transformer  # or viz_factory",
        "```",
        "",
        "## References",
        "- `rules_data_engine.md §5` — Polars Parity Mandate (ADR-035)",
        "- `rules_viz_factory.md §1` — Artist Parity Mandate (ADR-036)",
        "- `rules_verification_testing.md §8` — Playwright smoke testing after updates",
        "- Routine 11 (Package dependency health) in `.claude/workflows/audit_routine_registry.md`",
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

    print("Collecting declared dependencies ...", file=sys.stderr)
    declared = collect_declared_deps(project_root)

    print("Detecting editable (local) packages ...", file=sys.stderr)
    editable = get_editable_packages(python_bin)

    print("Checking for outdated packages ...", file=sys.stderr)
    outdated = get_outdated(python_bin)

    print("Running pip check (conflict detection) ...", file=sys.stderr)
    conflicts_code, conflicts_output = get_conflicts(python_bin)

    report = render_report(outdated, editable, conflicts_code, conflicts_output, declared, project_root)
    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    real_outdated = [
        p for p in outdated
        if p["name"].lower().replace("-", "_") not in editable
    ]
    has_major = any(classify_update(p["version"], p["latest_version"]) == "MAJOR" for p in real_outdated)
    return 1 if (conflicts_code != 0 or has_major) else 0


if __name__ == "__main__":
    sys.exit(main())
