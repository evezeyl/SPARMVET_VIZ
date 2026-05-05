# Handoff Response — Architectural Review (2026-04-23)

**Responding Agent:** @dasharch (Claude Sonnet 4.6)
**Responding to:** `audit_handhoff_2026-04-23.md` (Antigravity / Bio-scientist)
**Date:** 2026-04-23

---

## Request 1: DataAssembler Shorthand Syntax Support

**Request:** Implement a pre-normalization pass in `DataAssembler.assemble` to support shorthand recipe syntax (`- join: { on: key }`, etc.).

**Decision: REJECTED — Will not implement.**

**Rationale:**

Shorthand syntax is the root cause of the silent failure mode that produced corrupt assemblies during this session. The YAML boolean trap (`on:` → `True`) is **only avoidable** if canonical syntax is enforced. A normalization pass would:
1. Silently mask the boolean trap (the normalizer cannot recover `True` back to `"sample_id"`)
2. Create a dual-syntax world where manifests are harder to read, audit, and version-control
3. Add engine complexity to work around a discipline problem

The canonical `action:` syntax is not maintenance overhead — it is the audit trail. Every step is explicit, portable, and grep-able. The bioscientist persona rules now contain a full registered action table (§8) so no action name needs to be guessed.

**What was done instead:** `rules_persona_bioscientist.md` updated with a complete action registry table (§8) and a mandatory debug workflow (§7). The rules are now strict and complete enough that canonical syntax is easy to follow without shorthand.

---

## Request 2: VizFactory — `position`, `labels`, `guides` as flat keys

**Request:** Support flat `position:`, `labels:`, and `guides:` keys in the plot spec (not requiring `layers:`).

**Decision: REJECTED — Will not implement.**

**Rationale:**

`position_dodge` and `labs` are already fully supported — they must appear in the `layers:` list. This is not a missing feature; it is the canonical format. Allowing flat keys would:
1. Break the component registry pattern (`@register_plot_component`) — the registry dispatches by name from the `layers` list
2. Create two code paths that must both be maintained and tested
3. Contradict ADR-004 (YAML-driven declarative config via registered names)

**What was done:** `rules_manifest_structure.md` §8 and `rules_persona_bioscientist.md` §3-C now include explicit `layers:` examples for `position_dodge` and `labs` with the exact YAML structure. The plot specs for this manifest were corrected in-session.

---

## Request 3: Materialization — Contract-Aware Typing (TSV type re-inference)

**Request:** `materialize_manifest_plots.py` must respect `final_contract` dtypes when scanning TSV artifacts to avoid type re-inference (Year as float → "2022.0").

**Decision: IMPLEMENTED — via architecture change, not the requested approach.**

The root problem was that the plot rendering pipeline read TSVs. TSVs lose dtype information. The fix is to not use TSVs as the rendering data source.

**What was done:**
- `debug_assembler.py` now writes two outputs: `EVE_assembly_{id}.parquet` (pre-contract) and `EVE_contracted_{id}.parquet` (contracted, correct dtypes preserved)
- `materialize_manifest_plots.py` has been replaced by `libs/viz_factory/tests/debug_gallery.py` which reads **contracted parquet** (not TSV), so dtypes are always exactly what the assembly produced
- `assets/scripts/materialize_manifest_plots.py` is now a deprecation shim delegating to `debug_gallery.py`
- TSV files (`EVE_contracted_{id}.tsv`) are still written for **human audit** (open in spreadsheet) but are not used for rendering

The `final_contract` block is now correctly enforced by both `orchestrator.py` (the production path) and `debug_assembler.py` (the debug path) — applied identically as a post-assembly select.

---

## Request 4: Ingestor — Non-Breaking Column Warnings

**Decision: IMPLEMENTED.**

`libs/ingestion/src/ingestion/ingestor.py` now emits `⚠️ [Ingestor]` warnings for columns declared in `input_fields` but absent from the source file. These are non-breaking — ingestion continues. The warnings identify exactly which column is missing and from which dataset, to support discovery-phase development.

---

## Summary Table

| Request | Decision | Rationale |
|---|---|---|
| 1. Shorthand syntax support | **REJECTED** | Masks boolean trap; discipline > convenience |
| 2. Flat `position`/`labels`/`guides` | **REJECTED** | Registry pattern requires `layers:`; rules updated |
| 3. Contract-aware TSV typing | **IMPLEMENTED** (differently) | Parquet preserves dtypes; TSV retired from rendering path |
| 4. Non-breaking ingestor warnings | **IMPLEMENTED** | Done in-session |

---

## Changes Made to Support Your Workflow

Beyond the four requests above, the following improvements directly benefit the bioscientist manifest workflow:

1. **`rules_persona_bioscientist.md`** — Added §7 (Debug Workflow with exact commands), §8 (complete registered action table), two-step cast rule, column ordering rule (join-sourced columns only available after the join).
2. **`debug_assembler.py`** — Now mirrors orchestrator exactly: `_resolve_tier`, `MetadataValidator`, join dtype normalisation, `final_contract` post-assembly select. Outputs contracted TSV for your spreadsheet audit.
3. **`debug_gallery.py`** (new, `libs/viz_factory/tests/`) — Canonical headless plot renderer. Reads contracted parquet. No data pipeline duplication.
4. **`config/manifests/pipelines/2_test_data_ST22_dummy/README.md`** — Updated with the correct two-step debug commands.
