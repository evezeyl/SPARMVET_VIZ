"""The rules of the view badge (issue #17): what a panel shows, and when two views are the same.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_view_badge.py -q
"""
import pytest

from app.modules.view_badge import has_tier2_steps, view_badge

RAW = {
    "joins": {
        "WithT2": {"tier1": {"steps": [{"action": "sort", "columns": ["a"]}]},
                   "tier2": {"steps": [{"action": "filter_eq", "column": "a", "value": 1}]}},
        "WithoutT2": {"tier1": {"steps": [{"action": "sort", "columns": ["a"]}]}, "tier2": {"steps": []}},
        "TierOnly": {"tier1": {"steps": []}},
    }
}


def test_raw_view_has_no_notes():
    badge = view_badge("T1", has_tier2=False, has_changes=False)
    assert badge.label == "Viewing: Raw" and badge.notes == ()


@pytest.mark.parametrize("has_tier2,notes", [(True, ()), (False, ("T2=T1",))])
def test_result_view_says_when_it_equals_raw(has_tier2, notes):
    badge = view_badge("T2", has_tier2, has_changes=False)
    assert badge.label == "Viewing: Result" and badge.notes == notes


@pytest.mark.parametrize("has_tier2,has_changes,notes", [
    (True, False, ("T3=T2",)),          # no filter or drop: My view is the Result
    (False, False, ("T3=T2=T1",)),      # ... and the Result is the Raw data
    (True, True, ()),                   # real changes and real tier-2 steps: nothing to say
    (False, True, ("T2=T1",)),          # real changes, but Result equals Raw
])
def test_my_view_says_what_it_is_identical_to(has_tier2, has_changes, notes):
    badge = view_badge("T3", has_tier2, has_changes)
    assert badge.label == "Viewing: My view" and badge.notes == notes


def test_has_tier2_steps_reads_the_joins_steps():
    assert has_tier2_steps(RAW, "WithT2") is True
    assert has_tier2_steps(RAW, "WithoutT2") is False
    assert has_tier2_steps(RAW, "TierOnly") is False


def test_a_plot_on_a_bare_schema_or_unknown_dataset_has_no_tier2_steps():
    assert has_tier2_steps(RAW, "SomeDataSchema") is False   # not a join
    assert has_tier2_steps(RAW, None) is False
    assert has_tier2_steps({}, "WithT2") is False


@pytest.mark.parametrize("tier", ["T1", "T2"])
def test_preview_filters_are_announced_on_raw_and_result(tier):
    """ADR-098 (issue #56): a filtered preview must never pass for the reference data."""
    badge = view_badge(tier, has_tier2=True, has_changes=False, preview_filters=2)
    assert "2 preview filter(s) on, not saved" in badge.notes


def test_no_preview_note_without_filters_or_on_my_view():
    assert not any("preview" in n for n in view_badge("T2", True, False).notes)
    assert not any("preview" in n for n in view_badge("T3", True, True, preview_filters=2).notes)


def test_plot_badge_on_result_says_preview_filters_do_not_change_the_plot():
    badge = view_badge("T2", True, False, table_only_filters=2)
    assert any("table only" in n for n in badge.notes)
    assert not any("table only" in n for n in view_badge("T3", True, True, table_only_filters=2).notes)


@pytest.mark.parametrize("has_tier2,has_changes,notes", [
    (True, False, ("T3 = T2 plus this plot's own steps of the recipe",)),         # never "T3=T2": the plot has steps of its own
    (False, False, ("T3 = T2 = T1 plus this plot's own steps of the recipe",)),
    (True, True, ()),
    (False, True, ("T2=T1",)),
])
def test_my_view_of_a_plot_with_tier3_steps_does_not_claim_equality_with_the_result(has_tier2, has_changes, notes):
    """Slice A (piece A4): the plot's table is its table plus the plot's own tier-3 steps (PROVISIONAL words)."""
    badge = view_badge("T3", has_tier2, has_changes, plot_has_steps=True)
    assert badge.notes == notes and not any(n in ("T3=T2", "T3=T2=T1") for n in badge.notes)


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
@pytest.mark.parametrize("has_tier2", [True, False])
@pytest.mark.parametrize("has_changes", [True, False])
def test_a_plot_without_tier3_steps_has_the_same_badge_as_before(tier, has_tier2, has_changes):
    assert view_badge(tier, has_tier2, has_changes, 1, 1, plot_has_steps=False) == view_badge(tier, has_tier2, has_changes, 1, 1)


def test_has_plot_steps_reads_the_plots_tier3_of_the_recipe():
    from app.modules.view_badge import has_plot_steps
    raw = {"analysis_groups": {"g": {"plots": {
        "with": {"target_dataset": "C", "tier3": {"steps": [{"action": "polars_drop", "columns": ["a"]}]}},
        "empty": {"target_dataset": "C", "tier3": {"steps": []}},
        "none": {"target_dataset": "C"}}}}}
    assert has_plot_steps(raw, "with") is True
    assert has_plot_steps(raw, "empty") is False and has_plot_steps(raw, "none") is False
    assert has_plot_steps(raw, "nope") is False and has_plot_steps(raw, None) is False
