# Architecture Decisions (SPARMVET_VIZ)

# Last Updated: 2026-04-23 (Session 3) by @dasharch
>
> all paths must be provided relative to the project root. Absolute paths or symlinks are not allowed.

## ADR 001: Decorator-Based Action Registry

**Status:** IMPLEMENTED
**Context:** The Transformer module required a way to execute declarative YAML-based wrangling rules without a monolithic `registry.py`.
**Decision:** Implement a **Decorator Pattern** (`@register_action`).

- **Registry Heart:** `libs/transformer/src/actions/base.py` defines the decorator and the `AVAILABLE_WRANGLING_ACTIONS` dictionary.
- **Auto-Load Strategy:** `libs/transformer/src/actions/__init__.py` imports `core` and `advanced` sub-packages to trigger the registration of all actions at system startup.
- **Benefits:** Decouples core logic from the execution engine, simplifies adding new bio-math functions, and enables automated introspection for the "In-App Help" pillar.
- **Multi-Column Support:** All registered actions MUST support a `columns` argument that accepts either a single string or a List[str].
- **Polars Implementation:** Actions must use `pl.col(columns)` to enable parallel execution across the target list.

## ADR 002: Tidy Data Contract (Long Format)

**Status:** ENFORCED
**Context:** Multi-species dashboards with variable gene counts (AMR) require a data format that remains stable even if species columns change.
**Decision:** All pipelines **MUST** produce Tidy (Long Format) CSV/TSV data (e.g., `Sample | Gene_Name | Result`).

- **Transformer Implementation:** Actions like `split_and_explode` and `derive_categories` are designed specifically to operate on or produce long-format Polars LazyFrames.

## ADR 003: "Thin" Shiny Frontend & Project-Agnostic Mandate

**Status:** IMPLEMENTED (April 9, 2026)
**Context:** Heavy data processing (Polars) should not slow down the UI rendering, and the system must be applicable to any project schema.
**Decision:** The Shiny App (`app/src/ui.py` and `server.py`) acts solely as an **Orchestrator**.

- **Rule:** No raw data wrangling or complex plotting logic allowed inside the `server.py` reactive blocks; all logic must be deferred to `libs/`.
- **Agnostic Mandate:** The system MUST NOT assume domain-specific column names (e.g., 'species', 'sample_id'). All UI elements and logic chains must derive their structure from manifest introspection (**ADR-004**) or Polars schema discovery (**ADR-029b**).

## ADR 004: YAML-Only Configuration & Registry Recognition

**Status:** ENFORCED
**Context:** The "Four-Pillar Strategy" originally mentioned JSON Schema, but the current code architecture is strictly **YAML-driven**.
**Decision:** All metadata schemas, wrangling rules, and data contracts will be managed via **YAML manifests**.

- **Registry Recognition**: The system 'recognizes' novel wrangling functions via the `@register_action(name)` decorator. These functions are automatically discovered by the `DataWrangler` at runtime through the centralized Python registry.
- **Mapping**: The YAML `action` key acts as the look-up token. There is no intermediate JSON schema; the YAML is parsed directly into Python dictionaries for processing.
- **Manifest Schema:** The YAML `wrangling` block for any action should prefer the key `columns: []` to allow batch processing.

## ADR 005: Universal Wrangler Runner

- **Agnostic Logic:** `libs/transformer/tests/debug_wrangler.py` must not contain decorator-specific hardcoding.
- **Dynamic Dispatch:** It must initialize the `DataWrangler`, parse the provided `--manifest`, and apply whatever rules are defined therein to the `--data` TSV.
- **CLI Standard:** It must always support `--data`, `--manifest`, and `--output` arguments via `argparse` to ensure manual reproducibility.

## ADR 006: Asset-Driven Prototyping Strategy

**Status:** DEPRECATED (Moved to ADR-032)
**Context:** For the "Walking Skeleton" to be interactive without real Galaxy data, we required a robust synthetic data layer.
**Decision:** Use the `./assets/` layer to drive the prototype lifecycle.
**Note:** This strategy has been superseded by the "Library Autonomy" logic in ADR-032.

## ADR 007: Minimal Dataset & Manual UI Deferral

**Status:** ENFORCED
**Context:** To achieve a functional prototype by March 21st, we must reduce implementation debt.
**Decision:** Adopt a **'Minimal Dataset'** strategy and defer automated UI complexity.

- **Minimal Dataset**: We assume input TSVs follow the YAML contract perfectly for Phase A/B. Malformed data handling is moved to Phase C.
- **Manual UI Deferral**: The dashboard will initially support manual file loading and sidebar selection of synthetic assets, avoiding the immediate need for the BioBlend/Galaxy API Mode B.
- **Pillar 4 Shift**: Formal JSON Schema validation is deferred in favor of direct YAML manifest interpretation.

## ADR 008: Visualisation Library - Plotnine Primary

**Status:** ENFORCED
**Context:** Previous ADR prioritized Plotly. After re-evaluating the "Artist" pillar, Plotnine is chosen for consistency with the Tidy data logic.
**Decision:** **Plotnine** is the primary visualization engine for the Prototype.

- **Plotly Status**: Moved to **[DEFERRED]** list.
- **Implementation**: Factory functions will return `ggplot` objects. Interactivity is sacrificed for Phase 1 to ensure standard "walking skeleton" data-visual flow.

## ADR 009: Multi-Source Ingestion

**Status:** PROPOSED
**Context:** Multi-species dashboards require combining core analytical data (e.g., ResFinder, MLST) with metadata and other additional datasets.
**Decision:** Implement a **Multi-Source Ingestion** strategy.

- **Rule:** Additional datasets MUST share the same 'wrangling' decorator logic as core data and metadata to ensure consistency across the pipeline.
- **Rule:** Joins between datasets MUST be explicitly defined by a `join_on` key in the manifest.
- **Primary Key Rule:** The field referenced by `join_on` MUST be defined in the fields manifest with `is_primary_key: true`.
- **Implementation:** The `DataWrangler` or an Orchestrator must loop through all defined sources, apply respective wrangling rules, and perform Polars-based joins before handing off to the visualization factory.

## ADR 010: Polars as the Universal Engine

**Status:** ENFORCED
**Context:** To maintain scalability, the entire transformation chain must remain in **Polars**.
**Decision:** **Polars** is the mandatory library for all Wrangling, Ingestion, and Selection logic.

- **Legacy Rule**: No Pandas calls allowed in `libs/transformer/` or `libs/ingestion/`.
- **Hand-off Rule**: Conversion to Pandas is only permitted at the final moment inside the `viz_factory` for Plotnine compatibility.

## ADR 011: Modular Monorepo & Independent Package Management

**Status:** ENFORCED
**Context:** The project is a monorepo where each subdirectory in `libs/` and the main `app/` are designed to be independent Python packages.
**Decision:** Each library MUST maintain its own `pyproject.toml`.

- **Path Mapping:**
  - `./libs/transformer`
  - `./libs/viz_factory`
  - `./app`
  - `./libs/utils`
- **Installation Rule:** The global `.venv` at the root will install these libraries in 'editable mode' (`pip install -e ./libs/transformer`).
- **Integrity Rule:** No symlinks. Each module must define its own dependencies, ensuring that if extracted, it could function as a standalone library.
- **Dependency Rule:** Legacy requirements (`requirements.txt`, `requires.txt`) are strictly **FORBIDDEN**; the `pyproject.toml` file is the sole source of truth for module dependencies.
- **Two-Tier Model (clarified 2026-05-09):** `libs/utils/` is the **base layer** — may be imported by any domain lib, but must be declared explicitly in that lib's `pyproject.toml`. All other `libs/` are **domain layers** — zero peer-to-peer cross-lib imports permitted. `app/` and `assets/scripts/` are the **orchestration layer** — the only place that imports from multiple libs. Goal: each domain lib is usable standalone; if you want a different UI (CLI, API, Galaxy), import only the layers you need. See `rules_runtime_environment.md §4`.

## ADR 012: Staged Data Assembly

**Status:** PROPOSED
**Context:** Multi-source data ingestion and complex joins can lead to monolithic, hard-to-maintain code if handled within a single class.
**Decision:** Adopt a **Staged Pipeline** approach.

- **Layer 1: Atomic Cleaning (The Wrangler):** The `DataWrangler` remains atomic. Its sole responsibility is "One Input -> One Cleaned Output". It follows declarative rules for a single dataset and MUST NOT contain join logic.
- **Layer 2: Orchestrated Assembly (The Assembler):** A dedicated `DataAssembler` or Orchestrator component is responsible for coordinating multiple Wrangler instances.
- **Responsibilities of Layer 2:**
  - Looping through defined datasets in the manifest.
  - Executing Layer 1 cleaning for each.
  - Performing Polars-based joins across cleaned datasets using `join_on`.
  - Applying final cross-dataset wrangling rules (e.g., calculated fields across joined tables).
- **Benefit:** Decouples cleaning logic from assembly logic, enabling independent testing and reuse of atomic wrangling actions.

## ADR 013: Dual-Validation Manifests

**Status:** ENFORCED
**Context:** To maintain robust data lineage between raw ingestion and final presentation, we must track schema state at two distinct points.
**Decision:** Manifests MUST explicitly define two schema states:

- **`input_fields`**: Defines the raw incoming schema (Raw/Ingestion). Used for validation before any wrangling occurs.
- **`output_fields`**: Defines the final consumed schema post-wrangling. This acts as the "Published Contract" for the Viz Factory and Orchestrator.
**Wrangling Rule:** The `wrangling` block remains the operational bridge between these two states.
- **`input_fields`** -> **`wrangling`** -> **`output_fields`**.

## ADR 014: Identity Logic for Wrangling

**Status:** ENFORCED
**Context:** Some reference datasets (e.g., APEC Virulence) should be imported "as-is" without transformations or column filtering.
**Decision:** The `DataWrangler` and Universal Runner MUST support **Identity Transformations**.

- **Rule:** If the `wrangling` block is missing or an empty list `[]`, the pipeline bypasses all atomic actions.
- **Rule:** If the `output_fields` block is missing or an empty list `[]`, the pipeline retains all columns from the `input_fields`.
- **Benefit:** Reduces manifest boilerplate for reference data and ensures the system remains robust when dealing with "straight-through" data ingestion.

- **Implementation:** Codified in [Data Engine Protocol — §4 "The Manifest Data Contract"](./.claude/rules/rules_data_engine.md) (Identity Transformations section).
- **The Contract Guard:** The `output_fields` block is a strict Polars `.select()` contract, protecting the `DataAssembler` from Column Drift.

## ADR 015: Flexible Source Resolution (Manifest-First)

**Status:** IMPLEMENTED
**Context:** Multi-source ingestion required explicit path resolution.
**Decision:** Mandatory use of `source` blocks in yaml manifests.

- **Rule:** Every dataset entry must contain a `source` dictionary with `type` and `path`.
- **Implementation:** Prototyped in `DataIngestor` and finalized via `wrangle_debug.py`.
- **Reference:** See Section 3 (Manifest Data Contract) of the [Data Engine Protocol](./.claude/rules/rules_data_engine.md).

## ADR 016: Package-First Authority (Editable Mode)

**Status:** IMPLEMENTED
**Context:** Fragmented library imports required a standard, reusable interface.
**Decision:** Core libraries are installed in **Editable Mode** to enable clean package communication.

- **Enforcement:** The **"Clear Lines" Policy** ([Runtime Environment — §4](./.claude/rules/rules_runtime_environment.md)) prohibits cross-library imports (e.g., `transformer` → `ingestion`).
- **Standard:** All execution locked to root `.venv` ([Runtime Environment — §1 & §5](./.claude/rules/rules_runtime_environment.md)).
- **Execution:** Validated via `assets/scripts/wrangle_debug.py` acting as an orchestration layer.

## ADR 018: Unified Transformer Model (Shared Registry)

**Status:** IMPLEMENTED
**Context:** The expansion from atomic cleaning (Layer 1) to multi-source assembly (Layer 2) required consistent transformation logic across both stages without code duplication.
**Decision:** The `DataWrangler` and `DataAssembler` must share the same central registry for actions.

- **Standard:** Both classes pull from `AVAILABLE_WRANGLING_ACTIONS` populated via the `@register_action` decorator.
- **Homogeneity:** Any atomic decorator (e.g., `strip_whitespace`, `split_column`) is natively available as an operation within an assembly recipe.
- **Benefit:** Simplifies library maintenance and ensures that "Wrangling" is treated as a single unified discipline across all pipeline layers.

## ADR 019: Decorator-Based Plot Component Registry

**Status:** PROPOSED
**Context:** The Viz Factory requires a modular way to build plots without a monolithic plotting script.
**Decision:** Implement a **Decorator Pattern** (`@register_plot_component`).

- **Registry Heart:** `libs/viz_factory/src/registry.py`.
- **Categories:** Components are registered by type: `geoms`, `scales`, `themes`, `facets`, and `coords`.
- **Benefits:** Allows the UI to dynamically list available "Plot Layers" for user selection.

## ADR 020: Data-Agnostic Plotting Manifest

**Status:** PROPOSED
**Context:** Plots must be reusable across different datasets (e.g., boxplots for different species).
**Decision:** Use a **Dictionary-of-Plots** where each plot contains a **List-of-Layers**.

- **Mapping Block:** Defines data-agnostic aesthetics (`x`, `y`, `fill`, `color`).
- **Layers Block:** An ordered list of dictionaries defining the plot construction.
- **Example:** A `geom_boxplot` layer is a dictionary of parameters passed to the registered function.

## ADR 021: Reactive State Management (Anchor vs. Filter)

**Status:** PROPOSED
**Context:** Users need to explore data by filtering without losing the "Master" view.
**Decision:** Implement a dual-state hand-off between the Transformer and the Viz Factory.

- **The Anchor:** The `Master Tidy Table` remains the unmodified source of truth.
- **The Filtered View:** A temporary LazyFrame created by the Transformer for exploration.
- **Reactivity:** The Viz Factory re-renders the *same* manifest against whichever state is active (Unmodified vs. Filtered).

## ADR 022: The Violet Law (Documentation Standard)

**Status:** ENFORCED
**Context:** Consistent verbal and written communication is necessary when identifying core architectural classes and files.
**Decision:** All human-facing documentation (.qmd files) and library READMEs ("Key Components" lists) MUST format component references as `ComponentName (file_name.py)`.

- **Purpose:** Decouples technical context ambiguity by enforcing a "Who and Where" standard simultaneously for readers.
- **Strict Boundary:** This format is strictly DOCUMENTATION-ONLY. It MUST NOT be used for functional class names, variables, filenames, or high-level docstrings in the actual codebase logic.
- **Reference:** Workspace Rules `rules_aesthetic.md` (The Violet Law).

## ADR 023: Statistical Transformations (Stats) Delegation

**Status:** ENFORCED
**Context:** The `stat_*` layer logic in Plotnine often mimics or operates directly on geometric layers. Creating an entirely separate complex abstract registry mechanism for `stats` components would needlessly complicate the declarative YAML manifest structure.
**Decision:** All important standard statistical transformations (Stats) MUST be implemented and registered directly within the `geoms/` directory.

- **Benefit:** Simplifies the manifest structure by injecting stats logic as parameter arguments into existing geom factories (e.g. `geom_bar` handling `stat="count"`).
- **Compliance:** This explicitly preserves the ggplot2 (R) "Grammar of Graphics" while eliminating overhead from maintaining disjointed duplicate state.

## ADR 024: Tiered Wrangling & Data Lifecycle (ADR-024 Refinement)

**Status:** IMPLEMENTED (April 10, 2026)
**Context:** Plotnine's 22-minute render time for >200k rows necessitates a data reduction strategy. Users require "instant" UI filtering without re-running heavy Layer 1/2 joins.
**Decision:** Implement a three-tier tree lifecycle and a two-tier nested wrangling structure within the `DataWrangler (data_wrangler.py)`.

### 1. The 3-Tier Tree Lifecycle

- **Tier 1 (The Trunk):** Relational Anchor. The fully assembled Tidy Table (Layer 1 + Layer 2). Persisted as `tmp/session_anchor.parquet`.
- **Tier 2 (The Branch):** Plot-Specific Anchor. A filtered, summarized, or reshaped branch optimized for a functional group of plots. Persisted as `tmp/branch_*.parquet`.
- **Tier 3 (The Leaf):** Interactive UI View. Transient LazyFrames derived from Tier 1 or Tier 2 via Predicate Pushdown.

### 2. Nested Wrangling Structure (YAML)

All `wrangling` blocks in YAML manifests MUST use nested tier keys to separate logic:

- **`tier1` (Tidy/Relational):** Logic applied to wide data (Join, Clean, Rename, Filter). This produces the "Filterable Trunk".
- **`tier2` (Plot-Prep):** Visual-specific transformations (Unpivot/Long-format, Summarize, Aggregate).

**Identity Logic (Missing Keys):**

- If a manifest is missing `tier2`, it is treated as an **Identity Transformation** for that tier (Tier 1 output is passed through unchanged).
- The `DataWrangler` uses `_resolve_tier()` to extract the correct sequence, ensuring structural homogeneity.
- **Mandate:** Flat list wrangling is deprecated; all new manifests must adopt the nested structure.

## ADR 025: The Gallery & Recipe Pattern (Visual Cookbook)

**Status:** PROPOSED --- Target: Next Session
**Context:** Users without deep ggplot2 knowledge need a way to discover, understand, and adapt plot manifests for their own AMR datasets. Static documentation is insufficient --- examples must be executable and inspectable.
**Decision:** Implement a **Visual Gallery** where each registered VizFactory component is documented as a 3-part **Recipe**:

1. **Representative Data Header** --- A TSV snippet (first N rows) showing the expected data shape.
2. **YAML Manifest** --- The exact manifest used to produce the plot (copy-paste ready).
3. **Resulting Image** --- The rendered plot PNG.

**Implementation Rules:**

- **Gallery Flag**: The `bulk_debug_viz_factory_layers.py` runner SHALL support a `--gallery` flag. When set, it writes a `gallery_report.md` to the output dir containing all three recipe parts per component.
- **Premiere Example**: The Triple-Source Integration (Metadata/Phenotypes/Genotypes) plots from Phase 9 serve as the premier end-to-end gallery entry, demonstrating real AMR data.
- **Data Safety**: Gallery data headers are generated from test TSV files only. Real patient data MUST NOT appear in gallery output.
- **Documentation Target**: `docs/appendix/viz_factory_rationale.qmd` hosts the User-as-Artist philosophy linking to the gallery.

**Benefit:** Enables a self-service "copy, modify, render" workflow for end users, directly supporting the SPARMVET_VIZ mission of accessible AMR data visualisation.

**Low-Level Coding Design Note:** This pattern is explicitly designed to support **Low-Level Coding** --- a practice where domain scientists (veterinary epidemiologists, microbiologists) interact with the system at the YAML abstraction layer rather than the Python layer. The YAML manifest *is* the code. A user who can edit a text file can produce a custom AMR visualisation. The Gallery provides the examples needed to make this self-teaching.

## ADR 026: Reactive State, Persona Logic & Reporting

**Status:** ENFORCED (April 7, 2026)
**Context:** Decoupling production rigidity from developer flexibility while maintaining sub-5s responsiveness for 200k+ rows.
**Decision:**

- **Persona Isolation**: Use `config/ui/templates/ui_persona_template.yaml` to toggle feature visibility (e.g., masking 'Developer Mode', 'Interactability', 'Gallery'). UI Personas MUST ONLY control functional masking and rendering, NOT system paths.
- **The Identity Rule**: Tier 3 (Leaf) is initialized as an identity of Tier 2 (Branch). Sidebar filters modify the Leaf view via Predicate Pushdown ONLY.
- **Immutable Audit**: "No Trace, No Export" rule. Manual exclusions require a mandatory 'User Note'.
- **Persistence**: YAML is the authoritative format for all saved 'Recipes' to ensure human-readability and Git compatibility.

## ADR 027: Multi-Module UI Orchestration & Aesthetics

**Status:** PROPOSED (April 8, 2026)
**Context:** Need a scalable UI supporting different Personas (User/Developer) while adhering to the "Thin Frontend" rule.
**Decision:** Implement a 5-module UI stack where the frontend acts strictly as an **Orchestrator**.

- **Module Integration:**
  - **DataConnector**: Ingests via `libs/ingestion`.
  - **WrangleStudio**: Chains decorators from `libs/transformer`.
  - **VizViewer**: Renders side-by-side Tier 2/3 plots via `libs/viz_factory`.
  - **AuditEngine**: Immutable logging and "Recipe Pre-filling" logic.
  - **GalleryViewer**: Browser for `assets/gallery_data/`.
- **Aesthetic Constraints:** - **Sidebars**: Light Grey (#f8f9fa).
  - **Tooltips/Help**: Light Yellow (#fff9c4) or Light Green (#e8f5e9).
  - **Prohibition**: No "Deep Violet" themes in the UI (Documentation only).

## ADR 028: Gallery Content & Logic Separation

**Status:** PROPOSED (April 8, 2026)
**Context:** Need an expandable gallery with proper attribution and licensing.
**Decision:** Separate logic from data assets.

- **Logic Layer:** `libs/viz_gallery` (Standalone Python package).
- **Content Layer:** `assets/gallery_data/`.
- **Mandatory Assets:** Each example folder MUST contain: `example_data.tsv`, `recipe_manifest.yaml`, `preview_plot.png`, `LICENSE.md`, and `README.md` (for author credits).

### ADR 029a: Dashboard Theater & Panel Layout Specs

**Status:** SUPERSEDED by ADR-043 (2026-04-30). Historical reference only.
> State variables `ref_tier_switch`, `view_toggle`, and `is_comparison` described below were removed in Phase 21-A/C. The `is_triple` / `theater_state` flag system was replaced. See ADR-043 for the current Unified Home Theater model.

**Original status:** PROPOSED (April 8, 2026)
**Context:** Need a high-density, interactive workspace for data exploration with specific "Theater" states.
**Decision:** Implement a Three-Column Shell with a multi-state Central Theater.
Implement a manifest-driven UI that discovers its own structure at runtime.

- **Dynamic Tab Discovery:** The `VizViewer (viz_factory.py)` MUST scan the active YAML manifest for all defined plot IDs and programmatically generate a corresponding tab for each.
- **Automatic Column Discovery:** The UI MUST introspect the incoming Polars LazyFrame (Tier 1/2) to identify all available columns.

- **Navigation Panel (Left):**  - Nested hierarchy: `Group (e.g., QC)` > `Plot Selection`. - Must include a `Global Export` toggle and a `Persona Selector`. It must be possible to deactivate Persona selector by UI configuration file `config/ui/<template_persona>_template.yaml`)

- **Central Theater (Center):** Vertical Layout: Top 60% Plot / Bottom 40% Data Table (adjustable). Maximize/Minimize controls for each component.
- **Comparison Theater (APPROVED — Phase 12-A):** Optional dual-column layout activated by a `comparison_mode` toggle. Gated by `comparison_mode_enabled` in `config/ui/<persona>_template.yaml`.

  **Left Column — Reference Sandbox (`#f8f9fa` recessed):**
  - `plot_reference`: Tier 2 reference plot — **immutable**, never affected by user filters.
  - `ref_tier_switch` toggle: `Tier 1 (wide)` ↔ `Tier 2 (viz-transformed)` — affects reference table only.
  - `table_reference`: Read-only exploration table. User may filter/column-pick for visual inspection (e.g., "which samples are from France, 2002?") but NO writes are persisted. Label: `"⚠️ Inspection only — changes here are not saved"`.

  **Right Column — Active Pane (theater white `#ffffff`):**
  - `plot_leaf`: Tier 3 plot, recalculated only on explicit **▶ Apply** click.
  - `view_toggle`: `Wide (Tier 1)` ↔ `Long/Aggregated (Tier 3')` — switches the interactive table view; hints at filter stage.
  - `table_leaf`: Wide-format Tier 1 data with column picker and interactive row filters.
  - **▶ Apply Button**: Explicit trigger for `tier3_leaf()` recalculation. Prevents constant UI re-rendering on large datasets.

  **Position-Aware Recipe Pipeline (The Core Rule):**
  Tier 3 = Tier 1 fork with Tier 2 steps pre-filled in the right Audit Panel.
  The **position** of each step relative to inherited Tier 2 nodes determines its transform stage:
  - Steps placed **ABOVE** Tier 2 nodes → applied to wide Tier 1 data (pre-transform filtering).
  - Steps placed **BELOW** Tier 2 nodes → applied after viz transforms (post-transform selection).
  - Removing an inherited Tier 2 step triggers a `ui.modal` warning: "This may break the plot render."

- **Right Sidebar (Audit Stack):** Logic Color-Coding differentiates Inherited Tier 2 steps (Light violet background `#f3e5f5`) from User-added Tier 3 steps (Light Yellow background `#fffde7`). User steps must include a mandatory comment field. Each step has a trash icon (Remove). Removing Tier 2 steps requires warning + confirmation. Restore button (**Reset Sync**) is blue (`#0d6efd`) and resets Tier 3 state to match Tier 2. Centered header alignment is mandatory for all sidebar categories.

## ADR 029b: Dynamic Discovery & Interaction Logic

**Status:** PROPOSED (April 8, 2026)
**Decision:** Implement manifest-driven discovery and standardized interactivity.

- **Dynamic Tabs:** `VizViewer` MUST programmatically generate tabs by scanning plot IDs in the active YAML manifest. It must be possible to specify plot tittle and subtitle in The active YAML manifest (but optional).
- **Auto-Discovery:** UI MUST introspect the Polars schema to identify all columns; all columns (except Primary Keys) must be hideable via a picker and include top-level filter boxes.
- **Persistence:** Sidebars are open by default but must be collapsible to allow 100% theater width.

## ADR 029c: Interaction & Visibility Logic

**Status:** PROPOSED (April 8, 2026)
**Decision:** Standardize how users hide/show data and outliers.

- **Table Interactivity:** - Every column (except the Primary Key) must be "Hideable" via a column-picker. Affect the Tier 3 (Leaf) view.
  - Search/Filter boxes at the top of every column directly affect the Tier 3 (Leaf) view.
- **Sidebar Persistence:** Sidebars must be "Collapsible" (Open by default on Desktop) to allow the Theater to occupy 100% of the width during visualization.

## ADR 030: Manifest & External Data Ingestion

**Status:** PROPOSED (April 8, 2026)
**Decision:** Expand `DataConnector (ingestor.py)` to handle custom user inputs beyond standard pipelines.

- **Manifest Upload:** Support uploading predefined YAML manifests to override default pipeline logic.
- **External Data Joins:** Allow adding "Additional Data" files. The UI MUST provide a joining helper that uses `libs/transformer` relational logic to verify Primary Key matching before merging. (eg.can reuse parts of scripts in .assets/scripts)

## ADR 031: Data Tier, Session Persistence & Path Authority

**Status:** IMPLEMENTED (April 9, 2026)
**Context:** Need a configurable, reliable way to handle session recovery and multi-location data storage.
**Decision:** Implement a **Path Authority Strategy** strictly managed via `config/connectors/`.

- **Connector Authority Rule:** System connection paths (Locations 1-5), Script Agency paths, and Runtime Environments MUST be defined in dedicated connector configurations (e.g., `config/connectors/local/local_connector.yaml`), entirely decoupled from UI logic.
- **Location 1 (Raw/Ingestion):** Path to raw external data assets.
- **Location 2 (Manifests):** Path to pipeline definitions.
- **Location 3 (Tiers 1 & 2):** Curated Parquet Anchors & Views (`session_anchor.parquet`).
- **Location 4 (User & Tiers 3):** User-accessible directory for session states, active UI leaf interaction, and ghost saves.
- **Location 5 (Gallery):** Assets gallery for cloned/submitted recipes (`assets/gallery_data/`).

## ADR 032: Library Autonomy & Script Internalization

**Status:** IMPLEMENTED (April 9, 2026) — scope clarified 2026-04-24
**Decision:** All core utility scripts (Synthetic Data Generation, Excel Parsing) MUST reside within their respective library `src/` directories to ensure package self-sufficiency (**ADR-011**).

- **Migration**: Deprecated `assets/scripts/` in favor of library-internal modules (e.g., `generator_utils.aqua_synthesizer`).
- **Discovery**: The UI consumes these scripts via `bootloader.get_script_path()`, ensuring path autonomy.
- **Rule**: Deletion of the `assets/scripts/` directory is mandatory once migration is verified to prevent logic fragmentation.

**Scope clarification (2026-04-24):** The deletion mandate applies only to scripts that duplicated library-internal logic during early prototyping. `assets/scripts/` is **not deprecated** as a location — it is the designated home for **user-facing workspace helper scripts** (manifest creation, manifest validation, data verification, deployment debugging). These are not library functions and must not be moved into `libs/`. Library-internal test/debug runners belong inside their respective `libs/` packages. Cross-library dev utilities with no clear library owner may go in `libs/utils/`.

## ADR 033: Educational Gallery & Structured Metadata

**Status:** IMPLEMENTED (April 18, 2026)
**Context:** Users need more than just technical recipes; they need context on *how* and *why* to use specific visualizations.
**Decision:** Implement an "Educational Gallery" extension that pairs technical manifests with structured markdown metadata.

- **Split-Pane Viewer:** The Gallery Browser MUST utilize a 50/50 split layout.
  - **Left Pane (Technical):** Displays the plot, Tier 1/2 data samples, and the raw YAML recipe.
  - **Right Pane (Educational):** Displays a nicely formatted (shiny::markdown) description derived from an associated `.md` file.
- **Mandatory Metadata Template:** Every submission to the public gallery MUST include a description file with the following mandatory sections:
  1. **Suitability:** When most suited for use.
  2. **Data Schema (Tier 1):** Required data types (categorical vs numeric).
  3. **Transformation Logic (Tier 2):** Description of essential reshapes.
  4. **Interpretations:** Assumptions, known limitations, and comments.
- **Governance:** High-density analysis "Theaters" focus on discovery, while the Gallery focuses on "Visual Literacy."
- **Visual Polish**: Centering of the Guidance pane content using `mx-auto` and `text-center` is required for all recipes.

## ADR 034: Unified Diagnostic Layer & Aesthetic Error Handling

**Status:** IMPLEMENTED (April 10, 2026)
**Context:** Silent failures in large Polars pipelines lead to user frustration and "Black Box" analytical profiles.
**Decision:** Implement a system-wide diagnostic layer that traps common failures and suggests human-readable fixes.

- **The SPARMVET_Error Pattern**: Implement a central `SPARMVET_Error` class in `libs/utils`. Libraries (Ingestion, Transformer, VizFactory) MUST raise specific subclasses containing a `tip` attribute.
- **Visual Feedback**: The UI catches these errors and renders them inside a **Soft Note Modal** (`#fff9c4`).
- **Heuristic Suggestions**: When a 'Missing Column' error occurs, the Transformer must use string similarity (e.g. Levenshtein) to suggest the closest match from the existing schema to help catch typos immediately.
- **Fail-Fast Viz**: The VizFactory must pre-validate manifest aesthetics against the incoming dataset columns before attempting (ggplot) plotnine construction to prevent crashing the render reactive.

## ADR-035: Gallery Taxonomy & Visual Discovery System

**Status:** IMPLEMENTED (April 18, 2026)
**Context:**  As the Gallery grows, users require a structured way to discover recipes beyond simple folder browsing. ADR-033 established the split-pane view, but not the classification of plots.
**Decision:**  Implement a formal taxonomy based on "Families" and "Difficulty":

- **Families**: Distribution, Correlation, Comparison, Ranking, Evolution, Part-to-Whole.
- **Difficulty**: [Simple], [Intermediate], [Advanced].
- **Data Pattern**: Explicit labeling of numeric and categorical dimensions.
- **Metadata Integration**: These fields are mandatory in `recipe_meta.md` and drive the real-time UI filtering.
**Aesthetic Constraint**: Taxonomy sidebar headers must be bold, underlined, and scaled (1.2rem) for hierarchical clarity.

## ADR-036: Persistent UI Integrity (ID Sanitation Pivot)

**Status:** IMPLEMENTED (April 18, 2026)
**Context:** Switching between heavy-state modules (e.g., Wrangle Studio vs. Theater) can lead to 'ghost' elements (stale headers or metrics) if the DOM is not forcefully cleared by the reactive engine.
**Decision:** Implement a **Dynamic ID Pivot** for main orchestration containers.

- **Rule**: The ID of the primary `navset_card_tab` MUST be derived from the active sidebar selection (e.g., `id=f"central_theater_tabs_{sidebar_name}"`).
- **Effect**: This forces Shiny to treat each module's theater as a distinct DOM entity, ensuring all previous module artifacts are flushed upon context switch.

## ADR-038: Contextual Sidebar Masking (Focus Mode)

**Status:** PROPOSED (April 19, 2026)
**Context:** Global UI controls (Project Loader, Session management) clutter the interface during specialized tasks like Gallery browsing where those controls are redundant.

- **Decision**: Implement a **Focus Mode** pattern via server-side reactive reification.
- **Reactive Masking**: Global Sidebar tools (Project Navigator, Filters, Session) are moved from a static `ui.py` definition to a reactive `@render.ui` in `server.py`.
- **Benefit**: This physically removes the headers and accordion panels from the DOM when the "Gallery" tab is active, ensuring zero visual clutter.
- **Natural Interface**: The UI is reconfigured to provide a persistent Global Navigation header (Home/Gallery) while task-specific tools exist as transient reactive overlays.

## ADR-039: The Blueprint Architect Workflow & TubeMap

**Status:** PROPOSED (April 19, 2026)
**Context:** Manifest-driven development requires a "multiscale" environment—switching between project-wide lineage (Macro) and component-level transformations (Micro). Fragmented UI tabs prevent a cohesive "Design → Verify" loop.
**Decision:** Implement the **Blueprint Architect** as a Tri-Pane "Flight Deck" with a DAG-driven project context.

- **The TubeMap Navigation (Map-First):** The central theater features a top-aligned, collapsible **Interactive Map** (Mermaid/SVG). This graph visualizes the entire manifest lineage (Tier 1 → Tier 2 → Assembly → Plot).
- **Contextual Focus:** Clicking a node (station) in the map dynamically focuses the entire UI on that component's state.
- **The Architectural Stack (Right Sidebar):** The Right Sidebar is reconfigured as the **Active Blueprint Stack**. It displays the atomic logic steps (Wrangling) for the station currently selected in the Map.
- **Stacked Live Preview (The Live Viewer):** The primary theater panel displays a **Vertical Stack** (Plot over Data Table). This provides a single-view verification of how logic changes affect the visual and data outcomes simultaneously.
- **Branching & Forking:** The Map View enables "Visual Forking"—selecting a node and initiating a new branch directly in the DAG, producing corresponding YAML additions to the manifest.

**Benefit:** Creates a unified development environment that minimizes context switching and provides immediate visual feedback on architectural changes.

## ADR-041: Unified Manifest Standard (Keyed-Schema & Ordered-Logic)

**Status:** ENFORCED (April 20, 2026)
**Context:** Ambiguity between List-of-Dicts and Dictionary formats for manifest components led to inconsistent structural integrity and potential backend performance penalties.
**Decision:** Standardize on a hybrid model that respects the functional requirements of each manifest layer:

1. **Field Definitions (`input_fields`, `output_fields`):**
   - **Format:** Mandatory **Rich Dictionary** (`slug: {original_name, type, label}`).
   - **Rationale:** High-performance $O(1)$ lookup is essential for Ingestion and Column Mapping. Dictionary format aligns natively with Polars `.schema()`.
   - **Constraint:** Key names (slugs) must be unique within the manifest context.

2. **Wrangling Blocks (`tier1`, `tier2`):**
   - **Format:** Mandatory **Sequential List** of action dictionaries.
   - **Rationale:** Order of operations is foundational to data pipelining. Actions must be processed deterministically in the user-defined sequence.

3. **Fragment Packaging:**
   - **Standard:** Included YAML fragments (`!include`) MUST be "Flat". Redundant top-level anchoring keys (e.g., repeating `input_fields:` inside the included file) are strictly prohibited.
   - **Rationale:** Supports the `ConfigManager` auto-unnesting logic and prevents deep-key nesting in memory.

**Benefit:** Resolves the architectural disconnect between the UI contract viewer and the Backend data engines, ensuring both high performance and high integrity.

---

## ADR-040: Bidirectional Lineage Navigation & Blueprint Interface Fields

**Status:** PARTIALLY IMPLEMENTED (April 20, 2026 — Phases 18-A through 18-D, 18-B-fixes, 18-C, 18-F complete; 18-E pending)
**Context:** Phase 18 work on the Blueprint Architect Interface (Fields) tab revealed that a flat "view one component's fields" model cannot represent the real manifest topology: multi-ingredient assemblies (many Tier 1 → one Tier 2), per-plot wrangling steps, and branching outputs. More importantly, the most natural scientific workflow is **reverse lineage** — starting from a desired plot output and tracing backwards to find where a missing field must be added or computed.

**Decision:** Extend the Blueprint Architect with a **Bidirectional Lineage Rail** and a **3-column contract viewer** replacing the current flat Interface (Fields) tab.

### Core Concepts

**1. Two TubeMap levels (tabs within the existing accordion):**

- **Tab A — Project Overview (existing):** Full project DAG showing all Tier 1 datasets, assemblies, and plots. Provides macro context.
- **Tab B — Component Lineage Rail (new):** When a node is selected in Tab A, this renders only the linear chain for that node — from raw source to the terminal plot, showing the exact path that data travels. If the project branches (one assembly → N plots), the Rail shows one branch at a time, with a branch selector.

**2. 3-column Interface panel (replaces flat tab-3 Fields):**
When any node on the Lineage Rail is selected:

- **Left — Upstream Contract:** Fields arriving at this node. For Tier 1 wrangling: input_fields. For assembly: one collapsible accordion per ingredient showing each dataset's output_fields. For a plot: the parent assembly's final_contract.
- **Center — Active Component:** The component's own definition (wrangling recipe, plot spec, or field schema). Editable. The logic stack / raw YAML lives here.
- **Right — Downstream Contract:** Fields leaving this node. For Tier 1 wrangling: output_fields. For assembly: final_contract. For a plot: "Plot terminal — no output schema."

**3. Bidirectional workflow:**

- **Forward (build):** Source → wrangle → assemble → plot. Select a component, see what comes in, edit the recipe, see what goes out.
- **Reverse (design):** Start at a plot node. The left panel shows what fields are available from the assembly. If a needed field is missing, click backwards along the Rail to the assembly → then to the relevant Tier 1 wrangling → add the `mutate` step there → the field propagates forward. The Rail makes the gap immediately visible.

**4. Per-plot wrangling (new manifest concept):**
Some plots require dataset-specific transformations after the assembly (wide/long format pivots, aggregations, filters). These are represented as an optional `pre_plot_wrangling` key in the plot block:

```yaml
plots:
  mlst_bar:
    target_dataset: MLST_with_metadata
    pre_plot_wrangling: !include 'plots/mlst_bar_wrangling.yaml'  # optional
    spec: !include 'plots/mlst_bar.yaml'
```

This keeps plot-specific transformations explicit and traceable. In the Lineage Rail, this appears as an intermediate node between the assembly output and the plot spec. If absent, the slot shows an "➕ Add plot wrangling" affordance.

**5. Assembly branching representation:**
When an assembly recipe joins N ingredients, the Upstream Contract panel shows an accordion — one section per ingredient — each displaying that dataset's output_fields. This is honest: there is no single unified input schema; the inputs are the individual outputs of N Tier 1 pipelines. The final_contract represents the merged, curated output that all downstream plots consume.

### Technical Foundation (IMPLEMENTED as of 2026-04-20)

#### Module-level helpers in `server.py`

| Helper | Key | Value | Purpose |
| :--- | :--- | :--- | :--- |
| `_build_sibling_map(manifest_path_str)` | `rel_path` (str) | `{role, schema_id, schema_type, siblings, ingredients}` | File-path index. Assembly wrangling files get `role="assembly"`. Only file-path strings registered as keys (inline dicts are unhashable). |
| `_build_schema_registry(manifest_path_str, includes_map)` | `schema_id` (str) | `{schema_type, input_fields, wrangling, output_fields, recipe, ingredients, target_dataset, group_id, source, info}` | Schema-ID index capturing both `!include` rel-paths (str) and inline YAML content (`{"inline": val}`). |
| `_build_lineage_chain(selected_rel, ctx_map)` | — | `list[{rel, schema_id, role, label, is_active}]` | Walks backward then forward from selected node to produce an ordered chain for the Rail. |
| `_load_fields_file(abs_path)` | — | `list` | Reads field files; unwraps ADR-014 single-key wrapper if present. |
| `_slot(block, key)` | — | `str \| {"inline": val} \| None` | Distinguishes `!include` marker, inline content, and absent/empty. |

#### Reactive values in `server.py`

- `_includes_map: reactive.Value` — `{rel_path: abs_path_str}` for all `!include` files in active manifest.
- `_component_ctx_map: reactive.Value` — `{rel_path: {...}}` built by `_build_sibling_map` on manifest selection.
- `_schema_registry: reactive.Value` — `{schema_id: {...}}` built by `_build_schema_registry` on manifest selection.

#### Reactive state in `WrangleStudio.__init__`

```python
self.active_component_info  = reactive.Value({})   # {role, schema_id, schema_type, ingredients, wrangling}
self.active_upstream        = reactive.Value([])    # [] | list[fields] | list[{id, fields}] (assembly)
self.active_downstream      = reactive.Value([])    # [] | list[fields]
self.active_lineage_chain   = reactive.Value([])    # ordered Rail nodes
self.active_manifest_path   = reactive.Value("")    # master manifest path — set on every import
self.active_viz_id          = reactive.Value(None)  # plot schema_id — set only when role=="plot_spec"
```

#### Role dispatch in `_handle_manifest_import` Mode A

| `role` | `active_upstream` | `active_downstream` |
| :--- | :--- | :--- |
| `input_fields` | `[]` | fields from file |
| `output_fields` | fields from file | `[]` |
| `wrangling` | sibling `input_fields` file | sibling `output_fields` file |
| `assembly` | per-ingredient accordion (schema_id → output_fields via ctx_map) | assembly `output_fields` |
| `plot_spec` | parent `output_fields` resolved via `target_dataset` — searches assembly first, then data_schemas | `[]` (terminal) |

**Key constraint on `plot_spec` upstream resolution:** `target_dataset` in plot spec files typically names a **data schema** (e.g. `"FastP"`), not an assembly. The lookup in `_handle_manifest_import` tries three passes: (1) assembly `output_fields`, (2) any `output_fields` for matching `schema_id`, (3) `input_fields` fallback.

#### Lineage Rail UI (`lineage_rail_ui` output)

Renders a `<button>` per chain node with role icon, label, role tag. Active node: bold border + filled background. JS `onclick` sets a hidden `<input id="lineage_node_rel">` and dispatches a `change` event → `handle_lineage_node_click` effect → `ui.update_select` + `ui.js_eval` to click `btn_import_manifest` programmatically. TubeMap node clicks (`_sync_selector_from_node_click`) use the same JS pattern.

#### Sidebar display labels

`_update_dataset_pipelines` builds display labels as `"{schema_id} — {role}"` (from `_component_ctx_map`) instead of raw filenames. Fallback to `abs_path.name` when the rel_path is not in the sibling map.

#### Live View plot preview

`architect_active_plot` uses `ConfigManager(active_manifest_path.get()).raw_config` for the full resolved manifest config, not `yaml.safe_load(active_raw_yaml)` (which is the component file fragment). `active_viz_id` is set to `schema_id` when a `plot_spec` is loaded.

### Implementation Phases

- **Phase 18-A:** ✅ Field materialization, context map, role-aware loading, normalize button, `_build_sibling_map`, `_build_schema_registry`. *(COMPLETED 2026-04-20)*
- **Phase 18-B:** ✅ `_build_lineage_chain`, Rail UI rendering, chain populated on component load, Rail click → full component load via `ui.js_eval`. *(COMPLETED 2026-04-20)*
- **Phase 18-B-fixes:** ✅ Sidebar labels, plot_spec upstream resolution, Live View wiring, TubeMap click wiring. *(COMPLETED 2026-04-20 Session 2)*
- **Phase 18-C:** ✅ 3-column panel with `lineage_rail_ui`, upstream/component/downstream cards, dynamic headers. *(COMPLETED 2026-04-20)*
- **Phase 18-D:** ✅ `pre_plot_wrangling` support — optional key in plot block; Rail node between assembly and plot. *(COMPLETED 2026-04-20)*
- **Phase 18-E:** Reverse navigation — Field Gap Analysis tool. *(PENDING)*
- **Phase 18-F:** ✅ Full clickable TubeMap driving Rail navigation. *(COMPLETED 2026-04-20)*
  - `BlueprintMapper.generate_mermaid()`: plot nodes (in subgraphs) now tracked in `_clickable` and get `click` directives — they were previously missed.
  - `_sync_selector_from_node_click`: TubeMap node ID (`safe_schema_id`) resolved to best `rel_path` via `_component_ctx_map`, using role priority (assembly > wrangling > plot_spec > plot_wrangling > output_fields > input_fields). Previously tried to use schema_id directly as selector value → nothing loaded.
- **Phase 18-G:** ✅ Full inline manifest reactivity + Assembly Live Data + TubeMap zoom/pan. *(COMPLETED 2026-04-20 Session 5)*
  - See ADR-040-G below.

### Phase 18-G Detail (Session 5, 2026-04-20)

#### Bug: Join node "unable to find column 'category'" error

**Root cause:** `processed_data_surgical` in `wrangle_studio.py` called `apply_logic(lf)` unconditionally on the materialized parquet. For an `assembly` node, the parquet IS the final assembled output; re-running the assembly recipe (which starts with `filter_eq column: category` on the pre-unpivot data) against the already-assembled columns caused the column-not-found error.

**Fix:** `processed_data_surgical` now only calls `apply_logic` when `active_component_info.role` ∈ `{"wrangling", "plot_wrangling"}`. For all other roles (`assembly`, `plot_spec`, `output_fields`, `input_fields`) the parquet is served as-is.

#### Bug: Join node never materialised / Live Data Glimpse empty

**Root cause:** The `assembly` role handler in Mode A (`_handle_manifest_import`) set `active_upstream`/`active_downstream` but never called `orchestrator.materialize_tier1` or set `active_anchor_path`.

**Fix:** Added the same materialise-and-set-anchor block to the `assembly` handler that `plot_spec` already had.

#### Bug: Mode B (inline manifests) missing all reactive state

**Root cause:** Mode B (fallback path for inline manifests — no `!include` files) only set `logic_stack` and `active_fields`. All other reactive values (`active_component_info`, `active_upstream`, `active_downstream`, lineage chain, TubeMap highlight, `active_manifest_path`, assembly materialisation) were never set. This made clicking TubeMap nodes partially update the UI (logic stack changed) but left fields/contracts/TubeMap highlight blank.

**Fix:** Mode B now mirrors Mode A fully:
- Detects role from `_component_ctx_map` (which has inline entries since Phase 18-F)
- For `assembly` role: builds `ing_items` from inline `output_fields` dicts of each ingredient; materialises via `orchestrator.materialize_tier1`; sets `active_anchor_path`
- For all other roles: passes rich field dicts (not just key lists) to `active_upstream`/`active_downstream` so `_fields_table` renders type info
- Sets `active_component_info`, lineage chain, TubeMap highlight for all roles

#### Enhancement: TubeMap zoom/pan (`app/src/ui.py`, `app/modules/wrangle_studio.py`)

**Library added:** `svg-pan-zoom@3.6.1` (CDN).

**Integration:**
- `initTubeMapPanZoom()` defined globally in `ui.py`; called via `shiny:visualchange` event (300ms after mermaid re-render) and via inline `<script>` tag injected with each `blueprint_tubemap_ui` render
- Pan/zoom initialised on the `<svg>` produced by Mermaid; instance stored in `svg._panZoomInstance` to avoid double-init
- Toolbar: `＋ Zoom In` / `－ Zoom Out` / `⊡ Fit` buttons above viewport; each calls `_panZoomInstance.zoomIn/Out/fit/center()` inline
- Viewport: 300 px fixed height, `overflow: hidden` (pan replaces scroll)

**Known limitation:** `svg-pan-zoom` + Mermaid's `securityLevel:'loose'` both manipulate the SVG. Click handlers survive because they are on `<g>` nodes that pan-zoom does not replace — only the viewport transform changes. However, if the accordion is expanded after first render and the SVG dimensions were 0×0 at init time, `fit()` may need the 100ms settle timeout. The `setTimeout(pz.fit, 100)` handles this.

#### Open issue: TubeMap library replacement (tracked separately)

The current Mermaid.js + svg-pan-zoom stack works but has limitations:
- Graph is generated as a flat LR DAG; no hierarchical lane-based layout
- Compact "GitHub-style" commit graph is not achievable with Mermaid
- Re-render on every Shiny reactive change causes visible flicker
- Node shapes are limited; no swimlane or layered grouping without subgraphs

**Desired properties for a replacement library:**
1. **Compact, lane-based DAG** — GitHub-style commit graph where each schema type (Source / Wrangling / Assembly / Plot) occupies a horizontal lane
2. **Interactive** — click events surfaced to JS, programmatic node highlight
3. **Pan + zoom built-in** — no secondary library needed
4. **Works inside Shiny** — can be initialised from a JS string (not file-based), re-rendered reactively without full page reload
5. **Lightweight** — no heavy framework dependency (React, Vue, etc.)

**Candidate libraries to evaluate:**
- **`vis-network`** (visjs.org) — force-directed + hierarchical layout, full click API, CDN-available, ~1MB. Best fit for hierarchical DAG. `hierarchical: {direction: "LR", sortMethod: "directed"}`
- **`d3-dag`** (github.com/erikbrinkman/d3-dag) — proper DAG layout algorithms (Sugiyama), renders as SVG via D3. Most control, most work.
- **`ELK.js`** (Eclipse Layout Kernel JS) — industry-grade DAG layouter; Mermaid 10 can use it as a layout backend (`layout: elk`) which keeps click callbacks. May be the lowest-effort upgrade.
- **`Cytoscape.js`** — full graph library, pan/zoom/click built-in, `dagre` layout plugin for DAG. CDN-available.

**Recommended path:** Try `mermaid + elk` first (config change only: `layout: elk`, `elk.algorithm: 'layered'`). If layout quality is still insufficient, migrate to `vis-network` with `hierarchical` mode — it requires wrapping the Mermaid DSL in a JS node/edge array but the `BlueprintMapper` already has that data structure internally.

**Benefit:** The Blueprint Architect becomes a full bidirectional manifest development environment. A scientist can start from a visualization goal and work backwards to the data transformation needed, or build forward from raw source to plot — both workflows using the same graph, the same contracts, and the same editing tools.

## ADR-042: YAML 'on' Resilience & Key Purging (bool/startswith)

**Status:** IMPLEMENTED (2026-03-07)
**Context:** YAML's reserved word `on` automatically parses to boolean `True` in many loaders. This caused attribute errors (`'bool' object has no attribute 'startswith'`) in the `DataAssembler` and `DataWrangler` when iterating over rule keys or purging internal metadata (`__` prefixed keys).
**Decision:** Implement defensive type checks and explicit boolean-key handling in all key-iteration loops.

- **Resilience:** The `DataAssembler` now uses `isinstance(k, str)` before calling `startswith("__")`.
- **Selector Handling:** Both `DataAssembler` and `DataWrangler` now explicitly check for `rule.get(True)` when resolving column selectors like `on`, `source`, or `columns`.
- **Hygiene:** Manifests SHOULD quote `"on"`, but the codebase MUST handle unquoted variants to ensure stability across diverse YAML loaders and human error.

---

## ADR-043: Unified Home Theater — Elimination of Redundant "Analysis Theater" Nav Mode

**Status:** IMPLEMENTED (2026-04-30) — Phase 21-A through 21-H complete. All sub-phases verified (21-H headless: 76/76 PASS).
**Context:** The dashboard had two top-level navigation modes — "Home" and "Analysis Theater (Viz)" — that shared the same `dynamic_tabs()` render function and differed only in their header text. The `analysis_groups` manifest-driven tabs (QC, AMR, etc.) were appended identically to both modes. The "Viz" nav item was a stub falling through to Home logic. This created dead weight in the navigation, user confusion over the distinction, and a maintenance surface with no benefit.
**Decision:** **Eliminate the "Analysis Theater" / "Viz" nav item entirely.** Merge all content into a single **Home** mode. The `analysis_groups` manifest tabs become the primary tab structure of Home.

### Navigation Structure (Post-ADR-043)

```
Home
├── [Tab] <analysis_group_1>   ← e.g. "Quality Control"
│   ├── [Sub-Tab] <plot_1>    ← e.g. "QC Reads Horizontal Barplot"  [collapsible section]
│   └── [Sub-Tab] <plot_2>    ← e.g. "Assembly Quality Dotplot"     [collapsible section]
├── [Tab] <analysis_group_N>   ← from manifest analysis_groups
└── [Tab] Inspector             ← retained: flat full-data view
```

### Tier Toggle (replaces ref_tier_switch + view_toggle)

A unified **radio-button strip** above the theater content area controls which data tier is active. The available states are **persona-gated**:

| State | Plot Pane Shows | Data Pane Shows | Persona Gate |
|---|---|---|---|
| **T1 Raw** | T2 Reference Plot (blueprint, read-only) | T1 Anchor data (read-only) | All |
| **T2 Reference** | T2 Reference Plot (blueprint, read-only) | T2 Branch data (read-only) | All |
| **T3 Wrangling** | T3 Active Plot (live, Apply-gated) | T3 post-wrangling data (sandbox) | ≥ `pipeline_exploration_advanced` |
| **T3 Plot** | T3 Active Plot (live, Apply-gated) | T3 post-plot data slice | ≥ `pipeline_exploration_advanced` |

- T1 and T2 states are **read-only reference panes** — no Apply gate, no audit nodes generated.
- T3 states activate the **`btn_apply` gatekeeper** and the T3 sandbox section of the audit stack.
- For personas that cannot access T3 (`pipeline_static`, `pipeline_exploration_simple`): the T3 recipe silently pre-fills from T2 and the rendered output is **functionally identical to T2**. The Tier Toggle shows only T1/T2 options — T3 buttons are hidden entirely. There is no visual distinction between T2 and T3 for these personas because there is no functional distinction.
- Toggling between T1/T2 and T3 does NOT reset the T3 recipe; it merely changes what is displayed.

### Comparison Mode (Option A — Separate Toggle, Persona-Gated)

- Comparison Mode is a **distinct, persona-gated toggle** (≥ `pipeline_exploration_advanced`), independent of the Tier Toggle.
- When **ON**: the theater splits into a 2-column layout — left = current T1/T2 reference (driven by Tier Toggle state), right = T3 Active.
- When **OFF**: single-pane view driven solely by the Tier Toggle.
- This replaces the previous `is_comparison` + `is_triple` flag system.

### Context-Reactive Left Sidebar Filters

- The active **sub-tab** (individual plot) is the reactive context driver for left sidebar filter widgets.
- Reactive chain: `active_sub_tab_id → plot_spec (from manifest analysis_groups) → aesthetics (x, y, color, facet, grouping columns) → left panel filter widgets`.
- When the user navigates between sub-tabs, the left panel **regenerates** to show only columns declared in that plot's `plot_spec` aesthetics.
- Filters are always scoped to the currently active plot's data contract — never to the full schema.
- This applies to ALL personas; the left panel always reflects the active sub-tab context.

### Layout & Collapsibility

- **Plot sub-tabs** (`navset_underline` within each analysis group tab) are wrapped in a **collapsible `ui.accordion` panel**, allowing the user to collapse all plots to focus on data.
- **Data preview panes** (T1/T2 table or T3 sandbox table) are rendered in a **separate collapsible `ui.accordion` panel** positioned **below** the plot section.
- Column picker (for T3 data sandbox) MUST span full available width — `width: 100%`, `flex: 1 1 100%` — and MUST NOT wrap to multiple rows.
- Both plot and data accordion panels default to **expanded**; collapse state is user-driven and MUST NOT reset on sub-tab navigation.

**Supersedes:** The "Analysis Theater (Viz)" nav mode described in `rules_ui_dashboard.md` §2 and `ui_implementation_contract.md` §2.
**Affects:** `app/src/server.py` (`dynamic_tabs`, `sidebar_nav_ui`, filter generation), `app/src/ui.py` (CSS), `rules_ui_dashboard.md`, `ui_implementation_contract.md`.

---

## ADR-044: Persona-Gated Audit Stack & Right Sidebar Visibility

**Status:** IMPLEMENTED (2026-04-30) — Phase 21-G verified. Right sidebar suppression live in `home_theater.py:right_sidebar_content_ui`. `btn_revert` superseded by per-node 🗑 delete (Phase 22-I).
**Context:** The Pipeline Audit (right sidebar) previously displayed T2 Blueprint nodes (Violet) as a persistent reference for all personas. For lower-privilege personas (`pipeline_static`, `pipeline_exploration_simple`), the T3 sandbox is inaccessible and the T3 recipe silently mirrors T2. The right sidebar therefore contains no actionable information for these personas — it adds visual noise, consumes screen real estate, and misrepresents the interaction model by implying the user has an audit trail to manage.
**Decision:** Apply a two-level persona gate to the right sidebar.

### Right Sidebar Visibility Gate

| Persona | Right Sidebar (Audit Stack) | Rationale |
|---|---|---|
| `pipeline_static` | **Hidden entirely** | No sandbox, T3 = T2 silently. Nothing to audit. Theater expands to full width. |
| `pipeline_exploration_simple` | **Hidden entirely** | T3 silently mirrors T2; no actionable audit trail. Theater expands to full width. |
| ≥ `pipeline_exploration_advanced` | **Visible** | Full sandbox access; scientific audit trail is meaningful and required. |

- When the right sidebar is hidden, the theater center column MUST expand to fill the full available width. The `layout_sidebar` structure MUST programmatically suppress the right sidebar element — not merely set `display: none` — so that no residual gap or dead space appears in the layout.

### Audit Stack Section Visibility (when sidebar is visible, i.e. ≥ advanced persona)

| Section | Content | Visibility |
|---|---|---|
| **T2 Blueprint (Violet nodes)** | Inherited read-only recipe steps from the T2 manifest | Always shown (for advanced+ personas) |
| **T3 Wrangling nodes (Yellow)** | User-added pre/post-transform steps (filters, selects, mutations) | Shown; user can add/disable/delete |
| **T3 Plot override nodes (Yellow)** | User-added plot-parameter overrides scoped to the active `plot_spec` | Shown; user can add/disable/delete |
| **`btn_apply` gatekeeper** | Apply button + pending badge | Active only when T3 changes are pending |
| **`btn_revert`** | Full wipe back to T2 blueprint state | Always available while T3 sidebar is open |

### T3 Pre-fill Behaviour (All Personas — Silent)

- The T3 recipe ALWAYS initializes as a silent copy of the T2 blueprint for all personas, ensuring plot formatting is never broken by persona transitions.
- For `pipeline_static` and `pipeline_exploration_simple`: this pre-fill is invisible. T3 ≡ T2 functionally. The right sidebar is hidden.
- For ≥ `pipeline_exploration_advanced`: Violet nodes (the T2 blueprint) are displayed in the audit stack. The user may add Yellow nodes above (pre-transform, wide data) or below (post-transform, long data) the Violet block.

**Supersedes:** The Audit Stack and Persona Reactivity Matrix descriptions in `ui_implementation_contract.md` §1 and `rules_ui_dashboard.md` §3.
**Affects:** `app/src/server.py` (`right_sidebar_content_ui`, persona masking), `app/src/ui.py` (sidebar layout suppression), `ui_implementation_contract.md`, `rules_ui_dashboard.md`.

---

## ADR-045: Server Decomposition — Handlers Directory & Manifest Navigator Module

**Status:** IMPLEMENTED (2026-04-23) — Phase 22 complete. UI smoke test passed; no regressions.
**Context:** `app/src/server.py` had grown to ~2,362 lines containing five functionally distinct concerns: manifest introspection helpers, Home Theater UI wiring, Blueprint Architect UI wiring, Gallery UI wiring, and shared reactive state/calcs. This monolith made targeted development difficult, slowed orientation for new work, and violated the principle of modular separation already established by `WrangleStudio`, `GalleryViewer`, and `DataOrchestrator`. As Phase 21 adds further Home Theater logic, the file would grow further without decomposition.

**Decision:** Split `server.py` into a **thin orchestrator** (228 lines) plus a `app/handlers/` directory of Shiny-wiring modules, and extract the manifest introspection engine into `app/modules/manifest_navigator.py`.

### The Boundary Rule

Two categories of code are permanently separated:

| Category | Location | Characteristics |
|---|---|---|
| **Manifest introspection** (pure functions) | `app/modules/manifest_navigator.py` | No Shiny imports. No `input`/`output`/`session`. Pure Python — importable from headless scripts, test suites, and DevStudio without side effects. |
| **Shiny wiring** (reactive handlers) | `app/handlers/<concern>.py` | Contains `@render.*`, `@reactive.Effect`, `@reactive.Calc`. Receives shared state via explicit `define_server(...)` arguments. Never imported by non-Shiny contexts. |

This boundary is **architectural law** — not a convention. Mixing them is a protocol violation.

### `app/modules/manifest_navigator.py` (New)

Contains all five pure manifest introspection helpers currently at module level in `server.py`:

| Function | Purpose |
|---|---|
| `build_sibling_map(manifest_path_str)` | Parses master manifest without resolving `!include`; maps `rel_path → {role, schema_id, schema_type, siblings, ingredients}` |
| `build_schema_registry(manifest_path_str, includes_map)` | Full schema-level structural index: `schema_id → {schema_type, input_fields, wrangling, output_fields, ingredients, target_dataset, …}` |
| `build_lineage_chain(selected_rel, ctx_map)` | Walks sibling map bidirectionally; returns ordered `list[node_dict]` for the Lineage Rail |
| `load_fields_file(abs_path)` | Reads a standalone fields YAML with ADR-014 unnesting |
| `resolve_fields_for_schema(schema_id, ctx_map, inc_map)` | Recursive field resolution with cycle guard; returns ADR-041 Rich Dict |

**Why a module, not a handler:** These functions are pure data transformations with zero Shiny dependency. They are already being considered for the Field Gap Analysis tool (Phase 20), future headless test scripts, and DevStudio dev utilities. Placing them in a handler file would make them accidentally private and create import hazards (handler files contain Shiny registration side-effects).

**Public API convention:** Functions are exported without leading underscore (drop the `_` prefix from current private names). Internal helpers within the functions remain private.

### `app/handlers/` Directory (New)

Five handler modules, each exposing exactly one `define_server(input, output, session, *, ...)` function that registers its `@render.*` and `@reactive.*` blocks:

| File | Owns |
|---|---|
| `home_theater.py` | `dynamic_tabs`, `sidebar_nav_ui`, `sidebar_tools_ui`, `sidebar_filters`, `system_tools_ui`, `right_sidebar_content_ui` (Home branch), `recipe_pending_badge_ui`, `plot_reference`, `plot_leaf`, `table_reference`, `table_leaf`, `handle_plot_brush`, `comparison_mode_toggle_ui` |
| `audit_stack.py` | `audit_nodes_tier2`, `audit_nodes_tier3`, `audit_stack_tools_ui`, `handle_apply`, `track_recipe_changes` |
| `blueprint_handlers.py` | All Phase 18 Shiny wiring: `_init_wrangle_manifests`, `_update_dataset_pipelines`, `_sync_selector_from_node_click`, `_do_load_component`, `_handle_manifest_import`, `_handle_normalize_fields`, `_handle_upload_replace`, `_handle_upload_append`, `_handle_manifest_save_internal`, `btn_download_manifest`, `sync_blueprint_mapper`, `right_sidebar_content_ui` (Architect/Gallery/Dev branches) |
| `gallery_handlers.py` | All gallery effects/renders currently in `server.py`: `_sync_*_all`, `_init_gallery_selector`, `handle_gallery_clone`, `_gallery_active_metadata`, `gallery_preview_img`, `gallery_static_data`, `gallery_yaml_preview`, `gallery_md_content`, `_update_gallery_options`, `gallery_browser_anchor` |
| `ingestion_handlers.py` | `handle_ingest`, `update_persona_context` |

### `app/src/server.py` After Decomposition (~120 lines)

Retains only:
1. Imports and module initialisation (`WrangleStudio`, `DevStudio`, `DataOrchestrator`, `VizFactory`, `bootloader`)
2. Shared reactive state (`anchor_path`, `recipe_pending`, `snapshot_recipe`, `gallery_refresh_trigger`, `current_persona`)
3. Shared reactive calcs (`active_collection_id`, `active_cfg`, `tier1_anchor`, `tier_reference`, `tier3_leaf`)
4. Shared utility functions (`_safe_input`, `show_sparmvet_error`, `_apply_tier2_transforms`, `primary_keys`)
5. Five `define_server(...)` delegation calls

### The `define_server(...)` Contract

Each handler module function signature declares its dependencies explicitly:

```python
def define_server(input, output, session, *, active_cfg, tier1_anchor,
                  tier_reference, tier3_leaf, current_persona,
                  anchor_path, recipe_pending, snapshot_recipe,
                  wrangle_studio, orchestrator, viz_factory, bootloader):
    # All @render.*, @reactive.* registrations for this concern
```

Only keyword-only arguments (`*`) are permitted after `input, output, session` to prevent positional errors when adding new dependencies.

### Violet Law Compliance

Per the documentation standard: `ManifestNavigator (manifest_navigator.py)` for any doc/README reference.

**Affects:** `app/src/server.py`, `app/modules/`, `app/handlers/` (new), `workspace_standard.md`, `project_conventions.md`, `rules_ui_dashboard.md` (§4 Coding Standards).

---

## ADR-046: Scientific Audit Protocol & Manifest Precision

**Status:** PROPOSED (2026-04-23)
**Context:** Development of complexity-heavy AMR lineages (e.g. ST22) requires fine-grained scientific auditability. Initial builds revealed friction from "silently dropped" columns, imprecise naming (phenotype), and continuous-scale plot errors (float years).

### 1. The Audit Mandate (Tier 1 Visibility)
- **Decision:** During the development phase, agents MUST materialize Tier 1 (Atomic Wrangling) artifacts alongside Tier 2 (Assembled) results.
- **Protocol:** `debug_wrangler.py` MUST be executed for each ingredient to generate audit tables (e.g. `amr_data_debug.tsv`) showing the raw cleaning results (identity/overlap filters).

### 2. The Column Retention Policy
- **Decision:** "Identity" columns (sample_id, gene, accession) SHOULD be retained in Tier 1 and Tier 2 wrangling to facilitate row-level audit. 
- **Filtering Rule:** Dropping unnecessary columns is deferred to the **final_contract** of the Join manifest, ensuring they are only pruned after all biological plots are finalized.

### 3. Precision Renaming Standard
- **Decision:** Use biologically precise and source-aware column names. 
- **Standard:** Favor `predicted_phenotype` (ResFinder) or `observed_phenotype` (Lab) over generic `phenotype`. Use underscores to avoid collision in joined datasets.

### 4. Manifest Whitelisting (The Final Contract)
- **Decision:** The `final_contract` block is explicitly defined as a **Strict Projection Guard**. 
- **Effect:** Any column not listed in the contract is dropped from the final materialization. This ensures the output data matches the downstream dashboard requirements exactly.

### 5. Biological Typing Standard
- **Decision:** Categorical variables stored as numbers (e.g. Year, Sequence Type) MUST be explicitly cast to `int` or `string` in the Tier 2 assembly recipe.
- **Rationale:** Prevents Plotnine/ggplot from treating them as continuous scales, which causes "stretched" x-axes and incorrect legend rendering.

## ADR-047: Tier-Aware Export Bundle

**Status:** IMPLEMENTED (2026-04-23) — **Extended 2026-05-04** (EXPORT-REDESIGN-1/2)
**Context:** Users require a reproducible, self-contained output package from the Home Theater — plots, data, recipes, and a Quarto report — that can be used for publication and archiving without re-running the full pipeline.

**Decision:**

### 1. Export Bundle Structure
A zip archive `YYYYMMDD_HHMMSS_<user_name>_results.zip` containing:
- `plots/` — SVG (web preset) or PNG ≥600 DPI (publication preset) for every plot defined in the active manifest.
- `data/` — T1 and T2 TSVs always; T3 TSV only for advanced+ persona when T3 tier is active. Named `<dataset>_T1.tsv`, `<dataset>_T2.tsv`, `<dataset>_T3.tsv`.
- `recipes/<proj>/` — all YAML wrangling/assembly/plot files from the project manifest directory.
- `FILTERS.txt` — embedded when `applied_filters` is non-empty ("No Trace No Export" protocol).
- `report.qmd` — Quarto source report with YAML front-matter, optional filter table, figure includes, and data section listing tiers exported.
- `README.txt` — bundle manifest (timestamp, project, persona, preset, tiers, counts).

### 2. No Trace No Export Protocol
If any row filters are applied at the time of export, their full trace (column / operator / value) is embedded in `FILTERS.txt`. The bundle is never silently "clean" — the user note is mandatory. This matches the spirit of ADR-021 (reproducibility obligation).

### 3. Tier-Aware Data Policy
| Tier | Exported when |
|------|--------------|
| T1 (Assembled) | Always |
| T2 (Analysis-ready) | Always — via `tier_reference()` reactive |
| T3 (User-adjusted) | Advanced+ persona only (`pipeline_exploration_advanced`, `project_independent`, `developer`), AND `tier_toggle == "T3"` at export time |

### 4. Preset Policy
- `web`: SVG output (vector, scalable, small file); 300 DPI for raster elements.
- `publication`: PNG output, ≥600 DPI, suitable for journal submission.

### 5. Deferred Elements
- Ghost save to `user_sessions` location — deferred.
- Per-plot checkbox selection — all plots always exported for now.
- ~~T3 recipe serialization~~ — **implemented 2026-05-04** (see §7 below).

### 6. Implementation Location
`app/handlers/export_handlers.py`: `system_tools_ui` (UI), `export_bundle_download` (`@render.download` async generator), `_export_bundle_filename()` (helper).

### 7. Extensions (2026-05-04 — EXPORT-REDESIGN-1/2)

**Scope toggle (3-way):** `[Global project | Active group | Active plot]`
- Shown only when persona has both `export_enabled`.
- Active group = group the active plot tab belongs to; lineage backtraced per plot.
- Active plot = current plot tab (`active_home_subtab`).
- "Active group" hidden when manifest has no `analysis_groups` or active plot has no group.
- Falls back to Global at download time if no active plot tab.
- Spec: `.claude/design/export_specification.md`

**T3 audit trail in report.qmd:**
- Section `## T3 Audit Trail` appended when `t3_sandbox_enabled` AND any plot in scope has committed active T3 nodes.
- Per-plot table: Step / Action / Details / Justification. Deactivated nodes excluded.
- Keys in `t3_recipe_by_plot` are subtab IDs (`subtab_{plot_id}`).

**`recipes/t3_steps.yaml`:**
- Written when T3 has committed active nodes. Scoped to export scope.
- Structure: `generated`, `export_scope`, `t3_steps: {plot_id: [{action, params…, reason, committed_at}]}`.

**Single Graph Export accordion removed** from sidebar — superseded by scope toggle.
**`export_audit_report_ui/download` deleted** — audit trail now lives inside `report.qmd`.

---

## ADR-048: Multi-System Deployment Architecture — Deployment Profile & Connector Abstraction

**Status:** DECIDED (2026-04-24) — Implementation Phase 23
**Last Updated:** 2026-04-24 (Session 4) by @dasharch

**Context:** SPARMVET_VIZ must run in at least four distinct deployment contexts — Galaxy (GxIT), IRIDA (REST API), institutional/general server, and local developer PC — using a single Docker image. Each context delivers configuration differently, accesses data differently, and may lock different UI personas and manifests. The existing `config/connectors/local/local_connector.yaml` handles only the local filesystem case. No mechanism exists to communicate deployment context to the Bootloader at runtime, and there is no abstraction for the two fundamentally different data access paradigms (filesystem vs. API-fetched).

---

### 1. Naming Decision: `connectors/` → `deployment/`

The directory `config/connectors/` will be renamed to `config/deployment/`. This better reflects the purpose of these files: they define how SPARMVET is deployed into a specific environment, not merely how it connects to a data source. The schema of the YAML files is extended (see §3).

**Impact on code:** `bootloader.py` path reference changes. No other code references the directory directly — all paths are resolved through the Bootloader. This is a low-risk rename. Code migration is Phase 23.

Until Phase 23, `config/connectors/` remains in use. The template is extended in place to document the future schema.

---

### 2. The Four Deployment Contexts

| Context | Who launches the app | How config is communicated | Data access paradigm |
|---|---|---|---|
| **Galaxy** | Galaxy GxIT XML wrapper | Env var `SPARMVET_PROFILE` set in XML `<environment_variables>` block | Filesystem — Galaxy mounts datasets into job directory |
| **IRIDA** | IRIDA plugin / iframe at launch | Env var `SPARMVET_PROFILE` + `SPARMVET_IRIDA_TOKEN` | REST API — files fetched via OAuth2 to local cache, then filesystem |
| **General server** | Sysadmin (Docker Compose / systemd) | Config file placed at `/etc/sparmvet/profile.yaml` by admin | Filesystem — NFS, local disk, or object storage mount |
| **Local PC** | Admin or developer | Config file at `~/.sparmvet/profile.yaml`, or project fallback | Filesystem — local disk |

All contexts **MUST** run the same Docker image. Only the deployment profile YAML differs.

---

### 3. Deployment Profile Schema (YAML)

A deployment profile is a single YAML file that declares the full deployment context. It replaces and extends the current connector YAML.

```yaml
# ─── Identity ────────────────────────────────────────────────────────────────
deployment_type: filesystem          # "filesystem" | "irida" | "galaxy"
deployment_name: "AMR Pipeline — Galaxy EU"   # human-readable label (shown in UI footer)

# ─── Default startup state ───────────────────────────────────────────────────
default_manifest: "manifests/amr/master.yaml"   # relative to project_root; OPTIONAL
                                                 # if absent → manifest selector shown (persona-gated)
default_persona: pipeline-static                 # OPTIONAL; overrides persona selector

# ─── Filesystem locations (all relative to project_root) ─────────────────────
project_root: "/data/pipeline/amr/"             # absolute base; all sub-paths resolve under this

locations:
  raw_data:      "inputs/"          # Location 1: raw external data
  manifests:     "manifests/"       # Location 2: pipeline manifest definitions
  curated_data:  "parquet/"         # Location 3: Tier 1 & 2 Parquet caches
  user_sessions: "sessions/"        # Location 4: user exports, T3 artifacts, session saves
  gallery:       "gallery/"         # Location 5: gallery assets

# ─── IRIDA block (only when deployment_type: irida) ──────────────────────────
irida:
  base_url: "https://irida.myinstitution.ca"
  project_id: 42
  auth: oauth2                      # token read from env var SPARMVET_IRIDA_TOKEN at runtime
  local_cache: "/tmp/sparmvet_cache/"   # where API-fetched files land; then treated as filesystem

# ─── Runtime ─────────────────────────────────────────────────────────────────
runtime:
  python_interpreter: "./.venv/bin/python"
```

**Required fields:** `deployment_type`, `locations` (all five sub-keys), `project_root`.
**Optional fields:** `default_manifest`, `default_persona`, `irida` block, `deployment_name`.

---

### 4. Bootloader Resolution Chain

`bootloader.py` resolves the active deployment profile through a four-level priority chain. The first match wins:

```
Priority 1 — Environment variable:
    SPARMVET_PROFILE=/path/to/profile.yaml
    Used by: Galaxy (XML wrapper), IRIDA (container launch), Docker Compose, systemd unit.

Priority 2 — User-level config file:
    ~/.sparmvet/profile.yaml
    Used by: local PC (scientist or admin places this once at setup).

Priority 3 — System-level config file:
    /etc/sparmvet/profile.yaml
    Used by: institutional server (sysadmin places at deploy time, no env var needed).

Priority 4 — Project dev fallback:
    config/connectors/local/local_connector.yaml   (current)
    → config/deployment/local/local_profile.yaml   (Phase 23 rename)
    Used by: developer running the app directly from the repo.
```

No manual configuration is needed if a higher-priority level is already set. The Bootloader logs which level was resolved at startup (INFO level).

---

### 5. Data Access Abstraction — The Connector Library

Different `deployment_type` values require different data acquisition logic. A new `libs/connectors/` library (Phase 23) implements an adapter pattern:

```
libs/connectors/
  src/connectors/
    base.py            # Abstract interface: resolve_paths(), fetch_data(), get_manifest_path()
    filesystem.py      # FilesystemConnector — reads profile locations directly
    irida.py           # IridaConnector — OAuth2 fetch → local cache → paths like filesystem
    galaxy.py          # GalaxyConnector — env var path overrides (thin wrapper over filesystem)
```

All connectors expose the **same interface** to the rest of the app. After `fetch_data()` completes (instantaneous for filesystem, async download for IRIDA), every path returned is a local filesystem path. The `DataOrchestrator`, `DataIngestor`, and `Bootloader` never need to know the source system — they always see local paths.

**Interface contract (abstract):**
```python
class BaseConnector:
    def resolve_paths(self) -> dict[str, Path]: ...   # returns the five location paths
    def fetch_data(self) -> None: ...                  # no-op for filesystem; downloads for IRIDA
    def get_manifest_path(self) -> Path | None: ...    # returns default_manifest path or None
    def get_default_persona(self) -> str | None: ...   # returns default_persona or None
```

---

### 6. Multiple Pipelines — One Image

The same Docker image is deployed multiple times for different pipelines (e.g., AMR, Plasmid, Virulence) by varying only the `SPARMVET_PROFILE` env var (or placing different profile files). Each pipeline deployment is fully isolated:

- **Galaxy**: One XML tool wrapper per pipeline. Each wrapper sets `SPARMVET_PROFILE` to a different profile YAML bundled in the image (or mounted from a Galaxy data library).
- **Institutional server**: Multiple Docker Compose services, each with a different `SPARMVET_PROFILE` env var.
- **Shared server (manifest selector)**: A single deployment with `default_manifest` absent from the profile. The persona-gated manifest selector allows scientists to pick their pipeline from the `manifests/` directory.

---

### 7. Manifest Selection — Who Controls It

| Scenario | default_manifest in profile | Manifest selector shown |
|---|---|---|
| Dedicated pipeline deployment (Galaxy, IRIDA, specific server) | Present — locked | No (hidden by persona gate or absent from UI) |
| General server, multiple pipelines | Absent | Yes (persona-gated: developer/project-independent only) |
| Local developer PC | Absent (or present for testing) | Yes (developer persona) |

Lower personas (`pipeline_static`, `pipeline_exploration_simple`) never see the manifest selector regardless of whether `default_manifest` is set — their UI template has the selector disabled. If `default_manifest` is absent AND the persona would hide the selector, the Bootloader raises a configuration error at startup.

---

### 8. IRIDA-Specific Considerations

IRIDA integrates via REST API only — no env var injection, no mounted volumes (unlike Galaxy). The integration pattern:

1. IRIDA launches the app container with `SPARMVET_PROFILE` pointing to an IRIDA profile.
2. `SPARMVET_IRIDA_TOKEN` env var carries the OAuth2 bearer token (injected by IRIDA at launch, never stored in the profile YAML).
3. `IridaConnector.fetch_data()` calls the IRIDA REST API to download project samples, metadata, and analysis results to `irida.local_cache`.
4. All subsequent app logic reads from `local_cache` — identical to a filesystem deployment.
5. Optionally, results can be POSTed back to IRIDA via the same OAuth2 token (Phase 23+ feature).

---

### 9. Deferred / Phase 23 Scope

- Rename `config/connectors/` → `config/deployment/` with code migration in Bootloader.
- Implement `libs/connectors/` with `FilesystemConnector`, `IridaConnector`, `GalaxyConnector`.
- Write Galaxy XML tool wrapper templates (one per pipeline).
- IRIDA OAuth2 fetch integration and result POST-back.
- Extend connector template YAML with new schema fields.
- Document admin setup steps per deployment context in `docs/deployment/`.

---

### 10. Relationship to Existing ADRs

- **ADR-031** (Path Authority): Extended. ADR-031 defined the five location keys; ADR-048 defines how those keys are populated across deployment contexts.
- **ADR-004** (YAML-Only Config): Deployment profiles are YAML — compliant.
- **ADR-003** (Thin Frontend): The connector abstraction lives in `libs/connectors/`, not in the UI — compliant.
- **Persona templates** (`config/ui/templates/`): Unchanged. Persona = who the user is. Deployment profile = where the system runs. These remain orthogonal.

---

### ADR-048 §11 Amendment — Connector Lifecycle (Option B, 2026-05-02)

**Previously:** `bootloader.get_location()` read paths directly from the raw profile YAML dict. The connector was never called at startup.

**Decision (Option B):** At `Bootloader()` instantiation, the bootloader now wires the full connector lifecycle:

1. `get_connector(profile)` — factory selects the connector class for this `deployment_type`.
2. `connector.fetch_data()` — runs data acquisition (no-op for filesystem; OAuth2 download for IRIDA). Startup print: `[Bootloader] Connector: FilesystemConnector — fetch_data()`.
3. `connector.resolve_paths()` — returns the five named location paths. These become the authoritative source for all location resolution.

`bootloader.get_location(key)` now reads from `self._resolved_locations` (output of `resolve_paths()`), not from the raw profile dict.

**Caching:** The connector is cached per profile path at the class level (`_resolved_locations_cache`). `fetch_data()` runs at most once per process even if `Bootloader()` is re-instantiated.

---

### ADR-048 §12 Amendment — `prefer_discovery` Profile Field (2026-05-02)

**New optional field in deployment profile YAML:**

```yaml
# Default: false (not set). When true, orchestrator strips source blocks before ingest.
prefer_discovery: true
```

**Behaviour when `true`:**
- `DataOrchestrator.materialize_tier1()` strips the `source` block from each manifest schema entry before passing it to the ingestor.
- The ingestor falls back to filename discovery in `raw_data_dir`, finding `*{schema_id}*.tsv` files.
- This mirrors production connector behaviour (Galaxy, IRIDA) where pipeline output is delivered to `raw_data_dir` by the pipeline itself.

**`source.path` in manifests is a development shortcut only.** It provides a concrete example data path so developers can run the manifest locally from the repo. In production (Galaxy, IRIDA), data is always delivered by the connector to `raw_data_dir` and discovered by schema ID name. The `source.path` field is never used when `prefer_discovery: true`.

**When to use `prefer_discovery: true`:** Pipeline personas (`pipeline-static`, `pipeline-exploration-simple`) and any profile that simulates production connector delivery. The pipeline test profile (`config/deployment/pipeline_test/pipeline_test_profile.yaml`) uses this field to simulate production behaviour during testing. Do NOT set on the local dev fallback profile — developers rely on `source.path` to run manifests from arbitrary locations.

---

## ADR-049: Per-Plot T3 Audit Scoping & Join-Key Propagation (Phase 22-J, 2026-04-25)

**Status:** IMPLEMENTED at HEAD `94bb917`, live-UI verified 2026-04-30 (§1 per-plot scoping passed). **AMENDED 2026-04-30 (AUDIT-1)**: the §12g.3 "silent conversion" rule for PK-column filters is removed — see [ADR-049a](#adr-049a-2026-04-30-amendment-pk-filter-allowed) below.

### Problem

Phase 22-I shipped a working but flat T3 audit pipeline: every node lives in one `t3_recipe: list` and applies to every plot. Two real workflows broke under that model:

1. **Per-plot context**: a row filter `value > 90` makes sense on a long-format AMR similarity plot but is wrong on a metadata QC plot. The flat model couldn't express "this filter is specific to this plot's analytical context."
2. **Justification plots**: when a sample is excluded for poor quality, the user often wants to *keep it visible* on the QC plot that justifies the removal. The flat model couldn't express "exclude S2 from analysis but keep it on the QC contamination plot as evidence."

A third concern surfaced from data-integrity review: dropping a join-key column silently corrupts every joined plot. The flat model had no notion of "which columns are structurally protected."

### Decision

**Storage**: replace `t3_recipe: list` with `t3_recipe_by_plot: dict[plot_subtab_id, list[RecipeNode]]`. Each plot has its own stack. Switching plots swaps the visible stack in the right-sidebar audit panel.

**Propagation**: at audit-promotion time, eligible nodes (drop_column non-key, exclusion_row, color/shape/fill aesthetic) trigger a three-option dialog:
- This plot only
- All plots
- All plots except (multiselect)

The "All except" choice captures the justification-plot case directly without requiring the user to apply globally then manually delete from one plot.

**Linked-id propagation**: a node "applied to N plots" is N RecipeNode dicts sharing the same `id`. Linked deletion: clicking 🗑 on any copy removes all copies. Edits propagate by id.

**Primary-key set**: union of all join keys declared in `join_manifests.*.recipe[*].on/left_on/right_on`. Includes long-format secondary keys.

**Authoring rules around primary keys**:
- Drop column on PK: blocked absolutely.
- Filter row on PK: silent convert to `exclusion_row` (audit reads honestly: "Excluded sample S2" not "Filtered to ¬S2").
- `primary_key_warning: true` on every PK-touching node, persisted through ghost save and into the export Methods section as `⚠️ [Primary key affected]`.

**No automatic inheritance for new plots**: if the manifest gains a plot after a propagation, that new plot does NOT inherit the prior "all plots" decision. Re-propagation is explicit.

**Backward compatibility**: legacy ghosts with flat `t3_recipe: [...]` are loaded into an `__legacy__` orphaned bucket and surfaced in the audit panel for re-targeting.

### Rationale

- **Per-plot scoping** matches user mental model: audit decisions are usually local. Forcing a global model created friction whenever they switched plots.
- **Linked-id propagation** keeps the "I made one decision, applied many places" framing intact while allowing convenient bulk-delete.
- **Silent filter→exclusion conversion** trades a small UX surprise for a meaningful improvement in audit-report honesty. The Methods section now reads "Excluded sample S2 (reason: …)" instead of obscuring the deliberate removal as a positive selection.
- **Drop-PK absolute block** is a structural safety rail — if the user needs anonymization in the report, that is a separate concern outside T3's analytical-adjustment scope.
- **Primary-key warning persistence**: the warning is informational at authoring time and a permanent marker in the report. Reviewers see that PK adjustments were made and how the user justified them.

### Implementation references

- Spec (technical): `.claude/rules/ui_implementation_contract.md` §12g.
- User-facing explanation: `docs/user_guide/audit_pipeline.qmd`.
- Task tracking: `.claude/tasks/tasks.md` Phase 22-J (sub-tasks 22-J-1 through 22-J-13, decision matrix 22-J-D1 through 22-J-D13).

### Relationship to existing ADRs

- **ADR-037** (Gallery Browser): Gallery transplants now also receive a propagation dialog when targeting non-key columns. Existing gallery clone behaviour preserved as the default per-plot choice.
- **ADR-044** (Persona-Gated Audit Stack): Unchanged. Persona gates the right-sidebar visibility; per-plot scoping is orthogonal.
- **ADR-046** (Scientific Audit Protocol): Strengthened. The audit protocol now records propagation choices and primary-key warnings explicitly.
- **ADR-047** (Tier-Aware Export Bundle): The export Methods generator now recognises `primary_key_warning: true` and prepends a textual marker.

### ADR-049a (2026-04-30 amendment): PK-filter ALLOWED

**Trigger:** Phase 22-J live UI testing (2026-04-30) by @evezeyl found the §12g.3 silent-conversion rule confusing in practice — `sample_id == "S2"` is intuitively a *select*, not a *remove*, and silently flipping it to `ne` violated the principle of least surprise. Captured as AUDIT-1.

**Amended rule:**
- Filtering on a PK column is **ALLOWED**. The user's operator is preserved verbatim. Node remains a `filter_row`.
- `primary_key_warning=True` is still set; the warning banner appears in the propagation modal and the audit panel.
- Drop-column on a PK column **remains BLOCKED** (unchanged).
- Users who want exclusion semantics author `ne` or `not_in` directly. The audit report's "⚠️ \[Primary key affected\]" prefix still flows through (carried by `primary_key_warning`, not by node_type).

**Implementation commit:** `3c6195f` (2026-04-30) — `app/handlers/home_theater.py` lines around 2183-2193: `node_type = "filter_row"` unconditionally for PK columns; the previous `if is_pk: ... node_type = "exclusion_row"` branch removed.

**Rule of thumb:** **the operator is the truth**. The PK warning is the safety rail. We trust the user to read the warning and pick the operator they actually mean.

---

## ADR-050: Orchestrator Three-Path Materialization & Join-Key Normalisation (2026-04-30)

**Status:** IMPLEMENTED — `app/modules/orchestrator.py`, discovered and fixed in session 7.

### Problem

`DataOrchestrator.materialize_tier1(project_id, collection_id, output_path)` had two silent bugs that caused wrong data to be served to plots:

1. **Wrong base ingredient**: `DataAssembler` uses `list(ingredients.keys())[0]` as the base frame for all joins. The orchestrator was passing all project `data_schemas` in manifest iteration order, so the alphabetically/order-first schema became the assembly base — not the collection's declared first ingredient.

2. **No path for bare data schemas**: when a plot's `target_dataset` pointed to a `data_schemas` entry (not an `join_manifests` entry), the orchestrator fell to a legacy fallback that picked the first declared assembly — completely wrong data.

3. **Join key dtype mismatch**: Polars requires join key columns to have matching dtypes across left/right frames. `Categorical` ≠ `String` even when both hold string data, causing `SchemaError` on multi-ingredient assemblies.

### Decision

**Path A — Bare data schema**: when `collection_id` is not in `join_manifests` but IS in `ingredients` (ingested raw sources), write the ingredient directly to parquet without any assembly step.

**Path B — Named assembly**: `collection_id` found in `join_manifests`. Build `assembly_ingredients` as an ordered dict of ONLY the collection's declared `ingredients:` list in declaration order — preserving the intended base frame.

**Path C — Legacy fallback**: `collection_id` not found anywhere. Falls to first declared assembly for backward compat. Should never fire in a well-formed manifest.

**Join key normalisation**: before calling `DataAssembler`, scan all recipe steps for `on`, `left_on`, `right_on` fields. Cast those columns to `String` on the relevant ingredient frames. Handles both symmetric and asymmetric join keys. Applied per-ingredient to avoid unnecessary casts.

### Ordering law (DataAssembler)

The first ingredient in the `assembly_ingredients` dict IS the base frame. This is not configurable — `DataAssembler.assemble()` hardcodes `first_key = list(self.ingredients.keys())[0]`. The orchestrator MUST preserve declaration order from the manifest's `ingredients:` list.

### Rationale

- Correcting ingredient order eliminates the most common "wrong columns in plot" class of bug without any schema changes.
- Path A allows `target_dataset` to point to a bare source schema — a valid and common pattern (e.g. `amr_heatmap → ResFinder`). Without Path A, these plots always got wrong data from the fallback.
- `String` cast before join is the safe common denominator. Downstream consumers that need `Categorical` can re-cast. The alternative (inferring which dtype to upcast to) is fragile.

### Anti-pattern (removed)

`if not out_p.exists(): orchestrator.materialize_tier1(...)` guards were preventing recomputation when manifests or code changed. Removed from all call sites. `DataAssembler` internal hash-check (ADR-024) handles caching correctly and is faster than checking file existence.

### Implementation reference

`app/modules/orchestrator.py` — `materialize_tier1()` method.
`manifest_data_contract_rules.md` §11–§14 — full documentation with code examples.

---

## ADR-051: `home_theater.py` Decomposition — Phase 24

**Status:** IMPLEMENTED (2026-05-01) — Steps 24-A through 24-D landed on `dev`; final layout below. `home_theater.py` is now 1,278 lines (was 2,853 at pre-flight; -55.2%).
**Context:** `app/handlers/home_theater.py` has grown to 2,547 lines after absorbing Phase 21 (Unified Home Theater) and Phase 22-J (per-plot T3 audit scoping). This reproduces the exact monolith problem that motivated ADR-045 (`server.py` at 2,362 lines). Phase 21 is now stable, making this the right moment to design the split before Phase 23 (deployment) adds further complexity.

**Decision:** Split `home_theater.py` into a thin coordinator (~900 lines) plus three focused handler modules and one pure module, following the ADR-045 Two-Category Law and `define_server(input, output, session, *, ...)` contract.

### Boundary Rule (inherited from ADR-045)

| Category | Location | Rule |
|---|---|---|
| Pure data functions | `app/modules/` | No Shiny imports. Importable from headless scripts. |
| Shiny wiring | `app/handlers/` | All `@render.*`, `@reactive.*`. Never imported outside Shiny context. |

Sub-handlers are called from inside `home_theater.define_server()`, not from `server.py`. This nests one delegation level within the Home tier — `server.py` still has a single `define_home_theater_server(...)` call.

### Files (as implemented)

**`app/modules/t3_recipe_engine.py`** (Step 24-A + 24-D folded prep) — pure helpers:
- `_apply_filter_rows(lf, filter_rows)` — LazyFrame predicate application with
  dtype-aware coercion. (Originally a closure inside `define_server`.)
- `_op_label(op)` — symbolic label for filter operators; lifted in Step 24-D
  so both `export_handlers` and `filter_and_audit_handlers` import one copy.

**`app/handlers/session_handlers.py`** (Step 24-B) — session persistence UI:
- `define_session_server(...)` registers `session_management_ui`,
  `_handle_session_import`, `_handle_session_actions`, `_restore_session`.
- Kwargs: `session_manager`, `current_persona`, `home_state` (3 — leaner than
  originally planned).

**`app/handlers/export_handlers.py`** (Step 24-C) — export pipeline:
- `define_export_server(...)` registers `system_tools_ui`,
  `export_bundle_download`, `_export_bundle_filename`.
- `export_audit_report_ui`, `export_audit_report_download`, `_audit_report_filename`
  **deleted 2026-05-04** (EXPORT-REDESIGN-1) — audit trail now auto-included in
  `report.qmd` T3 Audit Trail section; see `.claude/design/export_specification.md`.
- Kwargs (13): `bootloader`, `orchestrator`, `viz_factory`, `current_persona`,
  `active_cfg`, `tier1_anchor`, `tier_reference`, `tier3_leaf`, `tier_toggle`,
  `applied_filters`, `home_state`, `safe_input`, `active_home_subtab`.

**`app/handlers/filter_and_audit_handlers.py`** (Step 24-D) — filter UI + T3
audit + propagation modal kept in **one file** (deviation from initial plan).
- `define_filter_audit_server(...)` registers `sidebar_filters`,
  `filter_rows_ui`, `filter_form_ui`, `filter_controls_ui`, `_filter_add_row`,
  `_filter_apply`, `_filter_reset`, `_col_drop_to_audit`,
  `_column_presence_per_plot`, `_open_propagation_modal`,
  `_handle_propagation_confirm`, `_plot_has_column`,
  `_clear_filters_on_t3_apply`, the `_make_remove_handler` factory + 50-row
  registry, and a private `_last_apply_count = reactive.Value(0)`.
- Why one file: `_filter_apply`, `_col_drop_to_audit`, and
  `_handle_propagation_confirm` share `_propagation_scratch` and call into
  `_open_propagation_modal`. Splitting would force exposing scratch state
  across module boundaries.
- Kwargs: `applied_filters`, `_pending_filters`, `_propagation_scratch`,
  `home_state`, `tier_toggle`, `active_home_subtab`, `safe_input`, plus six
  closure callables from `define_server` (`_resolve_active_spec`,
  `_resolve_active_lf`, `_spec_discrete_axes`, `_t3_drop_columns`,
  `_all_plot_subtab_ids`, `_plot_label`).

### Shared State Protocol (held)

`applied_filters`, `_pending_filters`, and `_propagation_scratch` remain as
`reactive.Value` instances created inside `home_theater.define_server()`
(Home-scoped, not global). They are passed as keyword arguments to
`define_filter_audit_server(...)` — same pattern as `server.py` → handlers
for `tier1_anchor`, `active_cfg`, etc.

### Verification (each step independently)

- 90/90 unit tests pass (incl. 21-case filter regression in
  `test_filter_operators.py`).
- App import clean: `from app.src.main import app`.
- 12/12 Playwright smoke pass (10 + 2 persona-skip), ~20s. Includes all 4
  filter pipeline tests: form_renders, add_filter_row, apply_filter_no_crash,
  filter_reset_clears_rows.

### Line-count comparison

| Phase | `home_theater.py` LoC |
|---|---|
| Pre-flight (2026-04-30 tag `pre-phase24-20260430`) | 2,853 |
| After 24-A (`_apply_filter_rows` extracted) | 2,759 |
| After 24-B (session block extracted) | 2,545 |
| After 24-C (export block extracted) | 2,017 |
| After 24-D (filter + audit block extracted) | 1,278 |
| **Δ** | **-1,575 (-55.2%)** |

### Implementation reference

- Source file: `app/handlers/home_theater.py`.
- Refactor protocol followed: `.claude/knowledge/archive/refactor_protocol_phase24.md`.
- Per-step change manifests: `.claude/tasks/tasks_phase24.md`.
- Two-Category Law: `app/handlers/__init__.py`.

---

## ADR-052: Left Sidebar Restructure & Persona Template Extensions — Phase 25

**Status:** FULLY IMPLEMENTED (steps A–O, 2026-05-01). All substeps complete including cascade enforcement (25-L), doc rewrite (25-M), and persona name anti-pattern elimination (25-O). Remaining tech debt: 25-N (legacy test stubs).

**Implementation audit (2026-05-01):**

| Step | Commits | Verified by |
|---|---|---|
| 25-A | 8f6e41c, a99e126 | qa smoke 10/10 |
| 25-B | 5ac91a3 | unit (test_persona_validator 12/12) + qa smoke |
| 25-C | e792734, 65f48b8, 806a72b | qa smoke after each commit |
| 25-D | dff0092 | qa + pipeline-static smoke (right sidebar absent) |
| 25-E | b817506, fd6dea2 | qa smoke 10/10 |
| 25-F | 29bf346 | qa smoke 10/10 (new `data_import_handlers.py`) |
| 25-G | a92ae53 | qa smoke 10/10 (audit format radio + active-session export) |
| 25-H | 4bc1e05 | qa smoke 10/10 (new `single_graph_export_handlers.py`) |

**Deviations from the design (status):**

1. ~~**§52-7 (Quarto-native PDF/DOCX)** — Pandoc fallback~~ — **CLOSED** in 25-K (commit `5f4c491`). `render_audit_report(fmt=...)` calls `quarto render --to <fmt>` natively; `pandoc_convert` and `pandoc_available` removed from `app/modules/exporter.py`.
2. ~~**Audit report visibility — hardcoded persona set**~~ — **CLOSED** in 25-K. New `audit_report_enabled` flag added to all 6 persona templates; `export_audit_report_ui` gates on `bootloader.is_enabled("audit_report_enabled")`. `qa` now sees the panel as expected.
3. **Per-session Export buttons removed** — accepted design choice. 25-G replaced the broken per-session `session_export_{sk}` download buttons (no registered backend) with one header-level `session_export_active` button keyed off the active `home_state` session_key. Per-session `Export` is no longer offered in the UI; restore + delete remain.

**Open work tracked separately:**

- **25-L** — ~~PersonaManager dependency-cascade enforcement~~ — `app/modules/persona_manager.py` deleted (2026-05-02, unused dead code). Dependency-cascade enforcement now lives entirely in `bootloader._load_persona_config()`. `bootloader.is_enabled()` is the sole flag-check API; persona name checks are prohibited.
- **25-M** — `ui_implementation_contract.md` rewrite for Phase 25 panel structure.

**Context:** Phase 24 closed cleanly. Visual inspection of the running app and a co-design session (2026-05-01) identified four categories of work: (1) persona-gating bugs and missing `bootloader.is_enabled()` calls throughout the left sidebar; (2) the right sidebar layout container always occupying 340px even when hidden for pipeline personas; (3) the left sidebar accordion having a flat, undifferentiated "System Tools" blob that mixes export, session, and data-ingestion concerns; (4) two new persona-template fields needed to support the production/testing-mode architecture and manifest-locked pipeline personas.

**Decisions:**

### 52-1: Right Sidebar — Conditional Layout (Option A)

The right sidebar container (`ui.sidebar(position="right")` in `app/src/ui.py`) is **excluded at layout build time** for pipeline-static and pipeline-exploration-simple. Previously, `right_sidebar_content_ui` returned `ui.div()` (empty) which left the 340px container in the DOM and wasted screen width.

Fix: read `os.getenv("SPARMVET_PERSONA")` in `ui.py` at startup. If persona ∈ `{pipeline-static, pipeline-exploration-simple}`, omit the `ui.sidebar(right)` argument entirely from `ui.layout_sidebar(...)`. The center column then fills full width. No handler changes required — the persona is immutable for the session lifetime.

### 52-2: Persona Template — New `manifest_selector` Section

All `config/ui/templates/*_template.yaml` files gain a `manifest_selector` block:

```yaml
manifest_selector:
  visible: true          # false = Manifest Choice dropdown hidden from UI
  fixed_manifest: null   # Required when visible=false — path to the manifest YAML
```

**Rule:** pipeline-static and pipeline-exploration-simple → `visible: false` (automated pipeline personas; one pipeline produces one data type, one manifest). All exploration personas → `visible: true`.

**Validator:** `PersonaValidator` (new pure module `app/modules/persona_validator.py`) checks at startup: if `visible=false` then `fixed_manifest` must be a non-null path to an existing file. Validator is called from `app/src/server.py` before `define_server()`.

### 52-3: Persona Template — New `testing_mode` Flag

```yaml
testing_mode: true   # true  = use default test data paths from manifest
                     # false = data injected by pipeline OR chosen by user
```

**Principle (architectural invariant):** pipeline-static and pipeline-exploration-simple are **always production-mode** (`testing_mode: false`). Data arrives via pipeline channels (Galaxy history, Nextflow outputs, etc.). Testing of pipeline integrations is done by switching to a more capable persona (developer or pipeline-exploration-advanced). Pipeline personas never need `testing_mode: true` because testing adds functionality — it never reduces it.

Exploration personas (advanced, project-independent, developer, qa) default to `testing_mode: true` — the data selector pre-fills from manifest default test data paths but the user can override.

### 52-4: Left Sidebar Accordion Restructure

The existing flat "System Tools" accordion panel is split into three named panels:

| New panel | Contents | Was |
|---|---|---|
| **Manifest Choice** | Manifest selector (visible/hidden per persona) | "Project Navigator" |
| **Data Import** | Data directory selector, metadata TSV replacement, multi-file/Excel ingestion | Buried in System Tools |
| **Global Project Export** | Bundle name, quality, plot format, audit report format, download | "System Tools — Export Bundle" |
| **Session Management** | Session import/export (.zip) | "System Tools — Session" |
| **Single Graph Export** | Single-plot + data + manifest fragment download | New (un-deferred from Phase 22) |

The "Filters" accordion panel is unchanged structurally. Data ingestion slots (metadata replacement, multi-file) move from System Tools into Data Import.

### 52-5: Gallery for project-independent

`project-independent_template.yaml`: `gallery_enabled` changed from `false` (absent) to `true`. The Gallery feature flag is documented as an independent config knob (ADR-038 / rules_persona_feature_flags.md). This change makes the Gallery accessible to project-independent users.

### 52-6: Test Lab Rename

`developer_mode_enabled` nav pill renamed from "Dev Studio" to "Test Lab". Same gate flag. Purpose: tooling for testing and mock data generation — "Test Lab" better communicates this intent.

### 52-7: Quarto-based Report Rendering (replaces Pandoc)

Audit report exports (HTML / PDF / DOCX) will be rendered server-side via Quarto, bundled with the Docker container. Quarto handles all three formats natively. The current code writes a `.qmd` template into the export bundle zip but does not run Quarto server-side — Phase 25 adds the server-side render step. Pandoc as a separate dependency is removed. Quarto is an acceptable datascience dependency and will ship in the Docker image.

### 52-8: Passive Exploration — Capability Column Added to Persona Matrix

Two new capability columns formalise existing but undocumented behaviour:

- **`passive_exploration`**: user can apply filters and drop columns to explore the view (T1/T2 — plot updates temporarily, nothing saved, no audit trail). Was already implemented; not documented in the matrix.
- **`t3_audit`**: user can promote filters/drops to the T3 audit pipeline (right sidebar, propagation modal, reason gatekeeper, recipe export).

| Persona | passive_exploration | t3_audit |
|---|---|---|
| pipeline-static | ❌ | ❌ |
| pipeline-exploration-simple | ✅ | ❌ |
| pipeline-exploration-advanced | ✅ | ✅ |
| project-independent | ✅ | ✅ |
| developer | ✅ | ✅ |
| qa | ✅ | ✅ |

### Implementation reference

- Design document: `EVE_WORK/daily/2026-05-01/persona_functionality_side_bars_v3_clean.csv`
- Companion persona template spec: `EVE_WORK/daily/2026-05-01/persona_template_new_fields.md`
- Refactor protocol: `.claude/knowledge/archive/refactor_protocol_phase24.md` (reused)
- Per-step change manifests: `.claude/tasks/tasks_phase25.md` (to be created at phase start)

## ADR-053: Flag-Only Persona Gating — Prohibition on Persona Name String Comparisons

**Status:** IMPLEMENTED (Phase 25-O, 2026-05-01)

**Context:** A persona is an abstract named preset — a convenient bundle of feature flags stored in a YAML template. Runtime code was comparing `bootloader.persona` against hardcoded name strings (`"pipeline-static"`, `"pipeline-exploration-advanced"`, etc.) to make UI and logic decisions. This meant that any custom persona template (different flag combination, novel name) would be invisible to those checks, silently breaking the features it was meant to configure.

Seven violation sites were found across 5 files: `ui.py`, `gallery_handlers.py`, `export_handlers.py`, `home_theater.py` (×2), and the `_T3_PERSONAS` module-level set.

**Decision:**

1. **Prohibition:** Runtime application code MUST NOT compare `bootloader.persona` against name strings. All behavioral branching must use `bootloader.is_enabled(flag_name)`.

2. **New flag `t3_sandbox_enabled`:** Added to all six persona templates and the `PersonaValidator._REQUIRED_FLAGS` list. Controls: T3 wrangling tier visibility in the tier toggle, right sidebar audit panel inclusion in the layout, Gallery "Send to T3" button, T3 data slice inclusion in export bundle.
   - `false`: `pipeline-static`, `pipeline-exploration-simple`
   - `true`: `pipeline-exploration-advanced`, `project-independent`, `developer`, `qa`

3. **Cascade:** `t3_sandbox_enabled` is a child of `interactivity_enabled` in Group B. If `interactivity_enabled=False`, `t3_sandbox_enabled` is forced to `False` by the bootloader cascade (same as `comparison_mode_enabled`, `session_management_enabled`, etc.).

4. **Corollary:** If future behavior needs gating but no flag exists, add a flag to all templates first. Never add a persona name check.

**Rule documented in:** `.claude/rules/rules_persona_feature_flags.md §Anti-Pattern`

---

## ADR-054: Bootloader — Component Architecture & Startup Contract (2026-05-02)

**Status:** IMPLEMENTED (component existed since ADR-031/ADR-048; this ADR formalises the full contract)

**Context:** `app/src/bootloader.py` is the first module executed at app startup. It is the single authority for deployment profile resolution, persona loading, feature flag evaluation, and path resolution. Prior to this ADR, its behaviour was spread across ADR-031 (path authority), ADR-026 (persona concept, now superseded), and ADR-048 (deployment profile chain). No single document described it as a complete component with a public API, startup sequence, caching model, and known limitations. The deletion of `app/modules/persona_manager.py` (2026-05-02) made the bootloader the sole owner of all persona/flag logic, making this gap acute.

**Decisions:**

### 1. Startup sequence (order is contractual)

At `Bootloader()` instantiation:

1. **Profile resolution** — 4-level priority chain (ADR-048 §4); prints resolved path and level to stdout.
2. **Profile load** — YAML loaded and cached by absolute path string (class-level `_connector_cache`).
3. **Connector lifecycle** — `get_connector(profile)` selects connector class; `connector.fetch_data()` runs data acquisition (no-op for filesystem); `connector.resolve_paths()` returns authoritative location paths stored in `self._resolved_locations`. Startup print: `[Bootloader] Connector: <ClassName> — fetch_data()`. The connector result is cached class-level in `_resolved_locations_cache` keyed by profile path — `fetch_data()` runs at most once per process. (ADR-048 §11)
4. **Persona resolution** — `persona=` kwarg > `SPARMVET_PERSONA` env var > `default_persona` in profile > `ValueError`. Raises at startup with a clear message if no persona source is found.
5. **Persona load + cascade** — template YAML loaded; dependency cascade applied (`_load_persona_config`); prints resolved absolute template path to stdout.
6. **Project discovery** — scans `locations["manifests"]` directory for YAML manifests.

### 2. Public API — sole stable interface for the rest of the app

| Method / attribute | Return type | Purpose |
|---|---|---|
| `bootloader.is_enabled(flag: str) → bool` | bool | Check if a UI feature flag is active after cascade. **The only permitted flag-check mechanism.** |
| `bootloader.get_location(key: str) → Path` | Path | Resolve a named path (`raw_data`, `manifests`, `curated_data`, `user_sessions`, `gallery`) from `self._resolved_locations` — the output of `connector.resolve_paths()`. Not read from the raw profile dict. |
| `bootloader.get_manifest_selector() → dict` | dict | Returns `{visible: bool, fixed_manifest: str|None}` from persona template. |
| `bootloader.get_testing_mode() → bool` | bool | Returns `testing_mode` from persona template. |
| `bootloader.get_automation_setting(key, subkey)` | Any | Returns values from persona template `automation:` block (e.g. ghost_save frequency). |
| `bootloader.persona` | str | Active persona ID (shortname). **Read-only reference only** — never use for behavioral branching (ADR-053). |
| `bootloader.deployment_level` | int (1–4) | Which profile resolution level was used. |
| `bootloader.available_projects` | dict | `{project_id: yaml_path}` map from manifest scan. |

### 3. Caching model

Both profile and persona configs are cached at the **class level** (`_persona_cache`, `_connector_cache`). This means:

- A second `Bootloader()` instantiation in the same process with the same persona/profile hits the cache with zero I/O.
- Tests that call `bootloader.set_persona()` to switch personas do NOT re-read the file if the persona was previously loaded.
- Cache is keyed by persona ID string and absolute profile path string respectively.
- There is no cache invalidation mechanism — profiles and templates are treated as immutable for the process lifetime.

### 4. Persona ID → template path coupling (known limitation)

`SPARMVET_PERSONA` accepts a shortname ID, not a file path. The template path is constructed as:

```
config/ui/templates/<persona_id>_template.yaml
```

**Consequence:** persona ID and filename prefix are coupled. A custom deployment with a differently-named template file must match the filename prefix to the env var value. There is no override mechanism to point at an arbitrary file path.

**Forward-looking enhancement (not yet implemented):** Allow `SPARMVET_PERSONA` to accept an absolute file path as well as a shortname ID — if the value starts with `/` or `./`, treat it as a path; otherwise treat it as a shortname. This would decouple naming from filesystem layout for custom deployments.

### 5. Flag cascade

`_load_persona_config()` applies two cascade rules after loading the raw YAML:

- **Group B:** `interactivity_enabled: false` forces to `false`: `t3_sandbox_enabled`, `comparison_mode_enabled`, `session_management_enabled`, `export_enabled`, `audit_report_enabled`. A WARNING is printed for each suppressed flag.
- **Group C:** `import_helper_enabled: false` forces `data_ingestion_enabled: false`. WARNING printed.
- **Profile override:** `data_ingestion_enabled: false` in the deployment profile is an absolute override regardless of template value (automated-pipeline deployments push data; users cannot upload).

### 6. Startup print contract

The bootloader always prints two lines to stdout at startup:

```
[Bootloader] Profile resolved at level N (<source label>): /absolute/path/to/profile.yaml
[Bootloader] Persona: <id> → /absolute/path/to/config/ui/templates/<id>_template.yaml
```

These lines are the canonical audit trail for "what config was this session using." Any WARNING lines for cascade suppressions appear after the Persona line. Tests and CI can assert on these lines.

### 7. Persona as file path — ADR-054 amendment (2026-05-02)

**Problem with shortname coupling:** The original design required `SPARMVET_PERSONA=developer` to map to `config/ui/templates/developer_template.yaml` by filename convention. This prevented custom personas from living outside that directory and required all deployment tooling (Galaxy XML, Docker Compose, IRIDA) to know the internal directory layout of the image.

**Decision:** `SPARMVET_PERSONA` (and `default_persona` in deployment profiles) now accepts either an **absolute file path**, a **relative file path**, or a **legacy shortname**. The bootloader detects the form by presence of `/`, `\`, or `.yaml` suffix. Shortnames resolve to `config/ui/templates/<id>_template.yaml` for backward compatibility with existing developer workflow.

**Consequences:**

- `bootloader.persona` = the raw value passed (path or shortname) — used only for cache key construction and startup print.
- `bootloader.persona_path` = the resolved absolute `Path` object — used for I/O and validation.
- `bootloader.persona_display_name` = `display_name` from config → `persona_id` → raw value. This is what the UI shows; never a path.
- `current_persona` reactive (server.py) now holds `bootloader.persona_display_name`, not the raw path or shortname.
- `PersonaValidator` Rule 1 (persona_id must match filename) removed — filename is no longer meaningful.
- Any persona config file can live anywhere: bundled in a Docker image at `/profiles/`, on a network share, or in the repo at any depth.

**Galaxy / multi-pipeline pattern:**

```xml
<!-- Each pipeline XML wrapper sets its own persona file path -->
<environment_variable name="SPARMVET_PERSONA">/profiles/amr_pipeline_persona.yaml</environment_variable>
```

Or embed in the deployment profile so only one env var is needed at launch:

```yaml
# amr_profile.yaml
default_persona: /profiles/amr_pipeline_persona.yaml
```

**Documentation:** `docs/reference/environment_variables.qmd`, `.claude/rules/rules_persona_feature_flags.md`

---

## ADR-055: CSS Theme Architecture — Externalised Stylesheet & Per-Persona Override (2026-05-02)

**Status:** IMPLEMENTED

**Context:** `CSS_THEME` was a 150-line Python string embedded in `app/src/ui.py`. It was invisible to CSS tooling (linters, formatters, IDEs), impossible to override per-deployment without editing Python, and contained a latent bug (a CSS comment written as `# text` rather than `/* text */`).

**Decision:**

1. Extract the stylesheet to `config/ui/theme.css` — the authoritative base stylesheet, sectioned with CSS comments. This file is the single place to edit global UI styling.
2. `app/src/bootloader.py` gains a new public method `get_theme_css_path()` that reads the `theme_css` key from the active persona template (falls back to `"config/ui/theme.css"` if not set).
3. `app/src/ui.py` reads the CSS file via `bootloader.get_theme_css_path()` at module load time and injects it via `ui.tags.style()`.
4. All six persona templates (`config/ui/templates/*_template.yaml`) declare `theme_css: "config/ui/theme.css"` after the `logic_access` line, making the extension point explicit.

**Consequences:**

- A deployment creates `config/ui/my_org_theme.css` and sets `theme_css: "config/ui/my_org_theme.css"` in its persona template — no Python changes required for branding.
- The base theme (`config/ui/theme.css`) remains available to any persona that does not override.
- CSS is now editable with standard CSS tooling and diffable in version control.

---

## ADR-056: View Title Banner Pattern & "Test Lab" Rename (2026-05-02)

**Status:** IMPLEMENTED

**Context:** Blueprint Architect, Test Lab, and Gallery views each had a bare `h4(..., class_="centered-header")` + paragraph + `hr` as their page heading — visually disconnected from the rest of the app chrome. The right sidebar (Dev Inspector / Gallery Explorer) cards appeared as plain static text with no structural match to the Home "Pipeline Audit" sidebar. Additionally the Python module `dev_studio.py` used the label "Developer Studio: Synthetic Engine" in its heading while the nav pill said "Test Lab" — inconsistent naming.

**Decisions:**

1. **`.view-title-banner` CSS component** — a new reusable class provides a rounded, shadowed banner with two text tiers (Primary bold ~1rem, Secondary normal ~0.78rem muted). Used for all view headings. Added to `config/ui/theme.css`.

2. **Rename "Developer Studio" → "Test Lab"** everywhere in user-visible text. The Python module remains `dev_studio.py` (internal name). The old name "Developer Studio" is recorded here as a legacy alias. The nav pill label "Test Lab" is canonical.

3. **Banner texts (all two-line):**
   - Gallery: "📚 Gallery Inspiration" / "Browse visual recipes for inspiration. Did you see a nice figure? Send us a request for recipe implementation."
   - Test Lab: "Test Lab: Synthetic Engine" / "Generate mock datasets to verify pipeline robustness across any schema."
   - Blueprint Architect: "Blueprint Architect Flight Deck" / "Pipeline overview — helps you build manifests."

4. **Right sidebar for Gallery and Test Lab** — structure deferred; functionality not yet defined. Sidebar cards retain placeholder content until ADR-05x specifies Dev Inspector and Gallery Explorer behaviour.

**Consequences:**

- All three views open with a visually consistent, branded top-of-content banner.
- `dev_studio.py` heading string changed from "Developer Studio: Synthetic Engine" to "Test Lab: Synthetic Engine".
- No functional changes to left/right sidebar content in this ADR.

---

## ADR-057: Gallery Sidebar Refactor — Internal Sidebar → nav_sidebar Accordion (2026-05-02)

**Status:** IMPLEMENTED

**Context:** `gallery_viewer.render_explorer_ui()` returned a `ui.layout_sidebar()` with a 280px internal sidebar carrying the recipe selector, clone button, and all three taxonomy filter groups (Family / Data Pattern / Difficulty). This pattern was inconsistent with Home, Blueprint, and Test Lab, all of which keep interactive controls in the persistent left `#nav_sidebar`. The internal sidebar wasted horizontal space and prevented the gallery preview from using the full theater width.

**Decisions:**

1. **Gallery filter UI moves to `#nav_sidebar`** via the `sidebar_tools_ui` Gallery branch in `home_theater.py`. The filter accordion is structured as three `ui.accordion_panel()` sections — Family, Data Pattern, Difficulty — plus a bottom Apply button, mirroring Home's Filters panel layout.

2. **Recipe selector and clone button** move to the top of the `sidebar_tools_ui` Gallery branch (above the filter accordion) — they are the primary navigation controls for the view and belong with the nav tools, not embedded in the content.

3. **Gallery main content** (`gallery_tech_tabs` + educational pane) is rendered as a plain full-width `ui.div()` — no `ui.layout_sidebar()` wrapper.

4. **Right sidebar ("Gallery Explorer")** — currently a static card with help text. Deferred to a future ADR once Gallery Explorer functionality is defined.

**Consequences:**

- `gallery_viewer.render_explorer_ui()` no longer calls `ui.layout_sidebar()`.
- `home_theater.py` `sidebar_tools_ui` Gallery branch replaces the "Discovery Mode Active" placeholder with recipe selector + accordion filters.
- Reactive inputs (`gallery_recipe_select`, `gallery_filter_*`, `btn_apply_gallery_filters`) remain at the same IDs — no changes to `gallery_handlers.py` reactive logic.
- `gallery_viewer.render_explorer_ui()` still builds the accordion filter UI via a helper so both callers (sidebar_tools_ui and any future modal) can reuse it.

---

## ADR-058: Data Import — Explicit Assignment Table (IMPORT-1, 2026-05-02)

**Status:** IMPLEMENTED

**Context:** When a user uploads data files, the app needs to know which uploaded file maps to which dataset ID in the manifest. Two options were considered:

- **Option A (naming convention):** infer dataset ID from filename (e.g., `metadata.tsv` → `metadata`). Fast but brittle — breaks when files are renamed or when multiple datasets share a common naming root.
- **Option B (explicit table):** after upload, show a `filename → [dataset dropdown]` assignment table. User assigns each file explicitly.

**Decision:** Option B — explicit assignment table.

Rationale: users uploading real data will often have files with institution-specific names (e.g., `NVI_AMR_2024_export.tsv`, not `amr_profile.tsv`). Guessing by filename is unreliable and provides no recovery path. The assignment table makes the mapping explicit, auditable, and reversible.

**Implementation:**

1. `data_import_handlers.py` — rewritten to:
   - Render `data_import_assignment_ui`: one row per uploaded file, each with a `filename` label + dataset-ID dropdown (`input_select(f"data_import_assign_{i}")`), plus a single **Apply** button and per-file error display.
   - On Apply: run `MetadataValidator.validate()` per file; surface errors inline (column names, wrong dtype); on success, copy to `source.path`, delete parquet cache, bust bootloader LF cache, increment `data_refresh_trigger`.
2. `app/src/server.py` — `data_refresh_trigger = reactive.Value(0)` added to shared state.
3. `app/handlers/home_theater.py` — `_resolve_t1_lf` subscribes to `data_refresh_trigger`; all plot renders invalidate after import.

**Failure path:** if `MetadataValidator` reports errors, no file is written. The user sees per-file error messages inline. They can re-upload without triggering a plot re-render. Only a successful Apply busts the cache.

**Consequences:**
- Import is always explicit: no silent filename-to-dataset matching.
- `data_refresh_trigger` is the standard mechanism for "tell all plots the source data changed" — any future data-mutation path (not just file import) should increment it rather than calling individual render invalidations.

---

## ADR-059: VizFactory `breaks_integer` Param — Integer Axis Breaks (VIZ-BREAKS-INT, 2026-05-02)

**Status:** IMPLEMENTED

**Context:** Year columns stored as `Int64` (after explicit `cast` in wrangling) were rendering with float axis labels (`2018.0`, `2019.0`) because plotnine's default break algorithm uses float arithmetic. A manifest-level parameter was needed so plot authors could opt in to integer-only axis breaks without editing Python.

**Decision:** Add `breaks_integer: true` as an optional parameter to `scale_x_continuous` / `scale_y_continuous` manifest layer specs.

**Implementation:**

`libs/viz_factory/src/viz_factory/scales/core.py`:
```python
def _integer_breaks(lims):
    return MaxNLocator(integer=True).tick_values(lims[0], lims[1])

def _resolve_continuous_spec(spec):
    spec = dict(spec)
    if spec.pop("breaks_integer", False):
        spec.setdefault("breaks", _integer_breaks)
    return spec
```
Both `scale_x_continuous` and `scale_y_continuous` handlers call `_resolve_continuous_spec(spec)` before building the plotnine scale object.

**Key constraint:** plotnine calls `breaks(limits)` where `limits` is a `(min, max)` tuple. `MaxNLocator` is not a direct callable with that signature — it must be wrapped as `_integer_breaks`.

**Manifest usage:**
```yaml
layers:
  - name: scale_x_continuous
    params:
      breaks_integer: true
```
Note: `breaks_integer` must be nested under `params:` — VizFactory reads `layer_spec.get('params', {})`, not the top-level layer dict.

**Consequences:**
- Plot authors can request integer-only breaks in the manifest; no Python changes required per plot.
- The `breaks_integer` key is consumed and removed from `spec` before passing to plotnine — it does not appear as an unknown kwarg.
- Any other custom break logic should follow the same `_resolve_continuous_spec` extension pattern.

---

## ADR-060: Notification Log Pattern — `make_notifier` + Right Sidebar Alert Accordion (UX-NOTIF-1, 2026-05-02)

**Status:** IMPLEMENTED

**Context:** `ui.notification_show()` toasts disappear after a few seconds. Users were missing failure notifications (e.g. session import errors, export problems, T3 apply blocks). No persistent log existed.

**Decision:**

1. **`app/handlers/notification_utils.py`** — new module, the sole place that wraps `ui.notification_show`. The `make_notifier(notification_log)` factory returns a `_notify(msg, type, duration)` callable that both fires the toast and appends a timestamped entry to a shared `notification_log` reactive.

2. **`notification_log = reactive.Value([])`** declared in `server.py` shared state block, alongside `data_refresh_trigger`. Passed into `home_theater.define_server` and `audit_stack.define_server`, which in turn thread it to all inner handler define calls.

3. **Right sidebar `notification_log_panel_ui`** — a `@render.ui` in `home_theater.py` that renders the log as a collapsed accordion (`🔔 Alerts (N)`) appended to every right sidebar state except the pipeline-persona empty return. Entries shown newest-first, type-colored, 160px scroll.

4. **Scope:** only user-facing handlers get `_notify` (filter_audit, audit_stack, session, export, data_import, sge — 24 call sites). Developer-internal handlers (Blueprint, Wrangle, Gallery clone, DevStudio, ingestion) keep plain `ui.notification_show` since those notifications are tool-level, not user-pipeline-level.

**Consequences:**

- Any new handler that should log notifications: import `make_notifier`, call at top of `define_*`, use `_notify(...)` throughout. No other changes needed.
- `notification_log` is in-memory (cleared on page refresh). T3 ghost persistence is the logical v2 and is deferred.
- If a handler has `notification_log=None` (e.g. called from a test or future context that doesn't pass the log), `_notify` gracefully falls back to plain toasts — no crash.
- The pattern does NOT replace `ui.notification_show` globally — it is opt-in per handler, scoped to user-pipeline operations.

## ADR-061: Gallery Theater Collapsible Panes + recipe_meta Standard Format (2026-05-03)

**Status:** Accepted

**Context:** The Gallery theater used a fixed two-pane vertical layout: a `navset_card_tab` at the top and a yellow "Visual Cookbook: Guidance" pane at the bottom (always fully expanded, `min-height: 400px`). Users wanting to read the full guidance content had no way to temporarily hide the preview tabs, and vice versa. Additionally, the educational markdown content had inconsistent heading hierarchy: `# Recipe Metadata: X` (h1) was visually larger than the "Visual Cookbook: Guidance" accordion header, and taxonomy classification lines (`## Family (Purpose): Ranking`) were styled identically to content section headings (`## Suitability`), making both visually indistinguishable.

**Decision:**

1. **Collapsible panes** — both the Preview tabs (`#gallery_preview_accordion`) and the Guidance pane (`#gallery_guidance_accordion`) are wrapped in separate `ui.accordion()` with `open=True`. Both are open on first load; either can be collapsed independently via the accordion header toggle.

2. **recipe_meta.md standard format** — all gallery recipe markdown files follow a 3-tier structure:
   ```markdown
   ## [Recipe Name]
   
   > 📊 [Family] · 🔢 [Data Pattern] · 📈 [Difficulty]
   
   ### Section Heading
   …
   ```
   - `##` = recipe name (h2, `1.0rem/700`) — same visual weight as the accordion header
   - `> ` blockquote = taxonomy tag strip — compact, left amber border, visually distinct from headings
   - `###` = content sections (h3, `0.85rem/700/uppercase`) — sub-headings, clearly below title

3. **CSS consolidated in §17** — all `.gallery-md-pane` content rules (heading scale, blockquote tag strip, images, tables, body text) live in `config/ui/theme.css` section 17 "Educational Guidance Pane Content". Override per deployment via `@import theme.css` + selector override in a persona-specific CSS file (same pattern as `assets/demo/demo_vetinst.css`).

4. **Layout cleanup** — removed `ui.hr()` between the view-title-banner and split viewer; removed the `height: 10px` structural gap div (replaced by `gap-2` on the flex column parent).

**Consequences:**
- `recipe_template.md` updated to document the standard — new recipes must follow this format.
- All 13 existing `recipe_meta.md` files migrated (2026-05-03).
- CSS §15 "Guidance Header Scaling" removed (consolidated into §17). Any future heading-scale overrides belong in §17.
- `#gallery_guidance_accordion .accordion-item { background: #fff9c4 !important }` must win over `.theater-container-main .accordion-item { background: #ffffff !important }` — it does because an ID selector always beats a class selector.

---

## ADR-062: Sidebar Toggle — Defer to bslib Positioning (2026-05-03)

**Status:** Accepted

**Context:** Phase 26 CSS applied `position: fixed !important` to `.collapse-toggle` (bslib's sidebar expand/collapse button) with explicit `top/left/right` coordinates to pin both toggles to viewport corners. Two bugs resulted:
1. The selector `#main_layout_outer > .bslib-sidebar-layout > .collapse-toggle` never matched — `#main_layout_outer` IS the `bslib-sidebar-layout` element, so the intermediate `.bslib-sidebar-layout` class was a phantom extra step. The left toggle received `position: fixed` but no coordinates — behaviour undefined.
2. More fundamentally: bslib uses `display: grid !important` with a `transition: grid-template-columns` for sidebar collapse animation. During this transition, the grid container becomes a new [fixed-containing-block](https://drafts.csswg.org/css-position/#fixed-cb) for its children in most browsers. A `position: fixed` child of an animating grid is re-anchored to that grid — not the viewport — and ends up at an unpredictable position after the transition completes. When both sidebars are collapsed in sequence, the toggles become unclickable or lost.

**Decision:** Remove all `position`, `top`, `left`, `right` overrides from `.collapse-toggle`. Only apply:
```css
.collapse-toggle {
    transform: scale(0.75) !important;
    z-index: 1100 !important;
}
```
Bslib positions the toggle correctly via its own `position: absolute` + CSS variables that adapt when `.sidebar-collapsed` class is added. Our only concern is visual size (scale) and ensuring it sits above any app content (z-index 1100 > bslib default 1000).

**Consequences:**
- Toggle buttons appear at the border between sidebar and main content (natural bslib position), not pinned to viewport corners. This is the standard bslib UX — accepted trade-off for reliable collapse/expand behaviour.
- Any future attempt to reposition toggles must work WITH bslib's grid-based positioning, not against it (e.g., via CSS variable overrides `--bslib-collapse-toggle-*` if bslib exposes them, or a JS portal approach).

---

## ADR-063: Gallery 6-Axis Taxonomy (2026-05-03)

**Status:** Accepted

**Context:** The original gallery taxonomy had 3 axes (family/pattern/difficulty), which were too coarse for users to find the right chart type efficiently. A user wanting a "geom_violin" specifically, or a chart that shows "ranking", had to browse recipe names rather than filter. The sidebar had 3 filter panels; adding 3 more required coordinated changes across the manifest format, pivot index, sidebar UI, and filter logic.

**Decision:** Add 3 new taxonomy axes to every gallery recipe manifest `info:` block:

| Field | CSS icon | Meaning |
|---|---|---|
| `geom` | ⚙️ | Primary plotnine geom/stat function name (exact lowercase, e.g. `geom_violin`) |
| `show` | 🎯 | What the chart communicates (`distribution`, `ranking`, `trend`, `relationship`, `change`, `proportion`, `frequency`, `normality`, `uncertainty`) |
| `sample_size` | 📏 | Recommended data volume (`any`, `individual points`, `medium+`, `large`) |

All 34 existing recipe manifests and `recipe_meta.md` tag strips were updated. The blockquote tag strip is now 6 fields:
```
> 📊 Family · 🔢 Data Pattern · 📈 Difficulty · ⚙️ geom_name · 🎯 show_value · 📏 sample_size_value
```

**Implementation:**
- `gallery_manager.py` — `submit_recipe()` accepts 3 new optional params; `rebuild_index()` adds `by_geom`, `by_show`, `by_sample_size` to the pivot dict
- `gallery_viewer.py` — `build_sidebar_ui()` adds 3 new `_filter_panel()` calls; all 6 taxonomy sub-panels default to `open=False` (collapsed) so the sidebar isn't overwhelming
- `gallery_handlers.py` — 3 new "Select all" sync effects; `_update_gallery_options()` refactored with `_pivot_set(axis, selections)` helper:
  - `_pivot_set` returns the full recipe set when selections is empty (no filter), or the union of matching IDs when selections is non-empty
  - `valid_ids` = 6-way intersection of all axis results
  - Empty = no filter (not "filter everything") — critical for single-axis browsing
- `assets/gallery_data/TAXONOMY_CHEATSHEET.md` — single-file canonical reference for all icon/axis/value mappings

**Consequences:**
- New recipes must populate all 6 fields in `info:` — `rules_gallery_standards.md` updated.
- `gallery_index.json` must be regenerated via `refresh_gallery.py` after any manifest change.
- Allowed values for `geom` are the exact plotnine function names (checked against `TAXONOMY_CHEATSHEET.md`). Values for `show` and `sample_size` are strict enums.

---

## ADR-064: Accordion-First UI Harmonization — §18/18b CSS Pattern (2026-05-03)

**Status:** Accepted

**Context:** Three content panels used inconsistent collapse/expand mechanisms: the Home Main Plot Card and Blueprint Work Area used `data-bs-toggle="collapse"` (Bootstrap's native collapse widget), which renders a visually separate grey strip that looks disconnected from the content below. The Gallery theater (ADR-061) used bslib `ui.accordion()` which renders as a unified card — header + content share one rounded container. The Data Preview accordion title used an inline `style` attribute forcing grey/light font that overrode the CSS bold/dark policy.

Additionally, CSS `border-radius: 0 0 7px 7px` was applied to inner navset-cards to round only the bottom corners, making accordions appear rounded at the bottom but flat at the top — visually inverted from expected card aesthetics.

**Decision:**

1. **`_collapsible_panel()` helper** (in `home_theater.py`) — wraps any content in `ui.accordion(ui.accordion_panel(title, content, value=...), id=..., open=panel_value)`. Single pattern for all collapsible content panels in Home Theater. Matches Gallery §14 style exactly.

2. **Blueprint Work Area** — changed from Bootstrap collapse to `ui.accordion()` with id `blueprint_workarea_accordion`. Bootstrap Glimpse + Plot Preview cards kept as collapse widgets (two small live-view panels at the bottom), but styled to match accordion aesthetics: `font-weight: 700`, `background: #f8f9fa`, `padding: 2px 10px`, `border: none`.

3. **CSS §18 (global)** — applied to ALL `.theater-container-main` and `.wrangle-studio-container` accordion buttons:
   - Bold 0.85rem dark text
   - `#f8f9fa` collapsed / `#ffffff` expanded background
   - `box-shadow: none` on expanded (removes Bootstrap's inset separator line)
   - `border: none` on accordion-items

4. **CSS §18b (per-ID)** — for `#home_plots_body_accordion`, `#acc_home_data`, `#blueprint_workarea_accordion`:
   - `.accordion-item { border-radius: 8px !important; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08) }` — outer clip fixes top-corner rounding; shadow provides card depth
   - Inner navset-card/pill: `border-radius: 0 !important` — let the accordion-item's `overflow: hidden` handle all corner clipping

5. **Bootstrap collapse cards** (`.wrangle-studio-container > .card`):
   - `border: none; border-radius: 8px; overflow: hidden; box-shadow`
   - `.card-header { border-radius: 8px 8px 0 0; border-bottom: none; padding: 0 }`

6. **Gallery fixes** — `#gallery_preview_accordion .accordion-item { border: none; box-shadow; border-radius: 8px; overflow: hidden }` eliminates Bootstrap's default `1px solid rgba(0,0,0,.125)` that was rendering as a grey bar. `#gallery_guidance_accordion .accordion-item { box-shadow: none }` prevents default shadow from bleeding between stacked accordions.

**Conventions for future agents:**
- Any new collapsible panel in `theater-container-main` MUST use `_collapsible_panel()` or an equivalent `ui.accordion()` wrapper — never `data-bs-toggle="collapse"`.
- All accordion-items in central theater areas need `overflow: hidden` to clip corners correctly.
- Never apply `border-radius: 0 0 7px 7px` on inner navset-cards when the accordion-item already has `border-radius + overflow: hidden`.
- Inline `style=` on panel titles overrides CSS policy — use plain strings or CSS-class spans only.

**Consequences:**
- Bootstrap collapse widgets in Blueprint (Glimpse/Plot Preview) are kept but look like mini-accordion headers — consistent visual language.
- The pattern is now: `ui.accordion()` = primary panel collapsible container; Bootstrap `card` = secondary small live-view widget inside a panel.

---

## ADR-065: CSS Colour Token Consolidation — `#345beb` as Sole Primary Blue (2026-05-03)

**Status:** IMPLEMENTED

**Context:** After ADR-055 (externalised stylesheet) and ADR-064 (accordion normalisation), several CSS rules still carried Bootstrap's default `#0d6efd` or dark-text `#1a1a1a` values on interactive element labels. TubeMap accordion text was deliberately reset to `#1a1a1a` in ADR-064 as part of normalisation, which was correct for neutral headers but wrong for labelled sections that should align with the primary accent. Additionally, ADR-064 Python changes (Home plot-collapse card, Blueprint Plot Preview card) introduced visual regressions caught on demo-day — `home_theater.py` and `wrangle_studio.py` were restored to pre-ADR-064 state via `git checkout bdf8723`, while the ADR-064 CSS rules (§18/18b) were kept.

**Decision:**

1. **`#345beb` is the sole primary blue accent.** Bootstrap default `#0d6efd` MUST NOT appear in `theme.css` or Python inline styles. It is overridden globally on `.btn-primary` (§6). Any new CSS rule introducing an accent colour MUST use `#345beb`.

2. **Full colour pass (§3/§5/§6/§9/§12/§14/§16/§17/§18):** All interactive label text (nav pill links, tab links, accordion headers, card-header titles, sidebar tier h6 dividers, Bootstrap collapse card button text) now uses `#345beb`.

3. **Three-token colour vocabulary for action buttons:**
   - Primary / analytical: `#345beb` (`.btn-primary`, `#btn_apply`)
   - Export / ingest: `#10a395` (teal) — `#btn_export`, `#filter_add_row`, upload buttons
   - Destructive / pending: `#ffc107` (amber) — `#filter_reset`, `.recipe-pending-badge`, `[id^="session_delete_"]`

4. **Right sidebar card full rounding:** `#audit_sidebar .card { border-radius: 8px }` — previously `8px 8px 0 0`. All four views share this rule; bottom corners are now rounded for visual homogeneity.

5. **CSS hard constraints documented** in `docs/reference/ui_style_guide.qmd`:
   - `#acc_home_data .accordion-body` must keep `overflow: visible` — selectize dropdowns clip otherwise.
   - `#gallery_guidance_accordion .accordion-item` intentionally has `overflow: hidden` — no dropdowns inside; needed for corner clipping.
   - `background-color` clips to its own `border-radius` without `overflow: hidden` on parent — apply `border-radius` on the element whose background you want clipped, not its ancestor.
   - Blueprint Live Data Glimpse `<button>` background (`#e9ecef`) is Python inline — CSS must not win this with `!important` (would desync Bootstrap toggle visual state).
   - Shiny's Bootstrap build does NOT use `--bs-form-check-input-checked-bg-color` — checked state must target `.shiny-input-container .radio input:checked`, and even that may lose to Shiny's internal specificity.

6. **Python revert scope:** ADR-064 Python changes to `home_theater.py` (Home plot collapsible card via `_collapsible_panel()`) and `wrangle_studio.py` (Blueprint Plot Preview Bootstrap card) were reverted to `bdf8723`. ADR-064 CSS (§18/18b) is unchanged and valid against the reverted Python.

**Conventions for future agents:**
- Never introduce `#0d6efd`, `#007bc2`, or `#1a1a1a` on accent-role text. Check `theme.css` for the `#345beb` pattern before adding any new colour value.
- When adding a new CSS rule for a Shiny toggle/checkbox checked state, use the `.shiny-input-container .radio input:checked` selector and document in §3 that it may not win against Shiny internals.
- The Blueprint Glimpse header background is pinned in Python — do not fight it with `!important`.
- Refer to `docs/reference/ui_style_guide.qmd` for the full per-element selector/modifiability table before changing any panel's visual style.

**Consequences:**
- Visual language is now consistent: `#345beb` blue = all semantic labels across all 4 views.
- Developer documentation exists: `docs/reference/ui_style_guide.qmd` is the single reference for "what selector do I need and can I safely change it?"
- ADR-064 Python changes deferred — the collapsible Home plot card is `THEATER-1` in the open backlog.

---

## ADR-066: Rename `assembly_manifests` → `join_manifests` (2026-05-04)

**Status:** IMPLEMENTED (2026-05-04)

**Context:** The term "assembly" has a precise and well-known meaning in bioinformatics (genome/contig assembly from sequencing reads). Using it for the dataset-joining section of manifests creates confusion, particularly in the Cytoscape TubeMap which is visible to the whole team.

**Decision:** Rename all occurrences of the `assembly` concept (where it refers to joining datasets) to `join`.

| Old | New |
|-----|-----|
| YAML key `assembly_manifests:` | `join_manifests:` |
| Python dict key `"assembly_manifests"` | `"join_manifests"` |
| Role string `"assembly"` | `"join"` |
| TubeMap node label `…\nAssembly` | `…\nJoin` |
| TubeMap node label `…\nAssembly Wrangling` | `…\nJoin Wrangling` |
| UI label `◆ Assembly` | `◆ Join` |
| UI label `Assembly Output (Input)` | `Join Output (Input)` |
| Variable `assemblies` | `join_defs` |
| Variable `asm_block` | `join_block` |
| Variable `is_assembly` | `is_join_step` |
| Variable `assembly_rels` | `join_rels` |

**Exception — not renamed:**
- `session_manager.py` and `debug_session_flow.py`: `{"assembly": ..., "contracted": ...}` — these are Parquet file path labels internal to the session ghost save mechanism, unrelated to the manifest role.

**Variable name rule:** Never use bare `join` as a Python variable name — it shadows `str.join()` and is confusing adjacent to Polars. Use `join_defs`, `join_block`, `join_step`, `is_join_step`.

**Scope:** ~35 files, ~65 occurrences. Config manifests, test fixtures, app/, libs/, docs. EVE_WORK/ historical daily logs left unchanged.

**Consequences:** Existing session ghost saves referencing `assembly_manifests` in serialised state will fail to find `join_manifests` on restore. Any manifests not in this repo still using the old key will fail to load. See `changelog.md` for full record.

---

## ADR-067: Extract `libs/blueprint_arch/` — Blueprint Architect Pure-Python Logic (2026-05-05)

**Status:** IMPLEMENTED (2026-05-05)

**Context:** `blueprint_mapper.py` lived in `libs/utils/` — a general-purpose headless lib — alongside config loading, hashing, and error utilities. `manifest_navigator.py` lived in `app/modules/`, violating the Two-Category Law (ADR-045) even though it has zero Shiny dependency and was already declared headless-safe. Both files exist solely to serve the Blueprint Architect feature.

**Decision:** Create `libs/blueprint_arch/` as a dedicated editable lib for all Blueprint Architect pure-Python logic.

**Moved:**
- `libs/utils/src/utils/blueprint_mapper.py` → `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py`
- `app/modules/manifest_navigator.py` → `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py`
- `libs/utils/tests/debug_blueprint_mapper.py` → `libs/blueprint_arch/tests/debug_blueprint_mapper.py`

**Import changes:** `blueprint_handlers.py` updated from `utils.blueprint_mapper` and `app.modules.manifest_navigator` to `blueprint_arch.*`.

**Rationale:** Gives the Blueprint Architect module a clean, growable home. Removes a headless-only module from `app/modules/` (ADR-045 compliance). Keeps `libs/utils/` focused on cross-cutting helpers (config, hashing, errors).

**Consequence:** `libs/blueprint_arch` must be installed as an editable package (`.venv/bin/pip install -e libs/blueprint_arch/`). Confirmed working.

---

## ADR-068: Extract `libs/test_lab/` + Absorb `generator_utils` + Rename `dev_studio` (2026-05-05)

**Status:** IMPLEMENTED (2026-05-05)

**Context:** `libs/generator_utils/` contained four modules (`aqua_synthesizer`, `bootstrapper`, `extractor`, `reconciler`) for synthetic data generation, manifest bootstrapping, XLSX extraction, and key reconciliation. `app/modules/dev_studio.py` (class `DevStudio`) was the Shiny UI for this functionality — its banner already displayed "Test Lab". The old package name `generator_utils` was undersized (it covers extraction and reconciliation, not just generation) and the name `dev_studio` / `DevStudio` referred to a superseded design concept.

**Decision (Option B — absorb):** Create `libs/test_lab/` and move all four `generator_utils` source modules into it. Do NOT keep `generator_utils` as a separate dependency.

**Moved:**
- `libs/generator_utils/src/generator_utils/{aqua_synthesizer,bootstrapper,extractor,reconciler}.py` → `libs/test_lab/src/test_lab/`
- `libs/generator_utils/tests/*` → `libs/test_lab/tests/` (with imports updated `generator_utils.*` → `test_lab.*`)
- `generator_utils` uninstalled from venv; directory removed.

**Renamed:**
- `app/modules/dev_studio.py` → `app/modules/test_lab_studio.py`
- Class `DevStudio` → `TestLabStudio`
- All consumers (`server.py`, `home_theater.py`) updated. The local variable name `dev_studio` is kept as a parameter-name convention.

**Import changes:** `assets/scripts/generate_demo_data.py` updated from `generator_utils.aqua_synthesizer` to `test_lab.aqua_synthesizer`.

**Rationale:** Unified lib allows Test Lab functionality to grow (future: inject T3 node types, run headless schema validation, drive the reconciler from the UI). Simpler dependency graph — one package instead of two.

**Consequence:** `libs/test_lab` must be installed as an editable package (`.venv/bin/pip install -e libs/test_lab/`). Confirmed working.

---

## ADR-070: Functionality-First Deployment Model — Personas are Named Bundles, Not the Primary Concept (2026-05-05)

**Status:** DECIDED (2026-05-05)

**Context:** The project historically described deployment configuration in terms of "personas" — named profiles such as `pipeline-static`, `developer`, etc. This framing caused recurring confusion: agents and developers would reason about what a persona "should have" rather than about what user functionality was needed and what its dependencies were. This led to inconsistent flag assignments, undocumented cascade rules, and difficulty explaining the system to potential deployers.

**The confusion it caused:**
- Flags were added to personas without reasoning about user-functionality dependencies
- Cascade rules (e.g. T3 requires export) existed in code but were not formally documented
- New personas were designed by copying existing ones rather than composing functionalities
- Documentation mixed "what persona X does" with "what the system can do" — making it hard to understand what was configurable vs locked

**Decision: Functionality-first framing**

The primary concept is the **user functionality** — a coherent capability the end user perceives (e.g. "I can filter data", "I can export results"). A **persona** is simply a named, reusable bundle of user functionalities. It is a convenience label, not the architectural primitive.

**Consequences for documentation and design:**
- All design documents lead with user functionalities and their dependency rules
- Personas are documented as "example deployment configurations" — starting points for deployers
- New personas are created by composing functionalities within the cascade rules, not by copying another persona
- Cascade rules are formally validated at startup (`PersonaConfigError`) — not implicit conventions

**Canonical references:**
- `.claude/design/functionality_dependency_map.md` — authoritative user→code flag mapping
- `.claude/design/persona_scoping_guide.md` — flag reference, retitled "Deployment Configuration Guide"
- `.claude/design/persona_capability_matrix.md` — retitled "Deployment Configuration Matrix"
- `docs/user_guide/deployment_personas.qmd` — user/deployer-facing explanation

**Rule going forward:** When adding a new flag or modifying a persona, always start from the user functionality question: *"What does the user need to be able to do, and what does that require?"* Never add flags to a persona template without first verifying the dependency map.

---

## ADR-071: Deployment Hardening Standard — Air-Gap Safety and Positive Inclusion (2026-05-05)

**Status:** DECIDED + PARTIALLY IMPLEMENTED (DEPLOY-CDN-1 done; DEPLOY-MODULES-1 + DEPLOY-LIBS-1 pending)

**Context:** SPARMVET is intended for deployment in institutional environments (e.g. Posit Connect, Galaxy, IRIDA, internal servers) that may have restricted or no outbound internet access. Additionally, the first real deployment must ensure that disabled modules are genuinely inaccessible — not merely hidden in the UI while still initialised server-side.

Two principles from `EVE_WORK/notes/deployment/considerations.md` are elevated here to binding ADR rules:

1. **Air-gap safety**: the app must function identically with no outbound network access.
2. **Positive inclusion**: only modules explicitly enabled by configuration are registered, initialised, and reachable. "Not intended to be used" is not the same as "impossible to access."

---

### Rule 1: No external network dependencies — ever

All JavaScript and CSS assets loaded by the UI **must** be vendored locally. CDN links (`cdn.jsdelivr.net`, `unpkg.com`, or any external URL) are **forbidden** in `ui.py` or any other file in this repository.

**Vendored assets live in `app/src/www/vendor/`**, served via Shiny's `static_assets` parameter in `main.py`. Referenced in `ui.py` as `/vendor/<filename>`.

**When adding a new frontend dependency:**
1. Download the asset at a specific pinned version (never `@latest`)
2. Place it in `app/src/www/vendor/` (CSS font files in `vendor/fonts/`)
3. Update `app/src/www/vendor/VENDOR_MANIFEST.md` with name, version, source URL, and licence
4. Reference it via `/vendor/<filename>` in `ui.py`
5. Never add a CDN fallback

**Current vendor manifest** (as of 2026-05-05):

| Asset | Version | Source | Licence |
|---|---|---|---|
| `cytoscape.min.js` | 3.29.2 | jsdelivr/cytoscape | MIT |
| `dagre.min.js` | 0.8.5 | jsdelivr/dagre | MIT |
| `cytoscape-dagre.js` | 2.5.0 | jsdelivr/cytoscape-dagre | MIT |
| `bootstrap-icons.css` + `fonts/` | 1.11.1 | jsdelivr/bootstrap-icons | MIT |

---

### Rule 2: Positive inclusion for server-side modules

`server.py` **must not** unconditionally instantiate or register modules. Every module instantiation and every `define_server()` call must be gated on the relevant persona flag from `bootloader`.

**The principle:** if a persona does not have a capability enabled, that module's server logic is never initialised, never registered as a reactive endpoint, and never reachable via any UI path, query parameter, or reactive chain.

**Forbidden pattern:**
```python
# BAD — loads Blueprint server logic for all personas, including pipeline-static
define_blueprint_server(...)
```

**Required pattern:**
```python
# GOOD — Blueprint server only initialised when explicitly enabled
if bootloader.is_enabled("blueprint_enabled"):
    define_blueprint_server(...)
```

**Applies to:**
- `WrangleStudio` / `TestLabStudio` instantiation
- `define_blueprint_server()` / `define_gallery_server()` / `define_ingestion_server()`
- Any handler, reactive output, or module that belongs to an optional capability

**Rationale:** "Not intended to be used" ≠ "impossible to access." Inactive modules still consume startup time, may expose reactive endpoints, and create maintenance burden in production. Positive inclusion is the only safe default.

---

### Rule 3: Clean deployment path for internal libraries

All `libs/` packages must be installable via a single command. A deployment without running this command must fail immediately with a clear import error — not silently at runtime.

**Implementation:** `scripts/install_libs.sh` (or equivalent) installs all editable packages in dependency order. This script is the single source of truth for which libs exist and their install order.

**In production environments (non-editable):** build wheel packages from each lib and declare them in the deployment bundle. Editable installs (`pip install -e`) are for development only.

---

### Rule 4: Vendor manifest must be kept current

`app/src/www/vendor/VENDOR_MANIFEST.md` records every vendored asset: name, version, source URL, and licence. This file must be updated whenever a vendor asset is added, upgraded, or removed. It serves as the audit trail for frontend dependencies.

---

### Rule 5: No cross-panel output references

A UI element that references an output (`ui.output_*`, `ui.output_plot`, `ui.output_text`, etc.) from module X **must** live inside module X's gated panel — or be explicitly gated by the same persona flag as module X.

**Forbidden pattern:**
```python
# BAD — Home panel references a Blueprint output; breaks when blueprint_enabled: false
ui.output_text("blueprint_lineage_summary")   # inside home panel
```

**Required pattern:**
```python
# GOOD — Blueprint outputs only referenced inside Blueprint's gated nav panel
# OR gated explicitly:
if bootloader.is_enabled("blueprint_enabled"):
    ui.output_text("blueprint_lineage_summary")
```

**Rationale:** If module X is disabled (not registered server-side), any UI element referencing its outputs will produce a dangling Shiny reference — a permanently-loading spinner or silent error. The only safe contract is: output references and their server registrations are gated by the same flag.

**Corollary — workarounds for cross-module UX:** If a feature genuinely needs to surface information from module X inside another panel (e.g. a "View in Blueprint" button in Home), the correct implementation is a shared reactive value or event bus owned by the core app, not a direct output reference. The button itself must also be gated on `blueprint_enabled`.

---

### Consequences

- Any PR that adds a CDN URL to `ui.py` or any other file violates this ADR and must be rejected.
- Any PR that adds an unconditional `define_<module>_server()` call in `server.py` violates Rule 2.
- Deployment to a new environment requires running `scripts/install_libs.sh` — no manual lib-by-lib installation.
- All future JS/CSS dependencies are vendored at a pinned version before any code referencing them is merged.

**Implementation tasks:**
- [x] **DEPLOY-CDN-1**: Vendor all 4 current CDN assets. `main.py` + `ui.py` updated. ✅ 2026-05-05
- [ ] **DEPLOY-MODULES-1**: Gate all `server.py` module instantiation + handler registration on persona flags
- [ ] **DEPLOY-LIBS-1**: Create `scripts/install_libs.sh`; document in README
- [ ] **VENDOR-MANIFEST-1**: Create `app/src/www/vendor/VENDOR_MANIFEST.md`

---

## ADR-069: Complete Export Audit Trail Standard (2026-05-05)

**Status:** DECIDED — implementation pending

**Context:** Export surfaces (bundle README, report.qmd, image files) currently include only a subset of provenance information. For scientific traceability, reproducibility, and regulatory/institutional compliance, every export must carry a complete, machine-readable and human-readable audit trail. This is a non-negotiable design requirement of the project.

**Decision — three binding rules:**

### Rule 1: All provenance fields are always present — no flag, no opt-out

Every export surface must include the full provenance set below. There is no persona flag, configuration option, or UI toggle that disables this. If an export is generated, the audit trail is generated with it.

### Rule 2: Complete provenance set (mandatory in every export)

| Field | Description | Source |
|---|---|---|
| `data_batch_hash` | SHA256 of raw source files | `home_state["data_batch_hash"]` |
| `manifest_sha256` | SHA256 of the loaded manifest YAML | `home_state["manifest_sha256"]` |
| `decision_hash` | SHA256 of the wrangling recipe (all T1/T2 transforms) | Read from Parquet metadata key `sparmvet_decision_hash` at export time |
| `git_commit` | Short git commit hash at runtime | `git rev-parse --short HEAD` |
| `release_version` | Release tag + offset if ahead of tag | `git describe --tags --always` |
| `created_at` | ISO 8601 UTC timestamp of export creation | `datetime.utcnow().isoformat() + "Z"` |
| `manifest_name` | Human-readable manifest name/path | From loaded manifest `info.name` or path |
| `persona_id` | Active persona ID at export time | `current_persona.id` |
| `active_tier` | Data tier displayed at export (T1 / T2 / T3) | From `home_state` |
| `software_versions` | Python, plotnine, polars, SPARMVET versions | `sys.version`, package metadata |
| `data_source_paths` | Relative paths of all raw source files loaded | From `bootloader` manifest resolution |
| `t3_recipe` | T3 audit steps (only when T3 active and has committed nodes) | From `t3_steps.yaml` content; omitted if T3 not active |
| `plot_id` + `group_id` | Plot and group identifiers | For single-graph exports; omitted in global bundle |

**Note on passive filter state:** Passive filters (applied by passive/non-T3 personas) are ephemeral and are NOT included in the audit trail. Only the T3 recipe captures modification state, because only T3 modifications are permanent and reproducible.

### Rule 3: Image and binary file metadata embedding

Any exported file that does not already contain the provenance information as visible text MUST have it embedded as file-level metadata. This ensures provenance survives file extraction from a bundle.

| Format | Mechanism | Namespace prefix |
|---|---|---|
| PNG | `PngImagePlugin.PngInfo` iTXt chunks (Pillow) | `sparmvet:` |
| SVG | `<metadata>` XML block inside `<svg>` | `sparmvet:` |
| PDF | XMP metadata block | `sparmvet:` |

Minimum fields in image metadata: `data_batch_hash`, `manifest_sha256`, `decision_hash`, `git_commit`, `release_version`, `created_at`, `plot_id`, `persona_id`.

### Export surfaces and their required content

| Surface | Full provenance set | Image metadata |
|---|---|---|
| Bundle README | ✅ All fields | N/A |
| `report.qmd` / rendered HTML | ✅ All fields | N/A |
| PNG plot images | Subset (8 fields above) | ✅ Embedded |
| SVG plot images | Subset (8 fields above) | ✅ Embedded |
| PDF exports | Subset (8 fields above) | ✅ Embedded |
| `t3_steps.yaml` | T3 recipe fields only | N/A |

**Implementation tasks:**
- **EXPORT-HASH-2**: Read `decision_hash` from Parquet metadata at export time (existing task)
- **EXPORT-VERSION-1**: Add `git_commit` + `release_version` to all export surfaces
- **EXPORT-IMG-META-1**: Embed 8-field provenance subset in PNG/SVG/PDF file metadata (Pillow iTXt + SVG `<metadata>` + XMP)
- **EXPORT-AUDIT-COMPLETE-1**: Add all remaining missing fields (`created_at`, `manifest_name`, `persona_id`, `active_tier`, `software_versions`, `data_source_paths`) to bundle README and report.qmd

**Consequence:** Exports are slightly larger (metadata overhead is negligible). The `get_parquet_metadata_hash()` utility must be called at export time for each materialized Parquet file. A helper function `build_export_provenance()` should be introduced in `export_handlers.py` to assemble the full provenance dict once and pass it to all export surfaces, avoiding duplication.

**Amendment (2026-05-09):** The bundle must include a per-source-file hash table (individual SHA256 for every raw data file loaded, not just the rolled-up `data_batch_hash`). Both must appear in README.txt and report.qmd so a reviewer can verify each input file independently, not just the aggregate. The `source_files` dict from the assembly ghost (keyed by dataset ID, value `{path, sha256}`) is the authoritative source.

---

## ADR-073: Configurable Sidebar Slot Registry (2026-05-09)

**Status:** DECIDED — implementation pending

**Context:**

The current left and right sidebars are hardcoded accordion panels in `home_theater.py` and `ui.py`, each individually gated by a feature flag. This works for a fixed set of panels but has three limitations:

1. **No per-workspace configuration** — Home, Blueprint, Gallery, and Test Lab each need different sidebar content, but there is no declarative way to express this in a persona template.
2. **No panel reordering or custom panels** — adding a new panel type (e.g. `project_info`, `deployment_info`) requires editing Python.
3. **Right sidebar structural exclusion is done by persona name comparison** — a known ADR-053 violation (tasks.md task 25-O).

The right sidebar currently contains only the T3 audit stack and is excluded from layout for `pipeline-static` and `pipeline-exploration-simple` by reading the persona name string in `ui.py` — which is prohibited by ADR-053. The left sidebar has no visibility control at all; it always renders even when nearly empty (e.g. only Export for static personas).

**Decision:**

### Rule 1 — Two-layer resolution (slot list + flag gate)

Sidebar configuration uses two independent axes:

| Axis | Controls | Defined in |
|---|---|---|
| **Slot list** | Which panel types appear, in what order | Persona template `workspaces.<ws>.left_sidebar.panels` |
| **Feature flag** | Whether the panel's functionality is active | Existing flag system (`bootloader.is_enabled(flag)`) — unchanged |

A panel in the slot list with a disabled gate flag is silently skipped. A panel type not in the slot list but with an enabled flag is not shown. **Flag capability is independent of slot presence.** Cascade rules (ADR-052, PersonaValidator) operate on flags only and are completely unaffected.

### Rule 2 — Per-workspace configuration

The persona template declares sidebar config separately for each user workspace. Workspaces are independent; changing the Home sidebar does not affect the Blueprint sidebar.

```yaml
workspaces:
  home:
    left_sidebar:
      visible: true
      panels:
        - type: project_info
        - type: filters
        - type: export
        - type: session_management
    right_sidebar:
      visible: true
      panels:
        - type: audit_stack
  blueprint:
    left_sidebar:
      visible: true
      panels:
        - type: project_info
        - type: blueprint_nav
    right_sidebar:
      visible: true
      panels:
        - type: blueprint_logic
  gallery:
    left_sidebar:
      visible: true
      panels:
        - type: gallery_search
    right_sidebar:
      visible: false
      panels: []
  test_lab:
    left_sidebar:
      visible: true
      panels:
        - type: project_info
    right_sidebar:
      visible: false
      panels: []
```

### Rule 3 — !include for shared sidebar configs

Sidebar panel lists live in `config/ui/sidebars/` as reusable YAML fragments and are referenced via `!include`. Multiple personas sharing the same sidebar layout use the same file — a change propagates to all.

```
config/ui/sidebars/
  home_static_left.yaml
  home_simple_left.yaml
  home_advanced_left.yaml          ← shared by advanced, independent, developer, qa
  home_advanced_right.yaml         ← shared by all T3-capable personas
  blueprint_standard_left.yaml
  blueprint_standard_right.yaml
  gallery_focus_left.yaml
  testlab_standard_left.yaml
```

Example persona template fragment:

```yaml
workspaces:
  home:
    left_sidebar: !include sidebars/home_advanced_left.yaml
    right_sidebar: !include sidebars/home_advanced_right.yaml
  blueprint:
    left_sidebar: !include sidebars/blueprint_standard_left.yaml
    right_sidebar: !include sidebars/blueprint_standard_right.yaml
```

### Rule 4 — Panel registry

A `PANEL_REGISTRY` dict in `app/modules/sidebar_registry.py` maps panel type names to their renderer function and gate flag. This module is headless-safe (no Shiny imports — Two-Category Law compliant). Shiny rendering is done in the caller (handler), not in the registry.

| Panel type | Gate flag | Workspace(s) | Notes |
|---|---|---|---|
| `project_info` | — | all | Always renders; shows manifest title, description, dataset summary |
| `deployment_info` | — | all | Optional branding; params: `logo`, `contact`, `institution` |
| `filters` | `interactivity_enabled` | home | Row filter recipe builder |
| `export` | `export_enabled` | home | Export bundle panel |
| `session_management` | `session_management_enabled` | home | Session save/restore/import |
| `data_import` | `metadata_ingestion_enabled` | home | Metadata upload + optional multi-file ingestion |
| `manifest_choice` | `manifest_selector.visible` | home | Manifest selector dropdown |
| `audit_stack` | `t3_sandbox_enabled` | home | T3 audit trail — right sidebar |
| `blueprint_nav` | `blueprint_enabled` | blueprint | Dataset pipeline selector, TubeMap node selector |
| `blueprint_logic` | `blueprint_enabled` | blueprint | Active component logic stack — right sidebar |
| `gallery_search` | `gallery_enabled` | gallery | Focus mode: search + filter controls |
| `notification_log` | — | any | Alert accordion (ADR-060) — right sidebar slot |

New panel types are registered by adding an entry to `PANEL_REGISTRY` — no sidebar wiring changes needed.

### Rule 5 — Sidebar visibility and structural exclusion

`left_sidebar.visible: false` hides the sidebar entirely (DOM excluded, not CSS hidden). This replaces the current implicit "nearly empty sidebar for static personas" with an explicit choice.

`right_sidebar.visible: false` excludes the right sidebar from layout at build time. This replaces the persona name string comparison in `ui.py` (the known ADR-053 violation, task 25-O) with `bootloader.get_sidebar_config("home", "right").visible`.

**Auto-hide rule:** If `visible` is not explicitly set and all panels in the list are skipped (all gate flags off), the sidebar is treated as `visible: false` and excluded from layout.

**`visible: true` with no active panels** produces an empty sidebar container — allowed when deployment info or project info is the sole content.

### Rule 6 — Compatibility validation (`SidebarValidator` + CLI script)

A `SidebarValidator` class (alongside existing `PersonaValidator`) checks sidebar configs at startup and in CI. A CLI script `scripts/validate_persona_config.py` wraps both validators:

```bash
# Validate one persona
.venv/bin/python scripts/validate_persona_config.py --persona pipeline-exploration-advanced

# Validate all personas (CI gate)
.venv/bin/python scripts/validate_persona_config.py --all --strict
```

Checks performed:

| Check | Severity | Action |
|---|---|---|
| Panel type not in registry | ERROR | Blocks startup and script |
| `!include` target file missing or unparseable | ERROR | Blocks startup and script |
| Panel in slot list but gate flag disabled | WARNING | Logged; panel silently skipped at runtime |
| Workspace listed but workspace flag disabled | WARNING | Logged; sidebar rendered but panels skipped |
| Cascade violations (existing PersonaValidator rules) | ERROR | Unchanged behaviour |
| `right_sidebar.visible: true` but `t3_sandbox_enabled: false` (audit_stack only panel) | WARNING | Right sidebar will be empty at runtime |

`--strict` mode upgrades warnings to errors (recommended for CI).

**Interactive conflict resolution:** When run interactively (not `--strict`), the script prompts for a choice when a panel/flag combination is ambiguous. Choices are recorded and can be applied as template patches.

### Rule 7 — Default templates preserve current behaviour exactly

All 6 existing persona templates receive `workspaces:` sections whose default slot lists reproduce current sidebar behaviour. No breaking change. The upgrade is additive.

### Consequences

- `ui.py` no longer reads persona name to decide right sidebar exclusion — reads `bootloader.get_sidebar_config(ws, "right").visible` (fixes task 25-O).
- `home_theater.py` iterates the panel slot list for the active workspace rather than rendering a hardcoded accordion sequence.
- Adding a new panel type in future: register in `PANEL_REGISTRY`, add to relevant sidebar YAML files, done — no Python sidebar wiring changes.
- Custom deployments can override a single `!include` target (e.g. replace `home_advanced_left.yaml`) without touching the persona template or any Python.
- `scripts/validate_persona_config.py` is the mandatory pre-deployment gate for any persona template change.

**Implementation tasks:**
- **SIDEBAR-CONFIGS-1** `[haiku/low]`: Create `config/ui/sidebars/` directory with shared sidebar YAML files for all workspace × tier combinations
- **SIDEBAR-REGISTRY-1** `[sonnet/high]`: Implement `app/modules/sidebar_registry.py` (panel registry), update `bootloader` to read `workspaces:` config, update `home_theater.py` to iterate slot list, fix `ui.py` right sidebar exclusion (replaces persona name check — task 25-O)
- **SIDEBAR-VALIDATE-1** `[sonnet/medium]`: Implement `SidebarValidator` + `scripts/validate_persona_config.py` CLI with `--all --strict` mode

---

## ADR-074: Lineage Infrastructure as Shared Provision (2026-05-09)

**Status:** DECIDED — implementation pending

**Context:** Two user spaces require manifest lineage tracing from different angles:

- **HOME export** needs per-plot and per-group provenance: for a given plot, which T1/T2 wrangling steps, which join/assembly recipe, and which plot spec contributed to its output — plus any T3 modifications layered on top. For group-scope exports, all plots in the group must first be discovered (forward), then each traced backward.
- **BLUEPRINT IDE** needs the same backward trace for visualization and navigation: when a user selects a node, the IDE shows the contributing upstream chain.

Both needs are served by two new functions in `manifest_navigator.py`. That module already lives in `libs/blueprint_arch/` (Phase 29, ADR-067) as formally shared infrastructure — importable by both HOME's export handler and BLUEPRINT's IDE handler without violating the Two-Category Law.

**Key principle:** *HOME users produce science from a pipeline; BLUEPRINT users produce and document pipelines.* This distinction drives the export format: lineage is a documentation/transparency artifact for HOME users, not a publication artifact — it belongs in the report. SVG export of the manifest DAG for pipeline documentation is a BLUEPRINT-scoped feature for pipeline authors, addressed separately in ADR-075.

---

### 1. Two new functions in `libs/blueprint_arch/.../manifest_navigator.py`

**`build_plot_lineage(plot_id, manifest_path) → list[dict]`**

Backward trace from a `plot_id` through all contributing manifest steps, in pipeline order:

1. Data source declarations (raw input files + schema)
2. T1 wrangling steps (from each contributing data schema)
3. T2 wrangling steps (if present)
4. Join/assembly recipe steps
5. Plot spec

Returns an ordered list of step dicts: `{step_type, source_file, action, params, description}`.

T3 modifications are NOT included — T3 lives in session state, not the manifest. The caller (export handler or BLUEPRINT handler) appends the T3 overlay from `home_state` after calling this function.

**`get_plot_ids_in_group(group_id, manifest_path) → list[str]`**

Forward trace: reads `analysis_groups[group_id].plots` from the manifest and returns the list of `plot_id`s declared in that group. Used as the first step in group-scope export.

---

### 2. Two tracking modes

| Mode | Used when | Sequence |
|---|---|---|
| **Backward only** | HOME per-plot export; BLUEPRINT node inspection | `build_plot_lineage(plot_id)` → T3 overlay appended by caller |
| **Forward then backward** | HOME group-scope export | `get_plot_ids_in_group(group_id)` → `build_plot_lineage()` for each plot_id |

---

### 3. Export bundle — `lineage/lineage_graph.json`

One JSON file per export scope (not one per plot). Shared steps (T1/T2 assembly nodes used by multiple plots) appear **once** as graph nodes with multiple downstream edges — no duplication. Per-plot paths are expressed as lists of node IDs within the shared graph. The `recipes/` folder already contains the actual YAML content; `lineage_graph.json` is a structural index of how those pieces connect.

```json
{
  "export_scope": "global",
  "generated": "2026-05-09T...",
  "nodes": {
    "node_001": {"step_type": "data_source", "schema_id": "amr_results", "source_file": "..."},
    "node_002": {"step_type": "t1_wrangling", "action": "filter_range", "params": {...}},
    "node_003": {"step_type": "join", "source_file": "assembly/AMR_Profile_Joint.yaml"},
    "node_004": {"step_type": "plot_spec", "plot_id": "multi_resistance_by_country", "source_file": "..."}
  },
  "edges": [
    {"from": "node_001", "to": "node_002"},
    {"from": "node_002", "to": "node_003"},
    {"from": "node_003", "to": "node_004"}
  ],
  "plot_paths": {
    "multi_resistance_by_country": ["node_001", "node_002", "node_003", "node_004"]
  },
  "t3_overlay": {
    "multi_resistance_by_country": []
  }
}
```

---

### 4. `report.qmd` additions

Three lineage-related additions to the report template, all in the report (no separate human-facing files):

1. **Mermaid flowchart** — the full lineage DAG for the export scope, auto-generated from the graph structure. Shared nodes appear once; multiple plot paths branch from the shared trunk. Renders to a visual in HTML/PDF via Quarto's native Mermaid support. No extra dependency — `graphviz` is not added.

2. **Step summary table** — one row per node: Step type | Action/Description | Source file | Plots that use this step. Readable without quarto render (plain markdown in the `.qmd` source). Users who prefer tables over diagrams get full coverage here.

3. **JSON note** — a brief explanatory paragraph adjacent to the download reference: *"`lineage/lineage_graph.json` is a machine-readable version of this lineage graph, intended for tooling and programmatic use (e.g. re-running the pipeline from a script, or building reproducibility checks). Most users can ignore this file — the diagram and summary table above contain the same information in readable form."*

---

### 5. No lineage SVG in HOME export

Pre-rendered SVG of the lineage DAG is explicitly **not** included in HOME exports. The Mermaid block in `report.qmd` is the visual delivery vehicle — it renders when the report is rendered, which is the natural use pattern for this transparency artifact. Adding a standalone SVG would duplicate content and imply publication use, which is not the purpose of lineage documentation.

SVG/PNG export of the manifest DAG for use in pipeline publications is a **BLUEPRINT-scoped feature** (pipeline authors documenting the pipeline architecture itself). This will be addressed in ADR-075.

---

### Consequences

- `manifest_navigator.py` gains two new public functions. Existing five-function public API (ADR-045 §4) is extended — not replaced.
- `export_handlers.py` calls both new functions at export time, appends T3 overlay from `home_state`, builds `lineage_graph.json`, and generates the Mermaid block + step summary table for `report.qmd`.
- `blueprint_handlers.py` uses `build_plot_lineage()` for node inspection in the BLUEPRINT IDE (backward trace from selected plot node).
- `lineage_graph.json` is generated at export time — not stored in session state between exports.
- No new dependencies added.

**Implementation tasks:**
- **LINEAGE-NAV-1** `[sonnet/medium]`: Implement `build_plot_lineage()` and `get_plot_ids_in_group()` in `libs/blueprint_arch/.../manifest_navigator.py`
- **LINEAGE-EXPORT-1** `[sonnet/high]`: Implement `lineage/lineage_graph.json` generation in `export_handlers.py`; add Mermaid flowchart + step summary table + JSON note to `report.qmd` template

---

## ADR-075: BLUEPRINT IDE Build Mode — Design Specification (2026-05-09)

**Status:** DECIDED — implementation pending (Phase 31+)

**Context:** BLUEPRINT is a visual IDE for building and editing SPARMVET manifests without writing code. The core design must be settled before implementation to avoid structural decisions that would require app-wide refactoring later. This ADR establishes the build mode interaction model, action schema format, documentation strategy, color system, and IDE state management.

**Key principle:** *BLUEPRINT users produce and document pipelines.* The IDE output is a valid SPARMVET manifest YAML loadable directly into HOME.

---

### 1. Action Schema — Embedded in Decorator

Action UI schemas are declared as a `ui_schema` keyword argument on the existing `@register_action` and `@register_plot_component` decorators. No separate schema files are created — the schema lives where the action lives, so updating a decorator immediately surfaces that its UI schema also needs updating.

```python
@register_action("filter_range", ui_schema={
    "label": "Filter by range",
    "category": "filtering",
    "context": ["t1", "t2"],
    "tags": ["numeric", "cleaning"],
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "filter"],
               "doc_url": "https://docs.pola.rs/..."}],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "dtype_filter": ["numeric"]},
        "min":     {"widget": "number", "label": "Min value", "required": False},
        "max":     {"widget": "number", "label": "Max value", "required": False},
    }
})
def action_filter_range(lf: pl.LazyFrame, spec: dict) -> pl.LazyFrame:
    ...
```

`blueprint_arch` reads the registry at startup and extracts all `ui_schema` dicts to build the form catalog. No Shiny imports in the action files — Two-Category Law compliant.

---

### 2. Widget Type Vocabulary

| Widget type | Used for | Notes |
|---|---|---|
| `column_selector` | Pick column(s) from upstream schema | `multi: true/false`; `dtype_filter` narrows to compatible types |
| `expression` | Polars expression string | Code editor (Monaco/CodeMirror); schema-aware column autocomplete |
| `enum` | Fixed option list | `options: [...]`; `preview: true` renders a visual sample (e.g. linetype) |
| `dtype_picker` | Polars dtype selection | Dropdown of Polars types |
| `number` | Numeric scalar | `min/max/step/default`; optional `widget: slider` |
| `string` | Free text | Default text input |
| `color` | Color aesthetic binding | See §3 for nested color model |
| `column_or_literal` | Map to column OR set a literal value | Toggle: "Map to column ↔ Set literal value" — fundamental ggplot/plotnine distinction |

**Column selector — dynamic upstream schema propagation:** column selector widgets receive the output schema of the upstream DAG position at form render time. Schema propagates on Apply (not continuously). The `dtype_filter` key restricts the offered columns to compatible types.

---

### 3. Color Widget — Nested Model (v1 scope)

Color is a composite widget with a mode toggle:

```
color field
├── Map to column     → column_selector (categorical columns only)
└── Set literal
    ├── From palette library   → predefined palette picker (ColorBrewer, viridis, etc.)
    ├── From project colors    → [RESERVED — v2, not implemented]
    └── Custom                 → hex color picker
```

**Project color registry (deferred to v2):** the `from_project_colors` slot is reserved in the widget definition and renders as a grayed-out "Coming soon" option. The slot exists so no widget refactoring is required when the registry is implemented. The registry will track `{variable_value → color}` assignments across all plots in the project to enforce visual homogeneity.

---

### 4. Documentation Strategy — Python `__doc__`

For each action's help panel, BLUEPRINT resolves documentation from the installed library at runtime:

```python
def _resolve_doc(wraps_entry: dict) -> str:
    import importlib
    obj = importlib.import_module(wraps_entry["lib"])
    for attr in wraps_entry["attr_path"]:
        obj = getattr(obj, attr)
    return getattr(obj, "__doc__", "") or ""
```

**Benefits:** air-gap safe; always matches the installed version; zero maintenance.

**External URL** (`doc_url`) is optional — rendered as an "Open in browser →" button, disabled in isolated deployments.

**Action naming alignment:** `@register_action` names should match Polars/Plotnine names for 1:1 wrappers (e.g. `sort`, `cast`, `rename`, `filter`). For composite/custom actions (`split_and_explode`, `label_if`), a custom one-line description is written in the decorator, and BLUEPRINT auto-generates: *"This action combines `[fn1]` and `[fn2]`. See component documentation:"* with each `__doc__` in a collapsible section.

Action renames are tracked and migrated via **ACTION-RENAME-1** (compatibility shims + manifest scanner).

---

### 5. Position Rules — BLUEPRINT Enforces DAG Validity

BLUEPRINT enforces valid node placement using the `context` tag in each action's `ui_schema`. Invalid positions are blocked at authoring time (not at manifest run time). The "Add node" menu only offers actions valid at the selected insertion point.

| `context` value | Valid positions |
|---|---|
| `t1` | Before any join/assembly node |
| `t2` | After a join/assembly node, before a plot spec |
| `assembly` | Join/assembly nodes connecting data sources |
| `plot` | Leaf positions in the DAG (plot spec nodes) |

---

### 6. Apply Gate and Edit/Remove After Apply

BLUEPRINT Apply propagates schema through the DAG but the manifest YAML is always the ground truth. No change is destructive until the manifest is saved to disk.

**Three-layer correction model:**

1. **Edit in place** (primary): click any node at any time → re-open form → change values → re-Apply. Node returns to "pending"; downstream nodes are marked schema-invalidated; re-propagation runs on the new Apply.

2. **Session undo deque** (immediate mistakes): 20-step Ctrl+Z restores any prior DAG state including pre-Apply snapshots. Session-only — not persisted between sessions.

3. **YAML escape hatch** (complex corrections): raw YAML view of the manifest. Read-only for all personas with `blueprint_enabled: true`. Editable when `manifest_edit_enabled: true` (see §7). Changes in the editable view re-parse and re-render the DAG on save.

---

### 7. New Persona Flag — `manifest_edit_enabled`

Controls whether the YAML escape hatch is editable (not whether it is visible — the read-only view is always available with `blueprint_enabled`).

| Flag | static | simple | advanced | independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `manifest_edit_enabled` | false | false | false | false | true | true |

Default `false` for all personas. Custom deployments can enable for any persona without code changes. Cascade: if `blueprint_enabled: false`, `manifest_edit_enabled` is suppressed (BLUEPRINT is not active).

---

### 8. Action Picker — Searchable Catalog

The "Add node" picker in BLUEPRINT is a searchable, filtered catalog driven by `ui_schema` metadata:

- Organized by `category` (cleaning, filtering, reshaping, aggregation, etc.)
- Filtered by `context` (only valid actions for the current insertion point)
- Searchable by `tags` and `label`
- `difficulty` tag is NOT used — BLUEPRINT is already persona-gated; further difficulty-based filtering is deferred

---

### Consequences

- `@register_action` and `@register_plot_component` gain an optional `ui_schema` kwarg. Existing decorators without it remain valid — BLUEPRINT degrades to a "no form available" state for unschemed actions.
- `blueprint_arch` gains a `schema_registry.py` module that reads `ui_schema` from the action/component registries at startup.
- `rules_persona_feature_flags.md` gains `manifest_edit_enabled` in the flag table and cascade rules.
- All six persona templates gain `manifest_edit_enabled` entry.
- Action naming audit and migration: **ACTION-RENAME-1**.
- Project color registry: reserved slot in the color widget, deferred to v2.

**Implementation tasks:**
- **BP-SCHEMA-1** `[sonnet/high]`: Add `ui_schema` kwarg to `@register_action` and `@register_plot_component`; implement `schema_registry.py` in `blueprint_arch`; populate schemas for the 20 most-used transformer actions and core viz_factory components as a first pass
- **BP-FORMS-1** `[sonnet/high]`: Implement form renderer in BLUEPRINT IDE — widget types, column selector with upstream schema propagation, Apply gate, edit-in-place flow
- **BP-ESCAPE-1** `[sonnet/medium]`: Implement YAML escape hatch — read-only view (all `blueprint_enabled` personas) + editable mode (`manifest_edit_enabled`) with re-parse on save
- **BP-UNDO-1** `[haiku/low]`: Implement 20-step session undo deque for BLUEPRINT DAG state
- **BP-HELP-1** `[sonnet/medium]`: Implement help panel — `__doc__` resolution via `_resolve_doc()`, collapsible sections for composite actions, optional external URL button (disabled in isolated deployments)
- **BP-COLOR-1** `[sonnet/medium]`: Implement color widget — column mapping toggle, palette library picker, hex color picker, `from_project_colors` slot reserved (grayed out, v2 placeholder)
- **manifest_edit_enabled flag** `[haiku/low]`: Add to all six persona templates + `rules_persona_feature_flags.md` + bootloader cascade

---

## ADR-076: BLUEPRINT AI Agent Helper — Adapter Architecture and Conversational Design (2026-05-09)

**Status:** DECIDED — implementation pending (Phase 31+)

**Context:** ADR-075 establishes BLUEPRINT as a visual IDE for building manifests through forms, schema-aware widgets, and a YAML escape hatch. That model still presumes the user knows *what* they want to build — which actions to chain, which join keys are valid, which aesthetics to map. Bench scientists drafting their first manifest typically do not.

A conversational AI helper, embedded in the BLUEPRINT right sidebar, reduces the floor of expertise required to design a working manifest. The helper interviews the user about the analytical goal, inspects the loaded data schema, proposes a manifest fragment, and drives the user toward a valid YAML output that loads in HOME.

The architectural decision is **how to embed the agent without coupling the app to a single LLM provider**. Three adapter backends are defined, all implementing one protocol. The app stays agnostic. The Two-Category Law (ADR-045) is honoured — the agent layer lives in `libs/blueprint_arch/`, headless-safe, with Shiny wiring confined to a thin handler.

**Key principle:** *The agent never modifies the manifest directly.* Every change is routed through a structured `propose_manifest_diff` tool call which renders as a diff preview in the UI. The user clicks Apply. This invariant is non-negotiable — it preserves user agency, makes the agent's effects auditable, and aligns with the propose-before-apply discipline used throughout SPARMVET (T3 audit gate, BLUEPRINT IDE Apply gate).

---

### 1. Three Adapter Backends — One Protocol

All adapters implement an `AgentAdapter` protocol so the app calls into them through a single interface. Switching backend is a persona-config change, not a code change.

```python
class AgentAdapter(Protocol):
    def start_session(self, system_prompt: str, context: dict) -> str: ...
    def send_message(self, session_id: str, message: str,
                     tools: list[Tool] | None = None) -> AgentResponse: ...
    def end_session(self, session_id: str) -> None: ...
```

| Backend | Identifier | Phase | Auth | Multi-user | Notes |
|---|---|---|---|---|---|
| `ClaudeCliAdapter` | `"claude_cli"` | 1 (now) | Inherits local Claude Code | No | Calls `claude -p "<msg>"` as subprocess in an isolated working directory (see §11). ~1–2 s spawn overhead per turn. Single-user, desktop-style deployment only. |
| `ClaudeApiAdapter` | `"claude_api"` | 2 (planned) | `ANTHROPIC_API_KEY` env var | Yes | Uses `anthropic` Python SDK directly. Per-request isolation. Recommended model `claude-opus-4-7` (configurable). Required for Posit Connect / Galaxy multi-user deployments. |
| `LocalModelAdapter` | `"local"` | 3 (air-gapped) | None | Yes | Calls Ollama / LM Studio compatible endpoint configured via `endpoint:` in persona template. Required for fully offline deployments (NVI internal, classified networks). |
| `DisabledAdapter` | `"disabled"` | always | n/a | n/a | Graceful degradation when `blueprint_agent_enabled: false`, when `claude` CLI is missing/logged-out, when API key is unset, or when adapter initialisation otherwise fails. Returns sentinel responses; UI hides the chat panel and renders an info banner explaining why. |

**Streaming:** All backends are buffered (full response delivered as one block). Token-by-token streaming is **explicitly deferred** — see §9. The UI shows a "thinking…" indicator during in-flight turns. Dropping streaming simplifies adapter implementation, makes the three backends interchangeable from the UI's perspective, and matches the conversational tempo of manifest design (turns are minutes apart, not seconds).

**Selection cascade:** persona template declares `blueprint_agent.backend`. Bootloader instantiates the adapter at startup. If the configured adapter cannot initialise (missing API key, missing endpoint, missing CLI binary, `claude` CLI not logged in), the bootloader falls back to `DisabledAdapter` and logs a warning — startup is never blocked by an agent misconfiguration. `ClaudeCliAdapter.__init__` runs `claude --version` and `claude --status` (or equivalent auth probe) before reporting itself ready.

---

### 2. Persona Configuration Shape

Added to persona templates as a new top-level block, gated by a new flag (Group D — see §6).

```yaml
features:
  blueprint_enabled: true
  blueprint_agent_enabled: true   # new flag — depends on blueprint_enabled

blueprint_agent:
  enabled: true
  backend: "claude_cli"            # claude_cli | claude_api | local | disabled
  model: "claude-opus-4-7"         # claude_api only; ignored by other backends
  api_key_env: "ANTHROPIC_API_KEY" # claude_api only
  endpoint: null                   # local only — full URL incl. port
  instructions_file: "config/ui/agents/blueprint_default.md"  # system prompt path
  gallery_awareness: false         # reserved flag, Phase 1 = false
```

`instructions_file` is a Markdown file containing the system prompt template. Different personas (or different deployments) can point at different instruction files — e.g. an AMR-focused deployment can ship a system prompt with AMR domain knowledge baked in.

`gallery_awareness` is a reserved flag for a future capability where the agent can browse the gallery (`assets/gallery_data/`) and recommend recipes. Phase 1 leaves it unimplemented.

---

### 3. Knowledge Architecture — Three Layers

The agent never sees the entire codebase. It sees three layers, in decreasing order of stability:

#### Layer 1 — Compressed system prompt (session-start, static per turn)

Injected once on `start_session()`. Contains:

- A condensed summary of the action registry (action names + one-line descriptions, grouped by `category`). Generated from `ui_schema` metadata at runtime — no manual maintenance.
- Manifest structure rules: canonical `action:` syntax, `tier1`/`tier2` requirement, `analysis_groups` shape, `final_contract` whitelist semantics.
- Current project context: active manifest path, list of declared `data_schemas`, list of `analysis_groups`.

This layer is rebuilt each session from registry + manifest state — never hand-written.

#### Layer 2 — Dynamic tools (called by the model, not text-parsed)

The agent uses tool calling. The app exposes seven tools; the agent decides which to invoke and when.

| Tool | Purpose |
|---|---|
| `get_available_actions` | List registered transformer actions with full `ui_schema` metadata (params, widgets, doc URLs). Filter by `context` (`t1`/`t2`/`assembly`/`plot`). |
| `get_available_components` | List registered viz_factory components with `ui_schema`. |
| `get_field_contract` | Return `input_fields` / `output_fields` for a named schema, resolved through the recursive lookup in `manifest_navigator.resolve_fields_for_schema()`. |
| `get_data_schema_summary` | Privacy-preserving schema summary: column names, dtypes, cardinality, min/max/mean/null-count for numerics, top-N values for categoricals. Reuses extraction logic from `AquaSynthesizer` (Test Lab's synthetic data generator) so we have one canonical schema-summary code path. **No raw rows.** |
| `get_current_manifest_section` | Read a section of the active manifest (e.g. `data_schemas.amr_results`, `analysis_groups.amr_insight`, `assembly.AMR_Profile_Joint`). Used so the agent can inspect what's already there before proposing changes. |
| `validate_manifest_fragment` | Run the existing manifest validator on a candidate YAML fragment without applying it. Returns structured errors (line, key, message). |
| `propose_manifest_diff` | **The only path through which manifest changes reach the user.** Submit a structured diff (target file path, JSON-patch-style operations). The UI renders it as a diff preview and unlocks the Apply button. |

Tool calls are structured (JSON) — the agent never emits free-text "here is your manifest, paste this in" output. If it tries, the UI does not render an Apply button.

#### Layer 3 — Per-turn session context (small, dynamic, attached to each turn)

A small dict appended to each user turn so the agent can reason about what the user is currently doing:

```python
{
  "active_workspace": "blueprint",
  "active_plot_subtab": "multi_resistance_by_country",  # if focused
  "current_manifest_section": "assembly.AMR_Profile_Joint",
  "last_validation_error": {...} | None,
  "row_counts": {"t1_anchor": 1240, "t2_branch": 870},  # only when data loaded
}
```

`row_counts` is the **wrangling performance profiler** — it lets the agent recommend ordering operations for UI responsiveness (e.g. "Filter on `Year` first — cuts the frame from 1240 to ~140 rows before the join — keeps the join cheap"). It surfaces through this context layer, not as a separate tool.

---

### 4. Data Visibility Toggle

The agent never sees raw data unless the user explicitly opts in. A three-state toggle in the agent panel governs what `get_data_schema_summary` returns.

| Mode | What the agent sees | Persona availability |
|---|---|---|
| `off` | Tool returns `{"data_visibility": "off"}` — agent has no schema info, must ask the user to describe the data. | All personas |
| `schema_summary` | Column names, dtypes, cardinality, min/max/mean/null-count for numerics, top-N (≤ 20) unique values for categoricals. **No raw rows ever.** Reuses `AquaSynthesizer` extraction. | All personas — **default** |
| `full_sample` | First 5 rows as TSV plus the schema summary. | `developer` persona only — never available to scientist personas |

Default is `schema_summary` — enough for the agent to suggest plausible filter values, join keys, and aesthetic mappings, without exposing patient-level or sample-level rows. Toggling to `off` is a one-click privacy escape; `full_sample` requires an explicit opt-in and is hidden outside the developer persona.

---

### 5. Propose-Before-Apply UI Discipline

The right sidebar in BLUEPRINT, when the agent is enabled, contains:

1. **Conversation log** — turn-by-turn, scrollable. Buffered (no streaming — see §1). A "thinking…" indicator appears between user submit and the next agent message.
2. **Decision summary accordion** — a running list of decisions the user and agent have agreed during the session ("Filter on Year ≥ 2020", "Use sample_id as join key", etc.). Built from `propose_manifest_diff` calls that were applied. Editable as a memory aid — survives panel switches via `home_state`-style reactive value. Persisted to the manifest creation report (§7).
3. **Pending diff preview** — only visible when the agent has just emitted `propose_manifest_diff` and the user has not yet acted. Shows the YAML diff with the BLUEPRINT diff renderer.
4. **Apply button** — gated. Only active when there is a pending `propose_manifest_diff`. Disabled otherwise. Clicking Apply: writes the diff to the in-memory manifest (not yet to disk — manifest persistence is the user's separate Save action), invalidates downstream BLUEPRINT DAG nodes, appends the decision to the summary accordion.
5. **Reject / Revise button** — discards the pending diff; the agent receives a turn message explaining the rejection so it can revise.
6. **Data visibility toggle** — three radio options (off / schema_summary / full_sample), gated by persona.

**Cold start (first open of BLUEPRINT in a session):** the chat panel renders a static greeting — adapter status (claude_cli / claude_api / local / disabled), data visibility default (`schema_summary`), and a one-line prompt ("Describe the analysis you want to build, or paste a goal statement"). No agent turn is consumed until the user submits.

**Single-flight discipline:** while a turn is in flight, the input is disabled and the submit button shows a spinner. Concurrent submissions are not allowed at the UI level (orthogonal to the subprocess lock in §11 — that is the backend safety net).

**Hard invariant:** the agent calling any tool other than `propose_manifest_diff` does NOT enable the Apply button. Reading state (`get_field_contract`, `get_data_schema_summary`, etc.) is read-only — the user sees the agent's responses but the manifest is not touched until a diff is proposed and applied.

---

### 6. New Persona Flag — `blueprint_agent_enabled` (Group D)

Added to `rules_persona_feature_flags.md` Group D (developer features), depends on `blueprint_enabled`.

| Flag | static | simple | advanced | independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `blueprint_agent_enabled` | false | false | false | false | true | true |

**Cascade rule:** `bootloader._load_persona_config()` forces `blueprint_agent_enabled = False` whenever `blueprint_enabled == False` (analogous to ADR-075's `manifest_edit_enabled` cascade). Logs `[Bootloader] WARNING: blueprint_agent_enabled=True ignored — blueprint_enabled=False` when the violation is detected.

**Default disabled for scientist personas (advanced, independent).** The agent is rolled out to developer + qa first to validate the prompt/tool surface before exposing it to scientists. Once validated, the flag can be flipped per deployment without code changes — including custom deployments that ship a domain-specific `instructions_file`.

---

### 7. Manifest Creation Report

Each agent session that produces an applied manifest fragment yields a report bundle stored under `agent_sessions/{uuid}/`:

| File | Contents |
|---|---|
| `conversation.jsonl` | Full turn-by-turn log: user message, agent response, tool calls, tool responses. One JSON object per line. |
| `report.qmd` | Quarto-rendered summary: goal statement (extracted from the opening user turns), data summary used, decisions made (from the decision summary accordion), final manifest fragment as YAML code block, agent backend used, model name (if applicable). |
| `manifest_sha256.txt` | SHA256 of the final manifest fragment. Lets a later session verify whether the manifest still matches the agent-produced version. |

`agent_sessions/` is a new directory under the project root, git-ignored. Bundle location is configurable via deployment profile (default: `{project_root}/agent_sessions/`).

---

### 8. Two-Category Law Compliance

| Component | Location | Category |
|---|---|---|
| `AgentAdapter` protocol + concrete adapters | `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` | Pure module — no Shiny imports. Importable from headless scripts and tests. |
| 7 agent tools | `libs/blueprint_arch/src/blueprint_arch/agent_tools.py` | Pure functions wrapping existing `manifest_navigator` and registry APIs. Headless-safe. |
| System prompt builder + context builder | `libs/blueprint_arch/src/blueprint_arch/agent_context.py` | Pure functions that read manifest + registry state and produce the Layer 1 prompt and Layer 3 context dict. |
| Tool-call parser (claude_cli) | `libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py` | Pure module. Parses fenced `<!-- AGENT_TOOL_CALL -->` JSON blocks out of `claude -p` stdout (see §10). |
| Default instructions Markdown | `config/ui/agents/blueprint_default.md` | Static asset. |
| Chat panel — sidebar registration | `app/modules/sidebar_registry.py` — new `blueprint_agent_chat` entry. | Headless-safe registry under ADR-073. |
| Chat panel — CSS | `config/ui/theme.css` — new `.bp-agent-*` rule block (per ADR-055, no inline styles). | Static asset. |
| Chat panel UI + reactive wiring | `app/handlers/blueprint_handlers.py` — extended with chat panel render outputs, submit-effect, single-flight gate. | Shiny-only. Imports from `blueprint_arch` adapters. |

This placement keeps the adapter and tool surface testable from the CLI (e.g. drive a `ClaudeCliAdapter` from a debug script with a fake manifest path) and keeps Shiny side-effects out of the library layer.

---

### 9. Confirmed Non-Decisions (Deferred)

- **Token-by-token streaming (SSE)** — explicitly out of scope for Phase 1, all backends. Re-evaluate if user feedback indicates the buffered tempo feels sluggish. Adopting streaming later is a per-adapter concern; the `AgentAdapter` protocol does not need to change (a streaming variant returns an async iterator instead of an `AgentResponse`).
- **MCP server exposing the 7 tools** — Phase 2 path for `claude_cli`. Replaces the JSON-in-fenced-block protocol from §10 with first-class MCP tool calls. Cleaner, more reliable, but requires MCP server boilerplate + user-side `--mcp-config` registration. Defer until the JSON protocol shows reliability problems in practice.
- **Gallery awareness** (`gallery_awareness: true`) — would let the agent browse `assets/gallery_data/` and recommend recipes. Reserved flag; not implemented in Phase 1. The gallery already has a structured `gallery_index.json` (ADR-037) which makes this cheap to add later.
- **Multi-user isolation for `claude_cli`** — even with the per-session `--cwd` discipline in §11, `claude_cli` is single-user by design (subprocess concurrency, local auth). For Posit Connect / Galaxy / IRIDA multi-user contexts, use `claude_api` instead.
- **Token / cost reporting per session** — useful for budgeting but adds adapter-specific code paths. Defer until a deployment requests it.
- **Agent-driven HOME workflows** — the agent in this ADR is BLUEPRINT-scoped (manifest design). A future ADR may extend it to HOME (T3 audit suggestions, filter recommendations). Keep the adapter library generic enough to support this; do not couple the tool surface to BLUEPRINT specifics.

---

### 10. Tool-Call Mechanism — Adapter-Specific

Tool calling (Layer 2 of §3) is the load-bearing mechanism that makes `propose_manifest_diff` reliable. Different adapters expose tool calling differently — this section documents the Phase 1 approach for each.

| Adapter | Mechanism | Reliability | Notes |
|---|---|---|---|
| `ClaudeCliAdapter` | **JSON-in-fenced-block protocol** (Phase 1) | High with strict prompt + parser | `claude -p` does not expose user-defined tools — only Claude Code's own (Read/Edit/Bash/...). The system prompt instructs the agent to emit tool calls as fenced blocks tagged with an HTML comment marker. Server-side parser extracts them. |
| `ClaudeApiAdapter` | Native `tool_use` / `tool_result` blocks via Anthropic SDK | Highest — first-class | Standard tool calling; no parsing fragility. |
| `LocalModelAdapter` | Endpoint-defined (Ollama function-calling, OpenAI-compatible tools, or fenced-block fallback) | Variable | Fenced-block fallback is the lowest common denominator; check endpoint capabilities at init. |

#### 10.1 JSON-in-fenced-block protocol (claude_cli, Phase 1)

The agent is instructed (via the system prompt in `blueprint_default.md`) to emit any tool call as a fenced YAML or JSON block prefixed by an HTML-comment marker:

````
<!-- AGENT_TOOL_CALL -->
```json
{
  "tool": "propose_manifest_diff",
  "arguments": {
    "target": "config/manifests/pipelines/my_pipeline.yaml",
    "operations": [
      {"op": "add", "path": "/data_schemas/amr_results/wrangling/tier1/-",
       "value": {"action": "filter_range", "columns": ["identity"], "min": 90}}
    ]
  }
}
```
<!-- /AGENT_TOOL_CALL -->
````

The server-side parser (`agent_tool_parser.py`) scans each agent reply for these marker pairs, extracts the JSON, validates against a Pydantic / dataclass schema for the named tool, and dispatches to the corresponding function in `agent_tools.py`. If parsing fails, the parser injects a system-turn error message ("Tool call malformed: …") and the agent re-tries on the next turn.

**The parser is not free-text reasoning** — it requires the exact marker pair and valid JSON. Any agent text outside the marker pair is treated as conversation, not a tool call.

#### 10.2 Why not a hybrid

A "hybrid that auto-upgrades to MCP if available" sounds appealing but doubles the surface area to test. Phase 1 ships the fenced-block protocol exclusively; the MCP path becomes a clean migration when authored.

---

### 11. Subprocess Isolation Discipline (claude_cli)

The naïve `claude --continue -p "<msg>"` call inherits the **most recent** conversation in the current project directory. If the user is also running Claude Code in their terminal (the very scenario that motivated this adapter — reusing existing auth), the BLUEPRINT agent's turns would interleave with the user's terminal turns. This is unacceptable: the agent must have its own conversation thread.

**Solution:** every BLUEPRINT agent session runs in a dedicated working directory, isolated from the user's main project conversation.

```
{project_root}/agent_sessions/{uuid}/
    .cwd-marker       # empty file — anchors a separate Claude Code project context
    conversation.jsonl
    lock              # POSIX lock file — single-flight enforcement
    report.qmd        # written on session end (§7)
    manifest_sha256.txt
```

**Subprocess invocation pattern:**

```python
SESSION_DIR = project_root / "agent_sessions" / session_uuid
SESSION_DIR.mkdir(parents=True, exist_ok=True)
(SESSION_DIR / ".cwd-marker").touch()

# First turn of the session:
proc = await asyncio.create_subprocess_exec(
    "claude", "-p", message,
    cwd=str(SESSION_DIR),
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
)

# Every subsequent turn in the same session:
proc = await asyncio.create_subprocess_exec(
    "claude", "--continue", "-p", message,
    cwd=str(SESSION_DIR),
    ...
)
```

Because Claude Code scopes session history per project directory, running the subprocess inside `{project_root}/agent_sessions/{uuid}/` puts each agent session in its own conversation thread, fully isolated from the user's main terminal session and from other agent sessions.

**Single-flight lock.** The adapter takes an exclusive `flock` on `lock` for the duration of a turn. A second concurrent turn blocks (or fails fast — implementation choice; default is fail-fast with a UI message "Agent is busy, please wait"). This prevents subprocess overlap if the UI single-flight gate (§5) is bypassed.

**Cleanup.** `end_session()` removes the lock file but preserves the directory (it contains the report bundle from §7). A periodic cleanup job (out of scope for Phase 1) can purge sessions older than N days.

**Auth precondition.** `ClaudeCliAdapter.__init__` runs `claude --version` and an auth probe (e.g. `claude --status`, or a trivial `claude -p "ok"` in a temp dir) at bootloader time. If either fails, the adapter raises and the bootloader falls back to `DisabledAdapter` with a UI banner explaining the cause ("Claude CLI not installed", "Claude CLI not logged in").

---

### Consequences

- New library module under `libs/blueprint_arch/` for adapters, tools, context, tool-call parser. No new top-level library — agent surface is BLUEPRINT-scoped for now.
- New Group D persona flag (`blueprint_agent_enabled`) with cascade to `blueprint_enabled`.
- New `blueprint_agent:` config block in persona template — only `developer` and `qa` ship with a populated block in Phase 1.
- New static asset directory `config/ui/agents/` containing default system prompts. Deployments can override per persona via `instructions_file`.
- New `agent_sessions/{uuid}/` per-session directory under project root (git-ignored) — used both as the subprocess `cwd` for `claude_cli` isolation (§11) and as the location of the manifest creation report bundle (§7).
- New `blueprint_agent_chat` panel type in `app/modules/sidebar_registry.py` (under ADR-073), wired into the BLUEPRINT workspace `right_sidebar.panels` slot list of the `developer` and `qa` persona templates. Co-exists with the existing `blueprint_logic` panel.
- New `.bp-agent-*` rule block in `config/ui/theme.css` (under ADR-055 — no inline styles).
- BLUEPRINT right sidebar gains the chat panel only when `blueprint_agent_enabled: true` AND a non-`DisabledAdapter` is active. Otherwise the panel slot renders nothing (or a small "agent unavailable" banner if init failed).
- Streaming is explicitly out of scope (Phase 1) — all backends buffer the response and the UI shows a "thinking…" indicator.
- No app-wide refactor required — the agent is purely additive. Existing BLUEPRINT IDE behaviour is unchanged when the flag is off.
- The `propose_manifest_diff` invariant is the discipline that makes the agent safe to ship — auditability and user agency are preserved.

**Implementation tasks** (full text in `.claude/tasks/tasks.md`):

| ID | Effort | Scope |
|---|---|---|
| `BP-AGENT-FLAG-1` | `[haiku/low]` | Persona flag + config block + cascade |
| `BP-AGENT-1` | `[sonnet/high]` | Adapter protocol + ClaudeCliAdapter (with §11 isolation) + DisabledAdapter + auth probe + context builder |
| `BP-AGENT-PARSER-1` | `[sonnet/medium]` | `agent_tool_parser.py` — fenced-block extractor, JSON validator, dispatch (per §10) |
| `BP-AGENT-TOOLS-1` | `[sonnet/medium]` | The 7 agent tools wrapping `manifest_navigator` + registry + `AquaSynthesizer` extraction |
| `BP-AGENT-INSTRUCT-1` | `[sonnet/medium]` | `config/ui/agents/blueprint_default.md` system prompt + tool-call format instructions |
| `BP-AGENT-PANEL-1` | `[haiku/low]` | Register `blueprint_agent_chat` in `sidebar_registry.py` + add to BLUEPRINT right sidebar in developer/qa templates |
| `BP-AGENT-UI-1` | `[sonnet/high]` | Chat panel render outputs in `blueprint_handlers.py`: conversation log, decision accordion, Apply gate, single-flight gate, data visibility toggle, cold-start greeting |
| `BP-AGENT-CSS-1` | `[haiku/low]` | `.bp-agent-*` rules in `config/ui/theme.css` |
| `BP-AGENT-REPORT-1` | `[sonnet/low]` | Per-session `agent_sessions/{uuid}/` bundle (`conversation.jsonl`, `report.qmd`, `manifest_sha256.txt`) |
