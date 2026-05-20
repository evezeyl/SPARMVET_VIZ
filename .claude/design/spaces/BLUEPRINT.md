# BLUEPRINT — Visual Manifest IDE

**Type:** User space  
**Status:** Build (feature set locked by ADR-082)  
**Last updated:** 2026-05-20

> **Feature set locked:** see **ADR-082 — BLUEPRINT Full Feature Set & Build-Mode Contract**
> (`.claude/knowledge/architecture_decisions.md`) for the authoritative four-layer model,
> the MVP/v2/out-of-scope inventory of the 18 functionalities below, and the T1/T2-vs-T3 boundary.

---

## Purpose

BLUEPRINT is a click-button IDE for building and editing manifests without writing code. The user assembles a full analysis pipeline visually: adding nodes (T1/T2/joint/tidy/wrangle/plot), configuring their parameters via forms, connecting them into a DAG, and seeing results in real time (or on push). The output is a valid SPARMVET manifest YAML that can be loaded directly into HOME.

The goal is that a user who understands their data and what they want to do with it can build a complete manifest with zero Python/R knowledge.

**Space identity: BLUEPRINT users produce and document pipelines.**

---

## Terminology — read this before discussing "branch"

> ⚠️ **"Branch" is an overloaded word. Agents and humans MUST pin the meaning before any
> branching discussion — we have already talked past each other once because of it.**

**Branch (BLUEPRINT / manifest sense) — the authoritative definition:**

A *branch* is a **lineage bifurcation at a node**. One lineage runs shared up to a chosen node;
at that node it **splits into two (or more) child lineages**. Everything **upstream of the split
stays shared** — it is computed once (the Tier 1 trunk is materialized to parquet and the branches
`scan_parquet` it; the shared cleaning/wrangling is **never duplicated or recomputed**). The child
lineages **diverge downstream** and are stored as **fragment-per-component `!include` files**
(`wrangling/`, `output_fields/`, `assembly/`, `plots/`) wired into the master manifest.

Canonical example in the codebase: `Summary` and `Summary_quality` — same source TSV, same
`input_fields` (shared upstream), divergent `wrangling` + `output_fields` (the branch). Typical
motivation: avoid redoing shared work when the process diverges, e.g. **wide → plot A** vs.
**long → plot B**.

This is the **Bifurcation Point Rule** (`rules_data_engine.md`) made interactive. Locked in
**ADR-082 Q3**.

**A branch is NOT:**

| Not this | Why it's different |
|---|---|
| **Graph fan-out** (one TubeMap node with several arrows out) | That is the *visual* of a branch on the DAG. The branch is the underlying manifest lineage split, not the picture of it. |
| **Whole-manifest duplication** (copy the entire `.yaml` to a new file) | That is a separate, *rare* operation, used only when adding genuinely new data. The usual start is a boilerplate template, then in-manifest branching. Tracked separately (BP-DUPLICATE-1, deferred). |
| **A Tier 3 audit branch** | T3 is HOME-only. BLUEPRINT never authors T3 (ADR-082 §4). |

When in doubt, restate the definition above and confirm before building or editing branching logic.

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
| **Branch** | Split a lineage in two **at a node**: upstream stays shared (computed once), the child lineage diverges downstream as a new `!include` fragment (e.g. wide→plotA / long→plotB). Not whole-manifest duplication. See ADR-082 Q3. |
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

## Current State (verified 2026-05-20)

**Done:**
- TubeMap DAG visualisation + Lineage Rail + 3-column contract viewer (ADR-039/040/074).
- Library-driven action forms: rich 8-widget renderer for editing logic-stack nodes — all 60 transformer actions verified rendering headless (ADR-075).
- Searchable, context-filtered action picker (BP-ACTION-PARITY-1); Field Gap Analysis + forward-prop hints (BP-FIELD-GAP-1, BP-FWD-HINT-1).
- Live preview on-Apply (Glimpse + plot); manifest save + download.
- Branching via Visual Fork (BP-VISUAL-FORK-1); 20-step undo; YAML escape hatch (read-only / editable per `manifest_edit_enabled`); AI agent (ADR-076 MVP-1).

**Gaps (tracked as Phase 32 tasks under ADR-082 §3 inventory):**
- Add-node still uses a primitive UI — must unify with the rich edit form (BP-FORMS-UNIFY-1).
- Plot/component node configuration: no form path; only 7/191 components schemed (BP-COMPONENT-SCHEMA-1, BP-COMPONENT-FORMS-1).
- Group/plot creation, manifest info/metadata, new-manifest-from-scratch, inline validation: YAML-only today (BP-GROUPS-1, BP-META-1, BP-NEW-1, BP-VALIDATE-1).
- Dedicated Joint Designer pane for joins (BP-JOINT-1, Q5).
- enum visual preview + expression code-editor with autocomplete (BP-ENUM-PREVIEW-1, BP-EXPR-EDITOR-1 — ADR-075 §2).
- Lineage isolation (hide unrelated nodes): deferred to v2.

---

## Open Questions

> **Resolved 2026-05-20 → ADR-082.** The answers Eve annotated below are now locked in
> ADR-082 (preview=on-Apply; branch=node-level lineage bifurcation / fragment-per-component;
> escape-hatch=yes, comments-lost-on-roundtrip MVP; manifest-draft autosave=yes; libraries=same
> as HOME; AI=advise-only/Socratic with a definition file). Retained here as the discussion record.

- **Preview trigger**: should results update live (on every change) or only on explicit "Run" push? [Run push]Live is more IDE-like but expensive; push is safer for large data. Probably configurable, defaulting to push [Good if can use a default here].
- **Branch storage**: branches as separate YAML files, or as named variants within one file? Needs decision before building branching.[separate files - branches will mostly be used to create different plots for same data, or eg to keep data wide vs long format and then different plot]
- **Pattern helper sharing**: same component as TEST_LAB, or separate? Resolve before building either.[If we can reuse we reuse]
- **Escape hatch**: should there be a raw YAML view/edit panel for power users? If yes, how do round-trip edits (YAML → form → YAML) preserve comments and custom fields? [Yes]
- **Undo/redo**: needed for any IDE feel. Scope: session-only or persistent? [session can be saved, and there is automatically save - at least implemented for HOME - can we hook into that ?]
- **Library loading in BLUEPRINT context**: does BLUEPRINT load the same libraries as HOME, or can you load a different library set for exploration? [Same as HOME - because blueprint if for creating manifests that will be then used via HOME, so it needs to be aware of the same actions]
- **AI assistant scope boundary**: where does "advise" end and "enforce" begin? Enforcement (blocking a save) should be reserved for correctness issues (missing keys, broken lineage). Performance/style advice should be warnings only, never blocking. [AI advises - if the user want to do shit its its problem! Never blocking - but encouraging discussion if user really want to do something that is bad, try to have a discussion - eg. is there a better solution ? why do you want to do this ? it probably mean something is unclear if user really want to do ill advised things]
- **AI assistant / agentic hook**: this is a future idea, not a planned feature. If implemented, it must be an opt-in hook (persona config flag, off by default) — not authorized for general deployment. The rules-based adviser (good practices, performance warnings) is the realistic near-term target; the LLM/agentic layer is exploratory and personal. [I think we should have a definition file for the assistant - so it can be improved and modified with proper instructions and context]
