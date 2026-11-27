## Home — Quick Reference

**Home** is the main analysis theater. Data analysis recipe-defined `analysis_groups` become tabs; each group's plots appear as sub-tabs.

### The mode and the header strip
The **mode** control "Exploration | Audit" sits at the right of the recipe title, in a row of its own; it exists only when the audit is switched on in your setup. Below it the strip has up to two rows ("Table to view", and the list of source tables while Source is chosen).

| Choice | What it does |
|---|---|
| **Mode: Exploration** | Look at the data. One plot per plot tab: the **Result**, drawn from the plot's own table. Filters change the table you view and never the plot. Nothing here is saved or exported. |
| **Mode: Audit** | Create audit steps (filters and column drops with a reason). The plot becomes the **audited plot**: the Result plus your audited steps. The switch **Compare with the original** (above the plots) shows the original plot and the audited plot side by side. |

| Table to view | What the data preview table shows |
|---|---|
| **Source** | One source table as read from its file, before any step of the recipe. A second list names the source tables that feed the open plot (one table: the list still shows it) |
| **T1** | The table the open plot reads, after the tier-1 steps of the recipe |
| **T2** | The same table after the tier-2 steps (T2 = T1 if the recipe has none) |
| **T3** | The Result data, the table the plot is drawn from: T2 plus the plot's own tier-3 steps of the recipe (T3 = T2 if it has none). In Audit mode, T3 also carries your audited steps |

The badge next to the table says which table it is and when two tables are the same. In Audit mode a step can be written at any table of "Path of the data" or at the Result data (T3) of a plot; T1 and T2 show the audited table where a step changes it, and Source stays the file as read.

### Filters (left sidebar)
**A filter is built on the table you are viewing, and it is cleared when that table changes.**

- In **Exploration**, a filter changes the **table only**. Use it to check "what is this data?". It does not change any plot, and it is never saved or exported. A badge says "N preview filter(s) on, not saved".
- When you change what you view (the table to view, the source table, the plot tab, the mode or the recipe), the staged and applied filters are removed and a notice says so. Nothing is carried over silently.
- In **Audit** mode the form builds the condition of an audit step, not a preview: there is no Apply. In the bar above the table (**Create an audit step**) the button **Try** computes the step at the table you are viewing and at the places you chose in "Path of the data": for each place how many rows it removes, and what is built from it. Nothing is applied, saved or exported yet. You may tick **User verified** on a place (advice only), write the **reason** (required) and press **Add to audit pipeline**: the step is written at every place of the trial, it is applied to the audited plots and to the exported plots and data, and it is recorded in the audit trail. One step at a time.
- To drop columns in Audit mode, view the Result data (T3) of a plot, deselect the columns in the column chooser and choose **Drop columns** in the bar above the table and press **Try**; it is tried and added the same way.

Operators: **= equals**, **≠ not equal**, **> greater than**, **≥ greater or equal**, **< less than**, **≤ less or equal**, **↔ between** (numbers); **∈ any of**, **∉ none of** (categories). Choosing one value shows as "column = value"; several values show as "any of".

A column of **whole numbers** (an integer type) takes whole numbers only, for every operator: a decimal such as 12.5 is refused with a line under the box and nothing is added. A column of decimal numbers takes decimals.

The right panel (Pipeline Audit) lists the audit steps you added, each with where it was written, whether the place was marked "User verified", its reason and a bin that removes it (from every place it was written at). Exploration never writes audit steps. The right panel opens when you choose **Audit** mode and closes when you leave it; opened by hand in Exploration it is empty.

The side panels follow the window width. To change a panel's width, drag the grip on its edge (double-click it to go back to the default width). The width is kept in this browser, on this machine, as a share of the window; the centre always keeps at least half of the window.

### The seed line and Reshuffle
A plot with a random layer (for example jitter) shows a line with its plot: the seed and where it comes from, for example "seed 0, written in the recipe". The same data and recipe then give the same picture everywhere. In **Audit** mode, a plot whose seed is written nowhere also has **Reshuffle**: it draws another arrangement and pins it as an audit step; **Remove the pinned seed** goes back. A seed written in the recipe is kept, so those plots have no Reshuffle.

### Info and Alerts (left sidebar)
**Info** shows what the recipe says about itself. **Alerts** lists the notices of this session (for example that a recipe was loaded or that filters were removed).

### Data Preview
Shows up to the first 100 rows of the table you chose to view for the active plot. Toggle **All rows** to remove the cap. The column selector above the table hides columns from the preview only; in Audit mode on T3, deselecting a column is the start of a drop (choose **Drop columns** in the bar and press **Try**, then add it to the audit pipeline).

### Export
Set a bundle label, pick a **Quality** preset (Web or Publication ≥600 DPI), a **Plot format** (PNG / SVG / PDF), a **Report format** (HTML / PDF / DOCX), and the plot size in inches, then click **Export Bundle**. Every export holds all plots of the loaded recipe. The bundle contains the plots, the underlying data, the data analysis recipe YAML, and a report with your audit trail. Only filters sent to audit are exported — exploration-only filters never are.

**Import a bundle** (above the export fields) reads a reproducibility bundle exported earlier and checks it against this machine; it writes a new recipe and session and never changes the app that is open. Reload the page afterwards to see the new recipe in the selector.

### Sessions
**Export Active Session (.zip)** downloads the files of the active session: the record of the recipe and data it belongs to, and your saved audit steps. Exploration filters are never saved. Each saved session is listed with **Restore** (reload it) and **Delete Session**; Delete asks for a confirmation first ("Delete this session? It cannot be undone.") and Cancel changes nothing.
