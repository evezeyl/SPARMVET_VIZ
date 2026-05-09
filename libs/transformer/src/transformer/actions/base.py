from typing import Callable, Dict, Any, List, Optional, Union
import polars as pl
import logging

logger = logging.getLogger(__name__)

# @deps
# provides: decorator:register_action, registry:AVAILABLE_WRANGLING_ACTIONS, registry:ACTION_SCHEMAS
# consumed_by: libs/transformer/src/transformer/actions/cleaning/core.py, libs/transformer/src/transformer/actions/cleaning/analytical.py, libs/transformer/src/transformer/actions/cleaning/advanced.py, libs/transformer/src/transformer/actions/cleaning/expressions.py, libs/transformer/src/transformer/actions/relational/joins.py, libs/transformer/src/transformer/actions/reshaping/core.py, libs/transformer/src/transformer/actions/performance/aggregation.py, libs/transformer/src/transformer/actions/persistence/anchor.py, libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/blueprint_arch/src/blueprint_arch/schema_registry.py
# doc: .claude/rules/rules_data_engine.md, .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps

# The Central Repository for all Registered Actions
AVAILABLE_WRANGLING_ACTIONS: Dict[str, Callable[[
    pl.LazyFrame, Dict[str, Any]], pl.LazyFrame]] = {}

# Parallel registry: action_name → ui_schema dict (ADR-075 BLUEPRINT IDE form catalog)
# Only populated when @register_action(..., ui_schema={...}) is provided.
ACTION_SCHEMAS: Dict[str, Dict[str, Any]] = {}


def register_action(name: str, ui_schema: Optional[Dict[str, Any]] = None):
    """
    Standard Plugin Decorator for Data Wrangling Actions.
    Any function decorated with `@register_action("action_name")`
    will automatically become available to the YAML manifest executor.

    Optional `ui_schema` kwarg populates ACTION_SCHEMAS for BLUEPRINT IDE form generation
    (ADR-075). Schema format: {label, category, context, tags, params: {param: {widget, ...}}}.
    """
    def decorator(func: Callable):
        if name in AVAILABLE_WRANGLING_ACTIONS:
            logger.warning(
                f"Warning: Extensibility clash. Action '{name}' is already registered and will be overwritten.")
        AVAILABLE_WRANGLING_ACTIONS[name] = func
        if ui_schema is not None:
            ACTION_SCHEMAS[name] = ui_schema
        return func
    return decorator


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
