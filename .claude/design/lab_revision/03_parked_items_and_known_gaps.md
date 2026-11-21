# TESTLAB-REVIEW-1, step 1c: parked items and known gaps

Written 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396). It builds nothing and decides nothing. Labels as in `02_planned_vs_existing.md`: "read" (file:line, read now), "document" (from a text, not re-checked), "run" (one of the two probes of `02`). `H` = `app/handlers/test_lab_handlers.py`.

**Summary.** The Test Lab is parked by the owner's order of work: "Blueprint and Test Lab only where the big recipe change forces it, kept minimal; everything else of them waits until after the demo" (D-0271). What is parked falls in four groups: (1) decisions already put to her and still open (the earlier review's nine questions, three ID-cleaning defects, the empty-key default, the empty draft); (2) design parts that were never built (the confirm-each-match step, multi-file matching, the transformation file with an audit log, the per-column synthetic config, scenarios on screen, several-file anonymisation, the de-anonymising step); (3) defects found by reading or by a run (section 2); (4) texts out of date (section 3). The three ideas of the task (pilot recipe, tool-specific recipe, combined recipes) have no description beyond one line.

---

## 1. Parked items, one by one

### 1.1 The order of work parks the Test Lab

- **Source.** D-0048 ("Order of work HOME, then Gallery, Blueprint and Test Lab last"); D-0271 (quoted above); D-0272 ("The demo comes AFTER the big recipe change."); `tasks.md:621` adds "No Test Lab scaffolding in the demo" (a task line, not a ledger line). The handoff says "Test Lab review: not started." (`.claude/logs/handoffs/handoff_active.md:47`, read).
- **What it means for this review.** The rebuild comes after HOME, GALLERY and the demo; this review prepares it ("also a preparation without details", her words in `ORDER.md`).

### 1.2 The earlier review's fixes and questions wait for her reading

- **Source.** `tasks.md:677`: "review DONE 2026-11-18: `.claude/design/exploration/2026-11-18_test_lab_review.md` (15 fixes in order, 9 questions). The fixes wait for Eve's reading, except the recipe writers' shape (in ENGINE-KEYS step 4). After the demo (Eve, 2026-11-18, D-0271)."
- **State.** The writers' shape was done in step 4c (read: the code writes D-0250 tiers). The other 14 fixes and the 9 questions are open (`02` section L lists which still hold). The nine questions: (1) where the data files go after scaffolding; (2) what the key of a scaffold may be (one column, a pair, a date); (3) does the scaffold write a join; (4) may synthetic data make dates and free text; (5) how the ID cleaning step is written; (6) the hash anonymisation; (7) the Excel extractor; (8) the order (before or after the format change; the format change is now merged); (9) the Info panel text. Each has the worker's default in that file (section 4); none is decided.

### 1.3 Three ID cleaning defects, recorded as strict xfail tests

- **Source.** `tasks.md:222` (ID-RECON-STEPS-1): "DECISION FOR EVE: three defects are recorded as strict xfail tests ... (the delimiter step is always `_` to `-`; the prefix step empties an ID that is not longer than the prefix; a step changes the whole column, also the IDs that matched as they were). The library keeps its own small step language with a bridge (recommended: keep the bridge)."
- **Code.** `libs/id_reconciliation/tests/test_suggested_steps.py:87-112` (read). Two of the three confirmed by a run now (`02` section C, cases C and D).
- **Why it matters.** A recipe written by the scaffold with these steps changes ids that were right, with no message (D-0050: "No silent error: that is the rule").

### 1.4 The silent `sample_id` default of the scaffold

- **Source.** `tasks.md:647` (TESTLAB-EMPTY-KEY-DEFAULT, "waits for Eve").
- **Code.** `H:337-342` (the box pre-filled `sample_id`), `H:421-424` (an empty box or an unreadable input gives `sample_id`) (read).
- **Related.** The scaffold also takes the first uploaded file when the choice of the file for the cleaning steps cannot be read; it now says so (`H:451-460`); the test that guards it says the choice itself "is a choice for Eve, see the report" (`app/tests/test_click_reads_visible.py:7-8`, read).

### 1.5 A recipe with no plot cannot be loaded

- **Source.** `tasks.md:220` (WRITERS-W8-1): "DECISIONS FOR EVE: (1) a new Blueprint draft has no plot, and the app's loader refuses a recipe without a plot, so a fresh draft cannot be opened ...: let the loader accept an empty draft, or make the form create a first plot".
- **For the Test Lab.** Every scaffold has `analysis_groups: {}`; the engine's own load refuses it (run, `02` section B2). The same decision covers both spaces.

### 1.6 The shim `pattern_detector.py`

- **Source.** `tasks.md:452` (PATTERN-DETECTOR-SHIM-1): "Eve's rule: no such in-between files. Fix: remove it and point the callers to the source." The rule file still describes it as the design (`rules_test_lab.md:64, 226`).
- **Code.** `libs/id_reconciliation/src/id_reconciliation/pattern_detector.py` (11 lines, read); also `data_structures.py:5` re-exports `PatternSuggestion` "for backward compat" (its `@deps`, read).

### 1.7 Formula evaluation in the ID reconciliation

- **Source.** FORMULA-SAFETY-1 (`tasks.md:123`): "Option A (allow-list) is built (fe856c26); Eve's confirmation and a possible time or size limit remain." SECURITY-DEPLOY-1 (`:272`) and SECURITY-REVIEW-END-1 (`:133`) list the ID reconciliation `mutate`.
- **Code.** `apply_recode_step` checks the formula with `utils.formula_check.evaluate_formula` (`core.py:286-289`, read). The screen offers no recode form, so the `mutate` step reaches it only through a transformation file (reasoned: no upload of a transformation exists).

### 1.8 Packaging of the two libraries

- **Source.** DOCKER-RELEASE-1 (`tasks.md:271`, issue #90): "the Dockerfile installs `libs/generator_utils` (gone) and leaves out `blueprint_arch`, `test_lab`, `id_reconciliation`".
- **Code.** No line of `assets/containers/Dockerfile` names `test_lab` or `id_reconciliation` (grep). `scripts/install_libs.sh:23-32` lists `test_lab` and not `id_reconciliation` (read). `libs/test_lab/pyproject.toml` does not declare `utils` (read).

### 1.9 Design parts that were planned and never built

From `.claude/design/spaces/TEST_LAB.md` (document) against the code (read, `02`):

| Part | Where planned | State |
|---|---|---|
| 2 to 6 files, multi-file sequencing, complexity warning | `TEST_LAB.md:72, 299-320` | not built |
| Confirm, reject, unverify, manual pick per match; "No false positives allowed" | `:151-162, 230-235` | not built; a threshold slider instead |
| Chunked review, bulk accept, re-run of patterns per round; the 50-unmatched advice | `:211-245, 275` | not built (`chunk_size` unused) |
| Recode form | `:271-297` | not built (library only) |
| The transformation file with files, date, who, counts, audit log; reuse by upload | `:164-209`; ADR-084 (manual load) | not built |
| Key selection after reconciliation; uniqueness check; integrity steps on the key | `:38, 331-347` | not built |
| Per-column synthetic config review; dates; normal distribution; "extend with" | `:62-64, 679-688, 729-756` | not built |
| Six error kinds and named scenarios on screen | `:689-704, 776-810` | two sliders; scenarios library only |
| Several files anonymised together; the de-anonymising step in the output | `:50-54, 569-573` | library only (`anonymise_batch`, `build_deanon_steps` with the old name `join`) |
| Bulk folder conversion | `:31` | library only (`convert_folder`) |
| "Audit trail: file-generation operations should log what was produced ... to the session audit log" | `:830` | not built: no notification or log call in `H` (grep for `notification_show`, `notification_log`: none) |
| Access control for the mapping | `:521-526` | deferred in the design itself |
| Anonymisation fidelity (full distributions) | `:872` | deferred in the design itself |
| The pattern helper shared with BLUEPRINT's Join Designer | ADR-084 point 3; `TEST_LAB.md:828, 868` | not built (`join_designer.py` does not import it) |

### 1.10 The three ideas of the task

- **Source.** `tasks.md:347` (Eve 2026-11-13, "we will need to work on Test Lab also"): "which of these ideas are wanted: extract a pilot recipe (reconstruct a lineage), a tool-specific recipe (for example a single-sheet variant), combine recipes (format detection, common datasets, branching)". `ORDER.md`: "The ideas already in the task ... are to be placed in the guide by size of decision" (the relaying session's sentence).
- **What exists.** Nothing named so in the code (grep for "pilot", "combine"). Related code that exists: the recipe graph and lineage walk in `libs/utils` (`recipe_graph.py`, `lineage_walk.py`, named in the BLUEPRINT review), BLUEPRINT's branch plan (`generate_branch_plan`), `utils.recipe_factory`. Not studied here.
- **Not known.** What each idea means in practice, who asked for it first, and its size.

### 1.11 Her two examples of what the Test Lab should help with

- **Source.** `ORDER.md`, her words: "eg. testing from synthetic data, preparing data files in the correct format".
- **What exists.** Synthetic data makes a TSV with no seed, no config record and no link to a recipe's declared fields (`02` section D). "Preparing data files in the correct format" is the reformatter (TSV only, no delimiter guess, no check against a recipe's `input_fields`) and, partly, the scaffold. Neither tool reads a recipe (by design: "Test Lab tools don't operate on an open data analysis recipe", `home_theater.py:1955-1957`, the owner's choice of 2026-11-08 as reported there).
- **Not known.** Whether "the correct format" means TSV, or the format a given recipe declares (types, column names, missing-value markers).

### 1.12 Others named in the sources

- **Anonymiser hint** (`developer_workflow.md:245-250`, open question): "should the Anonymiser surface a non-blocking, doc-style note ('for multi-file consistency, reconcile IDs first')".
- **The Info panel text** (`home_theater.py:1954-1966`): a placeholder "reserved for Test-Lab-specific instructions once that's decided".
- **The side panels** (D-0381): the Test Lab side panels take HOME's width and drag mechanism; "likely always visible" (a working direction).
- **The rule file proposals** R077 to R086 (`RULE_FILE_CHANGES.md:146-155`, status "proposed"; R078 is "Eve chooses").
- **CONFIG-REVIEW-1** (`tasks.md:196`): the target app features; the Test Lab stays developer-only there.
- **UTILS-REUSE-REVIEW-1** (`tasks.md:179`): code to move to `libs/utils`; the Test Lab has a type guess (`BS._map_dtype`), a slug rule (`_sanitize_name`) and a delimiter rule repeated in four places (reasoned).
- **The unused panel type** `test_lab` in `sidebar_registry.py:95-101`: its own comment says it was "left as-is rather than pulled into this issue's scope" (2026-11-08).
- **The legacy CLI** of the synthesizer and its helpers "retained for backward compatibility" (`aqua_synthesizer.py:305-458`).

---

## 2. Known defects and gaps

State: **R** = I confirmed it by reading now; **run** = confirmed by a probe now; **D** = from a document, not re-checked.

| # | Tool | Defect or gap | State | Evidence |
|---|---|---|---|---|
| 1 | Scaffolding | Tables named after Shiny's upload numbers (`'0'`, `'1'`); the user's file names appear nowhere | run | case A; `scaffolder.py:84-86`; `test_lab_studio.py:71-76` |
| 2 | Scaffolding | `source.path` is the temporary upload path; absolute in the app, refused by the checker (PA01) | run (the refusal); D (the Shiny folder) | `bootstrapper.py:95-103` |
| 3 | Scaffolding | A numeric-looking id becomes `Int64`; E03 refuses it; D-0225 | run | cases A, B |
| 4 | Scaffolding | The engine's load refuses every scaffold (no analysis group) | run | case G |
| 5 | Scaffolding | Silent `sample_id` key; typed key not slugged; key not checked in every file | R | `H:421-424`; `scaffolder.py:183`; `test_lab_studio.py:65-69` |
| 6 | Scaffolding | Entity key marked by column name, not by the user's key | R | `scaffolder.py:158-159`; `bootstrapper.py:81-82` |
| 7 | Scaffolding | Writes an inner join (against ADR-084 point 6); rows without a partner are dropped with no word | R | `scaffolder.py:177-189` |
| 8 | Scaffolding | Recipe id not checked (spaces, slashes) | R | `H:408-413` |
| 9 | Scaffolding | Every file read as tab, though `.csv` and `.txt` are accepted | R | `scaffolder.py:94, 108, 117`; `H:326-331` |
| 10 | Scaffolding | Tests use real file names and text ids, so 1 and 3 pass the tests | R | `test_scaffolder.py:9-27` |
| 11 | ID reconciliation | The cleaning step breaks ids that matched exactly | run, R (xfail) | case C; `test_suggested_steps.py:105-112` |
| 12 | ID reconciliation | Hyphen-to-underscore match gives a step that changes nothing | run, R (xfail) | case D; `test_suggested_steps.py:87-93` |
| 13 | ID reconciliation | The prefix step empties an id no longer than the prefix | R (xfail) | `test_suggested_steps.py:96-102` |
| 14 | ID reconciliation | Fuzzy matches are not written as steps, and the status does not say so | R | `core.py:219-222`; `H:501-506` |
| 15 | ID reconciliation | "A written reason is required before downloading" is not enforced | R | `H:221-224, 302-310` |
| 16 | ID reconciliation | Delimiter by file ending; an unreadable file reads as "Upload both files" | R | `H:43-54, 116-119, 154-158` |
| 17 | ID reconciliation | Fallbacks `ref_id`/`target_id` and threshold 0.7 on an unreadable input | R | `H:289-298` |
| 18 | ID reconciliation | `id_patterns` `@deps` names `join_designer.py` as a consumer; it is not | R | `id_patterns.py:10-11`; grep |
| 19 | Synthetic data | Text columns with more than 15 values and every named column become `value_A/B/C`; no dates | R; D (the run of 2026-11-18) | `aqua_synthesizer.py:166-170, 184-187, 215-217` |
| 20 | Synthetic data | A comma file read as tab gives one column | run | case E |
| 21 | Synthetic data | No seed, no config in the download, no scenario on screen | R | `H:639, 667-675` |
| 22 | Synthetic data | The duplicate-id slider does nothing when no key column is recognised, silently | R | `aqua_synthesizer.py:259` |
| 23 | Synthetic data | Error rates read inside `except Exception: pass` | R | `H:632-637` |
| 24 | Synthetic data | Only the first 100 rows are read; not said | R | `aqua_synthesizer.py:136` |
| 25 | Anonymisation | A missing id crashes (`KeyError None`) | run | case F; `anonymiser.py:302-303` |
| 26 | Anonymisation | One file only on screen; consistency across files not reachable | R | `H:688-721`; `anonymiser.py:144-226` unused |
| 27 | Anonymisation | Unsalted 8-character hash; collisions not reported | R (code); reasoned (risk) | `anonymiser.py:46-48` |
| 28 | Anonymisation | The key column renamed `anon_<column>`; not said | R | `anonymiser.py:119, 307-309` |
| 29 | Anonymisation | The mapping is in the same ZIP; no warning | R | `H:716-718, 813-835` |
| 30 | Anonymisation | The de-anonymising step is not shown and uses the old action name `join` | R | `anonymiser.py:228-246` |
| 31 | Reformatting | Unticking every sheet gives all sheets | R | `H:979` |
| 32 | Reformatting | Delimiter not guessed (default comma); no rows or columns count shown | R | `H:892-898, 950-965` |
| 33 | Reformatting | Two sheet names may map to one file name | reasoned | `reformatter.py:172-175` |
| 34 | Excel extractor | No screen; prints and skips silently on a missing key | R | `extractor.py:48-65`; grep |
| 35 | Whole space | 21 `except Exception` blocks, most with a quiet default | R | `grep -c` |
| 36 | Whole space | Results are not reset when a panel closes (the rule says they are) | R | `@reactive.event` calcs |
| 37 | Whole space | No log of what a tool produced (the design's audit trail) | R | grep |
| 38 | Whole space | `test_lab` imports `utils` without declaring it; `id_reconciliation` missing from `install_libs.sh`; neither in the Dockerfile | R | `02` section H |
| 39 | Whole space | The hand-off to BLUEPRINT is a ZIP; BLUEPRINT's upload takes one `.yaml` | R | `wrangle_studio.py:225-226` |
| 40 | Whole space | No browser test of any Test Lab tool; the smoke test checks the right sidebar text only | R (names); D (the smoke file not read) | `test_shiny_smoke.py` cited at `home_theater.py:2254-2255` |
| 41 | Whole space | Two audit greps of `rules_test_lab.md` section 10 fail on harmless files (a docstring, `.gitkeep`) | run | `02` section H |
| 42 | Records | TESTLAB-REVIEW-1 appears twice in `tasks.md` with two states | R | `tasks.md:347, 677` |

## 3. Texts out of date (to verify and update; nothing was changed here)

| Text | What is wrong | Evidence |
|---|---|---|
| `.claude/design/spaces/TEST_LAB.md:3-8` | "all six tools are implemented and wired", "990 lines", "94 passing tests"; "Last updated: 2026-05-05" | `02` section F; 1007 lines; 111 test functions in `libs/test_lab/tests` |
| `TEST_LAB.md:836-840` (Code Modules) | `test_lab_studio.py` as "UI and server handlers for all TEST_LAB tools"; `reconciler.py` "is migrated" and `libs/id_reconciliation/` "to be created" | the handlers are in `H`; the library exists |
| `TEST_LAB.md:862-875` (Open Questions) | "All design questions resolved 2026-05-22. No open items." | the open choices of `02` section M |
| `.claude/rules/rules_test_lab.md` | section 4b known bugs (fixed); 4c action list; 3d `load_scenario()`; 8 file layout (`steps.py`, missing `recipe_steps.py` and three test files); 9 the `ConfigManager.load()` gate; 1 "Closing a tool panel resets it"; 10 two greps that fail on harmless files | `02` sections H, K |
| ADR-084 | format 0 words (`join_manifests`, `ManifestBootstrapper`, `type:`); its own banner says "Partly stale" | `architecture_decisions.md:4006` |
| `.claude/design/developer_workflow.md:89` | `final_contract` | ADR-100 |
| `docs/workflows/test_lab_sdk.qmd` | ADR-084 for the rename (ADR-068); the extractor as "Stage A"; "990 lines" | read |
| `docs/appendix/test_lab_rationale.qmd` | "never authors `tier1`/`tier2`" | read |
| `docs/workflows/developer_workflow.qmd:87, 89` | open the ZIP in BLUEPRINT; the step "printed in the Anonymiser's own output" | read |
| `app/src/help/test_lab.md:6, 9, 12` | named transformation, plot stubs, named scenarios | read |
| `libs/test_lab/README.md:14, 52` | bootstrapper waits for bug fixes; "No cross-lib imports" | read |
| `anonymiser.py:31`, `reformatter.py:20` (`@deps`), `H:14-16` (module text) | "not yet built"; "handlers are added by: TL-UI-..." | read |
| `libs/utils/src/utils/id_patterns.py:10-11` (`@deps`) | `consumed_by: join_designer.py` | grep |
| `.claude/tasks/tasks.md:347, 677` | the same task twice | read |
| `.claude/logs/handoffs/handoff_active.md:47` | "Test Lab review: not started." (true until this run) | read |
| `docs/UML/app.mdj` TEST_LAB diagrams | not checked against the code | - |

## 4. What I could not find or verify

- A ledger line or a text that describes the three ideas of the task beyond `tasks.md:347`.
- Whether the owner wants the Test Lab reachable for scientists (her words say "for the user"; the flags say developers).
- The smoke test text (`test_shiny_smoke.py`) and whether a browser has ever run a Test Lab tool; the screenshots in the main tree's `tmpAI/` (listed in `01` section 9) were not opened.
- The xfail tests were read, not run.

## Not verified

- Every statement about the screen is read from the code; nothing was seen in a browser.
- Item 33 and the hash collision risk (item 27) are reasoned, not run.
- The "Shiny temporary folder is outside the project" of item 2 is taken from the 2026-11-18 review.
