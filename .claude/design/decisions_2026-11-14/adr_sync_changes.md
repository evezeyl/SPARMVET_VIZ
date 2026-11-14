# ADR log brought in line with the latest decisions (ADR-SYNC-1, 2026-11-14)

For Eve. Task: "The ADRs must be updated with the latest decisions ... the latest agreed is what is true" (Eve, 2026-11-14).
File changed: `.claude/knowledge/architecture_decisions.md` only. Nothing deleted: old text stays, under a dated banner or note.
Commits on branch `task/adr-sync`: `19ace9b2`, `5d89cc85`, `acc56b5c`, `adcd19b1`, and the commit that adds this file.

**Date correction.** The decisions recorded in channel message M72 and in the coordinator's note "EVE DIRECT 00:30" are labelled
2026-11-15 there; the coordinator checked the clock: they were taken on **2026-11-14, in the evening**. The log uses 2026-11-14.
The first commit (`19ace9b2`) wrote 2026-11-15 in two places; the second commit (`5d89cc85`) corrected them.

**Build status words.** DECIDED = Eve decided (date, source). BUILT = in the code of `feat/recipe-format-1` at `70b01370` per the cited
record or commit. NOT BUILT = no code yet (task named). The code itself was not re-run for this task.

## 1. New ADRs

| ADR | Title | What it records (source, date) | Supersedes or amends |
|---|---|---|---|
| ADR-100 | Recipe format version 1 | DEC01-DEC49 (`recipe_format_spec.md` 2.1, 2026-11-12/13/14) from the draft `adr_100_recipe_format_1_draft.md`; adds "where Polars can do it, the Polars action and nothing else" (channel M56, commit `d07fe567`, 2026-11-13) and "`column` for one input column" (DEC39 over DEC15). Mostly BUILT; DEC16 engine, DEC17 reader, DEC22, DEC10 NOT BUILT | Supersedes ADR-013, ADR-014, ADR-042 last point. Amends ADR-001, 004, 041 pt 1, 046, 037, 063, 090 pts 1 and 3, 094, 099 pt 16(g) |
| ADR-101 | Node keys are a series of labelled parts | `home_hash_model_2026-11-12.md` section 5 (Eve, 2026-11-12; commit `4e1407bb`). NOT BUILT (KEYS-NODE-1) | Supersedes ADR-089 pts 1-2, ADR-099 pt 5 formula, `hash(previous key, steps)` wording; retires `decision_hash` |
| ADR-102 | A join keeps the declared key types; no join step is skipped silently | `tasks.md` JOIN-KEY-TYPES-1 (Eve, 2026-11-14), built `bddaf76a`, `77538c54`; J09-J11; Eve 2026-11-14 "no silent error" flags (self-join, float key) | Supersedes ADR-050 "Join key normalisation" |
| ADR-103 | Missing values in filters follow Polars; every filter states `na` | M65 and M69 (Eve, 2026-11-14), recorded in `tasks.md` NA-RULE-63 and `home_audit_steps.md` section 19 (`412e7d4a`). Part 1 BUILT (`4b41b719`); part 2 on branch `task/na-rule-b`, not merged | Supersedes the 2026-11-12 NA rule (ADR-099 pt 12, "The software's role", `home_audit_steps.md` 5a pt 14 and section 19) |
| ADR-104 | No silent error; the recipe is the scientific document | M72 pts 1, 3, 5, 6 and "EVE DIRECT" pts 1, 4, 5, 6, 8 (Eve, 2026-11-14 evening). Seed-holds and operators NOT BUILT (SEED-HOLDS-1, OPERATORS-SCREENS-1) | Contradicts ADR-098 pt 4 (later wins; replacement open, D1) |
| ADR-105 | Audit acts along the lineage, chosen by the user; exploration acts only on the data viewed | `home_audit_steps.md` sections 3, 4, 5a (Eve, 2026-11-12, P1, P2, P3, P5, P7; 2026-11-13 pt 22); R1 confirmed in M73 (Eve, 2026-11-14). NOT BUILT | Supersedes ADR-099 pt 4, pt 6 as mechanism, pt 7 drop sentence; ADR-098 pts 7-8; ADR-049 |
| ADR-106 | The visualisation library follows the recipe standard | V1-V10 accepted as recommended (M72 pt 2, Eve, 2026-11-14; `viz_plan_for_eve.md` section 5). V5 BUILT (`70b01370`), rest NOT BUILT (VIZ-STANDARD-1) | Replaces the plotnine parity "MUST" of `rules_viz_factory.md` section 1 (never in the log); corrects the ADR-035/036 parity citations; replaces RECIPE-MIGRATE-1 for the 194 viz test recipes |

## 2. Existing ADRs touched

| ADR | Change | Justified by (source, date) |
|---|---|---|
| ADR-001, 004 | Note: the `columns` rule is replaced | ADR-100 (DEC14, DEC15, DEC32, DEC39; 2026-11-13) |
| ADR-002, 018 | Note: example actions removed | ADR-100 pt 7 (M56, DEC35; 2026-11-13) |
| ADR-009, 012 | Note: `join_on`, `is_primary_key` replaced | DEC13 (2026-11-13), ADR-102 |
| ADR-013, 014 | SUPERSEDED banner | DEC23, DEC24, DEC45 (2026-11-13) |
| ADR-021 | SUPERSEDED banner | ADR-098 (2026-11-11), ADR-099, ADR-105 |
| ADR-024 | Note: T3 is a node with a step list and a key | `home_audit_steps.md` 5a pt 15 (2026-11-12), DEC17 |
| ADR-026 | Note: sidebar filters | ADR-098, 099, 105 |
| ADR-031 | Note: Location 5 clone, `decision_hash` | ADR-093 (2026-11-08), ADR-101 |
| ADR-035 | Note: wrong parity citation; taxonomy moved | ADR-106; DEC21, DEC47, DEC48 (2026-11-13) |
| ADR-036 | Note: wrong parity citation; ADR itself current | ADR-106 |
| ADR-037 | Note under the taxonomy point | DEC21, DEC47 (2026-11-13) |
| ADR-040, 041, 046, 076 | Note: `output_fields` / `final_contract` removed | DEC23 (2026-11-13) |
| ADR-042 | SUPERSEDED banner for "MUST handle unquoted `on`" | DEC02 and check T07 (2026-11-13) |
| ADR-043, 044 | Note: tier toggle and audit stack replaced | ADR-086, ADR-099, ADR-105 |
| ADR-045, 067, 074 | Note: navigator to be rebuilt on `utils.recipe_graph` | ADR-099 pt 16(d) (2026-11-12) |
| ADR-047 | Note: audit-mode bundle | ADR-099 pt 8, `home_audit_steps.md` section 11 (2026-11-12) |
| ADR-049 | Correction under the existing banner | ADR-105 (the reach selector was itself superseded 2026-11-12) |
| ADR-050 | SUPERSEDED in part banner | ADR-102 (Eve, 2026-11-14) |
| ADR-052, 077 | Note: new cascade rules for audit mode | ADR-099 pt 11, P1 (2026-11-12) |
| ADR-060 | Note: log moved left | ADR-073 amendment (2026-11-08) |
| ADR-063 | SUPERSEDED banner (contradicted DEC47) | DEC21, DEC47, DEC48 (2026-11-13) |
| ADR-069 | Note: `decision_hash` retired | ADR-101 |
| ADR-075 | Note: prefixes and the `polars` field | DEC31 (2026-11-13) |
| ADR-082 | Note: `output_fields`; Q2 is OPEN | DEC23, DEC17 |
| ADR-083 | Note: wrong parity citation, `_meta` retired, pt 5, DEC22 | ADR-106, DEC02, ADR-105, DEC22 |
| ADR-084 | Note: bootstrapper output is format 0 | ADR-100, ADR-092; Eve 2026-11-14 order of work |
| ADR-085 | Second banner: superseded as target design | ADR-099 pts 1-2 (2026-11-11), ADR-105 |
| ADR-086 | Second banner: superseded as target design | ADR-099 pts 1-2, P2 (2026-11-12), ADR-105 |
| ADR-089 | Correction: its banner cited ADR-099 pt 16, which does not hold the key model | ADR-101 (2026-11-12) |
| ADR-090 | Note: pts 1, 3 amended (wording in the ADR-100 draft), cache "4", seed | DEC34 (2026-11-13), ADR-104 |
| ADR-094 | Note: one checker | DEC03 (2026-11-13) |
| ADR-097 | Note under point 2 (seed) | ADR-104; run in `tmpAI/results.md` |
| ADR-098 | Second banner: pts 1, 7, 8 superseded; pt 4 contradicts "no silent error" | ADR-099, ADR-105, ADR-104 |
| ADR-099 | Reading guide at the top; points 11-16 put in order 1-16; 10 inline HISTORICAL markers (pt 4, pt 5 twice, pt 6, pt 7, pt 12 three times, pt 16(g), "The software's role"); one "settled" marker | the seven inconsistencies of the ledger, each resolved by the later record |

Counts: 7 new ADRs (ADR-100 to ADR-106); 9 SUPERSEDED or CONTRADICTS banners (013, 014, 021, 042, 050, 063, 085, 086, 098) and 2 corrections of earlier banners (049, 089); 33 dated notes (27 one-line notes under headings, notes in ADR-035, 036, 037, 083, 090, 097); ADR-099 rewritten for reading only (no sentence removed).

## 3. Open points, as written in the log (awaiting Eve)

| Point | Record 1 | Record 2 | Where in the log |
|---|---|---|---|
| `categorical` | DEC27 (Eve, 2026-11-13): refused, "this was String" | commit `e9ac815f` (2026-11-13 22:15, an agent): migrates to `Categorical`; 75 shipped fields | ADR-100 |
| Blueprint authors a plot entry's tier 3 | ADR-082 Q2, ADR-099 header (2026-11-11): never | `home_audit_steps.md` 5a pt 15 (2026-11-12), DEC17: a maker writes any action there | ADR-100, ADR-082 note, ADR-099 guide |
| Seed when the recipe writes none | ADR-090 pt 2, `rules_viz_factory.md` 8: default 0 (gallery and export use 0) | ADR-097 pt 2 and HOME code: one per session, recorded (does not reproduce the export) | ADR-104, notes in ADR-090 and ADR-097 |
| D1: filter value of another type | convert, plain error when impossible (coordinator) | refuse first (scientist viewpoint); ADR-098 pt 4 skips today, which ADR-104 forbids | ADR-104, ADR-098 banner |
| Self-join: refuse or run | proposal D9 (2026-11-14): fail with a message, recommended by all viewpoints | build `b27f89e4` on `task/join-flags` (not merged): runs as written, advice J12 | ADR-102 |
| D7, D8 (one join-key rule; confirm J10) | listed open in M72 | | ADR-102 |
| Polars parity mandate | `rules_data_engine.md` 5 "MUST strive for 1:1 parity" | DEC32, DEC41 (2026-11-13): exact `polars_` actions, missing methods deferred; not said whether the mandate is withdrawn like V9 | ADR-106 |
| NA follow-ups Q-NA3 to Q-NA6 | `tasks.md` NA-RULE-63: waiting | `d3938877` (branch) carries an old step as `remove` | ADR-103 |
| FORMULA-SAFETY-1 time or size limit | `tasks.md`: open | allow-list decided (ADR-099 pt 14) and built (`fe856c26`) | ADR-100 pt 10 |

Treated as settled by "the latest holds": `column` in `modif_`/`step_` (DEC39 over DEC15); formulas are one decision (ADR-099 pt 14 = FORMULA-SAFETY-1); DEC22 decided, not built.

## 4. Where the ledger (`tmpAI/ledger.md`) was not followed

- Self-join: the brief said "runs as written". No record of Eve choosing this was found; Eve's decision is "no silent skip" and the proposal recommended refusing. Written as OPEN.
- ADR-075: the ledger said `wraps` is replaced by the field `polars`; DEC31 keeps both ("a registry field `polars` ... plus `wraps`").
- ADR-058 (Data Import copies to `source.path`) against the 2026-11-14 import decision: the import decision is about reproducibility bundles (IMPORT-PATH-1); its reach to the Data Import panel was not verified, so no note was written.
- ADR-069 "no opt-out" against the two export modes of ADR-097: not verified, noted as "not checked".
- The ledger's "11-15" dates are 2026-11-14 (coordinator's correction).

## 5. Files whose ADR citations or statements are now wrong (list only; not edited)

Rule files (Eve's double confirmation):
- `.claude/rules/rules_data_engine.md`: line 41 (determinism wording, ADR-090 -> ADR-100 DEC34); section 4 lines 64-72 (ADR-013, ADR-014 `output_fields`); section 5 line 76 (ADR-035 cited for Polars parity; see ADR-106).
- `.claude/rules/rules_viz_factory.md`: section 1 line 13 (ADR-036 cited; the parity MUST is replaced by ADR-106 V9, approved by Eve); section 8 (default seed 0 is OPEN; a recipe seed holds, ADR-104).
- `.claude/rules/rules_data_analysis_recipe_structure.md`: section 5 (`final_contract`), section 7 (unquoted `on` fallback, ADR-042 superseded), section 9 (types `categorical`, `utf8`), section 11 (ADR-094 with `check_recipe`).
- `.claude/rules/rules_agent_role_bioscientist.md`: line 144 (join cast, ADR-102), sections 3, 6 and the action list of section 8 (ADR-100).
- `.claude/rules/rules_test_lab.md`: section 4 (bootstrapper output in format 0).
- `.claude/rules/rules_gallery_standards.md`: lines 14 and 47 (6-axis taxonomy, ADR-063 superseded).
- `.claude/rules/rules_ui_dashboard.md`: line 72 (ADR-086), section 7 ("BLUEPRINT never authors T3", OPEN), section 1 T3 scope.
- `.claude/rules/rules_app_features_flags.md`: lines 41-47 (ADR-085 My view scratchpad; target replaced by ADR-099/105); new cascade rules of ADR-099 pt 11.
- `.claude/rules/ui_implementation_contract.md`: lines 29-55, 95, 101-138, 260-286 (ADR-085, ADR-086 model), section 12g (propagation, superseded by ADR-105).
- `.claude/rules/rules_app_structure.md` line 111 and `rules_code_quality.md` line 63 (ADR-014 `output_fields`).

Knowledge and documentation:
- `.claude/knowledge/project_conventions.md`: line 190 (ADR-014), section 10 line 220 (ADR-042).
- `.claude/knowledge/data_analysis_recipe_data_contract_rules.md` section 13 (join cast, ADR-102; DOC-JOIN-CAST-1).
- `.claude/knowledge/app_features_traceability_matrix.md` line 97 (ADR-086).
- `.claude/tasks/tasks.md`: KEYS-NODE-1 still says `hash(previous key, steps)` (ADR-101); NA-RULE-63 starts with the withdrawn rule (marked inside the line).
- `docs/foundations/data_contracts_adr.qmd` lines 1, 31, 95, 226 (ADR-013, 014, 042).
- `docs/foundations/reproducibility_hash_schema.qmd` lines 10, 32, 86, 208 (ADR-089 model; ADR-101).
- `docs/foundations/reproducibility_same_input_same_output.qmd` line 86 and the order rules (ADR-090 wording, ADR-100).
- `docs/foundations/data_tiering_adr.qmd` line 26 (ADR-024 T3).
- Parity citations of ADR-035/036: `docs/appendix/viz_factory_components.qmd:72`, `docs/workflows/audit_scripts.qmd:343`, `docs/workflows/transformer_integrity.qmd:51`, `docs/workflows/wrangling.qmd:131`, `docs/workflows/visualisation_factory.qmd:66`, `docs/UML/risks_and_technical_debt.md:12`.
- `docs/appendix/data_lifecycle_theater.qmd:24`, `docs/reference/ui_style_guide.qmd:107`, `docs/index.qmd:55` (ADR-085/086 "My view", Compare).
- `.claude/design/adr_100_recipe_format_1_draft.md`: its ADR text is now in the log; the "Discrepancies" section stays for D1-D6.
