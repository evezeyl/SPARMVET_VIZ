# Engine boundary: scientist and data scientist viewpoint (2026-11-21)

Labels: RUN = I ran it (scratch: `tmpAI/panel/engine_boundary/scientist_scratch/e1.py`, `e2.py`, `e3.py`; Polars 1.40.1, pandas 3.0.2, numpy 2.4.4, plotnine 0.15.4, matplotlib 3.10.9; load 3.6 to 4.1). READ = file:line. REASONED = inferred. I did not run the app, only the libraries.

## 8-line summary for the owner
1. Silent today: between Polars and plotnine, null and NaN become one value (both NaN in pandas). plotnine then drops those rows and says "Removed 2 rows" only as a Python warning (RUN e3). I found no place in app/ or libs/viz_factory that shows this to the user (READ: grep, only `checked_plot.py:202` touches warnings, and it silences them). Not sure; to be checked.
2. Silent: the export lists library versions for `polars`, `shiny`, `plotnine` only (READ `export_handlers.py:120-126`). The seam also runs pandas, numpy and pyarrow (`viz_factory.py:267`); their versions are not recorded. D-0248 `engine_versions` covers `matplotlib` but not pandas (READ `engines.py:45-48`).
3. The same recipe intent on another engine does NOT give the same result unless the engine is made to follow Polars' rules. RUN: filter `!=` and `not in` on null; NaN in `mean`/`sum`; null join keys; group-by order and null groups; default quantile method; string to number casting; regex dialect; seeded sample. All differ.
4. What can never be promised: the same bits for floats (sum depends on row order and thread split, RUN), the same sampled rows from one seed on two engines (RUN), the same picture on a machine with other fonts.
5. Recommended boundary (trust side): V2, an adapter per engine, with the missing-value meaning, the join rules and the order rules as services of the engine, and a conformance suite every engine must pass. V3 (a neutral table handle) is the right end state; do not start it before the demo.
6. The recipe's engine block is enough to say WHICH engine; it is not enough to say WHAT the step means. The checker must refuse a recipe whose steps use a rule the engine cannot keep (for example `na: keep`).
7. Time: marking, the import test, and the records (versions, engine per table, missing-value rule in the export) are before the demo and change no result. Moving `filter_values`, `missing_values`, `formula_check`, `orchestrator`, `viz_factory` is after the demo, tested against the golden baseline (`assets/scripts/golden_baseline.py`, READ named in `engine_registry.py` header; not run by me).
8. Each rule the engine must keep is written once, as a test with a small table, so a new engine is accepted by passing it, not by a promise.

## Question 5. THE SCIENCE (main weight)

Same recipe intent, another engine. Result of the runs (RUN, all in `e1.py`/`e2.py`):

| Point | Polars (today, decided D-0042, ADR-103, ADR-100) | pandas | Same? | Effect |
|---|---|---|---|---|
| `g != 'a'`, a null in g | null row removed | null row KEPT | NO | Different row count. This is exactly the rule that D-0042 fixes to "follows Polars". Another engine must reproduce it by hand. |
| `not in ['a']`, null | removed | kept | NO | same |
| `x != 1`, NaN and null | NaN kept, null removed | both kept | NO | NaN is a number in Polars; in pandas null and NaN are one thing |
| `x > 1`, NaN | NaN kept (NaN is "larger than every number") | NaN removed | NO | D-0042 sentence "NaN is a number, larger than every number" is a Polars fact, not a general one |
| `mean`, `sum` with a NaN | NaN (propagates); null skipped | NaN skipped | NO | a table value changes from "nan" to a number |
| sort with null and NaN | null first, NaN last, sorted | NaN (both) last | NO | order of rows with missing values |
| join on null keys | null does not match null | null matches null (RUN: 'None' row got r=20) | NO | row counts and values after a join. The join warning already carries `nulls_equal` (READ `join_keys.py:173`): good, engine-specific by design |
| join int key to float key | error (SchemaError) | joins | NO | pandas hides a type mismatch Polars refuses |
| group-by, no order asked | order changes between runs (RUN: 3 runs, 2 orders) | keys sorted; null key dropped | NO | ADR-100's required `maintain_order` is right. On pandas the same word means something else (`sort=False`). A null group is kept by Polars, dropped by pandas: a sample can VANISH from a group table |
| sort ties | stable here (RUN 200k rows); ADR-090 asks for a stated rule | default quicksort is NOT stable (RUN) | NO | tie order |
| `top_k` ties | first rows by input order (RUN) | not tested | not sure | ADR-5236 note says the wording waits for a test |
| quantile 0.3 of 1,2,3,4 | 2.0 | 1.9 | NO | default method differs; a boxplot or a median-like value changes. Any statistic step needs the method written |
| std of 1,2,3,4 | 1.29 (n-1) | 1.29 | yes (numpy gives 1.118, n) | engine defaults for ddof differ across libraries, not between these two |
| string to number | " 5" and "5,5" become null | " 5" becomes 5.0 | NO | silent loss vs silent repair |
| regex | Rust: no look-around, no back-reference (error, RUN) | Python `re`: ok | NO | a formula or filter with a regex is engine dialect |
| seeded `sample`, seed 0 | rows 2, 9, 3 | rows 2, 8, 4 | NO | same seed, other rows. A seed is only meaningful with its engine and version |
| float sum, 1e6 values | `-20899815402.86736` | `...867325` (also numpy) | NO at the 12th digit | and Polars' own sum changes when the SAME numbers come in a different row order (RUN) |
| int to pandas with a null | Int64 with null | float64, null becomes NaN (RUN) | NO | an integer column silently becomes float at the seam (`viz_factory.py:267`) |

Plot side (RUN e3): the same seed object gives the same PNG bytes twice on this machine. `random_state=0` as a plain int is falsy and would mean "no seed" in plotnine; the app already guards this with a generator (READ `viz_factory.py:42-55`): this is exactly a hidden engine rule that a second plot engine will not share. A family that is not installed draws with the default font and the PNG hash was the same as the explicit default (RUN: both `61e38758ced1`), so the picture changes with the machine and nothing in the file says so. The app does warn on screen (READ `viz_factory.py:417-430`); I did not check that the font used is in the export (not verified).

Rule of thumb: a result is the same only if the engine implements the SAME RULES, not the same intent. The app can state the rules; it cannot make the numbers bit-identical.

What the app must tell the user (information, not a choice for them):
- which engine, which version of every library in the path (including pandas, numpy, pyarrow, matplotlib), per table tier and per plot (D-0248 covers the engine; extend to the seam libraries);
- the missing-value rules in force (null: what `na` did, counts; NaN: separate) as numbers in the export, before and after each filter;
- rows dropped at the plot (null and NaN), as a count on the picture's record;
- row-order rule per step (ADR-090 already);
- seeds and the engine and version that make them meaningful;
- font asked, font used, machine;
- when a recipe is moved to another engine: a list of every step whose rule differs, shown before the run (see question 4).

What can never be promised: bit-identical floats across engines, versions or row orders; the same sample from one seed on two engines; the same pixels on two machines (fonts, matplotlib version); that a null/NaN distinction exists in every engine. A promise is only "same rules, same inputs, same engine and versions give the same result" (this is already the claim of the project; keep it exact and do not widen it to "any engine").

## Question 3. THE LINEAGE AND THE AUDIT
- "What a step writes" and "which joins can be followed": yes, a service of the data engine (REASONED). Today they sit in `libs/utils` and read Polars names: `step_effects.py:7-13, 55` (`READINGS` keyed by `polars_*` names), `FOLLOWED_JOINS = ("left","inner")` (READ line 55), `join_keys.py:36` (`_KEEPS_LEFT_KEYS`), `join_keys.py:240` (`_SAME_KEY_RESULT`). The module says "No Polars" (READ line 31), but it knows Polars' action names, kinds and the Polars meaning of a null key.
- Keeping the walk neutral: the walk asks the engine for a small closed record per step (`columns kept`, `renamed`, `written names`, `key link`, `not followed, and why`), and checks it against the engine's plan. The walk itself never sees an action name. Where the engine says "cannot follow", the walk shows the red "YET" sentence of D-0454 (information). The same reading already exists as a closed list (D-0351, D-0356, D-0444: names only, never formulas), so the data shape is already engine-neutral; only the keys are Polars names.
- Trust point: the walk's result is a claim about data ("this column comes from there"). For a second engine, an unfollowed step must be grey or red, never guessed. So a new engine starts with NO readings (everything "not followed yet") and gains them one by one with a test each. That is safe by construction.
- Mark from the start, in the data and the text: the join warning records `engine`, `how` and `nulls_equal` as fields next to the sentence (the sentence is then engine-specific text under an engine label). The uncertain drop (`key_drop.py:82`) is marked as a Polars reading. "Tables no plot reads": a neutral fact (graph of the recipe); mark neutral. `remove_from_all.py:22, 333` writes `modif_filter`: mark as the engine's step name.
- Also record in the audit export which engine's reading was used for each hop.

## Question 4. THE RECIPE
- The block names the engine; that is enough to route (DECIDED D-0219, D-0238). It is not enough to know a result: a filter `ne` with `na: remove` means "remove null" because Polars does; another engine must say the same or the recipe is not equal. So the engine is part of the recipe's meaning, and the recipe hash must contain it (D-0240, M216: already so for tier keys).
- Neutral in the format: `id`, `info`, `data_schemas`, `joins` (keys), `analysis_groups`, tiers as a structure, labels, `na: keep|remove`, order rule as a stated requirement. Engine dialect: action names, `named_exprs` text, dtype names, `how`/`maintain_order` values, regex, quantile method, aggregation names, geom/theme names, `random_state`.
- Proposal for the checker (REASONED): (1) refuse a step whose action does not belong to its block's engine (built, D-0238); (2) refuse a recipe whose engine does not declare that it keeps the rules the recipe uses (`na`, order, seed), by name; (3) never translate a recipe from one engine to another silently: a move is a new recipe, reviewed by the user, with the list of steps whose rule differs. Her view M216 fits this.
- Hidden hole today: `id_reconciliation/recipe_steps.py:58,77` and `step_migration.py:30-316` write Polars formula text into recipes (READ FACTS). Any tool that writes recipes must go through the engine's service, else a recipe for engine B can contain Polars text unseen.

## Question 1 from the side of trust
- V1 (mark only) does not protect a result: nothing forces an engine to keep the rules. V2 gives a place for each rule. V3 hides the engine object, which also removes the null/NaN collapse at the seam, because the table handle would carry null and NaN separately and the plot engine would be told how many rows it drops.
- Services that carry the science, and that must be written as rules with tests for each engine (not just "provided"): missing-value meaning of each filter operator (`filter_values.py:30, 374-411`, `missing_values.py`); join kinds with null-key rule and row-order rule; group and sort order; type names and casts (`polars_types.py`); statistics defaults (quantile method, ddof); hashing of a table (`hashing.py:28-36` goes through Polars Parquet metadata: a content hash must be defined on content, not on an engine's metadata; not sure what it hashes; not verified); seeds; error translation (D-0260, so that one engine's message cannot leak a different meaning); the record of versions.
- Conformance suite (the one test that earns trust): a short list of tiny tables with nulls, NaN, ties, empty tables, and expected results per rule. A new engine is added when it passes, or its failures are listed as "this engine differs here" and shown to users. This is also where "engine-specific marking" becomes testable.

## Question 7 from the side of trust (stages; sizes are rough, not sure)
| Stage | Touches | Changes a result? | Test | Risk to demo | Size |
|---|---|---|---|---|---|
| A. Mark: header field `engine:` or `neutral` in every file with Polars/plotnine import (54 + 11 files), a test with the allowed list | headers only, 1 test | no | the test itself; break it once | none | small, ~65 files by script, 1 session |
| B. Records: add pandas, numpy, pyarrow, matplotlib versions to the export; add null/NaN count and rows dropped at the plot | `export_handlers.py`, `engine_record.py`, `engines.py` | the export gains fields; no data change | export golden | low | small, 3-5 files |
| C. Conformance tests of the rules, on Polars only (writes the contract) | new tests | no | RUN against Polars | none | medium, 1-2 sessions |
| D. Move the rules behind engine services, Polars first: `filter_values`, `missing_values`, `polars_types`, `formula_check`, `hashing`, `step_effects`, `join_keys` | ~10 libs/utils files plus callers | must not; proven by golden baseline equal before and after | golden + C | medium to high if done before demo | large, 3-5 sessions |
| E. Table handle and picture object at the seam (V3) | `orchestrator`, `viz_factory`, `export_handlers`, `home_theater`, handlers | no, but it touches the null/NaN seam | golden + C | high | large |
Before the demo without risk: A, B (read-only or additive), and C. After: D and E. Waiting costs more code written against Polars names; deciding fast with A and C costs nothing in result terms. Lineage work in flight: continue only what stays "names in, records out" and mark each new text with its engine; hold anything that adds Polars knowledge to `libs/utils` until D.

## Question 2 (what a new engine adds, trust side only)
A second plot engine: its entry file, registry row, its components with `engine` field, its seed rule, its font and theme record, and the conformance suite for the plot seam (drop of missing rows, seed, fonts). R backend: reading and writing the same Parquet is neutral; null versus NA versus NaN mapping must be stated and tested; row order of `dplyr` group-by is the input order (REASONED, not run). A pandas or SQL data engine: all rows of the table in question 5 must be implemented by hand to follow Polars, or the engine declares a different rule set and the recipe says so. What still changes in existing code: the places in the "hardest" list of FACTS (orchestrator types, `viz_factory` pandas conversion, `plot_config_resolver.py:466-495` pandas dtype checks) and the version/seed records.

## Question 6 (one point)
A test that fails on an unmarked or misplaced engine import also guards science: a stray `import polars` in a neutral file is a place where a rule can be silently applied. User-facing texts that name an engine: keep them, but under an engine label (the null/NaN sentence is a Polars sentence today).

## Table
| point | status | proposal | reconsiders a decision? |
|---|---|---|---|
| engine is chosen by the code, no fallback | DECIDED | keep | no (D-0219) |
| missing values follow Polars | DECIDED | keep; a new engine must pass the conformance test or declare the difference | no (D-0042); information: it makes Polars the reference engine |
| versions in export | DECIDED (D-0248) | extend to seam libraries (pandas, numpy, pyarrow) | no |
| null/NaN collapse at the plot seam, rows dropped by the plot | OPEN | show count in picture record | no |
| one default seed for all plot engines | OPEN | seed belongs to the engine; record engine and version with it | no (engine_registry.py:118-124) |
| conformance suite | OPEN | stage C | no |
| recipe move to another engine | OPEN | new recipe, list of differing steps, user reviews | relates to M216 |
| hashing a table through Polars metadata | not sure | define on content | not sure |
| default plot seed D-0056 vs ADR-090 / ADR-106 "open" | contradiction in records | to Eve (from FACTS) | yes, information |

## To decide first (ranked)
1. Is Polars the reference for the rules (D-0042 says so for missing values): must every future engine reproduce them, or may an engine declare different rules that the recipe then names? (Decides what the conformance suite is.)
2. May the null/NaN collapse and the dropped rows at the plot seam be shown as a count in the picture record and the export (flag 1)?
3. Add the seam libraries (pandas, numpy, pyarrow) to the recorded versions (flag 2).
4. Is a recipe moved to another engine a new recipe with a reviewed list of differing steps, never an automatic translation?
5. Before the demo: stages A, B, C only? D and E after?
6. Seed: per engine, with engine and version recorded.

## Not verified
Whether the plot warning "Removed n rows" is shown anywhere in the app; that the font used is in the export; what `hashing.py` hashes exactly; whether the golden baseline runs and which part of the pipeline it covers; any pandas behaviour was run on pandas 3.0.2 only (not 2.x); R, SQL, DuckDB behaviour (duckdb is not installed; not run); `top_k` on pandas; thread count effects on Polars on another machine.
