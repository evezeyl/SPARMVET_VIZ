# Gallery study: the USER viewpoint (panel-user, 2026-11-20 night; condensed by the coordinator from its report; read from files, the app was not run)

## Name, heading, recipe
- The dropdown shows the name ("Bar Simple"); the guidance pane opens with a heading ("Bar Chart"); the YAML tab shows `info.label` and `ui_label` (both "Bar Simple"). Nothing on screen says "name in the list" versus "title of the guidance": two titles for one thing reads as a mistake. The name appears twice in the recipe; the user does not know which to copy.
- "Simple"/"Advanced" in a name repeats the Difficulty tag. Names like "Point Simple" are the recipe maker's wording; a user looks for "scatter".
- The 13 differing headings: 8 or 9 read better than the name (bar_simple, boxplot_simple, density_simple, histogram_simple, lollipop_advanced, point_faceted, point_simple, violin_simple, tile_simple), 2 are synonyms by word order (boxplot_faceted, violin_faceted), 2 or 3 confuse (heatmap_correlation "Correlation Matrix (Heatmap)" while the data are long, not a matrix; ridgeline_advanced "Ridgeline Distribution": Distribution is also a Family value; tile_simple and heatmap_correlation are two heatmaps under two naming schemes). No heading reads worse than its name.

## Content defects seen in 6 examples (to verify by the scientist viewpoint)
- bar_simple: family Ranking but the text says counts/distribution; the plot counts rows (no y), the `value` column of the Data Schema is unused.
- heatmap_correlation: pattern "3 Numeric (Matrix)" but the data hold id, var1, var2, correlation (two label columns, one number).
- point_faceted: tag "2 Numeric, 1 Categorical (Faceted)" but `date` is typed String and the facets use two categoricals.
- tile_simple: family Correlation but "relationships between two categories".
- ridgeline_advanced: primary geom is geom_density; a user filtering on a ridgeline geom will not find it.
- Pasted text: the "Interpretations" sentence naming Ridgeline, Lollipop and Heatmap is in several examples where it is wrong; "Transformation Logic: This is a basic demonstration of geom_bar mapping" repeated; slang ("Gourmet", "Staple", "Multi-Course view") says nothing about when to use the plot.

## Filter categories
- "Family (Purpose)" readable; its overlap with "What it Shows" (Correlation/relationship, Distribution/distribution) is unexplained.
- "Data Pattern" is the filter that matters most for "which plot fits my data" and is not said to be so; "Faceted", "Matrix" need a plain line; unclear that it counts columns of MY data.
- "What it Shows": "change" means before/after two states (cheatsheet), read as "over time".
- "Sample Size": "medium+", "large" carry no numbers on screen (the cheatsheet has n < about 200, n >= 50, n >= 500).
- "Difficulty": of the recipe, not of the statistics; explained only in the help overlay.
- "Primary Geom": plotnine function names; useless to someone who does not know plotnine.
- Where to explain: one short line under each filter heading in the panel; the cheatsheet that holds the meanings is shown nowhere.

## Options for the 13 headings (name = ui_label decided; heading = a description, not redundant, not generated)
A. Keep both as they are: two titles, unexplained.
B. Keep the headings, change the 13 names to the better words: equal on screen; can drift apart silently later.
C. Keep the names, make the heading a real description ("Bar Chart: compare counts across categories"): fits her words best; 13 sentences to write.
D. Keep the names, add a small fixed line above the heading ("Example: Bar Simple") so the name is visible in the pane.
E. Nothing on screen, a check that warns the recipe maker: not recommended.
Preference: C, possibly with D.

## What would mislead
A stale list (silent); a picture with no proven link to the recipe (worst for a user who copies by hand); a tag consistent with the recipe's taxonomy and still untrue of the data (nobody checks the taxonomy against the data); pasted text; two name fields in the recipe; a failed example shown by folder name; dead links; advice never shown.
