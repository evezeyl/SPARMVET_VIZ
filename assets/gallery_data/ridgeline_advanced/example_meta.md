## Ridgeline Distribution

> 📊 Distribution · 🔢 1 Numeric, 1 Categorical · 📈 Advanced · ⚙️ geom_density · 🎯 distribution · 📏 medium+

### Suitability
Visualizes densities across multiple categories. Excellent for comparing distributions side-by-side using vertical faceting.

### Credits
Inspired by the R Graph Gallery (r-graph-gallery.com)

### Data Schema (Tier 1)
- **Format:** Requires 'Long Format' (ADR-002) where each observation is a row in the `growth_index` column, associated with a `species` label.
- **Headers:** id, growth_index, species

### Transformation Logic (Tier 2)
- This recipe utilizes advanced layer stacking and coordinate manipulation.


### Inspiration & Resources
- [Inspired by R Graph Gallery](https://r-graph-gallery.com/ridgeline-plot.html)

### Interpretations
- Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap) to derive scientific insights.
