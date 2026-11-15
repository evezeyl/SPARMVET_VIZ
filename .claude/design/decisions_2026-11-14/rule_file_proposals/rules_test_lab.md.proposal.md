# Proposal: `.claude/rules/rules_test_lab.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked against `libs/test_lab/src/test_lab/bootstrapper.py` (read lines 100-200: it writes `spec_version: 1`, `data_engine`, `plot_engine`, `info.label`, `joins: {}`, `analysis_groups: {}`, `metadata_schema` only when a metadata file is given; no `output_fields`, no `plotting` key), ADR-100, ADR-094.

## 1. Table 4a, lines 130-143 (FACT; one CHANGES A RULE row)

Today (line 130): `| \`id:\` / \`info:\` block | Yes | \`id:\` equals the file name (ADR-092); no \`type:\` key |`
Proposed: `| \`id:\`, \`spec_version: 1\`, \`data_engine\`, \`plot_engine\`, \`info:\` | Yes | \`id:\` equals the file name (ADR-092); no \`type:\` key; the engine names are required (ADR-100 point 1) |`

Today (line 133): `| \`input_fields:\` with inferred types | Yes | From TSV headers + sampling |`
Proposed: `| \`input_fields:\` with inferred Polars types, \`label\`, \`original_name\` | Yes | From TSV headers + sampling; \`is_entity_key: true\` on \`id\`, \`sample_id\`, \`isolate_id\` (DEC13) |`

Today (line 135): `| \`output_fields: {}\` stub | Yes | Empty - user fills |`
Proposed (CHANGES A RULE: the stub no longer exists):
`| ~~\`output_fields: {}\` stub~~ | No | REMOVED (ADR-100 point 5, DEC23, 2026-11-14): no \`output_fields\`; the user ends a step list with \`polars_select\` when a column list is wanted. Tombstone expires two phases after this edit. |`

Today (line 140): `| \`analysis_groups:\` | No | User's responsibility |`
Proposed: `| \`analysis_groups:\` | Empty stub \`{}\` only | The key is required by the checker (T04); groups and plots are the user's responsibility |`
Why: `bootstrapper.py:189` writes `analysis_groups: {}`. The line 140 sentence and ADR-084's "never generate plot specs" stay true.

Today (line 143): `| \`final_contract:\` | No | User's responsibility |`
Proposed: `| ~~\`final_contract:\`~~ | No | REMOVED (ADR-100 point 5, DEC23): see the row above. |`

Also add a row: `| \`null_values\`, \`strip\` per schema | Yes | Stated, no default (DEC28); the code writes \`null_values: []\`, \`strip: false\` for the metadata schema |` (verify the data schemas get them too; I read only the metadata block).

## 2. Section 4b, "Known bugs" (lines 145-150) (FACT)

Today: three bugs to fix in TL-BOOTSTRAP-FIX-1 ("plotting" key, hardcoded `metadata_schema`, missing `joins: {}`), "Do not add new Bootstrapper features until TL-BOOTSTRAP-FIX-1 is complete."
Proposed: mark as HISTORICAL:
```
> **HISTORICAL (fixed; verified by reading `bootstrapper.py:177-189`, 2026-11-15):** the Bootstrapper no longer writes a `plotting` key (it writes `analysis_groups`), writes `metadata_schema` only when a metadata file was supplied, and writes `joins: {}`. The task TL-BOOTSTRAP-FIX-1 is not found in `tasks.md` (the status is not verified: Eve or the tasks archive says whether it is closed).
```
and delete the prohibition sentence only if Eve confirms the task is closed. Why: the three listed defects are absent from the code. I did not run the Bootstrapper.

## 3. Line 271, Bootstrapper correctness gate (CHANGES A RULE)

Today: `generated boilerplate MUST pass \`ConfigManager.load()\` without errors.`
Proposed: `generated boilerplate MUST pass the recipe checker (\`check_recipe\`, profile \`build\`: an empty \`analysis_groups\` and empty \`joins\` are the stubs) and \`ConfigManager.load()\` without errors.`
Why: ADR-100 point 3 (one checker for HOME, Blueprint, importer, scripts and tests; "New callers: ... the test-lab writers", `recipe_format_spec.md` section 14). Whether profile `build` accepts an empty `analysis_groups` was not run: see "Not settled".

## 4. Lines 13, 98, 114, 288 (no change)
`ConfigManager` still exists (`config_loader.py:57`), so the prohibitions against using it for synthetic configs stay true.

## Not settled
1. Whether the checker accepts the bootstrapper's output in profile `build` (not run).
2. Whether TL-BOOTSTRAP-FIX-1 is closed (not in `tasks.md`).
3. Whether the data-schema entries of the bootstrapper carry `null_values` and `strip` (only the metadata block was read).
