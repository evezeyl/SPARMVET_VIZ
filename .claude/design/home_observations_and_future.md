# HOME redesign: am I blocked? Observations on the model, and the future (2026-11-12)

**Written for:** Eve, to read later, to know where things stand and that nothing is blocked. Evidence classes: **verified** (run or read in the code), **reasoned**, **idea** (not checked).

## 1. Am I blocked? No.

| What | Who | Needed when | Blocks anything? |
|---|---|---|---|
| Your review of the design text (reading list in the guide, section 3) | you | before the first code, by your own order of work | it gates the code, not the specification work; changes found later are folded in |
| The right panel in audit mode (what stays of Inherited nodes, filter inventory, pending badge) | you, with me | at the screen redraw | no |
| The configuration stage (names, web configuration, Import flag) | you | last | no |
| The stage-2 specification, the build plan, the recipe fixes R1-R4, the UML redraw | me | now | no |
Everything decided is in `home_audit_reading_guide.md` section 2 (47 items). Nothing is waiting for an answer from you.

## 2. Where my text is interpretation, not your words (check these first when you review)
1. **The caption and the attrition wording** (`home_audit_steps.md` 19): the examples of the caption sentences are mine.
2. **The hash model details** (`home_evidence/home_hash_model_2026-11-12.md`): the 128-bit parts, the labels (`E`, `rC`, `dC`, `a`, `s`), the record hash. You decided the series, the precise parts, the full-content data hash, the record hash, the retirement of `decision_hash`.
3. **The fail list** (5a point 19): the four kinds of failure are my list; you confirmed it.
4. **The recipe-shape table** (5a point 18): my scan of the 7 shipped recipes and my reading of what the audit does for each.
5. **The T3 container name and place** (`steps: {tier3: [...]}` at the plot entry): a placeholder name; the principle is yours.
6. **The popup** (own window, a read-only snapshot with a refresh button): the first host is my proposal; the principle (a window now, a panel possible later) is yours.
7. **`exclusions.tsv` columns** (11): mine.
8. **The user glossary entries** (`docs/user_guide/glossary_and_feedback.qmd`): my wording.

## 3. Observations on the current model (honest)
**What I think is strong.** One mechanism for every removal (a filter on a field, the lineage, ticks) with the key as information; T1, T2, T3 defined the same way with identity by key; the audit as the original recipe plus steps (re-runnable, so reproducibility and export come from the same object); the series key (readable, comparable part by part, free to compute); fail instead of warn; data-agnostic wording and engine declarations.
**What worries me, in order.**
1. **Size.** 47 decisions and about 20 build tasks. The risk is building the whole before any value is delivered. **Suggestion: a walking skeleton:** one step kind (a filter), at T1 of one table, through the whole path (compile, audit recipe, keys, run, attrition, export, import), before the screen is polished. Several early packages deliver value alone: the missing-value rule (#63), unknown keys and the load gate (fail instead of warn), the dataset tier-2 fix, the recipe graph, keys per node.
2. **Verified facts the design depends on:** the T1 key is one key for the whole recipe; a dataset's own tier-2 is silently ignored (`ResFinder`); the validator reports nothing for unknown keys; removal at T1 of every table works with the unmodified engine; reopening the app reuses the stored tables; the Polars optimizer moves a filter only when provably safe.
3. **Reasoned, not yet tested (the first tests of stage 2):** audit T1 = the stored original T1 plus the steps equals running the exported audit recipe from the raw data; per-collection keys never miss an input (the property test is the gate); the cost of counting before and after at every step; the dry run on the column names is cheap for big recipes; the popup opens from a click without a pop-up blocker in every deployment mode.
4. **Risks I can name.** (a) The same field can have another type in another node (`2022` as a number or as text): the value is converted per node and a failure to convert is a warning; the canary `QA_year_types` is the test. (b) A step with a long list of values (thousands): size in the step record, the dialog and the key (the hash is fine; the screen needs a summary). (c) A renamed column breaks "the same field": the lineage does not track renames, the user chooses the new name. (d) The user pays the cost of many ticks on a big recipe: the dialog needs grouping and a search; "everywhere the field exists" is the default. (e) The recipe's formulas are code (`mutate` expressions): Import is gated, validated and uses an allowed list of operations. (f) The test migration (`TEST-ADAPT-1`) is large. (g) Reproducibility across machines depends on the engine versions: the declared engines and versions in the keys and the export help; a container is the real pin.
5. **Intentional limits of the first version.** One key family; no rename tracking; no stat cache (full content hash once per session); no multi-engine execution; a snapshot popup; the right panel decided later.

## 4. The future (nothing to build now; what to keep open)
| Direction | What would change | What to do now |
|---|---|---|
| **Another data engine** (for example `r-dbplyr`) | an action vocabulary per engine; the formulas of the recipe in another language; a handover at a node boundary through Parquet | the declaration (`data_engine`) and the failure on unknown values: done in the design |
| **Another plot engine** (for example `r-ggplot2`, `r-ggtree`) | the plot grammar is the same family; the output formats | the declaration (`plot_engine`), overridable per plot entry later |
| **Data that is not a table** (a phylogenetic tree, geometries, images) | a node has an engine and an ordered list of actions; each engine provides its own filter-like and drop-like actions ("prune these tips"); the stored format differs (Newick, GeoParquet); the entity key is the bridge between a tree and a table | keep the node model generic; keep the key declared; keep the key parts labelled by engine |
| **Maps** | geometries and a base map; no external tiles (ADR-071), so local tiles | nothing |
| **Interactive plots** | the output is HTML not an image; export must declare the output kind; "affected plot" stays data-based (the content hash of the data), which is an advantage | the engine registry (below) declares output kinds |
| **Pre-hash automation** | hash new data when it arrives, so a start is instant | later, after the build |
| **Provenance interchange** (idea, not looked up) | export the audit record in a standard form (W3C PROV, RO-Crate) for FAIR reuse | later; the record is already structured |
| **A second kind of entity** (patients and samples; genes) | more than one key family | covered for the hierarchical case by the attribute of the higher level; otherwise a later version |

## 5. The small engine registry (a sketch, not built)
**What it is.** A small table of the engines the software knows, kept as data (a yaml or a Python dict in `libs/utils`), never as branches in the code. The validator uses it for the failure on an unknown engine; the keys use it for the engine part and the versions; the export uses it for the output kinds; Blueprint uses it to filter its action and plot pickers.
**One entry:**
| Field | Example | Used by |
|---|---|---|
| `id` | `python-polars`, `python-plotnine` | the recipe, the validator, the keys |
| `role` | `data` or `plot` | the validator (a data engine in the plot slot fails) |
| `language` | python | information; the formulas of the recipe are in this language |
| `reads` | `table` (later `tree`, `geometry`) | the validator: the data kind a plot engine accepts |
| `actions` | a pointer to the action registry (data) or the grammar (plot) | Blueprint pickers, the validator |
| `outputs` (plot only) | `png`, `svg`, `pdf` (later `html`) | the export, the figure formats offered |
| `version_source` | the installed package version | the keys, the export |
| `status` | `built` or `placeholder` | the validator: a placeholder engine is refused until it is built |
| `constraints` | offline assets only (ADR-071) | the deployment checks |
**Why keep it small and later:** today it has two rows. It is needed when the second engine or the first non-table data kind appears. Until then the declaration plus the validator failure is enough, and the registry can be added without a change of the recipe format.

## 6. If you review: what I would do (a suggestion)
Read `spaces/HOME.md` first (one place, built or target, about 20 minutes) and mark anything that disagrees with what we discussed; then the eight items of section 2 above; the rest of the reading list is the detail behind HOME.md and can be sampled. The conversation decided the substance; the written text is my transcription, so the cheapest check is the one document that shows the whole.
