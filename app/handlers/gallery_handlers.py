"""app/handlers/gallery_handlers.py
Gallery Shiny wiring (ADR-037 / ADR-045, Phase 22-F).

Entry point:
    define_server(input, output, session, *,
                  bootloader, safe_input,
                  current_persona=None, home_state=None)

Concern: Gallery filtering, preview rendering, recipe clone, gallery_browser_anchor.
         Clone transplants a developer_raw_yaml RecipeNode into home_state._pending_t3_nodes
         (§12e). Gated on t3_sandbox_enabled.
Two-Category Law (ADR-045): This file contains @render.* and @reactive.* decorators
only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (gallery_handlers)
# consumes: app/src/bootloader.py, libs/transformer/src/transformer/data_wrangler.py (removed — clone now builds RecipeNode directly)
# consumed_by: app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-037, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/rules/ui_implementation_contract.md#12e
# @end_deps

import base64
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import polars as pl
import yaml
from shiny import reactive, render, ui


def define_server(input, output, session, *,
                  bootloader, safe_input,
                  current_persona=None, home_state=None):
    """Register all Gallery reactive handlers.

    Parameters
    ----------
    bootloader : Bootloader
        Path Authority instance (ADR-031).
    safe_input : callable
        Shared utility: safe_input(input_obj, key, default) → value.
    current_persona : reactive.Value[str] | None
        Active persona — used to gate "Send to T3" (§12e).
    home_state : reactive.Value[dict] | None
        §13 Home Module State Object — receives transplanted RecipeNodes.
    """

    # --- 🔬 Gallery Taxonomy 'Select All' Logic ---

    def _pivot_choices(key: str, fallback: list[str]) -> list[str]:
        """Read sorted choices for a pivot axis from gallery_index.json."""
        index_path = bootloader.get_location("gallery") / "gallery_index.json"
        if index_path.exists():
            try:
                with open(index_path) as f:
                    pivot = json.load(f).get("pivot", {})
                choices = sorted(pivot.get(key, {}).keys())
                if choices:
                    return choices
            except Exception:
                pass
        return fallback

    _diff_order = {"Simple": 0, "Intermediate": 1, "Advanced": 2}
    _ss_order   = {"any": 0, "individual points": 1, "medium+": 2, "large": 3}
    _fb_family  = ["Comparison", "Correlation", "Distribution",
                   "Evolution", "Part-to-Whole", "Ranking"]
    _fb_pattern = ["1 Numeric", "1 Numeric, 1 Categorical",
                   "1 Numeric, 2 Categorical", "1 Numeric, 2 Categorical (Faceted)",
                   "2 Numeric", "2 Numeric, 1 Categorical (Faceted)", "Numeric-Numeric"]
    _fb_diff    = ["Simple", "Intermediate", "Advanced"]
    _fb_geom    = ["geom_area", "geom_bar", "geom_bin_2d", "geom_boxplot",
                   "geom_col", "geom_density", "geom_freqpoly", "geom_histogram",
                   "geom_jitter", "geom_line", "geom_path", "geom_point",
                   "geom_pointrange", "geom_qq", "geom_segment", "geom_sina",
                   "geom_step", "geom_tile", "geom_violin", "stat_ecdf"]
    _fb_show    = ["change", "distribution", "frequency", "normality",
                   "proportion", "ranking", "relationship", "trend", "uncertainty"]
    _fb_ss      = ["any", "individual points", "medium+", "large"]

    @reactive.Effect
    def _sync_family_all():
        v = input.gallery_all_family()
        if v is None:
            return
        choices = _pivot_choices("by_family", _fb_family)
        ui.update_checkbox_group("gallery_filter_family", selected=choices if v else [])

    @reactive.Effect
    def _sync_pattern_all():
        v = input.gallery_all_pattern()
        if v is None:
            return
        choices = _pivot_choices("by_pattern", _fb_pattern)
        ui.update_checkbox_group("gallery_filter_pattern", selected=choices if v else [])

    @reactive.Effect
    def _sync_difficulty_all():
        v = input.gallery_all_difficulty()
        if v is None:
            return
        choices = sorted(
            _pivot_choices("by_difficulty", _fb_diff),
            key=lambda x: _diff_order.get(x, 99),
        )
        ui.update_checkbox_group("gallery_filter_difficulty", selected=choices if v else [])

    @reactive.Effect
    def _sync_geom_all():
        v = input.gallery_all_geom()
        if v is None:
            return
        choices = _pivot_choices("by_geom", _fb_geom)
        ui.update_checkbox_group("gallery_filter_geom", selected=choices if v else [])

    @reactive.Effect
    def _sync_show_all():
        v = input.gallery_all_show()
        if v is None:
            return
        choices = _pivot_choices("by_show", _fb_show)
        ui.update_checkbox_group("gallery_filter_show", selected=choices if v else [])

    @reactive.Effect
    def _sync_sample_size_all():
        v = input.gallery_all_sample_size()
        if v is None:
            return
        choices = sorted(
            _pivot_choices("by_sample_size", _fb_ss),
            key=lambda x: _ss_order.get(x, 99),
        )
        ui.update_checkbox_group("gallery_filter_sample_size", selected=choices if v else [])

    # --- Gallery Initialization (ADR-037) ---
    @reactive.Effect
    def _init_gallery_selector():
        """Ensure all plots are selected by default on startup."""
        index_path = bootloader.get_location("gallery") / "gallery_index.json"
        if index_path.exists():
            with open(index_path, "r") as f:
                idx = json.load(f)
            registry = idx.get("registry", {})
            choices = {rid: entry["name"] for rid, entry in registry.items()}
            choices = dict(sorted(choices.items(), key=lambda item: item[1]))
            ui.update_select("gallery_recipe_select", choices=choices)

    @reactive.Effect
    @reactive.event(input.btn_clone_gallery)
    def handle_gallery_clone():
        # Gate: only personas with T3 sandbox can receive transplants (§12e).
        if not bootloader.is_enabled("t3_sandbox_enabled"):
            ui.notification_show(
                "Send to T3 is not available for this persona.",
                type="warning", duration=5,
            )
            return

        if home_state is None:
            return

        recipe_id = safe_input(input, "gallery_recipe_select", None)
        if not recipe_id:
            return

        index_path = bootloader.get_location("gallery") / "gallery_index.json"
        if not index_path.exists():
            return

        try:
            with open(index_path, "r") as f:
                idx = json.load(f)

            recipe_entry = idx["registry"].get(recipe_id)
            if not recipe_entry:
                return

            file_path = recipe_entry["path"]
            with open(file_path, "r") as f:
                raw_yaml = f.read()
                manifest = yaml.safe_load(raw_yaml)

            # Extract the wrangling block as the YAML fragment for T3.
            wrangling_raw = manifest.get("wrangling", {})
            yaml_fragment = yaml.dump(
                {"wrangling": wrangling_raw}, default_flow_style=False, allow_unicode=True,
            )
            gallery_yaml_hash = hashlib.sha256(raw_yaml.encode()).hexdigest()[:16]

            # Build a developer_raw_yaml RecipeNode (§12b / §12e).
            node: dict = {
                "node_type": "developer_raw_yaml",
                "id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"),
                "plot_scope": "__all__",
                "plot_scopes_intent": ["__all_at_apply__"],
                "params": {"yaml_fragment": yaml_fragment},
                "reason": "",  # empty — blocks btn_apply until user fills it in
                "gallery_source": {
                    "gallery_id": recipe_id,
                    "gallery_yaml_hash": gallery_yaml_hash,
                },
            }

            # Append to pending nodes in home_state (§12g.7).
            cur = home_state.get()
            pending = list(cur.get("_pending_t3_nodes", []))
            pending.append(node)
            home_state.set({**cur, "_pending_t3_nodes": pending})

            ui.notification_show(
                f"Recipe '{recipe_id}' sent to T3 sandbox. "
                "Add a reason in the Audit panel, then press Apply.",
                type="message", duration=8,
            )
        except Exception as e:
            ui.notification_show(f"Clone failed: {e}", type="error", duration=10)

    # --- Gallery Content Resolution (ADR-037) ---
    @reactive.Calc
    def _gallery_active_metadata():
        rid = safe_input(input, "gallery_recipe_select", None)
        if not rid:
            return None
        index_path = bootloader.get_location("gallery") / "gallery_index.json"
        if not index_path.exists():
            return None
        with open(index_path, "r") as f:
            idx = json.load(f)
        return idx["registry"].get(rid)

    @output
    @render.ui
    def gallery_preview_img():
        meta = _gallery_active_metadata()
        if not meta:
            return ui.div("Select a recipe to view preview.", class_="p-5 text-muted")

        path_str = meta.get("path")
        if not path_str:
            return ui.div("Path missing in index.", class_="text-danger")

        img_path = Path(path_str).parent / "preview_plot.png"
        if img_path.exists():
            try:
                with open(img_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                return ui.div(
                    ui.img(src=f"data:image/png;base64,{encoded}",
                           style="max-width: 100%; border: 1px solid #dee2e6; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"),
                    class_="p-3 text-center"
                )
            except Exception as e:
                return ui.div(f"Error loading preview: {e}", class_="text-danger")
        return ui.div("No preview image found (.png)", class_="p-5 text-muted")

    @output
    @render.table(index=False)
    def gallery_static_data():
        """Render a clean, left-aligned table without row numbers (ADR-033)."""
        meta = _gallery_active_metadata()
        if not meta:
            return None
        path_str = meta.get("path")
        if not path_str:
            return None

        data_path = Path(path_str).parent / "example_data.tsv"
        if data_path.exists():
            try:
                # Polars maintains high-density left alignment by default in Shiny's render.table
                return pl.read_csv(data_path, separator="\t")
            except Exception as e:
                # Fallback to an empty DF with error message for debugging
                return pl.DataFrame({"Error": [f"Could not load data: {e}"]})
        return None

    @output
    @render.text
    def gallery_yaml_preview():
        meta = _gallery_active_metadata()
        if not meta:
            return "Select a recipe"
        path_str = meta.get("path")
        if not path_str:
            return "Manifest path not found"

        if Path(path_str).exists():
            with open(path_str, "r") as f:
                return f.read()
        return "Source YAML not found"

    @output
    @render.ui
    def gallery_md_content():
        meta = _gallery_active_metadata()
        if not meta:
            return ui.div("Select an entry to view guidance.", class_="p-4 text-center text-muted")

        path_str = meta.get("path")
        if not path_str:
            return ui.div("Metadata path not found", class_="text-danger")

        md_path = Path(path_str).parent / "recipe_meta.md"
        if md_path.exists():
            with open(md_path, "r") as f:
                return ui.div(ui.markdown(f.read()), class_="gallery-guidance-styled")
        return ui.div("Educational metadata (recipe_meta.md) missing.", class_="alert alert-warning")

    @reactive.Effect
    @reactive.event(input.btn_apply_gallery_filters, input.sidebar_nav)
    def _update_gallery_options():
        """
        High-Performance Filtering Gate (ADR-037).
        TRIGGERED BY: 'Apply' button OR Tab switch to Gallery.
        """
        # 1. Check if we are actually in the Gallery (don't recalc if switching away)
        if input.sidebar_nav() != "Gallery":
            return
        index_path = bootloader.get_location("gallery") / "gallery_index.json"
        if not index_path.exists():
            ui.notification_show("Indexer not found.", type="error")
            return

        with open(index_path, "r") as f:
            idx = json.load(f)

        # 2. Collect Filter Inputs
        sel_families    = input.gallery_filter_family()
        sel_patterns    = input.gallery_filter_pattern()
        sel_difficulties = input.gallery_filter_difficulty()
        sel_geoms       = safe_input(input, "gallery_filter_geom", [])
        sel_shows       = safe_input(input, "gallery_filter_show", [])
        sel_ss          = safe_input(input, "gallery_filter_sample_size", [])

        ui.notification_show("🔍 Filtering recipes...",
                             duration=1, type="message")

        # 3. Pivot-Set Intersection across all 6 axes
        registry = idx["registry"]
        pivot = idx["pivot"]

        def _pivot_set(axis: str, selections) -> set:
            """Union of recipe IDs matching any selected value on an axis.
            If nothing selected OR axis absent, return full registry (no filter)."""
            if not selections:
                return set(registry.keys())
            matched = set()
            for val in selections:
                matched.update(pivot.get(axis, {}).get(val, []))
            return matched

        family_matches     = _pivot_set("by_family",      sel_families)
        pattern_matches    = _pivot_set("by_pattern",     sel_patterns)
        difficulty_matches = _pivot_set("by_difficulty",  sel_difficulties)
        geom_matches       = _pivot_set("by_geom",        sel_geoms)
        show_matches       = _pivot_set("by_show",        sel_shows)
        ss_matches         = _pivot_set("by_sample_size", sel_ss)

        # Perform the final Multi-Set Intersection
        valid_ids = (family_matches & pattern_matches & difficulty_matches
                     & geom_matches & show_matches & ss_matches)

        # 3. Build UI Choices
        choices = {vid: registry[vid]["name"] for vid in valid_ids}
        choices = dict(sorted(choices.items(), key=lambda item: item[1]))

        # 4. Push Update to UI
        ui.update_select("gallery_recipe_select",
                         label=ui.span(
                             f"Visual Gallery ({len(choices)} matched)", style="font-weight:700;color:#345beb;"),
                         choices=choices,
                         selected=None)

        if not choices:
            ui.notification_show(
                "⚠️ No matches found for these filters.", type="warning")

    @output
    @render.ui
    def gallery_browser_anchor():
        """Placeholder for any additional anchor logic if needed."""
        return None
