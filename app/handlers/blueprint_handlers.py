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
# provides: function:define_server (blueprint_handlers)
# consumes: libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py, app/modules/orchestrator.py, libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py, libs/utils/src/utils/config_loader.py
# consumed_by: app/src/server.py
# doc: .antigravity/knowledge/architecture_decisions.md#ADR-039, .antigravity/knowledge/architecture_decisions.md#ADR-045
# @end_deps

import io
import re
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
from utils.config_loader import ConfigManager


def define_server(input, output, session, *,
                  bootloader, wrangle_studio, orchestrator, safe_input,
                  includes_map, component_ctx_map, schema_registry):
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
    """

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
                        print(f"🚀 [Architect] Materializing join '{schema_id}'")
                        orchestrator.materialize_tier1(
                            project_id=bp_project_id,
                            collection_id=schema_id,
                            output_path=out_p
                        )
                        wrangle_studio.active_anchor_path.set(str(out_p))
                    except Exception as e:
                        print(f"⚠️ Join materialization failed: {e}")

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
                            print(f"🚀 [Architect] Materializing '{target_ds}' from '{bp_project_id}'")
                            orchestrator.materialize_tier1(
                                project_id=bp_project_id,
                                collection_id=target_ds,
                                output_path=out_p
                            )
                            wrangle_studio.active_anchor_path.set(str(out_p))
                        except Exception as e:
                            print(f"⚠️ Surgical materialization failed: {e}")

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
                            print(f"⚠️ plot_wrangling materialization failed: {e}")

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
                    print(f"🚀 [Architect Mode B] Materializing join '{selected}'")
                    orchestrator.materialize_tier1(
                        project_id=bp_project_id,
                        collection_id=selected,
                        output_path=out_p
                    )
                    wrangle_studio.active_anchor_path.set(str(out_p))
                except Exception as e:
                    print(f"⚠️ Join materialization failed (Mode B): {e}")
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
                        print(f"⚠️ Plot materialization failed (Mode B): {_me}")
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
        """Thin wrapper — reads Shiny inputs and delegates to _do_load_component."""
        master_path = input.stored_manifest_selector()
        selected    = input.dataset_pipeline_selector()
        if not master_path or not selected:
            return
        _do_load_component(
            master_path, selected,
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

    @render.download(filename=lambda: f"exported_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml")
    def btn_download_manifest():
        nodes = wrangle_studio.logic_stack.get()
        manifest_data = {"wrangling": {"tier1": [], "tier2": [], "tier3": nodes}}
        buf = io.StringIO()
        yaml.dump(manifest_data, buf, default_flow_style=False, sort_keys=False)
        yield buf.getvalue()
