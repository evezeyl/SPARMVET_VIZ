"""The Gallery in a real browser: first paint, no-match line, the two stated rules, and the 'Select all' race.

Covers GALLERY-CHECK-1 findings 3 (the dropdown and the picture pane agree from the first paint), 4 (a combination that
matches nothing shows a standing line), 5 (the screen and the help state that filters act after Apply and that a group
with nothing ticked does not filter) and 6/9 (a tick made right after 'Select all' is not wiped).

Browser test (flag: SPARMVET_APP_FEATURES=qa, ghost save off), about 1 min. NOT covered: other app features, a
deployment with the gallery off, other browsers.
Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_gallery_filters.py -q
"""
import json
from pathlib import Path

from app.tests.conftest import shiny_app  # noqa: F401 - re-exports the fixture
from playwright.sync_api import Page

REPO = Path(__file__).resolve().parents[2]
INDEX = json.loads((REPO / "assets/gallery_data/gallery_index.json").read_text(encoding="utf-8"))
REGISTRY = INDEX["registry"]
PIVOT = INDEX["pivot"]


def _idle(page: Page, timeout: int = 60_000):
    page.wait_for_function("!document.documentElement.classList.contains('shiny-busy')", timeout=timeout)


def _options(page: Page) -> list:
    return page.eval_on_selector_all("#gallery_example_select option", "e=>e.map(x=>x.value)")


def _open_gallery(page: Page, url: str):
    page.goto(url)
    page.wait_for_selector("#sidebar_nav", timeout=60_000)
    _idle(page)
    page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
    page.wait_for_function("document.querySelectorAll('#gallery_example_select option').length>0", timeout=30_000)
    _idle(page)
    page.evaluate("()=>document.querySelectorAll('#gallery_taxonomy_sub_accordion .accordion-button.collapsed')"
                  ".forEach(b=>b.click())")
    page.wait_for_timeout(600)


def _only(page: Page, axis: str, value: str):
    """Tick exactly one term of a filter group (after 'Select all' is switched off) and wait for the round trip."""
    box = page.locator(f"#gallery_all_{axis}")
    if box.is_checked():
        box.uncheck(force=True)
    _idle(page)
    page.wait_for_function(
        f"document.querySelectorAll('input[name=gallery_filter_{axis}]:checked').length===0", timeout=10_000)
    page.locator(f"input[name=gallery_filter_{axis}][value='{value}']").check(force=True)
    _idle(page)


def _apply(page: Page):
    page.locator("#btn_apply_gallery_filters").click()
    _idle(page)
    page.wait_for_timeout(500)


def _selected(page: Page) -> str:
    return page.eval_on_selector("#gallery_example_select", "e=>e.value")


def _ticked(page: Page, axis: str) -> list:
    return page.eval_on_selector_all(f"input[name=gallery_filter_{axis}]:checked", "e=>e.map(x=>x.value)")


def _empty_pair():
    for v1, ids1 in PIVOT["by_family"].items():
        for v2, ids2 in PIVOT["by_pattern"].items():
            if not set(ids1) & set(ids2):
                return v1, v2
    raise AssertionError("the index has no pair of family and pattern without a common example")


def test_no_match_shows_a_standing_line(page: Page, shiny_app):
    _open_gallery(page, shiny_app.url)
    fam, pat = _empty_pair()
    _only(page, "family", fam)
    _only(page, "pattern", pat)
    _apply(page)
    assert _options(page) == []
    page.wait_for_timeout(6000)  # the toast is gone by now; the line must stay
    assert page.locator(".shiny-notification").count() == 0
    text = page.inner_text("#gallery_preview_img")
    assert "Nothing within this selection" in text


def test_first_paint_dropdown_and_picture_agree(page: Page, shiny_app):
    page.goto(shiny_app.url)
    page.wait_for_selector("#sidebar_nav", timeout=60_000)
    _idle(page)
    page.evaluate("""()=>{window.__bad=[];window.__seen=0;setInterval(()=>{
        const s=document.querySelector('#gallery_example_select');
        const p=document.querySelector('#gallery_preview_img');
        if(s&&s.options.length>0&&s.value){window.__seen++;
          if(p&&p.textContent.includes('Select an example'))
            window.__bad.push((p?p.textContent:'no pane').slice(0,60));}
      },5);}""")
    page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
    page.wait_for_timeout(3000)
    assert page.evaluate("window.__seen") > 0
    assert page.evaluate("window.__bad") == []  # a blank pane before its first render is not a contradiction
    page.wait_for_selector("#gallery_preview_img img", timeout=20_000)


def test_filter_panel_states_the_apply_rule(page: Page, shiny_app):
    _open_gallery(page, shiny_app.url)
    assert "only after you press Apply" in page.inner_text("#nav_sidebar")


def test_help_states_the_apply_rule():
    text = (REPO / "app/src/help/gallery.md").read_text(encoding="utf-8")
    assert "only after you press Apply" in text and "nothing ticked does not filter" in text
    assert "no example matches" in text.lower() or "nothing within this selection" in text.lower()


def test_tick_right_after_select_all_is_not_wiped(page: Page, shiny_app):
    """GALLERY-CHECK-1 finding 9: a tick made before the server could answer 'Select all' must stay."""
    _open_gallery(page, shiny_app.url)
    expected = len(PIVOT["by_geom"]["geom_line"])
    for _ in range(10):
        # all three clicks in one page task: no server answer can arrive between them
        page.evaluate("""()=>{document.querySelector('#gallery_all_geom').click();
            document.querySelector("input[name=gallery_filter_geom][value='geom_line']").click();
            document.querySelector('#btn_apply_gallery_filters').click();}""")
        _idle(page)
        page.wait_for_timeout(300)
        assert len(_options(page)) == expected
        assert _ticked(page, "geom") == ["geom_line"]
        page.locator("#gallery_all_geom").check(force=True)
        _idle(page)
        assert len(_ticked(page, "geom")) == len(PIVOT["by_geom"])



def test_apply_keeps_a_still_matching_example(page: Page, shiny_app):
    """Eve, 2026-11-20: Apply that still matches the example must not drop it."""
    _open_gallery(page, shiny_app.url)
    rid = "violin_simple"
    difficulty = next(d for d, ids in PIVOT["by_difficulty"].items() if rid in ids)
    page.select_option("#gallery_example_select", rid)
    _idle(page)
    _only(page, "difficulty", difficulty)
    _apply(page)
    assert _selected(page) == rid
    assert page.locator("#gallery_preview_img img").count() == 1
    assert "does not match" not in page.inner_text("#gallery_preview_img")


def test_apply_that_excludes_the_example_says_so(page: Page, shiny_app):
    _open_gallery(page, shiny_app.url)
    rid = "violin_simple"
    other = next(d for d, ids in PIVOT["by_difficulty"].items() if rid not in ids and ids)
    page.select_option("#gallery_example_select", rid)
    _idle(page)
    _only(page, "difficulty", other)
    _apply(page)
    assert _selected(page) != rid
    assert _selected(page) in PIVOT["by_difficulty"][other]
    note = page.inner_text("#gallery_preview_img")
    assert REGISTRY[rid]["name"] in note and "does not match" in note


def _all_ticked_count(page: Page) -> int:
    return page.eval_on_selector_all("input[name^=gallery_filter_]:checked", "e=>e.length")


def test_clear_all_ticks_unticks_everything_and_acts_only_after_apply(page: Page, shiny_app):
    """D-0379 (PROVISIONAL control): 'Clear all ticks' removes every tick of every axis; the list waits for Apply."""
    _open_gallery(page, shiny_app.url)
    full = len(_options(page))
    _only(page, "geom", "geom_line")
    _only(page, "difficulty", next(iter(PIVOT["by_difficulty"])))
    _apply(page)
    narrowed = len(_options(page))
    assert narrowed < full
    page.locator("#gallery_clear_ticks").click()
    _idle(page)
    page.wait_for_timeout(500)
    assert _all_ticked_count(page) == 0
    assert page.eval_on_selector_all("input[id^=gallery_all_]:checked", "e=>e.length") == 0
    assert len(_options(page)) == narrowed  # ticks only: the list is unchanged until Apply
    _apply(page)
    assert len(_options(page)) == full  # nothing ticked does not filter


def test_cleared_ticks_survive_going_to_home_and_back(page: Page, shiny_app):
    _open_gallery(page, shiny_app.url)
    page.locator("#gallery_clear_ticks").click()
    _idle(page)
    page.wait_for_timeout(500)
    page.locator("#sidebar_nav").get_by_text("Home", exact=True).first.click()
    _idle(page)
    page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
    page.wait_for_function("document.querySelectorAll('#gallery_example_select option').length>0", timeout=30_000)
    _idle(page)
    page.evaluate("()=>document.querySelectorAll('#gallery_taxonomy_sub_accordion .accordion-button.collapsed')"
                  ".forEach(b=>b.click())")
    page.wait_for_timeout(600)
    assert _all_ticked_count(page) == 0
