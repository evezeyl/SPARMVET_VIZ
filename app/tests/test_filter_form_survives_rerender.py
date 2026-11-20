"""The column, the operator and the value the user has chosen in the Filters form survive a recompute of the table (D-0050).

The defect (found 2026-11-19, "FORM RESET"): the add-row form read the table of the open plot directly. A shiny Calc invalidates its
readers every time it recomputes, even when the result is the same, so a change of the data choice mounted the column select again.
A render that had started before the server received the user's new column put the first column back, and nothing told the user.
(Slice B: the choice that changed is now the data choice, Source, T1, T2 or T3, and the mode.)
The form now depends on two signals that change only when what they stand for changes (`filter_and_audit_handlers._signal_dialog_table`).

Headless: the two signatures (`dialog_schema_signature`; `dialog_rows_signature` with `stored_table_identity`: the audited steps in full and the
keys of the stored files, never the text of a Polars plan, which printed a long list of values truncated and the same for a rewritten file), the
reactive pattern, and the real handler's Effect defined with stand-ins (it does nothing without interactivity). Browser (qa app features):
the real form, the real race, and the edge cases (the column is gone, a real change of columns, a number column on a discrete axis).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filter_form_survives_rerender.py -q
"""
import asyncio
from types import SimpleNamespace
from unittest import mock

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny import reactive
from shiny.run import ShinyAppProc

import app.handlers.filter_and_audit_handlers as h
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, tier2_path_for
from app.modules.session_manager import make_audit_step
from app.modules.t3_audit_engine import (audited_frame, dialog_rows_signature, dialog_schema_signature, stored_key,
                                          stored_table_identity)
from app.tests.browser_view import set_view
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_filter_types import typed_app  # noqa: F401 - a recipe of one table with an integer year on a discrete axis
from app.tests.test_shiny_step_order import (N, THRESHOLD, _expect_rows, _filter_step, _start,  # noqa: F401 - a recipe of one table of 30 rows
                                             staged_app)
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


def _step(column, op, value, dtype="String", **extra):
    """An audit step as the app records it (`make_audit_step`)."""
    return make_audit_step("filter_row", {"column": column, "op": op, "value": value, "dtype": dtype, **extra}, plot_scope="subtab_p", reason="r")


def _old_plan_signature(lf, table_key):
    """The signature of the first fix, kept here only to show the defect it had (review of 2026-11-19, finding 1): the text of the
    Polars plan plus the tier-1 key. The tests below assert that it is EQUAL for tables whose rows differ."""
    return (lf.explain(optimized=False), table_key)


def _stored(folder, t1_key="k1", t2_key=None, rows=("a", "b", "c"), t2_rows=None):
    """A stored Tier 1 table (and a Tier 2 table next to it) with the content keys in the footers, as `write_anchor` writes them."""
    t1 = folder / "t.parquet"
    pl.DataFrame({"era": list(rows)}).write_parquet(t1, metadata={TIER1_KEY_META: t1_key})
    if t2_key is not None:
        pl.DataFrame({"era": list(t2_rows or rows)}).write_parquet(tier2_path_for(t1), metadata={TIER2_KEY_META: t2_key})
    return t1


def _identity(t1, tier="T2", unstored=0, view_key="vk"):
    return stored_table_identity(tier, "t", "recipe", view_key, t1, unstored)


def _rows_after(parquet, nodes):
    return sorted(audited_frame(pl.scan_parquet(parquet), nodes, "p").collect()["sample_id"].to_list())


class TestRowsSignatureOfTheAuditedSteps:
    """The rows of Audit T3 are decided by the audited steps in full. The first signature (the text of the Polars plan) printed a
    long list of values truncated, so two steps that differ in the middle, or in the length, looked equal (finding 1, case a)."""

    @pytest.fixture
    def table(self, tmp_path):
        path = tmp_path / "t.parquet"
        pl.DataFrame({"sample_id": [f"s{i}" for i in range(20)], "year": list(range(20))}).write_parquet(path, metadata={TIER1_KEY_META: "k1"})
        return path

    def _sig(self, table, nodes):
        return dialog_rows_signature(_identity(table), nodes)

    def test_the_same_steps_twice_are_equal(self, table):
        nodes = [_step("sample_id", "not_in", ["s0", "s1", "s2", "s3", "s4", "s5"])]
        copy = [dict(n, params=dict(n["params"])) for n in nodes]
        assert self._sig(table, nodes) == self._sig(table, copy)

    def test_two_steps_that_differ_only_in_a_middle_value_are_not_equal(self, table):
        a = [_step("sample_id", "not_in", ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"])]
        b = [_step("sample_id", "not_in", ["s0", "s1", "s2", "s19", "s4", "s5", "s6", "s7"])]
        assert _rows_after(table, a) != _rows_after(table, b), "the two step lists must leave other rows"
        assert _old_plan_signature(audited_frame(pl.scan_parquet(table), a), "k1") == _old_plan_signature(audited_frame(pl.scan_parquet(table), b), "k1"), \
            "the defect of the plan text was not reproduced (the Polars version prints the whole list?)"
        assert self._sig(table, a) != self._sig(table, b)

    def test_two_steps_that_differ_only_in_the_length_of_the_list_are_not_equal(self, table):
        a = [_step("sample_id", "not_in", [f"s{i}" for i in range(0, 8)])]
        b = [_step("sample_id", "not_in", [f"s{i}" for i in range(0, 4)] + ["s9"] + [f"s{i}" for i in range(4, 8)])]   # one longer; first two and last equal
        assert _rows_after(table, a) != _rows_after(table, b)
        assert _old_plan_signature(audited_frame(pl.scan_parquet(table), a), "k1") == _old_plan_signature(audited_frame(pl.scan_parquet(table), b), "k1")
        assert self._sig(table, a) != self._sig(table, b)

    def test_a_changed_na_choice_or_closed_end_is_not_equal(self, table):
        assert self._sig(table, [_step("year", "gt", 3, "Int64", na="keep")]) != self._sig(table, [_step("year", "gt", 3, "Int64", na="remove")])
        between = lambda closed: [_step("year", "between", [3, 7], "Int64", closed=closed)]
        assert self._sig(table, between("both")) != self._sig(table, between("none"))

    def test_the_same_steps_in_another_order_are_not_equal(self, table):
        """Order can change the result (a drop before a filter of the same column fails, the other order works): unequal is the safe answer."""
        f = _step("sample_id", "not_in", ["s0"])
        d = make_audit_step("drop_column", {"column": "sample_id"}, plot_scope="subtab_p", reason="r")
        assert self._sig(table, [f, d]) != self._sig(table, [d, f])

    def test_a_step_added_or_removed_is_not_equal(self, table):
        one = [_step("sample_id", "not_in", ["s0"])]
        assert self._sig(table, one) != self._sig(table, [])
        assert self._sig(table, one) != self._sig(table, one + [_step("sample_id", "not_in", ["s1"])])

    def test_no_steps_in_raw_result_and_my_view_is_the_same_rows(self, table):
        """T2 and T3 without audited steps are the same table: the form must not be mounted again (the first fix)."""
        assert self._sig(table, []) == self._sig(table, list())

    def test_steps_that_cannot_be_written_as_text_are_never_equal(self, table):
        broken = [{"node_type": "filter_row", "params": {1: "a", "b": 2}}]    # mixed keys: sort_keys fails
        assert self._sig(table, broken) != self._sig(table, broken)


class TestRowsSignatureOfTheStoredTable:
    def test_the_same_table_read_twice_is_equal(self, tmp_path):
        t1 = _stored(tmp_path, "k1", "k2")
        assert dialog_rows_signature(_identity(t1), []) == dialog_rows_signature(_identity(t1), [])
        assert dialog_rows_signature(_identity(t1, "T1"), []) == dialog_rows_signature(_identity(t1, "T1"), [])

    def test_raw_and_result_with_tier_2_steps_are_not_equal(self, tmp_path):
        """The Tier 2 table has its own rows (its own file and key): T1 and T2 are two tables."""
        t1 = _stored(tmp_path, "k1", "k2", rows=("a", "b", "c", "d"), t2_rows=("a", "b"))
        assert dialog_rows_signature(_identity(t1, "T1"), []) != dialog_rows_signature(_identity(t1, "T2"), [])

    def test_raw_and_result_without_tier_2_steps_are_the_same_table(self, tmp_path):
        t1 = _stored(tmp_path, "k1")
        assert dialog_rows_signature(_identity(t1, "T1"), []) == dialog_rows_signature(_identity(t1, "T2"), []) == dialog_rows_signature(_identity(t1, "T3"), [])

    def test_a_changed_tier_2_key_with_the_same_tier_1_key_is_not_equal(self, tmp_path):
        """Case b of the review: a tier-2 step is edited. The Tier 1 key does not hold tier-2 steps, the file keeps its path and its row
        count, and the text of the plan is the same; only the key in the footer of the Tier 2 file tells."""
        t1 = _stored(tmp_path, "k1", "k2", rows=("a", "b", "c"))
        before = dialog_rows_signature(_identity(t1), [])
        plan_before = _old_plan_signature(pl.scan_parquet(tier2_path_for(t1)), "k1")
        _stored(tmp_path, "k1", "k2-edited", rows=("a", "b", "c"), t2_rows=("a", "b", "z"))     # same path, same row count, other value
        assert _old_plan_signature(pl.scan_parquet(tier2_path_for(t1)), "k1") == plan_before, "the defect of the plan text was not reproduced"
        assert dialog_rows_signature(_identity(t1), []) != before

    def test_the_same_path_rewritten_with_the_same_row_count_under_another_tier_1_key_is_not_equal(self, tmp_path):
        t1 = _stored(tmp_path, "k1", rows=("a", "b", "c"))
        before = dialog_rows_signature(_identity(t1, "T1"), [])
        _stored(tmp_path, "k1-new", rows=("a", "b", "z"))
        assert dialog_rows_signature(_identity(t1, "T1"), []) != before

    def test_a_changed_key_of_the_open_view_is_not_equal(self, tmp_path):
        t1 = _stored(tmp_path, "k1")
        assert dialog_rows_signature(_identity(t1, view_key="a"), []) != dialog_rows_signature(_identity(t1, view_key="b"), [])

    def test_a_table_built_and_returned_without_being_stored_makes_a_new_identity(self, tmp_path):
        """No file carries a key for such a table (STALE-KEY-STORE-1); the count of these builds is part of the identity."""
        t1 = _stored(tmp_path, "k1")
        assert dialog_rows_signature(_identity(t1, unstored=0), []) != dialog_rows_signature(_identity(t1, unstored=1), [])

    def test_a_table_with_no_key_is_never_equal_to_itself(self, tmp_path):
        """A doubt is never equal: a missing file, a file with no key, a plot with no collection, a Tier 1 table read with no identity."""
        keyless = tmp_path / "keyless.parquet"
        pl.DataFrame({"era": ["a"]}).write_parquet(keyless)
        for identity in (stored_table_identity("T2", "t", "r", "vk", tmp_path / "missing.parquet", 0),
                         stored_table_identity("T2", "t", "r", "vk", keyless, 0),
                         stored_table_identity("T2", None, "r", "vk", keyless, 0), None):
            assert identity is None
            assert dialog_rows_signature(identity, []) != dialog_rows_signature(identity, [])

    def test_a_footer_that_cannot_be_read_is_none_not_an_error(self, tmp_path):
        broken = tmp_path / "broken.parquet"
        broken.write_bytes(b"not a parquet file")
        assert stored_key(broken, TIER1_KEY_META) is None
        assert stored_key(tmp_path / "missing.parquet", TIER1_KEY_META) is None

    def test_in_memory_tables_have_no_identity_so_two_of_them_are_never_equal(self):
        """Case c of the review: `DF ["x"]` is the same plan text for other rows. The signature does not read the plan."""
        a = pl.DataFrame({"x": [1, 2]}).lazy()
        b = pl.DataFrame({"x": [7, 8]}).lazy()
        assert _old_plan_signature(a, "k") == _old_plan_signature(b, "k"), "the defect of the plan text was not reproduced"
        assert dialog_rows_signature(None, []) != dialog_rows_signature(None, [])


# ---- headless: the real handler's Effect, defined with stand-ins -------------------------------------------------------------

class _AnyInput:
    """Every input is a function that returns nothing: the handler only needs them to exist at definition time."""
    def __getattr__(self, name):
        return lambda *a, **k: None


def _define_handler(interactivity: bool, tier: str, nodes: list, mode: str = "audit"):
    """Define the real `define_filter_audit_server` with stand-ins and run its Effects once. Returns what the form's Effect asked for."""
    seen = {"tables": 0, "identity": [], "signature": []}

    def make_lf(spec, tier=None):
        seen["tables"] += 1
        return pl.DataFrame({"era": ["a", "b"]}).lazy()

    def identity(spec, tier_now):
        seen["identity"].append((spec, tier_now))
        return ("a stored table",)

    real_signature = h.dialog_rows_signature

    def record(identity_in, nodes_in):
        seen["signature"].append((identity_in, list(nodes_in)))
        return real_signature(identity_in, nodes_in)

    async def main():
        stub = SimpleNamespace(is_enabled=lambda flag: interactivity if flag == "interactivity_enabled" else True)
        with mock.patch.object(h, "bootloader", stub), mock.patch.object(h, "dialog_rows_signature", record):
            h.define_filter_audit_server(
                _AnyInput(), lambda fn: fn, None,
                applied_filters=reactive.Value([]), _pending_filters=reactive.Value([]), _propagation_scratch=reactive.Value({}),
                home_state=reactive.Value({"t3_audit_steps_by_plot": {"subtab_p": nodes}}), in_audit=lambda: mode == "audit",
                data_view=reactive.Value(tier), view_source_table=lambda: None, current_view_key=lambda: None,
                active_home_subtab=reactive.Value("subtab_p"), safe_input=lambda inp, key, default=None: default,
                _resolve_active_spec=lambda p: {"target_dataset": "t", "plot": p}, _resolve_active_lf=make_lf,
                _spec_discrete_axes=lambda spec: ([], []), _t3_drop_columns=lambda *a: [], _all_plot_subtab_ids=lambda: [],
                _plot_label=lambda sub: sub, _table_identity=identity)
            await reactive.flush()
    asyncio.run(main())
    return seen


class TestTheFormsEffectInTheRealHandler:
    def test_without_interactivity_the_effect_builds_no_table_and_asks_for_no_identity(self):
        """The Filters panel does not exist then (`sidebar_filters` shows a static message): the Effect does nothing."""
        seen = _define_handler(False, "T3", [_step("era", "in", ["a"])])
        assert seen["tables"] == 0 and seen["identity"] == [] and seen["signature"] == []

    def test_with_interactivity_the_effect_builds_the_table_once_and_asks_for_the_identity_of_the_open_plot_and_view(self):
        seen = _define_handler(True, "T2", [])
        assert seen["tables"] >= 1
        assert seen["identity"] == [({"target_dataset": "t", "plot": "p"}, "T2")]

    def test_the_audited_steps_are_part_of_the_signature_on_audit_t3_only(self):
        """The dialog applies the audited steps on T3 in Audit mode only, like `_active_frame`: the signature reads the same steps."""
        step = _step("era", "in", ["a"])
        assert _define_handler(True, "T3", [step])["signature"][-1] == (("a stored table",), [step])
        assert _define_handler(True, "T2", [step])["signature"][-1] == (("a stored table",), [])
        assert _define_handler(True, "T1", [step])["signature"][-1] == (("a stored table",), [])
        assert _define_handler(True, "SRC", [step])["signature"][-1] == (("a stored table",), [])
        assert _define_handler(True, "T3", [step], mode="exploration")["signature"][-1] == (("a stored table",), []), "Exploration: no audited step on T3"


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
    set_view(page, tier)
    _wait_shiny(page, 30_000)


def _ready_on_mlst(page: Page, base_url: str) -> None:
    """The MLST Bar plot of the 1_test_data_ST22_dummy recipe (`year` is a number column), data choice T2, form open."""
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
        """T2 and T3 of this plot hold the same columns: the form is not mounted again, so what was chosen is still there."""
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
        """The race of the defect, as a user makes it: change the data choice, then choose a column a few milliseconds later. The server
        used to render the form with the old column while the new one was on its way (9 of 30 tries before the fix)."""
        _ready_on_mlst(page, shiny_app.url)
        delays = [0, 5, 10, 20, 40, 0, 10, 20]
        for i, delay in enumerate(delays * 2):
            target = ("year", "sample_id")[i % 2]
            _show_start = ("T3", "T2")[i % 2]
            page.locator(f"#data_view input[value={_show_start}]").check(force=True)
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
        """T1 has no `era` column, T2 has: the columns really change. `year` is in both: it stays chosen."""
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
    operators AND the comparisons, and its value widget is a list or a number box by the operator. The plot casts `year` to text in its own tier-3
    steps (so that it draws, D-0327), so the whole number is the table of the earlier tiers: the test reads the dialog in Raw (T1) and Result (T2)."""

    def test_operator_and_value_of_a_discrete_year_survive_a_change_of_view(self, page: Page, typed_app):
        page.goto(typed_app)
        page.wait_for_selector("#data_analysis_recipe_id", timeout=20_000)
        _wait_shiny(page, 60_000)
        page.locator(".nav-link:has-text('Years')").first.click()
        _wait_shiny(page)
        _show(page, "T1")
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
        for tier in ("T2", "T1"):
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
        for tier in ("T2", "T1"):
            _show(page, tier)
        expect(page.locator("#fb_op")).to_have_value("gt")
        expect(page.locator("#fb_value")).to_have_value("1999")


def _list_options(page: Page) -> list:
    """The values the open list box offers."""
    return page.evaluate("() => { const e = document.getElementById('fb_value'); return e && e.selectize ? Object.keys(e.selectize.options) : []; }")


class TestTheValueWidgetFollowsTheRows:
    """The columns stay and the rows change: the value widget is built from the rows, so it must be built again (the rows signal).
    Table of 30 rows (sample_id s1..s30, score 1..30); an audited filter `score >= 16` keeps 15 of them. Waits are on the form's state."""

    def test_a_list_of_values_loses_the_removed_values_with_the_audited_step_and_gets_them_back_when_it_is_deleted(self, page: Page, staged_app):
        _start(page, staged_app)                                   # Audit mode, T3, 30 rows
        _filter_step(page, 1)                                      # audited step: score >= 16 (rows 16..30)
        _expect_rows(page, N - THRESHOLD + 1)
        _choose(page, "sample_id")
        page.wait_for_function("() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 0; }",
                               timeout=15_000)
        options = _list_options(page)
        assert "s30" in options and "s1" not in options and len(options) == N - THRESHOLD + 1, f"the list holds the removed rows: {options}"
        # The column stays chosen: only the rows change. Delete the step (the trash button of the audit step).
        page.locator("button[id^=t3_delete_]").first.click()
        _expect_rows(page, N)
        page.wait_for_function("() => Object.keys(document.getElementById('fb_value').selectize.options).length === 30", timeout=15_000)
        expect(page.locator("#fb_col")).to_have_value("sample_id")
        assert "s1" in _list_options(page), "the value list was not built again when the rows came back"

    def test_the_range_of_a_number_box_follows_the_rows_with_the_same_column_chosen(self, page: Page, staged_app):
        """`score` stays the chosen column and `>=` the operator while the step is applied and deleted: the box holds the smallest value of
        the rows that are there."""
        _start(page, staged_app)
        _filter_step(page, 1)
        _expect_rows(page, N - THRESHOLD + 1)
        expect(page.locator("#fb_col")).to_have_value("score")
        page.wait_for_function("() => document.querySelector('#fb_value') && document.querySelector('#fb_value').min === '16'", timeout=15_000)
        page.locator("button[id^=t3_delete_]").first.click()
        _expect_rows(page, N)
        page.wait_for_function("() => document.querySelector('#fb_value') && document.querySelector('#fb_value').min === '1'", timeout=15_000)
        expect(page.locator("#fb_col")).to_have_value("score")
