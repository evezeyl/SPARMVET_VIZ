"""The table of the view shown decides what the HOME filter form shows (D-0178, D-0310, D-0021, D-0177).

D-0178: "a filter is built on the table of the view shown: if the user is on T1 the filter is built from T1". The view has four values
(Source, T1, T2, T3) and two modes. The form's columns and values come from the table of the view shown; in Audit mode on T3 that table is
the plot's table after its audited steps (a value an audited step removed is not listed and the table does not show it); in Exploration
T3 holds no audited step. Changing the view changes the list in every direction with no page reload.

Headless: the pure functions the form is made of (`dialog_frame` below, a table that is audited on T3 in Audit mode only, `value_choices`, `dialog_rows_signature`, `stored_table_identity`), and the
REAL form (`filter_form_ui` of `define_filter_audit_server`, run on the real HOME readers) for each of the four views of a plot on a join.
Browser (qa app features): the real form of the real app on a small staged recipe (30 samples; the audited step keeps score >= 16, so it
removes the samples s1 to s15). The value list and the table rows are checked separately, so a failure says which one is wrong.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_tier_decides_filter_form.py -q
"""
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import polars as pl
import pytest
import yaml
from playwright.sync_api import Page, expect
from shiny import reactive

from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, tier2_path_for
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
from app.modules.session_manager import make_audit_step
from app.modules.t3_audit_engine import dialog_rows_signature, stored_table_identity, value_choices
from app.tests.audit_nodes import audited_lf
from app.tests.browser_view import in_audit_mode, set_mode, set_view, show_place, show_plot
from app.tests.subprocess_env import app_command, app_env
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly, _choose_operator
from app.tests.test_shiny_smoke import _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from app.tests.test_shiny_step_order import N, PLOT, THRESHOLD, _expect_rows, _filter_step, _start
from app.tests.home_harness import Home, ViewWorld
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_tier_filter"
REMOVED = [f"s{i}" for i in range(1, THRESHOLD)]            # s1 .. s15: the rows the audited step removes
KEPT = [f"s{i}" for i in range(THRESHOLD, N + 1)]           # s16 .. s30
EVERY = [f"s{i}" for i in range(1, N + 1)]


# -- headless: the claim at the level of the functions ------------------------------------------------------------------------

def _step(column, op, value, dtype="String"):
    return make_audit_step("filter_row", {"column": column, "op": op, "value": value, "dtype": dtype}, plot_scope="subtab_p", reason="r")


def _lf():
    return pl.DataFrame({"sample_id": [f"s{i}" for i in range(1, 11)], "year": [2000 + i % 3 for i in range(1, 11)]}).lazy()


def _listed(lf, column):
    return list(value_choices(lf, column))


def dialog_frame(lf, nodes, with_audited_steps):
    """The table the form's value list is read from: the audit steps are in the table of the audit copy on T3 in Audit mode (`home_theater._resolve_active_lf`), and on any other
    view the table is as it is. Here the steps are run by the engine's own actions on a frame (`audited_lf`), so the claim is about the steps and not about a second function."""
    return audited_lf(lf, nodes) if with_audited_steps else lf


class TestValueListFollowsTheViewShown:
    """The table the form's value list is read from: the audited steps are in it on T3 in Audit mode only."""

    def test_a_removed_sample_is_not_listed_in_audit_t3_and_is_listed_on_every_other_view(self):
        nodes = [_step("sample_id", "not_in", ["s1"])]
        assert "s1" not in _listed(dialog_frame(_lf(), nodes, with_audited_steps=True), "sample_id")
        assert "s1" in _listed(dialog_frame(_lf(), nodes, with_audited_steps=False), "sample_id")   # Source, T1, T2, Exploration T3: the table as it is

    def test_a_removed_year_is_not_listed_in_audit_t3_and_is_listed_otherwise(self):
        nodes = [_step("year", "ge", 2001, "Int64")]                      # removes every row of 2000
        assert 2000 in value_choices(dialog_frame(_lf(), nodes, with_audited_steps=False), "year").values()
        mine = value_choices(dialog_frame(_lf(), nodes, with_audited_steps=True), "year").values()
        assert 2000 not in mine and 2001 in mine

    def test_switching_back_and_forth_gives_the_same_lists(self):
        nodes = [_step("sample_id", "not_in", ["s1", "s2"])]
        mine = [_listed(dialog_frame(_lf(), nodes, with_audited_steps=v), "sample_id") for v in (True, False, True, False, True)]
        assert mine[0] == mine[2] == mine[4] and mine[1] == mine[3]
        assert mine[0] != mine[1]

    def test_the_step_taken_away_gives_the_value_back(self):
        """Removed, not only added (rules_verification_testing.md section 9): without the step the list is whole again."""
        with_step = _listed(dialog_frame(_lf(), [_step("sample_id", "not_in", ["s1"])], True), "sample_id")
        without = _listed(dialog_frame(_lf(), [], True), "sample_id")
        assert "s1" not in with_step and "s1" in without


class TestRowsSignatureFollowsTheViewShown:
    """The form mounts the value widget again when the rows signature changes: it must change with the view shown."""

    @pytest.fixture
    def stored(self, tmp_path):
        t1 = tmp_path / "t.parquet"
        pl.DataFrame({"sample_id": [f"s{i}" for i in range(1, 6)]}).write_parquet(t1, metadata={TIER1_KEY_META: "k1"})
        return t1

    def _sig(self, t1, tier, nodes):
        # The same call as the handler: the audited steps count on T3 in Audit mode only (`_signal_dialog_table`); `tier` here is the view.
        return dialog_rows_signature(stored_table_identity(tier, "t", "recipe", "vk", t1, 0), nodes if tier == "T3" else [])

    def test_audit_t3_with_the_step_differs_from_t1_and_t2_and_without_tier2_the_two_are_the_same_table(self, stored):
        nodes = [_step("sample_id", "not_in", ["s1"])]
        mine, raw, result = (self._sig(stored, t, nodes) for t in ("T3", "T1", "T2"))
        assert mine != raw and mine != result
        assert raw == result, "no tier-2 steps: T1 and T2 are one stored table, no reason to mount the list again"

    def test_with_a_tier2_table_t1_and_t2_differ_and_audit_t3_differs_from_both(self, stored):
        pl.DataFrame({"sample_id": ["s2", "s3"]}).write_parquet(tier2_path_for(stored), metadata={TIER2_KEY_META: "k2"})
        nodes = [_step("sample_id", "not_in", ["s2"])]
        mine, raw, result = (self._sig(stored, t, nodes) for t in ("T3", "T1", "T2"))
        assert len({mine, raw, result}) == 3

    def test_going_to_t1_or_t2_and_back_returns_the_first_signature(self, stored):
        nodes = [_step("sample_id", "not_in", ["s1"])]
        first = self._sig(stored, "T3", nodes)
        assert self._sig(stored, "T1", nodes) != first and self._sig(stored, "T3", nodes) == first
        assert self._sig(stored, "T2", nodes) != first and self._sig(stored, "T3", nodes) == first

    def test_t3_without_a_step_equals_t2(self, stored):
        assert self._sig(stored, "T3", []) == self._sig(stored, "T2", [])


# -- headless: the REAL form on the four views of a plot on a join -------------------------------------------------------------

def _options(html: str, select_id: str = "fb_col") -> list:
    import re
    block = re.search(rf'<select[^>]*id="{select_id}".*?</select>', html, re.S).group(0)
    return re.findall(r'<option value="([^"]+)"', block)


class TestTheRealFormFollowsTheViewShown:
    """The form's columns come from the table of the view shown (D-0178) for a plot on a join (T and M, joined; tier 2 keeps score >= 2) and for
    a plot with its own tier-3 steps (score >= 3, `site` dropped). MUTATION F1: the form reads the T3 table whatever the view; this fails."""

    def columns(self, tmp_path, monkeypatch, view, plot, source=None, mode="exploration", flags=("interactivity_enabled",)):
        world = ViewWorld(tmp_path)
        home = Home(world, monkeypatch, view=view, subtab=f"subtab_{plot}", source=source, mode=mode, flags=flags)
        home.filter_handlers(monkeypatch)
        with reactive.isolate():
            return _options(str(home.outputs["filter_form_ui"]()))

    # The marker column of the completion of the ids is an ordinary yes/no column of the table (the flag column is kept, D-0586): it is offered in the form from tier 1 on, one for
    # each table that takes part (T and M here). The Source view shows the file as read, so it has none.
    JOIN = ["sample_id", "group", "score", "T_not_in_original_data", "site", "M_not_in_original_data"]

    @pytest.mark.parametrize("view,source,expected", [
        ("SRC", "T", ["sample_id", "group", "score"]), ("SRC", "M", ["sample_id", "site"]),
        ("T1", None, JOIN), ("T2", None, JOIN), ("T3", None, JOIN)])
    def test_a_plot_on_a_join(self, tmp_path, monkeypatch, view, source, expected):
        assert self.columns(tmp_path, monkeypatch, view, "p_join", source) == expected

    @pytest.mark.parametrize("view,expected", [("T1", JOIN), ("T2", JOIN),
                                               ("T3", ["sample_id", "group", "score", "T_not_in_original_data", "M_not_in_original_data"])])   # `site` dropped by the plot's own steps
    def test_a_plot_with_its_own_tier3_steps(self, tmp_path, monkeypatch, view, expected):
        assert self.columns(tmp_path, monkeypatch, view, "p_steps") == expected

    def test_audit_mode_t3_does_not_offer_a_column_an_audited_step_dropped(self, tmp_path, monkeypatch):
        world = ViewWorld(tmp_path)
        drop = make_audit_step("drop_column", {"column": "group"}, plot_scope="__places__", reason="r", place="T3:p_join")
        state = {"t3_audit_steps_by_plot": {"__places__": [drop]}}
        flags = ("interactivity_enabled", "t3_sandbox_enabled", "comparison_mode_enabled")
        for mode, view, expected_has_group in (("audit", "T3", False), ("audit", "T2", True), ("exploration", "T3", True)):
            home = Home(world, monkeypatch, view=view, mode=mode, flags=flags, home_state=state, subtab="subtab_p_join")
            if mode == "audit" and view == "T2":
                home.show("T2:J")            # slice 3a: in Audit mode the table is the place shown, not a data choice
            home.filter_handlers(monkeypatch)
            with reactive.isolate():
                assert ("group" in _options(str(home.outputs["filter_form_ui"]()))) is expected_has_group, (mode, view)


# -- browser: the real form on a staged recipe --------------------------------------------------------------------------------

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def staged_app():
    """The app on a deployment of its own: one table of 30 samples (sample_id, year, score) and one plot of the samples per year."""
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "t.tsv").write_text("sample_id\tyear\tscore\n" + "".join(f"s{i}\t{2000 + i % 3}\t{i}\n" for i in range(1, N + 1)), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_tier_filter/t.tsv", {"sample_id": "String", "year": "Int64", "score": "Int64"}, entity_key="sample_id")
    schema["description"] = "One row per sample."
    plot = minimal_plot("t", {"x": "year"}, [{"name": "geom_bar", "params": {}}], label="per year")
    plot["description"] = "The number of samples per year."
    recipe = minimal_recipe("t", label="T", schemas={"t": schema}, plots={PLOT: plot})
    recipe["info"]["description"] = "A table of 30 samples and one plot, for a browser check that the viewed tier decides the filter list."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "TG", "description": "The one group."})
    recipe["analysis_groups"] = {"tg": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "t.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    problems = validate_data_analysis_recipe(recipes / "t.yaml")
    assert not problems, f"the staged recipe is refused by the load gate: {problems}"
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "locations": locations,
                                          "default_data_analysis_recipe": "t", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    with open(WORK / "server.log", "w") as out:
        proc = subprocess.Popen(app_command(port), cwd=REPO, env=app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(deployment)),
                                stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(90):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            yield url
        finally:
            proc.terminate()
            proc.wait(timeout=20)


def _print_flags(page: Page) -> None:
    """Print the flags the run is made with: from the app features file the app was started with (qa) and, as seen in the page, what
    each one shows. A flag that is not on is named in the report of the run, not assumed."""
    class _Plain(yaml.SafeLoader):
        """Reads the file as it is: the `!include` of the sidebar files is not followed, the flags do not need it."""
    _Plain.add_multi_constructor("!", lambda loader, suffix, node: None)
    flags = yaml.load((REPO / "config" / "app_features" / "qa.yaml").read_text(encoding="utf-8"), Loader=_Plain)
    on = flags["flags"]
    seen = {
        "audit (t3_sandbox_enabled) -> Pipeline Audit panel": page.locator("text=Pipeline Audit").count() > 0,
        "sessions (session_management_enabled) -> Session panel": page.locator("#nav_accordion .accordion-button:has-text('Session')").count() > 0,
        "export (export_enabled) -> Export panel": page.locator("#nav_accordion .accordion-button:has-text('Export')").count() > 0,
        "blueprint (blueprint_enabled) -> Blueprint nav": page.locator("text=Blueprint").count() > 0,
    }
    print(f"\nFLAGS qa.yaml: audit={on['t3_sandbox_enabled']} sessions={on['session_management_enabled']} export={on['export_enabled']} "
          f"blueprint={on['blueprint_enabled']} comparison={on['comparison_mode_enabled']} interactivity={on['interactivity_enabled']} "
          f"ghost_save={flags['automation']['ghost_save']['enabled']} testing_mode={flags['testing_mode']}")
    for name, shown in seen.items():
        print(f"FLAGS seen in the page: {name}: {shown}")


@pytest.fixture(scope="module")
def audited(page: Page, staged_app):
    """Audit mode on T3 of the plot with one applied audited step (score >= 16, with a reason): the samples s1..s15 are removed from it."""
    _start(page, staged_app)
    _print_flags(page)
    page.evaluate("() => { window.__no_reload_marker = 'same page'; }")
    _filter_step(page, 1)
    _expect_rows(page, len(KEPT))
    return page


def _pick_sample_list(page: Page) -> None:
    """The form on the column sample_id with the operator `in`: its value widget is the list of the samples."""
    _open_filters_panel(page)
    _wait_for_fb_col_option(page, "sample_id")
    _choose_column_firmly(page, "sample_id")
    _choose_operator(page, "in")
    _wait_for_list(page)


def _list_now(page: Page):
    """The values the value box of the form offers now (None when the box is not mounted)."""
    return page.evaluate("() => { const e = document.getElementById('fb_value'); return e && e.selectize ? Object.keys(e.selectize.options) : null; }")


def _wait_for_list(page: Page) -> None:
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 0; }",
                           timeout=15_000)


def _table_samples(page: Page, expected_count: int, timeout: float = 15.0):
    """The sample_id cells of the data table, as shown now; read again until there are `expected_count` of them or the time is over
    (a retrying read of the app state: the grid is redrawn a moment after the row summary changes). None when the column is not shown."""
    js = """() => { const heads = Array.from(document.querySelectorAll('#home_data_preview thead th')).map(t => t.innerText.trim());
                    const c = heads.indexOf('sample_id');
                    if (c < 0) return null;
                    return Array.from(document.querySelectorAll('#home_data_preview tbody tr'))
                        .filter(r => r.children.length > c).map(r => r.children[c].innerText.trim()); }"""
    deadline = time.time() + timeout
    seen = page.evaluate(js)
    while (seen is None or len(seen) != expected_count) and time.time() < deadline:
        page.wait_for_timeout(250)   # poll interval of a retrying read
        seen = page.evaluate(js)
    return seen


def _view(page: Page, tier: str) -> None:
    """Show the table of tier T1, T2 or T3 and wait until Shiny is idle; nothing is chosen again after it. In Audit mode (slice 3a) there is no data choice: T3 is the Result data of the open
    plot, and the table `t` of this recipe has no tier-2 steps, so its tier 2 is its tier 1: both are shown as the place `T1:t`."""
    if tier == "T3":
        if in_audit_mode(page):
            show_plot(page, PLOT)      # Audit mode has no plot tabs (slice 3b): the plot's Result data is shown from the lineage
        else:
            set_view(page, "T3")
    else:
        show_place(page, "T1:t", keep_chosen=False)


def _list_settles_to(page: Page, expected_count: int, timeout: float = 15.0):
    """Read the list until it holds `expected_count` values or the time is over; returns what was last seen (a retrying read of the app state)."""
    deadline = time.time() + timeout
    seen = _list_now(page)
    while (seen is None or len(seen) != expected_count) and time.time() < deadline:
        page.wait_for_timeout(250)   # poll interval of a retrying read
        seen = _list_now(page)
    return seen


def _describe(page: Page) -> str:
    """What the user sees now, for a failure message: the column box, the list size, the first values and the rows of the table."""
    shown = _list_now(page)
    return (f"column box={page.locator('#fb_col').input_value()!r}, list={'none' if shown is None else len(shown)} values "
            f"{None if shown is None else shown[:3]}..., table rows={len(_table_samples(page, 0, 0) or [])}")


class TestTheViewedTierDecidesTheForm:
    def test_audit_t3_list_does_not_hold_the_removed_samples(self, audited: Page):
        page = audited
        _view(page, "T3")
        _pick_sample_list(page)
        seen = _list_settles_to(page, len(KEPT))
        assert seen is not None and sorted(seen) == sorted(KEPT), f"POINT 1, value list in Audit T3: {_describe(page)}"
        assert not set(REMOVED) & set(seen)

    def test_audit_t3_table_does_not_show_the_removed_samples(self, audited: Page):
        page = audited
        _view(page, "T3")
        _expect_rows(page, len(KEPT))
        shown = _table_samples(page, len(KEPT))
        assert shown is not None and sorted(shown) == sorted(KEPT), f"POINT 1, table rows in Audit T3: {_describe(page)}"

    @pytest.mark.parametrize("tier", ["T1", "T2"])
    def test_t1_and_t2_list_holds_the_removed_samples(self, audited: Page, tier):
        page = audited
        _view(page, "T3")
        _pick_sample_list(page)
        _view(page, tier)
        seen = _list_settles_to(page, N)
        assert seen is not None and sorted(seen) == sorted(EVERY), f"POINT 2, value list in {tier}: {_describe(page)}"
        _view(page, "T3")      # leave the view as the next test expects it

    @pytest.mark.parametrize("tier", ["T1", "T2"])
    def test_t1_and_t2_table_shows_the_removed_samples(self, audited: Page, tier):
        page = audited
        _view(page, tier)
        _expect_rows(page, N)
        # The grid keeps only the rows in view in the page (23 of 30 here), so the summary says how many rows the table has ("of 30", above)
        # and the cells say which: the first rows are the removed samples, and nothing outside the table is shown.
        shown = _table_samples(page, 0, 3)
        assert shown, f"POINT 2, table rows in {tier}: no row shown; {_describe(page)}"
        assert set(REMOVED[:5]) <= set(shown) <= set(EVERY), f"POINT 2, table rows in {tier}: {_describe(page)}; shown {shown}"
        _view(page, "T3")

    @pytest.mark.parametrize("other", ["T1", "T2"])
    def test_switching_changes_the_list_in_both_directions_without_a_reload(self, audited: Page, other):
        page = audited
        _view(page, "T3")
        _pick_sample_list(page)
        for step, (tier, count) in enumerate([("T3", len(KEPT)), (other, N), ("T3", len(KEPT)), (other, N), ("T3", len(KEPT))]):
            _view(page, tier)
            seen = _list_settles_to(page, count)
            assert seen is not None and len(seen) == count, f"POINT 3, step {step} (view {tier}, expected {count} values): {_describe(page)}"
            assert ("s1" in seen) == (tier != "T3"), f"POINT 3, step {step} (view {tier}): 's1' listed={('s1' in seen)}; {_describe(page)}"
            assert page.locator("#fb_col").input_value() == "sample_id", f"POINT 3, step {step}: the column box changed; {_describe(page)}"
        assert page.evaluate("() => window.__no_reload_marker") == "same page", "the page was reloaded"

    def test_the_audited_step_is_still_applied_after_all_the_switches(self, audited: Page):
        """The applied step applies no matter which view was visited in between (D-0177): back on Audit T3 the table is the filtered one."""
        page = audited
        for tier in ("T1", "T2", "T3"):
            _view(page, tier)
        _expect_rows(page, len(KEPT))
        shown = _table_samples(page, len(KEPT))
        assert shown is not None and sorted(shown) == sorted(KEPT), f"after the switches, table rows in Audit T3: {_describe(page)}"

    def test_exploration_t3_holds_no_audited_step_so_its_list_and_table_hold_every_sample(self, audited: Page):
        """D-0180: Exploration is clean. The audited step waits in Audit mode; the T3 table of Exploration is the plot's own table."""
        page = audited
        try:
            set_mode(page, "exploration")
            _view(page, "T3")
            _expect_rows(page, N)
            _pick_sample_list(page)
            seen = _list_settles_to(page, N)
            assert seen is not None and sorted(seen) == sorted(EVERY), f"Exploration T3, value list: {_describe(page)}"
        finally:
            set_mode(page, "audit")
            _view(page, "T3")
