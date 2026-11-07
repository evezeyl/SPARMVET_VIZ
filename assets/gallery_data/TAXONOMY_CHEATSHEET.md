# Gallery Taxonomy Cheatsheet

Icons used consistently across all recipe data analysis recipes, recipe_meta.md tag strips, and the Gallery sidebar filter panels.

---

## Icon → Axis mapping

| Icon | Axis | Sidebar label | Where used |
|------|------|--------------|-----------|
| 📊 | **Family (Purpose)** | `📊 Family (Purpose)` | data analysis recipe `info.family`, meta `> 📊 …`, sidebar |
| 🔢 | **Data Pattern** | `🔢 Data Pattern` | data analysis recipe `info.pattern`, meta `> … 🔢 …`, sidebar |
| 📈 | **Difficulty** | `📈 Difficulty` | data analysis recipe `info.difficulty`, meta `> … 📈 …`, sidebar |
| ⚙️ | **Primary Geom** | `⚙️ Primary Geom` | data analysis recipe `info.geom`, meta `> … ⚙️ …`, sidebar |
| 🎯 | **What it Shows** | `🎯 What it Shows` | data analysis recipe `info.show`, meta `> … 🎯 …`, sidebar |
| 📏 | **Sample Size** | `📏 Sample Size` | data analysis recipe `info.sample_size`, meta `> … 📏 …`, sidebar |

---

## Allowed values per axis

### 📊 Family (Purpose)
| Value | Meaning |
|-------|---------|
| `Comparison` | Comparing values across discrete groups |
| `Correlation` | Relationship between two or more numeric variables |
| `Distribution` | Shape, spread, or density of a single numeric variable |
| `Evolution` | Change over time (continuous or ordered x) |
| `Part-to-Whole` | Composition / proportions that sum to a total |
| `Ranking` | Ordered comparison to highlight relative position |

### 🔢 Data Pattern
| Value | Meaning |
|-------|---------|
| `1 Numeric` | One numeric column, no grouping |
| `1 Numeric, 1 Categorical` | One numeric + one grouping variable |
| `1 Numeric, 2 Categorical` | One numeric + two grouping variables |
| `1 Numeric, 2 Categorical (Faceted)` | As above, faceted into panels |
| `2 Numeric` | Two numeric columns (x/y) |
| `2 Numeric, 1 Categorical` | Two numeric + one grouping variable |
| `2 Numeric, 1 Categorical (Faceted)` | As above, faceted into panels |
| `3 Numeric (Matrix)` | Three numeric columns forming a matrix (e.g. var1, var2, value) |
| `1 Year, 1 Numeric` | Time series: one year/date column + one value |
| `1 Year, 1 Numeric, 1 Categorical` | Time series with group colouring |

### 📈 Difficulty
| Value | Meaning |
|-------|---------|
| `Simple` | Single geom, direct mapping, no wrangling |
| `Intermediate` | Multiple geoms or position adjustments; may need pre-aggregation |
| `Advanced` | Non-trivial wrangling, derived columns, or specialised geoms |

### ⚙️ Primary Geom
The first `geom_*` or `stat_*` layer in the recipe. Use the exact plotnine function name (lowercase, underscore):

`geom_area` · `geom_bar` · `geom_bin_2d` · `geom_boxplot` · `geom_col` · `geom_density`
`geom_freqpoly` · `geom_histogram` · `geom_jitter` · `geom_line` · `geom_path` · `geom_point`
`geom_pointrange` · `geom_qq` · `geom_segment` · `geom_sina` · `geom_step` · `geom_tile`
`geom_violin` · `stat_ecdf`

### 🎯 What it Shows
| Value | Use when the chart primarily communicates… |
|-------|------------------------------------------|
| `change` | A before/after or discrete shift between two states |
| `distribution` | The shape, spread, or density of values within a group |
| `frequency` | Raw counts or how often values occur in bins |
| `normality` | Whether data follows a normal/theoretical distribution |
| `proportion` | How parts contribute to a whole (shares that sum to 100%) |
| `ranking` | Relative order or size comparison across categories |
| `relationship` | How two numeric variables co-vary or correlate |
| `trend` | Directional change over a continuous axis (usually time) |
| `uncertainty` | Error, confidence intervals, or variability around an estimate |

### 📏 Sample Size
| Value | Guidance |
|-------|---------|
| `any` | Works on aggregated/summary data — n doesn't matter |
| `individual points` | Best when individual dots are visible and meaningful (n < ~200) |
| `medium+` | Needs enough observations to show shape (n ≥ ~50 recommended) |
| `large` | Designed for overplotting; benefits from n ≥ 500 |

---

## Tag strip format in recipe_meta.md

Every `recipe_meta.md` must include a blockquote tag strip on line 3 (after the `## Name` heading and a blank line):

```markdown
## Recipe Name

> 📊 Family · 🔢 Data Pattern · 📈 Difficulty · ⚙️ geom_name · 🎯 show_value · 📏 sample_size_value
```

Example:
```markdown
## Violin + Boxplot Overlay

> 📊 Distribution · 🔢 1 Numeric, 1 Categorical · 📈 Intermediate · ⚙️ geom_violin · 🎯 distribution · 📏 medium+
```

---

## Data analysis recipe info block format

```yaml
info:
  name: Recipe Name
  submission_date: 'YYYY-MM-DD'
  family: Distribution         # 📊
  pattern: 1 Numeric, 1 Categorical  # 🔢
  difficulty: Intermediate     # 📈
  geom: geom_violin            # ⚙️
  show: distribution           # 🎯
  sample_size: medium+         # 📏
```
