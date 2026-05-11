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
# provides: function:define_server (blueprint_handlers), output:blueprint_agent_panel_ui, effect:_bp_apply_node_handler, effect:_bp_save_yaml_hatch, effect:_load_component_from_selection
# consumes: libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py, libs/blueprint_arch/src/blueprint_arch/agent_adapter.py, libs/blueprint_arch/src/blueprint_arch/agent_context.py, libs/blueprint_arch/src/blueprint_arch/agent_tools.py, libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py, app/modules/orchestrator.py, libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py, libs/utils/src/utils/config_loader.py
# consumes: libs/blueprint_arch/src/blueprint_arch/schema_registry.py (get_action_catalog — BP-FORMS-1)
# consumes: libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-BLUEPRINT-1)
# consumes: reactive.Value:selected_lineage_rel (passed from server.py — BP-LINEAGE-NAV-1; _load_component_from_selection watches it)
# consumed_by: app/src/server.py, app/handlers/home_theater.py (ui.output_ui("blueprint_agent_panel_ui"))
# doc: .claude/knowledge/architecture_decisions.md#ADR-039, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-075, .claude/knowledge/architecture_decisions.md#ADR-076
# @end_deps

import asyncio
import io
import json
import re
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path

import yaml
from shiny import reactive, render, ui

from blueprint_arch.manifest_navigator import (
    build_lineage_chain,
    build_schema_registry,
    build_sibling_map,
    load_fields_file,
    resolve_fields_for_schema,
)
from blueprint_arch.blueprint_mapper import BlueprintMapper
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

    # ── Local helpers (pure logic, no Shiny decorators) ──────────────────────

    def _parse_logic_to_nodes(wrangling, source_name):
        """
        Normalizes potentially flat manifest nodes into structured UI nodes.
        ADR-031: Supports both Structure (params: {}) and Flat (top-level keys) formats.
        """
        nodes = []
        raw_list = []

        if isinstance(wrangling, list):
            raw_list = wrangling
        elif isinstance(wrangling, dict):
            for tier in ["tier1", "tier2", "tier3"]:
                raw_list.extend(wrangling.get(tier, []))

        for node in raw_list:
            if not isinstance(node, dict):
                continue
            n = node.copy()
            action = n.pop("action", "unknown_action")
            comment = n.pop("comment", source_name)
            params = n.pop("params", n)
            nodes.append({"action": action, "params": params, "comment": comment})

        return nodes

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

    # --- 🧬 Blueprint Architect Visual Sync (ADR-039) ---
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

    # --- 🏗️ Phase 18: Wrangle Studio Manifest Management ---
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
                    display = f"{ctx_entry.get('schema_id', abs_path.stem)} — {ctx_entry.get('role', '?')}"
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
                    inline_groups.setdefault("additional_datasets_schemas", {})[sid] = f"{sid} — wrangling"
                for sid in raw.get("join_manifests", {}):
                    inline_groups.setdefault("join_manifests", {})[sid] = f"{sid} — join"
                ag = raw.get("analysis_groups", {})
                for grp, gspec in ag.items():
                    if isinstance(gspec, dict):
                        for pid in gspec.get("plots", {}):
                            inline_groups.setdefault(f"plots/{grp}", {})[pid] = f"{pid} — plot_spec"
                if inline_groups:
                    ui.update_select("dataset_pipeline_selector", choices=inline_groups)
                else:
                    ui.update_select("dataset_pipeline_selector",
                                     choices=["No components found"])

            # UX-NOTIF-3: Project-load notification — surface component count on manifest reload
            manifest_name = Path(path).name
            n_components = len(ctx_map) if ctx_map else sum(len(v) for v in groups.values())
            ui.notification_show(
                f"Blueprint: {manifest_name} ({n_components} component(s))",
                type="message",
                duration=4,
            )

        except Exception as e:
            print(f"[_update_dataset_pipelines] Error: {e}")
            ui.update_select("dataset_pipeline_selector",
                             choices=["⚠️ Error – see console"])

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
        path_str = input.stored_manifest_selector()
        if not path_str or not Path(path_str).exists():
            return
        try:
            with open(path_str, "r") as f:
                content = yaml.safe_load(f) or {}
            nodes = wrangle_studio.logic_stack.get()
            if "wrangling" not in content:
                content["wrangling"] = {}
            content["wrangling"]["tier1"] = []
            content["wrangling"]["tier2"] = []
            content["wrangling"]["tier3"] = nodes
            with open(path_str, "w") as f:
                yaml.dump(content, f, default_flow_style=False, sort_keys=False)
            ui.notification_show(
                f"✅ Saved to {Path(path_str).name}", type="success")
        except Exception as e:
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
        action_name = node.get("action", "")

        try:
            from blueprint_arch.schema_registry import get_action_catalog
            catalog = get_action_catalog()
            ui_schema = catalog.get(action_name, {})
        except Exception:
            ui_schema = {}

        params_schema = ui_schema.get("params", {})
        new_comment = safe_input(input, "bp_form_comment", node.get("comment", ""))
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
                val = safe_input(input, input_id, "")
                if val:
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

        updated = list(nodes)
        updated[idx] = {
            "action": action_name,
            "params": new_params,
            "comment": new_comment,
        }
        wrangle_studio.logic_stack.set(updated)

        # Mark downstream nodes as schema-stale after edit
        wrangle_studio.invalidated_from.set(
            idx + 1 if idx + 1 < len(updated) else None
        )

        ui.notification_show(
            f"Step {idx + 1} ({action_name}) updated.", type="message"
        )

    @render.download(filename=lambda: f"exported_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml")
    def btn_download_manifest():
        nodes = wrangle_studio.logic_stack.get()
        manifest_data = {"wrangling": {"tier1": [], "tier2": [], "tier3": nodes}}
        buf = io.StringIO()
        yaml.dump(manifest_data, buf, default_flow_style=False, sort_keys=False)
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
