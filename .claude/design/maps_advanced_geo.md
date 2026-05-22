# Advanced Geospatial Visualization — Solution B (Real Geo)

**Status:** PROPOSAL — not scheduled. Companion to Solution A (shipped via `MAP-A-*` tasks).
**Author:** @dasharch
**Date:** 2026-05-22
**Scope:** True geometry-aware maps (projections, CRS, real boundaries) via `geopandas` + plotnine `geom_map`.

---

## 1. Why this document exists

The original `VIZ-GEOM-MAP-1` task was filed as *"blocked — plotnine has no native GeoDataFrame/spatial support."* **That premise is false.** Verified 2026-05-22 against the installed stack:

- plotnine **0.15.4** ships `geom_map` with `REQUIRED_AES = {'geometry'}` — it draws shapely geometries directly (the plotnine analogue of ggplot2 `geom_sf`).
- The registration is already half-written (commented out) at [geoms/core.py:822](../../libs/viz_factory/src/viz_factory/geoms/core.py#L822).
- `geom_polygon`, `coord_equal`, `coord_fixed` are **all registered already**.

Maps are therefore not blocked by the plotting library. The real question is **how geometry travels through a Polars/Parquet tabular pipeline** — a data-contract problem, not a rendering problem.

This split gives two solutions:

| | Solution A (separate — shipping now) | **Solution B (this doc)** |
|---|---|---|
| Geom | `geom_polygon` (registered) | `geom_map` (uncomment + wire) |
| Geometry as | x/y/group **numeric columns** | shapely `geometry` objects |
| New deps | none | geopandas + shapely (+ pyproj) |
| Projections / CRS | none (flat lat/long) | full |
| Pipeline impact | none | geometry-aware contract |
| ggplot2 analogue | `geom_polygon` + `map_data()` | `geom_sf()` |

Solution A covers country/county choropleths (the realistic AMR-surveillance need). Solution B is for when we genuinely need accurate projections, CRS reprojection, or spatial operations.

---

## 2. The core architectural problem

The data engine is tabular end-to-end: Polars `LazyFrame` → `sink_parquet` (Tier 1/2) → `scan_parquet` → `df.collect().to_pandas()` at [viz_factory.py:198](../../libs/viz_factory/src/viz_factory/viz_factory.py#L198) → plotnine.

Geometry does not fit this contract:

- **Polars** has no native geometry dtype.
- **Parquet** (as written by the engine today) has no geometry awareness — only GeoParquet does, and the engine does not produce it.
- **plotnine `geom_map`** needs a `geometry` aesthetic backed by shapely objects (i.e. a `GeoDataFrame`).

So the design decision is: **where does the geometry live, and at what point does it meet the tabular data?** Three sub-options below.

---

## 3. Sub-options for carrying geometry

### B1 — Sidecar GeoDataFrame, merged at render time (RECOMMENDED within B)

Geometry **never enters the Polars/Parquet contract**. It lives as a reference `GeoDataFrame` (one row per region, keyed by region name/code), loaded from a standard GeoJSON/shapefile asset. At render time:

1. Tabular data flows through Tier 1/2/3 as today → `df.collect().to_pandas()`.
2. VizFactory loads the referenced boundary `GeoDataFrame` (cached, like gallery assets).
3. The collected pandas frame is merged onto the GeoDataFrame on the region key → a `GeoDataFrame` carrying both `geometry` and the analytical columns (rate, count…).
4. The `geom_map` layer receives this GeoDataFrame as its `data=`.

```
Tier 3 leaf (tabular) ──┐
                        ├── merge on region_key ──► GeoDataFrame ──► geom_map(data=…, aes(fill=rate))
boundary GeoDataFrame ──┘   (at render time only)
```

- **Pros:** zero change to the data engine; geometry is a pure rendering concern; Tier 1/2/3 stay tabular and cache-friendly; predicate-pushdown filters still apply to the tabular side before the merge.
- **Cons:** geometry is not part of the audit/contract; the merge key must be clean (region-name reconciliation — note the TEST_LAB ID-reconciliation tool could help here); boundary asset is a separate provenance item.
- **Verdict:** the minimally-invasive path. Mirrors how `geom_map`'s own `data=` parameter is designed (a layer can carry its own GeoDataFrame independent of the plot's main data).

### B2 — WKB geometry column in Parquet

Store geometry as a Well-Known-Binary (`bytes`) column inside the normal Parquet. Reconstruct shapely objects in `render()` via `shapely.from_wkb`, wrap in a GeoDataFrame.

- **Pros:** geometry travels with the data through tiers; single artifact.
- **Cons:** Polars carries an opaque binary blob it cannot reason about; every wrangling action must avoid touching it; `to_pandas()` + WKB decode on every render; bloats Parquet; the "tabular contract" becomes a half-truth. Filters/joins on geometry are impossible in Polars.
- **Verdict:** rejected unless a future requirement forces geometry into the tier lifecycle.

### B3 — GeoParquet end-to-end

Use geopandas' GeoParquet reader/writer; make a parallel "geo tier" path.

- **Pros:** standards-based, full fidelity.
- **Cons:** forks the entire persistence layer; Polars cannot read/write GeoParquet natively; large new surface area; over-engineered for choropleths.
- **Verdict:** out of scope unless SPARMVET pivots to genuine GIS work.

---

## 4. Dependency plan (B1)

Add to `libs/viz_factory/pyproject.toml` as an **optional extra** (so the lib stays installable without geo for non-map deployments):

```toml
[project.optional-dependencies]
geo = ["geopandas>=1.0", "shapely>=2.0"]   # pyproj pulled transitively
```

- VizFactory imports geopandas **lazily** inside the `geom_map` handler — a plain (non-geo) install raises a clear `VisualizationError("geom_map requires the 'geo' extra: pip install viz_factory[geo]")` rather than an ImportError at module load.
- Keeps the Clear-Lines policy intact: geo deps belong to the Artist pillar only; the data engine never imports them.

---

## 5. Manifest format design (B1)

A map plot spec references a boundary asset and a join key, then maps `fill` to an analytical column:

```yaml
spec:
  target_dataset: amr_rate_by_county
  geo_source:                          # NEW block — Solution B only
    boundary_asset: "norway_counties"  # named reference in config/geo/boundaries.yaml
    region_key_data: "county_name"     # column in target_dataset
    region_key_geo: "NAME_1"           # column in the boundary GeoDataFrame
    crs: "EPSG:4326"                    # optional reprojection target
  mapping:
    fill: resistance_rate              # analytical column → choropleth colour
  layers:
    - name: geom_map
      params: {}
    - name: coord_equal                # or a projected coord once supported
      params: {}
    - name: scale_fill_continuous
      params: {palette: "viridis"}
```

- `geo_source` is a new optional spec block, parsed only when a `geom_map` layer is present.
- Boundary assets are registered centrally (`config/geo/boundaries.yaml`: name → path + default keys + provenance), resolved by the bootloader and injected into VizFactory (same pattern as palettes, ADR-081 §6a — never read from disk inside the library).
- Region-key reconciliation is the user's responsibility (clean join), aided by TEST_LAB's ID-reconciliation tool.

---

## 6. Rendering wiring (B1)

Single new branch in `VizFactory.render()`:

1. Detect a `geom_map` layer in the resolved config.
2. If present and `geo_source` set: load + cache the boundary GeoDataFrame; reproject if `crs` differs; merge the collected pandas frame onto it (left join, geo side as left to preserve all regions); pass the result as the layer `data`.
3. If `geom_map` present but geo extra missing → `VisualizationError` with install hint.
4. Predicate-pushdown filters continue to apply to the **tabular** side before the merge (so filtering by year/species still works; filtering by geometry does not — acceptable).

This is one localized change at the existing single render call site — it composes with the L1–L5 plot-config cascade (`plot_config_cascade.md`) because `geom_map` is just another layer.

---

## 7. Projection / CRS handling

- **v1:** support `coord_equal` (flat lat/long, equal aspect) — adequate for Norway and Europe at surveillance scale.
- **v2:** add a projected-coordinate option. plotnine has no `coord_sf`; the pragmatic route is to **reproject the GeoDataFrame** (geopandas `.to_crs(...)`) before handing to `geom_map`, so the geometry is already in projected units and `coord_equal` renders it correctly. CRS target comes from `geo_source.crs`.

---

## 8. Tradeoffs summary

| Concern | B1 sidecar | B2 WKB | B3 GeoParquet |
|---|---|---|---|
| Data-engine change | none | medium | large |
| Geometry in audit contract | no | yes | yes |
| Parquet size impact | none | high | high |
| Polars stays geometry-agnostic | yes | no (blob) | no |
| Filter by geometry | no | no (blob) | yes |
| Implementation cost | low | medium | high |
| Fit for choropleth | excellent | overkill | overkill |

---

## 9. Recommendation

If/when Solution A proves insufficient (need real projections or accurate boundaries beyond fortified polygons), implement **B1 (sidecar GeoDataFrame merged at render time)**:

- smallest blast radius — one render branch + one optional dep extra + one manifest block;
- the data engine and tier lifecycle are untouched;
- it is the natural use of `geom_map`'s own `data=` design.

B2/B3 are only justified if SPARMVET takes on genuine GIS requirements (spatial joins, geometry filtering, multi-layer cartography) — at which point this doc should be superseded by a dedicated ADR.

---

## 10. Open questions (resolve before scheduling B)

1. **Boundary asset governance** — where do boundary GeoJSON/shapefiles live, and how is provenance/licensing recorded? (Natural Earth is public domain; GADM is not redistributable.)
2. **Region-key reconciliation** — do we standardise on ISO codes for the join key to avoid name-matching pain? Can the TEST_LAB reconciler pre-clean region names?
3. **Gallery taxonomy** — does a choropleth get a new `family`/`pattern` axis value, or fold into `Comparison`/`Distribution`? (Same question blocks Solution A's gallery bundle — decide once for both.)
4. **Interactivity** — static PNG/SVG only (consistent with current export), or is any hover/zoom expected? (Current architecture is server-side static; interactive maps would be a much larger scope.)

---

## 11. Relationship to scheduled work

- **Solution A** (`MAP-A-*` in `tasks.md`) ships choropleths now with zero new deps — `geom_polygon` + a boundary-fortification asset script. It is the prerequisite learning step and may satisfy the real need entirely.
- **`VIZ-GEOM-MAP-1` / `GALLERY-MAP`** are re-pointed to this document as Solution B; they remain deferred (a deliberate architecture choice, not a library block).
- The commented-out `geom_map` at [geoms/core.py:822](../../libs/viz_factory/src/viz_factory/geoms/core.py#L822) must **not** be uncommented until Solution B is scheduled — registering it without the geo extra + render branch would surface a geom that errors on use.
