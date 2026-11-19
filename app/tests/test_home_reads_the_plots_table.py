"""HOME reads the table of a plot through `DataOrchestrator.materialize_tier3` (piece A4, slice A of the HOME audit redesign).

The real `home_theater.define_server` is run with every part a fake except the recipe, the orchestrator and the keys; the two readers
HOME hands to the filter handlers (`_resolve_active_lf`, `_table_identity`) are captured and called, so the wiring of HOME's reader is
run without a browser (the plot render itself is run by the browser tests).

What is proved: the data view "Result" (T2) still shows the stored Tier 2 for every plot; "My view" (T3) and the plot read the plot's table
(its tier-3 steps applied); a plot with no tier-3 steps is untouched in both; the filter form's table identity holds the plot's key in
My view only; an entry that is not a plot of the open recipe is refused with a plain error and never read as another table.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_reads_the_plots_table.py -q
"""
import copy
from types import SimpleNamespace
from unittest import mock

import pytest
from shiny import reactive, render, ui

import app.handlers.home_theater as home_theater
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.t3_audit_engine import dialog_rows_signature, stored_table_identity
from app.tests.test_tier3_reader import Tier3World, ids


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class Home:
    """`define_server` with fakes; `readers` holds what HOME hands to the filter handlers."""

    def __init__(self, tmp_path, monkeypatch, tier: str):
        self.readers = {}
        monkeypatch.setattr(reactive, "Effect", lambda fn: fn)
        monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(reactive, "Calc", lambda fn: fn)
        monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
        for name in ("plot", "text", "data_frame", "download"):
            monkeypatch.setattr(render, name, lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(ui, "notification_show", lambda *a, **k: None)
        monkeypatch.setattr(home_theater, "define_filter_audit_server", lambda *a, **kw: self.readers.update(kw))
        self.world = Tier3World(tmp_path)
        self.cfg = load_data_analysis_recipe(self.world.data_analysis_recipes_dir / "tiny.yaml").config
        bootloader = mock.MagicMock()
        bootloader.get_location.side_effect = (
            lambda key: self.world.data_analysis_recipes_dir if key == "data_analysis_recipes" else self.world.root / "user")
        bootloader.get_default_data_analysis_recipe_or_none.return_value = "tiny"
        bootloader.get_default_data_analysis_recipe.return_value = "tiny"
        bootloader.is_enabled.return_value = False
        home_theater.define_server(
            mock.MagicMock(), lambda *a, **k: (lambda fn: fn) if not (a and callable(a[0])) else a[0], mock.MagicMock(),
            bootloader=bootloader, wrangle_studio=mock.MagicMock(), dev_studio=mock.MagicMock(),
            orchestrator=self.world.orch, viz_factory=mock.MagicMock(), gallery_viewer=mock.MagicMock(),
            current_app_features=mock.MagicMock(), anchor_path=mock.MagicMock(), tier1_anchor=mock.MagicMock(),
            active_cfg=lambda: self.cfg, active_collection_id=mock.MagicMock(),
            safe_input=lambda i, k, d: "tiny" if k == "data_analysis_recipe_id" else d,
            active_home_subtab=mock.MagicMock(), tier_toggle=SimpleNamespace(get=lambda: tier),
            home_state=reactive.Value({}), session_manager=mock.MagicMock(), notification_log=reactive.Value([]))

    def entry(self, plot_id: str) -> dict:
        return self.cfg.raw_config["analysis_groups"]["g"]["plots"][plot_id]

    def read(self, plot_id: str, tier=None):
        with reactive.isolate():
            return self.readers["_resolve_active_lf"](self.entry(plot_id), tier).collect()


def test_my_view_and_the_plot_read_the_plots_table_and_the_result_view_still_reads_the_stored_tier2(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T3")
    steps_table = home.read("p_steps")                  # the data view My view: the default tier is the toggle's
    assert ids(steps_table) == ["s3", "s4", "s5"] and "group" not in steps_table.columns
    assert ids(home.read("p_steps", tier="T3")) == ["s3", "s4", "s5"], "a plot asks for T3 explicitly: the table the plot reads"
    result = home.read("p_steps", tier="T2")
    assert ids(result) == ["s1", "s2", "s3", "s4", "s5"] and "group" in result.columns, "the data view Result is the stored Tier 2"
    assert ids(home.read("p_plain", tier="T3")) == ["s1", "s2", "s3", "s4", "s5"] and "group" in home.read("p_plain", tier="T3").columns


def test_the_data_view_result_follows_the_toggle_and_the_raw_view_is_not_changed(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T2")
    assert ids(home.read("p_steps")) == ["s1", "s2", "s3", "s4", "s5"], "the toggle is Result: the Tier 2 of the table, whatever the plot's steps"


def test_an_entry_that_is_not_a_plot_of_the_open_recipe_is_refused_not_read_as_another_table(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T3")
    stranger = copy.deepcopy(home.entry("p_steps"))
    with pytest.raises(RuntimeError, match="not a plot of the open data analysis recipe"):
        with reactive.isolate():
            home.readers["_resolve_active_lf"](stranger, "T3")


def test_the_table_identity_of_the_filter_form_holds_the_plots_key_only_for_a_plot_with_tier3_steps(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T3")
    with reactive.isolate():
        for plot_id in ("p_steps", "p_plain"):
            home.read(plot_id, tier="T3")                # builds and stores the tables the identity reads
        mine = home.readers["_table_identity"](home.entry("p_steps"), "T3")
        result = home.readers["_table_identity"](home.entry("p_steps"), "T2")
        plain = home.readers["_table_identity"](home.entry("p_plain"), "T3")
        plain_result = home.readers["_table_identity"](home.entry("p_plain"), "T2")
    keys = home.world.keys()
    assert mine[-1] == keys.plot_key_of("p_steps"), "a plot with tier-3 steps: its table is not a stored one, its key is in the identity"
    assert result[-1] is None, "T1 and T2 read stored files: their identity has no plot key"
    assert mine[:-1] == result[:-1], "the stored files they read are the same"
    assert mine != result, "My view of a plot with tier-3 steps is another table than its Result"
    assert plain[-1] is None, "a plot without tier-3 steps reads the stored table as it is: no plot key"
    assert plain == plain_result, "B1: the same table in Result and in My view has the same identity (the form is not mounted again)"
    assert mine != plain, "two plots on one table with different tier-3 steps are two tables"


def test_the_rows_signature_of_the_filter_form_is_equal_across_a_change_of_view_for_a_plot_without_tier3_steps(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T3")
    with reactive.isolate():
        for plot_id in ("p_steps", "p_plain"):
            home.read(plot_id, tier="T3")
        sign = lambda plot_id, tier: dialog_rows_signature(home.readers["_table_identity"](home.entry(plot_id), tier), [])
        assert sign("p_plain", "T2") == sign("p_plain", "T3"), "no tier-3 steps: a change of view keeps the signature"
        assert sign("p_steps", "T2") != sign("p_steps", "T3"), "tier-3 steps: My view is another table, the signature changes"
        assert sign("p_steps", "T3") != sign("p_plain", "T3")


def test_stored_table_identity_puts_the_plot_key_in_only_when_it_differs_from_the_tables_key(tmp_path):
    import polars as pl
    from app.modules.orchestrator import TIER1_KEY_META
    t1 = tmp_path / "t.parquet"
    pl.DataFrame({"a": [1]}).write_parquet(t1, metadata={TIER1_KEY_META: "k1"})
    same = stored_table_identity("T3", "t", "r", "vk", t1, 0, plot_key="K2", table_key="K2")
    other = stored_table_identity("T3", "t", "r", "vk", t1, 0, plot_key="K3", table_key="K2")
    assert same[-1] is None and other[-1] == "K3"
    assert same == stored_table_identity("T2", "t", "r", "vk", t1, 0, plot_key="K2", table_key="K2")
