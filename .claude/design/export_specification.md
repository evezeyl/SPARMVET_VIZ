# Export Specification
**Last updated:** 2026-05-04 (scope toggle refined to 3-way)  
**Status:** AGREED — pending implementation  
**Authority:** ADR-047 (extended), tasks EXPORT-REDESIGN-1/2

---

## 1. Export UI — Single accordion panel

One accordion panel labelled **"Export"** replaces the previous two-panel layout
(`Global Project Export` + `Single Graph Export`).

### 1.1 Scope toggle (3-way)

```
[ Global project ●  |  Active group ○  |  Active plot ○ ]
```

| Option | Scope | Tooltip shown on hover |
|---|---|---|
| **Global project** | All plots, all data, full recipes | "Export everything in the active project" |
| **Active group** | All plots in the group the current tab belongs to; lineage backtraced per plot | "Export all plots in the current group (e.g., all Quality Control plots)" |
| **Active plot** | The single plot currently displayed; its lineage backtraced | "Export only the plot you are currently viewing" |

**Source of truth for "active":** the currently open plot tab in the Home Theater.  
- `active_plot_id` = current tab  
- `active_group_id` = the `group_id` of `active_plot_id` (already in `ctx_map`)

**Disabled states:**

| Situation | Active group | Active plot |
|---|---|---|
| No plot tab open (data-preview tab, etc.) | Disabled — tooltip: *"Switch to a plot tab to enable scoped export."* | Disabled — same tooltip |
| Plot tab open, but the plot belongs to **no group** (ungrouped plot) | Disabled — tooltip: *"This plot has no group — use Active plot instead."* | Enabled |
| Plot tab open AND plot belongs to a group | Enabled | Enabled |

When the user navigates away from a plot tab while a scoped option is selected,
the toggle silently falls back to Global and the button exports globally.

**Detection:** `group_id` is stored per plot in `ctx_map`. If `group_id is None`
or the manifest has no `analysis_groups` (only a top-level `plots:` key), the
"Active group" option is hidden entirely, not just disabled.

**Persona gate:**
- Toggle only rendered when persona has **both** `export_enabled`.
- When only `export_enabled`: no toggle; button always operates in Global mode.
- Default: **Global project**.

### 1.2 Presentation controls (not content choices)

| Control | Options | Default |
|---|---|---|
| Quality | Web / Presentation · Publication (≥600 DPI) | Web |
| Plot format | PNG · SVG · PDF | PNG |
| Report format | HTML · PDF · DOCX | HTML |

These control HOW things are rendered, not WHAT is included.

### 1.3 One download button

```
[ 💾 Export Bundle ]
```

No separate "Export Audit Report" button. The audit trail is **automatically
included** in the bundle (as a section in `report.qmd`) when the conditions in
section 3 are met.

---

## 2. Global project export — bundle contents

ZIP filename: `YYYYMMDD_HHMMSS_<label>_results.zip`

| Path in ZIP | Included when | Notes |
|---|---|---|
| `plots/<plot_id>.<fmt>` | Always | All plots defined in active manifest |
| `data/<dataset>_T1.tsv` | Always | All datasets referenced by active plots |
| `data/<dataset>_T2.tsv` | Always | |
| `data/<dataset>_T3.tsv` | T3 active at export time | Advanced+ persona + T3 tier active |
| `recipes/<manifest_files>` | Always | All YAML files from active manifest directory |
| `recipes/t3_steps.yaml` | T3 active AND T3 has committed changes | Serialised T3 wrangling steps (see §4) |
| `report.<fmt>` | Always | Quarto-rendered report; includes T3 audit section when applicable (see §3) |
| `README.txt` | Always | Timestamp, project, persona, preset, tiers, hash values (all 3 hashes) |
| `FILTERS.txt` | Applied filters exist | Full filter trace — "No Trace No Export" protocol |

---

## 3. T3 audit section in report.qmd

The report includes a **"T3 Audit Trail"** section at the end **when**:
- `t3_sandbox_enabled: true` for the active persona, **AND**
- `t3_recipe_by_plot` contains at least one committed, active node

When the condition is not met, the section is absent (no empty placeholder).

### 3.1 Section contents

```
## T3 Audit Trail

For each plot that has T3 modifications:
  ### <plot_id>
  | Step | Action | Columns | Justification |
  |------|--------|---------|---------------|
  | 1    | filter_range | [year] min=2023 | "Focus on recent samples only" |
  ...
```

- Justifications come from the `reason` / `comment` field the user filled in the
  audit stack UI.
- Deactivated nodes are **excluded** (consistent with existing behaviour — deactivated
  = user chose not to commit that step).
- The same section appears in **Active group** and **Active plot** exports, scoped accordingly.

---

## 4. T3 recipe serialisation into recipes/

`recipes/t3_steps.yaml` structure (one file, all plots):

```yaml
# T3 recipe steps — user-committed modifications
# Generated: YYYYMMDD_HHMMSS
export_scope: global   # or: single_plot / <plot_id>
t3_steps:
  <plot_id>:
    - action: filter_range
      columns: [year]
      min: 2023
      max: 2025
      reason: "Focus on recent samples only"
      committed_at: "2026-05-04T14:32:00"
```

For **Active group** export: only steps for plots in that group; `export_scope: <group_id>`.  
For **Active plot** export: only the steps for that single plot's lineage; `export_scope: <plot_id>`.

---

## 5. Scoped export — Active group and Active plot

Both scoped modes use lineage backtrace: for each plot in scope, walk
`target_dataset → ingredients → data_schemas` to find every dataset and recipe
file that feeds it. The union of all lineage sets becomes the export contents.

| What is scoped | Active group | Active plot |
|---|---|---|
| `plots/` | All plots in the active group | Only the active plot |
| `data/` | Union of all upstream datasets for each plot in the group | Only datasets in the active plot's lineage |
| `recipes/` | Union of all manifest files feeding each plot in the group | Only the manifest files that feed the active plot |
| `recipes/t3_steps.yaml` | T3 steps for all plots in the group | T3 steps for the active plot only |
| `report.<fmt>` | Full report scoped to the group; T3 audit section per plot | Report for one plot; T3 audit section for that plot |

**Lineage backtrace algorithm:**  
`plot_id → spec.target_dataset → assembly_manifests[target].ingredients → data_schemas[*]`  
Recursive if an ingredient is itself an assembly. Already implemented in
`manifest_navigator.py` / `_build_sibling_map`.

---

## 6. Persona gate summary

| `export_enabled` | UI |
|---|---|---|
| ✓ | — | Export panel visible; no toggle; always Global mode |
| ✓ | ✓ | Export panel visible; 3-way toggle shown (Global / Active group / Active plot) |
| — | ✓ | Export panel hidden (no `EXP_BNDL` → no panel) |
| — | — | Export panel hidden |

---

## 7. Deferred / out of scope for now

- Per-plot height/width control before bundling (EXPORT-4)
- TubeMap SVG embed in report (EXPORT-TUBEMAP)
- Selective per-tier checkboxes (EXPORT-2) — explicitly NOT implemented; content is
  auto-determined by T3 state
- Configurable export content per persona — deferred pending funding / new use cases;
  this spec defines the current fixed content policy

---

## 8. Implementation pointers

| Component | Location | What changes |
|---|---|---|
| Export UI | `app/handlers/export_handlers.py` → `system_tools_ui()` | Remove `export_audit_report_ui` call; add scope toggle |
| Audit report UI | `app/handlers/export_handlers.py` → `export_audit_report_ui()` | **Delete** — replaced by auto-inclusion logic in bundle |
| Bundle builder | `app/handlers/export_handlers.py` → `export_bundle_download()` | Add T3 audit section to report.qmd; add t3_steps.yaml; 3-way scope logic (global / group / plot) |
| Single graph export | `app/handlers/single_graph_export_handlers.py` | Merge into bundle builder via scope flag — same download handler, scope parameter drives content |
| Persona flags | No change needed | `export_enabled` already exist |
