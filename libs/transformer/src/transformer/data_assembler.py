# @deps
# provides: class:DataAssembler, method:assemble
# consumes: libs/transformer/src/transformer/actions/ (all registered actions via registry)
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-ASSEMBLER-1)
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/rules/rules_manifest_structure.md#7
# @end_deps
import os
from typing import Dict, List, Any
import polars as pl
from transformer.registry import get_action_function
from utils.hashing import generate_config_hash, get_parquet_metadata_hash
from utils.errors import TransformationError
from utils.pipeline_error import PipelineError


class DataAssembler:
    """
    Orchestrates the assembly of multiple wrangled datasets (ingredients)
    into a final consolidated LazyFrame based on a relational recipe.
    """

    def __init__(self, ingredients: Dict[str, pl.LazyFrame]):
        """
        Args:
             ingredients: Dictionary mapping dataset_ids to their wrangled LazyFrames.
        """
        self.ingredients = ingredients

    @staticmethod
    def _normalize_recipe(recipe: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pre-normalization pass: expands shorthand step syntax to canonical form.

        Supported shorthand forms:
          {join: {on: key, right_ingredient: id}}
            → {action: join, on: key, right_ingredient: id}

          {select: [col1, col2]}
            → {action: select, columns: [col1, col2]}

          {mutate: {col: expr}}
            → {action: mutate, col: col, expr: expr}   (single mutation per step)

        Canonical steps (with explicit 'action' key) pass through unchanged.
        """
        import copy
        normalized = []
        _KNOWN_SHORTHAND = {"join", "join_filter", "select", "filter",
                            "rename", "drop", "mutate", "sink_parquet"}
        for raw_step in recipe:
            step = copy.deepcopy(raw_step)
            if "action" in step:
                # Already canonical
                normalized.append(step)
                continue

            # Detect shorthand: single top-level key that is a known action name
            top_keys = [k for k in step.keys() if k in _KNOWN_SHORTHAND]
            if len(top_keys) == 1:
                action_name = top_keys[0]
                payload = step[action_name]
                canonical = {"action": action_name}
                if isinstance(payload, dict):
                    canonical.update(payload)
                elif isinstance(payload, list):
                    # e.g. {select: [col1, col2]} → {action: select, columns: [...]}
                    canonical["columns"] = payload
                elif isinstance(payload, str):
                    # e.g. {filter: "col == val"} — pass as expr
                    canonical["expr"] = payload
                normalized.append(canonical)
                print(f"  └── 🔧 Normalized shorthand '{action_name}' → canonical step.")
            else:
                # Unknown form — pass through to let the registry raise a helpful error
                normalized.append(step)

        return normalized

    def assemble(self, recipe: List[Dict[str, Any]]) -> pl.LazyFrame:
        """
        Executes the assembly steps (joins, filters, renames) sequentially.
        Includes ADR-024 Short-Circuit logic for Tier 1 Parquet anchors.
        Handles optional ingredients and defensive join logic (ADR-012/014).

        Args:
            recipe: List of assembly actions (e.g., join, join_filter, sink_parquet).

        Returns:
            A consolidated Polars LazyFrame.
        """
        # Expand any shorthand syntax before hashing or executing
        recipe = self._normalize_recipe(recipe)

        # --- Defensive Identity Logic (ADR-014) ---
        if not recipe or len(self.ingredients) == 0:
            if len(self.ingredients) == 1:
                return list(self.ingredients.values())[0]
            pe = PipelineError(
                component="DataAssembler",
                problem="No recipe and no ingredients — cannot assemble.",
                location="assemble() entry",
                fix="Verify that the manifest declares at least one data_schema and a join_manifests recipe.",
                who="manifest_author",
                category="assembly",
                surface="plot_overlay",
                severity="error",
                reference="rules_manifest_structure.md §7",
            )
            print(pe.format())
            raise TransformationError(pe.problem, tip=pe.fix)

        # --- Decision Metadata Hash Calculation (ADR-024 refinement) ---
        # ADR-016: We hash a clean copy of the recipe to avoid mutation-induced invalidation.
        # We strip internal/injected keys (starts with __ or specific cache keys)
        import copy
        clean_recipe = copy.deepcopy(recipe)
        for step in clean_recipe:
            keys_to_purge = [k for k in step.keys() if isinstance(k, str) and (k.startswith(
                "__") or k in ("decision_hash",))]
            for k in keys_to_purge:
                step.pop(k, None)

        decision_hash = generate_config_hash(clean_recipe)

        consolidated_lf: pl.LazyFrame = None
        start_index = 0

        # --- ADR-024: Tier 1/2 Short-Circuit Logic ---
        for i in range(len(recipe) - 1, -1, -1):
            step = recipe[i]
            if step.get("action") == "sink_parquet":
                path = step.get("path")
                force = step.get("force_recompute", False)
                if path and os.path.exists(path) and not force:
                    # Verify if the logic (manifest) has changed since last materialization
                    existing_hash = get_parquet_metadata_hash(path)
                    if existing_hash == decision_hash:
                        print(
                            f"  ─── Short-Circuit: Valid Parquet branch found at {path}. Skipping early steps.")
                        consolidated_lf = pl.scan_parquet(path)
                        start_index = i + 1
                        break
                    else:
                        print(
                            f"  ─── WARNING: Cache Invalidation: Logic change detected for {path}. Recomputing...")

        # Process the remaining steps
        for i in range(start_index, len(recipe)):
            step = recipe[i]
            action_name = step.get("action")
            if not action_name:
                continue

            # Inject the decision hash into sink steps so they can persist it
            if action_name == "sink_parquet":
                step["decision_hash"] = decision_hash

            # Resolve the right-hand ingredient if it's a join-type action
            right_id = step.get("right_ingredient")
            if right_id:
                # Crash if ingredient is missing — the manifest's right_ingredient key is wrong.
                if right_id not in self.ingredients:
                    available = ", ".join(self.ingredients.keys())
                    pe = PipelineError(
                        component="DataAssembler",
                        problem=f"Ingredient '{right_id}' required by '{action_name}' step is not available.",
                        location=f"assembly step {i}: action='{action_name}', right_ingredient='{right_id}'",
                        fix=f"Check right_ingredient spelling. Available ingredients: {available}",
                        who="manifest_author",
                        category="assembly",
                        surface="plot_overlay",
                        severity="error",
                        evidence={"available_ingredients": available},
                        reference="rules_manifest_structure.md §7",
                    )
                    print(pe.format())
                    raise TransformationError(pe.problem, tip=pe.fix)

                # DEFENSIVE: Skip if join keys are missing (ADR-012)
                # We check multiple possible keys to be extremely robust
                join_key = (step.get("on") or
                            step.get("left_on") or
                            step.get("on_column") or
                            step.get(True))  # Handle YAML boolean 'on'

                if action_name in ("join", "join_filter") and not join_key:
                    actual_keys = list(step.keys())
                    pe = PipelineError(
                        component="DataAssembler",
                        problem=f"Join key missing for '{action_name}' with right_ingredient='{right_id}'.",
                        location=f"assembly step {i}: action='{action_name}'",
                        fix=(
                            "Add 'on': <column> to the join step (quoted — 'on' is a YAML boolean trap). "
                            f"Found keys in step: {actual_keys}"
                        ),
                        who="manifest_author",
                        category="assembly",
                        surface="plot_overlay",
                        severity="error",
                        evidence={"step_keys_found": str(actual_keys)},
                        reference="docs/appendix/manifest_structure.yaml §yaml_resilience",
                    )
                    print(pe.format())
                    raise TransformationError(pe.problem, tip=pe.fix)

                step["__right_df__"] = self.ingredients[right_id]

            # Initialize base if this is the first effective step
            if consolidated_lf is None:
                first_key = list(self.ingredients.keys())[0]
                consolidated_lf = self.ingredients[first_key]

                # If first step is a join involving original backbone, skip redundant init
                if action_name == "join" and right_id == first_key:
                    continue

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
                        f"'{action_name}' is not registered. Check the action name in the manifest recipe. "
                        "See rules_persona_bioscientist.md §8 for the authoritative action list."
                    ),
                    who="manifest_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    reference="rules_persona_bioscientist.md §8",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix) from exc

            try:
                consolidated_lf = action_func(consolidated_lf, step)
            except pl.exceptions.ColumnNotFoundError as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Column not found during '{action_name}': {exc}",
                    location=f"assembly step {i}: action='{action_name}'",
                    fix=(
                        "Verify the column exists at this point in the recipe. "
                        "Columns from a joined ingredient are only available AFTER the join step."
                    ),
                    who="manifest_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"polars_error": str(exc)},
                    reference="rules_persona_bioscientist.md §3-B",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix) from exc
            except pl.exceptions.SchemaError as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Schema mismatch during '{action_name}': {exc}",
                    location=f"assembly step {i}: action='{action_name}'",
                    fix=(
                        "Join keys on both sides must share the same dtype. "
                        "Add a cast step before the join to normalise the mismatched column."
                    ),
                    who="manifest_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"polars_error": str(exc)},
                    reference="rules_persona_bioscientist.md §3-B",
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix) from exc
            except Exception as exc:
                pe = PipelineError(
                    component="DataAssembler",
                    problem=f"Assembly step '{action_name}' raised an unexpected error: {type(exc).__name__}",
                    location=f"assembly step {i}: action='{action_name}'",
                    fix="Review the step parameters and the data state at this point in the recipe.",
                    who="manifest_author",
                    category="assembly",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
                )
                print(pe.format())
                raise TransformationError(pe.problem, tip=pe.fix) from exc

        return consolidated_lf
