# @deps
# provides: class:DataAssembler, method:assemble
# consumes: libs/transformer/src/transformer/actions/ (all registered actions via registry)
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-ASSEMBLER-1)
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/rules/rules_data_analysis_recipe_structure.md#7, .claude/knowledge/architecture_decisions.md#ADR-094
# @end_deps
import os
from typing import Dict, List, Any
import polars as pl
from transformer.registry import get_action_function
from utils.action_names import CAST, JOIN
from utils.errors import TransformationError
from utils.pipeline_error import PipelineError


class DataAssembler:
    """
    Orchestrates the assembly of multiple wrangled datasets (ingredients)
    into a final consolidated LazyFrame based on a relational step list.
    """

    def __init__(self, ingredients: Dict[str, pl.LazyFrame], *, recipe_id: str, join_id: str):
        """
        Args:
             ingredients: Dictionary mapping dataset_ids to their wrangled LazyFrames.
             recipe_id: The data analysis recipe being built (named in error messages).
             join_id: The join being built (named in error messages).
        """
        self.ingredients = ingredients
        self.recipe_id = recipe_id
        self.join_id = join_id

    @staticmethod
    def _key_columns(value: Any) -> List[str]:
        if value is None:
            return []
        return [value] if isinstance(value, str) else list(value)

    def _check_join_key_types(self, step: Dict[str, Any], index: int, left: pl.LazyFrame, right: pl.LazyFrame) -> None:
        """Fail when a join key has one type on the left and another on the right.

        Eve 2026-11-14: a join keeps the types the tables have; a change of type is a decision written in the
        recipe (input_fields or a polars_cast step), never done here. A key column that does not exist is left to
        the join itself, which names the missing column.
        """
        left_keys = self._key_columns(step.get("on") or step.get("left_on"))
        right_keys = self._key_columns(step.get("on") or step.get("right_on"))
        left_schema, right_schema = left.collect_schema(), right.collect_schema()
        right_id = step["right_ingredient"]
        for left_col, right_col in zip(left_keys, right_keys):
            if left_col not in left_schema or right_col not in right_schema:
                continue
            left_type, right_type = left_schema[left_col], right_schema[right_col]
            if left_type == right_type:
                continue
            names = f"column '{left_col}'" if left_col == right_col else f"column '{left_col}' (left) and '{right_col}' (right)"
            problem = (
                f"The join key types differ in data analysis recipe '{self.recipe_id}', join '{self.join_id}', step {index} "
                f"({step['action']} with '{right_id}'): {names} is {left_type} in the left table and {right_type} in '{right_id}'."
            )
            fix = (
                f"Declare the same type for this field in input_fields of both tables, or add a {CAST} step before the join. "
                "The engine does not change the type of a join key for you."
            )
            pe = PipelineError(
                component="DataAssembler", problem=problem,
                location=f"data analysis recipe '{self.recipe_id}', join '{self.join_id}', assembly step {index}: action='{step['action']}', right_ingredient='{right_id}'",
                fix=fix, who="data_analysis_recipe_author", category="assembly", surface="plot_overlay", severity="error",
                evidence={"left_column": left_col, "right_column": right_col, "left_type": str(left_type), "right_type": str(right_type)},
                reference="recipe_format_spec.md 7.5",
            )
            print(pe.format())
            raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe)

    @staticmethod
    def _canonical_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """A copy of the steps; every step must be written with its `action` key (no shorthand is guessed)."""
        import copy
        copied = copy.deepcopy(steps)
        for index, step in enumerate(copied):
            if not isinstance(step, dict) or "action" not in step:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Assembly step {index} has no 'action' key (found: {list(step) if isinstance(step, dict) else type(step).__name__}).",
                    location=f"assembly step {index}",
                    fix="Write every step as `- action: polars_join` with its parameters; the shorthand `- join: {...}` is not read.",
                    who="data_analysis_recipe_author", category="assembly", surface="plot_overlay", severity="error",
                    reference="recipe_format_spec.md 7.5",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe)
        return copied

    def assemble(self, steps: List[Dict[str, Any]]) -> pl.LazyFrame:
        """
        Executes the assembly steps (joins, filters, renames) sequentially.
        Includes ADR-024 Short-Circuit logic for Tier 1 Parquet anchors.
        Handles optional ingredients and defensive join logic (ADR-012/014).

        Args:
            steps: List of assembly actions (e.g., polars_join).

        Returns:
            A consolidated Polars LazyFrame.
        """
        steps = self._canonical_steps(steps)

        # --- Defensive Identity Logic (ADR-014) ---
        if not steps or len(self.ingredients) == 0:
            if len(self.ingredients) == 1:
                return list(self.ingredients.values())[0]
            pe = PipelineError(
                component="DataAssembler",
                problem="No step list and no ingredients — cannot assemble.",
                location="assemble() entry",
                fix="Verify that the data analysis recipe declares at least one data_schema and a joins step list.",
                who="data_analysis_recipe_author",
                category="assembly",
                surface="plot_overlay",
                severity="error",
                reference="rules_data_analysis_recipe_structure.md §7",
            )
            print(pe.format())
            raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe)

        consolidated_lf: pl.LazyFrame = None
        start_index = 0

        # Process the remaining steps
        for i in range(start_index, len(steps)):
            step = steps[i]
            action_name = step.get("action")
            if not action_name:
                continue

            # Resolve the right-hand ingredient if it's a join-type action
            right_id = step.get("right_ingredient")
            if right_id:
                # Crash if ingredient is missing — the data analysis recipe's right_ingredient key is wrong.
                if right_id not in self.ingredients:
                    available = ", ".join(self.ingredients.keys())
                    pe = PipelineError(
                        component="DataAssembler",
                        problem=f"Ingredient '{right_id}' required by '{action_name}' step is not available.",
                        location=f"assembly step {i}: action='{action_name}', right_ingredient='{right_id}'",
                        fix=f"Check right_ingredient spelling. Available ingredients: {available}",
                        who="data_analysis_recipe_author",
                        category="assembly",
                        surface="plot_overlay",
                        severity="error",
                        evidence={"available_ingredients": available},
                        reference="rules_data_analysis_recipe_structure.md §7",
                    )
                    print(pe.format())
                    raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe)

                # DEFENSIVE: Skip if join keys are missing (ADR-012)
                # We check multiple possible keys to be extremely robust
                join_key = (step.get("on") or
                            step.get("left_on") or
                            step.get("on_column") or
                            step.get(True))  # Handle YAML boolean 'on'

                if action_name == JOIN and not join_key:
                    actual_keys = list(step.keys())
                    pe = PipelineError(
                        component="DataAssembler",
                        problem=f"Join key missing for '{action_name}' with right_ingredient='{right_id}'.",
                        location=f"assembly step {i}: action='{action_name}'",
                        fix=(
                            "Add 'on': <column> to the join step (quoted — 'on' is a YAML boolean trap). "
                            f"Found keys in step: {actual_keys}"
                        ),
                        who="data_analysis_recipe_author",
                        category="assembly",
                        surface="plot_overlay",
                        severity="error",
                        evidence={"step_keys_found": str(actual_keys)},
                        reference="docs/appendix/data_analysis_recipe_structure.yaml §yaml_resilience",
                    )
                    print(pe.format())
                    raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe)

                step["__right_df__"] = self.ingredients[right_id]

            # Initialize base if this is the first effective step
            if consolidated_lf is None:
                first_key = list(self.ingredients.keys())[0]
                consolidated_lf = self.ingredients[first_key]

                # If first step is a join involving original backbone, skip redundant init
                if action_name == JOIN and right_id == first_key:
                    continue

            if action_name == JOIN and right_id:
                self._check_join_key_types(step, i, consolidated_lf, self.ingredients[right_id])

            # Execute the action via the shared registry (ADR-018).
            # Wrap Polars and registry errors in PipelineError for structured diagnostics
            # (ADR-079 Phase 2 — DIAG-RUNTIME-ASSEMBLER-1).
            try:
                action_func = get_action_function(action_name)
            except ValueError as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Unknown assembly action '{action_name}'.",
                    location=f"assembly step {i}",
                    fix=(
                        f"'{action_name}' is not registered. Check the action name in the data analysis recipe. "
                        "See rules_agent_role_bioscientist.md §8 for the authoritative action list."
                    ),
                    who="data_analysis_recipe_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    reference="rules_agent_role_bioscientist.md §8",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc

            try:
                consolidated_lf = action_func(consolidated_lf, step)
            except pl.exceptions.ColumnNotFoundError as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Column not found during '{action_name}': {exc}",
                    location=f"assembly step {i}: action='{action_name}'",
                    fix=(
                        "Verify the column exists at this point in the step list. "
                        "Columns from a joined ingredient are only available AFTER the join step."
                    ),
                    who="data_analysis_recipe_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"polars_error": str(exc)},
                    reference="rules_agent_role_bioscientist.md §3-B",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc
            except pl.exceptions.SchemaError as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Schema mismatch during '{action_name}': {exc}",
                    location=f"assembly step {i}: action='{action_name}'",
                    fix=(
                        "Join keys on both sides must share the same dtype. "
                        "Add a cast step before the join to normalise the mismatched column."
                    ),
                    who="data_analysis_recipe_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"polars_error": str(exc)},
                    reference="rules_agent_role_bioscientist.md §3-B",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc
            except Exception as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Assembly step '{action_name}' raised an unexpected error: {type(exc).__name__}",
                    location=f"assembly step {i}: action='{action_name}'",
                    fix="Review the step parameters and the data state at this point in the step list.",
                    who="data_analysis_recipe_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc

        return consolidated_lf
