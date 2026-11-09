"""
@deps
provides: function:validate_data_analysis_recipe, function:validate_data_analysis_recipe_data, function:find_data_analysis_recipes, function:read_data_analysis_recipe_header, function:resolve_contact, class:DataAnalysisRecipeProblem
consumes: libs/utils/src/utils/config_loader.py, libs/transformer/src/transformer/data_wrangler.py, app/modules/orchestrator.py
consumed_by: app/tests/test_data_analysis_recipe_validator.py, app/tests/test_data_analysis_recipe_data_check.py, app/tests/test_retest_data_analysis_recipes.py, app/handlers/blueprint_handlers.py (_handle_validate, BP-VALIDATE-1/VALIDATE-UI-1), app/src/bootloader.py (HOME load gate, ADR-094)
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

import yaml
from transformer.data_wrangler import DataWrangler
from utils.config_loader import ConfigManager

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


def validate_data_analysis_recipe(path: Union[str, Path]) -> list[DataAnalysisRecipeProblem]:
    """Return all step list problems of the data analysis recipe at path (empty list when it is valid)."""
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
      - an output_fields entry that matches no column of the finished dataset, with the closest
        real column as a hint. The engine never applies output_fields of a data schema, so
        without this check a wrong name stays silent.
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
            columns = orchestrator.prepare_ingredient(ds_id, spec).collect_schema().names()
        except Exception as exc:
            problems.append(DataAnalysisRecipeProblem(name, location, f"dataset cannot be loaded: {exc}", getattr(exc, "tip", None)))
            continue
        for slug in _declared_columns(spec.get("output_fields")):
            if slug in columns:
                continue
            close = difflib.get_close_matches(slug, columns, n=1, cutoff=0.6)
            tip = f"Did you mean '{close[0]}'?" if close else "Use a column the dataset has after tier-1 wrangling."
            problems.append(DataAnalysisRecipeProblem(
                name, f"{location}.output_fields.{slug}", f"declared column '{slug}' matches no column of the dataset", tip))
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
