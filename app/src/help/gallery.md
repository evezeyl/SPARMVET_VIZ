## Gallery — Quick Reference

**Gallery** is a curated browser of visualization examples — pre-built plot templates you can adapt to your data.

### Browsing
Use the **Family**, **Data Pattern**, **Difficulty**, **Primary Geom**, **What it Shows**, and **Sample Size** taxonomy filter panels (checkbox groups, with a "Select all" toggle each) to narrow the choices in the **Select an Example** dropdown.

### Example View
Once an example is selected, the top pane shows three tabs:
- **Plot Preview** — the rendered example plot
- **Data Sample** — the example's sample data
- **YAML Example** — the raw data analysis recipe fragment, to copy by hand

The bottom pane ("Visual Cookbook: Guidance") shows the example's educational metadata.

### Using an example elsewhere
Gallery has no in-app handoff into any other space — it's a pure static reference browser (ADR-093). To use an example as a starting point in Blueprint or anywhere else, copy the YAML from the **YAML Example** tab by hand, same as any other file-based handoff in this app.

### Difficulty guide
| Level | Meaning |
|---|---|
| Simple | Single geom, direct mapping, no wrangling |
| Intermediate | Multiple geoms or position adjustments; may need pre-aggregation |
| Advanced | Non-trivial wrangling, derived columns, or specialised geoms |
