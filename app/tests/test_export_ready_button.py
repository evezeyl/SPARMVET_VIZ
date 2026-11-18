"""D-0270 in the browser: the Export button is ready only when the server holds the values on the screen.

The race (question 20 of 2026-11-18): the download request can reach the server before the input messages the page sent a
moment earlier (Shiny applies input messages under the reactive lock, handles download requests without it). A tick
or a label pressed on Export within a fraction of a second was then lost, and nothing said so. The page now greys the
button from each change of the Export panel until the server has echoed the values it holds and they equal the values on
the screen. These tests change a field and press Export with no pause.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_export_ready_button.py -v
"""
import io
import json
import re
import zipfile
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.handlers.export_handlers import EXPORT_READY_TEXTS
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _load_data_analysis_recipe, _navigate_to_mlst_plot, _wait_shiny

BTN = "#export_bundle_download"


def _open_export_panel(page: Page) -> None:
    if not page.locator(BTN).is_visible():
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        _wait_shiny(page)


def _zip_of_click(page: Page) -> zipfile.ZipFile:
    """Press Export now (no pause) and read the bundle. Playwright waits for an enabled button, as a user does."""
    with page.expect_download(timeout=120_000) as info:
        page.locator(BTN).click()
    return zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))


_PRESS_AT_ONCE = """async (changes) => {
    // the changes of a field and a press on Export in the same instant (faster than a person can be)
    const b = document.querySelector('#export_bundle_download');
    for (const c of changes) {
        const el = c.kind === 'radio' ? document.querySelector(`input[name=${c.id}][value=${c.value}]`) : document.getElementById(c.id);
        if (c.kind === 'check') { el.checked = c.value; el.dispatchEvent(new Event('input', {bubbles: true}));
                                  el.dispatchEvent(new Event('change', {bubbles: true})); }
        else if (c.kind === 'radio') { el.checked = true; el.dispatchEvent(new Event('input', {bubbles: true}));
                                  el.dispatchEvent(new Event('change', {bubbles: true})); }
        else { el.value = c.value; el.dispatchEvent(new Event('input', {bubbles: true}));
               el.dispatchEvent(new Event('change', {bubbles: true})); }
    }
    const press = () => { const ev = new MouseEvent('click', {bubbles: true, cancelable: true});
                          b.dispatchEvent(ev); return !ev.defaultPrevented; };
    if (press()) return 'pressed at once';
    // a press on a grey button does nothing; the person presses again when the button says it is ready
    await new Promise(r => { const t = setInterval(() => {
        if (b.getAttribute('aria-disabled') !== 'true') { clearInterval(t); r(); } }, 10); });
    press();
    return 'pressed when ready';
}"""


def _change_and_press_at_once(page: Page, changes: list) -> zipfile.ZipFile:
    with page.expect_download(timeout=120_000) as info:
        page.evaluate(_PRESS_AT_ONCE, changes)
    return zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))


def _readme(z: zipfile.ZipFile) -> str:
    return next(z.read(n).decode() for n in z.namelist() if n.endswith("README.txt"))


def _is_grey(page: Page) -> bool:
    return page.locator(BTN).get_attribute("aria-disabled") == "true"


@pytest.fixture(scope="module")
def loaded(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_export_panel(page)
    expect(page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=15_000)
    return page


@pytest.fixture()
def clean(loaded):
    yield loaded
    loaded.locator("#export_include_reproducibility").uncheck(force=True)
    loaded.locator("#export_user_name").fill("")
    loaded.locator("input[name=export_plot_format][value=png]").check(force=True)
    loaded.locator("input[name=export_preset][value=web]").check(force=True)
    expect(loaded.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=15_000)


@pytest.mark.parametrize("run", range(8))
def test_change_then_export_with_no_pause_holds_the_new_choices(clean, run):
    """The box and the label are changed and Export is pressed at once: the bundle holds both."""
    page = clean
    label = f"race{run}"
    z = _change_and_press_at_once(page, [
        {"id": "export_include_reproducibility", "kind": "check", "value": True},
        {"id": "export_user_name", "kind": "text", "value": label}])
    names = z.namelist()
    assert any("data_analysis_recipes_reproducibility/" in n for n in names), "the tick was lost"
    assert any(label in n for n in names), f"the label was lost: {names[:3]}"
    assert "Reproducibility  : included" in _readme(z)


def test_two_quick_changes_in_a_row_both_arrive(clean):
    page = clean
    z = _change_and_press_at_once(page, [
        {"id": "export_plot_format", "kind": "radio", "value": "svg"},
        {"id": "export_preset", "kind": "radio", "value": "publication"}])
    text = _readme(z)
    assert "Plot format      : svg" in text, text
    assert "publication" in text.lower(), text


def test_the_button_is_grey_with_the_plain_text_after_a_change_and_back_when_ready(clean):
    page = clean
    page.locator("#export_user_name").fill("greycheck")
    # the same instant the field changed, the button is grey; nothing of it says server or timeout
    shown = page.evaluate("""() => { const b = document.querySelector('#export_bundle_download');
        return [b.getAttribute('aria-disabled'), b.innerText.trim()]; }""")
    # the echo may already be back; so check the text contract in the next test with the echo blocked
    assert shown[0] in ("true", None)
    expect(page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=15_000)
    assert "Export" in page.locator(BTN).inner_text()
    assert EXPORT_READY_TEXTS["waiting"] not in page.locator(BTN).inner_text()


def test_a_plot_tab_change_during_the_wait_leaves_the_button_working_and_the_fields_set(clean):
    page = clean
    page.locator("#export_user_name").fill("tabchange")
    _navigate_to_mlst_plot(page)
    expect(page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=15_000)
    assert page.locator("#export_user_name").input_value() == "tabchange"
    z = _zip_of_click(page)
    assert any("tabchange" in n for n in z.namelist())


def test_typing_a_label_and_pressing_export_with_the_mouse_gives_the_bundle_with_that_label(clean):
    """The browser fires "change" on the text field at the mouse-down on the button; that must not grey the button between
    the mouse-down and the mouse-up (the click would be lost). Fails with a script that greys on every "change" event."""
    page = clean
    page.locator("#export_user_name").click()
    page.locator("#export_user_name").press_sequentially("typed")
    expect(page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=15_000)
    z = _zip_of_click(page)
    assert any("typed" in n for n in z.namelist())


# ---- the confirmation is lost: a page whose websocket drops the echo ----------------------------------------------

@pytest.fixture(scope="module")
def blocked_page(browser, shiny_app: ShinyAppProc):
    """A page whose connection never delivers the server's echo (a test of the lost-confirmation path)."""
    page = browser.new_page()

    def _route(ws):
        server = ws.connect_to_server()

        def _from_server(message):
            if isinstance(message, str) and "export_ready_echo" in message:
                return      # the echo is lost
            ws.send(message)
        ws.on_message(lambda m: server.send(m))
        server.on_message(_from_server)

    page.route_web_socket("**/websocket/", _route)
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_export_panel(page)
    yield page
    page.close()


def _wait_ms(page: Page, ms: int) -> None:
    """How long the page waits for the echo before it gives up (read at each change)."""
    page.locator("#export_ready_panel").evaluate(f"e => e.setAttribute('data-timeout-ms', '{ms}')")


@pytest.fixture()
def blocked(blocked_page):
    """The blocked page with no wait pending and a long wait: a test that wants the timeout sets a short one."""
    _wait_ms(blocked_page, 1200)
    expect(blocked_page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=8_000)
    _wait_ms(blocked_page, 12_000)
    yield blocked_page
    _wait_ms(blocked_page, 1200)
    # let the wait of the test end, so the next test starts on a button that is ready
    expect(blocked_page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=20_000)


def test_a_lost_confirmation_does_not_leave_the_button_grey_and_says_what_to_check(blocked):
    page = blocked
    _wait_ms(page, 1200)
    page.locator("#export_user_name").fill("lost1")
    assert _is_grey(page)
    assert page.locator(BTN).inner_text().strip() == EXPORT_READY_TEXTS["waiting"]
    expect(page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=6_000)
    assert "Export" in page.locator(BTN).inner_text()
    expect(page.locator("#shiny-notification-panel")).to_contain_text(EXPORT_READY_TEXTS["lost"])


def test_the_grey_button_is_grey_on_the_input_event_before_the_field_is_sent(blocked):
    page = blocked
    grey = page.evaluate("""() => { const f = document.querySelector('#export_user_name');
        f.value = 'typing'; f.dispatchEvent(new Event('input', {bubbles: true}));
        return document.querySelector('#export_bundle_download').getAttribute('aria-disabled'); }""")
    assert grey == "true"


def test_a_grey_button_cannot_be_used_by_keyboard_or_a_second_click(blocked):
    page = blocked
    page.locator("#export_user_name").fill("kbd")
    assert _is_grey(page)
    page.locator(BTN).focus()
    for action in (lambda: page.keyboard.press("Enter"), lambda: page.keyboard.press("Space"),
                   lambda: page.locator(BTN).dispatch_event("click"),
                   lambda: page.locator(BTN).click(force=True, no_wait_after=True)):
        with pytest.raises(Exception):
            with page.expect_download(timeout=700):
                action()
    assert _is_grey(page)
    assert page.locator(BTN).get_attribute("tabindex") != "-1"      # it stays reachable by keyboard
    assert page.locator(BTN).get_attribute("role") in (None, "button", "link")


def test_a_button_drawn_again_during_the_wait_is_grey_again_and_comes_back(blocked):
    page = blocked
    _wait_ms(page, 1200)
    original = page.locator(BTN).evaluate("e => e.outerHTML")
    page.locator("#export_user_name").fill("redraw")
    assert _is_grey(page)
    page.evaluate("""(html) => { const b = document.querySelector('#export_bundle_download');
        const t = document.createElement('div'); t.innerHTML = html; b.replaceWith(t.firstElementChild); }""", original)
    expect(page.locator(BTN)).to_have_attribute("aria-disabled", "true", timeout=2_000)
    assert page.locator(BTN).inner_text().strip() == EXPORT_READY_TEXTS["waiting"]
    expect(page.locator(BTN)).not_to_have_attribute("aria-disabled", "true", timeout=6_000)
    assert "Export" in page.locator(BTN).inner_text()


def test_a_middle_click_on_the_grey_button_starts_no_download(blocked):
    """A middle click fires auxclick, not click, and a link would start its download: the grey button must refuse it."""
    page = blocked
    page.locator("#export_user_name").fill("middle")
    assert _is_grey(page)
    with pytest.raises(Exception):
        with page.expect_download(timeout=3000):
            page.locator(BTN).click(button="middle", force=True, no_wait_after=True)


def test_the_same_value_set_again_after_a_user_space_switch_greys_the_button_again(clean):
    """The server redraws the Export panel after a switch to Blueprint and back; the remembered values must not
    make the first change to the same value invisible to the button. Fails with a script that keeps lastSeen."""
    page = clean
    page.locator("#export_user_name").fill("again")
    expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=15_000)
    page.locator("#sidebar_nav").get_by_text("Blueprint Architect").first.click()
    _wait_shiny(page)
    page.get_by_text("Home", exact=True).first.click()
    _wait_shiny(page)
    _open_export_panel(page)
    expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=15_000)
    grey = page.evaluate("""() => { const f = document.querySelector('#export_user_name');
        f.value = 'again'; f.dispatchEvent(new Event('input', {bubbles: true}));
        return document.querySelector('#export_bundle_download').classList.contains('export-not-ready'); }""")
    assert grey
    expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=15_000)
