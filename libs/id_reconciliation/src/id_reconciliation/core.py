from __future__ import annotations

import re

import polars as pl
from utils.formula_check import evaluate_formula
from utils.id_patterns import PatternSuggestion, apply_pattern, suggest_regex
from .data_structures import IDPair, MatchResult, IdTransformation
from .matcher import exact_match, fuzzy_match_batch
from .pattern_detector import detect_patterns

# @deps
# provides: IDReconciliationEngine, detect_many_to_many, format_match_table, apply_recode_step
# consumes: libs/utils/src/utils/id_patterns.py,
#           libs/id_reconciliation/src/id_reconciliation/matcher.py,
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

    def generate_transformation(
        self,
        results: list[MatchResult],
        ref_column: str,
        target_column: str,
    ) -> IdTransformation:
        """Build an IdTransformation from reconciliation results.

        Infers cleaning steps from the transform_applied fields on matched results
        and includes an explicit recode map for remaining fuzzy matches.

        The steps are in this library's own step language (`apply_recode_step`); `recipe_steps` writes them as
        steps of a data analysis recipe. Raises ValueError for a transform_applied that no step can be made for:
        a match by a pattern must not give a transformation that lacks its step.
        """
        steps: list[dict] = []
        seen_transforms: set[str] = set()

        for r in results:
            if r.transform_applied and r.transform_applied not in seen_transforms:
                seen_transforms.add(r.transform_applied)
                # The descriptions are the ones utils.id_patterns.detect_patterns writes
                desc = r.transform_applied.lower()
                if "lowercas" in desc:
                    steps.append({"action": "lowercase"})
                elif "whitespace" in desc or "strip" in desc:
                    steps.append({"action": "strip_whitespace"})
                elif "delimiter" in desc or "swap" in desc:
                    steps.append({"action": "regex_replace", "pattern": "_", "replacement": "-"})
                elif "prefix" in desc or "removing first" in desc:
                    n = _character_count(r.transform_applied)
                    steps.append({"action": "regex_replace", "pattern": f"^.{{{n}}}", "replacement": ""})
                elif "suffix" in desc or "removing last" in desc:
                    n = _character_count(r.transform_applied)
                    steps.append({"action": "regex_replace", "pattern": f".{{{n}}}$", "replacement": ""})
                else:
                    raise ValueError(
                        f"No ID cleaning step is known for the pattern {r.transform_applied!r}: "
                        "the transformation would lack the step that made these IDs match.")

        fuzzy_pairs = [(r.ref_id, r.target_id) for r in results if r.match_type == "fuzzy" and r.target_id]
        metadata: dict = {}
        if fuzzy_pairs:
            metadata["fuzzy_recode_map"] = {orig: target for orig, target in fuzzy_pairs}

        return IdTransformation(
            ref_column=ref_column,
            target_column=target_column,
            steps=steps,
            metadata=metadata,
        )


def _character_count(description: str) -> int:
    """The number of characters a prefix or suffix removal takes off, read from its description ("... 7 character(s)")."""
    found = re.search(r"(\d+) character", description)
    count = int(found.group(1)) if found else 0
    if count < 1:
        raise ValueError(
            f"The pattern {description!r} does not say how many characters it removes: no ID cleaning step can be "
            "made for it.")
    return count


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
    id_transformation: IdTransformation,
) -> pl.DataFrame:
    """Apply recode steps from an IdTransformation to a DataFrame column.

    Supported actions: strip_whitespace, cast_string, regex_replace, lowercase,
    mutate (Polars expression string), drop_duplicates, null_if, drop_nulls.
    """
    for step in id_transformation.steps:
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
            # expression is a Polars expression string, checked (utils.formula_check) before it runs: only pl is in scope
            expr = evaluate_formula(step.get("expression", ""))
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
