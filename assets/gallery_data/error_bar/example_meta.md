## Error Bar / Point Range

> 📊 Comparison · 🔢 1 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ geom_pointrange · 🎯 uncertainty · 📏 any

### Suitability
Shows estimated means with uncertainty bands (confidence intervals or SD). Ideal for summarised data where individual values are not available — communicates both the central estimate and its precision.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism group |
| mean_mic | Numeric | Point estimate (e.g. mean log2 MIC) |
| ci_low | Numeric | Lower confidence bound |
| ci_high | Numeric | Upper confidence bound |

### Interpretation
Longer bars = more uncertainty (wider CI). Overlapping bars suggest groups may not differ significantly. Requires pre-computed summary statistics — use a T3 `summarize` step if raw data is available.

### R Graph Gallery
[Error Bar](https://r-graph-gallery.com/4-barplot-with-error-bar.html)
