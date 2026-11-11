"""The rules of the view badge (issue #17): what a panel shows, and when two views are the same.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_view_badge.py -q
"""
import pytest

from app.modules.view_badge import has_tier2_steps, view_badge

RAW = {
    "joins": {
        "WithT2": {"steps": {"tier1": [{"action": "sort", "columns": ["a"]}],
                              "tier2": [{"action": "filter_eq", "column": "a", "value": 1}]}},
        "WithoutT2": {"steps": {"tier1": [{"action": "sort", "columns": ["a"]}], "tier2": []}},
        "TierOnly": {"steps": {"tier1": []}},
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
