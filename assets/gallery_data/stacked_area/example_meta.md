## Stacked Area Chart

> 📊 Evolution · 🔢 1 Numeric, 2 Categorical · 📈 Intermediate · ⚙️ geom_area · 🎯 proportion · 📏 medium+

### Suitability
Shows how the total and composition of a numeric value evolves over time. Ideal for surveillance data where both overall trends and species/group contributions matter simultaneously.

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| species | Categorical | Organism contributing to count |
| year | Integer | Time point |
| count | Numeric | Isolate count or value |

### Interpretation
The top of the stacked area shows the total. Each colour band height shows that group's contribution at each time point. Growing total with stable proportions = uniform increase. Changing proportions = composition shift.

### R Graph Gallery
[Stacked Area](https://r-graph-gallery.com/stacked-area-graph.html)
