"""
Manifest migration utility — rename action or plot-component names across all manifests.

Usage examples:

  # Dry-run: show which files and lines would change
  .venv/bin/python scripts/migrate_manifests.py --old rename_column --new rename_columns --dry-run

  # Apply rename to all manifests under config/ and assets/gallery_data/
  .venv/bin/python scripts/migrate_manifests.py --old rename_column --new rename_columns

  # Restrict to a specific directory
  .venv/bin/python scripts/migrate_manifests.py --old rename_column --new rename_columns \
      --roots config/manifests/

  # List all unique action names and component names referenced in manifests
  .venv/bin/python scripts/migrate_manifests.py --inventory

Purpose
-------
When an @register_action or @register_plot_component name changes, all YAML manifests that
use the old name must be updated. This script performs a safe, context-aware string replacement
so that only values under the `action:` key (for wrangling steps) or the `name:` key inside
`layers:` blocks (for plot components) are changed — free-text in YAML strings is untouched.

Context-aware matching
-----------------------
The script matches lines of the form:

    action: <old_name>       # in wrangling / assembly recipe steps
    - name: <old_name>       # in plot spec layers

Both forms are matched with optional leading whitespace. The replacement preserves indentation.

Limitations
-----------
- `factory_id:` values (e.g. bar_logic, scatter_logic) are separate from component names and
  are NOT renamed by this script. Factory IDs map to render functions, not registered components.
- `target_dataset:` values are join manifest keys — not touched here.
- If a manifest uses YAML anchors or complex multi-document structures, manual review after
  migration is recommended.

After running
-------------
1. Review the diff (git diff config/ assets/gallery_data/) before committing.
2. Restart the app and verify startup logs show no "action not registered" warnings.
3. Run the debug assembler on affected pipelines to confirm pipeline output is unchanged.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --- patterns ----------------------------------------------------------------

# Matches:   action: <name>   (possibly leading whitespace)
_ACTION_PATTERN = re.compile(r'^(\s*-?\s*action:\s*)(\S+)', re.MULTILINE)

# Matches:   - name: <name>   inside a layers: block
# We use a simple heuristic: any "  - name: <value>" line.
_COMPONENT_NAME_PATTERN = re.compile(r'^(\s*-\s+name:\s*)(\S+)', re.MULTILINE)

# --- discovery ---------------------------------------------------------------

_DEFAULT_ROOTS = [
    "config/manifests",
    "assets/gallery_data",
]


def _find_yaml_files(roots: list[str]) -> list[Path]:
    files = []
    for root in roots:
        p = Path(root)
        if p.is_dir():
            files.extend(p.rglob("*.yaml"))
            files.extend(p.rglob("*.yml"))
        elif p.is_file():
            files.append(p)
    return sorted(set(files))


def _collect_inventory(files: list[Path]) -> dict[str, set[str]]:
    actions: set[str] = set()
    components: set[str] = set()
    for f in files:
        text = f.read_text(encoding="utf-8")
        for m in _ACTION_PATTERN.finditer(text):
            actions.add(m.group(2))
        for m in _COMPONENT_NAME_PATTERN.finditer(text):
            components.add(m.group(2))
    return {"actions": actions, "components": components}


# --- migration ---------------------------------------------------------------

def _migrate_file(path: Path, old: str, new: str, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    original = text

    def _replace_action(m: re.Match) -> str:
        if m.group(2) == old:
            return m.group(1) + new
        return m.group(0)

    def _replace_component(m: re.Match) -> str:
        if m.group(2) == old:
            return m.group(1) + new
        return m.group(0)

    text = _ACTION_PATTERN.sub(_replace_action, text)
    text = _COMPONENT_NAME_PATTERN.sub(_replace_component, text)

    changed_lines = 0
    if text != original:
        orig_lines = original.splitlines()
        new_lines = text.splitlines()
        for i, (ol, nl) in enumerate(zip(orig_lines, new_lines)):
            if ol != nl:
                print(f"  {path}:{i+1}  -{ol.strip()}  +{nl.strip()}")
                changed_lines += 1
        if not dry_run:
            path.write_text(text, encoding="utf-8")

    return changed_lines


# --- entry point -------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rename action or plot-component names across SPARMVET YAML manifests. "
            "Context-aware: only values under 'action:' or '- name:' keys are touched."
        )
    )
    parser.add_argument("--old", metavar="OLD_NAME",
                        help="Name to replace (exact match).")
    parser.add_argument("--new", metavar="NEW_NAME",
                        help="Replacement name.")
    parser.add_argument("--roots", nargs="+", default=_DEFAULT_ROOTS,
                        metavar="DIR",
                        help="Directories to search (default: config/manifests assets/gallery_data).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print changes without writing files.")
    parser.add_argument("--inventory", action="store_true",
                        help="List all unique action/component names referenced in manifests.")

    args = parser.parse_args()

    files = _find_yaml_files(args.roots)
    if not files:
        print(f"No YAML files found under: {args.roots}")
        return 1

    if args.inventory:
        inv = _collect_inventory(files)
        print(f"\nFound {len(files)} YAML files in {args.roots}\n")
        print("=== Action names (under 'action:') ===")
        for name in sorted(inv["actions"]):
            print(f"  {name}")
        print(f"\n=== Component names (under '- name:') ===")
        for name in sorted(inv["components"]):
            print(f"  {name}")
        return 0

    if not args.old or not args.new:
        parser.error("--old and --new are required unless --inventory is specified.")

    if args.old == args.new:
        print("Old and new names are identical — nothing to do.")
        return 0

    mode = "DRY RUN" if args.dry_run else "APPLYING"
    print(f"{mode}: rename '{args.old}' -> '{args.new}' across {len(files)} files")
    print()

    total_changes = 0
    changed_files = 0
    for f in files:
        n = _migrate_file(f, args.old, args.new, args.dry_run)
        if n:
            changed_files += 1
            total_changes += n

    if total_changes == 0:
        print(f"No occurrences of '{args.old}' found.")
    else:
        verb = "would change" if args.dry_run else "changed"
        print(f"\n{verb} {total_changes} line(s) in {changed_files} file(s).")
        if args.dry_run:
            print("Re-run without --dry-run to apply.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
