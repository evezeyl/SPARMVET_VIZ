## Step Chart

> 📊 Evolution · 🔢 1 Numeric, 1 Categorical · 📈 Simple · ⚙️ geom_step · 🎯 trend · 📏 any

### Suitability
Ideal for data that changes abruptly at discrete time points rather than continuously. Clinical breakpoints, regulatory threshold changes, and policy decisions all change in steps — the step chart makes these discontinuities explicit.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| drug_class | Categorical | Antibiotic drug class |
| year | Integer | Year of revision |
| breakpoint_change | Numeric | Breakpoint value at that time |

### Interpretation
Horizontal segments show periods of no change. Vertical jumps show the exact moment and magnitude of a revision. Downward steps = tightened breakpoints (more conservative). Use `geom_step` (not `geom_line`) to avoid linear interpolation.

### R Graph Gallery
[Step Chart](https://r-graph-gallery.com/line-chart-several-groups-ggplot2.html)
