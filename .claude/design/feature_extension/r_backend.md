# R / ggplot2 Rendering Backend — Possibilities

**Status:** EXPLORATORY — nothing decided. A "possibilities" doc to return to for further discussion, not a proposal.
**Author:** @dasharch
**Date:** 2026-05-22
**Related:** [`bioinformatics_viz.md`](bioinformatics_viz.md) (**the strongest motivating use case** — ggtree annotated phylogenies have no Python equal), `sankey_flow_geoms.md` (§7 gates Sankey work on this question), `../../maps_advanced_geo.md` (sf maps would come free with an R backend)

---

## 1. The question

Some colleagues at the institution use R. Could SPARMVET gain an alternate VizFactory that leverages R/ggplot2 — and how feasible is wiring Python↔R into the app?

Short answer: **technically very feasible, and the architecture fits more naturally than usual** — but it is a strategic fork with provenance and maintenance consequences worth thinking through. This doc lays out the options without choosing.

---

## 2. Why it fits unusually well: the manifest spec *is* ggplot2's grammar

SPARMVET plot specs are already grammar-of-graphics: `mapping:`, `layers: [geom_*]`, `scale_*`, `theme_*`, `facet_by`. That is **ggplot2's own vocabulary** — plotnine is just the Python port of ggplot2. So a second backend is not a parallel authoring model; it is a **transpiler**:

```
                  ┌─► plotnine            (Python path, today)
manifest spec ────┤
                  └─► ggplot2 code string ─► R render ─► image   (R path, possible)
```

One manifest, two possible renderers. `VizFactory` is already an abstraction (`render(df, plot_config) -> image`), so an `RVizFactory` honoring the same contract is conceivable without touching the authoring layer.

---

## 3. Two motivations — separate them before scoping

The ask "leverage R" can mean two different things with different solutions:

| Motivation | What it really needs | Solution category |
|---|---|---|
| **(a) Colleagues author in R** and want their ggplot2 recipes to run in the app | Accept raw ggplot2 snippets as an input | Ingestion / escape-hatch (see Option C) |
| **(b) Want R-only geoms / fidelity** (ggalluvial, ggsankey, ggraph, sf maps) that plotnine lacks | An R rendering path for specific chart families | Backend (see Option A / B) |

Worth confirming which one is actually driving the interest — they lead to different builds.

---

## 4. Interop mechanism — and the one to avoid

The data handoff is **already solved**: the engine materializes Tier 1/2/3 to **Parquet/Arrow**, which R reads natively via the `arrow` package (near zero-copy). No new serialization needed — Arrow is the bridge.

| Mechanism | How | Verdict |
|---|---|---|
| **rpy2** (embed R in-process) | R interpreter inside the Python process | **Avoid as primary.** R is single-threaded with global state; embedding inside Shiny-Python's async multi-session server is not thread-safe and is fragile under concurrency. |
| **Subprocess `Rscript` + Arrow/Feather** | Write data to Feather, invoke `Rscript render.R --data … --spec … --out plot.svg`, read image back | **Cleanest fit.** Full process isolation, no shared R state, language-agnostic, robust. Cost: process-spawn latency per render. |
| **Plumber microservice** (R "plot server") | Long-lived R service; app POSTs spec + data ref, gets image | Best if it must scale; warm R process avoids spawn cost. Cost: two services to deploy/monitor. |

**Lean: subprocess `Rscript` + Arrow** for a first version (simple, isolated); promote to a plumber service only if render latency becomes a problem.

---

## 5. Three architectural options

### Option A — Narrow opt-in R renderer for the gaps (lean for a *first* version)

R renders **only** the chart families plotnine genuinely can't do well — Sankey/alluvial (ggalluvial/ggsankey), networks (ggraph), real projected maps (sf). plotnine remains the default for everything else.

- **Pros:** R's mature geoms for free; no dual-renderer-of-the-same-plot provenance problem (R only renders what Python can't); R dependency only where opted in.
- **Cons:** two renderers coexist (but for disjoint plot sets); a manifest may need both R and Python available if it mixes families.
- **Gated behind:** a persona/deployment flag (e.g. `r_backend_enabled`) so R is present only where wanted.

### Option B — Full alternate `RVizFactory` backend (transpile everything)

Every plot spec can render through either backend; deployment or persona chooses.

- **Pros:** maximal flexibility; R-native output for those who prefer ggplot2 fidelity throughout.
- **Cons:** **dual-renderer provenance hazard** — two renderers of the *same* plot can diverge; export must record which backend produced each figure; you maintain and test two full paths (parity bugs). Heaviest option.

### Option C — ggplot2-snippet escape hatch (ingestion, not a backend)

Accept a raw ggplot2 code block in a manifest/recipe (analogous to the T3 `developer_raw_yaml` escape hatch), rendered via `Rscript`. Serves motivation (a) directly.

- **Pros:** lowest architectural commitment; meets "I wrote this in R, just run it"; no transpiler.
- **Cons:** breaks the declarative-spec model (arbitrary R code, not introspectable by Blueprint); a security/sandbox concern (executing user R); not portable to the form-driven IDE.

These are not mutually exclusive — A + C is a coherent combination (gap-filler backend *plus* an R escape hatch).

---

## 6. Strategic connection: this gates the custom-geom work

An R backend would deliver **ggtree/ggtreeExtra (annotated phylogenies — no Python equal; see [`bioinformatics_viz.md`](bioinformatics_viz.md)), ggalluvial, ggsankey, ggraph, and sf maps natively** — mature and maintained. The bioinformatics families are the strongest justification; the flow/network ones make the custom-plotnine-geom effort in `sankey_flow_geoms.md` (porting ggalluvial's math into a matplotlib `draw_group`) **partly redundant**.

The two are **partial substitutes.** Deciding the R-backend direction should therefore come *before* investing opus-level effort in reimplementing flow/network/map geoms in plotnine. This is the main reason the Sankey tasks are gated on this question.

| If the choice is… | Then for flow/network/maps… |
|---|---|
| R backend (Option A) | use ggalluvial / ggraph / sf — skip custom plotnine geoms |
| No R backend | build custom plotnine geoms (`sankey_flow_geoms.md`) + Solution-A choropleths |

---

## 7. Costs & constraints (for the future discussion)

- **Deployment footprint.** An R backend needs R + ggplot2 + arrow (+ ggalluvial/sf as used) wherever it runs. *Eve's steer (2026-05-22): R-in-container is routine in our environment — this is a smaller concern than first weighted. Parked as "another day" discussion.* Still worth a line in any eventual ADR for Galaxy/IRIDA portability expectations.
- **Provenance / audit.** SPARMVET is a reproducibility tool. Any figure must record which backend rendered it (manifest already hashed; add a `render_backend` field to the export report). Option A avoids same-plot divergence; Option B does not.
- **Concurrency.** Confirms the rpy2-avoidance: use process/service isolation, not in-process embedding.
- **Clear-Lines fit (ADR-011/016).** An R backend belongs to the Artist pillar. Cleanest placement: a `viz_factory` optional extra (`viz_factory[r]`) or a sibling lib `libs/viz_factory_r/`, with R deps lazily imported and a clear error when absent — never imported by the data engine.
- **IDE introspection.** A transpiler backend (A/B) can still feed the Blueprint form catalog (the spec is the same grammar). A raw-snippet escape hatch (C) cannot — it is opaque to the form builder.

---

## 8. Open questions

1. Which motivation drives the ask — author-in-R (C) or R-only geoms (A/B)?
2. If a backend: Option A (gap-filler) or Option B (full dual)? A is far lower risk.
3. Transpiler scope — which geoms/scales/themes must map to ggplot2 for v1?
4. Provenance — add `render_backend` to the export report and session ghost?
5. Placement — `viz_factory[r]` extra vs a separate `libs/viz_factory_r/`?
6. Decide *before* scheduling any `FLOW-*` custom-geom task (§6).

---

## 9. What a spike would test (not scheduled)

A half-day spike to de-risk, before any commitment:

1. `Rscript` reads a Feather file written by polars (`arrow` round-trip fidelity — dtypes, categoricals).
2. A trivial transpile: one SPARMVET bar-plot spec → ggplot2 code → PNG/SVG, compare visually to the plotnine render.
3. One ggalluvial Sankey rendered from a SPARMVET-shaped edge table — confirm the "free Sankey" claim end-to-end.
4. Measure subprocess render latency (informs subprocess-vs-plumber).

Outcome of the spike would inform whether to write a real ADR + proposal.
