# The HOME redesign: intent, succession of operations, consequences

**Status:** draft for Eve to read and correct, 2026-11-16 (task HOME-REDESIGN-INTENT-1). Written by reading only. Nothing in the code, the tests, the rule files, the ADRs or the other design files was changed.
**Who reads it:** every agent that touches HOME, the audit or the export, before it builds or asks Eve a question.
**What wins:** Eve's own words, the later over the earlier. A record written by an agent counts only where it quotes or names her.

**Labels on every statement.**
- **[READ: source]**: the statement is in a source I read. The source is given.
- **[REASONED: steps]**: derived from READ statements. The steps are given.
- **[ASSUMED]**: not stated by her anywhere I read. Such a statement is never given as her intent. It is in section (d), as open.

**Source keys.** Transcripts (`~/.claude/projects/-home-evezeyl-Documents-Insync-gdrive-OBSWORK-20-GITS-SPARMVET-VIZ/`): **T92** = `92f68895-...jsonl` (the HOME session, 2026-11-11 to 11-14); **Tcd** = `cd1b0ac7-...jsonl` (the review session, 2026-11-14 to 11-16); **Tad** = `ad032c0c-...jsonl` (2026-11-04 to 11-11); **T28** = `2836faff-...jsonl` (the recipe session, 2026-11-13). "T92 L9308" is line 9308 of that file, a turn of Eve; the time is UTC. **ADR** = `.claude/knowledge/architecture_decisions.md:line`. **AS** = `.claude/design/home_audit_steps.md:line`. **PF** = `.claude/design/home_preview_filters.md:line`. **S2** = `.claude/design/home_stage2_mechanism_spec.md:line`. **HO** = `.claude/design/spaces/HOME.md:line`. **HM** = `.claude/design/home_evidence/home_hash_model_2026-11-12.md`. **CH Mn** = block Mn of the main tree's `tmpAI/agent_channel.md` (not in git). **LG** = main tree `tmpAI/panel/adr/ledger.md`. **OA**, **QC**, **N74**, **RU** = main tree `tmpAI/panel/round7/original_vs_audit_recipe.md`, `questions_checked.md`, `n7_4/result.md`, `recipe_in_use/result.md`.

---

## First page (read this; correct it in one reading)

1. HOME opens the **original recipe**. It is the reference. HOME never changes it. Only Blueprint edits a recipe. [READ: Tcd L1383, 2026-11-15 19:16; paragraph confirmed, Tcd L1497]
2. **Exploration** is for looking. A filter there changes only the table you look at. The plot is always the recipe's Result. Nothing is saved or exported. [READ: T92 L115, L7849; ADR:5334]
3. **Audit mode** is the only way to change data, a plot or the export. Its purpose: a few justified removals for publication-ready figures. It is not for exploring, nor for cleaning messy fields. [READ: T92 L7815; Tcd L1165]
4. The audit works on a **full copy** of the original recipe: the **audit recipe**. It only adds steps. The original steps in the copy cannot be edited or removed. [READ: Tcd L1383, L1790]
5. An audit step is a row filter or a column drop. It changes **data**, never the plot recipe (geoms, mapping, theme). A plot reads its data **after T3**. [READ: Tcd L1774, L1790; T92 L8142]
6. The user picks a field. The app shows the lineage backwards to the roots and forwards to every descendant. The user ticks the places (T1 or T2 of a table, T3 of a plot). What is ticked is what is written. The only automatic placement is "remove these from all tables". [READ: T92 L9308, L10291; Tcd L1149; ADR:5335]
7. One step at a time, shown before Apply with rows and entities before and after. Apply needs a reason. Cancel changes nothing. [READ: T92 L7953; ADR:5337; Tcd L1165]
8. A step added in the audit can be removed again; this touches only the audit recipe. Removed steps are not in the final steps; a separate history log may keep them. [READ: Tcd L1383, L858, L880]
9. Every step of the recipe is done. Every audit step is applied, in the recorded order, in the table, the plot, the bundle and the export. A step that cannot run is a plain error, never a skip. [READ: Tcd L1368, L986; ADR:5343]
10. The original plots stay beside the audited plots. They are the evidence of what was removed and why. [READ: T92 L8336, L7849]
11. Exploration is never exported. The audit steps with their reasons are always exported. **How the export is split into its two modes, and when the recipe file is in it, is OPEN** (section d, O1). [READ: Tad L8704; Tcd L1497; QC:62-104]
12. If the recipe or the data changes while an audit is open, the export is refused until the user re-bases the audit. [READ: Tcd L1013; LG line 92]
13. The software informs and warns; the user decides and is responsible for the choices. [READ: T92 L3370; agent_principles.md:7]
14. **Built today:** the older per-plot model ("My view", "Plot to show", one dialog per plot). The audit recipe, the lineage ticks and the engine's reading of T3 are **not built**. [READ: S2:32-49; `recipe_check.py:46-47`; `home_theater.py:433-469`]
15. Open points: section (d). Places that contradict this page: section (e).

---

## (a) The intent, in her own words

### Her principles as they stand (`.claude/workflows/agent_principles.md`, lines 6 and 7, quoted unchanged)

> 2. **Science is transparent and reproducible.** (ADR-090; `ui_implementation_contract.md` section 7.2; `rules_agent_channel.md` section 7.) The same data and recipe give the same rows and the same picture. What a figure shows is what the export contains. Nothing changes a result silently (rows, samples, NA, rounding, order). The export is the Result plus the steps the user sent to audit with a reason; exploration is never exported. A proposal that weakens one of these is flagged first, even if everything else about it is good.
>
> 3. **Deliver robust tools, inform the user, do not choose for the user.** (Eve 2026-11-12.) The software must be right for every recipe, not for one example. Its job is to prevent silent failures, verify results after the fact, and show the user the consequences and the pitfalls so the user chooses. Automatic placement is limited to what Eve decided ("remove these samples from all tables"); everything else is the user's choice, shown with its consequences.

An earlier statement of hers, in her own words, that says the same as principle 3 (M139 asked agents to report such a place): T92 L3370, 2026-11-11 19:58: "The software role is to ensure that good data science is done possible and that the user can make informed choice, preventing bad one. Inform, warn - But let user decide." [READ]

### Why the redesign was done (her words, in time order)

- 2026-11-06 14:05, Tad L8704: "before audit its only a 'sandbanbox' playground to discover what the user really wants ... The T1/T2 exploration should never be exported ... but T3 audit is the rule for export." [READ]
- 2026-11-06 12:23, Tad L6807: "it is important that what user sees and what user does - is what it gets at the export and that there is no bug - it is science and it should be correct." [READ]
- 2026-11-11 10:04, T92 L115: exploration filters "should never be written in the parket file, its a temporary exploratoin. T3 should also allow temporary exploration BUT when added to audit and applied with a reason then it should modify the parket file and be registed." Also: "we cant have those showup and do nothing - this will confuse the logic." [READ]
- 2026-11-11 15:19, T92 L1563 (the turning point): "I choose to propagate to all plots but all T3 do not have eg. sample ID column - then I would miss the removal of the bad sample ... HERE we have a big logical problem for the science. If would remove samples but actually show them in the plot. Our T3 audit model is not good. In audit mode we need to be able to change the data T1 and T2 and T3 depending on the propagation choices." [READ]
- 2026-11-11 17:33, T92 L1857: "its to allow a result be publication ready not traficate your data to make them better . that is why I want the audit with justification and why I want it exported also." [READ]
- 2026-11-16 06:26, Tcd L1759: "we have refactored for the scientific logic and reproducibility mostly because it was not correct. But a lot of the UI was good and functionning well ... its an improvement ...but not a total replacement." [READ]

### What must be true for the science (her words)

- **The recipe does what it says.** Tcd L1203, 2026-11-15 18:02: "there will be no tradeoff regarding the recipe : it do what it says it does." Tcd L1368, 19:14: "all the steps in the recipe in home have to be done and all the steps sendt to audit and verified in audit have to be applied ... do what you are instructed to do." [READ]
- **The audit is about data, not plots.** T92 L8142, 2026-11-12 10:08: "the user does not removes from a plot but from data ... the plot is a visualisation of the data." Tcd L1774, 2026-11-16 06:29: "the audit does not change the steps of the plot - it changes the data before the plot - but yes the plot must read the data after T3 is applied." [READ]
- **The original stays as evidence.** T92 L8336, 2026-11-12 10:37: "we will still have the original plots : so If we remove those then we still have the proof of why they were removed." [READ]
- **The recipe is as is; the audit only adds.** T92 L8607, 2026-11-12 11:22: "The recipe is as is - we can only add steps not remove those ... a filter in the recipe has a purpose it cannot be removed in the audit." [READ]
- **The audit is a copy of the recipe.** T92 L10656, 2026-11-13 11:26: "The audit steps are registred in a copy of the recipe ... its important we know in audit that the data and plots that will be shown are from the copied recipe." T92 L10694, 11:41: "as long as we make sure that the user cannot modify the steps that are in the original in the copy." Tcd L1790, 2026-11-16 06:32: "the audit step are added in the audit recipe that is a full copy of the original recipe." [READ]
- **No silent change.** T92 L9167, 2026-11-12 13:14: "what we want is a software that is trustworthy and put warnings if the recipe is not correct, prevent silent failures." Missing values: T92 L8491, 2026-11-12 10:59: "We do not remove those silently." [READ]
- **The user decides, informed; we stay simple.** T92 L9167: "I do not think we should implement where to remove based on a lot of rules except for the I want to remove this from all tables ... keep it as simple as user to understand otherwise this will never work." T92 L9308, 13:46: "I want with the Tick to make it clear - what is the Tick is what is done. I want the user to take a decision here. Safe ...mode." [READ]
- **Who is responsible for what.** T92 L9650, 2026-11-12 15:08: "We are responsible for transparency and clear functioning . the recipe maker and user are responsible for good practices ... in audit only filters and drops operations are allowed by design." [READ]
- **Reproducible and checkable.** Tad L47621, 2026-11-09 10:10: "Science needs full reproducibility - however the users wil not know how to compare the hashes - so we will need to give them a way to do that - withing the app." [READ]
- **Small, few changes.** Tcd L1165, 2026-11-15 17:47: "we have to advise the user to only send / validate one audit point at the time ... The goal is small change in the data to have publication ready plots (not to do data exploration so we only expect a few changes)." [READ]

### Where she changed her mind (the later word wins)

| Subject | Earlier (her words) | Later (her words) |
|---|---|---|
| Where an audit step acts | 2026-11-11 13:44, T92 L1224: "I think it should always be applied on T3" | 2026-11-11 15:19, T92 L1563: "we need to be able to change the data T1 and T2 and T3 depending on the propagation choices"; then the lineage and ticks (T92 L9308, 2026-11-12) [READ] |
| Exploration filters and plots | 2026-11-11 12:25, T92 L681: "the plot changes only in my view" | 2026-11-12 08:56, T92 L7849: "In exploration mode we will have only one plot : Results - immutable" [READ] |
| A draft before Apply | 2026-11-12 09:16, T92 L7936: "may be we keep it simple : no preview - send to audit button ?" | 2026-11-12 09:21, T92 L7953: "yes : one step preview before validation in audit seems good" [READ] |
| T3 in Blueprint | 2026-11-08 08:10, Tad L24062: "No T3 should exist in blueprint" | 2026-11-15 08:05, Tcd L670 (e): "blueprint can add to tier 3 for a plot ... The T3 is the data that goes to the plot BUT not the plot recipe" [READ] |
| Missing values in filters | 2026-11-12 13:33, T92 L9231: "missing values are treated as a real value" | 2026-11-14 18:06, Tcd L178: "follow polars and informs clearly" (ADR-103) [READ] |
| Recipe file in the export | 2026-11-09 13:11, Tad L50822: "mode 1 - should not contain the recipe"; 2026-11-12 09:48, T92 L8069: "include recipe and data as one bundle option with the waring" | 2026-11-15 22:07, Tcd L1497: two exports, "one mode where export can be with results in home (the recipe produced this with the data used ...) ... the other mode export the changes in the audit". Not yet reconciled: section (d) O1 [READ] |
| Source of truth of the audit | 2026-11-11 (record, not her words): "the step list is the source of truth", AS:245, AS:342 | 2026-11-13: the copy is the source of truth, "Decided (Eve, 2026-11-13)", AS:164 [READ] |

---

## (b) The succession of operations, with one example

**The example.** The shipped test recipe `1_test_data_ST22_dummy`. Its tables (joins) are named in the records: `QC_Reads_Anchor`, `Quast_with_metadata`, `MLST_with_metadata` (AS:146; N74:12-20). [READ] Two things the user does:
- **Step A, a removal of samples ticked at two tables:** two samples sequenced badly (illustrative ids `S7` and `S9`) are removed by a filter on `sample_id`, ticked at T1 of `Quast_with_metadata` and at T1 of `MLST_with_metadata`. [ASSUMED: the ids and the choice of tables are mine, for illustration only; the mechanism is READ below]
- **Step B, a filter on the data of one plot:** in the plot `year_distribution` (it reads `MLST_with_metadata`, N74:16), one category with a single observation is removed at that plot's T3. [ASSUMED: the category is illustrative; "too few observations to compare" is her own example, T92 L1703]

**1. HOME opens the original recipe.**
- The user picks a recipe that passed the load gate; a failing recipe is refused with its reason. [READ: HO:68; ADR-100 point 3, ADR:5199; Tcd L858 N5]
- HOME builds the original T1 and T2 of each table and stores them by node key. The original never changes. [READ: AS:30; ADR-101, ADR:5237-5243]
- The session is named by the recipe hash and the data hash (`session_key = R[:12]:D[:12]`). [READ: ADR:5238]
- *Stored:* original recipe on disk (untouched); original stored tables in the original cache; nothing in the session yet about the audit. [REASONED: from the three lines above]

**2. Exploration (always available where interaction is on).**
- The user chooses the stage of the open plot: T1, T2 or T3 (later a "Source" choice too). [READ: PF:19; HO:125]
- A filter or column choice changes the table shown, at that stage only. [READ: PF:35-36; ADR-105 point 1, ADR:5334]
- The plot shown is always the Result, immutable. [READ: PF:37; T92 L7849]
- Changing the stage or the recipe clears the preview filters, with a message. [READ: PF:47-49]
- *Stored:* nothing. *Exported:* never. [READ: PF:38-39, PF:50]

**3. The user switches to audit mode.**
- The switch exists only with the sandbox flag. Audit mode needs Compare, sessions and export switched on too. [READ: AS:57-62; ADR-099 point 11, ADR:5123; T92 L7815]
- The screen shows the immutable Result beside the audited plot (Compare is an on/off toggle). [READ: AS:52; T92 L7849]
- The data and plots of audit mode come from the audit recipe; Exploration reads the original. [READ: AS:164; T92 L10656]
- *Stored:* the audit recipe is a real file in the session folder. **When this file first exists is OPEN** (O2). [READ: AS:164; QC:24]
- While the audit has no step, the audit recipe equals the original and the audited plot equals the Result. [REASONED: the copy minus its marked steps equals the original (AS:164); an empty step list keeps the previous node (ADR:5239); so with no marked step every node is the original node]

**4. Step A is made (nothing is applied yet).**
- The user picks the field `sample_id`, the operator "none of", the list of ids, and the missing-value tick (`na: keep` or `remove`). [READ: ADR-105 point 2, ADR:5335; ADR-103 points 2 and 8, ADR:5284, 5295]
- The values come from selectors built on the values present; typing only where a selector cannot do it, with a "matched / not found" report and a warning. [READ: Tcd L1759, L1774; CH M145, M146]
- The dialog lists, as tick lines, every node where `sample_id` exists, backwards to the roots and forwards to every descendant. [READ: ADR:5335; AS:138]
- The user ticks T1 of `Quast_with_metadata` and T1 of `MLST_with_metadata`. Each line states the exact write. [READ: AS:138; T92 L9308]
- The dialog shows rows and entities before and after for every table and plot downstream, the later steps that summarise rows, and a preview of the open plot. [READ: AS:138; HO:48]
- A reason is required. Apply or Cancel. Cancel changes nothing. [READ: ADR:5337; AS:333]
- *Stored:* nothing yet; the trial computation may sit in the audit cache as one entry. [READ: AS:78]

**5. Step A is applied.**
- The audit recipe gets, at the end of the tier-1 list of each ticked table, one filter step (`modif_filter`), each marked `id: audit_<8 hex>_<k>`. [READ: S2:122-123; DEC18 via S2:97]
- One reason covers the whole action, even though it is written in two places. [READ: AS:333; ADR-099 point 16(f)]
- The audit T1, T2 and T3 of the two tables and of every plot that reads them are recomputed; the original nodes are untouched. [READ: AS:31; ADR:5338]
- The audit node key is the original key plus a labelled part for the audit operation. [READ: ADR:5239; HM section 4]
- After Apply, the same condition is evaluated again on every node that has `sample_id`, and the app reports where the samples are still present (for example in `QC_Reads_Anchor`, not ticked). [READ: AS:143; AS:120] [REASONED: `QC_Reads_Anchor` has `sample_id` (AS:146 lists it among tables holding 42 samples) and was not ticked, so it still holds them]
- *Stored:* the audit recipe file (session folder), an "created" event in the append-only event log, the session ghost. [READ: AS:164; AS:336-338; AS:342]

**6. Step B is made and applied.**
- The user picks the field of the category in the plot's data and ticks only T3 of `year_distribution`. [READ: AS:135 "a change for one plot goes in its T3"]
- The step is written in the audit recipe at the plot entry, in `steps.tier3`, after any steps the recipe maker wrote there. [READ: S2:123; ADR-100 note, ADR:5222]
- The plot spec (mapping, layers, theme) is copied unchanged. [READ: AS:162; Tcd L1790]
- Only that plot's data changes. The other plot reading `MLST_with_metadata` does not change from step B. [REASONED: T3 belongs to one plot (AS:32); a step at T3 affects only what is downstream of that node (AS:133)]
- *Today this cannot run:* the engine does not read `steps.tier3` yet. [READ: `libs/utils/src/utils/recipe_check.py:46-47`, `:900`]

**7. The user checks.**
- Compare: the original Result beside the audited plot. [READ: AS:52]
- Every stage can be shown, original or audit, T1, T2, T3. Only the originals are never changed. [READ: AS:83; ADR:5338]
- A read-only popup per node says what the recipe already does there. [READ: AS:138; T92 L10162]

**8. A step is removed.**
- A step added in the audit can be removed again. It leaves the audit recipe only. [READ: Tcd L1383]
- "Undo last", "Revert to step N" and "Remove all" act on audit steps only; "Remove all" gives back the original recipe. [READ: AS:327-328; HO:124; QC:25 DECIDED]
- Removing is "recompute without it"; later steps are kept and re-checked (applied, not concerned, broken). [READ: AS:318-323]
- The final audit steps do not hold removed steps; a separate `audit_history_log` may keep them. [READ: Tcd L858, L880]
- *Stored:* a "removed" event in the log, the updated audit recipe file. [READ: AS:336-338]

**9. Session: leave and come back.**
- A session is for unfinished work. [READ: Tad L47635; T92 L7815]
- It holds the recipe and data references and, in audit, the audit recipe with its steps; restoring recomputes. [READ: HO:59; AS:164]
- If the data changes, the session key changes, so the audit steps of the old data stay with the old session (a warning on restore). [READ: HM section 5 point 3; HO:59] (Her own words cover only "when I import data then it should be recomputed", T92 L10022; the session consequence is an agent's sentence in a decided section: CONFIRM, O9.)

**10. The recipe or the data changes while the audit is open.**
- The export is refused until the user re-bases: the audit steps are written again into the new original; each is marked applied, not concerned or broken; a broken step blocks the export. [READ: Tcd L1013 "S2-3: a"; LG line 92; S2:79]
- She also asked whether a recipe in use can be blocked from editing, with a warning. [READ: Tcd L1013] The answer is OPEN (O6).

**11. Export.**
- Exploration is never in the export. [READ: Tad L8704; PF:39]
- The audit steps, with reasons, who and when, are always in the export. [READ: AS:346; Tcd L880; QC:69]
- The export holds the audited plots and, for each plot really affected, the original plot beside it. [READ: AS:346; T92 L8097]
- The export is refused if the recipe or data changed since the view, or if a step is broken. [READ: AS:325; contract 7.2 rule 1 as quoted in QC:75]
- `effective_run.yaml` (the hashes of recipe, data, engine, steps) is always written, so two bundles can be compared leg by leg. [READ: ADR:4867-4875; Tad L51061]
- **Which mode holds the recipe file (the audit recipe) and the raw data is OPEN** (O1).

**12. Import (gated).**
- Import is its own function, switched on by the configuration, for an authorised person. [READ: AS:348; T92 L8694]
- An invalid recipe blocks the import; the verification legs report match, mismatch or not checked and do not block. [READ: HO:58; ADR:4972]

---

## (c) The consequences, derived step by step

**C1. Nothing can be left out of the export.** [REASONED] (1) The audit recipe is a full copy of the original (Tcd L1790). (2) The audit steps are added to that copy (Tcd L1383). (3) The plot recipe is in the copy, unchanged (AS:162). (4) So every plot can be written in the exported audit recipe; there is no plot whose steps "cannot be written". (5) Every audit step must be applied (Tcd L1368), and nothing may fail silently (ADR-104 point 1, ADR:5308); a step that cannot run is an error, never a skip (ADR:5343). So a skip-and-name, as the export does today (`export_handlers.py:1303-1311`), contradicts this (section e).

**C2. The audit never edits a plot recipe, so a plot reads its data after the last tier.** [REASONED] (1) An audit step changes data, not the plot (Tcd L1774). (2) Every plot has a T3, equal to T2 when empty (T92 L9231; AS:146). (3) So the data that reaches the plot is its T3: the recipe maker's T3 steps, then the audit's T3 steps. (4) The engine must therefore read `steps.tier3` (today it refuses a non-empty one, `recipe_check.py:900`). Y7 is answered by this; it is not a question (Tcd L1790).

**C3. A step is applied at the tables the user ticks, and nowhere else.** [REASONED] (1) "What is the Tick is what is done" (T92 L9308). (2) The only automatic placement is "remove from all tables" (ADR:5335; agent_principles.md:7). (3) So a table not ticked keeps its rows, and the app says where the condition still matches (AS:143). Which lines are ticked when the dialog opens is OPEN (O3).

**C4. "Undo last", "Revert to step N" and "Remove all" touch audit steps only.** [REASONED] (1) Original steps cannot be edited or removed in the copy (Tcd L1383; AS:164). (2) These controls remove steps. (3) So they can only remove marked audit steps; "Remove all" returns the audit recipe to the original. Recorded as DECIDED in QC:25. Her word of 2026-11-13: "In audit ? the unto is the remove step button" (T92 L11773).

**C5. Who edits what, where.** [REASONED] (1) Full recipe edit only in Blueprint (Tcd L1383). (2) Blueprint may write a plot's T3 data steps (Tcd L670 e). (3) HOME's audit writes only filters and drops into the audit recipe, never into the original (T92 L9650; AS:162). (4) So: Blueprint edits the original (all tiers, the plot specs); HOME edits only the audit recipe, by adding or removing its own steps.

**C6. Exploration is a sandbox and is never exported.** [REASONED] (1) Exploration changes only the table shown (ADR:5334). (2) It is never saved (PF:50). (3) The export holds what the user validated with a reason (Tad L8704; principle 2). (4) So no exploration filter can reach a plot, a stored table, a session or an export.

**C7. Every recipe step is done, every audit step is applied, in one order everywhere.** [REASONED] (1) Tcd L1368. (2) The recorded order is the order run, in the table, the plot, the bundle and the export (ADR:5343). (3) So the table, the plot and a re-run of the exported recipe give the same rows, or the same plain error.

**C8. The original plots are evidence, not leftovers.** [REASONED] (1) T92 L8336. (2) The Result is immutable (T92 L7849). (3) So the export carries the original plot beside each affected audited plot (AS:346), and a QC plot can stay unaudited to justify a removal elsewhere (T92 L8114).

**C9. The export always holds the audit steps; its split into two modes is not settled.** [REASONED] (1) The steps with reasons are always exported (AS:346; QC:69). (2) Her two modes of 2026-11-15 (Tcd L1497) and the records (ADR-097; P4b at AS:346) differ on where the recipe file goes. (3) So an agent may build the always-present parts, but not the split (O1).

**C10. When the recipe or the data changes.** [REASONED] (1) The export is refused until re-base (Tcd L1013). (2) The original keys change with the recipe or the data (ADR:5238-5239). (3) The audit recipe names its original by hash (AS:164). (4) So a mismatch between that hash and the current original is the signal; nothing is exported from a mix of old and new.

**C11. What a session stores.** [REASONED] (1) The session is unfinished work (T92 L7815). (2) In audit it holds the audit recipe file and the event log (AS:164, AS:336). (3) Exploration filters are not in it (PF:50). (4) So restoring a session gives back the audit, not the exploration.

**C12. One step at a time.** [REASONED] (1) One candidate is previewed in a modal dialog (ADR:5337). (2) She advises the user to validate one audit point at a time (Tcd L1165). (3) So there is no staged list in audit mode, and the audit panel has no Apply gate (AS:75).

**C13. Y8 dissolves.** [REASONED] (1) Y8 came from the export form that forks a join per plot and repoints the plot (OA section C; `t3_translator.py:213`). (2) With a full copy, steps go into the copy's own lists (S2:123); no join is added and no plot is repointed. (3) So there is nothing to refuse; the old form is to be replaced (Tcd L1790; `t3_translator.py:35-37`).

---

## (d) What is still open

**O1. What is in each export mode, and where the recipe file goes.**
- Reading 1 (records): the standard export names the recipe and the data by hash and holds neither file; one tick adds the recipe (in audit, the audit recipe) and the raw data together, off by default. Sources: ADR:4857-4866 (2026-11-09); AS:346 (P4b, 2026-11-12); her T92 L8069.
- Reading 2 (her later words): "one mode ... the recipe produced this with the data used ... the other mode export the changes in the audit" (Tcd L1497, 2026-11-15). And the paragraph line 7 she confirmed: "The export is the audit recipe" (S2:19).
- Reading 3: two separate ticks, recipe and raw data (QC:99).
- Also open: does the user choose the data used in the export, or only when loading (QC:101-103)?

**O2. When the audit recipe file is created** (first step, switching audit on, or session start). No record answers (QC:24).

**O3. What is ticked when the dialog opens.** AS:134 and S2:128 say "all ticked by default"; AS:138 (same day) says "the place the user chose is ticked; other places are listed unticked"; her words say only "the user choose" (Tcd L1149) and "the Tick is what is done" (T92 L9308). Readings: (a) only the place chosen; (b) all candidates; (c) none. (CH M130, Open 2.)

**O4. Which ids reach a ticked table that lacks the field.** Example: `country = Norway` gives 21 samples at T2 and 28 at the root (N74:24-37). Readings: the 28, the 21, or the user chooses (CH M130, Open 1).

**O5. Screen words for the two plots and tables** ("Result" and "My view" today). The two recipe names are decided (CH M125; QC:26); the screen words are not (QC:27).

**O6. A recipe in use.** Should Blueprint warn when it saves a recipe open in HOME, or block it? Should a data file be watched? Her question: Tcd L1013. Points 42 to 47 of CH M138 wait for her.

**O7. Removal by an attribute in a table without that attribute.** The helper and suggestions are decided (AS:119); which samples a selection takes is O4.

**O8. The event log in the export.** She said a log "can be usefull ... but it needs to be separate" (Tcd L880). Whether it is in the export by default: the plan says yes (S2:71); not confirmed by her words.

**O9. Data changed, session.** "Audit steps of the old data stay with the old session" (HM section 5 (3); HO:59) is in a section headed as her decision, but her words cover only recomputation (T92 L10022). CONFIRM.

**O10. Where the recipe overview and the step panel sit.** Decided in principle: accordions in the right panel with a switch to a dialog (ADR:5183); her own words: "difficult for me to decide without trying it" (Tcd L880). To settle with pictures at the screen step.

---

## (e) Where today's build, the spec, the rule files or the docs contradict (a) to (c)

| # | Place (file:line) | What it says or does | Contradicts |
|---|---|---|---|
| E1 | `app/handlers/home_theater.py:433-469` | "My view", "Plot to show", Compare of the old model; exploration filters change the plot on My view (ADR-098 point 1, ADR:5030) | First page 2, 3; C6. Built by design as the starting point (ADR:5021); to replace (task AUDIT-REPLACE-1) |
| E2 | `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:30-40, :213` | the export forks a join per plot and repoints the plot | C1, C13: the audit recipe is a full copy with steps in its own lists |
| E3 | `app/handlers/export_handlers.py:1303-1311` | plots whose steps cannot be translated are skipped with a warning | C1; every audit step is applied (Tcd L1368); no silent error (ADR:5308) |
| E4 | `libs/utils/src/utils/recipe_check.py:46-47, :900` | `TIER3_READ_BY_ENGINE = False`; a non-empty `steps.tier3` is refused | C2 (stated as "not built", S2:148 P5) |
| E5 | `app/handlers/audit_stack.py` (no match for "Undo", "Revert", "Remove all") | only a delete per step | C4 (not built yet) |
| E6 | `.claude/rules/ui_implementation_contract.md:10-17` | violet (original) steps with a power icon, a trash with a modal, `btn_revert` full wipe, nodes dragged above or below | First page 4: original steps cannot be edited or removed (no "superseded" mark) |
| E7 | `.claude/rules/ui_implementation_contract.md:458, :462, :473, :641`; `.claude/rules/rules_ui_dashboard.md:13` | the step type `developer_raw_yaml` is still listed | Removed (AS:125; refused in code, `app/modules/renamed_keys.py:186`) |
| E8 | `.claude/design/home_audit_steps.md:245, :342` | "the step list is the source of truth" | AS:164 (2026-11-13): the copy is the source of truth |
| E9 | `.claude/design/home_audit_steps.md:134` vs `:138`; `home_stage2_mechanism_spec.md:128`; `spaces/HOME.md:46` | "all ticked by default" vs "only the chosen place ticked" | Internal contradiction; O3 |
| E10 | `.claude/design/spaces/HOME.md:37, :45` | "Missing values are a visible, selectable value"; a value "converted to the type of each column" | ADR-103 (the `na` tick) and ADR-104 point 7 (no conversion; a wrong type is an error) |
| E11 | `.claude/design/home_stage2_mechanism_spec.md:79` | S2-3 still under "New, to answer here" | Decided (a) on 2026-11-15 (Tcd L1013; LG line 92) |
| E12 | `docs/user_guide/understanding_your_export.qmd:12`; `export_handlers.py:571` | "This standard bundle never contains your data analysis recipe"; tick "Also include a reproducibility/reimport bundle" | Agrees with Reading 1 of O1, not with Reading 2; stays until O1 is answered |
| E13 | Diagrams `HOME-AUDIT-LINEAGE`, `HOME-AUDIT-FLOW`, `HOME-AUDIT-EFFECT` (`docs/UML/app.mdj`) | levels 0-3, reach selector, reason categories | Contradicted since 2026-11-12 (`home_evidence/home_uml_review_2026-11-12.md`, table rows 1-3); no banner |
| E14 | Diagram `UI-HOME-AUDIT` (`docs/UML/diagrams/UI-HOME-AUDIT_The_screen_with_audit_mode_on.png`) | dialog with "reach selector, nothing preselected" and "reason category + reason" | Ticks along the lineage (ADR:5335); free-text reason (ADR:5125) |
| E15 | Names | "audit recipe" has nine names in records, diagrams, docs and code; none is on the screen | Her rule: one pair of names everywhere (CH M125; OA section B) |

### What was good in the earlier UI and is to be reused (her words of 2026-11-16: "an improvement, not a total replacement", Tcd L1759)

- **Selectors built on the existing values**, with search, as before; typing only for the reason. [READ: Tcd L1759]
- **The Filters panel and its form**: shared by Exploration ("Add to preview") and audit mode ("Create audit step"). [READ: AS:51; PF:25-29]
- **The centre plot and table components**: reused, fed with the audit data; Compare already has two panes. [READ: AS:52, AS:100-102]
- **The right Pipeline Audit panel** (slot `audit_stack`): kept for the step list. Dropped from it: the "Inherited (T2)" nodes, the pending badge, the Apply gate, the plot style panel. [READ: AS:53; HO:124]
- **The existing error surface, the "recalculating" overlay, the Alerts panel**. [READ: AS:51, AS:286]
- **The session and export panels**, extended. [READ: HO:57-59]
- Which piece is kept as it is, adapted or replaced, piece by piece, is a separate inventory (CH M145, M146); it is not done here.

---

## Sources read (with dates)

**Transcripts** (`~/.claude/projects/-home-evezeyl-Documents-Insync-gdrive-OBSWORK-20-GITS-SPARMVET-VIZ/`; Eve's turns extracted with the automatic summaries removed; first and last time of each file):
| File | Dates (UTC) | How read |
|---|---|---|
| `4f9d21b6-...jsonl` | 2026-11-04 13:04-13:13 | listed (2 turns) |
| `82e7337d-...jsonl`, `b7fd8e77-...jsonl` | 2026-11-04 14:53 | listed (1 turn each) |
| `ad032c0c-...jsonl` | 2026-11-04 15:12 to 11-11 09:30 | searched (audit, export, T3, exploration, session, reproducib); turns read in full around the hits |
| `902da972-...jsonl` | 2026-11-07 07:45 to 11-14 10:07 | searched; no redesign turn found |
| `92f68895-...jsonl` (HOME session) | 2026-11-11 09:41 to 11-14 13:47 | all 158 turns of Eve read |
| `9b22d54e-...jsonl` | 2026-11-11 10:15 | listed |
| `2836faff-...jsonl` (recipe session) | 2026-11-13 09:20-20:48 | searched (audit, T3, copy, export) |
| `3e9e5fed-...jsonl` | 2026-11-14 13:02-13:36 | searched |
| `3ce2c163-...jsonl` (coordinator) | 2026-11-14 13:48 to 11-16 06:44 | searched (her pasted briefs) |
| `cd1b0ac7-...jsonl` (review session) | 2026-11-14 17:18 to 11-16 06:39 | all 96 turns of Eve read |

**Records** (worktree at `472c0ff2`): ADR-097 to ADR-106 (`architecture_decisions.md:4806-5370`); `home_audit_steps.md` lines 1-509; `home_preview_filters.md` (all); `home_stage2_mechanism_spec.md` (all, v0.2 of 2026-11-15); `spaces/HOME.md` (all); `export_specification.md` (headings, status); `home_evidence/home_hash_model_2026-11-12.md`, `home_audit_view_from_copy_2026-11-13.md`, `home_uml_review_2026-11-12.md`; `handoff_active.md` (searched; lines 503-504); `tasks.md` (searched: lines 82, 83, 94, 261, 397, 424); `.claude/workflows/agent_principles.md`; diagram picture `UI-HOME-AUDIT`.
**Main tree, not in git:** `tmpAI/agent_channel.md` blocks M124-M149 (2026-11-15 and 11-16) and the coordinator's M120-M139; `tmpAI/panel/adr/ledger.md` (searched); `tmpAI/panel/round7/original_vs_audit_recipe.md` (all), `questions_checked.md` (rows Q3-Q9, section B), `n7_4/result.md` (sections 0 to B), `recipe_in_use/result.md` (sections 0 to A2).
**Code checked** (worktree): `home_theater.py:433-469`; `t3_translator.py:30-40, 213`; `export_handlers.py:571, 1303-1311`; `recipe_check.py:46-47, 900`; `audit_stack.py` (search); `renamed_keys.py:186`; the rule files named in section (e).

**Not read:** the other UML pictures (only `UI-HOME-AUDIT` was looked at); `home_audit_steps.md` lines 510-666 (sections 18-20, the reviews); `home_audit_reading_guide.md`; `recipe_format_spec.md` beyond what the stage-2 spec and the ADRs quote; the archive tag `archive/home-filters-uml-2026-11-11`; the full text of `export_specification.md` and `ui_implementation_contract.md` section 7.2.
