# HOME — Main Analysis Space

**Type:** User space
**Status:** core built (Exploration, filters, export, sessions); **audit mode designed and agreed 2026-11-12, not built** (ADR-099). Each statement below says whether it is **[built]** or **[target]**.
**Last updated:** 2026-11-12 (rewritten from the agreed design; the earlier version of 2026-05-05 described "audit always on" and the "T3 cascade rule", both retired)

**Where the detail is** (read in this order): `home_audit_reading_guide.md` (start here: order of work, decision register, reading list), `home_preview_filters.md` (Exploration), `home_audit_steps.md` (audit mode), ADR-098 (what is built), ADR-099 (the target), `home_evidence/home_hash_model_2026-11-12.md` (the keys), `home_evidence/home_attrition_report_2026-11-12.md` (the counts and the caption), the diagrams `UI-HOME-*`, `HOME-*`, `DM-KEYS*` (`docs/UML/diagrams/`).

---

## Purpose

HOME is where the user runs **predefined, repeatable analyses** and gets **publication-ready results**. The analysis is defined in a data analysis recipe (built in BLUEPRINT); HOME runs it and lets the user look at the data, and, in audit mode, justify and record changes.

The core values of HOME are **transparency, reproducibility and a recorded reason for every change**. The software informs, warns and lets the user decide; it blocks only what is technically wrong.

The other user spaces serve HOME: BLUEPRINT builds the recipes HOME runs, TEST_LAB prepares data, GALLERY gives examples.

**Space identity: HOME users produce results from a pipeline, and can show exactly what was done to the data behind each figure.**

---

## The words (generic; examples marked)

An **entity** is the unit a key identifies (a sample, a patient, a site, a sensor). A **key** is the column that identifies it (it repeats in long tables, so rows and entities are counted separately). An **attribute** is a descriptive column. A **population table** has one row per entity.

The data flow of a plot has three stages. **T1**: the steps applied to a dataset as described in the T1 section of the recipe (the dataset's own steps and the first steps of a join). **T2**: further processing steps applied to the result of T1, as described in the T2 section of the recipe. **T3**: the data that is passed to the plotting system.

The processing steps are split into these stages in a way that can look arbitrary. The goal is to do each logical step only once: the steps that several plots share are done in T2 (or T1), and the plots then branch from them, in T2 but mostly in T3, to obtain different figures. This is, for example, where data are reshaped from wide to long, aggregated before plotting, and where compute time is optimised. The detailed description of the tiers and of the recipe is in `docs/foundations/data_tiering_adr.qmd`, `.claude/rules/rules_data_engine.md` and `docs/appendix/data_analysis_recipe_structure.yaml`.

**Every table has all three stages, with or without a join. T2 and T3 can be empty, and empty means the same as the previous one.** The path through the stages is the **lineage**. *Example (bioinformatics test recipe): entity = sequenced sample, key = `sample_id`, attribute = country.* Full vocabulary: `home_audit_steps.md` section 2 and the user glossary.

---

## Two modes

**Exploration [built, being simplified].** For looking. The user chooses which stage of the data to look at. *Proposed, to decide (see Open Questions): T1, T2 or T3 of the open plot (T3 is the data the plot shows, the Result), instead of the earlier "Raw | Result"; "Raw" meant T1, the data after the recipe's first steps, not the original file.* **Several preview filters can be applied at the same time** (they combine, and each can be removed). A preview filter changes the data table only; it is never saved, never exported, and is cleared when the view changes. One plot is shown, the Result, immutable. Missing values are a visible, selectable value; a notice says what the preview is and is not. Detail: `home_preview_filters.md`.

**Audit mode [target]**, switched on only by the sandbox flag. The only way to change data, a plot or an export. Requires export, Compare and sessions (the user compares the effect, saves unfinished work, exports what is finished). Replaces today's "My view", "Plot to show" and the propagation dialog.

---

## Audit mode in short [target]

1. **Two kinds of step:** filter rows by a value or a list of values; drop a column. The value can be of any content type (text, number, date, true/false, missing); it is converted to the type of each column where the step is written. Every step has **one free-text reason** (a hashtag convention is suggested), is recorded, and can be removed.
2. **One mechanism for every removal.** The user picks a field; the **lineage** (followed backwards and forwards) shows every node (T1, T2, T3 of every table) where the field exists, as tick lines; all are ticked by default; the user unticks what must not change. For a node without the field the dialog suggests, never imposes, a column it shares with another node. The key is **information** (counts, suggestions, the warning that a filter on a join key may change the join), not mechanism. A drop of a column works the same way.
3. **The audit recipe** is a copy of the recipe with the audit steps added: the audit can add a filter or a drop **at any stage** (T1, T2 or T3, wherever the user ticks). It is exportable and re-runnable; the original recipe, its steps and the data are never changed, and the audit never removes a recipe step; it only adds. The audit adds only filters and drops, not transformations: it is for showing less data with a reason, and a reshaping or a recalculation cannot be justified by one reason and has to be reviewed in the recipe. The recipe maker (in BLUEPRINT) can use any action at any stage, including T3, and is responsible for good practice.
4. **Information before Apply:** the lineage backwards to the roots and forwards to every descendant; the T3 data, and therefore the plots, that would change; rows **and entities** before and after; a preview of the open plot; and the later steps that summarise rows. A read-only popup per node (own window, built so a panel can replace it later) shows what the recipe already does there.
5. **Step-by-step counts** (called the attrition table). For every step, the number of rows and of entities before and after, so that a reader sees how many were removed and where, like a flow chart of what is left. It starts from all the entities of the population table, goes through the steps of the recipe that remove rows, then through the audit steps, and counts the missing values removed. It is computed again each time from the recipe and the steps (never stored), so removing an audit step updates the numbers. It does not mean that recipe steps can be removed: they cannot. The figure caption in the report is composed from these counts, in the entity's own word (declared in the recipe).
6. **Three levels of message:** info, warning, block (technical only). Missing values are a value: "everything except x" keeps them, "only x" and comparisons remove them, always counted.
7. **Original plots stay as evidence:** the immutable Result, the Compare reference, and in the export the original plot of every plot that is really affected. A change written at T1, T2 or T3 reaches a plot only through its T3, so a plot is affected exactly when its T3 content differs.

---

## Export, import, sessions

- **Export [built in part, target extended]:** one bundle: audited plots, the original Result plot for each really affected plot, original and audit data, the steps with reasons and the event log, the exclusion table, the attrition table, the verification legs (engine, data, recipe, audit recipe, steps, record) and the key of every node; one tick adds the recipe and the raw data (with a warning about sensitive data). Exploration is never exported. The export is refused when the recipe or the data changed since the view was opened.
- **Import [target, gated]:** its own functionality, on only through the configuration and only for an authorised person; recipes normally come from a system manager. **The recipe must be valid: an invalid recipe blocks the import, with the reason.** The same recipe validation is used by HOME's load gate and by BLUEPRINT's Validate, where a recipe can be checked first; it includes a rule that formulas use only an allowed list of operations. *Proposed, to confirm:* the verification legs (engine, data, recipe, audit recipe, steps, record) are reported as match, mismatch or not checked and do not block, because a different machine or engine is not an error; but a bundle whose own files differ from the hashes it records needs an explicit acknowledgment before the import goes on. The import writes a new recipe and session, never into the live state.
- **Sessions [built, extended]:** the session holds the recipe and data references and, in audit, the step list; restoring recomputes. Audit steps of old data stay with the old session (a warning on restore).
- **Hashes:** a series of labelled parts per node (`E . rC . dC . [a1] . [s2] . [a2] . [s3] . [a3]`); whole-recipe hashes identify the project state and never decide what to rebuild; the data hash is the full content once per session.

---

## User Functionalities

| Functionality | What the user can do | Status |
|---|---|---|
| **Select data analysis recipe** | choose a recipe that passed the load gate; rejected recipes are listed with the reason | built |
| **Navigate** | analysis groups and plots | built |
| **Inspect** | the data of one stage (T1, T2 or T3, to decide), first rows, column selector (preview only), row counts, notices | built, simplified by the redesign |
| **Preview filters** | change the table to look at it; never saved | built, being rebuilt per `home_preview_filters.md` |
| **Audit** | filter or drop with the lineage and ticks, with a reason; undo, revert to a step, remove all; Compare original and audited plot | target |
| **Information** | the node popup, the lineage, the attrition table | target |
| **Export / Import** | see above | built in part / target |
| **Session** | save, restore, import, export, delete | built |
| **Load data, replace metadata** | gated ingestion panels | built, gated by flags |
| **Palette override** | deferred, not in the UI (an earlier version of this table said built; no such control exists in HOME) | deferred |

---

## Non-Goals

- HOME does not build recipes and does not edit original recipes or **plot specifications** (the graphics description for the visualisation factory: mapping, layers, theme). In audit mode it adds filter and drop steps to a **copy** of the recipe (the audit recipe, generated for the session and the export; the original files are never touched). BLUEPRINT builds recipes and plot specifications, which can become original recipes, so it operates on plot specs and on all stages of a recipe. The audit writes only data steps into the copy's T1, T2 and T3 lists; the plot spec is copied unchanged, and the T3 list sits beside the spec, not inside it, so the two cannot step on each other.
- HOME does not generate test data (TEST_LAB) or browse examples (GALLERY).
- HOME does not expose raw code to the user. Audit steps are named, parameterised actions, never formula text assembled from user values.

---

## Key Design Constraints

- **Recipe-driven:** every change comes from the recipe or from a recorded audit step; structural changes go to BLUEPRINT.
- **Original data and recipe never change** (S1); same data, recipe and steps give the same figure and export (S4); what you see is what is exported (S6).
- **Engines are declared** (`data_engine: python-polars`, `plot_engine: python-plotnine`, required, unknown = failure) so a later integration of another language is a declared choice (`home_audit_steps.md` 5a point 21).
- **Fail instead of warn:** everything written in a recipe is executed or the recipe is rejected with the reason; HOME rejects at the load gate, BLUEPRINT reports and never blocks building.
- **Data-agnostic:** no field-specific word in the code or in fixed texts; the name of the entity and the examples come from the recipe and the help (W7).
- **Positive inclusion** (ADR-071): a feature that is off is absent, not greyed; the configuration file only switches functionalities on or off, the design is the same in every configuration.
- **Gating:** audit mode needs the sandbox flag plus export, comparison and sessions; comparison needs audit; Import has its own flag. The configuration stage is last (`CONFIG-REVIEW-1`): `pipeline-static` (no interaction), `pipeline-simple-exploration` (Exploration only), `pipeline-exploration-advanced` (Exploration and audit, no Test Lab, Blueprint or Gallery), `developer` (everything).
- **Palette override is deferred** (the trial was not good enough; it is not in the UI); labels adapt automatically to plot size.

---

## Code Modules

| Code module | Role | Status |
|---|---|---|
| `home_theater.py` and its handlers (`filter_and_audit_handlers.py`, `export_handlers.py`, `session_handlers.py`, `audit_stack.py`) | the screen and its reactive wiring | built; the audit pieces are replaced when audit mode is built (`AUDIT-REPLACE-1`) |
| `t3_audit_engine.py`, `view_badge.py` | pure helpers for filters and badges | built |
| `orchestrator.py`, `cache_keys.py` | build and store T1 and T2 with their keys | built; keys per node and T3 are target (`KEYS-NODE-1`) |
| `libs/utils` recipe graph (`utils.recipe_graph`) and the shared recipe rule set (`check_recipe`) | one model of the recipe (nodes, steps, columns per node, plots), one rule set; Blueprint's navigator is rebuilt on it | target |
| audit modules in `app/modules/` (step compiler, guard-rail registry, attrition, event log, node renderer) | pure logic, tested without a screen; thin handlers on top | target |
| `wrangle_studio.py`, `ingestion_handlers.py`, `data_import_handlers.py`, `exporter.py`, `session_manager.py` | pipeline rendering, loading, import panels, export, sessions | built |

---

## Current State

Built: the pipeline and plots; Exploration with the old header strip (My view, Compare and Plot to show still exist and are replaced when audit mode is built); the filter and audit panels of the old model; export with the key check; sessions; gated ingestion. Verified defects tracked as issues: #61, #62, #63 (missing values), #65, #66, #68. Everything of audit mode in this document is **target**.
The **recipes and the tests also have to be rebuilt** to the new decisions, otherwise nothing will work as intended when HOME is rebuilt: the recipe format specification (`recipe_format_spec.md`) is being reviewed in a parallel session, and the tests are adapted first (`TEST-ADAPT-1`).

---

## Open Questions

- **The right panel in audit mode: keep it for the audit steps** (Eve, 2026-11-13). Content to confirm: the step list (kind, the nodes it is written at, field, operator, value, reason, initials, date, status), undo, revert to a step, remove all; the detail of the selected step (where it is written, the lineage chain, rows and entities before and after); the step-by-step counts. It may grow wider or longer than today. What is dropped from today's panel: the "Inherited (T2)" nodes (the recipe's own steps go to the node popup, since the audit never edits them), the pending badge and the Apply gate (there is no draft; Apply is in the dialog), the plot style panel (not mounted).
- **Which stages the user can look at (Data selector):** T1, T2, T3 of the open plot, and what "Raw" means. Recommendation: a selector T1 | T2 | T3 (T3 = Result); the original source files are the roots of the lineage and are shown in the node popup, not in the strip.
- **Import:** confirm the three classes (invalid recipe blocks; environment legs inform; a bundle that differs from its own recorded hashes needs an acknowledgment).
- **Filter on any content type:** today the filter converts values for numbers (integers and decimals) and true/false only; dates, times, lists and categories are compared as text or not at all (verified in `t3_audit_engine.py`). Required: a table of column types with the operators and the value conversion for each, tested (task `FILTER-DTYPES-1`).
- **Auto-label algorithm:** when labels are rotated, truncated or hidden (font size, plot width, label count); needs a spec.
- Preview rows: default 100, "show all" toggle (UX-PREVIEW-ROWS-1); plot panel collapse (THEATER-1): as before.
- Navigation between several recipes when the selector is hidden: as before.
