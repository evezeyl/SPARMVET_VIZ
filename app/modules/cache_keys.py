"""
@deps
provides: function:load_data_analysis_recipe, function:tier1_material, function:tier1_engines, function:tier2_engine, function:collection_tier2_key, function:plot_tier3_key, function:tier3_key, function:tier3_engine, function:tier2_steps (from utils.recipe_tiers), function:tier3_steps (from utils.recipe_tiers), function:tier1_key, function:tier2_key, function:table_key_parts, function:table_definition_for_key, function:dataset_file_hashes, function:batch_hash_of, constant:ENGINE_CACHE_VERSION, constant:CACHE_VERSION_META, constant:STORED_TABLES_REBUILT_NOTICE, function:data_analysis_recipe_fileset_hash, function:data_analysis_recipe_keys, class:LoadedDataAnalysisRecipe, class:DataAnalysisRecipeKeys, class:TableKeyParts, class:ResolvedRecipe, function:loaded_from_resolved, function:tier1_audit_part, function:audit_part
consumes: libs/utils/src/utils/config_loader.py, libs/utils/src/utils/recipe_tiers.py, libs/utils/src/utils/engines.py (tier_engine: the one reading of the engine of a tier), libs/utils/src/utils/recipe_graph.py (build_graph: lineage_back, source_tables, parents: which definitions and which data files a table depends on, ADR-101), libs/utils/src/utils/audit_copy.py (split_marked, audit_operation, strip_marked: the marked audit steps of a copy are the audit parts of a key, not its definition)
consumed_by: app/modules/orchestrator.py, app/modules/session_manager.py, app/src/server.py, app/src/bootloader.py, app/handlers/export_handlers.py, app/tests/test_cache_keys.py, app/tests/test_engine_keys.py, app/tests/test_table_keys.py, app/tests/test_tier3_reader.py, app/tests/test_audit_keys.py, app/modules/audit_run.py
doc: .claude/knowledge/architecture_decisions.md#adr-089, .claude/knowledge/architecture_decisions.md#adr-101, docs/foundations/reproducibility_hash_schema.qmd
@end_deps

Cache keys of the stored tables (ADR-089 as amended by ADR-101), headless, no Shiny.

The key of a stored table is a SERIES OF LABELLED PARTS joined with dots in execution order, never hashed again (ADR-101 point 2).
Each part is 128 bits (32 hex characters); a part that is empty is left out:

    T1 key = E-<32> . rC-<32> . dC-<32> . [a1-<32>]
    T2 key = <the T1 key it is computed from> . [s2-<32>] . [a2-<32>]    (no s2 part when the table has no tier-2 steps: the key of T2 IS the T1 key)
    T3 key = <the T2 key of the plot's table> . [s3-<32>] . [a3-<32>]    (no s3 part when the plot has no tier-3 steps: the key of the plot IS the key of its table)

    E   the data engine(s) that build THIS table, with the versions of the engine libraries and the cache version
    rC  the definition of THIS table: its own and that of everything upstream of it (a join: its ingredients), from the recipe graph
    dC  the content of the data files THIS table reads (the source tables of the graph), not those of the whole recipe
    s2  the tier-2 steps of the table and the data engine that runs them
    s3  the tier-3 steps of a plot entry and the data engine that runs them (PROVISIONAL name of the label `s3`: ADR-101 names the part, not the spelling)
    a1 a2 a3  the AUDIT steps of a copy of the recipe (`utils.audit_copy`): the steps that carry the marker `id: audit_<8 hex>_<k>`, at the end of the
        tier-1 list of the table and of everything upstream of it (a1), of the tier-2 list of the table (a2) and of the tier-3 list of the plot (a3), as
        the operations without their `id` and `comment` ("without reasons, dates or initials"), in list order; a2 and a3 also hold the engine that runs
        the tier. The marked steps are NOT part of rC, s2 and s3, so a copy with no audit step has exactly the keys of its original, and an audit step
        reaches the keys downstream of it the way an upstream definition does (a1 is the audit part of the whole lineage, like rC is its definition).
        The part is left out when there is no audit step. PROVISIONAL: the spelling of the labels a1 a2 a3 is ADR-101's.

A change in one table therefore moves the key of that table and of the tables built from it, and no other (the fail-safe is below).
The first part that differs between two keys says where two builds diverge.

The engine rule (D-0240): a key holds the engine of what it stores, and nothing else. The ENGINE of a tier is its own
`data_engine`, else the recipe's (`utils.engines.tier_engine`, the value the orchestrator runs). It is an argument of the key,
not a part of the recipe text, so the same engine written on the tier or inherited gives the same key, and no text change can
forget it. A later stage's engine never moves an earlier key. The PLOT engine is in no table key: it is downstream (the plots),
a picture has no stored key. The tier-3 engine of a plot entry is an argument of its `s3` part and of no other key.

Fail-safe rule (ADR-101 point 3): a part is NARROW only when the recipe graph (`utils.recipe_graph`) can say what the table depends
on. When it cannot (the recipe is not a graph: an unknown ingredient, a cycle, ...), or a table reads no source table, the parts of
that table are COARSE: the definition is the whole resolved recipe minus the downstream-only parts and the data is every data file.
A wrong guess can then only cause an extra rebuild, never a stale result. A part of the recipe that belongs to no table (an unknown
or shared top-level section) enters the definition of every table.

Two identity hashes, two purposes; they say "is this the same project state" and NEVER decide what to rebuild:
  - data_analysis_recipe_sha256 (provenance, session key, export key check): hash of the FILE SET (entry file and
    every included file). Independently verifiable with sha256sum.
  - data_batch_hash (session key, export key check): hash of the content of ALL data files.
The keys of the tables use the RESOLVED content of the recipe, so comments, spacing and how the data analysis recipe is
split into files do not force a rebuild.

The loaded data analysis recipe is kept in memory and revalidated against the content of its files.
"""
import contextlib
import hashlib
import io
import json
import os
import threading
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable, Mapping, Union

from utils.audit_copy import audit_operation, split_marked, strip_marked
from utils.errors import RecipeLoadError
from utils.config_loader import ConfigManager
from utils.engines import tier_engine
from utils.recipe_graph import RecipeGraphError, build_graph
# The one reading of a collection's tier-2 list (issue #77); `tier2_steps` is used from here by the app.
from utils.recipe_tiers import (  # noqa: F401 - tier2_steps and tier3_steps are part of this module's interface
    METADATA_SCHEMA, SCHEMA_SECTIONS, collection_bodies, collection_body, plot_entries, plot_entry, step_list, tier2_steps, tier3_steps,
    without_data_engines, without_tier2)

# Bump when an action's behaviour or these key rules change: it invalidates every stored stage.
ENGINE_CACHE_VERSION = "6"   # 6: a key per stored table, a series of labelled parts (ADR-101); 5: the engine of a tier is an argument of the key of that tier, the plot engine is in no table key (D-0240); 4: recipe format 1 (the published columns are a polars_select step, no final_contract; new actions and ingestion); 3: the key order of final_contract (issue #86); 2: deterministic row order (ADR-090)

# Length of one part of a key, in hex characters (128 bits, ADR-101 point 2).
KEY_PART_LENGTH = 32

# Top-level data analysis recipe sections that only matter after Tier 2 (the plots). Everything else,
# including sections this code has never heard of, belongs to Tier 1 (fail-safe rule). The recipe's `plot_engine` is one of
# them: it draws, it builds no table (D-0240); the `plot_engine` of a plot entry is inside `analysis_groups`.
_DOWNSTREAM_TOP_LEVEL = ("info", "analysis_groups", "plot_defaults", "plots", "plot_engine")

# The top-level sections that hold the tables: each table is read on its own, from the graph. Every other top-level part is shared.
_TABLE_SECTIONS = (*SCHEMA_SECTIONS, METADATA_SCHEMA, "joins")

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


def key_part(label: str, *material: str) -> str:
    """One labelled part of a key: `label-` and 128 bits (32 hex characters) of the material."""
    return f"{label}-{hash_text(chr(10).join(material))[:KEY_PART_LENGTH]}"


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "unknown"


def engine_fingerprint() -> str:
    """The code that produces the data: cache version constant plus the installed engine versions."""
    return f"{ENGINE_CACHE_VERSION}|polars={_package_version('polars')}|transformer={_package_version('transformer')}"


# ---------------------------------------------------------------------------
# The data files: content hashes, once per session
# ---------------------------------------------------------------------------


def dataset_file_hashes(source_files: Mapping[str, Union[str, Path]]) -> dict[str, str]:
    """{dataset id: sha256 of its file content}, in sorted order; `MISSING:<id>` for a path that does not exist.

    The one reading of the data files for the keys: the batch hash and the `dC` part of every table are made from these."""
    hashes: dict[str, str] = {}
    for dataset_id in sorted(source_files):
        path = Path(source_files[dataset_id])
        hashes[dataset_id] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else f"MISSING:{dataset_id}"
    return hashes


def batch_hash_of(file_hashes: Mapping[str, str]) -> str:
    """The hash of ALL data files (the identity hash `data_batch_hash`): the `id:hash` lines in sorted id order, hashed once more."""
    return hash_text("\n".join(f"{dataset_id}:{file_hashes[dataset_id]}" for dataset_id in sorted(file_hashes)))


# ---------------------------------------------------------------------------
# Which parts of the resolved data analysis recipe belong to which stage
# ---------------------------------------------------------------------------


def tier1_material(raw: dict) -> dict:
    """The resolved data analysis recipe without the downstream-only parts (fail-safe: unknown parts stay in).

    This is the COARSE definition of a table (the fallback when the graph cannot say what a table depends on).
    The tier-2 list of every collection (a join's `tier2.steps`, a schema's `tier2.steps`) is downstream of
    Tier 1: it goes into the `s2` part instead (`utils.recipe_tiers`, issue #77). The written data engines are
    left out too: their effect on Tier 1 is `tier1_engines`, an argument of the key (D-0240). The marked audit steps of a copy are left out as well:
    they are the audit part `a1` (`tier1_audit_part`), never the definition."""
    return without_data_engines(without_tier2(strip_marked({k: v for k, v in raw.items() if k not in _DOWNSTREAM_TOP_LEVEL})))


def tier1_engines(raw: dict) -> dict:
    """{id of every table and join: the effective data engine of its tier 1}, the value `DataOrchestrator` runs it with.

    The tier's own `data_engine`, else the recipe's (`utils.engines.tier_engine`). None for a block that has no engine at all
    (the checker refuses such a recipe, T04; the key never invents a default engine)."""
    return {cid: tier_engine(raw, body, "tier1") for cid, body in collection_bodies(raw).items()}


def tier2_engine(raw: dict, collection_id: str):
    """The effective data engine of the tier 2 of one collection: its own `data_engine`, else the recipe's."""
    return tier_engine(raw, collection_body(raw, collection_id), "tier2")


def tier3_engine(raw: dict, plot_id: str):
    """The effective data engine of the tier 3 of one plot entry: its own `data_engine`, else the recipe's."""
    return tier_engine(raw, plot_entry(raw, plot_id), "tier3")


def table_definition_for_key(body: Any) -> Any:
    """What of the definition of one table or join enters the key of every table that is built from it.

    Today: everything written under it, except its tier-2 list (it is the `s2` part of the T2 key, never of T1) and the data
    engine written on its tier 1 (the effective engine is an argument of the key, D-0240), and the marked audit steps at the end of its tier 1
    (the audit part `a1`, never the definition: a copy with no audit step has the keys of its original). The `labels` and descriptions of a table
    or join stay IN: this is the owner's open point (a label change rebuilds the table, which is safe and wasteful). To take labels
    out, remove them HERE and nowhere else; the property test of `app/tests/test_table_keys.py` then has to learn that they are
    not an input. It waits for the owner's decision."""
    if not isinstance(body, dict):
        return body
    kept = {k: v for k, v in body.items() if k != "tier2"}
    tier1 = kept.get("tier1")
    if isinstance(tier1, dict):
        kept["tier1"] = {k: (split_marked(v)[0] if k == "steps" and isinstance(v, list) else v) for k, v in tier1.items() if k != "data_engine"}
    return kept


@dataclass(frozen=True)
class TableKeyParts:
    """What a table's tier-1 key is made of, except the content of the data files and the engine versions (no disk, no version).

    engines: canonical hash of {table: effective tier-1 data engine} of the table and everything upstream of it.
    definition: the finished `rC` part. datasets: the source tables whose files the table reads (empty when `coarse`).
    coarse: the fail-safe form: the definition is the whole recipe and the data is every file.
    audit: the finished `a1` part (the marked audit steps at tier 1 of the table and of everything upstream of it), or "" when there is none."""
    table: str
    engines: str
    definition: str
    datasets: tuple = ()
    coarse: bool = False
    audit: str = ""


def tier1_audit_part(bodies: dict, names) -> str:
    """The finished `a1` part of the tables `names` (a table and everything upstream of it; the whole recipe when coarse), or "" when none of them has a
    marked audit step at the end of its tier 1. The steps are the operations without `id` and `comment`, in list order, per table."""
    held = {name: [audit_operation(step) for step in split_marked(step_list(bodies[name], "tier1"))[1]] for name in names}
    held = {name: operations for name, operations in held.items() if operations}
    return key_part("a1", canonical_hash(held)) if held else ""


def audit_part(label: str, marked_steps: list, engine) -> str:
    """The finished `a2` or `a3` part of a list of marked audit steps (`label` says which), with the data engine that runs the tier, or "" when the list is empty."""
    if not marked_steps:
        return ""
    return key_part(label, canonical_hash([audit_operation(step) for step in marked_steps]), canonical_hash(engine))


def _coarse_parts(raw: dict, table: str = "") -> TableKeyParts:
    bodies = collection_bodies(raw)
    return TableKeyParts(table, canonical_hash(tier1_engines(raw)), key_part("rC", canonical_hash(tier1_material(raw))), (), True,
                         tier1_audit_part(bodies, bodies))


def table_key_parts(raw: dict) -> tuple[dict[str, TableKeyParts], TableKeyParts]:
    """({table: its parts}, the coarse parts of the whole recipe).

    The recipe graph says, for each table, which definitions (its own and everything upstream) and which source tables it depends
    on. When the graph cannot be drawn every table is coarse; so is a table that reads no source table (fail-safe, ADR-101 point 3).
    The coarse parts of the whole recipe also serve a table id the recipe does not name (nothing is stored under it)."""
    coarse = _coarse_parts(raw)
    try:
        graph = build_graph(raw)
    except RecipeGraphError:
        return {table: _coarse_parts(raw, table) for table in collection_bodies(raw)}, coarse
    bodies = collection_bodies(raw)
    shared = canonical_hash({k: v for k, v in raw.items()
                             if k not in _TABLE_SECTIONS and k not in _DOWNSTREAM_TOP_LEVEL and k != "data_engine"})
    parts: dict[str, TableKeyParts] = {}
    for table in graph.collections():
        node = f"T1:{table}"
        upstream = [graph.node(n).name for n in graph.lineage_back(node) if graph.node(n).kind == "T1"] + [table]
        datasets = tuple(sorted({graph.node(n).name for n in graph.source_tables(node)}))
        if not datasets:
            parts[table] = _coarse_parts(raw, table)
            continue
        definition = {name: {"path": graph.node(f"T1:{name}").path,
                             "reads": [graph.node(p).name for p in graph.parents(f"T1:{name}")],
                             "definition": table_definition_for_key(bodies[name])} for name in upstream}
        engines = {name: tier_engine(raw, bodies[name], "tier1") for name in upstream}
        parts[table] = TableKeyParts(table, canonical_hash(engines), key_part("rC", shared, canonical_hash(definition)), datasets,
                                     audit=tier1_audit_part(bodies, upstream))
    return parts, coarse


# ---------------------------------------------------------------------------
# Keys
# ---------------------------------------------------------------------------


def tier1_key(parts: TableKeyParts, file_hashes: Mapping[str, str]) -> str:
    """The key of the stored Tier 1 table: `E . rC . dC`, then `a1` when the table or something upstream of it has a marked audit step. `file_hashes`
    is `dataset_file_hashes(...)`; a source table with no file is part of the key as "no file", so the key moves when the file appears."""
    wanted = dict(file_hashes) if parts.coarse else {ds: file_hashes.get(ds, "NOFILE") for ds in parts.datasets}
    held = [key_part("E", engine_fingerprint(), parts.engines), parts.definition, key_part("dC", canonical_hash(wanted))]
    return ".".join(held + [parts.audit] if parts.audit else held)


def tier2_key(tier1_key_value: str, steps: list, engine) -> str:
    """The key of a Tier 2 table: the Tier 1 key it is computed from, then the `s2` part (its steps and the data engine that runs them, D-0240)."""
    return f"{tier1_key_value}.{key_part('s2', canonical_hash(steps), canonical_hash(engine))}"


def collection_tier2_key(raw: dict, collection_id: str, tier1_key_value: str) -> str:
    """The key of the Tier 2 table of one collection under the Tier 1 key given. The one place that makes a tier-2 key from a recipe,
    for the orchestrator, the keys object and the export record.

    A collection with tier-2 steps: the Tier 1 key and the `s2` part. A collection with none: T2 IS T1, the empty part is left out and
    the key is the Tier 1 key itself (ADR-101 point 2). Nothing is stored for it. (Before the tier-3 reader this returned an empty
    string for that case and each caller read "" as "no key"; a caller that needs to know whether T2 has steps asks `tier2_steps`.)
    The marked audit steps at the end of the list are not in `s2`: they are the part `a2`, after it (and alone when the original has no tier-2 step)."""
    plain, marked = split_marked(tier2_steps(raw, collection_id))
    if not (plain or marked):
        return tier1_key_value
    engine = tier2_engine(raw, collection_id)
    key = tier2_key(tier1_key_value, plain, engine) if plain else tier1_key_value
    return f"{key}.{audit_part('a2', marked, engine)}" if marked else key


def tier3_key(tier2_key_value: str, steps: list, engine) -> str:
    """The key of a plot's T3 table: the key of the Tier 2 table it is computed from, then the `s3` part (its steps and the data
    engine that runs them). A series of labelled parts like the other tiers (ADR-101 point 2); a place is left after `s3` for the audit part."""
    return f"{tier2_key_value}.{key_part('s3', canonical_hash(steps), canonical_hash(engine))}"


def plot_tier3_key(raw: dict, plot_id: str, tier2_key_value: str) -> str:
    """The key of the table one plot reads, under the key of the Tier 2 table of its target. A plot with tier-3 steps: that key and
    the `s3` part. A plot with none reads its table as it is: the empty part is left out, the key IS the key of its table, and
    nothing is built or stored twice. The marked audit steps at the end of the list are not in `s3`: they are the part `a3`, after it (and alone when the
    plot has no tier-3 step of its own). The one place that makes a tier-3 key from a recipe."""
    plain, marked = split_marked(tier3_steps(raw, plot_id))
    if not (plain or marked):
        return tier2_key_value
    engine = tier3_engine(raw, plot_id)
    key = tier3_key(tier2_key_value, plain, engine) if plain else tier2_key_value
    return f"{key}.{audit_part('a3', marked, engine)}" if marked else key


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
    table_parts: dict     # {table: TableKeyParts}: what the tier-1 key of each table is made of, apart from the data files (ADR-101)
    coarse_parts: TableKeyParts   # the fail-safe parts of the whole recipe, for a table id the recipe does not name

    @property
    def raw(self) -> dict:
        return self.config.raw_config


@dataclass(frozen=True)
class ResolvedRecipe:
    """What the engine reads of a recipe that is not a file: the resolved dictionary (`raw_config`) and no file (`loaded_files`). It stands where
    the `ConfigManager` of a loaded file stands, for an audit copy (`loaded_from_resolved`)."""
    raw_config: dict
    loaded_files: tuple = ()


def loaded_from_resolved(original: LoadedDataAnalysisRecipe, raw: dict) -> LoadedDataAnalysisRecipe:
    """The recipe `raw` (an audit copy of the original, `utils.audit_copy`) in the form the engine reads, with the key parts of that very dictionary.

    The path, the files and their signature are the original's: the copy has no file of its own, the original's names it (its id, its data
    location). `data_analysis_recipe_sha256` is the hash of the resolved dictionary, NOT of a file set (there is none): PROVISIONAL, the identity of
    an audit copy that is written to a file is not decided. The original is not changed."""
    table_parts, coarse_parts = table_key_parts(raw)
    return LoadedDataAnalysisRecipe(
        path=original.path, config=ResolvedRecipe(raw), files=original.files, signature=original.signature,
        data_analysis_recipe_sha256=canonical_hash(raw), table_parts=table_parts, coarse_parts=coarse_parts)


@dataclass(frozen=True)
class DataAnalysisRecipeKeys:
    """Everything the stored tables of one data analysis recipe depend on, computed once per session.

    The two identity hashes say whether the project state is the same (session, export key check); the key of each table decides
    what to rebuild. `tier1_keys` holds the Tier 1 key of every table and join of the recipe (ADR-101)."""

    data_analysis_recipe_sha256: str   # file-set hash (provenance, session key)
    data_batch_hash: str   # content hash of ALL the source data files (identity)
    tier1_keys: dict = field(hash=False)   # {table or join id: the key of its Tier 1 table}
    coarse_tier1_key: str = ""   # the key of a table id the recipe does not name: the whole recipe and every file (fail-safe)
    tier2_keys: dict = field(default_factory=dict, hash=False)   # {table or join id: the key of its Tier 2 table; the Tier 1 key when it has no tier-2 steps}
    plot_keys: dict = field(default_factory=dict, hash=False)   # {plot id: the key of the table the plot reads; the Tier 2 key of its target when it has no tier-3 steps}

    def tier1_key_of(self, table: str) -> str:
        """The Tier 1 key of one table. A table the recipe does not name gets the coarse key (nothing is ever stored under it)."""
        return self.tier1_keys.get(table, self.coarse_tier1_key)

    def tier2_key_of(self, table: str) -> str:
        """The key of the Tier 2 table of one table: its Tier 1 key when it has no tier-2 steps (ADR-101 point 2). A table the recipe
        does not name gets the coarse Tier 1 key."""
        return self.tier2_keys.get(table, self.coarse_tier1_key)

    def plot_key_of(self, plot_id: str) -> str:
        """The key of the table a plot reads: the one way to ask. The key of the Tier 2 table of its target when the plot has no
        tier-3 steps (the plot reads its table as it is), else that key and the `s3` part (ADR-101 point 2). A plot the recipe
        does not name has no key: the answer is an error, never another plot's key."""
        try:
            return self.plot_keys[plot_id]
        except KeyError:
            raise KeyError(f"The recipe has no plot '{plot_id}', so there is no key of the table it reads.") from None


def data_analysis_recipe_keys(loaded: "LoadedDataAnalysisRecipe", file_hashes: Mapping[str, str]) -> DataAnalysisRecipeKeys:
    """The keys of a loaded recipe over the content hashes of its data files (`dataset_file_hashes`); no file gives an empty batch hash."""
    tier1_keys = {table: tier1_key(parts, file_hashes) for table, parts in loaded.table_parts.items()}
    tier2_keys = {table: collection_tier2_key(loaded.raw, table, key) for table, key in tier1_keys.items()}
    coarse = tier1_key(loaded.coarse_parts, file_hashes)
    # a plot whose target the recipe does not name (or names none) is left out: its table has no key, and `plot_key_of` says so
    plot_keys = {plot_id: plot_tier3_key(loaded.raw, plot_id, tier2_keys[entry["target_dataset"]])
                 for plot_id, entry in plot_entries(loaded.raw).items() if entry.get("target_dataset") in tier2_keys}
    return DataAnalysisRecipeKeys(
        data_analysis_recipe_sha256=loaded.data_analysis_recipe_sha256,
        data_batch_hash=batch_hash_of(file_hashes) if file_hashes else "",
        tier1_keys=tier1_keys,
        coarse_tier1_key=coarse,
        tier2_keys=tier2_keys,
        plot_keys=plot_keys,
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
        table_parts, coarse_parts = table_key_parts(config.raw_config)
        loaded = LoadedDataAnalysisRecipe(
            path=key,
            config=config,
            files=files,
            signature=files_signature(files),
            data_analysis_recipe_sha256=data_analysis_recipe_fileset_hash(files, os.path.dirname(key)),
            table_parts=table_parts,
            coarse_parts=coarse_parts,
        )
        _CACHE[key] = loaded
        return loaded


def clear_data_analysis_recipe_cache() -> None:
    with _LOCK:
        _CACHE.clear()
