## Line Chart (Grouped)

> 📊 Evolution · 🔢 1 Year, 1 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ geom_line · 🎯 trend · 📏 medium+

### Suitability
Compare resistance trends across multiple organisms or drug classes simultaneously. Reveals diverging or converging trajectories that species-level aggregation would obscure.

### Data Schema (Tier 1)
- `year`: integer year
- `species`: categorical — the grouping variable (one line per value)
- `mean_resistance`: numeric — resistance rate per species per year

### Transformation Logic (Tier 2)
- Requires one row per (year, species) combination — pivot or group-aggregate if starting from isolate-level data.

### Interpretations
- Parallel rising lines: system-wide pressure (e.g. broad antibiotic use).
- Species-specific jumps: may indicate clonal spread or local selective pressure.

### Inspiration & Resources
- [R Graph Gallery — Line chart with multiple groups](https://r-graph-gallery.com/line-plot.html)
