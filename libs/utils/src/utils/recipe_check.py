"""`check_recipe`: the one function that judges a recipe in format version 1 (spec sections 3 to 11).

Pure: it reads the recipe (a dictionary) and the data of the specification file `recipe_spec.yaml`, and never the data
files, the registries or the disk. What it cannot know it is given:
- `catalogs`: the registries as plain data (`actions`: name -> ui_schema, `components`: name -> allowed argument names or
  None for free-form, `themes`: a set of names). Without them the checks of actions and components are not run, and
  `coverage` says so;
- `graph`: an object with `columns_of(dataset_id)` (the columns of a table after its tier 1), for the checks of columns
  per node (J08, X7); without it they are not run;
- `roots` and `base`: the folders a development path may lie in, and the folder its path is relative to, the project
  root (PA02); `bundle_dir`: the folder of a gallery example, for its companion files (GP05).
The caller reads `result.coverage` and asserts it when it must have every check (HOME's load gate does).

Every problem has a permanent code (the catalogue of spec section 11), a severity (E error, A advice), a path in the
recipe, what is wrong and the fix, in the message style of spec P5.

# @deps
# provides: function:check_recipe, function:spec, class:Problem, class:Result
# consumes: libs/utils/src/utils/recipe_spec.yaml, libs/utils/src/utils/ui_schema.py, libs/utils/src/utils/formula_check.py, libs/utils/src/utils/recipe_paths.py, libs/utils/src/utils/polars_types.py
# consumed_by: libs/utils/tests/test_recipe_check.py
# doc: .claude/design/recipe_format_spec.md (sections 3 to 11, 14)
# @end_deps
"""
import difflib
import re
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from typing import Any, Dict, Iterable, List, Optional, Set

import yaml

from utils.action_names import TIER1_ONLY
from utils.formula_check import formula_problems
from utils.polars_types import PARAMETER_KEYS, text_dtype_names
from utils.recipe_paths import containment_problems, shape_problems
from utils.ui_schema import STEP_KEYS, step_problems

# P05: the engine does not read `steps.tier3` yet; switched to True in the commit that adds the reader (spec 7.7).
TIER3_READ_BY_ENGINE = False

PROFILES = ("run", "build", "gallery", "audit")
_AUDIT_ID = re.compile(r"^audit_[0-9a-f]{8}_\d+$")
_SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
_TIER1_ONLY_DEFAULT = TIER1_ONLY


@lru_cache(maxsize=1)
def spec() -> dict:
    """The recipe format as data (the packaged file `recipe_spec.yaml`)."""
    return yaml.safe_load(resources.files("utils").joinpath("recipe_spec.yaml").read_text(encoding="utf-8"))


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
        body = f"{self.message}. Fix: {self.fix}" if self.fix else self.message
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

    # -- helpers
    def add(self, code: str, path: str, message: str, fix: str = "", severity: str = "E") -> None:
        self.result.problems.append(Problem(code, severity, path, message, fix))

    def unknown_keys(self, element: str, mapping: dict, path: str, code: str) -> None:
        wanted = self.spec["elements"][element]
        known = set(wanted["required"]) | set(wanted["optional"])
        renamed = self.spec["renamed"].get(element, {})
        for key in mapping:
            if key in known:
                continue
            if key in renamed:
                self.add(code, f"{path}.{key}" if path else str(key), f"{key} is not a key of this element", f"{renamed[key]}")
            else:
                close = difflib.get_close_matches(str(key), list(known), n=1, cutoff=0.6)
                fix = f"write {close[0]}" if close else "remove it, or write one of " + ", ".join(sorted(known))
                self.add(code, f"{path}.{key}" if path else str(key), f"{key} is not a key of this element", fix)

    def required_keys(self, element: str, mapping: dict, path: str, code: str) -> None:
        for key in self.spec["elements"][element]["required"]:
            if key not in mapping:
                self.add(code, path, f"{key} is required", f"add {key}")

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
        for key, allowed in self.spec["engines"].items():
            if key in raw and raw[key] not in allowed:
                self.add("T06", key, f"{raw[key]!r} is not a built {key}", "write one of " + ", ".join(allowed))

    def info(self, info: Any) -> None:
        if info is None:
            return
        if not isinstance(info, dict):
            self.add("I01", "info", "info is not a mapping", "write info: {label: ...}")
            return
        if "display_name" in info:
            self.add("I03", "info.display_name", "display_name was renamed", self.spec["renamed"]["info"]["display_name"])
        if not info.get("label"):
            self.add("I01", "info", "info.label is required", "add label")
        if "comment" in info and not isinstance(info["comment"], str):
            self.add("CM01", "info.comment", "a comment is text", "write text")
        for key in ("description", "contact"):
            if not info.get(key):
                self.add("I02", f"info.{key}", f"info.{key} is missing", "write it (spec section 13)", "A")

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

    def plot_targets(self, raw: dict) -> Set[str]:
        targets = set()
        for group in (raw.get("analysis_groups") or {}).values():
            for plot in ((group or {}).get("plots") or {}).values() if isinstance(group, dict) else []:
                if isinstance(plot, dict) and isinstance(plot.get("spec"), dict):
                    targets.add(plot["spec"].get("target_dataset"))
        return targets

    def schemas(self, raw: dict) -> None:
        seen: Dict[str, str] = {}
        targets = self.plot_targets(raw)
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
                self.schema(schema, path, sid in targets)
        if "metadata_schema" in raw:
            self.schema_ids.add("metadata_schema")
            self.schema(raw["metadata_schema"], "metadata_schema", "metadata_schema" in targets)

    def schema(self, schema: Any, path: str, is_target: bool) -> None:
        if not isinstance(schema, dict):
            self.add("S01", path, "a schema is a mapping", "write label, source, null_values, strip, input_fields, wrangling")
            return
        self.unknown_keys("schema", schema, path, "S01")
        if "label" not in schema:
            self.add("S03", path, "the schema has no label", "add label")
        if not schema.get("description"):
            self.add("S04", f"{path}.description", "the schema has no description", "write the grain: what one row is (spec section 13)", "A")
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
        wrangling = schema.get("wrangling")
        if wrangling is None:
            self.add("S06", f"{path}.wrangling", "wrangling is required", "write wrangling: {tier1: []}")
        else:
            self.step_container(wrangling, f"{path}.wrangling", "S06", self.spec["elements"]["tiers"]["schema"])
            if isinstance(wrangling, dict) and wrangling.get("tier2") and not is_target:
                self.add("S07", f"{path}.wrangling.tier2", "tier2 of a schema applies only when the schema is plotted directly",
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
        known = set(wanted["required"]) | set(wanted["optional"])
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
            fix = f"write {old}" if old else "write one of " + ", ".join(text_dtype_names())
            self.add("FD02", f"{path}.type", f"{type_!r} is not a Polars dtype that a text file can hold", fix)
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
    def step_container(self, container: Any, path: str, code: str, tiers: Iterable[str]) -> None:
        tiers = list(tiers)
        if not isinstance(container, dict):
            self.add(code, path, "the steps are written as {tier1: [...]}, not a list or a text",
                     "write {tier1: [...]}" if tiers[0] == "tier1" else "write {tier3: [...]}")
            return
        for key in container:
            if key not in tiers:
                self.add(code, f"{path}.{key}", f"{key} is not a tier here", "write one of " + ", ".join(tiers))
        if "tier1" in tiers and "tier1" not in container:
            self.add(code, path, "tier1 is required", "add tier1: []")
        for tier in tiers:
            steps = container.get(tier)
            if steps is None:
                continue
            if not isinstance(steps, list):
                self.add(code, f"{path}.{tier}", f"{tier} is a list of steps", f"write {tier}: [...]")
                continue
            self.steps(steps, f"{path}.{tier}", tier)

    def steps(self, steps: list, path: str, tier: str) -> None:
        actions = (self.catalogs or {}).get("actions")
        tier1_only = (self.catalogs or {}).get("tier1_only", _TIER1_ONLY_DEFAULT)
        audit_ids: Set[str] = set()
        for index, step in enumerate(steps, start=1):
            where = f"{path}[{index}]"
            if not isinstance(step, dict) or "action" not in step:
                self.add("ST01", where, "a step is a mapping with an action", "write - {action: <name>, ...}")
                continue
            if "id" in step:
                if self.profile != "audit":
                    self.add("ST08", f"{where}.id", "authors write no step id (the app writes it)", "remove id")
                elif not isinstance(step["id"], str) or not _AUDIT_ID.match(step["id"]):
                    self.add("ST08", f"{where}.id", f"{step['id']!r} is not an audit id", "write audit_<8 hex>_<k>")
                elif step["id"] in audit_ids:
                    self.add("ST08", f"{where}.id", f"the id {step['id']} is used twice", "ids are unique in a list")
                else:
                    audit_ids.add(step["id"])
            if "comment" in step and not isinstance(step["comment"], str):
                self.add("CM01", f"{where}.comment", "a comment is text", "write text")
            if tier in ("tier2", "tier3") and step.get("action") in tier1_only:
                self.add("ST05", where, f"{step['action']} is only allowed in tier1", "move it to tier1")
            if actions is None:
                continue
            name = step["action"]
            if name not in actions:
                legacy = (self.catalogs or {}).get("old_action_names", {}).get(name)
                close = difflib.get_close_matches(str(name), list(actions), n=1, cutoff=0.6)
                fix = f"write {legacy}" if legacy else f"write {close[0]}" if close else "choose a registered action"
                self.add("ST02", f"{where}.action", f"{name!r} is not a registered action", fix)
                continue
            schema = actions[name]
            if not isinstance(schema, dict):
                continue
            for problem in step_problems(name, step, schema):
                self.add(problem.code, f"{where}.{problem.param}" if problem.param else where, problem.message, problem.fix)
            self.formulas(step, schema, where)

    def formulas(self, step: dict, schema: dict, where: str) -> None:
        for name, definition in schema.get("params", {}).items():
            value = step.get(name)
            if value is None:
                continue
            if definition.get("widget") == "expression" and isinstance(value, str):
                values = [value]
            elif definition.get("widget") == "mapping" and definition.get("value_widget") == "expression" and isinstance(value, dict):
                values = [v for v in value.values() if isinstance(v, str)]
            else:
                continue
            for text in values:
                for message in formula_problems(text):
                    what, _, fix = message.partition(". Fix: ")
                    self.add("ST06", f"{where}.{name}", what, fix)

    # -- joins
    def joins(self, raw: dict) -> None:
        joins = raw.get("joins")
        if joins is None:
            return
        if not isinstance(joins, dict):
            self.add("J01", "joins", "joins is a mapping of id to join", "write join id: {...}")
            return
        for jid, join in joins.items():
            path = f"joins.{jid}"
            self.join_ids.add(jid)
            if jid in self.schema_ids:
                self.add("X1", path, f"the id {jid!r} is also a schema", "a plot's target must name one thing: rename one")
            if not isinstance(join, dict):
                self.add("J01", path, "a join is a mapping", "write label, ingredients, steps")
                continue
            self.unknown_keys("join", join, path, "J01")
            if "label" not in join:
                self.add("J02", path, "the join has no label", "add label")
            if not join.get("description"):
                self.add("J03", f"{path}.description", "the join has no description", "write the grain and the join type (spec section 13)", "A")
            if "comment" in join and not isinstance(join["comment"], str):
                self.add("CM01", f"{path}.comment", "a comment is text", "write text")
            ingredient_ids = self.ingredients(join.get("ingredients"), f"{path}.ingredients")
            if "steps" not in join:
                self.add("J07", f"{path}.steps", "steps is required", "write steps: {tier1: [...]}")
            else:
                self.step_container(join["steps"], f"{path}.steps", "J07", self.spec["elements"]["tiers"]["join"])
                self.join_steps(join["steps"], path, ingredient_ids)
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
            if dataset not in self.schema_ids:
                self.add("J04", f"{path}[{index}]", f"{dataset!r} is not a schema of this recipe", "name a schema")
            elif dataset in ids:
                self.add("J04", f"{path}[{index}]", f"{dataset!r} appears twice", "list each ingredient once")
            ids.append(dataset)
        return ids

    def join_steps(self, steps: Any, path: str, ingredient_ids: List[str]) -> None:
        if not isinstance(steps, dict):
            return
        for tier in ("tier1", "tier2"):
            for index, step in enumerate(steps.get(tier) or [], start=1):
                if not isinstance(step, dict) or "right_ingredient" not in step:
                    continue
                where = f"{path}.steps.{tier}[{index}]"
                if step["right_ingredient"] not in ingredient_ids:
                    self.add("J05", where, f"right_ingredient {step['right_ingredient']!r} is not an ingredient of this join", "list it in ingredients")
                if ("on" in step or True in step) == ("left_on" in step or "right_on" in step):
                    self.add("J05", where, "write either on, or left_on with right_on", "choose one form")
                if True in step:
                    self.add("T07", where, "an unquoted on became the key true", "quote it: 'on'")

    def join_columns(self, join: dict, path: str, ingredient_ids: List[str]) -> None:
        """J08 needs the recipe graph: a column in both ingredients that is not a join key is renamed silently by Polars."""
        if self.graph is None or len(ingredient_ids) < 2:
            return
        steps = (join.get("steps") or {}).get("tier1") if isinstance(join.get("steps"), dict) else None
        if not isinstance(steps, list):
            return
        base_columns = self.graph.columns_of(ingredient_ids[0])
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict) or "right_ingredient" not in step:
                continue
            right = self.graph.columns_of(step["right_ingredient"])
            if base_columns is None or right is None:
                continue
            keys = set(_as_list(step.get("on", step.get(True)))) | set(_as_list(step.get("left_on"))) | set(_as_list(step.get("right_on")))
            clash = sorted((set(base_columns) & set(right)) - keys)
            if clash:
                self.add("J08", f"{path}.steps.tier1[{index}]",
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
            if "label" not in group:
                self.add("G01", path, "the group has no label (the tab text)", "add label")
            if not group.get("description"):
                self.add("G02", f"{path}.description", "the group has no description", "write the question its plots answer", "A")
            if "comment" in group and not isinstance(group["comment"], str):
                self.add("CM01", f"{path}.comment", "a comment is text", "write text")
            plots = group.get("plots")
            if not isinstance(plots, dict):
                self.add("G01", f"{path}.plots", "plots is a mapping of id to plot", "write plot id: {label, spec}")
                continue
            for pid, plot in plots.items():
                plots_found += 1
                self.plot(plot, f"{path}.plots.{pid}", pid)
        if self.profile in ("run", "gallery", "audit") and plots_found == 0:
            self.add("T09", "analysis_groups", "profile run needs at least one group with one plot", "add a group with a plot")

    def plot(self, plot: Any, path: str, pid: str) -> None:
        if not isinstance(pid, str) or not _SNAKE.match(pid):
            self.add("P03", path, f"the plot id {pid!r} is not snake_case", "use lowercase letters, digits and underscores")
        if not isinstance(plot, dict):
            self.add("P01", path, "a plot is a mapping", "write label and spec")
            return
        self.unknown_keys("plot", plot, path, "P01")
        for key in ("label", "spec"):
            if key not in plot:
                self.add("P01", path, f"{key} is required", f"add {key}")
        if not plot.get("description"):
            self.add("P02", f"{path}.description", "the plot has no description", "write what is drawn and counted (spec section 13)", "A")
        if "comment" in plot and not isinstance(plot["comment"], str):
            self.add("CM01", f"{path}.comment", "a comment is text", "write text")
        if "steps" in plot:
            steps = plot["steps"]
            if not isinstance(steps, dict) or set(steps) - {"tier3"}:
                self.add("P04", f"{path}.steps", "steps at the plot entry holds only tier3", "write steps: {tier3: [...]}")
            else:
                self.step_container(steps, f"{path}.steps", "P04", self.spec["elements"]["tiers"]["plot"])
                if steps.get("tier3") and not TIER3_READ_BY_ENGINE:
                    self.add("P05", f"{path}.steps.tier3", "the engine does not read steps.tier3 yet, so these steps would never be applied",
                             "leave tier3 empty until the engine reads it")
        if isinstance(plot.get("spec"), dict):
            self.plot_spec(plot["spec"], f"{path}.spec")
        elif "spec" in plot:
            self.add("PS01", f"{path}.spec", "spec is a mapping", "write target_dataset, mapping, layers")
        if "taxonomy" in plot and not isinstance(plot["taxonomy"], dict):
            self.add("P01", f"{path}.taxonomy", "taxonomy is a mapping of axis to term", "write taxonomy: {family: ..., ...}")

    def plot_spec(self, spec_: dict, path: str) -> None:
        self.unknown_keys("spec", spec_, path, "PS01")
        target = spec_.get("target_dataset")
        if not target or (target not in self.schema_ids and target not in self.join_ids):
            self.add("PS02", f"{path}.target_dataset", f"target_dataset {target!r} is not a schema or a join of this recipe", "name one")
        if "mapping" not in spec_ or "layers" not in spec_:
            self.add("PS03", path, "mapping and layers are required", "add mapping and layers")
        layers = spec_.get("layers")
        if isinstance(layers, list):
            self.layers(layers, f"{path}.layers")
        elif "layers" in spec_:
            self.add("PS03", f"{path}.layers", "layers is a list", "write layers: [{name: geom_point}]")
        theme = spec_.get("theme")
        themes = (self.catalogs or {}).get("themes")
        if theme is not None and themes is not None and theme not in themes:
            self.add("PS05", f"{path}.theme", f"{theme!r} is not a registered theme", "write one of " + ", ".join(sorted(themes)))
        if "filters" in spec_ and TIER3_READ_BY_ENGINE:
            self.add("P06", f"{path}.filters", "filters in a plot spec moved to the plot's steps", "write the filters as steps.tier3")

    def layers(self, layers: list, path: str) -> None:
        components = (self.catalogs or {}).get("components")
        arguments = (self.catalogs or {}).get("component_arguments", {})
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
            has_geom = has_geom or (isinstance(name, str) and name.startswith(("geom_", "stat_")))
            if components is None:
                continue
            if name not in components:
                close = difflib.get_close_matches(str(name), list(components), n=1, cutoff=0.6)
                self.add("PS04", f"{where}.name", f"{name!r} is not a registered plot component", f"write {close[0]}" if close else "choose a registered component")
                continue
            allowed = arguments.get(name)
            params = layer.get("params") or {}
            if allowed is not None and isinstance(params, dict):
                for key in params:
                    if key not in allowed:
                        close = difflib.get_close_matches(str(key), sorted(allowed), n=1, cutoff=0.6)
                        self.add("PS04", f"{where}.params.{key}", f"{key} is not an argument of {name}", f"write {close[0]}" if close else "remove it")
        if not has_geom:
            self.add("PS03", path, "no geom or stat layer", "add a layer such as {name: geom_point}")

    def plot_defaults(self, raw: dict) -> None:
        defaults = raw.get("plot_defaults")
        if defaults is None:
            return
        if not isinstance(defaults, dict):
            self.add("PD01", "plot_defaults", "plot_defaults is a mapping", "write plot_defaults: {palette: ...}")
            return
        self.unknown_keys("plot_defaults", defaults, "plot_defaults", "PD01")

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
