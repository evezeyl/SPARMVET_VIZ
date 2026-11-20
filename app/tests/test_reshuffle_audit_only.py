"""Reshuffle belongs to Audit mode (D-0341, D-0019, D-0327): in Exploration the button is not shown and no pin is applied.

"The Reshuffle button of a plot with a random layer is offered only in Audit mode; in Exploration it is not shown, and the plot of Exploration is the
recipe's plot." The pin is an audit step (`home_state["t3_plot_overrides"]`, passed to the render as `aesthetic_override`). Headless on the real HOME:

- with a pin stored, the Exploration plot is drawn with NO override and equals the "Original" pane of Compare; the audited plot of Audit mode is
  drawn with the pin;
- the button is absent in Exploration and offered in Audit mode (a plot with a random layer, no seed written); a stored pin is neither applied nor
  announced in Exploration (the seed line shows the seed the plot is drawn with);
- the click handler pins nothing in Exploration.

MUTATION R1 (the render passes the pin in every mode): the render tests fail. MUTATION R2 (the button is offered in every mode): the button test
fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_reshuffle_audit_only.py -q
"""
import pytest
from shiny import reactive

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.home_harness import Home, ViewWorld

AUDIT = ("interactivity_enabled", "t3_sandbox_enabled", "comparison_mode_enabled", "session_management_enabled", "export_enabled")
PIN = {"subtab_p_jitter": {"random_state": 7}, "subtab_p_join": {"random_state": 7}}


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def home(tmp_path, monkeypatch, mode, pinned, plot="p_jitter"):
    state = {"t3_plot_overrides": dict(PIN)} if pinned else {}
    return Home(ViewWorld(tmp_path), monkeypatch, flags=AUDIT, mode=mode, subtab=f"subtab_{plot}", home_state=state)


def test_with_a_pin_stored_the_exploration_plot_is_drawn_without_it_and_the_audited_plot_with_it(tmp_path, monkeypatch):
    exploration = home(tmp_path / "e", monkeypatch, "exploration", pinned=True)
    exploration.plot("p_join")
    assert exploration.drawn_kw["p_join"].get("aesthetic_override") is None, "Exploration draws the recipe's plot"
    audit = home(tmp_path / "a", monkeypatch, "audit", pinned=True)
    audit.plot("p_join")
    assert audit.drawn_kw["p_join"].get("aesthetic_override") == {"random_state": 7}, "the audited plot carries the pin"


def test_the_exploration_plot_equals_the_original_pane_of_compare_when_a_pin_exists(tmp_path, monkeypatch):
    h = home(tmp_path, monkeypatch, "exploration", pinned=True)
    h.plot("p_join")
    exploration_rows, exploration_kw = h.drawn["p_join"], dict(h.drawn_kw["p_join"])
    with reactive.isolate():
        h.outputs["plot_group_p_join_cmp_base"]()
    assert h.drawn["p_join"].equals(exploration_rows)
    original_kw = dict(h.drawn_kw["p_join"])
    assert {k: v for k, v in exploration_kw.items() if k != "aesthetic_override"} == {k: v for k, v in original_kw.items() if k != "aesthetic_override"}
    assert exploration_kw.get("aesthetic_override") == original_kw.get("aesthetic_override") is None


def test_the_button_is_not_shown_in_exploration_and_is_offered_in_audit_mode(tmp_path, monkeypatch):
    for mode, offered in (("exploration", False), ("audit", True)):
        h = home(tmp_path / mode, monkeypatch, mode, pinned=False)
        with reactive.isolate():
            html = str(h.outputs["plot_reshuffle_p_jitter"]())
        assert ("plot_reshuffle_btn_p_jitter" in html) is offered, mode


def test_a_stored_pin_is_neither_applied_nor_announced_in_exploration(tmp_path, monkeypatch):
    exploration = home(tmp_path / "e", monkeypatch, "exploration", pinned=True)
    with reactive.isolate():
        line = str(exploration.outputs["plot_seed_p_jitter"]())
        assert "seed 0, default" in line and "pinned" not in line and "Remove the pinned seed" not in line
    audit = home(tmp_path / "a", monkeypatch, "audit", pinned=True)
    with reactive.isolate():
        line = str(audit.outputs["plot_seed_p_jitter"]())
        assert "seed 7" in line and "Remove the pinned seed" in line
        assert "plot_reshuffle_btn_p_jitter" not in str(audit.outputs["plot_reshuffle_p_jitter"]()), "already pinned: not offered again"


def test_the_click_pins_nothing_in_exploration_and_pins_in_audit_mode(tmp_path, monkeypatch):
    # the first plot of the recipe is p_table: its Reshuffle handler is the one captured by name
    for mode, pinned in (("exploration", False), ("audit", True)):
        h = home(tmp_path / mode, monkeypatch, mode, pinned=False, plot="p_table")
        with reactive.isolate():
            h.effects["_handle_reshuffle"]()
            overrides = h.home_state.get().get("t3_plot_overrides", {})
        assert (("subtab_p_table" in overrides) and "random_state" in overrides["subtab_p_table"]) is pinned, mode
