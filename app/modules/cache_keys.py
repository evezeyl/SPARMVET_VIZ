"""
@deps
provides: function:load_data_analysis_recipe, function:tier1_key, function:tier2_key, function:data_analysis_recipe_fileset_hash, function:data_analysis_recipe_keys, class:LoadedDataAnalysisRecipe, class:DataAnalysisRecipeKeys
consumes: libs/utils/src/utils/config_loader.py
consumed_by: app/modules/orchestrator.py, app/modules/session_manager.py, app/src/server.py, app/tests/test_cache_keys.py
doc: .claude/knowledge/architecture_decisions.md#adr-089, docs/foundations/reproducibility_hash_schema.qmd
@end_deps

Cache chain keys (ADR-089), headless, no Shiny.

Every stored stage has a key made from its own inputs and the key of the stage before it:

    tier1_key = hash(engine version, resolved data analysis recipe minus downstream-only parts, data_batch_hash)
    tier2_key = hash(tier1_key, the join's tier2 steps)

so a change anywhere upstream reaches every stage after it, and nothing is missed.

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
import hashlib
import json
import os
import threading
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable, Union

from utils.config_loader import ConfigManager

# Bump when an action's behaviour or these key rules change: it invalidates every stored stage.
ENGINE_CACHE_VERSION = "4"   # 4: recipe format 1 (the published columns are a polars_select step, no final_contract; new actions and ingestion); 3: the key order of final_contract (issue #86); 2: deterministic row order (ADR-090)

# Top-level data analysis recipe sections that only matter after Tier 2 (the plots). Everything else,
# including sections this code has never heard of, belongs to Tier 1 (fail-safe rule).
_DOWNSTREAM_TOP_LEVEL = ("info", "analysis_groups", "plot_defaults", "plots")


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
    """The resolved data analysis recipe without the downstream-only parts (fail-safe: unknown parts stay in)."""
    material = {k: v for k, v in raw.items() if k not in _DOWNSTREAM_TOP_LEVEL}
    joins = material.get("joins")
    if isinstance(joins, dict):
        stripped = {}
        for join_id, spec in joins.items():
            steps = spec.get("steps") if isinstance(spec, dict) else None
            if isinstance(steps, dict) and "tier2" in steps:
                spec = {**spec, "steps": {k: v for k, v in steps.items() if k != "tier2"}}
            stripped[join_id] = spec
        material["joins"] = stripped
    return material


def tier2_steps(raw: dict, join_id: str) -> list:
    """The tier2 steps of one join's step list (empty when there are none: T2 equals T1)."""
    joins = raw.get("joins")
    spec = joins.get(join_id) if isinstance(joins, dict) else None
    steps = spec.get("steps") if isinstance(spec, dict) else None
    steps = steps.get("tier2") if isinstance(steps, dict) else None
    return list(steps) if steps else []


# ---------------------------------------------------------------------------
# Keys
# ---------------------------------------------------------------------------


def tier1_key(material_hash: str, data_batch_hash: str) -> str:
    return hash_text("\n".join(["tier1", engine_fingerprint(), material_hash, data_batch_hash]))


def tier2_key(tier1_key_value: str, steps: list) -> str:
    return hash_text("\n".join(["tier2", tier1_key_value, canonical_hash(steps)]))


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
        tier1_key=tier1_key(loaded.material_hash, data_batch_hash),
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
        config = ConfigManager(key)
        files = tuple(os.path.abspath(f) for f in config.loaded_files)
        loaded = LoadedDataAnalysisRecipe(
            path=key,
            config=config,
            files=files,
            signature=files_signature(files),
            data_analysis_recipe_sha256=data_analysis_recipe_fileset_hash(files, os.path.dirname(key)),
            material_hash=canonical_hash(tier1_material(config.raw_config)),
        )
        _CACHE[key] = loaded
        return loaded


def clear_data_analysis_recipe_cache() -> None:
    with _LOCK:
        _CACHE.clear()
