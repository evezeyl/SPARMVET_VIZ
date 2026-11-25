# Round 2 facts: what a tier shows, and what exists for a "text plot" (scout survey, 2026-11-22; filed and shortened by the coordinator)

Read-only, branch `dev`. V = verified at file:line by the scout; R = reasoned; "not verified" is said where it applies. First round: `FACTS.md`.

## Her words (channel blocks M537, M538)
"we could do simple: when a table is the result it is shown in the highest tier that contains instruction no because the table shown is the result of the tier x applied (please I need a confirmation) - So we could actually have a "text plot" : the table Tier X shows the results requested by the recipe. That would avoid build something new. A note : there is still the switch in the tables view in home : normally it shows only the first 100 lines but there was a switch to show the whole table so this behavior still need to be there."
"that no tier 3 exist today does not mean it can - its still a data table - that we decided that it was the last stage before a plot is our choosing, but does not mean that table 3 could not be the final table of a result in table shape"

## 1. The confirmation she asks for: TRUE, with four things laid on top in the preview
- The table at a tier is the result of every step up to and including that tier (V): T1 = the source read plus the tier 1 steps (`app/modules/orchestrator.py:431-587`); T2 = T1 plus the tier 2 steps of that table (`:589-688`); T3 = T2 plus the entry's own tier 3 steps (`:690-750`; it calls the tier 2 build first, `:724`).
- A tier with no steps is the same table as the tier below, by key and by stored file: nothing extra is stored (`orchestrator.py:630-633, 726-731`; `app/modules/cache_keys.py:441, 452-459`). The badge says "T2=T1", "T3=T2" or "T3=T2=T1" (`app/modules/view_badge.py:88-99`).
- So "the highest tier that has steps" is the last place where the table changed, and T3 always shows exactly that table: the table after every step the recipe wrote. The two are the same table (R from the above).
- Laid on top, in the data preview only, never in the stored table: (a) in Audit mode, T3 also carries the audit steps (`app/handlers/home_theater.py:1685-1687`); (b) exploration filters (`:1688-1690`); (c) the first 100 rows unless "All rows" is on (`:1692-1693`); (d) the column selector (`:1696-1700`).
- Source is different: it is one source file as read, before any step (`home_theater.py:463-483`).

## 2. The "All rows" switch (V)
`ui.input_switch("preview_all_rows", "All rows", value=False)` (`home_theater.py:1253`); off by default. Off: `lf.head(100).collect()`; on: the whole table is collected (`:1692-1693`). The limit is applied AFTER filters and audit steps. The number 100 is written in the code line and in the title ("Data Preview (max. first 100 rows)", `:1665-1666`), not as a named constant. No "showing N of M" text exists.

## 3. A tier as a stage of data, and what our definition adds
- In the engine, tier 2 and tier 3 steps are run by the same runner, chosen the same way (`orchestrator.py:675, 744-746`; `app/modules/engine_registry.py:38-49`). Nothing in the data makes a tier 3 different in kind. The only difference: tier 3 checks each step as it is added and names the plot in the error (`orchestrator.py:128-144`).
- What ties a tier 3 to a plot is where we look it up, not what it is:
  | Place | Needs a plot, or only an id? |
  |---|---|
  | key `tier3` only in a plot entry (`recipe_spec.yaml:54, 57, 75`) | the plot entry |
  | `tier3_steps(raw, plot_id)`, `tier3_parts` (`recipe_tiers.py:164-173`; `orchestrator.py:112-125`) | looks up the plot entry; refuses an entry with no `target_dataset` |
  | `materialize_tier3(recipe, plot_id)` | through the lookup above |
  | key `plot_key_of(plot_id)` (`cache_keys.py:452-469`) | built from plot entries |
  | stored file `<target>__T3_<id>.parquet` (`orchestrator.py:37-38`) | ONLY AN ID |
  | audit run: one run per plot of the graph (`app/modules/audit_run.py:186-192, 240-263`) | the graph's list of plots |
  | lineage place `T3:<id>` (`lineage_walk.py:538`) | a graph node of kind plot |
  | HOME audit steps kept per id (`home_theater.py:546-554`) | ONLY AN ID |
  | HOME sub-tab `subtab_<id>` (`:583`) | ONLY AN ID for the name; content from the plot entry |
  | the plot engine | needed only for DRAWING, in no table key (D-0240) |
- Consequence (R): if a result table IS an entry found by the same lookup as a plot entry (same list, same id space), every place above works unchanged for building, keying, storing, auditing and tracing its table. If it is something else (an id outside the plot entries), it needs a second place for its steps, a second lookup and a key of its own.

## 4. What exists today for "a plot entry that shows its table"
- The check refuses a plot entry without `mapping` and `layers`, and without a drawing layer: PS03 "mapping and layers are required" (`recipe_check.py:1151`), "no geom or stat layer" (`:1218`).
- Every caller of the draw expects a plotnine object and draws or saves it: HOME plot (`home_theater.py:639, 734`, output `ui.output_plot` `:993`), Compare (`:758-799`, `:985`), the opening build (`app/modules/opening_build.py:149-152`), the export (`app/handlers/export_handlers.py:1277, 1294, 1313`), the Gallery previews (`app/modules/gallery_examples.py:131`), BLUEPRINT's live plot (`app/modules/wrangle_studio.py:706-714`), two scripts. An engine that returned a table could not be dropped in as it is: these callers must each branch.
- The plot engine (D-0238, D-0239, D-0240): an open list of engine names; today `python-polars` (data) and `python-plotnine` (plots) (`engine_registry.py:35`); a plot entry's `plot_engine` selects the library (`:52-61`); an unknown one is refused with "no library for this engine in this app".
- HOME: a sub-tab holds a plot output built per plot id (`home_theater.py:635-643, 985-1279`). The data preview is ONE shared grid under all sub-tabs (`:1258, 1669-1702`), a different kind of output. No two-pane table comparison exists (Compare is two plots).
- Export: per plot a picture; `T3_data_<plot>.tsv` when the plot has tier 3 or audit steps (`export_handlers.py:1438-1440`). The report template includes figures only; it links data files and includes no table (`app/assets/report_template.qmd:69-72`).
- Text drawing components are registered (`geom_text`, `geom_label`, `geom_tile`: `libs/viz_factory/src/viz_factory/geoms/core.py:355, 406, 437`), so a picture of a table is possible in principle; no shipped recipe does it.
- The format has no key that marks a table, a join or a group as a result (`recipe_spec.yaml:27-57`). A table and a join have `description`, `comment`, and a join has `labels`; a plot entry has `ui_label`, `description`, `labels`, `tier3`.
- No HOME path shows a table that no plot reads today: every table shown comes from a plot entry, and the "Source table" list holds only the sources that feed the open plot (`home_theater.py:290-313, 402-414, 1441-1461`).

## Not verified
What `VizFactory.render` does with a missing `mapping` (the check stops it first); whether an audit step written at tier 2 reaches the HOME T2 view in Audit mode; memory use of "All rows" on a large table; shipped recipes other than the demo.
