# Handoff — Session 6 (2026-04-21)

**Branch:** dev  
**Last commit before session:** `48a4644` (zoom controls + assembly materialization)

---

## What Was Done This Session

### 1. Interface (Fields) — Vertical Layout
**File:** `app/modules/wrangle_studio.py` ~L157–182

Replaced `ui.layout_columns([4,4,4])` with a `ui.div` stack of three full-width cards. Each card has `overflow-y: auto; max-height` so long field lists scroll independently. No more horizontal scrolling required to see all three contracts.

### 2. `_resolve_fields_for_schema` — Inline Fields Support  
**File:** `app/src/server.py` ~L491–560

Added two new resolution passes to handle inline manifests (no `!include`):
- **Pass 2:** `siblings["output_fields"] == {"inline": {...}}` — inline output_fields dict
- **Pass 5:** `siblings["input_fields"] == {"inline": {...}}` — inline input_fields dict (final fallback)

Pass 4 (assembly ingredient merge) now only short-circuits on non-empty result, allowing fallthrough when ingredients also have no explicit output_fields.

### 3. Upstream Backtracking for Plot Nodes — Mode B (Inline)
**File:** `app/src/server.py` ~L2300–2337

Added a dedicated `elif role_b in ("plot_spec", "plot_wrangling")` branch in Mode B's field resolution. Previously the `else` branch ran and set `active_upstream = in_f` (the plot's own `input_fields` = nothing). Now:
- Resolves `target_dataset`'s output fields via `_resolve_fields_for_schema`
- Sets `active_viz_id` for plot preview
- Materializes `target_dataset` parquet for Live Data Glimpse
- Also handles `pre_plot_wrangling` nodes via the same target_dataset scan

### 4. `plot_target_ds` Never Being Set — Root Cause Fix
**File:** `app/src/server.py` ~L2239–2254

The analysis_groups scan was looking for `pspec.get("target_dataset")` but the actual manifest structure nests `target_dataset` under `spec:`:

```yaml
mlst_bar:
  info: ...
  spec:
    target_dataset: MLST_with_metadata   # ← nested here
```

Fixed: now checks `pspec.get("target_dataset") or pspec.get("spec", {}).get("target_dataset")`.

The scan also moved from "only run when `target is None`" to always running, so `plot_target_ds` is correctly populated even when the plot_id happens to also appear elsewhere.

---

## Root Causes Found This Session

| Bug | Root Cause |
|---|---|
| Upstream Contract empty for plot nodes | `target_dataset` is under `plot_spec["spec"]["target_dataset"]`, not `plot_spec["target_dataset"]` |
| Upstream Contract empty for inline assemblies | `_resolve_fields_for_schema` had no pass for inline `{"inline": {...}}` siblings |
| Live Data Glimpse empty for inline plots | Mode B never set `active_anchor_path` for plot_spec role |
| `plot_target_ds` always None for all inline plots | Scan was only run when `target is None` and was checking wrong key depth |

---

## Knowledge Documents Written

1. **`manifest_data_contract_rules.md`** — NEW — Comprehensive reference on:
   - All manifest sections and their roles
   - Field inheritance rules (the full resolution protocol)
   - Inline vs. modular vs. hybrid manifest styles
   - ctx_map structure and key registration rules
   - Known edge cases with their fixes
   - Implementation checklist

2. **`blueprint_architect_ux_spec.md`** — UPDATED:
   - Status updated to reflect Session 5/6 completion
   - Section 2.5: Updated from Mermaid description to Cytoscape.js implementation
   - Section 2.6: New — Click bridge details, `_do_load_component` flow
   - Section 4: Layout changed from 3-column to vertical stack diagram
   - Section 4.1: New — Upstream backtracking for plot nodes, `spec.target_dataset` warning

---

## Deferred Items (carry forward)

| Item | Status |
|---|---|
| TubeMap aesthetics — tighter rail/tube look | DEFERRED |
| Rename 'ref' → 'Add' (Additional Dataset) in nodes and legend | DEFERRED |
| Phase 18-E — Field Gap Analysis reverse navigation | DEFERRED |

---

## Next Likely Work

- Verify the upstream contract and Live Data Glimpse now work for `mlst_bar` and other inline plots
- Verify assembly nodes (e.g. `Summary_phenotype_length_fragmentation`) show correct upstream ingredients accordion
- Test modular `!include` manifests (VIGAS-P) — Mode A path — upstream/downstream contracts
- Consider: should `output_fields: {}` (empty dict with keys) be normalized at display time to show inherited fields rather than empty table?
