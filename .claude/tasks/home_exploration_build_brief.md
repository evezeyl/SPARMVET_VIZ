# Build brief: HOME Exploration and engine fixes (start here in a new session)

**Written for:** the next Claude session that builds these parts. **Date:** 2026-11-11 (re-verified the same day).
**Owner of decisions:** Eve. **Goal that overrides everything below:** do not break what works, and do not do work that the
audit design (not yet decided) would make Eve undo.

**Read first, in this order:** `CLAUDE.md` (section 9 "No Guessing": ask when anything is unclear, do not guess),
`.claude/design/home_audit_reading_guide.md`, `.claude/design/home_preview_filters.md`, ADR-098 and ADR-099 in
`.claude/knowledge/architecture_decisions.md`, `.claude/workflows/design_review_personas.md` (rules 1-8 bind you).

## 0. Safety protocol (read before any edit; this is the part that protects Eve's work)

**S1. Baseline first.** `git status`, `git log --oneline -15`. Tag the start: `git tag pre-explore-build-$(date +%Y%m%d)`. Run the
headless suite and the smoke file (commands in section 1). Verified on 2026-11-11: headless **1599 passed**; `test_shiny_smoke.py`
**38 passed, 3 skipped**. If your baseline is red, **stop and report**; do not fix unrelated failures inside this work.

**S2. One work package = one commit, tests included, revertible alone.** After each package run the headless suite; after WP2, WP4
and WP5 also the full browser gate. If the gate is red and the cause is not clear within a few minutes, **revert that package's
commit** (`git revert`) and report; do not pile fixes on top.

**S3. Frozen files: do not edit.** If a package seems to need one of these, **stop and ask Eve**.
- the audit: `app/handlers/audit_stack.py`, the propagation dialog and the audit-step code in `filter_and_audit_handlers.py`
  (`_filter_send_to_audit`, `_open_propagation_modal`, `_handle_propagation_confirm`, `_col_drop_to_audit`, `_clear_filters_on_t3_apply`),
  `t3_audit_steps_by_plot`, `app/modules/session_manager.py` (except the single function named in WP2). **One exception:** WP4 may make the
  *mechanical* swap of the list accessors inside `_filter_send_to_audit` and `_clear_filters_on_t3_apply` (reading the staged rows, clearing the
  lists) and nothing else in them; a test must prove the audit nodes produced are identical to today's;
- the export and reproducibility: `app/handlers/export_handlers.py`, `app/modules/exporter.py`, `app/modules/bundle_importer.py`,
  `libs/blueprint_arch/**` (including `t3_translator.py`), `libs/transformer/**` (the registered actions), `app/modules/orchestrator.py`,
  `app/modules/cache_keys.py`;
- the header strip as built ("Plot to show", "Data to show", My view, Compare) and everything about the right sidebar;
- Blueprint, Gallery, Test Lab, `config/app_features/*`, `sidebar_registry.py`, `CLAUDE.md` (Eve's uncommitted edit stays uncommitted:
  never stage it), the UML model `docs/UML/app.mdj` and the diagrams (if a diagram becomes wrong, tell Eve).

**S4. Allowed files per package** are listed in each package. Anything else needs Eve.

**S5. Compatibility contract with the future audit (do not break; the audit will reuse all of this).**
- The stored filter row is `{column, op, value, dtype[, closed]}` with the operator names `eq ne gt ge lt le in not_in between`. Keep it.
  Keep the signatures of `_apply_filter_rows`, `OP_WORDS`, `op_choice_label`, `describe_filter` (`app/modules/t3_audit_engine.py`).
- Audit steps (`make_audit_step`, node types, `t3_steps.yaml`, ghost files, `home_state` keys, session files) stay byte-compatible:
  no new keys in `home_state`, no new fields in any saved or exported file.
- New logic goes into **pure, headless-testable modules** (no Shiny), because the audit's recipe graph and step compiler will absorb them.
- **Registered transformer actions keep their behaviour for every existing parameter.** Existing recipes must give the same data.
- Do not add anything that needs the audit (no event log, no cache, no new panel, no mode switch).

**S6. Before editing a function, list its consumers** (grep) and, after editing, re-run the tests that pin it. Consumers of the filter
engine today: `home_theater.py` (preview and plot), `export_handlers.py` (`audited_frame`, the exported `T3_data_<plot>.tsv`),
`libs/viz_factory/.../viz_factory.py` (its own copy of the filter code), and the translated recipe actions that the reproducibility
export re-runs (`libs/blueprint_arch/.../t3_translator.py` -> `libs/transformer` actions).

**S7. Tell Eve about every user-visible behaviour change before it lands** (list in section 5).

**S8. Stop and ask when:** a package needs a frozen file; a test you did not touch fails; the code differs from this brief; you are
about to guess a default; a number in this brief does not match what you see.

## 1. Facts to verify at the start (do not trust this brief)

Branch `dev`; code last changed by `fa552bf` and `28ec1a6`; since then only design files, UML and issues. Archive tag
`archive/home-filters-uml-2026-11-11`. Dev server (always with reload):
`PYTHONPATH=. SPARMVET_APP_FEATURES=developer ./.venv/bin/shiny run app/src/main.py --reload --port 8123`.
Headless: `PYTHONPATH=. ./.venv/bin/python -m pytest libs app/tests --ignore=app/tests/test_shiny_smoke.py --ignore=app/tests/test_shiny_smoke_blueprint.py --ignore=app/tests/test_export_download.py --ignore=app/tests/test_every_app_features_starts.py -q`
(about 60 s). Browser gate (about 7 min): `PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py app/tests/test_shiny_smoke_blueprint.py app/tests/test_export_download.py app/tests/test_every_app_features_starts.py -q`.
`TestRecipeSwitchPlotRender` is timing-flaky (8 s wait); it passes on rerun.

## 2. Working rules (from `CLAUDE.md` and Eve's global rules)

- Issue first, fix second, close with the evidence. Commit on `dev`, Conventional Commits, footer `Refs: evezeyl/SPARMVET_VIZ#N`
  (never a bare `#N`, never `Fixes`). Auto-commits are pre-approved here; stage files by name.
- Every rule you add must be breakable in a test: change the code once, see the test fail, restore it (mutation check).
- Scratch output in `tmpAI/`; `tmp/` only for `@verify` evidence, then stop: "Data/Plot ready in tmp/... Waiting for @verify".
- Session end: `@deps` blocks of touched files, `python assets/scripts/build_dep_graph.py`, `audit_docs_sync.py`, `audit_uml_model.py`,
  a log line in `.claude/logs/audit_YYYY-MM-DD.md`, a handoff entry (append, never delete).
- Eve is not a native English speaker: correct spelling in what she writes, one short line, no lesson. Say plainly what you could not
  verify. Work replies short. Code comments say WHY, never WHAT; no emojis in Python.

## 3. Work packages (in this order; each is shippable on its own)

### WP1 - integer thresholds (#62) `[sonnet/medium]`
**Verified problem:** on an `Int64` column [89, 90, 91] the audit engine and VizFactory truncate (`int(float(value))`):
`>= 90.5` keeps 90, `< 90.5` keeps only 89, `= 90.5` keeps 90. The registered recipe actions that the reproducibility export re-runs
(`filter_range`, `filter_lt`, `filter_eq`) compare correctly (`>= 90.5` -> 91; `< 90.5` -> 89, 90; `= 90.5` -> none). **So today the
figure and the reproducibility bundle disagree.** The actions are the reference; do **not** change them.
**Allowed files:** `app/modules/t3_audit_engine.py` (`_coerce_to_dtype` and its callers), `libs/viz_factory/src/viz_factory/viz_factory.py`
(the filter coercion block only, about line 171), a new pure module in `libs/utils/src/utils/` (viz_factory already depends on `utils`),
tests.
**Do:** one shared implementation of the filter-value coercion (comparison semantics identical to the registered actions: compare as
float when the value is not an integer); both consumers call it. Remove the second copy.
**Tests:** (a) the table of #62 for every operator and `.0`, `.5`, integer values; (b) an **equivalence test**: for every operator, the
engine, VizFactory and the translated action (`t3_translator` -> registered action) return the same rows on the same frames (integer,
float, text, with nulls); (c) the existing `test_t3_translator`, `test_export_view_consistency`, `test_filter_operators`, viz_factory tests;
(d) mutation check (put the truncation back).

### WP2 - key extraction (#61) `[sonnet/medium]`
**Verified problem (re-run 2026-11-11):** `extract_primary_keys` returns `[]` for `1_test_data_ST22_dummy`, `2_test_data_ST22_dummy` (tiered
join steps) and for `3_test_no_joins` (no joins; its declared `is_primary_key` is ignored). The ADR-049 safeguards never fire. The only test
is in `app/tests/debug_home_theater.py`, which pytest does not collect and which does not run (IndentationError, line 81).
**Allowed files:** a new pure module `app/modules/recipe_keys.py`; in `session_manager.py` only the body of `extract_primary_keys`, which
**delegates** to it and keeps the return type (sorted `list[str]` of column names); `app/tests/` (a collected `test_*.py`; fix or retire the dead script).
**Do:** read the loaded dicts (`raw_config`); handle tiered `tier1`/`tier2` lists and legacy lists; `on` as string or list, `left_on`/`right_on`,
the YAML `True` key; add the declared keys (`is_primary_key: true` in `input_fields`; optional, often absent: a join column of a schema without a
declared key counts as an **inferred** key). A recipe without joins returns its declared keys. Never find keys from column names.
**User-visible effect (announce, S7):** the primary-key warning banner now appears when an audit filter targets a key column, and dropping a key
column is blocked, as ADR-049 specifies. Re-run `TestAuditGate`, `test_session_manager`, the browser gate.
**Tests (real `ConfigManager`, `from utils.config_loader import ConfigManager`, no mocks):** ST22 returns `sample_id`; `3_test_no_joins` returns its
declared key; tiered, list, string, list-valued `on`, `left_on`/`right_on`; `VirulenceFinder.metadata_sample_material` is never a key; mutation check.

### WP3a - NA: inform only (#63, step 1) `[sonnet/medium]`
**Verified problem:** `!=`, none-of and comparisons drop rows with a missing value silently; NaN is kept by `>=` and dropped by `<`. The audit engine
and the translated actions **agree** today (both drop), so **do not change the behaviour in this package**.
**Allowed files:** `app/modules/t3_audit_engine.py` (a pure counting helper), the filter form and badge texts in `filter_and_audit_handlers.py`
(display only) and `view_badge.py`, tests.
**Do:** show, before and after Apply, "N rows have no value in this column and are removed by this filter" (count of null and NaN in the filter
column among the rows that the filter would remove). Information only: same rows as before.
**Tests:** counts for every operator with nulls, NaN, mixed; rows unchanged (compare with the pre-change output); mutation check.

### WP3b - NA: the rule (#63, step 2) `[sonnet/high]` **BLOCKED: do not start**
Needs Eve's decision on the default and the audit design (step compiler). Changing the engine alone would make the plot and the reproducibility
export disagree; changing the registered actions would silently change existing recipes. The plan (an optional `na` parameter whose default is today's
behaviour, passed explicitly by engine, VizFactory and translator; Blueprint schemas retested) is in the comment on #63. Leave it.

### WP4 - Exploration preview behaviour (#56) `[sonnet/high]`
Spec: `home_preview_filters.md` sections 3-5 and 9-10. **Interim rules, because the strip stays as built:**
**Allowed files:** new `app/modules/preview_filters.py` (pure store), `app/handlers/home_theater.py` and `app/handlers/filter_and_audit_handlers.py`
**only at the places listed here**, `view_badge.py`, tests, help and docs of WP6. **Leave `DEFAULT_HOME_STATE` (`orchestrator_helpers.py`) untouched**: it lists `_pending_filters` and `applied_filters` keys that no code reads; removing them changes the saved state shape (S5), so that is a later cleanup with the audit.
- Lists are keyed by **dataset** (the plot's `target_dataset`), not by view: everything is cleared on a view change, so only one view exists at a
  time. Replace the two reactive values `applied_filters` and `_pending_filters` (`home_theater.py` 203-204) by the store (`stage`, `apply`, `remove`,
  `reset`, `clear_all` returning the count, `applied_rows(dataset)`, `staged_rows(dataset)`) wrapped in one `reactive.Value`. Consumers to move,
  without changing what they compute: `home_theater.py` 483, 673, 744, 1321, 1346, 2056, 2240; `filter_and_audit_handlers.py` 32-44, 117, 288-301,
  421-439, 463, 508-516, 885-916. **`_filter_send_to_audit` reads the staged rows of the current dataset and must produce exactly the same audit nodes
  as today** (test it). `_clear_filters_on_t3_apply` keeps clearing everything (frozen).
- **Clear all lists when "Data to show" (`tier_toggle`) changes and when the recipe changes**, with the notification "N preview filters cleared (you
  changed view)". Idempotent guard (rule R3); not at the first render. "Plot to show" (`plot_view`) does not clear (interim). WHY comment at the
  clearing code: a filter is built against the columns, names and types of ONE stage (T1 wide, T2 long, Year 2022.0 vs "2022"); carried over it could
  match nothing or the wrong rows.
- The My view plot keeps using the dataset's applied list (as today); the table and plot rules of ADR-098 do not change.
- The Filters panel header names its target: "Filters: Raw table of MLST_with_metadata" (own small output; shell stability pattern; rules R2-R4 of
  `ui_implementation_contract.md` section 14).
- Column selector: a **"reset to all columns"** button (`ui.update_selectize`; never re-render the selectize: rule R4).
- One operator vocabulary in `filter_inventory_ui` (`home_theater.py` about 2072): use `OP_WORDS` / `describe_filter`. **Do not touch `audit_stack.py`**
  (its `_OP_SYMBOL` is replaced when audit mode is built).
- Fix the stale docstring of `_filter_apply`. Before editing `ui_implementation_contract.md` section 7.1 (it says filters are saved in sessions), verify in
  `session_manager.py` whether anything persists them.
**Not in this package:** strip rename, removal of My view / Compare / "Plot to show", mode switch, anything of the audit.

### WP5 - the filter test suite (data oracle, edge cases, screenshots) `[sonnet/high]`
New `app/tests/test_filters_behaviour.py` (browser, `qa` app features, recipe `1_test_data_ST22_dummy`) plus headless tests for the store and the
engine. **Oracle:** each test applies the same filter with Polars on the same stage and compares the table text and the "Viewing rows a through b of
N" count (N is the real check, not the badge). Screenshot after each step to `tmpAI/`. Edge cases: `home_preview_filters.md` section 9. Also: the
Result plot image is identical before and after Apply (plot_view = Result); nothing is written under `anchors/`; the export contains no preview filter;
Send to Audit from the new store gives the same audit nodes as before. **Mutation check each rule.** Leave the shared page clean (pattern:
`TestPreviewFiltersOnReferenceViews`; use the trash icon, not Reset, in cleanup).

### WP6 - help and documentation `[haiku/low]` after WP4
`app/src/help/home.md`, `docs/user_guide/system_transparency.qmd`, `docs/appendix/FAQ.qmd`: the two explanations of `home_preview_filters.md` section 8.
ADR-098: one line saying how far it is built. `ui_implementation_contract.md`: lists per dataset, cleared on view change.

## 4. Order for the demo
WP1 > WP2 > WP3a > WP4 (with WP5 alongside) > WP6. WP1-WP3a make the numbers in a figure correct and visible (and make the reproducibility bundle agree
with the figure); WP4-WP5 make the exploration behave as documented and protect it.

## 5. Questions for Eve (ask in ONE message at the start)
1. WP2 turns on safeguards that are specified (ADR-049) but dead today: a primary-key warning and a block on dropping a join-key column in the audit. OK?
2. WP1: may the shared filter-value code live in `libs/utils` (new pure module)?
3. Interim My view: the plot uses the dataset's applied list; the Filters panel acts on the view chosen in "Data to show". Acceptable until audit mode replaces it?
4. WP3b stays blocked until the audit decisions (NA default and the step compiler). Agreed?

## 6. Do not forget
`tasks.md` (entries `HOME-EXPLORE-*`), comments on the issues (#56, #61, #62, #63), the test plan items (`test_plan_home_2026-11.md`: HOM-09 to HOM-12
and new ones), `@deps`, the handoff entry. If this brief is wrong or out of date, say so and fix it; do not work around it.
