# Bioinformatics Visualization via R (ggtree & friends) — Possibilities

**Status:** EXPLORATORY — nothing decided. Feature-development discussion to return to.
**Author:** @dasharch
**Date:** 2026-05-22
**Related:** [`r_backend.md`](r_backend.md) (this is arguably the *strongest* motivating use case for an R backend), [`sankey_flow_geoms.md`](sankey_flow_geoms.md)

---

## 1. The question

Could R render the bioinformatics-specific plots that Python/plotnine cannot — phylogenetic trees (ggtree), tree-aligned metadata panels (ggtreeExtra), gene maps, sequence alignments — as a SPARMVET feature?

**Short answer: this is the clearest case for R interop.** Unlike Sankey (where Python has workable primitives), publication-quality annotated phylogenies have *no* Python equal. The phylogenetics literature states plainly that Python packages (ete3, toytree, Bio.Phylo) "cannot match the equivalents in R like ggtree." For a bacterial AMR surveillance tool, annotated trees are a core output, not a nice-to-have.

---

## 2. The R/Bioconductor ecosystem (all ggplot2-based)

| Package | What it does | SPARMVET relevance |
|---|---|---|
| **ggtree** | Visualise + annotate phylogenetic trees; extends ggplot2; stores tree + annotation in one `treedata` object | Core — strain/isolate phylogenies |
| **ggtreeExtra** | `geom_fruit()` aligns external data panels (heatmaps, bars) to tree tips in rectangular/circular/fan layouts | **Killer feature** — AMR gene presence/absence heatmap strips beside the tree |
| **treeio** | Read/write many tree formats (Newick, Nexus, BEAST, IQ-TREE, etc.) | Ingests upstream phylo pipeline output |
| **gggenes** | Gene arrow maps (operon / synteny structure) | Genomic context of resistance/virulence loci |
| **ggmsa** | Multiple sequence alignment visualisation | Alignment views alongside trees |

The canonical AMR-surveillance figure — a tree of isolates with tip colours by source/year and a heatmap strip of resistance-gene presence/absence — is `ggtree() + geom_tippoint() + ggtreeExtra::geom_fruit(geom_tile)`. This is exactly the user's domain (bacterial bioinformatics, AMR).

---

## 3. The architectural distinction that matters

**ggtree does NOT fit the generic "manifest spec = ggplot2 grammar → transpile a tidy frame" story** from `r_backend.md` §2. Its input is a **tree object** (phylo / treedata with topology), not a `target_dataset` tidy table. Its grammar operates on tree structure:

```r
ggtree(tree) + geom_tippoint(aes(color = source)) +
  geom_fruit(data = amr, geom = geom_tile, mapping = aes(y = isolate, x = gene, fill = present))
```

So bioinformatics viz is a **specialized renderer**, not a transpiler target. The right mental model is the **maps `geo_source` pattern** (`maps_advanced_geo.md`): a non-tabular asset (the tree file) + a tabular metadata table (the AMR/metadata frame), joined at render time. The tree is the "geometry"; the Tier 1/2/3 tabular data is the annotation.

This means:
- It rides on **Option A** of `r_backend.md` (narrow, opt-in R renderer for gaps) — *not* the generic dual backend.
- It is its own spec block and its own render path, distinct from the bar/point/box plots that plotnine handles.
- plotnine and ggtree coexist with no overlap — no dual-renderer-of-the-same-plot provenance problem.

---

## 4. How it would integrate (sketch — not a proposal)

**Input/data flow:**
- Tree file (Newick/Nexus) is an **asset** referenced by the manifest (like a boundary asset), parsed in R via `treeio`.
- Annotation comes from the normal pipeline: Tier 1/2/3 tabular data → Feather/Arrow → R (`arrow` package).
- R joins annotation onto tree tips by an isolate/sample key, renders via ggtree/ggtreeExtra, returns SVG/PNG bytes.

**Manifest spec sketch (a specialized `tree_plot` type):**

```yaml
spec:
  plot_type: tree            # NEW — signals the ggtree renderer, not plotnine
  tree_source:
    file: "isolates.treefile"   # Newick/Nexus asset
    format: "newick"
    tip_key: "isolate_id"        # tree tip label ↔ metadata key
  annotation_dataset: amr_by_isolate   # tabular Tier 1/2 frame (Arrow handoff)
  layers:
    - name: geom_tippoint
      mapping: {color: source}
    - name: geom_fruit          # ggtreeExtra panel
      geom: geom_tile
      mapping: {x: gene, fill: present}
  layout: rectangular           # or circular | fan
```

**Render path:** `Rscript render_tree.R --tree isolates.treefile --data amr.feather --spec spec.json --out tree.svg`, image bytes returned to the gallery/home theater. Same subprocess+Arrow mechanism as `r_backend.md` §4.

**Gating:** persona/deployment flag (`r_backend_enabled` or a finer `bioinformatics_viz_enabled`) so the R + Bioconductor footprint is only present where opted in.

---

## 5. Honest assessment of the Python alternative

| Tool | Verdict for SPARMVET |
|---|---|
| ete3 | Powerful for analysis; rendering is Qt-based, not grammar-of-graphics, awkward to integrate server-side and to style for publication |
| toytree | Minimalist; clean but limited annotation; no tree-aligned heatmap-panel equivalent of `geom_fruit` |
| Bio.Phylo | Basic; "has not been extended"; not publication-grade |
| **ggtree + ggtreeExtra** | The standard; tree-aligned metadata panels (`geom_fruit`) have no Python equal |

Building a `geom_fruit`-equivalent in plotnine would be a far larger effort than the Sankey geoms (tree topology layout + aligned multi-panel composition) — effectively reimplementing ggtree. **Not advisable.** If annotated trees are wanted, R is the pragmatic route.

---

## 6. Why this strengthens the R-backend case

| Use case | Python alternative exists? | R-backend justification |
|---|---|---|
| Sankey / alluvial | Partial (primitives, plotly) | Moderate |
| Networks | Partial (networkx + matplotlib) | Moderate |
| **Annotated phylogenies (ggtree)** | **No real equal** | **Strong** |
| Gene maps / MSA (gggenes/ggmsa) | Weak | Strong |

The bioinformatics families are where R interop pays off most. If the R-backend question (`r_backend.md`) is decided **yes**, this is likely the highest-value first target — higher than Sankey. If decided **no**, annotated trees simply remain out of scope for the app (users make them externally), because a plotnine reimplementation is not worth it.

---

## 7. Open questions

1. Are annotated phylogenies actually in scope for SPARMVET's outputs, or produced upstream by a separate phylo pipeline? (Determines whether this is in-app or not at all.)
2. Tree-file provenance — does the app ingest a tree asset, or compute trees? (Almost certainly ingest — tree-building is upstream.)
3. Which families for v1 — trees only, or trees + gene maps + MSA?
4. Flag granularity — one `r_backend_enabled`, or a dedicated `bioinformatics_viz_enabled`?
5. Bioconductor footprint in container (ggtree pulls a large dep tree) — acceptable given Eve's note that R-in-container is routine? Confirm for the specific Bioconductor weight.

---

## 8. What a spike would test (not scheduled)

1. `Rscript` + `treeio` reads a Newick file; `arrow` reads a polars-written Feather of isolate metadata.
2. Render one ggtree + `geom_tippoint` + `ggtreeExtra::geom_fruit` heatmap strip from SPARMVET-shaped inputs → SVG.
3. Confirm the tip-key ↔ metadata join works on real isolate IDs (ties into the TEST_LAB ID-reconciliation tool for key cleaning).
4. Measure Bioconductor container image size + cold render latency.

Outcome informs whether to fold bioinformatics viz into an R-backend ADR as the lead use case.
