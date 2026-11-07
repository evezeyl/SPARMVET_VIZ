## Dumbbell Chart

> 📊 Comparison · 🔢 1 Numeric, 2 Categorical · 📈 Intermediate · ⚙️ geom_segment · 🎯 change · 📏 any

### Suitability
Shows change between two states (e.g. two time points) for multiple categories. The dumbbell shape (line + two dots) emphasises the direction and magnitude of change per group. More compact than two grouped bars.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism (y-axis) |
| year_label | Categorical | Time point label (determines dot colour) |
| resistance_rate | Numeric | Rate at each time point |

### Interpretation
The length of each "dumbbell" is the change between the two time points. Longer = bigger change. Consistent rightward shift = universal increase. Uses `group=species` to connect the two points per species with a grey line.

### R Graph Gallery
[Dumbbell Chart](https://r-graph-gallery.com/lollipop-plot.html)
