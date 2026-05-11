"""libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py
Pure manifest introspection engine (ADR-045).

Public API
----------
build_sibling_map(manifest_path_str)
    Parse a master manifest WITHOUT resolving !include, then build:
    rel_path → {role, schema_id, schema_type, siblings, ingredients}

build_schema_registry(manifest_path_str, includes_map)
    Build a complete schema-level structural index:
    schema_id → {schema_type, input_fields, wrangling, output_fields, ...}

build_lineage_chain(selected_rel, ctx_map, target_ds_override=None)
    Construct an ordered list of components for the Lineage Rail.

load_fields_file(abs_path)
    Read a standalone fields YAML file, auto-unwrapping wrapper keys.

resolve_fields_for_schema(schema_id, ctx_map, inc_map, _stack=None)
    Walk ctx_map to find the output fields for schema_id (cycle-safe).

build_plot_lineage(plot_id, manifest_path)
    Backward trace: data sources → T1/T2 wrangling → join → plot spec.
    Used by export bundle lineage graph (ADR-074).

get_plot_ids_in_group(group_id, manifest_path)
    Forward trace: all plot IDs declared under analysis_groups[group_id].
    Used by export scope resolution (ADR-074).

generate_fork_yaml(schema_id, role, new_id, raw_config)
    Generate a YAML fragment for forking a manifest component.
    Used by the Blueprint Architect Visual Fork feature (BP-VISUAL-FORK-1).

Constraints (Two-Category Law — ADR-045)
-----------------------------------------
- Zero Shiny dependency: no import of shiny, reactive, render, or ui.
- Importable from headless scripts, test suites, and CLI tools without
  triggering any Shiny registration side-effects.
- All seven functions are pure (no global mutable state).
"""

from __future__ import annotations

# @deps
# provides: function:build_sibling_map, function:build_lineage_chain, function:build_schema_registry, function:load_fields_file, function:resolve_fields_for_schema, function:build_plot_lineage, function:get_plot_ids_in_group, function:generate_fork_yaml
# consumed_by: app/handlers/blueprint_handlers.py, app/handlers/home_theater.py, app/handlers/export_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-074
# @end_deps

from pathlib import Path

import yaml


# ── Public API ────────────────────────────────────────────────────────────────

def build_sibling_map(manifest_path_str: str) -> dict:
    """Parse a master manifest WITHOUT resolving !include, then build a map:
      rel_path → {role, schema_id, schema_type, siblings: {input_fields, output_fields, wrangling}}

    Uses a non-resolving subclass of SafeLoader so !include tags are captured
    as plain strings instead of being followed to disk.
    """
    class _CapLoader(yaml.SafeLoader):
        pass

    _MARK = "\x00INC\x00"

    def _capture(loader, node):
        return f"{_MARK}{loader.construct_scalar(node)}"

    # Override any previously registered !include handler on the subclass
    _CapLoader.add_constructor("!include", _capture)

    try:
        raw = Path(manifest_path_str).read_text(encoding="utf-8")
        tree = yaml.load(raw, Loader=_CapLoader)  # noqa: S506 – controlled loader
    except Exception:
        return {}

    if not isinstance(tree, dict):
        return {}

    ctx: dict = {}

    def _inc(val):
        if isinstance(val, str) and val.startswith(_MARK):
            return val[len(_MARK):]
        return None

    def _extract_ingredients(block: dict) -> list:
        """Extract ordered dataset_id list from an ingredients block."""
        raw = block.get("ingredients", [])
        if not isinstance(raw, list):
            return []
        ids = []
        for item in raw:
            if isinstance(item, dict):
                did = item.get("dataset_id")
                if did:
                    ids.append(did)
            elif isinstance(item, str):
                ids.append(item)
        return ids

    def _slot(block: dict, key: str):
        """Return the value for a manifest key as either:
          - a rel_path string  (when value is an !include marker)
          - {"inline": <val>}  (when value is defined inline and non-empty)
          - None               (key absent or empty list/None)
        This means the context map captures BOTH file-linked and inline content.
        """
        raw = block.get(key)
        inc_rel = _inc(raw)
        if inc_rel:
            return inc_rel           # file-linked — a rel_path string
        # Inline: non-None, non-empty list, non-empty dict
        if raw is not None and raw != [] and raw != {}:
            return {"inline": raw}   # inline content — a dict sentinel
        return None

    def _register(section_type: str, schema_id: str, block: dict,
                  ingredients: list | None = None):
        if not isinstance(block, dict):
            return
        inp = _slot(block, "input_fields")
        out = _slot(block, "output_fields")
        wrn = _slot(block, "wrangling")
        rec = _slot(block, "recipe")
        con = _slot(block, "final_contract")

        effective_out = out or con
        effective_wrn = wrn or rec
        sib = {"input_fields": inp, "output_fields": effective_out,
               "wrangling": effective_wrn}
        ings = ingredients or []

        is_join_step = section_type == "join_manifests"
        wrn_role = "join" if is_join_step else "wrangling"

        def _reg_if_file(slot_val, role):
            if isinstance(slot_val, str):
                ctx[slot_val] = {"role": role, "schema_id": schema_id,
                                 "schema_type": section_type, "siblings": sib,
                                 "ingredients": ings}

        _reg_if_file(inp, "input_fields")
        _reg_if_file(out, "output_fields")
        _reg_if_file(con, "output_fields")
        _reg_if_file(wrn, wrn_role)
        _reg_if_file(rec, wrn_role)

        # For inline manifests (no !include files) register the schema_id itself as
        # a navigable key so TubeMap clicks can find this entry via ctx_map lookup.
        # Only add if no file-path key was registered for this schema (avoids duplicate).
        if schema_id not in ctx:
            ctx[schema_id] = {"role": wrn_role, "schema_id": schema_id,
                              "schema_type": section_type, "siblings": sib,
                              "ingredients": ings}

    for section in ("data_schemas", "additional_datasets_schemas"):
        for sid, sdict in (tree.get(section) or {}).items():
            _register(section, sid, sdict)

    meta = tree.get("metadata_schema")
    if isinstance(meta, dict):
        _register("metadata_schema", "metadata_schema", meta)

    for aid, adict in (tree.get("join_manifests") or {}).items():
        ings = _extract_ingredients(adict) if isinstance(adict, dict) else []
        _register("join_manifests", aid, adict, ingredients=ings)

    # analysis_groups → plots: register each plot spec and optional pre_plot_wrangling
    for group_id, group_spec in (tree.get("analysis_groups") or {}).items():
        if not isinstance(group_spec, dict):
            continue
        for plot_id, plot_spec in (group_spec.get("plots") or {}).items():
            if not isinstance(plot_spec, dict):
                continue
            spec_rel = _inc(plot_spec.get("spec"))
            pre_wrn_rel = _inc(plot_spec.get("pre_plot_wrangling"))

            plot_entry = {
                "role": "plot_spec",
                "schema_id": plot_id,
                "schema_type": "plots",
                "group_id": group_id,
                "siblings": {"input_fields": None, "output_fields": None,
                             "wrangling": pre_wrn_rel},
                "ingredients": [],
            }
            if spec_rel:
                ctx[spec_rel] = plot_entry
            # Always register by plot_id so inline plots are navigable from TubeMap
            if plot_id not in ctx:
                ctx[plot_id] = plot_entry

            # Register the pre_plot_wrangling file as its own navigable node
            if pre_wrn_rel:
                ctx[pre_wrn_rel] = {
                    "role": "plot_wrangling",
                    "schema_id": plot_id,
                    "schema_type": "plots",
                    "group_id": group_id,
                    # plot_spec sibling stored so the chain can continue forward
                    "siblings": {"input_fields": None, "output_fields": None,
                                 "wrangling": spec_rel},
                    "ingredients": [],
                }

    return ctx


def build_lineage_chain(selected_rel: str, ctx_map: dict, target_ds_override: str | None = None) -> list[dict]:
    """
    Constructs an ordered list of components for the Lineage Rail.
    Strategy:
    1. From the selected node, walk *backward* to the earliest ancestor.
    2. Then walk *forward*.
    target_ds_override: optional ID to trigger plot ancestry lookup.
    """
    if selected_rel not in ctx_map:
        return []

    def _node(rel: str, is_active: bool) -> dict:
        e = ctx_map[rel]
        return {
            "rel": rel,
            "schema_id": e.get("schema_id", rel),
            "role": e.get("role", "unknown"),
            "label": e.get("schema_id", rel),
            "is_active": is_active,
        }

    # Build lookup indexes for fast traversal
    # schema_id → list of rels for that schema_id (different roles)
    by_schema: dict[str, list[str]] = {}
    for rel, e in ctx_map.items():
        sid = e.get("schema_id", "")
        by_schema.setdefault(sid, []).append(rel)

    # assembly schema_id → its assembly wrangling rel
    join_rels: dict[str, str] = {
        e["schema_id"]: rel
        for rel, e in ctx_map.items()
        if e.get("role") == "join"
    }

    # For each assembly schema_id, which plot specs reference it (via target_dataset)?
    # We can't read the plot spec files here (no inc_map), so we note plot_spec rels
    # and their group context — linking happens by schema_id match at display time.
    # Instead, walk forward from assembly via schema_id equality to plot_spec siblings.
    # plot_spec entries don't store target_dataset in ctx_map (it's inside the file).
    # So the chain stops at the assembly level unless we have the target_dataset.

    entry = ctx_map[selected_rel]
    role = entry.get("role", "unknown")
    schema_id = entry.get("schema_id", "")
    sib = entry.get("siblings", {})

    chain: list[dict] = []

    if role == "plot_wrangling":
        # Chain: [plot_wrangling, plot_spec]
        # siblings["wrangling"] stores the associated plot_spec rel_path
        spec_rel = sib.get("wrangling")
        chain = [_node(selected_rel, True)]
        if isinstance(spec_rel, str) and spec_rel in ctx_map:
            chain.append(_node(spec_rel, False))

    elif role == "plot_spec":
        # Chain: [Ancestors..., (pre_plot_wrangling)?, plot_spec(active)]
        target_ds = target_ds_override or entry.get("target_dataset")
        if target_ds:
            # Recursively find the "best" anchor/assembly node for this target
            origin_rels = by_schema.get(target_ds, [])
            priority = ["join", "output_fields", "wrangling", "input_fields"]
            best_origin = None
            for p in priority:
                match = [r for r in origin_rels if ctx_map[r]["role"] == p]
                if match:
                    best_origin = match[0]
                    break

            if best_origin:
                origin_chain = build_lineage_chain(best_origin, ctx_map)
                for node in origin_chain:
                    node["is_active"] = False
                    chain.append(node)

        pre_wrn_rel = sib.get("wrangling")
        if isinstance(pre_wrn_rel, str) and pre_wrn_rel in ctx_map:
            chain.append(_node(pre_wrn_rel, False))
        chain.append(_node(selected_rel, True))

    elif role == "join":
        # Chain: [ingredient_wranglings..., assembly, ?plots]
        for ing_id in entry.get("ingredients", []):
            ing_rels = by_schema.get(ing_id, [])
            # Prefer the wrangling file for each ingredient
            wrn_rels = [r for r in ing_rels if ctx_map[r]
                        ["role"] == "wrangling"]
            for r in (wrn_rels or ing_rels[:1]):
                chain.append(_node(r, r == selected_rel))
        chain.append(_node(selected_rel, True))
        # Add downstream output_fields node if present
        out_rel = sib.get("output_fields")
        if isinstance(out_rel, str) and out_rel in ctx_map:
            chain.append(_node(out_rel, False))

    elif role == "output_fields":
        # Walk backward: find the wrangling/assembly sibling for the same schema_id
        # then build that chain with output_fields appended
        wrn_rels = [r for r in by_schema.get(schema_id, [])
                    if ctx_map[r]["role"] in ("wrangling", "join")]
        if wrn_rels:
            # Recurse on the wrangling node, then replace its is_active with False
            sub = build_lineage_chain(wrn_rels[0], ctx_map)
            for node in sub:
                node["is_active"] = False
            chain = sub
            chain.append(_node(selected_rel, True))
        else:
            chain = [_node(selected_rel, True)]

    else:
        # input_fields or wrangling (Tier-1)
        # Chain: [input_fields, wrangling, ?assembly, ?output_fields]
        inp_rel = sib.get("input_fields")
        wrn_rel = sib.get("wrangling")
        out_rel = sib.get("output_fields")

        if isinstance(inp_rel, str) and inp_rel in ctx_map:
            chain.append(_node(inp_rel, inp_rel == selected_rel))
        if isinstance(wrn_rel, str) and wrn_rel in ctx_map:
            chain.append(_node(wrn_rel, wrn_rel == selected_rel))

        # Check if this schema_id is an ingredient in any assembly
        for join_sid, join_rel in join_rels.items():
            asm_entry = ctx_map[join_rel]
            if schema_id in asm_entry.get("ingredients", []):
                chain.append(_node(join_rel, False))
                asm_out = asm_entry["siblings"].get("output_fields")
                if isinstance(asm_out, str) and asm_out in ctx_map:
                    chain.append(_node(asm_out, False))
                # show first assembly only (branching handled by Rail UI)
                break

        if not chain:
            chain = [_node(selected_rel, True)]

        if isinstance(out_rel, str) and out_rel in ctx_map and not any(
                n["role"] in ("join", "output_fields") for n in chain):
            chain.append(_node(out_rel, False))

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped = []
    for node in chain:
        if node["rel"] not in seen:
            seen.add(node["rel"])
            deduped.append(node)

    return deduped


def build_schema_registry(manifest_path_str: str,
                           includes_map: dict) -> dict:
    """Build a complete schema-level structural index of a manifest.

    Unlike build_sibling_map (which indexes *file paths*), this maps:
      schema_id → {
        "schema_type": str,
        "input_fields":  str | {"inline": val} | None,
        "wrangling":     str | {"inline": val} | None,
        "output_fields": str | {"inline": val} | None,
        "ingredients":   list[str],        # assembly only
        "target_dataset": str | None,      # plot only (resolved from spec file)
        "group_id":      str | None,       # plot only
        "source":        dict | None,      # raw data source block
        "info":          dict | str | None,
      }

    Both !include references (stored as rel_path strings) and inline content
    (stored as {"inline": <value>}) are captured, giving a complete structural
    view of the manifest regardless of how authors have factored their YAML.
    """
    class _CapLoader(yaml.SafeLoader):
        pass

    _MARK = "\x00INC\x00"

    def _capture(loader, node):
        return f"{_MARK}{loader.construct_scalar(node)}"

    _CapLoader.add_constructor("!include", _capture)

    try:
        raw = Path(manifest_path_str).read_text(encoding="utf-8")
        tree = yaml.load(raw, Loader=_CapLoader)  # noqa: S506
    except Exception:
        return {}

    if not isinstance(tree, dict):
        return {}

    def _slot(val):
        """Convert a raw block value to either a rel_path, {"inline":<v>}, or None."""
        if val is None:
            return None
        if isinstance(val, str) and val.startswith(_MARK):
            return val[len(_MARK):]
        if val == [] or val == {}:
            return None
        return {"inline": val}

    def _extract_ingredients(block):
        raw = block.get("ingredients", []) if isinstance(block, dict) else []
        ids = []
        for item in (raw if isinstance(raw, list) else []):
            if isinstance(item, dict):
                did = item.get("dataset_id")
                if did:
                    ids.append(str(did))
            elif isinstance(item, str):
                ids.append(item)
        return ids

    def _resolve_target_dataset(spec_slot):
        """If spec_slot is a rel_path, read the file and extract target_dataset."""
        if spec_slot is None or isinstance(spec_slot, dict):
            return None
        abs_path = Path(includes_map.get(spec_slot, ""))
        if not abs_path.exists():
            return None
        try:
            content = yaml.safe_load(
                abs_path.read_text(encoding="utf-8")) or {}
            return content.get("target_dataset") if isinstance(content, dict) else None
        except Exception:
            return None

    reg: dict = {}

    def _add(schema_id, schema_type, block, group_id=None):
        if not isinstance(block, dict):
            return
        entry = {
            "schema_type":   schema_type,
            "input_fields":  _slot(block.get("input_fields")),
            "wrangling":     _slot(block.get("wrangling")),
            "output_fields": _slot(block.get("output_fields") or block.get("final_contract")),
            "recipe":        _slot(block.get("recipe")),
            "ingredients":   _extract_ingredients(block),
            "target_dataset": None,
            "group_id":      group_id,
            "source":        block.get("source") if not isinstance(
                block.get("source"), str) else None,
            "info":          block.get("info"),
        }
        reg[schema_id] = entry

    for section in ("data_schemas", "additional_datasets_schemas"):
        for sid, sdict in (tree.get(section) or {}).items():
            _add(sid, section, sdict)

    meta = tree.get("metadata_schema")
    if isinstance(meta, dict):
        _add("metadata_schema", "metadata_schema", meta)

    for aid, adict in (tree.get("join_manifests") or {}).items():
        _add(aid, "join_manifests", adict)

    for group_id, group_spec in (tree.get("analysis_groups") or {}).items():
        if not isinstance(group_spec, dict):
            continue
        for plot_id, plot_spec in (group_spec.get("plots") or {}).items():
            if not isinstance(plot_spec, dict):
                continue
            spec_slot = _slot(plot_spec.get("spec"))
            pre_wrn = _slot(plot_spec.get("pre_plot_wrangling"))
            target_ds = _resolve_target_dataset(spec_slot)
            reg[plot_id] = {
                "schema_type":    "plots",
                "input_fields":   None,   # resolved from target_dataset at display time
                "wrangling":      pre_wrn,
                "output_fields":  None,   # plots are terminals
                "recipe":         spec_slot,
                "ingredients":    [],
                "target_dataset": target_ds,
                "group_id":       group_id,
                "source":         None,
                "info":           plot_spec.get("info"),
            }

    return reg


def load_fields_file(abs_path: Path) -> dict | list:
    """Read a standalone fields YAML file.
    Unwraps a single redundant wrapper key (input_fields / output_fields)
    to mirror ConfigManager's ADR-014 auto-unnesting behaviour.
    """
    try:
        content = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    if isinstance(content, dict) and len(content) == 1:
        key = next(iter(content))
        if key in ("input_fields", "output_fields"):
            return content[key]
    return content


def resolve_fields_for_schema(schema_id: str, ctx_map: dict, inc_map: dict,
                               _stack: set | None = None) -> dict:
    """Walk ctx_map to find the output fields for schema_id.

    Priority:
      1. output_fields file (file-linked via !include)
      2. inline output_fields from siblings sentinel {"inline": {...}}
      3. input_fields file (fallback for raw source schemas)
      4. transparent assembly — merge ingredient output fields
      5. inline input_fields from siblings sentinel

    Returns an ADR-041 Rich Dict: {slug: {type, ...}} or empty dict.
    Cycle guard via _stack prevents infinite recursion.
    """
    if _stack is None:
        _stack = set()
    if schema_id in _stack:
        return {}
    _stack = _stack | {schema_id}  # immutable copy so siblings don't share state

    rels = [r for r, e in ctx_map.items() if e.get("schema_id") == schema_id]

    # Pass 1: explicit output_fields file
    for r in rels:
        if ctx_map[r].get("role") == "output_fields":
            ap = inc_map.get(r)
            if ap:
                f = load_fields_file(Path(ap))
                if f:
                    return f if isinstance(f, dict) else {}
            break

    # Pass 2: inline output_fields from siblings sentinel
    for r in rels:
        sib = ctx_map[r].get("siblings", {})
        out_slot = sib.get("output_fields")
        if isinstance(out_slot, dict) and "inline" in out_slot:
            inline_val = out_slot["inline"]
            if isinstance(inline_val, dict) and inline_val:
                return inline_val

    # Pass 3: input_fields file fallback
    for r in rels:
        if ctx_map[r].get("role") == "input_fields":
            ap = inc_map.get(r)
            if ap:
                f = load_fields_file(Path(ap))
                if f:
                    return f if isinstance(f, dict) else {}
            break

    # Pass 4: transparent assembly — merge ingredients' output fields
    for r in rels:
        if ctx_map[r].get("role") == "join":
            combined: dict = {}
            for ing_id in ctx_map[r].get("ingredients", []):
                combined.update(
                    resolve_fields_for_schema(ing_id, ctx_map, inc_map, _stack))
            if combined:
                return combined

    # Pass 5: inline input_fields from siblings sentinel
    for r in rels:
        sib = ctx_map[r].get("siblings", {})
        in_slot = sib.get("input_fields")
        if isinstance(in_slot, dict) and "inline" in in_slot:
            inline_val = in_slot["inline"]
            if isinstance(inline_val, dict) and inline_val:
                return inline_val

    return {}


# ── ADR-074 export / scope helpers ────────────────────────────────────────────

def get_plot_ids_in_group(group_id: str, manifest_path: str) -> list[str]:
    """Return all plot IDs declared under analysis_groups[group_id].

    str, str → list[str]

    Forward trace used by export scope resolution and test discovery.
    Returns [] when group_id is absent or the manifest cannot be parsed.
    ADR-074.
    """
    class _CapLoader(yaml.SafeLoader):
        pass

    # Capture !include values as plain strings — we only need the plot key names.
    _CapLoader.add_constructor("!include", lambda l, n: l.construct_scalar(n))

    try:
        raw = Path(manifest_path).read_text(encoding="utf-8")
        tree = yaml.load(raw, Loader=_CapLoader)  # noqa: S506
    except Exception:
        return []

    if not isinstance(tree, dict):
        return []

    group_spec = (tree.get("analysis_groups") or {}).get(group_id)
    if not isinstance(group_spec, dict):
        return []

    plots = group_spec.get("plots") or {}
    return list(plots.keys()) if isinstance(plots, dict) else []


def build_plot_lineage(plot_id: str, manifest_path: str) -> list[dict]:
    """Backward trace from a plot spec to its T1 data roots.

    str, str → list[dict]

    Returns an ordered list of step dicts representing the data pipeline
    from raw sources through T1/T2 wrangling, assembly (join), to the
    plot spec leaf.  T3 overlay nodes are appended by the caller
    (export_handlers.py).

    Step dict shape:
        {
          "step":      int,   # 1-based position in the chain
          "type":      str,   # "data_source" | "wrangling" | "join" | "plot_spec"
          "schema_id": str,   # ingredient / join / plot id
          "label":     str,   # human-readable label from manifest, else schema_id
          "rel":       str,   # include rel_path or source file path (empty if N/A)
        }

    Returns [] if plot_id is not found in any analysis_group.
    ADR-074.
    """
    manifest_dir = Path(manifest_path).parent

    class _CapLoader(yaml.SafeLoader):
        pass

    _MARK = "\x00INC\x00"

    def _capture(loader, node):
        return f"{_MARK}{loader.construct_scalar(node)}"

    _CapLoader.add_constructor("!include", _capture)

    try:
        raw = Path(manifest_path).read_text(encoding="utf-8")
        tree = yaml.load(raw, Loader=_CapLoader)  # noqa: S506
    except Exception:
        return []

    if not isinstance(tree, dict):
        return []

    def _rel_path(val) -> str | None:
        if isinstance(val, str) and val.startswith(_MARK):
            return val[len(_MARK):]
        return None

    # ── Locate the plot and resolve its target_dataset ────────────────────────
    target_dataset: str | None = None
    plot_label: str = plot_id
    found = False

    for _gid, group_spec in (tree.get("analysis_groups") or {}).items():
        if not isinstance(group_spec, dict):
            continue
        plots = group_spec.get("plots") or {}
        if plot_id not in plots:
            continue
        found = True
        plot_entry = plots[plot_id]
        if not isinstance(plot_entry, dict):
            break
        plot_label = plot_entry.get("label", plot_id)

        spec_val = plot_entry.get("spec")
        spec_rel = _rel_path(spec_val)
        if spec_rel:
            spec_abs = manifest_dir / spec_rel
            try:
                spec_content = yaml.safe_load(
                    spec_abs.read_text(encoding="utf-8")) or {}
                # ConfigManager auto-unnests a single "spec:" wrapper key
                if isinstance(spec_content, dict) and "spec" in spec_content:
                    spec_content = spec_content["spec"]
                if isinstance(spec_content, dict):
                    target_dataset = spec_content.get("target_dataset")
            except Exception:
                pass
        elif isinstance(spec_val, dict):
            target_dataset = spec_val.get("target_dataset")
        break

    if not found:
        return []

    # ── Trace backward using the sibling map ──────────────────────────────────
    ctx_map = build_sibling_map(manifest_path)
    steps: list[dict] = []

    def _step(type_: str, schema_id: str, label: str, rel: str = "") -> dict:
        return {
            "step": len(steps) + 1,
            "type": type_,
            "schema_id": schema_id,
            "label": label,
            "rel": rel,
        }

    def _source_path_for(sid: str) -> str:
        for section in ("data_schemas", "additional_datasets_schemas"):
            block = (tree.get(section) or {}).get(sid)
            if isinstance(block, dict):
                src = block.get("source") or {}
                if isinstance(src, dict):
                    return src.get("path") or ""
        if sid == "metadata_schema":
            meta = tree.get("metadata_schema")
            if isinstance(meta, dict):
                src = meta.get("source") or {}
                if isinstance(src, dict):
                    return src.get("path") or ""
        return ""

    if target_dataset:
        # Prefer a join entry; fall back to a direct data schema (T1-only path)
        join_rel = next(
            (r for r, e in ctx_map.items()
             if e.get("schema_id") == target_dataset and e.get("role") == "join"),
            None,
        )

        if join_rel:
            for ing_id in ctx_map[join_rel].get("ingredients", []):
                steps.append(_step("data_source", ing_id, ing_id,
                                   _source_path_for(ing_id)))
                wrn_rel = next(
                    (r for r, e in ctx_map.items()
                     if e.get("schema_id") == ing_id and e.get("role") == "wrangling"),
                    None,
                )
                if wrn_rel:
                    steps.append(_step("wrangling", ing_id,
                                       f"{ing_id} / wrangling", wrn_rel))
            steps.append(_step("join", target_dataset, target_dataset, join_rel))

        else:
            # Direct data schema — no assembly layer
            steps.append(_step("data_source", target_dataset, target_dataset,
                               _source_path_for(target_dataset)))
            wrn_rel = next(
                (r for r, e in ctx_map.items()
                 if e.get("schema_id") == target_dataset
                 and e.get("role") == "wrangling"),
                None,
            )
            if wrn_rel:
                steps.append(_step("wrangling", target_dataset,
                                   f"{target_dataset} / wrangling", wrn_rel))

    steps.append(_step("plot_spec", plot_id, plot_label))
    return steps


def generate_fork_yaml(
    schema_id: str,
    role: str,
    new_id: str,
    raw_config: dict,
) -> str:
    """Return a YAML fragment that adds a forked copy of schema_id to the manifest.

    The fragment targets the same top-level section as the original node.
    Forkable roles and target sections:

      wrangling / input_fields / output_fields
          → data_schemas (primary) or additional_datasets_schemas (fallback)
          Fork copies the source block and resets wrangling to empty tier1/tier2.

      join
          → join_manifests
          Fork copies ingredients list and resets recipe + final_contract.

      plot_spec
          → analysis_groups.<group_id>.plots
          Fork copies the spec dict under a new plot_id with a derived label.

    Returns an empty string when schema_id is not found or the role is not
    forkable (e.g., data_source, unknown).

    Designed to be pasted into the manifest YAML or written via
    _write_fork_to_manifest() in blueprint_handlers.py.
    """
    block: dict = {}

    if role in ("wrangling", "input_fields", "output_fields"):
        for section in ("data_schemas", "additional_datasets_schemas"):
            schema = (raw_config.get(section) or {}).get(schema_id)
            if isinstance(schema, dict):
                block = {
                    section: {
                        new_id: {
                            "source": dict(schema.get("source") or {}),
                            "input_fields": {},
                            "wrangling": {"tier1": [], "tier2": []},
                            "output_fields": {},
                        }
                    }
                }
                break

    elif role == "join":
        join_def = (raw_config.get("join_manifests") or {}).get(schema_id)
        if isinstance(join_def, dict):
            block = {
                "join_manifests": {
                    new_id: {
                        "ingredients": list(join_def.get("ingredients") or []),
                        "recipe": [],
                        "final_contract": {},
                    }
                }
            }

    elif role == "plot_spec":
        for grp_id, grp_val in (raw_config.get("analysis_groups") or {}).items():
            if not isinstance(grp_val, dict):
                continue
            plots = grp_val.get("plots") or {}
            if schema_id not in plots:
                continue
            plot_def = plots[schema_id]
            spec = (plot_def.get("spec") or {}) if isinstance(plot_def, dict) else {}
            block = {
                "analysis_groups": {
                    grp_id: {
                        "plots": {
                            new_id: {
                                "label": new_id.replace("_", " ").title(),
                                "spec": dict(spec) if isinstance(spec, dict) else {},
                            }
                        }
                    }
                }
            }
            break

    if not block:
        return ""
    return yaml.dump(block, default_flow_style=False, sort_keys=False, allow_unicode=True)
