# Removing the Export scope: what must change (a list, no change made)

Digest by the coordinator of a scout's read-only survey of `dev` (`0a1541c3`), 2026-11-18. Every line was READ at the place named; "reasoned" marks an inference. Nothing was run.
NOTE: the survey was briefed before the correction of channel M316. The two export modes and the mode tick STAY (D-0295). So the part "what the tick adds" below is kept as a description of today's two modes, not as a list of things to remove.

## Decided (ledger)
Scope removed, every export holds all plots (D-0292). Fields that stay: quality, plot format, report format, width, height; defaults SVG and HTML (D-0294). Fields kept in memory, one set per recipe and session (D-0288, D-0291). The modes and the tick stay (D-0295). Open: the bundle label; what her "2 modes" means exactly.

## 1. The scope in the code (`app/handlers/export_handlers.py`; none in `libs/`, `scripts/`)
- To remove: the words of the radio (`:514-515`), the builder of the choices (`:518-549`), the label tags (`:552-558`), the radio itself (`:609-632`, placed at `:704`), the effect that keeps it in step with the open tab and its two notices (`:755-779`), the scope filter of the download (`:966-986`), the rule "the reproducibility tick forces all plots" (`:962-965`; it has no object once every export holds all plots).
- Help text to rewrite: `app/src/help/home.md:41`.

## 2. What the bundle writes about the scope
- README line "Export scope" (`:2041`); `t3_steps.yaml` key `export_scope` (`:1375`); `lineage/lineage_graph.json` key `export_scope` (`:1625`). Not in `effective_run.yaml`, not in the picture metadata, not in `report.qmd`.
- The bundle import reads none of them.
- Open for the build: keep these three with the fixed value "global", or drop them.

## 3. Today's two modes (kept), for reference
- Only the tick adds: `data_analysis_recipes_reproducibility/<recipe>.yaml`, `data_reproducibility/<table>.<ext>` (or an `_ERROR.txt`), the README lines that describe those folders, and the section "Random scatter seeds" of `report.qmd`. `effective_run.yaml` differs in one value (`t3_translation_skipped`).
- Nothing of the plain bundle disappears when the tick is on. The only thing the tick changes in the plain part today is the scope (forced to all plots).
- The bundle import refuses a bundle without the reproducibility folders (`bundle_importer.py:220-230`).

## 4. The bundle label and the file name (label: still open with Eve)
- Zip name `<time>_<label>_results.zip` (`:2153-2160`); the folder inside `<time>_<label>` (`:1075`). An empty label becomes the word "user". README line "User :" (`:2037`).
- The two time stamps are taken separately and can differ by a second (reasoned).
- The rule text names the control `export_bundle_label`; the code calls it `export_user_name` (`ui_implementation_contract.md:193`).

## 5. The defaults
- Plot format "png" at `:716-717` and the fallback at `:896` become "svg". Report format is already "html" (`:729`, `:897`).
- A consequence the code shows: for a PDF report, SVG pictures need the tool `rsvg-convert` (`:1155-1168`); without it the report uses a PNG copy (reasoned, not run). To check before the build.
- Tests that assert the png default: `test_export_inputs_survive_plot_tab.py:67, 76`; `test_export_download_path.py:83`.
- **A docs error found:** `docs/user_guide/system_transparency.qmd:117, 127` and `docs/appendix/FAQ.qmd:83` say the QUALITY choice picks the format (Web = SVG, Publication = PNG). The code does not work that way: quality only sets the resolution (`:901`).

## 6. Tests that set or assert the scope
- Headless, to remove with the code: `test_export_scope_choices.py` (5 tests), `test_export_scope_notices.py` (2 of 3).
- Browser, to adapt: `test_export_inputs_survive_plot_tab.py` (4 tests; one is only about the scope), `test_export_download.py`.
- Helpers that pass a scope value: `test_export_download_path.py:83`, `test_export_provenance.py:24, 33`, `test_export_errors_visible.py`.
- On the Export button branch: `test_export_ready_button.py` (11 tests, the field list).

## 7. Rule, design and docs texts that describe the scope (nothing edited)
- Rules (her yes needed): `ui_implementation_contract.md` section 7.2 (lines 186-250; also 24, 258, 411), `rules_app_features_flags.md:25`.
- Comments in five app features files ("bundle zip + scope toggle").
- Design: `export_specification.md` (sections 1.1 and 5 and others), `reproducible_export_design.md:77-92, 147-149`.
- ADR text (hers): ADR-047 (`architecture_decisions.md:1000-1017`), ADR-074 (`:2652-2656`), ADR-097 (`:4900-4902`: "Mode 1 keeps the 3-way scope, Mode 2 forces global").
- User docs: `understanding_your_export.qmd`, `ui_app_features.qmd:86-91, 479`, `reproducible_plots.qmd:12`; the retest procedure (`retest_procedure.md:93, 101`).
- The UML model: 11 places in `docs/UML/app.mdj` name "scope".

## 8. The two branches not yet merged
- Export button branch: its field list goes from eight to six (the scope and nothing else leave; the tick stays; five if the label goes). It holds TWO texts, not three: "Getting ready ..." and "Your last change may not have been received. Check the box and the label, then press Export." (the ready state is the button's own text). Its script reads the field list from the page, so the script itself needs no change.
- Big recipe change branch: the same scope code, shifted by about 12 lines. Removing the scope on `dev` will conflict with it on these lines; the order of the two merges matters.

## What a build must decide (open in the code)
1. The bundle label stays or goes (with Eve).
2. The three scope keys of the bundle: fixed "global" or dropped.
3. With SVG as default: what happens for a PDF report when `rsvg-convert` is missing, and whether the user is told.
4. The order with the big recipe change (same lines).
