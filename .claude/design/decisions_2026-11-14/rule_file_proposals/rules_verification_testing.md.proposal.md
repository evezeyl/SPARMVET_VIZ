# Proposal: `.claude/rules/rules_verification_testing.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited.
Checked against: `libs/*/tests/*integrity_suite.py` (three exist: `id_reconciliation`, `ingestion`, `viz_factory`), `libs/viz_factory/tests/test_data` (194 recipes, none holds `spec_version`: all in the old form),
ADR-106 V10, `proposals_for_eve.md` D17 (line 143), `test_action_recipe_pairs.py`, `debug_wrangler.py` and `debug_assembler.py` (work on format 1).

## 1. Line 22, integrity suites (FACT)

Today (line 22, middle): `(today: \`viz_factory\`, \`ingestion\`, \`id_reconciliation\`). It is not a pytest wrapper and it is not the gate.`
Proposed: `(today: \`ingestion\` and \`id_reconciliation\`; the \`viz_factory\` suite cannot run: its 194 test recipes are in the old recipe format and are dropped, each component's YAML example becoming its test through a small generated recipe, ADR-106 V10, VIZ-STANDARD-1). It is not a pytest wrapper and it is not the gate.`
Kind: FACT. Why: ADR-106 point 10 ("The 194 old test recipes and the dead integrity suite are dropped ... This replaces RECIPE-MIGRATE-1 for those files"), decided by Eve 2026-11-14 ("V1 to V10 are OK as recommended"). Until it is built, `viz_factory_integrity_suite.py` still exists on disk; the sentence names that.

## 2. Line 17-18, component debuggers (FACT, no change needed)

`debug_wrangler.py` (`--tier tier1|tier2|all`) and `debug_assembler.py` run on a format-1 recipe (run 2026-11-15). The example in line 18 stays true.

## 3. Line 19-20, "What tests what" (FACT, optional)

Add to the transformer list: `test_min_items.py` = 40 of the 68 actions refuse an empty list or mapping (merged `b91a9fd5`); `test_registry_polars_rules.py` = the registry follows the Polars rules (DEC31 to DEC33). Optional: the sentence is a dated list, not a rule.

## 4. Line 145, browser tests duration (FACT; D17)

Today: `Browser tests (about 4 minutes; the first three run under the \`qa\` app features, ...`
Proposed: `Browser tests (about 10 minutes; add \`--durations=10\` to see the slowest; the first three run under the \`qa\` app features, ...` and add \`--durations=10\` to the command at line 150: `app/tests/test_every_app_features_starts.py -q --durations=10`.
Kind: FACT. Why: D17 says 8 minutes; the coordinator's brief says about 10; the time is not stable. Eve picks the number; the proposal gives the larger. Not settled: the exact figure.

## 5. Section 8 line 130-135 "Test baseline (checked 2026-11-06)" (FACT)

The heading date is old. Proposed: change to `Test baseline (checked 2026-11-06, still true on 2026-11-15 except the viz_factory suite: section 1)`. Only if someone has run the whole baseline on 2026-11-15; I did not run the suite (not in my brief), so this change is OPTIONAL and unverified. Leave unchanged if not verified.

## Not settled
1. Browser duration (change 4): 8 or about 10 minutes.
2. Whether the headless baseline is still "about 25 s" (line 137): not run here; the suite has grown (about 4000 tests per `task/seed-holds` progress note). Not verified.
