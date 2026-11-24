# Design agreed by the two agents, and the questions only the owner can answer

Note 2026-11-24: this file still holds quotations of the owner's words from the study rounds. The decisions are written once, in plain words, in the decision ledger; read `WHOLE_PICTURE.md` first.

**What this file is.** The points that the two design agents (one Opus, one Sonnet) agreed on before anything of the design is written, as the owner ordered (ledger D-0551 and D-0552). It also holds the eight questions that only the owner can answer. Nothing here is decided by the agents. The design documents are written after her answers.
**Date:** 2026-11-23.
**Where the evidence lives:** the positions, the rounds and the scripts of the runs are in `tmpAI/coordinator/design_dialogue/` (scratch folder, not in git; copies of the retest outputs are in `tmpAI/coordinator/design_dialogue/retest_copy/`); the retest with her scope is `tmpAI/coordinator/whole_picture/RETEST_her_scope.md`.
**Signed by both agents:** Sonnet (this file) and Opus (`OPUS_signs_v2.md` with its replacements, `OPUS_signs_v3.md`).
**Order:** the half page for her; the eight questions; the agreed points with their evidence; the facts still to run.

> **NOTE of 2026-11-23, after this file was signed (ledger D-0558, D-0559).** The owner ordered that no conclusion may rest on the old lineage code ("well we cannot do on the old structure on the lineage true --- no point it would inject errors in conclusions"). Some points below were established through that code (the lineage walk, its records, the place list of "remove from all the data") or through runs that used it. Until they are rechecked by engine runs and by a graph computed independently from the recipe, these are **NOT to be taken as signed**: the agreed points G11, G15 (the part that rests on a run), G16, G17, G24, G26; the claim about the demo in G27 (the small test recipe itself, mean 30 against 25, holds by hand); the numbers of the demo quoted in questions Q1 to Q4; the sentence in Q5 that "can remain here" is certain only at a join on the entity key; and the count of 27 places. This list is the Sonnet design agent's; the Opus design agent's list is still to come and may add points. Her answer to Q1 (ledger D-0553) stands: it is her rule, not a result of that code. Both agents have restarted their work on independent paths and derived places under the new evidence rules; the recheck is part of it. **Update, same day:** the recheck is done: see `PATHS_AND_DERIVED_AGREED.md` in this folder, section on the recheck of this list (which points are confirmed by which run, which four are void, and which is replaced by her answer D-0553); read the two files together; where they differ, the later file holds.

## HALF PAGE FOR HER

What the two agents agree on:
1. The recipe already tells the app, with no new key, which tables are original, which join an original table with the metadata, and what lies below each place. The app can draw one tree per original table.
2. A place is the end of a tier of a table, a join or a plot. A step reaches every place below it; those places are "derived" and are marked "~". In one step, no chosen place may lie below another chosen place.
3. When two chosen places lie one below the other, a calculation over all entities that lies between them is done on the data of the upper place. So choosing the upper or the lower place gives a different result when such a calculation lies between them. We ran this on a small recipe.
4. The effect of a step is known only after Apply, when the recipe has run again. Before Apply the app can show only the structure: the tree, what is derived, what each place reaches.
5. "~" means "below the step". It does not mean the entity is gone there. On the demo, where the metadata is the first table of a left join, a step at the original table leaves the entity's row.
6. Your case "remove from all analyses but the quality ones" can be written with 17 places and nothing nested. It gives the same 17 plot tables as our first test (run B3 of the retest, the one made with your rule). We ran it for two entities.
7. The three forms of "Remove from all the data" (27 places as decided, the 11 uppermost, the 19 defaults) give the same 17 plot tables, with the entity in none. They differ in where the steps are written, so the exported tier 1 files of the tables no plot reads would differ.
8. The place list, the tree view and "Remove from all the data" are not on screen today. Today the screen writes a step at the finished table of one plot. Only you can decide the eight points below.

The questions you must answer first, in order:
- Q1 One place per original table's tree, or one place per branch, in one step?
- Q2 Which place is the default where your rule says nothing (a branch with no metadata join)?
- Q3 How must the recipe be written so that the place is clear (today's form, "one trunk", or a declared default)?
- Q4 What does "Remove from all the data" write: the 27 places, the 11 uppermost, or the defaults?
- Q5 May the app say before Apply "the entity can remain in this place"?
- Q6 Does "Remove step" remove one written step or the whole decision?
- Q7 Must the metadata be the right table of a join (rule, advice or documentation)?
- Q8 Must the recipe declare the entity key?

## 2. THE EIGHT QUESTIONS (most blocking first; each can be read alone)

### Q1 One place per original table's tree, or one place per branch?
**The situation.** On the demo one original table can meet the metadata in several joined tables. MLST meets it in 3: `MLST_with_metadata`, `ST22_Anchor` and `AR1`. Quast has four branches: two quality ones (`Quast_with_metadata` and `QC_Reads_Anchor`), `QA_L50_integer` and `QA_population_zscore`. You wrote that the user chooses one place per history and that the places after it are derived. We do not know if "history" means the whole tree of an original table, or one branch of it.
**What you see on screen today.** A step is written at the finished table of the open plot. The screen offers "this plot only", "all plots" and "all plots except". You do not choose a place along the lineage.
**What exists only in the code, not on screen.** The code lists every place that holds the column, nested or not, and nothing in it stops a nested choice. "Remove from all the data" (code only) writes one step per place it is given; on the demo it offers 27.
**Option R1: one place per original table's tree, in one step.** Your words: "the user can only chose where to write the step in one corect scope - all the steps after are the following history. and are derived", "But the user can only choose one scope per history", "the user can only choose one scope per original T1 on where to apply the step"; "the only way to choose several places must be the case of the independent history - the original T1 steps of independent histories"; "each independent history is like an independent tree graph". Another choice in the same history is "another step audit step later". [D-0547, D-0549, D-0550, in this order]
- A property of R1: a step holds at most one place for each original's tree, and a shared place uses the one place of every tree it is in (`QC_Reads_Anchor` is in 4 trees).
- You would see, for "remove the entity from all analyses but the quality ones" with nothing nested: several steps with the same reason. The ResFinder tree holds 5 independent places (`ResFinder_with_metadata`, `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, and `T2:ResFinder` for `amr_heatmap`), so 5 steps, the smallest number. If the metadata's own tree counts as a tree, 11 places lie in it, so 11 steps, the smallest number (worked out by hand from the trees each place lies in). MLST: 3 steps for "MLST removed" (in our test with only `T1:MLST_with_metadata`, 2 plots change and the entity stays in 14).
- The final recipe holds the same places as under R2, so the tables are the same; what changes is how many steps you write and how many events the log has.
**Option R2: one place per branch.** The common rule: no chosen place is below another chosen place. A tree may then hold several chosen places on different branches, in one step.
- You would see your case in one step: 17 places, nothing nested (`T2:ResFinder` for `amr_heatmap`). In our run: 14 plots change, the entity stays in exactly the 3 quality plots (`qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou`), no column is emptied, and the 17 plot tables equal those of the first test (run B3 of the retest). Same for the entities 10668076 and 11843673.
- For Quast you tick `QA_L50_integer` and `QA_population_zscore`; the two quality branches are neither chosen nor derived. (`T1:Quast`, the one place that covers the whole Quast tree, removes the entity from `assembly_quality_dotplot` and `miaou` and empties four Quast columns in `qc_reads_horizontal_barplot`: our test with only `T1:Quast`.)
- Against R2: it is not what your sentences say literally.
**One thing you must know about the rule "no chosen place below another one, in one step".** It stays: it follows your words "the user cannot choose anymore". It does not block your result: you can choose the lower place instead of the upper one, or write it in a later step ("he must add another step audit step later"). But a place marked "~" can still hold the entity when the entity's row comes from another table of a join, for example when the metadata is the first table. Example on the demo: a step at `T1:ResFinder` alone leaves the entity in `qa_amr_genes_per_sample`; with `T1:QA_AMR_per_sample` as well, it is gone (runs E and A3 of the retest). This links Q1 to Q5 (may the app say "the entity can remain here" before Apply?) and to Q7 (the metadata as the right table). [D-0547]
**Neither: say what you meant.**
**What the two agents think.** Sonnet leans to R2: your own case ("remove the samples from all analyses BUT the ones that show the bad quality") is one decision, and R2 keeps what the rule is for (a place and a place below it are never both chosen). Opus does not lean: it reads your words as R1 and holds both readings as coherent. Both say it is yours to decide. [D-0547, D-0549, D-0550]

### Q2 Which place is the default where your rule says nothing?
**The situation.** Your rule: the default is where the original table and the metadata are joined; with no metadata join, "the first T1 of the lineage when no metadata join (so same level except there is no metadata joined)". On the demo some branches have no metadata join: `amr_heatmap` reads ResFinder itself; `qa_l50_integer` reads a table made from Quast alone (`QA_L50_integer`); `QA_year_types` and `QA_aggregated_no_key` are made from the metadata alone; the Summary tables have no metadata at all. In ResFinder and Quast the same original has branches with and without a metadata join.
**What you see on screen today.** No default: the screen writes at the plot's own table. The code proposes no default either.
**Options.**
- (a) Your literal rule: the first T1 of the original (`T1:ResFinder`, `T1:Quast`, `T1:metadata_schema` for the metadata-only tables). Your words "same level" may also point to `T1:QA_L50_integer` for Quast, which is option (b). You would see: `T1:Quast` removes the entity from the quality plots and empties four columns in `qc_reads_horizontal_barplot`; `T1:metadata_schema` is the place you call not advised.
- (b) The first place that only that branch reads: `T2:ResFinder` for `amr_heatmap`, `T1:QA_L50_integer` for `qa_l50_integer`, `T1:QA_year_types` and `T1:QA_aggregated_no_key` for the metadata-only tables. You would see the same 17 plot tables as our first test (two entities).
- (c) No default ticked on these branches; the tree shows what each place reaches and you choose.
**Neither: say what you meant.**
**What the two agents think.** Both leave it to you. Sonnet leans to (b) as a named default where a branch has no metadata join, and to no default where it is unsure. Opus: your words "same level" point to `T1:QA_L50_integer` for `qa_l50_integer`; for `amr_heatmap` no table at that level exists, so the choice is yours. [D-0549, D-0550, D-0547]

### Q3 How must the recipe be written so that the place is clear?
**The situation.** On the demo each data table meets the metadata in several joined tables, and one joined table is made from up to six originals (`ST22_Anchor`). So "the place where the original and the metadata are joined" is 2 to 4 places for one original. Your best practice: the original table, a left join, then the metadata (the data is the left table). A join reads source tables only (decided, "revisit if needed").
**What you see on screen today.** Nothing about places: the recipe form is read by the code only.
**First a fact.** For plots, a T3a made from a T2a that another result also uses already works today (two plots on one table, one with its own tier 3 steps). For a table as a result nothing exists yet. Your words: "one final result could be used on T2a but T2a could be used to produce one T3a for another final result - what would be done in this case ? yes we need the `from:` this clarifies but still the hiearchy is unclear of where to place it". Do you need two different T2 on one table's T1 (which needs derived tables), or is the present shape what you described? That decision is yours. [D-0517]
**Options.**
- (a) Keep today's form. The app finds the join places itself; the default is per branch. You would see several defaults for one original (MLST: 3).
- (b) "One trunk": each data table is joined with the metadata once (data left, metadata right) and every other table of that history is made from that joined table. You would see one default per original. Five originals already have such a table on the demo (`FastP`, `Quast`, `Bracken`, `ResFinder`, `MLST` with metadata); `VirulenceFinder` has none and would need one. 7 other tables would be rewritten to read a trunk, four of them with the metadata as base today. It needs a join that reads a joined table, or derived tables; the check refuses a join of a joined table today. A table made from several originals would read several trunks, each with the metadata columns. The metadata-only tables and the look-up tables have no trunk, and "all but the quality ones" still needs places below the trunk. [reopens D-0344]
- (c) The recipe author writes down the default place of each original (a new key). You would see one more key in each recipe that names the default place of each original (12 originals on the demo), and the recipe check refusing a named place that is not in that original's tree. For: nothing is guessed, the decided rule stays, and the user may not be the author. Against: the author must keep it right whenever the recipe changes; the app must still check it; it turns your rule into a per-recipe setting. [reopens D-0549]
**Neither: say what you meant.**
**What the two agents think.** Sonnet: "data left, metadata right" is a good practice for authors, not something the format must force. Opus: the scope rule does not depend on this choice; (b) makes the default unique but not your quality case a single choice; (c) is a fair third option. Both: settle with the question on the recipe form. [D-0344, D-0496, D-0500, D-0517, D-0547, D-0549]

### Q4 What does "Remove from all the data" write?
**The situation.** Decided: it writes the removal at tier 1 of every table that holds the key, the metadata included (27 places on the demo). Later you said the places after a chosen place are derived and the metadata is not advised.
**What you see on screen today.** Nothing: it is not on screen. **In the code** it writes one step per place, nested ones too (`T1:MLST` and `T1:MLST_with_metadata`), the metadata too.
**Options, with our runs (entities 10668076 and 11843673).**
- (a) As decided: the 27 places. You would see 27 steps, nested ones included, and a step in the metadata table and in the original tables.
- (b) Only the uppermost places, so that nothing is nested: the first T1 of every original, the metadata included: 11 places. A step in the metadata table and in the original tables.
- (c) The default of each branch, nothing at the metadata unless you choose it: 19 places (or the same with `T2:ResFinder`).
- What the runs say: all three change 17 of 17 plots, the entity stays in none, and the 17 plot tables are identical (0 differ). So on the plots you would see no difference.
- The one real difference: where the steps are written. Under (c) the metadata's and the originals' own tier 1 files keep the entity; under (a) and (b) they lose it. So the exported tier 1 files of the tables no plot reads would differ. This is by construction; those files were not compared in the run.
**Neither: say what you meant.**
**What the two agents think.** Neither agent chooses. Sonnet: (a) writes nested places in one step, which conflicts with your rule of one scope when the steps are read together; the plot tables are the same. Opus: (c) is the review session's reading, not decided; the ledger line says, in its "NOT decided" part (these are not your words): "a reading of the review session, to be asked once when the plan is checked". [reopens D-0416; D-0550, D-0547, D-0457]

### Q5 May the app say, before Apply, that the entity can remain in a derived place?
**The situation.** A step upstream of a join does not always remove the entity downstream. On the demo, where the metadata is the first table of a left join (`QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `ST22_Anchor`), a step at the original table leaves the entity's row. The recipe says this without a run (the kind and the side of the join). It is certain only at a join on the entity key (left, inner, semi), not for a join by another column, and a later step can still change it. We checked this by reading, not by a full run.
**What you see on screen today.** No note before Apply. The code has no note either. You decided that the effect is measured after Apply and kept in the log.
**Options.**
- (a) Nothing before Apply; the measure after Apply and the log show it.
- (b) A short plain note on the derived place: "the entity can remain here: this table is the first table of a left join". It would go into the log with the other warnings shown.
- (c) The note only after Apply, from the measure.
**Neither: say what you meant.**
**What the two agents think.** Neither decides. For (b), your words: "eg. left join keeps the rows of the second table - ensure you removed in second table if this is what you want (or something similar)"; "try to give as clear information as possible - so the user has elements it needs to be able to make a good decision". Against (b), your words: "I would just shows the differents where applied and no per table warnings about downstream effects"; "again after apply". Sonnet's distinction: "the entity can remain" is not a downstream natural consequence but whether the step does what was asked. Opus: the computed effect belongs after Apply; this note is structure. [D-0477, D-0543, D-0501, D-0546, in the order of the quotes; D-0478 asks that warnings shown be logged]

### Q6 Does "Remove step" remove one written step, or the whole decision?
**The situation.** One decision written at 17 places is 17 steps in the audit recipe, with one reason.
**What you see on screen today.** Each step has a bin that removes it together with its copies on the other plots (`audit_stack.py:531-533`). Decided, not built in that form: one control, "Remove step", which removes the step you pick. [D-0314]
**Options.** (a) One step at a time, as decided: you would see 17 lines for one decision, each removable (removing one undoes the decision in part). (b) The whole decision: one line per decision, which opens to show its places. (c) Both: at the removal you choose "this place" or "the whole decision".
**Neither: say what you meant.**
**What the two agents think.** Both put the grouping in the audit log (one event with its places) and no new key in the recipe (provisional). Which removal you want is yours. [D-0314, D-0315, D-0478]

### Q7 Must the metadata be the right table of a join?
**The situation.** On the demo the metadata is the right table in 7 joins and the first table in 4; two tables read the metadata alone. A first table with the metadata keeps all its entities, also those with no data; a data-left join keeps only the entities in the data (your reason: "some users will have metadata for more samples").
**What you see on screen today.** Nothing checks the side. Any join outside tier 1 is already refused.
**Options.** (a) A rule: the recipe check refuses a recipe that joins the metadata as first table; you would see the 4 demo joins refused until rewritten (in the one move of the recipes). (b) An advice: one advice line in the check report, and the recipe runs. (c) Documentation only: a paragraph of the good-practice page.
**Neither: say what you meant.**
**What the two agents think.** Neither chooses (not decided). [D-0547, D-0549, D-0550, D-0525]

### Q8 Must the recipe declare the entity key?
**The situation.** A removal by key needs to know which column is the entity key. The recipe can declare it; it is optional today.
**Options.** (a) Optional as today: a recipe without a declared key offers no removal by key and no "Remove from all the data". (b) Required in every recipe that has a metadata table: the check refuses a recipe that has a metadata table but no declared key. (c) Required for every recipe to run.
**Neither: say what you meant.**
**What the two agents think.** Both say it is yours; the app can only name "the entity" and its key from the declaration. [D-0313, D-0511, D-0500]

## 3. THE AGREED POINTS, with their evidence (signed by both agents)

The labels G1 to G31 are for the agents. "read" = read in code or in the ledger; "run" = a run; "grep" = a search of the code. The origin of a point is in brackets.

**G1 Place.** A place is `T1:<table>`, `T2:<table>` or `T3:<plot>`. Its audit steps go in `audit_steps` after the author's steps of that tier, and the author's steps never change. An empty tier 2, or one no plot reads, is the same place as tier 1; the one case where that is wrong is G28. A plot's own tier 3 is always a place. A source file holds no steps.
Evidence: D-0541 "audit steps can be written at each tier after the original tier block. The original recipe steps are always kept"; D-0346; D-0332. read: `audit_copy.py:106`, `:166-172`, `:177-179`; `lineage_walk.py:394-395` (only a T2 is folded). [S1 / A1]

**G2 Original table.** An original table is a `DS:` node: a schema of `data_schemas` or `additional_datasets_schemas`, or the block `metadata_schema`. Its kind is its block. Evidence: D-0513, D-0523; read `recipe_tiers.py:34-35`.

**G3 History.** A history is the tree of places reachable from one original table. A table made from several originals lies in the tree of each.
Evidence: read `recipe_graph.py:579-580` (a join's parents are the T1 of its ingredients), `:584-585` (a plot's parent is the T2 of its target); J04 `recipe_check.py:867, 869`; D-0344 ("a named join takes only source tables"). Her words: "each independent history is like an independent tree graph" (D-0550). run: all 12 originals of the demo give a tree; 50 of 50 shipped recipes that load give a tree; none has a join of a joined table. It stays a tree while joins read source tables only and a derived table reads one table (the form of derived tables is not confirmed, D-0496).

**G4 Derived place.** A place is derived from a chosen place when it is downstream of it. It is computed each time from the graph, never stored; it is shown with "~"; it cannot be chosen in the same step.
Evidence: D-0547 "All the derived steps must get a "~""; read `lineage_records.py:10`.

**G5 Shared place.** A shared place is a place with two or more originals upstream (the graph alone). A step there is one step on one table. For a removal by key, the dialog counts only the originals whose key reaches the place.
Evidence: D-0547 "So the step must be duplicated in all those T1 - this because of independent histories" (the duplication is only the first T1 of several originals). run on the demo: `ST22_Anchor` 6 originals, `QC_Reads_Anchor` 4, `AR1` 4.

**G6 A join with the metadata.** It is a join whose ingredients include `metadata_schema` and at least one other original table. Its place is the end of its tier 1. Its base is its first ingredient (read `recipe_graph.py:27`); its kind is the `how` of its step. Any join step outside tier 1 is already refused by ST05 (read `recipe_check.py:714-715`, `action_names.py:66`), and no code passes a `tier1_only` catalogue to the check (grep: the name appears only at `recipe_check.py:693, 714`). There is no rule on which side the metadata is (D-0550 "NOT decided"). A line of D-0510 says the check has no rule on a join in tier 2: that is a wrong fact in the records; her decision there stands. The two demo tables with the metadata as only ingredient (`QA_year_types`, `QA_aggregated_no_key`) are not joins with the metadata.

**G7 Default place.** Where a branch meets the metadata, her default place is the end of tier 1 of the table that joins them (D-0549: "in manycase I would select the scope of where original T1+ metadata are joined"; D-0550 point 1: "(original step/T1 where metadata join)"). It is named as a default and can be changed; that is the review session's reading, which she confirmed: "What I read in your comments - was correct" (D-0550). The app cannot choose the scope: "the app cannot decide the scope" (D-0531).

**G8 No nesting inside one step.** In one step, no chosen place is downstream of another chosen place. Both readings of her rule (Q1) contain this. Evidence: D-0547 "all the steps after are the following history. and are derived. ... the user cannot choose anymore". Example: `T1:FastP` with `T1:QC_Reads_Anchor` is nested, because `QC_Reads_Anchor` has FastP as its first ingredient.

**G9 The effect is known after Apply.** Before confirming only the structure is shown. The measure at each change of a tick is not built.
Evidence: D-0545 "you cannot see effect if you do not recalculate"; D-0546 "again after apply"; D-0536 "So for now you register"; D-0537.

**G10 Two pure functions.** The structure is computed from the graph alone, with no engine plan: trees, branches, derived and shared places, the places of joins with the metadata with their kind and side, and the validity of a set of chosen places. The fate of the column (present, renamed, retyped, red with a reason) stays in the existing walk and the engine's plan. So the tree is still shown when a plan fails.
Evidence: read `lineage_walk.walk` (`:883`) and `Line` (`lineage_records.py:267`) give no trees, no derived or shared places, no default, no check of a chosen set.

**G11 "~" means "below the step", not "gone here".**
Evidence: retest run E (the first T1 of each original): the entity stays in 5 plots. In 3 of them the table has the metadata as the base of a join (`qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `qa_population_zscore`, the last with `n50` and `n50_zscore` empty); the other 2 are made from the metadata alone. Retest run D (steps at `T1:MLST` and `T1:metadata_schema`): columns emptied in 3 plots.

**G12 No new recipe key.** The recipe already declares the blocks, the ingredients and their order, the tiers, the plot targets, `entity.population` and `is_entity_key` (read `recipe_check.py:332-348`). Two writing rules are needed, not keys: the metadata is written in `metadata_schema` (D-0511); the entity key is declared for a removal by key (Q8). Limit: whether the entity's rows survive a step (an aggregation without the key, a key rewritten) is the column's fate, not structure.

**G13 Results.** Today a result is a plot (`T3:<plot>`). That a result may be a table is decided as a direction: "a plot entry actually should be a result_entry with either plot or table" (D-0485); "we shuold be able to export the table that is as result also" (D-0487). The form is not decided (D-0496, D-0514 to D-0517). A table that no plot reads is a place (D-0451), not a result.

**G14 The tiers as shared steps (her note N2).** Today a source's T1 is read by several joins, a table's T2 by several plots, and each plot has its own T3 and may have its own tier 3 steps (read `recipe_graph.py:582-585`). Her note is met today for plot results. Her requests of D-0516 and D-0517 ("yes we need the `from:`") need the decision on the form (D-0496); that decision also says whether one table's T1 may feed two T2. This stays a question for her (Q3).

**G15 The first place that only one branch reads is a real place.** On the demo `T2:ResFinder` has 2 steps and is read only by `amr_heatmap`; `T1:ResFinder` has five children: `T2:ResFinder` and four joins (run on the demo graph). `T3:amr_heatmap` is also a place with the same single plot.
run: her case with `T2:ResFinder` in place of `T1:ResFinder` (17 places, nothing nested) gives 14 plots changed, the entity in exactly the 3 quality plots, and the same 17 plot tables as the first test (0 differ), for both entities.

**G16 A branch that never meets the metadata is not covered by "the join place".** On the demo: `amr_heatmap` (reads ResFinder itself), `qa_l50_integer` (reads Quast alone), and the Summary histories. Retest run A: the entity stays, complete, in `amr_heatmap` and `qa_l50_integer`. A default is needed for them (Q2).

**G17 A step at the first T1 of an original.** It does not remove the entity's row where the metadata is the base of a left join: the row comes from the metadata, and only the data columns turn empty. In `ST22_Anchor` the row still disappears, by coincidence: a later inner join by gene drops it (retest run E). A step there also hits the quality plots where one original feeds both (retest run B2: `T1:Quast` removes the entity from `assembly_quality_dotplot` and `miaou` and empties `n50`, `total_length`, `largest_contig`, `L50` in `qc_reads_horizontal_barplot`). The join place of each table has neither problem.

**G18 A table made from the metadata alone** lies only in the metadata's tree (`QA_year_types`, `QA_aggregated_no_key`). Its own table is its first place. Her literal "first T1" for it is `T1:metadata_schema`, which she calls "not advised" (D-0547: "If the user wants to remove from metada it must choose the T1 of metadata and remove there (not advised)").

**G19 A join with several ingredients has one place**, the end of its tier 1, whatever the number of the step that joins the metadata. One original has several such places (FastP 3, Quast 3, MLST 3, ResFinder 4; retest section 2).

**G20 A look-up table without the key column** (`APEC_STEC_virulence_genes`) is not offered for a removal by key. For a filter on another column its tree is an ordinary history. Evidence: retest section 2.

**G21 A later step.** A later step may choose a place derived from an earlier step's place; another scope in the same branch is another audit step (D-0547: "if he want another choice he must add another step audit step later - choosing a different scope"). The dialog may show such a place as "already covered by step n": that is structure, not effect.

**G22 The tree view.** The dialog shows one tree per original, with its places, its derived and shared places, and what each place reaches. Evidence: D-0547 "What would be best is to show the lineage/history on the audit step - a bit more structured"; D-0550 "we should see in the history what is common to both so then we can choose the right place". The words and the form of the view are not decided (D-0550).

**G23 (PROVISIONAL) Several steps of one decision.** A decision written at several places is one event in the audit log, with its places and the ids of the steps written; the audit recipe gets no new key. Evidence: read `remove_from_all.apply` (`:308`) writes one step per place, each with its own id and one shared reason, and nothing in the recipe groups them; the keys of the audit recipe are decided (D-0332, D-0354); the log is always exported (D-0478). PROVISIONAL: the form of the record is not decided (D-0536, D-0537). Whether "Remove step" works per step or per decision is Q6.

**G24 Facts of the retest the design must meet.** MLST meets the metadata in 3 tables and one place changes 2 plots (run C); the Quast conflict (run B2); the metadata is the base in 4 joins (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`); the z-scores of all 41 other entities change by up to 0.064; the count of `qa_aggregated_no_key` goes from 19 to 18 and names nobody. The last two are natural consequences of the rerun (D-0501), shown by the measure after Apply.

**G25 What is on screen today, and what is only in the library.** Today a step is written at the finished table of one plot ("this plot only / all plots / all plots except": `ui_implementation_contract.md` 12g.4).
From these libraries the app calls three things today:
- the rule of a key drop (`utils.key_drop.DropGate`), which builds the walk's lineage index for a drop (`key_drop.py:51`). HOME calls it when a column drop is sent to the audit (`filter_and_audit_handlers.py:938`) and when a session is restored (`session_manager.py:150`, called at `session_handlers.py:673`). It uses the engine's plan book that HOME composes (`home_theater.py:379-383`);
- the engine's guard on every build, which refuses audit steps in a recipe that is not an audit copy (`orchestrator.py:80-95`);
- the audit parts of the cache keys (`cache_keys.py:69`).
Library only (no code of `app/` calls these outside tests): the list of places for a filter (`lineage_walk.walk`); `start_audit`, `add_step` and `remove_step` (called only by `plan_composer.compose_candidate_plan_book`, which no screen calls); `remove_from_all`, `table_compare` and `run_audit`.
"Remove from all the data" as built (`remove_from_all.py:292-307`) accepts any subset of the 27 places the demo offers, with no check for nested places; `ticked=None` writes every reached place.
Evidence: grep of `app/` outside tests: imports of `key_drop` at `filter_and_audit_handlers.py:37` and `session_manager.py:46`; of `audit_copy` at `cache_keys.py:69`, `build_failure.py:28`, `plan_composer.py:48`; no import of `lineage_walk`, `remove_from_all` or `table_compare`; `run_audit` is defined in `audit_run.py:310` and called by no module of `app/`; `compose_candidate_plan_book` has no caller outside its own file. [replacement by Opus; I re-checked these lines]

**G26 The three forms of "Remove from all the data" (run, two entities).** (a) as decided (D-0416): the 27 places; (b) the 11 uppermost places (the first T1 of every original that holds the key, the metadata included, nothing nested); (c) the 19 places of the defaults reading (nothing at the metadata). For the entities 10668076 and 11843673: each changes 17 of 17 plots, the entity stays in none, no column is emptied, and the 17 plot tables are identical across the three (0 differ; compared by hash of each plot's table: `opus_runs.out` lines 2346-2348 and 4270-4272). The real difference is where the steps are written: the metadata table and the original tables carry a step under (a) and (b) and not under (c). So the exported tier 1 files of tables no plot reads (D-0457) would keep the entity under (c) and lose it under (a) and (b). This last point is by construction, NOT run: those exported files were not compared.

**G27 Two chosen places, one below the other (run).** A small temporary recipe: the source A (values 10, 20, 30, 40) is joined with B in J; the tier 1 of J computes the mean of the value over ALL rows after the join, so the computation lies between the upper place (end of A's tier 1) and the lower place (end of J's tier 1). The entity s1 is removed at the upper place, at the lower place, or at both:
- upper place only: J's table has s2, s3, s4 and the mean 30 (without s1);
- lower place only: the same rows and the mean 25 (the mean was computed with s1's value);
- both: the same table as the upper place alone (mean 30).
So when a computation over all entities lies between the two places, choosing the upper or the lower place gives a different result. The run shows it for one computation (a mean), on a synthetic recipe (`opus_b1_run.py`, `opus_b1_run.out`, load 9.84 at start).
On the demo, run B3 nests `T1:ResFinder` above four joins and gives the same 17 plot tables as the six-place result (0 differ). I read every tier 1 of the demo's joins: the one grouping, in `Summary_phenotype_length_fragmentation` (`polars_group_by` by `sample_id`, `ST`), is per entity; the not-per-entity computations of the demo (the mean of `QA_population_zscore`, the grouping of `QA_aggregated_no_key` by country and year) are in tier 2, after every place B3 uses.
In a nested pair, a calculation over all entities that lies between the two places is done on the data of the upper place. The lower place can still remove a row that comes back from another table of a join: a step at `T1:ResFinder` alone leaves the entity in `qa_amr_genes_per_sample` (the metadata is the base table of `QA_AMR_per_sample`, so the row comes from the metadata); with `T1:QA_AMR_per_sample` as well the entity is gone (runs E and A3 of the retest). Both sentences are agreed by both agents. [Sonnet / Opus after the correction]

**G28 The fold of an empty tier 2 (latent).** The walk folds an empty tier 2, or one no plot reads, into the tier 1 (`lineage_walk.py:394-395`). For a source table read directly by plots and by joins, with an empty tier 2, the walk offers `T1:<table>` (which reaches the joins too) and the plots' own `T3:<plot>`, and not `T2:<table>`. For one such plot nothing is missing (its T3 reaches that plot alone); for two or more such plots no single place covers them without the joins. The audit copy already accepts `T2:<table>` when a plot reads it (read `audit_copy.py:177-179`). Not on the demo (`ResFinder` has a tier 2 with 2 steps). The fold is the walk's own PROVISIONAL choice, not a decision of hers.

**G29 "One trunk" (facts).** Under "one trunk", 7 demo tables would be rewritten (`QC_Reads_Anchor`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_L50_integer`), four of which have the metadata as base today. One trunk would also be added: `VirulenceFinder` has no table that joins it alone with the metadata and, after D-0523, it is a data table. The recipe check refuses a join of a joined table today (J04); a table made from several originals (`ST22_Anchor`: 6) would read several trunks that each carry the metadata columns (same-named columns: check J08).

**G30 A declared default (option for Q3).** For: the author states the default, nothing is guessed, D-0344 stays; it helps a user who is not the author ("well the problem is that the user might not be the author", D-0500). Against: a new key that the author must keep right; the app must still check that the place lies in that original's tree; it turns her rule of D-0549 into a per-recipe setting (reopens D-0549: information only). It names one default per tree; it does not make her quality case one step.

**G31 The smallest number of steps for her case under "one place per tree" (settled by hand).** The places of her case with nothing nested are: `ResFinder_with_metadata`, `MLST_with_metadata`, `FastP_with_metadata`, `Bracken_with_metadata`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_year_types`, `QA_aggregated_no_key`, `T2:ResFinder`, `T1:QA_L50_integer`, and the four Summary-family tables. The 5 places below `T1:ResFinder` (`ResFinder_with_metadata`, `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `T2:ResFinder`) lie in one tree, so they need 5 different steps; if the metadata's own tree does not count, 5 is the smallest number, and this schedule works: step 1 `ResFinder_with_metadata`, `MLST_with_metadata`, `FastP_with_metadata`, `QA_population_zscore`; step 2 `ST22_Anchor`; step 3 `QA_AMR_per_sample`, `AR1_MLST_Serotype_Virulence`, `T1:QA_L50_integer`; step 4 `QA_fanout_exhibit`; step 5 `T2:ResFinder`; the other places go in any step. If the metadata's own tree counts, 11 places lie in it (the 11 joins that read the metadata), so the smallest number is exactly 11. I re-derived this from the ingredients of the demo joins; it is a hand count, not a run. [Opus; I checked the schedule]

## 4. FACTS STILL TO RUN

Done: the tree property on the demo and on all shipped recipes that load; the three forms of "Remove from all the data" and her case without nesting, on two entities; the nested pair with a calculation between the places (G27); the smallest number of steps (G31, by hand).
Still to run, by a builder or reviewer, load permitting (no run above load 10):
- B2: the exported tier 1 files under (a), (b) and (c) of G26 (by construction, not run).
- The static reading of join side and kind against all the test runs and the 27 places: done only by reading (consistent with runs D and E, no contradiction); a full run belongs after the structure function exists.
- A dry run of "one trunk": the check refuses it by construction, so it needs the check relaxed in a scratch copy, after Q3.
- The fold of G28 on a scratch copy of the demo with the 2 tier-2 steps of `ResFinder` removed: needs the engine's plans; not needed for the design.
