# Build brief: working protocol and package details for the HOME work

**Written for:** any Claude session that builds the packages P0-P12 of `.claude/design/home_stage2_mechanism_spec.md` section 5 (the plan), starting with P0, P1, P3, P8. **Owner of decisions:** Eve. **Status:** current since 2026-11-13; the earlier version (with the work-package history) is `outdated/home_exploration_build_brief_2026-11-11.md`.
**Rule that overrides everything below:** do not break what works; do not do work that the agreed audit design would make Eve undo. A package is started only on Eve's signal.

**Read first:** `CLAUDE.md` (section 9, no guessing), `.claude/design/spaces/HOME.md`, `.claude/design/home_audit_reading_guide.md`, `.claude/design/home_preview_filters.md`, ADR-098 and ADR-099, `.claude/workflows/design_review_personas.md`, `.claude/tasks/tasks.md` (the task lines say what is open).

## 1. Working protocol (binding)

**S1. Baseline first.** `git status`, `git log --oneline -15`; run the headless suite and note the count (1652 passed on 2026-11-13). The browser gate is about 7 minutes; `TestRecipeSwitchPlotRender` and a few others are timing-flaky (issue #72, task `TEST-FLAKY-1`): rerun alone before blaming your change.
**S2. One package = one commit, tests included, revertible alone.** After each package run the headless suite; after P1, P3 and P8 also the browser gate. If the gate is red and the cause is not clear within a few minutes, revert that commit and report; do not pile fixes on top.
**S3. Tests first** (`TEST-ADAPT-1`): tests that fail for the right reason on today's code, then the code. Every rule you add must be breakable in a test: break the code once, see the test fail, restore it (mutation check). Edge cases in every test set (`rules_verification_testing.md` section 9).
**S4. Frozen until the audit packages (P9-P11) replace them** (ask Eve if a package seems to need one): the audit screen and its code (`audit_stack.py`, the propagation dialog and audit-step code in `filter_and_audit_handlers.py`, `t3_audit_steps_by_plot`), the export and reproducibility code (`export_handlers.py`, `exporter.py`, `bundle_importer.py`, `libs/blueprint_arch/**` including `t3_translator.py`, `orchestrator.py`, `cache_keys.py`), the header strip as built, the right sidebar, Blueprint, Gallery, Test Lab, `config/app_features/*`, `sidebar_registry.py`, `CLAUDE.md`, the UML model (tell Eve when a diagram becomes wrong). Registered transformer actions (`libs/transformer`) change only with Eve's OK and only together with their consumers.
**S5. Compatibility until M1.** The stored filter row stays `{column, op, value, dtype[, closed]}` with the operators `eq ne gt ge lt le in not_in between`; keep the signatures of `_apply_filter_rows`, `OP_WORDS`, `op_choice_label`, `describe_filter` (`app/modules/t3_audit_engine.py`); audit steps, `t3_steps.yaml`, ghost files and `home_state` keys stay byte-compatible. New logic goes into pure, headless-testable modules (no Shiny); the recipe graph and the step compiler will absorb them. Existing recipes must give the same data.
**S6. Before editing a function, list its consumers** (grep) and re-run the tests that pin it. Consumers of the filter engine: `home_theater.py` (preview and plot), `export_handlers.py` (`audited_frame`, `T3_data_<plot>.tsv`), `libs/viz_factory/.../viz_factory.py` (its own copy of the filter code, about line 171), the translated actions that the reproducibility export re-runs (`t3_translator.py` -> `libs/transformer`).
**S7. Tell Eve about every user-visible behaviour change before it lands.**
**S8. Stop and ask when** a package needs a frozen file; a test you did not touch fails; the code differs from this brief; you are about to guess a default; a number here does not match what you see.
**S9. Rules from `CLAUDE.md` and Eve's global rules.** Issue first, fix second, close with the evidence; commit on `dev`, Conventional Commits, footer `Refs: evezeyl/SPARMVET_VIZ#N` (never a bare `#N`, never `Fixes`); auto-commits are pre-approved here; stage files by name. Scratch in `tmpAI/`; `tmp/` only for `@verify` evidence, then stop ("Data/Plot ready in tmp/... Waiting for @verify"). Session end: `@deps` blocks, `build_dep_graph.py`, `audit_docs_sync.py`, `audit_uml_model.py`, a line in `.claude/logs/audit_YYYY-MM-DD.md`, a handoff entry (append only). Eve is not a native English speaker: correct her spelling, one short line. Code comments say WHY; no emojis in Python.

**Commands.** Dev server: `PYTHONPATH=. SPARMVET_APP_FEATURES=developer ./.venv/bin/shiny run app/src/main.py --reload --port 8123`. Headless: `PYTHONPATH=. ./.venv/bin/python -m pytest libs app/tests --ignore=app/tests/test_shiny_smoke.py --ignore=app/tests/test_shiny_smoke_blueprint.py --ignore=app/tests/test_export_download.py --ignore=app/tests/test_every_app_features_starts.py -q`. Browser gate: `PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py app/tests/test_shiny_smoke_blueprint.py app/tests/test_export_download.py app/tests/test_every_app_features_starts.py -q`.

## 2. Issue protocol for parallel sessions

Issues on GitHub (`gh ... -R evezeyl/SPARMVET_VIZ`, never the default repo) are the shared record.
1. **Read first:** the issue and all its comments (`gh issue view N -R evezeyl/SPARMVET_VIZ --comments`) and its "Done when" boxes. If the issue text is wrong, say so in a comment and correct it.
2. **Claim:** one comment `CLAIMED <date> by <session name from -sessionname>: <package>; files I will edit: <list>; frozen files I will not touch: <list>.` One owner per file; a file in another open claim means wait or ask Eve.
3. **Sub-issues:** a piece that is not the issue's own problem gets its own issue (one problem per issue), first line `Part of #N`, added to the parent's checklist.
4. **Progress:** comment at each commit (hash, one line) and when blocked or when something differs from the brief.
5. **Done:** tick a "Done when" box only for what you verified in this session; comment `DONE: what changed (files); evidence (tests with counts, mutation check, pictures looked at); what was NOT done and why; commits`; close only when every box is ticked or moved to a sub-issue.
6. **Record:** move the task line of `tasks.md` to the archive; the issue, `tasks.md` and the handoff say the same thing.
7. Never edit or close an issue claimed by another session (comment instead); never mark done on a test you did not run; never leave a claim without a note when you stop.

## 3. The QA canaries (a safety net; extend it)

`1_test_data_ST22_dummy` has a group **QA Canaries** (not for publication). Each isolates one failure mode; the correct numbers are computed in `app/tests/test_qa_canaries.py` from the RAW tsv files, not through the engine, and printed in the plot subtitle. Run it before and after every package: `PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_qa_canaries.py -q` (3 s).

| Canary (collection / plot) | Known answer | Use it for |
|---|---|---|
| `QA_AMR_per_sample` / `qa_amr_genes_per_sample` | T1 long 74 rows, T2 42 samples, 4 with 0 genes, 70 genes; T1 and T2 differ on purpose | stage tests (a gene filter exists at T1 only); samples that vanish; the audit reach tests |
| `QA_ST_with_NA` / `qa_sequence_type_missing` | 42 samples, 2 missing sequence types (drawn as "nan") | P1: `!=` and none-of on a column with missing values |
| `QA_year_types` / `qa_year_label` | year is Float64 (2022.0); label is text "2022" (9), "2023" (8), "2024" (25) | filter value types (`in` on text, `>=` on the number); the ".0" trap |
| `QA_L50_integer` / `qa_l50_integer` | Int64 values 4 to 14, 42 samples | P1: `L50 >= 8.5` keeps 9 and not 8; `< 8.5` keeps 8; `= 8.5` nothing |
| `qa_facet_by_mapping` (on `QA_year_types`) | 3 panels: France, Germany, Norway | #65 stays fixed |
| `QA_fanout_exhibit` / `qa_fanout_rows_per_sample` | T1 1731 rows, up to 192 rows for one sample: a DEFECT shown on purpose | the many-to-many check (#68) must flag this collection and no other canary; change its test on purpose when #68 is built |
| `QA_aggregated_no_key` / `qa_aggregated_no_key` | T1 42 rows with `sample_id`; the T2 the plot reads has 9 rows (country x year) and no `sample_id`; counts sum to 42, Norway 2024 = 19 | the audit reach tests (#60): a plot a "remove sample X" step cannot reach by filtering its own data |
| `QA_population_zscore` | a population-dependent step: the order of steps changes the result | `TEST-ORDER-1`, the audit order tests |

Rules for canaries: one failure mode each; the answer is computed independently of the engine; the expected numbers are in the plot subtitle; a plot id starts with `qa_`; every new canary gets a test and a mutation check. Add yours to this table.

## 4. Package details (verified 2026-11-11; re-verify before use)

### P1 - integer thresholds (#62) `HOME-EXPLORE-1` `[sonnet/medium]`
**Verified problem:** on an `Int64` column [89, 90, 91] the audit engine and VizFactory truncate (`int(float(value))`): `>= 90.5` keeps 90, `< 90.5` keeps only 89, `= 90.5` keeps 90. The registered actions the reproducibility export re-runs (`filter_range`, `filter_lt`, `filter_eq`) compare correctly (`>= 90.5` -> 91; `< 90.5` -> 89, 90; `= 90.5` -> none): so today the figure and the reproducibility bundle disagree. The actions are the reference; do not change them.
**Files:** `app/modules/t3_audit_engine.py` (`_coerce_to_dtype` and its callers), `viz_factory.py` (the coercion block only), a new pure module in `libs/utils/src/utils/`, tests. **Do:** one shared implementation of the filter-value coercion (compare as float when the value is not an integer); both consumers call it; remove the second copy. Together with `FILTER-DTYPES-1` (every content type) and `NA-RULE-63`.
**Tests:** the table of #62 for every operator and `.0`, `.5`, integer values; an equivalence test: for every operator the engine, VizFactory and the translated action return the same rows on the same frames (integer, float, text, with nulls); the existing `test_t3_translator`, `test_export_view_consistency`, `test_filter_operators`, viz_factory tests; mutation check.

### P1 - NA rule (#63) `NA-RULE-63` `[sonnet/high]`
The rule is decided (`home_audit_steps.md` section 19): a missing value is a value; `!=` and none-of keep it; `==`, one-of and comparisons remove it; always counted and reported. Today `!=`, none-of and comparisons drop rows with a missing value silently, and the engine and the translated actions agree (both drop). Changing the engine alone would make the plot and the reproducibility export disagree; changing the registered actions would silently change existing recipes: the plan (an optional `na` parameter, passed explicitly by engine, VizFactory and translator; Blueprint schemas retested) is in the comment of 2026-11-12 on #63.

### P3 - key extraction (#61) `HOME-EXPLORE-2` `[sonnet/medium]`
**Verified problem:** `extract_primary_keys` returns `[]` for `1_test_data_ST22_dummy`, `2_test_data_ST22_dummy` (tiered join steps) and `3_test_no_joins` (its declared key is ignored); the ADR-049 safeguards never fire. The only test is in `app/tests/debug_home_theater.py`, which is not collected and does not run (IndentationError, line 81).
**Do:** read the loaded dicts; tiered and legacy lists; only steps whose `action` is `join` or `join_filter` (the current function also reads `on` of `unpivot` steps and returns `n50`, `total_length`...); `on` as string or list, `left_on`/`right_on`, the YAML `True` key; add declared keys (`is_primary_key` in `input_fields`; a join column of a schema without a declared key counts as inferred); a recipe without joins returns its declared keys; never find keys from column names. It is absorbed by `utils.recipe_graph` (`RECIPE-GRAPH-UTILS-1`). **User-visible effect (announce):** the primary-key warning appears when an audit filter targets a key column, and dropping a key column is blocked, as ADR-049 specifies.
**Tests (real `ConfigManager`, no mocks):** ST22 returns `sample_id`; `3_test_no_joins` returns its declared key; tiered, list, string, list-valued `on`, `left_on`/`right_on`; `VirulenceFinder.metadata_sample_material` is never a key; the unpivot columns are never keys; mutation check.

### P8 - Exploration preview behaviour (#56) `HOME-EXPLORE-4/5/6` `[sonnet/high]`
Spec: `home_preview_filters.md` sections 3-5 and 9-10 (selector Source | T1 | T2 | T3). Interim rules until the audit packages replace the strip:
- Lists keyed by dataset (the plot's `target_dataset`), not by view; a new pure store `app/modules/preview_filters.py` (`stage`, `apply`, `remove`, `reset`, `clear_all` returning the count, `applied_rows(dataset)`, `staged_rows(dataset)`) in one `reactive.Value`, replacing `applied_filters` and `_pending_filters`. Leave `DEFAULT_HOME_STATE` untouched (saved-state shape).
- `_filter_send_to_audit` reads the staged rows of the current dataset and must produce exactly the same audit nodes as today (test it); `_clear_filters_on_t3_apply` keeps clearing everything.
- Clear all lists when the data selector changes and when the recipe changes, with the notification "N preview filters cleared (you changed view)"; idempotent guard (rule R3); not at the first render. WHY comment: a filter is built against the columns, names and types of one stage.
- The Filters panel header names its target ("Filters: Raw table of MLST_with_metadata"; own small output, shell stability pattern, rules R2-R4 of `ui_implementation_contract.md` section 14). Column selector: a "reset to all columns" button (`ui.update_selectize`; never re-render the selectize, rule R4). One operator vocabulary in `filter_inventory_ui`: `OP_WORDS` / `describe_filter`. Fix the stale docstring of `_filter_apply`; verify in `session_manager.py` whether anything persists filters before editing contract section 7.1.
- **Test suite (`HOME-EXPLORE-5`):** `app/tests/test_filters_behaviour.py` (browser, `qa`, `1_test_data_ST22_dummy`) plus headless tests of the store and the engine. Oracle: the same filter with Polars on the same stage, compared with the table text and "Viewing rows a through b of N" (N is the real check, not the badge); screenshots to `tmpAI/`; edge cases of `home_preview_filters.md` section 9; the Result plot is identical before and after Apply; nothing written under `anchors/`; the export contains no preview filter; mutation check per rule. Leave the shared page clean (use the trash icon, not Reset).
- **Help and docs (`HOME-EXPLORE-6`):** `app/src/help/home.md`, `docs/user_guide/system_transparency.qmd`, `docs/appendix/FAQ.qmd`, ADR-098 (one line on how far it is built), contract text.

### Independent: warn for dropped plot-spec keys (#66) `HOME-EXPLORE-8` `[sonnet/medium]`
Files: `plot_config_resolver.py`, `viz_factory.py` (where unknown `plot_defaults` keys already give a `PipelineError` warning), tests. Same severity and surface (ADR-079). Passthrough metadata keys must not warn (`family`, `pattern`, `difficulty`, `description`, `info`). Hints: `facet_scales` -> `facet_wrap` layer with `scales`; `labs` -> `labs` layer; `coordinate_flip` -> `coord_flip` layer. (Under the recipe-format work this becomes a check of `check_recipe`.)

### Independent: many-to-many join warning (#68) `HOME-EXPLORE-10` `[sonnet/medium]`
Rows before and after each join; a key repeated on both sides gives a warning (one-to-many stays silent). Edits `libs/transformer`: needs Eve's OK. Input for guard-rail J1 of the audit (#64).

## 5. Questions for Eve still open
1. P3 turns on safeguards that are specified (ADR-049) but dead today: a primary-key warning and a block on dropping a join-key column in the audit. OK?
2. P1: may the shared filter-value code live in `libs/utils` (a new pure module)? (`libs/utils` as the home of shared graph and key code is decided in ADR-099 point 16.)
3. Waiting for Eve outside this brief: what `ST22_Anchor` answers (#67), the resistance score of samples without phenotype (#70), the rest of the recipe hygiene (#69) (see `recipe_review_st22_2026-11-11.md` and `RECIPE-ST22-FIX-1`).
