-------------------------------------------------------------------
5. RULES, SPEC, DESIGN, LEDGER, ADRs

5.1 .claude/rules/rules_gallery_standards.md (section by section)
- §1 (:7-12) "exactly" four files. DIFFERENT: every bundle also holds preview_thumb.png (glob, 34 files), written by gallery_previews.py:137-138. Not in the companion list (recipe_spec.yaml:215).
- §1 recipe "checked in the gallery profile" (:9): TRUE (recipe_check.py:224-225).
- §2 (:14-35) taxonomy on the plot entry, five axes, geom derived: TRUE (gallery() recipe_check.py:1257-1269; taxonomy.py:33-40).
- §2 (:16) "The name of the example is the ui_label of the plot entry; info holds label, description and submission_date": DIFFERENT from code: name = info.label (gallery_manager.py:107). The sentence also says info holds `label`, so the rule contradicts itself.
- §2 (:37) cheatsheet is "single source of truth for all allowed values"; "Do NOT invent new values; add them to the cheatsheet first": DIFFERENT. The values are read from recipe_spec.yaml:187-215 (taxonomy.py:1-5; spec D3 recipe_format_spec.md:577 says the cheat sheet is generated from it). No code reads the cheatsheet. Adding a value there changes no check.
- §2a-§2d (:40-49) the lists: TRUE (equal to recipe_spec.yaml:191-205).
- §2e (:51-52) geom "must be the first geom_* or stat_* layer" and "see the cheatsheet for the full allowed list": first layer TRUE (taxonomy.py:33-40); allowed list NOT CHECKED (4.2).
- §3 (:54-70) `##` = example name (:59, :67): DIFFERENT. Not enforced; 13 headings differ (section 3).
- §3 (:61, :68) six-field strip on the line right after the h2: TRUE for the output (taxonomy.py:70; all 34 at line 3). Not checked at runtime.
- §3 (:70) icons must match the cheatsheet exactly: not checked; equality of displayed icons TRUE, bytes not verified.
- §4 (:72-102) layer format (no `geom:` key, mapping at plot level): TRUE: a `geom` key in a layer is refused (recipe_check.py:1178, unknown key in layer, PS04).
- §5 (:104-109) "gallery_index.json is the sole source of truth for the UI": imprecise. The viewer reads the example folder files too (gallery_handlers.py:161-233). "Direct editing is FORBIDDEN": nothing enforces it [R]. "Regenerate via refresh_gallery.py (or rebuild_index())": TRUE (refresh_gallery.py:37-41; gallery_manager.py:95). "missing a required taxonomy field excluded": TRUE (GP02, recipe_check.py:1262-1264).
- §6 (:111-119) preview generation: DIFFERENT in four points: (a) path `libs/viz_gallery/assets/generate_previews.py` (:113) does not exist; the script is assets/scripts/gallery_previews.py; (b) `--force` (:116) does not exist; options are --gallery, --out, --only, --apply, --changed (gallery_previews.py:144-151); (c) "renders the first plot_id via VizFactory" (:118): it renders through the app path, ConfigManager + DataOrchestrator + PlotEngines (gallery_examples.py:82, :92, :119; gallery_previews.py:2-8); (d) "writes preview_plot.png": only with --apply, and only when content is unchanged or --changed (gallery_previews.py:134-136). "Do NOT commit a bundle without a valid preview_plot.png" (:119): only existence is checked (recipe_check.py:1278-1282), not validity.

5.2 .claude/design/recipe_format_spec.md (grep: gallery, taxonomy, DEC47, profile)
- Section 9 header (:553): [DECIDED, DEC47 and DEC48].
- :555 describes the old compact bundle as the state "before the conversion" (history, labelled as such).
- :563 G3 (validate the example as a recipe): done (gallery_manager.py:85, gallery_examples.py:40).
- :567 G7 (tag strip generated from taxonomy): generated at write time (gallery_manager.py:203; convert:168-180); not checked at runtime.
- :571 "22 previews pixel-identical, 10 differ only in size, 2 jitter" (proof-of-concept, scratch tmpAI/recipe_format/gallery_poc.py): not verified (C5).
- :575-579 D1-D7: consistent with code (D4 check at rebuild, start, tests: gallery_manager.py:95-161; app/tests/test_gallery_full_check.py).
- :577 D3: "the cheat sheet ... read it or are generated from it": the cheatsheet is neither (no code reads or writes it). DIFFERENT (B3).
- :581 GP01-GP06: matches recipe_check.py:1249-1282. GP05 is not run on the submit path (B21).
- :583-624 "An example looks like this (bar_simple)": not the shipped file. Differences: description texts (:592-593, :618) vs bundle (data_analysis_recipe.yaml:8-9, :36); schema description (:598-599) vs bundle :15; `label:` keys inside input_fields (:604-607) absent from bundle (:20-23); mapping key order (:621) vs bundle :39.
- :930 "a bundle written by GalleryManager.submit_example passes the checker": true only because the companion check is not run on the submit path (gallery_manager.py:196).
- :739/736 table row GP01-GP06 (E = error).

5.3 .claude/design/spaces/GALLERY.md
- :7-16 history (labelled). :22-27 purpose; :53-58 non-goals; :62-67 constraints; consistent with ADR-093 and code.
- :73-76 "Code Modules": lists two modules. DIFFERENT: the gallery has at least eight code modules (gallery_viewer, gallery_handlers, gallery_listing, gallery_examples, viz_gallery gallery_manager, taxonomy, example_recipe, and the scripts).
- :84 "GalleryViewer.submission_modal_ui() is defined but called from nowhere": STALE. Removed (app/tests/test_gallery_texts_and_links.py:48 asserts it is absent; docs/UML/risks_and_technical_debt.md:48 says removed 2026-11-18).
- :38-41 "Search", "Inspect example: description, required columns, dependencies": not built (no such code; status :82-83 agrees).

5.4 Ledger lines (decision_ledger.md; one line each)
- D-0008 (:37), 2026-11-08, gallery: T3 clone removed; Gallery is a static reference browser, no handoff to another space (Eve). DECIDED.
- D-0033 (:62), 2026-11-13, recipe format: one format for every recipe; one checker check_recipe in libs/utils (DEC01-12). DECIDED.
- D-0034 (:63), 2026-11-13, recipe format: `taxonomy` on the plot entry; profiles run/build/gallery/audit (DEC13-26). DECIDED.
- D-0039 (:68), 2026-11-13: DEC47/48: gallery = standard recipes with `taxonomy`. DECIDED.
- D-0046 (:75), 2026-11-14, gallery/missing: submit_example stays, dead submission code goes; NA = not recorded. DECIDED.
- D-0048 (:77), 2026-11-14, process: order of work HOME, then Gallery, Blueprint, Test Lab. DECIDED.
- D-0062 (:91), 2026-11-15, recipes/gallery: beeswarm_sina converted to the new form. DECIDED.
- D-0077 (:106), 2026-11-15, gallery: all gallery recipes and examples rewritten, every one works, nothing left out; gallery screen unchanged. DECIDED.
- D-0181 (:210), 2026-11-16, gallery: the preview command fails when its input files change during a build (option b). DECIDED (code: gallery_examples.py:61-66; gallery_previews.py:21-23).
- D-0251 (:280), 2026-11-18, gallery: the 34 bundles take the new recipe shape in the same pass (one checker, one reader). DECIDED.
- D-0252 (:281), 2026-11-18, gallery, plot file: a plot in its own file holds the whole entry; no new engine now. DECIDED.
- D-0253 (:282), 2026-11-18, names: `label` becomes `ui_label` ("short name: HOME tab, gallery and Blueprint lists"); new `ui_title`; amends D-0237. DECIDED. The gallery list does not follow it (B1).
- D-0258 (:288), 2026-11-18: gallery bundle without a theme gets theme_bw written in (code: recipes carry theme_bw in plot_defaults). DECIDED.
- D-0366 (:400), 2026-11-20: a demo tag needs the agents' walks of HOME and Gallery to find nothing that stops the demo path. DECIDED.
- D-0368 (:402), 2026-11-20, Gallery: keep the selection across space switches (nice to have); Apply keeps the shown example if it still matches; default empty-state text; help explains the Apply rule; a remove-all-ticks button "never existed; adding one is not decided". DECIDED, built and merged per the line (merge 95190ad0, not verified in git).
- D-0379 (:413), 2026-11-20, Gallery: dead links of 7 examples to be updated (6 addresses on r-graph-gallery.com) and a way to remove all ticks in the filter panel. DECIDED, NOT BUILT (no such button in gallery_viewer.py:127-152).
- D-0381 (:415), 2026-11-20: BLUEPRINT, GALLERY and TEST_LAB use the same width and drag mechanism for their side panels as HOME; their side panels likely always visible. DECIDED as working direction.
- D-0382 (:416), 2026-11-20: a dragged panel width is kept in the browser (trial). DECIDED as trial, not built.
- D-0384 (:418), 2026-11-20: after a drag the main panel never goes below half the window. DECIDED, not built.
- D-0387 (:421), 2026-11-20, Gallery: the name shown in the index and the dropdown is the plot `ui_label`; code reads info.label (gallery_manager.py:107); heading not generated from ui_label, no name or heading changed before the study. DECIDED (the field), not built.
- D-0388 (:422), 2026-11-20, Gallery: study before any further name question: (a) map what the Gallery reads (this report), (b) UML actualised, (c) logic reviewed, (d) missing recipe rules listed, (e) ADRs 061 and 063 reviewed (section 5.5). DECIDED (order), in work.
- "Asked, not decided" (:434, A07): the gallery G-b question (the word "filters") is open; one plain sentence is owed.

5.5 ADRs (headings found; body read only where listed)
- ADR-037 heading at architecture_decisions.md:489 (present). Body :500-509. Statements that no longer hold: :504 "libs/viz_gallery/assets/refresh_gallery.py (GalleryIndexer, integrated in GalleryManager)": the script is assets/scripts/refresh_gallery.py; GalleryIndexer does not exist (grep: only libs/viz_gallery/README.md:12). :506-507 taxonomy "in each bundle's info: block": stale, flagged by the note at :509 (the note is there, the body is not corrected). :500 "no direct filesystem scans or YAML parsing for filtering": consistent with the viewer (it reads YAML only for the YAML tab, gallery_handlers.py:213-215).
- ADR-061 heading :1889 (present). Body :1893-1920. Statements describing the OLD format or contradicting today:
  (a) :1899-1907 and :1908-1910: the file is called `recipe_meta.md`; today it is `example_meta.md` (gallery_manager.py:39 META_FILE; rules :56-70).
  (b) :1901 "`## [Recipe Name]`": the rule says example name (rules:59).
  (c) :1903 tag strip with three fields (family, pattern, difficulty): today six (rules:61; taxonomy.py:70).
  (d) :1917 "recipe_template.md updated": the file is now assets/gallery_data/example_template.md (glob); the rename rule is in assets/scripts/rename_vocabulary_rules.yaml:104-105.
  (e) :1918 "All 13 existing recipe_meta.md files migrated": there are 34 example_meta.md files now (glob).
  (f) :1893 and :1899 headings use the `## Family (Purpose): ...` style, history only.
  (g) :1897-1898 both panes open on first load: TRUE (gallery_viewer.py:48, :58-60 `open=True`).
- ADR-063 heading :1947; superseded banner :1949 (present, says the body is history). Body statements still describing the old format or contradicting today:
  (a) :1955 "Add 3 new taxonomy axes to every gallery recipe manifest `info:` block": today taxonomy is on the plot entry (rules:16; recipe_check.py:1258).
  (b) :1957-1961 `geom` typed in the info block with the ⚙️ icon: today derived, not typed (taxonomy.py:33-40; recipe_check.py:1267-1269).
  (c) :1963 "All 34 existing recipe manifests and recipe_meta.md tag strips were updated": file names old (see ADR-061 a).
  (d) :1969 "gallery_manager.py — submit_recipe() accepts 3 new optional params": no `submit_recipe` in code (only assets/scripts/rename_vocabulary_rules.yaml:102); the function is submit_example (gallery_manager.py:163) with `taxonomy` as one dict.
  (e) :1971-1973 "gallery_handlers.py — `_update_gallery_options()` refactored with `_pivot_set(axis, selections)`": no `_pivot_set` exists (grep app, libs, assets, config, docs); the logic is matching_examples (gallery_listing.py:81-97), called from gallery_handlers.py:249.
  (f) :1975 cheatsheet as "single-file canonical reference": today the spec (B3).
  (g) :1980 "Allowed values for geom are the exact plotnine function names (checked against TAXONOMY_CHEATSHEET.md)": not checked (4.2).
  (h) :1970 "all 6 taxonomy sub-panels default to open=False": TRUE (gallery_viewer.py:142).
  (i) :1969 "rebuild_index() adds by_geom, by_show, by_sample_size": TRUE in effect (gallery_manager.py:102, display axes).
  (j) :1978 "rules_gallery_standards.md updated": TRUE for the taxonomy placement (rules:16-35).
- ADR-093 heading :4531 (present), status "ACCEPTED and IMPLEMENTED (Eve, 2026-11-08)" :4533. handle_gallery_clone is gone (grep: no match in app). Consistent with the code. Superseded note :4550 (Blueprint may author plot tier 3) does not change the Gallery rule.

-------------------------------------------------------------------
6. THE CHECKER AND FAILURE BEHAVIOUR

6.1 What the `gallery` profile checks (recipe_check.py:1249-1282), in addition to all run checks (the run checks apply to every profile)
- GP01 exactly one group and one plot (:1253-1254).
- GP04 id equals folder name (:1255-1256; T05 also, :243-244).
- GP02/GP03 the five typed axes present, each in the spec term list, and no unknown key (:1257-1269). A typed `geom` is an unknown key (GP02).
- GP06 source path is the bundle's own example_data.tsv (:1270-1277).
- GP05 companion files exist in the bundle folder: example_data.tsv, example_meta.md, preview_plot.png (:1278-1282; list at recipe_spec.yaml:215). Runs only when `bundle_dir` is passed (recipe_loader.py:122-123), which the folder check does (gallery_manager.py:85) and submit does not (gallery_manager.py:196).
- Errors vs advice: only errors reject (gallery_manager.py:89-90; Result.errors recipe_check.py:140-141). Advice (severity A) is never shown (B33).
- Other checks that matter here, from the run profile: I01 info.label required (:315-316); P01 plot ui_label required (:1126-1127); G01 group ui_label required (:1101-1102); PS02 target_dataset (:1146-1147); PS03 mapping/layers, geom presence (:1148-1149, :1215-1216); PS04 layer names and arguments against the catalogs (:1168-1196); PS05 theme (:1160-1164, only if `themes` catalog given).

6.2 What is NOT checked today (a recipe may pass and still fail or mislead)
- Data columns versus `mapping`/`layers`/`input_fields`: the gallery check runs without `graph`, so the "columns" coverage is absent (recipe_check.py:231-232; gallery_examples.py:40; gallery_manager.py:73-74). Only the preview script catches a mismatch (test app/tests/test_gallery_app_path.py:59-66).
- Data types against the file: only when the picture is drawn [R].
- Plot ui_label and group ui_label: required, but nothing uses them (6.3).
- Heading `##` and the `### Suitability` section: not checked; only the presence of the file is (GP05).
- Tag strip equals taxonomy: checked only by the test libs/viz_gallery/tests/test_gallery_examples_are_recipes.py:67-72, not at start or in the check.
- preview_plot.png: existence only (GP05), not content, not a hash, not tied to the recipe (gallery_manager.py:106-112 stores no hash).
- preview_thumb.png: not checked, not shown.
- example_data.tsv: existence only (GP05), not readability; a corrupt file shows an error table in the Data Sample tab (gallery_handlers.py:198-200).
- Plot ids unique across examples: check_recipe_set (recipe_check.py:1285-1298) is not called by the gallery; only by libs/utils/tests/test_recipe_check.py:401-404.
- Duplicate info.label across examples: not checked [R: two identical dropdown entries, matching_examples keys by id, gallery_listing.py:97].
- info.description, info.contact, plot and group descriptions: advice only (recipe_check.py:319-321, :1103-1104, :1128-1129). Every bundle lacks `contact` (grep); so every bundle gets an advice that nobody sees.

6.3 Fields the checker requires that the gallery never reads
- plot `ui_label` (P01) and group `ui_label` (G01): required; nothing in libs/viz_gallery or app gallery code reads them.
- info.label IS read (gallery_manager.py:107), so it is the real name today.

6.4 What the gallery does when a field is missing or wrong (verified by reading)
- Missing or wrong in a checked field (info.label, the five taxonomy axes, an unknown taxonomy key, id != folder, a layer with an unknown name or argument, a missing geom, a missing companion file, a missing plot ui_label or target_dataset): the example is LEFT OUT of the index with its reasons (gallery_manager.py:89-93, :135-137); the app prints each reason (bootloader.py:243-244); the sidebar shows a block "N example(s) not shown, failed the check" listing each folder with its FIRST reason only (gallery_listing.py:47-53; gallery_handlers.py:270-287). No crash (bootloader.py:238-241).
- Missing or wrong in an unchecked field: the example is listed and shown with whatever is there: a bad heading shows as an odd heading (no error); a corrupt TSV shows an error table (gallery_handlers.py:198-200); a corrupt or non-PNG preview shows a broken image (gallery_handlers.py:165-180) [R]; a missing thumb is invisible; a missing YAML shows "Source YAML not found" (gallery_handlers.py:216); a missing `path` in the index shows "Path missing in index." (gallery_handlers.py:162-163).
- Missing index: the list is empty with no message until Apply, which then says "Indexer not found or no example passed the check." (gallery_listing.py:65-69; gallery_handlers.py:243-244).
- Start check raised an exception: status "failed", the listing is built from the old index and shows "The gallery check could not run, so the list may be out of date." (bootloader.py:238-241; gallery_listing.py:54-55).
- Folder read-only: the old index stays, "The gallery folder is read-only, so the list was not rewritten." (gallery_manager.py:141-161; gallery_listing.py:52-53).

-------------------------------------------------------------------
7. UML (docs/UML/app.mdj; grep only, 54 name matches)
Model elements (type, name, line):
- UMLModel "GALLERY" (:28719) with UMLUseCaseDiagram "UC-GALLERY What a user does" (:28727), FCFlowchartDiagram "COM-REACTIVE-GALLERY Reactive wiring of GALLERY" (:31043), WFWireframeDiagram "UI-GALLERY The screen" (:32475), and C4Diagram "C4-COMP-GALLERY Inside GALLERY" (:111406).
- FCProcess entries in the reactive diagram: "input: gallery_example_select" (:32170), "input: btn_apply_gallery_filters (event)" (:32216), "gallery_index.json (file, not reactive)" (:32285), FCPredefinedProcess "_gallery_active_metadata" (:32334), FCProcess "_init_gallery_selector" (:32396; NOT IN CODE: B25), FCProcess "_update_gallery_options" (:32404), FCProcess "gallery_preview_img" (:32427), "gallery_static_data" (:32435), "gallery_yaml_preview" (:32443), "gallery_md_content" (:32451), "gallery_browser_anchor (placeholder)" (:32459).
- WFWebFrame "GALLERY" (:33105) with WFPanels: "Navigation: Home, Blueprint Architect, Test Lab, Gallery, Help" (:33113), "Example: selector (gallery_example_select)" (:33147), "Gallery Taxonomy: Family, Pattern, Difficulty, Geom, Show, Sample size; Apply" (:33181), "Title banner: 'Gallery Inspiration'" (:33222), "Preview, collapsible (gallery_preview_img)" (:33256), "Guidance (example_meta.md rendered) (gallery_md_content)" (:33290), "Example data table (gallery_static_data)" (:33324), "Raw YAML preview, copy by hand (gallery_yaml_preview)" (:33358). Each has a WFText of the same name.
- Navigation WFPanel/WFText "Navigation: Home, Blueprint Architect, Test Lab, Gallery, Help" also at :11778, :12449, :24596, :24604, :26542, :26550, :46966, :46974, :53035, :53043 (other wireframes).
- FCProcess "NOT CHANGED: Blueprint, Gallery, Test Lab. ..." (:28707): a note-like process, not a gallery element.
- UMLPackage "viz_gallery" (:56879); UMLArtifact "gallery folder" (:59906).
- UMLAttribute "gallery" (:92054) in UMLClass "Locations"; UMLAttribute "gallery_enabled" (:92217) in UMLClass "Flags"; UMLAttribute "gallery" (:92312) in UMLClass "Workspaces (sidebar panels)".
- C4Component "GALLERY handlers" (:107061); C4Component "gallery_handlers" (:111279); C4Component "gallery_viewer" (:111326); C4Component "viz_gallery (GalleryManager)" (:111366); C4Container "Gallery" (:114362).
- Not present (grep for "gallery" is case-insensitive in my pattern): no element for gallery_listing, gallery_examples, taxonomy, example_recipe, GalleryViewer as a class, the scripts (refresh_gallery, gallery_previews, convert_gallery_examples), the CSS/JS file gallery_select_all.js.
- docs/UML/risks_and_technical_debt.md:48 (not a UML file) records the removal of submission_modal_ui.

-------------------------------------------------------------------
8. TESTS (every file on the gallery; one line each; "by name" = I read only the names and docstring, not the body)

libs/viz_gallery/tests/
- test_gallery_bundle.py (29 test functions; names read; head read lines 1-60): the taxonomy from the spec, the derived geom, the tag strip set/added/refused, the filter panels in spec order with only used terms, the plot entry shape, the steps placement, the data contract typing and null texts, a good example indexed, a rejected one left out with its reason, a wrong folder id, the old form, a missing folder/recipe, the empty gallery, the catalogs passed and coverage stated, submit_example accepted/refused with no leftover folder. (Bodies after line 60 not read: one-liners by name.)
- test_gallery_examples_are_recipes.py (7 test functions incl. parametrised; read): the gallery has >= 30 examples; each shipped example is a standard recipe with no errors (WAITING is empty); the WAITING ratchet; all companion files exist; the structure-only check accepts all; the tag strip of each shipped example equals its taxonomy.
- debug_gallery_ui_logic.py (not a test in effect; read): a headless printout of a filter intersection; test_gallery_filtering asserts nothing; imports app.src.bootloader; its comments say "from server.py". Named test_ but pytest's default naming does not collect it (no pytest config found; C12).

app/tests/
- test_gallery_full_check.py (7 functions; read): the catalogs hold the registries; every shipped example passes the full check (coverage = structure, actions, components); the full check finds a wrong layer, a wrong argument, a wrong theme; the committed index equals the index rebuilt from the examples (registry with relative paths, pivot, count, coverage); the dumbbell geom is geom_line in the index; refresh_gallery reports without --apply and writes with --apply.
- test_gallery_app_path.py (7 functions; partly read): for each accepted example the table read by the app path equals a plain read of the TSV and the picture renders at 960x600; data that does not fit the contract gets no picture; a missing data file gets no picture; two examples in one work folder stay separate; compare() classifies identical/size only/differs/new; apply writes only unchanged pictures; the thumb is recreated.
- test_gallery_check_at_start.py (9; by name): refuses a wrong argument and theme; all valid leaves the index untouched; one broken example left out with reason and nothing raises; a read-only folder keeps the app running; the bootloader runs the check only when enabled; the atomic write.
- test_gallery_listing.py (12; by name): rejected example not listed even if the old index lists it; read-only and writable notices; no block when nothing rejected; failed-check line; a missing or corrupt index gives an empty listing; a stale index never opens a rejected id.
- test_gallery_texts_and_links.py (5; read): every external link opens in a new tab; internal anchors untouched; every shipped guidance link fixed; removed promises gone (no Architect sandbox text; the GitHub-button text present); dead submission form gone (submission_modal_ui absent, submit_example callable).
- test_gallery_viewer_taxonomy.py (3; read): the filter panels come from the spec (labels, icons, ids, order, no "Numeric-Numeric"); the viewer and handler files hold no copy of the taxonomy terms or labels; the left-out slot is in the sidebar.
- test_gallery_script_loaded.py (2; by name): the Gallery script tag is on the page only when gallery_enabled.
- test_convert_gallery_examples.py (11; by name): dry run writes nothing; apply writes a standard recipe that passes the check; the typed geom is replaced and reported; a second run changes nothing; a stale tag strip is set again; unconvertible examples left as they are with the reason; two plots or a missing data file refused; only named examples; missing value text declared on its field; a gallery outside the project root refused; the command line returns 1 when an example is not converted.
- test_shiny_gallery_filters.py (7; by name, Playwright): no-match standing line; first paint of dropdown and picture agree; the apply rule text; help states the apply rule; a tick right after Select all is not wiped; Apply keeps a still-matching example; an Apply that excludes the example says so.
- test_shiny_gallery_left_out.py (3; by name, Playwright): the block names the broken example and reason; the select has no option for it; asking for its preview shows nothing.
- test_shiny_gallery_state.py (2; by name, Playwright): return from HOME keeps example and filters; a return keeps ticks not applied.
- test_shiny_smoke.py (3 gallery tests inside a class; by name): developer sees gallery (:228); simple hides gallery and devstudio (:250); the gallery left sidebar shows alerts (:579).
- test_ui_scenarios.py:48-59 test_gallery_taxonomy_parsing: only checks that the ridgeline meta file contains two substrings; the name says "parsing" (weak, B28).
Other tests that cover the gallery as part of a wider rule (by grep): test_descriptions_are_whole.py:1-16 (every gallery recipe description is whole); test_checker_advice_visible.py:65-72 (no shipped gallery recipe gets join advice); test_no_self_join_in_shipped_recipes.py:17 (gallery recipes have no self join); test_shipped_recipes_write_their_seeds.py:1-19 (each gallery recipe writes its seeds); test_plot_callers_are_checked.py:56-70 (an example that cannot be drawn leaves no picture); test_data_analysis_recipe_validator.py:221-224 (gate and gallery share the catalogs); test_scripts_need_the_app_path.py:78-83 (the printed hint command works); test_legacy_formats.py:152-167 (old bundle names converted); test_no_old_recipe_keys_read.py:21 (allows convert to read the old form); test_bootloader_launch.py:34,106,138 (gallery key and flag); test_app_features_validator.py:10.

-------------------------------------------------------------------
(A) TABLE: field -> read by -> shown where

field (where in bundle) | read by (file:line) | shown where
info.label (recipe L6) | gallery_manager.py:107; checker recipe_check.py:315-316 (required) | dropdown, selected name, "dropped" note (gallery_listing.py:97; gallery_viewer.py:119-124; gallery_handlers.py:157-158, 258, 261-265); YAML tab (raw)
info.description (L7-9) | checker advice recipe_check.py:319-321 only | YAML tab (raw) only
info.submission_date (L10) | written example_recipe.py:106-107; nothing at runtime | YAML tab only
info.contact / subtitle / version / comment | none in any bundle (grep) | none
id (L1) | checker recipe_check.py:243-244, 1255-1256; copy name gallery_examples.py:78 [R] | none
spec_version, data_engine, plot_engine (L2-4) | checker recipe_check.py:246-262; PlotEngines gallery_examples.py:119 [R] | none; picture
data_schemas.example.label (L13) | nothing | YAML tab
schema description (L14-15) | advice recipe_check.py:392; writer example_recipe.py:110 | YAML tab
source.type, source.path (L16) | checker recipe_check.py:1270-1277; loader gallery_examples.py:82, 92 [R] | picture (viewer uses the TSV next to the index path, gallery_handlers.py:193)
null_values, strip (L17-18) | loader [R]; NOT the Data Sample tab (gallery_handlers.py:197) | picture only
input_fields (L19-23) | checker [R] (schema part); loader [R]; test_gallery_app_path.py:43-46 | YAML tab
tier1 (L24) | gallery_examples.py:92 (DataOrchestrator) | picture only
plot_defaults.theme (L25-26) | engine [R] | picture only
analysis_groups.example.ui_label (L30) | checker recipe_check.py:1101-1102 (required) | nothing; YAML tab
group description (L31) | advice recipe_check.py:1103-1104 | nothing; YAML tab
plot ui_label (L34) | checker recipe_check.py:1126-1127 (required); NO gallery reader | nothing; YAML tab  [owner's name field, D-0387]
plot description (L35-36) | advice recipe_check.py:1128-1129; ignored by plot library (recipe_spec.yaml:55-57) | YAML tab
plot taxonomy (L37), five axes | taxonomy.py:55-65 via gallery_manager.py:105; checker recipe_check.py:1257-1269; writer example_recipe.py:125 | index registry.taxonomy and pivot (gallery_manager.py:111-114) -> sidebar checkboxes (gallery_viewer.py:127-152; taxonomy.py:95-109) -> matching (gallery_listing.py:81-97)
derived geom (first geom_/stat_ layer, L40-41) | taxonomy.py:33-40 (called :64); example_recipe.py:89; convert_gallery_examples.py:164 | index taxonomy.geom and pivot.by_geom -> "Primary Geom" filter
target_dataset (L38) | checker recipe_check.py:1146-1147; gallery_examples.py:91 | picture
mapping (L39) | checker recipe_check.py:1148-1149, 1156-1159; engine [R] | picture
layers (L40-41) | checker recipe_check.py:1168-1216; first_geom (taxonomy.py:33-40) | picture; geom filter
labs title (16 recipes, e.g. area_simple.yaml:39) | engine [R] | title printed inside preview_plot.png
example_data.tsv | gallery_handlers.py:193-197; checker GP05 recipe_check.py:1278-1282; writers gallery_manager.py:189, example_recipe.py:39-82 | Data Sample tab (all rows, plain read)
example_meta.md | gallery_handlers.py:229-232; GP05; convert_gallery_examples.py:61-73, 135-180; writer gallery_manager.py:203; test_gallery_examples_are_recipes.py:67-72 | guidance pane: H2 title, strip blockquote, H3 sections, external links in a new tab (gallery_listing.py:104-118)
  - ## heading (L1) | gallery_handlers.py:232 (markdown) | the H2 of the guidance pane
  - strip (L3) | not read at runtime | blockquote in the pane (theme.css:658)
  - ### Suitability (L5-6) | convert only (convert_gallery_examples.py:61-73, 149) | guidance pane
preview_plot.png | gallery_handlers.py:165-170; flag gallery_manager.py:109 (unread); gallery_previews.py:131 | "Plot Preview" tab
preview_thumb.png | written gallery_previews.py:137-138; flag gallery_manager.py:110 (unread) | nothing
gallery_index.json | gallery_listing.py:59-69 via gallery_viewer.py:66-69 and gallery_handlers.py:58-61; gallery_manager.py:151-152; refresh_gallery.py:41 | the list, the pivot, names, paths, notice
index registry.<id>.path | gallery_handlers.py:161, 186, 206, 221 | which folder is read for picture, data, YAML and guidance
index metadata.rejected | gallery_manager.py:152 (start check); tests; viewer uses bootloader.rejected_gallery_examples (gallery_viewer.py:68-69) | notice block (gallery_listing.py:47-55)
index metadata.generated_at, count | nothing at runtime (count: tests full_check.py:98) | none
index metadata.coverage | refresh_gallery.py:41 (apply report); tests full_check.py:100 | console only
index has_preview, has_thumb | nothing | none
index registry.<id>.taxonomy | tests only (test_gallery_bundle.py:201; test_gallery_full_check.py:106) | none directly
gallery_enabled (app features) | bootloader.py:230; ui.py:87; sidebar_registry.py:64, 88; server.py:265 | whole Gallery
example_template.md (gallery_data root) | nothing (glob; rename rule only) | none
help page gallery.md | home_theater.py:1852 | help overlay

-------------------------------------------------------------------
(B) CONTRADICTIONS AND GAPS (numbered; file:line)

Contradictions between records, rules, docs and code
B1. The name. Owner decided the plot `ui_label` (ledger.md:421, D-0387; also ledger.md:282 D-0253: "gallery and Blueprint lists use ui_label"; rules_gallery_standards.md:16). Code reads info.label (libs/viz_gallery/src/viz_gallery/gallery_manager.py:107; list at gallery_listing.py:97). DECIDED, not built; the study first (ledger.md:422).
B2. Heading. rules_gallery_standards.md:59, :67 say `##` = example name. Owner says the heading is guidance text, not redundant (ledger.md:421). 13 headings differ from the name (section 3). No check reads the heading.
B3. Cheatsheet as source. rules_gallery_standards.md:37 "single source of truth"; ADR-063:1975 "single-file canonical reference". Code: recipe_spec.yaml:187-215 (taxonomy.py:1-5). recipe_format_spec.md:577 D3 says the cheat sheet is read from or generated from the spec; no code reads or writes TAXONOMY_CHEATSHEET.md (grep).
B4. Cheatsheet old form. TAXONOMY_CHEATSHEET.md:11-16 (info.family, info.pattern, info.difficulty, info.geom, info.show, info.sample_size) and :103-115 (info block with `name:`) describe the old recipe format. Today taxonomy is on the plot entry (rules_gallery_standards.md:16-35; recipe_check.py:1258; gallery_manager.py:105).
B5. geom list. rules_gallery_standards.md:52 and TAXONOMY_CHEATSHEET.md:53-59 and ADR-063:1980 say geom is checked against an allowed list. Not checked: recipe_check.py:1262-1266 loops only the five axes; recipe_spec.yaml:189 has no geom; taxonomy.py:98-101 says it is open.
B6. Start-up check blind to changes. gallery_manager.py:152-153 rewrites the index only when the set of accepted names or the rejected dict changes. A changed name, taxonomy, path or picture is not picked up (see G1).
B7. Count of files. rules_gallery_standards.md:7-12 says "exactly" four files. All 34 bundles also hold preview_thumb.png (glob), written by assets/scripts/gallery_previews.py:137-138.
B8. Index as "sole source". rules_gallery_standards.md:106 vs gallery_handlers.py:161-233 (the viewer reads folder files). Imprecise wording.
B9. "Direct editing forbidden" (rules:107): no enforcement found [R].
B10. Preview tool. rules_gallery_standards.md:113 path libs/viz_gallery/assets/generate_previews.py does not exist (libs/viz_gallery/assets holds only .pyc, glob); :116 `--force` does not exist (gallery_previews.py:144-151); :118 "via VizFactory" is wrong (gallery_examples.py:82, :92, :119; gallery_previews.py:2-8); :118 "writes preview_plot.png" is true only with --apply and not for changed pictures (gallery_previews.py:134-136).
B11. Preview validity. rules:119 "valid preview_plot.png" vs existence check only (recipe_check.py:1278-1282).
B12. libs/viz_gallery/README.md:12 "GalleryIndexer" (not in code); :19 `libs/viz_gallery/assets/refresh_gallery.py` (real: assets/scripts/refresh_gallery.py); :25 `libs/viz_gallery/assets/generate_previews.py ... --force` (wrong); :32 "checked in the `gallery` mode" (the profile is `gallery`); :30 "all four files" (five present).
B13. docs/user_guide/viz_gallery.qmd:45 same wrong script path.
B14. ADR-037:504 "libs/viz_gallery/assets/refresh_gallery.py (GalleryIndexer ...)": wrong path; GalleryIndexer does not exist. :506-507 taxonomy in the info block: stale; the note at :509 says so.
B15. ADR-061:1899-1907 names `recipe_meta.md` (now example_meta.md, gallery_manager.py:39); :1903 three-field strip (now six; taxonomy.py:70); :1917 recipe_template.md (now assets/gallery_data/example_template.md); :1918 "13 files" (now 34).
B16. ADR-063 body (:1955-1980) describes the old format, although the banner (:1949) says history. Specific: :1955 info block (now plot taxonomy); :1957-1961 typed geom (now derived); :1963 "recipe_meta.md tag strips" (old name); :1969 submit_recipe() (now submit_example, gallery_manager.py:163); :1971-1973 _pivot_set (not in code; matching_examples gallery_listing.py:81-97); :1975 cheatsheet as canonical (B3); :1980 geom checked against the cheatsheet (B5).
B17. Spec sample. recipe_format_spec.md:583-624 "An example looks like this (bar_simple)" is not the shipped file: descriptions (:592-593, :618), schema description (:598-599), `label:` keys in input_fields (:604-607), mapping order (:621). The shipped file is bundle data_analysis_recipe.yaml.
B18. Submit path. recipe_format_spec.md:930 "a bundle written by submit_example passes the checker" and :581 GP05 companion check. submit_example checks without bundle_dir (gallery_manager.py:196), so GP05 never runs on submit; the files are written after the check (:202-204).
B19. GALLERY.md:84 "submission_modal_ui() is defined but called from nowhere": removed (app/tests/test_gallery_texts_and_links.py:48; docs/UML/risks_and_technical_debt.md:48). GALLERY.md:73-76 lists two code modules (there are eight or more).
B20. UML app.mdj:32396 "_init_gallery_selector" (FCProcess): no such function (grep app: none; the handler has _update_gallery_options, gallery_handlers.py:237).
B21. gallery_viewer.py:4 @deps "consumed_by: app/handlers/gallery_handlers.py": the handler does not import gallery_viewer (gallery_handlers.py:35-37). Minor.
B22. libs/viz_gallery/tests/debug_gallery_ui_logic.py: named test_, asserts nothing (:9-70), imports app.src.bootloader (:2), against the library rule ("no import of peers", libs/viz_gallery/tests/test_gallery_examples_are_recipes.py:3-4; gallery_manager.py:11-12). Comment "from server.py" (:33) is stale.
B23. app/tests/test_ui_scenarios.py:48-59 named taxonomy parsing; it checks two substrings only (weak).
B24. Ledger D-0379 (:413): dead links to fix (7 examples) and a remove-all-ticks button: DECIDED, not built. No link check exists (test_gallery_texts_and_links.py checks target only). The button is absent (gallery_viewer.py:127-152).
B25. Ledger D-0368 (:402) says the remove-all button "never existed" and adding one "is not decided"; D-0379 (:413) later decides it. The records disagree on the status: D-0379 completes D-0368 (the relation is stated in D-0379), so this is consistent as a sequence. Not a contradiction; kept for the record.
B26. Advice never shown: gallery_manager.py:89-90 keeps only errors; the advice codes I02, G02, P02, S04 (recipe_check.py:319-321, 1103-1104, 1128-1129, 392) never reach the user.

Gaps in the code (verified unless marked [R])
G1. Stale index is silent. gallery_manager.py:152-153 compares only names and rejected; a changed label, taxonomy, path or picture does not rewrite the index at start (verified). Effect until refresh_gallery.py --apply: the pivot and the filters show the old values [R].
G2. Plot not checked against data. gallery_examples.py:40 and gallery_manager.py:85 run without graph; recipe_check.py:231-232 adds "columns" only with graph. An example whose columns do not fit stays listed with its old picture (verified). Only assets/scripts/gallery_previews.py finds it.
G3. Picture not tied to recipe. gallery_manager.py:106-112 stores no hash or time of the recipe or data; the picture is never re-checked at start (verified).
G4. One reason on screen. gallery_listing.py:51 shows reasons[0] only; the others are in the index and the console (verified).
G5. Data Sample not the contract. gallery_handlers.py:197 plain read; the picture uses the contract (gallery_examples.py:97-100). Equal for the 34 today (test_gallery_app_path.py:43-46), so latent (verified).
G6. Encoding. gallery_handlers.py:214 and :231 open files with no encoding argument. The files contain non-ASCII (e.g. violin_boxplot recipe line 43 em dash; the icons on line 3 of each example_meta.md). Effect on a non-UTF-8 default locale is [R].
G7. Missing index. Silent until Apply (gallery_listing.py:65-69; gallery_handlers.py:243-244) (verified).
G8. Index paths fixed at build time. gallery_manager.py:108 stores the path string used at build; the viewer uses it (gallery_handlers.py:161-229). If the gallery location changes, the start check does not rewrite (see G1) [R].
G9. Duplicate names. Not checked (verified: no such check); two identical dropdown entries are possible [R].
G10. Plot ids across examples. Not checked (recipe_check.py:1285 not called by the gallery).
G11. Unused required fields. plot ui_label (P01) and group ui_label (G01) are required and never read by gallery code (verified).
G12. Unused index fields. has_preview, has_thumb, generated_at (verified: no reader).
G13. info.submission_date written and never read (verified).
G14. Tag strip and heading not checked at start (verified; only test_gallery_examples_are_recipes.py:67-72 checks the strip).
G15. Advice on every bundle. info.contact is absent in all 34 (grep), so I02 advice fires on every bundle (recipe_check.py:319-321) and is never shown (verified; the count is from grep).
G16. Thumb unchecked and unshown (verified).
G17. Links. External links in the 34 guidance files are not checked for liveness (D-0379 says some are dead). Not verified (no network) (C8).
G18. Index generated_at (2026-11-15 13:11:10, gallery_index.json:3) is earlier than the ledger date of the 34-bundle conversion (D-0251, 2026-11-18, ledger.md:280); the content equals the current recipes (verified 34 of 34). The order is not explained by any file read [R] (C5).
G19. The list of rejected examples uses folder names, not labels (gallery_listing.py:51); the bootloader prints folder names (bootloader.py:244). Consistent with the check, but not with the name decision.

-------------------------------------------------------------------
(C) WHAT I COULD NOT VERIFY

C1. No shell: no `git log -15 -- assets/gallery_data/TAXONOMY_CHEATSHEET.md`; no git history of any kind; the commit claims in the ledger (e.g. merge 95190ad0, D-0368) are not checked.
C2. No test run, no app run, no render. What the screen shows is reasoned from the code and the CSS (e.g. that ui.markdown renders `##` as H2 in the pane: theme.css:651, gallery_handlers.py:232 [R]).
C3. Whether the committed preview_plot.png files equal a fresh render of the current recipes (needs assets/scripts/gallery_previews.py). Not run.
C4. Whether the committed gallery_index.json equals a rebuild now (test app/tests/test_gallery_full_check.py:90-100 would say; not run).
C5. The index generated_at date vs the conversion decision date (G18): cause not determined.
C6. Picture sizes and content: not inspected (the 960x600 claim, recipe_format_spec.md:565, not checked). The claims in recipe_format_spec.md:571 (22 identical pictures, 10 size only, 2 jitter) are a scratch result (tmpAI/recipe_format/gallery_poc.py), not verified.
C7. Icon characters: cheatsheet and recipe_spec.yaml display the same glyphs; byte identity (e.g. variation selectors) not compared.
C8. External links and dead-link status (D-0379): no network use; not checked. Links per file not enumerated.
C9. Engine and loader internals (ConfigManager, DataOrchestrator, PlotEngines, the plot library): not read. Which recipe keys they read (id, null_values, strip, input_fields, tier1, plot ui_label, description) is [R] only.
C10. Test bodies: read only test_gallery_bundle.py lines 1-60, test_gallery_examples_are_recipes.py, test_gallery_full_check.py, test_gallery_app_path.py lines 20-80, test_gallery_texts_and_links.py, test_gallery_viewer_taxonomy.py. The rest are one-liners from names (marked "by name").
C11. libs/viz_gallery/tests/data/data_analysis_recipe.yaml and example_data.tsv: no reference found by grep in libs/viz_gallery; use in other tests not checked.
C12. Whether pytest collects libs/viz_gallery/tests/debug_gallery_ui_logic.py: no pytest config found in the globs tried; default naming assumed [R].
C13. Whether the reactive/click behaviour described in the UML matches the code beyond the names listed.
C14. Whether X5 (plot-id uniqueness) would matter to the app for gallery plots (G10): not traced.
C15. Owner decisions not yet taken: heading vs name (B2), the study outcome (D-0388), the empty state of the labs title in pictures; these are open, not checked for further lines beyond the ledger.
