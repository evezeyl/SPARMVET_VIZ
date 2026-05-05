---
description: Unified Workflow for Viz Factory Layer Implementation (Artist Pillar)
---

# 🎨 Viz Factory Implementation Workflow

This workflow defines the mandatory process for implementing new plotting components (geoms, scales, themes, etc.) in the **Artist Pillar**, ensuring adherence to the **Artist Law** and **Violet Law**.

## 1. Specification & Contract

- **Source Material**: Search `EVE_WORK/reference/plotnine_api_context.md` for the component signature and available parameters.
- **Contract Definition**: Define the `mapping` and `params` dictionary schema for the manifest.

## 2. Implementation Phase

- **Logic**: Implement and register the component in the appropriate `libs/viz_factory/src/` subdirectory (e.g., `geoms/core.py`).
- **Registration**: Use the `@register_plot_component("name")` decorator.
- **Imports**: Ensure all necessary Plotnine classes are imported in the target file.

## 3. The Artist Law Triplet (Evidence Loop)

No component is complete without an automated triplet test in `libs/viz_factory/tests/test_data/`:

1. **Data (`{component}_test.tsv`)**: Create a minimal TSV file with synthetic data suited for the component.
2. **Manifest (`{component}_test.yaml`)**: Define a manifest that MUST strictly follow the standards dictated in `[rules_manifest_structure.md](../rules/rules_manifest_structure.md)` and that additionally:
    - Points to the TSV via a `data_path` key.
    - Defines the aesthetic `mapping`.
    - Includes the new component in the `layers` list.
3. **Artifact Generation**: Run the **Unified Test Runner** from the project root:

    ```bash
    ./.venv/bin/python libs/viz_factory/tests/debug_runner.py libs/viz_factory/tests/test_data/{component}_test.yaml
    ```

4. **Verification**: Confirm the high-resolution plot is materialized at `tmp/viz_factory/USER_debug_{component}.png`.

## 4. Documentation & Task Closure

- **README Update**: Add the component to the "Key Components" list in `libs/viz_factory/README.md`.
- **User Documentation**: Append the component and its usage example (using `{{< include ... >}}`) to `docs/workflows/visualisation_factory.qmd`.
- **Task Closure**: Mark the component as completed in `.claude/tasks/tasks.md`.

## 5. Summary Presentation

- Present the generated PNG to the user.
- Provide the final documentation diff for verification.
- HALT: Only continue with next component after @verify
