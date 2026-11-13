# @deps
# provides: class:DataWrangler, method:_resolve_tier, method:run
# consumes: libs/transformer/src/transformer/actions/ (all registered actions via registry)
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-WRANGLER-1)
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py, libs/transformer/tests/debug_wrangler.py
# doc: .claude/rules/rules_data_engine.md, .claude/knowledge/architecture_decisions.md#ADR-094
# @end_deps
import polars as pl
from typing import Dict, Any, List
# Import the registry functions
from transformer.registry import get_action_function
from utils.action_names import JOIN
from utils.errors import TransformationError, DataAnalysisRecipeError
from utils.pipeline_error import PipelineError


class DataWrangler:
    """
    Applies the steps of a recipe to a Polars LazyFrame, one after the other.

    A step names an action of the central Action Registry and carries its parameters; the action judges the step
    (`utils.ui_schema.step_problems`) and fails on any problem. Nothing is guessed here: no column alias is read,
    no column list is injected, nothing is added to the step.
    """

    @staticmethod
    def _resolve_tier(wrangling_block: Any, tier: str) -> List[Dict[str, Any]]:
        """
        Resolves the action list for a specific tier from a wrangling block.

        Supported shapes:
          - dict with 'tier1'/'tier2' keys → returns that tier's list.
          - empty / None → returns [].

        Args:
            wrangling_block: The raw value under the 'wrangling' YAML key.
            tier: 'tier1', 'tier2', or 'all'.
        """
        if not wrangling_block:
            return []

        if isinstance(wrangling_block, dict):
            # ADR-034: Heuristic check for tiered keys
            if "tier1" not in wrangling_block and "tier2" not in wrangling_block:
                raise DataAnalysisRecipeError(
                    f"Wrangling block uses dict format but is missing tiered keys ('tier1', 'tier2').",
                    tip="If using the nested structure, please wrap your actions under 'tier1:' or 'tier2:' keys. If you prefer a simple list, remove the dictionary wrapping."
                )

            # Performance Heuristic: Global joins should be in Tier 1
            if tier == "tier2" or tier == "all":
                t2_actions = wrangling_block.get("tier2", [])
                for act in t2_actions:
                    if act.get("action") == JOIN:
                        raise DataAnalysisRecipeError(
                            f"Performance Alert: Action '{act.get('action')}' found in Tier 2.",
                            tip="Relational joins are foundational. Please move this step to 'tier1' (The Trunk) to ensure it is only computed once and shared across all dependent plots."
                        )

            if tier == "all":
                return wrangling_block.get("tier1", []) + wrangling_block.get("tier2", [])
            return wrangling_block.get(tier, [])

        # Flat list is no longer accepted — raise an actionable error.
        raise DataAnalysisRecipeError(
            "Flat 'wrangling:' list is no longer accepted. Use the tiered structure with 'tier1:' and 'tier2:' keys.",
            tip=(
                "Replace 'wrangling: [...]' with:\n"
                "  wrangling:\n"
                "    tier1:\n"
                "      - action: your_action\n"
                "        ...\n"
                "    tier2: []\n"
                "See rules_data_engine.md §3 for the full tiered data analysis recipe standard."
            )
        )

    def run(self, lf: pl.LazyFrame, wrangling_rules: List[Dict[str, Any]]) -> pl.LazyFrame:
        """
        Applies a list of declarative wrangling rules sequentially to the LazyFrame.
        Each rule is a dictionary containing an 'action' and parameters.
        Pass the output of _resolve_tier() for tiered execution.
        """
        if not wrangling_rules:
            return lf

        transformed_lf = lf

        for step_idx, rule in enumerate(wrangling_rules):
            action_name = rule.get("action")
            if not action_name:
                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Wrangling step {step_idx} is missing the 'action' key.",
                    location=f"wrangling step {step_idx}",
                    fix=(
                        "Every wrangling step must use the canonical 'action:' key format. "
                        "Shorthand like '- mutate: [...]' is silently ignored by the engine."
                    ),
                    who="data_analysis_recipe_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"step_keys": str(list(rule.keys()))},
                    reference="rules_data_analysis_recipe_structure.md §7",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe)

            # Fetch and execute the action (ADR-079 Phase 2 — DIAG-RUNTIME-WRANGLER-1).
            try:
                action_func = get_action_function(action_name)
            except ValueError as exc:
                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Action '{action_name}' is not registered.",
                    location=f"wrangling step {step_idx}",
                    fix=(
                        f"'{action_name}' is not a registered wrangling action. "
                        "See rules_agent_role_bioscientist.md §8 for the authoritative action list."
                    ),
                    who="data_analysis_recipe_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    reference="rules_agent_role_bioscientist.md §8",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc

            try:
                transformed_lf = action_func(transformed_lf, dict(rule))
            except pl.exceptions.ColumnNotFoundError as exc:
                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Column not found during '{action_name}': {exc}",
                    location=f"wrangling step {step_idx}: action='{action_name}'",
                    fix="Verify the column name in the action spec matches the data schema exactly.",
                    who="data_analysis_recipe_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"polars_error": str(exc)},
                    reference="rules_data_analysis_recipe_structure.md §7",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc
            except Exception as exc:
                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Action '{action_name}' raised {type(exc).__name__}: {exc}",
                    location=f"wrangling step {step_idx}: action='{action_name}'",
                    fix="Review the action parameters and the data state at this step.",
                    who="data_analysis_recipe_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc

        return transformed_lf

    def wrangle(self, dataframe: pl.DataFrame, wrangling_rules: List[Dict[str, Any]]) -> pl.DataFrame:
        """
        Convenience wrapper bridging Eager DataFrames to Lazy execution.
        """
        lf = dataframe.lazy()
        result_lf = self.run(lf, wrangling_rules)
        return result_lf.collect()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
