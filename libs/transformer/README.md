# Transformer Library

## Purpose

The central engine for data wrangling and Phase 4 relational assembly. It enforces the data contracts (data analysis recipe format 1) by cleaning raw data and joining disparate sources into a single, tidy Polars DataFrame ready for visualization.

## Documentation
>
> [!IMPORTANT]
> This README is a high-level summary. For exhaustive deep-dives, architectural ADRs, and the full gallery of actions, you MUST refer to the official [Transformer Dev-to-User Guide](../../docs/workflows/wrangling.qmd).

## Key Components

- `DataWrangler (data_wrangler.py)`: Core engine that executes atomic cleaning actions against single datasets using declarative YAML pipelines.
- `DataAssembler (data_assembler.py)`: Relational join orchestrator. Implements **Strict Assembly Enforcement**: requires all ingredients explicitly defined in a step list, otherwise triggers a controlled crash to protect data integrity.
- `ActionRegistry (registry.py)`: Central dictionary mapping YAML action keys to Python function logic.
- `test_action_recipe_pairs.py` - [Test]: every registered action has its 1:1:1 pair (recipe and data file in `tests/data/`); the pair runs through ingestion and the wrangler and equals the direct Polars call.
- `debug_wrangler.py` - [Dev Tool]: CLI runner that wrangles one format 1 recipe and writes the result as a TSV (`@verify` evidence). Entry: `main()`.
- `debug_assembler.py` - [Dev Tool]: CLI runner for multi-source assembly (the join's last tier-1 step publishes the columns). Entry: `run_assembler_debug()`.
- **Actions (`actions/`)**: `polars_calls.py` holds the `polars_<name>` actions (exactly the Polars call), `polars_aggregations.py` the twelve whole-table aggregations (`polars_sum` ... `polars_last`), `modified.py` the `modif_<name>` actions (today `modif_filter`), `composite.py` the `step_<name>` actions (today `step_top_n_other`), `polars_rows.py` the ten row actions (pick, cut, number, reverse or remove rows: `polars_head` ... `polars_remove`), `polars_time_joins.py` rank, time windows and special joins (`polars_rank`, `polars_join_asof`, `modif_join_where`, `polars_group_by_dynamic`, `polars_rolling`; each states what order or sorted key it needs and refuses a table that does not meet it), `base.py` the `register_action` decorator and the form schemas (`ACTION_SCHEMAS`).
- `Anchor (anchor.py)`: Tier 1 and Tier 2 disk anchors, written and read by the engine and never named in a data analysis recipe.
- **Reactive State (Tier 3)**: Transient views generated via Predicate Pushdown. Audit steps are added with "Add to audit pipeline" (a reason is required), allowing for side-by-side inspection in **Comparison Mode** (T2 reference vs T3 active).
- **Path Authority**: Persistence locations (Tiers 1-3) are determined by `config/connectors`, decoupling hardware from the UI.

## Data analysis recipe Syntax (Tiered Mandate)

Following **ADR-024**, every table and every join in a data analysis recipe MUST write its tiers as keys of its own. This formalizes the separation between generic data cleaning and plot-specific preparation. A tier is the key (`tier1`), then the optional `data_engine` (first key), then `steps` with the list; there is no `wrangling` key (removed 2026-11-17).

```yaml
tier1: # THE TRUNK: Tidy, Clean, Wide Data (Shared foundation)
  data_engine: python-polars   # optional; without it the data analysis recipe's data_engine applies
  steps:
    - action: polars_rename
      mapping: { Sample_ID: sample_id }
    - action: polars_str_strip_chars
      columns: [gene_slug]

tier2: # THE BRANCH: Plot-Ready, Long Data (Optional; only on a schema plotted directly)
  steps:
    - action: polars_unpivot
      index: [sample_id, country]
      'on': [n50, total_length]
      variable_name: metric
```

**The engine.** The library is the data engine `python-polars`. Every registered action carries the field `engine` (set by the decorator, default `python-polars`; an engine the app has no library for is refused at registration), and `engine_python_polars.py` names the engine and exposes `ENTRY` (`DataEngineEntry`: the wrangler and the assembler). `app/modules/engine_registry.py` joins the entry files; the orchestrator chooses the entry by the tier's `data_engine`, else the data analysis recipe's. `DataWrangler.tier_steps(body, "tier1")` reads the written shape of a tier and refuses an older one (`wrangling`, a list) with a message.

Joins are written in the `joins` block, where `tier1` (and `tier2`) are written the same way:

```yaml
joins:
  Combined:
    ui_label: Combined table
    ingredients: [{dataset_id: Anchor}, {dataset_id: metadata}]
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata
          'on': [sample_id]
          how: left
          maintain_order: left_right
        - action: polars_select      # publishes the columns, in this order
          exprs: [sample_id, gene_slug, country]
```

### Data analysis recipe Safeguards (ADR-012b)

- **The Boolean Shield**: To prevent the YAML parser from misinterpreting `on:` as `True`, always write `'on':` with quotes; the data analysis recipe checker refuses an unquoted `on`.
- **Relational Strategy**: When joining multiple 'Long' format datasets (e.g., AMR + Virulence), prefer a semi or anti `polars_join` (`how: semi` / `how: anti`) or a tier-2 aggregation to keep the row count manageable. A non-key column carried by both tables of a join is refused (Polars would silently rename one).
- **Flat-list rejection (LEGACY-FLAT-WRANGLING-1, Phase 34, 2026-05-22):** A tier written as a list (e.g. `tier1: [{action: ...}]`) and the old container `wrangling:` are refused by the data analysis recipe checker (and by `DataWrangler.tier_steps()` with a `DataAnalysisRecipeError`; before 2026-11-17 `_resolve_tier()`). Migrate to the tiered structure above.

### Identity Logic (ADR-014)

- **Automatic Fallback**: If the `tier2` block is omitted or left empty, the system automatically uses the Tier 1 output for visualization.
- **Recommendation**: Only utilize Tier 2 when the plot requires data transformations (e.g., pivoting to long format or aggregation) that differ from the tidy Tier 1 table.

## Short-Circuit & Freshness Guard (ADR-024 Refinement)

To maximize performance when iterating on complex pipelines, the `DataAssembler (data_assembler.py)` implements a **Short-Circuit Execution** pattern backed by **Decision Metadata Hashing**.

- **The Logic**: The orchestrator (`app/modules/orchestrator.py`) compares the key stored in the Parquet file's metadata (`sparmvet_tier1_key`, `sparmvet_tier2_key`) with the current key of that same table, before any ingestion. Each stored table has its own key (ADR-089, ADR-101).
- **Automated Freshness Check**: The key of a table is a series of labelled parts: the engine (the engine version, cache version 6, and the data engine of the table and of what it builds on), the definition of the table and of what it reads from the recipe graph, the content of the data files it reads, then the tier-2 steps for Tier 2. A plot with its own tier-3 steps adds one more part. The plot engine is in no table key (D-0240). If it matches, joins and wrangling are skipped. If it differs, the stage is recomputed. A Tier 2 change recomputes only Tier 2. The file is written with Polars, the key inside the file metadata.

## I/O Summary

- **Input**: Raw `pl.LazyFrame`s from the Ingestion layer, and YAML Data Analysis Recipe `spec` dictionaries.
- **Output**: Cleaned and joined `pl.LazyFrame`s whose columns are the ones published by the last tier-1 step of each join.

## Local CLI Runners

For Phase 1 & Phase 4 verification, use the local debugging runners to execute declarative YAML data analysis recipes and verify output TSVs.

**Full Suite Verification (The Automated Gate):**

```bash
PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests -q
```

**Atomic Wrangling (Isolated Action):**

```bash
./.venv/bin/python libs/transformer/tests/debug_wrangler.py --data [INPUT] --data-analysis-recipe [YAML] --output [OUT_TSV]
```

**Relational Assembly (Multi-Source Job):**

```bash
./.venv/bin/python libs/transformer/tests/debug_assembler.py --data-analysis-recipe [YAML] --tmp [OUT_DIR]
```

`debug_assembler.py` uses **detection-based data analysis recipe loading**: if the data analysis recipe text contains `!include`, it routes through `ConfigManager` (which resolves YAML include directives); otherwise it uses `yaml.safe_load` directly. This means both full pipeline data analysis recipes and standalone test data analysis recipes work without any flag.

## Registered Action Registry

All 68 actions available for use in data analysis recipe `wrangling` and `steps` blocks, read from `ACTION_SCHEMAS` on 2026-11-15 (the prefix says what an action is: `polars_` exactly Polars, `modif_` a documented change, `step_` several calls). A description and a YAML example of each are in the [Action Gallery](../../docs/appendix/transformer_actions.qmd).

| Category | Actions |
|---|---|
| **Aggregation** | `polars_group_by_dynamic`, `polars_rolling`, `polars_count`, `polars_first`, `polars_group_by`, `polars_last`, `polars_max`, `polars_mean`, `polars_median`, `polars_min`, `polars_null_count`, `polars_quantile`, `polars_std`, `polars_sum`, `polars_var`, `step_top_n_other` |
| **Analytical** | `polars_rank`, `polars_all_horizontal`, `polars_any_horizontal`, `polars_cum_count`, `polars_cum_sum`, `polars_describe`, `polars_max_horizontal`, `polars_mean_horizontal`, `polars_min_horizontal`, `polars_shift`, `polars_sum_horizontal` |
| **Cleaning** | `polars_coalesce`, `polars_drop_nans`, `polars_drop_nulls`, `polars_fill_nan`, `polars_fill_null`, `polars_interpolate`, `polars_unique` |
| **Derivation** | `polars_with_columns` |
| **Filtering** | `modif_filter`, `polars_sample` |
| **List** | `polars_list_join`, `polars_list_slice` |
| **Numeric** | `polars_round` |
| **Ordering** | `polars_sort` |
| **Relational** | `polars_join`, `polars_join_asof`, `modif_join_where` |
| **Renaming** | `polars_rename` |
| **Reshaping** | `polars_explode`, `polars_pivot`, `polars_str_split`, `polars_str_splitn`, `polars_unnest`, `polars_unpivot` |
| **Rows** | `polars_bottom_k`, `polars_gather_every`, `polars_head`, `polars_limit`, `polars_remove`, `polars_reverse`, `polars_slice`, `polars_tail`, `polars_top_k`, `polars_with_row_index` |
| **Selection** | `polars_drop`, `polars_select` |
| **String** | `polars_str_extract`, `polars_str_replace_all`, `polars_str_strip_chars` |
| **Temporal** | `polars_dt_truncate` |
| **Typing** | `polars_cast` |

`sink_parquet` and `scan_parquet` are engine functions, not data analysis recipe actions.

---|---|
| **Cleaning** | `fill_nulls`, `drop_nulls`, `replace_values`, `rename`, `drop_duplicates`, `unique_rows`, `recode_values`, `sanitize_column_names`, `keep_columns`, `drop_columns`, `strip_whitespace`, `round_numeric`, `filter_range`, `add_constant`, `filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `rename_columns`, `unique` |
| **Expressions** | `regex_extract`, `cast`, `coalesce`, `label_if`, `mutate`, `regex_replace`, `null_if` |
| **Analytical** | `polars_rank`, `top_n_other`, `window_agg`, `shift`, `fill_nulls_direction`, `sort`, `sample`, `cum_sum`, `cum_count`, `date_extract`, `date_truncate`, `list_slice`, `list_join`, `is_in`, `not_in`, `z_score`, `percentile`, `value_counts`, `describe_stats`, `select_by_pattern`, `horizontal_stats`, `any_horizontal`, `all_horizontal`, `interpolate` |
| **Advanced** | `split_and_explode`, `derive_categories`, `split_column_to_parts`, `divide_columns`, `split_column` |
| **Reshaping** | `unpivot`, `explode`, `unnest`, `split_to_list`, `to_struct`, `pivot` |
| **Performance** | `summarize`, `count_by_group` |
| **Relational** | `join`, `join_filter` |
| **Persistence** (engine-internal — do not write manually) | `sink_parquet`, `scan_parquet` |

---

## Action UI Schema (ADR-075)

Every action that should be visible in the **Blueprint Architect IDE** must declare a `ui_schema` dict in its `@register_action(...)` decorator. The schema drives automatic form generation — no hand-coded forms required.

### Adding a schema to a new action

```python
from transformer.actions.base import register_action

@register_action("my_action", ui_schema={
    "label": "Human-readable label",          # shown in action picker
    "category": "cleaning",                    # groups actions in the picker
    "context": ["t1", "t2"],                   # which tiers allow this action
    "tags": ["null", "cleaning"],              # free-text search terms
    "params": {
        "columns": {
            "widget": "column_selector",       # widget type (see vocabulary below)
            "multi": True,
            "label": "Columns",
            "required": True,
        },
        "value": {
            "widget": "column_or_literal",
            "label": "Fill value",
            "required": True,
        },
    },
})
def action_my_action(lf, spec):
    ...
```

### Widget type vocabulary

| Widget | UI element | Use for |
|---|---|---|
| `column_selector` | Multi/single select from frame schema | Column names |
| `expression` | Code editor with Polars syntax highlighting | Polars expressions |
| `enum` | Dropdown from fixed list (`options: [...]`) | Categorical choices |
| `dtype_picker` | Dropdown of Polars dtype strings | `cast` dtype |
| `number` | Numeric input (int or float) | Counts, thresholds |
| `string` | Plain text input | New column names, patterns |
| `color` | Colour picker (hex or named) | Fill / colour overrides |
| `column_or_literal` | Column select OR literal value | Fill values, join keys |
| `bool` | Checkbox | Flags, on/off options |
| `list` | A YAML list typed as one line, `[a, b]`; `items: mapping` when each item is a mapping | Values to replace, new column names, recode rules |
| `mapping` | A YAML mapping typed as one line, `{old: new}` | Rename mapping |

### Context tags

| Tag | Tier | Usage |
|---|---|---|
| `t1` | Tier 1 wrangling | Cleaning, renaming, filtering |
| `t2` | Tier 2 wrangling | Reshaping, aggregation |
| `assembly` | Assembly steps | Joins, cross-source derivation |

### Accessing the catalog programmatically

```python
from blueprint_arch.schema_registry import (
    get_action_catalog,
    get_actions_for_context,
    get_actions_by_category,
    search_actions,
)

# All annotated actions
catalog = get_action_catalog()

# Filter to t1-valid actions
t1_actions = get_actions_for_context("t1")

# Search by keyword
matches = search_actions("regex")
```

### Tests

Schema registration is covered by:
- `libs/transformer/tests/test_ui_schemas.py` — structure, param alignment, semantic rules (440 tests total across all three schema test files)

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/transformer/tests/test_ui_schemas.py -v
```

## Installation (Editable Mode)

According to the workspace standard, this library must be installed locally via:

```bash
pip install -e ./libs/transformer
```
