# How to build recipes from the directed-graph model: what two agents agree on, and what is open for her (2026-11-23)

Note 2026-11-24: this file still holds quotations of the owner's words from the study rounds. The decisions are written once, in plain words, in the decision ledger; read `WHOLE_PICTURE.md` first.

**What this is.** Step 2 of her sequence (ledger D-0554): "how to build the recipes from the directed-graph model". It carries her decision D-0562 (the field `is_entity_key` is renamed `is_entity_id`) and her open topic "joins that are not metadata". An Opus agent and a Sonnet agent each wrote a position without seeing the other, then compared them and agreed before this text was written (D-0552). The evidence rules D-0558 to D-0561 hold: every engine run was rebuilt from scratch in its own empty folder, nothing went through the old lineage code, every run was registered before it ran with its three points, and an equality counts only when both sides were rebuilt. NOT confirmed by her. Nothing here is built and no recipe is changed.

**Where the evidence lives.** The registers are `tmpAI/coordinator/design_dialogue/RUN_REGISTER_sonnet_recipes.md`, `RUN_REGISTER_opus_recipes.md` and `RUN_REGISTER_sonnet_cause.md`. The scratch recipes, data and outputs are in the same folder (`paths2/`, `opus3_*`, `cause/`). This folder is scratch (not in git); the registers and the two agents' positions (`SONNET_recipes_1.md`, `OPUS_recipes_1.md`, `RECIPES_AGREED_AND_OPEN_v1.md`, `OPUS_signs_recipes_v1.md`) are the source of the numbers below. The cause of the two identical tables, and the catalogue of solutions for the join that starts from the metadata, are in `CAUSE_AND_SOLUTIONS_ZEROS.md` (written from the files and her rules, no run, D-0566; checked by both agents by reading; the final file is `CAUSE_AND_SOLUTIONS_ZEROS.md`, beside this one).

**The limits of the evidence.** The demo recipe `1_test_data_ST22_dummy` and small scratch recipes. One or two entities in the scratch runs, small data. The demo has 42 entities. What was not run is said in each place.

Tags: [HER WORDS D-n] / [RECIPE FILE] / [GRAPH SCRIPT] (each agent's own parse of the recipe files, PyYAML only) / [ENGINE RUN, which] / [CHECKER code] / [CODE READ file:line] / [HAND COUNT] / [READ SCAN] / [REASONED, not run].

---

## REVIEW OF 2026-11-23 (her order, ledger D-0577 and D-0578): what her decisions since changed in this file

**Why.** This file was written before her answers D-0568 to D-0576 and her D-0579. Since then she decided: the metadata is refused when its ids are wrong; two checks of the ids (X, Y); the completion of a result table with the marker "not in original data", in the recipe, required on every result table, confirmed once per data batch, noted in a separate log, also in the export; "stopping first" is her question. She wrote about the code: "the code is not build yet" [HER WORDS D-0573]. So "what is true today" and "what is decided and to build" are kept apart in each row.

**The words used for the status.** STILL TRUE (nothing in her words touches it). SETTLED (her words answer it; the line is named). CHANGED MEANING (the text is true of today's recipes, but the question it answers is no longer the same). SUPERSEDED (replaced; kept as history). STILL OPEN. Where only the agents say so, the row says "the agents' reading" and the line to confirm with her.

**The half page**

| Item | Status | Deciding line |
|---|---|---|
| 1 A join with the metadata is written in tier 1 | STILL TRUE | D-0510 |
| 2 Two ways of writing a result; the metadata first with the counts filled with 0 gives a false zero | CHANGED MEANING: with the completion decided, a per-entity result can start from the result table and keep every entity; the false zero at a table's own place is accepted; the facts stay true of today's recipes | D-0569, D-0573, D-0574 |
| 3 A zero cannot tell "analysed, nothing found" from "not analysed"; a removed entity also shows 0 | SPLIT: the first half stays true (the risk the recipe maker takes); "a removed entity also shows 0" is SUPERSEDED: with the completion a removed entity is absent or has no line, and an added line is marked | D-0572, D-0573 |
| 4 Three kinds of join; rows multiply | STILL TRUE | |
| 5 Nothing checks today (uniqueness, side, block meaning, look-up key, inner join; two recipes declare no id) | STILL TRUE of the code; CHANGED in what is to be built: the metadata's ids are refused when wrong, two checks of the ids are decided, the recipes declare their ids | D-0569, D-0573 |
| 6 The engine does not run the check | STILL TRUE; weightier: a refusal of the metadata holds only where the check runs | D-0573 |
| 7 The five forms tried | STILL TRUE (history); a new decided element, the completion block, was not among them | D-0574 |
| 8 The rename counts | STILL TRUE (counts of that date) | D-0562 |
| "Since the list was written, her words D-0563 to D-0566" | add one line: D-0567 to D-0578 and D-0579 | |
| "Before the demo recipe can be touched: (iii), (iv), (v) answered, a solution chosen for the join that starts from the metadata" | CHANGED: the solution is decided in substance (the completion, D-0574); (iii) partly settled, (iv) narrower, (v) the form of the block is open | D-0574 |

**Her eight questions of the file**

| Question | Status | Deciding line |
|---|---|---|
| (viii) The engine does not run the recipe check: a gap, or by design? | STILL OPEN, weightier | D-0573 |
| (iii) Must the entity id be declared; where is "unique" judged | CHANGED MEANING, partly SETTLED: the shipped recipes declare their ids (D-0569); the completion needs a declared id on a result table (D-0574; whether a table with none says so is the new question 6); for the metadata a repeated id may be an error (new question 2); where uniqueness of a result table's id is judged: STILL OPEN | D-0569, D-0573, D-0574 |
| (iv) "The join should not start with the metadata": rule, advice or documentation | STILL OPEN, narrower: the completion is the "solution we do not have yet" of D-0564, so the result-table-first join keeps every entity (new question 12) | D-0564, D-0574 |
| (ii) A result per entity with zeros: the default place for a removal | CHANGED MEANING: with the result table first a removal at the result table is complete; the default at the join (D-0549) stands; the "can remain" sentence (PATHS Q6) is needed only for metadata-first joins and paths through other originals | D-0549, D-0574 |
| (i) A system for joins that are not metadata | STILL OPEN | |
| (vii) An inner look-up join removes rows | STILL OPEN | |
| (vi) A look-up join after tier 1 (her question 27) | STILL OPEN | |
| (v) The recipe form (PATHS Q3) | STILL OPEN; one decided element: the completion block on each result table | D-0574 |

**The 19 agreed points**

| Point | Status | Deciding line |
|---|---|---|
| G1 The three blocks | STILL TRUE; the metadata block is the population of the two checks; the completion applies to result tables (data schemas), never to look-up tables | D-0574 |
| G2 VirulenceFinder moves to `data_schemas` | STILL TRUE, not done; after the move it gets the completion block | D-0523, D-0574 |
| G3 Joins in tier 1, source tables only | STILL TRUE | D-0344, D-0510 |
| G4 The entity id | STILL TRUE, with a new fact: the entity id is the condition for the completion; the metadata's ids are checked and refused when wrong | D-0562, D-0567, D-0573, D-0574 |
| G5 A result per observation | STILL TRUE | |
| G6 A result per entity with zeros (the metadata first, the fill with 0, the false zero) | SUPERSEDED as the way to give zeros; its facts stay true of today's recipes (agents' reading, to confirm) | D-0573, D-0574 |
| G7 A zero cannot tell analysed from not analysed; an entity with metadata and no observation exists in the result only when the metadata is the first table | SPLIT: the first half STILL TRUE (the accepted risk); the second half SUPERSEDED: with the completion it exists with the result table first | D-0572, D-0574 |
| G8 A removal at a table with no entity id is refused by the engine | STILL TRUE | |
| G9 Three kinds of join | STILL TRUE | |
| G10 The tiers as shared steps; the audit block | STILL TRUE | D-0539, D-0541 |
| G11 A table result has no form yet | STILL TRUE of the code; the design is decided (D-0485, D-0487), its key open | D-0485, D-0487 |
| G12 Uniqueness differs between the file and tier 1 | STILL TRUE (a fact); "where unique is judged" is question (iii) | |
| G13 What nothing checks today | STILL TRUE of the code; the id check, the overlap and the two checks are decided, not built | D-0570, D-0573 |
| G14 An inner look-up join removes rows | STILL TRUE | |
| G15 The rename `is_entity_key` to `is_entity_id` | STILL TRUE (decided, not done) | D-0562, D-0567 |
| G16 The engine does not run the check | STILL TRUE | |
| G17 Reading rules and parents | STILL TRUE, with a new fact: a completed result table also reads the metadata (an edge from the metadata's file under reading (α), from its tier 1 under (β); new question 8) | D-0574 |
| G18 The forms as tried | STILL TRUE (history); the completion block was not tried | |
| G19 A rule "metadata on the right" would forbid the zeros pattern written with the metadata first | CHANGED MEANING: with the completion the zeros can be written with the result table first, so such a rule forbids only a spelling | D-0574 |

**The demo recipe candidates and the rest**

| Row | Status | Deciding line |
|---|---|---|
| The rename `is_entity_id` | STILL TRUE (YES, decided) | D-0562 |
| VirulenceFinder moves | STILL TRUE (YES) | D-0523 |
| An `entity` block | STILL TRUE (only under some answers) | |
| The metadata moved off the first place in the 4 joins | CHANGED: no longer needs a solution to be chosen; remains a choice under new question 12 | D-0574 |
| A kind on each join step; the inner look-ups; the reimport copies; the APEC joins in tier 2; the declared default key; joins of joins | STILL TRUE (only under their questions) | |
| NEW (decided in substance): the completion block with its stated meaning on every result table; on the demo 9 data tables today (10 after the VirulenceFinder move), only ResFinder receives lines (4) | NEW | D-0574 |
| NEW: ResFinder's steps that stamp "Detected" and count rows are adapted | NEW | D-0573 |
| NEW: `qa_amr_genes_per_sample`, whose text says "4 with 0 genes", follows the stated meaning | NEW | D-0573 |
| NEW: `demo_abromics`'s metadata without its 3 id-less lines | NEW (dry run) | D-0569, D-0573 |
| NEW: the two recipes with no declared id declare it | NEW (dry run) | D-0569 |
| "The old recipe study": the line "result: plot | table stays a direction (D-0487)" | CHANGED: a decided design, not built; its key open | D-0485, D-0487 |
| Facts F1 to F6 | STILL TO RUN, only when she asks; the expected numbers of F6 hold for today's recipe | |

**What stays hers to answer, from this file.** (viii), (i), (vii), (vi), (v), and narrower (ii), (iii) and (iv). They are now in the one list of `CAUSE_AND_SOLUTIONS_ZEROS.md` (section "Added 2026-11-23 (ledger D-0573 to D-0579)"), with the questions that her answers created. Where this file and that list differ, that list is the later.

---

## HALF PAGE FOR HER

**What both agents agree on** (the numbers come from runs made separately that gave the same result):
1. A join with the metadata is written in tier 1. The check already refuses every join outside tier 1, and the engine cannot run one there. [HER WORDS D-0510]
2. A result can be written in two ways, and where a removal is written matters for each:
   - **A result per observation** (the data table first, the metadata second). Removing the entity at the data table or at the join takes it out. Removing it at the metadata only empties the metadata values of its rows.
   - **A result per entity with zeros** (the metadata first, the counts filled with 0). Removing the entity at the table of counts leaves it in the result with a **false zero**: the entity is still there and shows 0. Only the join place or the metadata takes it out.
   > **Update of 2026-11-23 (ledger D-0573, D-0574):** the "metadata first, counts filled with 0, false zero" way is no longer the way to give zeros; the completion with the marker "not in original data" is decided. The false-zero facts stay true of today's recipes. See the review section at the top.
3. A zero cannot tell "analysed, nothing found" from "not analysed". Both show 0. A removed entity also shows 0 there.
   > **Update of 2026-11-23 (ledger D-0572, D-0573):** the first sentence stays true. "A removed entity also shows 0 there" is superseded: an added line carries the marker "not in original data", and a removed entity is absent.
4. There are three kinds of join: with the metadata, between two analysis tables on the entity id, and a look-up (another column; the right table has no entity id). Where the right side repeats the entity id, rows multiply (the metadata's 42 rows become 617 or 1731 in some demo tables).
5. Nothing checks today: that the entity id is unique where it is said to be, which side the metadata is on, what a block holds, that a look-up key is unique, or that an inner look-up join removes rows. In two shipped recipes four entity joins declare no entity id at all.
6. The recipe check runs when the app opens a recipe and in BLUEPRINT. The engine does not run it: a script that builds a recipe directly gets no check, and an unknown key is ignored silently there.
7. Of the five recipe forms tried, only today's form and her reimport rule run in the engine. "One trunk", a declared default place and `from:` are refused by the check; the first also fails in the engine.
8. The rename `is_entity_key` to `is_entity_id` touches 10 files of the demo (11 tables), 21 recipe files, and 111 tracked files in all (218 lines; code, tests, documents and records included). The sentence for the specification is approved by her and is in G15 (D-0567).

**The sentence for the specification of `is_entity_id` is approved by her** (ledger D-0567; her words: "yes it seems good"). It is in G15.

**Since the list was written, her words D-0563 to D-0566:** she asked for the cause of the two tables that stayed identical, then said "well there we have it the join should not start with the medata or we need a solution we do not have yet ." (D-0564), then "H1, H2 appear to be a consequence of that - so I think we need to find solution for that and then retest." (D-0565), then "no need to test that now then" (D-0566). The cause and a catalogue of solutions (no run) are in `CAUSE_AND_SOLUTIONS_ZEROS.md`. In short: the entity stayed because its 23 rows come by another path than the one she chose, and because the metadata is the first table of the join. A zero and a removal at the data table are the same state of the table; the catalogue lists what can be written and what the user would see. Then D-0567 to D-0579 (the review section at the top).

**The two agents differ on one wording only:** see "Open between the two agents" at the end.

**Her questions, in the order proposed** (each is written in full below; one line each):
1. (viii) Where must a rule be enforced, since the engine does not run the check?
2. (iii) Must the entity id be declared, and where is "unique" judged: in the file or in the table after tier 1?
3. (iv) Her direction "the join should not start with the metadata": a rule, an advice or documentation?
4. (ii) The result with zeros: the default place for a removal. Then PATHS Q4.
5. (i) A system for joins that are not metadata. Then (vii) an inner look-up join, and (vi) may a look-up join come after tier 1 (her question 27)?
6. PATHS Q1 (a parent reused by several results), then Q2.
7. (v) The recipe form (PATHS Q3).
8. PATHS Q5 "remove from all the data", then Q6 "can remain" before Apply. The Remove-step part of Q7 is independent: any time.

**Before the demo recipe can be touched:** (iii), (iv) and (v) must be answered, a solution must be chosen for the join that starts from the metadata (D-0564, D-0565), and the dry run must be shown to her. Her words: "we need to finalize the recipe design with the from and hyerarchy ... before we can do a big move on all demo recipes" [D-0525].

---

## HER QUESTIONS

How to read: "the entity" is what each row of the metadata is about (in the demo, a sample; the demo has 42). Numbers come only from runs rebuilt from scratch. A "lean" is a lean, not a decision. Where an option reopens something she decided, it says so as information. Nothing depends on how long it takes to build. Questions of `PATHS_AND_DERIVED_AGREED.md` are called PATHS Q1 to Q7.

**Order, and which answer changes which:**
1. (viii) changes how every "refused" below is read.
2. (iii) decides what "remove from all the data" (PATHS Q5) can offer and what (i) can check. [PATHS Q7, old Q8]
3. (iv) decides whether a result per entity with zeros keeps the metadata as the retained side. [PATHS Q7]
4. (ii) depends on (iv); then PATHS Q4 (the default place where her rule says nothing), which (ii) decides for the zeros pattern; and PATHS Q6.
5. (i), then (vii) and (vi) (options inside (i)).
6. PATHS Q1, then Q2. They depend on (ii): the zeros can be written without a second table on the same file, so the reimport rule matters less if she accepts that.
7. (v) (PATHS Q3) depends on (i) and on Q1.
8. PATHS Q5 (needs (iii), Q1, (ii)), then PATHS Q6 (needs (ii), (iv), Q5). The Remove-step part of PATHS Q7 is independent.

### (viii) The engine does not run the recipe check. A gap, or by design?

**What was found.** When the app opens a recipe, or in BLUEPRINT on Validate, the recipe is checked. When the engine builds a recipe on its own (a script, a test, any path that does not go through the opening) it reads it without the check. Four forms that the check refuses were tried: all four were loaded. Two of them (`default_place`, `from:`) were built with the unknown key ignored, without a word. [ENGINE RUN, Opus RR6, RR8; CODE READ `app/modules/cache_keys.py:484-509`, `app/src/bootloader.py:438`] A user in HOME meets the check when the recipe opens; a script that calls the engine does not.
**Her rule it touches:** "No silent error that is the rule." [D-0050, her turn of 2026-11-14]
**Options.** (a) By design: the check is at the entrances a user uses (the opening, BLUEPRINT); a document says so. (b) A gap: the engine's loader also runs the check and refuses. (c) The engine refuses an unknown key itself. (d) Neither: say what you meant.
**Lean:** (a) for HOME as it stands, and verify the other entrances (bundle import, session restore, Gallery, Test Lab) go through the same opening (fact F4). **Reopens:** nothing she decided. **Links:** every "refused" below.

### (iii) Must the entity id be declared? And where is "unique" judged?

> **Update of 2026-11-23 (ledger D-0578):** CHANGED MEANING, partly SETTLED: the shipped recipes declare their ids (D-0569); the completion needs a declared id on a result table (D-0574; whether a table with none says so is question 6 of the new list); for the metadata a repeated id may be an error (question 2); where uniqueness of a result table's id is judged: STILL OPEN.

**Her words.** "specify that if its unique then it is a key if not it refers to the column used for the join (eg. to the metadata)", "I think is_entity_id for all cases", "in some cases is_entity_id is a real key instead no ..." [D-0562]. The sentence she approved says "If its values are unique in the table, it is also the key of the table" [D-0567]. It does not say whether "the table" is the file or the table after tier 1: that is the question below, and her sentence is not an answer to it.
**What is the case today.** The flag is optional. The demo declares it in 10 files (11 tables). In `2_test_data_ST22_dummy` and `figshare_integration` 4 entity joins declare nothing, so the app sees them like look-up joins. Uniqueness is checked nowhere. When the flag is missing, today's library (no screen calls it) does not offer "remove from all the data", with a plain sentence (`remove_from_all.py:170`; old code, described only). [RECIPE FILE; CODE READ]
**A new fact.** Uniqueness changes between the file and tier 1. The raw `Summary` file has 42 rows for 42 entities. The table `Summary` after tier 1 has 623 rows for 42. `ResFinder` has 70 rows for 38 entities at both. The flag is written on the fields of the file; the joins read the table after tier 1. [RECIPE FILE; ENGINE RUN, Opus RR2; file read, Sonnet]
**Options.** (a) Optional as today; the removal by the entity is offered only where declared. (b) Required, refused by the check, in a recipe that has a metadata table. (c) Required as an advice. (d) The data check shows, as information, what it measured after tier 1 for each declared table: "unique" or "repeated, 623 rows for 42 entities". (d2) The data check shows it for the raw file instead ("`Summary`: unique, 42 rows"). (e) Neither: say what you meant.
**Leans (as leans):** Sonnet: (a) or (c) for the declaration, (d) as information. Opus: (c), and the uniqueness shown as information both in the file and after tier 1, since they differ. **Consequence:** (b) would make 2 shipped recipes invalid until they declare the id. **Reopens:** nothing decided. **Links:** PATHS Q5, Q7.

### (iv) Her direction: "the join should not start with the metadata". A rule, an advice or documentation?

> **Update of 2026-11-23 (ledger D-0578):** STILL OPEN, narrower: the completion is the "solution we do not have yet" of D-0564, so the result-table-first join keeps every entity (question 12 of the new list; D-0564, D-0574).

**Her words.**
- "The metadata should be the right table -- best practice and would solve problems (some users will have metadata for more samples so that will allow to join what really is in T1 without the extra in metadata)" [D-0549]
- "The left join early with the metadata would just make the metadata for the same sample be repeated a lot" [D-0562]
- "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564]
- "H1, H2 appear to be a consequence of that - so I think we need to find solution for that and then retest." [D-0565]

**What is true on the demo.** For a result per observation, the data first and the metadata second works today: removing the entity at the data table or at the join takes it out. For a result that must show every entity with a zero, the metadata has to be the table whose rows are all kept; the options for that are in the catalogue of solutions in `CAUSE_AND_SOLUTIONS_ZEROS.md`, section (g) (candidates (a) to (f)). They are not repeated here. The demo has 4 joins with the metadata first: `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`. [READ SCAN; RECIPE FILE]

> **Correction of 2026-11-23 (ledger D-0568; see `CAUSE_AND_SOLUTIONS_ZEROS.md` and `OVERLAP_AND_POPULATION.md`):** for a result that must show every entity with a zero, the entities that should appear must be kept by one table that is not the counted data table: the metadata, or a table of the analysed entities used as the first table of the join (candidate (a2), found after this file was signed). The sentence above names only the metadata.
**What this question asks, apart from the catalogue.** Is "the join should not start with the metadata" a rule that the check refuses, an advice, or documentation, for the results that do not need zeros?
**Options.** (a) A rule on the order of the tables in the file, refused by the check. (b) An advice, shown for a join whose result is per observation. (c) Documentation only. (d) Neither: say what you meant.
**Lean (as a lean):** (b), because she wrote "best practice" and the earlier choice between a rule and an advice (D-0510) went to a rule only for the join with the metadata in tier 1. **Reopens:** nothing decided. (a) would forbid the result per entity with zeros written with the metadata first (G6); whether a right join with the metadata second is also forbidden depends on whether the rule is about the order in the file or about which table keeps all its rows (see the catalogue, candidate (e)). **Links:** PATHS Q7; decides (ii).

### (ii) A result per entity with zeros: where does the removal go by default, and what does the user see?

> **Update of 2026-11-23 (ledger D-0578):** CHANGED MEANING: with the result table first a removal at the result table is complete; the default at the join (D-0549) stands; the "can remain" sentence (PATHS Q6) is needed only for metadata-first joins and paths through other originals. Still hers, narrower (D-0549, D-0574).

**Her words.** "my case where I want to remove the samples from all analyses BUT the ones that show the bad quality" [D-0549]; "where original T1+ metadata are joined" [D-0549]; her direction of D-0564 and D-0565 above.
**What she sees today.** In HOME the audit writes a step at the plot's own table (T3); the choice of an earlier place is decided and not built [D-0316 to D-0318, D-0337]. The plot shows the entities; a bar with 0 looks like "nothing found".
**What the runs show (5 entities, rebuilt from scratch).** Entity s1 has 2 genes. Removing s1: at the metadata or at the join, s1 is gone. At the table of counts, s1 STAYS in the result with 0 genes (a false zero). s4 (analysed, nothing found) and s5 (not analysed) both show 0. [ENGINE RUN, Opus RR4; Sonnet `world2.full`, 7 entities, 3 to 0]
**The options for the zeros** (counting per entity first, keeping the metadata first with the step at the join place, a completion of the population declared in the recipe, a derived table, a right or full join, others) are in `CAUSE_AND_SOLUTIONS_ZEROS.md`, section (g), with what the author writes, what the audit does and what the user sees. They are not repeated here, and none is chosen.
**What this question asks, apart from the catalogue.** Whatever way the zeros are written: is the default place for a removal on this kind of result the join place (her rule D-0549), and does the dialog say before Apply that a step at the data table's place "can remain" (PATHS Q6)? (a) Default at the join place, with the sentence. (b) Default at the join place, without the sentence. (c) No default for this kind of result: the user always chooses. (d) Neither: say what you meant.
**Lean (as a lean):** (a). **Reopens:** nothing decided. **Links:** PATHS Q4, Q6.

### (i) A system for joins that are not metadata

**Her words.** "We will need a system for joins that are not metadata though" [D-0562]. "those for example can be used as later join (eg, our example of filtering AMR genes of interest)" [D-0512]. "As we said the other data tables can be used in later joins." [D-0523]
**What exists in the demo.** 21 join steps: 15 with the metadata (kind M), 4 between analysis tables on the entity id (kind A), 2 look-ups with the APEC list (kind L, both `inner`). Where an analysis table repeats the entity id, rows multiply: the metadata's 42 rows become 617 (`ST22_Anchor`) and 1731 (`QA_fanout_exhibit`). [ENGINE RUN, Opus RR2; GRAPH SCRIPT, both] (The kinds are counted by Sonnet's parse; the kind of a step in a table of several joins depends on what its left side already holds, a convention to state.)
**What the user of the audit sees today:** nothing about the kind of a join; every join is a table. A removal at a look-up table is refused by the engine ("column 'sample_id' is not in the table"). [ENGINE RUN, both]
**Options (one list; names provisional).**
- **J0.** Nothing new: the three kinds are described in a good-practice page.
- **J1.** The kind is read from the declared entity ids and the blocks (no new key). The recipe check can say when a kind contradicts the declarations; the data check, or a build, reports what it measured as information: "the right side repeats the entity id: rows multiply (617 from 42)", "inner look-up join: rows can leave with no step". The user of the audit would see each join marked by its kind and a look-up table never offered for a removal by the entity.
- **J2.** The author writes the kind in each join step (a new key; 21 steps in the demo).
- **J3 (together with J0, J1 or J2).** Look-up joins may also be written in tier 2 (her question 27, below).
- **Neither: say what you meant.**
**What each does not solve:** none makes a look-up key unique (only the data check can say it); none helps a recipe that declares nothing (J1 reads those 4 entity joins as look-ups); none decides what a removal at a shared look-up should do.
**Information from the check on a table of `additional_datasets_schemas` that declares an entity id (agreed wording):** the check says so as information, with its reason: by her words, analyses about the entities are data tables (D-0512) and information about them is the metadata (D-0511); a look-up by the entity may still be what the author means. On the shipped recipes this concerns 2 of the 4 additional tables, both `VirulenceFinder` (the table her D-0523 moves in the demo). [GRAPH SCRIPT, Opus RR10]
**Lean:** J1 (both agents lean toward no new key). **Reopens:** J3 touches D-0344 ("revisit if needed") and her D-0510 words "other joins could be used after". **Links:** PATHS Q3 (the form), (iii).

#### (vii) An inner look-up join removes rows with no audit step

**Facts.** `ST22_Anchor`: 617 rows with `inner`, 1731 with `left` on a scratch copy; 1114 rows leave (64 %), the 42 entities are the same. In a small invented set one entity is lost altogether (5 rows against 9). [ENGINE RUN, Sonnet `L.out`, `world.out`]
**Options.** (a) Inform: the data check says "this inner join removed N rows (M entities)"; the author keeps the choice. (b) Refuse an inner look-up join unless the author says so in the step. (c) Documentation only. (d) Neither.
**Lean:** (a). **Reopens:** nothing decided; (b) would change 2 demo joins.

#### (vi) May a look-up join come after tier 1? (her question 27)

**Found.** The check refuses every join outside tier 1 (ST05). The engine cannot run one: tier 2 receives the table, not the ingredients. A tier-2 join would be a new kind of edge in the graph (an edge from the look-up's tier 1 into the join's tier 2). Nothing we ran needs it: the two look-ups of the demo are already in tier 1. [ENGINE RUN, both; CODE READ; REASONED for the last sentence]
**Options.** (a) No, as today. (b) Yes, later, when a real recipe needs it. (c) Yes now: the check, the engine and the graph change. (d) Neither.
**Lean:** (a) now, (b) when a recipe needs it. **Reopens:** her words "metada is a certain type of data - other joins could be used after but join with metadata must be done at T1" [D-0510] and "As we said the other data tables can be used in later joins" [D-0523]. Whether "after" and "later" mean "after the join with the metadata" or "in tier 2" is hers to say.

### (v) The recipe form (PATHS Q3)

> **Update of 2026-11-23 (ledger D-0578):** STILL OPEN; one decided element: the completion block on each result table (D-0574).

**What runs.** Today's form and her reimport rule (D-0556). Both express her quality case through the join place. Refused: one trunk (J04; the engine also fails); a declared default place (S01 or J01 by where the key is written; the engine ignores the key); `from:` and derived tables (T03 or J01; the engine ignores `from:`; `derived_tables` was not run in the engine, fact F1). What each needs: a new key in the check and the engine (declared default); the check, the engine and the graph (derived tables); J04 and the engine's reading of ingredients (one trunk). [ENGINE RUN, both; CHECKER, both]
**Her words.** "Yes, revisit if needed" [D-0344] for a join of joins; "yes we need the from:" [D-0517]; form 3 not confirmed [D-0496].
**Options.** (a) Keep today's form, with the reimport rule as an advice. (b) One trunk. (c) A declared default place. (d) Derived tables. (e) Neither: say what you meant.
**Lean:** (a) until a real recipe needs the others. **Reopens:** (b) and (d) reopen D-0344 only if she chooses them. **Links:** PATHS Q1, Q2, Q3.

---

## AGREED POINTS

**G1. The three blocks.** `data_schemas`: results of analysis about the entity. `metadata_schema`: the information about the entity, one table, reserved id. `additional_datasets_schemas`: look-up tables. [HER WORDS D-0512: "the other data are either results of analysis for the sample information so there is a common key with the metadata (sample id) - or tables used at look up"; D-0513] Enforced today: the shape of each block only; nothing checks what a block holds. [CHECKER, Sonnet world; CODE READ `recipe_tiers.py:34-35`] When not followed: the default place ("where original T1 + metadata are joined", D-0549) cannot be found from the recipe. New (advice): a data or metadata table with no entity id; and the information line of (i) for an additional table that declares one.

**G2. VirulenceFinder moves to `data_schemas` in the demo.** [HER WORDS D-0523: "Yes "VirulenceFinder moves""] It is per-entity analysis data (984 rows at tier 1, 42 distinct `sample_id`). [RECIPE FILE; ENGINE RUN, Opus RR2] Who makes the move and when is not decided.

**G3. Joins are written in tier 1; a join reads source tables only.** Enforced: ST05, J04; the engine fails on both. [HER WORDS D-0344, D-0510; CHECKER; ENGINE RUN, both]

**G4. The entity id.** Every table that holds the entity's column marks it. Unique in the table: it is also the key of the table; repeated: it refers to the entity and the table has several rows per entity. [HER WORDS D-0562; the wording approved by her, D-0567, in G15] Where uniqueness is judged, in the file or in the table after tier 1, is her question (iii) (G12). Checked today: the population table holds the flag (E02), a number type is refused (E03). Checked nowhere: uniqueness. [CHECKER E02, E03; CODE READ `recipe_check.py:344-348, 456`] When not followed: "remove from all the data" is not offered (the library, which no screen calls today, says so: `remove_from_all.py:170`; old code, described only), and the engine refuses a removal at a table with no such column ("column 'sample_id' is not in the table"). [ENGINE RUN, both]

**G5. A result per observation.** The data table first, the metadata second, left join. A removal at the data table or at the join removes the entity; at the metadata it empties the metadata values of its rows (the row stays). [HER WORDS D-0547, D-0549; ENGINE RUN, both: 4 rows, removal at the data table 2 rows, at the metadata 4 rows with `country` empty] Enforced today: nothing.

**G6. A result per entity with zeros.** The metadata first; the observations counted to the entity grain (a second table on the same file, or a group by the entity id after the join); then the empty counts filled with 0. A removal at the metadata or at the join place removes the entity. A removal at the counted table, or at the data table of the one-graph form, leaves the entity with a FALSE ZERO (3 to 0 in Sonnet's scratch world, 2 to 0 in Opus's). [ENGINE RUN, both] Enforced today: nothing. When not followed: the result changes in meaning without any message.

> **Update of 2026-11-23 (ledger D-0573, D-0574):** SUPERSEDED as the way to give zeros (the agents' reading, to confirm); the facts stay true of today's recipes.

**G7. A zero cannot tell "analysed, nothing found" from "not analysed".** Both show 0. An entity with metadata and no observation exists in the result only when the metadata is the first table. [ENGINE RUN, Opus RR4; Sonnet `world2.full`]

> **Update of 2026-11-23 (ledger D-0572, D-0574):** the first half stays true. The sentence "an entity with metadata and no observation exists in the result only when the metadata is the first table" is superseded: with the completion it exists with the result table first.

**G8. A removal at a table that holds no entity id is refused by the engine**: a look-up table, `T1:APEC_STEC_virulence_genes`, and 3 places in Sonnet's demo run. [ENGINE RUN, both]

**G9. Three kinds of join, one naming.** (M) with the metadata; (A) between two analysis tables on the entity id; (L) look-up: another column, the right table holds no entity id. A join of joins is not a kind: it is refused (J04). In the demo: 15 steps of kind M, 4 of kind A, 2 of kind L (the two inner joins with the APEC list). [GRAPH SCRIPT, both; ENGINE RUN] (The counts 15 M, 4 A, 2 L: Sonnet's parse only; the kind of a step in a table of several joins depends on what its left side already holds, a convention to state.) How a step by the entity id behaves below each:
- M and A: the base table's rows leave; the other side's rows stay with that side's columns empty; the join place removes the entity. With a right side that repeats the entity id, rows multiply (`QA_fanout_exhibit` 42 to 1731; 6 rows in Opus's scratch world). [ENGINE RUN, both]
- L: a step at the data table or at the join removes the entity's rows; at the look-up table it is refused; with `inner`, rows (and possibly an entity) can leave with no step (G14).

**G10. The tiers as shared steps, and the audit block.** [HER WORDS D-0539, D-0541] Enforced: a tier 2 nobody reads is refused (S07, J14); `audit_steps` only in an audit recipe (AU01). A step at a shared table changes every result that reads it (G17).

**G11. A table result has no form yet.** `derived_tables` is an unknown top-level key (T03), `from:` in a join an unknown key (J01); the engine ignores `from:` [ENGINE RUN, Opus RR8; CHECKER]. Form 3 is not confirmed [HER WORDS D-0496].

**G12. Uniqueness can differ between the file and the table after tier 1.** The raw `Summary` file has 42 rows and 42 distinct `sample_id`; the tier-1 table `Summary` has 623 rows. `Detailed_summary`: 280 rows and 42 distinct in the file, 91 rows and 36 distinct at tier 1. `ResFinder`: 70 rows, 38 distinct, at both. [RECIPE FILE; ENGINE RUN RR2; file read] (The counts of the raw files: Sonnet's file read only.) So "if its unique then it is a key" (D-0562), and "unique in the table" in the sentence she approved (D-0567), need a place where uniqueness is judged: the file, where the flag is written, or the table after tier 1, which joins read. The two differ for `Summary` and `Detailed_summary`. It is her question (iii).

**G13. What nothing checks today:** the uniqueness of the entity id (G12); the side of the metadata (G5, G6); the meaning of a block (G1); that a look-up key is unique (a duplicated key turns 4 rows into 6, [ENGINE RUN, Opus RR5]); that an inner look-up join removes rows (G14); recipes that declare no entity id (the 4 joins of `2_test_data_ST22_dummy` and `figshare_integration`). The recipe check reads the recipe, not the data: uniqueness and row multiplication need the files (the data check) or a build. [CODE READ `recipe_check.py`, `data_analysis_recipe_validator.py`]

**G14. An inner look-up join removes rows with no audit step.** `ST22_Anchor`: 617 rows with `how: inner`, 1731 with `left` on a scratch copy; 1114 rows (64 %) leave and the 42 entities are the same. In Sonnet's scratch world the inner join loses an entity. [ENGINE RUN: Sonnet only, `L.out`, `world.out`]

**G15. The rename `is_entity_key` to `is_entity_id`** [HER WORDS D-0562: "I think is_entity_id for all cases"], in one move by a script (D-0525), the old key refused with the new name, no shim. Touches: 10 demo files (11 tables), 21 files under `config/data_analysis_recipes` (10 demo, 1 stress test, 4 retest, 6 templates), 2 scripts in `assets/scripts`, code in `libs/utils/src/utils` and `app`, and 111 tracked files in all (218 lines; records and documents included). [RECIPE FILE; `git ls-files | grep`, Sonnet; Opus RR9, main tree `d7b9ea44`] **The wording for the specification, approved by the owner** (ledger D-0567; the review session's sentence, her words: "yes it seems good"; it replaces the sentence the two agents had proposed). Copied exactly from the channel block M621: "`is_entity_id: true` marks the column that identifies the entity (on the demo, the sample). It is the column used to join a table with the metadata and to find the entity's rows, for example to remove an entity from the analysis. If its values are unique in the table, it is also the key of the table: one row per entity. If its values repeat, the table has several rows per entity (a long table, for example one row per sample and gene). The column then refers to the entity, and a row is identified by the entity id together with the other columns that distinguish the rows." It is to be used, in the one big move (D-0525), in the format specification, the good-practice page, the help of BLUEPRINT and the messages of the recipe check for `is_entity_id`. The specification must NOT say that the app checks uniqueness or the long format: it does not. Her sentence says "unique in the table"; it does not say whether "the table" is the file or the table after tier 1, which stays her question (iii).

**G16. The recipe check is not run by the engine.** The loader reads the recipe with `ConfigManager` only. The check runs at the opening and in BLUEPRINT. [ENGINE RUN, Opus RR6; CODE READ `cache_keys.py:484-509`, `bootloader.py:438`, `blueprint_handlers.py:2850`] A rule marked "enforced by the check" holds in HOME at opening and in BLUEPRINT on Validate. An unknown key is ignored silently by the engine (`default_place`, `from:`) [ENGINE RUN, Opus RR8].

**G17. Reading rules and parents.** A join reads the tier 1 of each ingredient [CODE READ `orchestrator.py:269-283`]; a step written at a shared table changes every result that reads it [HER WORDS D-0555; PATHS G17, G18]. A look-up table read by several joins is such a shared parent, and it never takes a removal by the entity.

> **Update of 2026-11-23 (ledger D-0574):** new fact: a completed result table also reads the metadata; the parent is the metadata's file (reading α) or its tier 1 (reading β).

**G18. The recipe forms as tried.**

| Form | Engine | Check | Graph |
|---|---|---|---|
| Today's form | runs | only the noise of a scratch recipe (no labels, paths) | a tree below each original; joins have several parents |
| Her reimport rule (a second table on the same file) | runs; a step at the first table does not reach the second | as today | two roots on the same file |
| One trunk (a join reads a join) | fails ("names ... not a data schema") | J04 | a joined node as a parent |
| A default place declared by the author | the key is ignored | S01 (in a schema) or J01 (in a join) | unchanged |
| Derived tables, `from:` | `from:` ignored (`derived_tables` not run) | J01 / T03 | no form to draw |
| A look-up join in tier 2 | fails (two wordings: "needs the resolved right table", "No step list and no ingredients") | ST05 | an edge into a tier 2 |

[ENGINE RUN, both; CHECKER, both]

**G19. A rule "metadata on the right" would forbid pattern 2 written with the metadata first.** The 4 demo joins with the metadata first are `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`. [REASONED; RECIPE FILE; READ SCAN]

> **Update of 2026-11-23 (ledger D-0574):** CHANGED MEANING: with the completion the zeros pattern can be written with the result table first; such a rule forbids only a spelling.

---

## THE DEMO RECIPE: candidates only (nothing is changed)

| Change | Rule that requires it | Needed under EVERY option? | Files and count |
|---|---|---|---|
| `is_entity_key` becomes `is_entity_id` | G15 [D-0562], one move [D-0525] | YES (decided) | 10 files of `1_test_data_ST22_dummy/input_fields/` (11 tables); 21 files under `config/data_analysis_recipes`; 111 tracked files, 218 lines (code, tests, documents, records) |
| `VirulenceFinder` from `additional_datasets_schemas` to `data_schemas` | G2 [D-0523] | YES (her decision; who and when not decided) | 1 file (the demo's main recipe) |
| An `entity` block (noun, plural, population) | only if a declared entity is required, (iii) (b) or (c) | only under some answers | 1 file; the demo has none |
| The metadata moved off the first place in the 4 joins | G5; only if "the join should not start with the metadata" is a rule, (iv) (a); or a solution of the catalogue | only under (iv) (a) or a chosen solution | 4 joins (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`); it also changes their row sets |
| A kind on each join step | J2 | only under J2 | 21 steps in 12 joined tables |
| The 2 inner look-up joins to `left` plus a filter | (vii) (b) | only under (vii) (b) | 2 steps (`ST22_Anchor` step 5, `AR1_MLST_Serotype_Virulence` step 3) |
| A second table per extra use of an original | her reimport rule as a rule | only under a rule for PATHS Q1 | 16 tables, and 12 for the metadata (8 originals with more than one reader, one read by a plot) [GRAPH SCRIPT, Sonnet X1; Opus agrees] |
| The 2 APEC joins moved to tier 2 | J3 | only under J3 | 2 joins |
| One declared default key | (v) (c) | only under (v) (c) | 12 originals |
| A join that reads a join; derived tables | (v) (b), (d) | only under those | not counted: it depends on the form |
| A table per entity, counted before the join | candidate (a) of the catalogue | only under a chosen solution | per table, not counted |

**The one dry run shown to her before anything is applied** [D-0525]. A script of the kind of `assets/scripts/migrate_display_names.py` (a dry run, `rules_toolchain.md`):
- for each file: the file and line, the old text, the new text and the ledger number of the rule;
- the places no decision covers, listed apart (the 4 joins with the metadata first, the 2 inner look-ups, the grain not stated in the descriptions S04/J03, and any recipe that declares no entity id);
- for each join whose side or kind changes, the rows of its tier-1 table and of each plot before and after, rebuilt from scratch on a copy (for example 42, 617, 1731);
- a check that the recipe check passes on every recipe after the rename and that the old key is refused with the new name;
- writes nothing but the report file she names (under `tmpAI/`); `--apply` works on a copy only and refuses on the repository until she has seen the list.
This is the same form as the names pass, so it adds no new kind of tool. [CODE READ `rules_toolchain.md`]

---

## THE OLD RECIPE STUDY: kept, changed, dropped

Checked against `RECIPE_PROPOSAL_refined.md` (flags of Part 0, Part 3), `RECIPE_REDESIGN_REVIEW.md (removed 2026-11-24 in the cleaning of the studies; see git history)` (parts 5 and 6), `RECIPE_PROPOSAL_answers.md (removed 2026-11-24 in the cleaning of the studies; see git history)` (Q8, Q11) and `RECIPE_PROPOSAL_dialog_walkthrough.md (removed 2026-11-24 in the cleaning of the studies; see git history)` (its header). Not rerun.

**KEPT:** a definition comes before its use (form 3); a derived table reads one table (D-0517); the flag "a step at a shared table changes every reader" (now G17, D-0555); the two reading rules (a join reads tier 1, `from:` would read the last stage) and the warning not to unify them silently; J14 must count a derived table as a reader if derived tables come; result ids unique across the recipe.

**CHANGED:**
- "a result's tier 3 written by the audit only" is one place among others on a path (D-0553).
- The default ticks of D-0508 are now her defaults D-0549 and D-0550.
- "result: plot | table" stays a direction (D-0487); form 3 stays a candidate (D-0496).
  > **Update of 2026-11-23:** a table as a result is a decided design, not built; its key is open (D-0485, D-0487).
- The duplicate result id is no longer an open defect: the task `RESULT-ID-TWICE-NOT-REFUSED` is marked done in `.claude/tasks/tasks.md:984` (the answers file cites line 958 and "not started"). Whether the refusal works now is a fact to run (F5).
- The study's file counts (answers Q8) are for the renames of the plot keys; the rename of this file (`is_entity_id`) is a different move with its own count (G15).

**DROPPED:** the tick lists of the dialog walk-through (they rest on the old place list and on "every place ticked", D-0558); "one place per tree" (replaced by D-0553); the study's reading that the metadata line of Part 3 is a left-join effect of "reading A" without D-0510, D-0523 (answered by G1, G3).

---

## FACTS STILL TO RUN (only when she asks; each with its three points)

**F1. The engine on `derived_tables` and on `from:` in a table.**
1. Requirement: form 3 and derived tables [D-0496, D-0517]. 2. Expected: the engine loads and builds every table and ignores the new block, like `default_place`; if it fails, G11 changes. 3. Own scratch recipe, engine in a new empty folder, no lineage code.
**F2. Where the graph reaches under a tier-2 look-up join (the edge into a tier 2).**
1. Requirement: her question 27. 2. Expected: a removal at the look-up's tier 1 reaches the join's tier 2 and its plots, not the join's tier 1; today no place does that. 3. Own graph script on a scratch recipe; the engine does not run such a join, so this is a graph fact only.
**F3. The data check on repeated entity ids.**
1. Requirement: (iii) and G13. 2. Expected: `validate_data_analysis_recipe_data` reports nothing about a non-unique entity-id field (the demo's `ResFinder`); if it reports, G13's first item is wrong. 3. The data check on the demo and on a scratch recipe with repeated ids, in empty folders, no lineage code.
**F4. Which entrances run the check.**
1. Requirement: (viii). 2. Expected: the opening and BLUEPRINT run the check, and so does the bundle import; session restore, Gallery and Test Lab read recipes that were already checked. 3. Code reading, then one run of each entrance on a recipe the check refuses.
**F5. The duplicate result id.**
1. Requirement: "No silent error that is the rule." [D-0050]; the task is marked done. 2. Expected: a plot id in two groups is now refused by the check with a plain line. 3. One scratch recipe, the check only.
**F6. The demo's own metadata-first joins.**
1. Requirement: (iv) and (ii), numbers on the demo itself rather than the invented set. 2. Expected: a removal of one entity at `T1:ResFinder` leaves it in `QA_AMR_per_sample` with empty gene columns (the metadata is first); at the metadata or at the join it leaves. 3. The engine, new empty folders, steps written by hand into a scratch copy of the demo.
**The retest after her choice of a solution** (the one in D-0565) is described, one entry per candidate with its three points, at the end of `CAUSE_AND_SOLUTIONS_ZEROS.md`; it is run only after her choice.

---

## Open between the two agents

None.

**Signed by both agents: Sonnet (this file) and Opus (OPUS_signs_recipes_v1.md and OPUS_signs_recipes_v2.md; all replacements applied; the spec sentence of `is_entity_id` is the wording approved by the owner, D-0567)**

**D-0573 to D-0579 additions and the review:** Sonnet (this file) and Opus (`OPUS_checks_review_v1.md`, S1 to S18 applied).
