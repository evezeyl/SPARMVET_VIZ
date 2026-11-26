# Verify results (2026-11-14, branch feat/recipe-format-1). Scripts: tmpAI/panel/viz/verify/q1.py, q2.py

## 1. Full catalogues at HOME/Blueprint (RUN, q1.py)
Ran check_recipe_file with HOME catalogues ({actions, components}, as validator.py:111-112) and FULL (plus
component_arguments and themes, as gallery_examples.py:50-51) on 50 recipes: 16 under config/data_analysis_recipes
(pipelines, templates top level, retest, experimental) in profile run, and 34 gallery recipes in profile gallery.
- Recipes with NEW errors: 0. No new error lines. HOME would refuse no more recipes.
- Only 1 recipe already has errors with the HOME catalogues (the same with FULL).
- Limit: the 72 shipped plot specs use only registered components with valid argument names (see 2), so PS04-arguments/PS05
  have nothing to catch today. This says nothing about uploaded recipes.

## 2. Silent cases in shipped recipes (RUN, q2.py, includes resolved with load_recipe)
Scanned 72 plot specs in 49 recipes. Hits: 0 for every case:
- element_text without target: 0 (3 element_text layers, all have target)
- guide_* with unmapped aesthetic: 0 (no guide_* layer is used at all)
- position_* with no geom/stat before it: 0 (5 position layers, all after a geom)
- annotate without geom: 0 (annotate not used)
- unknown spec key: 0; param not accepted by the argument catalogue: 0; "colour" in name or param: 0
- Not scanned: config/data_analysis_recipes/experimental/test_logic.yaml (does not load).
- Components used: geom_*, labs 37, facet_*, scale_x_discrete, theme_minimal 12, position_*, coord_flip.
=> Turning the silent paths into errors changes no shipped picture and refuses no shipped recipe.
Not covered: the 194 libs/viz_factory/tests/test_data recipes (format 0, not shipped), uploaded recipes.

## 3. Draw-time error at HOME (READ)
- home_theater.py:506-559 (_group_plot_handler): try/except wraps only viz_factory.render(...) (:556). On error: a
  matplotlib figure with red text "Render error:\n<message>" and an entry in session_processing_issues (Processing Issues panel).
- But render() returns an undrawn ggplot (no .draw in viz_factory.py). Shiny draws it AFTER the handler returns
  (shiny/render/_render.py:338 try_render_plotnine), outside that try. So a TypeError/PlotnineError from .draw() is not caught by
  the app: not in the figure, not in Processing Issues, no notification.
- Shiny then prints the traceback to the console and sends the message to the browser (_session.py:1979-1992). The app does
  not set sanitize_errors (default False, _app.py:49), so the user sees the raw exception text as a red error in the plot area
  (standard Shiny output error), without our fix/who form. Not run in a browser: the red-text display is READ, not seen.
- Same for the Compare left pane handler (:623-640).

## 4. Seed (READ)
- Recipe without random_state and with jitter (layers_have_jitter): HOME draws a fresh seed per session with
  secrets.randbits(31) (home_theater.py:432) and passes it to render. It is stored in last_drawn_seeds (:437-441).
- Export: export_handlers.py:1286-1318 writes seeds_per_plot into effective_run.yaml: the T3-pinned random_state, else the
  drawn seed (last_drawn_seeds), only when the plot was rendered in that session. The export warns about unpinned seeds
  (:820-829, "random_state: random ... exported with the number actually drawn"). The report text points to effective_run.yaml (:1527).
- So the seed used IS written in the bundle (effective_run.yaml). Not checked: whether report.qmd itself shows the number,
  and the default VizFactory seed 0 when the render path has no seed (not the HOME path). The seed is not written back to the recipe.
