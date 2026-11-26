# Export modes: her statement of 2026-11-16 against the diagram, the records and the code

Task EXPORT-MODES-COMPARE-1. Read-only. HEAD `42118164`, branch `feat/recipe-format-1`.
Her statement is quoted as "relayed, 2026-11-16" (message M181 of `tmpAI/agent_channel.md`). It is not yet a ledger line.

Labels: **read** = I read it at file:line. **ran** = I ran it and saw the output. **reasoned** = my conclusion.

## 1. What the user gets in the zip today (ran)

I ran the real export generator (headless, no browser) on the shipped recipe `1_test_data_ST22_dummy`, scope global, 17 plots.
Driver: `tmpAI/panel/export_modes/run_four.py` (uses `tmpAI/panel/verification/scratch4b/drive.py`). The zips and their unpacked files are in `tmpAI/panel/export_modes/` (`x/<case>/`).
The audited case has three steps on the plot `mlst_bar`: keep two sources, drop the column `scheme`, remove one sequence type. Each has a reason.
"Box off" is the box "Also include a reproducibility/reimport bundle" unticked. "Box on" is ticked.

| Case | Entries in the zip (besides the plot pictures) |
|---|---|
| Explored only, box off | `<dataset>/T1_data.tsv` for 13 datasets, `T2_data.tsv` for 7 of them, `effective_run.yaml`, `lineage/lineage_graph.json`, `report.qmd`, `report.html`, `README.txt`. No recipe. No raw data. No `t3_steps.yaml`. 42 files with the pictures. |
| Explored only, box on | The same, plus `data_analysis_recipes_reproducibility/1_test_data_ST22_dummy.yaml` and `data_reproducibility/<12 raw files>`. 55 files. |
| Audited, box off | 44 files: the same as "explored, box off", plus `MLST_with_metadata/T3_data_mlst_bar.tsv` (the data of the audited plot) and `t3_steps.yaml` (steps with reasons and date). The report holds the Methods text and the audit table. No recipe. No raw data. |
| Audited, box on | 57 files: the same as "audited, box off", plus the recipe and the 12 raw files. |
| Audited, then all steps removed, box on (extra case) | Identical to "explored, box on". No `t3_steps.yaml`. The steps hash equals the explored one (`cee62b5e...`). So an empty audit is treated as exploration. |

What `effective_run.yaml` says (ran, same in all cases except two fields):
- recipe file-set hash, data batch hash, steps hash, engine fingerprint, git commit, software versions, the path of each data source, seeds per plot and per layer.
- It has no audit-recipe hash, no record hash, no key of each exported node, no hash of each data file (the diagram says it should). The tier keys are in `README.txt`, not in this file (read: `export_handlers.py:1327-1372`, ran).
- `t3_translation_skipped` says "not attempted - check 'Also include...'" with the box off and `{}` with the box on.

Form of the recipe with the box on (ran, compared with the loaded original):
- Explored: a full copy of the original recipe, written as one file with the `!include` files inlined and the comments lost. Its content is equal to the original (compared as data: equal).
- Audited: the same copy plus one new join `MLST_with_metadata__t3_mlst_bar` (the original join with the three steps added at the end of its `tier2`), and the plot `mlst_bar` repointed to it. Only `joins` and `analysis_groups` differ from the explored copy. The new join carries a comment that names the step ids only. The reasons are not in the recipe. They are in `t3_steps.yaml` and the report.
- Read: `t3_translator.py:213`, `export_handlers.py:1270-1285`.

A separate audit-steps file (`t3_steps.yaml`) is written when the plot has audit steps, or when a seed is pinned (a Reshuffle counts as an audit step), whatever the box (read: `export_handlers.py:1225-1256`, `plot_seeds.py:214-219`). With no step and no pin it is absent (ran).

There is no way to make a "Reproducibility only" zip. The box only adds to the Publication content (read: `export_handlers.py:1262-1266`, "Additive to everything above").

## 2. What the diagram `EXP-MODES` says

I could not see the picture. The StarUML tools are not available to me (no ToolSearch). I read the elements and the arrows from `docs/UML/app.mdj` (JSON, parsed). So I know the boxes, their text and the arrows. I do not know the layout or colours.

In five lines:
1. The user clicks Export Bundle. A decision "Mode selected?" has three arrows: Publication, Reproducibility, Both (recommended). Both = Publication and Reproducibility together.
2. Mode 1 Publication holds: `effective_run.yaml`, `report.qmd` (plots and Methods prose), `plots/`, `README.txt`.
3. Mode 2 Reproducibility holds: `effective_run.yaml`, `data_analysis_recipes_reproducibility/` ("frozen recipe, T3 baked in as real steps") and `data_reproducibility/` ("actual data files, copied"). No plots, no report.
4. `effective_run.yaml` is "ALWAYS written, identical content either way". It holds E, D, R (with file lists), AR, A, Rec, node keys (original and audit), file hashes, git commit, per-plot seeds, the skipped list (detail in the diagram DM-KEYS-EXPORT).
5. Two separate exports can be compared field by field. Import and Verify reads the recipe folder and the data folder, checks the legs, never blocks, and writes a NEW recipe and session.

Two things in the diagram file itself:
- The model holds three elements `TEST A`, `TEST B`, `TEST C` in the package `EXP-MODES` that are not on the diagram (read: no view of them). They look like leftovers.
- The diagram shows no data tables (`T1_data.tsv` and so on), no `t3_steps.yaml` and no `lineage/` in Publication. The code writes all three (ran).

## 3. What the records say, and what has been verified (read)

| Record | What it says about the export |
|---|---|
| Ledger `D-0005` (DECIDED, Eve, 2026-11-06) | "Export = Result + audited steps with reason; exploration never exported". |
| Ledger `D-0013` (DECIDED, Eve, 2026-11-09) | "Two export modes (standard; opt-in reproducibility bundle), `effective_run.yaml` always". The note says her 11-15 description of the two modes differs: open. |
| ADR-097 (`architecture_decisions.md:4806`, point 1; the #45 paragraph) | Mode 1 "never includes the recipe or raw data". Mode 1 holds `report.qmd`, `plots/`, `README.txt`, `t3_steps.yaml`. Mode 2 adds the frozen recipe and the data files, never plots or report. The two modes are "complements". Her words: "the point is for the user to provide evidence that its the same and where things come from". The ADR marks itself "to be amended by ADR-099". |
| `home_audit_steps.md:346` (decided 2026-11-12, Eve, P4b) | Audit mode, one bundle. One tick box "include recipe and raw data", off by default, with the sensitive-data warning. In audit mode the box adds the forked recipe and the raw data. Also: original plots beside affected audited plots; original T1/T2 labelled `original_`; audit tiers only where a step changed something; `exclusions.tsv`; attrition table; coverage check. |
| Ledger `D-0147` (DECIDED) | "In the export the user must be able to see the original and the modified plot." |
| Ledger `D-0148` (DECIDED) | "The audit export exports the audit recipe with the steps of the audit added to the recipe; the reason can be added as a # comment." A readable summary of the added steps is asked of agents (list "Asked, not decided"). |
| Ledger `D-0083` (DECIDED) | The final steps carry who and when. "an `audit_history_log` MAY be appended as a SEPARATE optional part, never mixed into the final steps; removed steps are not kept in the exported steps". This is the N7-2 line. |
| Ledger `D-0102`, `D-0135` (DECIDED) | Two recipes, original and audit. The audit recipe is a copy that only adds steps. "The export is that copy". A step the app cannot apply is refused, never skipped. |
| Ledger `D-0186` (DECIDED) | "Changing data is not necessarily a failure, but changing a recipe is." The use of several datasets with one recipe is asked, not decided (M175). |
| Intent document, point 11 and O1 | Answers "audit export = audit recipe". Open: does the results export without audit hold the `original_recipe`; the raw data files; one zip or two bundles. |
| `ui_implementation_contract.md` 7.2 | Out of date in places (lines 216-224, 234, 244): says `data_analysis_recipes/<proj>/` is in every bundle; the code writes none in the standard bundle (check 4b, verified). |
| `export_specification.md` | Also out of date: says all recipe files are always in the bundle (section 2, line 81). |
| `tmpAI/panel/verification/check_4b_export.md` | Verified as built on 2026-11-16 (ran): what is exported equals what is seen (23 rows = 23 = 23); the fork form is the older per-plot form (not the audit recipe of `D-0102`); a plot without a join is skipped and named in `effective_run.yaml`; Import checks two of four legs. I re-ran the four cases at HEAD. The files agree with that check. The code changed since only in text quoting. |

## 4. The table: each thing an export can hold

Cases: E = user only explored. A = user used audit. P = Publication. R = Reproducibility.
"S" = her statement. A cell marked **DIFFERS** is a cell where the code today does not do what her statement says (or what the diagram says). Numbers in square brackets point to section 5.

| Thing | S (her statement) | Diagram | Records | Code today (ran) |
|---|---|---|---|---|
| Plots | Not stated. | P only. | D-0147: audit export also shows the original plot beside the modified one. `home_audit_steps.md:346`: original plot only for plots really affected. | Always, in P (box on adds, never removes). Original plots beside audited plots: absent. **DIFFERS** from D-0147 (grep "original" in `export_handlers.py`: no code for it). |
| Data tables per tier | E-P and E-R: "the data that was used (the original tiers)". A-P and A-R: "the data, hashed". [Q2] | None in P, none in R. | Contract 7.2 rule 2-4: T1, T2, `T3_data_<plot>.tsv`. `home_audit_steps.md:346`: originals labelled `original_`, audit tiers where a step changed something. | T1 for every dataset, T2 when the dataset has tier-2 steps, `T3_data_<plot>.tsv` only for audited plots; in P and in R alike (`:1156-1218`). Not labelled `original_`. **DIFFERS** from the diagram (it shows no tables) and from `home_audit_steps.md:346`. |
| Recipe: which one | E-P and E-R: `original_recipe`. A-P and A-R: `audit_recipe`. [Q1] | R only: "frozen recipe, T3 baked in". | ADR-097 / D-0013: P never holds the recipe. D-0148: audit export holds the audit recipe. | R only (box on). E: copy of the original. A: copy of the original plus a forked join per audited plot (`:1270-1285`, `t3_translator.py:213`). **DIFFERS**: P has no recipe in E and in A. R in A is the fork form, not the audit recipe of D-0102. |
| Recipe: form and reasons | A: audit steps added, reason as `#` comment (D-0148). | "T3 baked in as real steps". | D-0102: the audit recipe is a copy with steps added in place, no join added. | One file, includes inlined, comments lost, written with `yaml.safe_dump` (`:1280`). Reasons not in the file. A comment names the step ids. **DIFFERS** from D-0148 (reasons) and D-0102 (no join added). |
| Audit-steps file (`t3_steps.yaml`) | E: none ("does not make sense"). A: not stated. [Q4] | Not shown. | ADR-097: in P. D-0148: a readable summary is open (list "Asked, not decided"). | Written iff the plot has audit steps or a pinned seed, at the zip root, whatever the box (`:1225-1256`). Absent for E (ran: 42 files with no `t3_steps.yaml`). Matches her E. |
| Audit history log (steps added and deleted) | A: optional, separate, for archive. | Not shown. | D-0083: optional, separate. | None. The event log is not built. **DIFFERS** (missing). |
| `effective_run.yaml` | "Data, hashed" in A-P and A-R. Names kept. | Always, identical in both modes. E, D, R, AR, A, Rec, node keys, file hashes. | ADR-097 point 3: four legs. | Always, identical (ran: only `generated` and `t3_translation_skipped` differ with the box). Holds R, D batch, A hash, E. Has no AR, Rec, node keys, per-file hashes. **DIFFERS** from the diagram. |
| Raw data copy | E-P and E-R: "the data that was used". A: "the data, hashed". [Q2] | R only. | `home_audit_steps.md:346`: behind the tick box, with the warning. ADR-097 point 8: a warning, no code rule. | R only (box on): the raw files named in `data_source_paths` (`:1281-1295`). Scope forced global. Not from "the dataset the user chose": the files of the recipe's sources. [Q7] |
| `report.qmd` and rendered report | Not stated. | P only. | Contract 7.2: Methods and audit trail. | Always. Has the Methods prose and the audit table when steps exist. |
| `README.txt` | Not stated. | P only. | - | Always. |
| `lineage/lineage_graph.json` | Not stated. | Not shown. | None found. | Always. |
| `exclusions.tsv`, attrition table, coverage check | Not stated. | `DM-KEYS-EXPORT` mentions the attrition table. | `home_audit_steps.md:346-347`. | None. Not built (audit mode stage 2). |

## 5. The cells that differ from her statement (one line each)

1. P holds no recipe in E and in A. Her statement says both modes export a recipe (`export_handlers.py:1270`, only under the box).
2. In E the code can give an original recipe only with the box (R). The file is under `data_analysis_recipes_reproducibility/` and it is a flattened copy without comments (ran).
3. In A the exported recipe is the old per-plot form: one extra join and the plot repointed (`t3_translator.py:213`; ran). It is not "the audit recipe with the steps added".
4. In A the reasons are not `#` comments in the recipe (`export_handlers.py:1280`, `yaml.safe_dump`; ran). `D-0148` asks for it.
5. In A a plot whose steps cannot be written as recipe steps is skipped and only named in `effective_run.yaml` (`export_handlers.py:1296-1311`; check 4b, ran with `3_test_no_joins`). Her statement and `D-0102` say it must not be skipped.
6. No audit history log exists (`D-0083`, her point 3).
7. There is one box, not a choice of mode. "Reproducibility only" cannot be made. The diagram has three choices (`export_handlers.py:574-593`).
8. `effective_run.yaml` has no audit-recipe hash, record hash, node keys or per-file hashes. The diagram says it holds them (read: `export_handlers.py:1327-1372`; ran).
9. No original plot beside the audited plot in the export (`D-0147`).
10. "Always the dataset the user actually worked with": the export takes the files of the recipe's sources (`orchestrator.get_source_files`, `export_handlers.py:120-126`). There is no choice of dataset in the app yet (`D-0186`, M175 open).
11. The tables in P: the diagram shows none, the code writes them in every export.

Cells that already agree with her statement:
- E has no audit-steps file (ran). A user who audited and then removed every step gets the same zip as one who only explored (ran, extra case).
- Exploration filters are never exported (`D-0005`; the export does not read `applied_filters`, check 4b).
- `effective_run.yaml` is the same in both modes.

## 6. What her statement does not settle (questions for her)

Each question has an example and the readings. A default is given only where a record supports one. A default is not a decision.

**Q1. In Publication, is the recipe inside the zip, or only named by its hash?**
Example: you export for your paper. A reader opens the zip.
- Reading A: the zip holds only the hash of the recipe (and of the data) in `effective_run.yaml`. The reader can check that a recipe someone gives them is the right one. The recipe file is only in Reproducibility.
- Reading B: the zip holds the recipe file (`original_recipe` or `audit_recipe`) in Publication too.
- What the records support: A. `D-0013`, ADR-097 ("Mode 1 never includes the recipe"), the diagram, and your words of 2026-11-09 "mode 1 - should not contain the recipe". Your words of 2026-11-15 "the recipe produced this with the data used" and your sentence 1 of today ("both modes use the audit_recipe and the data, hashed") can be read as A or as B.
- This reconsiders `D-0013` if the answer is B.

**Q2. What does "the data" mean in each mode?**
Example: the recipe reads 12 raw files. The export also writes tables after each step (T1, T2, and the audited T3 of a plot).
- Reading A: the tables of the tiers (what every zip holds today).
- Reading B: the raw files (today only in Reproducibility, behind the box, with the sensitive-data warning).
- Reading C: only the hash of the raw files, in `effective_run.yaml`.
- Your text for the explored user says "the data that was used (the original tiers)". "Tiers" points to A. Your text for the audit user says "the data, hashed". That points to C. The diagram shows B in Reproducibility only and nothing in Publication.
- If the raw files go in both modes, the sensitive-data stance of ADR-097 point 8 and your words of 2026-11-12 ("raw data can be sensitive") change.

**Q3. In Publication, with a scope of one plot or one group, which recipe is inside (if Q1 is B)?**
Example: you export only the plot `mlst_bar`.
- Reading A: always the whole recipe.
- Reading B: only what feeds that plot.
- Today the Reproducibility box forces the scope to global (`export_handlers.py:866`), because "you cannot partially reconstruct a recipe". The Publication zip has a scope choice.

**Q4. In the audit case, is there still a readable file of the steps (today `t3_steps.yaml`)?**
Example: three steps with reasons. The audit recipe holds them with the reasons as `#` comments. The report holds the Methods text.
- Reading A: no extra file. The recipe comments and the report are enough.
- Reading B: the file stays, as the readable list "as it sees them in the UI".
- This is the open point of `D-0148` (list "Asked, not decided"; agents are to give pros and cons). Your sentence "no audit-steps file when only explored" is already true in the code (ran).

**Q5. Which data tables are in the zip in the audit case?**
Example: you removed samples at two tables and filtered one plot.
- Reading A (`home_audit_steps.md:346`): the original T1/T2 labelled `original_`, the audit T1/T2/T3 only where a step changed something, each naming its original by hash.
- Reading B: as today (one T1, one T2, and `T3_data_<plot>.tsv` per audited plot).
- The original plot beside the modified one (`D-0147`) goes with A.

**Q6. Does a Reshuffle (a pinned seed) count as "used audit"?**
Example: the user only explored but pressed Reshuffle on one plot. The seed is pinned as an audit pin.
- Today the zip gets `t3_steps.yaml` and a different steps hash (read: `plot_seeds.py:214-219`; I did not run this exact case).
- Reading A: yes, it is an audit step, so the user is in the audit case.
- Reading B: no, it is part of the recipe's seeds (`D-0056`: every seed used is written in the recipe or the audit recipe), so the user is in the explored case.

**Q7. How does the export know "the dataset the user worked with"?**
Example: one recipe, three datasets on three days (M175).
- Today there is no dataset choice. The export takes the data source paths the orchestrator reports for the recipe.
- This depends on the proposals you asked for in M175 (sessions on different datasets). I suggest the answer waits for them.
- No default.

**Q8. On the screen: one box, or a choice of mode?**
- Reading A: keep the single box (today). Publication always, Reproducibility added by the box. "Reproducibility only" does not exist.
- Reading B: three choices as the diagram: Publication, Reproducibility, Both.
- Your words: "The names Publication and Reproducibility stay". The diagram shows B. `home_audit_steps.md:346` (2026-11-12) says one tick box.

**Q9. A user who audited and then removed every step.**
- Today (ran) the zip is identical to the explored zip. The record of the removed steps is not kept (`D-0083`: removed steps are not in the exported steps).
- If the optional history log is ticked, it would show the added and deleted steps. Is a log of "added and deleted, final list empty" wanted? Your point 3 says the log holds steps added and deleted, so I read: yes, offered. No other question here.

**Q10. What happens to Import (#48)?**
- Import reads a Reproducibility bundle and writes a NEW recipe and session. A Publication zip without a recipe cannot be imported (the box text says so, `:588-590`).
- If the recipe is in Publication (Q1 B), should a Publication zip be importable? Without raw files the data leg shows "not checked".

Settled by the records, no question: exploration filters are never exported (`D-0005`). The audit recipe is a copy with steps added in place (`D-0102`). Reasons can be `#` comments (`D-0148`). The log is separate and optional (`D-0083`).

## 7. What would have to change (not built; sizes are my estimate, reasoned)

**Large**
- Write the audit recipe as a copy with the steps in place, in the audit export. Replace the fork-and-repoint of `t3_translator.py`. A step that cannot be written is an error, not a skip. This is stage 2 of the audit redesign, not built. Today's code and tests (`libs/blueprint_arch/tests/test_t3_translator.py`, `test_export_download.py`, `test_bundle_importer.py`) follow the old form.
- The audit history log (needs the event log, not built).
- The keys of `DM-KEYS-EXPORT` in `effective_run.yaml`: AR, A, Rec, node keys, per-file hashes, attrition. Needs the key model of ADR-101 (not built).

**Medium**
- Write the reasons as `#` comments in the recipe. `yaml.safe_dump` cannot write comments, so a different writer is needed (`export_handlers.py:1280`).
- Put the recipe in Publication (if Q1 is B), with the scope rule of Q3, and give it one name for both modes (`original_recipe` / `audit_recipe`).
- A mode choice on the screen (if Q8 is B): three choices, a Reproducibility-only zip, and its README.
- Original plot beside the modified plot (`D-0147`) and `original_` labels (if Q5 is A).
- The rule "audit or explored": a function that says which case the user is in (Q6), used by the export and by the texts.
- Tests: one test per case of the four (zip entries and the recipe form), each with a mutation check (rules section 9). Existing tests that must change: `test_export_download.py`, `test_export_provenance.py`, `test_export_view_consistency.py`, `test_bundle_importer.py`, `test_t3_translator.py`.

**Small**
- Remove the stray elements `TEST A`, `TEST B`, `TEST C` from the diagram package.
- Texts that say the old thing: the box text and the docstring (`export_handlers.py:574-593`, `:777-790`), the README lines (`:1894-1912`), `docs/user_guide/understanding_your_export.qmd:12` ("This standard bundle never contains your data analysis recipe or your raw data files"), `t3_translation_skipped` "not attempted" text (`:1362-1365`).
- The ledger line for her statement (the review session's or a scribe's task).
- Records out of date already, whatever she answers: `export_specification.md` section 2, `ui_implementation_contract.md` 7.2 lines 216-244.

**Changes that touch a rule file or an ADR (her yes needed first)**
- ADR-097: point 1 and the #45 paragraph say "Mode 1 never includes the recipe". Her statement reconsiders this (Q1). Also `D-0013`.
- `home_audit_steps.md:346` (decided 2026-11-12, P4b): "one tick box 'include recipe and raw data', off by default". Her statement changes it in part (Q2, Q8). It is a design record, not a rule file, but she decided it.
- `ui_implementation_contract.md` 7.2 and 12f (rule file): bundle contents and the T3 audit trail. They need a rewrite when the build changes.
- `export_specification.md` (the design file for the export): needs a rewrite.
- The intent document points 11, O1, E12, E16: updated by her answers.
- UML: `EXP-MODES` and `DM-KEYS-EXPORT` (diagram change; the sync rule of `workspace_standard.md` applies; run `assets/scripts/audit_uml_model.py` after).

## 8. What I could not run or see

- The picture of `EXP-MODES`. No StarUML tools in this session. I read the JSON elements and arrows only.
- A real browser download. The runs used the real generator with a fake bootloader (as in check 4b).
- SVG and PDF plot files. I ran PNG only.
- The Quarto-rendered report was produced (`report.html` is in the zips). I did not open it.
- The case "Reshuffle only" (Q6) was read in code, not run.
- The audit case was run on a recipe that has a join (`1_test_data_ST22_dummy`). The case with no join (`3_test_no_joins`) was run in check 4b, not again.
- Import of a bundle: not re-run here (check 4b did).

## 9. Compliance

| Decision | How this work complies |
|---|---|
| D-0165: "Where no decision exists and one is needed, that must be reported to her." | Section 6 lists ten points that her statement and the records do not settle (Q1 to Q10). Each is reported with an example and the readings. None is decided here. Q1 and Q8 reconsider `D-0013` and `home_audit_steps.md:346`. They are flagged. |
| D-0101: "Everything she reads is written in short plain sentences, one idea each" | The report is in short sentences. The zip content comes first (section 1). Technical words are explained once. |
