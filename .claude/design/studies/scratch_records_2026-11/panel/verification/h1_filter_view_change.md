# H1: an exploration filter and a change of what the table shows (verification, read-only)

Task H1-FILTER-VIEW-1. Date 2026-11-16. Branch `feat/recipe-format-1`, HEAD `bb90db5c`. Nothing tracked was changed.
How I worked: a scratch copy of HEAD (`git archive`) in `tmpAI/panel/verification/scratch_h1/copy`, the app started under `SPARMVET_APP_FEATURES=qa` on port 8765, driven with Playwright (Chromium headless). Scripts: `scratch_h1/fn_case.py` (functions), `scen_explore.py`, `scen_mix.py`, `scen_audit.py` (browser), outputs `out_explore.txt`, `out_audit.txt`, screenshots in `scratch_h1/shots/`. Labels: RAN = I ran it; READ = I read the file and line; REASONED = from code, not run.
The frame is the one of the coordinator's messages: "My view" is NOT the target. The decided model is the stage (T1 | T2 | T3) and the version (Original | Audit), ledger D-0016 and `home_audit_steps.md:83`. Her words of M167 to M170 are quoted as "relayed, 2026-11-16" (not yet in the ledger).

## 0. The example used

Recipe `1_test_data_ST22_dummy`, table `QA_AMR_per_sample`, plot `qa_amr_genes_per_sample` (group "QA canaries"). RAN (`fn_case.py`):
- T1 ("Raw") has 74 rows and the columns sample_id, country, source, year, **gene**, predicted_phenotype.
- T2 ("Result") has 42 rows and the columns sample_id, country, n_amr_genes. **`gene` is not in T2.**
- Filter "gene = blaTEM-1C": on T1 it keeps 4 rows; on T2 it keeps all 42 (skipped); `inapplicable_filter_rows` finds it, nothing calls it.

## 1. What the screen does today (RAN, browser, one session)

What the user sees, step by step (`out_explore.txt`, S0 to S13):

| Step | Filter list | Badge of the table | Table shown | Plot |
|---|---|---|---|---|
| S1 Data to show = Raw | empty | "Viewing: Raw" | all rows | Result plot |
| S2 build "gene = blaTEM-1C", Apply | listed | "1 preview filter(s) on, not saved" | 4 rows (filtered) | unchanged (same image) |
| S3 Data to show = Result | **still listed** | **still "1 preview filter(s) on"** | **all rows, filter not applied, nothing said** | unchanged |
| S4 back to Raw | listed | "1 on" | 4 rows again (**the filter comes back**) | unchanged |
| S5 Plot to show = My view (data Raw) | listed | "1 on" | 4 rows | image unchanged: the filter is skipped on the plot table (T2, no `gene`), no notice; plot badge only says "Viewing: My view" |
| S6 Data to show = My view | listed | "Viewing: My view", **no count** (`view_badge.py:63` counts only on T1 and T2) | all rows (skipped) | unchanged |
| S7 another plot sub-tab (other dataset, columns sample_id and ST) | **still listed**, "1 on" | "Viewing: Raw / 1 on" | that table, unfiltered | its own plot |
| S8 back | listed | "1 on" | 4 rows | unchanged |
| S9 another group tab (Quality Control) | **still listed**, "1 on" | "1 on" | other table | other plot |
| S10 back | listed | "1 on" | 4 rows | unchanged |
| S11 Gallery and back | list not visible until the Filters panel is opened (panel collapses); after opening: listed (M4) | "1 on" | 4 rows | unchanged |
| S12 Blueprint and back | same | "1 on" | 4 rows | unchanged |
| S13 reload (F5) | new session: nothing kept | | | |

Two filters from two views mixed (`scen_mix.py`, RAN): on Result I added "n_amr_genes > 1" while "gene = ..." was still listed. List: both. Badge "2 preview filter(s) on". Table: 18 rows (only the second applied). Back on Raw: badge "2 on", table 4 rows (only the first applied, `n_amr_genes` skipped). So the count is always the list length, not the number applied.

In short: no change of view, tab or workspace resets or hides an exploration filter today. The list and the count follow the session. The table silently ignores a filter whose column is missing. The filter FORM offers only the columns of the table shown (RAN: after S3 the form columns are sample_id, country, n_amr_genes), so creating a filter on a missing column is not possible (complies with D-0175).

What counts as "the shown table changes" in code today (READ):
- "Data to show" radio `tier_toggle` -> `_track_tier_toggle` only copies the value (`home_theater.py:1170-1173`). `_resolve_active_lf` reads it (`:291`). Nothing is cleared.
- plot sub-tab and group tab -> `active_home_subtab` -> another `target_dataset`; nothing is cleared (S7, S9 RAN).
- workspace switch: nothing is cleared (S11, S12 RAN; "survives all panel switches", contract section 13).
- The only places that clear the two exploration lists today: the Reset button (`filter_and_audit_handlers.py:693-698`), Send to Audit (`:690-691`, the rows moved to audit), and an Apply of audit steps (`_clear_filters_on_t3_apply`, `:1062-1078`). No clearing on a change of view anywhere (grep of `applied_filters` / `_pending_filters` in `app/`: no such write).
- The list on screen is `_pending_filters` (`filter_and_audit_handlers.py:201`); the table uses `applied_filters` (`home_theater.py:1336`). Apply copies one into the other (`:625`). REASONED, not run: a staged row built on T1 and not yet applied survives a change to T2 and can be applied there.

## 2. Audit as built today (RAN, `scen_audit.py`)

Step: filter `country in France` sent to audit on this plot with a reason, Apply. Then:

| Step | Table (Data to show) | Plot | Audit step |
|---|---|---|---|
| A1 My view applied | My view: 4 rows | Result plot (plot choice still Result) | in the stack, reason field |
| A2 Data = Result | 24 rows window, unfiltered | Result | still in the stack |
| A3 Data = Raw | unfiltered | Result | still in the stack |
| A4 Plot to show = My view, data Raw | Raw unfiltered | **plot changes** (image differs) | still in the stack |
| A5 Data = My view | 4 rows | My view plot | still |
| A6 other plot sub-tab | other plot, step not shown (it belongs to the first plot) | | stack of that plot: none |
| A7, A8, A9 back, other group tab, Gallery and back | 4 rows in My view | My view plot, same image | still in the stack |
| Export, started from Data = Raw and Plot = Result | | | bundle holds `t3_steps.yaml` with the step (filter_row, country, the reason) and `T3_data_qa_amr_genes_per_sample.tsv` with 4 data rows |

So: an audit step does not depend on the view (stays, is exported). But it SHOWS only when the user picks "My view" for the table and "My view" for the plot. Raw and Result tables are never changed by it (ADR-085, ADR-098 point 2). The step belongs to one plot (`t3_audit_steps_by_plot`, contract section 13), not to nodes of a recipe copy (lineage ticks, `audit_recipe`: not built, ADR-105 "NOT BUILT"). A step on a column the plot's table lacks is an ERROR, not a skip (RAN, `fn_case.py`: `AuditStepError`: "step modif_filter: column 'gene' is not in the table. The table has the columns sample_id, country, n_amr_genes"). Exploration filters and audit steps are separate state: exploration = two `reactive.Value` (`home_theater.py:214-215`); audit = `home_state["t3_audit_steps_by_plot"]`; the Reset and the clearing paths of section 1 touch only the first two (READ `filter_and_audit_handlers.py:693-698`).

## 3. What is written (each with who and when)

| Text | What it says | Who, when |
|---|---|---|
| Ledger D-0019 (line 48) | "Exploration has ONE plot (Result, immutable); audit mode has the Result and the audited plot; inactive filters are hidden (P2)" | EVE, DECIDED, 2026-11-12. The cited source (`handoff_active.md:503`, "2026-11-12 (P2, plot decided)") quotes her only for "Exploration has ONE plot". The words "inactive filters are hidden" are not in that source. |
| Source of "hidden" | `home_audit_steps.md:80`: "the preview lists are **hidden** in audit mode (kept, shown again in Exploration)"; `home_audit_reading_guide.md:32` row P3 "Preview lists while audit mode is on: DECIDED 2026-11-12 (Eve): hidden, kept"; `home_preview_filters.md` section 4 point 8 "Switching between Exploration and audit mode is not a view change: the lists are kept, and not applied while audit mode is on" | Eve, 2026-11-12 (P3). The ledger labels it P2, the source is P3 (a label mismatch, rule H: reported, not resolved). |
| D-0014 | "Exploration filters change the table on every view, plots only on My view; audited steps permanent" | EVE 2026-11-11 (ADR-098 "confirmed by @evezeyl") |
| D-0175 | "A filter can only be created in a view whose table has the column ... the app cannot propose a filter on a column that does not exist in this table" | EVE 2026-11-16 |
| D-0053, ADR-105 point 1 | "in exploration the filter acts only on the data viewed"; "Exploration acts only on the data being viewed ... never saved or exported. Exploration has one plot" | EVE, 2026-11-14 |
| D-0016, `home_audit_steps.md:83` | audit mode replaces My view and Compare; two controls, stage and version | EVE 2026-11-11 / 2026-11-12 (P7) |
| **`home_preview_filters.md` section 4 point 5** | "**A change of Data view (T1, T2, T3) clears all preview filters and column choices**, with a message ("3 preview filters cleared, you changed view"). [to build]"; section 8: why filters clear; section 4 point 8 (mode switch is not a view change) | In the file since 2026-11-11 (commit `5f15cc41`, marked `[decided]` in `d5db8f8b`). Her comment in `d5db8f8b` line 47: "@eve: ok and I agree and understand: this is why the filters needs to be cleared on view change." (2026-11-11). The T1/T2/T3 wording is from `de05eaab`, 2026-11-13. It has NO ledger number. |
| `home_preview_filters.md` section 5 | "A preview list belongs to one view and one dataset ... Each dataset keeps its own list while you stay in the same view. [to build; today ONE global list]"; "The safety skip ... stays but should never fire." | file, 2026-11-11 |
| Contract section 13 (`ui_implementation_contract.md:855`) | "Tab changes clear `_pending_filters` and `_pending_t3_nodes` but never touch `applied_filters` or `t3_audit_steps`" ; line 805 "survives all panel switches" | contract, Phase 22 (an agent's record). RAN: tab changes do NOT clear the staged list; this sentence is not true today. |
| Contract section 8 | "They affect the 'My view' (T3) plot and data preview only — T1 and T2 never reflect `applied_filters`" | contract, ADR-085 era; contradicts ADR-098 and the code (the table shows them on every view). Already stale. |
| ADR-098 point 1 and 4 | plots change on My view; point 4 (skip) marked "no longer holds" 2026-11-14 -> "plain error (ADR-104 point 1)" | ADR-098 2026-11-11 / correction 2026-11-14 |
| M166 | Her proposal: "Well on explaration the data is not modified so ... the filter can be reset at change of view of table that solves the coordinator problem - then the user will have to filter again" | her turn 2026-11-16 (ledger "Asked, not decided") |
| M167, M168, M169, M170 (relayed, 2026-11-16) | see section 4 | her words, 2026-11-16 |

## 3a. Does D-0019 answer the case? No.

Readings of "inactive filters are hidden":
- A (the one the records support): the exploration (preview) filter lists are hidden while audit mode is on; kept and shown again in Exploration (`home_audit_steps.md:80`, reading guide P3, preview file point 8). "Inactive" = not applied in this mode. Nothing about a missing column.
- B (not written anywhere): a filter whose column is missing in the table shown is "inactive" and hidden there, shown again where the column exists. I found no text that says this. D-0019 is therefore not a source for reading B.
- C: "inactive" = filters not of the stage shown. Also not written.
D-0019 does not settle the case. Her M168/M170 words do (section 4).

## 4. What the decided model requires (her words, relayed 2026-11-16) and the gap

Her words: M167 "In EXPLORATION a filter reset is OK, because what we do is try to understand our data, and we can always go to T1. In AUDIT the filters and the scope are DEFINED and APPLIED, so they still apply no matter if the view changes, because they are written in the audit_recipe." M168 "if the user is on T1, the filter is built from T1; if the user sees T2, the filter is built on T2; if the user sees T3, the filter is built on T3; if the user changes the view, the filter is RESET and rebuilt. In PREVIEW mode (exploration), of course." M169 "There is no 'My view' anymore in the refactor. There is the original, and T1, T2 and T3: T1 feeds T2, T2 feeds T3, T3 feeds the plot. Any change that affects the content of T3 changes the plot." M170 "Yes, you got it now." plus "in EXPLORATION there is only ONE plot view (the plot is the Result); there is no button to select a plot version any more."

| # | Behaviour required | Source | Built today | Evidence | Gap |
|---|---|---|---|---|---|
| 1 | An exploration filter is built on the table of the stage shown (its columns only) | D-0175; M168 | YES | form columns follow the table (RAN S3, M2) | none |
| 2 | When the stage shown changes, the filter is reset and rebuilt | M168/M170; `home_preview_filters.md` s4 p5 [to build] | NO | S3 to S4: listed, counted, comes back | build the reset |
| 3 | The exploration filter never changes the plot | ADR-099 pt 1; ADR-105 pt 1; D-0019; M169/M170 | NO | the plot applies exploration filters when "Plot to show = My view" (`home_theater.py:440,474`; ADR-098 pt 1) | remove with the old screen (stage 2) |
| 4 | One plot in exploration, no plot-version button | D-0019; M170 | NO | "Plot to show" radio (`home_theater.py:975-1000`) | stage 2 screen |
| 5 | Two controls: stage (T1 or T2 or T3) and version (Original or Audit) | D-0016; AS:83 | NO | "Data to show" Raw/Result/My view plus "Plot to show" | stage 2 screen |
| 6 | Audit steps do not depend on the view; they live in the audit recipe | M167/M169; D-0102; ADR-105 pt 6 | PARTLY | steps persist and export from any view (RAN A1 to A9, export); but they are per plot in session state (`t3_audit_steps_by_plot`), not in a recipe copy | audit recipe not built (ADR-105 "NOT BUILT") |
| 7 | A change that affects T3 changes the plot | M169 | PARTLY | A4: the plot changes only when the user selects "Plot to show = My view"; default is Result | follows from 3, 4, 5 |
| 8 | No result changes silently / a filter not applied is shown as such | D-0050, D-0165 (principle), ADR-104 pt 1 | NO | S3: "1 on" and nothing applied; skip `t3_audit_engine.py:550-552`; test `test_modif_filter_vs_home_filter.py:57` says "by design" | with a reset the common path disappears; the remaining skip paths below need a choice |

Remaining problems she listed (RAN unless said):
- Stale badge: S3, S5, S6, M3. The count is `len(applied_filters)` (`home_theater.py:721,1311`), not the number applied.
- A filter that comes back: S3 to S4, M3.
- Two filters from two views mixed: M2/M3.
- A filter kept while the table is another dataset: S7, S9 (a plot sub-tab or group tab change). Eve's words name the stage; whether another dataset counts as "the view changes" is not in her words (question 1).
- Session restore: READ `session_handlers.py:417` restores `tier_toggle` from the ghost and does not touch `applied_filters` / `_pending_filters`; so after a restore the stage can differ from the one the filter was built on. Not run (needs a saved ghost; I did not build one).
- The Filters panel collapses after a workspace switch (S11), the list is then not visible but still applied (the badge says so).
- Not checked: the column selector ("column choices" in the design file), Compare mode.

## 5. Three ways side by side (the example: filter on `gene` built on T1, user then looks at T2)

| | A. Reset on a change of the stage shown (her proposal, M168, M170) | B. Hide where the column is missing, keep for the view that has it | C. As today plus a notice |
|---|---|---|---|
| T1 -> T2 | Filter and count disappear; notice "1 preview filter cleared, you changed view"; T2 table unfiltered; user builds a new filter on T2 | Filter list for T2 shows none; badge no count; the T1 filter is kept in the background | list and count stay; a line "gene is not in this table, the filter is not applied here"; table unfiltered |
| T2 -> T1 again | nothing: the user filters again | filter comes back, table 4 rows | filter applied again |
| Cost | a look at T2 loses the T1 filter ("we can always go to T1", her words) | hidden state; a filter exists that the user does not see; two lists to keep (one per stage); "comes back" kept | badge and list stay long; nothing prevents two filters of two views mixed; many notices |
| Agrees with | M167 to M170; `home_preview_filters.md` s4 p5 and s8 (her comment 2026-11-11); ADR-105 pt 1; D-0053 | D-0019 reading B only (not written); `home_preview_filters.md` s5 "each dataset keeps its own list" | D-0015 (inform, do not block) |
| Contradicts | `home_preview_filters.md` s5 (list per view and dataset); contract s13 "never touch applied_filters" (that sentence is already untrue) | M168 "the filter is RESET and rebuilt"; D-0050 ("no silent error": a hidden filter is a silent state); a hidden-but-kept filter is a result that depends on state the user cannot see | M168 (reset); `home_preview_filters.md` s4 p5; D-0050 (a filter listed as "on" and not applied is the silent case that was found) |
| Code touched | home_theater.py (an effect on the stage change) or filter_and_audit_handlers.py; clear both lists; notice; badge; about 15 to 30 lines; tests: a browser test (S3 case) and a headless test of the clearing; change test `test_modif_filter_vs_home_filter.py:57` only if the skip is also removed | a per-stage store of filters (a dict keyed by stage and dataset), the list, the badge and the table all read it: about 60 to 100 lines, tests for each stage | a notice from `inapplicable_filter_rows` (already written, uncalled) in the badge and list: about 20 lines; one test changed |
| Audit steps | not touched | not touched | not touched |

"Change of view" would have to mean (the cost to the user in each reading):
1. "Data to show" / the stage changes (T1, T2, T3): the one her words name. A filter built on T1 is gone after a look at T2 and back. Matches D-0175 and M168.
2. plot sub-tab of ANOTHER dataset: today the filter follows to a table with other columns (S7). Resetting costs the user the filter when moving between plots of different data; not resetting keeps a filter that is silently skipped. Her words do not say.
3. plot sub-tab of the SAME dataset, group tab: same table: in her reading (M168 "a change that keeps the same table keeps the filter") nothing to reset. This is the reading of the review session (M168), not her words.
4. workspace switch (Gallery, Blueprint, back): same stage and table; nothing to reset (the design file point 8 says a mode switch is not a view change).
For all three ways the audit steps stay: separate state (section 2). Confirmed from code (READ) and run (A1 to A9).

## 6. Is a reset on a change of "Data to show" small and also true in the old model?

- SMALL in size: yes. One effect on `tier_toggle` that sets `_pending_filters` and `applied_filters` to empty, plus one notice and a browser test of the S3 case: about 15 to 30 lines, files `app/handlers/home_theater.py` or `filter_and_audit_handlers.py` and one test file. Fixes the stale badge, the filter that comes back and the mixing for the case of the verification (Raw to Result).
- TRUE in the old model: only partly.
  1. In the old model the plot follows exploration filters when "Plot to show = My view" (ADR-098 point 1; `home_theater.py:440,474`; contract section 4 row "Filters panel Apply"). A reset on "Data to show" would silently change that plot (filter gone, plot redrawn) when the user only changed the table view. That is a result changing without a plot choice by the user. In the decided model the plot never depends on exploration filters, so the problem does not exist there.
  2. In the old model "My view" is a stage that carries audit steps and the exploration filters together; Result -> My view has the same columns, so the reset would fire where no column is missing. Her words (M168) say "RESET" for any change of the stage shown, so this is consistent with the decided rule, not with the old behaviour ADR-098 point 1.
  3. It does not fix: another dataset by plot sub-tab (S7, S9), session restore, a staged-but-not-applied row only partly (both lists must be cleared), the badge in My view (S6).
- My reading: small, but not clearly "also true in the old model"; her instruction says to wait for stage 2 unless it is both. Decide with her answer to question 2.

## 7. Texts that would change (nothing is changed; no rule file without her yes)

1. Ledger (scribe): a new line, her words M167 to M170 with date: exploration filter belongs to the stage shown; reset on a change of stage; one plot in exploration; audit steps tied to the audit recipe, never to the view; supersedes the part of D-0014 that says "plots only on My view" (M170 asks for this). D-0019 is not rewritten; its P2/P3 label mismatch is reported. D-0053 unchanged.
2. `home_preview_filters.md` section 4 point 5: already says it ("A change of Data view (T1, T2, T3) clears all preview filters and column choices"). Needs: the ledger number, "[to build]" kept, and a sentence on another dataset (after question 1). Section 5: "A preview list belongs to one view and one dataset ... Each dataset keeps its own list while you stay in the same view" -> must say the list belongs to the stage shown and is reset when it changes. Section 5 "The safety skip ... stays but should never fire" -> conflicts with ADR-104 pt 1 ("plain error", no silent skip); must say what happens on the paths where it can still fire.
3. `ui_implementation_contract.md` section 13: "Tab changes clear `_pending_filters` and `_pending_t3_nodes` but never touch `applied_filters` or `t3_audit_steps`" -> "A change of the stage shown clears `_pending_filters` and `applied_filters` (exploration, with a notice); a change of tab or workspace does not; `t3_audit_steps` never change with the view." Line 805 "survives all panel switches": true for audit state; for exploration filters it would say they survive a workspace switch but not a stage change.
4. Contract section 4, row "Filters panel 'Apply' ... Changes the data table on every view; changes PLOTS only on My view (ADR-098)" and the SUPERSEDED paragraph under the table: plots never change (ADR-099 pt 1, M170); add "reset when the stage shown changes". Section 8, "They affect the 'My view' (T3) plot and data preview only" and "`applied_filters` ... only when `tier_toggle.get() == "T3"`": already contradicted by ADR-098 and the code; replace with "they change the table of the stage shown".
5. ADR-098 point 1 ("In plots they apply only on My view") and point 7 ("a preview filter belongs to a dataset ... today it is one global list"); ADR-105 point 1 add "and is reset when the stage shown changes (her words, 2026-11-16)". ADR-098 point 4 already corrected.
6. Code comment and test: `t3_audit_engine.py:550-552` and `test_modif_filter_vs_home_filter.py:57` ("Difference by design") when the skip is replaced by a notice or an error.
7. `view_badge.py:63-66` and its tests if the badge counts applied filters only.

## 8. What must change (for her to confirm)

1. Record her logic as a ledger decision (words, date), superseding the "My view" wording of D-0014.
2. Reset both exploration lists when the stage shown changes, with the notice "N preview filters cleared, you changed view" (design file point 5).
3. In the stage 2 screen: one stage control and one version control; one plot in exploration; no exploration filter ever reaches a plot.
4. Keep audit steps in the audit recipe, shown by the version control, independent of the stage (ADR-105, not built).
5. Decide what happens on the paths where a column can still be missing (other dataset, restore): notice or error, never silent (D-0050).
6. Fix the records: contract s13 sentence, s8, s4; design file s5; the P2/P3 label of D-0019.

## 9. Questions for her (plain)

Example: you filter "gene = blaTEM-1C" while looking at Raw (T1). You then look at Result (T2); `gene` is not in T2.

1. Her words say the filter is reset when the stage changes (T1, T2, T3). When you go to a plot of ANOTHER table (another plot tab with other columns) and the stage stays the same, should the filter also be reset? (a) yes, any change of the table shown resets it; (b) no, only a change of stage; then the filter stays and a notice says "gene is not in this table, the filter is not applied here". Default: the records do not support one; the design file speaks of one list per view and dataset (a), the review session read it as (b) (M168).
2. Should the reset be built now on the old screen ("Data to show" and "Plot to show" still there), or wait for the stage 2 screen? On the old screen a reset also redraws the plot when "Plot to show = My view", because that screen still lets an exploration filter change the plot. Default: wait (her instruction M169: not on the old model unless small and also true there; I find it small but only partly true).
3. When the filters are reset, do you want the notice "3 preview filters cleared, you changed view"? Default: yes (written in `home_preview_filters.md` section 4 point 5; D-0015 inform the user).

## 10. What I could not run or see

- Session restore with a saved ghost (read only); Compare mode; the column selector reset; a staged-but-not-applied row after a stage change (reasoned from `:625`); the dtype fallback when a table schema cannot be read (`t3_audit_engine.py:543`).
- My plot test compares the image bytes of the visible plot; it shows "changed or not", not what changed.
- Only one recipe and one table; a second table with the same column in T1 and T2 would show the same behaviour (code is generic).
- Everything ran on HEAD `bb90db5c` under the `qa` features, one browser session, not the real deployment.

## 11. Compliance table

| Decision | What the code does today | file:line |
|---|---|---|
| D-0019 "inactive filters are hidden (P2)" | Does not answer this case (reading A: the lists are hidden while audit mode is on). Not testable today: the old screen has no audit mode, so no list is ever hidden; the lists are always applied | `home_theater.py:1336` (list always applied); source of "hidden": `home_audit_steps.md:80` |
| D-0175 "the app cannot propose a filter on a column that does not exist in this table" | Complied for creation: the form offers the columns of the table shown (RAN). A filter already built is not removed when the table changes (not covered by D-0175 text; her M168 covers it) | `filter_and_audit_handlers.py:237` (`_dialog_table`), RAN S3/M2 |
| D-0165 "Where no decision exists and one is needed, that must be reported to her" | Reported: (1) the other-dataset case, (2) old screen or stage 2, (3) the notice; and the ledger gap: her M168 logic has no number yet; the design-file rule of 2026-11-11 has none | section 9 |
