# T3 in the export bundle and the lineage trail: as built

> **PARTLY SUPERSEDED when audit mode is built (ADR-099, `home_audit_steps.md`):** per-plot T3 audit steps are replaced by steps written at T1, T2 or T3 into a copy of the recipe, and the export carries that copy. This file states what the app does today. The earlier problem statements are in `outdated/design_t3_export_threading_before_clean_2026-11-13.md`.

**Last cleaned:** 2026-11-13. Evidence class: verified by reading `export_handlers.py` (names and the lineage file) on 2026-11-13; behaviour not re-run.

## What the export does with T3 today
| Item | Behaviour | Where |
|---|---|---|
| Audited filters, exclusions and column drops (`filter_row`, `exclusion_row`, `drop_column`) | applied to the plot and to `T3_data_<plot>.tsv` of that plot, from any view; recorded in `t3_steps.yaml` and the T3 Audit Trail of `report.qmd` | `export_handlers.audited_frame`, the same steps and order as the HOME preview |
| Exploration filters | never exported, from any view (ADR-098) | `export_handlers.plot_content_rules` |
| `t3_plot_overrides` (aesthetics) | recorded in `t3_steps.yaml` under `t3_aesthetic_overrides` and in the Methods prose; **not applied to the rendered plot** (the Plot Style panel is not mounted, `UX-PLOTSTYLE-1`; the render wiring is `VIZFAC-T3-OVERRIDE-1`) | `export_handlers.py` |
| New T3 node types (rename, derive, pivot) | none exist; the audit redesign allows two kinds of step only (filter rows by value, drop column) | `home_audit_steps.md` section 4 |

## The lineage trail in the bundle
`lineage/lineage_graph.json` (a shared-node graph of the lineage of every plot in scope) and the recipe files under `data_analysis_recipes/<recipe>/`, so a reader can follow a plot from its data schema through the join steps to the plot spec. Built from `build_plot_lineage` (`data_analysis_recipe_navigator.py`, ADR-074). The recipe graph of the redesign (`utils.recipe_graph`, `RECIPE-GRAPH-UTILS-1`) replaces it.

## Not built, kept in the plan
The audit-recipe copy, the hash legs and the exclusion and attrition tables: `home_stage2_mechanism_spec.md` section 4 and package P10.
