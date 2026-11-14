"""
@deps
provides: function:uploaded_recipe_report, function:validate_data_analysis_recipe, function:checker_problems, function:engine_load_problems, function:checker_catalogs, function:validate_data_analysis_recipe_data, function:find_data_analysis_recipes, function:read_data_analysis_recipe_header, function:resolve_contact, class:DataAnalysisRecipeProblem
consumes: libs/utils/src/utils/config_loader.py, libs/utils/src/utils/recipe_loader.py (check_recipe_file), libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/actions/base.py (ACTION_SCHEMAS), libs/viz_factory/src/viz_factory/arguments.py (argument_catalog), app/modules/orchestrator.py
consumed_by: app/tests/test_upload_recipe_check.py, app/tests/test_data_analysis_recipe_validator.py, app/tests/test_data_analysis_recipe_data_check.py, app/tests/test_retest_data_analysis_recipes.py, app/handlers/blueprint_handlers.py (_handle_validate, BP-VALIDATE-1/VALIDATE-UI-1), app/src/bootloader.py (HOME load gate, ADR-094)
doc: .claude/tasks/tasks.md (BP-VALIDATE-1, VALIDATE-UI-1), .claude/rules/rules_data_engine.md#3, .claude/knowledge/architecture_decisions.md#ADR-094
@end_deps

Data analysis recipe validator (headless, no Shiny).

`validate_data_analysis_recipe` loads the recipe through the real engine path (ConfigManager,
SystemExit caught per ADR-094) and checks every wrangling block and assembly steps is in a shape
the engine accepts (tiered, with tier1/tier2 keys, via the same resolver the engine uses —
DataWrangler._resolve_tier), plus the id == file name rule (ADR-092). `validate_data_analysis_recipe_data`
goes further: it reads the real data and checks it against the declared contract.

Both are wired into the BLUEPRINT "Validate" action (`_handle_validate`, BP-VALIDATE-1 /
VALIDATE-UI-1 / issue #53). History, because both halves were independently "wired" and then
turned out not to be: the data-contract half was written and tested on 2026-05-xx but never
called from the running app until VALIDATE-UI-1 (2026-11-08) fixed that. This function
(`validate_data_analysis_recipe`, the structure/engine-load half) was written for HOME's load
gate (ADR-094) and this docstring then *claimed* it was also wired into Validate — it was not:
Validate only ran a separate hand-rolled static script that never touches ConfigManager, so a
recipe with `id:` != file name or a flat wrangling list could PASS Validate and still fail to
load in HOME. Actually wired in by issue #53 (2026-11-10) — found via Eve's own manual testing,
not caught by re-reading this docstring, which is exactly why it was wrong.

Lives in the app layer on purpose: only this layer may combine utils (ConfigManager) and
transformer (DataWrangler); the libraries stay isolated (ADR-011/016).

Works on any data analysis recipe path, including a temporary upload. It returns every problem found
instead of stopping at the first one, and reports a missing include as a problem.
"""
import difflib
import io
from contextlib import redirect_stderr
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Union

import polars as pl
import yaml
from transformer.data_wrangler import DataWrangler
from utils.config_loader import ConfigManager
from utils.recipe_loader import check_recipe_file

# What the recipe checker must have looked at before a recipe is accepted (its `coverage`): the form of the file, every
# step against the action registry, every plot layer against the component registry.
REQUIRED_COVERAGE = frozenset({"structure", "actions", "components"})

# Sections whose entries (dataset id -> spec) may carry a 'wrangling' block.
_SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")


@dataclass(frozen=True)
class DataAnalysisRecipeProblem:
    """One problem found in a data analysis recipe: which file, where in it, what is wrong, how to fix."""

    data_analysis_recipe: str
    location: str
    problem: str
    tip: Optional[str] = None

    def __str__(self) -> str:
        text = f"{self.data_analysis_recipe}: {self.location}: {self.problem}"
        return f"{text} Tip: {self.tip}" if self.tip else text


def find_data_analysis_recipes(directory: Union[str, Path]) -> list[Path]:
    """Return the data analysis recipe files (*.yaml) directly inside directory, sorted by name.

    Sub-folders hold the included fragments of a data analysis recipe, not data analysis recipes of their own.
    """
    return sorted(Path(directory).glob("*.yaml"))


def _step_blocks(raw: dict) -> Iterator[tuple[str, object]]:
    """Yield (location, block) for every wrangling block or assembly steps a data analysis recipe can carry."""
    if "wrangling" in raw:
        yield "wrangling", raw["wrangling"]
    for section in _SCHEMA_SECTIONS:
        entries = raw.get(section)
        if not isinstance(entries, dict):
            continue
        for ds_id, spec in entries.items():
            if isinstance(spec, dict) and "wrangling" in spec:
                yield f"{section}.{ds_id}.wrangling", spec["wrangling"]
    metadata = raw.get("metadata_schema")
    if isinstance(metadata, dict) and "wrangling" in metadata:
        yield "metadata_schema.wrangling", metadata["wrangling"]
    assemblies = raw.get("joins")
    if isinstance(assemblies, dict):
        for assembly_id, spec in assemblies.items():
            if isinstance(spec, dict) and "steps" in spec:
                yield f"joins.{assembly_id}.steps", spec["steps"]


def _load_error_text(stderr_text: str, exc: BaseException) -> str:
    """Prefer the first [FATAL] line printed by ConfigManager; fall back to the exception."""
    for line in stderr_text.splitlines():
        if line.startswith("[FATAL]"):
            return f"cannot load data analysis recipe: {line.removeprefix('[FATAL]').strip()}"
    return f"cannot load data analysis recipe (YAML or include error): {exc}"


def checker_catalogs() -> dict:
    """The registries as plain data for `check_recipe`: the actions with their form schema, the plot components with
    the arguments each accepts. Built here because only the app layer may read two libraries."""
    import transformer.actions  # noqa: F401  (loads the registry)
    from transformer.actions.base import ACTION_SCHEMAS
    from viz_factory.arguments import argument_catalog
    return {"actions": dict(ACTION_SCHEMAS), "components": argument_catalog()}


def _fragment_report(raw) -> list[str]:
    """One line per problem of the steps of a wrangling-only upload, each step against its action schema."""
    from utils.ui_schema import step_problems
    wrangling = raw.get("wrangling") if isinstance(raw, dict) else None
    if isinstance(wrangling, list):
        located = [("steps", i, s) for i, s in enumerate(wrangling)]
    elif isinstance(wrangling, dict):
        located = [(t, i, s) for t in ("tier1", "tier2", "tier3") for i, s in enumerate(wrangling.get(t) or [])]
    else:
        located = []
    if not located:
        return ["[UP01] the file has no wrangling steps and no data_schemas: nothing to import"]
    actions = checker_catalogs()["actions"]
    lines = []
    for tier, i, step in located:
        where = f"{tier}[{i}]"
        if not isinstance(step, dict) or not isinstance(step.get("action"), str):
            lines.append(f"[ST01] {where}: a step is a mapping with an action")
            continue
        name = step["action"]
        if name not in actions or not isinstance(actions[name], dict):
            lines.append(f"[ST02] {where} ({name}): {name!r} is not a registered action")
            continue
        flat = {**{k: v for k, v in step.items() if k != "params"}, **(step.get("params") or {})}
        for p in step_problems(name, flat, actions[name]):
            lines.append(f"[{p.code}] {where} ({name}): {p.message}" + (f" Fix: {p.fix}" if p.fix else ""))
    return lines


def uploaded_recipe_report(raw, profile: str = "build") -> list[str]:
    """One line per problem of an uploaded file (a dictionary), empty when it passes.

    A whole recipe (it has `data_schemas`) goes through the strict checker in the given profile; anything else is a
    wrangling fragment, whose steps are checked one by one with the same step check the checker uses (`step_problems`).
    Blueprint reports and never blocks (rules_data_analysis_recipe_structure.md 11a; profiles: recipe_format_spec.md
    DEC18, line 110), so this only returns text; the caller decides what to show."""
    from utils.recipe_check import check_recipe
    try:
        if not (isinstance(raw, dict) and "data_schemas" in raw):
            if isinstance(raw, dict) or raw is None:
                return _fragment_report(raw)
        result = check_recipe(raw, profile, catalogs=checker_catalogs())
    except Exception as exc:
        return [f"[CHECK] the recipe could not be checked: {exc}"]
    return [f"[{p.code}] {p.path + ': ' if p.path else ''}{p.message}" + (f" Fix: {p.fix}" if p.fix else "")
            for p in result.errors]


def checker_problems(path: Path, profile: str = "run") -> list[DataAnalysisRecipeProblem]:
    """The errors of the strict recipe checker (format 1) for the file, as problems of this module.

    An advice of the checker is not a problem here: it does not stop a recipe. When the checker could not look at the
    actions or the plot components, that is a problem of its own: a recipe is never accepted on a partial check."""
    result = check_recipe_file(path, profile, catalogs=checker_catalogs())
    problems = [DataAnalysisRecipeProblem(path.name, p.path or "recipe", f"[{p.code}] {p.message}", p.fix or None)
                for p in result.errors]
    missing = REQUIRED_COVERAGE - result.coverage
    if missing and not problems:
        problems.append(DataAnalysisRecipeProblem(
            path.name, "check", "the recipe check did not cover: " + ", ".join(sorted(missing)),
            "This is a fault of the app, not of the data analysis recipe: report it."))
    return problems


def validate_data_analysis_recipe(path: Union[str, Path], profile: str = "run") -> list[DataAnalysisRecipeProblem]:
    """Return all problems of the data analysis recipe at path (empty list when it is valid).

    First the strict checker of recipe format 1 (`check_recipe`: form, keys, steps against the action registry, plot
    layers against the component registry); a recipe it refuses is not handed to the engine. Then the engine's own
    load (`engine_load_problems`), which finds what only loading shows."""
    path = Path(path)
    if not path.is_file():
        return [DataAnalysisRecipeProblem(path.name, "file", f"data analysis recipe file not found: {path}")]
    return checker_problems(path, profile) or engine_load_problems(path)


def engine_load_problems(path: Union[str, Path]) -> list[DataAnalysisRecipeProblem]:
    """What only the engine's own load shows: a missing include, a step list the engine cannot resolve, an id that
    differs from the file name. The second half of `validate_data_analysis_recipe`; it never ends the program."""
    path = Path(path)
    name = path.name
    if not path.is_file():
        return [DataAnalysisRecipeProblem(name, "file", f"data analysis recipe file not found: {path}")]
    # ConfigManager ends the program (SystemExit) and prints a FATAL block to stderr on a
    # contradictory data analysis recipe (ADR-077). A validator used from the app must not do that:
    # catch it and keep the FATAL line as the problem text.
    captured = io.StringIO()
    try:
        with redirect_stderr(captured):
            raw = ConfigManager(str(path)).raw_config
    except (Exception, SystemExit) as exc:
        return [DataAnalysisRecipeProblem(name, "load", _load_error_text(captured.getvalue(), exc))]
    if not isinstance(raw, dict):
        return [DataAnalysisRecipeProblem(name, "load", "data analysis recipe root is not a mapping")]

    problems: list[DataAnalysisRecipeProblem] = []
    # The file name is the data analysis recipe id (selector, cache, sessions, export). The id: key of the
    # file is the root-key marker of a data analysis recipe and is shown in the audit panel, so it must say the same.
    file_id = raw.get("id")
    if file_id is not None and str(file_id) != path.stem:
        problems.append(DataAnalysisRecipeProblem(
            name, "id", f"id '{file_id}' differs from the file name '{path.stem}'.",
            f"Set 'id: {path.stem}', or rename the file to '{file_id}.yaml'; the file name without .yaml is the data analysis recipe id."))
    for location, block in _step_blocks(raw):
        seen: set[str] = set()
        for tier in ("tier1", "tier2"):
            try:
                DataWrangler._resolve_tier(block, tier)
            except Exception as exc:
                message = str(exc)
                # A flat list fails for both tiers with the same message: report it once.
                if message in seen:
                    continue
                seen.add(message)
                problems.append(DataAnalysisRecipeProblem(name, location, message, getattr(exc, "tip", None)))
    return problems


def _declared_columns(fields) -> list[str]:
    """Column names declared by an input_fields / output_fields block (dict form only)."""
    return list(fields) if isinstance(fields, dict) else []


def validate_data_analysis_recipe_data(path: Union[str, Path], raw_data_dir: Union[str, Path],
                           data_lookup: str = "data_analysis_recipe_paths") -> list[DataAnalysisRecipeProblem]:
    """Read every dataset of the data analysis recipe and check its declared fields against the real columns.

    Unlike validate_data_analysis_recipe this reads the data files (issue #18). For each data schema it
    builds the dataset the way the app does (input contract, tier-1 wrangling) and reports:
      - a dataset that cannot be loaded (missing file, missing input column, value that does not
        fit its type), with the engine's message and tip;
      - a wrangling step that cannot run on the declared types.
    """
    from app.modules.orchestrator import DataOrchestrator

    path = Path(path)
    name = path.name
    captured = io.StringIO()
    try:
        with redirect_stderr(captured):
            raw = ConfigManager(str(path)).raw_config
    except (Exception, SystemExit) as exc:
        return [DataAnalysisRecipeProblem(name, "load", _load_error_text(captured.getvalue(), exc))]

    orchestrator = DataOrchestrator(path.parent, Path(raw_data_dir), data_lookup=data_lookup)
    schemas: list[tuple[str, str, dict]] = []
    for section in _SCHEMA_SECTIONS:
        entries = raw.get(section)
        if isinstance(entries, dict):
            schemas += [(f"{section}.{ds_id}", ds_id, spec) for ds_id, spec in entries.items() if isinstance(spec, dict)]
    if isinstance(raw.get("metadata_schema"), dict):
        schemas.append(("metadata_schema", "metadata_schema", raw["metadata_schema"]))

    problems: list[DataAnalysisRecipeProblem] = []
    for location, ds_id, spec in schemas:
        try:
            frame = orchestrator.prepare_ingredient(ds_id, spec)
            columns = frame.collect_schema().names()
        except Exception as exc:
            problems.append(DataAnalysisRecipeProblem(name, location, f"dataset cannot be loaded: {exc}", getattr(exc, "tip", None)))
            continue
        # WHY: collect_schema() only plans the query. A step whose input type does not fit (a text step on a
        # column declared categorical) fails when the plan runs, so run it on one row (issue #71). Value
        # problems (a letter in a numeric column) are not reported here: they are checked at import (issue #11).
        try:
            frame.head(1).collect()
        except (pl.exceptions.SchemaError, pl.exceptions.ColumnNotFoundError) as exc:
            problems.append(DataAnalysisRecipeProblem(
                name, location, f"wrangling cannot run on this dataset: {exc}",
                "Compare the declared type of the column with what the wrangling step expects (a text step needs a String column, not a Categorical one)."))
        except pl.exceptions.PolarsError:
            pass
    return problems


def read_data_analysis_recipe_header(path: Union[str, Path]) -> Optional[dict]:
    """Read just the `id:`/`info:` keys of a data analysis recipe, tolerant of a broken body.

    HOME's load gate (ADR-094) rejects a data analysis recipe whose structure or data fails
    validation — but the rejection message still needs to show *who to contact*, and the
    `info.contact` convention (data_analysis_recipe_info.py) lives in the same file as the
    broken part. A plain `yaml.safe_load` (no `!include` resolution, no ConfigManager, no
    engine involvement) reads what it can; a YAML file broken badly enough that even this
    fails returns None rather than raising — the caller falls back to the deployment contact.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None
    return {"id": raw.get("id"), "info": raw.get("info") if isinstance(raw.get("info"), dict) else {}}


def resolve_contact(info: Optional[dict], deployment_contact: Optional[str]) -> Optional[str]:
    """Two-tier contact resolution (ADR-094): the data analysis recipe's own `info.contact`,
    else the deployment's own contact, else None (never a fabricated placeholder)."""
    if info:
        recipe_contact = info.get("contact")
        if recipe_contact:
            return str(recipe_contact)
    return deployment_contact or None
