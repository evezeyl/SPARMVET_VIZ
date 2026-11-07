"""
@deps
provides: function:validate_data_analysis_recipe, function:validate_data_analysis_recipe_data, function:find_data_analysis_recipes, class:DataAnalysisRecipeProblem
consumes: libs/utils/src/utils/config_loader.py, libs/transformer/src/transformer/data_wrangler.py
consumed_by: app/tests/test_data_analysis_recipe_validator.py, app/tests/test_data_analysis_recipe_data_check.py
doc: .claude/tasks/tasks.md (BP-VALIDATE-1), .claude/rules/rules_data_engine.md#3
@end_deps

Data analysis recipe validator (headless, no Shiny).

Checks that every wrangling block and every assembly steps of a data analysis recipe is in a shape the
engine accepts (tiered, with tier1/tier2 keys), by running the same resolver the engine uses
(DataWrangler._resolve_tier). One rule, shared by the contract test, the weekly audit and,
later, the BLUEPRINT "Validate data analysis recipe" action (BP-VALIDATE-1).

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
