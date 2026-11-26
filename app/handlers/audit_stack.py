"""app/handlers/audit_stack.py
Pipeline Audit Shiny wiring (ADR-044 / ADR-045, Phase 22-C).

Entry point:
    define_server(input, output, session, *,
                  wrangle_studio, audit_pending, snapshot_steps,
                  active_cfg, active_collection_id,
                  home_state=None, session_manager=None)

Concern: T2 violet node rendering, T3 Yellow AuditStep rendering, btn_apply
         gatekeeper (blocks if any required reason field is empty), audit trail
         change tracking, audit_pending_badge_ui.

Two-Category Law (ADR-045): This file contains @render.* and @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (audit_stack), output:audit_nodes_header_ui, output:audit_nodes_tier2, output:audit_nodes_tier3, output:processing_issues_ui, output:aesthetic_style_panel_ui (22-J-10)
# consumes: libs/utils/src/utils/display_names.py (the names of the places, shared with the lineage panel), libs/utils/src/utils/filter_words.py (value_text, no_value_words: the words of a filter step, one function), app/modules/frame_widths.py (HOME: the user space of the audit panel), app/modules/audit_places.py (PLACES_BUCKET, place_words, plots_below: the audit steps of every tier), app/modules/wrangle_studio.py, app/modules/error_notice.py (notice — VERIF-FIX-2), app/modules/session_manager.py, libs/transformer/src/transformer/data_wrangler.py
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-T3APPLY-1), home_mode (the reactive value of app/src/server.py: the badge and Apply are shown in Audit mode only, D-0377)
# consumed_by: app/src/server.py
# doc: .claude/rules/ui_implementation_contract.md#12a-12c, .claude/knowledge/architecture_decisions.md#ADR-044, .claude/knowledge/architecture_decisions.md#ADR-094 (gatekeeper fix text + _write_t3_ghost warning now reach the screen, processing_issues_ui shows fix/who)
# @end_deps

from collections import Counter

from shiny import reactive, render, ui

from utils import recipe_tiers
from utils.fix_text import fix_label
from utils.recipe_graph import RecipeGraphError, build_graph
from app.modules.error_notice import notice
from utils import display_names
from utils.filter_words import no_value_words, value_text
from utils.na_choice import na_of
from utils.pipeline_error import PipelineError
from app.modules import frame_widths
from app.modules.audit_places import PLACES_BUCKET, place_line, place_words, plots_below
from app.modules.cache_keys import tier2_steps
from app.modules.session_manager import (
    make_audit_step,
    gatekeeper_blocked,
)

# Node type display config: (icon, label)
_NODE_META = {
    "filter_row":        ("🔍", "Row Filter"),
    "exclusion_row":     ("🚫", "Exclusion"),
    "drop_column":       ("✂️",  "Drop Column"),
    "aesthetic_override":("🎨", "Plot Style"),
}

_REASON_REQUIRED = {"filter_row", "exclusion_row", "drop_column"}


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
    if nt == "aesthetic_override":
        keys = [k for k in ("fill", "colour", "alpha", "shape") if k in p]
        return ", ".join(keys) if keys else "overrides"
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
                  wrangle_studio, audit_pending, snapshot_steps,
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

    # ------------------------------------------------------------------
    # Reasons typed and not yet applied are kept when the panel's content is removed (the mode leaves Audit, or another user space is
    # shown: the reason boxes leave the page and their values with them). A plain dict, not a reactive value: it is written only by the
    # effect below (idempotent: the same text gives the same dict) and read, never written, by the renders (ui_implementation_contract.md
    # section 14, R1 to R4). PROVISIONAL (the builder's choice of where the text is kept; the decision asks only that typed text is not lost).
    # ------------------------------------------------------------------
    kept_reasons: dict[str, str] = {}
    last_read: dict[str, str] = {}          # the last raw value of each box, to tell a change of the user from what the page reports

    @reactive.Effect
    def _keep_typed_reasons():
        """Remember the text of every reason box; a box that left the page keeps its last text.

        When the panel leaves the page (Exploration, another user space) Shiny reports each of its boxes as empty text, and the
        stale empty value is still there when the panel comes back: only a raw value that CHANGED while the panel is on the page
        is the user's, so only that one is kept.
        """
        if home_state is None:
            return
        state = home_state.get()
        try:
            space = input.sidebar_nav()
        except Exception:
            space = frame_widths.HOME
        panel_on_page = home_mode.get() == "audit" and space == frame_widths.HOME
        nodes = [n for v in (state.get("t3_audit_steps_by_plot", {}) or {}).values() for n in v] + list(state.get("_pending_t3_nodes", []))
        ids = {n.get("id", "") for n in nodes if n.get("id")}
        for stale in [k for k in kept_reasons if k not in ids]:
            del kept_reasons[stale]
        for stale in [k for k in last_read if k not in ids]:
            del last_read[stale]
        for nid in ids:
            try:
                val = getattr(input, f"t3_reason_{_safe_input_suffix(nid)}")()
            except Exception:
                continue                               # the box has never been on the page
            if val is None:
                continue
            changed = last_read.get(nid) != val
            last_read[nid] = val
            if panel_on_page and changed:
                kept_reasons[nid] = val

    # ------------------------------------------------------------------
    # btn_apply: commit audit steps, ghost save, release gatekeeper
    # ------------------------------------------------------------------

    @reactive.Effect
    @reactive.event(input.btn_apply)
    def handle_apply():
        """Commit pending audit nodes, at any tier.

        Pending nodes carry their `place` (`T1:<table>`, `T2:<table>` or `T3:<plot>`, set by the dialog, `filter_and_audit_handlers._stage_nodes`)
        and the bucket `plot_scope` (`PLACES_BUCKET`). Commit means appending each node, in the order staged, to t3_audit_steps_by_plot[node.plot_scope];
        the audit copy is made from that list in that order.

        Reasons are read from live `t3_reason_<id_suffix>` inputs; multiple
        propagated copies share the same suffix (because they share `id`),
        so a single reason text applies to all linked copies — which matches
        the "one decision, many places" model.
        """
        if home_state is None:
            snapshot_steps.set(wrangle_studio.logic_stack.get())
            audit_pending.set(False)
            return

        state = home_state.get()
        by_plot: dict[str, list[dict]] = {
            k: [dict(n) for n in v] for k, v in state.get("t3_audit_steps_by_plot", {}).items()
        }
        pending = [dict(n) for n in state.get("_pending_t3_nodes", [])]

        # Pull live reason text into committed + pending nodes (§14 R1/R3).
        all_committed = [n for nodes in by_plot.values() for n in nodes]
        for node in all_committed + pending:
            nid = node.get("id", "")
            if not nid:
                continue
            sid = _safe_input_suffix(nid)
            try:
                val = getattr(input, f"t3_reason_{sid}")()
                if val is not None:
                    node["reason"] = val
            except Exception:
                if kept_reasons.get(nid) and not (node.get("reason") or "").strip():
                    node["reason"] = kept_reasons[nid]       # the box is not on the page: the text typed before is used

        # Linked-id reason fan-out: if the user typed a reason on one copy,
        # propagate it to every copy sharing the id (so the user doesn't have
        # to type the same justification N times).
        reasons_by_id: dict[str, str] = {}
        for n in all_committed + pending:
            r = (n.get("reason") or "").strip()
            if r:
                reasons_by_id.setdefault(n.get("id", ""), r)
        for n in all_committed + pending:
            nid = n.get("id", "")
            if nid in reasons_by_id and not (n.get("reason") or "").strip():
                n["reason"] = reasons_by_id[nid]

        # Gatekeeper over EVERYTHING (committed + pending across all plots)
        blocked_ids = set(gatekeeper_blocked(all_committed + pending))     # ids (strings), one per copy: copies of a step share the id
        if blocked_ids:
            # one step is one id (a decision propagated to several plots has one copy per plot); its kind is the kind of its nodes
            kind_of_step: dict[str, str] = {}
            for n in all_committed + pending:
                if n.get("id") in blocked_ids:
                    kind_of_step.setdefault(n["id"], n.get("node_type", "unknown"))
            kinds = Counter(kind_of_step.values())
            kinds_text = ", ".join(f"{count} {_NODE_META.get(kind, ('', kind))[1].lower()}" for kind, count in kinds.items())
            remedy = "write a reason for each step, then press Apply"
            pe = PipelineError(
                component="AuditStack",
                problem=f"{len(kind_of_step)} T3 step(s) have no reason ({kinds_text}).",
                location="handle_apply()",
                fix=f"Suggestion: {remedy}",
                who="analyst",
                category="t3_apply",
                surface="audit_panel",
                severity="warning",
                evidence={"blocked_count": len(kind_of_step), "node_types": sorted(kinds)},
            )
            print(pe.format())
            # ADR-094/PIPELINE-ERROR-WIRE-2: the text reaches the screen (toast and Alerts panel), not only the console.
            # Apply is locked while a step has no reason, so a user gets here only when the click came before the button was
            # drawn again (ui_implementation_contract.md sections 3 and 12a): nothing is applied, nothing is saved.
            _notify("⛔ " + notice(f"Nothing was applied: {len(kind_of_step)} step(s) have no reason ({kinds_text})", remedy),
                    type="error", duration=8)
            # Persist reason edits even on block so user keeps their typing.
            home_state.set({
                **state,
                "t3_audit_steps_by_plot": by_plot,
                "_pending_t3_nodes": pending,
            })
            return

        # Commit: append each pending node into its plot_scope bucket.
        for node in pending:
            scope = node.get("plot_scope") or ""
            if not scope:
                continue
            by_plot.setdefault(scope, []).append(node)

        new_state = {
            **state,
            "t3_audit_steps_by_plot": by_plot,
            "_pending_t3_nodes": [],
            "t3_apply_count": int(state.get("t3_apply_count", 0)) + 1,
        }
        home_state.set(new_state)

        if session_manager is not None and _ghost_save_enabled:
            ghost_warning = _write_t3_ghost(
                new_state, session_manager,
                notif_log=notification_log.get() if notification_log is not None else [])
            if ghost_warning:
                _notify(ghost_warning, type="warning", duration=8)

        snapshot_steps.set(wrangle_studio.logic_stack.get())
        audit_pending.set(False)

        total_nodes = sum(len(v) for v in by_plot.values())
        # a step at a table no plot reads (D-0627): say in plain words that no figure changes, the table does (PROVISIONAL words)
        no_plot_places: list[str] = []
        graph = _graph_of_open_recipe()
        if graph is not None:
            for n in pending:
                place = n.get("place") or ""
                if place and not place.startswith("T3:") and graph.has_node(place) and not plots_below(graph, [place]) and place not in no_plot_places:
                    no_plot_places.append(place)
        extra = (f" No plot is built from {', '.join(place_words(p) for p in no_plot_places)}: no figure changes; the table changes and its audited file is in the export "
                 f"(made in Audit mode).") if no_plot_places else ""
        _notify(
            f"✅ audit steps applied — {total_nodes} node(s) across "
            f"{len({n.get('place') for v in by_plot.values() for n in v})} place(s)." + extra,
            type="message", duration=10 if extra else 4,
        )

    # ------------------------------------------------------------------
    # Track audit trail changes (pending badge)
    # ------------------------------------------------------------------

    @reactive.Effect
    def track_audit_step_changes():
        _ = wrangle_studio.apply_logic
        audit_pending.set(True)

    # ------------------------------------------------------------------
    # audit_pending_badge_ui
    # ------------------------------------------------------------------

    @output
    @render.ui
    def audit_pending_badge_ui():
        # D-0377: in Exploration the badge does nothing, so it is not shown; `audit_pending` itself is not touched by the mode switch.
        if home_mode.get() == "audit" and audit_pending.get():
            return ui.div("⏳ Pending", class_="audit-pending-badge text-center")
        return ui.div()

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
    # audit_nodes_tier3 — Yellow AuditSteps (T3 committed + pending)
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

        # The cards are drawn again each time the panel comes back (the mode returns to Audit, the user space returns to HOME): the page
        # holds the cards of the last drawing, with the reason boxes as they were drawn then, and the text typed since is in `kept_reasons`.
        # These two reads are the only reason for the dependency; no input of a reason box is read here (R4).
        home_mode.get()
        try:
            input.sidebar_nav()
        except Exception:
            pass
        state = home_state.get()
        # The steps this plot is built from, at any tier: written at its own tier 3 or at a table it is built from (the audit copy runs them all in one order).
        # One step is one card here; a decision written for several plots has one node per plot and the card of this plot is its node.
        active_subtab = state.get("active_plot_subtab") or ""
        by_plot = state.get("t3_audit_steps_by_plot", {}) or {}
        pending_all = list(state.get("_pending_t3_nodes", []))
        open_plot = active_subtab.removeprefix("subtab_")
        reach_of: dict[str, list[str]] = {}
        graph = _graph_of_open_recipe()
        if graph is not None:
            for node in list(by_plot.get(PLACES_BUCKET, [])) + pending_all:
                place = node.get("place") or ""
                if place and place not in reach_of and graph.has_node(place):
                    reach_of[place] = plots_below(graph, [place])
            # a step written at a table that NO plot reads (LINEAGE-VIEW-G, D-0627) reaches no plot, so it belongs to none: it is listed with every plot's steps, with the words that no
            # figure changes, so that its reason can be typed and the step removed (PROVISIONAL: listed on every plot)
            committed_here = [n for n in by_plot.get(PLACES_BUCKET, []) if open_plot in reach_of.get(n.get("place") or "", []) or _reaches_no_plot(n, reach_of)]
            pending_here = [n for n in pending_all if open_plot in reach_of.get(n.get("place") or "", []) or _reaches_no_plot(n, reach_of)]
        else:
            committed_here, pending_here = [], []

        # For "Applied to N plots" badge: the plots a decision was written at, at their own tier 3 (one node per plot, one id).
        scope_count_by_id: dict[str, int] = {}
        for n in list(by_plot.get(PLACES_BUCKET, [])) + pending_all:
            nid = n.get("id", "")
            if nid and (n.get("place") or "").startswith("T3:"):
                scope_count_by_id[nid] = scope_count_by_id.get(nid, 0) + 1

        all_nodes = sorted(committed_here + pending_here, key=lambda n: n.get("created_at", ""))

        # Orphan/legacy nodes for this session
        orphaned = list(by_plot.get("__legacy__", []))

        # The section of the audit steps, below the recipe's own steps (Inherited, Tier 2) and apart from them: its heading is always shown, with the name of the open plot, in the style of
        # the heading of a recipe tier (`#audit_sidebar h6`). The heading words "My Adjustments" are the ones the panel already used.
        plot_name = display_names.shown_name(display_names.shown_names(active_cfg().raw_config), display_names.PLOT, open_plot) if open_plot else "plot"
        if not all_nodes and not orphaned:
            return ui.div(
                ui.h6(f"My Adjustments — {plot_name}"),
                ui.div(f"No T3 adjustments for {plot_name} yet.", class_="text-muted spv-text-sm", style="padding:4px;"),
                class_="spv-audit-mine",
            )

        blocked_ids = set(gatekeeper_blocked(pending_all + [n for nodes in by_plot.values() for n in nodes]))
        adj_header = ui.div(
            ui.h6(f"My Adjustments — {plot_name}", class_="m-0 spv-flex-1"),
            ui.span(
                f"{len(blocked_ids)} need reason",
                class_="text-danger spv-text-xxs",
            ) if blocked_ids else ui.span(),
            class_="spv-audit-card-row",
        )

        node_els = []
        seen_ids: set[str] = set()  # avoid duplicate cards when a propagated
                                    # node lands twice in committed+pending
        for node in reversed(all_nodes):  # newest first
            nid = node.get("id", "")
            if nid and nid in seen_ids:
                continue
            seen_ids.add(nid)

            is_pending = node in pending_here
            is_active = node.get("active", True)
            nt = node.get("node_type", "unknown")
            icon, label = _NODE_META.get(nt, ("❓", nt))
            summary = _params_summary(node)
            reason = node.get("reason", "") or kept_reasons.get(nid, "")
            needs_reason = nt in _REASON_REQUIRED
            reason_empty = needs_reason and not reason.strip()
            pk_warn = bool(node.get("primary_key_warning"))
            applied_count = scope_count_by_id.get(nid, 1)

            base_style = "opacity:0.45; text-decoration:line-through;" if not is_active else ""

            pending_badge = ui.span(
                "PENDING",
                class_="spv-badge-pending",
            ) if is_pending else ui.span()

            propagation_badge = ui.span(
                f"Applied to {applied_count} plots",
                class_="spv-badge-propagation",
            ) if applied_count > 1 else ui.span()

            pk_banner = ui.div(
                "⚠️ Primary key — Primary ID/Key alignment",
                class_="spv-badge-pk-warn",
            ) if pk_warn else ui.span()

            place = node.get("place") or ""
            place_banner = _place_banner(place, reach_of, active_cfg().raw_config)

            id_suffix = _safe_input_suffix(nid)

            if needs_reason and is_active:
                reason_field = ui.div(
                    ui.input_text(
                        f"t3_reason_{id_suffix}",
                        label=None,
                        value=reason,
                        placeholder="Reason (required)…",
                    ),
                    style=(
                        "margin-top:2px;"
                        + (" border:1px solid #dc3545; border-radius:4px;" if reason_empty else "")
                    ),
                )
            else:
                reason_field = ui.span()

            node_els.append(
                ui.div(
                    ui.div(
                        ui.span(f"{icon} {label}", class_="fw-bold spv-text-sm"),
                        pending_badge,
                        propagation_badge,
                        ui.input_action_button(
                            f"t3_delete_{id_suffix}", "🗑",
                            class_="btn btn-sm btn-link p-0 ms-auto text-danger",
                            title="Delete this audit node (linked: removes from all plots)",
                        ),
                        class_="spv-audit-header-row",
                    ),
                    pk_banner,
                    place_banner,
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
                    reason_field,
                    class_="audit-node-tier3",
                    style=base_style,
                )
            )

        # Render orphaned nodes from legacy ghost loads, if any.
        if orphaned:
            node_els.append(ui.hr(class_="spv-divider"))
            node_els.append(ui.div(
                f"⚠️ {len(orphaned)} orphaned node(s) from a legacy ghost. "
                "Delete or re-target manually.",
                class_="text-muted small spv-text-xxs",
                style="padding:2px 4px;",
            ))

        return ui.div(adj_header, *node_els, class_="spv-audit-mine")

    # ------------------------------------------------------------------
    # Reason inputs are NOT eagerly synced to home_state (would re-render the
    # right sidebar on every keystroke, destroying the input mid-typing).
    # Reasons are pulled from input.t3_reason_<id> at btn_apply time — see
    # handle_apply() above. §14 R1/R3 — see ui_implementation_contract.md.
    #
    # _nodes_with_live_reasons(): non-mutating overlay used by the apply-button
    # renders. Reads each reason input and returns a fresh node list with the
    # current text merged in, so the gatekeeper accurately reflects live state
    # WITHOUT writing to home_state.
    # ------------------------------------------------------------------

    def _nodes_with_live_reasons() -> list[dict]:
        """Non-mutating overlay: every committed (per-plot) + pending node
        with the live `t3_reason_<id_suffix>` input merged into `reason`.

        Phase 22-J: reads from t3_audit_steps_by_plot (flattened) plus _pending_t3_nodes.
        Linked-id reason fan-out: a single typed reason on any copy is mirrored
        into every copy sharing the same id, so the gatekeeper sees the user's
        intent across all linked copies even if they only typed in one box.
        """
        if home_state is None:
            return []
        state = home_state.get()
        by_plot = state.get("t3_audit_steps_by_plot", {}) or {}
        flat_committed = [n for nodes in by_plot.values() for n in nodes]
        merged: list[dict] = []
        # First pass: pull live reason text per node id.
        live_reason_by_id: dict[str, str] = {}
        for n in flat_committed + list(state.get("_pending_t3_nodes", [])):
            nid = n.get("id", "")
            if not nid:
                continue
            sid = _safe_input_suffix(nid)
            try:
                val = getattr(input, f"t3_reason_{sid}")()
                if val is not None and (val or "").strip():
                    live_reason_by_id[nid] = val
            except Exception:
                if (kept_reasons.get(nid) or "").strip():
                    live_reason_by_id[nid] = kept_reasons[nid]     # the box is not on the page now: the text typed before counts
                continue
        # Second pass: build the merged overlay.
        for n in flat_committed + list(state.get("_pending_t3_nodes", [])):
            n = dict(n)
            nid = n.get("id", "")
            if nid in live_reason_by_id:
                n["reason"] = live_reason_by_id[nid]
            merged.append(n)
        return merged

    # ------------------------------------------------------------------
    # Delete-node handlers — permanent removal from t3_audit_steps / _pending_t3_nodes
    # ------------------------------------------------------------------
    # We track click counts per-node-id between effect firings; nodes whose
    # click count increased since last seen are removed entirely. This is
    # idempotent — re-clicking a deleted node's ID does nothing because the
    # ID is no longer in state.

    _last_delete_clicks: dict[str, int] = {}

    @reactive.Effect
    def _handle_delete():
        """Linked-id permanent deletion across all per-plot stacks.

        Phase 22-J / ADR-049 §12g.10: clicking the delete icon on any copy removes EVERY
        copy sharing that id from every plot's stack and from pending nodes.
        """
        if home_state is None:
            return
        state = home_state.get()
        by_plot: dict[str, list[dict]] = {
            k: list(v) for k, v in state.get("t3_audit_steps_by_plot", {}).items()
        }
        pending = list(state.get("_pending_t3_nodes", []))

        all_known_ids: set[str] = set()
        for nodes in by_plot.values():
            all_known_ids.update(n.get("id", "") for n in nodes if n.get("id"))
        all_known_ids.update(n.get("id", "") for n in pending if n.get("id"))

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
        new_pending = [n for n in pending if n.get("id") not in ids_to_delete]
        home_state.set({
            **state,
            "t3_audit_steps_by_plot": new_by_plot,
            "_pending_t3_nodes": new_pending,
        })
        # Count how many physical copies were removed (for the notification)
        removed_count = sum(
            len(nodes) - len(new_by_plot[k])
            for k, nodes in by_plot.items()
        ) + (len(pending) - len(new_pending))
        with reactive.isolate():      # `_notify` reads and sets the notification log: the effect must not depend on it
            _notify(
                f"🗑 {len(ids_to_delete)} audit decision(s) deleted "
                f"({removed_count} copy/copies across plots).",
                type="message", duration=3,
            )

    # ------------------------------------------------------------------
    # audit_stack_tools_ui — gatekeeper-aware Apply button (right sidebar bottom)
    # ------------------------------------------------------------------
    # Right sidebar is now audit-trail only: T3 nodes are authored in the left
    # panel (filter rows) or via Gallery clone. No Add buttons here.

    @output
    @render.ui
    def audit_stack_tools_ui():
        # D-0377: the Apply button writes audit steps, which Exploration never does: it is shown in Audit mode only.
        # The slot stays mounted (shell stability); only its content changes with the mode.
        if home_mode.get() != "audit":
            return ui.div()
        if home_state is None:
            return ui.div(
                ui.input_action_button("btn_apply", "Apply", class_="btn-primary w-100"),
                class_="p-2",
            )

        all_nodes = _nodes_with_live_reasons()
        blocked = gatekeeper_blocked(all_nodes)

        apply_btn = ui.tooltip(
            ui.input_action_button(
                "btn_apply", "Apply ⛔",
                class_="btn-secondary w-100",
                disabled=True,
            ),
            f"{len(blocked)} node(s) missing reason — fill in reason fields above.",
            placement="top",
        ) if blocked else ui.input_action_button(
            "btn_apply", "Apply",
            class_="btn-primary w-100",
        )

        return ui.div(
            ui.hr(class_="spv-divider-sm"),
            apply_btn,
            class_="p-2",
        )

    # ------------------------------------------------------------------
    # btn_apply_ui — gatekeeper-aware Apply button (standalone output)
    # ------------------------------------------------------------------

    @output
    @render.ui
    def btn_apply_ui():
        if home_state is None:
            return ui.input_action_button("btn_apply", "Apply", class_="btn-primary w-100")

        all_nodes = _nodes_with_live_reasons()
        blocked = gatekeeper_blocked(all_nodes)

        if blocked:
            return ui.tooltip(
                ui.input_action_button(
                    "btn_apply", "Apply ⛔",
                    class_="btn-secondary w-100",
                    disabled=True,
                ),
                f"{len(blocked)} node(s) missing reason",
                placement="top",
            )
        return ui.input_action_button("btn_apply", "Apply", class_="btn-primary w-100")

    # ------------------------------------------------------------------
    # 22-J-10: aesthetic_style_panel_ui + _handle_aesthetic_apply
    # Per-plot style overrides (fill_color, colour, alpha, shape).
    # color/shape/fill → propagation dialog; alpha → per-plot direct.
    #
    # DEFERRED (not mounted): home_theater.py no longer places this panel in the right
    # sidebar, so nothing below runs. Kept as an eventual enhancement, fork issue #15.
    # Using it broke the plot (test plan HOM-47): find the cause before mounting it again.
    # ------------------------------------------------------------------

    # Scratch state: {fill_color, colour, alpha, shape} from the latest
    # "Apply Style" press — held until the propagation choice is confirmed.
    _aesthetic_scratch = reactive.Value({})

    @output
    @render.ui
    def aesthetic_style_panel_ui():
        """Compact plot-style override form for the active plot sub-tab."""
        if home_state is None:
            return ui.div()
        state = home_state.get()
        active_sub = state.get("active_plot_subtab", "")
        existing = state.get("t3_plot_overrides", {}).get(active_sub, {})
        return ui.accordion(
            ui.accordion_panel(
                "Plot Style",
                ui.div(
                    ui.input_text(
                        "ast_fill_color", "Fill colour (hex or name)",
                        value=existing.get("fill_color", ""),
                        placeholder="#345beb or steelblue",
                    ),
                    ui.input_text(
                        "ast_colour", "Outline colour",
                        value=existing.get("colour", ""),
                        placeholder="black",
                    ),
                    ui.input_slider(
                        "ast_alpha", "Opacity (alpha)",
                        min=0.1, max=1.0, value=float(existing.get("alpha", 1.0)), step=0.05,
                    ),
                    ui.input_select(
                        "ast_shape", "Point shape",
                        choices={"": "Default", "16": "● Circle", "17": "▲ Triangle",
                                 "15": "■ Square", "18": "◆ Diamond", "1": "○ Hollow circle"},
                        selected=str(existing.get("shape", "")),
                    ),
                    ui.input_action_button(
                        "btn_aesthetic_apply", "Apply Style",
                        class_="btn-primary btn-sm w-100 mt-2",
                    ),
                    class_="p-2 spv-text-xs",
                ),
                value="plot_style",
            ),
            open=False,
            class_="mb-2",
        )

    @reactive.Effect
    @reactive.event(input.btn_aesthetic_apply)
    def _handle_aesthetic_apply():
        """Collect style inputs, apply alpha directly, open propagation dialog for others."""
        if home_state is None:
            return
        state = home_state.get()
        active_sub = state.get("active_plot_subtab", "")
        if not active_sub:
            return

        try:
            fill_color = (input.ast_fill_color() or "").strip()
            colour = (input.ast_colour() or "").strip()
            alpha = float(input.ast_alpha() if hasattr(input, "ast_alpha") else 1.0)
            shape_raw = (input.ast_shape() or "").strip()
            shape = int(shape_raw) if shape_raw.isdigit() else None
        except Exception:
            return

        # Alpha is always per-plot: apply directly to t3_plot_overrides.
        overrides_all = dict(state.get("t3_plot_overrides", {}))
        current = dict(overrides_all.get(active_sub, {}))
        if alpha < 1.0:
            current["alpha"] = round(alpha, 2)
        elif "alpha" in current:
            del current["alpha"]
        overrides_all[active_sub] = current
        home_state.set({**state, "t3_plot_overrides": overrides_all})

        # Non-alpha aesthetics: open propagation dialog if any are set.
        has_propagatable = bool(fill_color or colour or shape is not None)
        if not has_propagatable:
            return

        _aesthetic_scratch.set({
            "fill_color": fill_color or None,
            "colour": colour or None,
            "shape": shape,
            "active_sub": active_sub,
        })

        # Build the propagation modal (simplified — no column-presence check for aesthetics).
        summary_parts = []
        if fill_color:
            summary_parts.append(f"fill={fill_color}")
        if colour:
            summary_parts.append(f"colour={colour}")
        if shape is not None:
            summary_parts.append(f"shape={shape}")
        summary = ", ".join(summary_parts)

        # Collect all subtabs for the except-picker.
        try:
            all_subs = [f"subtab_{p}" for p in recipe_tiers.plot_entries(active_cfg().raw_config)]
        except Exception:
            all_subs = [active_sub]
        others = [s for s in all_subs if s != active_sub]

        m = ui.modal(
            ui.tags.small(f"Aesthetics: {summary}", class_="d-block text-muted mb-2"),
            ui.input_radio_buttons(
                "aesthetic_propagation_choice",
                label="Apply to:",
                choices={
                    "this": "This plot only",
                    "all": "All plots",
                    "except": "All plots except…",
                },
                selected="this",
            ),
            ui.input_selectize(
                "aesthetic_propagation_except",
                label=ui.tags.small("(only with 'All plots except…')", class_="text-muted"),
                choices={s: s.removeprefix("subtab_") for s in others},   # the plot id as written; no name is made from it (D-0409)
                selected=[],
                multiple=True,
                options={"placeholder": "Plots to exclude…", "plugins": ["remove_button"]},
            ),
            ui.input_action_button(
                "aesthetic_propagation_confirm", "Apply Style",
                class_="btn-primary w-100 mt-2",
            ),
            title="Plot Style — choose scope",
            easy_close=True,
            footer=ui.modal_button("Cancel"),
            size="m",
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.aesthetic_propagation_confirm)
    def _handle_aesthetic_propagation_confirm():
        """Commit aesthetic overrides to t3_plot_overrides for the chosen plots."""
        if home_state is None:
            return
        scratch = _aesthetic_scratch.get()
        if not scratch:
            ui.modal_remove()
            return

        state = home_state.get()
        active_sub = scratch.get("active_sub", state.get("active_plot_subtab", ""))
        try:
            choice = input.aesthetic_propagation_choice()
        except Exception:
            choice = "this"
        try:
            except_picks = list(input.aesthetic_propagation_except() or [])
        except Exception:
            except_picks = []

        try:
            all_subs = [f"subtab_{p}" for p in recipe_tiers.plot_entries(active_cfg().raw_config)]
        except Exception:
            all_subs = [active_sub]

        if choice == "this":
            targets = [active_sub]
        elif choice == "all":
            targets = list(all_subs)
        elif choice == "except":
            targets = [s for s in all_subs if s not in set(except_picks)]
        else:
            targets = [active_sub]

        overrides_all = dict(state.get("t3_plot_overrides", {}))
        for sub in targets:
            current = dict(overrides_all.get(sub, {}))
            if scratch.get("fill_color"):
                current["fill_color"] = scratch["fill_color"]
            if scratch.get("colour"):
                current["colour"] = scratch["colour"]
            if scratch.get("shape") is not None:
                current["shape"] = scratch["shape"]
            overrides_all[sub] = current

        home_state.set({**state, "t3_plot_overrides": overrides_all})
        _aesthetic_scratch.set({})
        ui.modal_remove()

        n_targets = len(targets)
        _notify(
            f"Style applied to {n_targets} plot(s).",
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


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _write_t3_ghost(state: dict, session_manager, notif_log: list | None = None) -> str | None:
    """Write the T3 ghost; returns a user-facing warning string on failure, None on success.

    Module-level helper (no closure over `_notify`) — the caller shows the warning.
    ADR-094/PIPELINE-ERROR-WIRE-2: previously printed the built PipelineError's fix text
    to the console only; a failed ghost save (T3 state lost on refresh) was invisible to
    the user it actually matters to.
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
            t3_audit_steps_by_plot=state.get("t3_audit_steps_by_plot", {}),
            t3_plot_overrides=state.get("t3_plot_overrides", {}),
            label=state.get("t3_ghost_label", ""),
            notification_log=notif_log or [],
        )
    except Exception as exc:
        pe = PipelineError(
            component="AuditStack",
            problem=f"T3 ghost save failed: {type(exc).__name__}: {exc}",
            location="_write_t3_ghost()",
            fix="Check that the session directory is writable and the deployment 'user_data' path is valid. T3 state was applied in-memory but will not survive a page refresh.",
            who="operator",
            category="t3_apply",
            surface="audit_panel",
            severity="warning",
            evidence={"session_key": session_key, "error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
        )
        print(pe.format())
        return f"⚠️ {pe.problem} {pe.fix}"
