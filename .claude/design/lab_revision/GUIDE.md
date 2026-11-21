# Test Lab: a guide for the rebuild (larger decisions first)

Written 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396: "TEST_LAB: a review to plan its rebuild (fallback task, the same kind as BLUEPRINT-REVIEW-1)"), step 5 of the review. It builds nothing and decides nothing. Every open choice below is "to decide". No question is put to the owner here.

Her order for this work (`ORDER.md`): "also a preparation without details"; and "yes it will have to explore what we had planned, what is existing, many things will need to be anyway verified and updated". The relaying session's text (not her words) asks for a guide that puts the larger decisions and questions first and leaves the details out, with the three ideas of the task placed by size of decision.

Inputs: every file of this folder (`01` to `05`, the `06` files, `prior_work/README.md` and the files it lists). The detail is there; this guide only points to it.

Labels: **read** = the code was read at that file:line by a worker of this review (the file and the section say when); **read now** = re-read on 2026-11-21 while writing `06_proposals_one_table.md` or this guide; **as reported** = taken from a viewpoint or a document, not re-read; **ran** = run by a probe of this review (step 1, or a viewpoint in step 4; scripts in `prior_work/`); **reasoned** = a reading, not a fact. Short names: `H` = `app/handlers/test_lab_handlers.py`, `AN` = `libs/test_lab/src/test_lab/anonymiser.py`, `AQ` = `.../aqua_synthesizer.py`, `SC` = `.../scaffolder.py`, `BS` = `.../bootstrapper.py`, `RF` = `.../reformatter.py`, `CORE` = `libs/id_reconciliation/src/id_reconciliation/core.py`, `DI` = `app/handlers/data_import_handlers.py`.

---

## 1. One page

### What the Test Lab is meant to be (her words)

- The order: "a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format" (`ORDER.md`, block M422; the same words in the evidence field of D-0396).
- D-0048: "Order of work HOME, then Gallery, Blueprint and Test Lab last" (decision field).
- D-0271: "we do changes to blueprint and lab after - we focus on home and gallery" (her words, evidence field).
- D-0381: "BLUEPRINT, GALLERY and TEST_LAB use the same width and drag mechanism for their side panels as HOME" (decision field; the line says the wording is the coordinator's; her words: "I think the other spaces panels will functionne in the same way (and likely always visible)").

(All four ledger lines are taken by EVE and DECIDED; read now.) Nothing else she said describes what the Test Lab is for.

### Where it stands today (ten lines)

1. Five tools on the screen: ID reconciliation, recipe scaffolding, synthetic data, anonymisation, file reformatting; a sixth (the Excel extractor) exists in the library only (`02` summary).
2. It is shown only in the `developer` and `qa` setups; her words say "for the user" (`04` section 6).
3. Each tool ends with a file. Only a reformatted or synthetic TSV can reach the next user space as it is, through HOME's Data Import panel, and only when its column names match a loaded recipe (`04` section 2).
4. The recipe the scaffold writes opens nowhere: BLUEPRINT's upload takes one `.yaml`, HOME has no recipe upload on screen, and the engine refuses a recipe with no plot (`04` J5; ran in step 1, case G).
5. Synthetic data cannot be made again: no seed on the screen, no record of the settings (`H:639`, read now).
6. Three decided rules are broken by what the Test Lab writes: a numeric-looking sample id becomes a number (D-0225), the key is guessed from a column name (D-0082), several results change silently (D-0050) (`04` section 4).
7. Anonymisation by "hash" can give two samples one new id and can be reversed by guessing; the key travels in the same ZIP as the table (`06_proposals_one_table.md` F1 to F3).
8. ID reconciliation matches different samples at its default cutoff, and its cleaning step changes ids that already matched (F5, F6).
9. The same jobs are done in several places: five recipe writers, four Excel paths, three type guesses, several synthetic generators (`06_proposal_architect.md` 1.3).
10. A finding about HOME, not the Test Lab: HOME's Data Import and the engine disagree on which headers a file must have when a recipe uses `original_name`; it is verified separately by the coordinator (`06_proposals_one_table.md`, "Found on the way, about HOME").

### The panel's recommendation (a recommendation, not a decision)

The four viewpoints of step 4 recommend **approach A as the base**: a small, safe toolbox (reformatting, anonymisation, reproducible synthetic data), where **every file carries a record** of what was done (tool, settings, seed, the real input file names, counts, what the tool did that the user did not choose). The scientist and the architect add, as an optional later step, **a check of a file against a recipe the user chooses** (report only, never a rewrite), on one check function shared with HOME. Recipe-making and the three ideas move out of the Test Lab (BLUEPRINT or scripts), but the scaffold stays until its new home exists. Detail: `06_proposals_one_table.md`.

---

## 2. The larger decisions, ranked

Ranked by what each one blocks. Each line: the question, why at this rank, the options in a few words, the panel's recommendation when there is one, where the detail is. The smaller choices are grouped under the decision they depend on, by reference only. Decisions **shared with BLUEPRINT** are marked and point to `../blueprint_revision/GUIDE.md`.

### 1. What the Test Lab is, as a whole: which approach

- **Question.** Is the Test Lab a small safe toolbox (A), a companion to a chosen recipe (B), today's tools repaired (C), the recipe starter (D), or a combination?
- **Why first.** It decides which tools stay, what each screen shows, and which of the decisions below are needed at all.
- **Options.** A, B, C, D or a combination (`06_proposals_one_table.md`, the table).
- **Panel.** All four: A as the base. Scientist and architect: B's check-only part later. Developer: the scaffold kept until its new home exists. Nobody recommends D now.
- **Detail.** `06_proposals_one_table.md`; the four `06_proposal_*.md`; `04` "To decide"; `02` section M.
- **Grouped here.** The words on the screen, the help and the Info panel text (`04` To decide 13); the stale texts (section 5 below, `03` section 3).

### 2. Who the Test Lab is for, and how it is shown

- **Question.** Which setups show the Test Lab: developer and qa only (today), also the scientist setups, one flag per tool, or some tools as scripts only?
- **Why second.** Her words say "for the user"; the flags say developers (`02` K18). Every screen design waits for it, and a tool shown to scientists must first be safe for a non-developer. The developer and the user rank it first.
- **Options.** (a) developer and qa only; (b) also `standalone`; (c) one flag per tool; (d) some tools as scripts only (`04` section 6).
- **Panel.** A says "shown in the scientist setups" for the safe tools; the architect: at least two groups of tools, so flags per tool.
- **Detail.** `04` section 6 and To decide 1; `06_proposal_architect.md` 3.A (larger decision 1); `06_proposal_developer.md` section 1 (`test_lab_enabled` read in six places).
- **Grouped here.** The flag matrix of `rules_app_features_flags.md` and the target of CONFIG-REVIEW-1 (the configuration review); whether anonymisation is offered in the app at all (decision 7).

### 3. What every file the Test Lab writes must carry

- **Question.** Does every output come with a record (tool and version, app version, date, the user's real file name, every setting, the seed, counts before and after, what the tool did unasked, a content hash, for synthetic data the list of planted errors), and is there a "make it again" upload?
- **Why third.** It decides reproducibility for every tool and every approach; the scientist ranks it first; it is the "least regret" part (developer). Applying the seed rule of D-0056 to Test Lab files is a reading (D-0056 is about recipes).
- **Options.** (a) nothing extra (today, except anonymisation's own record); (b) a record in the download; (c) the record plus "make it again" (`04` To decide 3).
- **Panel.** All four: (b) at least; the architect: one shape for all tools, written once and shown twice (screen and record).
- **Detail.** `06_proposal_scientist.md` section 5; `06_proposal_architect.md` section 2 (T1 to T7); `06_proposal_developer.md` section 2 (F-1); `06_proposal_user.md` (the words).
- **Grouped here.** The seed: shown, written, and a generator that uses its own random state, not the state of the whole app process (F7 of the table); what marks a synthetic or anonymised file once HOME has copied it over a data file (architect 3.A); library versions in the record.

### 4. What "the correct format" means, and whether the Test Lab may read a recipe

- **Question.** Is "the correct format" a TSV, or the columns, types and missing-value words a chosen recipe declares, checked by one function that HOME also uses; and may a Test Lab tool read a recipe the user chooses?
- **Why fourth.** It decides A against B and whether the Test Lab can ever say "HOME will accept this file". The architect ranks it first, because today HOME itself has two definitions that disagree (the HOME finding, verified separately).
- **Options.** (a) a TSV only; (b) the recipe's declared fields, checked (B); (c) both, the second optional (`04` To decide 2). For reading a recipe: no; check and report only; reshape with confirmation.
- **Panel.** Scientist and architect: (c), check and report only, never rewrite, on one function shared with HOME's Data Import. Developer: extract the check anyway; B's reading only if she reverses the 2026-11-08 choice.
- **Detail.** `06_proposal_architect.md` sections 1.1, 3.B, 5; `06_proposal_scientist.md` 3.B; `06_proposals_one_table.md` R1 and "Found on the way, about HOME".
- **Grouped here.** "The choice of 2026-11-08" that the Test Lab does not operate on an open recipe: found only as a docstring (`app/handlers/home_theater.py:1955-1960`, read now), no ledger line, no ADR: to confirm, not a decision of record. How the Test Lab gets a recipe (an upload for the run, or the recipe places study, shared with BLUEPRINT, see decision 5). D-0374 ("Informing about undeclared file columns belongs to the user space BLUEPRINT"): B stays silent on them.

### 5. Where recipe-making lives (shared with BLUEPRINT)

- **Question.** Do the scaffold, the bootstrapper and "Bake in ID Reconciliation steps" stay in the Test Lab, move to BLUEPRINT, or become scripts; and which one recipe writer stays?
- **Why fifth.** It decides whether those parts are repaired or removed, and it is the same choice as BLUEPRINT's "how a table enters a recipe". Until it is settled, A leaves no screen path from files to a first recipe.
- **Options.** Test Lab (C), BLUEPRINT, scripts (the scripts already do it: `assets/scripts/create_data_analysis_recipe.py` writes a recipe with a first plot through `utils.recipe_factory`), or Test Lab boilerplate then BLUEPRINT.
- **Panel.** Out of the Test Lab in the end (all four), but not removed before its new home exists (developer, architect).
- **Detail.** `04` J5, section 3.4, To decide 4 to 7, 11, 12; `06_proposal_architect.md` 3.A, 3.C; `06_proposal_developer.md` 3.A, step 8.
- **Shared with BLUEPRINT** (`../blueprint_revision/GUIDE.md`): its decision 8 (how a whole recipe is built from empty; a table from a Test Lab boilerplate is option (a)); its decision 4 (the recipe places P1 to P11 and the dated name, D-0390 to D-0394); the draft recipe that opens: the loader refuses a recipe with no plot, for a scaffold and for BLUEPRINT's new draft alike (`tasks.md:220`, WRITERS-W8-1).
- **Grouped here.** The scaffold's join (`joins: {}` as ADR-084 says, a join marked "to check", or as today; `02` K1); its key (chosen by the user; D-0082, D-0216); its table names and data path; whether a scaffold is a production recipe for the `name_date` rule (D-0390, D-0392); how it reaches BLUEPRINT and HOME (a ZIP by hand, a recipe ZIP upload, the user's own recipe place).

### 6. What ID reconciliation becomes, and who reads its output

- **Question.** If the scaffold leaves, what does the user do with the matches: a steps file that BLUEPRINT reads, a recoded file written by the tool, or a report only?
- **Why sixth.** Today its only reader is the scaffold in the same session (`H:366-401`, as reported); three viewpoints name it as the gap of approach A. It must be decided with decision 5, not after.
- **Options.** (a) report plus a steps file with a defined reader (BLUEPRINT); (b) a tool that writes a recoded file (a new behaviour that changes ids: counts and the record are mandatory); (c) report only.
- **Panel.** No common choice; all agree fuzzy matches are a list a person confirms, never a rule.
- **Detail.** `04` J3 and To decide 8; `02` section C; `06_proposal_scientist.md` section 7; `06_proposal_developer.md` 3.A.
- **Grouped here.** Which match kinds may become a rule (exact, case and space) and which need each pair confirmed (fuzzy); the default cutoff (70 today, `CORE:28-31`, read now; F5 of the table); the cleaning step that breaks matched ids and the two other defects recorded as strict expected failures (`03` 1.3); the confirm-each-match step of the design; the crash on a missing id.

### 7. Anonymisation: in the app or not, and how

- **Question.** Is anonymisation offered in the app (and to whom), with which patterns, and where does the key go?
- **Why seventh.** Personal data entering a running app goes against the recommendation of ADR-097 point 8 ("anonymisation before data ever reaches the app, with any de-anonymisation key kept outside it entirely", read now, `architecture_decisions.md:4991-4995`; a record, not a ledger line). The hash pattern changes results silently (F1, F2).
- **Options.** In the app for everyone; in the app for local deployments only; a local script only. Patterns: remove the 8-character unsalted hash, salt it, or random labels with a stored mapping. The key: a separate download with a plain line; refuse a mapping that gives two ids one new id; keep the id column's name.
- **Panel.** Scientist: random labels with the key kept apart is the defensible form; never call the result "anonymised". Architect: CONFIRM against ADR-097 point 8. User: two downloads, not a stronger warning.
- **Detail.** `06_proposal_scientist.md` section 6; `06_proposal_architect.md` 3.A, 3.B; `04` J4, To decide 10; `02` K10.
- **Grouped here.** Several files with one mapping (`anonymise_batch`, library only); the way back (`build_deanon_steps`, old action name `join`, not called); the `anon_<column>` rename (H1); the name of the file in the record (likely Shiny's upload number, `04` V6).

### 8. What synthetic data is for, and what it may claim

- **Question.** What does a synthetic file prove, and from what is it made: a sample file or column names (today), or a chosen recipe's declared fields; one table or several on one set of ids?
- **Why eighth.** It is her first example ("testing from synthetic data"); its shape depends on decisions 3 and 4.
- **Options.** From a sample (today, types guessed from 100 rows); from declared fields (B); several tables on one set of ids (D-0205: "the same set of ids are used across all the datasets of the recipes", her words, for the test data of the recipes); dates and free text; the other four error kinds.
- **Panel.** Scientist and architect: planted errors in two labelled groups ("refused at ingestion" and "passes ingestion and tests the steps"); the screen says it tests that a recipe runs and handles the listed errors, not that the result is right; a result of zero rows is reported.
- **Detail.** `06_proposal_scientist.md` section 4; `06_proposal_architect.md` 1.2, 3.B; `04` J2, To decide 9.
- **Grouped here.** Named scenarios on the screen; the duplicate-id slider that does nothing without a recognised key (`03` item 22); the key found by column name (`AQ:20-28`, read now).

### 9. One way for each job

- **Question.** Which one of each stays: recipe writers (`SC`, `BS`, `utils.recipe_factory`, two scripts), Excel paths (`RF`, the extractor, `ExcelHandler`, HOME's Data Import), type guesses (three), synthetic generators (`AQ`, the scripts)?
- **Why ninth.** "One authoritative way to do each thing" (`rules_legacy_management.md`, a rule file); a repair of one path while others stay is a half fix. It follows decisions 1, 4 and 5.
- **Options.** Per job, keep one and remove the others with a tombstone.
- **Panel.** Architect: one recipe writer path (`recipe_factory`), one type inference shown as a proposal to confirm, an id never proposed as a number.
- **Detail.** `06_proposal_architect.md` 1.3 and T7; `04` section 3.7, To decide 11.
- **Grouped here.** The extractor wired or removed (`03` item 34); the shim `pattern_detector.py` (open task PATTERN-DETECTOR-SHIM-1: remove it); the pattern helper shared or not with BLUEPRINT's Joint Designer (`02` K6); the packaging of the two libraries (`03` 1.8).

### 10. Idea 3: combine recipes (large)

- **Question.** Is combining recipes (format detection, common datasets, branching) wanted, and where?
- **Why here.** By size it is the largest of the three ideas: names and plot ids clash (checker X5), joins and keys, sessions and audits of the source recipes, a store of known formats. It blocks nothing else in the Test Lab and waits for BLUEPRINT's rebuild.
- **Options.** Not wanted; a BLUEPRINT feature after its rebuild; a Test Lab tool that only reports (which tables two recipes share, which plot ids clash); a script (`05` section 4.5).
- **Panel.** All four: at most a report in the Test Lab; the combined recipe is written in BLUEPRINT.
- **Detail.** `05` section 4; `06_proposals_one_table.md` "Where the four agree".
- **Shared with BLUEPRINT**: joins, branching, full recipe edit (D-0102: "full recipe edit exists only in Blueprint"), and the recipe places and names (its decision 4).

### 11. Idea 1: extract a pilot recipe (medium)

- **Question.** Is cutting a smaller recipe out of a large one (by walking the lineage back from a plot) wanted, and where?
- **Why here.** Medium: a new writer, the recipe places, share or copy of fragment files, new plot ids. It depends on decision 5.
- **Options.** Not wanted; a Test Lab tool; a BLUEPRINT action next to "branch"; a script; the export's frozen recipe documented as the way to recover a recipe (`05` section 2.5).
- **Panel.** BLUEPRINT (it owns lineage and branch); before it is offered, a check that the cut-out gives the same rows for its plot as the parent on the same data (scientist, developer).
- **Detail.** `05` section 2.
- **Shared with BLUEPRINT**: the branch plan, the recipe places and names, share or copy of fragments.

### 12. Idea 2: a tool-specific recipe (small to medium)

- **Question.** Are recipes for one bioinformatics tool's output (or one sheet of a workbook) wanted, and in which form?
- **Why here.** The smallest of the three: templates from the per-tool fragments that already exist, or a documented chain (reformat a sheet, then start a recipe). Medium only if the project ships and maintains them per tool.
- **Options.** Not wanted; templates per tool; a scaffold mode "one tool's file"; an Excel sheet read directly by the recipe format (a format change, outside the Test Lab); a documented chain (`05` section 3.5).
- **Panel.** A template or a documented chain now, not a Test Lab screen; a tool recipe carries the tool version (scientist).
- **Detail.** `05` section 3.
- **Shared with BLUEPRINT**: where templates live and how they are named (its decision 4).

If the three ideas are wanted, the panel's build order is the reverse of this ranking (tool-specific, then pilot, then combine), smallest first.

---

## 3. What must be verified before any rebuild starts

Each item says how. None was done in this review. Most need a browser.

| # | What | How |
|---|---|---|
| 1 | Each tool in a browser, with the `developer` setup | Start the app, run each tool once with the files of the probes in `prior_work/`; note what the screen says (`04` V1) |
| 2 | The HOME finding (Data Import against the ingestor, `original_name`) | Being verified separately by the coordinator; in a browser: upload a file with each header spelling into `simple_template` and then open the recipe (`06_proposals_one_table.md` X1) |
| 3 | A reformatted TSV, a synthetic TSV (also a stress file) and an anonymised file through HOME's Data Import | Upload each into a table of a loaded recipe; read the message (`04` V2, V3, V4) |
| 4 | An Excel id column with leading zeros through the reformatter | Convert a sheet with `007` typed as a number and as text (`04` V5) |
| 5 | The file name written by the anonymiser through a real upload | Browser: anonymise a named file, open the ZIP (`04` V6) |
| 6 | The anonymiser hash collision and the false fuzzy matches, through the screen | Re-run `sci_probe.py`, `sci_probe2.py`, `sci_probe3.py` (paths from the main tree root), then the same cases in the browser |
| 7 | Who else in the app uses numpy's or Python's global random state | Grep for `np.random.` and `random.` outside a local generator (`04` V11) |
| 8 | The same-session carry-over of ID steps into the scaffold | Browser: reconcile, tick "Bake in", scaffold, read the tier file (`04` V10) |
| 9 | Whether BLUEPRINT would read an `id_transformation.yaml`, and whether the export's frozen recipe opens in HOME or BLUEPRINT | Try both in a browser (`04` and `05` "Not verified") |
| 10 | Whether anything outside this repository calls `BS.bootstrap()`, the extractor or the synthesizer's command line | Ask the owner's other repositories, outside this review (`04` V7) |
| 11 | The UML diagrams of the Test Lab against the code | `assets/scripts/audit_uml_model.py`, then the four diagrams (`04` V8) |
| 12 | The tests that hide defects (real file names, text ids) | Read `test_scaffolder.py:9-27`; add Shiny upload names in a scratch copy (`04` V9) |
| 13 | The recipe graph on two recipes at once | A scratch run of `RecipeGraph` on two shipped recipes (`05` "Not verified") |

---

## 4. A proposed order of the rebuild (proposal, not decided)

From the developer viewpoint (`06_proposal_developer.md` section 6), unchanged in substance. It starts only **after the refactoring of HOME and the Gallery** (D-0271: "we do changes to blueprint and lab after - we focus on home and gallery"), and after decisions 1, 2 and 3 above.

Place relative to BLUEPRINT's rebuild: D-0048 puts "Blueprint and Test Lab last" and does not say which of the two comes first. Steps 0 to 7 below do not depend on BLUEPRINT and could run before it or beside it (different files). Step 3 touches HOME's Data Import handler, so it comes after the HOME refactoring and with the HOME fix of the finding above. Step 8 (the recipe-making path) waits for BLUEPRINT's decision on how a table enters a recipe and, in practice, for BLUEPRINT's rebuild. The three ideas, if wanted, come after BLUEPRINT's rebuild.

| Step | What | Can run in parallel with |
|---|---|---|
| 0 | The browser checks of section 3; tests adapted to the decided design: test files with Shiny upload names, Excel with `007`, comma decimals, an empty id | alone, first |
| 1 | The record: one small library module, one shape for every tool | 2 and 3 (own files) |
| 2 | Synthetic data on its own random generator; the seed always shown and written; the list of planted errors | 1 and 3 |
| 3 | The "file against declared fields" check taken out of HOME's Data Import into a library, no message changed; HOME calls it | 1 and 2 (a reviewer checks HOME's tests unchanged) |
| 4 | Anonymisation repairs (empty id, the key apart, the hash pattern, several files) | after 1; with 5 |
| 5 | Reformatting repairs (counts, delimiter shown, sheets, Excel read as text) | after 1; with 4 |
| 6 | The logic of each remaining tool moved out of the handler, then the screens | after 2, 4, 5 (same handler file: alone) |
| 7 | Flags: per tool or per setup, with the validator, the sidebar registry, the setup files, the rule file | after decision 2 |
| 8 | The recipe-making path: remove or move the scaffold, the bootstrapper and "Bake in" (with tombstones); the reader of ID reconciliation | only after decisions 5 and 6 and BLUEPRINT's table entry |
| 9 | Screen words, help, Info panel | last |
| 10 | Records: rule file, ADR-084 and ADR-097 texts, UML, docs | after each merge that changes behaviour |

Rule for every step: tests adapted to the decided design first; break the code once and see a test fail (`agent_principles.md` point 5).

---

## 5. Defects found in today's Test Lab (not fixed by this review)

Kind: **changes a result** (what the user gets differs from what they asked, without a word), **hides** (something exists or happens that the user cannot see), **misleads** (a word on screen or in a text says something untrue), **cosmetic**. Numbers in brackets are those of `03` section 2, where the full list is.

| # | Tool | Defect | Where | Kind | Label |
|---|---|---|---|---|---|
| 1 | Anonymisation | The "hash" pattern keeps 8 hexadecimal characters of an unsalted hash: two ids can get one new id, with no message; the hash can be reversed by guessing (27) | `AN:39`, `AN:46-48` | changes a result | code read now; collisions and reversal ran (scientist) |
| 2 | Anonymisation | The "sequential" pattern depends on row order; two files give one sample two new ids | `06_proposal_scientist.md` R3 | changes a result | ran (scientist) |
| 3 | Anonymisation | `S1`, `S1 ` and `s1` get three new ids, with no warning | scientist R4 | changes a result (invents samples) | ran (scientist) |
| 4 | Anonymisation | The id column is renamed `anon_<column>` and moved first (28) | `AN:119-120`, `AN:302-309` | hides | read now |
| 5 | Anonymisation | The key is in the same ZIP as the table (29) | `H:717`, `H:824-829` | hides | read now |
| 6 | Anonymisation | A missing id crashes the tool (25) | `AN:302-303` | cosmetic (a crash, not silent); against D-0050 in spirit | ran (step 1, case F) |
| 7 | Anonymisation | One file only on the screen; the several-file function is unreachable (26) | `H:688-721` | hides | as reported |
| 8 | Anonymisation | The way back is not shown and writes the old action name `join` (30) | `AN:228-246` | misleads (the docs say it is printed) | as reported |
| 9 | Anonymisation | A custom pattern with no placeholder may give every row the same id | `AN:51-54` | changes a result | reasoned (scientist), not run |
| 10 | ID reconciliation | Default fuzzy cutoff 70, used by the screen, matches different samples (`ISO-1` to `ISO-10`) | `CORE:28-31`, `H:185` | changes a result | default read now; matches ran (scientist) |
| 11 | ID reconciliation | The cleaning step changes ids that matched as they were (11) | `test_suggested_steps.py:105-112` (strict xfail) | changes a result | read now; ran (step 1, case C) |
| 12 | ID reconciliation | Hyphen-to-underscore gives a step that changes nothing; the prefix step empties a short id (12, 13) | `test_suggested_steps.py:87-102` | changes a result | read now (xfail); case D ran |
| 13 | ID reconciliation | Fuzzy matches are not written as steps, and the screen does not say so (14) | `CORE:219-222`, `H:501-506` | hides | as reported |
| 14 | ID reconciliation | A missing id crashes the pattern step | `libs/utils/src/utils/id_patterns.py:39` | cosmetic (a crash) | read now; ran (scientist R6) |
| 15 | ID reconciliation | Case and trailing spaces are not offered as a cleaning step with a count (`S1` does not match `s1 `) | scientist R5 | hides | ran (scientist) |
| 16 | ID reconciliation | "A written reason is required" is not enforced (15) | `H:221-224`, `H:302-310` | misleads | as reported |
| 17 | ID reconciliation | Unreadable inputs fall back to defaults without a word (16, 17) | `H:43-54`, `H:289-298` | hides | as reported |
| 18 | Synthetic data | No seed on the screen; no settings in the download (21) | `H:639`, `H:667-675` | changes a result (not reproducible) | `H:639` read now |
| 19 | Synthetic data | A given seed sets the random state of the whole app process | `AQ:84-86` | changes a result (other random draws in the process) | read now; ran (scientist, architect) |
| 20 | Synthetic data | No list of planted errors; planted type errors are refused at ingestion and never test the steps | `AQ:220-300` | hides | as reported; ran (architect) |
| 21 | Synthetic data | Types guessed from 100 rows; text columns become `value_A/B/C`; no dates; the key found by column name (19, 24) | `AQ:20-28` (read now), `AQ:136`, `AQ:166-187` | changes a result | partly read now |
| 22 | Synthetic data | A comma file is read as tab (one column) (20) | step 1, case E | changes a result | ran (step 1) |
| 23 | Synthetic data | The duplicate-id slider does nothing without a recognised key; error rates read inside `except Exception: pass` (22, 23) | `AQ:259`, `H:632-637` | hides | `H:636-637` read now |
| 24 | Recipe scaffolding | A numeric-looking id is declared `Int64` (3); against D-0225 | `BS:41-48`, `SC:154` | changes a result | read now; ran (step 1) |
| 25 | Recipe scaffolding | The entity key is set by column name; an empty key box gives `sample_id` silently (5, 6); against D-0082 | `SC:158-159`, `H:421-424` | changes a result | read now |
| 26 | Recipe scaffolding | Every table is inner-joined to the first: rows without a partner are dropped (7) | `SC:177-189` | changes a result | as reported |
| 27 | Recipe scaffolding | Tables named after Shiny's upload numbers; the data path is the temporary upload path (1, 2) | `SC:84-86`, `BS:95-103` | hides | ran (step 1) |
| 28 | Recipe scaffolding | No plot, so the engine refuses every scaffold; the screen says "open in BLUEPRINT" (4, 39) | `H:509-510`; step 1, case G | misleads | line read now; ran (step 1) |
| 29 | Recipe scaffolding | Every file read as tab though `.csv` is accepted; the recipe id is not checked (8, 9) | `SC:94, 108, 117`; `H:408-413` | changes a result (csv) / cosmetic (id) | as reported |
| 30 | Recipe scaffolding | Its tests use real file names and text ids, so defects 24 and 27 pass the tests (10) | `test_scaffolder.py:9-27` | hides | as reported |
| 31 | File reformatting | Unticking every sheet gives all sheets (31) | `H:979` | changes a result | read now |
| 32 | File reformatting | Delimiter not guessed and not shown; no counts; Excel cell types kept (32) | `H:892-898`, `H:950-965`; `02` F | hides; Excel types may change a result (not run) | as reported |
| 33 | File reformatting | Two sheet names may map to one file name (33) | `RF:172-175` | changes a result | reasoned |
| 34 | Excel extractor | No screen; skips a sheet without the key with a printed line only (34) | `extractor.py:48-65` | hides | as reported |
| 35 | Whole space | 21 `except Exception` blocks, most with a quiet default (35) | `grep -c` (step 1) | hides | as reported |
| 36 | Whole space | No log of what a tool produced; results not reset when a panel closes (36, 37) | step 1 grep | hides / misleads (the rule says reset) | as reported |
| 37 | Whole space | `test_lab` imports `utils` without declaring it; `id_reconciliation` missing from `install_libs.sh` and the Dockerfile (38) | `02` section H | cosmetic (packaging) | as reported |
| 38 | Whole space | No browser test of any Test Lab tool (40) | `test_shiny_smoke.py` | hides | as reported |
| 39 | Rule file | Two audit greps of `rules_test_lab.md` section 10 fail on harmless files (41) | `02` section H | misleads | ran (step 1) |
| 40 | Texts | The design, the rule file, ADR-084, the docs, the help and several `@deps` lines are out of date | `03` section 3 | misleads | as reported |

---

## 6. Contradictions between sources (listed, not resolved)

- **K1 to K18** of `02_planned_vs_existing.md` section K: the join in the scaffold; what the Test Lab writes into tier 1; six tools wired; known bugs; the entity key; pattern sharing; the shim; the boilerplate gate; injected actions; where anonymisation and the key live; the scenario loader's name; panel reset; one task in two states (`tasks.md:347` open, `tasks.md:677` done: under rule H of `decision_compliance.md`, reported, not resolved); which ADR made `libs/test_lab`; install; library imports; the transformation file; who the Test Lab is for.
- **Added by step 2 (`04`).** The 2026-11-18 review calls the 2026-11-08 choice "Eve's decision" (`2026-11-18_test_lab_review.md:125`, as reported by the architect); the only source is a docstring with no ledger line and no ADR (`home_theater.py:1955-1960`, read now).
- **Added by step 3 (`05`).** The three ideas sit in the Test Lab task ("lab script", May 2026), while D-0102 ("full recipe edit exists only in Blueprint") and D-0306 put recipe authoring in BLUEPRINT; whether writing a new recipe out of existing ones is "edit" is not stated anywhere.
- **Added by step 4 (the viewpoints).** HOME's Data Import checks the declared slugs, the ingestor checks `original_name`: two definitions of the format a file must have (`06_proposals_one_table.md` X1; a HOME matter, verified separately). The synthetic config header of `rules_test_lab.md` section 3 and the record that all viewpoints ask for would be two records of one file (architect section 2).

---

## 7. Parked items about the Test Lab

| # | Item | Source | State |
|---|---|---|---|
| 7.1 | The whole Test Lab waits for HOME and the Gallery | D-0048, D-0271, D-0272 ("The demo comes AFTER the big recipe change."); `03` 1.1 | parked by the order of work |
| 7.2 | The 2026-11-18 review's 14 open fixes and 9 questions | `tasks.md:677`; `03` 1.2; `02` section L | wait for her reading |
| 7.3 | Three ID cleaning defects recorded as strict expected failures | ID-RECON-STEPS-1, `tasks.md:222`; `03` 1.3 | wait for her decision (with decision 6) |
| 7.4 | The silent `sample_id` default of the scaffold | TESTLAB-EMPTY-KEY-DEFAULT, `tasks.md:647`; `03` 1.4 | waits (with decision 5) |
| 7.5 | A recipe with no plot cannot be loaded (scaffold and BLUEPRINT draft) | WRITERS-W8-1, `tasks.md:220`; `03` 1.5 | waits; shared with BLUEPRINT |
| 7.6 | The shim `pattern_detector.py` | PATTERN-DETECTOR-SHIM-1, `tasks.md:452`; `03` 1.6 | open (with decision 9) |
| 7.7 | Formula checks in the ID reconciliation `mutate` | FORMULA-SAFETY-1, `tasks.md:123`; `03` 1.7 | built; her confirmation open |
| 7.8 | Packaging of `test_lab` and `id_reconciliation` (Dockerfile, install script) | DOCKER-RELEASE-1, `tasks.md:271`; `03` 1.8 | open |
| 7.9 | Design parts planned and never built (confirm each match, several files, the transformation file's audit log, per-column synthetic config, scenarios on screen, several-file anonymisation, the session log) | `TEST_LAB.md`; `03` 1.9 | not built |
| 7.10 | The three ideas of the task | `tasks.md:347`; `05` | decisions 10 to 12 |
| 7.11 | Her two examples (synthetic data, the correct format) | `ORDER.md`; `03` 1.11 | decisions 4 and 8 |
| 7.12 | The anonymiser hint "reconcile ids first" | `developer_workflow.md:245-250`; `03` 1.12 | open question in that file |
| 7.13 | The Info panel text (placeholder) | `home_theater.py:1954-1966`; `03` 1.12 | with decision 1 |
| 7.14 | Side panels of the Test Lab like HOME's | D-0381 | decided as the working direction, not built |
| 7.15 | Rule file proposals R077 to R086 | `RULE_FILE_CHANGES.md:146-155`; `03` 1.12 | proposed (R078: she chooses) |
| 7.16 | The Test Lab in the configuration review (developer-only in its target) | CONFIG-REVIEW-1, `tasks.md:196` | with decision 2 |
| 7.17 | Code to move to `libs/utils` (type guess, slug rule, delimiter rule) | UTILS-REUSE-REVIEW-1, `tasks.md:179` | with decision 9 |
| 7.18 | The unused panel type `test_lab`; the synthesizer's legacy command line | `sidebar_registry.py:95-101`; `aqua_synthesizer.py:305-458`; `03` 1.12 | with decision 9 |

---

## 8. Not verified

- Nothing in this review was seen on a screen. Every statement about the screen is read from the code.
- No test suite was run; test counts are counts of `def test`. The strict expected failures were read, not run.
- The viewpoints' probes were not re-run by this guide; their results are labelled "ran (viewpoint)" in `06_proposals_one_table.md`.
- The HOME finding (X1) was run by the architect on two functions and one recipe (`simple_template.yaml`), not through the panel; the coordinator verifies it separately.
- Excel conversion (`007`), a decimal comma, HOME's Data Import on stress files and on `anon_` columns, the file name the anonymiser writes through a real upload (section 3, items 3 to 5).
- What the owner meant by the three ideas: no source says it; the readings are `05`'s.
- The order between BLUEPRINT's rebuild and the Test Lab's: D-0048 does not state it.
- Line numbers: the code moves with the HOME and GALLERY work in `dev`; re-read before relying on one. On 2026-11-21 the Test Lab files, `DI` and the ingestor were unchanged in this branch since `514a54a4` (`git log -1` on those paths).
