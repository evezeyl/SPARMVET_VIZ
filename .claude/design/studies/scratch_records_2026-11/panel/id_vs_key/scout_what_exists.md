Read-only survey of SPARMVET_VIZ (branch dev). Nothing changed. Facts are "verified (read)" at file:line, or "not found". Reasoned counts are marked. tmp.md was not read.

1. RECIPE FORMAT
- Field today: is_entity_key: true on an input_fields entry. Not a primary-key, id_column, role or sample_id field.
  - .claude/design/recipe_format_spec.md:374 "is_entity_key | true when the column identifies the entity (it repeats in long tables)".
  - recipe_format_spec.md:342-344 entity: {noun, plural, population}; population = table id; "Without entity the software says 'entities' and never guesses from column names. [DECIDED, 5a-17]".
- Rename: is_primary_key -> is_entity_key. recipe_format_spec.md:105 (DEC13); libs/utils/src/utils/recipe_spec.yaml:79; libs/utils/src/utils/recipe_migration.py:40. assets/scripts/migrate_recipe_format.py:3 names is_primary_key but not the target.
- role: libs/utils/src/utils/strict_form_migration.py:187 "role removed (nothing reads it; the key of a table is is_entity_key)".
- Rules file .claude/rules/rules_data_analysis_recipe_structure.md:214 "sample_id MUST be type: categorical". Conflicts with D-0067 (String or Categorical).
- Appendix docs/appendix/data_analysis_recipe_structure.yaml:11 lists is_entity_key.
- Checker libs/utils/src/utils/recipe_check.py: entity() 246-262 (E01; E02 at 261-262 when population table has no is_entity_key field); FD03 at 386 (is_primary_key reported as renamed; severity not read); FD05 at 408-409. Spec rule X6 (recipe_format_spec.md:580) not found in recipe_check.py.
- Shipped recipes (config/data_analysis_recipes): is_entity_key on 22 lines in 20 files (templates e_coli, simple_template, audit, complex_template x2; retest x4; stress_test_master x1; pipelines/1_test_data_ST22_dummy/input_fields x10). is_primary_key: 1 file, pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml:5 (sample_id typed numeric). No is_entity_key in demo_abromics, 2_test_data_ST22_dummy, figshare_integration, 1_Abromics_general_pipeline, 3_test_no_joins (not found).

2. CODE THAT DECIDES THE SAMPLE ID OR KEY
- join_keys.py: decides no sample id; reads on / left_on / right_on / by as given (93-97, 140-151).
- HOME primary keys: app/modules/session_manager.py:119-149 extract_primary_keys = union of on/left_on/right_on of all joins (join-key method, not a declared field). Used at app/handlers/home_theater.py:1248-1282; app/handlers/filter_and_audit_handlers.py:659, 667-682, 726, 741; app/modules/audit_stack.py:431; session_manager.py:59, 69, 96-97; home_theater.py:2147; orchestrator_helpers.py:43 comment.
- Display only: app/modules/wrangle_studio.py:1327 (is_entity_key marker).
- Attrition / sample counts: not found in app/handlers or app/modules (non-test). t3_audit_engine.py: no match for primary_key, entity, sample_id, is_entity_key; unique() at 147-149 reads distinct values only.
- libs/id_reconciliation/src/id_reconciliation/core.py:23, 126: takes two key columns as arguments; no hard-coded id name.
- libs/test_lab: bootstrapper.py:122-123 and scaffolder.py:156-157 hard-code ("id","sample_id","isolate_id") -> is_entity_key (name guess). "Candidate PK" = 100%-unique column, comment only (bootstrapper.py:124-126, 137; scaffolder.py:158-159, 167). aqua_synthesizer.py:447 fallback "id".
- app/handlers/test_lab_handlers.py:422-424: user-typed join key, default "sample_id".
- assets/scripts/create_data_analysis_recipe.py:102-124: key = first --primary_key_data column found (user argument).
- Export (app/handlers/export_handlers.py): no match for primary_key, entity, sample_id, is_entity_key (not found).
- Worktree .claude/worktrees/data-ids/app/tests/test_recipe_data_one_set_of_ids.py: id_column_of 77-87 = first is_entity_key field, else field named sample_id (hard-coded, line 85). tables_of 96-108. COMMON_SET_TABLE line 40 = {"figshare_integration": "fg_metadata"}; default metadata_schema (183). UNIQUE_BY 53-62 hand-typed per (recipe, table), e.g. ("demo_abromics","MLST"): ("sample_id","Scheme"). ALLOWED_OUTSIDE 43-50 (complex_template genomics ACC0029, ACC0030). Exists only in the worktree.

3. SHIPPED RECIPES, JOIN KEYS
- Join key not sample_id: ST22_Anchor_wrangling.yaml:32-33 (left_on VF_gene / right_on Gene_name, inner); AR1_MLST_Serotype_Virulence.yaml:22-23 (same); ResFinder_Abromics_wrangling.yaml:29-30 (drug_name / phenotype_name; header line 4 says included by no shipped recipe).
- Different sample-id names in one recipe: complex_template genomics_input.yaml:1-2 ("Accession") vs metadata_input.yaml:1-2 ("ID"), both sample_id; master_steps.yaml:4 joins on sample_id. stress_test_master Stress_Source_input_fields.yaml:1-2 (id) renamed to sample_id by Stress_Source_wrangling.yaml:2-4; no join found there.
- Multi-column join: not found (all join key lists have one column). Multi-column lists are polars_unpivot, not joins: Summary_wrangling.yaml:12; Quast_Metadata_wrangling.yaml:8; Summary_phenotype_length_fragmentation_assembly.yaml:33.
- Other joins: 28 join steps on [sample_id] (reasoned count by grep).

4. DECISIONS (ledger .claude/knowledge/decision_ledger.md; all DECIDED, taken by EVE)
- D-0082 line 111 "Keys are declared in the recipe" (2026-11-15).
- D-0065 line 94 one pure join-key rule (built).
- D-0067 line 96 "samples id must be either string or categorical" (2026-11-15).
- D-0044 line 73 join keeps declared types.
- D-0029 line 58 entity: declaration (2026-11-12).
- D-0167 line 196; D-0168 line 197 (no silent loss; rows without sample id removed with warning).
- D-0197 line 226 ids of a step are those of the view where selected.
- D-0205 line 234 (2026-11-17) same set of ids across all datasets; D-0206 line 235.
- Design/ADR: architecture_decisions.md:5105-5107 ADR-099 point 6 "[confirm]" Keys are declared, not guessed; :5061 key is information, not mechanism. home_audit_steps.md:39-40, 154-157, 160, 492. .claude/design/home_evidence/home_attrition_report_2026-11-12.md:3 DECIDED 2026-11-12; :16 counts entities by key where the node has it.
- Exact phrase "count by sample id": not found.

5. OPEN TASKS (.claude/tasks/tasks.md)
- ENTITY-DECL-1 line 168 [ ]; HOME-EXPLORE-2 line 74 [ ] (key from joins and is_primary_key); RECIPE-DOCS-1 line 180 [ ]; KEYS-NODE-1 line 78 [ ] (node keys, not declaration).
- Possibly stale: line 236 (N1, decided by D-0065); line 241 (TEMPLATE-KEY-TYPE-1, closed by D-0067 at line 296).
- Line 239 N5 [ ]; line 361 N7-4 [ ] (removal by property).
- DATA-IDS / D-0205 work: not found in tasks.md.

NOT CHECKED: tmp.md; ADR-100/104/105 full text; full bodies of filter_and_audit_handlers.py and blueprint_arch; the extractor.py beyond line 55; whether data-ids is pushed or merged; FD03 severity; whether pk_candidates is used anywhere; TEST-SHAPES-1 in tasks.md.
