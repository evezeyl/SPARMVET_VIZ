"""HOME-WALK B: the header strip (Mode, Table to view) at narrow and usual window widths, measured in the browser (bounding boxes).

The defect (the walk of 2026-11-20, window 1100 px wide): the theater is about 400 px wide between the two sidebars; the options were four columns that shrank to
nothing, so "Exploration" was printed over "Audit" and "Source" was cut. Now the row wraps and the options use two columns below 520 px of strip.

Browser, qa app features (every flag on, ghost save off), one app on the staged recipe (`gate_stage`). Checks: at 1100 px no two controls overlap and every control
is inside the strip; at 1300 px and 1600 px the four data choices stay on one line (as before). NOT covered: widths under 1000 px, the width of the plot (it is
what the two fixed sidebars leave: 316 px of image at 1100 px; asked to the owner), other browsers.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_home_strip_narrow.py -q
"""
from playwright.sync_api import Browser

from app.tests import gate_stage as g

CONTROLS = """() => {
  const strip = document.querySelector('.theater-header-strip');
  const sr = strip.getBoundingClientRect();
  // what the eye sees: the radio circles and the TEXT of every option and title (a label's own box can be wider than its text)
  const box = (name, r) => ({name: name, l: r.left, r: r.right, t: r.top, b: r.bottom});
  const boxes = [];
  strip.querySelectorAll('input[type=radio]').forEach(e => { if (e.getClientRects().length) boxes.push(box('radio ' + e.value, e.getBoundingClientRect())); });
  const walker = document.createTreeWalker(strip, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const text = (node.textContent || '').trim();
    if (!text || !node.parentElement || !node.parentElement.getClientRects().length) continue;
    const range = document.createRange(); range.selectNodeContents(node);
    Array.from(range.getClientRects()).forEach(r => { if (r.width > 1 && r.height > 1) boxes.push(box('text ' + text.slice(0, 20), r)); });
  }
  strip.querySelectorAll('select').forEach(e => { if (e.getClientRects().length) boxes.push(box('select ' + e.id, e.getBoundingClientRect())); });
  const data = Array.from(document.querySelectorAll('#data_view input[type=radio]')).map(e => Math.round(e.getBoundingClientRect().top));
  return {strip: {l: sr.left, r: sr.right}, boxes: boxes, data_tops: data};
}"""


def _measure(browser: Browser, url: str, width: int) -> dict:
    page = browser.new_page(viewport={"width": width, "height": 1000})
    try:
        page.goto(url)
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
        page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=120_000)
        page.wait_for_selector("#data_view", timeout=60_000)
        return page.evaluate(CONTROLS)
    finally:
        page.close()


def _overlaps(boxes: list) -> list:
    found = []
    for i, a in enumerate(boxes):
        for c in boxes[i + 1:]:
            if min(a["r"], c["r"]) - max(a["l"], c["l"]) > 2 and min(a["b"], c["b"]) - max(a["t"], c["t"]) > 2:
                found.append((a["name"], c["name"]))
    return found


def test_the_strip_does_not_overlap_at_1100_and_keeps_its_line_at_1300_and_1600(browser: Browser, tmp_path):
    with g.running_app(tmp_path) as (url, _log):
        narrow = _measure(browser, url, 1100)
        assert _overlaps(narrow["boxes"]) == [], narrow
        assert all(b["r"] <= narrow["strip"]["r"] + 1 and b["l"] >= narrow["strip"]["l"] - 1 for b in narrow["boxes"]), narrow
        for width in (1300, 1600):
            wide = _measure(browser, url, width)
            assert len(set(wide["data_tops"])) == 1 and len(wide["data_tops"]) == 4, f"the four data choices stay on one line at {width} px: {wide}"
