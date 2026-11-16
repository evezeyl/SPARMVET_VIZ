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
from polars.exceptions import PanicException
from transformer.registry import get_action_function
from utils.action_names import CAST, JOIN, JOIN_ASOF
from transformer.join_diagnosis import JoinCheck
from utils.errors import TransformationError
from utils import join_keys
from utils.step_migration import removed_action_catalog
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
        self.join_checks: List[JoinCheck] = []  # the joins that write `validate`, for the plain message of a refusal (join_diagnosis)

    @staticmethod
    def _key_columns(value: Any) -> List[str]:
        if value is None:
            return []
        return [value] if isinstance(value, str) else list(value)

    def _fail_join(self, step: Dict[str, Any], index: int, problem: str, fix: str, evidence: Dict[str, Any]) -> None:
        """Raise the error of a join that cannot run, with the recipe, the join and the step named."""
        right_id = step["right_ingredient"]
        pe = PipelineError(
            component="DataAssembler", problem=problem,
            location=f"data analysis recipe '{self.recipe_id}', join '{self.join_id}', assembly step {index}: action='{step['action']}', right_ingredient='{right_id}'",
            fix=fix, who="data_analysis_recipe_author", category="assembly", surface="plot_overlay", severity="error",
            evidence=evidence, reference="recipe_format_spec.md 7.5",
        )
        print(pe.format())
        raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe)

    def _key_groups(self, step: Dict[str, Any]) -> List[tuple]:
        """The key columns of a join step as (left keys, right keys, left parameter, right parameter, shared parameter).

        A join has one group (`on`, or `left_on` with `right_on`); an as-of join has a second one, the groups of `by`.
        """
        groups = [(self._key_columns(step.get("on") or step.get("left_on")), self._key_columns(step.get("on") or step.get("right_on")),
                   "left_on", "right_on", "on")]
        if step["action"] == JOIN_ASOF:
            by = step.get("by")
            groups.append((self._key_columns(by or step.get("by_left")), self._key_columns(by or step.get("by_right")),
                           "by_left", "by_right", "by"))
        return groups

    def _check_join_key_types(self, step: Dict[str, Any], index: int, left: pl.LazyFrame, right: pl.LazyFrame) -> None:
        """Fail when the keys of a join cannot be joined: unequal key lists, a missing key column, or different types.

        Eve 2026-11-14: a join keeps the types the tables have; a change of type is a decision written in the
        recipe (input_fields or a polars_cast step), never done here. The same holds for the other two problems:
        they fail here with a plain message that names the recipe, the join and the step, not later with a raw
        Polars error. The keys of `by` of an as-of join are checked the same way.
        """
        left_schema, right_schema = left.collect_schema(), right.collect_schema()
        right_id = step["right_ingredient"]
        where = f"in data analysis recipe '{self.recipe_id}', join '{self.join_id}', step {index} ({step['action']} with '{right_id}')"

        for left_keys, right_keys, left_name, right_name, shared_name in self._key_groups(step):
            problem = join_keys.join_key_problem(left_schema, right_schema, left_keys, right_keys)  # the one rule (utils.join_keys, JOIN-KEY-ONE-1)
            if problem is None:
                continue
            if problem["kind"] == "length":
                self._fail_join(
                    step, index,
                    f"The key lists of the join differ in length {where}: {left_name} has {len(left_keys)} column(s) {left_keys} and {right_name} has {len(right_keys)} column(s) {right_keys}.",
                    f"Write {left_name} and {right_name} with the same number of columns, paired by position (the first of {left_name} with the first of {right_name}), "
                    f"or write '{shared_name}' when the columns have the same name in both tables.",
                    {"left_keys": str(left_keys), "right_keys": str(right_keys)},
                )
            if problem["kind"] == "missing":
                missing_left, missing_right = problem["missing_left"], problem["missing_right"]
                lacks = []
                if missing_left:
                    lacks.append(f"key column(s) {missing_left} missing in the left table (its columns: {list(left_schema)})")
                if missing_right:
                    lacks.append(f"key column(s) {missing_right} missing in '{right_id}' (its columns: {list(right_schema)})")
                self._fail_join(
                    step, index,
                    f"A join key column does not exist {where}: " + "; ".join(lacks) + ".",
                    f"Write the key column names as they are in each table: '{shared_name}' for a name that is the same in both, {left_name} and {right_name} for names that differ. "
                    "The left table is the table at this step: a column of a table joined later is not in it yet, and a step before the join may have renamed or dropped the column.",
                    {"missing_in_left": str(missing_left), "missing_in_right": str(missing_right)},
                )
            first = problem["differing"][0]
            left_col, right_col, left_type, right_type = first["left_column"], first["right_column"], first["left_type"], first["right_type"]
            names = f"column '{left_col}'" if left_col == right_col else f"column '{left_col}' (left) and '{right_col}' (right)"
            self._fail_join(
                step, index,
                f"The join key types differ {where}: {names} is {left_type} in the left table and {right_type} in '{right_id}'.",
                f"Declare the same type for this field in input_fields of both tables. A {CAST} step before the join changes only the left table "
                f"(the table at this step); the type of '{right_id}' is changed in its own input_fields or in its own wrangling. "
                "The engine does not change the type of a join key for you.",
                {"left_column": left_col, "right_column": right_col, "left_type": str(left_type), "right_type": str(right_type)},
            )

    def _check_anti_join_with_itself(self, earlier: List[Dict[str, Any]], step: Dict[str, Any], index: int, base_id: str) -> None:
        """Fail on the anti-join of the base table with itself on the same key (D-0078): it would return no row, silently.

        The rule and the words are `utils.join_keys` (the checker says the same, J15). Every other self-join runs as written.
        """
        found = join_keys.anti_join_with_itself(base_id, earlier, step)
        if found is None:
            return
        what, fix = join_keys.anti_join_with_itself_text(found)
        self._fail_join(step, index, what, fix, {"table": found["table"], "keys": str(found["keys"])})

    @staticmethod
    def _canonical_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """A copy of the steps; every step must be written with its `action` key (no shorthand is guessed)."""
        import copy
        copied = copy.deepcopy(steps)
        for index, step in enumerate(copied, start=1):
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
        # the same steps without any `validate`: the table each join sees if no earlier validation counted, for the plain message of a refusal
        plain_lf: pl.LazyFrame = None
        track_plain = any(isinstance(s, dict) and s.get("validate") in ("1:1", "1:m", "m:1") for s in steps)
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
                        location=f"assembly step {i + 1}: action='{action_name}', right_ingredient='{right_id}'",
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

                if action_name in (JOIN, JOIN_ASOF) and not join_key:
                    actual_keys = list(step.keys())
                    pe = PipelineError(
                        component="DataAssembler",
                        problem=f"Join key missing for '{action_name}' with right_ingredient='{right_id}'.",
                        location=f"assembly step {i + 1}: action='{action_name}'",
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
                plain_lf = consolidated_lf

            if action_name == JOIN and right_id:
                self._check_anti_join_with_itself(steps[:i], step, i + 1, list(self.ingredients)[0])

            if action_name in (JOIN, JOIN_ASOF) and right_id:
                self._check_join_key_types(step, i + 1, consolidated_lf, self.ingredients[right_id])

            if action_name == JOIN and right_id and step.get("validate") in ("1:1", "1:m", "m:1"):
                # Polars decides whether the join fails; this only lets the engine explain the failure afterwards (join_diagnosis)
                left_keys = step.get("on") or step.get("left_on")
                right_keys = step.get("on") or step.get("right_on")
                if isinstance(left_keys, list) and isinstance(right_keys, list):
                    self.join_checks.append(JoinCheck(
                        location=f"data analysis recipe '{self.recipe_id}', join '{self.join_id}', assembly step {i + 1}",
                        right_id=right_id, left=plain_lf, right=self.ingredients[right_id], validate=step["validate"],
                        left_keys=left_keys, right_keys=right_keys, nulls_equal=bool(step.get("nulls_equal")), how=str(step.get("how", "left"))))

            # Execute the action via the shared registry (ADR-018).
            # Wrap Polars and registry errors in PipelineError for structured diagnostics
            # (ADR-079 Phase 2 — DIAG-RUNTIME-ASSEMBLER-1).
            try:
                action_func = get_action_function(action_name)
            except ValueError as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Unknown assembly action '{action_name}'.",
                    location=f"assembly step {i + 1}",
                    fix=str(exc) if action_name in removed_action_catalog() else (
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
                if track_plain:
                    plain_lf = action_func(plain_lf, {k: v for k, v in step.items() if k != "validate"})
            except pl.exceptions.ColumnNotFoundError as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Column not found during '{action_name}': {exc}",
                    location=f"assembly step {i + 1}: action='{action_name}'",
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
                    location=f"assembly step {i + 1}: action='{action_name}'",
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
            except TransformationError as exc:
                # an action that refuses its step already says why in plain words (a missing parameter, a table that is not sorted):
                # keep that message and add where it happened, never reduce it to the name of the exception
                pe = PipelineError(
                    component="DataAssembler",
                    problem=str(exc),
                    location=f"data analysis recipe '{self.recipe_id}', join '{self.join_id}', assembly step {i + 1}: action='{action_name}'",
                    fix=getattr(exc, "tip", None) or "Review the step parameters and the data state at this point in the step list.",
                    who="data_analysis_recipe_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc
            except PanicException as exc:
                # a Rust panic of Polars is a BaseException: without this clause it passes every `except Exception` of the engine and the app
                # (ADR-104). Only this class is caught here; KeyboardInterrupt and SystemExit pass.
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Polars stopped at assembly step {i + 1} ('{action_name}') on this input ({str(exc).strip()[:120]})",
                    location=f"data analysis recipe '{self.recipe_id}', join '{self.join_id}', assembly step {i + 1}: action='{action_name}'",
                    fix="Check the values written in this step (a zero or very fine duration, an empty list) and the data it works on; "
                        "the action could not refuse this input before Polars ran.",
                    who="data_analysis_recipe_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"error_type": "PanicException", "error_detail": str(exc)[:200]},
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix, pipeline_error=pe) from exc
            except Exception as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Assembly step '{action_name}' raised an unexpected error: {type(exc).__name__}",
                    location=f"assembly step {i + 1}: action='{action_name}'",
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
