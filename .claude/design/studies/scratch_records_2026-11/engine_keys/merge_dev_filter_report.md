# Merge dev (filter form) into task/engine-keys

Commits: 1724966b (merge --no-ff dev 8f8474a9, no conflict, no manual resolution), 57831da3 (dependency index regenerated, own commit). Worktree clean, no app running.

## Meaning check (holds, nothing patched)
- Footer names and path helper exist unchanged: app/modules/orchestrator.py:22 TIER1_KEY_META="sparmvet_tier1_key", :24 TIER2_KEY_META, :27 tier2_path_for (`<stem>__T2.parquet`). t3_audit_engine.py:30 imports them; stored_key :722 reads the footer with pl.read_parquet_metadata; stored_table_identity :732-752.
- Tier-1 key: footer is written from built_from.tier1_key (orchestrator.py:236, 288, 324), where built_from = compute_data_analysis_recipe_keys(...) (:211, :235). The view holds keys from the same function (home_theater.py:287-296 `_data_analysis_recipe_keys`, used at :352 for the form). Same function, same inputs, so equal when nothing changed. They can differ only when inputs changed between the view's keys and the build (built_from is recomputed at :235); then the table is returned unstored with `unchanged()` false (the `_unstored_builds` counter covers it) or the footer is newer: the identity differs, the form rebuilds. That is the intended direction (a doubt is never equal); no false-equal case found.
- Tier-1 engine change: tier1_key(material, batch, engines) cache_keys.py:131-133 takes tier1_engines(raw) :113-118, so the footer key and the view key change together; ENGINE_CACHE_VERSION "5" (:60) also in the key via engine_fingerprint.
- Tier-2 engine change: footer key = collection_tier2_key(raw, cid, keys.tier1_key) (orchestrator.py:361-365, 407) = tier2_key(t1, steps, tier2_engine) cache_keys.py:136-145; engine is an argument, so the footer changes, stored_table_identity reads the footer now (t2 element) and the form follows. A tier with no steps: key "" and file removed (orchestrator.py:215-217), identity uses t2=None as on dev.
- anchor path used by the form (home_theater.py:352 `anchors/<ds>.parquet`) is the same path `_resolve_t1_lf`/materialize use (:333).
- Not run as a break-once here: whether an engine switch alone moves the form; it follows from the above (test_engine_keys.py passes) but no browser test changes an engine.

## Adapted
Nothing. test_filter_form_survives_rerender.py writes no recipe; it imports staged_app/typed_app from test_shiny_step_order.py / test_shiny_filter_types.py already in the new shape on this branch (last touched by bda106c6, 514a54a4). No assertion changed.

## Runs (qa: interactivity_enabled true, t3_sandbox_enabled true, ghost_save.enabled false)
- Headless (32 files importing t3_audit_engine/filter_and_audit_handlers/home_theater without browser, plus test_filter_operators, test_cache_keys, test_cache_version_5, test_engine_keys, test_engine_record, test_engine_registry, test_migrate_recipe_engine_keys): 1248 passed.
- Browser, one file at a time: test_filter_form_survives_rerender 37 passed; test_filters_cleared_on_recipe_change 13 passed; test_shiny_apply_blocked 1; test_shiny_filter_value_list 2; test_shiny_step_order 6; test_shiny_smoke 37 passed, 3 skipped.
- Import check: OK (app.src.main.__file__ lies in the worktree).
- Pictures (hash seed 0, baseline picture_baseline_15394ef5 untouched, out final_check/pictures_after_filter_merge): identical 50, error-changed 1 = experimental/test_logic.yaml refusal text ("...actions, components" now "...actions, components, engines"), the expected non-picture row. Script prints "PICTURES NOT IDENTICAL" because of that row.

## Not proven
Other test files of app/tests and libs not run (brief limited); the three smoke skips are existing skips; no browser test of an engine change moving the filter form. Dev's other browser files with waits (export_download, export_inputs_survive_plot_tab, session_restore) were not run.
