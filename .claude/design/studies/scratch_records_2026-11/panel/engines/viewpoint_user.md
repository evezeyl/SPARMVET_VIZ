Novice user / Teacher viewpoint. Read: agent_principles, decision_compliance, scout_what_exists, r_backend.md, demo_abromics.yaml, rules section 10 (rules_data_analysis_recipe_structure.md:218-263), developer_workflow.md (grep only: BLUEPRINT builds the recipes, HOME runs them, :14-26, :181).

RECOMMENDATION (mine, not a decision). Do not build a data-side R/dplyr engine. For plots, if Eve plans R, choose a per-plot override with a default at the top, and accept only the whole-recipe default plus a per-plot override. Per-tier and per-step switching is not needed for the use cases. Ship nothing silently falling back. Reason: one picture ("this plot is drawn by R"), one sentence, and it matches the plot_defaults model.

1. WHAT THEY SEE
Example text:
```
data_engine: python-polars
plot_engine: python-plotnine        # default for every plot
...
plots:
  tree_by_source:
    plot_engine: r-ggplot2          # only this plot
    spec: { target_dataset: tree_table, layers: [{name: ggplot2_geom_tree}] }
  demo_st_by_source:
    spec: { layers: [{name: plotnine_geom_bar}] }
```
A writer reads this correctly at first sight if the key sits next to the plot label, above spec. Today a plot engine key inside a plot is refused as unknown (scout: viz_factory.py:218-225). Two prefixes help: the prefix tells which engine owns the name, same as `polars_` (D-0036, D-0091). Risk: a writer gives plot_engine r-ggplot2 but keeps a `plotnine_` layer. The checker must refuse that mismatch at load, with the plot named.
(A) knows ggplot2 and expects the same names; two families will feel like a translation table. (B) must not need to know any of it: only a label such as "drawn by R" on the plot. (C) see 5.

2. TELL AT THE MOMENT IT MATTERS
- Slow plot: "This plot is drawn by R (ggplot2). It starts R, so it takes a few seconds longer than the other plots."
- R missing: "Plot 'tree_by_source' needs R (ggplot2) and the package ggtree. This deployment has no R. The plot was not drawn, and it was not replaced by another engine. Suggestion: ask the person who installed the app to add R and ggtree. Suggestion: ask the recipe author for a version of the recipe that uses plotnine. Suggestion: the other plots of this recipe are not affected."
- Package missing: same, naming the package.
- Look: show a small caption "R / ggplot2 4.x" on the plot; fonts and sizes can differ from neighbours. Say so once in the recipe description.
- Export: one line per picture: engine, engine version, package versions. Today the export has no engine field (tasks.md:365 open, per scout).

3. FIT WITH WHAT (A) KNOWS
plot_defaults is "default for all plots, a plot may override" (rules :220, :249, :255). A per-plot engine fits that. A surprise: palette and theme in plot_defaults are plotnine names; an R plot would ignore or misread them. The recipe must say whether plot_defaults apply to an R plot. Per-tier or per-step overrides have no model today (the five-tier cascade is for style, not engines) and would surprise. The use cases (ggtree, maps, alluvial) are all one picture from one table: per plot is enough.

4. DPLYR
A dplyr writer expects the same logic as `polars_` actions, but gets differences: NA vs null, row order after joins (demo_abromics uses maintain_order, :52), type names (Int64 vs integer, factor vs String; the year cast at :58-63 is exactly this trap). Real need: low. Clearer: "prepare the table in your own R, give it as a dataset". But that leaves the data step outside the recipe, so the audit does not cover it. State this plainly. Mixing Polars for part and dplyr for the rest in one table makes the order and null rules unknowable for (B). I would not offer it.

5. (C) INSTALLER
Before installing: R version, packages (ggplot2, arrow, plus ggtree, sf, ggalluvial as used), image size, and whether the deployment is offline (air-gap, ADR-071). The Dockerfile has no R today. At start the app should list: "Plot engines available: python-plotnine yes; r-ggplot2 no (R not found)", plus each package. Suggestion: show it on a status line in HOME, not only in logs.

6. NEVER SILENT
- Never draw with plotnine when R was asked.
- Never change engine without a visible line in the export.
- Never ignore plot_defaults keys on an R plot without saying so (the scout already found keys accepted but read by no code: default_font_family, legend_position).
- Never run R code from a recipe without telling the user (option C is arbitrary code).
- Never drop NA differently between engines unannounced.

7. QUESTIONS FOR ELIGE EVE (each default is a suggestion, not a decision)
1. Is the aim to run R-written ggplot2 (the author writes R) or to get R-only geoms (ggtree, alluvial)? Options: author-in-R / R-only geoms / both. Default: R-only geoms.
2. Level of override: whole recipe only / plus per plot / plus per tier. Default: plus per plot.
3. Does R draw from the same plot spec (translated) or from an R snippet? Options: translated / snippet / both. Default: translated for a small set of plots.
4. If R is missing: stop that plot with a message (default) or the whole recipe.
5. Data side: dplyr in the recipe / prepare outside and give as a dataset. Default: outside.
6. Do plot_defaults (theme, palette) apply to R plots? Default: no, R plots take their own, stated in the message.
7. Should recipes that use R be marked in the recipe list so (B) sees it before running? Default: yes.

NOT CHECKED: HOME screens and message texts as they appear today; how a plot label is shown; whether the checker could reject the prefix/engine mismatch cheaply; real R render time and font differences; offline install of R packages; developer_workflow.md beyond a grep; the wording of D-0036/D-0091 in the ledger itself.
