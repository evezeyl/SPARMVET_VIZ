"""test_shiny_smoke.py — headless Playwright smoke tests for SPARMVET_VIZ.

Run (full suite, qa persona):
    PYTHONPATH=. SPARMVET_PERSONA=qa .venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v

Run (developer persona — tests Gallery visibility):
    PYTHONPATH=. SPARMVET_PERSONA=developer .venv/bin/python -m pytest app/tests/test_shiny_smoke.py::TestPersonaMasking -v

Tests are grouped into four tiers:
  T1 — App startup and project load (always fast, always run)
  T2 — Persona masking (sidebar nav visibility for the active launch persona)
  T3 — Filter pipeline + T3 audit promotion (highest-risk refactor surface)
  T4 — Data preview grid

Note on persona switching: the app persona is set at launch via SPARMVET_PERSONA env var.
There is no runtime `#persona_selector` dropdown; runtime switching is not currently wired
to a rendered input. T2 tests reflect the LAUNCH persona only.

The `qa` persona is recommended for CI (ghost_save OFF = deterministic).
"""

import os
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture

_LAUNCH_PERSONA = os.environ.get("SPARMVET_PERSONA", "developer")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wait_shiny(page: Page, timeout: int = 10_000) -> None:
    """Wait for Shiny to finish all reactive computations (busy indicator clears)."""
    page.wait_for_function(
        "() => !document.documentElement.classList.contains('shiny-busy')",
        timeout=timeout
    )


def _load_project(page: Page, base_url: str, project_id: str = "1_test_data_ST22_dummy") -> None:
    """Navigate to app, select the test project, and wait for groups to render.

    If the project is already loaded (Quality Control nav visible), skips navigation
    so tests sharing a module-scoped page don't each trigger a fresh Shiny session
    and re-run T1 materialization.
    """
    qc = page.locator(".nav-link:has-text('Quality Control')")
    if qc.count() > 0 and qc.is_visible():
        _wait_shiny(page)
        return
    page.goto(base_url)
    page.wait_for_selector("#project_id", timeout=20_000)
    page.locator("#project_id").select_option(project_id)
    # Wait for dynamic_tabs group nav pills — the first group in 1_test_data_ST22_dummy
    # is "Quality Control". This is the slowest step
    # (tier1 materialization + dynamic_tabs render). 60s covers cold-start scenarios.
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=60_000)
    _wait_shiny(page)


def _navigate_to_mlst_plot(page: Page) -> None:
    """Navigate to the AMR/Virulence group → mlst_bar plot (has 'year' numeric column).

    Group label: "💊 AMR and ☠️ Virulence" (from manifest description field).
    Plot tab: "Mlst Bar" (from p_id.replace("_"," ").title() in dynamic_tabs).
    If navigation fails the caller should skip — this is dataset-specific.
    """
    # Group tab label comes from manifest description field (home_theater.py L709)
    # Use :has-text for emoji-containing labels (role matching can fail on emoji)
    amr_tab = page.locator(".nav-link:has-text('AMR')")
    if amr_tab.count() == 0:
        pytest.skip("AMR group tab not found in active project")
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

    The accordion initialises with only 'Manifest Choice' open (home_theater.py).
    The 'Filters' panel only renders when interactivity_enabled=true (developer/qa
    persona) and is collapsed by default — clicking the header expands it so
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
        expect(page.locator("#project_id")).to_be_visible(timeout=15_000)

    def test_no_startup_errors(self, page: Page, shiny_app: ShinyAppProc):
        """No Python traceback or render errors at startup."""
        page.goto(shiny_app.url)
        page.wait_for_load_state("networkidle", timeout=15_000)
        _no_render_error(page)

    def test_project_load(self, page: Page, shiny_app: ShinyAppProc):
        """Loading the test project renders at least one navigation link."""
        _load_project(page, shiny_app.url)
        _no_render_error(page)
        tabs = page.locator(".nav-link").all()
        assert len(tabs) > 0, "No navigation tabs found after project load"


# ---------------------------------------------------------------------------
# T2 — Persona masking (tests the LAUNCH persona only — no runtime switching)
# ---------------------------------------------------------------------------

class TestPersonaMasking:
    def test_sidebar_nav_renders(self, page: Page, shiny_app: ShinyAppProc):
        """sidebar_nav_ui renders and shows the Home tab for any persona."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        expect(page.locator("#sidebar_nav")).to_be_visible()

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in ("developer", "qa"),
        reason="Gallery only visible for developer/qa persona"
    )
    def test_developer_sees_gallery(self, page: Page, shiny_app: ShinyAppProc):
        """developer/qa persona: Gallery tab is visible in sidebar nav."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        expect(page.get_by_text("Gallery")).to_be_visible()

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in ("pipeline-static",),
        reason="Right sidebar hidden only for pipeline-static"
    )
    def test_static_hides_right_sidebar(self, page: Page, shiny_app: ShinyAppProc):
        """pipeline-static persona: right sidebar container excluded from DOM (ADR-052-§1)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=15_000)
        # Container must be absent — not just empty. A present container still occupies 340px.
        assert page.locator("#audit_sidebar").count() == 0, \
            "Right sidebar container (#audit_sidebar) should be absent from DOM for pipeline-static"

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in ("pipeline-exploration-simple", "pipeline-static"),
        reason="Gallery/DevStudio visible for advanced+ personas"
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
        """Filter sidebar renders with Add Row button after project load and panel open."""
        _load_project(page, shiny_app.url)
        _open_filters_panel(page)
        expect(page.locator("#filter_add_row")).to_be_visible()

    def test_add_filter_row(self, page: Page, shiny_app: ShinyAppProc):
        """Clicking Add Row with year > 2000 produces a pending filter row.

        Navigates to Results → mlst_bar first (MLST_with_metadata has 'year').
        Note: filter contract correctness is in test_filter_operators.py (21 cases).
        This smoke test verifies the reactive wiring survives the refactor.
        """
        _load_project(page, shiny_app.url)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
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
        _load_project(page, shiny_app.url)
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
        _load_project(page, shiny_app.url)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
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

_PIPELINE_PERSONAS = {"pipeline-static", "pipeline-exploration-simple"}
_INTERACTIVE_PERSONAS = {"pipeline-exploration-advanced", "project-independent",
                         "developer", "qa"}


class TestPhase25Panels:
    def test_accordion_renders(self, page: Page, shiny_app: ShinyAppProc):
        """#nav_accordion is present after startup (Phase 25-E accordion structure)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        expect(page.locator("#nav_accordion")).to_be_visible()

    def test_data_import_panel_visible_for_exploration_personas(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """Data Import accordion panel is present for interactive/exploration personas.

        For exploration personas (developer, qa, advanced, independent),
        the panel shows upload controls in addition to the source-file listing.
        Phase 25-F wiring: data_import_ui output is registered and renders.
        """
        if _LAUNCH_PERSONA in _PIPELINE_PERSONAS:
            pytest.skip("Data Import upload controls absent for pipeline personas")
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Data Import")).to_be_visible()

    def test_global_export_panel_visible(self, page: Page, shiny_app: ShinyAppProc):
        """Export accordion panel is always present (renamed from 'Global Project Export' in export redesign 2026-05-04)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Export")).to_be_visible()

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in ("pipeline-static", "pipeline-exploration-simple"),
        reason="Manifest Choice only absent for pipeline personas"
    )
    def test_manifest_choice_hidden_for_pipeline_static(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """pipeline-static/simple: Manifest Choice panel excluded from accordion DOM.

        manifest_selector.visible=false means the panel is never added to the
        accordion panels list — it is structurally absent, not just CSS-hidden.
        """
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        assert accordion.get_by_text("Manifest Choice").count() == 0, \
            "Manifest Choice panel should be absent from accordion for pipeline personas"

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _INTERACTIVE_PERSONAS,
        reason="Session Management panel only present for interactive personas"
    )
    def test_session_management_panel_visible(self, page: Page, shiny_app: ShinyAppProc):
        """Session Management accordion panel present for interactive personas (Phase 25-G)."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#nav_accordion", timeout=15_000)
        accordion = page.locator("#nav_accordion")
        expect(accordion.get_by_text("Session Management")).to_be_visible()


# ---------------------------------------------------------------------------
# T4 — Data preview
# ---------------------------------------------------------------------------

class TestDataPreview:
    def test_data_preview_renders(self, page: Page, shiny_app: ShinyAppProc):
        """Data preview grid renders without errors after project load."""
        _load_project(page, shiny_app.url)
        page.wait_for_selector("#home_data_preview", timeout=15_000)
        _no_render_error(page)
        expect(page.locator("#home_data_preview")).to_be_visible()
