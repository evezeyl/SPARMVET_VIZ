"""libs/blueprint_arch/src/blueprint_arch/agent_tools.py
MVP-1 tools for the BLUEPRINT AI Agent (ADR-076 §4).

Three tools are registered for Phase 1:
    get_available_actions      — list @register_action entries, optionally filtered
    get_available_components   — list @register_plot_component entries, optionally filtered
    get_field_contract         — resolve input/output fields for a data schema

Each tool function:
    - Accepts a dict of args (matching the schema in register_tool_schema)
    - Returns a JSON-serialisable dict with "status" ("ok" | "error") and "data" or "message"
    - Raises no exceptions — errors are returned in the result dict

Tool schemas are registered with agent_tool_parser so the parser can validate
args before the tool is called.

Constraints (Two-Category Law — ADR-045):
    Zero Shiny imports. Pure Python. Importable headlessly.
"""

from __future__ import annotations

# @deps
# provides: function:call_tool, function:get_tool_definitions, dict:TOOL_REGISTRY
# consumed_by: app/handlers/blueprint_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-076
# @end_deps

import re
from pathlib import Path
from typing import Any

from blueprint_arch.agent_adapter import Tool
from blueprint_arch.agent_tool_parser import register_tool_schema


# ── Tool registry ─────────────────────────────────────────────────────────────

# Maps tool_name -> callable(args: dict) -> dict
TOOL_REGISTRY: dict[str, Any] = {}


def _register(tool: Tool, fn: Any) -> None:
    """Add a tool + its schema to both registries."""
    TOOL_REGISTRY[tool.name] = fn
    # Register arg schema with the parser for validation
    required = [
        k for k, v in tool.parameters.get("properties", {}).items()
        if k in tool.parameters.get("required", [])
    ]
    properties = {
        k: {"type": v.get("type", "str")}
        for k, v in tool.parameters.get("properties", {}).items()
    }
    register_tool_schema(
        tool.name,
        required=required,
        properties=properties,
    )


# ── Tool: get_available_actions ───────────────────────────────────────────────

_GET_ACTIONS_TOOL = Tool(
    name="get_available_actions",
    description=(
        "List all @register_action entries available in the transformer registry. "
        "Optionally filter by category or context tier. "
        "Returns name, category, context tiers, and tags for each action."
    ),
    parameters={
        "type": "object",
        "required": [],
        "properties": {
            "category": {
                "type": "str",
                "description": (
                    "Filter to one category. One of: cleaning, expressions, analytical, "
                    "advanced, reshaping, performance, relational. Omit to return all."
                ),
            },
            "context": {
                "type": "str",
                "description": (
                    "Filter to one context tier: t1, t2, assembly. Omit to return all."
                ),
            },
        },
    },
)


def _tool_get_available_actions(args: dict) -> dict:
    """Return filtered action catalog entries."""
    try:
        # Deferred import — schema_registry lives in libs/blueprint_arch/
        from blueprint_arch.schema_registry import get_action_catalog
        catalog = get_action_catalog()
    except Exception as exc:
        return {"status": "error", "message": f"Failed to load action catalog: {exc}"}

    category_filter = args.get("category", "").strip().lower() or None
    context_filter = args.get("context", "").strip().lower() or None

    results: list[dict] = []
    for name, entry in sorted(catalog.items()):
        if category_filter and entry.get("category", "").lower() != category_filter:
            continue
        contexts = [c.lower() for c in entry.get("context", [])]
        if context_filter and context_filter not in contexts:
            continue
        results.append({
            "name": name,
            "label": entry.get("label", name),
            "category": entry.get("category", ""),
            "context": entry.get("context", []),
            "tags": entry.get("tags", []),
            "params": {
                k: {
                    "required": v.get("required", False),
                    "widget": v.get("widget", ""),
                    "label": v.get("label", k),
                }
                for k, v in entry.get("params", {}).items()
            },
        })

    return {
        "status": "ok",
        "data": {
            "count": len(results),
            "filters": {"category": category_filter, "context": context_filter},
            "actions": results,
        },
    }


# ── Tool: get_available_components ────────────────────────────────────────────

_GET_COMPONENTS_TOOL = Tool(
    name="get_available_components",
    description=(
        "List all @register_plot_component entries (geoms, scales, stats, themes). "
        "Optionally filter by category. "
        "Returns name, category, tags, and params for each component."
    ),
    parameters={
        "type": "object",
        "required": [],
        "properties": {
            "category": {
                "type": "str",
                "description": (
                    "Filter to one category. Examples: distribution, comparison, "
                    "correlation, scale, theme, coordinate. Omit to return all."
                ),
            },
        },
    },
)


def _tool_get_available_components(args: dict) -> dict:
    """Return filtered component catalog entries."""
    try:
        from blueprint_arch.schema_registry import get_component_catalog
        catalog = get_component_catalog()
    except Exception as exc:
        return {"status": "error", "message": f"Failed to load component catalog: {exc}"}

    category_filter = args.get("category", "").strip().lower() or None

    results: list[dict] = []
    for name, entry in sorted(catalog.items()):
        if category_filter and entry.get("category", "").lower() != category_filter:
            continue
        results.append({
            "name": name,
            "label": entry.get("label", name),
            "category": entry.get("category", ""),
            "tags": entry.get("tags", []),
            "params": {
                k: {
                    "required": v.get("required", False),
                    "widget": v.get("widget", ""),
                    "label": v.get("label", k),
                }
                for k, v in entry.get("params", {}).items()
            },
        })

    return {
        "status": "ok",
        "data": {
            "count": len(results),
            "filters": {"category": category_filter},
            "components": results,
        },
    }


# ── Tool: get_field_contract ──────────────────────────────────────────────────

_GET_FIELD_CONTRACT_TOOL = Tool(
    name="get_field_contract",
    description=(
        "Resolve the input_fields and output_fields for a named data schema in the "
        "active manifest. Returns field slugs, types, and labels. "
        "Use this to check which columns are available at each pipeline stage."
    ),
    parameters={
        "type": "object",
        "required": ["schema_id"],
        "properties": {
            "schema_id": {
                "type": "str",
                "description": (
                    "The data schema identifier (e.g. 'amr_data', 'metadata_schema'). "
                    "Must match a key declared in the active manifest's data_schemas block."
                ),
            },
            "manifest_path": {
                "type": "str",
                "description": (
                    "Path to the pipeline manifest YAML (relative to project root). "
                    "If omitted, the active manifest from the current session context is used."
                ),
            },
        },
    },
)


def _tool_get_field_contract(args: dict) -> dict:
    """Return input and output field contracts for a schema_id."""
    schema_id = args.get("schema_id", "").strip()
    manifest_path_str = args.get("manifest_path", "").strip() or None

    if not schema_id:
        return {"status": "error", "message": "'schema_id' is required."}

    if not manifest_path_str:
        return {
            "status": "error",
            "message": (
                "'manifest_path' was not provided and no active manifest is "
                "available in this tool call. Please supply 'manifest_path'."
            ),
        }

    manifest_path = Path(manifest_path_str)
    if not manifest_path.exists():
        return {
            "status": "error",
            "message": f"Manifest not found: {manifest_path_str}",
        }

    try:
        from blueprint_arch.manifest_navigator import (
            build_schema_registry,
            build_sibling_map,
            load_fields_file,
            resolve_fields_for_schema,
        )
    except Exception as exc:
        return {"status": "error", "message": f"Failed to import manifest_navigator: {exc}"}

    # Build inc_map from !include references (mirrors blueprint_handlers.py pattern)
    try:
        raw_text = manifest_path.read_text(encoding="utf-8")
        manifest_dir = manifest_path.parent
        inc_map: dict[str, str] = {}
        for rel_path in re.findall(r"!include\s+['\"]([^'\"]+)['\"]", raw_text):
            abs_path = (manifest_dir / rel_path).resolve()
            if abs_path.exists():
                inc_map[rel_path] = str(abs_path)
    except Exception as exc:
        return {"status": "error", "message": f"Failed to read manifest: {exc}"}

    try:
        ctx_map = build_sibling_map(str(manifest_path))
        schema_reg = build_schema_registry(str(manifest_path), inc_map)
    except Exception as exc:
        return {"status": "error", "message": f"Failed to build schema registry: {exc}"}

    if schema_id not in schema_reg:
        available = sorted(schema_reg.keys())
        return {
            "status": "error",
            "message": (
                f"Schema '{schema_id}' not found in manifest. "
                f"Available schemas: {available}"
            ),
        }

    try:
        fields = resolve_fields_for_schema(schema_id, ctx_map, inc_map)
    except Exception as exc:
        return {"status": "error", "message": f"Failed to resolve fields: {exc}"}

    entry = schema_reg[schema_id]

    # input_fields / output_fields may be path strings when declared via !include
    def _load_field_entry(val: Any) -> dict:
        if isinstance(val, dict):
            return val
        if isinstance(val, str) and val:
            # Relative path from manifest dir — resolve via inc_map or direct
            abs_path = (manifest_path.parent / val).resolve()
            if abs_path.exists():
                try:
                    return load_fields_file(abs_path)
                except Exception:
                    pass
        return {}

    input_fields = _load_field_entry(entry.get("input_fields", {}))
    output_fields = _load_field_entry(entry.get("output_fields", {}))
    resolved = fields if isinstance(fields, dict) else {}

    return {
        "status": "ok",
        "data": {
            "schema_id": schema_id,
            "schema_type": entry.get("schema_type", ""),
            "input_fields": _format_fields(input_fields),
            "output_fields": _format_fields(output_fields),
            "resolved_fields": _format_fields(resolved),
            "wrangling_tiers": list(entry.get("wrangling", {}).keys())
            if isinstance(entry.get("wrangling"), dict) else [],
        },
    }


def _format_fields(fields_dict: dict) -> list[dict]:
    """Normalise a Rich Dict of fields into a flat list for agent consumption."""
    if not isinstance(fields_dict, dict):
        return []
    out = []
    for slug, props in fields_dict.items():
        if isinstance(props, dict):
            out.append({
                "slug": slug,
                "type": props.get("type", ""),
                "label": props.get("label", slug),
                "required": props.get("required", False),
            })
        else:
            out.append({"slug": slug, "type": str(props), "label": slug})
    return out


# ── Public API ────────────────────────────────────────────────────────────────

# Register all three tools
_register(_GET_ACTIONS_TOOL, _tool_get_available_actions)
_register(_GET_COMPONENTS_TOOL, _tool_get_available_components)
_register(_GET_FIELD_CONTRACT_TOOL, _tool_get_field_contract)


def get_tool_definitions() -> list[Tool]:
    """Return Tool objects for all registered agent tools.

    Used by blueprint_handlers.py to pass tool metadata to start_session()
    and to include tool descriptions in the system prompt.
    """
    return [_GET_ACTIONS_TOOL, _GET_COMPONENTS_TOOL, _GET_FIELD_CONTRACT_TOOL]


def call_tool(tool_name: str, args: dict) -> dict:
    """Dispatch a validated tool call and return the result dict.

    The caller (blueprint_handlers.py) is responsible for calling this only
    after the args have been validated by extract_tool_calls().

    Returns {"status": "ok", "data": ...} or {"status": "error", "message": ...}.
    """
    fn = TOOL_REGISTRY.get(tool_name)
    if fn is None:
        available = sorted(TOOL_REGISTRY)
        return {
            "status": "error",
            "message": (
                f"Tool '{tool_name}' is not registered. "
                f"Available tools: {available}"
            ),
        }
    try:
        return fn(args)
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Tool '{tool_name}' raised an unexpected error: {exc}",
        }
