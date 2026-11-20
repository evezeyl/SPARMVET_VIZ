"""`check_recipe`: the one function that judges a recipe in format version 1 (spec sections 3 to 11).

Pure: it reads the recipe (a dictionary) and the data of the specification file `recipe_spec.yaml`, and never the data
files, the registries or the disk. What it cannot know it is given:
- `catalogs`: the registries as plain data (`actions`: name -> ui_schema, `components`: name -> allowed argument names or
  None for free-form, `themes`: a set of names, `component_kinds`: component name -> exact, modified or own, what it is to
  plotnine, named in the messages about its arguments). Without them the checks of actions and components are not run, and
  `coverage` says so. `action_engines` and `component_engines` (name -> engine, the `engine` field of every registry entry,
  D-0238) let it refuse a step or a layer written in a block of another engine (EN02); without them `coverage` lacks `engines`;
- `graph`: an object with `columns_of(dataset_id)` (the columns of a table after its tier 1), for the checks of columns
  per node (J08, X7); without it they are not run;
- `roots` and `base`: the folders a development path may lie in, and the folder its path is relative to, the project
  root (PA02); `bundle_dir`: the folder of a gallery example, for its companion files (GP05).
The caller reads `result.coverage` and asserts it when it must have every check (HOME's load gate does).

Every problem has a permanent code (the catalogue of spec section 11), a severity (E error, A advice), a path in the
recipe, what is wrong and the fix, in the message style of spec P5.

# @deps
# provides: function:check_recipe, function:spec, function:plot_keys, class:Problem, class:Result
# consumes: libs/utils/src/utils/recipe_spec.yaml, libs/utils/src/utils/engines.py, libs/utils/src/utils/action_names.py, libs/utils/src/utils/ui_schema.py, libs/utils/src/utils/formula_check.py, libs/utils/src/utils/plot_text_check.py, libs/utils/src/utils/recipe_paths.py, libs/utils/src/utils/polars_types.py, libs/utils/src/utils/filter_values.py, libs/utils/src/utils/recipe_tiers.py, libs/utils/src/utils/fix_text.py (split_fix, with_fix)
# consumed_by: libs/utils/src/utils/recipe_loader.py, libs/utils/src/utils/recipe_factory.py, libs/utils/src/utils/recipe_migration.py, libs/utils/src/utils/strict_form_migration.py, libs/ingestion/src/ingestion/declared.py, libs/viz_gallery/src/viz_gallery/gallery_manager.py, libs/viz_gallery/src/viz_gallery/example_recipe.py, libs/viz_gallery/src/viz_gallery/taxonomy.py, assets/scripts/convert_gallery_examples.py, assets/scripts/create_data_analysis_recipe.py, libs/utils/tests/test_recipe_check.py
# doc: .claude/design/recipe_format_spec.md (sections 3 to 11, 14)
# @end_deps
"""
import difflib
import re
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import polars as pl
import yaml

from utils import action_names, recipe_tiers
from utils.action_names import AUDIT_ACTIONS, TIER1_ONLY
from utils.random_layers import is_random_layer, is_seed_value
from utils.engines import ENGINES
from utils.filter_values import FilterValueError, check_filter
from utils.fix_text import split_fix, with_fix
from utils.formula_check import formula_problems
from utils.plot_text_check import facet_variable_problems, layer_text_problems
from utils import join_keys
from utils.polars_types import PARAMETER_KEYS, dtype_with_parameters, text_dtype_names
from utils.recipe_paths import containment_problems, shape_problems
from utils.ui_schema import STEP_KEYS, step_problems

# The tool that rewrites a recipe of the old shape (written in a later step of the engine-keys change); every refusal of an old shape names it.
REWRITE_TOOL = "assets/scripts/migrate_recipe_engine_keys.py"

# Tier-1 actions that only remove or reorder rows: they cannot change the columns or their types (exact names).
JOIN_KEEPS_COLUMNS = join_keys.JOIN_KEEPS_COLUMNS

# Steps whose `maintain_order` says whether the order of the rows is fixed (ST13).
_ORDER_STEPS = frozenset({action_names.SORT, action_names.UNIQUE, action_names.GROUP_BY, action_names.JOIN})

_SUM_OF_COLUMN = re.compile(r"pl\.col\(\s*['\"]([^'\"]+)['\"]\s*\)\.sum\(\)")

PROFILES = ("run", "build", "gallery", "audit")
_AUDIT_ID = recipe_tiers.AUDIT_ID   # one form, one place (`utils.recipe_tiers`)
_SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
_TIER1_ONLY_DEFAULT = TIER1_ONLY


def _declared_dtype(field: Any) -> Optional[Any]:
    """The Polars dtype a field declares (type and its parameters), None when it cannot be read (the field checks report it)."""
    if not isinstance(field, dict) or not isinstance(field.get("type"), str):
        return None
    try:
        return dtype_with_parameters(field["type"], field)
    except Exception:  # unknown dtype name or missing parameters: FD02 and FD05 report them
        return None


@lru_cache(maxsize=1)
def spec() -> dict:
    """The recipe format as data (the packaged file `recipe_spec.yaml`, plus the engine names of `utils.engines`)."""
    data = yaml.safe_load(resources.files("utils").joinpath("recipe_spec.yaml").read_text(encoding="utf-8"))
    data["engines"] = {key: list(names) for key, names in ENGINES.items()}  # one source: utils/engines.py (ADR-106 V8)
    return data


def plot_defaults_keys() -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """`(allowed keys, removed keys)` of `plot_defaults`, read from the specification.

    The plot library reads its list from here, so the checker and the library cannot disagree on what `plot_defaults` may
    hold (D-0220, D-0242).
    """
    data = spec()
    return tuple(data["elements"]["plot_defaults"]["optional"]), tuple(data["removed"]["plot_defaults"])


def plot_keys() -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """`(entry keys, content keys)` of a plot entry, read from the specification (`elements.plot`).

    The entry keys (`ui_label`, `ui_title`, `description`, `comment`, `taxonomy`, `plot_engine`, `tier3`) belong to the app;
    the content keys (`target_dataset`, `mapping`, `layers`, `theme`, ...) are what the plot library draws from. The plot
    library reads the two lists from here, so the checker and the library cannot disagree on what an entry may hold.
    """
    plot = spec()["elements"]["plot"]
    entry = tuple(plot["entry_keys"])
    content = tuple(key for key in [*plot["required"], *plot["optional"]] if key not in entry)
    return entry, content


def _plotnine_note(name: str, kinds: dict) -> str:
    """What a plot component is to plotnine (ADR-106 V1), added to a message about its arguments so the maker knows where to look."""
    kind = kinds.get(name)
    if kind == "exact":
        return f" (exactly plotnine's {name}: its arguments are plotnine's)"
    if kind == "modified":
        return f" (changes plotnine's {name}: read its description for what is different)"
    if kind == "own":
        return " (is not in plotnine: read its description for its arguments)"
    return ""


@dataclass(frozen=True)
class Problem:
    code: str
    severity: str  # "E" or "A"
    path: str
    message: str
    fix: str = ""

    def text(self, recipe: str = "") -> str:
        """`recipe : path : what is wrong. Fix: what to write.` (spec P5)."""
        head = " : ".join(part for part in (recipe, self.path) if part)
        body = with_fix(self.message, self.fix)
        return f"{head} : [{self.code}] {body}" if head else f"[{self.code}] {body}"


@dataclass
class Result:
    problems: List[Problem] = field(default_factory=list)
    coverage: Set[str] = field(default_factory=set)

    @property
    def errors(self) -> List[Problem]:
        return [p for p in self.problems if p.severity == "E"]

    @property
    def advices(self) -> List[Problem]:
        return [p for p in self.problems if p.severity == "A"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def codes(self) -> List[str]:
        return [p.code for p in self.problems]


class _Check:
    def __init__(self, raw, profile, file_stem, catalogs, graph, roots, base, bundle_dir) -> None:
        self.raw = raw
        self.profile = profile
        self.file_stem = file_stem
        self.catalogs = catalogs
        self.graph = graph
        self.roots = roots
        self.base = base
        self.bundle_dir = bundle_dir
        self.result = Result(coverage={"structure"})
        self.spec = spec()
        self.schema_ids: Set[str] = set()
        self.join_ids: Set[str] = set()
        self.schema_bodies: Dict[str, Any] = {}
        self.audit_ids: Dict[str, str] = {}   # {audit id: where it stands}: an audit id is used once in the whole recipe

    # -- helpers
    def add(self, code: str, path: str, message: str, fix: str = "", severity: str = "E") -> None:
        self.result.problems.append(Problem(code, severity, path, message, fix))

    def unknown_keys(self, element: str, mapping: dict, path: str, code: str, shape_codes: Optional[dict] = None,
                     skip: Iterable[str] = ()) -> None:
        wanted = self.spec["elements"][element]
        known = set(wanted["required"]) | set(wanted["optional"]) | self.label_keys_of(element)
        renamed = self.spec["renamed"].get(element, {})
        old_shapes = self.spec["old_shapes"].get(element, {})
        for key in mapping:
            if key in known or key in skip:
                continue
            if key in old_shapes:
                self.add((shape_codes or {}).get(key, code), f"{path}.{key}" if path else str(key), f"{key} is not a key of this element any more (the form of the recipe changed)",
                         f"{old_shapes[key]}. Rewrite tool: {self.spec['old_shapes']['tool']} (it rewrites a recipe file and says what it changed)")
            elif key in renamed:
                self.add(code, f"{path}.{key}" if path else str(key), f"{key} is not a key of this element", f"{renamed[key]}")
            else:
                close = difflib.get_close_matches(str(key), list(known), n=1, cutoff=0.6)
                fix = f"write {close[0]}" if close else "remove it, or write one of " + ", ".join(sorted(known))
                self.add(code, f"{path}.{key}" if path else str(key), f"{key} is not a key of this element", fix)

    def required_keys(self, element: str, mapping: dict, path: str, code: str) -> None:
        for key in self.spec["elements"][element]["required"]:
            if key not in mapping:
                self.add(code, path, f"{key} is required", f"add {key}")

    def label_keys_of(self, element: str) -> Set[str]:
        """The key that names this element in the table `label_keys` of the specification (pending: Eve decides which become ui_label)."""
        found = self.spec["label_keys"].get(element)
        return {found} if found else set()

    def label_key(self, element: str) -> str:
        return self.spec["label_keys"][element]

    # -- the whole recipe
    def run(self) -> Result:
        raw = self.raw
        if not isinstance(raw, dict):
            self.add("T01", "", "the recipe is not a mapping", "a recipe is a YAML mapping of keys")
            return self.result
        self.top_level(raw)
        self.version(raw)
        self.engines(raw)
        self.info(raw.get("info"))
        self.entity(raw)
        self.schemas(raw)
        self.joins(raw)
        self.groups(raw)
        self.plot_defaults(raw)
        if self.profile == "gallery":
            self.gallery(raw)
        self.result.coverage.add("actions") if self.catalogs and "actions" in self.catalogs else None
        if self.catalogs and "components" in self.catalogs:
            self.result.coverage.add("components")
        if self.catalogs and "action_engines" in self.catalogs and "component_engines" in self.catalogs:
            self.result.coverage.add("engines")
        if self.graph is not None:
            self.result.coverage.add("columns")
        return self.result

    def top_level(self, raw: dict) -> None:
        for key in raw:
            if key == "plots":
                self.add("T08", "plots", "a root-level plots key is not allowed", self.spec["renamed"]["top"]["plots"])
        self.unknown_keys("top", {k: v for k, v in raw.items() if k != "plots"}, "", "T03")
        for key in self.spec["elements"]["top"]["required"]:
            if key not in raw and key != "spec_version":
                self.add("T04", key, f"{key} is required", f"add {key}")
        if self.file_stem is not None and isinstance(raw.get("id"), str) and raw["id"] != self.file_stem:
            self.add("T05", "id", f"id is {raw['id']!r} but the file is {self.file_stem!r}", f"write id: {self.file_stem}")

    def version(self, raw: dict) -> None:
        current = self.spec["format_version"]
        if "spec_version" not in raw:
            self.add("V01", "spec_version", "this recipe is in the old format 0", "run the migration tool (assets/scripts/migrate_recipe_format.py)")
            return
        value = raw["spec_version"]
        if isinstance(value, bool) or not isinstance(value, int):
            self.add("V04", "spec_version", f"spec_version {value!r} is not an integer", f"write spec_version: {current}")
        elif value < current:
            self.add("V02", "spec_version", f"written for format {value}, this app reads {current}", "run the migration tool")
        elif value > current:
            self.add("V03", "spec_version", f"written for format {value}, this app reads {current}", "update the app")

    def engines(self, raw: dict) -> None:
        for key in self.spec["engines"]:
            if key in raw:
                self.engine_value(raw[key], key, key)

    def engine_value(self, value: Any, key: str, path: str) -> None:
        """T06 for an engine value at any level: the top of the recipe, a tier (`data_engine`) or a plot entry (`plot_engine`).

        D-0239: the engine names are an open list that an app release extends; an app without the library for a name refuses it
        and the message lists the engines of the app.
        """
        allowed = self.spec["engines"][key]
        if value not in allowed:
            self.add("T06", path, f"{value!r} is not a built {key}: no library for this engine in this app (the engines of this app: {', '.join(allowed)})",
                     "write one of " + ", ".join(allowed))

    def effective_engine(self, key: str, *levels: Any) -> Any:
        """The engine of a block: the first level that writes `key` (a tier, a plot entry), then the recipe's default (D-0219)."""
        for level in levels:
            if isinstance(level, dict) and level.get(key) is not None:
                return level[key]
        return self.raw.get(key) if isinstance(self.raw, dict) else None

    def check_engine_of(self, kind: str, name: Any, wanted: Any, path: str, what: str) -> None:
        """EN02: a step or a layer written in a block of another engine; EN03: the registry gives no engine for a registered name.

        `kind` is 'action' or 'component'. Nothing is said when the catalogues give no engine table (the coverage then lacks
        `engines`), when the name is not registered (ST02 and PS04 report that), or when the block names no engine (T04 reports it).
        """
        table = (self.catalogs or {}).get(f"{kind}_engines")
        if table is None or not isinstance(wanted, str) or not isinstance(name, str):
            return  # a block engine that is not text has its one message (T06)
        # PROVISIONAL (no decision names it; it follows the plain-message rule): a block whose engine is not an engine of this
        # app at all already has its one real message (T06). An EN02 per step or layer would compare with an engine that cannot
        # run here, so there is nothing true to compare, and it hid the T06 among dozens of lines. A plot engine written in a
        # data slot (or the reverse) is an engine of the app: it keeps its EN02.
        if wanted not in {name for names in self.spec["engines"].values() for name in names}:
            return
        registry = (self.catalogs or {}).get(f"{kind}s")
        if name not in table:
            if registry is not None and name in registry:
                self.add("EN03", path, f"the registry gives no engine for the {what} {name!r}, so the check cannot tell which engine runs it. "
                         "This is a fault of the app, not of the recipe.", "Report it: every registered action and component carries an engine.")
            return
        if table[name] != wanted:
            self.add("EN02", path, f"the {what} {name!r} belongs to the engine {table[name]}, but this block is written for the engine {wanted}",
                     f"move it to a block of the engine {table[name]}, or write the engine of this block as {table[name]}")

    def info(self, info: Any) -> None:
        if info is None:
            return
        if not isinstance(info, dict):
            self.add("I01", "info", "info is not a mapping", "write info: {label: ...}")
            return
        if "display_name" in info:
            self.add("I03", "info.display_name", "display_name was renamed", self.spec["renamed"]["info"]["display_name"])
        if not info.get(self.label_key("info")):
            self.add("I01", "info", f"info.{self.label_key('info')} is required", f"add {self.label_key('info')}")
        if "comment" in info and not isinstance(info["comment"], str):
            self.add("CM01", "info.comment", "a comment is text", "write text")
        for key in ("description", "contact"):
            if not info.get(key):
                self.add("I02", f"info.{key}", f"info.{key} is missing", "Suggestion: write it (spec section 13).", "A")
        self.cut_description("info.description", info.get("description"))

    def cut_description(self, path: str, text: Any) -> None:
        """Advice D01: a description with an open bracket is probably cut where an unquoted ' #' started a YAML comment."""
        if isinstance(text, str) and text.count("(") > text.count(")"):
            self.add("D01", path, "The description seems cut. An unquoted ' #' starts a comment in YAML, so the text after it is lost.",
                     "Suggestion: put the text in quotes.", "A")

    def entity(self, raw: dict) -> None:
        entity = raw.get("entity")
        if entity is None:
            return
        if not isinstance(entity, dict):
            self.add("E01", "entity", "entity is not a mapping", "write entity: {noun, plural, population}")
            return
        self.unknown_keys("entity", entity, "entity", "E01")
        self.required_keys("entity", entity, "entity", "E01")
        population = entity.get("population")
        schemas = self.all_schemas(raw)
        if population is not None and population not in schemas and population not in (raw.get("joins") or {}):
            self.add("E02", "entity.population", f"population {population!r} is not a table of this recipe", "name a schema or a join")
        elif population in schemas and isinstance(schemas[population], dict):
            fields_ = schemas[population].get("input_fields")
            if isinstance(fields_, dict) and not any(isinstance(f, dict) and f.get("is_entity_key") for f in fields_.values()):
                self.add("E02", "entity.population", f"{population!r} has no field with is_entity_key: true", "mark the key column")

    # -- schemas and fields
    def all_schemas(self, raw: dict) -> Dict[str, Any]:
        found: Dict[str, Any] = {}
        for section in ("data_schemas", "additional_datasets_schemas"):
            if isinstance(raw.get(section), dict):
                found.update(raw[section])
        if "metadata_schema" in raw:
            found["metadata_schema"] = raw["metadata_schema"]
        return found

    def schemas(self, raw: dict) -> None:
        seen: Dict[str, str] = {}
        # One reading of "a tier-2 list that is run nowhere" (utils.recipe_tiers, issue #77): the engine and this check agree.
        unapplied = set(recipe_tiers.unapplied_schema_tier2(raw))
        for section in ("data_schemas", "additional_datasets_schemas"):
            body = raw.get(section)
            if body is None:
                continue
            if not isinstance(body, dict):
                self.add("S01", section, f"{section} is not a mapping", "write schema id: schema")
                continue
            for sid, schema in body.items():
                path = f"{section}.{sid}"
                if sid in self.spec["reserved_schema_ids"]:
                    self.add("S02", path, f"{sid!r} is a reserved id", "choose another id")
                if sid in seen:
                    self.add("S02", path, f"the id {sid!r} is also used in {seen[sid]}", "ids are shared by all schema sections: rename one")
                seen[sid] = section
                self.schema_ids.add(sid)
                self.schema_bodies[sid] = schema
                self.schema(schema, path, sid in unapplied)
        if "metadata_schema" in raw:
            self.schema_ids.add("metadata_schema")
            self.schema_bodies["metadata_schema"] = raw["metadata_schema"]
            self.schema(raw["metadata_schema"], "metadata_schema", "metadata_schema" in unapplied)

    def schema(self, schema: Any, path: str, tier2_unapplied: bool) -> None:
        if not isinstance(schema, dict):
            self.add("S01", path, "a schema is a mapping", "write label, source, null_values, strip, input_fields, wrangling")
            return
        self.unknown_keys("schema", schema, path, "S01", {"wrangling": "S06"})
        if self.label_key("schema") not in schema:
            self.add("S03", path, f"the schema has no {self.label_key('schema')}", f"add {self.label_key('schema')}")
        if not schema.get("description"):
            self.add("S04", f"{path}.description", "The schema has no description, so the grain (what one row is) is not stated.", "Suggestion: write the grain: what one row is (spec section 13).", "A")
        self.cut_description(f"{path}.description", schema.get("description"))
        if "comment" in schema and not isinstance(schema["comment"], str):
            self.add("CM01", f"{path}.comment", "a comment is text", "write text")
        self.source(schema.get("source"), f"{path}.source", "source" in schema)
        self.missing_values(schema, path, required=True)
        fields_ = schema.get("input_fields")
        if fields_ is None:
            self.add("S08", f"{path}.input_fields", "input_fields is required", "write input_fields: {} or the fields")
        elif not isinstance(fields_, dict):
            self.add("S08", f"{path}.input_fields", "input_fields is not a mapping", "write column: {type: ...}")
        else:
            for slug, definition in fields_.items():
                self.field(definition, f"{path}.input_fields.{slug}")
                self.entity_key_type(definition, f"{path}.input_fields.{slug}.type", path.rsplit(".", 1)[-1], slug)
        lists = self.tiers(schema, path, "S06", self.spec["elements"]["tiers"]["schema"], "schema")
        if isinstance(fields_, dict):
            self.sum_advices(lists, path, fields_)
        if isinstance(fields_, dict) and fields_:
            self.filter_value_problems(lists, path, [(path.rsplit(".", 1)[-1], fields_)], joins=False)
        if tier2_unapplied:
            self.add("S07", f"{path}.tier2", "tier2 of a schema applies only when the schema is plotted directly: "
                     "no plot reads this schema, so these steps would run nowhere (a join reads the tier 1 of its ingredients)",
                     "move the steps to a join, or plot this schema")

    def source(self, source: Any, path: str, present: bool) -> None:
        if not present:
            self.add("S05", path, "the schema has no source", "write source: {type: local_tsv, path: ...}")
            return
        if not isinstance(source, dict):
            self.add("S05", path, "source is not a mapping", "write {type: local_tsv, path: ...}")
            return
        self.unknown_keys("source", source, path, "S05")
        types = self.spec["elements"]["source"]["types"]
        if source.get("type") not in types:
            self.add("S05", f"{path}.type", f"source type {source.get('type')!r} is not built", "write one of " + ", ".join(types))
        if not source.get("path"):
            self.add("S05", f"{path}.path", "source.path is missing", "write a path relative to the project root")
        else:
            self.dev_path(source["path"], f"{path}.path")

    def dev_path(self, value: Any, path: str) -> None:
        shape = shape_problems(value)
        for message in shape:
            what, _, fix = message.partition(" Fix: ") if " Fix: " in message else message.partition(". Fix: ")
            self.add("PA01", path, what.rstrip("."), fix)
        if not shape and self.roots is not None:
            for message in containment_problems(value, self.roots, base=self.base or "."):
                what, _, fix = message.partition(". Fix: ")
                self.add("PA02", path, what, fix)

    def entity_key_type(self, definition: Any, path: str, table: str, slug: str) -> None:
        """E03 (D-0225, D-0067): the declared entity key (the sample id) is a String or a Categorical, never a number.

        A number as an id loses leading zeros and makes 001, 1 and 1.0 one sample, and it gives join and type problems.
        Only a column marked is_entity_key is judged: nothing is guessed from a column name. A type that cannot be read is
        left to FD02 and FD05.
        """
        if not isinstance(definition, dict) or definition.get("is_entity_key") is not True:
            return
        declared = _declared_dtype(definition)
        if declared is not None and declared.is_numeric():
            self.add("E03", path,
                     f"The sample id {slug!r} of the table {table!r} is declared {declared}, a number. A number as an id loses leading zeros, "
                     "makes 001, 1 and 1.0 one sample, and gives join and type problems.",
                     f"Suggestion: declare it as String (or Categorical) in input_fields of {table!r}.")

    def missing_values(self, mapping: dict, path: str, *, required: bool) -> None:
        for key, ok, fix in (
            ("null_values", lambda v: isinstance(v, list) and all(isinstance(i, str) for i in v), "a list of texts, [] allowed"),
            ("strip", lambda v: isinstance(v, bool), "true or false"),
        ):
            if key not in mapping:
                if required:
                    self.add("S09", f"{path}.{key}", f"{key} is required", f"write {key}: {fix}")
            elif not ok(mapping[key]):
                self.add("S09", f"{path}.{key}", f"{key} has the wrong form", f"write {fix}")

    def field(self, definition: Any, path: str) -> None:
        if isinstance(definition, str):
            self.add("FD06", path, "a field is a mapping, not a bare string", f"write {{type: {definition}}}")
            return
        if not isinstance(definition, dict):
            self.add("FD01", path, "a field is a mapping", "write {type: String}")
            return
        wanted = self.spec["elements"]["field"]
        known = set(wanted["required"]) | set(wanted["optional"]) | self.label_keys_of("field")
        renamed = self.spec["renamed"]["field"]
        for key in definition:
            if key in known:
                continue
            code = "FD03" if key == "is_primary_key" else "FD04" if key == "source_name" else "FD01"
            if key in renamed:
                self.add(code, f"{path}.{key}", f"{key} was renamed", renamed[key])
            else:
                close = difflib.get_close_matches(str(key), list(known), n=1, cutoff=0.6)
                self.add(code, f"{path}.{key}", f"{key} is not a field property", f"write {close[0]}" if close else "remove it")
        type_ = definition.get("type")
        if type_ is None:
            self.add("FD02", f"{path}.type", "type is required", "write a Polars dtype: " + ", ".join(text_dtype_names()))
        elif not isinstance(type_, str) or type_ not in text_dtype_names():
            old = self.spec["renamed_types"].get(str(type_).lower()) if isinstance(type_, str) else None
            advice = self.spec.get("type_suggestions", {}).get(str(type_).lower()) if isinstance(type_, str) else None
            fix = " ".join(advice) if advice else f"write {old}" if old else "write one of " + ", ".join(text_dtype_names())
            self.add("FD02", f"{path}.type", f"{type_!r} is not a Polars dtype that a text file can hold (the old word is no longer read)" if advice
                     else f"{type_!r} is not a Polars dtype that a text file can hold", fix)
        elif isinstance(type_, str):
            for key, users in PARAMETER_KEYS.items():
                if key in definition and type_ not in users:
                    self.add("FD05", f"{path}.{key}", f"{key} is for {', '.join(users)}, not {type_}", f"remove {key}")
            if type_ == "Enum" and not (isinstance(definition.get("categories"), list) and definition["categories"]
                                         and all(isinstance(c, str) for c in definition["categories"])):
                self.add("FD05", f"{path}.categories", "an Enum needs its levels, in order", "write categories: [low, high]")
        if "is_entity_key" in definition and not isinstance(definition["is_entity_key"], bool):
            self.add("FD05", f"{path}.is_entity_key", "is_entity_key is true or false", "write true or false")
        self.missing_values(definition, path, required=False)

    # -- steps
    def tiers(self, parent: Any, path: str, code: str, names: Iterable[str], element: str) -> Dict[str, list]:
        """The tiers of a table, a join (`tier1`, `tier2`) or a plot entry (`tier3`): each tier is its own key of `parent`.

        D-0250: a tier is a mapping with an optional `data_engine` and `steps` (the list); `tier1` is required in a table and in a
        join. Returns {tier name: the list of steps} for the tiers that are well formed; the problems of the others are reported.
        """
        names = list(names)
        lists: Dict[str, list] = {}
        if not isinstance(parent, dict):
            return lists
        old_container = any(key in parent for key in self.spec["old_shapes"].get(element, {}))  # told once, as an old shape
        if "tier1" in names and "tier1" not in parent and not old_container:
            self.add(code, f"{path}.tier1", "tier1 is required", "write tier1: {steps: []}")
        for tier in names:
            if tier in parent:
                steps = self.tier(parent[tier], f"{path}.{tier}", code, tier)
                if steps is not None:
                    lists[tier] = steps
        self.order_advices(lists, path)
        self.tie_advices(lists, path)
        return lists

    def tier(self, body: Any, path: str, code: str, name: str) -> Optional[list]:
        """One tier: a mapping with `steps` and an optional `data_engine`. Returns its list of steps, None when it cannot be read."""
        tool = self.spec["old_shapes"]["tool"]
        if not isinstance(body, dict):
            self.add(code, path, f"{name} is written as a mapping with steps, not as {'a list' if isinstance(body, list) else 'a text or an empty value'} "
                     "(the form of the recipe changed)", f"write {name}: {{steps: [...]}}. Rewrite tool: {tool} (it rewrites a recipe file and says what it changed)")
            return None
        wanted = self.spec["elements"]["tier"]
        known = set(wanted["required"]) | set(wanted["optional"])
        for key in body:
            if key in known or key == recipe_tiers.AUDIT_STEPS:   # the audit list is judged below, by the profile
                continue
            if key in ("tier1", "tier2", "tier3"):
                self.add(code, f"{path}.{key}", f"{key} is written inside {name}: each tier is a key of its own table, join or plot entry, not of another tier",
                         f"write {key} next to {name}, and keep only data_engine and steps inside it. Rewrite tool: {tool}")
            else:
                self.add(code, f"{path}.{key}", f"{key} is not a key of a tier", "a tier holds data_engine and steps only")
        if "data_engine" in body:
            self.engine_value(body["data_engine"], "data_engine", f"{path}.data_engine")
        if recipe_tiers.AUDIT_STEPS in body:
            self.audit_list(body[recipe_tiers.AUDIT_STEPS], f"{path}.{recipe_tiers.AUDIT_STEPS}", name, self.effective_engine("data_engine", body))
        if "steps" not in body:
            self.add(code, path, f"{name} has no steps", f"write {name}: {{steps: []}} (steps is the list of steps, empty when there are none)")
            return None
        steps = body["steps"]
        if not isinstance(steps, list):
            self.add(code, f"{path}.steps", f"{name}.steps is a list of steps", "write steps: [...]")
            return None
        self.steps(steps, f"{path}.steps", name, self.effective_engine("data_engine", body))
        return steps

    # PROVISIONAL wording: the texts of AU01, AU02, AU03 and of the ST08 line for an audit id among the author's steps are the builder's (piece C-1); the owner reads
    # them in the app and may keep or change them (D-0330). The codes AU01 to AU03 are new and are not yet in spec section 11.
    def audit_step_keys(self, step: dict, where: str) -> None:
        """What an item of `audit_steps` must have (D-0322, D-0329, D-0321): an allowed action, an audit id used once in the recipe, a reason."""
        action = step.get("action")
        if isinstance(action, str) and action not in AUDIT_ACTIONS:
            self.add("AU02", f"{where}.action", f"the audit step is '{action}'; an audit step is a filter, a column drop or a removal by key: {', '.join(AUDIT_ACTIONS)} "
                     "(a removal by key is the filter on the key column)", f"use one of {', '.join(AUDIT_ACTIONS)}")
        step_id = step.get("id")
        if not isinstance(step_id, str) or not _AUDIT_ID.match(step_id):
            self.add("AU03", f"{where}.id", f"the audit step has no audit id ({step_id!r})", "write id: audit_<8 hex>_<k>")
        elif step_id in self.audit_ids:
            self.add("AU03", f"{where}.id", f"the audit id {step_id} is used twice (also at {self.audit_ids[step_id]})", "ids are unique in the recipe")
        else:
            self.audit_ids[step_id] = where
        reason = step.get(recipe_tiers.AUDIT_COMMENT)
        if not isinstance(reason, str) or not reason.strip():
            self.add("AU03", f"{where}.{recipe_tiers.AUDIT_COMMENT}", "the audit step has no reason (audit_comment is a text that is not empty)",
                     f"write {recipe_tiers.AUDIT_COMMENT}: <why the step was added>")

    def sum_advices(self, wrangling: Dict[str, list], path: str, fields: dict) -> None:
        """ST15 (advice, never blocks): a sum on a column declared Int32 or UInt32 (D43, PROVISIONAL).

        Only where the declared type is known: a step of this schema's own wrangling on a column of its input_fields, from
        the start of tier 1 until a step that may change the columns (a cast is followed: its dtype becomes the type).
        Not seen: a sum inside another formula (with_columns, mutate), a type made 32-bit by an earlier step, a join result.
        """
        types = {name: definition.get("type") for name, definition in fields.items() if isinstance(definition, dict)}
        steps = [s for tier in ("tier1", "tier2") for s in (wrangling.get(tier) if isinstance(wrangling.get(tier), list) else [])]
        positions = [(tier, i) for tier in ("tier1", "tier2") for i, _ in enumerate(wrangling.get(tier) if isinstance(wrangling.get(tier), list) else [], start=1)]
        for (tier, index), step in zip(positions, steps):
            if not isinstance(step, dict):
                return
            name = step.get("action")
            where = f"{path}.{tier}.steps[{index}]"
            if name == action_names.CAST:
                columns, dtype = step.get("columns"), step.get("dtype")
                if not isinstance(columns, list) or not isinstance(dtype, str):
                    return
                for column in columns:
                    if not isinstance(column, str):
                        return  # the parameter check (ST10, names must be text) refuses this step; no type is known for it here
                    types[column] = dtype
                continue
            wide = []
            if name == action_names.SUM:
                wide = list(types)
            elif name == action_names.CUM_SUM and isinstance(step.get("columns"), list):
                wide = [c for c in step["columns"] if isinstance(c, str)]
            elif name == action_names.GROUP_BY and isinstance(step.get("named_aggs"), dict):
                wide = [m for text in step["named_aggs"].values() if isinstance(text, str) for m in _SUM_OF_COLUMN.findall(text)]
            for column in dict.fromkeys(wide):
                if types.get(column) in ("Int32", "UInt32"):
                    self.add("ST15", where,
                             f"{name} of the column {column!r}, declared {types[column]}, can give a wrong total. A 32-bit whole-number total wraps around "
                             "above about 2 thousand million (4 for UInt32) with no error and can be negative "
                             "(the checker does not see a sum inside a formula, in a join result, or on a column made 32-bit by an earlier step).",
                             f"Suggestion: write a polars_cast step to Int64 (whole numbers) or Float64 (decimal numbers; it holds about 15 to 16 exact digits, so very large whole numbers lose their last digits) for {column!r} before this step.",
                             "A")
            if not isinstance(name, str) or name not in JOIN_KEEPS_COLUMNS and name not in (action_names.SUM, action_names.CUM_SUM):
                return  # the columns after this step are not known from the declarations

    def tie_advices(self, lists: Dict[str, list], path: str) -> None:
        """ST14 (advice, never blocks): every top_k or bottom_k step. The checker cannot know whether ties exist in the data."""
        for tier, steps in lists.items():
            for index, step in enumerate(steps, start=1):
                if isinstance(step, dict) and step.get("action") in (action_names.TOP_K, action_names.BOTTOM_K):
                    nan_place = "first" if step["action"] == action_names.TOP_K else "last"
                    self.add("ST14", f"{path}.{tier}.steps[{index}]",
                             f"Warning: {step['action']} keeps at most k rows: exactly k when the table has k rows or more. If several rows have the same value as the k-th row, only some of them fit, "
                             "and Polars does not promise which ones. "
                             f"A NaN comes {nan_place} ({'last' if nan_place == 'first' else 'first'} if `reverse` is true for that column). "
                             "Rows with no value fill the k rows when the real values run out.",
                             "Suggestion: to always keep the same rows, add a row number (`polars_with_row_index`) and use it as the last `by` column. "
                             "Suggestion: to keep every row that ties with the k best, use `polars_rank` (method `min`) and a filter; this can return more than k rows.",
                             "A")

    def order_advices(self, lists: Dict[str, list], path: str) -> None:
        """ST13 (advice, never blocks): a position action after a step that does not keep the row order.

        The checker knows an order only from what the recipe states: `maintain_order` of sort, unique, group_by and join
        (the form requires it, so it is always written). The steps are read in order, tier by tier; the last of these
        steps that comes before a position action decides. Nothing before it: the order is the file order, no advice.
        """
        unstated = None  # (path of the step, action) of the last step that does not keep the order
        for tier, steps in lists.items():
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    continue
                name = step.get("action")
                if not isinstance(name, str):
                    continue  # reported by `steps` (ST01)
                if name in _ORDER_STEPS and "maintain_order" in step:
                    keeps = step["maintain_order"] not in (False, "none")
                    unstated = None if keeps else (f"{path}.{tier}.steps[{index}]", name)
                elif name in action_names.POSITION_ACTIONS and unstated is not None:
                    self.add("ST13", f"{path}.{tier}.steps[{index}]",
                             f"{name} keeps rows by their position, but the order of the rows is not fixed by {unstated[1]} "
                             f"({unstated[0]}, maintain_order: {'none' if unstated[1] == action_names.JOIN else 'false'}), so Polars does not promise the same rows "
                             "(the checker looks only at steps with a stated order parameter; it can miss, for example, a pivot or an explode before).",
                             f"Suggestion: write maintain_order: {'left_right' if unstated[1] == action_names.JOIN else 'true'} in that step. "
                             "Suggestion: write a polars_sort step with maintain_order: true before this one.",
                             "A")

    def audit_list(self, audit_steps: Any, path: str, tier: str, engine: Any) -> None:
        """The `audit_steps` list of a tier (D-0332). Legal only in an audit recipe (profile `audit`); anywhere else it is refused with one plain line and its
        content is not read. In an audit recipe each item is a step of an allowed audit action (`action_names.AUDIT_ACTIONS`, D-0322) with an audit id and a
        reason (`audit_comment`, a text that is not empty), and passes the same checks as any step (the action's parameters, the engine of the tier)."""
        if self.profile != "audit":
            self.add("AU01", path, "only an audit recipe has audit steps (an audit recipe is the copy the audit made of a recipe; the app writes it, an author never does)",
                     f"remove {recipe_tiers.AUDIT_STEPS}; a step of the author goes in steps")
            return
        if not isinstance(audit_steps, list):
            self.add("AU03", path, f"{recipe_tiers.AUDIT_STEPS} is a list of steps", f"write {recipe_tiers.AUDIT_STEPS}: [...]")
            return
        self.steps(audit_steps, path, tier, engine, audit=True)

    def steps(self, steps: list, path: str, tier: str, engine: Any = None, audit: bool = False) -> None:
        """The steps of one list. `audit` is True for an `audit_steps` list of an audit recipe, False for the author's `steps` (where an audit id or an
        `audit_comment` is refused in every profile)."""
        actions = (self.catalogs or {}).get("actions")
        tier1_only = (self.catalogs or {}).get("tier1_only", _TIER1_ONLY_DEFAULT)
        for index, step in enumerate(steps, start=1):
            where = f"{path}[{index}]"
            if not isinstance(step, dict) or "action" not in step:
                self.add("ST01", where, "a step is a mapping with an action", "write - {action: <name>, ...}")
                continue
            if audit:
                self.audit_step_keys(step, where)
            else:
                if "id" in step:
                    if self.profile == "audit" and isinstance(step["id"], str) and _AUDIT_ID.match(step["id"]):
                        self.add("ST08", f"{where}.id", f"the audit id {step['id']} is on a step of the author's list: an audit step belongs in {recipe_tiers.AUDIT_STEPS}",
                                 f"move the step to {recipe_tiers.AUDIT_STEPS}, or remove id")
                    else:
                        self.add("ST08", f"{where}.id", "authors write no step id (the app writes it)", "remove id")
                if recipe_tiers.AUDIT_COMMENT in step:
                    self.add("AU01", f"{where}.{recipe_tiers.AUDIT_COMMENT}",
                             f"{recipe_tiers.AUDIT_COMMENT} is the reason of an audit step: it is written only on a step of {recipe_tiers.AUDIT_STEPS} in an audit recipe",
                             f"remove {recipe_tiers.AUDIT_COMMENT}; the author's note is comment")
            if "comment" in step and not isinstance(step["comment"], str):
                self.add("CM01", f"{where}.comment", "a comment is text", "write text")
            if tier in ("tier2", "tier3") and isinstance(step.get("action"), str) and step.get("action") in tier1_only:
                self.add("ST05", where, f"{step['action']} is only allowed in tier1", "move it to tier1")
            self.check_engine_of("action", step.get("action"), engine, where, "step")
            name = step["action"]
            if not isinstance(name, str):
                self.add("ST01", f"{where}.action", f"the action of a step is a name (text); it is {name!r}", "write - {action: <name>, ...}")
                continue
            if actions is None:
                continue
            if name not in actions:
                legacy = (self.catalogs or {}).get("old_action_names", {}).get(name)
                close = difflib.get_close_matches(str(name), list(actions), n=1, cutoff=0.6)
                why, use = "", None
                if isinstance(legacy, dict):  # a removed name: the replacement (when one is known) and the reason
                    why, use = (f" (removed: {legacy['why']})" if legacy.get("why") else ""), legacy.get("use")
                elif legacy:
                    use = legacy
                fix = (f"Suggestion: use {use}." if use else f"Suggestion: write {close[0]}." if close
                       else "Suggestion: choose a registered action.")
                self.add("ST02", f"{where}.action", f"{name!r} is not a registered action{why}", fix)
                continue
            schema = actions[name]
            if not isinstance(schema, dict):
                continue
            for problem in step_problems(name, step, schema):
                self.add(problem.code, f"{where}.{problem.param}" if problem.param else where, problem.message, problem.fix)
            self.formulas(step, schema, where)

    def formulas(self, step: dict, schema: dict, where: str) -> None:
        """ST06 for every formula the step holds: a parameter that is a text, a mapping of texts or a list of texts.

        A parameter takes formulas when its schema says `widget: expression` (one text) or `value_widget: expression` (the
        values of a mapping, the items of a list). A formula parameter without that mark is not read, so the registry
        test `app/tests/test_checker_reads_every_formula_place.py` fails for an action that evaluates a formula in
        a parameter the schema does not mark (D-0030).
        """
        for name, definition in schema.get("params", {}).items():
            value = step.get(name)
            if value is None:
                continue
            if definition.get("widget") == "expression" and isinstance(value, str):
                values = [value]
            elif definition.get("value_widget") == "expression" and definition.get("widget") == "mapping" and isinstance(value, dict):
                values = [v for v in value.values() if isinstance(v, str)]
            elif definition.get("value_widget") == "expression" and definition.get("widget") == "list" and isinstance(value, list):
                values = [v for v in value if isinstance(v, str)]
            else:
                continue
            for text in values:
                for message in formula_problems(text):
                    what, fix = split_fix(message)
                    self.add("ST06", f"{where}.{name}", what, fix)

    def filter_value_problems(self, steps: Dict[str, list], path: str, tables: List[Tuple[str, Dict[str, Any]]], *, joins: bool) -> None:
        """ST12: a `modif_filter` value does not have the declared type of its column (ADR-104 point 7).

        Walks tier1 then tier2 with the tables known at each step: a step that only removes or reorders rows keeps them,
        a join (in a join) adds the declared columns of its right table, any other step may change a column and ends the
        check (silent: the engine is the judge there). A column absent from every known table is not judged either.
        """
        for tier in ("tier1", "tier2"):
            for index, step in enumerate(steps.get(tier) or [], start=1):
                if not isinstance(step, dict):
                    return
                action = step.get("action")
                if action == action_names.FILTER:
                    self.filter_value_at(step, f"{path}.{tier}.steps[{index}].value", tables)
                elif joins and "right_ingredient" in step:
                    right = self.declared_fields(step["right_ingredient"])
                    if right is None:
                        return
                    tables = tables + [(step["right_ingredient"], right)]
                elif not isinstance(action, str) or action not in JOIN_KEEPS_COLUMNS:
                    return

    def filter_value_at(self, step: dict, where: str, tables: List[Tuple[str, Dict[str, Any]]]) -> None:
        column, op, value = step.get("column"), step.get("op"), step.get("value")
        if not isinstance(column, str) or value is None:
            return
        owner = next(((name, fields[column]) for name, fields in tables if column in fields), None)
        declared = _declared_dtype(owner[1]) if owner else None
        if declared is None:
            return
        try:
            check_filter(op, value, declared)  # the rule of the engine: the operator fits the type, each value has it
        except FilterValueError as exc:
            self.add("ST12", where, f"{exc.problem} (column {column!r} of {owner[0]!r})", exc.fix)

    # -- joins
    def joins(self, raw: dict) -> None:
        joins = raw.get("joins")
        if joins is None:
            return
        if not isinstance(joins, dict):
            self.add("J01", "joins", "joins is a mapping of id to join", "write join id: {...}")
            return
        unapplied_joins = set(recipe_tiers.unapplied_join_tier2(raw))
        for jid, join in joins.items():
            path = f"joins.{jid}"
            self.join_ids.add(jid)
            if jid in unapplied_joins:
                self.add("J14", f"{path}.tier2", "tier2 of a join applies only when a plot reads the join: "
                         "no plot reads this join, so these steps would run nowhere",
                         "plot this join, or remove the steps")
            if jid in self.schema_ids:
                self.add("X1", path, f"the id {jid!r} is also a schema", "a plot's target must name one thing: rename one")
            if not isinstance(join, dict):
                self.add("J01", path, "a join is a mapping", f"write {self.label_key('join')}, ingredients, tier1")
                continue
            self.unknown_keys("join", join, path, "J01", {"steps": "J07"})
            if self.label_key("join") not in join:
                self.add("J02", path, f"the join has no {self.label_key('join')}", f"add {self.label_key('join')}")
            if not join.get("description"):
                self.add("J03", f"{path}.description", "The join has no description, so its grain and its join type are not stated.", "Suggestion: write the grain and the join type (spec section 13).", "A")
            self.cut_description(f"{path}.description", join.get("description"))
            if "comment" in join and not isinstance(join["comment"], str):
                self.add("CM01", f"{path}.comment", "a comment is text", "write text")
            ingredient_ids = self.ingredients(join.get("ingredients"), f"{path}.ingredients")
            lists = self.tiers(join, path, "J07", self.spec["elements"]["tiers"]["join"], "join")
            self.join_steps(lists, path, ingredient_ids)
            first = self.declared_fields(ingredient_ids[0]) if ingredient_ids else None
            if first is not None:
                self.filter_value_problems(lists, path, [(ingredient_ids[0], first)], joins=True)
            labels = join.get("labels")
            if labels is not None and not (isinstance(labels, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in labels.items())):
                self.add("J06", f"{path}.labels", "labels maps a column to a display text", "write labels: {column: text}")
            self.join_columns(join, path, ingredient_ids)

    def ingredients(self, ingredients: Any, path: str) -> List[str]:
        if not isinstance(ingredients, list) or not ingredients:
            self.add("J04", path, "ingredients is a list of {dataset_id: ...}, at least one", "write ingredients: [{dataset_id: Table}]")
            return []
        ids: List[str] = []
        for index, item in enumerate(ingredients, start=1):
            if not isinstance(item, dict) or set(item) != {"dataset_id"}:
                self.add("J04", f"{path}[{index}]", "an ingredient is {dataset_id: <schema id>}", "write - {dataset_id: Table}")
                continue
            dataset = item["dataset_id"]
            if not isinstance(dataset, str):
                self.add("J04", f"{path}[{index}]", f"dataset_id of an ingredient is the id of a schema (text); it is {dataset!r}", "write - {dataset_id: Table}")
                continue
            if dataset not in self.schema_ids:
                self.add("J04", f"{path}[{index}]", f"{dataset!r} is not a schema of this recipe", "name a schema")
            elif dataset in ids:
                self.add("J04", f"{path}[{index}]", f"{dataset!r} appears twice", "list each ingredient once")
            ids.append(dataset)
        return ids

    def join_steps(self, steps: Dict[str, list], path: str, ingredient_ids: List[str]) -> None:
        for tier in ("tier1", "tier2"):
            for index, step in enumerate(steps.get(tier) or [], start=1):
                if not isinstance(step, dict) or "right_ingredient" not in step:
                    continue
                where = f"{path}.{tier}.steps[{index}]"
                right_is_text = isinstance(step["right_ingredient"], str)
                if tier == "tier1" and right_is_text:  # the key checks compare tables by id: they need a text id
                    self.join_key_problems(steps["tier1"], index - 1, where, ingredient_ids)
                    self.join_advices(steps["tier1"], index - 1, where, ingredient_ids)
                if not right_is_text:
                    self.add("J05", f"{where}.right_ingredient", f"right_ingredient of a join step is the id of an ingredient (text); it is {step['right_ingredient']!r}",
                             "write right_ingredient: Table")
                elif step["right_ingredient"] not in ingredient_ids:
                    self.add("J05", where, f"right_ingredient {step['right_ingredient']!r} is not an ingredient of this join", "list it in ingredients")
                # a join on conditions has no key columns: its predicates say which rows match
                if step.get("action") != action_names.JOIN_WHERE and ("on" in step or True in step) == ("left_on" in step or "right_on" in step):
                    self.add("J05", where, "write either on, or left_on with right_on", "choose one form")
                if True in step:
                    self.add("T07", where, "an unquoted on became the key true", "quote it: 'on'")
                for key_name in ("on", "left_on", "right_on", "by", "by_left", "by_right"):
                    value = step.get(True) if key_name == "on" and "on" not in step else step.get(key_name)
                    if value is not None and not _is_column_names(value):
                        self.add("J05", f"{where}.{key_name}", f"{key_name} of a join is a column name or a list of column names; it is {value!r}",
                                 "write the column names as text: on: sample_id, or on: [sample_id, gene_id]")

    def join_advices(self, tier1: list, position: int, where: str, ingredient_ids: List[str]) -> None:
        """J12, J13 (advice, never block): a join of a table with itself; a join key declared as a float.

        J12 (D-0183, Eve 2026-11-16): the right table is the first table of the join or a table joined by an earlier step.
        Every kind of join, every `how`, the same or other key columns, and the as-of join and the join on conditions give
        it; none is an error, Polars reports nothing for it. `join_keys.self_join` decides, `join_keys.self_join_text` writes
        the text; the build asks the same two functions and adds the row numbers.

        J13: a key declared Float32 or Float64 turns identifiers written differently ("001", "1", "1.0") into one number,
        and a join then merges different samples without a message (JOIN-FLOAT-1). The engine keeps what the recipe
        declares; the advice says what it means.
        """
        step = tier1[position]
        if not isinstance(step.get("action"), str):
            return  # ST01 reports it
        if any(isinstance(b, dict) and "right_ingredient" in b and not isinstance(b["right_ingredient"], str) for b in tier1[:position]):
            return  # an earlier join step has no text id for its right table: J05 reports it, and the tables joined so far are not known
        if ingredient_ids and isinstance(step.get("how"), (str, type(None))):  # a `how` of another shape is refused by the parameter check (ST10)
            found = join_keys.self_join(ingredient_ids[0], tier1[:position], step)
            if found is not None:
                what, fix = join_keys.self_join_text(found)
                self.add("J12", where, what, fix, "A")
        on = step.get("on", step.get(True))
        left_keys = _as_list(on if on is not None else step.get("left_on"))
        right_keys = _as_list(on if on is not None else step.get("right_on"))
        right_id = step["right_ingredient"]
        if (on is None and ("left_on" not in step or "right_on" not in step)) or len(left_keys) != len(right_keys) or not ingredient_ids:
            return
        if not all(isinstance(k, str) for k in left_keys + right_keys):
            return
        left_tables = [ingredient_ids[0]]
        for before in tier1[:position]:
            if not isinstance(before, dict):
                return
            if "right_ingredient" in before:
                if not isinstance(before["right_ingredient"], str):
                    return  # J05 reports it
                left_tables.append(before["right_ingredient"])
        fields_by_table = {table: self.declared_fields(table) for table in set(left_tables) | {right_id}}
        for table, columns in ((None, left_keys), (right_id, right_keys)):
            tables = [t for t in dict.fromkeys(left_tables)] if table is None else [table]
            for column in columns:
                for name in tables:
                    fields = fields_by_table.get(name)
                    field = fields.get(column) if isinstance(fields, dict) else None
                    declared = _declared_dtype(field) if field is not None else None
                    if declared is not None and declared in (pl.Float32, pl.Float64):
                        self.add("J13", where,
                                 f"The join key {column!r} is declared {declared} in {name!r}. Identifiers written differently "
                                 "(for example 001, 1 and 1.0) become the same number, leading zeros are lost, and the join merges different samples without a message.",
                                 f"Suggestion: declare the key as a text type in input_fields of {name!r} (for example String or Categorical, as for other identifiers).",
                                 "A")
                        break

    def declared_fields(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """The columns a table has after its ingestion and tier 1, from its declaration; None when a tier-1 step could change them.

        The ingestion keeps the declared columns only and gives each its declared type, so input_fields is the table
        when tier 1 has no step, or only steps that remove rows (JOIN_KEEPS_COLUMNS). Any other step may create, rename,
        drop or cast a column: then nothing is known here and the build check stays the judge.
        """
        schema = self.schema_bodies.get(dataset_id) if isinstance(dataset_id, str) else None
        if not isinstance(schema, dict) or not isinstance(schema.get("input_fields"), dict) or not schema["input_fields"]:
            return None  # an empty input_fields makes the ingestion keep every column of the file
        tier1 = schema.get("tier1")
        if tier1 is not None:
            if not isinstance(tier1, dict) or not isinstance(tier1.get("steps") or [], list):
                return None
            for step in tier1.get("steps") or []:
                if not isinstance(step, dict) or not isinstance(step.get("action"), str) or step.get("action") not in JOIN_KEEPS_COLUMNS:
                    return None
        return schema["input_fields"]

    def join_key_problems(self, tier1: list, position: int, where: str, ingredient_ids: List[str]) -> None:
        """J11, J10, J09: the build refuses a join with unequal key lists, a missing key or keys of different types (JOIN-KEY-TYPES-1).

        Asks the same rule as DataAssembler._check_join_key_types (utils.join_keys, JOIN-KEY-ONE-1), and says nothing when the declarations cannot tell: a step before
        the join that is not a join or a row filter may change the left table, and a tier-1 step of a schema may change it.
        """
        step = tier1[position]
        on = step.get("on", step.get(True))
        left_keys = _as_list(on if on is not None else step.get("left_on"))
        right_keys = _as_list(on if on is not None else step.get("right_on"))
        right_id = step["right_ingredient"]
        if on is None and ("left_on" not in step or "right_on" not in step):
            return  # J05 reports it
        if join_keys.key_length_problem(left_keys, right_keys):  # the one rule (utils.join_keys, JOIN-KEY-ONE-1)
            self.add("J11", where, f"the key lists of the join differ in length: left_on has {len(left_keys)} column(s) {left_keys} "
                     f"and right_on has {len(right_keys)} column(s) {right_keys}",
                     "write left_on and right_on with the same number of columns, paired by position, or write 'on' when the columns have the same name in both tables")
            return
        if not all(isinstance(k, str) for k in left_keys + right_keys) or not ingredient_ids:
            return
        # The left table at this step: the first ingredient, plus the columns of the tables joined before.
        left_tables = [ingredient_ids[0]]
        for before in tier1[:position]:
            if not isinstance(before, dict):
                return
            if "right_ingredient" in before:
                if not isinstance(before["right_ingredient"], str):
                    return  # J05 reports it
                left_tables.append(before["right_ingredient"])
            elif not isinstance(before.get("action"), str) or before.get("action") not in JOIN_KEEPS_COLUMNS:
                return
        left_fields = [(table, self.declared_fields(table)) for table in left_tables]
        right_fields = self.declared_fields(right_id)
        if right_fields is None or any(fields is None for _, fields in left_fields) or right_id not in self.schema_bodies:
            return
        # The types the declarations give; a column a step before may have created is known by name only (None: no difference).
        left_types: Dict[str, Any] = {}
        for _, fields in left_fields:
            for column, field in fields.items():
                left_types.setdefault(column, _declared_dtype(field))
        for key in left_keys:
            if len(left_tables) > 1 and key.endswith("_right"):  # Polars names a clashing column of an earlier join name_right
                left_types.setdefault(key, None)
        right_types = {column: _declared_dtype(field) for column, field in right_fields.items()}
        problem = join_keys.join_key_problem(left_types, right_types, left_keys, right_keys)  # the one rule (utils.join_keys)
        if problem is None:
            return
        if problem["kind"] == "missing":
            missing = [f"{key!r} is not declared in the left table ({', '.join(table for table, _ in left_fields)})" for key in problem["missing_left"]]
            missing += [f"{key!r} is not declared in {right_id}" for key in problem["missing_right"]]
            self.add("J10", where, "a join key column is not declared in input_fields: " + "; ".join(missing),
                     "write the key column names as they are in each table: 'on' for a name that is the same in both, left_on and right_on for names that differ; "
                     "the left table is the table at this step, so a column of a table joined later is not in it yet")
            return
        for pair in problem["differing"]:
            left_col, right_col, left_type, right_type = pair["left_column"], pair["right_column"], pair["left_type"], pair["right_type"]
            names = f"column {left_col!r}" if left_col == right_col else f"column {left_col!r} (left) and {right_col!r} (right)"
            self.add("J09", where, f"the join key types differ: {names} is {left_type} in the left table and {right_type} in {right_id}",
                     f"declare the same type for this field in input_fields of both tables. A polars_cast step before the join changes only the left table "
                     f"(the table at this step); the type of {right_id} is changed in its own input_fields or in its own wrangling. "
                     "The engine does not change the type of a join key for you")

    def every_action_is_text(self) -> bool:
        """True when every step of every tier-1 list of the schemas and the joins names its action in text (or is not a mapping)."""
        bodies = list(self.schema_bodies.values())
        joins = self.raw.get("joins") if isinstance(self.raw, dict) else None
        bodies += list(joins.values()) if isinstance(joins, dict) else []
        for body in bodies:
            tier1 = body.get("tier1") if isinstance(body, dict) else None
            steps = tier1.get("steps") if isinstance(tier1, dict) else None
            for step in steps if isinstance(steps, list) else []:
                if isinstance(step, dict) and not isinstance(step.get("action"), str):
                    return False
        return True

    def join_columns(self, join: dict, path: str, ingredient_ids: List[str]) -> None:
        """J08 needs the recipe graph: a column in both ingredients that is not a join key is renamed silently by Polars."""
        if self.graph is None or len(ingredient_ids) < 2:
            return
        tier1 = join.get("tier1")
        steps = tier1.get("steps") if isinstance(tier1, dict) else None
        if not isinstance(steps, list):
            return
        if not self.every_action_is_text():
            return  # the graph reads the columns through the action names; ST01 reports a step whose action is not text
        base_columns = self.graph.columns_of(ingredient_ids[0])
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict) or "right_ingredient" not in step or not isinstance(step["right_ingredient"], str):
                continue
            right = self.graph.columns_of(step["right_ingredient"])
            if base_columns is None or right is None:
                continue
            if not all(_is_column_names(step.get(k)) for k in ("on", "left_on", "right_on", "by", "by_left", "by_right")) \
                    or not _is_column_names(step.get(True)):
                continue  # a join key that is not text is reported (J05) by join_steps; no column comparison is possible
            keys = set(_as_list(step.get("on", step.get(True)))) | set(_as_list(step.get("left_on"))) | set(_as_list(step.get("right_on")))
            keys |= set(_as_list(step.get("by"))) | set(_as_list(step.get("by_left"))) | set(_as_list(step.get("by_right")))  # the `by` columns of an as-of join are merged, not renamed
            clash = sorted((set(base_columns) & set(right)) - keys)
            if clash:
                self.add("J08", f"{path}.tier1.steps[{index}]",
                         f"the column {clash[0]!r} is in both {ingredient_ids[0]} and {step['right_ingredient']} and is not a join key; "
                         "Polars would rename the second one silently",
                         "rename or drop one of them before the join")

    # -- groups, plots, spec
    def groups(self, raw: dict) -> None:
        groups = raw.get("analysis_groups")
        if groups is None:
            return
        if not isinstance(groups, dict):
            self.add("G01", "analysis_groups", "analysis_groups is a mapping of id to group", "write group id: {label, plots}")
            return
        plots_found = 0
        for gid, group in groups.items():
            path = f"analysis_groups.{gid}"
            if not isinstance(group, dict):
                self.add("G01", path, "a group is a mapping", "write label and plots")
                continue
            self.unknown_keys("group", group, path, "G01")
            if "ui_label" not in group and "label" not in group:  # an old `label` is told as renamed (above), not also as missing
                self.add("G01", path, "the group has no ui_label (the tab text)", "add ui_label")
            if not group.get("description"):
                self.add("G02", f"{path}.description", "The group has no description, so the question its plots answer is not stated.", "Suggestion: write the question its plots answer.", "A")
            self.cut_description(f"{path}.description", group.get("description"))
            if "comment" in group and not isinstance(group["comment"], str):
                self.add("CM01", f"{path}.comment", "a comment is text", "write text")
            plots = group.get("plots")
            if not isinstance(plots, dict):
                self.add("G01", f"{path}.plots", "plots is a mapping of id to plot", "write plot id: {ui_label, target_dataset, mapping, layers}")
                continue
            for pid, plot in plots.items():
                plots_found += 1
                self.plot(plot, f"{path}.plots.{pid}", pid)
        if self.profile in ("run", "gallery", "audit") and plots_found == 0:
            self.add("T09", "analysis_groups", "profile run needs at least one group with one plot", "add a group with a plot")

    def plot(self, plot: Any, path: str, pid: str) -> None:
        """A plot entry (D-0237, D-0253): the content of the plot is written in the entry itself, there is no `spec:`."""
        if not isinstance(pid, str) or not _SNAKE.match(pid):
            self.add("P03", path, f"the plot id {pid!r} is not snake_case", "use lowercase letters, digits and underscores")
        if not isinstance(plot, dict):
            self.add("P01", path, "a plot is a mapping", "write ui_label, target_dataset, mapping and layers")
            return
        self.unknown_keys("plot", plot, path, "P01", {"steps": "P04"})
        if "ui_label" not in plot and "label" not in plot:  # an old `label` is told as renamed (above), not also as missing
            self.add("P01", path, "ui_label is required", "add ui_label")
        if not plot.get("description"):
            self.add("P02", f"{path}.description", "The plot has no description, so what is drawn and counted is not stated.", "Suggestion: write what is drawn and counted (spec section 13).", "A")
        self.cut_description(f"{path}.description", plot.get("description"))
        if "comment" in plot and not isinstance(plot["comment"], str):
            self.add("CM01", f"{path}.comment", "a comment is text", "write text")
        if "plot_engine" in plot:
            self.engine_value(plot["plot_engine"], "plot_engine", f"{path}.plot_engine")
        if "tier3" in plot:
            # P05 is retired: the engine reads `tier3` (`DataOrchestrator.materialize_tier3`), so its steps are judged like any step list
            self.tiers(plot, path, "P04", self.spec["elements"]["tiers"]["plot"], "plot")
        if "taxonomy" in plot and not isinstance(plot["taxonomy"], dict):
            self.add("P01", f"{path}.taxonomy", "taxonomy is a mapping of axis to term", "write taxonomy: {family: ..., ...}")
        if "spec" not in plot:  # an old `spec` holds the content: told once as an old shape, the content is judged after the rewrite
            self.plot_content(plot, path)

    def plot_content(self, plot: dict, path: str) -> None:
        """The content of a plot (target, mapping, layers, theme, ...): the checks PS02 to PS06, read from the entry (PS01, unknown key of a spec, is retired: an unknown key of the entry is P01)."""
        target = plot.get("target_dataset")
        if not isinstance(target, str) or not target or (target not in self.schema_ids and target not in self.join_ids):
            self.add("PS02", f"{path}.target_dataset", f"target_dataset {target!r} is not a schema or a join of this recipe", "name one")
        if "mapping" not in plot or "layers" not in plot:
            self.add("PS03", path, "mapping and layers are required", "add mapping and layers")
        layers = plot.get("layers")
        if isinstance(layers, list):
            self.layers(layers, f"{path}.layers", plot_engine=self.effective_engine("plot_engine", plot))
        elif "layers" in plot:
            self.add("PS03", f"{path}.layers", "layers is a list", "write layers: [{name: geom_point}]")
        mapping = plot.get("mapping")
        if isinstance(mapping, dict) and "facet_by" in mapping and facet_variable_problems(mapping["facet_by"]):
            shown = ", ".join(repr(r) for r in facet_variable_problems(mapping["facet_by"]))
            self.add("PS06", f"{path}.mapping.facet_by", f"the facet variable {shown} is not a plain column name",
                     "Suggestion: write a column of the data (letters, digits, underscore, space, dot or dash); to facet by a computed value, add a recipe step that makes the column first")
        theme = plot.get("theme")
        themes = (self.catalogs or {}).get("themes")
        if theme is not None and themes is not None and (not isinstance(theme, str) or theme not in themes):
            self.add("PS05", f"{path}.theme", f"{theme!r} is not a registered theme" + ("" if isinstance(theme, str) else " (the theme is a name, text)"),
                     "write one of " + ", ".join(sorted(themes)))
        if "filters" in plot:
            self.add("P06", f"{path}.filters", "filters in a plot moved to the plot's tier3", "write the filters as tier3 steps")

    def layers(self, layers: list, path: str, *, needs_geom: bool = True, plot_engine: Any = None) -> None:
        components = (self.catalogs or {}).get("components")
        arguments = (self.catalogs or {}).get("component_arguments", {})
        kinds = (self.catalogs or {}).get("component_kinds", {})
        has_geom = False
        for index, layer in enumerate(layers, start=1):
            where = f"{path}[{index}]"
            if not isinstance(layer, dict) or "name" not in layer:
                self.add("PS04", where, "a layer is {name: <component>, params: {...}}", "write - {name: geom_point}")
                continue
            self.unknown_keys("layer", layer, where, "PS04")
            if "comment" in layer and not isinstance(layer["comment"], str):
                self.add("CM01", f"{where}.comment", "a comment is text", "write text")
            name = layer["name"]
            self.check_engine_of("component", name, plot_engine, where, "layer")
            has_geom = has_geom or (isinstance(name, str) and name.startswith(("geom_", "stat_")))
            if isinstance(name, str):
                # PS06: a text that plotnine evaluates as Python (smoother formula, facet variable, function string); needs no catalogue
                for param, what, suggestion in layer_text_problems(name, layer.get("params"), None):
                    self.add("PS06", f"{where}.params.{param}", what, suggestion)
            if components is None:
                continue
            if not isinstance(name, str):
                self.add("PS04", f"{where}.name", "the name of a layer is a component name (text)", "write - {name: geom_point}")
                continue
            if name not in components:
                close = difflib.get_close_matches(str(name), list(components), n=1, cutoff=0.6)
                self.add("PS04", f"{where}.name", f"{name!r} is not a registered plot component", f"write {close[0]}" if close else "choose a registered component")
                continue
            allowed = arguments.get(name)
            params = layer.get("params") or {}
            if allowed is not None and isinstance(params, dict):
                for key in params:
                    # a seed is accepted on a random layer even where plotnine's own list of the component does not
                    # hold it (a geom placed with position jitter, a geom with a bootstrapped summary stat), and
                    # only on a random layer (SEED-HOLDS-1, utils.random_layers)
                    if key == "random_state" and is_random_layer(name, params):
                        # PROVISIONAL (S1): a seed is a number; null, the word random and other text are refused
                        value = params[key]
                        if not is_seed_value(value):
                            self.add("PS04", f"{where}.params.{key}", f"random_state is {value!r}, but a seed is a number",
                                     "write random_state: 0 (any whole number)")
                        continue
                    if key not in allowed:
                        close = difflib.get_close_matches(str(key), sorted(allowed), n=1, cutoff=0.6)
                        self.add("PS04", f"{where}.params.{key}", f"{key} is not an argument of {name}{_plotnine_note(name, kinds)}",
                                 f"write {close[0]}" if close else "remove it")
        if needs_geom and not has_geom:
            self.add("PS03", path, "no geom or stat layer", "add a layer such as {name: geom_point}")

    def plot_defaults(self, raw: dict) -> None:
        defaults = raw.get("plot_defaults")
        if defaults is None:
            return
        if not isinstance(defaults, dict):
            self.add("PD01", "plot_defaults", "plot_defaults is a mapping", "write plot_defaults: {palette: ...}")
            return
        dead = self.spec["removed"]["plot_defaults"]
        self.unknown_keys("plot_defaults", defaults, "plot_defaults", "PD01", skip=dead)
        for key, why in dead.items():
            if key in defaults:
                self.add("PD02", f"plot_defaults.{key}",
                         f"{key} was removed from plot_defaults (REMOVED, {why['decision']}, {why['date']}): the key did nothing, and a key that does nothing is "
                         f"removed from the recipe (D-0220). {why['why']}.",
                         f"Remove the key. Rewrite tool: {self.spec['old_shapes']['tool']} removes it and prints its old value. "
                         f"Tombstone expires: {self.spec['removed']['tombstone_expires']}")
        # PROVISIONAL (S3): the one seed of the whole recipe, a whole number
        if "random_state" in defaults:
            value = defaults["random_state"]
            if not is_seed_value(value):
                self.add("PD01", "plot_defaults.random_state", f"random_state is {value!r}, but a seed is a whole number",
                         "write random_state: 0 (any whole number)")
        # D-0050: the layers of plot_defaults are judged by the same function as a plot's layers (same codes);
        # only the "needs a geom" rule does not apply, the defaults are added to every plot
        if "layers" in defaults:
            if isinstance(defaults["layers"], list):
                self.layers(defaults["layers"], "plot_defaults.layers", needs_geom=False, plot_engine=self.raw.get("plot_engine"))
            else:
                self.add("PS03", "plot_defaults.layers", "layers is a list", "write layers: [{name: theme_bw}]")

    # -- gallery profile
    def gallery(self, raw: dict) -> None:
        gallery = self.spec["gallery"]
        groups = raw.get("analysis_groups") or {}
        plots = [p for g in groups.values() if isinstance(g, dict) for p in (g.get("plots") or {}).values()] if isinstance(groups, dict) else []
        if len(groups) != 1 or len(plots) != 1:
            self.add("GP01", "analysis_groups", "a gallery example has exactly one group and one plot", "keep one group with one plot")
        if self.file_stem is not None and raw.get("id") != self.file_stem:
            self.add("GP04", "id", f"the id must equal the example's folder name {self.file_stem!r}", f"write id: {self.file_stem}")
        for plot in plots:
            taxonomy = plot.get("taxonomy") if isinstance(plot, dict) else None
            if not isinstance(taxonomy, dict):
                self.add("GP02", "taxonomy", "a gallery plot needs a taxonomy with " + ", ".join(gallery["axes"]), "add taxonomy")
                continue
            for axis in gallery["axes"]:
                if axis not in taxonomy:
                    self.add("GP02", f"taxonomy.{axis}", f"the axis {axis} is missing", f"add {axis}")
                elif taxonomy[axis] not in gallery["terms"][axis]:
                    self.add("GP03", f"taxonomy.{axis}", f"{taxonomy[axis]!r} is not a term of {axis}", "write one of " + "; ".join(gallery["terms"][axis]))
            for key in taxonomy:
                if key not in gallery["axes"]:
                    self.add("GP02", f"taxonomy.{key}", f"{key} is not an axis", "write one of " + ", ".join(gallery["axes"]))
        for sid, schema in (raw.get("data_schemas") or {}).items():
            source = schema.get("source") if isinstance(schema, dict) else None
            name = (source or {}).get("path") if isinstance(source, dict) else None
            if isinstance(name, str) and self.file_stem is not None:
                tail = name.replace("\\", "/").rstrip("/").split("/")[-1]
                if tail != "example_data.tsv" or (self.file_stem not in name and "/" in name.lstrip("./")):
                    self.add("GP06", f"data_schemas.{sid}.source.path", "the data of a gallery example is its own example_data.tsv",
                             f"write ./assets/gallery_data/{self.file_stem}/example_data.tsv")
        if self.bundle_dir is not None:
            from pathlib import Path
            for companion in gallery["companion_files"]:
                if not (Path(self.bundle_dir) / companion).exists():
                    self.add("GP05", companion, f"the companion file {companion} is missing in the example's folder", f"add {companion}")


def check_recipe_set(recipes: Dict[str, Any]) -> List[Problem]:
    """X5 across the recipes of a folder: a plot id must be unique over all of them (the app registers plots by id)."""
    owners: Dict[str, str] = {}
    problems: List[Problem] = []
    for name, raw in recipes.items():
        groups = raw.get("analysis_groups") if isinstance(raw, dict) else None
        for group in (groups or {}).values() if isinstance(groups, dict) else []:
            for pid in ((group or {}).get("plots") or {}) if isinstance(group, dict) else []:
                if pid in owners:
                    problems.append(Problem("X5", "E", f"{name}:analysis_groups.*.plots.{pid}",
                                            f"the plot id {pid!r} is also used in {owners[pid]}", "plot ids are unique over all recipes: rename one"))
                else:
                    owners[pid] = name
    return problems


def _is_column_names(value: Any) -> bool:
    """A join key: nothing, a column name, or a list of column names (text only)."""
    if value is None or isinstance(value, str):
        return True
    return isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value)


def _as_list(value: Any) -> list:
    if value is None:
        return []
    return list(value) if isinstance(value, (list, tuple)) else [value]


def check_recipe(raw: Any, profile: str = "run", *, file_stem: Optional[str] = None, catalogs: Optional[dict] = None,
                 graph: Any = None, roots: Optional[Iterable] = None, base: Any = None, bundle_dir: Any = None) -> Result:
    """Judge one recipe (a dictionary) in a profile; see the module text for the arguments and the spec for the checks."""
    if profile not in PROFILES:
        raise ValueError(f"profile {profile!r} is not one of {PROFILES}")
    return _Check(raw, profile, file_stem, catalogs, graph, roots, base, bundle_dir).run()
