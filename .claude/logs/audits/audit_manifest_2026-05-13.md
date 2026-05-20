# Audit Report: Manifest Structure Integrity
Generated: 2026-05-13T22:00:37
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Assembler: libs/transformer/tests/debug_assembler.py
Scratch output: tmpAI/audit_manifest_integrity
Rule: All pipeline manifests must assemble without error (ADR-041, ADR-024)

- Manifests checked: 6
- Passed: 0
- Failed: 6

## Result: ❌ FAIL

## ❌ Failing Manifests

### config/manifests/pipelines/1_Abromics_general_pipeline.yaml (exit 1)
```
[============================================================]
 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)
[============================================================]

  └── ❌ Manifest Error: Failed to load /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/1_Abromics_general_pipeline.yaml. could not determine a constructor for the tag '!include'
  in "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/1_Abromics_general_pipeline.yaml", line 60, column 17
```

**Fix guidance:**
- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).
- Verify all `action:` names exist in the transformer registry.
- Ensure `final_contract` columns are produced by the recipe.
- See `rules_persona_bioscientist.md §7` error diagnosis table.

### config/manifests/pipelines/1_test_data_ST22_dummy.yaml (exit 1)
```
[============================================================]
 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)
[============================================================]

  └── ❌ Manifest Error: Failed to load /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/1_test_data_ST22_dummy.yaml. could not determine a constructor for the tag '!include'
  in "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/1_test_data_ST22_dummy.yaml", line 149, column 17
```

**Fix guidance:**
- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).
- Verify all `action:` names exist in the transformer registry.
- Ensure `final_contract` columns are produced by the recipe.
- See `rules_persona_bioscientist.md §7` error diagnosis table.

### config/manifests/pipelines/2_test_data_ST22_dummy.yaml (exit 1)
```
[============================================================]
 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)
[============================================================]

  └── ❌ Manifest Error: Failed to load /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/2_test_data_ST22_dummy.yaml. could not determine a constructor for the tag '!include'
  in "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/2_test_data_ST22_dummy.yaml", line 20, column 17
```

**Fix guidance:**
- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).
- Verify all `action:` names exist in the transformer registry.
- Ensure `final_contract` columns are produced by the recipe.
- See `rules_persona_bioscientist.md §7` error diagnosis table.

### config/manifests/pipelines/demo_abromics.yaml (exit 1)
```
[============================================================]
 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)
[============================================================]

  └── ❌ Manifest Error: Failed to load /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/demo_abromics.yaml. could not determine a constructor for the tag '!include'
  in "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/demo_abromics.yaml", line 21, column 17
```

**Fix guidance:**
- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).
- Verify all `action:` names exist in the transformer registry.
- Ensure `final_contract` columns are produced by the recipe.
- See `rules_persona_bioscientist.md §7` error diagnosis table.

### config/manifests/pipelines/figshare_integration.yaml (exit 1)
```
[============================================================]
 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)
[============================================================]

  └── ❌ Manifest Error: Failed to load /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/figshare_integration.yaml. could not determine a constructor for the tag '!include'
  in "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/figshare_integration.yaml", line 23, column 19
```

**Fix guidance:**
- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).
- Verify all `action:` names exist in the transformer registry.
- Ensure `final_contract` columns are produced by the recipe.
- See `rules_persona_bioscientist.md §7` error diagnosis table.

### config/manifests/pipelines/stress_test_master.yaml (exit 1)
```
[============================================================]
 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)
[============================================================]

  └── ❌ Manifest Error: Failed to load /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/stress_test_master.yaml. could not determine a constructor for the tag '!include'
  in "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/config/manifests/pipelines/stress_test_master.yaml", line 25, column 15
```

**Fix guidance:**
- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).
- Verify all `action:` names exist in the transformer registry.
- Ensure `final_contract` columns are produced by the recipe.
- See `rules_persona_bioscientist.md §7` error diagnosis table.

## References
- `.claude/rules/rules_manifest_structure.md` — canonical YAML format
- `.claude/rules/rules_data_engine.md` — 3-Tier lifecycle, wrangling standards
- `libs/transformer/tests/debug_assembler.py` — assembler debug runner
- Routine 3 (Manifest integrity) in `.claude/workflows/audit_routine_registry.md`
Status: PROCESSED
Triaged: 2026-05-20 — Script bug, not a manifest error. All 6 manifests fail with "could not determine a constructor for the tag '!include'" because debug_assembler.py uses yaml.safe_load() which does not register the !include constructor. Manifests are structurally sound (coherence audit PASS 6/6). Root cause: Phase 28 modularised manifests with !include but debug_assembler.py was not updated. Fix needed: use ConfigManager from libs/utils/src/utils/config_loader.py instead of yaml.safe_load. Task added: MANIFEST-AUDIT-SCRIPT-1.
