# Where does a column exist? Facts for the panel (scout survey of dev, READ only, 2026-11-20; digest by the coordinator)

## The question (Q-A4 of the coordinator's list; NOT decided)
The audit dialog must list, as tick lines, every place (table, tier, plot) where the chosen column exists, back to the roots and forward to every descendant. Today the map of a recipe knows the columns at only 35 of 85 places of the demo recipe; the other 50 are "unknown" (never guessed).
The owner's words (2026-11-20): "This is why the lineage back and forth is done - In audit we should work on a copy of the recipe - Have the coordinator verify but I think that should be done by tracking the columns for the lineages as it should be anyway tracked for the filters to offer the scope for the filters to the user for choice - The coordinator can use agents blueprint architect, data scientist and user - I want possible solutions with pros and cons."
Her standing rule: study, not effort. Build time is no argument.

## DECIDED (ledger, taken by the owner)
- D-0022: one mechanism for every removal = a filter on a field; the lineage shows where the field exists; tick lines.
- D-0093 (refines D-0053): the lineage offers the nodes; the USER ticks the nodes where a step is written.
- D-0175, D-0196: a filter can only be created in a view whose table has the column; she cannot tick a place that does not have the column.
- D-0176: a step that names a column that does not exist gives a plain message everywhere, naming the step, the column and a fix.
- D-0194, D-0316: every candidate place is ticked when the dialog opens; rows and plots affected are shown before she confirms.
- D-0195: "The whole lineage must really be searched and found when the audit dialog lists the nodes: no silent failure."
- D-0031: one recipe graph in libs/utils; no shim, no half fix.
- D-0034: `output_fields` and `final_contract` are removed; a table's published columns are its last tier-1 select.
- ADR-105 point 2 (DECIDED, not built): the software lists every node of the lineage where the field exists; what is ticked is written, nothing else.
## CONFIRM (written in a design file, no ledger line)
- `home_audit_steps.md:310`: "the software knows the columns of every node".
- `home_stage2_mechanism_spec.md:120` (an agent's proposal): a node's columns come from the stored schema or a dry run on the column names, never from computing the data.
## OPEN
- How the columns of each place are known (this question).

## The map today (`libs/utils/src/utils/recipe_graph.py`)
- Columns are known from the declared `input_fields` of a source table (303-318), through row steps (filter, sort, unique, head, ...; 326-327), a `polars_select` of plain names (328-333), a `polars_drop` of names when already known (336-341). Every other step makes the columns "unknown" with a reason (342-345). An unknown place is never listed by `nodes_with_column` (356-359).
- A join's output is unknown even when both inputs are known (317, 342-345).
- 43 actions that keep the names (cast, fill, round, string changes in place, the 12 aggregations, ...) are treated as unknown today only because they are not on the short list.
- Knowledge comes back only at a later select of plain names. A name with a space or a dot in a select is treated as unknown (120-124).
- The map has a hook `columns_provider` (283-287, 432), asked only for unknown places, meant for "a dry run on column names, a stored schema". No caller passes one.

## The 68 registered actions, by what they do to the column NAMES (scout's reading of each action's code)
1. Keep the names exactly: 43.
2. Names fully given by the step's own arguments (rename mapping, drop, select, new column named by an argument, a join adds the other table's columns with a suffix on a clash, unpivot, with_columns, group_by with named outputs, horizontals): 19 + the 3 "fixed shape" ones (group_by, describe, group_by_dynamic) = 22.
3. Names depend on the input's columns or dtypes, not on values: unnest (the struct's field names); select or drop by pattern (`*`, `^...$`); unpivot without `on`.
4. Names depend on the DATA VALUES: pivot (one column per distinct value). One action.
5. Cannot tell from the code: rolling. One action.
The action forms mark which arguments are INPUT column names (`column_selector`), but nothing marks the arguments that NAME an output column (`mapping`, `named_exprs`, `named_aggs`, `target_column`, `new_column`), and no field describes the output columns.

## The engine (Polars)
- The whole build is lazy end to end (ingestion `scan_csv`/`scan_parquet`, every tier step, the joins, tier 3). Polars can give the names and types of a lazy plan without reading rows (`collect_schema()`); the app already does this in about 20 places: the filter dialog's column list (`filter_and_audit_handlers.py:821`), the per-plot presence check that decides "SKIPPED" today (863-905), the tier-3 step check (`orchestrator.py:492`), the validator (`data_analysis_recipe_validator.py:519`, comment "collect_schema() only plans the query").
- Not schema-only: pivot, sample and describe read the rows while the plan is built (`polars_calls.py:333-336`); a few checks read some rows (float-to-integer cast check, sort-order check for time joins, self-join row counts).
- It needs the data files to be present (their header is read). HOME always has them. Blueprint may build a recipe before the data exists.

## Stored tables
- A parquet file exists only for the END of tier 1 of each table and the END of tier 2 when it has steps; nothing for the steps in between, nothing for tier 3, nothing before a plot was first opened. Their schema can be read from the file footer without rows.

## Who needs the columns
- The audit dialog (slice C): the tick lines. Today's dialog asks the data's schema per plot, not the map.
- The audit run: finds a step that names a missing column by trying the marked steps in a scratch folder (`audit_run.py:189-217`).
- The checker: one check reads the map's columns (J08); there is no general "this step's column exists" check from the recipe alone; the data check runs each table's tier-1 steps on one row and does not cover joins.
- Blueprint: shows declared fields; join preview types come from the stored data.

## Blueprint and columns today (second scout, READ, 2026-11-20)
- Blueprint's column pickers offer the DECLARED `input_fields` of the table (or of the plot's target, or of a join's merged ingredients): `app/modules/wrangle_studio.py:1979-2053`, `app/handlers/blueprint_handlers.py:672-723`, `data_analysis_recipe_navigator.py:605-657`. No picker reads the data.
- Nothing in Blueprint follows the columns step by step: after a rename, a new column or a join, the next step's form still offers the same declared list. Apply does not check that the chosen column is in the list.
- The Join Designer shows declared names; types and key overlap come only from a real build of each side ("Preview"); without data: names, and "No preview yet".
- The tube map and the lineage rail show no columns. The contract viewer lists the declared fields upstream; its downstream side is always empty.
- Blueprint calls none of the map's column functions; it uses the map for structure only.
- Where nothing is declared the picker shows "(no upstream columns)".
So: Blueprint does not depend on the answer to this question today. It would only gain from rules per action later (a picker that follows a rename), which is a Blueprint improvement of its own.

## Facts that limit each approach
A. Rules per action in the map (tracking from the recipe alone): needs no data; works in Blueprint. Each of 68 actions must state what it does to the names, and a wrong statement shows a wrong place without any error. Cannot be exact for pivot (values), unnest (types), patterns, rolling, and a join's suffix on a name clash needs both sides known. Types are not tracked, only names.
B. Ask the engine for the schema of the lazy plan at each place (names AND types, what the engine will really produce): exact by construction, nothing to keep in step with the actions. Needs the data files. Three actions read rows while planning (so a recipe that uses pivot costs a real read up to that step). Gives nothing when the data is absent (Blueprint before data).
C. A full dry run on the real data: exact, also finds errors that only the rows show; costs a run; needs the data.
D. Read the stored tables' footers: exact, free, but only tier ends that were already built; no intermediate step, no tier 3.
E. Combinations, for example: B in HOME through the map's existing provider hook, A in the map as the fallback where no data is at hand, and a test that A and B agree on every shipped recipe and every action's own example (so a wrong rule fails a test instead of showing a wrong place).
