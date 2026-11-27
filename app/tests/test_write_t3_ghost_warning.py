"""save_audit_session's failure path (ADR-094/PIPELINE-ERROR-WIRE-2, 2026-11-08; FLOW-3: the function is public in `app/modules/audit_session_save.py`).

Before this fix: a failed T3 ghost save built a full PipelineError, printed it to the
server console, and returned nothing — the user had no way to know their T3 state
would not survive a page refresh. Now it returns a warning string (problem + fix) that
the callers ("Add to audit pipeline" in trial_handlers, the removal of a step in audit_stack) show via _notify. This test covers
the pure function in isolation; the caller wiring is exercised indirectly by the
browser tests of the Add (`test_audit_add_browser.py`).
"""
from app.modules.audit_session_save import save_audit_session


class _BrokenSessionManager:
    writable = True

    def write_t3_ghost(self, **kwargs):
        raise OSError("Read-only file system: '/sessions'")


class _WorkingSessionManager:
    writable = True

    def write_t3_ghost(self, **kwargs):
        return None


_STATE = {
    "data_analysis_recipe_sha256": "abc123",
    "data_batch_hash": "def456",
    "data_analysis_recipe_id": "test_recipe",
    "audit_pipeline": [],
    "t3_plot_overrides": {},
}


def test_returns_none_on_success():
    assert save_audit_session(_STATE, _WorkingSessionManager()) is None


def test_returns_a_warning_with_the_fix_text_on_failure():
    warning = save_audit_session(_STATE, _BrokenSessionManager())
    assert warning is not None
    assert "T3 ghost save failed" in warning
    assert "writable" in warning  # the fix text, not just the raw OSError


def test_keys_that_are_missing_give_a_warning_and_no_write_attempt():
    """VERIF-FIX-2 (D-0050 "No silent error that is the rule."): it returned None here and the screen said 'audit steps applied'
    although nothing was saved. It still makes no write attempt; it now says so (details: test_session_keys_missing_told.py)."""
    warning = save_audit_session({}, _BrokenSessionManager())
    assert warning is not None and "not saved" in warning and "Suggestion:" in warning


def test_not_writable_folder_says_not_saved_and_does_not_try():
    class _Off(_WorkingSessionManager):
        writable = False

        def write_t3_ghost(self, **kwargs):
            raise AssertionError("must not be called")

    warning = save_audit_session(_STATE, _Off())
    assert "not saved" in warning and "user folder cannot be written" in warning
