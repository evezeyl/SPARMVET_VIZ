"""The one rule that finds the file of a dataset in a data folder (IMPORT-PATH-1, SOURCE-LOOKUP-ONE-1).

`<dataset id>.tsv` or `<dataset id>.parquet`, the exact name; no fuzzy search; both for one id is an error.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/ingestion/tests/test_find_dataset_file.py -q
"""
import polars as pl
import pytest

from ingestion.ingestor import DataIngestor, find_dataset_file
from utils.errors import IngestionError


def _schema():
    return {"null_values": [], "strip": False, "input_fields": {"a": {"type": "String"}}}


def test_a_tsv_is_found_by_its_exact_name(tmp_path):
    (tmp_path / "T.tsv").write_text("a\n1\n")
    assert find_dataset_file(tmp_path, "T") == tmp_path / "T.tsv"


def test_a_parquet_is_found_by_its_exact_name(tmp_path):
    pl.DataFrame({"a": ["1"]}).write_parquet(tmp_path / "T.parquet")
    assert find_dataset_file(tmp_path, "T") == tmp_path / "T.parquet"


def test_nothing_is_found_when_no_file_has_the_name(tmp_path):
    assert find_dataset_file(tmp_path, "T") is None


def test_a_longer_name_is_not_a_match(tmp_path):
    """The loose search `*<id>*.tsv` is gone: a file that only contains the id is not the dataset."""
    (tmp_path / "T_old.tsv").write_text("a\n1\n")
    (tmp_path / "xT.tsv").write_text("a\n1\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "T.tsv").write_text("a\n1\n")
    assert find_dataset_file(tmp_path, "T") is None


def test_both_extensions_for_one_id_is_an_error_that_names_both(tmp_path):
    (tmp_path / "T.tsv").write_text("a\n1\n")
    pl.DataFrame({"a": ["2"]}).write_parquet(tmp_path / "T.parquet")
    with pytest.raises(IngestionError) as e:
        find_dataset_file(tmp_path, "T")
    assert "T.tsv" in str(e.value) and "T.parquet" in str(e.value)


def test_the_ingestor_reads_a_parquet_found_by_id(tmp_path):
    pl.DataFrame({"a": ["x", "y"]}).write_parquet(tmp_path / "T.parquet")
    lf, path = DataIngestor(str(tmp_path)).ingest("T", _schema())
    assert path == tmp_path / "T.parquet"
    assert lf.collect()["a"].to_list() == ["x", "y"]


def test_the_ingestor_reads_a_tsv_found_by_id(tmp_path):
    (tmp_path / "T.tsv").write_text("a\nx\ny\n")
    lf, path = DataIngestor(str(tmp_path)).ingest("T", _schema())
    assert path == tmp_path / "T.tsv"
    assert lf.collect()["a"].to_list() == ["x", "y"]


def test_the_ingestor_find_file_is_the_same_rule(tmp_path):
    (tmp_path / "T.tsv").write_text("a\n1\n")
    pl.DataFrame({"a": ["2"]}).write_parquet(tmp_path / "T.parquet")
    with pytest.raises(IngestionError):
        DataIngestor(str(tmp_path)).find_file("T")
