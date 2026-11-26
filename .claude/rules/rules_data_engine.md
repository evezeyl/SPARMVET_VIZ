---
trigger: always_on
deps:
  provides: [rule:3tier_lifecycle, rule:wrangling_block_structure, rule:decorator_standards, rule:polars_parity]
  documents: [libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/actions/, libs/transformer/src/transformer/engine_python_polars.py, app/modules/cache_keys.py, app/modules/engine_registry.py]
  consumed_by: [.claude/rules/rules_agent_role_bioscientist.md, .claude/knowledge/dependency_index.md]
---

# Data Engine & Transformation Protocols (rules_data_engine.md)

**Authority:** Defines the 3-Tier Tree Lifecycle and Wrangling contracts (Replaces tiered_data and wrangling legacy docs).

## 1. The 3-Tier Tree Data Lifecycle

To resolve 22-minute render bottlenecks and orchestrate Polars data hand-offs, the VIGAS-P pipeline strictly adheres to a three-tier lifecycle:

### Before Tier 1: the read of the files and the completion of the ids

The first place of every table is Tier 1. Before its steps run, the files are read as they are (strip, the missing-value words of the recipe, the declared type) and the ids are made equal: every table that declares an entity id (and the metadata) gets a line for each id of the union that it lacks, with a yes/no marker column; nothing is removed or changed, nothing blocks, the checks are warnings with a log (`libs/utils/src/utils/id_completion.py`, `rules_data_analysis_recipe_structure.md` section 13; D-0572 to D-0599, D-0613). There is no T0 place (D-0613): the user cannot choose a place before the completion, and no step of an audit runs before it.

### Tier 1 (The Trunk): Relational Anchor

- **Definition:** Logic applied to a common data source (identified by ID or Path) that is shared by ALL plots dependent on that source. This guarantees the fully composed and joined dataset remains highly generic.
- **Persistence:** Materialized to disk via `pl.sink_parquet("tmp/session_anchor.parquet")`.
- **Cache key:** the Tier 1 parquet is valid only while its `tier1_key` matches. Each stored table has its own key, a series of labelled parts: the engine and cache version, the definition of the table and of what it reads, and the content of the data files it reads (ADR-089, ADR-101, D-0025; built, cache version 6, `app/modules/cache_keys.py`). A key contains the engine of what it stores and nothing else: the effective data engine of each tier is an argument of that tier's key, and the plot engine is in no table key (D-0240). Never reuse an anchor by file name alone.
- **Instruction:** To minimize recalculation, always suggest a wrangling sequence that prioritizes shared transformations as early as possible (Tier 1) based on the common data source ID/Path.

### Tier 2 (The Branch): Plot-Specific Anchor

- **Definition:** Logic or pre-aggregation shared by a Functional Group of plots (e.g., all Heatmaps using the same filtered subset).
- **Persistence:** Stored as one Parquet per join with a non-empty `tier2` (`<name>__T2.parquet`), keyed by its own `tier2_key` (the parts of its Tier 1 key plus the tier-2 steps; the tier-2 engine is an argument of it; ADR-089, ADR-101, D-0025, D-0240); an empty `tier2` means T2 equals T1 and nothing is stored. Implemented 2026-11-06 (fork issue #10): `DataOrchestrator.materialize_tier2()` reads the stored file when its key matches, otherwise recomputes it from the valid Tier 1.
- **The Bifurcation Point Rule:** If logic is shared globally by a data source, it lives in the Trunk (Tier 1). If it strictly serves a defined functional plotting group or a unique set of visuals, it branches here into Tier 2.

### Tier 3 (The Leaf): Result data (T3), the table the plot reads

- **Definition:** Result data (T3) is the last data table, the one the plot reads: the Tier 2 of its target (Tier 1 when the target has no tier-2 steps) plus the plot's own `tier3` steps of the recipe; with no such steps T3 equals T2 (D-0024, D-0179, D-0343). T1 feeds T2 feeds T3 feeds the plot. The table a plot reads is T1, T2 or T3, depending on which tiers have steps (an empty tier equals the one before); T3 is the table behind the last data step that enters the plot (owner's word rule, channel blocks M700 and M701, 2026-11-26).
- **Execution (built):** `DataOrchestrator.materialize_tier3()` (`app/modules/orchestrator.py`) is the one reader of the data of a plot: HOME's plot and its Result data (T3), the export and the pictures read it, so a plot equals the table it reads. It returns a `pl.LazyFrame`; its key is `DataAnalysisRecipeKeys.plot_key_of(plot_id)`. It is stored (Parquet, read back while its key matches) when the plot has tier-3 steps of its own; a plot without them reads its Tier 2 and no file is added, and a stored file of a plot that lost its tier-3 steps is removed when found (`app/modules/orchestrator.py:808-855`; D-0343). The table of an audit copy handed in as a recipe is computed lazily and stored nowhere (`orchestrator.py:816-818`, PROVISIONAL). Exploration filters never reach it (D-0327); in Audit mode the audit steps are applied on top of it. The audit steps of a copy of the recipe take part in the keys of the copy as the parts `a1`, `a2`, `a3`, each holding the operations of its tier in list order, with no position among the original steps (`app/modules/cache_keys.py:224-231`); HOME reads the tables of that copy (`app/modules/audit_view.py`, `audit_run.py`; `app/handlers/home_theater.py`).
- **Handoff:** Only this leaf is collected into memory (`.collect()`) prior to sending to `VizFactory`.

### The opening of a recipe (DECIDED, built)

At the opening of a recipe the app builds and stores by key every tier 1 and tier 2 table and the tier 3 table of every plot that has its own tier 3 steps (a plot without them reads its tier 2 table and adds no file; a join without tier 2 steps stores nothing extra), and draws every plot once as the proof that it draws; no picture is stored, a plot is drawn again when it is selected; an error of the original recipe found while building is reported through the load gate with a plain reason; a later open with equal keys rebuilds nothing (D-0326, D-0335, D-0343). The first open shows a progress line in plain words (for example "tables 12 of 24, plots 5 of 17", D-0334). With a lot of data the recipe maker counts or aggregates first; the app warns in plain words when a plot receives very many rows and refuses nothing; the number of rows that triggers the warning: see D-0363 below (D-0336). A test shows that a recipe with a plot that cannot be drawn is refused at opening with a plain reason (D-0327). Built: `app/modules/opening_build.py` (`build_plan`, `run_opening`, `draw_plot_proof`, `progress_text`, `large_plot_warning`) and `app/handlers/opening_handlers.py` (the progress line, the refusal through `Bootloader.reject_after_opening`); the number of rows that triggers the warning is 1,000,000 and stays (D-0363; `opening_build.py:44`); tests `app/tests/test_opening_build.py`, `test_opening_failures.py`, `test_opening_handler.py`, `test_opening_browser.py`. The wording of the messages is PROVISIONAL.

## 2. Wrangling Decorator Standards (The Law of Decorators)

- **Homogeneity:** All wrangling actions MUST use `@register_action("name")`.
- **Signature:** Actions accept exactly two arguments: `(lf: pl.LazyFrame, spec: Dict[str, Any])`.
- **Atomicity:** Actions must be independent, extracting parameters entirely from `spec`.
- **Determinism (ADR-090):** the same input gives the same rows in the same order. An action that can reorder rows (grouping, deduplication, joins, sorting, sampling) states its order rule in its description and has a test of that rule (`libs/transformer/tests/test_deterministic_order.py`). Polars promises no row order unless asked: use `maintain_order`, `keep="first"`, `maintain_order="left_right"` for joins, and a fixed default `seed` for anything random.
- **1:1:1 Naming Law:** Logic: `@register_action("name")` -> Data analysis recipe: `name_data_analysis_recipe.yaml` -> Data: `name_test.tsv`.
- **Documentation Standard (ADR-075 §1/§4):** All actions MUST carry `description` and `yaml_example` in their `ui_schema`. `description` is one developer-oriented sentence (when to use this, vs. alternatives). `yaml_example` is a minimal correct YAML snippet for copy-paste into a data analysis recipe `tier1:`/`tier2:` block. For 1:1 Polars wrappers, `wraps` MUST also be populated (points to the Polars `LazyFrame`/`Expr` method — `importlib`-resolved at runtime by the help panel). See ADR-075 §4 for the full resolution fallback chain.

## 3. The Tiered Data Analysis Recipe Mandate (ADR-024)

To ensure consistency across the 3-Tier Lifecycle, the tiers of every table and join in YAML data analysis recipes MUST be written as keys of their own (`tier1`, `tier2`; `tier3` in a plot entry), each a mapping with an optional `data_engine` (first key) and `steps` (D-0250; built).

### Structure Requirement

- **`tier1`**: Required (even if its `steps` are empty). Contains relational foundations (cleaning, joining, column renaming). This is the shared "Trunk" of the data tree. Its `steps` MUST be a Sequential List of actions.
- **`tier2`**: Optional. Contains plot-specific transformations (aggregations, reshaping to long format, specific subsetting). This is the "Branch". Its `steps` MUST be a Sequential List of actions.
- **`data_engine`**: Optional, the first key of a tier. The engine that runs the tier; without it the `data_engine` at the top of the data analysis recipe applies. The list of engine names is open: a new name ships with an app release, and an app without its library refuses the value with "no library for this engine in this app" (D-0239).

```yaml
tier1:
  steps: [ ...ordered actions... ]
tier2:                               # Optional: skipped via Identity Logic if omitted
  steps: [ ...ordered actions... ]
```

### Flat List Rejection (LEGACY-FLAT-WRANGLING-1, Phase 34)

The engine rejects a tier written as a flat list, and the old container `wrangling:`, with a `DataAnalysisRecipeError`. All data analysis recipes must use the tiered structure. If a legacy data analysis recipe is encountered with a flat list, migrate it before running.

## 4. The Data analysis recipe Data Contract (ADR-013 & Identity Logic)

YAML data analysis recipes MUST contain, for each schema:

1. `input_fields`: Raw incoming schema. MUST be a Rich Dictionary (`slug: {props}`).
2. `tier1` (and optionally `tier2`): the tiers, each with its ordered `steps` (section 3).

`output_fields` and `final_contract` are removed: the published columns of a collection are the last step of its tier 1, a plain `polars_select` (or `polars_drop`), so every column change is a visible step (D-0034, DEC23; built: the checker refuses both keys with the replacement named). ADR-013/014 are superseded on this point.

- **Identity Transformations (ADR-014):**
  - If a specific tier is omitted or empty, the data passes through unchanged (Identity).

## 5. The Polars Parity Mandate (ADR-035)

To ensure the SPARMVET pipeline remains a "State of the Art" analytical engine, the Transformer library MUST strive for **1:1 Functional Parity** with the Polars core library.

- **Parity Rule**: Every significant high-level transformation available in the `polars` API should have a corresponding `@register_action` decorator in the Transformer layer.
- **Names (D-0036, DEC31-42; built):** `polars_<name>` is exactly the Polars call (tested against the direct call); `modif_<name>` is a Polars idea with a documented change; `step_<name>` is several calls. No hidden choice: a parameter that changes the result is required, or its default is the Polars default. Old names without a prefix are refused with the new name.
- **Maintenance**: Upon major Polars releases, the agent MUST perform an inventory audit to identify and implement new functional gaps.
- **Goal**: Allow users to define any valid Polars transformation via declarative YAML without requiring custom Python code extensions.

## 6. Scientific Audit Protocol (Development Phase)
- **The Protocol**: During the development phase of a new lineage, all intermediate data tiers MUST be materialized for manual review.
- **The Rule**: Materialization outputs MUST include both Tier 1 (Atomic Wrangling results) and Tier 2 (Assembly/Aggregate results).
- **Tooling**: Use `debug_wrangler.py` for Tier 1 and `debug_assembler.py` for Tier 2 verification.

## 7. Precision Renaming & Column Retention
- **Retention Rule**: "Identity" columns (ID, gene, original metadata keys) MUST be retained throughout Tier 1 and Tier 2 wrangling to facilitate auditing. They should only be dropped by the last `polars_select` of the collection's tier 1 (there is no final contract any more, D-0034).
- **Naming Rule**: Favor biological and source precision. Use underscores and descriptive names to avoid collision or ambiguity (e.g., `predicted_phenotype` instead of generic `phenotype`).
- **Standard**: Renaming should be handled as early as possible (Tier 1) to establish a stable internal contract.
