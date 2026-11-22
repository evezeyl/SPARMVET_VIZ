"""Exploration filters are cleared when the viewed table changes (D-0311, D-0178), with a notice, and only when there was something to clear.

The pure rule (headless): `view_key` says what the view is; `view_change_notice` says what to tell the user when it changed. The reactive effect
that applies them (every view change clears) is covered by the browser tests of `test_filters_cleared_on_view_change.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_view_change_clears_filters.py -q
"""
import pytest

from app.modules.t3_audit_engine import filters_cleared_notice, rows_built_on, staged_filter_row, view_change_notice, view_key, viewed_table

BASE = view_key("recipe_a", "exploration", "T3", "meta", ("J", None))


def test_the_key_names_the_five_things_that_make_a_view():
    assert view_key("recipe_a", "exploration", "SRC", "meta", ("J", None)) == ("recipe_a", "exploration", "SRC", "meta", ("J", None))


def test_the_source_table_is_part_of_the_view_only_when_the_source_is_shown():
    """A stored choice of source table does not make T1, T2 or T3 another view."""
    assert view_key("r", "exploration", "T2", "meta", ("J", None)) == view_key("r", "exploration", "T2", "other", ("J", None))
    assert view_key("r", "exploration", "SRC", "meta", ("J", None)) != view_key("r", "exploration", "SRC", "other", ("J", None))


@pytest.mark.parametrize("changed,word", [
    (view_key("recipe_a", "audit", "T3", "meta", ("J", None)), "Audit mode"),
    (view_key("recipe_a", "exploration", "T1", "meta", ("J", None)), "data you view"),
    (view_key("recipe_a", "exploration", "T3", "meta", ("other_table", None)), "reads another table"),
])
def test_each_change_of_the_view_gives_one_plain_notice_naming_the_cause(changed, word):
    text = view_change_notice(BASE, changed, n_pending=1, n_applied=0)
    assert text and word in text
    assert "removed" in text and "Audited steps are kept" in text


def test_changing_the_source_table_says_so():
    src = view_key("recipe_a", "exploration", "SRC", "meta", ("J", None))
    text = view_change_notice(src, view_key("recipe_a", "exploration", "SRC", "other", "subtab_p1"), 0, 1)
    assert text and "source table" in text


def test_switching_back_to_exploration_says_so():
    audit = view_key("recipe_a", "audit", "T3", "meta", ("J", None))
    text = view_change_notice(audit, BASE, n_pending=0, n_applied=2)
    assert text and "Exploration mode" in text


@pytest.mark.parametrize("pending,applied", [(0, 0)])
def test_nothing_to_clear_gives_no_notice_for_any_change(pending, applied):
    for other in (view_key("recipe_a", "audit", "T3", "meta", ("J", None)), view_key("recipe_a", "exploration", "T2", "meta", ("J", None)),
                  view_key("recipe_b", "exploration", "T3", "meta", ("J", None))):
        assert view_change_notice(BASE, other, pending, applied) is None


def test_an_unchanged_view_gives_no_notice_even_with_filters():
    assert view_change_notice(BASE, BASE, n_pending=3, n_applied=3) is None


def test_the_first_view_is_not_a_change():
    assert view_change_notice(None, BASE, n_pending=3, n_applied=3) is None


def test_a_recipe_change_keeps_the_recipe_notice_and_wins_over_the_other_changes():
    other_recipe = view_key("recipe_b", "audit", "T1", "x", ("Z", None))
    assert view_change_notice(BASE, other_recipe, 1, 1) == filters_cleared_notice(1, 1)


def test_only_one_cause_is_named_when_two_things_change_at_once():
    both = view_key("recipe_a", "audit", "T1", "meta", ("J", None))
    text = view_change_notice(BASE, both, 1, 1)
    assert "Audit mode" in text and "data you view" not in text


# ---- D-0505, D-0506: the filter belongs to the table, not to the plot ----------------------------------------------------------------------

def test_the_table_of_a_view_is_named_by_the_data_choice_and_the_plot_s_target():
    assert viewed_table("SRC", "J", "p1", False) is None, "Source: the source table is its own part of the key"
    assert viewed_table("T1", "J", "p1", True) == ("J", None)
    assert viewed_table("T2", "J", "p1", True) == ("J", None), "tier-3 steps do not change T1 or T2"
    assert viewed_table("T3", "J", "p1", False) == ("J", None)
    assert viewed_table("T3", "J", "p1", True) == ("J", "p1"), "a plot with its own tier-3 steps reads its own table"


def _key(plot, has_steps=False, target="J", view="T3", source="meta"):
    return view_key("r", "exploration", view, source, viewed_table(view, target, plot, has_steps))


def test_two_plots_on_one_table_share_the_key_and_clear_nothing():
    a, b = _key("p1"), _key("p2")
    assert a == b
    assert view_change_notice(a, b, n_pending=2, n_applied=2) is None
    for view in ("T1", "T2"):
        assert _key("p1", True, view=view) == _key("p2", True, view=view), "T1 and T2 never depend on tier-3 steps"
    assert _key("p1", view="SRC") == _key("p2", target="T", view="SRC"), "on Source the plot does not matter"


def test_two_plots_on_two_tables_clear_with_the_cause_named():
    a, b = _key("p1"), _key("p3", target="T")
    assert a != b
    text = view_change_notice(a, b, n_pending=1, n_applied=0)
    assert text and "you opened a plot that reads another table" in text and "Audited steps are kept" in text


def test_a_plot_with_its_own_tier_3_steps_is_another_table_than_its_neighbour():
    plain, own, own2 = _key("p1"), _key("p4", True), _key("p5", True)
    assert plain != own and own != own2
    assert "reads another table" in view_change_notice(plain, own, 1, 0)


def test_the_data_choice_stays_in_the_key_even_when_the_tables_are_equal():
    """T2 equals T1 for a target with no tier-2 steps, but a change of the viewed tier clears (D-0311)."""
    assert _key("p1", view="T1") != _key("p1", view="T2")
    assert "data you view" in view_change_notice(_key("p1", view="T1"), _key("p1", view="T2"), 1, 0)


def test_a_filter_built_on_one_plot_is_applied_on_a_plot_of_the_same_table_and_not_on_another_table():
    row = staged_filter_row("score", "ge", 4, "Int64", False, view=_key("p1"))
    assert rows_built_on([row], _key("p2")) == [row]
    assert rows_built_on([row], _key("p3", target="T")) == []
    assert rows_built_on([row], _key("p4", True)) == []
