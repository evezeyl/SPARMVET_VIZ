# Handoff — Active State (2026-04-30, Session 10)

**Branch:** dev
**Last commit:** `283207c` docs+test: filter operator contract — regression suite + user docs + ADR amendment
**Active agent:** @dasharch (Claude Sonnet 4.6)

---

## Current State

Phase 21 complete. Phase 22 implemented; **22-J live-UI test §1 PASSED 2026-04-30** (core per-plot scoping validated). Phase 23-A + 23-B complete. **Monday demo blockers DEMO-1..DEMO-4 all RESOLVED.** Filter pipeline contract is locked down by 21 regression tests, user docs are updated, ADR-049 amendment recorded. App is in solid shape for the Monday demo.

---

## What Was Done (Session 10)

### Demo blockers — all fixed and committed individually for safe rollback

| ID | Commit | What |
|---|---|---|
| **DEMO-1** | `55ab1c5` | viz_factory auto-rotation log KeyError on short-label branches (Virulence Variants plot) |
| **DEMO-2** | `b91dfc9` + `33afa1b` | Quast unpivot moved tier2→tier1 + register `boxplot_logic` factory_id (Assembly Quality dotplot) |
| **DEMO-3** | `4c962e6` | `_apply_filter_rows` reads actual column dtype from LF schema, coerces string operands |
| **DEMO-4** | `8b4f3a4` | viz_factory plot filter loop — same dtype-aware coercion (was the actual MLST year>2022 fix) |
| **BUG-CACHE-1** | `09366fc` | DataAssembler cache hash now includes upstream provenance (manifest_sha256 + data_batch_hash). Edits to TSVs / manifests now invalidate the parquet automatically. |
| **DATA-1** | `4133159` | Quast/FastP/Bracken/Quality_metrics test TSVs realigned to use canonical metadata sample_ids (was zero overlap) |

### Filter pipeline overhaul (UX-FILTER-1, AUDIT-1, PROP-1)

| ID | Commits | What |
|---|---|---|
| **UX-FILTER-1** | `f08b88f` `61e86a8` `f4b1a91` `5c5083f` | Dtype-aware filter widgets. Numeric scalar ops → `ui.input_numeric`. New `between` op → two numeric inputs (was a slider initially; replaced because of render-glitch + locale separator + imprecise input). Inclusivity toggle for `between`: `≤ ≤ inclusive` (default) or `<  < exclusive` → `closed='both'` / `closed='none'`. fb_op dropdown now preserves selection across re-renders (was resetting). |
| **AUDIT-1** | `3c6195f` | ADR-049 amendment: PK-column filtering ALLOWED (no more silent conversion to exclusion_row). Operator is the truth, PK warning is the safety rail. ADR-049a added in `architecture_decisions.md`. |
| **PROP-1** | `b4dcd10` | Propagation modal now shows per-plot column-presence preview BEFORE the user confirms. Three states: ✅ apply / ⚠️ skip (col missing) / ❓ unknown. Encourages "apply one at a time" workflow. |

### Cosmetic / structural

| Description | Commits |
|---|---|
| Cat 🐱 group + miaou violin plot | `f2b7fba` `97506e9` `b74e985` |
| Generalised id sanitiser (any unicode/emoji in group labels) | `7adc48a` `d9d3406` |
| Categorical→String cast before `.str` ops in AMR_Profile_Joint | `beb4b72` |
| Filter operator regression test (21 cases) + user docs | `283207c` |

---

## Documentation Updated

- `docs/user_guide/audit_pipeline.qmd` — Propagation preview section, PK-filter-allowed section, full filter operators reference appendix.
- `.agents/rules/ui_implementation_contract.md` §12g.3 — PK filter table updated.
- `.antigravity/knowledge/architecture_decisions.md` — ADR-049a (2026-04-30 PK amendment).
- `.agents/rules/rules_manifest_structure.md` §8 — Emoji/icon support in group labels (from earlier session).

---

## Test Coverage

| Suite | Count | Path |
|---|---|---|
| Filter operators (NEW this session) | 21 | `app/tests/test_filter_operators.py` |
| Connector library | 31 | `libs/connector/tests/test_connectors.py` |

Run all: `PYTHONPATH=. .venv/bin/python -m pytest app/tests/test_filter_operators.py libs/connector/tests/`

---

## Next Steps (Priority Order)

| # | Item | Notes |
|---|---|---|
| 1 | **22-J Live-UI test continued** | Sections 3–9 now testable (PK filter unblocked, types fixed). Walk through `tasks_test_22J.md` with current build. |
| 2 | **AUDIT-2** | Filter→audit operator translation correctness (UI says "exact France" → audit says "any of [France]" — verify single-value selectize→eq path is faithful) |
| 3 | **AUDIT-4** | Compare T2/T3 toggle does not hold state on plot switch — reactive scoping bug |
| 4 | **UX-1..5** | Polish (data preview column-selector width, header visibility, button rename "Send to Audit", trash icon homogenisation) |
| 5 | **BUG-PERF-1** | Wire `SessionManager.restore_t1t2()` fast-path into `home_theater.py:545` (orchestrator currently fires every project switch but DataAssembler short-circuits) |
| 6 | **PROP-4** | Documentation: write user-guide section on propagation rules + screenshots (PROP-1 is in, ready to be documented) |
| 7 | **PROP-2** | Filter inventory panel showing effective filters per plot (enhancement) |
| 8 | **PROP-3** | TubeMap propagation visualisation (enhancement, exploratory — own ADR/design pass) |
| 9 | **NAV-1..6 / TOOLS-1..5** | Left sidebar restructure (Data Navigator, System Tools split) |
| 10 | **Phase 24-A** | `t3_recipe_engine.py` extraction (gate now MET, but lower priority than UX work) |

---

## Key Conventions (Do Not Break)

- **Filter operator contract is now locked down** by `app/tests/test_filter_operators.py`. Any changes to `_apply_filter_rows` (home_theater.py) OR `viz_factory.py` filter loop must keep these tests green.
- **The two filter paths must agree.** Production has TWO filter implementations (data preview + plot render). They must produce identical results for the same filter row, otherwise UI inconsistency. The regression test mirrors both.
- **`closed=` field on `between` filter rows**: 'both' (default) or 'none'. Anything else triggers a defensive fallback to 'both' in `_filter_add_row`.
- **PK filter is ALLOWED** (AUDIT-1 / ADR-049a). Don't reintroduce the `if is_pk: node_type = "exclusion_row"` silent-conversion branch in `home_theater.py`.
- **Cache invalidation is upstream-aware** (BUG-CACHE-1). The orchestrator injects `upstream_provenance` (manifest_sha256[:16] + data_batch_hash[:16]) into the sink_parquet step. Don't strip it via the `__`-prefix purge.
- **Group labels can use any unicode**, plot ids must be snake_case (registration contract). `_safe_id()` in home_theater.py handles internal IDs; visible labels come from `label:`/`description:` fields.
- **Persona IDs use hyphens** (`pipeline-exploration-advanced`); underscores silently fail all gates.
- **Numeric filter widgets emit native types**; the defensive coercion in both filter paths logs `[filter] ⚠️ string operand…` if a string sneaks in. Treat that warning as a bug signal.

---

## App Status (Monday demo)

- App imports clean (`from app.src.main import app`)
- 52/52 tests pass (21 filter + 31 connector)
- All 4 demo blockers resolved + cache correctness fixed
- Filter UI: dtype-aware widgets, between with inclusivity toggle, propagation preview
- Documentation: audit pipeline guide updated end-to-end

Recommended demo path: `1_test_data_ST22_dummy` → walk through QC group → show miaou cat violin → demonstrate audit pipeline (filter year between 2022–2024, exclude S2 from one plot, etc.) → export bundle.


---

# Handoff — Demo state (2026-04-30, end of Session 11)

**Last commit:** `870f0e6` (refactor PERSONA-1a) + post-handoff: PERSONA-2 + DATA-2 + log + this handoff.

## Demo readiness

✅ App imports clean. 90/90 pytest pass. All 4 Monday-demo blockers fixed (DEMO-1..4) plus cache correctness (BUG-CACHE-1) plus test-data alignment (DATA-1).

**Demo path recommendation**: launch with `SPARMVET_PERSONA=developer`, load `1_test_data_ST22_dummy`. Walk through:
1. QC group → demonstrate plots rendering (Virulence Variants + Assembly Quality dotplot now work)
2. Cat 🐱 group → miaou violin shows assembly metrics by source
3. Filter UI → dtype-aware widgets, between with inclusivity toggle, audit propagation preview
4. Toggle T1 ↔ T2 on a MLST-related plot → visible difference (era column + year filter)
5. Export Bundle → comprehensive ZIP

**Known issues to acknowledge during demo (non-blocking)**:
- T3 toggle / panel-switch causes plot flicker (STATE-1/2)
- Compare T2/T3 button doesn't hold (AUDIT-4 = STATE-2)
- Notifications disappear too fast — FIXED (UX-NOTIF-1: alert log accordion in right sidebar, 2026-05-02)
- Single-graph export not wired (EXPORT-1, deferred from Phase 22)

## Personas available

| Persona | Use |
|---|---|
| `developer` | Full feature surface — for the demo |
| `project-independent` | Advanced + data ingestion |
| `pipeline-exploration-advanced` | T3 audit, no data ingestion |
| `pipeline-exploration-simple` | Filtering only, no T3 audit authoring |
| `pipeline-static` | Read-only |
| `qa` (NEW, PERSONA-2) | All flags ON + ghost_save OFF — for automated UI tests |

## Test commands

```bash
# Quick (sub-second, run before every commit)
PYTHONPATH=. ./.venv/bin/python -m pytest libs/ app/tests/ -q

# Long (full PNG render audit)
PYTHONPATH=. ./.venv/bin/python libs/viz_factory/tests/viz_factory_integrity_suite.py --output_dir tmp/viz_factory/

# Long (transformer assembler audit)
PYTHONPATH=. ./.venv/bin/python libs/transformer/tests/transformer_integrity_suite.py --output_dir tmp/transformer/
```

## Open priorities for next session (post-demo)

1. **STATE-1/STATE-2 + AUDIT-4**: trace the reactive scoping bug — active plot subtab is being reset by toggle effects somewhere
2. **UX-NOTIF-1**: ~~persistent alert log~~ DONE — `🔔 Alerts` accordion in right sidebar (2026-05-02); UX-NOTIF-2 (ghost persist) is next
3. **PERSONA-1b**: resolve doc-drift on `simple` persona's Comparison/Session Mgmt visibility
4. **Phase 24-A**: extract `t3_recipe_engine.py` (the safe pure-function piece of the home_theater split)
5. **EXPORT-1**: wire the deferred single-plot export

## Files most likely to bite next agent

- `app/handlers/home_theater.py` (~3000 lines now, refactor pending — Phase 24)
- Any change to filter logic must keep `app/tests/test_filter_operators.py` (21 cases) green
- Cache invalidation: do NOT remove `upstream_provenance` from sink_parquet step in `app/modules/orchestrator.py:materialize_tier1` — that's BUG-CACHE-1's keystone

## Conventions enforced

- Persona IDs: HYPHENS only (`pipeline-exploration-advanced`, never underscores)
- Filter widgets emit native types; coercion in apply paths is defensive (logs `[filter] ⚠️` if string sneaks in on numeric column)
- Group labels accept any unicode (`_safe_id()` sanitises internal IDs); plot ids must be snake_case
- Cache hash includes upstream_provenance (BUG-CACHE-1) — manifest/TSV edits invalidate parquet

---

# Handoff — Test infrastructure (2026-04-30, Session 12)

**Branch:** dev
**Context:** Playwright headless testing infrastructure added to `app/tests/`.

## What was added

### New files
- `app/tests/conftest.py` — pytest fixture using `shiny.pytest.create_app_fixture(app_path, scope="module")`. This is the correct Shiny pytest fixture; replaces the previously broken `shiny_app` fixture that did not exist in the installed shiny version.
- `app/tests/test_shiny_smoke.py` — 12 Playwright smoke tests across 4 concern areas (startup, persona masking, filter pipeline, data preview). Runtime ~35 s.

### Updated files
- `app/tests/test_reactive_shell.py` — fixed fixture import (was referencing non-existent `shiny_app`, now imports from conftest).
- `pyproject.toml` (root) — added `[project.optional-dependencies] test = ["pytest>=9.0.0", "playwright>=1.50.0", "pytest-playwright>=0.7.0"]`.

### Installed in .venv
- `playwright==1.59.0`, `pytest-playwright==0.7.2`
- Chromium headless shell at `~/.cache/ms-playwright/`

## Smoke test baseline

| Suite | Pass | Skip | Notes |
|---|---|---|---|
| Unit tests (filter + connector + deco2) | 90 | 0 | ~2 s |
| Playwright smoke (`test_shiny_smoke.py`) | 10 | 2 | ~35 s; 2 skips = persona-gated Gallery tests (expected) |

The 2 skipped tests are correct behaviour: Gallery is only enabled for `developer` and `qa` personas; when running under any other persona they skip. Under `SPARMVET_PERSONA=qa` they pass.

## Test commands

```bash
# Core unit tests — 90/90 baseline
PYTHONPATH=. ./.venv/bin/python -m pytest \
  app/tests/test_filter_operators.py \
  libs/connector/tests/ \
  libs/viz_factory/tests/test_deco2_components.py \
  -q

# Playwright smoke — 10 pass, 2 persona-skip (~35s)
PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v

# App import check
python -c "from app.src.main import app; print('OK')"
```

## Pre-existing failures (do NOT fix — out of scope)

These were broken before this session and are unrelated to Playwright:

- `libs/generator_utils/tests/test_sdk.py` — ImportError
- `libs/utils/tests/test_config_loader.py` — ImportError
- `app/tests/test_reactive_shell.py` — 2 failures: `#persona_selector` doesn't exist as a rendered UI element
- `app/tests/test_ui_scenarios.py` — 1 failure: same cause

## Key implementation notes for next agent

- `_wait_shiny(page)` waits for `document.documentElement.classList.contains('shiny-busy')` to clear. Always call it before interacting with reactive outputs.
- Persona is set via `SPARMVET_PERSONA` env var at launch time only. There is no `#persona_selector` UI element at runtime.
- After `fb_col` changes, `filter_form_ui` re-renders — always call `_wait_shiny()` before interacting with `fb_op` or `fb_value`.
- `_load_project` waits for `.nav-link:has-text('Quality Control')` as the signal that dynamic_tabs has rendered.
- Filter tests navigate: AMR group tab (`.nav-link:has-text('AMR')`) → Mlst Bar plot — this is where the "year" column exists.
- Emoji tab labels require `.nav-link:has-text('partial text')` selectors; role-based selectors are unreliable with emoji.
- `shiny add test` is a Shiny CLI scaffold tool; it was NOT used here because tests were written manually. Mentioning it for context only — do not re-run it as it would overwrite conftest.py.

## Documentation updated this session

- `.agents/rules/rules_verification_testing.md` — Section 8 added: Shiny App Headless Testing (Playwright)
- `EVE_WORK/notes/cheatsheat.md` — Test command reference section updated with correct quick command, Playwright command, and demo-readiness one-liner
- `.claude/projects/.../memory/project_infra.md` — Playwright infrastructure section added

---

# Handoff — Phase 24 home_theater decomposition (2026-05-01, Session 13)

**Branch:** dev
**Last commit:** `2393e50` refactor(24-D cleanup): @deps header + record change manifest
**Active agent:** Opus 4.7 (1M context)

## What landed (Steps 24-A through 24-D — full handler decomposition)

ADR-051 fully implemented. `home_theater.py` shrunk from 2,853 → 1,278 lines (-55.2%). Each step was two commits: a mechanical move + a `@deps`/manifest cleanup. All four extractions were verified independently with the same gate (90/90 unit + import + 12/12 smoke).

| Step | New file | LoC | Risk | Move commit | Cleanup commit |
|---|---|---|---|---|---|
| 24-A | `app/modules/t3_recipe_engine.py` | 133 | Low | `89bb5ef` | `890b609` |
| 24-B | `app/handlers/session_handlers.py` | 262 | Low | `f540cbf` | `d50197e` |
| 24-C | `app/handlers/export_handlers.py` | 597 | Med | `4c38f26` | `18dbd46` |
| 24-D | `app/handlers/filter_and_audit_handlers.py` | 811 | High | `f0f7d92` | `2393e50` |

Plus: a one-off `166ff82 fix(tests): module-scoped page fixture + idempotent _load_project` early in the run, after diagnosing the smoke suite as flake-prone due to Shiny session accumulation. Suite now ~20s deterministic.

## Deviations from the original plan (recorded in `tasks_phase24.md`)

- **24-B kwarg surface narrowed.** Plan listed 7 reactive kwargs (`tier1_anchor`, `tier_reference`, `tier3_leaf`, `active_cfg`, `active_collection_id`, etc.); the actual session block reads NONE of those. Final signature is `session_manager`, `current_persona`, `home_state` only.
- **24-C inline duplicate of `_op_label`.** During 24-C the function was duplicated inline in `export_handlers.py` to keep the move mechanical. Lifted in 24-D to `t3_recipe_engine.py` so both `export_handlers` and `filter_and_audit_handlers` import from one place.
- **24-D filter UI + T3 audit kept in ONE file.** ADR-051 originally proposed two files (`t3_audit_handlers.py` + something for filter UI). Kept together as `filter_and_audit_handlers.py` because `_filter_apply`, `_col_drop_to_audit`, and `_handle_propagation_confirm` all share `_propagation_scratch` and call `_open_propagation_modal`. Splitting would force exposing scratch state across modules.

## What remains in `home_theater.py` (1,278 lines)

- Module docstring + updated `@deps` header
- `_safe_id()`, `_collect_all_group_plot_ids()`
- `define_server()` signature + init block + reactive helpers (`_resolve_active_spec`, `_resolve_active_lf`, `_t3_filter_rows`, `_t3_drop_columns`, `_active_plot_t3_nodes`, `_all_plot_subtab_ids`, `_plot_label`, `_spec_discrete_axes`)
- `_make_group_plot_handler()`, `_make_cmp_baseline_handler()`
- `dynamic_tabs()` (the largest remaining piece)
- Tier toggle + session provenance trackers
- `home_data_preview()`, `home_col_selector_ui()`, `col_drop_audit_btn_ui()`
- Sidebar UI: `sidebar_nav_ui`, `sidebar_tools_ui`, `right_sidebar_content_ui`
- Calls to: `define_session_server(...)`, `define_export_server(...)`, `define_filter_audit_server(...)`
- Plot/table reference + leaf renderers + `handle_plot_brush()`, `comparison_mode_toggle_ui()`

## Verification gate (pass everywhere)

```bash
PYTHONPATH=. ./.venv/bin/python -m pytest \
  app/tests/test_filter_operators.py libs/connector/tests/ \
  libs/viz_factory/tests/test_deco2_components.py -q
# 90 passed in ~1.2s

PYTHONPATH=. ./.venv/bin/python -c "from app.src.main import app; print('OK')"
# OK

PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -q
# 10 passed, 2 skipped in ~20s  (4 filter pipeline tests included)
```

## Files most likely to bite the next agent

- `app/handlers/filter_and_audit_handlers.py` — high-risk move; the propagation modal closure interacts with `_propagation_scratch`, `home_state`, and `_pending_filters`. If you touch any of these, run the 21-case filter regression AND the smoke suite together.
- `app/handlers/home_theater.py` — `define_server` now passes 14 kwargs into `define_filter_audit_server`. Adding/removing closures defined inside `define_server` requires updating the call site too.
- `tasks_phase24.md` — full per-step change manifests for traceability if a regression appears later.

## Open priorities (carried forward, untouched by Phase 24)

1. **STATE-1/STATE-2 + AUDIT-4** — reactive scoping bug on plot subtab reset.
2. **UX-NOTIF-1** — DONE (2026-05-02). **UX-NOTIF-2** — ghost persistence deferred.
3. **PERSONA-1b** — doc drift on `simple` persona's Comparison/Session Mgmt visibility.
4. **EXPORT-1** — single-plot export wiring.
5. **22-J live-UI test §3-§9** — continue Walk-through using `tasks_test_22J.md`.

## Conventions reaffirmed by Phase 24

- ADR-045 Two-Category Law: `app/modules/` = pure (no Shiny imports), `app/handlers/` = Shiny-only.
- Shared `reactive.Value` instances stay in `home_theater.define_server()` and pass to sub-handlers as kwargs (NEVER module globals).
- Two-commit-per-step refactor protocol: move + cleanup. Verification gate after each.
- Persona IDs: HYPHENS only.

---

## Session 14 — Phase 25 design & documentation (2026-05-01)

**Branch:** dev
**Agent:** Claude Sonnet 4.6
**Phase 24 status:** CLOSED (from previous session). All gates green.

### What was done

Full co-design session for Phase 25 (Left Sidebar Restructure). No code changed — design, decisions, and documentation only.

**Design artefacts produced (all in `EVE_WORK/daily/2026-05-01/`):**
- `persona_functionality_side_bars.csv` — initial code-analysis layer (v1)
- `persona_functionality_side_bars_v3_clean.csv` — final agreed design (v3, pipe-separated)
- `persona_template_new_fields.md` — companion spec for new YAML sections
- `EVE_WORK/TESTING_protocols/` — 7 manual testing protocol CSVs created (protocol_01..07)

**Documentation updated:**
- `architecture_decisions.md` — ADR-052 added (Phase 25 full design)
- `persona_traceability_matrix.md` — rewritten with passive_exploration + t3_audit columns, Gallery for project-independent, right sidebar layout fix documented, known bugs table
- `.agents/rules/rules_ui_dashboard.md` §3 — persona reactivity matrix updated
- `.antigravity/tasks/tasks_phase25.md` — NEW: 10-step change manifests with model recommendations
- `.antigravity/tasks/tasks.md` — Phase 25 section rewritten with concrete substeps
- `.antigravity/plans/implementation_plan_master.md` — Phase 25 DESIGNED entry added

### Key decisions made (ADR-052)

| Decision | Resolution |
|---|---|
| Right sidebar layout | Option A: exclude container at `ui.py` build time for pipeline personas — currently wastes 340px even when "hidden" |
| New persona template fields | `manifest_selector.visible/fixed_manifest` + `testing_mode` |
| Pipeline personas testing mode | Always `testing_mode=false` — testing uses developer/advanced personas |
| Gallery for project-independent | `gallery_enabled: true` added to template |
| Dev Studio rename | → "Test Lab" |
| Report rendering | Quarto replaces Pandoc (HTML + PDF + DOCX server-side) |
| New capability columns | `passive_exploration` + `t3_audit` formalise existing undocumented behaviour |
| Single Graph Export | Un-deferred from Phase 22 — BUILD_NEW in 25-H |

### Phase 25 substep ordering

25-A (config/rename) → 25-B (template fields + validator) → 25-C (gating fixes + bugs) → 25-D (layout fix) → 25-E (accordion restructure) → 25-F (Data Import panel) → 25-G (export/Quarto) → 25-H (Single Graph Export) → 25-I (visual fixes) → 25-J (smoke tests)

**Model recommendation:** Sonnet for 25-A..E + 25-I..J. Opus for 25-F..H (new reactive builds).

### Next step

Run Phase 25 pre-flight, then start 25-A (two commits: config change + cheatsheet update).

### Files most likely to bite the next agent

- `app/src/ui.py` L400-417 — right sidebar layout (25-D target)
- `app/handlers/filter_and_audit_handlers.py` — filter form gating (25-C)
- `app/handlers/session_handlers.py` — PERSONA-1 hardcoded set (25-C)
- `config/ui/templates/*.yaml` — new fields needed (25-B)

---

## Session 15 — Gallery taxonomy, 13 new recipes, accordion harmonization (2026-05-03)

**Branch:** dev
**Agent:** Claude Sonnet 4.6
**Phase 25 status:** CLOSED (completed in earlier session). Current work is UI polish, gallery expansion.

### What was done

#### Gallery

- **13 new recipes**: `beeswarm_sina`, `ecdf`, `violin_boxplot`, `qq_plot`, `freqpoly`, `scatter_smooth`, `density_2d_bin`, `connected_scatter`, `bar_grouped`, `error_bar`, `dumbbell`, `stacked_area`, `step_chart`. All had VizFactory format bugs — normalized (name: key, global mapping, per-recipe fixes).
- **6-axis taxonomy** (ADR-063): added `geom`/`show`/`sample_size` to all 34 manifests, all 34 `recipe_meta.md` tag strips, `gallery_manager.py`, `gallery_viewer.py` (3 new filter panels), `gallery_handlers.py` (`_pivot_set()` helper, 6-way intersection).
- **`generate_previews.py`** — new headless PNG generator; all 34 previews regenerated.
- **`TAXONOMY_CHEATSHEET.md`** — new canonical reference for icon/axis/value mappings.

#### CSS & UI harmonization (ADR-064)

- **`_collapsible_panel()` helper** in `home_theater.py` — bslib accordion wrapper; canonical pattern for all collapsible content panels.
- **Home**: Main Plot Card (`home_plots_body_accordion`) + Data Preview (`acc_home_data`) → bslib accordion. Data Preview title: icon `📋` + removed inline style override.
- **Blueprint**: Work Area (`blueprint_workarea_accordion`) → bslib accordion. Glimpse/Plot Preview cards kept as Bootstrap collapse but styled to match.
- **CSS §18/18b**: bold 0.85rem on all accordion buttons; `border-radius: 8px + overflow: hidden` on accordion-items to fix top-corner rounding; Bootstrap card-header top rounding explicit.
- **Gallery**: `#gallery_preview_accordion .accordion-item { border: none }` fixes grey bar. Guidance accordion: `box-shadow: none` prevents bleed between stacked panels.
- **TubeMap**: normalized from blue to standard `#f8f9fa / #1a1a1a`.

### Open CSS issues (ongoing in same session)

CSS rounding still being tuned — user reported:
- Blueprint Bootstrap cards (Glimpse/Plot Preview): need confirmed top rounding in browser
- Home Plots accordion: `border-radius + overflow: hidden` applied; user to verify
- Data Preview: icon + font fix applied

### Files changed

```
app/handlers/home_theater.py        — _collapsible_panel(), acc_home_data title
app/modules/wrangle_studio.py       — blueprint_workarea_accordion, card mb-1
app/modules/gallery_viewer.py       — 3 new filter panels, 6 taxonomy sub-panels
app/handlers/gallery_handlers.py    — _pivot_set(), 3 new sync effects
libs/viz_gallery/src/.../gallery_manager.py — 6-axis pivot
libs/viz_gallery/assets/generate_previews.py  — NEW
assets/gallery_data/TAXONOMY_CHEATSHEET.md    — NEW
assets/gallery_data/*/recipe_manifest.yaml    — all 34 (6 taxonomy fields)
assets/gallery_data/*/recipe_meta.md          — all 34 (6-field tag strip)
config/ui/theme.css                 — §14, §18, §18b (accordion harmonization)
```

### Conventions added / changed

- **ADR-064**: `_collapsible_panel()` is the mandatory pattern for new collapsible panels in theater areas. Never use `data-bs-toggle="collapse"` for primary panels.
- **ADR-063**: Gallery manifests require all 6 taxonomy fields. `TAXONOMY_CHEATSHEET.md` is authoritative.
- **Never use inline `style=` on accordion panel titles** — it overrides CSS policy for font/color.
- **`overflow: hidden` on `.accordion-item`** is required whenever `border-radius` is applied to get visual corner clipping.

### Next steps

1. Verify CSS rounding in browser (Bootstrap cards + bslib accordions)
2. Continue CSS polish if user reports additional issues
3. Consider commit when CSS is stable
4. Run test suite before committing (`PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/ libs/ -q`)

---

## Session 16 — Export redesign + assembly→join rename + repository hygiene (2026-05-04/05)

**Branch:** dev
**Agent:** Claude Sonnet 4.6
**Last commits:** `60fe369` (export redesign + join rename)

### What landed

#### Export redesign (EXPORT-REDESIGN-1, EXPORT-REDESIGN-2)

- **Removed** "Export Audit Report" button and its handlers (`export_audit_report_ui`, `export_audit_report_download`, `_audit_report_filename`).
- **Removed** "Single Graph Export" accordion panel from left sidebar.
- **Added** 3-way scope toggle `export_scope` (`global` / `group` / `plot`) to the Export panel. Gated on `export_bundle_enabled + export_graph_enabled`. "Active group" and "Active plot" options styled with opacity 0.45 when no subtab is active.
- **Added** `t3_steps.yaml` to bundle (T3 committed active nodes, all plots in scope).
- **Added** T3 Audit Trail section to `report.qmd` (per-plot table; active nodes only; only when `t3_sandbox_enabled` and nodes exist).
- Accordion label: "Global Project Export" → "Export".
- `active_home_subtab` (reactive.Value[str]) passed as new kwarg to `define_export_server`.

Key files: `app/handlers/export_handlers.py`, `app/handlers/home_theater.py`.

#### assembly_manifests → join_manifests rename (ADR-066, ASSEMBLY-RENAME)

- All 10 config manifests: `assembly_manifests:` → `join_manifests:` (via sed).
- ~21 Python files: `"assembly_manifests"` → `"join_manifests"` (via sed).
- TubeMap labels: `\nAssembly` → `\nJoin`, `\nAssembly Wrangling` → `\nJoin Wrangling`.
- `wrangle_studio.py`: `◆ Assembly` → `◆ Join`, `Assembly Output (Input)` → `Join Output (Input)`.
- `blueprint_handlers.py`: role string, `asm_block` → `join_block`.
- `manifest_navigator.py`: `is_assembly` → `is_join_step`, `assembly_rels` → `join_rels`.
- 6 test fixture YAMLs under `libs/transformer/tests/data/`.
- **EXCEPTION (NOT renamed):** `session_manager.py` + `debug_session_flow.py` `{"assembly": ..., "contracted": ...}` — Parquet path labels, unrelated to manifest role.
- **Variable name rule:** Never use bare `join` as a Python variable (shadows `str.join()`). Use `join_defs`, `join_block`, `join_step`.

#### Documentation updated (2026-05-04/05)

- `changelog.md` — NEW in `.antigravity/knowledge/`. Release entries for both changes.
- `architecture_decisions.md` — ADR-047 §7 updated (scope toggle + T3 audit); ADR-051 updated (export_handlers new kwarg, deleted outputs); ADR-066 added (assembly rename).
- `project_conventions.md` — role string and join ingredient resolution updated.
- `AGENT_GUIDE.md` — removed archived knowledge files (`blockers.md`, `milestones.md`, `refactor_protocol_phase24.md`); added `changelog.md`; fixed handoff path.
- `ui_implementation_contract.md` — §7.2/§7.3/§11/§12f updated for export redesign; `assembly_manifests` → `join_manifests` in §12g.2.
- `rules_manifest_structure.md` — §2 `assembly/` → `join/`; §8 comment updated; §9 data types added (merged from `data_types.md`).

#### Repository hygiene (2026-05-04/05)

- New `.antigravity/` structure: `logs/sessions/`, `logs/audits/`, `logs/handoffs/archive/`, `knowledge/archive/`, `conversations/archive/`, `prompts/`.
- Archived: `blockers.md`, `milestones.md`, `refactor_protocol_phase24.md`, `galaxy_integration_prep.md`, `data_types.md`, `test_ui_persona.md`, old conversation files.
- Deleted: `PATHS_INITIATION.md`, `Hashses.md`, `offline_doc.md`, `presentation_prep_chat.md`.

### Current state

- **90/90 unit tests** should still pass (no logic changed in this session, only rename/restructure).
- **Run `PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py -q`** before coding to confirm.
- Export redesign code is in `app/handlers/export_handlers.py` — verify by launching with `developer` persona and testing the scope toggle in the Export accordion.

### Deferred next coding tasks

| Task | Notes |
|---|---|
| **EXPORT-HASH-2** | Read `decision_hash` from Parquet metadata at export time |
| **SESSION-PERSONA-1** | Gate ghost_save on `t3_sandbox_enabled` |
| **ST22 Lineage 2** | Plasmid Dynamics visualization |
| 6 REVIEW tasks | Design discussions needed — see `tasks.md` 🔵 REVIEW section |

### Conventions reaffirmed

- `join_manifests:` (not `assembly_manifests:`) everywhere — YAML keys, Python dict keys, role strings, UI labels, TubeMap labels.
- Never `join` as a bare Python variable — use `join_defs`, `join_block`, etc.
- Persona IDs: HYPHENS only.
- `export_graph_enabled` now gates the entire Export panel (scope toggle + bundle), not a separate accordion.
