# @deps
# provides: make_notifier() factory — returns a _notify(msg, type, duration) callable that calls ui.notification_show and appends to a reactive log
# consumes: shiny.ui, datetime
# consumed_by: app/handlers/session_handlers.py, app/handlers/audit_stack.py, app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/export_handlers.py, app/handlers/data_import_handlers.py
# @end_deps
"""app/modules/notification_utils.py
Shared notification factory for user-facing alerts (UX-NOTIF-1).

make_notifier(notification_log) → _notify(msg, type, duration)

The returned callable:
  - calls ui.notification_show(msg, type=type, duration=duration)
  - appends {"ts": "HH:MM:SS", "msg": str(msg), "type": type} to
    notification_log (keeps last 20 entries)

If notification_log is None the factory falls back to a plain
notification_show wrapper — no crash, no log.
"""

from __future__ import annotations

from datetime import datetime

from shiny import ui


def make_notifier(notification_log=None):
    """Return a _notify callable bound to notification_log.

    Parameters
    ----------
    notification_log : reactive.Value[list] | None
        Shared reactive list for the Alerts panel. When None, notifications
        are shown but not logged.

    Returns
    -------
    _notify(msg, type="message", duration=5)
        Drop-in replacement for ui.notification_show with identical call
        signature for the positional msg and keyword type/duration args.
    """

    def _notify(msg, type="message", duration=5):
        ui.notification_show(msg, type=type, duration=duration)
        if notification_log is None:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        entry = {"ts": ts, "msg": str(msg), "type": type}
        current = notification_log.get()
        updated = (current + [entry])[-20:]
        notification_log.set(updated)

    return _notify
