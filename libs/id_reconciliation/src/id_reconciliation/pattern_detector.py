from __future__ import annotations

from .data_structures import MatchResult, PatternSuggestion

# @deps
# provides: detect_patterns, apply_pattern
# consumes: libs/id_reconciliation/src/id_reconciliation/data_structures.py
# consumed_by: libs/id_reconciliation/src/id_reconciliation/core.py
# @end_deps


def detect_patterns(
    unmatched_refs: list[str],
    target_ids: list[str],
) -> list[PatternSuggestion]:
    """Detect candidate transformations that would increase overlap between unmatched refs and targets.

    Checks: prefix/suffix removal, case normalization, delimiter substitution.
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

    # Common prefix removal — find longest common prefix length that yields matches
    if unmatched_refs:
        sample = unmatched_refs[:50]
        for prefix_len in range(1, 8):
            stripped = [r[prefix_len:] for r in sample if len(r) > prefix_len]
            hits = sum(1 for s in stripped if s in target_set)
            if hits >= 2:
                example = sample[0]
                suggestions.append(PatternSuggestion(
                    pattern_type="prefix_removal",
                    description=f"Removing first {prefix_len} character(s) from ref IDs",
                    example_before=example,
                    example_after=example[prefix_len:],
                    match_count=hits,
                ))
                break

        # Common suffix removal
        for suffix_len in range(1, 8):
            stripped = [r[:-suffix_len] for r in sample if len(r) > suffix_len]
            hits = sum(1 for s in stripped if s in target_set)
            if hits >= 2:
                example = sample[0]
                suggestions.append(PatternSuggestion(
                    pattern_type="suffix_removal",
                    description=f"Removing last {suffix_len} character(s) from ref IDs",
                    example_before=example,
                    example_after=example[:-suffix_len],
                    match_count=hits,
                ))
                break

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
