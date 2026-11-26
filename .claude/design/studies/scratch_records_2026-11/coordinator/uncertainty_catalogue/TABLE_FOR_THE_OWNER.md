# Where the app cannot trace a column, and why: the catalogue (study, 2026-11-21)

Study only. Nothing in the repository was changed; the scripts and their outputs are in `scratch/` beside this file.
Decisions this study serves: D-0449 ("Right now od go for B"), D-0450 ("Sorry do not get wrong results because we did not select the correct scope"); her answer of the evening, ledger D-0460 (a line the app cannot trace is red and cannot be ticked, for now).
Labels: RUN = run on the real engine (Polars 1.40.1, the app's own code, tmp folders only). READ = read at file:line. REASONED = inferred, not run.
Names of keys and sentences written below are PROPOSALS, yours to change.

## 1. Summary, in plain words (10 lines)

1. Silent changes first. Six things change a table with NO message today, each run: (a) a formula over "all columns" gives other numbers after any column drop; (b) two tables with a same-named column: dropping the first one makes the second one's values appear under the same name; (c) a left join keeps the row of a removed sample (empty cells) when you remove it at the second table only; (d) a filter written on values you saw AFTER a step that rewrites or recomputes them removes nothing; (e) a step that keeps "the first 3 rows" or "rows without any empty cell" pulls other samples in after you remove one; (f) a plot silently leaves out rows with an empty number.
2. Your two questions. Formula over all columns: not a bug. "All columns" means the columns that exist at that step, so one column less gives another result, in Polars and in R alike; the app cannot see it because it does not read formulas. No shipped recipe uses such a formula.
3. Same-named columns of a join: Polars keeps the first table's name as it is and calls the second table's column `lab_right` (R gives `lab.x` and `lab.y`, both renamed). Drop `lab` on the first table and the second one takes the plain name `lab`, with no error. One shipped recipe (the demo) has such a join; it is protected by chance (a later step names the column and fails with a plain error).
4. The 5, 8 and 15 are three different counts, all right: 5 = places a walk with no engine plan cannot follow but the plan shows to be join keys, in 2 recipes (the review of 2026-11-20); 8 = the same count over all 7 shipped recipes (3 more in `1_Abromics_general_pipeline`); 15 = places the app cannot follow EVEN WITH the plan, demo recipe only. Without the plan the walk would call 173 places uncertain; with it, 15.
5. The 15 demo places: 6 end as the intended table, 9 as a plain error, none as a silent change (run). All come from one kind of step, the "unpivot" (wide to long).
6. Everything the app cannot trace comes from ONE of four causes: a step it does not read (48 of the 68 actions; 15 of them make the column vanish or change type and are the real red cases, the other 33 keep the name and the type and are ticked with a note), a join it does not follow (anti, right, full, as-of, on conditions), a failure of the engine's plan (none in the shipped recipes), or a column twice in one table (none shipped).
7. In the 7 shipped recipes only the demo has red lines for a row removal, and only 14 of its 99 plot-table columns (year, n50, total_length, largest_contig, L50, ST), all behind two unpivots.
8. Your use case, removing a bad sample by its key: 0 red lines in all 7 recipes (16 `sample_id` columns of the demo's plots, all ticked at tier 1, 2 and 3). Run on the demo, "remove from all the data": the sample is gone from all 27 tables that hold it, every plot table too, and no other row is touched, EXCEPT two tables that compute over all samples (a z-score of 41 other samples changes, a sample count goes down by one). That is the meaning of removing a sample, but nobody tells the user.
9. What can still touch you: the left join (only if you untick places), the two computing tables, the 6 tables where the key passes a step the app cannot read (the sample WAS removed there, in the run, but the app cannot prove it), tables no join links to the key, and rows a plot leaves out.
10. Not covered by "red where the app cannot trace": all six silent cases of line 1 are about steps the app CAN follow (the line is ticked). Red would not change them.

## 2. Part 1: her two questions

### Q-A. "Formula over all columns: a bug or a reason?"

Answer: a reason. It is the defined meaning of the formula, in Polars and in R. It is not a bug of the app and not a bug of Polars.

RUN (`scratch/qa_all_columns.py`, `qa_more.py`; table of 5 rows `sample, a, b, c` with a drop of `c` upstream; `scratch/qa_all_columns.out`):
| Formula (what it means) | With `c` | After dropping `c` upstream |
|---|---|---|
| `pl.sum_horizontal(pl.exclude('sample'))` (every column but one) | 111, 222, 333, 444, 555 | 11, 22, 33, 44, 55, no error |
| `pl.sum_horizontal(pl.all().exclude('sample'))` | same | same |
| `pl.sum_horizontal(pl.col(pl.Int64))` (by type) and `cs.numeric()` | same | same |
| `pl.col('^[abc]$')` (by name pattern) | a, b, c | a, b |
| `pl.nth(2)` (by position; after dropping `a`) | column `b` | column `c` (another column) |
| `pl.first()`, `pl.last()` (no argument) | last = `c` | last = `b` |
| `pl.struct(pl.all()).hash()` | hashes | other hashes |
| a row filter `~pl.any_horizontal(pl.all().is_null())` | rows s1, s4 | rows s1, s3, s4 (a row comes back) |
| `polars_drop_nulls()` with no subset | rows s1, s4 | rows s1, s3, s4 |
| `polars_unique()` with no subset | 3 rows | 2 rows |
| `pl.col('c')` (named) | works | plain error: unable to find column "c" |
On the real engine (`scratch/silent_cases.py`, case C1 and C2): a table total 111, 222, 333 became 11, 22, 33 with no error, and the rows kept by an "any empty cell" filter went from s1, s2, s4 to s1, s2, s3, s4.

What Polars says (docstrings of the installed package, `help(pl.all)` and the others): `pl.all()`: "If no arguments are passed, this function is syntactic sugar for `col("*")`"; `pl.col`: "Use the wildcard `*` to represent all columns"; `pl.exclude`: "Represent all columns except for the given columns"; `pl.nth`: "Get the nth column(s) of the context"; `pl.first()`: "returns an expression that takes the first column of the context". The "context" is the table at that step. Nowhere does it say "the columns the table had at the start".
In R (REASONED, dplyr is not installed here, nothing run): `across(everything())`, `across(where(is.numeric))`, `c_across(...)`, `select(-c(x))` are evaluated on the columns present at that step of the pipe. Same behaviour: remove a column upstream and the row sum changes with no message.
Why the app cannot see it: it reads only the names a step writes, never the formula (D-0356; `libs/utils/src/utils/step_effects.py:5, 20`). The formula check refuses formulas for SECURITY (names that run code or read files), not for meaning: `pl.all`, `pl.exclude`, `pl.nth`, `pl.first`, `pl.last`, `pl.struct` are on its allowed list (`libs/utils/src/utils/formula_check.py:55-58`, READ).
Hidden "all columns" without any formula: steps with no `subset`: `polars_unique`, `polars_drop_nulls`, `polars_drop_nans` (RUN above).

Shipped recipes that use such a formula (search of every `named_exprs`, `exprs`, filter and plot text of `config/data_analysis_recipes/` (143 yaml files with the included ones), `assets/gallery_data/`, `app/tests/equality/recipes/` and the transformer test pairs, for `pl.all`, `pl.exclude`, `cs.`, `pl.col(pl.`, `pl.nth`, `pl.first`, `pl.last`, `pl.struct`, regex names, `*`; RUN): NONE. Two steps hide an all-columns rule: `polars_unique` with no subset at step 10 of `VirulenceFinder` in the demo and in `1_Abromics_general_pipeline` (`scratch/clashes.out`); an audit step is written AFTER step 10 of that table, so a drop there cannot change it. One more case exists only in test pairs of the transformer (the horizontal actions name their columns).

Options for the app (consequences, no recommendation):
- a1 Nothing more: the standing sentence of the branch warning ("a formula that takes all columns ... will compute on one column less"). Cost: nothing; the user must remember it.
- a2 Refuse such formulas in recipes (a checker rule). Cost: removes a legitimate Polars use ("sum of all numeric columns"); changes the recipe format; reconsiders what a recipe may say.
- a3 Detect by name in the formula text and mark the drop line red or put a note. The formula check already walks the formula as syntax (`formula_check.py`), so finding `all`, `exclude`, `nth`, `first()`, `last()`, `col("*")`, `col("^...$")`, `col(<type>)` is small. It reconsiders D-0356 (the app would read formulas, for information only). It cannot catch the hidden all-columns steps without a subset (those are action arguments, not formulas) unless added by name too.
- a4 Compare the tables before and after the audit step and say what changed that nobody asked for. The app already builds the audit copy (`app/modules/audit_run.py`): the comparison would also catch the same-named join, the "any empty cell" filter and `drop_nulls`. Medium; it says WHAT changed, not why (RUN: `scratch/demo_remove.py` compares 52 tables in seconds).

### Q-B. "Two columns of the same name in a join: what does Polars do?"

RUN (`scratch/qb_joins.py`, tables A(k, lab, x) and B(k, lab, y), key `k`; `scratch/qb_joins.out`):
| Join kind | Columns after the join | Rows |
|---|---|---|
| left | k, lab, x, **lab_right**, y | 4 |
| inner | k, lab, x, lab_right, y | 3 |
| full | k, lab, x, **k_right**, lab_right, y (key kept twice) | 5 |
| right | lab, x, **k**, lab_right, y (key taken from the second table) | 4 |
| semi | k, lab, x (second table's columns not copied) | 3 |
| anti | k, lab, x | 1 |
- The first table keeps the plain name; the second table's column gets the suffix `_right`. The `suffix` parameter changes the suffix (`suffix='_B'` gives `lab_B`). The key is merged into one column in left, inner and right; `coalesce=False` keeps `k_right` for left too, and full needs `coalesce=True` to merge (RUN).
- dplyr (REASONED): a non-key name in both tables is suffixed on BOTH sides, `lab.x` and `lab.y` (parameter `suffix=c(".x", ".y")`); the plain `lab` no longer exists, so a later `lab` stops with an error. In Polars the plain name stays and keeps meaning the first table's column, so a later `lab` works silently.
- The silent change (RUN, case C3 of `scratch/silent_cases.py`): drop `lab` on the first table before the join. The join sees `lab` only once, so it is not renamed: the second table's `lab` keeps the plain name. The table after the join: columns k, x, lab, y; `lab` = [B1, B2, None] where it was [A1, A2, A3]; a plot that reads `lab` draws the other table's values, with no error. dplyr gives the same result in this case (REASONED: only one table has `lab` at the join, so no suffix).
- Any signal from the engine? Yes, two weak ones. (1) A column that nobody dropped disappears: in the run the table after the join lost `lab_right` (names compared before and after the audit step). (2) If the two columns have different types, the type of `lab` changes (RUN: String to Categorical). With equal types and a plain name there is no other trace. The app's walk already knows the first signal as data (`clash_no_longer`, `lineage_walk.py:683-689`, RUN: the walk of a drop of `lab` carries it); but the same walk also writes `plot_uses_column` for this plot ("the plot cannot be drawn", `lineage_walk.py:690`), which is false here (the plot IS drawn, with the other table's values) (review of the branch, must-fix 1; RUN here).
- Shipped recipes with a join whose two inputs both carry a same-named non-key column (the app's own plan, every join step of the 7 recipes, 29 joins; `scratch/clashes.out`): ONE, in the demo: step 4 of the join `Summary_phenotype_length_fragmentation` (left join of `Summary_quality`): column `ST` in both. A drop of `ST` at `Summary_quality` (the second table) ends as a plain error (RUN, place 7 of the 15 below). A drop at the first table was not run. Joins in the 20 recipe files of `config/data_analysis_recipes/` and `app/tests/equality/recipes/`: 28 left, 13 inner (41 joins); none uses `suffix`, `coalesce`, `validate` or `nulls_equal`; none is a self-join (RUN, `scratch/clashes.py` and the self-join rule `join_keys.self_join`).
Options for the app (no recommendation):
- b1 Nothing.
- b2 A note on every drop of a column that a later join renames around (the data exists today; the dialog does not exist yet).
- b3 Refuse the drop. Would also refuse harmless drops.
- b4 Require an explicit `suffix` (or a rename) in the recipe when a join has a same-named non-key column (a checker rule). Fixes it at the source; touches the demo recipe once.
- b5 Compare the plans before and after and say plainly: "the column `lab` now comes from table B; `lab_right` is gone" (cheap with the plan in hand; also catches the type change).

## 3. Part 2: the catalogue

Built from the code (every reason code of `lineage_records.py:53-58` and `:66-79`, every provisional note P1 to P17 of `lineage_walk.py:19-53`, the unsure codes of `remove_from_all.py:84-99`), then added: what the reports found and what I ran.
Letters in column "touches": F = row filter (removal by value), D = column drop, K = removal by key, A = "remove from all the data". "Walk" = the lineage walk. Outcome words as asked: HARMLESS / PLAIN ERROR / SILENT CHANGE.

### 3.1 The settled counts (RUN, `scratch/places.py`, `places.out`, `places.json`)

| Recipe | places (table, column) | uncertain with the plan | uncertain with NO plan | refused as join key (with plan / no plan) | no-plan uncertain that the plan shows to be a join key |
|---|---|---|---|---|---|
| 1_test_data_ST22_dummy (the demo) | 438 | **15** | 122 | 11 / 7 | 4 |
| demo_abromics | 29 | 0 | 16 | 2 / 1 | 1 |
| 1_Abromics_general_pipeline | 62 | 0 | 29 | 5 / 2 | 3 |
| 2_test_data_ST22_dummy | 80 | 0 | 0 | 3 / 3 | 0 |
| 3_test_no_joins | 9 | 0 | 6 | 0 / 0 | 0 |
| figshare_integration | 102 | 0 | 0 | 3 / 3 | 0 |
| stress_test_master | 25 | 0 | 0 | 0 / 0 | 0 |
| Total | 745 | **15** | **173** | 24 / 16 | **8** |
- "5 places" (review of 2026-11-20, finding F2) = the 5 of the last column in the first two rows plus `demo_abromics` (4 + 1): `FIVE` in `app/tests/test_plan_composer.py:56-58`. The review looked at 2 recipes.
- "8 places" (the builder, today) = the last column over all 7 recipes: the same 5 plus 3 of `1_Abromics_general_pipeline` (`MLST.sample_id`, `VirulenceFinder.sample_id`, `VirulenceFinder.VF_gene`). Same measure, wider search. With the plan each of the 8 is refused as a join key; without it they are "uncertain". Both numbers are right.
- "15 places" is another measure: places the walk cannot follow EVEN WITH the plan (the demo only; the other 6 recipes: 0). It is not a subset of the 8.
- 173 − 15 = 158 places are uncertain only because no plan was given: 8 turn into a join-key refusal and 150 turn out to be followable. Giving the plan always is the cheapest fix of all (the plan is composed from the build's own code, no data stored).
- Note: the main branch (`dev`) refuses these drops (gate P16); the branch `task/drop-uncertain-allowed` allowed them. The 15 were run on that branch's code, in tmp folders.

### 3.2 The 15 demo places (RUN, `scratch/demo15.py`, `demo15.json`)
| # | Table | Column | The step that loses it | A drop there ends as |
|---|---|---|---|---|
| 1-6 | Summary_quality | quality_module, taxon, genotype, phenotype, cge_phenotype, plasmid | the unpivot, step 5 of the join `Summary_phenotype_length_fragmentation`: keeps only its `index` and `on` columns | the INTENDED table: the column is gone, every other column equal, 0 plots affected (HARMLESS) |
| 7 | Summary_quality | ST | the same unpivot (it is in its `index`) | PLAIN ERROR: step 1 (a select) of the join `QA_ST_with_NA` fails |
| 8-10 | Summary_quality | genome_length, N50, contigs_sup300bp | the same unpivot names them in `on` | PLAIN ERROR: step 5 of `Summary_phenotype_length_fragmentation` cannot be built |
| 11-13 | Quast | n50, total_length, largest_contig | the unpivot, step 2 of `Quast_with_metadata`, names them | PLAIN ERROR: step 2 (unpivot) cannot be built |
| 14 | Quast | L50 | the same unpivot | PLAIN ERROR: a later cast names `L50` (column not found) |
| 15 | metadata_schema | year | the same unpivot (it carries `year` through) | PLAIN ERROR: a later filter names `year` (column not found) |
Totals: 6 intended, 9 plain error, 0 silent. The 6 intended are the cost of a red rule when the rule is applied to drops: a drop that would have worked.

### 3.3 The catalogue table

Frequency columns: "ship" = the 7 pipelines + 5 templates + 4 retest recipes (143 steps); "demo" = `1_test_data_ST22_dummy`; "test" = only in transformer test pairs or equality tests.

| # | What it is (plain words) | Why the app cannot follow it | Where it comes from | Touches | Places in shipped recipes and the demo (RUN) | Result today | What the user would see under her decision | Follow later: cost, and what is needed | Also changes a result for a step the app CAN follow? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | A step that melts or reshapes the table (unpivot, pivot, unnest, group by time, rolling) so the column is no longer a column, or is in another form | The step is outside the 7 steps the app may read (a decision, D-0351); the plan only shows that the name vanishes or changes type | `step_effects.py:53-61` (READINGS), `lineage_walk.py:235` and `_plan_links` `:296-318` (reason `step_not_read`) | F, D, K, A | ship: 3 unpivot steps, all demo; no pivot, rolling or group-by-time. Demo: 15 drop places, 14 plot-table columns for a filter (`walk_demo3.out`) | Drop: 6 HARMLESS, 9 PLAIN ERROR, 0 SILENT (3.2). Filter: the line is grey, nothing is written | Red, not tickable. The columns 14 of 99, none of them `sample_id` | Small to medium per action: a reading of its arguments (`on`, `index`, `values`) like the 7 existing ones; the closed list is a decision of hers (D-0351), adding one is a new decision | No: the red line writes nothing |
| 2 | A step that makes the column one row or another type (count, null_count, mean, median, std, var, quantile, cum_count, str_split, list_slice) | Same as 1: the plan shows the type change or the vanishing | same as 1 | F, D, K, A | ship: none. test: all (1:1:1 pairs). RUN `unread_actions.out`: `count`, `null_count` retype every column; `mean/median/std/var/quantile` retype numbers | Not met in shipped recipes: no result | Red, not tickable | Small each (one reading each), or leave red | No |
| 3 | A step that keeps every name and type but changes VALUES or ROWS: fill_null, fill_nan, str_strip_chars, str_replace_all, str_extract, round, shift, cum_sum, interpolate, reverse, coalesce, dt_truncate, list_join; first, last, min, max, sum (collapse to 1 row); drop_nans, explode (rows); join_asof; describe | Outside the readings; the plan shows name and type unchanged, so the walk passes the column as CERTAIN with the note `unread_step_passed` (it cannot know if values changed) | `lineage_walk.py:300-309` (P2); registry run: 33 of the 48 unread actions are of this kind (3.4) | F, D, K, A | ship: `str_strip_chars` 6, `fill_null` 5, `explode` 4 = 15 steps. Demo: `unread_step_passed` on 2 to 34 ticked lines per walk | SILENT CHANGE. RUN (`silent_unread.out`): the user sees `G1` after `str_replace_all` and filters `G1` at the earlier table, which still holds `g1`: removes nothing, same table, no message. For the two shipped value-rewriting steps on the key (strip) the run on the demo removed the sample everywhere (3.4) | Ticked with a small note (not shown: the dialog is not built) | Cheap to show "values may have changed"; to follow the value, no (the formula is not read) | YES: this is the line it ticks |
| 4 | A step the app reads that writes the column under its own name from ANOTHER column (a recompute or an aggregate under the same name) | The app reads names, never formulas (D-0356) | `lineage_walk.py:290-294` (P3, P12), note `recomputed_here` / `aggregated_here` with `knows_source_of_values` False | F, K | ship: `polars_with_columns` 20 steps, group_by 4. Demo: notes `one_row_per_group_after_this_step` on 4 lines | SILENT CHANGE. RUN (`silent_cases.out` C7): tier 2 rewrites `grp` from `other`; the walk ticks T1, T2, T3 (note on T1); a filter on the T2 value written at T1 removes nothing | Ticked with a note | Cannot be followed without reading formulas | YES |
| 5 | The engine cannot give the plan at a place (a missing file, a step naming a missing column) | The plan is the authority; without it nothing is known below | `lineage_walk.py:222`, `:547` (`plan_failed`); `plan_composer.py` (a failure is a value) | F, D, K, A | ship: 0 of 745 places (RUN: no plan failure in the 7 recipes) | PLAIN ERROR (the engine's own sentence is carried) | Red | Not "followable": fix the recipe or the data | No |
| 6 | A join step whose reading disagrees with the plan (for example `coalesce: false`) | A reading of D-0351 is checked against the plan; a mismatch is grey, never guessed | `lineage_walk.py:232` (`reading_disagrees`); `step_effects.py:209` (`agreement_problem`) | F, D, K | ship: 0 joins with `coalesce`/`suffix`/`validate`/`nulls_equal` (41 joins). RUN C15: the join with `coalesce: false` made the lines at the join and below grey | Grey, not written (PLAIN) | Red | Small: read `coalesce` (and `nulls_equal`) | No |
| 7 | A column that is twice in one table (a table joined with itself) | Which of the two a step means is not decided (P7) | `lineage_walk.py:558` (`several_columns`) | F, D, K, A | ship: none (RUN: 0 self-joins in the 41 joins; the checker allows one and tells the user, `join_keys.py:166`, J12) | Grey | Red | Needs her decision (which column) | No |
| 8 | Joins other than left and inner: anti, right, full, semi, as-of, on conditions, cross | Only left and inner are followed (provisional O8); the study of 2026-11-21 found the rules for semi (4 small additions); the others need a rule of direction | `step_effects.py:64`, `:155` (`a join of kind ... is not followed yet`) | F, D, K, A | ship: 0 (41 joins: 28 left, 13 inner). test: as-of and on conditions in 2 transformer pairs | RUN (`join_kinds.out`): remove b on the SECOND table only: anti ADDS a row (rows 1 to 2, b appears); right and full KEEP b's row (empty cells). Removal on the FIRST table through a right/full join: the walk ticks it (the plan keeps the names) and the row stays: SILENT | Second-table lines grey (red); first-table lines ticked | Semi: small (4 additions); anti/right/full: a new rule each; as-of: no | YES for right and full through the first table (ticked, row kept) |
| 9 | The same-named column of a join (Q-B) | The walk reads the join (suffix) but not what a later `lab` means; it also writes a false plot sentence for this case | `lineage_walk.py:683-689` (`clash_no_longer`), `:690` (`plot_uses_column`) | D | ship+demo: 1 join (demo step 4) | SILENT CHANGE, RUN C3 (Q-B) | Ticked; the fact exists as data, no dialog yet | Small: the data exists; the sentence must be fixed | YES |
| 10 | A formula over all columns, by type, by position, a hash of all columns, and the steps with no `subset` (unique, drop_nulls, drop_nans) (Q-A) | The app never reads formulas (D-0356); the all-columns steps are action arguments the walk does not read | `step_effects.py:5, 20`; `formula_check.py:55-58` allows these names | D (any column) | ship: 0 formulas; 2 `unique` no subset (step 10, harmless) | SILENT CHANGE, RUN C1, C2, C9 (values, rows) | Ticked | Detect by name: small; follow: no | YES |
| 11 | A column dropped upstream that a later join reads as a key | Known: refused by place | `key_drop.py` (`DropFacts.refused`) | D | ship: 24 places refused with the plan (11 demo, 5, 3, 2, 3) | PLAIN refusal with the join named | Grey "key needed later" (not an uncertainty) | Done | No |
| 12 | A left join keeps the row (removal at the second table only) | Not an uncertainty of tracing: the walk follows it correctly; the join's meaning is the effect | not coded: the planned note is not built (`lineage_records.py` has no code for it; `lineage_semi_join/REPORT.md` flag 1) | F, K | ship: 28 left joins of 41 (with the equality tests). Demo: tables `*_with_metadata` | SILENT CHANGE when the user unticks places. RUN C4: s3 stays in the joined table with empty species and genes (4 rows before and after); a plot of the number of genes then leaves that row out with no word (row 22, from the earlier check, not drawn here); a count by species shows `None` as a group | Ticked; the count of rows removed per line (planned, D-0316) would show "0 removed here" (not built) | A note on the line (proposed in `tmpAI/panel/left_join_note/FOR_THE_OWNER.md`) | YES (it is a followed step) |
| 13 | Steps after `head`, `tail`, `slice`, `sample`, `top_k`, `bottom_k`, `gather_every`, `limit` (row position) | The walk treats them as "keeps the columns" (`ROW_STEPS`): certain, no note | `join_keys.py:39-40`; `step_effects.py:125-126` | F, K, A | ship: 0. test: all | SILENT CHANGE, RUN C5: remove s1 upstream of `head(3)`: still 3 rows, now s2, s3, s4 | Ticked | A note is cheap; changing the rule: decision | YES |
| 14 | Cross-sample computations (z-score, rank, count, mean per group, cumulative sums) | They are new columns or recomputed names: the walk does not tell the user that other samples' numbers change | row 4 | F, K, A | Demo: `QA_aggregated_no_key` and `QA_population_zscore` (T2 and T3 tables) | RUN (3.4): removing one sample changes the z-score of 41 other samples and a sample count by 1 | Ticked | A note "values computed over all rows will be recomputed": cheap; the real change is intended | YES (intended) |
| 15 | Tables that hold the key but no join links to the key | The walk follows joins and declared keys, never a name alone (D-0355); listed as `Outside` | `lineage_walk.py:784` (`Outside`); `remove_from_all.py:85` (`same_name_not_linked`) | F, K (not A) | Demo: 4 tables for `metadata_schema`, 9 for `Summary` listed as outside; `remove_from_all` reached 27 of 28 tables (the 28th has no sample column) | A tick of a line leaves the sample in these tables (D-0457: they are exported). "Remove from all the data" reaches them | Information only | Declare the key in the recipe | YES (the sample stays in the export) |
| 16 | Tables no plot reads | Not an uncertainty of tracing; the effect is seen nowhere on screen | `lineage_walk.py:515-517` (`unread`), D-0451, D-0457 | F, D, K, A | Demo: 6 tables (`Quality_metrics`, `Detailed_summary`, 4 joins) | A step there is in no plot; D-0457 plans to show them in the data preview | A line (D-0451), with a sentence | Done by D-0457 when built | No |
| 17 | The source file itself | A source file holds no list of steps (D-0332) | `lineage_walk.py:566-569` (`no_step_list`, P1b, P13) | F, D, K | every walk: 7 source lines for `sample_id` in the demo, 1 per table | Grey by construction | Red (always) | Not followable: nothing can be written in a file | No |
| 18 | A key kept in the key path through steps the app cannot prove (the "may stay" list of "remove from all") | The step IS written; the typed values may not match values rewritten on the way | `remove_from_all.py:97-99` (`values_unproved`) | A | Demo: 6 tables (Summary, Summary_quality, Detailed_summary, Quast_with_metadata, Summary_phenotype_length_fragmentation, QA_ST_with_NA) | RUN 3.4: in the 6 the sample WAS removed; the logic cannot prove it | The list shown before and after (built) | Medium: needs reading the steps on the way | Yes (maybe) |
| 19 | A cast changes the type of the key at another place | The walk follows it with a note `another_type_here` | `lineage_walk.py:284` | F, K, A | Demo: `sample_id` String everywhere (`option.types == ("String",)`) | `apply` refuses the whole removal if one value does not fit one table's type (READ `remove_from_all.py:347`) | Note | Done | No |
| 20 | A rename across tiers, a key under another name, a join suffix | Followed (P3, P4b): the line carries the name there | `step_effects.py:163-` | all | ship: 8 rename steps | HARMLESS (the line on the other side carries its own name) | Ticked with the hop shown | Done | No |
| 21 | A column recreated under the same name after a reshape | Followed as the same column only if the plan agrees; after an unpivot, `variable` and `value` are new columns | row 1 | D | demo | As row 1 | Red | As row 1 | No |
| 22 | Rows a plot leaves out (an empty number on x or y) | Not tracing: the plot library drops them with a console line only | `viz_factory.py:267`; `plot_rows_dropped/REPORT.md` | all | Demo: 0 of 18 plots lose a row (RUN by the earlier check, not repeated); ship: about 30 more plots, 0 | SILENT CHANGE in principle; 0 cases today | Nothing | Option B to E of that report | Yes, for any table |
| 23 | A restored session that holds such a step | The stored step is judged by the same gate at its place `T3:<plot>`; nothing is built from a plot, so nothing is refused | `session_manager.py:138-163` | D | Today the screen writes only at `T3:<plot>` | No notice; harmless today | Notice (option D of the branch report) | Small | No |
| 24 | The plan reads data while it is made (pivot, sample, describe) | The plan is not purely a recipe fact for these steps | `plan_composer.py:10-11` | all | ship: 0 | Unknown | - | - | - |

Rows 1 to 8 and 17 are the red candidates (the app cannot trace); rows 3, 4, 9, 10, 12 to 15 are silent cases the app CAN follow.

### 3.4 Which steps the app does not read (RUN against the registry, `scratch/registry.py`, `unread_actions.py`)
68 actions are registered. 7 are READ (`polars_cast`, `polars_drop`, `polars_group_by`, `polars_join` (left, inner), `polars_rename`, `polars_select`, `polars_with_columns`). 13 are "row steps" the walk treats as keeping the columns (`modif_filter`, `polars_bottom_k`, `polars_drop_nulls`, `polars_gather_every`, `polars_head`, `polars_limit`, `polars_remove`, `polars_sample`, `polars_slice`, `polars_sort`, `polars_tail`, `polars_top_k`, `polars_unique`). 48 are UNREAD. By what the plan shows after the step (each 1:1:1 test pair of the transformer, run; `unread_actions.out`):
- the column vanishes or changes type, so the walk cannot follow it (red): `polars_pivot`, `polars_unpivot`, `polars_unnest`, `polars_group_by_dynamic`, `polars_rolling`, `polars_count`, `polars_null_count`, `polars_mean`, `polars_median`, `polars_std`, `polars_var`, `polars_quantile`, `polars_cum_count`, `polars_list_slice`, `polars_str_split` (15);
- name and type unchanged, so the walk ticks it with a note: `polars_all_horizontal`, `polars_any_horizontal`, `polars_coalesce`, `polars_cum_sum`, `polars_describe`, `polars_drop_nans`, `polars_dt_truncate`, `polars_explode`, `polars_fill_nan`, `polars_fill_null`, `polars_first`, `polars_last`, `polars_interpolate`, `polars_join_asof`, `polars_list_join`, `polars_max`, `polars_min`, `polars_sum`, `polars_max_horizontal`, `polars_min_horizontal`, `polars_mean_horizontal`, `polars_sum_horizontal`, `polars_rank`, `polars_reverse`, `polars_round`, `polars_shift`, `polars_str_extract`, `polars_str_replace_all`, `polars_str_splitn`, `polars_str_strip_chars`, `polars_with_row_index`, `step_top_n_other`, `modif_join_where` (33; for `polars_join_asof` and `modif_join_where` the second table's columns are grey). Among them, first, last, min, max, sum collapse the table to ONE row and explode and drop_nans change the row count, with the names unchanged.
In the shipped recipes only 7 unread actions occur: `polars_unpivot` 3, `polars_str_strip_chars` 6, `polars_fill_null` 5, `polars_explode` 4, `polars_str_splitn` 3, `polars_unnest` 3, `step_top_n_other` 1 (`shipped_steps.out`).

### 3.5 The one run that answers "what changes when one sample is removed" (RUN, `scratch/demo_remove.py`, `demo_remove.out`)
Demo recipe, the app's own "remove from all the data" for ONE sample (id 10668076, present in all tables that hold the key). I compared every stored table (tier 1 and tier 2) and every plot's table (tier 3) before and after: 52 tables (28 tier 1, 7 tier 2, 17 plot tables).
- 48 of 52: only that sample's rows are gone, every other row and value identical, same order (27 tier-1 tables, 5 tier-2 tables, 15 plot tables). The sample is absent from all of them afterwards.
- 1 table has no sample column at all (`APEC_STEC_virulence_genes`, tier 1): unchanged.
- 4 tables change values for OTHER samples or count (the two computing tables, each as tier 2 and as its plot table): `QA_population_zscore` (the z-score `n50_zscore` of 41 other samples changes; 1 row removed) and `QA_aggregated_no_key` (the count `n_samples` changes by 1; no row removed, the table is one row per group). That is the arithmetic of removing a sample, but the user is not told which tables are "computed over all samples".
- The 6 tables where the app cannot prove the removal (row 18): the sample was gone from all 6.
- The step was written at 27 tables (the 28th has no key); 0 "not written".

## 4. Part 3: facts for her decision "which actions become red"

Not a design: facts per source. "How often" = shipped recipes / demo. "Bad" = worst outcome (silent first). "Cost" = to follow later.

| Source (row) | How often | Worst outcome | Cost to follow |
|---|---|---|---|
| Reshape steps, unpivot etc. (1) | demo only (3 unpivot steps, 15 drop places, 14 filter columns) | PLAIN ERROR or HARMLESS | small per action |
| Retyping/aggregating steps (2) | test only | none seen | small per action |
| Rewriting or collapsing steps, name and type kept (3) | ship: 15 steps | SILENT (filter on a rewritten value removes nothing) | note: cheap; follow: no |
| Recompute/aggregate under the same name (4) | ship: formulas 20, group-by 4 | SILENT | no (reads formulas) |
| Plan fails (5) | 0 | PLAIN | n/a |
| Reading disagrees (6) | 0 | PLAIN | small |
| Column twice (7) | 0 | grey | decision |
| Other join kinds (8) | 0 ship; 2 test pairs | SILENT for right/full first-table | semi small; rest new rules |
| Same-named join column (9) | 1 join in the demo | SILENT (if no later step names it) | data exists; fix the sentence |
| Formula over all columns, steps with no subset (10) | 0 formulas; 2 harmless `unique` | SILENT | detect by name: small |
| Join key needed later (11) | 24 places | PLAIN refusal | done |
| Left join keeps the row (12) | 28 left joins | SILENT if places are unticked | a note: small |
| Row-position steps (13) | 0 ship | SILENT | note cheap |
| Cross-sample computations (14) | demo: 2 tables | intended change, not announced | note cheap |
| Key not linked by a join (15) | demo: 4 to 9 tables per walk | the sample stays in an exported table | declare keys |
| Tables no plot reads (16) | demo 6 | the step is seen nowhere | built by D-0451, D-0457 |
| Source file (17) | every table | grey by construction | not followable |
| Rows a plot leaves out (22) | 0 | SILENT | options B to E |

### Silent today, for a step the app CAN follow (the red rule does not cover these)
1. A formula over all columns, and steps without a subset (row 10): any column drop (RUN).
2. The same-named column of a join (row 9): a drop of the first table's column (RUN); the walk even writes a false sentence for it.
3. A filter written on values seen after a rewriting or recomputing step (rows 3, 4): removes nothing (RUN).
4. A left join keeps the row (row 12): when places are unticked (RUN).
5. Steps that keep rows by position (row 13) and the computing tables (row 14): other samples change or enter (RUN).
6. Right and full joins through the first table (row 8): ticked, row kept (RUN, `join_kinds.out`).
7. Tables the key reaches only by name (row 15) and rows a plot does not draw (row 22).
All seven are visible to the user only if the planned "rows removed per line" count and a before/after comparison of the tables exist; neither is built (the HOME dialog is not built).

### Red today but harmless (the cost of the red rule to the user)
1. 6 of the 15 demo drop places (RUN): the drop ends as the intended table (Summary_quality, 6 columns the unpivot discards anyway).
2. For a plan-less walk, 150 of 173 uncertain places turn out followable (RUN): red for no reason unless the plan is given.
3. Source-file lines (row 17): red by construction; nothing could be written there anyway.
4. 14 plot-table columns of the demo for a row filter (year, n50, total_length, largest_contig, L50, ST): red at three places each (`T1:Quast_with_metadata` or `T1:Summary_phenotype_length_fragmentation`, two plots' tables). Whether a filter there would have worked was NOT run (not verified); the same column stays ticked at its own source table, so the user can still write the step there.
None of these touches `sample_id`.

### Her use case: remove a bad sample by its key
- Red lines for a row removal on `sample_id` at tier 1, 2 and 3: 0 of 16 columns in the demo, 0 in the other 6 recipes (RUN, `walk_demo2.out`). A removal at `sample_id` crosses 3 to 34 unread steps with a note and still ticks.
- Run (3.5): sample gone from all 27 tables that hold it and from every plot table; no other row changes. Exceptions to say aloud: the two computing tables (41 z-scores change, one count changes), and the 6 tables where the removal cannot be proved by the logic but was real.
- What can still touch her: unticking places (the left join keeps the row of the sample at the second table), tables the key reaches only by name, rows a plot leaves out (none in the demo), the computing tables.

## 5. For you to decide (options, no recommendation; names and sentences are PROPOSALS)

1. Which of rows 1 to 8 and 17 become red, and does the rule apply to filters, drops and removals by key alike? (Today the walk's grey lines apply to filters and drops alike.)
2. Give the plan to every caller (proposal "always the plan"): 173 uncertain places become 15.
3. The silent cases of the second list: which get a note on the line (proposed: row 12, 13, 14, 3, 4), which get a before/after comparison (proposed name: "what else changed"), which nothing.
4. Q-A: a1 (standing sentence), a2 (refuse), a3 (detect by name), a4 (compare tables) or a mix.
5. Q-B: b1 to b5; b4 (a rule that a join with a same-named non-key column must name its suffix or rename) fixes the source and touches one shipped recipe.
6. The false sentence "the plot cannot be drawn" for a same-named column: fix before any dialog shows it (proposal: a separate fact "the plot reads the other table's column of that name").
7. Should "remove from all the data" tell the user that two tables compute over all samples (proposed sentence: "These tables are computed over all samples; their numbers for the other samples change: QA_population_zscore, QA_aggregated_no_key.")?
8. A proposed red sentence: "The app cannot follow this column here: a step the app does not read yet changes the table. Choose another place." (PROPOSAL)

## 6. Not verified

- dplyr: nothing run (the package is not installed); the R behaviour is REASONED.
- Polars 1.40.1 only. A newer Polars may change a default (the `suffix`, `coalesce`).
- The 15 demo drops were run on the branch `task/drop-uncertain-allowed` (the gate that allows them), in tmp folders; `dev` refuses them. The counts of 3.1 were run on `dev`.
- "Rows a plot leaves out" (row 22) and the join kinds anti/right/full in the app's walk were not re-run today: the first is from the earlier check, the second I re-ran only on plain Polars (`join_kinds.out`); the walk's own verdicts for these kinds come from `lineage_semi_join/REPORT.md` (RUN there).
- Whether a row filter at the 14 red demo columns would have worked: not run.
- The `no_step_list` count of 7 source lines per walk is for the levels "source, T1, T2, T3"; at T1 to T3 only it is 0.
- The gallery recipes hold no wrangling steps (34 bundles, 0 steps); their plots were not walked.
- No browser, no screen: "what the user would see" is the walk's output, not a dialog.
- Unread actions' effect was classified by the 1:1:1 test pairs (one table each); a real recipe can combine them.
