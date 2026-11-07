"""
@deps
provides: function:validate_manifest, function:validate_manifest_data, function:find_manifests, class:ManifestProblem
consumes: libs/utils/src/utils/config_loader.py, libs/transformer/src/transformer/data_wrangler.py
consumed_by: app/tests/test_manifest_validator.py, app/tests/test_manifest_data_check.py
doc: .claude/tasks/tasks.md (BP-VALIDATE-1), .claude/rules/rules_data_engine.md#3
@end_deps

Manifest recipe validator (headless, no Shiny).

Checks that every wrangling block and every assembly recipe of a manifest is in a shape the
engine accepts (tiered, with tier1/tier2 keys), by running the same resolver the engine uses
(DataWrangler._resolve_tier). One rule, shared by the contract test, the weekly audit and,
later, the BLUEPRINT "Validate manifest" action (BP-VALIDATE-1).

Lives in the app layer on purpose: only this layer may combine utils (ConfigManager) and
transformer (DataWrangler); the libraries stay isolated (ADR-011/016).

Works on any manifest path, including a temporary upload. It returns every problem found
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
class ManifestProblem:
    """One problem found in a manifest: which file, where in it, what is wrong, how to fix."""

    manifest: str
    location: str
    problem: str
    tip: Optional[str] = None

    def __str__(self) -> str:
        text = f"{self.manifest}: {self.location}: {self.problem}"
        return f"{text} Tip: {self.tip}" if self.tip else text


def find_manifests(directory: Union[str, Path]) -> list[Path]:
    """Return the manifest files (*.yaml) directly inside directory, sorted by name.

    Sub-folders hold the included fragments of a manifest, not manifests of their own.
    """
    return sorted(Path(directory).glob("*.yaml"))


def _recipe_blocks(raw: dict) -> Iterator[tuple[str, object]]:
    """Yield (location, block) for every wrangling block or assembly recipe a manifest can carry."""
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
    assemblies = raw.get("join_manifests")
    if isinstance(assemblies, dict):
        for assembly_id, spec in assemblies.items():
            if isinstance(spec, dict) and "recipe" in spec:
                yield f"join_manifests.{assembly_id}.recipe", spec["recipe"]


def _load_error_text(stderr_text: str, exc: BaseException) -> str:
    """Prefer the first [FATAL] line printed by ConfigManager; fall back to the exception."""
    for line in stderr_text.splitlines():
        if line.startswith("[FATAL]"):
            return f"cannot load manifest: {line.removeprefix('[FATAL]').strip()}"
    return f"cannot load manifest (YAML or include error): {exc}"


def validate_manifest(path: Union[str, Path]) -> list[ManifestProblem]:
    """Return all recipe problems of the manifest at path (empty list when it is valid)."""
    path = Path(path)
    name = path.name
    if not path.is_file():
        return [ManifestProblem(name, "file", f"manifest file not found: {path}")]

    # ConfigManager ends the program (SystemExit) and prints a FATAL block to stderr on a
    # contradictory manifest (ADR-077). A validator used from the app must not do that:
    # catch it and keep the FATAL line as the problem text.
    captured = io.StringIO()
    try:
        with redirect_stderr(captured):
            raw = ConfigManager(str(path)).raw_config
    except (Exception, SystemExit) as exc:
        return [ManifestProblem(name, "load", _load_error_text(captured.getvalue(), exc))]
    if not isinstance(raw, dict):
        return [ManifestProblem(name, "load", "manifest root is not a mapping")]

    problems: list[ManifestProblem] = []
    for location, block in _recipe_blocks(raw):
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
                problems.append(ManifestProblem(name, location, message, getattr(exc, "tip", None)))
    return problems


def _declared_columns(fields) -> list[str]:
    """Column names declared by an input_fields / output_fields block (dict form only)."""
    return list(fields) if isinstance(fields, dict) else []


def validate_manifest_data(path: Union[str, Path], raw_data_dir: Union[str, Path],
                           data_lookup: str = "manifest_paths") -> list[ManifestProblem]:
    """Read every dataset of the manifest and check its declared fields against the real columns.

    Unlike validate_manifest this reads the data files (issue #18). For each data schema it
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
        return [ManifestProblem(name, "load", _load_error_text(captured.getvalue(), exc))]

    orchestrator = DataOrchestrator(path.parent, Path(raw_data_dir), data_lookup=data_lookup)
    schemas: list[tuple[str, str, dict]] = []
    for section in _SCHEMA_SECTIONS:
        entries = raw.get(section)
        if isinstance(entries, dict):
            schemas += [(f"{section}.{ds_id}", ds_id, spec) for ds_id, spec in entries.items() if isinstance(spec, dict)]
    if isinstance(raw.get("metadata_schema"), dict):
        schemas.append(("metadata_schema", "metadata_schema", raw["metadata_schema"]))

    problems: list[ManifestProblem] = []
    for location, ds_id, spec in schemas:
        try:
            columns = orchestrator.prepare_ingredient(ds_id, spec).collect_schema().names()
        except Exception as exc:
            problems.append(ManifestProblem(name, location, f"dataset cannot be loaded: {exc}", getattr(exc, "tip", None)))
            continue
        for slug in _declared_columns(spec.get("output_fields")):
            if slug in columns:
                continue
            close = difflib.get_close_matches(slug, columns, n=1, cutoff=0.6)
            tip = f"Did you mean '{close[0]}'?" if close else "Use a column the dataset has after tier-1 wrangling."
            problems.append(ManifestProblem(
                name, f"{location}.output_fields.{slug}", f"declared column '{slug}' matches no column of the dataset", tip))
    return problems
