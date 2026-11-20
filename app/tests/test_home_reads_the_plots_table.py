"""HOME reads the table of a plot through `DataOrchestrator.materialize_tier3` (piece A4, slice A of the HOME audit redesign).

The real `home_theater.define_server` is run with every part a fake except the recipe, the orchestrator and the keys; the two readers
HOME hands to the filter handlers (`_resolve_active_lf`, `_table_identity`) are captured and called, so the wiring of HOME's reader is
run without a browser (the plot render itself is run by the browser tests).

What is proved: the data choice T2 still shows the stored Tier 2 for every plot; T3 and the plot read the plot's table (its tier-3 steps
applied); a plot with no tier-3 steps is untouched in both; the filter form's table identity holds the plot's key on T3 only; an entry
that is not a plot of the open recipe is refused with a plain error and never read as another table.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_reads_the_plots_table.py -q
"""
import copy

import pytest
from shiny import reactive

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.t3_audit_engine import dialog_rows_signature, stored_table_identity
from app.tests.home_harness import Home as _Home
from app.tests.test_tier3_reader import Tier3World, ids


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def Home(tmp_path, monkeypatch, view: str):
    """The real HOME with the data choice `view` (a plot "p_steps" with tier-3 steps and "p_plain" without, both on the join C)."""
    return _Home(Tier3World(tmp_path), monkeypatch, view=view, subtab="subtab_p_steps")


def test_t3_and_the_plot_read_the_plots_table_and_t2_still_reads_the_stored_tier2(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T3")
    steps_table = home.read("p_steps")                  # the data choice T3: the default tier is the choice's
    assert ids(steps_table) == ["s3", "s4", "s5"] and "group" not in steps_table.columns
    assert ids(home.read("p_steps", tier="T3")) == ["s3", "s4", "s5"], "a plot asks for T3 explicitly: the table the plot reads"
    result = home.read("p_steps", tier="T2")
    assert ids(result) == ["s1", "s2", "s3", "s4", "s5"] and "group" in result.columns, "T2 is the stored Tier 2"
    assert ids(home.read("p_plain", tier="T3")) == ["s1", "s2", "s3", "s4", "s5"] and "group" in home.read("p_plain", tier="T3").columns


def test_the_default_tier_follows_the_data_choice_and_t1_is_not_changed(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T2")
    assert ids(home.read("p_steps")) == ["s1", "s2", "s3", "s4", "s5"], "the choice is T2: the Tier 2 of the table, whatever the plot's steps"
    home = Home(tmp_path / "t1", monkeypatch, "T1")
    t1 = home.read("p_steps")
    assert ids(t1) == ["s1", "s2", "s3", "s4", "s5"] and "group" in t1.columns, "the choice is T1: the table after tier 1, whatever the plot's steps"


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
    assert mine != result, "T3 of a plot with tier-3 steps is another table than its T2"
    assert plain[-1] is None, "a plot without tier-3 steps reads the stored table as it is: no plot key"
    assert plain == plain_result, "B1: the same table in T2 and in T3 has the same identity (the form is not mounted again)"
    assert mine != plain, "two plots on one table with different tier-3 steps are two tables"


def test_the_rows_signature_of_the_filter_form_is_equal_across_a_change_of_view_for_a_plot_without_tier3_steps(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch, "T3")
    with reactive.isolate():
        for plot_id in ("p_steps", "p_plain"):
            home.read(plot_id, tier="T3")
        sign = lambda plot_id, tier: dialog_rows_signature(home.readers["_table_identity"](home.entry(plot_id), tier), [])
        assert sign("p_plain", "T2") == sign("p_plain", "T3"), "no tier-3 steps: a change of view keeps the signature"
        assert sign("p_steps", "T2") != sign("p_steps", "T3"), "tier-3 steps: T3 is another table, the signature changes"
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


def test_the_plot_and_the_original_pane_of_compare_are_drawn_from_the_plots_table_in_every_data_choice(tmp_path, monkeypatch):
    """M1, the render itself (headless: the real `define_server`, the plot render functions it registers, a factory that records the rows it
    is handed). The plot with tier-3 steps is drawn from its 3 kept rows and the plot without from the 5 rows of the Tier 2, whatever the data
    choice: a plot drawn from the Tier 2 of its target (the old reader) fails here. The browser test is `test_shiny_plot_tier3.py`."""
    for view in ("T2", "T3"):
        home = Home(tmp_path / view, monkeypatch, view)
        with reactive.isolate():
            home.outputs["plot_group_p_steps"]()
            home.outputs["plot_group_p_plain"]()
            assert ids(home.drawn["p_steps"]) == ["s3", "s4", "s5"] and "group" not in home.drawn["p_steps"].columns, view
            assert ids(home.drawn["p_plain"]) == ["s1", "s2", "s3", "s4", "s5"], view
            home.drawn.clear()
            home.outputs["plot_group_p_steps_cmp_base"]()
            home.outputs["plot_group_p_plain_cmp_base"]()
            assert ids(home.drawn["p_steps"]) == ["s3", "s4", "s5"], f"Compare's original pane with the data choice {view}"
            assert ids(home.drawn["p_plain"]) == ["s1", "s2", "s3", "s4", "s5"]
