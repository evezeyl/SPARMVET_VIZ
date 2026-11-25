# Recipes: what the two agents agree on, and what is open for her (v1, step 2 of D-0554, her decision D-0562)

Written by the Sonnet agent after reading in full `OPUS_recipes_1.md`, `RUN_REGISTER_opus_recipes.md` (RR1 to RR8) and its outputs `opus3_*`, with my own `SONNET_recipes_1.md` and `RUN_REGISTER_sonnet_recipes.md`. The Opus agent signs or objects. NOT confirmed by her. Nothing here is built and no recipe is changed.

Tags on every statement: [HER WORDS D-n] / [RECIPE FILE] / [GRAPH SCRIPT, both] (each agent's own YAML parse, no repository code) / [ENGINE RUN, which] / [CHECKER code] / [CODE READ file:line] / [REASONED, not run]. Every engine run was made from scratch in empty folders; nothing went through the old lineage code.

---

## HALF PAGE FOR HER

**What both agents agree on (all rest on runs we made separately and that gave the same numbers):**
1. A join with the metadata is written in tier 1. The check already refuses every join outside tier 1, and the engine cannot run one there. [D-0510; CHECKER ST05; ENGINE RUN, both]
2. There are two ways to write a result, and the place of a removal matters for each:
   - **One result per observation** (the data table first, the metadata second). Removing the entity at the data table or at the join takes it out of the result. Removing it at the metadata only empties the metadata columns of its rows.
   - **One result per entity, with zeros** (the metadata first, the counts filled with 0). Removing the entity at the table of counts leaves it in the result with a **false zero**. Only the join place, or the metadata, removes it.
3. A zero cannot tell "analysed, nothing found" from "not analysed": both show 0. [ENGINE RUN, Opus RR4]
4. There are three kinds of join: with the metadata, between two analysis tables on the entity id, and a look-up (another column, the right table has no entity id). The right side repeats the entity id in `ResFinder` and `VirulenceFinder`, so rows multiply (the metadata's 42 rows become 617 or 1731 in some demo tables).
5. Nothing checks today: that the entity id is unique where it is said to be, which side the metadata is on, what a block holds, that a look-up key is unique, or that an inner look-up join removes rows. In two shipped recipes four entity joins declare no entity id at all.
6. The recipe check is run when the app opens a recipe and in BLUEPRINT. The engine does not run it: a script that builds a recipe directly gets no check, and an unknown key is ignored silently there.
7. Of the five recipe forms we tried, only today's form and her reimport rule run in the engine. "One trunk", a declared default place and `from:` are refused by the check, and the first also fails in the engine.
8. The rename `is_entity_key` to `is_entity_id` touches 10 files of the demo (11 tables) and 111 tracked files in all (code, tests, documents, records). Proposed sentence for the spec is in G15.

**Where we differ:** two small points, in section 3. Everything else that differed in a number was settled by reading both outputs (section 0).

**Her questions, in the order I propose** (each is written in full in section 4; one line each):
1. Where must a rule be enforced (the engine does not run the check)? (viii)
2. Must the entity id be declared, and is "unique" judged on the file or on the table after tier 1? (iii)
3. The side of the metadata: rule, advice or documentation? (iv)
4. The result per entity with zeros: where does the removal go by default, and does the app say "the entity will show 0"? (ii)
5. A system for joins that are not metadata. (i) Then: an inner look-up join removes rows (vii), and may a look-up join come after tier 1 (vi, her question 27)?
6. A parent reused by several results (Q1 and Q2 of the paths file).
7. The recipe form (Q3).
8. "Remove from all the data" (Q5), then "can remain" before Apply (Q6). The Remove-step part of Q7 is independent and can be asked at any time.

---

## 0. What both agents ran on the same question, and whether the two results agree

| Question | Sonnet (mine) | Opus | Agree? | How a difference was settled |
|---|---|---|---|---|
| Join steps in the 50 shipped recipes that load | 33; 26 on the entity id (all `left`), 7 not [GRAPH SCRIPT `catalogue.out`] | 33; 26 declared on both sides, 0 on one side only, 7 on a column neither declares [GRAPH SCRIPT `opus3_catalogue.out`] | YES | Same 33, same 26, same 7 files and lines. |
| The 7 that are not entity joins | "look-up joins": 5 `inner`, 2 `left` | 3 look-up joins on `VF_gene` = `Gene_name` (inner) and 4 joins on `sample_id` in `2_test_data_ST22_dummy` (2, inner) and `figshare_integration` (2, left), two recipes that declare no entity id | YES, one naming difference | My "look-up" counted every join on an undeclared column. The 5 inner = 3 APEC + 2 in `2_test_data_ST22_dummy`; the 2 left = `figshare_integration`. Opus's split is the correct one: the app cannot tell an entity join from a look-up join where nothing is declared. I adopt it. |
| Demo: join steps and joined tables | 21 join steps in 16 joins; 19 left on `sample_id` (15 with the metadata, 4 between analyses), 2 inner look-ups | 21 steps in 12 joined tables | YES | The 16 joins include 4 with no join step (`QA_ST_with_NA`, `QA_year_types`, `QA_L50_integer`, `QA_aggregated_no_key`: one base table). 12 + 4 = 16. |
| Row counts of the demo's tier-1 tables | `ST22_Anchor` 42 to 617; `QA_fanout_exhibit` 1731; `AR1_MLST_Serotype_Virulence` 342; `QA_AMR_per_sample` 74; `Quast_with_metadata` 42 base rows to 126; `Summary_phenotype_length_fragmentation` 623 to 126 | the same numbers | YES | Both from the engine, in empty folders. Both note that 126 and 126 come from steps after the join (an unpivot, later steps), not from the join. |
| Right sides that are not unique on the join column | 13 of the 19 entity-join steps are unique; in the other 6 the right table is `ResFinder` or `VirulenceFinder` | `ResFinder`, `VirulenceFinder`, and also `Summary` and `Detailed_summary` | YES, two different questions | Mine counts right sides of join steps; Opus counts tables whose entity id is not unique at tier 1. `Summary` is a base (left) table, `Detailed_summary` is in no join. Both lists are right for their question. |
| ResFinder | 70 rows, "42 entities" in my text | 70 rows, 38 distinct `sample_id` | NO, a slip of mine | Read from the raw file: 70 rows, 38 distinct `sample_id`. Mine is corrected: 38. [file read] |
| Is the entity id unique in the raw file and at tier 1? | (not looked at) | `Summary` 623 rows, 42 distinct at tier 1 | NEW, settled by reading | The raw `Summary` file has 42 rows and 42 distinct `sample_id`; the tier-1 table `Summary` has 623 rows. So uniqueness changes between the file and tier 1. See G12 and question (iii). |
| Zeros pattern, removal at the counted table | `AM2`: a step at `RES_N` leaves the entity with count 0 (3 to 0) [ENGINE RUN `world2.full`] | s1 stays with `n_genes` 0 at `T1:RC` [ENGINE RUN RR4] | YES | Mine adds: `AM3` (metadata left, the observations right, then a group by the entity id, ONE graph, no second table) gives the same false zero for a step at the data table itself. So the false zero does not need her reimport rule; it comes from "metadata first, then fill zeros". |
| Pattern per observation | `AM1`: a step at the metadata empties the country of the entity's rows | JO: the same, `country` empty | YES | |
| A join of a join | J04 refuses; the engine fails: "names 'QM', which is not a data schema" | J04 refuses; the engine fails: "names 'JO', which is not a data schema" | YES | |
| A join step in tier 2 | ST05 "polars_join is only allowed in tier1"; the engine fails: "polars_join needs the resolved right table" | ST05 the same; the engine fails: "No step list and no ingredients - cannot assemble" | YES in result, two wordings | Different scratch recipes. Mine kept a tier-1 join and added a second join step in tier 2: tier 1 builds, tier 2 fails. Opus moved the only join step to tier 2: tier 1 has no steps and fails first. Both: the engine cannot run a join step in tier 2. |
| A declared default place | an unknown key, J01 (key put in a join) | an unknown key, S01 (key put in a schema) | YES | The code depends on where the key is written. The engine ignores the key (Opus RR8: it builds every table). |
| `from:` / derived tables | `derived_tables` at top level: T03; `from:` in a join: J01 [CHECKER] | `from:` in a join: J01; `derived_tables`: "REASONED, not run" | YES | I ran the checker for `derived_tables`; neither of us ran the engine on it (fact F1). |
| The recipe check in the engine's loader | not tried (I used the checker beside the engine) | the loader loaded all four refused forms (RR6) | confirmed by reading | `app/modules/cache_keys.py:484-509`: the loader reads the recipe with `ConfigManager` only. The check runs in `app/src/bootloader.py:438` (the load gate) and in BLUEPRINT (`blueprint_handlers.py:2850`). [CODE READ] |
| Rename: 10 or 11? | 10 files with `is_entity_key` | 11 tables | YES, both right (register X2) | 10 files, one line each; `Summary_input_fields.yaml` is included by two tables (`Summary`, `Summary_quality`, recipe lines 25 and 36); `APEC_STEC_virulence_genes` has none. 11 tables carry the flag. [RECIPE FILE] |
| Second table per extra use of an original | 16 more tables (FastP 2, Quast 3, Bracken 1, ResFinder 4, MLST 2, VirulenceFinder 2, APEC 1, Summary_quality 1) and 12 for the metadata | "8 originals and the metadata" | YES (register X1) | Rerun, own parse: the same 16 and 12 and the same 8 originals. `ResFinder` counts one reader that is a plot (`amr_heatmap` reads the original itself). |
| Row loss of an inner look-up join in the demo | `ST22_Anchor`: 617 rows (inner) against 1731 (left on a scratch copy): 1114 rows (64 %) leave, 42 entities in both [ENGINE RUN `L.out`] | (not measured; "inner look-up removes rows" only in the scratch world) | mine only | Opus's scratch world agrees in kind (JL left 4 rows). Adopted as mine, tagged. |

Result of point 0: no number of the two independent runs contradicts the other once the question is stated the same way. Two corrections of mine (ResFinder 38; the split of the 7). One new finding of the comparison (uniqueness differs between the file and tier 1).

---

## 1. Each Opus point: AGREE / DISAGREE / CHANGE

| Opus point | My answer | Evidence / reason |
|---|---|---|
| A1 three blocks, one kind each | AGREE; CHANGE one sentence | VirulenceFinder moving to `data_schemas` is now her own decision [HER WORDS D-0523: "VirulenceFinder moves"], not "if D-0513 is read as a decision". Who makes the move and when is not decided there. The advice "a data or metadata table without an entity id" AGREE as an advice; "an additional table with one" see section 3 point 1. |
| A2 the entity id | AGREE; CHANGE | Adopt Opus's split of the 7 (0 on one side only). Add the finding that uniqueness is a property of the table at tier 1, not of the file (raw `Summary` unique, tier-1 `Summary` 623 rows). "When it must be declared: when the audit offers a removal by the entity" AGREE [REASONED]; it is hers (iii). |
| A3 join with the metadata in tier 1 | AGREE | ST05 for every join [CHECKER, CODE READ `recipe_check.py:715`, `action_names.py:66`]; her D-0510 option A. |
| A3a pattern 1 | AGREE | Both engine runs. |
| A3b pattern 2, false zero, "analysed, nothing found" vs "not analysed" | AGREE; ADD | My `AM3` gives the false zero with one graph, with no second table. |
| A4 tiers as shared steps | AGREE | S07, J14 [CODE READ `recipe_check.py:415, 826`]; the engine reads ingredients at tier 1 [CODE READ `orchestrator.py:269-283`: "a join reads the T1 of its ingredients"]. |
| A5 results | AGREE | P01 needs `ui_label`; table results only a direction [HER WORDS D-0485, D-0487]. |
| A6 the audit block | AGREE | AU01; her D-0541. |
| A7 where the rules are enforced | AGREE, confirmed by code reading | `cache_keys.py:484-509`; the gate `bootloader.py:438`. |
| b.1 the catalogue and the table of demo joins | AGREE (section 0) | Same numbers. |
| b.2 the kinds | CHANGE | The two of us used "join between analyses" for different things (mine: a join of joins, which J04 refuses; Opus's: a join on the entity id between two analysis tables, 4 steps in the demo). One naming below (G9). I withdraw my row "no join between analyses in the demo". |
| b.3 options S0 to S3 | CHANGE | Merged with mine into one list J0 to J3 (section 4 (i)). One point of substance: the **recipe check cannot verify that a look-up table is unique on its key**; it reads the recipe, not the data. That is the data check (reads the files) [CODE READ `recipe_check.py` takes `raw`, catalogs, graph; `validate_data_analysis_recipe_data` reads the files]. Opus's "the check could verify" holds for the declared ids (both sides declare the same column), not for uniqueness. |
| Lean S2 (kind read from declarations, ids declared where a removal by entity is offered, uniqueness and many-to-many reported) | AGREE (mine was S1: the same idea, information at the data check) | One difference of wording only: where the report is shown (data check, BLUEPRINT Validate). |
| Q27 / S3 "allowed in tier 2" | CHANGE (I accept Opus) | I wrote "the graph would not change". That is wrong: a join in tier 2 adds an edge from `T1` of the ingredient into `T2` of the join. A removal at the look-up table would then reach `T2` but not `T1` of that join, which today no place does. My sentence is withdrawn. [REASONED from the graph rules; the engine facts are in section 0] |
| (c) forms table | AGREE; ADD | Add my run of `derived_tables` (T03). Add: the engine ignores `default_place` and `from:` silently [ENGINE RUN, Opus RR8]. |
| (d) demo candidates | AGREE; CHANGE two cells | Add my candidates: an entity block (only if a declared entity is required) and the 2 inner look-up joins (only if refusal). Remove "if D-0513 is read as a decision" (D-0523). |
| The old recipe study: KEPT / CHANGED / DROPPED | AGREE, with two corrections | Section 6. |
| (e) effects on Q1 to Q7 and five items she may be missing | AGREE all five | Item 2 ("a zero is not nothing found") and item 5 (a duplicated look-up key multiplies rows silently: 4 rows to 6, [ENGINE RUN RR5]) I also found in my scratch world. |

---

## 2. AGREED points

**G1. The three blocks.** `data_schemas`: results of analysis about the entity. `metadata_schema`: the information about the entity, one table, reserved id. `additional_datasets_schemas`: look-up tables. [HER WORDS D-0512: "the other data are either results of analysis for the sample information, so there is a common key with the metadata (sample id), or tables used as look-up"; D-0513] Enforced today: the shape of each block only. Nothing checks what a block holds; a metadata table written as an ordinary schema gives no code. [CHECKER, my world; CODE READ `recipe_tiers.py:34-35`] When not followed: the default place ("where original T1 and metadata are joined", D-0549) cannot be found from the recipe. New (advice): a data or metadata table with no entity id.

**G2. VirulenceFinder moves to `data_schemas` in the demo.** [HER WORDS D-0523] It is per-entity analysis data (984 rows at tier 1, 42 distinct `sample_id`). [RECIPE FILE; ENGINE RUN RR2] Who makes the move and when is not decided.

**G3. Joins are written in tier 1; a join reads source tables only.** Enforced: ST05 (a join action outside tier 1), J04 (a join of a join). The engine fails on both. [HER WORDS D-0344, D-0510; CHECKER ST05, J04; ENGINE RUN, both] When not followed (if it were allowed): places and parents change (G17).

**G4. The entity id.** Every table that holds the entity's column marks it. Unique at tier 1: a key; not unique: the column used for the join. [HER WORDS D-0562] Checked today: the population table holds the flag (E02), a number type is refused (E03). Checked nowhere: uniqueness. [CHECKER E02, E03; CODE READ `recipe_check.py:344-348, 456`; grep: no uniqueness check] When not followed: "remove from all the data" is not offered (the code already says so in plain words, `remove_from_all.py:170`), and the engine refuses a removal at a table with no such column ("column 'sample_id' is not in the table", [ENGINE RUN, both]).

**G5. Pattern 1, a result per observation.** The data table first, the metadata second, left join. A removal at the data table or at the join removes the entity; at the metadata it empties the metadata columns of its rows (the row stays). [HER WORDS D-0547, D-0549; ENGINE RUN, both: 4 rows, removal at `T1:R` 2 rows, at `T1:M` 4 rows with `country` empty] Enforced today: nothing; the side is free.

**G6. Pattern 2, a result per entity, with zeros.** The metadata first; the observations counted to the entity grain (a second table on the same file, or a group by the entity id after the join); then the nulls filled with 0. A removal at the metadata or at the join place removes the entity. A removal at the counted table, or at the data table of the one-graph form, leaves the entity with a FALSE ZERO (3 to 0 in my scratch world; 2 to 0 in Opus's). [ENGINE RUN, both] Enforced today: nothing. When not followed: the result changes in meaning without any message.

**G7. A zero cannot tell "analysed, nothing found" from "not analysed".** Both show 0 (Opus's s4 and s5). An entity with metadata and no observation exists in the result only when the metadata is the first table. [ENGINE RUN RR4; mine `world2.full`]

**G8. A removal at a table that holds no entity id is refused by the engine**: a look-up table, `T1:APEC_STEC_virulence_genes`, and (in my demo run) 3 places. [ENGINE RUN, both]

**G9. Three kinds of join, one naming.** (M) with the metadata; (A) between two analysis tables on the entity id; (L) look-up: another column, the right table holds no entity id. A join of joins is not a kind: it is refused (J04). In the demo: 15 steps of kind M, 4 of kind A, 2 of kind L (the two inner joins with the APEC list). [GRAPH SCRIPT, both; ENGINE RUN] How a step by the entity id behaves below each:
- M and A: the base table's rows leave; the other side's rows stay with that side's columns empty; the join place removes the entity. With a right side that repeats the entity id, rows multiply (`QA_fanout_exhibit` 42 to 1731; in Opus's scratch world 6 rows). [ENGINE RUN, both]
- L: a step at the data table or at the join removes the entity's rows; at the look-up table it is refused; with `inner` rows (and possibly an entity) can leave with no step (G14).

**G10. The tiers as shared steps, and the audit block.** [HER WORDS D-0539, D-0541] Enforced: a tier 2 nobody reads is refused (S07, J14); `audit_steps` only in an audit recipe (AU01). A step at a shared table changes every result that reads it (G17).

**G11. A table result has no form yet.** `derived_tables` is an unknown top-level key (T03), `from:` in a join an unknown key (J01); the engine ignores both [ENGINE RUN, Opus RR8; CHECKER]. Form 3 is not confirmed [HER WORDS D-0496].

**G12. Uniqueness depends on the table, not on the file.** The raw `Summary` file has 42 rows and 42 distinct `sample_id`; the tier-1 table `Summary` has 623 rows. `Detailed_summary`: 280 rows and 42 distinct in the file, 91 rows and 36 distinct at tier 1. `ResFinder`: 70 rows, 38 distinct, at both. [RECIPE FILE; ENGINE RUN RR2; file read] So "if it is unique it is a key" (D-0562) is a statement about a table at tier 1 (where joins read it), while the flag is written on the fields of the file.

**G13. What nothing checks today** (each: no code found, and the runs show the consequence): the uniqueness of the entity id (G12); the side of the metadata (G5, G6); the meaning of a block (G1); that a look-up key is unique (a duplicated key turns 4 rows into 6, [ENGINE RUN RR5]); that an inner look-up join removes rows (G14); recipes that declare no entity id (the 4 joins of `2_test_data_ST22_dummy` and `figshare_integration` look like look-up joins, section 0).

**G14. An inner look-up join removes rows with no audit step.** `ST22_Anchor` on its demo data: 617 rows with `how: inner`, 1731 with `left` on a scratch copy; 1114 rows (64 %) leave and the 42 entities are the same. In my scratch world the inner join loses an entity (e4: all its genes absent from the look-up; 5 rows against 9). [ENGINE RUN `L.out`, `world.out`]

**G15. The rename `is_entity_key` to `is_entity_id`** [HER WORDS D-0562: "`is_entity_id` for all cases"], in one move by a script (D-0525), the old key refused with the new name, no shim. Touches: 10 demo files (11 tables), 21 files under `config/data_analysis_recipes` (10 demo, 1 stress test, 4 retest, 6 templates), 2 scripts in `assets/scripts`, code in `libs/utils/src/utils` (10 files mention the key) and `app`, and 111 tracked files in all (218 lines, records and documents included). [RECIPE FILE; `git ls-files | grep`] **Proposed wording for the spec** (a proposal, hers to change): "`is_entity_id` marks the field of a table that holds the entity's id, whatever the table is. It is the column used to join the table with the metadata and with the other analysis tables. When its values are unique in the table after tier 1, it is a key of that table; when they are not, it is only a reference to the entity. A table with no entity id cannot receive a removal by the entity. It is never a row key."

**G16. The recipe check is not run by the engine.** The loader reads the recipe with `ConfigManager` only. The check runs at the load gate when the app opens a recipe and in BLUEPRINT. [ENGINE RUN, Opus RR6; CODE READ `cache_keys.py:484-509`, `bootloader.py:438`, `blueprint_handlers.py:2850`] A rule marked "enforced by the check" holds in HOME at opening and in BLUEPRINT on Validate. An unknown key is ignored silently by the engine (`default_place`, `from:`) [ENGINE RUN, Opus RR8].

**G17. Reading rules and parents.** A join reads the tier 1 of each ingredient [CODE READ `orchestrator.py:269-283`]; a step written at a shared table changes every result that reads it [HER WORDS D-0555; the paths file G17, G18]. A look-up table read by several joins is such a shared parent, and it never takes a removal by the entity.

**G18. The recipe forms as tried.**

| Form | Engine | Check | Graph |
|---|---|---|---|
| Today's form | runs | only the noise of a scratch recipe (no labels, paths) | a tree below each original; joins have several parents |
| Her reimport rule (a second table on the same file) | runs; a step at the first table does not reach the second | as today | two roots on the same file |
| One trunk (a join reads a join) | fails ("names ... not a data schema") | J04 | a joined node as a parent |
| A default place declared by the author | the key is ignored | S01 (in a schema) or J01 (in a join) | unchanged |
| Derived tables, `from:` | the key is ignored (`from:`; `derived_tables` not run) | J01 / T03 | no form to draw |
| A look-up join in tier 2 | fails (two wordings, section 0) | ST05 | an edge into a tier 2 |

[ENGINE RUN, both; CHECKER, both]

**G19. A table with entity id missing and a rule "metadata on the right".** A rule "metadata is the right table" would forbid pattern 2. The 4 demo joins with the metadata first are `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`. [REASONED; RECIPE FILE]

---

## 3. STILL DISAGREED (or not yet signed by the other agent)

1. **Opus's advice "an additional (look-up) table must not carry an entity id" (A1).** My position: information only, not an advice. A look-up table by the entity is legitimate (for example a list of entities with a status), and her words name only the AMR-genes example ([HER WORDS D-0512]). What would settle it: her answer to (i) and (iii), or a registered run that lists the shipped recipes' additional tables with an entity-id field (my script, one run; expected: 0, which would make the advice harmless but unneeded).
2. **Where uniqueness is reported.** My position (and the code reading): only at the data check, not at the recipe check. Opus's text leaves it at "the check could verify". To be signed or objected by Opus; settled by the code reading unless Opus finds a recipe-check path that sees data.

Everything else that looked different in the two positions is settled in section 0 (numbers) or section 1 (adopted).

---

## 4. FOR THE OWNER, most blocking first

How to read: "the entity" is what each row of the metadata is about (in the demo, a sample). The demo has 42. Numbers come only from runs rebuilt from scratch. A "lean" is a lean, not a decision. Where an option reopens something she decided, it says so as information. Nothing depends on how long it takes to build.

**Order proposed (which answer changes which), for all her open questions of this file and `PATHS_AND_DERIVED_AGREED.md`:**

1. (viii) where a rule is enforced. It changes how every "refused" below is read.
2. (iii) the entity id declared, and judged on the file or on tier 1. It changes what "remove from all the data" (Q5) can offer and what (i) can check. [PATHS Q7, old Q8]
3. (iv) the side of the metadata. It decides whether the zeros pattern exists. [PATHS Q7]
4. (ii) the result per entity with zeros: the default place and the false zero. It depends on (iv) and decides PATHS Q4 and Q6.
5. (i) the system for joins that are not metadata, then (vii) the inner look-up join, then (vi) look-up joins after tier 1 (her question 27). (vii) and (vi) are options inside (i).
6. PATHS Q1, a parent reused. It depends on (ii): the zeros pattern can be written without a second table on the same file (G6), so the reimport rule matters less if she accepts that. Then PATHS Q2.
7. (v) the recipe form (PATHS Q3). It depends on (i) (a join of a join, a look-up in tier 2) and on Q1.
8. PATHS Q5 "remove from all the data" (it needs (iii), Q1 and (ii)), then PATHS Q6 "can remain" before Apply (it needs (ii), (iv) and Q5). The Remove-step part of PATHS Q7 is independent: any time.

---

### (viii) The engine does not run the recipe check. A gap, or by design?

**What was found.** When the app opens a recipe, or in BLUEPRINT on Validate, the recipe is checked. When the engine builds a recipe on its own (a script, a test, any path that does not go through the load gate) it reads the recipe without the check. We tried four forms that the check refuses: all four were loaded. Two of them (`default_place`, `from:`) were built with the unknown key ignored, without a word. [ENGINE RUN RR6, RR8; CODE READ `cache_keys.py:484-509`, `bootloader.py:438`] A user in HOME opening a recipe meets the check first. A script that calls the engine does not.
**Her rule it touches:** no silent error [D-0050].
**Options:** (a) By design: the check is at the entrances a user uses (the gate, BLUEPRINT); a document says so. (b) A gap: the engine's loader also runs the check and refuses. (c) The engine refuses an unknown key itself. (d) Neither: say what you meant.
**Lean:** (a) for HOME as it stands, and verify the other entrances (bundle import, session restore, Gallery, Test Lab) go through the same gate (fact F4). **Reopens:** nothing she decided. **Links:** all "refused" words below.

### (iii) Must the entity id be declared? And judged on what?

**Her words.** "if its unique then it is a key if not it refers to the column used for the join (eg. to the metadata)" and "is_entity_id for all cases" [D-0562].
**What is the case today.** The flag is optional. The demo declares it in 10 files (11 tables). In `2_test_data_ST22_dummy` and `figshare_integration` 4 entity joins declare nothing, so the app sees them like look-up joins. Uniqueness is checked nowhere. When the flag is missing, "remove from all the data" is simply not offered, with the sentence "This recipe does not say which column is the entity key ..." (the code's own words, `remove_from_all.py:170`).
**A new fact.** Uniqueness changes between the file and tier 1: the raw `Summary` file has 42 rows for 42 entities, the table `Summary` after tier 1 has 623 rows for 42. `ResFinder` has 70 rows for 38 entities at both. The flag is written on the fields of the file; the joins read the table after tier 1. [RECIPE FILE; ENGINE RUN]
**Options.** (a) Optional as today; the removal by the entity is offered only where declared, with the plain sentence. (b) Required, refused by the check, in a recipe that has a metadata table. (c) Required as an advice. (d) Judged on tier 1: the data check shows, as information, "unique" or "repeated, 623 rows for 42 entities" for each declared table. (e) Neither: say what you meant.
**Leans:** (a) or (c) for the declaration; (d) as information for the uniqueness. **Reopens:** (b) would make 2 shipped recipes invalid until they declare the id. **Links:** PATHS Q5, Q7.

### (iv) The side of the metadata

**Her words.** "the metadata should be the right table (best practice and would solve problems (some users will have metadata for more samples so that will allow to join what really is in T1 without the extra in metadata))" [D-0549].
**What happens, on small invented data (5 entities, rebuilt from scratch).** Data left, metadata right: 4 rows (entities with no observation are absent). Metadata left, counts filled: 5 rows, 2 with 0. The demo has 4 joins with the metadata first: `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`. In `QA_AMR_per_sample`, `ResFinder` has 70 rows for 38 entities: the 4 other entities stay in the table with empty gene columns because the metadata is first.
**Options.** (a) A rule, refused by the check: it would forbid the zeros pattern (G6) and the 4 demo joins would be rewritten with the data on the left (the entities with no observation would leave those tables). (b) An advice: shown for a join whose result is per observation. (c) Documentation only. (d) Neither: say what you meant.
**Lean:** (b), because she wrote "best practice" and the earlier choice between a rule and an advice (D-0510) went to a rule only for the join with the metadata in tier 1. **Reopens:** (a) reopens nothing decided; it would forbid a pattern her own default place (where the original T1 and the metadata are joined, D-0549) relies on. **Links:** PATHS Q7; decides (ii).

### (ii) A result per entity, with zeros: where does the removal go, and what does the user see?

**What she sees today.** In HOME the audit writes a step at the plot's own table (T3), the choice of an earlier place being decided and not built [D-0316 to D-0318, D-0337]. The plot shows the entities; a bar with 0 looks like "nothing found".
**What the runs show (5 entities, rebuilt from scratch).** Entity s1 has 2 genes. A removal of s1: at the metadata or at the join, s1 is gone. At the table of counts, s1 STAYS in the result with 0 genes (a false zero). s4 (analysed, nothing found) and s5 (not analysed) both show 0. [ENGINE RUN, Opus RR4; mine `world2.full`, 7 entities, 3 to 0]
**Options.** (a) Nothing: the false zero stays a pitfall of the pattern. (b) The default place is the join, as in her rule [D-0549] (her case: "remove samples from all analyses but the ones that show the bad quality"); the lower place stays available but not ticked. (c) The dialog says, before Apply, "this entity will still be shown, with 0" for a left join followed by a fill (this is PATHS Q6). (d) The recipe maker writes a column that says "analysed" (documentation, a good-practice page; the app does not check it). (e) Neither: say what you meant.
**Lean:** (b) is already her default; add (c) and (d) if she wants the zero to be understood. **Reopens:** nothing decided. **Links:** PATHS Q4, Q6.

### (i) A system for joins that are not metadata

**Her words.** "We will need a system for joins that are not metadata though" [D-0562]; the look-up tables "can for example be used in a later join (for example the filtering of AMR genes of interest)" [D-0512].
**What exists in the demo.** 21 join steps: 15 with the metadata (kind M), 4 between analysis tables on the entity id (kind A), 2 look-ups with the APEC list (kind L, both `inner`). In the demo, joins with an analysis table that repeats the entity id multiply the rows: 42 rows of the metadata become 617 (`ST22_Anchor`) and 1731 (`QA_fanout_exhibit`). [ENGINE RUN RR2]
**What the user of the audit sees today:** nothing about the kind of a join; every join is a table. A removal at a look-up table is refused by the engine ("column 'sample_id' is not in the table").
**Options (one list; names provisional).**
- **J0.** Nothing new: the three kinds are described in a good-practice page.
- **J1.** The kind is read from the declared entity ids and the blocks (no new key). The recipe check can refuse a kind that contradicts the declarations; the data check reports, as information, what it measured: "the right side repeats the entity id: rows multiply (617 from 42)", "inner look-up join: rows can leave with no step". The user of the audit would see each join marked by its kind and a look-up table never offered for a removal by the entity.
- **J2.** The author writes the kind in each join step (a new key). The check can verify more, but a recipe has one more word per join (21 in the demo).
- **J3 (together with J0, J1 or J2).** Look-up joins may also be written in tier 2 (her question 27, below).
- **Neither: say what you meant.**
**What each does not solve:** none of them makes a look-up key unique (the data check can only say it); none helps a recipe that declares nothing (J1 reads those 4 entity joins as look-ups); none decides what a removal at a shared look-up should do.
**Lean:** J1 (both agents lean toward no new key). **Reopens:** J3 touches D-0344 ("revisit if needed") and the words of D-0510 ("other joins could be used after"). **Links:** PATHS Q3 (the form), (iii).

#### (vii) An inner look-up join removes rows with no audit step

**Facts.** `ST22_Anchor`: 617 rows with `inner`, 1731 with `left` on a scratch copy; 1114 rows leave (64 %), the entities are the same 42. In the small invented set one entity is lost altogether (5 rows against 9). [ENGINE RUN]
**Options.** (a) Inform: the data check says "this inner join removed N rows (M entities)"; the author keeps the choice. (b) Refuse an inner look-up join unless the author says so in the step. (c) Documentation only. (d) Neither.
**Lean:** (a), the software informs and the user decides. **Reopens:** nothing decided; (b) would change 2 demo joins.

#### (vi) May a look-up join come after tier 1? (her question 27)

**Found.** The check refuses every join outside tier 1 (ST05). The engine cannot run one: tier 2 receives the table, not the ingredients. A tier-2 join would be a new kind of edge in the graph (an edge from the look-up's tier 1 into the join's tier 2). Nothing we ran needs it: the two look-ups of the demo are already in tier 1. [ENGINE RUN, both; CODE READ; REASONED for the last sentence]
**Options.** (a) No, as today. (b) Yes, later, when a real recipe needs it. (c) Yes now: the check, the engine and the graph change. (d) Neither.
**Lean:** (a) now, (b) when a recipe needs it. **Reopens:** her words "other joins could be used after" (D-0510): they are not contradicted by (a) only if "after" means "after the join with the metadata", not "in tier 2". Which she meant is hers to say.

### (v) The recipe form (PATHS Q3)

**What runs.** Today's form (the checker has no complaint) and her reimport rule (D-0556). They both express her quality case through the join place. Refused: one trunk (J04, and the engine fails); a declared default place (S01/J01; the engine ignores the key); `from:` and derived tables (T03/J01; the engine ignores `from:`, `derived_tables` not run). What each needs: a new key in the check and the engine for the declared default; the check, the engine and the graph for derived tables; the check's J04 and the engine's reading of ingredients for the trunk.
**Her words.** "Yes, revisit if needed" (D-0344) for a join of joins; "yes we need the `from:`" (D-0517); form 3 not confirmed (D-0496).
**Options.** (a) Keep today's form, with the reimport rule as an advice. (b) One trunk. (c) A declared default place. (d) Derived tables. (e) Neither: say what you meant.
**Lean:** (a) until a real recipe needs the others. **Reopens:** (b) and (d) reopen D-0344 only if she chooses them. **Links:** PATHS Q1, Q2, Q3.

---

## 5. THE DEMO RECIPE: candidates only (nothing is changed)

| Change | Rule that requires it | Needed under EVERY option? | Files and count |
|---|---|---|---|
| `is_entity_key` becomes `is_entity_id` | G15 [D-0562], one move [D-0525] | YES (decided) | 10 files of `1_test_data_ST22_dummy/input_fields/` (11 tables); with the other recipes and templates: 21 files under `config/data_analysis_recipes`; with code, tests and documents: 111 tracked files |
| `VirulenceFinder` from `additional_datasets_schemas` to `data_schemas` | G2 [D-0523] | YES (her decision; who and when not decided) | 1 file (the demo's main recipe) |
| An `entity` block (noun, plural, population) | only if a declared entity is required, (iii) (b) or (c) | only under some answers | 1 file; the demo has none |
| The metadata moved to the right table in 4 joins | G5, only if "metadata right" is a rule, (iv) (a) | only under (iv) (a) | 4 joins (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`); it also changes their row sets |
| A kind on each join step | J2 | only under J2 | 21 steps in 12 joined tables |
| The 2 inner look-up joins to `left` plus a filter | (vii) (b) | only under (vii) (b) | 2 steps (`ST22_Anchor` step 5, `AR1_MLST_Serotype_Virulence` step 3); the demo loses 1114 rows now in `ST22_Anchor` otherwise |
| A second table per extra use of an original | her reimport rule as a rule | only under a rule for PATHS Q1 (Y-a, Y-r) | 16 tables, and 12 for the metadata (8 originals with more than one reader, one of which is read by a plot) |
| The 2 APEC joins moved to tier 2 | J3 | only under J3 | 2 joins |
| One declared default key | (v) (c) | only under (v) (c) | 12 originals |
| A join that reads a join; derived tables | (v) (b), (d) | only under those | not counted: the number depends on the form |

**The one dry run shown to her before anything is applied** [D-0525]. A script of the kind of `assets/scripts/migrate_display_names.py` (a dry run, `rules_toolchain.md`):
- for each file: the file and line, the old text, the new text and the ledger number of the rule;
- the places no decision covers, listed apart (the 4 joins with the metadata first, the 2 inner look-ups, the grain not stated in the descriptions S04/J03, and any recipe that declares no entity id);
- for each join whose side or kind changes, the rows of its tier-1 table and of each plot before and after, rebuilt from scratch on a copy (for example 42, 617, 1731);
- a check that the recipe check passes on every recipe after the rename and that the old key is refused with the new name;
- writes nothing but the report file she names (under `tmpAI/`); `--apply` works on a copy only and refuses on the repository until she has seen the list.
This is the same form as the names pass, so it adds no new kind of tool. [CODE READ `rules_toolchain.md`]

---

## 6. WHAT OF THE OLD RECIPE STUDY IS KEPT, CHANGED OR DROPPED

Checked against `RECIPE_PROPOSAL_refined.md` (flags of Part 0, Part 3), `RECIPE_REDESIGN_REVIEW.md` (parts 5 and 6), `RECIPE_PROPOSAL_answers.md` (Q8, Q11) and `RECIPE_PROPOSAL_dialog_walkthrough.md` (its header). Not rerun.

**KEPT (AGREE with Opus):** a definition comes before its use (form 3); a derived table reads one table (D-0517); the flag "a step at a shared table changes every reader" (now G17, D-0555); the two reading rules (a join reads tier 1, `from:` would read the last stage) and the warning not to unify them silently; J14 must count a derived table as a reader if derived tables come; result ids unique across the recipe.

**CHANGED:**
- "a result's tier 3 written by the audit only" is one place among others on a path (D-0553).
- The default ticks of D-0508 are now her defaults D-0549 and D-0550.
- "result: plot | table" stays a direction (D-0487); form 3 stays a candidate (D-0496).
- **Correction to what Opus lists as kept:** the duplicate result id is no longer an open defect: the task `RESULT-ID-TWICE-NOT-REFUSED` is marked done in `.claude/tasks/tasks.md:984` (the answers file cites line 958 and "not started"). Whether the refusal really works now is a fact to run (F5).
- **Correction to the study's counts:** the study's file counts (answers Q8) are for the renames of the plot keys; the rename of this file (`is_entity_id`) is a different move with its own count (G15).

**DROPPED:** the tick lists of the dialog walk-through (they rest on the old place list and on "every place ticked", D-0558); "one place per tree" (replaced by D-0553); the study's reading that the metadata line of Part 3 is a left-join effect of "reading A" without D-0510, D-0523 (answered by G1, G3).

---

## 7. FACTS STILL TO RUN (each: 1 requirement, 2 expected, 3 independence)

**F1. The engine on `derived_tables` and on `from:` in a table.**
1. Requirement: form 3 and derived tables [D-0496, D-0517]. 2. Expected: the engine loads and builds every table and ignores the new block, like `default_place`; if it fails, G11 changes. 3. Own scratch recipe, engine in a new empty folder, no lineage code.
**F2. Where the graph reaches under a tier-2 look-up join (the edge into a tier 2).**
1. Requirement: her question 27. 2. Expected: a removal at the look-up's tier 1 reaches the join's tier 2 and its plots, not the join's tier 1; today no place does that. 3. My own graph script on the scratch world; the engine does not run such a join, so this is a graph fact only.
**F3. The data check on repeated entity ids.**
1. Requirement: (iii) and G13. 2. Expected: `validate_data_analysis_recipe_data` reports nothing about a non-unique `is_entity_*` field (the demo's `ResFinder`); if it reports, G13's first item is wrong. 3. The data check on the demo and on a scratch recipe with repeated ids, in empty folders, no lineage code.
**F4. Which entrances run the check.**
1. Requirement: (viii). 2. Expected: the load gate, BLUEPRINT and the bundle import run the check; session restore, Gallery and Test Lab read recipes that were already checked. 3. Code reading, then one run of each entrance on a recipe the check refuses.
**F5. The duplicate result id.**
1. Requirement: no silent error [D-0050]; the task is marked done. 2. Expected: a plot id in two groups is now refused by the check with a plain line. 3. One scratch recipe, the check only.
**F6. A removal at the look-up table of a many-to-one look-up join in the demo, and the demo's own metadata-first joins.**
1. Requirement: (iv) and (ii), numbers on the demo itself rather than the invented set. 2. Expected: a removal of one sample at `T1:ResFinder` leaves it in `QA_AMR_per_sample` with empty gene columns, since the metadata is first; at `T1:metadata_schema` or the join it leaves. 3. The engine, new empty folders, steps written by hand into a scratch copy of the demo.
