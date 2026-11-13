# Recipe format: order of work, owners, models (format version 1)

**Written for:** Eve (to set the models and say go), the HOME session (to review and to start its items).
**Status:** PROPOSED by the recipe session on 2026-11-13 (task SPEC-CLEAN-1, part 2). No code before Eve says go. The decisions behind it are in `recipe_format_spec.md` (the decision numbers `DEC` and the recommendations `R` are cited here).
**Model tags** follow `CLAUDE.md` section 2: `[haiku/low]` mechanical; `[sonnet/low]` one file; `[sonnet/medium]` several files in an existing pattern; `[sonnet/high]` a new module, a cross-file change or a hard bug; `[opus/high]` architecture, an ADR, novel design; `[opus/max]` ambiguous and cross-cutting.
**Owners.** R = recipe session (spec, checker, migration, writers, gallery scripts, ADR, docs). H = HOME session (engine, ingestion, `libs/transformer`, tests of the engine, security tests, HOME and Blueprint code). One owner per file (`rules_agent_channel.md` 4).

## 1. The items

| # | Item | Owner | Model | Needs | Notes |
|---|---|---|---|---|---|
| W0 | **Golden baseline:** the content hash of every collection and of every plot's data of every shipped recipe, recorded before any change; a script that compares and lists every difference (DEC43) | H | `[sonnet/medium]` | nothing | **DONE** (commit `18e5cda6`: `assets/scripts/golden_baseline.py`, `app/tests/golden/baseline.json`, 8 tests; 7 recipes, 76 table records; the shipped `demo_abromics` plot `demo_st_by_source` already fails on an unknown column, recorded as a failing state). Every later item is measured against it |
| W1 | **`ui_schema` rules and `step_problems`:** the `rules` list (`when`, `require`, `one_of`, `exclusive`, R3) and `utils.ui_schema.step_problems(action, spec, schema)`, one rule set for the checker and the engine; tests first | R | `[sonnet/high]` | nothing | the shared interface H's registry work (W6) writes against; commit it first, small |
| W2 | **`check_recipe` core:** the packaged specification data file, the loader that raises on a repeated key, refuses unquoted `on`, fragment wrapper, `!include` outside the folder; all checks of section 11 of the spec; messages with the generated correction; `legacy_keys` table (old keys and old action names); profiles; coverage | R | `[sonnet/high]` | W1 (interface); the registry data of W6 for the action checks | the largest R item; build by groups of checks (structure, then fields and types, then steps, then plots) |
| W3 | **Security, checker side:** `formula_check.py` (allow-list read from Polars, the `stat_function` grammar, empty builtins), path shape and containment (PA01, PA02), `!include` confinement in the loader; attack tests for them | R | `[sonnet/high]` | nothing for the formula check | the design is in spec section 15 |
| W3b | **Security, engine side:** attack tests over all three formula sites, zip import (zip-slip), `report.qmd` labels, YAML alias expansion, regex | H | `[opus/high]` to design the attacks (adversarial thinking), `[sonnet/high]` to write them | W3 for the formula check to attack | in parallel with W3: write the attacks first, they fail until W3 lands |
| W4 | **Constants module for action names** in `libs/utils` and the two tests (R4) | R | `[sonnet/medium]` | the final names (decided) | then H changes the six consumers |
| W5 | **Ingestion:** the declared dtype to the CSV reader (`schema_overrides`), the dtype allow-list read from Polars with its probe test, `null_values` and `strip` replace the hidden sanitiser (order defined), `type` required, `categorical` refused; the stale `manifest_paths` in `renamed_keys.py:20`; strict import is built | H | `[sonnet/high]` | W0 | the checker side (FD02, FD05, S09) is in W2 |
| W6 | **Registry rework in `libs/transformer`:** prefixes and the `polars` field; parameters completed or required (no hidden choice, DEC33); the equality tests against Polars; the registry tests (prefix equals field, no default other than Polars', DEC32); `polars_select`, `polars_drop`, `polars_with_columns`, `modif_filter`, `polars_fill_nan`, `polars_drop_nans`; the removals (`percentile`, `mutate`, `add_constant`, `keep_columns`, `drop_columns`, the duplicates, `scan_parquet` and `sink_parquet` as recipe actions); the run-time guard `ACTION-MUST-ACT-1`; `MODIF-FILTER-VERIFY-1`; `MISSING-VIZ-FILTERS-1`; `REMOVE-CATEGORY-SELECT-1` (approved) | H | `[sonnet/high]`, one package per action family | W0, W1 | the largest H item; each `step_` action is read first (R7); `derive_categories` waits for Q2 |
| W7 | **Migration tool, run A** (names, types, every silent default written into the steps) and its runs over: `config/` (pipelines, templates, retest), the 68 transformer fixtures, the 194 + 1 viz test recipes, the writers' output, inline test recipes. Result-identical against W0 | R | `[sonnet/high]` | W6 (the new names exist), W5 (the types), W0 | the tool is one file; the runs are reviewed output, not 260 files by eye |
| W8 | **Writers and the test helper:** `utils.recipe_factory` (a minimal valid recipe), `write_recipe`; the test-lab bootstrapper and scaffolder, `create_data_analysis_recipe.py`, Blueprint's new-recipe form, the export's forked recipe, each emitting format 1 and keeping comments | R | `[sonnet/medium]` | W2 | one test per writer |
| W9 | **Migration run B and the engine side:** `final_contract`, `keep_columns`, `drop_columns` to `polars_select` and `polars_drop`, `labels`; the engine, the cache keys (one `ENGINE_CACHE_VERSION` bump at the release), the export and the audit translator stop reading `final_contract`; tests adapted first | R tool, H engine | R `[sonnet/high]`, H `[sonnet/high]` | W6 (strict `polars_select`), W7 | Eve sees every list of changed tables |
| W10 | **Tier-3 reader** in the engine (HOME package P5): the node of the plot's T3 list, `steps.tier3` read, P05 switched off, then spec-level `filters` migrated (P06) and the HOME merge bug (R1) | H | `[sonnet/high]` | W0; the mechanism spec of HOME | parallel with W7 to W9; `beeswarm_sina` follows it |
| W11 | **Gallery:** the profile checks (GP01 to GP06), the vocabulary data file, conversion of the 34 bundles to standard recipes, previews by the app's path, the viewer reads the terms, index rebuild checked, `GALLERY-RIGOR-1`; Eve looks at the 12 changed pictures | R | `[sonnet/medium]` | W2, W7; W10 for `beeswarm_sina` | `rules_gallery_standards.md` is rewritten with Eve's double confirmation |
| W12 | **ADR-100** (format version 1; supersedes ADR-013/014; amends ADR-090, ADR-094, ADR-083 `_meta`) | R | `[opus/high]` | the names and the order settled (now) | can be drafted at once |
| W13 | **Documentation sweep** (#79): the appendix, `Standards_yaml.qmd`, the user guides, `DOC-MISSING-VALUES-1` (null, NaN, text `NA`, `null_values`, `na`, the Namibia example); the rule files only with Eve's double confirmation | R | `[sonnet/low]`; the rule-file text `[opus/high]` | W7 for the final action names | the old-name table feeds it |
| W14 | **Blueprint:** forms for the new actions and keys, the type picker, `labels`, the tier-3 steps, the register of evidence section 5 | H | `[sonnet/high]` | W6, W9, W10 | last, its own package |
| W15 | **Science review of the pipelines** (`RECIPE-ST22-FIX-1`, #67 to #70; a data-scientist pass per recipe, spec section 18) | R with Eve | `[opus/high]` | W7 | before the descriptions are finalised |
| W16 | **`ID-RECON-STEPS-1`:** ID reconciliation's suggested steps use real keys and actions; its tests run them through `step_problems` | H | `[sonnet/low]` | W1, W6 | small |

## 2. One series on a branch, then the order

**Atomicity (HOME session's point, accepted):** W5 (ingestion requires `type`, `null_values`, `strip`) and W6 (the new names) break every shipped recipe until run A (W7) has rewritten them, and no shim is allowed. So **W5, W6 and W7 land as ONE series on a branch** (proposed `feat/recipe-format-1`, Eve to confirm) and `dev` stays green; the baseline must say "result-identical" before the merge. Tests-first parts can be committed on `dev` as strict `xfail` (reader dtype tests, `null_values` tests, equality tests, attacks). W10 (the tier-3 reader) is independent of the names and runs on `dev`.

## 3. Order and what can run at the same time

1. **W0 first** (H), alone: it is the measure for everything after.
2. **Right after W0, in parallel, because they touch different files:** W1 (R, `libs/utils`), W5 (H, `libs/ingestion`), W3 and W3b (R and H, the formula check and its attacks), W4 (R), W12 (R, a document), W16 later. W10 (H, the engine reader) can also start now: it does not depend on the names.
3. **After W1 is committed:** W6 (H) and W2 (R) can start; W6 is the long item and is split by action family so that parts can be reviewed. W2 can work with fixture registries until W6 has produced the real ones.
4. **After W6 and W5:** W7 (R, run A), then W8, then W11 and W13.
5. **After W7 and W6:** W9 (run B). W15 can start after W7.
6. **Last:** W14 (Blueprint), then the cache bump and the release check.

**What the HOME session can start in parallel once Eve says go:** W0 (already started), W3b (attacks written first), W5, W10, and W6 as soon as R has committed the `rules` interface of W1 (a small first commit, the same day). **What the recipe session starts at once:** W1, W3, W4, W12, then W2.

## 4. Models at a glance (for Eve to set)

| Model | Items |
|---|---|
| `opus/high` | W12 (ADR-100), W15 (science review), the text of the rule files in W13, the attack design of W3b |
| `sonnet/high` | W1, W2, W3, W3b, W5, W6, W7, W9 (both sides), W10, W14 |
| `sonnet/medium` | W0, W4, W8, W11 |
| `sonnet/low` | W13 (documentation), W16 |
| `haiku/low` | the cache-version bump at the release; any mechanical sweep of a name |

## 5. Rules that apply to every item

Tests first, and each test must be able to fail (break the code once and see it fail). Every change that could alter a table is measured against W0 and listed to Eve; nothing is accepted silently. A commit names its files; `git status` is read before staging. No change of a rule file without Eve's confirmation. Each finding is registered as a GitHub issue; an issue is closed when its item is done.
