# Custom Flow & Network Geoms — plotnine Extension (GALLERY-FLOW)

**Status:** PROPOSAL — Sankey deferred; design recorded so it is build-ready when scheduled.
**Author:** @dasharch
**Date:** 2026-05-22
**Tracks:** `GALLERY-FLOW` (tasks.md)
**Nothing is locked.** This is exploratory feature-development discussion. The leaning expressed 2026-05-22: *if* flow geoms are built in the plotnine path, they should be **homogeneous with the spirit of plotnine** — authored as real plotnine geoms (§2), not faked with a precompute hack and not delegated to an external renderer as the primary path. Whether the plotnine path is taken at all depends on the R-backend question (§7), which is also undecided.

---

## 1. What this covers

High-level "flow" and "network" visual families that plotnine does **not** ship:

- **Sankey / alluvial** (stage nodes + flowing ribbons) — the primary target.
- **Network / node-link** graphs (nodes + edges with a computed layout) — secondary.

plotnine *does* ship the low-level primitives (`geom_segment`, `geom_path`, `geom_polygon`, `geom_rect`, `geom_ribbon` — all registered in VizFactory). What is missing is a high-level geom that computes the flow/layout geometry for the user.

---

## 2. The leaning (if the plotnine path is taken): real custom geoms

End state would be a registered `geom_sankey` (and later `geom_alluvial`, `geom_net`) that a manifest author uses as one layer:

```yaml
layers:
  - name: geom_sankey
    params: {flow_alpha: 0.5, node_width: 0.04}
```

Not: hand-authored polygon-vertex tables (the precompute-only approach was rejected — clunky authoring, not homogeneous with the rest of the grammar).

This is a deliberate **extension beyond** the ADR-036 Artist Parity Mandate. ADR-036 targets parity with *plotnine*; these geoms do not exist in plotnine, so they are net-new components. **Schedule a one-line ADR-036 amendment** when this is built, so a future parity audit does not flag `geom_sankey` as a non-plotnine stray and try to remove it.

---

## 3. The hard constraint: port the math, rewrite the draw

ggplot2 reference packages (ggalluvial, ggsankey, ggsankeyfier) are the *spec and the algorithm* source — **not** copy-paste source. Confirmed against the installed stack (2026-05-22):

- plotnine renders with **matplotlib**: `geom_polygon.draw_group` builds a `matplotlib.collections.PolyCollection` against an `Axes`. R's geoms render with **grid grobs**. The two draw layers are not interchangeable.

| ggalluvial / ggsankey layer | Reuse path in plotnine |
|---|---|
| `setup_data` / `StatStratum` / flow coordinate math (ribbon x-spline control points, node rectangles, bump curves) | **Port as algorithm** → a plotnine `stat` subclass (`compute_group` / `compute_panel`). Pure data→coordinates; numpy/polars. The reusable, testable core. |
| `GeomFlow` / grid grob draw calls | **Rewrite** against matplotlib in the geom's `draw_group` (PolyCollection for ribbons, rectangles for nodes). |

So "we have ggplot2 as the example" is correct — for the **math and the visual contract**. The rendering is new code.

### plotnine extension API (confirmed present)

- `geom` subclass hooks: `setup_data`, `draw_group`, `draw_panel`, `draw_legend`.
- `stat` subclass hooks: `compute_group`, `compute_panel`, `setup_data`, `setup_params`.

A custom geom is therefore: a `stat` (the ported math) + a `geom` (matplotlib draw) + a `@register_plot_component` wrapper with a `ui_schema` (so it appears in the Blueprint IDE picker like every other geom).

---

## 4. Upstream signal & contribution opportunity

plotnine issue [#433 "sankey plot"](https://github.com/has2k1/plotnine/issues/433) is **open, filed 2020-08, last touched 2022, labelled `Feature`, 1 comment**. It is a *stale request*, not active roadmap work.

Implication: this is unlikely to land in plotnine soon on its own. If SPARMVET builds `geom_sankey` cleanly in plotnine's idiom (proper `stat` + `geom`), the `stat`/`geom` pair is a candidate **upstream contribution** — issue #433 is the ready-made home for a PR. Worth keeping the implementation free of SPARMVET-specific coupling so it could be donated. (Decision deferred — note only.)

---

## 5. Build path: math-first, then wrap (even though the end state is a geom)

The end state is a custom geom, but the build order still isolates the math:

1. **Coordinate engine first** — implement the ribbon/node/layout math as a standalone, pure function (input: edge/stage table; output: vertex/segment coordinate frame). Unit-test it on a TSV via the 1:1:1 evidence loop — no plotnine internals involved, fully verifiable in isolation.
2. **Wrap in a `stat`** — `compute_group` calls the coordinate engine.
3. **Author the `geom`** — `draw_group` consumes the stat output, emits matplotlib artists.
4. **Register** via `@register_plot_component("geom_sankey", ui_schema={...})` + a gallery bundle.

Rationale: the coordinate math is the risky, value-dense part; testing it standalone de-risks the whole feature and keeps the option of a precompute fallback or upstream donation open. The geom becomes a thin, well-understood wrapper over proven math.

---

## 6. Scope (when scheduled)

| Geom | Math source (port from) | Draw primitive | Priority |
|---|---|---|---|
| `geom_sankey` | ggsankey / ggsankeyfier | PolyCollection ribbons + node rects | First |
| `geom_alluvial` | ggalluvial `StatStratum`/`StatAlluvium` | same family | Second |
| `geom_net` (node-link) | igraph/networkx layout algorithm → x/y | `geom_segment` edges + `geom_point` nodes | Later / maybe |

`geom_curve` is **absent** in plotnine 0.15.4 — curved edges use computed `geom_path` points, not a curve geom.

For `geom_net`: graph layout (force-directed, etc.) needs either `networkx` (NOT installed) or a hand-roll on `scipy` (installed). Decide the dependency before starting network charts; Sankey needs neither (its math is deterministic interpolation).

---

## 7. The strategic dependency — decide the R-backend question FIRST

There is an open strategic question (raised 2026-05-22): **should the app gain an alternate R/ggplot2 rendering backend?** See [`r_backend.md`](r_backend.md) (exploratory — nothing decided).

This directly affects whether the work in this document should happen at all:

- An R/ggplot2 backend would provide **ggalluvial, ggsankey, ggraph, and sf maps natively** — for free, mature, maintained.
- If that backend is adopted, reimplementing `geom_sankey` in plotnine is **largely wasted effort** (you would have the real ggalluvial).
- If it is *not* adopted (e.g. R-in-container deployment footprint is judged too heavy for Galaxy/IRIDA portability), then the custom-plotnine-geom path in this document is the right route.

**Therefore: do not start building `geom_sankey` until the R-backend question is resolved.** The two are partial substitutes. This dependency is the main reason Sankey stays deferred beyond "just not now."

---

## 8. Open questions

1. R-backend decision (§7) — the gating one.
2. If plotnine route: donate `geom_sankey` upstream (issue #433) or keep in-tree?
3. Gallery taxonomy — Sankey/alluvial `family` is `Part-to-Whole` or `Evolution`? (Shared with the maps taxonomy question.)
4. `geom_net` dependency — add `networkx`, or hand-roll layout on `scipy`?

---

## 9. Proposed tasks (deferred — do not schedule before §7 resolves)

- **FLOW-MATH-1** `[opus/high]`: Port Sankey/alluvial coordinate math from ggsankeyfier/ggalluvial into a standalone, unit-tested pure function (edge/stage table → vertex frame). 1:1:1 evidence loop on a TSV. No plotnine internals.
- **FLOW-GEOM-SANKEY-1** `[opus/high]`: Wrap FLOW-MATH-1 in a plotnine `stat` + `geom` (matplotlib `draw_group`); register `geom_sankey` with `ui_schema`; gallery bundle + preview PNG.
- **FLOW-ADR-1** `[sonnet/low]`: One-line ADR-036 amendment — custom flow/network geoms are a sanctioned extension beyond plotnine parity (so audits do not remove them).
- **FLOW-NET-1** `[opus/high]` `[later]`: `geom_net` node-link graphs — pending the networkx-vs-scipy dependency decision.

All gated on the R-backend strategic decision (§7).
