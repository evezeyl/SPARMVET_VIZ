# Panel BLUEPRINT step 4: viewpoint of the scientist and the data scientist (2026-11-21)

I recommend. I decide nothing. Evidence labels: **read** (file:line), **ran** (scratch script `tmpAI/panel/blueprint_step4/scientist_scratch/t.py`, main venv, Polars), **document**, **reasoned**.

## Summary (6 lines)

1. The biggest scientific risk for a user writing a recipe in BLUEPRINT is a step that keeps the columns and types right and changes the rows: the plan (names and types) cannot show it. I ran filter with NaN, cast, left join with duplicate keys and key with whitespace: the schema is the same or looks fine, the rows are not.
2. So the help that matters most is not a live column list. It is what each step did to ROWS (in, out, null, NaN, unmatched keys), on the whole table, before saving. This is not built (JOIN-COUNTS-1 is provisional and unbuilt, `tasks.md:136`).
3. The plan (HOME's `plan_composer`) gives the right columns and types after every step without reading the data, and it is the same code as the build. It is the right source for column pickers, with three limits: it does not exist for an unsaved step, a failure greys everything below it, and a few steps (pivot, sample, describe) read rows to plan.
4. The lineage in BLUEPRINT is useful for "where am I, what feeds this, what breaks if I remove this", but the lineage reads step NAMES only, never formulas (`step_effects.py:1-30`): it must not be shown as "this column comes from X" without that limit.
5. A preview on `head(10)` (BLUEPRINT today, `wrangle_studio.py:755`) hides rare groups, duplicate keys and NaN. A sample must never be silent.
6. Recommendation: B (live plan and step effects) as the spine, with C (lineage) as the way to move and to see consequences, and D (YAML) kept as a read-only view. Not A alone.

---

## 1. One realistic job, walked, with the questions a reviewer asks

Job: the shipped recipe `2_test_data_ST22_dummy` style: sample metadata + AMR gene table + plasmid table, inner joins on the sample id, count genes per class, a bar plot per class coloured by a metadata group. (document: `tasks.md:137` RECIPE-SCIENCE-1 records exactly this recipe: an inner join drops 4 of 42 metadata samples from the AMR table and 1 from the plasmid table with no message; the plot title says samples, the count counts gene rows: 70 against 38 samples.)

| Moment | What the reviewer asks | What BLUEPRINT can show today | What the user would not know |
|---|---|---|---|
| Table and fields | Which file, how many rows, which columns the recipe leaves out, which type is the sample id | Declared fields only; the undeclared file columns are computed by the ingestion and printed in a console (`ingestor.py:147`, document `03` 1.3), not shown | That the file has columns the recipe ignores (D-0374 says BLUEPRINT should tell) |
| Tier 1 step: filter, cast | Which samples were removed and why; how many; was a NaN or a null treated as I think | `head(10)` of the table after the step; a row count of the stored anchor file (`W:735-737`) | The counts before and after; NaN against null |
| Join | How many rows in, out; which sample keys unmatched; did any row multiply | A key match on DISTINCT keys (`join_designer.py:90-118`): matched, left only, right only, sample of 8 | Row multiplication: it counts distinct keys, so a right table with a duplicate key looks "matched" and the row count still grows |
| Tier 2, tier 3 | What is the unit of one row now (sample, gene, gene per sample) | Nothing for tier 3 (no form) | The unit of a row at each tier |
| Plot | Is the x axis discrete or continuous; what is counted | A form that offers declared columns | That an integer code (cluster 1,2,3) is drawn as a continuous scale because its type is numeric (reasoned; the dtype test is `pd.api.types.is_numeric_dtype` in `viz_factory.py:491` and `plot_config_resolver.py:476`) |
| Final check and save | What did I guarantee by saving; will it run on the next batch | Validate (profile `run`, see `04` L19); Save | See section 6 |

## 2. What I ran (all on messy data, `t.py`)

Data: ids `["S1","S2 ","s3","S4",None]`, x `[1.5, NaN, None, 2.7, 3.0]`.

| Case | Result (ran) | What the plan shows | Consequence for BLUEPRINT |
|---|---|---|---|
| `filter x > 2` | Keeps the NaN row (Polars treats NaN as greater than any number), drops null; 3 rows kept | The same schema as before | A threshold on a column with NaN keeps the NaN sample. The user must be told "n NaN, n null in this column; the rule keeps NaN, drops null" before saving |
| `filter x != 3.0` | Drops the null row, keeps NaN | Same schema | Operators treat null and NaN differently from each other; one line of counts shows it |
| cast float to Int64 with `strict=False` | 2.7 becomes 2, NaN becomes null, silently | `Int64` | The registered `polars_cast` is strict by default and "a truncation is never silent" (`polars_calls.py:393`, read); but the strict failure comes at run, not when the user fills the form. The plan composer does give the failure as a value, so a live plan could show it at the step (reasoned) |
| left join, right table has key `A` twice | 3 rows become 4 | `{id, v, w}` | Schema cannot show it. Needs rows in and out |
| keys `"S2 "`, `"s3"`, `None` against `"S2"`, `"S3"` | No match, no error | Same | Unmatched samples vanish with `inner`. The key match panel lists left-only samples (good) but only 8 |
| join key `Int64` against `String` | Refused at the plan (`SchemaError`) | The plan shows the failure | Good: the plan catches a type mismatch with no data read |
| `pivot` | Columns come from the DATA values | A plan needs rows | The plan is not data-free for pivot, sample, describe (`plan_composer.py` module text, read): the picker for a later step depends on the data file |
| `head(100)` of a table with a rare group of 2 rows in 1002 | The rare group is not in the sample | - | A preview on the first rows hides rare categories |
| zero rows after a filter | Schema kept, 0 rows | Same schema | The plan says everything is fine for an empty table: a zero-row count must be loud |

Not run: Polars tie order in `unique`/`group_by` (the action texts warn already, `polars_aggregations.py:17`), time joins, decimal rounding.

## 3. The approaches

Names: A forms first; B live plan and step effects; C lineage first; D text first.

### A. Forms first, a check on Apply and on Save

| | |
|---|---|
| What the user sees | Today's shape completed: a form per step; Apply shows `head(10)`; Validate on Save lists problems. New: table/field form, tier 3 form, visible Save |
| Facilities | Action picker and form renderer (exist: 68 actions, `ui_schema`; `04` 3.2); checker (exists, profile mismatch `run` against `build`); data glimpse (exists, head only) |
| Pros | Smallest change from what exists; beginner sees one thing at a time. Evidence: read |
| Cons | The user finds out what a step did only if they look at `head(10)`. The check is syntactic and structural: it cannot know a filter dropped 4 samples. The columns offered stay the declared ones (a step after a rename or join cannot pick the new column; `03` 1.1) |
| Silent risks | A filter or a join that changes rows is accepted and saved with no number shown. This is the exact failure the scientist cannot defend to a reviewer |
| Engine selectable | Forms are per engine (`ui_schema`); the checker is generic (EN02). The expression widget and type names are Polars-specific (`05` section 5) |

### B. Live plan after every step; rows and effects on demand

| | |
|---|---|
| What the user sees | Under each step card: the columns and types after the step (from the plan, no data read), plus a line "rows in, rows out, null, NaN in the columns this step touches" that the user opens (collects). A join card shows rows in left, rows out, unmatched keys left and right, and rows from duplicate keys. A failing step shows the engine's sentence at that step and greys the steps below (the plan's failure is a value) |
| Facilities | Plan of every place: exists (`plan_composer.py`, same code as the build, a test compares it with the built tables on shipped recipes: document in the module text). EXTEND: it takes a recipe on disk and an audit step (`compose_candidate_plan_book` is for an audit copy and refuses audit steps outside one); BLUEPRINT would need a plan of a draft in memory and of a recipe that has no plot yet (the loader refuses a recipe without plot, `03` row 18). MISSING: row counts, null/NaN counts per step (the plan has only names and types), join counts (JOIN-COUNTS-1) |
| Pros | Catches type mismatch and absent column with no data (ran: `SchemaError`). Column pickers follow the real columns (answers the parked item). The step effect card answers the reviewer's question before the save. One code with the build, so the picture equals the run |
| Cons | A collect of the whole table after every step costs time on big tables; it can be on demand and cached by step list. The plan fails on a recipe that does not yet run, so pickers go blank at the first error: the user needs the sentence, not an empty list |
| Silent risks | (1) A count on a sample instead of the table looks like the real one: label "all N rows" or "first n of N". (2) pivot/sample make the plan data-dependent: the columns offered can differ with another data file. (3) A picker that hides columns not in the plan can hide a typo the user would want to see: show "not in the plan" as a warning, not a block |
| Engine selectable | Plan is per engine ("a second engine needs the same capability", `05` 5.6). Generic: the card layout, the counts as a contract (rows, nulls). Per engine: how to count NaN (a concept of float in Polars; not every engine has it), types names |

### C. Lineage first (the map is the editor)

| | |
|---|---|
| What the user sees | The tube map; clicking a place shows what feeds it, its columns, and what depends on it; steps are added at a place; removing a step shows what downstream breaks |
| Facilities | Graph (exists; structure only, `recipe_graph.py`); lineage walk (exists, used by HOME only, 775 lines); plan composer (as B). EXTEND: walk on an original recipe (today the walk is built for an audit); show empty tier places, tier 3 (the map does not draw them, `04` 3.2) |
| Pros | Answers "where am I" (D-0308) and "what depends on this step" before a deletion: a good protection against a silent cascade. It reuses HOME's walk (one source) |
| Cons | It shows names, not values or rows: it cannot say that a step dropped samples. The walk reads NAMES of a compute step, never the formula, so "this column is recomputed" is known, "from which column" is not (`step_effects.py`, the link carries `knows_source_of_values` False, PROVISIONAL, D-0356). A join is read only for `left` and `inner`; others are `unread` (grey) |
| Silent risks | A lineage display that says "comes from table X" when a `with_columns` made it from another column misleads a reviewer. Must show the limit in words |
| Engine selectable | Graph generic; the walk reads a closed list of Polars action names (`READINGS`): a second engine needs its own list |

### D. Text first with assistance (YAML is the editor)

| | |
|---|---|
| What the user sees | The YAML; completion of action names and parameters from the registry; the checker underlines; plan columns on hover |
| Facilities | Checker (exists); registry for completion (exists); YAML escape hatch exists but its Save writes nothing (`04` 3.2) |
| Pros | The recipe the user sees is exactly the recipe saved, nothing hidden; good for a maintainer; comments can live in the text if the writer keeps them (D-0174, not built) |
| Cons | Not "no code" for a bioscientist (D-0306); the user still needs the effect of steps on rows; a typo in YAML syntax stops everything |
| Silent risks | Completion that inserts defaults (for example `strict`, `how: inner`) would make a choice for the user: show the default and say it is a default |
| Engine selectable | Completion per engine from the registry's `engine` field; the field does not reach BLUEPRINT's catalog today (`05` section 3) |

## 4. Recommendation

Combination: **B as the spine, C as navigation, D as a read-only view of what will be saved, A's forms as the way to write each step.** One approach alone does not answer the reviewer:

- A alone repeats today's gap: the user cannot see what a step did to rows.
- C alone cannot show rows or values.
- B alone does not say where a step sits or what depends on it.

Why from my viewpoint (science first): "the user sees what a step did to rows and types before saving" is the one thing that lets a user defend the figure. B gives types by plan (exists), rows by a count (new). The count is information only; it changes nothing, so it respects "the tool informs and the user chooses".

Parts I would ask for in the step effect card (information, no choice made for the user):

1. Rows in, rows out for every step, on the full table.
2. For a filter: rows removed, and null and NaN counts of the columns the rule reads, with the sentence "this rule keeps NaN / drops null" for the operator picked.
3. For a join: left rows, right rows, rows out, keys unmatched left and right (a full list on demand, not 8), right keys that repeat, and rows added by repeats. The existing key match on distinct keys stays but is not enough.
4. For a cast: the plan's type before and after, and a failure shown at the step.
5. For a plot mapping: the type of each mapped column and whether the plot treats it as discrete or continuous; an integer type used as a group gets a note.
6. At the end of tier 1: the samples (entity key values) that left the table, as a list that can be exported to the user's own notes (BLUEPRINT writes no audit, `DECIDED`; the list is shown, not stored).

## 5. What the saved recipe guarantees, and what a preview may hide

- The saved recipe guarantees: the same data file and the same recipe give the same rows and the same picture (`agent_principles.md` 2). It does not guarantee that the next data file has the same columns, the same sample ids with the same spelling, or the same groups; the load gate and the checker only test names and types declared (read: strict import refuses a declared slug that is not a column, `03` 1.3).
- A preview on the user's file shows what happened on that file. A figure that is correct for batch 1 can silently lose 5 samples on batch 2 (whitespace or case in ids). The count of "samples that entered, samples that left" is the only protection; BLUEPRINT is the place to show it when writing the recipe, HOME's audit when running it.
- Whether the saved recipe should carry a note of the data it was tested on (file name, rows) is a choice: it would be written history and BLUEPRINT never writes an audit (DECIDED). So it goes to "to decide", not to the design.

## 6. Pitfalls that would change a result silently or hide a step (flagged first)

1. BLUEPRINT today: Save rewrites the file from the step list, drops comments, may write `comment: <file name>` in untouched steps (`03` row 9, `04` row 152-153). A save with no edit changes the recipe file and with it the stored tables' keys. Existing, flagged in `03`. A helper approach that edits more must not make this worse.
2. BLUEPRINT today: the glimpse shows the row count of the STORED anchor file and `head(10)` (`wrangle_studio.py:735-755`); `processed_data_surgical` serves the stored parquet as-is for some component roles. I did not verify whether the table shown after an edited, unsaved step list is the result of the steps or a stored file with the steps applied on top (a double transform is possible, `wrangle_studio.py:614-617`). To check before any preview is built on it.
3. Any approach that auto-adds the final published `polars_select` (D-0034) or a sort or a cast to fix a plan failure would choose for the user. Show the fix, do not write it.
4. A picker that offers only plan columns, when the plan failed, can offer an empty list: the user may write the name by hand and nothing says why it fails. Show the failing sentence at the picker.
5. A lineage line "from table X" derived from names only (section 3C).
6. A count on a sample labelled as a count.
7. A engine change that "translates" steps (excluded by `05` 4.1 R4).
8. Tier 3 of a plot takes the recipe's engine, not the engine of the table it reads (`05` section 2): matters with a second data engine only.
9. Validate profile `run` against `build` (`04` L19): a user trusting "passed" does not know which gate HOME will apply.

## 7. Engine selectable: generic and per engine

| Generic (one design for all) | Per engine (must exist for each) |
|---|---|
| The card layout; the counts contract: rows in/out, nulls, join unmatched; the lineage graph and the picture of "where it sits"; the checker with codes; the rule "an engine without its library is refused" | The plan (names and types) and its failure sentences; the closed list of actions the lineage reads (`READINGS`); the `ui_schema` widgets (expressions as text, type pickers); the NaN concept (float NaN is not null in Polars; other engines differ: the exploration note lists missing values in "greater than 2" as a difference, `05` 4.1 R4); the count of null/NaN; help texts |

For the scientist the reproducibility consequence: a step list is an engine's own language. A recipe is reproducible only with its engine and library version (the export record lists them, `05` section 2). BLUEPRINT must show the engine of the part being edited (E1 in `05`), even with one engine.

## 8. To decide first (ranked)

1. What the user must be shown about rows before saving a step (the minimum: rows in/out; join counts; null/NaN of what a filter reads) and whether a count on the whole table is always allowed (cost on big tables), or a labelled sample. This sets whether BLUEPRINT is a place where a reviewer-ready recipe can be made.
2. The source of the columns after each step in BLUEPRINT (`04` To decide 6): the plan (needs the plan of an unsaved draft and of a recipe with no plot) against the declared fields. The plan is the same code as the build.
3. Which gate BLUEPRINT's check applies (`build`, `run`, both), because the "passed" word is the user's guarantee (`04` To decide 3).
4. Whether a tested-on note is part of a recipe (history in the recipe against BLUEPRINT never writing an audit).
5. What a save may change in the file (comments, `comment:` lines; D-0174 decided, writer not built): before more editing features are added.
6. Whether the unmatched or removed samples are listed to the user at the end of tier 1 (information only).
7. Which engine-level display comes first (E1 of `05`).

Can wait: names of the card, where in the screen, the form for tier 3 text, themes.

## 9. Not verified

- I did not run BLUEPRINT on a screen. Nothing about how it looks or whether the glimpse shows a stale table (section 6 point 2).
- I did not run `plan_composer` on a draft recipe, nor measure its time on a large table. The claims "same code as the build" and "a test compares it with the tables built" are from its module text (`plan_composer.py:1-30`), not from running `test_plan_composer.py` (no test suite was run).
- Row-count cost per step on real tables: not measured.
- My Polars cases are on small frames with the installed Polars; the engine's own actions (`polars_filter` and `modif_filter`) might wrap the operators differently (for example the NaN rule of the filter); I tested raw Polars, not the registered actions. A scratch run through the action registry would settle it.
- The discrete/continuous plot behaviour is reasoned from two dtype tests; I did not render a plot.
- Whether `compose_candidate_plan_book` can be generalised to a non-audit draft: read its signature only.
