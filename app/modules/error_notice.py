# @deps
# provides: function:notice, function:what_failed, function:issue_entry
# consumes: utils.fix_text (with_fix, SUGGESTION)
# consumed_by: app/handlers/session_handlers.py, app/handlers/export_handlers.py, app/handlers/home_theater.py, app/handlers/audit_stack.py, app/handlers/test_lab_handlers.py, app/modules/session_manager.py, app/modules/bundle_importer.py
# doc: .claude/knowledge/decision_ledger.md (D-0050 no silent error, D-0099 advice text form)
# @end_deps
"""app/modules/error_notice.py
The text of an error that used to be swallowed (VERIF-FIX-2; D-0050 "No silent error that is the rule.").

A handler that catches an error and goes on must tell the user, in the one form every text of the app has (D-0099): what
happened, then "Suggestion: ...". The text is built here, once, so that no place writes its own sentence and the form cannot
drift. How it reaches the screen is not decided here: an effect or an event handler calls `_notify(...)` (the Alerts panel
and a toast, `app/modules/notification_utils.py`); a render, which may not write a reactive value, uses
`make_issue_reporter` (`app/modules/plot_issue_reporter.py`) with an entry made by `issue_entry`.
"""
from __future__ import annotations

import datetime

from utils.fix_text import SUGGESTION, with_fix


def what_failed(what: str, exc: BaseException | None = None) -> str:
    """`<what happened> (<ErrorType>: <the error's own words>)`; the error is left out when there is none."""
    if exc is None:
        return what.rstrip(". ")
    detail = " ".join(str(exc).split()) or "no message"
    return f"{what.rstrip('. ')} ({type(exc).__name__}: {detail})"


def notice(what: str, suggestion: str, exc: BaseException | None = None) -> str:
    """One text for the user: what happened, then `Suggestion: <suggestion>` (exactly one period between them)."""
    return with_fix(what_failed(what, exc), f"{SUGGESTION} {suggestion}")


def issue_entry(component: str, location: str, what: str, suggestion: str, exc: BaseException | None = None,
                severity: str = "error") -> tuple[dict, str]:
    """`(entry, message)` for `make_issue_reporter`: the row of the Processing issues table and the text of the Alerts panel.

    Same keys as `utils.pipeline_error.capture_entry` writes, so the table shows it like any other issue."""
    problem = what_failed(what, exc)
    fix = f"{SUGGESTION} {suggestion}"
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "component": component,
        "problem": problem,
        "fix": fix,
        "who": "operator",
        "severity": severity,
        "location": location,
    }
    return entry, with_fix(problem, fix)
