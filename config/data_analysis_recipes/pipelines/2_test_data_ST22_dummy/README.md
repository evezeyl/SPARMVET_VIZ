# README for DATA ANALYSIS RECIPE 2_test_data_ST22_dummy


> Note: Following: architectural standards (ADR-041)

> Note: Debug scripts (canonical locations)
- `libs/transformer/tests/debug_wrangler.py`  — Tier 1 wrangling audit
- `libs/transformer/tests/debug_assembler.py` — Tier 1/2 assembly + materialization
- `libs/viz_factory/tests/debug_gallery.py`   — Headless plot rendering audit

## AMR Profiling
- integrated ResFinder data with Metadata
- implemented the multi-resistance annotation logic [DESCRIBE]
- ResFinder Data was joined with metadata
    - filtered by biological thresholds (min 90% identity, min 60% overlap)
    - annotated with an is_multi_resistant flag (isolates resistant to ≥ 2 antimicrobial classes).


```bash
# Step 1 — Assemble data (writes contracted parquet + TSV for audit)
# Outputs:
#   tmp/EVE_assembly_AMR_Profile_Joint.parquet   (pre-contract intermediate)
#   tmp/EVE_contracted_AMR_Profile_Joint.parquet (contracted — used by plots)
#   tmp/EVE_contracted_AMR_Profile_Joint.tsv     (human-readable audit export)
./.venv/bin/python libs/transformer/tests/debug_assembler.py \
  --data-analysis-recipe config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml

# Step 2 — Render plots (reads contracted parquet from tmp/)
# Output: tmp/materialized_gallery/{data_analysis_recipe_id}/{group_id}/{plot_id}.png
./.venv/bin/python libs/viz_factory/tests/debug_gallery.py \
  --data-analysis-recipe config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml
```

