# @deps
# provides: function:lookup_anchor_rows
# consumed_by: app/handlers/home_theater.py, app/handlers/gallery_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-030
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any


def lookup_anchor_rows(coords: Dict[str, Any], tier1_path: str, x_col: str, y_col: str) -> pl.DataFrame:
    """
    Identifies specific rows from the Tier 1 Anchor corresponding to selected plot brush coordinates.
    ADR-030: Essential for preserving the identity link across transformation tiers.
    """
    if not tier1_path or not Path(tier1_path).exists():
        return pl.DataFrame()

    # Extract boundaries
    try:
        xmin, xmax = coords.get('xmin'), coords.get('xmax')
        ymin, ymax = coords.get('ymin'), coords.get('ymax')

        if None in [xmin, xmax, ymin, ymax]:
            return pl.DataFrame()
    except Exception:
        return pl.DataFrame()

    # Scan and filter
    lf = pl.scan_parquet(tier1_path)

    # Apply spatial filter based on manifest mappings
    # Note: We use the columns defined as X and Y in the VizFactory manifest
    selected = lf.filter(
        (pl.col(x_col) >= xmin) & (pl.col(x_col) <= xmax) &
        (pl.col(y_col) >= ymin) & (pl.col(y_col) <= ymax)
    )

    return selected.collect()
