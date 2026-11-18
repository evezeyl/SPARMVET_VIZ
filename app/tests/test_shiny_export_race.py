"""The Export fields and the Export button in the instant of a recipe switch (D-0288, D-0289, D-0270, D-0050), in the browser.

Review of task/export-ready, F1 and F2: the Export panel must be tied to the recipe in the instant of a switch.
- F1: right after a switch the button was active and a press exported the NEW recipe with the OLD recipe's field values.
- F2: two switches A, B, A within about 30 ms stored B's choices under A, silently.
After the fix the button is grey from the switch until the page shows the new session's fields and the server has confirmed
them; a value is remembered only under the session the page was showing when the user set it.

Recipes: P = 2_test_data_ST22_dummy (3 plots), Q = 3_test_no_joins (1 plot), so that a bundle shows by its plots which recipe
it is, and by its README which values it was made with. The values of the two sessions differ in every field that matters.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_export_race.py -v
"""
import re
import zipfile

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_export_fields_per_session import (
    BTN, _download, _expect_fields, _fields, _open_export_panel, _pictures, _plot_ids_of, _readme, _set,
)
from app.tests.test_shiny_smoke import _choose_recipe, _open_app, _wait_shiny

P = "2_test_data_ST22_dummy"
Q = "3_test_no_joins"
# what each session is set to; the fields differ in preset, plot format, size (and the report format is the same, html, to keep the
# bundle cheap)
P_SET = {"preset": "publication", "plot_format": "png", "report_format": "html", "width": "9", "height": "6"}
Q_SET = {"preset": "web", "plot_format": "svg", "report_format": "html", "width": "11", "height": "7"}
README_OF = {
    P: ("publication (DPI=600, 9.0×6.0 in)", "Plot format      : png", "png"),
    Q: ("web (DPI=300, 11.0×7.0 in)", "Plot format      : svg", "svg"),
}
SET_OF = {P: P_SET, Q: Q_SET}


def _shown(values: dict) -> dict:
    return {"label": "", "box": False, **values}


# Switch the recipe the way the page does (the select's own events), wait `delay` ms in the page, then press Export the way a
# click does (the page's own click event). `delay` null: only switch. Returns what the press found.
_SWITCH_PRESS = """async ({recipes, gaps, pressAfter}) => {
    const sel = document.querySelector('#data_analysis_recipe_id');
    const b = () => document.querySelector('#export_bundle_download');
    const pick = (r) => { sel.value = r; sel.dispatchEvent(new Event('input', {bubbles: true}));
                          sel.dispatchEvent(new Event('change', {bubbles: true})); };
    pick(recipes[0]);
    for (let i = 1; i < recipes.length; i++) {
        if (gaps[i - 1] > 0) await new Promise(r => setTimeout(r, gaps[i - 1]));
        pick(recipes[i]);
    }
    if (pressAfter === null) return null;
    if (pressAfter > 0) await new Promise(r => setTimeout(r, pressAfter));
    const ev = new MouseEvent('click', {bubbles: true, cancelable: true});
    const grey = b().classList.contains('export-not-ready');
    b().dispatchEvent(ev);
    return {prevented: ev.defaultPrevented, grey: grey, selector: sel.value};
}"""


def _ready(page: Page, timeout: int = 60_000) -> None:
    _wait_shiny(page, timeout)
    expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=timeout)


def _which_recipe(z: zipfile.ZipFile) -> str:
    pictures = set(_pictures(z))
    for recipe in (P, Q):
        if pictures == _plot_ids_of(recipe):
            return recipe
    raise AssertionError(f"the bundle holds the plots {sorted(pictures)}: they are those of neither recipe")


def _assert_bundle_is_one_sessions(z: zipfile.ZipFile, note: str) -> str:
    """The bundle holds the plots of one recipe and exactly that session's own values (README, and the pictures' file type)."""
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in z.namelist()), f"{note}: the export was refused"
    recipe = _which_recipe(z)
    preset_line, format_line, ext = README_OF[recipe]
    readme = _readme(z)
    assert preset_line in readme, f"{note}: the bundle holds the plots of {recipe} but not its preset/size ({preset_line}):\n{readme[:900]}"
    assert format_line in readme, f"{note}: the bundle holds the plots of {recipe} but not its plot format"
    assert set(_pictures(z).values()) == {ext}, f"{note}: the pictures of {recipe} are not {ext}"
    return recipe


@pytest.fixture(scope="module")
def app_page(page: Page, shiny_app: ShinyAppProc):
    _open_app(page, shiny_app.url)
    return page


@pytest.fixture()
def two_sessions(app_page: Page):
    """Q and P each set to their own values (the app remembers them); the page ends on P with the Export panel open."""
    page = app_page
    _choose_recipe(page, Q)
    _open_export_panel(page)
    _set(page, **Q_SET)
    _choose_recipe(page, P)
    _open_export_panel(page)
    _set(page, **P_SET)
    _expect_fields(page, _shown(P_SET), "P as set")
    downloads: list = []
    handler = lambda d: downloads.append(d)  # noqa: E731
    page.on("download", handler)
    yield page, downloads
    page.remove_listener("download", handler)
    _ready(page)


def test_a_press_right_after_a_switch_starts_nothing_and_the_bundle_after_the_wait_is_the_new_sessions_own(two_sessions):
    """Point 1 (F1): from the switch until the page shows the new session's fields and the server confirmed them the button is
    grey and a press starts no download; a press after that gives a bundle of Q with Q's own values."""
    page, downloads = two_sessions
    press = page.evaluate(_SWITCH_PRESS, {"recipes": [Q], "gaps": [], "pressAfter": 10})
    assert press["prevented"] and press["grey"], f"a press 10 ms after the switch was not refused: {press}"
    page.wait_for_timeout(2_000)
    assert downloads == [], "the press right after the switch started a download"
    _ready(page)
    _expect_fields(page, _shown(Q_SET), "the page shows Q's own fields once the button is ready")
    z = _download(page)
    assert _assert_bundle_is_one_sessions(z, "after the wait") == Q


def test_ten_switches_each_followed_by_a_press_never_make_a_mixed_bundle_and_never_leave_the_button_grey(two_sessions):
    """Point 1 and 4 (F1): 10 switches P/Q, each followed by a press after 0 to 600 ms. Every bundle that is made holds one
    recipe's plots with THAT session's values; after every press the button becomes ready again."""
    page, downloads = two_sessions
    delays = [0, 5, 10, 20, 50, 100, 150, 250, 400, 600]
    refused = 0
    for i, delay in enumerate(delays):
        target = Q if i % 2 == 0 else P
        press = page.evaluate(_SWITCH_PRESS, {"recipes": [target], "gaps": [], "pressAfter": delay})
        refused += bool(press["prevented"])
        # point 4: never stuck grey. The button must open by the confirmation, well before the existing 5 s fallback (that
        # fallback would hide a confirmation that never comes).
        expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=4_000)
        assert page.locator("#data_analysis_recipe_id").input_value() == target
    page.wait_for_timeout(1_000)
    made = list(downloads)
    mixed = []
    for i, d in enumerate(made):
        z = zipfile.ZipFile(d.path())
        try:
            _assert_bundle_is_one_sessions(z, f"press {i}")
        except AssertionError as error:
            mixed.append(str(error)[:400])
    assert not mixed, f"{len(mixed)} of {len(made)} bundles are mixed:\n" + "\n".join(mixed)
    assert refused >= 6, f"the presses in the window were not refused ({refused} of {len(delays)})"
    # and a real press on the settled page is a bundle of the recipe shown, with its own values
    z = _download(page)
    recipe = _assert_bundle_is_one_sessions(z, "final press")
    assert recipe == page.locator("#data_analysis_recipe_id").input_value()


@pytest.mark.parametrize("gap", [0, 30, 60, 300])
def test_two_switches_a_b_a_leave_the_remembered_choices_of_both_sessions_as_they_were(two_sessions, gap):
    """Point 2 (F2): P, then Q, then P again within `gap` ms (0: inside one tick of the page). Afterwards P shows P's values, and a
    normal round trip to Q and back shows each session's own values."""
    page, _ = two_sessions
    page.evaluate(_SWITCH_PRESS, {"recipes": [Q, P], "gaps": [gap], "pressAfter": None})
    expect(page.locator("#data_analysis_recipe_id")).to_have_value(P)
    _ready(page)
    _expect_fields(page, _shown(P_SET), f"gap {gap} ms: P shows P's values after the quick switches")
    _choose_recipe(page, Q)
    _expect_fields(page, _shown(Q_SET), f"gap {gap} ms: Q's choices were not touched")
    _choose_recipe(page, P)
    _expect_fields(page, _shown(P_SET), f"gap {gap} ms: P's choices were not overwritten by Q's")


@pytest.mark.parametrize("delay", [0, 40, 100])
def test_a_user_change_right_after_a_switch_is_the_same_on_the_screen_in_the_store_and_in_the_bundle(two_sessions, delay):
    """Point 3: the user picks plot format PDF `delay` ms after the switch to Q. Whichever wins (the user's value or the value the
    server shows for Q), the value on the screen, the value the app remembers for Q (read through a round trip to P and back) and
    the value in the bundle made then are one and the same."""
    page, _ = two_sessions
    page.evaluate("""async ({delay}) => {
        const sel = document.querySelector('#data_analysis_recipe_id');
        sel.value = %s; sel.dispatchEvent(new Event('input', {bubbles: true})); sel.dispatchEvent(new Event('change', {bubbles: true}));
        if (delay > 0) await new Promise(r => setTimeout(r, delay));
        const radio = document.querySelector('input[name=export_plot_format][value=pdf]');
        radio.checked = true;
        radio.dispatchEvent(new Event('input', {bubbles: true})); radio.dispatchEvent(new Event('change', {bubbles: true}));
    }""" % repr(Q), {"delay": delay})
    _ready(page, 90_000)
    on_screen = page.locator("input[name=export_plot_format]:checked").get_attribute("value")
    assert on_screen in ("pdf", "svg")
    z = _download(page)
    assert _which_recipe(z) == Q
    assert set(_pictures(z).values()) == {on_screen}, f"the screen shows {on_screen}, the bundle holds {set(_pictures(z).values())}"
    assert f"Plot format      : {on_screen}" in _readme(z)
    _choose_recipe(page, P)
    _choose_recipe(page, Q)
    remembered = page.locator("input[name=export_plot_format]:checked").get_attribute("value")
    assert remembered == on_screen, f"the screen showed {on_screen}, the app remembers {remembered} for Q"
    # put Q back
    _set(page, **Q_SET)


@pytest.mark.parametrize("after_apply", [0, 30, 150])
def test_a_user_change_right_after_the_page_shows_the_new_sessions_fields_wins_and_is_remembered(two_sessions, after_apply):
    """Point 3, the other branch: the user picks plot format PDF `after_apply` ms after the page put Q's fields in the panel (the
    button is still grey, the server has not confirmed yet). The user's value wins, and it is the one on the screen, the one the
    app remembers for Q (round trip) and the one in the bundle."""
    page, _ = two_sessions
    page.evaluate("""({after}) => {
        window.__hook = (e) => {
            if (e.name !== 'export_plot_format') return;
            window.jQuery(document).off('shiny:inputchanged', window.__hook);
            setTimeout(() => {
                const radio = document.querySelector('input[name=export_plot_format][value=pdf]');
                radio.checked = true;
                radio.dispatchEvent(new Event('input', {bubbles: true})); radio.dispatchEvent(new Event('change', {bubbles: true}));
            }, after);
        };
        window.jQuery(document).on('shiny:inputchanged', window.__hook);
        const sel = document.querySelector('#data_analysis_recipe_id');
        sel.value = %s; sel.dispatchEvent(new Event('input', {bubbles: true})); sel.dispatchEvent(new Event('change', {bubbles: true}));
    }""" % repr(Q), {"after": after_apply})
    page.wait_for_function("() => document.querySelector('input[name=export_plot_format][value=pdf]').checked", timeout=30_000)
    _ready(page, 90_000)
    assert page.locator("input[name=export_plot_format]:checked").get_attribute("value") == "pdf", "the user's choice was overwritten"
    z = _download(page)
    assert _which_recipe(z) == Q and set(_pictures(z).values()) == {"pdf"}, "the bundle does not hold the user's choice (pdf)"
    _choose_recipe(page, P)
    _choose_recipe(page, Q)
    assert page.locator("input[name=export_plot_format]:checked").get_attribute("value") == "pdf", "the app does not remember the user's choice for Q"
    _set(page, **Q_SET)
