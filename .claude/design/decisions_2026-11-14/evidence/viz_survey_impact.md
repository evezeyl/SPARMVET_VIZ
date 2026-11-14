# Impact survey: what depends on `libs/viz_factory` (scout, read-only, 2026-11-14)

All facts READ (search and file:line). Items marked NOT CHECKED were not searched.

## 1. Code outside the library that imports or calls it
- `app/src/server.py:22` imports `VizFactory`; `:41` imports `COMPONENT_SCHEMAS`.
- `app/handlers/blueprint_handlers.py:84` imports `normalise_plot_spec`, `serialise_plot_spec` (plot_config_resolver); `:2768` and `:2829` name the removed `factory_id` key.
- `app/handlers/home_theater.py:48` imports `layers_have_jitter`, `recipe_pins_random_state`.
- `app/modules/gallery_examples.py:40-43` (`argument_catalog`, `PLOT_COMPONENTS`), `:119` `VizFactory`.
- `app/modules/data_analysis_recipe_validator.py:111` imports `viz_factory.arguments.argument_catalog`.
- `app/modules/help_registry.py:86` imports `PLOT_COMPONENT_REGISTRY` (help_registry itself is imported by nothing).
- `libs/blueprint_arch/src/blueprint_arch/schema_registry.py:91-122` (component lookup by context tag "plot"); `agent_tools.py:6,143`.
- Tests: `app/tests/test_qa_canaries.py:32`, `test_render_every_plot.py:19`, `test_filter_int_equivalence.py:18`, `test_writers_emit_format_one.py:22,33,34`, `test_shipped_recipes_hygiene.py:17` (`_CANONICAL_SPEC_KEYS`, `_VALID_PLOT_DEFAULTS_KEYS`), `test_shipped_recipes_pass_the_checker.py:16`.
- Audit scripts under `scripts/`: `audit_data_analysis_recipe_coherence.py:566`, `audit_parity_coverage.py:402` (scan `@register_plot_component`), `audit_palette_registry.py:173`, `audit_package_deps.py:51`, `migrate_data_analysis_recipes.py:21`.
- NOT CHECKED: the imports of `libs/viz_gallery`; the exact calls in `assets/scripts/figshare_plot_integration.py`, `gallery_previews.py`, `convert_gallery_examples.py`; whether the library has its own error class.

## 2. Plot specs written in files
- `config/data_analysis_recipes/pipelines/*/plots/*.yaml`: 25 plot spec files (1_test_data_ST22_dummy 18, 2_test_data_ST22_dummy 3, stress_test_master 1, figshare_integration 3).
- Inline plot blocks in templates, retest and top-level pipeline files: 45 files match the key pattern (not split per plot).
- `assets/gallery_data/`: 34 `data_analysis_recipe.yaml`; `tasks.md:167` says the gallery shows 33 (`beeswarm_sina` not converted).
- Top-level keys seen in one spec (`MLST_counts_bar.yaml:1-10`): `target_dataset`, `title`, `layers`, `mapping`.
- `factory_id`: only as a refused key name in `blueprint_handlers.py:2768,2829` and in an audit script; no recipe file with it found (not checked file by file).
- NOT COUNTED: the test recipes under `libs/viz_factory/tests/`; the YAML examples with `layers:` in `docs/` (165 mentions of layers / plotnine / viz_factory across 31 files; `docs/appendix/viz_factory_components.qmd`, `docs/workflows/visualisation_factory.qmd`).

## 3. Readers of the plot part of a recipe outside the library
- `libs/utils/src/utils/recipe_check.py`: `plot_targets()` `:240-245` reads `analysis_groups[*].plots[*].spec.target_dataset`; group and plot checks G01, G02 `:621-647`; `plot_defaults` at `:157`; renamed `plots` key T08 `:169-171`.
- `.claude/design/plot_config_cascade.md`, `plot_authoring_model.md` exist.
- NOT CHECKED: the export (`report.qmd`, plot files), the gallery preview generator.

## 4. Records
- ADRs: ADR-008 (Plotnine primary), ADR-019 (decorator plot registry), ADR-020 (data-agnostic plotting manifest), ADR-036 (parity mandate), ADR-081 (palette registry), ADR-083 (canonical plot model, `factory_id` removed), ADR-086 (plot to show against data to show), ADR-090 (same picture). Gallery ADRs: 025, 028, 033, 035, 037, 057, 059, 061, 063, 093.
- Rule files: `.claude/rules/rules_viz_factory.md`, `rules_gallery_standards.md`, `rules_data_analysis_recipe_structure.md` sections 8 and 10. Workflow: `.claude/workflows/viz_factory_implementation.md`.
- Spec `.claude/design/recipe_format_spec.md`: `plot_engine` at `:28`, `:223`, `:525`; the DEC rows below; line `:465` on `facet_by` and filters with R1 open.
- `tasks.md`: `:41` (N9), `:97` (HOME-EXPLORE-8: plot-spec keys dropped to `_meta`), `:167` (gallery 33 examples), `:256-259` (MAP-A-DOCS-1 touches the library README). No task named VIZFAC-* found open.
- User docs: `docs/appendix/viz_factory_rationale.qmd`, `viz_factory_components.qmd`, `docs/workflows/visualisation_factory.qmd`, `docs/user_guide/viz_gallery.qmd`, `reproducible_plots.qmd`.

## 5. Already decided about plots in format 1 (`recipe_format_spec.md`)
- DECIDED (2026-11-13): DEC05 `plot_engine: python-plotnine` is required (`:92`); DEC09 plot arguments are checked (`:96`); DEC17 the tier-3 container sits on the plot entry, the checker refuses a non-empty one until the engine reads it (`:109`); DEC18 profiles run / build / gallery / audit (`:110`); DEC21 taxonomy on the plot entry (`:113`); DEC22 axis titles default to the field label (`:114`); DEC39 `modif_filter` replaces `filter_*` and the VizFactory filter vocabulary (`:141`).
- CONFIRM: DEC39 "its behaviour is verified first" (MODIF-FILTER-VERIFY-1), not verified yet.
- OPEN: R1 (the order of the tier-3 change; `facet_by` and filters written twice, `:465`); N9.
