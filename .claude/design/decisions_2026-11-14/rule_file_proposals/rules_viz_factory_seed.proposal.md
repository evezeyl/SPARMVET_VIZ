# Proposal: `rules_viz_factory.md` section 8, the random seed (SEED-HOLDS-1)

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Written by the SEED-HOLDS-1 branch (`task/seed-holds`).

Decision behind it: Eve, **2026-11-15**: "every seed that is used is written" (in the recipe or in the audit recipe). A layer that writes no
number uses 0, in every place; HOME draws no seed; `random_state: null` and `random` are refused (S1, provisional);
`plot_defaults: random_state` is the one seed of a whole recipe (S3, provisional). Built and tested on this branch; ADR-104.

The file's own line 123 is wrong today: it says `random_state: null` (or `random`) gives a new arrangement on each render. The code refuses it.

Section 8 as it stands (lines 115 to 124) and what to write instead. Old lines are quoted; "New" replaces them.

1. Line 117. Old: `Every random component (jitter in all its forms) is seeded:`
   New: `Every random layer is seeded. Which layers are random is one rule, utils.random_layers.is_random_layer: a random component (geom_jitter, position_jitter, position_jitterdodge, geom_sina, stat_sina), a geom placed with position jitter or jitterdodge, a geom with stat sina, and a bootstrapped summary (stat_summary or stat: summary with no function named or mean_cl_boot; stat_summary_bin only with mean_cl_boot). A position or a stat written as text is read the way plotnine reads it (jitter and position_jitter are the same). The factory seeds exactly these layers and the recipe checker (PS04) accepts random_state on exactly these layers.`
2. Line 118 (`DEFAULT_RANDOM_STATE = 0 ...`) stays.
3. Line 120. Old: `A layer sets its own with random_state (...); a seed set on the layer wins over the factory's.`
   New: `A layer sets its own with random_state (a whole number); it holds in every place (HOME, the comparison panes, the gallery, Blueprint, the results bundle, the reproducibility export and its re-run). A layer that writes none uses the factory's seed, 0. One seed per random layer: a layer's number never flows to another layer. HOME draws no seed.`
4. After line 120, add: `Order (one function, plot_config_resolver.resolve_layer_seeds): an audit pin (L5, applies to every random layer of the plot) > the layer's own number > [PROVISIONAL, S3] plot_defaults: random_state > 0.`
5. Line 123. Old: `The seed is a default, not a rule: random_state: null (or random) on a layer, or VizFactory(random_state=None), gives a different arrangement on every render.`
   New: `[PROVISIONAL, S1] A seed is a number. random_state: null, random and any text that is not a whole number are refused by the checker (PS04) and by the factory (VisualizationError in the one error form, with the fix "write random_state: 0"). VizFactory(random_state=None) stays as the handle for a test that needs a different arrangement each time; it is not a recipe key.`
6. Line 124. Old: `A new random component must be seeded in _seed_random_components, and libs/viz_factory/tests/test_reproducible_render.py must cover it.`
   New: `A new random component or random parameter is added to utils.random_layers (the one rule), seeded by _seed_random_components, and covered by libs/viz_factory/tests/test_reproducible_render.py and test_every_component_randomness.py (which builds every registered component and every statistic and position, in both spellings, twice and compares).`
7. After line 124, add: `Every seed that is used is written: the export records the seed of every random layer (seeds_per_layer, seeds_per_plot, seed_source_per_plot in effective_run.yaml), writes the seeds it added into the reproducibility recipe (seeds_added_to_recipe), and lists an audit pin as a random_seed step (t3_steps.yaml, Methods, audit table). HOME shows the seed in use and where it comes from next to the plot.`

Also (`rules_data_analysis_recipe_structure.md` section 10a, the `plot_defaults` keys): add
`random_state: 0   # [PROVISIONAL, S3] the one seed of the whole recipe: a whole number; 0 when absent`.

Stale in the ADR log (not a rule file): `.claude/knowledge/architecture_decisions.md`, the ADR-097 note that says HOME draws over a recipe's seed, and ADR-090 point 2 (`random_state: null` gives a new arrangement).
