"""An audit step error names the plot, and the export names EVERY failing plot (PLOT-TABLE-ORDER-1, review point 4).

Two plots whose audit lists cannot run give two errors, each with its plot id (so two Alerts entries, never one for both),
and `EXPORT_NOT_CREATED.txt` lists both.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_error_names_the_plot.py -q
"""
import polars as pl
import pytest

from app.handlers.export_handlers import blocked_audit_notice
from app.modules.t3_audit_engine import AuditStepError, audit_failures, audited_frame

FRAME = pl.LazyFrame({"x": [1, 2, 3, 4], "y": [1.0, 2.0, 3.0, 4.0]})


def step(kind, column, node_id):
    if kind == "drop":
        return {"id": node_id, "node_type": "drop_column", "params": {"column": column}, "reason": "r"}
    return {"id": node_id, "node_type": "filter_row", "params": {"column": column, "op": "ge", "value": 2}, "reason": "r"}


BROKEN = [step("drop", "x", "a"), step("filter", "x", "b")]
FINE = [step("filter", "x", "c"), step("drop", "x", "d")]


def test_the_error_names_the_plot_in_its_text_and_its_pipeline_error():
    with pytest.raises(AuditStepError) as caught:
        audited_frame(FRAME, BROKEN, "plot_one")
    assert "audit step 2 of the plot 'plot_one'" in str(caught.value)
    assert "audit step 1 of the plot 'plot_one'" in str(caught.value), "the step that removed the column is named with its plot"
    assert "plot_one" in caught.value.pipeline_error.location
    assert caught.value.pipeline_error.evidence["plot"] == "plot_one"


def test_two_failing_plots_give_two_different_alert_records():
    errors = []
    for plot in ("plot_one", "plot_two"):
        with pytest.raises(AuditStepError) as caught:
            audited_frame(FRAME, BROKEN, plot)
        errors.append(caught.value.pipeline_error)
    keys = {(e.component, e.problem, e.location) for e in errors}
    assert len(keys) == 2, "the Alerts panel keeps an entry per (component, problem, location): two plots, two entries"


def test_every_failing_plot_is_found_not_only_the_first():
    plots = [("plot_one", lambda: FRAME, BROKEN), ("plot_ok", lambda: FRAME, FINE), ("plot_two", lambda: FRAME, BROKEN),
             ("plot_empty", lambda: FRAME, [])]
    failing = audit_failures(plots)
    assert [p for p, _ in failing] == ["plot_one", "plot_two"]


def test_no_failing_plot_and_no_audit_steps_give_nothing():
    assert audit_failures([]) == []
    assert audit_failures([("p", lambda: FRAME, FINE)]) == []


def test_the_refusal_text_names_every_failing_plot_with_its_reason():
    failing = audit_failures([("plot_one", lambda: FRAME, BROKEN), ("plot_two", lambda: FRAME, BROKEN)])
    text = blocked_audit_notice(failing)
    assert text.startswith("EXPORT NOT CREATED") and "these 2 plots" in text
    assert "Plot 'plot_one':" in text and "Plot 'plot_two':" in text
    assert text.count("The audit step 2 of the plot") == 2 and "nothing was exported" in text


def test_the_refusal_text_for_one_plot_says_this_plot():
    text = blocked_audit_notice(audit_failures([("only", lambda: FRAME, BROKEN)]))
    assert "this plot" in text and "Plot 'only':" in text
