from typing import Callable, Dict, Any, List, Union
import polars as pl
import logging

logger = logging.getLogger(__name__)

# @deps
# provides: decorator:register_action, registry:AVAILABLE_WRANGLING_ACTIONS
# consumed_by: libs/transformer/src/transformer/actions/cleaning/core.py, libs/transformer/src/transformer/actions/cleaning/analytical.py, libs/transformer/src/transformer/actions/cleaning/advanced.py, libs/transformer/src/transformer/actions/cleaning/expressions.py, libs/transformer/src/transformer/actions/relational/joins.py, libs/transformer/src/transformer/actions/reshaping/core.py, libs/transformer/src/transformer/actions/performance/aggregation.py, libs/transformer/src/transformer/actions/persistence/anchor.py, libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py
# doc: .claude/rules/rules_data_engine.md
# @end_deps

# The Central Repository for all Registered Actions
AVAILABLE_WRANGLING_ACTIONS: Dict[str, Callable[[
    pl.LazyFrame, Dict[str, Any]], pl.LazyFrame]] = {}


def register_action(name: str):
    """
    Standard Plugin Decorator for Data Wrangling Actions.
    Any function decorated with `@register_action("action_name")` 
    will automatically become available to the YAML manifest executor.
    """
    def decorator(func: Callable):
        if name in AVAILABLE_WRANGLING_ACTIONS:
            logger.warning(
                f"Warning: Extensibility clash. Action '{name}' is already registered and will be overwritten.")
        AVAILABLE_WRANGLING_ACTIONS[name] = func
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
