# The big view: recipe design, audit, lineage, and what can be coded now (2026-11-23)
Status: for the owner's reading. Written by the coordinator; fact-checked by an independent agent on 2026-11-23 (11 statements corrected). Ledger: D-0598, D-0599. Nothing here is built by this page.

Words used on this page: a name in the recipe file (what developers call a YAML key); a column name; the entity id (the column that identifies the entity); the fingerprint of a stored table (what developers call a cache key). The bare word "key" is avoided (D-0602).

Written by the coordinator from the ledger and the study files, by reading only. No run was made. An independent agent checked every statement against the ledger and the files; it found 11 statements to correct, and they are corrected below. Not verified by it: what the held audit branch contains (section 3), which is taken from the builder's own report. Where a number comes from a run of an earlier day, the study file that holds it is named.

Your order: "can we move on the big view - what is the recipe design, audit lineage, what can we code now ... ?" (D-0598) and "we need the logic first" (D-0599).

## 1. The big line, in six sentences

1. A recipe is a directed graph: the tiers are its nodes, the results are its leaves, and the user chooses at most one node on a path (your words, D-0553). The agents' description of it, not your words: a node is a table at a tier; the original files are the roots; a joined table reads the tier 1 of its ingredients; a plot reads one table.
2. A recipe does not start a join from the metadata. The original data is joined with a left join on the metadata, when a metadata join is needed. (D-0586)
3. Before anything else, the ids are made equal: every original table and the metadata are completed to the union of all ids, with a marker ("not in original data", "not in metadata"), and the recipe says what the marked lines mean. Nothing blocks: the app warns and writes a log. (D-0572 to D-0591)
4. An audit step is a filter, a column drop or a removal by the entity id (the column that identifies the entity), written at a place the user chooses. In one step the user chooses at most one place on a path; the original parents may all be chosen; everything below is derived and cannot be chosen. (D-0553, D-0322, D-0535)
5. After a change at a place, every table below it is recalculated; no stored table of before is served. (D-0560)
6. The app never cleans data in HOME. It shows what is wrong; the user cleans, in the recipe or before the data enters the app. (D-0593 to D-0597)

## 2. Recipe design: where it stands

**Decided (your words, with the ledger line):**
- The graph model and the rule of places (D-0553); several chosen parents: the step is written in each tier 1 that comes from the parent (D-0555).
- The entity id: `is_entity_id`, one name for all cases, with your approved sentence (D-0562, D-0567); the rename is done in the one big move.
- Recipes do not start from the metadata; data first, left join (D-0564, D-0586).
- The completion of the ids is a required block in the recipe on every result table, with its meaning required; the recipe never records how many lines were added (D-0574); it is recipe-wide, with or without a join (D-0589); the marker column is kept (D-0586).
- A third check compares the id sets after the completion. With a metadata, a difference means a bug (your view, "I think", D-0590). Many unmatched ids before the completion mean a problem upstream, for example in a pipeline (D-0591).
- Your view, not a final decision (D-0588): a recipe whose only table is the "metadata" registers it under the data schemas; a guideline for the documentation. Whether it becomes a rule of the format is not decided.
- The one big migration of the recipes is shown to you as a dry run before anything is applied (D-0525; the dry-run step itself is the review session's reading, which you were not asked to confirm).

**Open, and it blocks coding the recipe format (few):**
- A. Does the completion read the files as they are (before any place), or follow the places? Your rule of places holds only in the first case. Both agents lean to "as read". (study file, D-0589 sub-section)
- B. The recipe form itself: the proposal "form 3" (blocks in order: original tables, joined tables, derived tables, results) is not confirmed (D-0496). The questions of `RECIPES_FROM_THE_MODEL_AGREED.md` that remain after the review of today are listed at its top.
- C. With no metadata: which tables are one population (the one the recipe names, or every table that declares the id).

**Kept for after the big line (small; the agents' lean is provisional meanwhile):** the names used inside the block of the recipe; before or after the recipe's tier-1 steps; the marker's exact form; the log's file name and directory; how often the "I have read this" button is shown; a dummy id; how "data first" is enforced (check, advice, documentation); the count per target; the threshold; the two metadata-only test tables.

## 3. Audit: where it stands

**Decided:**
- The first audit build writes audit steps at each tier at the places the user chose; the T3-only audit of today is replaced (D-0535).
- The effects of a step are measured and registered, and the log keeps them (D-0536, D-0537).
- One scope per history; the default place is where the original tier 1 and the metadata are joined (D-0538 to D-0550). The effect is measured after Apply (D-0546); what is shown of it is decided later (D-0536).
- The audit log with who, when, the reason, the scope and the warnings is always in the export (D-0478); an audit recipe with its record (D-0324, D-0333).
- A removal because a sample is bad is right; the audit covers it and its justification holds (D-0572).

**Built, on a held branch, not merged** (`task/audit-slice1-effects-log`): a fix for the plot columns, an audit log module, the measure of effects, a callback of the audit run. Its tests name today's places and must be redone after the design.

**Open, and it blocks the audit build:**
- D. Question A above (it decides what an audit step at the metadata does to a completed table).
- E. "Remove from all the data" under the rule of places: three forms were measured on the demo. They give the same 17 plot tables, but they differ in the exported tier-1 files (in one form 7 original tables still hold the entity). Which form is offered is not chosen. (`PATHS_AND_DERIVED_AGREED.md`, point 7 and question 5)
- F. Your notes in `WHOLE_PICTURE.md` are not closed: the file is uncommitted and waits for your "done".

## 4. Lineage: where it stands

**Decided:** the investigation runs must not rest on the old lineage structure (D-0558, D-0559); a parent reused in another graph: both graphs must be shown (D-0555; how is not decided); every run states beforehand what it tests, what is expected and why it does not rest on the old structure (D-0561).

**Not yet your decision, the agents' proposal:** the lineage of the app IS the graph of section 1, read from the recipe file itself (its blocks and names), and replaces the old lineage code.

**Established by runs of earlier days** (each variant rebuilt from scratch; `PATHS_AND_DERIVED_AGREED.md`, points at lines 35 and 40): on the demo the graph has 85 nodes and 55 places where the engine accepts a step; for every one of them, "below" equals "the fingerprint of its stored table changed"; a stored table with an old fingerprint is never served.

**In the code today (read, not run):** `libs/utils/src/utils/recipe_graph.py` already exists as one model of the recipe graph, beside the older `lineage_walk.py`, `lineage_records.py` and `lineage_sentences.py`. HOME's audit dialog uses neither for places: it writes audit steps at the plot's table (`app/modules/t3_audit_engine`).

**Not built:** the rule of places in code; the dialog that shows the places; the audit written at a chosen place.

**New with today's decisions:** the completion makes every original table depend on the metadata and the metadata on every original table. Under "files as read" (question A) this adds no place below another.

## 5. What can be coded now, within the quota

Nothing below needs Opus. Each piece is tagged with the model and effort of the repository's rule. "Needs from you" says what must be answered first.

| # | Piece | Size | Needs from you | Tag |
|---|---|---|---|---|
| 1 | The rule of places on the existing graph module (`libs/utils/src/utils/recipe_graph.py`): nodes, parents, "below", "at most one chosen place on a path", with tests on every shipped recipe. The design work left 17 scratch scripts that computed this independently; they are the reference for the tests, not code to ship. | small to medium | nothing | `[sonnet/medium]` |
| 2 | The id checks in the data check: the three checks, the numbers per table, the unmatched ids; a warning, never a refusal; the log written automatically. No completion yet. | medium | where the log directory is (a provisional place can be taken) | `[sonnet/high]` |
| 3 | A non-writable user folder warns instead of stopping the session start. | small | nothing | `[sonnet/low]` |
| 4 | The completion itself (the block in the recipe, the two markers, the required meaning, the third check as a test). | large | questions A and C; the block's names (provisional possible) | `[sonnet/high]`, after 1 and 2 |
| 5 | The one big move as a DRY RUN only (the names pass, `is_entity_id`, the four joins rewritten data first, the nine column lists that keep the marker, the entity ids of two recipes, the three `demo_abromics` lines): a report of every change, nothing applied. A dry-run script for the names already exists. | medium | nothing to start; your reading of the report before anything is applied | `[sonnet/medium]` |
| 6 | The audit at the chosen places (the held branch continued, on the new graph of piece 1). | large | questions A, E; your "done" on `WHOLE_PICTURE.md` | `[sonnet/high]`, after 1 |
| 7 | The red warning with the "I have read this" button in HOME, and the export pointing to the log. | medium | where the warning shows (provisional possible) | `[sonnet/medium]`, after 2 |

**My recommendation for the order, as a recommendation:** 1, 3 and 5 now (they need nothing from you and everything else rests on 1 and 5); then 2; then 4, 6 and 7 once A, C and E are answered. Pieces 1, 3 and 5 touch different files, so they can run side by side, each in its own worktree; one reviewer checks each before a merge.

**What stays held (quota, your order):** BLUEPRINT; the Gallery recipes; the two finished builds whose reviews must be redone; every feasibility run of the study files until its code exists.

## 6. The questions that block, in one list

- A. The completion reads the files as they are, or follows the places?
- C. With no metadata: which tables are one population?
- E. Which form of "remove from all the data" is offered?
- B. The recipe form ("form 3"): confirm, or another form.
- F. "Done" for your notes in `WHOLE_PICTURE.md`.

Everything else is on the list "after the big line".
