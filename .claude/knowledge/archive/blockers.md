# Blockers & Technical Debt (SPARMVET_VIZ)

# Last Updated: 2026-04-09 by @dasharch

## 🧱 Blocker: Data Orchestration - Lazy vs. Eager

**Category:** Implementation Logic | **Priority:** HIGH
**Current Status:** [RESOLVED] Viz Factory calls `.collect()` at the final rendering gate to satisfy Plotnine requirements while maintaining Lazy performance for upstream transformations (ADR-010).

## 🧱 Blocker: Multi-Dataset Phenotype Validation

**Category:** Algorithmic | **Priority:** MEDIUM
**Context:** Extending the "Explode-Join-Collapse" logic for complex AMR mappings beyond ResFinder.
**Status:** [ACTIVE] To be finalized in Phase 12-A during Universal Schema alignment.

## 🧱 Blocker: Metadata Constant Extraction (ADR-004)

**Category:** Implementation Logic | **Priority:** MEDIUM
**ID:** ST22-001
**Status:** [RESOLVED] Phase 11-F Refactor (April 9, 2026). WrangleStudio now leverages reactive column discovery from Tier 1, ensuring zero hardcoded column assumptions.

## 🧱 Blocker: Path Authority & Library Autonomy (ADR-031/032)

**Category:** Architecture | **Priority:** HIGH
**Context:** Logic was fragmented between `assets/scripts/` and hardcoded UI paths.
**Status:** [RESOLVED] April 9, 2026. Centralized all system paths via `Bootloader (bootloader.py)` and relocated core scripts to library internal source folders.
