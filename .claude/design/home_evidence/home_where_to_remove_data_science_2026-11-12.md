# Where in the data processing must a removal happen? How a data scientist answers (P5 investigation)

**Written for:** Eve, to discuss P5 (stage and reach). **Written:** 2026-11-12, after your correction: the user does not remove from a plot, the user removes **from the data**, and we must understand what the recipe does to the data (wrangling, tidy, joins, filters, aggregations) to know where a removal can go and what it affects.
**Status:** investigation and proposal. Nothing is decided. **Evidence:** verified = run on the shipped recipes and test data (scripts in `tmpAI/architect/lineage_scan.py`, not committed); reasoned = standard data-science and database theory, said so.

## 1. The question, in the data scientist's words

A removal is an operation on **entities** (here samples, identified by a key such as `sample_id`) somewhere in a **dataflow**: sources -> per-dataset steps -> joins -> per-table steps -> plot. Three things decide where it must go:
1. **The intent.** *Exclusion*: "as if this sample had never been in the experiment" (a really bad sequencing run; the default meaning of a quality removal). *Hiding*: "do not show it in this figure, but leave it in every computation" (rare, and easy to misuse).
2. **The dataflow.** Which datasets have the key, how they branch and join, which steps follow.
3. **What each step does when an entity is missing** (section 3). This is what makes the answer "it depends".

The usual rule is **remove as early as possible** (once, and nothing downstream can still be influenced by the entity), **but the science must stay correct**: a branch that must keep the entity, such as the QC plot that justifies the removal, must not lose it.

## 2. How a data scientist thinks about it (seven principles)

1. **Draw the dataflow first** (the lineage). Mark, at every node, whether the key is still there.
2. **Classify each step by its reaction to a missing entity** (section 3): does the result for every other row stay the same?
3. **Exclusion goes to the datasets, at every input that carries the key.** Removing a sample from only one input of a join leaves it in the others and can turn "removed" into "zero" (section 5, demo 3).
4. **Place it as early as the lineage allows, per branch.** One removal at the earliest node serves every branch that reads that node; removing late means repeating it in every branch.
5. **Branches that document the decision stay original.** The standard pattern is a flow: QC (decision) -> exclusion -> analysis (as in CONSORT flow diagrams and ARRIVE exclusion reporting). The QC branch is upstream of the exclusion, so it must read the original data. This is your use case.
6. **Two versions of the data, not edits.** Keep the original data and build an audited version next to it. Each result reads one of them. Then a QC plot and an analysis plot can read "the same table" in its two versions with no conflict.
7. **Say what was done and what it changed.** Rows and samples before and after, which datasets, which branches, the reason. (This is the attrition table and coverage check already in the design.)

Standard theory behind principle 3 and 4 (reasoned, not run here): in query optimisation this is **predicate pushdown**. A condition on a key can be pushed through projections, row filters and joins on that key, and through a group-by when the key is a grouping column; it **cannot** be pushed through an aggregate over other columns, a window over a partition that mixes entities, a ranking, a top-N, a sample or a pivot. Pushing a condition into the *right-hand* side of a **left join** changes the result (rows survive with empty values). The database literature calls the general problem of deleting from sources what must disappear from a result the "view deletion problem"; the easy case is when the key is preserved, which is exactly our case (the design cites Buneman, Khanna, Tan 2002).

## 3. How the 67 registered operations react to a missing sample

By name (from the registry): about **45 are row-local** (cast, rename, regex, fill, null_if, row filters `filter_*`, `is_in`, `not_in`, keep/drop columns, split, explode, unpivot, `label_if`, `divide_columns`, date parts, row-wise `horizontal_stats`, `sort`, and so on): the result for the other rows does not change if a sample is removed. **2 are joins** (`join`, `join_filter`) where the join type decides what a removal does. **2 are engine-internal** (save and load). **18 can depend on which other samples are present**: `z_score`, `percentile`, `window_agg`, `count_by_group`, `summarize`, `cum_sum`, `cum_count`, `shift`, `fill_nulls_direction`, `interpolate`, `top_n_other`, `value_counts`, `describe_stats`, `sample`, `drop_duplicates`, `unique`, `unique_rows`, `pivot`. A `mutate` expression can be either (it is arbitrary code).

**The name is not enough, the parameters decide.** `summarize` or `count_by_group` grouped **by the key** keeps each sample separate (entity-local); grouped by country they mix samples. `unique_rows` removes only whole-row copies, which belong to one sample when the key is in the row. `mutate` with `.over('sample_id')` is per sample, `.mean()` without it is not. So the software must read each step **relative to the key**, not only the action name.

## 4. What your recipes actually contain (verified)

Scan of all 7 shipped recipes, every lineage of every plotted table (13 tables):

| | |
|---|---|
| steps in these lineages | 91: **63 row-local, 20 joins, 8 flagged as possibly population-dependent** |
| the 8 flagged steps, read with their parameters | **all 8 are per-sample**: `count_by_group` and `summarize` grouped by `sample_id`, `unique_rows` and `drop_duplicates` including the key, `mutate` with `.over('sample_id')`. **None mixes samples.** |
| `summarize` steps that drop the key | 0 |
| tables with no flagged step | 8 of 13 |
| joins | 18 `join` and 2 `join_filter` |

So **in all shipped recipes a removal of a whole sample commutes with every step**: removing it at the sources or on the plot's table gives the same numbers, **where the key is still in the table**. Population-dependent steps (statistics across samples) are allowed by the engine (18 operations) but not used by any shipped recipe, so the "removal before the statistic" rule matters for recipes people will write, not for these.

Branching in `1_test_data_ST22_dummy` (verified): `metadata_schema` feeds 4 tables, `FastP`, `Quast`, `ResFinder` and `MLST` feed 2 tables each. Each table builds its own copy of its inputs (the engine prepares ingredients per table), so a removal inside one table does not touch the others. The QC plots read `QC_Reads_Anchor` and `Quast_with_metadata`; `Quast_with_metadata` is **also** read by `miaou`, a non-QC plot.

## 5. What goes wrong at the wrong place (measured on the shipped test data)

The worst sample by N50 in the Quast data: `66678807` (N50 131,595; median 324,189).

| Demo | What was done | Result |
|---|---|---|
| 1. A statistic over all samples (z-score of N50; allowed by the engine, not in the recipes) | remove the sample **before** the z-score, against hiding it **after** | the 41 other samples differ by up to **0.064** z-units (mean 0.037); no sample crossed |z| = 2. Small here with 42 samples and a moderate outlier; it grows with a more extreme outlier or fewer samples |
| 2. Counts per country and year (the `QA_aggregated_no_key` canary) | the sample is in Norway 2024 | removed **before** counting: 19 -> 18. In the counts table there is **no sample key**, so it cannot be removed there by its ID |
| 3. Left join of metadata with ResFinder | remove the sample from **only** ResFinder | it still appears, now with **0 genes**, which reads as "no resistance"; the result has 42 samples (should be 41) and the samples with 0 genes go from 4 to 5. A silent wrong claim |

## 6. What this means for the design (proposal, MINE; nothing decided)

1. **The user-facing model is data, not plots:** *datasets -> audited datasets*. A removal by ID is "remove sample X from the datasets" (every dataset that has the key, as decided; the coverage check lists the ones that do not). The lineage map shows datasets, tables and plots; the dialog says which datasets and tables change.
2. **Two versions of the data (principle 6) solve your use case:** every table exists as original and audited. **Each plot reads one version.** By default plots read the audited version; the plots that justify the exclusion (the QC plots) are **pinned to the original**. Then `Quast_with_metadata` can feed the QC dot plot (original) and `miaou` (audited) at the same time, and the earlier "shared table" conflict disappears. The original is never changed anyway (decided, S1).
3. **The scope of a removal is "the whole project, except the pinned plots"** (default: nothing pinned). A narrower scope (only this plot, for example a category with too few observations for one figure) is a plot-level step, late by nature, and says so.
4. **The software computes the earliest correct node per branch** from the lineage: the key must be present, every join input with the key is cut, and the removal comes before any step that depends on the sample set. It shows what it chose and what it affects. This is the "as early as possible, but modulated" rule.
5. **Value filters follow the same lineage logic** (an audit step and a recipe change are the same kind of step): the user filters on the table they look at; the earliest node is where the column exists; the dialog shows the downstream tables and plots. A filter before an aggregation is then legitimate, and the check "a step that depends on the population lies downstream" warns.
6. **What the system must compute from the recipe** (the checklist of "what is important for results to be correct"): where the key exists and where it is lost (aggregations without the key); the reaction of each step relative to the key (section 3); the join type and which inputs carry the key; where population-dependent steps are; which tables are shared between pinned and audited plots; many-to-many joins (rows are not samples; issue #68).

## 7. The refined questions (one at a time; this is what we discuss)

- **Q5.1 The model.** Do we describe a removal as **an operation on the datasets, with two versions of the data and plots pinned to the original** (section 6, points 1-3), instead of choosing among plots?
- **Q5.2 The default scope.** For "remove samples by ID": the whole project (every dataset that has the key), except the plots the user pins to the original?
- **Q5.3 The rule for the insertion point.** "The earliest correct node per branch, every join input with the key cut, before any population-dependent step" (section 6, point 4): is that the rule, with the software showing its choice?
- **Q5.4 Exclusion or hiding.** Is the only audit removal an **exclusion** (as if the sample never existed), with plot-level steps (late) offered only for "not meaningful in this plot", with the warning that upstream statistics still include the entities?
- **Q5.5 Value filters.** Same lineage logic on the table the user looks at, including before an aggregation?
- **Q5.6 (optional) Evidence link.** Should a step name its evidence plots (the QC plot) so the export shows them next to the reason?

## 8. Refined after the discussion with Eve (2026-11-12)

**Agreed in the discussion (to be recorded as decided once the questions below are answered):** a removal is an **operation on the data**, not on a plot (Q5.1); it must be possible to remove a key such as `sample_id` from **all datasets at once** (speed; a poor sample that must be re-run); **there is no "hiding" in audit mode**: every audit step really changes data and is recorded and exported.

**The contradiction you saw, and how it is resolved.** My Q5.1 said the operation is on datasets, my Q5.2 said the scope is chosen by plots. Two different things were mixed:
- the **operation** says *where in the data* it happens: a **node** of the dataflow (a dataset, a table at T1, a table at T2, or a plot's own table at T3);
- the **association view** (dataset -> table -> plot) shows what that operation reaches, and flags the plots that must stay original;
- **pinning** a plot to the original is a separate, visible setting of the plot, made in that view. It is not part of the operation.

**The stages (names to settle):** *dataset* (a source with its own first steps), *table T1* (the datasets joined, before the table's tier-2 steps), *table T2* (the table the plots read), *plot T3* (the plot's own table).

**The association, from your ST22 recipe (verified):**

| Dataset | Feeds table(s) | Plots |
|---|---|---|
| `metadata_schema` | all four tables below | |
| `FastP` | `QC_Reads_Anchor`, `ST22_Anchor` | `qc_reads_horizontal_barplot`; `virulence_bar`, `virulence_variants` |
| `Quast` | `QC_Reads_Anchor`, `Quast_with_metadata` | `qc_reads_horizontal_barplot`; `assembly_quality_dotplot` (QC), `miaou` |
| `ResFinder` | `ResFinder` (used directly), `ST22_Anchor` | `amr_heatmap`; `virulence_bar`, `virulence_variants` |
| `MLST` | `MLST_with_metadata`, `ST22_Anchor` | `mlst_bar`, `year_distribution`; the two virulence plots |

**What a value filter implies (question 5), with your data.** ResFinder has `%Identity` and a step that counts genes per sample (`total_gene_count`, `count_by_group` by `sample_id`). A filter `%Identity >= 99` placed **before** that count keeps 13 of the 70 rows, so `total_gene_count` changes for **35 of 38 samples** and **27 samples drop to 0 genes**. The same filter placed on the **plot's own table** (after the count) shows the same 13 rows in the figure, but `total_gene_count` still says the original number. Neither is "wrong": they answer different questions, and the dialog must show which one the user is doing. That is the implication: **a value filter before an aggregation changes every later number that was computed from those rows, in every table and plot that reads it.**

**What the evidence link (question 6) means.** When you remove samples because the QC plot shows they are poor, the step can store "evidence: `qc_reads_horizontal_barplot`". The export then shows that figure (the original, unfiltered one) next to the reason, so a reader sees what justified the removal. It documents the step; it does not change any data.

**The refined questions, in order**
- **R1 The model.** An audit operation is: *what* (remove entities by key | filter rows by value | drop a column), *where* (a node: dataset, table T1, table T2, plot T3) and a *reason*. The effect is everything downstream of that node. The dialog shows the association (which tables and plots) before Apply.
- **R2 Removing a key.** Offered in two ways: **all datasets that have the key, in one action** (the speed case; default), or **chosen datasets**. The dialog lists the datasets it cut and the ones without the key.
- **R3 Pinning.** Every table exists as original and audited. By default plots read the audited version; the user can **pin a plot to the original** (the QC plots) in the association view. One setting per plot.
- **R4 Plot-level steps.** A step on a plot's own table (stage T3) stays a real audit step (recorded, exported), for cases such as "a category with too few observations to be meaningful in this plot". It changes only that plot, not the tables before it.
- **R5 Value filters.** The user filters on the table they look at; the earliest node where the column exists is proposed; the dialog shows the downstream effect and warns when an aggregation lies downstream.
- **R6 Evidence link.** Optional: a step names its evidence plot(s), shown in the export next to the reason.

## 9. Eve's Polars question, and the audit as a recipe with steps inserted at different places

**Eve (2026-11-12):** could flags in Polars tell us which steps are aggregations, and would that help? And: the audit steps are basically added at different places in the (audit) recipe.

**The audit recipe.** Yes. An audit is **the original recipe plus audit steps inserted at chosen positions of its dataflow**: at the start of a dataset (before its own steps), after the joins of a table (T1), after the table's second stage (T2), or on a plot's own table (T3). This is the "forked recipe" already in the design (ADR-099 point 8; the user's own recipe files are never edited). Two consequences:
- One logical action such as "remove sample X from all datasets" **expands into several inserted steps**, one per dataset that has the key. The user sees one action; the audit recipe holds N insertions; the export lists them.
- Running the **original recipe** gives the original tables, running the **audit recipe** gives the audited tables. "Two versions of the data" is simply the result of two recipes, and a plot is set to read one of them.

**What Polars gives (verified on Polars 1.40.1):**
- **No "is an aggregation" flag on expressions** (`Expr.meta` offers nothing of the kind). A query plan can be inspected as text (`explain`) and as JSON (`serialize`; it names group-by nodes), but that format is not a stable public contract (reasoned).
- **The optimizer is a one-sided proof.** I asked it to move "sample is not d" below each step. Synthetic: 12 of 12 cases match the theory (row-local, group by the key, window over the key, joins, whole-row unique: moved; z-score, window over country, rank, running total, unique on country only, first 3 rows: not moved). On the **real ingredients of the 7 recipes**: 18 moved, 6 refused, 2 have no `sample_id`. The 6 refusals are all **entity-local steps** (`unpivot`, `split_and_explode`, `split_column_to_parts`, a numeric `filter_range`) that Polars simply cannot prove safe. So: **"moved" proves the step commutes; "refused" proves nothing**. It must not be used alone to warn.

**What would help, in two parts (MINE):**
1. **A declared property in our own action registry**: each action says whether it is row-local, depends on the other samples, or is a join, refined by its parameters relative to the key (grouped by the key = local; grouped by country = depends). This gives early warnings such as "an aggregation lies downstream of this step". The Polars optimizer can be used as a **test** of these declarations (a declared-local action that Polars refuses is checked by hand; a declared-local action that changes other rows is a bug).
2. **A data check in the dialog:** compute the audit recipe both ways on the real data (the sample removed early, against removed after the computation) and compare the other rows. If identical: "the result is the same wherever this is removed". If different: show which numbers differ. This is exact for the data at hand and needs no classification of the 67 operations; it is the trial computation of the design, used as a check.

Together they cover the problem of *detecting where a removal matters*. They do not decide the intent (exclusion or not), the scope, or which plots are evidence: those stay the user's choices, with the reason recorded (Eve: the reason at each step says "removed here but not there because...").

## 10. Settled in the discussion so far (2026-11-12, to be written into the design files when P5 closes)

- **R1 accepted, with Eve's definition:** *an audit is every change the user makes, with a recorded reason.* (Preview is not an audit: it changes nothing.)
- **R2 accepted:** remove a key from **all datasets at once**, or from chosen datasets.
- **R4 accepted:** a step on a plot's own table is a real step.
- **R5 accepted:** value filters and column drops follow the lineage logic; **all downstream effects are shown** before Apply; the **reason** records why it was done here and not there.
- **R6 dropped** (the reason text covers it, and the QC plot appears in the export anyway as a plot no step touched).
- **R3 pinning: not yet clear to Eve; to explain with an example.**

## 11. Eve's reply on the QC plots, and my view (2026-11-12; **confirmed by Eve**: the logic, the dropping of pinning, the tick boxes)

**Eve:** the original plots remain, so removing the samples from the QC plots too still leaves the proof of why they were removed. QC and analyses usually use different datasets, so one T1 can stay unchanged while others are audited. For a shared table such as Quast the removal must happen later, at the T3 concerned and not in the T1 of the lineage. The software needs the recipe's processing per dataset to decide.

**My view:**
1. **Pinning (R3) is dropped.** The immutable original Result plot is the evidence (Compare reference in audit mode; the export carries the original beside the audited plot). Keeping a QC plot unchanged is a matter of scope, not a mechanism.
2. **The scope is a set of tables** (their T1), because the engine builds a private copy of every dataset inside each table: a removal inside one table does not touch the others. In ST22 the QC and the analyses share `FastP`, `Quast` and `metadata_schema` (only `Bracken` is QC-only), so a dataset-level split is impossible and a table-level one is possible. "All at once" = every table that has the key.
3. **The Quast case (verified lineage):** `Quast` (`strip_whitespace`) -> left join with `metadata_schema` on `sample_id` -> `unpivot` (3 metrics) -> `cast`; T2 = T1 with `sample_id` present (126 rows = 42 x 3); the plots are a boxplot (QC) and a violin (`miaou`), their statistics computed after the filter. Every step is per-sample, so a removal at `miaou`'s own table equals a removal at the source.
4. **The recipe graph (D1 of the design, so far only "to confirm") is a prerequisite:** per table the datasets feeding it, the reaction of each step relative to the key, the join types, key presence, the plots that read it. It comes first in the build order.
5. **Proposed rule:** the user ticks the tables or plots that must change (default all); the software places the step at the earliest point inside each ticked table that does not reach an unticked plot; where a table is shared with an unticked plot it places the step later, at the plot's own table, and says so.

## 12. How to convey the information to a user who did not write the recipe (P5b; proposal)

**Eve:** the user will not know what `ST22_Anchor` is if they never wrote the recipe; maybe we can add pointers inside the recipe itself. She likes the tick boxes.

**What the recipes carry today (verified, 7 shipped recipes, non-QA):** group label or description 11 of 11; plot label 9 of 20, plot info 12 of 20, plot title 12 of 20; **description of a plotted table 4 of 13** (and they are generic, such as "Primary joined dataset for ST22 Dummy analysis"); dataset description 11 of 22. So a user would often see a bare name.

**Proposal: speak the user's language, from the plots down to the data, in four layers.**
1. **Results (what the user knows):** the plots, grouped by tab, with their titles. These are the tick boxes.
2. **The data behind each result, in one plain sentence:** generated from the lineage and, when the recipe has one, the table's own description. Example for `miaou`: "Quast results joined with the sample metadata and reshaped to one row per sample and metric (3 metrics). The sample key is kept. Also read by: Assembly quality (box plot)."
3. **What will happen to each plot, shown as you tick:** "changed at the source" | "changed at this plot only (the table is shared with an unticked plot)" | "unchanged".
4. **The lineage chain on request** (the lineage map of the design): datasets, steps in plain words, table, plot.

**Mock-up of the dialog (sample 66678807):**

    Which results must change?                         (all ticked by default)
    Quality Control
      [x] Reads per sample (horizontal bar)    data: QC reads table (FastP, Quast, Bracken, metadata)  -> changed at the source
      [ ] Assembly quality (box plot)          data: Quast results + metadata, one row per sample and metric. Also read by: Cat (miaou)   -> unchanged
    Cat
      [x] miaou                                 data: the same table as Assembly quality          -> changed at this plot only (shared with an unticked plot)

**Pointers inside the recipe (options):**
- **(a) Use the fields that exist** (`description` on tables and datasets, `label` and `info` on plots), add a recipe-validator **advice** (never a block) "a table read by a plot has no description", and a prompt in the Blueprint form. Where nothing is written the dialog generates the sentence from the steps. Cheap, no format change.
- **(b) Add structured fields** for the things the dialog needs most: what one row is ("one row per sample and gene"), a role (quality control, analysis, reference). More precise, but a recipe-format change and more authoring work.
- **(c) Nothing in the recipe**, everything generated. Works for every recipe now, but cannot say what `ST22_Anchor` means in the lab's words.
**Recommendation: (a) now**, with the generated sentence as fallback, and (b) only the single hint "what one row is" later if users need it (it is the "rows are not samples" problem at the source). The generated sentences need a plain-language text for each of the 67 actions (the action catalogue has developer descriptions today): a content task, not code.

