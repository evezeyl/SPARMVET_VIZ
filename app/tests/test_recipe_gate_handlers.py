"""GATE-GAP-1: what HOME's recipe selector does when the load gate changes (pure parts; the browser tests run the whole)."""
from types import SimpleNamespace

from app.handlers.recipe_gate_handlers import follow_gate, gate_notes, usable_config


def test_the_selector_keeps_the_recipe_that_is_still_available():
    assert follow_gate(["a", "b"], "b", "b") == (["a", "b"], "b", None)


def test_the_selector_moves_to_the_first_available_and_says_so_when_the_open_recipe_dropped():
    assert follow_gate(["a", "b"], "z", "z") == (["a", "b"], "a", ("z", "a"))


def test_the_selector_off_the_page_still_says_which_recipe_was_replaced():
    """Blueprint is open, the selector is not on the page (current None): the remembered choice is the recipe that was open."""
    assert follow_gate(["a"], None, "z") == (["a"], "a", ("z", "a"))


def test_nothing_is_said_when_no_recipe_was_open_or_none_is_left():
    assert follow_gate(["a"], None, None) == (["a"], "a", None)
    assert follow_gate([], "z", "z") == ([], None, None)


def test_a_repaired_recipe_returns_to_the_choices_without_moving_the_selection():
    assert follow_gate(["a", "z"], "a", "a") == (["a", "z"], "a", None)


def test_the_notes_list_the_unavailable_recipes_the_reason_the_contact_and_the_replacement():
    html = str(gate_notes({"r": {"problems": ["[ST02] unknown action", "p2", "p3"], "contact": None}}, {}, ("r", "a")))
    assert "'r' was open and no longer passes its checks" in html and "shows 'a' instead" in html
    assert "1 recipe(s) unavailable" in html and "[ST02] unknown action" in html and " ..." in html
    assert "not configured for this deployment" in html


def test_the_notes_are_empty_when_everything_passes():
    assert "unavailable" not in str(gate_notes({}, {}, None))


def test_a_recipe_that_is_not_available_gives_an_empty_stand_in_and_is_never_read():
    boot = SimpleNamespace(available_data_analysis_recipes={"ok": "p"}, get_location=lambda k: __import__("pathlib").Path("/x"))
    called = []
    for recipe in ("gone", None):
        assert usable_config(boot, recipe, lambda p: called.append(p)).raw_config == {}
    assert called == []


def test_a_recipe_broken_since_the_last_check_gives_an_empty_stand_in():
    boot = SimpleNamespace(available_data_analysis_recipes={"ok": "p"}, get_location=lambda k: __import__("pathlib").Path("/x"))

    def load(path):
        raise ValueError("cannot be loaded")

    assert usable_config(boot, "ok", load).raw_config == {}


def test_an_available_recipe_is_read():
    boot = SimpleNamespace(available_data_analysis_recipes={"ok": "p"}, get_location=lambda k: __import__("pathlib").Path("/x"))
    assert usable_config(boot, "ok", lambda p: SimpleNamespace(config=SimpleNamespace(raw_config={"k": 1}))).raw_config == {"k": 1}
