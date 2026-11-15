# @deps
# provides: pipeline:materialize_tier1, pipeline:materialize_tier2, method:prepare_ingredient, method:locate_dataset_file, method:get_source_files, function:compute_data_analysis_recipe_keys
# mirrors: libs/transformer/tests/debug_assembler.py
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/metadata_validator.py, app/modules/cache_keys.py
# consumed_by: app/src/server.py, app/handlers/home_theater.py, app/handlers/blueprint_handlers.py, app/modules/bundle_importer.py, app/modules/data_analysis_recipe_validator.py
# doc: .claude/knowledge/dependency_index.md
# @end_deps
import copy
import polars as pl
from pathlib import Path
from typing import Any
from utils.errors import DataAnalysisRecipeError, IngestionError
from utils.hashing import get_parquet_metadata_hash
from ingestion.ingestor import DataIngestor, find_dataset_file
from transformer.data_wrangler import DataWrangler
from transformer.data_assembler import DataAssembler
from transformer.anchor import write_anchor
from app.modules.cache_keys import DataAnalysisRecipeKeys, load_data_analysis_recipe, data_analysis_recipe_keys, tier2_key, tier2_steps

# Parquet metadata key holding the chained Tier 1 key (ADR-089).
TIER1_KEY_META = "sparmvet_tier1_key"
# Parquet metadata key holding the chained Tier 2 key (ADR-089 point 6).
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

    def compute_data_analysis_recipe_keys(self, data_analysis_recipe_id: str) -> DataAnalysisRecipeKeys:
        """The keys every stored stage of this project depends on (ADR-089).

        Reads the data files to hash their content, so callers compute it once per session
        and pass it to materialize_tier1().
        """
        from app.modules.session_manager import SessionManager
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            raise FileNotFoundError(f"Data analysis recipe not found: {data_analysis_recipe_path}")
        loaded = load_data_analysis_recipe(data_analysis_recipe_path)
        source_files = self.get_source_files(data_analysis_recipe_id)
        data_hash = SessionManager.compute_data_batch_hash(source_files) if source_files else ""
        return data_analysis_recipe_keys(loaded, data_hash)

    def prepare_ingredient(self, ds_id: str, ds_schema: dict, recipe_id: str | None = None) -> pl.LazyFrame:
        """Read one dataset of a data analysis recipe and apply its input contract and tier-1 wrangling (its T1).

        The schema's own tier-2 list is not run here: it is the T2 of the schema when a plot reads it directly, run by
        `materialize_tier2` like a join's (issue #77); a join reads the T1 of its ingredients.

        Raises when the file cannot be read, a declared input column is missing, or a value does
        not fit its declared type. Shared by materialize_tier1 and the data analysis recipe data check, so
        both see the dataset the same way. `recipe_id` selects the data folder of an imported recipe.

        The file read is the file `locate_dataset_file` names, the same one `get_source_files` hashes.
        """
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

        rules = DataWrangler._resolve_tier(ds_schema.get("wrangling", []), "tier1")
        return DataWrangler().run(lf, rules)

    def materialize_tier1(self, data_analysis_recipe_id: str, collection_id: str, output_path: Path,
                          keys: DataAnalysisRecipeKeys | None = None) -> pl.LazyFrame:
        """
        Executes the full ingestion and assembly to create a Tier 1 Anchor.

        The anchor is reused only when the chained key stored in its metadata matches the
        current one (ADR-089); never by file name alone.
        """
        import time
        _t_start = time.perf_counter()
        print(f"[Orchestrator] ▶ materialize_tier1 START — data_analysis_recipe='{data_analysis_recipe_id}', collection='{collection_id}'")

        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            raise FileNotFoundError(
                f"Data analysis recipe not found: {data_analysis_recipe_path}")

        # 1. Load Data Analysis Recipe (kept in memory while none of its files changed on disk)
        loaded = load_data_analysis_recipe(data_analysis_recipe_path)
        data_analysis_recipe = loaded.raw
        keys = keys or self.compute_data_analysis_recipe_keys(data_analysis_recipe_id)

        # No tier2 steps: T2 equals T1, so a Tier 2 file left from an earlier data analysis recipe would be a
        # false T2. It could never be served (its key would not match), but it must not stay.
        t2_file = tier2_path_for(output_path)
        if not tier2_steps(data_analysis_recipe, collection_id):
            t2_file.unlink(missing_ok=True)

        # Cheap validity check before any ingestion: the stored key must match the current one.
        if Path(output_path).exists() and \
                get_parquet_metadata_hash(str(output_path), TIER1_KEY_META) == keys.tier1_key:
            print(f"[Orchestrator] ✅ Tier 1 anchor '{collection_id}' is valid (key match) → {output_path}")
            return pl.scan_parquet(output_path)

        # Tier 1 is rebuilt, so the Tier 2 stored on top of the old one is invalid by definition.
        t2_file.unlink(missing_ok=True)

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
                ingredients[ds_id] = self.prepare_ingredient(ds_id, ds_schema, recipe_id=data_analysis_recipe_id)
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
            write_anchor(lf, str(output_path), decision_hash=keys.tier1_key, metadata={TIER1_KEY_META: keys.tier1_key})
            print(f"[Orchestrator] ✅ materialize_tier1 DONE — '{collection_id}' (bare schema) in {time.perf_counter()-_t_start:.2f}s → {output_path}")
            return pl.scan_parquet(output_path)

        # Path B: the id is neither a join nor a schema of this recipe. It fails: building another collection in its
        # place (the first join, as the code did before) gives a table that looks right and is something else.
        if collection_spec is None:
            known = sorted(list(data_analysis_recipe.get("joins", {}) or {}) + list(all_schemas))
            raise DataAnalysisRecipeError(
                f"No join or data schema '{collection_id}' in data analysis recipe '{data_analysis_recipe_id}'. "
                f"Known: {', '.join(known) or 'none'}.")

        # Path C: assembly — ordered ingredient dict so DataAssembler starts
        # from the correct base (first declared ingredient, not first dict key)
        steps_raw = collection_spec.get("steps", [])
        steps = DataWrangler._resolve_tier(steps_raw, "tier1")

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
        assembler = DataAssembler(assembly_ingredients, recipe_id=data_analysis_recipe_id, join_id=collection_id)
        lf = assembler.assemble(steps)

        # ADR-089: the chained Tier 1 key (the resolved recipe with every included file, the data content and the engine
        # version) is written into the anchor, so any upstream change rebuilds it.
        lf = write_anchor(lf, str(output_path), decision_hash=keys.tier1_key, metadata={TIER1_KEY_META: keys.tier1_key})

        print(f"[Orchestrator] ✅ materialize_tier1 DONE — assembly '{collection_id}' in {time.perf_counter()-_t_start:.2f}s → {output_path}")
        return lf

    def materialize_tier2(self, data_analysis_recipe_id: str, collection_id: str, tier1_path: Path,
                          keys: DataAnalysisRecipeKeys | None = None) -> pl.LazyFrame:
        """The Tier 2 data of one collection, read from its stored parquet (ADR-089 point 6, issue #10).

        A collection is a join or a schema that a plot reads directly; its tier-2 list is `tier2_steps` (one reading,
        `utils.recipe_tiers`, issue #77).

        - no tier2 steps: T2 equals T1, nothing is stored, the Tier 1 frame is returned;
        - stored file whose key matches: read, nothing is recomputed;
        - missing or mismatched file: recomputed from the (valid) Tier 1 and stored with its key.

        The key chains the Tier 1 key, so a change in a Tier 1 part invalidates Tier 2 as well,
        while a change in a Tier 2 step recomputes only Tier 2 (the Tier 1 file is only checked).
        """
        keys = keys or self.compute_data_analysis_recipe_keys(data_analysis_recipe_id)
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        steps = tier2_steps(load_data_analysis_recipe(data_analysis_recipe_path).raw, collection_id)
        t2_path = tier2_path_for(tier1_path)

        if not steps:
            # materialize_tier1 also removes a Tier 2 file left from an earlier data analysis recipe.
            return self.materialize_tier1(data_analysis_recipe_id, collection_id, tier1_path, keys=keys)

        key = tier2_key(keys.tier1_key, steps)
        if t2_path.exists() and get_parquet_metadata_hash(str(t2_path), TIER2_KEY_META) == key:
            print(f"[Orchestrator] ✅ Tier 2 '{collection_id}' is valid (key match) → {t2_path}")
            return pl.scan_parquet(t2_path)

        lf_t1 = self.materialize_tier1(data_analysis_recipe_id, collection_id, tier1_path, keys=keys)
        # A copy: the dicts belong to the data analysis recipe kept in memory and the key of the next read must match.
        lf_t2 = DataWrangler().run(lf_t1, copy.deepcopy(steps))
        print(f"[Orchestrator] ▶ Tier 2 '{collection_id}' recomputed from Tier 1 → {t2_path}")
        return write_anchor(lf_t2, str(t2_path), decision_hash=key, metadata={TIER2_KEY_META: key})

    def dataset_schemas(self, data_analysis_recipe_id: str) -> dict[str, Any]:
        """{dataset_id: schema} of every dataset a recipe names (data schemas, metadata, additional datasets)."""
        path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not path.exists():
            return {}
        recipe = load_data_analysis_recipe(path).raw
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
