# HOME: audit steps and the Audit workspace

**Status:** DRAFT 2026-11-11, written with Eve. Companion: `home_preview_filters.md`. Nothing here is code until
Eve has read both files and the diagrams. Marks: **[built]**, **[decided]**, **[open]**.

## 1. The rule, in one sentence

**An audit step is the only way to change what a plot shows, what the data is, and what is exported. It always
has a reason, it is recorded, and it never edits the reference data (the stored T1 and T2).**

## 2. Vocabulary (agreed)

| Word | Meaning |
|---|---|
| **Reference T1 / T2** | The stored stages, exactly as the recipe built them. Never changed. |
| **Audited lineage T1\* / T2\*** | The same stages rebuilt with the lineage-level audit steps applied (derived, cached, not the reference). | @eve : we will need to think about the cashing system - if we want to be efficient we need to keep original T1, T2 cached if we eg. return to empty state of audit (removing all audit steps and applied). So the audit should work from copy of T1 -> audit_T1 and then derive T2 and T3 from there. This also means that the way the audit recipe export will need to be changed to export the audited data  + the original T1 (original_T1) 
| **T3 of a plot** | That plot's frame: its T2\* plus its plot-level audit steps. Derived, not stored. | @will we still have a T3 if we have to derive T2 - because then the steps can be added directly to T2 no ? 
| **Preview** | Temporary look at Raw or Result (`home_preview_filters.md`). | @eve : yes but we still need a propagation so it is different than the other preview mode no ? but it is where the caching mechanism is leveraged. 
| **Draft step** | A step being tried in the Audit workspace; shown applied there, not yet sent. | @eve: Draft 
| **Audit step** | A draft step that was sent with a reason and applied. | @eve: Validated 

## 3. The Audit workspace (new panel) [decided]

- A separate panel (lighter blue, kept apart from Exploration). While it is open the Exploration strip is
  minimised to give space. @eve: it will need to be gated correctly, 
- It shows **the selected plot** and its data, and a small **lineage tree** of that plot (ingredient datasets ->
  join -> T2 -> T3), built from the existing backward trace (`build_plot_lineage`). A forward trace
  (dataset -> plots that depend on it) is to build. @eve : original_T1 -> audit_T1 -> audit_T2 (-> audit T3 if T3 is necessary)
- You choose the **kind of step**, the **stage or dataset** it applies to, and the **scope**; you try it as a
  **draft step** (shown on the plot and the data of the workspace), see the **impact preview**, write the
  **reason**, then **Apply** produces Audit step. 
- **Compare** (Reference Result vs audited) lives here.
- Offered only when audit capability is on. [open: ADR-085 offers My view without audit as a scratchpad; Eve:
  only when audit is on. Decide for the configs without audit.]

@eve : here in this mode - I am wondering if we should not just remove the preview : you do and send to audit - if you are wrong you remove from audit - its not exploration anymore - That would simplify our model. We are sure we want some changes - but we let the possibility of reversal if error has been made - That would simplify the steps for the users. 

@eve: start to review above - I did not yet read the rest. 
## 4. Kinds of audit step

| Kind | Example | Where it acts | Scope choices |
|---|---|---|---|
| **A. Exclude entities (key)** [decided, to build] | "sample ID2 is bad" | At the start of the lineage: T1 of every chosen dataset that has the key, **before** the recipe's tier-1/tier-2 steps. T1\* and T2\* are rebuilt from it. | **Whole project** = every dataset that has the key. **This lineage** = the datasets that feed the chosen plot. [open: pick datasets; which is the default] |
| **B. Filter rows (plot level)** [built, per plot] | "keep only 2023" | On one plot's T3 (T2\* plus step). | This plot / all plots / all except (propagation into the T3 of every *concerned* plot). |
| **C. Drop column (plot level)** [built, per plot] | remove a column from one plot's data | Same as B. | Same as B, **with a warning** listing plots that use the column (#59). |

*Concerned plot* = the column exists in that plot's T2\* (the lineage, not the data view; #58).
Aesthetic overrides (colour, shape) are a separate plot-level kind, out of scope of this file.

## 5. Why kind A is lineage-level (the science problem)

A plot-level filter on `sample_id` cannot remove a sample from a plot whose data has no `sample_id` (for example
counts per year): the plot silently keeps the bad sample. Applying the exclusion at the start of the lineage and
rebuilding downstream fixes this, including aggregates. Because the exclusion is by **key**, not by an arbitrary
output row, it is the easy case of the database "deletion propagation" problem (see section 9).

## 6. How kind A works (mechanics) [decided in principle, details open]

1. The key column of each dataset comes from the recipe's join steps (`on`, `left_on`/`right_on`; the app
   already collects them as `primary_keys`). Different key families (sample_id, gene_id) are kept apart.
2. A step "exclude key = value(s)" is inserted at the top of tier-1 of each chosen dataset, in a **forked copy**
   of the recipe (same mechanism as the reproducibility export, ADR-097 `t3_translator`).
3. T1\* and T2\* are materialised from the fork and cached under a key that includes the hash of the audit steps
   (ADR-089 chained keys). The reference files are untouched.
4. A plot reads T2\* (then its own plot-level steps = T3). The Result plot in Exploration still reads the
   reference.
5. Undo = delete the step; the cache key changes; the lineage is rebuilt without it.
6. A dataset without the key, or a key value not present, is a reported no-op ("0 rows in MLST").
7. Order of steps is kept and shown; several exclusions combine.
8. Cost: rebuilding can be heavy on large data. Warning in the dialog; incremental maintenance is a possible
   later optimisation (section 9).

## 7. Impact preview, reason, Apply [decided]

Before Apply the workspace shows: rows removed per dataset (attrition), plots that change, plots that cannot
show the step (and why), for drops the plots that use the column. Reason is required. Apply records the step,
rebuilds what is needed, and **clears the draft list** so the user sees what is committed and what is not.

## 8. Export and trace [decided in principle]

Bundle contains: the audit steps with reasons, the data of the audited lineage (T1\*/T2\*) and T3 data per plot,
an **attrition table** (rows excluded per dataset and step), and the forked recipe so the result can be re-run
(ADR-097). Preview filters are not exported.

## 9. Prior art (computer science, not only bioinformatics)

- **Deletion propagation in databases** (Buneman, Khanna, Tan, PODS 2002): which source deletions remove a
  derived tuple, with *source* and *view side effects*; it ties to why-/where-provenance and is tractable for
  *key-preserving* views. Our exclusion is by key, so it falls in the tractable case.
  https://www.cis.upenn.edu/~sanjeev/papers/pods02_view_deletion.pdf ,
  https://en.wikipedia.org/wiki/Reverse_data_management
- **Lineage-driven erasure** (GDPR in data lakes): delete at the source layer first, then propagate to derived
  layers; keep a record that proves it happened (tombstone, reason). Our step is a recorded exclusion at the
  lineage root; the reference data is kept (not erasure).
  https://docs.databricks.com/aws/en/ldp/gdpr
- **Incremental view maintenance** (differential dataflow, DBSP): a deletion is a change with weight -1 that
  flows through joins and aggregates, so only the affected part is recomputed. A possible optimisation for
  large data. https://arxiv.org/pdf/2203.16684v1.pdf
- **Column-level lineage tools** (impact analysis before a change). https://docs.getdbt.com/docs/explore/column-level-lineage
- Honest note: none of these is a ready-made answer for this app; they support the design (exclude at the
  root by key, rebuild downstream, record the reason, report impact).

## 10. What exists today vs target

| Item | Today | Target |
|---|---|---|
| Plot-level steps B and C | per plot, propagation dialog, `t3_audit_steps_by_plot` [built] | keep; concerned plots by T2\*; drop warning |
| Concerned-plot check | uses the data view (T1 or T2) (#58) | uses the plot's T2\* |
| Kind A (exclude by key) | not built; a `sample_id` filter on a plot lacking the column is skipped | lineage-level, whole project / this lineage |
| Audit workspace, impact preview, attrition | not built | build |
| Draft step | preview filters shown in My view | draft step in the workspace |
| Clear after Apply | clears all preview rows, every dataset | clears the draft list |

## 11. Edge cases (each needs a test)

bad sample present in no plot's column; present in some datasets only; key column named differently across
datasets; two key families; exclude then undo; two exclusions; exclusion + plot filter on the same column;
plot on an aggregate; plot sharing a dataset; recipe switch; export after an exclusion (attrition table, forked
recipe re-runs to the same result); huge data (warning); step on a key that no dataset has.

## 12. Open questions for Eve

1. Default scope of kind A: whole project or this lineage?
2. Pick datasets by hand (third option) or only the two?
3. Audit workspace in configs without audit capability (ADR-085 scratchpad).
4. Cache: store T1\*/T2\* files or rebuild on demand? (Eve: few changes expected; warn on huge data.)
