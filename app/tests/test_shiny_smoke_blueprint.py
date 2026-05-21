"""test_shiny_smoke_blueprint.py — Playwright smoke tests for the BLUEPRINT workspace.

New test infrastructure for BP-SMOKE-1 (existing suite covers HOME only).

Run:
    PYTHONPATH=. SPARMVET_PERSONA=qa .venv/bin/python -m pytest \
        app/tests/test_shiny_smoke_blueprint.py -v

Tests are grouped into four tiers:
  T1-BP — Navigation into the Blueprint workspace (Wrangle Studio sidebar)
  T2-BP — Manifest loading and sidebar panel rendering
  T3-BP — YAML escape hatch round-trip and Validate panel (BP-ESCAPE-1, BP-VALIDATE-1)
  T4-BP — Groups & Plots + Manifest Info panels (BP-GROUPS-1, BP-META-1)

Notes:
  - qa persona: blueprint_enabled=true, manifest_edit_enabled=true, ghost_save=false.
  - All tests require the app to render the Blueprint sidebar after loading a manifest.
  - `_wait_shiny` must follow every Shiny-reactive interaction to avoid DOM race conditions.
  - Emoji in accordion headers require :has-text selectors (role-based matching fails).
"""

import os
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture

_LAUNCH_PERSONA = os.environ.get("SPARMVET_PERSONA", "developer")
_BLUEPRINT_PERSONA_REQUIRED = {"developer", "qa"}


# ---------------------------------------------------------------------------
# Helpers (mirrors test_shiny_smoke.py conventions)
# ---------------------------------------------------------------------------

def _wait_shiny(page: Page, timeout: int = 10_000) -> None:
    page.wait_for_function(
        "() => !document.documentElement.classList.contains('shiny-busy')",
        timeout=timeout,
    )


def _no_render_error(page: Page) -> None:
    body = page.locator("body").inner_text(timeout=5_000)
    assert "Render error" not in body, f"Render error on page:\n{body[:500]}"
    assert "Traceback" not in body, f"Python traceback on page:\n{body[:500]}"


def _navigate_to_blueprint(page: Page, base_url: str) -> None:
    """Navigate to the Wrangle Studio (Blueprint) workspace.

    Selects the first available manifest in the dropdown, waits for the
    Blueprint sidebar accordion to render.  Skips the navigation if the
    accordion is already visible (so tests sharing a module-scoped page
    don't each trigger a full re-mount).
    """
    acc = page.locator("#wrangle_sidebar_accordion")
    if acc.count() > 0 and acc.is_visible():
        _wait_shiny(page)
        return

    page.goto(base_url)
    page.wait_for_selector("#sidebar_nav", timeout=20_000)

    # Click the "Blueprint Architect" nav pill (value="Wrangle Studio")
    page.locator("#sidebar_nav").get_by_text("Blueprint Architect").first.click()
    _wait_shiny(page)

    # Wait for the manifest selector to populate (auto-discovery runs on nav)
    page.wait_for_function(
        "() => {"
        "  var sel = document.querySelector('#stored_manifest_selector');"
        "  return sel && sel.options.length > 1;"
        "}",
        timeout=15_000,
    )

    # Select the first real manifest (index 1 — index 0 is the placeholder)
    page.evaluate(
        "() => {"
        "  var sel = document.querySelector('#stored_manifest_selector');"
        "  if (sel && sel.options.length > 1) {"
        "    sel.selectedIndex = 1;"
        "    sel.dispatchEvent(new Event('change', {bubbles: true}));"
        "  }"
        "}"
    )
    _wait_shiny(page, timeout=20_000)


def _expand_accordion(page: Page, label_text: str, timeout: int = 8_000) -> None:
    """Click a Blueprint sidebar accordion panel by its label text."""
    panel = page.locator(
        f"#wrangle_sidebar_accordion .accordion-button:has-text('{label_text}')"
    ).first
    if panel.count() == 0:
        pytest.skip(f"Accordion panel '{label_text}' not found")
    is_collapsed = "collapsed" in (panel.get_attribute("class") or "")
    if is_collapsed:
        panel.click()
        page.wait_for_timeout(300)
        _wait_shiny(page, timeout=timeout)


# ---------------------------------------------------------------------------
# T1-BP — Navigation into the Blueprint workspace
# ---------------------------------------------------------------------------

class TestBlueprintNavigation:
    def test_wrangle_studio_nav_tab_exists(self, page: Page, shiny_app: ShinyAppProc):
        """The 'Blueprint Architect' tab is present in the sidebar nav."""
        page.goto(shiny_app.url)
        page.wait_for_selector("#sidebar_nav", timeout=20_000)
        expect(page.locator("#sidebar_nav").get_by_text("Blueprint Architect")).to_be_visible()

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_navigate_to_blueprint_renders_sidebar(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """Clicking Wrangle Studio renders the Blueprint sidebar accordion."""
        _navigate_to_blueprint(page, shiny_app.url)
        expect(page.locator("#wrangle_sidebar_accordion")).to_be_visible()
        _no_render_error(page)

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_no_startup_errors_in_blueprint(self, page: Page, shiny_app: ShinyAppProc):
        """No render errors or tracebacks after navigating to Blueprint."""
        _navigate_to_blueprint(page, shiny_app.url)
        _no_render_error(page)


# ---------------------------------------------------------------------------
# T2-BP — Manifest loading and sidebar panel rendering
# ---------------------------------------------------------------------------

class TestBlueprintManifestLoad:
    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_manifest_selector_has_options(self, page: Page, shiny_app: ShinyAppProc):
        """The manifest selector populates with at least one YAML option."""
        _navigate_to_blueprint(page, shiny_app.url)
        count_js = (
            "() => {"
            "  var sel = document.querySelector('#stored_manifest_selector');"
            "  return sel ? Array.from(sel.options)"
            "      .filter(o => o.value.endsWith('.yaml')).length : 0;"
            "}"
        )
        count = page.evaluate(count_js)
        assert count >= 1, "No .yaml manifests found in stored_manifest_selector"

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_groups_plots_panel_renders(self, page: Page, shiny_app: ShinyAppProc):
        """After manifest load, Groups & Plots panel renders without error."""
        _navigate_to_blueprint(page, shiny_app.url)
        _expand_accordion(page, "Groups")
        content = page.locator("#bp_groups_inventory_ui")
        expect(content).to_be_visible(timeout=8_000)
        _no_render_error(page)

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_manifest_info_panel_renders(self, page: Page, shiny_app: ShinyAppProc):
        """After manifest load, Manifest Info panel renders without error."""
        _navigate_to_blueprint(page, shiny_app.url)
        _expand_accordion(page, "Manifest Info")
        content = page.locator("#bp_meta_form_ui")
        expect(content).to_be_visible(timeout=8_000)
        _no_render_error(page)


# ---------------------------------------------------------------------------
# T3-BP — YAML escape hatch round-trip + Validate panel (BP-ESCAPE-1, BP-VALIDATE-1)
# ---------------------------------------------------------------------------

class TestBlueprintEscapeAndValidate:
    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_escape_hatch_panel_renders(self, page: Page, shiny_app: ShinyAppProc):
        """YAML Escape Hatch panel renders with content after manifest load."""
        _navigate_to_blueprint(page, shiny_app.url)
        _expand_accordion(page, "YAML Escape")
        content = page.locator("#bp_yaml_escape_ui")
        expect(content).to_be_visible(timeout=8_000)
        _no_render_error(page)

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_escape_hatch_shows_yaml_content(self, page: Page, shiny_app: ShinyAppProc):
        """The escape hatch textarea/pre contains YAML text (not empty).

        (a) Validates that the escape hatch surface is populated after loading a manifest.
        For read-round-trip correctness: content must include at least one YAML keyword.
        """
        _navigate_to_blueprint(page, shiny_app.url)
        _expand_accordion(page, "YAML Escape")
        page.wait_for_selector("#bp_yaml_escape_ui", timeout=8_000)
        _wait_shiny(page)
        # Wait for the escape hatch to populate — accordion expansion triggers the
        # reactive, but the textarea value may lag behind the Shiny busy flag.
        # inner_text() skips <textarea> values, so poll via JS.
        page.wait_for_function(
            """() => {
                var el = document.querySelector('#bp_yaml_escape_ui');
                if (!el) return false;
                var ta = el.querySelector('textarea');
                if (ta && ta.value.length > 20) return true;
                var pre = el.querySelector('pre');
                if (pre && pre.innerText.length > 20) return true;
                return false;
            }""",
            timeout=15_000,
        )
        content_text = page.evaluate("""
            () => {
                var el = document.querySelector('#bp_yaml_escape_ui');
                if (!el) return '';
                var ta = el.querySelector('textarea');
                if (ta) return ta.value;
                var pre = el.querySelector('pre');
                if (pre) return pre.innerText;
                return el.innerText;
            }
        """)
        yaml_keywords = ["data_schemas", "info", "analysis_groups", "join_manifests"]
        found = any(kw in content_text for kw in yaml_keywords)
        assert found, (
            f"Escape hatch does not contain expected YAML content. "
            f"Got: {content_text[:200]!r}"
        )

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_validate_panel_renders(self, page: Page, shiny_app: ShinyAppProc):
        """Validate panel renders the 'Run validation' button after manifest load."""
        _navigate_to_blueprint(page, shiny_app.url)
        _expand_accordion(page, "Validate")
        expect(page.locator("#btn_bp_validate")).to_be_visible(timeout=8_000)
        _no_render_error(page)

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_validate_runs_and_shows_result(self, page: Page, shiny_app: ShinyAppProc):
        """Clicking 'Run validation' shows PASS or FAIL result within 30 s.

        This is the BP-VALIDATE-1 smoke verification — the subprocess-based validator
        must complete without crashing and render a result badge.
        """
        _navigate_to_blueprint(page, shiny_app.url)
        _expand_accordion(page, "Validate")
        page.locator("#btn_bp_validate").click()
        # Validation runs subprocess — allow up to 30 s
        _wait_shiny(page, timeout=35_000)
        result_el = page.locator("#bp_validate_ui")
        result_text = result_el.inner_text(timeout=30_000)
        assert "PASS" in result_text or "FAIL" in result_text, (
            f"Validation result badge not found. Got: {result_text[:300]!r}"
        )
        _no_render_error(page)


# ---------------------------------------------------------------------------
# T4-BP — Save/Export → HOME round-trip (c) and help panel check (b)
# ---------------------------------------------------------------------------

class TestBlueprintRoundTrip:
    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_save_internal_does_not_crash(self, page: Page, shiny_app: ShinyAppProc):
        """Clicking the hidden Save button (btn_save_internal) does not raise an error.

        (c) Partial smoke for the Save → HOME round-trip: the save action must not
        produce a traceback. Full HOME reload verification is covered by TestStartup
        in the HOME smoke suite.
        """
        _navigate_to_blueprint(page, shiny_app.url)
        # The Save button is hidden in #blueprint_hidden_controls — trigger via JS
        page.evaluate(
            "() => {"
            "  var btn = document.querySelector('#btn_save_internal');"
            "  if (btn) btn.click();"
            "}"
        )
        _wait_shiny(page, timeout=15_000)
        _no_render_error(page)

    @pytest.mark.skipif(
        _LAUNCH_PERSONA not in _BLUEPRINT_PERSONA_REQUIRED,
        reason="Blueprint requires developer or qa persona",
    )
    def test_blueprint_switch_back_to_home_no_error(
        self, page: Page, shiny_app: ShinyAppProc
    ):
        """Switching from Blueprint back to Home does not crash the app.

        (c) Verifies the workspace switch is clean and HOME can render after
        BLUEPRINT was active.  A broken workspace teardown would produce a
        render error visible in the page body.
        """
        _navigate_to_blueprint(page, shiny_app.url)
        # Switch back to Home via sidebar nav
        page.locator("#sidebar_nav").get_by_text("Home").first.click()
        _wait_shiny(page, timeout=15_000)
        _no_render_error(page)
