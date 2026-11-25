## Frequency Polygon

> 📊 Distribution · 🔢 1 Numeric, 1 Categorical · 📈 Simple · ⚙️ geom_freqpoly · 🎯 frequency · 📏 medium+

### Suitability
A line-based alternative to histogram. Connects bin midpoints with lines instead of bars — ideal for overlaying multiple groups without the visual clutter of stacked/overlapping bars.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism or group |
| mic_value | Numeric | MIC or measurement value |

### Interpretation
Peaks indicate the most common values. Multiple overlapping lines allow direct comparison of distribution shape across groups. Choose `binwidth` to match the scale of the data (e.g., 0.5 for log2 MIC steps).

### R Graph Gallery
[Frequency Polygon](https://r-graph-gallery.com/frequency-polygon.html)
