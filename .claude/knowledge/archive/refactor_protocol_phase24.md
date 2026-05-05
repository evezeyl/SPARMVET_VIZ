# Refactor Protocol — Reusable (originally Phase 24 / `home_theater.py`)

**Status:** REUSABLE (2026-05-01)
**Origin:** ADR-051 / Phase 24 (`home_theater.py` 2,853 → 1,278 lines, IMPLEMENTED 2026-05-01).
**Next consumer:** Phase 25 (Left Sidebar Restructure — see `tasks.md` §Phase 25).

> This document started as the Phase 24 execution discipline. Phase 24 closed cleanly (12/12 smoke + 90/90 unit + 21/21 filter regression after every commit), so the protocol below is now adopted as the **default refactor process for any Shiny-handler decomposition** in this codebase. Sections labelled "Phase 24 specifics" are kept as reference; **the discipline is generic**.

---

## Purpose

This document defines the step-by-step execution discipline for any large refactor of an `app/handlers/*.py` file (decomposition, restructure, or bulk extraction). It is written for an agent that may not have full conversation history. Follow it exactly; any deviation requires explicit user confirmation before proceeding.

---

## Pre-flight Checklist (do this ONCE before any code edit)

1. **Tag current state** (so we can always hard-reset to here):
   ```bash
   git tag pre-phase24-$(date +%Y%m%d)
   ```

2. **Capture baseline test results** (save to `.antigravity/baselines/phase24_pre.txt`):
   ```bash
   PYTHONPATH=. ./.venv/bin/python -m pytest libs/ app/tests/ -q 2>&1 | tee .antigravity/baselines/phase24_pre.txt
   python -c "from app.src.main import app; print('import OK')" >> .antigravity/baselines/phase24_pre.txt
   ```

3. **Verify gate**: 90/90 tests pass + import clean. If not, STOP and fix before proceeding.

---

## Extraction Steps (in order — do not reorder)

Leaf-to-root order: pure functions first, reactives last.

| Step | New File | Source Lines | Risk |
|---|---|---|---|
| **24-A** | `app/modules/t3_recipe_engine.py` | L284–L381 (pure helpers) | Low — pure functions, no Shiny |
| **24-B** | `app/handlers/filter_handlers.py` | L2005–L2762 (filter UI + reactives) | Medium — reactive.Value refs passed via kwargs |
| **24-C** | `app/handlers/t3_audit_handlers.py` | L2392–L2762 (T3 audit/propagation) | Medium — interleaved with filter, read carefully |
| **24-D** | `app/handlers/session_handlers.py` | L1772–L1994 (session persistence) | Low — self-contained, no filter deps |
| **24-E** | `app/handlers/export_handlers.py` | L1232–L1770 (export + system tools) | Medium — reads active_cfg, session_manager |

> **Note on 24-B vs 24-C**: filter UI (sidebar_filters, filter_rows_ui, filter_form_ui, filter_controls_ui) and T3 audit promotion (_filter_add_row, _col_drop_to_audit, propagation) are heavily interleaved. Read the full L2005–L2762 block before deciding whether to split into one or two files. If co-locating makes the kwarg interface simpler, keep them together as `filter_and_audit_handlers.py` and note the deviation here.

---

## Per-Step Discipline (mandatory for each step)

### Before editing — write a change manifest

Post to chat (and copy to `.antigravity/tasks/tasks_phase24.md` §step) before any edit:

```
CHANGE MANIFEST — Step 24-X
Target new file: <path>
Source lines in home_theater.py: L<start>–L<end>
Names being MOVED: [list all def/class names]
Names being KEPT in home_theater.py: [only the thin wrapper/call]
Dependencies being added to new file:
  imports: [list]
  reactive sources consumed: [list reactive.Value / reactive.Calc names]
  reactive sources created: [none / list]
Kwargs added to new file's define_* signature: [list]
Risk level: low / medium / high
```

### Commit discipline — mechanical move only

Each extraction is exactly **two commits**:

- **Commit N** (`move`): copy lines to new file + import it in home_theater.py. `git diff --stat` must show:
  - additions in new file ≈ deletions in home_theater.py (within ±10 lines for docstrings/imports)
  - No logic changes. No renames. No signature changes.
- **Commit N+1** (`cleanup`): remove the now-dead code from home_theater.py, update `@deps` header, update `__init__.py` if needed.

If `git diff --stat` shows additions without matching deletions, the commit is wrong — `git reset --hard HEAD~1` and redo.

### Verification gate (after EACH commit)

All must pass before the next commit:

```bash
# 1. Core unit tests — 90/90 baseline (fast, ~2s)
PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py -q

# 2. Filter contract must never slip (21 cases — already in step 1)
PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_operators.py -v

# 3. App import must stay clean
python -c "from app.src.main import app; print('OK')"

# 4. Headless Playwright smoke tests — 10 pass, 2 persona-skipped (~35s)
PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v
```

Smoke tests use headless Chromium (playwright + shiny.pytest.create_app_fixture).
They start a real app subprocess and exercise: startup, project load, group tab navigation,
filter add/apply/reset, data preview.

**Note:** `libs/generator_utils/` and `libs/utils/` have pre-existing import errors — always
exclude them. `app/tests/test_reactive_shell.py` and `test_ui_scenarios.py` have 3 pre-existing
failures unrelated to Phase 24 (persona_selector not rendered in UI). Don't regress them further.

If any gate fails:
1. `git reset --hard HEAD~1`
2. Diagnose. Do not patch on top.
3. Retry from the change manifest step.
4. If the same gate fails twice: STOP and post a failure report. Do not proceed.

---

## Hard Rules — No Exceptions Without Asking

1. **Never mix refactor + bug fix or feature in the same commit.**
2. **Never delete code in the same commit it's moved.** Move first (commit N), delete second (commit N+1).
3. **Never edit `_apply_filter_rows` semantics** without running the 21-case filter regression (`test_filter_operators.py`) before AND after.
4. **Never change `bootloader.is_enabled()` call sites.** Persona gating uses hyphens (`pipeline-exploration-advanced`), never underscores.
5. **Never strip `upstream_provenance` from sink_parquet step** in `app/modules/orchestrator.py` — that's BUG-CACHE-1's keystone.
6. **Never import a handler module from a non-Shiny context** (ADR-045 Two-Category Law). `app/modules/` = pure; `app/handlers/` = Shiny-only.
7. **Shared reactive.Values stay in `home_theater.define_server()`**: `applied_filters`, `_pending_filters`, `_propagation_scratch` must be created there and passed as kwargs to sub-handlers. They must NOT be module-level globals.

---

## Reporting Cadence

After every 2 commits or any failure:

```
PROGRESS REPORT — Phase 24
Steps completed: [list]
Tests: N/N pass
Lines removed from home_theater.py: N (was 2853)
Next step: [step id + brief description]
Blockers: [none / describe]
```

---

## Stopping Conditions — Agent Must Halt and Ask User

Stop and post a blocker report if:

- Any verification gate fails twice on the same step.
- An extraction would require changing a function *signature* on the public surface of `define_server(...)` in `home_theater.py`.
- Any `@reactive.Effect` / `@render.*` boundary becomes unclear (e.g., two reactives sharing a closure variable that can't be cleanly passed as kwargs).
- Total LOC added to new files differs from LOC removed from `home_theater.py` by more than 5% after cleanup commits. (Indicates hidden logic drift.)
- A new import dependency surfaces that wasn't listed in the change manifest.

---

## Public Surface (Do Not Change)

`app/src/server.py` calls:
```python
from app.handlers.home_theater import define_server
define_server(input, output, session, *,
              bootloader, wrangle_studio, dev_studio,
              orchestrator, viz_factory, gallery_viewer,
              current_persona, anchor_path, tier1_anchor,
              tier_reference, tier3_leaf, active_cfg,
              active_collection_id, safe_input,
              active_home_subtab, tier_toggle,
              home_state=None, session_manager=None)
```

This signature must remain **byte-for-byte identical** after Phase 24.

Sub-handler `define_*()` calls are internal — their signatures can evolve freely within the decomposition.

---

## Key Conventions to Carry Into New Files

- Every new handler file needs the `@deps` header comment block (see `home_theater.py` L22–27 for format).
- `_safe_id()` and `_collect_all_group_plot_ids()` stay in `home_theater.py` (called at init time before sub-handlers are registered).
- Filter operator contract: `closed=` field on between rows must be `'both'` or `'none'`. Anything else triggers defensive fallback. This logic lives in `t3_recipe_engine.py` after 24-A.
- PK filter is ALLOWED (ADR-049a). Do not reintroduce `if is_pk: node_type = "exclusion_row"` silent-conversion.
