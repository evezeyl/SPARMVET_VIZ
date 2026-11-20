"""GATE-GAP-1: what HOME's recipe selector does when the load gate changes (pure parts; the browser tests run the whole)."""
from types import SimpleNamespace

from app.handlers.recipe_gate_handlers import follow_gate, follow_step, gate_notes, notice_after_pick, usable_config


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


def test_the_first_screen_still_says_which_recipe_was_replaced_when_the_selector_value_has_not_reached_the_server():
    """The opening refused the recipe on the first screen: current is None, the recipe HOME opened is the remembered one (it was not before the fix: the notice was
    None and the recipe was switched silently)."""
    assert follow_step(["other"], None, "A", None) == (["other"], "other", ("A", "other"), True)
    assert follow_step(["other"], None, None, None) == (["other"], "other", None, False), "no recipe was ever shown: nothing to say"


def test_the_follower_remembers_into_the_value_the_opening_also_writes(monkeypatch):
    """`recipe_gate_handlers.define_server` keeps the recipe HOME shows in the `shown_recipe` it is given (shared with the opening), not in a private value."""
    from shiny import reactive
    from app.handlers import recipe_gate_handlers as handlers
    effects = {}
    monkeypatch.setattr(handlers.reactive, "Effect", lambda fn: effects.setdefault(fn.__name__, fn) and fn)
    monkeypatch.setattr(handlers.reactive, "poll", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(handlers, "render", SimpleNamespace(ui=lambda fn: fn))
    boot = SimpleNamespace(available_data_analysis_recipes={"A": 1}, data_analysis_recipe_gate_version=0)
    shown = reactive.Value(None)
    handlers.define_server(None, lambda fn: fn, None, bootloader=boot, safe_input=lambda i, k, d: "A", recipe_gate_version=reactive.Value(0), shown_recipe=shown)
    with reactive.isolate():
        effects["_remember_choice"]()
        assert shown.get() == "A"


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


# -- the notice "recipe X was open and no longer passes its checks" (CONTROLS-FIX-1, B; ADR-104: never switch silently) --------

def _ticks(steps, notice=None):
    """Run follow_step over a list of (available, selector value now, remembered) polls; returns the notice after each and
    how many times it was announced (written to the Alerts log)."""
    seen, announced = [], 0
    for available, current, remembered in steps:
        _, _, notice, announce = follow_step(available, current, remembered, notice)
        announced += bool(announce)
        seen.append(notice)
    return seen, announced


def test_the_notice_stays_over_later_polls_while_the_recipe_that_was_left_is_still_failing():
    """The bug: the next poll saw the selector on a valid recipe and cleared the notice, so the reason showed for about 2 s."""
    ticks = [(["b"], "x", "x"),          # the gate drops x: the selector moves to b
             (["b"], "b", "x"),          # a later version bump (another recipe changed), selector on b
             (["b", "c"], "b", "b"),
             (["b", "c"], "b", "b")]
    seen, announced = _ticks(ticks)
    assert seen == [("x", "b")] * 4
    assert announced == 1                # written to the Alerts log once, not at every poll


def test_the_notice_goes_when_the_recipe_that_was_left_passes_its_checks_again():
    seen, _ = _ticks([(["b"], "x", "x"), (["b"], "b", "x"), (["b", "x"], "b", "b")])
    assert seen == [("x", "b"), ("x", "b"), None]


def test_a_second_replacement_replaces_the_notice_and_is_announced_again():
    seen, announced = _ticks([(["b", "c"], "x", "x"), (["c"], "b", "b")])
    assert seen == [("x", "b"), ("b", "c")]
    assert announced == 2


def test_no_notice_without_a_replacement():
    assert _ticks([(["a", "b"], "a", "a"), (["a", "b"], "a", "a")]) == ([None, None], 0)


def test_choosing_a_recipe_by_hand_clears_the_notice():
    # the selector held 'b' (the replacement) and the user picks 'c'
    assert notice_after_pick(("x", "b"), "b", "c", ["b", "c"]) == (None, False)


def test_the_update_the_app_makes_itself_is_not_a_pick():
    for previous in ("x", None, "b"):
        assert notice_after_pick(("x", "b"), previous, "b", ["b"]) == (("x", "b"), False)


def test_the_selector_off_the_page_keeps_the_notice():
    assert notice_after_pick(("x", "b"), "b", None, ["b"]) == (("x", "b"), False)


def test_a_selector_rebuilt_on_another_recipe_makes_the_notice_name_the_recipe_that_is_open():
    """Back from Blueprint the selector is built again (previous None): the notice must still say what is open."""
    assert notice_after_pick(("x", "b"), None, "c", ["b", "c"]) == (("x", "c"), False)


def test_a_replacement_the_poll_has_not_announced_yet_is_announced_when_the_selector_shows_it():
    """The race of the browser test: the sidebar was built again from the new list (x gone) before the poll ticked, so the
    selector moved from x to b by itself and no notice existed."""
    assert notice_after_pick(None, "x", "b", ["b", "c"]) == (("x", "b"), True)
    # the poll then finds the selector already on b: nothing is lost, the notice stays
    seen, announced = _ticks([(["b", "c"], "b", "b")], notice=("x", "b"))
    assert seen == [("x", "b")] and announced == 0


def test_a_replacement_already_announced_is_not_announced_twice():
    assert notice_after_pick(("x", "b"), "x", "b", ["b"]) == (("x", "b"), False)


def test_no_notice_stays_no_notice_after_a_pick_between_available_recipes():
    assert notice_after_pick(None, "a", "b", ["a", "b"]) == (None, False)
    assert notice_after_pick(None, None, "b", ["a", "b"]) == (None, False)
