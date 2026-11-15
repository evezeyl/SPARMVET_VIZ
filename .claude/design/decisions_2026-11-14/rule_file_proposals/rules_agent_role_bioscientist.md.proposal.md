# Proposal: `.claude/rules/rules_agent_role_bioscientist.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited.
Checked against: the registry (run: `AVAILABLE_WRANGLING_ACTIONS` holds 68 names), `recipe_check.py` (ST01, ST02, ST06, T07, J09, FD02), the shipped
`config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml` and its `assembly/`, `input_fields/`, `wrangling/` files,
`libs/transformer/tests/debug_assembler.py` and `libs/viz_factory/tests/debug_gallery.py` (both RUN on that recipe on 2026-11-15: assembly complete, 3 of 3 plots rendered),
ADR-100, ADR-102, ADR-103.
Each change: FACT (corrects a fact) or CHANGES A RULE.

---

## 1. Prohibition 1 (line 19) (FACT)

Today (line 19, middle): `Shorthand like \`- join: {...}\` or \`- mutate: [...]\` is silently ignored by the engine and produces wrong data with no error.`
Proposed: `Shorthand like \`- join: {...}\`, an old action name (\`join\`, \`mutate\`, \`cast\`, \`sort\`) or an unknown parameter is refused by the checker before the run (ST01, ST02, ST06). A step must name a registered action (section 8).`
Why: `recipe_check.py:406, 428, 451`; the names `join`, `mutate`, `cast`, `sort` are not in the registry.

## 2. Prohibition 2 (line 20) (FACT)

Today: `2. **NEVER use \`dataset_id:\` as a join key.** The correct key is \`right_ingredient:\`.`
Proposed: `2. **NEVER use \`dataset_id:\` as a key of a join step.** The step names its right table with \`right_ingredient:\`. (\`dataset_id\` is only the key of an entry of the join's \`ingredients:\` list.)`
Why: `recipe_check.py` J04 requires `ingredients: [{dataset_id: <schema id>}]`; shipped `2_test_data_ST22_dummy.yaml` lines under `joins:`. The old sentence reads as if `dataset_id` were forbidden everywhere.

## 3. Prohibition 4 (line 22) (FACT)

Today: `4. **NEVER write multiple column expressions in a single \`mutate\` step.** Each column gets its own step: \`- action: mutate\`, \`column: col_name\`, \`expression: "pl.expr"\`.`
Proposed: `4. **NEVER hide several decisions in one step.** \`polars_with_columns\` takes \`named_exprs: {name: expression}\`; write one step per scientific decision so each can be read, explained and audited. A formula may use only the allowed Polars functions (checked by \`formula_check.py\`); anything else is refused.`
CHANGES A RULE only in its reason (one step per decision instead of "one column per mutate"); the action \`mutate\` does not exist.
Why: registry (68 actions, no `mutate`); shipped `AMR_Profile_Joint.yaml` uses one `polars_with_columns` per derived column; ADR-099 point 14 and ADR-100 point 10 (formula allow-list, built `fe856c26`).

## 4. Prohibition 9 (line 27) and the debug scripts (FACT)

Today: `9. **NEVER declare a lineage step "done" without running the canonical debug scripts** ...`
Proposed: no change to the sentence. Section 7 below is corrected so that "canonical debug scripts" is still true. Both scripts were RUN today and work on a format-1 recipe.

## 5. Mandatory knowledge files, lines 71-72 (FACT)

Today (line 71): `... canonical steps syntax (§7), plot spec format (§8), \`final_contract\` whitelist (§5). |`
Proposed: `... canonical steps syntax (§7), plot spec format (§8), published columns (§5). |`
Today (line 72): `... Decorator standards, Polars parity. |`
Proposed: `... Decorator standards (action names, parameters, determinism, missing values). |`
Why: `final_contract` removed (ADR-100 point 5); the "Polars parity mandate" is replaced (see `rules_data_engine.md.proposal.md` change 7).
Line 74 also: `YAML resilience (boolean traps)` stays true (an unquoted `on` is refused, T07).

## 6. Section 2, line 89 (FACT)

Today: `- **Column carry-over policy**: Which identity columns (sample_id, gene, accession) must be retained through to the \`final_contract\`?`
Proposed: `- **Column carry-over policy**: Which identity columns (sample_id, gene, accession) must be retained through to the last \`polars_select\` step of the join?`
Add a new bullet after it:
`- **Missing values**: For each filter, what must happen to rows with no value in the column (\`na: keep\` or \`na: remove\`; there is no default) (ADR-103).`
CHANGES A RULE for the new bullet only.
Why: ADR-100 point 5; ADR-103 points 1, 2, 8 (every filter states `na`); `modif_filter` requires `na` (shipped `2_test_data_ST22_dummy/wrangling/amr_data.yaml`).

## 7. Section 3-A, lines 95-111 (CHANGES A RULE)

Today (lines 99-109): the block with `action: filter_range` (`columns`, `min`) and `action: cast`; line 111 "Silent Skip Warning: ... the engine silently skips it - no error, no warning."
Proposed block:
```yaml
wrangling:
  tier1:
    - action: modif_filter
      column: identity
      op: ge
      value: 90
      na: remove
    - action: polars_cast
      columns: [Year]
      dtype: Int64
  tier2: []   # Optional; omit if empty
```
Proposed replacement of line 111:
```
**Strict reading (ADR-100 point 4, DEC24):** only the fields declared in `input_fields` are read. A declared field whose column is missing from the file fails with a message; it is never skipped. A column of the file that is not declared is not read. Before writing steps, inspect the real header (`head -1 <tsv_file>`) and declare each field with its `original_name` and its Polars `type`.
```
Also replace line 97 `Always tiered. \`tier1:\` is mandatory (even if empty):` by `A schema's \`wrangling\` is required and has \`tier1\` (mandatory, even if empty); \`tier2\` applies only when the schema is plotted directly (check S07):`.
CHANGES A RULE (silent skip becomes a failure; `filter_range` becomes `modif_filter` with required `na`).
Why: `filter_range` is not registered; `modif_filter` takes `column`, `op`, `value`, `na` (ADR-100 point 6, DEC39, DEC29); ADR-103 point 2; DEC24 built `9bfdaf4c`.

## 8. Section 3-B, lines 113-144 (CHANGES A RULE for 144, FACT for the rest)

8a. Line 115 stays, except `Use \`right_ingredient:\` (not \`dataset_id:\`)` becomes `Use \`right_ingredient:\` in the join step`.
8b. Today (lines 117-138): the block with `action: mutate`, `join` (`'on': sample_id`), `cast`, `sort`. Proposed: the block of `rules_data_analysis_recipe_structure.md.proposal.md` change 8 (taken from the shipped `AMR_Profile_Joint.yaml`), verbatim. Keep the comment line `# Year arrives from metadata_schema, cast AFTER the join, not before`.
8c. Today (line 140): `**Never batch multiple columns into one \`mutate\` step.**`. Proposed: delete the line (covered by change 3).
8d. Today (line 142, "Two-step cast"): same text with `cast` as the action name. Proposed: replace the last two sentences by: `Always cast Float64 to Int64 and then to String, in two separate \`polars_cast\` steps. A Float64 to Int64 cast that would drop decimals fails (DEC49); a cast is always a written step.`
8e. Today (line 144): `**Join key dtype mismatch**: If a join fails with a \`SchemaError\`, both sides ... The engine handles most cases automatically, but if the key is a numeric ID in one source and a string in another, add an explicit \`cast\` step before the join ...`
Proposed:
```
**Join key types (ADR-102)**: a join keeps the types the recipe declares. The checker refuses a join whose key columns have different declared types (J09), a key column that one side does not declare (J10), and key lists of unequal length (J11); the build refuses them too. Nothing is cast to String for you. Declare the key with the same text type in `input_fields` of both tables, or write a `polars_cast` step before the join (it changes only the left table). A float join key gets the advice J13; a self-join on the same key gets the advice J12; a join step is never skipped silently.
```
CHANGES A RULE (the engine does not "handle most cases automatically": there is no hidden cast).
Why: ADR-102 points 1 to 5 (`architecture_decisions.md:5234`); `recipe_check.py` J09 to J13.

## 9. Section 3-C, line 177 and the block (FACT, small)

Today: no `facet_by` problem is certain; see "Not settled" 1. Add after line 177: `A plot reads the published columns of its target table; a column that no step publishes is not available to the plot (the checker reports it where it can know it).` Delete this addition if Eve prefers to keep the section as it is; it is not required by a decision.
Why: ADR-100 point 5 (published columns are the last tier-1 step).

## 10. Section 3-E "final_contract whitelist", lines 194-208 (CHANGES A RULE)

Today (lines 194-208): the whole subsection (`final_contract:` block with `Year: string` ...).
Proposed (replaces the subsection):
```
### 3-E. Published columns (the last step of tier 1)

> **REMOVED (ADR-100 point 5, DEC23, 2026-11-14):** the `final_contract` block no longer exists. Replacement: end `tier1` of the join with a `polars_select` step (or `polars_drop`).
> **Tombstone expires:** two phases after this edit (add the task entry).

End the step list with `polars_select` and list ONLY the columns that should be published. Intermediate columns (e.g. `is_multi_resistant_bool`) are left out of the list. Identity and traceability columns (`sample_id`, `gene`, `accession`) SHOULD be kept unless explicitly agreed otherwise. Display names go in `labels` on the join.

```yaml
  - action: polars_select
    exprs: ["Year", "Source", "Country", "predicted_phenotype_clean", "sample_id", "Multiresistant"]
```

A column named in `polars_select` that no earlier step produced is an error of that step, reported with its place.
```
Why: ADR-100 point 5; shipped `AMR_Profile_Joint.yaml` last step.

## 11. Section 3-F, lines 222, 226, 227, 239, 249 (FACT)

- Line 226: `run debug_assembler.py, inspect contracted TSV, confirm join integrity` becomes `run debug_assembler.py, inspect the published TSV (the file name still says "contracted"), confirm join integrity`.
- Line 227: `Step 5 - Write final_contract` becomes `Step 5 - Write the last polars_select step of the join`.
- Line 239: `(e.g., \`filter_range identity min: 90\`)` becomes `(e.g., \`modif_filter\` on \`identity\` with \`op: ge\`, \`value: 90\`)`; and add at its end: `State also what happens to rows with no value (the \`na\` choice).`
- Line 249 (table): `| \`final_contract\` | Exactly the declared columns ...` becomes `| Last \`polars_select\` | Exactly the selected columns appear in the TSV; no "2022.0" for year columns; all types match |`.
Why: as above; the debug script still writes `EVE_contracted_*` files (`debug_assembler.py:144`), so the file name is kept.

## 12. Section 5, line 308 (FACT)

Today: `- **\`final_contract\` justification**: Which columns are retained and why ...`
Proposed: `- **Published columns justification**: Which columns the last \`polars_select\` keeps and why (including identity/traceability columns).`
Add a bullet: `- **Missing values**: For each filter, the \`na\` choice and what it does to the row count (ADR-103).`

## 13. Section 6 checklist, lines 317-327 (FACT, one CHANGES A RULE)

Proposed list (replaces lines 317-327; the other lines stay):
```
- [ ] Every step has `action:` with a registered action name (section 8); the checker (`check_recipe`, profile `run`) reports no error.
- [ ] No `dataset_id:` as a key of a join step (use `right_ingredient:`).
- [ ] `'on':` is quoted in all join steps (an unquoted `on` is refused, T07).
- [ ] Each derived column is its own `polars_with_columns` step (one decision per step).
- [ ] Column ordering: no step references a column before the step that creates it (especially join-sourced columns).
- [ ] Two-step cast (Int64, then String) applied when casting TSV-inferred numeric columns to String.
- [ ] Join key columns have the same declared type on both sides (J09); no cast is assumed.
- [ ] Every `modif_filter` states `na`.
- [ ] TSV column headers inspected: all `input_fields` slugs match actual column names in source files.
- [ ] All action names verified against §8 of this file (or `libs/transformer/src/transformer/actions/`).
- [ ] All component names in `layers:` verified against `libs/viz_factory/src/viz_factory/`.
- [ ] `position` and `labels` appear in `layers:`, NOT as flat keys.
- [ ] The last `polars_select` of each join lists only columns that exist after all steps.
```
Why: changes 1 to 10. CHANGES A RULE: the two new items (join key types, `na`).

## 14. Section 7, lines 354, 363-364, 383, 396-399 (FACT)

- Line 354: `Validates ingestion, wrangling, assembly, and \`final_contract\`.` becomes `Validates ingestion, wrangling, assembly and the published columns (the last polars_select).`
- Lines 363-364: `pre-contract intermediate (all columns)` and `contracted result (used by plots)` become `intermediate result before the last polars_select (all columns)` and `published result (used by plots); the file is still named EVE_contracted_*`.
- Line 383: `(matches \`final_contract\` keys exactly)` becomes `(matches the last polars_select exactly)`.
- Line 394: `| \`SchemaError\` on join | Join key dtype mismatch between ingredients | Add \`cast\` step before join on the mismatched side |` becomes `| Join key types differ (checker J09, or the build refuses) | The key is declared with different types in the two tables | Declare the same type in both \`input_fields\`, or add a \`polars_cast\` step before the join (it changes only the left table) |`.
- Lines 396-397: replace the two rows with `| Column missing from TSV output | The last \`polars_select\` does not list it | Add it to that step |` and `| Column named in \`polars_select\` but missing from output | No earlier step produced it | Check the step that should create it |`.
- Line 399: `| Plot renders but values look wrong | \`final_contract\` dtype mismatch | Verify cast steps match declared types |` becomes `| Plot renders but values look wrong | A column has a different type than the plot expects | Verify the cast steps and the declared types |`.
Why: as above; both scripts were RUN and work (assembly complete; 3 of 3 plots).

## 15. Section 8, the action list (lines 405-425) (FACT; replaces the whole list)

Today (lines 411-425): the lists "Cleaning", "Expressions", "Analytical", "Advanced", "Reshaping", "Performance", "Relational", "Persistence" with the old names (`fill_nulls`, `summarize`, `derive_categories`, `percentile`, `join`, `cast`, `sort`, ...).
Proposed (replaces lines 407 and 411-425; keep the "Documentation standard" paragraph, line 409):
```
**Use only these verified action names** in wrangling and join steps (68 registered; verified by listing `AVAILABLE_WRANGLING_ACTIONS`). A `polars_` action is exactly the Polars call of that name (ADR-100 point 6, DEC32); `modif_` is a Polars call with a stated change; `step_` is a composite. Verify against `libs/transformer/src/transformer/actions/` if in doubt.

**Rows:** `modif_filter`, `polars_remove`, `polars_drop_nulls`, `polars_drop_nans`, `polars_unique`, `polars_head`, `polars_tail`, `polars_limit`, `polars_slice`, `polars_top_k`, `polars_bottom_k`, `polars_gather_every`, `polars_sample`, `polars_sort`, `polars_reverse`

**Columns:** `polars_select`, `polars_drop`, `polars_rename`, `polars_with_columns`, `polars_cast`, `polars_with_row_index`, `polars_round`, `polars_coalesce`

**Missing values:** `polars_fill_null`, `polars_fill_nan`, `polars_interpolate` (and `polars_drop_nulls`, `polars_drop_nans` above)

**Text:** `polars_str_extract`, `polars_str_replace_all`, `polars_str_split`, `polars_str_splitn`, `polars_str_strip_chars`

**Lists and structs:** `polars_list_join`, `polars_list_slice`, `polars_explode`, `polars_unnest`

**Order and time:** `polars_shift`, `polars_dt_truncate`, `polars_rolling`, `polars_group_by_dynamic`, `polars_cum_count`, `polars_cum_sum`, `polars_rank`

**Aggregation:** `polars_group_by`, `polars_count`, `polars_sum`, `polars_mean`, `polars_median`, `polars_min`, `polars_max`, `polars_std`, `polars_var`, `polars_quantile`, `polars_first`, `polars_last`, `polars_null_count`, `polars_describe`

**Across columns:** `polars_all_horizontal`, `polars_any_horizontal`, `polars_max_horizontal`, `polars_mean_horizontal`, `polars_min_horizontal`, `polars_sum_horizontal`

**Reshaping:** `polars_pivot`, `polars_unpivot`

**Joins (tier 1 only, check ST05):** `polars_join`, `polars_join_asof`, `polars_join_where`

**Composite:** `step_top_n_other`

> **REMOVED (ADR-100 points 6 and 7, DEC31, DEC40, 2026-11-13/14):** `fill_nulls`, `replace_values`, `drop_duplicates`, `unique_rows`, `recode_values`, `sanitize_column_names`, `keep_columns`, `drop_columns`, `strip_whitespace`, `round_numeric`, `filter_range`, `add_constant`, `filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `rename_columns`, `unique`, `regex_extract`, `cast`, `label_if`, `mutate`, `regex_replace`, `null_if`, `window_agg`, `fill_nulls_direction`, `sort`, `cum_sum`, `cum_count`, `date_extract`, `date_truncate`, `list_slice`, `list_join`, `is_in`, `not_in`, `z_score`, `value_counts`, `describe_stats`, `select_by_pattern`, `horizontal_stats`, `any_horizontal`, `all_horizontal`, `interpolate`, `split_and_explode`, `split_column_to_parts`, `divide_columns`, `split_column`, `unpivot`, `explode`, `unnest`, `split_to_list`, `to_struct`, `pivot`, `summarize`, `count_by_group`, `join`, `join_filter`, `percentile`, `derive_categories`, `top_n_other`, `shift`, `sample`, `coalesce`.
> Replacement: the `polars_` action of the same Polars name, `modif_filter` for every filter, `polars_group_by` for `summarize`, `polars_str_splitn` for `split_column`; no replacement for `percentile` (DEC40). Old names are refused by the checker with the nearest valid name (ST02) and by the migration tool.
> **Tombstone expires:** two phases after this edit (add the task entry).

**Persistence (engine-internal, do not write):** `scan_parquet`, `sink_parquet` (DEC42).
```
Why: registry listing (68, no overlap, run today). The removed list is built from today's lines 411-425; the sentence "no replacement for `percentile`" is DEC40; `derive_categories` removal is NOT CONFIRMED by Eve (ADR-100 OPEN list), so Eve may want to delete that name from the banner, see "Not settled" 3. Names in the banner that are also registered (for example `shift`, `sample`) mean the old unprefixed name.
Kind: FACT (a list is corrected; the sentence "Use only these verified action names" is unchanged in force).

## 16. Line 75 (no change)

The sentence "(`@register_action("name")`)" is still true.

---

## Not settled

1. `facet_by`: the plot block (lines 158-161) writes it under `mapping`, as every shipped plot does; `recipe_spec.yaml` lists it as a key of `spec`. Not decided which is right; the proposal leaves the block alone.
2. SETTLED: `wraps` still exists in the schema (`polars_calls.py:229`) next to the new field `polars` (`exact` or `wrapper`, line 228). Line 409 needs no change; the sentence may add: `and a polars field (exact or wrapper)`.
3. `derive_categories` (change 15): its removal is in ADR-100's OPEN list (no record of Eve deciding). The action is gone from the code. Eve may keep or drop the name in the banner.
4. The 68 count comes from the code today; the spec says the registry may grow (ADR-100 point 6 note: `head`, `tail`, ... were added; more are planned). The proposed text says "68 registered" and points to the registry; a build task should regenerate this list (a test that compares the rule file with the registry would stop the drift; not proposed as a rule).
