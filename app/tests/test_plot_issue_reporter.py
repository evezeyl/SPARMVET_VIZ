"""A plot's error or warning reaches the Alerts and Processing issues panels once, without breaking the flush (VIZ-STANDARD-1, V7).

# @deps
# consumes: app/modules/plot_issue_reporter.py
# @end_deps

The first version read `session_processing_issues.get()` inside `session.on_flushed`, outside a reactive context:
`RuntimeError: No current reactive context`, three times, and the rest of the flush (the other plots, the Export panel)
did not run. The reporter reads under `reactive.isolate()` and does not add an issue twice.
"""
import pytest
from shiny import reactive

from app.modules.plot_issue_reporter import ALERT_CAP, ISSUE_CAP, make_issue_reporter


class FakeSession:
    """What the reporter needs of a session: `on_flushed`. The callbacks run later, outside any reactive context."""

    def __init__(self):
        self.callbacks = []

    def on_flushed(self, callback, once=True):
        self.callbacks.append(callback)

    def flush(self):
        callbacks, self.callbacks = self.callbacks, []
        for callback in callbacks:
            callback()


def entry(problem="Plot 'p', layer 1 (geom_point): bad. Fix: good.", location="render(plot_id='p')", severity="error"):
    return {"component": "VizFactory", "problem": problem, "location": location, "severity": severity, "timestamp": "2026-11-15T10:00:00"}


@pytest.fixture
def parts():
    session = FakeSession()
    issues, alerts = reactive.Value([]), reactive.Value([])
    return session, issues, alerts, make_issue_reporter(session, issues, alerts)


def read(value):
    with reactive.isolate():
        return value.get()


def test_the_flush_callback_reads_outside_a_reactive_context_without_error(parts):
    session, issues, alerts, report = parts
    report(entry(), "Plot 'p': bad.", "error")
    session.flush()   # RuntimeError "No current reactive context" without reactive.isolate()
    assert len(read(issues)) == 1 and len(read(alerts)) == 1


def test_the_same_issue_redrawn_many_times_is_reported_once(parts):
    session, issues, alerts, report = parts
    for _ in range(5):
        report(entry(), "Plot 'p': bad.", "error")
        session.flush()
    assert len(read(issues)) == 1 and len(read(alerts)) == 1


def test_several_reports_in_one_flush_are_each_kept_once(parts):
    session, issues, alerts, report = parts
    report(entry(problem="one"), "one", "error")
    report(entry(problem="two"), "two", "error")
    report(entry(problem="one"), "one", "error")
    session.flush()
    assert [e["problem"] for e in read(issues)] == ["one", "two"]
    assert [a["msg"] for a in read(alerts)] == ["one", "two"]


def test_the_same_problem_of_another_plot_is_another_issue(parts):
    session, issues, alerts, report = parts
    report(entry(location="render(plot_id='a')"), "Plot 'a': bad.", "error")
    report(entry(location="render(plot_id='b')"), "Plot 'b': bad.", "error")
    session.flush()
    assert len(read(issues)) == 2 and len(read(alerts)) == 2


def test_an_alert_has_the_kind_it_was_reported_with(parts):
    session, issues, alerts, report = parts
    report(entry(severity="warning"), "an unknown key", "warning")
    session.flush()
    assert read(alerts)[0]["type"] == "warning" and read(alerts)[0]["msg"] == "an unknown key"
    assert read(issues)[0]["severity"] == "warning"


def test_what_was_already_in_the_panels_is_kept(parts):
    session, issues, alerts, report = parts
    with reactive.isolate():
        issues.set([entry(problem="earlier")])
        alerts.set([{"ts": "09:00:00", "msg": "earlier", "type": "message"}])
    report(entry(), "later", "error")
    session.flush()
    assert [e["problem"] for e in read(issues)][0] == "earlier" and len(read(issues)) == 2
    assert [a["msg"] for a in read(alerts)] == ["earlier", "later"]


def test_the_panels_are_capped(parts):
    session, issues, alerts, report = parts
    for number in range(ISSUE_CAP + 5):
        report(entry(problem=f"issue {number}"), f"alert {number}", "error")
    session.flush()
    assert len(read(issues)) == ISSUE_CAP and len(read(alerts)) == ALERT_CAP
    assert read(alerts)[-1]["msg"] == f"alert {ISSUE_CAP + 4}"


def test_a_panel_that_is_not_there_is_skipped():
    session = FakeSession()
    report = make_issue_reporter(session, None, None)
    report(entry(), "bad", "error")
    session.flush()
