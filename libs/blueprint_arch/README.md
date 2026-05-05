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

## Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/blueprint_arch/tests/ -v
```
