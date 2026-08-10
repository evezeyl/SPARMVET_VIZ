# Audit Report: Manifest Structure Integrity
Generated: 2026-07-29T22:00:15
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Assembler: libs/transformer/tests/debug_assembler.py
Scratch output: tmpAI/audit_manifest_integrity
Rule: All pipeline manifests must assemble without error (ADR-041, ADR-024)

- Manifests checked: 6
- Passed: 4
- Failed: 2

## Result: ❌ FAIL

## ❌ Failing Manifests

### config/manifests/pipelines/1_test_data_ST22_dummy.yaml (exit 1)
```
──────┬──────────┬───┬──────────────┬─────────┬────────┬─────────┐
│ sample_id ┆ total_reads ┆ total_bases ┆ q20_rate ┆ … ┆ proportion_5 ┆ source  ┆ year   ┆ country │
│ ---       ┆ ---         ┆ ---         ┆ ---      ┆   ┆ ---          ┆ ---     ┆ ---    ┆ ---     │
│ str       ┆ f64         ┆ i64         ┆ f64      ┆   ┆ f64          ┆ cat     ┆ f64    ┆ cat     │
╞═══════════╪═════════════╪═════════════╪══════════╪═══╪══════════════╪═════════╪════════╪═════════╡
│ 32557144  ┆ 3.196007e6  ┆ 936595500   ┆ 0.912905 ┆ … ┆ 0.527004     ┆ Broiler ┆ 2024.0 ┆ Norway  │
│ 97991777  ┆ 3.116154e6  ┆ 265216929   ┆ 0.915854 ┆ … ┆ 0.581394     ┆ Parent  ┆ 2024.0 ┆ Norway  │
│ 80700308  ┆ 2.979581e6  ┆ 935681922   ┆ 0.861196 ┆ … ┆ 0.096484     ┆ Layer   ┆ 2024.0 ┆ Norway  │
│ 51573804  ┆ 3.285073e6  ┆ 615957744   ┆ 0.947089 ┆ … ┆ 0.533945     ┆ Parent  ┆ 2024.0 ┆ Norway  │
│ 35115511  ┆ 3.021266e6  ┆ 1109025927  ┆ 0.923271 ┆ … ┆ 0.378577     ┆ Layer   ┆ 2024.0 ┆ Norway  │
└───────────┴─────────────┴─────────────┴──────────┴───┴──────────────┴─────────┴────────┴─────────┘
  └── ✅ Final: 54 columns, 42 rows.

[ASSEMBLY: Summary_phenotype_length_fragmentation]
Traceback (most recent call last):
  File "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/transformer/tests/debug_assembler.py", line 281, in <module>
    run_assembler_debug(args.manifest, args.data, out)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/transformer/tests/debug_assembler.py", line 132, in run_assembler_debug
    recipe = DataWrangler._resolve_tier(recipe_raw, "tier1")
  File "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/transformer/src/transformer/data_wrangler.py", line 86, in _resolve_tier
    raise ManifestError(
    ...<10 lines>...
    )
utils.errors.ManifestError: Flat 'wrangling:' list is no longer accepted. Use the tiered structure with 'tier1:' and 'tier2:' keys.
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

  [ConfigManager] Auto-unnesting redundant key 'input_fields' from 1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml
  [ConfigManager] Auto-unnesting redundant key 'input_fields' from 1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml
  └── 📥 Ingestion Base: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/assets/test_data

[ASSEMBLY: demo_join]
Traceback (most recent call last):
  File "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/transformer/tests/debug_assembler.py", line 281, in <module>
    run_assembler_debug(args.manifest, args.data, out)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/transformer/tests/debug_assembler.py", line 132, in run_assembler_debug
    recipe = DataWrangler._resolve_tier(recipe_raw, "tier1")
  File "/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/transformer/src/transformer/data_wrangler.py", line 86, in _resolve_tier
    raise ManifestError(
    ...<10 lines>...
    )
utils.errors.ManifestError: Flat 'wrangling:' list is no longer accepted. Use the tiered structure with 'tier1:' and 'tier2:' keys.
```

**Fix guidance:**
- Check `input_fields` `original_name` values match actual TSV column headers (slugs are internal identifiers, not TSV headers).
- Verify all `action:` names exist in the transformer registry.
- Ensure `final_contract` columns are produced by the recipe.
- See `rules_persona_bioscientist.md §7` error diagnosis table.

## ✅ Passing Manifests

- `config/manifests/pipelines/1_Abromics_general_pipeline.yaml`
- `config/manifests/pipelines/2_test_data_ST22_dummy.yaml`
- `config/manifests/pipelines/figshare_integration.yaml`
- `config/manifests/pipelines/stress_test_master.yaml`

## References
- `.claude/rules/rules_manifest_structure.md` — canonical YAML format
- `.claude/rules/rules_data_engine.md` — 3-Tier lifecycle, wrangling standards
- `libs/transformer/tests/debug_assembler.py` — assembler debug runner
- Routine 3 (Manifest integrity) in `.claude/workflows/audit_routine_registry.md`