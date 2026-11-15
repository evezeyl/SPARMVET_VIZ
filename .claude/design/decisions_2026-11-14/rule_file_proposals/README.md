# Rule file proposals (RULES-FORMAT1-1, prepared 2026-11-15)

No file under `.claude/rules/` was edited. Each `<rule file>.proposal.md` lists numbered changes: the lines today, the text today, the proposed text, why (decision with file:line), and whether it only corrects a fact (FACT) or "CHANGES A RULE". Each ends with "Not settled". Counts are the numbered sections of the file (some are "no change, checked") and the number of times "CHANGES A RULE" appears (a change may name it twice).

Read in this order (the files agents read most first):

| # | Proposal | Sections | CHANGES A RULE | What kind |
|---|---|---|---|---|
| 1 | `rules_data_analysis_recipe_structure.md` | 17 | about 7 | `final_contract`, `output_fields`, old action names, unquoted `on`, types, unknown keys, plot include wrapper |
| 2 | `rules_agent_role_bioscientist.md` | 16 | about 6 | same, plus the list of 68 actions, silent skip, join key types, `na` |
| 3 | `rules_data_engine.md` | 11 | about 5 | action naming and no hidden choice, determinism, `output_fields`, parity mandate (Eve to confirm), cache-key marker |
| 4 | `rules_verification_testing.md` | 5 | 0 | viz integrity suite, browser duration (D17) |
| 5 | `rules_viz_factory.md` | 5 | about 5 | parity mandate replaced (ADR-106 V9), evidence loop, seed (one point OPEN) |
| 6 | `workspace_standard.md` | 2 changes | 0 | Viz row, `@deps` examples with old action names |
| 7 | `ui_implementation_contract.md` | 6 changes | 1 | ADR-098 contradicts lines 95-99 and 262-273; ADR-105 marker on 12g; example with old actions |
| 8 | `rules_test_lab.md` | 3 | 2 | bootstrapper output in format 1, known bugs historical, gate |
| 9 | `rules_app_structure.md` | 5 | 1 (server.py over its limit: Eve decides) | removed `exporter.py`, two missing modules, `output_fields` |
| 10 | `rules_ui_dashboard.md` | 3 | 1 | T3 wording synced with the contract; marker on ADR-086 |
| 11 | `rules_app_features_flags.md` | 2 | marker only | target cascade of ADR-099 point 11 (NOT BUILT) |
| 12 | `rules_gallery_standards.md` | 6 | about 4 | 5-axis taxonomy on the plot entry, generated tag strip, preview script path |
| 13 | `rules_code_quality.md` | 2 | 0 | removed suite named, `output_fields` example |
| 14 | `rules_toolchain.md` | 1 | 0 | four tools used this week are not listed |
| 15 | `dasharch.md` | 2 | 1 | `integrity_report.txt` does not exist; wrong workflow path |
| 16 | `rules_asset_scripts.md` | 1 | 0 | one script name does not exist |

No change needed (checked):

- `rules_runtime_environment.md`: grep for `final_contract`, `output_fields`, parity, ADR numbers of this week, old actions gives 0 hits; the libs named exist (`ls libs`).
- `rules_css_style_spec.md`: same grep, 0 hits; no decision of 2026-11-14 touches CSS.
- `rules_documentation_aesthetics.md`: same grep, 0 hits.
- `rules_legacy_management.md`: same grep, 0 hits; its examples (`factory_id`) are historical on purpose.
- `rules_agent_channel.md`: same grep, 0 hits; self-contained.

Points that need Eve first (details in the files): the Polars parity mandate (withdraw like plotnine's V9?), `Categorical` as a type (DEC27 against the migration), `column` against `columns`, the seed default (0 or per session), whether Blueprint may author tier 3, `server.py` at 263 lines against the ~250 limit, the tombstone task entries that `rules_legacy_management.md` asks for when a banner is added.

Newer facts folded in: the registry holds 68 actions and 40 of them refuse an empty list (`b91a9fd5`); the visualisation components carry a field `plotnine` (exact 125, modified 44, own 22) on branch `task/viz-field-engine`, not merged, so no proposal pastes those numbers as true.
