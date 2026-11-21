"""`ingest_file`: the read of one candidate file, the same read as `DataIngestor.ingest` (the Data Import check, D-0034, DEC24, DEC25).

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
