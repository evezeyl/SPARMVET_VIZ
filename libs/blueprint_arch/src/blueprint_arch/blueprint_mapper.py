# libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py

# @deps
# provides: class:BlueprintMapper, constant:_CY_COLOURS
# consumed_by: app/handlers/blueprint_handlers.py
# doc: .claude/rules/rules_ui_dashboard.md
# @end_deps

import json
import re
from pathlib import Path
from typing import Dict, List, Optional


# ── Cytoscape node/edge colours ───────────────────────────────────────────────
_CY_COLOURS = {
    "trunk":   {"bg": "#345beb", "border": "#2a4bc4", "text": "#ffffff"},
    "add":     {"bg": "#6c757d", "border": "#495057", "text": "#ffffff"},
    "meta":    {"bg": "#fd7e14", "border": "#dc6a0d", "text": "#ffffff"},
    "wrangle": {"bg": "#ffc107", "border": "#e0a800", "text": "#212529"},
    "branch":  {"bg": "#9c27b0", "border": "#7b1fa2", "text": "#ffffff"},
    "plot":    {"bg": "#10a395", "border": "#0d8a7e", "text": "#ffffff"},
    "info":    {"bg": "#eef0fb", "border": "#345beb", "text": "#1a1a1a"},
}

# Each tier maps to a numeric rank used by dagre for lane ordering (LR layout)
# Lower rank = further left (earlier in pipeline)
_TIER_RANK = {
    "trunk":   0,
    "add":     0,
    "meta":    0,
    "wrangle": 1,   # tier-1 wrangling
    "branch":  2,   # assembly join
    "plot":    3,
}


class BlueprintMapper:
    """
    [ADR-039] Generates a DAG-based 'TubeMap' visualization for SPARMVET manifests.

    Parses the full manifest structure (data_schemas, additional_datasets_schemas,
    metadata_schema, join_manifests, and plots flattened by ConfigManager from
    analysis_groups) and outputs:
      - generate_mermaid()      → Mermaid LR DAG string (legacy, kept for reference)
      - generate_cy_elements()  → Cytoscape.js elements JSON (primary, tube-map UI)

    IMPORTANT: Pass raw_config from ConfigManager (not yaml.safe_load) so that:
      - !include tags are resolved
      - analysis_groups plots are flattened into raw_config['plots'] with target_dataset

    Node types:
      trunk    (blue)   — raw data source (data_schemas)
      wrangle  (yellow) — wrangling step
      branch   (purple) — join_manifests join node
      plot     (green)  — terminal plot node
      add      (grey)   — additional_datasets_schemas
      meta     (orange) — metadata_schema
    """

    def __init__(self, raw_config: Dict, active_node: Optional[str] = None):
        self.cfg = raw_config
        self.nodes: List[str] = []
        self.edges: List[str] = []
        self.style_classes: List[str] = []
        self.active_node = active_node

    def _get_label(self, node_id: str, details) -> str:
        """Safely extracts a short display label from node details."""
        if not isinstance(details, dict):
            return node_id
        info = details.get("info", {})
        if isinstance(info, str):
            return info[:35] if len(info) > 35 else info
        elif isinstance(info, dict):
            return info.get("display_name", info.get("sub_category", info.get("title", node_id)))
        return details.get("description", node_id)[:35] if isinstance(
            details.get("description"), str) else node_id

    def _safe_node_id(self, raw_id: str) -> str:
        """Sanitize node IDs for Mermaid compatibility."""
        return re.sub(r'[^A-Za-z0-9_]', '_', raw_id)

    def _n(self, sid: str, suffix: str) -> str:
        """Build a composite Mermaid node ID: <safe_schema_id>__<suffix>"""
        return f"{self._safe_node_id(sid)}__{suffix}"

    def generate_mermaid(self) -> str:
        """
        Build a fully structure-aware Mermaid LR DAG.

        Each data schema is rendered as a mini-chain:
            [Source] --> [Wrangling] --> (Assembly) --> [[Plot]]

        All nodes are clickable and emit their schema_id to the Shiny bridge.
        """
        self.nodes = []
        self.edges = []
        self.style_classes = []
        _clickable: list = []   # (mermaid_node_id, schema_id) pairs
        all_known: set = set()

        def _add_node(mermaid_id: str, defn: str, css_class: str, schema_id: str):
            self.nodes.append(defn)
            self.style_classes.append(f'class {mermaid_id} {css_class}')
            all_known.add(mermaid_id)
            _clickable.append((mermaid_id, schema_id))

        def _add_edge(a: str, b: str):
            self.edges.append(f'{a} --> {b}')

        # ── 1. Data Schemas ────────────────────────────────────────────────────
        schemas = self.cfg.get("data_schemas", {})
        for sid, details in schemas.items():
            safe = self._safe_node_id(sid)
            label = self._get_label(sid, details)
            # Source node
            _add_node(safe, f'{safe}(["{label}\\nSource"])', "trunk", sid)
            # Wrangling node (always present — may be inline or file)
            has_wrn = isinstance(details, dict) and bool(
                details.get("wrangling") or details.get("recipe"))
            wrn_id = self._n(sid, "wrn")
            if has_wrn:
                _add_node(wrn_id, f'{wrn_id}["{sid}\\nWrangling"]', "wrangle", sid)
                _add_edge(safe, wrn_id)
            else:
                # passthrough — source connects directly downstream
                wrn_id = safe

        # ── 2. Additional Datasets ─────────────────────────────────────────────
        add_schemas = self.cfg.get("additional_datasets_schemas", {})
        for aid, details in add_schemas.items():
            safe = self._safe_node_id(aid)
            label = self._get_label(aid, details)
            _add_node(safe, f'{safe}(["{label}\\nAdd Data"])', "add", aid)
            has_wrn = isinstance(details, dict) and bool(
                details.get("wrangling") or details.get("recipe"))
            wrn_id = self._n(aid, "wrn")
            if has_wrn:
                _add_node(wrn_id, f'{wrn_id}["{aid}\\nWrangling"]', "wrangle", aid)
                _add_edge(safe, wrn_id)

        # ── 3. Metadata Schema ─────────────────────────────────────────────────
        meta = self.cfg.get("metadata_schema", {})
        if meta:
            _add_node("metadata_schema",
                      'metadata_schema(["Metadata\\nSchema"])', "meta", "metadata_schema")
            has_wrn = isinstance(meta, dict) and bool(
                meta.get("wrangling") or meta.get("recipe"))
            if has_wrn:
                wrn_id = self._n("metadata_schema", "wrn")
                _add_node(wrn_id, f'{wrn_id}["metadata_schema\\nWrangling"]',
                          "wrangle", "metadata_schema")
                _add_edge("metadata_schema", wrn_id)

        # ── 4. Assembly Manifests ──────────────────────────────────────────────
        join_defs = self.cfg.get("join_manifests", {})

        def _upstream_node(parent_raw: str) -> str:
            """Return the last node in the parent schema's chain."""
            safe = self._safe_node_id(parent_raw)
            wrn_id = self._n(parent_raw, "wrn")
            return wrn_id if wrn_id in all_known else safe

        for asid, details in join_defs.items():
            safe = self._safe_node_id(asid)
            _add_node(safe, f'{safe}{{"{asid}\\nJoin"}}', "branch", asid)

            ingredients = []
            if isinstance(details, dict):
                raw_ing = details.get("ingredients", [])
                for ing in raw_ing:
                    if isinstance(ing, dict):
                        did = ing.get("dataset_id", "")
                        if did:
                            ingredients.append(did)
                    elif isinstance(ing, str):
                        ingredients.append(ing)

            for parent_raw in ingredients:
                up = _upstream_node(parent_raw)
                _add_edge(up, safe)

            # Assembly wrangling/recipe node
            has_wrn = isinstance(details, dict) and bool(
                details.get("wrangling") or details.get("recipe"))
            if has_wrn:
                wrn_id = self._n(asid, "wrn")
                _add_node(wrn_id, f'{wrn_id}["{asid}\\nJoin Wrangling"]',
                          "wrangle", asid)
                _add_edge(safe, wrn_id)

        # ── 5. Plots ───────────────────────────────────────────────────────────
        analysis_groups = self.cfg.get("analysis_groups", {})
        plots_flat = self.cfg.get("plots", {})

        plot_to_group: dict = {}
        for group_name, group_spec in analysis_groups.items():
            if isinstance(group_spec, dict):
                for pid in group_spec.get("plots", {}).keys():
                    plot_to_group[pid] = group_name

        # Also pick up target_dataset from analysis_groups directly (inline manifests
        # don't go through ConfigManager flattening so plots_flat may be empty)
        inline_plots: dict = {}
        for group_name, group_spec in analysis_groups.items():
            if isinstance(group_spec, dict):
                for pid, pspec in group_spec.get("plots", {}).items():
                    if pid not in plots_flat:
                        inline_plots[pid] = pspec if isinstance(pspec, dict) else {}

        all_plots = {**plots_flat, **inline_plots}

        subgraphs: dict = {}
        for pid, pspec in all_plots.items():
            safe_pid = self._safe_node_id(pid)
            label = pid.replace("_", " ").title()
            node_def = f'{safe_pid}[["{label}\\nPlot"]]'
            self.style_classes.append(f'class {safe_pid} plot')
            all_known.add(safe_pid)
            _clickable.append((safe_pid, pid))

            group_name = plot_to_group.get(pid, "Ungrouped")
            subgraphs.setdefault(group_name, []).append(node_def)

            target_raw = None
            if isinstance(pspec, dict):
                target_raw = (pspec.get("target_dataset")
                              or pspec.get("join_id"))

            if target_raw:
                # Connect from assembly wrangling output if present, else assembly
                asm_wrn = self._n(target_raw, "wrn")
                up = asm_wrn if asm_wrn in all_known else self._safe_node_id(target_raw)
                self.edges.append(f'{up} --> {safe_pid}')
            else:
                info_id = f"INFO_{safe_pid}"
                self.nodes.append(
                    f'{info_id}["INFO: {pid}\\nSet target_dataset"]')
                self.style_classes.append(f"class {info_id} info")
                self.edges.append(f"{info_id} -.-> {safe_pid}")

        # ── Build Mermaid string ───────────────────────────────────────────────
        lines = [
            "graph LR",
            "%% Styling",
            "classDef trunk   fill:#345beb,stroke:#fff,stroke-width:2px,color:#fff",
            "classDef add     fill:#6c757d,stroke:#fff,stroke-width:2px,color:#fff",
            "classDef meta    fill:#fd7e14,stroke:#fff,stroke-width:2px,color:#fff",
            "classDef wrangle fill:#ffc107,stroke:#555,stroke-width:1px,color:#212529",
            "classDef branch  fill:#9c27b0,stroke:#fff,stroke-width:2px,color:#fff",
            "classDef plot    fill:#10a395,stroke:#fff,stroke-width:2px,color:#fff",
            "classDef info    fill:#eef0fb,stroke:#345beb,stroke-width:1px,color:#1a1a1a",
            "classDef activeNode stroke:#212529,stroke-width:4px,stroke-dasharray:5 5",
            "%% Nodes",
        ]
        lines.extend(self.nodes)

        for group_name, group_nodes in subgraphs.items():
            safe_group = self._safe_node_id(group_name)
            lines.append(f'subgraph {safe_group}["{group_name}"]')
            lines.extend(f'  {n}' for n in group_nodes)
            lines.append("end")

        lines.append("%% Edges")
        lines.extend(self.edges)
        lines.append("%% Classes")
        lines.extend(self.style_classes)

        if self.active_node:
            safe_active = self._safe_node_id(self.active_node)
            lines.append(f'class {safe_active} activeNode')
            # Also highlight wrangling sub-node if it exists
            wrn_active = self._n(self.active_node, "wrn")
            if wrn_active in all_known:
                lines.append(f'class {wrn_active} activeNode')

        lines.append("%% Interactions")
        for mermaid_id, schema_id in _clickable:
            lines.append(f'click {mermaid_id} call mermaidClick("{schema_id}")')

        return "\n".join(lines)


    def generate_cy_elements(self) -> str:
        """
        Build a Cytoscape.js elements array (JSON string) for the tube-map view.

        Returns a JSON string:
          [
            {"data": {"id": "...", "label": "...", "role": "...", "schema_id": "...",
                      "tier": 0-3, "group": "..."},
             "classes": "trunk active"},   ← space-separated Cytoscape classes
            ...
            {"data": {"id": "e_src__tgt", "source": "...", "target": "..."}},
            ...
          ]

        Tier assignments (used by dagre 'rank' constraint for lane positioning):
          0 — sources (trunk / add / meta)
          1 — tier-1 wrangling nodes (__wrn of data/add/meta schemas)
          2 — assembly join nodes + assembly wrangling nodes
          3 — plot nodes

        All nodes carry schema_id so the Shiny bridge can route clicks without
        knowing the internal Cytoscape node ID.
        """
        elements: list = []
        all_known: set = set()

        def _node(cy_id: str, label: str, role: str, schema_id: str,
                  tier: int, group: str = "") -> dict:
            classes = role
            if self.active_node and schema_id == self.active_node:
                classes += " active"
            return {
                "data": {
                    "id": cy_id,
                    "label": label,
                    "role": role,
                    "schema_id": schema_id,
                    "tier": tier,
                    "group": group,
                },
                "classes": classes,
            }

        def _edge(src: str, tgt: str) -> dict:
            return {"data": {"id": f"e_{src}__{tgt}", "source": src, "target": tgt}}

        def _safe(raw: str) -> str:
            return re.sub(r'[^A-Za-z0-9_]', '_', raw)

        def _wrn_id(sid: str) -> str:
            return f"{_safe(sid)}__wrn"

        # ── 1. Data Schemas (tier 0 → tier 1) ─────────────────────────────────
        schemas = self.cfg.get("data_schemas", {})
        for sid, details in schemas.items():
            safe = _safe(sid)
            label = self._get_label(sid, details)
            elements.append(_node(safe, label, "trunk", sid, 0))
            all_known.add(safe)

            has_wrn = isinstance(details, dict) and bool(
                details.get("wrangling") or details.get("recipe"))
            if has_wrn:
                wid = _wrn_id(sid)
                elements.append(_node(wid, f"{sid}\nWrangle", "wrangle", sid, 1))
                elements.append(_edge(safe, wid))
                all_known.add(wid)

        # ── 2. Additional Datasets (tier 0 → tier 1) ──────────────────────────
        add_schemas = self.cfg.get("additional_datasets_schemas", {})
        for aid, details in add_schemas.items():
            safe = _safe(aid)
            label = self._get_label(aid, details)
            elements.append(_node(safe, label, "add", aid, 0))
            all_known.add(safe)

            has_wrn = isinstance(details, dict) and bool(
                details.get("wrangling") or details.get("recipe"))
            if has_wrn:
                wid = _wrn_id(aid)
                elements.append(_node(wid, f"{aid}\nWrangle", "wrangle", aid, 1))
                elements.append(_edge(safe, wid))
                all_known.add(wid)

        # ── 3. Metadata Schema (tier 0 → tier 1) ──────────────────────────────
        meta = self.cfg.get("metadata_schema", {})
        if meta:
            elements.append(_node("metadata_schema", "Metadata", "meta",
                                  "metadata_schema", 0))
            all_known.add("metadata_schema")
            has_wrn = isinstance(meta, dict) and bool(
                meta.get("wrangling") or meta.get("recipe"))
            if has_wrn:
                wid = _wrn_id("metadata_schema")
                elements.append(_node(wid, "Metadata\nWrangle", "wrangle",
                                      "metadata_schema", 1))
                elements.append(_edge("metadata_schema", wid))
                all_known.add(wid)

        # ── 4. Assembly Manifests (tier 2) ─────────────────────────────────────
        join_defs = self.cfg.get("join_manifests", {})

        def _upstream(parent_raw: str) -> str:
            """Last node in a parent schema's chain (wrangling if present)."""
            wid = _wrn_id(parent_raw)
            return wid if wid in all_known else _safe(parent_raw)

        for asid, details in join_defs.items():
            safe = _safe(asid)
            elements.append(_node(safe, asid, "branch", asid, 2))
            all_known.add(safe)

            ingredients = []
            if isinstance(details, dict):
                for ing in details.get("ingredients", []):
                    if isinstance(ing, dict):
                        did = ing.get("dataset_id", "")
                        if did:
                            ingredients.append(did)
                    elif isinstance(ing, str):
                        ingredients.append(ing)

            for parent_raw in ingredients:
                elements.append(_edge(_upstream(parent_raw), safe))

            has_wrn = isinstance(details, dict) and bool(
                details.get("wrangling") or details.get("recipe"))
            if has_wrn:
                wid = _wrn_id(asid)
                # Assembly wrangling is still tier 2 — it follows the join
                elements.append(_node(wid, f"{asid}\nWrangle", "wrangle", asid, 2))
                elements.append(_edge(safe, wid))
                all_known.add(wid)

        # ── 5. Plots (tier 3) ──────────────────────────────────────────────────
        analysis_groups = self.cfg.get("analysis_groups", {})
        plots_flat = self.cfg.get("plots", {})

        plot_to_group: dict = {}
        for group_name, group_spec in analysis_groups.items():
            if isinstance(group_spec, dict):
                for pid in group_spec.get("plots", {}).keys():
                    plot_to_group[pid] = group_name

        inline_plots: dict = {}
        for group_name, group_spec in analysis_groups.items():
            if isinstance(group_spec, dict):
                for pid, pspec in group_spec.get("plots", {}).items():
                    if pid not in plots_flat:
                        inline_plots[pid] = pspec if isinstance(pspec, dict) else {}

        all_plots = {**plots_flat, **inline_plots}

        for pid, pspec in all_plots.items():
            safe_pid = _safe(pid)
            label = pid.replace("_", " ").title()
            group = plot_to_group.get(pid, "Ungrouped")
            elements.append(_node(safe_pid, label, "plot", pid, 3, group))
            all_known.add(safe_pid)

            target_raw = None
            if isinstance(pspec, dict):
                target_raw = pspec.get("target_dataset") or pspec.get("join_id")

            if target_raw:
                asm_wrn = _wrn_id(target_raw)
                up = asm_wrn if asm_wrn in all_known else _safe(target_raw)
                elements.append(_edge(up, safe_pid))
            else:
                # Orphan node — no target_dataset set
                info_id = f"INFO_{safe_pid}"
                elements.append(_node(info_id, f"WARNING: {pid}\nSet target_dataset",
                                      "info", pid, 3, group))
                elements.append(_edge(info_id, safe_pid))

        return json.dumps(elements)


if __name__ == "__main__":
    import argparse
    from utils.config_loader import ConfigManager

    parser = argparse.ArgumentParser(
        description="Generate a TubeMap (Mermaid) for a manifest.")
    parser.add_argument("manifest", help="Path to the manifest YAML")
    args = parser.parse_args()

    cm = ConfigManager(args.manifest)
    mapper = BlueprintMapper(cm.raw_config)
    print(mapper.generate_mermaid())
