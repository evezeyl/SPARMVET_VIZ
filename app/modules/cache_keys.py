"""
@deps
provides: function:load_data_analysis_recipe, function:tier1_material, function:tier1_engines, function:tier2_engine, function:collection_tier2_key, function:tier2_steps (from utils.recipe_tiers), function:tier1_key, function:tier2_key, constant:ENGINE_CACHE_VERSION, constant:CACHE_VERSION_META, constant:STORED_TABLES_REBUILT_NOTICE, function:data_analysis_recipe_fileset_hash, function:data_analysis_recipe_keys, class:LoadedDataAnalysisRecipe, class:DataAnalysisRecipeKeys
consumes: libs/utils/src/utils/config_loader.py, libs/utils/src/utils/recipe_tiers.py, libs/utils/src/utils/engines.py (tier_engine: the one reading of the engine of a tier)
consumed_by: app/modules/orchestrator.py, app/modules/session_manager.py, app/src/server.py, app/src/bootloader.py, app/handlers/export_handlers.py, app/tests/test_cache_keys.py, app/tests/test_engine_keys.py
doc: .claude/knowledge/architecture_decisions.md#adr-089, docs/foundations/reproducibility_hash_schema.qmd
@end_deps

Cache chain keys (ADR-089), headless, no Shiny.

Every stored stage has a key made from its own inputs and the key of the stage before it:

    tier1_key = hash(engine version, resolved recipe minus downstream-only parts and minus the written engines, data_batch_hash,
                     the effective tier-1 data engine of every table and join)
    tier2_key = hash(tier1_key, the collection's tier2 steps: a join's, or a schema plotted directly,
                     the effective tier-2 data engine of that collection)

so a change anywhere upstream reaches every stage after it, and nothing is missed.

The engine rule (D-0240): a key holds the engine of what it stores, and nothing else. The ENGINE of a tier is its own
`data_engine`, else the recipe's (`utils.engines.tier_engine`, the value the orchestrator runs). It is an argument of the key
function, not a part of the recipe text, so the same engine written on the tier or inherited gives the same key, and no text
change can forget it. A later stage's engine never moves an earlier key. The PLOT engine is in no table key: it is
downstream (the plots), a picture has no stored key.

Known limit, not changed here: the tier-1 key is ONE key per recipe (ADR-089 as built), so the engine of one table moves the key
that the other tables are stored under too. A key per table is ADR-101, not built.

Fail-safe rule: the Tier 1 material is the resolved data analysis recipe WITHOUT a short list of known
downstream parts. A new or unknown section is therefore part of Tier 1 automatically, so a
wrong guess can only cause an extra rebuild, never a stale result.

Two data analysis recipe hashes, two purposes:
  - data_analysis_recipe_sha256 (provenance, session key, export): hash of the FILE SET (entry file and
    every included file). Independently verifiable with sha256sum.
  - the cache keys use the RESOLVED content, so comments, spacing and how the data analysis recipe is
    split into files do not force a rebuild.

The loaded data analysis recipe is kept in memory and revalidated against the content of its files.
"""
import contextlib
import hashlib
import io
import json
import os
import threading
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable, Union

from utils.errors import RecipeLoadError
from utils.config_loader import ConfigManager
from utils.engines import tier_engine
# The one reading of a collection's tier-2 list (issue #77); `tier2_steps` is used from here by the app.
from utils.recipe_tiers import (  # noqa: F401 - tier2_steps is part of this module's interface
    collection_bodies, collection_body, tier2_steps, without_data_engines, without_tier2)

# Bump when an action's behaviour or these key rules change: it invalidates every stored stage.
ENGINE_CACHE_VERSION = "5"   # 5: the engine of a tier is an argument of the key of that tier, the plot engine is in no table key (D-0240); 4: recipe format 1 (the published columns are a polars_select step, no final_contract; new actions and ingestion); 3: the key order of final_contract (issue #86); 2: deterministic row order (ADR-090)

# Top-level data analysis recipe sections that only matter after Tier 2 (the plots). Everything else,
# including sections this code has never heard of, belongs to Tier 1 (fail-safe rule). The recipe's `plot_engine` is one of
# them: it draws, it builds no table (D-0240); the `plot_engine` of a plot entry is inside `analysis_groups`.
_DOWNSTREAM_TOP_LEVEL = ("info", "analysis_groups", "plot_defaults", "plots", "plot_engine")

# Parquet metadata key holding the cache version that wrote a stored table: the start of the app removes every stored table that
# does not carry the current one (`transformer.anchor.remove_tables_of_other_version`). The version is also in the key, so a table
# of another version is never served; the mark lets the sweep find such a table without knowing its recipe (D-0240).
CACHE_VERSION_META = "sparmvet_cache_version"

# The one sentence for the user when stored tables of another cache version were removed at the start of the app.
# PROVISIONAL: the wording is the review session's proposal (ledger D-0240), NOT approved by Eve.
STORED_TABLES_REBUILT_NOTICE = ("The tables of your recipes are rebuilt once because the app changed how it names what it stored. "
                                "Your results do not change.")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_hash(obj: Any) -> str:
    """SHA256 of a JSON form with sorted keys: independent of key order and YAML formatting."""
    return hash_text(json.dumps(obj, sort_keys=True, default=str, separators=(",", ":")))


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "unknown"


def engine_fingerprint() -> str:
    """The code that produces the data: cache version constant plus the installed engine versions."""
    return f"{ENGINE_CACHE_VERSION}|polars={_package_version('polars')}|transformer={_package_version('transformer')}"


# ---------------------------------------------------------------------------
# Which parts of the resolved data analysis recipe belong to which stage
# ---------------------------------------------------------------------------


def tier1_material(raw: dict) -> dict:
    """The resolved data analysis recipe without the downstream-only parts (fail-safe: unknown parts stay in).

    The tier-2 list of every collection (a join's `tier2.steps`, a schema's `tier2.steps`) is downstream of
    Tier 1: it goes into the chained `tier2_key` instead (`utils.recipe_tiers`, issue #77). The written data engines are
    left out too: their effect on Tier 1 is `tier1_engines`, an argument of `tier1_key` (D-0240)."""
    return without_data_engines(without_tier2({k: v for k, v in raw.items() if k not in _DOWNSTREAM_TOP_LEVEL}))


def tier1_engines(raw: dict) -> dict:
    """{id of every table and join: the effective data engine of its tier 1}, the value `DataOrchestrator` runs it with.

    The tier's own `data_engine`, else the recipe's (`utils.engines.tier_engine`). None for a block that has no engine at all
    (the checker refuses such a recipe, T04; the key never invents a default engine)."""
    return {cid: tier_engine(raw, body, "tier1") for cid, body in collection_bodies(raw).items()}


def tier2_engine(raw: dict, collection_id: str):
    """The effective data engine of the tier 2 of one collection: its own `data_engine`, else the recipe's."""
    return tier_engine(raw, collection_body(raw, collection_id), "tier2")


# ---------------------------------------------------------------------------
# Keys
# ---------------------------------------------------------------------------


def tier1_key(material_hash: str, data_batch_hash: str, engines: dict) -> str:
    """The key of the Tier 1 tables. `engines` is `tier1_engines(raw)`: required, so that no caller can forget it (D-0240)."""
    return hash_text("\n".join(["tier1", engine_fingerprint(), material_hash, data_batch_hash, canonical_hash(engines)]))


def tier2_key(tier1_key_value: str, steps: list, engine) -> str:
    """The key of a Tier 2 table: the Tier 1 key it is computed from, its steps, and the data engine that runs them (D-0240)."""
    return hash_text("\n".join(["tier2", tier1_key_value, canonical_hash(steps), canonical_hash(engine)]))


def collection_tier2_key(raw: dict, collection_id: str, tier1_key_value: str) -> str:
    """The Tier 2 key of one collection under the Tier 1 key given; an empty string when it has no tier-2 steps (T2 equals T1,
    nothing is stored). The one place that makes a tier-2 key from a recipe, for the orchestrator and the export record."""
    steps = tier2_steps(raw, collection_id)
    return tier2_key(tier1_key_value, steps, tier2_engine(raw, collection_id)) if steps else ""


def data_analysis_recipe_fileset_hash(files: Iterable[Union[str, Path]], base_dir: Union[str, Path]) -> str:
    """Hash of the data analysis recipe file set: `relative_path:sha256` lines, sorted, joined, hashed again."""
    base = os.path.abspath(str(base_dir))
    lines = []
    for f in files:
        absolute = os.path.abspath(str(f))
        try:
            digest = hashlib.sha256(Path(absolute).read_bytes()).hexdigest()
        except OSError:
            digest = "MISSING"
        lines.append(f"{os.path.relpath(absolute, base)}:{digest}")
    return hash_text("\n".join(sorted(lines)))


def files_signature(files: Iterable[Union[str, Path]]) -> tuple:
    """(path, content digest) per file, to see whether anything changed on disk.

    Content, not size and modification time: an edit that keeps the size and lands in the same
    clock tick (version 1 -> version 2) would otherwise be missed. Data analysis recipe files are small, so
    reading them is cheap. (The data files are large and are hashed once per session instead.)
    """
    signature = []
    for f in files:
        try:
            digest = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        except OSError:
            digest = "MISSING"
        signature.append((str(f), digest))
    return tuple(signature)


# ---------------------------------------------------------------------------
# The loaded data analysis recipe, kept in memory and revalidated against the disk
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LoadedDataAnalysisRecipe:
    path: str
    config: ConfigManager
    files: tuple
    signature: tuple
    data_analysis_recipe_sha256: str  # file-set hash (provenance)
    material_hash: str    # canonical hash of the Tier 1 material (cache keys)
    tier1_engines: dict   # the effective data engine of the tier 1 of every table and join (an argument of the tier-1 key)

    @property
    def raw(self) -> dict:
        return self.config.raw_config


@dataclass(frozen=True)
class DataAnalysisRecipeKeys:
    """Everything the stored stages of one data analysis recipe depend on, computed once per session."""

    data_analysis_recipe_sha256: str   # file-set hash (provenance, session key)
    data_batch_hash: str   # content hash of the source data files
    tier1_key: str         # chained key of the Tier 1 parquet


def data_analysis_recipe_keys(loaded: "LoadedDataAnalysisRecipe", data_batch_hash: str) -> DataAnalysisRecipeKeys:
    return DataAnalysisRecipeKeys(
        data_analysis_recipe_sha256=loaded.data_analysis_recipe_sha256,
        data_batch_hash=data_batch_hash,
        tier1_key=tier1_key(loaded.material_hash, data_batch_hash, loaded.tier1_engines),
    )


_CACHE: dict[str, LoadedDataAnalysisRecipe] = {}
_LOCK = threading.Lock()


def load_data_analysis_recipe(path: Union[str, Path]) -> LoadedDataAnalysisRecipe:
    """Load a data analysis recipe, or return the one in memory when none of its files changed on disk.

    A failed load (a data analysis recipe error) is never cached.
    """
    key = os.path.abspath(str(path))
    with _LOCK:
        entry = _CACHE.get(key)
        if entry is not None and files_signature(entry.files) == entry.signature:
            return entry
        printed = io.StringIO()
        try:
            with contextlib.redirect_stderr(printed):   # ConfigManager prints its [FATAL] block to stderr before it exits
                config = ConfigManager(key)
        except SystemExit as stop:
            # ConfigManager ends the program on a contradictory file (ADR-077). A recipe broken on disk after the app
            # started (a save from Blueprint, GATE-GAP-1) must not end the session of every reader: an ordinary error.
            from app.modules.data_analysis_recipe_validator import _load_error_text
            raise RecipeLoadError(f"{_load_error_text(printed.getvalue(), stop)}; the data analysis recipe cannot be loaded ({key})") from None
        files = tuple(os.path.abspath(f) for f in config.loaded_files)
        loaded = LoadedDataAnalysisRecipe(
            path=key,
            config=config,
            files=files,
            signature=files_signature(files),
            data_analysis_recipe_sha256=data_analysis_recipe_fileset_hash(files, os.path.dirname(key)),
            material_hash=canonical_hash(tier1_material(config.raw_config)),
            tier1_engines=tier1_engines(config.raw_config),
        )
        _CACHE[key] = loaded
        return loaded


def clear_data_analysis_recipe_cache() -> None:
    with _LOCK:
        _CACHE.clear()
