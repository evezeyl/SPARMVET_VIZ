# GALLERY — Example Inspiration & Community Browser

**Type:** User space  
**Status:** Partial build (`gallery_viewer.py` exists; community/contribution features not yet built)  
**Last updated:** 2026-11-08

> **History (kept for context, not current):** this page went through two corrections before
> landing on today's design. It originally said the Gallery→T3 transplant was "removed, replaced
> by copy-YAML→BLUEPRINT" — checked 2026-11-07 (`uml_findings.md` F-22) and found backwards: the
> transplant (`handle_gallery_clone`, "Clone to Sandbox") was alive and working, and a
> BLUEPRINT handoff had never been built. That fact-check was correct, but Eve then clarified
> (2026-11-08, F-23, `ADR-093`) that the transplant itself was wrong regardless: T3 is audited
> modifications a HOME user makes to their own running analysis, never a place to import recipe
> content from anywhere — Gallery included. **The transplant is now removed** (ADR-093), and no
> Gallery→BLUEPRINT handoff was built to replace it — GALLERY has no interactive handoff into any
> other space at all. The sections below describe that final state.

---

## Purpose

GALLERY is a browsable collection of plot examples. It serves two roles:

1. **Inspiration**: the user can browse existing examples, see rendered previews, and understand what kind of visualisations are possible — before committing to building a data analysis recipe.
2. **Community**: users can contribute examples they have developed, request examples based on articles or needs, and discover what others have shared.

GALLERY is read-only from the analysis perspective — it does not run analyses or modify data, and has no interactive handoff into HOME or BLUEPRINT. It feeds both only indirectly, as inspiration: a user who wants to reuse a recipe fragment copies the YAML by hand into a text file or into BLUEPRINT (ADR-093).

---

## User Functionalities

### Browsing

| Functionality | What the user can do |
|---|---|
| **Browse examples** | Scroll/filter the gallery of available plot examples |
| **Search** | Search by name, tag, plot type, data type, or keyword |
| **Preview** | See a rendered example plot for an example (using bundled sample data) |
| **Inspect example** | View the example's description, required columns, dependencies, and the raw data analysis recipe YAML |
| **Copy example YAML** | Copy the data analysis recipe snippet to use as a starting point in BLUEPRINT |

### Community / Contribution

| Functionality | What the user can do |
|---|---|
| **Request an example** | Submit a request (e.g. "I saw this plot type in paper X, can someone add an example?") — opens a pre-filled GitHub issue |
| **Contribute an example** | Submit a new example — guided form that creates a pull request to the community gallery repo |
| **Browse contributions** | See pending / recently merged community examples |

---

## Non-Goals

- GALLERY does not run the analysis — that is HOME.
- GALLERY does not build or edit data analysis recipes — that is BLUEPRINT.
- GALLERY does not store user data.
- GALLERY does not write into any other space's state at runtime — not T3, not BLUEPRINT (ADR-093, 2026-11-08). The only "handoff" is a human copying YAML text by hand.

---

## Key Design Constraints

- **Read-only data path**: GALLERY never modifies session state or data analysis recipes. It only provides YAML to copy.
- **Local-first**: the bundled gallery (shipped with the app) works fully offline. Community features (search GitHub, submit issues/PRs) require network access and are gracefully degraded when unavailable.
- **Positive inclusion** (ADR-071): GALLERY panel is only mounted when `gallery_enabled` is true in app features config.
- **No interactive handoff, anywhere (ADR-093, 2026-11-08)**: GALLERY has zero runtime coupling to HOME or BLUEPRINT. Reusing a recipe fragment is always a manual copy-paste of the YAML text (`gallery_yaml_preview` output) into a separate file or into BLUEPRINT's editor, same as any other file-based handoff (`developer_workflow.md §7`). A prior "Clone to Sandbox" button that wrote directly into HOME's T3 was removed — see ADR-093 for why.

---

## Code Modules

| Code module | Role |
|---|---|
| `gallery_viewer.py` | Browse UI, example list, preview rendering |
| `gallery_handlers.py` | Server-side handlers: example loading, taxonomy filtering, preview rendering |

---

## Current State

- Example browsing and preview: built and working.
- Search: not yet built (`RESEARCH-HELP-1` in `.claude/tasks/tasks.md`).
- Community contribution / request workflow: not yet built — `GalleryViewer.submission_modal_ui()` is defined but called from nowhere (no wired button).
- Gallery→T3 transplant ("Clone to Sandbox"): removed 2026-11-08 (ADR-093). GALLERY is now a pure read-only browser.

---

## Open Questions

- **Search scope**: local full-text search (fast, offline) vs. GitHub API search (broader, requires network). Start with local; add GitHub later.
- **Contribution workflow**: full PR via GitHub API (complex) vs. "copy this YAML template and open an issue with it" (simple, manual merge). Start simple.
- **Gallery index format**: current `gallery_index.json` registry — sufficient for local browsing; will need tags and search fields added.
- **Sample data for previews**: each example needs bundled sample data to render a preview. How is this managed? Stored per-example in the gallery dir, or a shared synthetic sample dataset?
- **Resolved 2026-11-08 (was open, F-23/ADR-093):** "Clone to Sandbox" removed outright. Eve declined a Gallery→BLUEPRINT handoff too, to keep the user spaces independent with no special case to maintain — GALLERY is inspiration only, reuse is manual copy-paste. If a machine-assisted "start a new recipe from this example" need emerges later, it is a new BLUEPRINT feature decided on its own, not a revival of this path.
