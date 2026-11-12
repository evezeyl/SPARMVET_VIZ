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

An **entity** is the unit a key identifies (a sample, a patient, a site, a sensor). A **key** is the column that identifies it (it repeats in long tables, so rows and entities are counted separately). An **attribute** is a descriptive column. A **population table** has one row per entity. The data flow of a plot is **T1** (the joined data after the recipe's first steps), **T2** (what plots share) and **T3** (the plot's own data); **every table has all three, with or without a join; T2 and T3 can be empty, and empty means the same as the previous one.** The path through them is the **lineage**. *Example (bioinformatics test recipe): entity = sequenced sample, key = `sample_id`, attribute = country.* Full vocabulary: `home_audit_steps.md` section 2 and the user glossary.

---

## Two modes

**Exploration [built, being simplified]** (Data: Raw | Result). For looking. A preview filter changes the data table only; it is never saved, never exported, and is cleared when the view changes. One plot is shown, the Result, immutable. Missing values are a visible, selectable value; a notice says what the preview is and is not. Detail: `home_preview_filters.md`.

**Audit mode [target]**, switched on only by the sandbox flag. The only way to change data, a plot or an export. Requires export, Compare and sessions (the user compares the effect, saves unfinished work, exports what is finished). Replaces today's "My view", "Plot to show" and the propagation dialog.

---

## Audit mode in short [target]

1. **Two kinds of step:** filter rows by a value or a list of values; drop a column. Every step has **one free-text reason** (a hashtag convention is suggested), is recorded, and can be removed.
2. **One mechanism for every removal.** The user picks a field; the **lineage** shows every node (T1, T2, T3 of every table) where the field exists, as tick lines; all are ticked by default; the user unticks what must not change. For a node without the field the dialog suggests, never imposes, a column it shares with another node. The key is **information** (counts, suggestions, the warning that a filter on a join key may change the join), not mechanism. A drop works the same way.
3. **The audit recipe** is the original recipe plus the steps written into its own lists (end of a table's tier 1 or tier 2, or the plot's T3 list); it is exportable and re-runnable; the original data and recipe are never changed. In audit only filters, drops and removals are possible; a recipe maker may use any action in T3 and is responsible for good practice.
4. **Information before Apply:** the lineage backwards to the roots and forwards to every descendant, the plots that would change, rows **and entities** before and after, a preview of the open plot, and the later steps that summarise rows. A read-only popup per node (own window, built so a panel can replace it later) shows what the recipe already does there.
5. **Attrition per step**, derived and never stored: from the source population, through the recipe's own row-removing steps, then the audit steps, each with before and after and the missing values removed. The figure caption in the report is composed from it, in the entity's own word (declared in the recipe).
6. **Three levels of message:** info, warning, block (technical only). Missing values are a value: "everything except x" keeps them, "only x" and comparisons remove them, always counted.
7. **Original plots stay as evidence:** the immutable Result, the Compare reference, and in the export the original plot of every plot that is really affected (its T3 content differs).

---

## Export, import, sessions

- **Export [built in part, target extended]:** one bundle: audited plots, the original Result plot for each really affected plot, original and audit data, the steps with reasons and the event log, the exclusion table, the attrition table, the verification legs (engine, data, recipe, audit recipe, steps, record) and the key of every node; one tick adds the recipe and the raw data (with a warning about sensitive data). Exploration is never exported. The export is refused when the recipe or the data changed since the view was opened.
- **Import [target, gated]:** its own functionality, on only through the configuration and only for an authorised person; recipes normally come from a system manager. Warn and validate with the same recipe validation as HOME's load gate, plus a rule that formulas use only an allowed list of operations. Every leg is reported as match, mismatch or not checked; it never blocks; it writes a new recipe and session, never into the live state.
- **Sessions [built, extended]:** the session holds the recipe and data references and, in audit, the step list; restoring recomputes. Audit steps of old data stay with the old session (a warning on restore).
- **Hashes:** a series of labelled parts per node (`E . rC . dC . [a1] . [s2] . [a2] . [s3] . [a3]`); whole-recipe hashes identify the project state and never decide what to rebuild; the data hash is the full content once per session.

---

## User Functionalities

| Functionality | What the user can do | Status |
|---|---|---|
| **Select data analysis recipe** | choose a recipe that passed the load gate; rejected recipes are listed with the reason | built |
| **Navigate** | analysis groups and plots | built |
| **Inspect** | Data: Raw or Result, first rows, column selector (preview only), row counts, notices | built, simplified by the redesign |
| **Preview filters** | change the table to look at it; never saved | built, being rebuilt per `home_preview_filters.md` |
| **Audit** | filter or drop with the lineage and ticks, with a reason; undo, revert to a step, remove all; Compare original and audited plot | target |
| **Information** | the node popup, the lineage, the attrition table | target |
| **Export / Import** | see above | built in part / target |
| **Session** | save, restore, import, export, delete | built |
| **Load data, replace metadata** | gated ingestion panels | built, gated by flags |
| **Palette override** | a per-session colour palette that does not modify the recipe | built |

---

## Non-Goals

- HOME does not build or edit recipes or **plot specifications** (the graphics description for the visualisation factory: mapping, layers, theme); that is BLUEPRINT, which needs to operate on plot specs to create plots. The audit writes only **data** steps (the T1, T2 and T3 lists); the plot spec is copied unchanged into the audit recipe, and the T3 list sits beside the spec, not inside it, so the two cannot step on each other.
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
- **Palette override is session-scoped;** labels adapt automatically to plot size.

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

---

## Open Questions

- What stays of the right panel in audit mode (Inherited nodes, filter inventory, pending badge): decided at the screen redraw.
- **Auto-label algorithm:** when labels are rotated, truncated or hidden (font size, plot width, label count); needs a spec.
- Preview rows: default 100, "show all" toggle (UX-PREVIEW-ROWS-1); plot panel collapse (THEATER-1).
- Navigation between several recipes when the selector is hidden.
