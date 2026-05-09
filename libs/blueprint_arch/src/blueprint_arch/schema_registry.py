# @deps
# provides: function:get_action_catalog, function:get_component_catalog, function:get_combined_catalog, function:get_actions_for_context, function:get_actions_by_category, function:get_components_for_context
# consumes: registry:ACTION_SCHEMAS (libs/transformer/src/transformer/actions/base.py), registry:COMPONENT_SCHEMAS (libs/viz_factory/src/viz_factory/registry.py)
# consumed_by: app/handlers/blueprint_handlers.py
# doc: .claude/knowledge/architecture_decisions.md (ADR-075), .claude/rules/rules_app_structure.md §2
# @end_deps
"""
schema_registry.py — BLUEPRINT IDE form catalog (ADR-075).

Reads ACTION_SCHEMAS from the transformer action registry and COMPONENT_SCHEMAS from the
viz_factory component registry. Provides a unified, headless-safe catalog for the BLUEPRINT
form renderer — no Shiny imports, safe to call from any context.

Widget type vocabulary (params entries):
    column_selector   — select one or more columns from the active frame schema
    expression        — free-form Polars expression string (eval'd in mutate context)
    enum              — dropdown from a fixed list of allowed values
    dtype_picker      — dropdown of supported Polars dtype strings (cast action)
    number            — numeric input (int or float)
    string            — plain text input
    color             — color picker (hex or named)
    column_or_literal — either a column name OR a literal value (user chooses)
    bool              — checkbox

Context tags (schema["context"]):
    t1       — valid in Tier 1 wrangling blocks
    t2       — valid in Tier 2 wrangling blocks
    assembly — valid in assembly recipe steps
    plot     — valid as a viz_factory layer (components only)
"""


def get_action_catalog() -> dict:
    """Return a copy of the transformer ACTION_SCHEMAS dict.

    Import is deferred so this module is importable even if transformer is not
    installed — callers receive an empty dict in that case.
    """
    try:
        from transformer.actions.base import ACTION_SCHEMAS
        return dict(ACTION_SCHEMAS)
    except ImportError:
        return {}


def get_component_catalog() -> dict:
    """Return a copy of the viz_factory COMPONENT_SCHEMAS dict."""
    try:
        from viz_factory.registry import COMPONENT_SCHEMAS
        return dict(COMPONENT_SCHEMAS)
    except ImportError:
        return {}


def get_combined_catalog() -> dict:
    """Return both catalogs keyed by 'actions' and 'components'."""
    return {
        "actions": get_action_catalog(),
        "components": get_component_catalog(),
    }


def get_actions_for_context(context: str) -> dict:
    """Return actions whose schema declares the given context tag.

    Args:
        context: one of 't1', 't2', 'assembly'
    """
    return {
        name: schema
        for name, schema in get_action_catalog().items()
        if context in schema.get("context", [])
    }


def get_actions_by_category(category: str) -> dict:
    """Return actions whose schema declares the given category string."""
    return {
        name: schema
        for name, schema in get_action_catalog().items()
        if schema.get("category") == category
    }


def get_components_for_context(context: str) -> dict:
    """Return viz_factory components whose schema declares the given context tag.

    For most geoms this will be 'plot'.
    """
    return {
        name: schema
        for name, schema in get_component_catalog().items()
        if context in schema.get("context", [])
    }


def search_actions(query: str) -> dict:
    """Simple keyword search across action name, label, tags, and category."""
    q = query.lower()
    results = {}
    for name, schema in get_action_catalog().items():
        haystack = " ".join([
            name,
            schema.get("label", ""),
            schema.get("category", ""),
            " ".join(schema.get("tags", [])),
        ]).lower()
        if q in haystack:
            results[name] = schema
    return results
