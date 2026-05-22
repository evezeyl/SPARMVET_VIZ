"""Gate tests for TL-REFORMAT-1 — DataReformatter XLSX / CSV conversion."""
import polars as pl
import pytest
from pathlib import Path

from test_lab.reformatter import DataReformatter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_tsv(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _write_csv(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# CSV → TSV
# ---------------------------------------------------------------------------

class TestConvertCsv:
    """CSV (any delimiter) → TSV conversion."""

    def test_comma_csv_parses(self, tmp_path):
        src = _write_csv(tmp_path / "data.csv", "id,value\nA,1\nB,2\n")
        df = DataReformatter().convert_csv(src, delimiter=",")
        assert df.columns == ["id", "value"]
        assert df.height == 2

    def test_semicolon_csv_parses(self, tmp_path):
        src = _write_csv(tmp_path / "data.csv", "id;value\nA;1\nB;2\n")
        df = DataReformatter().convert_csv(src, delimiter=";")
        assert "id" in df.columns
        assert df.height == 2

    def test_pipe_delimited_parses(self, tmp_path):
        src = _write_csv(tmp_path / "data.csv", "id|value\nA|1\nB|2\n")
        df = DataReformatter().convert_csv(src, delimiter="|")
        assert df.height == 2

    def test_tab_tsv_passes_through(self, tmp_path):
        src = _write_tsv(tmp_path / "data.tsv", "id\tvalue\nA\t1\nB\t2\n")
        df = DataReformatter().convert_csv(src, delimiter="\t")
        assert df.height == 2
        assert "id" in df.columns

    def test_writes_tsv_file(self, tmp_path):
        src = _write_csv(tmp_path / "data.csv", "id,value\nA,1\nB,2\n")
        DataReformatter().convert_csv(src, delimiter=",", out_dir=tmp_path / "out")
        out = tmp_path / "out" / "data.tsv"
        assert out.exists()
        content = out.read_text()
        assert "\t" in content

    def test_output_tsv_readable_by_polars(self, tmp_path):
        src = _write_csv(tmp_path / "data.csv", "id,value\nA,1\nB,2\n")
        DataReformatter().convert_csv(src, delimiter=",", out_dir=tmp_path / "out")
        df = pl.read_csv(str(tmp_path / "out" / "data.tsv"), separator="\t")
        assert df.height == 2
        assert "id" in df.columns

    def test_row_count_preserved(self, tmp_path):
        src = _write_csv(tmp_path / "data.csv", "id,value\n" + "\n".join(f"S{i},{i}" for i in range(50)) + "\n")
        df = DataReformatter().convert_csv(src)
        assert df.height == 50

    def test_no_out_dir_no_file_written(self, tmp_path):
        src = _write_csv(tmp_path / "data.csv", "id,value\nA,1\n")
        DataReformatter().convert_csv(src)
        assert not (tmp_path / "data.tsv").exists()


# ---------------------------------------------------------------------------
# XLSX → TSV  (polars uses openpyxl/xlrd; skip if not available)
# ---------------------------------------------------------------------------

def _skip_if_no_excel():
    # _make_xlsx uses openpyxl to write test fixtures — require it for xlsx tests
    try:
        import openpyxl  # noqa: F401
        return False
    except ImportError:
        return True


def _make_xlsx(path: Path, sheets: dict[str, list[dict]]) -> Path:
    """Write a minimal xlsx using openpyxl."""
    import openpyxl
    wb = openpyxl.Workbook()
    first = True
    for sheet_name, rows in sheets.items():
        if first:
            ws = wb.active
            ws.title = sheet_name
            first = False
        else:
            ws = wb.create_sheet(title=sheet_name)
        if rows:
            headers = list(rows[0].keys())
            ws.append(headers)
            for row in rows:
                ws.append([row[h] for h in headers])
    wb.save(str(path))
    return path


@pytest.mark.skipif(_skip_if_no_excel(), reason="openpyxl not installed")
class TestConvertXlsx:
    """XLSX → TSV conversion (requires openpyxl)."""

    def test_multi_sheet_returns_all_sheets(self, tmp_path):
        fp = _make_xlsx(
            tmp_path / "data.xlsx",
            {
                "metadata": [{"sample_id": "S1", "species": "E. coli"}],
                "results": [{"sample_id": "S1", "gene": "blaTEM"}],
            },
        )
        result = DataReformatter().convert_xlsx(fp)
        assert set(result.keys()) == {"metadata", "results"}

    def test_sheet_dataframe_has_expected_columns(self, tmp_path):
        fp = _make_xlsx(
            tmp_path / "data.xlsx",
            {"metadata": [{"sample_id": "S1", "species": "E. coli"}]},
        )
        result = DataReformatter().convert_xlsx(fp)
        assert "sample_id" in result["metadata"].columns

    def test_writes_one_tsv_per_sheet(self, tmp_path):
        fp = _make_xlsx(
            tmp_path / "data.xlsx",
            {
                "meta data": [{"id": "A"}],
                "results": [{"id": "A", "gene": "x"}],
            },
        )
        DataReformatter().convert_xlsx(fp, out_dir=tmp_path / "out")
        out_files = {f.name for f in (tmp_path / "out").iterdir()}
        assert "meta_data.tsv" in out_files
        assert "results.tsv" in out_files

    def test_sheet_subset_selection(self, tmp_path):
        fp = _make_xlsx(
            tmp_path / "data.xlsx",
            {
                "metadata": [{"id": "A"}],
                "results": [{"id": "A"}],
                "extra": [{"id": "A"}],
            },
        )
        result = DataReformatter().convert_xlsx(fp, sheet_names=["metadata", "results"])
        assert set(result.keys()) == {"metadata", "results"}
        assert "extra" not in result

    def test_missing_sheet_raises(self, tmp_path):
        fp = _make_xlsx(tmp_path / "data.xlsx", {"metadata": [{"id": "A"}]})
        with pytest.raises(ValueError, match="Sheets not found"):
            DataReformatter().convert_xlsx(fp, sheet_names=["nonexistent"])

    def test_non_excel_raises(self, tmp_path):
        csv = _write_csv(tmp_path / "data.csv", "id\nA\n")
        with pytest.raises(ValueError, match="Not an Excel file"):
            DataReformatter().convert_xlsx(csv)


# ---------------------------------------------------------------------------
# Bulk folder conversion
# ---------------------------------------------------------------------------

class TestConvertFolder:
    """Bulk conversion of a folder."""

    def test_csv_files_converted(self, tmp_path):
        folder = tmp_path / "src"
        folder.mkdir()
        _write_csv(folder / "a.csv", "id,val\nA,1\n")
        _write_csv(folder / "b.csv", "id,val\nB,2\n")
        results = DataReformatter().convert_folder(folder)
        assert "a.csv" in results
        assert "b.csv" in results

    def test_tsv_files_included(self, tmp_path):
        folder = tmp_path / "src"
        folder.mkdir()
        _write_tsv(folder / "a.tsv", "id\tval\nA\t1\n")
        results = DataReformatter().convert_folder(folder)
        assert "a.tsv" in results

    def test_writes_to_out_dir(self, tmp_path):
        folder = tmp_path / "src"
        folder.mkdir()
        _write_csv(folder / "a.csv", "id,val\nA,1\n")
        out = tmp_path / "out"
        DataReformatter().convert_folder(folder, out_dir=out)
        assert (out / "a.tsv").exists()

    def test_unrecognised_extension_skipped(self, tmp_path):
        folder = tmp_path / "src"
        folder.mkdir()
        (folder / "readme.md").write_text("# doc")
        results = DataReformatter().convert_folder(folder)
        assert "readme.md" not in results

    def test_error_stored_not_raised(self, tmp_path):
        # A text file with .xlsx extension will fail polars Excel reader.
        # convert_folder must catch the error and continue rather than raise.
        folder = tmp_path / "src"
        folder.mkdir()
        fake_xlsx = folder / "bad.xlsx"
        fake_xlsx.write_text("this is not an excel file")
        results = DataReformatter().convert_folder(folder, extensions=(".xlsx",))
        assert "bad.xlsx" in results
        assert "error" in results["bad.xlsx"]

    def test_empty_folder_returns_empty_dict(self, tmp_path):
        folder = tmp_path / "empty"
        folder.mkdir()
        assert DataReformatter().convert_folder(folder) == {}
