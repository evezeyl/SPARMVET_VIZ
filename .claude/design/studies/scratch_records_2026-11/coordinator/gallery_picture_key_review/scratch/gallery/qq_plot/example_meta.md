## Q-Q Plot (Quantile-Quantile)

> 📊 Distribution · 🔢 1 Numeric, 1 Categorical · 📈 Advanced · ⚙️ geom_qq · 🎯 normality · 📏 medium+

### Suitability
Tests normality of a distribution. Points falling near the diagonal reference line indicate the data is approximately normally distributed. Essential for validating statistical assumptions before parametric tests.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism or group |
| mic_value | Numeric | Raw MIC value |
| log_mic | Numeric (derived) | log2(mic_value) — computed in T3 |

### Interpretation
If points follow the line closely: data is approximately normal. S-curves indicate skewness. Points diverging at both ends indicate heavy tails. log-transformation is typically applied to MIC data before checking normality.

### R Graph Gallery
[QQ Plot](https://r-graph-gallery.com/qqplot-with-r-and-ggplot2.html)
