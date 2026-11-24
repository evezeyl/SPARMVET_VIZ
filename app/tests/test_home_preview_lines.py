"""The two facts of every HOME data preview (D-0488, PROVISIONAL words): how many rows, how many columns are hidden.

# @deps
# consumes: app/tests/home_harness.py (Home, ViewWorld), app/modules/view_badge.py (PREVIEW_ROW_LIMIT), app/handlers/home_theater.py (home_data_preview_badge, home_data_preview_title)
# @end_deps

Runs the real `home_theater.define_server` headless. The sentences are in the badge output (`home_data_preview_badge`), an output of its own
that never mounts the column chooser (ui_implementation_contract section 14, rule R4).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_preview_lines.py -q
"""
import re

import pytest
from shiny import reactive

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.view_badge import PREVIEW_ROW_LIMIT
from app.tests.audit_nodes import audit_state, filter_nodes
from app.tests.home_harness import Home, ViewWorld

AUDIT = ("interactivity_enabled", "t3_sandbox_enabled", "comparison_mode_enabled", "session_management_enabled", "export_enabled")
ROWS = 150
MARKER = "T_not_in_original_data"   # the marker column of the completion of the ids: a normal column of the table from tier 1 on


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


def chooser_key(home: Home) -> str:
    """The key the column chooser emits with itself (the table it was built for), read from the rendered chooser."""
    with reactive.isolate():
        html = str(home.outputs["home_col_selector_ui"]())
    hit = re.search(r'id="preview_col_selector_key"[^>]*value="([^"]*)"', html) or re.search(r'value="([^"]*)"[^>]*id="preview_col_selector_key"', html)
    assert hit, "the chooser must carry the key of its table"
    return hit.group(1)


def choose(home: Home, names, key=None) -> Home:
    """Give the chooser's value as the browser would send it: the names, with the key of the table it was built for (this one unless given)."""
    home.inputs["preview_col_selector"] = names
    home.inputs["preview_col_selector_key"] = chooser_key(home) if key is None else key
    return home


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
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"), ["sample_id", "group", "score", MARKER])
    assert "hidden" not in badge_text(home)


def test_unselected_columns_are_counted_as_hidden(world, monkeypatch):
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"), ["sample_id"])
    assert "3 columns hidden; add them back in the column chooser" in badge_text(home)
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"), ["sample_id", "group", MARKER])
    assert "1 column hidden; add it back in the column chooser" in badge_text(home)


def test_an_empty_selection_hides_nothing_because_the_grid_then_shows_every_column(world, monkeypatch):
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"), [])
    assert "hidden" not in badge_text(home)


def test_audit_t3_says_the_columns_are_not_dropped(world, monkeypatch):
    home = choose(Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table"), ["sample_id"])
    text = badge_text(home)
    assert "3 columns" in text and "not dropped" in text


def test_a_column_dropped_by_an_audit_step_is_not_counted_as_hidden(world, monkeypatch):
    nodes = filter_nodes([], drops=["group"])
    home = choose(Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table",
                       home_state=audit_state("p_table", nodes)), ["sample_id", "score", MARKER])
    text = badge_text(home)
    assert "hidden" not in text and "not dropped" not in text


def test_an_audit_step_that_cannot_run_gives_no_count_and_no_second_error(world, monkeypatch):
    nodes = filter_nodes([{"column": "no_such_column", "op": "ge", "value": 1, "dtype": "Int64", "na": "remove"}])
    home = Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table",
                home_state=audit_state("p_table", nodes))
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
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"), ["sample_id"])
    assert "preview_col_selector" not in badge_text(home)
    assert home.outputs["home_data_preview_badge"] is not home.outputs["home_col_selector_ui"]


def test_the_grid_has_no_total_of_its_own(world, monkeypatch):
    """The grid's own line ("Viewing rows 1 through 9 of 100") counts the cut table, so it would read as the table's total. It is off:
    the badge sentence is the one place that states the size."""
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    with reactive.isolate():
        assert home.outputs["home_data_preview"]().summary is False


def test_a_chooser_built_for_another_table_gives_no_hidden_sentence_even_when_every_name_exists(world, monkeypatch):
    """Right after a switch of table or plot tab the chooser still belongs to the PREVIOUS table for a moment. Its names can all exist in the
    table now shown (Source to T1, T1 to T2), so the names cannot tell: the key of the table it was built for does. A different key: no
    hidden sentence (it would say that the user hid columns he did not hide, D-0050); the row sentence stays."""
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"), ["sample_id"], key="p_table|SRC|some_source|view|")
    text = badge_text(home)
    assert "hidden" not in text and "not dropped" not in text
    assert f"Showing {PREVIEW_ROW_LIMIT} of {ROWS} rows" in text
    # the same names with the key of this very table: counted
    assert "3 columns hidden" in badge_text(choose(home, ["sample_id"]))


def test_no_key_at_all_gives_no_hidden_sentence(world, monkeypatch):
    """Before the chooser has reported (or when it could not be built) nothing is said about hidden columns."""
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_col_selector": ["sample_id"]})
    assert "hidden" not in badge_text(home)


def test_the_key_names_the_view_so_that_a_switch_of_table_changes_it(world, monkeypatch):
    keys = {v: chooser_key(Home(world, monkeypatch, view=v, subtab="subtab_p_table")) for v in ("T1", "T2", "T3")}
    assert len(set(keys.values())) == 3


def test_a_real_selection_is_still_counted_once_every_name_is_a_column(world, monkeypatch):
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"), ["group", "score", MARKER])
    assert "1 column hidden; add it back in the column chooser" in badge_text(home)


def test_audit_t3_counts_the_audited_table_and_a_pending_step_changes_nothing(world, monkeypatch):
    applied = filter_nodes([{"column": "score", "op": "ge", "value": 4, "dtype": "Int64", "na": "remove"}])
    expected = sum(1 for i in range(ROWS) if 1 + i % 4 >= 4)
    assert 0 < expected < ROWS
    home = Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table",
                home_state=audit_state("p_table", applied))
    text = badge_text(home)
    assert f"{expected} rows" in text and f"of {ROWS} rows" not in text
    # a step that is only pending (not applied) does not change the table, so it does not change the count
    pending = filter_nodes([{"column": "score", "op": "ge", "value": 4, "dtype": "Int64", "na": "remove"}])
    home = Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table",
                home_state={"_pending_t3_nodes": pending})
    assert f"Showing {PREVIEW_ROW_LIMIT} of {ROWS} rows" in badge_text(home)


def test_the_badge_total_is_the_true_height_while_the_grid_holds_the_cut(world, monkeypatch):
    """For a table of more than 100 rows: the grid holds 100 rows and the sentence gives the table's real height; with "All rows" on the
    grid holds every row and the sentence says so."""
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    with reactive.isolate():
        assert home.outputs["home_data_preview"]().data.height == PREVIEW_ROW_LIMIT
    assert f"Showing {PREVIEW_ROW_LIMIT} of {ROWS} rows" in badge_text(home)
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_all_rows": True})
    with reactive.isolate():
        assert home.outputs["home_data_preview"]().data.height == ROWS
    text = badge_text(home)
    assert f"{ROWS} rows" in text and "Showing" not in text


def _grid_height(home: Home) -> int:
    with reactive.isolate():
        return home.outputs["home_data_preview"]().data.height


def _badge_count(home: Home) -> int:
    hit = re.search(r"(?:of )?(\d+) rows", badge_text(home))
    assert hit, badge_text(home)
    return int(hit.group(1))


def test_the_grid_and_the_badge_read_the_same_table_with_an_exploration_filter(world, monkeypatch):
    """With "All rows" on the grid holds every row of the table it reads; the badge must count that same table (the filter applies to both)."""
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"preview_all_rows": True})
    assert _grid_height(home) == ROWS
    with reactive.isolate():
        key = home.readers["current_view_key"]()
        home.filters_applied.set([{"column": "score", "op": "ge", "value": 3, "dtype": "Int64", "na": "remove", "view": key}])
    grid = _grid_height(home)
    assert 0 < grid < ROWS, "the filter must have cut rows, or this test proves nothing"
    assert _badge_count(home) == grid


def test_the_grid_and_the_badge_read_the_same_table_with_an_applied_audit_step(world, monkeypatch):
    applied = filter_nodes([{"column": "score", "op": "ge", "value": 4, "dtype": "Int64", "na": "remove"}])
    home = Home(world, monkeypatch, view="T3", mode="audit", flags=AUDIT, subtab="subtab_p_table", inputs={"preview_all_rows": True},
                home_state=audit_state("p_table", applied))
    grid = _grid_height(home)
    assert 0 < grid < ROWS
    assert _badge_count(home) == grid


def _second_recipe(world):
    """The same recipe under another id (and so another file set): what the user opens with a switch of recipe."""
    text = (world.data_analysis_recipes_dir / "tiny.yaml").read_text().replace("id: tiny\n", "id: tiny2\n", 1)
    (world.data_analysis_recipes_dir / "tiny2.yaml").write_text(text)
    clear_data_analysis_recipe_cache()


def test_the_key_changes_with_the_recipe(world, monkeypatch):
    _second_recipe(world)
    one = chooser_key(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"))
    two = chooser_key(Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"data_analysis_recipe_id": "tiny2"}))
    assert one != two


def test_a_chooser_built_for_another_recipe_gives_no_hidden_sentence_even_when_plot_and_view_are_equal(world, monkeypatch):
    """The third review: after a switch of recipe the old plot id is still the active one for a moment and the names all exist in the new
    table, so only the recipe part of the key can tell (D-0050)."""
    _second_recipe(world)
    old = chooser_key(Home(world, monkeypatch, view="T1", subtab="subtab_p_table"))
    home = choose(Home(world, monkeypatch, view="T1", subtab="subtab_p_table", inputs={"data_analysis_recipe_id": "tiny2"}), ["sample_id"], key=old)
    text = badge_text(home)
    assert "hidden" not in text and f"of {ROWS} rows" in text
    assert "3 columns hidden" in badge_text(choose(home, ["sample_id"]))     # built for this recipe: counted


def test_a_change_of_the_data_changes_the_key(world, monkeypatch):
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    before = chooser_key(home)
    world.data_file.write_text(world.data_file.read_text() + "sx\tA\t1\n")
    clear_data_analysis_recipe_cache()
    assert chooser_key(home) != before


def test_unreadable_recipe_keys_on_both_sides_give_no_hidden_sentence(world, monkeypatch):
    """A failed key never equals another key (D-0050): when the recipe part of the key cannot be read, the chooser carries no key and the
    badge says nothing about hidden columns, even when the browser sends back the empty key, or the text a failed key used to be written
    as, and a column is deselected. The rows are still counted (the table itself reads fine)."""
    home = Home(world, monkeypatch, view="T1", subtab="subtab_p_table")
    real = world.orch.compute_data_analysis_recipe_keys

    class Unreadable:
        def __init__(self, keys):
            self._keys = keys

        def __getattr__(self, name):
            if name == "data_analysis_recipe_sha256":
                raise RuntimeError("hash unreadable")
            return getattr(self._keys, name)

    monkeypatch.setattr(world.orch, "compute_data_analysis_recipe_keys", lambda *a, **k: Unreadable(real(*a, **k)))
    assert chooser_key(home) == ""
    for key in ("", None, "recipe-unreadable|p_table|T1||view|"):
        home.inputs["preview_col_selector"] = ["sample_id"]
        home.inputs["preview_col_selector_key"] = key
        text = badge_text(home)
        assert "hidden" not in text and f"of {ROWS} rows" in text
