#!/usr/bin/env python
"""Create the Data Import test files from the shipped test data.

Writes a small set of valid and deliberately broken upload files to a folder, so the Data
Import panel (test plan HOM-34, HOM-35, HOM-36) can be tested by hand with the same files
every time. The files are derived from the FastP and Bracken test datasets of the data analysis recipe
`1_test_data_ST22_dummy`; nothing in the source data is modified.

Usage:
    ./.venv/bin/python assets/scripts/create_import_test_files.py
    ./.venv/bin/python assets/scripts/create_import_test_files.py --output-dir tmp/import_tests

Defaults: --source-dir assets/test_data/1_test_data_ST22_dummy, --output-dir assets/test_uploads
(a folder outside the data folder, so the engine's data discovery never picks these files up).
See assets/test_uploads/README.md for what each file should do in the app.
"""
import argparse
from pathlib import Path

import polars as pl

FASTP = "test_data_FastP_20260307_105756.tsv"
BRACKEN = "test_data_Bracken_20260307_105756.tsv"

# Columns changed in the "valid" files. The IDs (sample_id) are numbers too, so the columns are
# named on purpose; changing sample_id would break every join. Both columns are declared in the
# data analysis recipe AND used by a plot (qc_reads_horizontal_barplot: x = total_reads, fill = proportion_1),
# otherwise an import would change nothing visible.
FASTP_VALUE_COLUMN = "total_reads"
BRACKEN_VALUE_COLUMN = "proportion_1"   # declared in the data analysis recipe and used as the fill of the QC plot
FASTP_HEADER_TO_BREAK = "total_reads"


def build(source_dir: Path, output_dir: Path) -> list[Path]:
    """Write the test files and return their paths."""
    fastp = pl.read_csv(source_dir / FASTP, separator="\t")
    bracken = pl.read_csv(source_dir / BRACKEN, separator="\t")
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    def tsv(df: pl.DataFrame, name: str) -> None:
        path = output_dir / name
        df.write_csv(path, separator="\t")
        written.append(path)

    # --- valid: should import, and the change should be visible in the plots -------------
    tsv(fastp.with_columns(pl.lit(1_000_000).alias(FASTP_VALUE_COLUMN)), "FastP_valid_changed.tsv")
    tsv(bracken.with_columns(pl.lit(25.0).alias(BRACKEN_VALUE_COLUMN)), "Bracken_valid_changed.tsv")
    tsv(fastp.with_columns(pl.lit("extra").alias("an_extra_column")), "FastP_ok_extra_column.tsv")

    # --- must be rejected before anything is written --------------------------------------
    tsv(fastp.drop(FASTP_HEADER_TO_BREAK), "FastP_error_missing_column.tsv")
    broken = FASTP_HEADER_TO_BREAK[:-1] + "x"
    tsv(fastp.rename({FASTP_HEADER_TO_BREAK: broken}), "FastP_error_misspelled_header.tsv")
    path = output_dir / "FastP_error_wrong_delimiter.tsv"
    path.write_text(fastp.write_csv(separator=","))
    written.append(path)
    path = output_dir / "FastP_error_no_header.tsv"
    path.write_text(fastp.write_csv(separator="\t", include_header=False))
    written.append(path)

    # --- rejected by the import: text in a numeric column (type check, issue #11) --------------
    tsv(fastp.with_columns(pl.lit("abc").alias(FASTP_VALUE_COLUMN)), "FastP_gap_text_in_numeric_column.tsv")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source-dir", type=Path, default=Path("assets/test_data/1_test_data_ST22_dummy"),
                        help="folder with the shipped FastP and Bracken test data (default: %(default)s)")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/test_uploads"),
                        help="folder to write the upload test files to (default: %(default)s)")
    args = parser.parse_args()
    for path in build(args.source_dir, args.output_dir):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
