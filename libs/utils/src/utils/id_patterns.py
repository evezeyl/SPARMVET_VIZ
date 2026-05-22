from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# @deps
# provides: PatternSuggestion, detect_patterns, apply_pattern, suggest_regex
# consumes: —  (stdlib only)
# consumed_by: libs/id_reconciliation/src/id_reconciliation/pattern_detector.py,
#              libs/blueprint_arch/src/blueprint_arch/join_designer.py
# @end_deps


@dataclass
class PatternSuggestion:
    pattern_type: str  # "prefix_removal" | "suffix_removal" | "case_normalization" | "delimiter" | "regex"
    description: str
    regex_pattern: Optional[str] = None
    example_before: Optional[str] = None
    example_after: Optional[str] = None
    match_count: int = 0


def detect_patterns(
    unmatched_refs: list[str],
    target_ids: list[str],
) -> list[PatternSuggestion]:
    """Detect candidate transformations that would increase overlap between unmatched refs and targets.

    Checks: prefix/suffix removal (1–16 chars), case normalization, delimiter substitution.
    Returns suggestions sorted by match_count descending.
    """
    suggestions: list[PatternSuggestion] = []
    target_set_lower = {t.lower() for t in target_ids}
    target_set = set(target_ids)

    # Case normalization
    case_hits = sum(1 for r in unmatched_refs if r.lower() in target_set_lower)
    if case_hits:
        suggestions.append(PatternSuggestion(
            pattern_type="case_normalization",
            description="Lowercasing ref IDs matches target IDs",
            match_count=case_hits,
        ))

    # Delimiter substitution (underscore <-> hyphen)
    def swap_delimiter(s: str) -> str:
        return s.replace("_", "-") if "_" in s else s.replace("-", "_")

    delim_hits = sum(1 for r in unmatched_refs if swap_delimiter(r) in target_set)
    if delim_hits:
        suggestions.append(PatternSuggestion(
            pattern_type="delimiter",
            description="Swapping _ / - in ref IDs matches target IDs",
            match_count=delim_hits,
        ))

    # Common prefix removal — scan up to 16 chars (covers common bio prefixes like "sample_")
    if unmatched_refs:
        sample = unmatched_refs[:50]
        best_prefix: tuple[int, int] | None = None  # (hits, prefix_len)
        for prefix_len in range(1, 17):
            stripped = [r[prefix_len:] for r in sample if len(r) > prefix_len]
            hits = sum(1 for s in stripped if s in target_set)
            if hits >= 2:
                if best_prefix is None or hits > best_prefix[0]:
                    best_prefix = (hits, prefix_len)
        if best_prefix is not None:
            hits, prefix_len = best_prefix
            example = sample[0]
            suggestions.append(PatternSuggestion(
                pattern_type="prefix_removal",
                description=f"Removing first {prefix_len} character(s) from ref IDs",
                example_before=example,
                example_after=example[prefix_len:] if len(example) > prefix_len else "",
                match_count=hits,
            ))

        # Common suffix removal — scan up to 16 chars
        best_suffix: tuple[int, int] | None = None
        for suffix_len in range(1, 17):
            stripped = [r[:-suffix_len] for r in sample if len(r) > suffix_len]
            hits = sum(1 for s in stripped if s in target_set)
            if hits >= 2:
                if best_suffix is None or hits > best_suffix[0]:
                    best_suffix = (hits, suffix_len)
        if best_suffix is not None:
            hits, suffix_len = best_suffix
            example = sample[0]
            suggestions.append(PatternSuggestion(
                pattern_type="suffix_removal",
                description=f"Removing last {suffix_len} character(s) from ref IDs",
                example_before=example,
                example_after=example[:-suffix_len] if len(example) > suffix_len else "",
                match_count=hits,
            ))

    suggestions.sort(key=lambda s: s.match_count, reverse=True)
    return suggestions


def apply_pattern(ids: list[str], suggestion: PatternSuggestion) -> list[str]:
    """Apply a PatternSuggestion transformation to a list of IDs."""
    if suggestion.pattern_type == "case_normalization":
        return [s.lower() for s in ids]
    if suggestion.pattern_type == "delimiter":
        def swap(s: str) -> str:
            return s.replace("_", "-") if "_" in s else s.replace("-", "_")
        return [swap(s) for s in ids]
    if suggestion.pattern_type == "prefix_removal":
        n = len(suggestion.example_before or "") - len(suggestion.example_after or "")
        return [s[n:] if len(s) > n else s for s in ids]
    if suggestion.pattern_type == "suffix_removal":
        n = len(suggestion.example_before or "") - len(suggestion.example_after or "")
        return [s[:-n] if len(s) > n else s for s in ids]
    return ids


def suggest_regex(original: str, anchor: str) -> str:
    """Suggest a boundary-aware regex that extracts anchor from original.

    Generalizes digit runs (SAM001 → SAM\\d+) and adds non-alphanumeric
    boundary guards so patterns don't over-match embedded substrings.
    Returns r".*" when anchor is not found in original.
    """
    if anchor not in original:
        return r".*"

    escaped = re.escape(anchor)
    generalized = re.sub(r"\\d+|\d+", r"\\d+", escaped)
    return rf"(?:^|[^a-zA-Z0-9])({generalized})(?:$|[^a-zA-Z0-9])"
