# GALLERY — Example Inspiration & Community Browser

**Type:** User space  
**Status:** Partial build (`gallery_viewer.py` exists; community/contribution features not yet built)  
**Last updated:** 2026-05-05

> **Correction (2026-11-07):** this page said the Gallery→T3 transplant was "removed (dead code
> cleaned up 2026-05-05)" and that the handoff path is "copy YAML → open in BLUEPRINT". Checked
> against the live code (`gallery_handlers.py::handle_gallery_clone`, the "Clone to Sandbox"
> button) and `ui_implementation_contract.md §12e` ("Gallery → T3 Transplant Rules", described
> there as current and detailed): the transplant is alive today — clicking "Clone to Sandbox"
> inserts a `developer_raw_yaml` T3 node (empty `reason`, blocking apply) directly into HOME,
> gated on `t3_sandbox_enabled` and the app features (`pipeline-exploration-advanced` and
> `developer`). There is no "Open in BLUEPRINT" button and no copy-to-BLUEPRINT path anywhere
> in the code. The sections below (Non-Goals, Key Design Constraints, Current State, Open
> Questions) are corrected to match; `developer_workflow.md`/`developer_workflow.qmd` were also
> fixed (both repeated this page's stale claim).

---

## Purpose

GALLERY is a browsable collection of plot examples. It serves two roles:

1. **Inspiration**: the user can browse existing examples, see rendered previews, and understand what kind of visualisations are possible — before committing to building a data analysis recipe.
2. **Community**: users can contribute examples they have developed, request examples based on articles or needs, and discover what others have shared.

GALLERY is read-only from the analysis perspective — it does not run analyses or modify data. It feeds HOME (indirectly, via data analysis recipes) and BLUEPRINT (as inspiration for data analysis audit step).

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

---

## Key Design Constraints

- **Read-only data path**: GALLERY never modifies session state or data analysis recipes. It only provides YAML to copy.
- **Local-first**: the bundled gallery (shipped with the app) works fully offline. Community features (search GitHub, submit issues/PRs) require network access and are gracefully degraded when unavailable.
- **Positive inclusion** (ADR-071): GALLERY panel is only mounted when `gallery_enabled` is true in app features config.
- **Gallery→HOME (T3) is the implemented handoff path**: "Clone to Sandbox" sends the example's `wrangling` block straight into HOME's T3 sandbox as a `developer_raw_yaml` audit node (empty `reason`, blocking apply until filled in), gated on `t3_sandbox_enabled` and app features (`ui_implementation_contract.md §12e`). There is no GALLERY→BLUEPRINT handoff of any kind — copying a data analysis recipe fragment into BLUEPRINT (e.g. as a starting point) would be a manual copy-paste of the YAML text, same as any other file.

---

## Code Modules

| Code module | Role |
|---|---|
| `gallery_viewer.py` | Browse UI, example list, preview rendering |
| `gallery_handlers.py` | Server-side handlers: example loading, index, clone |

---

## Current State

- Example browsing and preview: built and working.
- Search: not yet built (`RESEARCH-HELP-1` in `.claude/tasks/tasks.md`).
- Community contribution / request workflow: not yet built — `GalleryViewer.submission_modal_ui()` is defined but called from nowhere (no wired button).
- Gallery→T3 transplant ("Clone to Sandbox"): built and working (`gallery_handlers.py::handle_gallery_clone`, `ui_implementation_contract.md §12e`).

---

## Open Questions

- **Search scope**: local full-text search (fast, offline) vs. GitHub API search (broader, requires network). Start with local; add GitHub later.
- **Contribution workflow**: full PR via GitHub API (complex) vs. "copy this YAML template and open an issue with it" (simple, manual merge). Start simple.
- **Gallery index format**: current `gallery_index.json` registry — sufficient for local browsing; will need tags and search fields added.
- **Sample data for previews**: each example needs bundled sample data to render a preview. How is this managed? Stored per-example in the gallery dir, or a shared synthetic sample dataset?
- **"Clone to Sandbox" is architecturally wrong as built, not just undocumented (reopened 2026-11-08, F-23 in `.claude/tasks/uml_findings.md`).** The clone button sends the example's whole `wrangling` block into HOME's T3 as a `developer_raw_yaml` node. Eve's clarification (2026-11-08): T3 is audited modifications a HOME user makes to *their own running analysis* — never a place to import new recipe content from anywhere. BLUEPRINT has no T3 and no audit stack at all; it is the IDE for building T1/T2 recipes. So this button is recipe-authoring wearing a T3 costume, one level deeper than the already-decided `ADR-082 §4` ("BLUEPRINT never authors T3 — T3 is HOME-only"). Not decided yet: remove the button entirely, or build a real Gallery→BLUEPRINT handoff (recipe-building help — matching what BLUEPRINT is actually for) to replace it. Eve will decide after testing real usage, not now. See F-23 for the full history.
