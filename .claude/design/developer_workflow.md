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

## 5. How Modules Link — Export and Choose

There is **no in-app "Send to" handoff and no automated injection between tools.** Modules link
the simple, independent way:

1. A tool runs and **exports** its result (download — TSV, recipe YAML, manifest ZIP, etc.).
2. The user **chooses** that file as the input to the next tool, exactly as any standalone
   module accepts a file.

This is deliberate. It keeps every tool a true independent module: each chooses its own input
files and produces its own exports, and works identically whether or not any other tool was
used. The "edit gap" is automatic — the exported file is a concrete artifact the user can
inspect or edit before feeding it onward; nothing auto-runs.

**One in-space convenience exists (optional, within TEST_LAB only):** if ID Reconciliation has
been run in the current session, the Manifest Scaffolding tool offers a checkbox to bake those
reconciliation steps into the generated `tier1:` wrangling. Scaffolding still works fully
standalone — you choose its data files yourself — so the reconciliation carry-over is pure
opt-in. This is the *only* cross-tool wiring, it lives entirely within one space (one
`test_lab_enabled` gate, so persona independence is unaffected), and it accumulates no state: it
reads a reactive calc that recomputes from inputs.

---

## 6. Stateless & Independent — the Invariant

- Each tool runs to completion and returns a downloadable artifact. Between runs it holds no
  state; closing a panel resets it (`rules_test_lab.md §1`).
- The only persistence is **named files** the user saves explicitly (reconciliation recipes,
  named synthetic scenarios).
- No `reactive.Value` store accumulates state across tools. Linking is via exported files the
  user re-chooses — not an in-memory pipeline engine.

---

## 7. Cross-Space Handoffs Stay File-Based (Independence Rule)

Handoffs **between** spaces are always file-based, and intentionally so: one space exports a
file; the user loads it in the other space *if and when* that space is enabled. There is **no
in-app "Open in BLUEPRINT"** and no cross-space state coupling.

**Why (decisive):** the spaces are **independently persona-gated** — `test_lab_enabled`,
`blueprint_enabled`, and `gallery_enabled` are independent flags (`rules_persona_feature_flags.md`).
A persona may grant TEST_LAB without BLUEPRINT, or GALLERY without BLUEPRINT. An in-app
cross-space handoff would break the instant the target space is disabled, and would violate
ADR-071 positive-inclusion (each space must stand alone). A file on disk works under *any*
persona combination.

| Handoff | How it works |
|---|---|
| TEST_LAB Scaffolding → BLUEPRINT | Export the boilerplate manifest ZIP; open it in BLUEPRINT (if enabled) via BLUEPRINT's normal manifest load. |
| GALLERY → BLUEPRINT | Copy the recipe YAML; paste/open it in BLUEPRINT (if enabled). |
| BLUEPRINT → HOME | Save the manifest to disk; HOME's manifest selector picks it up. |
| TEST_LAB Anonymiser → BLUEPRINT (de-anonymise) | Join the anonymised data with the mapping TSV in BLUEPRINT (recipe printed in the Anonymiser output). |

Each row is just "export here, choose there." No control reaches across a space boundary.

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

   Solid arrows = artifact flows, every one OPTIONAL. Each producing tool is usable standalone.
   Every arrow is a file the user EXPORTS from one tool/space and CHOOSES in the next — there are
   no in-app handoff buttons and no cross-space coupling (§5, §7).
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
