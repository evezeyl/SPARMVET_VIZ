"""Try an audit step before it is applied, in the browser (FLOW-1 of the new Audit flow; ledger D-0650, D-0656, D-0662, D-0669, D-0671).

Run (qa app features: every flag on, ghost save off; about ten minutes on an idle machine):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_try_browser.py -q
and, for the last test, with `SPARMVET_DATA_ANALYSIS_RECIPE=1_test_data_ST22_dummy SPARMVET_APP_FEATURES=pipeline-exploration-simple` (no audit: no Try).

# @deps
# consumes: app/handlers/trial_handlers.py (the panel, Discard, the ends of a trial), app/handlers/filter_and_audit_handlers.py (the button Try), app/handlers/home_theater.py (the preview, the band, the badge, the figure and Compare read the trial), app/modules/audit_trial.py (the engine), app/modules/audit_try.py (the words)
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0650, D-0656, D-0662, D-0669, D-0671, D-0302, D-0327)
# @end_deps

What a person does and sees, on the demo `1_test_data_ST22_dummy` (Audit mode, nothing applied):
- builds a condition in the Filters panel on the table shown and presses Try: a panel says, for each place, how many rows the step removes THERE (the engine's count, equal here to a count made with polars on
  the same tables) and what the places reach; the item shown shows the trial and says so in words (band, badge, title, plot area), the figure is drawn from it; Discard puts everything back;
- the same on a TABLE shown (new): Try at ResFinder T1; showing the plot built from it shows the trial (its rows equal an audit copy with the step really appended); a plot the step does not reach says so;
- two places chosen: each has its line; a place where the condition does not fit stops the trial and is named; a selection that does not hold the place shown asks to show it first;
- Compare beside a trial: the left pane "before this step", the right pane the trial, a switch for the original on the left;
- a trial ends, with one plain notice and its folder emptied, when the condition or the places change and when Audit mode is left (FLOW-3: the old entries, Send to Audit and the others, are gone);
- a trial is in no session file, no export and no stored audited table.

Mutation index (each seen failing): MUTATION F1 the preview keeps the audited table during a trial (`_preview_lf` without `with_trial`); MUTATION F2 the plot figure does not read the trial (`_group_plot_handler`);
MUTATION F3 the trial folder is not emptied at Discard.
"""
import hashlib
import io
import os
import zipfile
from pathlib import Path

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import preview_rows, set_compare, set_mode, show_place, show_plot, wait_preview_rows, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_audit_view import World
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_lineage_view_browser import _clear_choice, _line, _open_panel
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _choose_fb_op, _load_data_analysis_recipe, _open_filters_panel, _wait_shiny

LAUNCH = os.environ.get("SPARMVET_APP_FEATURES", "developer")
NEEDS_AUDIT = pytest.mark.skipif(LAUNCH not in _INTERACTIVE_APP_FEATURES or LAUNCH == "pipeline-exploration-simple", reason="needs the audit")
RECIPE = "1_test_data_ST22_dummy"
PLOT = "amr_heatmap"
ROOT = Path(__file__).resolve().parents[2]
AREA = ".spv-audit-plot-area"
PANEL = ".spv-trial-panel"
TRIAL_WORDS = "TRIAL: with the step you are trying. Not applied, not saved, not exported."


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    return World(tmp_path_factory.mktemp("try_browser"))


@pytest.fixture(scope="module")
def tables(world):
    """Everything the test compares with, computed here with polars from the engine's own tables (never typed in)."""
    orch, anchors = world.orch, world.anchors
    plot = orch.materialize_tier3(RECIPE, PLOT, anchors).collect()
    resfinder = orch.materialize_tier1(RECIPE, "ResFinder", anchors / "ResFinder.parquet").collect()
    quality = orch.materialize_tier1(RECIPE, "Quality_metrics", anchors / "Quality_metrics.parquet").collect()
    mlst_bar = orch.materialize_tier3(RECIPE, "mlst_bar", anchors).collect()
    identity = plot["identity"].drop_nulls()
    threshold = float(identity.unique().sort()[len(identity.unique()) // 2])
    kept_plot = plot.filter(pl.col("identity") < threshold).height
    kept_resfinder = resfinder.filter(pl.col("identity") < threshold).height
    assert 0 < kept_plot < plot.height and 0 < kept_resfinder < resfinder.height, "the test needs a value that removes some rows and keeps others"
    node = world.node(place="T1:ResFinder", params={"column": "identity", "op": "lt", "value": threshold, "na": "remove", "dtype": "Float64"})
    fresh_plot = world.audit().plot_lazy(RECIPE, PLOT, [node], world.plans).collect().height          # a fresh computation: the applied step really in the audit copy
    assert fresh_plot != plot.height, "a step at ResFinder must change the plot the demo builds from it"
    return {"plot": plot, "resfinder": resfinder, "quality": quality, "mlst_bar": mlst_bar, "threshold": threshold, "kept_plot": kept_plot, "kept_resfinder": kept_resfinder,
            "fresh_plot_after_resfinder_step": fresh_plot}


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url, RECIPE)
    _open_filters_panel(page)
    page.locator(".nav-link:has-text('AMR')").first.click()
    _wait_shiny(page)
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)
    yield page


@pytest.fixture(autouse=True)
def back_to_a_clean_page(request):
    """Every test leaves the page without a trial, a staged condition or an applied step, in Exploration."""
    yield
    if "ready" in request.fixturenames:
        page = request.getfixturevalue("ready")
        try:
            if page.locator("#trial_discard").count():
                page.locator("#trial_discard").click()
                wait_shiny(page)
            page.locator("#filter_reset").click()
            for b in page.locator("[id^='t3_delete_']").all():
                b.click()
                wait_shiny(page)
            _clear_choice(page)
            set_mode(page, "exploration")
        except Exception:
            pass


def user_data() -> Path:
    from app.src.bootloader import bootloader
    return bootloader.get_location("user_data")


def trial_files() -> list:
    root = user_data() / "audit_trial"
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()) if root.is_dir() else []


def listing(folder: Path) -> dict:
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()} if folder.is_dir() else {}


def enter_audit(page: Page) -> None:
    set_mode(page, "audit")
    _open_panel(page)
    _clear_choice(page)
    wait_shiny(page)
    expect(page.locator(AREA)).to_contain_text("Plot shown: AMR Heatmap", timeout=30_000)


def build_condition(page: Page, column: str, op: str, value: float) -> None:
    _choose_column_firmly(page, column)
    _choose_fb_op(page, op)
    _wait_shiny(page)
    page.locator("#fb_value").fill(repr(value))
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)


def build_list_condition(page: Page, column: str, op: str, value: str) -> None:
    """A condition on a text column: the value is taken from the list the form offers."""
    _choose_column_firmly(page, column)
    _choose_fb_op(page, op)
    _wait_shiny(page)
    page.wait_for_function("(v) => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).includes(v); }", arg=value, timeout=15_000)
    page.evaluate("(v) => document.getElementById('fb_value').selectize.addItem(v)", value)
    page.wait_for_function("(v) => document.getElementById('fb_value').selectize.items.includes(v)", arg=value, timeout=5_000)
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)


def press_try(page: Page) -> None:
    expect(page.locator("#filter_try")).to_be_visible(timeout=15_000)
    page.locator("#filter_try").click()
    wait_shiny(page, 90_000)


def notices(page: Page) -> str:
    panel = page.locator("#shiny-notification-panel")
    return panel.inner_text() if panel.count() else ""


def close_notices(page: Page) -> None:
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


def figure(page: Page, plot_id: str = PLOT) -> str:
    """A hash of the picture drawn in the plot shown."""
    page.wait_for_function(f"() => {{ const i = document.querySelector('#plot_group_{plot_id} img'); return i && i.src && i.naturalWidth > 0; }}", timeout=60_000)
    src = page.evaluate(f"() => document.querySelector('#plot_group_{plot_id} img').src")
    return hashlib.sha256(src.encode()).hexdigest()


# ---------------------------------------------------------------------------------------------------------------------------------
@NEEDS_AUDIT
def test_try_at_the_plot_shown_counts_the_rows_shows_the_trial_in_words_and_discard_puts_everything_back(ready: Page, tables):
    page = ready
    enter_audit(page)
    wait_preview_rows(page, tables["plot"].height, timeout=60_000)
    before_figure = figure(page)
    build_condition(page, "identity", "lt", tables["threshold"])
    audit_files, session_files = listing(user_data() / "audit_anchors"), listing(user_data() / "_sessions")
    press_try(page)
    panel = page.locator(PANEL)
    expect(panel).to_be_visible(timeout=60_000)
    expect(panel).to_contain_text(TRIAL_WORDS)
    removed = tables["plot"].height - tables["kept_plot"]
    expect(panel).to_contain_text(f"AMR Heatmap: Result data, T3: the step removes {removed} rows of {tables['plot'].height} here")
    expect(panel).to_contain_text("User verified")                                      # FLOW-2: each place has its mark, and the step is added here
    wait_preview_rows(page, tables["kept_plot"], timeout=60_000)                       # the preview shows the trial: the rows the independent count says
    expect(page.locator("#shown_band_ui")).to_contain_text(TRIAL_WORDS)
    expect(page.locator("#shown_band_ui .spv-shown-band-trial")).to_have_count(1)
    expect(page.locator("#acc_home_data")).to_contain_text("(TRIAL, not applied)")     # the title of the preview
    expect(page.locator("#home_data_preview_badge")).to_contain_text("TRIAL, not applied")
    expect(page.locator(AREA)).to_contain_text(TRIAL_WORDS)                            # beside the plot's title
    expect(page.locator(f"#plot_badge_{PLOT}")).to_contain_text("TRIAL, not applied")
    page.wait_for_timeout(1500)       # a step at the Result data (T3) of a plot stores no table: the trial folder is not needed there
    assert figure(page) != before_figure, "the figure is drawn from the trial: it is another picture"
    page.locator("#trial_discard").click()
    wait_shiny(page)
    expect(page.locator(PANEL)).to_have_count(0, timeout=15_000)
    wait_preview_rows(page, tables["plot"].height, timeout=60_000)
    expect(page.locator("#shown_band_ui")).not_to_contain_text("TRIAL")
    expect(page.locator("#shown_band_ui .spv-shown-band-trial")).to_have_count(0)
    page.wait_for_timeout(1500)
    assert figure(page) == before_figure, "after Discard the figure is the one it was"
    assert trial_files() == [], "Discard empties the trial's folder"
    assert listing(user_data() / "audit_anchors") == audit_files and listing(user_data() / "_sessions") == session_files, "a trial wrote nothing to the audit folder or to a session"
    assert "Discard" not in notices(page), "her own Discard says nothing"


@NEEDS_AUDIT
def test_try_at_a_table_shown_and_the_trial_followed_to_the_plots_it_reaches_and_to_one_it_does_not(ready: Page, tables):
    page = ready
    enter_audit(page)
    show_place(page, "T1:ResFinder", keep_chosen=False)
    wait_preview_rows(page, tables["resfinder"].height, timeout=60_000)
    build_condition(page, "identity", "lt", tables["threshold"])
    assert page.locator("#filter_send_to_audit").count() == 0, "FLOW-3: there is no Send to Audit; a table shown offers Try"
    press_try(page)
    panel = page.locator(PANEL)
    expect(panel).to_be_visible(timeout=60_000)
    removed = tables["resfinder"].height - tables["kept_resfinder"]
    expect(panel).to_contain_text(f"ResFinder: Table, T1: the step removes {removed} rows of {tables['resfinder'].height} here")
    expect(panel).to_contain_text("What these places reach:")
    page.locator(f"{PANEL} summary").click()
    expect(panel).to_contain_text("AMR Heatmap")
    wait_preview_rows(page, tables["kept_resfinder"], timeout=60_000)
    expect(page.locator("#shown_band_ui")).to_contain_text(TRIAL_WORDS)
    assert trial_files(), "a step at a table: the trial's tables are in the trial's own folder"
    page.locator(f"{PANEL} li", has_text="AMR Heatmap").locator("button", has_text="Show").click()      # another item shown while the trial exists: the plot built from the table
    wait_shiny(page)
    expect(page.locator(AREA)).to_contain_text("Plot shown: AMR Heatmap", timeout=30_000)
    expect(page.locator(PANEL)).to_be_visible()
    assert page.locator("#filter_remove_0").count() == 1, "the staged condition is kept while the trial exists"
    wait_preview_rows(page, tables["fresh_plot_after_resfinder_step"], timeout=60_000)   # equal to an audit copy with the step really appended
    expect(page.locator("#shown_band_ui")).to_contain_text(TRIAL_WORDS)
    expect(page.locator(AREA)).to_contain_text(TRIAL_WORDS)
    page.locator(f"{PANEL} li", has_text="ResFinder: Table, T1").locator("button", has_text="Show").first.click()      # and back to the table the step was written at
    wait_shiny(page)
    wait_preview_rows(page, tables["kept_resfinder"], timeout=60_000)
    expect(page.locator(PANEL)).to_be_visible()
    page.locator("#trial_discard").click()
    wait_shiny(page)
    expect(page.locator(PANEL)).to_have_count(0, timeout=15_000)
    assert trial_files() == []


@NEEDS_AUDIT
def test_a_step_that_removes_nothing_says_so_and_the_item_is_not_shown_as_a_trial(ready: Page, tables):
    page = ready
    enter_audit(page)
    wait_preview_rows(page, tables["plot"].height, timeout=60_000)
    build_condition(page, "identity", "ne", -1.0)                                       # no identity is -1, and `!=` keeps the rows with no value: no row goes
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)
    expect(page.locator(PANEL)).to_contain_text("the step removes no row")
    expect(page.locator("#shown_band_ui")).to_contain_text("The step you are trying does not change this.")
    expect(page.locator("#shown_band_ui")).not_to_contain_text(TRIAL_WORDS)
    wait_preview_rows(page, tables["plot"].height, timeout=60_000)
    page.locator("#trial_discard").click()
    wait_shiny(page)


@NEEDS_AUDIT
def test_two_places_chosen_each_has_its_line_and_the_counts_equal_independent_counts(ready: Page, tables):
    page = ready
    enter_audit(page)
    victim = tables["resfinder"]["sample_id"].drop_nulls().unique().sort()[0]
    show_place(page, "T1:ResFinder", keep_chosen=True)
    _line(page, "T1:Quality_metrics").click()                                           # a second place of ANOTHER independent graph: both stay chosen (one place per graph)
    wait_shiny(page)
    expect(page.locator("#lineage_root .spv-lin-chosen")).to_contain_text("Quality")
    build_list_condition(page, "sample_id", "not_in", victim)
    press_try(page)
    panel = page.locator(PANEL)
    expect(panel).to_be_visible(timeout=60_000)
    for name, table in (("ResFinder", tables["resfinder"]), ("Quality metrics", tables["quality"])):
        removed = table.filter(pl.col("sample_id") == victim).height
        line = f"{name}: Table, T1: the step " + (f"removes {removed} row{'' if removed == 1 else 's'} of {table.height} here" if removed else f"removes no row (of {table.height}) here")
        expect(panel).to_contain_text(line)
    page.locator("#trial_discard").click()
    wait_shiny(page)


@NEEDS_AUDIT
def test_a_place_where_the_condition_does_not_fit_is_named_and_nothing_is_tried(ready: Page, tables):
    page = ready
    enter_audit(page)
    show_place(page, "T1:ResFinder", keep_chosen=True)
    _line(page, "T1:Quality_metrics").click()
    wait_shiny(page)
    close_notices(page)
    build_condition(page, "identity", "lt", tables["threshold"])              # `identity` is a column of ResFinder, not of Quality_metrics
    press_try(page)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The condition does not fit every place chosen", timeout=15_000)
    assert "Quality" in notices(page) and "Nothing was tried" in notices(page)
    expect(page.locator(PANEL)).to_have_count(0)
    assert trial_files() == []


@NEEDS_AUDIT
def test_a_selection_that_does_not_hold_the_place_shown_asks_to_show_it_first(ready: Page, tables):
    page = ready
    enter_audit(page)
    _line(page, "T1:MLST").click()                                            # chosen, not shown: the place shown is the plot's Result data
    wait_shiny(page)
    close_notices(page)
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("Show your selection first", timeout=15_000)
    assert "Nothing was tried" in notices(page)
    expect(page.locator(PANEL)).to_have_count(0)


@NEEDS_AUDIT
def test_compare_beside_a_trial_says_which_pane_is_which_and_has_a_switch_for_the_original(ready: Page, tables):
    page = ready
    enter_audit(page)
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)
    set_compare(page, True)
    area = page.locator(AREA)
    expect(page.locator(f"[id='plot_group_{PLOT}_cmp_base']")).to_be_visible(timeout=60_000)
    expect(page.locator(f"#plot_group_{PLOT}")).to_be_visible(timeout=60_000)
    expect(area).to_contain_text("Before this step: no earlier step, so the same as the original", timeout=15_000)
    expect(area).to_contain_text(TRIAL_WORDS)
    expect(page.locator("#trial_left_original")).to_be_attached(timeout=15_000)
    page.locator("#trial_left_original").set_checked(True, force=True)
    wait_shiny(page)
    expect(area).to_contain_text("Original (as read)", timeout=15_000)
    page.locator("#trial_discard").click()
    wait_shiny(page)
    expect(area).to_contain_text("Original (before your audit steps)", timeout=15_000)
    expect(area).to_contain_text("Audited (no steps yet)")
    expect(page.locator("#trial_left_original")).to_have_count(0)
    set_compare(page, False)


@NEEDS_AUDIT
def test_a_trial_ends_with_one_notice_when_the_condition_changes(ready: Page, tables):
    page = ready
    enter_audit(page)
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)
    close_notices(page)
    page.locator("#filter_remove_0").click()
    wait_shiny(page)
    expect(page.locator(PANEL)).to_have_count(0, timeout=15_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The condition changed. The trial ended", timeout=15_000)
    wait_preview_rows(page, tables["plot"].height, timeout=60_000)
    assert trial_files() == []


@NEEDS_AUDIT
def test_a_trial_ends_when_the_places_chosen_change(ready: Page, tables):
    page = ready
    enter_audit(page)
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)
    close_notices(page)
    _line(page, "T1:ResFinder").click()
    wait_shiny(page)
    expect(page.locator(PANEL)).to_have_count(0, timeout=15_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The places chosen changed. The trial ended", timeout=15_000)
    assert trial_files() == []


@NEEDS_AUDIT
def test_a_trial_ends_when_audit_mode_is_left_and_its_folder_is_emptied(ready: Page, tables):
    page = ready
    enter_audit(page)
    show_place(page, "T1:ResFinder", keep_chosen=False)                                 # a step at a table stores tables: the trial's folder holds files
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)
    assert trial_files()
    close_notices(page)
    set_mode(page, "exploration")
    expect(page.locator("#shiny-notification-panel")).to_contain_text("You left Audit mode. The trial ended", timeout=15_000)
    assert trial_files() == [], "leaving Audit mode empties the trial's folder"
    set_mode(page, "audit")
    expect(page.locator(PANEL)).to_have_count(0, timeout=15_000)
    wait_preview_rows(page, tables["plot"].height, timeout=60_000)                      # the original again, nothing of the trial


@NEEDS_AUDIT
def test_nothing_of_a_trial_is_in_an_export_a_session_or_a_stored_audited_table(ready: Page, tables):
    page = ready
    enter_audit(page)
    build_condition(page, "identity", "lt", tables["threshold"])
    audit_files, session_files = listing(user_data() / "audit_anchors"), listing(user_data() / "_sessions")
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)
    wait_preview_rows(page, tables["kept_plot"], timeout=60_000)
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion .accordion-button", has_text="Export").first.click()
        _wait_shiny(page)
    page.locator("#export_user_name").fill("try")
    with page.expect_download(timeout=180_000) as info:
        page.locator("#export_bundle_download").click()
    z = zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))
    names = z.namelist()
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "the export was refused"
    assert not [n for n in names if "_audited" in n or "/audit_recipe/" in n], [n for n in names if "_audited" in n or "/audit_recipe/" in n]
    for n in names:
        if n.endswith((".txt", ".qmd", ".yaml", ".md")):
            assert "TRIAL" not in z.read(n).decode(errors="ignore"), f"{n} mentions the trial"
    plot_file = next(n for n in names if n.endswith(f"/T3_data_{PLOT}.tsv"))
    assert len(z.read(plot_file).decode().strip().splitlines()) - 1 == tables["plot"].height, "the data file of the plot is the original table: the trial is not in it"
    table_file = next(n for n in names if n.endswith("/ResFinder/T1_data.tsv"))
    assert len(z.read(table_file).decode().strip().splitlines()) - 1 == tables["resfinder"].height, "the table file is the original table"
    assert listing(user_data() / "audit_anchors") == audit_files, "the audit folder is byte for byte what it was"
    assert listing(user_data() / "_sessions") == session_files, "no session file was written"
    page.locator("#trial_discard").click()
    wait_shiny(page)


@pytest.mark.skipif(LAUNCH != "pipeline-exploration-simple", reason="run with SPARMVET_APP_FEATURES=pipeline-exploration-simple")
def test_without_the_audit_there_is_no_try(page: Page, shiny_app: ShinyAppProc):
    page.goto(shiny_app.url)                          # this app features file hides the recipe selector: the recipe is named by SPARMVET_DATA_ANALYSIS_RECIPE
    page.wait_for_selector("#nav_accordion", timeout=30_000)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=120_000)
    _wait_shiny(page)
    _open_filters_panel(page)
    page.locator("#filter_add_row").wait_for(state="attached", timeout=30_000)
    assert page.locator("#filter_try").count() == 0 and page.locator("#trial_discard").count() == 0
    expect(page.locator(".spv-trial-panel")).to_have_count(0)


@NEEDS_AUDIT
def test_a_condition_built_on_one_table_is_never_tried_at_another(ready: Page, tables):
    """FLOW-1 review: build on ResFinder (T1), Try, Show the plot built from it (the trial keeps the staged condition), press Try again: refused with one plain
    line, no new trial, no step. The condition belongs to the table it was built on."""
    page = ready
    enter_audit(page)
    show_place(page, "T1:ResFinder", keep_chosen=False)
    wait_preview_rows(page, tables["resfinder"].height, timeout=60_000)
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)
    page.locator(f"{PANEL} summary").click()
    page.locator(f"{PANEL} li", has_text="AMR Heatmap").locator("button", has_text="Show").click()
    wait_shiny(page)
    expect(page.locator(AREA)).to_contain_text("Plot shown: AMR Heatmap", timeout=30_000)
    assert page.locator("#filter_remove_0").count() == 1, "the trial keeps the staged condition (the premise of the trace)"
    close_notices(page)
    expect(page.locator("#filter_try")).to_be_visible(timeout=15_000)
    page.locator("#filter_try").click()
    wait_shiny(page)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("built on another table", timeout=15_000)
    assert "Nothing was tried" in notices(page)
    assert page.locator("[id^='t3_delete_']").count() == 0, "no step was written"
    page.locator("#trial_discard").click()
    wait_shiny(page)
