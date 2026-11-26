## Scatter Plot with Smoother

> 📊 Correlation · 🔢 2 Numeric, 1 Categorical · 📈 Simple · ⚙️ geom_point · 🎯 relationship · 📏 individual points

### Suitability
Adds a linear model (or LOESS) trend line with confidence interval to a scatter plot. Reveals the direction, strength, and uncertainty of the relationship between two numeric variables across groups.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism or group |
| year | Numeric (integer) | Year of observation |
| resistance_rate | Numeric | Resistance rate (%) |

### Interpretation
Upward slope = increasing resistance over time. The shaded band is the 95% CI of the linear fit. Compare slopes across groups to see which species shows fastest trend change.

### R Graph Gallery
[Scatter with Smoother](https://r-graph-gallery.com/50-51-52-scatter-plot-with-ggplot2.html)
