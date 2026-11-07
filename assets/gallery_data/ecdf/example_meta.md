## ECDF Plot

> 📊 Distribution · 🔢 1 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ stat_ecdf · 🎯 distribution · 📏 medium+

### Suitability
The Empirical Cumulative Distribution Function shows what fraction of values fall below any given threshold. Essential for comparing MIC distributions across species — allows reading off %S, %I, %R directly from breakpoints.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism or group |
| mic_value | Numeric (continuous) | MIC value |

### Interpretation
The step at each x value represents one observation. Curves shifted left = lower MICs (more susceptible). Read vertically at any MIC breakpoint to get cumulative % susceptible.

### R Graph Gallery
[ECDF](https://r-graph-gallery.com/ecdf.html)
