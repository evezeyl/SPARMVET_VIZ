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

Constraints (Two-Category Law — ADR-045)
-----------------------------------------
- Zero Shiny dependency: no import of shiny, reactive, render, or ui.
- Importable from headless scripts, test suites, and CLI tools without
  triggering any Shiny registration side-effects.
- All five functions are pure (no global mutable state).
"""

from __future__ import annotations

# @deps
# provides: function:build_sibling_map, function:build_lineage_chain, function:build_schema_registry, function:load_fields_file, function:resolve_fields_for_schema
# consumed_by: app/handlers/blueprint_handlers.py, app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045
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
