Status: PROCESSED 2026-11-08 — all clean, no action needed (UI wireframes sweep)

# Audit Report: Data Analysis Recipe Coherence
Generated: 2026-11-08T09:47:10
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-013 (Data analysis recipe Data Contract), ADR-041 (Unified Data analysis recipe Standard), rules_data_analysis_recipe_structure.md §7

- Data analysis recipes assessed: 6
- Parse errors: 0
- Data analysis recipes with input_fields/TSV mismatches: 0
- Data analysis recipes with invalid action names: 0
- Data analysis recipes with invalid component names: 0
- Data analysis recipes with join key violations: 0
- Data analysis recipes with deprecated factory_id key (ADR-083): 0

## Result: ✅ PASS

## Per-Data analysis recipe Summary

| Data analysis recipe | Parse | Actions | Components | Join Keys | TSV Fields | factory_id |
|----------|-------|---------|------------|-----------|------------|------------|
| `1_Abromics_general_pipeline.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `1_test_data_ST22_dummy.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `2_test_data_ST22_dummy.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `demo_abromics.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `figshare_integration.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `stress_test_master.yaml` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Fix Guidance

**Invalid action name:** Check `rules_agent_role_bioscientist.md §8` for the authoritative list.
If the action genuinely does not exist, file an `[ENHANCEMENT REQUEST]` in `tasks.md`.

**Invalid component name:** Scan `libs/viz_factory/src/viz_factory/` for `@register_plot_component`.
If missing, follow `viz_factory_implementation.md` to add it.

**Join key YAML trap:** `on:` without quotes parses as boolean `True`.
Always write `'on': column_name` (single-quoted key).

**Input field slug mismatch:** Run `head -1 <source.tsv>` to see actual column names.
Update the `input_fields` slug to match exactly (case-sensitive).

**Deprecated `factory_id` key (ADR-083):** Run the migration script:
`assets/scripts/migrate_plot_specs.py --apply`
Then verify with `debug_runner.py` that the plot still renders correctly.

## References
- `rules_data_analysis_recipe_structure.md §7` — Canonical steps syntax, YAML boolean trap
- `rules_agent_role_bioscientist.md §8` — Registered action names (authoritative list)
- `rules_agent_role_bioscientist.md §3-A/B` — Wrangling and assembly canon
- Routine 13 (Data analysis recipe coherence) in `.claude/workflows/audit_routine_registry.md`