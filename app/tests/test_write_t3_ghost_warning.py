"""_write_t3_ghost's failure path (ADR-094/PIPELINE-ERROR-WIRE-2, 2026-11-08).

Before this fix: a failed T3 ghost save built a full PipelineError, printed it to the
server console, and returned nothing — the user had no way to know their T3 state
would not survive a page refresh. Now it returns a warning string (problem + fix) that
the caller (handle_apply, inside define_server) shows via _notify. This test covers
the pure function in isolation; the caller wiring is exercised indirectly by the
existing Playwright AUDIT-GATE-UI-1 test (apply still works end to end).
"""
from app.handlers.audit_stack import _write_t3_ghost


class _BrokenSessionManager:
    def write_t3_ghost(self, **kwargs):
        raise OSError("Read-only file system: '/sessions'")


class _WorkingSessionManager:
    def write_t3_ghost(self, **kwargs):
        return None


_STATE = {
    "data_analysis_recipe_sha256": "abc123",
    "data_batch_hash": "def456",
    "data_analysis_recipe_id": "test_recipe",
    "tier_toggle": "T2",
    "t3_audit_steps_by_plot": {},
    "t3_plot_overrides": {},
}


def test_returns_none_on_success():
    assert _write_t3_ghost(_STATE, _WorkingSessionManager()) is None


def test_returns_a_warning_with_the_fix_text_on_failure():
    warning = _write_t3_ghost(_STATE, _BrokenSessionManager())
    assert warning is not None
    assert "T3 ghost save failed" in warning
    assert "writable" in warning  # the fix text, not just the raw OSError


def test_returns_none_when_keys_are_missing_without_attempting_a_write():
    assert _write_t3_ghost({}, _BrokenSessionManager()) is None
