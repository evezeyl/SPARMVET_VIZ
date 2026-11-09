"""app/handlers/session_handlers.py
Session Management panel + import/restore/delete reactive handlers.

Extracted from home_theater.py in Phase 24-B (ADR-051).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_session_server, output:session_management_ui, output:session_export_active
# consumes: shiny, pathlib, app.modules.cache_keys (canonical_hash — REPRO-RESTORE-HASH-1)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-097
# @end_deps

from pathlib import Path

from shiny import reactive, render, ui
from app.src.bootloader import bootloader


def define_session_server(input, output, session, *,
                          session_manager, current_app_features, home_state,
                          safe_input=None,
                          notification_log=None):
    """Register session-management UI + import/restore/delete reactive handlers.

    Parameters
    ----------
    session_manager : SessionManager | None
        Session persistence facade. May be None when launched without persistence.
    current_app_features : reactive.Value[str]
        Active launch app features (hyphen form, e.g. "pipeline-exploration-advanced").
    home_state : reactive.Value[dict] | None
        Shared home dashboard state (data_analysis_recipe_sha256, t3_audit_steps_by_plot, etc.).
    safe_input : callable | None
        safe_input(input, key, default) — used by the active-session export
        download to read data_analysis_recipe_id for the filename. Optional for back-compat.
    """
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    # HOM-53 (Eve, 2026-11-08): session_management_ui had no reactive dependency on
    # anything that changes after a delete — list_all_sessions() was a plain filesystem
    # scan, so the panel never re-rendered until the page reloaded. Read (R1-safe, a
    # plain .get()) at the top of the render to create the dependency; bumped by the
    # delete and delete-all handlers below.
    _session_list_version = reactive.Value(0)

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
        sessions = session_manager.list_all_sessions()

        active_key = ""
        if home_state is not None:
            state = home_state.get()
            msig = state.get("data_analysis_recipe_sha256") or ""
            dbh = state.get("data_batch_hash") or ""
            if msig and dbh:
                from app.modules.session_manager import SessionManager
                active_key = SessionManager.compute_session_key(msig, dbh)

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

        cards = []
        for grp_key, grp_sessions in groups.items():
            data_analysis_recipe_id = grp_sessions[0].get("data_analysis_recipe_id", grp_key)
            group_panels = []
            for s in grp_sessions:
                sk = s["session_key"]
                if s.get("legacy_problem"):
                    group_panels.append(ui.div(ui.tags.small(s["legacy_problem"], class_="text-danger d-block"),
                                               class_="session-card legacy mb-1"))
                    continue
                batch_short = s.get("data_batch_hash", "")[:8] or "?"
                t3_count = s.get("t3_count", 0)
                last_saved = s.get("latest_t3_saved_at") or s.get("assembled_at", "")
                label = s.get("label", "")
                safe_sk = sk.replace(":", "_")

                group_panels.append(
                    ui.div(
                        ui.div(
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
                                f"session_restore_{sk.replace(':', '_')}",
                                "Restore",
                                class_="btn-primary btn-sm",
                                style="font-size:0.72em; padding:1px 6px;",
                            ),
                            ui.input_action_button(
                                f"session_delete_{sk.replace(':', '_')}",
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

    # Session import handler
    @reactive.Effect
    @reactive.event(input.session_import_upload)
    def _handle_session_import():
        if session_manager is None:
            return
        file_info = input.session_import_upload()
        if not file_info:
            return
        try:
            zip_bytes = Path(file_info[0]["datapath"]).read_bytes()
            restored_key = session_manager.import_session_zip(zip_bytes)
            _notify(
                f"✅ Session imported: {restored_key}", type="message", duration=5
            )
        except Exception as e:
            _notify(f"❌ Import failed: {e}", type="error", duration=8)

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

    # Session restore + delete handlers are registered dynamically per session.
    # Because Shiny requires input IDs to be registered at render time, we use
    # a single reactive scan over all known sessions to catch clicks.
    @reactive.Effect
    def _handle_session_actions():
        if session_manager is None or home_state is None:
            return
        sessions = session_manager.list_all_sessions()
        for s in sessions:
            sk = s["session_key"]
            safe_sk = sk.replace(":", "_")

            # Restore
            restore_id = f"session_restore_{safe_sk}"
            try:
                clicks = getattr(input, restore_id)()
                if clicks and clicks > 0:
                    _restore_session(sk)
            except Exception:
                pass

            # Delete
            delete_id = f"session_delete_{safe_sk}"
            try:
                clicks = getattr(input, delete_id)()
                if clicks and clicks > 0:
                    session_manager.delete_session(sk)
                    _session_list_version.set(_session_list_version.get() + 1)  # HOM-53
                    _notify(
                        f"🗑 Session deleted: {sk[:24]}…",
                        type="message", duration=4,
                    )
            except Exception:
                pass

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
            try:
                new_label = (getattr(input, label_id)() or "").strip()
                if new_label != session_manager.get_session_label(sk):
                    session_manager.set_session_label(sk, new_label)
            except Exception:
                pass

    # HOM-54: confirm-before-destroy, same ui.modal/modal_button/modal_show/modal_remove
    # pattern as the propagation modal in filter_and_audit_handlers.py.
    @reactive.Effect
    @reactive.event(input.session_delete_all_btn)
    def _show_delete_all_confirm():
        if session_manager is None:
            return
        count = len(session_manager.list_all_sessions())
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
        n = session_manager.delete_all_sessions()
        _session_list_version.set(_session_list_version.get() + 1)  # HOM-53
        ui.modal_remove()
        _notify(f"🗑 Deleted {n} session(s).", type="message", duration=4)

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

        # Check data analysis recipe SHA256 vs current
        state = home_state.get()
        current_msig = state.get("data_analysis_recipe_sha256") or ""
        saved_msig = ghost.get("data_analysis_recipe_sha256", "")
        if current_msig and saved_msig and current_msig != saved_msig:
            _notify(
                "⚠️ Session was saved against a different data analysis recipe version. "
                "Audit step may not match current columns.",
                type="warning", duration=8,
            )

        # Data batch mismatch (ui_implementation_contract.md §12d — specified, found missing
        # here; the recipe check above existed, this one never did). Same ghost-vs-current
        # comparison, same non-blocking severity.
        current_dbh = state.get("data_batch_hash") or ""
        saved_dbh = ghost.get("data_batch_hash", "")
        if current_dbh and saved_dbh and current_dbh != saved_dbh:
            _notify(
                "⚠️ Session was saved against a different data batch. Row filters and "
                "exclusions may match different or no rows.",
                type="warning", duration=8,
            )

        # Load T3 ghosts list for this session
        try:
            t3_ghosts = session_manager.list_t3_ghosts(session_key)
        except LegacySessionError as exc:
            _notify(f"❌ {exc}", type="error", duration=12)
            return
        if t3_ghosts:
            # Restore most-recent T3 ghost into home_state.
            # Phase 22-J: list_t3_ghosts emits both flat t3_audit_steps (legacy) and
            # t3_audit_steps_by_plot (current). Legacy ghosts have nodes bucketed
            # under "__legacy__" — they're surfaced as orphans in the audit
            # panel until the user re-targets or deletes them.
            latest = t3_ghosts[0]
            by_plot = latest.get("t3_audit_steps_by_plot") or {}

            # REPRO-RESTORE-HASH-1 (ADR-097 decision 3/§6d): self-consistency check, not a
            # comparison against "current" T3 — there is no independent current copy to
            # compare against, restore is about to replace it with exactly this. Recompute
            # the hash from the ghost's own content and compare to its own stored field;
            # a mismatch means the ghost file was corrupted or hand-edited outside the app.
            # Empty stored hash = a ghost written before this field existed — nothing to
            # check, not a mismatch.
            from app.modules.cache_keys import canonical_hash as _canonical_hash
            _saved_t3_sha = latest.get("t3_audit_steps_sha256", "")
            if _saved_t3_sha:
                _recomputed = _canonical_hash({
                    "t3_audit_steps_by_plot": by_plot,
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

            new_state = {
                **state,
                "t3_audit_steps_by_plot": by_plot,
                "t3_plot_overrides": latest.get("t3_plot_overrides", {}),
                "tier_toggle": latest.get("tier_toggle", "T2"),
                "t3_ghost_file": latest.get("file", ""),
                "t3_ghost_saved_at": latest.get("saved_at", ""),
                "_pending_t3_nodes": [],
            }
            home_state.set(new_state)
            saved_log = latest.get("notification_log", [])
            if saved_log and notification_log is not None:
                notification_log.set(saved_log)
            legacy_n = len(by_plot.get("__legacy__", []))
            extra = (f" ({legacy_n} orphaned legacy node(s) — see audit panel)"
                     if legacy_n else "")
            _notify(
                f"✅ Session restored ({latest.get('saved_at','')[:16]}){extra}. "
                f"{len(t3_ghosts)} save(s) available for this batch.",
                type="message", duration=6,
            )
        else:
            _notify(
                "✅ Assembly session found. No T3 saves — starting fresh T3.",
                type="message", duration=5,
            )
