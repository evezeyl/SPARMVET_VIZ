"""app/handlers/filter_and_audit_handlers.py
Filter recipe builder UI + T3 audit promotion + propagation modal.

Extracted from home_theater.py in Phase 24-D (ADR-051).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.

Why filter UI and T3 audit live in one file:
    _filter_apply, _col_drop_to_audit, and _handle_propagation_confirm all
    share the _propagation_scratch reactive.Value and call into the same
    _open_propagation_modal helper. Splitting would force exposing the
    scratch state across module boundaries.
"""

from __future__ import annotations

# @deps
# provides: function:define_filter_audit_server, output:sidebar_filters, output:filter_rows_ui, output:filter_form_ui, output:filter_controls_ui
# consumes: app/modules/session_manager.py (make_recipe_node), app/modules/t3_recipe_engine.py (_op_label), shiny
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-049, .claude/knowledge/architecture_decisions.md#ADR-051
# @end_deps

from shiny import reactive, render, ui

from app.src.bootloader import bootloader
from app.modules.t3_recipe_engine import _op_label


def define_filter_audit_server(input, output, session, *,
                                applied_filters, _pending_filters,
                                _propagation_scratch, home_state,
                                tier_toggle, active_home_subtab,
                                safe_input,
                                _resolve_active_spec, _resolve_active_lf,
                                _spec_discrete_axes, _t3_drop_columns,
                                _all_plot_subtab_ids, _plot_label,
                                notification_log=None):
    """Register filter UI + T3 audit propagation handlers.

    Reactive deps (kwargs) — all shared with home_theater.define_server:
      applied_filters       reactive.Value[list]   — committed transient filters (T1/T2 plot view)
      _pending_filters      reactive.Value[list]   — staging rows in the add-row form
      _propagation_scratch  reactive.Value[dict]   — scratch nodes between Apply/Drop and modal confirm
      home_state            reactive.Value[dict] | None — t3 recipe state, active subtab, etc.
      tier_toggle           reactive.Value[str]    — "T1"|"T2"|"T3"
      active_home_subtab    reactive.Value[str]    — current home plot subtab id
    Helpers (kwargs):
      safe_input(input, key, default) → value
    Closures from home_theater.define_server (kwargs):
      _resolve_active_spec(p_id) → spec dict | None
      _resolve_active_lf(spec)   → LazyFrame
      _spec_discrete_axes(spec)  → (set, set)  — discrete x, discrete y columns
      _t3_drop_columns()         → list[str]   — committed drop-column targets
      _all_plot_subtab_ids()     → list[str]   — every "subtab_<plot_id>" id
      _plot_label(subtab_id)     → str         — human-readable plot label
    """
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    @output
    @render.ui
    def sidebar_filters():
        """
        Phase 21-F-1: Static shell — rendered once, never re-renders.
        Mounts stable output slots; child outputs re-render independently.
        Apply label and status are in filter_rows_ui to avoid shell re-renders.
        """
        # pipeline-static: no interactivity — static message, no filter UI
        if not bootloader.is_enabled("interactivity_enabled"):
            return ui.div(
                ui.tags.small(
                    "Filters are set by the pipeline configuration.",
                    class_="text-muted d-block px-1 spv-text-sm"
                )
            )
        # pipeline-exploration-simple: interactivity on but no T3 audit — show disclaimer
        # Proxy: metadata_ingestion_enabled=false identifies simple/passive-only personas
        disclaimer = None
        if not bootloader.is_enabled("metadata_ingestion_enabled"):
            disclaimer = ui.div(
                ui.tags.small(
                    "Exploration only — filters are not saved and do not modify data permanently.",
                    class_="text-warning d-block px-1 mb-1 border-start border-warning ps-2 spv-text-xs"
                )
            )
        # Left "Apply" is the single entry point: in T1/T2 it commits transient
        # filters; in T3 it pushes pending RecipeNodes into home_state for the
        # right-sidebar audit panel. No separate "Apply to recipe" button.
        return ui.div(
            disclaimer or ui.div(),
            ui.output_ui("filter_rows_ui"),
            ui.output_ui("filter_form_ui"),
            ui.div(
                ui.output_ui("filter_controls_ui"),
                class_="mt-2 px-1"
            ),
            class_="spv-text-sm"
        )

    @output
    @render.ui
    def filter_rows_ui():
        """Pending filter rows. Reads _pending_filters only — re-renders on Add/Remove."""
        pending = _pending_filters.get()
        if not pending:
            return ui.tags.small(
                "No filters yet. Add rows below.", class_="text-muted d-block px-1 mb-1 spv-text-xs",
            )
        rows = []
        for i, f in enumerate(pending):
            col = f.get("column", "")
            op = f.get("op", "eq")
            val = f.get("value", "")
            dtype_str = f.get("dtype", "")
            val_display = ", ".join(str(v) for v in val) if isinstance(val, list) else str(val)
            rows.append(ui.div(
                ui.div(
                    ui.tags.small(
                        f"{col} {_op_label(op)} {val_display}",
                        class_="text-dark spv-text-xs",
                    ),
                    ui.tags.small(f" [{dtype_str}]", class_="text-muted spv-text-micro"),
                    class_="flex-grow-1"
                ),
                *([] if not bootloader.is_enabled("interactivity_enabled") else [
                    ui.input_action_button(
                        f"filter_remove_{i}", "🗑",
                        class_="btn btn-sm btn-link p-0 text-danger",
                    )
                ]),
                class_="d-flex align-items-center gap-2 mb-1 px-1 py-1 border rounded bg-light",
            ))
        return ui.div(*rows)

    @output
    @render.ui
    def filter_form_ui():
        """
        Add-row form. Reads dataset columns + fb_col/fb_op input state.
        Does NOT read _pending_filters — so appending a row doesn't reset the form.
        Value type coercion happens at apply time in _apply_filter_rows;
        values are always stored as strings here and cast to column dtype when filtering.
        """
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        disc_x, disc_y = _spec_discrete_axes(spec)
        discrete_cols = disc_x | disc_y

        try:
            lf = _resolve_active_lf(spec)
            sample = lf.head(500).collect()
            all_cols = sample.columns
            dtypes = {c: str(sample[c].dtype) for c in all_cols}
        except Exception:
            all_cols = []
            dtypes = {}
            sample = None

        col_choices = {c: f"{c}  [{dtypes.get(c, '')}]" for c in all_cols} if all_cols else {}
        sel_col = safe_input(input, "fb_col", all_cols[0] if all_cols else None)
        sel_dtype = dtypes.get(sel_col, "Utf8") if sel_col else "Utf8"
        is_discrete = (sel_col in discrete_cols) or (
            "Int" not in sel_dtype and "Float" not in sel_dtype and "UInt" not in sel_dtype
        )

        # Op choices depend on whether the column is discrete or continuous.
        # Continuous columns get a `between` range operator (UX-FILTER-1).
        # eq is the first option for both — most intuitive default.
        if is_discrete:
            op_choices = {"in": "∈ any of", "not_in": "∉ none of", "eq": "= exact", "ne": "≠"}
        else:
            op_choices = {
                "eq": "=", "ne": "≠",
                "gt": ">", "ge": "≥",
                "lt": "<", "le": "≤",
                "between": "↔ between",
            }

        sel_op = safe_input(input, "fb_op", next(iter(op_choices.keys())))
        # If the user previously picked an op that's now unavailable (e.g.
        # column changed dtype between renders), fall back to the first valid.
        if sel_op not in op_choices:
            sel_op = next(iter(op_choices.keys()))

        # --- Value widget: dtype + op aware (UX-FILTER-1) -------------------
        # Discrete column: multi-select selectize regardless of op.
        # Numeric + 'between': two-handle range slider over the data's min/max.
        # Numeric + scalar op: numeric input (emits float/int natively).
        if is_discrete and sample is not None and sel_col and sel_col in sample.columns:
            unique_vals = sorted([str(v) for v in sample[sel_col].drop_nulls().unique().to_list()])
            value_widget = ui.input_selectize(
                "fb_value", label=None,
                choices=unique_vals, selected=[],
                multiple=True,
                options={"placeholder": "Select value(s)…", "plugins": ["remove_button"], "dropdownParent": "body"},
            )
        elif not is_discrete and sample is not None and sel_col and sel_col in sample.columns:
            # Compute min/max from the sample for slider bounds and numeric placeholder.
            is_int_col = "Int" in sel_dtype or "UInt" in sel_dtype
            try:
                col_series = sample[sel_col].drop_nulls()
                if is_int_col:
                    col_min = int(col_series.min()) if col_series.len() else 0
                    col_max = int(col_series.max()) if col_series.len() else 1
                else:
                    col_min = float(col_series.min()) if col_series.len() else 0.0
                    col_max = float(col_series.max()) if col_series.len() else 1.0
            except Exception:
                col_min, col_max = (0, 1) if is_int_col else (0.0, 1.0)
            # Guard degenerate range (all values equal): widen by 1 so the slider works.
            if col_min == col_max:
                col_max = col_min + 1
            step = 1 if is_int_col else (col_max - col_min) / 100 or 0.01

            if sel_op == "between":
                # Two numeric inputs (min, max) + an inclusivity toggle.
                # Default: closed-both (min ≤ X ≤ max). User can flip to
                # closed-none (min < X < max) for strict bounds.
                sel_closed = safe_input(input, "fb_closed", "both")
                inclusivity_label = (
                    "min ≤ value ≤ max (inclusive)" if sel_closed == "both"
                    else "min < value < max (exclusive)"
                )
                value_widget = ui.div(
                    ui.div(
                        ui.div(
                            ui.tags.small("min", class_="text-muted"),
                            ui.input_numeric(
                                "fb_value_lo", label=None,
                                value=col_min, step=step,
                            ),
                            class_="spv-flex-1",
                        ),
                        ui.div(
                            ui.tags.small("max", class_="text-muted"),
                            ui.input_numeric(
                                "fb_value_hi", label=None,
                                value=col_max, step=step,
                            ),
                            class_="spv-flex-1",
                        ),
                        class_="d-flex gap-1",
                    ),
                    ui.input_radio_buttons(
                        "fb_closed", label=None,
                        choices={"both": "≤ inclusive",
                                 "none": "< exclusive"},
                        selected=sel_closed,
                        inline=True,
                    ),
                    ui.tags.small(inclusivity_label,
                                  class_="text-muted fst-italic d-block spv-text-meta"),
                )
            else:
                value_widget = ui.input_numeric(
                    "fb_value", label=None,
                    value=col_min, min=col_min, max=col_max, step=step,
                )
        else:
            value_widget = ui.input_text("fb_value", label=None, placeholder="Value…")

        return ui.div(
            ui.tags.small("Add filter row:", class_="fw-semibold text-muted d-block mb-1"),
            # selected=sel_col preserves the user's column choice across re-renders
            ui.input_select("fb_col", label=None, choices=col_choices, selected=sel_col),
            ui.div(
                ui.input_select("fb_op", label=None, choices=op_choices,
                                selected=sel_op, width="100px"),
                ui.div(value_widget, class_="spv-flex-1"),
                class_="d-flex gap-1 align-items-center"
            ),
            class_="mt-2 pt-2 border-top spv-text-sm",
        )

    @output
    @render.ui
    def filter_controls_ui():
        """Apply/Reset buttons + status. Reads _pending_filters + applied_filters.

        In T3 mode the Apply button label changes to indicate that pressing it
        promotes staged rows into the audit pipeline (right sidebar) rather
        than committing a transient view filter.
        """
        n_applied = len(applied_filters.get())
        n_pending = len(_pending_filters.get())
        in_t3 = tier_toggle.get() == "T3"
        apply_label = (f"➜ Send to Audit ({n_pending})" if in_t3
                       else f"Apply ({n_pending})")
        apply_class = ("btn-warning btn-sm flex-grow-1" if in_t3
                       else "btn-primary btn-sm flex-grow-1")
        status = (
            ui.tags.small(f"{n_applied} active", class_="text-success d-block mb-1 spv-text-xxs")
            if n_applied else ui.div()
        )
        return ui.div(
            status,
            ui.div(
                ui.input_action_button(
                    "filter_apply", apply_label,
                    class_=apply_class + " spv-text-xs",
                ),
                ui.input_action_button(
                    "filter_add_row", "+ Add",
                    class_="btn-outline-primary btn-sm spv-text-xs",
                ),
                ui.input_action_button(
                    "filter_reset", "Reset",
                    class_="btn-outline-secondary btn-sm spv-text-xs",
                ),
                class_="d-flex gap-1 mt-1"
            ),
        )

    # ── Filter recipe builder effects ─────────────────────────────────────────

    @reactive.Effect
    @reactive.event(input.filter_add_row)
    def _filter_add_row():
        """Append a new filter row to _pending_filters from the add-row form."""
        col = safe_input(input, "fb_col", None)
        op = safe_input(input, "fb_op", "eq")
        # 'between' uses two separate numeric inputs (fb_value_lo / fb_value_hi)
        # plus an inclusivity radio (fb_closed). Read all three and synthesise
        # a tuple; auto-swap if the user enters lo > hi.
        bt_closed = "both"  # default
        if op == "between":
            lo = safe_input(input, "fb_value_lo", None)
            hi = safe_input(input, "fb_value_hi", None)
            if lo is None or hi is None:
                return
            if lo > hi:
                lo, hi = hi, lo
            bt_closed = safe_input(input, "fb_closed", "both")
            if bt_closed not in ("both", "none"):
                bt_closed = "both"
            raw_val = (lo, hi)
        else:
            raw_val = safe_input(input, "fb_value", "")
        if not col:
            return
        # Determine dtype from current sample
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        try:
            lf = _resolve_active_lf(spec)
            sample = lf.head(10).collect()
            dtype_str = str(sample[col].dtype) if col in sample.columns else "Utf8"
        except Exception:
            dtype_str = "Utf8"

        # raw_val type depends on the widget that produced it (UX-FILTER-1):
        #   - between op       → tuple (lo, hi) of nums → between filter
        #   - selectize multi  → list/tuple of strings  → set-membership filter
        #   - input_numeric    → int/float              → scalar comparison
        #   - input_text       → string                 → scalar comparison
        if op == "between" and isinstance(raw_val, (list, tuple)) and len(raw_val) == 2:
            # Two-numeric-input pair: native (lo, hi) tuple
            lo, hi = raw_val
            value = [lo, hi]
        elif isinstance(raw_val, (list, tuple)):
            # Selectize multi-pick: set membership
            value = list(raw_val)
            if not value:
                return  # nothing selected — don't add an empty filter
            if op == "eq":
                op = "in"
            elif op == "ne":
                op = "not_in"
        elif isinstance(raw_val, (int, float)):
            # Numeric input: native scalar
            value = raw_val
        elif isinstance(raw_val, str) and raw_val.strip():
            # Text input fallback: keep as string (downstream coercion if needed)
            value = raw_val.strip()
        else:
            return  # empty/None — don't add

        new_row = {"column": col, "op": op, "value": value, "dtype": dtype_str}
        if op == "between":
            new_row["closed"] = bt_closed  # 'both' (default) or 'none'
        current = list(_pending_filters.get())
        current.append(new_row)
        _pending_filters.set(current)

    @reactive.Effect
    @reactive.event(input.filter_apply)
    def _filter_apply():
        """Left-panel Apply.

        T1/T2: commit _pending_filters → applied_filters (transient view).
        T3 (Phase 22-J / ADR-049): build pending T3 nodes from staged rows.
          - Filter on a primary-key column → silent convert to exclusion_row
            and stamp primary_key_warning=true (§12g.3).
          - Open the propagation dialog so the user picks
            this-plot / all-plots / all-except.
        """
        rows = list(_pending_filters.get())

        if tier_toggle.get() != "T3" or home_state is None:
            applied_filters.set(rows)
            return

        if not rows:
            _notify(
                "No filter rows to send. Add rows below first (the '+ Add' button).",
                type="warning", duration=5,
            )
            return

        from app.modules.session_manager import make_recipe_node
        state = home_state.get()
        primary_keys = set(state.get("primary_keys") or [])
        active_subtab = state.get("active_plot_subtab") or active_home_subtab.get() or ""

        scratch_nodes: list[dict] = []
        for frow in rows:
            col = frow.get("column", "")
            op = frow.get("op", "eq")
            val = frow.get("value", "")
            params = {"column": col, "op": op, "value": val}
            if frow.get("dtype"):
                params["dtype"] = frow.get("dtype")

            is_pk = col in primary_keys
            # AUDIT-1 (ADR-049 amendment, 2026-04-30): filtering on a PK
            # column is now ALLOWED. Previously this silently converted to
            # exclusion_row with a negated op — that broke the user mental
            # model ("filter sample==X" should keep X, not exclude it).
            # Keep the row as filter_row; primary_key_warning=True still
            # raises the warning banner in the modal and audit panel.
            # Drop-column on a PK remains BLOCKED (handled at the drop
            # action site, not here).
            node_type = "filter_row"

            scratch_nodes.append(make_recipe_node(
                node_type, params,
                plot_scope=active_subtab,
                reason="",
                primary_key_warning=is_pk,
            ))

        # Stash for the propagation dialog handler to consume.
        _propagation_scratch.set({"nodes": scratch_nodes, "kind": "filter"})
        _open_propagation_modal(scratch_nodes, active_subtab, kind="filter")

        # Clear staged rows — they're moving into the audit pipeline.
        _pending_filters.set([])
        applied_filters.set([])

    @reactive.Effect
    @reactive.event(input.filter_reset)
    def _filter_reset():
        """Clear all pending and applied filters, and reset the value widget."""
        _pending_filters.set([])
        applied_filters.set([])
        ui.update_selectize("fb_value", selected=[])
        ui.update_text("fb_value", value="")

    @reactive.Effect
    @reactive.event(input.col_drop_to_audit)
    def _col_drop_to_audit():
        """Promote deselected columns into the T3 audit pipeline.

        Phase 22-J / ADR-049:
          - Drop on a primary-key column → BLOCKED with a notification listing
            the offending columns (§12g.3 / §12g.4).
          - Otherwise → build pending drop_column nodes and open the
            propagation dialog.
        """
        if home_state is None or tier_toggle.get() != "T3":
            return

        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        try:
            lf = _resolve_active_lf(spec)
        except Exception:
            return

        state = home_state.get()
        primary_keys = set(state.get("primary_keys") or [])
        committed = set(_t3_drop_columns())
        choosable = [c for c in lf.collect_schema().names() if c not in committed]
        visible = safe_input(input, "preview_col_selector", choosable)
        vis_set = set(visible) if isinstance(visible, (list, tuple)) else set(choosable)
        to_drop = [c for c in choosable if c not in vis_set]

        if not to_drop:
            _notify(
                "No deselected columns to drop. Uncheck columns above first.",
                type="warning", duration=4,
            )
            return

        # Block primary-key drops absolutely (§12g.4).
        pk_targets = [c for c in to_drop if c in primary_keys]
        if pk_targets:
            _notify(
                f"⛔ Cannot drop join key column(s): {', '.join(pk_targets)}. "
                "Use a row filter or row exclusion instead.",
                type="error", duration=8,
            )
            return

        from app.modules.session_manager import make_recipe_node
        active_subtab = state.get("active_plot_subtab") or active_home_subtab.get() or ""
        scratch_nodes = [
            make_recipe_node(
                "drop_column", {"column": col},
                plot_scope=active_subtab,
                reason="",
            )
            for col in to_drop
        ]
        _propagation_scratch.set({"nodes": scratch_nodes, "kind": "drop"})
        _open_propagation_modal(scratch_nodes, active_subtab, kind="drop")

        # Reset selectize to the kept columns so the user starts clean.
        remaining = [c for c in choosable if c in vis_set]
        ui.update_selectize("preview_col_selector",
                            choices=remaining, selected=remaining)

    # ── 22-J: Propagation modal (this/all/all-except) ─────────────────────────

    def _column_presence_per_plot(scratch_nodes: list[dict],
                                   plot_subtabs: list[str]) -> dict[str, str]:
        """For each subtab, report whether the scratch nodes' target columns
        are PRESENT in that plot's underlying dataset (PROP-1).

        Returns a dict mapping subtab_id → 'present' | 'absent' | 'unknown'.
        Plots whose target_dataset can't be resolved get 'unknown' (treated
        as a soft warning).
        Schema scans are memoised per target_dataset since many plots share
        the same assembly.
        """
        cols_needed = {
            n.get("params", {}).get("column", "")
            for n in scratch_nodes
        }
        cols_needed.discard("")
        if not cols_needed:
            return {sub: "present" for sub in plot_subtabs}

        result: dict[str, str] = {}
        schema_cache: dict[str, set[str]] = {}

        for sub in plot_subtabs:
            p_id = sub.removeprefix("subtab_")
            spec = _resolve_active_spec(p_id)
            if spec is None:
                result[sub] = "unknown"
                continue
            target_ds = spec.get("target_dataset") or "__tier1_anchor__"
            if target_ds not in schema_cache:
                try:
                    lf = _resolve_active_lf(spec)
                    schema_cache[target_ds] = set(lf.collect_schema().names())
                except Exception:
                    schema_cache[target_ds] = set()
            ds_cols = schema_cache[target_ds]
            if not ds_cols:
                result[sub] = "unknown"
            elif cols_needed.issubset(ds_cols):
                result[sub] = "present"
            else:
                result[sub] = "absent"
        return result

    def _open_propagation_modal(scratch_nodes: list[dict],
                                active_subtab: str,
                                kind: str) -> None:
        """Open a modal asking the user to choose propagation scope.

        Choices:
        - This plot only (default)
        - All plots
        - All plots except… (reveals a multiselect)

        On confirm, `_handle_propagation_confirm` reads the radio + multiselect
        and resolves the scratch nodes into one RecipeNode per target plot
        (sharing `id`), then appends them to home_state._pending_t3_nodes.
        """
        all_subtabs = _all_plot_subtab_ids()
        others = [s for s in all_subtabs if s != active_subtab]
        n = len(scratch_nodes)
        first = scratch_nodes[0] if scratch_nodes else {}
        any_pk = any(node.get("primary_key_warning") for node in scratch_nodes)

        # Plain-language summary of what we're about to add
        if kind == "drop":
            header = f"Drop {n} column(s) — choose scope"
            cols = ", ".join(node.get("params", {}).get("column", "?")
                             for node in scratch_nodes)
            summary = f"Columns: {cols}"
        else:
            header = f"Add {n} filter/exclusion(s) — choose scope"
            col = first.get("params", {}).get("column", "?")
            summary = f"Targets column: {col}"

        warn = ui.span()
        if any_pk:
            warn = ui.div(
                "⚠️ One or more nodes target a join key. "
                "Removing rows here changes which samples appear in joined plots.",
                class_="alert alert-warning py-1 px-2 mb-2 spv-text-sm",
            )

        # PROP-1: per-target column presence — surface BEFORE the user confirms.
        presence = _column_presence_per_plot(scratch_nodes, all_subtabs)
        n_present = sum(1 for v in presence.values() if v == "present")
        n_absent = sum(1 for v in presence.values() if v == "absent")
        n_unknown = sum(1 for v in presence.values() if v == "unknown")

        absent_items = [
            ui.tags.li(f"⚠️ {_plot_label(sub)} — column not in plot data; will be SKIPPED")
            for sub, st in presence.items() if st == "absent"
        ]
        unknown_items = [
            ui.tags.li(f"❓ {_plot_label(sub)} — could not resolve dataset; verify manually")
            for sub, st in presence.items() if st == "unknown"
        ]
        propagation_preview = ui.div(
            ui.tags.small(
                f"📍 Propagation preview: ✅ {n_present} apply  •  "
                f"⚠️ {n_absent} skip (col missing)" +
                (f"  •  ❓ {n_unknown} unknown" if n_unknown else ""),
                class_="d-block fw-semibold mb-1",
            ),
            ui.tags.details(
                ui.tags.summary(
                    "Show details",
                    class_="text-muted spv-text-xs",
                    style="cursor:pointer;",
                ),
                ui.tags.ul(
                    *absent_items,
                    *unknown_items,
                    class_="mb-0 ps-3 spv-text-xs",
                ) if (absent_items or unknown_items)
                else ui.tags.div("All plots have this column.",
                                 class_="text-muted ps-3 spv-text-xs"),
            ),
            ui.tags.small(
                "👉 Apply filters one at a time and verify each plot before stacking. "
                "A skipped plot is NOT filtered — it shows the unfiltered data.",
                class_="text-muted d-block mt-1 fst-italic spv-text-meta",
            ),
            class_="alert alert-info py-1 px-2 mb-2 spv-text-sm",
        )

        m = ui.modal(
            warn,
            propagation_preview,
            ui.tags.small(summary, class_="text-muted d-block mb-2"),
            ui.input_radio_buttons(
                "propagation_choice",
                label="Apply to:",
                choices={
                    "this": "This plot only",
                    "all": "All plots",
                    "except": "All plots except…",
                },
                selected="this",
                inline=False,
            ),
            ui.div(
                ui.input_selectize(
                    "propagation_except",
                    label=ui.tags.small(
                        "Select plots to exclude — the rest will receive the filter.",
                        class_="text-muted",
                    ),
                    choices={s: _plot_label(s) for s in others} or {},
                    selected=[],
                    multiple=True,
                    options={"placeholder": "Pick plots to skip…",
                             "plugins": ["remove_button"]},
                ),
                id="propagation_except_wrapper",
                style="display:none;",
            ),
            ui.tags.script(
                """
                (function () {
                    function syncExcept() {
                        var checked = document.querySelector(
                            'input[name="propagation_choice"]:checked'
                        );
                        var wrapper = document.getElementById(
                            'propagation_except_wrapper'
                        );
                        if (wrapper) {
                            wrapper.style.display =
                                (checked && checked.value === 'except') ? '' : 'none';
                        }
                    }
                    document.addEventListener('change', function (e) {
                        if (e.target && e.target.name === 'propagation_choice') {
                            syncExcept();
                        }
                    });
                    syncExcept();
                })();
                """
            ),
            ui.input_action_button(
                "propagation_confirm", "Add to audit pipeline",
                class_="btn-warning w-100 mt-2",
            ),
            title=header,
            easy_close=True,
            footer=ui.modal_button("Cancel"),
            size="m",
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.propagation_confirm)
    def _handle_propagation_confirm():
        """Resolve the user's propagation choice and commit pending nodes."""
        if home_state is None:
            return
        scratch = _propagation_scratch.get() or {}
        scratch_nodes: list[dict] = list(scratch.get("nodes", []))
        if not scratch_nodes:
            ui.modal_remove()
            return

        choice = safe_input(input, "propagation_choice", "this")
        except_picks = safe_input(input, "propagation_except", []) or []
        if isinstance(except_picks, (list, tuple)):
            except_picks = list(except_picks)
        else:
            except_picks = [except_picks]

        all_subtabs = _all_plot_subtab_ids()
        state = home_state.get()
        active_subtab = state.get("active_plot_subtab") or active_home_subtab.get() or ""

        if choice == "this":
            target_plots = [active_subtab] if active_subtab else []
        elif choice == "all":
            target_plots = list(all_subtabs)
        elif choice == "except":
            target_plots = [s for s in all_subtabs if s not in set(except_picks)]
        else:
            target_plots = [active_subtab] if active_subtab else []

        if not target_plots:
            _notify(
                "No target plots selected. Audit pipeline unchanged.",
                type="warning", duration=4,
            )
            ui.modal_remove()
            return

        # §12g.7 — expand each scratch node into one copy per target plot,
        # sharing id (linked deletion). Skip plots whose schema lacks the
        # targeted column (§12g.9 / D9): collect skipped for a notification.
        from app.modules.session_manager import make_recipe_node
        pending_nodes = list(state.get("_pending_t3_nodes", []))
        skipped: dict[str, list[str]] = {}  # plot → [columns skipped]
        applied_count = 0

        for scratch_node in scratch_nodes:
            shared_id = scratch_node.get("id")
            params = dict(scratch_node.get("params", {}))
            col = params.get("column", "")
            for plot_id in target_plots:
                # Schema check: does this plot's data have the column?
                if not _plot_has_column(plot_id, col):
                    skipped.setdefault(plot_id, []).append(col)
                    continue
                pending_nodes.append(make_recipe_node(
                    scratch_node["node_type"], dict(params),
                    plot_scope=plot_id,
                    reason="",
                    primary_key_warning=bool(scratch_node.get("primary_key_warning")),
                    node_id=shared_id,  # SHARED id across copies
                ))
                applied_count += 1

        home_state.set({**state, "_pending_t3_nodes": pending_nodes})
        _propagation_scratch.set({"nodes": [], "kind": ""})
        ui.modal_remove()

        msg = f"✅ {applied_count} audit entry(ies) added across {len(target_plots)} plot(s)."
        if skipped:
            skipped_summary = "; ".join(
                f"{_plot_label(p)}: {', '.join(cs)}"
                for p, cs in skipped.items()
            )
            msg += f" Skipped (column not in plot data): {skipped_summary}."
        _notify(msg, type="message", duration=7)

    def _plot_has_column(subtab_id: str, column: str) -> bool:
        """Return True if the plot's resolved LazyFrame has the column.

        Used by the propagation expansion to skip plots whose schema doesn't
        carry the targeted column (§12g.9). Errors fail-safe to True so we
        don't silently drop nodes when schema lookup is flaky.
        """
        if not column or not subtab_id:
            return True
        p_id = subtab_id.removeprefix("subtab_")
        try:
            spec = _resolve_active_spec(p_id)
            lf = _resolve_active_lf(spec)
            return column in lf.collect_schema().names()
        except Exception:
            return True

    # When btn_apply commits the T3 recipe, clear the left-panel filter list:
    # those rows are now permanent T3 nodes and should not be re-applicable as
    # transient filters. Triggered via t3_apply_count bumps in audit_stack.
    _last_apply_count = reactive.Value(0)

    @reactive.Effect
    def _clear_filters_on_t3_apply():
        """After T3 apply, clear left-panel filter staging.

        Both _pending_filters (staging UI) and applied_filters (active plot view)
        are cleared because T3 RecipeNodes now drive the plot via _t3_filter_rows
        (the legacy applied_filters path is no longer the source of truth once a
        node is committed to T3).
        """
        if home_state is None:
            return
        cnt = int(home_state.get().get("t3_apply_count", 0))
        if cnt > _last_apply_count.get():
            _last_apply_count.set(cnt)
            _pending_filters.set([])
            applied_filters.set([])

    # Dynamic remove buttons — one effect per row index up to a generous cap
    def _make_remove_handler(idx: int):
        @reactive.Effect
        @reactive.event(getattr(input, f"filter_remove_{idx}", lambda: None))
        def _remove():
            try:
                _ = getattr(input, f"filter_remove_{idx}")()
            except Exception:
                return
            current = list(_pending_filters.get())
            if idx < len(current):
                current.pop(idx)
                _pending_filters.set(current)
        return _remove

    # Register remove handlers for up to 50 filter rows
    _remove_handlers = [_make_remove_handler(i) for i in range(50)]
