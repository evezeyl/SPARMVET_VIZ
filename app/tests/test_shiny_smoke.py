"""test_shiny_smoke.py — headless Playwright smoke tests for SPARMVET_VIZ.

Run (full suite, qa app features):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa .venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v

Run (developer app features — tests Gallery visibility):
    PYTHONPATH=. SPARMVET_APP_FEATURES=developer .venv/bin/python -m pytest app/tests/test_shiny_smoke.py::TestAppFeaturesMasking -v

Tests are grouped into four tiers:
  T1 — App startup and data analysis recipe load (always fast, always run)
  T2 — App features masking (sidebar nav visibility for the active launch app features)
  T3 — Filter pipeline + T3 audit promotion (highest-risk refactor surface)
  T4 — Data preview grid

Note on app features switching: the app app features is set at launch via SPARMVET_APP_FEATURES env var.
There is no runtime `#app_features_selector` dropdown; runtime switching is not currently wired
to a rendered input. T2 tests reflect the LAUNCH app features only.

The `qa` app features is recommended for CI (ghost_save OFF = deterministic).
"""

import os
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wait_shiny(page: Page, timeout: int = 10_000) -> None:
    """Wait for Shiny to finish all reactive computations (busy indicator clears)."""
    page.wait_for_function(
        "() => !document.documentElement.classList.contains('shiny-busy')",
        timeout=timeout
    )


def _wait_for_fb_col_option(page: Page, value: str, timeout: int = 20_000) -> None:
    """Wait until a specific option appears in #fb_col before selecting it.

    filter_form_ui re-renders after active_home_subtab changes, but the columns
    come from a LazyFrame scan of the target dataset parquet. On first navigation
    to a plot, that parquet may not yet exist — the orchestrator materialises it
    asynchronously, then filter_form_ui re-renders with real columns. This helper
    waits for the option to be present rather than racing against materialisation.
    """
    js = (
        f"() => Array.from(document.querySelectorAll('#fb_col option'))"
        f".some(o => o.value === '{value}')"
    )
    page.wait_for_function(js, timeout=timeout)


def _load_data_analysis_recipe(page: Page, base_url: str, data_analysis_recipe_id: str = "1_test_data_ST22_dummy") -> None:
    """Navigate to app, select the test data analysis recipe, and wait for groups to render.

    If the data analysis recipe is already loaded (Quality Control nav visible), skips navigation
    so tests sharing a module-scoped page don't each trigger a fresh Shiny session
    and re-run T1 materialization.
    """
    qc = page.locator(".nav-link:has-text('Quality Control')")
    if qc.count() > 0 and qc.is_visible():
        _wait_shiny(page)
        return
    page.goto(base_url)
    page.wait_for_selector("#data_analysis_recipe_id", timeout=20_000)
    page.locator("#data_analysis_recipe_id").select_option(data_analysis_recipe_id)
    # Wait for dynamic_tabs group nav pills — the first group in 1_test_data_ST22_dummy
    # is "Quality Control". This is the slowest step
    # (tier1 materialization + dynamic_tabs render). 60s covers cold-start scenarios.
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=60_000)
    _wait_shiny(page)


def _navigate_to_phenotype_plot(page: Page) -> None:
    """Navigate to the Curiosity group -> phenotype_genome_length_fragmentation plot
    (the only plot in 1_test_data_ST22_dummy with an inline jitter layer and no
    recipe-pinned random_state — REPRO-RESHUFFLE-1, #49)."""
    curiosity_tab = page.locator(".nav-link:has-text('Curiosity')")
    if curiosity_tab.count() == 0:
        pytest.skip("Curiosity group tab not found in active data analysis recipe")
    curiosity_tab.first.click()
    _wait_shiny(page)
    plot_tab = page.locator(".nav-link:has-text('Phenotype Genome Length Fragmentation')")
    if plot_tab.count() > 0:
        plot_tab.first.click()
        _wait_shiny(page)


def _navigate_to_mlst_plot(page: Page) -> None:
    """Navigate to the AMR/Virulence group → mlst_bar plot (has 'year' numeric column).

    Group label: "💊 AMR and ☠️ Virulence" (from data analysis recipe description field).
    Plot tab: "Mlst Bar" (from p_id.replace("_"," ").title() in dynamic_tabs).
    If navigation fails the caller should skip — this is dataset-specific.
    """
    # Group tab label comes from data analysis recipe description field (home_theater.py L709)
    # Use :has-text for emoji-containing labels (role matching can fail on emoji)
    amr_tab = page.locator(".nav-link:has-text('AMR')")
    if amr_tab.count() == 0:
        pytest.skip("AMR group tab not found in active data analysis recipe")
    amr_tab.first.click()
    _wait_shiny(page)
    # Plot tab label = p_id.replace("_"," ").title() when no explicit label
    mlst_tab = page.locator(".nav-link:has-text('Mlst Bar')")
    if mlst_tab.count() > 0:
        mlst_tab.first.click()
        _wait_shiny(page)


def _no_render_error(page: Page) -> None:
    """Assert no visible 'Render error' or Python traceback on the page."""
    body = page.locator("body").inner_text(timeout=5_000)
    assert "Render error" not in body, f"Render error found on page:\n{body[:500]}"
    assert "Traceback" not in body, f"Python traceback found on page:\n{body[:500]}"


def _open_filters_panel(page: Page) -> None:
    """Expand the Filters accordion panel in the left sidebar.

    The accordion initialises with only 'Data analysis recipe Choice' open (home_theater.py).
    The 'Filters' panel only renders when interactivity_enabled=true (developer/qa
    app features) and is collapsed by default — clicking the header expands it so
    #filter_add_row becomes visible.
    """
    if page.locator("#filter_add_row").is_visible():
        return
    page.locator("#nav_accordion").get_by_text("Filters").first.click()
    page.wait_for_selector("#filter_add_row", timeout=8_000)
    _wait_shiny(page)


# ---------------------------------------------------------------------------
# T1 — Startup
# ---------------------------------------------------------------------------

class TestStartup:
    def test_app_loads(self, page: Page, shiny_app: ShinyAppProc):
        """App responds and shows the project selector."""
        page.goto(shiny_app.url)
        expect(page.locator("#data_analysis_recipe_id")).to_be_visible(timeout=15_000)

    def test_no_startup_errors(self, page: Page, shiny_app: ShinyAppProc):
        """No Python traceback or render errors at startup."""
        page.goto(shiny_app.url)
        page.wait_for_load_state("networkidle", timeout=15_000)
        _no_render_error(page)

    def test_data_analysis_recipe_load(self, page: Page, shiny_app: ShinyAppProc):
        """Loading the data analysis recipe renders at least one navigation link."""
        _load_data_analysis_recipe(page, shiny_app.url)
        _no_render_error(page)
        tabs = page.locator(".nav-link").all()
        assert len(tabs) > 0, "No navigation tabs found after data analysis recipe load"


# ---------------------------------------------------------------------------
# T2 — App features masking (tests the LAUNCH app features only — no runtime switching)
# ---------------------------------------------------------------------------

class TestAppFeaturesMasking:
    def test_sidebar_nav_renders(self, page: Page, shiny_app: ShinyAppProc):
        """sidebar_nav_ui renders and shows the Home tab for any app features."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        expect(page.locator("#sidebar_nav")).to_be_visible()

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in ("developer", "qa"),
        reason="Gallery only visible for developer/qa app features"
    )
    def test_developer_sees_gallery(self, page: Page, shiny_app: ShinyAppProc):
        """developer/qa app features: Gallery tab is visible in sidebar nav."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        expect(page.get_by_text("Gallery")).to_be_visible()

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in ("pipeline-static",),
        reason="Right sidebar hidden only for pipeline-static"
    )
    def test_static_hides_right_sidebar(self, page: Page, shiny_app: ShinyAppProc):
        """pipeline-static app features: right sidebar container excluded from DOM (ADR-052-§1)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        # Container must be absent — not just empty. A present container still occupies 340px.
        assert page.locator("#audit_sidebar").count() == 0, \
            "Right sidebar container (#audit_sidebar) should be absent from DOM for pipeline-static"

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in ("pipeline-exploration-simple", "pipeline-static"),
        reason="Gallery/DevStudio visible for advanced+ app features files"
    )
    def test_simple_hides_gallery_and_devstudio(self, page: Page, shiny_app: ShinyAppProc):
        """pipeline-exploration-simple: no Gallery, no Test Lab."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        expect(page.get_by_text("Gallery")).not_to_be_visible()
        expect(page.get_by_text("Test Lab")).not_to_be_visible()


# ---------------------------------------------------------------------------
# T3 — Filter pipeline (highest-risk refactor surface)
# ---------------------------------------------------------------------------

class TestFilterPipeline:
    def test_filter_form_renders(self, page: Page, shiny_app: ShinyAppProc):
        """Filter sidebar renders with Add Row button after data analysis recipe load and panel open."""
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        expect(page.locator("#filter_add_row")).to_be_visible()

    def test_add_filter_row(self, page: Page, shiny_app: ShinyAppProc):
        """Clicking Add Row with year > 2000 produces a pending filter row.

        Navigates to Results → mlst_bar first (MLST_with_metadata has 'year').
        Note: filter contract correctness is in test_filter_operators.py (21 cases).
        This smoke test verifies the reactive wiring survives the refactor.
        """
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
        # MLST_with_metadata parquet may not be ready on first navigation — wait
        # for the filter column picker to include "year" before selecting it.
        _wait_for_fb_col_option(page, "year")
        page.locator("#fb_col").select_option("year")
        _wait_shiny(page)
        page.locator("#fb_op").select_option("gt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("2000")
        page.wait_for_timeout(200)
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)

    def test_apply_filter_no_crash(self, page: Page, shiny_app: ShinyAppProc):
        """Applying a pending filter does not produce a render error."""
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        page.locator("#fb_col").select_option(index=1)
        page.wait_for_timeout(300)
        page.locator("#filter_add_row").click()
        page.wait_for_timeout(500)
        page.locator("#filter_apply").click()
        page.wait_for_timeout(1_500)
        _no_render_error(page)

    def test_filter_reset_clears_rows(self, page: Page, shiny_app: ShinyAppProc):
        """Resetting filters clears pending rows (filter_remove_0 disappears)."""
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
        # MLST_with_metadata parquet may not be ready on first navigation — wait
        # for the filter column picker to include "year" before selecting it.
        _wait_for_fb_col_option(page, "year")
        page.locator("#fb_col").select_option("year")
        _wait_shiny(page)
        page.locator("#fb_op").select_option("gt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("2000")
        page.wait_for_timeout(200)
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)
        page.locator("#filter_reset").click()
        _wait_shiny(page)
        expect(page.locator("#filter_remove_0")).not_to_be_visible()


# ---------------------------------------------------------------------------
# T4-B — The Apply gate (AUDIT-GATE-UI-1): a T3 node with no reason blocks
# btn_apply ("Apply ⛔"); filling the reason unblocks it ("Apply"). Replaces
# the removed test_reactive_shell.py::test_reactive_audit_gate — the gate
# LOGIC is already covered by test_session_manager.py::test_gatekeeper_blocked,
# this is the UI-level wiring check.
# ---------------------------------------------------------------------------

class TestAuditGate:
    def test_unreasoned_node_blocks_apply_then_reason_unblocks_it(
            self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)

        # Switch to "My view" (T3) — Send to Audit only renders there.
        page.locator("#tier_toggle input[value=T3]").check(force=True)
        _wait_shiny(page)

        _wait_for_fb_col_option(page, "year")
        page.locator("#fb_col").select_option("year")
        _wait_shiny(page)
        page.locator("#fb_op").select_option("gt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("2000")
        page.wait_for_timeout(200)
        page.locator("#filter_add_row").click()
        _wait_shiny(page)

        page.locator("#filter_send_to_audit").click()
        _wait_shiny(page)
        # Propagation modal: accept the default scope ("this plot only").
        page.locator("#propagation_confirm").click()
        _wait_shiny(page)

        apply_btn = page.locator("#btn_apply, #audit_stack_tools_ui #btn_apply").first
        expect(apply_btn).to_have_text("Apply ⛔", timeout=8_000)
        expect(apply_btn).to_be_disabled()

        reason_input = page.locator('input[id^="t3_reason_"]').first
        expect(reason_input).to_be_visible(timeout=8_000)
        reason_input.fill("Test: dropping pre-2000 samples for AUDIT-GATE-UI-1.")
        _wait_shiny(page)

        expect(apply_btn).to_have_text("Apply", timeout=8_000)
        expect(apply_btn).to_be_enabled()


# ---------------------------------------------------------------------------
# T4-C — HOM-08 (Eve, 2026-11-08): the "Plot to show" / "Data to show" strip
# used a hardcoded selected="T2" default every time dynamic_tabs re-rendered
# for any reason — including a workspace switch — silently discarding
# whatever the user had actually picked. Fixed with an isolated read of the
# current input value (same pattern as the existing active-tab restoration).
# ---------------------------------------------------------------------------

class TestTierPersistence:
    def test_tier_survives_a_workspace_switch(self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        page.wait_for_selector("#tier_toggle", timeout=15_000)

        page.locator("#tier_toggle input[value=T3]").check(force=True)
        _wait_shiny(page)
        expect(page.locator("#tier_toggle input[value=T3]")).to_be_checked()

        page.get_by_text("Gallery", exact=True).click()
        _wait_shiny(page)
        page.get_by_text("Home", exact=True).click()
        _wait_shiny(page)

        page.wait_for_selector("#tier_toggle", timeout=15_000)
        expect(page.locator("#tier_toggle input[value=T3]")).to_be_checked(timeout=8_000)


class TestNoJoinsRecipe:
    """A data analysis recipe with no joins: block at all (plots target a bare data schema
    directly) used to fail HOME with "Data Assembly Failed: No assembly or data_schema
    'Untitled_Collection' found" (issue #24, Eve, 2026-11-08: "If there is no join in the
    recipe then well there is just no join. The plots can just be made by data that are not
    joined with anything else."). Fixed in active_collection_id() (app/src/server.py) —
    falls back to the first plot's bare target_dataset instead of the placeholder string,
    which materialize_tier1's Path A does recognise as a real dataset id."""

    def test_plots_render_without_a_join(self, page: Page, shiny_app: ShinyAppProc):
        # Load a different recipe first and deliberately wait it out — a leftover plot
        # image from this recipe must not let a loose "any .shiny-plot-output img exists"
        # assertion pass vacuously once we switch to the no-joins recipe below.
        page.goto(shiny_app.url)
        page.wait_for_selector("#data_analysis_recipe_id", timeout=20_000)
        page.locator("#data_analysis_recipe_id").select_option("1_test_data_ST22_dummy")
        _wait_shiny(page)
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=20_000)

        page.locator("#data_analysis_recipe_id").select_option("3_test_no_joins")
        _wait_shiny(page)
        page.wait_for_timeout(1_000)  # let a failed assembly's error banner actually land

        expect(page.get_by_text("Data Assembly Failed", exact=False)).to_have_count(0)
        # Content unique to this recipe — can't be satisfied by a stale image left over
        # from the previous recipe the way a bare ".shiny-plot-output img" check could.
        expect(page.get_by_role("tab", name="No Joins")).to_be_visible(timeout=8_000)
        expect(page.get_by_text("Sequence Type Counts", exact=False).first).to_be_visible(timeout=8_000)
        expect(page.locator(".shiny-plot-output img").first).to_be_visible(timeout=8_000)

        page.locator("#data_analysis_recipe_id").select_option("1_test_data_ST22_dummy")
        _wait_shiny(page)


class TestRecipeSwitchPlotRender:
    """A data analysis recipe switch leaves the first plot sub-tab blank until clicked (found by
    Eve, 2026-11-08): `plots_card`'s selected= passed the OLD recipe's saved sub-tab id
    unconditionally, even when it matches none of the new recipe's plot_ids — so Bootstrap/Shiny
    never marks any pane genuinely active server-side. Fixed by guarding it the same way the
    outer group-level selected=_saved_group was already guarded."""

    def test_first_plot_renders_without_a_click_after_recipe_switch(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        # Deliberately NOT using _load_data_analysis_recipe's shared-session reuse — this
        # test needs a known-clean starting state (no stale active_plot_subtab from
        # whatever an earlier test in this module-scoped page left behind), so it does
        # its own fresh page.goto() regardless of where it runs in the file.
        page.goto(shiny_app.url)
        page.wait_for_selector("#data_analysis_recipe_id", timeout=20_000)
        page.locator("#data_analysis_recipe_id").select_option("1_test_data_ST22_dummy")
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=20_000)
        _wait_shiny(page)
        page.get_by_text("Qc Reads Horizontal Barplot", exact=False).first.click()
        _wait_shiny(page)

        page.locator("#data_analysis_recipe_id").select_option("1_Abromics_general_pipeline")
        _wait_shiny(page)
        # No tab click here — the bug was that the plot stayed blank indefinitely without one.
        expect(page.locator(".shiny-plot-output img").first).to_be_visible(timeout=8_000)

        # Leave the shared page back on the suite's default recipe so later tests in
        # this module aren't affected by this test's recipe switch. Found live, 2026-11-10:
        # 1_Abromics_general_pipeline ALSO has a "Quality Control" group, so
        # _load_data_analysis_recipe's shared-session shortcut (checks only that the
        # "Quality Control" nav-link is visible) can't tell the two recipes apart — a
        # later test that relies on that shortcut can run against the wrong recipe if
        # this restore is still in flight. Wait for the selector's own value, not just a
        # tab label both recipes share.
        page.locator("#data_analysis_recipe_id").select_option("1_test_data_ST22_dummy")
        expect(page.locator("#data_analysis_recipe_id")).to_have_value("1_test_data_ST22_dummy")
        # Wait for a plot sub-tab name unique to ST22 dummy (not just "Quality Control",
        # which both recipes have) — proof the DOM actually switched, not just the <select>.
        page.wait_for_selector("text=Qc Reads Horizontal Barplot", timeout=20_000)
        _wait_shiny(page)


# ---------------------------------------------------------------------------
# T5 — Phase 25 sidebar panels (accordion structure, ADR-052)
# ---------------------------------------------------------------------------

_PIPELINE_APP_FEATURES = {"pipeline-static", "pipeline-exploration-simple"}
_INTERACTIVE_APP_FEATURES = {"pipeline-exploration-advanced", "standalone",
                         "developer", "qa"}


class TestPhase25Panels:
    def test_accordion_renders(self, page: Page, shiny_app: ShinyAppProc):
        """#nav_accordion is present after startup (Phase 25-E accordion structure)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        expect(page.locator("#nav_accordion")).to_be_visible()

    def test_data_import_panel_visible_for_exploration_app_features(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """Data Import accordion panel is present for interactive/exploration app features files.

        For exploration app features files (developer, qa, advanced, independent),
        the panel shows upload controls in addition to the source-file listing.
        Phase 25-F wiring: data_import_ui output is registered and renders.
        """
        if _LAUNCH_APP_FEATURES in _PIPELINE_APP_FEATURES:
            pytest.skip("Data Import upload controls absent for pipeline app features files")
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Data Import")).to_be_visible()

    def test_info_panel_shows_the_info_block_of_the_open_data_analysis_recipe(self, page: Page, shiny_app: ShinyAppProc):
        """The Info panel lists what is written under info: of the open data analysis recipe, and opening
        a data analysis recipe does not rebuild the sidebar (the Filters and Export panels keep working)."""
        _load_data_analysis_recipe(page, shiny_app.url)
        accordion = page.locator("#nav_accordion")
        accordion.get_by_text("Info", exact=True).first.click()
        expect(page.locator("#data_analysis_recipe_info_ui")).to_contain_text("ST22 Dummy Dataset")
        expect(page.locator("#data_analysis_recipe_info_ui")).to_contain_text("version")

    def test_test_lab_left_sidebar_shows_only_its_own_panels(self, page: Page, shiny_app: ShinyAppProc):
        """Test Lab's left sidebar comes from testlab_standard_left.yaml (Info only), not from
        Home's slot list. Before the fix (finding F-01, .claude/tasks/uml_findings.md), switching
        to Test Lab fell through to bootloader.get_sidebar_config("home", "left") and showed the
        full Home panel set — Filters, Export, Session Management — which have no meaning there."""
        if _LAUNCH_APP_FEATURES not in {"developer", "qa"}:
            pytest.skip("Test Lab is only enabled for developer and qa app features")
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        page.locator("#sidebar_nav").get_by_text("Test Lab").first.click()
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Info", exact=True)).to_be_visible()
        expect(accordion.get_by_text("Filters", exact=True)).not_to_be_visible()
        expect(accordion.get_by_text("Export", exact=True)).not_to_be_visible()
        expect(accordion.get_by_text("Session Management", exact=True)).not_to_be_visible()
        expect(accordion.get_by_text("Data analysis recipe Choice", exact=True)).not_to_be_visible()

    def test_test_lab_right_sidebar_shows_the_tool_descriptions(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """Regression guard for issue #55 (2026-11-10): Test Lab's right sidebar was
        structurally present-but-empty (testlab_standard_right.yaml: visible:false, panels:[])
        from 2026-11-08 until this fix, even though the content
        (_render_test_lab_right_info, home_theater.py) had existed the whole time — nothing
        caught the gap because nothing asserted the right sidebar had content for Test Lab.
        Checks it shows the 5 tool names, not just that the container exists."""
        if _LAUNCH_APP_FEATURES not in {"developer", "qa"}:
            pytest.skip("Test Lab is only enabled for developer and qa app features")
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        page.locator("#sidebar_nav").get_by_text("Test Lab").first.click()
        page.wait_for_selector("#audit_sidebar", timeout=15_000)
        right = page.locator("#audit_sidebar")
        for tool_name in (
            "ID Reconciliation", "Data analysis recipe Scaffolding",
            "Synthetic Data", "Anonymisation", "File Reformatting",
        ):
            expect(right.get_by_text(tool_name, exact=True)).to_be_visible()

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in ("developer", "qa"),
        reason="Test Lab is only enabled for developer and qa app features",
    )
    def test_test_lab_info_panel_shows_a_placeholder_not_a_recipe(self, page: Page, shiny_app: ShinyAppProc):
        """Test Lab's Info panel (test_lab_info, not data_analysis_recipe_info) must show its own
        placeholder text and never the open data analysis recipe's info: block (issue #33, Eve,
        2026-11-08: "it should be empty because we can fill it with instructions later, but it
        should not display the recipe instructions as there are no recipes in the test lab")."""
        _load_data_analysis_recipe(page, shiny_app.url)
        page.locator("#sidebar_nav").get_by_text("Test Lab").first.click()
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        accordion.get_by_text("Info", exact=True).first.click()
        expect(accordion).to_contain_text("instructions coming soon")
        expect(accordion).not_to_contain_text("ST22 Dummy Dataset")

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in ("developer", "qa"),
        reason="Gallery only visible for developer/qa app features",
    )
    def test_gallery_left_sidebar_shows_alerts(self, page: Page, shiny_app: ShinyAppProc):
        """Alerts (notification_log) moved to Gallery's LEFT sidebar, 2026-11-08 (issue #33):
        Gallery's right sidebar is mostly empty/reserved for future modules, and alerts must
        stay reachable there regardless (same reasoning as Home's earlier fix)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
        page.wait_for_selector("#gallery_sidebar_accordion", timeout=15_000)
        expect(page.locator("#sidebar_tools_ui #notification_log_panel_ui")).to_be_visible()
        assert page.locator("#audit_sidebar #notification_log_panel_ui").count() == 0, \
            "Alerts must not also render in the right sidebar (no duplicate DOM id, REG-10)"

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in ("developer", "qa"),
        reason="Blueprint only visible for developer/qa app features",
    )
    def test_blueprint_left_sidebar_shows_alerts(self, page: Page, shiny_app: ShinyAppProc):
        """Alerts (notification_log) moved to Blueprint's LEFT sidebar, 2026-11-08 (issue #33):
        Blueprint's own left/right panels keep their existing, distinct layout (Eve: "they have
        their own specificity... I do not see what is the problem") — only the alerts placement
        changed, matching Home/Gallery/Test Lab."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        page.locator("#sidebar_nav").get_by_text("Blueprint Architect").first.click()
        page.wait_for_selector("#wrangle_sidebar_accordion", timeout=20_000)
        expect(page.locator("#sidebar_tools_ui #notification_log_panel_ui")).to_be_visible()
        assert page.locator("#audit_sidebar #notification_log_panel_ui").count() == 0, \
            "Alerts must not also render in the right sidebar (no duplicate DOM id, REG-10)"

    def test_global_export_panel_visible(self, page: Page, shiny_app: ShinyAppProc):
        """Export/Import accordion panel is always present (renamed from 'Global Export' in
        export redesign 2026-05-04; renamed again 'Export' -> 'Export / Import' issue #54)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Export / Import")).to_be_visible()

    def test_import_a_bundle_block_is_findable_above_export_form(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """Regression guard for issue #54 (found live, twice, 2026-11-10): a bundle-import
        control that merely *exists in the DOM* passed every structural test while still being
        practically unfindable, buried below ~10 export-form fields. This asserts the thing a
        human actually experiences: opening the panel, "Import a bundle" is the first heading
        seen, strictly above "Bundle label / name" (the first field of the Export form) in
        vertical position -- not just present somewhere in the accordion panel."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        accordion.get_by_text("Export / Import", exact=True).click()
        import_heading = page.get_by_text("Import a bundle", exact=False)
        export_heading = page.get_by_text("Bundle label / name", exact=False)
        expect(import_heading).to_be_visible()
        expect(export_heading).to_be_visible()
        import_box = import_heading.bounding_box()
        export_box = export_heading.bounding_box()
        assert import_box["y"] < export_box["y"], (
            f"'Import a bundle' (y={import_box['y']}) must appear above "
            f"'Bundle label / name' (y={export_box['y']}) -- it regressed back to being "
            "buried below the export form."
        )

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in ("pipeline-static", "pipeline-exploration-simple"),
        reason="Data analysis recipe Choice only absent for pipeline app features files"
    )
    def test_data_analysis_recipe_choice_hidden_for_pipeline_static(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """pipeline-static/simple: Data analysis recipe Choice panel excluded from accordion DOM.

        data_analysis_recipe_selector.visible=false means the panel is never added to the
        accordion panels list — it is structurally absent, not just CSS-hidden.
        """
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        assert accordion.get_by_text("Data analysis recipe Choice").count() == 0, \
            "Data analysis recipe Choice panel should be absent from accordion for pipeline app features files"

    @pytest.mark.skipif(
        _LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
        reason="Session Management panel only present for interactive app features files"
    )
    def test_session_management_panel_visible(self, page: Page, shiny_app: ShinyAppProc):
        """Session Management accordion panel present for interactive app features files (Phase 25-G)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Session Management")).to_be_visible()


# ---------------------------------------------------------------------------
# HOM-53/HOM-54 — Session list refresh without reload + bulk delete
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    _LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
    reason="Session Management panel only present for interactive app features files"
)
class TestSessionListRefresh:
    """Seeds real session ghosts under the same `user_data` location the test app's
    own local-dev deployment resolves to (tmp/UI_TEST/user/), then drives the panel
    through the browser. Matches the production path: app/src/server.py builds
    SessionManager(bootloader.get_location("user_data"))."""

    def _make_session_manager(self):
        from app.src.bootloader import bootloader
        from app.modules.session_manager import SessionManager
        return SessionManager(bootloader.get_location("user_data"))

    def _seed_session(self, sm, tmp_path, label: str):
        from app.modules.session_manager import SessionManager
        recipe = tmp_path / f"{label}.yaml"
        recipe.write_text(
            f"id: {label}\n"
            "analysis_groups:\n  g:\n    label: G\n    plots:\n      p:\n        label: P\n"
            "        spec:\n          target_dataset: C\n          mapping: {x: a}\n"
            "          layers:\n            - name: geom_bar\n"
        )
        data = tmp_path / f"{label}.tsv"
        data.write_text("a\tb\n1\t2\n")
        msig = SessionManager.compute_data_analysis_recipe_sha256(recipe)
        dbh = SessionManager.compute_data_batch_hash({"d": data})
        key = SessionManager.compute_session_key(msig, dbh)
        sm.write_assembly_ghost(key, label, msig, dbh, {"d": str(data)}, {})
        return key

    def _open_session_group(self, page: Page, label: str) -> None:
        """Sessions are grouped by data_analysis_recipe_id in a nested accordion
        (session_groups_accordion, 📁 {id}) — expand the group our seeded session
        belongs to before looking for its Delete button."""
        page.wait_for_selector("#session_groups_accordion", timeout=10_000)
        group_header = page.locator("#session_groups_accordion").get_by_text(f"📁 {label}", exact=False).first
        group_header.click()
        _wait_shiny(page)

    def test_delete_one_session_refreshes_without_reload(self, page: Page, shiny_app: ShinyAppProc, tmp_path):
        sm = self._make_session_manager()
        key = self._seed_session(sm, tmp_path, "hom53_single")
        try:
            page.goto(shiny_app.url)
            page.wait_for_selector("#nav_accordion", timeout=15_000)
            page.locator("#nav_accordion").get_by_text("Session Management").first.click()
            _wait_shiny(page)
            self._open_session_group(page, "hom53_single")

            safe_sk = key.replace(":", "_")
            delete_btn = page.locator(f"#session_delete_{safe_sk}")
            expect(delete_btn).to_be_visible(timeout=10_000)

            delete_btn.click()
            _wait_shiny(page)

            # No page.reload() — the fix is that the panel re-renders on its own.
            expect(page.locator(f"#session_delete_{safe_sk}")).to_have_count(0, timeout=8_000)
        finally:
            sm.delete_session(key)

    def test_delete_all_sessions_requires_confirm_then_clears_list(self, page: Page, shiny_app: ShinyAppProc, tmp_path):
        sm = self._make_session_manager()
        key_a = self._seed_session(sm, tmp_path, "hom54_a")
        key_b = self._seed_session(sm, tmp_path, "hom54_b")
        try:
            page.goto(shiny_app.url)
            page.wait_for_selector("#nav_accordion", timeout=15_000)
            page.locator("#nav_accordion").get_by_text("Session Management").first.click()
            _wait_shiny(page)
            self._open_session_group(page, "hom54_a")
            self._open_session_group(page, "hom54_b")

            expect(page.locator(f"#session_delete_{key_a.replace(':', '_')}")).to_be_visible(timeout=10_000)
            expect(page.locator(f"#session_delete_{key_b.replace(':', '_')}")).to_be_visible(timeout=10_000)

            page.locator("#session_delete_all_btn").click()
            _wait_shiny(page)

            # Confirm modal must appear — delete-all is gated, not immediate.
            confirm_btn = page.locator("#session_delete_all_confirm")
            expect(confirm_btn).to_be_visible(timeout=8_000)

            confirm_btn.click()
            _wait_shiny(page)

            expect(page.locator(f"#session_delete_{key_a.replace(':', '_')}")).to_have_count(0, timeout=8_000)
            expect(page.locator(f"#session_delete_{key_b.replace(':', '_')}")).to_have_count(0, timeout=8_000)
        finally:
            sm.delete_session(key_a)
            sm.delete_session(key_b)

    def test_session_label_saves_on_blur(self, page: Page, shiny_app: ShinyAppProc, tmp_path):
        """REPRO-SESSION-LABELS-1 (#50): typing a description and clicking away saves
        it — no separate Save button, and no session_list_version bump needed (the
        box already shows what was typed)."""
        sm = self._make_session_manager()
        key = self._seed_session(sm, tmp_path, "hom50_label")
        try:
            assert sm.get_session_label(key) == ""  # fresh session, never labelled

            page.goto(shiny_app.url)
            page.wait_for_selector("#nav_accordion", timeout=15_000)
            page.locator("#nav_accordion").get_by_text("Session Management").first.click()
            _wait_shiny(page)
            self._open_session_group(page, "hom50_label")

            safe_sk = key.replace(":", "_")
            label_input = page.locator(f"#session_label_input_{safe_sk}")
            expect(label_input).to_be_visible(timeout=10_000)

            label_input.fill("ST22 outbreak analysis, dataset batch Jan2025")
            label_input.press("Tab")  # update_on="blur" — only commits once focus leaves
            _wait_shiny(page)

            assert sm.get_session_label(key) == "ST22 outbreak analysis, dataset batch Jan2025"
        finally:
            sm.delete_session(key)


# ---------------------------------------------------------------------------
# Reshuffle control (REPRO-RESHUFFLE-1, #49)
# ---------------------------------------------------------------------------

class TestReshuffleControl:
    """The module-scoped page is shared with every other class in this file (same
    convention TestViewBadges documents): navigating to the Curiosity group here must
    not leave later tests (e.g. TestViewBadges._open_plot, which assumes Quality
    Control is the active group) stranded on a tab their own locators can't see."""

    def _restore_to_quality_control(self, page: Page) -> None:
        qc_tab = page.locator(".nav-link:has-text('Quality Control')")
        if qc_tab.count() > 0:
            qc_tab.first.click()
            _wait_shiny(page)

    def test_shown_on_a_jitter_plot_with_no_pinned_seed(self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        _navigate_to_phenotype_plot(page)
        try:
            expect(
                page.locator("#plot_reshuffle_btn_phenotype_genome_length_fragmentation")
            ).to_be_visible(timeout=10_000)
        finally:
            self._restore_to_quality_control(page)

    def test_absent_on_a_plot_with_no_jitter_layer(self, page: Page, shiny_app: ShinyAppProc):
        """Quality Control's assembly_quality_dotplot has no jitter layer at all —
        the control must not render there. Already ends on Quality Control."""
        _load_data_analysis_recipe(page, shiny_app.url)
        self._restore_to_quality_control(page)
        plot_tab = page.locator(".nav-link:has-text('Assembly Quality Dotplot')")
        if plot_tab.count() == 0:
            pytest.skip("assembly_quality_dotplot sub-tab not found")
        plot_tab.first.click()
        _wait_shiny(page)
        page.wait_for_selector("#plot_group_assembly_quality_dotplot", timeout=10_000)
        expect(page.locator("#plot_reshuffle_btn_assembly_quality_dotplot")).to_have_count(0)

    def test_click_pins_the_seed_and_hides_the_control(self, page: Page, shiny_app: ShinyAppProc):
        """Clicking Reshuffle draws and pins a new seed — the control then disappears
        (nothing left to reshuffle from until the pin is removed some other way)."""
        _load_data_analysis_recipe(page, shiny_app.url)
        _navigate_to_phenotype_plot(page)
        try:
            btn = page.locator("#plot_reshuffle_btn_phenotype_genome_length_fragmentation")
            expect(btn).to_be_visible(timeout=10_000)
            btn.click()
            _wait_shiny(page)

            expect(
                page.locator("#plot_reshuffle_btn_phenotype_genome_length_fragmentation")
            ).to_have_count(0, timeout=8_000)
            _no_render_error(page)
        finally:
            self._restore_to_quality_control(page)


# ---------------------------------------------------------------------------
# T4 — Data preview
# ---------------------------------------------------------------------------

class TestDataPreview:
    def test_data_preview_renders(self, page: Page, shiny_app: ShinyAppProc):
        """Data preview grid renders without errors after data analysis recipe load."""
        _load_data_analysis_recipe(page, shiny_app.url)
        page.wait_for_selector("#home_data_preview", timeout=15_000)
        _no_render_error(page)
        expect(page.locator("#home_data_preview")).to_be_visible()


# ---------------------------------------------------------------------------
# T5 — View badges (issue #17): what the plot and the data preview show now
# ---------------------------------------------------------------------------

class TestViewBadges:
    """A small HTML badge next to the plot and in the data preview title. The tests restore the
    choices at the end, because the module-scoped page is shared."""

    PLOT_BADGE = "[id^='plot_badge_'] .spv-view-badge"
    DATA_BADGE = "#home_data_preview_badge .spv-view-badge"

    def _open_plot(self, page: Page) -> None:
        """After a data analysis recipe switch no plot tab is selected (own finding), so click the first one."""
        page.locator(".nav-link:has-text('Qc Reads Horizontal Barplot')").first.click()
        _wait_shiny(page)

    def _choose(self, page: Page, group: str, value: str) -> None:
        page.locator(f"#{group} input[value={value}]").check(force=True)
        _wait_shiny(page)

    def test_both_badges_say_result_by_default(self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        self._open_plot(page)
        expect(page.locator(self.PLOT_BADGE).first).to_have_text("Viewing: Result", timeout=15_000)
        expect(page.locator(self.DATA_BADGE)).to_have_text("Viewing: Result", timeout=15_000)

    def test_plot_badge_follows_plot_to_show_and_says_when_my_view_is_the_result(
            self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        self._open_plot(page)
        self._choose(page, "plot_view", "T3")
        try:
            expect(page.locator(self.PLOT_BADGE).first).to_have_text("Viewing: My view", timeout=15_000)
            # no filter or column drop yet: My view is identical to the Result (T3=T2 or T3=T2=T1)
            expect(page.locator("[id^='plot_badge_'] .spv-view-note").first).to_contain_text("T3=T2", timeout=15_000)
        finally:
            self._choose(page, "plot_view", "T2")
        expect(page.locator(self.PLOT_BADGE).first).to_have_text("Viewing: Result", timeout=15_000)

    def test_data_badge_follows_data_to_show_and_is_independent_of_the_plot(
            self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        self._open_plot(page)
        self._choose(page, "tier_toggle", "T1")
        try:
            expect(page.locator(self.DATA_BADGE)).to_have_text("Viewing: Raw", timeout=15_000)
            expect(page.locator(self.PLOT_BADGE).first).to_have_text("Viewing: Result")   # plots never show T1
        finally:
            self._choose(page, "tier_toggle", "T2")
        expect(page.locator(self.DATA_BADGE)).to_have_text("Viewing: Result", timeout=15_000)

    def test_the_badge_is_html_and_not_part_of_the_plot_image(self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        self._open_plot(page)
        badge = page.locator(self.PLOT_BADGE).first
        expect(badge).to_be_visible(timeout=15_000)
        # the badge is a sibling of the plot output, not inside the <img> the plot is drawn as
        assert badge.evaluate("e => !e.closest('img') && !!e.closest('[id^=plot_badge_]')")


# ---------------------------------------------------------------------------
# T6 - Exploration filters preview on Raw and Result (ADR-098, issue #56, HOM-09)
# ---------------------------------------------------------------------------

class TestPreviewFiltersOnReferenceViews:
    """GUARDED: a filter must change what the user sees on Result and Raw, not only on My view.
    The old gate (ADR-085) accepted the filter and silently showed unfiltered data."""

    GRID_ROWS = "#home_data_preview tbody tr"

    def _grid_rows(self, page: Page) -> str:
        """The grid text. The grid shows a window of rows, so its row count cannot tell a filter
        applied from none; the removed value's rows do change the text."""
        page.wait_for_selector(self.GRID_ROWS, timeout=15_000)
        return page.locator("#home_data_preview").inner_text()

    def test_filter_shrinks_the_result_preview_and_reset_restores_it(
            self, page: Page, shiny_app: ShinyAppProc):
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        page.locator(".nav-link:has-text('Qc Reads Horizontal Barplot')").first.click()
        _wait_shiny(page)
        before = self._grid_rows(page)
        page.locator("#fb_col").select_option(index=1)
        _wait_shiny(page)
        page.locator("#fb_op").select_option("ne")
        _wait_shiny(page)
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        expect(page.locator("#home_data_preview_badge .spv-view-note", has_text="preview filter")).to_contain_text(
            "preview filter(s) on, not saved", timeout=15_000)
        try:
            assert self._grid_rows(page) != before
        finally:
            # trash, not Reset: Reset also clears the value widget, which the next test needs
            page.locator("#filter_remove_0").click()
            _wait_shiny(page)

    def test_removing_an_applied_row_updates_the_view_without_apply(
            self, page: Page, shiny_app: ShinyAppProc):
        """GUARDED: the trash icon undoes a filter at once; the user does not press Apply again."""
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        page.locator(".nav-link:has-text('Qc Reads Horizontal Barplot')").first.click()
        _wait_shiny(page)
        before = self._grid_rows(page)
        page.locator("#fb_col").select_option(index=1)
        _wait_shiny(page)
        page.locator("#fb_op").select_option("ne")
        _wait_shiny(page)
        page.locator("#filter_add_row").click()
        expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        note = page.locator("#home_data_preview_badge .spv-view-note", has_text="preview filter")
        expect(note).to_be_visible(timeout=15_000)
        page.locator("#filter_remove_0").click()
        _wait_shiny(page)
        expect(note).to_have_count(0, timeout=15_000)
        assert self._grid_rows(page) == before

    def test_plot_changes_only_on_my_view(self, page: Page, shiny_app: ShinyAppProc):
        """GUARDED (Eve, 2026-11-11): Apply changes the table everywhere, the PLOT only on My view.
        Raw/Result plots are the recipe's plots."""
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        page.locator(".nav-link:has-text('Qc Reads Horizontal Barplot')").first.click()
        _wait_shiny(page)
        img = page.locator(".shiny-plot-output img").first
        expect(img).to_be_visible(timeout=15_000)
        src_before = img.get_attribute("src")
        page.locator("#fb_col").select_option(index=1)
        _wait_shiny(page)
        page.locator("#fb_op").select_option("ne")
        _wait_shiny(page)
        page.locator("#filter_add_row").click()
        expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        try:
            page.wait_for_timeout(1_500)
            assert page.locator(".shiny-plot-output img").first.get_attribute("src") == src_before
            expect(page.locator("[id^='plot_badge_'] .spv-view-note", has_text="table only")).to_be_visible()
            page.locator("#plot_view input[value=T3]").check(force=True)
            _wait_shiny(page)
            page.wait_for_timeout(1_500)
            assert page.locator(".shiny-plot-output img").first.get_attribute("src") != src_before
        finally:
            page.locator("#plot_view input[value=T2]").check(force=True)
            _wait_shiny(page)
            page.locator("#filter_remove_0").click()
            _wait_shiny(page)
