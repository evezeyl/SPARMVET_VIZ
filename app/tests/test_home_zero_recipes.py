"""With zero usable recipes nothing on HOME's start path asks for the default recipe unguarded (ADR-094 point 6; review of slice B).

The regression: `_dialog_table_identity` (the filter form's table identity) read the recipe id with `get_default_data_analysis_recipe()` before it
knew whether there was a plot. With zero recipes that call raises `FileNotFoundError`, the form's effect logged "the stored table the form reads could
not be identified", and the server log held a Traceback. On dev the function returned None first (no plot, no table, no identity). Slice B's new
calls (the Source list, the Source reader, the screen record, the badges) are covered here too.

MUTATION Z1 (the recipe id is read first again): `test_no_plot_no_identity_and_no_default_recipe_is_asked_for` fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_zero_recipes.py -q
"""
from types import SimpleNamespace

import pytest
from shiny import reactive

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.home_harness import Home, ViewWorld

AUDIT = ("interactivity_enabled", "t3_sandbox_enabled", "comparison_mode_enabled", "session_management_enabled", "export_enabled")


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def zero_recipes(tmp_path, monkeypatch, view="T3", mode="exploration"):
    """HOME as the server starts it when no recipe is usable: no open recipe, no plot, and the raising default."""
    home = Home(ViewWorld(tmp_path), monkeypatch, view=view, mode=mode, flags=AUDIT, subtab="")
    home.bootloader.get_default_data_analysis_recipe.side_effect = FileNotFoundError("No data analysis recipes found")
    home.bootloader.get_default_data_analysis_recipe_or_none.return_value = None
    home.inputs["data_analysis_recipe_id"] = None
    home.cfg = SimpleNamespace(raw_config={})   # `active_cfg()` is an empty stand-in when no recipe is usable (server.py, issue #38)
    return home


@pytest.mark.parametrize("tier", ["SRC", "T1", "T2", "T3"])
def test_no_plot_no_identity_and_no_default_recipe_is_asked_for(tmp_path, monkeypatch, tier):
    home = zero_recipes(tmp_path, monkeypatch)
    with reactive.isolate():
        assert home.readers["_table_identity"](None, tier) is None
        assert home.readers["_table_identity"]({}, tier) is None


def test_the_filter_forms_effects_run_with_zero_recipes_and_log_nothing(tmp_path, monkeypatch, caplog):
    home = zero_recipes(tmp_path, monkeypatch)
    effects = home.filter_handlers(monkeypatch)
    with caplog.at_level("ERROR"), reactive.isolate():
        effects["_signal_dialog_table"]()
        effects["_clear_filters_on_view_change"]()
    assert [r.getMessage() for r in caplog.records] == []


@pytest.mark.parametrize("view", ["SRC", "T1", "T3"])
def test_the_new_calls_of_the_start_path_are_guarded(tmp_path, monkeypatch, view):
    """The Source list, the screen record of the export, the badge and the table do not raise: they say so in plain words or show nothing."""
    home = zero_recipes(tmp_path, monkeypatch, view=view)
    with reactive.isolate():
        text = home.readers["export"]["screen_view"]()
        assert text.startswith("Exploration mode, data view")
        home.outputs["source_table_ui"]()
        home.outputs["home_data_preview_badge"]()
        assert home.readers["view_source_table"]() is None
        assert home.readers["current_view_key"]() is None
