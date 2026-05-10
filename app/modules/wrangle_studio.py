# app/modules/wrangle_studio.py

# @deps
# provides: class:WrangleStudio, method:_render_action_form, method:_extract_upstream_cols, output:bp_yaml_escape_ui, output:bp_help_panel_ui, function:_resolve_action_doc
# consumes: libs/transformer/src/transformer/actions/base.py (AVAILABLE_WRANGLING_ACTIONS)
# consumes: libs/blueprint_arch/src/blueprint_arch/schema_registry.py (get_action_catalog)
# consumes: app/src/bootloader.py (method:get_palettes — via self._bootloader, optional)
# consumed_by: app/handlers/home_theater.py, app/handlers/blueprint_handlers.py, app/handlers/audit_stack.py, app/handlers/gallery_handlers.py, app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-004, .claude/knowledge/architecture_decisions.md#ADR-075
# @end_deps

from pathlib import Path
from shiny import ui, reactive, render
import polars as pl
import yaml
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS


def _resolve_action_doc(wraps_entry: dict) -> str:
    """Resolve __doc__ from a ui_schema 'wraps' entry via importlib (BP-HELP-1).

    Air-gap safe — reads from the installed library at runtime with no network calls.
    """
    import importlib
    try:
        obj = importlib.import_module(wraps_entry["lib"])
        for attr in wraps_entry.get("attr_path", []):
            obj = getattr(obj, attr)
        return (getattr(obj, "__doc__", "") or "").strip()
    except Exception:
        return ""


class WrangleStudio:
    """ComponentName (wrangle_studio.py)
    Architectural visual builder for transformation logic stacks.
    ADR-004 / ADR-011: Data-Agnostic Column Selection.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        # Reactive list of active nodes: [{"action": "rename", "params": {"columns": ["x"], "new_name": "y"}}]
        self.logic_stack = reactive.Value([])
        # Temporary storage for node being annotated
        self.pending_node = reactive.Value(None)

        # Expanded Manifest Data (ADR-031 Expansion)
        self.active_raw_yaml = reactive.Value("")
        self.active_fields = reactive.Value({"input": [], "output": []})
        self.active_viz_spec = reactive.Value({})

        # [ADR-040] Lineage Contract Viewer state
        # Component metadata for the currently loaded file
        self.active_component_info = reactive.Value({})
        # Upstream contract: fields arriving at this component
        # Values: [] | dict | {"type":"ingredients","items":[...]} | {"type":"terminal"}
        self.active_upstream = reactive.Value([])
        # Downstream contract: fields leaving this component
        self.active_downstream = reactive.Value([])
        # [ADR-040] Ordered lineage chain for Rail: list of node dicts
        # Each: {"rel": str, "schema_id": str, "role": str, "label": str, "is_active": bool}
        self.active_lineage_chain = reactive.Value([])

        # [ADR-039] TubeMap Code
        self.active_viz_id = reactive.Value(None)
        self.data_ready_signal = reactive.Value(0)
        self.active_tubemap_mermaid = reactive.Value("")
        # Master manifest path — set on every component import so architect_active_plot
        # can load the full resolved config via ConfigManager (not just the fragment)
        self.active_manifest_path = reactive.Value("")
        # Anchor parquet path set after materialization so surgical calc reacts to it
        self.active_anchor_path = reactive.Value("")

        # BP-FORMS-1: Node editing state
        self.selected_node_idx = reactive.Value(None)  # int index of node being edited
        self.invalidated_from = reactive.Value(None)   # nodes >= this idx are schema-stale

    def render_ui(self):
        actions = list(AVAILABLE_WRANGLING_ACTIONS.keys())

        return ui.div(
            ui.div(
                ui.span("👣 Blueprint Architect Flight Deck", class_="banner-title"),
                ui.span(
                    "Pipeline overview — helps you build manifests.",
                    class_="banner-subtitle"
                ),
                class_="view-title-banner"
            ),

            # --- TOP: Interactive TubeMap (Collapsible) ---
            ui.div(
                ui.accordion(
                    ui.accordion_panel(
                        "🗺️ Project Lineage (TubeMap)",
                        ui.div(
                            # ── Toolbar ──────────────────────────────────────────
                            ui.div(
                                ui.tags.button("＋", onclick="cyZoomIn()",
                                    class_="btn btn-sm btn-outline-secondary control-btn",
                                    title="Zoom in"),
                                ui.tags.button("－", onclick="cyZoomOut()",
                                    class_="btn btn-sm btn-outline-secondary control-btn",
                                    title="Zoom out"),
                                ui.tags.button("⊡", onclick="cyFit()",
                                    class_="btn btn-sm btn-outline-secondary control-btn",
                                    title="Fit all"),
                                ui.tags.span("● Source",
                                    style="font-size:0.65rem;color:#fff;background:#0d6efd;border-radius:8px;padding:1px 6px;"),
                                ui.tags.span("● Wrangle",
                                    style="font-size:0.65rem;color:#212529;background:#ffc107;border-radius:8px;padding:1px 6px;"),
                                ui.tags.span("◆ Join",
                                    style="font-size:0.65rem;color:#fff;background:#9c27b0;border-radius:8px;padding:1px 6px;"),
                                ui.tags.span("■ Plot",
                                    style="font-size:0.65rem;color:#fff;background:#198754;border-radius:8px;padding:1px 6px;"),
                                ui.tags.span("● Add",
                                    style="font-size:0.65rem;color:#fff;background:#6c757d;border-radius:8px;padding:1px 6px;"),
                                ui.tags.span("● Meta",
                                    style="font-size:0.65rem;color:#fff;background:#fd7e14;border-radius:8px;padding:1px 6px;"),
                                class_="d-flex align-items-center gap-1 flex-wrap mb-1"
                            ),
                            # ── Viewport ─────────────────────────────────────────
                            ui.div(
                                ui.tags.div(id="cy_tooltip", style=(
                                    "display:none;position:absolute;top:6px;left:50%;transform:translateX(-50%);"
                                    "background:rgba(0,0,0,0.75);color:#fff;font-size:0.75rem;"
                                    "padding:2px 8px;border-radius:4px;pointer-events:none;z-index:100;"
                                    "white-space:nowrap;max-width:90%;"
                                )),
                                ui.output_ui("blueprint_tubemap_ui"),
                                style=(
                                    "position:relative;height:320px;overflow:hidden;"
                                    "background:#fafafa;border:1px solid #e9ecef;border-radius:6px;"
                                ),
                                id="tubemap_viewport"
                            ),
                            class_="p-2",
                        ),
                        value="blueprint_tubemap_panel"
                    ),
                    id="blueprint_tubemap_accordion",
                ),
                class_="spv-panel mb-3",
            ),

            # --- MIDDLE: Tabs (Logic / Interface / YAML) ---
            ui.navset_card_pill(
                ui.nav_panel(
                    "1. Focus (Logic)",
                    ui.layout_columns(
                        ui.card(
                            ui.card_header("Plan & Actions"),
                            ui.layout_columns(
                                ui.input_text(
                                    "bp_action_search", None,
                                    placeholder="Search actions...",
                                ),
                                ui.input_select(
                                    "bp_action_context", None,
                                    choices={
                                        "": "All contexts",
                                        "t1": "T1 — Trunk",
                                        "t2": "T2 — Branch",
                                        "assembly": "Assembly",
                                    }
                                ),
                                col_widths=[7, 5],
                            ),
                            ui.input_select("action_selector",
                                            "1. Select Action:", choices=actions),
                            ui.panel_conditional(
                                "input.action_selector == 'join' || input.action_selector == 'join_filter'",
                                ui.input_select("secondary_dataset_selector", "2b. Secondary Dataset:", choices=[
                                                "Select a source file..."]),
                                ui.input_select("right_on_selector", "2c. Right Join Key:", choices=[
                                                "Select a Dataset first"])
                            ),
                            ui.input_select("column_selector", "2. Target Column / Key:", choices=[
                                "Select a Dataset first"]),
                            ui.input_text(
                                "new_param_value", "3. Parameter (e.g. New Name):", placeholder="Optional..."),
                            ui.input_action_button(
                                "btn_add_node", "➕ Add Transformation Node", class_="btn-primary"),
                            ui.div(
                                ui.h6("Action Help"),
                                ui.output_text("action_help_text"),
                                style="background-color: #fff9c4; padding: 10px; border-radius: 4px; margin-top: 10px;"
                            )
                        ),
                        ui.card(
                            ui.card_header("Active Component Logic Stack"),
                            ui.output_ui("logic_stack_ui"),
                            ui.input_action_button(
                                "btn_clear_stack", "🗑️ Clear All nodes", class_="btn-outline-danger btn-sm mt-3")
                        ),
                        col_widths=[4, 8]
                    )
                ),
                ui.nav_panel(
                    "2. Interface (Fields)",
                    # Hidden text input receives rel_path from Rail node JS clicks
                    ui.tags.input(
                        id="lineage_node_rel",
                        type="text",
                        value="",
                        style="display:none;"
                    ),
                    # Local lineage rail — shows component chain context
                    ui.output_ui("lineage_rail_ui"),
                    # Vertical contract viewer (ADR-040) — upstream / active / downstream stacked
                    ui.div(
                        ui.card(
                            ui.card_header(ui.output_ui("upstream_label_ui")),
                            ui.div(
                                ui.output_ui("lineage_upstream_ui"),
                                style="overflow-y: auto; max-height: 260px;"
                            ),
                            style="margin-bottom: 8px;"
                        ),
                        ui.card(
                            ui.card_header(ui.output_ui("component_label_ui")),
                            ui.div(
                                ui.output_ui("lineage_component_ui"),
                                style="overflow-y: auto; max-height: 200px;"
                            ),
                            style="margin-bottom: 8px;"
                        ),
                        ui.card(
                            ui.card_header(ui.output_ui("downstream_label_ui")),
                            ui.div(
                                ui.output_ui("lineage_downstream_ui"),
                                style="overflow-y: auto; max-height: 260px;"
                            ),
                        ),
                        # BP-FIELD-GAP-1: Field Gap Analysis tool
                        ui.card(
                            ui.card_header("Field Gap Analysis"),
                            ui.layout_columns(
                                ui.input_text(
                                    "bp_field_query", None,
                                    placeholder="Enter field name (slug)...",
                                ),
                                ui.input_action_button(
                                    "btn_field_gap", "Find",
                                    class_="btn btn-primary btn-sm"
                                ),
                                col_widths=[9, 3],
                            ),
                            ui.output_ui("field_gap_ui"),
                        ),
                    )
                ),
                ui.nav_panel(
                    "3. YAML (Raw Source)",
                    ui.card(
                        ui.card_header("Manifest Source Inspector"),
                        ui.output_ui("yaml_source_viewer_ui")
                    )
                ),
                id="architect_internal_tabs",
            ),

            # --- BOTTOM: Two collapsible live-view cards stacked vertically ---
            # Card 1: Live Data Glimpse (top, collapsed by default = open)
            ui.tags.div(
                ui.tags.div(
                    ui.tags.button(
                        "📋 Live Data Glimpse",
                        ui.tags.span("▲", id="glimpse_chevron",
                                     style="float:right;transition:transform 0.2s;"),
                        **{"data-bs-toggle": "collapse",
                           "data-bs-target": "#glimpse_body",
                           "aria-expanded": "true"},
                        class_="btn btn-sm w-100 text-start fw-semibold",
                        style="background:#e9ecef;border:none;padding:6px 12px;"
                    ),
                    class_="card-header p-0"
                ),
                ui.tags.div(
                    ui.div(
                        ui.output_ui("architect_data_status_ui"),
                        ui.output_table("architect_active_table"),
                        class_="p-1",
                        style="overflow:auto;max-height:280px;"
                    ),
                    id="glimpse_body",
                    class_="collapse show card-body p-0"
                ),
                class_="card shadow-sm mb-2"
            ),
            class_="wrangle-studio-container"
        )

    def define_server(self, input, output, session, available_cols, get_base_data,
                      viz_factory, get_schema_registry=None, get_includes_map=None,
                      bootloader=None):
        # Store bootloader so instance methods (e.g. _render_action_form) can access it
        self._bootloader = bootloader

        # [ADR-039] Surgical Context State
        self.active_viz_id = reactive.Value(None)
        _plot_error = reactive.Value("")  # stores last render error message

        @reactive.Effect
        @reactive.event(input.blueprint_node_clicked)
        def handle_node_selection():
            node_id = input.blueprint_node_clicked()
            ui.notification_show(f"Surgical Focus: {node_id}", type="message")

            # [ADR-039] Resolve Component Logic
            raw_yaml = self.active_raw_yaml.get()
            if not raw_yaml:
                return

            try:
                full_cfg = yaml.safe_load(raw_yaml)
            except Exception:
                return

            # --- Logic Discovery ---
            found_logic = []

            # 1. Check Assemblies (Tier 2 Junctions)
            join_defs = full_cfg.get("join_manifests", {})
            if node_id in join_defs:
                recipe = join_defs[node_id].get("recipe", [])
                from transformer.data_wrangler import DataWrangler
                found_logic = DataWrangler._resolve_tier(recipe, "tier1")
                self.active_viz_id.set(None)  # Not a plot

            # 2. Check Plots (Terminals)
            elif node_id in full_cfg.get("plots", {}):
                found_logic = []  # Logic is in the parent assembly
                self.active_viz_id.set(node_id)
                # Find parent assembly and load its logic too?
                # For now, we just focus on the plot aesthetics

            # Update the surgical stack
            ui_nodes = []
            for node in found_logic:
                ui_nodes.append({
                    "action": node.get("action", "unknown"),
                    "params": {k: v for k, v in node.items() if k != "action"},
                    "comment": node.get("label", "Inherited from Manifest")
                })

            self.logic_stack.set(ui_nodes)

        @reactive.Calc
        def processed_data():
            lf = get_base_data()
            if lf is None:
                return None
            return self.apply_logic(lf).collect()

        @reactive.Calc
        def processed_data_surgical():
            """[ADR-040] Load the materialized anchor for the active surgical component.

            Reacts to active_anchor_path which is set by server.py after
            orchestrator.materialize_tier1 completes — so the calc only fires
            when real data is available.

            Logic application rules:
            - wrangling / plot_wrangling: apply logic_stack (transform raw ingredient)
            - assembly / output_fields / input_fields / plot_spec: serve parquet as-is
              (parquet IS the final product — re-applying recipe would double-transform)
            """
            anchor_path_str = self.active_anchor_path.get()
            if not anchor_path_str:
                return None
            anchor_p = Path(anchor_path_str)
            if not anchor_p.exists():
                return None
            try:
                lf = pl.scan_parquet(anchor_p)
                # Only apply in-memory logic for roles that represent a wrangling step
                role = self.active_component_info.get().get("role", "")
                if role in ("wrangling", "plot_wrangling"):
                    lf = self.apply_logic(lf)
                return lf.collect()
            except Exception as e:
                print(f"[Surgical] Data load failed: {e}")
                return None

        @output
        @render.ui
        def architect_plot_error_ui():
            err = _plot_error.get()
            if not err:
                return ui.div()
            return ui.div(
                ui.span("⚠️ ", style="font-size:1rem;"),
                ui.span(err, style="font-size:0.8rem;"),
                class_="alert alert-warning py-1 px-2 mb-1 small text-start"
            )

        @output
        @render.plot
        def architect_active_plot():
            viz_id = self.active_viz_id.get()
            manifest_path = self.active_manifest_path.get()
            if not viz_id or not manifest_path:
                _plot_error.set("")
                return None

            # Prioritize surgical data (materialized anchor for this component)
            df = processed_data_surgical()
            if df is None or df.height == 0:
                df = processed_data()  # Fallback to base project anchor

            if df is None or df.height == 0:
                _plot_error.set(f"No data loaded for '{viz_id}' — select a plot node to materialise its dataset.")
                return None

            try:
                from utils.config_loader import ConfigManager as _CM
                if not Path(manifest_path).exists():
                    _plot_error.set(f"Manifest not found: {manifest_path}")
                    return None
                full_cfg = _CM(manifest_path).raw_config

                # Resolve the plot spec from flat `plots:` (gallery bundles)
                # or modern `analysis_groups:` (pipeline manifests, ADR-043).
                render_manifest = None
                if viz_id in full_cfg.get("plots", {}):
                    render_manifest = full_cfg
                else:
                    for grp_spec in full_cfg.get("analysis_groups", {}).values():
                        if not isinstance(grp_spec, dict):
                            continue
                        plot_entry = grp_spec.get("plots", {}).get(viz_id)
                        if plot_entry is not None:
                            spec = (plot_entry.get("spec", plot_entry)
                                    if isinstance(plot_entry, dict) else plot_entry)
                            render_manifest = {
                                "plots": {viz_id: spec},
                                "plot_defaults": full_cfg.get("plot_defaults", {}),
                            }
                            break

                if render_manifest is None:
                    available = list(full_cfg.get("plots", {}).keys())
                    for grp in full_cfg.get("analysis_groups", {}).values():
                        if isinstance(grp, dict):
                            available.extend(grp.get("plots", {}).keys())
                    _plot_error.set(
                        f"Plot ID '{viz_id}' not found in manifest. "
                        f"Available: {', '.join(available[:5])}"
                    )
                    return None

                _plot_error.set("")
                plt = viz_factory.render(df.lazy(), render_manifest, viz_id)
                return plt
            except Exception as e:
                msg = str(e)
                print(f"[Plot Preview] Render failed for '{viz_id}': {msg}")
                _plot_error.set(f"Render error: {msg}")
                return None

        @output
        @render.ui
        def architect_data_status_ui():
            """Status line above the data table showing what is loaded."""
            anchor = self.active_anchor_path.get()
            info = self.active_component_info.get()
            schema_id = info.get("schema_id", "") if info else ""
            if not anchor:
                return ui.div(
                    ui.span("⏳ No data loaded — select a plot or wrangling component",
                            class_="text-muted small fst-italic"),
                    class_="px-2 py-1"
                )
            p = Path(anchor)
            exists = p.exists()
            if exists:
                try:
                    rows = pl.scan_parquet(p).select(pl.len()).collect().item()
                    cols = len(pl.scan_parquet(p).columns)
                    label = f"✅ {schema_id} — {rows:,} rows × {cols} cols  ({p.name})"
                    cls = "text-success small"
                except Exception:
                    label = f"✅ Loaded: {p.name}"
                    cls = "text-success small"
            else:
                label = f"⚠️ Anchor not found: {p.name}"
                cls = "text-warning small"
            return ui.div(ui.span(label, class_=cls), class_="px-2 py-1")

        @output
        @render.table
        def architect_active_table():
            df = processed_data_surgical()
            if df is None:
                df = processed_data()
            if df is None:
                return None
            return df.head(10)

        # Sync column selector with the active dataset
        @reactive.Effect
        def update_column_list():
            cols = available_cols()
            if cols:
                ui.update_select("column_selector", choices=cols)
                ui.update_select("right_on_selector", choices=cols)
            else:
                ui.update_select("column_selector", choices=[
                                 "No Columns Detected"])
                ui.update_select("right_on_selector", choices=[
                                 "No Columns Detected"])

        @reactive.Effect
        def update_secondary_datasets():
            # In a real app, this would scan the raw_data_dir
            # For this MVP, we simulate discovery
            datasets = ["raw_pipeline_output.tsv", "ResFinder_metadata.tsv"]
            ui.update_select("secondary_dataset_selector", choices=datasets)

        @output
        @render.text
        def action_help_text():
            action = input.action_selector()
            func = AVAILABLE_WRANGLING_ACTIONS.get(action)
            if func:
                return func.__doc__ or "No documentation available for this action."
            return "Select an action to see details."

        @reactive.Effect
        @reactive.event(input.btn_add_node)
        def add_node():
            action = input.action_selector()
            target_col = input.column_selector()
            extra_val = input.new_param_value()

            if action in ["join", "join_filter"]:
                # Trigger Join Preview Modal (ADR-012)
                self.show_join_modal(input, session, available_cols)
                return

            # Stage the node and show Annotation Modal
            self.pending_node.set({
                "action": action,
                "target_col": target_col,
                "extra_val": extra_val
            })
            self.show_annotation_modal(action, target_col, extra_val)

        @reactive.Effect
        @reactive.event(input.btn_confirm_node)
        def handle_confirm_node():
            comment = input.node_comment_modal()
            if not comment:
                ui.notification_show("⚠️ Comment is mandatory.", type="error")
                return

            node_data = self.pending_node.get()
            if node_data:
                self._finalize_add_node(
                    node_data["action"],
                    node_data["target_col"],
                    node_data["extra_val"],
                    comment
                )
                ui.modal_remove()
                self.pending_node.set(None)

        @reactive.Effect
        @reactive.event(input.confirm_join)
        def handle_confirm_join():
            comment = input.node_comment_join()
            if not comment:
                ui.notification_show(
                    "⚠️ Justification is mandatory for Joins.", type="error")
                return

            ui.modal_remove()
            action = input.action_selector()
            target_col = input.column_selector()
            secondary = input.secondary_dataset_selector()
            right_on = input.right_on_selector()

            curr = self.logic_stack.get().copy()
            params = {
                "left_on": target_col,
                "right_on": right_on,
                "right_ingredient": secondary
            }
            curr.append(
                {"action": action, "params": params, "comment": comment})
            self.logic_stack.set(curr)
            ui.notification_show(
                f"Join Node added: {secondary}", type="message")

        @reactive.Effect
        @reactive.event(input.btn_clear_stack)
        def clear_stack():
            self.logic_stack.set([])
            self.selected_node_idx.set(None)
            self.invalidated_from.set(None)
            ui.notification_show("Logic stack cleared.", type="warning")

        # BP-FORMS-1: Track node click → set selected_node_idx
        @reactive.Effect
        @reactive.event(input.bp_node_click)
        def _track_bp_node_click():
            val = input.bp_node_click()
            if val is not None:
                self.selected_node_idx.set(int(val))

        # BP-ACTION-PARITY-1: Reactive action picker — filter by search + context.
        # Updates action_selector choices using schema_registry when available, falling
        # back to AVAILABLE_WRANGLING_ACTIONS for actions without ui_schema.
        @reactive.Effect
        def _update_action_picker():
            query = (input.bp_action_search() or "").strip().lower()
            ctx = (input.bp_action_context() or "").strip()

            try:
                from blueprint_arch.schema_registry import get_action_catalog, search_actions, get_actions_for_context
                catalog = get_action_catalog()
            except Exception:
                catalog = {}

            if ctx and catalog:
                in_scope = set(get_actions_for_context(ctx).keys())
            else:
                in_scope = set(AVAILABLE_WRANGLING_ACTIONS.keys()) | set(catalog.keys())

            if query and catalog:
                matched = set(search_actions(query).keys())
                in_scope = in_scope & matched
            elif query:
                # Fallback substring match when catalog is empty
                in_scope = {k for k in in_scope if query in k}

            with_schema = {
                k: catalog[k].get("label", k)
                for k in sorted(in_scope)
                if k in catalog
            }
            without_schema = {
                k: k
                for k in sorted(in_scope)
                if k not in catalog and k in AVAILABLE_WRANGLING_ACTIONS
            }

            if with_schema and without_schema:
                choices = {
                    "Rich form (all params editable)": with_schema,
                    "YAML fallback (edit via escape hatch)": without_schema,
                }
            elif with_schema:
                choices = with_schema
            elif without_schema:
                choices = without_schema
            else:
                choices = {"(no matches)": "(no matches)"}

            ui.update_select("action_selector", choices=choices)

        @output
        @render.ui
        def bp_action_form_ui():
            """Edit form for the selected logic-stack node (BP-FORMS-1)."""
            idx = self.selected_node_idx.get()
            nodes = self.logic_stack.get()

            if idx is None or not nodes or idx >= len(nodes):
                return ui.div(
                    ui.p(
                        "Click a step in the logic stack to edit its parameters.",
                        class_="text-muted small fst-italic p-2"
                    ),
                )

            node = nodes[idx]
            action_name = node.get("action", "")
            current_params = node.get("params", {})
            current_comment = node.get("comment", "")

            try:
                from blueprint_arch.schema_registry import get_action_catalog
                catalog = get_action_catalog()
                ui_schema = catalog.get(action_name, {})
            except Exception:
                ui_schema = {}

            upstream_cols = self._extract_upstream_cols()

            inv_from = self.invalidated_from.get()
            is_stale = (inv_from is not None and idx >= inv_from)
            stale_banner = (
                ui.div(
                    "Schema may be stale — re-Apply to propagate changes.",
                    class_="bp-form-stale-banner"
                ) if is_stale else ui.span("")
            )

            if ui_schema:
                form_widgets = self._render_action_form(
                    action_name, ui_schema, current_params, upstream_cols
                )
                header_label = ui_schema.get("label", action_name)
            else:
                form_widgets = [
                    ui.p(
                        f"No form schema registered for '{action_name}'. "
                        "Edit params via the YAML escape hatch.",
                        class_="text-muted small"
                    )
                ]
                header_label = action_name

            return ui.div(
                stale_banner,
                ui.div(
                    ui.span(f"Step {idx + 1}: ", class_="text-muted small"),
                    ui.span(header_label, class_="fw-bold small"),
                    class_="mb-2"
                ),
                ui.input_text(
                    "bp_form_comment", "Comment",
                    value=current_comment,
                    placeholder="Why this transformation?"
                ),
                *form_widgets,
                ui.div(
                    ui.input_action_button(
                        "btn_bp_apply_node", "Apply",
                        class_="btn btn-primary btn-sm w-100"
                    ),
                    class_="mt-3"
                ),
                class_="bp-form-container p-2"
            )

        @output
        @render.ui
        def bp_help_panel_ui():
            """Help panel for the selected action (BP-HELP-1).

            Resolves documentation from:
            1. ui_schema 'wraps' entries — importlib __doc__ resolution
            2. Composite actions — one collapsible section per wrapped component
            3. Action function's own __doc__ as fallback
            Optional doc_url button, disabled when allow_external_links is false.
            """
            idx = self.selected_node_idx.get()
            nodes = self.logic_stack.get()

            if idx is None or not nodes or idx >= len(nodes):
                return ui.div()

            node = nodes[idx]
            action_name = node.get("action", "")

            try:
                from blueprint_arch.schema_registry import get_action_catalog
                catalog = get_action_catalog()
                ui_schema = catalog.get(action_name, {})
            except Exception:
                ui_schema = {}

            # Resolve allow_external_links from deployment profile
            allow_external = True
            if bootloader is not None:
                try:
                    allow_external = bootloader.profile.get("allow_external_links", True)
                except Exception:
                    pass

            doc_url = ui_schema.get("doc_url", "")
            wraps = ui_schema.get("wraps", [])
            label = ui_schema.get("label", action_name)
            description = ui_schema.get("description", "")

            parts = []

            # Description line from ui_schema
            if description:
                parts.append(ui.p(description, class_="bp-help-description"))

            if wraps:
                # Resolve __doc__ for each wrapped symbol
                is_composite = len(wraps) > 1
                if is_composite:
                    parts.append(
                        ui.p(
                            "This action combines: "
                            + ", ".join(
                                f"{w.get('attr_path', ['?'])[-1]}"
                                for w in wraps
                            ) + ". See component documentation:",
                            class_="bp-help-composite-intro"
                        )
                    )

                doc_panels = []
                panel_ids = []
                for i, wraps_entry in enumerate(wraps):
                    resolved_doc = _resolve_action_doc(wraps_entry)
                    panel_label = ".".join(wraps_entry.get("attr_path", ["?"]))
                    panel_id = f"bp_help_wrap_{abs(hash(action_name + str(i))) % 99999999}"
                    panel_ids.append(panel_id)
                    doc_panels.append(
                        ui.accordion_panel(
                            panel_label,
                            ui.tags.pre(
                                resolved_doc or "(No docstring available.)",
                                class_="bp-help-docstring"
                            ),
                            value=panel_id
                        )
                    )

                if doc_panels:
                    # Single wrap: open it. Composite: open none (user expands as needed).
                    open_val = panel_ids[0] if not is_composite else None
                    parts.append(
                        ui.accordion(
                            *doc_panels,
                            id=f"bp_help_acc_{abs(hash(action_name)) % 99999999}",
                            multiple=True,
                            open=open_val,
                        )
                    )

            else:
                # Fallback: resolve doc from the registered action function itself
                action_fn = AVAILABLE_WRANGLING_ACTIONS.get(action_name)
                fallback_doc = ""
                if action_fn is not None:
                    fallback_doc = (getattr(action_fn, "__doc__", "") or "").strip()
                if fallback_doc:
                    parts.append(
                        ui.tags.pre(
                            fallback_doc,
                            class_="bp-help-docstring"
                        )
                    )
                else:
                    parts.append(
                        ui.p("No documentation available for this action.",
                             class_="text-muted small fst-italic")
                    )

            # External URL button (disabled in isolated deployments)
            if doc_url:
                btn_disabled = not allow_external
                parts.append(
                    ui.div(
                        ui.tags.a(
                            "Open docs",
                            href=doc_url if allow_external else "#",
                            target="_blank",
                            rel="noopener noreferrer",
                            class_=(
                                "btn btn-sm w-100 bp-help-ext-btn"
                                + (" disabled" if btn_disabled else "")
                            ),
                            **({"aria_disabled": "true"} if btn_disabled else {}),
                        ),
                        class_="mt-2"
                    )
                )

            if not parts:
                return ui.div()

            return ui.div(
                ui.div(
                    ui.span(f"Help: {label}", class_="bp-help-header"),
                    class_="mb-2"
                ),
                *parts,
                class_="bp-help-container p-2"
            )

        @output
        @render.ui
        def blueprint_tubemap_ui():
            cy_json = self.active_tubemap_mermaid.get()  # now stores Cytoscape JSON
            if not cy_json:
                return ui.div(
                    ui.p("No Blueprint Lineage Loaded.", class_="text-muted fst-italic"),
                    ui.p("Select a project to view its TubeMap.", class_="small text-muted"),
                    class_="d-flex flex-column align-items-center justify-content-center h-100"
                )

            # Escape the JSON for safe embedding inside a JS string literal.
            # Replace backslashes first, then single-quotes, then newlines.
            safe_json = (cy_json
                         .replace("\\", "\\\\")
                         .replace("'", "\\'")
                         .replace("\n", "\\n")
                         .replace("\r", ""))

            return ui.div(
                # The Cytoscape canvas — must have an explicit ID and fill the parent
                ui.tags.div(
                    id="cy_tubemap",
                    style="width:100%;height:100%;",
                ),
                # Bootstrap: call initCyTubeMap after DOM is ready
                ui.tags.script(
                    f"(function(){{"
                    f"  var d=document.getElementById('cy_tubemap');"
                    f"  if(!d){{setTimeout(function(){{initCyTubeMap('{safe_json}','cy_tubemap');}},80);return;}}"
                    f"  initCyTubeMap('{safe_json}','cy_tubemap');"
                    f"}})();"
                ),
                id="blueprint_tubemap_container",
                style="width:100%;height:100%;"
            )

        # ── [ADR-040] Lineage Contract Viewer render functions ────────────────

        _TYPE_BADGE = {
            "categorical": ("bg-primary", "CAT"),
            "numeric":     ("bg-success", "NUM"),
            "string":      ("bg-secondary", "STR"),
            "boolean":     ("bg-warning text-dark", "BOOL"),
            "date":        ("bg-info text-dark", "DATE"),
        }

        def _field_card(slug, meta):
            """Render one field as a compact info card showing all metadata."""
            if not isinstance(meta, dict):
                meta = {"type": str(meta) if meta else "?"}

            ftype = meta.get("type", meta.get("dtype", "")).lower()
            badge_cls, badge_text = _TYPE_BADGE.get(ftype, ("bg-light text-dark border", ftype.upper() or "?"))
            label       = meta.get("label", "")
            orig        = meta.get("original_name", "")
            is_pk       = meta.get("is_primary_key", False)
            description = meta.get("description", "")

            # Header row: slug + type badge + PK marker
            header_parts = [
                ui.tags.code(slug, style="font-size:0.8rem;color:#0d6efd;"),
            ]
            if is_pk:
                header_parts.append(
                    ui.tags.span("🔑 PK", style="font-size:0.65rem;color:#fd7e14;margin-left:4px;")
                )
            header_parts.append(
                ui.tags.span(badge_text,
                             class_=f"badge {badge_cls} ms-2",
                             style="font-size:0.65rem;vertical-align:middle;")
            )

            # Detail rows — only show if they have content
            detail_parts = []
            if label:
                detail_parts.append(
                    ui.tags.div(
                        ui.tags.span("label: ", style="color:#6c757d;"),
                        ui.tags.span(label, style="color:#212529;"),
                        style="font-size:0.72rem;"
                    )
                )
            if orig and orig != slug:
                detail_parts.append(
                    ui.tags.div(
                        ui.tags.span("source col: ", style="color:#6c757d;"),
                        ui.tags.code(orig, style="font-size:0.7rem;background:#f8f9fa;"),
                        style="font-size:0.72rem;"
                    )
                )
            if description:
                detail_parts.append(
                    ui.tags.div(description,
                                style="font-size:0.7rem;color:#6c757d;font-style:italic;")
                )

            return ui.tags.div(
                ui.tags.div(*header_parts,
                            style="display:flex;align-items:center;flex-wrap:wrap;"),
                ui.tags.div(*detail_parts, style="margin-top:2px;padding-left:4px;"
                            ) if detail_parts else ui.tags.span(),
                style=(
                    "border-left:3px solid #0d6efd;padding:4px 8px;margin-bottom:4px;"
                    "background:#f8f9fa;border-radius:0 4px 4px 0;"
                )
            )

        def _fields_cards(fields, slot_name="fields"):
            """Render fields as hierarchical cards. Accepts dict or list."""
            # Normalise to dict {slug: meta}
            if not fields:
                return ui.p(f"No {slot_name} defined.", class_="text-muted fst-italic small")

            if isinstance(fields, dict):
                fields_dict = fields
                is_legacy = False
            elif isinstance(fields, list):
                # list of strings (legacy) or list of {name, dtype, ...}
                fields_dict = {}
                is_legacy = False
                for item in fields:
                    if isinstance(item, str):
                        fields_dict[item] = {}
                        is_legacy = True
                    elif isinstance(item, dict):
                        slug = item.get("name", item.get("field", str(item)))
                        fields_dict[slug] = {
                            "type": item.get("dtype", item.get("type", "")),
                            "label": item.get("description", ""),
                        }
            else:
                return ui.tags.pre(str(fields), class_="small")

            cards = [_field_card(slug, meta) for slug, meta in fields_dict.items()]
            count_badge = ui.tags.span(
                f"{len(cards)} field{'s' if len(cards) != 1 else ''}",
                class_="badge bg-secondary ms-2",
                style="font-size:0.65rem;vertical-align:middle;"
            )

            legacy_warning = ui.div()
            if is_legacy:
                legacy_warning = ui.div(
                    ui.span("⚠️ Legacy format. ", class_="me-2"),
                    ui.input_action_button(
                        "btn_normalize_fields", "⚙️ Fix Format",
                        class_="btn btn-sm btn-warning py-0 px-2"
                    ),
                    class_="alert alert-warning small py-1 px-2 mb-2 d-flex align-items-center"
                )

            return ui.div(
                ui.div(
                    ui.tags.span(slot_name, style="font-size:0.75rem;color:#6c757d;font-weight:600;"),
                    count_badge,
                    style="margin-bottom:4px;"
                ),
                legacy_warning,
                *cards,
            )

        # Keep _fields_table as alias for backward compat with assembly accordion
        def _fields_table(fields, slot_name="fields"):
            return _fields_cards(fields, slot_name)

        @output
        @render.ui
        def lineage_rail_ui():
            """Clickable horizontal chain showing the full lineage path through the active component."""
            chain = self.active_lineage_chain.get()
            if not chain:
                info = self.active_component_info.get()
                if not info:
                    return ui.div()
                # Fallback: static badge when chain not yet computed
                role = info.get("role", "unknown")
                schema_id = info.get("schema_id", "")
                role_colors = {
                    "input_fields": "primary", "output_fields": "success",
                    "wrangling": "warning", "join": "info",
                    "plot_wrangling": "warning", "plot_spec": "secondary",
                }
                return ui.div(
                    ui.span("Lineage Rail", class_="fw-bold me-2 small text-muted"),
                    ui.span(schema_id or "—",
                            class_=f"badge text-bg-{role_colors.get(role, 'light')}"),
                    class_="border rounded px-3 py-2 mb-2 bg-light d-flex align-items-center"
                )

            role_colors = {
                "input_fields": "#0d6efd", "output_fields": "#198754",
                "wrangling": "#ffc107", "join": "#0dcaf0",
                "plot_wrangling": "#fd7e14", "plot_spec": "#6c757d",
            }
            role_icons = {
                "input_fields": "📥", "output_fields": "📤",
                "wrangling": "⚙️", "join": "🔗",
                "plot_wrangling": "🔧", "plot_spec": "📊",
            }
            nodes_ui = []
            for i, node in enumerate(chain):
                r = node["role"]
                label = node["label"]
                color = role_colors.get(r, "#adb5bd")
                icon = role_icons.get(r, "●")
                is_active = node["is_active"]
                rel = node["rel"]

                border = "3px solid #212529" if is_active else f"2px solid {color}"
                bg = color if is_active else "#f8f9fa"
                text_color = "#fff" if is_active and r not in ("wrangling",) else "#212529"
                font_weight = "bold" if is_active else "normal"

                # JS onclick: set hidden input value + fire change event so Shiny detects it
                js = (
                    f"var el=document.getElementById('lineage_node_rel');"
                    f"el.value={rel!r};"
                    f"el.dispatchEvent(new Event('change'));"
                )
                node_div = ui.tags.button(
                    ui.tags.span(icon, style="font-size:0.85rem;"),
                    ui.tags.span(f" {label}",
                                 style=f"font-size:0.78rem;font-weight:{font_weight};display:block;"),
                    ui.tags.span(r, style="font-size:0.65rem;display:block;opacity:0.75;"),
                    onclick=js,
                    style=(
                        f"background:{bg};border:{border};"
                        f"color:{text_color};border-radius:6px;padding:4px 10px;"
                        f"min-width:80px;text-align:center;cursor:pointer;"
                        "white-space:normal;line-height:1.2;"
                    )
                )
                nodes_ui.append(node_div)

                # Arrow between nodes
                if i < len(chain) - 1:
                    nodes_ui.append(
                        ui.span("→", style="font-size:1rem;color:#6c757d;padding:0 4px;align-self:center;")
                    )

            return ui.div(
                ui.span("Lineage Rail", class_="fw-bold me-3 small text-muted align-self-center"),
                *nodes_ui,
                class_="border rounded px-3 py-2 mb-2 bg-light d-flex align-items-center flex-wrap gap-1",
                style="overflow-x:auto;"
            )

        @output
        @render.ui
        def upstream_label_ui():
            info = self.active_component_info.get()
            role = info.get("role", "") if info else ""
            if role == "join":
                label = "Ingredients"
            elif role == "plot_wrangling":
                label = "Join Output (Input)"
            else:
                label = "Upstream Contract"
            return ui.span(label)

        @output
        @render.ui
        def lineage_upstream_ui():
            upstream = self.active_upstream.get()
            info = self.active_component_info.get()
            role = info.get("role", "") if info else ""

            if not upstream:
                return ui.p("No upstream contract.", class_="text-muted italic small")

            # Assembly: multi-ingredient accordion
            if role == "join" and isinstance(upstream, list) and upstream:
                panels = []
                for item in upstream:
                    if isinstance(item, dict) and "id" in item:
                        ing_id = item.get("id", "ingredient")
                        fields = item.get("fields", {})
                        panels.append(
                            ui.accordion_panel(
                                ing_id,
                                _fields_cards(fields, ing_id),
                                value=ing_id
                            )
                        )
                if panels:
                    return ui.accordion(*panels, open=True, multiple=True)

            # Dict (Rich Dict from _resolve_fields_for_schema) or list
            return _fields_cards(upstream, "upstream fields")

        @output
        @render.ui
        def component_label_ui():
            info = self.active_component_info.get()
            if not info:
                return ui.span("Selected Component")
            schema_id = info.get("schema_id", "Component")
            return ui.span(schema_id)

        @output
        @render.ui
        def lineage_component_ui():
            info = self.active_component_info.get()
            if not info:
                return ui.p("Select a component from the tree.",
                            class_="text-muted italic small")
            role = info.get("role", "unknown")
            schema_id = info.get("schema_id", "")
            schema_type = info.get("schema_type", "")
            ingredients = info.get("ingredients", [])

            parts = [
                ui.p(ui.strong("schema_id: "), schema_id or "—", class_="mb-1 small"),
                ui.p(ui.strong("role: "), role, class_="mb-1 small"),
                ui.p(ui.strong("schema_type: "), schema_type or "—", class_="mb-1 small"),
            ]
            if ingredients:
                parts.append(
                    ui.p(
                        ui.strong("ingredients: "),
                        ui.span(", ".join(ingredients), class_="small text-muted"),
                        class_="mb-1 small"
                    )
                )

            # Inline wrangling indicator
            wrangling_slot = info.get("wrangling")
            if isinstance(wrangling_slot, dict) and "inline" in wrangling_slot:
                parts.append(
                    ui.div(
                        ui.span("\u26a1 Inline wrangling", class_="small text-warning"),
                        class_="mt-1"
                    )
                )

            # Plot spec: show pre_plot_wrangling status
            if role == "plot_spec":
                has_pre_wrn = isinstance(wrangling_slot, str)  # str = rel_path = file exists
                if has_pre_wrn:
                    parts.append(
                        ui.div(
                            ui.span("🔧 Pre-plot wrangling linked",
                                    class_="small text-success"),
                            class_="mt-1"
                        )
                    )
                else:
                    parts.append(
                        ui.div(
                            ui.input_action_button(
                                "btn_add_plot_wrangling",
                                "➕ Add plot wrangling",
                                class_="btn btn-sm btn-outline-warning mt-1"
                            ),
                            class_="mt-1"
                        )
                    )

            return ui.div(*parts, class_="p-2")

        @output
        @render.ui
        def downstream_label_ui():
            info = self.active_component_info.get()
            role = info.get("role", "") if info else ""
            if role in ("input_fields", "wrangling", "join"):
                label = "Output Fields"
            elif role == "plot_wrangling":
                label = "→ Plot Spec (Terminal)"
            else:
                label = "Downstream Contract"
            return ui.span(label)

        @output
        @render.ui
        def lineage_downstream_ui():
            downstream = self.active_downstream.get()
            if not downstream:
                return ui.p("No downstream contract.", class_="text-muted italic small")
            return _fields_cards(downstream, "output fields")

        # BP-FIELD-GAP-1: Field Gap Analysis — trace a field name through the loaded tiers.
        @output
        @render.ui
        @reactive.event(input.btn_field_gap)
        def field_gap_ui():
            query = (input.bp_field_query() or "").strip().lower()
            if not query:
                return ui.div(
                    ui.p("Enter a field name above and press Find.",
                         class_="text-muted small fst-italic mt-2")
                )

            upstream = self.active_upstream.get()
            downstream = self.active_downstream.get()
            chain = self.active_lineage_chain.get()
            info = self.active_component_info.get() or {}

            def _in_fields(fields) -> bool:
                if isinstance(fields, dict):
                    return query in {k.lower() for k in fields}
                if isinstance(fields, list):
                    return any(
                        (isinstance(f, dict) and query in (f.get("name", ""), f.get("field", "")).lower())
                        or (isinstance(f, str) and query == f.lower())
                        for f in fields
                    )
                return False

            up_found = _in_fields(upstream)
            down_found = _in_fields(downstream)
            schema_id = info.get("schema_id", "current component")

            rows = []

            if up_found:
                rows.append(
                    ui.div(
                        ui.tags.span("Found", class_="badge bg-success me-2"),
                        f"'{query}' is in upstream contract (input to {schema_id})",
                        class_="small mb-1"
                    )
                )
            if down_found:
                rows.append(
                    ui.div(
                        ui.tags.span("Found", class_="badge bg-success me-2"),
                        f"'{query}' is in output contract (produced by {schema_id})",
                        class_="small mb-1"
                    )
                )
            if not up_found and not down_found:
                rows.append(
                    ui.div(
                        ui.tags.span("Not here", class_="badge bg-warning text-dark me-2"),
                        f"'{query}' not found at {schema_id}.",
                        class_="small mb-1"
                    )
                )
                if len(chain) > 1:
                    active_idx = next(
                        (i for i, n in enumerate(chain) if n.get("is_active")), None
                    )
                    if active_idx is not None and active_idx > 0:
                        upstream_nodes = [n["label"] for n in chain[:active_idx]]
                        rows.append(
                            ui.div(
                                ui.tags.span("Hint", class_="badge bg-secondary me-2"),
                                f"Click upstream in the Rail to check: {', '.join(upstream_nodes)}",
                                class_="small text-muted mb-1"
                            )
                        )
                    elif active_idx == 0:
                        rows.append(
                            ui.div(
                                ui.tags.span("Hint", class_="badge bg-secondary me-2"),
                                "This is the root tier. The field must be added "
                                "here (mutate/derive step in Tier 1 wrangling).",
                                class_="small text-muted mb-1"
                            )
                        )

            # BP-FWD-HINT-1: Forward propagation hint — which downstream contracts
            # would drop this field if it were added/renamed at the current tier?
            manifest_path = self.active_manifest_path.get()
            if (up_found or down_found) and manifest_path and chain:
                try:
                    from blueprint_arch.manifest_navigator import build_sibling_map as _bsm
                    ctx = _bsm(manifest_path)
                    active_idx = next(
                        (i for i, n in enumerate(chain) if n.get("is_active")), None
                    )
                    fwd_warnings = []
                    if active_idx is not None:
                        for node in chain[active_idx + 1:]:
                            node_rel = node.get("rel", "")
                            entry = ctx.get(node_rel, {})
                            sib = entry.get("siblings", {})
                            if not isinstance(sib, dict):
                                continue
                            out_slot = sib.get("output_fields")
                            if not out_slot:
                                continue
                            # Check inline final_contract
                            if isinstance(out_slot, dict) and "inline" in out_slot:
                                contract_fields = {
                                    k.lower() for k in out_slot["inline"]
                                }
                                if query not in contract_fields:
                                    fwd_warnings.append(
                                        f"{node.get('label', node_rel)} — inline contract does not include '{query}'"
                                    )
                            elif isinstance(out_slot, str):
                                # Explicit file — can't load here without inc_map, flag as "check manually"
                                fwd_warnings.append(
                                    f"{node.get('label', node_rel)} — has explicit output_fields file (verify '{query}' is listed)"
                                )

                    if fwd_warnings:
                        rows.append(
                            ui.div(
                                ui.tags.hr(),
                                ui.div(
                                    ui.tags.span("Forward impact", class_="badge bg-danger me-2"),
                                    "These downstream contracts will drop this field unless updated:",
                                    class_="small fw-bold mb-1"
                                ),
                                *[
                                    ui.div(
                                        ui.tags.span("Update needed", class_="badge bg-warning text-dark me-2"),
                                        w,
                                        class_="small mb-1"
                                    )
                                    for w in fwd_warnings
                                ],
                                class_="mt-2"
                            )
                        )
                    else:
                        rows.append(
                            ui.div(
                                ui.tags.hr(),
                                ui.div(
                                    ui.tags.span("Forward clear", class_="badge bg-success me-2"),
                                    f"No downstream contract explicitly excludes '{query}'.",
                                    class_="small"
                                ),
                                class_="mt-2"
                            )
                        )
                except Exception:
                    pass

            return ui.div(*rows, class_="mt-2 p-1")

        @reactive.Effect
        @reactive.event(input.btn_add_plot_wrangling)
        def handle_add_plot_wrangling():
            """Inform the user how to scaffold a pre_plot_wrangling file.
            Full scaffolding (Phase 18-D complete) will auto-create the file and
            insert the pre_plot_wrangling: !include key into the manifest plot block.
            """
            info = self.active_component_info.get()
            schema_id = info.get("schema_id", "this plot") if info else "this plot"
            ui.notification_show(
                f"To add plot wrangling for '{schema_id}': create a wrangling YAML "
                f"and add 'pre_plot_wrangling: !include <path>' to its plot block in "
                f"the master manifest. Then reload the manifest.",
                type="message",
                duration=8
            )

        @reactive.Effect
        @reactive.event(input.lineage_node_rel)
        def handle_lineage_node_click():
            """When user clicks a Rail node, load that component into the 3-column panel.
            Updates the pipeline selector then programmatically fires btn_import_manifest.
            """
            rel = input.lineage_node_rel()
            if not rel:
                return
            ui.update_select("dataset_pipeline_selector", selected=rel)
            ui.js_eval("document.getElementById('btn_import_manifest').click();")

        @output
        @render.ui
        def yaml_source_viewer_ui():
            yaml_str = self.active_raw_yaml.get()
            if not yaml_str:
                return ui.div(
                    ui.p(
                        "💡 Select a component file from the left and click ",
                        ui.strong("Load Component"),
                        " to view its YAML here.",
                        class_="text-muted small"
                    )
                )
            try:
                yaml_obj = yaml.safe_load(yaml_str)
            except Exception:
                # Parse failure: show raw text
                return ui.tags.pre(
                    yaml_str,
                    style="background:#1e1e2e;color:#cdd6f4;padding:15px;"
                          "border-radius:6px;overflow:auto;max-height:600px;"
                          "font-size:0.82rem;white-space:pre-wrap;"
                )

            # ── Accordion: one panel per top-level key, ALL open by default ───
            if not isinstance(yaml_obj, dict):
                # File is a plain list or scalar — show as raw YAML
                return ui.tags.pre(
                    yaml.dump(yaml_obj, default_flow_style=False,
                              allow_unicode=True),
                    style="background:#1e1e2e;color:#cdd6f4;padding:15px;"
                          "border-radius:6px;overflow:auto;max-height:600px;"
                          "font-size:0.82rem;white-space:pre-wrap;"
                )

            panels = []
            open_ids = []  # all panel ids — used to pre-open every panel

            for key, val in yaml_obj.items():
                panel_id = f"yp_{abs(hash(str(key))) % 99999999}"
                open_ids.append(panel_id)
                is_collection = isinstance(val, (dict, list))
                icon = "📂" if is_collection else "🔑"
                val_yaml = (
                    yaml.dump(val, default_flow_style=False,
                              allow_unicode=True)
                    if is_collection else str(val)
                )
                panels.append(
                    ui.accordion_panel(
                        f"{icon} {key}",
                        ui.tags.pre(
                            val_yaml,
                            style="background:#1e1e2e;color:#cdd6f4;padding:8px;"
                                  "border-radius:4px;font-size:0.8rem;"
                                  "max-height:400px;overflow:auto;white-space:pre-wrap;"
                        ),
                        value=panel_id
                    )
                )

            tree_id = f"ya_{abs(hash('yaml_viewer')) % 99999999}"
            return ui.div(
                ui.accordion(
                    *panels,
                    id=tree_id,
                    multiple=True,
                    open=open_ids  # all panels expanded by default
                )
            )

        @output
        @render.ui
        def bp_yaml_escape_ui():
            """YAML escape hatch (BP-ESCAPE-1).

            Read-only pre block for all blueprint_enabled personas.
            Editable textarea + Save when manifest_edit_enabled is true.
            """
            raw = self.active_raw_yaml.get()
            editable = bootloader is not None and bootloader.is_enabled("manifest_edit_enabled")

            if not raw:
                return ui.div(
                    ui.p("No manifest loaded. Select a manifest in the left panel first.",
                         class_="text-muted small fst-italic"),
                    class_="bp-escape-container p-2"
                )

            if editable:
                return ui.div(
                    ui.div(
                        ui.span("Edit mode — changes take effect on Save",
                                class_="bp-escape-edit-badge"),
                        class_="mb-2"
                    ),
                    ui.input_text_area(
                        "bp_yaml_raw_edit",
                        None,
                        value=raw,
                        rows=20,
                        width="100%",
                    ),
                    ui.input_action_button(
                        "btn_bp_save_yaml",
                        "Save & Re-parse",
                        class_="btn btn-primary btn-sm w-100 mt-2"
                    ),
                    class_="bp-escape-container p-2"
                )

            # Read-only view
            return ui.div(
                ui.div(
                    ui.span("Read-only", class_="bp-escape-readonly-badge"),
                    class_="mb-2"
                ),
                ui.tags.pre(
                    raw,
                    class_="bp-escape-pre"
                ),
                class_="bp-escape-container p-2"
            )

        @output
        @render.ui
        def logic_stack_ui():
            # BP-FORMS-1: nodes are clickable; selected node gets highlight;
            # nodes downstream of last Apply are marked stale.
            nodes = self.logic_stack.get()
            if not nodes:
                return ui.p(
                    "No active transformation nodes. "
                    "Click a TubeMap node to load its wrangling steps.",
                    class_="text-muted small fst-italic"
                )

            selected_idx = self.selected_node_idx.get()
            inv_from = self.invalidated_from.get()
            ui_nodes = []

            for i, node in enumerate(nodes):
                action = node.get("action", "unknown")
                comment = node.get("comment", "")
                params = node.get("params", {})

                is_selected = (selected_idx == i)
                is_stale = (inv_from is not None and i >= inv_from)

                extra_class = (
                    " bp-node-selected" if is_selected
                    else (" bp-node-invalidated" if is_stale else "")
                )

                stale_el = (
                    ui.span("stale", class_="badge ms-1",
                            style="background:#ffc107;color:#000;font-size:0.65rem;")
                    if is_stale else ui.span("")
                )

                params_preview = str(params)
                if len(params_preview) > 80:
                    params_preview = params_preview[:77] + "..."

                ui_nodes.append(
                    ui.div(
                        ui.div(
                            ui.span(f"{i + 1}. {action}", class_="fw-bold small"),
                            stale_el,
                        ),
                        ui.div(
                            ui.span(comment,
                                    style="color:#666;font-style:italic;font-size:0.78rem;")
                            if comment else ui.span("")
                        ),
                        ui.div(
                            ui.span(params_preview, class_="text-muted",
                                    style="font-size:0.72rem;")
                        ),
                        onclick=(f"Shiny.setInputValue('bp_node_click', {i},"
                                 " {priority: 'event'});"),
                        class_=f"p-2 mb-1 border rounded bp-node-card{extra_class}",
                        style="cursor:pointer;"
                    )
                )
            return ui.div(*ui_nodes)

    def _parse_fields_safe(self, fields):
        """Safely normalises input_fields/output_fields from either dict or list format.
        Returns (rows: list[dict], is_legacy: bool).
        is_legacy=True when the file uses a non-standard dict format (simple or rich).
        Standard format is a list [{name, dtype, description}].
        """
        is_legacy = False
        if isinstance(fields, dict):
            if not fields:
                return [], False
            is_legacy = True
            rows = []
            for k, v in fields.items():
                if isinstance(v, dict):
                    # Rich metadata: {original_name, type/dtype, label, ...}
                    rows.append({
                        "field": k,
                        "type": v.get("type", v.get("dtype", "?")),
                        "description": v.get("label", v.get("description", ""))
                    })
                else:
                    rows.append({"field": k, "type": str(v), "description": ""})
        elif isinstance(fields, list):
            rows = []
            for item in fields:
                if isinstance(item, dict):
                    rows.append({
                        "field": item.get("name", item.get("field", "?")),
                        "type": item.get("dtype", item.get("type", "?")),
                        "description": item.get("description", ""),
                    })
                else:
                    # Scalar string — legacy flat list
                    rows.append(
                        {"field": str(item), "type": "?", "description": ""})
                    is_legacy = True
        else:
            rows = []
        return rows, is_legacy

    def _render_yaml_tree(self, yaml_obj, path="root"):
        """Recursively renders a YAML dict as nested Bootstrap accordion panels.
        Uses full key-path hashing to guarantee globally unique DOM IDs."""
        if not isinstance(yaml_obj, dict):
            return ui.tags.pre(
                str(yaml_obj),
                style="background:#1e1e2e;color:#cdd6f4;padding:8px;border-radius:4px;"
                      "font-size:0.8rem;max-height:200px;overflow:auto;"
            )

        panels = []
        for key, val in yaml_obj.items():
            child_path = f"{path}__{key}"
            # Unique IDs using full path hash (avoids all sibling/depth collisions)
            panel_id = f"yp_{abs(hash(child_path)) % 9999999}"
            is_nested = isinstance(val, dict)
            summary_text = f"📂 {key}" if is_nested else f"🔑 {key}"

            focus_btn = ui.tags.button(
                "🎯",
                onclick=f"window.mermaidClick('{key}');",
                title=f"Highlight {key} in TubeMap",
                class_="btn btn-sm btn-outline-secondary py-0 px-1 ms-2",
                style="font-size: 0.7rem;"
            )

            body_content = (
                self._render_yaml_tree(val, path=child_path) if is_nested
                else ui.tags.pre(
                    str(val),
                    style="background:#1e1e2e;color:#cdd6f4;padding:8px;border-radius:4px;"
                          "font-size:0.8rem;max-height:150px;overflow:auto;white-space:pre-wrap;"
                )
            )

            panels.append(
                ui.accordion_panel(
                    ui.div(summary_text, focus_btn,
                           class_="d-flex align-items-center"),
                    body_content,
                    value=panel_id
                )
            )

        if not panels:
            return ui.p("(empty)", class_="text-muted small")

        tree_id = f"ya_{abs(hash(path)) % 9999999}"
        return ui.accordion(*panels, id=tree_id, multiple=True)

    def _finalize_add_node(self, action, target_col, extra_val, comment):
        curr = self.logic_stack.get().copy()
        params = {"columns": [target_col]}

        if action == "rename" and extra_val:
            params["new_name"] = extra_val
        elif action == "cast" and extra_val:
            params["dtype"] = extra_val
        elif action == "fill_nulls" and extra_val:
            params["value"] = extra_val

        curr.append({"action": action, "params": params, "comment": comment})
        self.logic_stack.set(curr)
        ui.notification_show(
            f"Node added: {action}({target_col})", type="message")

    def show_annotation_modal(self, action, target_col, extra_val):
        m = ui.modal(
            ui.div(
                ui.h3("Annotate Transformation", class_="mb-3"),
                ui.div(
                    ui.tags.b("Action: "), ui.tags.span(action),
                    ui.br(),
                    ui.tags.b("Target: "), ui.tags.span(target_col),
                    ui.br(),
                    ui.tags.b("Parameter: "), ui.tags.span(
                        extra_val) if extra_val else ui.tags.i("None"),
                    class_="mb-3 p-2 border rounded bg-white"
                ),
                ui.input_text_area("node_comment_modal", "Justification / User Note:",
                                   placeholder="Explain the purpose of this transformation step...",
                                   width="100%", rows=3),
                class_="p-2"
            ),
            title="ADR-026: Mandatory User Note",
            footer=ui.div(
                ui.modal_button("Cancel"),
                ui.input_action_button(
                    "btn_confirm_node", "Confirm & Append", class_="btn-success")
            ),
            size="m",
            easy_close=False,
            # class_ is not natively supported in ui.modal but we can wrap content
        )
        # Note: We use the CSS class in ui.py to target the modal dialog if needed,
        # or we wrap the content in a styled div.
        # But wait, ui.modal in shiny-python doesn't easily expose the top-level class.
        # I'll use a direct style tag for the modal body if needed.
        ui.modal_show(m)

    def show_join_modal(self, input, session, available_cols):
        # 1. Validation Logic
        left_col = input.column_selector()
        right_col = input.right_on_selector()
        secondary = input.secondary_dataset_selector()

        # Visual Indicators (Green/Red)
        pk_match = left_col == right_col
        status_color = "#e8f5e9" if pk_match else "#ffebee"
        status_text = "✅ Primary Key Contract Met" if pk_match else "❌ Primary Key Mismatch (Column Names)"

        # Preview Data (Simulated for Evidence)
        m = ui.modal(
            ui.h3("Join Integrity Preview"),
            ui.p(f"Attempting to join Anchor with: {secondary}"),
            ui.hr(),
            ui.layout_columns(
                ui.div(
                    ui.h6("Anchor (Join Key)"),
                    ui.tags.pre("ID_1\nID_2\nID_3\nID_4\nID_5"),
                    style="background: #f8f9fa; padding: 10px;"
                ),
                ui.div(
                    ui.h6(f"{secondary} (Join Key)"),
                    ui.tags.pre("ID_1\nID_2\nID_99\nID_4\nID_100"),
                    style="background: #f8f9fa; padding: 10px;"
                )
            ),
            ui.div(
                ui.h5(status_text),
                ui.p("Overlap Detection: 60% of keys matched (3/5 in preview)."),
                ui.input_text_area("node_comment_join", "Justification for Join:",
                                   placeholder="Why are you merging these datasets?", width="100%", rows=2),
                style=f"background-color: {status_color}; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px solid #ccc;"
            ),
            title="ADR-012: Join Integrity Gate",
            footer=ui.div(
                ui.modal_button("Cancel"),
                ui.input_action_button(
                    "confirm_join", "Proceed with Join", class_="btn-success")
            ),
            size="l",
            easy_close=True
        )
        ui.modal_show(m)

    def _extract_upstream_cols(self) -> dict:
        """Return {col_name: 'numeric'|'categorical'} from active_upstream.

        Used by column_selector widgets to offer dtype-appropriate column choices.
        """
        upstream = self.active_upstream.get()
        cols: dict = {}
        _NUMERIC = {"numeric", "float", "int", "float64", "int64", "int32",
                    "float32", "integer", "number"}

        if isinstance(upstream, dict):
            for name, props in upstream.items():
                if isinstance(props, dict):
                    dtype = str(props.get("type") or props.get("dtype", "string")).lower()
                else:
                    dtype = "string"
                cols[name] = "numeric" if dtype in _NUMERIC else "categorical"
        elif isinstance(upstream, list):
            for item in upstream:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("field", "?")
                    dtype = str(item.get("type") or item.get("dtype", "string")).lower()
                    cols[name] = "numeric" if dtype in _NUMERIC else "categorical"
                elif isinstance(item, str):
                    cols[item] = "categorical"
        return cols

    def _render_action_form(self, action_name, ui_schema, current_params,
                            upstream_cols) -> list:
        """Build Shiny UI form widgets for an action's ui_schema params.

        Returns a list of Shiny UI elements, one per declared parameter.
        """
        params_schema = ui_schema.get("params", {})
        if not params_schema:
            return [ui.p("No configurable parameters for this action.",
                         class_="text-muted small")]

        _POLARS_TYPES = ["String", "Categorical", "Int64", "Int32", "Float64",
                         "Float32", "Boolean", "Date", "Datetime", "UInt32", "UInt64"]
        widgets = []

        for param_key, param_def in params_schema.items():
            widget_type = param_def.get("widget", "string")
            label = param_def.get("label", param_key)
            required = param_def.get("required", False)
            hint = param_def.get("hint", "")
            current_val = current_params.get(param_key)
            input_id = f"bp_form_{param_key}"

            if required:
                label = f"{label} *"

            hint_el = (ui.p(hint, class_="ultra-small text-muted mb-0")
                       if hint else None)

            if widget_type == "column_selector":
                multi = param_def.get("multi", False)
                dtype_filter = param_def.get("dtype_filter", [])
                choices = [k for k, v in upstream_cols.items()
                           if not dtype_filter or v in dtype_filter]
                if not choices:
                    choices = list(upstream_cols.keys()) or ["(no upstream columns)"]

                if isinstance(current_val, list):
                    selected = current_val
                elif isinstance(current_val, str):
                    selected = [current_val] if multi else current_val
                else:
                    selected = [] if multi else None

                elem = ui.input_selectize(
                    input_id, label, choices=choices,
                    selected=selected, multiple=multi
                )

            elif widget_type == "expression":
                elem = ui.input_text_area(
                    input_id, label,
                    value=str(current_val or ""),
                    placeholder='pl.col("column").str.strip_chars()',
                    rows=3
                )

            elif widget_type == "enum":
                options = param_def.get("options", [])
                elem = ui.input_select(
                    input_id, label,
                    choices={v: v for v in options},
                    selected=str(current_val or (options[0] if options else ""))
                )

            elif widget_type == "dtype_picker":
                elem = ui.input_select(
                    input_id, label,
                    choices={t: t for t in _POLARS_TYPES},
                    selected=str(current_val or "String")
                )

            elif widget_type == "number":
                elem = ui.input_numeric(
                    input_id, label,
                    value=(float(current_val) if current_val is not None
                           else float(param_def.get("default", 0)))
                )

            elif widget_type == "bool":
                elem = ui.input_checkbox(
                    input_id, label,
                    value=bool(current_val) if current_val is not None else False
                )

            elif widget_type == "column_or_literal":
                mode_id = f"bp_form_{param_key}_mode"
                col_id = f"bp_form_{param_key}_col"
                lit_id = f"bp_form_{param_key}_lit"
                col_choices = list(upstream_cols.keys()) or ["(none)"]

                if isinstance(current_val, str) and current_val in upstream_cols:
                    current_mode = "column"
                    current_col_val = current_val
                    current_lit_val = ""
                else:
                    current_mode = "literal"
                    current_col_val = col_choices[0]
                    current_lit_val = str(current_val or "")

                elem = ui.div(
                    ui.p(label, class_="fw-bold small mb-1"),
                    ui.input_radio_buttons(
                        mode_id, None,
                        choices={"column": "Map to column",
                                 "literal": "Set literal"},
                        selected=current_mode, inline=True
                    ),
                    ui.panel_conditional(
                        f"input['{mode_id}'] === 'column'",
                        ui.input_selectize(col_id, "Column",
                                           choices=col_choices,
                                           selected=current_col_val)
                    ),
                    ui.panel_conditional(
                        f"input['{mode_id}'] === 'literal'",
                        ui.input_text(lit_id, "Value", value=current_lit_val)
                    ),
                )

            elif widget_type == "color":
                # BP-COLOR-1/2: composite color widget with project palette support
                # Sub-IDs follow the pattern bp_form_{param_key}_*
                mode_id = f"bp_form_{param_key}_mode"      # column | literal
                col_id = f"bp_form_{param_key}_col"        # column selector
                lit_mode_id = f"bp_form_{param_key}_lmode" # palette | project | custom
                palette_id = f"bp_form_{param_key}_palette"
                project_palette_id = f"bp_form_{param_key}_project_palette"
                hex_id = f"bp_form_{param_key}_hex"

                # Runtime matplotlib palette names (authoritative)
                _LIB_PALETTES = [
                    "Blues", "Greens", "Oranges", "Purples", "Reds",
                    "BuGn", "BuPu", "GnBu", "OrRd", "PuBu", "YlGn",
                    "RdYlGn", "RdYlBu", "Spectral",
                    "viridis", "plasma", "magma", "inferno", "cividis",
                    "Set1", "Set2", "Set3", "Paired", "Dark2", "Accent",
                ]

                # Project palettes from deployment registry (BP-COLOR-2)
                _project_palettes = {}
                if self._bootloader is not None:
                    _project_palettes = self._bootloader.get_palettes()
                _has_project_palettes = bool(_project_palettes)

                cat_cols = [k for k, v in upstream_cols.items()
                            if v == "categorical"]
                cat_cols = cat_cols or list(upstream_cols.keys()) or ["(none)"]

                # Determine current mode from saved value
                if isinstance(current_val, dict):
                    top_mode = current_val.get("mode", "literal")
                    cur_col = current_val.get("column", cat_cols[0])
                    cur_lmode = current_val.get("literal_mode", "palette")
                    cur_palette = current_val.get("palette", _LIB_PALETTES[0])
                    cur_project_palette = current_val.get(
                        "project_palette",
                        next(iter(_project_palettes), "")
                    )
                    cur_hex = current_val.get("hex", "#345beb")
                elif isinstance(current_val, str) and current_val in upstream_cols:
                    top_mode = "column"
                    cur_col = current_val
                    cur_lmode = "palette"
                    cur_palette = _LIB_PALETTES[0]
                    cur_project_palette = next(iter(_project_palettes), "")
                    cur_hex = "#345beb"
                else:
                    top_mode = "literal"
                    cur_col = cat_cols[0]
                    cur_lmode = "palette"
                    cur_palette = _LIB_PALETTES[0]
                    cur_project_palette = next(iter(_project_palettes), "")
                    cur_hex = str(current_val or "#345beb")

                # Build source radio choices: "project" only when palettes are defined
                _lmode_choices = {"palette": "Palette library"}
                if _has_project_palettes:
                    _lmode_choices["project"] = "Project palette"
                _lmode_choices["custom"] = "Custom hex"

                # Project palette selector (inside literal mode conditional)
                if _has_project_palettes:
                    _project_palette_names = list(_project_palettes.keys())
                    _project_palette_widget = ui.panel_conditional(
                        f"input['{lit_mode_id}'] === 'project'",
                        ui.input_select(
                            project_palette_id, "Project palette",
                            choices={p: p for p in _project_palette_names},
                            selected=(cur_project_palette
                                      if cur_project_palette in _project_palettes
                                      else _project_palette_names[0])
                        )
                    )
                else:
                    # No project palettes — placeholder slot kept for layout stability
                    _project_palette_widget = ui.span("")

                elem = ui.div(
                    ui.p(label, class_="fw-bold small mb-1"),
                    # Top-level: column mapping vs literal
                    ui.input_radio_buttons(
                        mode_id, None,
                        choices={"column": "Map to column",
                                 "literal": "Set literal"},
                        selected=top_mode, inline=True
                    ),
                    # Column mode
                    ui.panel_conditional(
                        f"input['{mode_id}'] === 'column'",
                        ui.input_selectize(
                            col_id, "Column (categorical)",
                            choices=cat_cols, selected=cur_col
                        )
                    ),
                    # Literal mode
                    ui.panel_conditional(
                        f"input['{mode_id}'] === 'literal'",
                        ui.div(
                            ui.input_radio_buttons(
                                lit_mode_id, "Source",
                                choices=_lmode_choices,
                                selected=cur_lmode, inline=True
                            ),
                            _project_palette_widget,
                            ui.panel_conditional(
                                f"input['{lit_mode_id}'] === 'palette'",
                                ui.input_select(
                                    palette_id, "Palette",
                                    choices={p: p for p in _LIB_PALETTES},
                                    selected=cur_palette
                                )
                            ),
                            ui.panel_conditional(
                                f"input['{lit_mode_id}'] === 'custom'",
                                ui.input_text(
                                    hex_id, "Hex color",
                                    value=cur_hex,
                                    placeholder="#345beb"
                                )
                            ),
                        )
                    ),
                )

            else:  # "string" default
                elem = ui.input_text(
                    input_id, label,
                    value=str(current_val or ""),
                    placeholder=param_def.get("placeholder", "")
                )

            widgets.append(ui.div(elem, hint_el, class_="mb-2"))

        return widgets

    def apply_logic(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Applies the current logic stack to a LazyFrame."""
        nodes = self.logic_stack.get()
        for node in nodes:
            action_name = node['action']
            params = node['params']
            func = AVAILABLE_WRANGLING_ACTIONS.get(action_name)
            if func:
                try:
                    lf = func(lf, params)
                except Exception as e:
                    print(f"Error applying {action_name}: {e}")
        return lf
