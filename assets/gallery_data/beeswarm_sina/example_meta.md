## Beeswarm / Sina Plot

> 📊 Distribution · 🔢 1 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ geom_sina · 🎯 distribution · 📏 individual points

### Suitability
Shows individual data points distributed within a category using a jittered-violin hybrid. Better than boxplot alone when sample size is small to medium and individual values matter.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism or group |
| mic_value | Numeric (continuous) | MIC or measurement |

### Interpretation
Each dot is one observation. The spread width reflects density — denser regions widen. Useful for comparing distributions across species/groups while maintaining individual visibility.

### R Graph Gallery
[Beeswarm / Violin](https://r-graph-gallery.com/violin_and_boxplot_ggplot2.html)
