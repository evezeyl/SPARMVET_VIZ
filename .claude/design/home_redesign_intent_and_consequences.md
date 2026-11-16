# The HOME redesign: intent, succession of operations, consequences

**Status after Eve's correction of the first page (2026-11-16).** Her answer is her turn Tcd L2020 (2026-11-16 10:22 UTC), relayed in CH M155; the ledger lines are `D-0143` to `D-0150` (`.claude/knowledge/decision_ledger.md`).
- **Confirmed by Eve on 2026-11-16:** first-page points 2, 4, 5, 6, 7, 8 and 15. Her words: "2. ok. ... 4. correct. 5 correct. 6. yes (this is what we agreed - at usage we might change the default of check box but we can start with that). 7. ok. 8. yes ... 15 good." [READ: Tcd L2020]
- **Corrected by Eve on 2026-11-16, now written in her words:** first-page points 1, 3, 9, 10, 11, 13 and 14. The list of what changed is the last section of this file. [READ: Tcd L2020]
- **Point 12:** CH M155 lists it among the confirmed points, but her turn Tcd L2020 does not mention point 12. It is not confirmed by her words (ledger `D-0151`, RELAYED). [READ: CH M155; Tcd L2020]
- **Under study (she asked agents for pros and cons; she decides after):** audit steps between steps or at the beginning of a list (O13); a readable summary of the added steps in the audit export (O1); a small help button in the audit dialog (O14). [READ: Tcd L2020]
- **Still open:** section (d).
- **Everything outside the first-page points she answered** is the agents' work, checked against her words (two reviews, two reading tests); it is **not** confirmed by her. Until she confirms it, nothing of stage 2, the audit or the export is built from those parts.

**History:** draft 4, 2026-11-16 (task HOME-REDESIGN-INTENT-1). Drafts 1 to 3 (`e9fc1e15`, `ff57c7c6`, `309af561`) were checked by two reviewers and two readers who had only the document (main tree `tmpAI/panel/round7/intent_check/`). Draft 4 applies Eve's correction. Written by reading only; this task changed no code, test, rule file, ADR or other design file.
**Who reads it:** every agent that touches HOME, the audit or the export, before it builds or asks Eve a question.
**What wins:** Eve's own words, the later over the earlier. A record written by an agent counts as hers only where it quotes her or names her with a date; where only a record names her and her own words were not found, the statement says so.

**Labels on every statement.**
- **[READ: source]**: the statement is in a source I read. The source is given.
- **[REASONED: steps]**: derived from READ statements. The steps are given.
- **[ASSUMED]**: not stated by her anywhere I read. Never given as her intent. Used only for the illustrative values of the example.

**Source keys.** Transcripts (`~/.claude/projects/-home-evezeyl-Documents-Insync-gdrive-OBSWORK-20-GITS-SPARMVET-VIZ/`): **T92** = `92f68895-...jsonl` (the HOME session, 2026-11-11 to 11-14); **Tcd** = `cd1b0ac7-...jsonl` (the review session, 2026-11-14 to 11-16); **Tad** = `ad032c0c-...jsonl` (2026-11-04 to 11-11); **T28** = `2836faff-...jsonl` (the recipe session, 2026-11-13). "T92 L9308" is line 9308 of that file, a turn of Eve; times are UTC. Her turns, extracted with their line numbers and dates: worktree `tmpAI/intent_turns/` (not in git). **ADR** = `.claude/knowledge/architecture_decisions.md:line`. **AS** = `.claude/design/home_audit_steps.md:line`. **PF** = `.claude/design/home_preview_filters.md:line`. **S2** = `.claude/design/home_stage2_mechanism_spec.md:line`. **HO** = `.claude/design/spaces/HOME.md:line`. **RG** = `.claude/design/home_audit_reading_guide.md:line`. **SP** = `.claude/design/recipe_format_spec.md:line`. **UC** = `.claude/rules/ui_implementation_contract.md:line`. **HM** = `.claude/design/home_evidence/home_hash_model_2026-11-12.md`. **CH Mn** = block Mn of the main tree's `tmpAI/agent_channel.md` (not in git; line given as CH:line). **LG** = main tree `tmpAI/panel/adr/ledger.md`. **OA**, **QC**, **N74**, **RU** = main tree `tmpAI/panel/round7/original_vs_audit_recipe.md`, `questions_checked.md`, `n7_4/result.md`, `recipe_in_use/result.md`.

---

## First page (read this; correct it in one reading)

1. HOME opens the `original_recipe`; it is the reference and HOME never changes it. Her words: "Blueprint edits recipes for creation. Audit add steps to a copy of an original_recipe : the audit_recipe" (2026-11-16). [READ: Tcd L2020; Tcd L1383]
2. **Exploration** is for looking. A filter there changes only the table you look at. The plot is the Result. Nothing is saved or exported. [READ: T92 L115, L7849; Tad L8704; ADR:5334]
3. "Changes are recorded in the audit_recipe. - correct" (2026-11-16). The audit changes the **data before the plot**; it never changes a plot's recipe. **Deferred, not part of this redesign:** "Some extension of the audit functioning might occur later to allow small aesthetic audit changes on the plot recipe part". The audit is for a few justified removals, not for exploring and not for cleaning messy fields. [READ: Tcd L2020; Tcd L1774; T92 L7815; Tcd L1165]
4. The audit works on a **full copy** of the `original_recipe`: the **`audit_recipe`**. It only adds steps. The original steps in it cannot be edited or removed. [READ: Tcd L1383, L1790]
5. An audit step is a row filter or a column drop. A plot reads its data **after T3**. [READ: Tcd L1774; ADR:5336]
6. The user picks a field. The app shows the lineage back to the roots and forward to every descendant. The user ticks the nodes; what is ticked is what is written. The only automatic placement is the option "remove these from all tables". [READ: T92 L9308, L10291; Tcd L1149; ADR:5335]
7. One step at a time, shown before Apply with rows and entities before and after. A free-text reason is required; a warning needs "I understand"; Cancel changes nothing. [READ: T92 L7953, L9397; AS:568-574; ADR:5337]
8. A step added in the audit can be removed; this touches the `audit_recipe` only. The final steps carry who and when. A separate history log, written by default, keeps the removed steps. [READ: Tcd L1383, L1264; CH M118]
9. "the audit steps can be added at the end of each T1 - T2 - T3 (for now)" (2026-11-16): after the recipe's steps of that list. Steps between steps or at the beginning are under study (O13). The audit steps run in the order recorded, the same in the table, the plot, the bundle and the export; a step that cannot run is an error, never a skip. [READ: Tcd L2020; ADR:5343; Tcd L986]
10. "In the export we need to be able to see original and modified plot. In the ui the original plot and modified plot is activated by compare (same concept we already had define for the audit)" (2026-11-16). [READ: Tcd L2020]
11. Exploration is never exported. "the audit export export the audit recipe with the step of the audit added to the recipe - the reason can be added as #comment" (2026-11-16). A more readable summary of the added steps is under study (O1). [READ: Tcd L2020; Tad L8704]
12. If the recipe or the data changes while an audit is open, the export is refused until the user re-bases the audit. [READ: Tcd L1013; LG line 92]
13. The app informs; "be aware of not over warning - warn only when problem" (2026-11-16); the user decides. It must work for any recipe and any field (data-agnostic); section (b) is an illustration only. A help button in the audit dialog is under study (O14). [READ: Tcd L2020; T92 L3370, L8522, L9167]
14. "My view and plot to show have been re-factored" (2026-11-16): built today are "Plot to show" (Result, My view, Compare) and "Data to show" (Raw, Result, My view) as refactored on 2026-11-05 (`D-0001`) and 2026-11-11 (`D-0014`); My view applies the audited steps in the recorded order (`D-0096`). Not built: the audit-mode switch, the `audit_recipe`, the ticks, and "the engine reading T3" ("was not build yet"). [READ: Tcd L2020; `home_theater.py:439-483, 725-750, 932-1019`]
15. The names `original_recipe` and `audit_recipe` are decided; the words on the screen are open (O5). Open points: section (d). Contradictions: section (e). [READ: CH M125; QC:26-27]

**Words used**
- **T1**: the table after the recipe's tier-1 list (a dataset's own steps and the first steps of a join). **T2**: T1 plus its tier-2 list. [READ: HO:27]
- **T3**: the data passed to one plot: T2 plus that plot's tier-3 list. The list sits at the plot entry, `steps: {tier3: [...]}`, **beside** the plot's specification, not inside it. It holds data steps only, never the plot recipe (geoms, mapping, theme). [READ: AS:162; SP:75, SP:109 (DEC17), SP:452; Tcd L670 (e)]
- An empty list means "the same as the node before": T3 = T2, T2 = T1. Every table has a T2, every plot a T3. [READ: T92 L9231; AS:146; HO:31]
- **Node**: one stage of one table or plot (T1 or T2 of a table, T3 of a plot). **Lineage**: the tree of nodes from the source files to the plots. [READ: AS:27; AS:138; T92 L9308 ("we have a graph/tree")]
- **Tick**: one line in the step dialog that states one write ("write at T1 of table X, read by plots a and b"). [READ: AS:138]
- **Result**: the original plot and the data it reads (its T3, or T2 when T3 is empty). [READ: PF:13]
- **Exploration**: the HOME mode for looking at the data of the open plot; it changes nothing. **Audit mode**: the HOME mode where audit steps are made and removed. [READ: PF:9-11; AS:36]
- **Compare**: in audit mode, the original plot beside the modified plot, an on/off toggle; "the original plot and modified plot is activated by compare" (2026-11-16). [READ: AS:52; T92 L8673 ("the comparison mode is only in audit now"); Tcd L2020]
- **Session**: the saved unfinished work of one recipe on one data set; its name is the recipe hash and the data hash. [READ: T92 L7815; ADR:5238]

---

## (a) The intent, in her own words

### Her principles as they stand (`.claude/workflows/agent_principles.md`, lines 6 and 7, quoted unchanged)

> 2. **Science is transparent and reproducible.** (ADR-090; `ui_implementation_contract.md` section 7.2; `rules_agent_channel.md` section 7.) The same data and recipe give the same rows and the same picture. What a figure shows is what the export contains. Nothing changes a result silently (rows, samples, NA, rounding, order). The export is the Result plus the steps the user sent to audit with a reason; exploration is never exported. A proposal that weakens one of these is flagged first, even if everything else about it is good.
>
> 3. **Deliver robust tools, inform the user, do not choose for the user.** (Eve 2026-11-12.) The software must be right for every recipe, not for one example. Its job is to prevent silent failures, verify results after the fact, and show the user the consequences and the pitfalls so the user chooses. Automatic placement is limited to what Eve decided ("remove these samples from all tables"); everything else is the user's choice, shown with its consequences.

An earlier statement of hers that says the same as principle 3 (CH M139 asked agents to report such a place): T92 L3370, 2026-11-11 19:58: "The software role is to ensure that good data science is done possible and that the user can make informed choice, preventing bad one. Inform, warn - But let user decide." [READ]

### Why the redesign was done (her words, in time order)

- 2026-11-06 14:05, Tad L8704: "before audit its only a 'sandbanbox' playground to discover what the user really wants ... The T1/T2 exploration should never be exported ... but T3 audit is the rule for export." [READ]
- 2026-11-06 12:23, Tad L6807: "it is important that what user sees and what user does - is what it gets at the export and that there is no bug - it is science and it should be correct." [READ]
- 2026-11-11 10:04, T92 L115: exploration filters "should never be written in the parket file, its a temporary exploratoin. T3 should also allow temporary exploration BUT when added to audit and applied with a reason then it should modify the parket file and be registed." Also: "we cant have those showup and do nothing - this will confuse the logic." [READ]
- 2026-11-11 15:19, T92 L1563 (the turning point): "I choose to propagate to all plots but all T3 do not have eg. sample ID column - then I would miss the removal of the bad sample ... HERE we have a big logical problem for the science. If would remove samples but actually show them in the plot. Our T3 audit model is not good. In audit mode we need to be able to change the data T1 and T2 and T3 depending on the propagation choices." [READ]
- 2026-11-11 17:33, T92 L1857: "its to allow a result be publication ready not traficate your data to make them better . that is why I want the audit with justification and why I want it exported also." [READ]
- 2026-11-16 06:26, Tcd L1759: "we have refactored for the scientific logic and reproducibility mostly because it was not correct. But a lot of the UI was good and functionning well ... its an improvement ...but not a total replacement." [READ]

### What must be true for the science (her words)

- **The recipe does what it says.** Tcd L1203, 2026-11-15 18:02: "there will be no tradeoff regarding the recipe : it do what it says it does." Tcd L1368, 19:14: "all the steps in the recipe in home have to be done and all the steps sendt to audit and verified in audit have to be applied ... do what you are instructed to do." [READ]
- **The audit is about data, not plots.** T92 L8142, 2026-11-12 10:08: "the user does not removes from a plot but from data ... the plot is a visualisation of the data." Tcd L1774, 2026-11-16 06:29: "the audit does not change the steps of the plot - it changes the data before the plot - but yes the plot must read the data after T3 is applied." Tcd L1790, 06:32: "we might one day implement minor changes on the plot eg color but not right now." T28 L38, 2026-11-13: "The audit right now consern the data - there is no audit of the plot (not yet ...)". [READ]
- **Two recipes (2026-11-16).** Tcd L2020: "Blueprint edits recipes for creation. Audit add steps to a copy of an original_recipe : the audit_recipe". [READ]
- **T3 is data, not the plot recipe.** Tcd L670 (e), 2026-11-15 08:05: "The T3 is the data that goes to the plot BUT not the plot recipe." [READ]
- **The original stays as evidence.** T92 L8336, 2026-11-12 10:37: "we will still have the original plots : so If we remove those then we still have the proof of why they were removed." [READ]
- **The recipe is as is; the audit only adds.** T92 L8607, 2026-11-12 11:22: "The recipe is as is - we can only add steps not remove those ... a filter in the recipe has a purpose it cannot be removed in the audit." [READ]
- **The audit is a full copy of the recipe.** T92 L10656, 2026-11-13 11:26: "The audit steps are registred in a copy of the recipe ... its important we know in audit that the data and plots that will be shown are from the copied recipe." T92 L10694, 11:41: "as long as we make sure that the user cannot modify the steps that are in the original in the copy." Tcd L1790, 2026-11-16 06:32: "the audit step are added in the audit recipe that is a full copy of the original recipe." [READ]
- **No silent change.** T92 L9167, 2026-11-12 13:14: "what we want is a software that is trustworthy and put warnings if the recipe is not correct, prevent silent failures." Missing values: T92 L8491, 10:59: "We do not remove those silently." [READ]
- **Every change has a reason; before and after are shown.** T92 L9397, 2026-11-12 14:10: "every change in audit from the original recipe need a reason. It must allways be entered - no exception." T92 L9558, 14:36: "I still want the before / after." [READ]
- **The user decides, informed; we stay simple.** T92 L9167: "I do not think we should implement where to remove based on a lot of rules except for the I want to remove this from all tables ... keep it as simple as user to understand otherwise this will never work." T92 L9308, 13:46: "I want with the Tick to make it clear - what is the Tick is what is done. I want the user to take a decision here. Safe ...mode." [READ]
- **Who is responsible for what.** T92 L9650, 2026-11-12 15:08: "We are responsible for transparency and clear functioning . the recipe maker and user are responsible for good practices ... in audit only filters and drops operations are allowed by design." [READ]
- **Data-agnostic.** T92 L8522, 2026-11-12 11:03: "We need to make as data agnostic as possible because we will want to use for other dataset than bioinformatics datasets." [READ]
- **Reproducible and checkable.** Tad L47621, 2026-11-09 10:10: "Science needs full reproducibility - however the users wil not know how to compare the hashes - so we will need to give them a way to do that - withing the app." [READ]
- **Same recipe, new data.** Tcd L1497, 2026-11-15 22:07: "the user will be able to select data to use - to replace the default data used in the recipe ... the purpose being to analyse data produced regularly (pipelines) using the same recipe." [READ]
- **Small, few changes.** Tcd L1165, 2026-11-15 17:47: "we have to advise the user to only send / validate one audit point at the time ... The goal is small change in the data to have publication ready plots (not to do data exploration so we only expect a few changes)." [READ]

### Where she changed her mind (the later word wins)

| Subject | Earlier | Later |
|---|---|---|
| Where an audit step acts | her words, 2026-11-11 13:44, T92 L1224: "I think it should always be applied on T3" | her words, 2026-11-11 15:19, T92 L1563: "change the data T1 and T2 and T3 depending on the propagation choices"; then the lineage and ticks (T92 L9308, 2026-11-12) [READ] |
| Exploration filters and plots | her words, 2026-11-11 12:25, T92 L681: "the plot changes only in my view" | her words, 2026-11-12 08:56, T92 L7849: "In exploration mode we will have only one plot : Results - immutable" [READ] |
| A draft before Apply | her words, 2026-11-12 09:16, T92 L7936: "may be we keep it simple : no preview - send to audit button ?" | her words, 09:21, T92 L7953: "yes : one step preview before validation in audit seems good" [READ] |
| T3 in Blueprint | her words, 2026-11-08 08:10, Tad L24062: "No T3 should exist in blueprint"; 2026-11-09 11:01, Tad L47977: "blueprint will never and should never write T3 - HOME can ... T3 blongs to HOME" | her words, 2026-11-15 08:05, Tcd L670 (e): "blueprint can add to tier 3 for a plot" [READ] |
| Missing values in filters | her words, 2026-11-12 13:33, T92 L9231: "missing values are treated as a real value" | her words, 2026-11-14 18:06, Tcd L178: "follow polars and informs clearly" (ADR-103) [READ] |
| Recipe file in the export | her words, 2026-11-09 10:23, Tad L47649: the normal export "also exports the recipe ... which actually is overkill if we have an export for reproducibility"; 13:11, Tad L50822: "mode 1 - should not contain the recipe"; 13:28, Tad L51145: "remove the things that says never includes ... we have to see those 2 modes as complement of each others not as separate"; 2026-11-12 09:48, T92 L8069: "include recipe and data as one bundle option with the waring" | her words, 2026-11-15 22:07, Tcd L1497: two exports, "one mode where export can be with results in home (the recipe produced this with the data used ...) ... the other mode export the changes in the audit"; same turn: "original and audit recipe correct" (the paragraph whose line 7 is "The export is the audit recipe", S2:19); then 2026-11-16 10:22, Tcd L2020: "the audit export export the audit recipe with the step of the audit added to the recipe - the reason can be added as #comment". Answered for the audit export; what stays open: O1 [READ] |
| Source of truth of the audit | records of 2026-11-11 (agent text): "the step list is the source of truth", AS:245, AS:342; "the step list is derived from" the events, AS:646 (D2) | record naming her, 2026-11-13: the copy is the source of truth, AS:164; her N7-2 of 2026-11-15: the log is separate and the final steps are "not derived from it" (CH:638; Tcd L1264) [READ] |
| Plot changes in the audit | her words, 2026-11-16 06:32, Tcd L1790: "we might one day implement minor changes on the plot eg color but not right now" | her words, 2026-11-16 10:22, Tcd L2020: a later extension "to allow small aesthetic audit changes on the plot recipe part - but this is not part of the current redesign (its a defered task)" [READ] |
| Ticks | record of 2026-11-12 (first version of P5): "tick boxes on the results", "earliest safe point" (RG:110 row P5) | her words, 2026-11-12 13:46, T92 L9308 ("what is the Tick is what is done"); record AS:138 [READ] |

---

## (b) The succession of operations, with one example

**The app must work for any recipe** (T92 L9167; AS:149-160). The example below only illustrates. [READ]
**The example.** The shipped test recipe `1_test_data_ST22_dummy`. Its tables (joins) `QC_Reads_Anchor`, `Quast_with_metadata` and `MLST_with_metadata` hold `sample_id` (AS:123, AS:146); the plots `mlst_bar` and `year_distribution` read `MLST_with_metadata` (N74:16). [READ] Two things the user does:
- **Step A, a removal of samples ticked at two tables:** two samples sequenced badly (illustrative ids `S7` and `S9`) are removed by a filter on `sample_id`, ticked at T1 of `Quast_with_metadata` and at T1 of `MLST_with_metadata`. [ASSUMED: the ids and the choice of tables are mine; the mechanism is READ below]
- **Step B, a filter on the data of one plot:** in `year_distribution`, one category with a single observation is removed at that plot's T3. [ASSUMED: the category is illustrative; "only eg 1 observation" is her own example, T92 L1703]

**1. HOME opens the `original_recipe`.**
- Blueprint edits recipes for their creation; HOME only opens them (Tcd L2020: "Blueprint edits recipes for creation"). [READ]
- The user picks a recipe that passed the load gate; a failing recipe is refused with its reason. [READ: HO:68; ADR:5199; Tcd L858 (N5)]
- HOME builds the original T1 and T2 of each table and stores them by node key. The original never changes. [READ: AS:30; ADR:5237-5243]
- The session is named by the recipe hash and the data hash (`session_key = R[:12]:D[:12]`). [READ: ADR:5238]
- The data used can be replaced by the user, to run the same recipe on new data (pipelines). Where: when the data is loaded or imported in HOME. [READ: Tcd L1497; QC:77 (records: "Load data, replace metadata" panels, HO:76; imported data in its own folder, decided by Eve 2026-11-14 per QC:77)]
- *Stored:* the `original_recipe` on disk (untouched); the original stored tables; no audit yet. [REASONED: from the lines above]

**2. Exploration.**
- The user chooses which node of the open plot to look at: Source, T1, T2 or T3; Source opens a second list with the datasets. [READ: HO:125 ("decided 2026-11-13 (Eve)"); PF:19]
- A filter or column choice changes the table shown, at that node only. [READ: PF:35-36; ADR:5334]
- The plot shown is always the Result, immutable. [READ: PF:37; T92 L7849]
- Changing the node or the recipe clears the preview filters, with a message. [READ: PF:47-49]
- *Stored:* nothing. *Exported:* never. [READ: PF:38-39, PF:50]

**3. The user switches to audit mode.**
- The switch exists only with the sandbox flag. Audit mode needs Compare, sessions and export switched on. [READ: AS:57-62; ADR:5123; T92 L7815]
- The screen shows the immutable Result beside the audited plot (Compare is an on/off toggle). [READ: AS:52; T92 L7849]
- The data and plots of audit mode come from the `audit_recipe`; Exploration reads the original. [READ: AS:164; T92 L10656]
- *Stored:* the `audit_recipe` is a real file in the session folder. When it is first written is OPEN (O2). [READ: AS:164; QC:24]
- While the audit has no step, the `audit_recipe` equals the original. [REASONED: the copy minus its marked steps equals the original (AS:164); an empty step list keeps the node before (ADR:5239)]

**4. Step A is made (nothing is applied yet).**
- The user picks the field `sample_id`, the operator "none of", the ids, and the missing-value tick (`na: keep` or `remove`). [READ: ADR:5335; ADR:5284, 5295]
- The values come from selectors built on the values present; typing only where a selector cannot do it, with a "n matched, m not found" report and a warning. [READ: Tcd L1759, L1774; CH M145, M146]
- The dialog lists, as tick lines, every node where `sample_id` exists, backwards to the roots and forwards to every descendant. [READ: ADR:5335; AS:138; T92 L10291]
- The user ticks T1 of `Quast_with_metadata` and T1 of `MLST_with_metadata`. [READ: AS:138; T92 L9308]
- The dialog shows rows and entities before and after for every table and plot downstream, the later steps that summarise rows, and a preview of the open plot. [READ: AS:138; HO:48; T92 L9558]
- Warn only when there is a problem: "be aware of not over warning - warn only when problem" (Tcd L2020, 2026-11-16). [READ]
- Messages come in three levels: information (nothing to do), warning (the user ticks "I understand"), block (technical only: a column or key that no longer exists, a renamed key, a step the `audit_recipe` cannot represent, a failed recomputation; nothing is applied). [READ: AS:568-574, AS:574 ("decided 2026-11-12, Eve"); T92 L3370]
- A filter on a join key is allowed with a warning that the join may change; a **drop** of a join-key column is refused. [READ: AS:134; RG:114 (the guide's item O12, "From Eve's answers of 2026-11-13: DECIDED ... drop of a key column refused"); her words in that turn: "yes - make fail", T92 L11773]
- A free-text reason is required; no fixed categories; the help suggests a hashtag form (`#technical failure: ...`). [READ: ADR:5125; AS:612; T92 L8522]
- Apply or Cancel. Cancel changes nothing. [READ: ADR:5337]
- *Stored:* nothing yet; the trial computation may sit in the audit cache as one entry. [READ: AS:78]

**5. Step A is applied.**
- The `audit_recipe` gets, at the end of the tier-1 list of each ticked table (the end of the list, "for now", Tcd L2020; O13), one filter step (`modif_filter`), marked `id: audit_<8 hex>_<k>`. [READ: S2:122-123; SP:110 (DEC18)]
- One reason covers the whole action, even though it is written in two places. [READ: AS:333; ADR:5129 (16(f))]
- The audit T1, T2 and T3 of the two tables and of every plot that reads them are recomputed; the original nodes are untouched. [READ: AS:31; ADR:5338]
- After Apply, the same condition is evaluated again on every node that has `sample_id`; the app reports where the samples are still present (here `QC_Reads_Anchor`, not ticked). [READ: AS:143; AS:607 (C3)] [REASONED: `QC_Reads_Anchor` holds `sample_id` (AS:123) and was not ticked]
- *Stored:* the `audit_recipe` file; the step with who and when; a "created" entry in the history log; the session ghost. [READ: AS:164; CH:638 (N7-2); AS:342]

**6. Step B is made and applied.**
- The user ticks only T3 of `year_distribution`. [READ: AS:135 ("a change for one plot goes in its T3")]
- The step is written at the plot entry, in `steps.tier3`, after any steps the recipe maker wrote there. [READ: S2:123; ADR:5222]
- The plot's specification (mapping, layers, theme) is copied unchanged. [READ: AS:162; Tcd L1790]
- `mlst_bar`, which reads the same table, does not change from step B. [REASONED: T3 belongs to one plot (AS:32); a step's effect is what is downstream of its node (AS:133)]
- *Today this cannot run:* the engine does not read `steps.tier3`. [READ: `libs/utils/src/utils/recipe_check.py:46-47, :900`]

**7. The user checks.**
- Compare: the original plot beside the modified plot ("activated by compare", Tcd L2020). [READ: AS:52; Tcd L2020]
- Every node can be shown, original or audit, T1, T2, T3. Only the originals are never changed. [READ: AS:83; ADR:5338]
- A read-only popup per node says what the recipe already does there. [READ: AS:138; T92 L10162]

**8. A step is removed.**
- A step added in the audit can be removed again; it leaves the `audit_recipe` only. [READ: Tcd L1383]
- Her word on undo: "In audit ? the unto is the remove step button" (T92 L11773, 2026-11-13). Her word on what removal does: "could just everything be redone without the step deleted ?" (T92 L1798, 2026-11-11). [READ]
- The records add three controls, "Undo last", "Revert to step N", "Remove all" (AS:327-328; AS:452-459 under "Decided (Eve)" of 2026-11-11; HO:124). Her own words for these three names were not found. The reading guide records the other side: "in audit mode the undo is the remove-step button" (RG:114, from her answers of 2026-11-13; it answers where Blueprint's undo goes, `tasks.md:261`). So HO:124 and AS:327 (three controls) disagree with RG:114. CONFIRM (O11). [READ]
- Removing is "recompute without it"; later steps are kept and re-checked (applied, not concerned, broken). [READ: AS:318-323]
- **The trace:** the final steps no longer hold the removed step; the separate history log, written by default, keeps "removed" with who and when; the final steps are the record that matters. [READ: Tcd L858 ("steps removed are of no use ... what is important is that the final autit steps applied are recorded"), Tcd L880, Tcd L1264; CH:437, CH:638]

**9. Session: leave and come back.**
- A session is for unfinished work. [READ: Tad L47635; T92 L7815]
- In audit it holds the `audit_recipe` (the copy) and its log; restoring recomputes. Exploration filters are not in it. [READ: HO:59; AS:164; PF:50]
- A changed data file changes the session key; "audit steps of old data stay with the old session" is a record (HM section 5 (3), HO:59); her own words cover only recomputation ("when I import data then it should be recomputed", T92 L10022). CONFIRM (O9). [READ]

**10. The recipe or the data changes while the audit is open.**
- The export is refused until the user re-bases: the audit steps are written again into the new original; each is marked applied, not concerned or broken; a broken step blocks the export. [READ: Tcd L1013 ("S2-3: a"); LG line 92; S2:79]
- She also asked whether a recipe in use can be blocked from editing, with a warning. Open (O6). [READ: Tcd L1013]

**11. Export.**
- Exploration is never in the export. [READ: Tad L8704; PF:39]
- The audit export holds the `audit_recipe`: "the audit export export the audit recipe with the step of the audit added to the recipe - the reason can be added as #comment" (Tcd L2020, 2026-11-16). [READ]
- The audit steps, with reasons, who and when, are always in the export. [READ: AS:346; Tcd L880; QC:69]
- The user must be able to see the original and the modified plot in the export: "In the export we need to be able to see original and modified plot" (Tcd L2020). The record adds: the original plot for each plot really affected, labelled "original, no audit" (AS:346). [READ]
- The report text holds, for each figure, a caption "n = ... after exclusions", on by default, never drawn on the figure; the attrition per step (rows and entities, from the source population); `exclusions.tsv`. [READ: AS:614 ("decided 2026-11-12, Eve"); T92 L8544 ("figure caption by default as long as it is in the report text and not on the figure"); ADR:5128]
- `effective_run.yaml` (the hashes of recipe, data, engine, steps) is always written, so two bundles can be compared leg by leg. [READ: ADR:4867-4875; Tad L51061]
- The export is refused if the recipe or the data changed since the view, or if a step is broken. [READ: AS:325; QC:75]
- A review before the export (a methods paragraph, the attrition, the acknowledged warnings): a record says "accepted (Eve)" (RG:110, O7); her words found ("O7 ok", T92 L10162) answer only the step compiler. CONFIRM (O12). [READ]
- A more readable summary of the added steps, and what the older records on the two ways of exporting still leave: see (c) C9 and (d) O1.

**12. Import (gated).**
- Import is its own function, switched on by the configuration, for an authorised person. [READ: AS:348; T92 L8694]
- An invalid recipe blocks the import; the verification legs report match, mismatch or not checked and do not block. [READ: HO:58; ADR:4972]

---

## (c) The consequences, derived step by step

**C1. Nothing can be left out of the export.** [REASONED] (1) The `audit_recipe` is a full copy of the original (Tcd L1790). (2) The audit steps are added to that copy (Tcd L1383). (3) The plot's specification is in the copy, unchanged (AS:162). (4) So every plot can be written in the exported `audit_recipe`. (5) Every audit step must be applied (Tcd L1368), and nothing may fail silently (ADR:5308); a step that cannot run is an error, never a skip (ADR:5343). So the export's present skipping (E3) is against this.

**C2. A plot reads its data after the last tier.** [REASONED] (1) An audit step changes data, not the plot (Tcd L1774). (2) Every plot has a T3, equal to T2 when empty (T92 L9231; AS:146). (3) So the data reaching a plot is its T3: the maker's T3 steps, then the audit's T3 steps. (4) The engine must read `steps.tier3`; today it refuses a non-empty one (`recipe_check.py:900`). Y7 is answered by this (Tcd L1790).

**C3. A step is applied at the nodes the user ticks, and nowhere else.** [REASONED] (1) "What is the Tick is what is done" (T92 L9308). (2) The only automatic placement is the option "remove from all tables" (ADR:5335; T92 L9191). (3) So an unticked node keeps its rows, and the app says where the condition still matches (AS:143). Which lines are ticked when the dialog opens: O3.

**C4. Removing touches audit steps only; removing all gives back the original.** [REASONED] (1) Original steps cannot be edited or removed in the copy (Tcd L1383; AS:164). (2) A removal deletes steps. (3) So a removal can only delete marked audit steps; with none left, the `audit_recipe` equals the original. Which buttons exist is O11.

**C5. Who edits what, where.** [REASONED] (1) Full recipe edit only in Blueprint (Tcd L1383). (2) Blueprint may write a plot's T3 data steps (Tcd L670 (e)). (3) The audit writes only filters and drops into the `audit_recipe` (T92 L9650; AS:162). (4) So: Blueprint edits the original (all tiers, the plot specifications); HOME adds or removes its own steps in the `audit_recipe` only.

**C6. Exploration is a sandbox and is never exported.** [REASONED] (1) Exploration changes only the table shown (ADR:5334). (2) It is never saved (PF:50). (3) The export holds what the user validated with a reason (Tad L8704; principle 2). (4) So no exploration filter can reach a plot, a stored table, a session or an export.

**C7. One order everywhere.** [REASONED] (1) "All the steps in the recipe ... have to be done and all the steps ... in audit have to be applied" (Tcd L1368). (2) Audit steps go at the end of the list of their node (AS:135; S2:123). (3) Within a list the recorded order is the order run, everywhere (ADR:5343; Tcd L986). (4) The node keys chain T1 to T2 to T3 (ADR:5239). (5) Her word of 2026-11-16: "the audit steps can be added at the end of each T1 - T2 - T3 (for now)" (Tcd L2020). (6) So the run order is: T1 (recipe steps, then audit steps), T2 (recipe, then audit), T3 (recipe, then audit). The table, the plot and a re-run of the exported recipe give the same rows, or the same error.

**C8. The original plots are evidence, not leftovers.** [REASONED] (1) T92 L8336. (2) The Result is immutable (T92 L7849). (3) So the export carries the original plot beside each affected audited plot (AS:346), and a QC plot can stay unaudited to justify a removal elsewhere (T92 L8114).

**C9. The export after her words of 2026-11-15 and 2026-11-16.** [REASONED] (1) She confirmed line 7 of the paragraph: "The export is the audit recipe" (Tcd L1497; S2:19). (2) On 2026-11-16 she answered: "the audit export export the audit recipe with the step of the audit added to the recipe - the reason can be added as #comment" (Tcd L2020). (3) In the same answer: "In the export we need to be able to see original and modified plot" (Tcd L2020). (4) Her later words win over the records of 2026-11-09 (ADR:4857-4866) and 2026-11-12 (AS:346). (5) So the audit export holds the `audit_recipe` file, with the steps added and the reasons as comments, and both plots. (6) What her answer does not settle is in O1.

**C10. When the recipe or the data changes.** [REASONED] (1) The export is refused until re-base (Tcd L1013). (2) The original keys change with the recipe or the data (ADR:5238-5239). (3) The `audit_recipe` names its original by hash (AS:164). (4) So a mismatch is the signal; nothing is exported from a mix of old and new.

**C11. What a session stores.** [REASONED] (1) The session is unfinished work (T92 L7815). (2) In audit it holds the `audit_recipe` file and its log (AS:164; CH:638). (3) Exploration filters are not in it (PF:50). (4) So restoring gives back the audit, not the exploration.

**C12. One step at a time.** [REASONED] (1) One candidate is previewed in a modal dialog (ADR:5337). (2) She advises one audit point at a time (Tcd L1165). (3) So there is no staged list in audit mode and no Apply gate in the panel (AS:75).

**C13. Y8 dissolves.** [REASONED] (1) Y8 came from the export form that forks a join per plot and repoints the plot (OA section C; `t3_translator.py:213`). (2) With a full copy, steps go into the copy's own lists (S2:123); no join is added and no plot is repointed. (3) So there is nothing to refuse (Tcd L1790).

**C14. The trace of a removed step.** [REASONED] (1) The final steps are the record that matters (Tcd L858). (2) The history log is separate, written by default, and the final steps are not derived from it (CH:638; Tcd L1264). (3) So a removed step is absent from the `audit_recipe` and the final steps, and present in the log with who and when; turning the log off is the only way to lose that trace (CH:519).

---

## (d) What is still open

**O1. The export: what is answered and what remains.**
- **Answered (2026-11-16):** the audit export holds the `audit_recipe` with the audit steps added, and the reason can be a `#` comment: "the audit export export the audit recipe with the step of the audit added to the recipe - the reason can be added as #comment" (Tcd L2020). The user can see the original and the modified plot in the export (Tcd L2020). The former question "Q3, is the audit recipe always in the export?" is answered in this direction. [READ]
- **Under study (her request; she decides after):** a more readable summary of all the added steps, "without the user having to read the whole recipe - maybe export the audit steps as it sees them in the ui in an audit step file record that is human redeable ?" (Tcd L2020). Options named in CH M155: the reasons as comments only; a separate readable audit-steps file; a table in `report.qmd`; more than one. Agents named in her words: "the data scientist and software architec and user". [READ]
- **Not settled by her answer (open, not resolved here):**
  - The results export of HOME without audit: she described it on 2026-11-15 as "the recipe produced this with the data used" (Tcd L1497); the records say the standard export names the recipe and the data by hash and holds neither file (ADR:4857-4866, 2026-11-09; AS:346, 2026-11-12). Does it hold the `original_recipe` file?
  - The raw data files: with the recipe or behind a tick with the sensitive-data warning. Her words: "raw data can be sensitive - recipe is not expected to be" (T92 L8062, 2026-11-12); "include recipe and data as one bundle option with the waring" (T92 L8069, 2026-11-12).
  - One zip or two bundles: "we might have a both also so it exports 2 different bundles in one eg. ziped archive" (Tad L47663, 2026-11-09); the two modes as "complement of each others" (Tad L51145, 2026-11-09).
  - Supports for every reading: the audit steps "are still kept in the 'normal' export because they contain the justification" (Tad L47649, 2026-11-09); "it is the data used that is exported ... not the default data" (Tad L3298, 2026-11-05).
- Sources: Tcd L2020, L1497; CH M131, M155; S2:19; ADR:4857-4866, 4900; AS:346; Tad L47649, L47663, L50822, L51145; QC:94-103.

**O2. When the `audit_recipe` file is first written** (first step, switching audit on, or session start). No record and no turn of hers answers (QC:24).

**O3. What is ticked when the dialog opens.** AS:134 and S2:128 say "all ticked by default"; AS:138 (same day) says "the place the user chose is ticked; other places are listed unticked". Her words: "I want the user to take a decision here. Safe ...mode" (T92 L9308) and "the user need to choose at which point" (Tcd L1149). Readings: (a) only the node the user chose; (b) all candidates; (c) none. (CH M130, Open 2.) Her word of 2026-11-16 on the ticks: "this is what we agreed - at usage we might change the default of check box but we can start with that" (Tcd L2020): the default may change after use, not now; which default to start with is still this point.

**O4. Which ids reach a ticked table that lacks the field.** Her words: "country commes from metadata so removal means cannot be removed at T1 but can be removed at T2 or T3" (T92 L8831, 2026-11-12 12:44); "the user should go in the metadata schema - find all samples that are from norway and remove the samples from there" (T92 L9111, 13:03); later "it maybe need actually to have the choice where" (T92 L9191). Example: `country = Norway` gives 21 samples at T2 and 28 at the root (N74:24-37). Readings: the 28, the 21, or the user chooses (CH M130, Open 1).

**O5. Screen words for the two plots and tables** ("Result" and "My view" today, in the refactored strip, `home_theater.py:966-981`). The recipe names are decided (CH M125; QC:26); the screen words are not (QC:27).

**O6. A recipe in use.** Should Blueprint warn when it saves a recipe open in HOME, or block it? Should a data file be watched? Her question: Tcd L1013. Points 42 to 47 of CH M138 wait for her.

**O7. Spec-level `filters` against `steps.tier3`.** A plot specification may hold `filters`; the recommendation R1 keeps them until the engine reads `steps.tier3`, then migrates them and refuses them (P06). R1 is "recommended, awaiting Eve" (SP:177, SP:471, SP:660; S2:67 asks for her confirmation).

**O8. A typed value that does not fit a ticked node (S2-2).** The spec's default: that tick line shows the error and cannot be ticked (S2:78). Her answer: "I do not see how this is possible ... we need to capture errors in types in columns ... I would need example when this could happen but verified first by the data scientist" (Tcd L998, 2026-11-15). Not decided.

**O9. Data changed, session.** "Audit steps of the old data stay with the old session" is a record (HM section 5 (3); HO:59); her words cover only recomputation (T92 L10022). CONFIRM.

**O10. The final place of the recipe overview, and its display.** Decided: the recipe overview is built as accordions in the right panel, with one switch that moves it into a dialog (ADR:5183, "DECIDED 2026-11-15 (Eve)"); the step list stays in the right panel, slightly wider, adjustable (HO:124, decided 2026-11-13). Her words: "it can be coded so its easier to change place ... difficult for me to decide without trying it" (Tcd L880). Open: only the final place (panel or dialog), after trying it, and the display (colours, insertion point, where the lineage joins), for which she wants proposals first (Tcd L1264; CH M118).

**O11. The undo controls.** Her word: "the unto is the remove step button" (T92 L11773). Records: "Undo last", "Revert to step N", "Remove all" (AS:327-328, AS:452-459, HO:124). Readings: (a) only a remove button per step; (b) the three controls as well. What they touch is not open (C4).

**O12. The review before the export and the history log in the export.** The record "accepted (Eve)" (RG:110, O7) bundles the step compiler, the event log, the pre-export review and D1-D14; her words found ("O7 ok", T92 L10162) answer the step compiler. The log is "written by default" (CH:638). CONFIRM: the review screen before the export; the log inside the export bundle.

**O13. Audit steps between steps or at the beginning of a list (under study).** Decided for now: at the end of each T1, T2 or T3 list (Tcd L2020). Her question: "Unless there is a good way to allow adding audit steps between steps or at the beginning of each Tx recipe - please have the coordinator launch agents - to see how this should be possible - and if it would be wise - we come back to this point when we have an answer of pros/cons from the data scientist and software architect." Her reasoning: "because the table we see when we select T1, T2, T3 are the data produced at the end of this step I would suppose if would be more consistent to only at steps at the end of T1, T2, or T3 - to ensure that it says comprehensible from a user and data science point of view." (Tcd L2020, 2026-11-16) [READ]

**O14. A help button in the audit dialog (under study).** Her words: "Investigate if maybe a little addtional help button could help the user get more information while doing audit or if the general help is sufficient. Again ask several agents." (Tcd L2020, 2026-11-16) [READ]

**Deferred, not part of this redesign.** Small aesthetic audit changes on the plot recipe part: "Some extension of the audit functioning might occur later to allow small aesthetic audit changes on the plot recipe part - but this is not part of the current redesign (its a defered task)" (Tcd L2020, 2026-11-16). [READ]

---

## (e) Where today's build, the spec, the rule files or the docs contradict (a) to (c)

Some entries are contradictions **between two records**, reported here as found and not resolved by this page: E9, E11, E13, E14, E17, and the older sentence AS:135 ("a step is written at **one** of these") against the tick lines that write a step at several nodes (AS:138). They are not errors of this page.

| # | Place (file:line) | What it says or does | Contradicts |
|---|---|---|---|
| E1 | `app/handlers/home_theater.py:932-1019` (the strip), `:439-483` (the plot on My view), `:725-750` (Compare) | Built in the refactored form (her word, 2026-11-16: "re-factored"): "Plot to show" Result / My view / Compare (Compare gated by `comparison_mode_enabled`, `:975`); "Data to show" Raw / Result / My view; My view exists whenever Filters exist, also without the sandbox flag (`:932-948`); on My view the plot applies the exploration filters, then the audited steps in the recorded order (`:469-473`); Compare = T2 left, My view right (`:739-750`) | Built as decided on 2026-11-05 and 2026-11-11 (`D-0001`, `D-0014`) and 2026-11-15 (`D-0096`). Not yet the target of `D-0016`/`D-0019` (audit mode with Compare; one immutable plot in Exploration; exploration filters change the table only, ADR:5334): to replace when audit mode is built (AUDIT-REPLACE-1) |
| E2 | `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:30-40, :213` | the export forks a join per plot and repoints the plot | C1, C13 |
| E3 | `app/handlers/export_handlers.py:1303-1311` | plots whose steps cannot be translated are left out of the re-runnable recipe, with a warning; their steps stay in the publication part | C1; Tcd L1368; ADR:5308 |
| E4 | `libs/utils/src/utils/recipe_check.py:46-47, :900` | `TIER3_READ_BY_ENGINE = False`; a non-empty `steps.tier3` is refused | C2 (not built yet, S2:148 P5) |
| E5 | `app/handlers/audit_stack.py` (no match for "Undo", "Revert", "Remove all") | only a delete per step | Not a contradiction if O11 (a); a gap if (b) |
| E6 | UC:10-17 | original (violet) steps with a power icon, a trash with a modal, `btn_revert` full wipe, nodes dragged above or below | First page 4 (no "superseded" mark) |
| E7 | UC:458, :462, :473, :641; `.claude/rules/rules_ui_dashboard.md:13` | the step type `developer_raw_yaml` still listed | Removed (AS:125; refused in code, `app/modules/renamed_keys.py:186`) |
| E8 | AS:245, AS:342; AS:646 (D2) | "the step list is the source of truth"; the step list "derived" from the events | AS:164 (2026-11-13); N7-2 (CH:638): the log is separate, steps not derived from it |
| E9 | AS:134 vs AS:138; S2:128; HO:46 | "all ticked by default" vs "only the chosen place ticked" | Internal contradiction; O3 |
| E10 | HO:37, HO:45 | "Missing values are a visible, selectable value"; a value "converted to the type of each column" | ADR-103 (the `na` tick); ADR-104 point 7 (no conversion; a wrong type is an error) |
| E11 | S2:79 | S2-3 under "New, to answer here" | Decided (a) on 2026-11-15 (Tcd L1013; LG line 92) |
| E12 | `docs/user_guide/understanding_your_export.qmd:12`; `export_handlers.py:571` | "This standard bundle never contains your data analysis recipe"; tick "Also include a reproducibility/reimport bundle" | Her words: the audit export holds the `audit_recipe` (Tcd L2020, 2026-11-16) and the results export is "with the data used" (Tcd L1497). Wrong for the audit export; the wording for the results export waits for O1 |
| E13 | Diagrams `HOME-AUDIT-LINEAGE`, `HOME-AUDIT-FLOW`, `HOME-AUDIT-EFFECT` (`docs/UML/app.mdj`) | levels 0-3, reach selector, reason categories | Contradicted since 2026-11-12 (`home_evidence/home_uml_review_2026-11-12.md` rows 1-3); no banner |
| E14 | Diagram `UI-HOME-AUDIT` (`docs/UML/diagrams/UI-HOME-AUDIT_The_screen_with_audit_mode_on.png`) | "reach selector, nothing preselected"; "reason category + reason" | Ticks along the lineage (ADR:5335); free-text reason (ADR:5125) |
| E15 | Names | the `audit_recipe` has nine names in records, diagrams, docs and code; none on the screen | One pair of names everywhere (CH M125; OA section B) |
| E16 | UC:204 (rule 4); UC:220 (bundle table) | audited steps applied to the export "from any view" (My view model; lists `aesthetic_override`); `data_analysis_recipes/<proj>/` "all YAML ... files" in every bundle | My view is replaced (ADR:5083); `aesthetic_override` out of scope (AS:125); the audit export holds the `audit_recipe` (Tcd L2020, 2026-11-16); the results export is O1 |
| E17 | RG:87 (section 1 point 3) | "there is no automatic placement" | ADR:5335; principle 3: the option "remove from all tables" is the one automatic placement |

### What was good in the earlier UI and is to be reused (her words of 2026-11-16: "an improvement, not a total replacement", Tcd L1759)

- **Selectors built on the existing values**, with search, as before; typing only for the reason. [READ: Tcd L1759]
- **The Filters panel and its form**, shared by Exploration ("Add to preview") and audit mode ("Create audit step"). [READ: AS:51; PF:25-29]
- **The centre plot and table components**, fed with the audit data; Compare already has two panes. [READ: AS:52, AS:100-102]
- **The right Pipeline Audit panel** (slot `audit_stack`), kept for the step list; dropped from it: the "Inherited (T2)" nodes, the pending badge, the Apply gate, the plot style panel. [READ: AS:53; HO:124]
- **The error surface, the "recalculating" overlay, the Alerts panel.** [READ: AS:51, AS:286]
- **The session and export panels**, extended. [READ: HO:57-59]
- Which piece is kept, adapted or replaced, piece by piece, is a separate inventory (CH M145, M146); not done here.

---

## Sources read (with dates)

**Transcripts** (Eve's turns extracted with the automatic summaries removed; script and extracts in worktree `tmpAI/intent_turns/`). **Read in order, every turn of hers:** `92f68895` and `cd1b0ac7` (up to 2026-11-16 06:39), and `ad032c0c` for 2026-11-08 to 11-11 (by the second reviewer). **Only searched by keyword:** `ad032c0c` for 2026-11-04 to 11-07, and all the others.
| File | Dates (UTC) | How read |
|---|---|---|
| `4f9d21b6-...jsonl` | 2026-11-04 13:04-13:13 | listed (2 turns) |
| `82e7337d-...jsonl`, `b7fd8e77-...jsonl` | 2026-11-04 14:53 | listed (1 turn each) |
| `ad032c0c-...jsonl` | 2026-11-04 15:12 to 11-11 09:30 | 264 turns; by me searched by keyword (audit, export, T3, exploration, session, reproducib), turns read in full around the hits; the turns of 2026-11-08 to 11-11 read in order by the second reviewer (`intent_check/review2.md` section 3) |
| `902da972-...jsonl` | 2026-11-07 07:45 to 11-14 10:07 | searched; no redesign turn found |
| `92f68895-...jsonl` (HOME session) | 2026-11-11 09:41 to 11-14 13:47 | all 158 turns of Eve read in order |
| `9b22d54e-...jsonl` | 2026-11-11 10:15 | listed |
| `2836faff-...jsonl` (recipe session) | 2026-11-13 09:20-20:48 | searched (audit, T3, copy, export) |
| `3e9e5fed-...jsonl` | 2026-11-14 13:02-13:36 | searched |
| `3ce2c163-...jsonl` (coordinator) | 2026-11-14 13:48 to 11-16 06:44 | searched (her pasted briefs) |
| `cd1b0ac7-...jsonl` (review session) | 2026-11-14 17:18 to 11-16 06:39 | all 96 turns of Eve read in order |

**Records** (worktree at `472c0ff2`): ADR-097 to ADR-106 (ADR:4806-5370); `home_audit_steps.md` (all); `home_audit_reading_guide.md` (all); `home_preview_filters.md` (all); `home_stage2_mechanism_spec.md` (all, v0.2); `spaces/HOME.md` (all); `recipe_format_spec.md` (rows on HOME, the audit, tier 3 and the export: lines 6-7, 66-75, 107-118, 145, 177, 205-207, 381-407, 452-471, 630, 658-660); `ui_implementation_contract.md` section 1 (lines 10-17) and section 7.2 (lines 186-232); `export_specification.md` (heading, status); `home_evidence/home_hash_model_2026-11-12.md`, `home_audit_view_from_copy_2026-11-13.md`, `home_uml_review_2026-11-12.md`; `handoff_active.md` (searched; lines 503-504); `tasks.md` (searched: lines 82, 83, 94, 261, 397, 424); `.claude/workflows/agent_principles.md`; diagram picture `UI-HOME-AUDIT`.
**Main tree, not in git:** `tmpAI/agent_channel.md` blocks M118-M149 of the review session and M120-M139 of the coordinator; `tmpAI/panel/adr/ledger.md` (searched); `tmpAI/panel/round7/original_vs_audit_recipe.md` (all), `questions_checked.md` (rows Q3-Q9, section B), `n7_4/result.md` (sections 0 to B), `recipe_in_use/result.md` (sections 0 to A2); `intent_check/review1.md` and `test1_answers.md` (the check of draft 1).
**Her answer of 2026-11-16:** her turn Tcd L2020 (10:22 UTC) read in full; CH M155 (main tree, line 1295) read twice; `.claude/workflows/decision_compliance.md` and `.claude/knowledge/decision_ledger.md` read (worktree `intent-doc-2` at `77b663f1`; none of the records cited above changed between `472c0ff2` and `77b663f1`, checked with `git diff --stat`).
**Code checked** (worktree): `home_theater.py:425-484, 705-760, 925-1021` (re-read at `77b663f1`); `filter_and_audit_handlers.py:144, 479-486`; `home_theater.py:433-469`; `t3_translator.py:30-40, 213`; `export_handlers.py:571, 1303-1311`; `recipe_check.py:46-47, 900`; `audit_stack.py` (search); `renamed_keys.py:186`.

**Not read:** the UML pictures other than `UI-HOME-AUDIT`; the archive tag `archive/home-filters-uml-2026-11-11`; `recipe_format_spec.md` outside the rows named; `export_specification.md` in full; `home_evidence/home_attrition_report_2026-11-12.md`.

---

## Changes of 2026-11-16 after Eve's correction

Her answer: Tcd L2020 (2026-11-16 10:22 UTC), relayed in CH M155. Only the first page is listed; the later sections were changed to agree with it (the status at the top, the words box (Compare), the table of changes of mind (two rows), the succession steps 1, 4, 5, 7 and 11, the consequences C7 and C9, the open points O1 (rewritten), O3 and O5, the new O13, O14 and "Deferred", the contradictions E1, E12 and E16, the sources). Points 2, 5, 6, 7 and 12 did not change; point 12 is not confirmed (see the status).

| First-page point | Old sentence | New sentence |
|---|---|---|
| 1 (corrected by Eve) | HOME opens the **original recipe**. It is the reference. HOME never changes it. Only Blueprint edits a recipe. [READ: Tcd L1383; confirmed, Tcd L1497] | HOME opens the `original_recipe`; it is the reference and HOME never changes it. Her words: "Blueprint edits recipes for creation. Audit add steps to a copy of an original_recipe : the audit_recipe" (2026-11-16). [READ: Tcd L2020; Tcd L1383] |
| 3 (corrected by Eve) | In HOME, audit mode is the only place where a change is recorded that reaches the audited tables, the audited plots and the export. It adds steps that change the **data before the plot**; it never changes a plot's recipe (a colour change: "one day ... but not right now"). It is for a few justified removals, not for exploring and not for cleaning messy fields. [REASONED: lines 2 and 4; READ: Tcd L1774, L1790; T92 L7815; Tcd L1165] | "Changes are recorded in the audit_recipe. - correct" (2026-11-16). The audit changes the **data before the plot**; it never changes a plot's recipe. **Deferred, not part of this redesign:** "Some extension of the audit functioning might occur later to allow small aesthetic audit changes on the plot recipe part". The audit is for a few justified removals, not for exploring and not for cleaning messy fields. [READ: Tcd L2020; Tcd L1774; T92 L7815; Tcd L1165] |
| 9 (corrected by Eve) | Order: tier 1, then tier 2, then tier 3. In each list the recipe's steps come first, then the audit steps in the order recorded. The table, the plot, the bundle and the export run the same order. A step that cannot run is an error, never a skip. [READ: AS:135; S2:123; ADR:5343; Tcd L986] | "the audit steps can be added at the end of each T1 - T2 - T3 (for now)" (2026-11-16): after the recipe's steps of that list. Steps between steps or at the beginning are under study (O13). The audit steps run in the order recorded, the same in the table, the plot, the bundle and the export; a step that cannot run is an error, never a skip. [READ: Tcd L2020; ADR:5343; Tcd L986] |
| 10 (corrected by Eve) | The original plots stay beside the audited plots, as evidence. [READ: T92 L8336, L7849] | "In the export we need to be able to see original and modified plot. In the ui the original plot and modified plot is activated by compare (same concept we already had define for the audit)" (2026-11-16). [READ: Tcd L2020] |
| 11 (corrected by Eve) | Exploration is never exported; the audit steps with reasons always are. She confirmed "the export is the audit recipe" and described a results export "with the data used", the user choosing the data (2026-11-15). Older records (2026-11-09, 11-12) say the standard export only names the recipe and the data. Her later words win. Her answer to the question "Q3, is the audit recipe always in the export?" chose no option: it is not decided (O1). [READ: Tcd L1497; CH M131; S2:19; ADR:4857-4866; AS:346] | Exploration is never exported. "the audit export export the audit recipe with the step of the audit added to the recipe - the reason can be added as #comment" (2026-11-16). A more readable summary of the added steps is under study (O1). [READ: Tcd L2020; Tad L8704] |
| 13 (corrected by Eve) | The app informs and warns; the user decides. It must work for any recipe and any field (data-agnostic). The example of section (b) is an illustration only. [READ: T92 L3370, L8522, L9167] | The app informs; "be aware of not over warning - warn only when problem" (2026-11-16); the user decides. It must work for any recipe and any field (data-agnostic); section (b) is an illustration only. A help button in the audit dialog is under study (O14). [READ: Tcd L2020; T92 L3370, L8522, L9167] |
| 14 (corrected by Eve) | **Built today:** the older per-plot model ("My view", "Plot to show"). The audit recipe, the ticks and the engine's reading of T3 are **not built**. [READ: S2:32-49; `recipe_check.py:46-47`; `home_theater.py:433-469`] | "My view and plot to show have been re-factored" (2026-11-16): built today are "Plot to show" (Result, My view, Compare) and "Data to show" (Raw, Result, My view) as refactored on 2026-11-05 (`D-0001`) and 2026-11-11 (`D-0014`); My view applies the audited steps in the recorded order (`D-0096`). Not built: the audit-mode switch, the `audit_recipe`, the ticks, and "the engine reading T3" ("was not build yet"). [READ: Tcd L2020; `home_theater.py:439-483, 725-750, 932-1019`] |
| 4 (confirmed by Eve; names only) | "audit recipe", "original recipe" | `audit_recipe`, `original_recipe`, written with the underscore as she does (Tcd L2020) |
| 8 (confirmed by Eve; names only) | "audit recipe", "original recipe" | `audit_recipe`, `original_recipe`, written with the underscore as she does (Tcd L2020) |
| 15 (confirmed by Eve; names only) | "audit recipe", "original recipe" | `audit_recipe`, `original_recipe`, written with the underscore as she does (Tcd L2020) |
