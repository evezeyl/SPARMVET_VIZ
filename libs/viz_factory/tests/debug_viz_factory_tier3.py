#!/usr/bin/env python3
# @deps
# provides: script:debug_viz_factory_tier3
# consumes: libs/viz_factory/src/viz_factory/, libs/transformer/src/transformer/data_wrangler.py
# consumed_by: manual Tier 3 wrangling+viz testing
# doc: .claude/rules/rules_data_engine.md
# @end_deps
import polars as pl
import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.

from viz_factory.viz_factory import VizFactory

def test_tier3_predicate_pushdown(output: str = None):
    # 1. Setup Data (Synthetic)
    df = pl.LazyFrame({
        "species": ["E. coli", "E. coli", "S. aureus", "S. aureus"],
        "count": [10, 20, 30, 40],
        "category": ["A", "B", "A", "B"]
    })
    
    # 2. Setup Manifest with Filter
    manifest = {
        "plots": {
            "species_comparison": {
                "mapping": {"x": "species", "y": "count", "fill": "category"},
                "filters": [
                    {"column": "species", "op": "eq", "value": "E. coli"}
                ],
                "layers": [
                    {"name": "geom_col", "params": {"position": "dodge"}}
                ]
            }
        }
    }
    
    # 3. Render
    factory = VizFactory()
    # Mocking get_component since registry is complex
    import viz_factory.registry as registry
    from plotnine import geom_col
    registry.PLOT_COMPONENTS["geom_col"] = lambda p, params: p + geom_col(**params)
    
    print("Starting Tier 3 Render...")
    p = factory.render(df, manifest, "species_comparison")
    
    # 4. Verify results (Internal State check)
    # We can check the data in the plot object
    plot_data = p.data
    print("\nRendered Plot Data:")
    print(plot_data)
    
    assert len(plot_data) == 2
    assert all(plot_data["species"] == "E. coli")
    print("\n✅ Tier 3 Verification Success: Predicate Pushdown confirmed.")

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        p.save(output, verbose=False)
        print(f"  → Plot saved: {output}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Test VizFactory Tier 3 predicate pushdown with synthetic data. "
                    "Runs fully in-memory, prints pass/fail to stdout.")
    parser.add_argument(
        "--output", default=None,
        help="Optional path to save the rendered plot PNG (default: not saved).")
    args = parser.parse_args()
    test_tier3_predicate_pushdown(output=args.output)
