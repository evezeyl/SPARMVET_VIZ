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
from app.tests.audit_nodes import audit_state, filter_nodes
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


def stamped(home: Home, row: dict) -> dict:
    """The row as "+ Add" stages it: carrying the view key of the view on screen now (review F3)."""
    with reactive.isolate():
        return {**row, "view": home.readers["current_view_key"]()}


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
    row = stamped(home, SCORE_GE_4)
    with reactive.isolate():
        home.filters_applied.set([row])
    after_table = table(home, view, "p_join", source)
    assert ids(after_table) == ["s4", "s5"] if view == "SRC" else ids(after_table) == ["s4"]
    assert after_table.height < before_table.height
    assert home.plot("p_join").equals(before_plot) and ids(home.plot("p_join")) == ["s2", "s3", "s4"]


def test_exploration_draws_the_result_even_when_audited_steps_exist(world, monkeypatch):
    """D-0019, D-0180: Exploration has ONE plot, the Result, with no audited step on it; the audited steps wait in Audit mode."""
    state = audit_state("p_join", AUDITED_SCORE_LE_3)
    home = Home(world, monkeypatch, flags=AUDIT, mode="exploration", home_state=state)
    assert ids(home.plot("p_join")) == ["s2", "s3", "s4"]
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3", "s4"], "the T3 table of Exploration holds no audited step either"


# -- (f) Audit mode ------------------------------------------------------------------------------------------------

def test_audit_mode_t3_is_the_audited_table_and_the_plot_is_the_audited_plot(world, monkeypatch):
    state = audit_state("p_join", AUDITED_SCORE_LE_3)
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
def test_audit_mode_shows_the_original_tables_on_t1_and_t2_where_no_step_changes_them(world, monkeypatch, view):
    """Slice 3a: in Audit mode the table shown is the place shown (`T1:J`, `T2:J`), not a data choice. The audited step here is written at the plot's tier 3 only, so the tables of J are the originals."""
    state = audit_state("p_join", AUDITED_SCORE_LE_3)
    audit = Home(world, monkeypatch, flags=AUDIT, mode="audit", home_state=state, subtab="subtab_p_join")
    exploration = Home(world, monkeypatch, flags=AUDIT, mode="exploration", home_state=state)
    audit.show(f"{view}:J")
    with reactive.isolate():
        shown = audit.outputs["home_data_preview"]().data
    assert shown.equals(table(exploration, view, "p_join"))


def test_audit_mode_ignores_the_data_choice_and_shows_the_audited_result_data_with_nothing_shown(world, monkeypatch):
    """The strip "Table to view" is hidden in Audit mode (slice 3a): a stale choice (here Source) changes nothing, the preview is the Result data (T3) of the open plot, audited."""
    state = audit_state("p_join", AUDITED_SCORE_LE_3)
    home = Home(world, monkeypatch, flags=AUDIT, mode="audit", home_state=state)
    assert ids(table(home, "SRC", "p_join", "T")) == ["s2", "s3"]


def test_exploration_filters_do_not_exist_in_audit_mode(world, monkeypatch):
    """A filter that survived in the reactive value (cleared by the effect in the app) changes neither the table nor the plot in Audit mode."""
    state = audit_state("p_join", AUDITED_SCORE_LE_3)
    home = Home(world, monkeypatch, flags=AUDIT, mode="audit", home_state=state)
    row = stamped(home, SCORE_GE_4)
    with reactive.isolate():
        home.filters_applied.set([row])
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3"]
    home.show("T2:J")
    with reactive.isolate():
        assert ids(home.outputs["home_data_preview"]().data) == ["s2", "s3", "s4"]
    assert ids(home.plot("p_join")) == ["s2", "s3"]


def test_without_the_audit_flag_the_mode_is_exploration_even_if_the_value_says_audit(world, monkeypatch):
    """No audit flag, no Audit mode: a stale value cannot put audited steps on a plot."""
    state = audit_state("p_join", AUDITED_SCORE_LE_3)
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
    """The plain IngestionError text, not a traceback; the Source view of the other table still works."""
    (world.data_dir / "M.tsv").unlink()
    home = Home(world, monkeypatch)
    shown = table(home, "SRC", "p_join", "M")
    assert shown.columns == ["Error"] and "Source table 'M' could not be read" in shown["Error"][0]
    assert "Traceback" not in shown["Error"][0]
    # T and M both declare an entity id, so they take part in the completion of the ids: T cannot be built without the ids of M (D-0613), and says so in plain words, naming M.
    # The file of T as read (the Source view) does not need M.
    built = table(home, "T3", "p_table")
    assert built.columns == ["Error"] and "The ids of the table 'M' could not be read" in built["Error"][0] and "Traceback" not in built["Error"][0]
    assert ids(table(home, "SRC", "p_table", "T")) == ["s1", "s2", "s3", "s4", "s5"]


def test_the_badge_of_the_source_says_which_table_and_that_it_is_before_any_step(world, monkeypatch):
    home = Home(world, monkeypatch, view="SRC", subtab="subtab_p_join", source="M")
    with reactive.isolate():
        badge = html(home.outputs["home_data_preview_badge"]())
    assert "Viewing: Source" in badge and "table &#x27;M&#x27;" in badge.replace("'", "&#x27;") and "before any recipe step" in badge


# -- (c) the switch and Compare ------------------------------------------------------------------------------------

def test_the_compare_line_holds_the_switch_in_audit_mode_only(world, monkeypatch):
    exploration = Home(world, monkeypatch, flags=AUDIT, mode="exploration")
    with reactive.isolate():
        assert "audit_compare" not in html(exploration.outputs["compare_switch_ui"]())
    audit = Home(world, monkeypatch, flags=AUDIT, mode="audit")
    with reactive.isolate():
        row = html(audit.outputs["compare_switch_ui"]())
    assert 'id="audit_compare"' in row and "Compare with the original" in row
    assert "for now" not in row and "plot's table" not in row.replace("&#x27;", "'"), "the old sentence of the audit strip is gone"


def test_compare_needs_the_comparison_flag_even_in_audit_mode(world, monkeypatch):
    home = Home(world, monkeypatch, flags=("interactivity_enabled", "t3_sandbox_enabled"), mode="audit")
    with reactive.isolate():
        assert "audit_compare" not in html(home.outputs["compare_switch_ui"]())


def _strip(home: Home) -> str:
    """What `dynamic_tabs` draws and the strip "Table to view" (its own output since slice 3a: `data_strip_ui`)."""
    with reactive.isolate():
        return html(home.outputs["dynamic_tabs"]()) + html(home.outputs["data_strip_ui"]())


def test_the_mode_switch_exists_only_with_the_audit_flag(world, monkeypatch):
    from unittest import mock
    for flags, expected in ((AUDIT, True), (("interactivity_enabled",), False), (("interactivity_enabled", "comparison_mode_enabled"), False)):
        home = Home(world, monkeypatch, flags=flags)
        text = _strip(home)
        assert ('id="home_mode"' in text) is expected, flags
        assert 'id="data_view"' in text, "the data choice exists whenever the strip does"


def _decisions(*nodes: tuple) -> dict:
    """HOME's state with committed audit steps: each item is `(decision id, place)`; two items with one id are ONE decision written at two places."""
    return {"t3_audit_steps_by_plot": {"__places__": [
        {"id": ident, "node_type": "filter_row", "params": {"column": "score", "op": "le", "value": 3, "dtype": "Int64", "na": "remove"}, "reason": "test",
         "place": place, "plot_scope": "__places__", "created_at": f"2026-11-26T10:00:0{i}"} for i, (ident, place) in enumerate(nodes)]}}


def _pane_label(world, monkeypatch, plot: str, *nodes: tuple) -> str:
    home = Home(world, monkeypatch, flags=AUDIT, mode="audit", subtab=f"subtab_{plot}", home_state=_decisions(*nodes))
    with reactive.isolate():
        return html(home.outputs[f"plot_cmp_label_{plot}"]())


def test_the_audited_pane_counts_two_decisions_at_one_table_as_two_steps(world, monkeypatch):
    assert "Audited (after 2 steps)" in _pane_label(world, monkeypatch, "p_table", ("a", "T1:T"), ("b", "T1:T"))


def test_the_audited_pane_counts_one_decision_written_at_two_places_as_one_step(world, monkeypatch):
    """MUTATION (seen failing): without the de-duplication by decision id in `_audit_nodes_for` this counts 2 (nodes, not decisions)."""
    assert "Audited (after 1 step)" in _pane_label(world, monkeypatch, "p_table", ("a", "T1:T"), ("a", "T3:p_table"))


def test_the_audited_pane_ignores_a_step_at_a_table_the_plot_is_not_built_from(world, monkeypatch):
    assert "Audited (no steps yet)" in _pane_label(world, monkeypatch, "p_table", ("a", "T1:M"))
    assert "Audited (after 1 step)" in _pane_label(world, monkeypatch, "p_join", ("a", "T1:M")), "the plot that IS built from that table counts it"


def _mode_row(home: Home) -> str:
    """The recipe banner and the mode row, the first element of what `dynamic_tabs` draws."""
    with reactive.isolate():
        tree = home.outputs["dynamic_tabs"]()
    return html(tree.children[0])


def test_the_mode_control_sits_in_a_row_of_its_own_with_the_title_and_leaves_the_strip(world, monkeypatch):
    home = Home(world, monkeypatch, flags=AUDIT)
    row, text = _mode_row(home), _strip(home)
    assert "spv-mode-row" in row and 'id="home_mode"' in row and 'class="banner-title"' in row, "the title and the control are one row"
    assert 'role="radiogroup"' in row and 'aria-labelledby="home_mode-label"' in row and ">Mode</span>" in row, "a labelled group (the label is visually hidden)"
    strip = text[text.index("theater-header-strip"):]
    assert 'id="home_mode"' not in strip and "Mode:" not in text, "the radios left the strip"
    assert 'id="data_view"' in strip, "Table to view stays in the strip"
    assert 'value="exploration"' in row and 'value="audit"' in row


def test_the_mode_row_exists_when_the_recipe_name_is_hidden_and_then_holds_the_control_alone(world, monkeypatch):
    home = Home(world, monkeypatch, flags=AUDIT)
    home.bootloader.show_recipe_name.return_value = False
    row = _mode_row(home)
    assert 'id="home_mode"' in row and "banner-title" not in row


def test_without_the_audit_there_is_no_control_and_the_banner_is_the_title_alone(world, monkeypatch):
    for flags in (("interactivity_enabled",), ("interactivity_enabled", "comparison_mode_enabled"), ()):
        home = Home(world, monkeypatch, flags=flags)
        row = _mode_row(home)
        assert "home_mode" not in row and "spv-mode-row" not in row and 'class="banner-title"' in row, flags
        home.bootloader.show_recipe_name.return_value = False
        assert "banner-title" not in _mode_row(home) and "home_mode" not in _mode_row(home), "the name hidden: no banner, no control"


def test_the_caption_tells_what_the_open_mode_does(world, monkeypatch):
    with reactive.isolate():
        exploration = html(Home(world, monkeypatch, flags=AUDIT, mode="exploration").outputs["mode_caption_ui"]())
        audit = html(Home(world, monkeypatch, flags=AUDIT, mode="audit").outputs["mode_caption_ui"]())
    assert "Nothing here is saved" in exploration and "never a plot" in exploration
    assert "change the plot and the export" in audit


def test_the_audited_pane_says_how_many_steps_reach_the_plot(world, monkeypatch):
    none = Home(world, monkeypatch, flags=AUDIT, mode="audit", subtab="subtab_p_join")
    with reactive.isolate():
        assert "Audited (no steps yet)" in html(none.outputs["plot_cmp_label_p_join"]())
    one = Home(world, monkeypatch, flags=AUDIT, mode="audit", subtab="subtab_p_join", home_state=audit_state("p_join", AUDITED_SCORE_LE_3))
    with reactive.isolate():
        assert "Audited (after 1 step)" in html(one.outputs["plot_cmp_label_p_join"]())


def test_the_strip_is_absent_without_interactivity(world, monkeypatch):
    text = _strip(Home(world, monkeypatch, flags=()))
    assert 'id="home_mode"' not in text and 'id="data_view"' not in text and "theater-header-strip" not in text


def test_the_data_choice_has_the_four_values_and_the_old_names_are_gone(world, monkeypatch):
    text = _strip(Home(world, monkeypatch, flags=AUDIT))
    for value in ("SRC", "T1", "T2", "T3"):
        assert f'value="{value}"' in text
    for old in ("My view", "Raw", "Plot to show", "Data to show", 'id="plot_view"', 'id="tier_toggle"'):
        assert old not in text, old


# -- review fixes: the memo of Source reads (F1), the view key of a filter (F3) ----------------------------------------

def test_an_edit_of_how_a_source_table_is_declared_is_read_again_not_served_from_the_memo(world, monkeypatch):
    """F1: the memo of Source reads is keyed by the recipe's own hash too. MUTATION M1 (the hash left out of the key): the table is served as
    it was read under the old declaration (score as Int64) after the recipe now declares it as a String."""
    home = Home(world, monkeypatch, view="SRC", subtab="subtab_p_table", source="T")
    assert table(home, "SRC", "p_table", "T").schema["score"] == pl.Int64
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    recipe.write_text(recipe.read_text().replace("score: {original_name: score, type: Int64", "score: {original_name: score, type: String", 1))
    clear_data_analysis_recipe_cache()
    assert table(home, "SRC", "p_table", "T").schema["score"] == pl.String


def test_a_filter_built_on_another_view_is_not_applied_by_the_preview(world, monkeypatch):
    """F3: a row carries the view key it was built on; the preview applies it only while the view is that one. A row built on T1 does nothing on
    T3, a row with no key does nothing anywhere, a row built on this view applies. MUTATION K1 (the preview applies every row): this fails."""
    home = Home(world, monkeypatch, view="T3", subtab="subtab_p_join")
    other = stamped(Home(world, monkeypatch, view="T1", subtab="subtab_p_join"), SCORE_GE_4)
    with reactive.isolate():
        home.filters_applied.set([other])
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3", "s4"], "a filter built on T1 is not applied on T3"
    with reactive.isolate():
        home.filters_applied.set([dict(SCORE_GE_4)])
    assert ids(table(home, "T3", "p_join")) == ["s2", "s3", "s4"], "a row with no view key is never applied"
    with reactive.isolate():
        home.filters_applied.set([stamped(home, SCORE_GE_4)])
    assert ids(table(home, "T3", "p_join")) == ["s4"]


def test_the_badge_counts_only_the_filters_of_this_view(world, monkeypatch):
    home = Home(world, monkeypatch, view="T3", subtab="subtab_p_join")
    other = stamped(Home(world, monkeypatch, view="T1", subtab="subtab_p_join"), SCORE_GE_4)
    with reactive.isolate():
        home.filters_applied.set([other])
        assert "preview filter" not in html(home.outputs["home_data_preview_badge"]())
        home.filters_applied.set([stamped(home, SCORE_GE_4)])
        assert "1 preview filter(s) on" in html(home.outputs["home_data_preview_badge"]())


def test_plus_add_stamps_the_row_with_the_view_it_was_built_on(world, monkeypatch):
    """The real `_filter_add_row` stages the row with the view key of the screen (the same `view_key` the clearing effect uses)."""
    inputs = {"fb_col": "score", "fb_op": "ge", "fb_value": 3}
    home = Home(world, monkeypatch, view="T2", subtab="subtab_p_join", inputs=inputs)
    effects = home.filter_handlers(monkeypatch)
    with reactive.isolate():
        effects["_filter_add_row"]()
        [row] = home.filters_pending.get()
        assert row["view"] == home.readers["current_view_key"]() == ("tiny", "exploration", "T2", None, ("J", None))
        assert row["column"] == "score" and row["op"] == "ge"
