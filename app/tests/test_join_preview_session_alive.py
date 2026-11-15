"""LIVE: an unexpected error in the Blueprint join preview does not end the user's session (D13).

The app of `join_preview_crash_app.py` raises a NameError inside the preview. The preview is a `reactive.Effect`; an
error that escapes it makes Shiny close the session. The test checks that the user sees the internal-error message
(not the user's-mistake one) and that the session still answers afterwards.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_join_preview_session_alive.py -q
"""
import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture

from app.tests.test_shiny_smoke_blueprint import _navigate_to_blueprint, _wait_shiny

crash_app = create_app_fixture(str(Path(__file__).parent / "join_preview_crash_app.py"), scope="module")

pytestmark = pytest.mark.skipif(os.environ.get("SPARMVET_APP_FEATURES", "developer") not in {"developer", "qa"},
                                reason="Blueprint requires developer or qa app features")


def _preview(page: Page, left_keys, right_keys) -> None:
    page.evaluate(
        """([lk, rk]) => {
            Shiny.setInputValue('joint_left_ingredient', 'a', {priority: 'event'});
            Shiny.setInputValue('joint_right_ingredient', 'b', {priority: 'event'});
            Shiny.setInputValue('joint_left_keys', lk, {priority: 'event'});
            Shiny.setInputValue('joint_right_keys', rk, {priority: 'event'});
            Shiny.setInputValue('btn_joint_preview', Math.random(), {priority: 'event'});
        }""", [left_keys, right_keys])
    _wait_shiny(page)


def test_an_unexpected_error_in_the_preview_keeps_the_session_alive(page: Page, crash_app):
    _navigate_to_blueprint(page, crash_app.url)
    # load the first component of the recipe: this sets the active data analysis recipe of the Blueprint
    page.wait_for_function("() => { var s = document.querySelector('#dataset_pipeline_selector'); return s && s.options.length > 0; }")
    page.evaluate("() => Shiny.setInputValue('btn_import_data_analysis_recipe', Math.random(), {priority: 'event'})")
    _wait_shiny(page, timeout=30_000)
    # a hidden output is not computed by Shiny: open the Joint Designer tab so that the preview box is rendered
    page.locator("#architect_internal_tabs a[data-value='joint_designer']").click()
    _wait_shiny(page)
    box = page.locator("#joint_preview_ui")
    expect(box).to_contain_text("No preview yet")

    _preview(page, ["k"], ["k"])  # the injected NameError
    expect(box).to_contain_text("an internal error, not your recipe")
    expect(box).not_to_contain_text("NameError")  # the fault is in the log, not blamed on the user

    assert page.evaluate("() => Shiny.shinyapp.$socket.readyState") == 1  # still open

    _preview(page, [], [])  # a different path of the same effect answers: the session is alive
    expect(box).to_contain_text("Select at least one key on each side.")
