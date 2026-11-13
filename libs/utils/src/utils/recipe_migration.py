"""Migration run A, text level: the changes that do not depend on the new action names (spec 4.1, decision DEC43).

What it does to a recipe in format 0 (the unversioned recipes before 2026-11-13):
- adds `spec_version`, `data_engine` and `plot_engine` after `id`;
- renames `info.display_name` to `label`, `is_primary_key` to `is_entity_key`, `source_name` to `original_name`;
- turns every field type into its Polars name (`categorical` was always a String);
- writes into every schema the settings the hidden sanitiser applied (`null_values` with its 14 texts and `strip: true`),
  so no table changes (spec 7.3);
- unwraps an `input_fields` fragment that repeats its own key (F01).
- converts every step of every `tier1`, `tier2` and `tier3` list to the steps of format 1 (`utils.step_migration`: new
  action names, every silent default written into the step); a step that needs a decision stays as it is and is reported.
Run B (`final_contract`, `keep_columns`, `drop_columns`) is separate.

It edits the TEXT at the positions the YAML parser reports, so every `#` comment and the layout stay. It never writes a
guess: a type it does not know is reported for a person. Safe to run twice: a key that is there is left alone.

# @deps
# provides: function:migrate_text, function:migrate_steps_text, function:migrate_recipe_file, constant:SANITISER_TEXTS, class:MigrationReport
# consumes: libs/utils/src/utils/recipe_spec.yaml, libs/utils/src/utils/step_migration.py
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

from utils.polars_types import text_dtype_names
from utils.recipe_check import spec
from utils.step_migration import NotConvertible, convert_step

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
    valid = set(text_dtype_names())
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


# -- steps: old action names and parameters to the steps of format 1 ---------------------------------------------------

_STEP_LISTS = ("tier1", "tier2", "tier3")
_NEW_PREFIXES = ("polars_", "modif_", "step_")
# The old pipeline cast `categorical` fields to Categorical right after reading, before any step: a `strip_whitespace` without
# columns (every String column at that moment) never touched them. Only the String-typed fields are text at the first step.
_TEXT_TYPES = {"utf8", "string", "character", "String"}


class _Flow(yaml.SafeDumper):
    """A dumper that writes lists of plain values in flow style, like the recipes are written by hand."""


def _represent_list(dumper, data):
    flow = all(isinstance(i, (str, int, float, bool)) or i is None for i in data)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)


_Flow.add_representer(list, _represent_list)


def _comments_in(text: str) -> List[str]:
    """The `# ...` comments written on the lines of a step (after a value, or on a line of their own inside it)."""
    found = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            found.append(stripped)
        elif " #" in line and line.count('"') % 2 == 0 and line.count("'") % 2 == 0:
            found.append(line[line.index(" #") + 1:].strip())
    return found


def _dump_steps(steps: List[dict], dash_column: int, comments: Optional[List[str]] = None) -> str:
    """The text of new steps as sequence items whose dash stands at `dash_column` (the first dash is already in place).
    The comments that were written on the old step go on lines above the new steps, so no comment is lost."""
    pad = " " * dash_column
    items = []
    for step in steps:
        body = yaml.dump(step, Dumper=_Flow, sort_keys=False, default_flow_style=False, width=10_000, allow_unicode=True).rstrip("\n")
        lines = body.split("\n")
        items.append("- " + lines[0] + "".join("\n" + pad + "  " + line for line in lines[1:]))
    return "".join(f"{c}\n{pad}" for c in (comments or [])) + ("\n" + pad).join(items)


def _content_end(node: yaml.Node) -> int:
    """The index just after the last character of a node's content. PyYAML's end mark of a block collection lies at the
    next token, past newlines and comments, which an edit must not swallow."""
    if isinstance(node, yaml.ScalarNode) or getattr(node, "flow_style", False):
        return node.end_mark.index
    children = node.value if isinstance(node, yaml.SequenceNode) else [n for pair in node.value for n in pair]
    return _content_end(children[-1]) if children else node.end_mark.index


def _step_items(root: yaml.Node) -> List[yaml.MappingNode]:
    """The step mappings of every tier list found anywhere under `root` (inline recipe or fragment)."""
    found: List[yaml.MappingNode] = []

    def walk(node: yaml.Node) -> None:
        if isinstance(node, yaml.MappingNode):
            for key_node, value_node in node.value:
                if isinstance(key_node, yaml.ScalarNode) and key_node.value in _STEP_LISTS and isinstance(value_node, yaml.SequenceNode):
                    found.extend(i for i in value_node.value if isinstance(i, yaml.MappingNode) and not i.flow_style)
                else:
                    walk(value_node)
        elif isinstance(node, yaml.SequenceNode):
            for item in node.value:
                walk(item)

    walk(root)
    return found


def _schema_spans(root: yaml.Node, base: Path) -> List[Tuple[int, int, Optional[Tuple[List[str], List[str]]]]]:
    """(start, end, text fields) of every schema written inline in a recipe, to know which fields a step may mean."""
    spans = []
    for section in _SCHEMA_SECTIONS:
        pair = _find(root, section)
        if pair:
            for _key, schema in _mapping_pairs(pair[1]):
                if isinstance(schema, yaml.MappingNode):
                    spans.append((schema.start_mark.index, schema.end_mark.index, _schema_facts(schema, base)))
    return spans


def migrate_steps_text(text: str, *, facts: Optional[Tuple[List[str], List[str]]] = None, where: str = "", base: Optional[Path] = None,
                       run: str = "A") -> Tuple[str, List[str]]:
    """Convert the old steps of a recipe or of a step fragment; `strings` are the declared text fields of the schema
    (for a recipe file they are found per schema from `base`, the folder of the recipe)."""
    report: List[str] = []
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if root is None:
        return text, report
    spans = _schema_spans(root, base) if base is not None else []
    edits: List[_Edit] = []
    constructor = yaml.SafeLoader("")
    for item in _step_items(root):
        try:
            step = constructor.construct_object(item, deep=True)
        except yaml.YAMLError as exc:
            report.append(f"{where}line {item.start_mark.line + 1}: a step with a tag or an anchor was not converted ({str(exc)[:60]}); a person must convert it")
            continue
        name = step.get("action") if isinstance(step, dict) else None
        if not isinstance(name, str) or name.startswith(_NEW_PREFIXES):
            continue
        item_facts = next((s for a, b, s in spans if a <= item.start_mark.index <= b), facts) or ([], [])
        try:
            converted = convert_step(step, strings=item_facts[0], keys=item_facts[1], run=run)
        except NotConvertible as exc:
            report.append(f"{where}line {item.start_mark.line + 1}: {exc}")
            continue
        start = item.start_mark.index
        line_start = _line_start(text, start)
        dash = text.rfind("-", line_start, start)          # the "- " of the sequence item, on the same line
        end = _content_end(item)
        if not converted:
            edits.append(_Edit(dash, end, f"# {name}: removed by the migration, it had nothing to act on (no String field in the schema)"))
            report.append(f"{where}line {item.start_mark.line + 1}: {name} -> removed (it did nothing)")
            continue
        edits.append(_Edit(dash, end, _dump_steps(converted, dash - line_start, _comments_in(text[dash:end]))))
        report.append(f"{where}line {item.start_mark.line + 1}: {name} -> {', '.join(s['action'] for s in converted)}")
    return _apply(text, edits), report


def _schema_facts(schema: yaml.Node, base: Path) -> Optional[Tuple[List[str], List[str]]]:
    """(the declared fields that Polars reads as text, the entity keys) of a schema (inline `input_fields` or a fragment)."""
    pair = _find(schema, "input_fields") or _find(schema, "fields")
    if not pair:
        return None
    node = pair[1]
    if isinstance(node, yaml.ScalarNode) and node.tag == "!include":
        fragment = base / node.value
        if not fragment.is_file():
            return None
        node = yaml.compose(fragment.read_text(encoding="utf-8"), Loader=yaml.SafeLoader)
        if isinstance(node, yaml.MappingNode) and len(node.value) == 1 and node.value[0][0].value == "input_fields":
            node = node.value[0][1]
    if not isinstance(node, yaml.MappingNode):
        return None
    out, keys = [], []
    for slug, definition in _mapping_pairs(node):
        type_pair = _find(definition, "type") if isinstance(definition, yaml.MappingNode) else None
        declared = type_pair[1].value if type_pair and isinstance(type_pair[1], yaml.ScalarNode) else None
        if declared in _TEXT_TYPES:
            out.append(slug.value)
        for key_name in ("is_entity_key", "is_primary_key"):
            flag = _find(definition, key_name) if isinstance(definition, yaml.MappingNode) else None
            if flag and isinstance(flag[1], yaml.ScalarNode) and str(flag[1].value).lower() == "true":
                keys.append(slug.value)
                break
    return out, keys


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


def _included_fragments(text: str, base: Path) -> Dict[str, Tuple[str, Optional[Tuple[List[str], List[str]]]]]:
    """`!include` targets of a recipe file: (role, the text fields of the schema it belongs to).

    Roles: `input_fields` (a fragment of fields) and `steps` (a fragment of tier lists, under `wrangling`, `steps` or a tier).
    """
    roles: Dict[str, Tuple[str, Optional[Tuple[List[str], List[str]]]]] = {}

    def walk(node: yaml.Node, parent_key: Optional[str], strings) -> None:
        if isinstance(node, yaml.ScalarNode) and node.tag == "!include":
            if parent_key == "input_fields":
                roles[node.value] = ("input_fields", None)
            elif parent_key in ("wrangling", "steps") + _STEP_LISTS:
                roles[node.value] = ("steps", strings)
        elif isinstance(node, yaml.MappingNode):
            for key_node, value_node in node.value:
                key = key_node.value if isinstance(key_node, yaml.ScalarNode) else None
                inner = _schema_facts(value_node, base) if key is not None and isinstance(value_node, yaml.MappingNode) and _find(value_node, "input_fields") else strings
                walk(value_node, key, inner)
        elif isinstance(node, yaml.SequenceNode):
            for item in node.value:
                walk(item, None, strings)

    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if root is not None:
        walk(root, None, None)
    return roles


def migrate_recipe_file(path, *, apply: bool = False, run: str = "A") -> MigrationReport:
    """Migrate a recipe file and the fragments it includes (fields and steps); writes only when `apply` is true."""
    path = Path(path)
    report = MigrationReport()
    text = path.read_text(encoding="utf-8")
    try:
        new, lines = migrate_text(text, role="recipe")
        new, step_lines = migrate_steps_text(new, where="", base=path.parent, run=run)
    except yaml.YAMLError as exc:
        report.lines.append(f"{path.name}: the file cannot be parsed and was not migrated ({str(exc).splitlines()[0][:80]}); a person must check it")
        return report
    lines = lines + step_lines
    if new != text:
        report.changed_files.append(path)
        report.lines += [f"{path.name}: {line}" for line in lines]
        if apply:
            path.write_text(new, encoding="utf-8")
    elif lines:
        report.lines += [f"{path.name}: {line}" for line in lines]
    for target, (role, strings) in _included_fragments(text, path.parent).items():
        fragment = path.parent / target
        if not fragment.is_file():
            report.lines.append(f"{path.name}: the include {target} was not found; a person must check it")
            continue
        old = fragment.read_text(encoding="utf-8")
        if role == "input_fields":
            migrated, lines = migrate_text(old, role=role)
        else:
            migrated, lines = migrate_steps_text(old, facts=strings, run=run)
        if migrated != old:
            report.changed_files.append(fragment)
            report.lines += [f"{target}: {line}" for line in lines]
            if apply:
                fragment.write_text(migrated, encoding="utf-8")
        elif lines:
            report.lines += [f"{target}: {line}" for line in lines]
    return report
