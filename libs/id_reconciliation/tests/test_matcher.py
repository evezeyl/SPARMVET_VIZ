"""Tests for exact and fuzzy matching engines."""
import pytest
from id_reconciliation.matcher import exact_match, fuzzy_match_batch


def test_exact_match_hit():
    results = exact_match(["ABCD_001", "ABCD_002"], ["ABCD_001", "ABCD_003"])
    by_ref = {r.ref_id: r for r in results}
    assert by_ref["ABCD_001"].match_type == "exact"
    assert by_ref["ABCD_001"].certainty == 1.0
    assert by_ref["ABCD_002"].match_type == "unmatched"


def test_fuzzy_match_rearranged_segments():
    # token_set_ratio should handle rearranged ID segments
    results = fuzzy_match_batch(["001_ABCD"], ["ABCD_001"], score_cutoff=70.0)
    assert results[0].match_type == "fuzzy"
    assert results[0].target_id == "ABCD_001"
    assert results[0].certainty > 0.7


def test_fuzzy_match_below_cutoff_returns_unmatched():
    results = fuzzy_match_batch(["XYZ999"], ["ABCD_001"], score_cutoff=90.0)
    assert results[0].match_type == "unmatched"
    assert results[0].certainty == 0.0
