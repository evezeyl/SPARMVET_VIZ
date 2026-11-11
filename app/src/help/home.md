## Home — Quick Reference

**Home** is the main analysis theater. Data analysis recipe-defined `analysis_groups` become tabs; each group's plots appear as sub-tabs.

### Plot to show / Data to show (header strip)
Two independent choices — one for the plots, one for the data preview table below them.

| Plot to show | What the plots render |
|---|---|
| **Result** | T2 result produced by the data analysis recipe (T2 = T1 if no processing steps are defined), plus any preview filters you apply |
| **My view** | Result plus your preview filters and the steps you sent to audit |
| **Compare** | Side by side: Result (left) vs My view (right) — only when comparison is enabled |

| Data to show | What the data preview table shows |
|---|---|
| **Raw** | T1 — as assembled, no processing (plus preview filters) |
| **Result** | T2 — with data analysis recipe processing applied (plus preview filters) |
| **My view** | Result plus your preview filters and the steps you sent to audit |

Plots never show Raw (T1) directly — Raw is for comparing against Result in the table only. Raw and Result are never changed by anything you do in Filters: the data files stay as they are.

### Filters (left sidebar)
Filters and column choices are a **preview**: they let you look at the data to understand it. They work on Raw, Result and My view, and they are **never written to the data and never exported**. A badge above the table or plot tells you when preview filters are on ("N preview filter(s) on, not saved").

Click **+ Add** to stage a filter row, then:
- **Apply** — shows the staged filters in the plots and the table (preview only).
- **➜ Send to Audit** — makes the step permanent, with a reason: it is applied to the exported plot and data and recorded in the audit trail. Only available on My view when the app features enables the audit sandbox.
- **Reset** — clears staged (unapplied) rows.

Operators: **= equals**, **≠ not equal**, **> greater than**, **≥ greater or equal**, **< less than**, **≤ less or equal**, **↔ between** (numbers); **∈ any of**, **∉ none of** (categories). Choosing one value shows as "column = value"; several values show as "any of".

If a filter names a column the current view does not have (Raw is wide, Result may be long), it is skipped for that view.

In Compare, the left plot (Result) never shows your preview filters, so you can see what they did.

### Data Preview
Shows up to the first 100 rows of the active plot's dataset at the selected "Data to show" tier. Toggle **All rows** to remove the cap. The column selector above the table hides columns from the preview only (view-only on Raw/Result); on My view, with the audit sandbox enabled, deselecting a column stages it to be permanently dropped via the audit trail.

### Export
Set a bundle label, pick a **Scope** (Global / Active group / Active plot), a **Quality** preset (Web or Publication ≥600 DPI), a **Plot format** (PNG / SVG / PDF), a **Report format** (HTML / PDF / DOCX), and the plot size in inches, then click **Export Bundle**. The bundle contains the plots, the underlying data, the data analysis recipe YAML, and a report with your audit trail. Only filters sent to audit are exported — exploration-only filters never are.

### Sessions
**Export Active Session (.zip)** downloads your current audit steps and filter state for archiving. Each saved session is listed with **Restore** (reload it) and **Delete Session**.
