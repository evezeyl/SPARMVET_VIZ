# Developer Workflow — End-to-End Producer Journey

**Type:** Cross-space design / workflow reference
**Status:** Design (LAB-WORKFLOW-1)
**Last updated:** 2026-05-22
**Companion specs:** `spaces/HOME.md`, `spaces/BLUEPRINT.md`, `spaces/TEST_LAB.md`, `spaces/GALLERY.md`, `functionality_dependency_map.md`

---

## 1. Purpose & Audience

This document explains how the four user spaces fit together into one coherent journey for
the **developer** — the person who *produces* an analysis pipeline. It is distinct from the
HOME scientist who *runs* a finished pipeline.

The space identities make the split explicit:

| Space | Identity (from its spec) |
|---|---|
| **HOME** | "HOME users produce science from a pipeline." |
| **BLUEPRINT** | "BLUEPRINT users produce and document pipelines." |

The developer's job is everything that gets you from *messy files + a scientific goal* to a
*valid, shareable manifest that HOME can run*. HOME.md states the spine:

> "BLUEPRINT builds the manifests HOME runs, TEST_LAB prepares the data HOME receives,
> GALLERY provides the inspiration BLUEPRINT uses."

This doc does **not** introduce a new locked pipeline. It documents how the existing,
independent tools can be *used together* — and where the seams between them sit.

---

## 2. The First Principle — Every Module Stands Alone

**The workflow is a map, not a wizard.** Each tool is independently useful and can be entered
directly. A user who only needs to convert an Excel file uses the Reformatter and leaves. A
user who only needs synthetic test data uses AquaSynthesizer and leaves. Nothing forces a user
through earlier stages they do not need.

This is a hard constraint, not a preference — it is the TEST_LAB **Stateless Tool Principle**
(`rules_test_lab.md §1`):

> Each tool runs to completion and returns a downloadable artifact. Between runs, tools hold no
> state. Closing a tool panel resets it to empty. Handlers MUST NOT create `reactive.Value`
> stores that accumulate state beyond the current tool interaction.

Everything below — the chains, the "Send to" handoff, the cross-space seams — is built **on
top of** this principle without violating it (see §6).

---

## 3. The End-to-End Arc

Four stages. **Each is optional and independently usable.** A developer enters at whichever
stage their data and goal require.

```
   STAGE 1                STAGE 2              STAGE 3                  STAGE 4
   Prepare data           Scaffold             Build pipeline           Run
   (TEST_LAB)             (TEST_LAB)           (BLUEPRINT)              (HOME)
   ─────────────          ────────────         ──────────────           ──────────
   Reformat               Manifest             Open boilerplate         Load manifest
   Reconcile IDs    ───►  Scaffolding    ───►  Add wrangling/joins ───► Run analysis
   Anonymise              (boilerplate         Add plots/groups         Filter + audit
   Synthesise             manifest ZIP)        Preview / validate       Export (provenance)
                                               Save manifest
                                                    ▲
                                                    │ inspiration (copy YAML)
                                               ┌────┴─────┐
                                               │ GALLERY  │
                                               └──────────┘
```

### Stage 1 — Prepare data (TEST_LAB)

| Tool | Produces | Standalone use |
|---|---|---|
| **Reformatter** | TSV(s) from XLSX/CSV | "I just need clean TSVs" |
| **ID Reconciliation** | Verified ID matches + transformation recipe (YAML) | "Do my files' IDs line up?" |
| **Anonymiser** | Anonymised TSV(s) + mapping TSV | "Make this safe to share" |
| **AquaSynthesizer** | Synthetic TSV + config (demo or stress-test) | "Give me test/edge-case data" |

### Stage 2 — Scaffold (TEST_LAB)

**Manifest Scaffolding** turns prepared files + reconciliation recipes into a **boilerplate
manifest ZIP** (basename-mirroring structure). It generates *boilerplate only* — structure,
inferred types, PK hints, and ID-cleaning recipes baked into `tier1`. Analysis groups, plots,
joins-strategy, and `final_contract` are **the developer's job in BLUEPRINT** (`rules_test_lab.md §4`).

### Stage 3 — Build pipeline (BLUEPRINT)

The developer opens the boilerplate and builds the real pipeline with no code: add
wrangling/join/plot nodes via forms, organise groups, preview on Apply, validate, save.
GALLERY feeds this stage as **inspiration** — browse a recipe, copy its YAML, adapt it.

### Stage 4 — Run (HOME)

The finished manifest is selected in HOME and run for publication-ready, audit-tracked output.
This is the consumer end — out of scope for the producer workflow except as the destination.

---

## 4. Recommended Orderings (Advisory — Never Enforced)

Some tools have a *logical prerequisite* — using them in order produces correct results. These
are **recommendations surfaced as guidance**, not enforced gates. The user can always ignore
them (and own the consequences).

| If you want to… | Recommended precursor | Why (the logical dependency) |
|---|---|---|
| **Anonymise multiple related files** | Reconcile IDs first | Anonymisation must map the *same original ID to the same anon ID across files* so joins stay valid. Reconciliation verifies the IDs actually align before they are replaced. (Single-file anonymisation needs no precursor.) |
| **Scaffold a manifest with joins** | Reconcile IDs first | The scaffolder bakes verified join keys + ID-cleaning recipes into `tier1`. Without reconciliation it has no recipe to bake and no verified key. |
| **Reconcile messy-format files** | Reformat first | Reconciliation needs clean tabular TSVs; an XLSX or odd-delimiter CSV is reformatted first. |
| **Test a manifest you are building** | Synthesise data | Stress-test data exercises the pipeline's error handling before real data is loaded. |

Reconciliation is therefore *frequently the first optional step* — but it is never mandatory,
and a developer with already-clean, already-aligned data skips it entirely.

---

## 5. How the User Picks a Handoff — The "Send to" Pattern

The question "how can they pick that?" is answered by a single, consistent UX pattern.

After any tool **finishes a run**, its results area offers a contextual **"Send to […]"**
control. The control:

- **Only offers valid targets** for the artifact just produced. Examples:
  - Reformatter result → *Send to ID Reconciliation* · *Send to Anonymisation* · *Send to Synthetic (learn from example)*
  - ID Reconciliation result → *Send to Manifest Scaffolding* · *Send to Anonymisation*
  - Manifest Scaffolding result → *Send to BLUEPRINT* (cross-space seam — see §7)
- **Loads the artifact into the target tool as if freshly uploaded.** The target opens
  pre-filled with that input. It does not "remember" anything — it received an input, exactly
  as an upload would deliver one.
- **Never auto-runs.** The user lands on the target tool with the input loaded and is free to
  edit it before running. This is the **edit gap** — handoffs always drop the user at an
  editable artifact, never a silently-executed next step.

**The "Send to" button is a convenience, not the only path.** Because every tool is fully
independent, the user can always instead **download** an artifact and **re-upload** it into any
other tool (or into BLUEPRINT). The handoff button just skips the download/upload round-trip.

---

## 6. Why This Does Not Break the Stateless Principle

A "Send to" handoff is a **one-shot baton pass of a concrete artifact**, not accumulating
session state:

| Stateless rule | How the handoff respects it |
|---|---|
| Tools hold no state between invocations | The target tool holds nothing — it is handed an input value, then behaves identically to an upload. Close it and it resets. |
| No `reactive.Value` stores that accumulate across tools | The baton is a passed artifact (a file path + optional recipe object), consumed once by the target's normal input path. It is not a growing cross-tool store. |
| Named files are the only persistence | Unchanged. Reconciliation recipes and named synthetic scenarios still persist as YAML; nothing else does. |

The mental model: the handoff is **plumbing between independent tools**, not a stateful pipeline
engine. If the plumbing were removed, every tool would still work exactly as before via
download/upload.

---

## 7. Cross-Space Seams

The same baton-pass pattern extends across space boundaries. These are the integration points
between the producer spaces — most are **manual today**, and the recurring unbuilt one is
**"Open in BLUEPRINT."**

| Seam | Direction | State today | Target |
|---|---|---|---|
| Reconcile → Scaffold | within TEST_LAB | Designed — "continuation mode", session-held output, no re-upload | "Send to Manifest Scaffolding" button |
| Reformat / Anon / Synth → other Lab tools | within TEST_LAB | Manual download → upload | "Send to […]" buttons (§5) |
| **Scaffold → BLUEPRINT** | TEST_LAB → BLUEPRINT | Manual: download ZIP, then open master YAML in BLUEPRINT | **"Open in BLUEPRINT"** — load scaffold ZIP straight into a BLUEPRINT session |
| **GALLERY → BLUEPRINT** | GALLERY → BLUEPRINT | Manual: copy recipe YAML, paste/open in BLUEPRINT (transplant removed; no state coupling) | **"Open in BLUEPRINT"** — same inbound-manifest path |
| BLUEPRINT → HOME | BLUEPRINT → HOME | Save manifest YAML to disk → HOME's manifest selector picks it up | (works today via the file system — no new seam needed) |
| Anonymised data → BLUEPRINT (de-anonymise) | TEST_LAB → BLUEPRINT | Manual: join anonymised data with mapping TSV in BLUEPRINT (recipe printed in TEST_LAB output) | (works today; documentation is the deliverable) |

**Key observation:** "Open in BLUEPRINT" is the *single* integration that, if built, unlocks
both the TEST_LAB→BLUEPRINT and GALLERY→BLUEPRINT seams — they share one mechanism: *BLUEPRINT
accepts an inbound manifest (or fragment) and opens it in a fresh session.* GALLERY.md and
TEST_LAB.md both list this as "not yet built."

**Boundary respected:** an inbound handoff loads a manifest *into* BLUEPRINT for editing — it
does not create cross-space *reactive* coupling. BLUEPRINT receives an artifact and opens it,
exactly as it would a file the user selected. This keeps GALLERY's "no direct state coupling"
constraint intact.

---

## 8. The Full Map (Optional Flows)

```
                          ┌─────────────────────────── TEST_LAB ───────────────────────────┐
                          │                                                                 │
  raw files ──► Reformat ─┼─► clean TSVs                                                     │
   (xlsx/csv)             │       │                                                          │
                          │       ├──────────────► AquaSynthesizer ──► synthetic TSV ──────┐ │
                          │       │                 (demo / stress)    + config/scenario   │ │
                          │       ▼                                                        │ │
                          │   ID Reconciliation ──► verified matches + recipe(YAML)        │ │
                          │       │       │                                                │ │
                          │       │       └────────► Anonymiser ──► anon TSV + mapping ───┐│ │
                          │       ▼                                                       ││ │
                          │   Manifest Scaffolding ──► boilerplate manifest ZIP ────────┐ ││ │
                          │                                                             │ ││ │
                          └─────────────────────────────────────────────────────────── │ ││ ┘
                                                                                        │ ││
   GALLERY ──► browse recipe ──► copy YAML ─────────────────────────────────────┐      │ ││
                                                                                 ▼      ▼ ▼▼
                                                                          ┌──────────────────┐
                                                                          │     BLUEPRINT    │
                                                                          │  build / preview │
                                                                          │  validate / save │
                                                                          └─────────┬────────┘
                                                                                    │ save manifest
                                                                                    ▼
                                                                          ┌──────────────────┐
                                                                          │       HOME       │
                                                                          │  run / export    │
                                                                          └──────────────────┘

   Solid arrows = artifact flows. Every arrow is OPTIONAL and the producing tool is usable
   standalone. "Send to" buttons (§5) and "Open in BLUEPRINT" (§7) automate the arrows that
   are otherwise download → upload / copy → paste.
```

---

## 9. Implementation Seams Identified (feeds tasks.md)

This design surfaces the following buildable seams. They are **not started** — listed here so
the workflow doc and the task backlog stay in sync. Author as tasks when prioritised.

1. **Intra-Lab "Send to" handoff** — contextual result-area buttons on each TEST_LAB tool that
   load the produced artifact into a valid target tool's input (editable, no auto-run). Builds
   on the already-designed Reconcile→Scaffold "continuation mode."
2. **"Open in BLUEPRINT" inbound-manifest path** — BLUEPRINT accepts an inbound manifest (ZIP
   from Scaffolding, or YAML fragment from GALLERY) and opens it in a fresh editing session.
   One mechanism unlocks both the TEST_LAB→BLUEPRINT and GALLERY→BLUEPRINT seams.
3. **User-facing Quarto version** — once the workflow is built, mirror this doc into
   `docs/workflows/` as a user-facing `.qmd` (DRY: link, do not duplicate, per
   `rules_documentation_aesthetics.md §4`).

---

## 10. Open Questions

- **"Open in BLUEPRINT" inbound contract** — does BLUEPRINT open the inbound manifest into a
  *new* session unconditionally, or warn/merge if a manifest is already open? (Resolve before
  building seam #2.)
- **"Send to" target discovery** — is the valid-target list per tool hard-coded in the handler,
  or derived from artifact type? Start hard-coded (few tools); revisit if the toolbox grows.
- **Anonymiser ↔ Reconcile ordering UX** — should the Anonymiser surface a non-blocking hint
  ("Reconcile IDs first for multi-file consistency") when more than one file is loaded? Advisory
  only, never blocking (matches the BLUEPRINT AI-assistant "advise, never block" stance).
