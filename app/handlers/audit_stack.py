"""app/handlers/audit_stack.py
Pipeline Audit Shiny wiring (ADR-044 / ADR-045, Phase 22-C).

Entry point:
    define_server(input, output, session, *,
                  wrangle_studio, active_cfg, active_collection_id, home_mode,
                  home_state=None, session_manager=None, notification_log=None,
                  bootloader=None, session_processing_issues=None)

Concern: the recipe's own tier 2 steps (violet), the audit steps that were ADDED to the audit pipeline (the cards of "My Adjustments": the place line, "User verified", the
reason, the bin) and the processing issues. FLOW-3 (2026-11-27): the panel has no staged ("pending") card, no reason box, no Apply button and no Pending badge; a step is created
in ONE way (Try, then "Add to audit pipeline", `trial_handlers.py`), always with its reason, and the right panel only lists and removes the steps that were added (D-0662, D-0672).

Two-Category Law (ADR-045): This file contains @render.* and @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (audit_stack), output:audit_nodes_header_ui, output:audit_nodes_tier2, output:audit_nodes_tier3, output:processing_issues_ui, effect:_handle_delete
# consumes: app/modules/audit_add.py (verified_card_line: the line "User verified" of a step added with Add to audit pipeline), app/modules/audit_shown.py (table_shown_in_panel: the right panel follows the item shown, slice 3b), app/modules/audit_places.py (nodes_reaching_node: the steps at a table shown or above it), app/modules/audit_session_save.py (save_audit_session: the session is saved after a removal), libs/utils/src/utils/display_names.py (the names of the places, shared with the lineage panel), libs/utils/src/utils/filter_words.py (value_text, no_value_words: the words of a filter step, one function), app/modules/frame_widths.py (HOME: the user space of the audit panel), app/modules/audit_places.py (PLACES_BUCKET, place_line, plots_below: the audit steps of every tier), app/modules/error_notice.py (notice — VERIF-FIX-2), app/modules/session_manager.py, libs/utils/src/utils/pipeline_error.py (PipelineError), home_mode (the reactive value of app/src/server.py)
# consumed_by: app/src/server.py
# doc: .claude/rules/ui_implementation_contract.md#12a-12c, .claude/knowledge/architecture_decisions.md#ADR-044, .claude/knowledge/architecture_decisions.md#ADR-094
# @end_deps

from shiny import reactive, render, ui

from utils.fix_text import fix_label
from utils.recipe_graph import RecipeGraphError, build_graph
from utils import display_names
from utils.filter_words import no_value_words, value_text
from utils.na_choice import na_of
from app.modules.audit_add import verified_card_line
from app.modules.audit_places import PLACES_BUCKET, nodes_reaching_node, place_line, plots_below
from app.modules.audit_session_save import save_audit_session
from app.modules.audit_shown import table_shown_in_panel
from app.modules.cache_keys import tier2_steps

# Node type display config: (icon, label)
_NODE_META = {
    "filter_row":        ("🔍", "Row Filter"),
    "exclusion_row":     ("🚫", "Exclusion"),
    "drop_column":       ("✂️",  "Drop Column"),
}


def _safe_input_suffix(node_id: str) -> str:
    """Sanitize an AuditStep id for use in a Shiny input ID.

    Shiny input IDs allow only [A-Za-z0-9_]. Legacy ghost files may contain
    UUID4 strings with hyphens, so we replace any invalid char with '_'.
    Current make_audit_step() emits hex (no hyphens), so this is a no-op for
    new nodes.
    """
    return "".join(c if c.isalnum() or c == "_" else "_" for c in node_id)


_OP_SYMBOL = {"eq": "=", "ne": "≠", "gt": ">", "ge": "≥",
              "lt": "<", "le": "≤", "in": "∈", "not_in": "∉",
              "between": "↔"}


def _format_value(val) -> str:
    """Render a filter value compactly. Lists become {a, b, c}; long strings truncate."""
    if isinstance(val, (list, tuple)):
        items = [value_text(v) for v in val]
        if len(items) <= 3:
            return "{" + ", ".join(items) + "}"
        return "{" + ", ".join(items[:3]) + f", … +{len(items)-3}}}"
    s = value_text(val)
    return s if len(s) <= 30 else s[:30] + "…"


def _params_summary(node: dict) -> str:
    text = _condition_summary(node)
    if node.get("node_type") in ("filter_row", "exclusion_row"):
        # NA-RULE-63: a step without `na` (made before the choice) always removed the rows with no value
        params = node.get("params") or {}
        text += " · " + no_value_words(na_of(params), str(params.get("column", "?")))
    return text


def _condition_summary(node: dict) -> str:
    p = node.get("params", {})
    nt = node.get("node_type", "")
    if nt == "filter_row":
        col = p.get("column", "?")
        op_raw = p.get("op", "eq")
        op = _OP_SYMBOL.get(op_raw, op_raw)
        val = p.get("value", "")
        # 'between' renders with explicit brackets: [ or ( at the lower end, ] or ) at the upper end;
        # a square bracket means the end is included (closed both, left or right, ADR-104 point 8).
        if op_raw == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
            closed = p.get("closed", "both")
            lb = "[" if closed in ("both", "left") else "("
            rb = "]" if closed in ("both", "right") else ")"
            return f"{col} ∈ {lb}{value_text(val[0])}, {value_text(val[1])}{rb}"
        return f"{col} {op} {_format_value(val)}"
    if nt == "exclusion_row":
        col = p.get("column", "?")
        return f"{col} = {_format_value(p.get('value', ''))}"
    if nt == "drop_column":
        return str(p.get("column", ""))
    return str(p)[:40]


def _reaches_no_plot(node: dict, reach_of: dict) -> bool:
    """True for an audit step written at a table (not a plot) that no plot is built from: the place is known to the graph and its plots list is empty."""
    place = node.get("place") or ""
    return bool(place) and not place.startswith("T3:") and place in reach_of and not reach_of[place]


def _place_banner(place: str, reach_of: dict, raw: dict):
    """The line of every step card that says at which table or plot, and tier, the step was written (the owner did not see it for a step on a plot, 2026-11-26; she meant the way the
    recipe's own steps are listed under their tier). Always shown, for a pending and a committed step: "Written at ResFinder: Table, T1" (the same text as the lineage panel, `place_line`), and
    under it, for a table, how many plots are built from there (or that no figure changes). PROVISIONAL words."""
    if not place:
        return ui.div(ui.div("Written at: no place is recorded in this step.", class_="spv-audit-place spv-audit-place-missing"))
    head = ui.div("Written at ", ui.tags.b(place_line(place, raw)), class_="spv-audit-place")
    if place.startswith("T3:"):
        return ui.div(head)
    if reach_of.get(place):
        n = len(reach_of[place])
        more = f"{n} plot{'s are' if n != 1 else ' is'} built from there."
    else:
        more = "No plot is built from there, so no figure changes. The table changes, and its audited file is in the export (made in Audit mode)."
    return ui.div(head, ui.div(more, class_="spv-text-xxs text-muted"))


def plot_target_dataset(raw_config: dict, p_id: str) -> str | None:
    """The `target_dataset` of one plot: the plot entry holds it directly (D-0237); None when the plot or the key is absent."""
    for gspec in (raw_config.get("analysis_groups") or {}).values():
        plot_entry = (gspec.get("plots") or {}).get(p_id)
        if plot_entry is not None:
            return plot_entry.get("target_dataset")
    top_plot = (raw_config.get("plots") or {}).get(p_id)
    return top_plot.get("target_dataset") if top_plot else None


def define_server(input, output, session, *,
                  wrangle_studio,
                  active_cfg, active_collection_id, home_mode,
                  home_state=None, session_manager=None,
                  notification_log=None, bootloader=None,
                  session_processing_issues=None):
    """Register all Pipeline Audit reactive handlers."""
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)
    _ghost_save_enabled = (
        bootloader.get_automation_setting("ghost_save", "enabled")
        if bootloader is not None else True
    )

    _graph_memo: dict = {}

    def _graph_of_open_recipe():
        """The recipe graph of the open recipe, kept while the recipe is the same object; None when it cannot be drawn (the card then says nothing of the place's reach)."""
        raw = active_cfg().raw_config
        if _graph_memo.get("raw") is not raw:
            try:
                _graph_memo.clear()
                _graph_memo.update(raw=raw, graph=build_graph(raw))
            except RecipeGraphError:
                _graph_memo.update(raw=raw, graph=None)
        return _graph_memo.get("graph")

    def _active_target_ds() -> str:
        """Return the target_dataset for the currently active plot.

        Falls back to active_collection_id() (first data analysis recipe collection) when
        home_state is absent or the active plot has no target_dataset — so the
        audit panel always shows something rather than going blank.
        """
        if home_state is not None:
            state = home_state.get()
            table_place = table_shown_in_panel(state.get("audit_shown_place"))
            if table_place:
                # Audit mode, a TABLE is shown (slice 3b): the panel is about that table, and no plot is open
                return table_place.partition(":")[2]
            subtab = state.get("active_plot_subtab") or ""
            p_id = subtab.removeprefix("subtab_") if subtab else None
            if p_id:
                ds = plot_target_dataset(active_cfg().raw_config, p_id)
                if ds:
                    return ds
        return active_collection_id()

    # ------------------------------------------------------------------
    # audit_nodes_header_ui — Data analysis recipe + Collection context line
    # ------------------------------------------------------------------

    @output
    @render.ui
    def audit_nodes_header_ui():
        cfg = active_cfg()
        collection_id = _active_target_ds()
        return ui.div(
            ui.div(f"Data analysis recipe: {cfg.raw_config.get('id')}", class_="audit-node-tier2"),
            ui.div(f"Collection: {collection_id}", class_="audit-node-tier2"),
            class_="mb-1",
        )

    # ------------------------------------------------------------------
    # audit_nodes_tier2 — Violet nodes (immutable T1/T2 steps)
    # ------------------------------------------------------------------

    @output
    @render.ui
    def audit_nodes_tier2():
        cfg = active_cfg()
        collection_id = _active_target_ds()
        # The violet nodes are the inherited Tier 2 steps (ui_implementation_contract.md section 1),
        # the ones the Result view applies on top of Tier 1; Tier 1 steps are not listed here.
        audit_steps = tier2_steps(cfg.raw_config, collection_id)

        if not audit_steps:
            return ui.div(ui.div("No Tier 2 steps defined.", class_="audit-node-tier2"))

        nodes = []
        for step in audit_steps:
            action = step.get("action", "unknown")
            label = step.get("label") or step.get("right_ingredient") or action
            nodes.append(ui.tooltip(
                ui.div(f"[Tier 2] {action}: {label}", class_="audit-node-tier2"),
                f"Action: {action}", placement="left"
            ))
        return ui.div(*nodes)

    # ------------------------------------------------------------------
    # audit_nodes_tier3 — the audit steps that were added (My Adjustments)
    # ------------------------------------------------------------------

    @output
    @render.ui
    def audit_nodes_tier3():
        if home_state is None:
            # Legacy fallback
            active_nodes = wrangle_studio.logic_stack.get()
            if not active_nodes:
                return ui.div()
            nodes = [ui.h6("Session Transformations (Tier 3)")]
            for i, node in enumerate(active_nodes):
                action = node.get("action", "unknown")
                comment = node.get("comment", "No comment")
                nodes.append(ui.tooltip(
                    ui.div(
                        ui.div(f"⚡ {action}", class_="fw-bold"),
                        ui.div(f"💬 {comment}", class_="spv-text-sm"),
                        class_="audit-node-tier3",
                    ),
                    f"Action: {action}", placement="left", id=f"node_tt_{i}"
                ))
            return ui.div(*nodes)

        # The cards are drawn again each time the panel comes back (the mode returns to Audit, the user space returns to HOME). These two reads are the only reason for the dependency.
        home_mode.get()
        try:
            input.sidebar_nav()
        except Exception:
            pass
        state = home_state.get()
        # The steps this plot is built from, at any tier: written at its own tier 3 or at a table it is built from (the audit copy runs them all in one order).
        # One step is one card here; a decision written at several places has one node per place and the card of this item is its node (the place line says which).
        active_subtab = state.get("active_plot_subtab") or ""
        by_plot = state.get("t3_audit_steps_by_plot", {}) or {}
        open_plot = active_subtab.removeprefix("subtab_")
        table_place = table_shown_in_panel(state.get("audit_shown_place"))
        reach_of: dict[str, list[str]] = {}
        graph = _graph_of_open_recipe()
        if graph is not None:
            for node in list(by_plot.get(PLACES_BUCKET, [])):
                place = node.get("place") or ""
                if place and place not in reach_of and graph.has_node(place):
                    reach_of[place] = plots_below(graph, [place])
            # a step written at a table that NO plot reads (D-0627) reaches no plot, so it belongs to none: it is listed with every plot's steps, with the words that no
            # figure changes, so that the step can be removed (PROVISIONAL: listed on every plot)
            if table_place and graph.has_node(table_place):
                # a TABLE is shown (slice 3b, D-0657; PROVISIONAL): the steps written at that table or above it on its path (`nodes_reaching_node`)
                committed_here = nodes_reaching_node(graph, by_plot.get(PLACES_BUCKET, []), table_place)
            else:
                committed_here = [n for n in by_plot.get(PLACES_BUCKET, []) if open_plot in reach_of.get(n.get("place") or "", []) or _reaches_no_plot(n, reach_of)]
        else:
            committed_here = []

        all_nodes = sorted(committed_here, key=lambda n: n.get("created_at", ""))

        # The section of the audit steps, below the recipe's own steps (Inherited, Tier 2) and apart from them: its heading is always shown, with the name of the open plot, in the style of
        # the heading of a recipe tier (`#audit_sidebar h6`). The heading words "My Adjustments" are the ones the panel already used.
        # a TABLE shown (slice 3b): the heading names the table as the lineage writes it ("ResFinder: Table, T1"); the plot's name otherwise
        if table_place:
            plot_name = place_line(table_place, active_cfg().raw_config)
            no_steps_text = f"No audit steps are written at {plot_name} or above it yet."
        else:
            plot_name = display_names.shown_name(display_names.shown_names(active_cfg().raw_config), display_names.PLOT, open_plot) if open_plot else "plot"
            no_steps_text = f"No T3 adjustments for {plot_name} yet."
        if not all_nodes:
            return ui.div(
                ui.h6(f"My Adjustments — {plot_name}"),
                ui.div(no_steps_text, class_="text-muted spv-text-sm", style="padding:4px;"),
                class_="spv-audit-mine",
            )

        adj_header = ui.div(
            ui.h6(f"My Adjustments — {plot_name}", class_="m-0 spv-flex-1"),
            class_="spv-audit-card-row",
        )

        node_els = []
        seen_ids: set[str] = set()  # one card for each decision on this list
        for node in reversed(all_nodes):  # newest first
            nid = node.get("id", "")
            if nid and nid in seen_ids:
                continue
            seen_ids.add(nid)

            is_active = node.get("active", True)
            nt = node.get("node_type", "unknown")
            icon, label = _NODE_META.get(nt, ("❓", nt))
            summary = _params_summary(node)
            reason = (node.get("reason", "") or "").strip()
            pk_warn = bool(node.get("primary_key_warning"))

            base_style = "opacity:0.45; text-decoration:line-through;" if not is_active else ""

            pk_banner = ui.div(
                "⚠️ Primary key — Primary ID/Key alignment",
                class_="spv-badge-pk-warn",
            ) if pk_warn else ui.span()

            place = node.get("place") or ""
            place_banner = _place_banner(place, reach_of, active_cfg().raw_config)
            # a step added with "Add to audit pipeline" says whether its place was user verified (PROVISIONAL words)
            verified_text = verified_card_line(node)
            verified_line = ui.div(verified_text, class_="spv-audit-verified") if verified_text else ui.span()
            reason_line = ui.div(f"Reason: {reason}", class_="spv-audit-reason") if reason else ui.span()

            id_suffix = _safe_input_suffix(nid)

            node_els.append(
                ui.div(
                    ui.div(
                        ui.span(f"{icon} {label}", class_="fw-bold spv-text-sm"),
                        ui.input_action_button(
                            f"t3_delete_{id_suffix}", "🗑",
                            class_="btn btn-sm btn-link p-0 ms-auto text-danger",
                            title="Remove this audit step (it is removed at every place it was written at)",
                        ),
                        class_="spv-audit-header-row",
                    ),
                    pk_banner,
                    place_banner,
                    verified_line,
                    ui.div(
                        summary,
                        class_="spv-text-sm mt-1",
                        style=(
                            "color:#212529; "
                            "font-family:ui-monospace,SFMono-Regular,Menlo,monospace; "
                            "background:#fff8d6; padding:2px 6px; border-radius:3px; "
                            "word-break:break-word;"
                        ),
                    ),
                    reason_line,
                    class_="audit-node-tier3",
                    style=base_style,
                )
            )

        return ui.div(adj_header, *node_els, class_="spv-audit-mine")

    # ------------------------------------------------------------------
    # Delete-step handler: removal of an added step, from every place it was written at
    # ------------------------------------------------------------------
    # We track click counts per-node-id between effect firings; nodes whose
    # click count increased since last seen are removed entirely. This is
    # idempotent — re-clicking a deleted node's ID does nothing because the
    # ID is no longer in state.

    _last_delete_clicks: dict[str, int] = {}

    @reactive.Effect
    def _handle_delete():
        """Permanent removal of a step from every place it was written at (the copies share the id; D-0314: one control, "Remove step", no reason asked)."""
        if home_state is None:
            return
        state = home_state.get()
        by_plot: dict[str, list[dict]] = {
            k: list(v) for k, v in state.get("t3_audit_steps_by_plot", {}).items()
        }

        all_known_ids: set[str] = set()
        for nodes in by_plot.values():
            all_known_ids.update(n.get("id", "") for n in nodes if n.get("id"))

        ids_to_delete: set[str] = set()
        for nid in all_known_ids:
            sid = _safe_input_suffix(nid)
            try:
                clicks = int(getattr(input, f"t3_delete_{sid}")() or 0)
            except Exception:
                continue
            prev = _last_delete_clicks.get(nid, 0)
            if clicks > prev:
                ids_to_delete.add(nid)
            _last_delete_clicks[nid] = clicks

        if not ids_to_delete:
            return

        new_by_plot = {
            k: [n for n in nodes if n.get("id") not in ids_to_delete]
            for k, nodes in by_plot.items()
        }
        removed_count = sum(len(nodes) - len(new_by_plot[k]) for k, nodes in by_plot.items())
        # REMOVED-APPLIED-STEP-NOT-SAVED (D-0680): removing an applied step is a change of what the session holds, so the session is saved as an Add saves it (a Restore then no longer brings
        # the step back). A removal needs no reason (D-0314). The count of saves moves too (AUDIT-REMOVAL-SESSION-COUNT-1): the session panel counts the saves of the session, and nothing
        # else is touched (the staged condition of the Filters panel is not cleared by a removal).
        saves = int(state.get("t3_apply_count", 0))
        will_save = session_manager is not None and _ghost_save_enabled and bool(removed_count)
        if will_save:
            saves += 1
        new_state = {**state, "t3_audit_steps_by_plot": new_by_plot, "t3_apply_count": saves}
        home_state.set(new_state)
        if will_save:
            with reactive.isolate():
                ghost_warning = save_audit_session(new_state, session_manager, notif_log=notification_log.get() if notification_log is not None else [])
                if ghost_warning:
                    _notify(ghost_warning, type="warning", duration=8)
        with reactive.isolate():      # `_notify` reads and sets the notification log: the effect must not depend on it
            _notify(
                f"🗑 {len(ids_to_delete)} audit step(s) removed "
                f"({removed_count} place(s) it was written at).",
                type="message", duration=3,
            )

    # ------------------------------------------------------------------
    # processing_issues_ui — DIAG-RUNTIME-AUDIT-1 structured error log
    # ------------------------------------------------------------------

    @output
    @render.ui
    def processing_issues_ui():
        if session_processing_issues is None:
            return ui.div()
        entries = session_processing_issues.get()
        if not entries:
            return ui.div()

        # Only show errors (not warnings) in the sidebar header, warnings go to notification_log
        errors = [e for e in entries if e.get("severity", "error") == "error"]
        if not errors:
            return ui.div()

        items = []
        for e in errors[-10:]:  # cap at 10 most recent
            ts = e.get("timestamp", "")[:19].replace("T", " ")
            comp = e.get("component", "?")
            prob = e.get("problem", "Unknown error")
            fix = e.get("fix")
            who = e.get("who")
            items.append(
                ui.div(
                    ui.div(
                        ui.span(f"[{comp}]", class_="spv-text-xs text-danger fw-bold"),
                        ui.span(ts, class_="spv-text-xs text-muted ms-1"),
                        class_="d-flex justify-content-between",
                    ),
                    ui.div(prob[:120], class_="spv-text-xs"),
                    # ADR-094/PIPELINE-ERROR-WIRE-2: fix/who are only present when the
                    # exception carried the library's real PipelineError (capture_entry()) —
                    # a plain exception's fallback entry has neither, so this stays empty.
                    ui.div(
                        fix_label(fix, who or ""),
                        class_="spv-text-xs text-muted",
                        style="margin-top:2px;",
                    ) if fix else ui.span(),
                    class_="spv-audit-issue-entry mb-1 p-1",
                    style="background:#fff0f0;border-radius:3px;border-left:3px solid #d62828;",
                )
            )

        return ui.div(
            ui.div(
                ui.tags.strong(f"Processing issues ({len(errors)})", class_="spv-text-xs text-danger"),
                class_="mb-1",
            ),
            *items,
            class_="p-2",
            id="processing_issues_panel",
        )
