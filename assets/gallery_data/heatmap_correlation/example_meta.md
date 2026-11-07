## Correlation Matrix (Heatmap)

> 📊 Correlation · 🔢 3 Numeric (Matrix) · 📈 Advanced · ⚙️ geom_tile · 🎯 relationship · 📏 any

### Suitability
Displays correlation intensity between variables. Essential for multi-dimensional data exploration.

### Credits
Inspired by the R Graph Gallery (r-graph-gallery.com)

### Data Schema (Tier 1)
- **Format:** Mandatory 'Long Format' (ADR-002). The matrix MUST be pivoted to 3 columns: `var1`, `var2`, and the numeric `correlation` value.
- **Headers:** id, var1, var2, correlation

### Transformation Logic (Tier 2)
- This recipe utilizes advanced layer stacking and coordinate manipulation.


### Inspiration & Resources
- [Inspired by R Graph Gallery](https://r-graph-gallery.com/199-correlation-matrix-with-ggally.html)

### Interpretations
- Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap) to derive scientific insights.
