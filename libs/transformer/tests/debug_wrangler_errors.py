#!/usr/bin/env python3
# @deps
# provides: script:debug_wrangler_errors
# consumes: libs/transformer/src/transformer/data_wrangler.py, libs/utils/src/utils/errors.py
# consumed_by: manual error-mode testing
# doc: .claude/rules/rules_data_engine.md#3
# @end_deps
import polars as pl
from transformer.data_wrangler import DataWrangler
from utils.errors import TransformationError


def test_typo_error():
    print("Testing Typo Detection in WrangleStudio...")
    df = pl.DataFrame({"sample_id": [1], "species": ["E. coli"]})
    wrangler = DataWrangler(
        {"sample_id": {"is_primary_key": True}, "species": {}})

    # Intentional typo in column name: 'specie' instead of 'species'
    rules = [{"action": "fill_nulls", "columns": ["specie"], "value": "Unknown"}]

    try:
        wrangler.run(df.lazy(), rules)
    except TransformationError as e:
        print(f"✅ Caught Expected Error: {e.message}")
        print(f"💡 Tip: {e.tip}")
    except Exception as e:
        print(f"❌ Caught Unexpected Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Test error detection in DataWrangler (typo in column name).")
    # No file I/O — runs fully in-memory. Prints pass/fail to stdout.
    parser.parse_args()
    test_typo_error()
