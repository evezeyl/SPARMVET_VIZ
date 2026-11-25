## Connected Scatter Plot

> 📊 Correlation · 🔢 2 Numeric · 📈 Intermediate · ⚙️ geom_path · 🎯 trend · 📏 any

### Suitability
Connects scatter points with lines ordered by a third implicit variable (usually time). Reveals how the relationship between two variables evolves — ideal for showing consumption-resistance feedback loops.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| drug_class | Categorical | Antibiotic drug class |
| year | Integer | Year (determines path order) |
| resistance_rate | Numeric | Resistance rate (%) |
| consumption_ddd | Numeric | DDD/1000/day consumption |

### Interpretation
Each path traces a drug class through time. Moving right = increasing resistance. Moving up = increasing consumption. Loops indicate reversal patterns. Use `geom_path` (not `geom_line`) to ensure correct temporal ordering.

### R Graph Gallery
[Connected Scatter](https://r-graph-gallery.com/connected-scatterplot.html)
