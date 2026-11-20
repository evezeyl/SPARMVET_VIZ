"""
@deps
provides: function:css_width, function:data_attributes, function:right_panel_open, function:clamp_width, constant:LEFT, constant:RIGHT, constant:MAIN_MIN_SHARE
consumes: none
consumed_by: app/src/ui.py, app/handlers/home_theater.py, app/tests/test_frame_widths.py, app/tests/test_panel_widths_browser.py
doc: .claude/rules/rules_css_style_spec.md#12, .claude/rules/ui_implementation_contract.md#2
@end_deps

The widths of the two side panels of the app frame, in ONE place (D-0386). Pure logic, no Shiny.

All four user spaces share the frame (`app/src/ui.py`): a left panel, a main panel and a right panel. The side panels follow the window
(D-0375): their default width is a share of the window between a floor and a ceiling (a CSS `clamp()`), so the main panel keeps about two thirds
of the window at every width from 1100 to 1920 px. The user may drag a panel wider or narrower (D-0381); a dragged width is kept in the browser as a
share of the window (D-0382) and the main panel never goes below half of the window (D-0384).

PROVISIONAL (D-0386: "Her manual test will judge the visuals", the values are expected to change): every number below. They are the architect's
starting values of the study `tmpAI/panel/panel_widths/`, then adjusted by measurement in the real app (see the report of the task).
The page script `app/src/www/panel_widths.js` reads these same values from data attributes (`data_attributes()`); nothing is repeated in it.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PanelWidth:
    """The default width of one side panel: `share` of the window, never below `floor` px nor above `ceiling` px."""
    share: float
    floor: int
    ceiling: int


# PROVISIONAL values (D-0386)
LEFT = PanelWidth(share=0.17, floor=190, ceiling=340)
RIGHT = PanelWidth(share=0.15, floor=170, ceiling=340)
# After a drag the main panel keeps at least this share of the window (D-0384: one half)
MAIN_MIN_SHARE = 0.5
# A stored share outside these limits is not used (a broken or hand-edited value of the browser's local storage, D-0382)
STORED_SHARE_MIN = 0.05
STORED_SHARE_MAX = 0.5

PANELS = {"left": LEFT, "right": RIGHT}

# The user spaces (the values of the input `sidebar_nav`)
HOME = "Home"


def css_width(panel: PanelWidth) -> str:
    """The `width` of the sidebar at build: a share of the window between the floor and the ceiling (CSS `clamp()`, vw = 1% of the window)."""
    return f"clamp({panel.floor}px, {panel.share * 100:g}vw, {panel.ceiling}px)"


def data_attributes() -> dict:
    """The values the page script needs, as HTML data attributes (the script never builds a style from text: it reads numbers)."""
    attrs = {"data-main-min-share": f"{MAIN_MIN_SHARE:g}", "data-stored-share-min": f"{STORED_SHARE_MIN:g}",
             "data-stored-share-max": f"{STORED_SHARE_MAX:g}"}
    for side, panel in PANELS.items():
        attrs[f"data-{side}-share"] = f"{panel.share:g}"
        attrs[f"data-{side}-floor"] = str(panel.floor)
        attrs[f"data-{side}-ceiling"] = str(panel.ceiling)
    return attrs


def default_px(panel: PanelWidth, window_px: float) -> float:
    """What the CSS `clamp()` of the default width gives at this window width."""
    return min(max(panel.share * window_px, panel.floor), panel.ceiling)


def clamp_width(side: str, wanted_px: float, window_px: float, other_px: float) -> float:
    """The width a drag or a stored share may take: not below the floor, and the two panels together at most one minus `MAIN_MIN_SHARE` of the window.

    `other_px` is the width of the other side panel (counted open or closed, so that opening it later cannot break the rule). When the floors alone
    are wider than the rule allows (a very narrow window) the floor wins: a panel is never made narrower than it can be used.
    """
    panel = PANELS[side]
    most = window_px * (1 - MAIN_MIN_SHARE) - other_px
    return max(panel.floor, min(wanted_px, most))


def right_panel_open(user_space: str, mode: str, audit_available: bool) -> bool:
    """Whether the right panel is open for this user space and mode (D-0375, D-0385).

    In HOME it is open in Audit mode only; with no audit in the app features the mode is always Exploration, so it is closed. The other user
    spaces keep it open (D-0381). A panel the user opened by hand in Exploration is not undone until the mode or the user space changes.
    """
    if user_space != HOME:
        return True
    return bool(audit_available and mode == "audit")
