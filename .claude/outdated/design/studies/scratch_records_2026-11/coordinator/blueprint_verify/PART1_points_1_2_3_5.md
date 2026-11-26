# BLUEPRINT today, points 1, 2, 3 and 5 of the owner's seven (scout survey, read only, 2026-11-22; filed and shortened by the coordinator)

Nothing was run. "verified" = read at file:line. Ledger D-0493, D-0494. Paths under the repository root.

## Verdicts in plain words
| Her point | Verdict | In one sentence |
|---|---|---|
| 1. Engines can be switched | PARTLY | The app can hold two engines and a recipe names them (top, per tier, per plot); BLUEPRINT keeps the engine keys on save but does not show them, does not let the author choose, does not filter its pickers by engine, and calls Polars directly in several places. |
| 2. Every Polars action usable in the forms, parameters selected or typed | PARTLY | All 68 actions have a form; for the 65 exact Polars ones every parameter has a field; but some values are typed as text, and Apply silently removes any parameter the form does not show. |
| 3. Every plotnine component usable, parameters selected or typed | PARTLY | All 191 components have a form; the 123 exact ones list every plotnine parameter but almost all as free text; nested objects cannot be typed; the mapping offers 8 aesthetics only. |
| 5. Write in all the data tiers | DOES NOT | BLUEPRINT saves tier 1 and tier 2 of a table, plot entries, groups and the info block; it cannot save join tiers, tier 3, input fields, new tables or joins; `plot_defaults` is never written to the file; no step reorder, no single-step delete; Save does not run the recipe check first. |

## Point 1: engines
- Recipe: `data_engine`, `plot_engine` at the top (`libs/utils/src/utils/recipe_spec.yaml:23`), per tier (`:63-65`), per plot (`:51-54`). D-0219 (her words): "The code MUST choose the engine"; "top recipe is the defaults engines used over the whole recipe unless its overwritten". D-0237, D-0238, D-0239, D-0240.
- App: two engine names (`libs/utils/src/utils/engines.py:31-48`), `app/modules/engine_registry.py:35-99`; every action and component is registered with an `engine` field (`libs/transformer/src/transformer/actions/base.py:30-51`; `libs/viz_factory/src/viz_factory/registry.py:50-82`).
- BLUEPRINT: no display and no choice of engine; a NEW recipe is written with the app's first engine without asking (`libs/utils/src/utils/recipe_factory.py:162-163`); pickers list by context only (`app/modules/wrangle_studio.py:851, 876-886`; `libs/blueprint_arch/src/blueprint_arch/schema_registry.py:82-113`); the catalogs carry no engine (`app/src/server.py:41-44`).
- Direct Polars in BLUEPRINT: `app/handlers/blueprint_handlers.py:61, 189, 2118-2123`; `app/modules/wrangle_studio.py:26, 605, 627-637, 736-737, 2317-2329`. Engine words held as data and NOT in the engine list: `libs/blueprint_arch/src/blueprint_arch/join_designer.py:27, 153` (join kinds, including "outer"); `wrangle_studio.py:2018-2019` (dtype list), `:2181-2187` (palette names).
- A second engine would touch about ten BLUEPRINT places (the list is in the scout's full report: pickers, new-recipe default, the direct calls, the dtype list and the expression placeholder, palettes and themes, the audit translator, the join kinds, component names).

## Point 2: data actions
- 68 registered (39 in `polars_calls.py`, 12 aggregations, 10 rows, 5 time joins, `modif_filter`, `step_top_n_other`); all have a `ui_schema`. For `polars_` actions the fields are read from the Polars signature (`polars_calls.py:159-178`); five parameters are deliberately not exposed, each with a reason.
- The form renderer: `app/modules/wrangle_studio.py:2007-2315`. Supported: column picker, expression (a text area), choice list, dtype picker (a FIXED list of 11 names, the schema's own options are ignored), number, yes/no, column-or-literal, colour; list, mapping and "any" are ONE LINE OF YAML TEXT; anything else falls back to a text box.
- Typing on Apply (`blueprint_handlers.py:1243-1371`): a literal typed in "column or literal" is saved as TEXT ("10", not 10); **parameters that are not fields of the form are DROPPED** (`:1255-1346`).
- Column pickers are filled from the table's declared input fields, not from the columns that exist after the earlier steps (`:684-689`); for a join the list would be the single entry "?" (reasoned; needs a run).
- Save rebuilds the tier block: `data_engine` if present, then `steps`; YAML comments are lost; other keys of the tier file are not kept (`:583-608`).
- The join designer offers "outer", which the join action does not accept (`join_designer.py:27`; task BLUEPRINT-JOIN-OUTER-OPTION).
- Tests: only 18 of 68 actions have their form metadata checked by name; no test renders every action through the form.

## Point 3: plot components
- 191 registered (65 geoms and stats, 67 scales, 25 themes, 11 guides, 9 facets, 8 positions, 6 coords); 123 exact, 46 modified, 22 own; all have a schema.
- Exact components: every plotnine parameter is a field, but the widget is "yes/no" for a boolean default and free YAML text otherwise (`libs/viz_factory/src/viz_factory/parameters.py:110, 127`).
- Hand-written components list only some parameters; the rest are lost on Apply. `allow_extra_params` is declared and read by NO production code.
- Nested objects: `theme_custom` has no fields (the form cannot show or edit it); a position as an object and a guide inside a scale cannot be expressed. How arguments and nested objects are passed is NOT decided (ledger D-0218; question Q6 open).
- Values that are lists or mappings are declared as text in several scales (`scales/core.py:185, 523, 1262`): saved as text; whether plotnine accepts that needs a run.
- The mapping form offers 8 aesthetics (x, y, fill, color, size, alpha, shape, facet_by); other mapping keys are DROPPED on Apply (`wrangle_studio.py:945-954`; `blueprint_handlers.py:1219-1238`).
- A conflict in the records: `facet_by` is a top-level key of a plot in the spec (`recipe_spec.yaml:53-54`) and is read inside `mapping` by the check and written there by BLUEPRINT.
- `plot_defaults` form: 5 theme names of 25; session only, never saved (`blueprint_handlers.py:1743-1771`).
- The prefix rename of components (`plotnine_<name>`) is decided and not built; BLUEPRINT depends on component names in about seven places.

## Point 5: where BLUEPRINT can write
| Place | Create | Edit | Reorder | Delete | Saved to the file | Check before save |
|---|---|---|---|---|---|---|
| Tier 1, tier 2 of a table | yes (append) | yes | no | only "Clear All" | yes | no |
| Tier 1, tier 2 of a join | in memory | in memory | no | no | **no**: "Save is not supported for component role 'join'" (`blueprint_handlers.py:610-613`) | - |
| Tier 3 of a plot | **no** (`:505, 1158-1159`: "BLUEPRINT never authors T3") | | | | kept as found | - |
| Input fields | no (read only) | | | | | |
| New tables, new joins | no code | | | | | |
| `plot_defaults` | session only | | | | **no** | |
| `info` | yes | yes | | | yes | no |
| Groups and plot entries | yes | yes | | reference only | yes (whole-file rewrite) | no |
- **A contradiction with a decision:** the code and `.claude/design/spaces/BLUEPRINT.md:51` say BLUEPRINT never writes tier 3; ledger D-0063 (2026-11-15) says BLUEPRINT may author the plot entry's tier 3.
- **Defect confirmed:** BLUEPRINT's Info form reads and writes `info.name` (`blueprint_handlers.py:2543, 2611`); HOME reads `info.label` (`app/handlers/home_theater.py:1144`); a new recipe is written with `info.label`. A name typed in BLUEPRINT is not shown in HOME.
- Validate is a separate button; Save writes without it.
- A step written in the old shape (with a `params:` key) is read and silently rewritten flat on save.

## Needs a run (not done)
The counts 68 and 191 by the registries; a headless render of every form; the Apply round trip for a number, a literal, a list declared as text, an extra key; what Save does to a file with a nested `!include`; the column picker of a join tier; whether plotnine accepts text where a list is expected.

## Stale records met
`rules_data_analysis_recipe_structure.md:117` says the save serializer is "not yet implemented" (it exists); `rules_ui_dashboard.md:121` and ADR-082 say "all 60 actions verified" and "eight widgets" (68 and twelve today); task BLUEPRINT-PLOT-DEFAULTS-FORM-1 does not match the code.
