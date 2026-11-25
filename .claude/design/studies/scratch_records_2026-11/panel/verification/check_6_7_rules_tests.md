# Check 6 and 7: rule and agent files, and the tests that were weakened or removed (HEAD 77b663f1, 2026-11-16)

Read-only. Nothing in the main tree was edited. Five undo experiments ran in a detached scratch worktree (removed at the end; `git status` of the main tree is clean).
Labels: read = I read the file or diff; ran = I ran it and saw the output; reasoned = my reading.
Decisions used (all read in `.claude/knowledge/decision_ledger.md`, status DECIDED): D-0104 (rule files: no change without her yes, one traceable list), D-0126, D-0128, D-0129, D-0050 ("No silent error that is the rule."), D-0031 (tests adapted before they run), D-0049 (Fable only as coordinator; the coordinator only coordinates), D-0041 (agent channel), D-0017 (CLAUDE.md section 9), D-0014 (exploration filters), D-0056 (seed 0 by default), D-0125 (decision-compliance rules), D-0046.
The list of rule-file changes: `.claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md` (144 rows; its scope is rule files, and since 11-16 also the agent files, CLAUDE.md and the hook).

## PART A. Rule files, agent files, hooks

### A1. Every commit since 2026-11-09 that touches `.claude/rules`, `agents`, `hooks`, `settings.json`, `CLAUDE.md`, `workflows` (ran: `git log --since='2026-11-09 00:00' -- <paths>`)
34 commits with their own content, plus 2 merge commits (`31af52e0`, `cacc79f8`, only merge main into a branch) that have no lines of their own. Today's merge `77b663f1` brings in 3a3aa73d, d64f0cdf, ee4f1eac, f1f70353.
Column "Yes of hers": L = ledger line DECIDED; R = row of the list; text = only the rule text names her; none = no record found. Class A = yes on record, B = the decision is on record but the edit has no recorded yes (the list says so itself), C = nothing on record and not in the list.

| Commit | Date | Files | What it says (one sentence) | List row | Yes of hers | Class |
|---|---|---|---|---|---|---|
| f1f70353 | 11-16 | coordinator.md, hook docstring, decision_compliance.md | Marks every place the builder added as [ADDED] and lists them in section 8 "she accepts or removes it" | none | none for the [ADDED] parts (the text itself says so) | C |
| ee4f1eac | 11-16 | hook | A NONE-CHECKED path must be a regular file inside the project, not the ledger | none | none (D-0125 says "a file that exists"; this is stricter) | C |
| d64f0cdf | 11-16 | hook | Refuse a builder/reviewer brief with no Decisions block or a number not in the ledger | R144 | L D-0125 | A |
| 3a3aa73d | 11-16 | 10 agent files, decision_compliance.md, CLAUDE.md | The decision-compliance text of M150, one pointer line, one line per agent | R132-R143 | L D-0125 | A |
| fdb7df0f | 11-15 | implementation_workflow_transformer.md | Points a dead doc path at an existing file | none | none (fact fix) | C |
| 2b13bbdb | 11-15 | rules_verification_testing.md | Browser-test time worded as "one measurement" | R102 | none for the wording (list says so) | B |
| 772881f3 | 11-15 | rules_verification_testing.md | Browser tests take about 14 minutes | R101 | D17 confirmed (M89) | A |
| 89043503 | 11-15 | rules_viz_factory.md, ui_implementation_contract.md | Typed filter values, operators by column type, `between` with four ends | R109, R116, R119 | decision ADR-104 DECIDED; edit unconfirmed | B |
| f8636ff4 | 11-14 | ui_implementation_contract.md | Filter row lists `between`, `closed`, what Send to Audit carries | R117 | none | B |
| 55e578f5 | 11-14 | hook, CLAUDE.md | Standing rules of the coordinator (never edits, agents check, traceability) and the hook refuses Bash that writes files | none | commit message says "Eve, 2026-11-14", no quote, no ledger line | C |
| 22a0dc14 | 11-14 | ui_implementation_contract.md | The filter row carries the `na` tick | R118 | NA rule D-0042 DECIDED; the edit unconfirmed | B |
| 6e318386 | 11-14 | 10 agent files, hook, settings.json, 2 workflows, CLAUDE.md | Creates the coordinator system, the guard hook and the settings (deny Agent(model:fable), default model sonnet) | none | L D-0049 for the Fable/coordinate part only; the ledger says "commits do not quote her" | A (partial) |
| 547c6a78 | 11-14 | CLAUDE.md | "The coordinator only coordinates" | none | L D-0049 | A |
| da4e5ae7 | 11-14 | retest_procedure.md | Retest steps follow the new action names | none | none (follows code) | C |
| 1f2c447e | 11-14 | CLAUDE.md | Only the coordinator may be Fable | none | L D-0049 | A |
| 74abfc48 | 11-14 | rules_verification_testing.md | The "orchestrator integrity suite in every library" rule is replaced by the pytest gate | R095 | plan yes in tasks.md:245; the rule edit has none (list says so) | B |
| 873cf3a4 | 11-13 | rules_agent_channel.md | One session (HOME) reports to Eve | R005 | text only | B |
| 9bfdaf4c | 11-13 | retest_procedure.md | Error text of the strict import | none | none (follows code) | C |
| 6521f966 | 11-13 | rules_agent_channel.md | Section 7: agents agree, Eve decides | R004 | L D-0041 | A |
| 58e56842 | 11-13 | rules_agent_channel.md | Message limit 10 lines to about 25; file 150 to 300 | R003 | text only | B |
| 16d52140 | 11-13 | audit_routine_registry.md, schedule_commands.md | "All automatic audits are off until the refactor is finished (Eve)" | none | text names Eve; no ledger line (ran: no sparmvet timer is listed, so it is true today) | C |
| 19285129 | 11-13 | workflows/retest_procedure.md (moved from tasks/) | The retest procedure becomes a permanent workflow file | none | none | C |
| c454bcf6 | 11-13 | rules_agent_channel.md (new), workspace_standard.md, CLAUDE.md | New rule file for sessions at the same time | R006, R127 | L D-0041 | A |
| e3865b59 | 11-13 | audit_routine_registry.md | Dates of the audit table | none | none (a record, not a rule) | C |
| 6349ba7f | 11-12 | rules_runtime_environment.md, ui_implementation_contract.md | Tier 1 allows declared third-party packages; T3 may hold any registered action in a recipe's own list | R076, R123 | "Eve, 2026-11-12, ADR-099 point 16" in the text; reading guide O1-O8 confirmed | A |
| e0f79a84 | 11-11 | CLAUDE.md | Section 9: no guessing | none | L D-0017 (her chat turn; the commit does not name her) | A |
| 4ba10ba9 | 11-11 | workflows/design_review_personas.md (new) | The review method with personas | none | none; the text says "Eve 2026-11-11" | C |
| d36a2a05 | 11-11 | ui_implementation_contract.md | ADR number 087 corrected to 098 | none | L D-0014 | A |
| fa552bf7 | 11-11 | ui_implementation_contract.md | Filters change the table on every view, plots only on My view | none | L D-0014 cites this commit | A |
| b055ba07 | 11-11 | ui_implementation_contract.md | Filters preview on Raw and Result (also plots) | none | none; replaced the same day by fa552bf7 | C |
| 143ae2d4 | 11-09 | ui_implementation_contract.md | `test_lab_right_info` row: reachable since #55 | none | none | C |
| 0db0b49e | 11-09 | rules_agent_role_bioscientist.md | Adds `filter_ne/gt/lt`, `not_in` to the list of registered actions | none | none | C |
| 0821ef6f | 11-09 | rules_app_structure.md | Rows for `bundle_importer.py` | none | none | C |
| c32e7ea2 | 11-09 | rules_data_analysis_recipe_structure.md | "Scope boundary closed (issue #38)": no usable recipe no longer crashes | none | none | C |

Counts (ran, counted from the table): 34 commits. A = 12, B = 7, C = 15. So 22 have no recorded yes of hers for the edit itself (7 B, where the list already says so, and 15 C). Entry 33's six commits are all class C.

Entry 33, the six commits named (is the change still in the file today? ran/read):
- `55e578f5`: yes. `CLAUDE.md:52` holds the standing rules and `coordinator_guard.py:87 bash_writes_files` is called at line 224. Read: text and hook agree.
- `b055ba07`: no. Its rows ("Preview on every view ... ADR-087") were replaced one day later by `fa552bf7`; today `ui_implementation_contract.md:88,90` say "Changes the data table on every view; changes PLOTS only on My view (ADR-098)", which is D-0014.
- `143ae2d4`: yes (`ui_implementation_contract.md:422`); it agrees with `config/ui/sidebars/testlab_standard_right.yaml:1,3` (`visible: true`, `test_lab_right_info`) (read).
- `0db0b49e`: the text is still in the file (`rules_agent_role_bioscientist.md:415`), but it is now STALE against the code (see A2, finding 1).
- `0821ef6f`: yes (`rules_app_structure.md:52,163`); `app/modules/bundle_importer.py` exists (ran `ls`).
- `c32e7ea2`: yes (`rules_data_analysis_recipe_structure.md:310`); `Bootloader.get_default_data_analysis_recipe_or_none` (bootloader.py:567) and `has_usable_data_analysis_recipe` (:584) exist.

### A2. Does today's rule text agree with her decisions and the code? (for the class B and C changes)
1. DEVIATED (rule against code, since 2026-11-13). `rules_agent_role_bioscientist.md` section 8 "Registered Actions": "Use only these verified action names" then lists 67 names. Ran: I compared them with `AVAILABLE_WRANGLING_ACTIONS` (68 registered names): none of the 67 listed names is registered (`filter_ne`, `filter_gt`, `filter_lt`, `not_in` from `0db0b49e`, and `join`, `cast`, `mutate`, `summarize`, ...). An agent that obeys this line writes recipes the engine refuses. Not a decision of hers: the list's own row R024 proposes the new text (status "proposed", waits for her yes). Since which commit: the old actions were removed by ADR-100 in the 11-13 migration. Fix: R024 (small, one row, her yes first).
2. DEVIATED (two rules of hers contradict each other inside CLAUDE.md). `CLAUDE.md:41` and `:48` and `.claude/agents/coordinator.md:27` say the coordinator does itself "a one-line fix, a merge, a git command" (547c6a78, 6e318386). `CLAUDE.md:52` standing rule (1) (55e578f5, later the same day, hook-enforced) says "never edits a file itself, not even a frozen file or a one-line fix". Both carry "(Eve, 2026-11-14)". The hook follows (1) (read, hook line 224). Not decided which one stands: one question for her (Q1).
3. DEVIATED (rule against code, new since 11-15): `rules_viz_factory.md:123` says "`random_state: null` (or `random`) on a layer ... gives a different arrangement on every render" (D-0004, DECIDED 2026-11-05). Commit `54e6979f` (11-15) built the refusal of null and random on a layer and says "PROVISIONAL (S1)"; `tasks.md:306` says "S1 to S3 NOT ANSWERED" (read). The code and the rule file now say opposite things and no yes of hers stands behind the code. This is entry 27's question; recorded here because the rule file is the one that is out of date (or the code is). Fix: her answer on S1 first (Q2).
4. DID NOT DEVIATE: `55e578f5` (hook and CLAUDE.md agree), `143ae2d4`, `0821ef6f`, `c32e7ea2` (code exists as the text says), `b055ba07` (replaced), `16d52140` (no audit timer exists), `da4e5ae7` and `9bfdaf4c` (retest steps follow the real actions and messages; I did not run the retest), `fdb7df0f`.
5. Class B rows: the edits agree with the decisions they name (ADR-104 points 4, 7, 8; NA rule D-0042; D-0041 channel text). The list already asks her. `74abfc48` (R095) replaced a rule ("an orchestrator integrity suite in every library") by the pytest gate: the code agrees (the transformer has no integrity suite any more); only her yes is missing.
6. The [ADDED] parts of the 11-16 files (`decision_compliance.md` section 8 lists them: the intro paragraphs, the section 4 table, the section 5 ledger text, the NONE-CHECKED form, section 7 "a change to these files gets a row in the list") and `ee4f1eac` are builder text; the file says she accepts or removes them. One more added choice: "Panel agents are not part of the hook until Eve says so" (section 6): scouts and scribes are exempt by M150, panel agents are not named there.

### A3. Hooks and settings: anything that LOOSENS what an agent may do since 2026-11-09
Ran: `git log -- .claude/hooks .claude/settings.json` gives 5 commits: `6e318386` (hook created, settings), `55e578f5`, `d64f0cdf`, `ee4f1eac`, `f1f70353`. The settings file was touched once.
- `settings.json` (6e318386): adds `env CLAUDE_CODE_SUBAGENT_MODEL=sonnet`, a `deny` of `Agent(model:fable)` and the hook entry; the `allow` list is unchanged (ran `git diff 6e318386 HEAD -- .claude/settings.json`: empty). Tightens.
- Hook: `55e578f5` only added lines (Bash that writes files refused); `d64f0cdf` only added lines (the decision gate); `ee4f1eac` removed 5 lines and replaced the path test by a stricter one (inside the project, not the ledger, regular file); `f1f70353` changed a docstring. No refusal was removed, no path newly allowed, no model newly allowed after 6e318386. DID NOT DEVIATE.
- Today's merge `77b663f1` against its first parent (ran `git diff 77b663f1^1 77b663f1 --stat`): 13 files, 223 insertions, 0 deletions; no removed line in `.claude/hooks`. It only tightens (read).
- Ran `app/tests/test_coordinator_guard.py`: 40 passed.
Things that are open doors, not changes (read, `coordinator_guard.py`): (a) `main()` returns 0 (allows) when its input is not JSON (`:189-190`) and when no coordinator marker exists (`:195`); the docstring says "Fails open". Nothing of hers records "fail open" (Q3). (b) The decision gate applies to `builder`, `builder-opus`, `reviewer` only (`DECISION_GATED`); an agent of another kind (for example `general-purpose`) called with `model: sonnet` passes the first test (`:241`) and is not gated, so a coordinator can build through it without a Decisions block. M150 exempts scouts and scribes, not other kinds. (c) Rule texts that loosen something for agents, each with its record: message limit 10 to 25 lines (R003, text only); Tier 1 may import declared third-party packages (R076); T3 recipe list may hold any registered action (R123); the orchestrator integrity suite is optional (R095, no recorded yes).

## PART B. Tests

### B1. Entry 42: commit `6f3ec110` (11-13) removed 96 assert lines and 5 test files
Ran: `git show 6f3ec110 --stat`, the removed files read at `6f3ec110^`, the current tests grepped and run.
| Removed | What it tested | Today | Verdict |
|---|---|---|---|
| test_filter_actions.py (11 tests) | `filter_ne/gt/lt`, `not_in`: strictness, no-op cases, missing column raises, `is_in`/`not_in` complements | Actions removed (ADR-100). Behaviour in `test_modif_filter.py` (operators, in/not_in with a list, missing column fails, `na` required) and the snapshot `step_conversion_snapshot.json` (`filter_gt`, `filter_lt`, `filter_ne`, `not_in`) | DID NOT DEVIATE |
| test_step_actions.py | `top_n_other` equals the old action, ties, refuses a step that hides a choice | `test_top_n_other.py` (ties alphabetical, label/column written not defaulted, bad parameters) | DID NOT DEVIATE |
| test_metadata_validator.py | type aliases `string`, `character` are refused | `libs/ingestion/tests/test_declared_types_and_missing_values.py::test_an_old_type_name_is_refused_and_named` (parameters numeric, categorical, utf8, integer, string). Ran a scratch call: `character` is refused with "'character' is not a Polars dtype" | DID NOT DEVIATE (the test list lacks `character`; the refusal is general) |
| test_validate_types.py (8 tests) | an uploaded file whose values do not fit the declared type is rejected with column and examples | `apply_declared` in the Data Import handler (`data_import_handlers.py:273-310`); `app/tests/test_import_test_files.py::test_the_text_in_numeric_file_names_the_column_and_the_value`; ingestion tests for decimals in an integer field, digits as text, empty cell | DID NOT DEVIATE for 7 of 8. Not tested any more: "only a few examples are shown" (cap `EXAMPLES` in `declared.py:133`): a display limit, small |
| test_replacements_by_polars_steps.py (18 tests) | an old action and its Polars steps give the same table; frozen right half | `test_step_conversion.py` + snapshot (113 cases, content hash): summarize, split_column, split_and_explode, strip_whitespace, z_score, label_if, window_agg, divide_columns, date_extract, horizontal_stats, unique_rows... | DID NOT DEVIATE except one: **`split_column_to_parts`** has NO case (ran grep: only `step_migration.py:362,453` mention it, no test, no snapshot key). The old test pinned "the old action lost the remainder; the Polars steps keep it" |
| 96 removed asserts in test_ui_schemas, test_schema_registry, test_actions_must_act, test_deterministic_order | schema keys of removed actions (`mutate`, `filter_eq`, alias keys), the two xfail guards, `value_counts` order, `sample` default seed | Ported: `test_actions_must_act.py` (123 passed, ran), `test_deterministic_order.py` (`test_sample_has_no_default_seed_any_more`), registry tests keep context, categories, search; `value_counts` is in `REMOVED_ACTIONS` (step_migration.py:28) and refused (test_a_removed_action_is_refused) | DID NOT DEVIATE |
Finding 42-a: DEVIATED, small: conversion of the old step `split_column_to_parts` is no longer tested (D-0031: tests adapted, not dropped; agent_principles 5). Fix: one case in `test_step_conversion.py` with a value that has a remainder (about 15 lines, one builder).
Related (entry 44, commit `8f2dfe7d`, 11-13): it deleted `app/tests/test_column_names_through_the_steps.py` (10 tests). Four of them tested behaviour that is not xfail: a rename in a schema's tier 1 is seen by the join steps of tier 1 and tier 2; a column that exists only after a join is seen by later steps and tier 2; a rename after the join is seen by tier 2; a missing column in a schema step fails with its name. Ran: I found no test with those names or that flow through the orchestrator (searched app/tests and libs/*/tests for rename, after_the_join, typo, seen_by). Finding 42-b: DEVIATED, medium: the flow of column names through the tiers and a join (her question in that file's header, answered by running) has no test now; the checker tests (`test_recipe_check_join_keys.py`) cover keys, not names flowing. Fix: one test file on the retest-sized recipe, about 60 lines.

### B2. Entry 43 (seed tests changed) and entry 44 (deleted test data and scripts)
- Entry 43: `551462d3` (removed 65 asserts), `54e6979f`, `4d2c0f75`. Read the removed asserts: they belong to the mechanism "HOME draws a seed per session" (stored drawn seed, two sessions draw independently, the warning for an unpinned plot). D-0056 (DECIDED): "HOME draws no seed per session". Kept and still tested: recipe seed holds, audit pin beats the recipe, default 0, reference pane without the pin, the record of seeds used (`test_plot_seeds.py` 17 tests, `test_plot_seed.py` 28). Class (a): rule changed by decision. DID NOT DEVIATE for the removals. The refusal of `null`/`random` (`54e6979f`) is not D-0056: see A2 finding 3.
- Entry 44: `74abfc48` (old test data and `debug_pipeline.py`): replaced by the pair per action, `test_action_recipe_pairs.py` exists (ran `ls`). `99a14148` (`app/tests/audit_export_bundle.py`, `debug_gallery_submission.py`): the dead submission code, D-0046 DECIDED ("dead submission code goes"). `6a5af970` (`test_join_validate_message.py`, 5 tests): the design changed (the message is now built after Polars raised); `test_join_validate_diagnosis.py` has 13 tests; the "validate met runs and gives Polars's rows", "m:m never refuses" and "nulls_equal" cases are covered by `test_the_message_appears_exactly_when_polars_raises_on_random_cases` and the null-key tests; I did not find a test for `left_on`/`right_on` naming (COULD NOT BE CHECKED by name). `8f2dfe7d`: see 42-b.

### B3. Entries 43/44 of the brief: every xfail, skip, deleted test since 2026-11-09 (ran: `git log -p` scan of added and removed lines, 133 hits)
Marks that were added and REMOVED when the behaviour was built or the test replaced (all good, strict xfail did its job): ingestion types and missing values, 15 marks (69b7bd2d added, f2ecfbb7 removed); `polars_` equals Polars (b0f97acf, removed 159ffe78); registry rules (removed c39c9cab, 6f3ec110); `test_actions_must_act` (4e4833ca, removed 6f3ec110, tests pass today: ran 123 passed); `test_filter_defects` #62/#63 (19a45571, removed 9427dc36, dd356f12); `test_step_order` N13 and 8.5 (removed 99447ec1, 307e6b4e); `test_filter_int_equivalence` (removed 24e2fbc7, 28a4581c); BP-SAVE-TUPLE-1 (0406d2ef added, 3945a1d7 removed; `tasks.md:368` done); `test_column_names_through_the_steps` (deleted, see 42-b).
Environment skips (legitimate): root user (`test_gallery_listing.py:63`, `test_join_preview_errors.py:131`, `test_gallery_check_at_start.py:79`), wheel build (`test_packaging.py:26`), pandas/openpyxl missing, app features not developer/qa in the browser tests, a tab not found in the browser smoke tests, and `test_polars_time_joins_preconditions.py:358` (skips only when Polars happens to give one order in 12 runs; the asserts before it still ran).
Marks that STAND at HEAD (entry 28), each run one at a time (ran `-rxX`):

| Test | Reason given | Task on `tasks.md`? | Ran | Verdict |
|---|---|---|---|---|
| test_registry_audit_vs_plotnine.py:473, :487 (8 cases) | wrapper sends every key to `theme()`; text read letter by letter | VIZ-DEFECTS-1 (open, line 452) | 8 xfailed | DID NOT DEVIATE |
| test_every_yaml_example_renders.py:133 `guide_label` | `guide_legend(labels=...)` refused | VIZ-DEFECTS-1 | 1 xfailed | DID NOT DEVIATE |
| test_no_silent_error.py:172,175 `GUIDE_LABEL_BROKEN` | same | VIZ-DEFECTS-1 | the mark is **never applied**: `guide_label` is not in `AFFECTED` (ran `python` import: False) | DEVIATED, small: a dead xfail mark, stale (since 9caab17a); remove the mark or add the case |
| test_suggested_steps.py:87,96,105 (3 tests) | the suggested ID cleaning steps do not give the matches the user accepted | `ID-RECON-STEPS-1` is marked DONE (`tasks.md:221`), the 3 findings are not in it | 3 xfailed | DEVIATED: a known science defect (the recipe does not give the accepted matches) with no open task; D-0050 "No silent error" says fix, not list. Fix size: needs her decision on how the steps are written (the test file says so) |
| test_shiny_blueprint_known_defects.py:17 | BP-GLIMPSE-ANCHOR-1: the glimpse applies a component's steps to HOME's anchor | none: the id is in no file under `.claude/tasks` (ran grep; only old worktrees) | 1 xfailed | DEVIATED: a known defect with no task |
| test_writers_emit_format_one.py:173 | a draft from Blueprint "cannot be loaded by the app; needs a decision (W8)" | WRITERS-W8-1 is done (`tasks.md:219`); this item is in no open task | 1 xfailed | DEVIATED: open defect, no task, waits for a decision of hers |
None of the 9 marks passes unexpectedly (strict). Stale mark found: 1 (`GUIDE_LABEL_BROKEN`). Stale documentation: `app/tests/test_filter_defects.py:4` still says "Each defect test is marked xfail(strict=True)" though all marks were removed (reasoned from the grep).
Other stale item: `ACTION-MUST-ACT-1` is still `[ ]` in `tasks.md:115` although the two xfail tests that waited for it now pass (123 passed). The task text was not updated (reasoned): ask a scribe.

### B4. Entry 45: commits that revert or undo an earlier fix; and the "fix with no test in the commit" list
- No commit starts with "Revert" since 11-09 (ran `git log --grep='^Revert'`: empty). Messages containing revert/undo/restore (17) are features or docs. One real reversal of behaviour: `b055ba07` (preview filters also on plots of Raw/Result) undone the same day by `fa552bf7`; this follows D-0014 (DECIDED, ADR-098 "confirmed by @evezeyl") and the ADR/contract/tests now agree. DID NOT DEVIATE.
- The 10 commits with no test in the commit (route 3): is there a test today?
  - 173faf20 (filter dialog reads a guarded mirror, rule R3/R4): no test names the mirror (ran grep `_dialog_audit_nodes`). It is a Shiny wiring rule (`ui_implementation_contract.md` section 14); only a browser test could show it. DEVIATED, small, COULD NOT BE CHECKED by mutation (browser).
  - 310495fa: only renames a string through `action_names`; the text is identical; nothing to break (reasoned).
  - fe2a812e (a schema plotted directly runs its own tier 2): yes, `test_schema_tier2.py`, `test_recipe_tiers.py`; experiment 3 below, caught.
  - 1bcb43d3 (HOME reports plot errors through the reporter): `test_shiny_plot_errors.py`, `test_plot_issue_reporter.py` exist; not mutated (browser).
  - 51adcbf0 (facet components state their plotnine class): `test_component_plotnine_field.py`, `test_component_schemas.py` exist.
  - 579499f0 (HOME and the export use one seed): replaced by 551462d3; `test_plot_seeds.py`, `test_shiny_seed_places.py`.
  - 8a534a4c, db9d5113 (key fields declared String): `test_complex_template_runs.py`, `test_categorical_migration.py`; no test fails for the single field I know of (not mutated).
  - f84b15a9 (retest recipe strict form): `test_retest_data_analysis_recipes.py`.

### B5. Route 3: the 15 largest "fix / no longer / refuses / identical / tested" commits in libs/ and app/ (by changed source lines), is a test present today?
All 15 have test files in the commit that still exist at HEAD (ran `ls`), except `fe2a812e` and `579499f0` (covered by later tests, see B4) and `6a5af970` (its old test file was replaced by `test_join_validate_diagnosis.py`).
2d4ddbf5 seed per layer (`test_plot_seeds.py`, `test_plot_seed.py`), 7cafc08a registry widgets (`test_schema_registry.py`, `test_action_registry_consistency.py`), 0406d2ef gate (`test_recipe_gate_handlers.py`, `test_export_refusal.py`), 307e6b4e audited frame order (`test_export_view_consistency.py`, `test_step_order.py`), d0d4f379 export Mode 1 (`test_export_download.py`, browser, not run), 870207ba join preview (`test_join_preview_parity.py`), 12019cdc gate rerun (`test_gate_gap.py`), 45742491 audit step refused (`test_audit_step_refused_not_skipped.py`), b3308150 time joins (`test_polars_time_joins_*`), plus the five below.

Five undo experiments (detached scratch worktree, my own `PYTHONPATH`, the one test run before and after; baseline passed each time, `git checkout` after each):
| # | Commit and fix | What I undid | Test run | Result |
|---|---|---|---|---|
| 1 | 6a5af970 join validate explained after Polars raised | `anchor.py`: `raise explained from exc` became `raise` | test_join_validate_diagnosis.py | CAUGHT: 12 failed, 1 passed (baseline 13 passed) |
| 2 | 26c40302 a failed gallery example is never listed | `gallery_listing.py:46` no longer filters the rejected names | test_gallery_listing.py | CAUGHT: 3 failed (baseline 14 passed) |
| 3 | fe2a812e a schema's own tier 2 is its T2 | `recipe_tiers.py:59` returns `[]` for a schema | test_schema_tier2.py + test_recipe_tiers.py | CAUGHT: 11 failed, 19 passed (baseline 30 passed) |
| 4 | a8fe20f2 a date and time text is checked (hour 25 is not a time) | `filter_values.py` `_is_datetime_text` ends `return True` | filter and datetime tests (526 tests) | CAUGHT, but by ONE test: `test_filter_values.py::test_read_datetime_column_gives_the_exact_text` (525 passed). The refusal of an impossible hour has a thin guard |
| 5 | d94bc6a4 `geom_sina`/`stat_sina` are seeded | `viz_factory.py` the `elif is_random_layer(...)` branch removed | test_every_component_randomness.py | CAUGHT: `test_no_component_is_random_once_the_factory_seeds_it` failed (baseline 7 passed, 60 s) |
Not established by experiment (could not): 173faf20 and 1bcb43d3 (browser, not run), d0d4f379 (browser download test).
Worktree removed (`git worktree list` shows none of mine; main tree `git status` clean).

## The two tables

Table 1, rule-file changes and her yes: see A1 (34 commits: A 12, B 7, C 15).

Table 2, tests lost or weakened and marks:
| Item | State | Verdict |
|---|---|---|
| `split_column_to_parts` conversion | no test since 6f3ec110 | DEVIATED (small) |
| column names through the tiers and a join | test file deleted by 8f2dfe7d, no replacement found | DEVIATED (medium) |
| "only a few examples are shown" in an upload error | not tested | minor |
| `GUIDE_LABEL_BROKEN` xfail | dead mark | DEVIATED (small) |
| ID-RECON-STEPS-1 (3 xfail) | task marked done, defects open | DEVIATED, needs her |
| BP-GLIMPSE-ANCHOR-1 | no task | DEVIATED, needs a task |
| Blueprint draft not loadable (W8) | no open task | DEVIATED, needs her |
| ACTION-MUST-ACT-1 | task open, tests pass | stale task |
| a8fe20f2 impossible hour | one guarding test | thin |

## For Eve: rule-file changes with no recorded yes (yes / no, one line each; old text, new text, what it changes for an agent)
1. `55e578f5` CLAUDE.md:52 and the hook. Old: (nothing). New: "(1) the coordinator never edits a file itself, not even a frozen file or a one-line fix ... (hook-enforced)", plus the Bash refusal in `coordinator_guard.py:87`. For an agent: a coordinator session cannot write any file outside `tmpAI/`. Yes / no? (See Q1: it contradicts lines 41, 48 and coordinator.md:27.)
2. `16d52140` `audit_routine_registry.md:3`, `schedule_commands.md:3`. Old: audits scheduled by timers. New: "PAUSED (2026-11-13, Eve): all automatic audits are off until the refactor is finished." For an agent: nobody runs the audits by themselves; run by hand. Yes / no?
3. `4ba10ba9` new file `workflows/design_review_personas.md` ("Eve, 2026-11-11"). New: the persona method (eight rules). For an agent: the method the reviewers follow. Yes / no?
4. `19285129` new file `workflows/retest_procedure.md` (from `tasks/`). New: the retest steps are permanent, "after any change to the orchestrator, cache keys, tier stores, export, load gate". Yes / no?
5. `0db0b49e` `rules_agent_role_bioscientist.md:415-417`. Old: "...`filter_eq`, `rename_columns`, `unique`". New: "...`filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`...", "`is_in`, `not_in`". Now stale (none of the names is registered); it is replaced by row R024 (proposed). Say yes to R024 and this goes away.
6. `143ae2d4` `ui_implementation_contract.md:422`. Old: "currently unreachable in every shipped template". New: "Reachable since issue #55 (2026-11-10)". Describes the code; changes nothing for an agent. Yes / no?
7. `0821ef6f` `rules_app_structure.md:52,163`; `c32e7ea2` `rules_data_analysis_recipe_structure.md:310`. Both describe code that exists. Yes / no?
8. `b055ba07` is replaced; nothing to ask. `fdb7df0f`, `da4e5ae7`, `9bfdaf4c`, `e3865b59`: fact and record edits; nothing to ask.
9. The [ADDED] parts of `decision_compliance.md` (section 8 lists them) and `ee4f1eac` (NONE-CHECKED must be a regular file inside the project, not the ledger; hook `_none_checked_problem`). Yes / no?
10. From her own list, still without a yes: R095 (`74abfc48`, the integrity-suite rule becomes the pytest gate), R102 (`2b13bbdb`), R117/R118/R109/R116/R119 (filter text), R003, R005 (message length, one session reports).

## Numbered questions
Q1. `CLAUDE.md` says both "the coordinator does a one-line fix itself" (lines 41, 48, coordinator.md:27) and "never, not even a one-line fix" (line 52, hook-enforced). Which stands? (the hook enforces the second.)
Q2. S1: a layer that writes `random_state: null` or `random`: refused (as built, PROVISIONAL, `54e6979f`) or "a different arrangement each render" (`rules_viz_factory.md:123`, D-0004)? Tasks says S1 to S3 not answered.
Q3. Should the guard hook fail open (allow) when its input cannot be read (`coordinator_guard.py:189`)? And should the decision gate also cover other agent kinds called with `model: sonnet` or `haiku`, or only builder, builder-opus, reviewer?
Q4. The three open findings of the ID cleaning steps (`test_suggested_steps.py`): how should the suggested steps be written so that the recipe gives the matches the user accepted? Task ID-RECON-STEPS-1 is closed; may an agent open a new one?
Q5. May an agent add a task for BP-GLIMPSE-ANCHOR-1 and one for the Blueprint draft that the app cannot load (W8)?
Q6. Yes to row R024 (the list of registered action names in the bioscientist rule)? It is the one rule text that today tells agents to write names the engine refuses.
Q7. May a builder re-add the lost tests (`split_column_to_parts` conversion; column names through the tiers and a join)?
