# Implementation Plan

## Goal Description
The objective is to fix technical debt, optimize dashboard reactivity, and resolve operational discrepancies within the Gallery system.
1. **[TBD-01] Path Hacking Violation:** Eradicate `sys.path.insert`/`sys.path.append` references from all test scripts. The testing environment will rely strictly on the `pip install -e` mechanism natively provided by the configured virtual environment. A strict warning comment will be added to each script.
2. **[TBD-02] Cache & Hashing Standardization:** Implement a hierarchical dictionary cache within the `Bootloader` and Server (`cache[project_id][dataset_id][plot_id]`). This allows retrieval of immutable Tier 1/Tier 2 data and associated pre-computed plots without recalculation natively at UI startup. The rulebook will be updated to document this cache hierarchy so future agents adhere to it.
3. **[TBD-03] Gallery functioning & Reactivity:** Refactor the Gallery to exclusively function as a fast static asset browser. It will load `png` images and `recipe_manifest/metadata` directly from Location 5. The active data computations will be purged from the Gallery, retaining ONLY the functionality to copy recipe steps into the active Analysis Tier 3 sandbox to aid development.
4. **[TBD-04] Rulebook Governance:** Explicitly update the UI dashboard architectural rulebook (`rules_ui_dashboard.md`) to document these Gallery constraints and caching invariants, ensuring these anti-pattern violations do not recur in the future.

## Proposed Changes

### `libs/*` Test Suites
Remove `sys.path` injection statements from the header of all relevant test scripts to enforce full ADR-016 compliance.
**All modified testing scripts will receive the following immutable header ban:**
`# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.`
#### [MODIFY] [app/tests/test_ui_persona_masking.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/tests/test_ui_persona_masking.py)
#### [MODIFY] `libs/transformer/tests/debug_runner.py`
#### [MODIFY] [libs/transformer/tests/transformer_integrity_suite.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/transformer/tests/transformer_integrity_suite.py)
#### [MODIFY] [libs/viz_factory/tests/viz_factory_integrity_suite.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/viz_factory/tests/viz_factory_integrity_suite.py)
*(This change applies to all testing scripts that currently violate the standard).*

### [app/src/bootloader.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/src/bootloader.py) & [app/src/server.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/src/server.py) (Caching & Optimization)
#### [MODIFY] [app/src/bootloader.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/src/bootloader.py)
- Introduce a hierarchical hash-based dictionary cache for parsed schemas, manifests, and pre-calculated assets, keyed by `project_id -> dataset_id -> plot_id`. This correctly groups multiple plots under their respective datasets.

#### [MODIFY] [app/src/server.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/src/server.py)
- Refactor the reactive pipeline to eagerly retrieve the immutable Tier 1 / Tier 2 data and plots via their identity at startup, skipping expensive computations.
- Prevent initial data/manifest auto-loading when launching the Developer persona.
- **Gallery Refactoring:** Strip the active rendering logic from the gallery observer. The Gallery must exclusively display pre-existing Location 5 components and provide a targeted copy-action to push the recipe steps into the Tier 3 wrangle studio ([logic_stack](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/modules/wrangle_studio.py#166-193)). 

### Project Architecture Rules
#### [MODIFY] [.claude/rules/rules_ui_dashboard.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/rules_ui_dashboard.md)
- Add a new section enforcing the **Gallery Isolation Boundaries**.
- Add the **Hierarchical Cache Architecture** (`project -> dataset -> plot`) to ensure agents universally respect and utilize the shared Bootloader cache structures properly without recalculating static Tier 1/2 outputs.

## Verification Plan

### Automated Tests
1. **Wrapper Integrity Suite Test**: 
   - Execute the centralized wrappers natively. They must pass seamlessly without path hacking.
   - Run [app/tests/test_ui_persona_masking.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/tests/test_ui_persona_masking.py).
   
### Manual Verification
- In the active app, load the Gallery tab and scroll through items to confirm lightning-fast reactivity and that only images/text are served (no computation delays). 
- Perform a "Copy" operation from a Gallery item back into Tier 3 to verify recipe transplantation works natively.
- Confirm Developer persona initializes rapidly with an empty slate.
- Verify that standard plots load instantly from UI cache via the `plot_id`-aware hashing without waiting for Tier 1 calculation triggers.
