## Home — Quick Reference

**Home** is the main analysis theater. Data analysis recipe-defined `analysis_groups` become tabs; each group's plots appear as sub-tabs.

### The header strip
Up to three rows; the first only when the audit is switched on in your setup.

| Choice | What it does |
|---|---|
| **Mode: Exploration** | Look at the data. One plot per plot tab: the **Result**, drawn from the plot's own table. Filters change the table you view and never the plot. Nothing here is saved or exported. |
| **Mode: Audit** | Create audit steps (filters and column drops with a reason). The plot becomes the **audited plot**: the Result plus your audited steps. A **Compare** switch shows the original plot and the audited plot side by side. |

| Table to view | What the data preview table shows |
|---|---|
| **Source** | One source table as read from its file, before any step of the recipe. A second list names the source tables that feed the open plot (one table: the list still shows it) |
| **T1** | The plot's table after the tier-1 steps of the recipe |
| **T2** | The plot's table after the tier-2 steps (T2 = T1 if the recipe has none) |
| **T3** | The table the plot is drawn from: T2 plus the plot's own tier-3 steps of the recipe (T3 = T2 if it has none). In Audit mode, T3 also carries your audited steps |

The badge next to the table says which table it is and when two tables are the same. In Audit mode, audit steps apply to the plot's table (T3) for now; T1, T2 and Source stay the original tables.

### Filters (left sidebar)
**A filter is built on the table you are viewing, and it is cleared when that table changes.**

- In **Exploration**, a filter changes the **table only**. Use it to check "what is this data?". It does not change any plot, and it is never saved or exported. A badge says "N preview filter(s) on, not saved".
- When you change what you view (the table to view, the source table, the plot tab, the mode or the recipe), the staged and applied filters are removed and a notice says so. Nothing is carried over silently.
- In **Audit** mode the form builds audit steps, not previews: there is no Apply. **➜ Send to Audit** (with a reason) is offered while T3 is viewed; it makes a step permanent: it is applied to the audited plot and to the exported plot and data and recorded in the audit trail. On another table the panel says: "To create an audit step, view T3."

Operators: **= equals**, **≠ not equal**, **> greater than**, **≥ greater or equal**, **< less than**, **≤ less or equal**, **↔ between** (numbers); **∈ any of**, **∉ none of** (categories). Choosing one value shows as "column = value"; several values show as "any of".

A column of **whole numbers** (an integer type) takes whole numbers only, for every operator: a decimal such as 12.5 is refused with a line under the box and nothing is added. A column of decimal numbers takes decimals.

### The seed line and Reshuffle
A plot with a random layer (for example jitter) shows a line with its plot: the seed and where it comes from, for example "seed 0, written in the recipe". The same data and recipe then give the same picture everywhere. In **Audit** mode, a plot whose seed is written nowhere also has **Reshuffle**: it draws another arrangement and pins it as an audit step; **Remove the pinned seed** goes back. A seed written in the recipe is kept, so those plots have no Reshuffle.

### Info and Alerts (left sidebar)
**Info** shows what the recipe says about itself. **Alerts** lists the notices of this session (for example that a recipe was loaded or that filters were removed).

### Data Preview
Shows up to the first 100 rows of the table you chose to view for the active plot. Toggle **All rows** to remove the cap. The column selector above the table hides columns from the preview only; in Audit mode on T3, deselecting a column stages it to be permanently dropped via the audit trail.

### Export
Set a bundle label, pick a **Quality** preset (Web or Publication ≥600 DPI), a **Plot format** (PNG / SVG / PDF), a **Report format** (HTML / PDF / DOCX), and the plot size in inches, then click **Export Bundle**. Every export holds all plots of the loaded recipe. The bundle contains the plots, the underlying data, the data analysis recipe YAML, and a report with your audit trail. Only filters sent to audit are exported — exploration-only filters never are.

**Import a bundle** (above the export fields) reads a reproducibility bundle exported earlier and checks it against this machine; it writes a new recipe and session and never changes the app that is open. Reload the page afterwards to see the new recipe in the selector.

### Sessions
**Export Active Session (.zip)** downloads the files of the active session: the record of the recipe and data it belongs to, and your saved audit steps. Exploration filters are never saved. Each saved session is listed with **Restore** (reload it) and **Delete Session**.
