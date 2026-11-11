## Home — Quick Reference

**Home** is the main analysis theater. Data analysis recipe-defined `analysis_groups` become tabs; each group's plots appear as sub-tabs.

### Plot to show / Data to show (header strip)
Two independent choices — one for the plots, one for the data preview table below them.

| Plot to show | What the plots render |
|---|---|
| **Result** | T2 result produced by the data analysis recipe (T2 = T1 if no processing steps are defined). Always the recipe's plot: preview filters do not change it |
| **My view** | Result plus your preview filters and the steps you sent to audit |
| **Compare** | Side by side: Result (left) vs My view (right) — only when comparison is enabled |

| Data to show | What the data preview table shows |
|---|---|
| **Raw** | T1 — as assembled, no processing (preview filters change this table) |
| **Result** | T2 — with data analysis recipe processing applied (preview filters change this table) |
| **My view** | Result plus your preview filters and the steps you sent to audit |

Plots never show Raw (T1) directly — Raw is for comparing against Result in the table only. Raw and Result are never changed by anything you do in Filters: the data files stay as they are.

### Filters (left sidebar)
**Raw and Result are for looking at the data; My view is where you change what the plot shows.**

- On **Raw** and **Result**, a filter changes the **table only**. Use it to check "what is this data?". It does not change any plot, and it is never saved or exported. A badge says "N preview filter(s) on, not saved".
- On **My view**, the same filters also change the **plot** (still a preview: not saved, not exported). In **Compare**, the left plot is always the Result as the recipe defines it and the right plot is My view, so you see what your filters did.
- Only **➜ Send to Audit** (with a reason, My view only) makes a step permanent: it is applied to the exported plot and data and recorded in the audit trail.

Filters are one list for the whole analysis: they apply to every plot and table whose data has the filtered column. A dataset without that column ignores the filter.

Click **+ Add** to stage a filter row, then **Apply** to show it. The 🗑 icon removes a row and its effect at once. **Reset** clears all rows. Send to Audit is described above.

Operators: **= equals**, **≠ not equal**, **> greater than**, **≥ greater or equal**, **< less than**, **≤ less or equal**, **↔ between** (numbers); **∈ any of**, **∉ none of** (categories). Choosing one value shows as "column = value"; several values show as "any of".

If a filter names a column the current view does not have (Raw is wide, Result may be long), it is skipped for that view.

### Data Preview
Shows up to the first 100 rows of the active plot's dataset at the selected "Data to show" tier. Toggle **All rows** to remove the cap. The column selector above the table hides columns from the preview only (view-only on Raw/Result); on My view, with the audit sandbox enabled, deselecting a column stages it to be permanently dropped via the audit trail.

### Export
Set a bundle label, pick a **Scope** (Global / Active group / Active plot), a **Quality** preset (Web or Publication ≥600 DPI), a **Plot format** (PNG / SVG / PDF), a **Report format** (HTML / PDF / DOCX), and the plot size in inches, then click **Export Bundle**. The bundle contains the plots, the underlying data, the data analysis recipe YAML, and a report with your audit trail. Only filters sent to audit are exported — exploration-only filters never are.

### Sessions
**Export Active Session (.zip)** downloads your current audit steps and filter state for archiving. Each saved session is listed with **Restore** (reload it) and **Delete Session**.
