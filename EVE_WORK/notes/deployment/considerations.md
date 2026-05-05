# Deployment considerations

## Core principle

The application should support multiple deployment targets **without modifying the codebase**.

Target rule:

- the codebase remains identical across deployment targets
- only configuration, packaging, and launch metadata should change

This should support:

- Posit Connect
- Galaxy
- rootless container deployment
- local Python installs on PCs
- Quarto documentation deployment
- future deployment targets if needed

---

## Multiple deployment targets

The deployment model should be **deployment-neutral**.

The same application code should be reusable across:

- **Posit Connect**
- **Galaxy**
- **rootless containers**
- **local Python installs**
- **Quarto documentation publishing**

Differences between targets should be handled through:

- deployment wrappers/adapters
- environment variables
- deployment-specific config
- packaging rules

Not through code edits in the main app.

---

## Deployment wrappers / adapters

A wrapper-based approach is preferred.

Suggested idea:

- one common application codebase
- one common config model
- one deployment wrapper per platform

Examples:

- `deploy/connect/`
- `deploy/galaxy/`
- `deploy/container/`
- `deploy/local/`
- `deploy/quarto/`

These wrappers should define:

- how the app is launched
- which config is selected
- what files are bundled
- any target-specific runtime metadata

This avoids modifying source code per deployment target.

---

## Configuration strategy

Configuration should be separated into two categories:

### 1. App behavior config
Defines application behavior such as:

- enabled modules
- UI mode/persona
- user-facing behavior
- feature flags
- access by mode

### 2. Deployment config
Defines target/runtime concerns such as:

- selected config path
- environment-specific settings
- deployment metadata
- runtime paths
- launch details

This separation will make multi-target deployment easier to maintain.

---

## Environment-variable driven selection

Behavior should be selected through environment variables rather than code changes.

Useful variables may include:

- `APP_CONFIG`
- `DEPLOY_TARGET`

Possibly more later if truly needed, but the goal should remain minimal.

Example idea:

- Posit Connect deployment sets `APP_CONFIG` to the relevant mode/config file
- Galaxy does the same with its own wrapper
- local install does the same via launcher script
- container deployment passes the same values at runtime

This keeps selection external to the codebase.

---

## Deployment bundle minimization

Only files required for a given deployment should be included in the deployment bundle.

Important note:

- `EVE_WORK` does **not** need to be included in deployments

Deployment packaging should deliberately exclude non-runtime material such as:

- notes
- planning material
- internal working documents
- other non-essential files

This should reduce bundle size and lower deployment complexity.

---

## Libraries and future git submodules

The libraries are already planned to work as independent repositories and later as **git submodules**.

Important requirement:

- imports must remain compatible with that future structure
- if import structure would break under submodule separation, it should be corrected

The codebase should continue to work whether libraries are:

- currently in-repo
- later split into independent repositories
- mounted as git submodules

This should be treated as a design constraint now.

---

## Quarto documentation deployment

Quarto documentation will need its **own deployment path**.

This should be treated as a first-class deployment target, not an afterthought.

Quarto deployment should likely have:

- its own wrapper
- its own packaging rules
- its own output/publish process
- clear separation from application deployment

This may eventually live under something like:

- `deploy/quarto/`

or equivalent deployment-specific structure.

---

## Deployment-sensitive and externally fetched assets

We need to trace all files and assets that are:

- fetched externally
- deployment-sensitive
- dependent on local machine assumptions
- not yet organized into a deployment-ready structure

These should be reviewed and moved or vendored locally as needed.

### Already identified as a concern

In `app/src/ui.py`, the UI currently references CDN-hosted assets:

- Bootstrap Icons CSS
- Cytoscape
- Dagre
- `cytoscape-dagre`

These should be traced and reorganized into a deployment-ready local structure where appropriate.

### Why this matters

This is especially important for:

- locked-down environments
- offline or restricted environments
- reproducible deployment bundles
- containerized deployment
- Connect deployment hardening

---

## Suggested structural direction

A better long-term structure should make it easy to identify:

- app code
- shared libraries
- deployment wrappers
- deployment configs
- local vendored assets
- documentation deployment material

The structure should support:

- reusable code
- selective packaging
- deployment-specific wrappers
- future submodule libraries
- Quarto documentation deployment

---

## Action list

1. Define a deployment-neutral directory strategy.
2. Separate app config from deployment config.
3. Add deployment wrappers/adapters per target.
4. Ensure config selection happens externally, not by editing code.
5. Exclude non-runtime content from deployment bundles, including `EVE_WORK`.
6. Prepare Quarto documentation as its own deployment target.
7. Trace all deployment-sensitive files and externally fetched assets.
8. Vendor or relocate required frontend assets into a local deployment-ready structure.
9. Validate that library import structure remains compatible with future git submodules.

---

## Immediate follow-up items

Priority items currently visible:

- review deployment bundle boundaries
- identify all non-runtime files to exclude
- trace frontend/CDN dependencies in `app/src/ui.py`
- define wrapper strategy for Connect, Galaxy, container, local, and Quarto
- confirm library layout remains submodule-safe