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
