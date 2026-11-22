"""The comparison of an original result and an audited result: layer 1 (counts), layer 2 (the whole-row diff), layer 3 (the paired view).

The tables are small and hand-made, shaped like the four kinds the trials of 2026-11-22 used on the demo recipe: an aggregate (one row per
country and year), a value computed over all samples (a z-score), one row per sample, and a long table with no key. Nothing here reads a
demo file. Each limit that the module states in `CANNOT_CATCH` has a test named `test_limit_<code>` that SHOWS it.

# @deps
# consumes: libs/utils/src/utils/table_compare.py
# doc: .claude/knowledge/decision_ledger.md (D-0485, D-0488, D-0489)
# @end_deps
"""
import math

import polars as pl
import pytest

from utils import table_compare as tc
from utils.table_compare import CANNOT_CATCH, compare

NAN = float("nan")


def aggregate(norway: int = 19) -> pl.DataFrame:
    """One row per country and year: the count of samples (the trial's `QA_aggregated_no_key`)."""
    return pl.DataFrame({"country": ["Denmark", "Norway", "Norway", "Sweden"], "year_label": ["2023", "2023", "2024", "2024"],
                         "n_samples": [4, 7, norway, 6]})


def zscore(n50: list, samples: list = None) -> pl.DataFrame:
    """One row per sample with a value computed over all samples (the trial's `QA_population_zscore`)."""
    ids = samples or [f"S{i}" for i in range(len(n50))]
    s = pl.Series("n50", n50, dtype=pl.Float64)
    return pl.DataFrame({"sample_id": ids, "country": ["Norway"] * len(ids), "n50": s, "n50_zscore": (s - s.mean()) / s.std()})


def long_table(drop_sample: str = None) -> pl.DataFrame:
    """Three measures per sample, no key (the trial's `Quast_with_metadata`)."""
    rows = [(s, m, float(v)) for s, base in (("S1", 10), ("S2", 20), ("S3", 30)) for m, v in (("N50", base), ("L50", base + 1), ("len", base + 2))]
    frame = pl.DataFrame(rows, schema=["sample_id", "measure", "value"], orient="row")
    return frame.filter(pl.col("sample_id") != drop_sample) if drop_sample else frame


# ----------------------------------------------------------------------------------------------------- layer 1

def test_equal_tables_say_equal_and_nothing_differs():
    c = compare(aggregate(), aggregate())
    assert c.equal is True
    assert (c.n_rows_original, c.n_rows_audited, c.n_columns_original, c.n_columns_audited) == (4, 4, 3, 3)
    assert c.columns_only_in_original == () and c.columns_only_in_audited == () and c.type_changes == ()
    assert c.only_in_original.total == 0 and c.only_in_audited.total == 0
    assert c.row_order_same is True


def test_two_empty_tables_are_equal():
    empty = pl.DataFrame({"a": pl.Series([], dtype=pl.Int64)})
    c = compare(empty, empty.clone())
    assert c.equal is True and c.n_rows_original == 0 and c.only_in_original.total == 0
    c0 = compare(pl.DataFrame(), pl.DataFrame())
    assert c0.equal is True and c0.n_columns_original == 0


def test_one_empty_table_lists_every_row_of_the_other():
    full, empty = aggregate(), aggregate().clear()
    c = compare(full, empty)
    assert c.equal is False and (c.n_rows_original, c.n_rows_audited) == (4, 0)
    assert c.only_in_original.total == 4 and c.only_in_audited.total == 0
    back = compare(empty, full)
    assert back.only_in_original.total == 0 and back.only_in_audited.total == 4


def test_a_row_removed_is_listed_as_only_in_the_original():
    original = long_table()
    c = compare(original, long_table(drop_sample="S2"))
    assert (c.n_rows_original, c.n_rows_audited) == (9, 6)
    assert c.only_in_original.total == 3 and c.only_in_audited.total == 0
    assert {r[0] for r in c.only_in_original.rows} == {"S2"}
    assert c.only_in_original.columns == ("sample_id", "measure", "value")
    assert c.equal is False


def test_duplicated_row_removed_once_is_seen():
    """A plain anti join on all columns sees nothing here; the counted comparison sees one row."""
    original = pl.DataFrame({"a": ["x", "x", "y"], "b": [1, 1, 2]})
    audited = pl.DataFrame({"a": ["x", "y"], "b": [1, 2]})
    c = compare(original, audited)
    assert c.only_in_original.rows == (("x", 1),) and c.only_in_audited.total == 0
    assert c.equal is False
    assert (compare(audited, original).only_in_audited.rows) == (("x", 1),)


def test_a_dropped_column_is_reported_with_the_diff_on_the_common_columns():
    original = pl.DataFrame({"sample_id": ["S1", "S2"], "country": ["Norway", "Sweden"], "n50": [1, 2]})
    audited = original.drop("country")
    c = compare(original, audited)
    assert c.columns_only_in_original == ("country",)
    assert c.columns_only_in_audited == ()
    assert c.common_columns == ("sample_id", "n50")
    assert c.only_in_original.total == 0 and c.only_in_audited.total == 0      # on the common columns nothing differs ...
    assert c.equal is False                                                     # ... and that is never read as "nothing differs"
    assert (c.n_columns_original, c.n_columns_audited) == (3, 2)


def test_an_added_column_is_reported():
    original = pl.DataFrame({"a": [1, 2]})
    audited = original.with_columns(b=pl.col("a") * 2)
    c = compare(original, audited)
    assert c.columns_only_in_audited == ("b",) and c.columns_only_in_original == ()
    assert c.only_in_original.total == 0 and c.equal is False


def test_a_changed_type_with_equal_values_is_said_and_not_compared_as_equal():
    original = pl.DataFrame({"k": ["a", "b"], "x": pl.Series([1, 2], dtype=pl.Int64)})
    audited = pl.DataFrame({"k": ["a", "b"], "x": pl.Series([1.0, 2.0], dtype=pl.Float64)})
    c = compare(original, audited)
    assert c.type_changes == (tc.TypeChange("x", "Int64", "Float64"),)
    assert c.equal is False
    assert "x" not in c.compared_columns and "k" in c.compared_columns


def test_a_changed_row_order_alone_is_reported_on_its_own_line():
    original = aggregate()
    audited = original.reverse()
    c = compare(original, audited)
    assert c.row_order_same is False
    assert c.only_in_original.total == 0 and c.only_in_audited.total == 0       # the content is the same
    assert c.equal is False


def test_the_same_order_after_a_removal_counts_as_the_same_order():
    original = aggregate()
    audited = original.filter(pl.col("country") != "Denmark")
    assert compare(original, audited).row_order_same is True


def test_null_equals_null_and_nan_equals_nan_in_the_same_place():
    original = pl.DataFrame({"a": [1, None, 3], "f": [NAN, 1.0, None]})
    c = compare(original, original.clone())
    assert c.equal is True and c.only_in_original.total == 0
    assert c.null_equals_null is True and c.nan_equals_nan is True


def test_null_and_nan_in_different_places_differ():
    original = pl.DataFrame({"a": [1, None, 3], "f": [NAN, 1.0, None]})
    audited = pl.DataFrame({"a": [1, 2, 3], "f": [NAN, 1.0, NAN]})        # None -> 2 in a; None -> NaN in f
    c = compare(original, audited)
    assert c.only_in_original.total == 2 and c.only_in_audited.total == 2
    assert c.equal is False


def test_list_and_struct_columns_are_compared():
    original = pl.DataFrame({"l": [[1, 2], [3], None, []], "s": [{"x": 1, "y": "a"}, {"x": 2, "y": "b"}, {"x": None, "y": None}, {"x": 5, "y": "e"}]})
    audited = pl.DataFrame({"l": [[1, 2], [3, 4], None, []], "s": [{"x": 1, "y": "a"}, {"x": 2, "y": "b"}, {"x": None, "y": None}, {"x": 5, "y": "e"}]})
    c = compare(original, audited)
    assert c.only_in_original.total == 1 and c.only_in_original.rows[0][0] == [3]
    assert c.only_in_audited.rows[0][0] == [3, 4]
    assert compare(original, original.clone()).equal is True


def test_a_column_named_like_an_internal_helper_works():
    original = pl.DataFrame({"_pos": [1, 2], "_occ": [3, 4], "__cmp_pos": [5, 6]})
    audited = pl.DataFrame({"_pos": [1], "_occ": [3], "__cmp_pos": [5]})
    c = compare(original, audited)
    assert c.only_in_original.rows == ((2, 4, 6),) and c.only_in_audited.total == 0


def test_categorical_columns_built_apart_are_compared_by_value():
    original = pl.DataFrame({"c": pl.Series(["a", "b", "b"], dtype=pl.Categorical)})
    audited = pl.DataFrame({"c": pl.Series(["b", "c"], dtype=pl.Categorical)})
    c = compare(original, audited)
    assert c.only_in_original.rows == (("a",), ("b",)) and c.only_in_audited.rows == (("c",),)


def test_compare_a_with_a_is_always_nothing_differs():
    for table in (aggregate(), long_table(), zscore([1, 2, 3, 4]), pl.DataFrame({"a": [None, None]}), pl.DataFrame({"f": [NAN, NAN, 1.0]})):
        c = compare(table, table, key_candidates=[tuple(table.columns[:1])])
        assert c.equal is True and c.row_order_same is True
        assert c.only_in_original.total == 0 and c.only_in_audited.total == 0
        if c.paired is not None:
            assert c.paired.removed.total == 0 and c.paired.added.total == 0 and c.paired.changed_cells.total == 0 and c.paired.n_rows_changed == 0


def test_swapping_the_two_tables_swaps_the_two_lists():
    a, b = long_table(), long_table(drop_sample="S3").with_columns(value=pl.when(pl.col("sample_id") == "S1").then(0.0).otherwise(pl.col("value")))
    ab, ba = compare(a, b), compare(b, a)
    assert ab.only_in_original.rows == ba.only_in_audited.rows and ab.only_in_audited.rows == ba.only_in_original.rows
    assert ab.columns_only_in_original == ba.columns_only_in_audited


def test_the_same_inputs_give_the_same_record():
    a, b = zscore([1, 2, 3, 4, 5]), zscore([1, 2, 3, 4, 5], samples=["S0", "S1", "S2", "S3", "S9"])
    assert compare(a, b, key_candidates=[("sample_id",)]) == compare(a, b, key_candidates=[("sample_id",)])


def test_the_two_lists_are_in_the_order_of_their_own_table():
    original = pl.DataFrame({"a": ["z", "y", "x", "w"]})
    audited = pl.DataFrame({"a": ["q", "p"]})
    c = compare(original, audited)
    assert c.only_in_original.rows == (("z",), ("y",), ("x",), ("w",))
    assert c.only_in_audited.rows == (("q",), ("p",))


# ----------------------------------------------------------------------------------------------------- limit and size guard

def test_a_list_longer_than_the_limit_is_cut_and_says_so():
    original = pl.DataFrame({"a": list(range(10))})
    c = compare(original, pl.DataFrame({"a": [100]}), limit=3)
    assert c.only_in_original.rows == ((0,), (1,), (2,)) and c.only_in_original.total == 10 and c.only_in_original.cut is True
    assert c.only_in_audited.rows == ((100,),) and c.only_in_audited.cut is False


def test_a_list_that_fits_the_limit_is_not_cut():
    original = pl.DataFrame({"a": [1, 2, 3]})
    c = compare(original, original.clear(), limit=3)
    assert c.only_in_original.cut is False and len(c.only_in_original.rows) == 3
    c0 = compare(original, original.clear(), limit=0)
    assert c0.only_in_original.rows == () and c0.only_in_original.total == 3 and c0.only_in_original.cut is True


def test_no_limit_means_no_cut():
    big = pl.DataFrame({"a": list(range(500))})
    c = compare(big, big.clear())
    assert len(c.only_in_original.rows) == 500 and c.only_in_original.cut is False


def test_a_negative_limit_is_refused():
    with pytest.raises(ValueError, match="limit"):
        compare(aggregate(), aggregate(), limit=-1)


def test_above_the_size_guard_layers_2_and_3_are_not_computed_and_layer_1_is():
    a, b = long_table(), long_table(drop_sample="S1")
    c = compare(a, b, key_candidates=[("sample_id", "measure")], max_cells=10)
    assert c.not_computed is not None and c.not_computed.reason == tc.NOT_COMPUTED_SIZE
    assert c.not_computed.cells == 27 and c.not_computed.max_cells == 10
    assert c.only_in_original is None and c.only_in_audited is None and c.row_order_same is None and c.paired is None
    assert c.key_status == tc.KEY_NOT_COMPUTED
    assert (c.n_rows_original, c.n_rows_audited) == (9, 6)
    assert c.equal is False and c.common_columns == ("sample_id", "measure", "value")


def test_at_the_size_guard_exactly_it_is_computed():
    a = long_table()
    c = compare(a, a, max_cells=27)
    assert c.not_computed is None and c.only_in_original.total == 0


def test_the_guard_looks_at_the_larger_of_the_two_tables():
    c = compare(long_table(), long_table(drop_sample="S1"), max_cells=20)
    assert c.not_computed is not None and c.not_computed.cells == 27


def test_no_comparable_column_is_said_not_guessed():
    c = compare(pl.DataFrame({"a": [1]}), pl.DataFrame({"b": [1]}))
    assert c.not_computed.reason == tc.NOT_COMPUTED_NO_COLUMNS and c.only_in_original is None
    assert c.columns_only_in_original == ("a",) and c.columns_only_in_audited == ("b",) and c.equal is False


# ----------------------------------------------------------------------------------------------------- layer 3: the key

def test_a_group_value_changed_with_a_key_names_the_group_and_the_cell():
    c = compare(aggregate(19), aggregate(18), key_candidates=[("country", "year_label")])
    assert c.key_status == tc.KEY_USED and c.key_used == ("country", "year_label") and c.key_rejections == ()
    p = c.paired
    assert p.n_paired == 4 and p.n_rows_changed == 1
    assert p.removed.total == 0 and p.added.total == 0
    assert p.changed_cells.cells == (tc.CellChange(("Norway", "2024"), "n_samples", 19, 18),)
    assert p.changed_cells.key_columns == ("country", "year_label")
    n = {col.column: col for col in p.columns}
    assert (n["n_samples"].n_changed, n["n_samples"].n_paired, n["n_samples"].smallest_change, n["n_samples"].largest_change) == (1, 4, -1.0, -1.0)


def test_a_group_value_changed_without_a_key_is_two_lines():
    c = compare(aggregate(19), aggregate(18))
    assert c.key_status == tc.KEY_NO_CANDIDATES and c.paired is None and c.key_rejections == ()
    assert c.only_in_original.rows == (("Norway", "2024", 19),) and c.only_in_audited.rows == (("Norway", "2024", 18),)


def test_a_removed_sample_is_a_removed_row_and_the_others_changed_cells_with_a_key():
    original = zscore([10.0, 20.0, 30.0, 40.0, 50.0])
    audited = zscore([10.0, 20.0, 40.0, 50.0], samples=["S0", "S1", "S3", "S4"])       # S2 removed upstream
    c = compare(original, audited, key_candidates=[("sample_id",)])
    p = c.paired
    assert p.n_paired == 4 and p.removed.total == 1 and p.removed.rows[0][0] == "S2" and p.added.total == 0
    assert p.removed.columns == tuple(original.columns)
    by_col = {col.column: col for col in p.columns}
    assert by_col["n50_zscore"].n_changed == 4 and by_col["n50"].n_changed == 0
    assert by_col["n50"].smallest_change is None and by_col["n50"].largest_change is None
    assert by_col["n50_zscore"].smallest_change is not None and by_col["n50_zscore"].smallest_change <= by_col["n50_zscore"].largest_change
    assert p.n_rows_changed == 4
    assert {cell.column for cell in p.changed_cells.cells} == {"n50_zscore"} and p.changed_cells.total == 4


def test_every_row_changed_without_a_key_lists_every_row():
    original = zscore([10.0, 20.0, 30.0, 40.0, 50.0])
    audited = zscore([10.0, 20.0, 40.0, 50.0], samples=["S0", "S1", "S3", "S4"])
    c = compare(original, audited)
    assert c.only_in_original.total == 5 and c.only_in_audited.total == 4


def test_a_row_added_is_listed_with_its_whole_audited_row():
    original, audited = aggregate(), aggregate().vstack(pl.DataFrame({"country": ["Finland"], "year_label": ["2024"], "n_samples": [2]}))
    p = compare(original, audited, key_candidates=[("country", "year_label")]).paired
    assert p.added.rows == (("Finland", "2024", 2),) and p.removed.total == 0 and p.n_paired == 4


def test_the_smallest_and_largest_change_of_a_numeric_column_are_signed():
    original = pl.DataFrame({"k": [1, 2, 3], "v": [10.0, 20.0, 30.0]})
    audited = pl.DataFrame({"k": [1, 2, 3], "v": [9.0, 20.0, 32.5]})
    v = {col.column: col for col in compare(original, audited, key_candidates=[("k",)]).paired.columns}["v"]
    assert (v.n_changed, v.smallest_change, v.largest_change) == (2, -1.0, 2.5)


def test_a_text_column_that_changed_counts_without_a_size_of_change():
    original = pl.DataFrame({"k": [1, 2], "t": ["a", "b"]})
    audited = pl.DataFrame({"k": [1, 2], "t": ["a", "c"]})
    p = compare(original, audited, key_candidates=[("k",)]).paired
    assert p.changed_cells.cells == (tc.CellChange((2,), "t", "b", "c"),)
    t = p.columns[0]
    assert t.n_changed == 1 and t.smallest_change is None


def test_unsigned_integers_do_not_wrap_in_the_size_of_a_change():
    original = pl.DataFrame({"k": [1], "u": pl.Series([5], dtype=pl.UInt8)})
    audited = pl.DataFrame({"k": [1], "u": pl.Series([3], dtype=pl.UInt8)})
    u = compare(original, audited, key_candidates=[("k",)]).paired.columns[0]
    assert u.smallest_change == -2.0


def test_changes_to_and_from_missing_values_are_changed_cells_without_a_size():
    original = pl.DataFrame({"k": [1, 2, 3], "v": [1.0, None, NAN]})
    audited = pl.DataFrame({"k": [1, 2, 3], "v": [None, 2.0, NAN]})
    p = compare(original, audited, key_candidates=[("k",)]).paired
    assert [cell.key for cell in p.changed_cells.cells] == [(1,), (2,)]
    assert p.columns[0].n_changed == 2 and p.columns[0].smallest_change is None


def test_the_list_of_changed_cells_is_cut_by_the_limit_and_says_so():
    original = pl.DataFrame({"k": list(range(10)), "a": list(range(10)), "b": list(range(10))})
    audited = pl.DataFrame({"k": list(range(10)), "a": [x + 1 for x in range(10)], "b": [x + 1 for x in range(10)]})
    p = compare(original, audited, key_candidates=[("k",)], limit=3).paired
    assert p.changed_cells.total == 20 and p.changed_cells.cut is True and len(p.changed_cells.cells) == 3
    assert [(cell.key, cell.column) for cell in p.changed_cells.cells] == [((0,), "a"), ((0,), "b"), ((1,), "a")]   # by row of the original, then column order
    assert p.n_rows_changed == 10 and {col.column: col.n_changed for col in p.columns} == {"a": 10, "b": 10}


def test_a_key_with_a_null_is_rejected_with_the_count():
    original = pl.DataFrame({"k": [1, None, 3], "v": [1, 2, 3]})
    c = compare(original, original.clone(), key_candidates=[("k",)])
    assert c.key_status == tc.KEY_NONE_USABLE and c.paired is None and c.key_used is None
    r = c.key_rejections[0]
    assert (r.columns, r.check, r.table, r.count) == (("k",), tc.CHECK_HAS_NULL, "original", 1) and r.reason
    assert c.only_in_original.total == 0                                         # layers 1 and 2 are still returned


def test_a_key_that_is_not_unique_in_one_table_only_is_rejected_naming_it():
    original = pl.DataFrame({"k": [1, 2, 3], "v": [1, 2, 3]})
    audited = pl.DataFrame({"k": [1, 2, 2], "v": [1, 2, 3]})
    r = compare(original, audited, key_candidates=[("k",)]).key_rejections[0]
    assert (r.check, r.table, r.count) == (tc.CHECK_NOT_UNIQUE, "audited", 2) and "2" in r.reason


def test_a_key_that_is_not_unique_in_both_tables_names_both():
    t = pl.DataFrame({"k": [1, 1, 2]})
    r = compare(t, t.clone(), key_candidates=[("k",)]).key_rejections[0]
    assert r.check == tc.CHECK_NOT_UNIQUE and r.table == "both"


def test_a_key_column_missing_in_one_table_is_rejected():
    original = pl.DataFrame({"k": [1, 2], "v": [1, 2]})
    audited = original.rename({"k": "id"})
    r = compare(original, audited, key_candidates=[("k",)]).key_rejections[0]
    assert (r.check, r.table) == (tc.CHECK_MISSING, "audited") and "k" in r.reason


def test_a_key_column_missing_in_both_tables_is_rejected_for_both():
    r = compare(aggregate(), aggregate(), key_candidates=[("nothing",)]).key_rejections[0]
    assert (r.check, r.table) == (tc.CHECK_MISSING, "both")


def test_a_key_whose_type_differs_is_rejected():
    original = pl.DataFrame({"k": [1, 2]})
    audited = pl.DataFrame({"k": ["1", "2"]})
    r = compare(original, audited, key_candidates=[("k",)]).key_rejections[0]
    assert r.check == tc.CHECK_TYPE_DIFFERS and "Int64" in r.reason and "String" in r.reason


def test_a_key_of_a_nested_type_is_rejected():
    t = pl.DataFrame({"k": [[1], [2]]})
    assert compare(t, t.clone(), key_candidates=[("k",)]).key_rejections[0].check == tc.CHECK_NESTED


def test_an_empty_candidate_is_rejected_not_used():
    r = compare(aggregate(), aggregate(), key_candidates=[()]).key_rejections[0]
    assert r.check == tc.CHECK_EMPTY


def test_the_first_candidate_that_passes_is_used_and_the_failed_ones_are_named():
    original = pl.DataFrame({"country": ["N", "N", "S"], "sample_id": ["a", "b", "c"], "v": [1, 2, 3]})
    audited = pl.DataFrame({"country": ["N", "N", "S"], "sample_id": ["a", "b", "c"], "v": [1, 5, 3]})
    c = compare(original, audited, key_candidates=[("country",), ("nope",), ("sample_id",), ("sample_id", "country")])
    assert c.key_used == ("sample_id",) and c.key_status == tc.KEY_USED
    assert [(r.columns, r.check) for r in c.key_rejections] == [(("country",), tc.CHECK_NOT_UNIQUE), (("nope",), tc.CHECK_MISSING)]
    assert c.paired.changed_cells.cells == (tc.CellChange(("b",), "v", 2, 5),)


def test_a_long_table_with_no_usable_key_gets_layers_1_and_2_only():
    c = compare(long_table(), long_table(drop_sample="S2"), key_candidates=[("sample_id",)])
    assert c.key_status == tc.KEY_NONE_USABLE and c.paired is None
    assert c.key_rejections[0].check == tc.CHECK_NOT_UNIQUE and c.key_rejections[0].count == 9
    assert c.only_in_original.total == 3                                        # S2's three rows, with the id


def test_a_composite_key_that_is_unique_pairs_the_long_table():
    c = compare(long_table(), long_table(drop_sample="S2"), key_candidates=[("sample_id",), ("sample_id", "measure")])
    assert c.key_used == ("sample_id", "measure") and c.paired.removed.total == 3 and c.paired.n_paired == 6


def test_no_key_is_ever_guessed_from_the_data():
    """A unique column is NOT used unless the caller lists it: the module never searches for a key."""
    c = compare(aggregate(19), aggregate(18))
    assert c.key_status == tc.KEY_NO_CANDIDATES and c.key_used is None


def test_rows_are_never_paired_by_position_or_by_a_single_differing_column():
    """The trials' S5 paired a removed `France|2022|7` with a new `France|2023|7` as 'year changed': that is not built."""
    original = pl.DataFrame({"country": ["France", "Norway"], "year": ["2022", "2024"], "n": [7, 19]})
    audited = pl.DataFrame({"country": ["France", "Norway"], "year": ["2023", "2024"], "n": [7, 19]})
    c = compare(original, audited)
    assert c.only_in_original.rows == (("France", "2022", 7),) and c.only_in_audited.rows == (("France", "2023", 7),)
    assert c.paired is None
    p = compare(original, audited, key_candidates=[("country", "year")]).paired
    assert p.removed.rows == (("France", "2022", 7),) and p.added.rows == (("France", "2023", 7),) and p.changed_cells.total == 0


def test_a_dropped_non_key_column_is_stated_beside_the_paired_view():
    original = pl.DataFrame({"k": [1, 2], "a": [1, 2], "b": [3, 4]})
    audited = original.drop("b")
    c = compare(original, audited, key_candidates=[("k",)])
    assert c.columns_only_in_original == ("b",)
    assert c.paired.changed_cells.total == 0 and [col.column for col in c.paired.columns] == ["a"]


def test_a_key_column_that_was_dropped_is_a_rejected_candidate_not_a_silent_no_change():
    original = pl.DataFrame({"k": [1, 2], "a": [1, 2]})
    c = compare(original, original.drop("k"), key_candidates=[("k",)])
    assert c.key_rejections[0].check == tc.CHECK_MISSING and c.columns_only_in_original == ("k",)


def test_the_key_check_works_on_empty_tables():
    empty = pl.DataFrame({"k": pl.Series([], dtype=pl.Int64), "v": pl.Series([], dtype=pl.Int64)})
    full = pl.DataFrame({"k": [1, 2], "v": [1, 2]})
    c = compare(full, empty, key_candidates=[("k",)])
    assert c.key_used == ("k",) and c.paired.removed.total == 2 and c.paired.n_paired == 0
    assert compare(empty, empty.clone(), key_candidates=[("k",)]).paired.n_paired == 0


def test_a_key_with_a_nan_float_is_refused_as_not_unique_or_accepted_but_never_wrong():
    """NaN equals NaN here, so two NaN keys are two rows that share a value: the key is not unique."""
    t = pl.DataFrame({"k": [NAN, NAN, 1.0], "v": [1, 2, 3]})
    assert compare(t, t.clone(), key_candidates=[("k",)]).key_rejections[0].check == tc.CHECK_NOT_UNIQUE


def test_swapping_the_two_tables_swaps_removed_and_added_and_before_and_after():
    a, b = aggregate(19), aggregate(18).filter(pl.col("country") != "Sweden")
    ab = compare(a, b, key_candidates=[("country", "year_label")]).paired
    ba = compare(b, a, key_candidates=[("country", "year_label")]).paired
    assert ab.removed.rows == ba.added.rows and ab.added.rows == ba.removed.rows
    assert [(c.key, c.column, c.before, c.after) for c in ab.changed_cells.cells] == [(c.key, c.column, c.after, c.before) for c in ba.changed_cells.cells]


def test_a_column_named_like_the_audited_suffix_does_not_break_the_pairing():
    original = pl.DataFrame({"k": [1, 2], "v": [1, 2], "v__audited": [5, 6]})
    audited = pl.DataFrame({"k": [1, 2], "v": [1, 9], "v__audited": [5, 6]})
    p = compare(original, audited, key_candidates=[("k",)]).paired
    assert p.changed_cells.cells == (tc.CellChange((2,), "v", 2, 9),)


# ----------------------------------------------------------------------------------------------------- the record

def test_the_record_is_plain_data():
    c = compare(aggregate(19), aggregate(18), key_candidates=[("country", "year_label")])
    for value in (c.only_in_original.rows, c.paired.changed_cells.cells, c.type_changes, c.common_columns):
        assert isinstance(value, tuple)
    assert not any(isinstance(v, (pl.DataFrame, pl.Series)) for v in vars(c).values())
    with pytest.raises(Exception):
        c.equal = False                                                          # frozen


def test_the_comparison_states_that_it_is_exact():
    assert compare(aggregate(), aggregate()).exact is True


# ----------------------------------------------------------------------------------------------------- the four kinds of table of the trials

def test_the_four_kinds_with_one_sample_removed_upstream():
    """What the trials showed on the demo, on small tables: the aggregate, the value over all samples, one row per sample, the long table."""
    kinds = {}
    kinds["aggregate"] = compare(aggregate(19), aggregate(18), key_candidates=[("country", "year_label")])
    original = zscore([10.0, 20.0, 30.0, 40.0, 50.0])
    audited = zscore([10.0, 20.0, 40.0, 50.0], samples=["S0", "S1", "S3", "S4"])
    kinds["zscore"] = compare(original, audited, key_candidates=[("sample_id",)])
    per_sample = pl.DataFrame({"sample_id": ["S0", "S1", "S2"], "country": ["N", "N", "S"], "n_genes": [3, 0, 2]})
    kinds["per_sample"] = compare(per_sample, per_sample.filter(pl.col("sample_id") != "S2"), key_candidates=[("sample_id", "country"), ("sample_id",)])
    kinds["long"] = compare(long_table(), long_table(drop_sample="S2"), key_candidates=[("sample_id",)])
    assert kinds["aggregate"].paired.changed_cells.total == 1
    assert kinds["zscore"].paired.removed.total == 1 and kinds["zscore"].paired.changed_cells.total == 4
    assert kinds["per_sample"].paired.removed.total == 1 and kinds["per_sample"].paired.changed_cells.total == 0
    assert kinds["per_sample"].key_used == ("sample_id", "country")
    assert kinds["long"].paired is None and kinds["long"].only_in_original.total == 3


# ----------------------------------------------------------------------------------------------------- the cases it cannot catch

def test_the_list_of_limits_is_plain_text_with_one_test_each():
    assert len(CANNOT_CATCH) >= 6
    codes = [item.code for item in CANNOT_CATCH]
    assert len(set(codes)) == len(codes)
    for item in CANNOT_CATCH:
        assert item.sentence.strip().endswith(".") and len(item.sentence) > 30
        assert callable(globals().get(f"test_limit_{item.code}")), f"no test shows the limit {item.code!r}"


def test_limit_why_a_value_moved():
    """19 -> 18: the record names the group and the numbers; the removed sample is not a row of the table, so it is nowhere in the record."""
    c = compare(aggregate(19), aggregate(18), key_candidates=[("country", "year_label")])
    assert c.paired.changed_cells.cells == (tc.CellChange(("Norway", "2024"), "n_samples", 19, 18),)
    assert c.paired.removed.total == 0 and c.paired.added.total == 0         # nothing says that a sample was removed upstream
    assert not hasattr(c, "reason") and not hasattr(c.paired, "reason")


def test_limit_a_value_over_all_samples_moves_every_row():
    original = zscore([10.0, 20.0, 30.0, 40.0, 50.0])
    audited = zscore([10.0, 20.0, 40.0, 50.0], samples=["S0", "S1", "S3", "S4"])
    c = compare(original, audited)
    assert c.only_in_original.total == 5 and c.only_in_audited.total == 4     # the removed sample is one line among all of them


def test_limit_a_unique_key_may_pair_rows_that_do_not_mean_the_same():
    """The means are unique in both tables, so the key is verified; but group A of the original and group B of the audited table are not the same thing."""
    original = pl.DataFrame({"mean": [1.5, 2.5], "group": ["A", "B"]})
    audited = pl.DataFrame({"mean": [1.5, 2.5], "group": ["C", "B"]})
    c = compare(original, audited, key_candidates=[("mean",)])
    assert c.key_status == tc.KEY_USED
    assert c.paired.changed_cells.cells == (tc.CellChange((1.5,), "group", "A", "C"),)    # read as "group A became C", not as "A removed, C added"


def test_limit_the_comparison_is_exact():
    one_step_up = math.nextafter(1.0, 2.0)
    c = compare(pl.DataFrame({"x": [1.0]}), pl.DataFrame({"x": [one_step_up]}))
    assert c.equal is False and c.only_in_original.total == 1 and c.exact is True


def test_limit_it_compares_two_tables_and_knows_nothing_of_the_steps():
    import inspect
    assert list(inspect.signature(compare).parameters)[:2] == ["original", "audited"]
    assert not any("step" in name or "recipe" in name for name in inspect.signature(compare).parameters)
    original = aggregate()
    removed_and_put_back = pl.concat([original.head(2), original.tail(2)])
    assert compare(original, removed_and_put_back).equal is True              # a step that removed and re-added a row leaves no trace


def test_limit_a_column_whose_type_changed_is_not_compared_by_value():
    original = pl.DataFrame({"k": [1, 2], "x": pl.Series([1, 2], dtype=pl.Int64)})
    audited = pl.DataFrame({"k": [1, 2], "x": pl.Series([1.0, 99.0], dtype=pl.Float64)})
    c = compare(original, audited, key_candidates=[("k",)])
    assert c.type_changes and c.only_in_original.total == 0 and c.paired.changed_cells.total == 0     # the value that changed to 99.0 is not listed


def test_limit_a_renamed_column_is_a_drop_and_an_add():
    original = pl.DataFrame({"k": [1, 2], "old_name": [5, 6]})
    audited = original.rename({"old_name": "new_name"})
    c = compare(original, audited)
    assert c.columns_only_in_original == ("old_name",) and c.columns_only_in_audited == ("new_name",)


# ----------------------------------------------------------------------------------------------------- the module is engine work and says so

def test_the_module_carries_its_engine_mark_and_is_listed():
    from utils.engine_boundary import PLACES
    place = next(p for p in PLACES if p.path == "libs/utils/src/utils/table_compare.py")
    assert place.engines == ("python-polars",)
    first = open(tc.__file__, encoding="utf-8").read().splitlines()[0]
    assert first == place.mark
