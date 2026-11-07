# @deps
# provides: pipeline:materialize_tier1, pipeline:materialize_tier2, method:prepare_ingredient, function:compute_recipe_keys
# mirrors: libs/transformer/tests/debug_assembler.py
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/metadata_validator.py, libs/transformer/src/transformer/actions/persistence/anchor.py, app/modules/cache_keys.py
# consumed_by: app/src/server.py, app/handlers/home_theater.py, app/handlers/blueprint_handlers.py
# doc: .claude/knowledge/dependency_index.md
# @end_deps
import copy
import polars as pl
from pathlib import Path
from typing import Any
from utils.errors import IngestionError
from utils.hashing import get_parquet_metadata_hash
from ingestion.ingestor import DataIngestor
from transformer.data_wrangler import DataWrangler
from transformer.data_assembler import DataAssembler
from transformer.actions.persistence.anchor import action_sink_parquet
from app.modules.cache_keys import RecipeKeys, load_data_analysis_recipe, recipe_keys, tier2_key, tier2_steps

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

class DataOrchestrator:
    """
    Handles the ingestion and assembly logic (Tier 1 Materialization).
    Ensures the UI remains 'Thin' by delegating heavy processing to libraries.
    """

    def __init__(self, data_analysis_recipes_dir: Path, raw_data_dir: Path, data_lookup: str = "data_analysis_recipe_paths"):
        self.data_analysis_recipes_dir = data_analysis_recipes_dir
        self.raw_data_dir = raw_data_dir
        if data_lookup not in DATA_LOOKUP_CHOICES:
            raise ValueError(f"data_lookup must be one of {DATA_LOOKUP_CHOICES}, got {data_lookup!r}")
        self.data_lookup = data_lookup
        self.discover_by_dataset_id = data_lookup == "by_dataset_id"
        self.ingestor = DataIngestor(data_dir=str(raw_data_dir))

    @staticmethod
    def _apply_final_contract(lf: pl.LazyFrame, collection_spec: dict | None) -> pl.LazyFrame:
        """ADR-013: final_contract is an exclusive whitelist projection of the anchor's columns.

        Applied the same way whether the anchor was just built or reused from disk, so the
        result never depends on whether the cache was warm.
        """
        final_contract = (collection_spec or {}).get("final_contract", {})
        if final_contract and isinstance(final_contract, dict):
            keep = list(final_contract.keys())
            schema_names = set(lf.collect_schema().names())
            missing = [c for c in keep if c not in schema_names]
            if missing:
                print(f"⚠️  final_contract references columns not in assembly output: {missing}")
                keep = [c for c in keep if c in schema_names]
            if keep:
                print(f"  └── 🛡️  final_contract: projecting to {len(keep)} contracted columns.")
                lf = lf.select(keep)
        return lf

    def compute_recipe_keys(self, data_analysis_recipe_id: str) -> RecipeKeys:
        """The keys every stored stage of this project depends on (ADR-089).

        Reads the data files to hash their content, so callers compute it once per session
        and pass it to materialize_tier1().
        """
        from app.modules.session_manager import SessionManager
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            raise FileNotFoundError(f"Project data analysis recipe not found: {data_analysis_recipe_path}")
        loaded = load_data_analysis_recipe(data_analysis_recipe_path)
        source_files = self.get_source_files(data_analysis_recipe_id)
        data_hash = SessionManager.compute_data_batch_hash(source_files) if source_files else ""
        return recipe_keys(loaded, data_hash)

    def prepare_ingredient(self, ds_id: str, ds_schema: dict) -> pl.LazyFrame:
        """Read one dataset of a data analysis recipe and apply its input contract and tier-1 wrangling.

        Raises when the file cannot be read, a declared input column is missing, or a value does
        not fit its declared type. Shared by materialize_tier1 and the data analysis recipe data check, so
        both see the dataset the same way.
        """
        from transformer.metadata_validator import MetadataValidator
        validator = MetadataValidator()
        if self.discover_by_dataset_id:
            # Production path: ignore data analysis recipe source.path, discover by schema ID name in
            # raw_data_dir (mirrors Galaxy/IRIDA connector).
            ds_schema = {k: v for k, v in ds_schema.items() if k != "source"}
        lf, _ = self.ingestor.ingest(ds_id, ds_schema)

        # ADR-034: Malformed Data Gatekeeping
        input_contract = ds_schema.get("input_fields", {})
        validator.validate(lf, input_contract, context=f"Dataset [{ds_id}]")
        lf = validator.enforce_schema(lf, input_contract)

        rules = DataWrangler._resolve_tier(ds_schema.get("wrangling", []), "tier1")
        return DataWrangler(data_schema=input_contract).run(lf, rules)

    def materialize_tier1(self, data_analysis_recipe_id: str, collection_id: str, output_path: Path,
                          keys: RecipeKeys | None = None) -> pl.LazyFrame:
        """
        Executes the full project ingestion and assembly to create a Tier 1 Anchor.

        The anchor is reused only when the chained key stored in its metadata matches the
        current one (ADR-089); never by file name alone.
        """
        import time
        _t_start = time.perf_counter()
        print(f"[Orchestrator] ▶ materialize_tier1 START — project='{data_analysis_recipe_id}', collection='{collection_id}'")

        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            raise FileNotFoundError(
                f"Project data analysis recipe not found: {data_analysis_recipe_path}")

        # 1. Load Data Analysis Recipe (kept in memory while none of its files changed on disk)
        loaded = load_data_analysis_recipe(data_analysis_recipe_path)
        data_analysis_recipe = loaded.raw
        keys = keys or self.compute_recipe_keys(data_analysis_recipe_id)

        # No tier2 steps: T2 equals T1, so a Tier 2 file left from an earlier data analysis recipe would be a
        # false T2. It could never be served (its key would not match), but it must not stay.
        t2_file = tier2_path_for(output_path)
        if not tier2_steps(data_analysis_recipe, collection_id):
            t2_file.unlink(missing_ok=True)

        # Cheap validity check before any ingestion: the stored key must match the current one.
        if Path(output_path).exists() and \
                get_parquet_metadata_hash(str(output_path), TIER1_KEY_META) == keys.tier1_key:
            print(f"[Orchestrator] ✅ Tier 1 anchor '{collection_id}' is valid (key match) → {output_path}")
            return self._apply_final_contract(
                pl.scan_parquet(output_path), data_analysis_recipe.get("joins", {}).get(collection_id))

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
                ingredients[ds_id] = self.prepare_ingredient(ds_id, ds_schema)
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
        # (e.g. a plot's target_dataset points directly to a source schema)
        if collection_spec is None and collection_id in ingredients:
            print(f"      └── 💾 Materializing data_schema '{collection_id}' to: {output_path}")
            lf = ingredients[collection_id]
            action_sink_parquet(lf, {
                "path": str(output_path),
                "decision_hash": keys.tier1_key,
                "metadata": {TIER1_KEY_META: keys.tier1_key},
            })
            print(f"[Orchestrator] ✅ materialize_tier1 DONE — '{collection_id}' (bare schema) in {time.perf_counter()-_t_start:.2f}s → {output_path}")
            return pl.scan_parquet(output_path)

        # Path B: assembly not found — old fallback (agnostic discovery)
        if collection_spec is None:
            collections = data_analysis_recipe.get("joins", {})
            if collections:
                collection_id = list(collections.keys())[0]
                collection_spec = collections[collection_id]
            else:
                raise ValueError(
                    f"No assembly or data_schema '{collection_id}' found in project '{data_analysis_recipe_id}'.")

        # Path C: assembly — ordered ingredient dict so DataAssembler starts
        # from the correct base (first declared ingredient, not first dict key)
        steps_raw = collection_spec.get("steps", [])
        steps = DataWrangler._resolve_tier(steps_raw, "tier1")

        ingredient_ids = [
            item.get("dataset_id") if isinstance(item, dict) else item
            for item in collection_spec.get("ingredients", [])
            if (item.get("dataset_id") if isinstance(item, dict) else item)
        ]
        assembly_ingredients = {
            ds_id: ingredients[ds_id]
            for ds_id in ingredient_ids
            if ds_id in ingredients
        }
        if not assembly_ingredients:
            assembly_ingredients = ingredients

        # Normalise join key dtypes across all ingredients before assembling.
        # Polars requires join keys to have matching dtypes; String is the safe
        # common denominator (Categorical ↔ String mismatches are the most common
        # SchemaError in cross-ingredient joins).
        #
        # Strategy: for each join step, collect (ingredient_id → set of columns to cast).
        # - symmetric keys ("on"): cast on base AND right ingredient
        # - asymmetric keys ("left_on"/"right_on"): cast left_on on base, right_on on right
        # We track per-ingredient so we only cast columns that actually exist in each.

        # ingredient_id → set of column names to cast to String
        per_ingredient_cast: dict[str, set] = {ds_id: set() for ds_id in assembly_ingredients}
        base_cast: set = set()  # columns to cast on the base frame

        for step in steps:
            right_id = step.get("right_ingredient")
            sym = step.get("on")
            left_on = step.get("left_on")
            right_on = step.get("right_on")

            # Symmetric join keys — cast on base and right ingredient
            if sym:
                cols = [sym] if isinstance(sym, str) else sym
                base_cast.update(cols)
                if right_id and right_id in per_ingredient_cast:
                    per_ingredient_cast[right_id].update(cols)

            # Asymmetric join keys
            if left_on:
                cols = [left_on] if isinstance(left_on, str) else left_on
                base_cast.update(cols)
            if right_on and right_id and right_id in per_ingredient_cast:
                cols = [right_on] if isinstance(right_on, str) else right_on
                per_ingredient_cast[right_id].update(cols)

        # Apply casts
        normalised: dict = {}
        for ds_id, lf in assembly_ingredients.items():
            schema_names = set(lf.collect_schema().names())
            cols_to_cast = per_ingredient_cast.get(ds_id, set())
            # First ingredient (base) also gets base_cast cols
            if ds_id == next(iter(assembly_ingredients)):
                cols_to_cast = cols_to_cast | base_cast
            cast_exprs = [
                pl.col(col).cast(pl.String)
                for col in cols_to_cast
                if col in schema_names
            ]
            normalised[ds_id] = lf.with_columns(cast_exprs) if cast_exprs else lf
        assembly_ingredients = normalised

        # Filter steps referring to missing ingredients
        filtered_steps = []
        for step in steps:
            right_id = step.get("right_ingredient")
            if right_id and right_id not in assembly_ingredients:
                print(
                    f"⚠️ Skipping step '{step.get('action')}' due to missing ingredient '{right_id}'")
                continue
            filtered_steps.append(step)

        # ADR-089: the chained Tier 1 key replaces the old provenance (data analysis recipe entry file
        # hash + data hash). It covers the resolved data analysis recipe including every included file,
        # the data content and the engine version, so any upstream change rebuilds the anchor.
        filtered_steps.append({
            "action": "sink_parquet",
            "path": str(output_path),
            "force_recompute": False,
            "upstream_provenance": keys.tier1_key,
            "metadata": {TIER1_KEY_META: keys.tier1_key},
        })

        assembler = DataAssembler(assembly_ingredients)
        lf = assembler.assemble(filtered_steps)


        lf = self._apply_final_contract(lf, collection_spec)

        print(f"[Orchestrator] ✅ materialize_tier1 DONE — assembly '{collection_id}' in {time.perf_counter()-_t_start:.2f}s → {output_path}")
        return lf

    def materialize_tier2(self, data_analysis_recipe_id: str, collection_id: str, tier1_path: Path,
                          keys: RecipeKeys | None = None) -> pl.LazyFrame:
        """The Tier 2 data of one join, read from its stored parquet (ADR-089 point 6, issue #10).

        - no tier2 steps: T2 equals T1, nothing is stored, the Tier 1 frame is returned;
        - stored file whose key matches: read, nothing is recomputed;
        - missing or mismatched file: recomputed from the (valid) Tier 1 and stored with its key.

        The key chains the Tier 1 key, so a change in a Tier 1 part invalidates Tier 2 as well,
        while a change in a Tier 2 step recomputes only Tier 2 (the Tier 1 file is only checked).
        """
        keys = keys or self.compute_recipe_keys(data_analysis_recipe_id)
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
        # A copy: DataWrangler.run adds keys to the step dicts in place, and these dicts belong to
        # the data analysis recipe kept in memory, so the next key would no longer match the stored one.
        lf_t2 = DataWrangler(data_schema={}).run(lf_t1, copy.deepcopy(steps))
        print(f"[Orchestrator] ▶ Tier 2 '{collection_id}' recomputed from Tier 1 → {t2_path}")
        return action_sink_parquet(lf_t2, {
            "path": str(t2_path),
            "decision_hash": key,
            "metadata": {TIER2_KEY_META: key},
        })

    def get_source_files(self, data_analysis_recipe_id: str) -> dict[str, Path]:
        """Return {dataset_id: resolved_path} for all source files in a project data analysis recipe.

        Used by SessionManager.compute_data_batch_hash to detect input file changes.
        Only returns paths that exist on disk; missing files are silently skipped.
        """
        data_analysis_recipe_path = self.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
        if not data_analysis_recipe_path.exists():
            return {}
        data_analysis_recipe = load_data_analysis_recipe(data_analysis_recipe_path).raw

        all_schemas: dict[str, Any] = {}
        all_schemas.update(data_analysis_recipe.get("data_schemas", {}))
        if "metadata_schema" in data_analysis_recipe:
            all_schemas["metadata_schema"] = data_analysis_recipe["metadata_schema"]
        all_schemas.update(data_analysis_recipe.get("additional_datasets_schemas", {}))

        result: dict[str, Path] = {}
        for ds_id, ds_schema in all_schemas.items():
            source = ds_schema.get("source", {})
            source_type = source.get("type")
            source_path = source.get("path")
            # data_lookup by_dataset_id (production): the data analysis recipe's source.path is only default data,
            # the data that counts is what the deployment delivered into raw_data_dir.
            if not self.discover_by_dataset_id and source_type in ("local_tsv", "local_parquet") and source_path:
                p = Path(source_path)
                if p.exists():
                    result[ds_id] = p
            else:
                # Legacy discovery — same logic as ingestor fallback
                name = ds_id
                exact = self.raw_data_dir / f"{name}.tsv"
                if exact.exists():
                    result[ds_id] = exact
                else:
                    found = list(self.raw_data_dir.glob(f"**/*{name}*.tsv"))
                    if found:
                        result[ds_id] = found[0]
        return result
