# Panel round 5: where is tier 3 defined? (2026-11-22)

PRIORITY: the owner waits for this to answer a question that blocks a build. One round. You only recommend; she decides. Never read `tmp.md`.

## Her rules for THIS panel (strict)
- **The cost of the change is NOT an argument.** Her words: "I need arguments for good practice and good data science (not economical in term of changes to do - because economy now might need problems later)". Say what an option costs only in a separate line "Cost (information only):". It must not enter your verdict.
- Judge ON MERIT. "Reopens D-xxxx" is information: a separate line "Reopens:", never an argument.
- Verify at file:line what you rely on.

## Her words
"I think the tier 3 should be described the same way wether its a table or the plot ... should not the tier3 defined as its done for the plot ? where is the T3 for the plot ?"
"but Id like the tier 3 to be defined in the same way tier 1 and 2 are defined - it does not makes sence in your example because tier 3 is dedined after the definition or results - it should occur before"
"I mean I want to see your hierarchy how to define T1, T2, T3, results {table , plots), plot recipe"
Earlier the same day (ledger D-0485): tier 3 is data like tiers 1 and 2; that it is "the last stage before a plot" is our choice, not a limit of the data; a result entry of a group is a plot or a table; the result is the last stage of the entry, with the fall back T3 = T2 = T1 when a tier has no steps; all tiers work as written.

## Today (read it in the code and in the demo recipe before you answer)
- The demo recipe: `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` and its folder `1_test_data_ST22_dummy/` (`wrangling/`, `join/`, `plots/`). Top-level keys: `data_schemas` (tables read from files; each has `tier1`, optionally `tier2`), `joins` (each has `tier1`, optionally `tier2`), `analysis_groups` (groups; each holds `plots`; a plot entry has `ui_label`, `target_dataset`, `mapping`, `layers`, optionally `tier3`).
- Tier 1 and tier 2 belong to a TABLE (a table or a join). Tier 2 of a table is ONE list, shared by every plot that reads that table. Tier 3 belongs to a PLOT ENTRY: it is that entry's own last steps after the tier 2 of its `target_dataset` (`libs/utils/src/utils/recipe_spec.yaml:34-57, 72-75`; `libs/utils/src/utils/recipe_tiers.py:131-179`; `app/modules/orchestrator.py:690-750`).
- The stored table of a tier 3 is keyed and named by the entry (`app/modules/cache_keys.py:452-469`; `<target>__T3_<entry id>.parquet`). The lineage place is `T3:<entry id>`. Audit steps are kept per entry. In an audit recipe each tier has the author's `steps` and a second list `audit_steps` (ledger D-0329; decided, partly built).
- Which entries of the demo have a `tier3` today: grep the `plots/` folder and say.

## The question: where is tier 3 defined?
**Reading 1 (the entry owns it):** `tier3` stays a key of the result entry, written BEFORE the result kind and the drawing parts:
```yaml
analysis_groups:
  quality:
    ui_label: "Quality control"
    results:
      reads_summary:
        ui_label: "Reads summary"
        target_dataset: FastP_with_metadata     # the table it reads (its tier 2, or tier 1)
        tier3: {steps: [...]}                   # this entry's own last steps
        result: table
      reads_barplot:
        ui_label: "Reads"
        target_dataset: FastP_with_metadata
        tier3: {steps: [...]}
        result: plot
        mapping: {...}
        layers: [...]
```
**Reading 2 (the data part owns it):** tier 3 is defined in the data part, with tiers 1 and 2, BEFORE the results, as a named stage; a result entry only points to the table it reads:
```yaml
data_schemas: {...}            # tier1, tier2 per table
joins: {...}                   # tier1, tier2 per join
tier3:                         # (the name and the place of this block are open)
  reads_summary_table:
    from: FastP_with_metadata
    steps: [...]
analysis_groups:
  quality:
    results:
      reads_summary:
        ui_label: "Reads summary"
        table: reads_summary_table
        result: table
      reads_barplot:
        ui_label: "Reads"
        table: FastP_with_metadata
        result: plot
        mapping: {...}
        layers: [...]
```
Her stated reasons for reading 2: T3 is DATA like T1 and T2; a definition should come before its use; tier 3 described the same way whether the result is a table or a plot.
**Option 3:** if you find a better form, name it and show it. Examples to judge, not to adopt blindly: (3a) reading 1's ownership, but the entry's `tier3` is written in the data part of the FILE order only (a rule of order, not of structure); (3b) a `tier3` block under each table or join, holding NAMED step lists, read only by the entries that name one; (3c) no "tier 3" at all in the data part: a stage that two results share is simply a new derived table (a join with one ingredient, or a new kind of table "derived from"), with its own tier 1 and tier 2, and a result entry reads exactly one table and has no steps of its own.

## Questions every viewpoint must answer for each reading
1. **Shared or owned.** Under reading 2 a named tier 3 stage can be read by TWO results. Is that a feature (one definition, two views of the same table: a plot and its table) or a risk (an audit step written at that stage changes both; a change by the author for one result silently changes the other)? Under reading 1 two results that need the same last steps repeat them (or `!include` the same file): can they then silently drift apart? What does "T1 feeds T2 feeds T3 feeds the result" mean under each?
2. **What tier 3 IS.** If a tier 3 stage is a named table in the data part that any result can read, how does it differ from a tier 2, or from another table? Is "tier 3" then still a tier, or just "one more derived table"? Does the distinction "tier 2 = shared by a group of plots, tier 3 = specific to one result" (ledger D-0063, D-0306: "T3 : data plot specific") survive reading 2, and should it?
3. **The fall back** (D-0343): T3 = T2 when the entry has no steps of its own. Under reading 2 an entry with no tier 3 points straight at a table: is the fall back then simpler (there is nothing to fall back from) or lost (the data view "T3" of HOME has no meaning for that entry)?
4. **The audit and the lineage.** The audit dialog offers places where a step can be written; the lowest is the entry's own table (`T3:<entry>`): "this plot only". Under reading 2, is "this result only" still expressible when two results share a tier 3 stage? Where do `audit_steps` go (D-0329: per tier)? What happens to the stored table's key and name (D-0025: keyed by its definition and what it reads)?
5. **Reading the file.** A recipe maker reads top to bottom. Which reading lets her answer fastest: "which data does this result show, after which steps?" and "if I change this step, which results change?" Count the places she must look at for one result under each reading, on the demo recipe (the entries are in `!include` files today: say how each reading uses files).
6. **A third result kind later** (a text, a map): what does each reading need?

## Your answer: AT MOST 350 words
Your verdict (reading 1, reading 2, or an option 3 you show) with the reasons of YOUR viewpoint only; the strongest argument AGAINST your own choice; one line on each other reading; "Cost (information only):"; "Reopens:"; "Flags:" anything that would change a result silently or hide a step from the user under each reading. Evidence as file:line or the recipe's lines. No preamble.
