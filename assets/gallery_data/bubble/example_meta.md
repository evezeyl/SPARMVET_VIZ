## Bubble Chart

> 📊 Correlation · 🔢 2 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ geom_point · 🎯 relationship · 📏 any

### Suitability
Encode three numeric variables simultaneously: position (x, y) and magnitude (bubble size). Use when you want to show the relationship between two continuous axes while also conveying a third quantity (e.g. sample size, % resistant, confidence).

### Data Schema (Tier 1)
- `species`: categorical — color grouping
- `sample_size`: numeric — x-axis (collection effort)
- `mean_resistance`: numeric — y-axis (outcome)
- `pct_resistant`: numeric — bubble size

### Transformation Logic (Tier 2)
- One row per group (here, per species). Requires pre-aggregation from isolate-level data.
- `scale_size(range=[4, 20])` controls bubble area; adjust to prevent overlap.

### Interpretations
- Position reveals correlation between x and y; size adds a third dimension.
- Bubble overlap is common — use alpha < 1 and consider log-scaling the x-axis for wide ranges.

### Inspiration & Resources
- [R Graph Gallery — Bubble chart](https://r-graph-gallery.com/bubble-chart.html)
