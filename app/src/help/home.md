## Home — Quick Reference

**Home** is the main analysis theater. Manifest-defined `analysis_groups` become tabs; each group's plots appear as sub-tabs.

### Tier Toggle
| Button | What you see |
|---|---|
| **T1 Raw** | Assembled anchor data — no transformations |
| **T2 Reference** | T1 + manifest-defined wrangling (read-only reference) |
| **T3 Wrangling** | Your personal adjustments — filtered, excluded, or dropped columns |
| **T3 Plot** | Same as T3 Wrangling with plot-level aesthetic changes |

### Filters (left sidebar)
Click **+ Add row** to stage a filter. Press **Apply** to commit. Filters affect all plots and the data preview. Reset clears uncommitted rows.

### Data Preview
Shows the first 100 rows of the active plot's dataset. Use the column selector to show/hide columns (preview only — does not affect plots).

### Export
Set a label, choose PNG/SVG, select scope (global / active group / active plot), then click **Export Bundle**. The bundle contains plots, data files, YAML recipes, and a Quarto report with your audit trail.

### Sessions
Save your current T3 recipe and filter state as a named session. Restore it later to continue from where you left off.
