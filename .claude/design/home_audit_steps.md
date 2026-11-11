# HOME: audit steps and the Audit workspace

**Status:** 2026-11-11, rewritten after Eve's review (history of the comments: git commit 5b59a4a). Companion:
`home_preview_filters.md`. Nothing here is code yet. Marks: **[built]**, **[to build]**, **[open]** = to decide.

## 1. The rule, in one sentence

**An audit step is the only way to change what a plot shows, what the data is and what is exported. It always has
a reason, it is recorded, it can be removed, and it never edits the original data (original T1 and T2).**

## 2. Vocabulary (agreed)

| Word | Meaning |
|---|---|
| **Original T1 / T2** | The stored stages exactly as the recipe built them. Cached, never changed. |
| **Audit T1 / audit T2** | The same stages rebuilt **from a copy** of the original with the audit steps applied. |
| **Audit T3 (of a plot)** | One plot's frame: its audit T2 plus the steps made for that plot only. Derived, not stored. |
| **Exploration** | Looking at Raw/Result with preview filters (`home_preview_filters.md`). Never changes anything. |
| **Validated step** | An audit step with its reason, applied. There is no draft: every step is validated when it is made, and removing a wrong step is the undo. |

Lineage chain used everywhere (in the workspace and in the diagrams):
`original T1 -> audit T1 -> audit T2 -> audit T3 (plot = xx)`.

## 3. The Audit workspace (new panel) [to build]

- A separate panel (lighter blue). It is **gated by the audit capability flag**: without it only Exploration
  exists (no My view scratchpad; ADR-085 is amended). It is exclusive with Exploration: opening one minimises
  the other.
- It shows **the selected plot** (audited) and its data, the **Compare** view (original Result plot | audited
  plot), the **step list** and the **lineage chain** of the plot.
- To make a step the user chooses **what** (kind), **where** (level, section 5) and the **reason**. The step is
  applied at once: no preview, no staged list. If it was a mistake, delete it from the step list.
- Before the step is applied the dialog shows **which lineages it will affect** (section 6). After it is applied
  an **impact report** shows rows removed per dataset and the plots that changed.

## 4. Kinds of step

| Kind | Example |
|---|---|
| **Exclude entities (by key)** | "sample ID2 is bad" |
| **Filter rows** | "identity >= 90", "keep 2023-2025" |
| **Drop column** | remove a column (warning: plots using it break, section 8) |

Aesthetic overrides (colour, shape) are plot-level appearance, out of scope of this file.

## 5. Levels: where a step acts (this is the scope)

The level decides which data and which plots are affected. One step has exactly one level.

| Level | Acts on | Affects | Typical use |
|---|---|---|---|
| **1. Project** (T1, all) | the start of every lineage whose data has the key | audit T1, T2, T3 of **every** plot downstream | remove a bad sample from the whole project |
| **2. Lineage** (T1, this lineage) | the start of the lineages that feed the chosen plot | audit T1, T2, T3 of the plots of those lineages | remove a sample only where this plot's data comes from |
| **3. Dataset** (T2) | the dataset's audit T2, after the recipe's tier-2 steps | **all plots that read that dataset** | a value filter on a derived column shared by plots |
| **4. Plot** (T3) | one plot (or several chosen plots) | only those plots | "years xx and yy are too small to compare in THIS plot" |

How steps combine, in order: level 1-2 steps -> the recipe's own tier-1/tier-2 steps -> level 3 steps -> level 4
steps. Consequences:
- **Two plots that share one T2:** a level 3 step changes both; a level 4 step changes only the chosen one.
- **"Only this plot" and the other plots untouched** = level 4. **A step for all plots of a dataset** = level 3.
  A single step cannot mix "T3 for this plot and T2 for the others"; that is two steps (level 3 plus level 4).
- **"Everyone except plot P" at level 3 does not exist** (T2 is shared); use level 4 steps on the others.
- T2 is a leaf stage: a level 3 step does not flow into other datasets' T1.
- Level 4 on several plots = pick the plots (default: this plot); a plot without the column is "not concerned"
  and listed.
- Default level proposed in the dialog: **4 (this plot)**, the safest. Levels 1-2 ask for a confirmation that
  names what will be rebuilt.

## 6. Showing the user what is affected [to build]

Every step dialog and every step in the list shows the lineage chain
`original T1 -> audit T1 -> audit T2 -> audit T3 (plot = xx)` as a small drawing:
- the level(s) the step changes in **bold and a different colour**; unaffected stages stay grey;
- under it, the list of **datasets and plots affected** (names), and for each, rows before/after;
- plots that **cannot show** the step, with the reason (column missing, plot uses a dropped column).

This is plain HTML/CSS in the panel, so colour and bold are possible.

## 7. Mechanics [to build, details open]

1. Original T1/T2 stay cached. Audit T1/T2 are derived from a **copy**; with no step, the audit stages ARE the
   original (same cache key, nothing recomputed).
2. Cache key of an audit stage = key of the original + hash of the ordered steps that apply to it (ADR-089
   chained keys). Removing a step returns to a previous key, so the earlier result is a cache hit. A small
   number of recent states is kept.
3. Level 1-2 steps are inserted at the start of the lineage in a **forked copy of the recipe** (same mechanism
   as the reproducibility export, ADR-097 `t3_translator`); level 3 steps after the dataset's tier-2 steps;
   level 4 steps on the plot frame at render time.
4. The key column of each dataset comes from the recipe's join steps (`on`, `left_on`/`right_on`; the app
   collects them as `primary_keys`). Different key families (sample_id, gene_id) are kept apart.
5. A key exclusion is inserted **at the sources** (before each ingredient's own tier-1 steps), so it is exact
   even when a tier-1 step aggregates across samples. [open: or on the anchor, simpler but not exact]
6. A dataset without the key, or a key value not present, is a reported no-op ("0 rows in MLST").
7. Cost: rebuilding can be heavy on large data. The dialog warns; incremental recomputation is a later
   optimisation (section 12).

## 8. Drop column warning [to build, #59]

Before a drop is applied the dialog lists the plots that use the column (x, y, colour, facet, layers) with a
warning that they will break. The user may continue. A plot broken by a drop shows
"column X was dropped by audit step N" instead of a generic render error.

## 9. Reason, undo, export

- **Reason** is required when the step is made. Removing a step needs no reason and is recorded.
- The step list shows level, kind, reason, date, who, and a delete button.
- **Export** (Mode 1 and 2, ADR-097) contains: the steps with level and reason, original T1 and T2, the audit
  T1/T2 and the T3 data of plots with level 4 steps, an **attrition table** (rows removed per dataset and
  step), and the forked recipe so the result can be re-run. Exploration is never exported.

## 10. Prior art (computer science)

- **Deletion propagation in databases** (Buneman, Khanna, Tan, PODS 2002): which source deletions remove a
  derived tuple; tractable for *key-preserving* views. Excluding by key is that easy case.
  https://www.cis.upenn.edu/~sanjeev/papers/pods02_view_deletion.pdf
- **Lineage-driven erasure** (GDPR in data lakes): delete at the source layer, propagate downstream, keep a
  record that proves it. Our step is a recorded exclusion with a reason; the original is kept.
  https://docs.databricks.com/aws/en/ldp/gdpr
- **Incremental view maintenance** (differential dataflow, DBSP): a deletion is a change of weight -1 that
  flows through joins and aggregates; only the affected part is recomputed. A later optimisation.
  https://arxiv.org/pdf/2203.16684v1.pdf
- **Column-level lineage tools** show impact before a change. https://docs.getdbt.com/docs/explore/column-level-lineage
- None is a ready-made answer; they support the design: act at the right level, rebuild downstream, record the
  reason, show the impact.

## 11. What exists today vs target

| Item | Today | Target |
|---|---|---|
| Plot-level filter/drop steps | per plot, propagation dialog "this / all / all except" [built] | level 4, pick plots; "all except" becomes picking plots |
| Concerned plots | checked on the data view (#58) | checked on the plot's audit T2 |
| Exclude by key at project/lineage level | not built; a `sample_id` filter on a plot without that column is skipped | levels 1-2 |
| Dataset-level step (shared T2) | not built | level 3 |
| Audit workspace, lineage chain drawing, impact report | not built | build |
| Draft / staged lists in audit | preview filters shown in My view | none: validated step + undo |
| Clear after apply | clears all preview rows | nothing to clear (no draft); Exploration lists are cleared by view change |
| My view without audit capability | offered (ADR-085) | not offered |
| Export | steps, T2, T3 data | + original T1/T2, audit T1/T2, attrition table, forked recipe |

## 12. Edge cases (each needs a test)

bad sample in no plot's column; present in some datasets only; key named differently across datasets; two key
families; exclusion then undo; two exclusions; exclusion plus a plot filter on the same column; plot on an
aggregate; two plots on one dataset (level 3 vs level 4); level 3 step on a column dropped by another step;
tier-1 step that aggregates across samples (source vs anchor insertion); a plot left with zero rows; a step on
a key that no dataset has; recipe switch with steps; export after a level 1 step (attrition table, forked
recipe re-runs to the same result); huge data (warning); order of steps; delete a step in the middle.

## 13. Open questions for Eve

1. Key exclusion inserted at the sources (exact, my recommendation) or on the anchor (simpler)?
2. Default level in the dialog: 4 (this plot)? Levels 1-2 with a confirmation?
3. How many recent audit states to keep in the cache (undo speed vs disk)?
4. "All except" at level 4 replaced by picking plots: OK?
