# What could have deviated since 2026-11-09 (first step: the list, nothing checked yet)

Branch `feat/recipe-format-1`, HEAD `77b663f1`. Written 2026-11-16. Nothing here is a finding that something IS wrong. Each entry is a place where a check is worth doing (D-0128, D-0129).
Labels: read = I read the file or the output; ran = I ran a command and saw the output; reasoned = my reading of what I saw; assumed = not checked.
Scripts and raw lists are in the same folder: `base.py` (areas), `route1.py`, `route2b.py`, `route3.py`, `baseline_diff.py`, `commit_areas.tsv` (one line per commit with its area).

Decisions this work answers (her words):
- D-0126: "I think we need to verify what has been done since we started the refactoring - to ensure no wrong things have been done otherwise that will lead to more problems after."
- D-0128: "...better safe that sorry and start from there. Also we do not need to run all the tests again but identify what could have deviated and then verify that to ensure its ok."
- D-0129: "...have then the list of could have deviated to actuall checks - did it deviate - if it did fix what can be fixed - as usual in case of doubt - ask."

## Counts (ran)
`git log --since='2026-11-09 00:00' --format=%h | wc -l` gives 701 commits (99 are merges). The files touched, counted once, are 1225 (`--name-only | sort -u | wc -l`). Her review session counted 688 and 1215; the difference is the commits made after that count. By day: 11-09 25, 11-10 1, 11-11 38, 11-12 67, 11-13 96, 11-14 168, 11-15 261, 11-16 45.
Commit author is always one person (`evezeyl`). The sessions can only be told apart by the "Co-Authored-By" line (ran): Sonnet 5.5 438 commits, Fable 5.2 102, Sonnet 5 27, Opus 5.5 18, Haiku 5.5 2, no line 15 (the 15 are almost all from 11-09 and 11-10, see entry 22).

## A. The commits grouped by area

How a commit got its area (reasoned, script `base.py`): each file path is sorted into an area (table below). A commit gets the area that has most of its code files. Test files and documents do not vote unless the commit has nothing else. Only tests = "tests only". Only documents and records = "documents and records". A merge commit has no files of its own, so it has its own line.
A commit that touches several areas is counted once here, in its main area. The second table counts every commit that touches the area at all.

| Area (path rule) | Commits | Files |
|---|---|---|
| Recipe format and checker (`libs/utils/src/utils/recipe_*`, `formula_check`, `action_names`, `engines`, migration scripts, shipped recipes in `config/data_analysis_recipes`, `assets/ref_data`, `app/modules/data_analysis_recipe_validator.py`, `renamed_keys.py`) | 62 | 369 |
| Engine actions, missing values, typed values, sort and ties, seed (`libs/transformer/src`, `libs/ingestion`, `libs/id_reconciliation`, `missing_values`, `na_choice`, `polars_types`, `random_layers`, `plot_seeds`) | 44 | 199 |
| Join rules (any path with "join" in it, outside tests: `join_keys.py`, `relational/joins.py`, `join_diagnosis.py`, `join_designer.py`) | 6 | 20 |
| HOME screens, filter dialog, audit steps, export, sessions (`app/handlers`, `app/modules`, `app/src`, `filter_values.py`, `ui_schema.py`, `config/ui`) | 67 | 139 |
| Plot library (`libs/viz_factory`, `app/modules/plot_*`) | 29 | 52 |
| Gallery (`libs/viz_gallery`, `assets/gallery_data`, any "gallery" path) | 13 | 92 |
| Blueprint (`libs/blueprint_arch`, `blueprint_handlers.py`) | 24 | 43 |
| Test Lab (`libs/test_lab`; not on your list, added so no commit is left over) | 4 | 15 |
| Documents and records (`docs/`, `.claude/design`, `knowledge`, `tasks`, `logs`, `README`) | 256 | 185 |
| Tests only (`*/tests/`, `app/tests/`, golden files) | 58 | 118 |
| Tests and documents only | 12 | 249 |
| Agent rules and hooks (`.claude/rules`, `agents`, `hooks`, `workflows`, `CLAUDE.md`, `settings.json`, `decision_ledger.py`) | 27 | 91 |
| Merge commits (no files of their own) | 99 | 0 |
| Total | 701 | 1225 distinct |

Touches (a commit counts in every area it touches, ran): documents/records 354 commits, tests 283, HOME 98, recipe format 94, engine 63, plot 49, rules 37, Blueprint 36, joins 23 (code files only; join tests are under tests), gallery 16, Test Lab 5.
Commits I could not assign: none (0 "unassigned"). Eight commits touch only small scripts outside every area (`assets/scripts/build_dep_graph.py`, `check_doc_links.py`, `figshare_plot_integration.py`, `scripts/audit_*`, `scripts/run_audits.sh`, `libs/utils/pyproject.toml`, `config/deployment/local/retest.yaml`); they are counted in the area of their other files. The "joins" area is small because most join work sits inside commits whose main part is engine, recipe or HOME.

## B. What could have deviated

How to read an entry: **What**, **Risk** (why), **Where** (commits, files), **Must agree with**, **Check** (what to read or run, and what it cannot see). `Routes` says which of the eight routes found it.

### Recipe format and checker

**1. The strict recipe reader and the one checker `check_recipe`** (Routes: 2)
- What: `libs/utils/src/utils/recipe_check.py` is the single place that decides if a recipe is valid. `recipe_loader.py` reads it, `recipe_spec.yaml` holds the format as data.
- Risk: the most changed code file of the format work: 30 commits on 4 days (ran, Route 2 table). One checker that is wrong in one rule lets wrong recipes in for every area.
- Where: `5a7ab37b` (11-13, "check_recipe, the strict recipe loader"), then 29 more; `libs/utils/tests/test_recipe_check.py` 10 commits.
- Must agree with: D-0033 "DEC01-12: one format for every recipe; unknown keys fail, no compat default; one checker `check_recipe` in libs/utils"; D-0029 "fail instead of warn (HOME rejects, Blueprint reports)"; D-0002 "errors raise; the app reports and skips, never exits".
- Check (medium, one short run): write a 30-line script that loads each shipped recipe (pipelines, templates, retest, gallery examples) with `check_recipe` and prints errors and warnings; then break 5 recipes (unknown key, missing `description`, missing `spec_version`, wrong engine name, old action name) and see 5 distinct errors. Cannot see: error classes the checker never looks for.

**2. `Categorical` and `String`: the spec and the code disagree on the record** (Routes: 1)
- What: DEC27 (spec line 124) says "`categorical` is refused with the message 'this was String'". The note of 2026-11-15 (line 129) says DEC27 "was a refactoring choice ... not a rule of the standard"; both types are usable.
- Risk: two records say different things (rule H: stop and report). The code may follow either.
- Where: `.claude/design/recipe_format_spec.md:124` and `:129`; `libs/utils/src/utils/recipe_check.py:741` (advice names String or Categorical); commits `8db67b47` (nominal fields to String), `dc59701d` (hint for the old word), `2ac83ddb`.
- Must agree with: D-0035 (DEC27, "replaced in part by D-0057"); D-0057 "`Categorical` and `String` are both usable and written as such"; D-0098 (levels order, Enum for ordered).
- Check (small, reading + 1 short run): read the checker message for lower-case `categorical`; run `check_recipe` on a recipe declaring `Categorical`: it must pass. Say that DEC27 line 124 still needs a "replaced by" mark. Cannot see: shipped fields that should be `Enum` (order has a meaning).

**3. Excel upload is read as text, then typed** (Routes: 1, 7)
- What: `app/handlers/data_import_handlers.py:303`: an Excel file is read with `pl.read_excel` and every column is cast to String; a CSV is read as text. Then `apply_declared` applies the declared types.
- Risk: Excel cells are numbers. A whole number may become the text "2022.0" and then fail or change when declared Int64. The old reader path `libs/ingestion/src/ingestion/excel_handler.py` was last changed in April, so it has not been looked at since the change.
- Must agree with: D-0035 "DEC27 `type` required, any Polars dtype; DEC28 `null_values`/`strip` stated"; agent_principles 2 "Nothing changes a result silently".
- Check (medium): upload a small .xlsx with a year column and a float column, declared Int64 and Float64, and compare with the same data as .tsv. Cannot see: other Excel quirks (dates).

**4. Decision rows of the format with no test that names them** (Routes: 1)
- What: the spec has 46 DEC rows. 32 of them are named in no test file (ran: `grep -rlw DECnn app/tests libs/*/tests`): DEC01, 02, 04-08, 10-15, 17-22, 24-26, 29, 37-42, 44-46.
- Risk: a row that no test names may not be tested at all. This is a weak signal: a test can check a rule without naming the row.
- Must agree with: D-0033, D-0034, D-0036, D-0039 (DEC01-DEC49).
- Check (medium, reading): for each of the 32, a reviewer finds the sentence of the row and one test that would fail if the rule were broken; "none found" is the finding. Cannot see: a test that exists with another name.

**5. `decision_hash` is still there** (Routes: 1)
- What: D-0025 says "retire `decision_hash`; drop the plot input key". The code still calls `write_anchor(..., decision_hash=...)` (`app/modules/orchestrator.py:213, 249, 287`) and `export_handlers.py:127-131` has `decision_hashes`.
- Risk: it may only be the name of a parameter that is kept, or the old key still written next to the new key.
- Must agree with: D-0025 "Key = series of labelled parts ..., 128 bits ...; retire `decision_hash`"; D-0003 "chained keys"; D-0082 "keys declared in the recipe".
- Check (small, reading): read `write_anchor` in `libs/transformer/src/transformer/actions/persistence/anchor.py` and what is stored under that name; confirm it holds the new labelled key. Cannot see: if a stored file from before the change is still used (see D-0090).

**6. The recipe graph in `libs/utils` is not there** (Routes: 1)
- What: D-0031 "Recipe graph in libs/utils, Blueprint navigator rebuilt on it". No file or class `recipe_graph` exists (ran: `ls libs/utils/src/utils`; grep gives nothing). `tasks.md:73` lists RECIPE-GRAPH-UTILS-1 as open (read).
- Risk: it is probably "not built yet", not a deviation. But three commits changed the navigator meanwhile (`32ddddbb`, `46cbceef`), so Blueprint may have its own copy of the rule.
- Check (small, reading): confirm the task is open and no commit claims it done.

**7. Commits that touch code and name no task, issue or decision** (Routes: 2)
- What: 131 of the 602 non-merge commits touch code or shipped recipes and carry no task code, issue number, decision number, or the word "decid" in their message (ran: `route2b.py`).
- Risk: nothing ties them to a decision. The biggest ones (files): `d63d3f3d` (93 files, "the switch to recipe format 1 on the branch"), `ce373923` (47, shipped recipes to the strict form), `c827d335` (41, `final_contract` and `output_fields` removed), `db9d5113` (28, key fields String), `d801ec29` (22, missing-value texts declared), `99a14148` (6 code files, demo recipe, dead submission code removed), `6f9479e0` and `551462d3` (seed).
- Must agree with: D-0033/D-0034/D-0047 (final_contract removal "next step ok"), D-0046 (submission code).
- Check (large, 5 reviewers one per group): for each commit, one sentence "this implements D-xxxx / DECnn because ..."; no sentence = report. `d63d3f3d` first. Cannot see: decisions taken in chat and never written.

**8. The formula check exists in two forms** (Routes: 7)
- What: `libs/utils/src/utils/formula_check.py:291` `formula_problems` (used by `recipe_check.py:570` and `evaluate_formula` at `:311`, which `polars_calls.py:195` and `id_reconciliation/core.py:254` call). A second check, `function_string_problems`, guards an `eval` in `libs/viz_factory/src/viz_factory/geoms/core.py:1308` for `stat_function`.
- Risk: two rule sets for "what text may run". Only one is the allow-list of D-0064.
- Must agree with: D-0030 "formulas only from an allowed list of Polars functions"; D-0064 "the formula allow-list as built is accepted for now".
- Check (small, reading + 1 run): read both lists, run `function_string_problems("lambda x: __import__('os')")` and `formula_problems("__import__('os')")`: both must refuse. Cannot see: bypasses through lambda attributes.

### Engine actions

**9. The action names and "equal to Polars"** (Routes: 2, 3)
- What: actions renamed `polars_*`, `modif_*`, `step_*`; an action named `polars_` must be exactly Polars. Churn: `docs/appendix/transformer_actions.qmd` 21 commits, `libs/utils/src/utils/action_names.py` 11, `libs/transformer/tests/test_action_recipe_pairs.py` 11, `libs/transformer/src/transformer/actions/polars_calls.py` 9.
- Risk: one action that adds a hidden choice (default, sort, cast) while keeping the `polars_` name.
- Where: `b0f97acf` (equality tests, strict xfail until built), `d63d3f3d`, `d07fe567`, `2e4b9dc8`, `35c0fa9a`, `6f1fa0f7`, `218417ff`, `0d0f2ccc`.
- Must agree with: D-0036 "a `polars_` action is exactly Polars; no hidden choice; determinism a required parameter; no silent no-op"; D-0037 "Where Polars can do it, the Polars action and nothing else"; D-0058 `modif_join_where`; D-0091 plot names follow the same rule; D-0047 "Each registered action has its own test pair".
- Check (medium): run only the Polars-equality test file(s) of `b0f97acf` (`libs/transformer/tests/` equality tests) and read that none is still xfail. Pick 3 actions at random and read the action beside the Polars function. Cannot see: behaviour in versions of Polars other than 1.40.1.

**10. `derive_categories` removed "as dead"** (Routes: 4)
- What: the ledger line D-0038 is PROVISIONAL (agent's remark, not hers): "`derive_categories` is removed 'as dead' (a lookup is a `polars_join`)"; code in `d63d3f3d`.
- Risk: a function that real recipes used was removed on an agent's word. D-0062 says "the fragment that used the three removed actions is converted, not deleted".
- Check (medium): in `git show d63d3f3d^`, grep the shipped recipes for `derive_categories` and compare each result with the golden baseline rows of the same recipe (the baseline holds 76 entries; the old file `app/tests/golden/resfinder_abromics/old_after_derive_categories.tsv` is the old result). Cannot see: user recipes outside the repository.

**11. The rule for missing values (NA)** (Routes: 1)
- What: D-0042 (11-14): engine follows Polars; every filter step states `na: keep|remove`, no default; the screens preselect with a visible tick. Files `libs/utils/src/utils/na_choice.py`, `missing_values.py` were last changed 11-14 (ran, `route1.py`), the day of the decision; later builds touched the filter code.
- Risk: the tick in HOME and the `na` in the recipe step may follow different rules; D-0043 says the tick replaces "NA (missing)" as a value.
- Where: `412e7d4a`, `22a0dc14`, `dd356f12` (test pins the NA rule in three filter places; one "count" test was xfail).
- Must agree with: D-0032 (superseded), D-0042 "every filter step states `na: keep|remove`, no default", D-0043.
- Check (medium): run `test_na_choice.py` and `test_shiny_na_tick.py` only; then by hand: a filter step without `na` must be refused by the checker. Cannot see: NaN versus null on real data columns.

**12. Ties and order: the ResFinder rule, and a skipped test** (Routes: 1, 8)
- What: D-0087, D-0111 (tie: lowest accession, then first row), D-0112 (identity, then overlap), D-0113 (drop NaN first). Commit `2e4b9dc8` adds `pytest.skip("Polars gave the same order in 12 runs on this machine; the reason for the fixed order could not be shown here")` for a tie-order test. D-0059 says "both tie behaviours are tested before the wording is fixed".
- Risk: the tie-order test that D-0059 asks for is skipped on this machine, so the wording may rest on an untested case. The ResFinder recipe was changed on 11-16, after the decisions D-0111 to D-0113, by `7f4ea21a` and `fc73c6fd`.
- Where: `libs/transformer/src/transformer/actions/polars_rows.py` (`fa3da901`, `8bc7c64d`), `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml`.
- Check (medium): run the one skipped test with a case built to tie; run `app/tests/test_resfinder_abromics_fragment.py` against the stored old result; read the recipe's comment for D-0113. Cannot see: whether the ST22 data ever has ties (the decision says it is unlikely).

**13. Silent fallbacks in the engine** (Routes: 7)
- What: `except Exception: ... return False/continue` added in `libs/transformer/src/transformer/join_diagnosis.py` (3, commits `f8f39444`, `74485b0d`, `6a5af970`) and `libs/transformer/src/transformer/actions/polars_time_joins.py` (`b3308150`).
- Risk: each has a reason in its comment ("a side that cannot be read here is not the one to name"), but a failure of the diagnosis is hidden, not reported.
- Must agree with: D-0050 "No silent error: that is the rule".
- Check (small, reading): for each of the four, read what the user sees when the fallback runs (it should still show Polars' own error). Cannot see: a case no one imagined.

### Join rules

**14. One join-key rule, three callers, and a cast to text** (Routes: 7)
- What: `join_keys.join_key_problem` (`libs/utils/src/utils/join_keys.py:40`) is called by `data_assembler.py:82` (the build), `recipe_check.py:806` (the checker) and `join_designer.py:50` (Blueprint preview). `libs/transformer/src/transformer/actions/composite.py:57` still casts a key to String (`pl.col(col).cast(pl.String)`, "rank on text").
- Risk: the three callers wrap the rule in their own code (`_check_join_key_types`, `join_key_problems`, `check_join_keys`); D-0044 says no hidden cast of join keys to String.
- Must agree with: D-0044 "A join keeps the types the recipe declares; the hidden cast of join keys to String is removed"; D-0065 "One pure join-key rule ... called by the build, the Blueprint preview and the checker".
- Check (medium): run `app/tests/test_join_key_one_pin.py` (273 cases, `b16c97a3`); read `composite.py:57` and say which action uses it and whether it touches a join key or only a rank. Cannot see: a fourth copy under another name (I searched names with "join_key", "key_dtype", "cast_key" only).

**15. Self-joins** (Routes: 1)
- What: D-0066 "a join of a table with itself runs as written, with a clear warning"; D-0078 "Only the anti-join of a table with itself on the same key is an error; every other self-join is a warning" and the ledger says it was "Not built yet". Commits before it: `b27f89e4`, `38fa288e` (advice J12 "for every self-join"), `f37ba13d` (a self-join removed from a shipped recipe).
- Risk: J12 may still treat all self-joins alike. `f37ba13d` removed a join step from a shipped recipe: a result may have changed.
- Check (small + golden): read J12 in `recipe_check.py`; compare the golden entry of `AR1_MLST_Serotype_Virulence` before and after `f37ba13d` (rows, hash). Cannot see: self-joins in user recipes.

**16. The message for a refused `validate` (PROVISIONAL)** (Routes: 4)
- What: `join_diagnosis.py` and tests carry "D35b, PROVISIONAL" (ran: grep). Commits `6b189414`, `74485b0d`, `6a5af970`, `f8f39444`.
- Risk: the text names a cause. It must only say what Polars established (D-0059 style).
- Check (small): run `test_join_validate_diagnosis.py` and `app/tests/test_join_validate_orchestrator.py`; read the message for a non-unique key. Waits for: her yes on the wording.

### HOME, export, sessions

**17. HOME still has the old "My view" model** (Routes: 1)
- What: `app/handlers/home_theater.py` (32 commits, 5 days) is the screen. The intent document (DRAFT, not confirmed by her) lists this as E1: "My view", "Plot to show", Compare of the old model.
- Risk: D-0016, D-0019, D-0053, D-0093, D-0102 (two recipes, original never edited) were decided 11-11 to 11-15 and the build predates them. The ledger says stage 2 is not built, so this is expected; the risk is that something built since writes into the original recipe or does what the new decisions forbid.
- Must agree with: D-0102 "the ORIGINAL recipe ... never edited in the audit; the AUDIT recipe ... the export"; D-0040; D-0016; D-0019 "Exploration has ONE plot".
- Check (medium): grep every write to a recipe path in `app/handlers` and `app/modules` (`yaml.dump`, `write_text`, `open(..., "w")`) and list which can touch the original recipe file. Cannot see: runtime paths.

**18. The audit order function was built before the decision that confirms it** (Routes: 1)
- What: `307e6b4e` (11-15 18:59 local time, i.e. 17:59 UTC) builds `audit_steps_in_order` and `audited_frame` in `app/modules/t3_audit_engine.py:617-690`. D-0096 "Agreed a for both" is at 18:28 UTC the same day, after the build; its docstring says "DECIDED 2026-11-15 (Eve, S2-1)". Later: `8bf8a8fc`, `173faf20`, `45742491`, `bbacaac5`.
- Must agree with: D-0096 "Audit steps run in the RECORDED order ... (one function); the filter dialog stops offering a column that an earlier audit step dropped; a filter on a column dropped earlier is an error from the engine".
- Check (medium): run `app/tests/test_step_order.py` and `test_filter_dialog_after_audit.py`; read that `export_handlers.py:1072` and `:1206` and `home_theater.py:473,1340` all call `audited_frame`. Cannot see: the Compare pane and the plot-style steps.

**19. A filter on an absent column is skipped without a word** (Routes: 7)
- What: `app/modules/t3_audit_engine.py:550-552`: `if actual_dtypes and col not in actual_dtypes: continue` (issue #56). A second function `inapplicable_filter_rows` (`:469`) is defined and nothing calls it (ran: grep). At `:543` a failed schema read gives `actual_dtypes = {}` and the condition then uses the stored `dtype` of the filter row.
- Risk: D-0050 "No silent error"; ADR-104 point 7 says the type is read from the table each time. The audit path is safe (`audited_frame` raises first); the exploration path (`home_theater.py:1335`) is not.
- Must agree with: D-0050; D-0014 "Exploration filters change the table on every view"; D-0096.
- Check (small, one run): apply an exploration filter on a column that only exists in T1 while viewing T2 and see what the user is told. Cannot see: whether a message is shown elsewhere.

**20. Filter pickers: eight choices of an agent** (Routes: 4)
- What: FILTER-PICKERS-1, merged `a386422a`: P1 to P8 and L10 are "PROVISIONAL (an agent's choice, waits for Eve)" in `tasks.md:97-106`, `t3_audit_engine.py:226-232,303,376`, `filter_and_audit_handlers.py:46-104`, `filter_values.py:311,357`.
- Risk: D-0061 decided only: date picker, two-choice control for true/false, no text greater/less, every type usable. Everything else (three time boxes, duration units, strict date text, 1000-value limit) is not hers.
- Check (small): list the 9 points; a reviewer confirms none changes a result silently (a value finer than the column unit is refused, not cut). Cannot see: how it feels to use.

**21. The filter condition is one function, but the export translates it again** (Routes: 7)
- What: `utils.filter_values.filter_condition` (`filter_values.py:373`) is called by `t3_audit_engine.py:448,463,555`, `transformer/actions/modified.py:70` and `viz_factory.py:258` (ran: grep). The export turns an audit step into a recipe step in `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:91-160` with its own rule on operators (`_TRANSLATABLE_OPS`, an `eq` with a list becomes `not_in`).
- Risk: the table and plot use the shared rule; the exported recipe uses the translator's own logic. They can differ (`test_modif_filter_vs_home_filter.py` exists to catch this).
- Must agree with: D-0065-style single source; D-0005 "Export = Result + audited steps"; agent_principles 2: what a figure shows is what the export contains.
- Check (medium): run `app/tests/test_modif_filter_vs_home_filter.py` and the translator tests; add two cases not in them (a value with a list and `ne`; `between` open ends). Cannot see: operators the audit does not offer yet.

**22. The export was built on 11-09 and decided again later** (Routes: 1, 2)
- What: `app/handlers/export_handlers.py` (22 commits) and `app/modules/exporter.py`. Built first by the 11-09 session without a Co-Authored-By line: `d0d4f379` ("Mode 1 never carries the recipe"), `682fdfe2`, `4bf00271`, `c2b70616`, `e6abc782`, `6515d2a4`.
- Risk: the intent document (DRAFT) lists E3: plots whose steps cannot be translated "are left out of the re-runnable recipe, with a warning" (`export_handlers.py:1303-1311`), and E12: `docs/user_guide/understanding_your_export.qmd:12` says the standard bundle never contains the recipe. D-0102 says "the export is the audit recipe". D-0083 (initials and date on the steps) and D-0088 (export refused until re-based) came after.
- Must agree with: D-0005 "Export = Result + audited steps with reason; exploration never exported; export refuses when files changed since the view"; D-0013 "two export modes ... `effective_run.yaml` always"; D-0083; D-0088; D-0050.
- Check (medium): run `test_export_refusal.py`, `test_export_provenance.py`; read `export_handlers.py:1295-1315` and decide if "left out with a warning" breaks "nothing is hidden". Cannot see: the export on a real two-plot project.

**23. The session screen swallows errors** (Routes: 7)
- What: `app/handlers/session_handlers.py:267, 281, 300`: `except Exception: pass` around restore, delete and label (added by `c8c62dc5`, 11-09).
- Risk: a failed restore of a session shows nothing. D-0050 and D-0018 (sessions flag).
- Check (small): read the three blocks; force `_restore_session` to raise (small script) and see if the user is told. Cannot see: the older handlers outside the range.

**24. The recipe gate at HOME start, and the biggest HOME file** (Routes: 2)
- What: `home_theater.py` 32 commits; `app/modules/cache_keys.py`, `orchestrator.py`, `recipe_gate_handlers.py`: `12019cdc`, `53a68cb6`, `0406d2ef`, `d1b13d68` (11-15), several without a task name.
- Must agree with: D-0009 "HOME checks every recipe at start; a failing one is not selectable, shows reason + contact"; D-0079 "A recipe with an error is not accepted in HOME".
- Check (medium): run `test_recipe_gate_handlers.py` and `test_gate_gap.py`; start with a recipe holding one error and one warning; the first is not selectable. Cannot see: a recipe that breaks only when a plot is drawn.

**25. The seed in HOME** (Routes: 1)
- What: 11-09 `e6abc782` (automatic seed bookkeeping, REPRO-SEED-2) and `dc49a7e5` (reshuffle control); 11-15 `579499f0`, `551462d3`, `39ed8983` ("Reshuffle follows the resolver's precedence; a way back from a pin"), after D-0056 "HOME draws no seed per session".
- Risk: a Reshuffle button still draws a seed. D-0056 "the session's seed is used in the export; HOME draws no seed per session".
- Check (small): read what Reshuffle does (`home_theater.py` near `plot_seeds.py:61`) and what the export writes for the pin (`9a57478e`). Waits for: her view on whether Reshuffle is a pin she chooses (user choice) or a draw.

### Plot library

**26. The plot library: heavy change and silent paths** (Routes: 2, 7)
- What: `libs/viz_factory/src/viz_factory/viz_factory.py` 20 commits on 3 days, `plot_config_resolver.py` 16, `geoms/core.py` 8, README 14. New `checked_plot.py` (`9caab17a`) has five `except Exception:` with `return None/False` or `continue`.
- Risk: D-0051 "silent paths become errors; one error form"; some of these fallbacks may hide the very errors it wants to show. Several `fix(viz)` commits name no task (`4f7de1ba`, `42189efe`, `64304ab8`, `894626b7`).
- Check (medium): read each `except` in `checked_plot.py` (lines 94, 149, 182, 225, 237, 280) and say what the user sees; run `libs/viz_factory/tests/test_no_silent_error.py`. Cannot see: plotnine behaviour in other versions.

**27. Seed rules S1 and S3 are PROVISIONAL and change D-0004** (Routes: 1, 4)
- What: `viz_factory.py:34,86,104,228`, `plot_config_resolver.py:255-267`, `recipe_check.py:958,979`: "PROVISIONAL (S1/S3)". `random_state: null` and "random" are refused; `plot_defaults.random_state` is the one seed of the recipe. D-0004 (11-05) said "null/random = new each render", now "replaced in part by D-0056".
- Must agree with: D-0052 "a seed fixed in the recipe HOLDS"; D-0056 "The seed is fixed at 0 by default and written in the recipe; every seed that is used is written".
- Check (medium): run `libs/viz_factory/tests/test_plot_seed.py` and `app/tests/test_plot_seeds.py`; render one jitter plot twice and compare pixels. Waits for: her yes on S1/S3 (ledger has no DECIDED line for them).

**28. Defects known and left open, pinned by strict `xfail`** (Routes: 8)
- What: 9 strict xfail marks at HEAD in 6 files (ran): `app/tests/test_shiny_blueprint_known_defects.py`, `app/tests/test_writers_emit_format_one.py`, `libs/id_reconciliation/tests/test_suggested_steps.py`, `libs/viz_factory/tests/test_no_silent_error.py`, `test_registry_audit_vs_plotnine.py`, `test_every_yaml_example_renders.py` (e.g. `guide_label` calls `guide_legend(labels=...)`, which plotnine refuses; `BP-SAVE-TUPLE-1`).
- Risk: each one is a deviation that is known and not fixed; a fix "turns the xfail into a failure".
- Must agree with: D-0050; D-0051.
- Check (small): list the 9 reasons and ask whether each is on `tasks.md`. Cannot see: defects with no test.

### Gallery

**29. "All gallery recipes work, nothing left out"** (Routes: 1)
- What: D-0077 "ALL gallery recipes and examples are rewritten ... and every one works; nothing is left out". Commit `52c9ac6a` converted "the 33 convertible examples"; `5363c930` converted `beeswarm_sina`; `26c40302` hides an example that fails the check ("show why it is left out"); `tasks.md:218` says an example left out at start has no screen element yet. There are 34 example folders (ran: `ls -d assets/gallery_data/*/`).
- Risk: one of 34 may be left out; this is the rule "left out" against D-0077.
- Check (medium): run the gallery check (`app/tests/test_gallery_full_check.py`) and count examples listed vs 34; any left out must have a reason in the screen. Cannot see: if each picture is right.

**30. Stored pictures of the gallery moved** (Routes: 6)
- What (ran, `git log -- libs/viz_gallery assets/gallery_data`): `abc6a186` (11-14) changed the preview pictures of 8 examples (boxplot x2, jitter_strip, point x2, tile, violin x2) with the message "review each, drop what is not wanted"; `d81ce81f` re-sized 3 whose picture is "unchanged"; `5363c930` new preview for `beeswarm_sina`. No record that she looked at them.
- Must agree with: D-0077 "The gallery screen works as before"; D-0008 gallery is a static reference browser; D-0004 same recipe, same picture.
- Check (medium): open the 8 old and 8 new pictures side by side (old = `git show abc6a186^:path`). A reviewer states the reason of each difference (seed, theme, jitter, rename). Cannot see: pixel differences below what an eye sees.

### Blueprint

**31. Blueprint and the third tier (T3)** (Routes: 1)
- What: D-0063 (11-15): "Blueprint MAY author the plot entry's tier 3". Before: her words 2026-11-08 "No T3 should exist in blueprint" (intent doc table, line 92, DRAFT). The translator `t3_translator.py` forks a join per plot (E2) and `TIER3_READ_BY_ENGINE = False` (`recipe_check.py:47`) makes the checker refuse a non-empty `steps.tier3` (E4).
- Risk: the 11-09 translator design (`6515d2a4`) is older than D-0063, D-0115 and D-0120 ("the audit does not change the steps of the plot").
- Check (small, reading): read `t3_translator.py:30-40` and `:213` against D-0063/D-0115; say if "fork the join" is still the design. Cannot see: the unbuilt tier-3 reader.

**32. Blueprint join preview: expected errors only** (Routes: 3)
- What: `a27e35b4` "an unexpected error in the join preview is logged and does not end the session", `5d9c5bdb`, `bd691703`, `9ebc8449` in `blueprint_handlers.py` (21 commits, 4 days).
- Must agree with: D-0068 "The Blueprint join preview catches only the expected errors; a programming error is not shown as the user's mistake".
- Check (small): run `app/tests/test_join_preview_crash_app.py` and `test_join_preview_errors.py`; confirm a programming error is logged and shown as "program error", not "your recipe". Cannot see: the log reaching a person.

### Rule files, agents, hooks

**33. Rule-file edits with no record of her yes** (Routes: 5)
- What: of 27 commits that touch `.claude/rules`, `agents`, `hooks`, `CLAUDE.md`, `settings.json` (ran: `route5_commits.txt`), these 6 are named in neither `RULE_FILE_CHANGES.md` nor the ledger nor tasks: `55e578f5` (the guard refuses Bash that writes files, `CLAUDE.md`), `b055ba07`, `143ae2d4` (`ui_implementation_contract.md`), `0db0b49e` (`rules_agent_role_bioscientist.md`), `0821ef6f` (`rules_app_structure.md`), `c32e7ea2` (`rules_data_analysis_recipe_structure.md`, 13 lines).
- Must agree with: D-0104 "no rule file is changed without her agreement; every rule-file change is kept in one dated, traceable list".
- Check (small): per commit, find her sentence in the chat or the ADR that asked for it; none = list for her. Cannot see: chat turns before 11-09.

**34. Rule-file edits that the list itself marks "no confirmation"** (Routes: 5)
- What: `RULE_FILE_CHANGES.md` lines 42-43 say 7 applied edits have no confirmation and 5 name her only inside the rule text (read). Commits named there: `f8636ff4`, `22a0dc14`, `89043503`, `74abfc48`, `2b13bbdb`, `772881f3`, `873cf3a4`, `58e56842`, `c454bcf6`, `6521f966`, `6349ba7f`.
- Risk: `74abfc48` replaced a rule ("every library needs an orchestrator integrity suite") by the pytest gate.
- Check (small): nothing to run; send the five in the list to her as one numbered question. Cannot see: other edits in the same files before the list was made.

**35. The guard hook and the agent files** (Routes: 5)
- What: `.claude/hooks/coordinator_guard.py` (`6e318386`, `55e578f5`, `d64f0cdf`, `ee4f1eac`, `f1f70353`) has an `except Exception: pass` (`6e318386`). The decision-compliance commits `3a3aa73d`, `d64f0cdf` are covered by D-0125 (ledger line, read).
- Risk: a hook that fails silently allows what it should refuse.
- Check (medium): run `app/tests/test_coordinator_guard.py` only; read the one `pass`. Cannot see: the hook inside a real session.

**36. Contradictions already listed in the intent document, section (e)** (Routes: 1)
- What: that document is a DRAFT, not confirmed by her. Its section (e) lists E1 to E17. Code spots: E1 (old model), E2/E3 (translator, plots left out), E4 (tier 3 not read), E5 (no undo in `audit_stack.py`), E7 (`developer_raw_yaml` in rule file `rules_ui_dashboard.md:13` and `ui_implementation_contract.md`), E10 (HO text on missing values vs ADR-103/104), E12 (docs on the export), E13/E14 (UML diagrams), E16, E17.
- Check (small): for E7 run grep `developer_raw_yaml` in active rule files (not tombstones); for E12 read `understanding_your_export.qmd:12`. The list is not mine to correct; reviewers confirm each is still true at HEAD.

### Golden baseline, stored pictures, equality findings (Route 6)

The baseline `app/tests/golden/baseline.json` moved in 6 commits (ran: `baseline_diff.py`; 76 entries: table records of each recipe, tiers T1 and T2 and plot data). Each record holds column names with types, row count, and a content hash (sha256). I compared the JSON before and after each commit.

| Commit (date) | Added | Removed | Hash changed | Column list changed | Rows changed | Reason in the message |
|---|---|---|---|---|---|---|
| `18e5cda6` (11-13) | 76 (first file) | - | - | - | - | "golden baseline of the tables of the shipped recipes" |
| `99a14148` (11-14) | 0 | 0 | 7 | 7 | 3 | "two deliberate changes": demo recipe, ST22 phenotype rename |
| `ce373923` (11-14) | 3 | 3 | 0 | 0 | 0 | not given; the 3 are plot ids `plot_A_..` to `plot_a_..` (lower case) |
| `1547aab9` (11-14) | 0 | 0 | 0 | 14 | 0 | `sample_id` Categorical to String in 14 records |
| `9490490d` (11-15) | 0 | 0 | 2 | 2 | 0 | DEC16, issue #77: a schema plotted directly runs its own tier 2 |
| `2ac83ddb` (11-15) | 0 | 0 | 0 | 71 | 0 | "column type text only" (CATEGORICAL-MIGRATION-1) |

**37. Move `99a14148`: 7 hash changes** (Routes: 6)
- What: `ST22_Anchor` T1, T2 and 2 plots get one more column (11 to 12, `phenotype`, a rename step); `demo_abromics` join T1/T2 30 to 28 rows and 4 to 5 columns; the plot `demo_st_by_source` had an error entry before and now 28 rows.
- Which decision allowed a changed result: D-0047 "demo recipe corrected (Eve)" for demo_abromics (read, ledger). For the `ST22_Anchor` new column I found no decision (the message says "the old contract named a column that never existed and was skipped silently", so it is a correction of a silent skip, D-0050). 
- Check (small): read the diff of `app/tests/golden/baseline.json` for those 7 keys; confirm the 28 rows of the join against the data (MLST and metadata). Cannot see: whether 30 to 28 dropped right rows.

**38. Move `ce373923`: three plot ids renamed** (Routes: 6)
- What: `figshare_integration` plots `plot_A/B/C...` become `plot_a/b/c...`; my script does not compare the hash across the rename.
- Check (small): compare the 3 hashes by hand (one `git show` each). Cannot see: other places that still use the capital letters (HOME selection, saved sessions).

**39. Moves `1547aab9` and `2ac83ddb`: types changed and the hash did not move** (Routes: 6)
- What: 85 record-column lists changed (14 + 71) while no hash changed (ran). The hash covers the values, not the types. So a wrong type conversion that keeps the text the same is not caught by the hash.
- Must agree with: D-0057, D-0098 (levels order is no problem if counts per category are equal; Enum where order matters).
- Check (medium): `app/tests/golden/categorical_content_before.json` and `categorical_counts_before.json` pin the content; run `app/tests/test_categorical_migration.py` only; compare the 71 type changes with the list in D-0098 (Enum for figshare `predicted_phenotype`, Float64 for stress value). Cannot see: changed ORDER of categories on a plot axis.

**40. Move `9490490d`: one table and one picture changed** (Routes: 6)
- What: `ResFinder` T2 and plot `amr_heatmap` of `1_test_data_ST22_dummy` get a new column `total_gene_count` and a sort by it; the picture changed. Decision named: DEC16 (D-0034 "schema's own tier2 applied").
- Risk: this is a changed result in a plot that she may know by its old look.
- Check (medium): show her the old and new picture of `amr_heatmap`; confirm the count of 70 rows unchanged. Cannot see: other plots using ResFinder T1.

**41. Equality tests' stored findings** (Routes: 6)
- What: `app/tests/equality/FINDINGS.md` and `open_findings.py` (`8c172bd2`, 11-15; `2e0be951`, 11-16): F1 "corrected" and moved to the normal run (73 passed); F2 still open: 5 comparisons where the engine and the hand-written Polars differ today, not run by default (`EQUALITY_FINDINGS=1`). One question open for her: does `unknown[...]` count as a class.
- Risk: 5 known differences between the engine and plain Polars sit outside the default run.
- Check (medium): run with `EQUALITY_FINDINGS=1` once and read the 5 differences; say which D-number each breaks (D-0036 "a polars_ action is exactly Polars"). Cannot see: scenarios the hand-written side does not cover (one recipe, the ST22 dummy data).

### Tests changed (Route 8) and fix claims (Route 3)

**42. Large removal of assertions in the library tests** (Routes: 8)
- What: `6f3ec110` (11-13) removed 96 assert lines and added 42, and deleted 5 test files (`test_filter_actions.py`, `test_metadata_validator.py`, `test_replacements_by_polars_steps.py`, `test_step_actions.py`, `test_validate_types.py`); message "the old action tests are replaced". `8f2dfe7d` removed 17, added 5; `d07fe567` 8 and 5.
- Must agree with: D-0031 "tests adapted before they run"; agent_principles 5 "Remove what a change invalidated at the moment it is detected".
- Check (large, one reviewer): for each deleted file, find the replacing test of the same behaviour (e.g. `test_action_recipe_pairs.py`); a behaviour with no replacement is the finding. Cannot see: an assertion that was wrong before.

**43. Seed tests changed to follow the decision** (Routes: 8)
- What: `551462d3` removed 65 and added 35 assert lines; `54e6979f` 31 and 14; `4d2c0f75` 23 and 22. The new asserts follow D-0056 (provisional S1/S3).
- Risk: the tests now agree with a build that waits for her yes (entry 27).
- Check (small): read the removed assert lines (`git show 551462d3 -- app/tests`) and sort: (a) rule changed by decision, (b) loosened. Cannot see: the intent of an author.

**44. Test data and debug scripts deleted** (Routes: 8)
- What: `74abfc48` deleted old test data and `libs/transformer/tests/debug_pipeline.py`, replaced by a pair per action; `99a14148` deleted `app/tests/audit_export_bundle.py`, `libs/viz_gallery/tests/debug_gallery_submission.py` (D-0046 dead submission code); `6a5af970` deleted `libs/transformer/tests/test_join_validate_message.py` (the later `test_join_validate_diagnosis.py` is probably its replacement: reasoned); `8f2dfe7d` deleted `app/tests/test_column_names_through_the_steps.py` (the name is in the range's file list; it is absent at HEAD: ran `ls`).
- Check (small): per deleted file say where its cases went. Cannot see: untested behaviour.

**45. Commits that say "fix" or "no longer" with no test in the same commit** (Routes: 3)
- What (ran, `route3.py`): of 145 non-merge commits whose message has fix, no longer, refuses, equal, identical or tested and that touch code, 135 hold a test file in the same commit. A sample of 40 spread over the areas: all 40 have one. 10 have none: `173faf20`, `310495fa`, `fe2a812e`, `1bcb43d3`, `51adcbf0`, `579499f0` (HOME, PLOT), `8a534a4c`, `db9d5113`, `f84b15a9` (recipes), `143ae2d4` (blueprint, home). Tests in the next four commits: `310495fa` 0 and `51adcbf0` 0.
- Risk: "a test file in the commit" does not prove that the test fails without the change (agent_principles 5).
- Check (medium): for the 10 and for 5 of the sample: revert the source hunk in a scratch copy and run the one test; it must fail. Cannot see: tests that exist but check nothing.

## Route count (how many entries each route gave)
- Route 1 (decision after a build): 16 entries (2, 3, 4, 5, 6, 11, 12, 15, 17, 18, 22, 25, 27, 29, 31, 36)
- Route 2 (files with many commits, commits naming no task): 6 (1, 7, 9, 22, 24, 26)
- Route 3 (claims more than the diff): 3 (9, 32, 45)
- Route 4 (PROVISIONAL): 4 (10, 16, 20, 27); the full list of the PROVISIONAL builds is below
- Route 5 (rule files and hooks): 3 (33, 34, 35)
- Route 6 (golden baseline, pictures, equality findings): 6 (30, 37, 38, 39, 40, 41)
- Route 7 (same rule twice, silent fallbacks): 8 (3, 8, 13, 14, 19, 21, 23, 26)
- Route 8 (tests weakened): 5 (12, 28, 42, 43, 44)

Route 4, all PROVISIONAL builds found (ran: grep in commits, code, records): FILTER-PICKERS-1 P1-P8 and L10 (entry 20); seed S1 and S3 (27); join-validate message D35b (16); advice ST14 and ST15 (D42, D43, `a7520e9c`, `9f294e11`; text now D-0099 DECIDED, wording of top_k PROVISIONAL, `tasks.md:418`); advice texts ADVICE-TEXTS-1 (`806dc852`); EQUALITY-CHECK-1 (all tests, `3eb954fc`); JOIN-COUNTS-1 (not built); stage-2 spec v0.2 (`5e610429`, a document); D-0038 `derive_categories` removal (10); the plot proposals of D-0131/D-0133 (not built). Records say "waits for Eve" for each.

## Route 1 detail: the files last changed before a decision of the same area (ran, `route1.py`)
Day level only (the ledger gives a time for some decisions, the files only a day). Per area: files that implement it and were last changed before the latest DECIDED line of that area:
- Recipe format: `formula_check.py`, `recipe_loader.py`, `recipe_paths.py` (last change 11-13; 7 decisions since).
- Engine: 23 of 25 files; the oldest `libs/ingestion/src/ingestion/__init__.py` and `excel_handler.py` (April, never touched), `metadata_validator.py`, `polars_types.py` (11-13); most others 11-14 or 11-15 against 9 to 17 decisions of 11-14 to 11-16.
- Joins: none (3 files, all changed after).
- HOME: `audit_stack.py`, `home_theater.py`, `cache_keys.py`, `orchestrator.py`, `view_badge.py` (11-15; 5 decisions of 11-15 and 11-16 since); `data_import_handlers.py` (11-13).
- Plots: 22 of 23 (the factory last changed 11-15; D-0091 and D-0092 of 11-15 and later).
- Gallery: `gallery_*.py`, `taxonomy.py` (11-14) against D-0077 and later.
- Blueprint: `widget_text.py` (11-13), `new_recipe.py` (11-14), `agent_adapter.py`, `agent_tool_parser.py`, `blueprint_mapper.py` (11-07).
- Rules: 21 of 33 rule files not touched since 11-07 to 11-15 (they are the ones D-0104 says are to be repaired).
These feed entries 2, 3, 11, 17, 18, 25, 29, 31.

## Route 2: the 30 files with most commits (ran; commits, distinct days)
tasks.md 122/7; home_audit_reading_guide.md 55/4; home_audit_steps.md 54/5; recipe_format_spec.md 52/4; architecture_decisions.md 48/6; handoff_active.md 45/8; `app/handlers/home_theater.py` 32/5; `libs/utils/src/utils/recipe_check.py` 30/4; docs/UML/app.mdj 27/3; `export_handlers.py` 22/3; `docs/appendix/transformer_actions.qmd` 21/4; `blueprint_handlers.py` 21/4; `t3_audit_engine.py` 20/4; `data_analysis_recipe_validator.py` 20/5; `viz_factory.py` 20/3; `filter_and_audit_handlers.py` 16/4; `plot_config_resolver.py` 16/3; uml_model_plan.md 15/4; dependency_index.md 15/6; home_preview_filters.md 15/4; actions_and_polars_2026-11-13.md 15/1; `libs/viz_factory/README.md` 14/3; `app/tests/test_export_download.py` 14/3; `data_assembler.py` 12/3; `1_test_data_ST22_dummy.yaml` 11/5; home_stage2_mechanism_spec.md 11/4; `wrangle_studio.py` 11/4; `test_shiny_smoke.py` 11/4; `action_names.py` 11/3; `test_action_recipe_pairs.py` 11/2.
Code files among them are entries 1, 9, 17, 18, 22, 24, 26. `wrangle_studio.py`, `data_analysis_recipe_validator.py`, `test_export_download.py` and `test_shiny_smoke.py` are not given their own entry: they are checked inside entries 1, 22 and 24.
Several sessions on one file: `session_manager.py`, `export_handlers.py`, `home_theater.py`, `t3_translator.py` and `orchestrator.py` were each touched by 4 different Co-Authored-By models (ran).

## C. Proposed order of the checks
Order follows what the next HOME stage builds on (recipe format and checker, engine, joins, then HOME with export and audit). Size: small = reading, medium = one short run, large = a group of runs. Agent kind: Sonnet reviewer (read-only, one area) unless stated.

| Order | Entries | Size | Agent |
|---|---|---|---|
| 1 Recipe format and checker | 1, 2, 5, 4 | medium | Sonnet reviewer, one |
| 2 Engine (types, NA, ties) | 11, 12, 9 (3 actions), 3 | medium | Sonnet reviewer, one |
| 3 Joins | 14, 15, 16 | medium | Sonnet reviewer, one |
| 4 HOME audit, filter, export | 18, 19, 21, 22, 17, 25 | large | one Sonnet reviewer per entry, at most 3 at once; entry 22 with Opus (many files) |
| 5 Baseline and pictures | 37, 38, 39, 40, 41, 30 | medium | Sonnet reviewer (Opus for 40) |
| 6 Rule files | 33, 34, 35 | small | Sonnet reviewer; then ONE list for her |
| 7 Tests weakened and fix claims | 42, 43, 44, 45, 28 | large | one Sonnet reviewer for 45 (reverts), one for 42 to 44 |
| 8 Plots, gallery, Blueprint, rest | 26, 27, 29, 31, 32, 20, 23, 24, 13, 8, 10, 6, 7, 36 | large | Sonnet reviewers, one area at a time |
Entries 20, 27, 16, 10 wait for her words, so they end in a question, not a fix.
Can run in parallel: 1 with 5 (own files); 6 with anything. 3 needs 2 only for entry 14 (the cast at `composite.py:57`).

## D. What this mapping cannot see
1. Anything decided only in chat and never written in the ledger: I measured against written lines only.
2. Behaviour at run time: I read code, grepped, and ran two small scripts on git; I did not run the application or the tests.
3. A rule applied in one place and not in another when the two copies have different names and different words: I searched names, not meaning.
4. Same-day order of a decision and a build: the ledger gives a time for some, the file history gives a time zone different from the ledger (commits +01:00, ledger UTC).
5. Commits before 11-09 and the base (DEC01-DEC49 rows were read for names only, not one by one against the code).
