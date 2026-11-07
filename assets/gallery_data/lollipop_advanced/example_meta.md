## Lollipop Chart

> 📊 Ranking · 🔢 1 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ geom_segment · 🎯 ranking · 📏 any

### Suitability
A cleaner alternative to Bar Charts, especially for many categories. Emphasizes the data points rather than the bars.

### Credits
Inspired by the R Graph Gallery (r-graph-gallery.com)

### Data Schema (Tier 1)
- **Format:** Assumes data is already summarized (Tier 2). Ensure columns `species` and `avg_growth` are present.
- **Headers:** id, species, avg_growth

### Transformation Logic (Tier 2)
- This recipe utilizes advanced layer stacking and coordinate manipulation.


### Inspiration & Resources
- [Inspired by R Graph Gallery](https://r-graph-gallery.com/lollipop-plot.html)

### Interpretations
- Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap) to derive scientific insights.
