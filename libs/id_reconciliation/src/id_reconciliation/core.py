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

    def precheck_compatibility(
        self,
        ref_ids: list[str],
        target_ids: list[str],
        recode_threshold: int = 50,
    ) -> dict:
        """Quick compatibility summary before running full reconciliation.

        Returns a dict with: overlap_count, overlap_pct, unmatched_count,
        needs_cleaning (True if unmatched > recode_threshold), suggestions (top 3).
        """
        ref_set = set(ref_ids)
        target_set = set(target_ids)
        overlap = ref_set & target_set
        unmatched_count = len(ref_set) - len(overlap)
        suggestions = detect_patterns(
            [r for r in ref_ids if r not in target_set],
            target_ids,
        )
        return {
            "total_ref": len(ref_ids),
            "total_target": len(target_ids),
            "overlap_count": len(overlap),
            "overlap_pct": round(len(overlap) / max(len(ref_ids), 1) * 100, 1),
            "unmatched_count": unmatched_count,
            "needs_cleaning": unmatched_count > recode_threshold,
            "top_suggestions": suggestions[:3],
        }

    def match_pair(
        self,
        ref_lf: pl.LazyFrame,
        target_lf: pl.LazyFrame,
        ref_column: str,
        target_column: str,
    ) -> list[MatchResult]:
        """Reconcile two LazyFrames by key column; reads full columns into memory for matching.

        Progressive display is handled by the caller slicing `format_match_table` output
        in chunks of `self.chunk_size` rows.
        """
        ref_ids = (
            ref_lf.select(pl.col(ref_column).cast(pl.String).drop_nulls())
            .unique()
            .collect()[ref_column]
            .to_list()
        )
        target_ids = (
            target_lf.select(pl.col(target_column).cast(pl.String).drop_nulls())
            .unique()
            .collect()[target_column]
            .to_list()
        )
        return self.reconcile(ref_ids, target_ids)

    def generate_recipe(
        self,
        results: list[MatchResult],
        ref_column: str,
        target_column: str,
    ) -> TransformationRecipe:
        """Build a TransformationRecipe from reconciliation results.

        Infers cleaning steps from the transform_applied fields on matched results
        and includes an explicit recode map for remaining fuzzy matches.
        """
        from .pattern_detector import suggest_regex

        steps: list[dict] = []
        seen_transforms: set[str] = set()

        for r in results:
            if r.transform_applied and r.transform_applied not in seen_transforms:
                seen_transforms.add(r.transform_applied)
                desc = r.transform_applied.lower()
                if "lowercase" in desc or "case" in desc:
                    steps.append({"action": "lowercase"})
                elif "whitespace" in desc or "strip" in desc:
                    steps.append({"action": "strip_whitespace"})
                elif "delimiter" in desc or "swap" in desc:
                    steps.append({"action": "regex_replace", "pattern": "_", "replacement": "-"})
                elif "prefix" in desc or "removing first" in desc:
                    # Extract prefix length from description "Removing first N character(s)"
                    import re
                    m = re.search(r"(\d+) character", desc)
                    n = int(m.group(1)) if m else 0
                    if n:
                        steps.append({"action": "regex_replace", "pattern": f"^.{{{n}}}", "replacement": ""})
                elif "suffix" in desc or "removing last" in desc:
                    import re
                    m = re.search(r"(\d+) character", desc)
                    n = int(m.group(1)) if m else 0
                    if n:
                        steps.append({"action": "regex_replace", "pattern": f".{{{n}}}$", "replacement": ""})

        fuzzy_pairs = [(r.ref_id, r.target_id) for r in results if r.match_type == "fuzzy" and r.target_id]
        metadata: dict = {}
        if fuzzy_pairs:
            metadata["fuzzy_recode_map"] = {orig: target for orig, target in fuzzy_pairs}

        return TransformationRecipe(
            ref_column=ref_column,
            target_column=target_column,
            steps=steps,
            metadata=metadata,
        )


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
    """Apply recode steps from a TransformationRecipe to a DataFrame column.

    Supported actions: strip_whitespace, cast_string, regex_replace, lowercase,
    mutate (Polars expression string), drop_duplicates, null_if, drop_nulls.
    """
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
        elif action == "mutate":
            # expression is a Polars expression string; pl and column name are in scope
            expression = step.get("expression", "")
            expr = eval(expression, {"pl": pl, "col": column})  # noqa: S307
            df = df.with_columns(expr.alias(column))
        elif action == "drop_duplicates":
            df = df.unique(subset=[column], keep="first")
        elif action == "null_if":
            value = step.get("value", "")
            df = df.with_columns(
                pl.when(pl.col(column) == value).then(None).otherwise(pl.col(column)).alias(column)
            )
        elif action == "drop_nulls":
            df = df.drop_nulls(subset=[column])
    return df
