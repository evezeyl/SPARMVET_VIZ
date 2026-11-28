"""app/handlers/session_handlers.py
Session Management panel + import/restore/delete reactive handlers.

Extracted from home_theater.py in Phase 24-B (ADR-051).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_session_server, effect:_sync_panel_inputs (the panel reads only the session key and the apply count), output:session_management_ui, output:session_export_active, effect:_handle_delete_one_confirmed (D-0378)
# consumes: app.src.bootloader (get_session_import_limits — D-0283), shiny, app.modules.error_notice (notice, issue_entry — VERIF-FIX-2), app.modules.plot_issue_reporter (make_issue_reporter), pathlib, app.modules.cache_keys (canonical_hash — REPRO-RESTORE-HASH-1), app.modules.session_manager (normalise_audit_steps, split_key_drops, key_drop_notice, session_id_collisions, session_input_id_parts)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-097
# @end_deps

from pathlib import Path

from shiny import reactive, render, ui
from shiny.types import SilentException
from app.modules.error_notice import issue_entry, notice
from app.modules.plot_issue_reporter import make_issue_reporter
from app.modules.session_manager import (
    SessionDeleteError,
    key_drop_notice,
    session_data_refusal,
    session_recipe_refusal,
    normalise_audit_steps,
    session_id_collisions,
    session_input_id_parts,
    split_key_drops,
)
from app.src.bootloader import bootloader
from app.modules.plan_composer import PlanComposerBug


_NOT_READ = object()   # a box of the screen that could not be read (does not exist yet, or failed)


def define_session_server(input, output, session, *,
                          session_manager, current_app_features, home_state,
                          safe_input=None,
                          notification_log=None,
                          session_processing_issues=None,
                          recipe_raw=None, recipe_plans=None):
    """Register session-management UI + import/restore/delete reactive handlers.

    Parameters
    ----------
    session_manager : SessionManager | None
        Session persistence facade. May be None when launched without persistence.
    current_app_features : reactive.Value[str]
        Active launch app features (hyphen form, e.g. "pipeline-exploration-advanced").
    home_state : reactive.Value[dict] | None
        Shared home dashboard state (data_analysis_recipe_sha256, audit_steps, etc.).
    safe_input : callable | None
        safe_input(input, key, default) — used by the active-session export
        download to read data_analysis_recipe_id for the filename. Optional for back-compat.
    recipe_raw : callable | None
        recipe_raw() -> the resolved dictionary of the open recipe; `split_key_drops` asks the rule of a key drop (`utils.key_drop`, by place, D-0358) about the stored
        drops of a restored session. None: nothing is judged.
    recipe_plans : callable | None
        recipe_plans() -> the engine's plan book of the open recipe (`app/modules/plan_composer.py`), or None; handed to the same rule so that it follows the column by the
        engine's plan and not by the names the recipe declares.
    """
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)
    # A render may not write a reactive value: what a render finds wrong goes through the plot issue reporter, as a plot's
    # error does (Processing issues table and Alerts panel, once, after the flush).
    _report_issue = make_issue_reporter(session, session_processing_issues, notification_log)

    # What was told for which box, so that a failure to read a box or to save a label is told once and not at every re-run of
    # the effect below (the effect re-runs whenever any box of the screen changes). `_notify` reads and then sets the
    # notification log, so it is only ever called under `reactive.isolate()`: an effect that called it in its own context would
    # depend on the log it writes and run again at every notice (R1 to R3, ui_implementation_contract.md section 14).
    _told: dict[tuple, tuple] = {}

    def _tell_once(action: str, session_key: str, token, text: str) -> None:
        if _told.get((action, session_key)) == (token, text):
            return
        _told[(action, session_key)] = (token, text)
        with reactive.isolate():
            _notify(text, type="error", duration=10)

    # The click count of every Restore and Delete button the effect below has already acted on. A click count only ever
    # grows, so "the count is above zero" is true for ever after the first click: the effect acts when the count is HIGHER
    # than the one it handled, the pattern of `audit_stack._last_delete_clicks`. A card that is drawn again sends 0 and starts over.
    _handled_clicks: dict[tuple[str, str], int] = {}

    def _is_new_click(kind: str, session_key: str, clicks) -> bool:
        count = int(clicks or 0)
        previous = _handled_clicks.get((kind, session_key), 0)
        _handled_clicks[(kind, session_key)] = count
        return count > previous

    # HOM-53 (Eve, 2026-11-08): session_management_ui had no reactive dependency on
    # anything that changes after a delete — list_all_sessions() was a plain filesystem
    # scan, so the panel never re-rendered until the page reloaded. Read (R1-safe, a
    # plain .get()) at the top of the render to create the dependency; bumped by the
    # delete and delete-all handlers below.
    _session_list_version = reactive.Value(0)

    # HOME-SESSION-PANEL-REDRAWS-ON-ANY-STATE: the panel shows the session key of the open recipe and data and the saves counted per session; nothing else of `home_state`. Reading the whole
    # state in the render drew the panel again on every write (a tab, a Show in Audit mode, a folded accordion) and closed the session group the person had opened. What the panel needs is
    # copied into a value of its own by an effect with an equality guard (section 14, R3): the session key, and the apply count (an Apply writes a save, so the count of saves changes);
    # the render reads only that value (R1).
    _panel_inputs = reactive.Value(("", 0))

    @reactive.Effect
    def _sync_panel_inputs():
        key, applies = "", 0
        if home_state is not None:
            state = home_state.get()
            msig = state.get("data_analysis_recipe_sha256") or ""
            dbh = state.get("data_batch_hash") or ""
            if msig and dbh:
                from app.modules.session_manager import SessionManager
                key = SessionManager.compute_session_key(msig, dbh)
            applies = int(state.get("audit_saves_count", 0) or 0)
        with reactive.isolate():
            if _panel_inputs.get() != (key, applies):
                _panel_inputs.set((key, applies))

    # ── 22-D: Session Management Panel ────────────────────────────────────────

    @output
    @render.ui
    def session_management_ui():
        """Session Management panel — gated by session_management_enabled flag.

        Gated by the flag, never by an app features name (ADR-053).
        """
        if not bootloader.is_enabled("session_management_enabled"):
            return ui.div()

        if session_manager is None:
            return ui.div(ui.p("Session manager unavailable.", class_="text-muted small"))

        _session_list_version.get()  # HOM-53: subscribe, re-render after delete/delete-all
        sessions, unreadable = session_manager.scan_sessions()
        for item in unreadable:
            if item.get("kind") == "save":
                # the session IS in the list; only this save is left out of its count and cannot be restored
                what = (f"The save {item['name']} of the session {item['session_key']} could not be read, so it is not counted "
                        "in the saves of this session and Restore skips it")
                remedy = ("restore the file from a copy, or delete this file by hand; the session and its other saves are "
                          "not affected")
            else:
                what = f"The file {item['name']} of the session {item['session_key']} could not be read, so the session is not in this list"
                remedy = "restore the file from a copy, or delete the session folder by hand and record the steps again"
            _report_issue(*issue_entry("SessionManager", f"{item['session_key']}/{item['name']}", what, remedy, item["reason"]), "error")

        active_key, _applies = _panel_inputs.get()      # the apply count only draws the panel again: an Apply wrote a save, the list counts it

        export_active_btn = (
            ui.download_button(
                "session_export_active",
                "💾 Export Active Session (.zip)",
                class_="btn-outline-primary btn-sm w-100 mb-1",
            )
            if active_key
            else ui.div()
        )

        header = ui.div(
            ui.p("Session Management", class_="ultra-small fw-bold mb-1"),
            export_active_btn,
            ui.div(
                ui.input_file(
                    "session_import_upload", None,
                    accept=[".zip"], multiple=False,
                ),
                ui.tags.small("Import a .zip session", class_="text-muted"),
                class_="upload-row mb-1",
            ),
        )

        if not sessions:
            return ui.div(
                header,
                ui.p("No saved sessions.", class_="text-muted small"),
            )

        # Group sessions by data_analysis_recipe_sha256[:12]
        groups: dict[str, list] = {}
        for s in sessions:
            grp = s.get("data_analysis_recipe_sha256", "")[:12] or "unknown"
            groups.setdefault(grp, []).append(s)

        id_parts = session_input_id_parts([s["session_key"] for s in sessions])
        collisions = session_id_collisions([s["session_key"] for s in sessions])
        clashing = {k for g in collisions for k in g}
        notice_box = ui.div()
        if collisions:
            # PROVISIONAL wording. Nothing silent (D-0050): the user is told why two cards look alike.
            names = "; ".join(" and ".join(f"'{k}'" for k in g) for g in collisions)
            notice_box = ui.div(ui.tags.small(
                f"Some stored session folders have names that differ only in a character the screen cannot tell apart: {names}. "
                "Each of their cards shows the exact folder name; a button acts only on the folder named on its own card.",
                class_="text-danger d-block"), class_="mb-1")
        cards = []
        for grp_key, grp_sessions in groups.items():
            data_analysis_recipe_id = grp_sessions[0].get("data_analysis_recipe_id", grp_key)
            group_panels = []
            for s in grp_sessions:
                sk = s["session_key"]
                if s.get("legacy_problem"):
                    # A refused session can be deleted from the panel (D-0312); it cannot be restored.
                    group_panels.append(ui.div(
                        ui.tags.small(s["legacy_problem"], class_="text-danger d-block"),
                        ui.input_action_button(
                            f"session_delete_{id_parts[sk]}", "Delete Session",
                            class_="btn-outline-danger btn-sm mt-1",
                            style="font-size:0.72em; padding:1px 6px;"),
                        class_="session-card legacy mb-1"))
                    continue
                batch_short = s.get("data_batch_hash", "")[:8] or "?"
                t3_count = s.get("t3_count", 0)
                last_saved = s.get("latest_t3_saved_at") or s.get("assembled_at", "")
                label = s.get("label", "")
                safe_sk = id_parts[sk]

                group_panels.append(
                    ui.div(
                        ui.div(
                            ui.tags.small(f"Folder: {sk}", class_="text-danger d-block", style="font-size:0.7em;")
                            if sk in clashing else ui.div(),
                            ui.tags.small(
                                f"Batch: {batch_short} · {t3_count} save(s)",
                                class_="text-muted d-block",
                                style="font-size:0.7em;",
                            ),
                            # REPRO-SESSION-LABELS-1 (#50): free-text description per
                            # session, saved on blur. Distinguishes sessions of the same
                            # recipe against different data batches better than a raw
                            # hash prefix does.
                            ui.input_text(
                                f"session_label_input_{safe_sk}", None,
                                value=label, placeholder="Describe this session…",
                                update_on="blur",
                                width="100%",
                            ),
                            ui.tags.small(
                                last_saved[:16].replace("T", " ") if last_saved else "—",
                                class_="text-muted d-block",
                                style="font-size:0.68em;",
                            ),
                        ),
                        ui.div(
                            ui.input_action_button(
                                f"session_restore_{safe_sk}",
                                "Restore",
                                class_="btn-primary btn-sm",
                                style="font-size:0.72em; padding:1px 6px;",
                            ),
                            ui.input_action_button(
                                f"session_delete_{safe_sk}",
                                "Delete Session",
                                class_="btn-outline-danger btn-sm",
                                style="font-size:0.72em; padding:1px 6px;",
                            ),
                            class_="d-flex gap-1 mt-1 flex-wrap",
                        ),
                        class_="spv-panel p-2 mb-1",
                        style="font-size:0.78em;",
                    )
                )

            cards.append(
                ui.accordion_panel(
                    f"📁 {data_analysis_recipe_id}",
                    *group_panels,
                )
            )

        return ui.div(
            header,
            notice_box,
            ui.accordion(*cards, id="session_groups_accordion", multiple=True),
            # HOM-54: unlike the per-session Delete, this is confirm-gated (a modal) since
            # it removes every session at once — matches the ui.modal/modal_button pattern
            # already used elsewhere (e.g. the propagation modal in
            # filter_and_audit_handlers.py), not the single-delete's immediate-click.
            ui.input_action_button(
                "session_delete_all_btn", "🗑 Delete All Sessions",
                class_="btn-outline-danger btn-sm w-100 mt-2",
                style="font-size:0.72em;",
            ),
        )

    # Session import (D-0281, D-0283): the zip is checked and, when its key exists, the user is asked BEFORE anything is
    # written. The waiting zip is kept in memory only (a cancelled import leaves no file behind); it is plain handler
    # state, written only from the effects below and never read by a render (ui_implementation_contract.md section 14).
    _waiting_import: dict = {}

    def _finish_import(on_exists: str | None, zip_bytes: bytes) -> None:
        from app.modules.session_manager import SessionKeyExists
        try:
            restored_key = session_manager.import_session_zip(
                zip_bytes, limits=bootloader.get_session_import_limits(), on_exists=on_exists)
        except SessionKeyExists as exc:
            _waiting_import["zip"] = zip_bytes
            ui.modal_show(ui.modal(
                ui.p("A session with this key already exists. Replace it, keep both, or cancel?"),
                ui.p(f"Key: {exc.session_key}"),
                ui.p("Replace: the stored session is replaced by the imported one. Keep both: the imported one is stored "
                     "next to it and listed as imported. Cancel: nothing is written."),
                title="This session already exists",
                easy_close=False,
                footer=ui.TagList(
                    ui.input_action_button("session_import_cancel", "Cancel", class_="btn btn-outline-secondary btn-sm"),
                    ui.input_action_button("session_import_keep", "Keep both", class_="btn btn-outline-primary btn-sm"),
                    ui.input_action_button("session_import_replace", "Replace", class_="btn btn-outline-danger btn-sm"),
                ),
            ))
            return
        except Exception as e:
            _notify(f"❌ Import failed: {e}", type="error", duration=12)
            return
        _session_list_version.set(_session_list_version.get() + 1)
        what = {"replace": "replaced the stored session", "keep_both": "stored next to the existing one, listed as imported"}.get(on_exists)
        _notify(f"✅ Session imported: {restored_key}" + (f" ({what})" if what else ""), type="message", duration=6)

    @reactive.Effect
    @reactive.event(input.session_import_upload)
    def _handle_session_import():
        if session_manager is None:
            return
        file_info = input.session_import_upload()
        if not file_info:
            return
        _waiting_import.clear()
        try:
            zip_bytes = Path(file_info[0]["datapath"]).read_bytes()
        except Exception as e:
            _notify(f"❌ Import failed: {e}", type="error", duration=12)
            return
        _finish_import(None, zip_bytes)

    def _answer_import(on_exists: str | None) -> None:
        zip_bytes = _waiting_import.pop("zip", None)
        ui.modal_remove()
        if on_exists is None:
            return
        if zip_bytes is None:
            _notify("No imported zip is waiting; nothing was written. Suggestion: upload the zip again.", type="warning", duration=8)
            return
        _finish_import(on_exists, zip_bytes)

    @reactive.Effect
    @reactive.event(input.session_import_replace)
    def _handle_import_replace():
        _answer_import("replace")

    @reactive.Effect
    @reactive.event(input.session_import_keep)
    def _handle_import_keep():
        _answer_import("keep_both")

    @reactive.Effect
    @reactive.event(input.session_import_cancel)
    def _handle_import_cancel():
        _answer_import(None)

    # ── Phase 25-G: Active-session export (.zip) ─────────────────────────────
    @render.download(filename=lambda: _active_session_export_filename())
    async def session_export_active():
        """Zip the active session directory (_sessions/{session_key}/) → bytes."""
        if session_manager is None or home_state is None:
            yield b""
            return
        state = home_state.get()
        msig = state.get("data_analysis_recipe_sha256") or ""
        dbh = state.get("data_batch_hash") or ""
        if not (msig and dbh):
            _notify(
                "No active session yet — assemble data first.",
                type="warning", duration=5,
            )
            yield b""
            return
        from app.modules.session_manager import SessionManager
        sk = SessionManager.compute_session_key(msig, dbh)
        try:
            yield session_manager.export_session_zip(sk)
        except Exception as e:
            _notify(f"❌ Session export failed: {e}", type="error", duration=8)
            yield b""

    def _active_session_export_filename() -> str:
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        data_analysis_recipe_id = ""
        if safe_input is not None:
            data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", "") or ""
        proj_tag = f"_{data_analysis_recipe_id}" if data_analysis_recipe_id else ""
        return f"{ts}{proj_tag}_session.zip"

    def _read_input(input_id: str, action: str, session_key: str):
        """The value of a box of the session screen. A box that does not exist yet (SilentException) is the normal state of
        a session whose card is not drawn: nothing is said. Any other failure to read it is told."""
        try:
            return getattr(input, input_id)()
        except SilentException:
            return _NOT_READ
        except Exception as exc:
            _tell_once(f"read_{action}", session_key, input_id, notice(
                f"The {action} control of the session {session_key[:24]} could not be read",
                "reload the page (F5); the session screen does not respond until the control can be read", exc))
            return _NOT_READ

    # Session restore + delete handlers are registered dynamically per session.
    # Because Shiny requires input IDs to be registered at render time, we use
    # a single reactive scan over all known sessions to catch clicks.
    @reactive.Effect
    def _handle_session_actions():
        if session_manager is None or home_state is None:
            return
        sessions = session_manager.list_all_sessions()
        id_parts = session_input_id_parts([s["session_key"] for s in sessions])
        for s in sessions:
            sk = s["session_key"]
            safe_sk = id_parts[sk]

            # Restore. The effect depends on the click box only: the restore itself runs isolated, because it reads and sets
            # `home_state` and writes the notification log (an effect that depends on what it writes runs again for ever).
            restore_id = f"session_restore_{safe_sk}"
            clicks = _read_input(restore_id, "restore", sk)
            if clicks is not _NOT_READ and _is_new_click("restore", sk, clicks):
                with reactive.isolate():
                    try:
                        _restore_session(sk)
                    except Exception as exc:
                        _notify(notice(
                            f"The session {sk[:24]} could not be restored",
                            "check that the session folder can be read and try Restore again; if it keeps failing, "
                            "delete the session and record the steps again", exc), type="error", duration=10)

            # Delete: D-0378, asks first. The click only opens the confirmation; `_handle_delete_one_confirmed` deletes.
            delete_id = f"session_delete_{safe_sk}"
            clicks = _read_input(delete_id, "delete", sk)
            if clicks is not _NOT_READ and _is_new_click("delete", sk, clicks):
                with reactive.isolate():
                    _ask_delete_one(sk)

            # Label (REPRO-SESSION-LABELS-1, #50): saved on blur (ui.input_text's own
            # update_on="blur"), not a separate button. Idempotent guard (R3,
            # ui_implementation_contract.md §14) against the STORED label, not the
            # rendered default — this effect re-scans every known label input on every
            # session action, so without the guard an unrelated restore/delete click
            # elsewhere would re-write every label to its current (possibly unchanged)
            # box value on every pass; comparing to storage makes repeats no-ops and
            # only ever writes when the user actually edited and blurred this box.
            # Deliberately does NOT bump _session_list_version: the box already shows
            # what the user typed, nothing else in this panel reads the label, and a
            # forced re-render would reset any OTHER session's box mid-edit (R4).
            label_id = f"session_label_input_{safe_sk}"
            label_box = _read_input(label_id, "label", sk)
            if label_box is not _NOT_READ:
                new_label = (label_box or "").strip()
                try:
                    if new_label != session_manager.get_session_label(sk):
                        session_manager.set_session_label(sk, new_label)
                except Exception as exc:
                    _tell_once("label", sk, new_label, notice(
                        f"The label of the session {sk[:24]} could not be saved",
                        "check that the session folder can be written and type the label again", exc))

    # D-0378: "Delete Session" asks for a confirmation before anything is deleted (the sentence is PROVISIONAL). The key of the
    # session the open dialog is about is kept here, read only when its Delete button is pressed; Cancel changes nothing.
    _delete_asked: dict[str, str] = {}

    def _ask_delete_one(sk: str) -> None:
        _delete_asked["sk"] = sk
        try:
            label = (session_manager.get_session_label(sk) or "").strip()
        except Exception:
            label = ""
        shown = label or sk
        ui.modal_show(ui.modal(
            ui.p("Delete this session? It cannot be undone."),
            ui.p(ui.tags.strong(shown), class_="mb-0 text-break"),
            title="Delete session?",
            easy_close=True,
            footer=ui.TagList(
                ui.modal_button("Cancel"),
                ui.input_action_button("session_delete_one_confirm", "Delete", class_="btn btn-sm"),
            ),
        ))

    @reactive.Effect
    @reactive.event(input.session_delete_one_confirm)
    def _handle_delete_one_confirmed():
        sk = _delete_asked.pop("sk", None)
        if session_manager is None or sk is None:
            ui.modal_remove()
            return
        try:
            session_manager.delete_session(sk)
        except Exception as exc:
            ui.modal_remove()
            _notify(notice(
                f"The session {sk[:24]} could not be deleted",
                "close any program that uses the session folder, check that it can be written and try again", exc),
                type="error", duration=10)
            return
        _session_list_version.set(_session_list_version.get() + 1)  # HOM-53
        ui.modal_remove()
        _notify(f"🗑 Session deleted: {sk[:24]}…", type="message", duration=4)

    # HOM-54: confirm-before-destroy, same ui.modal/modal_button/modal_show/modal_remove
    # pattern as the propagation modal in filter_and_audit_handlers.py.
    @reactive.Effect
    @reactive.event(input.session_delete_all_btn)
    def _show_delete_all_confirm():
        if session_manager is None:
            return
        count = len(session_manager.list_all_sessions())
        if not session_manager.writable:
            _notify(session_manager.not_writable_text(), type="warning", duration=8)
            return
        ui.modal_show(ui.modal(
            f"This permanently deletes all {count} saved session(s). This cannot be undone.",
            title="Delete all sessions?",
            easy_close=True,
            footer=ui.TagList(
                ui.modal_button("Cancel"),
                ui.input_action_button(
                    "session_delete_all_confirm", "Delete All",
                    class_="btn btn-outline-danger btn-sm",
                ),
            ),
        ))

    @reactive.Effect
    @reactive.event(input.session_delete_all_confirm)
    def _handle_delete_all_confirmed():
        if session_manager is None:
            return
        try:
            n = session_manager.delete_all_sessions()
        except Exception as exc:
            # what was and was not deleted, in plain words; the sessions that were deleted are gone from the list at once
            _session_list_version.set(_session_list_version.get() + 1)
            ui.modal_remove()
            if isinstance(exc, SessionDeleteError):
                what = (f"{len(exc.deleted)} session(s) were deleted; the session {exc.failed_key[:24]} could not be deleted and "
                        f"{len(exc.not_attempted)} more were not tried, so {1 + len(exc.not_attempted)} session(s) are still there")
                cause = exc.cause
            else:
                what = "The sessions could not be deleted; it is not known how many are still there"
                cause = exc
            _notify("❌ " + notice(what, "close any program that uses the session folders, check that they can be written and "
                                         "click Delete All Sessions again", cause), type="error", duration=12)
            return
        _session_list_version.set(_session_list_version.get() + 1)  # HOM-53
        ui.modal_remove()
        _notify(f"🗑 Deleted {n} session(s).", type="message", duration=4)

    def _tell_skipped_saves(skipped_saves: list[dict], restored: dict | None) -> None:
        """A save that cannot be read is still skipped; the user is told which one, why, and what was restored instead (D-0050).

        File names hold their time stamp, so a skipped name that sorts after the restored one is a NEWER save."""
        for item in skipped_saves:
            if restored is None:
                what = (f"The save {item['name']} of this session could not be read and was skipped; no readable save is left, "
                        "so nothing was restored and the audit steps in this view are unchanged")
            elif item["name"] > Path(restored["file"]).name:
                what = (f"The newest save {item['name']} of this session could not be read and was skipped; the OLDER save of "
                        f"{restored.get('saved_at', '')[:16]} was restored instead")
            else:
                what = f"The older save {item['name']} of this session could not be read and was skipped"
            remedy = (("check the audit steps of this view before you go on; " if restored is None
                       else "check the restored audit steps before you go on; ")
                      + "the damaged file stays in the session folder, keep it or delete it by hand")
            _notify("⚠️ " + notice(what, remedy, item["reason"]), type="warning", duration=12)

    def _open_recipe_id() -> str:
        """The id of the recipe open in this view: the recipe box, or the deployment's default when the box is hidden."""
        value = safe_input(input, "data_analysis_recipe_id", "") if safe_input is not None else ""
        if not value:
            finder = getattr(bootloader, "get_default_data_analysis_recipe_or_none", None)
            value = finder() if finder else ""
        return value or ""

    def _restore_session(session_key: str) -> None:
        """Run T1/T2 restore + open T3 ghost picker notification."""
        if session_manager is None or home_state is None:
            return

        from app.modules.session_manager import LegacySessionError
        try:
            ghost = session_manager.read_assembly_ghost(session_key)
        except LegacySessionError as exc:
            _notify(f"❌ {exc}", type="error", duration=12)
            return
        if ghost is None:
            _notify("❌ Session assembly record not found.", type="error", duration=6)
            return

        # D-0317: a session of another recipe is refused: nothing is applied and nothing is changed. Compared: the recipe id
        # of the session record with the id of the recipe open in this view. The same id with another content hash (the recipe
        # was edited) is NOT covered by D-0317: it keeps the warning below. PROVISIONAL wording.
        refusal = session_recipe_refusal(ghost, _open_recipe_id(), session_key)
        if refusal:
            _notify("❌ " + refusal, type="error", duration=12)
            return

        # G1 (Eve 2026-11-28): audit steps never mix across data. A session made on other data is refused: nothing of it is put into the state.
        # Compared: the data key of the record with the data key HOME keeps for the files now on disk (`_sync_session_provenance`).
        state = home_state.get()
        data_refusal = session_data_refusal(ghost, state.get("data_batch_hash") or "", state.get("data_files"))
        if data_refusal:
            _notify("❌ " + data_refusal, type="error", duration=20)
            return

        # Check data analysis recipe SHA256 vs current
        current_msig = state.get("data_analysis_recipe_sha256") or ""
        saved_msig = ghost.get("data_analysis_recipe_sha256", "")
        if current_msig and saved_msig and current_msig != saved_msig:
            _notify(
                "⚠️ Session was saved against a different data analysis recipe version. "
                "Audit step may not match current columns.",
                type="warning", duration=8,
            )

        # A comparison needs both keys. When one is missing it did not happen, and that is said (D-0050): without it the
        # restored steps look checked when they were not. The DATA keys are not here: a missing data key is refused above.
        _not_compared = [f"the {name} key of {where}"
                         for name, current, saved in (("recipe", current_msig, saved_msig),)
                         for where, value in (("the open view", current), ("the saved session", saved)) if not value]
        if _not_compared:
            _notify("⚠️ " + notice(
                "The saved audit steps could not be compared with the open recipe and data, so nobody checked that they were "
                "made on them (missing: " + ", ".join(_not_compared) + ")",
                "load the recipe and its data in this view first, then restore again, or check the steps by hand before you go on"),
                type="warning", duration=10)

        # Load T3 ghosts list for this session
        try:
            t3_ghosts, skipped_saves = session_manager.scan_t3_ghosts(session_key)
        except LegacySessionError as exc:
            _notify(f"❌ {exc}", type="error", duration=12)
            return
        _tell_skipped_saves(skipped_saves, t3_ghosts[0] if t3_ghosts else None)
        if t3_ghosts:
            # Restore the most recent save into home_state: the audit steps are ONE flat list (`audit_pipeline`, each step with its `place`); a file of another format number never gets here
            # (every reader refuses it as a whole, D-0312).
            latest = t3_ghosts[0]
            steps = latest.get("audit_pipeline") or []

            # REPRO-RESTORE-HASH-1 (ADR-097 decision 3/§6d): self-consistency check, not a
            # comparison against "current" T3 — there is no independent current copy to
            # compare against, restore is about to replace it with exactly this. Recompute
            # the hash from the ghost's own content and compare to its own stored field;
            # a mismatch means the ghost file was corrupted or hand-edited outside the app.
            # Empty stored hash = a ghost written before this field existed — nothing to
            # check, not a mismatch.
            from app.modules.cache_keys import canonical_hash as _canonical_hash
            _saved_t3_sha = latest.get("audit_steps_sha256", "")
            if _saved_t3_sha:
                _recomputed = _canonical_hash({
                    "audit_pipeline": steps,
                    "t3_plot_overrides": latest.get("t3_plot_overrides", {}),
                })
                if _recomputed != _saved_t3_sha:
                    _notify(
                        "⚠️ This session's T3 steps do not match their own recorded "
                        "checksum — the saved file may have been edited or corrupted "
                        "outside the app. Review the restored audit steps before trusting "
                        "them.",
                        type="warning", duration=10,
                    )

            # NA-RULE-63: steps made before the choice `na` existed are carried as "remove", what they always
            # did. After the checksum above, which is over the file as it was written.
            steps = normalise_audit_steps(steps)
            # D-0297, by place (D-0358): a stored step that drops a column a join still needs is not restored (a file saved before the rule, or written by hand); the rest
            # is, and the user is told which step and why. The recipe is the open one.
            try:
                steps, refused_key_drops = split_key_drops(steps, recipe_raw() if recipe_raw is not None else None, recipe_plans() if recipe_plans is not None else None)
            except PlanComposerBug:
                return      # the plain notice was shown by `recipe_plans` (an error of the app): nothing is restored
            if refused_key_drops:
                _kept_ids = {n.get("id") for n in steps}
                _notify("⚠️ " + key_drop_notice(refused_key_drops, len(_kept_ids)), type="warning", duration=15)
            new_state = {
                **state,
                "audit_pipeline": steps,
                "t3_plot_overrides": latest.get("t3_plot_overrides", {}),
                "t3_ghost_file": latest.get("file", ""),
                "t3_ghost_saved_at": latest.get("saved_at", ""),
            }
            home_state.set(new_state)
            saved_log = latest.get("notification_log", [])
            if saved_log and notification_log is not None:
                notification_log.set(saved_log)
            _notify(
                f"✅ Session restored ({latest.get('saved_at','')[:16]}). "
                f"{len(t3_ghosts)} save(s) available for this batch.",
                type="message", duration=6,
            )
        else:
            _notify(
                "✅ Assembly session found. It has no saved audit steps, so nothing was restored and the audit steps in this "
                "view are unchanged.",
                type="message", duration=5,
            )
