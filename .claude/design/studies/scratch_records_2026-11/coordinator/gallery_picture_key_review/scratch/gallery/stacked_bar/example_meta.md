## Stacked Bar Chart

> 📊 Part-to-Whole · 🔢 1 Numeric, 2 Categorical · 📈 Intermediate · ⚙️ geom_col · 🎯 proportion · 📏 any

### Suitability
Show absolute counts broken down by a second category. Useful for understanding both the total per primary category and how sub-categories contribute to it. Common for isolate counts by species broken down by AMR class.

### Data Schema (Tier 1)
- `species`: primary categorical axis
- `amr_class`: fill / stack grouping variable
- `count`: numeric count per (species, amr_class) combination

### Transformation Logic (Tier 2)
- One row per (species, amr_class) combination. Use group-count from isolate data.
- Ordering species by total count (reorder) makes the chart easier to read.

### Interpretations
- Total bar height = overall isolate burden per species.
- Segment proportion = relative contribution of each AMR class.
- Note: comparing segment sizes across bars is difficult — use proportion_bar for composition comparisons.

### Inspiration & Resources
- [R Graph Gallery — Stacked barplot](https://r-graph-gallery.com/stacked-barplot.html)
