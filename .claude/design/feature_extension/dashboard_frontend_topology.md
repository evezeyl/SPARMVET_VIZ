# Second Frontend ("app2") vs. New Space ("HOME2") — Application Topology

**Status:** EXPLORATORY — nothing decided. Return-to-and-discuss.
**Author:** @dasharch
**Date:** 2026-05-22
**Related:** [`composite_dashboard_home2.md`](composite_dashboard_home2.md), [`r_backend.md`](r_backend.md), [`bioinformatics_viz.md`](bioinformatics_viz.md), `../developer_workflow.md`

---

## 1. The question

Instead of (or as well as) a HOME2 space inside the current app, could we build a **separate application ("app2")** for the interactive multi-panel / dashboard vision — serving different audiences and deployments, while leveraging the existing libraries?

**Short answer: yes — and the architecture was explicitly designed for exactly this.** This is arguably cleaner than HOME2 for the interactive-viewer use case.

---

## 2. The enabler: Clear Lines already anticipates a second frontend

`rules_runtime_environment.md §4` (the two-tier dependency model) states the libraries are the product and `app/` is just *one* frontend:

> "Each library in `./libs/` is designed to be independently installable and reusable **without the UI layer**. If you want to build a different frontend (CLI tool, FastAPI service, Galaxy wrapper, Jupyter workflow), you import only the layer(s) you need. `app/` is the ONLY place that wires multiple libraries together."

So app2 is not a workaround — it is the designed-for case. The shared product is:

```
libs/ingestion · libs/transformer · libs/viz_factory · libs/connector · libs/blueprint_arch · libs/utils
        (the engine + render + manifest contract — frontend-agnostic)
              │                                   │
          app/ (app1)                         app2 (NEW)
       workbench / producer                viewer / dashboard / consumer
```

---

## 3. The conceptual split: workbench vs viewer (the strong argument FOR app2)

The two visions serve **different users with different mental models**:

| | **app1 (current)** | **app2 (proposed)** |
|---|---|---|
| Role | Workbench / producer | Viewer / dashboard / consumer |
| User | Bioinformatician building pipelines | Epidemiologist / surveillance team / decision-maker |
| Activity | Wrangle, audit (T3), author manifests, explore | Read pre-built pathogen dashboards; explore interactively |
| Journey | TEST_LAB → BLUEPRINT → GALLERY → HOME (`developer_workflow.md`) | Open a dashboard, interact, export/share |
| Interactivity | L1 server-reactive (filter→re-render) | L2 client-live (linked selection) — the JS fork |
| Personas | Full persona/flag system, T3 audit | Likely simpler (or none) — mostly read/explore |

**Field precedent:** this is the NextStrain model — *augur* (the pipeline) and *auspice* (the interactive viewer) are separate tools sharing a data contract. Microreact is similarly a viewer, not a pipeline builder. Splitting producer from consumer is the norm in genomic surveillance, not the exception.

The current app's whole architecture (persona masking, T3 audit gatekeeper, tier toggles, manifest authoring) is **producer machinery**. A consumer dashboard does not want most of it — bolting HOME2 into app1 means carrying all that weight for an audience that doesn't need it.

---

## 4. app2 vs HOME2 — the real decision

| Factor | HOME2 (space in app1) | app2 (separate app) |
|---|---|---|
| Reuses libs | yes | yes |
| Reuses app1 wiring (bootloader, personas, sidebar registry) | yes | no (re-implements the slim parts it needs) |
| Fights existing producer machinery | yes (persona masking, reactive shell, T3) | no — clean slate |
| Framework freedom (pick best for interactive dashboards) | constrained to app1's Shiny shell | free to choose |
| Deployment independence (different audience/target) | one artifact, shared deploy | independent deploy, own profile |
| Maintenance | one app | two apps (shared-lib contract must stay stable) |
| Best when… | dashboard is a producer convenience inside the workbench | dashboard is a distinct product for a distinct audience |

**Leaning:** if the dashboard is for the **same producers** as a richer results view → HOME2. If it is for a **different audience / deployment** (surveillance teams consuming pathogen dashboards) → **app2**. Eve's framing ("deployments and needs might differ") points at app2.

These are not exclusive: HOME2 could be a thin producer-side preview; app2 the polished consumer viewer. Both ride the same libraries.

---

## 5. What app2 reuses vs builds new

| Layer | Reused from libs/ | New in app2 |
|---|---|---|
| Ingestion, Tier 1/2/3 assembly, contracts | ✅ all | — |
| VizFactory (render backends: plotnine / R / geom_polygon) | ✅ all | render-backend dispatch reuse |
| Manifest grammar + `dashboard:` block | ✅ | dashboard layout consumer |
| Path authority / deployment profiles | pattern reusable (`connector`) | own profile set |
| **Frontend shell** | — | **the new app — layout, panel grid, interactivity** |
| Persona / T3 audit / authoring | — | mostly **not needed** (simpler gating) |

The engine and render layers are 100% reused. Only the **frontend** is new — exactly Eve's instinct ("leverage existing libraries, build new UI only").

---

## 6. Framework options for app2

| Option | Interactivity | Fit | Note |
|---|---|---|---|
| **Shiny for Python + JS widgets** (shinywidgets→Plotly, ipyleaflet, cytoscape) | L2 via htmlwidgets | continuity — same stack/skills, reuses config patterns | server-side, **not** WASM/shinylive → respects `dasharch.md §2` |
| **JS frontend (React/Svelte) + FastAPI** over the libs | full L2, polished | best for a public/institutional viewer | heaviest new stack; the libs already support a "FastAPI service" frontend per Clear Lines |
| Quarto / Observable dashboards | limited L2 | report-style static-ish dashboards | good for export-quality, weak for live linking |
| Panel / Dash / Streamlit | L2 | quick dashboards | new framework to maintain |

**Lean for a first app2:** Shiny for Python + JS widgets — keeps one framework and reuses bootloader/profile patterns, while getting client-side interactivity (Leaflet maps, Plotly charts, Cytoscape/phylo trees). Move to a JS+FastAPI frontend only if a polished public surveillance viewer is the actual requirement.

---

## 7. Deployment differentiation (Eve's point)

Producer and consumer apps deploy differently:

- **app1 (workbench):** Galaxy/IRIDA interactive tool, developer/scientist personas, behind institutional auth.
- **app2 (viewer):** could be a standalone web deployment — institutional or public-facing surveillance dashboard, read-mostly, simpler/no persona system, its own deployment profile.

Different audiences, different security postures, different uptime needs. One monolith serving both is awkward; two frontends on a shared engine is clean.

---

## 8. Risks / constraints

- **Two apps to maintain.** The shared-lib contract (manifest grammar, VizFactory API) must stay stable — version the libraries and treat their public APIs as contracts. (The `@deps` system already tracks cross-lib coupling.)
- **Duplicated app-level concerns** (config, deployment profiles, gating). Mitigate by extracting genuinely shared app-level helpers into a small lib (e.g. `connector` already holds path authority) rather than copy-paste.
- **The interactive (L2/JS) render path is new regardless** — app2 doesn't avoid it, it's the natural home for it (see `composite_dashboard_home2.md` §10). app2 decouples that JS investment from the producer app's stable server-reactive model.
- **Scope creep** — app2 must stay a *viewer*; the moment it grows authoring/wrangling it is duplicating app1. Keep the producer/consumer line crisp.

---

## 9. How this composes the whole exploration

- The **engine + manifest + shared-key** trunk serves app1, HOME2, and app2 alike — build/keep it solid.
- **R backend** (`r_backend.md`) and **ggtree** (`bioinformatics_viz.md`) produce static panels usable in *either* frontend.
- The **interactive (JS) roadmap** (`composite_dashboard_home2.md` §10) finds its cleanest home in **app2**, away from app1's producer machinery.
- **app2 is a way to satisfy "different needs/deployments" without overloading app1** — which is precisely the Clear Lines payoff.

---

## 10. Library distribution: how many UIs consume the shared libs

The intent has always been: **libs are the reusable, expandable product; build as many UIs as needed.** That is exactly the Clear Lines payoff (§2). The remaining choice is the *distribution mechanism* — and the clean-lined library design works under all three, so this is a logistics decision, not an architectural one:

| Mechanism | How | Pros | Cons |
|---|---|---|---|
| **Git submodules** (Eve's plan) | each lib is its own repo, included as a submodule in each app repo; app pins a commit | each UI pins an exact lib version; libs evolve independently; clean repo separation | submodule friction (detached HEAD, contributors forget to commit/update pointers, editable-install ergonomics across submodules); learning curve |
| **Versioned packages** | publish libs to a private index (or `pip install` from git tags); apps declare versions in `pyproject.toml` | standard Python dependency mgmt; semver; CI-friendly; no submodule quirks | needs a package index or git-tag discipline; release step per lib |
| **Monorepo, multiple apps** | keep `libs/` in one repo, add `app2/` beside `app/`; both editable-install the libs | simplest today (no packaging/submodule overhead); current setup already does editable installs (ADR-011/016) | apps share release cadence; one big repo |

All three honor the two-tier dependency model. The current state is **monorepo + editable installs** (ADR-011/016: deps declared in `pyproject.toml` by package name). Submodules or versioned packages become attractive once a *second repo* (app2) needs to consume the libs independently — i.e. exactly when app2 becomes real.

**Honest steer:** submodules achieve the goal but carry real day-to-day friction; if the team is comfortable with a private package index or git-tag installs, that path is usually smoother and CI-friendlier. The decision is reversible and can wait until app2 is actually scoped — the libraries are already clean-lined, which is the part that mattered. Keep the `@deps` blocks accurate (they already track cross-lib coupling) so any split stays safe.

---

## 11. Open questions (survey-informed)

1. Is the dashboard audience the **same** producers (→ HOME2) or a **different** consumer group (→ app2)? *The survey's most decision-relevant question.*
2. Does app2 need authoring at all, or is it strictly a viewer fed by app1-produced manifests/data?
3. Framework: Shiny+widgets (continuity) vs JS+FastAPI (polished public viewer)?
4. Deployment target(s) for app2 — institutional intranet, public, Galaxy/IRIDA embed?
5. Gating — does app2 need any persona system, or just per-dashboard access control?
6. Do app1 and app2 share a deployment profile mechanism, or fully separate?

**Nothing scheduled.** Decision waits on Eve's organizational needs survey — the producer-vs-consumer audience split is the pivot.
