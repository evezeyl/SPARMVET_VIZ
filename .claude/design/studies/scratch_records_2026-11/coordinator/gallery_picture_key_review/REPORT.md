# Review of task/gallery-picture-key (D-0400), Gallery user space

Verdict: FIT TO MERGE (no blocking finding; four low points listed for the owner and the builder).

Environment (RUN): load 5-10 during runs; `viz_gallery`, `utils`, `app` and `viz_gallery.picture_key` were imported from the worktree
(`.claude/worktrees/gallery-picture-key/...`), checked with a python one-liner using the PYTHONPATH of `tmpAI/env.txt`.
`git status` of the worktree: clean at start and end (0 lines). My app run (port 8733) is stopped; the other apps on the machine are not mine.

## 1. Diff (RUN: `git diff dev...task/gallery-picture-key --stat`)
43 files: 36 added (new `libs/viz_gallery/src/viz_gallery/picture_key.py`, `app/tests/test_gallery_picture_key.py`, 34 x `preview_plot.picture_key.json`), 7 modified:
`rules_gallery_standards.md` (+1 line), `app/handlers/gallery_handlers.py`, `app/modules/gallery_listing.py`, `app/src/bootloader.py`,
`app/tests/test_gallery_app_path.py`, `assets/scripts/gallery_previews.py`, `libs/viz_gallery/README.md`.
Forbidden files: RUN `git diff --name-only | grep -E "recipe.yaml|.tsv|meta.md|.png|spec|gallery_index|pyproject"` gives 0. No recipe, data, meta, picture, spec, taxonomy, index, pyproject changed. No name or label key touched.
Not decided and in the branch: all marked PROVISIONAL in code or described (table below). The key is kept per picture, written only by `assets/scripts/gallery_previews.py` (READ `gallery_previews.py` diff: `write_picture_key` called only after kept/written picture); compared at start (`bootloader.py` `_check_gallery_examples`); no drawing and no pixel compare at start; no redraw automation. It does what is decided and nothing more.

## 2. Correctness and edge cases
- Start-up cost (RUN): hashing 34 examples (68 files) and comparing = 0.045 s.
- Key hash is over file bytes (READ picture_key.py:`_digest`). A trailing newline or CRLF changes it (RUN-by-test: appending "\n" to the data makes it stale). `.gitattributes` has `*.tsv -text`, `*.yaml -text`, `*.json -text` (READ), so git never converts line endings: same bytes on every checkout. Good.
- No absolute path in any key (RUN: grep "/home" in the 34 files: none). Same on another checkout path. Key holds only 2 sha256 and the plotnine version (all 34: 0.15.4).
- plotnine not installed: `"unknown"` (READ). It is then written into a key and compared as a string: a machine without plotnine would show every example stale (correct and visible). The drawing script needs plotnine anyway.
- Key written for a picture not identical? Not possible (READ gallery_previews.py: key only in the `apply and row.new_picture is not None and (content_unchanged or changed)` branch; error rows get no key). Test `test_the_picture_key_is_written_only_when_a_picture_is_kept_or_written` covers dry run, differing picture not applied, and `--changed`.
- `--apply` with a differing picture and no `--changed`: nothing written, old key kept, so it stays "not current" when the inputs changed. With unchanged inputs (e.g. a matplotlib change) a differing picture keeps a matching key and shows no notice: this is the known limit of the PROVISIONAL key, see table.
- Race: parts taken before drawing and again after; a difference raises and no key is written (READ gallery_previews.py). Good.
- A stale key never hides or rejects an example (RUN, screenshot: 34 options still in the select, `bar_simple` and `dumbbell` stale and still listed; test `test_the_notice_names_a_stale_example_and_keeps_it_listed`). A hand-edited key is not trusted (self-check `key_of(parts) == key`).
- Whole-file key does not cover `!include`; a test fails if a shipped recipe uses one (READ test). Fine today.

## 3. Gallery start check and rules
- `libs/utils/src/utils/recipe_check.py`, `app/modules/gallery_examples.py` and `gallery_manager.py` do not list or count the files in an example folder (grep: only `iterdir` of example folders). The extra file is not reported (RUN: `test_gallery_check_at_start.py` passes, the whole Gallery group 84 passed; the app started with the 34 examples and rejected none).
- `gallery_index.json` unchanged (RUN: diff stat empty).
- `rules_gallery_standards.md` section 1 still says "exactly" four files (the branch only adds a line in section 6): the text is now not true on disk (5 files per example). Low, see finding L2.

## 4. Library boundaries
- `picture_key.py` imports: hashlib, json, importlib.metadata, pathlib, typing, and `viz_gallery.example_recipe` (own lib). No other lib, no Shiny (READ). `app/src/bootloader.py` (tier 3) imports `viz_gallery`: allowed.
- Fact for the owner: plotnine is read by name through `importlib.metadata.version("plotnine")`; it is not imported and not declared in `libs/viz_gallery/pyproject.toml` (grep: no `plotnine` line). I did not change it. `audit_cross_lib.py`: "No cross-lib violations found."

## 5. Tests can fail (RUN)
In-memory patch: `picture_key_parts` forced to return `data="x"` then `pytest app/tests/test_gallery_picture_key.py -x`: `test_changed_data_makes_it_not_current` FAILED (`assert (not True)`). Nothing left modified (`git status` clean).

## 6. Controls (worktree code, Python = main .venv, PYTHONPATH of the worktree)
a) `pytest app/tests/test_gallery_picture_key.py test_gallery_app_path.py test_gallery_listing.py test_gallery_check_at_start.py -q`: 84 passed in 37 s.
b) Full headless baseline, `-n 4`, exact command of section 8: `5 failed, 13809 passed, 14 skipped, 33 xfailed in 2644.98s (0:44:04)` (machine busy; a first attempt with `timeout 580` was killed by me, not a result). The 5:
   - `test_decision_ledger.py::test_real_ledger_header_counts_equal_the_computed_counts` and `::test_mutations_of_a_copy_of_the_ledger_are_caught`: `(400, 393, 1, 2, 4) != (408, 401, 1, 2, 4)`. Also fail on dev (main tree, RUN): the ledger header counts are out of date (lines D-0401 onward added, header not updated). Not this branch.
   - `test_filter_form_survives_rerender.py::...test_a_list_of_values_loses_the_removed_values...`, `test_shiny_plot_errors.py::test_the_alerts_panel_holds_one_entry...` and `::test_the_original_pane_of_compare_still_draws...`: pass when run alone, both on the main tree (74 passed with the ledger file) and in the worktree (RUN: these two files plus `test_shiny_gallery_left_out.py`: 44 passed, 1 xfailed, 300 s). So they failed only under load (timing), not a result of this branch. They are not Gallery tests.
c) Browser, qa features: `test_shiny_gallery_left_out.py` passed (in the 44 above). I did not run the Gallery tests of `test_shiny_smoke.py` (see Not verified). The known failing `TestPreviewFiltersOnReferenceViews` was not run.
d) Audits (on the worktree; `scripts/run_audits.sh all` NOT run: it does `git checkout dev`, which cannot be done in a worktree where dev is checked out in the main tree). Instead: `audit_cross_lib.py` no violations; `audit_old_words.py --check` exit 1 "retired words remain" (same head output on the main tree, exit 1 too: pre-existing, not this branch); `audit_docs_sync.py` FAIL with 3 items (`tmpAI/agent_channel.md`, `.venv/`, `libs/viz_factory/README.md tests/test_theme_slots.py`): none touches this branch. `audit_deps_verify.py` report written, no picture_key line flagged (I grepped; I read no full report). `audit_package_deps.py` could not run (looks for `.venv` inside the worktree).
e) `assets/scripts/decision_ledger.py` has no format check, only `list` and `check <numbers>`. RUN: `check --decided D-0400 D-0406 D-0407 D-0408 D-0409` -> OK. RUN own format check (10 fields separated by " | " per line, main tree ledger): 410 lines, 0 lines with another field count. The header counts of the ledger are out of date (see the 2 failing ledger tests, dev).

## 7. Notice on screen (RUN)
Scratch gallery copy under `tmpAI/coordinator/gallery_picture_key_review/scratch/` with one comment appended to the recipe of `dumbbell` and `bar_simple` (repository untouched), own deployment file; app on 8733, qa features; screenshot saved:
`/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/coordinator/gallery_picture_key_review/notice_screenshot.png` (and `notice_block.png`). Text on screen: "2 example(s) shown with a picture that is not current:" then "bar_simple, the picture is not current: the recipe, the data or the plot library changed since it was drawn (recipe)." and the same for dumbbell. Block is red-tinted like the "not shown" notice. The app printed the same two lines as `[Bootloader] WARNING`.

## Findings
- Blocking: none.
- L1 (low, Gallery notice wording, PROVISIONAL): the sentence says "the recipe, the data or the plot library changed since it was drawn (recipe)": the list and the specific part say the same twice; the "not current" is said twice per line. Also the block is red, like the "failed the check" block, although these examples are shown and usable. Plain wording is for the owner.
- L2 (low, records): `rules_gallery_standards.md` section 1 says each bundle contains "exactly" four files; there are now five on disk. Either the rule line or the note should say so (the owner decides; I did not edit).
- L3 (low): `app/handlers/gallery_handlers.py` still has the comment "The title line exists only when examples were rejected; a lone note has none" above the new rule; it no longer describes the code (any line ending in ":" is a title). Also unused import `List` in `picture_key.py`.
- L4 (low, behaviour): any future notice line that ends with ":" becomes a title; a recipe-reason ending in ":" would be shown as title. Today reasons end with "." (builder adds it). Not a defect now.
- Pre-existing, not this branch: the rules section 6 and README name `libs/viz_gallery/assets/generate_previews.py`, which does not exist (only `__pycache__`); so `gallery_previews.py` is truly the only writer of the pictures.

## PROVISIONAL choices for the owner
| Choice | Where | Note |
|---|---|---|
| Key inputs: recipe file bytes, data file bytes, plotnine version | picture_key.py docstring | D-0400 fixes plotnine; recipe and data are the obvious rest |
| Not in the key: matplotlib, fonts, polars, transformer, picture size/dpi, VizFactory code and default theme, seed | picture_key.py docstring | a change there redraws differently but shows no notice |
| Notice wording ("... shown with a picture that is not current:" and the reason sentences) | gallery_listing.py, picture_key.py | see L1 |
| File name `preview_plot.picture_key.json` (not `.key`: ignored by the repo) | picture_key.py KEY_FILE | five files per example now (L2) |
| Handler styles any notice line ending with ":" as a title | gallery_handlers.py | see L3, L4 |
| Whole-file hash (no `!include` support) | picture_key.py | a test fails if an example uses an include |
| Stale example stays listed and shown, only named in the notice | gallery_listing.py | consistent with D-0400 "existing notice" |

## Not verified
- The Gallery tests inside `app/tests/test_shiny_smoke.py` (not run; load and time).
- Full browser suite, `test_every_app_features_starts.py`, `test_export_download.py` (not asked).
- Full `scripts/run_audits.sh all` (it checks out dev; cannot run in the worktree); `audit_package_deps.py` did not run.
- Redrawing with another plotnine version, another machine, or a Windows checkout.
- That the 3 load-flaky tests always pass: they passed twice alone, failed once under load.
- Pixel-identity claims of the builder ("all 34 redraw identical"): not rerun (the drawing script was not run, to keep the picture files untouched).
