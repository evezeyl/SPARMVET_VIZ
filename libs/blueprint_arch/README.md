# Blueprint Architect Library (blueprint_arch)

**Authority:** ADR-045, ADR-067

Pure-Python manifest introspection and TubeMap rendering. Zero Shiny imports — fully headless-safe and importable by debug scripts, test suites, and CLI tools without side effects.

## Purpose

Provides the structural intelligence for the Blueprint Architect user space: parsing manifest lineages, building the dependency graph (TubeMap), and computing the Lineage Rail for the UI. Separated from `app/` under ADR-067 so this logic can be tested and invoked independently of the Shiny runtime.

## Key Components

- **ManifestNavigator (manifest_navigator.py)**: Pure manifest introspection engine. Builds sibling maps, schema registries, lineage chains, and resolves `input_fields`/`output_fields` contracts. The sole source of structural truth for manifest topology.
- **BlueprintMapper (blueprint_mapper.py)**: Generates Cytoscape.js graph elements (nodes + edges) for the TubeMap visualisation. Maps manifest roles to colour-coded visual tiers (trunk, branch, ref, plot, etc.).

## Public API

```python
from blueprint_arch.manifest_navigator import (
    build_sibling_map,         # rel_path → {role, schema_id, siblings, ingredients}
    build_schema_registry,     # schema_id → {schema_type, input_fields, wrangling, ...}
    build_lineage_chain,       # ordered [{rel, schema_id, role, label, is_active}]
    load_fields_file,          # ADR-041 Rich Dict with ADR-014 unnesting
    resolve_fields_for_schema, # recursive, cycle-guarded
)
from blueprint_arch.blueprint_mapper import BlueprintMapper

mapper = BlueprintMapper()
cy_elements = mapper.generate_cy_elements(sibling_map, component_ctx_map)
```

## Design Constraints

- **Zero Shiny imports** — Two-Category Law (ADR-045). Any file in this lib is safe to import from headless contexts.
- **No `sys.path` hacks** — must be installed editable (`pip install -e libs/blueprint_arch`).
- **Read-only** — this lib reads manifests, it never writes them. Writing belongs in `app/handlers/blueprint_handlers.py`.

## Installation

```bash
pip install -e libs/blueprint_arch
```

## Schema Registry (ADR-075)

`schema_registry.py` is the headless-safe catalog that surfaces the `ui_schema` dicts registered in `transformer` and `viz_factory` to the Blueprint Architect IDE. It uses deferred imports to avoid pulling Shiny or domain-library side effects into headless contexts.

### Public API

```python
from blueprint_arch.schema_registry import (
    get_action_catalog,           # -> dict[str, dict]  all annotated transformer actions
    get_component_catalog,        # -> dict[str, dict]  all annotated viz_factory components
    get_combined_catalog,         # -> {"actions": ..., "components": ...}
    get_actions_for_context,      # (context: str) -> dict  filter by "t1" | "t2" | "assembly"
    get_actions_by_category,      # (category: str) -> dict  filter by "cleaning" | "derivation" | ...
    get_components_for_context,   # (context: str) -> dict  filter by "plot"
    search_actions,               # (query: str) -> dict  case-insensitive search on name + tags
)
```

### Usage example

```python
import transformer.actions   # populates ACTION_SCHEMAS
import viz_factory            # populates COMPONENT_SCHEMAS

from blueprint_arch.schema_registry import (
    get_actions_for_context,
    get_component_catalog,
    search_actions,
)

# All actions valid in a Tier-1 wrangling block
t1_actions = get_actions_for_context("t1")

# Search for null-handling actions by tag
null_actions = search_actions("null")   # returns fill_nulls, drop_nulls

# All annotated plot components
plot_components = get_component_catalog()
```

### Schema entry shape

Every entry in the catalog follows the same structure regardless of whether it came from `@register_action` or `@register_plot_component`:

| Field | Required | Description |
|---|---|---|
| `label` | Yes | Human-readable name shown in the IDE picker |
| `category` | Yes | Semantic grouping (e.g. `cleaning`, `derivation`, `distribution`) |
| `context` | Yes | List of valid positions: `t1`, `t2`, `assembly` (actions) or `plot` (components) |
| `tags` | Yes | Free-text search keywords |
| `params` | Yes | Dict of param definitions — see param schema below |
| `wraps` | Components only | Link to the underlying plotnine function (`lib`, `attr_path`) |
| `allow_extra_params` | Components only | Must be `True` — passes unknown kwargs through to plotnine |

Each entry in `params` is a dict:

| Field | Required | Description |
|---|---|---|
| `widget` | Yes | Widget type (see vocabulary below) |
| `label` | Yes | Human-readable param label |
| `required` | Yes | `true` / `false` |
| `options` | `enum` / `dtype_picker` | List of allowed values |
| `multi` | `column_selector` | `true` allows multi-column selection |
| `default` | No | Default value pre-filled in the form |

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

### Registration is triggered by importing the source library

`schema_registry.py` uses deferred imports: the catalogs are empty until you import the libraries that register entries. Always import before calling catalog functions:

```python
import transformer.actions   # triggers all @register_action decorators → populates ACTION_SCHEMAS
import viz_factory            # triggers all @register_plot_component decorators → populates COMPONENT_SCHEMAS
```

In test files, place these imports at module level so all test functions see a populated catalog.

## Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/blueprint_arch/tests/ -v
```

`libs/blueprint_arch/tests/test_schema_registry.py` verifies:
- Both catalogs load and are non-empty when transformer and viz_factory are installed
- All 19 annotated transformer actions and 7 annotated viz_factory components are present
- Every schema entry has required structural fields (`label`, `category`, `context`, `params`)
- Every param entry has required fields (`widget`, `label`, `required`)
- Widget types are from the declared vocabulary; context tags are from the declared vocabulary
- Filtering (`get_actions_for_context`, `get_actions_by_category`) and search functions return correct subsets
