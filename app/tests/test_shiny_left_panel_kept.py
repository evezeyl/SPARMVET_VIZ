"""HOME: a left panel the user opens (or closes) while the recipe is still opening stays as the user left it (D-0502).

The defect (found 2026-11-22, `tmpAI/coordinator/browser_tests_cause/REPORT.md` point 2): the left sidebar was drawn a second
time when the page sent its `sidebar_nav` input, a few seconds after the first draw, with the fixed list of open panels, so a
panel opened in those seconds closed again by itself. These tests click in the first moments (they do not wait for Shiny to be
idle) and then wait until the page has sent that input and the recipe is open.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_left_panel_kept.py -v
"""
import pytest
from playwright.sync_api import Page
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _wait_shiny

_OPEN = """() => [...document.querySelectorAll('#nav_accordion .accordion-item')]
    .filter(i => i.querySelector('.accordion-collapse.show'))
    .map(i => i.querySelector('.accordion-button').innerText.trim())"""
_NAV_SENT = "() => window.Shiny && Shiny.shinyapp && Shiny.shinyapp.$inputValues && Shiny.shinyapp.$inputValues['sidebar_nav'] !== undefined"
CHOICE = "Data analysis recipe Choice"

# Holds back the page's first send of `sidebar_nav` until released, which is the moment of the late redraw on the old code. The
# natural timing differs from run to run; this makes the race the same every time (the user's click comes before the input).
_HOLD_NAV = """(() => { const iv = setInterval(() => {
  if (!(window.Shiny && Shiny.shinyapp && Shiny.shinyapp.sendInput)) return;
  clearInterval(iv);
  const orig = Shiny.shinyapp.sendInput.bind(Shiny.shinyapp);
  window.__held = {}; window.__release = false;
  Shiny.shinyapp.sendInput = function (v) {
    if (!window.__release) { const keep = {};
      for (const k in v) { if (k.startsWith('sidebar_nav')) window.__held[k] = v[k]; else keep[k] = v[k]; }
      v = keep; if (!Object.keys(v).length) return; }
    return orig(v); };
  window.__flush = () => { window.__release = true; const h = window.__held; window.__held = {};
    if (Object.keys(h).length) orig(h); };
}, 2); })();"""


@pytest.fixture()
def fresh(browser, shiny_app: ShinyAppProc):  # noqa: F811
    page = browser.new_page()
    yield page, shiny_app.url
    page.close()


def _toggle(page: Page, title: str) -> None:
    page.locator(f"#nav_accordion .accordion-button:has-text('{title}')").first.click()
    page.wait_for_timeout(700)  # the panel's own open and close animation


def _settle(page: Page) -> list:
    """Wait until the page has sent its nav input and the recipe is open, then give a late redraw time to come."""
    page.wait_for_function(_NAV_SENT, timeout=60_000)
    page.wait_for_selector("#dynamic_tabs .nav-link", timeout=120_000)
    _wait_shiny(page, 60_000)
    page.wait_for_timeout(1500)
    return page.evaluate(_OPEN)


@pytest.mark.parametrize("title", ["Export", "Filters"])
def test_panel_opened_in_the_first_moments_stays_open(fresh, title):
    page, url = fresh
    page.goto(url)
    page.wait_for_selector("#nav_accordion .accordion-button", timeout=60_000)
    _toggle(page, title)
    opened = _settle(page)
    assert any(title in name for name in opened), opened


def test_panel_closed_in_the_first_moments_stays_closed(fresh):
    page, url = fresh
    page.goto(url)
    page.wait_for_selector("#nav_accordion .accordion-button", timeout=60_000)
    assert any(CHOICE in n for n in page.evaluate(_OPEN)), "the Choice panel starts open (the fixed list)"
    _toggle(page, CHOICE)
    opened = _settle(page)
    assert not any(CHOICE in n for n in opened), opened


def test_changing_space_and_back_starts_from_the_fixed_list(fresh):
    page, url = fresh
    page.goto(url)
    _settle(page)
    _toggle(page, CHOICE)
    _toggle(page, "Export")
    assert not any(CHOICE in n for n in page.evaluate(_OPEN))
    page.locator("#sidebar_nav input[value='Gallery'], #sidebar_nav a[data-value='Gallery']").first.click()
    _wait_shiny(page, 30_000)
    page.locator("#sidebar_nav input[value='Home'], #sidebar_nav a[data-value='Home']").first.click()
    _wait_shiny(page, 30_000)
    page.wait_for_timeout(1500)
    assert any(CHOICE in n for n in page.evaluate(_OPEN)), page.evaluate(_OPEN)


def _hold_then_release(page: Page, url: str, act) -> list:
    """Open the page with `sidebar_nav` held back, let `act` click, then release the input and wait for the recipe."""
    page.add_init_script(_HOLD_NAV)
    page.goto(url)
    page.wait_for_selector("#nav_accordion .accordion-button", timeout=60_000)
    page.wait_for_function("() => window.__held !== undefined", timeout=10_000)
    act()
    before = page.evaluate(_OPEN)
    held = page.evaluate("() => Object.keys(window.__held)")
    assert any(k.startswith("sidebar_nav") for k in held), f"the nav input was not held back: {held}"
    page.evaluate("() => window.__flush()")
    return before, _settle(page)


@pytest.mark.parametrize("title", ["Export", "Filters"])
def test_held_nav_panel_opened_before_the_input_stays_open(fresh, title):
    page, url = fresh
    before, after = _hold_then_release(page, url, lambda: _toggle(page, title))
    assert any(title in n for n in before), before
    assert any(title in n for n in after), (before, after)


def test_held_nav_panel_closed_before_the_input_stays_closed(fresh):
    page, url = fresh
    before, after = _hold_then_release(page, url, lambda: _toggle(page, CHOICE))
    assert not any(CHOICE in n for n in before), before
    assert not any(CHOICE in n for n in after), (before, after)


def test_changing_recipe_leaves_the_left_panels_as_the_user_has_them(fresh):
    """A change of recipe has never drawn the left sidebar again (the render does not read the recipe); it stays so."""
    from app.tests.test_shiny_smoke import _choose_recipe

    page, url = fresh
    page.goto(url)
    _settle(page)
    _toggle(page, "Export")
    before = page.evaluate(_OPEN)
    assert any("Export" in n for n in before), before
    _choose_recipe(page, "3_test_no_joins")
    assert page.evaluate(_OPEN) == before


# Counts how often the left accordion is MOUNTED (added to the page), from before the app starts. A second mount at first load is
# the double draw: it is hidden from the user by the "keep the user's panels" rule, so only this count shows that the render is not
# invalidated by the first arrival of `sidebar_nav` (the equality guard of `_sync_active_space`, D-0502, section 14 R3).
_COUNT_MOUNTS = """(() => { window.__mounts = 0;
  new MutationObserver(ms => { for (const m of ms) for (const n of m.addedNodes) {
    if (n.nodeType === 1 && (n.id === 'nav_accordion' || n.querySelector('#nav_accordion'))) window.__mounts++; } })
    .observe(document, {childList: true, subtree: true}); })();"""


def test_the_left_accordion_is_mounted_once_at_first_load(fresh):
    page, url = fresh
    page.add_init_script(_COUNT_MOUNTS)
    page.goto(url)
    _settle(page)
    assert page.evaluate("() => window.__mounts") == 1


def test_the_left_accordion_is_mounted_once_when_the_nav_input_comes_late(fresh):
    page, url = fresh
    page.add_init_script(_COUNT_MOUNTS)
    _hold_then_release(page, url, lambda: page.wait_for_timeout(2500))
    assert page.evaluate("() => window.__mounts") == 1


def test_closing_every_panel_is_an_answer_of_the_page_not_a_missing_one(fresh):
    """The page sends `null` (not nothing) when no panel is open; the server reads it as None, which is "the user closed
    everything" and not a first draw (`_user_open_panels`; py-shiny `_manage_inputs` stores the null as a value)."""
    page, url = fresh
    page.goto(url)
    _settle(page)
    for name in page.evaluate(_OPEN):
        _toggle(page, name)
    assert page.evaluate(_OPEN) == []
    assert page.evaluate("() => Shiny.shinyapp.$inputValues['nav_accordion']") is None
    assert page.evaluate("() => 'nav_accordion' in Shiny.shinyapp.$inputValues")
