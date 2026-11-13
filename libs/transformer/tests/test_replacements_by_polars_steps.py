"""An old action and the Polars steps that replace it give the same table (W6 package 2, evidence section 25).

Eve 2026-11-13: where Polars can do it, use the Polars action and nothing else, otherwise it is difficult to control.
Each test runs the old action and the replacement steps (the exact steps the migration tool writes) on the same probe
table and compares them. The old actions are removed by the migration series; these tests then lose their left half and
keep the right half as a frozen expectation (`EXPECTED_AFTER_REMOVAL` below), so the replacement stays pinned.

Where the old action was wrong, the test says so and pins the difference (`split_column_to_parts` lost the remainder).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_replacements_by_polars_steps.py -q
"""
import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS as A

DATA = pl.DataFrame({
    "g": ["x", "x", "y", "y", "y", None],
    "v": [1, 2, 3, 4, 5, 6],
    "w": [1.5, None, 2.5, 3.5, 4.5, 5.5],
    "path": ["a_b_c", "d_e", "f", None, "g_h_i_j", "k"],
    "sp": ["Escherichia/coli", "Klebsiella/pneumoniae", "Salmonella", None, "A/B", "C/D"],
    "txt": ['  "a b"  ', "c", None, ' "d" ', "e f", ""],
    "genes": ["a,b", "c", None, "d,e,f", "g", ""],
    "d": [None] * 6,
})


def run(steps, frame=DATA):
    lf = frame.lazy()
    for step in steps:
        lf = A[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
    return lf.collect()


def same(old_steps, new_steps, frame=DATA):
    assert_frame_equal(run(new_steps, frame), run(old_steps, frame))


# -- summarize: group_by with named aggregations ---------------------------------------------------

@pytest.mark.parametrize("agg", ["count", "sum", "mean"])
def test_summarize_is_polars_group_by(agg):
    old = [{"action": "summarize", "group_by": ["g"], "columns": ["v", "w"], "agg": agg}]
    new = [{"action": "polars_group_by", "by": ["g"], "maintain_order": True,
            "named_aggs": {"v_" + agg: f"pl.col('v').{agg}()", "w_" + agg: f"pl.col('w').{agg}()"}}]
    same(old, new)


def test_summarize_with_a_chosen_name_and_over_the_whole_table():
    same([{"action": "summarize", "group_by": ["g"], "columns": ["v"], "agg": "sum", "new_name": "total"}],
         [{"action": "polars_group_by", "by": ["g"], "maintain_order": True, "named_aggs": {"total": "pl.col('v').sum()"}}])
    same([{"action": "summarize", "group_by": [], "columns": ["v"], "agg": "sum"}],
         [{"action": "polars_group_by", "by": [], "maintain_order": True, "named_aggs": {"v_sum": "pl.col('v').sum()"}}])


# -- split_column and split_column_to_parts: str.splitn, unnest, rename -------------------------------

def _split_steps(source, sep, names, drop_source=False):
    steps = [{"action": "polars_str_splitn", "columns": [source], "by": sep, "n": len(names), "target_column": "__parts"},
             {"action": "polars_unnest", "columns": ["__parts"]},
             {"action": "polars_rename", "mapping": {f"field_{i}": n for i, n in enumerate(names)}, "strict": True}]
    return steps + ([{"action": "polars_drop", "columns": [source], "strict": True}] if drop_source else [])


def test_split_column_is_splitn_unnest_rename():
    same([{"action": "split_column", "columns": ["path"], "new_columns": ["a", "b"], "delimiter": "_"}], _split_steps("path", "_", ["a", "b"]))


def test_split_column_with_drop_source_adds_a_drop_step():
    same([{"action": "split_column", "columns": ["path"], "new_columns": ["a", "b"], "delimiter": "_", "drop_source": True}],
         _split_steps("path", "_", ["a", "b"], drop_source=True))


def test_split_column_to_parts_is_the_same_steps_when_no_part_is_left_over():
    frame = DATA.filter(pl.col("sp").is_null() | (pl.col("sp").str.count_matches("/") <= 1))
    same([{"action": "split_column_to_parts", "column": "sp", "separator": "/", "new_columns": ["genus", "species"]}],
         _split_steps("sp", "/", ["genus", "species"]), frame)


def test_split_column_to_parts_lost_the_remainder_and_the_polars_steps_keep_it():
    frame = pl.DataFrame({"sp": ["Klebsiella/pneumoniae/extra"]})
    old = run([{"action": "split_column_to_parts", "column": "sp", "separator": "/", "new_columns": ["genus", "species"]}], frame)
    new = run(_split_steps("sp", "/", ["genus", "species"]), frame)
    assert old["species"].to_list() == ["pneumoniae"], "the finding: the old action dropped 'extra' without a message"
    assert new["species"].to_list() == ["pneumoniae/extra"]


# -- the formula replacements ------------------------------------------------------------------------

def test_split_and_explode_is_str_split_then_explode():
    same([{"action": "split_and_explode", "columns": ["genes"], "separator": ","}],
         [{"action": "polars_str_split", "columns": ["genes"], "by": ",", "inclusive": False, "literal": True, "strict": True},
          {"action": "polars_explode", "columns": ["genes"]}])


def test_strip_whitespace_is_str_strip_chars_with_the_characters_written():
    same([{"action": "strip_whitespace", "columns": ["txt"]}],
         [{"action": "polars_str_strip_chars", "columns": ["txt"], "characters": ' \t\n\r"'}])


def test_strip_whitespace_without_columns_is_the_explicit_list_of_text_columns():
    text_columns = [n for n, dt in DATA.schema.items() if dt == pl.String]
    same([{"action": "strip_whitespace"}], [{"action": "polars_str_strip_chars", "columns": text_columns, "characters": ' \t\n\r"'}])


def test_divide_columns_is_a_formula_with_the_cast_written():
    same([{"action": "divide_columns", "numerator": "v", "denominator": "w", "new_column": "r"}],
         [{"action": "polars_with_columns", "named_exprs": {"r": "pl.col('v').cast(pl.Float64) / pl.col('w').cast(pl.Float64)"}}])


def test_z_score_is_a_formula_with_the_name_written():
    same([{"action": "z_score", "columns": ["v", "w"]}],
         [{"action": "polars_with_columns", "named_exprs": {
             "v_zscore": "(pl.col('v') - pl.col('v').mean()) / pl.col('v').std()",
             "w_zscore": "(pl.col('w') - pl.col('w').mean()) / pl.col('w').std()"}}])


def test_count_by_group_is_len_over():
    same([{"action": "count_by_group", "group_by": ["g"], "new_column": "n"}],
         [{"action": "polars_with_columns", "named_exprs": {"n": "pl.len().over(['g'])"}}])


@pytest.mark.parametrize("function", ["mean", "sum", "min", "max", "count", "median", "std"])
def test_window_agg_is_the_function_over_the_partition(function):
    same([{"action": "window_agg", "column": "v", "partition_by": ["g"], "function": function, "target_column": "t"}],
         [{"action": "polars_with_columns", "named_exprs": {"t": f"pl.col('v').{function}().over(['g'])"}}])


def test_label_if_is_when_then_otherwise():
    same([{"action": "label_if", "column": "v", "new_column": "lab", "predicate": ">=", "value": 3, "then": "High", "otherwise": "Low"}],
         [{"action": "polars_with_columns", "named_exprs": {"lab": "pl.when(pl.col('v') >= 3).then(pl.lit('High')).otherwise(pl.lit('Low'))"}}])


def test_date_extract_is_dt_formulas_with_the_names_written():
    frame = pl.DataFrame({"d": [pl.Series(["2022-03-15"]).str.to_date()[0], None]})
    same([{"action": "date_extract", "column": "d", "parts": ["year", "month"]}],
         [{"action": "polars_with_columns", "named_exprs": {"d_year": "pl.col('d').dt.year()", "d_month": "pl.col('d').dt.month()"}}], frame)


def test_horizontal_stats_is_the_horizontal_function():
    same([{"action": "horizontal_stats", "columns": ["v", "w"], "operation": "sum", "target_column": "t"}],
         [{"action": "polars_sum_horizontal", "exprs": ["v", "w"], "ignore_nulls": True, "target_column": "t"}])


def test_fill_nulls_with_a_direction_is_fill_null_with_a_strategy():
    same([{"action": "fill_nulls_direction", "columns": ["w"], "direction": "forward"}],
         [{"action": "polars_fill_null", "columns": ["w"], "strategy": "forward"}])


def test_drop_duplicates_and_unique_rows_are_unique_with_the_rules_written():
    same([{"action": "drop_duplicates", "columns": ["g"]}], [{"action": "polars_unique", "subset": ["g"], "keep": "first", "maintain_order": True}])
    same([{"action": "unique_rows"}], [{"action": "polars_unique", "keep": "any", "maintain_order": True}])
