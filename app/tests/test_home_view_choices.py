"""The data choice of HOME and the two modes, run headless on the real `home_theater.define_server` (slice B, D-0310, D-0311, D-0016, D-0019).

`app/tests/home_harness.py` runs HOME with every part a fake except the recipe, the orchestrator and the keys. `ViewWorld` has two source
tables (T: its tier 1 keeps score <= 4; M), a join J of them (tier 2 keeps score >= 2) and three plots: `p_table` (on T), `p_join` (on J),
`p_steps` (on J, its own tier-3 steps: score >= 3 and drop `site`).

What is proved:
- (d) Source, T1, T2, T3 each show the right table for a plot on a table, a plot on a join, a plot with its own tier-3 steps, a table without
  tier-2 steps; the plot and its T3 table hold the same rows.
- (a) in Exploration a filter changes the table of every view and never the plot; (f) in Audit mode T3 is the audited table, the plot is the
  audited plot, Compare's original pane is the Result, T1/T2/Source are the original tables, exploration filters change nothing.
- (e) Source: the list of source tables of the plot, the table read from its file, a missing file gives a plain error and the app stays usable.
- (c) the mode switch exists only with the audit flag, and Compare only in Audit mode.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_view_choices.py -q
"""
import polars as pl
import pytest
from shiny import reactive

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.audit_nodes import filter_nodes
from app.tests.home_harness import Home, ViewWorld, ids

AUDIT = ("interactivity_enabled", "t3_sandbox_enabled", "comparison_mode_enabled", "session_management_enabled", "export_enabled")
SCORE_GE_4 = {"column": "score", "op": "ge", "value": 4, "dtype": "Int64", "na": "remove"}
AUDITED_SCORE_LE_3 = filter_nodes([{"column": "score", "op": "le", "value": 3, "dtype": "Int64", "na": "remove"}])


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


@pytest.fixture
def world(tmp_path):
    return ViewWorld(tmp_path)


def table(home: Home, view: str, plot: str, source=None):
    """The table the data preview shows for `view` of `plot` (the real `home_data_preview` render function, its DataGrid)."""
    home.set(view=view, subtab=f"subtab_{plot}", source=source)
    with reactive.isolate():
        grid = home.outputs["home_data_preview"]()
    return grid.data


def test_a_data_choice_shows_the_right_table_for_a_plot_on_a_table_a_plot_on_a_join_and_a_plot_with_its_own_steps(world, monkeypatch):
    home = Home(world, monkeypatch, flags=("interactivity_enabled",))
    # a plot on a table (T): Source is the file as read (5 rows); T1 the table after its tier-1 step (4 rows); no tier-2 steps: T2 = T1 = T3
    assert ids(table(home, "SRC", "p_table", "T")) == ["s1", "s2", "s3", "s4", "s5"]
    for view in ("T1", "T2", "T3"):
        assert ids(table(home, view, "p_table")) == ["s1", "s2", "s3", "s4"], view
    # a plot on a join (J): its sources are T and M; T1 = the join after tier 1, T2 after tier 2 (score >= 2), T3 = T2 (no tier-3 steps)
    assert ids(table(home, "SRC", "p_join", "T")) == ["s1", "s2", "s3", "s4", "s5"]
    assert table(home, "SRC", "p_join", "M").columns == ["sample_id", "site"]
    assert ids(table(home, "T1", "p_join")) == ["s1", "s2", "s3", "s4"] and "site" in table(home, "T1", "p_join").columns
    assert ids(table(home, "T2", "p_join")) == ["s2", "s3", "s4"]
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3", "s4"]
    # a plot with its own tier-3 steps: T1 and T2 as the join's, T3 the plot's own table (score >= 3, `site` dropped)
    assert ids(table(home, "T1", "p_steps")) == ["s1", "s2", "s3", "s4"]
    assert ids(table(home, "T2", "p_steps")) == ["s2", "s3", "s4"]
    t3 = table(home, "T3", "p_steps")
    assert ids(t3) == ["s3", "s4"] and "site" not in t3.columns


def test_the_plot_and_the_t3_table_hold_the_same_rows_for_every_plot(world, monkeypatch):
    home = Home(world, monkeypatch)
    for plot in ("p_table", "p_join", "p_steps"):
        drawn = home.plot(plot)
        shown = table(home, "T3", plot)
        assert drawn.equals(shown), plot


def test_the_data_choice_starts_on_t3_and_the_mode_on_exploration_in_the_server():
    """P-B1 (PROVISIONAL): server.py starts the data choice on T3, the table the plot shows; the mode on Exploration."""
    import re
    from pathlib import Path
    server = (Path(__file__).resolve().parents[1] / "src" / "server.py").read_text()
    assert re.search(r'data_view = reactive\.Value\("T3"\)', server) and re.search(r'home_mode = reactive\.Value\("exploration"\)', server)


# -- (a) Exploration: a filter changes the table, never the plot ---------------------------------------------------

@pytest.mark.parametrize("view,source", [("SRC", "T"), ("T1", None), ("T2", None), ("T3", None)])
def test_an_exploration_filter_changes_the_table_of_the_view_shown_and_never_the_plot(world, monkeypatch, view, source):
    """MUTATION V1: the plot render applies the exploration filters again (the old "My view"): this fails on the plot rows."""
    home = Home(world, monkeypatch)
    before_plot = home.plot("p_join")
    before_table = table(home, view, "p_join", source)
    with reactive.isolate():
        home.filters_applied.set([SCORE_GE_4])
    after_table = table(home, view, "p_join", source)
    assert ids(after_table) == ["s4", "s5"] if view == "SRC" else ids(after_table) == ["s4"]
    assert after_table.height < before_table.height
    assert home.plot("p_join").equals(before_plot) and ids(home.plot("p_join")) == ["s2", "s3", "s4"]


def test_exploration_draws_the_result_even_when_audited_steps_exist(world, monkeypatch):
    """D-0019, D-0180: Exploration has ONE plot, the Result, with no audited step on it; the audited steps wait in Audit mode."""
    state = {"t3_audit_steps_by_plot": {"subtab_p_join": AUDITED_SCORE_LE_3}}
    home = Home(world, monkeypatch, flags=AUDIT, mode="exploration", home_state=state)
    assert ids(home.plot("p_join")) == ["s2", "s3", "s4"]
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3", "s4"], "the T3 table of Exploration holds no audited step either"


# -- (f) Audit mode ------------------------------------------------------------------------------------------------

def test_audit_mode_t3_is_the_audited_table_and_the_plot_is_the_audited_plot(world, monkeypatch):
    state = {"t3_audit_steps_by_plot": {"subtab_p_join": AUDITED_SCORE_LE_3}}
    home = Home(world, monkeypatch, flags=AUDIT, mode="audit", home_state=state)
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3"], "T3 of Audit mode: the plot's table after the audited step (score <= 3)"
    assert ids(home.plot("p_join")) == ["s2", "s3"] and home.plot("p_join").equals(table(home, "T3", "p_join"))
    # the original pane of Compare is the Result: the plot's table with no audited step
    with reactive.isolate():
        home.outputs["plot_group_p_join_cmp_base"]()
    assert ids(home.drawn["p_join"]) == ["s2", "s3", "s4"]
    # the other plots have no audited step: their plot is their table
    assert ids(home.plot("p_steps")) == ["s3", "s4"]


@pytest.mark.parametrize("view", ["T1", "T2"])
def test_audit_mode_shows_the_original_tables_on_t1_and_t2(world, monkeypatch, view):
    state = {"t3_audit_steps_by_plot": {"subtab_p_join": AUDITED_SCORE_LE_3}}
    audit = Home(world, monkeypatch, flags=AUDIT, mode="audit", home_state=state)
    exploration = Home(world, monkeypatch, flags=AUDIT, mode="exploration", home_state=state)
    assert table(audit, view, "p_join").equals(table(exploration, view, "p_join"))


def test_audit_mode_source_is_the_original_table(world, monkeypatch):
    state = {"t3_audit_steps_by_plot": {"subtab_p_join": AUDITED_SCORE_LE_3}}
    home = Home(world, monkeypatch, flags=AUDIT, mode="audit", home_state=state)
    assert ids(table(home, "SRC", "p_join", "T")) == ["s1", "s2", "s3", "s4", "s5"]


def test_exploration_filters_do_not_exist_in_audit_mode(world, monkeypatch):
    """A filter that survived in the reactive value (cleared by the effect in the app) changes neither the table nor the plot in Audit mode."""
    state = {"t3_audit_steps_by_plot": {"subtab_p_join": AUDITED_SCORE_LE_3}}
    home = Home(world, monkeypatch, flags=AUDIT, mode="audit", home_state=state)
    with reactive.isolate():
        home.filters_applied.set([SCORE_GE_4])
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3"] and ids(table(home, "T2", "p_join")) == ["s2", "s3", "s4"]
    assert ids(home.plot("p_join")) == ["s2", "s3"]


def test_without_the_audit_flag_the_mode_is_exploration_even_if_the_value_says_audit(world, monkeypatch):
    """No audit flag, no Audit mode: a stale value cannot put audited steps on a plot."""
    state = {"t3_audit_steps_by_plot": {"subtab_p_join": AUDITED_SCORE_LE_3}}
    home = Home(world, monkeypatch, flags=("interactivity_enabled",), mode="audit", home_state=state)
    assert ids(home.plot("p_join")) == ["s2", "s3", "s4"] and ids(table(home, "T3", "p_join")) == ["s2", "s3", "s4"]


# -- (e) Source ----------------------------------------------------------------------------------------------------

def html(tag) -> str:
    return str(tag)


def test_the_second_list_names_the_source_tables_of_the_open_plot(world, monkeypatch):
    home = Home(world, monkeypatch, view="SRC", subtab="subtab_p_join")
    with reactive.isolate():
        listed = html(home.outputs["source_table_ui"]())
    assert 'id="source_table"' in listed and ">T<" in listed and ">M<" in listed
    home.set(subtab="subtab_p_table")
    with reactive.isolate():
        listed = html(home.outputs["source_table_ui"]())
    assert ">T<" in listed and ">M<" not in listed, "one table feeds this plot: the list still shows, with that one table"


def test_the_second_list_is_absent_unless_the_source_is_chosen(world, monkeypatch):
    home = Home(world, monkeypatch, view="T2")
    with reactive.isolate():
        assert "source_table" not in html(home.outputs["source_table_ui"]())


def test_the_pick_that_does_not_feed_the_open_plot_falls_back_to_the_first_table_that_does(world, monkeypatch):
    home = Home(world, monkeypatch, view="SRC", subtab="subtab_p_table", source="M")   # M does not feed p_table
    assert table(home, "SRC", "p_table", "M").columns == ["sample_id", "group", "score"]


def test_the_source_table_is_read_with_its_declared_types(world, monkeypatch):
    home = Home(world, monkeypatch)
    schema = table(home, "SRC", "p_table", "T").schema
    assert schema["score"] == pl.Int64 and schema["sample_id"] == pl.String


def test_a_missing_source_file_is_a_plain_text_in_the_tables_place_and_the_app_stays_usable(world, monkeypatch):
    """The plain IngestionError text, not a traceback; the other views and the plot still work."""
    (world.data_dir / "M.tsv").unlink()
    home = Home(world, monkeypatch)
    shown = table(home, "SRC", "p_join", "M")
    assert shown.columns == ["Error"] and "Source table 'M' could not be read" in shown["Error"][0]
    assert "Traceback" not in shown["Error"][0]
    assert ids(table(home, "T3", "p_table")) == ["s1", "s2", "s3", "s4"], "T and its views do not depend on M"
    assert ids(table(home, "SRC", "p_table", "T")) == ["s1", "s2", "s3", "s4", "s5"]


def test_the_badge_of_the_source_says_which_table_and_that_it_is_before_any_step(world, monkeypatch):
    home = Home(world, monkeypatch, view="SRC", subtab="subtab_p_join", source="M")
    with reactive.isolate():
        badge = html(home.outputs["home_data_preview_badge"]())
    assert "Viewing: Source" in badge and "table &#x27;M&#x27;" in badge.replace("'", "&#x27;") and "before any recipe step" in badge


# -- (c) the switch and Compare ------------------------------------------------------------------------------------

def test_the_audit_strip_row_holds_compare_in_audit_mode_only(world, monkeypatch):
    exploration = Home(world, monkeypatch, flags=AUDIT, mode="exploration")
    with reactive.isolate():
        assert "audit_compare" not in html(exploration.outputs["audit_strip_ui"]())
    audit = Home(world, monkeypatch, flags=AUDIT, mode="audit")
    with reactive.isolate():
        row = html(audit.outputs["audit_strip_ui"]())
    assert 'id="audit_compare"' in row and "Audit steps apply to the plot&#x27;s table (T3) for now." in row.replace("'", "&#x27;")


def test_compare_needs_the_comparison_flag_even_in_audit_mode(world, monkeypatch):
    home = Home(world, monkeypatch, flags=("interactivity_enabled", "t3_sandbox_enabled"), mode="audit")
    with reactive.isolate():
        assert "audit_compare" not in html(home.outputs["audit_strip_ui"]())


def _strip(home: Home) -> str:
    with reactive.isolate():
        return html(home.outputs["dynamic_tabs"]())


def test_the_mode_switch_exists_only_with_the_audit_flag(world, monkeypatch):
    from unittest import mock
    for flags, expected in ((AUDIT, True), (("interactivity_enabled",), False), (("interactivity_enabled", "comparison_mode_enabled"), False)):
        home = Home(world, monkeypatch, flags=flags)
        text = _strip(home)
        assert ('id="home_mode"' in text) is expected, flags
        assert 'id="data_view"' in text, "the data choice exists whenever the strip does"


def test_the_strip_is_absent_without_interactivity(world, monkeypatch):
    text = _strip(Home(world, monkeypatch, flags=()))
    assert 'id="home_mode"' not in text and 'id="data_view"' not in text and "theater-header-strip" not in text


def test_the_data_choice_has_the_four_values_and_the_old_names_are_gone(world, monkeypatch):
    text = _strip(Home(world, monkeypatch, flags=AUDIT))
    for value in ("SRC", "T1", "T2", "T3"):
        assert f'value="{value}"' in text
    for old in ("My view", "Raw", "Plot to show", "Data to show", 'id="plot_view"', 'id="tier_toggle"'):
        assert old not in text, old
