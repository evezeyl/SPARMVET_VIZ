#!/usr/bin/env python3
"""Declare the missing-value texts where they really occur: per table, per field (format 1, Eve 2026-11-14).

The migration to format 1 wrote the 14 texts of the old hidden sanitiser (`NA`, `N/A`, `-`, `None`, ...) into the
`null_values` of every table. That keeps every result identical, but it is a blanket: a `-` in a column where it is a
value would become missing, and a reader cannot see which texts mean "missing" in which column. Eve: "the recipes
concerned must declare NA for the correct field for the correct table".

What this script does, for every data schema of the recipes given:
  1. reads the data file of the schema as text (after `strip`, if the schema strips) and finds, for every declared field,
     which of the schema's `null_values` texts really occur in its column;
  2. writes the field's own `null_values: [..]` (the override of one field, spec 7.4) with exactly those texts;
  3. sets the schema's `null_values` to `[]`.
The result is identical: a text that never occurs in a field cannot change it. It edits the text, so every comment stays.
A fragment of fields that several tables or recipes include gets the union of the texts of all of them (all the recipes
given in one run are surveyed before anything is written), so no table loses a text it had.

Without --apply nothing is written: the script lists what it would change. Safe to run twice (a schema whose
`null_values` is already `[]` is left as it is; a field that already has its own `null_values` is left as it is).

Examples:
  .venv/bin/python assets/scripts/declare_missing_values.py config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml
  .venv/bin/python assets/scripts/declare_missing_values.py --apply config/data_analysis_recipes/pipelines
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import polars as pl
import yaml

SECTIONS = ("data_schemas", "additional_datasets_schemas")
Edit = Tuple[int, int, str]


def _pairs(node):
    return node.value if isinstance(node, yaml.MappingNode) else []


def _find(node, key):
    for k, v in _pairs(node):
        if isinstance(k, yaml.ScalarNode) and k.value == key:
            return k, v
    return None


def _schemas(root):
    """(id, schema node) of every data schema of a recipe (a standalone recipe is its own schema)."""
    found = []
    for section in SECTIONS:
        pair = _find(root, section)
        if pair:
            found += [(k.value, v) for k, v in _pairs(pair[1]) if isinstance(v, yaml.MappingNode)]
    meta = _find(root, "metadata_schema")
    if meta and isinstance(meta[1], yaml.MappingNode) and _find(meta[1], "input_fields"):
        found.append(("metadata_schema", meta[1]))
    if _find(root, "input_fields") and _find(root, "source"):
        found.append(("(recipe)", root))
    return found


def _apply(text: str, edits: List[Edit]) -> str:
    for start, end, new in sorted(edits, key=lambda e: -e[0]):
        text = text[:start] + new + text[end:]
    return text


def survey(files: List[Path], root_dir: Path, report: List[str]):
    """Pass 1: the schema-level edits of every recipe and the texts each field needs, by (file holding the field, slug)."""
    main_edits: Dict[Path, List[Edit]] = {}
    needs: Dict[Tuple[Path, str], List[str]] = {}   # the text of a field that is declared inline has the recipe as its file
    for path in files:
        text = path.read_text(encoding="utf-8")
        root = yaml.compose(text, Loader=yaml.SafeLoader)
        for sid, schema in _schemas(root):
            where = f"{path.name}:{sid}"
            nv, src = _find(schema, "null_values"), _find(schema, "source")
            src_path = _find(src[1], "path") if src else None
            tokens = [n.value for n in nv[1].value] if nv and isinstance(nv[1], yaml.SequenceNode) else []
            if not tokens or not src_path:
                continue  # already declared per field, or the table has no file to read
            data = (root_dir / src_path[1].value).resolve()
            if not data.is_file():
                report.append(f"{where}: the data file {src_path[1].value} was not found; nothing changed for this table")
                continue
            strip = _find(schema, "strip")
            stripping = bool(strip and str(strip[1].value).lower() == "true")
            df = pl.read_csv(data, separator="\t", infer_schema=False)
            holder = path
            fields_pair = _find(schema, "input_fields")
            fields = fields_pair[1] if fields_pair else None
            if isinstance(fields, yaml.ScalarNode) and fields.tag == "!include":
                holder = path.parent / fields.value
                fields = yaml.compose(holder.read_text(encoding="utf-8"), Loader=yaml.SafeLoader)
            main_edits.setdefault(path, []).append((nv[1].start_mark.index, nv[1].end_mark.index, "[]"))
            for slug_node, definition in _pairs(fields):
                if not isinstance(definition, yaml.MappingNode) or definition.flow_style or _find(definition, "null_values"):
                    continue
                original = _find(definition, "original_name")
                column = original[1].value if original else slug_node.value
                if column not in df.columns:
                    continue
                series = df[column].str.strip_chars() if stripping else df[column]
                hits = [t for t in tokens if bool((series == t).any())]
                if hits:
                    key = (holder, slug_node.value)
                    merged = sorted(set(needs.get(key, [])) | set(hits), key=lambda t: (tokens + [t]).index(t))
                    needs[key] = merged
                    report.append(f"{where}.{slug_node.value}: null_values {hits}")
    return main_edits, needs


def field_edits(field_maps, slugs: Dict[str, List[str]], text: str) -> List[Edit]:
    """The lines to insert in one text: `null_values` after the `type` of each field named in `slugs`."""
    edits: List[Edit] = []
    for fields in field_maps:
        for slug_node, definition in _pairs(fields):
            if slug_node.value not in slugs or not isinstance(definition, yaml.MappingNode) or _find(definition, "null_values"):
                continue
            anchor = (_find(definition, "type") or (None, definition.value[-1][1]))[1]
            at = text.find("\n", anchor.end_mark.index)
            at = len(text) if at == -1 else at
            indent = " " * definition.value[0][0].start_mark.column
            edits.append((at, at, f"\n{indent}null_values: {json.dumps(slugs[slug_node.value], ensure_ascii=False)}"))
    return edits


def _walk_field_maps(root):
    """The `input_fields` mappings written inline in a recipe."""
    for _, schema in _schemas(root):
        pair = _find(schema, "input_fields")
        if pair and isinstance(pair[1], yaml.MappingNode):
            yield pair[1]


def declare(files: List[Path], root_dir: Path, apply: bool = False) -> List[str]:
    report: List[str] = []
    main_edits, needs = survey(files, root_dir, report)
    by_holder: Dict[Path, Dict[str, List[str]]] = {}
    for (holder, slug), texts in needs.items():
        by_holder.setdefault(holder, {})[slug] = texts
    changed = set(main_edits) | set(by_holder)
    for path in sorted(changed):
        original = path.read_text(encoding="utf-8")
        edits = list(main_edits.get(path, []))
        if path in by_holder:
            slugs = by_holder[path]
            root = yaml.compose(original, Loader=yaml.SafeLoader)
            # a recipe holds its fields inline; a fragment of fields is itself the mapping of fields
            edits += field_edits(list(_walk_field_maps(root)) if path in main_edits else [root], slugs, original)
        new = _apply(original, edits)
        if new != original:
            report.append(f"{path.name}: changed")
            if apply:
                path.write_text(new, encoding="utf-8")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="recipe files, or folders searched for *.yaml recipes")
    parser.add_argument("--apply", action="store_true", help="write the changes (default: only list them)")
    parser.add_argument("--root", default=".", help="folder the `source.path` of the schemas is relative to (default: here)")
    args = parser.parse_args(argv)
    files: List[Path] = []
    for p in map(Path, args.paths):
        files += sorted(p.glob("*.yaml")) if p.is_dir() else [p]
    for line in declare(files, Path(args.root), apply=args.apply):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
