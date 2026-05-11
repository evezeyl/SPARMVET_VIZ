import polars as pl
from plotnine import ggplot, aes
from typing import Dict, Any, List
# Explicit imports to ensure registration occurs
from viz_factory.registry import get_component
from viz_factory.plot_config_resolver import resolve_plot_config
from utils.errors import VisualizationError
from utils.pipeline_error import PipelineError
import difflib

# @deps
# provides: class:VizFactory, method:render, method:_apply_palette
# consumes: libs/viz_factory/src/viz_factory/registry.py (PLOT_COMPONENTS via get_component)
#           libs/viz_factory/src/viz_factory/plot_config_resolver.py (resolve_plot_config — VIZFAC-RENDER-WIRE-1)
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-VIZFACTORY-1)
# consumed_by: app/handlers/home_theater.py, libs/viz_factory/tests/debug_gallery.py, app/src/server.py
# doc: .claude/rules/rules_viz_factory.md
# note: palette_registry is injected by app/src/server.py (bootloader.get_palettes()) — BP-COLOR-3
# @end_deps


# --- Default Layer Policy ---
# These are injected silently if the manifest omits the relevant layer category.
# NOTE: No default geom is injected; every manifest MUST define at least one geom explicitly.
_DEFAULT_THEME = "theme_bw"
_DEFAULT_COORD = "coord_cartesian"
_DEFAULT_FACET = "facet_null"


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
    - Project palettes are injected at construction via palette_registry kwarg — the app layer
      resolves config/palettes.yaml via bootloader.get_palettes() and passes the dict here.
    - Library is fully independent: works with only built-ins when no registry is passed.
    - Manifests may declare plot_defaults: palette: <name> to set a default scale for all plots.
    - Individual plot specs may declare palette: <name> to override the manifest default.
    - Resolution order: plot-level palette > manifest plot_defaults.palette > none (matplotlib default).
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

    def __init__(self, palette_registry: dict | None = None):
        # Merge built-ins with project palettes injected by the app layer.
        # Project palettes override built-ins when names collide (intentional branding).
        self._palette_registry: dict = {**self._BUILTIN_PALETTES, **(palette_registry or {})}

    def render(self, df: Any, manifest: Dict[str, Any], plot_id: str,
               aesthetic_override: dict | None = None):
        """
        Main entry point for rendering a single plot by ID from a manifest.
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
        # Ensure LazyFrame for consistent ADR-010 handling
        if isinstance(df, pl.DataFrame):
            df = df.lazy()

        raw_spec = manifest.get('plots', {}).get(plot_id)
        if not raw_spec:
            pe = PipelineError(
                component="VizFactory",
                problem=f"Plot ID '{plot_id}' not found in manifest.",
                location=f"VizFactory.render(plot_id='{plot_id}')",
                fix=(
                    "Verify that the plot_id is declared under 'analysis_groups.<group>.plots' "
                    "in the manifest and that the `spec: !include` path resolves correctly."
                ),
                who="manifest_author",
                category="visualization",
                surface="plot_overlay",
                severity="error",
                evidence={"plot_id": plot_id, "available_plots": list(manifest.get("plots", {}).keys())},
            )
            print(pe.format())
            raise VisualizationError(pe.problem, tip=pe.fix)

        plot_defaults = manifest.get('plot_defaults') or {}

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

            def _is_numeric(dt):
                return dt is not None and any(
                    t in str(dt) for t in ("Int", "UInt", "Float", "Decimal")
                )

            def _coerce_to_dtype(value, dt):
                try:
                    s = str(dt) if dt is not None else ""
                    if "Float" in s or "Decimal" in s:
                        return float(value)
                    if "Int" in s or "UInt" in s:
                        return int(float(value))
                except (ValueError, TypeError):
                    pass
                return value

            for f in ui_filters:
                col = f.get("column")
                op = f.get("op", "eq")
                val = f.get("value")
                if col is None:
                    continue

                actual_dt = actual_dtypes.get(col)
                is_numeric = _is_numeric(actual_dt)
                is_list_val = isinstance(val, list)

                # Auto-promote eq/ne to in/not_in when value is a list
                if is_list_val:
                    if op in ("eq", "in"):
                        op = "in"
                    elif op in ("ne", "not_in"):
                        op = "not_in"

                if op == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                    lo, hi = val
                    if is_numeric:
                        lo = _coerce_to_dtype(lo, actual_dt)
                        hi = _coerce_to_dtype(hi, actual_dt)
                    bt_closed = f.get("closed", "both")
                    df = df.filter(pl.col(col).is_between(lo, hi, closed=bt_closed))
                    continue

                if op in ("in", "not_in"):
                    vals = val if is_list_val else [val]
                    str_vals = [str(v) for v in vals]
                    expr = pl.col(col).cast(pl.Utf8).is_in(str_vals)
                    df = df.filter(expr if op == "in" else ~expr)
                    continue

                # String operand on a numeric column — coerce before compare.
                if is_numeric and isinstance(val, str):
                    print(
                        f"[viz_factory] WARNING: string operand on numeric column "
                        f"{col!r} ({actual_dt}); coercing {val!r}"
                    )
                if is_numeric:
                    val = _coerce_to_dtype(val, actual_dt)

                if op == "eq":
                    df = df.filter(pl.col(col) == val)
                elif op == "ne":
                    df = df.filter(pl.col(col) != val)
                elif op == "gt":
                    df = df.filter(pl.col(col) > val)
                elif op == "ge":
                    df = df.filter(pl.col(col) >= val)
                elif op == "lt":
                    df = df.filter(pl.col(col) < val)
                elif op == "le":
                    df = df.filter(pl.col(col) <= val)

        # 2. Single materialisation point — after all Polars filters (ADR-010).
        df_pandas = df.collect().to_pandas()

        # 3. Resolve five-tier cascade (L1 built-ins through L5 T3 override).
        resolved = resolve_plot_config(raw_spec, plot_defaults, df_pandas,
                                       aesthetic_override=aesthetic_override)

        # 4. Emit structured warnings for unrecognised plot_defaults keys and L5 mutex (ADR-079).
        for key in resolved["_unknown_plot_defaults_keys"]:
            pe = PipelineError(
                component="VizFactory",
                problem=f"Unknown plot_defaults key '{key}' — ignored.",
                location=f"VizFactory.render(plot_id='{plot_id}')",
                fix=(
                    f"Remove or correct the key '{key}' in the manifest 'plot_defaults:' block. "
                    "Valid keys: palette, theme, default_font_family, facet_panel_spacing, "
                    "legend_position, optimisation. See rules_manifest_structure.md §10."
                ),
                who="manifest_author",
                category="visualization",
                surface="notification",
                severity="warning",
                evidence={"unknown_key": key},
                reference="rules_manifest_structure.md §10",
            )
            print(pe.format())
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
            print(pe.format())

        # 5. Validate aesthetics — all mapped columns must exist in the dataset.
        mapping_spec = resolved["mapping"]
        all_cols = list(df_pandas.columns)
        for aesthetic, col_name in mapping_spec.items():
            if col_name not in all_cols:
                matches = difflib.get_close_matches(col_name, all_cols, n=1, cutoff=0.6)
                tip = f"Ensure column '{col_name}' exists in the target_dataset after all wrangling and assembly steps."
                if matches:
                    tip += f" Hint: Did you mean '{matches[0]}'?"
                pe = PipelineError(
                    component="VizFactory",
                    problem=f"Aesthetic '{aesthetic}' references unknown column '{col_name}'.",
                    location=f"VizFactory.render(plot_id='{plot_id}')",
                    fix=tip,
                    who="manifest_author",
                    category="visualization",
                    surface="plot_overlay",
                    severity="error",
                    evidence={
                        "aesthetic": aesthetic,
                        "column": col_name,
                        "near_match": matches[0] if matches else None,
                        "available_columns": all_cols[:20],
                    },
                    reference="rules_manifest_structure.md §8",
                )
                print(pe.format())
                raise VisualizationError(pe.problem, tip=pe.fix)

        # 6. Build the ggplot object.
        p = ggplot(df_pandas, aes(**mapping_spec))

        # 7. Apply resolved layers sequentially.
        # element_text layers are batched and applied together via a single theme()
        # call to avoid redundant theme accumulation overhead.
        element_text_batch: dict = {}
        for layer_spec in resolved["layers"]:
            layer_name = layer_spec.get("name")
            # Strip internal _tier / _meta keys before passing to components.
            layer_params = {k: v for k, v in layer_spec.get("params", {}).items()}

            if layer_name == "element_text":
                # Collect axis-text overrides; target is the theme kwarg name.
                target = layer_params.pop("target", None)
                if target:
                    element_text_batch[target] = layer_params
                continue

            try:
                component_func = get_component(layer_name)
            except ValueError as exc:
                all_registered = list(__import__("viz_factory.registry", fromlist=["PLOT_COMPONENTS"]).PLOT_COMPONENTS.keys())
                matches = difflib.get_close_matches(layer_name, all_registered, n=1, cutoff=0.6)
                pe = PipelineError(
                    component="VizFactory",
                    problem=f"Layer component '{layer_name}' is not registered.",
                    location=f"VizFactory.render(plot_id='{plot_id}')",
                    fix=(
                        f"'{layer_name}' is not a registered plot component. "
                        + (f"Did you mean '{matches[0]}'? " if matches else "")
                        + "See rules_viz_factory.md §1 and libs/viz_factory/src/viz_factory/ for the component list."
                    ),
                    who="manifest_author",
                    category="visualization",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"layer_name": layer_name, "near_match": matches[0] if matches else None},
                    reference="rules_viz_factory.md §1",
                )
                print(pe.format())
                raise VisualizationError(pe.problem, tip=pe.fix) from exc
            try:
                p = component_func(p, layer_params)
            except Exception as exc:
                pe = PipelineError(
                    component="VizFactory",
                    problem=f"Layer '{layer_name}' raised {type(exc).__name__}: {exc}",
                    location=f"VizFactory.render(plot_id='{plot_id}')",
                    fix="Review the layer parameters in the manifest spec. Check that all parameter values match the plotnine API for this component.",
                    who="manifest_author",
                    category="visualization",
                    surface="plot_overlay",
                    severity="error",
                    evidence={"layer_name": layer_name, "params": str(layer_params)[:200], "error_type": type(exc).__name__, "error_detail": str(exc)[:200]},
                )
                print(pe.format())
                raise VisualizationError(pe.problem, tip=pe.fix) from exc
            print(f"Applied layer: {layer_name}")

        # Apply batched element_text axis overrides (L3 optimisation + any L4/L5).
        if element_text_batch:
            from plotnine import theme, element_text
            theme_kwargs = {
                target: element_text(**et_params)
                for target, et_params in element_text_batch.items()
            }
            p = p + theme(**theme_kwargs)
            print(f"Applied axis text overrides: {list(element_text_batch.keys())}")

        # 8. Apply flat labels / guides blocks (backwards-compat with spec-level dicts).
        # In typical manifests these come from a labs layer; the flat keys are legacy.
        labels_block = resolved.get("labels", {})
        if labels_block:
            from plotnine import labs
            p = p + labs(**labels_block)
            print(f"Applied labels: {list(labels_block.keys())}")

        guides_block = resolved.get("guides", {})
        if guides_block:
            from plotnine import guides, guide_legend, guide_colorbar
            guide_map = {}
            _guide_ctors = {"guide_legend": guide_legend, "guide_colorbar": guide_colorbar}
            for aes_key, guide_spec in guides_block.items():
                if isinstance(guide_spec, dict):
                    guide_spec = dict(guide_spec)  # copy before pop
                    ctor_name = guide_spec.pop("name", "guide_legend")
                    ctor = _guide_ctors.get(ctor_name, guide_legend)
                    guide_map[aes_key] = ctor(**guide_spec)
                elif guide_spec is False or guide_spec == "none":
                    guide_map[aes_key] = False
            if guide_map:
                p = p + guides(**guide_map)
                print(f"Applied guides: {list(guide_map.keys())}")

        # 9. Palette injection (BP-COLOR-3, §6c).
        # palette_scope encodes which aesthetics still need a scale after dedup —
        # has_fill_scale / has_color_scale invert this for _apply_palette's API.
        palette_name = resolved["palette"]
        if palette_name:
            palette_scope = resolved["palette_scope"]
            has_fill_scale = "fill" not in palette_scope
            has_color_scale = "color" not in palette_scope
            p = self._apply_palette(
                p, palette_name, mapping_spec, has_fill_scale, has_color_scale
            )

        return p

    @staticmethod
    def _auto_adjust_axis_labels(p, df_collected, x_col: str | None, y_col: str | None = None):
        """
        Heuristically adjust x-axis label rotation and y-axis label font size
        to prevent crowding. Applied automatically unless the manifest has an
        explicit element_text layer.

        X-axis rules (categorical only — numeric/date left as-is):
          max_len > 12 or n_unique > 8  → 45° rotation, size 8, ha right
          max_len > 6  or n_unique > 5  → 35° rotation, size 9, ha right
          otherwise                      → no change

        Y-axis rules (any dtype):
          n_unique > 20 or max_len > 20  → size 7
          n_unique > 12 or max_len > 12  → size 8
          otherwise                      → no change
        """
        import pandas as pd
        from plotnine import theme, element_text

        x_kwargs = {}
        y_kwargs = {}

        # --- X-axis ---
        if x_col is not None and x_col in df_collected.columns:
            col = df_collected[x_col]
            if not (pd.api.types.is_numeric_dtype(col) or
                    pd.api.types.is_datetime64_any_dtype(col)):
                unique_vals = col.dropna().unique()
                n_unique = len(unique_vals)
                max_len = max((len(str(v)) for v in unique_vals), default=0)

                # Rotation only warranted for genuinely long labels.
                # Short labels (≤6 chars, e.g. ST codes "131", "1485") stay
                # horizontal even when numerous — reduce size instead.
                if max_len > 12:
                    x_kwargs = {"rotation": 45, "size": 8, "ha": "right"}
                elif max_len > 6:
                    x_kwargs = {"rotation": 35, "size": 9, "ha": "right"}
                elif n_unique > 12:
                    x_kwargs = {"size": 8}   # many short labels: shrink, no rotation
                elif n_unique > 6:
                    x_kwargs = {"size": 9}

                if x_kwargs:
                    rot = x_kwargs.get("rotation", 0)
                    print(f"Auto-adjusted x-axis: rotation={rot}°, "
                          f"size={x_kwargs['size']}, n_unique={n_unique}, max_len={max_len}")

        # --- Y-axis ---
        if y_col is not None and y_col in df_collected.columns:
            col = df_collected[y_col]
            # For categorical Y (e.g. horizontal bar charts)
            if not (pd.api.types.is_numeric_dtype(col) or
                    pd.api.types.is_datetime64_any_dtype(col)):
                unique_vals = col.dropna().unique()
                n_unique = len(unique_vals)
                max_len = max((len(str(v)) for v in unique_vals), default=0)
                if n_unique > 20 or max_len > 20:
                    y_kwargs = {"size": 7}
                elif n_unique > 12 or max_len > 12:
                    y_kwargs = {"size": 8}
            else:
                # Numeric Y: many unique values means densely packed tick labels
                n_unique = df_collected[y_col].dropna().nunique()
                if n_unique > 20:
                    y_kwargs = {"size": 7}
                elif n_unique > 12:
                    y_kwargs = {"size": 8}

            if y_kwargs:
                print(f"Auto-adjusted y-axis: size={y_kwargs['size']}, n_unique={n_unique}")

        if x_kwargs or y_kwargs:
            theme_kwargs = {}
            if x_kwargs:
                theme_kwargs["axis_text_x"] = element_text(**x_kwargs)
            if y_kwargs:
                theme_kwargs["axis_text_y"] = element_text(**y_kwargs)
            p = p + theme(**theme_kwargs)

        return p

    def _standardize_config(self, plot_config: Dict[str, Any], manifest_defaults: Dict[str, Any]) -> Dict[str, Any]:
        """ Standardizes high-level or legacy manifests into the mapping/layers spec. """
        import copy
        config = copy.deepcopy(plot_config)

        # Merge manifest-level defaults
        for k, v in manifest_defaults.items():
            if k not in config:
                config[k] = v

        # 1. Promote flat aesthetics to mapping if mapping is missing
        if 'mapping' not in config:
            mapping = {}
            # List of aesthetics to extract from top level
            possible_aes = ['x', 'y', 'color', 'fill',
                            'size', 'alpha', 'shape', 'label']
            for aes_key in possible_aes:
                if aes_key in config:
                    mapping[aes_key] = config[aes_key]

            if mapping:
                config['mapping'] = mapping

        # 2. Handle factory_id translation
        # Injects the base geom at position 0 if not already present, even when
        # additional layers (position, labs) are already declared in the manifest.
        factory_id = config.get('factory_id')
        if factory_id:
            base_geom = None
            if factory_id == "heatmap_logic":
                # Heatmaps use 'fill' for tiles; manifests may declare 'color'
                if 'mapping' in config and 'color' in config['mapping']:
                    config['mapping']['fill'] = config['mapping']['color']
                base_geom = {"name": "geom_tile", "params": {"color": "white", "size": 0.1}}
            elif factory_id == "bar_logic":
                if 'mapping' in config and 'y' in config['mapping']:
                    base_geom = {"name": "geom_col", "params": {}}
                else:
                    base_geom = {"name": "geom_bar", "params": {}}
            elif factory_id == "scatter_logic":
                base_geom = {"name": "geom_point", "params": {}}
            elif factory_id == "boxplot_logic":
                base_geom = {"name": "geom_boxplot", "params": {}}
            elif factory_id == "violin_logic":
                base_geom = {"name": "geom_violin", "params": {}}

            if base_geom:
                existing = config.get('layers', [])
                # Only prepend if the geom type is not already declared
                geom_names = {l.get('name') for l in existing}
                if base_geom['name'] not in geom_names:
                    config['layers'] = [base_geom] + existing

        return config

    def _apply_palette(
        self,
        p,
        palette_name: str,
        mapping_spec: dict,
        has_fill_scale: bool,
        has_color_scale: bool,
    ):
        """Inject a named palette as a plotnine fill/colour scale (BP-COLOR-3).

        Resolution:
        - Name found in self._palette_registry → scale_*_manual with the hex list.
        - Name not in registry → treat as a matplotlib palette name:
            Sequential/diverging names → scale_*_distiller (continuous-safe fallback).
            Otherwise → scale_*_brewer (categorical).
        - Only injects for aesthetics present in the mapping.
        - Never overwrites a scale already declared in the manifest layers.
        """
        uses_fill = "fill" in mapping_spec and not has_fill_scale
        uses_color = ("color" in mapping_spec or "colour" in mapping_spec) and not has_color_scale

        if not uses_fill and not uses_color:
            return p

        project_colors = self._palette_registry.get(palette_name)
        if project_colors:
            # Project palette — inject scale_*_manual
            if uses_fill:
                from plotnine import scale_fill_manual
                p = p + scale_fill_manual(values=project_colors)
                print(f"[VizFactory] Applied project palette '{palette_name}' → scale_fill_manual")
            if uses_color:
                from plotnine import scale_color_manual
                p = p + scale_color_manual(values=project_colors)
                print(f"[VizFactory] Applied project palette '{palette_name}' → scale_color_manual")
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
                    from plotnine import scale_fill_viridis_d, scale_color_viridis_d
                    if uses_fill:
                        p = p + scale_fill_viridis_d(option=palette_name)
                    if uses_color:
                        p = p + scale_color_viridis_d(option=palette_name)
                    print(f"[VizFactory] Applied viridis palette '{palette_name}'")
                except Exception as exc:
                    pe = PipelineError(
                        component="VizFactory",
                        problem=f"Viridis palette '{palette_name}' failed to apply: {exc}",
                        location="_apply_palette",
                        fix=f"Check that '{palette_name}' is a valid viridis option (viridis, plasma, magma, inferno, cividis).",
                        who="manifest_author",
                        category="visualization",
                        surface="plot_overlay",
                        severity="warning",
                        evidence={"palette_name": palette_name, "error": str(exc)[:200]},
                    )
                    print(pe.format())
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
                        problem=f"Palette '{palette_name}' not found in project registry or plotnine/RColorBrewer.",
                        location="_apply_palette",
                        fix=(
                            f"Check the palette name in the manifest. "
                            f"Valid project palettes: {list(self._palette_registry.keys()) or ['(none registered)']}. "
                            "Or use a matplotlib/RColorBrewer name such as 'Blues', 'Set1', 'viridis'."
                        ),
                        who="manifest_author",
                        category="visualization",
                        surface="plot_overlay",
                        severity="warning",
                        evidence={"palette_name": palette_name, "error": str(exc)[:200]},
                        reference="rules_viz_factory.md §6c",
                    )
                    print(pe.format())

        return p
