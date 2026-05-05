#!/usr/bin/env python3
# @deps
# provides: script:normalize_manifest_fields
# consumes: config/manifests/ (YAML files)
# doc: .claude/rules/rules_data_engine.md#4
# @end_deps
"""
normalize_manifest_fields.py
----------------------------
Sanitizes SPARMVET YAML manifests to comply with the ADR-041 Rich Dictionary standard.

The canonical format for input_fields / output_fields is:
  slug:                       # snake_case key — used for O(1) lookup
    original_name: "RawCol"   # exact column name in the source file
    type: categorical          # categorical | numeric | date | boolean
    label: "Human Label"       # display label in UI

This script detects legacy list-format or flat-dict-format entries and converts
them to the Rich Dictionary format. It also flags wrangling blocks that use a flat
list (instead of the required tiered structure) and reports them for manual review.

Usage:
  # Dry-run — inspect only, no files written:
  ./.venv/bin/python assets/scripts/normalize_manifest_fields.py --manifest path/to/manifest.yaml

  # Apply fixes:
  ./.venv/bin/python assets/scripts/normalize_manifest_fields.py --manifest path/to/manifest.yaml --write

  # Scan all manifests under a directory:
  ./.venv/bin/python assets/scripts/normalize_manifest_fields.py --dir config/manifests/

Options:
  --manifest   Path to a single YAML manifest to inspect / normalize.
  --dir        Directory to scan recursively for *.yaml files.
  --write      Write normalized manifests back to disk (default: dry-run).
  --no-backup  Skip creating a .bak copy before writing (default: create backup).
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml


# ── Type mapping helpers ──────────────────────────────────────────────────────

_LEGACY_TYPE_MAP = {
    # Polars-style or old schema strings → ADR-041 canonical types
    "string": "categorical",
    "str": "categorical",
    "utf8": "categorical",
    "character": "categorical",
    "object": "categorical",
    "int": "numeric",
    "int32": "numeric",
    "int64": "numeric",
    "float": "numeric",
    "float32": "numeric",
    "float64": "numeric",
    "double": "numeric",
    "bool": "boolean",
    "boolean": "boolean",
    "date": "date",
    "datetime": "date",
    "timestamp": "date",
    # Already canonical
    "categorical": "categorical",
    "numeric": "numeric",
}


def _canonical_type(raw_type: str) -> str:
    return _LEGACY_TYPE_MAP.get(str(raw_type).lower().strip(), str(raw_type))


def _slug(col_name: str) -> str:
    """Convert a raw column name to a snake_case slug."""
    s = str(col_name).lower()
    s = re.sub(r'[/.:\s\-]+', '_', s)
    s = re.sub(r'[^\w_]', '', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_')


# ── Field normalization ───────────────────────────────────────────────────────

def _normalize_fields(fields, path: str):
    """
    Converts a fields value to the ADR-041 Rich Dictionary format:
      slug: {original_name, type, label}

    Accepts:
      - Rich Dict (already standard): {slug: {original_name, type, label, ...}} → unchanged
      - Flat Dict (legacy):           {col: type_string} → convert
      - List (old list format):       [{name, dtype|type, ...}] → convert

    Returns (normalized_dict, changes: list[str]).
    """
    changes = []

    if isinstance(fields, dict):
        # Check if this looks like a Rich Dictionary (values are dicts) or flat (values are strings)
        if not fields:
            return fields, []

        first_val = next(iter(fields.values()))

        if isinstance(first_val, dict):
            # Already Rich Dictionary — validate and fill missing keys
            out = {}
            for slug, props in fields.items():
                entry = dict(props)
                fixed = False
                if "original_name" not in entry:
                    entry["original_name"] = slug
                    fixed = True
                if "type" not in entry:
                    entry["type"] = "categorical"
                    fixed = True
                else:
                    canonical = _canonical_type(entry["type"])
                    if canonical != entry["type"]:
                        entry["type"] = canonical
                        fixed = True
                if "label" not in entry:
                    entry["label"] = slug.replace("_", " ").title()
                    fixed = True
                if fixed:
                    changes.append(f"  [{path}] filled missing keys on slug '{slug}'")
                out[slug] = entry
            return out, changes

        else:
            # Flat dict: {col_name: type_string}
            out = {}
            for col, raw_type in fields.items():
                s = _slug(col)
                out[s] = {
                    "original_name": col,
                    "type": _canonical_type(str(raw_type)),
                    "label": col.replace("_", " ").title(),
                }
            changes.append(f"  [{path}]: converted flat dict {{col: type}} → Rich Dict")
            return out, changes

    if isinstance(fields, list):
        if not fields:
            # Empty list [] → empty Rich Dict {} (ADR-041: correct empty form)
            return {}, [f"  [{path}]: converted empty list [] → empty dict {{}}"]
        out = {}
        for item in fields:
            if isinstance(item, dict):
                col = item.get("name", item.get("field", item.get("slug", "unknown")))
                raw_type = item.get("type", item.get("dtype", "categorical"))
                s = _slug(col)
                out[s] = {
                    "original_name": item.get("original_name", col),
                    "type": _canonical_type(str(raw_type)),
                    "label": item.get("label", col.replace("_", " ").title()),
                }
            else:
                s = _slug(str(item))
                out[s] = {
                    "original_name": str(item),
                    "type": "categorical",
                    "label": str(item).replace("_", " ").title(),
                }
        changes.append(f"  [{path}]: converted list format → Rich Dict")
        return out, changes

    return fields, []


def _fix_wrangling(wrangling, path: str):
    """
    Ensures a wrangling block uses the required tiered structure.
    A flat list (legacy) is auto-converted to {tier1: [...]} — tier placement
    is unambiguous since flat lists have no tier2 by definition.
    Returns (fixed_wrangling, changes: list[str]).
    """
    changes = []
    if isinstance(wrangling, list) and len(wrangling) > 0:
        changes.append(
            f"  [{path}]: converted flat wrangling list → tiered {{tier1: [...]}}"
        )
        return {"tier1": wrangling}, changes
    return wrangling, changes


def _walk_and_normalize(obj, path="root"):
    """
    Recursively walks a parsed YAML structure, normalizing all input_fields /
    output_fields entries to Rich Dictionary format, and flagging flat wrangling.
    Returns (obj, changes: list[str], warnings: list[str]).
    """
    changes = []
    warnings = []

    if isinstance(obj, dict):
        for key, val in list(obj.items()):
            full_path = f"{path}.{key}"
            if key in ("input_fields", "output_fields"):
                normalized, field_changes = _normalize_fields(val, full_path)
                if field_changes:
                    changes.extend(field_changes)
                    obj[key] = normalized
            elif key == "final_contract":
                # final_contract must be a dict {col: type_string} or empty {}.
                # An empty list [] is corrected to {}.
                # Values that are None or empty dict {} are corrected to "string".
                if isinstance(val, list) and not val:
                    changes.append(f"  [{full_path}]: converted empty list [] → empty dict {{}}")
                    obj[key] = {}
                elif isinstance(val, dict) and val:
                    fixed_fc = {}
                    fc_changed = False
                    for col, type_val in val.items():
                        if not type_val or type_val == {}:
                            fixed_fc[col] = "string"
                            fc_changed = True
                        else:
                            fixed_fc[col] = type_val
                    if fc_changed:
                        changes.append(f"  [{full_path}]: filled empty type values → 'string'")
                        obj[key] = fixed_fc
            elif key == "wrangling":
                fixed_wrangling, wrangling_changes = _fix_wrangling(val, full_path)
                if wrangling_changes:
                    changes.extend(wrangling_changes)
                    obj[key] = fixed_wrangling
                    val = fixed_wrangling
                # Recurse into wrangling dict (e.g. tier1/tier2 lists) but don't normalize fields there
                sub_obj, sub_changes, sub_warnings = _walk_and_normalize(val, full_path)
                obj[key] = sub_obj
                changes.extend(sub_changes)
                warnings.extend(sub_warnings)
            else:
                sub_obj, sub_changes, sub_warnings = _walk_and_normalize(val, full_path)
                obj[key] = sub_obj
                changes.extend(sub_changes)
                warnings.extend(sub_warnings)

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            sub_obj, sub_changes, sub_warnings = _walk_and_normalize(item, f"{path}[{i}]")
            obj[i] = sub_obj
            changes.extend(sub_changes)
            warnings.extend(sub_warnings)

    return obj, changes, warnings


# ── YAML dumper with flow-style scalars ───────────────────────────────────────

class _RichDictDumper(yaml.Dumper):
    """Dumps Rich Dict field props on one line for readability."""
    pass


def _represent_field_props(dumper, data):
    """Render a field properties dict in flow style (one line)."""
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items(), flow_style=True)


# ── Single file processing ────────────────────────────────────────────────────

def process_manifest(manifest_path: Path, write: bool, no_backup: bool) -> bool:
    """Process a single manifest file. Returns True if changes were made."""
    raw = manifest_path.read_text(encoding="utf-8")

    # Use safe_load (can't round-trip !include — report if present)
    has_includes = "!include" in raw
    if has_includes:
        print(f"  NOTE: {manifest_path.name} uses !include — fragment files must be "
              f"normalized separately.")
        # Still process what we can (the top-level parsed content)

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        print(f"  ERROR: Cannot parse YAML in {manifest_path}: {e}", file=sys.stderr)
        return False

    if data is None:
        print(f"  SKIP: {manifest_path.name} is empty.")
        return False

    normalized_data, changes, warnings = _walk_and_normalize(data)

    if warnings:
        print(f"\n  Warnings in {manifest_path.name}:")
        for w in warnings:
            print(w)

    if not changes:
        if not warnings:
            print(f"  OK: {manifest_path.name} — already compliant.")
        return False

    print(f"\n  Changes in {manifest_path.name} ({len(changes)} fix(es)):")
    for c in changes:
        print(c)

    if not write:
        return False

    if not no_backup:
        backup_path = manifest_path.with_suffix(".yaml.bak")
        shutil.copy2(manifest_path, backup_path)
        print(f"  Backup: {backup_path.name}")

    out_yaml = yaml.dump(normalized_data, default_flow_style=False,
                         sort_keys=False, allow_unicode=True)
    manifest_path.write_text(out_yaml, encoding="utf-8")
    print(f"  Written: {manifest_path}")
    return True


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", metavar="FILE",
                       help="Path to a single YAML manifest to inspect / normalize.")
    group.add_argument("--dir", metavar="DIR",
                       help="Directory to scan recursively for *.yaml files.")
    parser.add_argument("--write", action="store_true", default=False,
                        help="Write normalized manifests back to disk (default: dry-run).")
    parser.add_argument("--no-backup", action="store_true", default=False,
                        help="Skip creating .bak backup before writing.")
    args = parser.parse_args()

    if args.write:
        print("MODE: Write (changes will be applied)\n")
    else:
        print("MODE: Dry-run (no files will be modified — use --write to apply)\n")

    manifests = []
    if args.manifest:
        p = Path(args.manifest)
        if not p.exists():
            print(f"ERROR: File not found: {p}", file=sys.stderr)
            sys.exit(1)
        manifests = [p]
    else:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"ERROR: Not a directory: {d}", file=sys.stderr)
            sys.exit(1)
        manifests = sorted(d.rglob("*.yaml"))
        print(f"Found {len(manifests)} YAML file(s) under {d}\n")

    changed_count = 0
    for mp in manifests:
        changed = process_manifest(mp, args.write, args.no_backup)
        if changed:
            changed_count += 1

    print(f"\n{'='*60}")
    if args.write:
        print(f"Done. {changed_count}/{len(manifests)} file(s) normalized.")
    else:
        print(f"Dry-run complete. {changed_count} file(s) would be modified.")
        if changed_count > 0:
            print("Re-run with --write to apply changes.")


if __name__ == "__main__":
    main()
