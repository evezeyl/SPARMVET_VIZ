## Jitter Strip Plot

> 📊 Comparison · 🔢 1 Numeric, 1 Categorical · 📈 Simple · ⚙️ geom_jitter · 🎯 distribution · 📏 individual points

### Suitability
Show individual data points distributed across categories. Ideal for small to medium datasets (n < 500 per group) where you want to reveal the raw distribution rather than summary statistics. Pairs well with a boxplot overlay (see boxplot_simple).

### Data Schema (Tier 1)
- `id`: unique isolate identifier
- `species`: categorical grouping
- `resistance_pct`: numeric — one value per isolate

### Transformation Logic (Tier 2)
- No transformation needed — plot individual rows.
- For large n (>500/group), consider switching to violin_simple or density_simple.

### Interpretations
- Dense clusters reveal the mode; isolated points reveal outliers.
- Width jitter is aesthetic — use `width=0.2` to prevent overlap without implying numeric spread on x.

### Inspiration & Resources
- [R Graph Gallery — Jitter](https://r-graph-gallery.com/jitter.html)
