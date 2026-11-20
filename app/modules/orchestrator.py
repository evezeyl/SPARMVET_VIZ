# @deps
# provides: pipeline:materialize_tier1, pipeline:materialize_tier2, pipeline:materialize_tier3, function:plot_read_error_text, method:prepare_ingredient, method:read_source, method:locate_dataset_file, method:get_source_files, function:compute_data_analysis_recipe_keys
# mirrors: libs/transformer/tests/debug_assembler.py
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/utils/src/utils/recipe_tiers.py (collection_body), app/modules/engine_registry.py (data_entry: the engine that runs a tier, D-0219), libs/utils/src/utils/recipe_tiers.py (plot_entry, tier3_steps), libs/transformer/src/transformer/anchor.py, app/modules/cache_keys.py (collection_tier2_key: the one place that makes the tier-2 key; ENGINE_CACHE_VERSION: the mark written into each stored table; DataAnalysisRecipeKeys.tier1_key_of: the key of each stored table, ADR-101; dataset_file_hashes)
# consumed_by: app/tests/test_read_source.py (read_source: one source table as the ingestion reads it, for the Source view of HOME, D-0310), app/src/server.py, app/handlers/home_theater.py (materialize_tier3: the plot and My view base; plot_read_error_text: the plot name on a read failure), app/handlers/export_handlers.py (materialize_tier3), app/modules/gallery_examples.py, assets/scripts/golden_baseline.py, assets/scripts/recipe_pictures.py, app/handlers/blueprint_handlers.py, app/modules/bundle_importer.py, app/modules/data_analysis_recipe_validator.py, app/modules/audit_run.py (materialize_tier1/2/3 with a handed recipe: the audit copy)
# doc: .claude/knowledge/dependency_index.md
# @end_deps
import copy
import polars as pl
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from utils.errors import DataAnalysisRecipeError, IngestionError, RecipeLoadError, SPARMVET_Error, TransformationError
from ingestion.ingestor import DataIngestor, find_dataset_file
from transformer.anchor import read_anchor_if_key, write_anchor
from app.modules.engine_registry import data_entry
from utils.recipe_tiers import collection_body, plot_entry
from app.modules.cache_keys import (CACHE_VERSION_META, DataAnalysisRecipeKeys, ENGINE_CACHE_VERSION, LoadedDataAnalysisRecipe, collection_tier2_key,
                                    data_analysis_recipe_keys, dataset_file_hashes, load_data_analysis_recipe, tier2_engine, tier2_steps, tier3_steps)

# Parquet metadata key holding the Tier 1 key of the table (ADR-089, ADR-101: a key per table).
TIER1_KEY_META = "sparmvet_tier1_key"
# Parquet metadata key holding the Tier 2 key of the table (ADR-089 point 6, ADR-101).
TIER2_KEY_META = "sparmvet_tier2_key"


def tier2_path_for(tier1_path: Path) -> Path:
    """Where the Tier 2 parquet of a join lives: next to its Tier 1 parquet, `<name>__T2.parquet`."""
    tier1_path = Path(tier1_path)
    return tier1_path.with_name(f"{tier1_path.stem}__T2{tier1_path.suffix}")


# data_lookup (deployment file): where the data of a dataset is found.
#   data_analysis_recipe_paths: the source.path written in the data analysis recipe (development default)
#   by_dataset_id:  a file named after the dataset id in the raw_data location (a pipeline delivers it)
DATA_LOOKUP_CHOICES = ("data_analysis_recipe_paths", "by_dataset_id")

# The sub-folder of one import (<imports_dir>/<recipe id>/) that holds its data files.
IMPORT_DATA_FOLDER = "data"

@dataclass(frozen=True)
class InputsChanged:
    """What changed while a table was being built (a clause, for example "the data files changed")."""
    text: str


def plot_read_error_text(raw_recipe: dict, plot_id: str, error: BaseException) -> str:
    """The text a consumer shows when reading the table of a plot failed: the error, and for a plot with tier-3 steps in the recipe
    a line that names the plot and says the table carries those steps. A failure that depends on values (a cast of a value that does
    not fit) shows only when the table is read, so `materialize_tier3` cannot name it; the engine's own message does not name the plot,
    and it does not name the step. A plot without tier-3 steps: the error as it is."""
    if not tier3_steps(raw_recipe, plot_id):
        return str(error)
    return (f"{error}\nThe plot '{plot_id}' has tier-3 steps in the data analysis recipe, applied to the table it reads; "
            f"if this error is about a value, check them.")


class DataOrchestrator:
    """
    Handles the ingestion and assembly logic (Tier 1 Materialization).
    Ensures the UI remains 'Thin' by delegating heavy processing to libraries.
    """

    def __init__(self, data_analysis_recipes_dir: Path, raw_data_dir: Path, data_lookup: str = "data_analysis_recipe_paths",
                 imports_dir: Path | None = None):
        self.data_analysis_recipes_dir = data_analysis_recipes_dir
        self.raw_data_dir = raw_data_dir
        if data_lookup not in DATA_LOOKUP_CHOICES:
            raise ValueError(f"data_lookup must be one of {DATA_LOOKUP_CHOICES}, got {data_lookup!r}")
        self.data_lookup = data_lookup
        self.discover_by_dataset_id = data_lookup == "by_dataset_id"
        # The folder that holds one sub-folder per recipe imported from a bundle (bundle_importer.py):
        # <imports_dir>/<recipe id>/data/<dataset id>.tsv. Its existence for a recipe id is the record of the import.
        self.imports_dir = Path(imports_dir) if imports_dir else None
        self.ingestor = DataIngestor(data_dir=str(raw_data_dir))

    def import_data_dir(self, data_analysis_recipe_id: str | None) -> Path | None:
        """The data folder of a recipe that was imported from a bundle, or None for any other recipe."""
        if not (self.imports_dir and data_analysis_recipe_id):
            return None
        folder = self.imports_dir / data_analysis_recipe_id / IMPORT_DATA_FOLDER
        return folder if folder.is_dir() else None

    def locate_dataset_file(self, data_analysis_recipe_id: str | None, ds_id: str, ds_schema: dict) -> Path | None:
        """The ONE place that decides which file holds a dataset; reading and hashing both use the answer.

        - a recipe imported from a bundle: `<dataset id>.tsv|.parquet` in the folder of that import; the recipe's own
          path and `raw_data` are never consulted (the data of an import is only what the bundle carried);
        - `data_lookup: by_dataset_id` (production): `<dataset id>.tsv|.parquet` in `raw_data`, the recipe's path ignored;
        - `data_lookup: data_analysis_recipe_paths` (development): the recipe's `source.path` when it names a file; a
          schema without a path is found by id in `raw_data`.
        Returns None when there is no such file; raises IngestionError when one id has both a .tsv and a .parquet.
        """
        imported = self.import_data_dir(data_analysis_recipe_id)
        if imported is not None:
            return find_dataset_file(imported, ds_id)
        source = ds_schema.get("source") or {}
        if not self.discover_by_dataset_id and source.get("type") in ("local_tsv", "local_parquet") and source.get("path"):
            declared = Path(source["path"])
            return declared if declared.exists() else None
        return find_dataset_file(self.raw_data_dir, ds_id)

    def compute_data_analysis_recipe_keys(self, data_analysis_recipe_id: str,
                                          loaded: LoadedDataAnalysisRecipe | None = None) -> DataAnalysisRecipeKeys:
        """The keys every stored stage of this project depends on (ADR-089).

        Reads the data files to hash their content, so callers compute it once per session
        and pass it to materialize_tier1(). `loaded` is the recipe a build reads: the key is then made from that very
        object, not from a second reading of the files.
        """
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            raise FileNotFoundError(f"Data analysis recipe not found: {data_analysis_recipe_path}")
        loaded = loaded or load_data_analysis_recipe(data_analysis_recipe_path)
        # The data files are read once, here: the identity hash of all of them and the data part of the key of each table come
        # from the same content hashes (ADR-101 point 4).
        return data_analysis_recipe_keys(loaded, dataset_file_hashes(self.get_source_files(data_analysis_recipe_id)))

    def _read_source(self, ds_id: str, ds_schema: dict, recipe_id: str | None = None) -> tuple[pl.LazyFrame, dict]:
        """The ONE read of a source table: the file `locate_dataset_file` names, with the declared types, `strip` and `null_values`
        the ingestion applies, before any recipe step. Returns the lazy table and the schema with the file it was read from, so that
        `prepare_ingredient` (tier 1) and `read_source` (the Source view) read exactly the same."""
        located = self.locate_dataset_file(recipe_id, ds_id, ds_schema)
        if located is not None:
            kind = "local_parquet" if located.suffix == ".parquet" else "local_tsv"
            ds_schema = {**ds_schema, "source": {"type": kind, "path": str(located)}}
        elif self.import_data_dir(recipe_id) is not None:
            # WHY: without this the ingestor would look in raw_data and read another dataset of the same id.
            raise IngestionError(
                f"Dataset '{ds_id}' has no file in the data folder of the import of '{recipe_id}': "
                f"{self.import_data_dir(recipe_id)}.",
                tip=f"Expected {ds_id}.tsv or {ds_id}.parquet there. Import the bundle again; the data of an import is only what its bundle carried.")
        elif self.discover_by_dataset_id:
            # Production path: ignore data analysis recipe source.path, discover by schema ID name in
            # raw_data_dir (mirrors Galaxy/IRIDA connector); no file gives the ingestor's own error.
            ds_schema = {k: v for k, v in ds_schema.items() if k != "source"}
        # The declared types, `strip` and `null_values` are applied by the ingestion itself; a value that does not
        # fit its declared type fails there and names the column and the values.
        lf, _ = self.ingestor.ingest(ds_id, ds_schema)
        return lf, ds_schema

    def prepare_ingredient(self, ds_id: str, ds_schema: dict, recipe_id: str | None = None, recipe: dict | None = None) -> pl.LazyFrame:
        """Read one dataset of a data analysis recipe and apply its input contract and tier-1 wrangling (its T1).

        The schema's own tier-2 list is not run here: it is the T2 of the schema when a plot reads it directly, run by
        `materialize_tier2` like a join's (issue #77); a join reads the T1 of its ingredients.

        Raises when the file cannot be read, a declared input column is missing, or a value does
        not fit its declared type. Shared by materialize_tier1 and the data analysis recipe data check, so
        both see the dataset the same way. `recipe_id` selects the data folder of an imported recipe; `recipe` is the recipe's
        mapping, for the default `data_engine` of a table whose tier 1 names none (D-0219).

        The file read is the file `locate_dataset_file` names, the same one `get_source_files` hashes, through `_read_source`.
        """
        lf, ds_schema = self._read_source(ds_id, ds_schema, recipe_id)
        engine = data_entry(recipe, ds_schema, "tier1", where=f"The tier1 of the table '{ds_id}'")
        rules = engine.wrangler.tier_steps(ds_schema, "tier1")
        return engine.wrangler().run(lf, rules)

    # PROVISIONAL name (the coordinator's): read_source
    def read_source(self, data_analysis_recipe_id: str, dataset_id: str, loaded: LoadedDataAnalysisRecipe | None = None) -> pl.LazyFrame:
        """One source table of a recipe as the ingestion reads it, with its declared types, before any tier-1 step (the Source view of HOME,
        D-0310). Lazy; nothing is written to disk and no key is touched. The same read as the tier-1 build (`_read_source`).
        `loaded` is a pinned recipe (an audit copy), as in `materialize_tier1`.

        Raises FileNotFoundError for a recipe that has no file, DataAnalysisRecipeError for a table id the recipe does not name, and the
        ingestion's own error (IngestionError) when the file is missing or cannot be read; the error is the one the tier-1 build gives."""
        path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if loaded is None and not path.exists():
            raise FileNotFoundError(f"Data analysis recipe not found: {path}")
        loaded = loaded or load_data_analysis_recipe(path)
        schemas = self._schemas_of(loaded.raw)
        if dataset_id not in schemas:
            raise DataAnalysisRecipeError(
                f"No source table '{dataset_id}' in data analysis recipe '{data_analysis_recipe_id}'. Known: {', '.join(sorted(schemas)) or 'none'}.")
        try:
            lf, _ = self._read_source(dataset_id, schemas[dataset_id], data_analysis_recipe_id)
        except IngestionError as error:
            # The same kind of error as the tier-1 build ("Dataset 'X' could not be loaded ..."), naming the table and the reason.
            raise IngestionError(f"Source table '{dataset_id}' could not be read: {error}",
                                 tip=getattr(error, "tip", None) or "Check the file and the input_fields of this table in the data analysis recipe.") from error
        return lf

    def inputs_changed(self, data_analysis_recipe_id: str, built_from: DataAnalysisRecipeKeys, collection_id: str,
                       pinned: LoadedDataAnalysisRecipe | None = None) -> InputsChanged | None:
        """None when what the table `collection_id` depends on is still what `built_from` was made from, else what changed.

        The last check of a build, before its table is stored (STALE-KEY-STORE-1): a table built while its inputs
        changed holds rows of neither state, so no key could be true for it. The inputs of a table are what its key says
        (ADR-101): a change in another table, or a comment in the recipe, is not a change of this one and does not stop the
        store. A recipe that can no longer be read, or a recipe file that is gone, is a change and is named as such, never turned
        into "nothing changed" or left unsaid.

        `pinned` is a recipe the caller handed the build (an audit copy, `loaded_from_resolved`): it is not a file, so it cannot change on disk; the
        keys now are those of that very recipe over the data files as they are now, and only a change of the data is a change.
        """
        try:
            now = self.compute_data_analysis_recipe_keys(data_analysis_recipe_id, loaded=pinned)
        except RecipeLoadError as exc:
            return InputsChanged(f"the data analysis recipe can no longer be read ({str(exc).strip()[:200]})")
        except FileNotFoundError:
            return InputsChanged("the data analysis recipe file is gone")
        if now.tier1_key_of(collection_id) == built_from.tier1_key_of(collection_id):
            return None
        if now.data_analysis_recipe_sha256 != built_from.data_analysis_recipe_sha256:
            return InputsChanged("the data analysis recipe changed")
        if now.data_batch_hash != built_from.data_batch_hash:
            return InputsChanged("the data files changed")
        return InputsChanged("the processing rules changed")

    @staticmethod
    def tell_inputs_changed(change: InputsChanged, callback: Callable[[InputsChanged], None] | None) -> None:
        """The build says that its inputs changed while it ran: on the console, and to the caller that asked to be told."""
        print(f"[Orchestrator] ⚠ {change.text} while a table was being built; the table was returned but not stored")
        if callback is not None:
            callback(change)

    def materialize_tier1(self, data_analysis_recipe_id: str, collection_id: str, output_path: Path,
                          keys: DataAnalysisRecipeKeys | None = None,
                          on_inputs_changed: Callable[[InputsChanged], None] | None = None,
                          loaded: LoadedDataAnalysisRecipe | None = None) -> pl.LazyFrame:
        """
        Executes the full ingestion and assembly to create a Tier 1 Anchor.

        The anchor is reused only when the chained key stored in its metadata matches the
        current one (ADR-089); never by file name alone.

        A table that is built is stored under the key of the files it was built from, never under `keys`: a view holds
        its keys while the recipe or the data change on disk, and `keys` then describe files that are no longer there
        (STALE-KEY-STORE-1). The built table is not stored at all when its inputs changed while it was built; it is still
        returned (it may mix the two states), and `on_inputs_changed` is called with what changed so that the caller can
        tell the user. Nothing is re-read or blocked here.

        `loaded` is a recipe the caller hands the build instead of the file (an audit copy, `cache_keys.loaded_from_resolved`, with the keys of that
        copy): the build then reads that recipe and is not stopped by the difference between it and the recipe file. The file of the original still
        names the recipe (its id, its data location). Without it nothing changes.
        """
        lf, _, _, change = self._materialize_tier1(data_analysis_recipe_id, collection_id, output_path, keys, loaded=loaded,
                                                   pinned=loaded is not None)
        if change is not None:
            self.tell_inputs_changed(change, on_inputs_changed)
        return lf

    def _materialize_tier1(self, data_analysis_recipe_id: str, collection_id: str, output_path: Path,
                           keys: DataAnalysisRecipeKeys | None, loaded: LoadedDataAnalysisRecipe | None = None, pinned: bool = False
                           ) -> tuple[pl.LazyFrame, str, DataAnalysisRecipeKeys | None, InputsChanged | None]:
        """(table, the Tier 1 key that table carries, the keys of the build or None when a stored table was served,
        what changed while it was built or None). `pinned`: `loaded` was handed in by the caller and is the recipe of the build (see `materialize_tier1`)."""
        import time
        _t_start = time.perf_counter()
        print(f"[Orchestrator] ▶ materialize_tier1 START — data_analysis_recipe='{data_analysis_recipe_id}', collection='{collection_id}'")

        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            raise FileNotFoundError(
                f"Data analysis recipe not found: {data_analysis_recipe_path}")

        # 1. Load Data Analysis Recipe (kept in memory while none of its files changed on disk)
        loaded = loaded or load_data_analysis_recipe(data_analysis_recipe_path)
        data_analysis_recipe = loaded.raw
        built_from = None
        if keys is None:
            keys = built_from = self.compute_data_analysis_recipe_keys(data_analysis_recipe_id, loaded=loaded)

        # No tier2 steps: T2 equals T1, so a Tier 2 file left from an earlier data analysis recipe would be a
        # false T2. It could never be served (its key would not match), but it must not stay.
        t2_file = tier2_path_for(output_path)
        if not tier2_steps(data_analysis_recipe, collection_id):
            t2_file.unlink(missing_ok=True)

        # Cheap validity check before any ingestion: the stored key must match the current one.
        # The key is read from the very file that is then scanned (a rename between the two would pair a key with the
        # content of another file).
        stored = read_anchor_if_key(output_path, TIER1_KEY_META, keys.tier1_key_of(collection_id))
        if stored is not None:
            print(f"[Orchestrator] ✅ Tier 1 anchor '{collection_id}' is valid (key match) → {output_path}")
            return stored, keys.tier1_key_of(collection_id), None, None

        # Tier 1 is rebuilt, so the Tier 2 stored on top of the old one is invalid by definition. The table that did not match
        # (another key, another cache version, an unreadable file) is removed now, at the moment it is found: a build that
        # then fails must not leave a table that a later change could serve (rules_verification_testing.md section 9).
        t2_file.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)

        # The key of what this build reads: the recipe object loaded above and the data files as they are now. `keys` may
        # be older than both (a view computes them once).
        built_from = built_from or self.compute_data_analysis_recipe_keys(data_analysis_recipe_id, loaded=loaded)
        built_key = built_from.tier1_key_of(collection_id)
        stored_key = {TIER1_KEY_META: built_key, CACHE_VERSION_META: ENGINE_CACHE_VERSION}
        verdict: list[InputsChanged] = []

        def unchanged() -> bool:
            change = self.inputs_changed(data_analysis_recipe_id, built_from, collection_id, pinned=loaded if pinned else None)
            if change is not None:
                verdict.append(change)
            return change is None

        # 2. Ingest and Wrangle Ingredients
        ingredients = {}
        all_schemas = {}
        all_schemas.update(data_analysis_recipe.get("data_schemas", {}))

        # Optional Metadata Support (ADR-014)
        if "metadata_schema" in data_analysis_recipe:
            all_schemas["metadata_schema"] = data_analysis_recipe["metadata_schema"]

        all_schemas.update(data_analysis_recipe.get("additional_datasets_schemas", {}))

        failures: dict[str, Exception] = {}
        for ds_id, ds_schema in all_schemas.items():
            try:
                ingredients[ds_id] = self.prepare_ingredient(ds_id, ds_schema, recipe_id=data_analysis_recipe_id, recipe=data_analysis_recipe)
            except Exception as e:
                # Kept, not dropped: a dataset the requested collection needs makes the build
                # fail below (issue #18). One the collection does not use only gets a console line.
                failures[ds_id] = e
                print(f"⚠️ Ingestion Error in '{ds_id}': {str(e)}")

        # 3. Resolve target — may be an assembly OR a bare data_schema
        collection_spec = data_analysis_recipe.get("joins", {}).get(collection_id)

        needed = (
            [i.get("dataset_id") if isinstance(i, dict) else i for i in collection_spec.get("ingredients", [])]
            if collection_spec is not None else [collection_id]
        )
        broken = [(ds, failures[ds]) for ds in needed if ds in failures]
        if broken:
            ds, error = broken[0]
            others = f" (and {len(broken) - 1} more: {', '.join(d for d, _ in broken[1:])})" if len(broken) > 1 else ""
            raise IngestionError(
                f"Dataset '{ds}' could not be loaded for '{collection_id}'{others}: {error}",
                tip=getattr(error, "tip", None) or "Check the file and the input_fields of this dataset in the data analysis recipe.",
            )

        # Path A: bare data_schema / additional_dataset / metadata_schema
        # (e.g. a plot's target_dataset points directly to a source schema). Its T1 is stored here; its own tier-2
        # list is its T2, built by materialize_tier2 (issue #77).
        if collection_spec is None and collection_id in ingredients:
            print(f"      └── 💾 Materializing data_schema '{collection_id}' to: {output_path}")
            lf = ingredients[collection_id]
            stored = write_anchor(lf, str(output_path), decision_hash=built_key, metadata=stored_key, still_valid=unchanged)
            print(f"[Orchestrator] ✅ materialize_tier1 DONE — '{collection_id}' (bare schema) in {time.perf_counter()-_t_start:.2f}s → {output_path}")
            return stored, built_key, built_from, (verdict[0] if verdict else None)

        # Path B: the id is neither a join nor a schema of this recipe. It fails: building another collection in its
        # place (the first join, as the code did before) gives a table that looks right and is something else.
        if collection_spec is None:
            known = sorted(list(data_analysis_recipe.get("joins", {}) or {}) + list(all_schemas))
            raise DataAnalysisRecipeError(
                f"No join or data schema '{collection_id}' in data analysis recipe '{data_analysis_recipe_id}'. "
                f"Known: {', '.join(known) or 'none'}.")

        # Path C: assembly — ordered ingredient dict so DataAssembler starts
        # from the correct base (first declared ingredient, not first dict key)
        engine = data_entry(data_analysis_recipe, collection_spec, "tier1", where=f"The tier1 of the join '{collection_id}'")
        steps = engine.wrangler.tier_steps(collection_spec, "tier1")

        ingredient_ids = [
            item.get("dataset_id") if isinstance(item, dict) else item
            for item in collection_spec.get("ingredients", [])
            if (item.get("dataset_id") if isinstance(item, dict) else item)
        ]
        unknown = [ds_id for ds_id in ingredient_ids if ds_id not in ingredients]
        if unknown or not ingredient_ids:
            what = f"names {', '.join(repr(u) for u in unknown)}, which is not a data schema of this recipe" if unknown else "has no ingredients"
            raise DataAnalysisRecipeError(
                f"The join '{collection_id}' of data analysis recipe '{data_analysis_recipe_id}' {what}. "
                f"Data schemas: {', '.join(sorted(all_schemas)) or 'none'}.")
        assembly_ingredients = {ds_id: ingredients[ds_id] for ds_id in ingredient_ids}

        # A step that names an ingredient the join does not hold fails in the assembler; no step is skipped.
        assembler = engine.assembler(assembly_ingredients, recipe_id=data_analysis_recipe_id, join_id=collection_id)
        lf = assembler.assemble(steps)

        # ADR-101: the Tier 1 key of THIS table (its definition and that of what it reads, the data files it reads, the engine and
        # its version) is written into the anchor, so a change in any of them rebuilds it and a change elsewhere does not.
        lf = write_anchor(lf, str(output_path), decision_hash=built_key, metadata=stored_key,
                          join_checks=assembler.join_checks, still_valid=unchanged)

        print(f"[Orchestrator] ✅ materialize_tier1 DONE — assembly '{collection_id}' in {time.perf_counter()-_t_start:.2f}s → {output_path}")
        return lf, built_key, built_from, (verdict[0] if verdict else None)

    def materialize_tier2(self, data_analysis_recipe_id: str, collection_id: str, tier1_path: Path,
                          keys: DataAnalysisRecipeKeys | None = None,
                          on_inputs_changed: Callable[[InputsChanged], None] | None = None,
                          loaded: LoadedDataAnalysisRecipe | None = None, tier2_path: Path | None = None) -> pl.LazyFrame:
        """The Tier 2 data of one collection, read from its stored parquet (ADR-089 point 6, issue #10).

        A collection is a join or a schema that a plot reads directly; its tier-2 list is `tier2_steps` (one reading,
        `utils.recipe_tiers`, issue #77).

        - no tier2 steps: T2 equals T1, nothing is stored, the Tier 1 frame is returned;
        - stored file whose key matches: read, nothing is recomputed;
        - missing or mismatched file: recomputed from the (valid) Tier 1 and stored with its key.

        The key starts with the Tier 1 key of the table, so a change in a Tier 1 part invalidates Tier 2 as well,
        while a change in a Tier 2 step recomputes only Tier 2 (the Tier 1 file is only checked).

        A table built while its inputs changed is returned, not stored, and `on_inputs_changed` is called with what
        changed (see `materialize_tier1`).

        `loaded`: the recipe of the build when the caller hands one in (an audit copy, see `materialize_tier1`). `tier2_path`: where the Tier 2
        table is stored when it is not next to the Tier 1 table (an audit copy reads a Tier 1 table that its original stored, and stores its own Tier 2
        in its own folder); without it the Tier 2 table is `tier2_path_for(tier1_path)`, as always.
        """
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        pinned = loaded is not None
        loaded = loaded or load_data_analysis_recipe(data_analysis_recipe_path)
        keys = keys or self.compute_data_analysis_recipe_keys(data_analysis_recipe_id, loaded=loaded)
        steps = tier2_steps(loaded.raw, collection_id)
        t2_path = Path(tier2_path) if tier2_path is not None else tier2_path_for(tier1_path)
        # The engine of the tier is chosen before anything is built, also when it has no steps: a tier that names an engine this
        # app has no library for is refused, never skipped (D-0050).
        engine = data_entry(loaded.raw, collection_body(loaded.raw, collection_id), "tier2", where=f"The tier2 of '{collection_id}'")

        if not steps:
            # materialize_tier1 also removes a Tier 2 file left from an earlier data analysis recipe.
            lf, _, _, change = self._materialize_tier1(data_analysis_recipe_id, collection_id, tier1_path, keys, loaded=loaded, pinned=pinned)
            if change is not None:
                self.tell_inputs_changed(change, on_inputs_changed)
            return lf

        key = collection_tier2_key(loaded.raw, collection_id, keys.tier1_key_of(collection_id))
        stored = read_anchor_if_key(t2_path, TIER2_KEY_META, key)
        if stored is not None:
            print(f"[Orchestrator] ✅ Tier 2 '{collection_id}' is valid (key match) → {t2_path}")
            return stored
        t2_path.unlink(missing_ok=True)   # not the table of this key: removed when found, as Tier 1 (see `_materialize_tier1`)

        lf_t1, t1_key, t1_built_from, t1_change = self._materialize_tier1(
            data_analysis_recipe_id, collection_id, tier1_path, keys, loaded=loaded, pinned=pinned)
        verdict: list[InputsChanged] = [t1_change] if t1_change is not None else []
        # The chain is that of the Tier 1 table this one is computed from: a Tier 1 built just now carries the key of the
        # files it was built from, which can differ from `keys` (STALE-KEY-STORE-1).
        key = collection_tier2_key(loaded.raw, collection_id, t1_key)
        engine_now = tier2_engine(loaded.raw, collection_id)

        def unchanged() -> bool:
            # A Tier 1 that was itself built from changed inputs makes this table a mix too: nothing to store.
            if t1_change is not None:
                return False
            if t1_built_from is not None:
                change = self.inputs_changed(data_analysis_recipe_id, t1_built_from, collection_id, pinned=loaded if pinned else None)
                if change is not None:
                    verdict.append(change)
                    return False
            try:
                raw_now = loaded.raw if pinned else load_data_analysis_recipe(data_analysis_recipe_path).raw
                steps_now = tier2_steps(raw_now, collection_id)
                engine_then = tier2_engine(raw_now, collection_id)
            except RecipeLoadError as exc:
                verdict.append(InputsChanged(f"the data analysis recipe can no longer be read ({str(exc).strip()[:200]})"))
                return False
            except FileNotFoundError:
                verdict.append(InputsChanged("the data analysis recipe file is gone"))
                return False
            if steps_now != steps or engine_then != engine_now:
                verdict.append(InputsChanged("the tier-2 steps of this table changed"))
                return False
            return True

        # A copy: the dicts belong to the data analysis recipe kept in memory and the key of the next read must match.
        lf_t2 = engine.wrangler().run(lf_t1, copy.deepcopy(steps))
        print(f"[Orchestrator] ▶ Tier 2 '{collection_id}' recomputed from Tier 1 → {t2_path}")
        table = write_anchor(lf_t2, str(t2_path), decision_hash=key,
                              metadata={TIER2_KEY_META: key, CACHE_VERSION_META: ENGINE_CACHE_VERSION}, still_valid=unchanged)
        if verdict:
            self.tell_inputs_changed(verdict[0], on_inputs_changed)
        return table

    def materialize_tier3(self, data_analysis_recipe_id: str, plot_id: str, anchors_dir: Path,
                          keys: DataAnalysisRecipeKeys | None = None,
                          on_inputs_changed: Callable[[InputsChanged], None] | None = None,
                          loaded: LoadedDataAnalysisRecipe | None = None, tier2_path: Path | None = None) -> pl.LazyFrame:
        """The table one plot reads: the Tier 2 of its target (Tier 1 when the target has no tier-2 steps) with the plot's own
        `tier3` steps applied (DEC17, ADR-101). PROVISIONAL name: the specification leaves the name and place of the reader open
        (`recipe_format_spec.md`, "Who reads tier3").

        The one reader of a plot's data: HOME's plot and its My view table, the export, the pictures and the baselines read this table, so
        a plot equals its table. The key of the table is `DataAnalysisRecipeKeys.plot_key_of(plot_id)`.

        - no tier-3 steps: the plot reads its table as it is: the frame of `materialize_tier2` is returned (same key, nothing built or
          stored twice);
        - tier-3 steps: applied, in order, by the data engine of the tier (`data_engine` of the `tier3`, else the recipe's) through
          the same step runner as the other tiers, on a LAZY frame over the stored table. PROVISIONAL: nothing is stored for it (the
          design files leave "stored or derived on demand" open, `home_audit_steps.md` point 15), so the key names the table but no
          file carries it. Every step is checked as it is added (the column names and types it needs): a step that cannot be applied
          raises, naming the plot and the step. A failure that depends on the values (a cast of a value that does not fit) can only
          show when the table is read, and then it is the engine's own error: it names neither the step nor the plot. The consumers
          that read the table and already catch errors (HOME's plot and data preview) add the plot's name with `plot_read_error_text`;
          the step is not named there (the engine's message names the column and the values, not the number of the step).

        `anchors_dir` is the folder of the stored tables: the target is stored as `<anchors_dir>/<target>.parquet`.

        `loaded` and `tier2_path` are for an audit copy: the recipe of the build when the caller hands one in, and where the Tier 2 table of the target is
        when it is not next to its Tier 1 table (see `materialize_tier2`). Without them nothing changes.
        """
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        handed = loaded
        loaded = loaded or load_data_analysis_recipe(data_analysis_recipe_path)
        entry = plot_entry(loaded.raw, plot_id)
        if entry is None:
            raise DataAnalysisRecipeError(f"The data analysis recipe '{data_analysis_recipe_id}' has no plot '{plot_id}'.")
        target = entry.get("target_dataset")
        if not target:
            raise DataAnalysisRecipeError(f"The plot '{plot_id}' of '{data_analysis_recipe_id}' names no target_dataset, so it has no table.")
        # The engine of the tier is chosen before anything is built, also when it has no steps: an engine this app has no library for
        # is refused, never skipped (D-0050), as for the other tiers.
        engine = data_entry(loaded.raw, entry, "tier3", where=f"The tier3 of the plot '{plot_id}'")
        steps = tier3_steps(loaded.raw, plot_id)
        lf = self.materialize_tier2(data_analysis_recipe_id, target, Path(anchors_dir) / f"{target}.parquet",
                                    keys=keys, on_inputs_changed=on_inputs_changed, loaded=handed, tier2_path=tier2_path)
        if not steps:
            return lf
        runner = engine.wrangler()
        for number, step in enumerate(steps, start=1):
            action = step.get("action") if isinstance(step, dict) else None
            try:
                # A copy: the dicts belong to the recipe kept in memory. One step at a time through the same runner, then the
                # schema is read so that a missing column or a wrong type shows here and not at the first read of the table.
                lf = runner.run(lf, [copy.deepcopy(step)])
                lf.collect_schema()
            except Exception as exc:
                why = (f"{exc}" + (f" ({exc.tip})" if isinstance(exc, SPARMVET_Error) and getattr(exc, 'tip', None) else "")).strip()
                raise TransformationError(
                    f"The tier 3 of the plot '{plot_id}' cannot be applied: step {number} ('{action}') failed: {why}",
                    tip=f"Correct or remove step {number} of the tier3 of the plot '{plot_id}' in the data analysis recipe '{data_analysis_recipe_id}'.") from exc
        return lf

    def dataset_schemas(self, data_analysis_recipe_id: str) -> dict[str, Any]:
        """{dataset_id: schema} of every dataset a recipe names (data schemas, metadata, additional datasets)."""
        path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not path.exists():
            return {}
        return self._schemas_of(load_data_analysis_recipe(path).raw)

    @staticmethod
    def _schemas_of(recipe: dict) -> dict[str, Any]:
        """{dataset_id: schema} of a recipe mapping: data schemas, metadata, additional datasets."""
        schemas: dict[str, Any] = {}
        schemas.update(recipe.get("data_schemas", {}))
        if "metadata_schema" in recipe:
            schemas["metadata_schema"] = recipe["metadata_schema"]
        schemas.update(recipe.get("additional_datasets_schemas", {}))
        return schemas

    def get_source_files(self, data_analysis_recipe_id: str) -> dict[str, Path]:
        """Return {dataset_id: resolved_path} for all source files in a data analysis recipe.

        Used by SessionManager.compute_data_batch_hash to detect input file changes. The paths are the files
        `prepare_ingredient` reads (`locate_dataset_file`), nothing else. A dataset with no file is left out.
        """
        result: dict[str, Path] = {}
        for ds_id, ds_schema in self.dataset_schemas(data_analysis_recipe_id).items():
            located = self.locate_dataset_file(data_analysis_recipe_id, ds_id, ds_schema)
            if located is not None:
                result[ds_id] = located
        return result
