from __future__ import annotations

import re
import polars as pl
from .data_structures import MatchResult

_DELIM_RE = re.compile(r"[_\-]")

# @deps
# provides: exact_match, fuzzy_match_batch
# consumes: libs/id_reconciliation/src/id_reconciliation/data_structures.py
# consumed_by: libs/id_reconciliation/src/id_reconciliation/core.py
# @end_deps


def exact_match(ref_ids: list[str], target_ids: list[str]) -> list[MatchResult]:
    """Return MatchResult for each ref_id; exact string equality only."""
    target_set = set(target_ids)
    results = []
    for ref in ref_ids:
        if ref in target_set:
            results.append(MatchResult(ref_id=ref, target_id=ref, match_type="exact", certainty=1.0))
        else:
            results.append(MatchResult(ref_id=ref, target_id=None, match_type="unmatched", certainty=0.0))
    return results


def fuzzy_match_batch(
    unmatched_refs: list[str],
    target_ids: list[str],
    score_cutoff: float = 70.0,
) -> list[MatchResult]:
    """Fuzzy-match unmatched ref IDs against target_ids using rapidfuzz token_set_ratio.

    Underscores and hyphens are normalized to spaces before scoring so that
    rearranged segments (e.g. ABCD_001 vs 001_ABCD) are scored correctly.
    Score cutoff is on the 0–100 scale; certainty stored as 0.0–0.99.
    """
    from rapidfuzz import process, fuzz

    def _norm(s: str) -> str:
        return _DELIM_RE.sub(" ", s)

    normalized_targets = [_norm(t) for t in target_ids]

    results = []
    for ref in unmatched_refs:
        match = process.extractOne(
            _norm(ref),
            normalized_targets,
            scorer=fuzz.token_set_ratio,
            score_cutoff=score_cutoff,
        )
        if match is not None:
            _, score, idx = match
            best_target = target_ids[idx]
            results.append(
                MatchResult(
                    ref_id=ref,
                    target_id=best_target,
                    match_type="fuzzy",
                    certainty=round(score / 100.0, 4),
                )
            )
        else:
            results.append(MatchResult(ref_id=ref, target_id=None, match_type="unmatched", certainty=0.0))
    return results
