## Proportion Bar Chart

> 📊 Part-to-Whole · 🔢 1 Numeric, 2 Categorical · 📈 Intermediate · ⚙️ geom_col · 🎯 proportion · 📏 any

### Suitability
Compare the proportional composition across groups when total counts vary and the relative share matters more than absolute values. Ideal for showing AMR class distribution profiles across species regardless of collection size.

### Data Schema (Tier 1)
- `species`: primary categorical axis
- `amr_class`: fill grouping variable
- `count`: raw counts — `position_fill` normalises to 100% automatically

### Transformation Logic (Tier 2)
- Same data structure as stacked_bar. `position_fill` handles normalisation in-plot.
- All bars become equal height; the y-axis shows 0–1 (or 0–100%).

### Interpretations
- Equal bar heights remove the "total burden" signal — only composition is visible.
- Use when asking "what fraction of each species's isolates are resistant to X?"
- Pair with stacked_bar to show both composition AND total count.

### Inspiration & Resources
- [R Graph Gallery — 100% stacked barplot](https://r-graph-gallery.com/stacked-barplot.html)
