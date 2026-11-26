## Line Chart (Simple)

> 📊 Evolution · 🔢 1 Year, 1 Numeric · 📈 Simple · ⚙️ geom_line · 🎯 trend · 📏 medium+

### Suitability
Use when you have a single numeric variable measured over time and want to reveal a trend or trajectory. Ideal for longitudinal AMR resistance rates, annual incidence, or cumulative counts at one aggregation level.

### Data Schema (Tier 1)
- `year`: integer year (or any ordinal time axis)
- `mean_resistance`: numeric — the value tracked over time
- `n_isolates`: integer — sample count per time point (for reference, not mapped)

### Transformation Logic (Tier 2)
- Data should be pre-aggregated (one row per time point).
- If raw isolate data: apply mean/count aggregation in tier2 before rendering.

### Interpretations
- A rising slope indicates increasing resistance over time — a key surveillance signal.
- Flat or declining lines after an intervention suggest treatment policy effectiveness.

### Inspiration & Resources
- [R Graph Gallery — Line chart](https://r-graph-gallery.com/line-plot.html)
