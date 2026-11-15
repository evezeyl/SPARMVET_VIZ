import pandas as pd
import polars as pl
from plotnine import ggplot, aes
from typing import Dict, Any, List
# Explicit imports to ensure registration occurs
from viz_factory.registry import get_component
from viz_factory.plot_config_resolver import (
    BATCHED_COMPONENTS, resolve_plot_config, spec_key_names, unknown_spec_keys)
from utils.random_layers import is_random_layer, is_seed_value, position_of
from viz_factory.checked_plot import (
    CheckedPlot, PlotContext, Step, draw_checked, explain_build_failure, plot_warnings, show_draw_errors)
from viz_factory.errors import layer_label, plot_failure
from utils.engines import engine_problem
from utils.errors import VisualizationError
from utils.filter_values import filter_condition
from utils.missing_values import keep_missing
from utils.na_choice import na_of
from utils.pipeline_error import PipelineError
import dataclasses
import difflib

# @deps
# provides: class:VizFactory, function:VizFactory.render, constant:DEFAULT_RANDOM_STATE, function:draw_checked and function:show_draw_errors (re-exported from checked_plot.py)
# consumes: libs/viz_factory/src/viz_factory/registry.py, libs/viz_factory/src/viz_factory/plot_config_resolver.py, libs/viz_factory/src/viz_factory/checked_plot.py, libs/viz_factory/src/viz_factory/errors.py, libs/utils/src/utils/errors.py, libs/utils/src/utils/pipeline_error.py, libs/utils/src/utils/filter_values.py, libs/utils/src/utils/engines.py, libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py
# consumed_by: app/src/server.py, app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/gallery_examples.py, app/tests/test_render_every_plot.py, libs/viz_factory/tests/
# doc: .claude/rules/rules_viz_factory.md, .claude/knowledge/architecture_decisions.md (ADR-081, ADR-090, ADR-094, ADR-106)
# @end_deps

# Default seed of every random plot component (jitter). With a fixed default the same data and the
# same data analysis recipe give the same picture, which reports and audits need. A layer can set its own
# `random_state`, and VizFactory(random_state=...) changes the default for a whole factory
# (tests that need a known arrangement, or a deliberate different one).
#
# PROVISIONAL (S1, Eve's rule of 2026-11-15): a seed is a number. `random_state: null` or "random" on a layer is
# refused (the same recipe gives the same picture); VizFactory(random_state=None) stays as the handle for a test
# that needs a different arrangement each time.
DEFAULT_RANDOM_STATE = 0
RANDOM = "random"   # the word that means "no seed"; refused in a layer, see _refuse_unseeded_layer


def _generator(seed):
    """A numpy random generator for this seed, or None for "no seed" (random every time).

    "No seed" is None, null in YAML, or the word "random".

    plotnine's jitter does `if not random_state: use the global random generator`, so a seed of 0
    (falsy) would silently mean "no seed". A generator object is always truthy, so every number,
    0 included, really seeds the arrangement. A new one is built per use, so every render of the
    same plot draws the same sequence.
    """
    import numpy as np
    if seed is None or (isinstance(seed, str) and seed.strip().lower() == RANDOM):
        return None
    return np.random.RandomState(int(seed))


JITTER_COMPONENTS = ("geom_jitter", "position_jitter", "position_jitterdodge")


def _seed_random_components(layer_name: str, params: dict, random_state) -> dict:
    """Give every random layer a seed, unless the layer sets its own `random_state`.

    A layer is random when `utils.random_layers.is_random_layer` says so (the recipe checker uses the same rule).
    It reaches a plot in these ways: a geom's `position: jitter` or `jitterdodge` parameter, `geom_jitter`, the
    `position_jitter` / `position_jitterdodge` layers, `geom_sina` / `stat_sina`, and a bootstrapped summary
    (`fun_data: mean_cl_boot`). The seed goes in as a numpy generator, never a bare number (plotnine reads 0 as
    "no seed" for jitter).
    """
    from plotnine import position_jitter, position_jitterdodge
    params = dict(params)
    position = position_of(params)            # `jitter` and `position_jitter` are the same position (plotnine's rule)
    if position == "position_jitter":
        params["position"] = position_jitter(random_state=_generator(params.pop("random_state", random_state)))
    elif position == "position_jitterdodge":
        params["position"] = position_jitterdodge(random_state=_generator(params.pop("random_state", random_state)))
    elif layer_name in JITTER_COMPONENTS and not (layer_name == "geom_jitter" and "position" in params):
        params["random_state"] = _generator(params.get("random_state", random_state))
    elif is_random_layer(layer_name, params):
        # sina and a bootstrapped summary: the seed is a parameter of the stat
        params["random_state"] = _generator(params.get("random_state", random_state))
    return params


def _refuse_unseeded_layer(layer_name: str, params: dict, plot_id: str, where: str) -> None:
    """Raise when a random layer writes a `random_state` that is not a number: null, the word random, other text
    (PROVISIONAL S1, Eve's rule of 2026-11-15, "every seed that is used is written"). A layer that writes nothing
    takes the factory's seed. `VizFactory(random_state=None)` (a factory built without a seed, the handle for tests) is
    not a layer and is not refused. `where` is how an error names the layer (`layer 2 (geom_point)`)."""
    if "random_state" in params and is_random_layer(layer_name, params):
        _refuse_non_number(where, params["random_state"], plot_id)


def _refuse_non_number(where: str, written, plot_id: str) -> None:
    """The one error form of the plot layer (`errors.plot_failure`): what, which plot and layer, and the fix."""
    if not is_seed_value(written):
        raise plot_failure(
            plot_id, f"random_state is {written!r}, but a seed is a number",
            "write a number: random_state: 0 (any whole number; another number gives another arrangement, the same "
            "number gives the same one)",
            layer=where, evidence={"random_state": written}, reference="rules_viz_factory.md section 8")


def _recipe_seed(plot_defaults: dict, plot_id: str, factory_seed):
    """`plot_defaults.random_state` (PROVISIONAL S3: the one seed of the whole recipe), else the factory's seed.
    null and the word random are refused like in a layer (S1)."""
    if "random_state" not in plot_defaults:
        return factory_seed
    written = plot_defaults["random_state"]
    _refuse_non_number("plot_defaults", written, plot_id)
    return written


def _refuse_plot_engine_not_built(data_analysis_recipe: Dict[str, Any], plot_id: str) -> None:
    """Raise when the recipe names a plot engine this library does not implement (ADR-106 V8).

    No `plot_engine` key (library use outside a recipe, tests) means the implemented engine. The names are in
    `utils.engines`, the same list the recipe checker uses (code T06).
    """
    if "plot_engine" not in data_analysis_recipe:
        return
    problem = engine_problem("plot_engine", data_analysis_recipe["plot_engine"])
    if problem is None:
        return
    what, fix = problem
    raise plot_failure(plot_id, f"it cannot be drawn: {what} (recipe key plot_engine)", f"in the data analysis recipe, {fix}",
                       evidence={"plot_id": plot_id, "plot_engine": data_analysis_recipe["plot_engine"]})


class VizFactory:
    """
    Electronic Artist Pillar (VizFactory).
    Takes standardized Polars dataframes and applies declarative Plotnine layers.

    Default Injection Policy:
    - Theme: theme_bw (if no theme_ layer defined)
    - Coord: coord_cartesian (if no coord_ layer defined)
    - Facet: facet_null (if no facet_ layer defined)
    - Position/Stat: These are ggplot2 geom-level defaults (identity); no injection needed.

    Palette registry (BP-COLOR-3):
    - Built-in SPARMVET palettes are always present (no external file required).
    - Deployment palettes are injected at construction via palette_registry kwarg — the app layer
      resolves config/palettes.yaml via bootloader.get_palettes() and passes the dict here.
    - Library is fully independent: works with only built-ins when no registry is passed.
    - Data analysis recipes may declare plot_defaults: palette: <name> to set a default scale for all plots.
    - Individual plot specs may declare palette: <name> to override the data analysis recipe default.
    - Resolution order: plot-level palette > data analysis recipe plot_defaults.palette > none (matplotlib default).
    """

    # Built-in brand palette — always present; no external config required.
    # Uses the authoritative brand colors from rules_css_style_spec.md §1c.
    _BUILTIN_PALETTES: dict = {
        "sparmvet_brand": [
            "#345beb",  # Blue — primary action
            "#10a395",  # Teal — export/upload
            "#ffc107",  # Amber — warning/pending
            "#d62828",  # Red — error/destructive
            "#6c757d",  # Grey — muted
            "#6a4c93",  # Violet — audit nodes
        ]
    }

    def __init__(self, palette_registry: dict | None = None, random_state=DEFAULT_RANDOM_STATE):
        # Seed used by every random component that does not set its own (see DEFAULT_RANDOM_STATE).
        self._random_state = random_state   # an int, or None / "random" for no seed
        # Merge built-ins with deployment palettes injected by the app layer.
        # Deployment palettes override built-ins when names collide (intentional branding).
        self._palette_registry: dict = {**self._BUILTIN_PALETTES, **(palette_registry or {})}

    @property
    def default_random_state(self):
        """The seed used by every random component whose recipe writes none (see DEFAULT_RANDOM_STATE)."""
        return self._random_state

    def render(self, df: Any, data_analysis_recipe: Dict[str, Any], plot_id: str,
               aesthetic_override: dict | None = None):
        """
        Main entry point for rendering a single plot by ID from a data analysis recipe.
        Supports both Polars LazyFrame and DataFrame.

        Uses the five-tier plot config cascade (VIZFAC-PLOT-CASCADE-1):
        L5 (T3 aesthetic_override) > L4 (spec) > L3 (optimisation) >
        L2 (plot_defaults) > L1 (built-ins). Delegation to resolve_plot_config()
        is the single merge point — _standardize_config and _auto_adjust_axis_labels
        are no longer called from this path (VIZFAC-RENDER-WIRE-1).

        aesthetic_override : dict | None
            T3 L5 overrides for this specific plot (fill_color, fill_palette,
            colour, alpha, shape, size, theme). Supplied by home_theater from
            home_state['t3_plot_overrides'][plot_id]. VIZFAC-T3-OVERRIDE-1.
        """
        _refuse_plot_engine_not_built(data_analysis_recipe, plot_id)

        # Warnings: the plot still draws, but the author must be told (VIZ-STANDARD-1). They are kept on the plot, where a screen
        # reads them (`plot_warnings`), and also printed. A warning that is the same twice is kept once.
        warnings_found: list = []

        def warn(pe: PipelineError, plot_scoped: bool = True) -> None:
            if plot_scoped:
                pe = dataclasses.replace(pe, problem=f"Plot '{plot_id}': {pe.problem}")
            print(pe.format())
            if not any((w.problem, w.location) == (pe.problem, pe.location) for w in warnings_found):
                warnings_found.append(pe)

        # Ensure LazyFrame for consistent ADR-010 handling
        if isinstance(df, pl.DataFrame):
            df = df.lazy()

        raw_spec = data_analysis_recipe.get('plots', {}).get(plot_id)
        if not raw_spec:
            raise plot_failure(
                plot_id, "it is not in the data analysis recipe",
                "declare it under 'analysis_groups.<group>.plots' in the data analysis recipe and check that the `spec: !include` path resolves",
                evidence={"plot_id": plot_id, "available_plots": list(data_analysis_recipe.get("plots", {}).keys())})

        # A key that is not part of the plot spec format used to be moved to `_meta` and ignored: `theem: theme_bw`
        # drew the plot without the theme and said nothing (VIZ-STANDARD-1, V6).
        unknown = unknown_spec_keys(raw_spec)
        if unknown:
            known = spec_key_names()
            close = difflib.get_close_matches(str(unknown[0]), known, n=1, cutoff=0.6)
            raise plot_failure(
                plot_id, "; ".join(f"{key!r} is not a key of a plot spec" for key in unknown),
                f"write {close[0]}" if close else "remove it, or write one of " + ", ".join(known),
                evidence={"unknown_keys": [str(k) for k in unknown]})

        plot_defaults = data_analysis_recipe.get('plot_defaults') or {}
        # PROVISIONAL (S3): the seed of a random layer that writes none is the recipe's (plot_defaults), else the factory's
        recipe_seed = _recipe_seed(plot_defaults, plot_id, self._random_state)

        # 1. Tier 3: Apply UI-driven filters (predicate pushdown on LazyFrame).
        # Must happen before collect() to preserve lazy evaluation.
        # DEMO-4: coerce string filter values to column dtype for numeric columns.
        ui_filters = raw_spec.get('filters', [])
        if ui_filters:
            print(f"  └── Tier 3 (Leaf): Applying {len(ui_filters)} UI filters...")
            try:
                schema = df.collect_schema()
                actual_dtypes = {n: schema[n] for n in schema.names()}
            except Exception:
                actual_dtypes = {}

            for f in ui_filters:
                col = f.get("column")
                if col is None:
                    continue
                # Issue #56: a filter on a column this plot's data does not have is skipped, not an error.
                if actual_dtypes and col not in actual_dtypes:
                    continue
                # ADR-104 point 7: the same condition as the HOME table and the recipe action (typed values; a value that
                # cannot be read in the type of the column stops with a plain error). NA-RULE-63: `na` adds the rows with no value.
                dtype = actual_dtypes.get(col) or f.get("dtype")
                condition = filter_condition(col, f.get("op", "eq"), f.get("value"), dtype, f.get("closed", "both"))
                df = df.filter(keep_missing(condition, col, na_of(f)))

        # 2. Single materialisation point — after all Polars filters (ADR-010).
        df_pandas = df.collect().to_pandas()

        # 3. Resolve five-tier cascade (L1 built-ins through L5 T3 override).
        try:
            resolved = resolve_plot_config(raw_spec, plot_defaults, df_pandas,
                                           aesthetic_override=aesthetic_override)
        except VisualizationError as exc:
            raise plot_failure(plot_id, exc.message, exc.tip) from exc

        # 4. Emit structured warnings for unrecognised plot_defaults keys and L5 mutex (ADR-079).
        for key in resolved["_unknown_plot_defaults_keys"]:
            pe = PipelineError(
                component="VizFactory",
                problem=f"Unknown plot_defaults key '{key}' — ignored.",
                location="recipe plot_defaults",
                fix=(
                    f"Remove or correct the key '{key}' in the data analysis recipe 'plot_defaults:' block. "
                    "Valid keys: palette, theme, default_font_family, facet_panel_spacing, "
                    "legend_position, optimisation. See rules_data_analysis_recipe_structure.md §10."
                ),
                who="data_analysis_recipe_author",
                category="visualization",
                surface="notification",
                severity="warning",
                evidence={"unknown_key": key},
                reference="rules_data_analysis_recipe_structure.md §10",
            )
            warn(pe, plot_scoped=False)
        if resolved["_l5_mutex_warn"]:
            pe = PipelineError(
                component="VizFactory",
                problem="T3 aesthetic_override supplied both 'fill_color' and 'fill_palette' (mutex). fill_palette takes precedence.",
                location=f"VizFactory.render(plot_id='{plot_id}')",
                fix="Use either 'fill_color' (hex) OR 'fill_palette' (palette name) — not both. See ui_implementation_contract.md §12g.9.",
                who="analyst",
                category="t3_apply",
                surface="audit_panel",
                severity="warning",
            )
            warn(pe)

        # 5. Validate aesthetics — all mapped columns must exist in the dataset.
        mapping_spec = resolved["mapping"]
        all_cols = list(df_pandas.columns)
        for aesthetic, col_name in mapping_spec.items():
            if col_name not in all_cols:
                matches = difflib.get_close_matches(col_name, all_cols, n=1, cutoff=0.6)
                raise plot_failure(
                    plot_id, f"the aesthetic '{aesthetic}' is mapped to the column '{col_name}', which the data does not have",
                    (f"write '{matches[0]}' (the closest column)" if matches else
                     f"use a column that exists in the target_dataset after all wrangling and assembly steps") + ".",
                    evidence={"aesthetic": aesthetic, "column": col_name, "near_match": matches[0] if matches else None,
                              "available_columns": all_cols[:20]},
                    reference="rules_data_analysis_recipe_structure.md §8")

        # 6. Build the plot. It is a CheckedPlot: it keeps the steps it was built from, so that a failure while it is
        # drawn (plotnine builds lazily) is traced to a layer and a parameter and raised in the one error form (V7).
        context = PlotContext(plot_id, df_pandas, mapping_spec)
        p = CheckedPlot(df_pandas, aes(**mapping_spec))
        context.warnings = warnings_found
        p._sparmvet = context

        def apply(p, step: Step):
            """Apply one step; a failure of the component is the one error form, naming this layer."""
            try:
                out = step.func(p, dict(step.params))
            except Exception as exc:
                raise explain_build_failure(plot_id, p, step, exc) from exc
            context.steps.append(step)
            return out

        # 7. Apply resolved layers sequentially. The element_text layers (axis-text overrides, L3 and above) go last.
        deferred: list = []
        for layer_spec in resolved["layers"]:
            layer_name = layer_spec.get("name")
            tier, number = layer_spec.get("_tier"), layer_spec.get("_layer_no")
            # `_tier` / `_layer_no` are internal markers; only the params go to the component.
            layer_params = {k: v for k, v in layer_spec.get("params", {}).items()}
            where = layer_label(tier, number, str(layer_name))

            if not layer_name:
                raise plot_failure(plot_id, "a layer has no name", "write name: geom_point (or another component) for every layer",
                                   layer=where)
            if layer_name not in BATCHED_COMPONENTS:
                _refuse_unseeded_layer(layer_name, layer_params, plot_id, where)
                layer_params = _seed_random_components(layer_name, layer_params, recipe_seed)
            try:
                component_func = get_component(layer_name)
            except ValueError as exc:
                all_registered = list(__import__("viz_factory.registry", fromlist=["PLOT_COMPONENTS"]).PLOT_COMPONENTS.keys())
                matches = difflib.get_close_matches(layer_name, all_registered, n=1, cutoff=0.6)
                raise plot_failure(
                    plot_id, f"'{layer_name}' is not a registered plot component",
                    f"write {matches[0]}" if matches else "write the name of a registered component (see libs/viz_factory/README.md)",
                    layer=where, evidence={"layer_name": layer_name, "near_match": matches[0] if matches else None},
                    reference="rules_viz_factory.md §1") from exc

            step = Step(layer_name, layer_params, component_func, tier=tier, layer_no=number)
            if layer_name in BATCHED_COMPONENTS:
                deferred.append(step)
                continue
            p = apply(p, step)
            print(f"Applied layer: {layer_name}")

        for step in deferred:
            p = apply(p, step)
        if deferred:
            print(f"Applied axis text overrides: {[s.params.get('target') for s in deferred]}")

        # 8. Apply flat labels / guides blocks (backwards-compat with spec-level dicts).
        # In typical data analysis recipes these come from a labs layer; the flat keys are legacy.
        labels_block = resolved.get("labels", {})
        if labels_block:
            from plotnine import labs
            p = apply(p, Step("labels", dict(labels_block), lambda q, params: q + labs(**params), label="the spec's labels"))
            print(f"Applied labels: {list(labels_block.keys())}")

        guides_block = resolved.get("guides", {})
        if guides_block:
            from plotnine import guides, guide_legend, guide_colorbar
            _guide_ctors = {"guide_legend": guide_legend, "guide_colorbar": guide_colorbar}

            def _guides(q, params):
                guide_map = {}
                for aes_key, guide_spec in params.items():
                    if isinstance(guide_spec, dict):
                        guide_spec = dict(guide_spec)  # copy before pop
                        ctor_name = guide_spec.pop("name", "guide_legend")
                        ctor = _guide_ctors.get(ctor_name, guide_legend)
                        guide_map[aes_key] = ctor(**guide_spec)
                    elif guide_spec is False or guide_spec == "none":
                        guide_map[aes_key] = False
                return q + guides(**guide_map) if guide_map else q

            p = apply(p, Step("guides", dict(guides_block), _guides, label="the spec's guides"))
            print(f"Applied guides: {list(guides_block.keys())}")

        # 9. Palette injection (BP-COLOR-3, §6c).
        # palette_scope encodes which aesthetics still need a scale after dedup —
        # has_fill_scale / has_color_scale invert this for _apply_palette's API.
        palette_name = resolved["palette"]
        if palette_name:
            palette_scope = resolved["palette_scope"]
            has_fill_scale = "fill" not in palette_scope
            has_color_scale = "color" not in palette_scope
            p = apply(p, Step(
                "palette", {}, lambda q, _params: self._apply_palette(q, palette_name, mapping_spec, has_fill_scale, has_color_scale, warn, df_pandas),
                label=f"the palette '{palette_name}'"))

        return p

    def _apply_palette(
        self,
        p,
        palette_name: str,
        mapping_spec: dict,
        has_fill_scale: bool,
        has_color_scale: bool,
        warn,
        df=None,
    ):
        """Inject a named palette as a plotnine fill/colour scale (BP-COLOR-3).

        Resolution:
        - Name found in self._palette_registry → scale_*_manual with the hex list.
        - Name not in registry → treat as a matplotlib palette name:
            Sequential/diverging names → scale_*_distiller (continuous-safe fallback).
            Otherwise → scale_*_brewer (categorical).
        - Only injects for aesthetics present in the mapping.
        - Never overwrites a scale already declared in the data analysis recipe layers.
        """
        uses_fill = "fill" in mapping_spec and not has_fill_scale
        uses_color = ("color" in mapping_spec or "colour" in mapping_spec) and not has_color_scale

        if not uses_fill and not uses_color:
            return p

        deployment_colors = self._palette_registry.get(palette_name)
        if deployment_colors:
            # Deployment palette — inject scale_*_manual
            if uses_fill:
                from plotnine import scale_fill_manual
                p = p + scale_fill_manual(values=deployment_colors)
                print(f"[VizFactory] Applied deployment palette '{palette_name}' → scale_fill_manual")
            if uses_color:
                from plotnine import scale_color_manual
                p = p + scale_color_manual(values=deployment_colors)
                print(f"[VizFactory] Applied deployment palette '{palette_name}' → scale_color_manual")
        else:
            # Matplotlib palette name — use brewer or distiller
            # Viridis family and continuous palettes go through distiller
            _continuous_palettes = {
                "viridis", "plasma", "magma", "inferno", "cividis",
                "Blues", "Greens", "Oranges", "Purples", "Reds",
                "BuGn", "BuPu", "GnBu", "OrRd", "PuBu", "YlGn",
                "RdYlGn", "RdYlBu", "Spectral",
            }
            _viridis_palettes = {"viridis", "plasma", "magma", "inferno", "cividis"}
            if palette_name in _viridis_palettes:
                try:
                    # plotnine has no scale_*_viridis_*; the colour map is applied with scale_*_cmap_d (a discrete
                    # aesthetic) or scale_*_cmap (a numeric one), chosen by the dtype of the mapped column.
                    from plotnine import scale_fill_cmap, scale_fill_cmap_d, scale_color_cmap, scale_color_cmap_d

                    def _is_continuous(aes_key: str) -> bool:
                        column = mapping_spec.get(aes_key)
                        return df is not None and column in df.columns and \
                            pd.api.types.is_numeric_dtype(df[column]) and not pd.api.types.is_bool_dtype(df[column])

                    if uses_fill:
                        scale = scale_fill_cmap if _is_continuous("fill") else scale_fill_cmap_d
                        p = p + scale(cmap_name=palette_name)
                    if uses_color:
                        colour_key = "color" if "color" in mapping_spec else "colour"
                        scale = scale_color_cmap if _is_continuous(colour_key) else scale_color_cmap_d
                        p = p + scale(cmap_name=palette_name)
                    print(f"[VizFactory] Applied viridis palette '{palette_name}'")
                except Exception as exc:
                    pe = PipelineError(
                        component="VizFactory",
                        problem=f"Viridis palette '{palette_name}' failed to apply: {exc}",
                        location="_apply_palette",
                        fix=f"Check that '{palette_name}' is a valid viridis option (viridis, plasma, magma, inferno, cividis).",
                        who="data_analysis_recipe_author",
                        category="visualization",
                        surface="plot_overlay",
                        severity="warning",
                        evidence={"palette_name": palette_name, "error": str(exc)[:200]},
                    )
                    warn(pe)
            else:
                try:
                    from plotnine import scale_fill_brewer, scale_color_brewer
                    if uses_fill:
                        p = p + scale_fill_brewer(palette=palette_name)
                    if uses_color:
                        p = p + scale_color_brewer(palette=palette_name)
                    print(f"[VizFactory] Applied brewer palette '{palette_name}'")
                except Exception as exc:
                    pe = PipelineError(
                        component="VizFactory",
                        problem=f"Palette '{palette_name}' not found in the deployment palette registry or plotnine/RColorBrewer.",
                        location="_apply_palette",
                        fix=(
                            f"Check the palette name in the data analysis recipe. "
                            f"Valid deployment palettes: {list(self._palette_registry.keys()) or ['(none registered)']}. "
                            "Or use a matplotlib/RColorBrewer name such as 'Blues', 'Set1', 'viridis'."
                        ),
                        who="data_analysis_recipe_author",
                        category="visualization",
                        surface="plot_overlay",
                        severity="warning",
                        evidence={"palette_name": palette_name, "error": str(exc)[:200]},
                        reference="rules_viz_factory.md §6c",
                    )
                    warn(pe)

        return p
