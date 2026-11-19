# @deps
# provides: class:DataWrangler, method:tier_steps, method:run
# consumes: libs/transformer/src/transformer/actions/ (all registered actions via registry)
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-WRANGLER-1)
# consumed_by: libs/transformer/src/transformer/engine_python_polars.py (the entry that app/modules/engine_registry.py hands to app/modules/orchestrator.py), app/modules/data_analysis_recipe_validator.py (tier_steps), app/modules/wrangle_studio.py (tier_steps), app/handlers/blueprint_handlers.py, libs/transformer/tests/debug_assembler.py, libs/transformer/tests/debug_wrangler.py
# doc: .claude/rules/rules_data_engine.md, .claude/knowledge/architecture_decisions.md#ADR-094
# @end_deps
import polars as pl
from typing import Dict, Any, List
# Import the registry functions
from transformer.registry import get_action_function
from utils.step_migration import removed_action_catalog
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
    def tier_steps(body: Any, tier: str) -> List[Dict[str, Any]]:
        """
        The step list of one tier of a table, a join or a plot entry (D-0250): `body[tier]["steps"]`.

        `body` is the table (or join, or for tier3 the plot entry) mapping itself. A tier is written as its own key, a mapping with the
        list under `steps` and an optional `data_engine`; a tier that is not written gives no steps. The old shapes
        are refused with a message that names the key and the rewrite tool; none is read (no shim): a recipe in
        another shape is not run with fewer steps and no word.

        Args:
            body: the table or join mapping (empty or None gives no steps).
            tier: 'tier1' or 'tier2' of a table or a join; 'tier3' of a plot entry.
        """
        if tier not in ("tier1", "tier2", "tier3"):
            raise ValueError(f"tier must be 'tier1', 'tier2' or 'tier3', not {tier!r}")
        if not body:
            return []
        tool = "assets/scripts/migrate_recipe_engine_keys.py"
        if not isinstance(body, dict):
            raise DataAnalysisRecipeError(
                f"A table or a join is a mapping, not {type(body).__name__}.",
                tip="Write the table or the join as a mapping with its tiers (tier1: {steps: [...]}, tier2: {steps: [...]}).")
        for old, what in (("wrangling", "the tiers are written directly in the table, each as a mapping with steps"),
                          ("steps", "the tiers are written directly in the join, each as a mapping with steps")):
            if old in body:
                raise DataAnalysisRecipeError(
                    f"'{old}' is not a key of a table or a join any more: {what}.",
                    tip=f"Rewrite the recipe with {tool}; it moves the steps to tier1 and tier2.")
        if tier not in body:
            return []
        held = body[tier]
        if not isinstance(held, dict):
            raise DataAnalysisRecipeError(
                f"{tier} is written as {'a list' if isinstance(held, list) else repr(held)}, not as a mapping with steps.",
                tip=f"Write {tier}: {{steps: [...]}} (the list under steps). Rewrite tool: {tool}.")
        extra = sorted(k for k in held if k not in ("data_engine", "steps"))
        if extra:
            raise DataAnalysisRecipeError(
                f"{tier} has the key(s) {', '.join(map(str, extra))}; a tier holds data_engine and steps only.",
                tip=f"Write the steps under {tier}.steps. Rewrite tool: {tool}.")
        steps = held.get("steps")
        if not isinstance(steps, list):
            raise DataAnalysisRecipeError(
                f"{tier} has no list of steps.", tip=f"Write {tier}: {{steps: []}} when the tier is empty.")
        # Performance heuristic: relational joins belong in Tier 1 (computed once and shared by every plot)
        if tier == "tier2":
            for act in steps:
                if isinstance(act, dict) and act.get("action") == JOIN:
                    raise DataAnalysisRecipeError(
                        f"Performance Alert: Action '{act.get('action')}' found in Tier 2.",
                        tip="Relational joins are foundational. Please move this step to 'tier1' (The Trunk) to ensure it is only computed once and shared across all dependent plots.")
        return steps

    def run(self, lf: pl.LazyFrame, wrangling_rules: List[Dict[str, Any]]) -> pl.LazyFrame:
        """
        Applies a list of declarative wrangling rules sequentially to the LazyFrame.
        Each rule is a dictionary containing an 'action' and parameters.
        Pass the output of tier_steps() for tiered execution.
        """
        if not wrangling_rules:
            return lf

        transformed_lf = lf

        for step_idx, rule in enumerate(wrangling_rules, start=1):
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
                    fix=str(exc) if action_name in removed_action_catalog() else (
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
