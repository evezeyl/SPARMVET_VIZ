## Blueprint Architect — Quick Reference

**Blueprint Architect** lets you inspect, edit, and design pipeline manifests through a visual interface.

### TubeMap
The DAG at the top shows your manifest's data lineage — from raw schemas through joins and assembly to plots. Click any node to load its configuration in the right sidebar.

### Lineage Rail
The breadcrumb strip below the TubeMap shows the path from the selected node back to its data source.

### Right Sidebar — Blueprint Surgeon
When a **transformation node** is selected, the Surgeon panel shows the node's wrangling steps. Use the action picker to add or edit steps.

### Right Sidebar — Plot Defaults
When the **manifest root** is selected (no sub-node active), the Plot Defaults form lets you set global style defaults for all plots in this manifest:
- **Palette** — named color palette (project or matplotlib)
- **Theme** — plotnine theme (theme_light, theme_bw, etc.)
- **Font family** — default axis/label font
- **Facet spacing** — space between facet panels (0–1)
- **Legend position** — right / top / bottom / left / none

Changes apply immediately in-session (not saved to YAML — use the YAML escape hatch to persist).

### YAML Escape Hatch
The YAML panel shows the raw manifest fragment for the selected node. In developer persona it is editable — changes are staged as a T3 `developer_raw_yaml` node.

### Import / Save
**Import** loads a manifest YAML from disk. **Save** writes the current manifest back to disk (requires appropriate permissions).
