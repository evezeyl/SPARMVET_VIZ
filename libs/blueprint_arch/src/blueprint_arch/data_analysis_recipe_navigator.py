"""libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py
Pure data analysis recipe introspection engine (ADR-045).

Public API
----------
build_sibling_map(data_analysis_recipe_path_str)
    Parse a master data analysis recipe WITHOUT resolving !include, then build:
    rel_path → {role, tier, schema_id, schema_type, siblings, ingredients}
    (`tier` is "tier1" or "tier2" for the file of one tier of a table or a join)

build_schema_registry(data_analysis_recipe_path_str, includes_map)
    Build a complete schema-level structural index:
    schema_id → {schema_type, input_fields, tier1, tier2, ...}

build_lineage_chain(selected_rel, ctx_map, target_ds_override=None)
    Construct an ordered list of components for the Lineage Rail.

load_fields_file(abs_path)
    Read a standalone fields YAML file, auto-unwrapping wrapper keys.

resolve_fields_for_schema(schema_id, ctx_map, inc_map, _stack=None)
    Walk ctx_map to find the output fields for schema_id (cycle-safe).

build_plot_lineage(plot_id, data_analysis_recipe_path)
    Backward trace: data sources → T1/T2 wrangling → join → plot.
    Used by export bundle lineage graph (ADR-074).

get_plot_ids_in_group(group_id, data_analysis_recipe_path)
    Forward trace: all plot IDs declared under analysis_groups[group_id].
    Used by export scope resolution (ADR-074).

generate_branch_plan(master_path, schema_id, role, new_id)
    Plan a node-level lineage bifurcation: shared upstream by !include reuse,
    divergent downstream as new empty fragment files wired into the master.
    Used by the Blueprint Architect Branch Node feature (BP-BRANCH-NODE-1,
    ADR-082 Q3). Replaces the legacy append-into-data-analysis-recipe Visual Fork.

Constraints (Two-Category Law — ADR-045)
-----------------------------------------
- Zero Shiny dependency: no import of shiny, reactive, render, or ui.
- Importable from headless scripts, test suites, and CLI tools without
  triggering any Shiny registration side-effects.
- All seven functions are pure (no global mutable state).
"""

from __future__ import annotations

# @deps
# provides: function:build_sibling_map (entry keys: role; tier = tier1 or tier2 for a tier file (new); schema_id; schema_type; siblings = input_fields/tier1/tier2 with no wrangling and no output_fields; ingredients; a plot entry is the plot itself, D-0250 D-0252), function:build_lineage_chain, function:build_schema_registry, function:load_fields_file, function:resolve_fields_for_schema, function:build_plot_lineage, function:get_plot_ids_in_group, function:generate_branch_plan (BP-BRANCH-NODE-1 — replaces generate_fork_yaml)
# consumes: libs/utils/src/utils/recipe_tiers.py
# consumed_by: app/handlers/blueprint_handlers.py, app/handlers/home_theater.py, app/handlers/export_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-074
# @end_deps

import re
from pathlib import Path

import yaml

from utils.recipe_tiers import step_list


# ── Public API ────────────────────────────────────────────────────────────────

def build_sibling_map(data_analysis_recipe_path_str: str) -> dict:
    """Parse a master data analysis recipe WITHOUT resolving !include, then build a map:
      rel_path → {role, tier, schema_id, schema_type, siblings: {input_fields, tier1, tier2}, ingredients}

    A table or a join writes each tier as its own key (`tier1`, `tier2`, D-0250); a tier that is an !include has its file
    registered (role "wrangling" for a table, "join" for a join, `tier` says which). A plot entry is the plot itself (D-0252):
    written inline it is registered by its id, written as `!include` its file is registered too.

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
        raw = Path(data_analysis_recipe_path_str).read_text(encoding="utf-8")
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
        """Return the value for a data analysis recipe key as either:
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
        tier1 = _slot(block, "tier1")
        tier2 = _slot(block, "tier2")
        sib = {"input_fields": inp, "tier1": tier1, "tier2": tier2}
        ings = ingredients or []

        is_join_step = section_type == "joins"
        wrn_role = "join" if is_join_step else "wrangling"

        def _reg_if_file(slot_val, role, tier=None):
            if isinstance(slot_val, str):
                entry = {"role": role, "schema_id": schema_id,
                         "schema_type": section_type, "siblings": sib,
                         "ingredients": ings}
                if tier:
                    entry["tier"] = tier
                ctx[slot_val] = entry

        _reg_if_file(inp, "input_fields")
        _reg_if_file(tier1, wrn_role, "tier1")
        _reg_if_file(tier2, wrn_role, "tier2")

        # For inline data analysis recipes (no !include files) register the schema_id itself as
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

    for aid, adict in (tree.get("joins") or {}).items():
        ings = _extract_ingredients(adict) if isinstance(adict, dict) else []
        _register("joins", aid, adict, ingredients=ings)

    # analysis_groups → plots: each plot entry is the plot (inline, or the whole entry in its own file)
    for group_id, group_spec in (tree.get("analysis_groups") or {}).items():
        if not isinstance(group_spec, dict):
            continue
        for plot_id, plot_entry in (group_spec.get("plots") or {}).items():
            entry_rel = _inc(plot_entry)
            if entry_rel is None and not isinstance(plot_entry, dict):
                continue
            plot_ctx = {
                "role": "plot_spec",
                "schema_id": plot_id,
                "schema_type": "plots",
                "group_id": group_id,
                "siblings": {"input_fields": None, "tier1": None, "tier2": None},
                "ingredients": [],
            }
            if entry_rel:
                ctx[entry_rel] = plot_ctx
            # Always register by plot_id so inline plots are navigable from TubeMap
            if plot_id not in ctx:
                ctx[plot_id] = plot_ctx

    return ctx


def build_lineage_chain(selected_rel: str, ctx_map: dict, target_ds_override: str | None = None) -> list[dict]:
    """
    Constructs an ordered list of components for the Lineage Rail.
    Strategy:
    1. From the selected node, walk *backward* to the earliest ancestor.
    2. Then walk *forward*.
    target_ds_override: optional ID to trigger plot ancestry lookup.

    A join reads the tier 1 of its ingredients (a table's tier 2 runs only where a plot reads the table directly), so the
    chain of a join lists the tier 1 of its ingredients, never their tier 2.
    """
    if selected_rel not in ctx_map:
        return []

    def _node(rel: str, is_active: bool) -> dict:
        e = ctx_map[rel]
        return {
            "rel": rel,
            "schema_id": e.get("schema_id", rel),
            "role": e.get("role", "unknown"),
            # the tier 2 file of a table or a join has the id of its table: the rail tells the two files apart
            "label": e.get("schema_id", rel) + (" (tier 2)" if e.get("tier") == "tier2" else ""),
            "is_active": is_active,
        }

    # Build lookup indexes for fast traversal
    # schema_id → list of rels for that schema_id (different roles)
    by_schema: dict[str, list[str]] = {}
    for rel, e in ctx_map.items():
        sid = e.get("schema_id", "")
        by_schema.setdefault(sid, []).append(rel)

    # the join of each schema id (the last one registered: the id itself when the join is written inline or has files)
    join_rels: dict[str, str] = {
        e["schema_id"]: rel
        for rel, e in ctx_map.items()
        if e.get("role") == "join"
    }

    # The plot entries of ctx_map do not carry `target_dataset` (it is inside the entry), so the chain of a plot
    # needs `target_ds_override` and stops at the plot without it.

    entry = ctx_map[selected_rel]
    role = entry.get("role", "unknown")
    schema_id = entry.get("schema_id", "")
    sib = entry.get("siblings", {})

    chain: list[dict] = []

    if role == "plot_spec":
        # Chain: [Ancestors..., plot(active)]
        target_ds = target_ds_override or entry.get("target_dataset")
        if target_ds:
            # Recursively find the "best" anchor/assembly node for this target
            origin_rels = by_schema.get(target_ds, [])
            priority = ["join", "wrangling", "input_fields"]
            best_origin = None
            for p in priority:
                match = [r for r in origin_rels
                         if ctx_map[r]["role"] == p and ctx_map[r].get("tier") != "tier2"]
                if match:
                    best_origin = match[0]
                    break

            if best_origin:
                origin_chain = build_lineage_chain(best_origin, ctx_map)
                for node in origin_chain:
                    node["is_active"] = False
                    chain.append(node)

        chain.append(_node(selected_rel, True))

    elif role == "join":
        # Chain: [ingredient_wranglings..., join tier 1, join tier 2]
        for ing_id in entry.get("ingredients", []):
            ing_rels = by_schema.get(ing_id, [])
            # Prefer the wrangling file for each ingredient: its tier 1 (a join never reads an ingredient's tier 2)
            wrn_rels = [r for r in ing_rels if ctx_map[r]["role"] == "wrangling"
                        and ctx_map[r].get("tier") != "tier2"]
            for r in (wrn_rels or ing_rels[:1]):
                chain.append(_node(r, r == selected_rel))
        own = [r for r in (sib.get("tier1"), sib.get("tier2")) if isinstance(r, str) and r in ctx_map]
        if selected_rel in own:
            for r in own:
                chain.append(_node(r, r == selected_rel))
        else:
            chain.append(_node(selected_rel, True))

    else:
        # input_fields or wrangling
        # Chain: [input_fields, tier 1, tier 2, ?join]
        inp_rel = sib.get("input_fields")
        wrn_rels = [r for r in (sib.get("tier1"), sib.get("tier2")) if isinstance(r, str) and r in ctx_map]

        if isinstance(inp_rel, str) and inp_rel in ctx_map:
            chain.append(_node(inp_rel, inp_rel == selected_rel))
        for wrn_rel in wrn_rels:
            chain.append(_node(wrn_rel, wrn_rel == selected_rel))

        # Check if this schema_id is an ingredient in any join
        for join_sid, join_rel in join_rels.items():
            asm_entry = ctx_map[join_rel]
            if schema_id in asm_entry.get("ingredients", []):
                chain.append(_node(join_rel, False))
                # show first join only (branching handled by Rail UI)
                break

        if not chain:
            chain = [_node(selected_rel, True)]

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped = []
    for node in chain:
        if node["rel"] not in seen:
            seen.add(node["rel"])
            deduped.append(node)

    return deduped


def build_schema_registry(data_analysis_recipe_path_str: str,
                           includes_map: dict) -> dict:
    """Build a complete schema-level structural index of a data analysis recipe.

    Unlike build_sibling_map (which indexes *file paths*), this maps:
      schema_id → {
        "schema_type": str,
        "input_fields":  str | {"inline": val} | None,
        "tier1":         str | {"inline": val} | None,
        "tier2":         str | {"inline": val} | None,
        "ingredients":   list[str],        # join only
        "target_dataset": str | None,      # plot only (inline, or read from the plot's own file)
        "group_id":      str | None,       # plot only
        "source":        dict | None,      # raw data source block
      }

    Both !include references (stored as rel_path strings) and inline content
    (stored as {"inline": <value>}) are captured, giving a complete structural
    view of the data analysis recipe regardless of how authors have factored their YAML.
    """
    class _CapLoader(yaml.SafeLoader):
        pass

    _MARK = "\x00INC\x00"

    def _capture(loader, node):
        return f"{_MARK}{loader.construct_scalar(node)}"

    _CapLoader.add_constructor("!include", _capture)

    try:
        raw = Path(data_analysis_recipe_path_str).read_text(encoding="utf-8")
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

    def _target_dataset_of(plot_entry):
        """`target_dataset` of a plot entry: written inline, or read from the entry's own file (None when it cannot be read)."""
        if isinstance(plot_entry, dict):
            return plot_entry.get("target_dataset")
        if isinstance(plot_entry, str) and plot_entry.startswith(_MARK):
            abs_path = Path(includes_map.get(plot_entry[len(_MARK):], ""))
            if not abs_path.is_file():
                return None
            try:
                content = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}
            except Exception:
                return None
            return content.get("target_dataset") if isinstance(content, dict) else None
        return None

    reg: dict = {}

    def _add(schema_id, schema_type, block, group_id=None):
        if not isinstance(block, dict):
            return
        entry = {
            "schema_type":   schema_type,
            "input_fields":  _slot(block.get("input_fields")),
            "tier1":         _slot(block.get("tier1")),
            "tier2":         _slot(block.get("tier2")),
            "ingredients":   _extract_ingredients(block),
            "target_dataset": None,
            "group_id":      group_id,
            "source":        block.get("source") if not isinstance(
                block.get("source"), str) else None,
        }
        reg[schema_id] = entry

    for section in ("data_schemas", "additional_datasets_schemas"):
        for sid, sdict in (tree.get(section) or {}).items():
            _add(sid, section, sdict)

    meta = tree.get("metadata_schema")
    if isinstance(meta, dict):
        _add("metadata_schema", "metadata_schema", meta)

    for aid, adict in (tree.get("joins") or {}).items():
        _add(aid, "joins", adict)

    for group_id, group_spec in (tree.get("analysis_groups") or {}).items():
        if not isinstance(group_spec, dict):
            continue
        for plot_id, plot_entry in (group_spec.get("plots") or {}).items():
            if not (isinstance(plot_entry, dict) or _slot(plot_entry) is not None):
                continue
            reg[plot_id] = {
                "schema_type":    "plots",
                "input_fields":   None,   # resolved from target_dataset at display time
                "tier1":          None,
                "tier2":          None,
                "ingredients":    [],
                "target_dataset": _target_dataset_of(plot_entry),
                "group_id":       group_id,
                "source":         None,
            }

    return reg


def load_fields_file(abs_path: Path) -> dict | list:
    """Read a standalone fields YAML file.
    Unwraps a single redundant `input_fields` wrapper key to mirror ConfigManager's
    ADR-014 auto-unnesting behaviour. `output_fields` is not a key of a recipe any more.
    """
    try:
        content = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    if isinstance(content, dict) and len(content) == 1:
        key = next(iter(content))
        if key == "input_fields":
            return content[key]
    return content


def resolve_fields_for_schema(schema_id: str, ctx_map: dict, inc_map: dict,
                               _stack: set | None = None) -> dict:
    """Walk ctx_map to find the fields of schema_id.

    Priority:
      1. input_fields file (file-linked via !include)
      2. transparent join — merge the fields of the ingredients
      3. inline input_fields from siblings sentinel

    Recipe format 1 has no `output_fields`: what a join publishes is its last step, so the fields of a join are those
    of its ingredients here (the columns the steps add or drop are not computed).

    Returns an ADR-041 Rich Dict: {slug: {type, ...}} or empty dict.
    Cycle guard via _stack prevents infinite recursion.
    """
    if _stack is None:
        _stack = set()
    if schema_id in _stack:
        return {}
    _stack = _stack | {schema_id}  # immutable copy so siblings don't share state

    rels = [r for r, e in ctx_map.items() if e.get("schema_id") == schema_id]

    # Pass 1: input_fields file
    for r in rels:
        if ctx_map[r].get("role") == "input_fields":
            ap = inc_map.get(r)
            if ap:
                f = load_fields_file(Path(ap))
                if f:
                    return f if isinstance(f, dict) else {}
            break

    # Pass 2: transparent join — merge ingredients' fields
    for r in rels:
        if ctx_map[r].get("role") == "join":
            combined: dict = {}
            for ing_id in ctx_map[r].get("ingredients", []):
                combined.update(
                    resolve_fields_for_schema(ing_id, ctx_map, inc_map, _stack))
            if combined:
                return combined

    # Pass 3: inline input_fields from siblings sentinel
    for r in rels:
        sib = ctx_map[r].get("siblings", {})
        in_slot = sib.get("input_fields")
        if isinstance(in_slot, dict) and "inline" in in_slot:
            inline_val = in_slot["inline"]
            if isinstance(inline_val, dict) and inline_val:
                return inline_val

    return {}


# ── ADR-074 export / scope helpers ────────────────────────────────────────────

def get_plot_ids_in_group(group_id: str, data_analysis_recipe_path: str) -> list[str]:
    """Return all plot IDs declared under analysis_groups[group_id].

    str, str → list[str]

    Forward trace used by export scope resolution and test discovery.
    Returns [] when group_id is absent or the data analysis recipe cannot be parsed.
    ADR-074.
    """
    class _CapLoader(yaml.SafeLoader):
        pass

    # Capture !include values as plain strings — we only need the plot key names.
    _CapLoader.add_constructor("!include", lambda l, n: l.construct_scalar(n))

    try:
        raw = Path(data_analysis_recipe_path).read_text(encoding="utf-8")
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


def build_plot_lineage(plot_id: str, data_analysis_recipe_path: str) -> list[dict]:
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
          "label":     str,   # human-readable label from data analysis recipe, else schema_id
          "rel":       str,   # include rel_path or source file path (empty if N/A)
        }

    Returns [] if plot_id is not found in any analysis_group.
    ADR-074.
    """
    data_analysis_recipe_dir = Path(data_analysis_recipe_path).parent

    class _CapLoader(yaml.SafeLoader):
        pass

    _MARK = "\x00INC\x00"

    def _capture(loader, node):
        return f"{_MARK}{loader.construct_scalar(node)}"

    _CapLoader.add_constructor("!include", _capture)

    try:
        raw = Path(data_analysis_recipe_path).read_text(encoding="utf-8")
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
        # The entry is the plot's content (D-0237): inline, or the whole entry in its own file (`p: !include plots/p.yaml`)
        entry_rel = _rel_path(plot_entry)
        if entry_rel:
            try:
                plot_entry = yaml.load((data_analysis_recipe_dir / entry_rel).read_text(encoding="utf-8"),
                                       Loader=_CapLoader)  # noqa: S506
            except Exception:
                plot_entry = None
        if not isinstance(plot_entry, dict):
            break
        plot_label = plot_entry.get("ui_label", plot_id)
        target_dataset = plot_entry.get("target_dataset")
        break

    if not found:
        return []

    # ── Trace backward using the sibling map ──────────────────────────────────
    ctx_map = build_sibling_map(data_analysis_recipe_path)
    steps: list[dict] = []

    def _step(type_: str, schema_id: str, label: str, rel: str = "") -> dict:
        return {
            "step": len(steps) + 1,
            "type": type_,
            "schema_id": schema_id,
            "label": label,
            "rel": rel,
        }

    def _block_of(sid: str):
        """The schema (or the metadata schema) with this id, as the recipe file has it; None when there is none."""
        block = None
        for section in ("data_schemas", "additional_datasets_schemas"):
            found = (tree.get(section) or {}).get(sid)
            if isinstance(found, dict):
                block = found
        if sid == "metadata_schema" and isinstance(tree.get("metadata_schema"), dict):
            block = tree["metadata_schema"]
        return block

    def _wrangling_label(sid: str) -> str:
        """`<id> / wrangling`, with a note when the schema has a tier-2 list (issue #77).

        A schema's tier 2 runs only where a plot reads the schema directly; a join reads its tier 1. The note says so in
        both places, so a node shared by both kinds of plot (the export deduplicates by id) is true for both."""
        block = _block_of(sid)
        tier2 = block.get("tier2") if isinstance(block, dict) else None
        rel = _rel_path(tier2)
        if rel:
            try:
                tier2 = yaml.load((data_analysis_recipe_dir / rel).read_text(encoding="utf-8"), Loader=_CapLoader)  # noqa: S506
            except Exception:
                tier2 = None
        if step_list({"tier2": tier2}, "tier2"):
            return f"{sid} / wrangling (tier 1; tier 2 only where {sid} is plotted directly)"
        return f"{sid} / wrangling"

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

    def _tier1_node(sid: str, role: str):
        """The node of the tier 1 of a table (role "wrangling") or a join (role "join"): its include file, else the id
        (written inline). Never the node of the tier 2: a join reads the tier 1 of its ingredients."""
        return next(
            (r for r, e in ctx_map.items()
             if e.get("schema_id") == sid and e.get("role") == role and e.get("tier") != "tier2"),
            None,
        )

    if target_dataset:
        # Prefer a join entry (the engine's order); fall back to a direct data schema
        join_rel = _tier1_node(target_dataset, "join")

        if join_rel:
            for ing_id in ctx_map[join_rel].get("ingredients", []):
                steps.append(_step("data_source", ing_id, ing_id,
                                   _source_path_for(ing_id)))
                wrn_rel = _tier1_node(ing_id, "wrangling")
                if wrn_rel:
                    steps.append(_step("wrangling", ing_id,
                                       _wrangling_label(ing_id), wrn_rel))
            steps.append(_step("join", target_dataset, target_dataset, join_rel))

        else:
            # Direct data schema, no assembly layer: its wrangling node holds its T1 and its T2 (issue #77)
            steps.append(_step("data_source", target_dataset, target_dataset,
                               _source_path_for(target_dataset)))
            wrn_rel = _tier1_node(target_dataset, "wrangling")
            if wrn_rel:
                steps.append(_step("wrangling", target_dataset,
                                   _wrangling_label(target_dataset), wrn_rel))

    steps.append(_step("plot_spec", plot_id, plot_label))
    return steps


# ── BP-BRANCH-NODE-1: node-level lineage bifurcation (ADR-082 Q3) ───────────────

_INC_MARK = "\x00INC\x00"


def _load_captured(raw: str):
    """Load YAML capturing every !include target as a marked string (non-resolving)."""
    class _CapLoader(yaml.SafeLoader):
        pass

    def _capture(loader, node):
        return f"{_INC_MARK}{loader.construct_scalar(node)}"

    _CapLoader.add_constructor("!include", _capture)
    return yaml.load(raw, Loader=_CapLoader)  # noqa: S506 – controlled loader


def _inc_path(val):
    """Return the !include rel-path if val is a captured marker, else None."""
    if isinstance(val, str) and val.startswith(_INC_MARK):
        return val[len(_INC_MARK):]
    return None


def _render_block_key(key: str, value, indent: int) -> str:
    """yaml.dump {key: value} and re-indent every line by `indent` spaces."""
    pad = " " * indent
    dumped = yaml.safe_dump(
        {key: value}, default_flow_style=False, sort_keys=False, allow_unicode=True
    ).rstrip("\n")
    return "\n".join((pad + line) if line else line for line in dumped.split("\n"))


def _key_line(line: str) -> str:
    """The line without a comment after its key (`joins:  # why` gives `joins:`): a note of the author must not hide the key."""
    return re.sub(r":\s+#.*$", ":", line.rstrip())


def _insert_after_top_level_anchor(raw: str, anchor: str, block_text: str) -> str | None:
    """Insert block_text immediately after a top-level key line `anchor` (col 0)."""
    lines = raw.split("\n")
    for i, line in enumerate(lines):
        if _key_line(line) == anchor and not line.startswith((" ", "\t")):
            return "\n".join(lines[:i + 1] + block_text.split("\n") + lines[i + 1:])
    return None


def _insert_into_group_plots(raw: str, group_id: str, block_text: str) -> str | None:
    """Insert block_text after the `plots:` line nested under `  <group_id>:`."""
    lines = raw.split("\n")
    in_group = False
    for i, line in enumerate(lines):
        stripped = _key_line(line).strip()
        # group header at indent 2
        if line.startswith("  ") and not line.startswith("   ") and stripped == f"{group_id}:":
            in_group = True
            continue
        if in_group:
            # a new indent-2 sibling ends the group before we found plots:
            if line.startswith("  ") and not line.startswith("   ") and stripped.endswith(":"):
                if stripped != "plots:":
                    return None
            if stripped == "plots:":
                return "\n".join(lines[:i + 1] + block_text.split("\n") + lines[i + 1:])
    return None


# The new, empty tier file of a branch: a tier is a mapping with its steps (D-0250); a flat list is refused by the format and by
# the engine. Tier 2 is not written: an absent tier 2 means the table of tier 2 equals the table of tier 1.
_EMPTY_TIER = "steps: []\n"


def _branch_label(source: dict, new_id: str) -> str:
    """The label of a branch: the label of what it branches from, else the new id in words, marked "(branch)"."""
    return f"{source.get('label') or new_id.replace('_', ' ').title()} (branch)"


def _plot_branch_label(entry: dict, new_id: str) -> str:
    """The `ui_label` of a branched plot: the label of the plot it branches from, marked "(branch)"."""
    return f"{entry.get('ui_label') or new_id.replace('_', ' ').title()} (branch)"


def _branch_error(msg: str) -> dict:
    return {"ok": False, "error": msg, "summary": "",
            "new_master_text": "", "fragments": []}


def generate_branch_plan(
    master_path: str,
    schema_id: str,
    role: str,
    new_id: str,
) -> dict:
    """Plan a node-level lineage bifurcation (ADR-082 Q3 / BP-BRANCH-NODE-1).

    Splits one lineage in two AT the selected node: everything upstream stays
    SHARED (reused by the same !include reference, or copied inline for small
    mappings like source/ingredients), and the divergent downstream is written
    as NEW empty fragment files wired into the master via fresh !include keys.
    This is the Bifurcation Point Rule (rules_data_engine.md) made interactive —
    the canonical example is Summary / Summary_quality (shared input_fields,
    divergent wrangling).

    What is written is recipe format 1: no `output_fields` key (the published
    columns are the last step of a join's tier 1), a `label` on the new schema
    or join, a `ui_label` on the new plot, and a tier as its own key, a mapping
    with `steps` (D-0250), never a flat list.

    Returns:
      {
        "ok": bool,
        "error": str,                # populated when ok is False
        "summary": str,              # human description for a notification
        "new_master_text": str,      # full master YAML with the branch inserted
        "fragments": [               # NEW empty fragment files to create on disk
            {"abs_path": str, "rel_include": str, "content": str}, ...
        ],
      }

    Role handling (the selected node's role decides what is shared vs divergent):
      wrangling / input_fields                   → branch a data_schema:
          SHARED  : source, null_values, strip (copied inline: the same file, read
                    in the same way; a key the source schema lacks is not invented),
                    input_fields (!include reused)
          DIVERGE : new tier 1 file (steps: [])
      join                                       → branch an assembly:
          SHARED  : ingredients (copied inline)
          DIVERGE : new tier 1 file (steps: [])
      plot_spec                                  → branch a plot (leaf node):
          SHARED  : target_dataset (carried inside the copied entry)
          SEED    : a COPY of the original entry under new_id, in its own file,
                    with the branch label as `ui_label` — a plot is a leaf, the
                    whole entry is the branch unit, and an empty plot cannot
                    render. (Distinct from the empty-seed rule for data_schemas.)

    Pure (no Shiny). Reads master_path with a non-resolving loader so !include
    references survive as strings, then performs a text-level insertion that
    preserves all existing !include tags untouched.
    """
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", new_id or ""):
        return _branch_error("New ID must be snake_case (letters, digits, underscores only).")

    mp = Path(master_path)
    if not master_path or not mp.exists():
        return _branch_error("Master data analysis recipe not found.")

    try:
        raw = mp.read_text(encoding="utf-8")
        tree = _load_captured(raw)
    except Exception as exc:
        return _branch_error(f"Cannot read data analysis recipe: {exc}")
    if not isinstance(tree, dict):
        return _branch_error("Data analysis recipe is not a valid YAML mapping.")

    master_dir = mp.parent
    basename = mp.stem

    # ── data_schema branch ──────────────────────────────────────────────────
    if role in ("wrangling", "input_fields"):
        section = None
        block = None
        for sec in ("data_schemas", "additional_datasets_schemas"):
            d = tree.get(sec) or {}
            if schema_id in d and isinstance(d[schema_id], dict):
                section, block = sec, d[schema_id]
                break
        if block is None:
            return _branch_error(f"Data schema '{schema_id}' not found.")
        if new_id in (tree.get(section) or {}):
            return _branch_error(f"ID '{new_id}' already exists in {section}.")

        wrn_rel = f"{basename}/wrangling/{new_id}_wrangling.yaml"

        lines = [f"  {new_id}:", _render_block_key("label", _branch_label(block, new_id), indent=4)]
        source = block.get("source")
        if source not in (None, {}, []):
            lines.append(_render_block_key("source", source, indent=4))
        # how the file is read is part of what is shared; a key the source schema lacks is not chosen here
        for key in ("null_values", "strip"):
            if key in block:
                lines.append(_render_block_key(key, block[key], indent=4))

        inp_raw = block.get("input_fields")
        inp_inc = _inc_path(inp_raw)
        if inp_inc:
            lines.append(f"    input_fields: !include '{inp_inc}'")
        elif inp_raw not in (None, {}, []):
            lines.append(_render_block_key("input_fields", inp_raw, indent=4))
        else:
            lines.append("    input_fields: {}")

        lines.append(f"    tier1: !include '{wrn_rel}'")
        block_text = "\n".join(lines)

        new_master = _insert_after_top_level_anchor(raw, f"{section}:", block_text)
        if new_master is None:
            return _branch_error(f"Could not locate '{section}:' in the data analysis recipe.")

        return {
            "ok": True, "error": "",
            "summary": (f"Branched {schema_id} -> {new_id}: shares source + "
                        "input_fields; new empty tier 1."),
            "new_master_text": new_master,
            "fragments": [
                {"abs_path": str(master_dir / wrn_rel), "rel_include": wrn_rel,
                 "content": _EMPTY_TIER},
            ],
        }

    # ── join / assembly branch ──────────────────────────────────────────────
    if role == "join":
        join_def = (tree.get("joins") or {}).get(schema_id)
        if not isinstance(join_def, dict):
            return _branch_error(f"Assembly '{schema_id}' not found in joins.")
        if new_id in (tree.get("joins") or {}):
            return _branch_error(f"ID '{new_id}' already exists in joins.")

        rec_rel = f"{basename}/assembly/{new_id}_assembly.yaml"

        lines = [f"  {new_id}:", _render_block_key("label", _branch_label(join_def, new_id), indent=4)]
        ingredients = join_def.get("ingredients")
        if ingredients not in (None, {}, []):
            lines.append(_render_block_key("ingredients", ingredients, indent=4))
        lines.append(f"    tier1: !include '{rec_rel}'")
        block_text = "\n".join(lines)

        new_master = _insert_after_top_level_anchor(raw, "joins:", block_text)
        if new_master is None:
            return _branch_error("Could not locate 'joins:' in the data analysis recipe.")

        return {
            "ok": True, "error": "",
            "summary": (f"Branched assembly {schema_id} -> {new_id}: shares "
                        "ingredients; new empty tier 1."),
            "new_master_text": new_master,
            "fragments": [
                {"abs_path": str(master_dir / rec_rel), "rel_include": rec_rel,
                 "content": _EMPTY_TIER},
            ],
        }

    # ── plot_spec branch (leaf duplication, shares target_dataset) ───────────
    if role == "plot_spec":
        group_id = None
        plot_def = None
        for gid, gval in (tree.get("analysis_groups") or {}).items():
            if not isinstance(gval, dict):
                continue
            plots = gval.get("plots") or {}
            if schema_id in plots and (isinstance(plots[schema_id], dict) or _inc_path(plots[schema_id])):
                group_id, plot_def = gid, plots[schema_id]
                break
        if plot_def is None:
            return _branch_error(f"Plot '{schema_id}' not found in any analysis_group.")
        if new_id in (((tree.get("analysis_groups") or {}).get(group_id) or {}).get("plots") or {}):
            return _branch_error(f"Plot ID '{new_id}' already exists in group '{group_id}'.")

        entry_rel = f"{basename}/plots/{new_id}.yaml"

        # Seed the new plot with a COPY of the original entry (the whole entry is the plot, D-0252), in its own file.
        entry_inc = _inc_path(plot_def)
        if entry_inc:
            try:
                src_entry_text = (master_dir / entry_inc).read_text(encoding="utf-8")
                src_entry = _load_captured(src_entry_text)
            except Exception as exc:
                return _branch_error(f"Cannot read source plot '{entry_inc}': {exc}")
            if not isinstance(src_entry, dict) or not src_entry:
                return _branch_error(f"Plot '{schema_id}' has no usable content to branch.")
            # the file keeps its comments; only the line of the short name changes, so that the two plots can be told apart
            entry_text, changed = re.subn(
                r"(?m)^ui_label:.*$", lambda _m: _render_block_key("ui_label", _plot_branch_label(src_entry, new_id), indent=0),
                src_entry_text, count=1)
            if not changed:
                return _branch_error(f"Plot '{schema_id}': the file '{entry_inc}' has no `ui_label:` line at its root, "
                                     "so the branch cannot name itself. Write the short name of the plot there first.")
        elif isinstance(plot_def, dict) and plot_def:
            if "ui_label" not in plot_def:
                return _branch_error(f"Plot '{schema_id}' has no `ui_label`, so the branch cannot name itself.")
            # the new file holds the entry itself: an included file has no wrapper key (spec 6.1, check F01)
            entry_text = yaml.safe_dump(
                {**plot_def, "ui_label": _plot_branch_label(plot_def, new_id)},
                default_flow_style=False, sort_keys=False, allow_unicode=True)
        else:
            return _branch_error(f"Plot '{schema_id}' has no usable content to branch.")

        block_text = f"      {new_id}: !include '{entry_rel}'"

        new_master = _insert_into_group_plots(raw, group_id, block_text)
        if new_master is None:
            return _branch_error(
                f"Could not locate the 'plots:' block under group '{group_id}'.")

        return {
            "ok": True, "error": "",
            "summary": (f"Branched plot {schema_id} -> {new_id} in group "
                        f"'{group_id}': shares target_dataset (entry copied)."),
            "new_master_text": new_master,
            "fragments": [
                {"abs_path": str(master_dir / entry_rel), "rel_include": entry_rel,
                 "content": entry_text},
            ],
        }

    return _branch_error(
        f"Role '{role}' is not branchable. Select a data schema, assembly, or plot node.")
