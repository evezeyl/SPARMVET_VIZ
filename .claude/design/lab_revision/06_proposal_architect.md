<!-- copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/architect.md of the main tree (not in git; written 2026-11-21 night, step 4 of TESTLAB-REVIEW-1); a viewpoint's proposal: it recommends, it decides nothing -->
# Test Lab, step 4: the software architect's proposal (one round)

Viewpoint: software architect (dasharch: smart simplicity, decoupled, audit-ready). I recommend; I decide nothing. Date 2026-11-21. Tags: DECIDED / CONFIRM / OPEN / MINE. Evidence labels: **ran** (I ran it, script in `tmpAI/panel/lab_step4/arch_check*.py`), **read** (file:line), **reasoned**, **assumed**. Short names as in `04_what_test_lab_must_be.md`: `H` = `app/handlers/test_lab_handlers.py`, `AQ` = `libs/test_lab/src/test_lab/aqua_synthesizer.py`, `SC` scaffolder, `BS` bootstrapper, `RF` reformatter, `AN` anonymiser, `DI` = `app/handlers/data_import_handlers.py`, `ING` = `libs/ingestion/src/ingestion/ingestor.py`.

## Summary (6 lines)

1. A new fact decides the shape of the whole rebuild: the app has TWO definitions of "the format a file must have", and they disagree (ran, section 1.1). Until one exists, no Test Lab tool can promise "this file is in the correct format".
2. Whatever is chosen, every Test Lab tool should have one contract: a headless library function that returns the file(s), a record of settings and seed, and a list of notices (what the tool did that the user did not choose). The screen and the record show the same list. This is approach A's core and it is also needed by B, C and D.
3. I recommend A as the base, with B's recipe-aware part added as an OPTIONAL second step, built on ONE check function that HOME's Data Import and the Test Lab both call. I do not recommend C as written (it keeps five writers and fixes defects in a space whose job is not decided) or D now (three open decisions outside the Test Lab, and it puts recipe authoring in the wrong space, D-0102).
4. The "choice of 2026-11-08" that B reverses is a code comment about the Info panel text (`app/handlers/home_theater.py:1955-1960`); I find no ledger line and no ADR for it (grep). It is CONFIRM, a smaller reversal than the brief says.
5. A leaves two gaps that must be named to her: ID reconciliation has no place in A's list, and its only consumer is the scaffold that A moves out; and "shown in the scientist setups" puts real personal data into the app, the opposite of what ADR-097 point 8 recommends.
6. The three ideas are not Test Lab tools: idea 2 is a template pattern, ideas 1 and 3 are recipe authoring (BLUEPRINT's ground by D-0102, D-0306); the Test Lab may at most REPORT (section 6).

---

## 1. What I checked (facts the proposal rests on)

### 1.1 Two definitions of "the format a file must have" (ran; a bug of HOME, not of the Test Lab)

- The ingestor reads a file strictly: each declared field is found by its `original_name` (the slug if none), then renamed to the slug (read: `ING:109-135`, comment "Strict import (Eve 2026-11-13, spec O22)").
- HOME's Data Import panel checks an uploaded file with `MetadataValidator.validate` on the declared KEYS (the slugs), then `apply_declared` (read: `DI:272-315`; `libs/transformer/src/transformer/metadata_validator.py:27-35`). It does not use `original_name`.
- Ran, recipe `config/data_analysis_recipes/templates/simple_template.yaml` (fields `sample_id` with `original_name: ID`, `value` with `Measurement`, `group` with `Group`): a file with the headers the recipe itself reads (`ID, Measurement, Group`) is REFUSED by the Data Import check ("Missing columns: ['sample_id', 'value', 'group']") and ACCEPTED by the ingestor; a file with the slug headers is ACCEPTED by the Data Import check and REFUSED by the ingestor (`arch_check5.py`). Not seen in a browser.
- Consequence: today a user cannot get a file through HOME's Data Import for any recipe that uses `original_name`, with either header spelling that also works at run time. Every Test Lab output headed for HOME meets this. Reported as a finding for HOME; the Test Lab cannot fix it, but any approach that says "checks the format" is built on sand until it is fixed. Class: software bug (HOME Data Import), to be filed.
- Also read: Data Import copies the accepted file over the recipe's data file with no existence check and no backup (`DI:326-337`, `shutil.copy2`). A Test Lab file (synthetic or reformatted) replaces real data silently. Point of no return of every hand-off by file; the Test Lab is not the place that can stop it.

### 1.2 Synthetic data (ran, `arch_check1.py`, `arch_check2.py`)

- `AQ.generate(config, seed=7)` twice gives the same frame and the same bytes of TSV, also from two separate processes (hash `a05b3a53...` both times). Without a seed two runs differ. So the library can already be reproducible; the screen calls it without a seed (read: `H:639`, `synth.generate(config)`).
- With a seed, `generate` calls `np.random.seed` and `random.seed`: the process-wide state of the whole app changes (ran: `random.random()` after `generate(seed=7)` differs from before). Any other code using the global state is affected, and two users of one server share it. MINE: the library must take its own generator object.
- Planted errors give no list of where they are: `_apply_error_injection` returns only the frame (read: `AQ:220-300`).
- From a list of column names every column becomes `categorical` (ran: `n_reads` is categorical); only a sample file gives numbers (read: `AQ:135-173`, `pl.read_csv` with inference, so an all-digit id column is read as an integer). Types come from guessing, not from the recipe.
- A planted wrong type (`"ERROR"` in a column declared `Int64`) is refused by `apply_declared` with a message naming the column and the values (ran). So planted type errors never reach the recipe's steps: they test only the ingestion message. Planted errors that pass ingestion (a duplicate id, an orphan id, a value out of range, a spelling variant) are the ones that test a recipe's wrangling. What a planted error proves must be said on the screen (scientist's weight; stated here because it sets the design of the error list).

### 1.3 Duplication today (read)

| Job | Implementations (all read) |
|---|---|
| Write a recipe | `SC` (own dictionaries), `BS` (own dictionaries), `utils.recipe_factory` (checks `id` equals file name; keeps key order; `minimal_schema(..., entity_key=, null_values=, strip=)`), `assets/scripts/create_data_analysis_recipe.py` (264 lines, uses the factory, writes a first plot), `assets/scripts/SF_create_data_analysis_recipe.py` (83 lines, no plot) |
| Infer a type from a sample | `BS._map_dtype` (threshold 15), `SC._infer_fields`, `AQ._infer_from_tsv` (own constant 15, own vocabulary: integer, float, categorical) |
| Excel to text | `RF` (`pl.read_excel(sheet_id=0)`), `EX` (same call), `libs/ingestion/src/ingestion/excel_handler.py:54`, `DI:303` (first sheet only, cast to text) |
| Synthetic tables | `AQ`, `assets/scripts/generate_demo_data.py` (several tables, one set of ids, a seed), two `make_*_data.py` scripts |
| Record of settings | `anonymisation_config.yaml` (`AN`), `synthetic_data_config:` (`AQ.save_config`, with the firewall header of `rules_test_lab.md` section 3), `id_transformation.yaml`, nothing for `RF` and the scaffold |

### 1.4 Headless reading of a recipe is possible without a peer import (ran, `arch_check3.py`)

`utils.recipe_loader.load_recipe` (Tier 1, `libs/utils`) returns the resolved recipe with `!include` followed; `data_schemas[<table>].input_fields`, `null_values`, `strip`, `source` are plain dictionaries. `libs/test_lab` already imports `utils` (read-1). `ingestion/declared.py` imports only `utils` and `polars` (read: lines 14-22), so it could sit in `utils` without breaking Clear Lines; or the app layer (a handler may import several libs) composes. `RecipeGraph.declared_entity_keys(table)` and `key_families()` exist (read: `recipe_graph.py:395,426`), so "which tables share a key" is already computed once.

### 1.5 Testability (read)

`H` is 1007 lines with 112 defs and holds journey logic: defaults read with `except Exception` and a silent fallback (`H:~408-424`: the join key falls back to `sample_id` silently), the choice of the file for the cleaning steps, the order of operations. Only `app/tests/test_id_cleaning_steps_reach_a_recipe.py` and `test_click_reads_visible.py` mention Test Lab handlers (grep). The libraries have headless tests (111 functions, counted by the earlier step). What a headless test would not catch: the Shiny upload names `0`, `1` (tests use real file names, V9), the real download, and the wording on screen.

---

## 2. What every approach needs (the contract of a Test Lab tool) - MINE, to confirm

These do not belong to one approach; they are the "one way" that the rules ask for. Each is smaller than any of A to D.

| # | Rule | Why (rule or decision) | Where it lives |
|---|---|---|---|
| T1 | A tool is a headless function: inputs (paths, settings, a seed if random) to a result with three parts: the files, a record, a list of notices. The handler only reads inputs and offers downloads. | Two-Category Law; testable without a browser; ADR-084 point 1 (stateless) holds | the tool's library; no Shiny |
| T2 | The notices are written once and shown twice: on screen and in the record. Today `H` already has the idea ("what the form did that the user did not choose; shown under the result", read: `H:~417`, D-0050). | the screen and the record cannot disagree; "what each tool did, in plain words, at the moment of the choice" | result object |
| T3 | One shape of record for all tools, a sidecar file next to the data file: tool name and version, app version, library versions (numpy and polars are `>=`, unpinned, read: `libs/test_lab/pyproject.toml`), date, input file names with a hash, every setting, the seed, the output names with a hash, the notices. A TSV cannot hold a comment line (HOME reads the first line as the header), so the record cannot be embedded. | D-0004 reproducible, D-0056 seeds written, goal text | a small writer in `libs/utils` (two libs need it: `rules_test_lab.md` 2c) |
| T4 | A seed is an explicit setting, shown, with a default written in the record; the generator uses its own `numpy.random.Generator`, never the global state. | D-0056 (about recipes; applying it to Test Lab files is MINE), ran 1.2 | `AQ` |
| T5 | What reproducible means is tested: same input and settings give the same BYTES of the data file (the record has a date, so it differs). | goal text "the same data and recipe give the same result" | a test per tool |
| T6 | No `except Exception` with a quiet default in a handler; a missing input is a message. | D-0050 | `H` |
| T7 | One inference of types from a sample, shared, and its result shown to the user as a proposal to confirm. | D-0015, D-0082, D-0225 (an id never becomes a number) | `libs/utils` if two spaces need it (BLUEPRINT's table entry, the Test Lab) |

Amends: `rules_test_lab.md` section 3 (the firewall header of the synthetic config: the record would take its place or sit beside it; the firewall's aim, "never loaded as a recipe", is kept by a distinct root key); ADR-084 point 4 (same). Not amended: ADR-084 points 1, 2, 3, 5, 6.

---

## 3. The four approaches

### 3.A. A small, safe toolbox for every user (reformat, anonymise, reproducible synthetic data)

**By journey**

| Journey | What the user sees and leaves with | Exists / extend / missing |
|---|---|---|
| J1 reformat | The file, the delimiter that was guessed AND shown (changeable), the sheets (all listed, which are ticked shown), rows and columns found, the first rows as text. Leaves with the TSV (or one TSV per sheet) and the record. Next: HOME Data Import by file. | Exists: `RF.convert_xlsx/csv/folder` (read: `RF:42,87,122`). Extend: show the delimiter, counts, record, read cells of Excel as text so `007` stays `007` (V5, not verified). Missing: any statement that the file fits a recipe. "Correct format" = TSV (reading 1 of `04` J1). |
| J2 synthetic | Sample file or names; the number of rows; a seed field; the error kinds with the planted counts; a result that says how many errors of each kind were planted and where. Leaves with the TSV and a record holding the config, seed, versions and the list of planted errors. | Exists: `AQ.generate(seed=)`, `save_config`, `load_config`, named scenarios (read). Extend: own generator (T4), planted-error list, the four error kinds not on screen, several tables from one set of ids (D-0205; the demo script does it, `AQ` cannot). Missing: dates, free text; a "make it again" from a record. |
| J3 ids | Not in A's list (see cons). | `libs/id_reconciliation` (read). |
| J4 anonymise | Files, id column, personal columns; the table and the KEY (mapping) as two separate downloads, with a line before the download: "the key brings the real ids back; keep it outside the place where you share the table". Several files with one mapping (`AN.anonymise_batch` exists). The id column keeps its name or the renaming is shown. | Exists: `AN.anonymise`, `anonymise_batch`. Extend: no `anon_` rename without a notice, the empty-id crash (ran in step 1), the hash pattern (unsalted, 8 hex characters, read `AN:46-47`), record. |
| J5 recipe | Not in the Test Lab: BLUEPRINT or a script. | Scripts exist (section 1.3). BLUEPRINT's table entry is its open choice #1 (BLUEPRINT review). |

**Pros.** Smallest change that makes the two examples she gave true ("testing from synthetic data", "preparing data files"); every tool is stateless and independent (ADR-084 point 1); the library is mostly there; no new recipe reading, so no reversal; the record is one shape (T3). The tools do not depend on the recipe format, so a format change does not touch them.

**Cons and pitfalls.**
- "The correct format" stays the weaker meaning (TSV). A user takes a TSV to HOME and learns there, not here, that it does not fit (and today HOME's check disagrees with itself, 1.1). The Test Lab would produce a file it cannot say is usable.
- ID reconciliation (J3) is missing from A's list. Its output has one consumer, the scaffold (read-1: `H:366-401`, "Bake in ID Reconciliation steps"). If the scaffold moves out, J3 has no next place: BLUEPRINT's upload takes a whole recipe `.yaml` and puts its steps on the step stack (read-1: `wrangle_studio.py:225-226`); whether it would read `id_transformation.yaml` is not verified. So A must say what happens to J3: stays with its own downloadable steps, goes to BLUEPRINT, or is dropped. OPEN.
- Moving the scaffold "to BLUEPRINT or to scripts" decides one of BLUEPRINT's open choices by the side (how a table enters a recipe, (a) Test Lab boilerplate, (b) a table and field editor, (c) a branch copy; BLUEPRINT review, To decide #1). Both spaces are rebuilt last (D-0048, D-0271), so until BLUEPRINT is rebuilt a scientist has NO screen path from files to a recipe, only scripts. Not a half fix if said openly; it is a gap if not.
- "Shown in the scientist setups" for anonymisation puts real personal data into a running app and its temporary upload folder (assumed: Shiny keeps uploads in a temp path for the session). ADR-097 point 8 says sensitive data is a documentation concern and recommends anonymising "before data ever reaches the app, with any de-anonymisation key kept outside it entirely". The tool in the app contradicts the recommendation unless the deployment is the user's own machine. CONFIRM. Option inside A: the anonymiser as a script that runs locally (`assets/scripts`) and an in-app tool only where the deployment is local.
- A synthetic or anonymised TSV, once taken through HOME's Data Import, is renamed `<table>.tsv` and copied over the data file (1.1): nothing marks it as synthetic any more. The record stays with the user; the data does not carry it. What marks a synthetic file inside its content (an id prefix, a column the recipe ignores) is a design question, because an undeclared column is ignored by the recipe (D-0374 context). OPEN, and it matters for science: synthetic results mistaken for real.

**What could change a result silently or hide a step in A.** A delimiter guess not shown (`RF`, read-1: by file ending); "no sheet ticked means all" (read-1: `H:979`); Excel number cells written as numbers into an id column (V5); `AN` renaming the key column; a seed set globally (1.2); a planted-error list missing, so the user cannot tell what was planted.

**Asks of BLUEPRINT and HOME (hand-offs are files, ADR-093).** HOME: nothing new, but the Data Import check must be fixed (1.1) and should tell the user that the target file is replaced. BLUEPRINT: the table entry decision; and whether it opens a steps file from J3.

**Larger decisions A needs first (ranked).** 1) Who sees which tool (flags per tool: `test_lab_enabled` is one flag for all five today, `app/handlers/home_theater.py:1835`, `sidebar_registry.py:91-101`; A needs at least two groups; amends `rules_app_features_flags.md` and the target of CONFIG-REVIEW-1). 2) Anonymisation in the app against ADR-097 point 8. 3) The record and the seed (T3, T4). 4) J3's place. 5) What marks a synthetic file. **Can wait:** dates and free text, the other error kinds, named scenarios on screen, the words of the help.

### 3.B. A companion to a chosen recipe (check or reshape against its declared fields; synthetic data from them; ids on its keys)

**The point of B for an architect.** The format a file must have is declared in the recipe (`input_fields`, `null_values`, `strip`, `original_name`; D-0082 keys declared; format 1). B is the only approach that uses the recipe as the single source of truth for "the correct format". That is also its risk: today the source is not single (1.1).

**By journey**

| Journey | What the user sees and leaves with | Exists / extend / missing |
|---|---|---|
| J1 check or reshape | Picks a recipe and a table. Sees, in plain words: columns the recipe expects and does not find (with the validator's closest-spelling hint, never applied without a click), values that do not fit the declared type (column and values, as `apply_declared` says), what `strip` and the null words would do. Leaves with the file, changed only by what the user ticked, plus the record. The check is the SAME function HOME runs at ingestion, so "passes here" means "the ingestor accepts it". | Exists: `load_recipe` (ran), `apply_declared`, `MetadataValidator`, the ingestor's strict import. Missing: all of them as ONE headless function (today inline in a handler, `DI:272-315`, and disagreeing, 1.1); a recipe list for the Test Lab (it reads no location today, read-1 `02` J). |
| J2 synthetic | Types, entity key (declared, so F5 and D-0082 are met by construction), null words and several tables on ONE set of ids (from `key_families`, D-0205) come from the recipe. Errors are planted in two labelled groups: "the ingestion will refuse this" and "this passes ingestion and tests the steps". Leaves with TSVs, a record, the list of planted errors. | Exists: `AQ` engine, the demo script's idea, `RecipeGraph.key_families` (read). Missing: a generator driven by declared fields. |
| J3 ids | The two key columns are the recipes' declared keys, not chosen from a list by name. The result is a steps file. Writing the steps INTO a recipe is a recipe edit and stays with BLUEPRINT (D-0102). | Exists: the engine. Missing: link to declared keys; a consumer of the steps file. |
| J4 anonymise | The id column keeps its declared name (no `anon_` rename), so the recipe still reads the file; the sequential id stays a string (D-0225); the key as a separate download. Personal columns are still the user's pick (the recipe does not know them). | Extend `AN`; the rename is the defect to remove. |
| J5 recipe | Not B's job: B starts from a recipe that exists. A user with no recipe has nothing here. | - |

**Pros.** One definition of the format (once 1.1 is fixed); the file check is as strong as the engine's own reading; synthetic data has the right types and keys, so a test is a test of THIS recipe; fixes F4, F5 by construction; no second type inference needed for J1 and J2 (T7 shrinks). The library stays recipe-free if it takes a plain mapping of declared fields (the handler reads the recipe), so `libs/test_lab` gains no peer import.

**Cons and pitfalls.**
- It reverses the 2026-11-08 comment, CONFIRM (section 5). It couples every tool to the recipe format: a format 2 means the Test Lab must follow. Mitigation: the reading is one function in `utils` (`load_recipe`), the same one as everywhere.
- A new dependency on the recipe places study (D-0394, open): the Test Lab needs a list of recipes to pick from and a rule for a user's own recipe. In the meantime: a recipe uploaded for the run (stateless, ADR-084 point 1), which needs no place.
- "Passes the check" can be heard as "the recipe will work". It means only: the file is read by the declared fields. A file that passes ingestion can still break the steps. The screen must say what was and was not checked.
- Double cleaning: if the Test Lab APPLIES `strip` and the null words to the output, HOME applies them again and the two can drift. The Test Lab must check and report; it must not clean content (reshaping = what the user ticks: rename a column, choose a delimiter). MINE.
- D-0374: informing about undeclared file columns "belongs to the user space BLUEPRINT" (DECIDED). A B that lists undeclared columns would do BLUEPRINT's job. CONFIRM: B stays silent on them or the owner moves the line.
- The check function must be extracted from `DI` and `ING` and `DI` must call it: that is a change in HOME (a bug fix in effect). Do it once, with a test that fails if the two disagree again (ran: a two-line test on `simple_template.yaml`).

**Silent-change risks.** Suggested renames accepted by default; the preview shows `strip` applied but the output is raw (say so); a check on the first 100 rows only (as `AQ` reads) would hide a bad value further down: the check must read the whole file as HOME does.

**Asks of BLUEPRINT and HOME.** HOME: the extracted check function (HOME's own fix, 1.1); the file replaced notice. BLUEPRINT: nothing new for B itself; D-0374's line.

**Larger decisions B needs first (ranked).** 1) The single definition of the file format and the fix of 1.1 (HOME). 2) The Test Lab reads a recipe: yes or no (CONFIRM against the comment). 3) Where the Test Lab gets a recipe (upload, or the places study). 4) D-0374 for undeclared columns. **Can wait:** several tables on one set of ids; J3's link to keys.

### 3.C. Keep today's tools, fix the defects, make the hand-offs work

**By journey.** J1, J2, J3, J4 unchanged in shape: the defects of `04` section 4 are fixed (seed and settings in the download, id kept as text, key declared by the user, no silent `sample_id`, no `anon_` surprise). J5: the scaffold writes a loadable recipe with a first plot through `utils.recipe_factory`; the ZIP goes to the user's own recipe place; the tools stay developer-only, flags per tool; the three ideas wait.

**What exists / missing.** Exists: all five tools, the factory, a script that already does the J5 job (`create_data_analysis_recipe.py`, 264 lines). Missing: the user's own recipe place (D-0394, the places study is OPEN: C's J5 hand-off depends on it); a loadable draft decision (`tasks.md:220`, shared with BLUEPRINT).

**Pros.** The least that makes today's tools honest. The scaffold fix is not wasted: its logic belongs in `utils` and survives a later move.

**Cons and pitfalls.**
- It keeps FIVE recipe writers until someone chooses (1.3) unless C includes the removal: "one authoritative way" (`rules_legacy_management.md`). A fix of `SC` without deleting `BS` or the scripts is a half fix (rule 4 of the principles).
- It leaves the file-format question (1.1) open: the Test Lab still cannot say a file will be accepted.
- A first plot the user did not ask for: a plot is a statement about the data (bar chart of the first column, `recipe_factory._default_plot`). It must be shown as a placeholder ("Rows per ...", as the script does), not left as if chosen. D-0015.
- "Still developer-only" fixes the audience before the owner has said it (her words: "for the user"). CONFIRM.
- It writes into a recipe place whose overwrite and naming rules are open (D-0390 `name_date`, D-0392 production recipes only, D-0394 overwrite only in the user's own directory). A scaffold is a draft, and a draft is not a "real production recipe" (D-0392), so the name rule may not apply: OPEN (04 To decide 12).

**Silent-change risks that stay.** Inner join of every table to the first (K1 of 02) unless the join is written as `joins: {}` or marked "to check" with the rows without a partner shown; the cleaning step that breaks matched ids (J3).

**Asks.** BLUEPRINT: must open the file the scaffold writes (a recipe `.yaml` in the recipe place). HOME: none.

**Larger decisions C needs first.** 1) Audience and flags. 2) A loadable draft (shared with BLUEPRINT). 3) The user's own recipe place. 4) Which one recipe writer stays. 5) Join in the scaffold. **Can wait:** everything of J2 beyond seed and record.

### 3.D. The Test Lab as the recipe starter (scaffold, tool-specific recipes from fragments, format detection, pilot extraction; reports what recipes share; BLUEPRINT edits)

**By journey.** J5 becomes the centre: the user drops files; the Test Lab recognises a tool's output (format detection), writes a recipe from per-tool fragments (`ResFinder_input_fields.yaml` and others exist, read: `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/`), can cut a smaller recipe from a large one, and reports which tables two recipes share. J1 to J4 remain as helpers.

**Exists / missing.** Exists: fragments per tool, `RecipeGraph` (`lineage_back`, `source_tables`, `same_t1_definition`, one recipe at a time), BLUEPRINT's branch plan, the frozen one-file export. Missing: a list of known tool formats (grep: none), a cut-out writer, a combine writer, behaviour on two recipes at once (not run).

**Pros.** Uses what the app already knows about tools; makes the first recipe fast; puts the user's first contact with a recipe where she can start from files.

**Cons and pitfalls.**
- It puts recipe authoring in the Test Lab. D-0102 (full recipe edit only in BLUEPRINT) and D-0306 (BLUEPRINT builds the WHOLE recipe) point at BLUEPRINT. "The Test Lab reports and BLUEPRINT edits" is a clean split only for idea 3 (report); a cut-out (idea 1) and a template (idea 2) WRITE a recipe.
- A list of known tool formats is a store that goes stale when a tool changes its columns, and a wrong detection is a silent choice by the software (D-0015: it may propose, not choose).
- Share or copy of fragment files (shared: one edit changes two results; copied: drift): "nothing changes a result silently" (goal text). Plot ids must be unique over all recipes (checker X5, read: `utils/recipe_check.py:1287-1296`). Names and places are open (D-0390 to D-0394).
- Reads a recipe: same CONFIRM as B.
- Biggest build, three decisions it cannot make alone (places, plot ids, share or copy); it asks BLUEPRINT to wait or to duplicate.

**Silent-change risks.** A fragment shared between two recipes; a detected format applied as if chosen; a cut-out whose plot ids differ from the source.

**Asks.** BLUEPRINT: open and edit what the Test Lab writes; settle the table entry; branch and combine live there. HOME: none.

**Larger decisions D needs first.** 1) The recipe places (D-0394, open). 2) Share or copy. 3) Plot ids across recipes (X5). 4) Where recipe authoring lives (D-0102, D-0306). 5) A list of known formats and who keeps it. **Can wait:** everything for J1 to J4.

---

## 4. Where each approach reconsiders a decision or amends a record

| Item | A | B | C | D |
|---|---|---|---|---|
| The 2026-11-08 comment "Test Lab tools don't operate on an open data analysis recipe" (`home_theater.py:1955-1960`; only a code comment, no ledger line, no ADR; the 2026-11-18 review calls it "Eve's decision", `2026-11-18_test_lab_review.md:125`) | no | yes (reads a recipe; note: the comment is about the Info panel and an OPEN recipe in HOME, B reads a CHOSEN one) | no | yes |
| D-0102 full recipe edit only in BLUEPRINT; D-0306 | no | no (check and report, no edit) | no | pressed (ideas 1, 3 write recipes) |
| D-0374 undeclared columns belong to BLUEPRINT | no | pressed unless B stays silent | no | no |
| ADR-084 | point 4 (config header) amended by the record | same | point 6 vs the scaffold join (K1) | points 5 and 6 stretched: the Test Lab writes more than boilerplate |
| `rules_test_lab.md` | section 3 (firewall), section 4 (what the scaffold writes), the boundary greps | same, plus a rule on reading a recipe | sections 3 and 4 | sections 3, 4 and prohibition 4 (no analysis_groups from the bootstrapper) |
| ADR-097 point 8 | CONFIRM (anonymiser in the app for everyone) | same | same (developer-only) | no |
| ADR-082 against ADR-084 point 3 (pattern helper sharing, K6) | no | no | no | possibly |
| Flag rules (`rules_app_features_flags.md`, ADR-071) | per-tool flags | same | per-tool flags | same |

DECIDED and respected by all: recipe format 1, D-0225, D-0082 (A and B need the user to declare or confirm the key; C and D must stop guessing it), D-0050, ADR-084 points 1 to 3.

## 5. The question "does the Test Lab read a recipe" is smaller than the brief says

- The brief and `04` J1 call it a reversal of "the choice of 2026-11-08". What I read: a docstring in `_render_test_lab_info` says "Eve, 2026-11-08: deliberately distinct from data_analysis_recipe_info. Test Lab tools don't operate on an open data analysis recipe at all, so showing recipe info: content here is actively wrong" (`app/handlers/home_theater.py:1955-1960`). The decision is about the text of an Info panel, and the reason is "the open recipe in HOME is not what the tools work on". I grep the ledger for Test Lab lines: D-0048, D-0271, D-0381, D-0396 only, none on this. ADR-084 has no sentence forbidding a recipe as an input.
- B reads a recipe the user CHOSES for one run, not the one open in HOME. Whether she meant to forbid that is CONFIRM, and it is for her to say; the architecture allows either. If the answer is yes, the Info panel text can say what the tool read.

## 6. Where the three recipe ideas belong (architect)

| Idea | Size (as in `05`) | Boundary | My reading |
|---|---|---|---|
| 2 tool-specific recipe | small to medium | a template or a fragment library, files in the recipe places; if the tool must DETECT a format, a store of known formats | Not a Test Lab tool. A set of templates built from the existing fragments (`templates/`), kept with the shipped recipes, with a check that the plot ids are unique (X5). A "start from this tool's file" action belongs to BLUEPRINT's table entry. |
| 1 pilot (cut out) | medium | a recipe writer using `RecipeGraph` and `recipe_factory` | BLUEPRINT's ground (D-0102, D-0306; its branch plan is next door). Until then a script. |
| 3 combine | large | joins, keys, names, sessions of the source recipes | The Test Lab may REPORT what two recipes share (tables with `same_t1_definition`, plot-id clashes; informs, does not choose, D-0015). Writing the combined recipe is BLUEPRINT's, after its rebuild. I did not run the graph on two recipes at once. |

Reason in one line: all three WRITE a recipe; there must be one writer path (`utils.recipe_factory`, which keeps comments and checks `id` equals the file name), and one place that edits recipes.

## 7. Recommendation (one combination; Eve decides)

**A as the base (T1 to T7 for every tool), plus B's recipe-aware check and synthetic data as an optional second step, built on one extracted check function. Not C as written, not D now.**

Why, from the architecture:
1. T1 to T7 are needed whatever she picks, they are small, and they remove the three broken rules (D-0225, D-0082, D-0050) and the unreproducible synthetic data. They are testable without a browser (results are plain objects).
2. "The correct format" has one honest meaning: what the recipe declares and what the ingestor reads. B's check is the only way the Test Lab can say so, and it forces the one fix HOME needs anyway (1.1). It is optional, so a user without a recipe still has A.
3. The recipe starter (J5, ideas 1 to 3) is decided by BLUEPRINT's table-entry choice and the places study. Doing it first in the Test Lab would build twice. Until then the scaffold stays developer-only and unchanged except for what T1 to T7 touch, and the tools say so on screen. This is a gap, named, not a half fix.
4. It reconsiders only one code comment (CONFIRM) and keeps D-0102, D-0306, D-0374, ADR-084 points 1 to 3.

Order that follows from dependencies (facts, not time): the HOME check fix and the single check function; the record and seed (T3, T4); J1 and J2 on them; J4; B's optional step; then the scaffold and J3 once BLUEPRINT's choice exists. A, B and the HOME fix touch different files and can run in parallel.

What an audit or test would NOT catch in this plan: the Shiny upload names (use Shiny-shaped inputs in tests); a record that is complete but wrong about the file name (a real upload is needed); that the user understands the notices (words need real users); that a synthetic file is later taken for real data (nothing in HOME says so, 1.1); `audit_docs_sync.py` and the UML audit do not read the Test Lab diagrams against code (V8).

## 8. What the user must be told to choose well (not what to choose)

- Today the Test Lab cannot say that a file will be accepted by HOME: HOME's Data Import and the ingestor disagree (1.1, ran).
- "Correct format" can mean a text file (TSV) or "the columns, types and missing-value words one recipe declares"; the second needs the Test Lab to read a recipe the user picks, which changes a code comment of 2026-11-08, not a ledger decision.
- Anonymising in the app means the real ids and the key pass through the app; the ADR-097 recommendation is to do it before; the key and the table should be two downloads.
- A synthetic file is not marked once HOME renames it and copies it over the recipe's data file.
- Planted errors of the type kind are refused at ingestion and do not test the recipe's steps.
- Moving the scaffold out leaves no screen path to a first recipe until BLUEPRINT's table-entry decision is built; reconciliation of ids has no next place without the scaffold.
- Each tool would show: what it read (file, delimiter, sheet, rows, columns), what it chose by default and why, what it changed, the seed, and where the record is.

## To decide first (ranked)

1. What "the correct format" means, and that there is ONE definition (the recipe's declared fields as the ingestor reads them); includes filing and fixing the HOME Data Import disagreement (1.1). It decides A against B.
2. Whether a Test Lab tool may read a recipe the user chooses (CONFIRM: the 2026-11-08 comment, section 5), and how it gets one (upload, or the recipe places study D-0394).
3. Who the Test Lab is for, per tool (flags per tool; the audience of anonymisation against ADR-097 point 8).
4. What every file carries: one record shape, a seed, library versions, hashes, notices; and what marks a synthetic or anonymised file once HOME has copied it over a data file.
5. Where a recipe starter lives (Test Lab, BLUEPRINT, script), which one recipe writer stays, and what J3 (ID reconciliation) does when the scaffold leaves; shared with BLUEPRINT's table-entry choice and the loadable-draft question (`tasks.md:220`).
6. Which of the three ideas are wanted; by my reading none is a Test Lab writer (section 6).
7. Later: dates and free text in synthetic data, the other four error kinds, named scenarios on screen, the several-table synthetic set, the words.

## Not verified

- Nothing was seen in a browser. The disagreement of 1.1 was run on the two functions (the validator plus `apply_declared`, and `DataIngestor._import_declared_columns` on an instance made without `__init__`), with a scratch file; not through the panel and not on other recipes than `simple_template.yaml`. A recipe without `original_name` would agree in both.
- The temporary upload folder of Shiny keeping personal files (assumed).
- That `load_recipe` reads a recipe with no plot or a draft in every case; that the recipe graph works on two recipes at once; that BLUEPRINT would open `id_transformation.yaml`.
- Excel cell types through `RF` (V5); the file name written by `AN` through a real upload (V6).
- That NumPy's legacy seeded streams stay identical across versions (external knowledge, not checked); hence the library versions in the record.
- I did not read all of `H` again: the `except Exception` defaults at `H:~408-424` are read at those lines; the rest is from step 1.
- The test functions were not run (no suite, by the brief).

Scratch scripts: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/lab_step4/arch_check1.py` to `arch_check5.py`, `simple_data.tsv`.
