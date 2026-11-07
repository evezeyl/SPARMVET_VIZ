"""The Data Import test files (assets/test_uploads/) behave as their README says.

Uses the same checks the Data Import panel runs (MetadataValidator: column names, then types,
against the data analysis recipe's input_fields), and checks that the files are exactly what the generating script
produces, so the set cannot drift away from the data.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_import_test_files.py -q
"""
import importlib.util
from pathlib import Path

import polars as pl
import pytest

from ingestion.ingestor import DataIngestor
from transformer.metadata_validator import MetadataValidator
from utils.config_loader import ConfigManager

ROOT = Path(__file__).resolve().parents[2]
UPLOADS = ROOT / "assets" / "test_uploads"
DATA_ANALYSIS_RECIPE = ROOT / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"

ACCEPTED = [
    ("FastP", "FastP_valid_changed.tsv"),
    ("Bracken", "Bracken_valid_changed.tsv"),
    ("FastP", "FastP_ok_extra_column.tsv"),
]
REJECTED = [
    "FastP_gap_text_in_numeric_column.tsv",   # text in a numeric column: the type check (issue #11)
    "FastP_error_missing_column.tsv",
    "FastP_error_misspelled_header.tsv",
    "FastP_error_wrong_delimiter.tsv",
    "FastP_error_no_header.tsv",
]


@pytest.fixture(scope="module")
def schemas():
    return ConfigManager(str(DATA_ANALYSIS_RECIPE)).raw_config["data_schemas"]


def _column_check_accepts(path: Path, schema: dict) -> bool:
    try:
        lf = pl.scan_csv(path, separator="\t")
        validator = MetadataValidator()
        validator.validate(lf, schema["input_fields"], context="[test]")
        validator.validate_types(lf, schema["input_fields"], context="[test]")
        return True
    except Exception:
        return False


@pytest.mark.parametrize("dataset,name", ACCEPTED)
def test_these_files_pass_the_import_check(schemas, dataset, name):
    assert _column_check_accepts(UPLOADS / name, schemas[dataset])


@pytest.mark.parametrize("name", REJECTED)
def test_these_files_fail_the_import_check(schemas, name):
    assert not _column_check_accepts(UPLOADS / name, schemas["FastP"])


def test_the_valid_files_keep_the_sample_ids_and_change_only_the_named_column():
    original = pl.read_csv(ROOT / "assets/test_data/1_test_data_ST22_dummy/test_data_FastP_20260307_105756.tsv", separator="\t")
    changed = pl.read_csv(UPLOADS / "FastP_valid_changed.tsv", separator="\t")
    assert changed["sample_id"].to_list() == original["sample_id"].to_list()
    differing = [c for c in original.columns if original[c].to_list() != changed[c].to_list()]
    assert differing == ["total_reads"]


def test_the_bracken_file_changes_only_the_named_declared_column(schemas):
    original = pl.read_csv(ROOT / "assets/test_data/1_test_data_ST22_dummy/test_data_Bracken_20260307_105756.tsv", separator="\t")
    changed = pl.read_csv(UPLOADS / "Bracken_valid_changed.tsv", separator="\t")
    assert changed["sample_id"].to_list() == original["sample_id"].to_list()
    differing = [c for c in original.columns if original[c].to_list() != changed[c].to_list()]
    assert differing == ["proportion_1"]
    assert "proportion_1" in schemas["Bracken"]["input_fields"], "the changed column must be one the data analysis recipe declares"


def test_the_files_are_exactly_what_the_script_generates(tmp_path):
    spec = importlib.util.spec_from_file_location("make_files", ROOT / "assets/scripts/create_import_test_files.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    written = module.build(ROOT / "assets/test_data/1_test_data_ST22_dummy", tmp_path)
    assert sorted(p.name for p in written) == sorted(p.name for p in UPLOADS.glob("*.tsv"))
    for path in written:
        assert path.read_bytes() == (UPLOADS / path.name).read_bytes(), f"{path.name} differs from the committed file"


def test_digits_only_ids_still_import_as_text(schemas, tmp_path):
    """sample_id is declared categorical: IDs that are only digits are valid (issue #11)."""
    path = tmp_path / "ids.tsv"
    original = pl.read_csv(UPLOADS / "FastP_valid_changed.tsv", separator="\t", infer_schema_length=0)
    original.with_columns(pl.Series("sample_id", [str(10_000_000 + i) for i in range(original.height)])).write_csv(path, separator="\t")
    assert _column_check_accepts(path, schemas["FastP"])


def test_the_text_in_numeric_file_names_the_column_and_the_value(schemas):
    with pytest.raises(Exception) as err:
        lf = pl.scan_csv(UPLOADS / "FastP_gap_text_in_numeric_column.tsv", separator="\t")
        MetadataValidator().validate_types(lf, schemas["FastP"]["input_fields"], context="[FastP]")
    assert "'total_reads'" in str(err.value) and "'abc'" in str(err.value)
