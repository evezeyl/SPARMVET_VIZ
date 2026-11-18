# @deps
# provides: ExportFieldsStore, EXPORT_FIELD_DEFAULTS, EXPORT_LABEL_FIELD, EXPORT_LABEL_DEFAULT, REMEMBERED_EXPORT_FIELDS
# consumes: —
# consumed_by: app/handlers/export_handlers.py (the Export panel remembers its fields per session)
# doc: .claude/knowledge/decision_ledger.md (D-0288, D-0291, D-0294, D-0296)
# @end_deps
"""What the Export panel remembers for each session while the app runs (D-0288, D-0291, D-0296).

A session is one recipe plus one data batch (its `session_key`). The panel shows one set of Export fields at a time, for the
loaded recipe; this store keeps the other sessions' sets in memory so that recipe A, then B, then A shows A's choices again.
Nothing here touches the disk, and the session save and the session import do not read or write it (D-0291).

The bundle label is the one field that is NOT kept (D-0296): the user retypes it, so it starts empty on every load.
No Shiny import: the wiring is in app/handlers/export_handlers.py.
"""
from __future__ import annotations

# The bundle label field of the panel and what a fresh panel shows in it. PROVISIONAL (D-0296 says only that the label is not
# remembered): empty. The review session proposed the recipe name as the default text; Eve has not decided that.
EXPORT_LABEL_FIELD = "export_user_name"
EXPORT_LABEL_DEFAULT = ""

# The fields that are remembered per session, with the value a first visit shows (D-0294: plot format SVG, report format HTML).
# `export_include_reproducibility` is the mode tick (D-0295: it stays as built).
EXPORT_FIELD_DEFAULTS: dict = {
    "export_include_reproducibility": False,
    "export_preset": "web",
    "export_plot_format": "svg",
    "export_report_format": "html",
    "export_plot_width": 8,
    "export_plot_height": 5,
}
REMEMBERED_EXPORT_FIELDS = tuple(EXPORT_FIELD_DEFAULTS)


class ExportFieldsStore:
    """One set of remembered Export fields per session key, in memory only.

    A key is known to the store only after `begin_session(key)`: the server calls it when it tells the page that this session is
    now the one shown. A value is remembered under the key the PAGE reports it was showing when the user set it, and only if
    the store knows that key; it is never written under "the key that is current now" (two quick recipe switches would
    otherwise store one session's choices under the other)."""

    def __init__(self) -> None:
        self._by_session: dict[str, dict] = {}
        self._issued: set[str] = set()

    def begin_session(self, session_key: str) -> None:
        """The server tells the page that this session is shown from now on; values the page reports for it may be remembered."""
        if not session_key:
            raise ValueError("a session key is needed to begin an Export session")
        self._issued.add(session_key)

    def fields_for(self, session_key: str) -> dict:
        """The fields to show for a session: what it remembers over the defaults (a copy; the first visit gets the defaults)."""
        return {**EXPORT_FIELD_DEFAULTS, **self._by_session.get(session_key, {})}

    def remember(self, session_key: str, field: str, value) -> bool:
        """Remember one field under the key the page reported. Returns True when it was stored, False when it was dropped
        because the key is empty (the page had no session yet) or was never begun here; the caller shows the user the screen
        the server then sets, so a dropped value is not lost unseen (D-0050). A field that is not remembered (the label, an
        unknown name) is a programming error and raises."""
        if field not in EXPORT_FIELD_DEFAULTS:
            raise ValueError(f"'{field}' is not an Export field that is remembered per session "
                             f"(remembered: {', '.join(REMEMBERED_EXPORT_FIELDS)}; the bundle label is never remembered)")
        if not session_key or session_key not in self._issued:
            return False
        self._by_session.setdefault(session_key, {})[field] = value
        return True
