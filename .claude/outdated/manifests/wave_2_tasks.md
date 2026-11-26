# Wave 2: the task list `.claude/tasks/tasks.md` (manifest, 2026-11-26)

Order: the owner's, channel block M704 (one source of truth; what is old moves out of the live files) and M710 (her rule for the tasks wave). Plan: `tmpAI/status/SOURCE_OF_TRUTH_CLEANUP_PLAN_2026-11-26.md` (main tree, not in git). Written before any change of `tasks.md`; the changes follow in later commits of the branch `task/outdated-wave-tasks`.

## The rule of this wave

Her rule (ledger `D-0676`, block M710): a task that is not done and still actual stays; a task that is stale but deferred may stay; a task whose design changed is removed; a task that is done is moved to the task archive (the existing archive files); a task that is wrong or superseded is removed.

- "Removed" means removed from `tasks.md`; git keeps the history; this manifest lists each removed task with its verdict and evidence, so that nothing disappears without a trace.
- The rule at the top of `tasks.md` says: done tasks move to a file in `archives/` with a pointer at the bottom; superseded tasks move to `outdated/` with the reason. The coordinator's words (later, M710) say superseded tasks are removed and listed here and that no new file with the full blocks is made. DIFFERENCE reported: the top rule says superseded tasks go to `outdated/`; this wave follows the later words (removed, listed here). The existing folder `.claude/tasks/outdated/` is left where it is (it holds old plan, test and rename files, not tasks; its README says so).
- A done task moves to the archive file of its unit (`tasks_archive_home_audit.md`, `tasks_archive_backlog.md`, `tasks_archive_decisions_2026_11_15.md`, `tasks_archive_tasks_2026_11_16.md`, `tasks_archive_tasks_2026_11_17.md`), whole, text unchanged, under a dated heading; pointers at the bottom of `tasks.md` already list those files.
- A task that is open and waits for the owner gets one plain line "Waits for: ..." if it lacks one. A task I cannot judge stays with a line "Verdict needed: ...".
- Nothing is decided here that is not in the ledger: where a verdict rests on a decided line, the line is cited; where it rests on the code, the file and line or the commit is cited.

## How the verdicts were made

1. A script listed every task block of `tasks.md` (an open `- [ ]` or a ticked `- [x]` at the start of a line, with its indented lines): 499 open, 90 ticked, 589 in all. The 90 ticked are DONE by their own tick.
2. Ten read-only reviewer agents, one batch of about 40 KB of task text each, gave one verdict per open task with its evidence (file and line, commit, ledger number). The reviewers read code and ledger and ran no test suite.
3. I re-checked a sample of the A (done) verdicts against the branch (commits are ancestors of HEAD, files and symbols exist) and corrected what failed: **979** (BLUEPRINT-DUPLICATE-PLOT-ID-SHOWN-WRONG: the BLUEPRINT part is on branch `task/blueprint-duplicate-id`, which is not on `dev`: now D, stays), **992** (REVIEWS-D0534-TO-REDO: its commits `349d1474` and `fdc6380f` are not on `dev`, and the task says no merge before the reviews are redone: now F, stays), **621** (DEMO-BRANCH-PLAN-1: only the plan page is done, the branch is cut later: now F, stays). I downgraded to G (stays, verdict needed) three B verdicts that rested on a reading the reviewer did not complete: **470** AUDIT-RULES (six questions unread), **858** AUDIT-FOLDER-WARNING-AND-DOCS (she may still want the warning file), **1012** LINEAGE-UNFOLLOWED-JOIN-WARNING (she may still want the red lines in the lineage panel).
4. The owner's extra rule of M710 (D-0675: the place model replaces D-0316, D-0359, D-0451) makes **935** AUDIT-DEFAULT-TICKS-REVIEW and **936** AUDIT-DIALOG-TABLE-NO-PLOT-READS, and **1009** LINEAGE-UNREAD-TABLES-ARE-LINES, B. What is left of 935 and 936 is carried by the slice tasks (see the table).

5. CORRECTIONS after the check of the branch (2026-11-26, the coordinator's list; each is one line; the tables below show the corrected verdict, marked CORRECTED): restored to `tasks.md`: S2-3 (D-0088 stands), RECIPE-OVERVIEW-2, EXPORT-RECIPE-REFUSE-1 (all three now E, waits for the owner); un-archived with done and missing lines: AUDIT-VIEW-1, RECIPE-RULE-ONE-NAME-ONE-MEANING, AUDIT-SAVE-RULE-TEXT-1, ENTITY-DECL-1, FILTER-PICKERS-1, FILTER-CONTROLS-TYPE; APPLY-REASON-FALLBACK is not restored (one line in AUDIT-OLD-SCOPE-REMOVE-1 carries it, evidence `audit_stack.py:175, 210, 253-254, 540, 666-667`); UML-CHECK is folded into UML-TASKS (two lines); UML-STALE-TEST-TAG-1 is archived as done (audit_uml_model.py finds no discrepancy; the model does not contain the test name).
6. STAGE2-SPEC-1 point 7 ("if the recipe steps become dictionaries, refuse duplicate keys in the loader") is MOOT and stays removed: in recipe format 1 the steps of a tier are a list (`.claude/design/recipe_format_spec.md` section 5), and the loader already refuses a repeated key of any mapping: `libs/utils/src/utils/strict_yaml.py:17-36` (`DuplicateKeyError`, check T10), used by `libs/utils/src/utils/recipe_loader.py:28`, tested in `libs/utils/tests/test_strict_yaml.py`. No new task.
7. Two different tasks share the id N7-4: the one at line 351 was REMOVED as superseded (verdict B: remove from all the data is now a choice of places, D-0499, D-0531, D-0662); the one at line 387 was ARCHIVED as done (verdict A: the library step `libs/utils/src/utils/remove_from_all.py`; the screen is tracked by AUDIT-REMOVE-FROM-ALL-DATA).
8. The ledger line D-0151 is a RELAYED line (not hers); the rule it points at is D-0088 (DECIDED). A FACT note in the ledger says the task list was corrected on this point.

## Totals

| Verdict | Meaning | Count (open tasks before) | Count after the wave |
|---|---|---|---|
| A | DONE (moved to the archive) | 62 | 0 |
| B | SUPERSEDED (removed) | 28 | 0 |
| C | DUPLICATE (removed or the better one stays) | 17 | 1 |
| D | OPEN, actionable | 110 | 110 |
| E | OPEN, waits for the owner | 146 | 146 |
| F | OPEN, deferred or held | 108 | 108 |
| G | CANNOT JUDGE (stays) | 28 | 28 |
| total | | 499 | 393 |

Open tasks at the start: 499. Moved to the archive as done: 62 (verdict A) and the 90 ticked tasks. Removed as superseded: 28. Removed as duplicates: 16. Open at the end: 393 (before the seven new tasks added the same evening, REMOVED-APPLIED-STEP-NOT-SAVED, DATA-PATHS-FULL-IN-EXPORT-AND-SESSION, RECIPE-SWITCH-AUDIT-RECIPE, AUDIT-STEPS-SURVIVE-RECIPE-CHANGE, BUNDLE-IMPORT-RELOAD-MESSAGE, WHOLE-PICTURE-SOURCES-MOVE-TO-OUTDATED and LINEAGE-SCOPE-STUDY-MOVE-TO-OUTDATED, which make it 400; the new top block is not a task).

## The tasks, by section of `tasks.md`

Columns: task id, the line in `tasks.md` before the wave, verdict, evidence, what happens to it. A = DONE, B = SUPERSEDED, C = DUPLICATE, D = actionable, E = waits for the owner, F = deferred or held, G = cannot judge.

### 1. HOME audit build (stage 2)

Verdicts: A 13, B 5, C 1, D 7, E 3, F 7, G 7 (43 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| TEST-ADAPT-1 | 33 | G | inventory file home_test_inventory_2026-11-13.md; app/tests/test_filter_defects.py:4 strict xfails; no commit names the id | stays; Verdict needed line added |
| TEST-SHAPES-1 | 37 | C | RECIPE-TESTS-1 (line 154) says "Includes TEST-SHAPES-1" | removed from tasks.md, merged into RECIPE-TESTS-1 |
| PLOT-TABLE-ORDER-1 | 44 | A | merge 4f299025; app/tests/test_step_order.py:629 "Was an xfail" | archived (moved to the done archive of its unit) |
| SEED-HOLDS-1 | 45 | A | merge 653e70b1; app/modules/plot_seeds.py; app/tests/test_shiny_seed_places.py | archived (moved to the done archive of its unit) |
| ROW-ORDER-1 | 47 | A | merge be08b169; libs/transformer/src/transformer/actions/min_items.py:29 modif_join_where | archived (moved to the done archive of its unit) |
| CATEGORICAL-LIST-1 | 48 | E | D-0057 makes both types usable; steps 1 to 3 not in git log | stays; Waits for line added |
| ORPHAN-FRAGMENT-1 | 54 | A | merge d6a2822a (RECIPES-SMALL-1) converted the fragment; app/tests/test_resfinder_abromics_fragment.py:9 | archived (moved to the done archive of its unit) |
| VIZ-STANDARD-1 | 56 | D | V2, V4, V9, V10 remain; V1, V3, V5 to V8 merged (c442af4c) | stays |
| PY-RECIPE-1 | 61 | F | task says idea only, no build | stays |
| FILTER-DTYPES-1 | 63 | A | merge a386422a (FILTER-PICKERS-1); app/modules/t3_audit_engine.py typed values (ADR-104 point 7); 46425c89 | archived (moved to the done archive of its unit) |
| RECIPE-GRAPH-UTILS-1 | 68 | G | libs/utils/src/utils/recipe_graph.py exists; b9d9b325 slice A1 | stays; Verdict needed line added |
| HOME-EXPLORE-2 | 69 | B | key extraction replaced by the entity key (D-0034, D-0313); libs/utils/src/utils/join_keys.py, key_drop.py exist | removed from tasks.md (history in git) |
| KEYS-NODE-1 | 73 | G | app/modules/cache_keys.py:292-305 tier1_key and tier2_key | stays; Verdict needed line added |
| STAGE2-SPEC-1 | 77 | B | stage-2 spec of 2026-11-13 replaced by the places model (D-0662, D-0672) | removed from tasks.md (history in git) |
| AUDIT-VIEW-1 | 78 | D | CORRECTED (was A, archived): restored with done and missing lines; done: the audit copy is the source of truth (app/modules/audit_view.py; audit_copy.py:270); missing: the re-base after a change of the original (S2-3) and the badg | stays |
| HOME-EXPLORE-4 | 82 | B | D-0311, D-0505, D-0506: the filter belongs to the viewed table; built | removed from tasks.md (history in git) |
| HOME-EXPLORE-5 | 83 | G | test_filter_operators.py, test_step_order.py exist | stays; Verdict needed line added |
| HOME-EXPLORE-6 | 84 | G | - | stays; Verdict needed line added |
| AUDIT-USABILITY-1 | 88 | F | depends on the dialog that D-0672 reworks; demo priority | stays |
| AUDIT-REPLACE-1 | 89 | B | places model (D-0662, D-0665, D-0672) replaces the per-plot stack, pop-up and Apply; contract: __places__ | removed from tasks.md (history in git) |
| FILTER-PICKERS-1 | 91 | E | CORRECTED (was A, archived): restored; the eight provisional choices still wait for her; the text on time and duration columns is corrected to what ops_for_column offers today (t3_audit_engine.py:330-357) | stays; Waits for line added |
| TIME-NANOSECONDS-DRAW-1 | 102 | G | t3_audit_engine.py:220 handles nanoseconds in filter values | stays; Verdict needed line added |
| HOME-DESIGN-REVIEW-1 | 106 | G | almost all decided | stays; Verdict needed line added |
| ACTION-MUST-ACT-1 | 110 | A | polars_calls.py:35 imports step_problems; data_wrangler.py:26; no xfail left in test_actions_must_act.py | archived (moved to the done archive of its unit) |
| ACTION-POLARS-1 | 114 | A | D-0036, D-0035; rules_agent_role_bioscientist.md lists 68 prefixed actions | archived (moved to the done archive of its unit) |
| MISSING-VIZ-FILTERS-1 | 115 | A | task says MEASURED; NA rule superseded by D-0035 (DEC29) | archived (moved to the done archive of its unit) |
| INT-TYPE-1 | 117 | B | D-0035 (DEC27), D-0057: Polars type names, categorical refused | removed from tasks.md (history in git) |
| FORMULA-SAFETY-1 | 118 | A | fe856c26; libs/utils/src/utils/formula_check.py; libs/utils/tests/test_formula_check.py (follow-ups a, b, c to be re-filed) | archived (moved to the done archive of its unit) |
| BLUEPRINT-AFTER-RECIPE-1 | 120 | F | register only; BLUEPRINT held | stays |
| SPEC-CLEAN-1 | 121 | A | commit 5e49015a; .claude/design/recipe_format_spec.md | archived (moved to the done archive of its unit) |
| BLUEPRINT-CHECK-RECIPE-1 | 122 | F | Fix Format removal done; later Check recipe is BLUEPRINT, held | stays |
| MODIF-FILTER-VERIFY-1 | 123 | A | commit c39c9cab | archived (moved to the done archive of its unit) |
| SECURITY-RECIPE-1 | 124 | D | eval, path, include parts done (test_formula_check.py, test_include_confinement.py, test_recipe_paths.py); zip import, report.qmd cells, YAML aliases, regex remain | stays |
| DOCS-SECURITY-1 | 125 | D | decided 2026-11-15 (M86, ADR-071); no build found | stays |
| SECURITY-REVIEW-END-1 | 126 | F | for the end of the app, not now | stays |
| GATE-GAP-1 | 127 | A | merge c46cd11b | archived (moved to the done archive of its unit) |
| EQUALITY-CHECK-1 | 128 | D | step 1 merged 3eb954fc; steps 2 and 3 open | stays |
| JOIN-COUNTS-1 | 129 | D | join_diagnosis.py explains a refused validate only; no rows in and out counts | stays |
| RECIPE-SCIENCE-1 | 130 | E | no ledger line found | stays; Waits for line added |
| HOME-EXPLORE-8 | 134 | A | libs/viz_factory/src/viz_factory/viz_factory.py:218 and :278 (_unknown_plot_defaults_keys); refusal not run | archived (moved to the done archive of its unit) |
| HOME-EXPLORE-10 | 135 | D | join_diagnosis.py has no many-to-many warning; needs her OK for libs/transformer | stays |
| UML-HOME-REDRAW-1 | 141 | F | UML edits need her OK (D-0012); after the audit; to retitle against the 2026-11-26 state | stays |
| DOC-RECIPE-PLACEMENT-1 | 142 | F | rule files need her double confirmation; after demo | stays |

### 2. Recipe format (the recipe session; parent issue #73; package P2)

Verdicts: A 8, B 2, C 1, D 4, E 1, G 2 (18 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| RECIPE-SPEC-1 | 152 | A | .claude/design/recipe_format_spec.md exists, cleaned in 5e49015a | archived (moved to the done archive of its unit) |
| RECIPE-FORMAT-VERSION-1 | 153 | A | libs/utils/src/utils/recipe_check.py:245-253 V01 to V04; assets/scripts/migrate_recipe_format.py | archived (moved to the done archive of its unit) |
| RECIPE-TESTS-1 | 154 | D | app/tests/test_every_recipe_follows_the_spec.py exists; per-rule tests of catalogue section 11 not counted; absorbs TEST-SHAPES-1 | stays |
| RECIPE-ORDER-IDS-1 | 155 | G | recipe_loader.py:88 T10; strict_yaml.py exists | stays; Verdict needed line added |
| RECIPE-REGISTRY-1 | 156 | G | #87 done per the task | stays; Verdict needed line added |
| RECIPE-STEP-PROBLEMS-1 | 157 | A | libs/utils/src/utils/ui_schema.py:216 step_problems; polars_calls.py:35; data_wrangler.py:26 | archived (moved to the done archive of its unit) |
| RECIPE-TYPES-1 | 158 | B | the task says superseded by DEC27 = D-0035, D-0057 | removed from tasks.md (history in git) |
| RECIPE-FORMULAS-1 | 159 | A | libs/utils/src/utils/formula_check.py; test_formula_check.py | archived (moved to the done archive of its unit) |
| UNKNOWN-KEYS-1 | 160 | A | recipe_check.py:180,235,337,395,437,845 (unknown_keys; T03, E01, S01, S05, J01); D-0033 | archived (moved to the done archive of its unit) |
| ENTITY-DECL-1 | 161 | D | CORRECTED (was A, archived): restored; done: recipe_check.py:330-337 (E01); missing: the BLUEPRINT form part (held) and the docs appendix (no entry for the key entity: in docs/) | stays |
| RECIPE-DATASET-TIER2-1 | 162 | A | commits ef63bc27 (J14), 533a0880, c141934c; recipe_check.py:361,419-420 S07; app/tests/test_schema_tier2.py | archived (moved to the done archive of its unit) |
| RECIPE-FORMAT-1 | 163 | A | libs/utils/src/utils/engine_keys_migration.py; recipe_migration.py:40; D-0033, D-0034, D-0024 | archived (moved to the done archive of its unit) |
| RECIPE-MIGRATE-1 | 167 | A | app/tests/test_every_recipe_follows_the_spec.py:40-42 (exceptions empty); D-0638 | archived (moved to the done archive of its unit) |
| RECIPE-ST22-FIX-1 | 168 | D | R1 not done: config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:14 still joins ResFinder | stays |
| UTILS-REUSE-REVIEW-1 | 172 | E | the task says when Eve wants it | stays; Waits for line added |
| RECIPE-DOCS-1 | 173 | D | docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd:204-205 still has dataset_id; rule-file part waits for her double confirmation | stays |
| RECIPE-AUDIT-REFRESH-1 | 179 | C | same subject as AUDITS-REACTIVATE-1; D-0467 | removed from tasks.md, merged into AUDITS-REACTIVATE-1 |
| RESULT-CHANGES-1 | 181 | B | task says DROPPED 2026-11-15, replaced by EQUALITY-CHECK-1 | removed from tasks.md (history in git) |

### 3. Configuration stage (last, after the build)

Verdicts: C 1, E 1, F 6 (8 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| CONFIG-REVIEW-1 | 189 | F | stage 5, after the build; pipeline-exploration-simple.yaml still exists | stays |
| HOME-GATING-DECIDE-1 | 190 | F | PAUSED, stage 5, by its own text | stays |
| CONFIG-PIPELINE-RENAME-1 | 191 | C | renames of the pipeline-* names are in CONFIG-REVIEW-1; the name question moves there | removed from tasks.md, merged into CONFIG-REVIEW-1 |
| CONFIG-APP-RESOURCES-1 | 192 | F | configuration stage, design first | stays |
| CONFIG-CACHE-LOCATION-1 | 193 | E | config/deployment/local/local.yaml:24 still has cache | stays; Waits for line added |
| CONFIG-STEPS-WRITE-1 | 194 | F | Blueprint writes the step lists; BLUEPRINT held | stays |
| CONFIG-IRIDA-CHECK-1 | 195 | F | IRIDA connector not built | stays |
| AUDITS-REACTIVATE-1 | 197 | F | schedule_commands.md banner (paused); D-0467 after HOME and Gallery; absorbs RECIPE-AUDIT-REFRESH-1 | stays |

### 4. Backlog (older than 2026-11-11; triaged 2026-11-13, not yet reviewed by Eve)

Verdicts: A 1, C 2, D 3, E 9, F 15 (30 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| IMPORT-UX-1 | 220 | E | the task says not decided | stays; Waits for line added |
| DOC-JOIN-CAST-1 | 230 | E | docs part done | stays; Waits for line added |
| TEMPLATE-KEY-TYPE-1 | 231 | E | D-0225 refuses a number type on an entity id | stays; Waits for line added |
| RECIPE-WORD-1 | 233 | E | D-0085, D-0069 | stays; Waits for line added |
| FILTER-UNIFY-1 | 236 | A | libs/utils/src/utils/filter_values.py imported at viz_factory.py:17,264, modified.py, t3_audit_engine.py | archived (moved to the done archive of its unit) |
| AUDIT-REPAIR-1 | 237 | E | decision N6 open | stays; Waits for line added |
| UNDO-WIRE-1 | 243 | F | Blueprint only; blueprint_handlers.py:210,342 | stays |
| PIPELINE-WARNING-SURFACE-1 | 244 | D | PipelineError(severity="warning") still at viz_factory.py:291,305,430 and ingestor.py:80 | stays |
| TEST-INGESTION-1 | 245 | D | its condition (loader rebuilt) is met | stays |
| BP-STALE-VIEW-1 | 247 | F | Blueprint; the A/B/C choice is hers | stays |
| EXPORT-CHECK-1 | 248 | E | export rebuilt since | stays; Waits for line added |
| DOCKER-RELEASE-1 | 252 | F | assets/containers/Dockerfile:79 still has libs/generator_utils; she said not urgent; absorbs CONTAINER-RECIPE-BROKEN | stays |
| SECURITY-DEPLOY-1 | 253 | F | before official deployment | stays |
| DEPS-REVIEW-1 | 254 | F | deferred by her, 2026-11-05 | stays |
| 23-C | 255 | F | Galaxy wrappers, deployment | stays |
| 23-D | 256 | F | IRIDA, deployment | stays |
| 23-E | 257 | F | quick-start guides, deployment | stays |
| RESEARCH-LIMS-1 | 258 | F | awaiting the LIMS project | stays |
| BLUEPRINT-AGENT-API-1 | 259 | F | agent_adapter.py:399 still degrades claude_api; Blueprint | stays |
| HELP-FROM-DOCS-1 | 263 | F | later (Eve 2026-11-07) | stays |
| DOC-TIER-PROSE-REFRESH-1 | 264 | D | the rebuild it waits for is done; D-0660 | stays |
| CODE-DOCS-RETROSPECTIVE | 265 | F | pre-deployment sprint not started | stays |
| DEMO-USERS-1 | 266 | F | after the build; config names change in stage 5 | stays |
| UML-HOME-AUDIT-TAGS | 268 | C | belongs with UML-HOME-REDRAW-1; D-0639, D-0640, D-0661 | removed from tasks.md, merged into UML-HOME-REDRAW-1 |
| UML-C4-GALLERY-LAYOUT | 269 | F | Gallery, layout only | stays |
| CONTAINER-RECIPE-BROKEN | 270 | C | same Dockerfile problem (Dockerfile:79) | removed from tasks.md, merged into DOCKER-RELEASE-1 |
| TESTLAB-PYPROJECT-UTILS | 271 | F | Test Lab left alone (D-0637); the owner writes pyproject.toml | stays |
| DATA-IMPORT-SILENT-FACTS | 274 | E | task says waits for the owner | stays; Waits for line added |
| CONNECT-TEMPLATE-DATA-LOOKUP | 275 | E | task says waits for the owner | stays; Waits for line added |
| TOOLS-UML-0 | 276 | E | licence not bought | stays; Waits for line added |

### 5. Eve's decisions of 2026-11-15 (recorded by the coordinator, 2026-11-15 09:42; channel M87 to M90 from sparmvet-viz-57)

Verdicts: E 1, F 15 (16 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| UML-FAQ-DIAGRAMS-1 | 304 | F | waits for the UML redraw | stays |
| UML-NAVIGATOR-1 | 305 | F | done with the UML redraw; D-0639 | stays |
| UML-DOCS-1 | 307 | F | after the UML redraw and the licence | stays |
| REPO-CLEAN-1 | 308 | E | a history rewrite with a force push | stays; Waits for line added |
| MAP-A-BOUNDARY-ASSET-1 | 321 | F | assets/geo_boundaries/ does not exist; maps are Gallery work | stays |
| MAP-A-DATA-ANALYSIS-RECIPE-PATTERN-1 | 324 | F | maps | stays |
| MAP-A-GALLERY-1 | 326 | F | Gallery plus an open taxonomy choice | stays |
| MAP-A-DOCS-1 | 327 | F | maps | stays |
| VIZ-GEOM-MAP-1 | 328 | F | deferred architecture choice | stays |
| GALLERY-MAP | 329 | F | deferred | stays |
| GALLERY-FLOW | 330 | F | deferred | stays |
| RESEARCH-HELP-1 | 331 | F | Gallery keyword search | stays |
| EXPORT-TUBEMAP | 332 | F | Blueprint tube map | stays |
| UX-GALLEXP-1 | 333 | F | Gallery, functionality TBD | stays |
| UX-PLOTSTYLE-1 | 334 | F | marked deferred; Plot Style panel not mounted (to review when the colour pop-up is removed, D-0665) | stays |
| UX-CSS-DEMO | 335 | F | condition default theme final not met | stays |

### 6. Eve's decisions of 2026-11-15, afternoon (recorded by the coordinator, 2026-11-15 18:45; channel M94, M95, M97, M100 from sparmvet-viz-57)

Verdicts: A 2, B 2, D 8, G 1 (13 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| PIPELINE-RECIPES-1 | 346 | D | decided 2026-11-15 (N5, M94); D-0172 | stays |
| SELF-JOIN-1-ADDENDUM | 347 | D | D-0078; no self-join check found in recipe_check.py | stays |
| WARNINGS-LOOK-1 | 348 | D | decided yes to all (M94); no ledger number found | stays |
| AUDIT-HISTORY-LOG-1 | 349 | B | D-0083 made the log optional; D-0478 and D-0673 replace that (always, every export) | removed from tasks.md (history in git) |
| RECIPE-OVERVIEW-1 | 350 | D | D-0084, D-0085; no recipe_overview found in app/ | stays |
| N7-4 | 351 | B | remove from all the data is now the user's choice of places: D-0499, D-0531, D-0662 (the screen is tracked by AUDIT-REMOVE-FROM-ALL-DATA) | removed from tasks.md (history in git) |
| FRAGMENTS-1 | 352 | D | decided 2026-11-15 (N8); old output-fields list not checked | stays |
| RESFINDER-PIECE-1 | 353 | D | D-0111, D-0112, D-0113; no ResFinder tier file found | stays |
| OLD-WORDS-LIST-1 | 354 | D | decided N12, D-0069 | stays |
| VIZ-NIGHT-QUEUE | 355 | G | ledger has only "M97 V1-V10 stand" | stays; Verdict needed line added |
| HOME-STATE-PER-RECIPE-1 | 357 | A | ui_implementation_contract.md section 13 (a change of recipe clears them, ADR-099 point 1); _clear_filters_on_view_change filter_and_audit_handlers.py:19 | archived (moved to the done archive of its unit) |
| SCRIPT-DUMPERS-1 | 358 | D | assets/scripts/debug_bootstrap_viz_yamls.py:176 plain yaml.dump; migrate_plot_specs.py:60,238 | stays |
| GOLDEN-BROKEN-RECIPE-1 | 359 | A | assets/scripts/golden_baseline.py:8,45-46,87-94; --check exits 1 (line 209) | archived (moved to the done archive of its unit) |

### 7. Eve's decisions of 2026-11-15, evening (channel blocks M101 to M118 and M119 to M129 of the review session)

Verdicts: A 12, B 2, C 4, D 12, E 12, F 2, G 4 (48 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| V1-B | 371 | D | D-0091, D-0210, D-0218; no plotnine_ registrations exist (grep); rules_viz_factory.md 1a "DECIDED, not built" | stays |
| V1-B-AUDIT | 372 | D | D-0210, D-0212, D-0213; nothing built; first step | stays |
| V1-B-RENAME | 373 | E | D-0091; starts only after the impact list | stays; Waits for line added |
| TYPED-VALUE-FORM-1 | 374 | F | D-0277; built with and after the rename (V1-B-RENAME) | stays |
| N28 | 375 | E | D-0218 says not decided how arguments are passed | stays; Waits for line added |
| CLEAN-SAVED-1 | 378 | D | M105 decided; no commit found; a builder should check whether it was done with D-0312 | stays |
| S2-5 | 379 | E | depends on CLEAN-SAVED-1 | stays; Waits for line added |
| S2-2 | 383 | C | same subject as READING-ERRORS-1 (443) | removed from tasks.md, merged into READING-ERRORS-1 |
| S2-3 | 384 | E | CORRECTED (was B, removed): restored; D-0088 DECIDED (the export is refused until a re-base; a broken step blocks it) and D-0151 (RELAYED, the rule is D-0088) are not superseded by D-0662, D-0672 or D-0675, and no kept task, page  | stays; Waits for line added |
| S2-3-Q | 385 | D | investigation only; no decision needed | stays |
| S2-4 | 386 | B | build order of the old stage-2 packages; audit rebuilt as places (D-0535, D-0662, D-0672) | removed from tasks.md (history in git) |
| N7-4 | 387 | A | libs/utils/src/utils/remove_from_all.py exists; contract: DECIDED, built as a library step (D-0499, D-0531); the screen is tracked by AUDIT-REMOVE-FROM-ALL-DATA | archived (moved to the done archive of its unit) |
| N7-2 | 388 | B | the history log is replaced by D-0673 and D-0478; D-0315 | removed from tasks.md (history in git) |
| AUDIT-ADVICE | 389 | D | M112 decided; advice text for the dialog, help and docs still wanted (the flow changes under D-0672) | stays |
| AUDIT-WARN | 390 | E | the fourth point is open | stays; Waits for line added |
| AUDIT-ERROR-Q | 391 | E | options go to her | stays; Waits for line added |
| RECIPE-OVERVIEW-2 | 394 | E | CORRECTED (was B, removed): restored; her wishes recorded in the task (one ordered list of recipe steps and audit steps, different colours, the insertion point visible, an accordion per table with counts and a check line) are not  | stays; Waits for line added |
| PY-RESEARCH | 397 | F | start only after the visualisation library is done | stays |
| CATEG-1 | 400 | A | merge 78c620bf (CATEGORICAL-MIGRATION-1); D-0098, D-0057 | archived (moved to the done archive of its unit) |
| STANDARD-POLARS-TYPES | 401 | A | D-0057; rules_data_analysis_recipe_structure.md section 9 | archived (moved to the done archive of its unit) |
| JOIN-WHERE-RENAME | 402 | A | libs/transformer/src/transformer/actions/min_items.py:29; polars_time_joins.py:16 | archived (moved to the done archive of its unit) |
| EMPTY-REFUSE | 403 | A | min_items.py (lines 30-31) refuses empty select, unpivot on, top_k by, bottom_k by | archived (moved to the done archive of its unit) |
| TIES-INFORM | 404 | A | libs/transformer/src/transformer/actions/polars_rows.py:64 | archived (moved to the done archive of its unit) |
| ADVICE-TEXT | 405 | A | 806dc852; polars_rows.py:64-75 | archived (moved to the done archive of its unit) |
| SUM-64 | 406 | A | libs/transformer/tests/test_sum_32_bit.py; 806dc852 | archived (moved to the done archive of its unit) |
| AUDIT-RAWYAML-REMOVE-1 | 409 | A | commit 8bf8a8fc; app/modules/renamed_keys.py:237 refuses it | archived (moved to the done archive of its unit) |
| AUDIT-RECIPE-RULE | 410 | A | app/tests/test_audit_recipe_runs_alone.py; contract section 7.2 rules 8 and 10; D-0535 | archived (moved to the done archive of its unit) |
| TWO-RECIPES | 411 | D | decided M125; the check waits for UML-CHECK; the build exists (contract 7.2 rule 10) | stays |
| UML-CHECK | 412 | C | CORRECTED (was B): folded into UML-TASKS for real: (1) the check of the audit diagrams after the place model (D-0012), (2) the paragraph Original recipe and audit recipe; both are lines of UML-TASKS now | removed from tasks.md, merged into UML-TASKS |
| DOC-CONTROL-STOPPED | 415 | G | - | stays; Verdict needed line added |
| RULE-PATHS-R1 | 416 | C | kept as the better written; absorbs RULE-LINKS-R1 | stays |
| AGENT-PROBE-1 | 422 | E | BLUEPRINT agent, also held | stays; Waits for line added |
| GATE-NOTICE-TESTS-1 | 423 | D | no test fails under the mutation always announce (test_recipe_gate_handlers.py:89-92) | stays |
| RULE-LINKS-R1 | 424 | C | same subject as RULE-PATHS-R1 (416) | removed from tasks.md, merged into RULE-PATHS-R1 |
| FILTER-CONTROLS-TYPE | 429 | E | CORRECTED (was A, archived): restored with FILTER-PICKERS-1 (the same eight choices) | stays; Waits for line added |
| EXPORT-RECIPE-REFUSE-1 | 432 | E | CORRECTED (was B, removed): restored; the refusal is built and PROVISIONAL (contract 7.2 rules 8 and 10), she has not confirmed it | stays; Waits for line added |
| TWO-RECIPE-NAMES-1 | 433 | D | decided 2026-11-15; the ADR texts wait for her | stays |
| SEED-POOL-TIMEOUT-1 | 434 | D | grep timeout in libs/viz_factory/tests/test_reproducible_render.py found nothing | stays |
| SEED-GATE-TEXT-1 | 435 | G | grep Tip: finds only tests | stays; Verdict needed line added |
| AUDIT-MESSAGES-PLAIN-1 | 436 | D | renamed_keys.py:235 still holds internal step type names | stays |
| PATTERN-DETECTOR-SHIM-1 | 437 | E | pattern_detector.py still exists | stays; Waits for line added |
| VIZ-DEFECTS-1 | 438 | G | - | stays; Verdict needed line added |
| DOCS-DATA-TYPES-1 | 439 | D | docs/appendix/data_types_philosophy.qmd not opened | stays |
| PLOT-TEXT-RUNS-CODE-1 | 440 | A | commit cfe1dc22 (ancestor of HEAD); libs/viz_factory/src/viz_factory/checked_plot.py:42 | archived (moved to the done archive of its unit) |
| REPORT-TEXT-RUNS-CODE-1 | 441 | D | no commit found; decision of 2026-11-13 applies | stays |
| FACET-NAME-WITH-SPACE-1 | 442 | G | - | stays; Verdict needed line added |
| READING-ERRORS-1 | 443 | E | Appendix A AP19 to AP21; absorbs S2-2 | stays; Waits for line added |
| TEST-STAGING-1 | 444 | A | app/tests/gate_stage.py:3,30 staged copy under tmpAI/gate_stage | archived (moved to the done archive of its unit) |

### 8. Tasks from 2026-11-16 (verification, decisions D-0143 to D-0193)

Verdicts: A 6, B 1, C 1, D 13, E 23, F 7, G 1 (52 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| CHECK-ON-SELECT | 452 | E | D-0184, D-0185 | stays; Waits for line added |
| EXPORT-MODES | 453 | E | D-0187 to D-0193; D-0292 removed the scope choice | stays; Waits for line added |
| EXPORT-PANEL-RESET-1 | 454 | A | c743cce3 (D-0288, D-0291, D-0296); app/tests/test_export_box_survives_plot_tab.py | archived (moved to the done archive of its unit) |
| FILTER-STALE-COLUMN-1 | 455 | D | no commit found; no decision needed | stays |
| FILTER-RESET-ON-STAGE | 456 | A | D-0311, D-0361, D-0505, D-0506 built per contract section 2 (_clear_filters_on_view_change, view_key) | archived (moved to the done archive of its unit) |
| JOIN-ROW-COUNTS | 458 | D | D-0168, D-0050 decided; not built | stays |
| BP-COMMENTS-1 | 459 | F | BLUEPRINT held (D-0174; a new library needs her yes) | stays |
| MISSING-COLUMN-MESSAGE-1 | 460 | D | D-0176 decided; not built | stays |
| LABELS-IN-EXPORT | 461 | B | label replaced by ui_label everywhere including the export (D-0253, D-0409) | removed from tasks.md (history in git) |
| RULE-EDITS-15 | 463 | E | D-0172, D-0173 | stays; Waits for line added |
| HOOK-SIMPLER | 464 | E | a question, not a decision | stays; Waits for line added |
| SESSIONS-MANY-DATASETS | 465 | E | D-0186, D-0191 | stays; Waits for line added |
| VIEWPOINTS-O13-O14 | 466 | E | - | stays; Waits for line added |
| UML-TASKS | 467 | D | D-0012; part may be outdated by the places model; absorbs UML-CHECK | stays |
| CHANNEL-CLEAN | 468 | D | rules_agent_channel.md section 3 | stays |
| REPO-AUDIT | 469 | F | last, after the rest; she decides first | stays |
| AUDIT-RULES | 470 | G | reviewer judged B but did not read the six questions | stays; Verdict needed line added |
| AUDIT-DIALOG-PREVIEWS | 471 | E | - | stays; Waits for line added |
| AUDIT-HELP-TEXT | 472 | E | - | stays; Waits for line added |
| TYPED-VALUES-1 | 473 | A | D-0202; contract section 8 value type rule (ADR-104 point 7); utils.filter_values.filter_condition | archived (moved to the done archive of its unit) |
| ENGINE-T3-READER | 474 | A | rules_data_engine.md Tier 3: DataOrchestrator.materialize_tier3() reads a plot's own tier3 steps (D-0343) | archived (moved to the done archive of its unit) |
| DATA-CHECK-ONE-ROW | 475 | E | waits for Eve | stays; Waits for line added |
| DATA-IMPORT-OVERWRITE | 477 | F | D-0434, D-0438, D-0440 decided; needs the named places of the deployment specification (not met); its old waits text is out of date | stays |
| HOME-DATA-IMPORT-MESSAGES-WORDS | 480 | E | proposals in tmpAI/panel/data_import_words/TABLE_FOR_THE_OWNER.md | stays; Waits for line added |
| HOME-DATA-IMPORT-HANDLER-TEST | 481 | D | no commit found; a test for a failing later replace | stays |
| TOMBSTONE-METADATAVALIDATOR | 483 | F | tombstone expires in Phase 38; project_conventions.md:260 still there | stays |
| OLD-WORDS-AUDIT | 484 | E | audit_old_words.py --check still fails | stays; Waits for line added |
| HELP-OLD-AUDIT-TEXT | 485 | D | docs/user_guide/audit_pipeline.qmd:45 and :118 still describe the propagation modal; narrow to those lines | stays |
| CHECKER-AUDIT-STEP-AT-END | 486 | E | D-0535 | stays; Waits for line added |
| AUDIT-PANEL-UNTESTED | 489 | D | not verified whether a test clicks the delete icon; D-0672 may have removed Revert | stays |
| EXPORT-REPORT-FIGURE-LINKS | 490 | E | bundle layout is her choice | stays; Waits for line added |
| EXPORT-ANCHOR-FOLDERS | 491 | E | waits for Eve | stays; Waits for line added |
| SAFE-INPUT-DEFAULTS | 492 | E | waits for Eve | stays; Waits for line added |
| APPLY-REASON-FALLBACK | 493 | C | CORRECTED (was B): the fallback kept_reasons is still in app/handlers/audit_stack.py (:175, :210, :253-254, :540, :666-667); not restored as its own task; one line in AUDIT-OLD-SCOPE-REMOVE-1 says it goes with the old Apply and th | removed from tasks.md, merged into AUDIT-OLD-SCOPE-REMOVE-1 |
| EXPORT-PROVENANCE-SILENT | 494 | D | export_handlers.py:92-154 not opened | stays |
| DELETE-ALL-HALF-DELETED | 495 | D | not verified | stays |
| GATE-NOTICE-IN-EFFECT | 496 | D | recipe_gate_handlers.py:186 area read; low | stays |
| EXP-MODES-DIAGRAM | 497 | E | related to EXPORT-MODES | stays; Waits for line added |
| IMPORT-OLD-BUNDLE-MESSAGE-1 | 499 | F | part of V1-B-RENAME | stays |
| IMPORT-REVIEW-1 | 500 | F | LATER by her words | stays |
| MIGRATION-SCRIPTS-LATER-1 | 501 | F | LATER, for the planning of production | stays |
| ID-TEST-REFERENCE-TABLES-1 | 502 | E | D-0222; D-0610 | stays; Waits for line added |
| ENTITY-DECL-SHIPPED-1 | 503 | E | D-0029, D-0082 decide part | stays; Waits for line added |
| JOIN-GROWTH-CAUTION-1 | 504 | E | task says not decided | stays; Waits for line added |
| ST22-DUPLICATE-ROWS-1 | 505 | E | task says not decided | stays; Waits for line added |
| VIZ-OWN-22-1 | 506 | D | D-0211, D-0212; no register_plot_component("plotnine_ in code; rules_viz_factory.md 1a not built | stays |
| VIZ-PARITY-30-1 | 507 | D | D-0212; no plotnine_ registrations found | stays |
| PLOT-DEFAULTS-DEAD-KEYS-1 | 510 | A | D-0242, D-0236; PD02 tombstone at libs/utils/src/utils/recipe_check.py:1293 | archived (moved to the done archive of its unit) |
| VIZ-NOT-ADDABLE-15-1 | 511 | E | - | stays; Waits for line added |
| ENGINES-PLAN-1 | 519 | A | engine_python_polars.py, engine_python_plotnine.py; ENGINE_CACHE_VERSION "6" at app/modules/cache_keys.py:81; D-0236 to D-0240 | archived (moved to the done archive of its unit) |
| CONTACT-BLANK-HOME-1 | 520 | E | task says waits for Eve | stays; Waits for line added |
| STALE-RECORDS-1 | 521 | E | ADR text needs her yes | stays; Waits for line added |

### 9. Tasks from 2026-11-17 (records of 18:40; coordinator's list; tags marked [records] were not given by the brief)

Verdicts: A 10, B 10, C 4, D 26, E 46, F 31, G 4 (131 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| FORMULA-ALLOWLIST-DESERIALIZE-1 | 529 | A | libs/utils/src/utils/formula_check.py:15-18; branch gone | archived (moved to the done archive of its unit) |
| WORKTREE-TEST-IMPORTS-1 | 530 | G | - | stays; Verdict needed line added |
| VIZ-SEED-DICT-POSITION-1 | 531 | E | - | stays; Waits for line added |
| VIZ-PICTURE-EQUALITY-TEST-1 | 532 | E | - | stays; Waits for line added |
| SECURITY-FINDINGS-2026-11-17 | 533 | E | D-0282, D-0281 cover two items | stays; Waits for line added |
| SILENT-DEFAULTS-2026-11-17 | 539 | C | umbrella; D-0278 points 1 to 5 are split into SEED-STAT-SUMMARY-1, MEAN-SE-WARNING-DOCS-1, LEGEND-PAIRING-CHECK-1, FORMULA-REFUSE-SHUFFLE-SAMPLE-1, QUANTILE-WARNING-DOCS-1 | removed from tasks.md, merged into the five split tasks |
| ENGINE-FIELDS-PLAN-1 | 540 | B | D-0236 Format 1 amended, no format 2, answers its first question | removed from tasks.md (history in git) |
| ENGINE-PLOT-HANDOFF-1 | 541 | A | app/handlers/export_handlers.py:1370 passes **plot_engine_slot | archived (moved to the done archive of its unit) |
| PLOT-ENTRY-KEYS-LOST-1 | 542 | G | config_loader moved to libs/utils/src/utils/config_loader.py | stays; Verdict needed line added |
| BLUEPRINT-PLOT-DEFAULTS-FORM-1 | 543 | F | BLUEPRINT held; BP-FORM-FIX covers the same form | stays |
| CONTACT-AUTHOR-MANIFEST-1 | 544 | E | D-0227 | stays; Waits for line added |
| LOOKUP-TABLE-1 | 545 | E | D-0222 | stays; Waits for line added |
| SAMPLE-ID-FOLLOWUPS-ASK-EVE | 546 | E | no build | stays; Waits for line added |
| AUDIT-PLAN-FORMAT-1 | 548 | E | not checked | stays; Waits for line added |
| FONT-EXAMPLE-1 | 554 | D | D-0241; no font library in Dockerfile or pyproject | stays |
| THEME-BUILDER-PROPOSAL-1 | 556 | F | after the demo, D-0271; Blueprint | stays |
| SEED-STAT-SUMMARY-1 | 560 | D | D-0278 point 1, D-0279 point 1; viz_factory.py:86 _refuse_unseeded_layer; summary layer not covered | stays |
| MEAN-SE-WARNING-DOCS-1 | 561 | D | D-0278 point 2; no mean_se rule in recipe_check.py | stays |
| MODIF-MEAN-SE-DESIGN-1 | 562 | E | no build before her yes | stays; Waits for line added |
| LEGEND-PAIRING-CHECK-1 | 563 | D | D-0278 point 3 | stays |
| FORMULA-REFUSE-SHUFFLE-SAMPLE-1 | 564 | D | D-0278 point 4, D-0279 point 4 | stays |
| QUANTILE-WARNING-DOCS-1 | 565 | D | D-0278 point 5, D-0279 point 3; no interpolation rule in recipe_check.py | stays |
| ARGS-REFUSE-RC-FNAME-1 | 566 | D | D-0280 point 1 | stays |
| PATH-USE-CASES-STUDY-1 | 567 | E | task says not decided, report only | stays; Waits for line added |
| ARGS-SAFE-SOLUTIONS-LATER-1 | 571 | F | reopen when a recipe needs one; D-0280 point 2 | stays |
| DEFERRED-SHORT-KEYS-1 | 572 | F | if needed; D-0242 option B | stays |
| CONTAINER-RECIPE-UPDATE-1 | 574 | F | D-0263 defers; Dockerfile:32 still python:3.12-slim | stays |
| BLUEPRINT-HELP-STEP-MODIF-1 | 576 | F | D-0266 defers; Blueprint | stays |
| STAT-FUNCTION-POLARS-WAY-LATER-1 | 578 | F | D-0275 | stays |
| USER-FUNCTIONS-EVALUATION-LATER-1 | 580 | F | D-0276 | stays |
| PROPOSAL-NAMED-THEMES-BLUEPRINT | 584 | F | not decided; Blueprint | stays |
| BP-FORM-FIX | 588 | F | D-0271 after the demo; Blueprint held | stays |
| BP-FORM-THEME-FIELDS | 589 | F | same | stays |
| PARK-OBJECT-PANIC-1 | 593 | F | D-0230, parked with a condition | stays |
| ENGINE-KEYS | 602 | A | engine files exist; ENGINE_CACHE_VERSION "6" (cache_keys.py:81); plot_engine_slot (export_handlers.py:1370); branch gone | archived (moved to the done archive of its unit) |
| SESSION-IMPORT-KEY-EXISTS-1 | 610 | E | D-0281, D-0283; size limit built at session_manager.py:739-742 | stays; Waits for line added |
| INCLUDE-PRIVATE-LOADER-1 | 611 | D | D-0282; libs/utils/src/utils/config_loader.py:132 still has yaml.SafeLoader.add_constructor !include | stays |
| LABEL-TRACE-1 | 612 | B | name keys decided by the names pass (D-0407 to D-0412, D-0468 to D-0484) | removed from tasks.md (history in git) |
| HOME-AUDIT-REDESIGN-SLICES-1 | 613 | B | D-0284 built and replaced by D-0662, D-0665, D-0672 | removed from tasks.md (history in git) |
| TEST-SPEED-STUDY-1 | 614 | E | D-0285 (xdist installed); study partial | stays; Waits for line added |
| AGENTS-AT-ONCE-MEASURE-1 | 615 | E | D-0287 | stays; Waits for line added |
| JOIN-KEY-PROTECTION-CHECK-1 | 616 | A | D-0297; libs/utils/src/utils/key_drop.py; contract 12g.3 (merge 8772f368) | archived (moved to the done archive of its unit) |
| EXPORT-BUTTON-READY-1 | 617 | A | D-0270; app/src/www/export_ready.js; app/tests/test_export_ready_script_loaded.py | archived (moved to the done archive of its unit) |
| EXPORT-COLLECTS-WARNINGS-1 | 618 | A | D-0269; export_handlers.py:1335 and :37 (plot_warnings) | archived (moved to the done archive of its unit) |
| FORMULA-D-STUDY-1 | 620 | E | D-0267, report only | stays; Waits for line added |
| DEMO-BRANCH-PLAN-1 | 621 | F | the plan page is done (not in git), but the demo branch is cut only when she says HOME and GALLERY are settled and after the big recipe change (D-0271, D-0272) | stays |
| PLOT-ORDER-MISSING-GROUP-1 | 622 | E | task says waits for her word | stays; Waits for line added |
| STAT-FUNCTION-BLOCK-1 | 623 | D | D-0274, D-0275; libs/utils/tests/test_stat_function_names.py exists; plain refusal not verified | stays |
| DEMO-FORMULAS-SAFE-EVIDENCE-1 | 624 | E | D-0274 point 3 | stays; Waits for line added |
| VALIDATE-OUTSIDE-FOLDER | 629 | D | scripts/audit_data_analysis_recipe_coherence.py:206 still uses relative_to(project_root) | stays |
| BANNER-INTERPRETER-TEXT | 630 | A | app/src/main.py:41 prints sys.executable | archived (moved to the done archive of its unit) |
| FORMULA-FIELD-PLAIN-ERROR | 631 | D | not re-run | stays |
| THEME-LEGEND-ELEMENT-CHECKER | 632 | E | - | stays; Waits for line added |
| BLUEPRINT-RECIPE-LOCATION | 633 | F | BLUEPRINT held | stays |
| TESTLAB-EMPTY-KEY-DEFAULT | 634 | F | Test Lab | stays |
| TESTLAB-REFORMAT-CONVERSION | 635 | F | owner: low priority, plan only; Test Lab | stays |
| RULE-JOIN-KEY-CAST-TEXT | 636 | E | - | stays; Waits for line added |
| SPEC-BEESWARM-TIER3-CLAIM | 637 | B | corrected with the big recipe change (spec: removed, D-0237); check recipe_format_spec.md:459 | removed from tasks.md (history in git) |
| EXPORT-DOWNLOAD-RACE-1 | 638 | C | replaced by EXPORT-BUTTON-READY-1 (D-0270) | removed from tasks.md, merged into EXPORT-BUTTON-READY-1 |
| EXPORT-NO-PLOT-TAB-SILENT-1 | 639 | B | D-0292 removed the scope choice; no export_scope in export_handlers.py | removed from tasks.md (history in git) |
| EXPORT-NO-CONFIRM-1 | 640 | E | to confirm with her | stays; Waits for line added |
| EXPORT-README-AFTER-WRITE-1 | 641 | E | to confirm with her | stays; Waits for line added |
| EXPORT-WORKSPACE-SWITCH-TEST-1 | 642 | D | no behaviour choice; test missing | stays |
| THEME-DOCS-DESCRIPTIONS-1 | 643 | A | libs/viz_factory/src/viz_factory/themes/core.py:266 (D-0258) | archived (moved to the done archive of its unit) |
| THEME-DOC-HOW-TO-ADD-1 | 644 | D | D-0256 points 3 and 5; no How to add a theme in docs | stays |
| FILTER-FORM-COLUMN-SNAPS-BACK-1 | 646 | B | My view gone (D-0179, D-0311); task says the redesign replaces it | removed from tasks.md (history in git) |
| FILTERS-CLEAR-ON-VIEW-CHANGE-1 | 647 | A | D-0311, D-0361; contract section 2 (_clear_filters_on_view_change) | archived (moved to the done archive of its unit) |
| STAT-FUNCTION-NONFINITE-WARN-1 | 649 | F | D-0261; deferred by D-0275 | stays |
| INTERPRETER-ONE-PYTHON-1 | 652 | D | D-0263; task/one-python not merged; python_interpreter in config/deployment/local/retest.yaml:28 | stays |
| ONE-PYTHON-TOMBSTONE-1 | 653 | E | REMOVED_DEPLOYMENT_KEYS at app/modules/renamed_keys.py:25; branch unmerged | stays; Waits for line added |
| WIDE-SPLIT-MODIF-DESIGN-1 | 654 | D | D-0264, D-0265, D-0266; no step_split_wide in code | stays |
| DOCS-STEP-MODIF-1 | 655 | D | D-0266 point 4; starts after the design note is accepted | stays |
| TESTLAB-REVIEW-1 | 659 | F | review done; fixes after the demo (D-0271); Test Lab | stays |
| KEY-WORDING-OPTIONS-1 | 661 | E | no DECIDED line on the wording | stays; Waits for line added |
| JOIN-REPORT-PROPOSAL-1 | 662 | E | PROPOSAL, not decided | stays; Waits for line added |
| EXPORT-MODE-TWO-TICKS-1 | 669 | D | D-0298, D-0301; single checkbox at app/handlers/export_handlers.py:706 | stays |
| UPLOAD-MULTI-FILE-FLOW-CHECK-1 | 670 | D | read-only check, feeds EXPORT-MODE-TWO-TICKS-1 | stays |
| EXPORT-ACTIVE-PLOT-DISABLED-1 | 671 | B | the task says MOOT; D-0292 removes the scope choice | removed from tasks.md (history in git) |
| PATH-BASE-1 | 672 | E | task says waits for Eve (point 4 of the path page) | stays; Waits for line added |
| PATH-CHECK-1 | 673 | E | task says waits for Eve | stays; Waits for line added |
| EXPORT-SOURCE-RECORD-1 | 674 | E | task says waits for Eve (point 7) | stays; Waits for line added |
| FORMULA-BUILD-D-1 | 675 | E | branch trial/formula-d unmerged | stays; Waits for line added |
| FORMULA-RULE-TESTS-1 | 676 | D | no test for MAX_EXPONENT or the underscore rule found; libs/utils/src/utils/formula_check.py | stays |
| ROW-ORDER-PROJECTION-1 | 677 | E | task says waits for Eve (point 9) | stays; Waits for line added |
| JOIN-LABEL-REBUILD-1 | 678 | E | task says waits for Eve | stays; Waits for line added |
| BLUEPRINT-SAVE-COMMENTS-1 | 679 | F | BLUEPRINT held; blueprint_handlers.py:978 | stays |
| GALLERY-LEFTOVERS-1 | 680 | E | rules_app_structure.md:50 still lists exporter.py; _GITHUB_REPO_URL constant at home_theater.py:87 | stays; Waits for line added |
| OTHER-PYTHON-PATHS-1 | 681 | E | D-0263 | stays; Waits for line added |
| EXPORT-SVG-TEXT-AS-SHAPES-1 | 685 | E | task says waits for Eve | stays; Waits for line added |
| EXPORT-PDF-REPORT-PNG-SILENT-1 | 686 | E | export_handlers.py:1313-1319 | stays; Waits for line added |
| EXPORT-SVG-SIZE-CHECK-1 | 687 | D | measurement task | stays |
| EXPORT-MODES-QUESTION-1 | 688 | E | D-0298, D-0301 settled ticks and warning | stays; Waits for line added |
| EXPORT-DOCS-AFTER-SIMPLIFY-1 | 689 | D | docs sync after D-0292 to D-0296; rule and ADR passages wait for her yes | stays |
| UML-STALE-TEST-TAG-1 | 690 | A | CORRECTED (was G): audit_uml_model.py --project-root . prints No discrepancy found; docs/UML/app.mdj contains no test_audited_rows_and_drops_are_exported (grep count 0) | archived (moved to the done archive of its unit) |
| UML-AUDIT-SAME-NAME-TAGS-1 | 691 | D | task says it does not wait; audit script not read | stays |
| AUDIT-SAVE-RULE-TEXT-1 | 692 | E | CORRECTED (was A, archived): restored; done: rules_ui_dashboard.md:15, ui_implementation_contract.md:183, :555; missing: the UML, ADR and docs copies were not checked | stays; Waits for line added |
| CONFIG-REVIEW-1 | 693 | F | its own condition (just before her HOME testing) not met | stays |
| TEST-RUNS-STATE-THEIR-FLAGS-1 | 694 | F | standing rule until CONFIG-REVIEW-1 | stays |
| BLUEPRINT-PLOT-PREVIEW-NOT-MOUNTED-1 | 695 | F | BLUEPRINT held; wrangle_studio.py:721 | stays |
| BLUEPRINT-NODE-CLICK-WRONG-TABLE-1 | 696 | F | BLUEPRINT held (D-0271) | stays |
| LOADER-WRAPPER-UNWRAP-1 | 697 | E | task says waits for Eve | stays; Waits for line added |
| RECIPE-ORPHAN-FILES-1 | 698 | E | experimental/ folder is gone | stays; Waits for line added |
| AUDIT-REDESIGN-SLICE-PLAN-1 | 699 | B | the audit was rebuilt as places (D-0662, D-0665, D-0672) | removed from tasks.md (history in git) |
| BLUEPRINT-REMOVED-BUTTON-AND-HINT-1 | 700 | F | D-0305, D-0307; BLUEPRINT held | stays |
| ONE-PYTHON-RULE-WORDING-1 | 701 | E | task/one-python unmerged | stays; Waits for line added |
| BLUEPRINT-PLOT-RECIPE-BUILDER-STUDY-1 | 702 | F | BLUEPRINT held | stays |
| BLUEPRINT-GLOBAL-PICTURE-1 | 703 | F | BLUEPRINT held | stays |
| TIER3-WORDS-MIXUP-CHECK-1 | 704 | E | recipe_check.py:1200 (P05 retired) | stays; Waits for line added |
| BLUEPRINT-T1-T2-PROOF-1 | 705 | C | the task marks itself superseded | removed from tasks.md, merged into BLUEPRINT-TIER1-TIER2-PROOF-AFTER-HOME-GALLERY |
| TIER3-READER-AND-TEXTS-1 | 706 | B | checker no longer refuses tier 3 (recipe_check.py:1200); materialize_tier3 reads it; D-0343, D-0179 | removed from tasks.md (history in git) |
| BLUEPRINT-TIER-REFUSAL-MESSAGE-1 | 707 | F | BLUEPRINT held; app/modules/blueprint_tier_refusal.py exists | stays |
| FILTER-FORM-LOST-PICK-1 | 717 | E | parked until the audit redesign (now built) | stays; Waits for line added |
| FILTER-OPERATOR-WAIT-1 | 718 | D | test repair, no decision needed | stays |
| FILTER-FORM-RULE-AND-UML-1 | 720 | E | UML check due by D-0012 | stays; Waits for line added |
| FILTERS-TIER-VISION-FOR-REDESIGN | 721 | B | audit and lineage rebuilt (D-0638 to D-0674); D-0179 removed My view | removed from tasks.md (history in git) |
| FINAL-REVIEW-RULE-PASSAGES-1 | 722 | C | option A decided 2026-11-19; engine-keys merged | removed from tasks.md, merged into RULE-SENTENCES-AFTER-RECIPE-CHANGE-1 |
| RULE-SENTENCES-AFTER-RECIPE-CHANGE-1 | 724 | E | merge condition met | stays; Waits for line added |
| INCLUDE-WATCH-LIST-1 | 725 | D | D-0282; bootloader.py:450-491 not re-checked | stays |
| TEST-SMOKE-SKIPS-LIST-1 | 726 | D | list task, no decision needed | stays |
| RULE-SECTION-8-BROWSER-FILES | 727 | E | a rule text change | stays; Waits for line added |
| REVIEW2-OPEN-POINTS-FOR-EVE | 728 | E | no build until Eve says | stays; Waits for line added |
| NEW-MODULES-NOT-IN-RULE-FILE | 729 | E | modules exist | stays; Waits for line added |
| BLUEPRINT-DESIGN-FINDINGS-1 | 730 | F | BLUEPRINT held | stays |
| BLUEPRINT-RECIPES-FOLDER-IGNORES-DEPLOYMENT | 731 | F | blueprint_handlers.py:978; parked with the Blueprint pass | stays |
| BLUEPRINT-TIER1-TIER2-PROOF-AFTER-HOME-GALLERY | 732 | F | decided order: HOME and GALLERY first; absorbs BLUEPRINT-T1-T2-PROOF-1 | stays |
| QUESTIONS-PARKED-UNTIL-REFACTOR-STEP | 733 | E | row (ii) waits for the Blueprint pass | stays; Waits for line added |
| PLOT-PICTURES-STORED-LATER | 736 | F | D-0335, D-0336 consider later; nothing built | stays |
| GRAPH-REFUSES-JOIN-OF-JOINS | 737 | D | D-0344; libs/utils/src/utils/recipe_graph.py:46 | stays |
| DATA-FILE-LINE-ENDINGS-MAIN-CHECKOUT | 752 | G | concerns the main checkout working copy, not git | stays; Verdict needed line added |
| TEXTS-OUT-OF-DATE-AFTER-SLICE-A | 753 | E | plain docs FAQ done in 110866a6 | stays; Waits for line added |
| AUDIT-QUESTIONS-FOR-THE-STOP | 789 | G | many of Q-A1 to Q-A17 probably settled by D-0638 to D-0672 | stays; Verdict needed line added |

### HOME audit redesign, slice B: two modes on screen, Exploration is clean (DONE and controlled 2026-11-20, dev `3bfb0050`)

Verdicts: A 10, B 6, C 3, D 37, E 50, F 25, G 9 (140 open tasks).

| Task id | Line | Verdict | Evidence | What happens |
|---|---|---|---|---|
| SLICE-B-POINTS-FOR-THE-OWNER | 797 | E | D-0365 covers the start values only | stays; Waits for line added |
| TEXTS-OUT-OF-DATE-AFTER-SLICE-B | 798 | E | D-0179 | stays; Waits for line added |
| SPEED-TABLE-BUILD-READS-ALL-SOURCES | 799 | D | D-0326; opening build f14d8f1b related; defect not re-measured | stays |
| COMMENT-KEY-ENTERS-THE-TABLE-KEY | 800 | G | cache_keys.py:25 and audit_copy.py:64 exclude comment for audit steps only | stays; Verdict needed line added |
| AUDIT-FORM-LOW-FINDINGS | 802 | G | - | stays; Verdict needed line added |
| TEXTS-FOLLOW-UP | 803 | D | rules_app_structure.md:50 still lists exporter.py and lacks opening_handlers.py and recipe_gate_handlers.py; ADR items are hers | stays |
| ADRS-FOR-DECISIONS-WITHOUT-ONE | 804 | E | task says it waits for her choice | stays; Waits for line added |
| SESSION-REFUSED-AFTER-RECIPE-EDIT | 805 | D | D-0362; session_handlers.py:602 only warns | stays |
| STUDY-RECIPE-VERSIONS | 806 | E | points c and e open; D-0389 to D-0394 answer the rest | stays; Waits for line added |
| EXPORT-ORIGINAL-RECIPE-ALWAYS | 807 | D | D-0389; not built; check wording against the place-model export | stays |
| RECIPE-NAME-DATE-RULE | 808 | C | same subject as RECIPE-NAME-RULE; D-0390 to D-0393 | removed from tasks.md, merged into RECIPE-NAME-RULE |
| STUDY-RECIPE-PLACES | 809 | G | D-0394, D-0435 fix part of it | stays; Verdict needed line added |
| OPENING-BUILD-VALUES-DECIDED | 810 | A | D-0363 (1,000,000 rows) and D-0365 (Exploration, T3) decided; record note only | archived (moved to the done archive of its unit) |
| LEDGER-HISTORY-TEST-HEADER | 812 | A | D-0380 option A; app/tests/test_decision_ledger.py:251, :314 | archived (moved to the done archive of its unit) |
| OPENING-FOLLOW-UP | 813 | D | app/src/server.py is 294 lines against a limit of about 250; items 1 to 5 not re-checked | stays |
| OPENING-BLOCKS-THE-SERVER | 814 | F | measurement record; background drawing is on her later list (D-0336) | stays |
| KEY-DROP-FOLLOW-UP | 815 | E | item 2 is hers | stays; Waits for line added |
| GALLERY-TWO-NAMES | 836 | C | same 13 mismatches (D-0397) | removed from tasks.md, merged into GALLERY-NAMES-HEADINGS |
| GALLERY-STUDY | 837 | F | D-0388; Gallery | stays |
| GALLERY-NAMES-HEADINGS | 838 | F | D-0397; waits for her reading of the draft; absorbs GALLERY-TWO-NAMES | stays |
| GALLERY-CHART-TYPE-AXIS | 839 | F | D-0398; Gallery | stays |
| GALLERY-TAXONOMY-ONE-SOURCE | 840 | F | D-0399; Gallery | stays |
| GALLERY-PICTURE-REDRAW-AUTOMATION | 843 | F | D-0400; low priority | stays |
| GALLERY-VERIFY-ALL-34 | 844 | E | D-0401 | stays; Waits for line added |
| GALLERY-TAG-CHECKS | 846 | F | D-0402, D-0403; Gallery | stays |
| GALLERY-FILTER-TERM-MEANINGS | 847 | F | D-0404; Gallery | stays |
| HELP-BESIDE-THE-SCREEN-STUDY | 848 | E | study done | stays; Waits for line added |
| GALLERY-TAXONOMY-REVIEW | 849 | E | study done | stays; Waits for line added |
| NAME-FIELDS-PURPOSE-TABLE | 850 | E | D-0405 | stays; Waits for line added |
| RECIPE-DEFAULT-DATA-FALLBACK-TEST | 851 | D | part 1 merged a91139d3 (app/tests/test_recipe_default_data.py); part 2 (D-0426) not built; narrow to part 2 | stays |
| DATA-FILE-CUT-ACCEPTED | 852 | E | no fix before her choice | stays; Waits for line added |
| RECIPE-NAME-RULE | 853 | E | D-0437, D-0440 to D-0442 decided; absorbs RECIPE-NAME-DATE-RULE | stays; Waits for line added |
| WRITE-TEST-AT-START | 856 | E | D-0440, D-0441 | stays; Waits for line added |
| BUNDLE-IMPORT-INTO-USER-PLACES | 857 | F | D-0435 decided; needs the named places of the deployment specification | stays |
| AUDIT-FOLDER-WARNING-AND-DOCS | 858 | G | reviewer judged B; kept until she says | stays; Verdict needed line added |
| WHOLE-PICTURE-DESIGN | 859 | A | DELIVERED (merge 0c41fa28); .claude/design/studies/whole_picture_2026-11/ exists; D-0538 to D-0569 | archived (moved to the done archive of its unit) |
| DEMO-VIRULENCEFINDER-TO-DATA-SCHEMAS | 888 | A | config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:148 under data_schemas; commits 10cc2706, af0080c5 (D-0524, D-0525) | archived (moved to the done archive of its unit) |
| AUDIT-REMOVE-FROM-ALL-DATA | 889 | E | step 1 DONE (merged 9af81573, 882983c6); the screen was built on the old dialog | stays; Waits for line added |
| RECIPE-RULE-ONE-NAME-ONE-MEANING | 897 | E | CORRECTED (was A, archived): restored with done and missing lines; done: docs/user_guide/good_practice_recipes.qmd:31, :37; missing: the recipe-check advice, the BLUEPRINT prompt (D-0500), the proposal she was to see | stays; Waits for line added |
| DATA-CHECK-IDS-WITHOUT-METADATA | 899 | D | D-0568, D-0569; id checks built (merge 1f6cb913; app/modules/id_check_run.py:57); the data-check channel that only informs is missing | stays |
| DOCS-ID-RULES-IN-GUIDELINES | 905 | F | HELD by D-0580, D-0583; the cheat sheet and the static-deployment sentence (D-0585) are missing | stays |
| NAMES-ACROSS-THE-APP-STUDY | 908 | A | names pass merged (b0c64e1b); ui_label everywhere (D-0407 to D-0412); app/handlers/home_theater.py:113-118 | archived (moved to the done archive of its unit) |
| NAMES-UI-LABEL-EVERYWHERE | 909 | A | merge b0c64e1b; recipe_spec.yaml:110,133 ui_title removed; unbuilt remainder (allowed-key lists, D-0412) belongs to DEPLOYMENT-STANDARD (D-0413) | archived (moved to the done archive of its unit) |
| HOME-TABS-DRAWN-TWICE | 910 | F | the task says after the demo build | stays |
| AUDIT-ONE-FAILING-STEP-BREAKS-ALL-PLOTS | 911 | D | PlaceAudit.run_of still builds the whole copy (audit_view.py:51) | stays |
| LINEAGE-MAP-HOME | 912 | A | app/handlers/lineage_handlers.py, app/modules/lineage_view.py, app/tests/test_lineage_view.py; contract says built 2026-11-25 (D-0627, D-0630); leftovers in tasks 917 to 920 and 922 | archived (moved to the done archive of its unit) |
| LINEAGE-OLD-SESSION-META-STEP | 917 | E | D-0632 covers the refusal at the plots only | stays; Waits for line added |
| LINEAGE-STEP-AT-TABLE-NO-PLOT-LISTING | 918 | E | task says waits for the owner | stays; Waits for line added |
| LINEAGE-SMALL-FORM-TYPES | 919 | D | D-0627, D-0630; build only if the small form stays under the step bar (S-bar says not decided) | stays |
| LINEAGE-INCOMPARABLE-PLACES | 920 | E | the contract notes the difference | stays; Waits for line added |
| HOME-MODE-SWITCH-SCROLL | 922 | E | task says the owner's choice | stays; Waits for line added |
| METADATA-NO-JOIN-LISTS-IT | 923 | E | D-0637 NOT decided | stays; Waits for line added |
| AUDIT-OLD-SCOPE-REMOVE-1 | 924 | D | D-0662, D-0663, D-0665, D-0672; the new stored names wait for her word | stays |
| HOME-SLICE-1-TOGGLE-COMPARE | 925 | D | D-0652; in work on task/strip-toggle-compare | stays |
| HOME-SLICE-3A-SHOWN-ITEM | 927 | D | D-0653, D-0654, D-0655 | stays |
| HOME-SLICE-3B-NO-TABS-IN-AUDIT | 928 | D | D-0657; after 3a | stays |
| HOME-SLICE-Q1-EFFECT-ONCE | 929 | D | D-0656, D-0666; in work on task/trial-engine | stays |
| HOME-SLICE-4-CONFIRM-APPLY-FLOW | 930 | D | D-0662, D-0669, D-0670, D-0672 | stays |
| HOME-SLICE-Q2-TRY | 931 | D | D-0662, D-0656, D-0671, D-0672; needs Q1 | stays |
| HOME-SLICE-Q3-MARKS | 932 | D | D-0670, D-0673 | stays |
| HOME-SLICE-S-BAR-STEP-BAR | 933 | D | D-0663, D-0672; last slice | stays |
| AUDIT-LOG-DESIGN-AND-BUILD | 934 | E | already has its waits-for line; D-0673, D-0677, D-0678 | stays |
| AUDIT-DEFAULT-TICKS-REVIEW | 935 | B | D-0675 replaces D-0316, D-0359, D-0451 (the default ticks no longer exist); its lessons (D-0508) are carried by the place model | removed from tasks.md (history in git) |
| AUDIT-DIALOG-TABLE-NO-PLOT-READS | 936 | B | D-0675: a table no plot reads is a place like any other, not a line of the dialog (D-0627, D-0630) | removed from tasks.md (history in git) |
| DECISION-HASH-REMOVE-1 | 937 | F | gate: the export of an audit is built (D-0345); anchor.py:63,81 still holds sparmvet_decision_hash | stays |
| METADATA-DUPLICATE-ID-MULTIPLIES-ROWS | 938 | E | task says NOT decided | stays; Waits for line added |
| RECIPE-UPLOAD-HANDLER-OVERWRITES | 939 | D | D-0390 decides a plain refusal; ingestion_handlers.py:38-54 still copies with no check; the dated-name form is not decided | stays |
| DATED-COPIES-VS-UNIQUE-PLOT-IDS | 940 | E | D-0390, D-0393 against D-0534 | stays; Waits for line added |
| HOME-PREVIEW-FALLBACK-FIRST-PLOT | 941 | E | fallback at home_theater.py:311-321 | stays; Waits for line added |
| RECIPE-OF-TABLES-ONLY-REFUSED | 942 | E | refusal exists: recipe_check.py T09, config_loader.py:193-205 | stays; Waits for line added |
| PLOT-ID-ACROSS-RECIPES-APP-CHECK | 943 | F | gate: the answer on DATED-COPIES-VS-UNIQUE-PLOT-IDS; branch task/plot-id-across-recipes parked | stays |
| EQUALITY-DIRTY-DATA-GENERATOR | 944 | D | app/tests/equality/make_dirty_data.py and FINDINGS.md exist; FINDINGS.md:53 old text | stays |
| REMOVE-FROM-ALL-MISSES-TABLES | 945 | D | D-0499, D-0531; misses four tables without the plan; on no screen | stays |
| AUDIT-RECIPE-BESIDE-ORIGINAL | 946 | E | task says options, not decided | stays; Waits for line added |
| DEPLOYMENT-STANDARD | 947 | E | D-0413, D-0417, D-0418 | stays; Waits for line added |
| ENGINE-BOUNDARY-STUDY | 967 | E | D-0455, D-0456; stage 0 built (rules_runtime_environment.md Engine marks) | stays; Waits for line added |
| AUDITS-REVERIFY-ALL | 969 | F | D-0467: after HOME and the Gallery are refactored | stays |
| BROWSER-TESTS-INTERMITTENT | 970 | D | cause (a) fixed (merge 6b2734dc); (b), (c) have own tasks; D-0466; trim to the open parts | stays |
| HOME-RIGHT-SIDE-AND-CENTRE-DRAWN-TWICE | 974 | D | home_theater.py:1106 and :2318 use safe_input(input,"sidebar_nav"); :2071 uses _active_space; D-0502 | stays |
| EXPORT-RACE-TEST-FAILS-ALONE | 975 | D | not started; D-0466, D-0050 | stays |
| INGESTION-DISPLAY-NAME-AS-LAUNCH-VALUE | 976 | E | merge dcd9f8f3; handler is dead code | stays; Waits for line added |
| BLUEPRINT-DUPLICATE-PLOT-ID-SHOWN-WRONG | 979 | D | the recipe check P07 is merged (b6742164; recipe_check.py:1150-1173); the BLUEPRINT part is on branch task/blueprint-duplicate-id (349d1474), which is NOT on dev (re-checked after the reviewer said done) | stays |
| PLOT-ID-ACROSS-RECIPES-NOT-CHECKED | 980 | G | D-0534; 4afbb382 | stays; Verdict needed line added |
| P07-SMALL-POINTS | 981 | D | X5 recipe_check.py:1349-1359 does not skip a duplicate inside one recipe; point 3 done; trim to points 1 and 2 | stays |
| HOME-FILTER-T1-T2-SAME-TABLE | 982 | E | PROVISIONAL in t3_audit_engine.py viewed_table; D-0311 against D-0506 | stays; Waits for line added |
| DOCS-JOINS-AND-KEY-PAGES-DISAGREE | 983 | D | D-0486 | stays |
| REMOVE-FROM-ALL-SMALL-POINTS | 984 | D | remove_from_all.py:89 still says certainly not in it; point 2 waits for: refuse, require a list, or default to all places | stays |
| IMPORT-UNDECLARED-COLUMN-ONLY-IN-CONSOLE | 985 | E | D-0050; ingestor.py:55-85 | stays; Waits for line added |
| AUDIT-STEPS-KEYED-WITHOUT-RECIPE | 986 | B | audit steps are nodes with a place in bucket __places__, per-plot stack gone (D-0662, D-0665, D-0672); whether steps survive a recipe switch may need a smaller new task | removed from tasks.md (history in git) |
| BLUEPRINT-ID-REUSED-AND-LEFT-OUT-NOT-SHOWN | 987 | F | BLUEPRINT held | stays |
| LINEAGE-EMPTY-TIER2-FOLD | 988 | B | belongs to the new lineage design (D-0551); utils.lineage_data.lineage_of replaces the old walk | removed from tasks.md (history in git) |
| LEDGER-HEADER-RAISED-NOTES | 989 | D | header notes not checked | stays |
| MACHINE-OLD-WAITER-LOOPS | 990 | A | loops stopped; rule in agent_dispatch_howto.md section 7 and agent_principles.md rule 13 | archived (moved to the done archive of its unit) |
| REVIEWS-D0534-TO-REDO | 992 | F | 349d1474 and fdc6380f are NOT on dev (git merge-base); the task says no merge before the reviews are redone, when the owner says | stays |
| BLUEPRINT-VERIFY-SEVEN-POINTS | 993 | F | D-0493, D-0494; BLUEPRINT held | stays |
| BLUEPRINT-PREVIEW-READS-HOME-TABLE | 994 | F | fix only inside the rebuild; BLUEPRINT held | stays |
| REVIEW-RUNS-FULL-SUITE-AFTER-SHARED-LIST-CHANGE | 995 | E | process note | stays; Waits for line added |
| PLOT-ROWS-NOT-DRAWN | 996 | E | no fix before her choice | stays; Waits for line added |
| DEPLOYMENT-NO-USER-STUDY | 997 | E | D-0428, D-0442 | stays; Waits for line added |
| PERMANENT-DOCUMENTS-OUT-OF-TMP | 1000 | G | D-0419, D-0420, D-0421 | stays; Verdict needed line added |
| LEDGER-ADD-COMMAND | 1004 | D | decision_ledger.py has only list and check (lines 83-89); the task lists options for the owner | stays |
| LEDGER-WORDS-CHECK | 1005 | E | row 5 answered (D-0459) | stays; Waits for line added |
| LINEAGE-QUESTIONS-ONE-LIST | 1007 | D | D-0444; many questions are settled by the place model (D-0662, D-0672, D-0675): drop those about ticks and dialog lines | stays |
| LINEAGE-UNREAD-TABLES-ARE-LINES | 1009 | B | D-0675 replaces D-0451; the library part stays merged (1f3d61de) | removed from tasks.md (history in git) |
| UNREAD-TABLES-EXPORTED-AND-VIEWABLE | 1010 | E | export part built: export_handlers.py:69 tables_no_plot_reads (used :1059); D-0457 preview part not built | stays; Waits for line added |
| LINEAGE-SEMI-JOIN-STUDY | 1011 | A | D-0486 build now; libs/utils/src/utils/lineage_walk.py:45 (P12), :341 | archived (moved to the done archive of its unit) |
| LINEAGE-UNFOLLOWED-JOIN-WARNING | 1012 | G | reviewer judged B for the screen part | stays; Verdict needed line added |
| AUDIT-UNCERTAINTY-CATALOGUE | 1013 | E | D-0473, D-0477 | stays; Waits for line added |
| RESULT-ENTRY-TABLE | 1014 | E | D-0485, D-0487 | stays; Waits for line added |
| AUDIT-TABLE-COMPARISON | 1017 | E | slice 1 merged (libs/utils/src/utils/table_compare.py); slice 2 not built; D-0489 | stays; Waits for line added |
| AUDIT-LOG-ALWAYS-EXPORTED | 1018 | E | D-0478 widened by D-0673 | stays; Waits for line added |
| EXPORT-REPRODUCIBILITY-TWO-PARTS | 1019 | D | D-0492; no final_audited in export_handlers.py; folder names, which part opens at import, old layout wait for her | stays |
| EXPORT-REPORT-BY-GROUP | 1020 | D | D-0484, D-0491; export_handlers.py:2057 still says not built here | stays |
| AUDIT-LIMITS-DOCUMENTED | 1021 | F | D-0461; waits for AUDIT-UNCERTAINTY-CATALOGUE and her reading | stays |
| RECIPE-RULE-DO-NOT-IMPORT-REPLACED-COLUMNS | 1022 | D | D-0462, D-0464 | stays |
| LINEAGE-COLOURS-AND-MARKS-IDEA | 1023 | F | her idea, not a decision; D-0463; deferred until she asks | stays |
| DOCS-AVOID-UNFOLLOWED-JOINS | 1024 | D | D-0486, D-0464; verify the 5 corrected places | stays |
| PYPI-INVESTIGATE | 1025 | F | D-0441 deferred | stays |
| PANEL-STATISTICIAN-AGENT | 1026 | E | no .claude/agents/panel-statistician.md | stays; Waits for line added |
| PLOT-BUILD-ERROR-RAW-TEXT | 1029 | D | strict xfail at app/tests/test_shiny_plot_errors.py:197 | stays |
| BLUEPRINT-UNDECLARED-COLUMNS | 1030 | F | BLUEPRINT held; words not decided | stays |
| HOME-AUDIT-PANEL-BLANK-ON-OPEN | 1032 | G | screen defect | stays; Verdict needed line added |
| HOME-REASON-LOST-DURING-REDRAW | 1033 | B | D-0672: the separate Apply and staged cards go; re-test the reason box in the new step bar | removed from tasks.md (history in git) |
| UML-FRAME-WIDTHS-CHECK | 1034 | G | needs StarUML open | stays; Verdict needed line added |
| BLUEPRINT-CAST-TO-INTEGER-WARNING | 1037 | F | D-0376 note; for when BLUEPRINT is done | stays |
| GALLERY-CONTENT-CORRECTIONS | 1038 | E | D-0401, D-0402 | stays; Waits for line added |
| GALLERY-PICTURE-PROOF | 1039 | A | D-0400 built: merge 8c0d3c53; app/tests/test_gallery_picture_key.py; app/src/bootloader.py | archived (moved to the done archive of its unit) |
| RECIPE-PLACES-SAFE-STEPS | 1040 | E | confirm before building | stays; Waits for line added |
| HOME-FILTER-APPLIED-MARKER | 1041 | E | task says waits for owner | stays; Waits for line added |
| AUDIT-OLD-STEP-DECIMAL | 1042 | E | task says waits for owner | stays; Waits for line added |
| GALLERY-STUDY-PART-B-E | 1043 | F | part b needs StarUML; Gallery held | stays |
| STUDY-RECIPE-PLACES | 1044 | C | the task says folded into DEPLOYMENT-READ-WRITE-STUDY | removed from tasks.md, merged into DEPLOYMENT-READ-WRITE-STUDY |
| DEPLOYMENT-READ-WRITE-STUDY | 1045 | E | D-0417 to D-0443 answered many | stays; Waits for line added |
| BLUEPRINT-JOIN-OUTER-OPTION | 1064 | F | join_designer.py:27 still has outer; D-0486; BLUEPRINT part delayed | stays |
| RECORDS-TASKS-FULL-PASS | 1066 | E | task says waits for a session with the owner | stays; Waits for line added |
| PARKED-BRANCHES-KEEP-OR-DELETE | 1067 | E | task says waits for the owner | stays; Waits for line added |
| AUDIT-OLD-WORDS-FAILS | 1069 | D | audit_old_words.py --check still prints hits | stays |
| FIGSHARE-ROW-ORDER-CONFIRM | 1070 | E | task says waits for the owner | stays; Waits for line added |
| HANDOFF-ARCHIVE-TRACKED-OR-NOT | 1071 | E | task says waits for the owner | stays; Waits for line added |
| SCRATCH-TRASH-EMPTY | 1072 | E | task says waits for the owner | stays; Waits for line added |

### The ticked tasks (done by their own tick)

90 blocks of `tasks.md` start with `- [x]`. Each moves whole to the archive file of its unit (the verdict is A; the evidence is the tick and the text of the task, which says what was done). List: id (line): 
TEST-ORDER-1 (34), EXPORT-FILTER-VALUE-1 (41), OPERATORS-SCREENS-1 (49), POLARS-ACTIONS-2 (50), CLEANUP-COUNTS-1 (53), GALLERY-FLAGS-1 (55), TEST-FLAKY-1 (136), GALLERY-RECIPES-1 (169), GALLERY-SUBMIT-SCHEMA-1 (170), RECIPES-SMALL-1 (180), GALLERY-RIGOR-1 (207), WRITERS-W8-1 (212), ID-RECON-STEPS-1 (214), RETEST-REPLACE-1 (216), IMPORT-PATH-1 (218), JOIN-KEY-TYPES-1 (221), JOIN-PREVIEW-STRICT-1 (225), CHECKER-JOIN-KEYS-1 (228), SMOKE-RACE-2 (232), SMOKE-FLAKE-1 (234), CONTRACT-REMOVE-1 (235), DATA-NA-ISOLATION-1 (241), BP-VALIDATE-1 (246), GALLERY-SUBMIT-EXAMPLE-UNUSED (272), GALLERY-STUDY-RECHECK (273), TESTLAB-REVIEW-1 (337), GALLERY-RECIPES-1 (345), S2-1 (356), S2-1 (382), L427 (427), L428 (428), SELF-JOIN-WARN-1 (451), DEMO-JOIN-1 (457), VERIF-FIX-2 (462), HOME-DATA-IMPORT-FORMAT-CHECK (476), HOME-SMOKE-PREVIEW-FILTER-FAILS (482), RESTORE-LOOP-1 (487), APPLY-BLOCKED-1 (488), SAMPLE-ID-TYPE-1 (527), FORMULA-ELEMENT-FIELD (598), VIZ-GALLERY-INIT (599), DOC-WORKTREE-SECTION (600), THEME-SNIPPETS-DESIGN (601), VALIDATE-INTERPRETER (603), EXPORT-PANEL-KEEPS-FIELDS-1 (604), HOME-RECIPE-SWITCH-CHECK-1 (645), POLARS-CATCH-PLAN-1 (650), NONFINITE-REACH-REPORT-1 (651), AXIS-TEXT-PANEL-1 (656), TEMPLATES-NOT-LOADABLE-1 (657), TEST-LOGIC-RECIPE-REJECT-1 (658), BLUEPRINT-REVIEW-1 (660), EXPORT-FIELDS-PER-SESSION-1 (667), EXPORT-PANEL-SIMPLIFY-1 (668), FLAKY-APPLY-BLOCKED-TEST-1 (713), FILTER-FORM-RESET-1 (714), FLAKY-BROWSER-UNDER-PARALLEL-1 (738), AUDIT-SLICE-A2-NAVIGATOR-ON-GRAPH (771), AUDIT-SLICE-A4-TIER3-READER (780), AUDIT-RUN-NESTED-FOLDERS-1 (787), AUDIT-SLICE-B-WAITS-FOR-THE-OWNER (788), OLD-SESSION-FILES-REMOVED (796), AUDIT-SLICE-C1 (801), GALLERY-PICTURE-CURRENT (841), RULE-OF-PLACES-1 (901), USER-FOLDER-NOT-WRITABLE-WARNS (902), BIG-MOVE-DRY-RUN-1 (903), LINEAGE-DATA-FUNCTION (913), JOIN-META-LEFT-ENFORCED (914), METADATA-DECLARED-RULE (915), LINEAGE-VIEW-G (916), LINEAGE-UML-SYNC (921), HOME-SLICE-2-ONE-READER (926), ENGINE-STAGE-0 (968), HOME-FILTER-VALUE-LOST-ON-REDRAW (971), HOME-FILTER-BETWEEN-NEEDS-BOTH-VALUES (972), HOME-LEFT-PANEL-CLOSES-ON-LATE-REDRAW (973), GATE-GAP-BROWSER-TEST-INTERMITTENT (977), RESULT-ID-TWICE-NOT-REFUSED (978), LINEAGE-DESIGN-QUESTIONS-REVIEW (1006), AUDIT-DROP-UNCERTAIN-ALLOWED (1008), HOME-PREVIEW-ROWS-AND-HIDDEN-COLUMNS (1015), HOME-ALL-ROWS-SWITCH-FOLDS-PANEL (1016), GALLERY-NAME-FROM-UI-LABEL (1027), GALLERY-DEAD-LINKS (1028), FRAME-PANEL-WIDTHS (1031), FILTER-WHOLE-NUMBER-VALUE (1035), HOME-AUDIT-CONTROLS-SCOPED (1036), BLUEPRINT-REVIEW-1 (1063), AUDIT-UML-STALE-TAGS (1068)

## Carried over from the two tasks removed by D-0675

- **AUDIT-DEFAULT-TICKS-REVIEW** (935): the default ticks of the dialog no longer exist (the places are chosen in the lineage). What remains is carried by HOME-SLICE-3A-SHOWN-ITEM and HOME-SLICE-4-CONFIRM-APPLY-FLOW (the staged places, the confirmation of the places chosen); its lessons (D-0508) are kept in the ledger.
- **AUDIT-DIALOG-TABLE-NO-PLOT-READS** (936): a table no plot reads is a place like any other, chosen in the lineage (D-0627, D-0630, D-0675). It is carried by HOME-SLICE-3A-SHOWN-ITEM (a table place shows its table) and HOME-SLICE-4-CONFIRM-APPLY-FLOW (the step is written at it); a sentence is added to both.

## The files of `.claude/tasks/`

46 tracked files. The live list is `tasks.md`. The others:

| File | What it is |
|---|---|
| `archives/tasks_archive_2026-04-10.md` | # Tasks Archive: 2026-04-10 (2 KB) |
| `archives/tasks_archive_2026-04-14.md` | # Tasks Archive (2026-04-14) (0 KB) |
| `archives/tasks_archive_2026-05-03.md` | # Tasks Archive — 2026-05-03 (6 KB) |
| `archives/tasks_archive_2026-05-09.md` | # Tasks Archive — 2026-05-09 (18 KB) |
| `archives/tasks_archive_2026-05-11.md` | # Tasks Archive — 2026-05-11 (38 KB) |
| `archives/tasks_archive_2026-05-22.md` | # Task Archive — 2026-05-22 (16 KB) |
| `archives/tasks_archive_2026-11-13_done_since_nov.md` | # Tasks archive, cleanup of 2026-11-13 (done tasks that were still in `tasks.md`) (56 KB) |
| `archives/tasks_archive_documentation.md` | ## 📘 Documentation Recovery (DONE) (0 KB) |
| `archives/tasks_archive_hygiene_2026-05-21.md` | # Task Archive — Documentation & Hygiene Sprint (2026-05-21) (4 KB) |
| `archives/tasks_archive_infrastructure.md` | # Archive: Foundational Infrastructure & UI Shell (100% DONE) (3 KB) |
| `archives/tasks_archive_integration_qa.md` | # Archive: Phase 9 Integration, QA & Documentation Sync (100% DONE) (2 KB) |
| `archives/tasks_archive_phase14.md` | # Tasks Archive: Phase 12-14 (SPARMVET_VIZ) (1 KB) |
| `archives/tasks_archive_phase24.md` | # Phase 24 Task Plan — `home_theater.py` Decomposition (16 KB) |
| `archives/tasks_archive_phase25.md` | # Phase 25 — Left Sidebar Restructure: Change Manifests (23 KB) |
| `archives/tasks_archive_phase32.md` | # Archive: Phase 18-F, Phase 32, and Audit Script Fixes (19 KB) |
| `archives/tasks_archive_phase33.md` | # Archive: Phase 33 — Blueprint AI Agent MVP-1 (ADR-076) (2 KB) |
| `archives/tasks_archive_phase9.md` | ## 🟢 Phase 9: Triple-Source AMR Integration (FIGSHARE DATASET) — VERIFIED ✅ (1 KB) |
| `archives/tasks_archive_viz_factory.md` | # Archive: Viz Factory & Documentation Recovery (100% DONE) (8 KB) |
| `archives/tasks_test_22J.md` | # Phase 22-J Live-UI Test Checklist (14 KB) |
| `archives/test_ui_persona_archived_20260505.md` | # Testing the different UI personas (0 KB) |
| `home_exploration_build_brief.md` | # Build brief: working protocol and package details for the HOME work (16 KB) |
| `outdated/20260810_testing_part1.md` | > **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** raw evide (21 KB) |
| `outdated/README.md` | # Outdated task files (kept for history only) (2 KB) |
| `outdated/audit_findings_2026-11-07.md` | # Audit findings of 2026-11-07 that the rename did not cause (CONFIG-AUDIT-FIXES-1) (3 KB) |
| `outdated/config_rename_inventory.md` | > **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** key inven (6 KB) |
| `outdated/config_rename_mapping.md` | > **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** generated (82 KB) |
| `outdated/config_rename_review.md` | > **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** review ga (13 KB) |
| `outdated/config_rename_strategy.md` | > **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** plan of t (15 KB) |
| `outdated/home_exploration_build_brief_2026-11-11.md` | > **OUTDATED (2026-11-13): archive copy of the build brief as it was before the clean-up.* (28 KB) |
| `outdated/next_session_start.md` | # Start here (2026-11-12): builders and the design review side by side (8 KB) |
| `outdated/project_word_mapping.md` | > **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** mapping o (3 KB) |
| `outdated/retest_procedure_2026-11-06.md` | > **OUTDATED (2026-11-13): archive copy of the one-off retest of 2026-11-06** (issues #10, (15 KB) |
| `outdated/tasks_backlog_details_2026-11-13.md` | > **OUTDATED (2026-11-13): original text of the backlog tasks that were shortened, merged  (19 KB) |
| `outdated/tasks_before_sort_2026-11-13.md` | > **OUTDATED (2026-11-13): archive copy of `tasks.md` before it was sorted.** It keeps the (87 KB) |
| `outdated/tasks_test_ui_current.md` | > **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** supersede (25 KB) |
| `outdated/test_plan_2026-06_before_clean.md` | > **OUTDATED (2026-11-13): archive copy of `test_plan_2026-06.md` before it was cleaned**  (37 KB) |
| `outdated/test_plan_home_2026-11_ledger.md` | > **OUTDATED (2026-11-13): the full ledger of the HOME test plan as built until 2026-11-12 (36 KB) |
| `tasks_archive_backlog.md` | # Archive: backlog, done items (9 KB) |
| `tasks_archive_decisions_2026_11_15.md` | # Archive: decisions 2026 11 15, done items (3 KB) |
| `tasks_archive_home_audit.md` | # Archive: HOME audit build (stage 2), done items (17 KB) |
| `tasks_archive_tasks_2026_11_16.md` | # Archive: tasks 2026 11 16, done items (2 KB) |
| `tasks_archive_tasks_2026_11_17.md` | # Archive: tasks 2026 11 17, done items (12 KB) |
| `test_plan_2026-06.md` | # SPARMVET_VIZ — Live App Test Plan (35 KB) |
| `test_plan_home_2026-11.md` | # HOME test plan: what is still open (as-built HOME) (20 KB) |
| `uml_findings.md` | # UML model: findings register (26 KB) |

The folder `outdated/` (16 files, its README) holds old plan, test, build-brief and rename files marked OUTDATED; it is covered by the rule at the top of `tasks.md` (superseded material goes to `outdated/`), so it stays where it is. `archives/` holds the task archives of earlier phases; the `tasks_archive_*.md` files beside `tasks.md` hold the archives of the November work. `test_plan_*.md`, `uml_findings.md` and `home_exploration_build_brief.md` are live working files, not tasks.

## Part C: the scratch studies again, with the cleaned task list

Rule (wave 1, applied again to the cleaned list): a group of `.claude/design/studies/scratch_records_2026-11/` stays only while an open task of `.claude/tasks/tasks.md` names its folder or its main page; a group that loses its last such task moves to `.claude/outdated/design/studies/scratch_records_2026-11/` with unchanged content (`git mv`; SHA-256 of all moved files compared before and after: equal). One-line pointers stay at the old path of the files that live files still cite (`.claude/design/decisions_2026-11-14/*`, `.claude/design/home_redesign_intent_and_consequences.md`). A script matched each group's path against the text of the 400 open tasks; it does not judge, task by task, whether the task waits on the group or only cites it as a source (all remaining tasks are of verdict D, E, F or G), so a group may be held by a task that only cites it; that is the safe side.

Totals: 71 groups before (502 files), 61 kept (427 files), 10 moved (75 files). Files in the scratch folder: 533 before, 465 after (the 75 moved, plus 7 new pointer files, plus the 30 pointers of wave 1 and the README, which stay).

### Moved

| Group | Files | The task that held it | Verdict | Moved or kept |
|---|---|---|---|---|
| `coordinator/WHAT_BLOCKS_THE_BUILD.md` | 1 | (named by the coordinator; ledger names it) | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `coordinator/app_features_name` | 4 | NAMES-UI-LABEL-EVERYWHERE | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `coordinator/gallery_fixes_review` | 4 | GALLERY-TWO-NAMES | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `coordinator/gallery_picture_key_review` | 40 | MAP-A-GALLERY-1 | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `coordinator/names_pass_plan` | 4 | NAMES-UI-LABEL-EVERYWHERE | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `panel/adr` | 4 | ADRS-FOR-DECISIONS-WITHOUT-ONE | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `panel/audit_redesign` | 3 | HOME-AUDIT-REDESIGN-SLICES-1 | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `panel/axis_text` | 3 | FORMULA-BUILD-D-1]** , PATH-BASE-1]** , PATH-CHECK-1]** , DATA-IMPORT-OVERWRITE | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `panel/names_whole_app` | 8 | NAMES-ACROSS-THE-APP-STUDY, NAMES-UI-LABEL-EVERYWHERE, TEXTS-FOLLOW-UP | no open task names it now (the task was moved, removed or no longer cites it) | moved |
| `panel/viz` | 4 | VIZ-NOT-ADDABLE-15-1, VIZ-OWN-22-1 | no open task names it now (the task was moved, removed or no longer cites it) | moved |

### Kept (with the open tasks that name it)

| Group | Files | Open task(s) | Moved or kept |
|---|---|---|---|
| `controls_8f951761` | 3 | JOIN-GROWTH-CAUTION-1, ST22-DUPLICATE-ROWS-1 | kept |
| `coordinator/QUESTIONS_FOR_THE_STOP.md` | 1 | AUDIT-QUESTIONS-FOR-THE-STOP | kept |
| `coordinator/blueprint_verify` | 7 | BLUEPRINT-PREVIEW-READS-HOME-TABLE, BLUEPRINT-VERIFY-SEVEN-POINTS | kept |
| `coordinator/data_file_cut` | 1 | DATA-FILE-CUT-ACCEPTED | kept |
| `coordinator/data_import_check` | 1 | DATA-IMPORT-OVERWRITE | kept |
| `coordinator/data_import_questions` | 1 | CONNECT-TEMPLATE-DATA-LOOKUP | kept |
| `coordinator/default_data` | 3 | RECIPE-DEFAULT-DATA-FALLBACK-TEST | kept |
| `coordinator/home_data_picker` | 2 | DATA-IMPORT-OVERWRITE | kept |
| `coordinator/ledger_words_check` | 2 | LEDGER-WORDS-CHECK | kept |
| `coordinator/panel_statistician_draft` | 1 | PANEL-STATISTICIAN-AGENT | kept |
| `coordinator/permanent_documents` | 1 | PERMANENT-DOCUMENTS-OUT-OF-TMP | kept |
| `coordinator/plot_rows_dropped` | 1 | PLOT-ROWS-NOT-DRAWN | kept |
| `coordinator/recipe_name_rule` | 1 | DEPLOYMENT-READ-WRITE-STUDY, DEPLOYMENT-STANDARD, RECIPE-NAME-RULE | kept |
| `coordinator/remove_from_all_review` | 1 | AUDIT-REMOVE-FROM-ALL-DATA | kept |
| `coordinator/remove_from_all_review2` | 1 | AUDIT-REMOVE-FROM-ALL-DATA | kept |
| `coordinator/report_by_group` | 1 | EXPORT-REPORT-BY-GROUP | kept |
| `coordinator/uncertainty_catalogue` | 1 | AUDIT-LIMITS-DOCUMENTED, AUDIT-UNCERTAINTY-CATALOGUE | kept |
| `engine_keys` | 29 | BLUEPRINT-DESIGN-FINDINGS-1, BLUEPRINT-NODE-CLICK-WRONG-TABLE-1, BLUEPRINT-PLOT-PREVIEW-NOT-MOUNTED-1, BLUEPRINT-REMOVED-BUTTON-AND-HINT-1, BLUEPRINT-SAVE-COMMENTS-1, INCLUDE-WATCH-LIST-1, LOADER-WRAPPER-UNWRAP-1, QUESTIONS-PARKED-UNTIL-REFACTOR-STEP, RECIPE-ORPHAN-FILES-1, RULE-SENTENCES-AFTER-RECIPE-CHANGE-1, TIER3-WORDS-MIXUP-CHECK-1 | kept |
| `panel/adr_history` | 110 | ADRS-FOR-DECISIONS-WITHOUT-ONE, DEPLOYMENT-READ-WRITE-STUDY | kept |
| `panel/audit_docs` | 1 | AUDIT-HELP-TEXT | kept |
| `panel/audit_model` | 22 | AUDIT-RULES | kept |
| `panel/audit_rules` | 1 | AUDIT-RULES | kept |
| `panel/author_manifest` | 1 | CONTACT-AUTHOR-MANIFEST-1 | kept |
| `panel/check_on_select` | 1 | CHECK-ON-SELECT | kept |
| `panel/data_ids` | 4 | ID-TEST-REFERENCE-TABLES-1 | kept |
| `panel/data_import_words` | 1 | DATA-IMPORT-SILENT-FACTS, HOME-DATA-IMPORT-MESSAGES-WORDS | kept |
| `panel/deployment_io` | 13 | DEPLOYMENT-READ-WRITE-STUDY, DEPLOYMENT-STANDARD | kept |
| `panel/deployment_no_user` | 9 | DATA-FILE-CUT-ACCEPTED, DEPLOYMENT-NO-USER-STUDY | kept |
| `panel/deployment_standard` | 6 | DEPLOYMENT-STANDARD, PERMANENT-DOCUMENTS-OUT-OF-TMP | kept |
| `panel/dialog_preview` | 2 | AUDIT-DIALOG-PREVIEWS | kept |
| `panel/engine_boundary` | 6 | ENGINE-BOUNDARY-STUDY | kept |
| `panel/engines` | 8 | STALE-RECORDS-1 | kept |
| `panel/export_modes` | 2 | EXP-MODES-DIAGRAM, EXPORT-MODES | kept |
| `panel/export_simplify` | 8 | EXPORT-DOCS-AFTER-SIMPLIFY-1, EXPORT-MODE-TWO-TICKS-1, EXPORT-MODES-QUESTION-1, EXPORT-PDF-REPORT-PNG-SILENT-1, EXPORT-REPORT-FIGURE-LINKS, EXPORT-SVG-SIZE-CHECK-1, EXPORT-SVG-TEXT-AS-SHAPES-1, REVIEW2-OPEN-POINTS-FOR-EVE | kept |
| `panel/formula_d` | 11 | FORMULA-BUILD-D-1, FORMULA-D-STUDY-1, FORMULA-RULE-TESTS-1, ROW-ORDER-PROJECTION-1 | kept |
| `panel/formula_night` | 2 | FORMULA-FIELD-PLAIN-ERROR | kept |
| `panel/formula_safety` | 3 | FORMULA-D-STUDY-1 | kept |
| `panel/gallery_check` | 3 | GALLERY-LEFTOVERS-1 | kept |
| `panel/gallery_study` | 9 | GALLERY-CHART-TYPE-AXIS, GALLERY-CONTENT-CORRECTIONS, GALLERY-NAMES-HEADINGS | kept |
| `panel/gallery_taxonomy` | 5 | GALLERY-TAXONOMY-REVIEW | kept |
| `panel/gallery_verify` | 9 | GALLERY-CONTENT-CORRECTIONS, GALLERY-VERIFY-ALL-34 | kept |
| `panel/help_beside` | 8 | HELP-BESIDE-THE-SCREEN-STUDY | kept |
| `panel/id_vs_key` | 1 | ENTITY-DECL-SHIPPED-1 | kept |
| `panel/key_types` | 2 | KEY-WORDING-OPTIONS-1 | kept |
| `panel/label_trace` | 6 | BLUEPRINT-SAVE-COMMENTS-1, JOIN-LABEL-REBUILD-1 | kept |
| `panel/lookup_table` | 1 | LOOKUP-TABLE-1 | kept |
| `panel/name_fields` | 1 | NAME-FIELDS-PURPOSE-TABLE | kept |
| `panel/one_python` | 4 | INTERPRETER-ONE-PYTHON-1, ONE-PYTHON-RULE-WORDING-1, OTHER-PYTHON-PATHS-1 | kept |
| `panel/path_use_cases` | 4 | DATA-IMPORT-OVERWRITE, EXPORT-SOURCE-RECORD-1, PATH-BASE-1, PATH-CHECK-1, PATH-USE-CASES-STUDY-1 | kept |
| `panel/recipe_arguments` | 6 | SECURITY-FINDINGS-2026-11-17, VIZ-SEED-DICT-POSITION-1 | kept |
| `panel/recipe_places` | 6 | RECIPE-PLACES-SAFE-STEPS, STUDY-RECIPE-PLACES | kept |
| `panel/recipe_versions` | 7 | DEPLOYMENT-READ-WRITE-STUDY, STUDY-RECIPE-VERSIONS | kept |
| `panel/round7` | 46 | AGENT-PROBE-1, READING-ERRORS-1 | kept |
| `panel/session_import` | 7 | SESSION-IMPORT-KEY-EXISTS-1 | kept |
| `panel/sessions` | 2 | SESSIONS-MANY-DATASETS | kept |
| `panel/steps_position_help` | 1 | VIEWPOINTS-O13-O14 | kept |
| `panel/test_speed` | 1 | TEST-SPEED-STUDY-1 | kept |
| `panel/uploaded_data_place` | 4 | DATA-IMPORT-OVERWRITE, DEPLOYMENT-READ-WRITE-STUDY, DEPLOYMENT-STANDARD | kept |
| `panel/verification` | 18 | RULE-EDITS-15 | kept |
| `panel/viz_rename` | 5 | VIZ-NOT-ADDABLE-15-1, VIZ-OWN-22-1 | kept |
| `panel/write_test_at_start` | 2 | DEPLOYMENT-READ-WRITE-STUDY, DEPLOYMENT-STANDARD, WRITE-TEST-AT-START | kept |

The three folders of wave 1 marked KEEP (`whole_picture_2026-11`, `lineage_scope_2026-11`, `staruml_text_practice`) are not part of this check. By the owner's approval (D-0691) `whole_picture_2026-11/sources/` (115 files) and `lineage_scope_2026-11/` (78 files) move to `.claude/outdated/` once what they describe is built and that build is merged; they are NOT moved now; the tasks WHOLE-PICTURE-SOURCES-MOVE-TO-OUTDATED and LINEAGE-SCOPE-STUDY-MOVE-TO-OUTDATED carry the condition. `.claude/outdated/` is in `.aiignore` since the same day (commit `7321ad6c`).

