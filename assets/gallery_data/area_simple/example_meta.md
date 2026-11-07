## Area Chart

> 📊 Evolution · 🔢 1 Year, 1 Numeric · 📈 Simple · ⚙️ geom_area · 🎯 trend · 📏 medium+

### Suitability
Emphasises the cumulative magnitude of a metric over time rather than just its direction. More visually impactful than a line when the area under the curve carries meaning (e.g. total resistance burden, cumulative cases).

### Data Schema (Tier 1)
- `year`: integer year
- `resistance_pct`: numeric — the quantity whose area is filled

### Transformation Logic (Tier 2)
- One row per time point. Pre-aggregate if starting from raw isolate data.

### Interpretations
- Growing filled area = accumulating resistance burden.
- Avoid stacked areas when values are not additive parts of a whole — use line_grouped instead.

### Inspiration & Resources
- [R Graph Gallery — Area chart](https://r-graph-gallery.com/area-chart.html)
