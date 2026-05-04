# Posit Connect deployment notes

## Summary

The app looks deployable to Posit Connect as a **Shiny for Python** application, assuming the Connect server supports Python content and can create the required runtime environment.

## Key points

- The app architecture appears compatible with Posit Connect.
- Using a **configuration JSON selected at deployment time** is an acceptable pattern.
- Internal libraries under `libs/` can be bundled with the app, as long as imports resolve correctly in the deployed environment.
- Posit Connect should typically manage its own isolated Python environment rather than reusing the local `.venv`.

## Python environment

- Do not plan on copying the local `.venv` directly to the server.
- Instead, ensure Python dependencies are declared cleanly so the server can build an isolated environment.
- The current project structure should be workable if dependencies are reproducible.

## Config files

- Deployment-time selection of a config JSON is reasonable.
- The important requirement is that the selected config is available to the deployed app and loaded from a predictable path.
- This pattern can be used to control UI behavior and access rules.

## Internal libraries

- The app’s internal libraries in `libs/` should be included in the deployment bundle.
- If they are already imported normally as `libs` and package structure is valid, this should be fine.
- Reorganization into submodules is possible if needed, but may not be necessary.

## Frontend assets

### Local CSS

The app’s core styling appears to be local:

- `config/ui/theme.css`
- optional persona CSS loaded from disk

These are injected directly into the page and do not depend on an external fetch.

### External CDN assets currently used

`app/src/ui.py` currently loads external assets from CDNs for:

- Bootstrap Icons CSS
- Cytoscape
- Dagre
- `cytoscape-dagre`

## Locked-down environment risk

If the deployment environment blocks outbound access, these CDN-hosted assets may fail to load.

That would mainly affect:

- icons, if they are still used
- Cytoscape graph rendering and related JS behavior

## Recommended mitigation

To make deployment robust in a locked-down environment:

- vendor the JS/CSS assets locally
- serve them from the app bundle instead of loading them from CDNs
- remove Bootstrap Icons entirely if they are not needed

Priority for local bundling:

1. Cytoscape
2. Dagre
3. `cytoscape-dagre`
4. Bootstrap Icons only if still required

## Overall assessment

This looks like a **manageable deployment-hardening task**, not a major rewrite.

Most likely work items:

- vendor external frontend assets locally
- confirm app entry point for Connect
- ensure `libs/` is bundled correctly
- ensure deployment config JSON is selected and available
- test startup in a clean environment without relying on the local `.venv`
- test with restricted internet access if possible.