"""app/handlers/audit_stack.py
Pipeline Audit Shiny wiring (ADR-044 / ADR-045, Phase 22-C).

Entry point:
    define_server(input, output, session, *,
                  wrangle_studio, recipe_pending, snapshot_recipe,
                  active_cfg, active_collection_id,
                  home_state=None, session_manager=None)

Concern: T2 violet node rendering, T3 Yellow RecipeNode rendering, btn_apply
         gatekeeper (blocks if any required reason field is empty), recipe
         change tracking, recipe_pending_badge_ui.

Two-Category Law (ADR-045): This file contains @render.* and @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (audit_stack), output:audit_nodes_header_ui, output:audit_nodes_tier2, output:audit_nodes_tier3, output:pipeline_issues_ui, output:aesthetic_style_panel_ui (22-J-10)
# consumes: app/modules/wrangle_studio.py, app/modules/session_manager.py, libs/transformer/src/transformer/data_wrangler.py
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-T3APPLY-1)
# consumed_by: app/src/server.py
# doc: .claude/rules/ui_implementation_contract.md#12a-12c, .claude/knowledge/architecture_decisions.md#ADR-044
# @end_deps

from shiny import reactive, render, ui

from transformer.data_wrangler import DataWrangler
from utils.pipeline_error import PipelineError
from app.modules.session_manager import (
    make_recipe_node,
    gatekeeper_blocked,
)

# Node type display config: (icon, label)
_NODE_META = {
    "filter_row":        ("🔍", "Row Filter"),
    "exclusion_row":     ("🚫", "Exclusion"),
    "drop_column":       ("✂️",  "Drop Column"),
    "aesthetic_override":("🎨", "Plot Style"),
    "developer_raw_yaml":("⚙️",  "Dev Fragment"),
}

_REASON_REQUIRED = {"filter_row", "exclusion_row", "drop_column", "developer_raw_yaml"}


def _safe_input_suffix(node_id: str) -> str:
    """Sanitize a RecipeNode id for use in a Shiny input ID.

    Shiny input IDs allow only [A-Za-z0-9_]. Legacy ghost files may contain
    UUID4 strings with hyphens, so we replace any invalid char with '_'.
    Current make_recipe_node() emits hex (no hyphens), so this is a no-op for
    new nodes.
    """
    return "".join(c if c.isalnum() or c == "_" else "_" for c in node_id)


_OP_SYMBOL = {"eq": "=", "ne": "≠", "gt": ">", "ge": "≥",
              "lt": "<", "le": "≤", "in": "∈", "not_in": "∉",
              "between": "↔"}


def _format_value(val) -> str:
    """Render a filter value compactly. Lists become {a, b, c}; long strings truncate."""
    if isinstance(val, (list, tuple)):
        items = [str(v) for v in val]
        if len(items) <= 3:
            return "{" + ", ".join(items) + "}"
        return "{" + ", ".join(items[:3]) + f", … +{len(items)-3}}}"
    s = str(val)
    return s if len(s) <= 30 else s[:30] + "…"


def _params_summary(node: dict) -> str:
    p = node.get("params", {})
    nt = node.get("node_type", "")
    if nt == "filter_row":
        col = p.get("column", "?")
        op_raw = p.get("op", "eq")
        op = _OP_SYMBOL.get(op_raw, op_raw)
        val = p.get("value", "")
        # 'between' renders with explicit inclusivity bracket: [lo, hi] when
        # closed='both' (inclusive), (lo, hi) when closed='none' (exclusive).
        if op_raw == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
            closed = p.get("closed", "both")
            lb, rb = ("[", "]") if closed == "both" else ("(", ")")
            return f"{col} ∈ {lb}{val[0]}, {val[1]}{rb}"
        return f"{col} {op} {_format_value(val)}"
    if nt == "exclusion_row":
        col = p.get("column", "?")
        return f"{col} = {_format_value(p.get('value', ''))}"
    if nt == "drop_column":
        return str(p.get("column", ""))
    if nt == "aesthetic_override":
        keys = [k for k in ("fill", "colour", "alpha", "shape") if k in p]
        return ", ".join(keys) if keys else "overrides"
    if nt == "developer_raw_yaml":
        frag = str(p.get("yaml_fragment", ""))
        return frag[:40] + "…" if len(frag) > 40 else frag
    return str(p)[:40]


def define_server(input, output, session, *,
                  wrangle_studio, recipe_pending, snapshot_recipe,
                  active_cfg, active_collection_id,
                  home_state=None, session_manager=None,
                  notification_log=None, bootloader=None,
                  session_pipeline_errors=None):
    """Register all Pipeline Audit reactive handlers."""
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)
    _ghost_save_enabled = (
        bootloader.get_automation_setting("ghost_save", "enabled")
        if bootloader is not None else True
    )

    # ------------------------------------------------------------------
    # btn_apply: commit T3 recipe, ghost save, release gatekeeper
    # ------------------------------------------------------------------

    @reactive.Effect
    @reactive.event(input.btn_apply)
    def handle_apply():
        """Commit pending T3 nodes — Phase 22-J / ADR-049 per-plot version.

        Pending nodes carry their target `plot_scope` (set by the propagation
        expansion in home_theater._handle_propagation_confirm). Commit means
        appending each node into t3_recipe_by_plot[node.plot_scope].

        Reasons are read from live `t3_reason_<id_suffix>` inputs; multiple
        propagated copies share the same suffix (because they share `id`),
        so a single reason text applies to all linked copies — which matches
        the "one decision, many places" model.
        """
        if home_state is None:
            snapshot_recipe.set(wrangle_studio.logic_stack.get())
            recipe_pending.set(False)
            return

        state = home_state.get()
        by_plot: dict[str, list[dict]] = {
            k: [dict(n) for n in v] for k, v in state.get("t3_recipe_by_plot", {}).items()
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
                pass

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
        blocked = gatekeeper_blocked(all_committed + pending)
        if blocked:
            blocked_types = list({n.get("node_type", "unknown") for n in blocked})
            pe = PipelineError(
                component="AuditStack",
                problem=f"{len(blocked)} T3 node(s) are missing required reason fields.",
                location="handle_apply()",
                fix="Fill in the 'Reason' text field for every highlighted node before pressing Apply.",
                who="analyst",
                category="t3_apply",
                surface="audit_panel",
                severity="warning",
                evidence={"blocked_count": len(blocked), "node_types": blocked_types},
            )
            print(pe.format())
            _notify(
                f"⛔ {len(blocked)} node(s) require a reason before applying.",
                type="error", duration=6,
            )
            # Persist reason edits even on block so user keeps their typing.
            home_state.set({
                **state,
                "t3_recipe_by_plot": by_plot,
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
            "t3_recipe_by_plot": by_plot,
            "_pending_t3_nodes": [],
            "t3_apply_count": int(state.get("t3_apply_count", 0)) + 1,
        }
        home_state.set(new_state)

        if session_manager is not None and _ghost_save_enabled:
            _write_t3_ghost(new_state, session_manager,
                            notif_log=notification_log.get() if notification_log is not None else [])

        snapshot_recipe.set(wrangle_studio.logic_stack.get())
        recipe_pending.set(False)

        total_nodes = sum(len(v) for v in by_plot.values())
        _notify(
            f"✅ T3 recipe applied — {total_nodes} node(s) across "
            f"{len([k for k, v in by_plot.items() if v])} plot stack(s).",
            type="message", duration=4,
        )

    # ------------------------------------------------------------------
    # Track recipe changes (pending badge)
    # ------------------------------------------------------------------

    @reactive.Effect
    def track_recipe_changes():
        _ = wrangle_studio.apply_logic
        recipe_pending.set(True)

    # ------------------------------------------------------------------
    # recipe_pending_badge_ui
    # ------------------------------------------------------------------

    @output
    @render.ui
    def recipe_pending_badge_ui():
        if recipe_pending.get():
            return ui.div("⏳ Pending", class_="recipe-pending-badge text-center")
        return ui.div()

    def _active_target_ds() -> str:
        """Return the target_dataset for the currently active plot.

        Falls back to active_collection_id() (first manifest collection) when
        home_state is absent or the active plot has no target_dataset — so the
        audit panel always shows something rather than going blank.
        """
        if home_state is not None:
            state = home_state.get()
            subtab = state.get("active_plot_subtab") or ""
            p_id = subtab.removeprefix("subtab_") if subtab else None
            if p_id:
                cfg = active_cfg()
                for gspec in cfg.raw_config.get("analysis_groups", {}).values():
                    plot_entry = gspec.get("plots", {}).get(p_id)
                    if plot_entry is not None:
                        ds = (plot_entry.get("spec") or {}).get("target_dataset")
                        if ds:
                            return ds
                top_plot = cfg.raw_config.get("plots", {}).get(p_id)
                if top_plot:
                    ds = top_plot.get("target_dataset")
                    if ds:
                        return ds
        return active_collection_id()

    # ------------------------------------------------------------------
    # audit_nodes_header_ui — Project + Collection context line
    # ------------------------------------------------------------------

    @output
    @render.ui
    def audit_nodes_header_ui():
        cfg = active_cfg()
        collection_id = _active_target_ds()
        return ui.div(
            ui.div(f"Project: {cfg.raw_config.get('id')}", class_="audit-node-tier2"),
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
        collections = cfg.raw_config.get("join_manifests", {})
        recipe = []
        if collection_id in collections:
            raw_recipe = collections[collection_id].get("recipe", [])
            recipe = DataWrangler._resolve_tier(raw_recipe, "tier1")

        if not recipe:
            return ui.div(ui.div("No Tier 2 steps defined.", class_="audit-node-tier2"))

        nodes = []
        for step in recipe:
            action = step.get("action", "unknown")
            label = step.get("label") or step.get("right_ingredient") or action
            nodes.append(ui.tooltip(
                ui.div(f"[Tier 2] {action}: {label}", class_="audit-node-tier2"),
                f"Action: {action}", placement="left"
            ))
        return ui.div(*nodes)

    # ------------------------------------------------------------------
    # audit_nodes_tier3 — Yellow RecipeNodes (T3 committed + pending)
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

        state = home_state.get()
        # Phase 22-J: per-plot view. Show only the active plot's committed
        # stack plus pending nodes targeting this plot (or any plot — pending
        # nodes carry plot_scope set during propagation expansion).
        active_subtab = state.get("active_plot_subtab") or ""
        by_plot = state.get("t3_recipe_by_plot", {}) or {}
        committed_here = list(by_plot.get(active_subtab, []))
        pending_all = list(state.get("_pending_t3_nodes", []))
        pending_here = [n for n in pending_all
                        if n.get("plot_scope") == active_subtab]

        # For "Applied to N plots" badge: count unique plot_scopes per id.
        scope_count_by_id: dict[str, int] = {}
        for plot_id, nodes in by_plot.items():
            for n in nodes:
                nid = n.get("id", "")
                if nid:
                    scope_count_by_id[nid] = scope_count_by_id.get(nid, 0) + 1
        for n in pending_all:
            nid = n.get("id", "")
            if nid:
                scope_count_by_id[nid] = scope_count_by_id.get(nid, 0) + 1

        all_nodes = committed_here + pending_here

        # Orphan/legacy nodes for this session
        orphaned = list(by_plot.get("__legacy__", []))

        if not all_nodes and not orphaned:
            return ui.div(
                ui.div(
                    f"No T3 adjustments for {active_subtab.removeprefix('subtab_') or 'this plot'} yet.",
                    class_="text-muted spv-text-sm",
                    style="padding:4px;",
                ),
            )

        blocked_ids = set(gatekeeper_blocked(pending_all + [n for nodes in by_plot.values() for n in nodes]))
        adj_header = ui.div(
            ui.h6(f"My Adjustments (Tier 3) — {active_subtab.removeprefix('subtab_') or 'plot'}",
                  class_="m-0 spv-flex-1"),
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
            reason = node.get("reason", "")
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

        return ui.div(adj_header, *node_els)

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

        Phase 22-J: reads from t3_recipe_by_plot (flattened) plus _pending_t3_nodes.
        Linked-id reason fan-out: a single typed reason on any copy is mirrored
        into every copy sharing the same id, so the gatekeeper sees the user's
        intent across all linked copies even if they only typed in one box.
        """
        if home_state is None:
            return []
        state = home_state.get()
        by_plot = state.get("t3_recipe_by_plot", {}) or {}
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
    # Delete-node handlers — permanent removal from t3_recipe / _pending_t3_nodes
    # ------------------------------------------------------------------
    # We track click counts per-node-id between effect firings; nodes whose
    # click count increased since last seen are removed entirely. This is
    # idempotent — re-clicking a deleted node's ID does nothing because the
    # ID is no longer in state.

    _last_delete_clicks: dict[str, int] = {}

    @reactive.Effect
    def _handle_delete():
        """Linked-id permanent deletion across all per-plot stacks.

        Phase 22-J / ADR-049 §12g.10: clicking 🗑 on any copy removes EVERY
        copy sharing that id from every plot's stack and from pending nodes.
        """
        if home_state is None:
            return
        state = home_state.get()
        by_plot: dict[str, list[dict]] = {
            k: list(v) for k, v in state.get("t3_recipe_by_plot", {}).items()
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
            "t3_recipe_by_plot": new_by_plot,
            "_pending_t3_nodes": new_pending,
        })
        # Count how many physical copies were removed (for the notification)
        removed_count = sum(
            len(nodes) - len(new_by_plot[k])
            for k, nodes in by_plot.items()
        ) + (len(pending) - len(new_pending))
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
            all_specs = state.get("t3_recipe_by_plot", {})
            all_subs = list(all_specs.keys())
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
                choices={s: s.removeprefix("subtab_").replace("_", " ").title() for s in others},
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
            all_specs = state.get("t3_recipe_by_plot", {})
            all_subs = list(all_specs.keys())
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
    # pipeline_issues_ui — DIAG-RUNTIME-AUDIT-1 structured error log
    # ------------------------------------------------------------------

    @output
    @render.ui
    def pipeline_issues_ui():
        if session_pipeline_errors is None:
            return ui.div()
        entries = session_pipeline_errors.get()
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
            items.append(
                ui.div(
                    ui.div(
                        ui.span(f"[{comp}]", class_="spv-text-xs text-danger fw-bold"),
                        ui.span(ts, class_="spv-text-xs text-muted ms-1"),
                        class_="d-flex justify-content-between",
                    ),
                    ui.div(prob[:120], class_="spv-text-xs"),
                    class_="spv-audit-issue-entry mb-1 p-1",
                    style="background:#fff0f0;border-radius:3px;border-left:3px solid #d62828;",
                )
            )

        return ui.div(
            ui.div(
                ui.tags.strong(f"Runtime issues ({len(errors)})", class_="spv-text-xs text-danger"),
                class_="mb-1",
            ),
            *items,
            class_="p-2",
            id="pipeline_issues_panel",
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _write_t3_ghost(state: dict, session_manager, notif_log: list | None = None) -> None:
    msig = state.get("manifest_sha256") or ""
    dbh = state.get("data_batch_hash") or ""
    if not msig or not dbh:
        return
    from app.modules.session_manager import SessionManager
    session_key = SessionManager.compute_session_key(msig, dbh)
    try:
        session_manager.write_t3_ghost(
            session_key=session_key,
            manifest_id=state.get("manifest_id", ""),
            manifest_sha256=msig,
            data_batch_hash=dbh,
            tier_toggle=state.get("tier_toggle", "T2"),
            t3_recipe_by_plot=state.get("t3_recipe_by_plot", {}),
            t3_plot_overrides=state.get("t3_plot_overrides", {}),
            label=state.get("t3_ghost_label", ""),
            notification_log=notif_log or [],
        )
    except Exception as exc:
        pe = PipelineError(
            component="AuditStack",
            problem=f"T3 ghost save failed: {type(exc).__name__}: {exc}",
            location="_write_t3_ghost()",
            fix="Check that the session directory is writable and the deployment profile 'user_sessions' path is valid. T3 state was applied in-memory but will not survive a page refresh.",
            who="operator",
            category="t3_apply",
            surface="audit_panel",
            severity="warning",
            evidence={"session_key": session_key, "error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
        )
        print(pe.format())
