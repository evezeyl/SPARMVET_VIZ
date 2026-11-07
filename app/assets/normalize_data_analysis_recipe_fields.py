#!/usr/bin/env python
"""
normalize_data_analysis_recipe_fields.py (app/assets/)
------------------------------------------
Utility to enforce the SPARMVET Unified Data Analysis Recipe Standard (ADR-041).
Ensures all field schemas and wrangling blocks are correctly structured.

Standard Format (ADR-041):
1. Fields (input_fields/output_fields): Rich Dictionary { slug: { props } }
2. Wrangling: Tiered Sequential Lists { tier1: [actions], tier2: [actions] }
3. Fragments: Flat (no redundant top-level anchoring keys)

Importable API (used by Blueprint Architect UI):
    from app.assets.normalize_data_analysis_recipe_fields import normalize_file
    changes, success, message = normalize_file(Path("path/to/file.yaml"), write=True)

Usage:
    ./.venv/bin/python app/assets/normalize_data_analysis_recipe_fields.py \\
        --data-analysis-recipe path/to/file.yaml [--write] [--no-backup]
"""
import argparse
import shutil
import sys
from pathlib import Path

import yaml


# ── Core Logic (importable) ───────────────────────────────────────────────────

def _normalize_fields(fields):
    """
    Ensures fields are in the Rich Dictionary format: { slug: { properties } }.
    Accepts:
      - list [{name, dtype, label}, ...] (Deprecated Standard)
      - dict {col: type}                (Simple Dict)
      - dict {col: {props}}             (Rich Dict - target)
    Returns (normalized_dict, was_changed: bool).
    """
    if not fields:
        return {}, False

    changed = False
    normalized = {}

    # Case 1: Deprecated List Format or simple String List
    if isinstance(fields, list):
        changed = True
        for item in fields:
            if isinstance(item, dict):
                slug = item.get("name", item.get("field", "unknown_col"))
                normalized[slug] = {
                    "original_name": item.get("original_name", slug),
                    "type": item.get("type", item.get("dtype", "categorical")),
                    "label": item.get("label", item.get("description", slug.replace("_", " ").capitalize()))
                }
            else:
                slug = str(item)
                normalized[slug] = {
                    "original_name": slug,
                    "type": "categorical",
                    "label": slug.replace("_", " ").capitalize()
                }
        return normalized, True

    # Case 2: Dictionary Format
    if isinstance(fields, dict):
        for k, v in fields.items():
            if isinstance(v, dict):
                # Ensure rich properties exist
                entry = {
                    "original_name": v.get("original_name", k),
                    "type": v.get("type", v.get("dtype", "categorical")),
                    "label": v.get("label", v.get("description", k.replace("_", " ").capitalize()))
                }
                # Check for other properties (is_primary_key, etc.)
                for prop_k, prop_v in v.items():
                    if prop_k not in ("dtype", "description") and prop_k not in entry:
                        entry[prop_k] = prop_v

                if entry != v or "dtype" in v or "description" in v:
                    changed = True
                normalized[k] = entry
            else:
                # Simple {col: type} -> Rich
                normalized[k] = {
                    "original_name": k,
                    "type": str(v),
                    "label": k.replace("_", " ").capitalize()
                }
                changed = True
        return normalized, changed

    return fields, False


def _normalize_wrangling(wrangling):
    """
    Ensures wrangling is in the Tiered Sequential List format (ADR-024).
    Returns (normalized_dict, was_changed: bool).
    """
    if not wrangling:
        return {"tier1": [], "tier2": []}, False

    changed = False

    # Case 1: Legacy Flat List
    if isinstance(wrangling, list):
        return {"tier1": wrangling, "tier2": []}, True

    # Case 2: Dictionary (Tiered)
    if isinstance(wrangling, dict):
        # Already has tiers?
        if "tier1" in wrangling or "tier2" in wrangling:
            normalized = {
                "tier1": wrangling.get("tier1", []),
                "tier2": wrangling.get("tier2", [])
            }
            if normalized != wrangling:
                changed = True
            return normalized, changed

        # Legacy flat dict format (unlikely but possible)
        return {"tier1": [wrangling], "tier2": []}, True

    return wrangling, False


def _walk_and_normalize(obj, path="root"):
    """
    Recursively normalizes fields and wrangling structures.
    """
    changes = []
    if not isinstance(obj, dict):
        return obj, []

    for key in list(obj.keys()):
        val = obj[key]
        if key in ("input_fields", "output_fields"):
            normalized, changed = _normalize_fields(val)
            if changed:
                changes.append(
                    f"  [{path}.{key}]: enforced Rich Dictionary format")
                obj[key] = normalized
        elif key in ("wrangling", "steps", "pre_plot_wrangling"):
            normalized, changed = _normalize_wrangling(val)
            if changed:
                changes.append(
                    f"  [{path}.{key}]: enforced Tiered Sequential List format")
                obj[key] = normalized
        elif isinstance(val, (dict, list)):
            sub_obj, sub_changes = _walk_and_normalize(
                val, path=f"{path}.{key}")
            obj[key] = sub_obj
            changes.extend(sub_changes)

    return obj, changes


def normalize_file(data_analysis_recipe_path: Path, write: bool = False,
                   backup: bool = True) -> tuple:
    """
    Main API for normalization. 
    Handles both full data analysis recipes and individual fragments.
    """
    if not data_analysis_recipe_path.exists():
        return [], False, f"File not found: {data_analysis_recipe_path}"

    try:
        raw = data_analysis_recipe_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw) or {}
    except Exception as e:
        return [], False, f"YAML parse error: {e}"

    changes = []

    # 1. Fragment Unwrapping (Hygiene Rule #3)
    # If the file is a fragment starting with a redundant key, unwrap it.
    fragment_keys = ("input_fields", "output_fields", "wrangling")
    if isinstance(data, dict) and len(data) == 1:
        top_key = list(data.keys())[0]
        if top_key in fragment_keys:
            data = data[top_key]
            changes.append(f"  [root]: unwrapped redundant '{top_key}' header")

    # 2. Schema/Logic Normalization
    # Special case: if we unwrapped a fragment, the "root" is now the fields/wrangling itself
    if isinstance(data, dict):
        # Are we looking at a fields fragment? (Check for properties common to field dicts)
        is_fields = any(isinstance(v, dict) and (
            "type" in v or "original_name" in v or "dtype" in v) for v in data.values())
        # Are we looking at a wrangling fragment? (Check for tier1 key)
        is_wrangling = "tier1" in data or "tier2" in data

        if is_fields:
            normalized, changed = _normalize_fields(data)
            if changed:
                changes.append(
                    "  [root]: normalized fields fragment to Rich Dictionary")
                data = normalized
        elif is_wrangling:
            normalized, changed = _normalize_wrangling(data)
            if changed:
                changes.append(
                    "  [root]: normalized wrangling fragment to Tiered Tiers")
                data = normalized
        else:
            # Full data analysis recipe walker
            data, walk_changes = _walk_and_normalize(data)
            changes.extend(walk_changes)
    else:
        # It's a list (likely a flat wrangling fragment)
        normalized, changed = _normalize_wrangling(data)
        if changed:
            changes.append(
                "  [root]: converted flat wrangling list to Tiered format")
            data = normalized

    if not changes:
        return [], True, "Already in standard format — no changes needed."

    if not write:
        return changes, True, f"Dry-run: {len(changes)} structural correction(s) identified."

    # Write with backup
    if backup:
        bak = data_analysis_recipe_path.with_suffix(".yaml.bak")
        shutil.copy2(data_analysis_recipe_path, bak)

    out_yaml = yaml.dump(data, default_flow_style=False,
                         sort_keys=False, allow_unicode=True)
    data_analysis_recipe_path.write_text(out_yaml, encoding="utf-8")

    msg = f"Normalized {len(changes)} structural item(s) in '{data_analysis_recipe_path.name}'."
    if backup:
        msg += " (.bak created)"
    return changes, True, msg


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-analysis-recipe", required=True, help="Path to YAML file.")
    parser.add_argument("--write", action="store_true",
                        help="Write changes to disk.")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip backup.")
    args = parser.parse_args()

    path = Path(args.data_analysis_recipe)
    changes, success, message = normalize_file(
        path, write=args.write, backup=not args.no_backup)

    if not success:
        print(f"ERROR: {message}", file=sys.stderr)
        sys.exit(1)

    if changes:
        print(f"🔍 Normalized {len(changes)} item(s):")
        for c in changes:
            print(c)
    print(f"\n{message}")


if __name__ == "__main__":
    main()
