"""`ingest_file`: the read of one candidate file, the same read as `DataIngestor.ingest`, followed by one full read (the Data Import check, D-0034, DEC24, DEC25, D-0050).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/ingestion/tests/test_ingest_file.py -q
"""
import polars as pl
import pytest

from ingestion.ingestor import DataIngestor, file_kind, ingest_file
from utils.errors import IngestionError

SCHEMA = {
    "null_values": [], "strip": False,
    "input_fields": {
        "sample_id": {"original_name": "Sample ID", "type": "String"},
        "score": {"type": "Int64"},
    },
}


def write(path, text):
    path.write_text(text)
    return path


def test_it_reads_a_file_exactly_as_the_ingestor_does(tmp_path):
    f = write(tmp_path / "S.tsv", "Sample ID\tscore\textra\ns1\t5\tx\ns2\t7\ty\n")
    expected, _ = DataIngestor(str(tmp_path)).ingest("S", {**SCHEMA, "source": {"type": "local_tsv", "path": str(f)}})
    got = ingest_file(f, "S", SCHEMA)
    assert got.collect().equals(expected.collect()) and got.collect_schema().names() == ["sample_id", "score"]


def test_it_ignores_the_source_block_of_the_schema(tmp_path):
    f = write(tmp_path / "S.tsv", "Sample ID\tscore\ns1\t5\n")
    got = ingest_file(f, "S", {**SCHEMA, "source": {"type": "local_tsv", "path": str(tmp_path / "nowhere.tsv")}})
    assert got.collect()["score"].to_list() == [5]


def test_a_slug_header_is_refused_with_the_expected_headers(tmp_path):
    f = write(tmp_path / "S.tsv", "sample_id\tscore\ns1\t5\n")
    with pytest.raises(IngestionError, match=r"expected file headers: \['Sample ID'\]"):
        ingest_file(f, "S", SCHEMA)


def test_a_value_that_does_not_fit_names_the_column_and_the_value(tmp_path):
    f = write(tmp_path / "S.tsv", "Sample ID\tscore\ns1\tfive\n")
    with pytest.raises(IngestionError) as err:
        ingest_file(f, "S", SCHEMA)
    assert "'score'" in str(err.value) and "'five'" in str(err.value)


def test_an_empty_file_names_the_file_given_not_the_temporary_path(tmp_path):
    f = write(tmp_path / "0.tsv", "")
    with pytest.raises(IngestionError) as err:
        ingest_file(f, "S", SCHEMA, file_name="my_upload.tsv")
    assert "my_upload.tsv" in str(err.value) and "0.tsv" not in str(err.value)


def test_the_kind_decides_the_read_not_the_name_of_a_temporary_file(tmp_path):
    f = tmp_path / "upload_without_suffix"
    pl.DataFrame({"Sample ID": ["a"], "score": ["3"]}).write_parquet(f)
    assert file_kind(f) == "tsv" and file_kind(tmp_path / "x.parquet") == "parquet"
    got = ingest_file(f, "S", SCHEMA, kind="parquet")
    assert got.collect()["score"].to_list() == [3]
    with pytest.raises(IngestionError):
        ingest_file(f, "S", SCHEMA)          # read as text: not a table


TEXT_SCHEMA = {"null_values": [], "strip": False, "input_fields": {"id": {"type": "String"}, "v": {"type": "String"}}}

DAMAGED = [
    ("extra field, String-only", TEXT_SCHEMA, b"id\tv\na\tb\nc\td\textra\n"),
    ("extra field, typed", SCHEMA, b"Sample ID\tscore\ns1\t5\ns2\t7\textra\n"),
    ("not UTF-8, String-only", TEXT_SCHEMA, b"id\tv\na\tb\xff\n"),
    ("not UTF-8, typed (a String column)", SCHEMA, b"Sample ID\tscore\ns\xff\t5\n"),
    ("unterminated quote, String-only", TEXT_SCHEMA, b'id\tv\na\t"b\nc\td\n'),
    ("unterminated quote, typed", SCHEMA, b'Sample ID\tscore\n"s1\t5\ns2\t7\n'),
]


@pytest.mark.parametrize("label,schema,content", DAMAGED, ids=[d[0] for d in DAMAGED])
def test_the_whole_file_is_read_so_damage_outside_the_header_and_the_typed_columns_is_refused(tmp_path, label, schema, content):
    f = tmp_path / "x.tsv"
    f.write_bytes(content)
    with pytest.raises(IngestionError) as err:
        ingest_file(f, "D", schema, file_name="my_upload.tsv")
    assert "my_upload.tsv" in str(err.value) and "cannot be read in full" in str(err.value)
    assert "ComputeError" not in str(err.value) and "Failed to read" not in str(err.value)
    assert "UTF-8" in err.value.tip and "tab-separated fields" in err.value.tip


def test_the_engines_own_ingest_is_unchanged_it_stays_lazy_and_fails_only_when_the_table_is_collected(tmp_path):
    f = tmp_path / "x.tsv"
    f.write_bytes(b"id\tv\na\tb\nc\td\textra\n")
    lf, _ = DataIngestor(str(tmp_path)).ingest("D", {**TEXT_SCHEMA, "source": {"type": "local_tsv", "path": str(f)}})
    with pytest.raises(Exception, match="more fields"):
        lf.collect()


def test_a_rule_of_the_recipe_keeps_its_own_text_and_a_readable_file_returns_a_lazy_table(tmp_path):
    f = write(tmp_path / "S.tsv", "Sample ID\tscore\ns1\tfive\n")
    with pytest.raises(IngestionError) as err:
        ingest_file(f, "S", SCHEMA)
    assert "cannot be read in full" not in str(err.value) and "values that do not fit the declared type" in str(err.value)
    g = write(tmp_path / "G.tsv", "Sample ID\tscore\ns1\t5\n")
    assert isinstance(ingest_file(g, "S", SCHEMA), pl.LazyFrame)


def test_an_empty_file_is_empty_in_plain_words(tmp_path):
    f = write(tmp_path / "0.tsv", "")
    with pytest.raises(IngestionError) as err:
        ingest_file(f, "S", SCHEMA, file_name="my_upload.tsv")
    assert str(err.value) == "The file 'my_upload.tsv' is empty: it has no header line and no rows." and "NoDataError" not in str(err.value)
