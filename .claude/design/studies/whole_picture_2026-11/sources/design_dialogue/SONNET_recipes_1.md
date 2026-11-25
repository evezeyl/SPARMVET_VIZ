# SONNET position 1 on how to build the recipes from the directed-graph model (step 2 of D-0554; her decision D-0562)

Written blind (the Opus file of this topic is not read). Register: `RUN_REGISTER_sonnet_recipes.md` (every run has its three points and its observed result; all runs AGREE with what was expected unless said).
Tags: [HER WORDS D-n] / [RECIPE FILE] / [MY GRAPH SCRIPT] / [ENGINE RUN script, output] / [CHECKER verdict] / [CODE READ file:line] / [REASONED, not run]. The checker (`check_recipe`) is used only to report which code refuses a form; no conclusion rests on its graph. Every table was rebuilt from scratch in its own empty folder; no lineage code is used.
Scratch world (written by `paths2/sonnet_world.py`, `world2.py`; recipes in `paths2/recipes_world/`): entities e1 to e7; `QUAL` (one row per entity), `RES` (observations: several rows per entity; the entity id is NOT unique), `LK` (a look-up by gene, no entity id), `metadata_schema` (7 entities, two without observation), `RES_N` (a second table on the file of `RES`, grouped by entity). Joins: `QM` = QUAL + metadata; `AM1` = RES left, metadata right; `AM2` = metadata left, `RES_N` right, zeros filled; `AM3` = metadata left, `RES` right, then a group by the entity id inside the join; `LKJ`, `LKI` = RES + LK by gene, left and inner. One plot on each (`pq`, `pa1`, `pa2`, `pa3`, `pl`, `pli`). Graph [MY GRAPH SCRIPT]: QUAL -> QM; RES -> AM1, AM3, LKJ, LKI; RES_N -> AM2; metadata -> QM, AM1, AM2, AM3; LK -> LKJ, LKI; each join -> its plot.

---

## (a) THE CONSTRUCTION RULES

| # | Rule: what the author writes | Status today | What breaks for the audit when it is not followed | Basis |
|---|---|---|---|---|
| R1 | Each table in its block: `data_schemas` (results of analysis for the entities), `metadata_schema` (the metadata, one table, reserved id), `additional_datasets_schemas` (look-up tables used in later joins) [HER WORDS D-0512, D-0513] | The shape of each block is checked; the MEANING of a block is documentation (a metadata table written as an ordinary schema gives no code) | The "join with the metadata" and the default place cannot be recognised from the recipe; nothing else breaks (the graph does not read the block) | [CHECKER: the metadata as an ordinary schema: no code] [MY GRAPH SCRIPT: graph built without the block] |
| R2 | The entity id (D-0562: `is_entity_id`, one name for all cases): the column that refers to the entity, in every table that has it. Unique in its table = a key; not unique = a reference to the entity, the column used for the join. Declared in every table that takes part in a removal by the entity id, and in the table named by `entity.population` | `entity.population` must name a table with the flag: E02; a number type is refused: E03; NOTHING checks uniqueness. The demo declares the flag in 10 schemas, among them `ResFinder`, whose id is not unique (70 rows, 42 entities) | No break in the graph or the places. Without the declaration there is nothing to write "remove from all the data" at (the old option is not offered) and the engine refuses a removal at a table that has no such column (`T1:LK`: "column 'sample_id' is not in the table") | [CHECKER: E02, E03] [CODE READ `recipe_check.py:341-348, 440-458`] [ENGINE RUN world.out] [ENGINE RUN catalogue.out] |
| R3 | Every join step is in tier 1, and a join reads original tables only | ENFORCED for every join: ST05 (a join in tier 2), J04 (a join of a join); the engine also fails on both | A join in tier 2 or of a join would make the places and the tree different (graph no longer a tree below an original) | [CHECKER: ST05, J04] [ENGINE RUN world.out: "polars_join needs the resolved right table"; "names 'QM', which is not a data schema"] [CODE READ `recipe_check.py:714-715, 867`] |
| R4 | The side of the metadata in the join. Pattern 1, a result per observation: data left, metadata right. Pattern 2, a result per entity that needs zeros: the metadata left, the observations aggregated to the entity grain (a second table on the same file, or a group by the entity id after the join) | NO check on the side; the grain is only asked as advice in the description (S04, J03) | The place of a step matters. Pattern 1 (`AM1`: 9 rows, e2 has 3, each with its country): a step at the data table or at the join removes e2; a step at the metadata leaves e2's 3 rows with the country empty. Pattern 2 (`AM2`, `AM3`: 7 rows, e6 and e7 with count 0): a step at the data table does NOT remove e2: the row stays with count 0 (`AM3`: 3 -> 0); a step at the join or at the metadata removes it. For `AM2` the separate table `RES_N` is not reached by a step at `RES` at all | [ENGINE RUN world.out; world2.full] [CHECKER: no code] |
| R5 | The tiers as shared steps: write a step at the tier where it is common to every result below | Nothing to write; a tier 2 that no plot reads is refused (S07, J14) | A step written at the wrong tier shares or isolates results wrongly; the audit places follow the tiers | [HER WORDS D-0539] [CHECKER: S07] [MY GRAPH SCRIPT] |
| R6 | A result is a plot today; a result that is a table has no form yet | The checker refuses unknown keys (J01, T03) | The audit has no place for a table result except its tier | [HER WORDS D-0485, D-0487] [CHECKER: `derived_tables` T03, `from:` J01] |
| R7 | The audit block `audit_steps` is written by the app after each tier, only in an audit recipe | Enforced: `audit_steps` in an ordinary recipe is refused (AU01) | The original steps would be changed | [HER WORDS D-0541] [CHECKER: AU01] |
| R8 | One source table for each use of a file when a parent must feed one graph only (her reimport rule) | Allowed; nothing enforced; the engine runs it | Without it, a step at the table reaches every graph below it; with it, graphs separate (`RES_N` is not reached by a step at `RES`) | [HER WORDS D-0556] [ENGINE RUN world.out] |
| R9 | A look-up join by a column that is not the entity id is written `left` unless the author wants it to remove rows | NO check | An `inner` look-up join removes rows and can remove an entity without any step: in the world `LKI` has 5 rows against 9 and loses e4 (all its genes are missing in the look-up table); on the demo the inner join with the APEC list in `ST22_Anchor` removes 1114 of 1731 rows (64 %) and no entity (42 in both) | [ENGINE RUN world.out; L.out] |

**Her quality case on the world** (remove e2 from every analysis but `pq`) [ENGINE RUN world2.full]:
- the roots `T1:RES`, `T1:RES_N` (valid): e2 leaves `pa1`, `pl`, `pli` and STAYS in `pa2` and `pa3` with count 0;
- the five join places (siblings, valid): e2 leaves all five; `pq` keeps it;
- `T1:RES` with `T1:AM3`: not valid in one step (`AM3` reads `RES`); as two steps it gives the join-place result.
So for a result per entity with zeros, the default place cannot be the original's first place; it is the join (or the entity-grain table). [REASONED from the runs]

---

## (b) JOINS THAT ARE NOT METADATA (D-0562)

**Catalogue by my script** [MY GRAPH SCRIPT + ENGINE RUN catalogue.out]. Shipped recipes that load: 50; 33 join steps; 26 on the entity id (all `left`), 7 not on it (5 `inner`, 2 `left`); the classification reads the declared flags: a recipe that does not declare the id is counted as look-up. Demo: 16 joins, 21 join steps; 19 `left` on `sample_id` (15 with the metadata, 4 between analysis tables); 2 look-up joins, both `inner` by gene with `APEC_STEC_virulence_genes` (`ST22_Anchor` step 5, `AR1_MLST_Serotype_Virulence` step 3). The right side is unique on its key in 13 of the 19 entity-join steps; in the other 6 the right table is `ResFinder` or `VirulenceFinder`, which repeat the entity id, and rows multiply (1731 rows from 42 in `QA_fanout_exhibit`). Every joined table still holds `sample_id`. No join in the demo is a join between analyses (a join reads originals only).

**Three kinds, and a step by the entity id below each** [ENGINE RUN world.out]:
| Kind | Example | A step by the entity id at... |
|---|---|---|
| Entity join (the key is the entity id on both sides): metadata, or another analysis table | `QM` = QUAL + metadata | the base table: the row leaves; the other side: the row stays with that side's columns empty (a join place removes it) |
| Look-up join (the key is not the entity id; the right table has no entity id) | `LKJ`, `LKI` (RES + LK by gene) | `RES` or the join: rows leave; `LK`: not writable (the engine refuses: no entity id column); inner: rows and possibly entities vanish without any step |
| Join between analyses | none today | not possible (J04) |

**Options for "a system".**
- **S1, nothing new to write.** The kind is read from the entity-id flags: a join step is an entity join when both sides carry the flag on the key columns, else a look-up join. The data check (not the recipe check) reports, as information, what it measured: key unique on the look-up side (many-to-one), the entity id kept in the result, rows multiplied, entities lost by an inner look-up join. The author sees an information line per join; the user of the audit sees "this join can remove entities by itself" on an inner look-up join.
- **S2, the author declares the purpose** in the join step (a new key such as `kind: lookup`). The author writes one word per join; the check can then refuse an entity-join key that is not flagged. New key.
- **S3, documentation only**: the three kinds and the advice "write a look-up join `left` unless you want it to remove rows".
- **Her question 27, look-up joins after tier 1.** Today ST05 refuses every join outside tier 1 and the engine cannot run one in tier 2 (tier 2 receives the table, not the ingredients) [CODE READ `orchestrator.py` `_materialize_tier2`; ENGINE RUN]. Allowing it needs an engine change. Nothing run or found requires it: a look-up join before an aggregation can be written in tier 1 (the order of steps is the author's). The graph would not change (a tier-2 join would read the ingredients' tier 1 as a tier-1 join does) [REASONED].
- **Neither: say what you meant.**
**Lean (a lean):** S1 with information at the data check, keep look-up joins in tier 1 (ST05 unchanged), and the advice of S3. Reason: it needs no new key and it shows the one real risk found (an inner look-up join removes rows and can remove an entity). [REASONED; runs W2, L]

---

## (c) THE RECIPE FORM

Each form was tried on the world [ENGINE RUN world.out; CHECKER verdicts]:
| Form | Small complete example | Engine / checker | Graph | What the user of the audit sees for her quality case |
|---|---|---|---|---|
| Today's form | the world itself | runs; checker: no error (the scratch paths give PA01 five times, outside the project; ignore) | a tree below each original; joins have several parents | one valid step with the five join places removes e2 from five analyses and keeps `pq` |
| "One trunk" (a join of a join, `QM2` = `QM` + `RES`) | the world plus `QM2` | J04 refuses ("not a schema of this recipe"); the engine fails: "names 'QM', which is not a data schema" | would be a chain `QUAL` -> `QM` -> `QM2` | not runnable today; needs J04 and the engine's ingredient rule changed (D-0344) |
| A default place declared by the author | `default_place: T1:AM1` in a join | refused as an unknown key (J01) | unchanged | a default shown from the declaration; a new key and its check (the place must lie in that original's tree) |
| Her reimport rule | `RES_N` is a second table on the file of `RES` | runs | `RES` and `RES_N` are separate roots | a step at `RES` does not reach `AM2`; a step at `RES_N` reaches only `AM2` |
| Derived tables with `from:` | `derived_tables: {X: {from: QM}}`, or `from:` in a join | refused: T03 (top-level key) and J01 | no form to draw | not drawable; the check and the engine would both have to change (her form 3 is not confirmed, D-0496) |
Needs under "today's form": nothing new for the rule. The per-entity pattern is written today with a second table on the file (`AM2`, a reimport) or by a group by after the join (`AM3`, one graph). [ENGINE RUN]

---

## (d) WHAT THE DEMO WOULD NEED (candidates only; the demo is not changed; a scratch copy was used for run L)

| Candidate change of `1_test_data_ST22_dummy` | Required by | Under which options |
|---|---|---|
| `is_entity_key` becomes `is_entity_id` in the 10 `input_fields` files that declare it (and nowhere else in the demo) | D-0562 (decided) | EVERY option |
| `VirulenceFinder` moves from `additional_datasets_schemas` to `data_schemas`; the label of the QA group and the plot `ui_title` (D-0525 list) | D-0523 (decided) | EVERY option |
| An `entity` block (noun, plural, population) | only if a declared entity is required (old Q8 (b) or (c)); the demo has none, and only 1 shipped recipe has one | only under some options |
| The 4 joins with the metadata first (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`) rewritten data-left | only if "the metadata is the right table" is a RULE (old Q7 (a)); it would also refuse the legitimate zeros pattern (`AM2`, `AM3`) and change the row sets (REASONED); under an advice or documentation: no change | only under some |
| The two inner look-up joins (`ST22_Anchor` step 5, `AR1` step 3) `how: inner` to `left` plus a filter | only if the look-up advice of S3 becomes a refusal; on the data no entity is lost | only under some |
| 16 more source tables (FastP 2, Quast 3, Bracken 1, ResFinder 4, MLST 2, VirulenceFinder 2, APEC 1, Summary_quality 1) and, for the metadata, 12 more; one file per name in a deployment that finds files by table name | her reimport rule as a refusal or a followed advice | only under some |
| 7 tables rewritten and a join that reads a join, or derived tables | "one trunk" | only under some |
| One declared default key in each of the 12 originals | the declared default | only under some |
**The one dry run (D-0525)** would list, for each file: the file and the line, the old key and the new, the rule and the decision that require it, and the places no decision covers (the 4 joins with the metadata first, the 2 inner look-up joins, the grain not stated in descriptions S04/J03); nothing is written. [REASONED]

---

## (e) THE EFFECT ON THE OPEN QUESTIONS OF `PATHS_AND_DERIVED_AGREED.md`, AND WHAT SHE MAY BE MISSING

- **Q1 (a parent reused).** The zeros pattern needs a second table on the file (or a group by after the join): her reimport rule is already how that result is written today (`AM2`); `AM3` shows a way with one graph. [ENGINE RUN]
- **Q3 (the recipe form).** The table of (c). The rule works on today's form.
- **Q4 (the default).** For a per-entity result the first place of the original is not a removal place (the row stays); the default is the join or the entity-grain table, which supports "where the original and the metadata are joined". [ENGINE RUN world2.full]
- **Q5 ("remove from all").** The roots leave e2 in the zeros analyses (2 of 5); the 11 first places include the metadata, which removes it; the join places do. [ENGINE RUN]
- **Q6 ("can remain").** The rows that stay are exactly where the metadata (or another table) is the first table; the coverage per incoming path says it as structure. [MY GRAPH SCRIPT]
- **Q7, the side of the metadata.** "The metadata is the right table" as a RULE would forbid the zeros pattern. It fits as an advice for results per observation. [REASONED, with W1]
- **What she may be missing.** (1) A table's grain (one row per entity, per observation, per gene) decides the place; the checker already asks for it only as advice (S04, J03). (2) The uniqueness of an entity id is checked nowhere; with `is_entity_id` the data check could report "unique" or "repeated" so that she and the user see whether a step removes one row or all lines. (3) An inner look-up join can remove an entity with no audit step (world: e4); the demo does not. (4) A table without the entity id cannot receive a removal (3 places refused in the demo run). (5) An entity that has metadata and no observation exists only if the metadata is the first table (e6, e7).
