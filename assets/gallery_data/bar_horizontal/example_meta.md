## Horizontal Bar Chart

> 📊 Ranking · 🔢 1 Numeric, 1 Categorical · 📈 Simple · ⚙️ geom_col · 🎯 ranking · 📏 any

### Suitability
Rank categories by a numeric value when category labels are long or numerous. The horizontal layout prevents x-axis label overlap and makes left-to-right reading natural. Preferred over vertical bars for named rankings.

### Data Schema (Tier 1)
- `amr_class`: categorical — the ranked items
- `mean_resistance`: numeric — the value determining rank

### Transformation Logic (Tier 2)
- Pre-sort data by value before plotting, or use `reorder(amr_class, mean_resistance)` in the mapping for automatic ordering.

### Interpretations
- Longest bar = highest resistance — immediate visual ranking.
- Consider adding a threshold line (geom_vline) at a clinically relevant cut-off.

### Inspiration & Resources
- [R Graph Gallery — Horizontal barplot](https://r-graph-gallery.com/barplot.html)
