# Handoff — Session 7 (2026-04-21)

**Branch:** dev  
**Last commit before session:** `125b046` (reverted commit — see git log)

---

## What Was Done This Session

### 1. `from pathlib import Path` — Missing Import in wrangle_studio.py

`architect_data_status_ui` and `architect_active_table` used `Path(...)` but the module had no top-level import.

**Fix:** Added `from pathlib import Path` at line 2 of `app/modules/wrangle_studio.py`. Removed a redundant local `from pathlib import Path as _Path` that existed inside `architect_active_plot`.

---

### 2. Hierarchical Field Cards (replaced flat table)

The `_fields_table` renderer showed a flat HTML table — hard to read for fields with rich metadata.

**Replaced with `_field_card` + `_fields_cards`:**
- `_field_card(slug, meta)`: one Bootstrap card per field with left-border accent, type badge (CAT/NUM/STR/BOOL/DATE coloured), 🔑 PK marker, label, source column, description
- `_fields_cards(fields, slot_name)`: accepts dict OR list; normalises; renders count badge; loops over `_field_card`
- `_fields_table` kept as alias so all callers continue to work

Also fixed `lineage_upstream_ui` and `lineage_downstream_ui` — previously gated on `isinstance(upstream, list)` which caused dict fields to fall through to a raw `pre(str(...))` dump.

---

### 3. Plot Error Banner

`architect_active_plot` was silently returning `None` on all failure paths. User saw a blank plot pane with no explanation.

**Fix:**
- Added `_plot_error = reactive.Value("")` in `define_server`
- Added `architect_plot_error_ui` output renderer — shows a yellow Bootstrap warning banner when non-empty
- Updated `architect_active_plot` to call `_plot_error.set(msg)` on every error path
- Cleared `_plot_error` on success

---

### 4. Live View → Two Stacked Collapsible Cards

Replaced the single "Live View (Result)" card in Zone C with two independent Bootstrap 5 collapsible cards:

- **Card 1 (top):** 📋 Live Data Glimpse — status line + DataGrid table
- **Card 2 (bottom):** 📈 Plot Preview — error banner + matplotlib figure

Each card has its own `data-bs-toggle="collapse"` button and starts expanded (`class="collapse show"`).

---

### 5. Orchestrator Bug 1 — Wrong Base Ingredient

**Symptom:** `mlst_bar` rendered "Aesthetic 'x' references unknown column 'sequence_type'" because the materialised parquet didn't contain `sequence_type`.

**Root cause:** `DataAssembler` uses `list(ingredients.keys())[0]` as the base frame. Orchestrator was passing ALL `data_schemas` from the manifest to `DataAssembler` in iteration order. `Summary` came before `MLST` alphabetically, so `Summary` became the base of the `MLST_with_metadata` assembly — wrong.

**Fix:** Build `assembly_ingredients` as an ordered dict of only the collection's declared `ingredients:` list, in declaration order:

```python
ingredient_ids = [
    item.get("dataset_id") if isinstance(item, dict) else item
    for item in collection_spec.get("ingredients", [])
]
assembly_ingredients = {
    ds_id: ingredients[ds_id]
    for ds_id in ingredient_ids
    if ds_id in ingredients
}
```

---

### 6. Orchestrator Bug 2 — Missing Path A for Bare Data Schemas

**Symptom:** `amr_heatmap` (targets `ResFinder`, a `data_schema`) rendered "Aesthetic 'x' references unknown column 'gene'" and the Live Data Glimpse showed `FastP_with_metadata` data instead of `ResFinder`.

**Root cause:** When `collection_id` was not found in `join_manifests`, orchestrator fell through to the legacy fallback (Path C), which picked the first declared assembly (`FastP_with_metadata`). `ResFinder` is a bare data schema — it should be materialised directly without any assembly step.

**Fix:** Added Path A — checks `collection_id in ingredients` before falling to Path C:

```python
if collection_spec is None and collection_id in ingredients:
    lf = ingredients[collection_id]
    lf.sink_parquet(output_path, compression="snappy")
    return pl.scan_parquet(output_path)
```

---

### 7. Orchestrator Bug 3 — Join Key Dtype Mismatch

**Symptom:** `virulence_bar`, `virulence_variants` (targeting `ST22_Anchor`) failed with `SchemaError: type mismatch` during Polars join. `ST22_Anchor` joins 6 ingredients where `sample_id` is `str` in `ResFinder` but `cat` in all others.

**Root cause:** Polars requires join key columns to have matching dtypes. `Categorical ≠ String` even though both hold string data.

**Fix:** Before calling `DataAssembler`, scan all recipe steps for join keys (`on`, `left_on`, `right_on`) and cast those columns to `String` on the relevant ingredient frames. Handles both symmetric and asymmetric join keys.

See `app/modules/orchestrator.py` — the `per_ingredient_cast` / `base_cast` block above the `DataAssembler` call.

---

### 8. Removed Stale Cache Guards

Five `if not out_p.exists(): materialize(...)` guards in `server.py` were preventing the orchestrator from rerunning when the manifest or code changed. DataAssembler's internal hash check (ADR-024) handles caching correctly.

**Fix:** Removed all five guards. Orchestrator always called; DataAssembler skips the sink if the logic hash matches.

---

## Root Causes Found This Session

| Bug | Root Cause |
|---|---|
| `Path` not defined | `wrangle_studio.py` used `Path` without importing it |
| Upstream/downstream showed raw dict string | `isinstance(upstream, list)` gate dropped dict fields to `pre(str(...))` |
| Plot errors invisible | `architect_active_plot` returned `None` silently on all failure paths |
| `mlst_bar` wrong columns | Orchestrator passed all data_schemas to DataAssembler; wrong first ingredient became base |
| `amr_heatmap` wrong dataset | No Path A for bare data_schema — fell to fallback assembly instead |
| Virulence plots SchemaError | `sample_id` dtype mismatch (str vs cat) across `ST22_Anchor` ingredients |
| Stale parquets served indefinitely | `if not out_p.exists()` guards prevented re-materialisation after code/manifest changes |

---

## Knowledge Documents Updated

1. **`manifest_data_contract_rules.md`** — Added four new sections:
   - §11: Orchestrator materialization paths (Path A / B / C)
   - §12: DataAssembler order-dependency (first ingredient = base)
   - §13: Join key dtype normalisation (Categorical ↔ String fix)
   - §14: The `if not exists` anti-pattern for Blueprint Architect

---

## Deferred Items (carry forward)

| Item | Status |
|---|---|
| TubeMap aesthetics — tighter rail/tube look | DEFERRED |
| Rename 'ref' → 'Add' (Additional Dataset) in nodes and legend | DEFERRED |
| Phase 18-E — Field Gap Analysis reverse navigation | DEFERRED |

---

## Next Likely Work

- Verify all plots now render correctly: `mlst_bar`, `amr_heatmap`, `virulence_bar`, `virulence_variants`
- Test modular `!include` manifests (VIGAS-P) — Mode A path — upstream/downstream contracts
- Consider: should `output_fields: {}` (empty dict) be normalized at display time to show inherited fields rather than an empty table?
- Blueprint Architect aesthetics pass (TubeMap tighter layout, colours)
