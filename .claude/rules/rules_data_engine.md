---
trigger: always_on
deps:
  provides: [rule:3tier_lifecycle, rule:wrangling_block_structure, rule:decorator_standards, rule:polars_parity]
  documents: [libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/actions/]
  consumed_by: [.claude/rules/rules_persona_bioscientist.md, .claude/knowledge/dependency_index.md]
---

# Data Engine & Transformation Protocols (rules_data_engine.md)

**Authority:** Defines the 3-Tier Tree Lifecycle and Wrangling contracts (Replaces tiered_data and wrangling legacy docs).

## 1. The 3-Tier Tree Data Lifecycle

To resolve 22-minute render bottlenecks and orchestrate Polars data hand-offs, the VIGAS-P pipeline strictly adheres to a three-tier lifecycle:

### Tier 1 (The Trunk): Relational Anchor

- **Definition:** Logic applied to a common data source (identified by ID or Path) that is shared by ALL plots dependent on that source. This guarantees the fully composed and joined dataset remains highly generic.
- **Persistence:** Materialized to disk via `pl.sink_parquet("tmp/session_anchor.parquet")`.
- **Instruction:** To minimize recalculation, always suggest a wrangling sequence that prioritizes shared transformations as early as possible (Tier 1) based on the common data source ID/Path.

### Tier 2 (The Branch): Plot-Specific Anchor

- **Definition:** Logic or pre-aggregation shared by a Functional Group of plots (e.g., all Heatmaps using the same filtered subset).
- **Persistence:** Saved optimally as specific Parquet branches (e.g., `tmp/branch_plot_density.parquet`).
- **The Bifurcation Point Rule:** If logic is shared globally by a data source, it lives in the Trunk (Tier 1). If it strictly serves a defined functional plotting group or a unique set of visuals, it branches here into Tier 2.

### Tier 3 (The Leaf): Interactive UI View

- **Definition:** Transient, dynamic subsets generated on-the-fly (`pl.LazyFrame`) derived directly from Tier 1 or Tier 2.
- **Execution:** Handled exclusively via Predicate Pushdown (`pl.scan_parquet().filter()`) from user UI inputs (sidebars, date ranges).
- **Handoff:** Only this lightweight leaf is collected into memory (`.collect()`) prior to sending to `VizFactory`.

## 2. Wrangling Decorator Standards (The Law of Decorators)

- **Homogeneity:** All wrangling actions MUST use `@register_action("name")`.
- **Signature:** Actions accept exactly two arguments: `(lf: pl.LazyFrame, spec: Dict[str, Any])`.
- **Atomicity:** Actions must be independent, extracting parameters entirely from `spec`.
- **1:1:1 Naming Law:** Logic: `@register_action("name")` -> Manifest: `name_manifest.yaml` -> Data: `name_test.tsv`.

## 3. The Tiered Manifest Mandate (ADR-024)

To ensure consistency across the 3-Tier Lifecycle, all `wrangling` blocks in YAML manifests MUST adopt the tiered nesting structure.

### Structure Requirement

- **`tier1`**: Required (even if empty). Contains relational foundations (cleaning, joining, column renaming). This is the shared "Trunk" of the data tree. MUST be a Sequential List of actions.
- **`tier2`**: Optional. Contains plot-specific transformations (aggregations, reshaping to long format, specific subsetting). This is the "Branch". MUST be a Sequential List of actions.

```yaml
wrangling:
  tier1: [ ...ordered actions... ]
  tier2: [ ...ordered actions... ] # Optional: skipped via Identity Logic if omitted
```

### Proactive Refactoring Rule

Agents encountering legacy manifests with a flat `wrangling: []` list MUST proactively suggest refactoring them into the tiered structure.

## 4. The Manifest Data Contract (ADR-013 & Identity Logic)

YAML manifests MUST contain:

1. `input_fields`: Raw incoming schema. MUST be a Rich Dictionary (`slug: {props}`).
2. `wrangling`: Tiered nesting of operational Sequential Lists for atomic processing.
3. `output_fields`: The Published Contract (Terminal Polars `.select()` step). MUST be a Rich Dictionary (`slug: {props}`).

- **Identity Transformations (ADR-014):**
  - If a specific tier is omitted or empty, the data passes through unchanged (Identity).
  - If `output_fields` is omitted/empty, all `input_fields` are retained (Import-As-Is).

## 5. The Polars Parity Mandate (ADR-035)

To ensure the SPARMVET pipeline remains a "State of the Art" analytical engine, the Transformer library MUST strive for **1:1 Functional Parity** with the Polars core library.

- **Parity Rule**: Every significant high-level transformation available in the `polars` API should have a corresponding `@register_action` decorator in the Transformer layer.
- **Maintenance**: Upon major Polars releases, the agent MUST perform an inventory audit to identify and implement new functional gaps.
- **Goal**: Allow users to define any valid Polars transformation via declarative YAML without requiring custom Python code extensions.

## 6. Scientific Audit Protocol (Development Phase)
- **The Protocol**: During the development phase of a new lineage, all intermediate data tiers MUST be materialized for manual review.
- **The Rule**: Materialization outputs MUST include both Tier 1 (Atomic Wrangling results) and Tier 2 (Assembly/Aggregate results).
- **Tooling**: Use `debug_wrangler.py` for Tier 1 and `debug_assembler.py` for Tier 2 verification.

## 7. Precision Renaming & Column Retention
- **Retention Rule**: "Identity" columns (ID, gene, original metadata keys) MUST be retained throughout Tier 1 and Tier 2 wrangling to facilitate auditing. They should only be dropped at the final assembly contract.
- **Naming Rule**: Favor biological and source precision. Use underscores and descriptive names to avoid collision or ambiguity (e.g., `predicted_phenotype` instead of generic `phenotype`).
- **Standard**: Renaming should be handled as early as possible (Tier 1) to establish a stable internal contract.
