# Tasks archive, cleanup of 2026-11-13 (done tasks that were still in `tasks.md`)

Done items moved out of `tasks.md` by the cleanup of `.claude` (Eve, 2026-11-13), following the protocol of `tasks.md` (done items go to an archive file). Each item keeps its text; the heading is the section it was in. Nothing was changed or deleted.


### HOME Exploration and engine fixes (issues #56, #61, #62, #63; brief: `home_exploration_build_brief.md`)

- [x] **RECIPE-ST22-1** `[sonnet/medium]` (2026-11-11, `recipe_review_st22_2026-11-11.md`) — data-scientist review of `1_test_data_ST22_dummy`: plots with ignored `facet_by`/`facet_scales`/`labs`/`coordinate_flip` corrected with explicit layers, horizontal QC bars, unknown `plot_defaults` keys, `Detailed_summary` type, `sample_id` contract type, legacy `tier3` block removed; collections byte-identical; guard `app/tests/test_shipped_recipes_hygiene.py`. Issues #65-#71.
- [x] **HOME-EXPLORE-7** `[sonnet/medium]` — DONE 2026-11-11 (`4f85ec2`): #65 `mapping.facet_by` honoured by the resolver; unit tests, `test_render_every_plot` asserts panels, six plots looked at, mutation-checked. `virulence_variants` kept unfaceted until Eve decides (#67).
- [x] **HOME-EXPLORE-9** `[sonnet/low]` — DONE 2026-11-11 (`af36dc9`): #71 the recipe data check runs the wrangling on one row (types, not values); two tests, mutation-checked.
- [x] **RECIPE-ST22-3** `[sonnet/high]` — DONE 2026-11-11 (`c2cb302`): group "QA Canaries" in `1_test_data_ST22_dummy` (6 plots, 5 collections, one failure mode each, answers computed from the raw files in `app/tests/test_qa_canaries.py`, expected numbers in the plot subtitles, one exhibit of a known defect). Canary map: brief section 0b. Extend it when you find a new failure mode.
- [x] **QA-CANARY-AGG-1** `[sonnet/low]` — done 2026-11-12: canary `QA_aggregated_no_key` / `qa_aggregated_no_key` in `1_test_data_ST22_dummy` (T1 keeps `sample_id`, the T2 the plot reads has none; 9 country/year groups, 42 samples) and `test_aggregated_plot_data_has_no_sample_key` with a raw-file oracle. Mutation-checked (keeping `sample_id` in the aggregate fails the test), picture looked at (the first subtitle was cut off and said "9 bars" instead of 9 segments: fixed). Headless 1649 passed. Fixture for the audit reach (#60, forensics F1).
- [x] **AUDIT-ARCH-REVIEW-1** `[opus/high]` — done 2026-11-12: `.claude/design/home_evidence/home_audit_architect_review_2026-11-12.md` (findings AR1-AR10, undecided items seen by an architect, decisions N2-N6) and the cheaper engine explained with measurements in `.claude/design/home_evidence/home_audit_forensics_2026-11-12.md` 3.2b; F8 and 3.7 corrected (a feature without audit never changes a plot: Eve's rule, not a loss). Scratch scripts in `tmpAI/architect/`.
- [x] **HOME-GATING-PAPER-1** `[opus/high]` — done 2026-11-12: `.claude/design/home_evidence/home_gating_and_test_configs_2026-11-12.md` (how filters are gated by configuration, preview vs audit capabilities, options G1-G4, companion rule R-a..R-c, test configurations C1-C4, 8 questions). Verified by running: scratch configurations validate by path and launch; a no-audit configuration offers My view; the "Exploration only" notice is gated by a proxy flag; the Export panel says "steps sent to audit" where none can exist; Rule 6 makes audit without Compare fatal.

### Manual-testing findings, 2026-11-10 (issues #53/#54/#55)

- [x] **#55** `[sonnet/low]` — Test Lab right sidebar showed nothing. Confirmed deliberate
  since #42 (2026-11-08), documented then as "a separate, smaller finding, out of scope,"
  but never turned into its own issue. The content (`_render_test_lab_right_info()`,
  `home_theater.py`) already existed and was already correct — only
  `config/ui/sidebars/testlab_standard_right.yaml` was stale (`visible: false, panels: []`).
  Flipped to `visible: true, panels: [{type: test_lab_right_info}]`. `SidebarValidator`:
  0 violations across all 8 app features templates.
- [x] **#53** `[sonnet/low]` — "I think the external exchange landed in blueprint and not in
  home panel." Real cause found: Blueprint's left sidebar has a panel literally titled
  "External Exchange" (recipe YAML upload/replace/append/download) — generic enough that
  Eve reasonably looked there first for the new reproducibility-bundle import (#48), which
  correctly lives in Home's Export panel (confirmed in code: no actual sidebar-config
  overlap). Renamed the Blueprint panel to "Recipe File Exchange" with an explicit note
  pointing at Home's Export panel for bundles (`wrangle_studio.py`). Also gave Home's
  `import_bundle_upload` file control a visible label (was `None`) and a one-line reminder
  of the same distinction. Updated the two active docs that still said "External Exchange"
  (`docs/reference/ui_style_guide.qmd`, `.claude/design/ui_panel_map_current.md`); left
  historical log/archive hits untouched.
- [x] **#54** `[sonnet/low]` — reproducibility bundle Import appeared to do nothing. Root
  cause: "Also include a reproducibility/reimport bundle" is unchecked by default at export
  time; importing a Mode-1-only bundle correctly refuses (`BundleImportError`, the 4-leg
  comparison table only renders on success) but the refusal rendered as small grey/red text
  under a long accordion — easy to read as "the feature does nothing." Added a hint at the
  checkbox itself ("check this now if you'll want to Import this bundle later"), reworded the
  file-control's help text to lead with the same requirement, and turned the error state into
  a proper red alert box instead of `ui.tags.small`. **Open:** whether "comparison to what
  was before" means something beyond the 4-leg hash table (e.g. a diff view against the
  currently-open recipe) — needs Eve's clarification, not assumed.
- [x] **Validate-button rule drift** `[sonnet/low]` — see the correction note under
  `VALIDATE-UI-1` below; `_handle_validate` now also runs `validate_data_analysis_recipe()`
  (the real `ConfigManager` load path) and surfaces the `factory_id` check row the coherence
  script already computed but the UI silently dropped.

### Reproducible export & import (ADR-097, 2026-11-09) — implementation order

- [x] **REPRO-SEED-1** `[sonnet/medium]` (#39/4A, part 1) — DONE 2026-11-09: `random_state`
  added as a recognised `aesthetic_override` key in `resolve_plot_config()`
  (`libs/viz_factory/src/viz_factory/plot_config_resolver.py`) — injected into every
  jitter-capable layer the resolved plot has (`geom_jitter`, `position_jitter`,
  `position_jitterdodge`, or any layer with `params.position` of `"jitter"`/`"jitterdodge"`),
  overriding any recipe-set `random_state` on that layer; a no-op when the plot has no jitter
  at all. 8 new unit tests (`TestResolvePlotConfigL5RandomState`) plus a live end-to-end check
  (same override seed → identical jitter across renders; different seed → different jitter).
  Full viz_factory suite (246) and full headless suite (1494) pass, no regressions.
- [x] **REPRO-SEED-2** `[sonnet/medium]` (#39/4A, part 2) — DONE 2026-11-09: automatic seed
  bookkeeping for the default case (`random_state: random`, no pinned override). Per plot,
  `_effective_random_state` (`@reactive.Calc`, `home_theater.py`) returns a pinned T3 override
  unchanged or draws one fresh `secrets.randbits(31)` seed; a separate idempotency-guarded
  `@reactive.Effect` (`_persist_drawn_seed`) is the only thing that writes it into
  `last_drawn_seeds` (new per-session `reactive.Value({})`, threaded through `server.py` →
  `home_theater.py` → `export_handlers.py`) — never inside the `@render.plot` itself (R1). The
  render reads the same Calc, so what's shown and what's bookkept always agree. Skips plots
  with no jitter at all (`layers_have_jitter`, factored out of REPRO-SEED-1's resolver code for
  reuse here) — verified against the real shipped `phenotype_genome_length_dotplot.yaml` plot
  (inline `position: jitter`), not just synthetic test data. Non-blocking notification added in
  `export_bundle_download` when any exported plot's seed is unpinned. `test_render_purity.py`
  (44, R1 check), full headless suite (1498), and the `qa` Playwright smoke suite (29) all pass.
- [x] **REPRO-PROV-1** `[sonnet/medium]` (#39/4A, part 3) — DONE 2026-11-09: consolidated
  provenance record (`build_export_provenance()`, `export_handlers.py`) now carries all four
  hash legs. Recipe/data unchanged (already existed). Engine leg is environment-aware,
  detected automatically, never asked of the user: containerized (`/.dockerenv` or `container`
  env var) → `image_ref` from `SPARMVET_IMAGE_REF` if set, `"not set"` if not (never a false
  pin); source install → existing `git_commit` + `uv_lock_sha256` (checked directly: this
  project has no `uv.lock` committed yet — recorded as `None`, a documented limitation, not a
  silent gap). New `t3_audit_steps_sha256` leg: `canonical_hash()` (`cache_keys.py`, reused,
  not reinvented) over `{t3_audit_steps_by_plot, t3_plot_overrides}` — confirmed missing before
  this (grep found zero hits, despite the field being named in the original
  `ui_implementation_contract.md §12f` spec). Surfaced in the existing README.txt
  "Reproducibility" section and report.qmd's hash table — no new UI. 13 provenance tests (6
  new) + full headless suite (1504) + real-download Playwright suite (4) all pass.
- [x] **REPRO-RESTORE-HASH-1** `[sonnet/low]` (#50, the hash-check half only — labels/multi-dataset
  distinction is separate, lower-priority UI work, not ordered here) — DONE 2026-11-09:
  `write_t3_ghost()` (`session_manager.py`) now computes and stores `t3_audit_steps_sha256`
  (via `cache_keys.canonical_hash`, same shape as export's leg) on every save;
  `list_t3_ghosts()` surfaces it (`""` for ghosts written before this field existed — "nothing
  to check", never a fabricated mismatch). `_restore_session()` (`session_handlers.py`)
  recomputes the hash from the ghost's own content and compares to its own stored value — a
  **self-consistency** check (the ghost file was corrupted/hand-edited), not a
  comparison-against-current (there is no independent "current" T3 before restore replaces
  it). While here, also fixed a second, adjacent gap found by the same read: the
  `data_batch_hash` mismatch warning was specified (`ui_implementation_contract.md §12d`) but,
  like the T3 hash, never actually implemented — only the recipe-sha check existed. Both are
  now checked, same non-blocking severity. 11 new/changed tests (`test_session_manager.py`),
  full headless suite (1508), `qa` Playwright smoke suite (29) all pass.
- [x] **REPRO-TRANSLATOR-1** `[sonnet/high]` (#47/4D) — DONE 2026-11-09:
  `libs/blueprint_arch/src/blueprint_arch/t3_translator.py`. Per plot, computes the full
  ordered translated-action sequence for that plot's `target_dataset` join (`exclusion_row`/
  `filter_row` → `filter_eq`/`filter_range`/`is_in` with the same eq/ne+list auto-promotion
  viz_factory applies at render time; `drop_column` → `drop_columns`; `aesthetic_override`
  skipped, not translated; `developer_raw_yaml` parsed and passed through after validating it's
  a list of canonical `action:` steps); forks the join under a plot-specific id in the returned
  copy only, appends the sequence after the join's existing `tier2:` steps (T2-then-T3,
  matching live behaviour; empty original `tier2` → fork's `tier2` is just the translated
  actions). Dedupes to a shared fork only when two plots' resulting sequences for the same join
  are byte-identical, computed independently per plot first — never grouped by propagation scope
  directly (ADR-097 decision 4; covered by dedicated multi-plot propagation tests). Marker
  convention decided: a structured `_t3_origin` dict key on the forked join (not a YAML
  comment) — round-trips through plain `yaml.safe_dump`/`safe_load`, directly machine-readable
  on read-back. **Engine-coverage gap found, not approximated:** no registered action exists
  for `ne`/strict `gt`/strict `lt`/`not_in` — filed as #52; a plot using one of these ops is
  named in the `skipped` return dict rather than silently exported as falsely reproducible.
  **A second real gap found and fixed:** `ConfigManager` injects an internal `plots:` mirror
  key into `raw_config` that breaks reload (`LEGACY-FLAT-PLOTS-1`) — confirmed live, now
  stripped unconditionally by `build_mode2_recipe()`. 40 unit tests
  (`test_t3_translator.py`) + verified live end-to-end against the real engine (not a mock):
  materialized the forked join's actual Tier 2 output via `DataOrchestrator` against the real
  shipped `2_test_data_ST22_dummy` recipe/data and confirmed it byte-identical to manually
  filtering the original join's Tier 1 the same way. Full headless suite (1548) passes.
  **Not yet done:** wiring this into the actual Mode 2 export (#45) or Import (#48) — this
  task built the translator itself, standalone and tested, not its integration.
- [x] **REPRO-EXPORT-MODES-1** `[sonnet/medium]` (#45/4B) — DONE 2026-11-09, **corrected once
  already** after Eve's review of the first pass (see ADR-097's implementation-status note for
  the full before/after). First pass kept Mode 1's recipe copy unchanged and invented a
  combined "Analysis ID" — both wrong. Corrected, settled design (confirmed against a native
  StarUML diagram, `docs/UML/app.mdj` HOME package, `EXP-MODES Export bundle contents by mode`,
  built live with her before the fix): **Mode 1 never includes the recipe or raw data** — only
  `report.qmd`, `plots/`, `README.txt`, `t3_steps.yaml`. **`effective_run.yaml` is written
  unconditionally, identical content either way**, at the bundle root — not scattered hash
  values restated as prose; this is the actual mechanism for proving two *separately* exported
  bundles correspond (diff it field by field — not eyeball, not one collapsed code, #48's job).
  **Mode 2** (opt-in checkbox, forces `export_scope: global`) adds the translator's frozen
  recipe (`data_analysis_recipes_reproducibility/<id>.yaml`) and the actual data files
  (`data_reproducibility/<dataset>.<ext>` — "needs all to be fully reproducible"); nothing
  Mode-2-only duplicates into Mode 1. `t3_translation_skipped` is a dict when Mode 2 ran, else
  an explicit "not attempted" string — never a fabricated empty dict implying nothing was
  skipped. README/report trimmed to point at `effective_run.yaml` instead of repeating the
  hash table. Playwright tests (real browser download, `qa`) updated/added: confirms Mode 1
  alone never has the recipe, `effective_run.yaml` is present either way with matching
  recipe/data hashes across both downloads, Mode 2 adds the recipe/data additively, the frozen
  recipe reloads cleanly (no leftover ConfigManager `plots:` key). Full `test_export_download.py`
  suite (5) and full headless suite (1548) pass.
- [x] **REPRO-SENSITIVE-1** `[haiku/low]` (#46/4C): DONE 2026-11-09. Non-blocking
  `_notify(..., type="warning", duration=12)` fired inside `export_bundle_download()`'s
  `if wants_mode2:` block, right after the raw data files are copied into
  `data_reproducibility/` — names that the bundle now carries the actual data and points at
  the user guide. New guidance added to `docs/user_guide/understanding_your_export.qmd`
  (section "Before you include your raw data"): anonymise before loading into the app, not at
  export time, and keep any de-anonymisation mapping file outside the SPARMVET_VIZ project
  folders entirely. While touching this area, also corrected now-stale claims left over from
  before REPRO-EXPORT-MODES-1/REPRO-SEED-2 in both `understanding_your_export.qmd` (three
  fingerprints → five fields of `effective_run.yaml`, added `t3_audit_steps_sha256` and
  `engine_fingerprint`/`git_commit` as comparison fields, added "Two things your export can
  be" explaining Mode 1 vs. the opt-in add-on) and `reproducible_plots.qmd` (it said SPARMVET
  "does not yet record" a drawn random seed and that reshuffling was "not available" — both
  now done by REPRO-SEED-2; rewrote the seed table and "Coming later" section accordingly).
  Depends on REPRO-EXPORT-MODES-1 (done).
- [x] **REPRO-IMPORT-1** `[sonnet/high]` (#48/4E): DONE 2026-11-09. New pure module
  `app/modules/bundle_importer.py` (`import_bundle`, `read_effective_run`, `ImportResult`,
  `LegResult`, `BundleImportError`) — a parallel importer, confirmed distinct from
  `SessionManager.export_session_zip`/`import_session_zip` (those only ever zip ghost metadata
  + source *paths*, never the recipe or data itself). File-based only (ADR-093): extracts
  `data_reproducibility/` into `raw_data_dir/_imported/<id>_imported_<timestamp>/`, repoints the
  frozen recipe's `data_schemas.*.source.path` at the extracted files, writes it into the real
  recipes directory, and writes a `SessionManager` assembly ghost under `_sessions/` — never
  touches a live `wrangle_studio`/`home_state` object. The imported recipe only becomes
  selectable after a reload (`Bootloader` resolves `available_data_analysis_recipes` once per
  process, ADR-094) — the UI and docs say so plainly rather than pretending otherwise. Four
  legs, non-blocking (`status`: `match`/`mismatch`/`not_checked`, never a refusal): **data**
  (always checkable — rehashes the bundle's own `data_reproducibility/` files against the
  recorded `data_batch_hash`); **engine** (this machine's `engine_fingerprint()`/`git_commit`
  vs. recorded — explains "software changed, not your analysis" per ADR-097 decision 3);
  **recipe** (only checkable, to avoid a guaranteed false mismatch, when the *original*
  untranslated recipe is found locally by id in `bootloader.available_data_analysis_recipes` —
  the frozen copy has T3 baked in by design and never hashes the same as the original);
  **t3_steps** (reported for reference, `not_checked` — no independent local source once T3
  only existed in the exporting session; compare two `effective_run.yaml` files instead).
  Found and fixed live, not just in review: calling `ConfigManager` (via
  `SessionManager.compute_data_analysis_recipe_sha256`) directly on an untrusted, just-written
  recipe would `sys.exit(1)` the whole Shiny process on a broken bundle (ADR-077's fail-fast
  behaviour, correct at app startup, fatal from inside a running request) — caught by the
  module's own headless test suite, fixed by gating with
  `data_analysis_recipe_validator.validate_data_analysis_recipe()` first (the same
  `SystemExit`-catching wrapper ADR-094's HOME load gate already uses) and raising
  `BundleImportError` instead. Wired into the Export panel (`export_handlers.py`'s
  `system_tools_ui`/new `import_bundle_report` output), gated on `export_enabled` alone —
  reachable without `test_lab_enabled` or `blueprint_enabled`, per the issue's done-when.
  `app/tests/test_bundle_importer.py` (16 tests, headless: writes a real tiny recipe, runs it
  through the real `build_mode2_recipe`, round-trips a hand-built bundle through
  `import_bundle`, covers every leg's match/mismatch/not_checked path, source repointing, the
  `SystemExit`-safety fix, and skipped-T3-plot passthrough). `test_export_download.py` gained
  `test_import_a_bundle_reports_the_four_legs` (real browser: ticks the reproducibility
  checkbox, downloads a real Mode 2 bundle, uploads it back through `#import_bundle_upload`,
  asserts the rendered report; cleans up the real recipe/data files it writes into the
  project tree in a `finally` block — confirmed by checking `git status` before/after, since
  Import's whole point is writing outside `tmp_path`). Full suites green: headless 1566
  (`libs app/tests`, up from 1548), Playwright `test_export_download.py` 6/6 and
  `test_shiny_smoke.py` 34 passed/3 skipped. Docs: `understanding_your_export.qmd` gained
  "Importing someone else's reproducibility bundle".
- [x] **ACTIONS-FILTER-GAPS-1** `[sonnet/medium]` (#52): DONE 2026-11-09. Closed the
  engine-coverage gap REPRO-TRANSLATOR-1 found and refused to approximate: no registered
  action existed for `ne`, strict `gt`/`lt`, or `not_in`. Added `filter_ne`, `filter_gt`,
  `filter_lt` (`libs/transformer/src/transformer/actions/cleaning/core.py`, next to
  `filter_eq`/`filter_range`, same silent-no-op-on-missing-params idiom) and `not_in`
  (`cleaning/analytical.py`, next to `is_in`, same `TransformationError`-on-missing-params
  idiom) — all four follow the existing pattern exactly, including `ui_schema` for the
  BLUEPRINT form catalog. `t3_translator.py`'s `_TRANSLATABLE_OPS` extended from
  `{eq, ge, le, in}` to all eight T3 filter ops (`eq, ne, gt, ge, lt, le, in, not_in`,
  `ui_implementation_contract.md §8`'s full op list); `translate_t3_node()` maps each to
  its action. The `ne`-with-list-value case, previously asserted to still raise, now
  correctly promotes to `not_in` and translates. Kept one defensive
  "unrecognised op still raises, never approximates" test (`op: "regex"`, not a real T3
  op) since every real op is now translatable — the two downstream tests that had used
  `op: "ne"` as their "this op is untranslatable" example were switched to the same bogus
  op, since `ne` no longer demonstrates that. Updated the authoritative action list
  (`rules_agent_role_bioscientist.md §8`). New `libs/transformer/tests/test_filter_actions.py`
  (11 tests, includes an is_in/not_in exact-complement check). `test_t3_translator.py`
  rewritten for all 8 ops (52 tests total, up from 40). Full headless suite 1578 passed
  (up from 1566).
- [x] **REPRO-SESSION-LABELS-1** `[sonnet/low]` (#50, the UI half): DONE 2026-11-09. Found a
  real bug while implementing, not just adding UI: `set_session_label`/`get_session_label`
  only ever read/wrote the most-recent T3 ghost — a brand-new session (`assembly.json` only,
  before any Apply) had no T3 ghost yet, so it silently could not be labelled at all.
  Canonical storage moved to `assembly.json` (`write_assembly_ghost` gained a `label: str |
  None = None` param — `None`, every real caller's default, preserves whatever label is
  already on disk across a recipe/data-change rewrite rather than wiping it; an explicit
  string sets/clears it). `get_session_label` falls back to the legacy T3-ghost location for
  sessions labelled before this fix. `list_all_sessions()` now returns `label` directly (no
  extra per-card lookup). UI: the static italic label text in `session_handlers.py`'s session
  card replaced with `ui.input_text(..., update_on="blur")` — no separate Save button. The
  scanning `@reactive.Effect` (same one restore/delete already use) saves only when the
  blurred value differs from the STORED label (R3 idempotent guard,
  `ui_implementation_contract.md §14`) — without it, any unrelated session action anywhere
  would re-fire this effect and re-write every label to its current box value on every pass.
  Deliberately does not bump `_session_list_version` on save: nothing else in the panel reads
  the label, and forcing a re-render would reset any *other* session's box mid-edit (R4).
  Distinguishing sessions of the same recipe against different data batches (the second
  done-when) is served by the same free-text label, since a hash prefix alone isn't
  meaningfully distinguishable to a user. 8 new headless tests
  (`app/tests/test_session_manager.py`, including the before-any-T3-ghost case and the
  reassembly-preserves-label case) + 1 new Playwright test
  (`test_shiny_smoke.py::TestSessionListRefresh::test_session_label_saves_on_blur`, fills,
  tabs to blur, asserts the backend actually stored it). Full suites green: headless 1583
  (up from 1578).
- [x] **REPRO-RESHUFFLE-1** `[sonnet/medium]` (#49): DONE 2026-11-09. "🔀 Reshuffle
  arrangement" button (`app/handlers/home_theater.py`, `_make_plot_cell_handler`'s
  `_plot_reshuffle_ui`/`_handle_reshuffle`, registered per known plot id — not a scan over
  dynamic ids, plot ids are known upfront from the recipe) next to the plot badge, its own
  narrow output — never a revival of the Plot Style panel (stays unmounted, fork issue #15,
  `ui_implementation_contract.md §12g.9`). Visibility (new `recipe_pins_random_state()`,
  `libs/viz_factory/src/viz_factory/plot_config_resolver.py`, next to `layers_have_jitter`):
  hidden unless the plot has a jitter-capable layer AND neither the recipe itself (a fixed
  `random_state` number in the layer's own params) nor a T3 override has already pinned a
  seed. Click → draws `secrets.randbits(31)` and writes it into
  `home_state['t3_plot_overrides'][subtab]['random_state']` (an `@reactive.Effect`, R2) — the
  existing `_effective_random_state` Calc (REPRO-SEED-2) picks it up on its own, no new
  render-side plumbing needed, and the button then hides itself (nothing left to reshuffle
  from until the pin is removed some other way — no unpin control, not asked for). Found and
  fixed two real bugs via the Playwright test, not just in review: (1) the output wrapper's
  id and the button's own id were both `plot_reshuffle_{p_id}` — an invalid DOM id collision
  that made every selector match two elements; split into `plot_reshuffle_{p_id}` (wrapper)
  and `plot_reshuffle_btn_{p_id}` (button). (2) The visibility render wrapped its
  `home_state.get()` read in `reactive.isolate()` (copied from `_plot_cell_ui`'s *different*
  use of isolate, for collapse state) — this silently prevented the button from ever
  reacting to its own pin, so it never hid itself after a click; removed the isolate, this
  render must react to `home_state`. Checked against `COM-REACTIVE Reactive wiring of HOME`
  (`docs/UML/app.mdj`) before skipping a UML update: the diagram tracks
  `home_state → plot_group of each plot` at the whole-plot-cell granularity, already covers
  this addition, no new box needed. 6 new headless tests
  (`libs/viz_factory/tests/test_plot_config_resolver.py::TestRecipePinsRandomState`) + 3 new
  Playwright tests (`test_shiny_smoke.py::TestReshuffleControl`: shown when meaningful, absent
  on a non-jitter plot, click pins and hides). Docs: `reproducible_plots.qmd`'s "Coming
  later" section and `reproducibility_same_input_same_output.qmd`'s open question both
  updated — this was the feature either one described as not yet built. Full suites green:
  headless 1589 (up from 1583).

### Audit Fixes — ADR Compliance (ADR behavioural audit 2026-11-06)

- [x] **ADR-045-PLOTERR-1** `[AUDIT]` `[sonnet/low]`: `architect_active_plot` (`@render.plot`, `app/modules/wrangle_studio.py` lines 552-607) calls `_plot_error.set(...)` six times. This breaks the reactive write rule R1 (`ui_implementation_contract.md §14`): renders are read-only. Fix: compute the error text in a `@reactive.Calc` (or write it from a `@reactive.Effect` with an idempotent guard) and let the render only read it. Affects BLUEPRINT (demo scope). Add a Playwright or unit check that the Blueprint plot still shows its error banner. DONE 2026-11-06: the error text is computed in the `_plot_outcome` Calc; `app/tests/test_render_purity.py` fails if any render in `app/` writes a reactive value. The error banner itself is not covered by an automated test (check by hand in BLUEPRINT).
- [x] **ADR-045-SERVER-SIZE-1** `[AUDIT]` `[sonnet/medium]`: `app/src/server.py` has 287 lines; `rules_app_structure.md §3` sets a hard limit of ~250. Find what is not shared state, a shared calc or a `define_server` call, and move it to a handler or module. DONE 2026-11-06: the excess was dead code (`tier_reference`, `tier3_leaf`, `apply_tier2_transforms` and the unmounted outputs `plot_reference`, `table_reference`, `plot_leaf`, `table_leaf`, `handle_plot_brush`), removed; `server.py` is 237 lines.

### Clean-up recheck 2026-11-06 (dead code, old tests, documentation)

- [x] **DEAD-CODE-REVIEW-1** `[sonnet/medium]` (done 2026-11-07, re-verified every item by grep, not relying on the 2026-11-06 scan): dependency sweep per `rules_legacy_management.md` §6 for each item.
  **Deleted (confirmed zero real callers anywhere, including tests):**
  - `app/modules/wrangle_studio.py` `_fields_table` (a "backward compat" alias with no caller) and `_parse_fields_safe` (a complete method, but superseded — `_fields_cards`, the one actually used, reimplements the same dict/list normalisation inline with the *opposite* legacy-format convention; `_parse_fields_safe` was never wired to anything).
  - `libs/ingestion/src/ingestion/ingestor.py` `validate_schema` — unused AND incomplete (`# For now, simply confirming we can read the raw columns. Strict validation... will occur here.` — never finished, never called).
  - `libs/connector/src/connector/galaxy_connector.py` — a **second, different** `GalaxyConnector` class (BioBlend-based, not the real `galaxy.py` GxIT wrapper `__init__.py` actually exports). A 37-line mock stub (`bioblend` isn't even installed; its own `@deps consumed_by:` claim of `connector/__init__.py`/`bootloader.py` was false, same false-claim pattern as the `adapter_*.py` files deleted for F-12). Deleted the whole file.
  Verified: `from app.src.server import server` clean, `libs/connector/tests` (27), `libs/ingestion`+`app/tests` headless (510), full headless suite (1444), Blueprint Playwright suite (12) all pass. `build_dep_graph.py` rerun.
  **Kept, unused but not dead** (complete, correct, zero cost to leave; deleting would remove sanctioned infrastructure nobody has adopted yet, not fix anything): `bootloader.py` `get_python_path()` (recommended by `audit_hardcoded_config.py`'s own warning text as the replacement for hardcoded `python3`, just not yet adopted anywhere), `libs/utils/src/utils/debug_output.py` `get_debug_out_dir()` (implements the `tmpAI/YYYY-MM-DD/[label]/` convention of `rules_verification_testing.md §6`, no debug script uses the helper yet), `libs/id_reconciliation/.../core.py` `suggest_patterns` and `libs/viz_gallery/.../gallery_manager.py` `list_submissions` (thin, correct, documented public methods on classes whose *other* methods — `precheck_compatibility`/`reconcile`, `rebuild_index`/`submit_example` — are actively used; `rebuild_index` itself turned out NOT dead, see F-18).
  **Already tracked elsewhere, no new action:** `app/modules/help_registry.py` (whole module unused) and `app/modules/exporter.py` (`bundle_package`, `render_audit_report`, imported only by tests) → `HELP-FROM-DOCS-1` (F-20). `app/modules/gallery_viewer.py` `submission_modal_ui`, `autofill_meta_from_audit` (gallery submission, unwired) → noted in `docs/UML/risks_and_technical_debt.md` (F-18). `libs/blueprint_arch/.../agent_adapter.py` etc. are **not dead** — ADR-076's `claude_cli` backend is wired and working; `claude_api`/`local` are the deliberate Phase-2 gap tracked at `CONFIG-AGENT-BACKENDS-1` and `BLUEPRINT-AGENT-API-1`.
  **Needs Eve's call, moved to Needs Discussion (not deleted — real, substantial work, just incomplete):**
  - `app/handlers/blueprint_handlers.py:203 _undo()` — the undo *capture* side (`_snapshot_state`, the 20-step deque, draft persistence/restore) is fully wired and working; the *restore* side (`_undo()` itself, which pops the deque and calls `wrangle_studio.logic_stack.set(...)`) has zero callers — no "Undo" button exists anywhere in the UI. BP-UNDO-1 (`rules_ui_dashboard.md §7`) was half-built. See `UNDO-WIRE-1` below.
  - `app/src/render/pipeline_error_renderers.py` (whole module: `dispatch_pipeline_error` + 5 surface renderers, ADR-079) — zero importers anywhere, but this is not simple dead code: `PipelineError` itself IS actively raised in 7 production files (`data_assembler.py`, `data_wrangler.py`, `ingestor.py`, `viz_factory.py`, `audit_stack.py`, `blueprint_handlers.py`) and nothing anywhere catches it — no `except PipelineError` exists in `app/`. The structured 5-surface rendering design (plot overlay, toast, audit panel row, data-import banner, Blueprint inline) was built and unit-tested on the producer side (`make_render_payload`, tested in isolation) but the consumer/dispatch side was never wired to any of those 7 raise points. See `PIPELINE-ERROR-WIRE-1` below.
- [x] **PIPELINE-ERROR-WIRE-1** `[opus/medium]` (decided 2026-11-08, Eve: wire it, not remove it — ADR-094). While wiring this, found the catch side was not pure zero: `home_theater.py`'s VizFactory render path (line ~475, `DIAG-RUNTIME-AUDIT-1`) already captured failures into `session_pipeline_errors`, and `audit_stack.py`'s `pipeline_issues_ui` already rendered them in the right sidebar — just with a hand-rolled dict shape, not `PipelineError`/`make_render_payload`/`dispatch_pipeline_error`, and only for that one catch point. Extended the same pattern to the data-materialization catch point (`_resolve_active_lf` failures in `_group_plot_handler`) — now PipelineError-aware (uses `.component`/`.problem`/`.fix`/`.who` when the caught exception is one). `app/src/render/pipeline_error_renderers.py`'s renderers (`dispatch_pipeline_error` etc.) are still not called by anything — the existing capture path renders its dict shape directly in `pipeline_issues_ui` rather than through them; reconciling the two is part of the remaining scope. See `PIPELINE-ERROR-WIRE-2` for what's left: the other 5 retrofit targets (VizFactory render failures beyond the existing capture, T3 Apply, Blueprint inline, Data Import panel) and reconciling the renderer module with the dict-shape capture already in use.
- [x] **PIPELINE-ERROR-WIRE-2** `[opus/medium]` (closed 2026-11-08, ADR-095). **(b) Blueprint inline done first** (Eve: "if it is built then it should be wired... the detection and guidance text need to reach the screen"): all 3 `blueprint_handlers.py` catch points now call `make_render_payload()` and render inline via `render_blueprint_inline()` (extended to include `fix_md`, which it previously omitted). **Then, finishing (b)'s other three targets, found a bigger problem:** every one of the 24 `PipelineError` construction sites across `ingestor.py`/`data_assembler.py`/`data_wrangler.py`/`viz_factory.py` built a rich `PipelineError`, printed it, then discarded it for a plain `SPARMVET_Error` carrying only message+tip — ADR-079's own `to_pipeline_error()` adapter was never implemented anywhere, so the `isinstance(e, PipelineError)` check added earlier today could never actually fire for a real library error. Fixed at the root (ADR-095): `errors.py`'s `SPARMVET_Error` now carries the original `PipelineError` via an optional kwarg (no breaking change), all 19 raising sites updated, new shared `capture_entry()` helper replaces the broken isinstance check everywhere. VizFactory ("beyond the one existing catch point" = `_cmp_baseline_handler`, the Comparison Mode twin, found with its data-materialization capture missing entirely) and T3 Apply (two silent `PipelineError`s found along the way: the gatekeeper-blocked message, now showing the fix text though the path is effectively unreachable since `btn_apply` is HTML-disabled while blocked; `_write_t3_ghost`'s failure, now a real reachable fix — ghost save failing silently meant T3 state lost on refresh with zero warning) are closed. Export's per-plot error stub also enriched. (a) Data Import panel target turned out to be based on an imprecise premise — real `IngestionError` already flows through the HOME data-materialization path already fixed; no separate catch point existed to wire. (c)/(d) unchanged from the 2026-11-08 earlier note: export report.qmd section already done; T3 Ghost `pipeline_errors:` list still not done. Proven: new unit tests in `test_pipeline_error.py` (carry-through + `capture_entry`) and `test_write_t3_ghost_warning.py`, both mutation-proven; headless suite 1459; full Playwright suite (HOME/Blueprint/export/every-app-features) run clean.
  **Still open, new scope from this pass:** `PIPELINE-WARNING-SURFACE-1` (4 non-raising "warning" PipelineError sites in ingestor.py/viz_factory.py print to console only — needs a return-value/callback mechanism, not an exception catch, since nothing raises); deciding whether `dispatch_pipeline_error()`'s surface renderers should replace the dict-capture pattern now used everywhere, or be reconciled to it; T3 Ghost `pipeline_errors:` list extension (ADR-079 Phase 3).
- [x] **PROCESSING-ISSUES-RENAME-1** `[sonnet/medium]` (done 2026-11-08, finding F-26, `.claude/tasks/uml_findings.md`): `audit_stack.py`'s `pipeline_issues_ui` was built but never mounted in the DOM (traced to the original commit, predates this session). Renamed throughout — `pipeline_issues_ui` → `processing_issues_ui`, `session_pipeline_errors` → `session_processing_issues`, the `id="pipeline_issues_panel"` DOM id, the inner "Runtime issues" heading, every `@deps` block, ADR-079/ADR-094/ADR-095 text, `cross_cutting_concepts.md`, `data_contract_and_failures.md`, `project_conventions.md`, `report.qmd`'s section title, README.txt's count-line text — to resolve the collision with `CTX-1`'s "Analysis pipeline" C4 actor (external upstream Abromics/VIGAS-P system, a different thing from this app's own internal processing). Mounted on the **left** sidebar, not the right, per `.claude/design/ui_reachability_map.md` (new, this session): new `processing_issues` panel type in `sidebar_registry.py` (`gate_flag: None`), added to the shared `home_standard_left.yaml` used by all 8 app features files. Verified: app import clean, `test_shiny_smoke.py` (21 passed), `test_every_app_features_starts.py` with a new permanent regression assertion that the output is mounted in every app features (9 passed), mutation-tested (removed the slot, confirmed `pipeline-static` fails with the expected message, restored, confirmed it passes).
- [x] **DOC-RECHECK-2** `[sonnet/medium]` (done 2026-11-07, all 7 points checked):
  1. "Comparison Theater" → ADR-086 terms ("Compare Result vs My view" / "Comparison Mode") in `docs/index.qmd`, `docs/workflows/visualisation_factory.qmd`, `docs/reference/ui_style_guide.qmd`. `Terminology.qmd` never had the term (checked, clean) — also fixed a real bug there while at it: it described "Wrangle Studio" as "available within the Test Lab", which is wrong — Blueprint Architect and Test Lab are separate, independently-gated user spaces. The 3 links to the archived `docs/appendix/data_lifecycle_theater.qmd` redirected to its stated replacement, `docs/user_guide/audit_pipeline.qmd` (the archived file's own banner names it; left the archived file untouched, it's already correctly marked HISTORICAL).
  2. `docs/vision/platform_evolution.qmd`'s Figshare example used the old `joins: - anchor:/join: [...]` shorthand (forbidden since rules §7). Corrected to the real, canonical `action: join` / `right_ingredient:` / quoted `'on':` syntax actually used in `config/data_analysis_recipes/pipelines/figshare_integration/wrangling/figshare_triple_join_steps.yaml` (this gallery example is real and shipped, not hypothetical).
  3. `.claude/design/ui_panel_map_current.md` — one-line fix, "Global Export accordion" → "Export accordion (renamed... 2026-05-04)". `export_specification.md` — added a proper `**Status:** IMPLEMENTED` banner (was still "AGREED — pending implementation" despite the design being fully live); noted `single_graph_export_handlers.py` was deleted outright, not "merged" as the spec's own §8 implied.
  4. `project_conventions.md` §E corrected: L1-L4 of the plot config cascade are implemented (checked `resolve_plot_config()` is wired into `viz_factory.py`); only L5 (T3 `aesthetic_override`) remains open, matching `rules_viz_factory.md §7`'s per-task ✓/open status. Also fixed two adjacent stale "to be created" file-registry rows for files that already exist (`plot_config_resolver.py`, `pipeline_error.py`), and a wrong path (`viz_factory.py` missing its package directory).
  5. DOC-GAP-2/3/5 (May) are untraceable — no definition found anywhere outside this one line. Spot-checked their described content directly instead: README.md has no `ExcelHandler`/"Comparison Theater" claims (already clean), the ADR-074 Programmatic Lineage API section of the deployment guide matches the real public API (`rules_app_structure.md §4`). Nothing to fix.
  6. `docs/_freeze/` is git-ignored (`.gitignore:27`) — confirmed "ignore" is correct, not tracked so nothing to re-render for a commit.
  7. Ran the three `rules_legacy_management.md §5` audit greps. Check 1 (unmarked deprecated-sounding prose) is mostly past-tense documentation, not actionable — spot-checked the highest-signal hits. Check 2 found one genuine violation: `assets/scripts/materialize_data_analysis_recipe_plots.py`, marked "DEPRECATED SHIM" in its own docstring with no linked task — added a proper banner and opened `LEGACY-MATERIALIZE-SHIM-REMOVE-1`. The `architecture_decisions.md:58` hit is an ADR entry correctly pointing to its own superseding ADR (ADR-032) — that's the ADR log's built-in convention, not a violation. Check 3 (tombstone expiry) found nothing past its stated phase.
- [x] **AUDIT-GATE-UI-1** `[sonnet/medium]` (done 2026-11-07): `app/tests/test_shiny_smoke.py::TestAuditGate::test_unreasoned_node_blocks_apply_then_reason_unblocks_it` — switches to My view (T3), adds a filter row, sends it to audit (accepting the default propagation scope), asserts `#btn_apply` reads "Apply ⛔" and is disabled, fills the `t3_reason_*` input, asserts it flips to "Apply" and enabled. Proven by mutation: stubbing `gatekeeper_blocked()` to always return `[]` makes the test fail on the first assertion (button shows "Apply", not "Apply ⛔"); restoring it passes along with the rest of the smoke suite (21/21, +3 skipped).
- [x] **VALIDATE-UI-1** `[sonnet/medium]` (done 2026-11-08): issue #26. `validate_data_analysis_recipe_data()` (issue #18) was written and tested but called from nowhere in the running app — the one wired button, BP-VALIDATE-1, explicitly skipped it (`--skip-tsv`). Found while writing up the "process of failures" for Eve and confirmed against `rules_agent_role_bioscientist.md`'s own "Silent Skip Warning": a mismatched `input_fields`/`output_fields` column name was silently skipped with zero warning anywhere in the app. `_handle_validate` (`blueprint_handlers.py`) now runs both checks and merges them: structure (existing subprocess) + data-vs-contract (now wired), shown as a fifth check row plus a detail list (location, problem, "did you mean" tip) for any data-contract problem. Proven by mutation: disabling the new `checks.append` call makes `test_validate_runs_the_data_contract_check` fail (assertion on the "data vs contract" row text); restoring it, that test plus the full Blueprint Playwright suite (14/14) and the headless suite (1444) pass. **Not done:** auto-run on data analysis recipe upload (the structure subprocess check alone can take up to 30s — auto-firing it on every upload is a separate UX/perf decision, not bundled into this fix).
  **Correction, 2026-11-10 (issue #53):** this entry's "structure (existing subprocess)" phrase masked a real gap — the "structure" check was *only* `audit_data_analysis_recipe_coherence.py`, a hand-rolled static script that never calls `ConfigManager`. `validate_data_analysis_recipe()` (the function `VALIDATE-UI-1` names in its own id and that HOME's load gate, ADR-094, uses) was **never actually called from Validate** until now. This meant Validate could PASS a recipe with `id:` != file name (ADR-092) or a flat (non-tiered) wrangling list (LEGACY-FLAT-WRANGLING-1) — both hard rejections at real load time — because neither check path the button ran touches the real engine. Found via Eve's manual testing ("ensure it checks the recipe according to the latest rules... to ensure it does not validate something not working"). Fixed: `_handle_validate` now runs three checks (engine load via `validate_data_analysis_recipe`, the static coherence script, data-vs-contract), none superseding the others. Also fixed a second, smaller gap found while re-reading: the coherence script already computed and reported `factory_id_violations` (deprecated key, ADR-083) in its markdown output and in `overall_pass`, but the Blueprint UI's `_count()` calls never surfaced it as its own check row — added.

### Export consistency (the export holds the Result plus the audited steps; exploration is never exported), added 2026-11-06

- [x] **EXPORT-KEYCHECK-1** `[opus/high]` (done 2026-11-06, Eve: block, never better safe than sorry): the export compares the keys the open view was built on with the keys now. If the data analysis recipe (any file) or the data changed, nothing is exported: an error notification explains it and the download holds only `EXPORT_NOT_CREATED.txt` (what it means, reload with F5, check, export again, both sets of keys). Tests: `test_export_view_consistency.py`, `test_export_download.py`.
- [x] **EXPORT-T3-1** `[sonnet/medium]` (done 2026-11-06, corrected after Eve's clarification, issue #25): build rule T3 > T2 > T1 (stored Tier 2, which is Tier 1 without tier2 steps). The export is the Result plus the AUDITED T3 steps (rows, drops, aesthetic overrides, trail), always applied to the exported plot and its data; exploration (filters tried in T1/T2/My view, not sent to audit) is a sandbox and is never exported, from any view (no checkbox, no `FILTERS.txt`). T3 data is one file per plot with audited steps (`T3_data_<plot>.tsv`), built by `audited_frame`. `tier3_leaf` is gone (ADR-045-SERVER-SIZE-1). Still open: a hash of the audit steps in the report.
- [x] **EXPORT-T3-UX-1** (decided 2026-11-06, Eve): no message about left-out T3 steps is needed, because audited steps are never left out. What is not audited is a sandbox: a reminder says so (Export panel, and under the filter buttons in My view). Done in issue #25.

### Configuration vocabulary and launch variables (ADR-091, proposed 2026-11-07, revised: one pass, no hybrid)

- [x] **CONFIG-VOCAB-REVIEW-1** (done 2026-11-07, decisions in ADR-091) `[opus/high]`: Eve reviews ADR-091 and the issue draft and decides open points 1 to 5 of the ADR (key renames, launcher, operator lock, "agent role" wording, IRIDA check). Issue #27 is created.
- [x] **CONFIG-INVENTORY-1** (done 2026-11-07) `[sonnet/medium]`: read-only inventory of every key in `config/deployment/*` and `config/app_features/*` (used / unused / wrong home, with the line that reads it), output in `.claude/logs/`; Eve reviews. Depends: CONFIG-VOCAB-REVIEW-1.
- [x] **CONFIG-MAPPING-1** (done 2026-11-07, rules and table in assets/scripts/rename_vocabulary*) `[sonnet/high]`: script output of every word, path and key containing app features, data analysis recipe or step list, with meaning and new name; Eve approves. Depends: CONFIG-INVENTORY-1.
- [x] **CONFIG-RENAME-1** (done on branch rename/config-vocabulary 2026-11-07, merge after the retest) `[sonnet/high]`: dry run, real run with `git mv`, startup errors for old variables and keys, `default_data_analysis_recipe` takes effect, `~` and `${VAR}` expansion, delete `logic_access`, `app_features_name`, `data_import_panel_visible` (absorbs LEGACY-DATAIMPORT-FLAG-1), migration script for files and sessions, old-words audit added to the audit registry, docs and launch commands updated. Depends: CONFIG-MAPPING-1.
- [x] **CONFIG-PROJECT-WORD-1** (done 2026-11-07) audit:allow-old-word (issue evezeyl/SPARMVET_VIZ#29, mapping in `.claude/tasks/outdated/project_word_mapping.md`) `[sonnet/high]`: one name for the recipe, no "project" for it; Info panel shows `info:`; remove recipe `type:`; "Deployment palette"; `standalone` -> `standalone`; rewrite Terminology.qmd. Gate: retest of #27 done or folded in.
- [x] **CONFIG-BLUEPRINT-FLAG-1** (done 2026-11-07, ADR-092, issue evezeyl/SPARMVET_VIZ#30) `[sonnet/high]`: `blueprint_enabled` alone controls the Blueprint Architect; `developer_mode_enabled` and `wrangle_studio_enabled` retired; blank page of standalone and advanced fixed.
- [x] **CONFIG-DATA-ANALYSIS-RECIPE-ID-1** (done 2026-11-07, ADR-092, issue evezeyl/SPARMVET_VIZ#31) `[sonnet/medium]`: the `id:` key equals the file name; validator, test, rule, files corrected.
- [x] **CONFIG-TESTLAB-DATA-ANALYSIS-RECIPE-CHOICE-1** (done 2026-11-07/08, issue evezeyl/SPARMVET_VIZ#33, closed) `[sonnet/medium]`: Test Lab's sidebar branch fixed (was falling through to Home's full panel set); Alerts moved to the left sidebar for Gallery/Blueprint/Test Lab; Test Lab got its own `test_lab_info` placeholder panel. The open question this entry used to track — migrate Gallery/Blueprint's sidebars onto the registry, or correct the yamls to admit they're bypassed — is decided: **migrate for real**. Eve, 2026-11-08, after walking through the tradeoffs: "makes it more separation of concerns and that means its the good choice." Tracked as its own issue, not re-opening #33: **issue evezeyl/SPARMVET_VIZ#42**.
- [x] **SIDEBAR-UNIFY-1** (done 2026-11-08/09, issue evezeyl/SPARMVET_VIZ#42, closed) `[sonnet/high]`: unified left AND right sidebar construction for all 4 workspaces through the slot registry. Phase 1: Gallery left (`gallery_main` freestanding panel). Phase 2: Blueprint left (~140 lines moved into `WrangleStudio.build_sidebar_ui()`, `blueprint_main` freestanding panel). Phase 3: right sidebar, all 4 workspaces (`_build_right_sidebar` + `_right_panel_renderers`; Blueprint decomposed into 5 real panels — found `blueprint_standard_right.yaml` had the exact same bypass-plus-stale-yaml bug as the left side, undetected until this phase). Phase 4: docs (`ui_implementation_contract.md §11d/e`, ADR-073 second amendment, `uml_findings.md` F-01), `PANEL_REGISTRY` cleanup (3 dead entries removed), `@deps`/dep-graph. Phase 5: full regression sweep — headless (1478), Playwright (49 + 9 every-app-features), strict validator, `audit_uml_model.py`, all clean; grep-confirmed zero hardcoded sidebar-construction branches remain in either `sidebar_tools_ui()` or `right_sidebar_content_ui()`. One new regression test closed a real coverage gap found along the way (`test_blueprint_right_sidebar_shows_its_panels` — nothing previously checked that panel's content). Every new wiring mutation-tested. Done overnight while Eve rested, one commit per phase, no behavior change anywhere.
- [x] **CONFIG-BLUEPRINT-ID-DISPLAY-1** (done 2026-11-07, issue evezeyl/SPARMVET_VIZ#34) `[sonnet/low]`: the Blueprint selector ("Master data analysis recipe") listed file paths while the Home selector already listed ids. Both `_init_wrangle_data_analysis_recipes()` and the "create new" refresh in `blueprint_handlers.py` now build `choices` as `{path: id}` (id = `Path(p).stem`, per ADR-092 "id equals file name") instead of a flat path list — the option value is still the path, only the visible label changed. Proven by mutation: reverting to the flat-list form makes the new Playwright test `test_data_analysis_recipe_selector_shows_id_not_path` fail with the full path visible; restoring it passes (13/13 Blueprint suite green).
- [x] **CONFIG-AUDIT-FIXES-1** (done 2026-11-07, steps 1 to 7, issue evezeyl/SPARMVET_VIZ#32) `[sonnet/medium]`: plan in `.claude/tasks/outdated/audit_findings_2026-11-07.md` (the failures of the scheduled audits that the rename did not cause: missing `@deps` block, placeholder paths in docs, stale Violet Law references, missing `rules_toolchain.md`, `complex_template` that does not load, no load test of templates).
- [x] **ADR-037-GAP-1** (done 2026-11-07, finding F-21, `.claude/tasks/uml_findings.md`; found by `assets/scripts/audit_uml_model.py`'s first run) `[sonnet/low]`: "ADR-037" was cited in 4 places for the Gallery index-only-filtering rule with no `## ADR-037` heading ever written (git history traces the dangling citation to commit `cdb2b7a`, 2026-04-19). Wrote the missing entry from the already-consistent citing text.
- [x] **CONFIG-GHOST-DOC-1** (done 2026-11-07: user_preferences.qmd describes the event-driven saving) `[sonnet/low]`: `docs/workflows/user_preferences.qmd` (Quarto page) promises a debounced autosave every 2 minutes (`ghost_save_trigger`) that was never built; the saving is event-driven (Apply, leaving Home, assembly). Correct the page, delete `ghost_save.frequency_minutes`. Part of the docs phase.
- [x] **CONFIG-SETTINGS-CLEAN-1** (done 2026-11-07) `[haiku/low]`: remove the stale allow-list entries (old commands and paths) from `.claude/settings.json`; review the diff.
- [x] **CONFIG-BRANDING-1** (done 2026-11-07 (branding block in the deployment file)) `[sonnet/medium]`: move `theme_css` and the banner (`logo_url`, title) from the app features files to a `branding:` block in the deployment file; the base stylesheet always loads from the code root and the deployment stylesheet holds only the differences. Behaviour phase of the rename (phase 9), with an error for the old keys.

### LAB-WORKFLOW follow-up

- [x] **LAB-WORKFLOW-QMD-1** `[sonnet/low]` `[doc-sync]` (done 2026-11-07): `docs/workflows/developer_workflow.qmd` — the four-stage producer journey (TEST_LAB prepare/scaffold → GALLERY inspiration → BLUEPRINT build → HOME run), recommended (never enforced) orderings, the export-then-choose linking model, and why cross-space handoffs stay file-based (independent app features flags). Links back to `.claude/design/developer_workflow.md` for the full design record rather than duplicating it, per `rules_documentation_aesthetics.md §4`. Added to `docs/_quarto.yml` Chapter 2 nav, between `workflows/wrangling.qmd` and `user_guide/system_transparency.qmd`. Verified: `check_doc_links.py` clean, `quarto render --no-execute` builds without error.

### Blocked until live app testing is finished (TOOLS / UML chain, added 2026-11-04)

- [x] **TOOLS-TOOLCHAIN-1** (done 2026-11-07: `.claude/rules/rules_toolchain.md`, linked from CLAUDE.md 3.2 and the master index) `[sonnet/low]`: Create `.claude/rules/rules_toolchain.md` = tools needed to build SPARMVET_VIZ (uv, `./.venv`, pytest, Playwright, Quarto, Mermaid CLI, podman/docker, git/gh, StarUML marked "pending TOOLS-UML-1"), with what each is for and how to call it. Link it from `CLAUDE.md` section 3.2 (rules table) and `workspace_standard.md` master index. Must not depend on `~/.claude/CLAUDE.md` or `my-mentoring/toolbox.md` (collaborators and CI do not have them). Personal tools (Gmail, Zotero, YouTrack, bio-research plugin) stay out. Done when: a fresh clone's agent can list the build tools from repo files alone.
- [x] **TOOLS-UML-1** (done 2026-11-07: shared tool in `OBSWORK/_bin/staruml/`, MCP servers `staruml` and `staruml-bridge` at user scope, not per repo) `[sonnet/medium]`: StarUML MCP setup. Depends on `[@user] TOOLS-UML-0` (licence decided and StarUML installed). Add repo `.mcp.json` entry for the StarUML MCP server, add `mcp__staruml__*` permissions to `.claude/settings.json`, update `rules_toolchain.md` (remove "pending"). Check first: StarUML >= 7.0.0 and Node >= 22 (Node 25 is installed); which MCP package is the official one (`staruml-mcp-server` listing vs community `staruml-mcp`); transport (stdio vs HTTP). Done when: agent can create one test element in a running StarUML and Eve sees it.

- [x] **LEGACY-MATERIALIZE-SHIM-REMOVE-1** (done 2026-11-13): the forwarding shim `assets/scripts/materialize_data_analysis_recipe_plots.py` was deleted; the docs (`FAQ.qmd`, `running_helper_scripts.qmd`, `visualisation_factory.qmd`), `libs/viz_factory/README.md` and `assets/scripts/README.md` name `libs/viz_factory/tests/debug_gallery.py` instead.

- [x] **STRICT-IMPORT-1** (done 2026-11-13, Eve decided; spec O22): only the declared `input_fields` enter; a declared column the file lacks fails; `original_name` matches exactly; the import reports the undeclared file columns left out (`libs/ingestion/src/ingestion/ingestor.py`, tests `libs/ingestion/tests/test_strict_import.py`). Recipes fixed: `metadata_schema` `original_name` `Sample_ID` to `sample_id` (the file header), `L50` declared on Quast, the QA canary casts L50 to Int64 explicitly. Headless 2119 passed; browser gate 70 passed, 3 skipped; retest walkthrough 14 of 14.
