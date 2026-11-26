# ONE list for Eve: what needs you (2026-11-16)

For Eve. Nothing was decided and no repository file was edited by the writer. Checked at `HEAD` `a386422a` on `feat/recipe-format-1`.

## At the top: five lines

1. **How many.** 34 yes/no points (Part 1) and 41 choose points (Part 2). 25 points turned out to be already decided by you and are not asked (Appendix A, AP1 to AP25; AP26 adds 6 old-words items the source already marks as answered). 12 groups of duplicates were merged (Appendix C).
2. **Built on a provisional basis, and can be undone** (each is one commit; "undo" means revert that commit):
   the seed for the whole recipe (`plot_defaults.random_state`) and the audit pin of a seed (`54e6979f`, `6f9479e0`, `653e70b1`);
   the list of values served on demand while typing, above 1000 values (`588af396`, not pushed);
   the texts of the advices, "what happens, then Suggestion:" (`806dc852`);
   the eight choices of the filter dialog (`4f37565d`, `69392b71`, not pushed);
   also, because they are agent's choices: the type of three Categorical fields (`Enum`, `Float64`, the kept `breakpoint`; `8db67b47`), the removal of `derive_categories` (`d63d3f3d`, never marked provisional), and the first line of the multi-resistance formula (in work, branch `task/recipe-fixes`, no number moves).
3. **Merged and pushed.** `origin/dev` is `78c620bf` (RUN `git rev-parse`): the `Categorical` fields migrated, the recorded order of audit steps, the audit of the plot components, the seed, the advice texts. One more merge is on this branch and NOT pushed: the filter dialog (`a386422a`, 9 commits). Two work branches are not merged at all: `task/recipe-fixes` (6 commits) and `task/smooth-formula` (2 commits, the fix of a formula that runs code). Nothing is in `main`.
4. **How to answer.** By number: "Y3 yes, 7 b, 12 default". A point you do not answer stays open. The "default" in each point is only what is built provisionally or what is proposed. It is not a decision.
5. **Read first.** Part 3 names the files to open before some answers. Points that STOP a build that is waiting come first in each part and say which build.

**Words used once.** *Original recipe*: the recipe HOME opens; it is never edited while auditing. *Audit recipe*: a copy that carries the audit steps; the export is this copy. *T1, T2, T3*: the first stage of a table, its second stage (after the recipe's own steps), and the table of one plot. *Audit step*: one removal or one dropped column that you send to audit with a reason. *Lineage*: the chain of tables a table is built from, and the tables built from it. *Node*: one place of the lineage, for example T1 of one table. *Tick line*: one node where the step is written. *ids*: a list of sample numbers used when a table has no column for the property. *`na` tick*: the choice "keep or remove the rows with no value" in every filter (ADR-103). *Checker*: the program `check_recipe` that judges a recipe file without reading the data. *Advice*: a checker message that is not an error. *Golden baseline*: `app/tests/golden/baseline.json`, the stored hash of every table and plot table of the 7 shipped recipes. *`String`, `Enum`, `Categorical`, `Date`, `Float64`*: Polars types for text, text with a written order, text stored as codes, a calendar date, a decimal number.

**Stage 2** is the build of the new HOME audit (lineage, tick lines, audit recipe); it is not built yet. **Source marks.** `AP1` to `AP26` are the rows of Appendix A. `[F1]` to `[F9]` are the nine source files (list in Appendix B). `ADR-nnn` is `.claude/knowledge/architecture_decisions.md` (line given). `DECnn` is a row of `.claude/design/recipe_format_spec.md`. `L..`/`N..`/`A..` are lines of `tmpAI/panel/adr/ledger.md`. `M129 (57)` is block M129 of `tmpAI/agent_channel.md` from the review session `sparmvet-viz-57`; `(40)` is from the coordinator `sparmvet-viz-40` (the two series use the same numbers). A line number alone is in the file named before it.

---

# PART 1. Yes or no

Each line says what the record says and asks "still right?". A "no" gets one line from you.

## 1A. These stop a build that is waiting

### Recipes and numbers (stops: the recipe fixes, branch `task/recipe-fixes`; the fragments and the ResFinder rule are not built until you answer, M131 (40) :979)

**Y1. The PlasmidFinder list: delete, not wire.** You said: wire the four unwired recipe pieces (N31; M94 (57) "b, c, d, e ... the data-scientist agent wires them"). You also said: what is not current is deleted. For one piece, the old PlasmidFinder field list of `1_test_data_ST22_dummy`, no recipe reads that data, and `2_test_data_ST22_dummy` already has the current list. So the data scientist proposes to delete it. Delete it? yes / no (no: wire it, which adds a table that nothing reads). [F4 fix_list.md:166, :173; M131 (40) :977]

**Y2. The ResFinder tie rule.** You asked for a stated rule for two hits of one sample and one gene that have the same identity and the same overlap (N9; M95 (57)). The proposed rule: keep the one with the lowest accession (text order); if the accession is also equal, keep the first row of the file. On the shipped file no pair is tied. The column `accession` must then be declared as text. Yes? yes / no [F4 fix_list.md:248; ledger N32 `ledger.md:91`]

**Y3. "Best hit": identity first, then overlap.** Your words are "best identity and best coverage". The order of the words is read as the order of the sort. If overlap came first, 4 of the 63 kept rows would be other rows. Yes? yes / no [F4 fix_list.md:247, :292; M95 (57) N9]

**Y4. A step "drop the rows with NaN" before the ResFinder filter.** A failed calculation (NaN) counts as larger than every number. Sorted from the highest, a NaN identity would be kept as the best hit, and "identity at least 90" lets it pass. The step is not in your words. ADR-103 point 5 (`architecture_decisions.md:5287`) already says NaN is handled by explicit steps (`polars_drop_nans`). On the shipped data 0 rows are NaN, so no number moves. Add the step? yes / no [F4 fix_list.md:246]

**Y5. One extra plot for the ResFinder result.** The new table (60 rows) has no plot. The data scientist added one: the number of genes per sample, coloured by class. It is a new picture; no existing picture changes. Without it you would never see the result. Add it? yes / no [F4 fix_list.md:256, :291]

### The audit screen (stops: the audit screen of stage 2, not started. Stage 2 is the build of the new HOME audit. Its build order puts the dialog last: `home_stage2_mechanism_spec.md` part A4, point S2-4, your yes of 2026-11-15)

**Y6. "n ids matched, m not found".** You type or paste sample numbers. A number with a space (" 32557144") removes nothing and says nothing: 42 samples stay. The records say a removal that finds nothing is "a reported no-op, always shown" (`home_audit_steps.md:274`). Show "n ids matched, m not found" and warn when a typed id is not found? yes / no [F3 section C Confirm 1, E8]

**Y7. Plots can be ticked only after the engine can read steps written on a plot.** Today the engine does not read them (`TIER3_READ_BY_ENGINE = False`, `recipe_check.py:47`). The plan builds that reader first (package P5 of stage 2: the part that makes the engine read steps written on a plot). Until it exists a plot is shown only as "this plot reads these numbers". Yes? yes / no. (This is the one-line confirmation waiting in `home_stage2_mechanism_spec.md:67`.) [F3 section C Confirm 2, E9]

### The export (stops: the fix "refuse the export", task listed in `tasks.md:441`)

**Y8. Refuse the export when a plot's audit steps cannot be written as recipe steps.** With the box "recipe and raw data" ticked, such a plot is today left out of the exported recipe; the export names it; nothing else warns. Your rule of 2026-11-15 is "a step the app cannot apply is refused, never skipped" (M124 (57) line 4). Here HOME applies the step; only the writing fails. `tasks.md:441` already calls "refuse" decided, from that same rule. Refuse the export with a plain message that names the plot? yes (refuse) / no (leave out and name) [F1 section C Confirm 17; `original_vs_audit_recipe.md` section C]

### The plot names (stops: the rename of all plot components, `tasks.md:387`: it starts only after you have seen the impact list; read Part 3, R1 first)

**Y9. An old results bundle with old plot names is refused.** M107 (57): no old name is accepted, "not even for a time". A bundle exported before the rename is refused with "did you mean" and the migration command. The converted recipe has a new fingerprint (`data_analysis_recipe_sha256`) but the same data and the same picture. Right? yes / no [F1 V1; `viz_rename_impact_2026-11-15.md:26` (section 1 point 5), `:413`]

**Y10. Register 30 of the 35 plotnine objects that are missing.** ADR-106 point 9 (2026-11-14) says what is missing is listed. M106 (57) (later) says verify that ALL plotnine components are registered. The later wins. 30 need no extra package; 5 do or are not layers. Register the 30? yes / no [F1 V3; document section 8 Q3 `:417`]

### Categorical fields not yet touched (stops: the migration of the date fields; the clean-up of two old files is not done either; M134 (40) :1039 "Not touched")

**Y11. The two date fields (`collection_date`, `submission_date`; three declarations): `Date`, or drop the columns.** M119 (57): they become `Date`, or the columns are dropped if no shipped recipe uses them. No step, plot, filter or join uses them. Read literally: drop. The data scientist advises `Date`, because dropping moves the golden hashes. The three fields are still `Categorical` today (RUN grep: `stress_test_master/.../Stress_Source_input_fields.yaml:16`, `templates/e_coli.yaml:61`, `templates/audit.yaml:29`). Keep `Date`? yes (Date) / no (drop) [F1 C5ab; `categorical_migration_list.md:280-290`]

**Y12. Delete or archive two old files that hold 7 lower-case `categorical` fields.** No recipe includes them. Your rule of 2026-11-15 (M94 (57)): what is not current is deleted or moved to an archive folder, not left for a git search. Delete or archive them? yes (clean) / no (leave) [F1 C7b; `categorical_migration_list.md:8, :334`]

### The Blueprint AI helper (stops: any fix; `tasks.md:435` "Nothing is built before her answer")

**Y13. "Startup is never blocked by an agent misconfiguration" (ADR-076, `architecture_decisions.md:2948`).** Today, with the helper switched on (the `developer` setting only), the start can wait up to 40 seconds if the `claude` command hangs, with no message. The app then always starts. Two readings: (1) "never blocked" means the app always starts: today's code follows the record. (2) It means the start must not wait for the helper: the check must run in the background. Which one? (1) / (2) [F1 Confirm 1; M128 (40) :920-925; `agent_adapter.py:158, :180`]

### The words (stops: the change of the old-words check and the clean-up of old words; nothing is applied before you have seen the exclusions, M132 (40) :984; read Part 3, R3 first)

**Y14. "profile" for the checker's four modes (`run`, `build`, `gallery`, `audit`).** DEC18 (2026-11-13) uses the word. On 2026-11-07 you said "profile" was ambiguous for the deployment, and that word is retired. No turn of yours on the checker's use was found. Keep "profile" for the checker? yes (keep) / no (rename, for example "check mode") [F5 D1; `recipe_check.py:50`; `recipe_format_spec.md:110`]

**Y15. "persona" for the review method (viewpoints of the panel agents).** ADR-091 point 5 retired the word for the app's configuration only. You use it yourself (2026-11-14, session `3ce2c163` turn 1074). 31 lines in about 17 files use it. Keep it for the review method? yes (keep) / no (rename to "viewpoint" or "agent role", about 24 files) [F5 D2; `design_review_personas.md:1`]

**Y16. The settings names `pipeline-*` stay.** Two records disagree. 2026-11-08 (`tasks.md:198`): `pipeline-*` collides with the upstream pipeline, find a new name. 2026-11-12 (`tasks.md:196`, your words `92f68895` turn 8673): rename to `pipeline-simple-exploration`, keep the prefix. The later one wins. The "demo" words (`web-demo-vetinst`) are renamed as you said. Keep the prefix `pipeline-`? yes / no [F5 D7, row 23]

## 1B. The rest, by subject

### The filter dialog (all built on a provisional basis; the push of the dialog does not wait for these)

**Y17. True/false offers "equal" and "not equal" only.** The record says every operator the engine has must be usable from the screens (ADR-104 point 4, `:5312`; your words 2026-11-14 M74), narrowed only for greater/less on text (N06). On two choices "one of" and "none of" mean the same as "equal" and "not equal". Accept the shorter list? yes / no (no: also offer "one of" and "none of") [F7 point 1]

**Y18. Time of day and duration offer comparisons and "between", but no list "one of".** Same record as Y17. Dates and date-times do offer the list. Accept? yes / no (no: add a list of the values present) [F7 point 2]

**Y19. A value finer than the column is refused, never cut.** Example: 1.5 microseconds on a microsecond column: the row is not added, with "Suggestion: write at most the digits of the unit". DEC49 (`recipe_format_spec.md:159`, your decision 2026-11-13) and ADR-104 point 1 say a result is never changed silently. Keep "refuse"? yes / no (no: round and say so) [F7 point 7]

**Y20. A filter "one of" with an empty list is refused with a plain message.** Today it is accepted and gives 0 rows. Your rule: a step the app cannot apply is refused, never skipped. This step can be applied, but it removes every row. Refuse? yes (refuse) / no (keep) [F1 Confirm 16; `tasks.md:449`]

### Reading data files

**Y21. "A value is kept exactly, or the read stops."** Reading today changes some values with no message: `1.234` becomes `1` in a `Decimal` with no digits given, `1.235` becomes `1.24` with two decimals, `1e400` becomes infinity, `1e-400` becomes 0, digits beyond the unit are cut from a date-time. Your rule: "No silent error: that is the rule" (ADR-104 point 1 `:5308`; DEC28, DEC33, DEC49). Apply it to those five cases (the build stops and names the column and the value)? yes / no [F6 typing_at_reading.md section A.0 rows 1, 2, 3, 6, 10; section D point 3]

**Y22. HOME's own table and plot also refuse a value of the wrong type.** The recipe action already does: "the value 2022 is a number, but this column holds text". The two HOME paths pass no `strict` (the switch that makes a value of the wrong type an error; RUN grep: `libs/viz_factory/src/viz_factory/viz_factory.py:258`, `app/modules/t3_audit_engine.py:555`), so text "2022" on a number column is silently converted there. ADR-104 point 7 says the engine is strict and old steps get their type from the column. Make the two paths strict, old saved steps typed first? yes / no [F6 typing_at_reading.md section B.3, D5; M133 (40) :1028]

### The Categorical fields already built (on `dev`; "no" changes them)

**Y23. `NI` stays on the figshare scale `Enum [S, I, R, NI]`.** M119 (57) names the scale S, I, R, NI. No file defines `NI` (the data holds it 405 times, only with breakpoint `clsi`). The data scientist thinks `NI` is not a point on the scale. Built as you wrote it. Keep? yes / no [F1 C1; `categorical_migration_list.md:328`; `fg_phenotypes_input_fields.yaml:17-19`]

**Y24. The stress `value` is `Float64`.** M119 (57): the wrong-type `value` becomes numbers. `Float64` keeps all 10000 values exactly. The other candidate is `Decimal` with two decimals. Keep `Float64`? yes / no [F1 C6]

**Y25. The documented `Categorical` example is `breakpoint` (figshare, 2 values over 18437 rows).** M119 (57): one `Categorical` field stays as the documented example. No record names the field. Keep `breakpoint`? yes / no [F1 C8; `fg_phenotypes_input_fields.yaml:13`]

### The plot names

**Y26. The prefix rule goes into `rules_viz_factory.md`.** `plotnine_` = exactly plotnine, `modif_` = plotnine with a written change, `step_` = the project's own. Your rule: rule files change only after your yes. The text goes into sections 1, 2 and 7 when you have seen it. Yes to that plan? yes / no [F1 V10; `viz_rename_impact_2026-11-15.md:429`]

### The two recipes

**Y27. Until the audit copy is built, today's optional export recipe keeps the name "forked recipe".** `home_audit_steps.md:132` (2026-11-12): "forked recipe" and "audit recipe" mean the same. The code comment says the audit copy is to replace the fork. Keep the old name in the interim? yes / no [F1 Q9, Confirm 4]

**Y28. A one-line note on the three diagrams that are contradicted, and one small new diagram "two recipes".** The review of 2026-11-12 asks your OK for each diagram edit. The full redraw of the seven diagrams comes later. Yes? yes / no [F1 Q8, Confirm 3]

### Rule files and texts

**Y29. Change the four docs pages that teach the old picture, now.** The four old rule-file texts are rows R092, R112, R113, R122 of the rule-file list (Part 3, R2). The record says no rule file changes without your yes (M128 (57)). The four docs pages are not rule files; no record says when to change them. Change them now? yes / no [F1 Q7, Confirm 2]

**Y30. Seven rule-file edits made on 2026-11-14 and 2026-11-15 stay as they are.** Each follows a decision of yours (ADR-104; the NA rule) but your yes to the rule text is not recorded (rows R095, R102, R109, R116 to R119). Say yes to the text as it stands? yes / no [F1 Q10, Confirm 5]

**Y31. Correct the sentence that says an emoji scan is "active now".** `rules_code_quality.md` says it; no such scan exists (RUN: `ls scripts`). Correct the sentence and build no scan? yes / no [F1 Q12, Confirm 6]

**Y32. Rewrite three checker ERROR texts as "what is wrong, then Suggestion:".** M120 (57): "say what happens, then Suggestion: ...". Three checker errors keep the old form. Rewrite them? yes / no [F1 Q14, Confirm 7]

**Y33. The advice texts as built.** The form "what happens, then Suggestion:" is yours (N44). The words of each text are the agent's and marked provisional. Part 3 (the "Also" line) names the file that shows old and new text side by side. One text, ST15 (the warning that a sum of a 32-bit whole-number column can wrap to a wrong total), has one added remedy: declare the column `Float64`, with its cost (about 15 to 16 exact digits). Keep the texts as built? yes / no [`advice_texts_before_after.md`; `tasks.md:418`]

### Who decided

**Y34. `derive_categories` stays removed.** The relaying session wrote "removed as dead" (M56); the spec says "read it, then decide". The code already lacks it (`d63d3f3d`); it was not marked provisional. A lookup is now a `polars_join`. Confirm the removal? yes / no (no: bring it back) [F2 section 3 point 2; ledger L36b]

---

# PART 2. Choose

Each point: what you see or what is at stake; the options; the default; why no record answers it. "Default" is the built or proposed choice, never a decision of yours.

## 2A. These stop a build that is waiting

### The export (stops: every change of the export; M131 (57) :821 "Do not change the export before she answers")

**1. What is always in the export, and what is behind the tick.** Today the standard export holds the plots, the audit steps with their reasons, and `effective_run.yaml` (the hashes and paths of the recipe and of the data). It names the recipe and the data; it does not copy them. The recipe file and the raw data files come only behind one tick "recipe and raw data", off by default. You said on 2026-11-15 that there are two export modes: the results with the recipe and the data used (the data can be replaced, for data produced regularly), and the changes of the audit.
- Part 1. (A) As recorded: the recipe file (in audit mode, the audit recipe) and the raw data together behind one tick, off by default. (B) The recipe file is always in the export; the tick holds only the raw data. This changes the export decision of 2026-11-12 (called P4b, `home_audit_steps.md:346`) and ADR-097 point 1. (C) Two ticks: one for the recipe file, one for the raw data. **Default (A).**
- Part 2. Where does the user choose the data used? (a) When the data is loaded or imported in HOME; the export only names it. (b) A data choice in the export box (in no record). **Default (a).**
- Part 3. The names of the two export modes and of the "reproducibility bundle" (12 places in `app/`, 12 in `docs/`) follow your answer.

Why no record answers: ADR-097 (2026-11-09, you corrected it: mode 1 never holds the recipe) and P4b (2026-11-12, one tick, off by default) say (A). Your words of 2026-11-15 say the export holds "the recipe that produced them, with the data used". Two readings: you meant "names" (the records agree), or you want the file in the standard export. M131 (57) says "Q3 NOT decided". Two older texts (`export_specification.md:81`, `ui_implementation_contract.md:220`) show the opposite and predate ADR-097.
Sources: [F1 section B and Q3], [F2 section 3 point 5], [F5 D9], M131 (57) :816-821, ADR-097 `:4857-4866`, `home_audit_steps.md:346`.

### The audit and the two recipes (stops: the audit screen, stage 2)

**2. [CORRECTED 2026-11-16; Eve decided it: D-0197] Which sample ids "remove these samples from all tables" uses.** The first version of this point said that you tick `country = Norway` at the MLST data file. That is impossible: the file has no `country` column, and a filter is built only in a view whose table has the column (D-0196, "I do not see how it is possible for me to tick country = Norway at the MLST data file"). The case that can happen is this. On `1_test_data_ST22_dummy` you look at the table `MLST_with_metadata`. At T1 it shows 28 Norway samples. At T2 it shows 21, because the recipe's own step keeps only the years 2023 to 2025 and the 7 Norway samples of 2022 are already gone. You select Norway there and choose "remove these samples from all tables". The tables without a `country` column (13 at T1: 10 data files, among them MLST, FastP and Quast, and 3 other tables) get the step as a list of sample ids. Decided: the list is the one of the view where you selected (D-0197: "if you apply the T1 then you will have 28, eg if you apply in T2 there will be 21"). Run on the real engine: with the 21 ids of T2, the 7 Norway samples of 2022 stay in 66 of 73 places, among them 14 of the 17 plots (only `mlst_bar`, `year_distribution` and the aggregate plot are free of them); with the 28 ids of T1 they stay nowhere. So the number depends on where you select, and to remove a sample from the whole lineage you select as early as possible (D-0197: "you need to do that as early as possible in the lineage"). Nothing is asked here; the dialog and the help must say it (text drafts: `tmpAI/panel/audit_model/scenarios_report.md`).
Sources: `tmpAI/panel/audit_model/` (scripts and outputs, S3); `tmpAI/panel/round7/n7_4/result.md` for the one-table case. [This replaces the old point 2; the old text said "the plots are the same", which is true only when ONE table is ticked, not for "all tables".]

**3. What is ticked when the dialog opens.** The dialog lists the nodes where the field exists. Ticking the metadata file by property changes 14 of the 28 tables. With "all ticked", one press on Apply writes the step at every node.
(A) All candidate nodes ticked; you untick. (B) Only the node you chose is ticked; for "remove these samples from all tables" every table with the ID is ticked; the others are listed unticked. (C) Nothing ticked; Apply stays off until you tick one line. **Default (B)**: it fits "the user need to choose" (your words, 2026-11-15) and "Nothing is written that is not ticked" (`home_audit_steps.md:138`).
Why no record answers: two sentences of 2026-11-12, both under "decided ... Eve", differ (`home_audit_steps.md:134` "all ticked" against `:138` "the place the user chose"); M111 does not speak of defaults; the spec line "ticks default to all" (`home_stage2_mechanism_spec.md:128`) is a draft by an agent.
Sources: [F3 Open 2, E10, section B].

**4. A value that cannot be typed at one ticked node.** You write "Year = 2022" at a table where `Year` is a number. A later table holds `Year` as text, because the recipe itself casts it (2 of 43 recipes that build: `Year` in `2_test_data_ST22_dummy`, `year` in `demo_abromics`). There the value is refused: "the value 2022 is a number, but this column holds text". A text "ABC" in a year column cannot occur: reading stops at once (RUN).
(a) That line shows the error and cannot be ticked; the other nodes can be written. (b) Only nodes whose column has the same type as where the value was typed are offered. (c) Drop the rule. **Default (a).**
Why no record answers: the stage-2 spec (`home_stage2_mechanism_spec.md:78, :121`) proposes (a) and marks it as the writer's own; you doubted the case on 2026-11-15 ("I do not see how this is possible", `tasks.md:396`).
Sources: [F6 typing_at_reading.md B, C, D1].

**5. When the audit recipe file is created.** (a) At the first audit step; before that HOME reads the original. (b) When audit mode is switched on. (c) At session start. **Default (a).**
Why no record answers: the records say where the copy lives and that an empty audit uses the original (`home_audit_steps.md:31`, `spaces/HOME.md:47`), not when it first exists.
Sources: [F1 Q4].

**6. The screen words for the two plots and tables.** Today the screen says "Result" and "My view". (a) "Result (original recipe)" and "Audited (audit recipe)". (b) Keep "Result" and "My view". (c) Words of yours. **Default (a).**
Why no record answers: "Result" is in a decided notice text (`home_audit_steps.md:81`); no record gives a word for the audited plot; "My view" is the old model's word.
Sources: [F1 Q6b].

### Recipes and numbers (stops: the recipe fixes; see M131 (40) :979)

**7. Is "unknown[...]" a class of antibiotics when the recipe counts "multi-resistant"?** In `2_test_data_ST22_dummy` the flag Multiresistant is "Yes" when a sample has hits for more than one phenotype. Today 16 of 38 samples are "Yes". 13 of the 70 hits have a phenotype written `unknown[...]`, each counted as its own class. The formula also counts drugs, not classes: sample 11843673 (gentamicin and spectinomycin, both aminoglycosides) is "Yes". Your definition of 2026-04-23: "resistant to more than one class".
(a) Keep as today (16) and say so in the plot title. (b) Leave "unknown" out: 11 samples; 5 change from Yes to No (20545497, 25542390, 29208527, 32557144, 51573804); bars: Germany 2024 "Yes" 2 to 0 (bar gone), Norway 2022 7 to 3, Norway 2024 21 to 17; two pictures change (6.9 and 16.7 percent of pixels). (c) Count classes through the drug-to-class table (10 samples); the table has no row for kanamycin and sulfisoxazole (8 hits each), so you extend it first. **Default (b) now, (c) later** (the coordinator's M131 (40) lists these as (a) leave out, (b) keep, (c) classes).
If (c): which phenotype column feeds the class, "Predicted Phenotype" (used today) or "CGE Predicted Phenotype" (17 samples; the two columns agree on 6 of 70 rows here)? **Default "Predicted Phenotype".**
You should know: "multi-resistant" here means more than one class (your words). The usual surveillance term "multidrug-resistant" means resistance in at least three classes (from memory, not checked). The bars of both multi-resistance plots and the plasmid plot count hit rows (70 for 38 samples), not samples; the new descriptions say so.
Why no record answers: asked as N22 in M95 (40) "No default from me"; no answer in the ledger or in `tasks.md`. Sources: [F4 section A, Q1, Q2, F]; channel :418; M131 (40) :971-972.

**8. Which thresholds does the ResFinder rule use.** You asked for the old minimum identity and coverage, verified, not guessed (N9). The history holds two pairs. Pair 1: identity at least 90 and overlap at least 60 (the AMR tables, commit of 2026-04-23): on the shipped file 70 hits stay 70; 63 after "one row per sample and gene"; 60 rows in the final table. Pair 2: identity at least 90, overlap at least 85 and length ratio at least 0.8 (the detailed summary, commit of 2026-04-10): with overlap alone 34 of 70 hits go and 16 of 38 samples lose every hit; with the ratio 35 and 17.
(a) Identity 90 and overlap 60. (b) Identity 90, overlap 85, ratio 0.8. **Default (a).** A literature source for either pair was never found in the repository (your question of 2026-04-23 stayed unanswered).
Why no record answers: your rule says verify; the check found two pairs, so the ambiguity rule applies. Sources: [F4 section E, Q3]; ledger N32.

**9. Does "one row per sample and gene" also apply to the AMR join of `2_test_data_ST22_dummy`?** Your words name the converted piece. If it applies there: 70 rows become 63; multi-resistant samples go from 16 to 15 (today's formula) or 11 to 10 (point 7 (b)); the sample that flips is 12244317. (a) No, only the converted piece. (b) Yes, both. **Default (a).**
Why no record answers: "AMR genes are given per sample and per gene" (M94 (57) N9) does not name a recipe. Sources: [F4 section E, Q4].

**10. The FastP box plot cannot work as written.** The old plot (`FastP_reads_boxplot.yaml`) draws one box per sample, but the table has one row per sample (42 rows, 42 samples), so every box holds one value. You said wire it. (a) Wire it by source: Broiler 13 samples (median 1,653,504 reads), Layer 19 (2,534,734), Parent 10 (2,468,538). This changes the old intent. (b) Leave it unwired and archive it. (c) You say what the plot should show. **Default (a).**
Why no record answers: your words say "wire"; the data scientist found the old plot cannot be a box plot. Sources: [F4 section D (b)]; M131 (40) :978.

### The plot names (stops: the rename of all plot components; read Part 3, R1 first; each point has the document's own default)

**11. Names that plotnine does not have** (22 names; none is a renamed plotnine object, RUN on plotnine 0.15.4, 0.12.0, 0.5.1). (a) `step_` for any name plotnine does not have. (b) The one-call conveniences (`facet_rows`, `guide_nrow` ...) become `modif_<their name>`; then the prefix says "changed" for a name with no plotnine original. **Default (a).** No record answers: M107 (57) asked for this list. Sources: [F1 V2]; document section 8 Q2 `:415`.

**12. Names written as values** (`geom: geom_area`, `stat: stat_bin`, `position: position_identity`). (a) They stay plotnine's names (they describe a plotnine object; they are not calls). (b) They get the prefix too. The `theme:` key of a plot changes in both cases. **Default (a).** No record speaks of values. Sources: [F1 V5]; document `:421`.

**13. The 15 plotnine objects that cannot be added to a plot** (`element_*`, `position_*`, `guide_legend`, `guide_colorbar`, `guide_colourbar`). (a) `modif_<name>` only; the description says why. (b) Also as a parameter of the component that takes them (for example `position: dodge` on a geom). **Default (a).** No record. Sources: [F1 V6]; document Q6 `:422`.

**14. `guide_label` fails on every use.** (a) Remove it now. (b) Rebuild it on plotnine's own means (verified to work, channel :429). (c) Keep it, renamed. **Default (a) in the rename document; the coordinator's earlier default was (b) (channel :429); `tasks.md:312` says "your choice: rebuild or remove" and `:447` says "fixed and tested".** No record answers. Sources: [F1 V7]; document Q7 `:424`.

**15. The facet and guide conveniences** (21 own components work; only `theme_legend_position` is used by a shipped recipe). (a) Keep all 21 as `step_`. (b) Remove the 9 that an exact plotnine component already does (`facet_rows`, `facet_cols`, `coord_lims`, `guide_title`, `guide_ncol`, `guide_nrow`, `guide_reverse`, `guide_direction`, `guide_none`). (c) Fold the four facet setters into parameters of `plotnine_facet_wrap` and `plotnine_facet_grid`. **Default (a).** M107 (57) asked for the list; no record decides. Sources: [F1 V8]; document Q8 `:425`.

### Functions as a parameter (stops: the `stat_summary` work; `tasks.md:388` "Not on the night queue until she answers")

**16. How a recipe maker gets a mean with an error bar per group (N28).** Plotnine's `stat_summary` can take three functions (`fun_y`, `fun_ymin`, `fun_ymax`); a recipe cannot write a function. Example: `n50` of 42 samples by country (Norway 28, France 4, Germany 10).
- Written as table steps (mean, standard deviation, standard error), the numbers are a table you read and export.
- With `stat_summary` and a name (`mean_se`), the numbers are computed inside the picture and nothing reads them back. Its "standard error" divides by n, not n minus 1: the bar is 13 percent narrower with 4 samples (France 54134 against 62508) and 2 percent with 28. Its default summary (when no `fun_data` is written) is a random bootstrap, half as wide as the usual t interval with 4 samples.
- Named summaries (`mean`, `median`, `min`, `max`, a quantile written as a number, `sd`) each equal the direct plotnine call (difference 0, RUN). The quantile must say "linear" (Polars' own default is "nearest").
(a) Keep the three parameters not offered; teach the table-step route (an example in the gallery and the help). (b) Add named summaries as a `modif_stat_summary` (the exact `plotnine_stat_summary` stays next to it); a `modif_` with the usual n minus 1 formula can be one of them. (c) Both. **Default (a)** (the coordinator's standing default, M99 (40) :471). The data scientist's view: (a) is the most transparent for a published figure.
Already decided, not asked: an advice for `mean_se` and for a `stat_summary` with no `fun_data` (Appendix A, rule "advice when it helps").
Why no record answers: "N28 NOT decided" (M106 (57)); you asked for a concrete example. Sources: [F6 stat_summary.md A to E1, E2, E3]; [F1 V9]; document Q9 `:427`.

### The words (stops: the change of the old-words check and the clean-up; read Part 3, R3 first)

**17. "audit node" and `node_type` for one audit step.** "Node" means a point of the lineage (your words: "I think you call that node"). "audit node" appears in 86 lines of `app/` and 32 of `libs/`, in 22 doc lines; the stored key `node_type` in 94 lines of `app/`. (a) Keep: a node is a point of the lineage and `node_type` is the stored key of a step. (b) Say "audit step" on screens and in docs; keep the stored key. (c) Also rename the stored key (old saved sessions then need a refusal message like `renamed_keys.py:63-69`). **Default (a)** (nothing changes). No record. Sources: [F5 D3].

**18. The words for the reach of an audit step** ("every plot in the project", "project = 0", "extend to the whole project"; 28 live lines in 8 design files, 18 in `home_audit_steps.md`). (a) "every plot of the recipe". (b) "all tables with the field". (c) Keep until the dialog wording review (`home_audit_steps.md:484, :496` "to review together"). (d) Mark those lines as the old model: ADR-105 (2026-11-14, `architecture_decisions.md:5330`) replaced the reach levels 0 to 3 by tick lines of nodes. **Default (c).** The order "recipe overview" covers only the name of the dialog. Sources: [F5 D4, row 9].

**19. "Assembly" for the join.** The rename of 2026-05-04 (ADR-066) is partly done: 2 screen texts ("Data Assembly Failed", "Assembly session found"), 84 doc lines, the action context `assembly`, the stored file `assembly.json`, the folders `assembly/` in recipes. (a) Screen texts and user docs only. (b) Also the code context and `assembly.json` (needs a message for old sessions). (c) Leave: "assembly" is also a real genome word here. **Default (a).** Sources: [F5 D5, row 15].

**20. `WrangleStudio` / `wrangle_studio.py` / `dev_studio` in the code.** The screen says Blueprint and Test Lab already. `Terminology.qmd` says the old names stay as internal names; on 2026-11-07 you said folder and file names must be consistent. (a) Keep (as ADR-068 kept `dev_studio`). (b) Rename the module and the class (195 lines in `app/`; moves files and tests). **Default (a).** Sources: [F5 D6, row 17].

**21. The title "Pipeline Audit" and the `static_web` name.** The panel title "Pipeline Audit" (8 lines in `app/`, 26 in `docs/`) holds "pipeline", which also names the upstream program. The record names `static_web` as "a name to decide". (a) Keep the title. (b) Rename it. (c) Decide with the audit screen build, which replaces the old model. **Default (c).** Sources: [F5 D7, row 23].

**22. The form of the old-words check.** Today the script exits 1 because it flags words that are not old in that meaning (for example the checker's `profile`). (a) Narrow patterns of the old meaning: few exclusions, passes today except real leftovers; a new use of the bare word in prose would pass. (b) Wide words and about 50 path exclusions. (c) Both: wide for `manifest` and `connector`; narrow for `profile`, `project`, `persona`. Also: do the library `README.md` files count as user-facing (19 lines in 5 files)? Is a second test for string literals in code wanted (113 candidates)? **Default (c)** (the form the table in section B is written for). Sources: [F5 D8 and section B].

## 2B. The rest, by subject

### The filter dialog (built on a provisional basis; "default" is what is built; sources [F7], `tasks.md:97-105`)

**23. The list of values served on demand.** A column with more than 1000 different values shows a short list and loads more while you type (10000 values took 6.6 s and 30000 took 87 s with the whole list in the page; 100000 now take 2.0 s). Up to 1000 values the whole list stays in the page. (a) As built (two paths). (b) On demand at every size (one path; the browser tests would wait for the list). **Default (a).** No record. Source: `filter_pickers.proposal.md` "Change 2"; `tasks.md:105`.

**24. A time of day.** Three number boxes: hour, minute, second (the second takes decimals, up to nine digits). (a) As built (Shiny for Python has no time input). (b) One native time input through a small custom input binding (a JavaScript file in the app). (c) One text box "hh:mm:ss" with a check. **Default (a).** No record. [F7 point 3]

**25. A duration.** A number box and a unit list: ns, us, ms, s, min, h, d, w (for example 90 min); the box starts with the largest unit that holds the value exactly (5400 s shows as 90 min). (a) As built. (b) Fewer units (s, min, h, d). (c) One text box "1h30m". **Default (a).** No record. [F7 point 4]

**26. A date and time.** A date picker and the three boxes of a time under it; the dialog says the time is read in the time zone of the column. A time that does not exist (summer time) or exists twice (winter time) is refused with a message; for the repeated hour the dialog cannot choose and says so. (a) As built. (b) One text box "yyyy-mm-dd hh:mm:ss". (c) A date picker, a time box and a time zone choice (not needed today: the column has one zone). **Default (a).** No record. [F7 point 5]

**27. The starting values of the boxes.** For a comparison the box starts at the smallest value of the column; for "between" the two boxes start at the smallest and the largest value (exact, no digit cut). (a) As built. (b) Empty boxes; you must fill them; a missing value is refused. (c) Today / zero. **Default (a).** With (b) nothing is ever filled in for you (`agent_principles.md:7`: "do not choose for the user"). No record. [F7 point 6]

**28. The date box.** The date staged is exactly a date typed in full as year-month-day (2023-02-28; 2023-2-8 is accepted and shown in full) or a day picked in the calendar. Anything else ("2023-0", "abc", "20220305", "03/05/2022", "2023-02-30") is refused with a message and the box keeps the text. The calendar widget used to repair free text (today for a partial text; 2023-03-02 for 2023-02-30); that repair is off. Keyboard-only: you can type the date and Tab; the arrow keys and Enter of the calendar are off, so the calendar needs a mouse. (a) As built. (b) A plain text box with the same strict rule; the calendar is only a helper button (arrow keys can come back). (c) Also refuse 2023-2-8 (only 2023-02-08). **Default (a).** The rule "no silent repair" is yours (Appendix A); the form is not. [F7 point 8]

### Reading data files (no build waits yet; the decided part of the reading work can start, Appendix A)

**29. A `Date` with no `format`.** Today `format` is optional. A file with `03/05/2022` is read as the 3rd of May (day first is guessed); if every date in it is ambiguous, a month-first file is read wrong with no message. A two-digit year `01/01/68` is read as 2068. The module text says "no guessed type" (`declared.py:5`). (a) The checker requires `format` for `Date`, `Datetime` and `Time` (a change of the recipe format). (b) Keep the guess and add an advice when `format` is missing. (c) Leave as it is. **Default (a)** (the data scientist's). Why no record answers: `recipe_format_spec.md:370` says `format` is optional; changing it needs your yes. [F6 typing_at_reading.md A.0 rows 7, 8; D3]

**30. A cell that holds only spaces.** With `strip: true` it becomes an empty text (`''`), while a truly empty cell is a missing value: two kinds of "empty" in one column. The coordinator asked on 2026-11-15 (N23): "an empty cell, also after removing spaces, is always missing, in every column type". (a) That rule. (b) Keep `''` for a cell of spaces. (c) Leave. **Default (a).** Why no record answers: N23 (channel :419) has no answer in the ledger or in `tasks.md`. [F6 A.0 row 14]

### Categorical fields set to `String` that wait for your word (built on `dev`; none of them stops a build)

**31. `quality_module` (values Passed, Warning).** Is there a "Failed"? (a) `String`. (b) `Enum [Passed, Warning]` (a later "Failed" would stop the load). (c) `Enum [Failed, Warning, Passed]` once you give the full list. **Default (a).** The list of verdicts is in no file. [F1 C2]

**32. `year` in the retest recipe** (2022, 2023, 2024). (a) `String` (a 4-digit text sorts in time order; same picture). (b) `Enum ['2022','2023','2024']` (same picture; a new year needs a recipe edit). (c) `Int64` (matches your integer-years decision of 2026-11-13, but a bar chart then treats the year as a continuous axis). **Default (a).** No record weighs the two. [F1 C3]

**33. `status` in the `audit` template.** (a) `String`. (b) `Enum` with the order you give. **Default (a).** The template has no data file in the repository. [F1 C4]

**34. The plotted table of the stress plot.** With `Date` it writes `2023-04-11 00:00:00` where the other tables keep `2023-04-11`. This only matters if you say `Date` in Y11. (a) Accept and say so in the commit. (b) Fix the writing first. **Default (a).** Found by running; no record. [F1 C5c; `categorical_migration_list.md` flag 2]

### Names for functions in plot parameters

**35. Names for label and rescale functions** (`percent`, `comma`, `censor`, `squish`). Today `percent` as scale labels is refused with the misleading "Breaks and labels are different lengths". (a) Add them as names. (b) Do not; a maker writes a list or a label column. **Default (b)** (a recipe cannot hold a function; a list is the transparent form). I did not check whether a shipped recipe wants one of these. No record. [F6 stat_summary.md D, E5]

### The audit

**36. A short pop-up when the open recipe is replaced.** Besides the lasting sentence and the line in Alerts. (a) Keep the pop-up. (b) Sentence and Alerts line only. **Default (a).** No record speaks of pop-ups. [F1 Q2]

### The seed

**37. The seed mechanism built provisionally (the "two seed builds" of the report).** Your decision: fixed at 0 by default, every seed used is written in the recipe or the audit recipe (N01). You also asked whether a special seed field per jitter step can exist (A01). What is built: `random_state: null` and "random" are refused with the fix "write `random_state: 0`" (`54e6979f`); `plot_defaults.random_state` is the one seed of the whole recipe (`6f9479e0`); an audit step pins a seed for one plot (button "Reshuffle") or removes the pin (`653e70b1`). (a) Keep as built. (b) Remove the audit pin; only the recipe seed. (c) Build the seed field per jitter step (not built). **Default (a).** Why no record answers: `tasks.md:306` lists S1 to S3 as "NOT ANSWERED"; A01 has no answer. [F2 section 3 point 6; ledger A01; M85 (40) :233-234]

### Rule files

**38. A type-only import between libraries.** An import that only the type checker reads and that is never used when the program runs. ADR-016 (2026-05-11) allows it between two libraries. `rules_test_lab.md:58` allows it only for standard types in `id_reconciliation`. No library uses it today. (a) Remove only the dead example in `rules_runtime_environment.md:79`. (b) Remove it and say in `rules_test_lab.md:58` that the stricter rule is on purpose for that library. (c) Leave both. **Default (a).** No record says whether the stricter line is on purpose. [F1 Q11]

### Who decided

**39. Who defined the "step compiler"?** (It turns one user step into the registered recipe actions of the audit recipe.) The audit file says "defined 2026-11-12" and names nobody. On 2026-11-12 16:33 UTC you asked "O7 what is the step compiler?"; no later yes was found. (a) You, later, after an explanation. (b) An agent, as a design word. (c) You do not remember: then it is open. [F2 point 1; ledger L27b; `home_audit_steps.md:35`]

**40. Who set the rule "a build on an agent's recommendation is PROVISIONAL"?** `tasks.md:21` says "Eve 2026-11-15". Your chat turns of that day hold no such sentence; it is in the review session's relays (M83, M97, M129). (a) You, in words I did not find. (b) The review session proposed it and you did not object. (c) You do not remember: then it is open. [F2 point 3; ledger N52]

**41. `column` or `columns` for the input column of `modif_` and `step_` actions.** DEC15 (`columns`, a list) and DEC39 (`column`) are both dated 2026-11-13 in the "Eve" column. The code and every shipped recipe use `column`; the stage-2 plan says `column`. (a) DEC15 holds (`columns`). (b) DEC39 holds (`column`). (c) Open. **Default (b).** [F2 point 4; ledger L33; channel :272]

---

# PART 3. Read first

Open these files before the answers named. Each is short in what it asks of you.

**R1. The plot-name document** `.claude/design/viz_rename_impact_2026-11-15.md` (630 lines). Read sections 1 and 2 (lines 17 to 55) before Y9, Y10, Y26 and points 11 to 16. Section 1 says in five points what changes for a recipe maker: every component name gets a prefix, an old name is refused, pictures must not change, an old results bundle runs only after conversion and then has a new fingerprint. Section 2 is the audit in numbers: 232 plotnine objects, 191 registered (123 exact, 46 modified, 22 own), 63 not registered (35 real gaps), and 0 differences found between an exact component and the direct plotnine call. Its own questions are in section 8 (Q1 to Q10); here they are Y9, Y10, Y26 and points 11 to 16 (the document's "Q4" is decided, Appendix AP6). The rename, 535 files and 5185 places, starts only after you have seen it (`tasks.md:387`).

**R2. The list of rule-file changes** `.claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md`. Its first page says what you are asked: say yes or no to the "proposed" rows and answer the "question" rows; look at the applied edits that have no recorded yes; confirm once the applied edits where only the rule text names you. Counts today (RUN count of the rows; the list's own table still says 128 rows, three rows R129 to R131 were added after): **131 rows.** 109 proposed. 3 proposed with a question for you. 4 proposed, wording not written yet (they contradict your two-recipes rule). 3 applied, your yes recorded elsewhere. 5 applied, you named only in the rule text. 7 applied, no confirmation found (five commits: `f8636ff4`, `22a0dc14`, `89043503`, `74abfc48`, `2b13bbdb`). Y29, Y30, Y31 and point 38 are rows of this list. No rule file changes without your yes (M128 (57)).

**R3. The old-words exclusions** `tmpAI/panel/round7/old_words/replacements.md`, section B (lines 79 to 97) and section C (lines 99 to 136). Read before Y14, Y15 and points 17 to 22. Section B lists, word by word, the hits the check flags that are not an old meaning (for example 153 lines for `profile` in 45 files, mostly the checker's own modes and tests). For each it gives the exact exclusion and says whether the check still fails on a real leftover. Today the script exits 1. Section C lists what is left to replace by kind of file: 113 screen texts in 38 files say the bare "recipe"; 112 doc lines in 27 pages; "Must NOT be changed" at the end (history, ADR texts, refusal code, biology words). Nothing is applied before you have seen section B (M132 (40) :984).

**R4. The picture changes of the `Categorical` migration** `tmpAI/panel/round7/categorical_migration_list.md`, "Summary first" (lines 6 to 14), "Flags first" (lines 16 to 26) and section B (line 220 on). Already built on `dev` (`78c620bf`); read it before Y11 to Y12, Y23 to Y25 and points 31 to 34. 32 plots ran; 21 pictures change (20 shipped, 1 template), 11 are identical. In all 32 every count per category is equal before and after, and no value is lost. What changes is the order of the levels, so also the colour each level gets, the order of axis ticks and of panels (the figshare legend was S, R, NI, I and is now S, I, R, NI; sequence types are drawn 10, 101, 117, 131 ... 93, 95 because "alphabetical" is byte order). Section B lists every plot with the order before and after. You decided on 2026-11-15 that a different order of a nominal field is no problem when the counts are equal (Appendix AP5); this is the file that shows what you accepted.

Also, shorter (added by the writer): `advice_texts_before_after.md` (69 lines) before Y33; `n7_4/result.md` (the example run, every table with its numbers) before points 2 and 3; `recipe_fixes/fix_list.md` sections A, E and F before points 7 to 10 and Y1 to Y5 (the ready patches are beside it); `s2_2/typing_at_reading.md` and `s2_2/stat_summary.md` before points 4, 16, 29 and 30; `filter_pickers_points_for_eve.md` before Y17 to Y19 and points 23 to 28. All are under `tmpAI/panel/round7/`.

---

# APPENDIX A. Points that turned out DECIDED (not asked)

Each: what is decided, who and when (only your decisions count), and what is to build. "Built" means in `origin/dev` `78c620bf` unless said.

| # | What is decided | Source (you, date) | What is to build |
|---|---|---|---|
| AP1 | "Undo last", "Revert to step N" and "Remove all" touch audit steps only; "Remove all" gives back exactly the original recipe | `spaces/HOME.md:124` (2026-11-13); `home_audit_steps.md:164, :327-328`; M125 (57) line 3 [F1 Q5] | Three controls in the audit panel; today the panel has only a delete icon per step (`app/handlers/audit_stack.py:566`). The screen word "Remove all audit steps" follows point 6 |
| AP2 | The two recipes are named "original recipe" and "audit recipe" everywhere | M125 (57) :678-686 (2026-11-15); `tasks.md:442`; [F5 row 12] | Records, docs, screen use the two names; retire the nine others. "audit recipe" is on no screen today. ADR texts change only after your yes |
| AP3 | A filter on a column dropped earlier is an error from the engine; steps run in the recorded order; the dialog does not offer a dropped column | M100 (57) your words; M116 (57) "(a) and (a)" (2026-11-15); ADR-105 note [F1 Q13] | Built (`4f299025` on `dev`). The question's old premise ("Send to Audit" staging) belongs to the old dialog |
| AP4 | The equality test copies and the hand-written reference change with the shipped recipe | ADR-099 point 16 (2026-11-12) [F1 C7a] | Built (`8db67b47`) |
| AP5 | Alphabetical order is accepted for nominal fields when the counts per category are equal | M119 (57) your words (2026-11-15) [F1 C9] | Built (`8db67b47`); the pictures are in R4 |
| AP6 | Both spellings `color` and `colour` are registered as separate plotnine components, each proved equal to plotnine | ADR-106 point 9 (`:5362`); "V1 to V10 are OK as recommended" (2026-11-14) [F1 V4] | In the rename: `plotnine_scale_colour_manual` next to `plotnine_scale_color_manual`, and 15 more pairs. Not built |
| AP7 | Rows with no country: the `na` tick is required in every filter step; it starts on "keep" for "is not" and "none of"; the count is shown at the table where the filter runs | ADR-103 (`:5283-5297`, 2026-11-14); M65 [F3 E2] | In the new dialog: the tick starts on keep, the count at each ticked table. Partly built (`na_choice.py:32`, merge `4674b604`, single-table dialog only) |
| AP8 | A tick on the lookup side of a join removes no sample; the numbers per table built from it are shown (42 stay 42, 28 with no country) | `home_audit_steps.md:123, :138, :143, :298` (2026-11-12) [F3 E3] | After a trial run, list every table built from the ticked table with samples and rows before and after. Needs the forward lineage; not built |
| AP9 | A tick on a data file reaches every table built from it, with its counts (ticking the metadata file changes 14 of 28 tables) | ADR-105 point 2 (`:5335`); `home_audit_steps.md:138, :158`; M111 (57) [F3 E4] | A forward lineage function and a trial run over all descendants. Not built (only the backward `build_plot_lineage` exists) |
| AP10 | The same samples removed in one table that stay in another are reported, and the other table is listed unticked | `home_audit_steps.md:143, :138, :134` (2026-11-12) [F3 E5] | After Apply, evaluate the condition on every node with the field and list where it still matches. Not built |
| AP11 | You choose T1 or T2 of a table; both are separate tick lines with numbers | `home_audit_steps.md:135, :138`; `spaces/HOME.md:46` [F3 E6] | Show T1 and T2 as separate tick lines with numbers before and after. Not built |
| AP12 | A tick that removes nothing new, or that empties a table, is a warning or information, never a block | `home_audit_steps.md:604, :610`; M113 (57) your words "Warnings/information can be good - 3 first I agree" (2026-11-15) [F3 E7] | Per ticked node "removes 0 more rows" and "leaves 0 rows" as warnings. Not built |
| AP13 | The 37 missing step descriptions of the shipped pipelines are written; one false description (`demo_join`: "one row per sample", the data gives 28 rows for 15 samples) is corrected | N25 (`ledger.md:84`): "Pipelines recipes need to be fixed ... and anything else" [F4 B] | `patch_B_descriptions.patch`; the checker then gives 0 advice; no table changes (golden check "result-identical"); a new test "no advice on the pipelines". Branch `task/recipe-fixes`, not merged |
| AP14 | The gallery needs no fix: all 34 examples pass the checker and draw their stored picture | N22 (`ledger.md:81`) [F4 C] | Nothing; keep the two existing tests |
| AP15 | The old output-fields list of the phenotype view is deleted | N31 (a) (`ledger.md:90`) | Done on `task/recipe-fixes` (`dbdb0f20`), not merged |
| AP16 | The empty file `config/data_analysis_recipes/experimental/test_logic.yaml` (0 bytes) is deleted | N31 cleaning rule: deleted or archived, not left for a git search [F4 D] | Delete it. Also found: the loader crashes with a raw `TypeError` on any empty recipe a user uploads; a defect for the builder (RUN) |
| AP17 | The join `Detailed_summary_with_metadata` and the richer stress plot `final_plot.yaml` are wired | N31 "b, c, d, e ... wire it" [F4 D (c), (e)] | `patch_D_fragments.patch`. One new table (91 rows, 36 samples). The stress picture changes (43.4 percent of pixels: bars side by side, palette Set1); its plot table does not. Waits for point 10 and Y1 |
| AP18 | The ResFinder piece: rows below the minimum identity and overlap are removed; then per sample and per gene the best hit stays (identity first, then overlap); wire it in a recipe that uses that data | N9, N10 (M94, M95 (57); `ledger.md:91`) [F4 E] | `patch_E_resfinder_rule.patch`: new table `ResFinder_AMR_classes` (60 rows). Waits for point 8, point 9, Y2 to Y5 |
| AP19 | Reading captures the errors of Polars and the type errors in one error form | `tasks.md:396` (M101 (57): "the most important thing") [F6 D2] | One message that names the file, the column, the number of bad cells and the first 3 line numbers with their values; wrap every raw Polars text (Date, Datetime, Time, Decimal, `format`, zone, Parquet). Today 5000 bad cells give the same 3-value message with no file. The detail "stop at the first bad column or list every bad column" is the builder's (default: list every one) |
| AP20 | The checker judges the declaration of a type without data | DEC03 (`recipe_format_spec.md:90`); FD05 (`:621`); N12 "add checker advice always good" (`ledger.md:71`) [F6 D4] | `format`, `time_zone`, `time_unit`, `precision`, `scale` (and scale at most precision), repeated `Enum` levels, an `Enum` level that is also a null word. Today the checker says "no problem" for all (RUN). The list of checks is the builder's |
| AP21 | An advice is added whenever it helps: for the narrow-type cases of reading (`Float32`, huge whole numbers, leading zeros "declare it String if it is an ID"), for `mean_se` dividing by n, and for a `stat_summary` with no `fun_data` | `tasks.md:296` "Always add a checker advice when it helps"; N12 [F6 D3, E2, E3] | Advices with texts; the wording is provisional like Y33 |
| AP22 | A recipe text must not be able to run code: the text of a `geom_smooth` `formula` is checked against an allow-list before it runs | ADR-099 point 14 (`:5126`); N09 (`ledger.md:68`); M133 (40) :1005-1008 [F6 E4] | Branch `task/smooth-formula` (2 commits `cfe1dc22`, `3527855d`, not merged). The builder stops and brings you the example if a shipped recipe uses a form the check refuses. The bug was verified by running (a recipe wrote a file); file the issue |
| AP23 | A text given where a list is meant (`labels: "abc"` draws a, b, c) is a silent error and is fixed | ADR-104 point 1 (`:5308`) [`viz_rename_impact_2026-11-15.md:428`; `tasks.md:447`] | Check and fix with a test that names the error |
| AP24 | The filter dialog follows the type of the column: a date picker; a two-choice control for true/false; no greater/less on text; every type usable | N06 (`ledger.md:65`; M84 (57) point 9, 2026-11-15) [F7] | Built (on the branch, not pushed). The forms of time, duration, date and time are points 24 to 26 |
| AP25 | The calendar widget must not repair free text (today for a partial text; a rolled-over day); an emptied date box means "no date chosen" | ADR-104 point 1 (`:5308`): "No silent error" [F7 point 8; `tasks.md:105`] | Built (`69392b71`, `c19d0b65`). The form of the box is point 28 |
| AP26 | Six old-words points the source marks as already answered: "project" for the repository; refusal tests and tables; "recipe overview"; the short form "recipe" in code; "original recipe"/"audit recipe"; "pipeline" stays for the upstream program | [F5 section D intro, `replacements.md:140`] | Use them in the check (R3) |

---

# APPENDIX B. The source files

F1 `tmpAI/panel/round7/questions_checked.md` (section C: 17 confirmations, 15 open points; checked earlier).
F2 `tmpAI/panel/adr/taken_by_report.md` (section 3: 6 points; ledger `tmpAI/panel/adr/ledger.md`).
F3 `tmpAI/panel/round7/n7_4/points_checked.md` (section C: 2 confirmations, 2 open points; checked earlier).
F4 `tmpAI/panel/round7/recipe_fixes/fix_list.md` and the channel block M131 (40), `tmpAI/agent_channel.md:959-981`. Checked now: `FOR_EVE_notes_checks.md`.
F5 `tmpAI/panel/round7/old_words/replacements.md` (section D: 9 points; section B: the exclusions; section C: what remains).
F6 `tmpAI/panel/round7/s2_2/typing_at_reading.md` and `s2_2/stat_summary.md` (5 and 5 points; the coordinator counted 9, channel :1028). Checked now.
F7 `tmpAI/panel/round7/filter_pickers_points_for_eve.md` (8 points and 2 smaller; the title says seven). Checked now.
F8 `.claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md` (R2).
F9 `.claude/design/viz_rename_impact_2026-11-15.md` (R1).
Records read for the new checks: `.claude/knowledge/architecture_decisions.md` (ADR-103, 104, 105, 106; ADR-099 point 14), `.claude/design/recipe_format_spec.md` (DEC03, 15, 18, 28, 33, 39, 44, 49), `.claude/design/home_audit_steps.md`, `home_stage2_mechanism_spec.md`, `.claude/tasks/tasks.md` sections 1, 5, 6, 7, the ledger, the channel (M80 to M138 of 57; M85 to M134 of 40).

# APPENDIX C. Duplicates merged, and what is not in the list

**12 groups of duplicates, each now one entry:**
1. The export (F1 Q3 and section B; F2 point 5; F5 D9; M131 (57)) is point 1. 
2. The two seed builds (F2 point 6; `tasks.md:306` "S1 to S3 NOT ANSWERED"; ledger A01) is point 37.
3. The names of the two recipes (F1 Q6; F5 row 12; `tasks.md:442`) is AP2; the interim name (F1 Q9) stays Y27.
4. A mean with an error bar (F1 V9; F6 `stat_summary.md` E1 and E2 (b)) is point 16.
5. `column` or `columns` (F2 point 4; ledger Q2 of "questions where the latest cannot be established"; stage-2 plan L18) is point 41.
6. Plots ticked after the reader exists (F3 E9; `home_stage2_mechanism_spec.md:67`) is Y7.
7. What is ticked when the dialog opens (F3 E10, Open 2; M130 (40) Open 2) is point 3.
8. Which ids go to a table with no column (F3 E1, Open 1; M130 (40) Open 1; `tasks.md:361, :400`) is point 2.
9. The four questions of the recipe fixes (F4 `fix_list.md` Q1 to Q4; M131 (40) R1 to R4) are points 7 to 9 (R2 is inside point 7).
10. V1 to V10 (F1 and the document's Q1 to Q10) are Y9, Y10, Y26, points 11 to 16 and AP6.
11. The choices of the filter dialog (F7; `tasks.md:97-105` P1 to P8; `filter_pickers.proposal.md`) are Y17 to Y19 and points 23 to 28.
12. The rule-file edits (F1 Q7, Q10, Q12; rows of F8) are Y29 to Y31 and R2.

**Not in the list, for the records' owners (no decision of yours is needed):**
- Verified defects: the `geom_smooth` formula that runs code (AP22); an empty recipe file crashes the loader with a raw `TypeError` (AP16); a table with a Time or Duration column finer than a microsecond cannot be drawn (`tasks.md:107`).
- Records out of date: `recipe_format_spec.md` section 7.4 says the declared type is given to the reader as `schema_overrides` which "fails strictly"; the code reads text first (`declared.py`). `export_specification.md:81` and `ui_implementation_contract.md:220` predate ADR-097. The text of F8 and `tasks.md:429` says 128 rows; there are 131. `filter_pickers_points_for_eve.md` says seven choices; it holds eight.
- Conflict between records worth a look: `tasks.md:441` calls "refuse the export" decided (see Y8); `tasks.md:312` and `:447` speak of `guide_label` as fixed while you have not chosen (point 14).
- The coordinator's builds that wait for no answer: the 37 descriptions, the first line of the formula, the empty file, the checker hint for the word `categorical` (M134 (40) :1045).

**What this list would not catch.** (1) A decision of yours that exists only in a chat turn and in no record: I re-read none of your turns for F4, F6, F7 (the old-words file did). (2) The "Eve" date column of the spec is taken as your record; a decision entered there by a scribe would pass. (3) Where you said "yes" to a proposal, the ledger counts it as reviewed; it cannot show how closely you read it. (4) Part 1 lines repeat the coordinator's reading of F1 and F3 (checked earlier by others); I re-checked only the state on `dev` (the Categorical fields, the two `strict` calls, the three date fields, the row counts of F8, `origin/dev`). (5) Which build "waits" comes from the records cited at each stop; I did not check the task branches' code.

---

## Added by the coordinator, 2026-11-16 07:08: points 42 to 47 (a recipe or a data file changed while a view is open)

Source: `tmpAI/panel/round7/recipe_in_use/result.md`, section F (an investigation by reading and small runs; nothing was built). No record answers these points. Three defects found by the same investigation are being fixed and are NOT questions (a wrong table stored under an old key; stored tables written in place; a pop-up that says "re-assembling" when nothing is re-assembled).

42. **When the recipe changes while a view is open.** Today HOME shows the new layout on old stored tables, and says nothing unless the recipe now fails its checks. Options: (a) HOME keeps what you opened until you press Reload, and says that the recipe changed; (b) HOME follows the new recipe at once and says so. Default: (a). It agrees with your decision of 2026-11-15 that the export is refused until the audit steps are written into the new original.
43. **Data files.** Today a changed data file is not watched; the export is the only place that always catches it. Options: (a) a check every 2 seconds, like the recipe (cheap: size and time of the files); (b) the warning at the next click and the refusal at export are enough. Default: (a).
44. **Blueprint tells the person who saves** "n views of this recipe are open in this app". It covers one running app only, and no editor outside the app. Options: (a) no, the warning in HOME covers it; (b) yes. Default: (a).
45. **Confirm: Blueprint's save is never blocked** (so there is no lock; a lock file stays behind after a crash, and no lock stops an outside editor). yes / no. Default: yes.
46. **Two users on one app and one user-data folder.** Is that a supported way to run the app? Today they would share the stored tables and the session folder. Options: (a) not supported: the deployment guide says one user per user-data folder; (b) supported: the shared files need a rule (to design). Default: (a), until you decide otherwise.
47. **The Data Import panel writes the uploaded file over the recipe's data path.** For the shipped recipes that path is a test file tracked in git. Options: (a) not intended: an imported file goes to the user's data folder (your decision of 2026-11-14 on imported data; the mechanism was left open); (b) intended. Default: (a).

## Added by the coordinator, 2026-11-16 07:32: point 48, and what your answers Y1 to Y6 changed

48. **The three figshare plots count rows, not samples.** The joined table has one row per test and per gene, for all 980 samples, so each bar counts rows. The descriptions now say so (corrected on 2026-11-16). The plots themselves are unchanged. Options: (a) change the recipe so that the bars count samples; (b) keep the plots and the note. Default: (a).

Answered by you on 2026-11-16 (channel blocks M140 to M145 of the review session), so no longer open: Y1 (wire the PlasmidFinder piece: in work), Y2 (the tie rule: lowest accession, then the first row), Y3 (best hit: highest identity, then highest overlap), Y4 (drop NaN before the filter, with a comment), Y5 (two heatmaps, gene per country and gene per year, plus the plot by class with metadata), Y6 (selectors first; typed ids only where a selector cannot do it, with "n matched, m not found"; reuse the earlier UI where it was good).
Still open for the ResFinder build: point 8 (which thresholds). It is built on the default (identity at least 90, overlap at least 60), marked provisional, written in one place.
