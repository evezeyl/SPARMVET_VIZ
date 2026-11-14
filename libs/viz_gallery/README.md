# VizGallery Library (viz_gallery)

**Scientific Textbook & Cookbook Persistence Layer**

## Overview

`viz_gallery` manages the storage, retrieval, and indexing of SPARMVET examples. It ensures that every plot in the "Scientific Cookbook" adheres to the formal governance standards.

## Key Components

- **GalleryManager (gallery_manager.py)**: Handles the creation of gallery bundles (YAML, TSV, MD, PNG).
- **GalleryIndexer (integrated in GalleryManager)**: Generates the `gallery_index.json` Pivot-Index for zero-latency filtering.

## Maintenance (ADR-037)

The gallery requires a pre-computed index for UI efficiency. Run the following command from the project root to rebuild the index and perform an integrity audit:

```bash
export PYTHONPATH=$PYTHONPATH:. && ./.venv/bin/python libs/viz_gallery/assets/refresh_gallery.py
```

After adding or changing an example's data analysis recipe or data, regenerate its `preview_plot.png` before rebuilding the index (`rules_gallery_standards.md §6`):

```bash
./.venv/bin/python libs/viz_gallery/assets/generate_previews.py [--only <name> ...] [--force]
```

## Governance (Mandatory Triplet — ADR-061, ADR-063)

Every gallery bundle folder MUST contain all four files:

1. `data_analysis_recipe.yaml` — a standard recipe in format 1 (checked in the `gallery` profile). The `taxonomy` key of each plot entry types five axes (family, pattern, difficulty, show, sample_size); the sixth, `geom`, is derived from the first `geom_*` or `stat_*` layer of the plot
2. `example_data.tsv` — representative dataset
3. `example_meta.md` — scientific guidance + author metadata
4. `preview_plot.png` — pre-rendered evidence PNG

Full standards: `.claude/rules/rules_gallery_standards.md`

## Installation

```bash
pip install -e libs/viz_gallery
```

## Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/viz_gallery/tests/ -v
```
