# Gallery examples as standard recipes: what must change, options, pros and cons (2026-11-13)

**Written for:** Eve, to choose. Companion of `recipe_format_spec.md` (its section 6.9 is **withdrawn** until you choose here).
**Status:** proposal. Nothing in the gallery, the recipes or the code was changed. Evidence labels: **verified** (read at file:line or run), **reasoned**, **proposal**.

## 0. In short

You asked that the gallery follows the same specification as every recipe, is checked by the same code as the app (one source of truth), and that its special needs become part of the spec. Investigated, it works:

- **Verified by running** (`tmpAI/recipe_format/gallery_poc.py`, scratch): all **34** examples written as standard recipes build and render through the app's own path (ConfigManager, DataOrchestrator, VizFactory, the call HOME makes). 22 previews are pixel-identical. 10 differ only because the committed picture is 800x600 and today's size is 960x600. 2 differ by 0.9 % and 2.6 % of the pixels (jitter, reasoned). No example errors. The taxonomy of all 34 is already inside the cheat sheet.
- **What is wrong today** (section 3): the taxonomy terms are copied in five places and have drifted; the previews come from a special path that is not the app's; the example file is never validated as a recipe; one bundle declares a geom that its plot does not use; the submission code is dead.
- **Recommended design** (one line each, options in section 5):
  1. an example **is** a standard recipe (one data schema, one group, one plot) checked by `check_recipe` in a `gallery` profile (more rules, same format);
  2. the classification is one optional key of the plot, **`taxonomy:`** (`family`, `pattern`, `difficulty`, `show`, `sample_size`); `geom` is not typed, it is **derived** from the first geom layer;
  3. the allowed terms live in **one dictionary file** (`gallery_terms.yaml`) that the checker, the filter panels, the index and the cheat sheet all read: your "dictionary specific for the gallery terms for the selectors";
  4. the same check runs at index rebuild, at app start (like HOME's load gate) and in the tests;
  5. previews are produced by the app's own path;
  6. `example_meta.md` stays as the teaching text; its tag strip is generated from `taxonomy`.
- **Effort:** about 10 packages (section 7). It is a real change, not a rename, mostly mechanical for the 34 files.
- **What I need:** your choice on the six decisions of section 5 (my recommendation is the first option of each) and the name `taxonomy`.

## 1. What I read and ran

`gallery_manager.py` (all), `gallery_viewer.py` (all), `gallery_handlers.py` (taxonomy part), `generate_previews.py`, `TAXONOMY_CHEATSHEET.md`, `rules_gallery_standards.md`, `spaces/GALLERY.md`, `plot_authoring_model.md` (ADR-083), ADR-033/035/037/061/063/093 (headings), the 34 bundles, `gallery_index.json`, both shipped deployments, the gallery tests; and I ran the proof of concept above.

## 2. How the gallery works today

| Part | What it does | Where |
|---|---|---|
| A bundle | folder with `data_analysis_recipe.yaml`, `example_data.tsv`, `example_meta.md`, `preview_plot.png`, `preview_thumb.png` | `assets/gallery_data/<id>/` (34 bundles) |
| The bundle's YAML | `info` (name, submission date, six taxonomy values), `data_path`, `plots` (one plot body), `wrangling` (tier1, tier2, optional tier3). It is the plot engine's own input shape, not a recipe | `bar_simple/data_analysis_recipe.yaml` |
| The index | `gallery_index.json`: a registry (name, taxonomy, flags) and a pivot (value to list of examples). Rebuilt from the bundles; a bundle without the three required files is skipped | `gallery_manager.py:86-188` |
| The viewer | filter panels (six axes, icons, labels), example list, tabs Plot / Data / YAML, guidance pane | `gallery_viewer.py`, `gallery_handlers.py` |
| The YAML tab | shows the **whole file as text**; the user copies it by hand (ADR-093) | `gallery_handlers.py:210-221` |
| Previews | offline script: reads the bundle's YAML as a dict, reads `example_data.tsv` with Polars, calls `VizFactory.render(df, dict, plot_id)`, saves 960x600 and a thumbnail | `libs/viz_gallery/assets/generate_previews.py:36-67` |
| Adding an example | `GalleryManager.submit_example(...)` (a library function; no screen calls it). The banner says "send us a request" | `gallery_manager.py:28-80` |
| Constraints | static reference (ADR-093): no run in the app, no handoff to HOME or BLUEPRINT; works offline; mounted only if `gallery_enabled` (ADR-071); the gallery folder is a deployment location (`gallery: assets/gallery_data/` in both shipped deployments) | `GALLERY.md`, `rules_ui_dashboard.md` 5 |

## 3. What is wrong or fragile today

| # | Finding | Evidence |
|---|---|---|
| G1 | The **terms are copied in five places**: the cheat sheet, the viewer's fallback lists, the handler's fallback lists, the bundles, and the icons and labels written inside the UI strings. The copies disagree: both fallback lists contain a pattern "Numeric-Numeric" that the cheat sheet does not allow, and lack 4 of its 10 patterns (`2 Numeric, 1 Categorical`, `3 Numeric (Matrix)`, `1 Year, 1 Numeric`, `1 Year, 1 Numeric, 1 Categorical`). The difficulty and sample-size orders are written twice more | verified: `gallery_viewer.py:167-195`, `gallery_handlers.py:72-89`, cheat sheet |
| G2 | The **previews do not come from the app's path.** The script hands the bundle's own dict to the renderer. An example that the app could not load would still get a picture | verified: `generate_previews.py:47-55` |
| G3 | The **example file is never validated as a recipe**; only its `info` is read, by the index. `data_path` is read by nobody (the code uses the fixed name `example_data.tsv`); `wrangling` is only shown, never run | verified: `gallery_manager.py:130-168`, `gallery_handlers.py:198` |
| G4 | **One declared value disagrees with the plot**: `dumbbell` says `geom: geom_segment` and draws `geom_line` and `geom_point` | verified |
| G5 | **10 of 34 committed previews are 800x600**, the other 24 are 960x600 (two generator settings over time) | verified |
| G6 | **Dead submission code**: `submission_modal_ui`, `autofill_meta_from_audit` and the button `btn_confirm_submission` have no handler; `GALLERY.md` says so | verified: grep |
| G7 | The **tag strip** in each `example_meta.md` repeats the taxonomy; the rule says it must match, nothing checks it (today all 34 match) | verified by the proof of concept |
| G8 | The taxonomy also travels, by copy, into pipeline plot specs (16 of 17 ST22 plots) through the `_meta` passthrough of ADR-083, where nothing reads it | verified |

## 4. What must not change

ADR-093 (static browser, no handoff, no run at view time), the offline use, `gallery_enabled` and the positive-inclusion rule, the six filter axes and their icons, the index format that the viewer reads, the one-plot-per-example rule, the folder name as the example's id, and `example_data.tsv` and `example_meta.md` as companion files. The gallery stays a *reference*: the new design only changes what the example file is and who checks it.

## 5. Decisions, options, pros and cons

### D1. What is an example file?

| Option | Pros | Cons |
|---|---|---|
| **A. A standard recipe** (id, engines, info, one data schema, one group, one plot) checked in a `gallery` profile **[recommended]** | one format, one checker, one render path; an example is runnable (saved to a file and imported in Blueprint it works, with no change); the examples demonstrate good practice (labels, descriptions, types); the 34 examples become a regression suite for the whole plot path; a later "start a recipe from this example" (GALLERY.md, open question) needs nothing new | the file is longer (about 35 to 60 lines against 25); 34 files to rewrite (scripted and reviewed); the data path is a project-root path like in every recipe, so a deployment that moves the gallery folder can browse but not run the example |
| B. Keep the compact shape and only add checks (my v0.2) | smallest change | **two formats** (your objection); the example is still not a recipe; the special render path stays |
| C. Keep the compact shape as the source and generate a standard recipe from it | the source stays short | two sources and a generated file in git; drift between them; more tools |

### D2. Where does the classification live?

| Option | Pros | Cons |
|---|---|---|
| **A. `taxonomy:` on the plot entry** (`family`, `pattern`, `difficulty`, `show`, `sample_size`) **[recommended]** | the classification describes a plot; fits one plot per example; **any recipe's plot may carry it**, so a plot can be offered to the Gallery without retyping; the plot spec stays pure grammar (the boundary with Blueprint); replaces the `_meta` passthrough of ADR-083 (which becomes unnecessary) | one gallery word in the common spec (one optional key, checked against the dictionary when present); Blueprint's save must keep the entry's keys (to check in `group_plot_manager`) |
| B. `info.taxonomy` in the recipe's free-form `info` | no new key | `info` is free-form, so the check would be a special case; wrong level when a recipe has several plots |
| C. A sidecar file `taxonomy.yaml` in the bundle | the recipe has no gallery word at all | a second file and format to specify and keep consistent; a recipe plot offered later needs a new file; the loader cannot check it |
| D. Inside the plot spec, as ADR-083 does with `_meta` | follows ADR-083 | the spec stops being pure grammar; an exception in the checker; the audit/Blueprint boundary blurs |

### D3. The terms: one dictionary

| Option | Pros | Cons |
|---|---|---|
| **A. One machine-readable file `assets/gallery_data/gallery_terms.yaml`** **[recommended]**: for each axis its label, icon, ordered terms, one line of meaning | the checker, the filter panels, the index order, the cheat sheet (generated) and the tag strip all read the same file; adding a term is one line; fixes G1 | one more file; the viewer builds its panels from it (a loop instead of six hand-written panels) |
| B. Keep the markdown cheat sheet and the lists in code | nothing to build | the five copies and the drift of G1 |
| C. A dictionary per deployment (`config/`) | an institute can use its own terms | the shipped examples would have to match every institute's dictionary; over-built for now. A already isolates the file, so C can be added later |

Declared axes: `family`, `pattern`, `difficulty`, `show`, `sample_size`. **`geom` is derived** from the first `geom_*` or `stat_*` layer (it cannot disagree with the plot, G4 disappears) and is added to the index and the filter. `[proposal]`

### D4. Where is an example checked? (one source of truth)

| Option | Pros | Cons |
|---|---|---|
| **A. The same `check_recipe` (profile `gallery`) at index rebuild, at app start and in the tests** **[recommended]** | a broken example is caught wherever it enters; at app start it works like HOME's load gate (ADR-094): the example is left out of the list and the reason is shown; the data-and-render check runs offline where the previews are made | a small start-up cost (34 small files, no data read); a few lines in the Bootloader |
| B. Offline and tests only | no change at start | a broken example can reach users if the tests are skipped |
| C. At app start only | users are protected | nobody sees the error while adding an example |

Layering `[reasoned]`: `libs/viz_gallery` may import `utils` (Tier 1) where `check_recipe` lives, but not `transformer` or `viz_factory` (peers); the catalogues of actions and plot components are handed in by the caller (the script or the app), as for HOME.

### D5. How are previews made?

| Option | Pros | Cons |
|---|---|---|
| **A. By the app's own path**, in a Tier-3 script under `assets/scripts/` **[recommended]** | a preview proves that the example runs in the app; same seed rule (ADR-090); one standard size; fixes G2 and G5 | the script depends on app code, so it leaves `libs/viz_gallery/assets/`; the first regeneration changes 12 pictures in git |
| B. Keep the current script and the direct call | nothing moves | a second path; G2 stays |

### D6. `example_meta.md` and its tag strip

| Option | Pros | Cons |
|---|---|---|
| **A. Keep the teaching text; the viewer builds the tag strip from `taxonomy`** (the line is removed from the 34 files) **[recommended]** | nothing to keep equal (G7 disappears) | 34 small edits; the file on disk has no strip when read outside the app |
| B. Keep the hand-written strip and check that it equals `taxonomy` (EX04) | files unchanged | the information stays in two places; a check instead of one source |
| C. Fold the text into `description` or `comment` | one file less | loses the teaching text (suitability, data schema, interpretation) |

### D7 (smaller). The data contract of an example

`input_fields: {}` (no contract, what the proof of concept used) or a contract generated from the file (type from the Polars dtype, label from the column name) and reviewed. **Recommended: generated**, because the gallery should show good practice; verify with the same script that the 34 previews do not change (a numeric column must stay numeric; the generator must not use the `categorical` default for numbers).

## 6. What an example would look like (recommended design; `bar_simple`)

```yaml
id: bar_simple
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: Bar Simple
  description: >-
    Number of records per species, coloured by antimicrobial class: the basic bar chart.
  submission_date: '2026-04-10'            # free-form info key, kept
data_schemas:
  example:
    label: Example data
    description: >-
      One row per record (100 rows): a species, an antimicrobial class and a numeric value.
    source: {type: local_tsv, path: ./assets/gallery_data/bar_simple/example_data.tsv}
    input_fields:
      id: {type: categorical, label: Record}
      species: {type: categorical, label: Species}
      amr_class: {type: categorical, label: Antimicrobial class}
      value: {type: numeric, label: Value}
    wrangling: {tier1: []}
analysis_groups:
  example:
    label: Example
    description: The one plot of this example.
    plots:
      bar_simple:
        label: Bar Simple
        description: Bar count of records per species, filled by antimicrobial class.
        taxonomy: {family: Ranking, pattern: "1 Numeric, 1 Categorical", difficulty: Simple, show: ranking, sample_size: any}
        spec:
          target_dataset: example
          mapping: {x: species, fill: amr_class}
          layers:
            - {name: geom_bar, params: {}}
```

`geom` (`geom_bar`) is not typed: it is read from the first layer. The old `data_path`, `name` and `wrangling.tier3` disappear: the path is in `source`, the name is `label`, and the example's own steps (what `submit_example` wrote into `tier3`) are the plot's `steps: {tier3: [...]}`, which is the same container as in audit mode (ADR-099).

## 7. What changes, and in which order

| # | Change | Size |
|---|---|---|
| 1 | Specification: a `gallery` profile (exactly one group and one plot, `taxonomy` present, `id` equal to the folder name, companion files, taxonomy values in the dictionary), the `taxonomy` key in 6.7, EX checks rewritten | S (part of #76) |
| 2 | `gallery_terms.yaml` and the generated cheat sheet | S |
| 3 | The 34 bundle files rewritten as standard recipes (a script writes them from the old file, I review pictures and descriptions, you review the taxonomy of any that look odd, e.g. `dumbbell`) | M |
| 4 | `gallery_manager.py`: `rebuild_index` (taxonomy from the plot entry, derived geom, calls the check, same index format), `submit_example` (writes the new format) | M |
| 5 | Previews: script moved to `assets/scripts/`, app path, one size; regenerate and look at 34 pictures | M |
| 6 | `gallery_handlers.py` and `gallery_viewer.py`: choices, order, icons and labels from the dictionary; remove the dead modal and autofill; the YAML tab shows the recipe | M |
| 7 | Bootloader: the gallery load gate (D4) | S |
| 8 | Rules and records: `rules_gallery_standards.md` rewritten (your double confirmation), a new ADR "Gallery examples are recipes" that amends ADR-037, 061, 063 and ADR-083 (`_meta` and taxonomy), `GALLERY.md`, `docs/user_guide/viz_gallery.qmd`, `libs/viz_gallery/README.md`, the four gallery UML diagrams, glossary | M |
| 9 | Tests: the gallery tests adapted first (`test_gallery_bundle.py`, the two debug files, `test_legacy_formats.py`, UI scenarios, smoke), plus: index equals rebuilt index, every example passes the checker, every preview renders, every term in the dictionary, `submit_example` output passes | M |
| 10 | Migration scripts that touch gallery files (`migrate_config_vocabulary.py`, `LEGACY_GALLERY_FILES`) | S |

Order: 1, 9 (tests first, failing for the right reason), 2, 3, 4, 7, 5, 6, 10, 8.

## 8. Effects on what was written before

- `recipe_format_spec.md` section 6.9 and the gallery rows of sections 3, 8, 11, 13 are rewritten once you choose; the other sections are not affected except: the optional `taxonomy` key (6.7), and one **correction** found while reading `plot_authoring_model.md`: the key for a comment is **`comment`** (singular), already written by Blueprint on steps, layers, groups and plots (BP-COMMENTS-1, ADR-082 Q4), so my `comments` of section 5b becomes `comment` and the checker must accept it on steps and layers (see `recipe_format_spec.md` v0.3).
- Issue #78 (migration): the gallery row is replaced by this design; a new issue holds the gallery work (#82).
- ADR-083 is amended: `_meta` and the taxonomy passthrough are replaced by declared keys (`taxonomy`, `comment`).

## 9. Risks

1. Blueprint's save path must keep the entry's keys (`taxonomy`, `comment`, `steps`); to verify in `group_plot_manager` before the migration.
2. A longer example file in the YAML tab; mitigation: tabs "Recipe" and "Plot only", or the plot part first.
3. First preview regeneration changes 12 pictures in git (size, jitter); looked at one by one.
4. A deployment that moves the gallery folder cannot run the examples (it can browse them).
5. The Playwright gallery tests and four diagrams need an update.
6. A generated data contract could change a picture if a type is guessed wrong; the proof-of-concept script is the guard.

## 10. What I need from you

1. D1 to D6 (and D7): my recommendation is the first option of each. A different choice for any of them changes the plan, not the principle.
2. The key name **`taxonomy`** on the plot entry (alternative: `gallery`).
3. Whether the dead submission code is removed now (recommended) or kept for the contribution form that GALLERY.md plans.
