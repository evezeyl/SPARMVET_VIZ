# Design: T3 Export Threading + Lineage Recipe
# Covers: T3 node type gap + export bundle lineage (formerly EXPORT-SGE-2)
# Status: MOSTLY COMPLETE — aesthetic_override render wiring blocked by VIZFAC-RESOLVER-1.
#
# As of 2026-05-11:
# - Dead code (single_graph_export_handlers.py): REMOVED ✓
# - Lineage in export bundle: IMPLEMENTED as lineage_graph.json (shared-node DAG) ✓
# - T3 threading (filter_row, exclusion_row, drop_column): IMPLEMENTED ✓
#   via _t3_filter_rows() + _t3_drop_columns() in home_theater.py
# - t3_plot_overrides in export bundle: IMPLEMENTED ✓
#   export_handlers.py collects t3_plot_overrides dict and includes it in
#   t3_steps.yaml as "t3_aesthetic_overrides:" key; Methods prose extended.
# - aesthetic_override RENDERING (L5 cascade): PENDING — blocked by VIZFAC-RESOLVER-1.
#   The overrides are correctly recorded, exported, and shown in the audit panel,
#   but are not yet applied to rendered plots. That wiring is VIZFAC-T3-OVERRIDE-1.
# - T3 threading for rename/derive/pivot node types: pending (no node types yet)

---

## ⚠️ Architecture note (2026-05-04 export redesign)

The "Single Graph Export" accordion panel was **removed** from the sidebar. Its functionality
is now covered by the **"Active plot" scope option** in the 3-way scope toggle on the main
Export panel (`export_handlers.py`).

However, `app/handlers/single_graph_export_handlers.py` **still exists and is still imported**
by `home_theater.py` (line 50 import + line 1377 call). Its Shiny outputs
(`single_graph_export_ui`, `export_single_graph`) are registered but have **no UI mount point**
— the accordion that mounted them was removed. This is dead code.

**Decision needed:** Either (a) remove `single_graph_export_handlers.py` entirely and clean up
the import+call in `home_theater.py`, or (b) keep it for future re-use and add a comment.
Until this is decided, Problem 1 and Problem 2 below remain relevant to the handler file.

---

## Problem 1 — T3 node types not threaded through `_resolve_active_lf`

**Applies to:** `single_graph_export_handlers.py` (currently dead code — see note above)
AND to `export_handlers.py` (the active scope-based export bundle).

**Current state:**
Only `drop_column` and `filter_row`/`exclusion_row` T3 nodes are applied to the
LazyFrame before export. They are extracted by `_t3_drop_columns()` and
`_t3_filter_rows()` in `home_theater.py`.

If new T3 node types are added (rename, derive, pivot, cast …), they will:
- be committed to `t3_recipe.json` correctly (ghost + session)
- appear in the on-screen plot correctly IF `viz_factory.render()` respects them
- **NOT appear in the exported TSV** in the export bundle

**Where the gap lives:**
`single_graph_export_handlers.py` — lines ~139–147:
```python
lf = _resolve_active_lf(spec)
drops = [c for c in _t3_drop_columns(subtab) if c in lf.collect_schema().names()]
if drops:
    lf = lf.drop(drops)
```
Filter rows are injected into `plot_spec["filters"]` (line ~119–131), which
`viz_factory.render()` applies internally. Column drops are applied here directly.

The same gap exists in `export_handlers.py` for the scope-based bundle export.

**Recommended fix:**
Create `_apply_t3_to_lf(lf, subtab) -> LazyFrame` in `home_theater.py` that iterates
`_active_plot_t3_nodes(subtab)` and dispatches on `node_type`:
- `drop_column` → `lf.drop([col])`
- `filter_row` / `exclusion_row` → already handled via `_apply_filter_rows`
- `rename` (future) → `lf.rename({old: new})`
- `derive` (future) → `lf.with_columns([expr])`
- `pivot` (future) → `lf.collect().pivot(...).lazy()` (pivot breaks LazyFrame)

Then use `_apply_t3_to_lf` in both export handlers and the data-preview path
so all three paths are consistent.

---

## Problem 2 — No lineage recipe in the export bundle

**Current state:**
The export bundle includes `recipes/<proj>/` (all YAML files) and `t3_steps.yaml`
(T3 committed nodes). A reader can reconstruct the wrangling pipeline but must
manually trace which join recipe produced the dataset for a given plot.

**Data linkage pattern (from manifests):**
Plot spec has `target_dataset: "legacy_results"`.
The full manifest has:
- `data_schemas.legacy_results` — field contracts
- `join_manifests.legacy_results` — the T1→T2 join recipe (join, wrangle steps)

**Proposed addition: `full_recipe.yaml` per in-scope plot:**

```yaml
# Full reproducible recipe for plot: amr_profile
plot_id: amr_profile
target_dataset: legacy_results

# ── T1/T2 ──────────────────────────────────────────────────────────────────
data_schema:
  # from manifest data_schemas.{target_dataset}
  fields: …

join_recipe:
  # from manifest join_manifests.{target_dataset}
  recipe: …

# ── T3 (user session) ───────────────────────────────────────────────────────
t3_nodes:
  # from committed home_state.t3_recipe_by_plot[subtab]
  - node_type: drop_column
    params: {column: year}
    active: true
  …

# ── Plot spec ───────────────────────────────────────────────────────────────
plot_spec:
  # from manifest plots.{plot_id}
  type: bar
  …
```

**Implementation sketch (in `export_handlers.py`, once per in-scope plot):**

```python
target_ds = spec.get("target_dataset", "")
raw = cfg.raw_config

full_recipe = {
    "plot_id": p_id,
    "target_dataset": target_ds,
    "data_schema": raw.get("data_schemas", {}).get(target_ds, {}),
    "join_recipe": raw.get("join_manifests", {}).get(target_ds, {}),
    "t3_nodes": _active_plot_t3_nodes(subtab),
    "plot_spec": spec,
}
zf.writestr(f"recipes/{p_id}_full_recipe.yaml", yaml.safe_dump(full_recipe, sort_keys=False))
```

**Edge cases to resolve before implementing:**
- What if `target_dataset` is absent from the plot spec? (fall back to empty join block)
- What if `join_manifests` uses `!include` tags? (`raw_config` may not have resolved them)
  → Check if `active_cfg().raw_config` returns resolved or raw YAML. If raw, the `!include`
    paths need to be resolved or the included file content inlined.
- Multi-dataset plots? Check if the schema supports multiple `target_dataset` values.

---

## Summary

| Task | File(s) | Complexity | Prerequisite |
|------|---------|-----------|-------------|
| T3 threading gap | `home_theater.py` (new `_apply_t3_to_lf`), `export_handlers.py` | Low (now) / Medium (when new node types land) | Add new T3 node type first |
| Lineage recipe in bundle | `export_handlers.py` | Low-Medium | Confirm `!include` resolution in `active_cfg().raw_config` |
| Dead code cleanup | `home_theater.py` (remove import+call), `single_graph_export_handlers.py` (remove file) | Low | Decision: keep or remove handler |

**Suggested order:** (1) decide fate of `single_graph_export_handlers.py`; (2) resolve
`!include` question; (3) implement lineage recipe in bundle. T3 threading gap is a
forward-compatibility concern — no urgency until the first rename/derive node type is designed.
