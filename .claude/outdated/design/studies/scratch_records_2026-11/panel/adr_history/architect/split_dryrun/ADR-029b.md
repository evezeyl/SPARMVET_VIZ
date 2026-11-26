## ADR-029b: Dynamic Discovery & Interaction Logic

**Status:** PROPOSED (April 8, 2026)
**Decision:** Implement manifest-driven discovery and standardized interactivity.

- **Dynamic Tabs:** `VizViewer` MUST programmatically generate tabs by scanning plot IDs in the active YAML manifest. It must be possible to specify plot tittle and subtitle in The active YAML manifest (but optional).
- **Auto-Discovery:** UI MUST introspect the Polars schema to identify all columns; all columns (except Primary Keys) must be hideable via a picker and include top-level filter boxes.
- **Persistence:** Sidebars are open by default but must be collapsible to allow 100% theater width.

