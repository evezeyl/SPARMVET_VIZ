# GALLERY — Recipe Inspiration & Community Browser

**Type:** User space  
**Status:** Partial build (`gallery_viewer.py` exists; community/contribution features not yet built)  
**Last updated:** 2026-05-05

---

## Purpose

GALLERY is a browsable collection of plot recipes. It serves two roles:

1. **Inspiration**: the user can browse existing recipes, see rendered previews, and understand what kind of visualisations are possible — before committing to building a manifest.
2. **Community**: users can contribute recipes they have developed, request recipes based on articles or needs, and discover what others have shared.

GALLERY is read-only from the analysis perspective — it does not run analyses or modify data. It feeds HOME (indirectly, via manifests) and BLUEPRINT (as inspiration for manifest nodes).

---

## User Functionalities

### Browsing

| Functionality | What the user can do |
|---|---|
| **Browse recipes** | Scroll/filter the gallery of available plot recipes |
| **Search** | Search by name, tag, plot type, data type, or keyword |
| **Preview** | See a rendered example plot for a recipe (using bundled sample data) |
| **Inspect recipe** | View the recipe's description, required columns, dependencies, and the raw manifest YAML |
| **Copy recipe YAML** | Copy the manifest snippet to use as a starting point in BLUEPRINT |

### Community / Contribution

| Functionality | What the user can do |
|---|---|
| **Request a recipe** | Submit a request (e.g. "I saw this plot type in paper X, can someone add a recipe?") — opens a pre-filled GitHub issue |
| **Contribute a recipe** | Submit a new recipe — guided form that creates a pull request to the community gallery repo |
| **Browse contributions** | See pending / recently merged community recipes |

---

## Non-Goals

- GALLERY does not run the analysis — that is HOME.
- GALLERY does not build or edit manifests — that is BLUEPRINT.
- GALLERY does not send recipes directly to T3 or pre-fill HOME sessions (the gallery→T3 transplant feature was removed; the replacement approach is: copy YAML → open in BLUEPRINT).
- GALLERY does not store user data.

---

## Key Design Constraints

- **Read-only data path**: GALLERY never modifies session state or manifests. It only provides YAML to copy.
- **Local-first**: the bundled gallery (shipped with the app) works fully offline. Community features (search GitHub, submit issues/PRs) require network access and are gracefully degraded when unavailable.
- **Positive inclusion** (ADR-071): GALLERY panel is only mounted when `gallery_enabled` is true in persona config.
- **Gallery→BLUEPRINT is the handoff path**: the integration point between GALLERY and BLUEPRINT is YAML copy-paste (or a future "open in BLUEPRINT" button). No direct state coupling between the two spaces.

---

## Code Modules

| Code module | Role |
|---|---|
| `gallery_viewer.py` | Browse UI, recipe list, preview rendering |
| `gallery_handlers.py` | Server-side handlers: recipe loading, index, clone |

---

## Current State

- Recipe browsing and preview: built and working.
- Search: not yet built.
- Community contribution / request workflow: not yet built (requires GitHub integration).
- "Open in BLUEPRINT" button: not yet built.
- Gallery→T3 transplant: removed (dead code cleaned up 2026-05-05).

---

## Open Questions

- **Search scope**: local full-text search (fast, offline) vs. GitHub API search (broader, requires network). Start with local; add GitHub later.
- **Contribution workflow**: full PR via GitHub API (complex) vs. "copy this YAML template and open an issue with it" (simple, manual merge). Start simple.
- **Gallery index format**: current `gallery_index.json` registry — sufficient for local browsing; will need tags and search fields added.
- **Sample data for previews**: each recipe needs bundled sample data to render a preview. How is this managed? Stored per-recipe in the gallery dir, or a shared synthetic sample dataset?
- **"Open in BLUEPRINT" handoff**: should clicking "open in BLUEPRINT" pre-populate a new manifest in BLUEPRINT, or just copy the YAML to clipboard? The former is cleaner UX but requires BLUEPRINT to be enabled and accept an inbound manifest.
