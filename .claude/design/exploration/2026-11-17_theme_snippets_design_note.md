Report for Eve. Nothing in it is decided.

# Named themes: design note for Eve

2026-11-17. Design only. Nothing is built, no repository file is changed.
Decisions it follows: D-0243 (a theme is copied into the recipe), D-0244 (theme rule, template), D-0242 (many settings), D-0245, D-0248 (export record).
Evidence labels: **ran** (I ran it, scripts in this folder), **read** (file:line), **reasoned**, **not checked**.

## What the recipe author sees

- In Blueprint, a list of named themes: "Lab default", "Publication", "Dashboard", and the lab's own. Each has a label, one line of description and a preview. (NEW)
- One click copies the theme into the recipe: into the recipe defaults (all plots) or into one plot. (NEW)
- After the copy, the theme is ordinary recipe text. The author can change any value. The theme file is not read again.
- "New recipe" offers the same list. (NEW)

## 1. The open point: who can add a theme

Your words (D-0243): "how easy to add new themes - will be new actions ... means it's a new release". The review session read this as "adding a theme must not need a release". You have not confirmed that. Two readings:

| Option | What a lab does to add a theme | For | Against |
|---|---|---|---|
| **R1**: a theme is a small data file in a folder | Puts one file in the theme folder. No code, no release. | Cheap. The values are copied into the recipe, so a file that changes or vanishes changes no result. Matches D-0243 and D-0211 (no shortcut components). | A lab file can hold a mistake. Suggestion: check each file with the recipe checker when Blueprint lists it (section 6). |
| **R2**: a theme is a registered component in code (like `theme_dashboard` today) | Asks for a code change. The theme comes with the next app release. | The project controls every theme. | The values sit in code, not in the recipe, and are looked up when the plot is drawn. That contradicts D-0243 ("nothing is looked up at drawing time"). It also reconsiders D-0211 (shortcut components are removed). |
| R2 without the contradiction: theme files that ship only with the app | Asks for a release that adds a file. | No lab files to check. | Same file format as R1; only the lab folder is missing. |

**Recommendation (reasoned, not a decision): R1.** It needs no code per theme. The copy keeps every result reproducible. Only R1 lets a lab add its own theme without waiting.

## 2. Where the files live

- Precedent: the palettes. They are one shipped file, `config/palettes.yaml`. The bootloader reads it once at start (`app/src/bootloader.py:841-914`, path fixed at `:860`) and hands it to the plot library (`app/src/server.py:105`). It is the same for every deployment, although the code calls it "deployment palettes".
- One difference matters. A palette is looked up by name when the plot is drawn (`libs/viz_factory/src/viz_factory/viz_factory.py:440`). A theme is copied (D-0243). So the plot library never sees the theme folder. Only Blueprint and "new recipe" read it.
- Suggestion: shipped themes in `config/themes/`, one file per theme (a new file never edits a shared file). A lab folder is named in the deployment file, like `branding.theme_css` names the lab's own CSS file (ADR-055, ADR-091; `bootloader.get_theme_css_path`). The key is NEW.

## 3. One theme file

A name, a label, one line of description, and a list of layers in the existing layer form. Nothing else. No code.

Layout rule I propose (MINE): the base theme carries only the font and the size; every single setting goes in `theme_custom`. Two facts support it:
- The checker refuses single settings on `theme_bw` inside a plot (ran: `legend_position is not an argument of theme_bw`, error PS04, `libs/utils/src/utils/recipe_check.py:997`), although drawing accepts them (`themes/core.py:20-35`). In `theme_custom` both accept them (ran).
- Settings in `theme_custom` stay when a plot changes the base theme (section 5).

The three examples are at the end. Each was drawn through `VizFactory.render`, in the recipe defaults and in one plot, and checked by the recipe checker in the "run" profile: all draw, no problem reported (ran, `scratch_final.py`; pictures `*.png` in this folder).

Fonts: I used only fonts that matplotlib finds on this machine without falling back (ran `font_manager.findfont(..., fallback_to_default=False)`). Liberation Sans and Liberation Serif come from Fedora (`/usr/share/fonts`). DejaVu Sans and DejaVu Serif come inside matplotlib itself, so they exist wherever the app is installed. Arial and Helvetica are not found here. The font question on other machines is a separate task.

## 4. The custom theme template

`template_custom_theme.yaml` (at the end). One commented file with the common settings: font family and size, legend position, direction, title and text, panel spacing, grid, backgrounds, plot title, axis title, a margin, facet labels, outer margin, axis tick labels. Every line draws today (ran). It points to `theme_custom` and to plotnine's list of settings.

## 5. How a theme gets into a recipe, and what happens after

- **Recipe defaults:** the layers go under `plot_defaults: layers:` (an allowed key, `plot_config_resolver.py:67-70`). **One plot:** they are added to that plot's `layers:`. Both draw the same (ran).
- **Blueprint today:** the plot-defaults form (`app/handlers/blueprint_handlers.py:1806-1902`) has a theme picker of five names. It is fixed first, alone (D-0246). The theme list, the preview and the two copy buttons are NEW. Suggestion: when the recipe already has theme layers, the copy shows what it replaces and asks before replacing.
- **New recipe today:** the dialog asks id, name, description, author (`blueprint_handlers.py:2772-2850`) and writes a draft with no plot defaults (`libs/blueprint_arch/src/blueprint_arch/new_recipe.py:19-35`). A theme choice there is NEW. Default: no theme, so the built-in default applies.
- **After the copy:** the recipe holds every value. The theme file can change or vanish; no picture changes. Suggestion: each copied layer carries a comment, for example `comment: "copied from theme lab_default on 2026-11-17"`. Layers accept a comment today (ran: draws, checker silent).
- **Export:** D-0248 decided that `effective_run.yaml` records the theme as applied per plot. It is not built: the export mentions a theme only for the old T3 override (`app/handlers/export_handlers.py:492`).

**The theme rule (D-0244) when a plot has its own theme** (ran, with the lab default in the recipe defaults):
- The plot writes a complete theme (`theme_minimal`): it replaces the default's base, so the font is lost. The default's `theme_custom` settings stay: the legend stays at the bottom.
- The plot writes a single setting (`theme_custom` legend top): it is added. The font stays; the plot's legend wins.

Note: the ledger line of D-0244 says such a plot "loses the default's font and legend". That holds when the legend sits inside the base theme layer. With the layout of section 3, only the font is lost. The checker note that D-0244 asks for is not built (not checked beyond the builder's report).

## 6. A lab adds its own theme (R1)

- **Where:** the lab folder named in the deployment file. **Who:** whoever administers the server. App users cannot write there. (MINE)
- **Check:** Blueprint checks each file when it lists it: the known keys only, every layer name registered, every argument known, no code. A file that fails is not offered; its problem is shown with the file name. Suggestion: reuse the layer check of the recipe checker. It needs one small change: today it demands a geom layer in a plot (`recipe_check.py:956-1000`), and a theme has none. NEW.
- **Risk: a font the server lacks.** Today the plot still draws, in DejaVu Sans, and only a log line says so (ran with Arial). The author is not told. This is a silent change of the picture; it belongs to the separate font task.
- **Risk: the rename of the components** (`plotnine_...`, D-0091, decided, not built). Copied recipes are converted by the migration tool, like any recipe. Shipped theme files are converted in the same pass. A lab file with an old name is refused by the check with "did you mean", and the lab runs the same tool on its folder. The new name of `theme_custom` is not decided yet.

## 7. `theme_dashboard`: which text is wrong

- Its description says it is "the default theme in SPARMVET data analysis recipes" (`libs/viz_factory/src/viz_factory/themes/core.py:264`).
- The real default is `theme_bw` with plotnine's size 11: the built-in layer at `plot_config_resolver.py:47`, the default at `:63`, the docstring at `viz_factory.py:135`. No shipped recipe or gallery example uses `theme_dashboard` (read: grep over `config/` and `assets/gallery_data/`).
- **The description is wrong.** Proposed line (not applied): "SPARMVET screen preset: theme_bw with base_size 14 unless given. Not the default; the default of every plot is theme_bw size 11."
- Two more wrong texts of the same kind: `docs/workflows/visualisation_factory.qmd:102` calls it "High contrast"; `theme_publication` claims "increased font sizes" (`core.py:284`) but uses size 11, plotnine's own default for `theme_classic` (ran: `inspect.signature`).
- Both are shortcuts that an exact plotnine theme already does with one argument. Under D-0211 they are removed. Their content becomes the "Dashboard" and "Publication" theme files.

## 8. What waits for the argument research, what does not

- **Can be built now (plain values):** the folder, the file format, the list, the copy, the check, the comment line, the export record. Settings: font family and size, legend position and direction, panel spacing, outer margin.
- **Waits for the research (nested values):** a setting written as `{name: element_text, params: {...}}`, and a margin inside an element (`margin: {t: 8}`). They draw today through `theme_custom` (ran). But the format of nested values is not decided (`rules_viz_factory.md` 1a, D-0218). If the research changes it, theme files and recipes with elements are migrated. The Blueprint form fields for these settings also wait (D-0246).

## Found on the way (ran, not fixed)

1. The checker does not look inside `plot_defaults: layers:` at all: an unknown component or argument there is not reported (`recipe_check.py:1002-1015`). Drawing then fails with a clear message (ran). So the check before drawing does not catch it (reasoned; the HOME gate itself was not run).
2. The checker and the drawing disagree on `theme_bw` with extra settings (section 3).
3. An axis-text `element_text` layer in the recipe defaults does not override the automatic axis-text adjustment; in one plot it does (ran: angle 45, size 8 versus 9). D-0242 says the author overrides it "with an element_text"; it does not say where.
4. Blueprint's plot-defaults form is registered only when the AI agent is switched on: it sits after `if not bootloader.is_enabled("blueprint_agent_enabled"): return` (`blueprint_handlers.py:1787`). It belongs to the form fix (D-0246).

## What you are asked

1. Adding a theme: R1 (a lab adds a file, no release) or R2 (a theme comes with a release)?
2. Shipped themes in `config/themes/`, a lab folder named in the deployment file: yes or no?
3. Theme file layout: base theme with font and size only, all single settings in `theme_custom`: yes or no?
4. `theme_dashboard` and `theme_publication` leave the code (D-0211) and become theme files: yes or no?
5. Correct their wrong descriptions now, before the removal: yes or no?
6. Finding 2: should `theme_bw` refuse extra settings (as the checker and plotnine do) or accept them (as the drawing does)? Refuse or accept?
7. Finding 3: should an axis-text layer in the recipe defaults override the automatic adjustment for every plot: yes or no?

## Not checked

- Fonts on any machine other than this one; the server images.
- The full HOME gate on a whole recipe with theme layers (I ran `check_recipe` with the app's catalogues, not the gate itself).
- How Blueprint draws a preview (live on the recipe's plot or a stored picture).
- `facet_grid` strips (the examples use `facet_wrap`).
- The exact wording of the D-0244 checker note; whether any other text calls `theme_dashboard` the default outside the files grepped.
- Whether the palette lookup at drawing time is recorded in the export (the plan of 2026-11-17 says it is not; I did not check).

---

## The examples (each drawn and checked, ran)

`snippet_lab_default.yaml`
```yaml
name: lab_default
label: "Lab default"
description: "White background with a grid, Liberation Sans 11 pt, legend at the bottom."
layers:
  - name: theme_bw
    params: {base_family: "Liberation Sans", base_size: 11}
  - name: theme_custom
    params:
      legend_position: bottom
      panel_spacing: 0.1
```

`snippet_publication.yaml`
```yaml
name: publication
label: "Publication"
description: "Classic axes, no grid, Liberation Serif 9 pt, bold facet titles, legend on the right."
layers:
  - name: theme_classic
    params: {base_family: "Liberation Serif", base_size: 9}
  - name: theme_custom
    params:
      legend_position: right
      strip_text: {name: element_text, params: {face: bold}}
      strip_background: {name: element_blank}
      plot_title: {name: element_text, params: {size: 10, face: bold}}
```

`snippet_dashboard.yaml`
```yaml
name: dashboard
label: "Dashboard"
description: "Large text for the screen: DejaVu Sans 14 pt, white background, no minor grid, legend at the top."
layers:
  - name: theme_bw
    params: {base_family: "DejaVu Sans", base_size: 14}
  - name: theme_custom
    params:
      legend_position: top
      panel_grid_minor: {name: element_blank}
```

`template_custom_theme.yaml`
```yaml
# Custom theme template. Copy it, keep the lines you need, delete the others.
# Every line below draws today. The settings are plotnine's theme() settings:
# https://plotnine.org/reference/theme.html  (also in the help of theme_custom).
name: my_theme
label: "My theme"
description: "One line: what this theme is for."
layers:
  # 1. The base look and the font of all text. A complete theme: it replaces the default's base.
  #    Other bases: theme_classic, theme_minimal, theme_light, theme_gray ...
  - name: theme_bw
    params:
      base_family: "Liberation Sans"   # a font installed on the server that draws
      base_size: 11                    # points; every text size follows it
  # 2. Single settings, added on top of the base (a partial theme: it replaces nothing).
  - name: theme_custom
    params:
      # legend
      legend_position: bottom          # right, left, top, bottom, none
      legend_direction: horizontal     # horizontal or vertical
      legend_title: {name: element_text, params: {size: 10, face: bold}}
      legend_text: {name: element_text, params: {size: 9}}
      # panels and grid
      panel_spacing: 0.1               # space between facet panels (fraction of the figure)
      panel_grid_major: {name: element_line, params: {color: "#dddddd", linewidth: 0.5}}
      panel_grid_minor: {name: element_blank}        # element_blank = not drawn
      panel_background: {name: element_rect, params: {fill: white}}
      plot_background: {name: element_rect, params: {fill: white}}
      # titles and facet labels
      plot_title: {name: element_text, params: {size: 13, face: bold}}
      axis_title: {name: element_text, params: {size: 11}}
      axis_title_x: {name: element_text, params: {margin: {t: 8}}}   # space above the x title, in points
      strip_text: {name: element_text, params: {size: 10, face: bold}}
      # outer margin of the figure
      plot_margin: 0.02                # fraction of the figure
  # 3. Axis tick labels: use an element_text layer with a target, not theme_custom.
  #    For a category axis the app adapts angle and size by itself; only this layer overrides it,
  #    and today only inside a plot, not in the recipe defaults (finding 3).
  - name: element_text
    params: {target: axis_text_x, size: 9, angle: 45, hjust: 1}
```
