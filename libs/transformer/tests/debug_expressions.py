#!/usr/bin/env python3
# @deps
# provides: script:debug_expressions
# consumes: libs/transformer/src/transformer/actions/cleaning/expressions.py, libs/transformer/tests/data/expressions_test.yaml
# consumed_by: manual expression-action testing
# doc: .claude/rules/rules_data_engine.md#3
# @end_deps
from transformer.actions.cleaning import expressions
import sys
import argparse
import polars as pl
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.


def main():
    parser = argparse.ArgumentParser(
        description="""
        🧪 EXPRESSIONS DEBUGGER (ADR-032)
        Isolated test runner for atomic Polars cleaning expressions (Cast, Coalesce, LabelIf).
        """
    )
    parser.add_argument(
        "--test", choices=["all", "cast", "coalesce", "label_if"], default="all")
    args = parser.parse_args()

    if args.test in ["all", "cast"]:
        print("\n--- Testing Cast ---")
        lf = pl.LazyFrame({"col": ["1", "2", None]})
        spec = {"columns": ["col"], "dtype": "Int64"}
        print(expressions.action_cast(lf, spec).collect())

    if args.test in ["all", "coalesce"]:
        print("\n--- Testing Coalesce ---")
        lf = pl.LazyFrame({"a": [1, None, 3], "b": [10, 20, 30]})
        spec = {"columns": ["a", "b"]}
        print(expressions.action_coalesce(lf, spec).collect())

    if args.test in ["all", "label_if"]:
        print("\n--- Testing Label If ---")
        lf = pl.LazyFrame({"score": [40, 50, 60]})
        spec = {
            "columns": ["score"],  # Standardized to 'columns'
            "new_column": "label",
            "predicate": ">=",
            "value": 50,
            "then": "PASS",
            "otherwise": "FAIL"
        }
        print(expressions.action_label_if(lf, spec).collect())


if __name__ == "__main__":
    main()
