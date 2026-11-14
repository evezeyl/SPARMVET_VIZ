"""A gallery example written as a standard recipe (format 1): build it, write it as text, generate its data contract.

A gallery example is a standard recipe with one schema, one group and one plot (spec section 9, D1). Two writers need
the same form: `GalleryManager.submit_example` (a new example) and `assets/scripts/convert_gallery_examples.py` (the
examples of the old compact form). Both call this module, so there is one form.

The data contract (`data_contract`) is generated from the example's own data file: the columns, the Polars type of
each, and the texts that often mean "missing" where they really occur. It is a proposal that a person reviews; the
notes it returns say what to look at.

Consumed by: gallery_manager.py, assets/scripts/convert_gallery_examples.py. No Shiny import.
If deleted: no gallery example can be written in the standard form.

# @deps
# provides: function:example_recipe, function:dump_example, function:data_contract, function:data_summary, function:plot_summary, constant:SCHEMA_ID, constant:GROUP_ID, constant:DATA_FILE
# consumes: libs/utils/src/utils/recipe_check.py (spec), libs/utils/src/utils/recipe_migration.py (SANITISER_TEXTS), libs/utils/src/utils/polars_types.py
# consumed_by: libs/viz_gallery/src/viz_gallery/gallery_manager.py, assets/scripts/convert_gallery_examples.py
# doc: .claude/design/recipe_format_spec.md (section 9; D1, D2, D7)
# @end_deps
"""
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import polars as pl
import yaml

from utils.polars_types import text_dtype_names
from utils.recipe_check import spec
from utils.recipe_migration import SANITISER_TEXTS
from viz_gallery.taxonomy import first_geom

SCHEMA_ID = "example"
GROUP_ID = "example"
DATA_FILE = "example_data.tsv"
_LINE_WIDTH = 110


def data_contract(data_file: Union[str, Path]) -> Tuple[Dict[str, dict], List[str]]:
    """The `input_fields` of an example generated from its data file, and the notes a person must review.

    The file is read as text. For every column: whitespace around a value is stripped (the schema says `strip: true`),
    the texts that often mean "missing" (the list of the old sanitiser) are looked for, and the type is the one Polars
    infers from the remaining values. A text that occurs is declared as `null_values` of that field only, never for the
    whole table, and is named in the notes: only the owner of the data knows whether `NA` is missing or a value.
    """
    text = pl.read_csv(data_file, separator="\t", infer_schema=False)
    stripped = text.select(pl.all().str.strip_chars())
    words = [word for word in SANITISER_TEXTS if word]
    notes: List[str] = []
    found: Dict[str, List[str]] = {}
    for column in text.columns:
        if bool((stripped[column] != text[column]).any()):
            notes.append(f"{column}: some values have whitespace around them; strip: true removes it")
        found[column] = [word for word in words if bool((stripped[column] == word).any())]
    cleaned = stripped.with_columns([
        pl.when(pl.col(column).is_in(texts)).then(None).otherwise(pl.col(column)).alias(column)
        for column, texts in found.items() if texts])
    inferred = pl.read_csv(io.BytesIO(cleaned.write_csv(separator="\t").encode("utf-8")),
                           separator="\t", infer_schema_length=None)
    fields: Dict[str, dict] = {}
    for column, dtype in inferred.schema.items():
        name = str(dtype)
        if name not in text_dtype_names():
            notes.append(f"{column}: Polars infers {name}, which a recipe cannot declare; String is written")
            name = "String"
        fields[column] = {"type": name}
        if found[column]:
            fields[column]["null_values"] = found[column]
            notes.append(f"{column}: the text(s) {found[column]} are declared as missing values of this field; "
                         "remove a text that is a real value here")
        if inferred[column].null_count() == inferred.height and inferred.height:
            notes.append(f"{column}: every value is missing")
        elif name not in ("String", "Int64", "Float64"):
            notes.append(f"{column}: type {name}; check that it is what the plot needs")
    return fields, notes


def data_summary(data_file: Union[str, Path]) -> str:
    """One sentence of facts about the data file (counted, not remembered): rows, columns and their names."""
    text = pl.read_csv(data_file, separator="\t", infer_schema=False)
    return f"The data of this example: {text.height} rows and {text.width} columns ({', '.join(text.columns)})."


def plot_summary(plot_spec: dict) -> str:
    """One sentence of facts about a plot specification: its first geom and its mapping."""
    mapping = plot_spec.get("mapping") or {}
    pairs = ", ".join(f"{aesthetic} is {column}" for aesthetic, column in mapping.items())
    geom = first_geom(plot_spec) or "no geom"
    return f"Drawn with {geom}; {pairs}." if pairs else f"Drawn with {geom}."


def example_recipe(*, example_id: str, label: str, data_path: str, fields: Dict[str, dict], taxonomy: Dict[str, str],
                   plot_id: str, plot_spec: dict, description: str = "", data_description: str = "",
                   plot_description: str = "", submission_date: Optional[str] = None,
                   tier1: Optional[list] = None, tier2: Optional[list] = None, tier3: Optional[list] = None) -> dict:
    """The standard recipe of one gallery example (spec section 9): one schema, one group, one plot.

    `taxonomy` holds the five typed axes; `geom` is not written (it is read from the layers). The steps of the example
    go where the format puts them: `tier1` and `tier2` in the schema, `tier3` on the plot entry.
    """
    typed = spec()["gallery"]["axes"]
    info: Dict[str, Any] = {"label": label}
    if description:
        info["description"] = description
    if submission_date:
        info["submission_date"] = str(submission_date)
    wrangling: Dict[str, Any] = {"tier1": list(tier1 or [])}
    if tier2:
        wrangling["tier2"] = list(tier2)
    schema: Dict[str, Any] = {"label": "Example data"}
    if data_description:
        schema["description"] = data_description
    schema.update({
        "source": {"type": "local_tsv", "path": data_path},
        "null_values": [],
        "strip": True,
        "input_fields": {column: dict(definition) for column, definition in fields.items()},
        "wrangling": wrangling,
    })
    plot: Dict[str, Any] = {"label": label}
    if plot_description:
        plot["description"] = plot_description
    plot["taxonomy"] = {axis: taxonomy[axis] for axis in typed if axis in taxonomy}
    ordered_spec = {"target_dataset": SCHEMA_ID}
    for key in ("mapping", "layers"):
        if key in plot_spec:
            ordered_spec[key] = plot_spec[key]
    ordered_spec.update({key: value for key, value in plot_spec.items() if key not in ordered_spec})
    plot["spec"] = ordered_spec
    if tier3:
        plot["steps"] = {"tier3": list(tier3)}
    return {
        "id": example_id,
        "spec_version": spec()["format_version"],
        "data_engine": spec()["engines"]["data_engine"][0],
        "plot_engine": spec()["engines"]["plot_engine"][0],
        "info": info,
        "data_schemas": {SCHEMA_ID: schema},
        "analysis_groups": {GROUP_ID: {"label": "Example", "description": "The one plot of this example.",
                                       "plots": {plot_id: plot}}},
    }


class _OneLine(dict):
    """A mapping written on one line (`{a: 1, b: 2}`)."""


class _Folded(str):
    """A text written as a folded block (`>-`), the form the specification asks for a description (section 13)."""


class _Dumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


_Dumper.add_representer(_OneLine, lambda dumper, data: dumper.represent_mapping("tag:yaml.org,2002:map", data, flow_style=True))
_Dumper.add_representer(_Folded, lambda dumper, data: dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">"))


def _short(value: Any) -> bool:
    return len(yaml.dump(value, Dumper=_Dumper, default_flow_style=True, width=10 ** 6, allow_unicode=True)) <= 72


def _layout(recipe: dict) -> dict:
    """The same recipe with the small mappings marked for one line and the descriptions marked as folded blocks."""
    out = {key: value for key, value in recipe.items()}
    out["info"] = {key: _Folded(value) if key == "description" else value for key, value in recipe["info"].items()}
    schemas = {}
    for sid, schema in recipe["data_schemas"].items():
        laid = dict(schema)
        if "description" in laid:
            laid["description"] = _Folded(laid["description"])
        laid["source"] = _OneLine(laid["source"])
        laid["input_fields"] = {column: _OneLine(definition) for column, definition in laid["input_fields"].items()}
        if all(not steps for steps in laid["wrangling"].values()):
            laid["wrangling"] = _OneLine(laid["wrangling"])
        schemas[sid] = laid
    out["data_schemas"] = schemas
    groups = {}
    for gid, group in recipe["analysis_groups"].items():
        plots = {}
        for pid, plot in group["plots"].items():
            laid = dict(plot)
            if "description" in laid:
                laid["description"] = _Folded(laid["description"])
            laid["taxonomy"] = _OneLine(laid["taxonomy"])
            plot_spec = dict(laid["spec"])
            if isinstance(plot_spec.get("mapping"), dict):
                plot_spec["mapping"] = _OneLine(plot_spec["mapping"])
            if isinstance(plot_spec.get("layers"), list):
                layers = []
                for layer in plot_spec["layers"]:
                    if not isinstance(layer, dict):
                        layers.append(layer)
                        continue
                    ordered = {key: layer[key] for key in ("name", "params") if key in layer}
                    ordered.update({key: value for key, value in layer.items() if key not in ordered})
                    if isinstance(ordered.get("params"), dict) and _short(ordered["params"]):
                        ordered["params"] = _OneLine(ordered["params"])
                    layers.append(_OneLine(ordered) if _short(ordered) else ordered)
                plot_spec["layers"] = layers
            laid["spec"] = plot_spec
            plots[pid] = laid
        groups[gid] = {**group, "plots": plots}
    out["analysis_groups"] = groups
    return out


def dump_example(recipe: dict) -> str:
    """The text of an example recipe: the key order of the recipe is kept, nothing is sorted.

    The text is read back and compared with the recipe before it is returned, so the layout can never change a value.
    """
    text = yaml.dump(_layout(recipe), Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=_LINE_WIDTH,
                     default_flow_style=False)
    if yaml.safe_load(text) != recipe:
        raise ValueError("the written text does not read back as the recipe; nothing is written")
    return text
