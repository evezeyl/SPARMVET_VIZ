"""The rules of the view badge (issue #17, slice B): what a panel shows, and when two views are the same.

The data choice has four values: Source, T1, T2, T3 (D-0310). The data badge names them so; the plot badge says what the plot is (the Result in
Exploration; the audited plot in Audit mode). Exploration filters change the table only, never a plot.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_view_badge.py -q
"""
import pytest

from app.modules.view_badge import (
    AUDITED_TABLE_NOTE, SOURCE_NOTE, ViewBadge, has_plot_steps, has_tier2_steps, plot_badge, view_badge)

RAW = {
    "joins": {
        "WithT2": {"tier1": {"steps": [{"action": "sort", "columns": ["a"]}]},
                   "tier2": {"steps": [{"action": "filter_eq", "column": "a", "value": 1}]}},
        "WithoutT2": {"tier1": {"steps": [{"action": "sort", "columns": ["a"]}]}, "tier2": {"steps": []}},
        "TierOnly": {"tier1": {"steps": []}},
    }
}


def test_t1_view_has_no_notes():
    badge = view_badge("T1", has_tier2=False, plot_has_steps=False)
    assert badge.label == "Viewing: T1" and badge.notes == ()


@pytest.mark.parametrize("has_tier2,notes", [(True, ()), (False, ("T2=T1",))])
def test_t2_view_says_when_it_equals_t1(has_tier2, notes):
    badge = view_badge("T2", has_tier2, plot_has_steps=False)
    assert badge.label == "Viewing: T2" and badge.notes == notes


@pytest.mark.parametrize("has_tier2,notes", [
    (True, ("T3=T2",)),          # the plot has no steps of its own: its table is the T2 table
    (False, ("T3=T2=T1",)),      # ... and T2 is itself T1
])
def test_t3_view_says_what_it_is_identical_to(has_tier2, notes):
    badge = view_badge("T3", has_tier2, plot_has_steps=False)
    assert badge.label == "Viewing: T3" and badge.notes == notes


@pytest.mark.parametrize("has_tier2,notes", [
    (True, ("T3 = T2 plus this plot's own steps of the recipe",)),         # never "T3=T2": the plot has steps of its own
    (False, ("T3 = T2 = T1 plus this plot's own steps of the recipe",)),
])
def test_t3_of_a_plot_with_tier3_steps_does_not_claim_equality_with_t2(has_tier2, notes):
    badge = view_badge("T3", has_tier2, plot_has_steps=True)
    assert badge.notes == notes and not any(n in ("T3=T2", "T3=T2=T1") for n in badge.notes)


def test_source_view_names_the_table_and_says_it_is_before_any_recipe_step():
    badge = view_badge("SRC", has_tier2=True, plot_has_steps=True, source_table="metadata")
    assert badge.label == "Viewing: Source"
    assert badge.notes[0] == "table 'metadata'" and SOURCE_NOTE in badge.notes
    # no tier relation is claimed for a source table
    assert not any("T2" in n or "T3" in n for n in badge.notes)


def test_no_old_view_name_is_used():
    for view in ("SRC", "T1", "T2", "T3"):
        for mode in ("exploration", "audit"):
            text = " ".join([view_badge(view, True, False, mode=mode, audited_steps=1).label,
                             *view_badge(view, True, False, mode=mode, audited_steps=1).notes])
            assert "Raw" not in text and "Result" not in text and "My view" not in text


def test_audit_t3_with_audited_steps_says_it_is_the_audited_table_and_is_amber():
    badge = view_badge("T3", has_tier2=True, plot_has_steps=False, mode="audit", audited_steps=2)
    assert badge.label == "Viewing: T3 (audited)" and badge.tone == "audited"
    assert AUDITED_TABLE_NOTE.format(n=2) in badge.notes
    assert "T3=T2" not in badge.notes   # the audited table is not equal to T2


def test_audit_t3_without_audited_steps_is_the_plain_t3():
    badge = view_badge("T3", has_tier2=True, plot_has_steps=False, mode="audit", audited_steps=0)
    assert badge.label == "Viewing: T3" and badge.tone == "plain" and badge.notes == ("T3=T2",)


@pytest.mark.parametrize("view", ["SRC", "T1", "T2"])
def test_audit_mode_shows_the_original_tables_for_the_other_views(view):
    """Audit steps apply to T3 only (slice B); T1, T2 and Source stay the original tables even with audited steps."""
    exploration = view_badge(view, True, False, mode="exploration", source_table="t")
    audit = view_badge(view, True, False, mode="audit", audited_steps=3, source_table="t")
    assert audit == exploration


@pytest.mark.parametrize("view", ["SRC", "T1", "T2", "T3"])
def test_preview_filters_are_announced_as_changing_the_table_only(view):
    """ADR-098 (issue #56), D-0311: a filtered table must never pass for the reference data, and never changes a plot."""
    badge = view_badge(view, has_tier2=True, plot_has_steps=False, preview_filters=2)
    assert any("2 preview filter(s) on, not saved" in n and "never a plot" in n for n in badge.notes)


def test_no_preview_note_without_filters():
    assert not any("preview" in n for n in view_badge("T2", True, False).notes)


def test_no_preview_note_in_audit_mode():
    """Exploration filters do not exist in Audit mode; a count handed in is not announced."""
    assert not any("preview" in n for n in view_badge("T3", True, False, preview_filters=2, mode="audit").notes)


# -- the plot badge --------------------------------------------------------------------

def test_exploration_plot_is_the_result():
    badge = plot_badge("exploration", plot_has_steps=False, has_tier2=True)
    assert badge.label == "Plot: Result" and badge.tone == "plain" and badge.notes == ()


def test_exploration_plot_says_preview_filters_do_not_change_it():
    badge = plot_badge("exploration", plot_has_steps=False, has_tier2=True, preview_filters=2)
    assert badge.notes == ("2 preview filter(s) change the table only; this plot is not changed",)


def test_exploration_plot_with_own_steps_says_so():
    badge = plot_badge("exploration", plot_has_steps=True, has_tier2=True)
    assert badge.notes == ("drawn from T3 = T2 plus this plot's own steps of the recipe",)
    badge = plot_badge("exploration", plot_has_steps=True, has_tier2=False)
    assert badge.notes == ("drawn from T3 = T2 = T1 plus this plot's own steps of the recipe",)


def test_audit_plot_without_steps_says_it_equals_the_result():
    badge = plot_badge("audit", plot_has_steps=False, has_tier2=True, audited_steps=0)
    assert badge.label == "Plot: Audited" and badge.tone == "plain"
    assert badge.notes == ("no audited step for this plot yet: identical to the Result",)


def test_audit_plot_with_steps_is_amber_and_counts_the_steps():
    badge = plot_badge("audit", plot_has_steps=False, has_tier2=True, audited_steps=2)
    assert badge.label == "Plot: Audited" and badge.tone == "audited" and badge.notes == ("2 audited step(s) on this plot",)


def test_audit_mode_plot_never_announces_exploration_filters():
    assert not any("preview" in n for n in plot_badge("audit", False, True, preview_filters=3).notes)


def test_badges_are_frozen_records():
    assert isinstance(view_badge("T1", True, False), ViewBadge)
    with pytest.raises(Exception):
        view_badge("T1", True, False).label = "x"


# -- the recipe readers ---------------------------------------------------------------

def test_has_tier2_steps_reads_the_joins_steps():
    assert has_tier2_steps(RAW, "WithT2") is True
    assert has_tier2_steps(RAW, "WithoutT2") is False
    assert has_tier2_steps(RAW, "TierOnly") is False


def test_a_plot_on_a_bare_schema_or_unknown_dataset_has_no_tier2_steps():
    assert has_tier2_steps(RAW, "SomeDataSchema") is False   # not a join
    assert has_tier2_steps(RAW, None) is False
    assert has_tier2_steps({}, "WithT2") is False


def test_has_plot_steps_reads_the_plots_tier3_of_the_recipe():
    raw = {"analysis_groups": {"g": {"plots": {
        "with": {"target_dataset": "C", "tier3": {"steps": [{"action": "polars_drop", "columns": ["a"]}]}},
        "empty": {"target_dataset": "C", "tier3": {"steps": []}},
        "none": {"target_dataset": "C"}}}}}
    assert has_plot_steps(raw, "with") is True
    assert has_plot_steps(raw, "empty") is False and has_plot_steps(raw, "none") is False
    assert has_plot_steps(raw, "nope") is False and has_plot_steps(raw, None) is False


# D-0488: the two facts of every data preview, how many rows and how many columns are hidden (PROVISIONAL words)
from app.modules.view_badge import PREVIEW_ROW_LIMIT, hidden_columns_note, row_count_note


def test_the_row_limit_is_one_number_of_100():
    assert PREVIEW_ROW_LIMIT == 100


@pytest.mark.parametrize("total,all_rows,text", [
    (0, False, "0 rows"),
    (1, False, "1 row"),
    (100, False, "100 rows"),                       # exactly the limit: nothing is cut
    (101, False, "Showing 100 of 101 rows"),
    (2340, False, "Showing 100 of 2340 rows"),
    (2340, True, "2340 rows"),                      # All rows on: the table is shown whole
    (5, True, "5 rows"),
])
def test_row_count_note(total, all_rows, text):
    assert row_count_note(total, all_rows) == text


def test_row_count_note_is_absent_when_the_count_is_unknown():
    assert row_count_note(None, False) is None      # the table could not be built: its error is shown in the table's place


@pytest.mark.parametrize("hidden,audit,text", [
    (0, False, None), (0, True, None),
    (1, False, "1 column hidden; add it back in the column chooser"),
    (3, False, "3 columns hidden; add them back in the column chooser"),
])
def test_hidden_columns_note_exploration(hidden, audit, text):
    assert hidden_columns_note(hidden, audit) == text


def test_hidden_columns_note_in_audit_t3_says_they_are_not_dropped():
    note = hidden_columns_note(3, True)
    assert "3 columns" in note and "not dropped" in note and "chooser" in note


def test_view_badge_carries_the_two_facts_after_the_other_notes():
    badge = view_badge("T2", False, False, 2, total_rows=2340, all_rows=False, hidden_columns=3)
    assert badge.notes[0] == "T2=T1"
    assert badge.notes[-2:] == ("Showing 100 of 2340 rows", "3 columns hidden; add them back in the column chooser")


def test_view_badge_without_the_facts_is_unchanged():
    assert view_badge("T1", True, False).notes == ()
    assert view_badge("T1", True, False, total_rows=0).notes == ("0 rows",)
