# Impact report: check a recipe when it is selected (CHECK-ON-SELECT-IMPACT-1)

Date 2026-11-16. Branch `feat/recipe-format-1`, HEAD `36fc906c`. Nothing was built or changed. All runs were made on a scratch copy of HEAD (`git archive`), never in the tracked tree.
Labels: **ran** = I ran it; **read** = I read it at file:line; **reasoned** = my inference.
Machine: 12 cores, load average 3.5 to 6.5 during all measurements (other sessions were running tests). Values are wall seconds. Absolute numbers will be smaller on an idle machine; the ratios hold.

Decisions this report answers (all DECIDED, taken by EVE):
- D-0184: "A recipe is checked when it is selected, not all recipes at start."
- D-0185: "Measure the time of start at first load."
- D-0186: "Changing data is not necessarily a failure, but changing a recipe is."
- D-0165: "Where no decision exists and one is needed, that must be reported to her."

What is her decision and what is the review session's proposal (marked in the ledger line D-0184 and D-0185): her decision is the check on selection, the contact in the message, the measurement, and "data change is not a failure". The result kept by hash, the split in two parts keyed by the recipe file set hash and by recipe hash plus data hash, and the order of work are the review session's proposal. She has not confirmed them.

---

## Summary for Eve (read this first)

1. Today the app checks every recipe once when it starts. With the 7 shipped recipes this costs about 2.6 to 3.4 seconds of a 3.9 to 4.8 second start. With 100 copies of a small recipe the start is 15 to 16 seconds. With 500 copies it is 58 to 63 seconds. Without the check the start is 2 to 3.7 seconds in all three cases. So your fear is right: the cost grows in a straight line with the number of recipes, about 0.12 seconds per small recipe.
2. Removing the check at start is not enough to make the app fast with hundreds of recipes. Every new session also reads every recipe once, to register the plot slots (`home_theater.py:199`). That costs 0.25 s with 7 recipes, 1.3 s with 107 and 5.2 to 5.5 s with 507, for the first session after the app started. If we only remove the check at start we leave the second half of the problem in place. That would be a half fix.
3. The check on selection costs about 0.1 to 0.5 seconds per recipe on the shipped recipes and data (structure 0.04 to 0.33 s, data 0.02 to 0.22 s). That is about as much as the work HOME already does on the first selection (0.02 to 0.25 s).
4. The data check looks at the tier-1 steps on ONE row only (`data_analysis_recipe_validator.py:395-404`). A step that fails on a value in row 2000 passes the check and fails later when the table is built, with the message "Data Assembly Failed: ..." that names no contact (`home_theater.py:894`). I ran this. After the change a user would read "passed" and then an error without a contact. This needs your decision (question 6).
5. Cases that would become silent or blank if we only remove the check: (a) the hidden selector with a failing default, (b) HOME opens a recipe that fails and draws an empty page without a message and without a contact, (c) the contact is lost on a data failure. Section 3 and section 7 give the order of work that avoids it.
6. Eight questions for you are in section 6. Most have a record that supports a default; three have none.

---

## 1. What runs at start today

**Path (read, then run).**
1. `app/src/bootloader.py:959` creates the one `bootloader` object when the module is imported. It runs once per process, not per session.
2. `Bootloader.__init__` (`bootloader.py:181-193`): finds every `*.yaml` in the recipes folder (`:372-385`), then runs `_validate_data_analysis_recipes` on all of them (`:189-191`), then records which files each recipe is made of so it can see changes (`:192`), then resolves the default recipe (`:193`, function at `:502-554`).
3. `_validate_data_analysis_recipes` (`:412-430`) calls `_gate_one` for each recipe (`:387-410`). `_gate_one` runs, in this order:
   - `validate_data_analysis_recipe(path)` (`data_analysis_recipe_validator.py:293-302`): the strict checker `check_recipe_file` (`:254-267`), then the engine load with `ConfigManager` (`:305-344`).
   - if no problem: `validate_data_analysis_recipe_data(path, raw_data_dir, ...)` (`:352-405`).
   - if a problem: `read_data_analysis_recipe_header` (`:408-425`) and `resolve_contact` (`:428-435`): the recipe's `info.contact`, then the deployment's `branding.contact` (`bootloader.py:498-500`).
   - if no problem: `checker_advices(path)` (`:270-280`), which runs `check_recipe_file` a second time on the same file.
4. A failing recipe goes to `rejected_data_analysis_recipes` with its problems and contact. The others go to `available_data_analysis_recipes`.

**What each step reads.**
- Recipe files: all of them, each time. `ConfigManager` reads the recipe and its includes. The recipe file is read about four times per recipe: checker, engine load, data check (another load), advices (another check). Reasoned from the code; I did not count the reads.
- Data files: the data check builds each dataset through `DataOrchestrator.prepare_ingredient` (`orchestrator.py:108-139`): it reads the file, applies the declared types and runs the tier-1 steps lazily.
- Tier-1 steps on all rows or on one row: **one row**. `frame.head(1).collect()` at `data_analysis_recipe_validator.py:396`. The ingestion step that applies the declared types does read the whole column: I ran a bad value in the last of 2000 rows and the data check found it (type error, "dataset cannot be loaded"). But a tier-1 step that fails on a value (a text cast to a number) is only seen if the bad value is in row 1. Run, same recipe, 2000 rows, step `polars_cast Int64 strict`:

  | where the bad value "abc" is | data check says | the real build says |
  |---|---|---|
  | no bad value | NO PROBLEM | OK |
  | row 1 | "wrangling cannot run on this dataset: conversion from `str` to `i64` failed ..." | fails |
  | row 2000 | **NO PROBLEM** | **fails**: "conversion from `str` to `i64` failed in column 'n' for 1 out of 2000 values" |

**What is checked again later, and when (read and run).**
- A recipe file (or an include, or a file under its mirrored folder) that changes while the app runs: `Bootloader.recheck_changed_data_analysis_recipes` (`bootloader.py:462-496`) compares a content hash of the recipe files and runs `_gate_one` again for the changed recipe. HOME calls it by a poll every 2 seconds per session (`recipe_gate_handlers.py:138-141`); Blueprint calls it after each save (`blueprint_handlers.py:266-282`). Run: edit one recipe, the recheck returns it in 0.03 s and it is rejected. With nothing changed the poll costs 0.003 s (7 recipes), 0.023 s (107), 0.027 s (507), per session, every 2 seconds. It hashes all recipe files of all recipes each time.
- **Data files are not watched.** Run: I changed a data file after the start so that a declared column is gone. The recheck returned `[]`, the recipe stayed in `available_data_analysis_recipes`, and the next build raised "Dataset 'A' could not be loaded for 'A': Column(s) ['a'] declared in input_fields ... not found". HOME draws it as "**Data Assembly Failed**: <that text>" (`home_theater.py:894`): no recipe-or-data wording, no contact.
- A **new** recipe file is not found while the app runs. `_discover_data_analysis_recipes` runs only in `__init__` (`bootloader.py:186`; the text at `:375-383` and `:469-470` says so). Run: I added `three.yaml` after the start; recheck `[]`, still not discovered.
  Side finding (read): the import of a reproducibility bundle writes a new recipe and tells the user "reload (F5) to see it in the selector" (`export_handlers.py:791`). F5 does not rediscover recipes; the app must be restarted. That message is wrong today.
- `ingestion_handlers.py:51` calls `bootloader.__init__(...)` again after a recipe upload. That reruns the whole gate on all recipes.
- Every new session also does an all-recipes read that is not the check: see section 4 (`home_theater.py:85-112`, called at `:199`).

---

## 2. Who reads the result

`available_data_analysis_recipes` today means: found on disk AND passed both checks at start (or at the last recheck). `rejected_...` means found on disk and failed.

| # | Reader (file:line) | What it does today | What it would do when nothing is known before selection (reasoned) |
|---|---|---|---|
| 1 | `bootloader.py:462-496` `recheck_changed...` | rechecks changed recipes; replaces the two dictionaries; raises `data_analysis_recipe_gate_version` | must be narrowed: recheck the open recipe only, or all recipes are still hashed every 2 s per session. Cost 0.027 s per poll at 500 recipes: small, but it is the only per-recipe cost that stays |
| 2 | `bootloader.py:502-554` `_resolve_default...` | default named by env var or deployment: not found = stop (`:521-529`); fails the gate and selector hidden = stop (`:532-541`); fails the gate and selector visible = falls through to the first valid one (`:542-544`) | cannot know that the default fails without checking it. This is case 3(a)/(b)/(h) below |
| 3 | `bootloader.py:556-582` `get_default...` and `..._or_none` | first available recipe if no default; raises when none | "first available" is no longer "first that passes". The raising form (still called at `home_theater.py:270,284,311,877`, `data_import_handlers.py:83,269`, `export_handlers.py:838`) stays correct only if "available" means "listed" |
| 4 | `bootloader.py:589-592` `has_usable...` | true when at least one recipe passed | means "at least one recipe file exists" |
| 5 | `server.py:92` `active_cfg` and `recipe_gate_handlers.py:120-130` `usable_config` | a recipe not in `available` or one that cannot be loaded gives an EMPTY stand-in (`SimpleNamespace(raw_config={})`) silently; about 15 readers only read `.raw_config` | **blank-page risk.** If `available` becomes "all listed", a failing recipe that is selected loads with an error, `usable_config` catches it (`ValueError`) and returns the empty stand-in with no message. This is the main silent case |
| 6 | `recipe_gate_handlers.py:146-173` selector follower | keeps the selector choices equal to `available`; moves to the first one if the open one drops | the selector would list all discovered recipes; the "drop and switch" logic only applies to the open recipe |
| 7 | `recipe_gate_handlers.py:86-117,188-194` notes under the selector | lists each rejected recipe with two problems and its contact, in red | empty at start. Could list the recipes that failed since the app started, if the result is kept (question 4) |
| 8 | `home_theater.py:841-875` | empty state "No data analysis recipes yet" with each rejected recipe; or "This data analysis recipe is not available" when the open one is rejected, using `rejected_recipe_text` | the text of `rejected_recipe_text` (`validator.py:438-448`) says "failed its checks after its files changed". That is wrong for a failure at selection. Needs a new text |
| 9 | `home_theater.py:1604-1611` selector choices | `available` keys plus the default | all discovered recipe names |
| 10 | `home_theater.py:894` build failure | "**Data Assembly Failed**: <engine message>", no contact | becomes the place where a failure on selection must be shown with what failed and the contact (D-0184) |
| 11 | `data_import_handlers.py:83,269`, `export_handlers.py:838` | take the default or the selected recipe through the raising form | unchanged if the selected recipe was checked first |
| 12 | `export_handlers.py:114,1425` and `export_refusal.py:35-` | export info and lineage read `available`; the export is refused (a zip with only `EXPORT_NOT_CREATED.txt`) when the recipe is in `rejected` | refusal must read the new result for the open recipe. If it only looks at the old dictionary the export of a failing recipe is no longer refused: silent |
| 13 | `ingestion_handlers.py:51-53` | `bootloader.__init__` again after an upload, then the selector choices | would no longer re-check all recipes after an upload (good); must refresh the list of files |
| 14 | `bundle_importer.py:309` | uses `available.get(original_id)` only to hash the original recipe for the "recipe" leg; guarded by try | works if the original is listed; no check needed |
| 15 | `blueprint_handlers.py:266-282` `tell_save_outcome` | after a save, rechecks and notifies "HOME will not use X until it passes" | stays valid for the open recipe; the text "HOME will not use" is still true |
| 16 | `blueprint_handlers.py:2938-3020` Validate | manual check of structure + data + advices; never blocks | unchanged. Becomes the same function as the check on selection (one function) |
| 17 | Session restore, `session_handlers.py` | does not read the gate at all (no `bootloader` call except the feature flag, `:63`); it applies the saved steps to the open recipe and warns if the recipe hash differs (`:349-358`) | unchanged; see case 3(g) |
| 18 | Gallery | does not read these dictionaries (own check, `gallery_examples.check_gallery_at_start`) | unchanged |
| 19 | Scripts in `assets/`, `scripts/`, libs | none read them (grep) | unchanged |
| 20 | `home_theater.py:95` `discovered_data_analysis_recipes` | all recipes, for plot slots, at every new session (section 4) | the part that keeps the 500-recipe cost alive |

Tests that name these readers: see section 5 and section 7 (list of tests that change).
Docs that name the start check: `docs/user_guide/system_transparency.qmd:44`, `docs/UML/data_contract_and_failures.md`, `docs/UML/app.mdj`, `docs/workflows/blueprint_architect.qmd:367` (Validate), the comments in `config/deployment/templates/deployment_template.yaml:41-45` and `config/deployment/demo/demo-vetinst.yaml:25`, `config/deployment/local/local.yaml`, and the rule and ADR texts in section 7.

---

## 3. The cases that must not become silent

All "today" results were run on the scratch copy with small recipes (a good one and a failing one, relative data paths). The deployment contact in the runs is `ops@example.org`; the failing recipe's own contact is `owner@example.org` where noted.

### (a) Hidden selector, the operator-named default fails
- Today (ran, pipeline-static): the app does not start. The operator reads on stderr:
  `[FATAL] The data analysis recipe 'bad' named by default_data_analysis_recipe failed validation.` `Fix: Fix the recipe's structure or data, or point default_data_analysis_recipe at a different recipe. Problems: bad.yaml: data_schemas.A: [S03] the schema has no label Tip: add label. Contact: owner@example.org.` Code `bootloader.py:532-541`.
- Same for a data failure (missing column): `Problems: bad.yaml: data_schemas.A: dataset cannot be loaded: Column(s) ['zzz'] declared in input_fields for 'A' not found in the source file ... Contact: ops@example.org.`
- Typo in the name (ran): "was not found ... Found: ['bad', 'good']" (`:521-529`). This one only needs the file list, not the check, and keeps working.
- No default named at all, selector hidden (ran): "The app features hide the data analysis recipe selector but no data analysis recipe is named." (`:545-553`). Also keeps working.
- After the change, if nothing is checked at start: the app starts, a user opens HOME, the default recipe is selected, the check fails. The message goes to an end user, not to the operator. Without care HOME draws the empty stand-in (reader 5). **This is the case your review session asked to hold.** Two safe versions (question 3): keep the stop by checking only the named default at start (one recipe, 0.1 to 0.5 s), or show the failure plainly in HOME with what failed and the contact.

### (b) Default fails, selector visible
- Today (ran): the app starts; HOME opens the first recipe that passes (`good`); the failing default is listed under the selector: "1 recipe(s) unavailable — failed data or structure check: bad ... [S03] the schema has no label Tip: add label ... Contact: owner@example.org". There is **no notice that the named default was not the one opened**: the notice (`follow_step`) only appears when a recipe that was open is dropped later. So this case is already half-quiet today.
- After the change: the named default is the one selected; the check runs; it fails; the message must say so. No other recipe is opened silently.

### (c) Every recipe fails
- Today (ran): the app starts. `available` is empty, `rejected` has both. The selector has no choices. HOME shows "No data analysis recipes yet" with "2 data analysis recipe(s) exist but failed validation (also listed in Data analysis recipe Choice in the sidebar). Open **Blueprint** to build one or **Test Lab** to bootstrap one from a file." (`home_theater.py:841-860`, text read; the Blueprint/Test Lab hint depends on the flags), then `rejected_recipe_text` for each. That text says "failed its checks after its files changed, so HOME does not use it", which is false for a start-time failure (read `:446`).
- After the change: the selector lists them all; the user picks one; the failure message shows. No "No data analysis recipes yet" state except when no file exists.

### (d) No recipe at all
- Today (ran): the app starts; no rejected list; HOME shows "No data analysis recipes yet" with "No data analysis recipe files were found." (`home_theater.py:851-875`, read). Unchanged after the change; this case does not depend on the check.

### (e) A recipe that fails only on its DATA
- Today at start (ran): a missing data file: `bad.yaml: data_schemas.A: dataset cannot be loaded: Failed to read 'NOT_THERE.tsv': FileNotFoundError: No such file or directory (os error 2): .../NOT_THERE.tsv Tip: Check that the file is a valid tab-separated file and that the declared fields match it`, then `Contact: owner@example.org` (the recipe's own contact; falls back to `ops@example.org`). A column of the contract missing: `dataset cannot be loaded: Column(s) ['zzz'] declared in input_fields for 'A' not found in the source file (expected file headers: ['zzz']). Tip: The file header must match original_name exactly ...` and the contact. The message names the failing table and column but does not say "recipe or data" and does not name the data file in the column case.
- Today after the start (ran): the data changes: no recheck, the recipe stays available, the build fails with "Data Assembly Failed: ..." and no contact (section 1).
- After the change: this is the case D-0185/D-0186 are about. A dataset that differs but fits the contract is no failure. A dataset that does not fit the contract is a failure of the pair (recipe, data): the message must say which data file and which column, that the recipe is not at fault, and whom to contact (question 5).
- Hole to close: the check reads one row of tier 1 (section 1). A failure on a later row is only found by the build, whose message has no contact (question 6).

### (f) A recipe whose file changes while it is in use
- Today (ran): edit the file, the recheck (poll, 2 s) rejects it; HOME draws "This data analysis recipe is not available" (`home_theater.py:867-872`) with "The data analysis recipe 'one' failed its checks after its files changed, so HOME does not use it. Problems: one.yaml: data_schemas.A: [S03] the schema has no label Tip: add label. Open it in Blueprint, fix it and save; HOME takes it back when it passes. Contact: owner-one@example.org." The selector moves to another recipe with a red notice (`recipe_gate_handlers.py:81-83`). The export is refused with `EXPORT_NOT_CREATED.txt` (`export_refusal.py`). Browser tests cover this (`test_shiny_gate_gap.py`).
- After the change: keep it. It fits D-0186 ("changing a recipe is" a failure). Narrow the watch to the open recipe. The poll must run the NEW check function (structure + data), not the old one.

### (g) A session restore or a bundle import that names a recipe that now fails
- Session restore (read, `session_handlers.py:333-420`): it does not look at the gate. It restores the steps onto whatever recipe is open and warns only if the recipe hash differs. A saved session of recipe X restored while recipe Y is open is warned (hash differs); it never says that X fails. After the change: no new silence, because it never asked. But if we want "recipe X fails" shown at restore, that is new work (question 8 asks about the session side; the review session is handling it in M175).
- Bundle import (read, `bundle_importer.py:188-340`): writes the recipe, its data folder and a session ghost; it does not run the checks on the imported recipe (the test does, `test_bundle_importer.py:249-258`). The recipe becomes selectable only after a restart today (the text says F5: wrong). After the change: the imported recipe is checked when it is selected, with the data folder of the import (`imports_dir`, passed already by `_gate_one`: `bootloader.py:397-398`). The check on selection must pass `imports_dir`, or an imported recipe fails on missing data.

### (h) A recipe selected by the environment variable for one run
- Today (ran): selector hidden: stop at start with the same [FATAL] text naming `SPARMVET_DATA_ANALYSIS_RECIPE`, the problems and the contact. Selector visible and the named recipe fails: **HOME silently opens another recipe** (`good`) and lists the failing one beneath (same as (b)). The user who typed the variable gets no sentence "your recipe X failed, I opened Y".
- After the change: same answer as (a) and (b).

**Summary of what becomes silent or blank if only the start check is removed:**
1. The hidden selector with a failing default: no stop, and HOME shows an empty stand-in (readers 5, 10).
2. A selected recipe that fails to load: `usable_config` returns the empty stand-in without a message (reader 5).
3. The export of a failing recipe is no longer refused (reader 12).
4. A data failure shows "Data Assembly Failed" without a contact (reader 10).
5. The text "failed its checks after its files changed" appears for failures that did not follow a change (reader 8).

---

## 4. Measurements (D-0185)

Setup. Scratch copy of HEAD, `SPARMVET_APP_FEATURES=qa` (the Blueprint agent is off, so no `claude` probe), local deployment, recipes `config/data_analysis_recipes/pipelines/` (7 recipes, 4.6 MB in `assets/test_data`, the biggest recipe `1_test_data_ST22_dummy` reads 11 tables, 807 rows, 312 KB). "Start" = from the start of the script to the end of `import app.src.main` (the Shiny `app` object is ready): imports plus `Bootloader()` plus the agent adapter. Probe: `bootloader.py` executed with the last line removed so that I could time the gate; "skip" replaces `_validate_data_analysis_recipes` by a stub that lists every file as available (my stand-in for "no check at start"; it is NOT the proposed design, only a measure). Each value is one run; three runs per cell, in order, one after the other.

### 4.1 Start time (seconds)

| recipes | check at start (today), 3 runs | check removed (skip), 3 runs | the check alone, wall of `_validate_data_analysis_recipes`, 3 runs |
|---|---|---|---|
| 7 shipped | 3.97, 3.87, 4.78 (a first run with cold file cache: 5.06) | 2.44, 2.02, 3.37 | 2.65, 2.73, 3.41 |
| 107 (7 + 100 copies of `3_test_no_joins`) | 15.20, 16.08, 15.33 | 2.54, 2.25, 2.15 | 13.91, 14.91, 14.19 |
| 507 (7 + 500 copies) | 61.93, 62.53, 58.26 | 3.75, 2.47, 2.01 | 60.17, 61.09, 57.14 |

Load average at the start of those runs: 4.5 to 5.5 (7 and 107), 4.9 to 6.5 (507).
The copies: `3_test_no_joins` (one table of 42 rows, 3.7 KB, no joins, 1 plot), file renamed and `id:` changed; the includes are shared with the original. Small on purpose; a real recipe with 11 tables costs more (4.2).
Cost per small recipe: about 0.12 s (13.2 s / 100 and 58.9 s / 500).
The difference start minus "skip" is a little smaller than the check wall because the check also pays the one-time import of the action and plot registries (about 1 s), which the app pays anyway when it imports the server. Run: after the app import the first `checker_catalogs()` costs 0.021 to 0.023 s.

Where the check time goes (sum over the recipes, 3 runs each; the rest is `checker_advices`, which re-runs the checker, plus the header read):

| recipes | structure function | data function | rest (advices) |
|---|---|---|---|
| 7 | 1.68, 1.85, 2.28 | 0.43, 0.42, 0.59 | 0.53, 0.45, 0.53 |
| 107 | 6.86, 7.44, 7.09 | 2.18, 2.28, 2.22 | 4.87, 5.18, 4.88 |
| 507 | 28.71, 28.99, 26.96 | 9.18, 9.12, 8.78 | 22.28, 22.98, 21.40 |

The advices step is about a third of the gate and is a duplicate: it runs the same checker a second time on the same file (`validator.py:270-280` after `:254-267`). A single call that returns errors and advices would remove it. (Reasoned from the code and the timings; I did not remove it.)

### 4.2 The check on the first selection (warm process, per recipe, 3 repetitions each)
"Today first selection" = what HOME already does when a recipe is first opened: load the recipe, compute the keys (hash of the data files), build tier 1 (recipe cache and stored table cleared before each repetition). The structure check, the data check and the advices are the new work.

| recipe (tables) | structure check, 3 values | data check, 3 values | advices, 3 values | today first selection, 3 values |
|---|---|---|---|---|
| 1_Abromics_general_pipeline | 0.229, 0.171, 0.160 | 0.092, 0.051, 0.058 | 0.050, 0.050, 0.050 | 0.065, 0.057, 0.058 |
| 1_test_data_ST22_dummy (11) | 0.317, 0.292, 0.289 | 0.215, 0.208, 0.207 | 0.274, 0.234, 0.200 | 0.214, 0.239, 0.207 |
| 2_test_data_ST22_dummy | 0.195, 0.078, 0.074 | 0.055, 0.047, 0.050 | 0.051, 0.049, 0.049 | 0.072, 0.098, 0.088 |
| 3_test_no_joins (1) | 0.152, 0.088, 0.091 | 0.039, 0.019, 0.015 | 0.036, 0.032, 0.034 | 0.024, 0.024, 0.025 |
| demo_abromics | 0.080, 0.056, 0.052 | 0.035, 0.026, 0.032 | 0.045, 0.036, 0.037 | 0.038, 0.036, 0.039 |
| figshare_integration | 0.162, 0.123, 0.124 | 0.070, 0.038, 0.039 | 0.041, 0.042, 0.042 | 0.131, 0.143, 0.114 |
| stress_test_master | 0.055, 0.037, 0.036 | 0.025, 0.019, 0.018 | 0.030, 0.029, 0.029 | 0.035, 0.041, 0.039 |

The first value of each structure and data cell includes first-call warm-up in that process (first use of the checker and engine); later values are the steady state. Load 4.2 to 4.5 during these runs. In the app the registry import is already paid at start (4.1), so the first-selection cost is the steady state plus the first-call warm-up.

### 4.3 How the data check grows with the data
The same recipes with every data table of the folder rewritten with its rows repeated (header once). `1_test_data_ST22_dummy` reads 11 tables; `3_test_no_joins` reads one (42 rows x factor).

| factor | rows (11 tables) / folder size | recipe | structure, 3 values | data check, 3 values | today first selection, 3 values |
|---|---|---|---|---|---|
| 1x | 807 / 312 KB | 1_test_data_ST22_dummy | 0.334, 0.295, 0.301 | 0.221, 0.204, 0.202 | 0.226, 0.230, 0.256 |
| 10x | 8,070 / 2.9 MB | same | 0.321, 0.301, 0.305 | 0.248, 0.238, 0.218 | 0.234, 0.218, 0.220 |
| 100x | 80,700 / 28 MB | same | 0.321, 0.287, 0.286 | 0.305, 0.290, 0.296 | 0.444, 0.435, 0.450 |
| 1x | 42 rows | 3_test_no_joins | 0.074, 0.040, 0.041 | 0.021, 0.020, 0.027 | 0.025, 0.024, 0.024 |
| 10x | 420 rows | same | 0.140, 0.082, 0.083 | 0.036, 0.015, 0.029 | 0.027, 0.026, 0.026 |
| 100x | 4,200 rows | same | 0.067, 0.040, 0.041 | 0.021, 0.015, 0.020 | 0.028, 0.026, 0.025 |

The structure check does not depend on the data. The data check grows slowly (0.20 s to 0.30 s for 100x more rows; the build grows from 0.23 s to 0.45 s). The data check is cheap partly because it plans the query and runs the steps on one row (4.1 above). A check that ran every tier-1 step on all rows would cost about as much as the build. I did not measure beyond 100x or on real production data (millions of rows): not run.

### 4.4 What a new session reads about all recipes (the half that stays)
`home_theater.py:85-112` loads every discovered recipe with `load_data_analysis_recipe` to collect all plot ids, once per new session (`:199`). The first session fills the in-memory cache; the next sessions only hash the files. Run, gate stubbed out, 3 runs each, seconds for: first session, second session, third session:

| recipes | run 1 | run 2 | run 3 |
|---|---|---|---|
| 7 | 0.247, 0.002, 0.002 | 0.243, 0.002, 0.002 | 0.261, 0.002, 0.002 |
| 107 | 1.320, 0.007, 0.007 | 1.292, 0.007, 0.007 | 1.288, 0.007, 0.007 |
| 507 | 5.203, 0.029, 0.030 | 5.544, 0.092, 0.093 | 5.482, 0.031, 0.032 |

So "time of start at first load" with no check at start is (about) start 2.0 to 3.7 s plus 0.25 / 1.3 / 5.3 s for the first session. Today it is the check (2.7 / 14 / 60 s) plus the same first session read. With 500 recipes the first page would still take about 7 to 9 s after the check is removed, from this read alone. Reasoned: the plot slots are registered by plot id for all recipes because ids are unique across recipes (`rules_data_analysis_recipe_structure.md` section 8). Whether to change that is question 7.

---

## 5. What exists as a production test

Read and run (57 + 104 tests, all passed on the scratch copy: `test_data_analysis_recipe_load_gate`, `test_gate_gap`, `test_shipped_deployments`, `test_recipe_gate_handlers`, `test_export_refusal`, `test_data_analysis_recipe_data_check`, `test_data_analysis_recipe_validator`, `test_shipped_recipes_pass_the_checker`, `test_bundle_importer`).

| What | Test file (read) | Covers | Would miss |
|---|---|---|---|
| structure of the 7 recipes of the active deployment | `test_data_analysis_recipe_validator.py:25-29,222-225` | `validate_data_analysis_recipe` on `pipelines/` (via the Bootloader's recipes folder) | only the deployment `local`; recipes of other deployments |
| strict checker on pipelines, retest, templates | `test_shipped_recipes_pass_the_checker.py:16-30` | `check_recipe_file` with registries, 14+ recipes | only the first half of the structure check; not the engine load, not the data check |
| id equals file name, templates valid | `test_data_analysis_recipe_validator.py:168-183` | `validate_data_analysis_recipe` over `config/data_analysis_recipes` and its sub folders; templates | a recipe in a folder outside it |
| data check on pipelines | `test_data_analysis_recipe_data_check.py:24-27` | `validate_data_analysis_recipe_data` on the 7 pipelines with `assets/test_data` | templates (they have no data: ran, they fail the data check by design: `audit`, `e_coli`, `simple_template` fail with missing files); retest recipes (two fail by design) |
| both checks inside the Bootloader, for every shipped deployment | `test_shipped_deployments.py:34-47` | starts `Bootloader()` for each file in `config/deployment/*/*.yaml` and asserts the default recipe is available | would break when "available" changes meaning |
| gate rules and contact | `test_data_analysis_recipe_load_gate.py` (about 12 tests) | structure fail, data fail, contact tiers, hidden selector fatal, all rejected, none | assert the start behaviour; all need rewriting |
| recheck within seconds | `test_gate_gap.py`, `test_recipe_gate_handlers.py`, browser `test_shiny_gate_gap.py`, `test_empty_data_analysis_recipe_startup.py` | recheck, selector follow, export refusal | assert the start-time dictionaries |

What is missing, for a production test as you asked (D-0184: "All the recipes should be tested when implemented for production"):
1. One test that runs BOTH checks, through the SAME single function the app will call, on every recipe of every shipped deployment with that deployment's data folder and data lookup. Today the two checks are run by different test files over different folders, and the combined path only by constructing the Bootloader.
2. A test with a bad value after row 1 in a tier-1 step (my probe above). None exists: `test_a_step_that_fails_on_the_values_is_reported_not_passed_in_silence` (`test_data_analysis_recipe_data_check.py:193-201`) makes every row bad (both rows `1/2` and `3/4`), so it cannot show a failure that sits only in a later row.
3. No test for a data change after the start (the data file is not watched).
4. The test suite is not run by CI today: `.github/workflows/` holds only `_disabled_workflows/` (deploy-connect, docs_build, lint_and_format, test_suite). "CI" in the sense of D-0184 does not run; the suite is run by the agents before a merge (`rules_toolchain.md`).
5. A mutation check ("test can fail"): I did not break the code to see these tests fail; for the 12 tests of the load gate I read them only.

---

## 6. Questions for Eve (D-0165: no record answers them)

Each has an example. Where a record supports a default it is named; a default is not a decision.

**Q1. Is a recipe that failed still shown in the selector?**
Example: the folder has `AMR_2025` (fine) and `AMR_2024` (its data file moved). The user opens the selector.
- Reading A: all recipes are listed; `AMR_2024` looks like the others; the user picks it and then reads the error message. (This is your sentence in M171: "We should SEE the recipe in the selector ... an ERROR MESSAGE should show after the load attempt".)
- Reading B: as A, and after a failed attempt in this run the name gets a mark "failed" until it is repaired.
- Default with record: A. D-0184 replaces in part D-0009, naming "a failing one is not selectable". With no check at start the app cannot know which recipes fail before they are tried. B is not in any record: it needs question 2 first.

**Q2. Is the result of a check kept, so an unchanged recipe is not checked twice? For how long?**
Example: a user opens `AMR_2025`, goes to Blueprint, comes back. Or two users in two browser tabs open it.
- Reading A: kept in memory while the app runs, keyed by the recipe file set hash (structure) and by the recipe hash plus the data hash (data). A changed recipe or new data gives a new check. (The review session's proposal, M173/M174.)
- Reading B: never kept; every selection checks again (0.1 to 0.5 s here, more with big data).
- Reading C: kept on disk, also after a restart.
- No record supports a default (the review session's proposal is not hers). My recommendation, labelled as mine: A. It gives a message the first time and no repeat cost; the key is the thing D-0186 distinguishes.

**Q3. Hidden selector (pipeline-static) and the operator-named default fails: what should happen?**
Example: a deployment names `AMR_2025` as its only recipe, the data folder of this week lacks one column.
- Reading A: at start, check only the named default (one recipe, 0.1 to 0.5 s here); if it fails, the app stops with the message the operator reads today (see 3a). Not "all recipes at start".
- Reading B: no check at start; the app starts; the user opens HOME and reads the failure plainly in the page with what failed and the contact.
- Reading C: both.
- No record from you. ADR-094 point 5 (2026-11-08) is the old rule: stop. The review session's request in M173 is "must still stop, or show the failure plainly, never an empty HOME" (not your words). No default.

**Q4. Does the list of rejected recipes beneath the selector go away?**
Example: today a user sees "2 recipe(s) unavailable — failed data or structure check" in red under the selector, listed with the contact, from the start.
- Reading A: it goes away (nothing is rejected at start).
- Reading B: it stays, but only for recipes that failed since the app started (needs Q2 reading A or C).
- Default with record: A at start (D-0184). B is open.

**Q5. A dataset that does not fit the recipe's contract: who is named, and is the recipe called "failed"?**
Example: the pipeline delivers this week's table without the column `mlst`. The recipe is unchanged.
- D-0186: changing data is not necessarily a failure. A new dataset that fits is no failure. This one does not fit.
- Reading A: it is a failure of the pair (recipe, data). The message says: the table `ST22_MLST.tsv` has no column `mlst`; the recipe is not at fault; contact = the recipe's contact (`info.contact`, then the deployment's `branding.contact`), because D-0184 says "the information of the recipe is given in a message".
- Reading B: as A, but the contact is a "data provider" contact that does not exist yet (a new field in the deployment or the recipe).
- Default with record: A (D-0184 and the two-tier contact in `rules_data_analysis_recipe_structure.md` 11a).

**Q6. Should the check run the tier-1 steps on all rows or on one row?**
Example (ran): 2000 rows, one value "abc" in row 2000, a step that turns the column into numbers. The check says "passed". The build fails: "conversion from `str` to `i64` failed in column 'n' for 1 out of 2000 values". HOME shows "Data Assembly Failed: ..." with no contact.
- Reading A: keep one row (fast); make the build failure carry what failed and the contact, so a late failure reads the same as an early one.
- Reading B: the check is the build: all rows, cost about the first selection (0.2 to 0.45 s on the shipped data at 28 MB; grows with the data). "Passed" then means "built".
- Reading C: both: one row first, the build error with the contact.
- D-0050 ("No silent error: that is the rule") is not broken by A or C because the build error is shown; but a user who read "passed" is misled. No default.

**Q7. The all-recipes read in every new session (plot slots): keep or change?**
Example: 500 recipes: the first session waits 5.2 to 5.5 s to read all 500 recipes even when the check at start is gone (4.4).
- Reading A: keep (simple; the cost is a one-time cost of the first session after a start).
- Reading B: register the plot slots only for the recipe that is selected. Needs a design (plot ids are unique across recipes and registered by id at session start; a recipe selected later needs its slots then).
- Reading C: read the recipe files only for plot ids, without `ConfigManager` (cheaper). Needs a check of how much it saves.
- No record. Without a choice D-0184 fixes the start and leaves the first-session cost: a half fix for the "hundreds of recipes" reason in the ledger line.

**Q8. Does the selector learn about a recipe file added while the app runs?**
Example: you import a reproducibility bundle. The page says "reload (F5) to see it in the selector" (`export_handlers.py:791`). I verified: F5 does not show it; only a restart does.
- Reading A: list the recipe files again each time the selector is drawn (a file listing, no check; cheap). The imported recipe appears at once, and is checked when selected.
- Reading B: keep the restart, correct the message ("restart the app").
- Default with record: none; ADR-094 text (issue #38) says a new recipe needs a restart; it is not your decision (not in the ledger).

---

## 7. What would change, by size, and an order of work

### 7.1 List
Sizes: S = under half a day, M = one day, L = more.

**Code**
- (M) One function `check_recipe(recipe, data)` returning the result: ok, or what failed, in the recipe or in the data, which file and column, the problems, the contact. Built from `_gate_one` (`bootloader.py:387-410`); runs structure then data once; `checker_advices` merged into the first checker call (removes a duplicate run). Used by HOME on selection, by Blueprint's Validate (`blueprint_handlers.py:2938-3020`), by the poll. Takes `imports_dir` and `data_lookup` as `_gate_one` does today.
- (M) Keep results (Q2): in memory keyed by the file set hash of the recipe and by recipe + data hash (`compute_data_analysis_recipe_keys`, `orchestrator.py:91-`). Files hashed already: `cache_keys.py:115-129`.
- (M) HOME: on selection show the result; failure message with what failed, recipe or data, the file and column, and the contact; replace the empty stand-in with an explicit failure state in `usable_config` (`recipe_gate_handlers.py:120-130`) and the reader at `home_theater.py:841-895`; a new text for `rejected_recipe_text` (`validator.py:438-448`).
- (S) The selector lists all discovered recipes (`home_theater.py:1604-1611`, `recipe_gate_handlers.py:146-173`), the notes under it (`:86-117,188-194`) change (Q4).
- (M) Default resolution (`bootloader.py:502-554`, `:556-592`) for the hidden selector and the env variable (Q3, 3a, 3b, 3h); the notice "your named default failed, I opened Y" is not needed if the named default stays selected.
- (S) The poll (`recipe_gate_handlers.py:138-141`) rechecks the open recipe with the new function; data change watched or not (D-0186: not a failure by itself; Q5).
- (S) Export refusal (`export_refusal.py`, `export_handlers.py:848`) reads the new result for the open recipe.
- (S) `ingestion_handlers.py:51`: no `bootloader.__init__` rerun; refresh the list of files.
- (S to L, Q7) `home_theater.py:85-112,199`.
- (S, Q8) the F5 message at `export_handlers.py:791`.
- (S) `bundle_importer.py:309`: nothing changes if "available" = listed; check on selection with `imports_dir`.

**Tests** (they assert start behaviour or the old dictionaries; counts from `grep -c` of the names): `test_data_analysis_recipe_load_gate.py` (28 hits, rewrite), `test_gate_gap.py` (27, rewrite), `test_blueprint_failed_load.py` (13), `test_recipe_gate_handlers.py` (3), `test_shipped_deployments.py` (1, the assertion `get_default in available`), `test_bootloader_launch.py` (4), `test_export_download_path.py` (3), `test_export_provenance.py` (2), `test_export_refusal.py` (1), `test_bundle_importer.py` (1), `test_retest_data_analysis_recipes.py` (4), `test_checker_advice_visible.py` (2), and the browser tests `test_shiny_gate_gap.py`, `test_empty_data_analysis_recipe_startup.py`, `gate_stage.py`. New tests that can fail: the single function on every shipped recipe and deployment (section 5 item 1); bad value after row 1 (item 2); the start time with 100 copies stays below a stated bound (a guard against a return of the check at start); each case of section 3 as a test (a) to (h); a failing recipe selected shows the message and the contact and HOME does not draw the empty stand-in; the export is refused for a failing selected recipe.

**Docs and records**
- Needs your yes (a rule file or an ADR; nothing edited): `.claude/rules/rules_data_analysis_recipe_structure.md` section 11 (the status banner) and 11a (all of it: "checks every recipe once at startup", the rejected list, the default rules, the "Scope boundary"); `.claude/knowledge/architecture_decisions.md` ADR-094 points 1, 2, 5, 6 and "Consequences" (a new ADR that amends it, or an amendment note); `.claude/knowledge/decision_ledger.md` (a scribe: D-0009 is replaced in part by D-0184; the new lines of your answers to section 6).
- Without a rule-file yes (user and developer texts; a scribe after the merge): `docs/user_guide/system_transparency.qmd:44` ("checks every data analysis recipe once at startup"), `docs/UML/data_contract_and_failures.md`, `docs/UML/quality_goals.md`, the UML model `docs/UML/app.mdj` (and `audit_uml_model.py`), comments in `config/deployment/templates/deployment_template.yaml:41-45`, `config/deployment/demo/demo-vetinst.yaml:25`, `config/deployment/local/local.yaml`, `docs/reference/environment_variables.qmd:24`, the `@deps` and `doc:` lines of `bootloader.py`, `recipe_gate_handlers.py`, `data_analysis_recipe_validator.py`, `export_refusal.py`.
- A record gap found: `test_gate_gap.py:1-8` says "Decided (Eve, 2026-11-15): a recipe must pass all checks at validation before HOME can use it", and the task says "defect, no decision". No ledger line carries that sentence. D-0186 now supports the part that stays (a changed recipe is a failure).

### 7.2 Order of work (no case of section 3 is silent at any step)
1. **The function and its tests; no behaviour change.** Build the single check function with its result (ok, recipe-or-data, file, column, problems, contact) and the production test of section 5 item 1 and 2. The start check stays. At the end of this step nothing changed for a user.
2. **Use the function on selection, with the start check still in place.** HOME shows the failure state with the contact for the open recipe; `usable_config` no longer returns a silent empty stand-in; export refusal reads the result; the poll uses the function. Cases (e), (f) become better; none is silent; the start check still covers (a), (b), (c), (h).
3. **Decide Q3, Q4, Q6, Q8 with you, then change the default and the selector.** The selector lists all files; the hidden-selector case is solved as you decide (Q3); the tests of (a), (b), (c), (h) are rewritten BEFORE the start check goes, and they must fail with the old behaviour (a test that cannot fail does not count).
4. **Remove the check of all recipes at start.** Only now. Remove `_validate_data_analysis_recipes` at `__init__` for all recipes, the rejected list at start and the re-run of `__init__` after an upload; keep the poll for the open recipe. Measure the start with 100 and 500 copies again (the guard test) and the first-selection time.
5. **The per-session all-recipes read (Q7), if you want it.** Without it, the start stays about 3 s but the first session still waits 1.3 s (107) or 5.3 s (507).
6. **Records and docs** (a scribe, with your yes for the rule file and the ADR); the UML and ADR sync law in `workspace_standard.md`.

---

## What I did not check or could not run
- No browser test (Playwright) was run; no real `shiny run` session. "What the user sees" is from the Python functions that build the text (`gate_notes`, `rejected_recipe_text`, the [FATAL] block) and from the code of the HOME draw functions; the HOME texts at `home_theater.py:841-895` were read, not rendered.
- Start times were measured for `qa` (agent off). `developer` adds the `claude` probe of several seconds (comment at `app/src/main.py` about the auth probe); not measured.
- Not measured: data above 100x or real production data, 1000 recipes, an idle machine, many sessions in parallel (the poll cost per session is only the single-process value).
- The 100 and 500 copies share include files with the original, so their `ConfigManager` loads are cheaper than 500 different big recipes; the real per-recipe cost is higher (the 11-table recipe costs 0.3 s structure + 0.2 s data).
- Session restore and bundle import were read, not run end to end with a failing recipe (3g).
- I did not break the code to make the existing tests fail (mutation check).
- I did not read `tmp.md`, and I changed no tracked file.
