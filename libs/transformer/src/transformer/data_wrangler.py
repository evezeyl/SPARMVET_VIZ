# @deps
# provides: class:DataWrangler, method:_resolve_tier, method:run
# consumes: libs/transformer/src/transformer/actions/ (all registered actions via registry)
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-WRANGLER-1)
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py, libs/transformer/tests/debug_wrangler.py
# doc: .claude/rules/rules_data_engine.md
# @end_deps
import polars as pl
from typing import Dict, Any, List
# Import the registry functions
from transformer.registry import get_action_function
from utils.errors import TransformationError, ManifestError
from utils.pipeline_error import PipelineError


class DataWrangler:
    """
    Applies declarative YAML configuration rules to a Polars LazyFrame.

    It maps column names to specific transformation actions defined in
    the central Action Registry.
    """

    def __init__(self, data_schema: Dict[str, Any]):
        """
        Args:
            data_schema: The dictionary from the YAML representing the schema (categories, types, etc.)
        """
        self.data_schema = data_schema

    def _resolve_category_targets(self, key: str) -> List[str]:
        """
        If a rule targets a category (e.g. "@AMR"), this returns all column names
        in the data_schema that have that category. Otherwise, returns the single column name.
        """
        if not isinstance(key, str) or not key.startswith("@"):
            return [key]

        category_name = key[1:]  # strip the '@'
        target_cols = []
        for col_name, col_props in self.data_schema.items():
            if "categories" in col_props and category_name in col_props["categories"]:
                target_cols.append(col_name)

        return target_cols

    @staticmethod
    def _resolve_tier(wrangling_block: Any, tier: str) -> List[Dict[str, Any]]:
        """
        Resolves the action list for a specific tier from a wrangling block.

        Supported shapes:
          - dict with 'tier1'/'tier2' keys → returns that tier's list.
          - flat list → treated as tier1 (legacy/simple manifests).
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
                raise ManifestError(
                    f"Wrangling block uses dict format but is missing tiered keys ('tier1', 'tier2').",
                    tip="If using the nested structure, please wrap your actions under 'tier1:' or 'tier2:' keys. If you prefer a simple list, remove the dictionary wrapping."
                )

            # Performance Heuristic: Global joins should be in Tier 1
            if tier == "tier2" or tier == "all":
                t2_actions = wrangling_block.get("tier2", [])
                for act in t2_actions:
                    if act.get("action") in ("join", "join_filter"):
                        raise ManifestError(
                            f"Performance Alert: Action '{act.get('action')}' found in Tier 2.",
                            tip="Relational joins are foundational. Please move this step to 'tier1' (The Trunk) to ensure it is only computed once and shared across all dependent plots."
                        )

            if tier == "all":
                return wrangling_block.get("tier1", []) + wrangling_block.get("tier2", [])
            return wrangling_block.get(tier, [])

        # Flat list → treat as tier1
        if tier in ("tier1", "all"):
            return wrangling_block
        return []  # tier2 on a flat list → skip gracefully

    def run_tier1(self, lf: pl.LazyFrame, wrangling_block: Any) -> pl.LazyFrame:
        """Executes only the tier1 actions from a wrangling block."""
        return self.run(lf, self._resolve_tier(wrangling_block, "tier1"))

    def run_tier2(self, lf: pl.LazyFrame, wrangling_block: Any) -> pl.LazyFrame:
        """Executes only the tier2 actions from a wrangling block. No-op if tier2 is absent."""
        return self.run(lf, self._resolve_tier(wrangling_block, "tier2"))

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
                    who="manifest_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"step_keys": str(list(rule.keys()))},
                    reference="rules_manifest_structure.md §7",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix)

            # 1. Resolve targets (inject back into rule for standard spec compliance)
            raw_selectors = rule.get("columns", rule.get(
                "column", rule.get(
                    "source", rule.get(
                        "source_column", rule.get("target_column", rule.get(True))))))

            target_columns = []
            if raw_selectors:
                if isinstance(raw_selectors, str):
                    raw_selectors = [raw_selectors]
                for selector in raw_selectors:
                    target_columns.extend(
                        self._resolve_category_targets(selector))

            # Ensure unique columns while preserving resolution order
            # This 'resolved_columns' becomes the truth for the action
            rule["columns"] = list(dict.fromkeys(target_columns))

            # Advanced Error Handling: Column Presence Check with Typo Correction (ADR-034)
            # NOTE: We only check if the column list was explicitly provided and failed to resolve.
            # ACTIONS that create new columns (mutate, add_constant, regex_extract) are exempt
            # if the target does not yet exist.
            exempt_actions = ["mutate", "add_constant",
                              "regex_extract", "divide_columns", "unpivot"]
            import difflib
            all_cols = transformed_lf.collect_schema().names()

            # If we targeted specific columns but none are found in the CURRENT LazyFrame
            if (rule["columns"] and
                action_name not in exempt_actions and
                    not any(c in all_cols for c in rule["columns"])):
                missing = [c for c in rule["columns"] if c not in all_cols]
                suggestions = {}
                for m in missing:
                    matches = difflib.get_close_matches(
                        m, all_cols, n=1, cutoff=0.6)
                    if matches:
                        suggestions[m] = matches[0]

                tip = f"Ensure that {missing} are defined in the schema or correctly renamed/derived in previous steps."
                if suggestions:
                    tip += f" Hint: Did you mean {list(suggestions.values())}?"

                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Action '{action_name}' — column(s) {missing} not found in current frame.",
                    location=f"wrangling step {step_idx}: action='{action_name}'",
                    fix=tip,
                    who="manifest_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    evidence={
                        "missing_columns": missing,
                        "near_match": str(suggestions) if suggestions else None,
                        "available_columns": all_cols[:20],
                    },
                    reference="rules_manifest_structure.md §7",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix)

            # 2. Resolve primary keys for safety
            pks = [col for col, props in self.data_schema.items()
                   if isinstance(props, dict) and props.get("is_primary_key")]
            rule["__metadata__"] = {"primary_keys": pks}

            # 3. Fetch and execute the action (ADR-079 Phase 2 — DIAG-RUNTIME-WRANGLER-1).
            try:
                action_func = get_action_function(action_name)
            except ValueError as exc:
                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Action '{action_name}' is not registered.",
                    location=f"wrangling step {step_idx}",
                    fix=(
                        f"'{action_name}' is not a registered wrangling action. "
                        "See rules_persona_bioscientist.md §8 for the authoritative action list."
                    ),
                    who="manifest_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    reference="rules_persona_bioscientist.md §8",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix) from exc

            try:
                transformed_lf = action_func(transformed_lf, rule)
            except pl.exceptions.ColumnNotFoundError as exc:
                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Column not found during '{action_name}': {exc}",
                    location=f"wrangling step {step_idx}: action='{action_name}'",
                    fix="Verify the column name in the action spec matches the data schema exactly.",
                    who="manifest_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"polars_error": str(exc)},
                    reference="rules_manifest_structure.md §7",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix) from exc
            except Exception as exc:
                pe = PipelineError(
                    component="DataWrangler",
                    problem=f"Action '{action_name}' raised {type(exc).__name__}: {exc}",
                    location=f"wrangling step {step_idx}: action='{action_name}'",
                    fix="Review the action parameters and the data state at this step.",
                    who="manifest_author",
                    category="wrangling",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix) from exc

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
