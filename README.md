# SPARMVET_VIZ: AMR Visualization Architecture 🔬📊

SPARMVET (SP-Analytical AMR Visualization Engine) is a modular, declarative framework for building high-integrity visualizations from genomic and AMR surveillance data.

## 🚀 Core Philosophy

1. **Strict Data Contracts (ADR-013)**: Data enters through an ingestion layer where it is immediately validated against a manifest.
2. **3-Tier Data Lifecycle (ADR-024)**:
    - **Tier 1 (The Trunk)**: Foundations. Cleaning, joining, and relational tidy-up.
    - **Tier 2 (The Branch)**: Specifics. Reshaping and aggregation for a particular plot.
    - **Tier 3 (The Leaf)**: Transient. Reactive filtering in the UI via Predicate Pushdown.
3. **Electronic Artist Pillar (VizFactory)**: A declarative Plotnine/ggplot abstraction that decouples "what to plot" from "how to plot."

## 📜 Declarative Manifest Syntax

Wrangling logic is separated into logical tiers to promote reuse and clarity:

```yaml
id: "example_manifest"
wrangling:
  tier1: # Relational Foundations
    - action: "rename"
      mapping: { "old": "new" }
    - action: "join"
      right_ingredient: "metadata"

  tier2: # Plot-Ready Reshaping (Optional)
    - action: "summarize"
      group_by: ["sample_id"]
      metrics: { "counts": "sum" }
```

> [!NOTE]
> If `tier2` is omitted, the system invokes **Identity Logic (ADR-014)**, passing the refined Tier 1 data directly to the visualization engine.

## 🛠️ Library Ecosystem

Each library is independently installable and usable without the UI layer. If you want to use only the wrangling engine in a script, install `libs/transformer/` + `libs/utils/` — nothing else required. `app/` is the only layer that wires libraries together.

**Dependency model:** `libs/utils/` is the base layer (shared utilities; no cross-lib deps of its own). All other domain libraries must not import from each other — only from `libs/utils/` (declared explicitly in their `pyproject.toml`). See [Library Dependency Model](./docs/foundations/core_architecture_code.qmd#library-dependency-model) for details.

- [**ingestion**](./libs/ingestion/): TSV/Excel discovery, schema normalization, MetadataValidator gatekeeper.
- [**transformer**](./libs/transformer/): The central wrangling and assembly engine (DataWrangler, DataAssembler).
- [**viz_factory**](./libs/viz_factory/): Graphical composition and Plotnine orchestration.
- [**viz_gallery**](./libs/viz_gallery/): Gallery persistence layer — bundles, index, recipe governance.
- [**test_lab**](./libs/test_lab/): AquaSynthesizer for synthetic test data, manifest bootstrapping, and reconciliation.
- [**utils**](./libs/utils/): Configuration loading, hashing, and shared utilities. **Base layer** — may be imported by any domain lib.
- [**connector**](./libs/connector/): Deployment profile resolution and data-source adapters (ADR-048, Phase 23).
- [**blueprint_arch**](./libs/blueprint_arch/): Blueprint Architect pure-Python logic (TubeMap mapper, manifest navigator). Headless-safe — usable in CLI tools and export handlers without Shiny.

## 🚀 Deployment Configuration

SPARMVET is designed to be deployed in different contexts — from a read-only pipeline display to a full interactive research workbench. Deployment is controlled by a **configuration profile** (called a persona) that defines which user functionalities are available.

### User functionalities

| Functionality | What users can do |
|---|---|
| **View** | Browse visualisations (always available) |
| **Passive filter** | Explore data ephemerally — no audit trail |
| **T3 audit** | Justify and commit data decisions — creates permanent audit branch |
| **Export** | Download reproducible bundle with full provenance |
| **Import** | Upload metadata or full data mapped to the manifest |
| **Gallery** | Browse chart recipe templates |
| **Blueprint Architect** | Inspect and design manifest lineage |
| **Test Lab** | Generate synthetic data and scaffold manifests |

### Non-negotiable rule: full audit trail in every export

Every export — regardless of configuration — includes a complete provenance record: data hashes, manifest hash, wrangling recipe hash, git commit, software versions, and creation timestamp. This cannot be disabled. See [ADR-069](./.claude/knowledge/architecture_decisions.md) and the [Deployment Configuration Guide](./docs/user_guide/deployment_personas.qmd).

### Quick start

```bash
SPARMVET_PERSONA=pipeline-exploration-simple .venv/bin/python -m shiny run app/src/main.py
```

Available profiles: `pipeline-static`, `pipeline-exploration-simple`, `pipeline-exploration-advanced`, `project-independent`, `developer`, `qa`. Custom profiles can be created in `config/ui/templates/`.

**Sidebar layout is configurable per persona and per workspace** (Home, Blueprint, Gallery, Test Lab). Each persona template declares its sidebar panel slots under a `workspaces:` key. Shared sidebar configs live in `config/ui/sidebars/` and are referenced via `!include`. See [Deployment Configuration](./docs/workflows/ui_persona.qmd#sidebar-configuration-adr-073) for the full guide and built-in panel type reference.

**Validate persona configs before deploying:**
```bash
.venv/bin/python scripts/validate_persona_config.py --all --strict
```

See [Deployment Configuration](./docs/user_guide/deployment_personas.qmd) for the full guide, dependency rules, and how to create a custom profile.

---

## 📖 Documentation

Detailed technical guides are in the [docs/](./docs/) directory:

- [Developer Preface & Architecture](./docs/index.qmd): Vision, integrity status, and filter message flow.
- [Wrangling Guide](./docs/reference/wrangling_guide.qmd): Tier 1/2/3 lifecycle and assembly logic.
- [Deployment Configuration](./docs/user_guide/deployment_personas.qmd): User functionalities, dependency rules, and available profiles.
- [Deployment Guide](./docs/deployment/deployment_guide.qmd): Galaxy, IRIDA, server, and local deployment (ADR-048).
- [Connector / Profile Schema](./docs/workflows/connector.qmd): Deployment profile YAML schema reference.

## 🔧 Developer Scripts

### `scripts/` — setup helpers

| Script | Purpose |
|---|---|
| `scripts/install_libs.sh` | Install all 8 editable libs in one command (`VENV=.my_venv ./scripts/install_libs.sh`) |

### `assets/scripts/` — manifest and deployment authoring

| Script | Purpose |
|---|---|
| `normalize_manifest_fields.py` | Sanitize manifests to ADR-041 Rich Dict standard |
| `create_manifest.py` | Scaffold a new pipeline manifest from a dataset |
| `create_test_deployment.py` | Generate a dev deployment profile (ADR-048) |
| `build_dep_graph.py` | Rebuild the `@deps` dependency graph |
| `generate_demo_data.py` | Generate synthetic demo data via AquaSynthesizer |

> Note: `debug_viz_factory_audit.py` was relocated to `libs/viz_factory/tests/` (ADR-032 — library-internal debug runners belong in their own `libs/<x>/tests/`).

## ⚖️ Standards & Governance

This project follows the **Violet Law** (Component naming convention) and the **@verify Protocol** (Mandatory evidence-based testing).
