"""Strict import: only the input fields a recipe declares enter the app (Eve, 2026-11-13).

Why: with the recipe written like Polars code, the columns of a table are exactly the declared ones plus the
ones the steps create, so the table, the audit and the export are reproducible from the recipe alone. Measured
before the change on the shipped pipelines: 37 of 40 VirulenceFinder file columns, 19 of 23 Quast columns,
13 of 16 Bracken columns, ... passed through undeclared (`tmpAI/architect/strict_import_probe.py`).

Rules (agreed with the recipe session, `recipe_format_spec.md` O22):
  - a declared column that the file lacks FAILS (it was a warning);
  - `original_name` matches the file header EXACTLY (it matched ignoring case);
  - file columns that are not declared are not imported, and the import says how many and which (information);
  - the declared types still apply (numeric, categorical, date).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/ingestion/tests/test_strict_import.py -q
"""
import pytest

from ingestion.ingestor import DataIngestor
from utils.errors import IngestionError


def schema(path, **fields):
    return {"source": {"type": "local_tsv", "path": str(path)}, "input_fields": fields}


@pytest.fixture
def tsv(tmp_path):
    f = tmp_path / "S.tsv"
    f.write_text("Sample ID\tgroup\tscore\textra\ns1\tA\t5\tx\ns2\tB\t15\ty\n")
    return f


def ingest(tmp_path, tsv, **fields):
    lf, _ = DataIngestor(str(tmp_path)).ingest("S", schema(tsv, **fields))
    return lf.collect()


def test_the_header_is_renamed_to_the_slug_and_the_type_applies(tmp_path, tsv):
    df = ingest(tmp_path, tsv, sample_id={"original_name": "Sample ID"}, score={"type": "numeric"})
    assert df.columns == ["sample_id", "score"]
    assert str(df["score"].dtype) == "Float64"


def test_a_file_column_that_is_not_declared_is_not_imported(tmp_path, tsv):
    df = ingest(tmp_path, tsv, sample_id={"original_name": "Sample ID"}, group={})
    assert df.columns == ["sample_id", "group"]
    assert "extra" not in df.columns and "score" not in df.columns


def test_the_import_says_which_file_columns_were_left_out(tmp_path, tsv, capsys):
    ingest(tmp_path, tsv, sample_id={"original_name": "Sample ID"}, group={})
    out = capsys.readouterr().out
    assert "2 file columns" in out and "score" in out and "extra" in out


def test_a_declared_column_missing_from_the_file_fails_and_names_it(tmp_path, tsv):
    with pytest.raises(IngestionError, match="no_such_column"):
        ingest(tmp_path, tsv, sample_id={"original_name": "Sample ID"}, no_such_column={})


def test_original_name_matches_exactly_not_ignoring_case(tmp_path, tsv):
    with pytest.raises(IngestionError, match="sample id"):
        ingest(tmp_path, tsv, sample_id={"original_name": "sample id"})


def test_an_undeclared_column_with_the_slug_of_a_renamed_one_does_not_break_the_rename(tmp_path):
    f = tmp_path / "T.tsv"
    f.write_text("Sample ID\tsample_id\ns1\tzzz\n")
    lf, _ = DataIngestor(str(tmp_path)).ingest("T", schema(f, sample_id={"original_name": "Sample ID"}))
    assert lf.collect()["sample_id"].to_list() == ["s1"]
