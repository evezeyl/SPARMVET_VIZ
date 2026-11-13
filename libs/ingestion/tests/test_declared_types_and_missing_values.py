"""Declared Polars types and explicit missing values at ingestion (W5, tests first, 2026-11-13).

Decisions of Eve (`recipe_format_spec.md` DEC27, DEC28):
  - `type` is required on every field and is a Polars dtype that a text file can hold; the declared dtype goes
    to the CSV reader, which fails strictly and names the value (`2022.0` into `Int64` fails);
  - `categorical` was a tweak (String at ingestion) and is refused, like every old name (`numeric`, `utf8`, ...);
  - missing values have NO default: the schema states `null_values` (a list of texts, `[]` allowed) and `strip`
    (true or false), a field may override both; today's hidden sanitiser (strip, then 14 tokens such as `NA`
    and `-` become null in every text column) goes. `NA` is Namibia, `-` can be a value.
  - NaN is not null: an unlisted `NaN` in a Float64 field is read as a NaN.

State: built (`ingestion.declared`, `DataIngestor.ingest_declared`, W5). Until the migration (run A) switches the
engine to it, `ingest` keeps serving the old recipes; the switch renames `ingest_declared` to `ingest`. The key
names follow spec 7.3 and 7.4.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/ingestion/tests/test_declared_types_and_missing_values.py -q
"""
import datetime
import math

import polars as pl
import pytest

from ingestion.ingestor import DataIngestor
from utils.errors import IngestionError

def ingest(tmp_path, text, fields, **schema_keys):
    """Write `text` as a TSV, ingest it with the given fields and schema-level keys, return the DataFrame."""
    f = tmp_path / "S.tsv"
    f.write_text(text)
    schema = {"source": {"type": "local_tsv", "path": str(f)}, "input_fields": fields, **schema_keys}
    lf, _ = DataIngestor(str(tmp_path)).ingest("S", schema)
    return lf.collect()


# the two keys a schema must state; a test that is not about them says "no words, no strip"
EXPLICIT = {"null_values": [], "strip": False}


# -- declared Polars types go to the reader --------------------------------------------------

def test_an_integer_field_with_a_decimal_value_fails_and_names_the_value(tmp_path):
    with pytest.raises(IngestionError, match=r"2022\.0"):
        ingest(tmp_path, "id\tyear\ns1\t2022.0\n", {"id": {"type": "String"}, "year": {"type": "Int64"}}, **EXPLICIT)


def test_a_boolean_field_is_boolean_even_when_every_cell_is_empty(tmp_path):
    """The declared type, not what the reader infers from the cells, decides the type."""
    df = ingest(tmp_path, "id\tok\ns1\t\ns2\t\n", {"id": {"type": "String"}, "ok": {"type": "Boolean"}}, **EXPLICIT)
    assert df["ok"].dtype == pl.Boolean and df["ok"].null_count() == 2


def test_a_datetime_and_a_time_field_are_read_as_such(tmp_path):
    df = ingest(tmp_path, "id\tat\tt\ns1\t2022-03-01 10:00:00\t10:00:00\n",
                {"id": {"type": "String"}, "at": {"type": "Datetime"}, "t": {"type": "Time"}}, **EXPLICIT)
    assert df["at"].dtype.base_type() == pl.Datetime and df["at"][0] == datetime.datetime(2022, 3, 1, 10, 0)
    assert df["t"].dtype == pl.Time and df["t"][0] == datetime.time(10, 0)


def test_a_categorical_field_is_a_polars_categorical(tmp_path):
    df = ingest(tmp_path, "id\tg\ns1\tx\n", {"id": {"type": "String"}, "g": {"type": "Categorical"}}, **EXPLICIT)
    assert df["g"].dtype == pl.Categorical


def test_an_enum_field_keeps_its_levels_in_the_declared_order(tmp_path):
    df = ingest(tmp_path, "id\tlevel\ns1\thi\ns2\tlo\n",
                {"id": {"type": "String"}, "level": {"type": "Enum", "categories": ["lo", "hi"]}}, **EXPLICIT)
    assert df["level"].dtype == pl.Enum(["lo", "hi"])
    assert df.sort("level")["level"].to_list() == ["lo", "hi"]


@pytest.mark.parametrize("old_name", ["numeric", "categorical", "utf8", "integer", "string"])
def test_an_old_type_name_is_refused_and_named(tmp_path, old_name):
    with pytest.raises(IngestionError, match=old_name):
        ingest(tmp_path, "id\tx\ns1\t1\n", {"id": {"type": "String"}, "x": {"type": old_name}}, **EXPLICIT)


def test_a_field_without_a_type_fails_and_names_the_field(tmp_path):
    with pytest.raises(IngestionError, match="no_type_here"):
        ingest(tmp_path, "id\tno_type_here\ns1\t1\n", {"id": {"type": "String"}, "no_type_here": {}}, **EXPLICIT)


# -- missing values have no default ------------------------------------------------------------

def test_na_is_a_value_when_the_recipe_does_not_list_it(tmp_path):
    """NA is the ISO code of Namibia: with `null_values: []` it must stay text."""
    df = ingest(tmp_path, "id\tcountry\ns1\tNA\ns2\tNO\n", {"id": {"type": "String"}, "country": {"type": "String"}}, **EXPLICIT)
    assert df["country"].to_list() == ["NA", "NO"]


def test_only_the_listed_words_become_null(tmp_path):
    df = ingest(tmp_path, "id\tv\ns1\tNA\ns2\t-\ns3\tok\n", {"id": {"type": "String"}, "v": {"type": "String"}},
                null_values=["NA"], strip=False)
    assert df["v"].to_list() == [None, "-", "ok"]


def test_a_field_overrides_the_null_words_of_the_schema(tmp_path):
    df = ingest(tmp_path, "id\ta\tb\ns1\tNA\tNA\n",
                {"id": {"type": "String"}, "a": {"type": "String"}, "b": {"type": "String", "null_values": []}},
                null_values=["NA"], strip=False)
    assert df["a"].to_list() == [None] and df["b"].to_list() == ["NA"]


def test_strip_false_keeps_the_whitespace(tmp_path):
    df = ingest(tmp_path, "id\tv\ns1\t x \n", {"id": {"type": "String"}, "v": {"type": "String"}}, null_values=[], strip=False)
    assert df["v"].to_list() == [" x "]


def test_strip_then_the_null_words_is_the_order(tmp_path):
    """Passes today (the hidden sanitiser strips first) and must keep passing: strip, then the words, then the type."""
    df = ingest(tmp_path, "id\tv\ns1\t NA \ns2\t y \n", {"id": {"type": "String"}, "v": {"type": "String"}},
                null_values=["NA"], strip=True)
    assert df["v"].to_list() == [None, "y"]


def test_a_nan_only_column_is_a_nan_today(tmp_path):
    """Passes today by the reader's inference (an all-numeric column keeps its NaN) and must keep passing."""
    df = ingest(tmp_path, "id\tv\ns1\tNaN\ns2\t1.5\n", {"id": {"type": "String"}, "v": {"type": "Float64"}}, **EXPLICIT)
    assert df["v"].null_count() == 0 and math.isnan(df["v"][0])


def test_an_unlisted_nan_stays_a_nan_whatever_else_the_column_holds(tmp_path):
    """Found 2026-11-13: today a text NaN is a NaN in an all-numeric column and a null in a column that also holds NA."""
    df = ingest(tmp_path, "id\tv\ns1\tNaN\ns2\tNA\ns3\t1.5\n", {"id": {"type": "String"}, "v": {"type": "Float64"}},
                null_values=["NA"], strip=False)
    assert math.isnan(df["v"][0]) and df["v"][1] is None and df["v"][2] == 1.5


def test_a_listed_nan_is_a_null(tmp_path):
    df = ingest(tmp_path, "id\tv\ns1\tNaN\ns2\t1.5\n", {"id": {"type": "String"}, "v": {"type": "Float64"}},
                null_values=["NaN"], strip=False)
    assert df["v"].null_count() == 1 and df["v"][1] == 1.5


def test_an_unlisted_word_in_a_numeric_field_fails_and_names_it(tmp_path):
    with pytest.raises(IngestionError, match="NA"):
        ingest(tmp_path, "id\tv\ns1\tNA\n", {"id": {"type": "String"}, "v": {"type": "Float64"}}, **EXPLICIT)


@pytest.mark.parametrize("missing", ["null_values", "strip"])
def test_a_schema_without_the_two_keys_fails_and_names_the_missing_key(tmp_path, missing):
    keys = {k: v for k, v in EXPLICIT.items() if k != missing}
    with pytest.raises(IngestionError, match=missing):
        ingest(tmp_path, "id\nx\n", {"id": {"type": "String"}}, **keys)


def test_an_empty_cell_is_a_null_in_a_numeric_field(tmp_path):
    """Polars reads an empty cell as null; this is Polars' own rule, not one of our words. Passes today and must keep passing."""
    df = ingest(tmp_path, "id\tn\ns1\t\ns2\t5\n", {"id": {"type": "String"}, "n": {"type": "Int64"}}, **EXPLICIT)
    assert df["n"].to_list() == [None, 5]


# -- more cases of the built ingestion --------------------------------------------------------------

def test_an_enum_value_outside_the_levels_fails_and_names_it(tmp_path):
    with pytest.raises(IngestionError, match="medium"):
        ingest(tmp_path, "id\tlevel\ns1\tmedium\n", {"id": {"type": "String"}, "level": {"type": "Enum", "categories": ["lo", "hi"]}}, **EXPLICIT)


def test_a_declared_date_format_is_used(tmp_path):
    df = ingest(tmp_path, "id\td\ns1\t15/03/2022\n", {"id": {"type": "String"}, "d": {"type": "Date", "format": "%d/%m/%Y"}}, **EXPLICIT)
    assert df["d"].to_list() == [datetime.date(2022, 3, 15)]


def test_a_decimal_field_needs_its_precision_and_keeps_its_scale(tmp_path):
    df = ingest(tmp_path, "id\tp\ns1\t1.50\n", {"id": {"type": "String"}, "p": {"type": "Decimal", "precision": 10, "scale": 2}}, **EXPLICIT)
    assert df["p"].dtype == pl.Decimal(10, 2)
    with pytest.raises(IngestionError, match="categories|precision"):
        ingest(tmp_path, "id\tlevel\ns1\tlo\n", {"id": {"type": "String"}, "level": {"type": "Enum"}}, **EXPLICIT)


def test_a_field_can_override_strip_only(tmp_path):
    df = ingest(tmp_path, "id\ta\tb\ns1\t x \t y \n",
                {"id": {"type": "String"}, "a": {"type": "String"}, "b": {"type": "String", "strip": False}}, null_values=[], strip=True)
    assert df["a"].to_list() == ["x"] and df["b"].to_list() == [" y "]


def test_the_error_names_every_column_that_does_not_fit(tmp_path):
    with pytest.raises(IngestionError) as info:
        ingest(tmp_path, "id\ta\tb\ns1\tx\tq\n", {"id": {"type": "String"}, "a": {"type": "Int64"}, "b": {"type": "Float64"}}, **EXPLICIT)
    assert "column 'a' (Int64): 'x'" in str(info.value) and "column 'b' (Float64): 'q'" in str(info.value)


def test_only_the_declared_columns_are_read_in_the_declared_path(tmp_path):
    df = ingest(tmp_path, "id\tkeep\tleft_out\ns1\ta\tb\n", {"id": {"type": "String"}, "keep": {"type": "String"}}, **EXPLICIT)
    assert df.columns == ["id", "keep"]


def test_columns_with_a_different_number_of_bad_values_are_all_reported(tmp_path):
    """Found by the Data Import panel test: one column with two bad values, one with none, one with one."""
    with pytest.raises(IngestionError) as info:
        ingest(tmp_path, "id\ta\tb\tc\ns1\tx\t1\t2022-01-01\ns2\ty\t2\tnot a date\ns3\t3\t4\t2022-01-03\n",
               {"id": {"type": "String"}, "a": {"type": "Int64"}, "b": {"type": "Int64"}, "c": {"type": "Date"}}, **EXPLICIT)
    message = str(info.value)
    assert "column 'a' (Int64): 'x', 'y'" in message and "column 'c' (Date): 'not a date'" in message and "column 'b'" not in message
