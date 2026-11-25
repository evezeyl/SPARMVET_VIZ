# Where is tier 3 defined? (panel round 5, 2026-11-22)

Your order (channel block M553). Three viewpoints, as you asked: data science (the scientist), software architecture, and the recipe maker who reads the file. No developer viewpoint. **The cost of the change was not allowed as an argument**: it is in its own row, as information. "Reopens" is in its own row too. Their answers as given: `VIEWPOINTS_5.md`.

## 1. Flags first
1. **All three found the same thing: two different things carry the name "tier 3".**
   - (a) A table that several results read, or that someone wants to see: for example a summary shown as a bar plot AND as its table. That is data, with one definition and several readers.
   - (b) The last steps of ONE result only: a filter, an order, a rename for one figure. Nothing else reads them.
2. **For (a), all three agree with you:** it belongs in the data part, with a name, before the results. And all three say it is then simply a TABLE (a "derived table"), not a third tier: under your reading 2 the word "tier 3" in the data part confuses, because nothing distinguishes it from another table.
3. **They disagree on (b):** may a result keep a few steps of its own? The architect says no (one way to do one thing). The scientist and the recipe maker say yes, because of the audit ("this result only").
4. **Silent change, under each form:**
   - Steps kept inside each result (reading 1): when two results need the same last steps, the steps are written twice, and the two copies can drift apart with no message. A plot and its table would then show different numbers.
   - A shared stage (reading 2): an audit step written there changes EVERY result that reads it. Right when the user means that; wrong when she means "this result only". The dialog must list the readers before she confirms.
5. **A fact:** no plot of the demo recipe has tier 3 steps today, and only one template uses them. So no shipped result depends on the present form.
6. **A rule of order alone would be cosmetic** (writing `tier3` earlier in the same entry): the app reads the file into a structure where the order of keys carries no meaning (architect).

## 2. The forms, written out on the demo recipe
The example: the join `FastP_with_metadata`, a bar plot of it, and a summary shown as a table.

**Form 1 = your reading 1: the result owns its last steps.**
```yaml
joins:
  FastP_with_metadata: {ingredients: [FastP, metadata_schema], tier1: {...}, tier2: {...}}   # definition
analysis_groups:
  quality:
    results:
      reads_barplot:                     # use
        target_dataset: FastP_with_metadata
        tier3: {steps: [...]}            # this result's own steps
        result: plot
        mapping: {...}
        layers: [...]
      reads_summary:                     # use
        target_dataset: FastP_with_metadata
        tier3: {steps: [group_by, mean]} # the summary is computed HERE, inside the result
        result: table
```
**Form 2 = your reading 2 as written: a block `tier3` in the data part, named stages.**
```yaml
joins:
  FastP_with_metadata: {...}
tier3:
  reads_summary_table: {from: FastP_with_metadata, steps: [group_by, mean]}   # definition
analysis_groups:
  quality:
    results:
      reads_barplot: {table: FastP_with_metadata, result: plot, mapping: {...}, layers: [...]}
      reads_summary: {table: reads_summary_table, result: table}
```
**Form 3 = derived tables only (the architect's): the data part defines tables; a result reads exactly one table and has NO steps of its own.**
```yaml
joins:
  FastP_with_metadata: {ingredients: [FastP, metadata_schema], tier1: {...}, tier2: {...}}   # definition
  FastP_reads_summary: {from: FastP_with_metadata, tier1: {steps: [group_by, mean]}}          # definition (derived)
analysis_groups:
  quality:
    results:
      reads_barplot: {table: FastP_with_metadata, result: plot, mapping: {...}, layers: [...]}   # use
      reads_summary: {table: FastP_reads_summary, result: table}                                  # use
```
**Form 4 = derived tables, AND a result may keep private last steps (the scientist's and the recipe maker's).** Form 3, plus the optional `tier3` of form 1 on a result, for steps that only this result needs.

## 3. The arguments (cost and "reopens" are information only)
| | Form 1: the result owns it | Form 2: a `tier3` block in the data part | Form 3: derived tables only | Form 4: derived tables + private steps |
|---|---|---|---|---|
| **Data science: what is a result, what is a stage** | a result carries its steps, so its provenance is in one place; but a reusable table (a summary) is hidden inside a result | sharing and "definition before use"; but a stage that any result may read is not different from a table | one table, one definition; a plot and its table are the same table by construction | the same, and a result's truly private steps stay with it: "T1 feeds T2 feeds T3 feeds the result" keeps its meaning |
| **Same numbers for a plot and its table** | not guaranteed: two copies of the steps can drift | guaranteed when both name the stage | guaranteed | guaranteed, unless an author adds a private step to one of them (the screen must say "this result adds N steps of its own") |
| **Audit: "this result only" and "all results that read this"** | "this result only" is natural; "all" needs a place higher up | "all" is natural; "this result only" is lost when a stage is shared | "this result only" exists only where the table has ONE reader; the dialog computes the readers (the code can already list them) | both exist: a step at the shared table for all its readers, a step at the result for this one |
| **Architecture: one definition of "the table a result shows"** | one (the entry's last stage) | two: the named stage, and the result that points to it; a third family of names beside tables and joins | one (`table:`); the data and the results stay two independent things | one table plus an optional private list: a second way to add last steps, which needs a rule to tell them apart |
| **Definition before use** | no: the steps sit in the result | yes | yes | yes for everything shared; a private step sits with its result |
| **Described like tier 1 and tier 2** | no | in name only: tier 1 and 2 belong to a table, this block to nothing | yes: a derived table HAS a tier 1 and a tier 2 | yes for the shared part |
| **The recipe maker: "if I change this step, which results change?"** | open every result's file | search for one name | search for one name | search for one name; plus the results that add their own steps |
| **A third kind of result later (a text, a map)** | one more value of the key | one more value | one more value | one more value |
| **The words "tier 3" and "T3" on screen** | keep their meaning | confusing for an author (it is a table) | disappear from the recipe; "Table to view" then shows the stages of the table the result reads | keep the meaning "this result's own steps"; "T3 = T2" when there are none, as today |
| **Strongest argument against (their own)** | drift; fails your two wishes | no "this result only"; needs a new kind of table anyway | one more named table for each result that needs private steps; it gives up "data specific to one plot" | two places for last steps: an author may not know which to use |
| **Who chose it** | nobody | nobody as written | the architect | the scientist and the recipe maker |
| **Reopens (information)** | nothing | D-0237, D-0250, D-0343, D-0063 | D-0063, D-0306, D-0250, D-0343, D-0485 ("the result is the last stage of the entry"), the lineage level `T3:<entry>` | D-0109 only as already modified; adds a kind of table "made from another table" |
| **Cost (information only, not in any verdict)** | none | large | large: the place `T3:<entry>`, the audit copy, the keys of stored tables, the lineage levels, the check | medium: a new kind of table; everything about tier 3 stays |

One open technical point for forms 3 and 4 (architect): a derived table must read the table it is made from AFTER that table's tier 2. Today a join reads the tier 1 of its ingredients. So "made from" (`from:`) is a new key with its own meaning; it is not a join with one ingredient.

## 4. My recommendation (the coordinator's; yours to accept, change or refuse)
**Form 4, with the rule the recipe maker gave:** "A table is defined once in the data part, and every result reads a table by name. A result may add private last steps for its own figure only if no other result needs them."
- It gives you what you asked for wherever it matters: a table that is shared, or worth seeing, is data, defined in the data part, before the results, with its own tier 1 and tier 2.
- It keeps what your earlier decisions rest on: the result's own last stage (T3), the fall back T3 = T2 = T1, and the lowest audit place "this result only".
- The architect's objection is real: two places for last steps. Three things would hold it in check: the recipe check ADVISES when two results carry the same private steps ("make it a table"); the screen says "this result adds N steps of its own"; the documentation gives the one rule above.
If you prefer one way only, form 3 is the clean one, and then "this result only" in the audit means: the audit recipe adds a small table of its own for that result [my idea, not a viewpoint's: not examined by the panel].

## 5. For you to decide (nothing chosen)
1. The form: 1, 2, 3 or 4.
2. If 3 or 4: the word for a table made from another table (the recipe maker suggests "derived tables" and `from:`), and whether it lives among the joins or in a block of its own.
3. If 4: the name of the result's private steps: still `tier3`, or another word, since the shared case moved away.
4. If 3: what "this result only" means in the audit when a table has several readers.
5. Under 3 and 4, a plot and its table can read the same table: this also answers part of your earlier question on a table as a result (the summary is a table of the data part; the result of kind "table" simply shows it).

## 6. Not verified
No form was built or run. Whether ids of results are checked as unique inside one recipe today was not confirmed (the architect found only the check across recipes). The effect of each form on HOME's "Table to view" was reasoned, not tried.
