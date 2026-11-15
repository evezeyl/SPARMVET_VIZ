# Equality check: the engine against a hand-written reading (EQUALITY-CHECK-1, PROVISIONAL)

Aim (Eve, 2026-11-15): "we want the results to be correct". Each table the engine builds from the recipe
`2_test_data_ST22_dummy` is compared with the same table written directly in plain Polars and plotnine, on clean and
on deliberately dirty data. Built on a recommendation (tests only, changes no result, reversible).

## The independence rule (the whole point)

The expected side, `reference_2_test_data_ST22_dummy.py`, is written BY HAND from the MEANING of the recipe, in plain
Polars (`import polars as pl`) and plotnine; it imports nothing from `libs/` or `app/`. Its author did NOT read the
engine's implementation: not `libs/transformer/src/transformer/` (actions, assembler), not
`app/modules/orchestrator.py`, not `libs/viz_factory/src/`. Allowed and used: the recipe files, the recipe format spec
(`.claude/design/recipe_format_spec.md`), the user documentation of the actions (`docs/appendix/transformer_actions.qmd`),
the Polars and plotnine documentation, the data files. The engine is only RUN, as a black box, the way
`assets/scripts/golden_baseline.py` runs it (`engine_black_box.py`). A difference between the two sides is a finding
(`FINDINGS.md`), never a reason to adjust the hand-written side to the engine. If you change the reference file, say
which sentence of the recipe or the docs you followed.

## Files

| File | What it is |
|---|---|
| `reference_2_test_data_ST22_dummy.py` | the hand-written tables and plots (one comment per step, quoting the recipe) |
| `make_dirty_data.py` | writes `data/` and `recipes/` (argparse, fixed seed, reproducible); the shipped files are only read |
| `data/dirty`, `data/emptied`, `data/fractional_year` | synthetic edits of the shipped data (declared columns only); `EDITS.md` in each |
| `recipes/` | staged copies of the shipped recipe that read those files (the shipped recipe is not changed) |
| `engine_black_box.py`, `scenarios.py`, `checks.py` | run the engine, the scenarios, the comparisons |
| `test_recipe_equals_hand_written.py` | the comparisons that agree today |
| `test_findings_open.py`, `open_findings.py`, `conftest.py` | the comparisons that differ today (failing on purpose, not collected by default) |
| `FINDINGS.md` | each difference and each misleading-but-equal fact |

## Scenarios

`clean` (shipped recipe, shipped data), `dirty` (missing values in a filtered, a grouping and a key column, NaN, repeated
and missing keys, one-sided samples, values at, just below and just above each threshold, stray spaces and case, a
sample removed by the filter), `emptied` (the plasmid filter removes every row), `fractional_year` (Year 2023.5: both
sides must refuse), `dirty_no_null_text` (the dirty data with the recipe's own `null_values: []`).
The dirty recipe states `null_values: [""]` (otherwise an empty number cell cannot be read; see F2).

## What is compared

Per scenario: tier 1 and tier 2 of the 3 schemas and the 2 joins (same columns, dtypes, rows, row order, with
`polars.testing.assert_frame_equal`); the table each of the 3 plots receives (as the pandas frame plotnine gets); the
built plot (labels, layer frames, panels) against a plain plotnine call written by hand, once on the hand-written table
and once (`plot_isolated`) on the engine's own plot data, so that a table difference does not hide a drawing difference.
The tier 2 of every table is its tier 1 (the recipe has no `tier2` step).

## Tables with no stated row order (compared as a sorted set, and also in file order)

`metadata_schema`, `amr_data`, `plasmid_data`: the recipe never says what order a data file's rows come out in; the
`order` cases check that it is the file's order (it is today). Also unstated: where a missing value goes in
`polars_sort` (the plain-Polars default, first, is what both sides do). `AMR_Profile_Joint` and `Plasmid_Profile_Joint`
state their order (`polars_sort ... maintain_order: true`) and are compared row by row.

## Run

    PYTHONPATH=$PWD:$(ls -d $PWD/libs/*/src | tr '\n' ':') ./.venv/bin/python -m pytest app/tests/equality -q
    # the open findings (they fail today, on purpose):
    PYTHONPATH=... ./.venv/bin/python -m pytest app/tests/equality/test_findings_open.py -q
    # reproduce the data (same seed, same bytes):
    ./.venv/bin/python app/tests/equality/make_dirty_data.py

A pytest marker was not used: the project has no pytest configuration or registered markers, so the findings are in a
separate file that a directory run does not collect (`conftest.py`); naming the file runs it.
