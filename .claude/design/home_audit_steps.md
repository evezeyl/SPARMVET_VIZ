# HOME: audit steps and audit mode

**Read `home_audit_reading_guide.md` first (the map, the questions to decide, the status of the diagrams).**
**Status:** 2026-11-11, version 4, after the full consistency review with Eve (history: git commits 5b59a4a, e5ae922,
069052b). Companion: `home_preview_filters.md`. Decision record: ADR-099 (`architecture_decisions.md`). Section 18 is the review as a scientist and as a data
scientist (findings, evidence, remedies); section 19 is the software's role and the guard rails (issue #64); section 20 is the review as the software developer
(architecture, how the information reaches the user, what changed). Nothing here is code yet. Marks: **[built]**, **[to build]**, **[confirm]** = my proposal from the review, Eve to confirm before code.

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
| **Lineage** | The path of the data of one plot: sources -> the ingredients -> the collection's T1 -> its T2 -> the plot (T3), in its original and its audit version. A collection is the node that several plots can share; a plot has one lineage, and a collection is reached by the lineages of all the plots that read it. |
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
- **One candidate step at a time, previewed before it is applied (decided 2026-11-12, Eve, P3).** The dialog "New audit step" is modal: one candidate; changing it replaces the preview; Cancel or closing discards it; Apply with a reason adopts the computed preview (a cache hit). The cache keeps at most one trial entry besides the real states. There is no staged list and no preview in the panel; the plots change only at Apply. Undo last, Revert to step N and Remove all stay. Large data: the dialog may show counts only (the "estimate only" option of 6.5); Eve does not expect data large enough to need it.
- **Columns follow the same logic as filters (decided 2026-11-12, Eve, P3).** In audit mode there is no separate permanent control that hides columns. Dropping a column is a candidate step: the dialog previews the audit table without the column (view only), lists the plots and steps that would break, and Apply with a reason makes it a step; Cancel changes nothing.
- **The Filters panel and the column control follow the mode, automatically (decided 2026-11-12, Eve, P3).** Exploration: the form says "Add to preview", columns are those of the stage you look at, the column control hides columns in the table. Audit mode: the form says "Create audit step", columns are those of the audit table of the selected plot (their names can differ from Raw), the column control is "drop column" (a step). Each mode keeps its own state; the preview lists are **hidden** in audit mode (kept, shown again in Exploration).
- **Notice while audit mode is on (decided 2026-11-12, Eve; to build):** "Audit mode: each step changes the audited plot and the data, needs a reason, is recorded and is exported. The Result plot stays unchanged for comparison."
- **Compare** is an on/off toggle inside audit mode. **Decided 2026-11-12 (Eve, P1):** audit mode requires the flags `comparison_mode_enabled`, `session_management_enabled` and `export_enabled` (the validator's Rule 6 stays); with the toggle off the audited plot uses the full width.
- **The user can see every stage of the data (decided 2026-11-12, Eve, P7; corrects the earlier "read-only, no filters").** The audit tables **audit T1, audit T2 and audit T3 (when it exists)** can be shown, so the user can check where a sample was removed, and **the original (immutable) T1, T2 and T3** can be shown too. The filters and column drops of audit mode **apply to the audit table being shown** (it is the table the user looks at: its columns are offered and it is the default place of the step, `5a` points 2 and 6); **only the original tables are never changed**. **Open design questions:** (1) the form of the control (one selector, two controls stage x version, or tick boxes to show several tables); (2) what T3 is and whether the recipe can define it.
- **Lineage map [confirm]:** a button "Show the lineage map" (in the dialog and in the right panel) opens a read-only
  map of the plot's lineage: sources, ingredients and their tier-1 steps, the join and how it joins, the tier-2
  steps, the plot; steps in plain words; steps that compute population statistics flagged; the audit steps overlaid;
  the nodes the step being made would change highlighted. The user may not know how the recipe is built, so this is how
  they understand it before deciding. **How it avoids overlapping Blueprint (checked in the code and the rules):**
  - *Layers:* no problem. `BlueprintMapper` and `build_plot_lineage` are pure library code (no Shiny; HOME already
    imports `blueprint_arch`, for example in `export_handlers.py`); Tier 3 (`app/`) may import any library.
  - *Rendering:* the Blueprint map is Blueprint's own panel (`blueprint_tubemap_ui`, gated by `blueprint_enabled`).
    The cross-panel rule (CLAUDE.md section 8, rule 4) forbids HOME from mounting it. HOME has **its own read-only
    renderer** in its own dialog, gated by the sandbox flag. First version: a plain layered list (HTML), no graph
    library; the vendored Cytoscape stays an option.
  - *One source of truth:* the structure comes from the shared lineage code (`build_plot_lineage`, extended if needed);
    the plain-language text comes from the action catalogue that the app injects at startup (`schema_registry`, the
    descriptions every action already has); the "population statistics" flags come from the guard-rail registry in
    `app/` (the library cannot import `transformer`). Blueprint is not modified, so the two maps cannot drift.
  - *No handoff:* no "edit this step" button (user-space independence); the text points to Blueprint for recipe changes.
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

## 5. Where a step goes (decided 2026-11-12, Eve, P5)

### 5a. The decided design

1. **An audit is every change the user makes, with a recorded reason.** Preview is not an audit (it changes nothing). The audit is **the original recipe plus audit steps inserted at chosen places of its dataflow** (the forked recipe, ADR-097/099); the user's recipe files are never edited. Running the original recipe gives the original tables, running the audit recipe gives the audited ones.
2. **A step is an operation on the data, not on a plot:** *what* (remove entities by key | filter rows by value | drop a column), *where* (a node of the dataflow: a dataset, a table at T1, a table at T2, or a plot's own table at T3) and a *reason*. Its effect is everything downstream of that node, shown before Apply.
3. **Removing a key** (for example `sample_id`) is offered **from all tables that have the key in one action** (the default; for a poor sample that must be re-run) or from chosen ones. The dialog lists where it cut and where the key does not exist.
4. **Scope by tick boxes.** The user ticks the results (plots) that must change, all ticked by default. The software places the step **at the earliest point inside each ticked table that reaches no unticked plot**; where a table is shared with an unticked plot it places the step **later, at the plot's own table**, and says so. There is no pinning: the original plots (the immutable Result, the Compare reference, the original plots in the export) are the evidence of why data was removed.
5. **A step on a plot's own table (T3) is a real step**, recorded and exported (for example a category with too few observations to be meaningful in this plot). **There is no hiding in audit mode.**
6. **Value filters and column drops follow the same logic**, on the table the user looks at; **all downstream effects are shown** before Apply (a filter before an aggregation changes every later number computed from those rows); the **reason** records why it was done here and not there.
7. **What the user is shown** (four layers): (1) the results with tick boxes, grouped by tab; (2) one plain sentence per result on the data behind it (from the lineage and the table's description; what one row is; which other plots share it); (3) what will happen to each plot as the user ticks (changed at the source | changed at this plot only | unchanged); (4) the lineage chain on request, a read-only plain layered list (per node: name, description, steps in plain words, a verdict per step, key present, rows and samples, shared plots; the user's step marked where it sits).
8. **What the software must know** (the recipe graph, D1, a prerequisite built first): per table the datasets feeding it, the reaction of each step to a missing sample **relative to the key** (declared properties in the action registry refined by parameters; Polars' optimizer used as a test of those declarations, since "pushed down" proves a step is safe and "refused" proves nothing), join types and which inputs carry the key, key presence at each stage, population-dependent steps, and which plots share each table. The dialog also **compares the result of removing early and removing after** on the real data and reports whether it is the same.
9. **Names (decided):** every element (recipe `info:`, group, plot, table, dataset) has `label` (short name) and `description` (one or two sentences: what it is and what one row is). `info` on plots, datasets and tables and `display_name` in the recipe's `info:` are old names: a validator warning first, a refusal later (the "renamed to" rule). The recipe's top-level `info:` block and a plot's `title` (the title drawn on the figure) stay. The recipe validator gives an **advice** (never a block) for a plotted table without a description.

Evidence and the measurements behind these points: `home_evidence/home_where_to_remove_data_science_2026-11-12.md`.

### 5b. Earlier text, kept for history until this file is rewritten

> **SUPERSEDED IN PART (2026-11-12, Eve, P5):** the three reach options, the levels 0-3 and "value filters are never inserted early" below are replaced by 5a. The parts about stage order, early insertion at the sources inside each reached table, and the notes on key families still describe the intended engine behaviour.

#### Earlier section 5 (history)

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
options with a checklist, instead of four options ("only this plot" and "these plots" merged). **Decided (Eve):** the reach
selector sits in the "New audit step" dialog (everything to read and decide is in one place, and Apply stays
disabled until a reach is chosen).

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
- **A hint under the selector depends on the kind:** for "Remove samples" because of bad quality: "Usually every
  plot in the project"; for a value filter: "Use the smallest choice that fits". The hint never preselects.
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
4. **Key mapping.** Read **directly from the loaded recipe dictionaries** (`raw_config`), so no transformation of the
   recipe is needed; the reader handles tiered steps (`tier1`/`tier2` lists) and legacy lists. Built once per recipe
   from (a) the **declared keys**: every input field with
   `is_primary_key: true` in a data schema (an existing, documented property of the data contract), and (b) the
   **join steps** (`action: join`, `on` as a string or a list, `left_on`/`right_on`), which link differently named
   columns into one key family and flag a join on a column that is not declared (a warning for the recipe author).
   A collection that is a join takes the keys of its ingredients. A **data schema used directly** (a recipe without
   any join, such as `3_test_no_joins`) has its declared key and needs no join, so removing samples by ID works there
   too. `is_primary_key` is optional and often absent: a data schema with no declared key whose column is used in a join is
   given that column as an **inferred key** (shown as "inferred" in the dialog and in the project overview, with a
   note for the recipe author). A data schema with **no declared key and no join** has no key: reported "no key declared"; for it, "Remove
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
- **Export contents in audit mode (decided 2026-11-12, Eve, P4b).** One bundle. Publication part: the audited plots; for each plot **affected by a step** also the original Result plot, in separate folders and clearly labelled "original, no audit" (an unaffected plot is included once, noted "not affected by any audit step"); the original T1/T2 labelled `original_`; the audit T1/T2/T3 only where a step changed something (audit T1 only if an early step exists), each naming the original it comes from by name and hash; the steps with reasons, the event log, the attrition table, the coverage check, the acknowledged warnings, the generated Methods text, the pre-export review. `effective_run.yaml` as in ADR-097 plus the audit keys. **One tick box "include recipe and raw data"**, off by default, with the sensitive-data warning: it adds only the recipe (in audit mode the forked recipe) and the raw data files, together, to the same zip. The plots, audited and original, are always in the publication part above; the tick adds none (unchanged from ADR-097). Sharing is the user's responsibility. Developer check kept: for an unaffected plot the original and audited renders must be identical.
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
| NEW `app/modules/recipe_graph.py`, `audit_events.py` (event log), `audit_compiler.py` (step compiler), `audit_policy.py` | recipe graph (D1), event-sourced log (D2), compiler (D3), policy (D7) | property tests (D9) and golden tests on every shipped recipe |
| NEW `app/modules/audit_guard_rails.py` (pure functions, the registry of section 19) | checks, levels, messages, help anchors | one test per check with a mutation check; test that the dialog, help and export list the same ids |
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
`app/src/help/home.md` (and the help of the audit filters), `app/README.md`, a new page "Before you audit", user guide (`system_transparency`, `audit_pipeline`, `reproducible_plots`,
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
flag on and sandbox off (validator refuses); a warning acknowledged, and an override with its reason, stored and exported; a step with a warning but no override reason (refused); NA rows with each operator; a recipe without any join (`3_test_no_joins`) with a declared key; a
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

**Decided (Eve, later in the review):** the reach selector sits in the dialog; the key mapping is read from the loaded
dictionaries; `is_primary_key` is optional (inference as fallback); all three items I had forgotten (atomic Apply, event
log, recipe documentation) are accepted.

**Decided (Eve, 2026-11-11, section 19):** the principle (inform, warn, let the user decide; a risky choice needs a recorded
reason; block only technical problems); the four levels; the NA rule (never silent); a guard-rail registry; the review
findings documented in issue #64; the problems and the principle go into the documentation and the help.
**To confirm [confirm]:** the changes D1-D14 of section 20 (recipe graph, event-sourced log, step compiler, three-step
dialog with an effect preview, pre-export review gate, policy configuration, `hypothesis`, build order), the first list of
checks and their levels (section 19), the thresholds (20 %, 3 entities), the
reason categories, the optional caption (off by default), the lineage map.

**Open:**
1. Exact wording of the reach options and kinds (draft in section 17, to review together).
2. Manual key mapping by the user (not in the first version).
3. Excluding by a secondary key (Gene) in a later version.
4. Where the project overview opens (dialog or wide accordion under the table).
5. What stays of the existing right panel: the "Inherited (Tier 2)" nodes, the filter inventory, the pending badge.
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

## 18. Review as a scientist and as a data scientist (2026-11-11)

**Verdict.** The structure (original data never changed, steps with reasons, recompute and cache, coverage and
overview) is sound, but the audit **cannot yet be trusted for publication figures**. Tests of the current filter engine
and a review of the design found the flaws below. "Verified" = run on the real code, "reasoned" = follows from the
design or the data; a reasoned item still needs a test. Background: ARRIVE and CONSORT require exclusions and
attrition to be reported with their reasons
([ARRIVE 3b](https://arriveguidelines.org/arrive-guidelines/inclusion-and-exclusion-criteria/3b/explanation));
flexible analysis choices made after seeing data inflate false positives
([Simmons, Nelson, Simonsohn 2011](https://www.bitss.org/education/mooc-parent-page/week-2-publication-bias/is-there-a-credibility-crisis/false-positive-psychology-2/)).

| # | Flaw | Evidence | Remedy in the design | Status |
|---|---|---|---|---|
| 1 | **Integer thresholds are truncated**: `v >= 90.5` keeps 90, `v < 90.5` drops 90, `v = 90.5` keeps 90 | verified; same code twice (`t3_audit_engine.py`, `viz_factory.py`) | one implementation, correct rounding by operator; tests | issue #62, independent of the redesign |
| 2 | **Missing values vanish silently**: "remove Norway" (`!=`, none-of) also drops rows with no country; NaN is kept by `>=` and dropped by `<` | verified; Polars drops null predicates ([docs](https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.filter.html)) | an explicit rule in every step: missing values kept or removed (safe default for "remove": keep), shown in the dialog with the count, part of the step record and its hash | issue #63, needs Eve's default |
| 3 | **Rows are not samples**: in long format a filter can remove every row of a sample, the sample disappears and the denominator changes ("absent" instead of "zero") | verified (a sample with no row at identity >= 90 vanished) | the dialog, the attrition table and the project overview count **entities (by key) as well as rows**, and list entities that lose all their rows | reasoned design; to build |
| 4 | **Key matching is exact**: removing `S2` leaves `' S2'` and `'s2'`; an early step sits **before** tier-1 normalisation (strip, case) | verified for the filter; reasoned for the sources | values are offered from the **T1** of the reached collections (what the recipe's joins see); after every key exclusion a **post-condition check** verifies that the excluded values (and look-alike variants) are absent from every reached audit T1 and T2; if not, the step is "incomplete" (red) and blocks the export | to build |
| 5 | **Removal after a computed statistic is contaminated**: z-scores, percentiles, ranks, top-N, pivots and summaries computed over all samples still contain the removed samples if the removal is applied later (plot level, T2) | reasoned; the actions exist: `z_score`, `percentile`, `window_agg`, `cum_sum`, `cum_count`, `value_counts`, `describe_stats`, `top_n_other`, `pivot`, `derive_categories`, `summarize`, `count_by_group` (checked in the registry); none is cross-sample in the ST22 recipe | the dialog scans the collection's steps and **warns** when samples are removed at plot or T2 level downstream of such a step, and recommends "this table" or "every plot" (removal before the computation) | to build |
| 6 | **Tables end with different sample sets**: only a coverage check on the excluded IDs, no view of which entities each table holds | reasoned | the project overview adds a **sample census**: entities per table before/after, and entities present in some tables but not others | to build |
| 7 | **Researcher degrees of freedom**: exclusions made after seeing the result cannot be prevented | external evidence, above | a **reason category** (technical failure, contamination, duplicate, out of scope, outlier by value, other) plus free text; the **event log** keeps steps that were made and removed; the report says which exclusions are "outlier by value" and prints the attrition (rows and entities, per step, ARRIVE/CONSORT style); an optional figure caption "n = X after exclusions (see audit trail)" **[confirm]** | to build |
| 8 | **Redundant or contradictory steps**: a step that changes nothing (already removed by another) looks "applied"; two filters can leave no rows | reasoned | status **"no effect (already done by step N)"**; zero rows warn before Apply | to build |
| 9 | **Exported data must be what the plot used**: today's test covers the T3 path only | reasoned | tests: the forked recipe re-run headlessly must give the same data hash as the audit stages; a new "audit data hash" leg in the importer; at export, entity and row counts of the exported frame must equal those of the rendered plot | to build |
| 10 | **Hash and cache robustness**: the canonical form of the operation list, partial writes, two sessions writing the same file | reasoned | canonical JSON (sorted keys, typed numbers, normalised strings, a format version and the engine version); write to a temporary file and rename; the key is checked on read | to build |
| 11 | **A table step cannot be limited to one plot**: a T1 or T2 step changes every plot that reads the table. Example: `MLST_with_metadata` is read by `mlst_bar` and `year_distribution`; a T1 step with "only mlst_bar" would also change `year_distribution` | verified in the recipe | see "Stage and reach" below | **[confirm]** |
| 12 | **Compare uses each plot's own axes**, which can make the audited and original plots look alike or unlike for the wrong reason | reasoned | option "same axes" in Compare | low priority |
| 13 | Steps tied to a data version: a reused ID in new data | reasoned; the session key already contains the data batch hash (contract section 12d) | verify at implementation that steps are never carried to another batch | check |

**Stage and reach (proposed change to section 5) [confirm].** Eve's questions show that for value filters the user
works on **the table they look at** (T1, T2 or the plot), and that values must come from that table:
- **Stage = the table the user is looking at** (audit table selector: T1 | T2 | the plot). A value filter or a drop
  acts at the end of the collection's tier-1 steps (T1), after its tier-2 steps (T2), or on the plot frame (T3).
  Columns and values come from that stage. This replaces "value filters are never early": a filter on T1 is exact
  because it acts on the T1 table the user sees (no renamed-column problem), and it is cheap (the original T1 file
  filtered, then tier-2 recomputed).
- **Reach depends on the stage**: T1 or T2 -> "this table" (all plots that read it, named) or "every table in the
  project that has the column"; plot -> "selected plots". A table step cannot be limited to some of the plots that
  read it. If the user looks at T1 or T2 and chooses a subset of plots, the dialog says: "this changes the table:
  these N plots read it [names]. Change the table, or apply to the plot level (only if the column exists in the
  plot's frame)".
- **Remove samples** (the key kind) keeps the reach choice: selected plots (level 3) | this table (sources of this
  collection) | every plot in the project (sources of all collections with the key).
- The number "levels 0-3" no longer fits (a project reach exists at T1 and at T2): the internal record becomes
  **stage** (sources, T1, T2, T3) and **reach** (plots, table, project). The old numbers stay in a conversion table
  (0 = project at T1, 1 = table at T1, 2 = table or project at T2, 3 = plots at T3). The diagrams HOME-AUDIT-LINEAGE
  and HOME-AUDIT-EFFECT are redrawn after Eve confirms this.

**What I would not trust even after these remedies:** removing samples at plot level for a table that contains
population statistics (flaw 5): the tool warns, but only the user can decide; and any audit on data whose IDs are
not clean (flaw 4): the post-condition check catches it, it does not fix it.

## 19. The software's role and the guard rails (principle decided by Eve, 2026-11-11; issue #64)

**Principle.** The software makes good data science possible and the user's informed choice easy. It does not decide
for the user: it **informs, warns and lets the user decide**. A risky choice needs a **written reason** that is
recorded and exported. The software **blocks only what is technically wrong or not reproducible**, never a scientific
judgement. What is data-science practice (not exploring data with the audit, not homogenising messy fields with it, stating exclusion criteria in advance,
reporting every exclusion) is taught in the help and the documentation: "with great power comes great
responsibility: think before you do".

**Four levels.**

| Level | What the user sees and must do | Recorded in the step and exported |
|---|---|---|
| **Info** | shown in the dialog (counts, affected plots and tables, chain), nothing to do | the numbers |
| **Warning** | shown with a plain explanation; the user ticks "I understand" before Apply | which warnings were shown and acknowledged |
| **Confirm with a reason** | a strong warning for choices that usually bias results; the user writes why it is acceptable here | the override reason, with the warning id |
| **Block** | technical only: a column or key that no longer exists, a renamed key refused, a step the forked recipe cannot represent, a failed recomputation | nothing is applied; the error is shown |

**The mechanism: a guard-rail registry.** One module of pure functions, one entry per check: `id`, trigger (kind,
stage, reach, data), level, plain-language message, help anchor, test. The checks run when the dialog opens and
whenever a choice changes, again at Apply, and after recomputation (post-conditions). The list in the dialog, the help
page and the export section are all built from the registry, so they cannot drift; adding a check is one entry and one
test. For every check the entry states whether a warning is enough or the functionality must change, which is the
decision Eve asked to make explicit.

**Software correctness (must simply be right, with tests; not guard rails):** integer thresholds (#62); the NA rule
below (#63); one filter implementation shared by the preview, the audit and VizFactory; the canonical hash; atomic
cache writes; the export self-checks; the post-condition check itself.

**The NA rule (decided: never silent).** Missing values are a visible, selectable value ("NA (missing)") in every
value list. "Remove" filters keep rows with NA unless NA is selected; "keep" filters remove them unless NA is
selected; for comparisons (>, <, between) rows with NA are removed unless the user ticks "keep rows with NA". The
dialog always says "N rows have no value in this column: they are kept / removed". NaN follows the same rule.
**Confirmed 2026-11-12 (Eve, P6), with the reason:** a missing value can mean very different things in the datasets of a pipeline (the software did not find the value in its database; the software failed and the sample must be rerun; the sample quality was insufficient). The software cannot know which, so it never removes or keeps them silently: they stay visible, and the user (and, before, the recipe maker) decides how to treat them. In an audit step the user chooses and the reason records why; in Exploration the user chooses whether to look at those rows or not (the same "NA (missing)" value in the filter).

**Checks (first list; extend as problems are found).**

| Id | Check | Level | Why |
|---|---|---|---|
| I1 | rows and **entities** before/after; entities that lose all their rows; NA rows touched | info | rows are not samples (flaw 3) |
| I2 | tables and plots that change, with names; a table step cannot be limited to some plots | info | flaw 11 |
| I3 | sample census per table; entities present in some tables only | info | flaw 6 |
| W1 | large attrition (default more than 20 % of rows or entities; a setting) | warning | flaw 12 |
| W2 | a plot loses a whole level of its x, fill or facet variable | warning | flaw 12 |
| W3 | a group left with fewer than 3 entities | warning | flaw 12 |
| W4 | drop of a column used by plots, steps or as a key (#59) | warning | #59 |
| W5 | the step has no effect (already done by step N); a plot is left with zero rows | warning | flaw 8 |
| C1 | samples removed at plot or T2 level **downstream of population statistics** (`z_score`, `percentile`, `window_agg`, `cum_sum`, `cum_count`, `value_counts`, `describe_stats`, `top_n_other`, `pivot`, `derive_categories`, `summarize`, `count_by_group`) | confirm with reason | flaw 5 |
| C2 | the filter acts on the **variable the plot shows** ("outlier by value"): selection on the outcome | confirm with reason | flaw 7 |
| C3 | **incomplete exclusion**: after the step the excluded values, or look-alikes (`' S2'`, `'s2'`), are still in a reached table | confirm with reason | flaw 4 |
| B1 | a column or key used by a step no longer exists (status broken); a key renamed in tier-1; a step the forked recipe cannot represent; the recomputation failed | block | technical |

**Reason (decided 2026-11-12, Eve, P7; replaces the fixed category list).** The software is **data-agnostic**: it will be used for datasets other than bioinformatics, so there is **no fixed list of categories**. The reason is **free text, required, and must be a good justification**. The help suggests a convention that keeps it clean and lets the vocabulary grow at no cost: a hashtag with a short category, then the explanation, for example `#technical failure: sequencing run bad` or `#technical failure: instrument calibration failed`, with good examples from several fields. **Accepted on top (Eve, if the cost is small):** the dialog offers the tags already used in the project as suggestions. **Deferred:** grouping the report by tag (Eve: beyond what we settle now; the report content is a separate matter). The check C2 (the filter acts on the variable the plot shows, i.e. selection on the outcome) is **data-based**, not category-based, so it does not need the category. The report prints the attrition (rows and entities, per step) and lists every acknowledged warning and override reason.

**Figure caption (decided 2026-11-12, Eve, P7; replaces the optional setting).** The caption of each figure **in the report text** (never drawn on the figure itself) states the count after exclusions, for example "n = 38 samples after exclusions (4 excluded; see audit trail)". It is **on by default**: the software is transparent, and the user can delete the line in the report. It exists only where an audit exists (with Audit mode; an Exploration-only export has no exclusions to state). The count is of **entities by key**, not rows. **Data-agnostic:** the word for the entity ("samples", "patients", "sites") comes **from the recipe** (the label of the key column; fallback "entities"), never from the code. Proposed (Eve may veto): a figure that no audit step affects says "no audit step affects this figure" so the caption is always present when an audit exists.


**Documentation and help.** A page "Before you audit" and the help of the audit filters: the problems above in plain
words with an example each, the prior art (ARRIVE, CONSORT, Simmons et al. 2011), the principle, and the advice to use
the lowest reach that fits. The check messages come from the registry.

## 20. Review as the software developer (2026-11-11)

**Question.** Does the logic we have make sure the user has the information needed and takes good decisions? **Answer.**
The *rules* (what the system must do) are good. The *architecture* behind them was not yet good enough: the same
recipe analysis was needed by seven features and would have been written seven times, the audit trail lived in two
places, information came in one overloaded dialog, and the strongest check was missing at the point of no return (the
export). The changes below fix that. What remains risky is human (wording, warning fatigue) and can only be tested with
real users.

**What holds (keep):** original data never changed; recompute, never copy; chained keys and the canonical hash; atomic
Apply; stage and reach; the NA rule; the four levels (info, warning, confirm with a reason, block); the guard-rail
registry as the single source of messages; the rule that only technical problems block.

**Evidence for the biggest human risk (warning fatigue).** In clinical decision support, 46-96 % of alerts are
overridden ([Poly et al. 2020](https://medinform.jmir.org/2020/7/e15653/PDF)); tailoring alerts to the user's role was
the most successful remedy ([Hussain et al. 2019](https://psnet.ahrq.gov/issue/medication-safety-alert-fatigue-may-be-reduced-interaction-design-and-clinical-role-tailoring)).
Attention to repeated warnings falls over time and recovers when the warning's appearance changes
([Vance et al. 2018](https://misq.org/tuning-out-security-warnings-a-longitudinal-examination-of-habituation-through-fmri-eye-tracking-and-field-experiments.html)).
So: few, specific, rare warnings; a different look for each level; the strongest review where it matters.

**Changes (D1-D14); [confirm] = Eve to confirm before code.**

| # | Change | Why (what was not good enough) | Effect on the design |
|---|---|---|---|
| D1 | **One recipe graph** (`recipe_graph`, pure, built once per recipe from `raw_config`): data schemas, ingredient steps, joins, tier steps, plots, key families, the columns available at each stage, the columns each plot uses, flags for population-statistic steps. Everything below is a **query** on it | key mapping (#61), concerned plots (#58), used-by-plot (#59), impact preview, lineage map and checks C1, W2, W4 each needed their own parsing of the recipe: duplicated logic gives inconsistent answers, and the first of them (`extract_primary_keys`) is already wrong | new component; tested against every shipped recipe; sections 6, 7.4, 9 and 19 use it |
| D2 | **Event-sourced log**: only append-only events are stored (step created, removed, reverted, warning acknowledged, override written); the step list is derived from them. Undo is a new event | "step list + separate event log" (sections 10-11) can disagree; the log is also what the report needs (steps made and removed, acknowledgements) | one store; session, export and history come from it |
| D3 | **Step compiler**: a step compiles to a list of the **existing registered recipe actions** (the translator already does this for plot steps); that one output is hashed, executed, exported as the forked recipe, used to highlight the lineage map and to compute the impact | "one code path" was stated, not structured | one module; golden tests per step kind; new NA-aware actions with #63 |
| D4 | **Three-step dialog with an effect preview** (not a draft list): 1 *What* (kind, reach, values), 2 *Check* (rows and entities before/after, findings sorted by level, the lineage map, a **before/after preview of the open plot** from the trial computation), 3 *Why* (reason category and text, acknowledgements, Apply) | one dialog with everything is overload; the best information is to **show the effect**, not only describe it; the stepwise order also gives the pause Eve asked for | dialog text, flow diagram and wireframe updated |
| D5 | **Pre-export review gate**: before an export the user sees a generated plain-language methods paragraph, the attrition table, every acknowledged warning and override, and any broken or incomplete step, and attests | the strongest check belongs at the point of no return; it lets the step-time dialog ask for fewer confirmations (less fatigue) | new screen before the export; the paragraph goes into the report |
| D6 | **Few, specific, rare warnings** | evidence above | every check must carry a number or a name, offer the alternative, fire rarely; one distinct look per level; confirm-with-reason only for C1-C3; thresholds tested with users |
| D7 | **Policy in configuration** (`audit_policy` in the deployment or the app features): attrition threshold, minimum group size, reason categories, minimum reason length, whether initials are required, whether the confirm-level checks may be overridden | different labs, different rules; keeps "the user decides" at the right level; defaults safe | one config block, validated at startup like the flags |
| D8 | **Honest checks**: guard rails are heuristics (a `mutate` expression such as `x / x.sum()` hides a population statistic from an action-name scan). The scan also reads `mutate` expressions for aggregations; a clean result says "no issue found by checks A, B, C", never "safe"; the lineage map lists every step so a person can look | false assurance is worse than no check | wording; a "what the audit guarantees and what it does not" page |
| D9 | **Executable guarantees (property tests)**: audit with no steps equals the original (same hash); a step applied twice equals once; row steps commute within a stage; undo restores the earlier hash; the original files never change; trial equals apply; the exported recipe re-run equals the audit data; the key changes if and only if the operations change; the result equals an independent reference implementation on random frames with nulls, NaN, whitespace and case. Property-based testing with `hypothesis` **[confirm: new dev dependency]** | the design claims properties; they must be executable | new test suite, listed in section 14 |
| D10 | **Persistent awareness**: "N audit steps active" in Exploration, in the plot header and in the export metadata; a plot made with audit steps says so | nobody should mistake an audited plot for the original, or forget steps exist | badge texts |
| D11 | **Quick path for the common job** (remove a bad sample): an entry in the Filters panel that opens the dialog at step 1 with the kind chosen; the reach stays unselected | most use is one job; the full dialog should not be needed to find it | one button |
| D12 | **Background computation with progress and cancel** (Shiny extended task, to check against the installed Shiny version); Apply is disabled while it runs; the existing "recalculating" overlay stays | recomputation can be slow; the page must not freeze | atomic Apply unchanged |
| D13 | **Format versions**: `schema_version` on events and exports; sessions of the old model are migrated by a mapping (section 4) | the format will change again | one field and a migration test |
| D14 | **Build order** (each stage shippable and tested headless; the UI last): (1) engine bugs #62, #63 and one shared filter implementation; (2) recipe graph and key mapping (#61); (3) event log, step compiler, audit cache, without a UI; (4) guard-rail registry and tests; (5) the dialog, the panel and the lineage map; (6) export, importer and the review gate; (7) documentation and help | the risky logic is testable without a browser; a UI built on untested logic is where wrong figures come from | build plan for #60 |

**A usability check before the wording is final:** let two or three scientists who did not write the design use the
dialog on the ST22 recipe (think-aloud), with the real warning texts. The wording of the reach options and of C1-C3 is
decided after that, not before.

**Verdict after the changes.** Good enough to build, in the order of D14. The two things no design removes: users who
click through warnings (reduced by D4-D6, caught by D5), and recipes whose structure the checks cannot see (D8: the
lineage map and the honest wording are the answer).
