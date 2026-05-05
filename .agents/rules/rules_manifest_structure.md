---
trigger: always_on
deps:
  provides: [rule:canonical_recipe_syntax, rule:directory_taxonomy, rule:analysis_groups_structure, rule:final_contract]
  documents: [libs/transformer/src/transformer/data_assembler.py, app/handlers/home_theater.py]
  consumed_by: [.agents/rules/rules_persona_bioscientist.md, docs/appendix/manifest_structure.yaml, .antigravity/knowledge/dependency_index.md]
---

# Manifest Structural Standard (rules_manifest_structure.md)

**Authority:** Defines the structural organization and explicit layout requirements for all project data and plotting manifests.

## 1. Basename Mirroring Mandate (Keyword & Complexity Trigger)

To maintain modularity and prevent YAML bloat, **high-complexity manifests** (e.g., Master Pipelines) MUST separate their logical components into individual YAML snippet files via the `!include` constructor.

- **The Rule**: A main manifest file (e.g., `main.yaml`) MUST organize its `!include` components within a directory matching its exact basename (e.g., a `main/` directory located at same level as `main.yaml`).
- **Complexity Trigger**: For small or "Single-Task" manifests, inline logic is permitted to avoid overhead. However, any manifest exceeding ~150 lines or involving more than 3 data sources MUST transition to the Mirrored Directory standard.

## 2. Directory Taxonomy (Keyword-Driven Organization)

When decomposition is triggered, components must be strictly categorized into subdirectories based on their logical keywords. Specifically:

- `input_fields/`: Defines raw incoming schemas.
- `wrangling/`: Defines all Transformation (`tier1`, `tier2`) operations for individual data sources.
- `output_fields/`: Defines the terminal contract schemas.
- `join/`: Defines the join recipe (`recipe:` key only) for joining multiple ingredients into a collection. One file per join block (e.g., `AMR_Profile_Joint.yaml`). Top-level manifest key: `join_manifests:`.
- `plots/`: Contains visualization specifications for `analysis_groups`. Each file contains a single `spec:` block.

## 3. Structural Authority Reference

The file `assets/template_manifests/1_test_data_ST22_dummy.yaml` serves as the official structural standard.

- Any adaptations made to the `1_test_data_ST22_dummy.yaml` template logic or subdirectory groupings MUST be immediately reflected back into this rulebook to remain the authoritative requirement for the entire system.

## 4. Documentation & Appendix Mandate

- **User Documentation Sync**: Any changes made to the structure of manifests MUST be immediately reflected in the appropriate library READMEs and user-facing `.qmd` documentation files.
- **Standalone Appendix Registry**: The YAML manifest structure must be physically maintained as a standalone reference file located at `docs/appendix/manifest_structure.yaml`. If any changes are implemented regarding how manifests are used, grouped, or structured, this appendix file must be updated to serve as the external user-facing source of truth.

## 5. Explicit Whitelisting (The Final Contract)
- **The Protocol**: The `final_contract` block in a pipeline or assembly manifest is an **Exclusive Whitelist**. 
- **The Effect**: Any column existing in the dataframe but not explicitly listed in the `final_contract` will be dropped by the Assembler projection guard. 
- **Developer Rule**: Always check the `final_contract` if a newly created column is missing from the output TSV/Parquet.

## 6. Biological Typing & Discrete Plotting
- **The Protocol**: To ensure Plotnine correctly renders discrete scales (e.g., for Year, Sequence Type), columns MUST be cast to appropriate types in the assembly recipe.
- **The Rule**: Numeric values used as categories (integer years) MUST be cast to `int` or `string` in the Tier 2 assembly to prevent continuous-scale stretching in visualizations.

---

## 7. Canonical Recipe Syntax (STRICT — No Shorthand)

**ALL** wrangling and assembly steps MUST use the canonical `action:` key format. Shorthand formats (using the action name as the YAML key, e.g., `- join: {...}`, `- mutate: [...]`, `- sort: [...]`) are **NOT supported by the engine** and are **silently skipped**, producing wrong results with no error.

### ✅ Canonical (ONLY valid format)

```yaml
recipe:
  - action: cast
    columns: [Year]
    dtype: String
  - action: mutate
    column: predicted_phenotype_clean
    expression: "pl.col('predicted_phenotype').str.strip_chars().str.to_lowercase()"
  - action: join
    right_ingredient: metadata_schema
    'on': sample_id
    how: inner
  - action: sort
    columns: [Year, Source, Country]
```

### ❌ Forbidden shorthand (silently broken)

```yaml
# ALL OF THESE ARE FORBIDDEN:
- mutate:
    - col: "expr"        # WRONG — engine never sees 'action' key
- join:
    dataset_id: foo      # WRONG — must be 'right_ingredient', not 'dataset_id'
    on: sample_id        # WRONG — 'on' is YAML boolean True, must be quoted 'on'
- sort:
    - Year               # WRONG — shorthand, no 'action' key
```

### Key-specific rules

| Recipe concept | Canonical key | FORBIDDEN alias |
|---|---|---|
| Join right-side dataset | `right_ingredient` | `dataset_id` |
| Join column (symmetric) | `'on'` (quoted!) | `on` (unquoted — YAML parses as boolean `True`) |
| Mutate (one column per step) | `column` + `expression` | List of `{col: expr}` pairs |
| Cast a column type | `action: cast`, `columns`, `dtype` | `action: mutate` with `pl.col().cast()` inline |

### YAML Boolean Trap

The key `on` is a **YAML reserved word** that is silently parsed as boolean `True`. **Always quote it**: `'on': sample_id`.

---

## 8. `analysis_groups` Structure (Manifest-Driven Home Theater)

The `analysis_groups` top-level key defines the groups and plots rendered in the Home Theater (Phase 21-B). **This is the ONLY way to render plots in the app.** The legacy flat `plots:` key at the manifest root is no longer used.

```yaml
analysis_groups:
  <group_id>:                         # Snake_case, no spaces
    label: "Human-readable group name"
    plots:
      <plot_id>:                      # Snake_case; unique across ALL manifests
        label: "Human-readable plot name"
        spec: !include <basename>/<subdir>/<plot_id>.yaml
```

**Rules:**
- `plot_id` must be snake_case (ASCII identifier — letters, digits, underscore) and **globally unique across all project manifests** (the app registers `@render.plot` by ID at startup).
- `group_id` (the dict key) is auto-sanitised to a Shiny-safe internal ID via `_safe_id()`. **Spaces, emoji, and punctuation are allowed** — they're stripped from the internal ID but preserved verbatim in the visible label. (Updates ADR-036: previously hardcoded sanitisation; now general regex sanitisation.)
- Each `spec: !include` points to a file in `plots/` subdirectory.
- The included plot file must contain a single `spec:` root key. `ConfigManager` auto-unnests it.

### Visible labels (icons & emoji are encouraged)

The visible tab/group label in the UI comes from this resolution chain:

1. `label:` field if set (recommended — explicit and concise)
2. `description:` field if set
3. The dict key (group_id / plot_id) as fallback

All three preserve any unicode, including emoji and CJK. Manifest authors can use any icons in `label:` to make the UI friendly. Example:

```yaml
analysis_groups:
  Cat 🐱:                              # Internal id auto-sanitised to "cat"
    label: "🐱 Cat"                    # ← Tab shows "🐱 Cat"
    description: The boss's favourites
    plots:
      miaou:                           # plot_id stays snake_case (unique-id contract)
        label: "Miaou 🐱"              # ← Tab shows "Miaou 🐱"
        spec: !include cat/miaou.yaml
```

Reserve `description:` for longer prose; use `label:` for short emoji-rich tab text.

### Plot spec file structure (`plots/<plot_id>.yaml`)

```yaml
spec:
  factory_id: bar_logic          # Registered factory: bar_logic, scatter_logic, heatmap_logic
  target_dataset: <join_id>  # Must match a join_manifests key
  x: <column>                    # Aesthetic mapping — column must exist in target_dataset
  y: <column>                    # Optional
  fill: <column>                 # Optional
  color: <column>                # Optional
  facet_by: <column>             # Optional — triggers facet_wrap(~<column>)
  theme: theme_light             # Optional — must be a registered theme component
  layers:                        # Optional but required for position, labels, guides
    - name: position_dodge       # For side-by-side bars
      params: {}
    - name: labs
      params:
        title: "Plot Title"
        fill: "Legend Label"
        x: "X Axis Label"
```

**`position` and `labels` as flat keys are NOT supported.** They must appear as named layers. See registered components in `libs/viz_factory/src/viz_factory/`.

### Registered `factory_id` values

| `factory_id` | Geom injected | Notes |
|---|---|---|
| `bar_logic` | `geom_bar` (no `y`) or `geom_col` (with `y`) | For `dodge`, add `position_dodge` layer |
| `scatter_logic` | `geom_point` | |
| `heatmap_logic` | `geom_tile` | Uses `fill` aesthetic |

---

## 9. Authorized Data Types for `input_fields` / `output_fields`

| Manifest type | Polars load type | Polars output contract | When to use |
|---|---|---|---|
| `categorical` | `pl.String` (internal) | `pl.Categorical` | **Default** for identifiers and repeating values (`sample_id`, `taxon`, `country`, `gene`). Ensures discrete-scale correctness in Plotnine. |
| `string` (or `utf8`) | `pl.String` | `pl.String` | High-cardinality text, descriptions, free-form fields where categorization gives no benefit. |

**Primary key rule:** `sample_id` MUST be `type: categorical`. Using `numeric` for join keys causes type-parity mismatches in `action: join` steps.
