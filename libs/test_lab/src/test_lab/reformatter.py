"""
DataReformatter — headless file format conversion for TEST_LAB.

Converts XLSX (multi-sheet) → TSV, and CSV/any-delimiter → TSV.
Supports bulk folder processing.

Shiny-free. No ConfigManager. Polars + stdlib only.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

# @deps
# provides: DataReformatter class (convert_xlsx, convert_csv, convert_folder)
# consumes: polars, pathlib (stdlib/third-party)
# consumed_by: libs/test_lab/tests/test_reformatter.py
#              app/handlers/test_lab_handlers.py (TL-UI-REFORMAT-1 — not yet built)
# @end_deps

_XLSX_SUFFIXES = {".xlsx", ".xls", ".xlsm"}
_CSV_SUFFIXES = {".csv", ".tsv", ".txt"}


class DataReformatter:
    """Convert XLSX / CSV files to TSV.

    Usage::

        r = DataReformatter()
        sheets = r.convert_xlsx("results.xlsx", out_dir="/tmp/out")
        df = r.convert_csv("metadata.csv", out_dir="/tmp/out")
        summary = r.convert_folder("/data/raw", out_dir="/tmp/out")
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def convert_xlsx(
        self,
        filepath: str | Path,
        out_dir: str | Path | None = None,
        sheet_names: list[str] | None = None,
    ) -> dict[str, pl.DataFrame]:
        """Convert an XLSX file to one TSV per sheet.

        Parameters
        ----------
        filepath:
            Path to .xlsx / .xls / .xlsm file.
        out_dir:
            If set, write ``<sheet_name>.tsv`` files here.
        sheet_names:
            Subset of sheets to extract. None = all sheets.

        Returns
        -------
        dict mapping sheet name → DataFrame.
        """
        filepath = Path(filepath)
        if filepath.suffix.lower() not in _XLSX_SUFFIXES:
            raise ValueError(f"Not an Excel file: {filepath}")

        # polars.read_excel with sheet_id=0 returns {sheet_name: DataFrame}
        all_sheets: dict[str, pl.DataFrame] = pl.read_excel(filepath, sheet_id=0)

        if sheet_names is not None:
            missing = [s for s in sheet_names if s not in all_sheets]
            if missing:
                raise ValueError(f"Sheets not found in {filepath.name}: {missing}")
            selected = {s: all_sheets[s] for s in sheet_names}
        else:
            selected = dict(all_sheets)

        if out_dir is not None:
            out_dir = Path(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            for name, df in selected.items():
                safe_name = _safe_stem(name)
                df.write_csv(str(out_dir / f"{safe_name}.tsv"), separator="\t")

        return selected

    def convert_csv(
        self,
        filepath: str | Path,
        delimiter: str = ",",
        out_dir: str | Path | None = None,
    ) -> pl.DataFrame:
        """Convert a delimited text file to TSV.

        Any delimiter is accepted (comma, semicolon, pipe, tab, etc.).
        If the file is already TSV (tab-delimited), it is read and re-written
        normalised (consistent quoting, no BOM).

        Parameters
        ----------
        filepath:
            Path to source file.
        delimiter:
            Column separator in the source file (default: comma).
        out_dir:
            If set, write ``<stem>.tsv`` here.

        Returns
        -------
        Parsed DataFrame.
        """
        filepath = Path(filepath)
        df = pl.read_csv(str(filepath), separator=delimiter, infer_schema_length=0)

        if out_dir is not None:
            out_dir = Path(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            df.write_csv(str(out_dir / f"{filepath.stem}.tsv"), separator="\t")

        return df

    def convert_folder(
        self,
        folder: str | Path,
        out_dir: str | Path | None = None,
        extensions: tuple[str, ...] | None = None,
        csv_delimiter: str = ",",
    ) -> dict[str, dict | pl.DataFrame]:
        """Convert all supported files in a folder.

        Parameters
        ----------
        folder:
            Source folder (non-recursive).
        out_dir:
            If set, write converted files here (mirrors convert_xlsx / convert_csv).
        extensions:
            File extensions to process. Default: all XLSX + CSV/TSV variants.
        csv_delimiter:
            Delimiter for CSV files encountered in the folder.

        Returns
        -------
        dict mapping filename → result (for XLSX: ``{sheet_name: df}``; for CSV: df).
        Failures are stored as ``{"error": <message>}`` so bulk runs don't abort.
        """
        folder = Path(folder)
        if extensions is None:
            extensions = tuple(_XLSX_SUFFIXES | _CSV_SUFFIXES)

        results: dict[str, dict | pl.DataFrame] = {}
        for fp in sorted(folder.iterdir()):
            if not fp.is_file() or fp.suffix.lower() not in extensions:
                continue
            try:
                if fp.suffix.lower() in _XLSX_SUFFIXES:
                    results[fp.name] = self.convert_xlsx(fp, out_dir=out_dir)
                else:
                    # TSV files use tab; everything else uses csv_delimiter
                    sep = "\t" if fp.suffix.lower() == ".tsv" else csv_delimiter
                    results[fp.name] = self.convert_csv(fp, delimiter=sep, out_dir=out_dir)
            except Exception as exc:
                results[fp.name] = {"error": str(exc)}

        return results


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _safe_stem(name: str) -> str:
    """Replace whitespace and filesystem-unsafe chars in a sheet name."""
    import re
    return re.sub(r'[^\w\-]', '_', name.strip())
