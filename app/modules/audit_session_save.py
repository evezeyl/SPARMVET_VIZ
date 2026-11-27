"""Saving the audit steps in the session (HOME, Audit mode): the one function that writes the session file after a step is added or removed.

Pure of Shiny (a code module, importable by the handlers and by tests). It was a private function of `app/handlers/audit_stack.py` that `home_theater.py` imported across the handler boundary
(`_write_t3_ghost`); FLOW-3 (2026-11-27) made it a public function of its own module.

WHEN IT IS CALLED. After "Add to audit pipeline" (`trial_handlers.py`) and after a removal of an applied step (the bin of its card, `audit_stack.py`): only applied steps are saved, never a trial
and never a staged condition (D-0302, D-0314). It never raises: a failure to save is a plain warning that the caller shows (D-0050: nothing is lost silently).

PROVISIONAL (the builder's words): every sentence of the warnings.

# @deps
# provides: function:save_audit_session
# consumes: app/modules/session_manager.py (SessionManager.write_t3_ghost, compute_session_key), app/modules/error_notice.py (notice), libs/utils/src/utils/pipeline_error.py (PipelineError)
# consumed_by: app/handlers/audit_stack.py, app/handlers/home_theater.py, app/tests/test_write_t3_ghost_warning.py, app/tests/test_session_keys_missing_told.py
# doc: .claude/rules/ui_implementation_contract.md#12d, .claude/knowledge/architecture_decisions.md#ADR-094, .claude/knowledge/decision_ledger.md (D-0302, D-0314, D-0680)
# @end_deps
"""
from __future__ import annotations

from app.modules.error_notice import notice
from utils.pipeline_error import PipelineError


def save_audit_session(state: dict, session_manager, notif_log: list | None = None) -> str | None:
    """Write the T3 ghost; returns a user-facing warning string on failure, None on success.

    ADR-094/PIPELINE-ERROR-WIRE-2: a failed save used to print the PipelineError to the console only; a failed save (the audit steps lost on a refresh) is invisible to the user it matters to,
    so the caller shows the returned text.
    """
    msig = state.get("data_analysis_recipe_sha256") or ""
    dbh = state.get("data_batch_hash") or ""
    if not msig or not dbh:
        missing = " and ".join(name for name, value in (("recipe", msig), ("data", dbh)) if not value)
        return "⚠️ " + notice(
            f"The audit steps were applied in this view but not saved: this session has no {missing} key yet, so there is no "
            "session file to write them to; they are lost when the page is reloaded",
            "look in the Alerts panel for a problem with the recipe or its data (the keys are computed from them), then apply "
            "again; export the bundle to keep the steps")
    from app.modules.session_manager import SessionManager
    session_key = SessionManager.compute_session_key(msig, dbh)
    if not session_manager.writable:
        return "⚠️ " + notice(
            "The audit steps were applied in this view but not saved: the user folder cannot be written",  # PROVISIONAL wording
            "export the bundle to keep the steps, or fix the user folder and restart")
    try:
        session_manager.write_t3_ghost(
            session_key=session_key,
            data_analysis_recipe_id=state.get("data_analysis_recipe_id", ""),
            data_analysis_recipe_sha256=msig,
            data_batch_hash=dbh,
            audit_steps=state.get("audit_pipeline", []),
            t3_plot_overrides=state.get("t3_plot_overrides", {}),
            label=state.get("t3_ghost_label", ""),
            notification_log=notif_log or [],
        )
    except Exception as exc:
        pe = PipelineError(
            component="AuditStack",
            problem=f"T3 ghost save failed: {type(exc).__name__}: {exc}",
            location="save_audit_session()",
            fix="Check that the session directory is writable and the deployment 'user_data' path is valid. T3 state was applied in-memory but will not survive a page refresh.",
            who="operator",
            category="t3_apply",
            surface="audit_panel",
            severity="warning",
            evidence={"session_key": session_key, "error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
        )
        print(pe.format())
        return f"⚠️ {pe.problem} {pe.fix}"
    return None
