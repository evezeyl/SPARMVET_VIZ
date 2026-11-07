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

    def test_global_export_panel_visible(self, page: Page, shiny_app: ShinyAppProc):
        """Export accordion panel is always present (renamed from 'Global Export' in export redesign 2026-05-04)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Export")).to_be_visible()

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
