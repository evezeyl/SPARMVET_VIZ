# Tasks Archive — 2026-05-03
Archived from active `tasks.md` after Wave 1 remediation sprint.

---

## User Verified

- [x] **Phase 21 T1/T2 visual diff**: Verified 2026-05-02 — T1↔T2 toggle works, earlier years disappear in T2. T2/T3 comparison mode also confirmed working.
- [x] **22-G-4**: Session ghost files verified 2026-05-02. Sessions `7f265b1d7b27` and `b98f603ac5f7` both have `assembly.json` written by the SESSION-1 fix. Old pre-fix sessions still present but will import via T3-ghost fallback. No cleanup needed.
- [x] **Lineage 1 (AMR Profile)**: Materialized. Verified Integer Year and Predicted Phenotype.

---

## Bugs (resolved)

- [x] **STATE-T2**: Plot render handlers (`_group_plot_handler`, `_cmp_baseline_handler`) had inline data resolution that always served T1 — ignored `tier_toggle`. Fixed 2026-05-02: both now use `_resolve_active_lf` (T1 or T2 per toggle) and `_resolve_t1_lf` (baseline always T1).
- [x] **STATE-1**: Flicker on T3 toggle and panel switch — resolved 2026-05-02 via per-plot `plot_cell_{p_id}` handlers (layout isolated from `dynamic_tabs`) + CSS hide/show for compare switch. `home_state` remains monolithic but observable flicker is gone; split-state refactor deferred to BUG-PERF-1 scope if needed.
- [x] **STATE-2**: Compare T2/T3 toggle wrong-plot-wins — resolved 2026-05-02; user-verified no longer reproduces after per-plot cell handler isolation.
- [x] **BUG-PERF-1**: `materialize_tier1` skip-if-exists guard confirmed present in `home_theater.py:199` — `if out_path.exists(): return pl.scan_parquet(out_path)`. Only rematerializes on cache miss.

---

## Filter / Audit (resolved)

- [x] **AUDIT-2**: Filter display mismatch — resolved. Promotion `eq`→`in` happens at Add-time (`filter_and_audit_handlers.py:373`); staged row immediately renders with `∈` via `_op_label(op)`; `_params_summary` in audit panel uses the same symbol table. Display is consistent end-to-end.
- [x] **AUDIT-3**: Propagation skip is NOT silent — confirmed. Modal preview shows `⚠️ N skip (col missing)` before confirm; post-confirm notification explicitly lists each skipped plot + column (`filter_and_audit_handlers.py:772`). ADR-049 D9 implemented.
- [x] **AUDIT-4**: Compare T2/T3 toggle loses state on plot switch — resolved with STATE-2 (per-plot cell handlers), user-verified.
- [x] **PROP-4**: Propagation rules documented in `docs/user_guide/audit_pipeline.qmd` — one-at-a-time workflow (8-step sequence), writing good reasons section, column-presence semantics already covered in propagation preview section.

---

## Export (resolved)

- [x] **EXPORT-TIERS**: Both global and single graph export were only exporting T1 data — T2 wrangling was a stub (`t2_equals_t1 = True`). Fixed 2026-05-02: both now export `_T1_data.tsv` always, `_T2_data.tsv` when tier2 recipe steps exist, `_T3_data.tsv` when T3 nodes committed.
- [x] **EXPORT-SGE-2**: `full_recipe.yaml` added to single graph export bundle — T1/T2 assembly + T3 nodes + plot spec. `!include` confirmed resolved in `raw_config` (custom SafeLoader constructor). `manifest_fragment.yaml` and `t3_recipe.json` kept for backwards compat.
- [x] **EXPORT-SGE-4**: Multi-file upload hint added — "Hold Ctrl/⌘ Cmd to select multiple files". Native `multiple=True` already in place; dynamic "Add another" loop not needed.
- [x] **EXPORT-SGE-7**: Dataset-to-plot mapping when multiple source files uploaded — resolved by IMPORT-1. The assignment table (filename → dataset dropdown per manifest) is the implementation; same Option B design. 2026-05-02.

---

## Session / Import (resolved)

- [x] **IMPORT-1**: Data Import — implemented 2026-05-02. Assignment table (filename → dataset dropdown), per-file `MetadataValidator` validation with `.tip` fuzzy suggestions surfaced inline, writes to `source.path` or `raw_data_dir/{ds_id}`, busts parquet cache + `bootloader` LF cache, `data_refresh_trigger` invalidates plot renders. MetadataValidator dtype map audited and fixed (numeric→Float64, date→Date, character→Utf8) before implementation.

---

## UX (resolved)

- [x] **UX-1**: Plot rendering slow — resolved with BUG-PERF-1 (parquet cache hit on fast path).
- [x] **UX-NOTIF-1**: Toast notifications disappear too fast — implemented 2026-05-02. `notification_log = reactive.Value([])` in `server.py`; `app/handlers/notification_utils.py` provides `make_notifier(notification_log)` factory; `_notify` wrapper replaces `ui.notification_show` in 6 user-facing handlers (filter_and_audit, audit_stack, session, export, data_import, sge); right sidebar shows `🔔 Alerts (N)` accordion (newest-first, last 20, type-colored). T3 ghost persistence deferred.

---

## Wave 1 Remediation (2026-05-03)

Documentation, test, and infrastructure debt from exhaustive audit:

- [x] §6C Taxonomy docs — added 6-axis section to `viz_factory_components.qmd` + `viz_gallery.qmd` (`57aaa43`)
- [x] §7A+§7B terminology drift — Dev Studio→Test Lab, System Tools→Global Project Export, Analysis Theater→Home, T3 definition across 6 docs files (`ac30754`)
- [x] §6A Violet Law — prose references in 5 lib READMEs (`ac65147`)
- [x] §6B `phenotype`→`predicted_phenotype` cascade — ResFinder fields, ST22 anchor, heatmap plot, figshare manifest + script (`7b14991`)
- [x] Broken collectors — renamed `test_sdk.py`→`debug_sdk.py`, `test_config_loader.py`→`debug_config_loader.py`; fixed stale import; fixed 2 stale `test_persona_validator.py` assertions (`8788915`)
- [x] TestFilterPipeline ×4 — added `_open_filters_panel()` helper; Filters accordion is collapsed by default (`c37669e`)
- [x] §3B-A argparse `generate_demo_data.py` (`95e592a`)
- [x] §3B-B argparse + `main()` wrap `figshare_plot_integration.py` (`7a9bf02`)
- [x] §3D `get_debug_out_dir()` helper in `libs/utils/src/utils/debug_output.py` (`87fc7e1`)
- [x] §2B failure-test gap audit + §8 corrections log appended to exhaustive audit (`82f09c0`)
- [x] §1A `INGEST-SANITIZE-1` registered in tasks.md (`e9827ed`)
- [x] §5 `@deps` blocks injected into 18 files (4 batches); dep graph regenerated 117 nodes / 222 edges (`f463f47`, `f473642`)
