# Actions and Polars: names, steps done at once, the whitelist (2026-11-13)

**Written for:** Eve (decisions) and the recipe session (the policy goes into the spec). Eve asked on 2026-11-13: stay aligned with Polars; check which action names already mean something else in Polars; actions that do several steps at once will go; what is the whitelist; Blueprint is not touched now but what changes must be recorded.

**Evidence labels.** VERIFIED = run by a probe (`tmpAI/architect/polars_names_probe.py`, `polars_wraps_probe.py`, `polars_names_bodies.py`). READ = the body of the action was read (25 of 67 actions: the ones named below). NOT READ = judged from the name only; each package reads the body before it changes the action. Counts of recipes are files that contain the word (`grep -l` in `config/data_analysis_recipes` and `assets/gallery_data`), comments included.

## 1. The whitelist

`final_contract` of a recipe. The rule (`rules_data_analysis_recipe_structure.md` section 5) calls it an exclusive whitelist: a column that is not listed is dropped. In the code it is `Orchestrator._apply_final_contract` (VERIFIED earlier today): it acts on Tier 1 only, a listed column that does not exist only prints a line, the types are not applied, and the order of its keys is the order of the columns (and part of the Tier 1 key). 6 recipe files contain `final_contract`; the Blueprint navigator reads it as a slot (`data_analysis_recipe_navigator.py:134, 456`). It is not `output_fields` of a schema (a second, different field).

## 2. Names against Polars

**Same name, but the action does something else** (VERIFIED by running or READ):

| Action | Polars | The action |
|---|---|---|
| `is_in`, `not_in` | `Expr.is_in` returns a true/false column | filter the rows (a filter, not an expression) |
| `value_counts` | `Expr.value_counts` returns a struct column | returns a new frame (value, count), first-appearance order; collects (not lazy) |
| `coalesce` | `pl.coalesce` returns a column | overwrites the first listed column |
| `percentile` | Polars has `quantile` for percentiles | wraps `Expr.rank`, returns rank / number of rows: the name is misleading |
| `rename` | `LazyFrame.rename(mapping)` | two forms (mapping, or columns + new_name); no `wraps`; a second action `rename_columns` exists |
| `sort` | `sort(by, ...)` | accepts `by` or the alias `columns`; always a stable sort |
| `sample` | no seed by default | seed 0 by default (ADR-090, a declared difference); collects |

**Same name, same meaning** (READ or by `wraps`): `drop_nulls`, `explode`, `unnest`, `unpivot`, `pivot`, `join` (takes a named ingredient instead of a frame), `cast`, `shift`, `interpolate`, `cum_sum`, `cum_count`.

**One Polars method, several actions** (VERIFIED, `wraps`): `LazyFrame.unique` has three (`drop_duplicates`, `unique`, `unique_rows`; the description of `unique` says "alias"); `LazyFrame.filter` has five (`filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `filter_range`); `Expr.is_in` two; `Expr.fill_null` two (`fill_nulls`, `fill_nulls_direction`); `Expr.over` two (`count_by_group`, `window_agg`); `LazyFrame.join` two (`join`, `join_filter`).

**Not a Polars name, so no conflict, but not the Polars word** (VERIFIED): `keep_columns` (Polars: `select`), `drop_columns` (`drop`), `drop_duplicates`, `unique_rows` (`unique`), `rename_columns` (`rename`), `fill_nulls` (`fill_null`), `round_numeric` (`round`), `summarize` (`group_by` + `agg`), `mutate` (`with_columns`), `strip_whitespace`, `regex_replace`, `regex_extract`, `null_if`, `replace_values`, `recode_values`, `z_score` and 24 actions in all without `wraps` and without a Polars name. All `wraps` entries resolve (0 broken).

## 3. Actions that do several steps at once (candidates; READ unless marked)

| Action | Steps done at once |
|---|---|
| `split_and_explode` | split a string, then explode to rows (two Polars methods) |
| `split_column` | split, pick parts, join the remainder into the last part, optionally drop the source; **returns the frame unchanged when the source column is absent** |
| `split_column_to_parts` | `split_exact`, rename the fields, unnest (a comment says it casts to Float64; it does not) |
| `top_n_other` | count, rank, join back, label the rest "Other" (about 8 Polars calls) |
| `derive_categories` | reads an external file and maps each row with a Python function (`map_elements`): not a Polars operation |
| `keep_columns` | select **plus** silently put the primary keys first |
| `drop_columns` | drop **plus** silently protect the primary keys **plus** silently ignore a column that does not exist |
| `summarize` | group and aggregate; an unknown `agg` is silently counted |
| `recode_values` | returns the frame unchanged when `column` or `rules` is missing |
| `label_if`, `window_agg`, `count_by_group`, `horizontal_stats`, `date_extract` | NOT READ (judged by size and name) |

## 4. How much would the shipped recipes change

Files that contain the word: `keep_columns` 7, `final_contract` 6, `drop_columns` 3. In the Python of `app/` and `libs/blueprint_arch`: `keep_columns` 0, `drop_columns` 17 (mostly the audit translator, `t3_translator.py:142`, and tests), `final_contract` 37 (the orchestrator, cache keys, export, tests). So the migration of the shipped recipes is small; the tests and the audit translator are the larger part.

## 5. Register: what Blueprint will have to change afterwards (Blueprint is NOT touched now; Eve 2026-11-13)

From grep, not read in full: the action picker and forms are built from `ACTION_SCHEMAS` (`ui_schema`), so renamed or new actions appear by themselves but their `yaml_example`, help and widgets must be right; the `dtype_picker` options list needs the integer type (3 hits of `dtype_picker`); `wrangle_studio.py:1735` checks an inline `final_contract`; the navigator reads `final_contract` as a slot (lines 134, 456); a trailing `select` step would replace the contract panel; the form of an `H1` role (`columns` list, `new_column`) is the widget `column_selector` plus the per-action table; spec-level `filters` of a plot (O9) and the tier-3 container need a form. Each item becomes a task when its recipe change lands.

## 6. Proposed order (a recommendation to Eve; nothing here is decided)

Reason for the order: a rename made before the action is strict would move the silent behaviour to a new name, and a migration made twice rebuilds every stored stage twice (one cache-version bump is the aim).

1. **Now, no recipe change.** Integer type in ingestion and `cast` (Eve decided yes), tests first (me). The checker side and the spec (recipe session).
2. **The step checker** `step_problems` (recipe session) and the table of action names (sections 2 and 3 above are the input). Eve decides the names.
3. **One migration** (recipe session tool, #83; me for the engine side): H1 renames, alias removal, new action names, plain strict `select` and `drop`, shipped recipes and tests adapted first.
4. **Run-time guard** (`ACTION-MUST-ACT-1`) and the `na` parameter on the filters (me), then the two `xfail` marks are removed.
5. **`final_contract` becomes a last `select` step** and is refused by the checker (O27, needs Eve's yes after 3).
6. **Tier-3 container read by the engine** (O9) with the audit build; then spec-level `filters` migrate to it.
7. **Blueprint** after 5, as its own package (section 5).

## 7. Second round (Eve's answers, 2026-11-13) and why the differing actions exist

**Eve's answers.** The whitelist (`final_contract`) is removed (not transparent); a `select` step replaces it. Actions that do several steps may stay when they are simple, unambiguous, well documented and every behaviour switch is an option. The real Polars actions are kept or added with all their parameters. What differs from Polars is renamed so that the name shows it. First understand why each differing action exists.

**Why they exist** (VERIFIED: usage counted in 28 action names over `config/data_analysis_recipes` and `assets/gallery_data`; git dates by `git log -S`; the intent of the author is NOT in any commit message, so "why" below is the use, not the intention):

| Action(s) | Use today | History |
|---|---|---|
| `is_in`, `not_in` | 0 steps in shipped recipes; emitted by the audit translator (`t3_translator.py:133, 136`) for the dialog operators "one of" and "none of" | added 2026-04-17, commit "add analytical cleaning actions" (no reason given) |
| `filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `filter_range` | `filter_range` 9 steps in 5 files, `filter_eq` 1; the others only through the audit translator (`t3_translator.py:120-130`), one action per dialog operator | one Polars method (`filter`) behind five names |
| `drop_duplicates`, `unique_rows`, `unique` | 2, 1 and 0 steps | `drop_duplicates` 2026-03-23 (a pandas name, a column subset), `unique_rows` 2026-03-25 ("adding unique rows decorator", all columns), `unique` = alias of `drop_duplicates` (it is the Polars name) |
| `keep_columns`, `drop_columns` | 7 and 2 steps; `drop_columns` also emitted by the audit translator (`t3_translator.py:142`) | the primary-key rules were added "to prevent join breakage" (docstring) |

**New findings of this round.** (1) The audit translator already knows each action's own keys (`filter_eq` takes `column`, `filter_gt` takes `columns`): that is the vocabulary split of H1, hidden in one place; after H1 the translator gets simpler. (2) `assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml` has `wrangling: tier3:` with an action `filter_rows` that is not registered (the engine reports "not registered"; the gallery only shows the preview image, so nobody noticed); the spec (section 7.7) already lists `wrangling.tier3` as disappearing. (3) The audit translator will become the step compiler (P5) and should emit the Polars-named actions.

**Check of Eve's point 5 (tier-3 container, O9) against the HOME decisions** (READ: `home_audit_steps.md` 5a-15 and the spec, line 392): it fits. 5a-15 gives every plot an optional T3 container at the plot entry (`steps: {tier3: [...]}`), any registered action allowed in the recipe, only filters, drops and removals in audit, an empty list = the previous key, a plot always reads its T3. A spec-level `filters` is then a T3 step of the maker; exploration filters stay out. One caution: the planned bug fix (HOME merges the author's `filters` with the exploration filters, `home_theater.py:498`) is useful only until the container is read; do it only if the container is more than one package away, otherwise it is built twice.

## 8. O10 formulas: the risk, the options (a recommendation to Eve)

**Facts** (VERIFIED by run or READ): the 6 formulas in 4 shipped recipes use only `pl.col`, `pl.lit`, `pl.when/then/otherwise`, `cast`, `str.strip_chars`, `str.to_lowercase`, `n_unique`, `over`: no `lambda`, no `map_elements`, no name outside `pl`. A recipe formula is passed to Python `eval` at three sites: `mutate` (`libs/transformer/.../expressions.py:221`, with `{"pl": pl}` as globals, which still reaches the Python built-ins), the ID-reconciliation `mutate` (`id_reconciliation/core.py:239`, same) and `stat_function` of the plots (`libs/viz_factory/.../geoms/core.py:1335`, `eval(fun)` with no restriction at all; the comment says "safe for developer-controlled recipes only"). A reproducibility bundle is verified by hash against its own record; that proves it was not changed, not that it is safe.

| Option | Keeps | Risk left | Work |
|---|---|---|---|
| A. Check the formula before running it (an allow-list: `pl.<known function>`, methods from a list of Polars expression methods, numbers, text, operators; no names, no `lambda`, no attribute starting with `_`) | every Polars formula, `str.to_lowercase` included | a mistake in the list; heavy computation is not stopped | one small module in `libs/utils`, used by the three sites, tested with attack cases (`__import__`, `().__class__`, `lambda`, `getattr`) and a mutation check |
| B. Remove free formulas; single-step actions instead (`lowercase`, `strip`, `when/then` through `label_if`) | the transparency of single steps | none from formulas | each formula of a recipe becomes steps; some Polars expressions have no step |
| C. User consent before running a recipe with formulas | nothing is lost | consent does not protect a user who cannot read the formula; an attacker only has to ask | a dialog |
| D. Block formulas now, solve later (A, B or a developer-only flag) | nothing runs | the 6 shipped formulas need a replacement first | small now, a stop-gap |

**Recommendation: A for all three sites (the third one is the worst today), then B step by step** where a single-step action reads better (ID reconciliation already has `lowercase`). C is not a defence. D only if A cannot be done before recipes from outside are accepted. In every case recipes of other people stay unverified until they pass the checker; the checker (`check_recipe`) is where option A is called, so the two belong in the same package.

## 9. Third round (Eve's answers, 2026-11-13) and what was checked

**Eve's answers** (recorded with the date; the sessions may discuss, only Eve decides):

| Point | Eve |
|---|---|
| Naming | Prefix AND registry field (`polars: exact / modified / composite / wrapper` + `wraps`): an action that is not Polars must be easy to see by its name; the registry field and the Blueprint display come in addition. Before renaming: check that each difference is deliberate and not an implementation error. |
| O7, O19 (`labels`), O11, O16, O1, O23 | yes, as recommended. |
| O25 (missing values in filters) | yes, but the default is **keep** (not remove). The recipe maker must choose, and the right choice depends on the data; we have no automatic solution. This is a known open limit and is written down as such. |
| Percentile | split. Composites: see the naming rule (kept if simple, documented, every switch an option). |
| Types | Why not follow Polars for the types? (section 11). |
| `filter_rows` of the gallery | fix, or search for a missed rename (section 12). |
| Gallery | the same rules as every recipe; no silent failure. |
| Name policy N1 to N6 | yes: one action per Polars method, with the exception of the special names (N7, N8: the recipe session appends). |
| O28 (two runs) | yes; tell Eve if a problem needs a new discussion afterwards. |
| O10 (formulas) | she wants a **security check**: that a bad recipe cannot do bad things (section 13). |
| Working mode | the two sessions may discuss up to 10 rounds, then present to Eve. |

## 10. Classification of the 67 actions (VERIFIED: every body read through `tmpAI/architect/actions_digest.py`, output `actions_digest.txt`; the column `polars` is the registry field Eve accepted)

Counts: **13 plainly Polars**, **10 Polars name but different behaviour**, **26 our own name for one Polars call**, **14 several steps**, **4 duplicates**.

| polars | Actions | Notes (all VERIFIED by reading the body) |
|---|---|---|
| `exact` (6) | `drop_nulls`, `explode`, `unnest`, `unpivot`, `pivot`, `scan_parquet` | only the parameter names differ from Polars (`columns` for `subset`); `pivot` collects (eager) |
| `wrapper` with the Polars name (7) | `cast`, `shift`, `cum_sum`, `cum_count`, `interpolate`, `all_horizontal`, `any_horizontal` | one Polars call, applied through `with_columns`, optional `target_column` |
| `modified`: Polars name, other behaviour (10) | `coalesce` (overwrites the first column), `is_in`, `not_in` (filter rows; Polars returns a mask), `value_counts` (returns a frame, first-appearance order), `join` (default `how` is `left`; Polars default is `inner`; order fixed `left_right`), `sort` (always stable, alias `columns`), `sample` (seed 0; default fraction 0.1; collects), `rename` (two forms), `sink_parquet` (writes metadata, returns a scan), `unique` (alias of `drop_duplicates`: keeps first, ordered) | see "deliberate or not" below |
| `wrapper`, our own name for one Polars call (26) | `add_constant`, `count_by_group`, `date_truncate`, `describe_stats`, `divide_columns`, `fill_nulls`, `fill_nulls_direction`, `horizontal_stats`, `label_if`, `list_join`, `list_slice`, `mutate`, `null_if`, `regex_extract`, `regex_replace`, `replace_values`, `round_numeric`, `select_by_pattern`, `split_to_list`, `strip_whitespace`, `window_agg`, `filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `filter_range` | hidden choices inside some: `strip_whitespace` also strips double quotes; `select_by_pattern` adds `^...$` itself; `replace_values` maps many old values to ONE new value; `divide_columns` casts both columns to Float64 |
| `composite`, several steps or own logic (14) | `date_extract`, `derive_categories` (external file + Python `map_elements`), `drop_columns` (protects keys, ignores a missing column), `keep_columns` (adds the keys first), `percentile` (rank divided by the row count: not a percentile), `recode_values`, `sanitize_column_names`, `split_and_explode`, `split_column`, `split_column_to_parts`, `summarize` (unknown `agg` counts), `to_struct` (struct, then drop), `top_n_other`, `z_score` | |
| duplicates (4) | `drop_duplicates`, `unique_rows`, `rename_columns`, `join_filter` | covered by `unique`, `rename`, `join` (how `inner` or `semi`) |

**Why there are so many renames (the answer to Eve's question).** They are NOT corrections of implementation errors. 26 actions are convenient names we gave to one Polars call (`fill_nulls`, `round_numeric`, `regex_replace`, `strip_whitespace`): they behave as Polars does, but their names are ours; only 13 actions carry a Polars name and behave like Polars. The count of renames is therefore decided by the rule, not by mistakes.

**Deliberate or accidental** (each difference of the 10 "modified"; evidence = ADR, description or code comment; the author's intention is NOT in any commit message):

| Difference | Verdict | Evidence |
|---|---|---|
| `sample` seed 0, `sort` stable, `value_counts` first-appearance order, `join` order `left_right`, `drop_duplicates` keeps first | DELIBERATE | ADR-090, code comments |
| `coalesce` overwrites the first column | DELIBERATE (documented) | the `description` field says so |
| `sink_parquet` metadata and scan | DELIBERATE (engine-internal) | docstring, ADR-024/031/089 |
| `is_in` / `not_in` filter the rows | USE is deliberate (the audit dialog operators); REUSING the Polars name is not | `t3_translator.py:133, 136`; added 2026-04-17 without a reason |
| `value_counts` returns a frame | order deliberate; the frame shape differs from Polars and is not described | `analytical.py:517-519` |
| `join` default `how: left` | UNKNOWN (no reason found; Polars default is `inner`); needs Eve | `data_assembler`, `join_action` |
| `rename` two forms, `rename_columns`, `join_filter`, `unique_rows`, `drop_duplicates`, `unique` | ACCIDENTAL duplicates, from history (three `unique` entries from 2026-03-23, 2026-03-25 and an alias) | `git log -S` |
| `sample` default `fraction: 0.1` | UNDOCUMENTED hidden default | `sample` body |
| `strip_whitespace` strips `"` too | UNDOCUMENTED hidden choice | body |

**A finding for the rule.** Where our default differs from Polars only to be deterministic (`sort` stable, `unique` keep first, `sample` seed, `join` how), another way keeps the Polars name: make the parameter **required** in the recipe (no default), so the recipe states it and the action is `exact`. Eve decides between this and `modif_` with a documented default.

**Three ways to name (counts from the table above; Eve decides).**

| Scheme | Renames | Result |
|---|---|---|
| 1. Eve's rule: prefix everything that is not Polars (`modif_` for one Polars call changed, `step_` for several) | about 50 (36 + 14) and 4 removed | every unprefixed name is Polars; each of our own names is marked |
| 2. Recipe session: prefix only where a reader could mistake the name for Polars, registry field for the rest | about 14 | smaller migration; the signal is in the field |
| 3. Toward Polars first: rename the 26 own one-call wrappers to the Polars name with the namespace written in the name (`fill_null`, `round`, `str_replace_all`, `str_strip_chars`, `dt_truncate`), then prefix only the true deviations (10 `modif_`, 14 `step_`) | about 50, but afterwards about 39 of 67 are exact Polars names | "no prefix means it is Polars" holds for most actions, which is what Eve wants |

Whatever the scheme, the registry field `polars` is added, and it is shown in Blueprint. Scheme 3 is my recommendation (it satisfies "most actions should follow Polars", and the prefix stays meaningful); it is a recommendation, not a decision.

## 11. Types: follow Polars? (VERIFIED by run, Polars 1.40.1)

- `cast` already uses the Polars names (`Int64`, `Float64`, `String`, `Boolean`, `Date`, `Categorical`; `expressions.py:78-85`). The `type:` of `input_fields` uses another vocabulary: ingestion casts only `numeric` (Float64), `categorical` and `string` (both String) and `date` (`ingestor.py:169-178`); `utf8`, `integer` and others are not cast at ingestion; the validator has a wider map (`metadata_validator.py:21-36`, with `integer` and `int` already) that disagrees: `categorical` is `Categorical` there and `String` at ingestion.
- So yes, we can follow Polars: one vocabulary for the type of a column in `input_fields` and in `cast`, the Polars names. This also removes the `categorical` ambiguity.
- Polars strict rules (run): a String `"2022"` casts to `Int64`; `"2022.0"` and `"2022.5"` FAIL naming the value; a Float64 `2022.5` cast to `Int64` is **truncated to 2022 without any error** (a silent science risk in the current rule "Float64 to Int64 to String"). A TSV with all whole numbers is already read as `Int64`, also with an empty cell.
- Recommendation: declare `Int64` and follow the Polars strict behaviour (a file that holds `2022.0` fails and names the value; the maker declares `Float64`, then casts). This is simpler than the earlier idea "accept `2022.0` as whole" and needs no special rule. Plus: `cast` from Float64 to Int64 must fail when a value is not whole.
- Migration: the shipped recipes use `numeric`, `categorical`, `utf8`, `date`; a mapping table is needed (what `categorical` becomes is Eve's decision: `String` is what ingestion does today). Registered as INT-TYPE-1 (amended).

## 12. `filter_rows` of the gallery, and the gallery rigor (VERIFIED)

- `filter_rows` was **never a registered action**: no `register_action("filter_rows")` in any commit. It appears only in `assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml` (`wrangling: tier3: - action: filter_rows, column: mic_value, operator: '>', value: 0`), added 2026-05-03 with the first gallery recipes (commit acbe48f0). It is an invented name, not a missed rename. The intended meaning is `filter_gt` on `mic_value` (value 0). It is the only gallery recipe that uses any `action:` at all.
- Nobody noticed because `generate_previews.py` does not run wrangling (no `wrangling`, `DataAssembler` or `materialize` in it) and `test_gallery_bundle.py` checks only the bundle files and the index. So the gallery recipes are never checked as recipes: the same silent failure Eve wants gone.
- Proposed (tasks GALLERY-RIGOR-1): run the same recipe checker (profile `gallery`) over every gallery recipe at index rebuild and in a test; fix `beeswarm_sina` (a real `filter_gt`, after checking that the preview image is unchanged, or removal of the dead block).

## 13. Missing values in the three filter paths (informational; probe `tmpAI/architect/missing_values_filters_probe.py`)

Frame: id 1 (A, 1.0), id 2 (B, 2.0), id 3 (missing, missing), id 4 (A, NaN). The filter actions, the HOME/audit filter rows (`_apply_filter_rows`) and the VizFactory `filters` give the **same rows** in all nine cases (`!=`, `not in`, `==`, `>`, `<`, `in`, range, on text and numbers):

- a missing value (null) is **dropped** by `!=` and `not in` (id 3 never appears), as SQL does;
- a NaN is treated as a number: it is larger than every number (so `> 1` and `!= 1` keep it) and it is dropped by nothing.
So the three paths agree today. The open point is semantic (Eve's O25): "keep the missing rows" is not what any path does now; the `na` option would add it, with default `keep` as Eve decided, which CHANGES today's results for `!=` and `not in` (the golden baseline measures this).

## 14. Security: what a recipe can make the app read, write or run (first inventory, VERIFIED by reading; not yet attacked)

| Site | What a recipe can do | State |
|---|---|---|
| `mutate`, ID-reconciliation `mutate`, `stat_function` | run Python (`eval`); `stat_function` has no restriction | option A (formula check) agreed by both sessions; Eve wants it verified |
| `sink_parquet` | write a Parquet file to ANY path the user can write (`os.makedirs` and `write_parquet(path)`; no confinement) | open; O11 says allowed for tests; needs a confinement or a refusal in the checker |
| `scan_parquet`, `derive_categories` `reference_file`, data source `path` | read any path the user can read (the content then appears in tables and exports) | open; needs a rule: paths relative to the deployment locations, no absolute path, no `..` |
| `!include` | `os.path.join(dirname(recipe), included_file)`: `../..` and an absolute path read any YAML or text file (`config_loader.py:56-58`); a parse error may show part of it | open; needs confinement to the recipe folder |
| bundle import (zip) | `bundle_importer.py` extracts files; zip-slip not yet checked | TO VERIFY |
| report.qmd of an export | labels and reasons from a recipe are written into a Quarto file the user renders; a code cell in a label could run | TO VERIFY |
| YAML | `SafeLoader` everywhere (no object construction); aliases can still expand (memory) | low; TO VERIFY with a test |
| regex | Polars uses the Rust regex engine (no catastrophic backtracking) | believed safe; TO VERIFY |
| agent adapter (`subprocess` of the `claude` CLI) | recipe text reaches an LLM prompt in Blueprint (developer app features only) | out of the HOME scope; note |

## 15. Recount under the conditions of the recipe session (N9 b: an exact name only for a wrapper that equals the Polars call with all its parameters; a hidden choice gets `modif_` and becomes an option; a result change never travels with a rename). ESTIMATE from the bodies read; each exact name still needs its equality test.

| Outcome | Actions (old names) | Count |
|---|---|---|
| Keep the name; complete or require the parameters (no hidden default) | `drop_nulls`, `explode`, `unnest`, `unpivot`, `pivot`, `scan_parquet`, `cast` (plus the Float to Int guard), `shift`, `cum_sum`, `cum_count`, `interpolate`, `all_horizontal`, `any_horizontal`, `join` (`how` required), `sort` (`maintain_order` required), `sample` (`seed`, `n` or `fraction` required), `rename` (mapping only), `coalesce` (`target_column` required), `list_join`, `list_slice`, `unique` (`keep`, `maintain_order` required; absorbs `drop_duplicates`, `unique_rows`) | 21 |
| Rename TO a Polars name (exact after the test) | `fill_nulls` to `fill_null` (absorbs `fill_nulls_direction`), `round_numeric` to `round` (decimals required), `regex_replace` to `str_replace_all`, `regex_extract` to `str_extract`, `split_to_list` to `str_split`, `date_truncate` to `dt_truncate`, `describe_stats` to `describe`, `horizontal_stats` to `sum_horizontal` / `min_horizontal` / `max_horizontal` / `mean_horizontal`, `drop_duplicates` to `unique`, `keep_columns` to `select`, `drop_columns` to `drop`, `percentile` to `rank` plus a `mutate` | 12 |
| `modif_` (one Polars call with a choice that becomes an option, or a documented difference) | `divide_columns` (casts), `replace_values` (many to one), `select_by_pattern` (adds the anchors), `strip_whitespace` (strips `"`), `null_if`, `sink_parquet`, `value_counts` (a frame); and two merges: `filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `filter_range`, `is_in`, `not_in` become ONE `modif_filter` (column, op, value, na), and `count_by_group`, `window_agg` become ONE `modif_over` | 16 old names, 9 resulting actions |
| `step_` (several Polars calls) | `date_extract`, `derive_categories`, `recode_values`, `sanitize_column_names`, `split_and_explode`, `split_column`, `split_column_to_parts`, `summarize`, `to_struct`, `top_n_other`, `z_score`, `label_if` | 12 |
| Removed as a duplicate | `unique_rows`, `rename_columns`, `join_filter`, `fill_nulls_direction` | 4 |
| Undecided | `add_constant` (`with_columns` plus `lit`), `mutate` (`with_columns` with a text formula) | 2 |

Names that change or disappear: about 44 of 67; names kept: 23. This is not the "about 14" of the first estimate because the difference between schemes 2 and 3 is mostly the 26 own wrappers: 11 of them go TO a Polars name, which counts as a rename but removes a difference. The migration of the shipped recipes stays small (filter_range 9 steps in 5 recipes, the rest 1 to 3 steps each; section 4).

## 16. Answers to the recipe session on paths (VERIFIED by reading and grep)

- **Five location keys:** `raw_data`, `data_analysis_recipes`, `cache`, `user_data`, `gallery` (`config/deployment/local/local.yaml:13-27`). `resolve_paths` (`filesystem.py:41-50`) prepends the deployment's `project_root` to every relative location; without `project_root` a relative path stays relative to the process working directory (the repository root when the app starts there).
- **A recipe path is NOT resolved against a location.** `source.path` goes to `Path(source_path)` (`ingestor.py:74`) and `orchestrator.py:368`: relative to the working directory. The 38 shipped values are `./assets/test_data/...` (31 + 3) or `assets/...` (4) (project-root relative; no absolute path, no `..`), and they repeat the `raw_data` prefix of the local deployment (`assets/test_data/`), so a rule "relative to `raw_data`" would refuse every shipped recipe. In production (`discover_by_dataset_id`, `orchestrator.py:97, 365-367`) `source.path` is ignored and the file is found by the dataset name inside `raw_data` (`find_file`, recursive glob).
- **`reference_file`:** one shipped use, `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:7`, `config/references/amr_phenotypes/test_amr_categories_phenotype.tsv` (project-root relative; not under any of the five locations). One more in the test fixture `libs/transformer/tests/data/derive_categories_data_analysis_recipe.yaml`.
- **`sink_parquet` / `scan_parquet`:** no shipped recipe and no gallery recipe. Four test fixtures in `libs/transformer/tests/data/` (`persistence_test_data_analysis_recipe.yaml`, `scan_parquet_data_analysis_recipe.yaml`, `sink_parquet_data_analysis_recipe.yaml`, `tier2_branch_test.yaml`). The engine itself calls `action_sink_parquet` and `pl.scan_parquet` with paths it builds from the `cache` location (`orchestrator.py:143, 190, 196, 291, 330, 337`), never from the recipe; `data_assembler.py:50, 132-156` also lets an assembly step name `sink_parquet`.
- **So the caller's allowed roots** for a recipe path are not "the five locations": the shipped data lives under `assets/test_data/` and a reference under `config/references/`. A rule has to state the base (project root, with the allowed sub-folders of the deployment) and is a decision for Eve and the recipe session.

## 17. Fourth round (Eve's answers, 2026-11-13) and the interaction check

**Eve's answers.** (1) The 10 actions with a Polars name must behave as Polars. If a special behaviour was wanted on purpose, it becomes either a separate modified action, or (better) it is written in the recipe. (2) The 26 own wrappers get the Polars names; the namespace written in the name (`str_replace_all` style) is acceptable: "then all is specified, clearer, fewer problems". (3) The "deliberate" differences are bad choices: they exist because of a tweak (the id column first, protected from dropping) that is a good rule but must be optional in the recipe; the recipe should be reorganised so that the id is set at the beginning; tweaked actions must behave as Polars and the recipes are adjusted. (4) Transparency: a hidden choice is not allowed; every choice is written in the recipe. (5) Naming: `polars_` for every action that is Polars, plus the registry fields (MY READING of "we rename all polars_ for what is polars and your fields"; to confirm).

**Consequences, applied as recommendations (nothing built).**
- The prefix then marks the class on every name: `polars_<name>` (is the Polars call), `modif_<name>` (a Polars idea with a documented change), `step_<name>` (several calls). No unprefixed action name remains. The registry field `polars: exact | modified | composite | wrapper` stays, and Blueprint shows it.
- `modif_` shrinks. Defaults that exist only for determinism (`sort` stable, `unique` keep first, `sample` seed, `join` how) become required recipe parameters: ADR-090 stays satisfied (the recipe states the order rule) and the action is exactly Polars. ADR-090 needs a wording change (the rule moves from action defaults to required parameters checked by the checker).
- Hidden choices go into the recipe: `strip_whitespace` strips `"` (becomes an explicit `characters`), `select_by_pattern` anchors (the maker writes `^...$`, which Polars already reads as a regex name), `sample` fraction 0.1, `round` decimals 2, `str_split` separator `,`, `dt_truncate` every `1mo`, `divide_columns` cast, `replace_values` many to one: each becomes a required parameter or a visible explicit step. This also removes the case for a default in `na` (O25): by Eve's rule `na` is required on every filter (my reading; she earlier said default keep).
- `coalesce` (overwrote the first column) becomes `polars_coalesce` with a required `target_column`: the maker writes the first column's name when that is meant.
- `polars_is_in` gives a mask column (as Polars); row filtering by "one of" and "none of" is `modif_filter` (ops `in`, `not_in`). `value_counts` (a frame) is not Polars: a `step_` with its order written, or the maker uses a group-by and a count.
- `scan_parquet` and `sink_parquet` stop being recipe actions: they are engine functions (security: refused in recipes; no shipped recipe uses them).

**The id-first tweak, where it comes from (VERIFIED).** `is_primary_key: true` on a field of a schema; `DataWrangler` puts the list in `rule["__metadata__"]["primary_keys"]` (`data_wrangler.py:193-196`); `keep_columns` puts these first and adds them when missing, `drop_columns` refuses to drop them and prints a warning (`core.py:320, 349`), the code dates from 2026-04-07. The shipped `keep_columns` lists already name `sample_id` first (QA_AMR_per_sample, MLST, VirulenceFinder, ...), so removing the tweak changes a table only where a list lacked the key; run B finds those cases by a dry run and writes an explicit `select` with the key first. The "good rule, optional in the recipe" becomes a recipe-level choice (an optional checker rule, for example "the primary key is the first column after tier 1"), designed by the recipe session.

**Interaction check: were the 26 names chosen because of an interaction?** Partly yes, and these places spell action names as strings, so a rename must change them (VERIFIED by a scan of `app`, `libs`, scripts outside the action files and tests):

| Place | Names it spells |
|---|---|
| audit translator `t3_translator.py:120-142` | `filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `filter_range`, `is_in`, `not_in`, `drop_columns` |
| `data_wrangler.py:75, 153-154` | `join`, `join_filter`; the list of actions that create columns: `mutate`, `add_constant`, `regex_extract`, `divide_columns`, `unpivot` |
| `data_assembler.py:42-50, 156, 187` | `join`, `join_filter`, `select`, `filter`, `rename`, `drop`, `mutate`, `sink_parquet` |
| Blueprint `wrangle_studio.py:354, 770`, `blueprint_handlers.py:2053` | `join`, `join_filter` |
| Test Lab bootstrapper (`bootstrapper.py:77`) and ID reconciliation (`id_reconciliation/core.py:163-178`) | `strip_whitespace`, `cast`, `regex_replace` |
| `orchestrator.py`, `data_assembler.py` | `sink_parquet` |

So the migration needs a test that no action name is spelled outside the registry, and these places should read the names from the registry (or one constants module), not from strings.

**A finding of this check (VERIFIED by run).** `id_reconciliation/core.py:165` suggests the step `{"action": "regex_replace", "pattern": "_", "replacement": "-"}` and `core.py:172, 178` the same key, but the action reads the key `value`: run on `S_1` it gives `S1` (underscore deleted), with `value` it gives `S-1`. The suggested "swap delimiter" step does the wrong thing if it is used as a recipe step; `{"action": "lowercase"}` (`core.py:161`) is not a registered action. Whether these suggested steps are ever consumed by the transformer is NOT verified. Registered as ID-RECON-STEPS-1.

## 18. Fifth round (Eve's answers, 2026-11-13)

**Eve's answers.** (a) The id-first rule is a recommendation to the recipe maker, optional, done through steps written in the recipe; NO code enforces it, NO verification of it; the recipe must work without anyone assuming that the id is the first column. (b) `polars_` reading: yes. N14 (Polars parameter names win in `polars_` actions): ok. Coding: wait. (c) `with_columns`: yes (so `polars_with_columns` with a mapping, `add_constant` removed). (d) Column order: the recipe adjusts the order after reading (a step), ingestion imposes no declared order. (e) Types: `categorical` is a tweak; follow ALL Polars types in the wrapper of the Polars library. (f) Paths: check whether containment is needed for the gallery; a default data path for testing is convenient: find a good way to give the data path. (g) The merges: she did not understand; explained in the chat (evidence below).

**Consequences (recommendations).**
- The optional `checks:` mapping of O32 (`entity_key_first`, `entity_key_kept`) and the function `columns_at_each_node` are NOT needed for it. Run B does not need a dry run either: `keep_columns` puts the keys first by a fixed rule (`list(dict.fromkeys(pks + columns))`, `core.py:343-352`), so the migration can write the explicit `select` from the lists alone; a key named in a `drop_columns` list is removed from the list by the tool (the action ignored it, with a warning), keeping the table identical. `columns_at_each_node` stays a possible later tool for "a step names a column that does not exist" (not decided, not built).
- Types (VERIFIED by run, Polars 1.40.1): `Categorical` IS a Polars type; our `categorical` meant String at ingestion (`ingestor.py:169-178`) and Categorical in the validator: a tweak. The Polars way is to give the declared dtype to the CSV reader (`schema_overrides`): it parses `Int64`, `Float64`, `Boolean` (`true`), `Date`, `Datetime`, `Time`, `Categorical`, `String` from text, and fails strictly and names the value (`2022.0` into `Int64`: "could not parse `2022.0` as dtype `i64` at column 'i'"). A plain `cast` from text does NOT work for `Boolean`, `Datetime`, `Time`, `Duration`, `Decimal`, so the type of an `input_field` should be handed to the reader, not cast afterwards. `Enum` (fixed ordered levels, which fixes the axis order in plots) needs its levels; `Decimal` its precision. A Categorical key does not join with a String key: the join FAILS loudly (`SchemaError`, VERIFIED), it does not go silent. Detail to settle: today a sanitiser (strip, null sentinels) runs on text BEFORE the cast; the reader's own `null_values` and the sanitiser must be kept in one defined order.
- Gallery (VERIFIED): a gallery recipe has no `source.path`; it has `data_path: example_data.tsv` (relative to its own bundle folder) and the preview script and `GalleryManager` read that file themselves. So the path rules of the engine do not apply to the gallery; the gallery profile of the checker needs only: `data_path` is a plain file name inside the bundle folder (no `/`, no `..`).
- Data path for pipelines (VERIFIED): `source.path` is today relative to the working directory and repeats the `raw_data` prefix; in production it is ignored and the file is found by the dataset name inside `raw_data`. Options in the chat. Recommendation: the path in the recipe is relative to the `raw_data` location of the deployment; the testing fallback is a deployment (the local and retest deployments already point `raw_data` at `assets/test_data/`); a test passes its own folder.

## 19. Polars methods and the registry (Eve's question 2026-11-13: "is there a select in Polars? if so it should be in the actions"; VERIFIED by introspection of Polars 1.40.1 and the registry)

`LazyFrame.select`, `drop`, `with_columns` and `filter` exist in Polars. No action carries these names today (`select`, `drop`, `filter`, `with_columns` are not registered): they exist under other names (`keep_columns` wraps `select`, `drop_columns` wraps `drop`, `mutate` is `with_columns` with a text formula, the five `filter_*` wrap `filter`). In the new scheme they are `polars_select`, `polars_drop`, `polars_with_columns`, and for `filter` both can exist: `polars_filter` (a formula predicate, exactly Polars) and `modif_filter` (column, op, value, na: the vocabulary of the HOME filter panel).

Polars `LazyFrame` has 41 table-step methods without an action of the same name: `approx_n_unique`, `bottom_k`, `count`, `describe`, `drop_nans`, `fill_nan`, `fill_null`, `first`, `gather_every`, `group_by_dynamic`, `head`, `interpolate`, `join_asof`, `join_where`, `last`, `limit`, `max`, `mean`, `median`, `melt`, `min`, `null_count`, `pivot`, `quantile`, `remove`, `rename`, `reverse`, `rolling`, `select_seq`, `shift`, `show`, `slice`, `std`, `sum`, `tail`, `top_k`, `var`, `with_columns`, `with_columns_seq`, `with_row_count`, `with_row_index`. Of these, `rename`, `pivot`, `describe`, `fill_null`, `interpolate` and `shift` are covered by an action under another name or through the expression they wrap. Real gaps a scientist may need: `head`, `tail`, `slice`, `limit`, `top_k`, `bottom_k`, `reverse`, `gather_every`, `with_row_index`, `drop_nans`, `fill_nan`, `remove`, the table aggregations (`sum`, `min`, `max`, `mean`, `median`, `std`, `var`, `quantile`, `count`, `null_count`, `first`, `last`), `join_asof`, `join_where`, `group_by_dynamic`, `rolling`. `quantile` is the real percentile (our `percentile` computes rank divided by the row count). The expression side is large: `Expr` 218 public methods, `str` 49, `list` 43, `dt` 47; the registry wraps a small part. ADR-035 (Polars parity) already asks for 1:1 parity; the gap list is its inventory. Which ones to add, and in which order, is Eve's decision; adding one needs its equality test against the Polars call (N9 b) and, for any that takes a formula, the formula check.

## 20. The sanitiser: what it does today (VERIFIED by reading `libs/ingestion/src/ingestion/sanitizer.py`; asked by the recipe session, M45)

It runs in `ingestor.py` after the column rename and before the type cast, on every column that is a `String` at that point (a column the reader inferred as a number is not touched), and it is not configurable from the recipe (`DataSanitizer()` is called without `extra_null_tokens`):

1. **Strip:** `str.strip_chars()` (the Polars default: whitespace only) on every String column.
2. **Null sentinels:** these 14 exact strings become a real null, in every String column: `""`, `NA`, `N/A`, `None`, `null`, `NaN`, `-`, `na`, `n/a`, `none`, `nan`, `NULL`, `n.a.`, `N.A.`.

**A science risk found by reading:** the list is applied to identifiers and free text too. `NA` is the ISO code of Namibia, `-` can be a real value, `None` can be a real label: such a value silently becomes a missing value, and every later filter on that column drops the row (`!=`, `not in`). By the rule "no hidden choice" the strip and the tokens must become explicit keys of the field (`null_values` with today's list written in by migration run A, so no table changes, and the maker can then shorten the list per column). Not measured yet: how many cells of the shipped test data are changed by this today (to do with the golden baseline).

## 21. Sixth round (Eve's answers, 2026-11-13)

**Eve's answers.** (a) We must KNOW that each `polars_` action works: it is registered exactly as Polars, and a test compares it with the direct Polars call (N9 b); special needs get a separate `modif_` action. (b) Types: every `categorical` of the recipes becomes `String` (it always meant String); the Polars type `Categorical` must exist for those who want it. (c) Data paths: how data reaches a deployment is not known yet (an API, different disks); relative paths are not the answer; it is the deployment's business; a development fallback is needed, perhaps in a development configuration ("I think it already is"). (d) The Polars table-step methods are to be added later, with all options and the same conventions, and may be DEFERRED when no recipe uses them and the app keeps working; `percentile` is removed, the real Polars one (`quantile`, `rank`) is used when added. (e) `polars_filter` and `modif_filter` can both exist. (f) Come back to Eve before anything is done.

**Check of (c) (VERIFIED by reading `app/modules/orchestrator.py:32-36, 90-100, 358-376` and `app/src/bootloader.py:117, 263`).** The development fallback already exists. The deployment file has `data_lookup` with two choices: `data_analysis_recipe_paths` (the `source.path` written in the recipe: "development default") and `by_dataset_id` (production: a file named after the dataset id in the `raw_data` location, which a pipeline or a connector delivers; the recipe's `source.path` is then ignored). Default is `data_analysis_recipe_paths`. So: no engine change is needed; a path in a recipe matters only in a development or test deployment; the path-shape rule (no absolute, no `..`, no `~`, no URL) is needed only there and containment is not needed in production, where the path is ignored. Cleaner, later and optional: move the development paths out of the recipes into the development deployment file, so that a recipe names no path at all (38 values). One stale line found: `app/modules/renamed_keys.py:20` names a choice `manifest_paths` that does not exist (`DATA_LOOKUP_CHOICES` has two); to fix with the next change of that file.

**Consequences, as recommendations.** `percentile` is removed (0 steps in shipped recipes, 1 in a test fixture); `polars_rank` and `polars_quantile` join the deferred gaps. The shipped recipes' `categorical` becomes `String` in run A (the table does not change; ingestion made it String). The gaps of section 19 are DEFERRED, except what replaces an existing action (`polars_select`, `polars_drop`, `polars_with_columns`, `polars_unique`, `polars_fill_null`, the `*_horizontal`, `polars_rank` when a recipe uses it). `modif_filter` is needed now (the audit writes it); `polars_filter` waits until a recipe needs a formula filter.

## 22. Seventh round (Eve's answers, 2026-11-13): types and missing values

**Eve's answers.** `modif_filter` behaviour is a verification task, ok for now. `type` is REQUIRED on every field. For the levels, respect Polars conventions. Missing values: a WARNING for recipe makers that they must say how `NA` and nulls are treated (it depends on the data); no default; the recipe must be able to treat them in different ways; a warning in the documentation. Question: does Polars have an NA?

**Answers (VERIFIED by run, Polars 1.40.1).**
- **Polars has no `NA`** (`pl.NA` does not exist). It has two different things: `null` (a missing value, any type) and `NaN` (a floating point value, "not a number", a number that is larger than every other in comparisons and is not null). The text `NA` in a file is just a string. Polars' own CSV reader turns only an EMPTY field into null by default; `NA`, `-` and `NaN` stay text until the maker says otherwise (`null_values`, a list for all columns, or one string per column; there is no list per column in the reader). R's `NA` corresponds to Polars `null`.
- **Levels:** Polars names the levels of an `Enum` `categories` (`pl.Enum(categories)`). Following Polars means the field key is `categories`. Our existing field key `categories` (a list that lets a step select columns as `@AMR`, `data_wrangler.py:27-42`) is used by NO yaml file of the repository (recipes, templates, tests, gallery: 0). It is a dead feature and the collision is only on paper: recommendation, remove the `@category` selection (legacy rule: no half-finished feature) and let `categories` mean the Polars thing.
- **A consequence for NaN:** today the sanitiser turns the text `NaN` into null before the cast, so no NaN ever comes from a file. With an explicit `null_values` list a `NaN` that is NOT listed is read by a Float64 field as a real NaN (VERIFIED: `nan`), which the filters treat as a number larger than all (section 13). So NaN needs its own handling in the recipe: `polars_fill_nan` and `polars_drop_nans` are no longer plainly deferrable (small, and part of how missing values are treated), and the documentation must name both.
- **Explicit null handling without a default:** the key (`null_values`, a list, `[]` allowed) is REQUIRED; to limit the friction I recommend one setting per data schema (one line per file) with an optional override per field, and the same for stripping whitespace (`strip: true or false`), both required. Because the Polars reader has no per-column list, the implementation reads text, applies the declared null words, then casts (the order of today's ingestion).

**Tasks created from this round.** MODIF-FILTER-VERIFY-1 (verify the behaviour of `modif_filter`: every op, `na`, types, nulls, NaN, lists, against the three current paths and the audit); DOC-MISSING-VALUES-1 (a section in the recipe documentation: null, NaN, text `NA`, `null_values`, `na`, `fill_null`, `fill_nan`, with examples; also the Namibia example); NAN-ACTIONS-1 (`polars_fill_nan`, `polars_drop_nans`); REMOVE-CATEGORY-SELECT-1 (remove the unused `@category` selection).

## 23. Two measurements for the work order (2026-11-13)

**Q4, what the sanitiser would change in the shipped test data** (probe, upper bound: every column read as text; the real sanitiser touches only columns that are text after the reader's inference): 33 `.tsv` files in `assets/test_data/`, 176162 cells; cells equal to one of the 14 tokens after stripping: `NA` 2630, `-` 156, empty 43, `None` 21, `N/A` 6. Almost all of the `NA` cells are one column, `metadata_isolation_method` of the VirulenceFinder files (1315 cells in two copies of the same file, one in the legacy `2_VIGAS-P_ST22_dummy` folder). Whether `NA` there means a missing value or a value is a question for the data owner; the baseline will show the effect on each table once `null_values` is explicit.

**Methods that take a function** (so a formula could smuggle code in): `Expr.map_batches(function)`, `Expr.map_elements(function)`, `Expr.pipe(function)`, `Expr.rolling_map(function)`, `list.to_struct(fields)` (a function form); the namespaces `str` and `dt` have none. Recommendation for the deny set of the formula check: read it from the signatures of the installed Polars (any parameter annotated `Callable`) instead of a hand-kept list, plus `meta` and the names starting with `_`; the grammar already refuses `lambda`.

## 24. Correction of section 22 (found while writing the ingestion tests, VERIFIED by run, 2026-11-13)

Section 22 said that today "no NaN ever comes from a file" because the sanitiser turns the text `NaN` into null. That is only half true. The sanitiser acts only on columns that are text after the reader's inference. So today the same text `NaN` is read as a real NaN in a column whose other cells are all numbers (`NaN`, `1.5` gives `[nan, 1.5]`), and as a null in a column that also holds another word such as `NA` (`NaN`, `NA`, `1.5` gives `[None, None, 1.5]`). The result depends on the OTHER cells of the column: a hidden, data-dependent behaviour, which is one more reason for explicit `null_values` and a declared type. Under the explicit rule an unlisted `NaN` is a NaN in every case. Test: `libs/ingestion/tests/test_declared_types_and_missing_values.py` (the mixed column case fails today, strict).

## 25. W6 package 2: which old actions become Polars steps, which stay `step_` (a recommendation to Eve, 2026-11-13; counts VERIFIED over all yaml and test code)

Eve: several-step actions may stay but are minimised, must be `step_` and are recorded. Rule applied: an old action goes when the same table can be written with Polars steps that already exist (`polars_with_columns` with a formula, `polars_str_split`, ...); each replacement is proved by a differential test (old action and new steps give the same table) before it is removed. Steps in shipped recipes / all yaml and test code:

| Old action | Becomes | Shipped / all steps |
|---|---|---|
| `mutate`, `add_constant` | `polars_with_columns` (built) | 6, 1 / 21, 2 |
| `count_by_group`, `window_agg` | `polars_with_columns` with `pl.len().over(...)` or `pl.col(c).mean().over(...)` (no `modif_over` needed: R2 falls) | 2, 0 / 3, 1 |
| `divide_columns`, `z_score`, `label_if`, `null_if`, `replace_values`, `recode_values`, `date_extract`, `to_struct` | `polars_with_columns` formulas (each hidden cast or name is written in the formula) | 1, 1, 0, 0, 1, 1, 0, 0 / 2, 2, 2, 2, 2, 2, 1, 2 |
| `strip_whitespace` | `polars_str_strip_chars` with the characters written (the quote where it was stripped) | 13 / 20 |
| `split_and_explode` | `polars_str_split` then `polars_explode` | 3 / 4 |
| `horizontal_stats` | the four `*_horizontal` (built) | 0 / 1 |
| `drop_duplicates`, `unique_rows`, `unique` | `polars_unique` (built) | 2, 1, 0 / 5, 2, 1 |
| `rename_columns`, `join_filter` | `polars_rename`, `polars_join` with `how` | 0, 2 / 1, 3 |
| `fill_nulls`, `fill_nulls_direction`, `round_numeric`, `regex_replace`, `regex_extract`, `split_to_list` | `polars_fill_null`, `polars_round`, `polars_str_replace_all`, `polars_str_extract`, `polars_str_split` (built) | 1, 0, 0, 0, 0, 0 / 4, 1, 1, 7, 1, 2 |
| `filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `filter_range`, `is_in`, `not_in` | `modif_filter` (built, verified, `na` required) | 1, 0, 0, 0, 9, 0, 0 / 19, 4, 8, 2, 19, 4, 3 |
| `keep_columns`, `drop_columns` | `polars_select`, `polars_drop` (run B) | 7, 2 / 8, 5 |
| `percentile`, `value_counts`, `select_by_pattern`, `sanitize_column_names` | removed (0 shipped steps; a rename mapping replaces the last) | 0 / 1, 1, 1, 1 |
| `summarize`, `top_n_other`, `split_column`, `split_column_to_parts`, `derive_categories` | stay as `step_` actions, each read, documented and given explicit options | 5, 1, 1, 1, 1 / 7, 2, 2, 2, 2 |

So `step_` falls from 12 (the spec's list) to 5, and `modif_` stays at one action (`modif_filter`). `derive_categories` waits for Q2 (a lookup file mapped by a Python function; it may be a `polars_join` with a lookup table). Shipped steps that must keep their table: 13 `strip_whitespace`, 9 `filter_range`, 6 `mutate`, 5 `summarize`, 3 `split_and_explode`, 7 `keep_columns`; the golden baseline measures each replacement.

## 26. Findings while building the step_ actions and checking the replacements (2026-11-13, VERIFIED by run and reading)

1. **`derive_categories` has no live use.** Its only shipped step is in `1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml`, a fragment that NO recipe includes (the baseline builds that recipe without it), and its `lookup_right` and `extract_column` ("Predicted Phenotype", "AMR Category (Class)") are not columns of the reference file it names (`gene_id`, `phenotype_class`): the step would fail. The other uses are a test fixture and the integrity suite. Eve: a lookup is a `polars_join` with a reference table; so the action is removed with its dead fragment and its fixture is rewritten as a join. (Task for the removal series.)
2. **The old `split_column_to_parts` dropped data silently:** a value with more parts than names lost the extra parts (`Klebsiella/pneumoniae/extra` into two columns gave `pneumoniae`, `extra` vanished; its comment claims a cast to Float64 that never happened). `step_split_column_to_parts` uses `str.splitn` and keeps the remainder in the last column (test pins both behaviours).
3. **`strip_whitespace` with no `columns` means "every String column" (a data-dependent set):** 10 of the 13 shipped steps are written that way, and it also strips the double quote. Ingestion already strips whitespace on every text column (`strip: true`, DEC28), so the step only adds the quote. The migration writes `polars_str_strip_chars` with an explicit list of the String fields of the schema (known from the declared types, because these steps stand at the start of tier 1) and the characters ` \t\n\r"`.
4. **Mutation survivors:** `modif_filter`: `condition.fill_null(False)` is equivalent to the bare condition (a null filters out); kept for clarity.

Built and committed: `polars_calls.py` (37 `polars_`), `modified.py` (`modif_filter`), `composite.py` (4 `step_`), `declared.py` (ingestion W5). Remaining before the switch: the differential tests that prove each replacement of section 25 gives the same table, then the removal of the old actions together with `ingest` becoming `ingest_declared` and migration run A.

## 27. The converter old step to new steps, and four more old actions that did not do what they said (2026-11-13, VERIFIED by running the old path and the new steps on the same tables)

`libs/utils/src/utils/step_migration.py` converts every old action to the steps of format 1 (one function each, every silent default written into the step); `libs/transformer/tests/test_step_conversion.py` runs the old step through the real old path (`DataWrangler` with its aliases and defaults, joins through the assembler's action) and the converted steps through the new actions: 113 tests, 6 mutations out of 8 caught (the two survivors are an equivalent right-join order, and a sample seed fixed by a stronger case). Removed actions are refused with what to write instead; `keep_columns` and `drop_columns` wait for run B.

Four old actions were broken, found because the test compares behaviour with what the action says it does:
1. **`drop_duplicates` without `columns` failed** ("at least one key is required"), although its description says it deduplicates on all columns. Converted: `polars_unique` without `subset`.
2. **`drop_nulls` without `columns` dropped nothing** (a silent no-op; the wrangler passed `subset=[]`); its description says it drops rows with any null. Converted: `polars_drop_nulls` without `subset` (drops rows with any null). 0 shipped steps, 2 in tests.
3. **`null_if` never nulled the column** and added a stray column named after the literal. Converted: one in-place formula per column that does what it says. 0 shipped steps.
4. **`split_column` failed (index out of bounds) on a value with fewer parts than names.** Converted: `str.splitn` gives null for the missing parts.
Each old behaviour is pinned in a test, so the changes are recorded and not silent. In every case the old step either failed or did nothing, so no shipped table changes (the golden baseline measures this at the switch).
