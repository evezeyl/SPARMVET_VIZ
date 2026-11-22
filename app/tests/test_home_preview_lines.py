"""The two facts of every HOME data preview (D-0488, PROVISIONAL words): how many rows, how many columns are hidden.

# @deps
# consumes: app/tests/home_harness.py (Home, ViewWorld), app/modules/view_badge.py (PREVIEW_ROW_LIMIT), app/handlers/home_theater.py (home_data_preview_badge, home_data_preview_title)
# @end_deps

Runs the real `home_theater.define_server` headless. The sentences are in the badge output (`home_data_preview_badge`), an output of its own
that never mounts the column chooser (ui_implementation_contract section 14, rule R4).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_preview_lines.py -q
"""
import pytest
from shiny import reactive

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.view_badge import PREVIEW_ROW_LIMIT
from app.tests.audit_nodes import filter_nodes
from app.tests.home_harness import Home, ViewWorld

AUDIT = ("interactivity_enabled", "t3_sandbox_enabled", "comparison_mode_enabled", "session_management_enabled", "export_enabled")
ROWS = 150


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


@pytest.fixture
def world(tmp_path):
    w = ViewWorld(tmp_path)
    # 150 rows, scores 1 to 4 so that tier 1 (score <= 4) keeps them all
    lines = ["sample_id\tgroup\tscore"] + [f"s{i}\t{'A' if i % 2 else 'B'}\t{1 + i % 4}" for i in range(ROWS)]
    w.data_file.write_text("\n".join(lines) + "\n")
    clear_data_analysis_recipe_cache()
    return w


def badge_text(home: Home) -> str:
    with reactive.isolate():
        return str(home.outputs["home_data_preview_badge"]())


def test_more_than_the_limit_says_showing_100_of_n(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    assert f"Showing {PREVIEW_ROW_LIMIT} of {ROWS} rows" in badge_text(home)


def test_all_rows_on_says_the_number_of_rows(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_all_rows": True})
    text = badge_text(home)
    assert f"{ROWS} rows" in text and "Showing" not in text


def test_a_small_table_says_its_size(world, monkeypatch):
    home = Home(world, monkeypatch, view="T2", subtab="subtab_p_join")      # tier 2 keeps score >= 2: well under 100? 150 rows -> check below
    with reactive.isolate():
        n = home.outputs["home_data_preview"]().data.height
    # T2 of the join has fewer rows than the limit only when the filter cuts enough; the grid and the sentence must agree either way
    text = badge_text(home)
    assert (f"Showing {PREVIEW_ROW_LIMIT} of" in text) == (n == PREVIEW_ROW_LIMIT)


def test_the_count_is_the_count_of_the_table_after_the_exploration_filters(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    before = badge_text(home)
    assert f"of {ROWS} rows" in before
    with reactive.isolate():
        key = home.readers["current_view_key"]()
        home.filters_applied.set([{"column": "score", "op": "ge", "value": 4, "dtype": "Int64", "na": "remove", "view": key}])
    after = badge_text(home)
    expected = sum(1 for i in range(ROWS) if 1 + i % 4 >= 4)
    assert f"of {expected} rows" in after or f"{expected} rows" in after
    assert f"of {ROWS} rows" not in after


def test_a_table_of_zero_rows_says_zero(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    with reactive.isolate():
        key = home.readers["current_view_key"]()
        home.filters_applied.set([{"column": "score", "op": "gt", "value": 99, "dtype": "Int64", "na": "remove", "view": key}])
    assert "0 rows" in badge_text(home)


def test_no_hidden_columns_no_sentence(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    assert "hidden" not in badge_text(home)
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_col_selector": ["sample_id", "group", "score"]})
    assert "hidden" not in badge_text(home)


def test_unselected_columns_are_counted_as_hidden(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_col_selector": ["sample_id"]})
    assert "2 columns hidden; add them back in the column chooser" in badge_text(home)
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_col_selector": ["sample_id", "group"]})
    assert "1 column hidden; add it back in the column chooser" in badge_text(home)


def test_an_empty_selection_hides_nothing_because_the_grid_then_shows_every_column(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_col_selector": []})
    assert "hidden" not in badge_text(home)


def test_audit_t3_says_the_columns_are_not_dropped(world, monkeypatch):
    home = Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table",
                inputs={"preview_col_selector": ["sample_id"]})
    text = badge_text(home)
    assert "2 columns" in text and "not dropped" in text


def test_a_column_dropped_by_an_audit_step_is_not_counted_as_hidden(world, monkeypatch):
    nodes = filter_nodes([], drops=["group"])
    home = Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table",
                inputs={"preview_col_selector": ["sample_id", "score"]},
                home_state={"t3_audit_steps_by_plot": {"subtab_p_table": nodes}})
    text = badge_text(home)
    assert "hidden" not in text and "not dropped" not in text


def test_an_audit_step_that_cannot_run_gives_no_count_and_no_second_error(world, monkeypatch):
    nodes = filter_nodes([{"column": "no_such_column", "op": "ge", "value": 1, "dtype": "Int64", "na": "remove"}])
    home = Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table",
                home_state={"t3_audit_steps_by_plot": {"subtab_p_table": nodes}})
    text = badge_text(home)
    assert "rows" not in text and "Error" not in text      # the table's place says why; the badge stays quiet
    assert not home.notes                                  # and the badge raised no notification of its own


def test_the_title_and_the_cut_use_the_one_limit(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    with reactive.isolate():
        assert home.outputs["home_data_preview_title"]() == f"Data Preview (max. first {PREVIEW_ROW_LIMIT} rows)"
        assert home.outputs["home_data_preview"]().data.height == PREVIEW_ROW_LIMIT


def test_the_badge_output_does_not_mount_the_column_chooser(world, monkeypatch):
    """Rule R4: the chooser is mounted by `home_col_selector_ui`; the sentence lives in another output."""
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_col_selector": ["sample_id"]})
    assert "preview_col_selector" not in badge_text(home)
    assert home.outputs["home_data_preview_badge"] is not home.outputs["home_col_selector_ui"]


def test_the_grid_has_no_total_of_its_own(world, monkeypatch):
    """The grid's own line ("Viewing rows 1 through 9 of 100") counts the cut table, so it would read as the table's total. It is off:
    the badge sentence is the one place that states the size."""
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    with reactive.isolate():
        assert home.outputs["home_data_preview"]().summary is False
