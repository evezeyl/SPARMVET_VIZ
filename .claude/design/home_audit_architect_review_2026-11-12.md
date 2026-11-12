# The app and the audit plan seen by a software architect

**Written for:** Eve, to decide with (before the review of 2026-11-12). **Written:** 2026-11-12; **rebuilt in a second pass** after you asked me to check every statement against what is decided. **Status:** analysis and recommendations. Nothing here is decided.
Nothing was changed in the app code, the design files or the UML; the only change made while writing it is the new QA canary (forensics F1).
**Companion:** `home_audit_forensics_2026-11-12.md` (the design forensics, section 3.2b explains the cheaper engine). **Method:** the persona method of
`.claude/workflows/design_review_personas.md`, with one more point of view: **A** = software architect. Status words as in the forensics: **DECIDED**, **CONFIRM** (`[confirm]` in the design), **OPEN**, **MINE** (a proposal from these reviews, not in the design). The others: **S** scientist who publishes, **DS** data scientist,
**Dev** developer, **QA** checker, **Ops** operator, **N** novice user, **Sec** someone who must run this on a shared server.
**Evidence classes:** **verified** (run, or read at `file:line`), **reasoned** (follows from verified facts, not run), **not verified** (said so). The checks are scripts in
`tmpAI/architect/` (`scan.py`, `engine_cost.py`, `recipe_is_code.py`, `allowlist_probe.py`, `render_canary.py`; scratch, not committed).

## 0. The answer in ten lines

1. The layer rules hold where a machine can check them (section 1). The base is better than the size of the code suggests.
2. Three weak points sit exactly where the audit build will touch the code: **recipe text is code** (AR1), **the rule "which filter reaches which view" lives in many places** (AR2), and **the handlers are giant functions** (AR3).
3. The cheaper engine (E: audit state = recipe plus your steps, run by a second orchestrator) is a good shape (one way to compute data), but **it reconsiders a decided mechanism** (the audit cache with its own keys) and it does not cover level 3. It was measured in the plot-level mode only (forensics 3.2b); the two modes HOME needs are not measured.
4. The first cut (`home_audit_first_cut.md`, a proposal that follows the reading guide, 6) is architecturally sound: each piece is a pure module, compatible with the brief's rule S5. My first idea of a view-policy module inside WP4 is **withdrawn**: WP4 is interim and the decided target replaces the view model (3.2).
5. Your rule is already decided (ADR-099 point 2): the strip is "Data: Raw | Result" in every feature, "Plot to show" never appears, and without the sandbox flag only Exploration exists. The real catch is the **interim**: until audit mode exists, the two features without the flag keep a plot that changes unrecorded (forensics F8, 3.7). It needs your answer.
6. Five new decisions came out of this review (section 4): N2 what to do with the `developer_raw_yaml` step type (no code creates it, 3.1 and N2), N3 trust levels for recipe sources, N4 how to hold the decided flag rules, N5 architecture rules as tests, N6 stored stages (atomic write and path for the original anchors; the design already has both for the audit cache).
7. The most consequential finding is AR1. It matters only on a shared server (Galaxy, IRIDA, Connect are named targets in `dasharch.md`); on one scientist's machine it is low.
8. Nothing here blocks the two builder tracks (A engine, B exploration); WP4 stays as briefed (interim). Only your answer to the interim question (forensics 3.7) may change its scope.
9. There is no automatic check on push: no CI, four empty workflow files (AR5). The headless gate takes 75 seconds, so a first CI job is cheap.
10. What I did not verify is in section 7.

## 1. What holds (checked, no change needed)

| What | Evidence |
|---|---|
| No UI library in the libraries | scan: no `shiny` or `htmltools` import in `libs/*/src` (verified) |
| No library imports another domain library at run time | scan flagged `transformer/pipeline.py` -> `ingestion`; it is under `TYPE_CHECKING` only (`pipeline.py:13-23`), as the rules allow. So: zero violations (verified) |
| No `sys.path` edits anywhere | scan (verified) |
| No import cycles among the app modules that import each other by `app.` path; modules never import handlers | scan: 21 modules, 0 cycles, 0 module->handler imports (verified; relative imports are not covered) |
| YAML is loaded safely | all 14 `yaml.load` calls in `app/` and `libs/*/src` use `yaml.SafeLoader` or a subclass of it, including the local `_L` at `blueprint_handlers.py:1392` (verified: `grep`) |
| Subprocesses run without a shell | `shell=True` appears nowhere (0 hits); the 6 calls pass an argument list (verified: `agent_adapter.py:156,177,284`, `exporter.py:38,308`, `blueprint_handlers.py:2813`) |
| The stored-stage keys fail safe | an unknown recipe section is part of tier 1 by default, "a wrong guess can only cause an extra rebuild" (`cache_keys.py` header, verified) |
| A half-written stored file is not trusted | the key reader swallows every error and returns "no key", so the stage is rebuilt (`hashing.py:44`, verified) |
| Row order is deterministic and tested | ADR-090; `test_anchor_determinism.py` runs on every collection, including the new canary (verified: collected) |
| The headless gate is fast and green | 1649 passed in 75 s on 2026-11-12 (verified) |

## 2. Findings

Severity is written with its condition, because it depends on where the app runs.

| # | Finding | Evidence | Severity | What it means for the audit build |
|---|---|---|---|---|
| **AR1** | **Recipe text is Python code.** `mutate` runs `eval(expression, {"pl": pl})`, which gives the text the full builtins. Two more `eval` sites: ID recoding (`id_reconciliation/core.py:239`) and `stat_function` (`viz_factory/geoms/core.py:1335`, the comment says "developer-controlled recipes only"). **Run:** a `developer_raw_yaml` step, translated by `build_mode2_recipe` and built by a second orchestrator, wrote a file (`recipe_is_code.py`: marker created). | verified (run) | **High** on a shared server; low on one machine. Not exploited; shown as a capability | E (MINE) would make an audit state a recipe, and the decided design keeps `developer_raw_yaml` as a listed legacy type (`home_audit_steps.md` 4). Both touch this path: N2 and N3 |
| AR1a | Where recipe text can come from outside: **bundle import** writes the zip's recipe into the shared recipes folder and checks its structure only (`bundle_importer.py:239-244`); the control is in the Export panel, the gate seen on the way is `export_enabled` (`export_handlers.py:467,584`), so it is available in every feature file that has Export, also `pipeline-static` (reasoned from reading; the app was not launched to click it). Blueprint recipe import and the YAML escape hatch (gates `blueprint_enabled`, `data_analysis_recipe_edit_enabled`). A **session zip** carrying a `developer_raw_yaml` step: HOME does not run it, but export Mode 2 copies it into the bundle's recipe (`export_handlers.py:1223-1228`) and a later bundle import runs it (reasoned). **No code in the app creates such a step** (verified: every non-test mention is a reader or the translator; the Blueprint escape hatch Save only re-parses YAML into Blueprint's own state, `blueprint_handlers.py:1342-1376`), although `rules_ui_dashboard.md` 7 says the escape hatch emits one: a rules/code discrepancy. So the step can only arrive inside a saved or imported session file | verified by reading; end to end through the UI not run | as AR1 | Importing a bundle is importing code. The import is a decided feature (ADR-097, #48) built for reproducibility, so its trust model needs a sentence in the docs at least |
| **AR2** | **The rule "which filters reach which view" is implemented several times.** In `home_theater.py` alone: plot filters (line 481), the "my view has changes" test (673), badges (744, 1321), the data table (1346), the audited-table gate (1394, 1458) and the filter summary (2056); the export has its own (`audited_frame`, `plot_content_rules`). **Three filter engines** exist: VizFactory `filters` (plots), `_apply_filter_rows` (tables, `t3_audit_engine.py:75`) and the named actions of the translator (export). They already disagree: issue #62 (integer thresholds). A test keeps export and view in line (`test_export_view_consistency.py`), but nothing makes it true by construction | verified (grep counts: `applied_filters.get()` 6, `_t3_drop_columns(` 6, `tier_toggle.get()` 6, `plot_view` 11 in `home_theater.py`) | **High for the build**, not a runtime risk today | The decided target replaces this model (`home_audit_steps.md` 14: `home_theater.py` "strip -> Exploration, mode switch, ... My view/Compare removed"), so all these places change at that moment: see 3.2 |
| **AR3** | **Giant handler functions.** `define_server` closures of 2,755 lines (`blueprint_handlers.py:144`), 2,145 (`home_theater.py:110`), 1,491 (`wrangle_studio.py:540`), 963 (`test_lab_handlers.py`), 831 (`audit_stack.py`); `export_bundle_download` is one function of 1,145 lines; 58 of 1,034 functions are over 100 lines (nested ones counted); three places nest control flow 11 deep. Shared state is reached through the enclosing scope, so a change cannot be checked by reading one function | verified (`scan.py`) | Medium. It makes every change slower to check and hides coupling; it is probably part of why UI changes lean on the 7.5-minute browser gate (reasoned) | Do not refactor the monoliths now. **Rule for the build:** new logic goes into pure modules with table tests; a handler only wires. Extract the policy (AR2) at the moment it is touched |
| **AR4** | **Stored stages.** All sessions of one deployment share `user_data/anchors/<collection>.parquet` (named by collection only; `home_theater.py:257,875,1191`, `export_handlers.py:939`, `blueprint_handlers.py` x6). The key check prevents a wrong result (good), but: two recipes with the same collection name rebuild each other's file at every switch (the 7 shipped recipes share none: verified, so it holds by convention, not by rule); the write is direct to the final path, not temp file plus rename (`anchor.py`: `df.write_parquet(path)`), so a second process could read a partial file (safe direction: it is rebuilt); **no clean-up of stored stages exists** (only stale tier-2 files are removed, `orchestrator.py:136,146`) | verified; the multi-process case is reasoned (Shiny runs synchronous handlers on one event loop, so inside one process the writes do not interleave) | Low now; Medium with several workers or a disk quota | The design already has the N = 5 removal and "atomic cache writes" for the **audit** cache (`home_audit_steps.md` 7.3, 18 flaw 10, 19). N6 (MINE) extends the same two rules to the original `anchors/` folder |
| **AR5** | **No automatic checks on push.** `.github/workflows/_disabled_workflows/` holds four **empty** files (0 bytes: `test_suite.yml`, `lint_and_format.yml`, `docs_build.yml`, `deploy-connect.yml`). Every gate is run by hand; the browser gate is timing-flaky under load (forensics section 5, #72). Dependencies have lower bounds only (`polars>=1.0.0`, `shiny>=1.0.0`, `pandas>=2.0`; only plotnine is capped) and no lock file is tracked (`requirements-connect.txt` only). The cache key records the Polars and transformer versions, so stored stages are rebuilt after an upgrade, but two users with different Polars versions can still get different figures (reasoned) | verified (`ls`, `git ls-files`, `pyproject.toml`) | Medium | A green gate depends on who remembers to run it. First job: the headless gate (75 s). The workflow file is yours to write (mentoring rule: CI by hand, I review); a lock file for deployments is one command |
| **AR6** | **Failure handling and logging.** `print()` is the log: 158 calls in the libraries and the app (69 in `app/`), the `logging` module is imported in 2 modules; every recipe load prints dozens of "Auto-unnesting" lines. 199 broad `except Exception` handlers (167 in `app/`), 28 of them silent (`pass`/`continue`). `ConfigManager` ends the process with `sys.exit` on a bad recipe (documented in `rules_data_analysis_recipe_structure.md` 11 and in a comment of `bundle_importer.py`); each caller must remember to wrap it (`validate_data_analysis_recipe`) | verified (`scan.py`, `rg`) | Medium for operation (no levels, no per-user trace), Low for correctness | The audit adds a log of decisions. It should use one structured channel (the event log of decision 9), not more `print` |
| **AR7** | **The audit record and imported sessions.** `AuditStep` is a `TypedDict(total=False)` with a free `params: dict` per node type and two dead fields: `active` ("legacy soft-delete flag") and `gallery_source` (the Gallery clone was removed, ADR-093) (`session_manager.py:44-56`). `import_session_zip` checks that `assembly.json` or `t3_*.json` exist and refuses old-rename keys, then `extractall`s into `_sessions/` (`session_manager.py:498-516`); it does not check node types, parameter shapes or sizes. Stored `parquet_paths` are only tested for existence and no handler loads them (grep), so no path from a file is trusted today | verified | Medium (it is the entry to AR1a for sessions) | The step record is decided (`home_audit_steps.md` 11: id, kind, reach, level, targets, params, reason, initials, created_at; status computed). What is MINE: a typed model per kind (an enum of kinds, the reason categories of question 3) and one validator used on every load, **import included** |
| **AR8** | **Flags are independent booleans.** 13 `*_enabled` flags per feature file, 8 files, two kinds of cascade (soft in the bootloader, fatal in the validator). A dead combination ships: `pipeline-exploration-simple` has `comparison_mode_enabled: true` with the sandbox off (the file's own comment says it "requires t3_sandbox_enabled to be meaningful", line 18). Only the 8 shipped combinations are tested (`test_every_app_features_starts.py`, `test_app_features_validator.py`, `test_flag_matrix_doc.py`) | verified | Low to Medium | The two validator rules are **DECIDED** (`home_audit_steps.md` 14 and 16: comparison requires the sandbox flag; the sandbox flag requires the `audit_stack` slot), and the shipped dead combination "must change". N4 only proposes how to hold them: one table |
| **AR9** | **Documentation is larger than the code and drifts.** `.claude/` holds 57,324 lines of Markdown (rules 4,544; ADR log 5,075 lines, 99 ADRs) against 35,967 lines of product Python. Drift seen today: `rules_app_structure.md` says `server.py` "hard limit ~250 lines", it has 262; the word "never" stands in 16 places of 8 HOME diagrams for behaviour that is not built (forensics F9). The doc audits catch part of this (`audit_docs_sync.py` passes) | verified (`wc`, `grep`) | Low for the app, Medium for the cost of every session (this session started with about 4,500 lines of rules in context) | Prefer a test to a sentence where a machine can check (N5) |
| AR10 | Smaller: a hard-coded `".venv/bin/python"` relative path in `blueprint_handlers.py:2814` (the rules say the interpreter comes from the deployment, `rules_runtime_environment.md` 5); `.collect()` 11 and `.to_pandas()` 4 in `app/` (fine at 203,146 rows measured; production size not known) | verified | Low | none |

## 3. The three biggest, in more detail

### 3.1 AR1: what to do about recipe text being code (decision N3)

Measured facts that decide the options: **all 19 expressions in 420 YAML files** (7 recipes, the gallery bundles, templates, test recipes) use only `pl.col`, `pl.lit`, `pl.when`, `pl.String`, `pl.Int64` and the methods
`cast`, `n_unique`, `otherwise`, `over`, `str`, `strip_chars`, `then`, `to_lowercase` (verified: `allowlist_probe.py`). A first prototype of an allow-list (syntax only: `pl` attribute chains, literals, operators; no other names, no `_` attributes, no lambda or comprehension)
accepted **19 of 19** and refused `__import__`, `open`, `__class__`, a lambda and a comprehension. **It is not enough:** two bypasses are accepted (verified): `'{0.__class__}'.format(pl)` and `pl.read_csv('/etc/hostname')` (36 `pl.read_*/scan_*/from_*/write_*` names exist). A real allow-list must restrict the **vocabulary**: `pl` names to the expression builders and dtypes, methods to the public `pl.Expr` API
(218 methods and 9 namespaces) and no method calls on string constants.

| Option | S | DS | Dev | QA | Ops / Sec |
|---|---|---|---|---|---|
| **(a) Document only:** "a recipe is code; import only what you trust"; bundle import off by default on hosted features | nothing changes | nothing changes | none | none | cheap; the risk stays and rests on a sentence |
| **(b) Two trust levels:** shipped and operator recipes run as today; imported recipes (bundle import, session-borne steps, escape hatch when enabled) must pass a vocabulary allow-list at import and at every build | imported bundles still re-run if they use plain Polars expressions (all 19 shipped ones do) | same | one pure module (about 100 lines) plus a bypass corpus; called in `bundle_importer`, the translator and the validator | a test with the bypasses found today and with all shipped expressions | closes the verified path; a rejected recipe gets a clear message |
| **(c) Structured expressions** (an expression tree in YAML instead of text) | every recipe is rewritten | the same, harder to type by hand | a new language | large | strongest, but breaks everything shipped |
| **(d) Run imported recipes in a sandbox** (separate process or container, no network, read-only data) | invisible | invisible | process plumbing | hard to test | strongest isolation, heavy to run |

**Recommendation: (a) now, (b) with the audit build** (the translator already writes recipe steps from audit steps, so the check belongs there whichever engine is chosen). (c) is out of proportion; (d) only if the app is offered to unknown users.
**Reversibility:** high. **What would change it:** a hosted deployment before the audit build ships: then (b) first.

### 3.2 AR2: the view rules in one place (status: MINE; my first proposal is withdrawn)

My first version proposed a pure policy module as the first package of WP4. **Withdrawn.** WP4 is an interim step on today's view model (Raw, Result, My view, Compare, "Plot to show") that the decided target replaces (forensics 0.1 and 3.7);
the brief's goal is "do not do work that the audit design would make Eve undo". A module that encodes the interim would be partly undone.
What stays true: the rule is coded in several places (section 2, AR2), and **the replacement of My view and Compare is exactly the moment when all of them change** (`home_audit_steps.md` 14: `home_theater.py`, "strip -> Exploration, mode switch, panel dispatch, plot and table data sources, My view/Compare removed").
**Proposal (MINE, for the audit build, not now):** write the module **against the target model** as the first package of the audit build without a UI (D14 stage 3). Two modes (Exploration, Audit mode), the Exploration data view (Raw, Result), the sandbox flag.
It answers three questions: which stage the table reads; which filters apply to the table (Exploration: the preview list of the dataset; audit mode: none); which source the plot reads (Exploration: the Result plot; audit mode: the audit plot).
The table to test is small and comes from a decided diagram: {Exploration Raw, Exploration Result, Audit mode} x {preview filters present, audit steps present} x {sandbox on, off} = 12 cells, written once from `HOME-VIEW-MATRIX`.
**Consequences:** S one rule for table, plot and export; DS the same; Dev the section 14 change to `home_theater.py` becomes mostly a change to one module; QA a 12-cell table test, not a browser walk; Ops and N none.
**Cost:** about half a day with tests when the audit build starts. **Reversibility:** high. It does not fix the three filter engines, and not level 3 (forensics F15).

### 3.3 AR3: how to live with the giant functions

Do not rewrite them. Three rules for the build, all cheap: (1) new rules go into pure modules with table tests (the pattern already works: `t3_translator`, `t3_audit_engine`, `cache_keys`); (2) a handler only reads inputs, calls a module and sets outputs;
(3) the sizes cannot grow: a headless test with the current maxima of the five biggest functions (a ratchet; part of N5). When a handler must be edited anyway, extract what you touch (strangler approach: the old function shrinks a little each time).
**Why not more:** a rewrite of 6,000 lines of reactive code is the most expensive way to get no new feature, and the browser gate that would verify it is the flaky one.

## 4. The undecided items as an architect sees them

**Status** uses the words of the forensics (DECIDED, CONFIRM, OPEN, MINE). "Do first" says what to build before the item, so that the item is cheap.

| Item (forensics) | Status | Architect view | Better or added design | Do first |
|---|---|---|---|---|
| 3.1 cut or full | on the path (reading guide 6); the cut plan is MINE | The cut is the right size: each piece is a pure module (brief S5). The full design puts a subsystem (checks, event log, lineage, dialogs) on top of AR3 and AR7 | none | the engine fixes (WP1-WP3a); the typed step record (AR7) |
| 3.2 audit data engine | the mechanism is DECIDED; E is MINE and reconsiders it | E fits "one way to compute data", and the two translator modes are needed for the export anyway. It does not cover level 3 (render time, F15) and the measured cost is the plot-level mode only | the spike also tries the N = 5 removal (decided) and the trust check (N3) | the spike |
| 3.3 reach and stage | selector, stage from the kind: DECIDED; three options: CONFIRM; B reconsiders | In E "reach" is where in the recipe a step is inserted: at every source that has the key, inside one collection's tier 2, or at the plot. That may be simpler to explain and test than kind x reach x stage (reasoned; to try in the spike) | show the insertion point on the lineage chain | the canary (done) |
| 3.4 NA rule | the rule DECIDED in principle; where it lives OPEN | decide where the rule lives: in each of the 8 actions, or in the step compiler only | prefer the compiler if the spike shows it can express all 8 operators (an expression-based filter, fine with the allow-list of N3) | the matrix of #63 as a test table; WP3a |
| 3.5 event log | in principle DECIDED; D2 CONFIRM; option C is MINE | C is right for the cut; add `schema_version` and refuse unknown versions | the typed record of AR7 | AR7 |
| 3.6 keys | DECIDED | one pure function "key map of a recipe", used by the audit, the checks and the validator (D1 starts there) | recipe-validator advice "no key declared" | WP2 (#61) |
| 3.7 strip and no sandbox flag | the target DECIDED; the interim OPEN (brief question 3); the early slice MINE (R5) | the target is "Data: Raw \| Result" in every feature. Until audit mode the code carries two strips. The early slice for features without the flag is the **final** screen of those features, so it is not rework | the flag rules of N4 come with it | your answer to 3.7 and to F14 |
| 3.8 #11 first checks | CONFIRM | the guard-rail list as a table-driven pure module (id, trigger, level, message, test): adding a check is adding data | thresholds as settings | the typed record |
| 3.8 #10 lineage map | CONFIRM | `build_plot_lineage` (listed in `rules_app_structure.md` 4, ADR-074) already traces a plot back to its tier-1 root; reuse it (not read here) | | read it in the spike |
| 3.8 #13 legacy names and types | CONFIRM | keep the `t3_*` names behind a glossary line (an anti-corruption layer); rename only with a saved-format version bump | | none |
| **N2** the `developer_raw_yaml` step type | design text DECIDED ("stays as it is ... never authored in audit mode", `home_audit_steps.md` 4); "legacy types kept" CONFIRM (question 13); my change is MINE (R4) | **Verified:** no code creates this step (3.1, AR1a), yet it is the only audit step that carries code, and it can arrive in a session file. **Options:** (i) keep as designed; (ii) keep it **display-only**: listed as "recipe fragment", deletable, but the translator refuses it, which the design already names as a block (B1: "a step the forked recipe cannot represent"); (iii) retire the type and refuse it when a session loads | **Recommend (ii):** it keeps the decided listing for old sessions, closes the verified path, and needs no new rule. Also fix the rules that say the escape hatch emits it (`rules_ui_dashboard.md` 7; @sync) | your decision |
| **N3** trust levels for recipe text | MINE | section 3.1 | (a) now, (b) with the audit build | your decision |
| **N4** how to hold the flag rules | the two rules DECIDED; the table is MINE | the rules exist in the design (14, 16); **options:** (i) keep the booleans and put all parent-child rules in one table that the validator and the bootloader both read (the dead combination of AR8 becomes a startup error); (ii) capability levels (static, explore, audit, build) plus independent add-ons | **recommend (i)**; (ii) only if more combinations appear. Reversible | the table |
| **N5** architecture rules as tests | MINE | the scan of this review can become `app/tests/test_architecture_rules.py`, about 2 s, headless: no `shiny` in libs; no lib imports another at run time; no `sys.path` edits; `eval`/`exec` only in a named list of files; modules do not import handlers; a ratchet on the five biggest function sizes and on `server.py` (262 lines now). The rules exist as prose; this makes the checkable ones fail loudly (AR9) | | none |
| **N6** stored stages of the original anchors | atomic write and the N = 5 removal DECIDED for the **audit** cache; extending them to `anchors/` is MINE | atomic write (a temp file in the same folder, then `os.replace`), a path that includes the recipe id, and a clean-up of old stages. Touches `anchor.py` in `libs/transformer` (WP10's area: needs your OK) | | the spike decides the audit part |

## 5. The structural moves, by point of view

| Move | S | DS | Dev | QA | Ops / Sec | N |
|---|---|---|---|---|---|---|
| View rules in one module, written against the target (AR2, for the audit build) | table, plot and export agree | one rule | one place to edit when My view and Compare are replaced | a 12-cell table test | none | none |
| Audit as recipe overlay, E (3.2b) | the export re-runs what you saw | figure equals bundle | little new code | oracle = direct filter | audit folder per session; clean-up needed | none |
| Trust levels and allow-list (N3) | imported bundles of plain expressions still run | none | one pure module | bypass corpus | closes the verified path | a clear message when refused |
| Flags in one table (N4) | none | none | one table to read | startup refuses dead combinations | fewer wrong deployments | none |
| Architecture tests (N5) | none | none | fails fast on a wrong import | 2-second headless | none | none |

## 6. Proposed order of work, and issues I have **not** filed

The order changes the recommended path of the forensics (section 4) by adding what this review found; nothing is built before your decision.

| Step | What | Who decides |
|---|---|---|
| 0 | Builders: WP1-WP9 as briefed (WP4 stays interim; the earlier idea of adding a policy module to WP4 is withdrawn). The canary of F1 is **done** (`QA_aggregated_no_key`, 1649 headless tests pass) | none |
| 1 | You answer the interim question of forensics 3.7 and F14; then decide 3.1 cut, 3.2 E (after the spike, it reconsiders a decided mechanism), 3.4, 3.5 and the new N2-N6 (3.6 is decided) | you |
| 2 | Spike (no UI): early key exclusion, rebuild cost, clean-up rule, trust check, key check of an audit state | after step 1 |
| 3 | Decide 3.3 with the spike's evidence; build the typed audit record (AR7), the checks, the screen | you |

Candidate issues, titles only; I file nothing without your word (your rule: Claude files an issue only when you ask):
(1) security: recipe text runs as Python, trust levels for imported bundles and the escape hatch (AR1); (2) refactor: the view rules in one module, written against the target, for the audit build (AR2);
(3) engine: stored stages, atomic write, path by recipe, clean-up (AR4); (4) CI: headless gate on push, lock file for deployments (AR5, your workflow to write); (5) config: parent-child flag table and the dead combination of `pipeline-exploration-simple` (AR8, forensics 3.7);
(6) tests: architecture rules as tests (N5); (7) logging: replace `print` in the app and libraries (AR6, low).

## 7. Not verified (said plainly)

- **Production data size** and how many people use one server; whether any real deployment lets unknown users import a bundle (AR1 is severe only there).
- The gate of bundle import was read in the code, **not clicked** in a running app of each feature file.
- The allow-list was tested on the **19 expressions that ship**; recipes written by others may use more of the Polars API, and a final list needs a bypass corpus made from the Polars `Expr` API (not written).
- Zip extraction: the stdlib is documented to drop `..` and absolute parts when extracting; this was **not tested** here, and a size limit (a zip bomb) is absent (reasoned).
- Multi-process behaviour of the stored stages (AR4) is reasoned, not run.
- `build_plot_lineage` was not read; its reuse for the lineage chain is a suggestion.
- The `import` graph scan covers absolute `app.` imports only; relative imports were not followed.
