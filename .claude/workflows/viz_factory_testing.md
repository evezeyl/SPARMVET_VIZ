---
description: Unified Workflow for Viz Factory Layer Output Testing
---
# 🎨 Viz Factory Testing Workflow

This workflow isolates the component verification logic for ggplot rendering in relation to new data analysis recipes.

## 1. Engine

The rendering test engine is `debug_runner.py`.

## 2. Protocol

Follow the Universal Evidence Loop:

1. Setup the specific mapping/params in the data analysis recipe and target a synthetic dataset.
2. Run `debug_runner.py` via CLI.
3. **Artifact Routing**:
   - Materialize headless outputs (data snapshot and PNG) strictly to `tmp/data_analysis_recipe_test/{data_analysis_recipe_basename}/`.
   - If doing automatic library testing (e.g. testing a native @register_plot_component), output to `tmp/viz_factory/`.
4. Render `df.glimpse()` and confirm generation of `USER_debug_{plot}.png` before halting for `@verify`.
