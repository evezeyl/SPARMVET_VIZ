## 2D Bin Density

> 📊 Correlation · 🔢 2 Numeric · 📈 Intermediate · ⚙️ geom_bin_2d · 🎯 relationship · 📏 large

### Suitability
Visualises the joint distribution of two numeric variables using rectangular bins coloured by count. Handles overplotting better than raw scatter for large datasets. Reveals clustering, diagonal correlation patterns, and outlier concentrations.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| log_mic_drug_a | Numeric | log2 MIC for Drug A |
| log_mic_drug_b | Numeric | log2 MIC for Drug B |

### Interpretation
Dark bins = many isolates with that combination of MIC values. A diagonal pattern indicates cross-resistance (isolates resistant to one drug tend to be resistant to the other). Spread bins = independent resistance mechanisms.

### R Graph Gallery
[2D Density](https://r-graph-gallery.com/2d-density-chart.html)
