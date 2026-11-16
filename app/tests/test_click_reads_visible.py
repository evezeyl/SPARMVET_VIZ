"""A click or a choice that cannot be read is told, not swallowed (VERIF-FIX-2, the four places of check 8 F4;
D-0050 "No silent error that is the rule.").

1. HOME: the "Reshuffle arrangement" click and the "Remove the pinned seed" click were read inside `try ... except Exception: return`.
2. TEST_LAB: the scaffold form took the FIRST uploaded file when the dataset choice of the ID cleaning steps could not be read.

An input that does not exist yet (`SilentException`) is the normal state and stays silent. What the code does after is not
changed (the click still does nothing; the scaffold still uses the first file, which is a choice for Eve, see the report).

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION C1  the Reshuffle click read goes back to `except Exception: return`
  MUTATION C2  the unpin click read goes back to `except Exception: return`
  MUTATION C3  the scaffold does not say that the first file was taken

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_click_reads_visible.py -q
"""
from types import SimpleNamespace
from unittest import mock

import pytest
from shiny import reactive, render, ui

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_session_errors_visible import FakeInput
from app.tests.test_session_keys_missing_told import Home


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _home_with_a_plot(tmp_path, monkeypatch, values):
    """HOME with the plot `p` of the tiny recipe and a fake input holding `values`."""
    fake = FakeInput(**values)
    home = Home(tmp_path, monkeypatch, input_object=fake,
                discovered={"tiny": None})
    return home, fake


@pytest.mark.parametrize("handler, button", [("_handle_reshuffle", "plot_reshuffle_btn_p"), ("_handle_unpin", "plot_unpin_btn_p")])
def test_a_click_that_cannot_be_read_is_told(tmp_path, monkeypatch, handler, button):
    """MUTATION C1 and MUTATION C2 fail here."""
    home, _ = _home_with_a_plot(tmp_path, monkeypatch, {button: RuntimeError("the input store is broken")})
    with reactive.isolate():
        home.functions[handler]()
    errors = home.texts("error")
    assert len(errors) == 1 and "input store is broken" in errors[0] and ". Suggestion:" in errors[0], home.notes


@pytest.mark.parametrize("handler", ["_handle_reshuffle", "_handle_unpin"])
def test_a_button_that_does_not_exist_yet_is_silent(tmp_path, monkeypatch, handler):
    """The control: SilentException is the normal state before the button is drawn."""
    home, _ = _home_with_a_plot(tmp_path, monkeypatch, {})
    with reactive.isolate():
        home.functions[handler]()
    assert home.notes == []


def test_a_reshuffle_click_that_can_be_read_still_pins_a_seed(tmp_path, monkeypatch):
    """The control: the success path is unchanged."""
    home, _ = _home_with_a_plot(tmp_path, monkeypatch, {"plot_reshuffle_btn_p": 1})
    with reactive.isolate():
        home.functions["_handle_reshuffle"]()
        overrides = home.home_state.get()["t3_plot_overrides"]
    assert "random_state" in overrides["subtab_p"] and home.notes == []


# -- TEST_LAB scaffold -----------------------------------------------------------------------------------------------

def _scaffold(tmp_path, monkeypatch, choice):
    """The TEST_LAB `_scaffold_result` with two uploaded files and a reconciliation that gives steps, `choice` = what the dataset box gives."""
    import app.handlers.test_lab_handlers as tl
    functions = {}
    monkeypatch.setattr(reactive, "Calc", lambda fn: functions.setdefault(fn.__name__, fn))
    monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(render, "ui", lambda fn=None, **k: functions.setdefault(fn.__name__, fn) if fn else (lambda f: f))
    monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
    first, second = tmp_path / "first.tsv", tmp_path / "second.tsv"
    first.write_text("sample_id\tx\nS1\t1\nS2\t2\n")
    second.write_text("sample_id\ty\nS1\t1\nS2\t2\n")
    values = {
        "tl_scaffold_data_analysis_recipe_id": "scaffolded", "tl_scaffold_files": [
            {"name": "first.tsv", "datapath": str(first)}, {"name": "second.tsv", "datapath": str(second)}],
        "tl_scaffold_meta_file": None, "tl_scaffold_join_key": "sample_id", "tl_scaffold_use_recon": True,
        "tl_scaffold_run": 1, "tl_recon_threshold": 0.5, "tl_recon_ref_col": "sample_id", "tl_recon_target_col": "sample_id",
        "tl_recon_file1": [{"name": "first.tsv", "datapath": str(first)}], "tl_recon_file2": [{"name": "second.tsv", "datapath": str(second)}],
        "tl_recon_run": 1, "tl_recon_precheck": 0,
    }
    if choice is not None:
        values["tl_scaffold_recon_dataset"] = choice
    tl.define_server(FakeInput(**values), lambda *a, **k: (lambda fn: fn) if not (a and callable(a[0])) else a[0], mock.MagicMock(),
                     dev_studio=mock.MagicMock(), bootloader=mock.MagicMock())
    with reactive.isolate():
        return functions["_scaffold_result"](), str(functions["tl_scaffold_status_ui"]())


def test_a_dataset_choice_that_cannot_be_read_is_said_in_the_result(tmp_path, monkeypatch):
    """MUTATION C3 fails here. Before: the first uploaded file silently got the ID cleaning steps."""
    result, status = _scaffold(tmp_path, monkeypatch, choice=None)
    assert "error" not in result, result
    assert "first.tsv" in status and "Suggestion:" in status, "the status line under the form shows the note"
    assert result["id_steps_file"] == "first.tsv", "what the code does is not changed (a choice for Eve)"
    notes = result.get("notes", [])
    assert len(notes) == 1 and "first.tsv" in notes[0] and ". Suggestion:" in notes[0], result


def test_a_dataset_choice_that_can_be_read_gets_no_note(tmp_path, monkeypatch):
    """The control."""
    result, status = _scaffold(tmp_path, monkeypatch, choice="second.tsv")
    assert result["id_steps_file"] == "second.tsv" and result.get("notes", []) == [], result


# -- the schema of the table (t3_audit_engine) --------------------------------------------------------------------------

def test_a_table_whose_columns_cannot_be_read_says_nothing_was_checked():
    """MUTATION C4 (the callback is not called) fails here. The return value is as before: `[]`, which is itself a choice for Eve."""
    from app.modules.t3_audit_engine import inapplicable_filter_rows

    class Broken:
        def collect_schema(self):
            raise RuntimeError("the table cannot be scanned")

    told = []
    assert inapplicable_filter_rows(Broken(), [{"column": "gone"}], on_problem=told.append) == []
    assert len(told) == 1 and "the table cannot be scanned" in told[0] and ". Suggestion:" in told[0], told
    assert inapplicable_filter_rows(Broken(), [{"column": "gone"}]) == [], "without a callback: as before"


def test_a_table_whose_columns_can_be_read_reports_the_missing_column_and_nothing_else():
    """The control."""
    import polars as pl
    from app.modules.t3_audit_engine import inapplicable_filter_rows
    told = []
    lf = pl.DataFrame({"a": [1]}).lazy()
    assert [f["column"] for f in inapplicable_filter_rows(lf, [{"column": "a"}, {"column": "gone"}], on_problem=told.append)] == ["gone"]
    assert told == []
