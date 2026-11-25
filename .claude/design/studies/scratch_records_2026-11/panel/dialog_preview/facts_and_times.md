# DIALOG-PREVIEW-COST-1: facts and times for "can the user check the other plots and tables while the audit dialog is open?"

Date 2026-11-16, branch `feat/recipe-format-1`, HEAD `11c7ca5e`. Read-only: nothing tracked was changed. Scripts and raw numbers: `tmpAI/panel/dialog_preview/measure.py`, `m1.json` (recipe data as it is), `m10.json` (10 times the rows), `run10.log`, scratch data `x10/`. The scripts reuse `tmpAI/panel/audit_model/common.py` and `engine.py`.
Labels: READ = I read it in the file named. RAN = I ran it, numbers below. REASONED = my inference, steps given. NOT RUN = said at the end.

## 1. What is decided or written about the dialog (READ)

Ledger (`.claude/knowledge/decision_ledger.md`), all DECIDED and taken by EVE unless said:
- D-0016 (line 45): "Apply/Cancel dialog with reason; original T1/T2 never changed"; "no draft"; accepted in principle, not built.
- D-0020 (line 49): "One candidate step at a time, previewed in a modal; column drop follows the filter logic ... (P3)". Source `home_audit_steps.md:78-81`.
- D-0093 (line 122): "the lineage offers the nodes; the USER ticks the nodes where a step is written; it is applied at each ticked node and counted before and after along the lineage".
- D-0194 (line 223): all candidate nodes are ticked when the dialog opens; "it show clearly the extend of where it will be removed". D-0195 (224): the whole lineage is searched, no silent failure.
- D-0197 (226): the ids are those of the view where the selection was made (T1 28, T2 21).
- D-0202 (231): B4, option (a): the value is typed per node. D-0203 (232): the dialog warns when a value does not correspond one-to-one between nodes.
- D-0168 (197): nothing vanishes silently in the audit; a warning. D-0149 (178): warn only when there is a problem.
- Not a decision: M185 (ledger line 274, "Asked, not decided"): her question "he can checks the other plots and tables ... before commiting ... Is this possible ?".

What the decided dialog shows per place (`home_audit_steps.md`):
- Line 74-75: reach, "the chain, affected plots, warnings, rows before/after"; Apply only when a reach is chosen and a reason is written; "Cancel closes the dialog and changes nothing"; "There is no draft list".
- Line 78: the dialog "is modal: one candidate; changing it replaces the preview; Cancel or closing discards it; Apply with a reason adopts the computed preview (a cache hit)"; "There is no staged list and no preview in the panel; the plots change only at Apply". "Large data: the dialog may show counts only ... Eve does not expect data large enough to need it."
- Line 138 (item 7, decided 2026-11-12): the lineage back to the roots and forward to every descendant, "with rows and samples before and after, from running the audit recipe". Each place is a tick line. A read-only popup per node "kept open while the user looks (not a modal dialog that blocks the screen: a pinned panel ...; the mechanism is for stage 2)"; it answers "what was already done to this data?" (the recipe's steps of that node), not "what would the candidate do".
- Line 143 (item 12): "rows and entities before and after for every table and plot downstream, from running the audit recipe"; after Apply the same condition is evaluated again on every node that has the field.
- `home_stage2_mechanism_spec.md:130` (item 3, tagged DECIDED, ADR-105 point 4): the dialog "compiles the candidate into a temporary copy, runs the affected nodes through the audit orchestrator, shows counts before and after and a preview of the open plot, and discards it". So counts per place and a preview of the OPEN plot are written as decided. A preview of any other plot, or of a table at a clicked place, is not written.
- `home_audit_steps.md:222-225` (item 5, tagged "[confirm]", not decided): trial computation stored in the audit cache under the key of the would-be step list; Apply adopts it; Cancel lets it age out.
- Intent document first page (`home_redesign_intent_and_consequences.md:31-32`, points 6 and 7, confirmed by Eve 2026-11-16, D-0143 to D-0150): "The user ticks the nodes; what is ticked is what is written"; "One step at a time, shown before Apply with rows and entities before and after ... Cancel changes nothing."
- `home_audit_steps.md:648` (D4: a three-step dialog with a "before/after preview of the open plot") is a proposal in a table marked "[confirm]": not decided.

## 2. What exists today (READ, not run in a browser)

- The filter form is in the left sidebar, not a modal. Its counts are one sentence about missing values in ONE table: `filter_na_text_ui` calls `dialog_lines(_active_frame(), col, op, na)` (`app/handlers/filter_and_audit_handlers.py:458-472`); `dialog_lines` -> `count_missing` counts null and NaN rows in the column of that one table (`libs/utils/src/utils/missing_values.py:63-77, 130-142`). `dialog_frame` (`app/modules/t3_audit_engine.py:677-681`) gives the table the form acts on (My view: after the plot's audited steps). No before/after, no other table.
- The propagation dialog (`_open_propagation_modal`, `filter_and_audit_handlers.py:814-960`): "This plot only / All plots / All plots except", and a line "N apply, M skip (col missing)" from `_column_presence_per_plot` (a schema check, 770-810). It shows NO row or sample counts. Candidate state lives in `_propagation_scratch` (a `reactive.Value`, line 686, 760) until confirm.
- Compare (`plot_view == "CMP"`, `home_theater.py:731-743`): the original plot beside the My view plot, for the ACTIVE plot only, with the steps already in My view (committed in `home_state`, or the exploration filters). It is not a preview of a step that is not yet entered.
- Blocking: the propagation dialog and the help dialog are built with `ui.modal(..., easy_close=True)` then `ui.modal_show` (`filter_and_audit_handlers.py:896-960`, `home_theater.py:1572-1579`). Shiny `ui.modal` is a Bootstrap modal with a backdrop; I did not run a browser to confirm what a click on the page does (REASONED). So today a modal hides and blocks HOME. The decided design also says "modal" (`home_audit_steps.md:78`); the per-node popup of line 138 is the one written as not blocking.

## 3. Measurements on recipe `1_test_data_ST22_dummy` (RAN)

Machine: 12 CPUs, load average 1.3 to 2.8 during the runs (other sessions running; numbers are not quiet-machine numbers). Three runs each; the table gives the middle of three, range in brackets. Engine: the real `DataOrchestrator` on a forked recipe; real `modif_filter`; plots drawn with the real `VizFactory.render(...)`, then `.draw()` and `savefig` to a PNG in memory (dpi 100). The step at a plot (T3) is applied with the same action on the plot's T2 table, because the engine has no reader of a plot's tier-3 list (as in `audit_model/scenarios_report.md`).
"cold" = tables not stored (fresh folder, built from the tsv files). "warm" = stored tables read again by the same orchestrator and keys. A candidate step changes the key, so a candidate is always cold the first time; warm is what Apply or a second look would cost. Python was already running (imports not counted). Before-numbers for the whole recipe are the app's normal start; a candidate rebuilds ALL tables, because the cache key covers the whole recipe (`home_stage2_mechanism_spec.md` and `home_audit_steps.md` note this; I did not re-check `cache_keys.py` today).
Candidates: (P) `country != Norway`, ticked at the 39 places that have `country`; (I) `sample_id not in <the 28 Norway ids>`, ticked at the 69 places that have `sample_id` (4 of the 73 places have no `sample_id`: the reference table at two stages and two plots; so 69 and not 73; 71 of 73 places changed their counts with (I), 25 of 73 with (P)).

| What | Rows as they are (recipe data) | 10 times the rows |
|---|---|---|
| Whole recipe, before, cold (all 28 tables, two stages each) | 1.7 s (1.69 to 1.74) | 2.7 s (2.70 to 2.75) |
| Whole recipe, before, warm | 0.08 s | 0.08 s |
| Counts of rows and samples at all 73 places (arithmetic on the frames, after they exist) | 0.004 to 0.011 s | 0.011 to 0.017 s |
| (a) Candidate (P) at 39 places, whole recipe rebuilt, cold | 1.8 s (1.76 to 1.83) | 2.8 s (2.72 to 2.83) |
| (a) Candidate (I) at 69 places, whole recipe rebuilt, cold | 2.0 s (1.93 to 2.02) | 3.1 s (3.09 to 3.16) |
| (a) Candidate, warm (second look or Apply) | 0.06 to 0.09 s | 0.07 to 0.12 s |
| (a) ONE place only (step at `metadata_schema` T1, counts at `MLST_with_metadata` T2), building only that table and its ingredients, cold | 0.07 s (0.06 to 0.07) | 0.10 s (0.095 to 0.109) |
| (a) the same one place, before, stored | 0.004 s | 0.003 s |
| (b) First 100 rows at one place (`ST22_Anchor` T2; 617 rows, 6170 at 10x), before, cold / warm | 0.07 s / 0.004 s | 0.12 s / 0.005 s |
| (b) First 100 rows, after the candidate, cold / warm | 0.08 s / 0.003 s | 0.12 s / 0.005 s |
| (b) First 100 rows, after the step at all table places, cold | 0.08 s | 0.14 s |
| (c) Plot `qa_aggregated_no_key` (smallest: 9 rows), before / after | 0.19 s / 0.19 s | 0.19 s / 0.19 s |
| (c) Plot `virulence_bar` (617 rows, the slowest) , before / after (I) | 3.2 s / 1.1 s | 29.6 s (28.9 to 32.9) / 10.3 s (9.9 to 10.8) |
| (c) A mid plot (`qc_reads_horizontal_barplot`, 42 rows; 10x: 420), before / after | 0.5 s (0.46 to 0.84) / 0.27 s | 3.2 s / 1.2 s |
| (c) All 17 plots, before (sum) | 9.5 to 11.2 s | 45.1 to 47.9 s |
| (c) All 17 plots, after (I) (sum) | 6.2 to 6.6 s | 17.8 to 20.1 s |

Per-plot numbers are in `m1.json` / `m10.json` (`c_plot_before_s`, `c_plot_after_ids_all_places_s`). The "after" plots have fewer rows (the 28 Norway samples removed: 42 to 14 samples), so they draw faster; the sum "before + after" for a before/after view of all 17 plots is about 16 s at these data and about 65 s at 10 times the rows. The largest plot by rows (`virulence_bar` and `virulence_variants`, 617 each) differ: 3.2 s against 0.43 s, so the time follows the geometry the plot draws, not the number of rows alone.

What dominates (REASONED from the table):
- Tables: a fixed cost of about 1.7 s for the whole recipe (reading the tsv files, 20-odd actions, 28 tables); 10 times the rows add about 1 s. One table and its ingredients: below 0.1 s. Counts: below 0.02 s. The first 100 rows: below 0.15 s.
- Plots: drawing. Each plot costs 0.2 to 3 s here and up to 30 s at 10 times the rows (a point plot with 6170 rows); it grows with the rows drawn. Drawing all plots twice is the only operation that is not instant.
- So: counts, tables and the first rows are cheap at any size tried. Plots are the cost.

## 4. What "check the other plots and tables" could mean (facts per meaning, no recommendation)

(i) A count per place in the dialog (rows and entities before and after).
- Decided already: D-0093, `home_audit_steps.md:138, 143`, intent point 7; with D-0194 all places are ticked on opening. Also D-0203 (warn on a non-one-to-one value) and D-0197 (the ids of the view).
- Computed: the candidate step at every ticked place, then rows and samples at each place from the candidate frames. The stored "before" counts exist. 
- Cost: 1.8 to 2.0 s for the 73 places on these data (3 s at 10 times), counts themselves 0.01 s. One-off per candidate; changing a tick means a new candidate and about 2 s again (the key covers the whole recipe). A cheaper path for one place exists (0.07 s) but needs the candidate to be built only for the chain of that place; no code does this today (RAN on my own runner).
- State: a temporary copy of the audit recipe plus a trial entry (`home_stage2_mechanism_spec.md:130`, `home_audit_steps.md:78` "at most one trial entry"); the "N states" cache rule of line 224 is tagged [confirm].
- Risk: low; a number is read as a number. The count of a place whose column is missing needs the "no effect here" line (S6b of the model run found 4 places that the graph lists and nothing changes).

(ii) A preview of the table at a place the user clicks (the first 100 rows, before and after).
- Decided: not written; `home_audit_steps.md:79` says the column-drop dialog "previews the audit table without the column (view only)" for the drop kind; for the filter kind the only written preview is counts and the open plot. So a table preview exists in the text for a column drop, not for a row filter.
- Computed: the candidate table at that place (needs the candidate built, 0.07 s for one table, or the full candidate ~2 s if it is already built for the counts) plus its first 100 rows (0.08 to 0.14 s cold, 0.003 to 0.005 s warm).
- Cost: instant after the candidate exists.
- State: the candidate frames from (i); needs a display area inside or beside the dialog; two grids (before, after).
- Risk: medium. A table of the candidate looks like a table of HOME ("Data to show") and may be taken as saved; "Cancel changes nothing" must also remove it from view. A 100-row head can hide the removed rows (rows are removed anywhere in the table): fact, the head shows the top rows only.

(iii) A preview of an affected plot, before and after.
- Decided: the OPEN plot only (`home_stage2_mechanism_spec.md:130`: "a preview of the open plot"). A preview of other plots: not written. D-0194 says all candidate nodes are ticked "so it show clearly the extend"; this is about nodes and counts.
- Computed: the plot frame after the candidate (from (i)), then `VizFactory.render`, draw, PNG. The before image is not stored (I found no PNG store in `home_theater.py`; plots are drawn by `@render.plot`; not searched elsewhere), so the before is drawn again.
- Cost: one small plot 0.2 s, a slow plot 3 s (30 s at 10 times the rows), before and after together about double; all 17 plots before and after: about 16 s now, about 65 s at 10 times (RAN). Only the plots that change need drawing (71 of 73 places changed with (I), 14 of 17 plots in the earlier model run for the 21-id case); a plot whose table does not change need not be drawn (rule: "affected = the content of its T3 differs", `home_audit_steps.md:141` item 10).
- State: the candidate frames; rendering needs the plot specification and the factory; no write.
- Risk: medium to high. A preview picture next to the real plot looks like a saved result; the plot of the preview is the only place where the user sees the candidate in the same form as the figure that is exported. A draw error in the preview must show in its place, as for a plot in HOME.

(iv) The user leaves the dialog open (not a blocking modal) and walks through HOME, which shows the candidate result.
- Decided: the opposite, for the dialog: "modal" (`home_audit_steps.md:78`) and "the plots change only at Apply". The only non-blocking element written is the read-only per-node popup of line 138 (a pinned panel, "the mechanism is for stage 2"), which shows the recipe's steps, not the candidate.
- Computed: everything HOME shows (every table of Data to show, every plot, Compare) read from the candidate instead of the audit recipe. That is (iii) for all plots on demand, as the user walks, and (ii) for every table.
- Cost: each view the user opens costs what it costs now plus the candidate build (about 2 s once per candidate); each plot it draws 0.2 to 3 s (up to 30 s at 10 times). The user chooses which, so the cost is paid only for what he looks at. Nothing is computed in advance.
- State: a candidate view alongside the original and the audit views. `home_stage2_mechanism_spec.md` item 7 (View) defines two (original recipe for Exploration, audit copy for audit mode, Compare reads both) and a test that in audit mode no handler reads the original; 34 lines with `active_cfg` and 14 with `orchestrator.` in the HOME handlers (recount 2026-11-15, same file) would need to read a third thing. "Cancel changes nothing" then needs the candidate view dropped on Cancel, on closing, and on a change of recipe, data or tick; and the dialog must not be reachable from other workspaces. Today the candidate is in `_propagation_scratch`, which only the modal reads.
- Risk: the highest of the five: the candidate is shown in the same panels as the saved result; two states of the same plot on one screen (the audit one and the candidate one); a user who navigates and forgets that the step is not applied; HOME's own rule "My view / Result" labels (ADR-086) then need a third label. Also the user can change the selection in HOME while a candidate is open (exploration filter, tier toggle): the candidate and the view can disagree (fact of the design; not tested).

(v) The recipe overview with the places marked.
- Decided: the overview dialog exists in the plan (`home_stage2_mechanism_spec.md:73, 152` "the overview dialog", name N13 to confirm, built at the screen step P9, "NOT BUILT"). That the candidate's places are marked on it is not written.
- Computed: the list of ticked places and the counts of (i) placed on the recipe graph; no plot drawing.
- Cost: the same as (i) (about 2 s per candidate); the drawing of the graph is not measured (NOT RUN).
- State: the places and counts only; nothing else.
- Risk: low; it is information, like a count. It shows where, not what the plot looks like.

## 5. What state exists while the dialog is open, and what "Cancel changes nothing" requires (READ + REASONED)

- Today: `_propagation_scratch` holds the nodes between click and confirm (`filter_and_audit_handlers.py:686, 760`); the audit steps (`home_state`) and the preview filters (`applied_filters`) are not touched until confirm. The scratch is read only by the modal.
- Decided: one candidate; "changing it replaces the preview"; Cancel or closing discards it; the cache holds "at most one trial entry besides the real states" (`home_audit_steps.md:78`); nothing is computed twice because Apply adopts the trial by key (`home_stage2_mechanism_spec.md:130`, the reuse marked [MINE, for information]).
- For (i), (ii), (v): the trial entry plus counts; Cancel discards the entry. For (iii), (iv): the trial entry is also read by plot and table panels, so the entry must be tied to the dialog (dropped on Cancel and close) and must not be served after a change of the recipe, the data or the ticks: its key already contains the would-be step list (`home_audit_steps.md:222`), a changed tick is a new key (fact: the key covers the whole recipe; I did not re-run the key code).
- Memory: a 10 times larger candidate is 113 thousand rows in all tables; small. Not measured as bytes.

## 6. What I could not run or check

- No browser: I did not test whether a click on the page behind the modal is blocked (read: Bootstrap modal; reasoned) and I did not time the real Shiny `render.plot` path (I used `savefig` to a PNG in memory; the Shiny path adds an image transfer to the browser, not measured).
- The dialog of the new design does not exist; I measured the pieces it would use, on my own runner (forked recipe, real orchestrator and actions), not the audit orchestrator of the design (not built).
- Steps at a plot (T3) were simulated with the same action on the plot's table (the engine has no tier-3 reader).
- Data: recipe 1 is small (42 samples, at most 1731 rows in one table). Ten times the rows was made by repeating each file with sample ids suffixed `_r1` to `_r9` (the reference table was not repeated); it is not real data, and a join with a many-to-many key would grow faster than 10 times (not tried). One recipe only.
- The machine was shared (load 1.3 to 2.8 on 12 CPUs); three runs each; one process (Python and Polars caches warm after the first run; the first plot drawn in a process is slower, e.g. 0.84 s against 0.46 s).
- "Cold" means the stored parquet tables were absent; the operating system file cache was warm for the tsv files. A real first load after a reboot is not measured.
- The cache key code (`cache_keys.py`) was not re-read: the statement that a candidate rebuilds every table comes from the design text and from my measurement (a candidate at one place cost the full 1.8 s when all tables were read).
- Not measured: the number of plots the user would look at, a user test, the plot drawn at a screen size (dpi 100 here), several users at once.
