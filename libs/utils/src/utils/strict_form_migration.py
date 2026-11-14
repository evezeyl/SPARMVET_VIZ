"""Migration run D: the recipes take the strict form that `check_recipe` asks for (spec sections 5, 7 and 12).

What it writes, and why the screen does not change:
  - a `label` on every schema, join, group and plot that has none. The app made one up (a group showed its description or
    its id, a plot its id in title case); the same text is now written in the recipe, so it is a choice of the author
    and not a hidden rule. A schema or a join had no display text: it gets its id with spaces;
  - the old `info` block of a schema or join becomes `description` (what the table is) and `comment` (why); the `info`
    text of a plot becomes its `description`, joined with the `description` that sat inside the plot spec;
  - the taxonomy keys that sat inside a plot spec (`family`, `pattern`, `difficulty`, `show`, `sample_size`) move to
    `taxonomy` on the plot entry; `geom` is removed (it is derived from the first geom layer);
  - a fragment that starts with the key it is included under (`wrangling:`, `steps:`, `spec:`) loses that wrapper line;
  - what nothing reads is removed and reported: `role` of a field, `output_fields` of a join, the removed keys of
    `plot_defaults`; `wrangling: []` and a missing `wrangling` become `wrangling: {tier1: []}`.

It edits the text, so the comments stay (except inside a block that is replaced as a whole). A second run finds nothing.
Used by `assets/scripts/migrate_recipe_format.py --run D`.

Consumed by: assets/scripts/migrate_recipe_format.py. If deleted: recipes of the earlier runs do not pass the checker.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from utils.recipe_check import spec
from utils.recipe_migration import MigrationReport, _content_end

# @deps
# provides: function:migrate_strict_form
# consumes: libs/utils/src/utils/recipe_migration.py (MigrationReport, _content_end), libs/utils/src/utils/recipe_check.py (spec)
# consumed_by: assets/scripts/migrate_recipe_format.py, libs/utils/tests/test_strict_form_migration.py
# doc: .claude/design/recipe_format_spec.md (sections 5, 7, 12)
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
    start = _line_start(text, key_node.start_mark.index)
    nl = text.find("\n", _content_end(value_node))
    return start, (len(text) if nl == -1 else nl + 1)


def _apply(text: str, edits: List[Edit]) -> str:
    # at the same position a replacement goes first, then an insertion, so that an inserted line lands above it
    for start, end, new in sorted(edits, key=lambda e: (-e[0], -e[1])):
        text = text[:start] + new + text[end:]
    return text


def _q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _is_include(node) -> bool:
    return isinstance(node, yaml.ScalarNode) and node.tag == "!include"


def _scalar(node) -> Optional[str]:
    return node.value if isinstance(node, yaml.ScalarNode) else None


def unwrap_text(text: str, key: str) -> str:
    """The text of a fragment without its wrapper line `key:` (the content moves left); unchanged when there is none."""
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if not isinstance(root, yaml.MappingNode) or len(root.value) != 1 or root.value[0][0].value != key:
        return text
    key_node, value = root.value[0]
    if isinstance(value, yaml.ScalarNode) or getattr(value, "flow_style", False):
        return text
    key_line = _line_start(text, key_node.start_mark.index)
    after_key_line = text.find("\n", key_node.end_mark.index) + 1
    first = value.value[0][0] if isinstance(value, yaml.MappingNode) else value
    indent = first.start_mark.column
    if isinstance(value, yaml.SequenceNode):
        dash = text.rfind("-", 0, value.value[0].start_mark.index)
        indent = dash - _line_start(text, dash)
    lines = []
    for line in text[after_key_line:].split("\n"):
        lines.append(line[indent:] if line[:indent].strip() == "" else line)
    return text[:key_line] + "\n".join(lines)


class _Run:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.base = path.parent
        self.report: List[str] = []
        self.texts: Dict[Path, str] = {}
        self.originals: Dict[Path, str] = {}
        self.edits: List[Edit] = []

    # -- fragments: each change is applied to the text at once, so the next one reads the new text
    def fragment(self, node) -> Optional[Path]:
        target = self.base / node.value
        if not target.is_file():
            self.report.append(f"{self.path.name}: the include {node.value} was not found; a person must check it")
            return None
        if target not in self.texts:
            self.originals[target] = self.texts[target] = target.read_text(encoding="utf-8")
        return target

    def unwrap(self, node, key: str) -> Optional[Path]:
        target = self.fragment(node)
        if target is None:
            return None
        new = unwrap_text(self.texts[target], key)
        if new != self.texts[target]:
            self.texts[target] = new
            self.report.append(f"{target.name}: the wrapper line '{key}:' removed")
        return target

    def edit_fragment(self, target: Path, edits: List[Edit]) -> None:
        self.texts[target] = _apply(self.texts[target], edits)

    # -- the pieces
    def label(self, text: str, mapping, shown: str, where: str) -> None:
        if not isinstance(mapping, yaml.MappingNode) or mapping.flow_style or _find(mapping, "label") or not mapping.value:
            if isinstance(mapping, yaml.MappingNode) and mapping.flow_style and not _find(mapping, "label"):
                self.report.append(f"{where}: written in one line, add label: {_q(shown)} by hand")
            return
        first = mapping.value[0][0]
        at = _line_start(text, first.start_mark.index)
        self.edits.append((at, at, f"{' ' * first.start_mark.column}label: {_q(shown)}\n"))
        self.report.append(f"{where}: label {_q(shown)}")

    def info_block(self, text: str, mapping, where: str) -> None:
        """`info` of a schema or join: a mapping (category, sub_category, comments) or a text."""
        pair = _find(mapping, "info")
        if pair is None:
            return
        indent = " " * pair[0].start_mark.column
        description, comment = _scalar(pair[1]), None
        if isinstance(pair[1], yaml.MappingNode):
            values = {k.value: _scalar(v) for k, v in pair[1].value}
            category, sub = values.get("category"), values.get("sub_category")
            description = values.get("description") or (f"{sub} ({category})" if sub and category else sub or category)
            comment = values.get("comments") or values.get("comment")
        lines = ""
        if description and not _find(mapping, "description"):
            lines += f"{indent}description: {_q(description)}\n"
        if comment and not _find(mapping, "comment"):
            lines += f"{indent}comment: {_q(comment)}\n"
        start, end = _pair_span(text, *pair)
        self.edits.append((start, end, lines))
        self.report.append(f"{where}: info -> description{' and comment' if comment else ''}")

    def remove_pair(self, text: str, mapping, key: str, where: str, why: str) -> None:
        pair = _find(mapping, key)
        if pair is not None:
            self.edits.append((*_pair_span(text, *pair), ""))
            self.report.append(f"{where}: {key} removed ({why})")

    def fields(self, text: str, schema, where: str) -> None:
        pair = _find(schema, "input_fields")
        if pair is None:
            return
        target, fields_text, fields = None, text, pair[1]
        if _is_include(pair[1]):
            target = self.unwrap(pair[1], "input_fields")
            if target is None:
                return
            fields_text = self.texts[target]
            fields = yaml.compose(fields_text, Loader=yaml.SafeLoader)
        edits: List[Edit] = []
        for slug, definition in _pairs(fields):
            role = _find(definition, "role") if isinstance(definition, yaml.MappingNode) and not definition.flow_style else None
            if role is not None:
                edits.append((*_pair_span(fields_text, *role), ""))
                self.report.append(f"{where}.input_fields.{slug.value}: role removed (nothing reads it; the key of a table is is_entity_key)")
        if target is None:
            self.edits += edits
        elif edits:
            self.edit_fragment(target, edits)

    def wrangling(self, text: str, schema, where: str) -> None:
        pair = _find(schema, "wrangling")
        if pair is None:
            last = schema.value[-1]
            _, end = _pair_span(text, *last)
            tail = "" if text[:end].endswith("\n") else "\n"
            self.edits.append((end, end, f"{tail}{' ' * last[0].start_mark.column}wrangling: {{tier1: []}}\n"))
            self.report.append(f"{where}: wrangling: {{tier1: []}} added (the schema had none)")
        elif _is_include(pair[1]):
            self.unwrap(pair[1], "wrangling")
        elif isinstance(pair[1], yaml.SequenceNode) and not pair[1].value:
            self.edits.append((pair[1].start_mark.index, pair[1].end_mark.index, "{tier1: []}"))
            self.report.append(f"{where}: wrangling [] -> {{tier1: []}}")

    def schema(self, text: str, schema_id: str, schema, where: str) -> None:
        if not isinstance(schema, yaml.MappingNode) or schema.flow_style:
            return
        self.label(text, schema, schema_id.replace("_", " "), where)
        self.info_block(text, schema, where)
        self.fields(text, schema, where)
        self.wrangling(text, schema, where)

    def join(self, text: str, join_id: str, join, where: str) -> None:
        if not isinstance(join, yaml.MappingNode) or join.flow_style:
            return
        self.label(text, join, join_id.replace("_", " "), where)
        self.info_block(text, join, where)
        self.remove_pair(text, join, "output_fields", where, "the engine never applied it; the published columns are the last polars_select of tier1")
        steps = _find(join, "steps")
        if steps is not None and _is_include(steps[1]):
            self.unwrap(steps[1], "steps")

    def plot(self, text: str, plot_id: str, plot, where: str) -> None:
        if not isinstance(plot, yaml.MappingNode) or plot.flow_style:
            return
        self.label(text, plot, plot_id.replace("_", " ").title(), where)
        spec_pair = _find(plot, "spec")
        moved: Dict[str, str] = {}
        if spec_pair is not None:
            target, spec_text, spec_node = None, text, spec_pair[1]
            if _is_include(spec_pair[1]):
                target = self.unwrap(spec_pair[1], "spec")
                if target is not None:
                    spec_text = self.texts[target]
                    spec_node = yaml.compose(spec_text, Loader=yaml.SafeLoader)
            if target is not None or isinstance(spec_node, yaml.MappingNode):
                edits: List[Edit] = []
                stray = set(spec()["gallery"]["axes"]) | {"description", "info", "geom"}
                for key_node, value in _pairs(spec_node) if isinstance(spec_node, yaml.MappingNode) and not spec_node.flow_style else []:
                    if key_node.value in stray and isinstance(value, yaml.ScalarNode):
                        moved[key_node.value] = value.value
                        edits.append((*_pair_span(spec_text, key_node, value), ""))
                if target is None:
                    self.edits += edits
                elif edits:
                    self.edit_fragment(target, edits)
        indent = " " * plot.value[0][0].start_mark.column
        info, own = _find(plot, "info"), _find(plot, "description")
        parts = [t for t in (_scalar(own[1]) if own else None, _scalar(info[1]) if info else None,
                             moved.get("description"), moved.get("info")) if t]
        description = " ".join(dict.fromkeys(parts))
        anchor = spec_pair[0] if spec_pair is not None else plot.value[-1][0]
        at = _line_start(text, anchor.start_mark.index)
        if info is not None or (own is not None and description != _scalar(own[1])):
            for pair in (info, own):
                if pair is not None:
                    self.edits.append((*_pair_span(text, *pair), ""))
            self.edits.append((at, at, f"{indent}description: {_q(description)}\n"))
            self.report.append(f"{where}: description written from the old info and the spec")
        elif own is None and description:
            self.edits.append((at, at, f"{indent}description: {_q(description)}\n"))
            self.report.append(f"{where}: description moved from the spec to the plot entry")
        axes = {axis: moved[axis] for axis in spec()["gallery"]["axes"] if axis in moved}
        if axes and not _find(plot, "taxonomy"):
            self.edits.append((at, at, f"{indent}taxonomy: {json.dumps(axes, ensure_ascii=False)}\n"))
            self.report.append(f"{where}: taxonomy {axes} moved from the spec to the plot entry")
        if "geom" in moved:
            self.report.append(f"{where}: geom {moved['geom']!r} removed from the spec (it is derived from the first geom layer)")

    def run(self, apply: bool) -> MigrationReport:
        result = MigrationReport()
        try:
            text = self.path.read_text(encoding="utf-8")
            root = yaml.compose(text, Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            result.lines.append(f"{self.path.name}: the file cannot be parsed and was not migrated ({str(exc).splitlines()[0][:80]}); a person must check it")
            return result
        if not isinstance(root, yaml.MappingNode):
            return result
        name = self.path.name
        for section in _SCHEMA_SECTIONS:
            pair = _find(root, section)
            for key_node, schema in _pairs(pair[1]) if pair else []:
                self.schema(text, key_node.value, schema, f"{name}:{section}.{key_node.value}")
        meta = _find(root, "metadata_schema")
        if meta is not None:
            self.schema(text, "metadata", meta[1], f"{name}:metadata_schema")
        joins = _find(root, "joins")
        for key_node, join in _pairs(joins[1]) if joins else []:
            self.join(text, key_node.value, join, f"{name}:joins.{key_node.value}")
        groups = _find(root, "analysis_groups")
        for group_key, group in _pairs(groups[1]) if groups else []:
            if not isinstance(group, yaml.MappingNode) or group.flow_style:
                continue
            where = f"{name}:analysis_groups.{group_key.value}"
            description = _find(group, "description")
            shown = (_scalar(description[1]) if description else None) or group_key.value
            self.label(text, group, shown, where)
            plots = _find(group, "plots")
            for plot_key, plot in _pairs(plots[1]) if plots else []:
                self.plot(text, plot_key.value, plot, f"{where}.plots.{plot_key.value}")
        defaults = _find(root, "plot_defaults")
        if defaults is not None and isinstance(defaults[1], yaml.MappingNode) and not defaults[1].flow_style:
            for key, fix in spec()["renamed"]["plot_defaults"].items():
                if fix == "removed":
                    self.remove_pair(text, defaults[1], key, f"{name}:plot_defaults", "the key was removed from the format; nothing reads it")
        new = _apply(text, self.edits)
        if new != text:
            result.changed_files.append(self.path)
            if apply:
                self.path.write_text(new, encoding="utf-8")
        for target, current in self.texts.items():
            if current != self.originals[target]:
                result.changed_files.append(target)
                if apply:
                    target.write_text(current, encoding="utf-8")
        result.lines = self.report
        return result


def migrate_strict_form(path, *, apply: bool = False) -> MigrationReport:
    """Run D on one recipe file and the fragments it includes; writes only when `apply` is true."""
    return _Run(Path(path)).run(apply)
