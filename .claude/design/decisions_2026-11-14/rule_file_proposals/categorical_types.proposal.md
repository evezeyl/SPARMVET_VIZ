# Proposal: the type table of section 9 of `rules_data_analysis_recipe_structure.md` (CATEGORICAL-MIGRATION-1)

Status: PROPOSAL for Eve's double confirmation. No rule file was edited.
Source: Eve, 2026-11-15, agent channel block M119 ("shipped fields declared Categorical become String when nominal; Enum with the order written when the order has a meaning; one Categorical stays as the documented example"). The code already does this: the shipped recipes declare `String`, `Enum` or one `Categorical`; the lower-case words `categorical` and `utf8` are refused by the checker (verified in `docs/foundations/data_contracts_adr.qmd`, "Step 3").

All three rows are in `RULE_FILE_CHANGES.md` (R129 to R131). File: `.claude/rules/rules_data_analysis_recipe_structure.md`.

## 1. Line 206, the `categorical` row of the type table

Old line:
`| `categorical` | `pl.String` (internal) | `pl.Categorical` | **Default** for identifiers and repeating values (`sample_id`, `taxon`, `country`, `gene`). Ensures discrete-scale correctness in Plotnine. |`

New line:
`| `String` | `pl.String` | `pl.String` | Identifiers and nominal fields (`sample_id`, `taxon`, `country`, `gene`) and free text. A plot draws it as a discrete scale in alphabetical (byte) order. |`
plus two rows: `Enum` (the levels and their order written in `categories`; a value outside the list stops the load; the order is the plot order) and `Categorical` (valid; kept in one shipped field as the documented example).

## 2. Line 207, the `utf8` row

Old: `| `utf8` | `pl.String` | `pl.String` | High-cardinality text, ... |`
New: remove the row. `utf8` is a refused old word; `String` (row above) replaces it.

## 3. Line 214, the primary key rule

Old line: `**Primary key rule:** `sample_id` MUST be `type: categorical`. Using `numeric` for join keys causes type-parity mismatches in `action: join` steps.`
New line: `**Join key rule:** a join key (`sample_id`) is declared `String` on both sides of a join. The engine never changes the type of a key; a mismatch stops the build.`

(Lines 209-212, the tombstone block, say `type: string` should become `categorical` or `utf8`: the migration target is now `String`. Same proposal: replace the two words by `String`.)
