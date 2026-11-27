"""The shown item of HOME in Audit mode (slice 3a): the pure rules of `app/modules/audit_shown.py` and the notice of `t3_audit_engine.view_change_notice` for the table shown.

The design expects (D-0653, D-0654, D-0655, D-0657; the header-strip design page of 2026-11-26): choosing a place only stages it; "Show" shows one place; "Show selection" shows the first place
clicked and the others are counted; a place that cannot be shown is a plain sentence and never another table; the band says what is shown and whether it is the original or the audited table; a
condition built on the table shown is cleared, with a notice, only when another table is shown (or the columns of the table shown changed), never when the same table is shown again; a selection that
does not include the place shown is refused with "Show your selection first".

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_shown.py -q

Mutation index (each seen failing): MUTATION S1 `request_to_show` takes the LAST chosen place for "Show selection"; S2 `request_to_show` accepts a stale id; S3 `others_chosen` counts the shown place too;
S4 `selection_problem` never refuses; S5 `view_change_notice` ignores the columns part of the key.
"""
import pytest

from app.modules.audit_place_view import AUDIT, ORIGINAL, AUDITED, TableFacts, view_identity, viewed
from app.modules.audit_places import nodes_reaching_node, plots_below
from app.modules.audit_shown import (CHOOSE_FIRST, SHOW_SELECTION_FIRST, band_lines, others_chosen, open_subtab_of, plot_area_title, request_to_show, selection_problem, table_shown_in_panel, table_shown_lines, unlisted_pending_line)
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.lineage_view import line_text
from app.modules.t3_audit_engine import view_change_notice
from app.tests.test_audit_view import RECIPE_ID, World
from utils.lineage_data import lineage_of


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    clear_data_analysis_recipe_cache()
    made = World(tmp_path_factory.mktemp("audit_shown"))
    made.lineage = lineage_of(made.loaded.raw, made.plans)
    yield made
    clear_data_analysis_recipe_cache()


# -- request_to_show -----------------------------------------------------------------------------------------------
def test_show_selection_shows_the_first_place_clicked_and_show_shows_the_one_pressed(world):
    chosen = ["T1:MLST", "T1:ResFinder"]
    assert request_to_show(None, chosen, world.graph, world.lineage).place == "T1:MLST", "'Show selection' shows the first clicked"
    assert request_to_show("T1:ResFinder", chosen, world.graph, world.lineage).place == "T1:ResFinder", "'Show' on a line shows that line"
    assert request_to_show("T3:amr_heatmap", [], world.graph, world.lineage).place == "T3:amr_heatmap", "a plot node can be shown"


def test_nothing_chosen_shows_nothing_and_says_what_to_do(world):
    outcome = request_to_show(None, [], world.graph, world.lineage)
    assert outcome.place is None and outcome.problem == CHOOSE_FIRST


@pytest.mark.parametrize("bad", ["T1:NoSuchTable", "", "garbage"])
def test_a_place_that_is_not_a_place_of_this_recipe_is_a_plain_sentence_not_another_table(world, bad):
    outcome = request_to_show(bad or None, [bad] if bad else [], world.graph, world.lineage)
    assert outcome.place is None and outcome.problem, "a stale id never raises and never shows another place"
    if bad == "T1:NoSuchTable":
        assert "not a place of this recipe" in outcome.problem


def test_the_metadata_and_an_empty_tier_two_cannot_be_shown_as_places(world):
    metadata = world.lineage.metadata_table
    if metadata:
        assert request_to_show(f"T1:{metadata}", [], world.graph, world.lineage).place is None, "the metadata is not a place (D-0632)"
    no_t2 = [n for n in world.graph.nodes() if n.startswith("T1:") and not world.graph.has_node("T2:" + n[3:])]
    if no_t2:
        outcome = request_to_show("T2:" + no_t2[0][3:], [], world.graph, world.lineage)
        assert outcome.place is None and outcome.problem


# -- the counts and the band ---------------------------------------------------------------------------------------
def test_others_chosen_counts_the_chosen_places_that_are_not_shown_and_each_once():
    assert others_chosen([], "T1:a") == 0
    assert others_chosen(["T1:a"], "T1:a") == 0
    assert others_chosen(["T1:a", "T1:b", "T1:c"], "T1:a") == 2
    assert others_chosen(["T1:a", "T1:b", "T1:b"], "T1:a") == 1, "a place named twice is one place"
    assert others_chosen(["T1:b"], "T1:a") == 1 and others_chosen(["T1:b"], None) == 1


def facts(**kw):
    base = dict(mode=AUDIT, tier="T1", table="ResFinder", place="T1:ResFinder", state=ORIGINAL, why_original="", no_plot_reads=False)
    base.update(kw)
    return TableFacts(**base)


def test_the_band_names_the_place_with_the_lineage_words_and_says_original_or_audited(world):
    node = world.lineage.node("T1:ResFinder")
    original = band_lines(line_text(node), facts(why_original="No audit step has been added yet, so this is the original table."))
    assert original[0] == f"Shown: {line_text(node)}. Original (as read)" and original[1].startswith("No audit step"), original
    audited = band_lines(line_text(node), facts(state=AUDITED))
    assert audited == (f"Shown: {line_text(node)}. Audited: your applied steps",)


def test_the_band_says_how_many_other_places_are_chosen_the_open_plot_and_a_restored_session():
    lines = band_lines("X: Table, T1", facts(), others=2)
    assert lines[-1] == "2 other places chosen, not shown." and band_lines("X", facts(), others=1)[-1] == "1 other place chosen, not shown."
    lines = band_lines("X: Table, T1", facts(), from_open_plot=False)
    assert "does not change the open figure" in lines[-1]
    lines = band_lines("X: Table, T1", facts(no_plot_reads=True), from_open_plot=False)
    assert "No plot reads this table." in lines and not any("open figure" in line for line in lines), "a table no plot reads says so, once"
    restored = band_lines("X", facts(), restored_steps=3)
    assert restored[0] == "Restored session: 3 audit steps are applied." and band_lines("X", facts(), restored_steps=1)[0] == "Restored session: 1 audit step is applied."
    assert not any("Restored" in line for line in band_lines("X", facts(), restored_steps=0))


def test_the_band_of_a_view_with_nothing_to_show_gives_the_note_and_still_counts_the_others():
    empty = TableFacts(AUDIT, "", None, None, ORIGINAL, "Choose a place in Path of the data to see a table.", False)
    assert band_lines("", empty, others=1) == ("Choose a place in Path of the data to see a table.", "1 other place chosen, not shown.")


# -- a selection that is not the table shown -----------------------------------------------------------------------
def test_a_selection_without_the_place_shown_is_refused_with_show_your_selection_first():
    assert selection_problem([], "T3:p") is None, "nothing chosen: the place is the item shown (BEHAVIOUR.md)"
    assert selection_problem(["T1:a"], "T1:a") is None
    assert selection_problem(["T1:a", "T1:b"], "T1:b") is None
    assert selection_problem(["T1:b"], "T1:a") == SHOW_SELECTION_FIRST
    assert selection_problem(["T1:b"], None) == SHOW_SELECTION_FIRST, "nothing shown yet is not the chosen place"
    assert "Show your selection first" in SHOW_SELECTION_FIRST


# -- slice 3b: no plot tabs in Audit mode, the plot shown is the open plot -----------------------------------------------
def audit_view(world, shown_place, default_plot="amr_heatmap"):
    """What the screen reads in Audit mode, as `home_theater._audit_viewed` builds it: the open plot of the reader is the plot shown, none while a table is shown, the default plot with nothing shown."""
    candidate = default_plot
    if shown_place and world.graph.has_node(shown_place):
        node = world.graph.node(shown_place)
        candidate = node.name if node.kind == "T3" else None
    return viewed(AUDIT, "T3", None, candidate, [shown_place] if shown_place else [], world.graph, world.lineage)


def test_the_open_plot_of_audit_mode_is_the_plot_shown_not_the_tab_of_exploration(world):
    assert open_subtab_of(audit_view(world, "T3:mlst_bar", default_plot="amr_heatmap")) == "subtab_mlst_bar", "the plot shown, whatever tab Exploration had"
    assert open_subtab_of(audit_view(world, None, default_plot="amr_heatmap")) == "subtab_amr_heatmap", "nothing shown: the default plot (the tab of Exploration)"
    assert open_subtab_of(audit_view(world, "T3:amr_heatmap")) == "subtab_amr_heatmap"


def test_while_a_table_is_shown_no_plot_is_open(world):
    for place in ("T1:ResFinder", "T1:Quality_metrics"):
        shown = audit_view(world, place)
        assert shown.shown_plot is None and shown.from_open_plot is None and shown.place == place
        assert open_subtab_of(shown) == "", "no plot is open: nothing may write a step at the plot the tab had"


def test_no_plot_is_open_when_nothing_can_be_shown(world):
    assert open_subtab_of(None) == ""
    nothing = viewed(AUDIT, "T3", None, None, [], world.graph, world.lineage)
    assert nothing.nothing_chosen and open_subtab_of(nothing) == ""


def test_the_open_plot_does_not_depend_on_which_tab_exploration_had_when_a_plot_is_shown(world):
    other = audit_view(world, "T3:mlst_bar", default_plot="mlst_bar")
    assert open_subtab_of(audit_view(world, "T3:mlst_bar", default_plot="amr_heatmap")) == open_subtab_of(other)


def test_the_words_of_the_plot_area(world):
    assert plot_area_title("AMR Heatmap") == "Plot shown: AMR Heatmap"
    lines = table_shown_lines("ResFinder: Table, T1", ["AMR Heatmap", "MLST"])
    assert lines[0].startswith("No figure: ResFinder: Table, T1 is a table")
    assert "2 plots are built from it: AMR Heatmap, MLST." in lines and lines[-1].startswith("To see a figure")
    one = table_shown_lines("X", ["P"])
    assert "1 plot is built from it: P." in one
    none = table_shown_lines("Quality: Table, T1", [])
    assert any("No plot is built from it." in line for line in none) and not any("built from it:" in line for line in none)


def test_the_plots_named_in_the_note_of_a_table_are_the_plots_built_from_it(world):
    below = plots_below(world.graph, ["T1:ResFinder"])
    assert "amr_heatmap" in below
    assert plots_below(world.graph, ["T1:Quality_metrics"]) == [], "a table no plot reads names no plot"


def test_the_right_panel_lists_the_steps_written_at_the_table_shown_or_above_it(world):
    here = {"id": "a", "place": "T1:ResFinder"}
    above = None
    for node in world.graph.lineage_back("T2:ResFinder") if world.graph.has_node("T2:ResFinder") else []:
        if world.graph.node(node).kind == "T1":
            above = {"id": "b", "place": node}
    below = {"id": "c", "place": "T3:amr_heatmap"}
    beside = {"id": "d", "place": "T1:MLST"}
    listed = nodes_reaching_node(world.graph, [here, below, beside], "T1:ResFinder")
    assert [n["id"] for n in listed] == ["a"], "a step at the table itself; a step below it (the plot) or beside it is not on its path"
    assert [n["id"] for n in nodes_reaching_node(world.graph, [here, below, beside], "T3:amr_heatmap")] == ["a", "c"], "the plot is built from the table"


def test_table_shown_in_panel_reads_only_table_nodes():
    assert table_shown_in_panel("T1:ResFinder") == "T1:ResFinder" and table_shown_in_panel("T2:x") == "T2:x"
    assert table_shown_in_panel("T3:amr_heatmap") == "" and table_shown_in_panel(None) == "" and table_shown_in_panel("") == ""


def test_pending_steps_the_right_panel_does_not_list_are_told_not_dropped_silently():
    assert unlisted_pending_line(0, 0) == "" and unlisted_pending_line(2, 2) == ""
    one = unlisted_pending_line(1, 0)
    assert "1 pending step is written elsewhere and not listed here" in one and "Apply needs a reason for every step" in one
    assert unlisted_pending_line(3, 1).startswith("2 pending steps are written elsewhere")


# -- the condition belongs to the table shown (key + notice) -------------------------------------------------------
def audit_key(world, place, columns=None, own=False):
    shown = viewed(AUDIT, "T3", None, "amr_heatmap", [place] if place else [], world.graph, world.lineage)
    return view_identity(shown, RECIPE_ID, own, columns)


COLS = [("sample_id", "String"), ("identity", "Float64")]


def test_showing_the_same_table_again_clears_nothing_and_showing_another_table_clears_with_a_notice(world):
    here = audit_key(world, "T1:ResFinder", COLS)
    assert view_change_notice(here, audit_key(world, "T1:ResFinder", COLS), 1, 0) is None, "the same table shown again: nothing is cleared, no notice"
    other = audit_key(world, "T1:MLST", COLS)
    text = view_change_notice(here, other, 1, 0)
    assert text and "condition you were building was removed" in text and "you showed another table" in text, text
    assert view_change_notice(here, other, 0, 0) is None, "nothing staged: no notice for nothing"


def test_two_plots_that_read_one_table_keep_a_staged_condition(world):
    one = view_identity(viewed(AUDIT, "T3", None, "amr_heatmap", [], world.graph, world.lineage), RECIPE_ID, False, COLS)
    same = view_identity(viewed(AUDIT, "T3", None, "amr_heatmap", ["T3:amr_heatmap"], world.graph, world.lineage), RECIPE_ID, False, COLS)
    assert one == same, "showing the open plot's own place when it is already the default changes nothing (D-0505, D-0506)"


def test_a_column_drop_while_a_condition_is_staged_clears_it_with_its_own_cause(world):
    before = audit_key(world, "T1:ResFinder", COLS)
    after = audit_key(world, "T1:ResFinder", COLS[:1])
    text = view_change_notice(before, after, 1, 0)
    assert text and "columns of the table shown changed" in text, text
    assert view_change_notice(before, audit_key(world, "T1:ResFinder", list(reversed(COLS))), 1, 0) is None, "the order of the columns alone changes nothing"


def test_a_switch_between_the_modes_names_the_mode_even_when_one_key_has_no_digest(world):
    exploration = view_identity(viewed("exploration", "T3", None, "amr_heatmap", [], world.graph, world.lineage), RECIPE_ID)
    audit = audit_key(world, None, COLS)
    assert len(exploration) != len(audit), "the Audit key carries the digest of the columns, the Exploration key does not"
    assert "switched to Audit mode" in view_change_notice(exploration, audit, 1, 0)
    assert "switched to Exploration mode" in view_change_notice(audit, exploration, 1, 0)
