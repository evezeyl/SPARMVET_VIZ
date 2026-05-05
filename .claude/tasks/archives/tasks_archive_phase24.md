# Phase 24 Task Plan — `home_theater.py` Decomposition

**ADR:** ADR-051
**Protocol:** `.claude/knowledge/refactor_protocol_phase24.md` — read this first
**Source file:** `app/handlers/home_theater.py` (2853 lines as of 2026-04-30)
**Pre-condition gate:** 90/90 pytest pass + `from app.src.main import app` clean

---

## Pre-flight (do once, before 24-A)

- [ ] `git tag pre-phase24-$(date +%Y%m%d)`
- [ ] Capture baseline: `PYTHONPATH=. ./.venv/bin/python -m pytest libs/ app/tests/ -q 2>&1 | tee .claude/baselines/phase24_pre.txt`
- [ ] Confirm 90/90 pass before proceeding

---

## Step 24-A — Extract pure helpers → `app/modules/t3_recipe_engine.py`

**Risk:** Low (pure functions, no Shiny)
**Source lines in home_theater.py:** L284–L381

### Functions to move

| Function | Source lines | Notes |
|---|---|---|
| `_is_numeric(dt)` | L306–L309 | Inner closure of `_apply_filter_rows` — extract as module-level |
| `_coerce_to_dtype(value, dt)` | L311–L321 | Inner closure — extract as module-level |
| `_apply_filter_rows(lf, filter_rows)` | L284–L381 | Move wholesale; remove closure wrappers |

### Functions to keep in home_theater.py
- `_t3_filter_rows()` (L258–L283) — stays (reactive, reads `home_state`)
- `_t3_drop_columns()` (L210–L222) — stays (reactive)
- `_active_plot_t3_nodes()` (L194–L209) — stays (reactive)

### New file interface
```python
# app/modules/t3_recipe_engine.py
def apply_filter_rows(lf: pl.LazyFrame, filter_rows: list[dict]) -> pl.LazyFrame: ...
def extract_t3_filter_rows(t3_recipe_by_plot: dict, plot_id: str | None) -> list[dict]: ...
def extract_t3_drop_columns(t3_recipe_by_plot: dict, plot_id: str | None) -> list[str]: ...
```

### home_theater.py after move
```python
from app.modules.t3_recipe_engine import apply_filter_rows
# Replace all internal calls to _apply_filter_rows → apply_filter_rows
```

### Also update viz_factory filter loop
`libs/viz_factory/src/viz_factory/viz_factory.py` has a second copy of the dtype coercion logic (DEMO-4 fix). After 24-A, it should import `apply_filter_rows` from `t3_recipe_engine` OR keep its own copy with a comment noting the duplication. Do NOT silently diverge the two paths.

### Verification gate
```bash
PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_operators.py -v  # 21/21
PYTHONPATH=. ./.venv/bin/python -m pytest libs/ app/tests/ -q                    # 90/90
python -c "from app.src.main import app; print('OK')"
```

### Commits
- **24-A-move**: copy functions to new file, import in home_theater.py, replace call sites
- **24-A-cleanup**: remove dead code from home_theater.py, update `@deps` header

### Change manifest (executed 2026-04-30, Opus)

```
Target new file: app/modules/t3_recipe_engine.py
Source lines in home_theater.py: L284–L381
Names being MOVED:
  - _apply_filter_rows(lf, filter_rows) — closure inside define_server
    (nested helpers _is_numeric, _coerce_to_dtype stay nested as in source)
Names being KEPT in home_theater.py:
  - 1 internal call site at L886 — uses the imported name after move
  - _t3_filter_rows, _active_plot_t3_nodes, _t3_drop_columns STAY (reactive closures)
Dependencies being added to new file:
  imports: polars as pl
  reactive sources consumed: NONE (pure function)
  reactive sources created: NONE
Kwargs added to new file's signature: NONE — module-level pure function
Deviations from initial plan:
  - Keeping symbol name `_apply_filter_rows` (NOT renaming to `apply_filter_rows`)
    in move commit. Protocol forbids renames here. Rename deferred to cleanup
    or future commit.
  - viz_factory parallel copy NOT touched in 24-A; deferred to a later step.
Risk level: LOW
```

---

## Step 24-B — Extract session persistence → `app/handlers/session_handlers.py`

**Risk:** Low (self-contained, minimal reactive deps)
**Source lines in home_theater.py:** L1772–L1994

### Functions to move

| Function | Source lines | Notes |
|---|---|---|
| `session_management_ui()` | L1774–L1889 | @output @render.ui |
| `_handle_session_import()` | L1891–L1909 | @reactive.Effect |
| `_handle_session_actions()` | L1911–L1940 | @reactive.Effect |
| `_restore_session(session_key)` | L1941–L1995 | plain def, called by _handle_session_actions |

### Reactive deps needed as kwargs
- `input`, `output`, `session` (standard)
- `session_manager` — passed through already
- `active_cfg` — reactive.Calc
- `active_collection_id` — reactive.Calc
- `home_state` — reactive.Value[dict]
- `tier_toggle` — reactive.Value[str]
- `tier1_anchor`, `tier_reference`, `tier3_leaf` — for restore path

### New file entry point
```python
# app/handlers/session_handlers.py
def define_session_server(input, output, session, *,
                          session_manager, active_cfg, active_collection_id,
                          home_state, tier_toggle,
                          tier1_anchor, tier_reference, tier3_leaf): ...
```

### home_theater.py after move
```python
from app.handlers.session_handlers import define_session_server
# Inside define_server():
define_session_server(input, output, session,
                      session_manager=session_manager, ...)
```

### Commits
- **24-B-move**: copy to new file, add define_session_server call in home_theater.py
- **24-B-cleanup**: remove dead code from home_theater.py, update `@deps` header

### Change manifest (executed 2026-04-30, Opus)

```
Target new file: app/handlers/session_handlers.py
Source lines in home_theater.py (post-24-A): L1676–L1900
Names being MOVED:
  - session_management_ui()        @output @render.ui
  - _handle_session_import()       @reactive.Effect
  - _handle_session_actions()      @reactive.Effect
  - _restore_session(session_key)  plain helper called by _handle_session_actions
Names being KEPT in home_theater.py:
  - call to define_session_server(input, output, session, ...) at the same location
  - _export_bundle_filename() — belongs to export step, NOT moved here
Dependencies being added to new file:
  imports: from pathlib import Path; from shiny import reactive, render, ui
  reactive sources consumed: current_persona (read), home_state (read+set)
  reactive sources created: NONE
Kwargs added to define_session_server signature:
  input, output, session, *, session_manager, current_persona, home_state
Deviations from initial plan:
  - tasks_phase24.md plan listed tier1_anchor / tier_reference / tier3_leaf
    / active_cfg / active_collection_id as kwargs. The actual block reads NONE
    of those — restore writes only into home_state. Final signature is leaner
    than planned.
Risk level: LOW (confirmed by verification gate)
Verification:
  - 90/90 unit tests pass after move
  - App import clean
  - 10/12 smoke pass (2 persona-skip), ~19s, no regression
home_theater.py: 2759 → 2545 (-214 lines)
```

---

## Step 24-C — Extract export pipeline → `app/handlers/export_handlers.py`

**Risk:** Medium (async download handler, reads many reactive sources)
**Source lines in home_theater.py:** L1232–L1770

### Functions to move

| Function | Source lines | Notes |
|---|---|---|
| `system_tools_ui()` | L1234–L1285 | @output @render.ui — contains export_bundle_download button |
| `export_bundle_download()` | L1287–L1637 | @render.download — async, large |
| `export_audit_report_ui()` | L1640–L1693 | @output @render.ui |
| `export_audit_report_html()` | L1695–L1736 | @render.download |
| `export_audit_report_docx()` | L1737–L1762 | @render.download |
| `_audit_report_filename(fmt)` | L1763–L1771 | plain def, helper |
| `_export_bundle_filename()` | L1996–L2004 | plain def — note: currently AFTER session block; move together |

### Reactive deps needed as kwargs
- `input`, `output`, `session`
- `bootloader`, `orchestrator`
- `current_persona` — reactive.Value[str]
- `active_cfg`, `active_collection_id`, `anchor_path`
- `tier1_anchor`, `tier_reference`, `tier3_leaf`
- `home_state`
- `session_manager`

### Commits
- **24-C-move**: copy to new file, call define_export_server in home_theater.py
- **24-C-cleanup**: remove dead code, update `@deps` header

### Change manifest (executed 2026-05-01, Opus)

```
Target new file: app/handlers/export_handlers.py
Source lines in home_theater.py (post-24-B):
  L1139–L1192  system_tools_ui              @output @render.ui
  L1194–L1541  export_bundle_download       @render.download (async, ~347 lines)
  L1543–L1600  export_audit_report_ui       @output @render.ui
  L1602–L1642  export_audit_report_download @render.download
  L1644–L1668  export_audit_docx            @render.download
  L1670–L1675  _audit_report_filename       plain helper
  L1688–L1695  _export_bundle_filename      plain helper (was below 24-B block)
Names being MOVED: all 7 above into define_export_server
Names being KEPT in home_theater.py:
  - call to define_export_server(...) at the original location
  - existing _op_label (used by filter_rows_ui — stays until 24-D)
Cross-block dependency:
  - export_bundle_download uses _op_label twice. Resolved by INLINING a
    duplicate _op_label at module top of export_handlers.py (3-line pure
    lookup). When 24-D extracts the filter block, _op_label will be lifted
    to t3_recipe_engine.py and both handlers will import it from there.
Dependencies added to new file:
  imports: pathlib.Path, polars as pl, shiny.{reactive, render, ui}
  reactive sources consumed (kwargs):
    bootloader, orchestrator, viz_factory,
    current_persona, active_cfg,
    tier1_anchor, tier_reference, tier3_leaf,
    tier_toggle, applied_filters, home_state, safe_input
  reactive sources created: NONE
Risk level: MEDIUM (largest single block, multiple reactive deps)
Verification:
  - 90/90 unit tests pass
  - App import clean
  - 10/12 smoke pass (2 persona-skip), ~19s — no regression
home_theater.py: 2545 → 2017 (-528 lines)
Cumulative since pre-flight: 2853 → 2017 (-836 lines, -29.3%)
```

---

## Step 24-D — Extract filter UI + T3 audit → `app/handlers/filter_and_audit_handlers.py`

**Risk:** High (largest block, reactive state passed by reference, propagation modal)
**Source lines in home_theater.py:** L2005–L2762

> Read the full block BEFORE writing the change manifest. The filter UI renderers and T3 audit reactives are deeply interleaved. If splitting into two files looks cleaner, do it — but note the decision here.

### Functions to move

| Function | Source lines | Notes |
|---|---|---|
| `sidebar_filters()` | L2007–L2025 | @output @render.ui |
| `filter_rows_ui()` | L2027–L2061 | @output @render.ui |
| `filter_form_ui()` | L2064–L2205 | @output @render.ui — large, dtype-aware widgets |
| `filter_controls_ui()` | L2208–L2243 | @output @render.ui |
| `_op_label(op)` | L2244–L2248 | pure helper |
| `_filter_add_row()` | L2251–L2319 | @reactive.Effect |
| `_filter_apply()` | L2322–L2384 | @reactive.Effect — calls _open_propagation_modal |
| `_filter_reset()` | L2387–L2391 | @reactive.Effect |
| `_col_drop_to_audit()` | L2394–L2458 | @reactive.Effect |
| `_column_presence_per_plot(...)` | L2459–L2502 | plain def |
| `_open_propagation_modal(...)` | L2503–L2627 | plain def — builds ui.modal |
| `_handle_propagation_confirm()` | L2630–L2706 | @reactive.Effect |
| `_plot_has_column(...)` | L2707–L2728 | plain def |
| `_clear_filters_on_t3_apply()` | L2730–L2746 | @reactive.Effect |
| `_make_remove_handler(idx)` | L2748–L2762 | factory returning @reactive.Effect |

### Reactive state: MUST be passed as kwargs (not re-created)
These are created in `home_theater.define_server()` and must be passed through:
- `applied_filters` — reactive.Value([])
- `_pending_filters` — reactive.Value([])
- `_propagation_scratch` — reactive.Value({"nodes": [], "kind": ""})

Also needed:
- `input`, `output`, `session`
- `active_cfg`, `active_collection_id`
- `active_home_subtab` — reactive.Value[str]
- `tier_toggle` — reactive.Value[str]
- `home_state` — reactive.Value[dict]
- `tier1_anchor`, `tier_reference`, `tier3_leaf`
- `_all_plot_subtab_ids` — callable (the closure defined at L223)
- `_plot_label` — callable (closure at L245)
- `apply_filter_rows` — imported from t3_recipe_engine (after 24-A)

### Commits
- **24-D-move**: copy to new file, call define_filter_audit_server in home_theater.py
- **24-D-cleanup**: remove dead code, update `@deps` header

### Change manifest (executed 2026-05-01, Opus)

```
Target new file: app/handlers/filter_and_audit_handlers.py
  (single file — filter UI and T3 propagation share _propagation_scratch
   and call into a common modal helper. Splitting would force exposing
   scratch state across module boundaries.)
Source lines in home_theater.py (post-24-C): L1169–L1926 (~758 lines)
Names being MOVED (15 + 1 reactive.Value):
  sidebar_filters, filter_rows_ui, filter_form_ui, filter_controls_ui,
  _filter_add_row, _filter_apply, _filter_reset, _col_drop_to_audit,
  _column_presence_per_plot, _open_propagation_modal,
  _handle_propagation_confirm, _plot_has_column, _clear_filters_on_t3_apply,
  _make_remove_handler (+ 50-element handler registry),
  _last_apply_count (reactive.Value, private to filter block)

Names being KEPT in home_theater.py:
  - call to define_filter_audit_server(...) at the original location

Folded prep step (in same move commit, not a separate one):
  - Lifted _op_label from home_theater define_server to
    app/modules/t3_recipe_engine.py (canonical place for pure filter helpers).
  - export_handlers.py: replaced inline _op_label def with import from
    t3_recipe_engine. Removes the 24-C inline-duplicate.
  - filter_and_audit_handlers.py imports _op_label from t3_recipe_engine.

Reactive state passed as kwargs (NOT recreated):
  applied_filters, _pending_filters, _propagation_scratch, home_state
Closures from home_theater.define_server passed as callable kwargs:
  _resolve_active_spec, _resolve_active_lf, _spec_discrete_axes,
  _t3_drop_columns, _all_plot_subtab_ids, _plot_label
Other kwargs:
  input, output, session, tier_toggle, active_home_subtab, safe_input
Reactive sources created INSIDE the new module (private):
  _last_apply_count = reactive.Value(0)

Risk level: HIGH (largest block, most reactive deps, propagation modal)
Verification:
  - 90/90 unit tests pass (incl. 21-case filter regression)
  - App import clean
  - 12/12 Playwright smoke pass (10 + 2 persona-skip), ~20s
    Includes all 4 filter pipeline tests: form_renders, add_filter_row,
    apply_filter_no_crash, filter_reset_clears_rows.
home_theater.py: 2017 → 1278 (-739 lines)
Cumulative since pre-flight: 2853 → 1278 (-1575 lines, -55.2%)
```

---

## Step 24-E — Validate and finalise home_theater.py

After steps 24-A..D, `home_theater.py` should be ~700–1000 lines containing:
- Module docstring + `@deps` header (updated)
- Imports
- `_safe_id()` (L47–L52)
- `_collect_all_group_plot_ids()` (L55–L81)
- `define_server()` signature + docstring + init block
- `_resolve_active_spec()`, `_resolve_active_lf()` (L151–L192, reactive helpers)
- `_all_plot_subtab_ids()`, `_plot_label()` (L223–L256, closures)
- `_make_group_plot_handler()` + `_make_cmp_baseline_handler()` (L400–L571)
- `dynamic_tabs()` (L573–L778)
- `_track_tier_toggle()`, `_sync_session_provenance()`, `_track_active_home_subtab()` (L779–L875)
- `home_data_preview()`, `home_col_selector_ui()`, `col_drop_audit_btn_ui()` (L876–L979)
- `sidebar_nav_ui()` (L980–L1007)
- `right_sidebar_content_ui()` (L1108–L1231)
- Calls to: `define_export_server(...)`, `define_session_server(...)`, `define_filter_audit_server(...)`
- `plot_reference()`, `table_reference()`, `plot_leaf()`, `table_leaf()`, `handle_plot_brush()`, `comparison_mode_toggle_ui()` (L2764–end)

### Final verification gate
```bash
PYTHONPATH=. ./.venv/bin/python -m pytest libs/ app/tests/ -q           # 90/90
PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_operators.py -v  # 21/21
python -c "from app.src.main import app; print('OK')"
wc -l app/handlers/home_theater.py  # should be 700–1100
```

### Commit
- **24-E-finalise**: update @deps header, confirm all sub-handler call sites are present, update handoff_active.md

---

## Post-Phase 24 Deliverables

- [ ] Update `@deps` header in home_theater.py to reflect new `provides/consumes`
- [ ] Update `architecture_decisions.md#ADR-051` status → IMPLEMENTED
- [ ] Update `handoff_active.md` with new file map
- [ ] Update `dependency_index.md` with new handler files
- [ ] Post line-count comparison: `home_theater.py` before (2853) vs after
