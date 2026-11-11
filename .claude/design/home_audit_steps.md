# HOME: audit steps and audit mode

**Status:** 2026-11-11, version 4, after the full consistency review with Eve (history: git commits 5b59a4a, e5ae922,
069052b). Companion: `home_preview_filters.md`. Decision record: ADR-099 (`architecture_decisions.md`). Nothing here
is code yet. Marks: **[built]**, **[to build]**, **[confirm]** = my proposal from the review, Eve to confirm before code.

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
| **Data schema** (an **ingredient** when it is joined) | One source file with its contract (`input_fields`) and its own tier-1 steps. In the recipe: `data_schemas:`, `dataset_id`. |
| **Join** | A combination of data schemas into one table (`joins:`; older text says "assembly"). |
| **Collection** | What a plot reads: a **join**, or a **data schema used directly** (a recipe without joins, such as `3_test_no_joins`). Internal word: `target_dataset` in a plot spec, `collection_id` in the code. |
| **Table** (the user's word) | The data table behind a plot = the T2 of its collection. |
| **Dataset** | Avoid in new text: the recipe uses it loosely for a data schema (`dataset_id`) and for a plot's target (`target_dataset`). |
| **Original T1 / T2** | The stored stages of a collection exactly as the recipe built them. Cached, never changed. |
| **Audit T1 / audit T2** | The stages of a collection **recomputed** with the audit steps applied. With no early step there is no audit T1: the original T1 is used as it is. Nothing is ever copied: a stage is either reused or recomputed. |
| **Audit T3 (of a plot)** | One plot's frame: its audit T2 plus the steps made for that plot only. Derived, not stored. Exported as T3 data when a plot has its own steps. |
| **Exploration** | Looking at Raw/Result with preview filters (`home_preview_filters.md`). Changes nothing. |
| **Audit mode** | The HOME mode in which audit steps are made and removed. (Earlier drafts: "Audit workspace".) |
| **Filters** | The filter form (same widgets everywhere). In Exploration it makes a preview; in audit mode the same form creates an audit step (section 3). |
| **Validated step** | An audit step applied with its reason. No draft list: a step cannot be applied without a reason and the Apply press, and removing a wrong step is the undo. |
| **Key** (entity ID) | The column that identifies the entity (for example `sample_id`), **declared with `is_primary_key: true`** in the data schema's `input_fields`. In long-format tables it repeats on many rows: "key" means the entity identifier, not a unique row key. |
| **Key family** | The columns that identify the same entity across the recipe: the declared keys, linked when a join equates differently named columns (`on`, or `left_on` = `right_on`). Example: `sample_id`. Never found from column names. |

Lineage chain used everywhere (screens and diagrams): `original T1 -> audit T1 -> audit T2 -> audit T3 (plot = xx)`.

## 3. Audit mode (a mode of HOME, reusing the existing panels) [to build]

Audit mode is not a new central page. It reuses what HOME already has, so very little new layout is needed:

| Where | What it holds in audit mode |
|---|---|
| **Mode switch** | **Exploration \| Audit mode**, at the **left of the group-tabs row**, high in the centre (decided by Eve: saves a full row). Shown only with the sandbox flag. |
| **Left sidebar, Filters panel** | the shared filter form. Exploration: button "Add to preview". Audit mode: button **"Create audit step"**. Alerts (notification log) and processing issues stay in the left sidebar as today (checked in `home_theater.py`). |
| **Centre (kept as small as possible)** | the same plot and data components as today, fed with the audit data: the **audited plot** (audit T3), the audit table, and **Compare** (original Result plot \| audited plot) as an **on/off toggle**. The Exploration strip is minimised (exclusive: opening one minimises the other). |
| **Right sidebar = the existing Pipeline Audit panel** (slot `audit_stack`, already gated by the sandbox flag) | the **step list** (kind, reach, reason, initials, date, status, delete; Undo last, Revert to step N, Remove all), the **lineage chain** (drawn vertically to fit), the list of **what is affected**, and a button to open the project overview. Today this panel holds the audit nodes and the apply tools (checked in `home_theater.py` and `sidebar_registry.py`); processing issues are in the LEFT sidebar, not here. |
| **Dialog "New audit step"** (replaces today's propagation dialog) | the kind, the reach selector (section 5), the chain drawing and affected list for the step about to be made, warnings, the **reason** (required), optional initials, and two buttons, **Cancel** and **Apply**. |
| **Dialog "Project overview"** | collections x steps and the coverage check (too wide for the sidebar). |

- **Gating (one rule).** The mode switch, the "Create audit step" button, the Pipeline Audit panel, the dialogs and
  Compare are all gated by the **sandbox flag** (today `t3_sandbox_enabled`) on top of `interactivity_enabled`.
  Without the sandbox flag only Exploration exists (no My view scratchpad; ADR-085 is amended). Consequences to
  enforce with the flag validator (section 14): `comparison_mode_enabled` becomes a child of the sandbox flag
  (today `pipeline-exploration-simple` has comparison on and sandbox off: a dead flag), and the sandbox flag
  requires the right sidebar slot `audit_stack` to exist (else the step list has no place).
- **Filters in audit mode.** The Exploration filters are not applied while audit mode is on (they are kept for
  when the user returns; switching mode is not a view change). The same form widgets are reused; **under the hood
  the two behave differently** (preview = lazy filter on the shown table; audit step = recomputation through the
  lineage, cached). A short note in the code and the docs states the difference. In audit mode the form offers
  the columns of the plot's **audit T2** (the stage steps apply on), not those of the Raw/Result view.
- **Columns and values come from the data, never from the plots.** For a plot-level step (level 3) from the plot's
  T3 frame; for a late step (level 2) from the collection's audit T2; for "remove samples" (levels 0-1) the key
  values found in the sources of the reached collections (distinct, with a search box and a paste-a-list field, since
  there can be thousands of IDs). The plots only decide *where* a step applies (the reach).
- To make a step the user chooses the kind, the reach and the reason (sections 4-5), reads the information in
  the dialog (chain, affected plots, warnings, rows before/after) and presses **Apply** (enabled only when a
  reach is chosen and a reason is written; **Cancel** closes the dialog and changes nothing). Apply is the pause
  that lets the user read before committing. **There is no draft list and no Apply gate in the Audit panel**: the
  step is applied when Apply is pressed in the dialog. If it was a mistake, delete it from the step list
  (section 10).
- **Compare** is shown only when the existing flag `comparison_mode_enabled` is on (checked in `home_theater.py`,
  `app_features_validator.py`). Off: the audited plot uses the full width.
- **Audit table stage selector [confirm]:** the audit table can show audit T1 | audit T2 | audit T3 of the plot
  (read-only, no filters there), so the user can check where a sample was removed (Eve's idea of selecting T1, T2,
  T3 in the workspace).
- **Plots are not rebuilt in a new place.** The central plot and table handlers are the ones used today (My view
  already reads another data source for the same plots; Compare already has two panes). Only the data source
  changes to the audit data.

Screens: `UI-HOME-EXPLORATION` (audit mode off) and `UI-HOME-AUDIT` (audit mode on).

## 4. Kinds of step

| Kind (user wording) | Example | Today's node type |
|---|---|---|
| **Remove samples (by ID)** = exclude entities by key | "sample ID2 is bad" | `exclusion_row` (plot level) |
| **Keep or remove rows by a value** = filter rows | "identity >= 90", "keep 2023-2025" | `filter_row` |
| **Remove a column** = drop column (policy: section 9) | | `drop_column` |

Existing step types that are NOT new kinds: `developer_raw_yaml` (BLUEPRINT's YAML escape hatch, translated by
`t3_translator`) stays as it is: listed in the step list as "recipe fragment", deletable, **never authored in
audit mode**; `aesthetic_override` (colour, shape) is not implemented and stays out of scope (maybe one day).
Old sessions: every saved per-plot node maps to a level 3 step of the same kind with reach "these plots", empty
initials; legacy types are kept as they are.

## 5. Reach and stage: what the user chooses, and what happens (replaces "levels")

Two different questions, kept apart:
- **Reach**: which plots are affected. The user picks it with a **selector** (radio buttons, **nothing
  preselected** so the user must think); the option labels are in plain words and each shows the plots it means.
- **Stage**: where in the pipeline the step is inserted. It follows from the kind and the reach, not from the user.

| Reach (words the user sees) | Remove samples (by ID) | Filter rows by a value / Remove a column |
|---|---|---|
| **Selected plots** (a checklist of the recipe's plots, grouped by tab, the open plot marked; one checked = "only this plot") | level 3 on each selected plot: a row filter on the key column of the plot's T3 frame (only if the frame has it; otherwise "this plot cannot show it") | level 3 on each selected plot |
| **All plots that use the same table as this plot** (names listed) | **level 1**: early, at the sources of this collection | **level 2**: late, on T2 of this collection, after its tier-2 steps |
| **Every plot in the project** | **level 0**: early, at the sources of every collection that has the key | level 2 on every collection that has the column (others: "not concerned") |

The checklist is built from the recipe's `analysis_groups`, so the selector adapts to every recipe. **[confirm]** three
options with a checklist, instead of four options ("only this plot" and "these plots" merged). **[open]** where the
reach selector sits: in the "New audit step" dialog (proposed: everything to read and decide is in one place, and
Apply stays disabled until a reach is chosen), or in the Filters panel next to the form, with the dialog only
confirming.

Numbers 0-3 are the internal names and follow the T numbers (project = 0, T1 = 1, T2 = 2, T3 = 3). The user never
sees them.
- **Value filters and drops are never inserted early** [confirm]. The filter form offers the columns of the plot's
  audit T2, whose names can come from renames or derived columns that do not exist at the sources, so an early
  insertion could hit the wrong column or none. Filtering before an aggregation is a recipe change (tier-1 steps),
  not an audit step. Only **key exclusion** is early, because keys come from the join steps and are stable.
  (This replaces the earlier "before / after the recipe's steps" choice.)
- **Levels 1 and 2 reach the same plots** (those reading this plot's collection). They differ by stage.
- **Order of application:** level 0-1 -> the recipe's own tier-1/tier-2 steps -> level 2 -> level 3.
- **Two plots that share one T2:** a level 2 step changes both; a level 3 step changes only the chosen plot(s).
- **A single step cannot mix "T3 for this plot and T2 for the others"**: that is two steps. "Everyone except
  plot P" does not exist at level 2 (T2 is shared); check the other plots in "Selected plots". The checklist needs
  a navigator (grouped by tab, with a search box) when there are many plots.
- T2 is a leaf stage: a level 2 step does not flow into other collections (checked: a join cannot be an
  ingredient of another join; the orchestrator keeps only data schemas as ingredients).
- Help and user documentation must explain the choice in these words, with the simple advice: **always use the
  lowest reach that fits what you want** (this plot, then this table, then the project).

## 6. Showing the user what is affected, and keeping the project consistent [to build]

1. **Chain drawing** in every step dialog and step-list entry: `original T1 -> audit T1 -> audit T2 -> audit T3
   (plot = xx)` with the stages the step changes in **bold and a different colour**, others grey (plain HTML/CSS).
2. **Affected list** under it: collections and plots affected (names), rows before/after, and plots that
   **cannot show** the step (reason).
3. **Project overview**: rows = collections (and the plots reading them), columns = steps; each cell = applied /
   not concerned / not applied (by the user's reach) / broken; totals rows before -> after.
4. **Coverage check for key exclusions**: for each excluded key value, list the collections where that value
   still exists although it is excluded elsewhere ("ID2 is excluded in 9 of 11 collections; still present in
   Summary, Summary_quality"). A warning with a button "extend to the whole project". The user decides; the
   point is that an inconsistency is never silent. The coverage is written in the export report.
5. **Impact before Apply [confirm]:** the numbers in the dialog come from a **trial computation** of the stages
   the step would change, stored in the audit cache under the key of the would-be step list. Pressing Apply then
   adopts it (a cache hit), Cancel leaves it to age out (it counts toward the N states). Exact, and it costs one
   computation, not two. For very large data the dialog may offer "estimate only" (counts on the stored stages).

## 7. Mechanics [to build]

1. Original T1/T2 are never touched. The audit stages are **recomputed** and live in a **separate audit cache**
   (its own folder, never in the anchors folder; with no early step the audit T1 does not exist and the original
   T1 is used as it is). Cache naming must make "original" and "audit" unmistakable.
2. **Invalidation by construction**: the key of an audit stage = SHA-256 of (the key of the stage before it + the
   **canonical list of operations that will actually be executed for this stage**: kind, column, operator, value,
   stage and insertion point, collection; sorted, values normalised). The reason, initials and date are **not** in
   the hash (they do not change the data). The same code produces the list that is hashed and the list that is
   run, so the hash cannot describe something different from what is done. The key is also stored inside the
   audit file and compared on read, as for the originals (ADR-089): a mismatch recomputes. A level 1 step changes
   the T1 key and therefore every later key; a level 2 step changes only the T2 key and reuses the T1 stage. Nothing
   has to be "updated" by hand. Tests: every audit stage key contains its upstream key; different operation lists
   never give the same key; changing only the reason does not change the key; originals are never written by an
   audit.
3. **Limit and recompute.** The audit cache keeps the current state plus the last N-1 states per recipe session
   (**N = 5 by default, a setting**); the oldest are removed (never the one in use). A missing, removed or corrupt
   entry is never a problem: it is recomputed from the step list and the nearest cached earlier stage, or from the
   originals. The cache only speeds things up; the step list is the source of truth. When the recipe or the data
   change (the original keys change) the audit entries that depended on them are removed at that moment. Location:
   under `user_data` next to `anchors/`, in `audit/<session_key>/`.
4. **Key mapping.** Built once per recipe from (a) the **declared keys**: every input field with
   `is_primary_key: true` in a data schema (an existing, documented property of the data contract), and (b) the
   **join steps** (`action: join`, `on` as a string or a list, `left_on`/`right_on`), which link differently named
   columns into one key family and flag a join on a column that is not declared (a warning for the recipe author).
   A collection that is a join takes the keys of its ingredients. A **data schema used directly** (a recipe without
   any join, such as `3_test_no_joins`) has its declared key and needs no join, so removing samples by ID works there
   too. A data schema with **no declared key and no join** has no key: reported "no key declared"; for it, "Remove
   samples" falls back to a row filter on a column the user picks (late stage or plot), with a warning if the
   table's steps contain aggregations (a filter after an aggregation does not change the aggregate). Never found from
   column names. **Today's `extract_primary_keys` returns an empty list on tiered join steps (issue #61); the new
   mapping replaces it and has a test on the shipped recipe.**
5. **Early insertion (key exclusion only)** is at the sources, **inside the build of each reached collection**,
   on each ingredient that has the key family, before that ingredient's own tier-1 steps. Checked in the code:
   `prepare_ingredient` runs once per collection build, so this is exact (even if a tier-1 step aggregates across
   samples) and local to the reached collections. Values are compared as strings (as `_apply_filter_rows` does), so
   a tier-1 `cast sample_id -> String` does not matter. If a tier-1 step **renames** the key column the insertion is
   refused with a clear message ("key renamed in tier-1 of X, keep key names in the recipe"), never silently skipped.
6. **Late and plot steps.** Level 2 steps are inserted after the collection's tier-2 steps; level 3 steps run on the
   plot frame at render time. A **forked recipe** carries levels 0-2 (same mechanism as the reproducibility export:
   `t3_translator`, ADR-097, which today forks the join per plot and appends level 3 steps to its tier-2). The
   translator is extended with two modes: shared late insertion (level 2) and early source insertion (levels 0-1).
   The user's recipe files are never edited.
7. A dataset without the key, or a key value not present, is a **reported no-op** ("0 rows in MLST"), always shown.
8. **Recipe good practice (docs now, a Blueprint check later, not enforced in the first version):**
   (1) declare `is_primary_key: true` on the ID column of every data schema that has one; (2) use the **same column
   name** for the same ID in all data schemas: different names work (`left_on`/`right_on`, and the key family links
   them) but then both columns exist after the join and every step must handle both; (3) **never rename or
   recompute the ID column in tier-1** (an early removal is refused with a message if it is renamed); (4) declare in
   a join only the ingredients it uses (today every collection build prepares ALL ingredient schemas, used or not,
   which makes audit recomputation slower; the ST22 dummy recipe is an example to avoid).
9. Cost: recomputing can be heavy on large data. The dialog warns. The audit is for production-ready figures, not
   for exploring data: limit it to changes that are really needed.
10. **Apply is atomic.** The step list changes only if the recomputation succeeds. If it fails (an error, a plot
    left with no rows, a key renamed in tier-1) the previous state stays and the error is shown with the existing
    error surface (ADR-094). While it runs, the plots show the existing "recalculating" overlay and Apply is
    disabled; the result of a long computation is not lost if the user waits.

## 8. Keys: what the ST22 dummy recipe shows (checked in the recipe files, 2026-11-11)

All collections of `1_test_data_ST22_dummy` carry `sample_id`, and `metadata_schema` is joined in most. Verified from
the recipe, its joins and the source file headers:

| Case found | Consequence for the design |
|---|---|
| `is_primary_key: true` is declared on `sample_id` in 10 of the 11 ST22 data schemas; **not** on `APEC_STEC_virulence_genes` (reference table, 4 columns) | the key mapping starts from the declared keys; a sample exclusion does not apply to the reference table, reported as "no key declared, not affected" |
| `VirulenceFinder` has `metadata_sample_material` (name contains "sample" but is not a key) | **never detect keys by column name**; take them from the join steps |
| `AR1_MLST_Serotype_Virulence` uses **left joins** | rows survive if only some ingredients lose the sample: the exclusion must apply to **every ingredient of the collection that has the key**, or rows with empty metadata remain |
| `Summary` and `Summary_quality` read the **same file** as two ingredients | both are excluded together |
| `ResFinder`, `Detailed_summary` have `Gene` / `Accession` | secondary keys; a sample exclusion removes that sample's gene rows; excluding by Gene is another key family (not in the first version) |
| `ResFinder` is a data schema used **directly** as a plot collection (plot `amr_heatmap`); `FastP` also has a plot spec (`FastP_reads_boxplot`) that is **not mounted** in `analysis_groups` | a bare data schema is its own collection; its key comes from the joins where it is an ingredient (section 7.4) |
| `on` is a string in some joins and a list in others | both forms handled; the YAML `True` key trap too |
| `sample_id` is **cast to String** at tier-1 in `ResFinder` and in the `ST22_Anchor` join; **no** step renames it (only `VF_gene`, `VF_protein` are renamed) | values are compared as strings; the rename refusal of 7.5 does not fire here |
| aggregations by sample exist (`count_by_group` by `sample_id` in the `ResFinder` and `ST22_Anchor` tier-2; `summarize` by `sample_id, ST` in the `Summary_phenotype_length_fragmentation` tier-1) but **none aggregates across samples** | exclusion at the sources and on T1 give the same rows here; the test with a recipe that aggregates across samples must be synthetic |

In the first version the key mapping comes from the declared keys and the join steps; no manual mapping by the user.

## 9. Drop column policy [to build; helper and message: #59]

- **Not recommended** as a project-wide or dataset-wide step. Allowed at plot level (level 3) for plotting needs,
  for example dropping an unclean column so the exported T3 data matches the plot. (At level 2 it is possible
  but gets a stronger warning.)
- A drop of a column that **no plot, no contract and no step uses** is a recipe problem: the dialog suggests
  revising the recipe instead.
- Before any drop is applied the dialog lists the plots that use the column (x, y, colour, facet, layers) and
  the steps that use it, with a warning that they will break. The user may continue.
- A plot broken by a drop shows "column X was dropped by audit step N" instead of a generic error.

## 10. Deleting or changing a step

Steps are declarative and independent: **row steps (exclude, filter) combine as AND and drops as a union, so
their order inside one stage does not matter**; the stage order is fixed by the reach (section 5). So removing
any step is simply **"recompute without it"**; later steps are not deleted and nothing has to be re-entered.
After the recomputation each remaining step is checked and shows a status:
- **Applied** (rows or columns changed);
- **Not concerned** (column or key absent in that collection);
- **Broken** (its column no longer exists, for example another step dropped it): shown in red with the reason.

A broken step does not fail silently: the export is refused until it is fixed or removed (like the existing key
check refusal). Safeguards at creation: adding a drop lists steps that use the column; adding a filter on a
column already dropped is not possible. Controls: **Undo last**, **Remove all steps** (back to the originals,
cheap thanks to the cache), **Revert to step N** (removes every step after N, in one action), delete any single
step, edit a step (= replace it).

## 11. Reason, who, step record, export

- **Reason** is required when the step is made. Removing a step needs no reason and is recorded.
- **Who**: the app has no login, so the user may type optional initials once per session (several people can
  work on one project); empty is allowed.
- **Event log [confirm]:** the step list shows what exists now; an append-only **event log** records every
  creation, removal and revert (time, initials, the step, the reason of a creation). It is exported with the audit
  trail, so removing a step to hide it is visible. Without it "removing a step is recorded" would not be true.
- **Step record** (stored in the session, shown in the list, exported): `id`, `kind`, `reach`, `level`, `targets`
  (collections or plots), `params` (column, operator, value; or key family and values), `reason`, `initials`,
  `created_at`. The **status** (applied / not concerned / broken) is computed, never stored.
- **Sessions:** the step list is the source of truth and is saved with the session (today's T3 ghost is written
  when a step is applied or removed and on leaving HOME); restoring recomputes. If the recipe or the data changed
  since the session was saved, steps whose columns or keys are gone show "broken" and the existing "saved against
  a different version" warning is kept.
- **Export** (Mode 1 and 2, ADR-097): the steps with level and reason, original T1/T2, audit T1/T2, T3 data of
  plots with level 3 steps, the **attrition table** (rows removed per collection and step), the **coverage
  check**, the audit cache keys (so the key check of ADR-089 also covers the audit stages), and the forked recipe
  so the result can be re-run. Exploration is never exported. **To detail with the export build:** the four
  verification legs of the importer (data, engine, recipe, steps): the recipe leg stays the hash of the original
  recipe file set, the steps leg becomes the hash of the ordered step list, and the forked recipe gets its own
  hash.

## 12. Prior art (computer science)

- **Deletion propagation in databases** (Buneman, Khanna, Tan, PODS 2002): tractable for *key-preserving* views;
  excluding by key is that easy case. https://www.cis.upenn.edu/~sanjeev/papers/pods02_view_deletion.pdf
- **Lineage-driven erasure** (GDPR in data lakes): delete at the source layer, propagate downstream, keep a
  record that proves it. https://docs.databricks.com/aws/en/ldp/gdpr
- **Incremental view maintenance** (differential dataflow, DBSP): a deletion is a change of weight -1 that
  flows through joins and aggregates; a later optimisation. https://arxiv.org/pdf/2203.16684v1.pdf
- **Column-level lineage tools** show impact before a change. https://docs.getdbt.com/docs/explore/column-level-lineage
- None is a ready-made answer; they support: act at the right reach and stage, recompute downstream, record the
  reason, show the impact. These principles also go into the user help.

## 13. What exists today vs target

| Item | Today | Target |
|---|---|---|
| Plot-level filter/drop steps | per plot, dialog "this / all / all except" [built] | level 3, reach "only this plot" or "these plots (pick)" |
| Concerned plots | checked on the data view (#58, closed: superseded by #60) | checked on the plot's audit T2 |
| Exclude by key | not built; a `sample_id` filter on a plot lacking the column is skipped | levels 0-1, exact at the sources |
| Dataset-level step (shared T2) | not built | level 2 |
| Audit mode, chain drawing, project overview, coverage check | not built | build |
| Draft / staged lists in audit | preview filters shown in My view | none: validated step + undo |
| My view without sandbox flag | offered (ADR-085) | not offered |
| `comparison_mode_enabled` | independent flag | child of the sandbox flag |
| Export | steps, T2, T3 data | + original T1/T2, audit T1/T2, attrition table, coverage, audit keys, forked recipe |
| Filters panel | one form, one global list | same form, two actions (preview / audit step) |
| `t3_translator` | plot-private fork, appends to tier-2 | + shared late insertion, + early source insertion |

## 14. Impact of the change and what must be retested

Everything below is touched by this change and must be retested (headless suite, the full Playwright gate and the
HOME test plan items). Checked list, to re-verify before the code starts.

**Code and tests**

| Component | What changes | Existing tests to re-run (new ones in the test plan) |
|---|---|---|
| `app/handlers/home_theater.py` | strip -> Exploration, mode switch, panel dispatch, plot and table data sources, My view/Compare removed | `test_shiny_smoke`, `test_view_badge`, `test_render_every_plot`, `test_export_view_consistency`, `debug_home_theater`, `test_ui_scenarios`, `test_ui_app_features_masking` |
| `app/handlers/filter_and_audit_handlers.py` | shared filter form, two actions, new dialog, propagation replaced | `test_filter_operators`, smoke filter tests (new data-oracle suite) |
| `app/handlers/audit_stack.py` | step list, statuses, delete/undo/revert, no draft | `test_session_manager` (gatekeeper), smoke `TestAuditGate` |
| `app/modules/t3_audit_engine.py`, `view_badge.py` | filter apply, labels, skip rule, badge texts | `test_filter_operators`, `test_view_badge` |
| `app/modules/session_manager.py`, `session_handlers.py` | steps carry kind/reach/level/initials; old per-plot nodes map to level 3 | `test_session_manager`, `test_legacy_formats`, `test_write_t3_ghost_warning`, `debug_session_flow` |
| `app/modules/orchestrator.py`, `cache_keys.py` | audit overlay, separate audit cache, chained keys, no unused-ingredient builds | `test_cache_chain`, `test_tier2_store`, `test_anchor_determinism`, `test_data_analysis_recipe_data_check`, `test_retest_data_analysis_recipes` |
| `app/handlers/export_handlers.py`, `app/modules/exporter.py` | originals + audit data, attrition, coverage, audit keys, refusal on broken steps | `test_export_download`, `test_export_view_consistency`, `test_export_provenance` |
| `app/modules/bundle_importer.py`, `libs/blueprint_arch/.../t3_translator.py` | steps with levels, forked recipe modes, verification legs | `test_bundle_importer`, `libs/blueprint_arch/tests/test_t3_translator.py` |
| `app/src/server.py`, `app/src/ui.py`, `app/src/bootloader.py`, `sidebar_registry.py`, `app_features_validator.py`, `config/app_features/*.yaml` (8 files), `config/ui/sidebars/home_standard_right.yaml` | audit mode gate; **new validator rules**: comparison requires sandbox, sandbox requires the `audit_stack` slot (`pipeline-exploration-simple`: comparison on, sandbox off, must change); the `audit_stack` slot gets the new content | `test_every_app_features_starts`, `test_app_features_validator`, `test_ui_app_features_masking`, import check |
| Blueprint (`blueprint_handlers.py`, `wrangle_studio.py`), `data_import_handlers.py` | none by design, but they call the orchestrator | smoke Blueprint tests, import tests |
| VizFactory | clear message for a plot broken by a drop (#59) | viz_factory tests |
| `app/modules/session_manager.py` `extract_primary_keys` | replaced by the key mapping (declared keys + join steps), issue #61 | new test on the shipped recipe with the real `ConfigManager` |
| Naming debt | the flag `t3_sandbox_enabled`, `t3_steps.yaml`, `T3_data_<plot>.tsv`, ghost `t3_*.json`, `t3_audit_engine.py` keep their names (a rename is a separate task using the `renamed_keys` mechanism) | n/a |

**Rules, knowledge, docs (text to rewrite when built)**

`ui_implementation_contract.md` (tier toggle, gatekeeper, section 12 audit trace), `rules_ui_dashboard.md`
(sections 1-2: T3 scope, gatekeeper), `rules_app_features_flags.md` (Group B cascade), `rules_data_engine.md`
(section 1 lifecycle: audit stages), `rules_app_structure.md`, `rules_verification_testing.md` (new suite),
`app_features_traceability_matrix.md`, `project_conventions.md`, `.claude/design/` maps (`ui_panel_map_current`,
`ui_reachability_map`, `functionality_dependency_map`, `app_features_capability_matrix`,
`app_features_scoping_guide`, `export_specification`, `design_t3_export_threading`, `reproducible_export_design`),
`app/src/help/home.md`, `app/README.md`, user guide (`system_transparency`, `audit_pipeline`, `reproducible_plots`,
`understanding_your_export`), `docs/appendix/FAQ.qmd`, `docs/appendix/data_lifecycle_theater.qmd`,
`docs/workflows/ui_app_features.qmd`, `docs/user_guide/glossary_and_feedback.qmd` (add data schema, join, table; there is no
definition of collection or table in the documentation today), `docs/appendix/Standards_yaml.qmd` and
`docs/foundations/data_contracts_adr.qmd` (`is_primary_key`: today "informational" and "unique identifier"; the
audit now uses it, and in long format it repeats), `project_conventions.md` (vocabulary), a short "good recipe
practice" page (section 7.8), the HOME test plan items about My view and Compare, ADRs 024, 044, 049, 085, 086,
089, 097, 098 (amendment notes), UML (below).

**Older UML elements that describe today's behaviour (kept as built, replaced when the change is built)**

`UC-HOME` use cases "My view: filter and hide columns, sandbox", "Compare Result and My view", "Apply audit steps",
"Send a filter or drop to audit" (new planned use cases are added); `SEQ-AUDIT`; `COM-REACTIVE` (tier_toggle,
applied_filters, audit_pending); `C4-COMP-HOME`; `STM-STAGE` (gains an audit-stage companion); `SEQ-EXPORT`;
`UI-HOME The screen as built today` (kept deliberately).

## 15. Edge cases (each needs a test)

bad sample in no plot's column; present in some collections only (coverage check); key absent in a dataset;
reference table without a key; left joins where only some ingredients are excluded; the same file read as two
ingredients; key on a secondary column; key renamed in tier-1 (refusal); key cast to String in tier-1; a tier-1
step that aggregates across samples (synthetic recipe); exclusion then undo; two exclusions; remove a step in the
middle; revert to step N; broken step after another step's drop; exclusion plus a plot filter on the same column;
plot on an aggregate (no key column in its frame, reach "only this plot"); two plots on one collection (level 2 vs
level 3); a plot left with zero rows; a drop of a used column; a drop of an unused column; recipe switch with
steps; session restore against a changed recipe; export after a level 0 step (attrition, coverage, forked recipe
re-runs to the same result); huge data (warning); cache depth reached; missing audit cache entry (recompute); trial
computation then Cancel; Remove all steps returns to the originals; stage keys contain the upstream key; comparison
flag on and sandbox off (validator refuses); a recipe without any join (`3_test_no_joins`) with a declared key; a
data schema with no declared key; a join on a column that is not declared as a key; recomputation that fails (Apply is
atomic); a step that leaves a plot with zero rows; a pasted list of thousands of IDs; the plot checklist with many plots.

## 16. Decided and open

**Decided (Eve):** one rule and vocabulary (sections 1-2); reach (selector, plain-word labels, nothing
preselected) and stage (from the kind) instead of levels; numbering 0-3; early insertion at the sources, inside each
reached collection; no draft; the Filters form is shared with two actions; audit mode, button, Pipeline Audit panel
and dialogs gated by the sandbox flag; audit mode reuses the left Filters panel, the centre plot components and
the existing right Audit panel (a dialog replaces the propagation dialog); Apply and Cancel in the dialog; Compare
as an on/off toggle; mode switch at the left of the group-tabs row; separate audit cache with chained keys,
canonical hash, N = 5 by default as a setting, recompute when missing; delete = recompute without it; Undo last,
Revert to step N, Remove all; broken steps block the export; drop policy; project overview and coverage check;
optional initials on each step.

**Confirmed by Eve in the review:** "remove samples" on a plot reach is a level 3 row filter on the key column;
`comparison_mode_enabled` becomes a child of the sandbox flag and the validator gets the two new rules; filter values
come from the data, not from the plots.

**Proposed in the review, to confirm [confirm]:** value filters and drops are never early (section 5); the reach
selector with three options and a plot checklist (section 5); the key mapping from `is_primary_key` plus the join
steps, and the no-key fallback (section 7.4); the audit table stage selector; the trial computation for the impact
numbers; the event log; atomic Apply; legacy step types kept as they are; names with `t3` kept.

**Open:**
1. Exact wording of the reach options and kinds (draft in section 17, to review together).
2. Manual key mapping by the user (not in the first version).
3. Excluding by a secondary key (Gene) in a later version.
4. Where the project overview opens (dialog or wide accordion under the table).
5. What stays of the existing right panel: the "Inherited (Tier 2)" nodes, the filter inventory, the pending badge.
5b. Where the reach selector sits: in the dialog (proposed) or in the Filters panel (section 5).
6. The importer's verification legs with levels 0-2 (section 11).

## 17. Wording to review together (draft v3)

Kinds (what the user sees): "Remove samples (by ID)" | "Keep or remove rows by a value" | "Remove a column".
Reach (selector, nothing preselected; each option lists its plots and their number):
- "Selected plots" (a checklist of the plots of the recipe, grouped by tab; the open plot is marked)
- "All plots that use the same table as this plot" (N plots: names)
- "Every plot in the project" (N plots)

Under the selector, always: the lineage chain with the changed stages in bold and colour, the plots affected, rows
before/after. One-line advice: "Use the smallest choice that fits." Open wording questions: is "table" understood
(the data table behind the plot) or better "data set"/"data"? Is "Every plot in the project" clear when some plots
do not contain the sample? (the dialog then says "N plots contain it, M do not").
