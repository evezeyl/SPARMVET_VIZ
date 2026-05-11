## Test Lab — Quick Reference

**Test Lab** is a developer sandbox for validating pipeline components in isolation — no UI, no Shiny reactivity.

### AquaSynthesizer
Generate synthetic test data matching a schema. Outputs to `tmp/` for immediate inspection with debug scripts.

### Wrangler Debug
Run the Tier 1 and Tier 2 wrangling steps from a manifest fragment against a TSV file without the full app. Outputs a `USER_debug_view.tsv` in `tmp/` for manual review.

### Assembler Debug
Run the full assembly recipe (joins + derived columns + `final_contract`) against source data. Produces pre-contract and contracted Parquet + TSV files.

### Gallery Debug
Render all plots from a manifest into PNG files. Requires the Assembler to have been run first (needs Parquet in `tmp/`).

### Usage pattern
1. Select the manifest and data source
2. Click the stage you want to test (Wrangler → Assembler → Gallery)
3. Inspect the TSV output in `tmp/` before proceeding to the next stage
4. Use `@verify` in your agent session to confirm the output matches expectations

This is the `[DEVELOPMENT ONLY]` persona area — not visible to scientist or pipeline personas.
