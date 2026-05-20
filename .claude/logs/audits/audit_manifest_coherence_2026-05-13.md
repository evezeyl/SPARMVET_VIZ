# Audit Report: Manifest Coherence
Generated: 2026-05-13T22:00:37
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-013 (Manifest Data Contract), ADR-041 (Unified Manifest Standard), rules_manifest_structure.md §7

- Manifests assessed: 6
- Parse errors: 0
- Manifests with input_fields/TSV mismatches: 0
- Manifests with invalid action names: 0
- Manifests with invalid component names: 0
- Manifests with join key violations: 0

## Result: ✅ PASS

## Per-Manifest Summary

| Manifest | Parse | Actions | Components | Join Keys | TSV Fields |
|----------|-------|---------|------------|-----------|------------|
| `1_Abromics_general_pipeline.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `1_test_data_ST22_dummy.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `2_test_data_ST22_dummy.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `demo_abromics.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `figshare_integration.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `stress_test_master.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ |

## Fix Guidance

**Invalid action name:** Check `rules_persona_bioscientist.md §8` for the authoritative list.
If the action genuinely does not exist, file an `[ENHANCEMENT REQUEST]` in `tasks.md`.

**Invalid component name:** Scan `libs/viz_factory/src/viz_factory/` for `@register_plot_component`.
If missing, follow `viz_factory_implementation.md` to add it.

**Join key YAML trap:** `on:` without quotes parses as boolean `True`.
Always write `'on': column_name` (single-quoted key).

**Input field slug mismatch:** Run `head -1 <source.tsv>` to see actual column names.
Update the `input_fields` slug to match exactly (case-sensitive).

## References
- `rules_manifest_structure.md §7` — Canonical recipe syntax, YAML boolean trap
- `rules_persona_bioscientist.md §8` — Registered action names (authoritative list)
- `rules_persona_bioscientist.md §3-A/B` — Wrangling and assembly canon
- Routine 13 (Manifest coherence) in `.claude/workflows/audit_routine_registry.md`
Status: PROCESSED
Triaged: 2026-05-20 — PASS, no action required.
