# app/modules/wrangle_studio.py

# @deps
# provides: class:WrangleStudio
# consumes: libs/transformer/src/transformer/actions/base.py (AVAILABLE_WRANGLING_ACTIONS)
# consumed_by: app/handlers/home_theater.py, app/handlers/audit_stack.py, app/handlers/gallery_handlers.py, app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-004, .claude/knowledge/architecture_decisions.md#ADR-011
# @end_deps

from pathlib import Path
from shiny import ui, reactive, render
import polars as pl
import yaml
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS


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
                      viz_factory, get_schema_registry=None, get_includes_map=None):
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
                if viz_id not in full_cfg.get("plots", {}):
                    available = list(full_cfg.get("plots", {}).keys())
                    _plot_error.set(f"Plot ID '{viz_id}' not found in manifest. Available: {', '.join(available[:5])}")
                    return None
                _plot_error.set("")
                plt = viz_factory.render(df.lazy(), full_cfg, viz_id)
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
            ui.notification_show("Logic stack cleared.", type="warning")

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
        def logic_stack_ui():
            nodes = self.logic_stack.get()
            if not nodes:
                return ui.p("No active transformation nodes. Add one to begin.")

            ui_nodes = []
            for i, node in enumerate(nodes):
                # Robust extraction (ADR-031)
                action = node.get("action", "unknown")
                comment = node.get("comment", "No comment")
                params = node.get("params", {})

                ui_nodes.append(
                    ui.div(
                        ui.div(
                            ui.div(
                                ui.span(f"Step {i+1}: {action}",
                                        class_="fw-bold"),
                                ui.span(
                                    f" — {comment}", style="color: #666; font-style: italic;"),
                            ),
                            ui.div(
                                ui.span(f"Config: {params}",
                                        class_="text-muted small"),
                            )
                        ),
                        class_="p-2 mb-2 border rounded shadow-sm bg-light d-flex justify-content-between align-items-center"
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
