## Violin + Boxplot Overlay

> 📊 Distribution · 🔢 1 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ geom_violin · 🎯 distribution · 📏 medium+

### Suitability
Combines the density shape of a violin with the quartile summary of a boxplot. Best of both worlds: see the full distribution shape AND the median/IQR in one chart.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism or group |
| mic_value | Numeric (continuous) | MIC or measurement value |

### Interpretation
The violin width represents data density at each value. The inner boxplot shows median (middle line), IQR (box), and whiskers (1.5×IQR). Bimodal distributions appear as double-waisted violins.

### R Graph Gallery
[Violin + Boxplot](https://r-graph-gallery.com/violin_and_boxplot_ggplot2.html)
