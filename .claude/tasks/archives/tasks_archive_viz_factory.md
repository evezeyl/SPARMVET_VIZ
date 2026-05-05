# Archive: Viz Factory & Documentation Recovery (100% DONE)

### 🎨 Viz Factory: Implementation Trackers (ARCHIVE)

#### Geoms (geoms/)

- [x] geom_point: Basic scatter plots.
- [x] geom_line: Path/Time-series data.
- [x] geom_bar
- [x] geom_col: Categorical distributions and totals.
- [x] geom_histogram: Continuous frequency distributions.
- [x] geom_boxplot: Quartile summaries (requires stat_boxplot).
- [x] geom_violin: Density summaries (requires stat_ydensity).
- [x] geom_smooth: Regression lines and CI ribbons.
- [x] geom_density: 1D Kernel density estimation.
- [x] geom_errorbar
- [x] geom_pointrange: Uncertainty visualization (point + range).
- [x] geom_tile: Discrete heatmaps.
- [x] geom_raster: Continuous heatmaps.
- [x] geom_text
- [x] geom_label: Data annotation (with boxes).
- [x] geom_jitter: Avoiding overplotting.

#### Scales

- [x] `scale_color_gradient`: Two-color gradient (low-high)
- [x] `scale_color_gradient2`: Diverging three-color gradient (low-mid-high)
- [x] `scale_color_distiller`: ColorBrewer sequential/diverging palettes for continuous data
- [x] `scale_color_viridis_c`: Matplotlib Viridis/Magma/Inferno palettes (Perceptually Uniform)
- [x] `scale_color_cmap`: Any Matplotlib Colormap by name
- [x] `scale_color_discrete`: Default categorical color scale
- [x] `scale_color_brewer`: ColorBrewer palettes (Set1, Dark2, etc.) for categories
- [x] `scale_color_manual`: User-defined hex code mapping
- [x] `scale_color_viridis_d`: Discrete Viridis palettes
- [x] `scale_x_continuous`
- [x] `scale_y_continuous`
- [x] `scale_x_discrete`
- [x] `scale_y_discrete`
- [x] `scale_x_log10`
- [x] `scale_y_log10`
- [x] `scale_x_reverse`
- [x] `scale_y_reverse`
- [x] `scale_x_datetime`
- [x] `scale_y_datetime`
- [x] `scale_size_continuous`: Map data values to point size or line width
- [x] `scale_size_discrete`: Different sizes for categories
- [x] `scale_shape_discrete`: Mapping different point shapes to categories
- [x] `scale_alpha_continuous`: Variable transparency based on values
- [x] `scale_alpha_discrete`: Transparency levels for categories
- [x] `scale_linetype_discrete`: Different dash/line patterns for categories
- [x] `scale_color_identity`: Use data column strings as colors directly
- [x] `scale_alpha_identity`: Use data column values as transparency directly
- [x] `scale_fill_identity`: Use data column strings as fill colors directly
- [x] `scale_size_identity`: Use data column numeric values as sizes directly
- [x] `scale_shape_identity`: Use data column string values as shapes directly
- [x] `scale_linetype_identity`: Use data column values as linetypes directly

#### Themes (themes/)

- [x] `theme_gray`: The default Plotnine theme (gray background, white gridlines).
- [x] `theme_bw`: White background with a thin black border.
- [x] `theme_linedraw`: Black lines on a white background.
- [x] `theme_light`: Light gray gridlines on a white background.
- [x] `theme_minimal`: No background annotations, minimal gridlines.
- [x] `theme_classic`: Axis lines with no gridlines.
- [x] `theme_void`: A completely empty theme.
- [x] `theme_dark`: Dark background for high-contrast data visualization.
- [x] `theme_dashboard`: Optimized for Shiny integration (high-contrast, legible font scaling).
- [x] `theme_publication`: Journal-ready theme with specific DPI and font-weight presets.
- [x] `element_text`: Component for modifying text aesthetics (color, size, angle, etc.) via `theme_custom`.
- [x] `element_line`: Component for modifying axis lines and gridline aesthetics via `theme_custom`.
- [x] `element_rect`: Component for plot/panel backgrounds and borders via `theme_custom`.
- [x] `theme_legend_position`: Registered component to toggle legend placement (top, bottom, left, right, none).

#### Facets

- [x] `facet_wrap`: 1D ribbon of panels wrapped into 2D (Standard categorical splitting).
- [x] `facet_grid`: 2D grid of panels formed by the intersection of two variables.
- [x] `facet_null`: The default single-panel display (Internal reference).
- [x] `facet_scales`: Implementation of 'free', 'free_x', and 'free_y' scale behaviors.
- [x] `facet_space`: Support for 'fixed' vs 'free' panel sizing in grids.
- [x] `facet_labeller`: Integration of custom label formatting (inherited from Plotnine).
- [x] `facet_rows`: Shortcut component for vertical-only stacking.
- [x] `facet_cols`: Shortcut component for horizontal-only stacking.
- [x] `facet_margins`: Logic for displaying marginal totals in grid layouts.

#### Coordinates (coords/)

- [x] `coord_cartesian`: The default Cartesian coordinate system (Standard x-y).
- [x] `coord_flip`: Cartesian coordinates with x and y flipped (Essential for horizontal bar charts).
- [x] `coord_fixed`: Cartesian coordinates with a fixed aspect ratio (Ensures 1 unit on x = 1 unit on y).
- [x] `coord_polar`: [DEFERRED - FEATURE NOT YET IMPLEMENTED IN PLOTNINE] Not in current source build.
- [x] `coord_trans`: Cartesian coordinates with arbitrary transformations (e.g., log, square root) applied to the axes.
- [x] `coord_equal`: Shortcut for `coord_fixed` with a 1:1 ratio.
- [x] `coord_lims`: Component for strictly enforcing axis limits at the coordinate level (prevents data clipping seen in scales).

#### Positions

- [x] `position_identity`: Default positioning; places objects exactly where the data dictates (may cause overlapping).
- [x] `position_stack`: Stacks objects on top of each other (Essential for stacked bar charts).
- [x] `position_fill`: Stacks objects and standardizes height to 100% (Essential for proportional bar charts).
- [x] `position_dodge`: Places objects side-by-side (Essential for grouped bar charts).
- [x] `position_dodge2`: Enhanced dodging for variable widths (Works with boxplots).
- [x] `position_jitter`: Adds a small amount of random noise to points to reveal overplotted data.
- [x] `position_jitterdodge`: Combines jittering and dodging (Ideal for points overlaid on boxplots).
- [x] `position_nudge`: Shifts points by a specific fixed distance (Useful for moving text labels away from points).

#### Guides

- [x] `guide_legend`: Standard discrete legend for scales (color, fill, shape, etc.).
- [x] `guide_colorbar`: Continuous color scale display (also known as `guide_colourbar`).
- [x] `guide_none`: Component to explicitly suppress a specific guide.
- [x] `guide_title`: Implementation for overriding scale titles and alignment within the guide.
- [x] `guide_label`: Support for toggling labels, setting rotation, and defining fonts.
- [x] `guide_direction`: Logic for 'horizontal' vs 'vertical' guide orientation.
- [x] `guide_reverse`: Functionality to reverse the order of items or the colorbar direction.
- [x] `guide_nrow` Controls for wrapping legend items into rows.
- [x] `guide_ncol`: Controls for wrapping legend items into columns.

#### Stats

- [x] Important stats are implemented in the geoms directory.
- [x] `stat_count`: Calculates the number of cases at each x position (Essential for bar charts).
- [x] `stat_bin`: Bins continuous data into ranges and counts cases (Essential for histograms).
- [x] `stat_identity`: Leaves the data as is (Default for many geoms like `geom_point`).
- [x] `stat_summary`: Summarizes y values at unique x values (e.g., mean, median, min, max).
- [x] `stat_boxplot`: Computes the components of a standard boxplot (quartiles, whiskers, outliers).
- [x] `stat_ydensity`: Computes a 1D kernel density estimate (Essential for violin plots).
- [x] `stat_smooth`: Aids in seeing patterns in the presence of overplotting (Regression/LOESS).
- [x] `stat_density`: Computes 1D kernel density estimates for area plots.
- [x] `stat_qq`: Calculates values for quantile-quantile plots.
- [x] `stat_ecdf`: Computes the empirical cumulative distribution function.
- [x] `stat_unique`: Removes duplicate observations (Useful for cleaning data at the plot level).
- [x] `stat_function`: Computes y values from a user-defined function across an x range.

#### LAST CHECK

- [x] FAILED VERIFICATIONS - RESOLVED: (scale_color_cmap, facet_labeller, stat_ecdf, stat_function).
- [x] DEFERRED CONFIRMED (NOT IN PLOTNINE BUILD): (coord_polar, guide_bins, guide_ticks).
- [x] Layer omission defaults implemented in `VizFactory (viz_factory.py)`.
- [x] `bulk_debug_viz_factory_layers.py` created at `libs/viz_factory/tests/`.
- [x] Documentation updated: `developer_how_to.qmd` now documents both bulk and single runners.
- [x] Documentation updated: `visualisation_factory.qmd` and `viz_factory_rationale.qmd` updated with DEFERRED items.

## 📘 Documentation Recovery (DONE)

- [x] **Mermaid Sync & Relocation**: Moved .mmd files to local directories.
- [x] **Broken Link Reconciliation**: Fixed guide/ into workflows/ paths.
- [x] **Aesthetic Overhaul**: Standardized high-contrast technical theme for all diagrams.
- [x] **Quarto Master Alignment**: Updated _quarto.yml with full chapter list.
