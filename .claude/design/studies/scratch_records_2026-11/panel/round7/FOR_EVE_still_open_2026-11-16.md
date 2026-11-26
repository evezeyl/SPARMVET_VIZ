# What is still open for the app (2026-11-16, evening)

For Eve. Nothing was decided and no repository file was edited by the writer. Written for the review session (M176) by an agent that re-tagged every point of `tmpAI/panel/round7/FOR_EVE_one_list.md` and every question raised today. Checked against the ledger `.claude/knowledge/decision_ledger.md` (186 lines, D-0143 to D-0186 are today's) and the channel blocks M155 to M176 (review session) and M145 to M151 (coordinator). Branch `feat/recipe-format-1`, HEAD `42118164`.

**How to answer.** By the code in bold, for example "Pt3 (b)" or "Y11 Date". A point you do not answer stays open. A default is shown only where a record supports it, and the record is named; it is never a decision.

**Tags.** DECIDED: a ledger line taken by you says it (number and her words quoted). DISSOLVED: the question no longer exists because of a decision (number says which). CONFIRM: a decision exists and one word from you closes the point. OPEN: no record answers, or two records disagree.

---

## (a) The counts

**191 points** counted (5 merged duplicates are not counted). DECIDED 44, DISSOLVED 24, CONFIRM 40, OPEN 83 (counts updated 2026-11-16 after D-0187, D-0188, D-0192: Pt1 is DECIDED in part, see B1).

Blocking OPEN points (a build waits for them): see section (b). Count of OPEN that block: 23 (groups B2 to B13). Blocking CONFIRM points are marked in section (d).

**Per tag and per source of the point**

| Source | DECIDED | DISSOLVED | CONFIRM | OPEN | Total |
|---|---|---|---|---|---|
| list: yes/no (Y) | 7 | 5 | 14 | 8 | 34 |
| list: choose (Pt) | 2 | 0 | 2 | 44 | 48 |
| list: appendix A (AP) | 24 | 0 | 1 | 1 | 26 |
| new today | 11 | 19 | 23 | 30 | 83 |
| **all** | 44 | 24 | 40 | 83 | 191 |

**Per tag and per area**

| Area | DECIDED | DISSOLVED | CONFIRM | OPEN | Total |
|---|---|---|---|---|---|
| Recipe and data | 23 | 8 | 12 | 21 | 64 |
| Audit and export | 10 | 6 | 2 | 12 | 30 |
| HOME screens | 3 | 1 | 3 | 12 | 19 |
| Visualisation and names | 2 | 1 | 4 | 7 | 14 |
| Gallery | 2 | 1 | 0 | 2 | 5 |
| Blueprint | 1 | 1 | 0 | 6 | 8 |
| Rules and records | 2 | 1 | 16 | 20 | 39 |
| Process | 1 | 5 | 3 | 3 | 12 |

**Merged duplicates** (one entry kept, the other not counted): PF4 into Pt8 (thresholds); PF6 into Pt48 (hits or samples); I7 (intent O7) into PF7; V1.3 into Y11 (dates); V6.1 into E4 (one-line fix). Also folded into one point without their own row: batch 4a q2 and q3, batch 6/7 q2, batch 8 q1 into Pt37 (seed); batch 4b q1 into Pt1; batch 4b q2 into Y8; batch 8 q3 into Y34; batch 8 q9 and batch 5 q2 into V5.2; batch 3 q6 into V1.4; M147 points 2 to 5, the hook question of M150 and M171 D into C8; Y30 and batch 6/7 q3 into E1 to E15; intent O1 into Pt1, O2 into Pt5, O3 into Pt3, O4 into Pt2, O5 into Pt6, O6 into Pt42 to Pt47, O8 into Pt4, O11 into AP1; ledger A01 into Pt37, A10 into AP19, A11 into Pt44/Pt45, A12 into Pt16, A17 into Pt1. Not questions (no row): the helper scripts that now need the project path (M147 section 4); the points the one list already marked answered.

---

## (b) OPEN points that BLOCK a build

Each says what waits. "Records" names what I read. A default is given only where a record supports one.

### B1. What the results export holds (Pt1). DECIDED in part (2026-11-16): D-0187, D-0188, D-0192. The tick is still open (see below).
- Decided: D-0187 "If the user has used audit, both mode 1 and mode 2 must use the audit recipe and the data, hashed." D-0188 "mode 1 and mode 2 export the original recipe and the data that was used (the original tiers)" when only explored. D-0192 "The recipe is added to the reproducibility mode 2, and removed from mode 1" (the audit points file can stay in mode 1).
- Not answered by these lines: whether the raw data sits behind a tick (readings A, B, C below); where the data used is chosen (a) or (b). D-0192 refines D-0013 (it does not replace it on the tick).
- Still open after her answer: see `tmpAI/panel/export_modes/export_modes_compare.md` and channel message M153 (five points).
- Example: a user exports the results of recipe 1 with no audit. Today the zip holds the plots, the audit steps with their reasons and `effective_run.yaml` (hashes and paths of the recipe and the data). The recipe file and the raw data are inside only when the box "recipe and raw data" is ticked (off by default).
- Already decided and not asked: the audit export holds the audit_recipe with the steps added (D-0148 "the audit export export the audit recipe with the step of the audit added to the recipe"); the original and the modified plot can be seen in the export (D-0147).
- The question is the export without audit. Readings: (A) as recorded: the recipe file and the raw data together behind one tick, off by default. (B) The recipe file is always in; the tick holds only the raw data (changes ADR-097 point 1 and the decision P4b of 2026-11-12). (C) Two ticks, one for the recipe file and one for the raw data. Second part: where the data used is chosen: (a) when the data is loaded in HOME, the export only names it; (b) in the export box (in no record).
- Earlier, before her answer: D-0013 (ADR-097, 2026-11-09, mode 1 never holds the recipe) and P4b said (A). Her words of 2026-11-15 said the export holds "the recipe that produced them, with the data used". Ledger A17: "Q3 NOT decided". Two older texts (`export_specification.md:81`, `ui_implementation_contract.md:220`) show the opposite of ADR-097. D-0192 now replaces the recipe part of this.
- Default: none for the tick.

### B2. CLOSED 2026-11-16 (D-0197): which sample ids "remove these samples from all tables" uses (Pt2). The first wording ("you tick `country = Norway` at the MLST data file") was wrong: that file has no `country` column, so nothing can be selected there (D-0196).
- Example (recipe 1): you look at `MLST_with_metadata`: 28 Norway samples at T1, 21 at T2 (the recipe's own year filter removed the 7 of 2022). You select Norway there and choose "remove these samples from all tables". Tables with no `country` column get the step as a list of sample ids.
- Decided (D-0197): the ids are those of the view where the selection was made: "if you apply the T1 then you will have 28, eg if you apply in T2 there will be 21 due to the other events in between"; "you need to do that as early as possible in the lineage".
- Run (scenarios S3): with the 21 ids the 7 samples stay in 66 of 73 places and in 14 of 17 plots; with the 28 ids nowhere.
- Open: nothing about the ids. The dialog and help text is a draft in `tmpAI/panel/audit_model/scenarios_report.md`.

### B3. What is ticked when the audit dialog opens (Pt3). Waits: the audit screen.
- Example: ticking the metadata file by a property changes 14 of the 28 tables. With everything ticked, one Apply writes the step at all 14.
- Readings: (A) all candidate nodes ticked, you untick; (B) only the node you chose is ticked, and "remove these samples from all tables" ticks every table with the ID; (C) nothing ticked, Apply stays off until you tick one.
- Records disagree: `home_audit_steps.md:134` (all ticked) and `:138` (only the place the user chose; "Nothing is written that is not ticked"). D-0144: you confirmed point 6 of the first page and said "we can start with that" and the default "may change after use"; the document does not name the default.
- Default: none supported.

### B4. A typed value that does not fit one ticked node (Pt4). Waits: the audit screen.
- Example: you write `Year = 2022` where `Year` is a number. A later table holds `Year` as text (2 of 43 recipes that build). There the value is refused: "the value 2022 is a number, but this column holds text".
- Readings: (a) that line shows the error and cannot be ticked, the other nodes can be written; (b) only nodes whose column has the same type are offered; (c) drop the rule.
- Records: D-0175 (a filter is created only in a view whose table has the column); D-0176 (a plain message). Your doubt "I do not see how this is possible" (`tasks.md:396`) is not a ledger line. Intent document O8: not decided.
- Default: none supported (the stage-2 spec default (a) is the writer's).

### B5. When the audit_recipe file is created (Pt5). Waits: the audit screen.
- Readings: (a) at the first audit step, before that HOME reads the original_recipe; (b) when audit mode is switched on; (c) at session start.
- Records: D-0143 and D-0102 say what the audit_recipe is, not when it first exists. M176 says: ASK, not decided.
- Default: none.

### B6. The screen words for the two plots and tables (Pt6). Waits: the audit screen.
- Today the screen says "Result" and "My view". D-0179 "There is not my view anymore in the refactor" removes "My view" as a choice. D-0180: in exploration there is one plot, the result.
- Readings: (a) "Result (original recipe)" and "Audited (audit recipe)"; (c) words of yours.
- Records: the recipe names are decided (D-0143); the screen words are in no record (`home_audit_steps.md:81` holds "Result" in a notice only).
- Default: none.

### B7. The recipe fixes (branch `task/recipe-fixes`, ResFinder and PlasmidFinder recipes). Waits: the final form of the fixed recipes (the fixes are built on provisional defaults and shown to you as pictures).
- **Pt7, the multi-resistance flag.** M176 says point 7 is decided. D-0172 decides only one part: a MISSING phenotype is not counted ("missing here means that no resistance phenotype has been detected"). What is still open: 13 of the 70 hits have a phenotype written `unknown[...]`, each counted as its own class, and the formula counts drugs, not classes (sample 11843673 with gentamicin and spectinomycin, both aminoglycosides, is "Yes"). Your definition of 2026-04-23: "resistant to more than one class". Readings: (a) keep as today (16 of 38 samples) and say so in the plot title; (b) leave "unknown" out (11 samples; 5 change from Yes to No); (c) count classes through the drug-to-class table (10 samples; the table lacks kanamycin and sulfisoxazole). If (c): the column "Predicted Phenotype" (used today) or "CGE Predicted Phenotype". Default: none supported.
- **Pt8, thresholds of the ResFinder rule.** D-0087 says filter below the minimum identity and coverage, "old thresholds verified". The history holds two pairs: identity 90 and overlap 60 (63 rows after one per sample and gene, 60 in the final table); or identity 90, overlap 85 and length ratio 0.8 (34 of 70 hits go, 16 of 38 samples lose every hit). PlasmidFinder has the same question (cut 90/60; the web service default is 95/60). Built on identity 90 / overlap 60, marked provisional. Default: none supported (two pairs found, no source).
- **Pt9, "one row per sample and gene" for the AMR join of `2_test_data_ST22_dummy`.** 70 rows would become 63; multi-resistant samples 16 to 15. D-0110 decides that recipe 2 is merged into recipe 1 or removed (and D-0132: the list is shown to you first), so this answer depends on that outcome. Readings: (a) only the converted piece; (b) both. Default: none.
- **Pt10, the FastP box plot.** The old plot draws one box per sample but the table has one row per sample, so every box holds one value. D-0086 says wire the fragments. Readings: (a) wire it by source (Broiler 13, Layer 19, Parent 10 samples), which changes the old intent; (b) leave it unwired and archive it; (c) you say what it should show. Default: none supported.

### B8. The rename of all plot components (Pt11 to Pt15). Waits: the whole rename (535 files, 5185 places; starts only after you have seen the impact document, `tasks.md:387`). Read `.claude/design/viz_rename_impact_2026-11-15.md` sections 1 and 2 first.
- Pt12: names written as values (`geom: geom_area`): they stay plotnine's names, or get the prefix. Pt13: the 15 plotnine objects that cannot be added to a plot (`element_*`, `position_*`, `guide_legend`): only `modif_<name>`, or also as a parameter of the component that takes them. Pt14: `guide_label` fails on every use: remove, rebuild on plotnine's own means, or keep renamed. Records disagree: `tasks.md:312` ("your choice: rebuild or remove") and `:447` ("fixed and tested"). Pt15: the 21 facet and guide conveniences: keep all as `step_`, remove the 9 that an exact component does, or fold the four facet setters into parameters.
- Pt11 (CONFIRM, listed in (d)), Y10 and Y26 (CONFIRM) belong to the same block.
- Records: D-0091 (new names, "price of transparency and reproducibility"). No record speaks of Pt12 to Pt15. Default: none supported.

### B9. A mean with an error bar per group (Pt16). Waits: the `stat_summary` work (`tasks.md:388`).
- Example: `n50` of 42 samples by country (Norway 28, France 4, Germany 10). Plotnine's `stat_summary` takes three functions; a recipe cannot write a function. Readings: (a) not offered; the user builds the numbers with table steps (mean, standard deviation, standard error) and the gallery and help show it; (b) named summaries as a `modif_stat_summary`; (c) both. The built-in `mean_se` divides by n, not n minus 1 (the bar is 13 percent narrower with 4 samples).
- Records: ledger A12 "N28 NOT decided"; the advices for `mean_se` and for a missing `fun_data` are decided (D-0067). Default: none supported (the coordinator's standing default (a), M99 (40), is not a record of yours).

### B10. The old words (Pt17 to Pt22; Y14, Y15 are in (c) and (d)). Waits: the change of the old-words check and the clean-up of old words; nothing is applied before you have seen the exclusions (`tmpAI/panel/round7/old_words/replacements.md` sections B and C).
- D-0069 decides that old words are corrected everywhere active, not in history. What is not decided: Pt17 "audit node" and `node_type`; Pt18 the words for the reach of an audit step ("every plot in the project"; ADR-105 replaced the reach levels); Pt19 how far "assembly" is renamed; Pt20 `WrangleStudio` in the code (D-0048 puts Blueprint last); Pt21 the title "Pipeline Audit"; Pt22 the form of the check (narrow, wide or both). Default: none supported.

### B11. The Blueprint AI helper at start (Y13). Waits: any fix (`tasks.md:435`: nothing is built before your answer).
- Today, with the helper on (the developer setting only), the start can wait up to 40 seconds if the `claude` command hangs, with no message. ADR-076 (`architecture_decisions.md:2948`) says "Startup is never blocked by an agent misconfiguration". Readings: (1) never blocked means the app always starts (today's code follows it); (2) the start must not wait for the helper, so the check runs in the background.
- Records: no ledger line and no channel block. M176 lists Y13 as changed today, but I found no record that answers it. Default: none.

### B12. The exploration filter reset when the user goes to another table (C13). Waits: the build of the reset; M147 point 1 says nothing is built before you confirm the list in `h1_filter_view_change.md` section 8.
- Example (recipe 1, table `QA_AMR_per_sample`): the filter `gene = blaTEM-1C` is built on T1 (it has `gene`, 74 rows). You look at T2 (no `gene`, 42 rows): today the filter is still listed, the badge says "1 filter on", all 42 rows show and nothing is said.
- D-0177 and D-0178 decide the reset at a change of view. Open: when you go to a plot of ANOTHER table at the same stage, is that a change of view? Readings: (a) yes, any change of the table shown resets the filter; (b) no, only a stage change resets; on the other table the filter stays with a notice "gene is not in this table, the filter is not applied here". The coordinator found no default. Related one-word points in (d): C14 (build now or wait for stage 2) and C15 (the notice).

### B13. The Export panel when the user changes plot tab (C17). Waits: the fix of the Export panel (the coordinator's M151).
- Example: the user opens the Export panel and ticks "Also include a reproducibility/reimport bundle", types a bundle name, then clicks another plot tab. The panel is drawn again with its defaults: the box is unticked and the name is gone. The download then has no reproducibility recipe and nothing on the screen says so. Verified by the coordinator's worker (a probe, deterministic).
- Readings: (a) keep everything the user set; only the choice "active plot / active group / all" follows the tab; (b) reset to the defaults and say so in a notice.
- Records: no decision. D-0050 "No silent error that is the rule" and D-0108 ("not to make choices for the user") support (a). The coordinator's default is (a). Not a decision.

---

## (c) The other OPEN points, by area

For the readings and the example of a point from the list, open `tmpAI/panel/round7/FOR_EVE_one_list.md` at the same code (Pt = point, Y = yes/no). Points new today have their source in the line.

### Recipe and data (17)

- **Y34** derive_categories stays removed. Records: D-0038 is PROVISIONAL (an agent's remark, not hers); D-0037 (Polars only) does not name it. Built (d63d3f3d). Same as batch 8 question 3.
- **Pt29** A Date with no 'format': require it, advise, or leave. Records: recipe_format_spec.md:370 says format is optional; no ledger line.
- **Pt30** A cell that holds only spaces: always missing, or an empty text. Records: The coordinator asked it on 2026-11-15 (channel :419); no ledger line answers.
- **Pt31** quality_module (Passed, Warning): is there a 'Failed'. Records: D-0098 (nominal become String; ordered become Enum) needs the full list of verdicts, which is in no file.
- **Pt32** 'year' in the retest recipe: String, Enum or Int64. Records: D-0098 does not weigh the three; no record.
- **Pt33** 'status' in the audit template: String or Enum. Records: No data file in the repository; no record.
- **Pt34** The plotted table of the stress plot writes '2023-04-11 00:00:00' with Date. Records: Only matters if Y11 says Date; no record.
- **Pt48** The three figshare plots (and the PlasmidFinder plots) count rows (hits), not samples. Records: tasks.md RECIPE-SCIENCE-1 pending; no ledger line. Merged: PlasmidFinder point 6.
- **PF5** A sample with no replicon hit counts as 'no replicon found' in the group size. Records: No record; only she knows whether the pipeline writes a row for a plasmid-free isolate.
- **PF7** The plot's own filter before the tier-3 reader exists (plot filters / two collections / wait). Records: D-0115 "so 2 plots that can furk on the same t1 or t2 so 2 t3"; D-0133 'T3 only for what one plot alone needs'; the reader is not built (D-0150). Merged: intent document O7 (spec-level filters vs steps.tier3, 'recommended, awaiting Eve').
- **PF9** The overlap column in the dummy PlasmidFinder file is not trustworthy (values above 100). Records: No record; information, no plot uses it.
- **V1.2** Batch 1 q2: correct the words 'SHA256 of wrangling steps' in the report now, or wait for the task that retires the old key name. Records: No record (default: correct now).
- **V2.2** Batch 2 q2: an Excel upload writes the checked table as a tab-separated file instead of copying the Excel file. Records: No record (default: yes). Related D-0045 (imported data by dataset id).
- **V3.1b** Batch 3 q1: a join that MULTIPLIES rows is told nowhere. Records: No record covers it (4 rows became 7 in the run); default yes, a warning never a block.
- **V3.2** Batch 3 q2: the self-join warning with row numbers shown after the run, or from the data check. Records: D-0078 and D-0183 decide the warning; the moment is not decided.
- **V3.5** Batch 3 q5: keep refusing a 32-bit against a 64-bit whole-number key although Polars joins them. Records: D-0044 (types the recipe declares, no hidden cast) and D-0065 (one join-key rule) support refusing; D-0183 "no error in polars then no error for us" (said for self-joins) points the other way.
- **L5** M141: a warning at run time when a ResFinder tie is found. Records: D-0111 evidence: 'proposed, not built before she agrees'.

### Audit and export (7)

- **Y27** Until the audit copy exists, today's optional export recipe keeps the name 'forked recipe'. Records: D-0143 names the two recipes original_recipe and audit_recipe; no record on the interim name for today's code.
- **Pt36** A short pop-up when the open recipe is replaced. Records: No record; D-0149 "warn only when problem" and D-0186 "changing a recipe is" a failure bear on it.
- **Pt42** When the recipe changes while a view is open: keep what was opened until Reload, or follow at once. Records: D-0186 "changing a recipe is" a failure; D-0088 (export refused until the user re-bases); D-0184 evidence lists a check of a changed recipe within seconds (the review session's list, not hers). None says what HOME shows.
- **Pt43** Data files: watched every 2 seconds, or only the warning at the next click and the refusal at export. Records: D-0186 "changing data is not necessary a failure"; M175 asks for proposals on datasets. Merged with the sessions proposal.
- **Pt46** Two users on one app and one user-data folder: supported or not. Records: No record.
- **AP1** 'Undo last', 'Revert to step N' and 'Remove all' in the audit panel. Records: Records disagree: spaces/HOME.md:124 and home_audit_steps.md:164, :327-328 list three controls; the intent document (O11) quotes her 'the unto is the remove step button' (T92 L11773). D-0102 only says a step added in the audit can be removed again.
- **V4b.4** Batch 4b q4: a restore of a session made for other keys (another recipe version or data): needs a click, and the saved record keeps the old keys. Records: No record; merged into the sessions proposal (M175).

### HOME screens (10)

- **Y17** True/false offers only 'equal' and 'not equal'. Records: D-0054 "All required operators will need to be wired in the screens" and D-0061 "every type must be usable" point to offering all; the agent's built choice offers two. No record says that two operators are enough.
- **Y18** Time of day and duration: comparisons and 'between', no list 'one of'. Records: Same records as Y17 (D-0054, D-0061); no record on this case.
- **Y20** A filter 'one of' with an empty list. Records: No record. Nearest: D-0060 (empty select/unpivot/top_k parameters are refused). This step can be applied, but it removes every row.
- **Pt23** The list of values served on demand above 1000 values. Records: No record; D-0117 asks to reuse what was good in the earlier UI.
- **Pt24** A time of day: three number boxes, one native input, or one text box. Records: No record.
- **Pt25** A duration: number box and 8 units, fewer units, or one text box. Records: No record.
- **Pt26** A date and time: date picker plus time boxes, one text box, or a zone choice. Records: No record.
- **Pt27** The starting values of the filter boxes (smallest value, empty, or zero). Records: No record. Principle D-0108 'not to make choices for the user' and D-0015 (the software informs, the user decides) bear on it.
- **Pt28** The date box: strict typed text with a calendar for the mouse, or plain text box, or refuse 2023-2-8 too. Records: D-0050 "No silent error" (no repair of free text) is decided; the form of the box is not.
- **L4** Ledger A14: which audit signals could be an error; thresholds, how to count 'diverse' steps. Records: D-0095 decides warnings not blocks; thresholds 'asked, not decided'.

### Visualisation and names (2)

- **Pt35** Names for label and rescale functions (percent, comma, censor, squish). Records: No record; D-0030 limits formulas to an allowed list.
- **PF2** Heatmap colour: share of the group's samples, or count. Records: D-0114 gives the two heatmaps, not the colour. The report's default (share) is the agent's.

### Gallery (2)

- **V5.5** Batch 5 q5: the 8 changed gallery pictures (7 changed size 800x600 to 960x600, jitter_strip differs in 2.6 percent of pixels): keep, or put the old ones back. Records: No record that she looked at them; the jitter change is allowed by D-0056.
- **L3** Ledger A07: gallery G-b 'filters' read as interaction; one plain sentence is owed. Records: NOT decided.

### Blueprint (5)

- **Pt44** Blueprint tells the person who saves that n views of the recipe are open. Records: No record (A11: investigation, no build).
- **Pt45** Confirm: Blueprint's save is never blocked. Records: No record (A11).
- **C12** M147 section 4: a failing step of a dataset the recipe does not use: does it make the recipe fail when selected. Records: D-0184 moves the check to selection; no record on this detail (the coordinator's default was: yes, name the dataset).
- **V8.5** Batch 8 q5: 'Create plot' in Blueprint: may an empty draft plot exist, or must Blueprint ask for table and columns first. Records: No record (default: ask first).
- **L1** Ledger A05: Blueprint must be able to open a recipe that fails, each failing point shown as a point to fix. Records: her design wish; 'investigate, no build yet'; no proposal file found.

### Rules and records (14)

- **Y15** The word 'persona' for the review method (viewpoints of the panel agents). Records: No ledger line. ADR-091 point 5 retired the word for the app configuration only. She uses it herself. Linked: edit E10 (is the persona review file wanted at all).
- **Y29** Change the four docs pages that teach the old picture now. Records: No record says when. The four rule-file rows (R092, R112, R113, R122) need her yes (D-0104).
- **Pt38** A type-only import between libraries (rules_runtime_environment.md:79 and rules_test_lab.md:58). Records: No record says whether the stricter line is on purpose.
- **Pt39** Who defined the 'step compiler'. Records: D-0028 is NOT-STATED (no decision of hers found).
- **Pt40** Who set the rule 'a build on an agent's recommendation is PROVISIONAL'. Records: D-0107 is NOT-STATED (tasks.md:21 says Eve 2026-11-15; her turns hold no such sentence).
- **Pt41** 'column' or 'columns' for the input column of modif_ and step_ actions. Records: Two ledger lines disagree: D-0034 (DEC15 `columns`) and D-0036 (DEC39 `column`), both dated 2026-11-13. Code and recipes use `column`.
- **E1** Do you accept the parts marked [ADDED] in decision_compliance.md (table, ledger description, block syntax). Records: edit f1f70353; D-0125 covers her text only; the file says so itself.
- **E2** Should the hook accept NONE-CHECKED only for a regular file inside the project, not the ledger. Records: edit ee4f1eac; D-0155 does not ask for it.
- **E7** Automatic audits paused until the refactor is finished (banner in two workflow files). Records: edit 16d52140; tasks.md:204 says '(Eve ...)'; no ledger line.
- **E8** retest_procedure.md as a permanent workflow file. Records: edit 19285129; no ledger line.
- **E9** Run dates of audits in audit_routine_registry.md (next dates now wrong). Records: edit e3865b59; small; no decision.
- **E10** design_review_personas.md as a permanent workflow file. Records: edit 4ba10ba9; only the 'never guess' line is hers (D-0017).
- **E12** ui_implementation_contract.md line 422 (Test Lab right panel reachable): may a rule file describe the code state without her yes. Records: edit 143ae2d4; no decision.
- **L6** M148 point 4: put the intent document first in the reading list of every agent (CLAUDE.md section 3, agent_principles.md). Records: a proposal; D-0104 needs her yes to rule-file text.

### Process (3)

- **C8** M147 points 2 to 5, M150, M171 D: the hook asks for a quote of 12+ characters; simplify to 'decided number plus any quoted piece', or keep as built. Records: D-0166 option C ("each decision number is followed by quoted words that appear in that ledger line") is decided; the 12 and 4 minimums, quotation marks, short quotes and fields are the builder's. Her question 'do we need to be so stringent?' is in the ledger list 'Asked, not decided'. The coordinator's recommendation: simplify. The coordinator stopped all tuning until she answers.
- **L2** Ledger A06: an explanation list of the results that changed under the new rules is owed. Records: no file found.
- **L7** M137: add a step 8 to the repository audit (logic and coherence of the whole). Records: a task request, not a decision.

---

## (d) CONFIRM points: one word from you

A decision exists. The agent's wording or choice needs one word. Points marked [blocks] hold a build.

- **Y10** [blocks the plot rename] Register 30 of the 35 missing plotnine objects. one word: register the 30 (the later wish), or only list what is missing (ADR-106 point 9). (Record: D-0051 "honest parity list, both spellings"; D-0091 "the registry audit comes first". The wish 'verify that ALL are registered' is M106 (57), not a ledger line..)
- **Y11** [blocks the migration of the date fields] The two date fields: Date, or drop the columns. one word: Date or drop (blocks the migration of the date fields). (Record: D-0098 "dates become Date (or the columns are dropped if no recipe uses them)". No shipped recipe uses them, so the literal reading is drop; the data scientist advises Date (dropping moves the golden hashes).)
- **Y14** The word 'profile' for the checker's four modes. one word: keep 'profile' for the checker, or rename (for example 'check mode'). (Record: D-0034 "profiles run/build/gallery/audit" (DEC13-26, her date column). Against it: 2026-11-07 she called the word ambiguous for the deployment (D-0006 names). No turn of hers on the checker's use was found.)
- **Y16** The settings names pipeline-* stay. one word: keep the prefix pipeline-. (Record: Two records: tasks.md:198 (2026-11-08, find a new name) and tasks.md:196 (2026-11-12, her words `92f68895` turn 8673, rename to pipeline-simple-exploration, keep the prefix). The later holds; there is no ledger line.)
- **Y19** A value finer than the column is refused, never cut. one word: refuse (as built), or round and say so. (Record: D-0050 "No silent error that is the rule"; D-0039 (DEC49: a cast that loses decimals fails). The choice 'refuse' or 'round and say so' is not in a record.)
- **Y23** NI stays on the figshare scale Enum [S, I, R, NI]. one word: keep NI on the scale or not. (Record: D-0098 "categories whose order has a meaning become Enum with the order written in the recipe"; the list S, I, R, NI is M119 (57). No file defines NI.)
- **Y24** The stress 'value' is Float64. one word: Float64 or Decimal with two decimals. (Record: D-0098 "the `value` of the stress recipe is corrected"; the type Float64 (or Decimal) is the agent's choice.)
- **Y25** The documented Categorical example is 'breakpoint'. one word: breakpoint, or another field. (Record: D-0098 "one documented `Categorical` example may stay"; the field breakpoint is the agent's choice.)
- **Y26** [blocks the plot rename] Put the plot-name prefix rule into rules_viz_factory.md. one word: yes to writing the rule text (after she has seen the document). (Record: D-0091 decides the prefixes; D-0104 "No rule is changed without me agreed".)
- **Y28** A one-line note on the three contradicted diagrams and one small new diagram 'two recipes'. one word: yes to the notes and the new diagram. (Record: D-0071 covers only the six arrows of PKG-TIERS ("star uml is open - fix"); the review session released the other UML tasks in M180 (a relay, not hers). D-0012 (UML sync) applies.)
- **Y30** Seven rule-file edits of 2026-11-14/15 stay as they are. one word per row: yes or no. (Record: D-0173 "investigate that then present the list"; the list is ready (rule_edits_and_action_names.md); merged with the 15 edits E1 to E15 below.)
- **Y31** Correct the sentence that says an emoji scan is 'active now'. one word: correct the sentence, build no scan. (Record: D-0073 "if unsure verify and ask" (rule files follow the code); D-0104 needs her yes to the text.)
- **Y32** Rewrite three checker ERROR texts as 'what is wrong, then Suggestion:'. one word: yes. (Record: D-0099 covers advice texts ("Suggestion: To always ..."); the three are error texts.)
- **Y33** The advice texts as built. one word: keep the texts (side by side in advice_texts_before_after.md). (Record: D-0099 decides the form; the words are the agent's (PROVISIONAL in tasks.md). One text (ST15) has an added remedy (Float64).)
- **Pt11** [blocks] Names plotnine does not have (22): prefix step_ or modif_. one word: step_ for all 22 (default (a)), or modif_ for the one-call conveniences. (Record: D-0036 (DEC31-42: step_ is the project's own) and D-0091 "a composite is `step_<name>`"; the 22 are not all composites.)
- **Pt37** The seed mechanism built provisionally (null refused; seed for the whole recipe; audit pin with 'Reshuffle'). one word: keep as built, remove the audit pin, or build the per-step seed field. (Record: D-0056 "Fixed 0 by default fixed and simple" and "every seed that is used is written in the recipe or the audit recipe"; the three built parts are the agent's (PROVISIONAL). A01 (a special seed field per jitter step) has no answer. The plot rule file still says null = new each time (D-0004, replaced in part by D-0056). Merged: batch 4a Q2 and Q3, batch 6/7 Q2, batch 8 Q1.)
- **AP19** Reading captures Polars and type errors in one error form. one word: yes to the one error form (file, column, number of bad cells, first 3 lines). (Record: Ledger 'Asked, not decided' A10: she wants Polars and type errors captured at reading (M101: 'the most important thing'), not a numbered decision; D-0176 is for a missing column only.)
- **PF1** Merge recipe 2 (2_test_data_ST22_dummy) into recipe 1, or remove it. one word: the merge list (result.md section 3.4). (Record: D-0110 "can be merged with 1_test_data_ST22_dummy it it adds something otherwise remove"; D-0132 "Nothing is removed before the merge or removal list is shown to her". D-0172 keeps the multi-resistance change, so the flag is wanted. The report recommends merge, then remove.)
- **PF3** Best hit per sample and type in the PlasmidFinder table (150 rows, tie = lowest accession). one word: yes, same rule. (Record: D-0087 and D-0111 decide the rule for AMR genes; extension to plasmid types is the agent's.)
- **PF8** Regenerate the golden baseline (7 new entries) after she has seen the pictures. one word: yes after the pictures. (Record: D-0132 "any decision about the golden baseline" is shown to her first.)
- **C2** M145: the handoff is 'append, do not delete'; M157 says done items are removed or archived. one word: done items are moved to an archive file, never deleted. (Record: D-0160 "keep precise and upated"; the 'archived means moved' sentence is marked ADDED by an agent in CLAUDE.md.)
- **C3** M145: CLAUDE.md 'one-screen state' for the coordinator's note is a length limit. one word: no fixed length, open state at the top. (Record: D-0160 "should not have strict limits" (names the handoff and the channel).)
- **C5** M145: the two periods of the verification (D-0163, relayed). one word: yes, two passes. (Record: D-0163 is RELAYED; her turn #2087 'yes please' does not name the passes.)
- **C14** M148 q2: build the reset now on the old screen, or wait for the stage-2 screen. one word: wait for stage 2. (Record: D-0179 (My view is the old model to be replaced); D-0089 (the screen last). M148 says 'as she said in M169' wait; no ledger line says wait.)
- **C15** M148 q3: show the notice '3 preview filters cleared, you changed view'. one word: yes. (Record: home_preview_filters.md section 4 point 5 (her comment of 2026-11-11, not a ledger line); D-0015 (the software informs).)
- **C16** M149: a new ledger line that says D-0019 'inactive filters are hidden' means 'the preview lists are hidden while audit mode is on' (it is labelled P2, the source is P3). one word: yes to a new correcting line. (Record: D-0019 as written; the old line is not changed.)
- **C18** After D-0177 to D-0186: texts that must change (ADR-098 points 1 and 7, ADR-105 point 1, ADR-094 and rules_data_analysis_recipe_structure.md section 11a for D-0184, ui_implementation_contract.md sections 4, 8, 13, home_preview_filters.md section 5). one word: yes to the text changes (an agent writes them). (Record: D-0104 "No rule is changed without me agreed"; D-0055 "the latest decisions must hold"; the list of texts is in h1_filter_view_change.md section 7.)
- **E3** Broken path in implementation_workflow_transformer.md repaired. one word: yes to the text. (Record: edit fdb7df0f follows D-0104 "Broken paths in rule files are repaired by an agent".)
- **E4** CLAUDE.md standing rules of the coordinator; the guard refuses Bash that writes files. one word: yes; the two lines 'one-line fix' are corrected. (Record: edit 55e578f5 follows D-0049 "the coordinator only coordinates"; contradicts CLAUDE.md lines 41 and 48 ('a one-line fix'). Same as batch 6 question 1.)
- **E5** retest_procedure.md uses the new action names. one word: yes to the text. (Record: edit da4e5ae7 follows D-0036.)
- **E6** retest_procedure.md line 156 (strict import message). one word: yes to the text. (Record: edit 9bfdaf4c follows D-0034 (DEC24).)
- **E13** Replace section 8 of the bioscientist role file by the list of the 68 registered names (R024); today the 67 old names are not registered. one word: yes to R024. (Record: D-0073 "if unsure verify and ask"; D-0104. The file calls it 'c' (no decision found).)
- **E14** rules_app_structure.md rows for bundle_importer.py. one word: yes to the text. (Record: edit 0821ef6f follows D-0013.)
- **E15** rules_data_analysis_recipe_structure.md section 11 scope boundary closed. one word: yes to the text. (Record: edit c32e7ea2 follows D-0009 and D-0079. Note D-0184 now replaces in part D-0009 (check at selection).)
- **V3.1a** Batch 3 q1: a join that DROPS rows is told in HOME and at the check. one word: yes, as a warning with the two row counts. (Record: D-0168 "Nothing should vanish silently in the audit - warning" (about the audit); M159 asked for the count of rows lost by any join (relay).)
- **V3.4** Batch 3 q4: wording of the message for a key that is not unique, naming both tables. one word: yes. (Record: D-0099 (form of advice texts); the words are the agent's.)
- **V5.6** Batch 5 q6: the ResFinder second stage (new column total_gene_count, new row order) follows her decision on directly plotted tables. one word: seen and kept. (Record: D-0034 (decision on directly plotted tables); she has not said she saw the heatmap before and after (tmp/dataset_tier2/).)
- **V8.7** Batch 8 q7: keep the three removed actions (value_counts, select_by_pattern, sanitize_column_names) removed, with the replacement named. one word: keep removed. (Record: D-0037 "maybe we need the polar action and nothing else" (consistent); no decision names these three.)
- **I9** Intent O9: audit steps of the old data stay with the old session. one word: yes. (Record: Record: hash model section 5 (3) and home_audit_steps.md:59; D-0186 "changing data is not necessary a failure".)
- **I12** Intent O12: the review screen before the export; the history log inside the export. one word: yes to the review screen. (Record: D-0083 "You can appen a log ... separate than the final steps" (may be appended); D-0144 'point 8 yes' (log written by default). The pre-export review screen is in no hers-line.)

---

## (e) The proposals you wait for, and their state

| Proposal | You asked | State at 20:00 | Where it is |
|---|---|---|---|
| Recipe overview display (right panel accordions, colours, insertion point, where the lineage joins) | M118 / ledger A15: proposals with pictures first. D-0084 decides accordions in the right panel with one switch. The final place and the display are open | Not started. The UML tasks were parked (M177, M179) and freed again in M180 (the open StarUML project is now tied to `docs/UML/app.mdj`) | No file found |
| Audit steps between steps or at the start of a list | D-0146 (for now at the end of each list); ledger "Asked, not decided" M155 point 9: data scientist and software architect, pros and cons | Queued by the coordinator (M151 item 5). Not started when its note was written (19:39) | No file found |
| The readable summary of all audit steps in the export | M155 point 11: data scientist, software architect and user; options named: reasons as `#` comments only, a separate readable file, a table in `report.qmd`, more than one | Queued (M151 item 5). Not started | No file found. D-0148 decides only the audit_recipe with the reason as a `#` comment |
| A help button in the audit dialog | M155 point 13: ask several agents | Queued (M151 item 5). Not started | No file found |
| Sessions on different datasets (M175) | Proposals with pros, cons, effort, risk; seven questions (how the user chooses the data, what identifies a session, the comment per session, sessions side by side, what a data change does to the audit steps, the data check per dataset, what the export records) | Queued (M151 item 5): three viewpoints after a read-only agent has marked DECIDED / CONFIRM / OPEN. Not started. D-0186 "changing data is not necessary a failure but changing a recipe is" is the only decision | No file found |
| The plotnine rename impact | M129 / `tasks.md:387`: you see the impact before the rename | Written (630 lines). Waits for you to read it. Nothing is renamed | `.claude/design/viz_rename_impact_2026-11-15.md` |
| The Python research (a recipe built from Python and back, and the Blueprint AI agent) | A03: research and proposal, NOT a decision; after the visualisation library | Queued (`tasks.md:410` PY-RESEARCH). Only the first architect viewpoint exists as scratch (round 5) | `tmpAI/panel/round5/python_recipe/README.md` |
| The impact report for "a recipe is checked when it is selected" (D-0184), with the start time and the first-selection time of the structure check and the data check | M173, M174: before anything is removed at start | Queued (M150 item 3, M151 item 4). Not started | No file found |
| The list of the 15 rule-file edits with no recorded yes | D-0173 | Done. Waits for your word per row (E1 to E15) | `tmpAI/panel/verification/rule_edits_and_action_names.md` |
| The filter check (exploration against the decided model) | M165 to M170 | Done. Waits for your answers (B12, C14, C15) | `tmpAI/panel/verification/h1_filter_view_change.md` |
| An explanation list of the results that changed under the new rules (A06) | M84 | Not found | none |

---

## Records that contradict each other (tagged OPEN or flagged)

1. Y7: D-0120 says "Her Y7 is answered by this"; the ledger list "Asked, not decided" (M146) says Y7 was NOT decided as a question and asks an agent to say whether it still is. I tagged it DISSOLVED by D-0120 and flag the mismatch. The report that D-0135 asks (does Y8 dissolve when the audit copy is built) was not found.
2. Pt7: M176 says "point 7 (multi-resistance: decided)". D-0172 covers only the missing phenotype, not the `unknown[...]` text or classes. Tagged OPEN for the rest.
3. Y13: M176 lists it as changed today. No record answers it. Tagged OPEN.
4. Pt1: D-0013 / ADR-097 / P4b against your words of 2026-11-15 on the two export modes (and the older `export_specification.md:81`, `ui_implementation_contract.md:220`).
5. Pt3: `home_audit_steps.md:134` against `:138`; D-0144 "we can start with that" names no default.
6. AP1: `spaces/HOME.md:124` and `home_audit_steps.md:164, :327-328` (three undo controls) against the intent document O11 ("the unto is the remove step button"). The one list called AP1 decided; I tagged OPEN.
7. Pt41: D-0034 (DEC15, `columns`) and D-0036 (DEC39, `column`), both dated 2026-11-13 in her column.
8. D-0009 (check every recipe at start; a failing one is not selectable) against D-0184 (check at selection). D-0184 replaces D-0009 in part; ADR-094, `rules_data_analysis_recipe_structure.md` section 11a and the code still say the old. The review session's design (a split check keyed by hashes, M173, M174) is not hers.
9. D-0078 against D-0183: replaced in part (the anti-join error becomes a warning). The error is in the main line `7ef46987` (not pushed); the coordinator says a branch (`task/self-join-warn`) removes it. Not verified here.
10. V3.5: D-0183 "no error in polars then no error for us" (said for self-joins) against the refusal of a 32-bit key joined to a 64-bit key (D-0044, D-0065 support the refusal).
11. Plot rule file and ADR text: a `null` seed means a new arrangement each time (D-0004) against the code, which refuses `null` (a provisional build under D-0056). D-0056 does not say whether `null` is refused.
12. D-0098 "dates become Date (or the columns are dropped if no recipe uses them)": no shipped recipe uses them, so the literal reading is drop; the data scientist advises Date (Y11).
13. `tasks.md:312` and `:447` on `guide_label`; `tasks.md:198` and `:196` on the `pipeline-*` names.
14. D-0038 (PROVISIONAL, agent) against the built removal (`d63d3f3d`); D-0028 and D-0107 are NOT-STATED (Pt39, Pt40).
15. M155 lists point 12 of the first page as confirmed; her turn answers 1 to 11 and 13 to 15 (D-0151 is RELAYED). The rule itself stands in D-0088.

---

## (f) Appendix: every point, its tag and the evidence

`area`: RD recipe and data; AE audit and export; HS HOME screens; VN visualisation and names; GA gallery; BP Blueprint; RR rules and records; PR process. A `*` after the tag means the point blocks a build.

| Code | Area | Tag | Point | Evidence (ledger number and words, or the record) |
|---|---|---|---|---|
| Y1 | RD | DECIDED | PlasmidFinder piece: wire it, do not delete it | D-0109 "Y1 - have it wired" |
| Y2 | RD | DECIDED | ResFinder tie rule (lowest accession, then first row) | D-0111 "yes - rule deterministic" |
| Y3 | RD | DECIDED | Best hit: identity first, then overlap | D-0112 "if same identity favor the one that has higest overlap/coverage" |
| Y4 | RD | DECIDED | Drop the NaN rows before the ResFinder filter, with a comment | D-0113 "yes add the step in the recipe" |
| Y5 | RD | DECIDED | Plots for the ResFinder result (two heatmaps, plus the class plot) | D-0114 "heatmap gene per country - heat map gene per year"; D-0133 (confirmed by D-0161) |
| Y6 | HS | DECIDED | Typed ids: selectors first, report n matched / m not found, warn in all cases | D-0116 "typing in the audit should be limited as much as possible"; D-0118 "we will need to warn in all the cases"; D-0134 (confirmed by D-0161) |
| Y7 | AE | DISSOLVED | Plots ticked only after the engine reads steps written on a plot | D-0120 "the plot must read the data after T3 is applied" (it says her Y7 is answered); D-0089 build order; D-0150 "the engine reading T3 was not build yet". Mismatch: the ledger list 'Asked, not decided' (M146) still asks an agent to say whether Y7 is still a question |
| Y8 | AE | DISSOLVED | Refuse the export when a plot's audit steps cannot be written | D-0120 "the audit recipe is copied from the original recipe" (Y8 trivial); D-0102 "refused with a message, never skipped". D-0135 says: report whether Y8 dissolves once the audit copy is built (report not found) |
| Y9 | VN | DISSOLVED | An old results bundle with old plot names is refused | consequence of D-0091 "we only accept new names" (no old names accepted; refused with "did you mean") |
| Y10 | VN | CONFIRM | Register 30 of the 35 missing plotnine objects | D-0051 "honest parity list, both spellings"; D-0091 "the registry audit comes first". The wish 'verify that ALL are registered' is M106 (57), not a ledger line. |
| Y11 | RD | CONFIRM | The two date fields: Date, or drop the columns | D-0098 "dates become Date (or the columns are dropped if no recipe uses them)". No shipped recipe uses them, so the literal reading is drop; the data scientist advises Date (dropping moves the golden hashes) |
| Y12 | RD | DECIDED | Delete or archive two old files with 7 lower-case categorical fields | D-0086 "what is not current is deleted or moved to an archive folder" |
| Y13 | BP | OPEN* | Blueprint AI helper: does 'startup is never blocked' mean the app always starts, or the start must not wait for the helper | No ledger line, no channel block. M176 lists Y13 as 'changed today' but I found no record that answers it. ADR-076 (architecture_decisions.md:2948) is the only source (not a ledger line). Today the start can wait up to 40 seconds with no message when the helper is on (developer setting only). |
| Y14 | RR | CONFIRM | The word 'profile' for the checker's four modes | D-0034 "profiles run/build/gallery/audit" (DEC13-26, her date column). Against it: 2026-11-07 she called the word ambiguous for the deployment (D-0006 names). No turn of hers on the checker's use was found |
| Y15 | RR | OPEN | The word 'persona' for the review method (viewpoints of the panel agents) | No ledger line. ADR-091 point 5 retired the word for the app configuration only. She uses it herself. Linked: edit E10 (is the persona review file wanted at all) |
| Y16 | RR | CONFIRM | The settings names pipeline-* stay | Two records: tasks.md:198 (2026-11-08, find a new name) and tasks.md:196 (2026-11-12, her words `92f68895` turn 8673, rename to pipeline-simple-exploration, keep the prefix). The later holds; there is no ledger line |
| Y17 | HS | OPEN | True/false offers only 'equal' and 'not equal' | D-0054 "All required operators will need to be wired in the screens" and D-0061 "every type must be usable" point to offering all; the agent's built choice offers two. No record says that two operators are enough |
| Y18 | HS | OPEN | Time of day and duration: comparisons and 'between', no list 'one of' | Same records as Y17 (D-0054, D-0061); no record on this case |
| Y19 | HS | CONFIRM | A value finer than the column is refused, never cut | D-0050 "No silent error that is the rule"; D-0039 (DEC49: a cast that loses decimals fails). The choice 'refuse' or 'round and say so' is not in a record |
| Y20 | HS | OPEN | A filter 'one of' with an empty list | No record. Nearest: D-0060 (empty select/unpivot/top_k parameters are refused). This step can be applied, but it removes every row |
| Y21 | RD | DISSOLVED | A value is kept exactly, or the reading stops (five cases) | consequence of D-0050 "No silent error that is the rule" and D-0039 (DEC49); also D-0035 (DEC28) |
| Y22 | RD | DISSOLVED | HOME's own table and plot also refuse a value of the wrong type | consequence of D-0050 "No silent error that is the rule"; the engine rule is ADR-104 point 7 |
| Y23 | RD | CONFIRM | NI stays on the figshare scale Enum [S, I, R, NI] | D-0098 "categories whose order has a meaning become Enum with the order written in the recipe"; the list S, I, R, NI is M119 (57). No file defines NI |
| Y24 | RD | CONFIRM | The stress 'value' is Float64 | D-0098 "the `value` of the stress recipe is corrected"; the type Float64 (or Decimal) is the agent's choice |
| Y25 | RD | CONFIRM | The documented Categorical example is 'breakpoint' | D-0098 "one documented `Categorical` example may stay"; the field breakpoint is the agent's choice |
| Y26 | VN | CONFIRM | Put the plot-name prefix rule into rules_viz_factory.md | D-0091 decides the prefixes; D-0104 "No rule is changed without me agreed" |
| Y27 | AE | OPEN | Until the audit copy exists, today's optional export recipe keeps the name 'forked recipe' | D-0143 names the two recipes original_recipe and audit_recipe; no record on the interim name for today's code |
| Y28 | RR | CONFIRM | A one-line note on the three contradicted diagrams and one small new diagram 'two recipes' | D-0071 covers only the six arrows of PKG-TIERS ("star uml is open - fix"); the review session released the other UML tasks in M180 (a relay, not hers). D-0012 (UML sync) applies |
| Y29 | RR | OPEN | Change the four docs pages that teach the old picture now | No record says when. The four rule-file rows (R092, R112, R113, R122) need her yes (D-0104) |
| Y30 | RR | CONFIRM | Seven rule-file edits of 2026-11-14/15 stay as they are | D-0173 "investigate that then present the list"; the list is ready (rule_edits_and_action_names.md); merged with the 15 edits E1 to E15 below |
| Y31 | RR | CONFIRM | Correct the sentence that says an emoji scan is 'active now' | D-0073 "if unsure verify and ask" (rule files follow the code); D-0104 needs her yes to the text |
| Y32 | RR | CONFIRM | Rewrite three checker ERROR texts as 'what is wrong, then Suggestion:' | D-0099 covers advice texts ("Suggestion: To always ..."); the three are error texts |
| Y33 | RR | CONFIRM | The advice texts as built | D-0099 decides the form; the words are the agent's (PROVISIONAL in tasks.md). One text (ST15) has an added remedy (Float64) |
| Y34 | RD | OPEN | derive_categories stays removed | D-0038 is PROVISIONAL (an agent's remark, not hers); D-0037 (Polars only) does not name it. Built (d63d3f3d). Same as batch 8 question 3 |
| Pt1 | AE | DECIDED* | What the standard (results) export always holds, and what is behind the tick | DECIDED 2026-11-16 by D-0187 "If the user has used audit, both mode 1 and mode 2 must use the audit recipe and the data, hashed", D-0188 "mode 1 and mode 2 export the original recipe and the data that was used", D-0192 "The recipe is added to the reproducibility mode 2, and removed from mode 1" (where the recipe goes; the ledger says it refines D-0013). Also covers O1 and A17. Not answered: whether the raw data is behind a tick (readings A, B, C of B1) and where the data used is chosen. D-0148 and D-0147 as before. |
| Pt2 | AE | DECIDED (D-0197) | Which sample ids 'remove these samples from all tables' uses (the first wording, a tick at a table without the column, was wrong, D-0196) | D-0197 "if you apply the T1 then you will have 28, eg if you apply in T2 there will be 21": the ids of the view where the selection was made |
| Pt3 | AE | OPEN* | What is ticked when the audit dialog opens | D-0144: she confirmed point 6 and said 'we can start with that' and the default 'may change after use', but the document does not name the default. Records disagree: home_audit_steps.md:134 (all ticked) and :138 (only the place the user chose) |
| Pt4 | AE | OPEN* | A typed value that cannot be typed at one ticked node (a number vs a text column) | Nearest: D-0175 (a filter can only be created where the column exists) and D-0176 (plain message). Her doubt 'I do not see how this is possible' (tasks.md:396, 2026-11-15) is not a ledger line. Stage-2 spec default (a) is the writer's |
| Pt5 | AE | OPEN* | When the audit_recipe file is created (first audit step, audit mode on, or session start) | No record (M176 says 'ASK, not decided'). D-0143 and D-0102 say what the audit_recipe is, not when it first exists |
| Pt6 | HS | OPEN* | The screen words for the two plots and tables | D-0179 "There is not my view anymore in the refactor" removes option (b) 'keep My view'. D-0180 says one plot view in exploration. The words for the audited plot and the original are in no record (home_audit_steps.md:81 holds 'Result' in a notice only) |
| Pt7 | RD | OPEN* | The multi-resistance flag: does 'unknown[...]' count as a class, and does it count drugs or classes | D-0172 decided only that a MISSING phenotype is not counted ("missing here means that no resistance phenotype has been detected"). M176 says point 7 is decided; the ledger line does not cover the unknown[...] text or classes. Her definition 2026-04-23: 'resistant to more than one class' |
| Pt8 | RD | OPEN* | Which thresholds the ResFinder rule uses (identity 90 with overlap 60, or identity 90 with overlap 85 and ratio 0.8) | D-0087 "you filter out what is below" with 'old thresholds verified'; the history holds two pairs, so no record chooses. PlasmidFinder has the same question (cut 90/60, web default 95/60), merged here |
| Pt9 | RD | OPEN* | Does 'one row per sample and gene' also apply to the AMR join of 2_test_data_ST22_dummy | D-0087 names the converted piece. D-0110 decides that recipe 2 is merged into recipe 1 or removed (list shown to her first, D-0132), so the answer depends on that outcome |
| Pt10 | RD | OPEN* | The FastP box plot cannot work as written (one row per sample) | D-0086 "b,c,d,e - ask ... agent data science to wire it"; the agent found the plot cannot be a box plot. Whether to change the intent is not in a record |
| Pt11 | VN | CONFIRM* | Names plotnine does not have (22): prefix step_ or modif_ | D-0036 (DEC31-42: step_ is the project's own) and D-0091 "a composite is `step_<name>`"; the 22 are not all composites |
| Pt12 | VN | OPEN* | Names written as values (geom: geom_area) get the prefix or stay plotnine's | No record speaks of values |
| Pt13 | VN | OPEN* | The 15 plotnine objects that cannot be added to a plot (element_*, position_* ...) | No record |
| Pt14 | VN | OPEN* | guide_label fails on every use: remove, rebuild, or keep renamed | Records disagree: tasks.md:312 'your choice: rebuild or remove' and :447 'fixed and tested'; the rename document's default is remove; the coordinator's earlier default was rebuild |
| Pt15 | VN | OPEN* | The facet and guide conveniences (21 own components): keep, remove 9, or fold 4 | M107 (57) asked for the list; no record decides |
| Pt16 | VN | OPEN* | How a recipe maker gets a mean with an error bar (stat_summary takes functions) | Ledger 'Asked, not decided' A12: 'NOT decided; investigation with a concrete example'. The advice for mean_se and for stat_summary without fun_data is decided (D-0067) |
| Pt17 | RR | OPEN* | 'audit node' and the stored key node_type for one audit step | No record. Her words: 'I think you call that node' (for a point of the lineage) |
| Pt18 | RR | OPEN* | The words for the reach of an audit step ('every plot in the project', 'project = 0') | D-0069 "All old words need to be corrected" (everywhere active, not history); ADR-105 replaced the reach levels. The replacement words are in no record |
| Pt19 | RR | OPEN* | 'Assembly' for the join: how far to rename | D-0069 covers old words in general; ADR-066 (2026-05-04) is partly done. The extent (screen texts only, or the code context and assembly.json) is in no record |
| Pt20 | RR | OPEN* | WrangleStudio / wrangle_studio.py / dev_studio in the code | No record. D-0048 puts Blueprint and Test Lab last in the order of work |
| Pt21 | RR | OPEN* | The title 'Pipeline Audit' and the name static_web | No record; the audit screen build replaces the old model (D-0016) |
| Pt22 | RR | OPEN* | The form of the old-words check (narrow, wide, or both) | D-0069 decides the clean-up; the form of the check and its exclusions are in no record (nothing applied before she sees R3) |
| Pt23 | HS | OPEN | The list of values served on demand above 1000 values | No record; D-0117 asks to reuse what was good in the earlier UI |
| Pt24 | HS | OPEN | A time of day: three number boxes, one native input, or one text box | No record |
| Pt25 | HS | OPEN | A duration: number box and 8 units, fewer units, or one text box | No record |
| Pt26 | HS | OPEN | A date and time: date picker plus time boxes, one text box, or a zone choice | No record |
| Pt27 | HS | OPEN | The starting values of the filter boxes (smallest value, empty, or zero) | No record. Principle D-0108 'not to make choices for the user' and D-0015 (the software informs, the user decides) bear on it |
| Pt28 | HS | OPEN | The date box: strict typed text with a calendar for the mouse, or plain text box, or refuse 2023-2-8 too | D-0050 "No silent error" (no repair of free text) is decided; the form of the box is not |
| Pt29 | RD | OPEN | A Date with no 'format': require it, advise, or leave | recipe_format_spec.md:370 says format is optional; no ledger line |
| Pt30 | RD | OPEN | A cell that holds only spaces: always missing, or an empty text | The coordinator asked it on 2026-11-15 (channel :419); no ledger line answers |
| Pt31 | RD | OPEN | quality_module (Passed, Warning): is there a 'Failed' | D-0098 (nominal become String; ordered become Enum) needs the full list of verdicts, which is in no file |
| Pt32 | RD | OPEN | 'year' in the retest recipe: String, Enum or Int64 | D-0098 does not weigh the three; no record |
| Pt33 | RD | OPEN | 'status' in the audit template: String or Enum | No data file in the repository; no record |
| Pt34 | RD | OPEN | The plotted table of the stress plot writes '2023-04-11 00:00:00' with Date | Only matters if Y11 says Date; no record |
| Pt35 | VN | OPEN | Names for label and rescale functions (percent, comma, censor, squish) | No record; D-0030 limits formulas to an allowed list |
| Pt36 | AE | OPEN | A short pop-up when the open recipe is replaced | No record; D-0149 "warn only when problem" and D-0186 "changing a recipe is" a failure bear on it |
| Pt37 | VN | CONFIRM | The seed mechanism built provisionally (null refused; seed for the whole recipe; audit pin with 'Reshuffle') | D-0056 "Fixed 0 by default fixed and simple" and "every seed that is used is written in the recipe or the audit recipe"; the three built parts are the agent's (PROVISIONAL). A01 (a special seed field per jitter step) has no answer. The plot rule file still says null = new each time (D-0004, replaced in part by D-0056). Merged: batch 4a Q2 and Q3, batch 6/7 Q2, batch 8 Q1 |
| Pt38 | RR | OPEN | A type-only import between libraries (rules_runtime_environment.md:79 and rules_test_lab.md:58) | No record says whether the stricter line is on purpose |
| Pt39 | RR | OPEN | Who defined the 'step compiler' | D-0028 is NOT-STATED (no decision of hers found) |
| Pt40 | RR | OPEN | Who set the rule 'a build on an agent's recommendation is PROVISIONAL' | D-0107 is NOT-STATED (tasks.md:21 says Eve 2026-11-15; her turns hold no such sentence) |
| Pt41 | RR | OPEN | 'column' or 'columns' for the input column of modif_ and step_ actions | Two ledger lines disagree: D-0034 (DEC15 `columns`) and D-0036 (DEC39 `column`), both dated 2026-11-13. Code and recipes use `column` |
| Pt42 | AE | OPEN | When the recipe changes while a view is open: keep what was opened until Reload, or follow at once | D-0186 "changing a recipe is" a failure; D-0088 (export refused until the user re-bases); D-0184 evidence lists a check of a changed recipe within seconds (the review session's list, not hers). None says what HOME shows |
| Pt43 | AE | OPEN | Data files: watched every 2 seconds, or only the warning at the next click and the refusal at export | D-0186 "changing data is not necessary a failure"; M175 asks for proposals on datasets. Merged with the sessions proposal |
| Pt44 | BP | OPEN | Blueprint tells the person who saves that n views of the recipe are open | No record (A11: investigation, no build) |
| Pt45 | BP | OPEN | Confirm: Blueprint's save is never blocked | No record (A11) |
| Pt46 | AE | OPEN | Two users on one app and one user-data folder: supported or not | No record |
| Pt47 | AE | DECIDED | The Data Import panel must not write over the recipe's data path | D-0045 "the recipe's path is not touched" (imported data by dataset id in its own folder) |
| Pt48 | RD | OPEN | The three figshare plots (and the PlasmidFinder plots) count rows (hits), not samples | tasks.md RECIPE-SCIENCE-1 pending; no ledger line. Merged: PlasmidFinder point 6 |
| AP1 | AE | OPEN | 'Undo last', 'Revert to step N' and 'Remove all' in the audit panel | Records disagree: spaces/HOME.md:124 and home_audit_steps.md:164, :327-328 list three controls; the intent document (O11) quotes her 'the unto is the remove step button' (T92 L11773). D-0102 only says a step added in the audit can be removed again |
| AP2 | RR | DECIDED | The two recipes are named original_recipe and audit_recipe | D-0143 "The two names are written with the underscore (original_recipe, audit_recipe)"; D-0102 |
| AP3 | AE | DECIDED | A filter on a column dropped earlier is an error; steps run in the recorded order | D-0096 "a filter on a column dropped earlier is an error from the engine" |
| AP4 | RD | DECIDED | Equality test copies and hand-written reference change with the recipe | D-0031 "no shim, no half fix, tests adapted before they run" |
| AP5 | RD | DECIDED | A different level order is accepted for nominal fields when the counts are equal | D-0098 "a different level order is no problem for nominal categories if the counts per category are equal" |
| AP6 | VN | DECIDED | Both spellings color and colour are registered | D-0051 "honest parity list, both spellings" |
| AP7 | AE | DECIDED | The na tick in every filter; starts on keep for 'is not' and 'none of' | D-0042 "every filter step states `na: keep/remove`, no default" |
| AP8 | AE | DECIDED | A tick on the lookup side of a join removes no sample; counts shown | D-0093 "counted before and after along the lineage" (the lookup-side sentence rests on home_audit_steps.md:123 only) |
| AP9 | AE | DECIDED | A tick on a data file reaches every table built from it, with counts | D-0093 "applied at each ticked node and counted before and after"; D-0053 |
| AP10 | AE | DECIDED | Samples removed in one table that stay in another are reported | D-0023 "checks after Apply" |
| AP11 | AE | DECIDED | T1 or T2 of a table are separate tick lines with numbers | D-0022 "a step is written at ONE of T1/T2 of a table or T3 of a plot" |
| AP12 | AE | DECIDED | A tick that removes nothing new or empties a table is a warning, never a block | D-0095 "Audit signals are warnings or information, never a block" |
| AP13 | RD | DECIDED | The 37 missing step descriptions are written; one false description corrected | D-0080 "Pipelines recipes need to be fixed" |
| AP14 | GA | DECIDED | The gallery needs no fix: 34 of 34 pass and draw their stored picture | D-0077 "All recipes need to work" |
| AP15 | RD | DECIDED | The old output-fields list of the phenotype view is deleted | D-0086 "a remove old output fields" |
| AP16 | RD | DECIDED | The empty file experimental/test_logic.yaml is deleted | D-0086 "deleted or moved to an archive folder" |
| AP17 | RD | DECIDED | Detailed_summary_with_metadata and the richer stress plot are wired | D-0086 "the other fragments are wired by a data-scientist agent" |
| AP18 | RD | DECIDED | ResFinder: filter below the minimum, then best hit per sample and gene | D-0087 "keep the one with best identity and best coverage"; D-0111 to D-0113 |
| AP19 | RD | CONFIRM | Reading captures Polars and type errors in one error form | Ledger 'Asked, not decided' A10: she wants Polars and type errors captured at reading (M101: 'the most important thing'), not a numbered decision; D-0176 is for a missing column only |
| AP20 | RD | DECIDED | The checker judges the declaration of a type without data | D-0067 "a checker advice is added whenever it helps" |
| AP21 | RD | DECIDED | An advice is added whenever it helps (narrow types, mean_se, stat_summary) | D-0067 "add checker advice alsways good" |
| AP22 | RD | DECIDED | A recipe text must not run code (geom_smooth formula checked) | D-0030 "formulas only from an allowed list of Polars functions"; D-0064 |
| AP23 | VN | DECIDED | A text given where a list is meant is a silent error and is fixed | D-0050 "No silent error that is the rule" |
| AP24 | HS | DECIDED | The filter dialog follows the column type | D-0061 "the pickers adjust to the type of the column" |
| AP25 | HS | DECIDED | The calendar must not repair free text | D-0050 "No silent error that is the rule" |
| AP26 | RR | DECIDED | Six old-words points (project, refusal tests, recipe overview, short 'recipe' in code, two recipes, pipeline stays) | D-0069 "All old words need to be corrected"; D-0085 "recipe overview"; D-0143. I did not check the other three in replacements.md |
| PF1 | RD | CONFIRM | Merge recipe 2 (2_test_data_ST22_dummy) into recipe 1, or remove it | D-0110 "can be merged with 1_test_data_ST22_dummy it it adds something otherwise remove"; D-0132 "Nothing is removed before the merge or removal list is shown to her". D-0172 keeps the multi-resistance change, so the flag is wanted. The report recommends merge, then remove |
| PF2 | VN | OPEN | Heatmap colour: share of the group's samples, or count | D-0114 gives the two heatmaps, not the colour. The report's default (share) is the agent's |
| PF3 | RD | CONFIRM | Best hit per sample and type in the PlasmidFinder table (150 rows, tie = lowest accession) | D-0087 and D-0111 decide the rule for AMR genes; extension to plasmid types is the agent's |
| PF4 | RD | merged into Pt8 | PlasmidFinder thresholds 90/60 or 95/60 | merged into Pt8 |
| PF5 | RD | OPEN | A sample with no replicon hit counts as 'no replicon found' in the group size | No record; only she knows whether the pipeline writes a row for a plasmid-free isolate |
| PF6 | RD | merged into Pt48 | Hits or samples for the plots | merged into Pt48 |
| PF7 | RD | OPEN | The plot's own filter before the tier-3 reader exists (plot filters / two collections / wait) | D-0115 "so 2 plots that can furk on the same t1 or t2 so 2 t3"; D-0133 'T3 only for what one plot alone needs'; the reader is not built (D-0150). Merged: intent document O7 (spec-level filters vs steps.tier3, 'recommended, awaiting Eve') |
| PF8 | RD | CONFIRM | Regenerate the golden baseline (7 new entries) after she has seen the pictures | D-0132 "any decision about the golden baseline" is shown to her first |
| PF9 | RD | OPEN | The overlap column in the dummy PlasmidFinder file is not trustworthy (values above 100) | No record; information, no plot uses it |
| C1 | PR | DISSOLVED | M145: the '15 plain lines per area' of D-0139 against no length limit | D-0182 "C YES" (no limit on worker reports), D-0154, D-0160 |
| C2 | PR | CONFIRM | M145: the handoff is 'append, do not delete'; M157 says done items are removed or archived | D-0160 "keep precise and upated"; the 'archived means moved' sentence is marked ADDED by an agent in CLAUDE.md |
| C3 | PR | CONFIRM | M145: CLAUDE.md 'one-screen state' for the coordinator's note is a length limit | D-0160 "should not have strict limits" (names the handoff and the channel) |
| C4 | PR | DISSOLVED | M145: Explore and Plan agents need a Decisions block | D-0156 "gate every agent except scout, scribe and the panel-* agents" |
| C5 | PR | CONFIRM | M145: the two periods of the verification (D-0163, relayed) | D-0163 is RELAYED; her turn #2087 'yes please' does not name the passes |
| C6 | PR | DISSOLVED | M145: D-0140 replaced by D-0141 | D-0161 "D-0140 is replaced by D-0141"; D-0162 "choose the earliest date" |
| C7 | PR | DECIDED | M147: worker reports have no length limit | D-0182 "C YES" |
| C8 | PR | OPEN | M147 points 2 to 5, M150, M171 D: the hook asks for a quote of 12+ characters; simplify to 'decided number plus any quoted piece', or keep as built | D-0166 option C ("each decision number is followed by quoted words that appear in that ledger line") is decided; the 12 and 4 minimums, quotation marks, short quotes and fields are the builder's. Her question 'do we need to be so stringent?' is in the ledger list 'Asked, not decided'. The coordinator's recommendation: simplify. The coordinator stopped all tuning until she answers |
| C9 | PR | DISSOLVED | M147 point 6: D-0130 to D-0142 keep the review session's wording in the decision field | D-0161 "that is my decisions you wrote" |
| C10 | RD | DISSOLVED | M147 section 4: when the anti-join of a table with itself is an error | D-0183 "no error in polars then no error for us. Warning/caution is good." |
| C11 | RD | DECIDED | M147 section 4: self-join warning carries row numbers | D-0078 (the warning with the row numbers stays); D-0183 replaces only the error sentence |
| C12 | BP | OPEN | M147 section 4: a failing step of a dataset the recipe does not use: does it make the recipe fail when selected | D-0184 moves the check to selection; no record on this detail (the coordinator's default was: yes, name the dataset) |
| C13 | HS | OPEN* | M148 q1: the exploration filter reset, when the user goes to a plot of ANOTHER table at the same stage (reset, or keep with a notice) | D-0178 "if user change from view then the filter is reset and rebuild"; M168 itself says which user action counts as a change of view 'is to be checked and is not decided'. The coordinator found no default |
| C14 | HS | CONFIRM | M148 q2: build the reset now on the old screen, or wait for the stage-2 screen | D-0179 (My view is the old model to be replaced); D-0089 (the screen last). M148 says 'as she said in M169' wait; no ledger line says wait |
| C15 | HS | CONFIRM | M148 q3: show the notice '3 preview filters cleared, you changed view' | home_preview_filters.md section 4 point 5 (her comment of 2026-11-11, not a ledger line); D-0015 (the software informs) |
| C16 | RR | CONFIRM | M149: a new ledger line that says D-0019 'inactive filters are hidden' means 'the preview lists are hidden while audit mode is on' (it is labelled P2, the source is P3) | D-0019 as written; the old line is not changed |
| C17 | AE | OPEN* | M151: when the user changes the plot tab, the Export panel is drawn again with its default values (box unticked, name gone). Keep what the user set, or reset with a notice | No record. Nearest: D-0050 "No silent error that is the rule" (a download then has no reproducibility recipe and nothing says so). The coordinator's default (a) keep |
| C18 | RR | CONFIRM | After D-0177 to D-0186: texts that must change (ADR-098 points 1 and 7, ADR-105 point 1, ADR-094 and rules_data_analysis_recipe_structure.md section 11a for D-0184, ui_implementation_contract.md sections 4, 8, 13, home_preview_filters.md section 5) | D-0104 "No rule is changed without me agreed"; D-0055 "the latest decisions must hold"; the list of texts is in h1_filter_view_change.md section 7 |
| E1 | RR | OPEN | Do you accept the parts marked [ADDED] in decision_compliance.md (table, ledger description, block syntax) | edit f1f70353; D-0125 covers her text only; the file says so itself |
| E2 | RR | OPEN | Should the hook accept NONE-CHECKED only for a regular file inside the project, not the ledger | edit ee4f1eac; D-0155 does not ask for it |
| E3 | RR | CONFIRM | Broken path in implementation_workflow_transformer.md repaired | edit fdb7df0f follows D-0104 "Broken paths in rule files are repaired by an agent" |
| E4 | RR | CONFIRM | CLAUDE.md standing rules of the coordinator; the guard refuses Bash that writes files | edit 55e578f5 follows D-0049 "the coordinator only coordinates"; contradicts CLAUDE.md lines 41 and 48 ('a one-line fix'). Same as batch 6 question 1 |
| E5 | RR | CONFIRM | retest_procedure.md uses the new action names | edit da4e5ae7 follows D-0036 |
| E6 | RR | CONFIRM | retest_procedure.md line 156 (strict import message) | edit 9bfdaf4c follows D-0034 (DEC24) |
| E7 | RR | OPEN | Automatic audits paused until the refactor is finished (banner in two workflow files) | edit 16d52140; tasks.md:204 says '(Eve ...)'; no ledger line |
| E8 | RR | OPEN | retest_procedure.md as a permanent workflow file | edit 19285129; no ledger line |
| E9 | RR | OPEN | Run dates of audits in audit_routine_registry.md (next dates now wrong) | edit e3865b59; small; no decision |
| E10 | RR | OPEN | design_review_personas.md as a permanent workflow file | edit 4ba10ba9; only the 'never guess' line is hers (D-0017) |
| E11 | RR | DISSOLVED | ui_implementation_contract.md line 88/90 (filters on every view) | edit b055ba07 was replaced the same day by fa552bf7 (D-0014); D-0178 and D-0179 now change the model again (see C18) |
| E12 | RR | OPEN | ui_implementation_contract.md line 422 (Test Lab right panel reachable): may a rule file describe the code state without her yes | edit 143ae2d4; no decision |
| E13 | RR | CONFIRM | Replace section 8 of the bioscientist role file by the list of the 68 registered names (R024); today the 67 old names are not registered | D-0073 "if unsure verify and ask"; D-0104. The file calls it 'c' (no decision found) |
| E14 | RR | CONFIRM | rules_app_structure.md rows for bundle_importer.py | edit 0821ef6f follows D-0013 |
| E15 | RR | CONFIRM | rules_data_analysis_recipe_structure.md section 11 scope boundary closed | edit c32e7ea2 follows D-0009 and D-0079. Note D-0184 now replaces in part D-0009 (check at selection) |
| V1.1 | RD | DISSOLVED | Batch 1 q1: the checker refuses a forbidden formula at once | D-0064 "the formula allow-list as built is accepted"; D-0030 formulas only from an allowed list (fix started) |
| V1.2 | RD | OPEN | Batch 1 q2: correct the words 'SHA256 of wrangling steps' in the report now, or wait for the task that retires the old key name | No record (default: correct now) |
| V1.3 | RD | merged into Y11 | Batch 1 q3 (the two date fields) | merged into Y11 |
| V1.4 | RD | DISSOLVED | Batch 1 q4 and batch 3 q6: the duplicate-column-name rule is never run by the checker; say 'not checked' or run it from the declared fields | D-0050 "No silent error that is the rule" (silence is not allowed; the choice between the two is technical); J08 is an error in D-0034 |
| V1.5 | RD | DISSOLVED | Batch 1 q5: the three recipe-writing tools use the lists of actions and plot components | D-0050; listed by the coordinator among fixes that follow a decision |
| V2.1 | RD | DECIDED | Batch 2 q1: a missing column gives a plain message everywhere | D-0176 "Q8. a) if possible - if not possible then b)" |
| V2.2 | RD | OPEN | Batch 2 q2: an Excel upload writes the checked table as a tab-separated file instead of copying the Excel file | No record (default: yes). Related D-0045 (imported data by dataset id) |
| V2.3 | RD | DISSOLVED | Batch 2 q3: old filter step without the missing-value choice | D-0090 "remove all saved versions" (all stored sessions removed, so the old-step case mostly disappears) |
| V2.4 | RD | DISSOLVED | Batch 2 q4: docs say Polars changes the order of join pairs 'on every run' or 'can change' | D-0059 "yes inform" (docs say how Polars behaves); the run shows 'can change' (factual) |
| V2.5 | RD | DECIDED | Batch 2 q5: keep the multi-resistance change (missing not counted) | D-0172 "missing here means that no resistance phenotype has been detected so it should not be counted" |
| V3.1a | RD | CONFIRM | Batch 3 q1: a join that DROPS rows is told in HOME and at the check | D-0168 "Nothing should vanish silently in the audit - warning" (about the audit); M159 asked for the count of rows lost by any join (relay) |
| V3.1b | RD | OPEN | Batch 3 q1: a join that MULTIPLIES rows is told nowhere | No record covers it (4 rows became 7 in the run); default yes, a warning never a block |
| V3.2 | RD | OPEN | Batch 3 q2: the self-join warning with row numbers shown after the run, or from the data check | D-0078 and D-0183 decide the warning; the moment is not decided |
| V3.3 | RD | DECIDED | Batch 3 q3: a decimal key made by a step gets the advice too | D-0067 "add checker advice alsways good" |
| V3.4 | RD | CONFIRM | Batch 3 q4: wording of the message for a key that is not unique, naming both tables | D-0099 (form of advice texts); the words are the agent's |
| V3.5 | RD | OPEN | Batch 3 q5: keep refusing a 32-bit against a 64-bit whole-number key although Polars joins them | D-0044 (types the recipe declares, no hidden cast) and D-0065 (one join-key rule) support refusing; D-0183 "no error in polars then no error for us" (said for self-joins) points the other way |
| V4a.1 | HS | DISSOLVED | Batch 4a q1: an exploration filter names a column the table does not have | D-0175 "it cannot propose a filter on a column that does not exist in this table"; D-0178 (reset at a change of view) |
| V5.1 | RD | DECIDED | Batch 5 q1: the demo table keeps every sample (left join) | D-0167 "its a demo to show what we can do"; "Raws without sample id must go" |
| V5.2 | RD | DECIDED | Batch 5 q2: the phenotype column keeps the source Predicted Phenotype | D-0169 "a)" (keep the column and the source) |
| V5.3 | GA | DECIDED | Batch 5 q3: the three figshare plots keep lower-case names | D-0170 "a)"; D-0171 labels decide what is seen |
| V5.4 | RD | DECIDED | Batch 5 q4: the multi-resistance formula | D-0172 |
| V5.5 | GA | OPEN | Batch 5 q5: the 8 changed gallery pictures (7 changed size 800x600 to 960x600, jitter_strip differs in 2.6 percent of pixels): keep, or put the old ones back | No record that she looked at them; the jitter change is allowed by D-0056 |
| V5.6 | RD | CONFIRM | Batch 5 q6: the ResFinder second stage (new column total_gene_count, new row order) follows her decision on directly plotted tables | D-0034 (decision on directly plotted tables); she has not said she saw the heatmap before and after (tmp/dataset_tier2/) |
| V6.1 | PR | merged into E4 | Batch 6 q1: CLAUDE.md allows the coordinator 'a one-line fix' in two lines and 'never edits' in a third | merged with E4; D-0049 |
| V6.4 | PR | DISSOLVED | Batch 7 q4: restore the two tests that were lost | D-0129 "if it did fix what can be fixed" |
| V4b.3 | AE | DISSOLVED | Batch 4b q3: the import of a bundle checks 2 of its 4 parts | D-0013 "import verification warns, never blocks" (the four legs are in ADR-097); D-0129 fix what deviated |
| V4b.4 | AE | OPEN | Batch 4b q4: a restore of a session made for other keys (another recipe version or data): needs a click, and the saved record keeps the old keys | No record; merged into the sessions proposal (M175) |
| V4b.5 | AE | DISSOLVED | Batch 4b q5: an on-screen message when a plot or the report fails during an export | D-0050 "No silent error that is the rule" |
| V4b.6 | AE | DISSOLVED | Batch 4b q6: PDF pictures carry the keys too (PNG and SVG do) | D-0005 / ui_implementation_contract.md 7.2 point 5 (keys and hashes recorded in the export) |
| V4b.7 | AE | DECIDED | Batch 4b q7: fix the 14 swallowed errors and E2 to E5 of the export check now | D-0129 "if it did fix what can be fixed"; D-0050 |
| V8.2 | AE | DISSOLVED | Batch 8 q2: replace the export's per-plot join by the audit copy when HOME audit is built | D-0148 "the audit export export the audit recipe with the step of the audit added to the recipe" |
| V8.4 | BP | DECIDED | Batch 8 q4: Blueprint keeps the comments of a recipe on save | D-0174 "a)" (keep the comments, using a YAML writer that preserves them; a new library needs her yes) |
| V8.5 | BP | OPEN | Batch 8 q5: 'Create plot' in Blueprint: may an empty draft plot exist, or must Blueprint ask for table and columns first | No record (default: ask first) |
| V8.6 | BP | DISSOLVED | Batch 8 q6: the check of a recipe against its data reports a step that fails | D-0050 "No silent error that is the rule" |
| V8.7 | RD | CONFIRM | Batch 8 q7: keep the three removed actions (value_counts, select_by_pattern, sanitize_column_names) removed, with the replacement named | D-0037 "maybe we need the polar action and nothing else" (consistent); no decision names these three |
| V8.8 | GA | DISSOLVED | Batch 8 q8: plot names in lower case only | D-0170 "a)" (keep the lower-case names) |
| I7 | RD | merged into PF7 | Intent O7: spec-level plot filters until the engine reads steps.tier3 | merged into PF7 |
| I9 | AE | CONFIRM | Intent O9: audit steps of the old data stay with the old session | Record: hash model section 5 (3) and home_audit_steps.md:59; D-0186 "changing data is not necessary a failure" |
| I12 | AE | CONFIRM | Intent O12: the review screen before the export; the history log inside the export | D-0083 "You can appen a log ... separate than the final steps" (may be appended); D-0144 'point 8 yes' (log written by default). The pre-export review screen is in no hers-line |
| L1 | BP | OPEN | Ledger A05: Blueprint must be able to open a recipe that fails, each failing point shown as a point to fix | her design wish; 'investigate, no build yet'; no proposal file found |
| L2 | PR | OPEN | Ledger A06: an explanation list of the results that changed under the new rules is owed | no file found |
| L3 | GA | OPEN | Ledger A07: gallery G-b 'filters' read as interaction; one plain sentence is owed | NOT decided |
| L4 | HS | OPEN | Ledger A14: which audit signals could be an error; thresholds, how to count 'diverse' steps | D-0095 decides warnings not blocks; thresholds 'asked, not decided' |
| L5 | RD | OPEN | M141: a warning at run time when a ResFinder tie is found | D-0111 evidence: 'proposed, not built before she agrees' |
| L6 | RR | OPEN | M148 point 4: put the intent document first in the reading list of every agent (CLAUDE.md section 3, agent_principles.md) | a proposal; D-0104 needs her yes to rule-file text |
| L7 | PR | OPEN | M137: add a step 8 to the repository audit (logic and coherence of the whole) | a task request, not a decision |

## What I did not check

- I did not read your own turns (the transcript `cd1b0ac7`). A decision that exists only in a turn and in no ledger line is tagged OPEN or CONFIRM; the ledger and the channel are my sources.
- I took the facts (row counts, run results, `file:line`) of the one list, the verification files and the channel as written; I did not re-run them. The one list says it was checked at `a386422a`; the branch is now at `42118164`.
- I did not open `tasks.md`, the ADR file, `recipe_format_spec.md`, `home_audit_steps.md`, the stage-2 spec or the rename document; the lines I cite from them come from the one list, the intent document or the verification files.
- I did not check the code state of the branches `task/self-join-warn`, `task/stale-keys`, `task/recipe-plots`, `task/flake` beyond their progress notes.
- State of the proposals in (e) is from file search and the channel up to M180; a worker may have written a file after.
- The tag "CONFIRM" for a point whose decision is a ledger line and whose wording or choice is the agent's is my judgement of what is one word for you; the ledger line is quoted so you can disagree.
