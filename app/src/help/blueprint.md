## Blueprint Architect — Quick Reference

**Blueprint Architect** lets you inspect, edit, and design data analysis recipes through a visual interface.

### TubeMap
The DAG at the top shows your data analysis recipe's data lineage — from raw schemas through joins and assembly to plots. Click any node to load its configuration in the right sidebar.

### Lineage Rail
The breadcrumb strip below the TubeMap shows the path from the selected node back to its data source.

### Right Sidebar — Blueprint Surgeon
When a **transformation node** is selected, the Surgeon panel shows the node's wrangling steps. Use the action/component picker (searchable, filtered by position) to add or edit steps. Apply propagates the schema to downstream nodes.

### Joint Designer
A dedicated pane for authoring `join` steps: pick left and right ingredient schemas side-by-side, choose the key column(s), and see a live key-match preview computed from real data. Apply is audit-gated (requires a justification) and emits a canonical `join` step.

### Right Sidebar — Plot Defaults
When the **data analysis recipe root** is selected (no sub-node active), the Plot Defaults form lets you set style defaults for all plots in this data analysis recipe:
- **Palette** — named color palette (deployment or matplotlib)
- **Theme** — plotnine theme (theme_light, theme_bw, etc.)
- **Default font family** — axis/label font
- **Facet panel spacing** — space between facet panels (0–1)
- **Legend position** — right / top / bottom / left / none

Changes apply immediately in-session (not saved to YAML — edit the YAML directly, or use the escape hatch, to persist).

### Branching
Branch a data schema, assembly, join, or plot node to split its lineage: upstream stays shared, the new branch diverges downstream. Give the new branch an ID, **Preview branch** to see what will be written, then **Create branch**.

### Undo
Every applied change is pushed onto a session undo stack — use it to step back through recent edits.

### YAML Escape Hatch
The YAML panel shows the raw data analysis recipe fragment for the selected node. It is read-only unless the app features enables `data_analysis_recipe_edit_enabled` (developer/qa) — there it becomes editable, and a save stages a `developer_raw_yaml` T3 node.

### AI Agent
A conversational helper panel in the right sidebar (when the app features enables `blueprint_agent_enabled` and a backend is configured) — ask it about the active data analysis recipe or request changes.

### Validate
**Run validation** checks the data analysis recipe's coherence (schema/join/plot consistency) and reports PASS/FAIL per check — a static check, no data is materialized.

### Groups & Plots
Use the groups inventory panel to create analysis groups, add plots to a group, or move a plot between groups.

### Import / Save / New
**Import** loads a data analysis recipe YAML from disk (also via clicking a TubeMap node). **Save** writes the current component back to its file. **New** creates a new data analysis recipe from scratch.
