"""Tests for pattern_detector — gate test for TL-IDLIB-PATTERN-1."""
import pytest
from id_reconciliation.pattern_detector import detect_patterns, apply_pattern, suggest_regex


def test_pattern_suggestion_prefix_sample():
    """Gate test: prefix 'sample_' detected and ranked first."""
    refs = [f"sample_{i:03d}" for i in range(1, 6)]   # sample_001 … sample_005
    targets = [f"{i:03d}" for i in range(1, 6)]        # 001 … 005

    suggestions = detect_patterns(refs, targets)

    assert len(suggestions) >= 1, "Expected at least one suggestion"
    top = suggestions[0]
    assert top.pattern_type == "prefix_removal"
    assert top.match_count == 5
    # The removed prefix is exactly "sample_" (7 chars)
    assert top.example_before.startswith("sample_")
    assert not top.example_after.startswith("sample_")


def test_detect_case_normalization():
    suggestions = detect_patterns(["ABCD", "EFGH"], ["abcd", "efgh"])
    types = [s.pattern_type for s in suggestions]
    assert "case_normalization" in types


def test_detect_delimiter_swap():
    suggestions = detect_patterns(["A_001", "B_002"], ["A-001", "B-002"])
    types = [s.pattern_type for s in suggestions]
    assert "delimiter" in types


def test_apply_pattern_prefix():
    from id_reconciliation.data_structures import PatternSuggestion
    suggestion = PatternSuggestion(
        pattern_type="prefix_removal",
        description="Removing first 7 character(s)",
        example_before="sample_001",
        example_after="001",
        match_count=3,
    )
    result = apply_pattern(["sample_001", "sample_002"], suggestion)
    assert result == ["001", "002"]


def test_suggest_regex_boundary():
    # Use non-numeric anchor so digit generalization does not interfere
    pattern = suggest_regex("SAM_CTRL", "CTRL")
    import re
    # Should match when anchor is surrounded by non-alphanumeric (underscore)
    assert re.search(pattern, "SAM_CTRL")
    # Should NOT match when anchor is embedded in solid alphanumeric — no delimiter
    assert not re.search(pattern, "SAMCTRLX")


def test_suggest_regex_digit_generalization():
    pattern = suggest_regex("SAM001", "SAM001")
    # Generalized pattern should have \d+
    assert r"\d+" in pattern


def test_suggest_regex_anchor_not_in_original():
    pattern = suggest_regex("ABCD", "XYZ")
    assert pattern == r".*"
