# Design: Canonical Plot Model & BLUEPRINT Authoring Seam
# Tracks: BP-PLOT-MODEL-1 (foundation), BP-COMPONENT-FORMS-1 (sits on top)
# Status: DESIGN — drafted 2026-05-20. Authority: @dasharch.
# Companion: .claude/design/plot_config_cascade.md (the RENDER side; this is the AUTHORING side)
# Companion ADRs: ADR-083 (this model), ADR-082 (BLUEPRINT feature set), ADR-081 (palette/cascade), ADR-036 (Artist parity)

---

## 0. TL;DR

A plot has exactly **one** internal representation in code: a **canonical grammar-of-graphics model** —
a data mapping plus an ordered list of layers, where the primary geom is just the first layer. This is
what `plotnine` itself models (`ggplot(df, aes(...)) + geom_*() + scale_*() + ...`), and it is already
what the render resolver produces internally.

The legacy manifest keys — `factory_id`, flat `x:`/`y:`/`fill:` — are **input sugar**, not part of the
model. A single seam, `normalise_plot_spec()`, converts sugar → canonical at the front door. Everything
downstream (rendering today, BLUEPRINT authoring tomorrow) operates on the canonical model only.

Because BLUEPRINT authors the **same** canonical model the renderer consumes, the two can never drift.
HOME stays on its narrow L5 `aesthetic_override` path (ADR-082 boundary). The render cascade
(plot_config_cascade.md) merges everything. This document defines that model, the seam, and how HOME
and BLUEPRINT each use it.

---

## 1. Why this exists (the problem)

Today a plot spec mixes two abstraction levels (verified in real manifests, e.g.
`config/manifests/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml`):

```yaml
factory_id: "boxplot_logic"   # primary geom HIDDEN behind a chart-type id
target_dataset: "FastP"
x: "sample_id"                # mapping is FLAT
y: "total_reads"
title: "Total Reads by Sample (QC)"
# (many specs have no `layers:` at all — they rely on factory_id + auto-everything)
```

Consequences:

- **The primary geom and the mapping are not layers.** A layer-parser sees neither. So "add one layer at
  a time" and "load a plot and edit it" cannot work uniformly — the geom and axes are invisible to the
  layer model.
- **`factory_id` is a vestige.** It comes from the original Visualization Factory / `draw_plot(df,x,y,color)`
  pattern (dasharch.md §5), a coarse "pick a chart type" idea that predates the grammar-of-graphics
  `layers:` system (ADR-036) and now coexists awkwardly with it. `plotnine` has no such concept.
- **Round-trip is lossy.** `factory_id → geom` is one-way; on save you cannot tell whether a `geom_col`
  came from `factory_id: bar_logic` or an explicit layer.

The fix is **not** a render-path redesign. The render path already normalises this away. The fix is to
(a) name the canonical model explicitly, (b) make the normaliser a shared public seam, and (c) have
BLUEPRINT author the canonical model directly.

---

## 2. The canonical plot model (the single code-level truth)

A plot, in code, is this dict. Nothing else is "a plot."

```python
{
    "target_dataset": str,            # which assembled collection feeds this plot
    "mapping":        dict[str, str], # aesthetic -> column   (the plotnine aes())
    "layers":         list[Layer],    # ORDERED; layers[0] is the primary geom
    "theme":          str | None,     # plot-level scalar (a registered theme component)
    "facet_by":       str | None,     # plot-level scalar
    "palette":        str | None,     # plot-level scalar (resolved by _apply_palette)
    "labels":         dict,           # {title, x, y, fill, ...}  -> labs()
    "guides":         dict,           # legend/colorbar config
    "_meta":          dict,           # PRESERVED passthrough: taxonomy + unknown keys (see §6)
}

# Layer:
{
    "name":    str,    # a registered component: geom_*, stat_*, scale_*, coord_*,
                       #                          facet_*, theme_*, guides, labs
    "params":  dict,   # component params (the same 8-widget ui_schema params)
    "comment": str,    # free-text intent (BP-COMMENTS-1); preserved, never sent to plotnine
}
```

Key properties:

- **The geom is `layers[0]`** — a layer like any other. There is no special "geom slot."
- **`mapping` is explicit** — never flat top-level `x:`/`y:` in the canonical form.
- **Plot-level scalars** (`theme`, `facet_by`, `palette`) stay scalar because the cascade treats them as
  winner-takes-all keys (plot_config_cascade.md §2). A `theme_*` *layer* and the `theme:` scalar both
  resolve to the same effective theme via dedup; authors may use either, but BLUEPRINT writes the scalar
  for plot-level intent and a `theme_*` layer only when a layer-position matters.
- **`_meta`** carries everything the model does not interpret (gallery taxonomy `family`/`pattern`/
  `difficulty`, author notes, future keys) so round-trip is lossless.

This mirrors `plotnine` exactly: `mapping` = `aes()`, `layers` = the `+ geom/scale/...` chain.

---

## 3. The shared seam — `normalise_plot_spec` / `serialise_plot_spec`

One pair of pure functions in `libs/viz_factory/src/viz_factory/plot_config_resolver.py` is the **single
source of truth** for "raw manifest spec ⇄ canonical model." Both the renderer and BLUEPRINT use it, so
they cannot diverge.

```python
def normalise_plot_spec(raw_spec: dict) -> dict:
    """Sugar -> canonical. Promote `_normalise_spec` (currently private, line 152) to public.

    - flat x/y/fill/color/...  -> mapping  (if `mapping` absent)
    - factory_id               -> prepend the mapped base geom as layers[0]  (legacy read only)
    - collect unknown/taxonomy keys into `_meta`
    Idempotent: normalise(normalise(x)) == normalise(x).
    """

def serialise_plot_spec(canonical: dict) -> dict:
    """Canonical -> YAML-ready dict (the inverse; NEW).

    - emit explicit `mapping:` + `layers:` (geom as layers[0])
    - NEVER emit factory_id or flat aesthetics (canonical is plotnine-faithful)
    - re-attach `_meta` keys verbatim
    Round-trip law:  serialise(normalise(raw)) is render-equivalent to raw  (see §7 truth table).
    """
```

- The renderer's `resolve_plot_config()` already calls `_normalise_spec` as L4 step 0
  (plot_config_cascade.md §9). Promotion to `normalise_plot_spec` is a rename + export; behaviour
  unchanged.
- `serialise_plot_spec` is new — it is the missing inverse that makes BLUEPRINT commit lossless.

---

## 4. How BLUEPRINT works (the authoring side)

BLUEPRINT authors **L4** (the manifest plot spec) and **L2** (`plot_defaults`). It operates exclusively on
the canonical model via the seam.

| Step | Mechanism |
|---|---|
| **Load** | On selecting a `plot_spec` component: `normalise_plot_spec(raw)` → canonical. Populate (a) the **mapping form** from `canonical["mapping"]`, (b) the **logic stack** from `canonical["layers"]` as layer nodes (geom included). |
| **Edit a layer** | Click a layer node → the shared 8-widget form opens, driven by `COMPONENT_SCHEMAS[node.name]`. (This is BP-COMPONENT-FORMS-1 — now coherent because the geom is a layer too.) |
| **Add a layer** | Component picker filtered by `context: ["plot"]` → `add_node` appends a layer node `{name, params:{}, comment:""}` and opens its form (Add==Edit, ADR-082 §5.1). |
| **Mapping form** | A small dedicated form (NOT the component picker): column pickers for `x`, `y`, `fill`, `color`, `facet_by`. Mapping is `aes()`, not a component — it needs its own widget set. |
| **Reorder** | Layer order is the plotnine `+` order. Drag/reorder updates `canonical["layers"]` order. |
| **Commit** | `serialise_plot_spec(canonical)` → write the plot spec file's `spec:` block (its `mapping:` + `layers:`). **Never `wrangling.tier3`** (that legacy dump is the bug fixed here — see §8). |

**Starter templates (replaces `factory_id` UX).** "Pick a chart type to begin" survives as a BLUEPRINT
*template*, not a stored manifest key: choosing "Bar chart" seeds `layers=[{name: geom_col}]` + empty
mapping slots. The template is authoring-time sugar; what gets stored is the explicit canonical model.

---

## 5. How HOME works (and why the boundary holds)

HOME does **not** author L4 layers. Per ADR-082 §4, HOME T3 is a *Publication Finisher*, locked to
filters / exclusions / column-drops / `aesthetic_override`. It authors **L5** — a narrow, fixed-schema
override (plot_config_cascade.md §6): `fill_color` ⊕ `fill_palette`, `color`, `alpha`, `shape`, `size`,
`theme`. Session-only, never written to the manifest.

The render cascade merges them: **L4 (BLUEPRINT, persistent) + L5 (HOME, session) → one layer list → one
plot** (plot_config_cascade.md §2). They never compete for authorship; they layer.

**Future-proofing.** If HOME ever needs to add a real layer (today out of scope; would need a superseding
ADR), the cascade's append-then-dedupe (plot_config_cascade.md §4) already accommodates an L5-contributed
layer. So holding the narrow boundary now costs nothing later.

**Why both work efficiently:** one canonical model; one normaliser; render = cascade L1–L5; BLUEPRINT
emits canonical L4; HOME emits narrow L5. BLUEPRINT cannot produce anything the renderer can't consume,
because it serialises the very model the renderer normalises to.

---

## 6. Lossless round-trip rules

`serialise(normalise(raw))` must be render-equivalent to `raw`. Rules:

1. **Preserve `_meta`.** Unknown + taxonomy keys (`family`, `pattern`, `difficulty`, author notes) are
   carried in `_meta` and re-emitted verbatim. The model never silently drops a key.
2. **Comments survive.** Each layer's `comment` is preserved in `_meta`-adjacent form on the layer node
   (BP-COMMENTS-1) and re-emitted; it is stripped only on the way into `plotnine`.
3. **Geom-as-first-layer is stable.** A `factory_id` read in becomes an explicit `layers[0]` geom; on
   write it stays an explicit geom layer (factory_id is not re-emitted). This is the one intentional
   normalisation: legacy in, canonical out.
4. **Mapping is explicit out.** Flat `x:`/`y:` read in become `mapping:` out. Flat keys are not re-emitted.
5. **Scalars stay scalars.** `theme`/`facet_by`/`palette` round-trip as plot-level keys unless the author
   expressed them as layers, in which case they round-trip as layers.

A truth table mirroring plot_config_cascade.md §11 will live in
`libs/viz_factory/tests/test_plot_spec_roundtrip.py`.

---

## 7. `factory_id` and flat aesthetics — clean removal (not "read forever")

Following the transformer precedent (decorators renamed to match the Polars API), the viz layer matches
`plotnine` — and we go all the way: the sugar is **removed**, not kept as a permanent second code path.
A second representation that lingers "just in case" is exactly the kind of ambiguity that breeds bugs
(the lossy round-trip in §1 is one). One format, one path.

- **Component names already match plotnine** — `geom_*`, `stat_*`, `scale_*`, `coord_*`, `facet_*`,
  `theme_*` (ADR-036 parity). No rename needed there.
- **`factory_id` has no `plotnine` analogue → it is removed from the model entirely.** Not renamed in
  place (renaming to `chart_type` would keep a non-grammar concept alive). Same for top-level flat
  aesthetics (`x:`/`y:`/`fill:` outside a `mapping:` block).
- **The "pick a chart type" UX survives only as a BLUEPRINT authoring template** (§4) that seeds a geom
  layer — never a stored manifest key.

### 7a. Transition discipline (how we remove without cutting the branch)

The legacy reader is removed **last**, only after every *producer* emits canonical. Sequence:

1. **Transitional read.** `normalise_plot_spec` initially still expands `factory_id` + promotes flat aes,
   so the app keeps working through migration. (This is the current `_normalise_spec` behaviour, promoted.)
2. **Migrate every producer:** all data manifests (BP-PLOT-MIGRATE-1), the generators
   (`create_manifest.py:281`, `debug_bootstrap_viz_yamls.py`), BLUEPRINT commit (BP-PLOT-COMMIT-1), and
   the format-authority docs/rules (BP-PLOT-DOCS-1).
3. **Verify zero producers remain:** `grep -rn "factory_id" config/ assets/ app/ libs/ tests/` returns only
   the removal code itself + historical ADR text. Render parity checked before/after migration.
4. **Remove the reader + fail loud (BP-PLOT-LEGACY-REMOVE-1).** Delete the `factory_id` expansion, the
   flat-aes promotion, `_FACTORY_GEOMS`, the `bar_logic` y-check, and the `heatmap_logic` color→fill remap
   from `normalise_plot_spec`. Replace with a **hard `PipelineError`**: if a plot spec contains `factory_id`
   or top-level flat aesthetics, raise with a clear message (the canonical shape + "run migrate_plot_specs.py").
   Silent sugar becomes a loud, helpful failure.

### 7b. After removal, what `normalise_plot_spec` still does

The seam survives — only the legacy-expansion logic inside it is removed. Post-removal it: (a) validates
the canonical shape (`mapping` + `layers`, geom present), (b) splits known keys vs `_meta`, (c) raises the
helpful legacy-format error. `serialise_plot_spec` remains its inverse.

Also delete the **dead** `_standardize_config` (viz_factory.py:455) — its own docstring says the resolver
replaced it; confirmed uncalled.

Net: the grammar is plotnine-faithful, there is exactly one plot format, and any legacy straggler fails
loud instead of silently rendering through a hidden path.

---

## 8. The tier3 commit bug (fixed by this model)

Both `_handle_manifest_save_internal` (blueprint_handlers.py:826-828) and `btn_download_manifest`
(blueprint_handlers.py:971) currently wipe `tier1`/`tier2` and dump the whole logic stack into
`wrangling.tier3`. This contradicts ADR-082 §4 ("BLUEPRINT never writes T3") and is meaningless for a
geom node. It is legacy from when this class was the Test Lab "Wrangle Studio."

Under this model the commit path routes by node kind + active component role:
- **Wrangling action nodes** → the source component's `wrangling.tier1`/`tier2` (the tier they were loaded
  from), never tier3.
- **Plot layer nodes** → the plot spec file's `layers:` via `serialise_plot_spec`.
- **T3 is never written by BLUEPRINT.** It is HOME-only (ADR-082 §4).

This is tracked as part of the commit task (§9), not silently bundled into BP-COMPONENT-FORMS-1.

---

## 9. Task sequence (full, resequenced — clean break)

BP-COMPONENT-FORMS-1 sits on the foundation; the legacy reader is removed **last**, after all producers
emit canonical. Dependencies are explicit so nothing is forgotten.

| # | Task | Effort | Delivers | Depends on |
|---|---|---|---|---|
| 1 | **BP-PLOT-MODEL-1** | `[sonnet/high]` | Promote `_normalise_spec` → public `normalise_plot_spec`; add inverse `serialise_plot_spec`; `_meta` passthrough; round-trip truth-table tests (`test_plot_spec_roundtrip.py`). **Delete dead `_standardize_config`** (viz_factory.py:455). Reader still expands legacy (transitional). No render behaviour change. | — |
| 2 | **BP-PLOT-LOAD-1** | `[sonnet/high]` | BLUEPRINT plot_spec load → mapping form + layer nodes (geom incl.) via `normalise_plot_spec`. `plot_spec` branch (blueprint_handlers.py:264) currently only visualizes — never sets logic_stack. Read-only first. | 1 |
| 3 | **BP-COMPONENT-FORMS-1** | `[opus/high]` | Component picker (context `plot`) + `search_components` helper + add/edit layer nodes via the shared 8-widget form. Node-kind discriminator (`{component}` vs `{action}`); branch in `bp_action_form_ui`, `_bp_apply_node_handler`, `logic_stack_ui`. | 1, 2, BP-COMPONENT-SCHEMA-1 (done) |
| 4 | **BP-MAPPING-FORM-1** | `[sonnet/medium]` | Dedicated mapping form (x/y/fill/color/facet_by column pickers) — `aes()`, not a component. | 1 |
| 5 | **BP-PLOT-COMMIT-1** | `[opus/high]` | `serialise_plot_spec` → write plot spec `layers:`; route wrangling nodes to their source tier; **kill the tier3 dump** (§8). BLUEPRINT emits canonical only (no factory_id). | 1 |
| 6 | **BP-PLOT-MIGRATE-1** | `[sonnet/medium]` | `assets/scripts/migrate_plot_specs.py` (argparse) — rewrite the 19 legacy manifests (13 plot specs + 6 masters) to canonical: factory_id→explicit geom (bar y-check → geom_col/geom_bar; heatmap color→fill+geom_tile), flat aes→`mapping:`. Scan `tests/` fixtures too. Verify render parity before/after (debug_gallery). **Update generators**: `create_manifest.py:281`, `debug_bootstrap_viz_yamls.py` → emit canonical. | 1 |
| 7 | **BP-PLOT-DOCS-1** | `[sonnet/medium]` | Rewrite plot-spec format authority to canonical, remove factory_id: `rules_manifest_structure.md §8` (the `factory_id` table + examples), `rules_persona_bioscientist.md §3-C`, `docs/appendix/manifest_structure.yaml`, `project_conventions.md`, `assets/template_manifests/1_test_data_ST22_dummy.yaml` (the §3 structural reference). Confirm `rules_gallery_standards.md` already canonical (it is). | — (do before 8) |
| 8 | **BP-PLOT-LEGACY-REMOVE-1** | `[sonnet/high]` | Remove factory_id expansion + flat-aes promotion + `_FACTORY_GEOMS` + bar y-check + heatmap remap from `normalise_plot_spec`; replace with a hard helpful `PipelineError` (§7a.4). Update `test_plot_config_resolver.py`: drop expansion tests, add legacy-error tests. **Gate:** `grep -rn factory_id config/ assets/ app/ libs/ tests/` returns only this error code + historical ADRs. | 5, 6, 7 |

Tasks 1–2 are behaviour-neutral for rendering. 3–5 are the authoring feature. 6–7 migrate all producers.
8 is the clean break — irreversible, gated on 5+6+7, fails loud on any straggler.

---

## 10. Out of scope (explicit)

- **Render-path changes** — the cascade (plot_config_cascade.md) is unchanged; this doc only adds the
  authoring seam and BLUEPRINT consumption.
- **HOME authoring of layers** — locked out by ADR-082 §4; cascade accommodates it if a future ADR opens it.
- **Forced manifest migration** — legacy reads forever; migration (task 6) is optional cleanup.
- **Joint Designer (BP-JOINT-1), Groups CRUD (BP-GROUPS-1)** — separate BLUEPRINT layers (ADR-082 §1).

---

## 11. References

- `.claude/design/plot_config_cascade.md` — the five-tier render cascade (the RENDER side)
- ADR-082 — BLUEPRINT feature set + T1/T2-vs-T3 boundary (BLUEPRINT never writes T3)
- ADR-036 — Artist Parity (component names match plotnine)
- ADR-075 — 8-widget `ui_schema` form renderer
- `libs/viz_factory/src/viz_factory/plot_config_resolver.py` — `_normalise_spec` (to be promoted), `_FACTORY_GEOMS`
- `rules_manifest_structure.md §8` — `analysis_groups` + plot spec file structure
