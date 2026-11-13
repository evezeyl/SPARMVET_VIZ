"""Migration run A, text level: the changes that do not depend on the new action names (spec 4.1, decision DEC43).

What it does to a recipe in format 0 (the unversioned recipes before 2026-11-13):
- adds `spec_version`, `data_engine` and `plot_engine` after `id`;
- renames `info.display_name` to `label`, `is_primary_key` to `is_entity_key`, `source_name` to `original_name`;
- turns every field type into its Polars name (`categorical` was always a String);
- writes into every schema the settings the hidden sanitiser applied (`null_values` with its 14 texts and `strip: true`),
  so no table changes (spec 7.3);
- unwraps an `input_fields` fragment that repeats its own key (F01).
The action names and the parameters they now require are the next part of run A; run B (`final_contract`, `keep_columns`,
`drop_columns`) is separate.

It edits the TEXT at the positions the YAML parser reports, so every `#` comment and the layout stay. It never writes a
guess: a type it does not know is reported for a person. Safe to run twice: a key that is there is left alone.

# @deps
# provides: function:migrate_text, function:migrate_recipe_file, constant:SANITISER_TEXTS, class:MigrationReport
# consumes: libs/utils/src/utils/recipe_spec.yaml
# consumed_by: libs/utils/tests/test_recipe_migration.py, assets/scripts/migrate_recipe_format.py
# doc: .claude/design/recipe_format_spec.md (4.1, 7.3, 7.4, 12)
# @end_deps
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from utils.recipe_check import spec

# What ingestion/sanitizer.py turned into null in every text column, in its order (evidence section 20).
SANITISER_TEXTS = ("", "NA", "N/A", "None", "null", "NaN", "-", "na", "n/a", "none", "nan", "NULL", "n.a.", "N.A.")

_FIELD_KEY_RENAMES = {"is_primary_key": "is_entity_key", "source_name": "original_name"}
_SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")
_ENGINES = (("spec_version", "1"), ("data_engine", "python-polars"), ("plot_engine", "python-plotnine"))


@dataclass
class MigrationReport:
    changed_files: List[Path] = field(default_factory=list)
    lines: List[str] = field(default_factory=list)


@dataclass
class _Edit:
    start: int
    end: int
    text: str


def _scalar_text(node: yaml.Node) -> str:
    return node.value


def _quoted_like(original: str, new: str) -> str:
    return f"{original[0]}{new}{original[0]}" if original[:1] in ("'", '"') else new


def _span(text: str, node: yaml.Node) -> Tuple[int, int]:
    return node.start_mark.index, node.end_mark.index


def _line_end(text: str, index: int) -> int:
    end = text.find("\n", index)
    return len(text) if end == -1 else end


def _line_start(text: str, index: int) -> int:
    return text.rfind("\n", 0, index) + 1


def _mapping_pairs(node: yaml.Node) -> List[Tuple[yaml.Node, yaml.Node]]:
    return list(node.value) if isinstance(node, yaml.MappingNode) else []


def _find(node: yaml.Node, key: str) -> Optional[Tuple[yaml.Node, yaml.Node]]:
    for key_node, value_node in _mapping_pairs(node):
        if isinstance(key_node, yaml.ScalarNode) and key_node.value == key:
            return key_node, value_node
    return None


def _field_edits(text: str, fields: yaml.Node, report: List[str], where: str) -> List[_Edit]:
    edits: List[_Edit] = []
    types = spec()["renamed_types"]
    valid = {"String", "Int64", "Float64", "Boolean", "Date"}
    for slug_node, definition in _mapping_pairs(fields):
        if not isinstance(definition, yaml.MappingNode):
            continue
        for key_node, value_node in _mapping_pairs(definition):
            key = _scalar_text(key_node)
            if key in _FIELD_KEY_RENAMES:
                start, end = _span(text, key_node)
                edits.append(_Edit(start, end, _FIELD_KEY_RENAMES[key]))
                report.append(f"{where}.{_scalar_text(slug_node)}: {key} -> {_FIELD_KEY_RENAMES[key]}")
            elif key == "type" and isinstance(value_node, yaml.ScalarNode):
                old = value_node.value
                new = types.get(old) or types.get(str(old).lower())
                if old in valid or new is None and old not in types:
                    if old not in valid:
                        report.append(f"{where}.{_scalar_text(slug_node)}: the type {old!r} has no known replacement; a person must choose")
                    continue
                if old == new:
                    continue
                start, end = _span(text, value_node)
                new_name = new.split(" ")[0]
                edits.append(_Edit(start, end, _quoted_like(text[start:end], new_name)))
                report.append(f"{where}.{_scalar_text(slug_node)}: type {old} -> {new_name}")
    return edits


def _unwrap(text: str, report: List[str]) -> str:
    """Remove a line `input_fields:` that wraps the whole fragment and dedent what it held (F01)."""
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if not (isinstance(root, yaml.MappingNode) and len(root.value) == 1):
        return text
    key_node, value_node = root.value[0]
    if key_node.value != "input_fields" or not isinstance(value_node, yaml.MappingNode) or value_node.flow_style:
        return text
    first_child = value_node.value[0][0]
    indent = first_child.start_mark.column
    begin = _line_start(text, key_node.start_mark.index)
    body_start = _line_start(text, first_child.start_mark.index)
    kept = text[:begin]
    block = text[body_start:]
    lines = []
    for line in block.split("\n"):
        lines.append(line[indent:] if line[:indent].strip() == "" and len(line) >= indent and line.strip() else line)
    report.append("input_fields: removed the wrapper line and dedented the fragment (F01)")
    return kept + "\n".join(lines)


def _recipe_edits(text: str, root: yaml.Node, report: List[str]) -> List[_Edit]:
    edits: List[_Edit] = []
    present = {_scalar_text(k) for k, _ in _mapping_pairs(root)}
    id_pair = _find(root, "id")
    missing = [(k, v) for k, v in _ENGINES if k not in present]
    if id_pair and missing:
        at = _line_end(text, id_pair[1].end_mark.index)
        edits.append(_Edit(at, at, "".join(f"\n{k}: {v}" for k, v in missing)))
        report.extend(f"top level: added {k}: {v}" for k, v in missing)
    info = _find(root, "info")
    if info:
        name = _find(info[1], "display_name")
        if name:
            start, end = _span(text, name[0])
            edits.append(_Edit(start, end, "label"))
            report.append("info: display_name -> label")
    for section in _SCHEMA_SECTIONS + ("metadata_schema",):
        pair = _find(root, section)
        if not pair:
            continue
        schemas = [(None, pair[1])] if section == "metadata_schema" else _mapping_pairs(pair[1])
        for schema_key, schema in schemas:
            sid = section if schema_key is None else f"{section}.{_scalar_text(schema_key)}"
            if not isinstance(schema, yaml.MappingNode) or schema.flow_style:
                continue
            fields_pair = _find(schema, "input_fields")
            old_fields = _find(schema, "fields")
            if old_fields and not fields_pair:
                start, end = _span(text, old_fields[0])
                edits.append(_Edit(start, end, "input_fields"))
                report.append(f"{sid}: fields -> input_fields")
                fields_pair = old_fields
            if fields_pair and isinstance(fields_pair[1], yaml.MappingNode):
                edits.extend(_field_edits(text, fields_pair[1], report, f"{sid}.input_fields"))
            if fields_pair and not _find(schema, "null_values") and not _find(schema, "strip"):
                key_node = fields_pair[0]
                indent = " " * key_node.start_mark.column
                values = json.dumps(list(SANITISER_TEXTS), ensure_ascii=False)
                at = _line_start(text, key_node.start_mark.index)
                edits.append(_Edit(at, at, f"{indent}null_values: {values}\n{indent}strip: true\n"))
                report.append(f"{sid}: wrote null_values (the 14 texts of the old sanitiser) and strip: true")
    return edits


def _apply(text: str, edits: List[_Edit]) -> str:
    for edit in sorted(edits, key=lambda e: (e.start, e.end), reverse=True):
        text = text[:edit.start] + edit.text + text[edit.end:]
    return text


def migrate_text(text: str, role: str = "recipe") -> Tuple[str, List[str]]:
    """Migrate the text of a recipe (`role='recipe'`) or of an `input_fields` fragment (`role='input_fields'`)."""
    report: List[str] = []
    if role == "input_fields":
        text = _unwrap(text, report)
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if not isinstance(root, yaml.MappingNode):
        return text, report
    if role == "recipe":
        edits = _recipe_edits(text, root, report)
    elif role == "input_fields":
        edits = _field_edits(text, root, report, "input_fields")
    else:
        raise ValueError(f"unknown role {role!r}")
    return _apply(text, edits), report


def _included_fragments(text: str) -> Dict[str, str]:
    """`!include` targets of a recipe file with the role of the key they are included under (only input_fields so far)."""
    roles: Dict[str, str] = {}

    def walk(node: yaml.Node, parent_key: Optional[str]) -> None:
        if isinstance(node, yaml.ScalarNode) and node.tag == "!include" and parent_key == "input_fields":
            roles[node.value] = "input_fields"
        elif isinstance(node, yaml.MappingNode):
            for key_node, value_node in node.value:
                walk(value_node, key_node.value if isinstance(key_node, yaml.ScalarNode) else None)
        elif isinstance(node, yaml.SequenceNode):
            for item in node.value:
                walk(item, None)

    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if root is not None:
        walk(root, None)
    return roles


def migrate_recipe_file(path, *, apply: bool = False) -> MigrationReport:
    """Migrate a recipe file and the `input_fields` fragments it includes; writes only when `apply` is true."""
    path = Path(path)
    report = MigrationReport()
    text = path.read_text(encoding="utf-8")
    new, lines = migrate_text(text, role="recipe")
    if new != text:
        report.changed_files.append(path)
        report.lines += [f"{path.name}: {line}" for line in lines]
        if apply:
            path.write_text(new, encoding="utf-8")
    for target, role in _included_fragments(text).items():
        fragment = path.parent / target
        if not fragment.is_file():
            report.lines.append(f"{path.name}: the include {target} was not found; a person must check it")
            continue
        old = fragment.read_text(encoding="utf-8")
        migrated, lines = migrate_text(old, role=role)
        if migrated != old:
            report.changed_files.append(fragment)
            report.lines += [f"{target}: {line}" for line in lines]
            if apply:
                fragment.write_text(migrated, encoding="utf-8")
    return report
