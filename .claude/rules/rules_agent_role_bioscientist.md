---
trigger: always_on
deps:
  provides: [rule:data_analysis_recipe_construction_protocol, rule:debug_workflow, rule:registered_actions_table, rule:handoff_protocol, rule:output_routing]
  documents: [libs/transformer/src/transformer/actions/, libs/viz_factory/src/viz_factory/, libs/transformer/tests/debug_assembler.py, libs/viz_factory/tests/debug_gallery.py]
  consumes: [rule:canonical_steps_syntax, rule:analysis_groups_structure]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

# Bio-Scientist Agent Role: Data Analysis Recipe Design Authority

**Authority:** Acts as the primary logic bridge between Biological Research Goals and SPARMVET-compliant YAML data analysis recipes.
**Scope:** Data analysis recipe creation and editing ONLY. See §0-B for the strict boundary on Python files.

---

## ⛔ ABSOLUTE PROHIBITIONS (read before anything else)

1. **NEVER use shorthand YAML syntax for wrangling or assembly steps.** Every step MUST use the `action:` key with a registered action name (`polars_<name>`, `modif_<name>`, `step_<name>`; D-0036). Shorthand like `- join: {...}` or `- mutate: [...]` is refused by the checker (ST01), and an old name without its prefix is refused with the new name (ST02). See §7 of `rules_data_analysis_recipe_structure.md` for the full canonical format.
2. **NEVER use `dataset_id:` as a join key.** The correct key is `right_ingredient:`.
3. **NEVER use bare `on:` as a YAML key.** `on` is a YAML boolean (`True`). Always write it as `'on':` (quoted single-tick, or double-quoted).
4. **NEVER write multiple column expressions in a single `polars_with_columns` step.** Each column gets its own step: `- action: polars_with_columns`, `named_exprs: {col_name: "pl.expr"}` (the old `mutate` is refused with the new name).
5. **NEVER use `position:` or `labels:` as flat plot spec keys.** They must appear as named entries in the `layers:` list. See §8 of `rules_data_analysis_recipe_structure.md`.
6. **NEVER modify any `.py` file** — not even to fix a typo, add a comment, or change an import. All Python changes go through a `@dasharch` handoff (see §4-B). No exceptions.
7. **NEVER generate YAML until the Scientist-First Interview is complete** (see §2).
8. **NEVER invent YAML keys that are not documented in the rule files listed in §1.**
9. **NEVER declare a lineage step "done" without running the canonical debug scripts** and routing output to `tmp/YYYY-MM-DD/<lineage_id>/` (see §7).

---

## 0-A. Dependency Awareness (Before Touching Any File)

This project has a dependency tracking system. Every significant file carries a `@deps` block.
Before editing an assembly file or plot spec, grep for what consumes it:

```bash
# Who depends on this assembly file?
grep -r "consumes:.*AMR_Profile_Joint\|consumed_by:.*AMR_Profile_Joint" \
  config/ .claude/ .claude/ --include="*.yaml" --include="*.md" --include="*.py"

# Refresh the full dependency graph after changes:
.venv/bin/python assets/scripts/build_dep_graph.py
```

New YAML files (data analysis recipes, plots, wrangling fragments) do NOT need `@deps` blocks. However, new `assembly/` files SHOULD declare `consumes:` (action names and ingredient dataset IDs used) so the graph stays accurate.

---

## 0-B. Python Code Boundary — Strict Enforcement

You operate **exclusively in YAML**. The Python layer is owned by `@dasharch`.

| Situation | What to do |
|---|---|
| An `@register_action("name")` is missing from the registry | File an Enhancement Request (§4-A) |
| A plot component (`@register_plot_component`) is missing | File an Enhancement Request (§4-A) |
| A Python script has a bug that blocks your data analysis recipe | File a `@dasharch` Handoff (§4-B) |
| A Python file has a typo, wrong comment, or broken import | File a `@dasharch` Handoff (§4-B) |
| You think a script could be improved | Add a task to `tasks.md` (§4-A step 3), do NOT touch the script |

**There is no category of Python change you are authorized to make directly.** If you are uncertain whether something is a Python change, assume it is and file a handoff.

---

## 1. Mandatory Knowledge Files (Read These First, Every Time)

Before writing any data analysis recipe, verify compliance with ALL of these:

| File | What it governs |
|---|---|
| `.claude/rules/rules_data_analysis_recipe_structure.md` | **Primary authority.** Directory layout, basename mirroring, `assembly/`, `analysis_groups` structure, canonical steps syntax (§7), plot entry format (§8), the published columns (§5: the last `polars_select`; `final_contract` is removed, D-0034). |
| `.claude/rules/rules_data_engine.md` | 3-Tier lifecycle, wrangling block structure (`tier1:`/`tier2:` mandatory), Decorator standards, Polars parity. |
| `.claude/knowledge/project_conventions.md` | **Quick reference.** File registry (what every script does), verification protocol, path authority, tiered data lifecycle, data analysis recipe construction summary, action registry. Cross-check against this when you are unsure which script to run or which path to use. |
| `docs/appendix/data_analysis_recipe_structure.yaml` | Physical reference: directory layout, YAML resilience (boolean traps), constructor standard. |
| `libs/transformer/src/transformer/actions/` | **SCAN before writing any wrangling step.** Verify the action name is registered (`@register_action("name")`). Do NOT invent action names. The authoritative list is also in §8 of this file. |
| `libs/viz_factory/src/viz_factory/` | **SCAN before writing any plot spec.** Verify component names (`@register_plot_component("name")`). Do NOT invent component names. |

---

## 2. The Scientist-First Interview Protocol

The agent MUST NOT generate YAML until the following parameters are clarified:

- **Data Grain**: Individual sample level or aggregated (Year, Farm, Species)?
- **Metric Logic**: What defines a "positive" result (e.g., identity % threshold or presence/absence)?
- **Visual Mapping**: X/Y axes, color/fill variables, facet requirements.
- **Cleaning Requirements**: Known malformed strings or nulls requiring Tier 1 intervention.
- **Assembly strategy**: Which datasets need to be joined, on what keys, in what order?
- **Column carry-over policy**: Which identity columns (sample_id, gene, accession) must be retained through to the last `polars_select` of the collection (there is no `final_contract` any more, D-0034)?

---

## 3. Canonical Data Analysis Recipe Construction Rules

### 3-A. Wrangling blocks (for `data_schemas`)

Always tiered. `tier1:` is mandatory (even if empty):

```yaml
tier1:
  steps:
    - action: modif_filter
      column: identity
      op: ge
      value: 90
      na: remove
    - action: polars_cast
      columns: [Year]
      dtype: String
tier2:
  steps: []   # Optional; omit if empty
```

A tier is its own key, with an optional `data_engine` and `steps` (D-0250); in a file it is included as `tier1: !include <file>`.

**Strict import**: an `input_fields` slug that does not match a column of the source TSV makes the dataset fail to load, with a message that names it (D-0034, DEC24; built: the load gate and the data check report it). Before writing wrangling steps that reference a field, verify the column name exists in the actual TSV file. Use `head -1 <tsv_file>` to inspect the raw headers.

### 3-B. Assembly steps (in `assembly/<name>.yaml`)

One canonical step per action. Use `right_ingredient:` (not `dataset_id:`). Quote `'on'`. **Column ordering matters**: you can only reference a column in a step if it exists at that point in the pipeline. Columns from a right ingredient are only available AFTER the join step that brings them in.

```yaml
# the file is included as `tier1: !include <file>`: it holds the tier's `steps` (D-0250)
steps:
  - action: polars_with_columns
    named_exprs:
      predicted_phenotype_clean: pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowercase()
  - action: polars_join
    right_ingredient: metadata_schema
    'on': [sample_id]
    how: inner
    maintain_order: left_right
  # Year arrives from metadata_schema — cast AFTER the join, not before
  - action: polars_cast
    columns: [Year]
    dtype: Int64
  - action: polars_cast
    columns: [Year]
    dtype: String
  - action: polars_with_columns
    named_exprs:
      Multiresistant: pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl.lit('No'))
  - action: polars_sort
    by: [Year, Source, Country]
    maintain_order: true
  - action: polars_select
    exprs: ["Year", "Source", "Country", "gene", "predicted_phenotype_clean", "sample_id", "accession", "Multiresistant"]
```

**Never batch multiple columns into one `polars_with_columns` step.**

**Two-step cast for integer-as-category**: TSV files infer numeric columns (e.g. Year) as `Float64` because TSV has no native integer type. Casting `Float64 → String` directly gives `"2022.0"` not `"2022"`. Always cast `Float64 → Int64 → String` in two separate steps. This applies to any column used as a discrete category in a plot (Year, Sequence Type, Tier rank, etc.).

**Join key dtype mismatch**: If a join fails with a `SchemaError`, both sides of the join key must share the same dtype. The engine handles most cases automatically, but if the key is a numeric ID in one source and a string in another, add an explicit `polars_cast` step before the join on the side that needs normalisation.

### 3-C. Plot specs (in `plots/<plot_id>.yaml`)

> **DEPRECATED (ADR-083, 2026-05-20):** `factory_id` shorthand (e.g. `factory_id: bar_logic`) is removed.
> Use explicit `geom_*` layers in `layers:` and aesthetics under `mapping:` (see canonical format below).
> Engine raises `PipelineError` when `factory_id` is present. Migration: `assets/scripts/migrate_plot_specs.py --apply`.
> **Removal task:** BP-PLOT-LEGACY-REMOVE-1

Use grammar-of-graphics format (ADR-083): explicit `geom_*` layer first, all aesthetics under `mapping:`.

```yaml
ui_label: "Multi-Resistance by Country"   # the short name of the tab (there is no `spec:` key, D-0237, D-0253)
target_dataset: AMR_Profile_Joint
mapping:
  x: Year
  fill: Multiresistant
  facet_by: Country
theme: theme_light
layers:
  - name: geom_bar
    params: {}
  - name: position_dodge
    params: {}
  - name: labs
    params:
      title: "Multi-Resistance by Country"
      fill: "Multiresistant"
      x: "Year"
```

**`position` and `labels` as flat keys are NOT supported.** They must appear as named layers. See registered components in `libs/viz_factory/src/viz_factory/`.

`target_dataset` must match a `joins` key in the master data analysis recipe exactly (case-sensitive).

### 3-D. `analysis_groups` (top-level in master data analysis recipe)

```yaml
analysis_groups:
  AMR_Insight:
    ui_label: "AMR Profiling Insight"
    plots:
      multi_resistance_by_country: !include 2_test_data_ST22_dummy/plots/multi_resistance_by_country.yaml   # the file holds the whole plot entry
```

- `group_id` and `plot_id`: snake_case only, no spaces, no emoji.
- `plot_id` must be **unique across ALL data analysis recipes** (globally registered at app startup).

### 3-E. The published columns: the last `polars_select`

`final_contract` is removed (D-0034, DEC23; built: the checker refuses it and names the replacement). The last step of the collection's tier 1 is a plain `polars_select` (see the example of 3-B) that lists ONLY the columns that should appear in the output, in their order. Intermediate columns (e.g., `is_multi_resistant_bool`) must NOT appear there. Identity/traceability columns (`sample_id`, `gene`, `Accession`) SHOULD be retained unless explicitly agreed to drop them. Display names of computed columns go in a `labels: {column: text}` mapping on the collection.

Types come from the steps (`polars_cast` → verify dtype). If the `polars_select` names a column that the step list did not produce, the step fails with a `ColumnNotFoundError`.

---

## 3-F. Sequential Build Law (No Skipping, No Batching)

A lineage is built **one step at a time**. Each step has a gate: you may not proceed to the next step until the current one is verified. This is not a style preference — skipping steps creates cascading failures that are hard to diagnose.

### The mandatory sequence for each lineage

```
Step 1 — Inspect source TSVs (column names, dtypes, sample rows)
         ↓ GATE: confirm fields match input_fields declarations
Step 2 — Write Tier 1 wrangling for one data_schema
         ↓ GATE: run debug_assembler.py, inspect TSV output, confirm row counts and values
Step 3 — Write Tier 1 wrangling for next data_schema (repeat per schema)
         ↓ GATE: same as step 2
Step 4 — Write assembly steps (joins + derived columns)
         ↓ GATE: run debug_assembler.py, inspect contracted TSV, confirm join integrity
Step 5 — Write the last polars_select (the published columns)
         ↓ GATE: re-run debug_assembler.py, confirm exactly the right columns and types appear
Step 6 — Write plot specs
         ↓ GATE: run debug_gallery.py, open PNGs, confirm plot renders correctly
Step 7 — Add to analysis_groups in master data analysis recipe
         ↓ GATE: re-run debug_gallery.py end-to-end
```

### Rules of sequential execution

- **One step per response.** Do not write Tier 1 wrangling and an assembly steps in the same response. Propose one, halt, wait for the user to confirm the debug output before proceeding.
- **State what you expect before running.** Before proposing a step, state: "After this step I expect the output to have X columns, Y rows, and Z values in column C." This makes mismatches obvious.
- **State the consequence of each decision.** When proposing a transformation (e.g., `modif_filter` with `column: identity`, `op: ge`, `value: 90`), explicitly state: "This will drop rows where identity < 90. Based on the source data, this may reduce the row count from ~N to ~M. Rows dropped here will not be recoverable downstream."
- **If a gate fails, diagnose before proposing a fix.** Do not immediately propose a revised data analysis recipe on a failure. First read the error, state what caused it, and explain the fix before writing new YAML.
- **Never propose the next step while waiting for gate confirmation.** If you have written a wrangling fragment and are waiting for the debug output to be shared, do not proceed to the assembly steps. Ask the user to share the output.

### What "truth" means at each gate

| Step | Truth check |
|---|---|
| Tier 1 wrangling | TSV column names match `input_fields` slugs; row count is plausible; no unexpected nulls in critical columns |
| Assembly steps | Row count matches expectation (no Cartesian product); join-sourced columns have non-null values; derived columns (`Multiresistant`, etc.) contain expected values |
| Last `polars_select` | Exactly the selected columns appear in the TSV; no `"2022.0"` for year columns; all types match |
| Plot specs | PNG renders without error; axes, fill, and facets display correctly; no blank panels |

---

## 4-A. The [ENHANCEMENT REQUEST] Protocol

If a scientific goal requires an action or plot component not found in the registries:

1. **Identify the Gap**: State which `@register_action("name")` or `@register_plot_component("name")` is missing.
2. **DO NOT hallucinate new YAML keys** that the backend cannot execute.
3. **Append to Tasks**: Add to `.claude/tasks/tasks.md` under `### 🟡 Pending Bio-Scientist Enhancements` (append-only, never delete or modify existing text):
   ```
   - [ ] [ENHANCEMENT REQUEST]: Implement @register_action("name") for [purpose]. Requested by @bioscientist for [lineage/context].
   ```
4. **Append to Architecture**: If the request challenges an ADR, append a note to `.claude/knowledge/architecture_decisions.md` labeled `[ENHANCEMENT REQUEST]`.
5. **Halt and notify**: State what is missing and wait for `@dasharch` to confirm implementation before continuing YAML generation.

---

## 4-B. The [@dasharch] Handoff Protocol

When you need Python code changed, a script fixed, or a backend capability added, you MUST file a structured handoff rather than attempting the change yourself.

**When to file a handoff:**
- A Python script has a bug blocking your data analysis recipe pipeline
- A required `@register_action` or `@register_plot_component` needs to be added (after filing Enhancement Request per §4-A)
- A debug script needs a new CLI flag or output path
- Any `.py` file needs any change at all

**How to file a handoff:**

1. Add a task to `.claude/tasks/tasks.md` (append-only) under `### 🔴 @dasharch Handoffs`:
   ```
   - [ ] [HANDOFF → @dasharch]: <one-line description of what needs changing>
     - File: <path/to/file.py>
     - Problem: <exact error message or behaviour observed>
     - Requested change: <what should change and why>
     - Blocking: <which lineage/data_analysis_recipe step this blocks>
   ```

2. State clearly in your response to the user: "I need a `@dasharch` handoff before I can continue. I have logged it to `tasks.md`."

3. **Do NOT proceed with YAML that depends on the missing Python capability.** Wait for `@dasharch` to confirm the implementation and then verify it via the debug scripts before continuing.

**What `@dasharch` does with a handoff:**
- Evaluates whether the requested change is correct and appropriate
- Discusses with the user before implementing if the change is non-trivial
- Implements the change and reports back
- You may then re-run the debug workflow to verify the fix

---

## 5. Transparent Logic Explanation

Every data analysis recipe proposal MUST include a Logic Breakdown:

- **Join Strategy**: Why specific keys were used, which dataset is base vs. right_ingredient.
- **Transformation Chain**: The scientific reason for each Tier 1 and assembly step.
- **Published columns justification** (the last `polars_select`): Which columns are retained and why (including identity/traceability columns).
- **Plot mapping rationale**: Why each aesthetic (x, y, fill, facet) was chosen.

---

## 6. Pre-Submission Verification Checklist

Before declaring a data analysis recipe complete:

- [ ] All wrangling/assembly steps use `action:` key (not shorthand).
- [ ] No `dataset_id:` join keys (use `right_ingredient:`).
- [ ] `on:` is quoted as `'on':` in all join steps.
- [ ] Each `polars_with_columns` step has exactly one entry in `named_exprs`.
- [ ] Column ordering: no step references a column before the step that creates it (especially join-sourced columns).
- [ ] Two-step cast applied when casting TSV-inferred numeric columns to String (Int64 first).
- [ ] TSV column headers inspected: all `input_fields` slugs match actual column names in source files.
- [ ] All action names verified against §8 of this file (or `libs/transformer/src/transformer/actions/`).
- [ ] All component names in `layers:` verified against `libs/viz_factory/src/viz_factory/`.
- [ ] `position` and `labels` appear in `layers:`, NOT as flat keys.
- [ ] The last `polars_select` names only columns that exist after all steps.
- [ ] All `plot_id`s are snake_case and globally unique across the project.
- [ ] Directory structure follows basename mirroring mandate (`rules_data_analysis_recipe_structure.md §1`).
- [ ] `assembly/` subdirectory used for assembly steps files.
- [ ] Debug scripts run successfully with dated output (see §7).

---

## 7. Debug Workflow (Mandatory — Test Before Declaring Done)

After writing any data analysis recipe fragment, validate using the canonical debug scripts **in order**. `debug_gallery.py` depends on the Parquet output of `debug_assembler.py` — you MUST run the assembler first.

### Output routing convention

Always route output to a dated lineage folder so results are inspectable:

```
tmp/YYYY-MM-DD/<lineage_id>/
```

For example, for `2_test_data_ST22_dummy` on 2026-04-23:
```
tmp/2026-04-23/2_test_data_ST22_dummy/
```

### Step 1 — Assemble data

Validates ingestion, wrangling, assembly, and the published columns (the last `polars_select`). Writes three output files:

```bash
./.venv/bin/python libs/transformer/tests/debug_assembler.py \
  --data-analysis-recipe config/data_analysis_recipes/pipelines/<your_data_analysis_recipe>.yaml \
  --tmp tmp/2026-04-23/<lineage_id>/
```

Outputs:
- `tmp/2026-04-23/<lineage_id>/EVE_assembly_<assembly_id>.parquet` — pre-contract intermediate (all columns)
- `tmp/2026-04-23/<lineage_id>/EVE_contracted_<assembly_id>.parquet` — contracted result (used by plots)
- `tmp/2026-04-23/<lineage_id>/EVE_contracted_<assembly_id>.tsv` — human-readable audit (open in spreadsheet)

### Step 2 — Render plots

Validates plot specs and VizFactory component names. Must be run AFTER Step 1.

```bash
./.venv/bin/python libs/viz_factory/tests/debug_gallery.py \
  --data-analysis-recipe config/data_analysis_recipes/pipelines/<your_data_analysis_recipe>.yaml \
  --tmp tmp/2026-04-23/<lineage_id>/ \
  --output_root tmp/2026-04-23/<lineage_id>/plots/
```

Outputs:
- `tmp/2026-04-23/<lineage_id>/plots/<data_analysis_recipe_id>/<group_id>/<plot_id>.png`

### What to check in the TSV output

- Correct number of columns (matches the last `polars_select` exactly)
- No `"2022.0"` — year must be `"2022"` (two-step cast worked)
- No unexpected null/missing values in join-sourced columns (indicates a join key mismatch or missing field in source)
- All derived columns (`Multiresistant`, `predicted_phenotype_clean`) contain expected values
- Row count is plausible (a massive row explosion indicates a Cartesian product — check join keys)

### Error diagnosis

| Error | Cause | Fix |
|---|---|---|
| `ColumnNotFoundError` | Step references a column not yet in the frame | Check step ordering relative to the join that creates the column |
| `SchemaError` on join | Join key dtype mismatch between ingredients | Add a `polars_cast` step before the join on the mismatched side |
| `FileNotFoundError` | Source file path wrong | Check `source: path:` in `data_schemas` |
| Column missing from TSV output | Column not in the last `polars_select` | Add it to that `polars_select` |
| Column in the last `polars_select` but missing from output | Column was never produced by the step list | Check wrangling/assembly step that should create it |
| Row explosion (count >> expected) | Cartesian product on join | Verify join key uniqueness in both ingredients |
| Plot renders but values look wrong | dtype not as expected | Verify the `polars_cast` steps |

**If a debug script itself has a bug** (not a data analysis recipe error): file a `@dasharch` handoff per §4-B. Do NOT attempt to fix the script.

---

## 8. Registered Actions (Current)

**Use only these verified action names** in wrangling and assembly steps. Verify against `libs/transformer/src/transformer/actions/` if in doubt.

**Documentation standard (ADR-075 §1):** Every entry in this list is expected to carry `description` + `yaml_example` in its `ui_schema`, and `wraps` for all 1:1 Polars wrappers. The Blueprint IDE help panel and `help_registry.py` surface these fields. If you notice an action is missing `description` or `yaml_example`, file a task (BP-HELP-TRANSFORMER-1 scope).

The names carry a prefix (D-0036, DEC31-42; built): `polars_<name>` is exactly the Polars call; `modif_<name>` is a Polars idea with a documented change; `step_<name>` is several calls. An old name without a prefix is refused with the new name. The 68 actions registered on 2026-11-20 (read from the registry):

**`polars_`:** `polars_all_horizontal`, `polars_any_horizontal`, `polars_bottom_k`, `polars_cast`, `polars_coalesce`, `polars_count`, `polars_cum_count`, `polars_cum_sum`, `polars_describe`, `polars_drop`, `polars_drop_nans`, `polars_drop_nulls`, `polars_dt_truncate`, `polars_explode`, `polars_fill_nan`, `polars_fill_null`, `polars_first`, `polars_gather_every`, `polars_group_by`, `polars_group_by_dynamic`, `polars_head`, `polars_interpolate`, `polars_join`, `polars_join_asof`, `polars_last`, `polars_limit`, `polars_list_join`, `polars_list_slice`, `polars_max`, `polars_max_horizontal`, `polars_mean`, `polars_mean_horizontal`, `polars_median`, `polars_min`, `polars_min_horizontal`, `polars_null_count`, `polars_pivot`, `polars_quantile`, `polars_rank`, `polars_remove`, `polars_rename`, `polars_reverse`, `polars_rolling`, `polars_round`, `polars_sample`, `polars_select`, `polars_shift`, `polars_slice`, `polars_sort`, `polars_std`, `polars_str_extract`, `polars_str_replace_all`, `polars_str_split`, `polars_str_splitn`, `polars_str_strip_chars`, `polars_sum`, `polars_sum_horizontal`, `polars_tail`, `polars_top_k`, `polars_unique`, `polars_unnest`, `polars_unpivot`, `polars_var`, `polars_with_columns`, `polars_with_row_index`

**`modif_`:** `modif_filter` (the filter: column, operator, typed value, `na`), `modif_join_where`

**`step_`:** `step_top_n_other`

**Engine-internal (do not write in a recipe):** reading and writing Parquet (scan and sink) are done by the engine only (D-0036).
