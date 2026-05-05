# Handoff — Session 8 (2026-04-30)

**Branch:** dev  
**Last commit:** `76b3f02` feat(21-E): implement Comparison Mode

---

## What Was Done This Session

### 1. Documentation — Session 7 Catch-Up

Updated `manifest_data_contract_rules.md` with four new sections (§11–§14) covering the orchestrator bugs found and fixed in session 7:

- **§11** — Three-path orchestrator resolution (Path A: bare data_schema, Path B: assembly, Path C: fallback)
- **§12** — DataAssembler order-dependency (first ingredient = base; anti-pattern of passing all project schemas)
- **§13** — Join key dtype normalisation (Categorical ↔ String mismatch; the `per_ingredient_cast`/`base_cast` general solution)
- **§14** — The `if not out_p.exists()` anti-pattern (stale cache; why the guard must be removed)

Created `handoff_session7.md` covering all 8 changes from session 7.

### 2. Task Housekeeping

Added "Blueprint Architect — Deferred Aesthetics & Debug" section to `tasks.md` with:
- "Data: …" header display review (deferred)
- TubeMap aesthetics (deferred)
- Full Blueprint debug pass (deferred)

Added persona launch commands + capability matrix to `EVE_WORK/notes/cheatsheat.md` and committed as demo-safe snapshot (`5b406c6`).

### 3. Phase 22-J Status Verified

Code-verified all 24 Phase 22-J features present in the implementation. Only `22-J-13` (live-UI test) remains pending.

### 4. Phase 21-G — Confirmed Complete

Verified that `right_sidebar_content_ui` already returns `ui.div()` for `pipeline-static` and `pipeline-exploration-simple`. Full T2/T3 audit stack renders for advanced personas. `btn_revert` concept was superseded by 🗑 delete in Phase 22-I. Marked done.

### 5. Phase 21-E — Comparison Mode (main new work)

**File:** `app/handlers/home_theater.py`

#### Fix: `comparison_mode_toggle_ui` (line ~2434)

- Replaced underscore persona IDs (`pipeline_exploration_advanced`) with hyphen IDs (`pipeline-exploration-advanced`) — same bug class as 22-H-2
- Added tier gate: toggle only renders when `tier_toggle.get() == "T3"` (comparing T2 vs T3 only makes sense in T3 mode)
- Label changed to "⚖ Compare T2 vs T3"

#### New: `_make_cmp_baseline_handler(p_id)` factory

Registered alongside `_make_group_plot_handler` at server init. Renders `plot_group_{p_id}_cmp_base`:
- Same data resolution as the regular handler (target_dataset → materialize_tier1, fallback to tier1_anchor)
- Skips ALL T3 audit nodes (no `_t3_filter_rows`, no `_t3_drop_columns`)
- Represents the pure T1 baseline — what the data looks like before any user adjustments

#### Fix: Toggle placed in layout

Added `ui.output_ui("comparison_mode_toggle_ui")` to `theater_header` in `dynamic_tabs`. Previously the render existed but was never placed in any layout — it was completely invisible.

#### New: 2-column layout in `dynamic_tabs`

`dynamic_tabs` now reads `input.comparison_mode`. When ON:
- Each plot tab renders `ui.layout_columns([6, 6], ...)` instead of a single `ui.output_plot`
- Left column: grey badge "T2 — Baseline (Analysis-ready)" + `plot_group_{p_id}_cmp_base`
- Right column: amber badge "T3 — My adjustments" + `plot_group_{p_id}` (existing handler with T3 audit nodes applied)

**Use:** In T3 mode with committed audit nodes (filters, exclusions, column drops), flip the toggle to see the before/after side-by-side.

---

## Root Causes Found This Session

| Issue | Root Cause |
|---|---|
| Comparison Mode toggle never visible | `ui.output_ui("comparison_mode_toggle_ui")` missing from `theater_header` layout |
| Toggle showed for wrong personas | Underscore persona IDs — same class as 22-H-2 |
| No visual diff in comparison mode | No baseline handler registered; layout only had single plot output |

---

## Files Changed This Session

- `.antigravity/knowledge/manifest_data_contract_rules.md` — §11–§14 added
- `.antigravity/knowledge/handoff_session7.md` — created
- `.antigravity/knowledge/handoff_session8.md` — this file
- `.antigravity/tasks/tasks.md` — Phase 21-E done, 21-G done, deferred items added
- `EVE_WORK/notes/cheatsheat.md` — persona launch commands + matrix
- `app/handlers/home_theater.py` — Phase 21-E implementation

---

## Deferred Items (carry forward)

| Item | Status |
|---|---|
| 22-J-13 Live-UI verification | PENDING — user must run `tasks_test_22J.md` |
| Phase 21-H Headless verification | NOT STARTED — next dev item |
| ST22 Lineage 2 (Plasmid Dynamics) | NOT STARTED |
| Phase 23-A–E Deployment Architecture | DESIGNED, not implemented |
| Blueprint Architect aesthetics | DEFERRED |
| TubeMap rename ref→Add | DEFERRED |
| "Data: …" header display | DEFERRED |

---

## Next Likely Work

1. **Phase 21-H** — Headless verification script (`debug_home_theater.py`) for all 5 personas
2. **ST22 Lineage 2** — Build Plasmid Dynamics manifest + assembly (enables meaningful T2/T3 comparison)
3. **Phase 23-A** — Bootloader extension (deployment profiles)
