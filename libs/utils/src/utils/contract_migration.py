"""Migration run C: `final_contract` and the schema `output_fields` are removed (DEC23, DEC43).

The published columns of a join become the last step of its `steps.tier1`, a plain `polars_select` with the columns of the
old contract in their order; the display texts of the contract (`label`) become the join's `labels`. The old engine applied
`final_contract` only when it was a dictionary, so a contract in list form (or in any other form) never acted: it is removed
without a select, so that every result stays identical, and the report says so. A schema's `output_fields` was never applied
by the engine: it is removed and the report names it.

It edits the text, so every comment stays; a fragment that only the removed key included is deleted. A second run finds
nothing to do. Used by `assets/scripts/migrate_recipe_format.py --run C`.

Consumed by: assets/scripts/migrate_recipe_format.py. If deleted: the recipes keep the removed keys and the checker refuses them.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from utils.action_names import SELECT
from utils.recipe_migration import MigrationReport, _content_end

# @deps
# provides: function:migrate_contracts
# consumes: libs/utils/src/utils/recipe_migration.py (MigrationReport)
# consumed_by: assets/scripts/migrate_recipe_format.py, libs/utils/tests/test_contract_migration.py
# doc: .claude/design/recipe_format_spec.md#DEC23
# @end_deps

_SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")
Edit = Tuple[int, int, str]


def _pairs(node):
    return node.value if isinstance(node, yaml.MappingNode) else []


def _find(node, key):
    for k, v in _pairs(node):
        if isinstance(k, yaml.ScalarNode) and k.value == key:
            return k, v
    return None


def _line_start(text: str, index: int) -> int:
    return text.rfind("\n", 0, index) + 1


def _pair_span(text: str, key_node, value_node) -> Tuple[int, int]:
    """From the start of the key's line to the end of the value's last line (with its newline)."""
    start = _line_start(text, key_node.start_mark.index)
    end = _content_end(value_node)  # not the end mark: PyYAML puts it at the next token, past comments and blank lines
    nl = text.find("\n", end)
    return start, (len(text) if nl == -1 else nl + 1)


def _apply(text: str, edits: List[Edit]) -> str:
    for start, end, new in sorted(edits, key=lambda e: -e[0]):
        text = text[:start] + new + text[end:]
    return text


def _unwrap(node, key: str):
    """The value under a single wrapper key (`output_fields:` or `steps:` around the real content), else the node."""
    if isinstance(node, yaml.MappingNode) and len(node.value) == 1 and node.value[0][0].value == key:
        return node.value[0][1]
    return node


class _Files:
    """The texts being edited, by path, so that two joins that share a fragment edit it once."""

    def __init__(self) -> None:
        self.original: Dict[Path, str] = {}
        self.edits: Dict[Path, List[Edit]] = {}
        self.delete: List[Path] = []

    def text(self, path: Path) -> str:
        if path not in self.original:
            self.original[path] = path.read_text(encoding="utf-8")
        return self.original[path]

    def add(self, path: Path, edit: Edit) -> None:
        self.text(path)
        self.edits.setdefault(path, []).append(edit)


def _contract(value, base: Path, files: _Files, report: List[str], where: str):
    """(columns in order, {column: label}, the fragment included or None); columns is None for a form that never acted."""
    fragment: Optional[Path] = None
    node = value
    if isinstance(value, yaml.ScalarNode) and value.tag == "!include":
        fragment = base / value.value
        if not fragment.is_file():
            report.append(f"{where}: the include {value.value} was not found; a person must check it")
            return False, None, None, None
        node = yaml.compose(files.text(fragment), Loader=yaml.SafeLoader)
        node = _unwrap(_unwrap(node, "final_contract"), "output_fields")
    if not isinstance(node, yaml.MappingNode):
        return True, None, {}, fragment  # a list or another form: the old engine never applied it
    columns, labels = [], {}
    for key_node, definition in node.value:
        columns.append(key_node.value)
        label = _find(definition, "label") if isinstance(definition, yaml.MappingNode) else None
        if label and isinstance(label[1], yaml.ScalarNode) and label[1].value:
            labels[key_node.value] = label[1].value
    return True, columns, labels, fragment


def migrate_contracts(path, *, apply: bool = False) -> MigrationReport:
    """Run C on one recipe file and the fragments it includes; writes only when `apply` is true."""
    path = Path(path)
    report = MigrationReport()
    files = _Files()
    try:
        text = files.text(path)
        root = yaml.compose(text, Loader=yaml.SafeLoader)
    except yaml.YAMLError as exc:
        report.lines.append(f"{path.name}: the file cannot be parsed and was not migrated ({str(exc).splitlines()[0][:80]}); a person must check it")
        return report
    if not isinstance(root, yaml.MappingNode):
        return report
    base = path.parent
    removed_includes: List[Path] = []

    joins = _find(root, "joins")
    for key_node, join in _pairs(joins[1]) if joins else []:
        pair = _find(join, "final_contract") if isinstance(join, yaml.MappingNode) else None
        if pair is None:
            continue
        where = f"{path.name}:joins.{key_node.value}"
        ok, columns, labels, fragment = _contract(pair[1], base, files, report.lines, where)
        if not ok:
            continue
        steps = _find(join, "steps")
        if columns is None:
            report.lines.append(f"{where}: final_contract was a list: the old engine never applied it, so it is removed with no select (the result is identical); a person decides whether the columns should be selected")
        elif steps is None or not _add_select(files, base, path, steps[1], columns, report.lines, where):
            continue
        else:
            report.lines.append(f"{where}: final_contract -> {SELECT} {columns}")
        start, end = _pair_span(text, *pair)
        new = ""
        if labels:
            new = f"{' ' * pair[0].start_mark.column}labels: {json.dumps(labels, ensure_ascii=False)}\n"
            report.lines.append(f"{where}: labels {labels}")
        files.add(path, (start, end, new))
        if fragment is not None:
            removed_includes.append(fragment)

    for section in _SCHEMA_SECTIONS + ("metadata_schema",):
        pair = _find(root, section)
        if not pair:
            continue
        schemas = [(None, pair[1])] if section == "metadata_schema" else _pairs(pair[1])
        for schema_key, schema in schemas:
            out = _find(schema, "output_fields") if isinstance(schema, yaml.MappingNode) else None
            if out is None:
                continue
            sid = section if schema_key is None else f"{section}.{schema_key.value}"
            fragment = None
            if isinstance(out[1], yaml.ScalarNode) and out[1].tag == "!include":
                fragment = base / out[1].value
            start, end = _pair_span(text, *out)
            files.add(path, (start, end, ""))
            if fragment is not None:
                removed_includes.append(fragment)
            report.lines.append(f"{path.name}:{sid}: output_fields removed (the engine never applied it; its display texts are in the git history)")

    for fragment in removed_includes:
        if fragment.is_file() and fragment not in files.delete and not _still_included(fragment, path, files):
            files.delete.append(fragment)
            report.lines.append(f"{fragment.name}: deleted (nothing includes it any more)")

    for target, edits in files.edits.items():
        new = _apply(files.original[target], edits)
        if new != files.original[target]:
            report.changed_files.append(target)
            if apply:
                target.write_text(new, encoding="utf-8")
    if apply:
        for fragment in files.delete:
            fragment.unlink()
    report.changed_files += [f for f in files.delete]
    return report


def _still_included(fragment: Path, recipe: Path, files: _Files) -> bool:
    """True when a file other than the removed keys of this run still names the fragment in an `!include`."""
    name = fragment.relative_to(recipe.parent).as_posix() if fragment.is_relative_to(recipe.parent) else fragment.name
    for yaml_file in recipe.parent.rglob("*.yaml"):
        if yaml_file == fragment:
            continue
        text = files.original.get(yaml_file)
        if text is None:
            text = yaml_file.read_text(encoding="utf-8", errors="ignore")
        edits = files.edits.get(yaml_file, [])
        remaining = _apply(text, edits) if edits else text
        if f"!include {name}" in remaining or f"!include '{name}'" in remaining or f'!include "{name}"' in remaining:
            return True
    return False


def _add_select(files: _Files, base: Path, recipe: Path, steps_value, columns: List[str], report: List[str], where: str) -> bool:
    """Append `polars_select` to `steps.tier1` (in the recipe or in the fragment the steps are included from)."""
    target = recipe
    node = steps_value
    if isinstance(steps_value, yaml.ScalarNode) and steps_value.tag == "!include":
        target = base / steps_value.value
        if not target.is_file():
            report.append(f"{where}: the include {steps_value.value} was not found; a person must check it")
            return False
        node = _unwrap(yaml.compose(files.text(target), Loader=yaml.SafeLoader), "steps")
    tier1 = _find(node, "tier1")
    if tier1 is None:
        report.append(f"{where}: the steps have no tier1; add `- action: {SELECT}` with the columns {columns} by hand")
        return False
    key_node, seq = tier1
    text = files.text(target)
    exprs = json.dumps(columns, ensure_ascii=False)
    if isinstance(seq, yaml.SequenceNode) and seq.value and not seq.flow_style:
        last = seq.value[-1]
        dash = text.rfind("-", 0, seq.value[0].start_mark.index)
        indent = " " * (dash - _line_start(text, dash))
        end = _content_end(last)
        files.add(target, (end, end, f"\n{indent}- action: {SELECT}\n{indent}  exprs: {exprs}"))
        return True
    step = json.dumps({"action": SELECT, "exprs": columns}, ensure_ascii=False)
    if isinstance(seq, yaml.SequenceNode) and seq.flow_style:
        if seq.value:
            at = seq.end_mark.index - 1  # before the closing bracket
            files.add(target, (at, at, f", {step}"))
        else:
            files.add(target, (seq.start_mark.index, seq.end_mark.index, f"[{step}]"))
        return True
    report.append(f"{where}: tier1 is written in a form this tool does not edit; add `- action: {SELECT}` with the columns {columns} by hand")
    return False
