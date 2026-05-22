from __future__ import annotations

import polars as pl
from .data_structures import IDPair, MatchResult, PatternSuggestion, TransformationRecipe
from .matcher import exact_match, fuzzy_match_batch
from .pattern_detector import detect_patterns

# @deps
# provides: IDReconciliationEngine, detect_many_to_many, format_match_table, apply_recode_step
# consumes: libs/id_reconciliation/src/id_reconciliation/matcher.py,
#           libs/id_reconciliation/src/id_reconciliation/pattern_detector.py,
#           libs/id_reconciliation/src/id_reconciliation/data_structures.py
# consumed_by: libs/id_reconciliation/src/id_reconciliation/__init__.py
# @end_deps


class IDReconciliationEngine:
    """Orchestrates pairwise ID reconciliation between two single key columns.

    Each run is stateless — no state persists between calls.
    """

    def __init__(
        self,
        fuzzy_cutoff: float = 70.0,
        chunk_size: int = 50,
    ) -> None:
        self.fuzzy_cutoff = fuzzy_cutoff
        self.chunk_size = chunk_size

    def reconcile(
        self,
        ref_ids: list[str],
        target_ids: list[str],
    ) -> list[MatchResult]:
        """Run exact → pattern-detected → fuzzy matching pipeline.

        Returns results sorted by certainty descending (highest confidence first).
        """
        results: list[MatchResult] = []

        exact_results = exact_match(ref_ids, target_ids)
        matched_refs = {r.ref_id for r in exact_results if r.match_type == "exact"}
        results.extend(r for r in exact_results if r.match_type == "exact")

        unmatched_refs = [r for r in ref_ids if r not in matched_refs]
        if not unmatched_refs:
            return sorted(results, key=lambda r: r.certainty, reverse=True)

        # Pattern pass — apply best suggestion if any
        suggestions = detect_patterns(unmatched_refs, target_ids)
        if suggestions:
            from .pattern_detector import apply_pattern
            best = suggestions[0]
            transformed = apply_pattern(unmatched_refs, best)
            target_set = set(target_ids)
            still_unmatched = []
            for orig, transformed_id in zip(unmatched_refs, transformed):
                if transformed_id in target_set:
                    results.append(MatchResult(
                        ref_id=orig,
                        target_id=transformed_id,
                        match_type="pattern",
                        certainty=0.95,
                        transform_applied=best.description,
                    ))
                else:
                    still_unmatched.append(orig)
            unmatched_refs = still_unmatched

        # Fuzzy pass on remaining unmatched
        if unmatched_refs:
            fuzzy_results = fuzzy_match_batch(unmatched_refs, target_ids, self.fuzzy_cutoff)
            results.extend(fuzzy_results)

        return sorted(results, key=lambda r: r.certainty, reverse=True)

    def suggest_patterns(
        self,
        ref_ids: list[str],
        target_ids: list[str],
    ) -> list[PatternSuggestion]:
        """Return pattern suggestions without running the full reconciliation."""
        return detect_patterns(ref_ids, target_ids)


def detect_many_to_many(results: list[MatchResult]) -> dict[str, list[str]]:
    """Return dict of ref_id → [target_ids] for cases with multiple matches (many-to-many warning)."""
    from collections import defaultdict
    mapping: dict[str, list[str]] = defaultdict(list)
    for r in results:
        if r.target_id is not None:
            mapping[r.ref_id].append(r.target_id)
    return {k: v for k, v in mapping.items() if len(v) > 1}


def format_match_table(results: list[MatchResult]) -> pl.DataFrame:
    """Return a Polars DataFrame of reconciliation results, sorted by certainty descending."""
    return pl.DataFrame({
        "ref_id": [r.ref_id for r in results],
        "target_id": [r.target_id for r in results],
        "match_type": [r.match_type for r in results],
        "certainty": [r.certainty for r in results],
        "transform_applied": [r.transform_applied for r in results],
    }).sort("certainty", descending=True)


def apply_recode_step(
    df: pl.DataFrame,
    column: str,
    recipe: TransformationRecipe,
) -> pl.DataFrame:
    """Apply recode steps from a TransformationRecipe to a DataFrame column."""
    for step in recipe.steps:
        action = step.get("action")
        if action == "strip_whitespace":
            df = df.with_columns(pl.col(column).str.strip_chars())
        elif action == "cast_string":
            df = df.with_columns(pl.col(column).cast(pl.String))
        elif action == "regex_replace":
            pattern = step.get("pattern", "")
            replacement = step.get("replacement", "")
            df = df.with_columns(pl.col(column).str.replace_all(pattern, replacement))
        elif action == "lowercase":
            df = df.with_columns(pl.col(column).str.to_lowercase())
    return df
