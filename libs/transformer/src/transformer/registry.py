# ==========================================
# The Central Action Registry Interface
# ==========================================
# @deps
# provides: function:get_action_function
# consumes: libs/transformer/src/transformer/actions/base.py (AVAILABLE_WRANGLING_ACTIONS)
# consumed_by: libs/transformer/src/transformer/data_wrangler.py
# doc: .claude/rules/rules_data_engine.md
# @end_deps
# This file now serves purely as a lightweight interface bridge to the
# dynamic plugin sub-modules located in `actions/`.
#
# Do NOT write wrangling logic here. Add new files to `actions/core/`
# or `actions/advanced/` instead.

from typing import Callable, Dict, Any
import polars as pl
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS

# We must import the main actions __init__.py here just to trigger the auto-load process
import transformer.actions


def get_action_function(action_name: str) -> Callable:
    """Returns the function for a given action, or raises a friendly error."""
    if action_name not in AVAILABLE_WRANGLING_ACTIONS:
        available = ", ".join(AVAILABLE_WRANGLING_ACTIONS.keys())
        raise ValueError(
            f"Action '{action_name}' is not registered. Available actions: {available}")
    return AVAILABLE_WRANGLING_ACTIONS[action_name]


# Future expansion: Plotting Defaults Registry
AVAILABLE_PLOT_DEFAULTS = {
    # e.g., "color_scale": apply_color_scale_default
}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
