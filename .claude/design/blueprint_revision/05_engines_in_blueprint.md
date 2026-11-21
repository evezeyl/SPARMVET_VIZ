# BLUEPRINT-REVIEW-1, step 3: the engine "language" in BLUEPRINT

Written 2026-11-21 by a worker of BLUEPRINT-REVIEW-1 (D-0395). It builds nothing and decides nothing. Labels as in `04_what_blueprint_must_be.md` (read, read-1, run, document, reading of this review).

## Summary (10 lines)

1. The owner's words: "now we have only one engine for the data and one engine for the plotting - but the engine 'language' will need to be able to selected in the blueprint" (`ORDER.md`).
2. Decided and built in the engine layer: a recipe names `data_engine` and `plot_engine` at its top; a tier may name its own `data_engine`, a plot entry its own `plot_engine`; the code chooses the engine named; an unknown engine is refused with "no library for this engine in this app".
3. Built too: every registered action and plot component has an engine (68 actions `python-polars`, 191 components `python-plotnine`); the checker refuses a step written under another engine's block (EN02); the engine of each tier is part of that tier's cache key; the export record lists the engines and their library versions.
4. BLUEPRINT shows none of this: no control to choose or see an engine at any level; it only passes the recipe's plot engine to its (unmounted) plot preview and keeps a tier file's `data_engine` line on save.
5. BLUEPRINT's catalog of actions and components does not even receive the engine: the engine lives in separate tables that are not handed to it (run: 0 catalog entries carry an engine).
6. "Selectable" can mean three levels: the recipe default, a tier (tier 1, tier 2 of a table or a join, tier 3 of a plot), a plot.
7. At each level the same three questions come back: what the user sees, what the pickers and forms must filter, and what happens to the steps already written when the engine changes.
8. The hardest question is the last one: a translation of steps from one engine to another would change results without a word; the decided principles exclude a silent change.
9. Many questions cannot be judged with one engine only: column type names, expressions written as Polars code, the hand-over of a table between tiers of two engines, help texts, the agent's instructions.
10. No new engine is added now (D-0252); what BLUEPRINT needs is a design that does not block one later, and a plain display of the engine that is used.

---

## 1. What the owner decided about engines (ledger, taken by EVE, DECIDED)

| Number | Decision (her words where the ledger holds them) |
|---|---|
| D-0029 | "`data_engine`/`plot_engine` required" (in the recipe) |
| D-0219 | "So top recipe is the defaults engines used over the whole recipe unless its overwritten." "The code MUST choose the engine - otherwise why would we have added that ?" and "the engine would be determined in the correct tier or plot recipe if changed from the default of the recipe". The line also records, as the review session's words, not hers: "a data-engine override per tier is a plan owed to her, not decided" |
| D-0236 | Format 1 is amended before its first release; no format 2 ("B we are still in development so no problem - ensure all changes are propagated.") |
| D-0238 | "Every registry entry (every registered action and plot component) carries a field `engine`"; the checker refuses a step under another engine's block; `modif_` and `step_` carry no engine in the name (her answer: "A") |
| D-0239 | Engine names are an open list; "an app without its library refuses the value with 'no library for this engine in this app'" (her answer: "A") |
| D-0240 | "The plot engine enters no table key; the tier-2 engine is an argument of the tier-2 key, and each tier's engine is in its own key" (her answer: "A") |
| D-0247 | Each library has one small entry file that names its engine (`engine_python_polars.py`, `engine_python_plotnine.py`); "the libraries do not import each other; `app/` joins them" (her answer: "A") |
| D-0248 | `effective_run.yaml` holds the engine per plot and per table tier and the library versions |
| D-0250 | "a tier is written as its key (`tier1:`), then the optional `data_engine:`, then `steps:`" (her answer: "B") |
| D-0252 | "No new engine is added now"; her words: "even if we will not add new engines now, we can plan for it so the correct functioning takes in account that we will add new." |
| D-0036, D-0091, D-0210 | The name prefix says the engine for exact wrappers: `polars_` (built), `plotnine_` (decided, not built); `modif_` and `step_` carry no engine in the name |

Not decided (document: `.claude/design/exploration/2026-11-17_engines_default_and_override.md`): whether a second engine is ever added and which (the note names R with ggplot2 for plots and dplyr for data; "An engine per plot: yes, this is a sound feature to plan"; per data tier "possible in principle, large, and risky for correctness"; "An engine per step: all four say no").

---

## 2. What is built in the engine layer

| Piece | What it does | Evidence | Label |
|---|---|---|---|
| The engine table | Two rows: `python-polars` (key `data_engine`, library `transformer`, prefix `polars_`) and `python-plotnine` (key `plot_engine`, library `viz_factory`, prefix `plotnine_`) | `libs/utils/src/utils/engines.py:45-48` | read |
| The rule "own value, else the recipe's" | `effective_engine` returns the first level that writes the key; `tier_engine(recipe, body, tier)` reads the tier's own `data_engine`, else the recipe's | `engines.py:100-116` | read |
| The refusal words | "no library for this engine in this app (the engines of this app: ...)" | `engines.py:124-136` | read |
| The app's choice | `data_entry` picks the data engine of a tier, `plot_entry` the plot engine of a plot; one table of entries `REGISTRY` | `app/modules/engine_registry.py:35-61` | read |
| The entry files | `engine_python_polars.py`, `engine_python_plotnine.py` | `libs/transformer/src/transformer/`, `libs/viz_factory/src/viz_factory/` | read (files exist) |
| The engine of each registry entry | `ACTION_ENGINES` (68, all `python-polars`), `COMPONENT_ENGINES` (191, all `python-plotnine`); action names: 65 `polars_`, 2 `modif_`, 1 `step_`; component names: none prefixed | `transformer/actions/base.py`, `viz_factory/registry.py` | run: `PYTHONPATH=. .venv/bin/python -c` importing `app.modules.engine_registry`, then `Counter(ACTION_ENGINES.values())`, `Counter(COMPONENT_ENGINES.values())` |
| The checker | T06: an engine value the app has no library for, at any level; EN02: a step or layer in a block of another engine; EN03: a registered name with no engine | `libs/utils/src/utils/recipe_check.py:260-306` | read |
| Cache keys | "a key holds the engine of what it stores, and nothing else"; the plot engine is in no table key; the tier-3 engine is an argument of the plot's `s3` part | `app/modules/cache_keys.py:36-40` (module text) | read |
| Export record | `engine_record` writes the engines per table tier and per plot with library versions | `app/modules/engine_record.py:52`; `engines.py:60-73` (`engine_versions`) | read (signature and text only) |
| A new recipe | gets the first engine of each list | `libs/utils/src/utils/recipe_factory.py:161-162` | read |

One reading of the code that matters for BLUEPRINT (read: `engines.py:113-116`): a join's tier and a plot's tier 3 take their own `data_engine`, else the **recipe's**; they do not inherit the engine of the table or tier they read. With one engine this never shows. With two, a tier-3 step list under a plot whose target table runs in another engine would run in the recipe's default unless the user writes the key. Reading of this review, not decided: whether that is the intended rule.

---

## 3. What BLUEPRINT shows of it today

Nothing the user can see or choose. Confirmed by reading:

| Where | What happens | Evidence | Label |
|---|---|---|---|
| Plot preview | The recipe's `plot_engine` is passed to the dispatcher; the dispatcher picks the plot's own if written. The preview itself is not mounted on any page | `W:688-689` (`plot_engine_slot`); `04` section 3 | read |
| Save of a tier file | The file's `data_engine` line is kept when it was there; never added, never changed | `H:603-605` | read |
| Save of a plot | `plot_engine` is kept as one of the entry's own keys | `H:535` (docstring), `H:574-579` | read |
| The catalog of the picker and the forms | Filled from `ACTION_SCHEMAS` and `COMPONENT_SCHEMAS` only (`app/src/server.py:39-42`); the engine tables are not handed over; no catalog entry holds an `engine` key | `libs/blueprint_arch/src/blueprint_arch/schema_registry.py:39`; grep "engine" in `schema_registry.py`: none | read; run: after the import of `app.src.server`, `sum('engine' in v for v in catalog)` = 0 |
| New recipe | Writes the default engines; no choice shown | `H:2700` (comment), `new_recipe.py` | read |
| Validate | Runs the checker, so T06 and EN02 would be listed with the other problems | `H:2844` | read |
| TubeMap, rail, forms | No engine label anywhere | grep "engine" in `W` and `H`: only the lines above | read |

---

## 4. What "selectable" would need, level by level

Common to every level (reading of this review, not decided):

- **Show before choose.** Even with one engine, the user could see which engine runs each part (a label on the map node, on the rail, on the form). That is information, not a choice, and it costs no decision about a second engine.
- **The picker must use the engine field, not the name.** `modif_` and `step_` names carry no engine (D-0238), and the plot components carry no prefix yet. So a filter by engine has to read `ACTION_ENGINES` and `COMPONENT_ENGINES`, which today do not reach BLUEPRINT's catalog.
- **Forms are per engine.** A form is built from the `ui_schema` of an entry. A second engine brings its own entries, with their own `ui_schema`. Widgets that hold engine-specific text (the `expression` widget holds "a Polars expression as text", `libs/utils/src/utils/ui_schema.py:25`; the `dtype_picker` offers Polars type names) would differ per engine.
- **The checker already says when a step is in the wrong engine's block (EN02).** BLUEPRINT could show it on the step, not only in Validate.

### 4.1 The recipe level (`data_engine`, `plot_engine` at the top)

What changes when the user changes it: every block that does not write its own engine changes engine.

| Option | What the user sees | Pickers and forms | Steps already written | Pros | Cons |
|---|---|---|---|---|---|
| R1. Shown, not changeable in BLUEPRINT (choose only in "+ New") | The two engines in the info panel and in the new-recipe dialog | Filtered by the recipe engine | Not touched: the default cannot change after creation | Simple; nothing changes silently | A recipe written for one engine can never move; the user starts a new recipe |
| R2. Changeable, with a list of what it affects first | Before the change: the list of blocks that would change engine and the steps that would no longer fit (EN02 lines) | Filtered by the engine of the edited block | Kept as written; each step that no longer fits is marked; nothing runs until fixed | The user decides with the consequences in front of them (goal: "informs the user and does not choose") | A recipe can sit broken for a while; the list can be long |
| R3. Changeable; blocks that had steps keep their old engine written as their own key | The default changes; the existing blocks show the old engine as their own | As R2 | Unchanged; the app writes the old engine into each block that has steps | No result changes | The app writes keys the user did not write (a choice made for the user); the file grows |
| R4. Translate the steps to the new engine | - | - | Rewritten in the new engine | One click | **Changes results silently**: the exploration note lists Polars and R differences (a missing value in "greater than 2", rounding 2.675, missing keys in a join, category order); it also says "One spec is never drawn by two engines"; against the goal ("nothing changes a result silently") |

### 4.2 The tier level (`data_engine` on `tier1`, `tier2` of a table or a join, `tier3` of a plot)

| Option | What the user sees | Pickers and forms | Steps already written | Pros | Cons |
|---|---|---|---|---|---|
| T1. Not offered (tiers always use the recipe default) | The engine of the recipe on each tier, as a label | Recipe engine | - | Matches the note's advice "not now" for data engines | The format and the code already allow a tier engine (D-0250 built); a recipe written by hand can hold one that BLUEPRINT cannot show or change |
| T2. A tier engine chosen when the tier is empty only | An engine list on an empty tier; a label once steps exist | Tier engine | None exist | No step is ever in the wrong engine; simple rule | To change, the user empties the tier (or makes a new tier file) |
| T3. Changeable at any time, steps kept and marked | A list on the tier; EN02 marks on steps that no longer fit | Tier engine | Kept and marked | Informed choice | Same as R2 at a smaller scale |
| T4. A new tier file (copy) in the other engine, the old one kept until the user removes it | Two versions side by side | Per file | The old list stays as it was | Nothing lost; the user compares | Two files for one tier; which one the recipe uses must be visible; it resembles the branch mechanism (ADR-082 Q3) |

Specific to tiers (reading of this review): the cache key of a tier holds its engine (D-0240), so a tier engine change rebuilds that tier and the tiers after it. BLUEPRINT could say so ("the stored tables of this table are rebuilt once"). Tier 3 of a plot takes the recipe's engine, not the target's (section 2): with a second data engine this needs a visible rule.

### 4.3 The plot level (`plot_engine` on a plot entry)

| Option | What the user sees | Pickers and forms | Layers already written | Pros | Cons |
|---|---|---|---|---|---|
| P1. Not offered (plots use the recipe default) | Label only | Recipe plot engine | - | Simple | The format allows it (DEC53, built in `plot_entry`); D-0252 asks that a later engine is not blocked |
| P2. Chosen when the plot is created ("+ Plot") | An engine list in the new-plot dialog | Plot engine | None exist | Plots are where a second engine is most likely (the note: per plot "sound") | Changing later means a new plot |
| P3. Changeable, layers kept and marked | A list on the plot; EN02 on each layer of the other engine | Plot engine | Kept and marked; the plot is not drawn until fixed | Informed | A plot of mixed layers stays broken until fixed |
| P4. Translate the layers | - | - | Rewritten | - | Excluded by the note ("A translator from the plotnine spec to ggplot2 is what the exploration file itself warns against"); a picture changes without a word |

Specific to plots (reading of this review): the plot engine is in no table key (D-0240), so changing it rebuilds no table; only the picture changes. The data step of a plot (tier 3) is a data engine question (4.2), not a plot engine question.

### 4.4 What the pickers must filter, in one table

| Being edited | Engine that applies (as built) | What the picker should offer (reading of this review) | Source of the filter |
|---|---|---|---|
| Tier 1 or tier 2 of a table | tier's own `data_engine`, else the recipe's | actions whose engine field equals it, and whose context fits the tier | `ACTION_ENGINES`, the action's `context` |
| Tier 1 or tier 2 of a join | same | same | same |
| Tier 3 of a plot | tier 3's own `data_engine`, else the recipe's | same; the registry has no "t3" context (run: contexts t1 46, t2 65, assembly 36) | same; a t3 context would have to be defined |
| Layers of a plot | plot's own `plot_engine`, else the recipe's | components whose engine field equals it | `COMPONENT_ENGINES` |
| Plot defaults (`theme`, `palette`, `layers`) | the recipe's `plot_engine` (reading: defaults apply to every plot, but a plot may use another engine) | open: a default layer of one engine is meaningless on a plot of another | - |

---

## 5. What cannot be judged with one engine only

Each item is a question that has no test case today, because every block runs in the same engine.

1. **The hand-over between tiers of two engines.** Stored tables are Parquet; inside a run one engine passes a lazy frame. How a tier in engine B reads the output of a tier in engine A (types, missing values, category order) is not defined.
2. **Column type names.** `input_fields` types are Polars type names (D-0035, D-0057, document). A form for a second data engine would need its own names or a mapping.
3. **Expressions.** `polars_with_columns` takes Polars expression text (`pl.col(...)`). Another engine has another expression language; the `expression` widget, the checker's formula check (ST06, `recipe_check.py:742`) and the help are Polars-specific.
4. **Plot defaults across engines.** A theme or palette default written for one plot engine, applied to a plot of another (4.4).
5. **The audit.** HOME's audit writes `modif_filter` and `polars_drop` steps; in a tier of another engine those steps would be EN02. The note says the audit "could never be R" for T3 (document).
6. **The lineage walk and the plan.** HOME's plan of every place asks the engine for names and types (D-0325); a second engine needs the same capability, or BLUEPRINT's column pickers break for its tiers.
7. **Help, the agent's instructions, the docs.** All name Polars and plotnine objects (`config/ui/agents/blueprint_default.md`, `app/src/help/blueprint.md`).
8. **The prefix rule for components.** The `plotnine_` rename is decided and not built (D-0091); until it is, a component name says nothing of its engine and only the field does.
9. **Performance and errors of a second engine** (start time, error messages that must reach the user): the note measured nothing ("Not run: anything with ggplot2, dplyr or arrow").
10. **Whether the per-tier data engine is wanted at all.** D-0219's line keeps "a data-engine override per tier is a plan owed to her, not decided" as the review session's words, while D-0250 built the optional tier key.

---

## Not verified

- Nothing was run with a second engine; there is none.
- That the export record writes the engines as D-0248 says: only the signature and the module text were read.
- How the checker treats a `data_engine` on `tier3` in each profile: not run.
- Whether BLUEPRINT's Validate shows T06 and EN02 in plain words: not seen on a screen.
- The feature-extension notes (`.claude/design/feature_extension/r_backend.md` and others) were not read in detail.

## To decide (for the guide)

| # | Choice | Options | Blocks or is blocked by |
|---|---|---|---|
| E1 | Does BLUEPRINT show the engine of each part now, with one engine | yes (labels on map, rail, form) / no | independent; cheapest information |
| E2 | Where the engine can be chosen in BLUEPRINT | recipe only / recipe and plot / recipe, plot and tier (4.1 to 4.3) | blocked by E5 for the tier level |
| E3 | What happens to written steps when an engine changes | refuse / keep and mark / copy into a new file / translate (excluded by the goal unless she decides otherwise) | blocks E2 (every changeable level needs it) |
| E4 | How the picker gets the engine of each entry | hand the engine tables to BLUEPRINT's catalog / read them from the app's engine registry | blocks any filter by engine |
| E5 | Whether a per-tier data engine is wanted | the ledger line keeps it as "a plan owed to her, not decided" while the format allows it | blocks the tier level of E2 |
| E6 | Which engine a join's tier and a plot's tier 3 inherit | the recipe's (as built) / the engine of what they read | only matters with a second data engine |
| E7 | Plot defaults with several plot engines | one default per engine / defaults only for the recipe's engine | only matters with a second plot engine |
