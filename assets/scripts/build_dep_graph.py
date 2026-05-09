#!/usr/bin/env python3
# @deps
# provides: script:build_dep_graph
# consumes: all files with @deps blocks across the project
# consumed_by: assets/dep_graph.html, .claude/knowledge/dependency_index.md
# doc: .claude/rules/workspace_standard.md#5
# @end_deps
"""
build_dep_graph.py — Dependency Graph Builder (ADR workspace standard §5)

Scans all project files for @deps annotation blocks, parses them into a
directed dependency graph, and emits:

  1. tmp/dep_graph.json          — Cytoscape.js elements array (nodes + edges)
  2. .claude/knowledge/dependency_index.md  — auto-generated human index

Usage:
  .venv/bin/python assets/scripts/build_dep_graph.py [--root <project_root>]

Agents: run this after adding or modifying @deps blocks to refresh the graph.
Then open assets/dep_graph.html in a browser to explore interactively.
"""
import re
import json
import argparse
import sys
from pathlib import Path
from typing import Any

# ── Configuration ─────────────────────────────────────────────────────────────

# File extensions to scan
SCAN_EXTENSIONS = {".py", ".yaml", ".yml", ".md"}

# Directories to skip entirely
SKIP_DIRS = {".venv", ".git", "node_modules", "__pycache__", ".pytest_cache",
             ".mypy_cache", "dist", "build", "tmp", "tmpAI"}

# Coupling types → Cytoscape edge style class
EDGE_STYLES = {
    "consumes":       "consumes",       # structural dependency
    "mirrors":        "mirrors",        # must stay behaviourally in sync
    "documents":      "documents",      # doc authority
    "include_parent": "include_parent", # !include file composition
    "consumed_by":    "consumed_by",    # backlink (derived from forward links)
}

# Node role colours — mirrors _CY_COLOURS in blueprint_mapper.py
# Role is inferred from file path/type
ROLE_MAP = {
    "app/modules":              "ref",
    "app/handlers":             "ref",
    "app/src":                  "ref",
    "libs/transformer":         "wrangle",
    "libs/ingestion":           "wrangle",
    "libs/viz_factory":         "plot",
    "libs/utils":               "ref",
    "config/manifests":         "branch",
    ".claude/rules":            "meta",
    ".claude/knowledge":   "meta",
    ".claude/plans":       "meta",
    "assets/scripts":           "info",
    "docs":                     "info",
}


# ── Parser ────────────────────────────────────────────────────────────────────

def _infer_role(rel_path: str) -> str:
    for prefix, role in ROLE_MAP.items():
        if rel_path.startswith(prefix):
            return role
    return "info"


def _short_label(rel_path: str) -> str:
    """A readable short label: last two path components."""
    parts = Path(rel_path).parts
    return "/".join(parts[-2:]) if len(parts) > 1 else rel_path


def _parse_deps_block_text(block: str) -> dict[str, list[str]]:
    """
    Parse a @deps...@end_deps block into a dict of keyword → list of values.
    Handles both plain-text blocks (# key: val, val) and YAML frontmatter dicts.
    """
    result: dict[str, list[str]] = {}
    for line in block.splitlines():
        line = line.strip().lstrip("#").strip()
        if not line or line.startswith("@"):
            continue
        if ":" not in line:
            continue
        key, _, raw_val = line.partition(":")
        key = key.strip()
        raw_val = raw_val.strip()
        # strip YAML list brackets if present
        raw_val = raw_val.strip("[]")
        values = [v.strip().strip("'\"") for v in raw_val.split(",") if v.strip()]
        if key and values:
            result.setdefault(key, []).extend(values)
    return result


def _parse_yaml_frontmatter_deps(content: str) -> dict[str, list[str]]:
    """
    Extract deps: block from YAML frontmatter (--- ... ---).
    Returns flat keyword → list[str] same as _parse_deps_block_text.
    """
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return {}
    fm_text = fm_match.group(1)
    # Find deps: block
    deps_match = re.search(r"^deps:\s*\n((?:  .+\n?)*)", fm_text, re.MULTILINE)
    if not deps_match:
        return {}
    deps_text = deps_match.group(1)
    result: dict[str, list[str]] = {}
    for line in deps_text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, raw_val = line.partition(":")
        key = key.strip()
        raw_val = raw_val.strip().strip("[]")
        values = [v.strip().strip("'\"") for v in raw_val.split(",") if v.strip()]
        if key and values:
            result.setdefault(key, []).extend(values)
    return result


def scan_file(path: Path, root: Path) -> dict[str, Any] | None:
    """
    Scan a single file for @deps blocks or YAML frontmatter deps.
    Returns a node descriptor or None if no deps found.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    rel = str(path.relative_to(root))
    deps: dict[str, list[str]] = {}

    if path.suffix == ".md":
        # Try frontmatter first
        deps = _parse_yaml_frontmatter_deps(content)

    if not deps:
        # Strip fenced code blocks before scanning — prevents picking up @deps
        # examples written inside ``` ... ``` in documentation files.
        searchable = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        block_match = re.search(r"@deps\s*\n(.*?)@end_deps", searchable, re.DOTALL)
        if block_match:
            deps = _parse_deps_block_text(block_match.group(1))

    if not deps:
        return None

    return {
        "file": rel,
        "role": _infer_role(rel),
        "label": _short_label(rel),
        "deps": deps,
    }


def scan_project(root: Path) -> list[dict]:
    """Walk the project and collect all annotated file descriptors."""
    nodes = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        # Skip ignored directories
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        node = scan_file(path, root)
        if node:
            nodes.append(node)
    return nodes


# ── Graph builder ─────────────────────────────────────────────────────────────

def _safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_./\-]", "_", s)


def build_cy_elements(nodes: list[dict]) -> list[dict]:
    """
    Build a Cytoscape.js elements list from parsed node descriptors.

    Edge semantics:
      consumes A→B       : A depends on B (A consumes what B provides)
      mirrors A↔B        : A must stay in sync with B (bidirectional, shown as A→B)
      documents A→B      : A documents B's contract
      include_parent A→B : A is included by B
      consumed_by A→B    : A is consumed by B (explicit backlink, same as B consumes A)
    """
    file_set = {n["file"] for n in nodes}
    elements: list[dict] = []
    seen_edges: set[str] = set()

    # Add all nodes
    for n in nodes:
        elements.append({
            "data": {
                "id": _safe_id(n["file"]),
                "label": n["label"],
                "role": n["role"],
                "file": n["file"],
            },
            "classes": n["role"],
        })

    def _add_edge(src: str, tgt: str, coupling: str):
        # tgt may be a partial path match — find best match in file_set
        matched = _resolve_target(tgt, file_set)
        if not matched:
            return  # target not annotated yet — skip silently
        eid = f"e__{_safe_id(src)}__{_safe_id(matched)}__{coupling}"
        if eid in seen_edges:
            return
        seen_edges.add(eid)
        elements.append({
            "data": {
                "id": eid,
                "source": _safe_id(src),
                "target": _safe_id(matched),
                "coupling": coupling,
            },
            "classes": coupling,
        })

    for n in nodes:
        src = n["file"]
        deps = n["deps"]

        for tgt in deps.get("consumes", []):
            if tgt.startswith("action:") or tgt.startswith("rule:") or tgt.startswith("dataset:"):
                continue  # semantic tags, not file paths — skip for file graph
            _add_edge(src, tgt, "consumes")

        for tgt in deps.get("mirrors", []):
            _add_edge(src, tgt, "mirrors")

        for tgt in deps.get("documents", []):
            _add_edge(src, tgt, "documents")

        for tgt in deps.get("include_parent", []):
            _add_edge(src, tgt, "include_parent")

        for tgt in deps.get("consumed_by", []):
            # consumed_by is a backlink: tgt→src (tgt consumes src)
            matched = _resolve_target(tgt, file_set)
            if not matched:
                continue
            eid = f"e__{_safe_id(matched)}__{_safe_id(src)}__consumed_by"
            if eid in seen_edges:
                continue
            seen_edges.add(eid)
            elements.append({
                "data": {
                    "id": eid,
                    "source": _safe_id(matched),
                    "target": _safe_id(src),
                    "coupling": "consumed_by",
                },
                "classes": "consumed_by",
            })

    return elements


def _resolve_target(tgt: str, file_set: set[str]) -> str | None:
    """Find a file in file_set that matches the target reference (exact or suffix)."""
    tgt = tgt.strip()
    if tgt in file_set:
        return tgt
    # Suffix match — e.g. "orchestrator.py" matches "app/modules/orchestrator.py"
    matches = [f for f in file_set if f.endswith(tgt) or tgt in f]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # Prefer shortest (most specific) match
        return min(matches, key=len)
    return None


# ── Markdown index emitter ────────────────────────────────────────────────────

def emit_dependency_index(nodes: list[dict], out_path: Path):
    lines = [
        "# Dependency Index (AUTO-GENERATED — do not edit by hand)",
        "",
        "> Generated by `assets/scripts/build_dep_graph.py` from `@deps` blocks across the project.",
        "> To update: `.venv/bin/python assets/scripts/build_dep_graph.py`",
        "> To explore visually: open `assets/dep_graph.html` in a browser.",
        "",
        "---",
        "",
    ]

    for n in sorted(nodes, key=lambda x: x["file"]):
        lines.append(f"## `{n['file']}`")
        lines.append(f"- **Role:** `{n['role']}`")
        deps = n["deps"]
        for key in ("provides", "consumes", "mirrors", "documents", "include_parent", "consumed_by", "doc"):
            vals = deps.get(key)
            if vals:
                lines.append(f"- **{key}:** {', '.join(f'`{v}`' for v in vals)}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Sync Risk Register")
    lines.append("")
    lines.append("Pairs with `mirrors:` coupling — must always be edited together:")
    lines.append("")
    for n in nodes:
        for tgt in n["deps"].get("mirrors", []):
            lines.append(f"- `{n['file']}` ↔ `{tgt}`")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ dependency_index.md → {out_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build dependency graph from @deps annotations across the project.")
    parser.add_argument("--root", default=None,
                        help="Project root (default: 4 levels up from this script)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else script_dir.parent.parent

    print(f"\n{'='*60}")
    print(f" 🔗  DEPENDENCY GRAPH BUILDER")
    print(f"{'='*60}")
    print(f"  Root: {root}\n")

    # Scan
    nodes = scan_project(root)
    print(f"  Found {len(nodes)} annotated files.\n")

    if not nodes:
        print("  ⚠️  No @deps blocks found. Annotate files per workspace_standard.md §5.")
        sys.exit(0)

    # Build Cytoscape elements
    elements = build_cy_elements(nodes)
    node_count = sum(1 for e in elements if "source" not in e["data"])
    edge_count = sum(1 for e in elements if "source" in e["data"])
    print(f"  Graph: {node_count} nodes, {edge_count} edges.")

    # Emit dep_graph.json
    tmp_dir = root / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    graph_path = tmp_dir / "dep_graph.json"
    graph_path.write_text(json.dumps(elements, indent=2), encoding="utf-8")
    print(f"  ✅ dep_graph.json → {graph_path}")

    # Emit dependency_index.md (auto-generated)
    index_path = root / ".claude" / "knowledge" / "dependency_index.md"
    emit_dependency_index(nodes, index_path)

    print(f"\n  Open assets/dep_graph.html in a browser to explore the graph.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
