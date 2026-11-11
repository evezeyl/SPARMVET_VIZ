# HOME: audit steps and the Audit workspace

**Status:** 2026-11-11, third version, after Eve's second review (history: git commits 5b59a4a, e5ae922).
Companion: `home_preview_filters.md`. Nothing here is code yet. Marks: **[built]**, **[to build]**, **[open]**.

## 1. The rule, in one sentence

**An audit step is the only way to change what a plot shows, what the data is and what is exported. It always has
a reason, it is recorded, it can be removed, and it never edits the original data (original T1 and T2). The
audit exists to keep the WHOLE PROJECT consistent, not to explore data.**

**Recommended use (goes into the help):** make results publication-ready. Do not "clean" data to make it look
better. Remove only cases that are really bad or that make no sense to show, and say so ("data not shown" and
why): that is what the mandatory reason and the export are for. Results are often long format, where `sample_id`
repeats on many rows and is not unique in the original data; the audit works on that entity identifier.

## 2. Vocabulary (agreed)

| Word | Meaning |
|---|---|
| **Original T1 / T2** | The stored stages exactly as the recipe built them. Cached, never changed. |
| **Audit T1 / audit T2** | The same stages rebuilt from a copy of the original with the audit steps applied. |
| **Audit T3 (of a plot)** | One plot's frame: its audit T2 plus the steps made for that plot only. Derived. Exported as T3 data when a plot has its own steps. |
| **Filters** | The filter form (same widgets everywhere). In Exploration it makes a preview; in the Audit workspace the same form creates an audit step (section 3). |
| **Validated step** | An audit step applied with its reason. No draft: a step cannot be applied without a reason, and removing a wrong step is the undo. |

Lineage chain used everywhere (workspace and diagrams): `original T1 -> audit T1 -> audit T2 -> audit T3 (plot = xx)`.

## 3. The Audit workspace (a mode of HOME, reusing the existing panels) [to build]

The audit mode is not a new central page. It reuses what HOME already has, so very little new layout is needed:

| Where | What it holds in audit mode |
|---|---|
| **Left sidebar, Filters panel** | the shared filter form. Exploration: button "Add to preview". Audit mode: button **"Create audit step"**. Alerts (notification log) and processing issues stay in the left sidebar as today (checked in `home_theater.py`). |
| **Centre (kept as small as possible)** | the same plot and data components as today, fed with the audit data: the **audited plot** (audit T3), the audit table and **Compare** (original Result plot \| audited plot). Exploration is minimised (exclusive: opening one minimises the other). |
| **Right sidebar = the existing Pipeline Audit panel** (slot `audit_stack`, already gated by the sandbox flag) | the **step list** (kind, reach, reason, initials, date, status, delete; Undo last, Revert to step N, Remove all), the **lineage chain** (drawn vertically to fit), the list of **what is affected**, and a button to open the project overview. Today this panel holds the audit nodes and the apply tools (checked in `home_theater.py` and `sidebar_registry.py`); processing issues are in the LEFT sidebar, not here. |
| **Dialog "New audit step"** (replaces today's propagation dialog) | the reach selector (section 5), the stage choice when needed, the chain drawing and affected list for the step about to be made, the **reason** (required) and Apply. |
| **Dialog / wide view "Project overview"** | collections x steps and the coverage check (too wide for the sidebar). |

- **Gating:** the audit mode, the "Create audit step" button, the Audit panel and the dialogs are all gated by the
  **same sandbox flag** (today `t3_sandbox_enabled`). Without it only Exploration exists (no My view scratchpad;
  ADR-085 is amended).
- **Filters in audit mode.** The Exploration filters are not applied while audit mode is on (they are kept for
  when the user returns). The same form widgets are reused; **under the hood the two behave differently**
  (preview = lazy filter on the shown table; audit step = rebuild through the lineage, cached). A short note in
  the code and the docs states the difference.
- To make a step the user chooses the kind, the reach and the reason (sections 4-5). The step is applied at
  once. If it was a mistake, delete it from the step list (section 10).
- **Plots are not rebuilt in a new place.** The central plot and table handlers are the ones used today (My view
  already reads another data source for the same plots; Compare already has two panes). Only the data source
  changes to the audit data.

Wireframes of the screen with audit mode off and on: `UI-HOME-EXPLORATION` and `UI-HOME-AUDIT` (see also `HOME-AUDIT-PANEL`).

## 4. Kinds of step

| Kind | Example |
|---|---|
| **Exclude entities (by key)** | "sample ID2 is bad" |
| **Filter rows** | "identity >= 90", "keep 2023-2025" |
| **Drop column** | see the policy in section 9 |

Aesthetic overrides (colour, shape) are not implemented and out of scope (maybe one day).

## 5. Reach and stage: what the user chooses, and what happens (replaces "levels")

Two different questions, kept apart:
- **Reach**: which plots are affected. The user picks it with a **selector** (radio buttons, **nothing
  preselected** so the user must think); the option labels are in plain words and each shows the plots it means.
- **Stage**: where in the pipeline the step is inserted. It follows from the kind, not from the user.

| Reach (words the user sees) | Early stage (before the recipe's steps) | Late stage (after the recipe's tier-2) | Plot stage |
|---|---|---|---|
| **This plot only** | not available | not available | level 3 (T3) |
| **All plots that use the same table as this plot** (names listed) | level 1 (T1 of this collection) | level 2 (T2 of this collection) | n/a |
| **Every plot of the project** (all collections that have the key or column) | level 0 (project) | level 2 on every collection that has the column | n/a |

Numbers 0-3 are the internal names and follow the T numbers (project = 0, T1 = 1, T2 = 2, T3 = 3).
- **Key exclusion = early stage** (level 0 or 1). **Drop or filter on a column that only exists in T2 = late stage**
  (level 2). A filter on a column that exists at both stages needs one explicit choice: "before / after the
  recipe's steps" (default after) because filtering before or after an aggregation gives different science.
- **Levels 1 and 2 reach the same plots** (those reading this plot's collection). They differ by stage.
- **Order of application:** level 0-1 -> the recipe's own tier-1/tier-2 steps -> level 2 -> level 3.
- **Two plots that share one T2:** a level 2 step changes both; a level 3 step changes only the chosen plot(s).
- **A single step cannot mix "T3 for this plot and T2 for the others"**: that is two steps. "Everyone except
  plot P" does not exist at level 2 (T2 is shared); make level 3 steps on the others. At level 3 several plots
  are picked from a list (needs a plot navigator when there are many).
- T2 is a leaf stage: a level 2 step does not flow into other collections.
- Help and user documentation must explain the choice in these words, with the simple advice: **always use the
  lowest reach that fits what you want** (this plot, then this table, then the project).

## 6. Showing the user what is affected, and keeping the project consistent [to build]

1. **Chain drawing** in every step dialog and step-list entry: `original T1 -> audit T1 -> audit T2 -> audit T3
   (plot = xx)` with the stages the step changes in **bold and a different colour**, others grey (plain HTML/CSS).
2. **Affected list** under it: collections and plots affected (names), rows before/after, and plots that
   **cannot show** the step (reason).
3. **Project overview** in the workspace: rows = collections (and the plots reading them), columns = steps; each
   cell = applied / not concerned / not applied (by the user's reach) / broken; totals rows before -> after.
4. **Coverage check for key exclusions**: for each excluded key value, list the collections where that value
   still exists although it is excluded elsewhere ("ID2 is excluded in 9 of 11 collections; still present in
   Summary, Summary_quality"). A warning with a button "extend to the whole project". The user decides; the
   point is that an inconsistency is never silent. The coverage is written in the export report.

## 7. Mechanics [to build]

1. Original T1/T2 are never touched. The audit stages are derived from a **copy** and live in a **separate audit
   cache** (its own folder, never in the anchors folder; with no step the audit stages simply point at the
   originals, nothing is copied). Cache naming must make "original" and "audit" unmistakable.
2. **Invalidation by construction**: the key of an audit stage = SHA-256 of (the key of the stage before it + the
   **canonical list of operations that will actually be executed for this stage**: kind, column, operator, value,
   stage and insertion point, collection; sorted, values normalised). The reason, initials and date are **not** in
   the hash (they do not change the data). The same code produces the list that is hashed and the list that is
   run, so the hash cannot describe something different from what is done. The key is also stored inside the
   audit file and compared on read, as for the originals (ADR-089): a mismatch rebuilds. A level 1 step changes the
   T1 key and therefore every later key; a level 2 step changes only the T2 key and reuses audit T1. Nothing has to
   be "updated" by hand. Tests: every audit stage key contains its upstream key; different operation lists never
   give the same key; changing only the reason does not change the key; originals are never written by an audit.
3. **Limit and rebuild.** The audit cache keeps the current state plus the last N-1 states per recipe session
   (**N = 5 by default, a setting**); the oldest are removed (never the one in use). A missing, removed or corrupt
   entry is never a problem: it is rebuilt from the step list and the nearest cached earlier stage, or from the
   originals. The cache only speeds things up; the step list is the source of truth. When the recipe or the data
   change (the original keys change) the audit entries that depended on them are removed at that moment.
4. Early-stage steps are inserted **at the sources, inside the build of each reached collection** (before each
   ingredient's own tier-1 steps). Checked in the code: `prepare_ingredient` runs once per collection build, so
   this is exact (even when a tier-1 step aggregates across samples) and local to the reached collections.
5. Late-stage steps are inserted after the dataset's tier-2 steps; level 3 steps run on the plot frame at render
   time. A forked recipe (same mechanism as the reproducibility export, ADR-097 `t3_translator`) carries them.
6. A dataset without the key, or a key value not present, is a **reported no-op** ("0 rows in MLST"), always shown.
7. **Recipe good practice (docs, later a Blueprint check, not fixed now):** declare in a collection only the
   ingredients it uses. Today every collection build prepares ALL ingredient schemas, used or not, which makes
   audit rebuilds slower; the dummy ST22 recipe is an example of what to avoid.
8. Cost: rebuilding can be heavy on large data. The dialog warns. The audit is for production-ready figures, not
   for exploring data: limit it to changes that are really needed.

## 8. Keys: what the ST22 dummy recipe shows

All lineages of `1_test_data_ST22_dummy` carry `sample_id`, and `metadata_schema` is joined everywhere. Checked
in the recipe, joins and source file headers:

| Case found | Consequence for the design |
|---|---|
| `APEC_STEC_virulence_genes` (reference table, 4 columns) has no sample key and is no `sample_id` join | a sample exclusion does not apply; reported as "no key found, not affected" |
| `VirulenceFinder` has `metadata_sample_material` (name contains "sample" but is not a key) | **never detect keys by column name**; take them from the join steps (`on`, `left_on`/`right_on`) |
| `AR1_MLST_Serotype_Virulence` uses **left joins** | rows survive if only some ingredients lose the sample: the exclusion must apply to **every ingredient of the collection that has the key**, or rows with empty metadata remain |
| `Summary` and `Summary_quality` read the **same file** as two ingredients | both are excluded together |
| `ResFinder`, `Detailed_summary` have `Gene` / `Accession` | secondary keys; a sample exclusion removes that sample's gene rows; excluding by Gene is another key family (not in the first version) |
| `FastP`, `ResFinder` are data schemas used **directly** as plot targets | each is its own collection |
| `on` is a string in some joins and a list in others | both forms handled; the YAML `True` key trap too |
| No wrangling step renames `sample_id` | key columns stay stable through tier-1 in this recipe |

In the first version a key mapping comes from the join steps only; no manual mapping by the user. An ingredient
with no key found is reported, never guessed.

## 9. Drop column policy [to build; helper and message: #59]

- **Not recommended** as a project-wide or dataset-wide step. Allowed at plot level (level 3) for plotting needs,
  for example dropping an unclean column so the exported T3 data matches the plot.
- A drop of a column that **no plot, no contract and no step uses** is a recipe problem: the dialog suggests
  revising the recipe instead.
- Before any drop is applied the dialog lists the plots that use the column (x, y, colour, facet, layers) and
  the steps that use it, with a warning that they will break. The user may continue.
- A plot broken by a drop shows "column X was dropped by audit step N" instead of a generic error.

## 10. Deleting or changing a step

Steps are declarative and independent: **row steps (exclude, filter) combine as AND and drops as a union, so
their order inside one stage does not matter**; the stage order is fixed by the reach (section 5). So removing
any step is simply **"rebuild without it"**; later steps are not deleted and nothing has to be re-entered.
After the rebuild each remaining step is checked and shows a status:
- **Applied** (rows or columns changed);
- **Not concerned** (column or key absent in that collection);
- **Broken** (its column no longer exists, for example another step dropped it): shown in red with the reason.

A broken step does not fail silently: the export is refused until it is fixed or removed (like the existing key
check refusal). Safeguards at creation: adding a drop lists steps that use the column; adding a filter on a
column already dropped is not possible. Controls: **Undo last**, **Remove all steps** (back to the originals,
cheap thanks to the cache), **Revert to step N** (removes every step after N, in one action), delete any single
step, edit a step (= replace it).

## 11. Reason, who, export

- **Reason** is required when the step is made. Removing a step needs no reason and is recorded.
- The step list shows level, kind, reach, reason, **initials**, date and a delete button. **Who**: the app has no
  login, so the user may type optional initials once per session (several people can work on one project);
  empty is allowed.
- **Export** (Mode 1 and 2, ADR-097): the steps with level and reason, original T1/T2, audit T1/T2, T3 data of
  plots with level 3 steps, the **attrition table** (rows removed per collection and step), the **coverage
  check**, and the forked recipe so the result can be re-run. Exploration is never exported.

## 12. Prior art (computer science)

- **Deletion propagation in databases** (Buneman, Khanna, Tan, PODS 2002): tractable for *key-preserving* views;
  excluding by key is that easy case. https://www.cis.upenn.edu/~sanjeev/papers/pods02_view_deletion.pdf
- **Lineage-driven erasure** (GDPR in data lakes): delete at the source layer, propagate downstream, keep a
  record that proves it. https://docs.databricks.com/aws/en/ldp/gdpr
- **Incremental view maintenance** (differential dataflow, DBSP): a deletion is a change of weight -1 that
  flows through joins and aggregates; a later optimisation. https://arxiv.org/pdf/2203.16684v1.pdf
- **Column-level lineage tools** show impact before a change. https://docs.getdbt.com/docs/explore/column-level-lineage
- None is a ready-made answer; they support: act at the right reach and stage, rebuild downstream, record the
  reason, show the impact. These principles also go into the user help.

## 13. What exists today vs target

| Item | Today | Target |
|---|---|---|
| Plot-level filter/drop steps | per plot, dialog "this / all / all except" [built] | level 3, pick plots from a list |
| Concerned plots | checked on the data view (#58, closed: superseded by #60) | checked on the plot's audit T2 |
| Exclude by key | not built; a `sample_id` filter on a plot lacking the column is skipped | levels 0-1, exact at the sources |
| Dataset-level step (shared T2) | not built | level 2 |
| Audit workspace, chain drawing, project overview, coverage check | not built | build |
| Draft / staged lists in audit | preview filters shown in My view | none: validated step + undo |
| My view without sandbox flag | offered (ADR-085) | not offered |
| Export | steps, T2, T3 data | + original T1/T2, audit T1/T2, attrition table, coverage, forked recipe |
| Filters panel | one form, one global list | same form, two actions (preview / audit step) |

## 14. Impact of the change and what must be retested

Everything below is touched by this change and must be retested (headless suite, the full Playwright gate and the
HOME test plan items). First list, to complete with an impact check before the code starts:

| Component | What changes | Existing tests to re-run (new ones in the test plan) |
|---|---|---|
| `app/handlers/home_theater.py` | strip -> Exploration, panel dispatch, plot and table data sources, My view/Compare removed | `test_shiny_smoke`, `test_view_badge`, `test_render_every_plot`, `test_export_view_consistency`, `debug_home_theater` |
| `app/handlers/filter_and_audit_handlers.py` | shared filter form, two actions, new dialog, propagation replaced | `test_filter_operators`, smoke filter tests (new data-oracle suite) |
| `app/handlers/audit_stack.py` | step list, statuses, delete/undo, no draft | `test_session_manager` (gatekeeper), smoke `TestAuditGate` |
| `app/modules/t3_audit_engine.py` | filter apply, labels, skip rule | `test_filter_operators` |
| `app/modules/session_manager.py`, `session_handlers.py` | steps carry a level; old per-plot sessions map to level 3 | `test_session_manager`, `test_legacy_formats`, `test_write_t3_ghost_warning`, `debug_session_flow` |
| `app/modules/orchestrator.py`, `cache_keys.py` | audit overlay, separate audit cache, chained keys, no unused-ingredient builds | `test_cache_chain`, `test_tier2_store`, `test_anchor_determinism`, `test_data_analysis_recipe_data_check`, `test_retest_data_analysis_recipes` |
| `app/handlers/export_handlers.py`, `app/modules/exporter.py` | originals + audit data, attrition table, coverage, refusal on broken steps | `test_export_download`, `test_export_view_consistency`, `test_export_provenance` |
| `app/modules/bundle_importer.py`, `libs/blueprint_arch/.../t3_translator.py` | steps with levels, forked recipe, the four verification legs | `test_bundle_importer`, `libs/blueprint_arch/tests/test_t3_translator.py` |
| `app/src/server.py`, flags, `sidebar_registry.py`, `app_features_validator.py`, `config/app_features/*.yaml`, `config/ui/sidebars/home_standard_right.yaml` | audit mode gate, the existing `audit_stack` slot gets the new content, shared state | `test_every_app_features_starts`, validator tests, import check |
| Blueprint (`blueprint_handlers.py`, `wrangle_studio.py`), `data_import_handlers.py` | none by design, but they call the orchestrator | smoke Blueprint tests, import tests |
| VizFactory | clear message for a plot broken by a drop (#59) | viz_factory tests |
| Docs, help (`app/src/help/home.md`), user guide, FAQ, ADRs (085, 087, 097 notes), UML, `renamed_keys.py` check | rewritten | `audit_docs_sync`, `audit_uml_model` |

## 15. Edge cases (each needs a test)

bad sample in no plot's column; present in some collections only (coverage check); key absent in a dataset;
reference table without a key; left joins where only some ingredients are excluded; the same file read as two
ingredients; key on a secondary column; exclusion then undo; two exclusions; remove a step in the middle;
broken step after another step's drop; exclusion plus a plot filter on the same column; plot on an aggregate;
two plots on one collection (level 2 vs level 3); a tier-1 step that aggregates across samples; a plot left with
zero rows; a drop of a used column; a drop of an unused column; recipe switch with steps; export after a level 0
step (attrition, coverage, forked recipe re-runs to the same result); huge data (warning); cache depth reached;
Remove all steps returns to the originals; stage keys contain the upstream key.

## 16. Decided and open

**Decided:** one rule and vocabulary (sections 1-2); reach (selector, plain-word labels, nothing preselected) and
stage (from the kind) instead of levels; numbering 0-3; early insertion at the sources, inside each reached
collection; no draft; the Filters form is shared with two actions; audit mode, button, Audit panel and dialogs gated
by the sandbox flag; audit mode reuses the left Filters panel, the centre plot components and the existing right
Audit panel (a dialog replaces the propagation dialog); separate audit cache with chained keys, canonical hash, N = 5
by default as a setting, rebuild when missing; delete = rebuild without it; Undo last, Revert to step N, Remove all;
broken steps block the export; drop policy; project overview and coverage check; optional initials on each step.

**Open:**
1. Exact wording of the reach options and kinds (draft in section 17, to review together).
2. Manual key mapping by the user (not in the first version).
3. Excluding by a secondary key (Gene) in a later version.
4. Where the project overview opens (dialog or wide accordion under the table).
5. Where the mode switch (Exploration | Audit mode) sits on the screen.
6. What stays of the existing right Pipeline Audit panel: the "Inherited (Tier 2)" nodes, the filter inventory, the pending badge and the Apply gate (no draft, so no Apply gate is proposed).

## 17. Wording to review together (draft v1)

Kinds (what the user sees): "Remove samples (by ID)" | "Keep or remove rows by a value" | "Remove a column".
Reach (selector, nothing preselected; each option lists its plots and their number):
- "Only this plot" (1 plot: name)
- "All plots that use the same table as this plot" (N plots: names)
- "Every plot in the project" (N plots)

Under the selector, always: the lineage chain with the changed stages in bold and colour, the plots affected, rows
before/after. One-line advice: "Use the smallest choice that fits." Open wording questions: is "table" understood
(the data table behind the plot) or better "data set"/"data"? Is "Every plot in the project" clear when some plots
do not contain the sample? (the dialog then says "N plots contain it, M do not").
