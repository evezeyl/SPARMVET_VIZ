<!-- copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/developer.md of the main tree (not in git; written 2026-11-21 night, step 4 of TESTLAB-REVIEW-1); a viewpoint's proposal: it recommends, it decides nothing -->
# Test Lab step 4: DEVELOPER viewpoint (2026-11-21)

Reads: BRIEF, ORDER, `04` (sections 2, 4, 6, To decide), `05` (section 5, To decide), `02` K and M, `agent_principles.md`, `decision_compliance.md`. Checks run now (read-only): line counts, `def test` counts, grep of `test_lab_enabled`, `aqua_synthesizer.py` RNG calls, `data_import_handlers.py:265-340`, `recipe_factory.py` function list. Labels: verified (file:line or command), reasoned, assumed.

## Summary

1. I recommend approach A as the core, with one foundation built first: a shared "record" (what was done, settings, seed, real input names, app version, row counts) written beside every file the Test Lab makes. Every approach needs it; A needs nothing else new.
2. B's extra part (check a file against a recipe's declared fields) is cheap to add later on A's foundation, because the check already exists as a function outside Shiny (`MetadataValidator.validate` plus `apply_declared`, `data_import_handlers.py:278-319`, verified). It should be extracted once and shared by HOME Data Import and the Test Lab. B reverses the choice of 2026-11-08 (flagged); build it only if she reverses it.
3. C is the lowest risk but leaves two things: the order's words "for the user" (flags) and the recipe-writing path with its defects (it keeps the scaffold's join, inner-join row drops, and so on).
4. D is the largest and highest risk: it needs a list of known tool formats (a new store, none in code), BLUEPRINT's recipe edit ground (D-0102, D-0306) and the open recipe places study (D-0394). Do not start it before BLUEPRINT's rebuild.
5. The ordering problem nobody has named: ID reconciliation's only consumer today is the scaffold ("Bake in ID steps", `H:366-401`, read-1). If the scaffold leaves the Test Lab (A), the reconciliation output has no reader. This must be decided with A, not after it.
6. Not verified: nothing was seen in a browser or run through Shiny; no test was run.

## 1. Facts I checked that the build depends on

| Fact | Evidence | Why it matters to a build |
|---|---|---|
| The synthetic generator uses the process-wide random state of both `numpy` and `random` (`np.random.seed`, `random.seed` at `aqua_synthesizer.py:84-86`; global calls at lines 204-217, 235, 250, 264-275, 299, 323-356) | verified, grep | A seed is only reproducible inside one process and one thread. Shiny serves several sessions from one process; two users generating at once can change each other's file, and `np.random.seed` also changes other code. A real fix is a local generator (`numpy.random.default_rng(seed)` plus `random.Random(seed)`) passed through every method: a rewrite of one 462-line file and its 21 tests. Old seed 42 outputs change; nothing stored depends on them (reasoned) |
| The generator returns the table only; planted errors are not listed (`generate` returns `df`, lines 77-104) | verified | "Planted errors" prove something only if the test can say which cells were damaged. Needs a returned list (kind, column, row). Without it the user cannot tell whether the recipe caught the error |
| The error injection acts after the columns are made and uses the same random stream | verified, lines 98-100 | Adding the list does not change the seed meaning if done in the same order; a test must pin it |
| HOME Data Import already validates a file against a table's declared fields with `MetadataValidator.validate(lf, input_fields)` and `apply_declared(...)`, reading all columns as text first | verified, `data_import_handlers.py:278-319` | The check B wants exists. It sits inside a Shiny handler; to share it, extract a function into a lib (no Shiny). One way per job |
| Five Test Lab libs plus `id_reconciliation`: about 1,400 lines in `libs/test_lab/src`, 265+117 in `id_reconciliation`, 1,007 in `H`, 131 in `S` | verified, `wc -l` | `H` is the biggest and least testable part (one handler file, no Shiny-free layer). Every approach is cheaper if the logic of each tool leaves `H` first |
| Tests (def count): `test_lab` 111 (anonymiser 22, scaffolder 24, synthesizer 21, reformatter 20, bootstrapper 18, extractor 6), `id_reconciliation` about 56, `app/tests/test_id_cleaning_steps_reach_a_recipe.py` 16 | verified, grep -c | Scaffolder and bootstrapper tests use file names and text ids that hide the upload-name and `Int64` defects (read-1, `04` V9). They must be adapted before the code, or they pass a wrong scaffold |
| `test_lab_enabled` is read in 6 places (`server.py:122,191`, `home_theater.py:1068,1835`, `sidebar_registry.py:92,99`, `sidebar_validator.py:28`, `app_features_validator.py:20`); true only in `developer.yaml` (and `qa`) | verified, grep | One flag now. A per-tool flag or a "show in scientist setups" choice touches the validator, the sidebar registry, the setup YAMLs, `rules_app_features_flags.md` and CONFIG-REVIEW-1. Small to medium, mostly mechanical, with tests of the validator |
| `recipe_factory` has `minimal_schema`, `minimal_join`, `minimal_plot`, `minimal_recipe`, `write_recipe`, `write_fragment` (default plot unless `plots={}`) | verified, `recipe_factory.py:64-211` | A loadable first recipe has one writer already. The scaffolder (217 lines) and bootstrapper (198 lines) build dictionaries themselves (read-1) |

## 2. The common foundation (needed by every approach)

These are independent of the choice of A to D and should come first. They are the part of the work with the least regret.

| # | Part | Effort | Risk | Tests needed |
|---|---|---|---|---|
| F-1 | The record: one small function in `test_lab` (no Shiny) that writes a plain record file next to every output: tool, app version or commit, date, the real input file names (not the upload number), settings, seed, row and column counts, the planted-error list. One format for all tools | small | low; a wrong record misleads, so the content is tested, not only the presence | the record of each tool names the real file; same settings and seed give the same record; the record is in the ZIP and in a single download |
| F-2 | Logic out of `H` into libs, tool by tool, with `H` calling it (the screen keeps only reading inputs and showing results) | medium (1,007-line handler) | medium: a move can drop a message; the handler tests are few | each moved function gets its edge cases (empty, corrupt, nothing to do); break once and see it fail |
| F-3 | Synthetic generator on a local random generator, seed always written (a blank seed gets a drawn seed that is shown and recorded; never silent), list of planted errors returned | medium | medium: output of a given seed changes; global-state leak is removed | same seed same file; two interleaved generations (two threads) give independent files; the planted list matches the damaged cells; each of the six error kinds |
| F-4 | A shared "file against declared fields" function, extracted from `data_import_handlers.py:278-319` into a lib (`transformer` or `ingestion`), used by Data Import first | small to medium | medium: HOME Data Import is a decided panel; the extraction must change no message | Data Import tests unchanged and green; new tests of the function: a wrong type, a missing column, an extra column, a numeric-looking id (D-0225) |
| F-5 | Real-world test fixtures: Shiny-style upload names, Excel with `007` stored as a number, a comma-decimal file, an empty id | small | low | these are the tests; they replace the ones that hide defects |

F-4 matters beyond B: the same function lets the Test Lab tell the user, at the moment of the choice, what HOME will say to the file (informing, D-0015), without making the Test Lab read a recipe by itself (it takes the declared fields as input).

## 3. The four approaches

### A. Small safe toolbox (reformat, anonymise, synthetic), each with a record and a seed

| Item | Assessment |
|---|---|
| What the user sees, per journey | J1 reformat: counts, delimiter shown and chosen, a record. J2 synthetic: seed shown, settings saved, list of planted errors, a "make it again" input. J3 id reconciliation: undefined in A (see below). J4 anonymise: several files, key kept apart, warning that the table and mapping must not travel together. J5 recipe: no longer in the Test Lab |
| What exists | The libraries for all three tools (reformatter 175 lines, anonymiser 360, synthesizer 462), `save_config`/`load_config`/scenarios in the synthesizer (verified `aqua_synthesizer.py:106-133`), `anonymise_batch` (read-1) |
| Must be extended | F-1 to F-3; anonymiser: empty-id crash (run-1 case F), renamed key column stated or kept, salt or no hash, the mapping written to a separate download; reformatter: counts, no silent "all sheets" |
| Missing | A consumer for ID reconciliation output; a home for the scaffold (BLUEPRINT or script) |
| Effort | medium to large in total, but in small independent pieces; the removal of the scaffold (about 215 lines of handler, 415 lines of libs, 42 tests, plus the "Bake in" path and 31 more tests) is medium and must leave a tombstone (rule: a removal leaves a tombstone) |
| Risk | low for the three tools. Medium for the removal: it can leave a Test Lab with no way to make a recipe before BLUEPRINT can accept a table (BLUEPRINT review To decide #1). A removal done before that is a half fix |
| Silent-change risks | Reformatter on Excel keeps Excel's cell types (number ids, leading zeros lost) unless it reads as text like Data Import does (`data_import_handlers.py:~290`, `cast(pl.String)`); a hash that is shown as anonymous but is unsalted and reversible by guessing |
| Asks of BLUEPRINT / HOME | HOME: nothing new (Data Import takes the TSV). BLUEPRINT: a way to start from data files and a way to read ID steps; this is the BLUEPRINT review's choice, outside this one |
| Larger decisions first | who sees it (flags); what happens to ID reconciliation; where recipe-making goes; what the record contains |
| Can wait | the other four error kinds; several tables from one set of ids; named scenarios on screen |

Pitfall specific to A: "recipe-making moves to BLUEPRINT or scripts" removes the Test Lab's only journey that is not safe for a non-developer. That fits "shown in the scientist setups" but it makes ID reconciliation a tool with no output consumer. Options for the owner: keep ID reconciliation as a report plus a transformation file with a defined reader (BLUEPRINT), or make it a tool that outputs a recoded file directly. The second is a new behaviour (it changes ids, so the record and a before/after count are mandatory).

### B. File-preparation companion to a chosen recipe

| Item | Assessment |
|---|---|
| What the user sees | Picks a recipe; per table, a check of a file against the declared fields with plain messages; a reshaped file; synthetic data from the declared fields with planted errors; ids reconciled on the recipe's declared keys |
| What exists | The check (F-4), the recipe graph (`recipe_graph.py`, no file read), the key declared in the recipe (D-0082), the synthesizer (needs rework) |
| Must be extended | F-1 to F-4; a recipe chooser (needs the recipe place, D-0394 open); a generator from declared fields: declared types only give type-correct values (no value ranges, no categories unless the recipe lists them): a synthetic file from field types tests the loader, not the science; several tables with one set of ids (D-0205, the demo script says the generator cannot do this, `generate_demo_data.py:16-18`) |
| Missing | Everything about reading a recipe in the Test Lab; the decision that reverses 2026-11-08 |
| Effort | large |
| Risk | high: it makes the Test Lab a second reader of recipes (two readers can disagree); synthetic data from declared fields is easy to over-trust (a user may defend "tested on synthetic data" in a methods section when only the loader was tested) |
| Silent-change risks | A reshape "to match the recipe" (renaming, retyping) is a choice made for the user unless every change is listed and confirmed; an id reconciliation by the declared key can write steps that break other matches (run-1 cases C, D remain until fixed) |
| Asks of BLUEPRINT / HOME | HOME: the same check, shared (F-4). BLUEPRINT: none, but the recipe it saves must be readable by the Test Lab |
| Larger decisions first | reverse 2026-11-08 or not; recipe place (D-0394); what "valid synthetic test" means |
| Can wait | all of it except F-1 to F-4, which it shares with A |

### C. Keep today's tools, fix the defects, make hand-offs work

| Item | Assessment |
|---|---|
| What the user sees | The same screens with fixes: scaffold writes a loadable recipe with a first plot through `recipe_factory`; ZIP to the user's own recipe place; developer-only |
| What exists | All code; the script `create_data_analysis_recipe.py` already writes a recipe with a first plot via `recipe_factory` (read, `04` 3.7) |
| Must be extended | The scaffold to use the factory (medium: replace its dictionary builders, adapt 24 + 18 tests); key chosen by the user (D-0082); table names from the real file names; relative data path; ID cleaning step that does not break matches (strict xfail tests exist, `test_suggested_steps.py:87-112`: flip them to normal when fixed); F-1, F-3; anonymiser fixes |
| Missing | A decision on the user's own recipe place (D-0394 open); the flag question (stays open) |
| Effort | medium to large (about 35 listed defects in `03`, each small; the scaffold and ID-step fixes are the larger ones) |
| Risk | low to medium. Danger: a half fix by order: fixing the scaffold while the join stays inner (K1) keeps a silent row drop |
| Silent-change risks | The scaffold's inner join (rows with no partner vanish); fuzzy matches left out of the steps without a word |
| Asks of BLUEPRINT / HOME | A file that BLUEPRINT's upload reads (one `.yaml`) or a ZIP route; HOME has no recipe upload on screen (`file_ingest` is not made by any UI, read-1) |
| Larger decisions first | recipe place; join in the scaffold or `joins: {}`; first plot or draft profile |
| Can wait | the three ideas (as stated) |

C leaves two recipe writers (scaffolder, bootstrapper) plus the factory and two scripts. That is not "one way per job"; a clean C also removes or merges them (add to its effort).

### D. Recipe starter (scaffold, tool-specific recipes, format detection, pilot extraction, report of shared parts)

| Item | Assessment |
|---|---|
| What the user sees | Files in, a recipe out, recognised formats named ("looks like ResFinder output"), a smaller recipe cut from a large one, a report of what recipes share |
| What exists | Recipe graph with lineage queries, `build_plot_lineage`, export's frozen recipe, branch plan, factory, per-tool fragments in `1_test_data_ST22_dummy/input_fields/` (read, `05` 2.2 and 3.2) |
| Missing | A list of known tool formats (none in code, `05` 4.2); a cut-out writer; share-or-copy rule for fragment files; plot-id rule across recipes (checker X5); recipe place (D-0394) |
| Effort | large (idea 3), medium (idea 1), small to medium (idea 2) |
| Risk | high. A shared fragment edited for one recipe changes another recipe's result silently; a format guess from column names can be wrong and must be shown with its reason and be overridable; it is recipe authoring, which D-0102 and D-0306 put in BLUEPRINT |
| Silent-change risks | Share against copy of fragment files; the same table id or plot id in two recipes; a guessed entity key (D-0082) |
| Asks of BLUEPRINT / HOME | BLUEPRINT must open the produced recipe and probably do the combining; HOME must load it |
| Larger decisions first | the three ideas wanted or not (their order: 2, 1, 3 by size); where recipe-making lives; share or copy; known formats list |
| Can wait | all |

## 4. Where the three recipe ideas belong (build view)

| Idea | Size (build) | Depends on | Build condition |
|---|---|---|---|
| 2 tool-specific | small to medium (templates per tool from existing fragments, plot ids checked once with the checker X5) or a documented chain "reformat a sheet, then scaffold" (no build) | recipe place and names (D-0390 to D-0394) if shipped | After the foundation; the documented chain needs nothing |
| 1 pilot extraction | medium: a writer on top of `recipe_graph.py` and `recipe_factory.py` | share or copy; X5; places | After BLUEPRINT's rebuild; test: the cut-out recipe gives the same rows for its plot as the full recipe (a strong, simple property test) |
| 3 combine | large | joins, keys, names, sessions | A report-only version (what two recipes share, which plot ids clash) is medium and safe; the combined recipe waits for BLUEPRINT |

I could not verify that the recipe graph works on two recipes at once (`05` Not verified; not run).

## 5. Recommendation

One approach: A, built on the foundation of section 2, with the scaffold not removed until its new home exists (BLUEPRINT accepts a table or a script is the declared one way). Reasons (build only):
- Its parts are small, independent, and testable without a browser once logic leaves `H` (F-2).
- It fixes the three broken decided rules (id as number, guessed key, silent changes) by taking out the tool that breaks the first two (the scaffold) and fixing the third in each remaining tool.
- It adds no second recipe reader and reverses no decision.
- B's extra part is then a small addition (F-4 exists), and D waits for BLUEPRINT.
Risk: A as written does not say what ID reconciliation becomes; if the owner wants it kept, its consumer is a decision to take together with A.
If she prefers not to remove the scaffold now, C's scaffold fixes are the same work as the "move" would be, minus the removal; the foundation F-1 to F-5 is still first.

## 6. Build order

Tags follow CLAUDE.md section 2 (haiku/low mechanical; sonnet/low single-file; sonnet/medium multi-file in a pattern; sonnet/high new module or cross-file refactor; opus/high design; opus/max new space design). Planning only; nothing here is started.

| Step | What | Tag | Parallel? |
|---|---|---|---|
| 0 | Tests adapted to the decided design: fixtures with Shiny upload names, Excel with `007`, comma decimals, an empty id; flip the strict xfails when their fix lands | sonnet/medium | first; alone |
| 1 | F-1 the record (a small library module, one format) | sonnet/medium | with 2 and 3 (own files) |
| 2 | F-3 generator on a local generator, seed recorded, planted-error list (risky logic first) | sonnet/high | parallel to 1, 3 (own file `aqua_synthesizer.py`) |
| 3 | F-4 extract the declared-fields check from Data Import into a lib, no message changed | sonnet/medium | parallel (own files; touches HOME's handler: a reviewer checks the HOME tests unchanged) |
| 4 | Anonymiser fixes (empty id, key, salt, separate mapping, several files) | sonnet/high | after 1; parallel with 5 |
| 5 | Reformatter fixes (counts, delimiter shown, sheets, Excel as text) | sonnet/medium | after 1; parallel with 4 |
| 6 | F-2 move logic out of `H` for each remaining tool, then screens | sonnet/high | after 2, 4, 5 (same handler file: not parallel) |
| 7 | Flags: per-tool or per-setup visibility; validator, registry, YAMLs, rules file | sonnet/medium | after the owner's choice; independent of 4 and 5 |
| 8 | The recipe-making path: remove the scaffold, bootstrapper and "Bake in" (with tombstones) or move them; ID reconciliation consumer | sonnet/high; design of the consumer is opus/high | only after BLUEPRINT's choice of how a table enters a recipe and the decision on ID reconciliation |
| 9 | Screen words, help, Info panel (last) | sonnet/low | last |
| 10 | Rule file `rules_test_lab.md` and ADR-084/097 amendments, UML sync (scribe) | sonnet/medium | after each behaviour merge |

Worktrees: steps 1, 2, 3, 4, 5 touch separate files and can run in separate worktrees; step 6 touches `H` and goes alone. Reviewers check each merge against the decisions of the brief.

## 7. Decided points a proposal could touch (flagged)

| Point | Where |
|---|---|
| Test Lab does not read a recipe (choice of 2026-11-08, a code comment, not a ledger line I found) | B and D reverse it; F-4 does not (the fields are given as input) |
| ADR-084 (tools are stateless; single key; boilerplate only) | A amends point 6 (the scaffold leaves); B amends the stateless wording |
| ADR-097 point 8 (key kept outside the app) | A's anonymiser must not put the key in the same download without a warning; only a decision of the owner can settle whether the key may be made in the app at all |
| D-0102, D-0306 (full recipe edit only in BLUEPRINT) | D and ideas 1, 3 |
| D-0056 (seeds written in the recipe) | applying it to Test Lab files is my reading (also noted in `04` F6) |

## To decide first (ranked)

1. Who the Test Lab is for and how it is shown (flags: developer only, scientist setups, per tool). Everything in the screen design waits for this.
2. Where recipe-making lives (Test Lab, BLUEPRINT, scripts). It decides whether the scaffold, bootstrapper and "Bake in" are repaired or removed.
3. What ID reconciliation becomes and who reads its output.
4. Whether the Test Lab may read a recipe's declared fields (B), or only take them as an input from a shared check (F-4).
5. What every file carries: the record, the seed (shown, never silent), the list of planted errors.
6. Anonymisation: where the key goes and whether a hash is called anonymous.
7. The three ideas: wanted or not, in the order tool-specific, pilot, combine; report-only first for combine.
8. The recipe place (D-0394) for anything that writes a recipe.

What the user must be told to choose well: for each approach, what stays and what leaves the Test Lab; that a synthetic file from declared types tests the loader, not the science; that a record and seed make a result repeatable but a hash of an id is not anonymous by itself; that approach A needs a decision on ID reconciliation and on BLUEPRINT's way in before the scaffold leaves.

## Not verified

- No tool was run; nothing seen in a browser or through a real Shiny upload.
- No test was run; counts are `def test` counts.
- The effort sizes are reasoned from line counts and file touches, not measured.
- Whether Data Import's check refuses type errors or planted errors (`04` V3); whether extracting it changes a message.
- Whether anything outside this repository calls the bootstrapper, the extractor or the synthesizer's command line.
- Whether the recipe graph works on two recipes; whether the export's frozen recipe loads in HOME or BLUEPRINT.
- The code comment of 2026-11-08 has no ledger line that I found; I did not search the ledger for it.
