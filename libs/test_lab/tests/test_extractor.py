"""XlsxExtractor: sheets of a workbook become one normalised TSV each (Stage A of the TEST_LAB flow).

Replaces the extraction step of the removed debug_sdk.py demo (its synthesizer and bootstrapper
steps are covered by test_synthesizer.py and test_bootstrapper.py).

Run: ./.venv/bin/python -m pytest libs/test_lab/tests/test_extractor.py -q
"""
import polars as pl
import pytest
import yaml

openpyxl = pytest.importorskip("openpyxl")

from test_lab.extractor import XlsxExtractor


@pytest.fixture
def workbook(tmp_path):
    wb = openpyxl.Workbook()
    meta = wb.active
    meta.title = "Metadata"
    meta.append(["Sample_ID", "Species", "Country"])
    meta.append(["SAM001", "E. coli", "Norway"])
    meta.append(["SAM002", "S. enterica", "Denmark"])
    hits = wb.create_sheet("ResFinder Hits")
    hits.append(["ID", "Gene", "Identity"])
    hits.append(["SAM001", "tet(A)", 99.5])
    hits.append(["SAM001", "dfrA1", 100.0])
    path = tmp_path / "raw.xlsx"
    wb.save(path)
    return path


def config(tmp_path, sheets) -> str:
    path = tmp_path / "extract.yaml"
    path.write_text(yaml.dump({"extract_sheets": sheets}))
    return str(path)


def test_each_configured_sheet_becomes_a_tsv_with_the_standard_key_name(workbook, tmp_path):
    cfg = config(tmp_path, {
        "Metadata": {"target_name": "test_metadata", "primary_key": "Sample_ID"},
        "ResFinder Hits": {"target_name": "test_resfinder", "primary_key": "ID"},
    })
    out = XlsxExtractor().extract(str(workbook), cfg, str(tmp_path / "out"), standardized_id="sample_id")
    assert set(out) == {"test_metadata", "test_resfinder"}
    meta = pl.read_csv(out["test_metadata"], separator="\t")
    assert meta.columns[0] == "sample_id" and meta.height == 2
    assert pl.read_csv(out["test_resfinder"], separator="\t").height == 2


def test_output_goes_into_a_subfolder_named_after_the_project_or_the_workbook(workbook, tmp_path):
    cfg = config(tmp_path, {"Metadata": {"primary_key": "Sample_ID"}})
    by_recipe_name = XlsxExtractor(recipe_basename="Proj").extract(str(workbook), cfg, str(tmp_path / "a"))
    by_workbook = XlsxExtractor().extract(str(workbook), cfg, str(tmp_path / "b"))
    assert by_recipe_name["metadata"].parent.name == "Proj"
    assert by_workbook["metadata"].parent.name == "raw"


def test_target_name_defaults_to_the_lowercase_sheet_name_with_underscores(workbook, tmp_path):
    cfg = config(tmp_path, {"ResFinder Hits": {"primary_key": "ID"}})
    assert set(XlsxExtractor().extract(str(workbook), cfg, str(tmp_path / "o"))) == {"resfinder_hits"}


def test_a_sheet_that_does_not_exist_is_skipped_not_an_error(workbook, tmp_path):
    cfg = config(tmp_path, {"No Such Sheet": {"primary_key": "ID"}, "Metadata": {"primary_key": "Sample_ID"}})
    assert set(XlsxExtractor().extract(str(workbook), cfg, str(tmp_path / "o"))) == {"metadata"}


def test_a_sheet_without_a_primary_key_or_with_a_wrong_one_is_skipped(workbook, tmp_path):
    cfg = config(tmp_path, {"Metadata": {}, "ResFinder Hits": {"primary_key": "Nope"}})
    assert XlsxExtractor().extract(str(workbook), cfg, str(tmp_path / "o")) == {}


def test_a_config_without_extract_sheets_is_refused(workbook, tmp_path):
    empty = tmp_path / "empty.yaml"
    empty.write_text("something_else: 1\n")
    with pytest.raises(ValueError, match="extract_sheets"):
        XlsxExtractor().extract(str(workbook), str(empty), str(tmp_path / "o"))
