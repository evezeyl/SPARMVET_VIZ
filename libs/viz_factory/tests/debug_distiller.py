#!/usr/bin/env python3
# @deps
# provides: script:debug_distiller
# consumes: libs/viz_factory/src/viz_factory/distiller.py, libs/viz_factory/tests/test_data/
# consumed_by: manual distiller testing
# doc: .claude/rules/rules_data_engine.md
# @end_deps
import sys
import argparse
import polars as pl
from pathlib import Path
from plotnine import ggplot, aes, geom_point, scale_color_distiller

# Avoid GUI issues
import matplotlib
matplotlib.use('Agg')


def main():
    parser = argparse.ArgumentParser(
        description="""
        🎨 DISTILLER DEBUGGER (ADR-032)
        Verifies Color Distiller scaling in Plotnine components.
        """
    )
    parser.add_argument("--out", default="tmp/test_distiller.png",
                        help="Output path for verification plot.")
    args = parser.parse_args()

    print(f"--- 🎨 Testing Color Distiller ---")
    try:
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df.to_pandas(), aes(x="x", y="y", color="y")) + \
            geom_point() + scale_color_distiller(palette="Spectral")
        p.save(args.out)
        print(f"✅ Success: {args.out}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
