## Home — Quick Reference

**Home** is the main analysis theater. Data analysis recipe-defined `analysis_groups` become tabs; each group's plots appear as sub-tabs.

### Plot to show / Data to show (header strip)
Two independent choices — one for the plots, one for the data preview table below them.

| Plot to show | What the plots render |
|---|---|
| **Result** | T2 result produced by the data analysis recipe (T2 = T1 if no processing steps are defined) |
| **My view** | T2 plus your filters/drops (exploration, and audited steps if sent to audit) |
| **Compare** | Side by side: Result (left) vs My view (right) — only when comparison is enabled |

| Data to show | What the data preview table shows |
|---|---|
| **Raw** | T1 — as assembled, no processing |
| **Result** | T2 — with data analysis recipe processing applied |
| **My view** | T2 plus your filters/drops |

Plots never show Raw (T1) directly — Raw is for comparing against Result in the table only. T1 and T2 are always pure references: nothing you do in Filters ever changes them.

### Filters (left sidebar)
Click **+ Add** to stage a filter row, then:
- **Apply** — applies the staged filters for exploration on **My view** only. Transient: not written to any audit log, not included in exports.
- **➜ Send to Audit** — writes the filters to the permanent audit trail with a reason. Included in every export. Only available when the app features enables the T3 audit sandbox.
- **Reset** — clears staged (unapplied) rows.

Filters and column drops only ever affect "My view" — Raw and Result are never touched.

### Data Preview
Shows up to the first 100 rows of the active plot's dataset at the selected "Data to show" tier. Toggle **All rows** to remove the cap. The column selector above the table hides columns from the preview only (view-only on Raw/Result); on My view, with the audit sandbox enabled, deselecting a column stages it to be permanently dropped via the audit trail.

### Export
Set a bundle label, pick a **Scope** (Global / Active group / Active plot), a **Quality** preset (Web or Publication ≥600 DPI), a **Plot format** (PNG / SVG / PDF), a **Report format** (HTML / PDF / DOCX), and the plot size in inches, then click **Export Bundle**. The bundle contains the plots, the underlying data, the data analysis recipe YAML, and a report with your audit trail. Only filters sent to audit are exported — exploration-only filters never are.

### Sessions
**Export Active Session (.zip)** downloads your current audit steps and filter state for archiving. Each saved session is listed with **Restore** (reload it) and **Delete Session**.
