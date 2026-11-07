# assets/scripts/ — User-Facing Helper Scripts

Standalone scripts for data analysis recipe authoring, data generation, deployment setup, and dev diagnostics. Run from the repository root with the project venv active.

```bash
source .venv/bin/activate
python assets/scripts/<script>.py --help
```

## Scripts

### Data analysis recipe Authoring

| Script | Purpose |
|---|---|
| `create_data_analysis_recipe.py` | Scaffold a full YAML data analysis recipe from a TSV/CSV source file. Supports `!include` fragments, column name cleaning, and primary key detection. |
| `SF_create_data_analysis_recipe.py` | Simpler schema-only variant — infers `input_fields` from a TSV without `!include` support. Useful for quick bootstrapping. |
| `normalize_data_analysis_recipe_fields.py` | Scan data analysis recipes in `config/data_analysis_recipes/` and normalise field names to ADR-041 standards (snake_case slugs, required properties). |

### Data Generation & Verification

| Script | Purpose |
|---|---|
| `generate_demo_data.py` | Generate synthetic demo TSVs via `AquaSynthesizer` from ground-truth ST22 data. Output: `assets/test_data/demo_high_integrity/`. |
| `figshare_triple_integration.py` | Integration smoke test: scan figshare.21737288 CSVs, write join TSVs to `tmp/integration/`. |
| `figshare_plot_integration.py` | Downstream of `figshare_triple_integration.py` — render plots from the join output into `tmp/integration/`. |

### Deployment Setup

| Script | Purpose |
|---|---|
| `create_test_deployment.py` | Create or validate a local deployment under `config/deployment/local/`. Useful for setting up a fresh dev environment. |

### Dev Diagnostics & Dependency Graph

| Script | Purpose |
|---|---|
| `build_dep_graph.py` | Scan `@deps` blocks across all project files and write `assets/dep_graph.html` + `dependency_index.md`. Run after adding or changing `@deps` annotations. |
| `debug_apply_data_analysis_recipe_standards.py` | Apply ADR-041 data analysis recipe standards to test YAML files in `libs/viz_factory/tests/test_data/`. |
| `debug_bootstrap_viz_yamls.py` | Bootstrap test data analysis recipes from scratch into `libs/viz_factory/tests/test_data/`. |
| `materialize_data_analysis_recipe_plots.py` | **Deprecated shim** — forwards to `libs/viz_factory/tests/debug_gallery.py`. Kept for backward compatibility only. Use `debug_gallery.py` directly. |

> Note: `debug_viz_factory_audit.py` was relocated to `libs/viz_factory/tests/` (ADR-032 — library-internal debug runners belong in their own `libs/<x>/tests/`).

## Notes

- All scripts use the project venv (`pip install -e ./libs/<lib>` must have been run for any lib they import).
- Scripts that write output do so under `tmp/` or `assets/` — never under `app/` or `libs/`.
- `build_dep_graph.py` should be re-run after any `@deps` block changes to keep `dependency_index.md` current.
