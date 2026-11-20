"""Exploration filters are cleared when the viewed table changes (D-0311, D-0178), with a notice, and only when there was something to clear.

The pure rule (headless): `view_key` says what the view is; `view_change_notice` says what to tell the user when it changed. The reactive effect
that applies them (every view change clears) is covered by the browser tests of `test_filters_cleared_on_view_change.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_view_change_clears_filters.py -q
"""
import pytest

from app.modules.t3_audit_engine import filters_cleared_notice, view_change_notice, view_key

BASE = view_key("recipe_a", "exploration", "T3", "meta", "subtab_p1")


def test_the_key_names_the_five_things_that_make_a_view():
    assert view_key("recipe_a", "exploration", "SRC", "meta", "subtab_p1") == ("recipe_a", "exploration", "SRC", "meta", "subtab_p1")


def test_the_source_table_is_part_of_the_view_only_when_the_source_is_shown():
    """A stored choice of source table does not make T1, T2 or T3 another view."""
    assert view_key("r", "exploration", "T2", "meta", "s") == view_key("r", "exploration", "T2", "other", "s")
    assert view_key("r", "exploration", "SRC", "meta", "s") != view_key("r", "exploration", "SRC", "other", "s")


@pytest.mark.parametrize("changed,word", [
    (view_key("recipe_a", "audit", "T3", "meta", "subtab_p1"), "Audit mode"),
    (view_key("recipe_a", "exploration", "T1", "meta", "subtab_p1"), "data you view"),
    (view_key("recipe_a", "exploration", "T3", "meta", "subtab_p2"), "another plot"),
])
def test_each_change_of_the_view_gives_one_plain_notice_naming_the_cause(changed, word):
    text = view_change_notice(BASE, changed, n_pending=1, n_applied=0)
    assert text and word in text
    assert "removed" in text and "Audited steps are kept" in text


def test_changing_the_source_table_says_so():
    src = view_key("recipe_a", "exploration", "SRC", "meta", "subtab_p1")
    text = view_change_notice(src, view_key("recipe_a", "exploration", "SRC", "other", "subtab_p1"), 0, 1)
    assert text and "source table" in text


def test_switching_back_to_exploration_says_so():
    audit = view_key("recipe_a", "audit", "T3", "meta", "subtab_p1")
    text = view_change_notice(audit, BASE, n_pending=0, n_applied=2)
    assert text and "Exploration mode" in text


@pytest.mark.parametrize("pending,applied", [(0, 0)])
def test_nothing_to_clear_gives_no_notice_for_any_change(pending, applied):
    for other in (view_key("recipe_a", "audit", "T3", "meta", "subtab_p1"), view_key("recipe_a", "exploration", "T2", "meta", "subtab_p1"),
                  view_key("recipe_b", "exploration", "T3", "meta", "subtab_p1")):
        assert view_change_notice(BASE, other, pending, applied) is None


def test_an_unchanged_view_gives_no_notice_even_with_filters():
    assert view_change_notice(BASE, BASE, n_pending=3, n_applied=3) is None


def test_the_first_view_is_not_a_change():
    assert view_change_notice(None, BASE, n_pending=3, n_applied=3) is None


def test_a_recipe_change_keeps_the_recipe_notice_and_wins_over_the_other_changes():
    other_recipe = view_key("recipe_b", "audit", "T1", "x", "subtab_zz")
    assert view_change_notice(BASE, other_recipe, 1, 1) == filters_cleared_notice(1, 1)


def test_only_one_cause_is_named_when_two_things_change_at_once():
    both = view_key("recipe_a", "audit", "T1", "meta", "subtab_p1")
    text = view_change_notice(BASE, both, 1, 1)
    assert "Audit mode" in text and "data you view" not in text
