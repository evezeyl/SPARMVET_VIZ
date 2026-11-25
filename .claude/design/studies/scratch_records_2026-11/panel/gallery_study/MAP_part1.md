MAP OF THE GALLERY (part a). Read-only. Nothing changed.

SCOPE AND LABELS
- ROOT = /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ (branch dev, clean at start). Paths below are relative to ROOT.
- Tools: Read, Grep, Glob only. No shell: no `git log` (so no cheatsheet history), no pytest, no app run, no rendering. tmp.md not read.
- Untagged facts are verified (read, or a grep result, at the cited line). [R] = reasoned from code I read, not run.
- Decisions: the brief has no "Decisions" block. I read the ledger `.claude/knowledge/decision_ledger.md` directly. Governing lines: D-0387 (line 421, the name) and D-0388 (line 422, the study order), both quoted in the brief. Also D-0253 (282), D-0251 (280), D-0252 (281), D-0039 (68), D-0033 (62), D-0034 (63), D-0046 (75), D-0077 (106), D-0181 (210), D-0008 (37). Section 5 lists them.

HEADLINE
1. The name: the index and the dropdown read `info.label` (libs/viz_gallery/src/viz_gallery/gallery_manager.py:107). The owner decided the plot entry `ui_label` (D-0387, ledger:421; the rule file says the same at .claude/rules/rules_gallery_standards.md:16). No gallery code reads a plot `ui_label`. Today all 34 examples have identical `info.label` and plot `ui_label`, so nothing shows the difference yet. Status: DECIDED, not built; D-0388 orders a study first.
2. 13 of 34 `##` headings differ from the name. The heading is shown in the guidance pane (app/handlers/gallery_handlers.py:232). Section 3 lists them.
3. Taxonomy: all typed values and all derived geoms of the 34 examples are in TAXONOMY_CHEATSHEET.md, and all 34 tag strips equal the recipe taxonomy. No disagreement found. The cheatsheet, ADR-061 and ADR-063 still describe the old format.
4. The start-up check does not rewrite the index when a name, a taxonomy or a picture changes (gallery_manager.py:152-153). The stale index stays silently until `refresh_gallery.py --apply` is run.
5. The geom is not checked against any list. The checker judges only the five typed axes (libs/utils/src/utils/recipe_check.py:1262-1266).

-------------------------------------------------------------------
1. COMPONENTS, ROLE, INPUTS, OUTPUTS, CALLERS

1.1 libs/viz_gallery/src/viz_gallery/gallery_manager.py (class GalleryManager, 210 lines)
- Role: lists example folders (:61-63); checks each with `check_recipe` profile `gallery` (:65-93); builds `gallery_index.json` (:95-139); syncs it at start (:141-161); writes a new example (`submit_example`, :163-209).
- Inputs: gallery folder; `catalogs` (actions and components) from the app layer; recipe files via libs/utils/src/utils/recipe_loader.py:113-126 (`check_recipe_file`, which sets `bundle_dir` for profile gallery, :122-123).
- Outputs: the index (atomic write, :125-134); console lines (:135-138); example folders (submit).
- Callers: app/modules/gallery_examples.py:40,49,54 (check_gallery, check_gallery_at_start, rebuild_gallery_index); tests (libs/viz_gallery/tests/test_gallery_bundle.py:269 calls `submit_example`; this is the only caller of `submit_example`, per the module docstring :15 and grep).
- Consumes: utils.legacy_keys.LEGACY_GALLERY_FILES (:32), utils.recipe_check.check_recipe (:33).

1.2 libs/viz_gallery/src/viz_gallery/taxonomy.py
- Role: the six axes (`display_axes` :28-30), the derived geom (`first_geom` :33-40), the typed-plus-derived taxonomy of an example (`example_taxonomy` :55-65, geom at :64), the tag strip line (`tag_strip` :68-70), the strip writer (`with_tag_strip` :73-92), the filter panels (`filter_panels` :95-109).
- Inputs: `spec()["gallery"]` from libs/utils/src/utils/recipe_spec.yaml:187-215.
- Outputs: dicts, the strip text, panel descriptors `{axis, pivot_key, label, choices}`.
- Callers: gallery_manager.py:36; gallery_viewer.py:12,109; gallery_handlers.py:37; example_recipe.py:31; assets/scripts/convert_gallery_examples.py:43; libs tests and app tests.

1.3 libs/viz_gallery/src/viz_gallery/example_recipe.py
- Role: writes an example as a standard recipe: `example_recipe` (:93-142), `dump_example` with a read-back check (:210-219), `data_contract` (:39-76, types and null texts generated from the TSV), `data_summary` (:79-82), `plot_summary` (:85-90).
- Inputs: TSV path, fields, taxonomy, plot spec, texts. Outputs: recipe dict and YAML text.
- Callers: gallery_manager.py:35 (submit); assets/scripts/convert_gallery_examples.py:41.

1.4 libs/viz_gallery/src/viz_gallery/__init__.py: docstring only (:1-15), exports nothing.

1.5 app/modules/gallery_examples.py (app layer; the only place that combines libraries)
- `check_gallery` (:38-40) uses `checker_catalogs()` from app/modules/data_analysis_recipe_validator.py.
- `check_gallery_at_start` (:43-49), `rebuild_gallery_index` (:52-54).
- `tell_inputs_changed` (:61-66), `_build` (:69-94: copies the recipe to `<work>/<folder>.yaml` :78, loads it with ConfigManager :82, takes the plot with `the_plot` :85, reads `target_dataset` :91, runs DataOrchestrator tiers :92 and :94).
- `example_table` (:97-100), `render_example` (:103-122, PlotEngines at :119), PREVIEW_SIZE 960x600 at 120 dpi (:35).
- Callers: bootloader.py:235 (start check); assets/scripts/refresh_gallery.py:25; assets/scripts/gallery_previews.py:43; tests app/tests/test_gallery_full_check.py:16, test_gallery_app_path.py:19, test_plot_callers_are_checked.py:20.

1.6 app/modules/gallery_viewer.py (GalleryViewer; singleton at :183)
- Role: the sidebar (`build_sidebar_ui` :94-159: the Example dropdown :119-124, the Gallery Taxonomy panels :127-152 built by `filter_panels` :109, the Apply button :146-150, the left-out notice slot :159), the main screen (`render_explorer_ui` :161-179: banner :166-175, `gallery_browser_anchor` :176, `split_viewer_layout` :177), the accordions and tabs (`split_viewer_layout` :24-64: "Plot Preview", "Data Sample", "YAML Example" :35-42; "Visual Cookbook: Guidance" :53).
- Inputs: `state` (gallery_state dict, :94-98) and the listing read from the index (`_load_listing` :66-69).
- Outputs: Shiny UI.
- Callers: server.py:25 (import) and :210 (passed to home_theater); home_theater.py:1033-1034 (`render_explorer_ui`); home_theater.py:2017 (`build_sidebar_ui` inside `_render_gallery_main`).
- Note: its @deps header says `consumed_by: app/handlers/gallery_handlers.py` (line 4). The handler does not import it (gallery_handlers.py:35-37). Contradiction B26.

1.7 app/handlers/gallery_handlers.py (`define_server`, :40)
- Role: reactive wiring. Select-all trackers (:73-91, one per axis from `display_axes`), tick trackers (:93-106), `_visible` (:109-112), `_current_rid` (:114-130: dropdown value, else the kept one, else first), `_track_selection` (:132-139), `_gallery_active_metadata` (:141-146).
- Outputs (renders): `gallery_preview_img` (:148-180; reads `preview_plot.png` next to the index path, :165-170), `gallery_static_data` (:182-201; reads `example_data.tsv` with a plain `pl.read_csv`, :193-197), `gallery_yaml_preview` (:203-216; raw recipe text, :213-215), `gallery_md_content` (:218-233; `example_meta.md` through `ui.markdown`, :229-232), `_update_gallery_options` on Apply (:235-268), `gallery_left_out_notice` (:270-287), `gallery_browser_anchor` (:289-293, returns None).
- Inputs: input ids `gallery_example_select`, `gallery_filter_<axis>`, `gallery_all_<axis>`, `btn_apply_gallery_filters`; the state.
- Callers: server.py:264-271, only when `bootloader.is_enabled("gallery_enabled")`.

1.8 app/modules/gallery_listing.py (exists; pure, no Shiny)
- Role: turns the stored index plus the rejected list into the listing: `build_listing` (:40-56), `read_listing` (:59-69; a missing or unreadable index gives an empty listing), `FILTER_AXES` (:73), `APPLY_RULE_TEXT` (:76), `NO_MATCH_TEXT` (:77-78), `matching_examples` (:81-97, AND across groups, OR within a group, sorted by name at :97), `external_links_new_tab` (:104-118).
- Inputs: index JSON, rejected dict, status string. Output: `GalleryListing(registry, pivot, notice)`.
- Callers: gallery_viewer.py:11; gallery_handlers.py:35-36; app/tests/test_gallery_listing.py; test_gallery_texts_and_links.py:7.

1.9 assets/scripts/refresh_gallery.py (CLI)
- Role: check every example and, with `--apply`, write the index (`main` :28-53; check at :43-44, rebuild at :37-41; exit 0, 1 if any rejected, 2 if folder missing).
- Inputs: `--gallery` (default assets/gallery_data), `--apply`. Output: console report, `gallery_index.json` with apply.
- Callers: a person, from the CLI; app/tests/test_gallery_full_check.py:27 and :110-121. Also named in .claude/rules/rules_gallery_standards.md:108 and libs/viz_gallery/README.md:19.

1.10 assets/scripts/gallery_previews.py (CLI)
- Role: draws each example through the app path (`render_example`) and compares it pixel by pixel with the committed `preview_plot.png` (`compare` :83-100; `run` :109-141). With `--apply` it writes the new picture (and `preview_thumb.png`) only if the content is unchanged, or with `--changed`.
- Inputs: `--gallery`, `--only`, `--apply`, `--changed`, `--out` (default tmpAI/gallery_previews). Output: verdict table; pictures in `--out`; with apply, the files in the example folders (:134-139).
- Callers: a person, from the CLI; app/tests/test_gallery_app_path.py:27-30 (loads the module).

1.11 assets/scripts/convert_gallery_examples.py (CLI)
- Role: converts the old compact form to the standard recipe (`convert_bundle` :124-180), writes the tag strip into `example_meta.md` (:168-180) for converted and standard examples. The `info.description` is copied from the `### Suitability` paragraph (:149, function `suitability` :61-73).
- Callers: a person; app/tests/test_convert_gallery_examples.py; the hint text in gallery_manager.py:43 and :80.

1.12 libs/viz_gallery/assets/: only `__pycache__` files remain (`generate_previews.cpython-314.pyc`, `refresh_gallery.cpython-314.pyc`). No source file exists there (Glob). Stale bytecode.

1.13 app/src/www/gallery_select_all.js (page script)
- Role: the "Select all" box ticks or clears its group in the page (:17-26). Contract in its header (:10-11): box `gallery_all_<axis>`, boxes `gallery_filter_<axis>`.
- Inputs: DOM change events. Outputs: checked state and one change event to the server.
- Loaded by app/src/ui.py:85-89 (only when `gallery_enabled`), included at ui.py:107.

1.14 Gallery check at start
- bootloader.py:197-199 (call), :226-231 (runs only if `gallery_enabled`), :233-244 (`_check_gallery_examples`: calls `check_gallery_at_start`, sets `gallery_index_status` and `rejected_gallery_examples`, prints each reason :243-244). An exception sets status "failed" (:238-241).
- Profile `gallery` of the checker: libs/utils/src/utils/recipe_check.py:224-225 (`self.gallery(raw)`), :1249-1282 (GP01 to GP06). Per file: `check_recipe_file` (recipe_loader.py:113-126) from gallery_manager.py:85.

1.15 Sidebar registry panels
- app/modules/sidebar_registry.py:63-66 `gallery_main` (gate `gallery_enabled`, label "Gallery Explorer"); :87-90 `gallery_right_info` (same gate and label).
- Config: config/ui/sidebars/gallery_focus_left.yaml:4 lists `gallery_main`; config/ui/sidebars/gallery_focus_right.yaml:3 lists `gallery_right_info`.
- Renderers in app/handlers/home_theater.py: `gallery_main` at :2014-2029 (calls `gallery_viewer.build_sidebar_ui(gallery_state.get())`, isolated); `gallery_right_info` at :2194-2204 (static card: "Browse visual examples ... copy the recipe text by hand"); registry map :2270; left build :2087-2088; right build :2310-2312.
- Gate: `gallery_enabled` is true in config/app_features/developer.yaml:9, qa.yaml:23, standalone.yaml:11; false in demo-vetinst.yaml:9, pipeline-exploration-advanced.yaml:9, pipeline-exploration-simple.yaml:9, pipeline-static.yaml:10, web-demo.yaml:9. Nav item: home_theater.py:1796-1797.

1.16 Help page: app/src/help/gallery.md. Mapped at app/handlers/home_theater.py:1852 ("Gallery": "gallery.md"), shown by the workspace help button (:1845-1859). The page text matches the screen (Select an Example, the three tabs, the Apply rule, ADR-093 wording).

1.17 "gallery" location key: config/deployment/*.yaml (e.g. demo/demo-vetinst.yaml:14 `assets/gallery_data/`; templates/deployment_template.yaml:76 `gallery/`). Required at bootloader.py:342. Index paths depend on it (see B-G8).

1.18 Server wiring: server.py:128-129 (`gallery_refresh_trigger`, `gallery_state`), :210-211 (passed to home_theater), :264-271 (handlers).

-------------------------------------------------------------------
2. ONE BUNDLE: assets/gallery_data/bar_simple/ (verified: all 34 folders have the same five files: data_analysis_recipe.yaml, example_data.tsv, example_meta.md, preview_plot.png, preview_thumb.png; example_template.md sits at the root of gallery_data and is not an example, because `list_submissions` takes folders only, gallery_manager.py:61-63)

2.1 data_analysis_recipe.yaml (bar_simple), field by field
- L1 `id: bar_simple`. Read by: checker GP04 (recipe_check.py:1255-1256), T05 (:243-244). Loader keys the copy by file name (gallery_examples.py:78) [R]. Shown: no.
- L2-4 `spec_version`, `data_engine`, `plot_engine`. Read by: checker (:246-262). Preview engine: gallery_examples.py:119 [R for engine lookup]. Shown: no.
- L6 `info.label: Bar Simple`. Read by: gallery_manager.py:107 (name), checker I01 required (recipe_check.py:315-316). Shown: dropdown and selected name, the "dropped" note (see §3).
- L7-9 `info.description` (folded). Read by: checker advice I02 only (:319-321). Shown: no (raw YAML tab only).
- L10 `info.submission_date: '2026-04-10'`. Written by example_recipe.py:106-107. Read at runtime by nothing (grep). Shown: raw YAML tab only.
- L13-15 schema `label`, `description`. Schema description: advice S04 if missing (recipe_check.py:392); written by example_recipe.py:110. Read at runtime by nothing. Shown: YAML tab only.
- L16 `source: {type: local_tsv, path: ./assets/gallery_data/bar_simple/example_data.tsv}`. Read by: checker GP06 (recipe_check.py:1270-1277), loader for the picture [R] (gallery_examples.py:82, :92). The viewer does NOT read this path; it reads the TSV next to the index path (gallery_handlers.py:193).
- L17 `null_values: []`, L18 `strip: true`. Read by: loader for the picture [R]; not by the Data Sample tab (gallery_handlers.py:197). Shown: no.
- L19-23 `input_fields` (id, species, amr_class, value). Read by: checker schema part [R]; loader typing [R]; test app/tests/test_gallery_app_path.py:43-46 compares the contract table with a plain read. Shown: YAML tab only.
- L24 `tier1: {steps: []}`. Read by the loader for the picture [R] (gallery_examples.py:92). Shown: no.
- L25-26 `plot_defaults: theme: theme_bw`. Read by the engine for the picture [R]. Shown: picture only.
- L30 group `ui_label: Example`. Required by checker G01 (recipe_check.py:1101-1102). Read by nothing in gallery. Shown: no.
- L31 group `description`. Advice G02 (:1103-1104). Read by nothing. Shown: no.
- L34 plot `ui_label: Bar Simple`. Required by checker P01 (recipe_check.py:1126-1127). READ BY NO GALLERY CODE. This is the owner's name field (D-0387). Shown: no.
- L35-36 plot `description: Drawn with geom_bar; fill is amr_class, x is species.` Advice P02 (:1128-1129). The plot library ignores entry keys (libs/utils/src/utils/recipe_spec.yaml:55-57). Read by nothing in gallery. Shown: no.
- L37 plot `taxonomy: {family: Ranking, pattern: '1 Numeric, 1 Categorical', difficulty: Simple, show: ranking, sample_size: any}`. Read by: taxonomy.py:55-65 via gallery_manager.py:105; checker GP02/GP03 (recipe_check.py:1257-1269); writer example_recipe.py:125. Index: registry `taxonomy` and `pivot` (gallery_manager.py:111-114). Shown: sidebar checkboxes (gallery_viewer.py:127-152, labels and order from taxonomy.py:95-109) and filtering (gallery_listing.py:81-97).
- Derived `geom` = first `geom_*`/`stat_*` layer, from L41 `geom_bar`: taxonomy.py:33-40 (called at :64). Index: `taxonomy.geom`, `pivot.by_geom`. Shown: "Primary Geom" filter.
- L38 `target_dataset: example`. Checker PS02 (recipe_check.py:1146-1147); preview reads it (gallery_examples.py:91). Shown: no.
- L39 `mapping: {fill: amr_class, x: species}`. Checker PS03 (:1148-1149), PS06 (:1156-1159). Picture: engine [R]. Shown: no.
- L40-41 `layers: - {name: geom_bar, params: {}}`. Checker PS04 (:1168-1196), geom presence PS03 (:1215-1216). first_geom (taxonomy.py:33-40). Picture: engine [R]. Shown: picture and geom filter.
- No `tier2`, `tier3`, `ui_title`, `comment`, `contact`, `subtitle` in this bundle; none of the 34 has `ui_title`, `contact`, `subtitle`, `version` or `comment` (grep over assets/gallery_data returned no matches).

2.2 example_meta.md (bar_simple)
- L1 `## Bar Chart`. Read by: gallery_handlers.py:229-232 (through ui.markdown; shown as the H2 of the guidance pane, styled by config/ui/theme.css:651). No code parses it as a name. Read by tests: test_gallery_examples_are_recipes.py:71-72 (strip only), test_gallery_texts_and_links.py:24-34 (links).
- L3 the blockquote tag strip (six fields with icons: family, pattern, difficulty, geom, show, sample size). Read by: displayed as a blockquote (theme.css:658). Parsed by code? NO: no runtime code reads it. It is written by taxonomy.py:68-70 / :73-92 (with_tag_strip) at submit (gallery_manager.py:203) and convert (convert_gallery_examples.py:168-180), and checked only by the test test_gallery_examples_are_recipes.py:67-72. Its position is "the first `>` line after the first `## ` heading" (taxonomy.py:76-91).
- L5 `### Suitability` (+ L6 paragraph). Read by: convert_gallery_examples.py:61-73 (used once, to fill info.description). Shown: guidance pane.
- L8 `### Data Schema (Tier 1)`, L9 bullet naming the TSV headers. Shown: guidance pane. Not read by code.
- L11 `### Transformation Logic (Tier 2)`, L12. Shown only.
- L15 `### Inspiration & Resources`, L16 external link to r-graph-gallery.com. Shown; external links open in a new tab (gallery_listing.py:104-118).
- L18 `### Interpretations`, L19. Shown only.

2.3 example_data.tsv
- Read by: Data Sample tab, `pl.read_csv(separator="\t")` with no contract (gallery_handlers.py:193-197); the picture, through the recipe source path (gallery_examples.py:82, :92) [R]; GP05 presence (recipe_check.py:1278-1282); writers gallery_manager.py:189, example_recipe.py:39-82. Row counts: 34 files, 100 data rows in 10 of them, 200 in ridgeline_advanced; every count equals the recipe's `data_schemas.example.description` sentence (checked, all 34). Column lists in those sentences equal the `input_fields` names (checked, all 34).

2.4 preview_plot.png and preview_thumb.png
- preview_plot.png: read by gallery_handlers.py:165-170 (base64 into the "Plot Preview" tab); flag `has_preview` written at gallery_manager.py:109 and read by nothing (grep); compared by gallery_previews.py:131, :63-64; existence checked by GP05 (recipe_check.py:1278-1282). The viewer does not re-render.
- preview_thumb.png: written by gallery_previews.py:137-138; flag `has_thumb` at gallery_manager.py:110, read by nothing; not in the companion list (libs/utils/src/utils/recipe_spec.yaml:215); shown nowhere.

2.5 gallery_index.json (structure, verified at the file, lines 1-812)
- Top: `metadata` {generated_at "2026-11-15 13:11:10" (:3), count 34 (:4), coverage ["actions","components","structure"] (:5-9), rejected {} (:10)}; `registry` (:12); `pivot` (:490).
- `registry.<folder>` = {name, path, has_preview, has_thumb, taxonomy{family, pattern, difficulty, geom, show, sample_size}}. Example: bar_simple at :55-68. `path` is the relative string `assets/gallery_data/<id>/data_analysis_recipe.yaml`.
- `pivot.by_<axis>` = {term: [folder ids]} for axes family (:491), pattern (:539), difficulty (:595), geom (:637), show (:713), sample_size (:767). Ids are in folder order (gallery_manager.py:63, :75).
- Writer: gallery_manager.py:115-124 (dict), :125-134 (atomic write). Fields come from: name = info.label (:107); path = folder/recipe (:108); flags = file existence (:109-110); taxonomy = example_taxonomy (:105, :111); pivot = display axes (:102, :113-114); metadata: generated_at (:117), count (:118), coverage (:119), rejected (:120). Writer invoked by refresh_gallery.py (via gallery_examples.rebuild_gallery_index) and sync_index (gallery_manager.py:157) at start.
- Readers: gallery_listing.read_listing (:59-69) via gallery_viewer.py:66-69 and gallery_handlers.py:58-61 (registry names, paths, pivot); gallery_manager.sync_index (:151-152: compares registry key set and `metadata.rejected` only); refresh_gallery.py:41 (apply report: coverage); tests (test_gallery_full_check.py:90-107, test_gallery_bundle.py:201, :204, :249).
- Not read by runtime code: generated_at, count (tests only), has_preview, has_thumb, registry.taxonomy (tests only), metadata.rejected (the viewer uses bootloader.rejected_gallery_examples instead: gallery_viewer.py:68-69).

-------------------------------------------------------------------
3. NAMES. Every place a name is shown, with its source field
- Dropdown items and selected name: `registry[id].name` = `info.label` (gallery_manager.py:107) -> matching_examples (gallery_listing.py:97) -> choices (gallery_viewer.py:119-124; gallery_handlers.py:261-265, update_select with the dict).
- Dropdown label text "Visual Gallery (N matched)" or "Select an Example": a count, not a name (gallery_viewer.py:112-113; gallery_handlers.py:262-263).
- "dropped" note: `"<name>" does not match the ticked filters` uses `registry[...]["name"]` (gallery_handlers.py:258 and :157-158).
- Guidance pane heading: the `##` line of example_meta.md, rendered as an H2 (gallery_handlers.py:229-232; theme.css:651). Not the info.label.
- YAML tab: the raw text, so `info.label` and the plot `ui_label` appear as written (gallery_handlers.py:213-215).
- Left-out notice: the FOLDER name and the first reason (gallery_listing.py:51), not the label. Bootloader prints folder names too (bootloader.py:244).
- Preview picture: a title drawn inside the PNG when the recipe has a `labs` title (16 recipes: e.g. area_simple/data_analysis_recipe.yaml:39, and beeswarm_sina, bar_grouped:44, bar_horizontal:42, connected_scatter:45, density_2d_bin:43, dumbbell:45, ecdf:43, error_bar:45, freqpoly:42, line_simple:40, qq_plot:45, scatter_smooth:45, stacked_area:44, step_chart:45, violin_boxplot:43). This is a fourth name source. Its text is from the `labs` layer, not from any name field.
- Banner "Gallery Inspiration" is static (gallery_viewer.py:168). Filter labels come from the specification (taxonomy.py:108; recipe_spec.yaml:208-214).
- The owner's rule (D-0387, ledger:421): index and dropdown show plot `ui_label`. Not built; code reads info.label. Heading: "probably part of the markdown preview ... I do not think it is redundant" (Eve's words, ledger:421).

NAME TABLE (all 34; info.label at recipe line 6 in every file; plot ui_label line as given; heading is line 1 of example_meta.md)
folder | info.label | plot ui_label (line) | `##` heading | differs?
area_simple | Area Chart | Area Chart (29) | Area Chart | no
bar_grouped | Grouped Bar Chart | (33) same | Grouped Bar Chart | no
bar_horizontal | Horizontal Bar Chart | (29) same | Horizontal Bar Chart | no
bar_simple | Bar Simple | (34) same | Bar Chart | HEADING
beeswarm_sina | Beeswarm / Sina Plot | (32) same | Beeswarm / Sina Plot | no
boxplot_faceted | Boxplot Faceted | (33) same | Faceted Boxplot | HEADING
boxplot_simple | Boxplot Simple | (33) same | Boxplot | HEADING
bubble | Bubble Chart | (32) same | Bubble Chart | no
connected_scatter | Connected Scatter Plot | (34) same | Connected Scatter Plot | no
density_2d_bin | 2D Bin Density | (33) same | 2D Bin Density | no
density_simple | Density Simple | (32) same | Density Plot | HEADING
dumbbell | Dumbbell Chart | (33) same | Dumbbell Chart | no
ecdf | ECDF Plot | (32) same | ECDF Plot | no
error_bar | Error Bar / Point Range | (34) same | Error Bar / Point Range | no
freqpoly | Frequency Polygon | (32) same | Frequency Polygon | no
heatmap_correlation | Heatmap Correlation | (30) same | Correlation Matrix (Heatmap) | HEADING
histogram_simple | Histogram Simple | (32) same | Histogram | HEADING
jitter_strip | Jitter Strip Plot | (31) same | Jitter Strip Plot | no
line_grouped | Line Chart (Grouped) | (30) same | Line Chart (Grouped) | no
line_simple | Line Chart (Simple) | (30) same | Line Chart (Simple) | no
lollipop_advanced | Lollipop Advanced | (31) same | Lollipop Chart | HEADING
point_faceted | Point Faceted | (34) same | Faceted Scatter | HEADING
point_simple | Point Simple | (33) same | Scatter Plot | HEADING
proportion_bar | Proportion Bar Chart | (31) same | Proportion Bar Chart | no
qq_plot | Q-Q Plot (Quantile-Quantile) | (33) same | same | no
ridgeline_advanced | Ridgeline Advanced | (30) same | Ridgeline Distribution | HEADING
scatter_smooth | Scatter Plot with Smoother | (33) same | same | no
stacked_area | Stacked Area Chart | (33) same | same | no
stacked_bar | Stacked Bar Chart | (30) same | same | no
step_chart | Step Chart | (34) same | same | no
tile_simple | Tile Simple | (33) same | Heatmap (Tile) | HEADING
violin_boxplot | Violin + Boxplot Overlay | (32) same | same | no
violin_faceted | Violin Faceted | (33) same | Faceted Violin | HEADING
violin_simple | Violin Simple | (32) same | Violin Plot | HEADING

Where two fields differ: info.label vs plot ui_label: none (34 of 34 equal). Name vs `##` heading: 13 differ (marked). The index name equals info.label for all 34 (verified against gallery_index.json registry, names at lines 14-483).

Confirmation of the owner's point: the code reads `recipe["info"]["label"]` (gallery_manager.py:107). Confirmed.

-------------------------------------------------------------------
4. TAXONOMY

4.1 Cheatsheet (assets/gallery_data/TAXONOMY_CHEATSHEET.md)
- Axes and allowed values: family 6 (:25-30); pattern 10 (:35-44); difficulty 3 (:49-51); geom list 20 names (:56-59); show 9 (:64-72); sample_size 4 (:77-80).
- Sidebar labels (:11-16): "Family (Purpose)", "Data Pattern", "Difficulty", "Primary Geom", "What it Shows", "Sample Size", with the six icons. The filter labels are the same text (recipe_spec.yaml:209-214 display; taxonomy.py:108 builds icon + label).
- The spec terms (recipe_spec.yaml:191-205) are identical to the cheatsheet values for family, pattern, difficulty, show and sample_size. Icons compared as displayed; byte identity not checked (C7).
- Old format in the cheatsheet: "Where used" column says `info.family`, `info.pattern`, `info.difficulty`, `info.geom`, `info.show`, `info.sample_size` (:11-16); the info block example (:103-115) uses `name:` and `info:`. These are the old form (see B4).
- Tag strip rule (:84-86): line 3, after the `## Name` heading and a blank line. Matches all 34 files (line 3 in each).
- Cheatsheet read by code: none (grep over app, libs, assets, config). Mentioned only in a docstring (app/tests/test_gallery_viewer_taxonomy.py:4) and libs/viz_factory/README.md:294.

4.2 Where each value comes from
- Five typed axes: the recipe `analysis_groups.*.plots.*.taxonomy` (example_recipe.py:125 writes them; taxonomy.py:61-64 reads them).
- geom: not typed. Derived by taxonomy.py:33-40 (`first_geom`: the first layer whose `name` starts with `geom_` or `stat_`), used at taxonomy.py:64; also in example_recipe.py:89 and convert_gallery_examples.py:164. A typed `geom` key is refused by the checker as "not an axis" (recipe_check.py:1267-1269).
- Term check: recipe_check.py:1262-1266 loops the five axes in recipe_spec.yaml:189. The geom list is not in the spec; geom is open ("an open list: every registered geom is a possible value", taxonomy.py:98-101).

4.3 Per example (taxonomy line in the recipe; first geom line; all values checked against the cheatsheet; the tag strip in example_meta.md line 3 compared term by term)
folder | tax. line | family | pattern | difficulty | show | sample_size | geom (line) | strip = taxonomy?
area_simple | 32 | Evolution | 1 Year, 1 Numeric | Simple | trend | medium+ | geom_area (36) | yes
bar_grouped | 36-37 | Ranking | 1 Numeric, 2 Categorical | Intermediate | ranking | any | geom_col (41) | yes
bar_horizontal | 32 | Ranking | 1 Numeric, 1 Categorical | Simple | ranking | any | geom_col (36) | yes
bar_simple | 37 | Ranking | 1 Numeric, 1 Categorical | Simple | ranking | any | geom_bar (41) | yes
beeswarm_sina | 35-36 | Distribution | 1 Numeric, 1 Categorical | Intermediate | distribution | individual points | geom_sina (40) | yes
boxplot_faceted | 36-37 | Comparison | 1 Numeric, 2 Categorical (Faceted) | Intermediate | distribution | medium+ | geom_boxplot (41) | yes
boxplot_simple | 36-37 | Distribution | 1 Numeric, 1 Categorical | Simple | distribution | medium+ | geom_boxplot (41) | yes
bubble | 35-36 | Correlation | 2 Numeric, 1 Categorical | Intermediate | relationship | any | geom_point (40) | yes
connected_scatter | 37 | Correlation | 2 Numeric | Intermediate | trend | any | geom_path (41) | yes
density_2d_bin | 36 | Correlation | 2 Numeric | Intermediate | relationship | large | geom_bin_2d (40) | yes
density_simple | 35 | Distribution | 1 Numeric | Simple | distribution | medium+ | geom_density (39) | yes
dumbbell | 36-37 | Comparison | 1 Numeric, 2 Categorical | Intermediate | change | any | geom_line (41) | yes
ecdf | 35-36 | Distribution | 1 Numeric, 1 Categorical | Intermediate | distribution | medium+ | stat_ecdf (40) | yes
error_bar | 37-38 | Comparison | 1 Numeric, 1 Categorical | Intermediate | uncertainty | any | geom_pointrange (42) | yes
freqpoly | 35-36 | Distribution | 1 Numeric, 1 Categorical | Simple | frequency | medium+ | geom_freqpoly (40) | yes
heatmap_correlation | 33 | Correlation | 3 Numeric (Matrix) | Advanced | relationship | any | geom_tile (37) | yes
histogram_simple | 35 | Distribution | 1 Numeric | Simple | frequency | medium+ | geom_histogram (39) | yes
jitter_strip | 34-35 | Comparison | 1 Numeric, 1 Categorical | Simple | distribution | individual points | geom_jitter (39) | yes
line_grouped | 33-34 | Evolution | 1 Year, 1 Numeric, 1 Categorical | Intermediate | trend | medium+ | geom_line (38) | yes
line_simple | 33 | Evolution | 1 Year, 1 Numeric | Simple | trend | medium+ | geom_line (37) | yes
lollipop_advanced | 34-35 | Ranking | 1 Numeric, 1 Categorical | Intermediate | ranking | any | geom_segment (39) | yes
point_faceted | 37-38 | Comparison | 2 Numeric, 1 Categorical (Faceted) | Intermediate | relationship | individual points | geom_point (42) | yes
point_simple | 36-37 | Correlation | 2 Numeric | Simple | relationship | individual points | geom_point (41) | yes
proportion_bar | 34-35 | Part-to-Whole | 1 Numeric, 2 Categorical | Intermediate | proportion | any | geom_col (39) | yes
qq_plot | 36-37 | Distribution | 1 Numeric, 1 Categorical | Advanced | normality | medium+ | geom_qq (41) | yes
ridgeline_advanced | 33-34 | Distribution | 1 Numeric, 1 Categorical | Advanced | distribution | medium+ | geom_density (38) | yes
scatter_smooth | 36-37 | Correlation | 2 Numeric, 1 Categorical | Simple | relationship | individual points | geom_point (41) | yes
stacked_area | 36-37 | Evolution | 1 Numeric, 2 Categorical | Intermediate | proportion | medium+ | geom_area (41) | yes
stacked_bar | 33-34 | Part-to-Whole | 1 Numeric, 2 Categorical | Intermediate | proportion | any | geom_col (38) | yes
step_chart | 37 | Evolution | 1 Numeric, 1 Categorical | Simple | trend | any | geom_step (41) | yes
tile_simple | 36-37 | Correlation | 1 Numeric, 2 Categorical | Simple | relationship | any | geom_tile (41) | yes
violin_boxplot | 35-36 | Distribution | 1 Numeric, 1 Categorical | Intermediate | distribution | medium+ | geom_violin (40) | yes
violin_faceted | 36-37 | Comparison | 1 Numeric, 2 Categorical (Faceted) | Intermediate | distribution | medium+ | geom_violin (41) | yes
violin_simple | 35-36 | Distribution | 1 Numeric, 1 Categorical | Simple | distribution | medium+ | geom_violin (40) | yes

The index taxonomy of each entry equals this table (checked for all 34).

4.4 Checks requested
(i) Values not in the cheatsheet: NONE. All 34 typed values are cheatsheet terms; all 20 derived geoms are in the cheatsheet geom list (geom_area, geom_col, geom_bar, geom_sina, geom_boxplot, geom_point, geom_path, geom_bin_2d, geom_density, geom_line, stat_ecdf, geom_pointrange, geom_freqpoly, geom_tile, geom_histogram, geom_jitter, geom_segment, geom_qq, geom_step, geom_violin).
(ii) Disagreements between recipe taxonomy and the tag strip: NONE for all 34 (six fields each, icons in the same order as taxonomy.py:70 and spec display order).
(iii) Renamed term names in the recipe refactor: none found. Keys are the same in cheatsheet and recipes (family, pattern, difficulty, show, sample_size) and the derived geom. Old fallback term "Numeric-Numeric" is gone (app/tests/test_gallery_viewer_taxonomy.py:27 asserts it is absent; recipe_format_spec.md:561 names it). A typed `geom` key is now an error (recipe_check.py:1267-1269).
(iv) git log of the cheatsheet: not run (no shell).

