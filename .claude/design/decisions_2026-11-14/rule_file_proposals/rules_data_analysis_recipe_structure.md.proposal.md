# Proposal: `.claude/rules/rules_data_analysis_recipe_structure.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited.
Checked against: `libs/utils/src/utils/recipe_check.py` (codes T07, F01, T11, FD02, ST01, ST02, J04 to J13, S01 to S09),
`libs/utils/src/utils/recipe_spec.yaml`, `libs/utils/src/utils/recipe_loader.py`, the 68 registered actions, the shipped recipes
`config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml` and its folder, ADR-100, ADR-102, ADR-106.
Read the numbered changes in order. Kind: FACT = corrects a fact only; "CHANGES A RULE" = a rule changes.

---

## 1. Front matter, line 4 (FACT)

Today (line 4): `  provides: [rule:canonical_steps_syntax, rule:directory_taxonomy, rule:analysis_groups_structure, rule:final_contract]`

Proposed:
```
  provides: [rule:canonical_steps_syntax, rule:directory_taxonomy, rule:analysis_groups_structure, rule:published_columns]
```
Why: `final_contract` is removed (ADR-100 point 5, DEC23, built, cache version "4"). Other files list `rule:final_contract` in `consumed_by`/`consumes`: run `build_dep_graph.py` after the edit.

## 2. Section 2, line 26 (FACT)

Today (line 26): `- \`output_fields/\`: Defines the terminal contract schemas.`

Proposed (replaces the line):
```
- ~~`output_fields/`~~ **REMOVED (ADR-100 point 5, DEC23, 2026-11-14):** there is no `output_fields` key and no folder for it. The published columns are the last step of tier 1 of a schema or join (`polars_select` or `polars_drop`).
  Replacement: `polars_select` (see section 5).
```
Why: `recipe_spec.yaml` `renamed.top.output_fields` and `renamed.schema.output_fields`: "removed: end the step list ... with a polars_select step". Kept visible, as `rules_legacy_management.md` asks.

## 3. Section 2, line 27 (FACT)

Today (line 27): `- \`join/\`: Defines the join steps (\`steps:\` key only) for joining multiple ingredients into a collection. One file per join block (e.g., \`AMR_Profile_Joint.yaml\`). Top-level data analysis recipe key: \`joins:\`.`

Proposed:
```
- `assembly/`: Defines the steps of one join (the content of `steps:`, that is `tier1:` and optionally `tier2:`) for joining several ingredients into a collection. One file per join block (e.g. `AMR_Profile_Joint.yaml`). Top-level recipe key: `joins:`.
```
Why: both shipped recipe folders that have joins use `assembly/` (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/assembly`, `.../2_test_data_ST22_dummy/assembly`); no recipe folder is named `join/`. The checker does not look at folder names, so this is a fact about the shipped standard, not a check.

## 4. Section 2, new bullet after line 28 (FACT)

Proposed addition (new last bullet of section 2):
```
- An included file holds the content of the key it is included under, without repeating the key (`plots/x.yaml` starts with `target_dataset:`, not with `spec:`). A file that repeats the key is refused (check F01). An include path must stay inside the project (check T11).
```
Why: line 142 of the same file says the included plot file "must contain a single `spec:` root key" and that `ConfigManager` unnests it. The loader now refuses that (`recipe_loader.py:44-46`, F01); every shipped plot file starts with `target_dataset:`.

## 5. Section 5 (lines 41-44), "Explicit Whitelisting (The Final Contract)" (CHANGES A RULE)

Today (lines 41-44):
```
## 5. Explicit Whitelisting (The Final Contract)
- **The Protocol**: The `final_contract` block in a pipeline or assembly data analysis recipe is an **Exclusive Whitelist**. 
- **The Effect**: Any column existing in the dataframe but not explicitly listed in the `final_contract` will be dropped by the Assembler projection guard. 
- **Developer Rule**: Always check the `final_contract` if a newly created column is missing from the output TSV/Parquet.
```

Proposed (replaces the section):
```
## 5. Published Columns (replaces the Final Contract)

> **REMOVED (ADR-100 point 5, DEC23, 2026-11-14):** `final_contract` (and the schema `output_fields`) no longer exist. They were a second, hidden column selection.
> A recipe that still has them is refused (check T03 or the "renamed" message) with the replacement named.
> **Tombstone expires:** two phases after the phase that records this edit (add the task entry as the legacy rule asks).

- **The Protocol**: the columns a schema or a join publishes are the columns left by its **last tier-1 step**. To publish a chosen list, end the step list with `polars_select` (keep these columns) or `polars_drop` (remove these columns). Nothing else selects columns.
- **The Effect**: with no `polars_select` or `polars_drop` at the end, every column of the table is published. Nothing is dropped silently.
- **Display names**: write them in `labels` on the join (`labels: {column: display text}`), not in a contract.
- **Developer Rule**: if a column is missing from a published table, read the last `polars_select`/`polars_drop` step of its tier 1.
```
CHANGES A RULE (the whitelist becomes an explicit last step).
Why: ADR-100 point 5 (`architecture_decisions.md:5180` ff.; DEC23 in `recipe_format_spec.md`), `recipe_spec.yaml` `renamed.top.final_contract`, shipped example `2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml` (last step `polars_select`).

## 6. Section 6 (lines 46-48), "Biological Typing" (FACT, plus one CHANGES A RULE sentence)

Today (lines 47-48): `columns MUST be cast to appropriate types in the assembly steps.` / `... MUST be cast to \`int\` or \`string\` in the Tier 2 assembly ...`

Proposed:
```
- **The Protocol**: To make Plotnine draw a discrete scale (for example Year or Sequence Type), the column must have a discrete type when the plot reads it.
- **The Rule**: Numeric values used as categories (integer years) are cast by a written step (`polars_cast`) in tier 1 of the join (or tier 2 where the join has one), or declared with a discrete type in `input_fields`. No cast is made for you (ADR-102, ADR-100 DEC49). A cast from a decimal number to an integer that would lose decimals fails; cast Float64 to Int64 only when the values are whole, then to String.
```
CHANGES A RULE only by the last sentence (DEC49); the rest names the step by its present action name.
Why: DEC49 (ADR-100 point 4); the shipped `AMR_Profile_Joint.yaml` steps 3 use `polars_cast` twice (`Int64`, then `String`). Verify DEC49's exact failure condition before pasting (see "Not settled" 1).

## 7. Section 7, heading and first paragraph (lines 52-54) (FACT)

Today (line 54, start): `**ALL** wrangling and assembly steps MUST use the canonical \`action:\` key format. Shorthand formats (using the action name as the YAML key ...) are **NOT supported by the engine** and are **silently skipped** ...`

Proposed (replace the paragraph; keep the heading):
```
**ALL** wrangling and join steps MUST use the `action:` key, and the value MUST be a registered action name (`polars_*`, `modif_*`, `step_*`: 68 actions today). A step with no `action`, an unknown action name (an old name such as `join`, `mutate`, `cast`, `sort` is one), an unknown parameter, or a missing required parameter is **refused by the checker before the run** (checks ST01, ST02, ST06). Nothing is skipped silently (ADR-100, ADR-104).
```
Why: the old text says shorthand is "silently skipped"; the checker now refuses it (`recipe_check.py:406` ST01, `:428` ST02, `:451` ST06). The names `join`, `mutate`, `cast`, `sort` do not exist in the registry (verified by listing `AVAILABLE_WRANGLING_ACTIONS`: 68 names).

## 8. Section 7, canonical example (lines 56-72) (FACT)

Today (lines 58-72): the block with `action: cast`, `action: mutate` (with `column:` and `expression:`), `action: join` (with `'on': sample_id`), `action: sort` (with `columns:`).

Proposed (replaces the block; taken from the shipped `2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml`):
```yaml
tier1:
  - action: polars_with_columns
    named_exprs:
      predicted_phenotype_clean: pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowercase()
  - action: polars_join
    right_ingredient: metadata_schema
    'on': [sample_id]
    how: inner
    maintain_order: left_right
  - action: polars_cast
    columns: [Year]
    dtype: Int64
  - action: polars_cast
    columns: [Year]
    dtype: String
  - action: polars_sort
    by: [Year, Source, Country]
    maintain_order: true
  - action: polars_select
    exprs: ["Year", "Source", "Country", "sample_id", "predicted_phenotype_clean"]
```
Why: old names and parameter names are refused. Shipped example verified by reading the file (the example above shortens it).

## 9. Section 7, forbidden shorthand block (lines 74-85) (FACT)

Today (lines 76-85): the `# ALL OF THESE ARE FORBIDDEN` block with `- mutate:`, `- join:` (`dataset_id: foo`, `on: sample_id`), `- sort:`; headline "(silently broken)".

Proposed: change the headline to `### Forbidden shorthand (refused by the checker, ST01)` and replace the comment `# WRONG - engine never sees 'action' key` by `# WRONG - refused: a step is a mapping with an action (ST01)`; keep the three examples.

## 10. Section 7, key table (lines 89-94) (FACT)

Today (lines 91-94): the four rows (`right_ingredient`/`dataset_id`; `'on'`; Mutate `column`+`expression`; Cast `action: cast`).

Proposed table:
```
| Step list concept | Canonical form | FORBIDDEN alias |
|---|---|---|
| Join right-side table | `right_ingredient: <ingredient id>` (the id is listed in the join's `ingredients:` as `- dataset_id: <schema id>`) | `dataset_id` as a step key |
| Join columns (same name both sides) | `'on': [col, ...]` (quoted, a list) | `on` unquoted (YAML boolean `True`; refused, check T07) |
| Join columns (different names) | `left_on: [...]` with `right_on: [...]`, same length (check J11) | `on` together with `left_on` |
| Add or change one column | `polars_with_columns` with `named_exprs: {name: expression}` | the old `mutate` with `column` and `expression` |
| Cast a column | `polars_cast` with `columns` and `dtype` | `action: cast`; a cast written inside an expression to hide a type change |
```
Why: `recipe_check.py` J04 (ingredient is `{dataset_id: ...}`), J05 (`on` or `left_on` with `right_on`), J11; shipped steps as in change 8. NOTE: `dataset_id` stays the key of an ingredient entry; only its use as a join-step key is wrong.

## 11. Section 7, YAML Boolean Trap (lines 96-115) (CHANGES A RULE)

Today (lines 100-115): "Engine resilience (defensive fallback ...)": the assembler recovers from an unquoted `on:`; `ConfigManager` has no resolver; `parse_join_step` guard; "The fallback is a safety net, not the intended path."

Proposed (replaces lines 100-115):
```
**An unquoted `on` is refused.** The loader reads the YAML key `on` as the boolean `True`; the checker reports it (check T07: "an unquoted on became the key true") and the recipe does not pass the gate. Always write `'on':`.
The code still holds the old repair as a safety net (`data_assembler.py:205`, `config_loader.py:31` prints a warning, `join_designer.py:176`). It is not a licence: a recipe that needs it fails the checker. Removing the repair is not decided here (see ADR-100 point 3, PARTLY BUILT).
When a tool writes a join step back to YAML it must write the key as the string `"on"` (`build_join_step` does).
```
CHANGES A RULE (from "the engine recovers" to "the checker refuses").
Why: ADR-100 "Supersedes: ... the last point of ADR-042 (an unquoted `on` is refused, DEC02 and check T07)"; `recipe_check.py:521`, `recipe_loader.py:40-43` (T07 from the loader); `data_assembler.py:205` still has `step.get(True)`.

## 12. Section 8, line 142 (FACT)

Today (line 142): `- The included plot file must contain a single \`spec:\` root key. \`ConfigManager\` auto-unnests it.`

Proposed: `- The included plot file holds the content of \`spec:\` (it starts with \`target_dataset:\`), not a \`spec:\` key. A wrapper is refused (check F01).`
Why: same as change 4.

## 13. Section 8, plot spec block (lines 176-198) (FACT)

Today: `theme: theme_light # Optional`; `facet_by` inside `mapping`; "(ADR-083)".

Proposed: add one line under the code block: `Allowed keys of a plot spec: target_dataset, mapping, layers (required); title, theme, facet_by, palette, labels, guides, filters (optional). Any other key is refused; a layer component is checked against the registry (ADR-106).` Keep the example.
Why: `recipe_spec.yaml` `elements.spec`. See "Not settled" 2 (where `facet_by` lives).

## 14. Section 9 (lines 202-214), types (CHANGES A RULE)

Today (lines 202, 204-207, 214): heading "`input_fields` / `output_fields`"; table of `categorical` and `utf8`; "`sample_id` MUST be `type: categorical`".

Proposed (replaces section 9 except the REMOVED banner, which is rewritten):
```
## 9. Field types of `input_fields`

A field is `{type: <Polars dtype name>, ...}`; `type` is required and has no default (ADR-100 point 4, DEC27, check FD02). The names are Polars names: `String`, `Int64`, `Float64`, `Boolean`, `Date`, `Datetime`, `Categorical`, `Enum` (needs `categories`), and the other integer, float and decimal types that a text file can hold. `null_values` and `strip` are stated on every schema, no default (DEC28).

> **REMOVED (ADR-100, DEC27, 2026-11-14):** the old type names `categorical`, `utf8`, `string`, `character`, `numeric`, `float`, `integer`, `int`, `date`, `bool` are refused; the message names the Polars name to write (`recipe_spec.yaml` `renamed_types`).
> Replacement: `String` for text and identifiers; `Float64`, `Int64`, `Date`, `Boolean` for the others.
> **Tombstone expires:** two phases after the phase that records this edit (add the task entry).

**Key rule (ADR-102):** the columns of one join key must have the same declared type on both sides; differing types fail (check J09). Declare a join key as a text type (for example `String`) in `input_fields` of both tables. Nothing is cast to String for you.
```
CHANGES A RULE ("`sample_id` MUST be `categorical`" becomes "same declared type on both sides, a text type").
Why: ADR-100 points 4 (DEC27); ADR-102 points 1 and 2; shipped `2_test_data_ST22_dummy/input_fields/amr_data.yaml` uses `type: String` for `sample_id` and `type: Categorical` for `gene`. The old PK sentence is false under ADR-102.
Open point: `Categorical` is accepted by the code and used by 75 shipped fields, but DEC27 says refuse it (ADR-100 OPEN, "`categorical`"). The proposed text lists `Categorical` as accepted because the checker accepts it; Eve decides, see "Not settled" 3.

## 15. Section 10a, "Unknown key warning" (line 243) (CHANGES A RULE)

Today (line 243): `**Unknown key warning:** keys not in the list above emit \`PipelineError(severity: warning, ...)\`. Non-fatal — experimental keys are allowed ...`

Proposed:
```
**Unknown keys fail.** A key of `plot_defaults` that is not in the list above is refused by the checker with the nearest valid name (DEC02, ADR-100 point 2). There are no experimental keys.
```
And add `layers` to the allowed-key list (line 225 block): `  layers: [...]   # default layers for every plot`.
CHANGES A RULE.
Why: ADR-100 "Amends ... ADR-099 point 16(g) (unknown keys fail, DEC02)"; `recipe_spec.yaml` `plot_defaults.optional` = `palette, theme, default_font_family, facet_panel_spacing, legend_position, optimisation, layers`; `plot_defaults.height` and `show_legend` are listed as "removed". Enforced: `recipe_check.py:798` (check PD01).

## 16. Section 11 (lines 267-340), load errors (FACT)

16a. Today (line 269-275, the "Implementation status" banner): states that `ConfigManager` "still calls `exit_if_errors` (`sys.exit`)" and HOME checks with `validate_data_analysis_recipe()`.
Proposed: append one sentence at the end of the banner: `Since ADR-100 (2026-11-14) both checks are the one function check_recipe (libs/utils/src/utils/recipe_check.py, profiles run, build, gallery, audit); validate_data_analysis_recipe() in the app layer builds the catalogs and calls it.`
Why: ADR-100 point 3; `app/modules/data_analysis_recipe_validator.py:247-275` (`checker_problems`, `checker_advices`).

16b. Today (lines 332-335): `... reports a dataset that cannot be loaded and an \`output_fields\` entry that matches no column after tier-1 wrangling ... The engine does not apply \`output_fields\` of a data schema, so a wrong name there is otherwise silent.`
Proposed: `... reports a dataset that cannot be loaded. (output_fields no longer exist: ADR-100 point 5; a name that matches no column is now a plain error of the step that uses it.)`
Why: `output_fields` is refused (`recipe_spec.yaml`). Verify that `validate_data_analysis_recipe_data` no longer checks `output_fields` (its helper `_declared_columns`, line 340, still mentions the word in the docstring): see "Not settled" 5.

16c. Add a bullet at the end of 11a: `Advices (severity A, for example J12 a self-join on the same key, J13 a float join key) are shown to the recipe maker in HOME's recipe choice and in Blueprint's Validate; they never block (ADR-102).`
Why: ADR-102 status line; `recipe_check.py:558, 572`.

## 17. Line numbers 100-115, `data_assembler.py:182-185` (FACT)

The citation `data_assembler.py:182-185` is now `data_assembler.py:205`. Covered by change 11; listed so nobody keeps the old number elsewhere.

---

## Not settled (cannot be decided from the code or the records)

1. DEC49 (change 6): the exact failure condition of a float-to-integer cast is in ADR-100 point 4 ("a float-to-integer cast that would drop decimals fails"); the code path was not read. A reviewer should read it before the sentence is pasted.
2. Where `facet_by` lives: `recipe_spec.yaml` lists it as a key of `spec`; every shipped plot file (for example `2_test_data_ST22_dummy/plots/multi_resistance_by_country.yaml`) writes it under `mapping`. The checker has no hit for `facet_by`. Not decided; the rule text keeps both as they are.
3. `Categorical` (change 14): ADR-100 OPEN list, Record 1 (DEC27 refuses it) against Record 2 (migration writes it; 75 shipped fields).
4. SETTLED: `check_recipe` enforces the `plot_defaults` keys (`recipe_check.py:798`, `unknown_keys("plot_defaults", ..., "PD01")`).
5. SETTLED in part: `validate_data_analysis_recipe_data` (`data_analysis_recipe_validator.py:345-395`) compares declared `input_fields` with the real columns; only its helper docstring (line 341) still names `output_fields`. Change 16b is right; also change that docstring when the file is next edited (code, not a rule file).
