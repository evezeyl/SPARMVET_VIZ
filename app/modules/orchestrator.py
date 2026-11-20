# @deps
# provides: pipeline:materialize_tier1, pipeline:materialize_tier2, pipeline:materialize_tier3 (stores the table of a plot with tier-3 steps by its key, D-0343), function:tier3_path_for, constant:TIER3_KEY_META, function:plot_read_error_text, method:prepare_ingredient, method:read_source, method:locate_dataset_file, method:get_source_files, function:compute_data_analysis_recipe_keys, method:_plot_key_now (the key of the table of a plot now, reading only the data files that table reads: the last check of a Tier 3 store)
# mirrors: libs/transformer/tests/debug_assembler.py
# consumes: app/modules/build_failure.py (the plain error of a build that failed: table, tier, step), libs/ingestion/src/ingestion/ingestor.py, libs/utils/src/utils/recipe_tiers.py (collection_body, audit_step_places), app/modules/engine_registry.py (data_entry: the engine that runs a tier, D-0219), libs/utils/src/utils/recipe_tiers.py (plot_entry, tier3_steps), libs/transformer/src/transformer/anchor.py, app/modules/cache_keys.py (collection_tier2_key: the one place that makes the tier-2 key; ENGINE_CACHE_VERSION: the mark written into each stored table; DataAnalysisRecipeKeys.tier1_key_of: the key of each stored table, ADR-101; dataset_file_hashes)
# consumed_by: app/modules/opening_build.py (materialize_tier1/2/3: the opening of a recipe), app/tests/test_read_source.py (read_source: one source table as the ingestion reads it, for the Source view of HOME, D-0310), app/src/server.py, app/handlers/home_theater.py (materialize_tier3: the plot and T3 table base; plot_read_error_text: the plot name on a read failure), app/handlers/export_handlers.py (materialize_tier3), app/modules/gallery_examples.py, assets/scripts/golden_baseline.py, assets/scripts/recipe_pictures.py, app/handlers/blueprint_handlers.py, app/modules/bundle_importer.py, app/modules/data_analysis_recipe_validator.py, app/tests/test_tier3_store.py, app/tests/test_build_failure_names.py, app/modules/audit_run.py (materialize_tier1/2/3 with a handed recipe: the audit copy)
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
from app.modules.build_failure import computed_failure, first_failing_step, step_failure_error, table_failure_error
from utils.recipe_tiers import audit_step_places, collection_body, plot_entry
from app.modules.cache_keys import (CACHE_VERSION_META, DataAnalysisRecipeKeys, ENGINE_CACHE_VERSION, LoadedDataAnalysisRecipe, collection_tier2_key,
                                    data_analysis_recipe_keys, dataset_file_hashes, load_data_analysis_recipe, plot_tier3_key, tier2_engine, tier2_steps, tier3_steps)

# Parquet metadata key holding the Tier 1 key of the table (ADR-089, ADR-101: a key per table).
TIER1_KEY_META = "sparmvet_tier1_key"
# Parquet metadata key holding the Tier 2 key of the table (ADR-089 point 6, ADR-101).
TIER2_KEY_META = "sparmvet_tier2_key"
# Parquet metadata key holding the Tier 3 key of the table of a plot that has tier-3 steps of its own (D-0343).
TIER3_KEY_META = "sparmvet_tier3_key"


def tier2_path_for(tier1_path: Path) -> Path:
    """Where the Tier 2 parquet of a join lives: next to its Tier 1 parquet, `<name>__T2.parquet`."""
    tier1_path = Path(tier1_path)
    return tier1_path.with_name(f"{tier1_path.stem}__T2{tier1_path.suffix}")


def tier3_path_for(folder: Path, target: str, plot_id: str) -> Path:
    """Where the Tier 3 parquet of a plot lives: `<target>__T3_<plot id>.parquet` in the folder of the stored tables. Only a plot with tier-3
    steps of its own has one; a plot without reads the Tier 2 of its target and stores nothing (T3 = T2, D-0343)."""
    return Path(folder) / f"{target}__T3_{plot_id}.parquet"


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


def refuse_audit_steps_outside_an_audit(loaded: LoadedDataAnalysisRecipe, recipe_id: str) -> None:
    """The engine's own refusal (D-0332), asked before any table or plot is built from `loaded`.

    A recipe that is not an audit copy and holds an `audit_steps` key anywhere (even empty, even where no tier reads it) is not run, with a plain error that says
    where. An audit copy is run only when it is the original plus sound audit steps: `utils.audit_copy.integrity_errors` against the recipe it was made from
    (`ResolvedRecipe.original_raw`, set by `loaded_from_resolved`), so a caller that builds a copy by hand and goes to `materialize_*` directly meets the same
    refusals as `run_audit` (an action that is not allowed, a missing reason, a dropped key column, an `audit_steps` that is not a list at any tier). A copy built
    without its original is refused. The checker refuses an audit key when a recipe is loaded from a file (profile run); this reads what the build holds."""
    places = audit_step_places(loaded.raw)
    if not loaded.is_audit_copy:
        if places:
            raise DataAnalysisRecipeError(
                f"The data analysis recipe '{recipe_id}' has audit steps at {', '.join(places)}, and it is not an audit recipe: only an audit recipe has audit steps.",
                tip="Remove the audit_steps lists; the steps of the author are written under steps.")
        return
    problems = loaded.config.integrity_problems()
    if problems:
        raise DataAnalysisRecipeError(
            f"The audit copy of '{recipe_id}' is not the original plus sound audit steps, so it is not run: " + " ".join(problems),
            tip="Add the audit steps only through the audit (add_step), never by hand.")


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

    def _plot_key_now(self, data_analysis_recipe_id: str, plot_id: str) -> str:
        """The key of the table a plot reads, as the recipe and the data are now, reading only the data files that table depends on.

        The last check of a Tier 3 store (`materialize_tier3`) asks this once per stored table. The key of a table is made from the files that table
        reads (`TableKeyParts.datasets`, ADR-101), so a file the table does not read cannot change the key: it is not read. A table whose key is the coarse
        fail-safe form (every file) reads every file. Raises what `compute_data_analysis_recipe_keys` raises (the recipe cannot be read, the file is gone)
        and `KeyError` when the recipe has no such plot."""
        path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Data analysis recipe not found: {path}")
        loaded = load_data_analysis_recipe(path)
        entry = plot_entry(loaded.raw, plot_id)
        parts = loaded.table_parts.get(entry.get("target_dataset")) if entry else None
        files = self.get_source_files(data_analysis_recipe_id)
        if parts is not None and not parts.coarse:
            files = {ds: files[ds] for ds in parts.datasets if ds in files}
        return data_analysis_recipe_keys(loaded, dataset_file_hashes(files)).plot_key_of(plot_id)

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

    def prepare_ingredient(self, ds_id: str, ds_schema: dict, recipe_id: str | None = None, recipe: dict | None = None, audit: bool = False) -> pl.LazyFrame:
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
        rules = engine.wrangler.tier_steps(ds_schema, "tier1", audit=audit)
        return engine.wrangler().run(lf, rules)

    # PROVISIONAL name (the coordinator's, owner's question P-B7): read_source
    def read_source(self, data_analysis_recipe_id: str, dataset_id: str, loaded: LoadedDataAnalysisRecipe | None = None) -> pl.LazyFrame:
        """One source table of a recipe as the ingestion reads it, with its declared types, before any tier-1 step (the Source view of HOME,
        D-0310). The same read as the tier-1 build (`_read_source`).

        What is true: the CALL reads the file once to validate it, as the tier-1 build does (a missing file, an empty file, a missing declared
        column or a value that does not fit its type raise here, not at `.collect()`); the returned frame is a lazy scan of the file, so the
        rows are read again when it is collected. Nothing is written to disk and no key is touched. It is not free: it costs one read of the file.
        `loaded` is a pinned recipe (an audit copy), as in `materialize_tier1`: the table is then the one of the pinned text, and the recipe
        file need not exist. It goes through the same guard as the builds (`refuse_audit_steps_outside_an_audit`): an audit copy that is not the original
        plus sound audit steps is refused with the same plain error, and so is an `audit_steps` list in a recipe that is not an audit copy.

        Raises FileNotFoundError for a recipe that has no file (and none handed in), DataAnalysisRecipeError for a table id the recipe does not
        name, and IngestionError ("Source table 'X' could not be read: ...") when the file cannot be read; it is the kind of error the tier-1 build
        gives. IngestionError has no subclass today, so the re-raise loses none; the ingestion's PipelineError is carried over."""
        path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if loaded is None and not path.exists():
            raise FileNotFoundError(f"Data analysis recipe not found: {path}")
        loaded = loaded or load_data_analysis_recipe(path)
        # the same guard as every build: a source table read through an audit copy that is not sound, or through a recipe that is not an audit copy but holds
        # `audit_steps`, is refused (the Source view shows what a build would read, so it is held to the same form)
        refuse_audit_steps_outside_an_audit(loaded, data_analysis_recipe_id)
        schemas = self._schemas_of(loaded.raw)
        if dataset_id not in schemas:
            raise DataAnalysisRecipeError(
                f"No source table '{dataset_id}' in data analysis recipe '{data_analysis_recipe_id}'. Known: {', '.join(sorted(schemas)) or 'none'}.")
        try:
            lf, _ = self._read_source(dataset_id, schemas[dataset_id], data_analysis_recipe_id)
        except IngestionError as error:
            # The same kind of error as the tier-1 build ("Dataset 'X' could not be loaded ..."), naming the table and the reason.
            raise IngestionError(f"Source table '{dataset_id}' could not be read: {error}",
                                 tip=getattr(error, "tip", None) or "Check the file and the input_fields of this table in the data analysis recipe.",
                                 pipeline_error=getattr(error, "pipeline_error", None)) from error
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

    def _explain_table_failure(self, exc: BaseException, recipe_id: str, loaded: LoadedDataAnalysisRecipe, table_id: str, schema: dict):
        """The plain error for a source table (or a bare table a plot reads) whose tier-1 steps failed when the table was computed: the table, the
        tier and the first step that fails, found by running the steps again a prefix at a time (`build_failure`). Without a step: the table and
        the engine's sentence. Only runs after a failure."""
        where = f"The tier 1 of the table '{table_id}'"
        tip = f"Correct the step the message names, or the values of the column it reads in the data, in the table '{table_id}' of the data analysis recipe '{recipe_id}'."
        try:
            engine = data_entry(loaded.raw, schema, "tier1", where=where)
            steps = engine.wrangler.tier_steps(schema, "tier1", audit=loaded.is_audit_copy)
            source, _ = self._read_source(table_id, schema, recipe_id)
            found = first_failing_step(lambda k: engine.wrangler().run(source, copy.deepcopy(steps[:k])), len(steps))
        except Exception:
            found = None
            steps = []
        if found is None:
            return table_failure_error(where, exc, tip)
        return step_failure_error(where, steps, found[0], found[1], tip)

    def _explain_join_failure(self, exc: BaseException, recipe_id: str, loaded: LoadedDataAnalysisRecipe, join_id: str, spec: dict, engine,
                              steps: list, ingredient_ids: list, ingredients: dict, all_schemas: dict):
        """The plain error for a join whose tier 1 failed when the table was computed. A source table that fails on its own is named first (its
        table and step); else the first step of the join that fails. Only runs after a failure."""
        for ds_id in ingredient_ids:
            if computed_failure(ingredients[ds_id]) is not None:
                return self._explain_table_failure(exc, recipe_id, loaded, ds_id, all_schemas[ds_id])
        where = f"The tier 1 of the join '{join_id}'"
        tip = f"Correct the step the message names, or the values of the column it reads in the data, in the join '{join_id}' of the data analysis recipe '{recipe_id}'."
        try:
            held = {ds_id: ingredients[ds_id] for ds_id in ingredient_ids}
            found = first_failing_step(
                lambda k: engine.assembler(held, recipe_id=recipe_id, join_id=join_id).assemble(copy.deepcopy(steps[:k])), len(steps))
        except Exception:
            found = None
        if found is None:
            return table_failure_error(where, exc, tip)
        return step_failure_error(where, steps, found[0], found[1], tip)

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
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            raise FileNotFoundError(
                f"Data analysis recipe not found: {data_analysis_recipe_path}")

        # 1. Load Data Analysis Recipe (kept in memory while none of its files changed on disk)
        loaded = loaded or load_data_analysis_recipe(data_analysis_recipe_path)
        refuse_audit_steps_outside_an_audit(loaded, data_analysis_recipe_id)
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

        # HOME-WALK H: the START line is for a build only; a read of a stored table is one line (the line above). It was printed before the check, so
        # that every look at a stored table (a plot tab, a data choice, a mode) wrote two lines and the log of one session held about 450 of them.
        print(f"[Orchestrator] ▶ materialize_tier1 START — data_analysis_recipe='{data_analysis_recipe_id}', collection='{collection_id}'")

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

        # 3. Resolve target — may be an assembly OR a bare data_schema
        collection_spec = data_analysis_recipe.get("joins", {}).get(collection_id)

        needed = (
            [i.get("dataset_id") if isinstance(i, dict) else i for i in collection_spec.get("ingredients", [])]
            if collection_spec is not None else [collection_id]
        )

        # Only the tables this collection reads are read and run: a build used to read every source table of the recipe, for every table it built
        # (SPEED-TABLE-BUILD-READS-ALL-SOURCES, measured on the demo recipe: 17 tables, 12 sources read each time). A table the collection does not
        # read cannot change it, and the load gate checks every table of the recipe at the start.
        failures: dict[str, Exception] = {}
        for ds_id in dict.fromkeys(ds for ds in needed if ds in all_schemas):
            try:
                ingredients[ds_id] = self.prepare_ingredient(ds_id, all_schemas[ds_id], recipe_id=data_analysis_recipe_id, recipe=data_analysis_recipe,
                                                             audit=loaded.is_audit_copy)
            except Exception as e:
                # Kept, not dropped: the collection reads this table, so the build fails below (issue #18).
                failures[ds_id] = e
                print(f"⚠️ Ingestion Error in '{ds_id}': {str(e)}")

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
            try:
                stored = write_anchor(lf, str(output_path), decision_hash=built_key, metadata=stored_key, still_valid=unchanged)
            except pl.exceptions.PolarsError as exc:
                raise self._explain_table_failure(exc, data_analysis_recipe_id, loaded, collection_id, all_schemas[collection_id]) from exc
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
        steps = engine.wrangler.tier_steps(collection_spec, "tier1", audit=loaded.is_audit_copy)

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
        try:
            lf = write_anchor(lf, str(output_path), decision_hash=built_key, metadata=stored_key,
                              join_checks=assembler.join_checks, still_valid=unchanged)
        except pl.exceptions.PolarsError as exc:
            raise self._explain_join_failure(exc, data_analysis_recipe_id, loaded, collection_id, collection_spec, engine, steps,
                                             ingredient_ids, ingredients, all_schemas) from exc

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
        lf, _, change = self._materialize_tier2(data_analysis_recipe_id, collection_id, tier1_path, keys, loaded, tier2_path)
        if change is not None:
            self.tell_inputs_changed(change, on_inputs_changed)
        return lf

    def _materialize_tier2(self, data_analysis_recipe_id: str, collection_id: str, tier1_path: Path,
                           keys: DataAnalysisRecipeKeys | None, loaded: LoadedDataAnalysisRecipe | None, tier2_path: Path | None
                           ) -> tuple[pl.LazyFrame, str, InputsChanged | None]:
        """(the table, the key that table carries, what changed while it was built or None). The key is that of the files the table was built
        from, which can differ from `keys` (STALE-KEY-STORE-1): the Tier 3 table of a plot is keyed from it."""
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        pinned = loaded is not None
        loaded = loaded or load_data_analysis_recipe(data_analysis_recipe_path)
        refuse_audit_steps_outside_an_audit(loaded, data_analysis_recipe_id)
        keys = keys or self.compute_data_analysis_recipe_keys(data_analysis_recipe_id, loaded=loaded)
        steps = tier2_steps(loaded.raw, collection_id)
        t2_path = Path(tier2_path) if tier2_path is not None else tier2_path_for(tier1_path)
        # The engine of the tier is chosen before anything is built, also when it has no steps: a tier that names an engine this app has no library for
        # is refused, never skipped (D-0050).
        engine = data_entry(loaded.raw, collection_body(loaded.raw, collection_id), "tier2", where=f"The tier2 of '{collection_id}'")

        if not steps:
            # materialize_tier1 also removes a Tier 2 file left from an earlier data analysis recipe.
            lf, t1_key, _, change = self._materialize_tier1(data_analysis_recipe_id, collection_id, tier1_path, keys, loaded=loaded, pinned=pinned)
            return lf, collection_tier2_key(loaded.raw, collection_id, t1_key), change

        key = collection_tier2_key(loaded.raw, collection_id, keys.tier1_key_of(collection_id))
        stored = read_anchor_if_key(t2_path, TIER2_KEY_META, key)
        if stored is not None:
            print(f"[Orchestrator] ✅ Tier 2 '{collection_id}' is valid (key match) → {t2_path}")
            return stored, key, None
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
        try:
            table = write_anchor(lf_t2, str(t2_path), decision_hash=key,
                                 metadata={TIER2_KEY_META: key, CACHE_VERSION_META: ENGINE_CACHE_VERSION}, still_valid=unchanged)
        except pl.exceptions.PolarsError as exc:
            where = f"The tier 2 of the table '{collection_id}'"
            tip = f"Correct the step the message names, or the values of the column it reads in the data, in the tier 2 of '{collection_id}' of the data analysis recipe '{data_analysis_recipe_id}'."
            try:
                found = first_failing_step(lambda k: engine.wrangler().run(lf_t1, copy.deepcopy(steps[:k])), len(steps))
            except Exception:
                found = None
            raise (table_failure_error(where, exc, tip) if found is None else step_failure_error(where, steps, found[0], found[1], tip)) from exc
        return table, key, (verdict[0] if verdict else None)

    def materialize_tier3(self, data_analysis_recipe_id: str, plot_id: str, anchors_dir: Path,
                          keys: DataAnalysisRecipeKeys | None = None,
                          on_inputs_changed: Callable[[InputsChanged], None] | None = None,
                          loaded: LoadedDataAnalysisRecipe | None = None, tier2_path: Path | None = None) -> pl.LazyFrame:
        """The table one plot reads: the Tier 2 of its target (Tier 1 when the target has no tier-2 steps) with the plot's own
        `tier3` steps applied (DEC17, ADR-101). PROVISIONAL name: the specification leaves the name and place of the reader open
        (`recipe_format_spec.md`, "Who reads tier3").

        The one reader of a plot's data: HOME's plot and its T3 table, the export, the pictures and the baselines read this table, so
        a plot equals its table. The key of the table is `DataAnalysisRecipeKeys.plot_key_of(plot_id)`.

        - no tier-3 steps: the plot reads its table as it is: the frame of `materialize_tier2` is returned (same key, nothing built or
          stored twice, D-0343: T3 = T2);
        - tier-3 steps: the table is stored by its key next to the Tier 2 table of the target (`tier3_path_for`, D-0343) and read from there while
          the key matches; else the steps are applied, in order, by the data engine of the tier (`data_engine` of the `tier3`, else the
          recipe's) through the same step runner as the other tiers, on a LAZY frame over the stored Tier 2 table, and the result is
          stored. A table built while its inputs changed is returned and not stored, as for the other tiers. Every step is checked as
          it is added (the column names and types it needs): a step that cannot be applied raises, naming the plot and the step. A
          failure that depends on the values (a cast of a value that does not fit) shows when the table is stored; it is then named
          by the step, as for the Tier 2 (`build_failure`). The consumers that read the table and already catch errors (HOME's plot and
          data preview) add the plot's name with `plot_read_error_text`.

        `anchors_dir` is the folder of the stored tables: the target is stored as `<anchors_dir>/<target>.parquet`.

        `loaded` and `tier2_path` are for an audit copy: the recipe of the build when the caller hands one in, and where the Tier 2 table of the target is
        when it is not next to its Tier 1 table (see `materialize_tier2`). A recipe that is handed in has its Tier 3 table computed and stored nowhere (PROVISIONAL, see
        the comment below); without them the table is stored.
        """
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        handed = loaded
        loaded = loaded or load_data_analysis_recipe(data_analysis_recipe_path)
        refuse_audit_steps_outside_an_audit(loaded, data_analysis_recipe_id)
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
        keys = keys or self.compute_data_analysis_recipe_keys(data_analysis_recipe_id, loaded=loaded)
        lf, t2_key, change = self._materialize_tier2(data_analysis_recipe_id, target, Path(anchors_dir) / f"{target}.parquet", keys, handed, tier2_path)
        t3_path = tier3_path_for(Path(tier2_path).parent if tier2_path is not None else Path(anchors_dir), target, plot_id)
        if not steps:
            if handed is None:
                t3_path.unlink(missing_ok=True)   # the plot lost its tier-3 steps: the table it stored is not its table any more, removed when found
            if change is not None:
                self.tell_inputs_changed(change, on_inputs_changed)
            return lf
        t3_key = plot_tier3_key(loaded.raw, plot_id, t2_key)
        t2_frame = lf
        # PROVISIONAL (the audit copy keeps its own folder protocol, `audit_run`: it reads and removes the files it knows; a Tier 3 file is not one of
        # them and storing the Tier 3 of a copy is not decided): the Tier 3 table of a recipe that was handed in is computed lazily and stored nowhere.
        store = handed is None
        if store and change is None:
            stored = read_anchor_if_key(t3_path, TIER3_KEY_META, t3_key)
            if stored is not None:
                print(f"[Orchestrator] ✅ Tier 3 of the plot '{plot_id}' is valid (key match) → {t3_path}")
                return stored
        if store:
            t3_path.unlink(missing_ok=True)   # not the table of this key (or its inputs changed): removed when found, as the other tiers
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
        if change is not None:
            self.tell_inputs_changed(change, on_inputs_changed)
        if not store or change is not None:
            return lf

        verdict: list[InputsChanged] = []

        def unchanged() -> bool:
            # The Tier 2 table it reads was stored under its key; what can change while this one is computed is the data, the recipe and its own steps.
            try:
                same = self._plot_key_now(data_analysis_recipe_id, plot_id) == t3_key
            except RecipeLoadError as exc:
                verdict.append(InputsChanged(f"the data analysis recipe can no longer be read ({str(exc).strip()[:200]})"))
                return False
            except FileNotFoundError:
                verdict.append(InputsChanged("the data analysis recipe file is gone"))
                return False
            except KeyError:
                same = False
            if not same:
                verdict.append(InputsChanged("the data analysis recipe or the data files changed"))
            return same

        print(f"[Orchestrator] ▶ Tier 3 of the plot '{plot_id}' computed from its Tier 2 → {t3_path}")
        try:
            table = write_anchor(lf, str(t3_path), decision_hash=t3_key,
                                 metadata={TIER3_KEY_META: t3_key, CACHE_VERSION_META: ENGINE_CACHE_VERSION}, still_valid=unchanged)
        except pl.exceptions.PolarsError as exc:
            where = f"The tier 3 of the plot '{plot_id}'"
            tip = f"Correct the step the message names, or the values of the column it reads in the data, in the tier3 of the plot '{plot_id}' of the data analysis recipe '{data_analysis_recipe_id}'."

            def prefix(k: int) -> pl.LazyFrame:
                frame = t2_frame
                for step in steps[:k]:
                    frame = runner.run(frame, [copy.deepcopy(step)])
                return frame

            try:
                found = first_failing_step(prefix, len(steps))
            except Exception:
                found = None
            raise (table_failure_error(where, exc, tip) if found is None else step_failure_error(where, steps, found[0], found[1], tip)) from exc
        if verdict:
            self.tell_inputs_changed(verdict[0], on_inputs_changed)
        return table

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
