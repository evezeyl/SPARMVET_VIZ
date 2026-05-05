# Vendor Manifest
**Last updated:** 2026-05-05
**Rule:** ADR-071 — all frontend assets must be vendored locally. No CDN links anywhere in the codebase.

When adding a new asset: download at a pinned version, place here, update this file.
When upgrading: re-download, update version and date below, test app.

| File | Version | Downloaded from | Licence | Date vendored |
|---|---|---|---|---|
| `cytoscape.min.js` | 3.29.2 | https://cdn.jsdelivr.net/npm/cytoscape@3.29.2/dist/cytoscape.min.js | MIT | 2026-05-05 |
| `dagre.min.js` | 0.8.5 | https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js | MIT | 2026-05-05 |
| `cytoscape-dagre.js` | 2.5.0 | https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.5.0/cytoscape-dagre.js | MIT | 2026-05-05 |
| `bootstrap-icons.css` + `fonts/` | 1.11.1 | https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/ | MIT | 2026-05-05 |
