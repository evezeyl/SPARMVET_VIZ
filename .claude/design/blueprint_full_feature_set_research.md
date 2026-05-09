---
trigger: manual
status: NEEDS_DISCUSSION_WITH_USER
prepared_by: "@dasharch"
prepared_at: 2026-05-09
target_adr: TBD (proposed: ADR-082 — BLUEPRINT Full Feature Set Lock)
deps:
  documents: [.claude/design/spaces/BLUEPRINT.md, .claude/knowledge/blueprint_architect_ux_spec.md]
  consumed_by: []
---

# BLUEPRINT Architect — Full Feature Set ADR Research & Discussion Prep

**Purpose:** Pre-reading and decision points for the upcoming ADR discussion (task: `Define [opus/high]: ADR for Blueprint Architect full feature set`).

**How to use this document:** Read TL;DR (§0), then skim §1–§3 to recall context, then focus on §5 (Gap Analysis) and §6 (Decision Points). §6 is where Eve's input is needed.

---

## §0. TL;DR

- **BLUEPRINT is partially built.** ADRs 039–076 cover navigation (TubeMap), lineage (Rail + 3-column contracts), shared infrastructure, IDE Build Mode design, and the AI Agent helper. The AI Agent MVP-1 shipped 2026-05-09.
- **The form builder is the missing core.** `BP-FORMS-1` (8-widget renderer driven by `ui_schema`) is the central feature for "build without code" — it has NOT been implemented yet. Five other Phase 32 sub-tasks also remain open.
- **No existing ADR covers the full feature set as one decision.** Current ADRs are incremental. The user task asks for a single architectural lock that names every Blueprint capability and how the parts compose.
- **Seven open design questions** (§6) need explicit choices before BP-FORMS-1 can ship. Most are user-facing UX trade-offs, not technical risks.
- **Recommended ADR title:** "ADR-082 — BLUEPRINT Full Feature Set & Build-Mode Contract".

---

## §1. What is already decided (existing ADRs)

| ADR | Status | What it locks down |
|---|---|---|
| **ADR-039** | APPROVED | TubeMap (Mermaid/Cytoscape DAG) is primary nav. Three-zone Flight Deck: TubeMap (A) → tri-tab work area (B) → bottom plot+data card (C). |
| **ADR-040** | COMPLETED 2026-04-20 | Bidirectional Lineage Navigation. 3-column contract viewer (upstream / active / downstream). Lineage Rail = horizontal scrollable button strip from raw source to plot. |
| **ADR-056** | APPROVED | View title banner: "Blueprint Architect Flight Deck" with subtitle. TubeMap accordion header colour `#345beb`. |
| **ADR-067** | APPROVED 2026-05-05 | `libs/blueprint_arch/` extracted as dedicated pure-Python library. Houses `blueprint_mapper.py` + `manifest_navigator.py`. Two-Category Law (ADR-045) compliance. |
| **ADR-071** | APPROVED 2026-05-05 | Positive inclusion: Blueprint server logic only initialised when `blueprint_enabled: true`. UI outputs gated to nav panel. |
| **ADR-074** | APPROVED 2026-05-09 | Lineage infrastructure as shared provision. `build_plot_lineage()` (backward) + `get_plot_ids_in_group()` (forward). Used by HOME export AND BLUEPRINT IDE. |
| **ADR-075** | APPROVED 2026-05-09 (Design) | IDE Build Mode design. 8 widget types from `ui_schema` decorator kwarg. Action picker filtered by `context` tag (t1/t2/assembly/plot). Apply gate. 20-step undo. YAML escape hatch (read-only / editable per `manifest_edit_enabled`). |
| **ADR-076** | IMPLEMENTED 2026-05-09 | AI Agent MVP-1. `ClaudeCliAdapter` subprocess isolation. Layer 1 system prompt + Layer 3 turn context. Max 3-round tool loop. 3 MVP tools. |

**What's NOT in any single ADR:** the relationship between TubeMap navigation, Lineage Rail, the IDE form builder, the AI agent, and the YAML escape hatch as a unified user experience. Each is an island today.

---

## §2. What is currently working (implementation state)

### Core navigation — DONE
- `libs/blueprint_arch/manifest_navigator.py` — 7 public functions (sibling map, schema registry, lineage chain, fields resolution, plot-level lineage). Pure-Python, headless-safe.
- `libs/blueprint_arch/blueprint_mapper.py` — Cytoscape.js + dagre DAG generation. Node colours by role.
- TubeMap click → reactive selector sync → manifest import → logic-stack repopulation. Implemented in `app/handlers/blueprint_handlers.py`.
- Lineage Rail (Zone B Tab 2): role-badged buttons, full path from raw source to plot, active node bold-bordered.

### Form catalog infrastructure — DONE (Phase 31)
- `libs/blueprint_arch/schema_registry.py` — reads `ACTION_SCHEMAS` and `COMPONENT_SCHEMAS` populated by decorators.
- `@register_action(name, ui_schema=...)` and `@register_plot_component(name, ui_schema=...)` accept the schema.
- `get_action_catalog()`, `get_actions_for_context(t1|t2|assembly)`, `search_actions(query)` all return correct structures.

### AI Agent MVP-1 — DONE 2026-05-09
- All 8 BP-AGENT-* tasks complete. Chat panel renders. Adapter status banner. Single-flight gate. Tool-call loop.

### Undo & persona gating — DONE
- 20-step session undo deque (`BP-UNDO-1`).
- `manifest_edit_enabled` flag in all 6 persona templates (developer + qa: true; others: false).
- Cascade rule: if `blueprint_enabled: false`, `manifest_edit_enabled` silently suppressed.

---

## §3. What is pending (Phase 32 open work)

| Task | Scope | Risk | Blocks |
|---|---|---|---|
| **BP-FORMS-1** `[opus/high]` | Form renderer for all 8 widget types. Edit-in-place + Apply gate. Schema invalidation markers on downstream nodes. | HIGH | Everything — without forms, the only edit path is YAML. |
| **BP-ESCAPE-1** `[sonnet/medium]` | YAML escape hatch: read-only (blueprint_enabled) + editable (manifest_edit_enabled). Re-parse on save. | MEDIUM | Power-user workflow. |
| **BP-HELP-1** `[sonnet/medium]` | Help panel: Python `__doc__` resolution via `importlib`; optional `doc_url` (air-gap safe). | LOW | Discoverability for first-time users. |
| **BP-COLOR-1** `[sonnet/medium]` | Color widget: column mapping toggle / palette picker / hex picker. `from_project_colors` reserved for v2. | LOW | Plot aesthetics. |
| **ACTION-RENAME-1** `[haiku/low]` | `scripts/migrate_manifests.py` — scan YAML for renamed actions. | LOW | Future-proofing. |

**Critical observation:** BP-FORMS-1 is the gate. Until it ships, "build without code" is aspirational — users still need to read YAML or trust the AI agent.

---

## §4. Cross-references — what the rules say today

| Source | Says |
|---|---|
| `rules_ui_dashboard.md §7` | TubeMap (collapsible) → Plot → Data Glimpse central stack. Right sidebar = Logic. Reactive sync on edit. Apply gate. Three edit layers (in-place, undo, YAML). |
| `rules_persona_feature_flags.md §Group D` | `blueprint_enabled` gates the workspace. `manifest_edit_enabled` gates editable YAML. `blueprint_agent_enabled` gates the agent. Soft cascade: child off when parent off. |
| `BLUEPRINT.md` design doc | 18 user functionalities listed (open/create, add nodes, configure, branch, AI assistant, etc.). 4 non-goals. **Not all 18 functionalities map to existing ADRs or implementation.** |
| `blueprint_architect_ux_spec.md` (Phase 26) | UX spec for 3-zone layout. Status: core layout DONE. Several refinements deferred. |

---

## §5. Gap Analysis — task scope vs current state

The task names eight feature areas:

| Feature area | Currently covered by | Gap |
|---|---|---|
| **Functionalities** | Listed in `BLUEPRINT.md` (18 items), no consolidated ADR | Need a feature-level lock: which 18 are MVP? Which are v2? Which are out of scope? |
| **Help develop without code** | BP-FORMS-1 designed (ADR-075), not implemented; AI agent shipped | Until BP-FORMS-1 ships, "without code" = "with AI agent only". Need to decide if that's acceptable for first release or a blocker. |
| **Input/output contracts** | ADR-040 + ADR-074 cover lineage + 3-column contract viewer | Working, but contract editing UI is read-only today. Editing a schema cell would update the manifest's `input_fields`/`output_fields` — **not yet wired**. |
| **Action insertions** | Form picker designed (ADR-075), context-tagged catalog working | Insert UI not built. Position rules ("can I add a `join` here?") rely on `context` tag — but no UI to enforce it visually. |
| **Update data view for selected lineage** | Zone C "Live Data Glimpse" exists, materialises from cached parquets | Works for current node. **Does not refresh dynamically when user edits a node** — currently shows last-applied state. Decision point: live vs. on-Apply (BLUEPRINT.md Open Question 1). |
| **Improved data inspection** | DataGrid + status line | No column stats, no value-distribution preview, no null-profile UI. Mentioned as desire in §9 but no ADR. |
| **Joint definitions** | `assembly/` recipe files, `right_ingredient` + `'on'` join syntax | No visual UI for join authoring. Join key inference is manual today. **Significant gap** for "without code". |
| **Work in T1/T2/T3** | T1/T2 authoring shares the same form picker (filtered by `context`); T3 is HOME-only (publication finisher) | BLUEPRINT does NOT author T3. T3 lives in HOME (audit nodes). Decision needed: should BLUEPRINT also expose T3? Or is the boundary "BLUEPRINT writes manifest YAML, HOME writes T3 audit nodes"? |
| **Definition of groups and plot recipe** | `analysis_groups` block in master manifest, `plots/<plot_id>.yaml` files | UI for creating groups / plots / assigning plots to groups: NOT built. Today user must edit YAML directly. |

---

## §6. Open Decision Points (the discussion list)

These are the concrete questions to settle in the new ADR. Each has 2–3 options with consequences.

### Q1. Preview trigger — when does the data view refresh?

| Option | Behaviour | Trade-off |
|---|---|---|
| **A. Live (every keystroke)** | IDE-like; cell shows result instantly | Expensive on large data; burns Polars LazyFrame collection budget |
| **B. On-Apply only** | User commits → frame recomputes → glimpse updates | Predictable, cheap, matches HOME T3 Apply pattern |
| **C. Configurable per-persona** | Default Apply; developer/qa can opt into live | Adds a flag; complex |

**Recommendation:** B (matches HOME mental model). User input needed.

### Q2. T3 authoring scope — does BLUEPRINT touch T3?

| Option | Behaviour |
|---|---|
| **A. BLUEPRINT writes manifest only (T1/T2 + plots)** | Boundary stays clean: BLUEPRINT = pipeline author; HOME = analyst |
| **B. BLUEPRINT also exposes T3 (preview T3 nodes within IDE)** | Pipeline author can simulate analyst experience in-IDE |
| **C. Read-only T3 view in BLUEPRINT (cannot edit, can see existing)** | Compromise; useful for understanding what HOME analysts will produce |

**Recommendation:** A (preserves separation of concerns). User input needed.

### Q3. Branching storage — how are variants persisted?

| Option | Storage |
|---|---|
| **A. Separate YAML files per variant** | `pipeline_v1.yaml`, `pipeline_v2.yaml` in same dir |
| **B. Named variants within one manifest** | YAML `variants:` block; one file holds many |
| **C. Git branches** | Defer to git tooling; no in-app variant management |

**Recommendation:** A (simplest, matches existing manifest convention). User input needed.

### Q4. YAML escape hatch round-trip — how do we handle comments?

If user writes a YAML comment `# this is the join for Q3`, then opens form view, then re-saves: does the comment survive?

| Option | Mechanism |
|---|---|
| **A. Don't try; comments lost on round-trip** | Document the limitation; users keep important notes elsewhere |
| **B. Preserve via ruamel.yaml round-trip mode** | Library exists; adds dependency complexity |
| **C. Capture all comments as `_comments:` keys in the manifest schema** | Lossless but pollutes the manifest |

**Recommendation:** B if it works simply, else A with a clear limitation note. User input needed.

### Q5. Joint (assembly) definitions — what UI for join authoring?

| Option | UI |
|---|---|
| **A. Form-driven (action picker shows `join`, opens dialog with left/right/on/how)** | Consistent with other actions; needs schema introspection of left + right ingredients |
| **B. Dedicated "Joint Designer" pane** | Separate UI sub-tab; can show side-by-side schemas + key match preview |
| **C. AI-agent assisted only** | User describes join in plain English; agent proposes YAML |

**Recommendation:** Hybrid A+C — form for power users, AI agent as helper. User input needed.

### Q6. Group + plot creation UI

| Option | Mechanism |
|---|---|
| **A. "Add group" / "Add plot" buttons in TubeMap context menu** | New plot stub created; user fills via form |
| **B. Sidebar list of all groups/plots, with create/delete affordances** | Persistent visible inventory |
| **C. Both — sidebar list + TubeMap context menu** | More discoverability, more complexity |

**Recommendation:** B for MVP (clearer mental model). User input needed.

### Q7. Data inspection beyond glimpse — scope

| Option | Inspection capabilities |
|---|---|
| **A. Glimpse only (current state — DataGrid + 5-row preview)** | MVP-safe |
| **B. Glimpse + per-column stats panel (mean/median/null count/uniques)** | Polars `describe_stats` already exists as an action; UI presents it without writing into the recipe |
| **C. Full profiler (B + value distributions + correlation)** | Heavy UI; overlaps with downstream tooling |

**Recommendation:** B (cheap win, leverages existing action). User input needed.

---

## §7. Out-of-scope clarifications

To keep the ADR tight, propose these are **explicitly OUT of scope** for the full-feature-set lock:

- **Pattern helper sharing with TEST_LAB** — separate ADR; both spaces continue to use their own implementations until a clear duplication emerges
- **Library loading variations** — same libraries as HOME; no separate "BLUEPRINT library set"
- **Branching feature implementation** — design decided in this ADR (Q3), but build deferred to Phase 33+
- **Real-time collaboration** — single-user only; no concurrent-edit features
- **Manifest version control / diff viewer** — defer to git tooling
- **Schema migration when actions are renamed** — `ACTION-RENAME-1` script, separate task

---

## §8. Proposed ADR structure

```
ADR-082: BLUEPRINT Full Feature Set & Build-Mode Contract

§1. Status: PROPOSED
§2. Context: Why an umbrella ADR now (incremental ADRs leave gaps; need one
    document a new contributor can read end-to-end)
§3. Decision: Lock the feature set into 4 layers
    - Layer 1 — Navigation (TubeMap + Rail) — locked by ADR-039/040/074
    - Layer 2 — Forms (action/component picker + 8 widgets) — locked here
    - Layer 3 — Data view (Glimpse + per-column stats) — locked here
    - Layer 4 — Helpers (AI agent + YAML escape hatch + undo) — locked by ADR-075/076
§4. Decisions on the seven open questions (§6)
§5. MVP feature inventory (which of BLUEPRINT.md's 18 functionalities ship in
    Phase 32; which slip to v2)
§6. T1/T2 vs T3 boundary statement
§7. Out-of-scope (§7 above)
§8. Consequences:
    - Documentation impact (rules, design specs, knowledge index)
    - Test impact (what smoke tests need to be added)
    - Persona impact (which flags gate which layer)
§9. Implementation order: which Phase 32 tasks unblock which features
```

---

## §9. Pre-Discussion Checklist (Eve to read fresh)

Before the discussion, please skim these to refresh context:

1. `.claude/design/spaces/BLUEPRINT.md` — the original 18 functionalities (~5 min)
2. `.claude/knowledge/blueprint_architect_ux_spec.md` — UX spec (status: core layout DONE) (~10 min)
3. This document, §6 (decisions) (~10 min)

**Bring opinions on:** Q1 (preview trigger), Q2 (T3 boundary), Q5 (joint UI), Q7 (data inspection scope). The other questions have a clear lean.

---

## §10. Status

**This document is READY FOR DISCUSSION.** Tag `NEEDS_DISCUSSION_WITH_USER` in frontmatter. Updated:

- `.claude/tasks/tasks.md`: tagged `[NEEDS DISCUSSION]` with link to this file
- No code or rule changes made; this is research only

When discussion happens, the output is a written ADR-082 draft + updates to `BLUEPRINT.md`, `rules_ui_dashboard.md §7`, `implementation_plan_master.md` Phase 32, and `tasks.md`.
