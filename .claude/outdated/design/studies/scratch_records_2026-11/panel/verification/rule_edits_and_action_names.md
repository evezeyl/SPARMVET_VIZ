# Rule edits and action names (read-only check, 2026-11-16)

Repository HEAD `42d66368`, branch `feat/recipe-format-1`. Nothing was changed or reverted.
Every statement says how I know: read (file:line) or ran (command output).

## PART 1. Your question: how can an action be used if it is not registered?

**Your question was right, and the answer is: the register IS the decorator, and 68 actions are registered.** The file `rules_agent_role_bioscientist.md` section 8 is simply out of date. It lists 67 OLD names. None of the 67 old names is registered under the same name, but 60 of them exist under a NEW name and 7 were removed.

1. The register is the dictionary `AVAILABLE_WRANGLING_ACTIONS`, filled by the function `register_action` (`libs/transformer/src/transformer/actions/base.py:22-36`). Calling it puts the name and the function into the dictionary (read).
2. Only 2 actions use the `@register_action("...")` line that your review session searched for: `modif_filter` (`modified.py:59`) and `step_top_n_other` (`composite.py:42`) (read). That is why the search found only those two.
3. The other 66 (the 65 `polars_*` actions and `modif_join_where`) call the same function WITHOUT the `@` form: `register_action(name, ui_schema=...)(function)`. Python treats both forms the same. They are written one by one (one line per Polars method, with its description and example), not generated from a hidden table. The helper is `_define` (`polars_calls.py:230-240`, the call to `register_action` is at line 240); the helpers `_frame`, `_eager`, the expression helper and the function helper (`polars_calls.py:246`, `:336`, `:390`, `:425`) call `_define`. More direct calls: `polars_calls.py:303`, `:328`; `polars_rows.py:160`; `polars_time_joins.py:221`, `:316`, `:417`, `:432` (read).
4. The files are loaded when the library starts: `libs/transformer/src/transformer/actions/__init__.py` imports `polars_calls`, `polars_aggregations`, `polars_rows`, `polars_time_joins`, `modified`, `composite`, `min_items` (read). Importing runs the registration.
5. I ran the registry: **68 names are registered now** (65 `polars_*`, 2 `modif_*`, 1 `step_*`). The earlier verification also counted 68; I got the same number.
6. So no one has to "register" anything by hand; a recipe uses the name that the dictionary holds. The old names (`cast`, `sort`, `join`, `mutate`, `fill_nulls`, ...) were removed on 2026-11-13 by commit `d63d3f3d` ("old actions removed", ADR-100, decision D-0036: the three prefixes `polars_`, `modif_`, `step_`).
7. The bioscientist file was NOT updated then. It was last changed on 2026-11-09 (`0db0b49e`), four days before. That is the "none of the 67 is registered" finding.
8. The proposed new text exists as row R024 in the list of rule-file changes, status proposed, waiting for your yes (as the earlier check says). I did not verify R024's wording in this task.

### (c) One true sentence to replace "none of the 67 is registered"

"Of the 67 names listed in section 8 of the bioscientist file, none is registered under that name today: 60 exist under a new name (`polars_...`, `modif_filter` or `step_top_n_other`) and 7 were removed; the registry holds 68 actions, all named with the prefixes `polars_`, `modif_` or `step_`."

### (d) What happens today to a recipe that uses an old name (ran)

I took the shipped template `config/data_analysis_recipes/templates/simple_template.yaml`, put one old action in tier 1 and ran the recipe checker (`check_recipe` with the app's catalogs). The user reads, for `cast` and `sort`:
`ST02 'cast' is not a registered action` with the fix line `choose a registered action` (same for `sort`).
For `top_n_other` the fix line is better: `write step_top_n_other`.
Running the engine (`get_action_function('cast')`) gives: `Action 'cast' is not registered. Available actions: polars_select, polars_drop, ...` (the full list of names).
So the user is told that the name is not registered, but for most old names NOT which new name to use. The commit `affee3f1` ("an old action name is refused with the new action named", 2026-11-16) fixes this, but it is only on the branch `task/verif-fix-1`, not on `feat/recipe-format-1` (ran: `git merge-base --is-ancestor` said no). There is also a migration tool, `assets/scripts/migrate_recipe_format.py`, that converts old steps to new ones (read; not run).

### (b) The 67 names, one by one

How I decided (ran): I took the 67 names from section 8, asked the registry whether each one exists (none does), then ran the migration converter `convert_step` (`libs/utils/src/utils/step_migration.py`, the list `CONVERTERS` and `REMOVED_ACTIONS`) on a test step of each name. The converter's output names the new action(s); each new name was checked to be registered (all are). The file `step_migration.py` is on `feat` already (the branch `task/verif-fix-1` does not have it under that path).
Removal commit for all rows: `d63d3f3d` (2026-11-13) with ADR-100 and D-0036. Where a name exists "nowhere", the reason is in the last column.

| # | Old name (bioscientist file, section 8) | Status today | Registered name(s) now, or what to do |
|---|---|---|---|
| 1 | `fill_nulls` | exists under a NEW name | `polars_fill_null` |
| 2 | `drop_nulls` | exists under a NEW name | `polars_drop_nulls` |
| 3 | `replace_values` | exists under a NEW name | `polars_with_columns` |
| 4 | `rename` | exists under a NEW name | `polars_rename` |
| 5 | `drop_duplicates` | exists under a NEW name | `polars_unique` |
| 6 | `unique_rows` | exists under a NEW name | `polars_unique` |
| 7 | `recode_values` | exists under a NEW name | `polars_with_columns` |
| 8 | `sanitize_column_names` | exists NOWHERE (removed) | no action of this name; use input_fields slug/original_name or polars_rename |
| 9 | `keep_columns` | exists under a NEW name | `polars_select` |
| 10 | `drop_columns` | exists under a NEW name | `polars_drop` |
| 11 | `strip_whitespace` | exists under a NEW name | `polars_str_strip_chars` |
| 12 | `round_numeric` | exists under a NEW name | `polars_round` |
| 13 | `filter_range` | exists under a NEW name | `modif_filter` |
| 14 | `add_constant` | exists under a NEW name | `polars_with_columns` |
| 15 | `filter_eq` | exists under a NEW name | `modif_filter` |
| 16 | `filter_ne` | exists under a NEW name | `modif_filter` |
| 17 | `filter_gt` | exists under a NEW name | `modif_filter` |
| 18 | `filter_lt` | exists under a NEW name | `modif_filter` |
| 19 | `rename_columns` | exists under a NEW name | `polars_rename` |
| 20 | `unique` | exists under a NEW name | `polars_unique` |
| 21 | `regex_extract` | exists under a NEW name | `polars_str_extract` |
| 22 | `cast` | exists under a NEW name | `polars_cast` |
| 23 | `coalesce` | exists under a NEW name | `polars_coalesce` |
| 24 | `label_if` | exists under a NEW name | `polars_with_columns` |
| 25 | `mutate` | exists under a NEW name | `polars_with_columns` |
| 26 | `regex_replace` | exists under a NEW name | `polars_str_replace_all` |
| 27 | `null_if` | exists under a NEW name | `polars_with_columns` |
| 28 | `top_n_other` | exists under a NEW name | `step_top_n_other` |
| 29 | `window_agg` | exists under a NEW name | `polars_with_columns` |
| 30 | `shift` | exists under a NEW name | `polars_shift` |
| 31 | `fill_nulls_direction` | exists under a NEW name | `polars_fill_null` |
| 32 | `sort` | exists under a NEW name | `polars_sort` |
| 33 | `sample` | exists under a NEW name | `polars_sample` |
| 34 | `cum_sum` | exists under a NEW name | `polars_cum_sum` |
| 35 | `cum_count` | exists under a NEW name | `polars_cum_count` |
| 36 | `date_extract` | exists under a NEW name | `polars_with_columns` |
| 37 | `date_truncate` | exists under a NEW name | `polars_dt_truncate` |
| 38 | `list_slice` | exists under a NEW name | `polars_list_slice` |
| 39 | `list_join` | exists under a NEW name | `polars_list_join` |
| 40 | `is_in` | exists under a NEW name | `modif_filter` |
| 41 | `not_in` | exists under a NEW name | `modif_filter` |
| 42 | `z_score` | exists under a NEW name | `polars_with_columns` |
| 43 | `percentile` | exists NOWHERE (removed) | D-0036 "percentile removed"; it was rank divided by row count, not a percentile |
| 44 | `value_counts` | exists NOWHERE (removed) | no action of this name; the converter says: use polars_group_by with pl.len() |
| 45 | `describe_stats` | exists under a NEW name | `polars_describe` |
| 46 | `select_by_pattern` | exists NOWHERE (removed) | no action of this name; name the columns in polars_select |
| 47 | `horizontal_stats` | exists under a NEW name | `polars_sum_horizontal` |
| 48 | `any_horizontal` | exists under a NEW name | `polars_any_horizontal` |
| 49 | `all_horizontal` | exists under a NEW name | `polars_all_horizontal` |
| 50 | `interpolate` | exists under a NEW name | `polars_interpolate` |
| 51 | `split_and_explode` | exists under a NEW name | `polars_explode`, `polars_with_columns` |
| 52 | `derive_categories` | exists NOWHERE (removed) | removed in code only; D-0038 is PROVISIONAL (an agent, not Eve); a lookup is a polars_join |
| 53 | `split_column_to_parts` | exists under a NEW name | `polars_str_splitn`, `polars_unnest`, `polars_rename` |
| 54 | `divide_columns` | exists under a NEW name | `polars_with_columns` |
| 55 | `split_column` | exists under a NEW name | `polars_str_splitn`, `polars_unnest`, `polars_rename` |
| 56 | `unpivot` | exists under a NEW name | `polars_unpivot` |
| 57 | `explode` | exists under a NEW name | `polars_explode` |
| 58 | `unnest` | exists under a NEW name | `polars_unnest` |
| 59 | `split_to_list` | exists under a NEW name | `polars_str_split` |
| 60 | `to_struct` | exists under a NEW name | `polars_drop`, `polars_with_columns` |
| 61 | `pivot` | exists under a NEW name | `polars_pivot` |
| 62 | `summarize` | exists under a NEW name | `polars_group_by` |
| 63 | `count_by_group` | exists under a NEW name | `polars_with_columns` |
| 64 | `join` | exists under a NEW name | `polars_join` |
| 65 | `join_filter` | exists under a NEW name | `polars_join` |
| 66 | `sink_parquet` | exists NOWHERE (removed) | D-0036 "scan/sink are engine-only"; not a recipe action |
| 67 | `scan_parquet` | exists NOWHERE (removed) | D-0036 "scan/sink are engine-only"; not a recipe action |

**Three counts of the 67:**
- registered under the SAME name: **0**
- exists under a NEW name: **60**
- exists NOWHERE (removed): **7** (`percentile`, `value_counts`, `select_by_pattern`, `sanitize_column_names`, `derive_categories`, `scan_parquet`, `sink_parquet`)

Notes for you:
- Some old names become two or three steps (for example `split_column` becomes `polars_str_splitn`, `polars_unnest`, `polars_rename`; `to_struct` becomes `polars_drop` and `polars_with_columns`). Several old names become the same new action (for example the `filter_*` names, `is_in`, `not_in` all become `modif_filter`).
- For `value_counts`, `select_by_pattern` and `sanitize_column_names` the converter gives a replacement recipe (a different action), so they are "removed as an action", not "removed as a possibility".
- `derive_categories`: removed from the code; the ledger line D-0038 is PROVISIONAL (taken by an agent), and ADR-100 says you have not confirmed this removal. That is an open point for you, not part of the 15 edits.
- What I did not check: that each new action gives exactly the same table as the old one (the converters are tested by `libs/transformer/tests/test_step_conversion.py`; I did not run that suite).

## PART 2. The 15 edits to rule, agent, hook and workflow files with no recorded yes

How to read: "a" = follows a decision of yours (number); you confirm the text. "c" = no decision found; it comes back to you as a question. I do not judge if an edit is good. I searched: the ledger (`.claude/knowledge/decision_ledger.md`, now 247 lines, the earlier count of 181 is out of date), the ADR log, `tasks.md`, the handoff and `RULE_FILE_CHANGES.md` (the last one holds no row for any of these 15).
Your D-0104 says: "no rule file is changed without her agreement". Most of these edits came before D-0104 (2026-11-15 20:36 local); only items 1 and 2 came after.
Result: **a = 6, c = 9.**

### 1. `f1f70353` (2026-11-16 08:45) docs(agents): mark what is not Eve's text in the decision-compliance files
- Files and lines: `.claude/workflows/decision_compliance.md` (43 lines changed: top paragraphs, sections 4, 5, 6, 7, new section 8); `.claude/agents/coordinator.md:34`; `.claude/hooks/coordinator_guard.py:61` (the example in the help text)
- What the rule now says that it did not say before: The file now marks every part the builder wrote as "[ADDED]" and lists them in a new section 8, saying you accept or remove them. The hook's example now quotes your real words of D-0112.
- Linked decision: D-0125 "The decision-compliance rules are APPROVED: the text of M150" covers her text only. The [ADDED] parts have no decision; the file says so itself.
- Status: **c: no decision found for the [ADDED] parts, comes back to her as a question**
- Still in the file today? Yes, and extended since (sections 8 and 9 grew: `decision_compliance.md` now has 113 lines).
- Question for you: Do you accept the parts marked [ADDED] in `decision_compliance.md` (the summary table, the description of the ledger, the Decisions block syntax)? If no, an agent removes them and the file keeps only your text.

### 2. `ee4f1eac` (2026-11-16 08:39) fix(hooks): a NONE-CHECKED path is a regular file inside the project, leading dots kept
- Files and lines: `.claude/hooks/coordinator_guard.py` lines 26-27, 63, new function `_none_checked_problem` (about line 130), `brief_problem` (about line 155)
- What the rule now says that it did not say before: The hook now refuses a "NONE-CHECKED" path that is outside the project folder, is the ledger itself, or is a directory. Before it accepted any existing file.
- Linked decision: D-0125 says the path is "a file that exists"; this is stricter. D-0155 (scout report saved under tmpAI/) does not ask for it either.
- Status: **c: no decision found, comes back to her as a question**
- Still in the file today? Yes (`_none_checked_problem` is in the hook, 2 matches).
- Question for you: Should the hook accept only a regular file inside the project that is not the ledger for NONE-CHECKED? If no, it goes back to "any file that exists".

### 3. `fdb7df0f` (2026-11-15 19:49) docs: point the document references at the files that exist today
- Files and lines: `.claude/workflows/implementation_workflow_transformer.md:41`
- What the rule now says that it did not say before: The user-documentation file to append to is now `docs/workflows/transformer_integrity.qmd` (the old `transformer_implementation.qmd` does not exist; I confirmed `transformer_integrity.qmd` exists).
- Linked decision: D-0104 "Broken paths in rule files are repaired by an agent: find the original purpose of each sentence".
- Status: **a: follows D-0104 (a broken path repaired); she confirms the text**
- Still in the file today? Yes, line 41.

### 4. `55e578f5` (2026-11-14 23:48) chore(agents): standing rules of the coordinator, and the guard refuses Bash that writes files
- Files and lines: `CLAUDE.md:52` (one long bullet added); `.claude/hooks/coordinator_guard.py` rule 4 in the docstring (lines 19-26), functions `bash_writes_files` and helpers (lines 51-86), the refusal at about line 130
- What the rule now says that it did not say before: A coordinator session never edits a file (not even a one-line fix), agents check evidence, contradictions are fixed by agents, decided behaviour must be tested, work stays traceable. The hook refuses Bash that writes files outside `tmpAI/` (sed -i, tee, redirections, rm/mv/cp, inline Python).
- Linked decision: D-0049 "the coordinator only coordinates" (2026-11-14); the handoff of 2026-11-14 23:50 (`handoff_active.md:829`) lists under "Decided by Eve on 2026-11-14 (evening)" "The coordinator never edits a file." The commit message says "Eve, 2026-11-14" without her words. The Bash refusals themselves (the list of blocked commands) are the builder's implementation; no decision names them.
- Status: **a: follows D-0049 and the handoff record; she confirms the text (note: this edit contradicts `CLAUDE.md` lines 41 and 48 "a one-line fix", see question Q1 of the earlier check)**
- Still in the file today? Yes (`CLAUDE.md:52`, `bash_writes_files` in the hook).

### 5. `da4e5ae7` (2026-11-14 13:25) test(retest): a select step with a misspelled column replaces the retired output field scenario
- Files and lines: `.claude/workflows/retest_procedure.md` (21 lines added, 16 removed: lines 26-44, 66-139)
- What the rule now says that it did not say before: The retest steps use the new action names (`modif_filter` with `column`, `op`, `value`, `na`), say which recipes the selector offers and which are listed as unavailable, and the broken-recipe scenario is now `retest_bad_select_column`.
- Linked decision: D-0036 "prefixes polars_/modif_/step_ ... modif_filter"; D-0034 (DEC13-26) for the removal of `output_fields`. The file just follows the new code.
- Status: **a: follows D-0036 and D-0034; she confirms the text**
- Still in the file today? Yes (lines 29, 44, 66, 78 use the new names).

### 6. `9bfdaf4c` (2026-11-13 16:35) feat(ingestion): strict import - only declared input fields enter ...
- Files and lines: `.claude/workflows/retest_procedure.md:156` (one line: the error text the user reads)
- What the rule now says that it did not say before: The expected message now reads "Column(s) [...] declared in input_fields for ... not found in the source file (expected file headers: ...)".
- Linked decision: D-0034 (DEC13-26 includes DEC24 strict import, `recipe_format_spec.md:116`: "a declared column missing from the file fails").
- Status: **a: follows D-0034 (DEC24); she confirms the text**
- Still in the file today? Yes (line 156).

### 7. `16d52140` (2026-11-13 14:57) docs(tests): P0 inventory ...; automatic audits paused
- Files and lines: `.claude/workflows/audit_routine_registry.md:3` and `.claude/workflows/schedule_commands.md:3` (a banner of 2 lines each)
- What the rule now says that it did not say before: Says all automatic audits are off until the refactor is finished (the four systemd timers are disabled); run the audits by hand.
- Linked decision: The banner says "(Eve)"; `tasks.md:204` (AUDITS-REACTIVATE-1) says "paused since 2026-11-13 (Eve; ...)". No ledger line and none of her words found.
- Status: **c: no decision found, comes back to her as a question**
- Still in the file today? Yes (banner on line 3 of both files).
- Question for you: Did you decide on 2026-11-13 that the automatic audits are paused until the refactor is finished? If no, an agent removes the banner and re-enables the timers.

### 8. `19285129` (2026-11-13 14:40) chore(claude): triage the backlog; make the retest procedure permanent; remove the materialize shim
- Files and lines: `.claude/workflows/retest_procedure.md` (new file, 180 lines, moved from `.claude/tasks/`)
- What the rule now says that it did not say before: The one-off retest of 2026-11-06 becomes a permanent procedure to run "after any change to the orchestrator, cache keys, tier stores, export, load gate".
- Linked decision: No ledger line, no ADR, no task with her words. `tasks.md:267` (EXPORT-CHECK-1) uses the file but does not record a decision.
- Status: **c: no decision found, comes back to her as a question**
- Still in the file today? Yes (the file exists; later commits 9bfdaf4c and da4e5ae7 edited it).
- Question for you: Should the retest procedure be a permanent workflow file that agents run after changes to the export, cache keys, tier stores and the load gate? If no, it goes back to a one-off note in the task archive.

### 9. `e3865b59` (2026-11-13 10:23) chore(audits): triage the 2026-11-12 Thursday reports (all six pass)
- Files and lines: `.claude/workflows/audit_routine_registry.md` lines 23-27 and 33 (six table rows: last run and next run dates)
- What the rule now says that it did not say before: Only dates: the six Thursday audits show last run 2026-11-12 and next run 2026-11-19.
- Linked decision: None needed: a record of a run, not a rule. No decision found.
- Status: **c: no decision found, comes back to her as a question (small)**
- Still in the file today? Yes (6 rows show 2026-11-12), but the next-run dates are now wrong: the audits are paused (item 7).
- Question for you: Is a record of audit run dates in this file allowed without your yes? If no, the dates are removed from the table.

### 10. `4ba10ba9` (2026-11-11 21:34) docs(home): reading guide, review personas, UML status, safe build brief and handoff
- Files and lines: `.claude/workflows/design_review_personas.md` (new file, 100 lines)
- What the rule now says that it did not say before: A reusable method to review a design with personas (scientist, data scientist, developer, checker, novice) with eight rules (verify, label evidence, run, search outside, ...).
- Linked decision: The text quotes "(Eve, 2026-11-11.)" for "Never guess, always verify" (line 14); that rule is D-0017 "Never guess: CLAUDE.md section 9". The method as a whole (the personas, their order) has no decision.
- Status: **c: no decision found for the method, comes back to her as a question**
- Still in the file today? Yes (the file exists; the checker persona is the one used by the agents today).
- Question for you: Do you want the persona review method as a permanent workflow file? If no, it is moved out of `.claude/workflows/` and agents stop citing it.

### 11. `b055ba07` (2026-11-11 11:33) feat(home): preview filters on Raw and Result, one operator vocabulary
- Files and lines: `.claude/rules/ui_implementation_contract.md` lines 88, 90, 93 (4 lines added, 2 removed)
- What the rule now says that it did not say before: Said that exploration filters preview on EVERY view (Raw, Result, My view); only audit steps stay on My view.
- Linked decision: It was replaced the same day by `fa552bf7`, which follows D-0014 "Exploration filters change the table on every view, plots only on My view" (ADR-098, confirmed by you). The first text said plots too, so it did not match D-0014.
- Status: **c: no decision found for this version; moot because it was replaced**
- Still in the file today? No. Replaced since: lines 88 and 90 now say "Changes the data table on every view; changes PLOTS only on My view (ADR-098)", which is D-0014. Note: line 93 still carries the "SUPERSEDED in part (ADR-098 ...)" wording of the later fix.

### 12. `143ae2d4` (2026-11-09 20:12) fix(blueprint,home): close #53/#54/#55 and make Validate check the real recipe rules
- Files and lines: `.claude/rules/ui_implementation_contract.md:422` (one table row)
- What the rule now says that it did not say before: The `test_lab_right_info` panel is "reachable since issue #55 (2026-11-10)" instead of "currently unreachable in every shipped template".
- Linked decision: No decision of hers. The handoff (`handoff_active.md:336-342`) describes issue #55 as a fix of a stale setting; the row describes the code.
- Status: **c: no decision found, comes back to her as a question (small; it only describes the code)**
- Still in the file today? Yes, line 422.
- Question for you: May a rule file describe the state of the code (here: the Test Lab right panel is shown) without your yes? If no, the sentence is removed.

### 13. `0db0b49e` (2026-11-09 16:25) feat(transformer): register filter_ne/filter_gt/filter_lt/not_in actions (#52)
- Files and lines: `.claude/rules/rules_agent_role_bioscientist.md:411` and `:415` (2 lines: `filter_ne`, `filter_gt`, `filter_lt` and `not_in` added to the list)
- What the rule now says that it did not say before: The four filter names were added to the list of "verified action names".
- Linked decision: No decision. ADR-097 (line 4838) records the gap and the closure (ACTIONS-FILTER-GAPS-1) but not a rule text.
- Status: **c: no decision found, comes back to her as a question**
- Still in the file today? Yes, but it is now wrong: none of these four names is registered (Part 1; they became `modif_filter`). Row R024 of the list proposes the new text, still waiting for her yes.
- Question for you: Do you agree that section 8 of the bioscientist file is replaced by the list of the 68 registered names (R024)? If no, the old list stays and agents keep writing names the engine refuses.

### 14. `0821ef6f` (2026-11-09 15:33) feat(export): sensitive-data warning + import with hash verification (#46, #48)
- Files and lines: `.claude/rules/rules_app_structure.md:52` and `:163` (2 rows: directory map and ownership matrix)
- What the rule now says that it did not say before: The file `app/modules/bundle_importer.py` (import of a reproducibility bundle with 4-leg hash verification) is listed with its owner.
- Linked decision: D-0013 "Two export modes ... import verification warns, never blocks (Eve)" (ADR-097).
- Status: **a: follows D-0013 (ADR-097); she confirms the text**
- Still in the file today? Yes (lines 52 and 163; the file exists).

### 15. `c32e7ea2` (2026-11-09 10:21) fix(home): empty data analysis recipe state no longer crashes startup
- Files and lines: `.claude/rules/rules_data_analysis_recipe_structure.md:310-318` (9 lines added, 4 removed)
- What the rule now says that it did not say before: The "scope boundary" is now closed: when no recipe passes the gate, startup does not crash; HOME shows a short message ("No data analysis recipes yet").
- Linked decision: D-0009 "HOME checks every recipe at start ... a failing one is not selectable, shows reason + contact (Eve)" (ADR-094 point 6 left the empty state open; the closure is in ADR-094, line 4595, 2026-11-09). D-0079 "A recipe with an error is not accepted in HOME (a message ...)".
- Status: **a: follows D-0009 and D-0079; she confirms the text**
- Still in the file today? Yes, line 310.

## Summary of the 15

| Status | Count | Commits |
|---|---|---|
| a: follows a decision, she confirms the text | 6 | fdb7df0f (D-0104), 55e578f5 (D-0049 + handoff), da4e5ae7 (D-0036), 9bfdaf4c (D-0034), 0821ef6f (D-0013), c32e7ea2 (D-0009) |
| c: no decision found, question to her | 9 | f1f70353, ee4f1eac, 16d52140, 19285129, e3865b59, 4ba10ba9, b055ba07 (moot, replaced), 143ae2d4, 0db0b49e |

Still in the file today: 14 of 15. One was replaced: b055ba07.

## What I could not find or check
- No decision of yours in the ledger, ADR log, tasks, handoff or the list of rule-file changes for the 9 "c" items. The conversation record (`cd1b0ac7`) is not something I read; her words may exist there.
- The earlier count of 15 matches the "nothing on record" set in `check_6_7_rules_tests.md` (class C). I did not recount the other 19 commits.
- For item 4 I rate "a" because D-0049 and the handoff record it; the hook's Bash refusals are not named in any decision.
- Part 1: I did not run the conversion test suite, and I did not check R024's new wording.
