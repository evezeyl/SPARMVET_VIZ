# PipelineExecutor (pipeline.py)
# @deps
# provides: class:PipelineExecutor
# consumes: utils.config_loader (ConfigManager), transformer.data_wrangler, transformer.data_assembler
# consumes_typeonly: ingestion.ingestor (DataIngestor — TYPE_CHECKING guard, injected at runtime per Clear Lines policy)
# consumed_by: libs/transformer/tests/debug_pipeline.py, app/modules/orchestrator.py
# doc: .claude/rules/rules_data_engine.md, .claude/rules/rules_runtime_environment.md#4
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING
from utils.config_loader import ConfigManager
from transformer.data_wrangler import DataWrangler
from transformer.data_assembler import DataAssembler

if TYPE_CHECKING:
    # Type annotation only — no runtime cross-library import (Clear Lines policy,
    # rules_runtime_environment.md §4). The DataIngestor instance is injected by
    # the caller (typically a test runner under libs/transformer/tests/ or the
    # production Orchestrator at app/modules/orchestrator.py).
    from ingestion.ingestor import DataIngestor


class PipelineExecutor:
    """
    High-level orchestrator for executing full data pipelines defined in manifests.
    Bridges Ingestion, Wrangling, and Assembly into a single execution unit.
    """

    def __init__(self, ingestor: "DataIngestor"):
        self.ingestor = ingestor

    def run_pipeline(self, manifest_path: Path, join_id: str | None = None) -> pl.LazyFrame:
        """
        Loads a manifest, ingests all components, wrangles them, and assembles the result.

        Args:
            manifest_path: Path to the YAML pipeline manifest.
            join_id: Specific assembly to run. Defaults to the first one found if None.

        Returns:
            A Polars LazyFrame of the assembled data.
        """
        cm = ConfigManager(str(manifest_path))
        manifest = cm.raw_config

        # 1. Ingredient Processing
        ingredients = {}
        all_schemas = {}
        all_schemas.update(manifest.get("data_schemas", {}))
        if "metadata_schema" in manifest:
            all_schemas["metadata_schema"] = manifest["metadata_schema"]
        all_schemas.update(manifest.get("additional_datasets_schemas", {}))

        for ds_id, ds_schema in all_schemas.items():
            lf, _ = self.ingestor.ingest(ds_id, ds_schema)

            # Atomic Wrangling (Layer 1)
            wrangling_rules = ds_schema.get("wrangling", [])
            wrangler = DataWrangler(
                data_schema=ds_schema.get("input_fields", {}))
            lf = wrangler.run(lf, wrangling_rules)

            ingredients[ds_id] = lf

        # 2. Relational Assembly (Layer 2)
        if not join_id:
            join_defs = manifest.get("join_manifests", {})
            if not join_defs:
                raise ValueError(
                    f"No join_defs defined in manifest {manifest_path}")
            join_id = list(join_defs.keys())[0]

        assembly_spec = manifest.get(
            "join_manifests", {}).get(join_id, {})
        if not assembly_spec:
            raise ValueError(
                f"Assembly '{join_id}' not found in manifest.")

        recipe_data = assembly_spec.get("recipe", [])
        if isinstance(recipe_data, dict) and "steps" in recipe_data:
            recipe = recipe_data["steps"]
        else:
            recipe = recipe_data

        assembler = DataAssembler(ingredients)
        return assembler.assemble(recipe)
