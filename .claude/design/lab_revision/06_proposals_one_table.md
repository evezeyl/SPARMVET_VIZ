# TESTLAB-REVIEW-1, step 4: the four viewpoints in one table

Written 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396: "TEST_LAB: a review to plan its rebuild (fallback task, the same kind as BLUEPRINT-REVIEW-1)"). It sums up the four proposals of step 4; it builds nothing and decides nothing. The viewpoints recommend; the owner decides.

Sources (same folder): `06_panel_brief.md` (the question and the four approaches), `06_proposal_scientist.md`, `06_proposal_architect.md`, `06_proposal_developer.md`, `06_proposal_user.md`; their probe scripts are in `prior_work/probes_step4_2026-11-21/`.

The four approaches of the brief:

- **A.** A small, safe toolbox for every user: reformatting, anonymisation and reproducible synthetic data, each writing a file plus a record of its settings and seed; shown in the scientist setups; recipe-making moves to BLUEPRINT or to scripts.
- **B.** A file-preparation companion to a chosen recipe: the Test Lab checks or reshapes files against the recipe's declared fields, makes synthetic data from them, and reconciles ids on its keys.
- **C.** Today's tools repaired, with working hand-offs: the scaffold writes a loadable recipe with a first plot; still developer-only; the three ideas wait.
- **D.** The Test Lab as the recipe starter: scaffold, tool-specific recipes from per-tool fragments, format detection, extraction of a pilot recipe; it reports what recipes share; BLUEPRINT edits.

Labels: **read now** = I re-read the cited line on 2026-11-21 in this worktree (branch `task/lab-review`, equal to `dev` `4e8c151e` for these files); **as reported** = as the viewpoint gave it, not re-read or re-run by me; **ran (viewpoint)** = the viewpoint ran it with its probe; I did not run it again. Short names: `H` = `app/handlers/test_lab_handlers.py`, `AN` = `libs/test_lab/src/test_lab/anonymiser.py`, `AQ` = `.../aqua_synthesizer.py`, `SC` = `.../scaffolder.py`, `BS` = `.../bootstrapper.py`, `CORE` = `libs/id_reconciliation/src/id_reconciliation/core.py`, `DI` = `app/handlers/data_import_handlers.py`, `ING` = `libs/ingestion/src/ingestion/ingestor.py`.

---

## Flagged first

What changes a result silently, hides a step from the user, or reconsiders a decision. Each item names the Test Lab tool.

### Changes a result silently

| # | Tool | What | Evidence | Label |
|---|---|---|---|---|
| F1 | Anonymisation, pattern "hash" | The new id is the first 8 hexadecimal characters of an unsalted SHA-256 of the id. Two different ids can get the same new id, with no message: the scientist found 3 collisions in 200,000 ids and one pair (`S8597`, `S18230`) merged into `A_9D4AE85D`. | `AN:39` (`_HASH_PREFIX_LEN = 8`), `AN:46-48`; scientist R1 | the code: read now; the collisions: ran (viewpoint) |
| F2 | Anonymisation, pattern "hash" | The hash can be reversed by guessing: an id of a known shape (`ISO-2023-0417`) was found again by hashing 10,000 candidates. A hash of an id is a pseudonym, not anonymous. | scientist R2 | ran (viewpoint) |
| F3 | Anonymisation | The key (the mapping back to the real ids) is in the same ZIP as the anonymised table; the button says so only in its label. | `H:717` ("Download ZIP (anonymised + mapping + config)"), `H:824-829` (every written file into one ZIP) | read now |
| F4 | Anonymisation, pattern "sequential" | The same ids in another row order get other new ids; two files anonymised one after the other give the same sample two new ids. | scientist R3 | ran (viewpoint) |
| F5 | ID reconciliation | The engine's default fuzzy cutoff is 70, and the screen uses the default. At that cutoff different samples match: `ISO-1` to `ISO-10` (0.91), `Sample_A12` to `Sample_A21` (0.90). | `CORE:28-31` (`fuzzy_cutoff: float = 70.0`); `H:185` (`IDReconciliationEngine()`); scientist R5 | the default and its use: read now; the false matches: ran (viewpoint) |
| F6 | ID reconciliation, the cleaning step | The step written for the matches acts on the whole column and changes ids that already matched as they were. Recorded as a strict expected failure. | `libs/id_reconciliation/tests/test_suggested_steps.py:105-112`; step 1 run, case C | read now; run in step 1 |
| F7 | Synthetic data | The screen calls the generator with no seed, so the same settings give another file next time; and when a seed is given, the generator sets the random state of the whole app process (`np.random.seed`, `random.seed`), which changes every other random draw in that process. | `H:639` (`synth.generate(config)`); `AQ:84-86` | read now; the effect on the process state: ran (scientist R7, architect 1.2) |
| F8 | Recipe scaffolding | A numeric-looking sample id is declared `Int64` (against D-0225: "The sample id is a string or a categorical, never a number"). | `BS:41-48` (`_map_dtype` returns `"Int64"`), `SC:154` | read now; run in step 1 (cases A, B) |
| F9 | Recipe scaffolding | The entity key is set from the column name (`id`, `sample_id`, `isolate_id`), not from the user's choice (against D-0082: "Keys are declared in the recipe"); an empty key box gives `sample_id` with no word. | `SC:158-159`; `H:421-424` | read now |
| F10 | Recipe scaffolding | Every table is inner-joined to the first on the key: rows without a partner are dropped with no word. | `SC:177-189`; step 1 (`03` item 7) | as reported |
| F11 | File reformatting | Unticking every sheet gives all sheets; an Excel sheet keeps Excel's cell types (an id `007` typed as a number may become `7`; not run). | `H:979` (`... or None`); `02` section F | `H:979` read now; Excel types: as reported, not run |
| F12 | Approaches B, C, D themselves | B's "reshape to fit the recipe", D's "format detection" and C's "first plot" or join in a scaffold each choose for the user unless every change is shown with a count and confirmed (all four viewpoints). | scientist section 10 item 6-7; architect 3.B, 3.C; developer 3.B | as reported |

### Hides a step from the user

| # | Tool | What | Evidence | Label |
|---|---|---|---|---|
| H1 | Anonymisation | The id column is renamed `anon_<column>` and moved first; the screen does not say so, and a recipe that declares the old name will not find it. | `AN:119-120`, `AN:304-310` | read now; the refusal by HOME: reasoned, not run (`04` V4) |
| H2 | ID reconciliation | Fuzzy matches are not written as steps and the screen does not say so. | `03` item 14 | as reported |
| H3 | Synthetic data | No list of the planted errors is returned; the user cannot tell what the test covered. Planted type errors are refused at ingestion and never reach the recipe's steps. | architect 1.2 (`AQ:220-300`; a run of `apply_declared`) | as reported; the refusal: ran (viewpoint) |
| H4 | Synthetic and reformatted files in HOME | Once HOME's Data Import has copied a Test Lab file over a recipe's data file, nothing marks it as synthetic (see "Found on the way, about HOME"). | architect 3.A cons | reasoned (viewpoint) |
| H5 | Recipe scaffolding | The status line says "Download the ZIP and open in BLUEPRINT to continue"; BLUEPRINT cannot open it. | `H:509-510` | read now (the line); BLUEPRINT's upload: `04` J5 |

### Reconsiders a decision (or a record)

| # | Approach | What | Evidence | Label |
|---|---|---|---|---|
| R1 | B, D | The Test Lab would read a recipe. This reverses "the choice of 2026-11-08" that "Test Lab tools don't operate on an open data analysis recipe". That choice was found only as a docstring of the Info panel, `app/handlers/home_theater.py:1955-1960` ("Eve, 2026-11-08: deliberately distinct from data_analysis_recipe_info ..."), with no ledger line and no ADR (the ledger lines that name the Test Lab are D-0048, D-0271, D-0381, D-0396; none is on this). **To confirm, not a decision of record.** The architect adds that the comment is about an OPEN recipe in HOME's Info panel, while B reads a recipe the user CHOOSES for one run. | `home_theater.py:1955-1960`; grep of the ledger | read now |
| R2 | D; ideas 1 and 3 | Recipe authoring in the Test Lab presses D-0102 ("full recipe edit exists only in Blueprint") and D-0306 ("Blueprint is the UI IDE for building the recipes and must be able to build the WHOLE recipe"). | ledger lines read now | read now |
| R3 | A (and B, C) | Anonymisation in the app for scientists puts real personal data and the key into the running app. ADR-097 point 8 (a record, not a ledger line) recommends "anonymisation before data ever reaches the app, with any de-anonymisation key kept outside it entirely". | `architecture_decisions.md:4991-4995` | read now |
| R4 | A | Moving the scaffold to "BLUEPRINT or scripts" settles, by the side, BLUEPRINT's own first open choice (how a table enters a recipe); until BLUEPRINT is rebuilt a scientist would have no screen path from files to a first recipe. | architect 3.A; BLUEPRINT review `04` To decide #1 | as reported |
| R5 | B | Listing file columns that the recipe does not declare would do BLUEPRINT's job: D-0374, "Informing about undeclared file columns belongs to the user space BLUEPRINT." | ledger line read now | read now |
| R6 | all | Applying D-0056 ("every seed that is used is written in the recipe or the audit recipe") to Test Lab files is a reading of the viewpoints: D-0056 is about recipes. | ledger line read now | read now |
| R7 | C | "Still developer-only" fixes the audience before the owner has said it; her words say "a set of utilities for the user" (`ORDER.md`). | `ORDER.md`; flags in `04` section 6 | read now |
| R8 | A, C | Amends records: ADR-084 point 4 and `rules_test_lab.md` section 3 (the record would take the place of the synthetic config header); ADR-084 point 6 (the scaffold leaves, in A); the flag matrix of `rules_app_features_flags.md` (flags per tool). | architect section 4; developer section 7 | as reported |

---

## Found on the way, about HOME

Two findings of the architect concern HOME's Data Import panel, not the Test Lab. They are recorded here because every Test Lab file headed for HOME passes through that panel. **The coordinator is verifying them separately**; this review does not fix or file them.

| # | What | Evidence | Label |
|---|---|---|---|
| X1 | HOME's Data Import and the engine's ingestor disagree on which column headers a file must have when a recipe uses `original_name`. Data Import checks the declared slugs (`MetadataValidator.validate` compares the contract's keys with the file's columns); the ingestor looks for each field's `original_name` (the slug when none is given). On `config/data_analysis_recipes/templates/simple_template.yaml` (fields `sample_id` with `original_name: ID`, `value` with `Measurement`, `group` with `Group`), a file with headers `ID, Measurement, Group` is refused by Data Import and accepted by the ingestor; a file with headers `sample_id, value, group` is accepted by Data Import and refused by the ingestor. | `DI:315-316`; `libs/transformer/src/transformer/metadata_validator.py:30-31`; `ING:109-117`; `simple_template.yaml:22, 26, 30`; architect `arch_check5.py` | the code lines: read now; the two outcomes: ran (viewpoint), not run again, not seen in a browser |
| X2 | Data Import copies the accepted file over the recipe's data file (the `source.path` of the table) with no check that a file is there and no backup. | `DI:326-337` (`target = Path(source_path)` at 328, `shutil.copy2(tmp, target)` at 336) | read now |

---

## The table: approach by viewpoint

Evidence as the viewpoint gave it. Sc = scientist and data scientist, Ar = architect, De = developer, Us = user who is not a developer.

| Approach | Viewpoint | Pro | Con | Evidence |
|---|---|---|---|---|
| A | Sc | Every tool is a transformation that can be written in one methods sentence with its record; nothing reads or writes a recipe, so D-0102, D-0082, D-0050, D-0015 and ADR-097 point 8 stay intact. | "Correct format" stays a TSV; the user learns at HOME that it does not fit. Each tool must first be made safe for a non-developer (hash, collisions, crashes). | R1 to R8 of the scientist (ran); `DI:273-315` (read by the viewpoint) |
| A | Ar | Smallest change that makes her two examples true; tools stateless (ADR-084 point 1); one record shape for all tools; no reversal. | ID reconciliation has no place and no reader; moving the scaffold decides BLUEPRINT's open choice by the side; anonymisation in the app against ADR-097 point 8; a synthetic file is not marked once HOME copies it. | `H:366-401` (read-1); `wrangle_studio.py:225-226`; architect 1.1 to 1.3 (ran, read) |
| A | De | Small, independent parts, testable without a browser once logic leaves the handler; no second recipe reader; reverses nothing. | The removal of the scaffold (about 215 lines of handler, 415 of libs, 73 tests) is medium and is a half fix if done before BLUEPRINT accepts a table; ID reconciliation loses its consumer. | `wc -l`, `grep -c "def test"` (verified by the viewpoint) |
| A | Us | One sentence and one picture: "each tool gives you a file and a note of what was done". Removes the two worst traps (the ZIP nobody can open, synthetic data nobody can make again). | Hidden from the user: that BLUEPRINT now makes recipes. | `H:509-510`; `04` J2, J5 |
| B | Sc | Synthetic data from the recipe's declared fields is the strongest valid test of that recipe; the key comes from the recipe (D-0082). | Reverses the 2026-11-08 comment (R1); "reshape to match" is a choice made for the user (D-0015) unless every change is confirmed and counted; a shape check can be heard as "the science is right". | scientist section 3.B (reasoned) |
| B | Ar | The only approach where "the correct format" has one source of truth (the declared fields as the ingestor reads them); forces the HOME fix that is needed anyway; the library can stay recipe-free (the handler passes the fields). | Couples every tool to the recipe format; depends on the recipe places study (D-0394) or a recipe upload; double cleaning if the Test Lab applies `strip` and the null words; D-0374 (R5). | `utils.recipe_loader.load_recipe` (ran, `arch_check3.py`); `RecipeGraph.key_families` (read `recipe_graph.py:395,426`) |
| B | De | The check already exists outside Shiny's logic and can be extracted once (F-4), so B's extra part is cheap on A's foundation. | Large and high-risk as a whole: a second reader of recipes; synthetic data from field types tests the loader, not the science, and is easy to over-trust in a methods section. | `DI:278-319` (verified by the viewpoint) |
| B | Us | "Pick your recipe, and the tools adapt to it": what a scientist most wants ("is my file right for my recipe?"). | False comfort: a pass may be read as "the science is right"; the rule used is hidden. | `04` J1 |
| C | Sc | The repairs are needed under every approach. | Still developer-only; a first plot chosen by the Test Lab (D-0015); three recipe writers stay; no record unless the record is added. | scientist section 3.C |
| C | Ar | The least that makes today's tools honest; the scaffold fix survives a later move (its logic belongs in `utils`). | Keeps five recipe writers (a half fix unless the others are removed); leaves the format question (X1) open; writes into a recipe place whose rules are open (D-0390, D-0392, D-0394). | architect 1.3 (five writers, read) |
| C | De | Lowest risk; the scaffold's move to `recipe_factory` and the flip of the strict xfail tests are known work. | About 35 defects of `03`, each small; a fix of the scaffold with an inner join kept is a half fix by order. | `03` section 2; `test_suggested_steps.py:87-112` |
| C | Us | Nothing new to learn. | Scientists still see no Test Lab: "half a fix" from the user's seat. | flags, `04` section 6 |
| D | Sc | A new user starts with the known fields of a tool. | Format detection by column names is a guess; a tool recipe must carry the tool version or the figure changes meaning silently when the tool changes its columns; a cut-out recipe can give other rows than its parent; a shared fragment couples two recipes. | scientist section 3.D (reasoned) |
| D | Ar | Uses what the app already knows (per-tool fragments, the recipe graph, the branch plan). | Recipe authoring in the wrong space (D-0102, D-0306); a list of known formats goes stale; three decisions outside the Test Lab (places, plot ids X5, share or copy). | `config/.../1_test_data_ST22_dummy/input_fields/`; `utils/recipe_check.py:1287-1296` (read by the viewpoint) |
| D | De | Idea 2 alone is small to medium. | Largest and highest risk; a new store of known formats (none in code); must wait for BLUEPRINT's rebuild. | `05` sections 2 to 4 |
| D | Us | Fast start for a recipe author. | "The Test Lab starts your recipe" is too much for a utility; joins and keys chosen for the user (D-0082, D-0225). | user, "One sentence and one picture" |

---

## Where the four agree

- **A is the base.** All four recommend A as the core.
- **A record beside every file.** Every file a Test Lab tool writes carries a record: the tool and its version, the date, the user's real input file name (not Shiny's upload number), every setting including defaults, the seed, counts before and after, what the tool did that the user did not choose, and, for synthetic data, the list of planted errors. All four put it first or second; the scientist and the architect say it is needed whatever approach is chosen.
- **A seed that is shown and written**, and a generator that uses its own random generator, not the state of the whole process (scientist, architect, developer).
- **The key as a separate download**, with a plain line that it brings the real ids back (all four).
- **Fuzzy matches are a list a person confirms**, never a rule (scientist, developer, user).
- **The three ideas are not Test Lab writers.** Idea 2 is a template or a documented chain; ideas 1 and 3 belong to BLUEPRINT; the Test Lab may at most report what two recipes share (all four).
- **D waits** for BLUEPRINT's rebuild and the recipe places study (all four).
- **The removal of "open the ZIP in BLUEPRINT"** until BLUEPRINT can open it (user; architect and developer by implication).

## Where they differ

| Point | Sc | Ar | De | Us |
|---|---|---|---|---|
| B's recipe-aware part | later, check and report only, never rewrite; only if she accepts the reversal | an optional second step, on ONE check function shared with HOME's Data Import; the reversal is smaller than said (R1) | only if she reverses 2026-11-08; the shared check (F-4) is built anyway as part of the foundation | later, flagged step |
| The scaffold now | leaves the Test Lab (recipe-making is not its job) | stays developer-only and unchanged except for the common contract, until BLUEPRINT's choice exists | not removed until its new home exists; if kept, C's fixes are the same work | if kept: "a starting draft", no guessed key |
| First thing to decide | what every output carries (the record) | what "the correct format" means, one definition, and the HOME fix | who sees the Test Lab (flags) | who sees the Test Lab |
| The HOME check disagreement (X1) | not found | found and run; ranks it first | not named (names the extraction of the check) | not named |
| Anonymisation in the app | defensible only as random labels with the key kept apart; never call it "anonymised" | CONFIRM against ADR-097 point 8; option: a local script, in-app only for local deployments | warning and separate download; only the owner can say whether the key may be made in the app | two downloads, not a stronger warning |

## The combination each recommends

- **Scientist:** A as the base, plus B's check-only part later (report, never rewrite), D moved out; C's repairs are inside A.
- **Architect:** A as the base (its contract T1 to T7 for every tool), plus B's recipe-aware check and synthetic data as an optional second step, built on one extracted check function that HOME also calls; not C as written; not D now.
- **Developer:** A, on a common foundation built first (the record, logic out of the handler, a local random generator with the seed written, the extracted check, realistic test files); the scaffold kept until its new home exists.
- **User:** A, with a plain-text record of what was done in every download.

## Gaps in approach A that three viewpoints name

1. **No reader left for ID reconciliation.** Its output (`id_transformation.yaml`) has one consumer today, the scaffold's "Bake in ID Reconciliation steps" (`H:366-401`, as reported); A moves the scaffold out. Options named: keep it as a report plus a steps file with a defined reader (BLUEPRINT), or a tool that writes a recoded file (a new behaviour that changes ids, so counts and the record are mandatory). Named by the architect, the developer, and the scientist (who keeps the tool but writes each accepted pair to the record).
2. **No screen path from files to a first recipe** until BLUEPRINT's table entry is rebuilt (BLUEPRINT review, To decide #1), only scripts (`assets/scripts/create_data_analysis_recipe.py`). Named by the architect, the developer and the user.
3. **Real personal data entering the app**, against the recommendation of ADR-097 point 8, if anonymisation is shown in the scientist setups. Named by the scientist (the key in the same ZIP), the architect (CONFIRM) and the developer (only the owner can settle it); the user asks for two downloads.

## Not verified (by this file)

- I re-ran no probe. Every "ran (viewpoint)" is the viewpoint's run; the scripts are in `prior_work/probes_step4_2026-11-21/` and read their paths from the main tree root.
- Nothing was seen in a browser by any viewpoint.
- The collision rate and the "1 in 86 for 10,000 ids" are the scientist's (one run and a birthday approximation).
- The effort sizes are the developer's, reasoned from line and test counts.
