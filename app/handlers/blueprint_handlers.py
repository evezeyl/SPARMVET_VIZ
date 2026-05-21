"""app/handlers/blueprint_handlers.py
Blueprint Architect Shiny wiring (ADR-039 / ADR-045).

Entry point:
    define_server(input, output, session, *,
                  bootloader, wrangle_studio, orchestrator, safe_input,
                  includes_map, component_ctx_map, schema_registry)

Concern: manifest import, TubeMap sync, Lineage Rail, upload/save/download,
         dataset pipeline selector, normalize fields, sync_blueprint_mapper.
Two-Category Law (ADR-045): This file contains @render.* and @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (blueprint_handlers), output:blueprint_agent_panel_ui, output:bp_fork_ui, output:bp_fork_preview_ui, output:bp_groups_inventory_ui, effect:_bp_apply_node_handler, effect:_bp_save_yaml_hatch, effect:_load_component_from_selection, effect:_handle_fork_preview, effect:_handle_fork_write
# provides: effects:_handle_grp_action/_handle_create_group_btn/_handle_grp_submit/_handle_plt_submit/_handle_move_plt_submit (BP-GROUPS-1)
# provides: helper:_do_refresh_blueprint (BP-GROUPS-1 — extracts manifest rebuild logic so CRUD Effects can call it after mutations)
# provides: output:bp_meta_form_ui, effect:_handle_meta_save (BP-META-1 — manifest info: block read/edit form)
# provides: effects:_handle_new_manifest_btn/_handle_new_manifest_submit (BP-NEW-1 — create manifest from scratch)
# consumes: libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py, libs/blueprint_arch/src/blueprint_arch/agent_adapter.py, libs/blueprint_arch/src/blueprint_arch/agent_context.py, libs/blueprint_arch/src/blueprint_arch/agent_tools.py, libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py, app/modules/orchestrator.py, libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py, libs/utils/src/utils/config_loader.py
# consumes: function:generate_fork_yaml (libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py — BP-VISUAL-FORK-1)
# consumes: libs/blueprint_arch/src/blueprint_arch/schema_registry.py (get_action_catalog — BP-FORMS-1; get_component_catalog — BP-COMPONENT-FORMS-1; __mapping__ aes form inputs bp_map_* — BP-MAPPING-FORM-1)
# consumes: function:normalise_plot_spec, function:serialise_plot_spec (libs/viz_factory/src/viz_factory/plot_config_resolver.py — BP-PLOT-LOAD-1 + BP-PLOT-COMMIT-1)
# consumes: libs/blueprint_arch/src/blueprint_arch/join_designer.py (compute_key_match, build_join_step, parse_join_step — BP-JOINT-1 Joint Designer pane)
# consumes: libs/blueprint_arch/src/blueprint_arch/group_plot_manager.py (list_groups_plots, create_group, delete_group, create_plot, delete_plot, assign_plot — BP-GROUPS-1)
# provides: outputs:joint_designer_status_ui/joint_left_schema_ui/joint_right_schema_ui/joint_key_pickers_ui/joint_preview_ui, effects:_jd_run_preview/_jd_apply/_jd_load_for_edit (BP-JOINT-1)
# provides: function:_serialise_component_for_save (BP-PLOT-COMMIT-1 — plot_spec/wrangling commit), helper:_bundle_filename (full-manifest zip)
# consumes: reactive.Value:active_component_path (WrangleStudio — BP-PLOT-COMMIT-1; Save target file); node marker _tier (source-tier routing on commit)
# note: Apply handler supports multi-select enum (BP-ENUM-PREVIEW-1 — multi:true for date_extract.parts)
# consumes: libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-BLUEPRINT-1)
# consumes: reactive.Value:selected_lineage_rel (passed from server.py — BP-LINEAGE-NAV-1; _load_component_from_selection watches it)
# consumed_by: app/src/server.py, app/handlers/home_theater.py (ui.output_ui("blueprint_agent_panel_ui"), ui.output_ui("bp_fork_ui"), ui.output_ui("bp_groups_inventory_ui"), ui.output_ui("bp_meta_form_ui"))
# doc: .claude/knowledge/architecture_decisions.md#ADR-039, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-075, .claude/knowledge/architecture_decisions.md#ADR-076, .claude/knowledge/architecture_decisions.md#ADR-082
# @end_deps

import asyncio
import io
import json
import re
import uuid
import zipfile
from collections import deque
from datetime import datetime
from pathlib import Path

import polars as pl
import yaml
from shiny import reactive, render, ui

from blueprint_arch.manifest_navigator import (
    build_lineage_chain,
    build_schema_registry,
    build_sibling_map,
    generate_fork_yaml,
    load_fields_file,
    resolve_fields_for_schema,
)
from blueprint_arch.blueprint_mapper import BlueprintMapper
from blueprint_arch.join_designer import (
    compute_key_match, build_join_step, parse_join_step, JOIN_HOW_OPTIONS,
)
from blueprint_arch.group_plot_manager import (
    list_groups_plots, create_group, delete_group,
    create_plot, delete_plot, assign_plot,
    _IncludeTag, _IncludeLoader, _IncludeDumper,
)
from viz_factory.plot_config_resolver import normalise_plot_spec, serialise_plot_spec
from blueprint_arch.agent_context import build_system_prompt
from blueprint_arch.agent_tools import call_tool, get_tool_definitions
from blueprint_arch.agent_tool_parser import extract_tool_calls
from utils.config_loader import ConfigManager
from utils.pipeline_error import PipelineError


def define_server(input, output, session, *,
                  bootloader, wrangle_studio, orchestrator, safe_input,
                  includes_map, component_ctx_map, schema_registry,
                  selected_lineage_rel=None,
                  active_cfg=None):
    """Register all Blueprint Architect reactive handlers.

    Parameters
    ----------
    bootloader : Bootloader
        Path Authority (ADR-031).
    wrangle_studio : WrangleStudio
        Shared WrangleStudio state (logic_stack, active_* reactive values).
    orchestrator : DataOrchestrator
        Used for surgical Parquet materialization.
    safe_input : callable
        Shared utility: safe_input(input_obj, key, default) → value.
    includes_map : reactive.Value[dict]
        Per-session cache: rel_path → abs_path for all !include files.
        Declared in server() so wrangle_studio.define_server() can reference it.
    component_ctx_map : reactive.Value[dict]
        Per-session sibling map: rel_path → {role, schema_id, ...}.
    schema_registry : reactive.Value[dict]
        Per-session schema registry: schema_id → structural entry.
    selected_lineage_rel : reactive.Value[str | None]
        BP-LINEAGE-NAV-1: shared signal written by lineage rail clicks and btn_import_manifest.
        _load_component_from_selection watches it and calls _do_load_component() directly.
    """

    # BP-UNDO-1: 20-step session undo deque (ADR-082 placeholder)
    undo_stack: deque = deque(maxlen=20)

    # BP-GROUPS-1: group/plot CRUD local state
    _groups_refresh: reactive.Value = reactive.Value(0)   # bumped after every CRUD mutation
    _grp_modal_ctx: reactive.Value = reactive.Value({})   # transient context for open modals

    def _snapshot_state():
        """Capture current logic_stack state for undo history."""
        current = wrangle_studio.logic_stack.get()
        if current:
            undo_stack.append(json.dumps(current, default=str))

    def _undo():
        """Restore to previous state from undo stack."""
        if undo_stack:
            prev_state = undo_stack.pop()
            restored = json.loads(prev_state)
            wrangle_studio.logic_stack.set(restored)
            return True
        return False

    def _do_refresh_blueprint(path: str) -> tuple[dict, dict]:
        """Rebuild includes_map/ctx_map/schema_registry and bump _groups_refresh.

        Called on manifest load and after any group/plot CRUD mutation.
        Returns (ctx_map, inc_map) for callers that need the data directly.
        """
        if not path or not Path(path).exists():
            return {}, {}
        try:
            manifest_path = Path(path)
            manifest_dir = manifest_path.parent
            raw_text = manifest_path.read_text(encoding="utf-8")

            rel_paths = re.findall(r"!include\s+['\"]([^'\"]+)['\"]", raw_text)
            inc_map: dict = {}
            groups: dict = {}
            seen: set = set()

            for rel_path in rel_paths:
                if rel_path in seen:
                    continue
                seen.add(rel_path)
                abs_path = (manifest_dir / rel_path).resolve()
                if not abs_path.exists():
                    print(f"[Blueprint] Included file not found: {abs_path}")
                    continue
                inc_map[rel_path] = str(abs_path)

            includes_map.set(inc_map)
            ctx_map = build_sibling_map(path)
            component_ctx_map.set(ctx_map)
            schema_registry.set(build_schema_registry(path, inc_map))

            for rel_path in inc_map:
                abs_path = Path(inc_map[rel_path])
                ctx_entry = ctx_map.get(rel_path, {})
                if ctx_entry:
                    display = (f"{ctx_entry.get('schema_id', abs_path.stem)}"
                               f" — {ctx_entry.get('role', '?')}")
                else:
                    display = abs_path.name
                parts = Path(rel_path).parts
                subdir = parts[-2] if len(parts) >= 2 else "root"
                if subdir not in groups:
                    groups[subdir] = {}
                groups[subdir][rel_path] = display

            if groups:
                ui.update_select("dataset_pipeline_selector", choices=groups)
            else:
                cfg_inline = ConfigManager(path)
                raw = cfg_inline.raw_config
                inline_groups: dict = {}
                for sid in raw.get("data_schemas", {}):
                    inline_groups.setdefault("data_schemas", {})[sid] = f"{sid} — wrangling"
                for sid in raw.get("additional_datasets_schemas", {}):
                    inline_groups.setdefault(
                        "additional_datasets_schemas", {})[sid] = f"{sid} — wrangling"
                for sid in raw.get("join_manifests", {}):
                    inline_groups.setdefault("join_manifests", {})[sid] = f"{sid} — join"
                ag = raw.get("analysis_groups", {})
                for grp, gspec in ag.items():
                    if isinstance(gspec, dict):
                        for pid in gspec.get("plots", {}):
                            inline_groups.setdefault(
                                f"plots/{grp}", {})[pid] = f"{pid} — plot_spec"
                if inline_groups:
                    ui.update_select("dataset_pipeline_selector", choices=inline_groups)
                else:
                    ui.update_select("dataset_pipeline_selector",
                                     choices=["No components found"])

            with reactive.isolate():
                _groups_refresh.set(_groups_refresh.get() + 1)

            return ctx_map, inc_map

        except Exception as e:
            print(f"[_do_refresh_blueprint] Error: {e}")
            return {}, {}

    # ── Local helpers (pure logic, no Shiny decorators) ──────────────────────

    def _parse_logic_to_nodes(wrangling, source_name):
        """
        Normalizes potentially flat manifest nodes into structured UI nodes.
        ADR-031: Supports both Structure (params: {}) and Flat (top-level keys) formats.

        BP-PLOT-COMMIT-1: each node is tagged with its source tier (``_tier``) so the
        commit path can route it back to the same wrangling.tier{1,2} on Save. A bare
        list (legacy flat / recipe) defaults to tier1. Legacy tier3 nodes (artifacts of
        the pre-BP-PLOT-COMMIT-1 dump bug) are folded into tier2 — BLUEPRINT never
        authors T3 (ADR-082 §4).
        """
        nodes = []
        tagged: list = []  # (raw_node, tier_name)

        if isinstance(wrangling, list):
            tagged = [(n, "tier1") for n in wrangling]
        elif isinstance(wrangling, dict):
            for tier in ["tier1", "tier2", "tier3"]:
                dest = "tier2" if tier == "tier3" else tier
                tagged.extend((n, dest) for n in wrangling.get(tier, []))

        for node, tier_name in tagged:
            if not isinstance(node, dict):
                continue
            n = node.copy()
            action = n.pop("action", "unknown_action")
            comment = n.pop("comment", source_name)
            params = n.pop("params", n)
            nodes.append({
                "action": action, "params": params,
                "comment": comment, "_tier": tier_name,
            })

        return nodes

    def _serialise_component_for_save(role, nodes, raw_text):
        """Pure: serialise the live logic_stack back to the component file's dict shape.

        BP-PLOT-COMMIT-1 (ADR-083 §8). Routes by component role:
          - plot_spec     -> canonical {mapping, layers, ...} via serialise_plot_spec;
                             wrapped in {spec: ...} iff the source file used that wrapper.
                             Plot-level scalars / taxonomy (target_dataset, theme, palette,
                             family, ...) are recovered from the original file; mapping +
                             layers are taken from the live stack (authoritative).
          - wrangling /   -> {wrangling: {tier1: [...], tier2: [...]}} (or {recipe: ...}),
            plot_wrangling    action nodes routed to their source tier via the _tier marker.
                              T3 is never written (ADR-082 §4) — _parse_logic_to_nodes folded
                              any legacy tier3 into tier2 on load.

        Raises ValueError for roles that cannot be saved from the logic stack.
        """
        try:
            original = yaml.safe_load(raw_text) or {}
        except Exception:
            original = {}

        if role == "plot_spec":
            had_wrapper = (isinstance(original, dict)
                           and isinstance(original.get("spec"), dict))
            base = (original["spec"] if had_wrapper
                    else (original if isinstance(original, dict) else {}))
            canonical = normalise_plot_spec(base)

            # Live stack is authoritative for mapping + layers.
            mapping: dict = {}
            layers: list = []
            for node in nodes:
                comp = node.get("component")
                if comp is None:
                    continue  # ignore stray action nodes in a plot spec
                if comp == "__mapping__":
                    mapping = dict(node.get("params", {}))
                else:
                    layer = {"name": comp, "params": dict(node.get("params", {}))}
                    node_comment = node.get("comment", "")
                    if node_comment:
                        layer["comment"] = node_comment
                    layers.append(layer)
            canonical["mapping"] = mapping
            canonical["layers"] = layers

            spec_out = serialise_plot_spec(canonical)
            return {"spec": spec_out} if had_wrapper else spec_out

        if role in ("wrangling", "plot_wrangling"):
            # Preserve the original container key (wrangling vs recipe) for round-trip.
            container_key = "wrangling"
            if isinstance(original, dict) and "recipe" in original \
                    and "wrangling" not in original:
                container_key = "recipe"

            tiers: dict = {"tier1": [], "tier2": []}
            for node in nodes:
                if node.get("action") is None:
                    continue  # ignore stray component nodes
                tier = node.get("_tier", "tier1")
                if tier not in tiers:
                    tier = "tier1"
                step = {"action": node["action"]}
                step.update(node.get("params", {}))
                comment = node.get("comment", "")
                if comment:
                    step["comment"] = comment
                tiers[tier].append(step)

            block: dict = {"tier1": tiers["tier1"]}
            if tiers["tier2"]:
                block["tier2"] = tiers["tier2"]
            return {container_key: block}

        raise ValueError(
            f"Save is not supported for component role '{role}'. "
            "Editable roles: plot_spec, wrangling, plot_wrangling."
        )

    def _extract_wrangling_for_id(cfg, lid):
        """Helper to find wrangling block in complex manifest."""
        target = cfg.raw_config.get("data_schemas", {}).get(lid)
        if not target:
            target = cfg.raw_config.get("additional_datasets_schemas", {}).get(lid)
        if not target:
            target = cfg.raw_config.get("join_manifests", {}).get(lid)
        if not target and lid == "metadata_schema":
            target = cfg.raw_config.get("metadata_schema")
        if not target:
            return {}
        return target.get("wrangling", target.get("recipe", {}))

    def _do_load_component(master_path: str, selected: str,
                           inc_map: dict, ctx_map: dict):
        """
        Core import logic — shared by btn_import_manifest and TubeMap click.

        Mode A: `selected` is a rel_path that exists in inc_map → load the file.
        Mode B: `selected` is an inline schema_id → read directly from raw_config.
        """
        if not master_path or not selected:
            return
        if selected in inc_map:
            abs_file = Path(inc_map[selected])
            target_ds = None
            try:
                raw_text = abs_file.read_text(encoding="utf-8")
                try:
                    file_content = yaml.safe_load(raw_text) or {}
                except Exception:
                    file_content = {}

                if isinstance(file_content, list):
                    wrangling = file_content
                elif isinstance(file_content, dict):
                    wrangling = file_content.get(
                        "wrangling",
                        file_content.get("recipe", file_content.get("tier1", []))
                    )
                else:
                    wrangling = []

                nodes = _parse_logic_to_nodes(wrangling, abs_file.name)
                wrangle_studio.logic_stack.set(nodes)
                wrangle_studio.active_raw_yaml.set(raw_text)
                # BP-PLOT-COMMIT-1: remember the loaded fragment file so Save writes here.
                wrangle_studio.active_component_path.set(str(abs_file))

                ctx = component_ctx_map.get().get(selected, {})
                role = ctx.get("role", "unknown")
                sib = ctx.get("siblings", {})
                schema_id = ctx.get("schema_id", "")
                schema_type = ctx.get("schema_type", "")
                ingredients = ctx.get("ingredients", [])

                wrangle_studio.active_component_info.set({
                    "role": role,
                    "schema_id": schema_id,
                    "schema_type": schema_type,
                    "ingredients": ingredients,
                    "wrangling": sib.get("wrangling"),
                })

                if role == "input_fields":
                    in_fields = load_fields_file(abs_file)
                    out_fields = []
                    wrangle_studio.active_upstream.set([])
                    wrangle_studio.active_downstream.set(in_fields)

                elif role == "output_fields":
                    in_fields = []
                    out_fields = load_fields_file(abs_file)
                    wrangle_studio.active_upstream.set(out_fields)
                    wrangle_studio.active_downstream.set([])

                elif role == "wrangling":
                    inp_rel = sib.get("input_fields")
                    out_rel = sib.get("output_fields")
                    in_fields = load_fields_file(Path(inc_map[inp_rel])) \
                        if inp_rel and inp_rel in inc_map else []
                    out_fields = load_fields_file(Path(inc_map[out_rel])) \
                        if out_rel and out_rel in inc_map else []
                    wrangle_studio.active_upstream.set(in_fields)
                    wrangle_studio.active_downstream.set(out_fields)

                elif role == "join":
                    ctx_map_now = component_ctx_map.get()
                    id_to_out_rel = {}
                    for rel, entry in ctx_map_now.items():
                        if entry.get("role") == "output_fields":
                            sid = entry.get("schema_id", "")
                            if sid and sid not in id_to_out_rel:
                                id_to_out_rel[sid] = rel

                    ing_items = []
                    for ing_id in ingredients:
                        out_rel_for_ing = id_to_out_rel.get(ing_id)
                        ing_abs = inc_map.get(out_rel_for_ing) if out_rel_for_ing else None
                        if not ing_abs:
                            ing_entry = ctx_map_now.get(ing_id, {})
                            out_slot = ing_entry.get("siblings", {}).get("output_fields")
                            if isinstance(out_slot, dict) and "inline" in out_slot:
                                fields = list(out_slot["inline"].keys()) if isinstance(
                                    out_slot["inline"], dict) else []
                                ing_items.append({"id": ing_id, "fields": fields})
                                continue
                        fields = load_fields_file(Path(ing_abs)) if ing_abs else []
                        ing_items.append({"id": ing_id, "fields": fields})

                    out_rel = sib.get("output_fields")
                    out_fields = load_fields_file(Path(inc_map[out_rel])) \
                        if isinstance(out_rel, str) and out_rel in inc_map else []
                    if not out_fields and isinstance(out_rel, dict) and "inline" in out_rel:
                        out_fields = list(out_rel["inline"].keys()) if isinstance(
                            out_rel["inline"], dict) else []
                    in_fields = []
                    wrangle_studio.active_upstream.set(ing_items)
                    wrangle_studio.active_downstream.set(out_fields)

                    try:
                        anchor_dir = bootloader.get_location("user_sessions") / "anchors"
                        anchor_dir.mkdir(parents=True, exist_ok=True)
                        out_p = anchor_dir / f"{schema_id}.parquet"
                        bp_project_id = Path(master_path).stem
                        print(f"[Architect] Materializing join '{schema_id}'")
                        orchestrator.materialize_tier1(
                            project_id=bp_project_id,
                            collection_id=schema_id,
                            output_path=out_p
                        )
                        wrangle_studio.active_anchor_path.set(str(out_p))
                    except Exception as e:
                        print(f"[Architect] Join materialization failed: {e}")

                elif role == "plot_spec":
                    target_ds = file_content.get("target_dataset") \
                        if isinstance(file_content, dict) else None

                    ctx_map_now = component_ctx_map.get()
                    upstream_fields: list = []
                    if target_ds:
                        resolved = resolve_fields_for_schema(target_ds, ctx_map_now, inc_map)
                        if resolved:
                            upstream_fields = resolved

                    in_fields = []
                    out_fields = []
                    wrangle_studio.active_upstream.set(upstream_fields)
                    wrangle_studio.active_downstream.set([])
                    wrangle_studio.active_viz_id.set(schema_id)

                    # Populate logic_stack with plot spec nodes (read-only; BP-PLOT-LOAD-1)
                    # BP-PLOT-COMMIT-1 handles writing back. component nodes use {"component":...}
                    if isinstance(file_content, dict):
                        canonical = normalise_plot_spec(file_content)
                        plot_nodes: list = []
                        mapping = canonical.get("mapping", {})
                        if mapping:
                            plot_nodes.append(
                                {"component": "__mapping__", "params": mapping, "comment": ""}
                            )
                        for layer in canonical.get("layers", []):
                            plot_nodes.append({
                                "component": layer.get("name", ""),
                                "params": layer.get("params", {}),
                                "comment": "",
                            })
                        wrangle_studio.logic_stack.set(plot_nodes)
                    else:
                        wrangle_studio.logic_stack.set([])

                    if target_ds:
                        try:
                            anchor_dir = bootloader.get_location("user_sessions") / "anchors"
                            anchor_dir.mkdir(parents=True, exist_ok=True)
                            out_p = anchor_dir / f"{target_ds}.parquet"
                            bp_project_id = Path(master_path).stem
                            print(f"[Architect] Materializing '{target_ds}' from '{bp_project_id}'")
                            orchestrator.materialize_tier1(
                                project_id=bp_project_id,
                                collection_id=target_ds,
                                output_path=out_p
                            )
                            wrangle_studio.active_anchor_path.set(str(out_p))
                        except Exception as e:
                            print(f"[Architect] Surgical materialization failed: {e}")

                elif role == "plot_wrangling":
                    target_ds = file_content.get("target_dataset") \
                        if isinstance(file_content, dict) else None

                    ctx_map_now = component_ctx_map.get()
                    upstream_fields: list = []
                    if target_ds:
                        resolved = resolve_fields_for_schema(target_ds, ctx_map_now, inc_map)
                        if resolved:
                            upstream_fields = resolved

                    if target_ds:
                        try:
                            anchor_dir = bootloader.get_location("user_sessions") / "anchors"
                            anchor_dir.mkdir(parents=True, exist_ok=True)
                            out_p = anchor_dir / f"{target_ds}.parquet"
                            bp_project_id = Path(master_path).stem
                            orchestrator.materialize_tier1(
                                project_id=bp_project_id,
                                collection_id=target_ds,
                                output_path=out_p
                            )
                            wrangle_studio.active_anchor_path.set(str(out_p))
                        except Exception as e:
                            print(f"[Architect] plot_wrangling materialization failed: {e}")

                    if isinstance(file_content, list):
                        wrangling = file_content
                    elif isinstance(file_content, dict):
                        wrangling = file_content.get(
                            "wrangling",
                            file_content.get("recipe", file_content.get("tier1", [])))
                    else:
                        wrangling = []
                    nodes = _parse_logic_to_nodes(wrangling, abs_file.name)
                    wrangle_studio.logic_stack.set(nodes)

                    in_fields = []
                    out_fields = []
                    wrangle_studio.active_upstream.set(upstream_fields)
                    wrangle_studio.active_downstream.set([])

                else:
                    in_fields = file_content.get("input_fields", []) \
                        if isinstance(file_content, dict) else []
                    out_fields = file_content.get("output_fields", []) \
                        if isinstance(file_content, dict) else []
                    wrangle_studio.active_upstream.set(in_fields)
                    wrangle_studio.active_downstream.set(out_fields)

                wrangle_studio.active_fields.set({"input": in_fields, "output": out_fields})

                chain = build_lineage_chain(
                    selected, component_ctx_map.get(), target_ds_override=target_ds)
                wrangle_studio.active_lineage_chain.set(chain)
                wrangle_studio.active_manifest_path.set(master_path)

                try:
                    cfg_for_map = ConfigManager(master_path)
                    mapper = BlueprintMapper(cfg_for_map.raw_config, active_node=schema_id)
                    wrangle_studio.active_tubemap_mermaid.set(mapper.generate_cy_elements())
                except Exception as _e:
                    print(f"[TubeMap highlight] Failed: {_e}")

                msg = f"✅ Loaded '{abs_file.name}' ({len(nodes)} step(s))"
                ui.notification_show(msg, type="message")
            except Exception as e:
                pe = PipelineError(
                    component="BlueprintHandlers",
                    problem=f"Failed to load component file: {type(e).__name__}: {e}",
                    location="_load_component_from_selection()",
                    fix="Check that the selected manifest component file exists and contains valid YAML. Verify the !include path resolves correctly from the manifest root.",
                    who="manifest_author",
                    category="blueprint_edit",
                    surface="blueprint_inline",
                    severity="error",
                    evidence={"error_type": type(e).__name__, "error_detail": str(e)[:200]},
                )
                print(pe.format())
                ui.notification_show(f"❌ Failed to load file: {e}", type="error")
            return

        # --- Mode B: fallback — treat selected as component ID via ConfigManager ---
        if not Path(master_path).exists():
            return
        try:
            cfg = ConfigManager(master_path)
            raw = cfg.raw_config

            schema_id = selected
            target = (raw.get("data_schemas", {}).get(selected)
                      or raw.get("additional_datasets_schemas", {}).get(selected)
                      or raw.get("join_manifests", {}).get(selected))

            plot_target_ds = None
            for grp_spec in raw.get("analysis_groups", {}).values():
                if isinstance(grp_spec, dict):
                    plots = grp_spec.get("plots", {})
                    if selected in plots:
                        pspec = plots[selected]
                        if isinstance(pspec, dict):
                            spec_block = pspec.get("spec", {}) if isinstance(pspec.get("spec"), dict) else {}
                            plot_target_ds = (pspec.get("target_dataset")
                                              or spec_block.get("target_dataset"))
                        if target is None:
                            target = pspec
                        break
                    for _pid, pspec in plots.items():
                        if isinstance(pspec, dict) and pspec.get("pre_plot_wrangling") == selected:
                            spec_block = pspec.get("spec", {}) if isinstance(pspec.get("spec"), dict) else {}
                            plot_target_ds = (pspec.get("target_dataset")
                                              or spec_block.get("target_dataset"))
                            break

            wrangling = _extract_wrangling_for_id(cfg, selected)
            nodes = _parse_logic_to_nodes(wrangling, f"Master: {selected}")
            wrangle_studio.logic_stack.set(nodes)
            wrangle_studio.active_raw_yaml.set(
                yaml.dump(raw, default_flow_style=False, sort_keys=False))
            # BP-PLOT-COMMIT-1: inline component (no standalone file) — Save is disabled.
            wrangle_studio.active_component_path.set("")

            ctx_map_b = ctx_map or component_ctx_map.get()
            comp_entry = ctx_map_b.get(selected, {})
            role_b = comp_entry.get("role", "wrangling")
            ingredients_b = comp_entry.get("ingredients", [])

            in_f = target.get("input_fields", {}) if isinstance(target, dict) else {}
            out_f = target.get("output_fields", {}) if isinstance(target, dict) else {}

            if role_b == "join":
                ing_items_b = []
                for ing_id in ingredients_b:
                    ing_block = (raw.get("data_schemas", {}).get(ing_id)
                                 or raw.get("additional_datasets_schemas", {}).get(ing_id)
                                 or raw.get("join_manifests", {}).get(ing_id))
                    fields = ing_block.get("output_fields", {}) \
                        if isinstance(ing_block, dict) else {}
                    ing_items_b.append({"id": ing_id, "fields": fields})
                wrangle_studio.active_upstream.set(ing_items_b)
                wrangle_studio.active_downstream.set(out_f)
                wrangle_studio.active_fields.set({"input": {}, "output": out_f})
                try:
                    anchor_dir = bootloader.get_location("user_sessions") / "anchors"
                    anchor_dir.mkdir(parents=True, exist_ok=True)
                    out_p = anchor_dir / f"{selected}.parquet"
                    bp_project_id = Path(master_path).stem
                    print(f"[Architect Mode B] Materializing join '{selected}'")
                    orchestrator.materialize_tier1(
                        project_id=bp_project_id,
                        collection_id=selected,
                        output_path=out_p
                    )
                    wrangle_studio.active_anchor_path.set(str(out_p))
                except Exception as e:
                    print(f"[Architect Mode B] Join materialization failed: {e}")
            elif role_b in ("plot_spec", "plot_wrangling"):
                upstream_b: dict = {}
                if plot_target_ds:
                    upstream_b = resolve_fields_for_schema(plot_target_ds, ctx_map_b, inc_map)
                if not upstream_b:
                    join_block = (raw.get("join_manifests") or {}).get(
                        plot_target_ds or selected)
                    if isinstance(join_block, dict):
                        upstream_b = join_block.get("output_fields", {}) or {}
                wrangle_studio.active_upstream.set(upstream_b)
                wrangle_studio.active_downstream.set([])
                wrangle_studio.active_fields.set({"input": upstream_b, "output": {}})
                wrangle_studio.active_viz_id.set(schema_id)
                if plot_target_ds:
                    try:
                        anchor_dir = bootloader.get_location("user_sessions") / "anchors"
                        anchor_dir.mkdir(parents=True, exist_ok=True)
                        out_p = anchor_dir / f"{plot_target_ds}.parquet"
                        bp_project_id = Path(master_path).stem
                        orchestrator.materialize_tier1(
                            project_id=bp_project_id,
                            collection_id=plot_target_ds,
                            output_path=out_p
                        )
                        wrangle_studio.active_anchor_path.set(str(out_p))
                    except Exception as _me:
                        print(f"[Architect Mode B] Plot materialization failed: {_me}")
            else:
                in_f_val = in_f if isinstance(in_f, (dict, list)) else []
                out_f_val = out_f if isinstance(out_f, (dict, list)) else []
                wrangle_studio.active_fields.set({"input": in_f_val, "output": out_f_val})
                wrangle_studio.active_upstream.set(in_f_val)
                wrangle_studio.active_downstream.set(out_f_val)
            wrangle_studio.active_manifest_path.set(master_path)

            wrangle_studio.active_component_info.set({
                "role": role_b,
                "schema_id": schema_id,
                "schema_type": comp_entry.get("schema_type", ""),
                "ingredients": ingredients_b,
                "wrangling": bool(wrangling),
            })

            chain = build_lineage_chain(
                selected, ctx_map_b, target_ds_override=plot_target_ds)
            wrangle_studio.active_lineage_chain.set(chain)

            try:
                mapper = BlueprintMapper(raw, active_node=schema_id)
                wrangle_studio.active_tubemap_mermaid.set(mapper.generate_cy_elements())
            except Exception as _e:
                print(f"[TubeMap highlight Mode B] Failed: {_e}")

            ui.notification_show(
                f"✅ Imported {len(nodes)} steps from '{selected}'", type="message")
        except Exception as e:
            pe = PipelineError(
                component="BlueprintHandlers",
                problem=f"Manifest import failed: {type(e).__name__}: {e}",
                location="_load_component_from_selection() Mode B",
                fix="Verify the manifest YAML is well-formed and all !include paths resolve. Check that the selected component ID exists in the manifest.",
                who="manifest_author",
                category="blueprint_edit",
                surface="blueprint_inline",
                severity="error",
                evidence={"error_type": type(e).__name__, "error_detail": str(e)[:200]},
            )
            print(pe.format())
            ui.notification_show(f"❌ Import failed: {e}", type="error")

    # ── Shiny reactive handlers ───────────────────────────────────────────────

    # --- Blueprint Architect Visual Sync (ADR-039) ---
    @reactive.Effect
    def sync_blueprint_mapper():
        """Syncs TubeMap from the Architect's own manifest selector."""
        if safe_input(input, "sidebar_nav", "Home") != "Wrangle Studio":
            return
        path_str = safe_input(input, "stored_manifest_selector", None)
        if not path_str:
            return
        if not Path(path_str).exists():
            return
        try:
            cfg = ConfigManager(str(path_str))
            info = wrangle_studio.active_component_info.get()
            active_node = info.get("schema_id") if info else None
            mapper = BlueprintMapper(cfg.raw_config, active_node=active_node)
            cy_json = mapper.generate_cy_elements()
            wrangle_studio.active_tubemap_mermaid.set(cy_json)
            wrangle_studio.active_raw_yaml.set(
                yaml.dump(cfg.raw_config, default_flow_style=False, allow_unicode=True)
            )
        except Exception as e:
            print(f"[sync_blueprint_mapper] Failed: {e}")

    # --- Phase 18: Wrangle Studio Manifest Management ---
    @reactive.Effect
    @reactive.event(input.sidebar_nav)
    def _init_wrangle_manifests():
        """Auto-discovery of Master manifests in config/ directory."""
        if input.sidebar_nav() != "Wrangle Studio":
            return

        config_dir = Path("config/manifests/pipelines")
        if not config_dir.exists():
            config_dir = Path("config")

        all_yamls = list(config_dir.glob("*.yaml"))
        master_manifests = [str(p) for p in all_yamls if p.is_file()]
        master_manifests.sort()
        ui.update_select("stored_manifest_selector",
                         choices=master_manifests,
                         selected=master_manifests[0] if master_manifests else None)

    @reactive.Effect
    @reactive.event(input.stored_manifest_selector)
    def _update_dataset_pipelines():
        """Discovers all actual !include files referenced by the manifest.
        Files are grouped by subdirectory type (wrangling/, plots/, input_fields/, ...).
        """
        path = input.stored_manifest_selector()
        if not path or not Path(path).exists():
            return
        ctx_map, inc_map = _do_refresh_blueprint(path)
        # UX-NOTIF-3: Project-load notification — surface component count on manifest reload
        manifest_name = Path(path).name
        n_components = len(ctx_map) if ctx_map else len(inc_map)
        ui.notification_show(
            f"Blueprint: {manifest_name} ({n_components} component(s))",
            type="message",
            duration=4,
        )

    @reactive.Effect
    @reactive.event(input.blueprint_node_clicked)
    def _sync_selector_from_node_click():
        """Handles a TubeMap node click end-to-end."""
        try:
            node_id = input.blueprint_node_clicked()
            if not node_id or str(node_id).startswith("INFO_"):
                return

            master_path = safe_input(input, "stored_manifest_selector", None)
            if not master_path or not Path(master_path).exists():
                ui.notification_show("⚠️ Select a Master Manifest first.", type="warning")
                return

            inc_map = includes_map.get()
            ctx_map = component_ctx_map.get()
            if not ctx_map:
                inc_map = {}
                raw_text = Path(master_path).read_text(encoding="utf-8")
                for rel in re.findall(r"!include\s+['\"]([^'\"]+)['\"]", raw_text):
                    abs_p = (Path(master_path).parent / rel).resolve()
                    if abs_p.exists():
                        inc_map[rel] = str(abs_p)
                includes_map.set(inc_map)
                ctx_map = build_sibling_map(master_path)
                component_ctx_map.set(ctx_map)

            _PRIORITY = {
                "join": 0, "wrangling": 1, "plot_spec": 2,
                "plot_wrangling": 3, "output_fields": 4, "input_fields": 5,
            }

            best_rel: str | None = None
            best_pri: int = 999
            for rel, entry in ctx_map.items():
                safe_sid = re.sub(r'[^A-Za-z0-9_]', '_', entry.get("schema_id", ""))
                if safe_sid != node_id:
                    continue
                pri = _PRIORITY.get(entry.get("role", ""), 99)
                if pri < best_pri:
                    best_pri = pri
                    best_rel = rel

            if not best_rel:
                best_rel = node_id

            ui.update_select("dataset_pipeline_selector", selected=best_rel)
            _do_load_component(master_path, best_rel, inc_map, ctx_map)

        except Exception as _e:
            print(f"[TubeMap click] Error: {_e}")
            ui.notification_show(f"⚠️ Could not load node: {_e}", type="warning")

    @reactive.Effect
    @reactive.event(input.btn_import_manifest)
    def _handle_manifest_import():
        """Write selected component to shared signal — _load_component_from_selection fires next.

        BP-LINEAGE-NAV-1: btn_import_manifest no longer calls _do_load_component() directly.
        Both this effect and handle_lineage_node_click (wrangle_studio.py) write to
        selected_lineage_rel; _load_component_from_selection is the single call site.
        """
        master_path = input.stored_manifest_selector()
        selected    = input.dataset_pipeline_selector()
        if not master_path or not selected or selected_lineage_rel is None:
            return
        selected_lineage_rel.set(selected)

    @reactive.Effect
    @reactive.event(selected_lineage_rel)
    def _load_component_from_selection():
        """Single call site for _do_load_component — watches the shared lineage signal.

        Fires when either btn_import_manifest or a lineage rail click writes a new rel path.
        Reads master_path directly from input (no race: selected_lineage_rel carries the
        chosen rel, bypassing the async ui.update_select lag).
        """
        if selected_lineage_rel is None:
            return
        rel = selected_lineage_rel.get()
        if not rel:
            return
        master_path = safe_input(input, "stored_manifest_selector", None)
        if not master_path:
            return
        _do_load_component(
            master_path, rel,
            inc_map=includes_map.get(),
            ctx_map=component_ctx_map.get(),
        )

    @reactive.Effect
    @reactive.event(input.btn_normalize_fields)
    def _handle_normalize_fields():
        """Normalize legacy {column: type} input_fields/output_fields in the active file."""
        from app.assets.normalize_manifest_fields import normalize_file as _normalize_file

        selected = safe_input(input, "dataset_pipeline_selector", None)
        inc_map = includes_map.get()

        if not selected or selected not in inc_map:
            ui.notification_show(
                "⚠️ No component file loaded. Import a blueprint component first.",
                type="warning"
            )
            return

        abs_path = Path(inc_map[selected])
        changes, success, message = _normalize_file(abs_path, write=True)

        if not success:
            ui.notification_show(f"❌ Normalize failed: {message}", type="error")
            return

        if not changes:
            ui.notification_show(f"ℹ️ {message}", type="message")
            return

        try:
            raw_text = abs_path.read_text(encoding="utf-8")
            file_content = yaml.safe_load(raw_text) or {}
            in_fields = file_content.get("input_fields", []) \
                if isinstance(file_content, dict) else []
            out_fields = file_content.get("output_fields", []) \
                if isinstance(file_content, dict) else []
            wrangle_studio.active_fields.set({"input": in_fields, "output": out_fields})
            wrangle_studio.active_raw_yaml.set(raw_text)
        except Exception as e:
            print(f"[_handle_normalize_fields] Reload failed after write: {e}")

        ui.notification_show(f"✅ {message}", type="success")

    @reactive.Effect
    @reactive.event(input.btn_upload_replace)
    def _handle_upload_replace():
        file_info = input.manifest_uploader()
        if not file_info:
            return
        try:
            cfg = ConfigManager(file_info[0]["datapath"])
            wrangling = cfg.raw_config.get("wrangling", {})
            nodes = _parse_logic_to_nodes(wrangling, "Uploaded (Replace)")
            wrangle_studio.logic_stack.set(nodes)
            ui.notification_show("✅ Stack Replaced.", type="success")
        except Exception as e:
            ui.notification_show(f"❌ Upload failed: {e}", type="error")

    @reactive.Effect
    @reactive.event(input.btn_upload_append)
    def _handle_upload_append():
        file_info = input.manifest_uploader()
        if not file_info:
            return
        try:
            cfg = ConfigManager(file_info[0]["datapath"])
            wrangling = cfg.raw_config.get("wrangling", {})
            new_nodes = _parse_logic_to_nodes(wrangling, "Uploaded (Append)")
            current_stack = wrangle_studio.logic_stack.get()
            wrangle_studio.logic_stack.set(current_stack + new_nodes)
            ui.notification_show(f"➕ Appended {len(new_nodes)} nodes.", type="success")
        except Exception as e:
            ui.notification_show(f"❌ Append failed: {e}", type="error")

    @reactive.Effect
    @reactive.event(input.btn_save_internal)
    def _handle_manifest_save_internal():
        # BP-PLOT-COMMIT-1 (ADR-083 §8): write the LOADED component file in its native
        # shape — plot specs serialise mapping+layers; wrangling routes nodes to their
        # source tier. The legacy tier3 dump (which wiped tier1/tier2 of the master
        # manifest) is removed: BLUEPRINT never authors T3 (ADR-082 §4).
        comp_path = wrangle_studio.active_component_path.get()
        if not comp_path:
            ui.notification_show(
                "This component was loaded inline — open it as a file to save, "
                "or edit it via the YAML escape hatch.", type="warning")
            return
        if not Path(comp_path).exists():
            ui.notification_show(
                f"❌ Component file no longer exists: {Path(comp_path).name}",
                type="error")
            return

        info = wrangle_studio.active_component_info.get() or {}
        role = info.get("role", "")
        nodes = wrangle_studio.logic_stack.get()
        raw_text = wrangle_studio.active_raw_yaml.get()

        try:
            content = _serialise_component_for_save(role, nodes, raw_text)
        except ValueError as ve:
            ui.notification_show(f"⚠️ {ve}", type="warning")
            return
        except Exception as e:
            ui.notification_show(f"❌ Save failed: {e}", type="error")
            return

        try:
            with open(comp_path, "w") as f:
                yaml.dump(content, f, default_flow_style=False, sort_keys=False)
            ui.notification_show(
                f"✅ Saved to {Path(comp_path).name}", type="success")
        except OSError as e:
            ui.notification_show(f"❌ Save failed: {e}", type="error")

    @reactive.Effect
    @reactive.event(input.btn_bp_apply_node)
    def _bp_apply_node_handler():
        """Apply form edits to the selected node in the logic stack (BP-FORMS-1)."""
        idx = wrangle_studio.selected_node_idx.get()
        nodes = wrangle_studio.logic_stack.get()

        if idx is None or not nodes or idx >= len(nodes):
            ui.notification_show("No node selected for editing.", type="warning")
            return

        node = nodes[idx]

        # BP-COMPONENT-FORMS-1/BP-MAPPING-FORM-1: branch by node kind.
        # Component (plot layer) nodes resolve schema from component catalog.
        # __mapping__ node uses bp_map_{aes_key} inputs (dedicated aes form).
        # Action nodes resolve schema from action catalog.
        component_name = node.get("component")
        is_component = component_name is not None
        new_comment = safe_input(input, "bp_form_comment", node.get("comment", ""))

        if is_component and component_name == "__mapping__":
            # BP-MAPPING-FORM-1: read aes mapping inputs and rebuild mapping params.
            _AES_KEYS = ["x", "y", "fill", "color", "size", "alpha", "shape", "facet_by"]
            new_params = {
                k: v
                for k in _AES_KEYS
                for v in [safe_input(input, f"bp_map_{k}", "")]
                if v
            }
            _snapshot_state()
            updated = list(nodes)
            updated[idx] = {
                "component": "__mapping__",
                "params": new_params,
                "comment": new_comment,
            }
            wrangle_studio.logic_stack.set(updated)
            wrangle_studio.invalidated_from.set(None)
            ui.notification_show("Aesthetic mapping updated.", type="message")
            return

        node_kind_key = "component" if is_component else "action"
        node_name = component_name if is_component else node.get("action", "")

        try:
            if is_component:
                from blueprint_arch.schema_registry import get_component_catalog
                catalog = get_component_catalog()
            else:
                from blueprint_arch.schema_registry import get_action_catalog
                catalog = get_action_catalog()
            ui_schema = catalog.get(node_name, {})
        except Exception:
            ui_schema = {}

        params_schema = ui_schema.get("params", {})
        new_params: dict = {}

        for param_key, param_def in params_schema.items():
            widget_type = param_def.get("widget", "string")
            input_id = f"bp_form_{param_key}"

            if widget_type == "column_selector":
                val = safe_input(input, input_id, None)
                if val is not None:
                    multi = param_def.get("multi", False)
                    if multi:
                        new_params[param_key] = (
                            val if isinstance(val, list) else [val]
                        )
                    else:
                        new_params[param_key] = (
                            val[0] if isinstance(val, list) and val else val
                        )
            elif widget_type in ("expression", "string"):
                val = safe_input(input, input_id, "")
                if val:
                    new_params[param_key] = val
            elif widget_type == "number":
                val = safe_input(input, input_id, None)
                if val is not None:
                    new_params[param_key] = val
            elif widget_type == "bool":
                new_params[param_key] = bool(safe_input(input, input_id, False))
            elif widget_type in ("enum", "dtype_picker"):
                multi = param_def.get("multi", False) if widget_type == "enum" else False
                val = safe_input(input, input_id, [] if multi else "")
                if val:
                    if multi:
                        new_params[param_key] = (
                            val if isinstance(val, list) else [val]
                        )
                    else:
                        new_params[param_key] = val
            elif widget_type == "column_or_literal":
                mode_id = f"bp_form_{param_key}_mode"
                mode = safe_input(input, mode_id, "literal")
                sub_id = (f"bp_form_{param_key}_col"
                          if mode == "column"
                          else f"bp_form_{param_key}_lit")
                val = safe_input(input, sub_id, "")
                if val:
                    new_params[param_key] = val

            elif widget_type == "color":
                # BP-COLOR-1/2: read composite color widget (includes project palette source)
                mode_id = f"bp_form_{param_key}_mode"
                top_mode = safe_input(input, mode_id, "literal")
                if top_mode == "column":
                    col_val = safe_input(input, f"bp_form_{param_key}_col", "")
                    if col_val:
                        new_params[param_key] = {"mode": "column", "column": col_val}
                else:
                    lit_mode = safe_input(input, f"bp_form_{param_key}_lmode", "palette")
                    if lit_mode == "project":
                        proj_val = safe_input(
                            input, f"bp_form_{param_key}_project_palette", ""
                        )
                        new_params[param_key] = {
                            "mode": "literal",
                            "literal_mode": "project",
                            "project_palette": proj_val or "",
                        }
                    elif lit_mode == "palette":
                        palette_val = safe_input(input, f"bp_form_{param_key}_palette", "")
                        new_params[param_key] = {
                            "mode": "literal",
                            "literal_mode": "palette",
                            "palette": palette_val or "Blues",
                        }
                    else:
                        hex_val = safe_input(input, f"bp_form_{param_key}_hex", "#345beb")
                        new_params[param_key] = {
                            "mode": "literal",
                            "literal_mode": "custom",
                            "hex": hex_val or "#345beb",
                        }
            else:
                val = safe_input(input, input_id, "")
                if val:
                    new_params[param_key] = val

        # No schema registered — preserve existing params
        if not params_schema:
            new_params = node.get("params", {})

        _snapshot_state()

        rebuilt = {
            node_kind_key: node_name,
            "params": new_params,
            "comment": new_comment,
        }
        # BP-PLOT-COMMIT-1: preserve the source-tier marker across edits (action nodes
        # only — component/plot nodes have no tier).
        if not is_component and node.get("_tier"):
            rebuilt["_tier"] = node["_tier"]

        updated = list(nodes)
        updated[idx] = rebuilt
        wrangle_studio.logic_stack.set(updated)

        # Mark downstream nodes as schema-stale after edit (action nodes only —
        # plot layers do not propagate an upstream schema).
        if is_component:
            wrangle_studio.invalidated_from.set(None)
        else:
            wrangle_studio.invalidated_from.set(
                idx + 1 if idx + 1 < len(updated) else None
            )

        unit = "Layer" if is_component else "Step"
        ui.notification_show(
            f"{unit} {idx + 1} ({node_name}) updated.", type="message"
        )

    def _bundle_filename():
        try:
            mp = wrangle_studio.active_manifest_path.get() or ""
        except Exception:
            mp = ""
        stem = Path(mp).stem if mp else "manifest"
        return f"{stem}_bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    @render.download(filename=_bundle_filename)
    def btn_download_manifest():
        # BP-PLOT-COMMIT-1 (ADR-083 §8): emit the FULL multi-file manifest as a zip —
        # the master .yaml plus its mirrored basename/ directory (all !include
        # fragments: input_fields/, wrangling/, output_fields/, assembly/, plots/).
        # Reflects the on-disk state, so the workflow is Save (commit fragment) ->
        # Download (bundle the tree). The old tier3 dump is removed.
        master = (wrangle_studio.active_manifest_path.get()
                  or safe_input(input, "stored_manifest_selector", None))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            if master and Path(master).exists():
                mp = Path(master)
                zf.write(mp, arcname=mp.name)
                # Mirrored basename/ directory holds every !include fragment.
                mirror = mp.parent / mp.stem
                if mirror.is_dir():
                    for f in sorted(mirror.rglob("*")):
                        if f.is_file():
                            arc = Path(mp.stem) / f.relative_to(mirror)
                            zf.write(f, arcname=str(arc))
            else:
                # No master resolved — fall back to the active fragment alone.
                comp = wrangle_studio.active_component_path.get()
                if comp and Path(comp).exists():
                    zf.write(Path(comp), arcname=Path(comp).name)
        yield buf.getvalue()

    # ── BP-ESCAPE-1: YAML escape hatch Save (manifest_edit_enabled only) ──────

    if bootloader.is_enabled("manifest_edit_enabled"):
        @reactive.Effect
        @reactive.event(input.btn_bp_save_yaml)
        def _bp_save_yaml_hatch():
            """Re-parse edited YAML from the escape hatch and update active_raw_yaml."""
            raw = input.bp_yaml_raw_edit()
            if not raw or not raw.strip():
                ui.notification_show("YAML escape hatch is empty.", type="warning")
                return
            try:
                yaml.safe_load(raw)
            except Exception as exc:
                pe = PipelineError(
                    component="BlueprintHandlers",
                    problem=f"YAML escape hatch parse error: {type(exc).__name__}: {exc}",
                    location="_bp_save_yaml_hatch()",
                    fix="Fix the YAML syntax error shown above. Common issues: wrong indentation, unquoted colons, missing closing brackets, or reserved word traps (e.g. 'on' must be quoted as 'on':).",
                    who="manifest_author",
                    category="blueprint_edit",
                    surface="blueprint_inline",
                    severity="error",
                    evidence={"error_type": type(exc).__name__, "error_detail": str(exc)[:300]},
                    reference="rules_manifest_structure.md §7",
                )
                print(pe.format())
                ui.notification_show(
                    f"YAML parse error: {exc}", type="error", duration=8
                )
                return
            wrangle_studio.active_raw_yaml.set(raw)
            wrangle_studio.data_ready_signal.set(wrangle_studio.data_ready_signal.get() + 1)
            ui.notification_show("Manifest YAML updated and re-parsed.", type="message")

    # ── BP-VISUAL-FORK-1: Visual Fork (manifest_edit_enabled only) ───────────

    if bootloader.is_enabled("manifest_edit_enabled"):
        _fork_preview_text: reactive.Value[str] = reactive.Value("")

        def _write_fork_to_manifest(master_path: str, fork_text: str) -> tuple[bool, str]:
            """Append fork_text to the master manifest file.

            Only safe when the manifest has NO !include directives — yaml.safe_load
            cannot round-trip files with !include tags.  When includes are present,
            the fork text is shown for manual paste instead.

            Returns (success: bool, message: str).
            """
            if not master_path or not Path(master_path).exists():
                return False, "No active manifest path."
            try:
                raw = Path(master_path).read_text(encoding="utf-8")
            except OSError as exc:
                return False, f"Cannot read manifest: {exc}"

            if "!include" in raw:
                return False, (
                    "This manifest uses !include directives — auto-write is not safe. "
                    "Copy the YAML fragment above and paste it into the manifest file manually."
                )
            try:
                # Append the fork block as a YAML comment-separated section
                separator = "\n# --- visual fork added by Blueprint Architect ---\n"
                new_raw = raw.rstrip() + separator + fork_text
                # Validate the combined YAML parses cleanly before writing
                yaml.safe_load(new_raw)
            except Exception as exc:
                return False, f"YAML merge validation failed: {exc}"
            try:
                Path(master_path).write_text(new_raw, encoding="utf-8")
            except OSError as exc:
                return False, f"Cannot write manifest: {exc}"
            return True, "Fork YAML written to manifest."

        @output
        @render.ui
        def bp_fork_ui():
            """Fork Node form — reads active_component_info only (Rule R4: never reads its own inputs)."""
            info = wrangle_studio.active_component_info.get() if wrangle_studio else {}
            schema_id = info.get("schema_id", "")
            role = info.get("role", "")
            forkable_roles = {"wrangling", "input_fields", "output_fields", "join", "plot_spec"}
            if not schema_id or role not in forkable_roles:
                return ui.div(
                    ui.tags.small(
                        "Select a forkable node (data schema, join, or plot) in the TubeMap.",
                        class_="text-muted",
                    ),
                    class_="p-2",
                )
            return ui.div(
                ui.tags.small(
                    f"Fork: {schema_id} ({role})",
                    class_="text-muted d-block mb-2",
                ),
                ui.input_text(
                    "bp_fork_new_id",
                    "New component ID",
                    value=f"{schema_id}_fork",
                    placeholder="snake_case_id",
                    width="100%",
                ),
                ui.div(
                    ui.input_action_button(
                        "btn_bp_fork_preview",
                        "Preview YAML",
                        class_="btn btn-primary btn-sm",
                    ),
                    ui.input_action_button(
                        "btn_bp_fork_write",
                        "Write to manifest",
                        class_="btn btn-warning btn-sm ms-2",
                    ),
                    class_="d-flex mt-2",
                ),
                ui.output_ui("bp_fork_preview_ui"),
                class_="p-2",
            )

        @output
        @render.ui
        def bp_fork_preview_ui():
            """Shows generated fork YAML — reads _fork_preview_text only (Rule R4)."""
            text = _fork_preview_text.get()
            if not text:
                return ui.div()
            return ui.div(
                ui.tags.pre(
                    text,
                    class_="bp-escape-pre mt-2",
                    style="max-height:220px;overflow-y:auto;font-size:0.78rem;",
                ),
                ui.tags.small(
                    "Review, then click 'Write to manifest' or paste manually.",
                    class_="text-muted d-block mt-1",
                ),
            )

        @reactive.Effect
        @reactive.event(input.btn_bp_fork_preview)
        def _handle_fork_preview():
            """Generate fork YAML from generate_fork_yaml() and cache in _fork_preview_text."""
            info = wrangle_studio.active_component_info.get() if wrangle_studio else {}
            schema_id = info.get("schema_id", "")
            role = info.get("role", "")
            if not schema_id or not role:
                ui.notification_show("No component selected.", type="warning")
                return
            try:
                new_id = (input.bp_fork_new_id() or "").strip()
            except Exception:
                new_id = ""
            if not new_id:
                ui.notification_show("Enter a new component ID first.", type="warning")
                return
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", new_id):
                ui.notification_show(
                    "New ID must be snake_case (letters, digits, underscores only).",
                    type="warning",
                )
                return
            if active_cfg is None:
                ui.notification_show("No active manifest configuration.", type="warning")
                return
            try:
                cfg = active_cfg()
                raw_config = cfg.raw_config
            except Exception as exc:
                ui.notification_show(f"Cannot read manifest config: {exc}", type="error")
                return
            fork_text = generate_fork_yaml(schema_id, role, new_id, raw_config)
            if not fork_text:
                ui.notification_show(
                    f"Could not generate fork for role '{role}' / id '{schema_id}'. "
                    "Ensure the manifest is loaded and the node is forkable.",
                    type="warning",
                )
                _fork_preview_text.set("")
                return
            _fork_preview_text.set(fork_text)

        @reactive.Effect
        @reactive.event(input.btn_bp_fork_write)
        def _handle_fork_write():
            """Write cached fork YAML to the active manifest file (inline manifests only)."""
            fork_text = _fork_preview_text.get()
            if not fork_text:
                ui.notification_show(
                    "Generate a preview first before writing.", type="warning"
                )
                return
            master_path = safe_input(input, "stored_manifest_selector", None)
            success, msg = _write_fork_to_manifest(master_path or "", fork_text)
            if success:
                ui.notification_show(msg, type="message", duration=5)
                _fork_preview_text.set("")
                # Re-load sibling map so new node appears in the TubeMap
                try:
                    ctx_map = build_sibling_map(master_path)
                    component_ctx_map.set(ctx_map)
                except Exception:
                    pass
            else:
                ui.notification_show(msg, type="warning", duration=8)

        @reactive.Effect
        def _clear_fork_preview_on_node_change():
            """Clear stale fork preview when the selected TubeMap node changes (Rule R3 idempotent guard)."""
            _ = wrangle_studio.active_component_info.get()  # subscribe
            cur = _fork_preview_text.get()
            if cur:  # idempotent guard — only write when a clear is actually needed
                _fork_preview_text.set("")

    # ── Blueprint AI Agent (ADR-076) ─────────────────────────────────────────

    if not bootloader.is_enabled("blueprint_agent_enabled"):
        return  # remainder of this block only registers when the flag is on

    _agent_session_id: reactive.Value[str] = reactive.Value("")
    _agent_conversation: reactive.Value[list] = reactive.Value([])
    _agent_in_flight: reactive.Value[bool] = reactive.Value(False)

    def _get_or_create_session() -> str:
        sid = _agent_session_id.get()
        if not sid:
            sid = str(uuid.uuid4())
            _agent_session_id.set(sid)
        return sid

    def _render_message(role: str, text: str):
        css_class = "bp-agent-message user" if role == "user" else "bp-agent-message agent"
        return ui.div(text, class_=css_class)

    # ------------------------------------------------------------------
    # bp_plot_defaults_form_ui — VIZFAC-BLUEPRINT-FORM-1
    # Shows editable plot_defaults for the active manifest (manifest root node).
    # Shown when no sub-component is selected (active_viz_id empty / None).
    # ------------------------------------------------------------------

    # Allowed plot_defaults keys per rules_manifest_structure.md §10.
    _PLOT_DEFAULT_KEYS = ["palette", "theme", "default_font_family",
                          "facet_panel_spacing", "legend_position"]
    _THEME_CHOICES = ["theme_light", "theme_bw", "theme_minimal",
                      "theme_classic", "theme_dashboard"]
    _LEGEND_CHOICES = ["right", "top", "bottom", "left", "none"]

    @output
    @render.ui
    def bp_plot_defaults_form_ui():
        """Edit form for manifest-level plot_defaults (manifest root node). VIZFAC-BLUEPRINT-FORM-1."""
        # Only render when active_cfg is available and no sub-component is selected
        if active_cfg is None:
            return ui.div()
        active_id = wrangle_studio.active_viz_id.get() if wrangle_studio is not None else None
        if active_id:
            # A specific schema/plot/assembly node is selected — form not relevant here
            return ui.div()

        try:
            cfg = active_cfg()
            defaults = cfg.raw_config.get("plot_defaults") or {}
        except Exception:
            return ui.div()

        palette_val = defaults.get("palette", "")
        theme_val = defaults.get("theme", "theme_light")
        font_val = defaults.get("default_font_family", "")
        spacing_val = str(defaults.get("facet_panel_spacing", "0.05"))
        legend_val = defaults.get("legend_position", "right")

        return ui.div(
            ui.tags.small("Active manifest — plot_defaults", class_="text-muted d-block mb-2"),
            ui.input_text("bp_pd_palette", "Palette", value=palette_val,
                          placeholder="e.g. nvi_official or Blues"),
            ui.input_select("bp_pd_theme", "Theme",
                            choices={t: t for t in _THEME_CHOICES},
                            selected=theme_val if theme_val in _THEME_CHOICES else "theme_light"),
            ui.input_text("bp_pd_font", "Default font family", value=font_val,
                          placeholder="e.g. Liberation Sans"),
            ui.input_text("bp_pd_spacing", "Facet panel spacing", value=spacing_val,
                          placeholder="0.05 – 1.0"),
            ui.input_select("bp_pd_legend", "Legend position",
                            choices={v: v for v in _LEGEND_CHOICES},
                            selected=legend_val if legend_val in _LEGEND_CHOICES else "right"),
            ui.input_action_button("bp_pd_apply", "Apply to session",
                                   class_="btn-primary btn-sm w-100 mt-2"),
            ui.tags.small(
                "Changes are session-only. Edit YAML directly to persist.",
                class_="text-muted d-block mt-1",
            ),
            class_="p-2",
        )

    @reactive.Effect
    @reactive.event(input.bp_pd_apply)
    def _bp_apply_plot_defaults():
        """Write bp_plot_defaults form values into the active manifest raw_config (session-only)."""
        if active_cfg is None:
            return
        try:
            cfg = active_cfg()
        except Exception:
            return
        try:
            palette = (getattr(input, "bp_pd_palette")() or "").strip()
            theme = (getattr(input, "bp_pd_theme")() or "theme_light").strip()
            font = (getattr(input, "bp_pd_font")() or "").strip()
            spacing_raw = (getattr(input, "bp_pd_spacing")() or "0.05").strip()
            legend = (getattr(input, "bp_pd_legend")() or "right").strip()
        except Exception:
            return

        try:
            spacing = float(spacing_raw)
        except (ValueError, TypeError):
            spacing = 0.05

        new_defaults: dict = {}
        if palette:
            new_defaults["palette"] = palette
        if theme:
            new_defaults["theme"] = theme
        if font:
            new_defaults["default_font_family"] = font
        if spacing != 0.05 or "facet_panel_spacing" in (cfg.raw_config.get("plot_defaults") or {}):
            new_defaults["facet_panel_spacing"] = spacing
        if legend and legend != "right":
            new_defaults["legend_position"] = legend

        cfg.raw_config["plot_defaults"] = new_defaults
        ui.notification_show("plot_defaults updated for this session.", type="message", duration=3)

    @output
    @render.ui
    def blueprint_agent_panel_ui():
        """Renders the full agent chat panel. Reads reactive state; never calls .set()."""
        adapter = bootloader.get_agent_adapter()
        in_flight = _agent_in_flight.get()
        conversation = _agent_conversation.get()

        # Status banner
        if adapter is None or adapter.is_disabled:
            banner_class = "bp-agent-status-banner error"
            banner_text = "Agent unavailable — backend not configured."
        elif in_flight:
            banner_class = "bp-agent-status-banner busy"
            banner_text = ui.div(
                ui.span(class_="spinner"),
                ui.span(" Thinking..."),
                class_="d-flex align-items-center gap-2"
            )
        else:
            banner_class = "bp-agent-status-banner ok"
            banner_text = "Blueprint Agent ready."

        # Conversation log
        if not conversation:
            log_content = ui.div(
                ui.p("Ask me about actions, components, or field contracts "
                     "for the active manifest.",
                     class_="text-muted small fst-italic p-2 mb-0"),
                class_="bp-agent-log-empty"
            )
        else:
            msgs = [_render_message(m["role"], m["content"]) for m in conversation
                    if m.get("role") in ("user", "assistant")]
            log_content = ui.div(*msgs, class_="bp-agent-log")

        # Input row — disable send while in-flight or no adapter
        send_disabled = in_flight or adapter is None or adapter.is_disabled

        return ui.div(
            ui.div(banner_text, class_=banner_class),
            log_content,
            ui.div(
                ui.input_text("bp_agent_input", label=None,
                              placeholder="Type a question...",
                              width="100%"),
                ui.input_action_button("bp_agent_send", "Send",
                                       disabled=send_disabled,
                                       class_="btn btn-primary btn-sm mt-1 w-100"),
                class_="bp-agent-input-area"
            ),
            id="blueprint_agent_panel",
            class_="bp-agent-panel d-flex flex-column h-100"
        )

    @reactive.Effect
    @reactive.event(input.bp_agent_send)
    async def _bp_agent_send():
        """Handles send button: calls adapter in a thread, runs tool loop, updates conversation."""
        user_text = (input.bp_agent_input() or "").strip()
        if not user_text:
            return

        adapter = bootloader.get_agent_adapter()
        if adapter is None or adapter.is_disabled:
            return

        # Guard: single-flight
        if _agent_in_flight.get():
            return

        session_id = _get_or_create_session()

        # Append user message and set in-flight
        cur = _agent_conversation.get()
        _agent_conversation.set(cur + [{"role": "user", "content": user_text}])
        _agent_in_flight.set(True)

        try:
            # Load system prompt once per panel lifecycle
            agent_cfg = bootloader.get_agent_config()
            instructions_file = agent_cfg.get("instructions_file")
            if not instructions_file:
                raise ValueError(
                    "blueprint_agent.instructions_file is required in the persona template "
                    "when blueprint_agent_enabled=True."
                )
            system_prompt = build_system_prompt(instructions_file)

            # Tool-call loop (max 3 rounds to prevent runaway)
            current_user_msg = user_text
            final_reply = ""
            for _round in range(3):
                reply_text = await asyncio.to_thread(
                    adapter.send_message,
                    session_id,
                    current_user_msg,
                    system_prompt=system_prompt,
                )
                parse_result = extract_tool_calls(reply_text)

                if not parse_result.tool_calls:
                    # No tool calls — this is the final response
                    final_reply = reply_text
                    break

                # Execute each tool call and collect results
                tool_results = []
                for tc in parse_result.tool_calls:
                    result = call_tool(tc.tool_name, tc.args)
                    tool_results.append({"tool": tc.tool_name, "result": result})

                if parse_result.errors:
                    # Malformed blocks — ask agent to retry with error context
                    current_user_msg = parse_result.format_error_turn()
                else:
                    # Feed results back as a user turn for the next round
                    lines = []
                    for tr in tool_results:
                        lines.append(
                            f"Tool `{tr['tool']}` result:\n```json\n"
                            f"{json.dumps(tr['result'], indent=2)}\n```"
                        )
                    current_user_msg = "\n\n".join(lines)
            else:
                # Exhausted rounds without a clean reply
                final_reply = reply_text  # use last reply

            # Append assistant reply
            conv = _agent_conversation.get()
            _agent_conversation.set(conv + [{"role": "assistant", "content": final_reply}])

        except Exception as exc:
            conv = _agent_conversation.get()
            _agent_conversation.set(
                conv + [{"role": "assistant",
                         "content": f"[Agent error: {exc}]"}]
            )
        finally:
            _agent_in_flight.set(False)

    # ══════════════════════════════════════════════════════════════════════
    # BP-JOINT-1 (ADR-082 Q5) — Joint Designer pane
    # Left + right ingredient schemas side-by-side with a live, real-data
    # key-match preview; emits a canonical `join` recipe step into logic_stack.
    # ══════════════════════════════════════════════════════════════════════

    # Last computed key-match result (+ meta), rendered by joint_preview_ui.
    joint_preview = reactive.Value(None)
    # Desired key pre-selection for the pickers (set on edit; empty on create).
    joint_prefill = reactive.Value({"left": [], "right": []})

    def _jd_field_names(fields):
        """Extract an ordered list of field slugs from any field shape.

        Accepts dict {slug: meta}, list[str], or list[{name|field|slug, ...}].
        """
        if not fields:
            return []
        if isinstance(fields, dict):
            return list(fields.keys())
        if isinstance(fields, list):
            names = []
            for item in fields:
                if isinstance(item, str):
                    names.append(item)
                elif isinstance(item, dict):
                    names.append(item.get("name") or item.get("field")
                                 or item.get("slug") or "")
            return [n for n in names if n]
        return []

    def _jd_ingredients():
        """Return {schema_id: [field_names]} for joinable data-source schemas.

        Excludes join and plot schemas — only raw/metadata/additional data
        sources can be join ingredients.
        """
        reg = schema_registry.get() or {}
        ctx = component_ctx_map.get() or {}
        inc = includes_map.get() or {}
        out = {}
        for sid, entry in reg.items():
            stype = (entry.get("schema_type") or "").lower()
            if stype in ("join_manifests", "join", "plots", "plot_spec"):
                continue
            try:
                fields = resolve_fields_for_schema(sid, ctx, inc)
            except Exception:
                fields = []
            names = _jd_field_names(fields)
            if names:
                out[sid] = names
        return out

    @reactive.Effect
    def _jd_populate_ingredients():
        """Populate ingredient selects from the active manifest's schemas.

        Depends only on schema_registry / ctx_map (changes on manifest import) —
        never on the ingredient inputs, so user picks are not clobbered.
        """
        ings = list(_jd_ingredients().keys())
        choices = {sid: sid for sid in ings}
        ui.update_select("joint_left_ingredient", choices=choices,
                         selected=(ings[0] if ings else None))
        ui.update_select("joint_right_ingredient", choices=choices,
                         selected=(ings[1] if len(ings) > 1 else
                                   (ings[0] if ings else None)))

    @output
    @render.ui
    def joint_designer_status_ui():
        edit_idx = wrangle_studio.joint_edit_idx.get()
        # Re-render when a fresh-join request arrives.
        wrangle_studio.joint_request.get()
        if not _jd_ingredients():
            return ui.div(
                "Import a manifest with at least one data source to design a join.",
                class_="ultra-small text-muted fst-italic")
        if edit_idx is not None:
            return ui.div(
                ui.tags.strong("Editing join step "),
                ui.tags.code(f"#{edit_idx}"),
                " — adjust keys/strategy and press Apply to update it.",
                class_="ultra-small",
                style="background:#eef0fb;padding:6px 10px;border-radius:4px;")
        return ui.div(
            "Creating a new join step. Pick the right ingredient, choose join "
            "key(s) on each side, preview the match, then Apply.",
            class_="ultra-small text-muted")

    def _jd_schema_card(ingredient_id):
        ings = _jd_ingredients()
        if not ingredient_id or ingredient_id not in ings:
            return ui.p("Select an ingredient.", class_="text-muted small fst-italic")
        names = ings[ingredient_id]
        chips = [
            ui.tags.code(n, style=("font-size:0.72rem;color:#345beb;"
                                   "background:#f8f9fa;padding:1px 5px;"
                                   "border-radius:3px;margin:1px;display:inline-block;"))
            for n in names
        ]
        return ui.div(
            ui.div(ui.tags.strong(ingredient_id),
                   ui.tags.span(f"  {len(names)} field"
                                f"{'s' if len(names) != 1 else ''}",
                                class_="text-muted",
                                style="font-size:0.7rem;"),
                   class_="mb-1"),
            ui.div(*chips),
        )

    @output
    @render.ui
    def joint_left_schema_ui():
        return _jd_schema_card(safe_input(input, "joint_left_ingredient", None))

    @output
    @render.ui
    def joint_right_schema_ui():
        return _jd_schema_card(safe_input(input, "joint_right_ingredient", None))

    @output
    @render.ui
    def joint_key_pickers_ui():
        """Mount the per-side key multi-selects.

        Rule R4: this output reads only the ingredient selects (+ joint_prefill),
        never the key values — so selecting keys does not re-mount the widgets.
        """
        ings = _jd_ingredients()
        left_ing = safe_input(input, "joint_left_ingredient", None)
        right_ing = safe_input(input, "joint_right_ingredient", None)
        left_fields = ings.get(left_ing, [])
        right_fields = ings.get(right_ing, [])
        prefill = joint_prefill.get()
        left_sel = [k for k in prefill.get("left", []) if k in left_fields]
        right_sel = [k for k in prefill.get("right", []) if k in right_fields]
        return ui.layout_columns(
            ui.input_selectize(
                "joint_left_keys", "Left join key(s)",
                choices={c: c for c in left_fields},
                selected=left_sel, multiple=True),
            ui.input_selectize(
                "joint_right_keys", "Right join key(s)",
                choices={c: c for c in right_fields},
                selected=right_sel, multiple=True),
            col_widths=[6, 6],
        )

    @reactive.Effect
    @reactive.event(wrangle_studio.joint_request)
    def _jd_reset_on_new():
        """A fresh-join request (Add Node: join) clears the draft."""
        if wrangle_studio.joint_request.get() == 0:
            return
        joint_prefill.set({"left": [], "right": []})
        joint_preview.set(None)
        ui.update_text_area("joint_comment", value="")
        ui.update_select("joint_how", selected="inner")

    @reactive.Effect
    @reactive.event(wrangle_studio.selected_node_idx)
    def _jd_load_for_edit():
        """Selecting a join node in the stack opens the Designer pre-filled (edit)."""
        idx = wrangle_studio.selected_node_idx.get()
        if idx is None:
            return
        stack = wrangle_studio.logic_stack.get()
        if not (0 <= idx < len(stack)):
            return
        node = stack[idx]
        if node.get("action") not in ("join", "join_filter"):
            return
        params = node.get("params", {})
        parsed = parse_join_step(params)
        comment = node.get("comment", "")

        ings = _jd_ingredients()
        ing_ids = list(ings.keys())
        right_ing = parsed.get("right_ingredient")
        # Best-effort left = first ingredient that is not the right one.
        left_ing = next((i for i in ing_ids if i != right_ing),
                        (ing_ids[0] if ing_ids else None))

        joint_prefill.set({"left": parsed.get("left_keys", []),
                           "right": parsed.get("right_keys", [])})
        wrangle_studio.joint_edit_idx.set(idx)
        if left_ing:
            ui.update_select("joint_left_ingredient", selected=left_ing)
        if right_ing:
            ui.update_select("joint_right_ingredient", selected=right_ing)
        ui.update_select("joint_how", selected=parsed.get("how", "inner"))
        ui.update_text_area("joint_comment", value=comment)
        joint_preview.set(None)
        ui.update_navs("architect_internal_tabs", selected="joint_designer")

    def _jd_extract_keys(project_id, ingredient_id, keys):
        """Materialise an ingredient and return (rows, dtypes) for its key columns.

        rows: list of String-cast key tuples (mirrors how the assembler joins).
        dtypes: original polars dtype names, key-aligned.
        Raises on materialisation / missing-column errors (caller surfaces them).
        """
        anchor_dir = bootloader.get_location("user_sessions") / "anchors"
        anchor_dir.mkdir(parents=True, exist_ok=True)
        out_p = anchor_dir / f"_jd_{ingredient_id}.parquet"
        orchestrator.materialize_tier1(
            project_id=project_id, collection_id=ingredient_id, output_path=out_p)
        lf = pl.scan_parquet(out_p)
        schema = lf.collect_schema()
        missing = [k for k in keys if k not in schema.names()]
        if missing:
            raise ValueError(
                f"Ingredient '{ingredient_id}' has no column(s): {', '.join(missing)}")
        dtypes = [str(schema[k]) for k in keys]
        rows = (lf.select([pl.col(k).cast(pl.String) for k in keys])
                  .unique().collect().rows())
        return rows, dtypes

    @reactive.Effect
    @reactive.event(input.btn_joint_preview)
    def _jd_run_preview():
        left_ing = safe_input(input, "joint_left_ingredient", None)
        right_ing = safe_input(input, "joint_right_ingredient", None)
        left_keys = list(safe_input(input, "joint_left_keys", []) or [])
        right_keys = list(safe_input(input, "joint_right_keys", []) or [])

        if not left_ing or not right_ing:
            joint_preview.set({"error": "Select both a left and right ingredient."})
            return
        if not left_keys or not right_keys:
            joint_preview.set({"error": "Select at least one key on each side."})
            return
        if len(left_keys) != len(right_keys):
            joint_preview.set({"error": (
                f"Key arity mismatch: {len(left_keys)} left vs "
                f"{len(right_keys)} right. Pick an equal number on each side.")})
            return

        manifest_path = wrangle_studio.active_manifest_path.get()
        if not manifest_path:
            joint_preview.set({"error": "No active manifest — import one first."})
            return
        project_id = Path(manifest_path).stem

        try:
            with ui.Progress(min=0, max=2) as p:
                p.set(0, message=f"Materialising {left_ing}…")
                left_rows, left_dtypes = _jd_extract_keys(
                    project_id, left_ing, left_keys)
                p.set(1, message=f"Materialising {right_ing}…")
                right_rows, right_dtypes = _jd_extract_keys(
                    project_id, right_ing, right_keys)
            stats = compute_key_match(
                left_rows, right_rows, left_dtypes, right_dtypes)
            stats["error"] = None
            stats["_meta"] = {"left_ing": left_ing, "right_ing": right_ing,
                              "left_keys": left_keys, "right_keys": right_keys}
            joint_preview.set(stats)
        except Exception as exc:
            joint_preview.set({"error": f"Preview failed: {exc}"})

    @output
    @render.ui
    def joint_preview_ui():
        r = joint_preview.get()
        if r is None:
            return ui.div(
                "No preview yet — choose keys and press “Preview key match”.",
                class_="ultra-small text-muted fst-italic")
        if r.get("error"):
            return ui.div(r["error"], class_="ultra-small",
                          style=("background:#ffe0e0;color:#d62828;padding:8px 10px;"
                                 "border-radius:4px;"))
        if not r.get("arity_ok"):
            return ui.div(
                "Key arity mismatch — select an equal number of keys on each side.",
                class_="ultra-small",
                style=("background:#ffe0e0;color:#d62828;padding:8px 10px;"
                       "border-radius:4px;"))

        rate = r["match_rate"] * 100
        # Status tint by match quality.
        if rate >= 99.9:
            bg, fg = "#d5efec", "#0b6358"
        elif rate >= 50:
            bg, fg = "#fff3cd", "#856404"
        else:
            bg, fg = "#ffe0e0", "#d62828"

        dtype_rows = [
            ui.tags.li(
                f"{p['left_key_dtype']} ↔ {p['right_key_dtype']}: "
                + ("compatible" if p["family_match"] else "DIFFERENT family — "
                   "values may not align (e.g. Float64 '2022.0' vs Int64 '2022')"),
                style="font-size:0.7rem;")
            for p in r.get("dtype_pairs", [])
        ]
        samp_left = r.get("left_only_sample", [])
        samp_right = r.get("right_only_sample", [])

        def _fmt_sample(rows):
            return ", ".join("/".join(str(x) for x in t) for t in rows) or "—"

        return ui.div(
            ui.div(
                ui.tags.strong(
                    f"{r['matched']} / {r['left_total']} left keys matched "
                    f"({rate:.1f}%)"),
                style=f"font-size:0.85rem;color:{fg};"),
            ui.tags.ul(
                ui.tags.li(f"Left distinct keys: {r['left_total']}  ·  "
                           f"Right distinct keys: {r['right_total']}",
                           style="font-size:0.72rem;"),
                ui.tags.li(f"Left-only (dropped by inner join): {r['left_only']}  ·  "
                           f"Right-only: {r['right_only']}",
                           style="font-size:0.72rem;"),
                ui.tags.li([ui.tags.span("dtype compatibility:"), ui.tags.ul(*dtype_rows)]
                           if dtype_rows else "dtype compatibility: —",
                           style="font-size:0.72rem;"),
                ui.tags.li(f"Sample left-only: {_fmt_sample(samp_left)}",
                           style="font-size:0.7rem;color:#6c757d;"),
                ui.tags.li(f"Sample right-only: {_fmt_sample(samp_right)}",
                           style="font-size:0.7rem;color:#6c757d;"),
                style="margin:4px 0 0 0;padding-left:18px;"),
            style=(f"background:{bg};padding:10px 12px;border-radius:6px;"
                   "margin-top:8px;"),
        )

    @reactive.Effect
    @reactive.event(input.btn_joint_apply)
    def _jd_apply():
        left_ing = safe_input(input, "joint_left_ingredient", None)
        right_ing = safe_input(input, "joint_right_ingredient", None)
        left_keys = list(safe_input(input, "joint_left_keys", []) or [])
        right_keys = list(safe_input(input, "joint_right_keys", []) or [])
        how = safe_input(input, "joint_how", "inner")
        comment = (safe_input(input, "joint_comment", "") or "").strip()

        if not right_ing:
            ui.notification_show("Select a right ingredient.", type="error")
            return
        if not left_keys or not right_keys:
            ui.notification_show("Select at least one key on each side.",
                                 type="error")
            return
        if len(left_keys) != len(right_keys):
            ui.notification_show(
                "Key arity mismatch — equal number of keys required.", type="error")
            return
        # Audit gate (ui_implementation_contract §3): justification is mandatory.
        if not comment:
            ui.notification_show(
                "Justification is required before applying a join.", type="error")
            return

        step = build_join_step(right_ing, left_keys, right_keys, how=how,
                               comment=comment)
        params = {k: v for k, v in step.items()
                  if k not in ("action", "comment")}
        node = {"action": "join", "params": params, "comment": comment}

        _snapshot_state()
        stack = wrangle_studio.logic_stack.get().copy()
        edit_idx = wrangle_studio.joint_edit_idx.get()
        if edit_idx is not None and 0 <= edit_idx < len(stack):
            stack[edit_idx] = node
            msg = f"Join step #{edit_idx} updated ({right_ing})."
        else:
            stack.append(node)
            msg = f"Join step added ({right_ing})."
        wrangle_studio.logic_stack.set(stack)
        wrangle_studio.joint_edit_idx.set(None)
        ui.notification_show(msg, type="message")

    # ══════════════════════════════════════════════════════════════════════
    # BP-GROUPS-1 — Groups & Plots inventory (ADR-082 Q6)
    # Sidebar inventory list with create/delete/assign affordances.
    # Pure CRUD logic lives in group_plot_manager.py (Two-Category Law).
    # ══════════════════════════════════════════════════════════════════════

    @output
    @render.ui
    def bp_groups_inventory_ui():
        """Inventory of analysis_groups/plots with CRUD affordances."""
        _groups_refresh.get()   # reactive dependency — re-render after mutations
        path = safe_input(input, "stored_manifest_selector", None)
        if not path or not Path(path).exists():
            return ui.div("Load a manifest first.",
                          class_="ultra-small text-muted p-2")
        try:
            groups = list_groups_plots(path)
        except Exception as e:
            return ui.div(f"Error reading manifest: {e}",
                          style="font-size:0.72rem;color:#d62828;padding:8px;")

        def _btn(label: str, action: str, style: str = "") -> ui.Tag:
            base = ("height:22px;font-size:0.65rem;padding:0 6px;"
                    "border:none;cursor:pointer;border-radius:3px;")
            return ui.tags.button(
                label,
                style=base + style,
                onclick=(
                    f"Shiny.setInputValue('bp_grp_action',"
                    f"'{action}',{{priority:'event'}});"
                ),
            )

        group_cards = []
        for grp_id, grp in (groups or {}).items():
            grp_label = (grp.get("label", grp_id)
                         if isinstance(grp, dict) else grp_id)
            plots = grp.get("plots", {}) if isinstance(grp, dict) else {}

            plot_rows = []
            for pid, pspec in (plots or {}).items():
                plabel = (pspec.get("label", pid)
                          if isinstance(pspec, dict) else pid)
                plot_rows.append(
                    ui.div(
                        ui.span(plabel,
                                style="font-size:0.72rem;flex:1 1 0;overflow:hidden;"
                                      "text-overflow:ellipsis;white-space:nowrap;"),
                        _btn("Go", f"goto:{grp_id}/{pid}",
                             "background:#345beb;color:#fff;margin-left:3px;"),
                        _btn("Move", f"move:{grp_id}/{pid}",
                             "background:#345beb;color:#fff;margin-left:3px;"),
                        _btn("Del", f"del_plt:{grp_id}/{pid}",
                             "background:#ffc107;color:#000;font-weight:700;"
                             "margin-left:3px;"),
                        style="display:flex;align-items:center;padding:2px 0;"
                              "border-top:1px solid #f0f0f0;",
                    )
                )

            group_cards.append(
                ui.div(
                    ui.div(
                        ui.tags.strong(grp_label,
                                       style="font-size:0.78rem;flex:1 1 0;"),
                        _btn("+ Plot", f"add_plt:{grp_id}",
                             "background:#345beb;color:#fff;"),
                        _btn("Del grp", f"del_grp:{grp_id}",
                             "background:#ffc107;color:#000;font-weight:700;"
                             "margin-left:3px;"),
                        style="display:flex;align-items:center;gap:4px;",
                    ),
                    *plot_rows,
                    style=("padding:6px 8px;margin-bottom:6px;"
                           "background:#f8f9fa;border-radius:6px;"
                           "border:1px solid #e9ecef;"),
                )
            )

        return ui.div(
            *group_cards,
            ui.input_action_button(
                "btn_bp_create_group", "+ Group",
                class_="btn btn-primary btn-sm",
                style="margin-top:4px;width:100%;height:28px;font-size:0.78rem;",
            ),
            class_="p-2",
        )

    # --- BP-GROUPS-1 CRUD dispatcher ---

    @reactive.Effect
    @reactive.event(input.bp_grp_action)
    def _handle_grp_action():
        """Dispatch group/plot CRUD actions from the inventory panel."""
        raw = safe_input(input, "bp_grp_action", None)
        if not raw:
            return
        path = safe_input(input, "stored_manifest_selector", None)
        if not path or not Path(path).exists():
            return

        try:
            if raw.startswith("del_grp:"):
                grp_id = raw[len("del_grp:"):]
                ok, msg = delete_group(path, grp_id)
                ui.notification_show(msg, type="success" if ok else "warning")
                if ok:
                    _do_refresh_blueprint(path)

            elif raw.startswith("del_plt:"):
                rest = raw[len("del_plt:"):]
                grp_id, pid = rest.split("/", 1)
                ok, msg = delete_plot(path, grp_id, pid)
                ui.notification_show(msg, type="success" if ok else "warning")
                if ok:
                    _do_refresh_blueprint(path)

            elif raw.startswith("goto:"):
                rest = raw[len("goto:"):]
                grp_id, pid = rest.split("/", 1)
                ctx_map = component_ctx_map.get()
                for rel, entry in ctx_map.items():
                    if (entry.get("schema_id") == pid
                            and entry.get("role") == "plot_spec"):
                        if selected_lineage_rel is not None:
                            selected_lineage_rel.set(rel)
                        break

            elif raw.startswith("move:"):
                rest = raw[len("move:"):]
                from_grp, pid = rest.split("/", 1)
                groups = list_groups_plots(path)
                other = {g: (groups[g].get("label", g)
                             if isinstance(groups[g], dict) else g)
                         for g in groups if g != from_grp}
                if not other:
                    ui.notification_show("No other groups to move to.",
                                         type="warning")
                    return
                _grp_modal_ctx.set({"path": path, "from_grp": from_grp,
                                    "pid": pid})
                ui.modal_show(
                    ui.modal(
                        ui.p(f"Move plot '{pid}' from '{from_grp}' to:",
                             class_="ultra-small"),
                        ui.input_select("bp_move_target_group",
                                        "Target group", choices=other),
                        ui.input_action_button(
                            "btn_bp_move_plt_submit", "Move",
                            class_="btn btn-primary btn-sm mt-2"),
                        title="Move Plot",
                        easy_close=True,
                        footer=None,
                    )
                )

            elif raw.startswith("add_plt:"):
                grp_id = raw[len("add_plt:"):]
                _grp_modal_ctx.set({"path": path, "grp_id": grp_id})
                ui.modal_show(
                    ui.modal(
                        ui.input_text("bp_new_plot_id", "Plot ID (snake_case)", ""),
                        ui.input_text("bp_new_plot_label", "Label (optional)", ""),
                        ui.input_action_button(
                            "btn_bp_plt_submit", "Create",
                            class_="btn btn-primary btn-sm mt-2"),
                        title=f"Add plot to '{grp_id}'",
                        easy_close=True,
                        footer=None,
                    )
                )

        except Exception as e:
            ui.notification_show(f"Action failed: {e}", type="error")

    @reactive.Effect
    @reactive.event(input.btn_bp_create_group)
    def _handle_create_group_btn():
        """Open modal to create a new analysis group."""
        path = safe_input(input, "stored_manifest_selector", None)
        if not path:
            return
        _grp_modal_ctx.set({"path": path})
        ui.modal_show(
            ui.modal(
                ui.input_text("bp_new_group_id", "Group ID (snake_case)", ""),
                ui.input_text("bp_new_group_label", "Label (optional)", ""),
                ui.input_action_button(
                    "btn_bp_grp_submit", "Create",
                    class_="btn btn-primary btn-sm mt-2"),
                title="Create analysis group",
                easy_close=True,
                footer=None,
            )
        )

    @reactive.Effect
    @reactive.event(input.btn_bp_grp_submit)
    def _handle_grp_submit():
        """Create group from modal."""
        ctx = _grp_modal_ctx.get()
        path = ctx.get("path")
        if not path:
            return
        grp_id = (safe_input(input, "bp_new_group_id", "") or "").strip()
        label = (safe_input(input, "bp_new_group_label", "") or "").strip()
        ok, msg = create_group(path, grp_id, label)
        ui.notification_show(msg, type="success" if ok else "warning")
        if ok:
            ui.modal_remove()
            _do_refresh_blueprint(path)

    @reactive.Effect
    @reactive.event(input.btn_bp_plt_submit)
    def _handle_plt_submit():
        """Create plot stub from modal."""
        ctx = _grp_modal_ctx.get()
        path = ctx.get("path")
        grp_id = ctx.get("grp_id")
        if not path or not grp_id:
            return
        pid = (safe_input(input, "bp_new_plot_id", "") or "").strip()
        label = (safe_input(input, "bp_new_plot_label", "") or "").strip()
        ok, msg = create_plot(path, grp_id, pid, label)
        ui.notification_show(msg, type="success" if ok else "warning")
        if ok:
            ui.modal_remove()
            _do_refresh_blueprint(path)

    @reactive.Effect
    @reactive.event(input.btn_bp_move_plt_submit)
    def _handle_move_plt_submit():
        """Assign plot to another group from modal."""
        ctx = _grp_modal_ctx.get()
        path = ctx.get("path")
        from_grp = ctx.get("from_grp")
        pid = ctx.get("pid")
        if not path or not from_grp or not pid:
            return
        to_grp = safe_input(input, "bp_move_target_group", None)
        if not to_grp:
            return
        ok, msg = assign_plot(path, pid, from_grp, to_grp)
        ui.notification_show(msg, type="success" if ok else "warning")
        if ok:
            ui.modal_remove()
            _do_refresh_blueprint(path)

    # ══════════════════════════════════════════════════════════════════════
    # BP-META-1 — Manifest info: block form (ADR-082 Q7)
    # Reads/writes the top-level info: dict in the master manifest.
    # Edit mode requires manifest_edit_enabled; read-only view always shown.
    # ══════════════════════════════════════════════════════════════════════

    @output
    @render.ui
    def bp_meta_form_ui():
        """Read/edit form for manifest info: block. BP-META-1."""
        path = safe_input(input, "stored_manifest_selector", None)
        if not path or not Path(path).exists():
            return ui.div("Load a manifest first.", class_="ultra-small text-muted p-2")
        try:
            with open(path, encoding="utf-8") as f:
                raw = yaml.load(f, Loader=_IncludeLoader) or {}
        except Exception as e:
            return ui.div(f"Error: {e}", style="font-size:0.72rem;color:#d62828;padding:8px;")

        info = raw.get("info") or {}
        can_edit = bootloader.is_enabled("manifest_edit_enabled")

        name_val    = info.get("name", "")
        desc_val    = info.get("description", "")
        author_val  = info.get("author", "")
        version_val = info.get("version", "")
        tags_raw    = info.get("tags", [])
        tags_val    = ", ".join(tags_raw) if isinstance(tags_raw, list) else str(tags_raw)

        if not can_edit:
            # Read-only display
            def _row(label: str, val: str):
                return ui.div(
                    ui.tags.small(label, class_="text-muted d-block"),
                    ui.tags.span(val or "—", style="font-size:0.8rem;"),
                    class_="mb-2",
                )
            return ui.div(
                _row("Name", name_val),
                _row("Description", desc_val),
                _row("Author", author_val),
                _row("Version", version_val),
                _row("Tags", tags_val),
                ui.tags.small(
                    "Read-only. Enable developer mode to edit.",
                    class_="text-muted d-block mt-1",
                ),
                class_="p-2",
            )

        return ui.div(
            ui.input_text("bp_meta_name", "Name", value=name_val,
                          placeholder="Short display name"),
            ui.input_text_area("bp_meta_desc", "Description", value=desc_val,
                               rows=3, placeholder="What this pipeline analyses"),
            ui.input_text("bp_meta_author", "Author", value=author_val,
                          placeholder="Your name or team"),
            ui.input_text("bp_meta_version", "Version", value=version_val,
                          placeholder="e.g. 1.0.0"),
            ui.input_text("bp_meta_tags", "Tags (comma-separated)", value=tags_val,
                          placeholder="e.g. amr, salmonella, surveillance"),
            ui.input_action_button("btn_bp_meta_save", "Save to manifest",
                                   class_="btn-primary btn-sm w-100 mt-2"),
            class_="p-2",
        )

    @reactive.Effect
    @reactive.event(input.btn_bp_meta_save)
    def _handle_meta_save():
        """Write info: block back to the manifest file on disk. BP-META-1."""
        path = safe_input(input, "stored_manifest_selector", None)
        if not path or not Path(path).exists():
            ui.notification_show("No manifest loaded.", type="warning")
            return
        try:
            with open(path, encoding="utf-8") as f:
                raw = yaml.load(f, Loader=_IncludeLoader) or {}
        except Exception as e:
            ui.notification_show(f"Load error: {e}", type="error")
            return

        name    = (safe_input(input, "bp_meta_name", "") or "").strip()
        desc    = (safe_input(input, "bp_meta_desc", "") or "").strip()
        author  = (safe_input(input, "bp_meta_author", "") or "").strip()
        version = (safe_input(input, "bp_meta_version", "") or "").strip()
        tags_str = (safe_input(input, "bp_meta_tags", "") or "").strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

        info: dict = raw.get("info") or {}
        if name:
            info["name"] = name
        if desc:
            info["description"] = desc
        if author:
            info["author"] = author
        if version:
            info["version"] = version
        info["tags"] = tags

        raw["info"] = info
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(raw, f, Dumper=_IncludeDumper,
                          default_flow_style=False, sort_keys=False, allow_unicode=True)
            ui.notification_show("Manifest info saved.", type="message")
        except Exception as e:
            ui.notification_show(f"Save error: {e}", type="error")

    # ══════════════════════════════════════════════════════════════════════
    # BP-NEW-1 — Create new manifest from scratch (ADR-082 Q2)
    # Writes a minimal YAML stub to config/manifests/pipelines/ and
    # refreshes the manifest selector so the user can start editing.
    # ══════════════════════════════════════════════════════════════════════

    _SLUG_RE_NEW = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    @reactive.Effect
    @reactive.event(input.btn_bp_new_manifest)
    def _handle_new_manifest_btn():
        """Open the new-manifest modal. BP-NEW-1."""
        ui.modal_show(
            ui.modal(
                ui.input_text("bp_new_slug", "Manifest ID (snake_case)",
                              placeholder="e.g. my_analysis_v2"),
                ui.input_text("bp_new_display_name", "Display name",
                              placeholder="e.g. My Analysis V2"),
                ui.input_text_area("bp_new_desc", "Description (optional)",
                                   rows=2, placeholder="What this manifest analyses"),
                ui.input_text("bp_new_author", "Author (optional)",
                              placeholder="Your name or team"),
                ui.tags.small(
                    "Creates a minimal manifest stub in config/manifests/pipelines/.",
                    class_="text-muted d-block mt-1",
                ),
                title="Create New Manifest",
                footer=ui.div(
                    ui.input_action_button("btn_bp_new_submit", "Create",
                                           class_="btn-primary btn-sm"),
                    ui.input_action_button("btn_bp_new_cancel", "Cancel",
                                           class_="btn-secondary btn-sm ms-2"),
                ),
                easy_close=True,
            )
        )

    @reactive.Effect
    @reactive.event(input.btn_bp_new_cancel)
    def _handle_new_manifest_cancel():
        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.btn_bp_new_submit)
    def _handle_new_manifest_submit():
        """Write minimal manifest stub and refresh the selector. BP-NEW-1."""
        slug = (safe_input(input, "bp_new_slug", "") or "").strip()
        if not slug or not _SLUG_RE_NEW.match(slug):
            ui.notification_show(
                "Manifest ID must be snake_case (letters/digits/underscores, "
                "start with letter or underscore).",
                type="warning",
            )
            return

        config_dir = Path("config/manifests/pipelines")
        config_dir.mkdir(parents=True, exist_ok=True)
        dest = config_dir / f"{slug}.yaml"
        if dest.exists():
            ui.notification_show(
                f"Manifest '{slug}.yaml' already exists. Choose a different ID.",
                type="warning",
            )
            return

        display_name = (safe_input(input, "bp_new_display_name", "") or slug).strip()
        desc    = (safe_input(input, "bp_new_desc", "") or "").strip()
        author  = (safe_input(input, "bp_new_author", "") or "").strip()
        today   = datetime.now().strftime("%Y-%m-%d")

        stub: dict = {
            "info": {
                "name": display_name,
                "description": desc or "",
                "author": author or "",
                "version": "1.0.0",
                "created": today,
                "tags": [],
            },
            "data_schemas": {},
            "join_manifests": {},
            "analysis_groups": {},
        }

        try:
            with open(dest, "w", encoding="utf-8") as f:
                yaml.dump(stub, f, default_flow_style=False,
                          sort_keys=False, allow_unicode=True)
        except Exception as e:
            ui.notification_show(f"Create error: {e}", type="error")
            return

        ui.modal_remove()

        # Refresh the selector and select the new manifest
        all_yamls = sorted(config_dir.glob("*.yaml"))
        choices = [str(p) for p in all_yamls]
        ui.update_select("stored_manifest_selector",
                         choices=choices,
                         selected=str(dest))
        ui.notification_show(f"Manifest '{slug}.yaml' created.", type="message")
