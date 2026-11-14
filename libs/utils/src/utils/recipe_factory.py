"""A minimal valid recipe in format version 1, and the one way to write recipe text (work order W8).

Two uses:
- a test or a script needs a small recipe and should not type the boilerplate: `minimal_recipe` returns a plain
  dictionary that passes `check_recipe`; the caller changes what the case is about;
- a program writes a recipe or a fragment to disk: `write_recipe`, `write_fragment` and `recipe_text` keep the order
  of the keys (the order of `analysis_groups` and of `plots` is the order of the tabs, spec section 5), never write a
  YAML anchor, and write `!include` for an `Include`.

Nothing here reads a data file or a registry: the factory spells no action name. The format version and the engine
names are read from the specification data (`recipe_spec.yaml`), so they cannot go stale.

These writers are for NEW text. A tool that changes an existing recipe file edits its text, so that every comment of
the author is kept (spec 6.2); it does not load the file and write it again with this module.

# @deps
# provides: function:minimal_recipe, function:minimal_schema, function:minimal_join, function:minimal_plot, function:recipe_text, function:write_recipe, function:write_fragment, class:Include
# consumes: libs/utils/src/utils/recipe_check.py (spec), libs/utils/src/utils/recipe_spec.yaml
# consumed_by: libs/utils/tests/test_recipe_factory.py, app/tests/test_writers_emit_format_one.py, assets/scripts/create_data_analysis_recipe.py, assets/scripts/SF_create_data_analysis_recipe.py, app/handlers/blueprint_handlers.py (new recipe form)
# doc: .claude/design/recipe_format_spec.md (sections 1, 3, 4, 5, 7), .claude/design/recipe_format_work_order.md (W8)
# @end_deps
"""
import copy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import yaml

from utils.recipe_check import spec

DEFAULT_GROUP_ID = "main"
_DEFAULT_SCHEMA_ID = "table"
_DEFAULT_COLUMNS = {"sample_id": "String", "value": "Float64"}


class Include:
    """A value that is written as `!include <path>`; the path is relative to the folder of the recipe."""

    def __init__(self, path: str) -> None:
        self.path = str(path)

    def __repr__(self) -> str:
        return f"Include({self.path!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Include) and other.path == self.path

    def __hash__(self) -> int:
        return hash(("Include", self.path))


class _RecipeDumper(yaml.SafeDumper):
    """Plain YAML in the order given; the same object used twice is written twice (no `&id001` anchor)."""

    def ignore_aliases(self, data: Any) -> bool:
        return True


_RecipeDumper.add_representer(Include, lambda dumper, data: dumper.represent_scalar("!include", data.path, style=""))


# -- the dictionary

def minimal_schema(path: str, columns: Mapping[str, Union[str, Mapping[str, Any]]], *, label: Optional[str] = None,
                   entity_key: Optional[str] = None, null_values: Iterable[str] = (), strip: bool = False,
                   tier1: Iterable[dict] = (), tier2: Optional[Iterable[dict]] = None,
                   source_type: str = "local_tsv") -> dict:
    """One schema. `columns` maps a column to its Polars type name, or to its full field mapping.

    `label` is the file name without its ending unless given. `null_values` and `strip` are written as given: by
    default no text means "missing" and no whitespace is stripped (the file is read as it is).
    """
    fields: Dict[str, dict] = {}
    for column, definition in columns.items():
        fields[column] = copy.deepcopy(dict(definition)) if isinstance(definition, Mapping) else {"type": definition}
    if entity_key is not None:
        if entity_key not in fields:
            raise ValueError(f"entity_key {entity_key!r} is not one of the columns {list(fields)}")
        fields[entity_key]["is_entity_key"] = True
    wrangling: Dict[str, list] = {"tier1": copy.deepcopy(list(tier1))}
    if tier2 is not None:
        wrangling["tier2"] = copy.deepcopy(list(tier2))
    return {
        "label": label if label is not None else Path(path).stem,
        "source": {"type": source_type, "path": str(path)},
        "null_values": list(null_values),
        "strip": strip,
        "input_fields": fields,
        "wrangling": wrangling,
    }


def minimal_join(ingredients: Iterable[str], tier1: Iterable[dict], *, label: Optional[str] = None,
                 tier2: Optional[Iterable[dict]] = None, labels: Optional[Mapping[str, str]] = None) -> dict:
    """One join. `ingredients` are schema ids, the first is the base; `tier1` are its steps, in order.

    `label` is the ingredient ids joined by " + " unless given.
    """
    ids = list(ingredients)
    steps: Dict[str, list] = {"tier1": copy.deepcopy(list(tier1))}
    if tier2 is not None:
        steps["tier2"] = copy.deepcopy(list(tier2))
    join: Dict[str, Any] = {
        "label": label if label is not None else " + ".join(ids),
        "ingredients": [{"dataset_id": dataset_id} for dataset_id in ids],
        "steps": steps,
    }
    if labels is not None:
        join["labels"] = dict(labels)
    return join


def minimal_plot(target: str, mapping: Mapping[str, str], layers: Optional[Iterable[dict]] = None, *,
                 label: Optional[str] = None, tier3: Optional[Iterable[dict]] = None) -> dict:
    """One plot entry on the table `target`. Without `layers` it is a bar chart (`geom_bar`), which needs only `x`.

    `label` is "Plot of <target>" unless given. `tier3` writes `steps: {tier3: [...]}`; without it the key is absent.
    """
    plot: Dict[str, Any] = {
        "label": label if label is not None else f"Plot of {target}",
        "spec": {
            "target_dataset": target,
            "mapping": dict(mapping),
            "layers": copy.deepcopy(list(layers)) if layers is not None else [{"name": "geom_bar"}],
        },
    }
    if tier3 is not None:
        plot["steps"] = {"tier3": copy.deepcopy(list(tier3))}
    return plot


def minimal_recipe(recipe_id: str = "minimal", *, label: Optional[str] = None,
                   schemas: Optional[Mapping[str, dict]] = None, joins: Optional[Mapping[str, dict]] = None,
                   steps: Optional[Iterable[dict]] = None, plots: Optional[Mapping[str, dict]] = None) -> dict:
    """A recipe in format 1 as a new dictionary (nothing is shared with the arguments or between two calls).

    - `recipe_id`: the id; the file must be named `<recipe_id>.yaml` (`write_recipe` checks it).
    - `schemas`: schema id -> schema (see `minimal_schema`). Without it: one schema `table` with the columns
      `sample_id` (String, the entity key) and `value` (Float64), read from `data/table.tsv`.
    - `joins`: join id -> join (see `minimal_join`). Without it the key `joins` is absent.
    - `steps`: the tier 1 steps of the only schema. With several schemas it is refused: say the place with
      `minimal_schema(tier1=...)` or `minimal_join`.
    - `plots`: plot id -> plot entry (see `minimal_plot`), put in one group `main`. Without it: one bar chart
      `<recipe_id>_plot` of the first column of the first join, or of the first schema when there is no join.
      `plots={}` writes `analysis_groups: {}`: a draft, valid in profile `build` only.
    """
    if schemas is None:
        schemas = {_DEFAULT_SCHEMA_ID: minimal_schema(f"data/{_DEFAULT_SCHEMA_ID}.tsv", _DEFAULT_COLUMNS, entity_key="sample_id")}
    schemas = copy.deepcopy(dict(schemas))
    joins = copy.deepcopy(dict(joins)) if joins is not None else None
    if steps is not None:
        if len(schemas) != 1:
            raise ValueError(f"steps were given for {len(schemas)} schemas, so their place is not said: "
                             "write them with minimal_schema(tier1=...) or minimal_join(...)")
        (only,) = schemas.values()
        only["wrangling"]["tier1"] = copy.deepcopy(list(steps))
    if plots is None:
        plots = {f"{recipe_id}_plot": _default_plot(schemas, joins)}
    format_spec = spec()
    recipe: Dict[str, Any] = {
        "id": recipe_id,
        "spec_version": format_spec["format_version"],
        "data_engine": format_spec["engines"]["data_engine"][0],
        "plot_engine": format_spec["engines"]["plot_engine"][0],
        "info": {"label": label if label is not None else recipe_id},
        "data_schemas": schemas,
    }
    if joins is not None:
        recipe["joins"] = joins
    recipe["analysis_groups"] = {DEFAULT_GROUP_ID: {"label": "Main", "plots": copy.deepcopy(dict(plots))}} if plots else {}
    return recipe


def _default_plot(schemas: Mapping[str, dict], joins: Optional[Mapping[str, dict]]) -> dict:
    """A bar chart of the first column of the first join's base table, or of the first schema."""
    first_schema = next(iter(schemas))
    if joins:
        target = next(iter(joins))
        ingredients: List[dict] = joins[target].get("ingredients") or []
        source = ingredients[0]["dataset_id"] if ingredients else first_schema
    else:
        target = source = first_schema
    columns = list((schemas.get(source) or {}).get("input_fields") or {})
    if not columns:
        raise ValueError(f"the schema {source!r} has no column to draw: give plots=..., or plots={{}} for a draft without plots")
    return minimal_plot(target, {"x": columns[0]})


# -- the text

def recipe_text(value: Any, comment: Optional[str] = None) -> str:
    """The YAML text of a recipe or of a fragment, keys in the order given. `comment` becomes `#` lines at the top."""
    head = "".join(f"# {line}\n" if line else "#\n" for line in comment.splitlines()) if comment else ""
    return head + yaml.dump(value, Dumper=_RecipeDumper, sort_keys=False, default_flow_style=False, allow_unicode=True)


def write_recipe(path: Union[str, Path], recipe: Mapping[str, Any], comment: Optional[str] = None) -> Path:
    """Write a recipe file. The id of a recipe is its file name (spec section 4): another id is refused, nothing is written."""
    path = Path(path)
    if not isinstance(recipe, Mapping) or recipe.get("id") != path.stem:
        found = recipe.get("id") if isinstance(recipe, Mapping) else None
        raise ValueError(f"the recipe id is {found!r} but the file is {path.stem!r}: the id of a recipe is its file name without .yaml")
    return _write(path, recipe_text(dict(recipe), comment))


def write_fragment(path: Union[str, Path], value: Union[Mapping, list], comment: Optional[str] = None) -> Path:
    """Write an included file: the value itself (a mapping or a list), with no wrapper key (spec 6.1)."""
    if not isinstance(value, (Mapping, list)):
        raise ValueError(f"a fragment is a mapping or a list, not {type(value).__name__}")
    return _write(Path(path), recipe_text(dict(value) if isinstance(value, Mapping) else value, comment))


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
