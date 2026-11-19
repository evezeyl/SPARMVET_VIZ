"""The column, the operator and the value the user has chosen in the Filters form survive a recompute of the table (D-0050).

The defect (found 2026-11-19, "FORM RESET"): the add-row form read the table of the open plot directly. A shiny Calc invalidates its
readers every time it recomputes, even when the result is the same, so a change of "Data to show" mounted the column select again.
A render that had started before the server received the user's new column put the first column back, and nothing told the user.
The form now depends on two signals that change only when what they stand for changes (`filter_and_audit_handlers._signal_dialog_table`).

Headless: the two signatures (`dialog_schema_signature`, `dialog_rows_signature`) and the reactive pattern. Browser (qa app features):
the real form, the real race, and the edge cases (the column is gone, a real change of columns, a number column on a discrete axis).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filter_form_survives_rerender.py -q
"""
import asyncio

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny import reactive
from shiny.run import ShinyAppProc

from app.modules.t3_audit_engine import column_types, dialog_rows_signature, dialog_schema_signature
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_filter_types import typed_app  # noqa: F401 - a recipe of one table with an integer year on a discrete axis
from app.tests.test_shiny_smoke import (_load_data_analysis_recipe, _navigate_to_mlst_plot, _open_filters_panel, _wait_for_fb_col_option,
                                        _wait_shiny)


# ---- headless: the signatures -------------------------------------------------------------------------------------------------

TYPES = {"sample_id": pl.String, "year": pl.Float64}


class TestSchemaSignature:
    def test_the_same_columns_and_types_are_equal_whatever_the_rows(self):
        assert dialog_schema_signature(TYPES, set()) == dialog_schema_signature(dict(TYPES), set())

    def test_a_column_added_or_removed_changes_it(self):
        assert dialog_schema_signature({**TYPES, "era": pl.String}, set()) != dialog_schema_signature(TYPES, set())
        assert dialog_schema_signature({"sample_id": pl.String}, set()) != dialog_schema_signature(TYPES, set())

    def test_a_type_change_with_the_same_names_changes_it(self):
        assert dialog_schema_signature({"sample_id": pl.String, "year": pl.Int64}, set()) != dialog_schema_signature(TYPES, set())

    def test_the_order_of_the_columns_changes_it(self):
        assert dialog_schema_signature(dict(reversed(list(TYPES.items()))), set()) != dialog_schema_signature(TYPES, set())

    def test_a_discrete_axis_changes_it(self):
        """A number column on a discrete axis is offered other operators: the form must be built again."""
        assert dialog_schema_signature(TYPES, {"year"}) != dialog_schema_signature(TYPES, set())

    def test_no_table_is_a_signature_of_its_own(self):
        assert dialog_schema_signature({}, set()) == ((), ())
        assert dialog_schema_signature({}, set()) != dialog_schema_signature(TYPES, set())


class TestRowsSignature:
    def _write(self, path, rows):
        pl.DataFrame({"sample_id": [r[0] for r in rows], "year": [r[1] for r in rows]}).write_parquet(path)
        return pl.scan_parquet(path)

    def test_the_same_table_read_again_is_equal(self, tmp_path):
        self._write(tmp_path / "a.parquet", [("s1", 2020.0)])
        one = dialog_rows_signature(pl.scan_parquet(tmp_path / "a.parquet"), "key1")
        two = dialog_rows_signature(pl.scan_parquet(tmp_path / "a.parquet"), "key1")
        assert one == two

    def test_another_stored_table_with_the_same_columns_is_not_equal(self, tmp_path):
        """Same columns, other rows (the T1 table and the T2 table of a join, another plot's dataset)."""
        a = self._write(tmp_path / "a.parquet", [("s1", 2020.0)])
        b = self._write(tmp_path / "b.parquet", [("s2", 2021.0), ("s3", 2022.0)])
        assert dialog_schema_signature(column_types(a), set()) == dialog_schema_signature(column_types(b), set())   # the form would be the same
        assert dialog_rows_signature(a, "key1") != dialog_rows_signature(b, "key1")

    def test_the_same_path_with_another_content_key_is_not_equal(self, tmp_path):
        """The stored table is rewritten under the same path when the data or the recipe change (ADR-089): the key tells."""
        a = self._write(tmp_path / "a.parquet", [("s1", 2020.0)])
        assert dialog_rows_signature(a, "key1") != dialog_rows_signature(a, "key2")

    def test_an_audited_step_changes_the_table_and_the_signature(self, tmp_path):
        """The dialog in My view acts on the table after the audited steps (a filter keeps fewer rows)."""
        a = self._write(tmp_path / "a.parquet", [("s1", 2020.0), ("s2", 2021.0)])
        assert dialog_rows_signature(a, "k") != dialog_rows_signature(a.filter(pl.col("year") > 2020), "k")

    def test_no_table(self):
        assert dialog_rows_signature(None, "k") == (None, "k")

    def test_a_plan_that_cannot_be_read_is_never_equal_to_another(self):
        """A doubt means one more render, never a stale list of values."""
        class Broken:
            def explain(self, **_):
                raise RuntimeError("no plan")
        assert dialog_rows_signature(Broken(), "k") != dialog_rows_signature(Broken(), "k")


# ---- headless: the reactive pattern -------------------------------------------------------------------------------------------

def _renders(pattern: str, recompute_with: list) -> int:
    """How many times an output that stands for the form renders when the table is recomputed with `recompute_with` (a list of
    `(types, rows_key)`). The handler is a closure and cannot be imported: the two patterns are built here with the real
    `reactive` objects and the real signatures, as `test_dialog_mirror_window.py` does."""
    async def main():
        runs = []
        trigger = reactive.Value(0)
        tables = [({"sample_id": pl.String, "year": pl.Float64}, "k1")]

        @reactive.Calc
        def table():
            trigger.get()
            return tables[-1]

        signal = reactive.Value(None)

        @reactive.Effect
        def signal_effect():
            types, _key = table()
            new = dialog_schema_signature(types, set())
            with reactive.isolate():
                if signal.get() != new:
                    signal.set(new)

        @reactive.Effect
        def form():
            if pattern == "reads the table":
                table()
            else:
                signal.get()
                with reactive.isolate():
                    table()
            runs.append(1)

        await reactive.flush()
        runs.clear()
        for item in recompute_with:
            tables.append(item)
            trigger.set(len(tables))
            await reactive.flush()
        return len(runs)
    return asyncio.run(main())


SAME = ({"sample_id": pl.String, "year": pl.Float64}, "k1")
OTHER_ROWS = ({"sample_id": pl.String, "year": pl.Float64}, "k2")
NEW_COLUMN = ({"sample_id": pl.String, "year": pl.Float64, "era": pl.String}, "k1")
LESS_COLUMN = ({"sample_id": pl.String}, "k1")


def test_a_form_that_reads_the_table_renders_on_every_recompute_even_when_nothing_changed():
    assert _renders("reads the table", [SAME, OTHER_ROWS]) == 2, "the defect was not reproduced"


def test_a_form_on_the_signal_does_not_render_when_the_columns_and_types_are_the_same():
    assert _renders("signal", [SAME, OTHER_ROWS, SAME]) == 0


def test_a_form_on_the_signal_renders_once_when_a_column_is_added_and_once_when_it_goes():
    assert _renders("signal", [NEW_COLUMN]) == 1
    assert _renders("signal", [NEW_COLUMN, LESS_COLUMN]) == 2


# ---- browser ------------------------------------------------------------------------------------------------------------------

_COUNT_RENDERS = """() => { if (!window.__fr) { window.__fr = {}; $(document).on('shiny:value', e => { window.__fr[e.name] = (window.__fr[e.name] || 0) + 1; }); } }"""


def _renders_of(page: Page, name: str) -> int:
    return page.evaluate("(n) => (window.__fr || {})[n] || 0", name)


def _show(page: Page, tier: str) -> None:
    page.locator(f"#tier_toggle input[value={tier}]").check(force=True)
    _wait_shiny(page, 30_000)


def _ready_on_mlst(page: Page, base_url: str) -> None:
    """The MLST Bar plot of the 1_test_data_ST22_dummy recipe (`year` is a number column), Result view, form open."""
    _load_data_analysis_recipe(page, base_url)
    _open_filters_panel(page)
    _navigate_to_mlst_plot(page)
    _wait_for_fb_col_option(page, "year")
    _show(page, "T2")
    _wait_for_fb_col_option(page, "era")   # the T2 table has the `era` column, the T1 table has not (a real change of columns)
    page.evaluate(_COUNT_RENDERS)


def _choose(page: Page, column: str) -> None:
    """Choose the column and check the form holds it (its own text under the tick names it)."""
    page.locator("#fb_col").select_option(column)
    _wait_shiny(page)
    expect(page.locator("#fb_col")).to_have_value(column)
    expect(page.locator("#filter_na_text_ui")).to_contain_text(" " + column, timeout=10_000)


def _pick_first_value(page: Page) -> str:
    page.wait_for_function(
        "() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 0; }",
        timeout=10_000)
    value = page.evaluate("() => { const s = document.getElementById('fb_value').selectize; const v = Object.keys(s.options)[0]; s.addItem(v); return v; }")
    page.wait_for_function("(v) => document.getElementById('fb_value').selectize.items.includes(v)", arg=value, timeout=5_000)
    _wait_shiny(page)
    return value


class TestFormInTheBrowser:
    def test_a_change_of_view_without_new_columns_keeps_column_operator_and_value_and_mounts_nothing(self, page: Page, shiny_app: ShinyAppProc):
        """Result and My view hold the same columns: the form is not mounted again, so what was chosen is still there."""
        _ready_on_mlst(page, shiny_app.url)
        _choose(page, "source")
        page.wait_for_function("() => Array.from(document.querySelectorAll('#fb_op option')).some(o => o.value === 'not_in')", timeout=15_000)
        page.locator("#fb_op").select_option("not_in")
        _wait_shiny(page)
        value = _pick_first_value(page)
        page.evaluate("() => { window.__fbCol = document.getElementById('fb_col'); window.__fbValue = document.getElementById('fb_value'); }")
        before = {n: _renders_of(page, n) for n in ("filter_form_ui", "filter_op_ui", "filter_value_ui")}
        for tier in ("T3", "T2", "T3", "T2"):
            _show(page, tier)
        assert page.evaluate("() => window.__fbCol === document.getElementById('fb_col')"), "the column select was mounted again"
        assert page.evaluate("() => window.__fbValue === document.getElementById('fb_value')"), "the value box was mounted again"
        after = {n: _renders_of(page, n) for n in before}
        assert after == before, f"the form rendered again with the same columns: {before} -> {after}"
        expect(page.locator("#fb_col")).to_have_value("source")
        expect(page.locator("#fb_op")).to_have_value("not_in")
        assert page.evaluate("(v) => document.getElementById('fb_value').selectize.items.includes(v)", value), "the value the user picked is gone"

    def test_the_column_chosen_right_after_a_change_of_view_is_not_put_back(self, page: Page, shiny_app: ShinyAppProc):
        """The race of the defect, as a user makes it: change "Data to show", then choose a column a few milliseconds later. The server
        used to render the form with the old column while the new one was on its way (9 of 30 tries before the fix)."""
        _ready_on_mlst(page, shiny_app.url)
        delays = [0, 5, 10, 20, 40, 0, 10, 20]
        for i, delay in enumerate(delays * 2):
            target = ("year", "sample_id")[i % 2]
            _show_start = ("T3", "T2")[i % 2]
            page.locator(f"#tier_toggle input[value={_show_start}]").check(force=True)
            if delay:
                page.wait_for_timeout(delay)   # the user's own delay between the two clicks, the thing under test
            page.locator("#fb_col").select_option(target)
            _wait_shiny(page, 30_000)
            expect(page.locator("#fb_col")).to_have_value(target)
            expect(page.locator("#filter_na_text_ui")).to_contain_text(" " + target, timeout=10_000)

    def test_a_column_that_is_not_in_the_other_table_falls_back_to_the_first_column(self, page: Page, shiny_app: ShinyAppProc):
        """A different table: falling back is right (the choice cannot be kept). The form is mounted again for it."""
        _ready_on_mlst(page, shiny_app.url)
        _choose(page, "year")
        before = _renders_of(page, "filter_form_ui")
        page.locator(".nav-link:has-text('AMR Heatmap')").first.click()   # a plot of the same group that reads a table without `year`
        _wait_shiny(page, 30_000)
        page.wait_for_function("() => !Array.from(document.querySelectorAll('#fb_col option')).some(o => o.value === 'year')", timeout=30_000)
        _wait_shiny(page)
        assert _renders_of(page, "filter_form_ui") > before, "the form was not built again for the other table"
        first = page.evaluate("() => document.querySelector('#fb_col option').value")
        expect(page.locator("#fb_col")).to_have_value(first)

    def test_a_real_change_of_columns_builds_the_form_again_and_keeps_the_column_that_is_still_there(self, page: Page, shiny_app: ShinyAppProc):
        """Raw (T1) has no `era` column, Result (T2) has: the columns really change. `year` is in both: it stays chosen."""
        _ready_on_mlst(page, shiny_app.url)
        _choose(page, "year")
        before = _renders_of(page, "filter_form_ui")
        _show(page, "T1")
        page.wait_for_function("() => !Array.from(document.querySelectorAll('#fb_col option')).some(o => o.value === 'era')", timeout=15_000)
        assert _renders_of(page, "filter_form_ui") > before, "the columns changed and the form was not built again"
        expect(page.locator("#fb_col")).to_have_value("year")
        _show(page, "T2")
        _wait_for_fb_col_option(page, "era")
        expect(page.locator("#fb_col")).to_have_value("year")


class TestNumberColumnOnADiscreteAxis:
    """`year` of the `typed_app` table is a whole number that the plot uses as a discrete axis: its operator list holds the list
    operators AND the comparisons, and its value widget is a list or a number box by the operator."""

    def test_operator_and_value_of_a_discrete_year_survive_a_change_of_view(self, page: Page, typed_app):
        page.goto(typed_app)
        page.wait_for_selector("#data_analysis_recipe_id", timeout=20_000)
        _wait_shiny(page, 60_000)
        page.locator(".nav-link:has-text('Years')").first.click()
        _wait_shiny(page)
        _open_filters_panel(page)
        _wait_for_fb_col_option(page, "year")
        _choose(page, "year")
        page.evaluate(_COUNT_RENDERS)
        ops = page.locator("#fb_op option").evaluate_all("els => els.map(e => e.value)")
        assert ops == ["in", "not_in", "eq", "ne", "gt", "ge", "lt", "le", "between"], "the discrete year offers the list and the comparisons"
        page.locator("#fb_op").select_option("in")
        _wait_shiny(page)
        value = _pick_first_value(page)
        before = _renders_of(page, "filter_form_ui") + _renders_of(page, "filter_op_ui") + _renders_of(page, "filter_value_ui")
        for tier in ("T3", "T2"):
            _show(page, tier)
        after = _renders_of(page, "filter_form_ui") + _renders_of(page, "filter_op_ui") + _renders_of(page, "filter_value_ui")
        assert after == before, "the discrete year was mounted again with the same columns"
        expect(page.locator("#fb_op")).to_have_value("in")
        assert page.evaluate("(v) => document.getElementById('fb_value').selectize.items.includes(v)", value)
        # a comparison uses the number box; the number typed in it is kept through the same change of view
        page.locator("#fb_op").select_option("gt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("1999")
        page.locator("#fb_value").press("Tab")
        _wait_shiny(page)
        for tier in ("T3", "T2"):
            _show(page, tier)
        expect(page.locator("#fb_op")).to_have_value("gt")
        expect(page.locator("#fb_value")).to_have_value("1999")
