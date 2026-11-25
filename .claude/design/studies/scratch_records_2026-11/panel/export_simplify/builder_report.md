# Builder report: export simplify + Export fields per session (D-0288 to D-0296)

Worktree `.claude/worktrees/export-ready`, branch `task/export-ready`. `git status --short` at the end: empty (nothing uncommitted, no app or test process of mine running).
Interpreter: main `.venv`, `PYTHONPATH=".:libs/*/src"`; the worktree's modules were printed once (`app/handlers/export_handlers.py` under the worktree path).

## Commits (newest first)
- `73ba5390` test(export): the Export fields per session in the browser
- `c743cce3` feat(export): the Export fields belong to the loaded recipe and session, in memory only (store wiring, panel from the store, `export_ready.js`)
- `c1c1c8ee` feat(export): plot format SVG by default, the defaults in one place (`app/modules/export_fields_store.py`)
- `371ab4cb` refactor(export): remove the scope choice
- `7d586528` merge of `dev` (743156f0) into the branch: no conflict.

## What the user sees now, point by point
1. **No scope choice; every export holds all plots, both modes.** Scope radio, its choices, the effect that followed the tab, the two notices, the filter in the download and the rule "the tick forces all plots" are deleted (no dead function). `active_home_subtab` was only used for the scope, so the kwarg of `define_export_server` is deleted too (and the caller in `home_theater.py`). README says "Plots : N (all plots of the recipe are exported)" (`export_handlers.py:2073`). Tests: `test_export_all_plots_and_defaults.py::test_the_bundle_holds_every_plot_of_the_recipe_with_and_without_the_mode_tick[False/True]` (3 plots in 2 groups), browser `test_shiny_export_fields_per_session.py::test_the_fields_follow_the_session...` (set of pictures == all plots of recipe A) and `::test_the_mode_tick_does_not_change_which_plots_are_exported` (recipe B, with and without tick).
2. **Mode tick unchanged** (label text, default off, same contents). I only removed the sentence "Forces Scope to Global ..." from its small note (it described the deleted rule). Test: `test_export_download.py::test_mode2_checkbox_adds_the_reproducibility_bundle` (passes, unchanged).
3. **Fields that stay**: label, tick, quality, plot format, report format, W, H. Defaults SVG and HTML (`export_fields_store.py`). Tests: `test_export_all_plots_and_defaults.py::test_the_panel_shows_svg_and_html_selected_and_no_scope_choice`, `::test_a_bundle_made_without_touching_the_plot_format_holds_svg_pictures`, store `test_a_first_visit_shows_the_defaults...`.
4. **Fields belong to the loaded session, in memory only.** Browser test `test_the_fields_follow_the_session_and_the_label_is_never_remembered` (real app, qa): A first visit = defaults; set A; switch to B = defaults (no leak); set B; back to A = A's values; back to B = B's values; Home to Blueprint and back = B's values; Export on A holds A's values (png, publication 600 DPI, 9x6, tick folders, docx report) and all plots of A. Nothing on disk, nothing in the session save, no Restore/import reads them (grep: no export field in `session_handlers.py` or `session_manager.py`). Same recipe + new data batch = another `session_key` = defaults: proved on the pure store only (two keys do not leak, `test_two_sessions_do_not_leak_into_each_other`), not in the browser (I did not change a data file under a running app).
5. **Label is not remembered**: empty on every load, recipe switch and return to Home (same browser test, label asserted `""` after each step; empty label still gives the word "user" in the file name, unchanged). The store refuses the label field (`test_the_label_is_never_remembered`). The recipe name is NOT used as the default (`EXPORT_LABEL_DEFAULT = ""`, marked PROVISIONAL in the code).
6. **Export button when the server sets the fields**: see "Button" below. Test `test_a_value_set_by_the_server_greys_the_button_until_the_server_holds_it`.

## Design of the store (five lines)
- `app/modules/export_fields_store.py` (pure, no Shiny): `EXPORT_FIELD_DEFAULTS` (6 fields), `ExportFieldsStore.fields_for(key)` (copy; defaults on a first visit) and `.set_field(key, field, value)` (refuses the label, an unknown field and an empty key: no silent write).
- One store per page session, created in `define_export_server` (same lifetime as `home_state`; a reload with F5 forgets it: PROVISIONAL reading of "while the app runs").
- Key = `SessionManager.compute_session_key(recipe sha, data batch hash)` read from `home_state` (the same rule as the session files).
- Writes: one `@reactive.Effect` per field (`_remember_one`), each isolated on the key and guarded by equality; an empty number box is not a choice and is skipped. Pushes: `_show_the_fields_of_the_session` runs when the session key changes and sets the fields that differ in place (`ui.update_*`), with an empty label. The panel render reads the store inside `reactive.isolate()` (`export_handlers.py:569-593`).
- Why the panel is drawn again after a user-space switch: Shiny sends an output that is not drawn again as it was last drawn; the first run showed the old defaults come back and then be written into the store (a leak). The render now reads `input.sidebar_nav` so it is drawn again on a user-space switch only (measured: 4 draws in the test = start and the Blueprint trips; none on recipe switches or plot tab changes; `test_export_inputs_survive_plot_tab.py` and `test_export_box_survives_plot_tab.py` pass).

## Button (point 6): how a server-side set is confirmed
- Finding (read in py-shiny `_session.py`): a custom message is sent at once, input messages wait for the flush, so a "pending" custom message arrives BEFORE the new values. A native `input`/`change` listener does not see a value that Shiny sets (jQuery trigger).
- Chosen: `export_ready.js` also listens to Shiny's own `shiny:inputchanged` for the panel fields. A value set by the server then does what a typed value does: grey, ping, echo, ready when the server holds the shown values. The same listener makes the button grey for a moment at page load and after a panel redraw (the new inputs announce themselves); the echo opens it.
- Found while testing and fixed: Shiny removes `aria-disabled` from the download link when the output value arrives; with a grey state that begins at load the class stayed but the mark was gone (5 tests of `test_export_ready_button.py` failed). `render()` now sets `aria-disabled` every time while grey.
- Test: the page presses Export in the very instant it applies the plot format the server set (hook on `shiny:inputchanged`): the press is refused (`prevented`, `grey`), no download starts, the button opens, and the bundle then holds the SHOWN value (svg), not the one of the recipe left (png).

## PROVISIONAL choices (options)
1. Keys `export_scope` in `t3_steps.yaml`, `lineage_graph.json` and the provenance dict: built "drop the key". Options: keep it with the value "global". Reader check: grep over `app`, `libs`, `assets`, `config` finds no reader; `bundle_importer.py` and its tests do not read it. (Old bundles that carry it import as before.)
2. README line: "Plots : N (all plots of the recipe are exported)" replaces the line "Export scope". Options: a separate line.
3. Label default: empty (recipe name is a proposal, not built).
4. Store lifetime: per page session (F5 forgets). Option: a store shared by all pages of the app process (not decided, not built).
5. Panel drawn again on a user-space switch (needed, see design). Option: a JS or server signal on re-appearance instead (more moving parts).
6. Grey at page load and after a redraw (consequence of listening to Shiny's event). Option: ignore events before the first echo (more code, a gap in the confirmation).
7. The three texts of `EXPORT_READY_TEXTS` and 5000 ms: untouched. Note: the "lost" text names "box and label" (existing).

## SVG with a PDF report (real run, not changed)
- `rsvg-convert` is NOT on this machine. Real runs of the download generator with real Quarto (scratch `tmpAI/svgpdf/test_scratch_svg_pdf.py`): SVG + HTML: `plots/p.svg`, `report.html` rendered, `report.qmd` links `_render/p.svg`. SVG + PDF: `plots/p.svg`, `report.pdf` rendered, but `report.qmd` links `_render/p.png`: the report holds PNG copies (code `export_handlers.py` ~1200-1220: PDF native formats lose svg without rsvg). **No notice, no README line, no `report_RENDER_FAILED`: the user is not told** that the PDF figures are PNG and the plots folder SVG. SVG + DOCX: svg figures. PNG + PDF: png. This is a silent difference between the `plots/` pictures and the report figures: it needs a decision (tell the user; or refuse; or install the tool). Not changed.

## Tests
Removed: `test_export_scope_choices.py` (5 tests), `test_export_scope_notices.py` (3 tests; all three tested the deleted effect).
Adapted: `test_export_inputs_survive_plot_tab.py` (4 -> 3 tests, scope parts and one scope-only test out, svg default, chosen format pdf), `test_export_box_survives_plot_tab.py` (trigger set now also `home_state`, `_session_key`; check-itself cases added), `test_export_download_path.py` (harness: no scope value; `None` = not touched like the real `safe_input`), `test_export_provenance.py`, `test_export_errors_visible.py` (no `scope_label`), `test_export_download.py` (the exploration-filter test chooses PNG, it compares images), `test_shiny_step_order.py` and `test_shiny_seed_places.py` (choose PNG before the download; adapted, NOT run: not on my list).
New: `test_export_fields_store.py` (7), `test_export_all_plots_and_defaults.py` (5), `test_shiny_export_fields_per_session.py` (3, browser).
Fail-once (reversible edits, files restored and compared; no git checkout/stash):
- only the first plot exported: `test_the_bundle_holds_every_plot...` fails; also browser `...follow...` fails ("the bundle holds ALL plots").
- default plot format png: `test_a_bundle_made_without_touching...` fails.
- provenance keeps `export_scope`: `test_the_provenance_has_no_scope_key` fails.
- panel default png: `test_the_panel_shows_svg_and_html...` fails.
- store accepts the label: `test_the_label_is_never_remembered` fails.
- one shared key for all sessions (store): `test_two_sessions_do_not_leak...` fails; the same in the app (`_session_key` returns "shared"): browser test fails ("nothing of A leaks into B").
- JS without `shiny:inputchanged`: `test_a_value_set_by_the_server_greys...` fails (`prevented False, grey False`).
- push removed: browser `...follow...` fails (A's values shown on B).
- label not reset by the push: browser `...follow...` fails.
- panel not drawn from the store: browser fails at "Home -> Blueprint -> Home".
Final runs (qa, one file at a time, load below 10): `test_export_ready_button.py` 18 passed (6 min 30 s); `test_export_inputs_survive_plot_tab.py` 3 passed; `test_export_download.py` 9 passed (5 min 28 s); `test_shiny_export_fields_per_session.py` 3 passed; `test_filters_cleared_on_recipe_change.py` 13 passed; headless `test_export_*.py` (without the three browser files above) 217 passed, 4 skipped (6 min); `python -c "from app.src.main import app"` OK. A first run of `test_export_ready_button.py` had 5 failures (the aria problem above), fixed, then 18 passed. The earlier mid-work run of the old pattern (explicit files ignore `--ignore`) also passed 242 on the scope-removed commit.
Seed test of `test_export_download.py`: 3 runs alone, 3 passed (50 s, 44 s, 38 s); it also passes inside the full file. Stable now.

## Decisions table
| Decision | How the code complies | Where | Test |
|---|---|---|---|
| D-0292 "all plots included in the export" | no scope, all plots | `export_handlers.py` (download, no filter) | `test_the_bundle_holds_every_plot...` |
| D-0295 "Within those 2 modes we have the plots exported - all exported" | tick kept, same plots both modes | `export_handlers.py` panel + download | `...[True]`, `test_the_mode_tick_does_not_change_which_plots_are_exported` |
| D-0294 svg and html defaults | defaults in one place | `export_fields_store.py` | defaults tests |
| D-0288 / D-0289 per recipe and session | store per `session_key` | `export_handlers.py:569-593, 754-800` | browser follow test |
| D-0291 / D-0296 memory only, label not remembered | no disk, label refused | store, `_show_the_fields...` | store test, browser |
| D-0270 button grey until the server holds the values | `shiny:inputchanged` | `export_ready.js:127-137,175` | server-set test, `test_export_ready_button.py` |
| D-0050 no silent error | the store raises on a bad write; SVG+PDF finding reported | store; this report | store tests |
| D-0285 do not run the same tests twice | targeted runs, one process at a time | n/a | n/a |
Consequence asked (what happens after this change): a recipe switch no longer keeps the label or the other session's choices; a user who typed a label and goes to Blueprint and back finds the label empty (decided, D-0296).

## Passages now untrue (not edited; a records task follows)
- Rules: `.claude/rules/ui_implementation_contract.md:24, 195, 208, 231, 242, 249, 258, 411` (3-way scope toggle, `export_scope`, scope detection, t3_steps key, "Active plot" panel; plot format selector default; label field named `export_bundle_label` vs code `export_user_name` was already off); `.claude/rules/rules_app_features_flags.md:25`.
- ADR text: `.claude/knowledge/architecture_decisions.md:1000-1005, 1014-1017` (ADR-047), `2652-2656, 2684` (ADR-074, `export_scope` key), `4901-4902` (ADR-097 "unchanged 3-way scope", "`export_scope` forced to `global`").
- Design: `.claude/design/export_specification.md:13-42, 54 (default PNG), 114, 125, 136-137, 141-153, 167, 188-191`; `.claude/design/reproducible_export_design.md:77-79, 149`; `.claude/design/app_features_scoping_guide.md:37, 99, 101`; `.claude/design/functionality_dependency_map.md:79`; `.claude/design/app_features_capability_matrix.md:69`.
- User docs: `docs/workflows/ui_app_features.qmd:86-91, 272, 479`; `docs/user_guide/system_transparency.qmd:117, 127` and `docs/appendix/FAQ.qmd:83` (quality picks SVG or PNG: it never did, quality only sets the resolution; and the default format is SVG now); `.claude/workflows/retest_procedure.md:101` (scope "Global", PNG).
- App features comments: `config/app_features/developer.yaml:26`, `pipeline-exploration-advanced.yaml:26`, `pipeline-exploration-simple.yaml:26`, `pipeline-static.yaml:27`, `standalone.yaml:28` ("bundle zip + scope toggle") (not in my file list, not edited).
- UML `docs/UML/app.mdj` lines 11136, 11958, 12428, 23717, 24609, 24617, 25268, 26482, 26490 ("Export label, scope, ...") and 79822, 81079 ("export_bundle_download with export_scope"); the UML also lacks the new store.
- Fixed by me: `app/src/help/home.md:41` (the app shows it).
- Also in the code: the docstring line about the pictures at the head of the download ("SVG (web preset) or high-DPI PNG (publication)") was untrue already; corrected.

## What I did not check
- Same recipe with a new data batch in the browser (only the store with two keys; the key rule is the session files' own).
- Session Restore and session import in the browser (by construction no code reads or writes the fields; grep only).
- Two browser tabs, F5, other browsers (Firefox, Safari).
- `test_shiny_step_order.py` and `test_shiny_seed_places.py` after my one-line PNG change (not run).
- A user edit in the instant between a recipe switch and the server's push (the push could overwrite it; not seen).
- Flicker of "Getting ready ..." at load and after a Blueprint return: seen in tests as short, not timed.
- The full suite (one control run is for later).

## Open points for Eve (nothing was decided by me)
1. SVG with a PDF report on a machine without `rsvg-convert`: the report holds PNG figures, nothing says so (see above).
2. The provisional choices 1-6 above.

`git status --short`: (empty)
