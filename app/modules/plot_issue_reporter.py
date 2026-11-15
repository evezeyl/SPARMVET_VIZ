# @deps
# provides: make_issue_reporter() -> report(entry, message, kind)
# consumes: shiny.reactive, datetime
# consumed_by: app/handlers/home_theater.py
# doc: .claude/rules/ui_implementation_contract.md section 14 (reactive write discipline)
# @end_deps
"""app/modules/plot_issue_reporter.py
Takes a plot's error or warning from a render function to the user's panels (VIZ-STANDARD-1, V7).

A `@render.plot` function draws, so it may not write a reactive value (R1, `ui_implementation_contract.md` section 14).
The report is therefore queued and written after the flush, in a callback that runs outside any reactive context
(`session.on_flushed`). Two things make it safe:

- the callback reads the two reactive values under `reactive.isolate()`: outside a reactive context a plain `.get()`
  raises `RuntimeError: No current reactive context`, which broke the whole flush (the other plots stayed blank);
- the write is idempotent (R3): an issue that is already in the panel (same component, problem and location) is not added
  again, so a plot that is redrawn on every view, resize or tab change is reported once.

An issue goes to the two places a user looks: `session_processing_issues` (the Processing issues panel and the
"Processing Issues During Session" table of `report.qmd`) and `notification_log` (the Alerts panel, never gated by an
app features file).
"""
from __future__ import annotations

from datetime import datetime

from shiny import reactive

ISSUE_CAP = 50   # entries kept in session_processing_issues
ALERT_CAP = 20   # entries kept in the Alerts panel, as make_notifier keeps them


def make_issue_reporter(session, session_processing_issues, notification_log):
    """Return `report(entry, message, kind)`; `kind` is "error" or "warning" (the Alerts colour)."""
    queue: list = []

    def drain():
        batch = list(queue)
        queue.clear()
        with reactive.isolate():
            for entry, message, kind in batch:
                if session_processing_issues is not None:
                    current = session_processing_issues.get()
                    key = (entry.get("component"), entry.get("problem"), entry.get("location"))
                    known = any((e.get("component"), e.get("problem"), e.get("location")) == key for e in current)
                    if not known and len(current) < ISSUE_CAP:
                        session_processing_issues.set(current + [entry])
                if notification_log is not None:
                    current = notification_log.get()
                    if not any(e.get("msg") == message and e.get("type") == kind for e in current):
                        alert = {"ts": datetime.now().strftime("%H:%M:%S"), "msg": message, "type": kind}
                        notification_log.set((current + [alert])[-ALERT_CAP:])

    def report(entry: dict, message: str, kind: str = "error") -> None:
        queue.append((entry, message, kind))
        session.on_flushed(drain, once=True)

    return report
