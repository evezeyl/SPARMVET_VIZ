# OPUS position: how to build the recipes from the graph model (step 2 of D-0554), v1, written blind

Her order: "and then we need to review how to build the recipes from that and then modify recipe 1_ST22 viz where it needs to be if necessary" [HER WORDS D-0554]. Her new decision and open topic: "is_entity_id for all cases - specify that if its unique then it is a key if not it refers to the column used for the join (eg. to the metadata). We will need a system for joins that are not metadata though" [HER WORDS D-0562].

**Tags:** [HER WORDS D-n] / [RECIPE FILE path] / [MY GRAPH SCRIPT] / [ENGINE RUN run, output] / [CODE READ file:line] / [REASONED, not run].

**Runs:** `RUN_REGISTER_opus_recipes.md`, each run written before it was made.
- RR1 to RR8 are done.
- Two runs contradicted my stated expectation, and both are findings:
  - RR2: Summary and Detailed_summary also hold several rows per sample, and a joined tier-1 table can change its row count through its other steps.
  - RR6: the engine's loader does not run the recipe check; RR8 asks the check itself.
- Scratch recipes, data and outputs are in `tmpAI/coordinator/design_dialogue/opus3_*`.
- Scratch data: metadata M with s1 to s5 (s5 has no analysis); genes R with several rows per sample (s4 has none); a quality table Q with one row per sample; a look-up table G of genes; a second per-observation table V.

---

## (a) The construction rules

| # | Rule: what the author writes | Today | What breaks for the audit when it is not followed |
|---|---|---|---|
| A1 | **Three blocks, one kind each** [HER WORDS D-0513]: `data_schemas` holds results of analysis about the entities, `metadata_schema` holds the information about the entities, `additional_datasets_schemas` holds look-up tables. "results of analysis for the sample information so there is a common key with the metadata (sample id) - or tables used at look up" [HER WORDS D-0512] | The blocks exist [CODE READ `recipe_tiers.py:34-35`]; nothing checks what a block holds. On the demo, VirulenceFinder (per-sample analysis) sits under additional; her words: "I think VirulenceFinder should be moved under data_schemas" [D-0513] | The default place ("where original T1+ metadata are joined", D-0549) is found only through the metadata block. A removal by entity at a look-up table is refused by the engine [ENGINE RUN RR5: "column 'sample_id' is not in the table"]. **New, as an advice:** a data or metadata table without an entity id; an additional table with one. |
| A2 | **The entity id** [HER WORDS D-0562]: every table that holds the entity's column marks it `is_entity_id`. Unique in its table: a key. Not unique: the reference used to join | The field is `is_entity_key` (the rename is decided, D-0562, one move D-0525). It is optional. Checked: not a number type (E03, `recipe_check.py:456`) and, when an `entity:` block exists, that its population has the field (E02, `:344-348`) [CODE READ] | Without a declaration the app cannot tell an entity join from a look-up join. Across the 50 shipped recipes, 26 join steps join on a column both sides declare, 0 on one side only, and 7 on a column neither declares: 3 are look-up joins and 4 are joins on `sample_id` in two recipes that declare nothing (`2_test_data_ST22_dummy`, `figshare_integration`) [MY GRAPH SCRIPT RR1]. "Remove from all the data" (D-0416) and the default place both need the entity's column. **When it must be declared (old Q8):** when the audit offers a removal by the entity [REASONED]. Hers to decide. |
| A3 | **The join with the metadata is in tier 1** | Enforced: ST05 refuses every join action outside tier 1 [CODE READ `recipe_check.py:715`; ENGINE RUN RR8] | See A3a and A3b below. |
| A3a | **Pattern 1, a result per observation:** the data table first, the metadata second (left join) [HER WORDS D-0547: "T1 original -> left_join -> metadata"; D-0549] | An advice; the side is free | Rows are the observations; entities with no data are absent (s4, s5). A removal at the data table takes the entity out. A removal at the metadata only empties the metadata columns of the entity's rows [ENGINE RUN RR3]. |
| A3b | **Pattern 2, a result per entity that needs zeros:** count to the entity grain in a table of its own (today: a second table on the same file), then join with the metadata FIRST and fill the zeros | An advice; nothing checks it | Rows are every metadata entity (s1 to s5). A removal at the metadata or at the join place takes the entity out. **A removal at the counted table leaves the entity with a FALSE ZERO** (s1: 2 genes becomes 0) [ENGINE RUN RR4]. The zero also cannot tell "analysed, nothing found" (s4) from "not analysed" (s5): both are 0 [ENGINE RUN RR4]. |
| A4 | **The tiers as shared steps** [HER WORDS D-0539]: tier 1 holds what every reader needs; tier 2 what the plots of that table need; tier 3 what one result needs. A join reads the tier 1 of its ingredients | Enforced: a tier 2 that no plot reads is refused (S07, J14, `recipe_check.py:415`, `:826`); the engine reads ingredients at tier 1 [CODE READ `orchestrator.py:269-283`] | A step in a tier 1 that only one reader needs changes every reader (`PATHS_AND_DERIVED_AGREED.md` G17, G18). |
| A5 | **The results**: a plot today; a table as a result is decided as a direction (D-0485, D-0487: "a good key system ... a definition of what the result is, a table or a plot"); the recipe form with derived tables is not confirmed (D-0496) | Plots only (P01 needs `ui_label`) | Nothing for the audit today; a table result needs its kind (new key, hers). |
| A6 | **The audit block after each tier** [HER WORDS D-0541: "audit steps can be written at each tier after the original tier block. The original recipe steps are always kept"] | Enforced: `audit_steps` only in an audit recipe [CODE READ `orchestrator.py:80-100`] | - |
| A7 | **Where the rules are enforced** | The engine's loader does NOT run the check [ENGINE RUN RR6: all four refused forms loaded]. The check runs at the app's load gate and in BLUEPRINT [CODE READ `app/modules/data_analysis_recipe_validator.py:303`] | A rule "enforced by the check" protects HOME at opening and BLUEPRINT on Validate. It does not protect a script that runs the engine directly. |

---

## (b) Joins that are not metadata

**b.1 The catalogue.** Shipped recipes [MY GRAPH SCRIPT RR1]: 33 join steps; 26 entity joins (declared on both sides); 7 undeclared (3 look-up joins on `VF_gene` = `Gene_name`, inner; 4 joins on `sample_id` in recipes that declare nothing). The demo's tier-1 tables, rebuilt from scratch [ENGINE RUN RR2]:

| Joined table | Base, then the right tables (unique on the join column?) | Base rows -> T1 rows | Still holds the entity id |
|---|---|---|---|
| `FastP_`, `Bracken_`, `MLST_with_metadata` | data, metadata (unique) | 42 -> 42 | yes |
| `ResFinder_with_metadata` | ResFinder (70 rows, 38 samples), metadata (unique) | 70 -> 70 | yes |
| `Quast_with_metadata` | Quast, metadata (unique) | 42 -> 126 (its `polars_unpivot` after the join) | yes |
| `QC_Reads_Anchor` | FastP, then Quast, Bracken, metadata (all unique) | 42 -> 42 | yes |
| `ST22_Anchor` | metadata, then FastP (unique), ResFinder (no), MLST (unique), VirulenceFinder (no), APEC on `Gene_name` (unique, look-up, inner) | 42 -> 617 | yes |
| `AR1_MLST_Serotype_Virulence` | MLST, then metadata (unique), VirulenceFinder (no), APEC (look-up, inner) | 42 -> 342 | yes |
| `QA_AMR_per_sample` | metadata, ResFinder (no) | 42 -> 74 | yes |
| `QA_fanout_exhibit` | metadata, ResFinder (no), VirulenceFinder (no) | 42 -> 1731 | yes |
| `QA_population_zscore` | metadata, Quast (unique) | 42 -> 42 | yes |
| `Summary_phenotype_length_fragmentation` | Summary (623 rows, 42 samples), Summary_quality (unique) | 623 -> 126 (its later steps) | yes |

The entity id is not unique in ResFinder, VirulenceFinder, Summary and Detailed_summary [ENGINE RUN RR2]. In these tables it is "the column used for the join", in her words.

**b.2 The kinds and how a step by the entity behaves below each** [ENGINE RUN RR5]:
- **Look-up join** (on another column; the look-up table holds no entity id). The entity's rows go when the step is at the data table. A step by the entity at the look-up table is refused by the engine. A look-up table with a duplicated key multiplies rows silently (G2: 4 rows become 6).
- **Join between analyses on the entity id.**
  - With one row per entity on the right, no rows multiply.
  - With several rows on both sides, rows multiply (JV: 6 rows; the demo: `QA_fanout_exhibit` 1731).
  - A removal at the right table keeps the left's rows, with the right's columns empty (JV: s1's 2 rows, `vf` empty).
- **Join with the metadata:** A3a and A3b above.

**b.3 Options for "a system"** (what she would see). Her question 27, whether look-up joins may come after tier 1, is open [D-0562 "NOT decided"].

| # | Option | The author writes | The check could verify | The user of the audit sees |
|---|---|---|---|---|
| S0 | Neither: today | nothing new | nothing about the kinds | joins drawn alike |
| S1 | A kind per join step (`entity` / `lookup` / `between analyses`; names PROVISIONAL) | one word per join step | lookup: the right table is unique on the join column (G2 is refused or flagged) and holds no entity id. entity: the join column is the declared entity id on both sides. Many-to-many: the row multiplication is reported as information | each join marked by kind; a look-up table never offered for a removal by entity; "rows multiply here" on a many-to-many join |
| S2 | No new key: the kind is read from the declarations (entity id on both sides = entity join; on neither = look-up) and from the blocks (A1) | the entity id on every table that holds it (A2) | the same as S1, from the declarations | the same as S1 |
| S3 | S1 or S2, and look-up joins also allowed in tier 2 (her question 27) | a join step in a tier 2 | today ST05 refuses it, and the engine cannot run it: it has no ingredients after tier 1 [ENGINE RUN RR8: "No step list and no ingredients"]; the check, the engine and the graph (an edge into a tier 2) would change | a look-up join drawn into the tier 2 of a table |

**Lean, as a lean:** S2 with the entity id required where the audit offers a removal by entity, and with the check's verifications (look-up side unique; many-to-many reported). S3 only when a real recipe needs it, as she said of joins of joins ("Yes, revisit if needed", D-0344). Reason: S2 asks the author for nothing that A1 and A2 do not already ask. [REASONED]

---

## (c) The recipe form

| Form | Example | Does the engine run it? | Recipe check | My graph | Her quality case |
|---|---|---|---|---|---|
| Today's form | `both`: R, RC, Q, M; JO = [R, M], JE = [M, RC], JQ = [Q, M]; plots on JO, JE, JQ | yes, every table [ENGINE RUN RR3, RR4, RR7] | only the errors every minimal scratch recipe has (no labels, absolute paths) [RR8] | `T1:JO`, `T1:JE`, `T1:JQ` each have 2 parents; the metadata lies above the 3 plots [MY GRAPH SCRIPT] | one place, `T1:JO`: the analysis table loses s1, the quality table keeps it [ENGINE RUN RR7] |
| Her reimport rule | in `both`: RC reads R's file | yes [RR4]; a step at `T1:R` does not reach JE | as today | `T1:R` reaches only `p_obs`; `T1:RC` reaches only `p_ent` | as today |
| "One trunk" (a join reads a join) | JJ = [JO, Q] | no: "names 'JO', which is not a data schema" [ENGINE RUN RR8] | J04 [RR8; CODE READ `recipe_check.py:867`] | a joined node as a parent | the trunk's place covers every plot of that original; her case still needs places below it [REASONED] |
| A default place declared by the author | `default_place: JO` on R | yes, the key is ignored [RR8] | S01, unknown key [RR8] | unchanged | the declared place ticked; a check that it lies below its table would be new [REASONED] |
| Derived tables with `from:` | `from: R` on JO | yes, ignored [RR8] | J01, unknown key [RR8]; a block `derived_tables` would be an unknown top-level key [REASONED, not run] | a derived table would be a node with one parent | as today, with derived tables as more places |

What would have to change for the refused forms:
- One trunk: J04 and the engine's reading of ingredients.
- A declared default: the list of schema keys of the spec.
- `from:`: a new block, the engine, the graph, and J14 counting a derived table as a reader, as the earlier study found.
[CODE READ as above; REASONED]

---

## (d) What the demo would need, if necessary (candidates only; the demo is not changed)

| Candidate | Rule | Needed under every option? | Depends on |
|---|---|---|---|
| `is_entity_key` becomes `is_entity_id` (11 tables) | A2, D-0562 | yes (decided) | the one move, D-0525 |
| VirulenceFinder moved to `data_schemas` | A1; her words in D-0513 | under every option, if D-0513 is read as a decision | D-0513 |
| The metadata as the second table in `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore` | A3a | only if "metadata right" becomes a rule, and only where the result is per observation; a per-entity result with zeros keeps the metadata first (A3b) | PATHS Q7 (the side of the metadata) |
| A kind on each of the 21 join steps (in 12 joined tables) | S1 | only under S1 | b.3 |
| A second table per extra use of a shared original (8 originals and the metadata) | her reimport rule | only under Y-a or Y-r | PATHS Q1 |
| The two APEC joins in tier 2 | S3 | only under S3 | question 27 |
| Summary tables as derived tables | `from:` | only if form 3 is confirmed | D-0496, PATHS Q3 |

**The dry run shown to her before anything is applied** (D-0525). For each file of the demo:
- every change: file, line, old text, new text, and the ledger number of the rule;
- every place that no decision covers;
- for each join whose side or kind changes, the rows of its tier-1 table and of its plots before and after, rebuilt from scratch;
- nothing written to the demo; an apply only on a copy.

This is the form of the existing names dry run (`assets/scripts/migrate_display_names.py`, `rules_toolchain.md`).

**The earlier recipe study** (`RECIPE_PROPOSAL_refined.md`, `RECIPE_REDESIGN_REVIEW.md`, `RECIPE_PROPOSAL_answers.md`, `RECIPE_PROPOSAL_dialog_walkthrough.md`; `RECIPE_STUDY_REVISED.md` was never written):
- **KEPT:**
  - a definition comes before its use;
  - a derived table reads ONE table, as a node with one parent (D-0517 "yes we need the `from:`");
  - its flags:
    - an audit step at a shared table changes every result that reads it (now D-0555, PATHS G17);
    - joins read tier 1 while `from:` would read the last stage, and this must stay her decision;
    - J14 must count a derived table as a reader;
    - result ids must be unique.
- **CHANGED:**
  - "the result's tier 3 written by the audit only" becomes one place among others on a path, under her rule (D-0553);
  - the default ticks of D-0508 become her defaults D-0549 and D-0550 under D-0553;
  - "result: plot | table" stays a direction, not decided (D-0487);
  - form 3 stays a candidate (D-0496).
- **DROPPED:**
  - the tick lists of the dialog walk-through, which rest on the old place list (D-0558);
  - "one place per tree", which D-0553 replaced.

---

## (e) The effect on Q1 to Q7 of `PATHS_AND_DERIVED_AGREED.md`, and what she may be missing

- **Q1 (a parent reused).** A look-up table read by several joins is a shared parent that can never take a removal by entity [RR5]. A join between analyses multiplies rows, so a removal at one side leaves the other side's rows with empty columns [RR5].
- **Q2 ("each T1 coming from the parent").** Unchanged by these runs.
- **Q3 (the recipe form).** Only today's form and the reimport form run today. "One trunk", a declared default and `from:` each need a change of the format, and the first also of the engine [RR8].
- **Q4 (the default place).** Under pattern 2, the join place (her default, D-0549) is the only place on the data side that removes the entity without a false zero [RR4].
- **Q5 ("Remove from all the data").** It needs the entity id declared on every table that holds it; 2 shipped recipes declare none [RR1].
- **Q6 (saying before Apply).** The structure can show "a side of a left join followed by a fill of zeros". Whether the app says "the entity would show a zero" is hers.
- **Q7.** The entity key becomes `is_entity_id` (D-0562); whether it is required (old Q8) is still hers.

**What she may be missing (argued):**
1. **The false zero.** A removal at the data side of pattern 2 does not remove the entity: it shows the entity with 0 [RR4]. The result changes in meaning, silently.
   - Why: the left join keeps the metadata's row, and the fill writes 0.
   - What she would see: the entity in the plot, with zero genes.
   - Alternatives: write the step at the join place; or the app shows the structure (Q6); or the recipe joins a table of the analysed entities so that a missing entity stays missing.
2. **A zero is not "nothing found".** s4 (analysed) and s5 (not analysed) both show 0 [RR4]. This is a recipe practice to document.
3. **The check is not run by the engine** [RR6]. A rule "enforced by the check" holds at HOME's opening and in BLUEPRINT only.
4. **Undeclared recipes.** In 2 shipped recipes, an entity join looks the same as a look-up join [RR1]. A system for joins needs the declaration (A2).
5. **A look-up table with a duplicated key multiplies rows silently** [RR5]. Today nothing checks it.

---

## (f) The run register
`RUN_REGISTER_opus_recipes.md`: RR1 to RR8, each written before the run, with its result and AGREES or CONTRADICTS. Outputs: `opus3_catalogue.out`, `opus3_recipes.out`, `opus3_rr8.out`, `opus3_rr8_codes.out`; scratch recipes under `opus3_out/recipes/`.
