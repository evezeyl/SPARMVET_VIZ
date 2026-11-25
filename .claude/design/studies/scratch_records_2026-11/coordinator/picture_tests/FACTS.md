# What the picture tests compare today (scout survey, 2026-11-21; filed and shortened by the coordinator)

For her words (D-0466): "normally we should test until the end, thought i am not sure that a byte by byte way of testing is best ... Still comparing only data is not good for a test up to plot in other cases". Read-only; no test run. READ = seen at file:line; REASONED = inferred.

## For the owner
1. The picture-level tests exist and stay. The strongest is the picture proof: every plot of every shipped recipe, drawn through the app's own path at a fixed size (960 x 600), compared pixel by pixel with a stored picture, drawn twice to catch an unstable plot. It is run by hand, not by the test suite.
2. The "golden baseline" compares TABLES and the plot's data, not pictures.
3. Four browser tests compare a HOME picture pixel by pixel (seed places, step order, plot tier 3, export download). The one being repaired compared the picture's text string, which is the same as the file's bytes.
4. Why a byte comparison fails when the plot is the same: the width of the panel in the browser; the fonts of the machine (no test fixes them); text stored inside the picture file (the drawing library's version; the app's own record with a time).
5. PROPOSAL, not decided: one shared way to compare pictures that reads the pixels (not the bytes), at a size and resolution set by the test, ignores the text stored in the file, and checks the plot's table in the same test, so that a changed picture is traced to its cause (data, or drawing). Exact or with a small tolerance is yours to choose.

## Who compares what
| Test or tool | Draws | Size | Compares | The app's path? |
|---|---|---|---|---|
| `assets/scripts/recipe_pictures.py --check` | every plot of every recipe of 5 folders | 8 x 5 in at 120 dpi (`:86`) | decoded pixels, exact (`:219-232`); drawn twice (`:286-299`) | yes (`materialize_tier3` `:279`, `PlotEngines.render` `:289`); run by hand (`:48-51`) |
| `assets/scripts/golden_baseline.py` | no picture: tables and each plot's data (`:94-121`) | - | hash of the table, row count, types (`:34-41`) | yes, for the data |
| `libs/viz_factory/tests/test_reproducible_render.py` | 15 jitter cases (`:42-57`) | dpi 60 (`:38`) | hash of the FILE BYTES, two renders in one run (`:39, 61-64`) | no (the plot library directly) |
| `libs/viz_factory/tests/test_every_component_randomness.py` | on request | dpi 20 (`:120`) | hash of the file bytes (`:122`); its comment says "pixels hashed" | no |
| `assets/scripts/gallery_previews.py` | the 34 Gallery examples | 8 x 5 at 120 dpi | pixels, exact; reports a percent, no threshold (`:73-106`) | the Gallery path |
| `app/tests/test_export_unchanged_by_the_view.py` | three exports of one small recipe | export dpi 300 | decoded pixels; the stored text is left out because it holds a time (`:46, 52`) | the export |
| `app/tests/test_export_download.py:163-201` | exported plots | export dpi | pixels, exact | browser and export |
| `app/tests/test_shiny_seed_places.py`, `test_shiny_step_order.py`, `test_shiny_plot_tier3.py` | HOME plots in the browser | the browser's layout (tier 3 fixes the pane width by hand, `:207`) | pixels, exact, same size required | browser, HOME |
| `app/tests/test_shiny_smoke.py:994-1027` (being repaired) | one HOME plot | the browser's layout | the picture's text string before and after | browser, HOME |

## Why bytes differ for the same plot (READ)
- The drawing library writes its own "Software" text into each picture by default.
- The app's export writes a record into the picture, with a time (`app/handlers/export_handlers.py:388-420`).
- The browser pane width (`test_shiny_plot_tier3.py:207`: "pictures of different widths are never the same picture").
- Fonts: no picture test sets a font; a missing font is replaced with only a log line (`libs/viz_factory/src/viz_factory/font_check.py:1-11`).
- One plot depends on a Python setting fixed by the tool (`recipe_pictures.py:41-46`).

## Options (what each catches and misses)
| Way | Catches | Misses or false alarms | Needs |
|---|---|---|---|
| file bytes | everything | false alarms on stored text | nothing |
| decoded pixels, exact | every visible change, size included | sees font and width differences | nothing |
| pixels with a small tolerance | real changes above the band | small real changes inside the band; the band is a choice | nothing |
| size and resolution fixed by the test | removes the width effect | changes visible only at other sizes | nothing |
| the plot's table plus the picture at a fixed size | names the cause: data or drawing | browser layout effects | nothing |
| a perceptual likeness score | large changes | a single changed label | a package that is not installed |

## Not verified
Installed versions; whether the test suite on a server runs the browser tests or the picture proof; the number of plots in the picture proof; whether the HOME page reaches the same draw call (inferred from `app/src/server.py:111` and `app/handlers/home_theater.py:733`).
