import polars as pl
from plotnine import ggplot, aes
from typing import Dict, Any, List
# Explicit imports to ensure registration occurs
from viz_factory.registry import get_component
from utils.errors import VisualizationError
import difflib

# @deps
# provides: class:VizFactory, method:render, method:_apply_palette
# consumes: libs/viz_factory/src/viz_factory/registry.py (PLOT_COMPONENTS via get_component)
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

    def render(self, df: Any, manifest: Dict[str, Any], plot_id: str):
        """
        Main entry point for rendering a single plot by ID from a manifest.
        Supports both Polars LazyFrame and DataFrame.
        """
        # Ensure it's a LazyFrame for consistent ADR-010 handling
        if isinstance(df, pl.DataFrame):
            df = df.lazy()

        raw_plot_config = manifest.get('plots', {}).get(plot_id)
        if not raw_plot_config:
            raise KeyError(f"Plot ID '{plot_id}' not found in manifest.")

        # 1. Standardize Manifest (Handle factory_id and flat aesthetics)
        plot_config = self._standardize_config(
            raw_plot_config, manifest.get('plot_defaults', {}))

        # 2. Validate Aesthetics (ADR-034)
        mapping_spec = plot_config.get('mapping', {})
        all_cols = df.columns
        for aesthetic, col_name in mapping_spec.items():
            if col_name not in all_cols:
                matches = difflib.get_close_matches(
                    col_name, all_cols, n=1, cutoff=0.6)
                tip = f"Ensure column '{col_name}' exists in the current dataset."
                if matches:
                    tip += f" Hint: Did you mean '{matches[0]}'?"
                raise VisualizationError(
                    f"Aesthetic '{aesthetic}' references unknown column '{col_name}'.",
                    tip=tip
                )

        # Initialize mapping (Agnostic Mapping)
        mapping = aes(**mapping_spec)

        # 2. Tier 3: Apply UI-driven Filters (Predicate Pushdown)
        # DEMO-4: read actual column dtype from the LF schema and coerce
        # string filter values when the column is numeric. The UI sends
        # string operands regardless of column type (selectize/text input).
        # Without coercion, polars rejects "2022" > Float64 column, etc.
        ui_filters = plot_config.get('filters', [])
        if ui_filters:
            print(
                f"  └── Tier 3 (Leaf): Applying {len(ui_filters)} UI filters...")
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

                # Scalar ops: coerce value to column dtype before compare.
                # Log when a string operand reaches a numeric column — the
                # filter widget should be emitting native numerics already
                # (UX-FILTER-1); a string here means a bypass we should fix.
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

        # 3. Instantiate the ggplot object & ADR-010: Hand-off to Pandas strictly at init.
        # We materialise here after all UI/Leaf filters are pushed down.
        p = ggplot(df.collect().to_pandas(), mapping)

        # 3. Apply Layers sequentially
        layers = plot_config.get('layers', [])
        applied_layers = []
        for layer_spec in layers:
            layer_name = layer_spec.get('name')
            layer_params = layer_spec.get('params', {})

            # Fetch the registered component
            component_func = get_component(layer_name)

            # Pipe the plot object through the component
            p = component_func(p, layer_params)
            applied_layers.append(layer_name)
            print(f"Applied layer: {layer_name}")

        # 4. Inject Defaults for missing layer categories
        # Theme: Manifest defaults or fallback
        if not any(l.startswith("theme_") or l.startswith("element_") for l in applied_layers):
            theme_name = plot_config.get('theme', _DEFAULT_THEME)
            try:
                theme_func = get_component(theme_name)
                p = theme_func(p, {})
                print(f"Applied default theme: {theme_name}")
            except:
                from plotnine import theme_bw
                p = p + theme_bw()
                print(f"Applied fallback theme: theme_bw")

        # Coord default: coord_cartesian
        if not any(l.startswith("coord_") for l in applied_layers):
            from plotnine import coord_cartesian
            p = p + coord_cartesian()
            print(f"Applied default layer: {_DEFAULT_COORD}")

        # Facet: Handle flat 'facet_by' or default
        if not any(l.startswith("facet_") for l in applied_layers):
            facet_col = plot_config.get('facet_by')
            if facet_col:
                from plotnine import facet_wrap
                p = p + facet_wrap(f"~{facet_col}")
                print(f"Applied facet_wrap: ~{facet_col}")
            else:
                from plotnine import facet_null
                p = p + facet_null()
                print(f"Applied default layer: {_DEFAULT_FACET}")

        # Labels — support both flat 'title' and structured 'labels' block
        # e.g. labels: {title: "...", x: "Year", fill: "Multiresistant"}
        labels_block = plot_config.get('labels', {})
        title = plot_config.get('title')
        if title and 'title' not in labels_block:
            labels_block['title'] = title
        if labels_block:
            from plotnine import labs
            p = p + labs(**labels_block)
            print(f"Applied labels: {list(labels_block.keys())}")

        # Guides — support structured 'guides' block
        # e.g. guides: {fill: {name: guide_legend, title: "Multiresistant"}}
        guides_block = plot_config.get('guides', {})
        if guides_block:
            from plotnine import guides, guide_legend, guide_colorbar
            guide_map = {}
            _guide_ctors = {"guide_legend": guide_legend, "guide_colorbar": guide_colorbar}
            for aes_key, guide_spec in guides_block.items():
                if isinstance(guide_spec, dict):
                    ctor_name = guide_spec.pop('name', 'guide_legend')
                    ctor = _guide_ctors.get(ctor_name, guide_legend)
                    guide_map[aes_key] = ctor(**guide_spec)
                elif guide_spec is False or guide_spec == "none":
                    guide_map[aes_key] = False
            if guide_map:
                p = p + guides(**guide_map)
                print(f"Applied guides: {list(guide_map.keys())}")

        # 5. Auto-adjust axis label orientation/size.
        # Per-axis guard: only skip an axis if the manifest already addressed it
        # via an explicit element_text layer targeting that axis specifically.
        manifest_axis_x_set = any(
            l.get("name") == "element_text" and
            l.get("params", {}).get("target", "").startswith("axis_text_x")
            for l in plot_config.get("layers", [])
        )
        manifest_axis_y_set = any(
            l.get("name") == "element_text" and
            l.get("params", {}).get("target", "").startswith("axis_text_y")
            for l in plot_config.get("layers", [])
        )
        p = self._auto_adjust_axis_labels(
            p,
            df_collected=p.data,
            x_col=None if manifest_axis_x_set else mapping_spec.get("x"),
            y_col=None if manifest_axis_y_set else mapping_spec.get("y"),
        )

        # 6. Palette injection (BP-COLOR-3)
        # Resolution: plot-level 'palette' > manifest 'plot_defaults.palette' > none.
        # _standardize_config already merged plot_defaults into plot_config, so a
        # manifest-level default is visible here as plot_config['palette'].
        palette_name = plot_config.get("palette")
        if palette_name:
            has_fill_scale = any(l.startswith("scale_fill_") for l in applied_layers)
            has_color_scale = any(
                l.startswith("scale_color_") or l.startswith("scale_colour_")
                for l in applied_layers
            )
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
                    print(
                        f"[VizFactory] WARNING: palette '{palette_name}' failed "
                        f"(scale_*_viridis_d): {exc}"
                    )
            else:
                try:
                    from plotnine import scale_fill_brewer, scale_color_brewer
                    if uses_fill:
                        p = p + scale_fill_brewer(palette=palette_name)
                    if uses_color:
                        p = p + scale_color_brewer(palette=palette_name)
                    print(f"[VizFactory] Applied brewer palette '{palette_name}'")
                except Exception as exc:
                    print(
                        f"[VizFactory] WARNING: palette '{palette_name}' not found in "
                        f"project registry or matplotlib. Check the palette name in the "
                        f"manifest. Valid project palettes: "
                        f"{list(self._palette_registry.keys()) or ['(none registered)']}"
                    )

        return p
