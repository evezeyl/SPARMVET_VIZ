## Grouped Bar Chart

> 📊 Ranking · 🔢 1 Numeric, 2 Categorical · 📈 Intermediate · ⚙️ geom_col · 🎯 ranking · 📏 any

### Suitability
Compares a numeric value across combinations of two categorical variables. Best when you want to compare both between categories on the x-axis AND between sub-groups (fill) within each category.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism (x-axis) |
| drug_class | Categorical | Drug class (fill/groups) |
| resistance_rate | Numeric | Resistance rate (%) |

### Interpretation
Each cluster of bars represents one species. Within each cluster, bars show resistance to each drug class. Useful for spotting which drug-species combinations have highest resistance and comparing resistance profiles across organisms.

### R Graph Gallery
[Grouped Bar Chart](https://r-graph-gallery.com/grouped-barplot.html)
