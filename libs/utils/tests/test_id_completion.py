"""The completion of the ids (D-0572 to D-0599, D-0613): the pure parts, on small tables.

What is checked: who takes part (the metadata and the tables of `data_schemas` that declare an entity id, never an additional table), the block each of them
must carry (E04 to E07, and the engine refuses the same), the ids as read (a line with no usable id is not an id), the completion itself (lines added both ways, the
union, no metadata, nothing removed, the marker is a yes/no column, the same input gives the same table), and the three checks of the ids.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_id_completion.py -q
"""
import copy

import polars as pl
import pytest

from utils.errors import DataAnalysisRecipeError
from utils.id_completion import (Participant, TableIds, build_report, complete_table, completion_problems, participant_of, participants, read_ids,
                                 report_lines, union_of)
from utils.recipe_check import check_recipe, spec

DATA_BLOCK = {"marker": "not_in_original_data", "meaning": "no result for this entity"}
META_BLOCK = {"marker": "not_in_metadata", "meaning": "no metadata for this entity"}


def schema(*, id_declared=True, block=None, extra_fields=None):
    fields = {"sample_id": {"type": "String", **({"is_entity_id": True} if id_declared else {})}, "v": {"type": "Float64"}, **(extra_fields or {})}
    out = {"ui_label": "T", "description": "d", "source": {"type": "local_tsv", "path": "x.tsv"}, "null_values": [], "strip": True,
           "input_fields": fields, "tier1": {"steps": []}}
    if block is not None:
        out["completion"] = copy.deepcopy(block)
    return out


def recipe(*, metadata=True, tables=("A", "B"), additional=False):
    raw = {"id": "r", "data_schemas": {t: schema(block={**DATA_BLOCK, "marker": f"{t}_not_in_original_data"}) for t in tables}}
    if metadata:
        raw["metadata_schema"] = schema(block=META_BLOCK)
    if additional:
        raw["additional_datasets_schemas"] = {"L": schema()}
    return raw


def codes(raw):
    return sorted({c for c, _, _, _ in completion_problems(raw, spec())})


# -- who takes part ------------------------------------------------------------------------------

def test_the_metadata_comes_first_then_the_data_tables_in_the_order_written():
    parts = participants(recipe(tables=("B", "A")))
    assert [(p.table, p.kind) for p in parts] == [("metadata_schema", "metadata"), ("B", "data"), ("A", "data")]
    assert parts[0] == Participant("metadata_schema", "metadata", "sample_id", "not_in_metadata", "no metadata for this entity")


def test_an_additional_table_never_takes_part_even_when_it_declares_an_entity_id():
    raw = recipe(additional=True)
    assert [p.table for p in participants(raw)] == ["metadata_schema", "A", "B"]
    assert participant_of(raw, "L") is None


def test_a_table_that_declares_no_entity_id_does_not_take_part():
    raw = recipe()
    raw["data_schemas"]["B"] = schema(id_declared=False)
    assert [p.table for p in participants(raw)] == ["metadata_schema", "A"]


def test_a_recipe_with_no_entity_id_has_no_participant():
    raw = {"data_schemas": {"A": schema(id_declared=False)}}
    assert participants(raw) == []


def test_the_first_declared_entity_id_is_the_id_column():
    raw = recipe(tables=("A",), metadata=False)
    raw["data_schemas"]["A"]["input_fields"] = {"x": {"type": "String", "is_entity_id": True}, "sample_id": {"type": "String", "is_entity_id": True}}
    assert participants(raw)[0].id_column == "x"


# -- what the recipe must say --------------------------------------------------------------------

def test_a_table_with_an_entity_id_and_no_block_is_refused_E04_and_the_engine_refuses_too():
    raw = recipe(tables=("A",), metadata=False)
    del raw["data_schemas"]["A"]["completion"]
    assert codes(raw) == ["E04"]
    with pytest.raises(DataAnalysisRecipeError) as error:
        participants(raw)
    assert "'A'" in str(error.value) and "completion" in str(error.value) and "no result for this entity" in error.value.tip


def test_an_unknown_meaning_is_refused_E05_and_the_message_lists_the_words():
    raw = recipe(tables=("A",), metadata=False)
    raw["data_schemas"]["A"]["completion"]["meaning"] = "zero"
    found = [p for p in completion_problems(raw, spec()) if p[0] == "E05"]
    assert len(found) == 1 and "no result for this entity" in found[0][3] and "'zero'" in found[0][2]


def test_a_meaning_of_the_other_kind_is_refused():
    raw = recipe()
    raw["metadata_schema"]["completion"]["meaning"] = "no result for this entity"   # a word for a data table
    assert codes(raw) == ["E05"]


@pytest.mark.parametrize("block", [{"marker": "not_in_original_data"}, {"meaning": "unknown"}, {"marker": "m", "meaning": "unknown", "count": 3}, "text"])
def test_a_block_with_a_missing_or_unknown_key_or_not_a_mapping_is_refused_E05(block):
    raw = recipe(tables=("A",), metadata=False)
    raw["data_schemas"]["A"]["completion"] = block
    assert codes(raw) == ["E05"]


@pytest.mark.parametrize("marker", ["Not In", "1abc", "has space", "", None, 5])
def test_a_marker_that_is_not_a_column_name_is_refused_E06(marker):
    raw = recipe(tables=("A",), metadata=False)
    raw["data_schemas"]["A"]["completion"]["marker"] = marker
    assert "E06" in codes(raw)


def test_two_tables_never_share_a_marker_E06_and_the_message_names_both():
    raw = recipe(tables=("A", "B"), metadata=False)
    raw["data_schemas"]["B"]["completion"]["marker"] = "A_not_in_original_data"
    found = [p for p in completion_problems(raw, spec()) if p[0] == "E06"]
    assert len(found) == 1 and "'B'" in found[0][2] and "'A'" in found[0][2] and "B_A_not_in_original_data" in found[0][3]


def test_a_marker_may_be_written_with_capitals_like_a_table_id():
    raw = recipe(tables=("FastP",), metadata=False)
    assert codes(raw) == [] and participants(raw)[0].marker == "FastP_not_in_original_data"


def test_a_marker_that_is_already_a_field_of_the_table_is_refused_E06():
    raw = recipe(tables=("A",), metadata=False)
    raw["data_schemas"]["A"]["completion"]["marker"] = "v"
    assert codes(raw) == ["E06"]


def test_a_block_where_nothing_is_completed_is_refused_E07():
    raw = recipe(additional=True)
    raw["additional_datasets_schemas"]["L"]["completion"] = copy.deepcopy(DATA_BLOCK)
    raw["data_schemas"]["B"]["input_fields"]["sample_id"].pop("is_entity_id")   # B declares no id: its block does nothing
    assert codes(raw) == ["E07"]
    assert len([p for p in completion_problems(raw, spec()) if p[0] == "E07"]) == 2


def test_the_checker_reports_the_same_codes_as_the_function_the_engine_reads():
    raw = {"id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine", "info": {"ui_label": "R"},
           "data_schemas": {"A": schema(block=None)}, "analysis_groups": {}}
    assert "E04" in {p.code for p in check_recipe(raw, "build", file_stem="r").problems}


# -- the ids as read -----------------------------------------------------------------------------

def part(table="A", kind="data", column="sample_id"):
    return Participant(table, kind, column, "not_in_original_data" if kind == "data" else "not_in_metadata", "unknown")


def test_a_line_with_no_usable_id_is_not_an_id_and_is_listed_by_its_line_number():
    lf = pl.LazyFrame({"sample_id": ["S1", None, "S2", "", "   ", "S1"], "v": [1.0] * 6})
    got = read_ids(lf, part())
    assert got.ids == ("S1", "S2") and got.no_id_lines == (2, 4, 5) and got.rows == 6


def test_an_id_is_compared_as_written_not_changed():
    lf = pl.LazyFrame({"sample_id": ["s1", "S1", " S1"], "v": [1.0] * 3})
    assert read_ids(lf, part()).ids == (" S1", "S1", "s1")   # three ids: nothing is lowered or trimmed here (the recipe's `strip` does that at the read)


def test_a_categorical_id_is_read_as_text():
    lf = pl.LazyFrame({"sample_id": pl.Series(["b", "a", "a"], dtype=pl.Categorical), "v": [1.0, 2.0, 3.0]})
    assert read_ids(lf, part()).ids == ("a", "b")


def test_an_empty_table_has_no_id():
    got = read_ids(pl.LazyFrame({"sample_id": pl.Series([], dtype=pl.String)}), part())
    assert got.ids == () and got.rows == 0 and got.no_id_lines == ()


def test_the_union_is_the_sorted_union_of_the_usable_ids_of_all_tables():
    a = TableIds("A", "data", "sample_id", 2, ("S2", "S1"), ())
    b = TableIds("B", "data", "sample_id", 1, ("S3",), (4,))
    assert union_of([a, b]) == ("S1", "S2", "S3")
    assert union_of([]) == ()


# -- the completion ------------------------------------------------------------------------------

def table_a():
    return pl.LazyFrame({"sample_id": ["S1", "S2", "S2"], "v": [1.0, 2.0, 3.0], "w": ["x", "y", "z"]})


def test_the_missing_ids_are_added_after_the_own_lines_with_every_other_value_missing_and_the_marker_true():
    done = complete_table(table_a(), part(), ("S1", "S2", "S3", "S4"), ("S1", "S2")).collect()
    assert done.columns == ["sample_id", "v", "w", "not_in_original_data"]
    assert done["sample_id"].to_list() == ["S1", "S2", "S2", "S3", "S4"]
    assert done["not_in_original_data"].to_list() == [False, False, False, True, True]
    assert done["v"].to_list() == [1.0, 2.0, 3.0, None, None] and done["w"].to_list() == ["x", "y", "z", None, None]
    assert done.schema["not_in_original_data"] == pl.Boolean and done.schema["v"] == pl.Float64


def test_nothing_is_removed_or_changed_and_the_own_lines_keep_their_order():
    own = table_a().collect()
    done = complete_table(table_a(), part(), ("S0", "S1", "S2", "S9"), ("S1", "S2")).collect()
    assert done.head(3).drop("not_in_original_data").equals(own)
    assert done["sample_id"].to_list()[3:] == ["S0", "S9"]    # the added lines are in the order of the ids


def test_a_complete_table_gets_the_marker_all_false_and_no_line():
    done = complete_table(table_a(), part(), ("S1", "S2"), ("S1", "S2")).collect()
    assert done.height == 3 and done["not_in_original_data"].to_list() == [False] * 3


def test_the_same_input_gives_the_same_table_twice():
    first = complete_table(table_a(), part(), ("S1", "S3"), ("S1", "S2")).collect()
    second = complete_table(table_a(), part(), ("S1", "S3"), ("S1", "S2")).collect()
    assert first.equals(second)


def test_a_line_with_no_usable_id_stays_and_is_not_completed():
    lf = pl.LazyFrame({"sample_id": ["S1", None, ""], "v": [1.0, 2.0, 3.0]})
    got = read_ids(lf, part())
    done = complete_table(lf, part(), ("S1", "S2"), got.ids).collect()
    assert done["sample_id"].to_list() == ["S1", None, "", "S2"]    # the two lines stay as they are; S2 is added once
    assert done["not_in_original_data"].to_list() == [False, False, False, True]


def test_a_categorical_id_column_keeps_its_type():
    lf = pl.LazyFrame({"sample_id": pl.Series(["a"], dtype=pl.Categorical), "v": [1.0]})
    done = complete_table(lf, part(), ("a", "b"), ("a",)).collect()
    assert done.schema["sample_id"] == pl.Categorical and done["sample_id"].cast(pl.String).to_list() == ["a", "b"]


def test_an_id_that_the_declared_type_cannot_hold_is_a_plain_error_that_names_the_table():
    lf = pl.LazyFrame({"sample_id": pl.Series(["a"], dtype=pl.Enum(["a"])), "v": [1.0]})
    with pytest.raises(DataAnalysisRecipeError) as error:
        complete_table(lf, part(), ("a", "zzz"), ("a",))
    assert "'A'" in str(error.value) and "sample_id" in str(error.value)


def test_a_marker_that_is_already_a_column_is_refused():
    with pytest.raises(DataAnalysisRecipeError):
        complete_table(table_a().with_columns(pl.lit(1).alias("not_in_original_data")), part(), ("S1",), ("S1",))


# -- the three checks ----------------------------------------------------------------------------

def ids(table, kind, values, no_id=()):
    return TableIds(table, kind, "sample_id", len(values) + len(no_id), tuple(sorted(values)), tuple(no_id))


def test_check_1_check_2_and_the_ids_added_per_table_with_a_metadata():
    parts = [part("metadata_schema", "metadata"), part("A"), part("B")]
    read = [ids("metadata_schema", "metadata", ["S1", "S2", "S3"]), ids("A", "data", ["S1", "S2", "S3"]), ids("B", "data", ["S1", "S9"])]
    report = build_report(parts, read)
    by = {t.table: t for t in report.tables}
    assert report.has_metadata and report.union_count == 4 and not report.completed
    assert by["B"].not_in_metadata == ("S9",) and by["B"].missing_from_table == ("S2", "S3")
    assert by["B"].added == ("S2", "S3") and by["A"].added == ("S9",) and by["metadata_schema"].added == ("S9",)
    assert by["A"].not_in_metadata == () and by["A"].missing_from_table == ()
    assert by["metadata_schema"].not_in_metadata is None and by["metadata_schema"].missing_from_table is None


def test_without_a_metadata_the_tables_complete_each_other_and_checks_1_and_2_do_not_apply():
    parts = [part("A"), part("B")]
    report = build_report(parts, [ids("A", "data", ["S1"]), ids("B", "data", ["S2"])])
    assert not report.has_metadata and report.tables[0].not_in_metadata is None and report.tables[0].added == ("S2",)


def test_check_3_passes_when_every_table_holds_the_union_after_the_completion():
    parts = [part("metadata_schema", "metadata"), part("A")]
    read = [ids("metadata_schema", "metadata", ["S1", "S2"]), ids("A", "data", ["S1"])]
    after = [ids("metadata_schema", "metadata", ["S1", "S2"]), ids("A", "data", ["S1", "S2"])]
    report = build_report(parts, read, after)
    assert report.completed and report.check3_ok and report.as_dict()["check_3"] == "passed"


def test_check_3_fails_and_says_it_is_a_bug_when_a_table_does_not_hold_the_union():
    parts = [part("metadata_schema", "metadata"), part("A")]
    read = [ids("metadata_schema", "metadata", ["S1", "S2"]), ids("A", "data", ["S1"])]
    broken = [ids("metadata_schema", "metadata", ["S1", "S2"]), ids("A", "data", ["S1"])]   # A was not completed
    report = build_report(parts, read, broken)
    assert not report.check3_ok and report.tables[1].after_difference == ("S2",)
    assert "FAILED: a bug of the app" in report.as_dict()["check_3"]
    assert any("BUG OF THE APP" in line and "A" in line for line in report_lines(report))


def test_equal_ids_say_nothing_and_a_difference_is_in_plain_words():
    parts = [part("metadata_schema", "metadata"), part("A")]
    same = [ids("metadata_schema", "metadata", ["S1"]), ids("A", "data", ["S1"])]
    assert report_lines(build_report(parts, same, same)) == [] and not build_report(parts, same, same).differs
    other = [ids("metadata_schema", "metadata", ["S1", "S2"]), ids("A", "data", ["S1"], no_id=(3,))]
    text = " ".join(report_lines(build_report(parts, other)))
    assert "1 line(s) have no usable id (line numbers 3)" in text and "1 id(s) of the metadata are not in this table: S2" in text
    assert "1 line(s) were added for ids it lacks (S2)" in text and "not_in_original_data" in text and "unknown" in text


def test_a_long_list_of_ids_is_cut_in_the_words_but_whole_in_the_data():
    many = [f"S{i:03d}" for i in range(40)]
    parts = [part("metadata_schema", "metadata"), part("A")]
    report = build_report(parts, [ids("metadata_schema", "metadata", many), ids("A", "data", [])])
    assert "and 28 more" in " ".join(report_lines(report))
    assert report.as_dict()["tables"][1]["ids_added"]["count"] == 40 and len(report.as_dict()["tables"][1]["ids_added"]["ids"]) == 40


def test_the_lines_with_no_id_are_listed_up_to_a_limit_and_the_count_is_whole():
    parts = [part("A")]
    report = build_report(parts, [ids("A", "data", ["S1"], no_id=tuple(range(2, 150)))])
    row = report.tables[0]
    assert row.no_id_lines == 148 and len(row.no_id_line_numbers) == 100
    assert report.as_dict()["tables"][0]["lines_with_no_usable_id_numbers_shown"] == 100
