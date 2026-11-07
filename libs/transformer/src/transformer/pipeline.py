# PipelineExecutor (pipeline.py)
# @deps
# provides: class:PipelineExecutor
# consumes: utils.config_loader (ConfigManager), transformer.data_wrangler, transformer.data_assembler
# consumes_typeonly: ingestion.ingestor (DataIngestor — TYPE_CHECKING guard, injected at runtime per Clear Lines policy)
# consumed_by: libs/transformer/tests/debug_pipeline.py
# note: the app does not use this class; app/modules/orchestrator.py (DataOrchestrator) is the production path
#       and adds the input gatekeeper, join-key normalisation and the chained cache keys (ADR-089).
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
    High-level orchestrator for executing full data pipelines defined in data analysis recipes.
    Bridges Ingestion, Wrangling, and Assembly into a single execution unit.

    Produces the Tier 1 result (tier1 wrangling and tier1 recipe steps). Tier 2 is not applied.
    This is the plain executor used by the debug runner; the app uses DataOrchestrator.
    """

    def __init__(self, ingestor: "DataIngestor"):
        self.ingestor = ingestor

    def run_pipeline(self, data_analysis_recipe_path: Path, join_id: str | None = None) -> pl.LazyFrame:
        """
        Loads a data analysis recipe, ingests all components, wrangles them, and assembles the result.

        Args:
            data_analysis_recipe_path: Path to the YAML pipeline data analysis recipe.
            join_id: Specific assembly to run. Defaults to the first one found if None.

        Returns:
            A Polars LazyFrame of the assembled data.
        """
        cm = ConfigManager(str(data_analysis_recipe_path))
        data_analysis_recipe = cm.raw_config

        # 1. Ingredient Processing
        ingredients = {}
        all_schemas = {}
        all_schemas.update(data_analysis_recipe.get("data_schemas", {}))
        if "metadata_schema" in data_analysis_recipe:
            all_schemas["metadata_schema"] = data_analysis_recipe["metadata_schema"]
        all_schemas.update(data_analysis_recipe.get("additional_datasets_schemas", {}))

        for ds_id, ds_schema in all_schemas.items():
            lf, _ = self.ingestor.ingest(ds_id, ds_schema)

            # Atomic Wrangling (Layer 1)
            # Tiered data analysis recipes (ADR-024): only the tier1 steps belong to the shared trunk.
            wrangling_rules = DataWrangler._resolve_tier(ds_schema.get("wrangling", []), "tier1")
            wrangler = DataWrangler(
                data_schema=ds_schema.get("input_fields", {}))
            lf = wrangler.run(lf, wrangling_rules)

            ingredients[ds_id] = lf

        # 2. Relational Assembly (Layer 2)
        if not join_id:
            join_defs = data_analysis_recipe.get("joins", {})
            if not join_defs:
                raise ValueError(
                    f"No join_defs defined in data analysis recipe {data_analysis_recipe_path}")
            join_id = list(join_defs.keys())[0]

        assembly_spec = data_analysis_recipe.get(
            "joins", {}).get(join_id, {})
        if not assembly_spec:
            raise ValueError(
                f"Assembly '{join_id}' not found in data analysis recipe.")

        recipe = DataWrangler._resolve_tier(assembly_spec.get("recipe", []), "tier1")

        assembler = DataAssembler(ingredients)
        return assembler.assemble(recipe)
