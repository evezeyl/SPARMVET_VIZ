# Viz Factory Artist Integrity Suite 🎨

This directory contains visual validation tests for the Electronic Artist Pillar (VizFactory).

## Tiered Data Integration (ADR-024)

The test runner (`debug_runner.py`) has been synchronized to support the tiered data lifecycle. While VizFactory primarily focuses on Tier 3 (Plot Layers), it can now execute upstream wrangling defined in the manifest:

```yaml
id: "geom_point_test"
data_path: "./geom_point_test.tsv"
wrangling:
  tier1: [] # Relational cleanup (Identity by default)
  tier2: [] # Plot-specific reshaping (Identity by default)
plots:
  example:
    mapping: { x: "x", y: "y" }
    layers:
      - name: "geom_point"
```

## Test Runners

- **debug_runner.py**: Single-plot renderer. Generates comparison plots (Baseline vs. Applied) for geoms and positions.
  - usage: `python debug_runner.py path/to/manifest.yaml --output_dir tmp/viz/`
- **viz_factory_integrity_suite.py**: Batch processor that renders every registered plot component and generates an integrity report.

## Baseline Comparisons

For geoms and positions, the runner automatically generates a side-by-side comparison:

- **Left**: Default (Identity) state.
- **Right**: Applied manifest state.
Artifacts are saved as PNG files in `tmp/viz_factory/`.

## Pytest — fast component contract check

```bash
PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/ -v
```

Test modules:
- `test_deco2_components.py` — DECO-2 wrappers (38 cases)
- `test_component_schemas.py` — verifies all 7 `@register_plot_component(ui_schema=...)` entries in `COMPONENT_SCHEMAS`. Checks required fields (`label`, `category`, `context`, `params`, `wraps`, `allow_extra_params`), semantic category vocabulary, and that `params` cover the core plotnine constructor surface for each geom.
