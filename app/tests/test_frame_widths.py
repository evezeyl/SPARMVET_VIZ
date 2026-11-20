"""The named widths of the app frame and the rule for the right panel, without a browser (D-0375, D-0384, D-0385, D-0386).

# @deps
# consumes: app/modules/frame_widths.py, app/src/www/panel_widths.js
# @end_deps

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_frame_widths.py -q
"""
from pathlib import Path

import pytest

from app.modules import frame_widths as fw

WINDOWS = (1100, 1280, 1366, 1600, 1920)


def test_floors_are_below_ceilings_and_shares_are_sane():
    for panel in (fw.LEFT, fw.RIGHT):
        assert 0 < panel.floor < panel.ceiling
        assert 0 < panel.share < fw.MAIN_MIN_SHARE
    assert fw.STORED_SHARE_MIN < fw.STORED_SHARE_MAX <= fw.MAIN_MIN_SHARE


@pytest.mark.parametrize("window", WINDOWS)
def test_default_widths_leave_the_main_panel_about_two_thirds(window):
    both = fw.default_px(fw.LEFT, window) + fw.default_px(fw.RIGHT, window)
    main = 1 - both / window
    assert main >= fw.MAIN_MIN_SHARE, f"main panel under half at {window} px"
    assert main >= 0.65, f"main panel {main:.2f} at {window} px: about two thirds was decided (D-0375)"


def test_css_width_is_a_clamp_of_the_named_values():
    assert fw.css_width(fw.LEFT) == f"clamp({fw.LEFT.floor}px, {fw.LEFT.share * 100:g}vw, {fw.LEFT.ceiling}px)"
    # the same numbers the CSS clamp gives, computed in Python
    assert fw.default_px(fw.LEFT, 100) == fw.LEFT.floor
    assert fw.default_px(fw.LEFT, 100_000) == fw.LEFT.ceiling


def test_the_page_receives_every_number_as_data_attributes():
    attrs = fw.data_attributes()
    for side, panel in fw.PANELS.items():
        assert float(attrs[f"data-{side}-share"]) == panel.share
        assert int(attrs[f"data-{side}-floor"]) == panel.floor
        assert int(attrs[f"data-{side}-ceiling"]) == panel.ceiling
    assert float(attrs["data-main-min-share"]) == fw.MAIN_MIN_SHARE


def test_the_script_holds_no_copy_of_the_numbers():
    """The script reads the named values from the page: none of them is written in it (D-0386: one place)."""
    text = (Path(__file__).resolve().parents[1] / "src" / "www" / "panel_widths.js").read_text(encoding="utf-8")
    for number in (str(fw.LEFT.floor), str(fw.RIGHT.floor), str(fw.LEFT.ceiling), "0.17", "0.15"):
        assert number not in text, number
    assert "localStorage" in text and "try" in text


def test_a_drag_cannot_take_the_main_panel_under_half():
    window = 1366
    other = fw.default_px(fw.RIGHT, window)
    wide = fw.clamp_width("left", 5000, window, other)
    assert wide == window * (1 - fw.MAIN_MIN_SHARE) - other
    assert (window - wide - other) / window == pytest.approx(fw.MAIN_MIN_SHARE)


def test_a_drag_cannot_go_under_the_floor():
    assert fw.clamp_width("left", 10, 1366, 200) == fw.LEFT.floor
    assert fw.clamp_width("right", -5, 1366, 200) == fw.RIGHT.floor


def test_the_floor_wins_when_the_window_is_too_narrow_for_the_half_rule():
    assert fw.clamp_width("left", 400, 500, 170) == fw.LEFT.floor


def test_a_width_inside_the_limits_is_kept():
    assert fw.clamp_width("left", 250, 1600, 240) == 250


@pytest.mark.parametrize("space,mode,audit,expected", [
    ("Home", "exploration", True, False),     # closed in Exploration (D-0375)
    ("Home", "audit", True, True),            # open in Audit mode
    ("Home", "audit", False, False),          # no audit in the app features: the mode is always Exploration
    ("Home", "exploration", False, False),
    ("Wrangle Studio", "exploration", True, True),   # the other user spaces keep it open (D-0381)
    ("Gallery", "exploration", True, True),
    ("Test Lab", "exploration", False, True),
    ("Gallery", "audit", True, True),         # the HOME mode does not matter elsewhere
])
def test_right_panel_open(space, mode, audit, expected):
    assert fw.right_panel_open(space, mode, audit) is expected


def test_leaving_audit_mode_closes_the_panel_again():
    assert fw.right_panel_open("Home", "audit", True) is True
    assert fw.right_panel_open("Home", "exploration", True) is False
