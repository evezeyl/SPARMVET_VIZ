"""
@deps
provides: function:open_panels_after_redraw
consumed_by: app/handlers/home_theater.py, app/tests/test_sidebar_open_panels.py, app/tests/test_left_sidebar_redraw_wiring.py
doc: .claude/rules/ui_implementation_contract.md#11e
@end_deps

Which panels of the left sidebar are open after the app draws the sidebar again (D-0502). Pure logic, no Shiny.

The user may open a panel and close another one; a redraw the app makes by itself must not undo that. The panels named by the
fixed list open only at the first draw, and for a panel that is new in the redraw.
"""
from typing import Optional, Sequence


def open_panels_after_redraw(
    fixed_open: Sequence[str],
    existing: Sequence[str],
    previous_existing: Optional[Sequence[str]],
    previous_open: Optional[Sequence[str]],
) -> list[str]:
    """The panels to draw open: the user's own choice for a panel that was there before, the fixed list for a new one.

    `previous_open` is None when the page has not told the app which panels are open (first draw, or the answer is not
    there yet): the fixed list decides. A panel that no longer exists is not in the result (it cannot be opened).
    """
    if previous_open is None or previous_existing is None:
        return [name for name in existing if name in fixed_open]
    was_there = set(previous_existing)
    was_open = set(previous_open)
    return [
        name
        for name in existing
        if (name in was_open if name in was_there else name in fixed_open)
    ]
