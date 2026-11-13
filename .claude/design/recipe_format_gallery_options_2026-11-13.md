# Gallery examples as standard recipes: what must change, options, plan (2026-11-13, version 2)

**Written for:** Eve, to choose. Companion of `recipe_format_spec.md` v0.4 (its section 6.9 stays withdrawn until you choose here).
**Status:** proposal and plan. Nothing in the gallery, the recipes or the code was changed. Evidence labels: **verified** (read at file:line or run), **reasoned**, **proposal**.
**What changed since version 1 (your message of the same day):** the `taxonomy` key is **required** for the gallery (D2); recipes carry a **`format_version`** and so do the examples (spec 4b); the allowed gallery terms go **into the specification itself, one place instead of two** (D3, rewritten); everything that is wrong is mapped to the package that fixes it and the test that proves it (section 3); the work is **planned now and scheduled later** (section 7).

## 0. In short

- **It works** (verified by running, `tmpAI/recipe_format/gallery_poc.py`, scratch): all 34 examples written as standard recipes build and render through the app's own path (ConfigManager, DataOrchestrator, VizFactory: the call HOME makes). 22 previews are pixel-identical; 10 differ only in size (800x600 committed, 960x600 today); 2 differ by jitter (0.9 % and 2.6 % of the pixels, reasoned). Taxonomy values of all 34 are already inside the cheat sheet.
- **What is wrong will be fixed** (section 3): 8 findings, each has a package and a test.
- **Recommended design:** an example is a standard recipe (with `format_version`) checked in a `gallery` profile; the plot carries a **required** `taxonomy` (family, pattern, difficulty, show, sample size), `geom` is derived; the allowed terms live **in the specification**, which becomes a data file, so the checker, the filter panels, the index, the docs and the migration tool read one place.
- **Decide now** (they shape the spec file and the checker that #76 builds first): D1, D2, D3 and the key name. D4 to D7 can wait until the gallery work starts.
- **Schedule:** the specification part comes with the checker (soon); the gallery conversion itself comes after the checker and the pipeline-recipe migration (later); the order and dependencies are fixed in section 7.

## 1. What I read and ran

`gallery_manager.py`, `gallery_viewer.py`, `gallery_handlers.py` (taxonomy part), `generate_previews.py`, `TAXONOMY_CHEATSHEET.md`, `rules_gallery_standards.md`, `spaces/GALLERY.md`, `plot_authoring_model.md` (ADR-083), ADR-033/035/037/061/063/093 (headings), the 34 bundles, `gallery_index.json`, both shipped deployments, the gallery tests; and the proof of concept above.

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

## 3. What is wrong, and where each item is fixed

| # | Finding | Evidence | Fixed by (section 7) | Test that proves it |
|---|---|---|---|---|
| G1 | The **terms are copied in five places** (cheat sheet, viewer fallback lists, handler fallback lists, bundles, UI strings) and disagree: both fallback lists contain "Numeric-Numeric", which the cheat sheet does not allow, and lack 4 of its 10 patterns. Difficulty and sample-size orders are written twice more | verified: `gallery_viewer.py:167-195`, `gallery_handlers.py:72-89` | GAL-1 (terms in the spec), GAL-6 (UI reads them) | no list of terms in code (a grep test); every term shown by the UI comes from the spec file |
| G2 | **Previews do not come from the app's path**: the script hands the bundle's own dict to the renderer, so an example the app could not load still gets a picture | verified: `generate_previews.py:47-55` | GAL-5 | every example renders through ConfigManager and DataOrchestrator |
| G3 | The **example file is never validated as a recipe**; only its `info` is read. `data_path` is read by nobody; `wrangling` is only shown | verified: `gallery_manager.py:130-168`, `gallery_handlers.py:198` | GAL-1 (profile), GAL-4, GAL-7 | every example passes `check_recipe` in the gallery profile, at rebuild, at app start and in the tests |
| G4 | **One declared value disagrees with the plot**: `dumbbell` says `geom: geom_segment` and draws `geom_line` and `geom_point` | verified | GAL-3 (geom derived, so it cannot disagree; the example itself is reviewed with you: is it a dumbbell that should use `geom_segment`?) | derived `geom` equals the first geom layer for all 34 |
| G5 | **10 of 34 previews are 800x600**, 24 are 960x600 | verified | GAL-5 | all previews have the standard size |
| G6 | **Dead submission code**: `submission_modal_ui`, `autofill_meta_from_audit`, `btn_confirm_submission` (no handler) | verified: grep, `GALLERY.md` | GAL-6 (removed, or kept on purpose: your call) | no unreferenced submission symbol |
| G7 | The **tag strip** of each `example_meta.md` repeats the taxonomy; nothing checks it (today all 34 match) | verified | GAL-6 (strip generated from `taxonomy`) or GAL-1 (checked) | strip equals `taxonomy` for all 34, or no strip in the files |
| G8 | The taxonomy **travels by copy into pipeline plot specs** (16 of 17 ST22 plots) through the `_meta` passthrough of ADR-083, where nothing reads it | verified | #78 (ST22 migration removes it), spec 6.8 | no pipeline recipe carries `family`, `pattern` or `difficulty` in a spec |

## 4. What must not change

ADR-093 (static browser, no handoff, no run at view time), the offline use, `gallery_enabled` and the positive-inclusion rule, the six filter axes and their icons, the index format that the viewer reads, one plot per example, the folder name as the example's id, and `example_data.tsv` and `example_meta.md` as companion files. The gallery stays a *reference*: the design only changes what the example file is, who checks it, and where its terms live.

## 5. Decisions, options, pros and cons

### D1. What is an example file? *(decide now)*

| Option | Pros | Cons |
|---|---|---|
| **A. A standard recipe** (id, `format_version`, engines, info, one data schema, one group, one plot) checked in a `gallery` profile **[recommended]** | one format, one checker, one render path; an example is runnable (saved to a file and imported in Blueprint it works, unchanged); the examples show good practice (labels, descriptions, types); the 34 examples become a regression suite for the whole plot path; a later "start a recipe from this example" (GALLERY.md, open question) needs nothing new | the file is longer (about 35 to 60 lines against 25); 34 files to rewrite (scripted, reviewed); the data path is a project-root path like in every recipe, so a deployment that moves the gallery folder can browse but not run the example |
| B. Keep the compact shape and only add checks | smallest change | **two formats** (your objection); the example is still not a recipe; the special render path stays |
| C. Keep the compact shape as the source and generate a standard recipe from it | the source stays short | two sources and a generated file in git; drift between them |

### D2. The classification key *(decide now)*

You asked for a key that carries family, pattern and difficulty. Its **place** and **requiredness**:

| Option | Pros | Cons |
|---|---|---|
| **A. `taxonomy:` on the plot entry; required in the gallery profile, optional in any other recipe** **[recommended]** | the classification describes a plot; fits one plot per example; any recipe's plot may carry it, so a plot can be offered to the Gallery without retyping; the plot spec stays pure grammar (the boundary with Blueprint); replaces the `_meta` passthrough of ADR-083 | one gallery word in the common spec (checked against the vocabulary when present); Blueprint's save must keep the entry's keys (to verify in `group_plot_manager`) |
| B. `info.taxonomy` in the recipe's free-form `info` | no new key | `info` is free-form, so the check is a special case; wrong level for a recipe with several plots |
| C. A sidecar file in the bundle | the recipe has no gallery word | a second file and format; the loader cannot check it |
| D. Inside the plot spec, as ADR-083 does with `_meta` | follows ADR-083 | the spec stops being pure grammar; an exception in the checker |

Content: five declared axes (`family`, `pattern`, `difficulty`, `show`, `sample_size`), all required in the gallery profile. **`geom` is derived** from the first `geom_*` or `stat_*` layer (it cannot disagree with the plot) and is still offered as a filter. Key name: `taxonomy` (alternative `gallery`). `[proposal]`

### D3. Where do the rules and the allowed terms live? *(decide now)*

Your question: can the authorised terms be in the specification, so there is one place instead of two? **Yes**, if the specification is also something the program can read. Today the "spec" would be prose in a document, the checker is code, and the terms would be a third thing.

| Option | Pros | Cons |
|---|---|---|
| **A. The specification is a data file** in `libs/utils` (next to `check_recipe`): for each element its allowed keys and whether each is required, advice or optional; the types; the **vocabularies** (types, engines, **the gallery terms** with label, icon, order and one line of meaning); the table of renamed keys; the format version **[recommended]** | **one place** for every allowed key and value, gallery terms included; the checker, the filter panels, the index order, the cheat sheet and the markdown tables of the appendix are read or generated from it; adding a key or a term is one edit; the version of the file is the `format_version`, so spec and code cannot disagree; the tests can be generated per row | a small schema language to design (kept minimal; the cross-element rules and the registries of actions and plot components stay in code); the human text of the tables becomes a build output; **terms change more often than structure**: rule proposed, a new term in an open vocabulary does not change `format_version` (it ships with an app release), a change of a key does |
| B. Markdown spec as the text, plus a `gallery_terms.yaml` for the terms, plus the checker code | the spec stays prose | three places that must be kept equal (the drift of G1 again), kept in line only by tests |
| C. Terms written only in the markdown and parsed from it | one place on paper | fragile; the program cannot rely on it |

**Verified against the rules (spec section 0b):** a data file and the checker core in `libs/utils` respect the Tier-1 rule (pure Python and pyyaml, no peer import: shown by running a prototype), ADR-011 and ADR-099 16(g). One condition, found by building two wheels: the container installs `utils` non-editable, and without a `package-data` declaration a YAML file in the package is silently missing from the wheel. Declare it and test it.

If you choose A, it also decides how #76 is built: the "unknown key" check is then data-driven (no code change to add a key), and the generated tables replace the hand-written ones of sections 4 to 9 of the spec.

### D4. Where is an example checked? (one source of truth) *(can wait)*

| Option | Pros | Cons |
|---|---|---|
| **A. The same `check_recipe` (profile `gallery`) at index rebuild, at app start and in the tests** **[recommended]** | a broken example is caught wherever it enters; at app start it works like HOME's load gate (ADR-094): the example is left out of the list and the reason is shown; the data-and-render check runs offline where the previews are made | a small start-up cost (34 small files, no data read, reasoned); a few lines in the Bootloader |
| B. Offline and tests only | no change at start | a broken example can reach users if the tests are skipped |
| C. At app start only | users are protected | nobody sees the error while adding an example |

Layering `[verified, spec 0b]`: `libs/viz_gallery` may import `utils` (Tier 1) where `check_recipe` and the specification file live, but not `transformer` or `viz_factory` (peers); the catalogues of actions and plot components are handed in by the caller (script or app), as for HOME.

### D5. How are previews made? *(can wait)*

| Option | Pros | Cons |
|---|---|---|
| **A. By the app's own path**, in a Tier-3 script under `assets/scripts/` **[recommended]** | a preview proves that the example runs in the app; same seed rule (ADR-090); one standard size | the script depends on app code, so it leaves `libs/viz_gallery/assets/`; the first regeneration changes 12 pictures in git |
| B. Keep the current script | nothing moves | a second path; G2 stays |

### D6. `example_meta.md` and its tag strip *(can wait)*

| Option | Pros | Cons |
|---|---|---|
| **A. Keep the teaching text; the viewer builds the tag strip from `taxonomy`** (the line is removed from the 34 files) **[recommended]** | nothing to keep equal | 34 small edits; the file on disk has no strip when read outside the app |
| B. Keep the hand-written strip and check that it equals `taxonomy` | files unchanged | the information stays in two places |
| C. Fold the text into `description` or `comment` | one file less | loses the teaching text |

### D7. The data contract of an example *(can wait)*

`input_fields: {}` (what the proof of concept used) or a contract generated from the file (type from the Polars dtype, label from the column name) and reviewed. **Recommended: generated**, because the gallery should show good practice; the proof-of-concept script then confirms that no preview changes (a numeric column must stay numeric).

## 6. What an example would look like (recommended design; `bar_simple`)

```yaml
id: bar_simple
format_version: 1
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

`geom` (`geom_bar`) is not typed: it is read from the first layer. The old `data_path`, `name` and `wrangling.tier3` disappear: the path is in `source`, the name is `label`, and the example's own steps (what `submit_example` wrote into `tier3`) are the plot's `steps: {tier3: [...]}`, the same container as in audit mode (ADR-099).

## 7. The plan (scheduled later, fixed now)

**Decide now:** D1, D2, D3 and the key name, because the specification file and the checker (#76) are built first and take their shape from them. **Later:** D4 to D7 are chosen when the gallery work starts.

| Pkg | What | Depends on | Model / effort | Fixes |
|---|---|---|---|---|
| GAL-0 | You decide D1 to D3 and the key name | this document | you | |
| GAL-1 | In the specification file: the `gallery` profile (exactly one group and one plot, `taxonomy` present, `id` equal to the folder name, companion files exist), the `taxonomy` key, the vocabularies with the gallery terms, the EX checks. Built **with** the checker | `format_version` (#83), checker (#76) | `[opus/high]` | G1, G3 |
| GAL-2 | Tests first: adapt `test_gallery_bundle.py`, the two debug files, `test_legacy_formats.py`, UI scenarios, smoke; add: committed index equals rebuilt index, every example passes the checker, every preview renders through the app path, every term is in the vocabulary, `submit_example` output passes, every example has `format_version` | GAL-1 | `[opus/high]` | proves G1 to G7 |
| GAL-3 | Convert the 34 bundles: the migration tool (0 to 1), a gallery step (`name`, `data_path`, `info`, `tier3` to the recipe form), generated data contract, one-line descriptions, taxonomy and `dumbbell` reviewed with you | GAL-1, GAL-2, migration tool (#83) | `[sonnet/medium]`, review `[opus/high]` | G4, G8 |
| GAL-4 | `gallery_manager.py`: `rebuild_index` (taxonomy from the plot entry, derived geom, calls the check, same index format), `submit_example` (writes the new form) | GAL-3 | `[sonnet/high]` | G3 |
| GAL-5 | Previews by the app's path in `assets/scripts/`; regenerate the 34, one standard size; look at every picture | GAL-3 | `[sonnet/medium]` | G2, G5 |
| GAL-6 | Viewer and handlers read the vocabularies (panels, order, icons, labels); the YAML tab shows the recipe; the tag strip generated; dead submission code removed or kept on purpose | GAL-4 | `[sonnet/medium]` | G1, G6, G7 |
| GAL-7 | Bootloader: the gallery load gate (D4) | GAL-1 | `[sonnet/medium]` | G3 |
| GAL-8 | Rules and records: `rules_gallery_standards.md` rewritten (your double confirmation), a new ADR "Gallery examples are recipes" that amends ADR-037, 061, 063 and ADR-083 (`_meta`, taxonomy), `GALLERY.md`, `docs/user_guide/viz_gallery.qmd`, `libs/viz_gallery/README.md`, the four gallery UML diagrams, glossary | GAL-3 to GAL-7 | `[sonnet/medium]` | |
| GAL-9 | Remove the old-name code (`LEGACY_GALLERY_FILES`, gallery parts of old migration scripts if obsolete) | GAL-8 | `[haiku/low]` | |

Order: GAL-0, GAL-1 (with the checker), then later GAL-2, 3, 4, 7, 5, 6, 9, 8.

## 8. Effects on what was written before

- `recipe_format_spec.md` v0.4: section 4b (the format version), `taxonomy` required in the gallery profile (6.7 and 6.9 when you choose), and, if D3-A, a new section on the data file. Issue #82 holds this work and now carries the plan; #83 holds the format version and its migration tool.
- ADR-083 is amended: `_meta` and the taxonomy passthrough are replaced by declared keys (`taxonomy`, `comment`).

## 9. Risks

1. Blueprint's save path must keep the entry's keys (`taxonomy`, `comment`, `steps`); verify in `group_plot_manager` before GAL-3.
2. A longer example file in the YAML tab; mitigation: tabs "Recipe" and "Plot only", or the plot part first.
3. The first preview regeneration changes 12 pictures in git (size, jitter); each is looked at.
4. A deployment that moves the gallery folder cannot run the examples (it can browse them).
5. The Playwright gallery tests and four diagrams need an update.
6. A generated data contract could change a picture if a type is guessed wrong; the proof-of-concept script is the guard.
7. If D3-A: the schema language can grow; the guard is to keep it to keys, requiredness, types, vocabularies, renames and the version, and to keep cross-element rules in code.
8. The format version means an old export cannot be re-run without migrating its recipe (spec 4b); the recorded version tells which app generation reads it.

## 10. What I need from you

1. D1, D2, D3 (recommended: A, A, A) and the key name `taxonomy`.
2. Whether the format version is `format_version`, an integer (spec 4b).
3. Later, when the work starts: D4 to D7, and whether the dead submission code is removed.
