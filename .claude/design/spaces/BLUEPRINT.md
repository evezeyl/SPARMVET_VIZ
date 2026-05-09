# BLUEPRINT — Visual Manifest IDE

**Type:** User space  
**Status:** Vision / early build  
**Last updated:** 2026-05-05

---

## Purpose

BLUEPRINT is a click-button IDE for building and editing manifests without writing code. The user assembles a full analysis pipeline visually: adding nodes (T1/T2/joint/tidy/wrangle/plot), configuring their parameters via forms, connecting them into a DAG, and seeing results in real time (or on push). The output is a valid SPARMVET manifest YAML that can be loaded directly into HOME.

The goal is that a user who understands their data and what they want to do with it can build a complete manifest with zero Python/R knowledge.

**Space identity: BLUEPRINT users produce and document pipelines.**

---

## User Functionalities

| Functionality | What the user can do |
|---|---|
| **Open/create manifest** | Load an existing manifest into the IDE, or start a new one from scratch |
| **Add nodes** | Insert action nodes (T1 filter/select, T2 group/aggregate, joint merge, tidy pivot/reshape, wrangle, plot) at the correct position in the DAG |
| **Configure nodes** | Fill in node parameters via auto-generated forms (dropdowns, column pickers, value inputs) based on what the action requires |
| **Add groups** | Organise nodes into named groups (manifest sections) |
| **Add info/metadata** | Attach description, author, version, tags to the manifest or to individual nodes |
| **Visualise the DAG** | See the full pipeline as an interactive graph (TubeMap); trace lineage from any node back to source |
| **Isolate lineage** | Focus on a single manifest branch — hide unrelated nodes so you can work on one lineage at a time |
| **Branch** | Fork from any node to explore an alternative pipeline path without breaking the main branch |
| **Preview results** | See live (or push-triggered) output at any node — data preview + plots — without leaving BLUEPRINT |
| **Use actions from libraries** | Choose wrangling/tidy/plot actions from what is available in the loaded libraries; BLUEPRINT shows only valid choices for the current node type |
| **Auto-match helper** | Get suggestions for column mapping, pattern matching on IDs, and step ordering based on the loaded data |
| **Pattern matching escalation** | When automatic regex matching fails, the helper adapts: tries alternative patterns, asks the user for a hint, and eventually delegates to an agentic hook that resolves the hard case and learns from it |
| **AI manifest assistant** | Describe your analytical goal in plain language; the assistant proposes manifest structure, suggests nodes, warns about performance anti-patterns, and enforces good practices (see below) |
| **Validate** | Run manifest validation and see errors/warnings inline before saving |
| **Save / export manifest** | Write the finished manifest YAML back to disk; download it |

---

## Non-Goals

- BLUEPRINT does not run the full production analysis — that is HOME.
- BLUEPRINT does not generate test data — that is TEST_LAB.
- BLUEPRINT does not curate or share community recipes — that is GALLERY.
- BLUEPRINT does not expose a raw YAML editor as the primary interface (it may have one as an advanced escape hatch).

---

## Key Design Constraints

- **No coding required**: every action parameter must be configurable via UI controls. If an action cannot be fully configured without code, it is out of scope for this IDE.
- **Library-aware**: available actions and their parameter forms are driven by what is registered in the loaded action libraries. BLUEPRINT does not hard-code action lists.
- **Manifest-schema-faithful**: the output must be a valid manifest that passes the same validator as any hand-written YAML.
- **TubeMap is the primary navigation surface** (ADR-039): the DAG graph is not decorative — it is the main way to orient, select, and navigate nodes.
- **Positive inclusion** (ADR-071): BLUEPRINT panel is only mounted when `blueprint_enabled` is true in persona config.
- **Pattern helper shared with TEST_LAB**: the ID/column pattern matching utility must be the same component used in both spaces. Design for reuse from the start.
- **Pattern matching has an escalation ladder**: (1) automatic regex suggestion → (2) user hint + retry → (3) agentic hook for hard cases. Each level only activates when the previous fails.
- **AI assistant is implementation-aware**: it knows what actions exist in the loaded libraries, what the performance implications are, and what the app can render. It does not suggest things that are out of scope or would break the pipeline.
- **AI assistant advises and enforces good practices**, including:
  - Aggregate early (T2) if downstream nodes don't need row-level data — keeps the app reactive
  - Avoid branching unless the lineages truly diverge — unnecessary branches increase maintenance cost
  - Warn before adding a wrangle step that duplicates what a tidy/T1/T2 action already covers
  - Flag missing group keys before a join
  - Remind the user to add info/metadata nodes before finalising a manifest for sharing

---

## Code Modules

| Code module | Role |
|---|---|
| `blueprint_handlers.py` | Server-side handlers, node CRUD, manifest save/load |
| `wrangle_studio.py` | Reused for live preview rendering inside BLUEPRINT |
| `orchestrator.py` | Manifest execution engine (reused for preview runs) |

---

## Current State

- TubeMap visualisation (DAG graph) built and working in HOME's Blueprint Viewer tab.
- `blueprint_handlers.py` exists but is early-stage.
- Node add/configure/save UI: not yet built.
- Lineage isolation: not yet built.
- Branching: not yet built.
- Live preview: not yet built.
- Library-driven action forms: not yet built.

---

## Open Questions

- **Preview trigger**: should results update live (on every change) or only on explicit "Run" push? Live is more IDE-like but expensive; push is safer for large data. Probably configurable, defaulting to push.
- **Branch storage**: branches as separate YAML files, or as named variants within one file? Needs decision before building branching.
- **Pattern helper sharing**: same component as TEST_LAB, or separate? Resolve before building either.
- **Escape hatch**: should there be a raw YAML view/edit panel for power users? If yes, how do round-trip edits (YAML → form → YAML) preserve comments and custom fields?
- **Undo/redo**: needed for any IDE feel. Scope: session-only or persistent?
- **Library loading in BLUEPRINT context**: does BLUEPRINT load the same libraries as HOME, or can you load a different library set for exploration?
- **AI assistant scope boundary**: where does "advise" end and "enforce" begin? Enforcement (blocking a save) should be reserved for correctness issues (missing keys, broken lineage). Performance/style advice should be warnings only, never blocking.
- **AI assistant / agentic hook**: this is a future idea, not a planned feature. If implemented, it must be an opt-in hook (persona config flag, off by default) — not authorized for general deployment. The rules-based adviser (good practices, performance warnings) is the realistic near-term target; the LLM/agentic layer is exploratory and personal.
