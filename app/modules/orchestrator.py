# @deps
# provides: pipeline:materialize_tier1
# mirrors: libs/transformer/tests/debug_assembler.py
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/metadata_validator.py
# consumed_by: app/src/server.py, app/handlers/home_theater.py, app/handlers/blueprint_handlers.py
# doc: .antigravity/knowledge/dependency_index.md
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, List
from utils.config_loader import ConfigManager
from ingestion.ingestor import DataIngestor
from transformer.data_wrangler import DataWrangler
from transformer.data_assembler import DataAssembler


class DataOrchestrator:
    """
    Handles the ingestion and assembly logic (Tier 1 Materialization).
    Ensures the UI remains 'Thin' by delegating heavy processing to libraries.
    """

    def __init__(self, manifests_dir: Path, raw_data_dir: Path, prefer_discovery: bool = False):
        self.manifests_dir = manifests_dir
        self.raw_data_dir = raw_data_dir
        self.prefer_discovery = prefer_discovery
        self.ingestor = DataIngestor(data_dir=str(raw_data_dir))

    def materialize_tier1(self, project_id: str, collection_id: str, output_path: Path) -> pl.LazyFrame:
        """
        Executes the full project ingestion and assembly to create a Tier 1 Anchor.
        """
        import time
        _t_start = time.perf_counter()
        print(f"[Orchestrator] ▶ materialize_tier1 START — project='{project_id}', collection='{collection_id}'")

        manifest_path = self.manifests_dir / f"{project_id}.yaml"
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"Project manifest not found: {manifest_path}")

        # 1. Load Manifest
        cm = ConfigManager(str(manifest_path))
        manifest = cm.raw_config

        # 2. Ingest and Wrangle Ingredients
        ingredients = {}
        all_schemas = {}
        all_schemas.update(manifest.get("data_schemas", {}))

        # Optional Metadata Support (ADR-014)
        if "metadata_schema" in manifest:
            all_schemas["metadata_schema"] = manifest["metadata_schema"]

        all_schemas.update(manifest.get("additional_datasets_schemas", {}))

        from transformer.metadata_validator import MetadataValidator
        validator = MetadataValidator()

        for ds_id, ds_schema in all_schemas.items():
            try:
                if self.prefer_discovery:
                    # Production path: ignore manifest source.path, discover by
                    # schema ID name in raw_data_dir (mirrors Galaxy/IRIDA connector).
                    ds_schema = {k: v for k, v in ds_schema.items() if k != "source"}
                lf, _ = self.ingestor.ingest(ds_id, ds_schema)

                # --- ADR-034: Malformed Data Gatekeeping ---
                input_contract = ds_schema.get("input_fields", {})
                validator.validate(lf, input_contract,
                                   context=f"Dataset [{ds_id}]")
                lf = validator.enforce_schema(lf, input_contract)

                # Wrangle (Tier 1 only for ingredients)
                wrangling_raw = ds_schema.get("wrangling", [])
                rules = DataWrangler._resolve_tier(wrangling_raw, "tier1")

                wrangler = DataWrangler(data_schema=input_contract)
                lf = wrangler.run(lf, rules)

                ingredients[ds_id] = lf
            except Exception as e:
                # ADR-034: Propagate SPARMVET_Errors or wrap generic ones
                print(
                    f"⚠️ Ingestion Error in '{ds_id}': {str(e)}")
                # If it's a critical schema mismatch, we might want to halt here
                # but for 'optional' ingredients we continue.
                continue

        # 3. Resolve target — may be an assembly OR a bare data_schema
        collection_spec = manifest.get("join_manifests", {}).get(collection_id)

        # Path A: bare data_schema / additional_dataset / metadata_schema
        # (e.g. a plot's target_dataset points directly to a source schema)
        if collection_spec is None and collection_id in ingredients:
            print(f"      └── 💾 Materializing data_schema '{collection_id}' to: {output_path}")
            lf = ingredients[collection_id]
            lf.sink_parquet(output_path, compression="snappy")
            print(f"[Orchestrator] ✅ materialize_tier1 DONE — '{collection_id}' (bare schema) in {time.perf_counter()-_t_start:.2f}s → {output_path}")
            return pl.scan_parquet(output_path)

        # Path B: assembly not found — old fallback (agnostic discovery)
        if collection_spec is None:
            collections = manifest.get("join_manifests", {})
            if collections:
                collection_id = list(collections.keys())[0]
                collection_spec = collections[collection_id]
            else:
                raise ValueError(
                    f"No assembly or data_schema '{collection_id}' found in project '{project_id}'.")

        # Path C: assembly — ordered ingredient dict so DataAssembler starts
        # from the correct base (first declared ingredient, not first dict key)
        recipe_raw = collection_spec.get("recipe", [])
        recipe = DataWrangler._resolve_tier(recipe_raw, "tier1")

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

        for step in recipe:
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
        filtered_recipe = []
        for step in recipe:
            right_id = step.get("right_ingredient")
            if right_id and right_id not in assembly_ingredients:
                print(
                    f"⚠️ Skipping recipe step '{step.get('action')}' due to missing ingredient '{right_id}'")
                continue
            filtered_recipe.append(step)

        # BUG-CACHE-1: include upstream provenance in the recipe so the
        # DataAssembler's decision_hash invalidates the cached parquet whenever
        # the manifest YAML or any source TSV content changes. Without this,
        # changes outside the assembly recipe (input_fields, source TSV edits,
        # per-ingredient wrangling) would silently serve a stale parquet.
        from app.modules.session_manager import SessionManager
        try:
            manifest_sha256 = SessionManager.compute_manifest_sha256(manifest_path)
            source_files = self.get_source_files(project_id)
            data_batch_hash = SessionManager.compute_data_batch_hash(source_files) if source_files else ""
            upstream_provenance = f"{manifest_sha256[:16]}:{data_batch_hash[:16]}"
        except Exception as e:
            print(f"⚠️ Provenance hash unavailable ({e}); falling back to recipe-only hash")
            upstream_provenance = ""

        filtered_recipe.append({
            "action": "sink_parquet",
            "path": str(output_path),
            "force_recompute": False,
            "upstream_provenance": upstream_provenance,
        })

        assembler = DataAssembler(assembly_ingredients)
        lf = assembler.assemble(filtered_recipe)


        # ADR-013: Apply final_contract as an exclusive whitelist projection.
        # Only columns listed in final_contract are retained in the output Parquet.
        # Intermediate columns (e.g. boolean flags) are dropped here.
        final_contract = collection_spec.get("final_contract", {})
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

        print(f"[Orchestrator] ✅ materialize_tier1 DONE — assembly '{collection_id}' in {time.perf_counter()-_t_start:.2f}s → {output_path}")
        return lf

    def get_source_files(self, project_id: str) -> dict[str, Path]:
        """Return {dataset_id: resolved_path} for all source files in a project manifest.

        Used by SessionManager.compute_data_batch_hash to detect input file changes.
        Only returns paths that exist on disk; missing files are silently skipped.
        """
        manifest_path = self.manifests_dir / f"{project_id}.yaml"
        if not manifest_path.exists():
            return {}
        cm = ConfigManager(str(manifest_path))
        manifest = cm.raw_config

        all_schemas: dict[str, Any] = {}
        all_schemas.update(manifest.get("data_schemas", {}))
        if "metadata_schema" in manifest:
            all_schemas["metadata_schema"] = manifest["metadata_schema"]
        all_schemas.update(manifest.get("additional_datasets_schemas", {}))

        result: dict[str, Path] = {}
        for ds_id, ds_schema in all_schemas.items():
            source = ds_schema.get("source", {})
            source_type = source.get("type")
            source_path = source.get("path")
            if source_type in ("local_tsv", "local_parquet") and source_path:
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
