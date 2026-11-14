"""The cleaning steps suggested after a reconciliation do to the IDs what the matching did (task ID-RECON-STEPS-1).

The match table shows the user which IDs a pattern matched. The steps of the IdTransformation are what a recipe will
run later. If the two differ, the recipe does not give the matches the user accepted.

The defect tests are marked `xfail(strict=True)`: they describe what is wrong today and wait for a decision on how
the steps should be written (see the report of ID-RECON-STEPS-1). When a defect is fixed its test starts to pass, the
strict mark makes the suite fail, and the mark is removed.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/id_reconciliation/tests/test_suggested_steps.py -q
"""
import polars as pl
import pytest

from id_reconciliation import IDReconciliationEngine, MatchResult, apply_recode_step
from utils.id_patterns import apply_pattern, detect_patterns

# One list of IDs per pattern the matching knows: name -> (IDs to clean, IDs to reach, the pattern type).
PATTERNS = {
    "prefix": ([f"sample_{i:03d}" for i in range(1, 6)], [f"{i:03d}" for i in range(1, 6)], "prefix_removal"),
    "suffix": ([f"{i:03d}_R1" for i in range(1, 6)], [f"{i:03d}" for i in range(1, 6)], "suffix_removal"),
    "lower case": ([f"ABC{i}" for i in range(1, 6)], [f"abc{i}" for i in range(1, 6)], "case_normalization"),
    "underscore to hyphen": ([f"a_{i}" for i in range(1, 6)], [f"a-{i}" for i in range(1, 6)], "delimiter"),
}


def _cleaned(refs, targets):
    """The reference IDs after the suggested steps, and the steps."""
    engine = IDReconciliationEngine()
    transformation = engine.generate_transformation(engine.reconcile(refs, targets), "id", "id")
    return apply_recode_step(pl.DataFrame({"id": refs}), "id", transformation)["id"].to_list(), transformation.steps


def test_the_examples_cover_every_pattern_the_matching_knows():
    """A new pattern type in `detect_patterns` needs its example here, so that its step is tested."""
    found = {detect_patterns(refs, targets)[0].pattern_type for refs, targets, _ in PATTERNS.values()}
    assert found == {kind for _, _, kind in PATTERNS.values()}
    assert found == {"prefix_removal", "suffix_removal", "case_normalization", "delimiter"}


@pytest.mark.parametrize("name", sorted(PATTERNS))
def test_a_pattern_match_suggests_one_step_that_gives_the_matched_ids(name):
    refs, targets, _ = PATTERNS[name]
    engine = IDReconciliationEngine()
    assert {r.match_type for r in engine.reconcile(refs, targets)} == {"pattern"}
    cleaned, steps = _cleaned(refs, targets)
    assert len(steps) == 1, f"a pattern matched every ID, the steps are {steps}"
    assert cleaned == targets


def test_ids_that_match_as_they_are_suggest_no_step():
    ids = [f"{i:03d}" for i in range(1, 6)]
    assert _cleaned(ids, ids) == (ids, [])


def test_no_result_suggests_no_step():
    transformation = IDReconciliationEngine().generate_transformation([], "id", "id")
    assert transformation.steps == []
    assert transformation.metadata == {}


def test_the_same_pattern_on_many_ids_suggests_its_step_once():
    refs, targets, _ = PATTERNS["prefix"]
    _, steps = _cleaned(refs, targets)
    assert steps == [{"action": "regex_replace", "pattern": "^.{7}", "replacement": ""}]


def test_a_pattern_without_a_step_is_refused():
    """A match by a pattern nobody can turn into a step must not give a transformation that looks complete."""
    result = MatchResult(ref_id="A", target_id="a", match_type="pattern", certainty=0.95,
                         transform_applied="Reversing the ref IDs")
    with pytest.raises(ValueError, match="Reversing the ref IDs"):
        IDReconciliationEngine().generate_transformation([result], "id", "id")


@pytest.mark.parametrize("description", ["Removing first character(s) from ref IDs",
                                         "Removing last 0 character(s) from ref IDs"])
def test_a_removal_without_a_count_is_refused(description):
    result = MatchResult(ref_id="xA", target_id="A", match_type="pattern", certainty=0.95,
                         transform_applied=description)
    with pytest.raises(ValueError, match="character"):
        IDReconciliationEngine().generate_transformation([result], "id", "id")


# ---- defects that wait for a decision ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="ID-RECON-STEPS-1 finding: the delimiter step is always '_' to '-', "
                                       "also when the matching swapped '-' to '_'")
def test_hyphen_to_underscore_suggests_a_step_that_gives_the_matched_ids():
    refs = [f"a-{i}" for i in range(1, 6)]
    targets = [f"a_{i}" for i in range(1, 6)]
    cleaned, _ = _cleaned(refs, targets)
    assert cleaned == targets


@pytest.mark.xfail(strict=True, reason="ID-RECON-STEPS-1 finding: the matching keeps an ID that is not longer than "
                                       "the prefix, the step '^.{n}' empties it")
def test_the_prefix_step_treats_a_short_id_as_the_matching_did():
    refs = ["sample_001", "sample_002", "sample_003", "sample_"]
    targets = ["001", "002", "003"]
    cleaned, _ = _cleaned(refs, targets)
    assert cleaned == apply_pattern(refs, detect_patterns(refs, targets)[0])


@pytest.mark.xfail(strict=True, reason="ID-RECON-STEPS-1 finding: the matching applies a pattern only to the IDs that "
                                       "did not match as they are, the step changes the whole column")
def test_an_id_that_matched_as_it_is_still_matches_after_the_steps():
    refs = ["sample_001", "sample_002", "sample_003", "control_x1"]
    targets = ["001", "002", "003", "control_x1"]
    by_ref = {r.ref_id: r for r in IDReconciliationEngine().reconcile(refs, targets)}
    assert by_ref["control_x1"].match_type == "exact"
    cleaned, _ = _cleaned(refs, targets)
    assert cleaned[3] == "control_x1"
