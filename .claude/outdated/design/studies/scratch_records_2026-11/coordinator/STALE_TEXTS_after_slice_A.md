# Texts that are out of date after slice A (2026-11-19; from a text-only builder, merged `ebbdd787`)

## Corrected (plain documents)
`libs/transformer/README.md:82-83`, `.claude/knowledge/project_conventions.md:31`, `docs/UML/cross_cutting_concepts.md:55`, `docs/foundations/data_tiering_adr.qmd:26, :33`: one key per stored table, labelled parts, cache version 6.

## Plain documents still to correct (not in the builder's list; a small text piece)
- `docs/appendix/FAQ.qmd:28`: "compares the chained key stored in the file with the current one. The Tier 1 key covers the resolved data analysis recipe (every included file), the data content and the engine version" (a user reads this).
- `docs/UML/quality_goals.md:30`: "served only while its chained ..." (REQ-VIZ-DATA-01): to read and correct if untrue.
- `docs/UML/app.mdj`: several labels "chained keys" (model file; through the StarUML bridge only; with the UML batch).
- Code comments that say "chained key": `app/handlers/export_handlers.py:984`, `:1128`; `app/handlers/home_theater.py:311`; `app/modules/orchestrator.py:190` (still true in the sense that tier 2 is built on tier 1; wording only).

## Need the owner's yes (rule, design, spec, ADR text): not edited
- `.claude/rules/rules_data_engine.md:21`: one key from the whole recipe.
- ADR-101 status line: "NOT BUILT" (the key per table and the tier-3 part are built; the audit parts come with piece A5).
- `.claude/design/recipe_format_spec.md:718` (the P05 row: the check is retired), `:507` and `:121` (the tier-3 reader described as a target: it exists, `DataOrchestrator.materialize_tier3`), and the sentence "Its key is `hash(tier2 key, steps)`" (the key is a labelled part).
- `.claude/knowledge/architecture_decisions.md:5206` (ADR-100: "until the engine reads it a non-empty list is refused").
- `.claude/design/adr_100_recipe_format_1_draft.md:105`, `:134`; `.claude/design/home_redesign_intent_and_consequences.md:285`; `.claude/design/recipe_format_work_order.md:23`; `.claude/design/exploration/2026-11-17_engine_fields_plan.md:339` ("cache version 5"); `.claude/design/home_stage2_mechanism_spec.md` (P3 line reference to J08, `steps: {tier3: [...]}` and `wrangling.tier2` containers: both removed forms).
