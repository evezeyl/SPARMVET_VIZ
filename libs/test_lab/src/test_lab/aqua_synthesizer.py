# @deps
# provides: AquaSynthesizer class (synthesize), standalone helpers: clean_header, generate_fake_column, introduce_missing_values
# consumes: polars, numpy, random, re, pathlib, datetime, argparse (stdlib)
# consumed_by: assets/scripts/generate_demo_data.py, libs/test_lab/tests/debug_sdk.py
# @end_deps
#!/usr/bin/env python3
# libs/test_lab/src/test_lab/aqua_synthesizer.py
import argparse
import polars as pl
import numpy as np
import random
import re
from pathlib import Path
from datetime import datetime


def clean_header(col_name: str) -> str:
    """Sanitizes a messy TSV column header into a safe, snake_case name."""
    s = str(col_name).lower()
    # Replace slashes, dots, colons, spaces, hyphens with underscores
    s = re.sub(r'[/.:\s\-]+', '_', s)
    # Remove all other special characters
    s = re.sub(r'[^\w_]', '', s)
    # Deduplicate underscores and strip
    s = re.sub(r'_+', '_', s)
    return s.strip('_')


def generate_fake_column(series: pl.Series, n_rows: int) -> pl.Series:
    """Generates synthetic data matching the type and distribution of a polar series."""
    dtype = series.dtype
    if dtype in [pl.Int32, pl.Int64]:
        min_val, max_val = series.min(), series.max()
        return pl.Series(series.name, np.random.randint(min_val or 0, (max_val or 100) + 1, size=n_rows))
    elif dtype in [pl.Float32, pl.Float64]:
        min_val, max_val = series.min(), series.max()
        return pl.Series(series.name, np.random.uniform(min_val or 0.0, max_val or 1.0, size=n_rows))
    elif dtype in [pl.Date, pl.Datetime]:
        min_val, max_val = series.min(), series.max()
        if min_val is None or max_val is None:
            return pl.Series(series.name, [None] * n_rows)
        min_ts = int(min_val.strftime("%s")) if hasattr(
            min_val, 'strftime') else min_val
        max_ts = int(max_val.strftime("%s")) if hasattr(
            max_val, 'strftime') else max_val
        random_timestamps = np.random.randint(min_ts, max_ts + 1, size=n_rows)
        if dtype == pl.Date:
            return pl.Series(series.name, [datetime.fromtimestamp(ts).date() for ts in random_timestamps])
        else:
            return pl.Series(series.name, [datetime.fromtimestamp(ts) for ts in random_timestamps])
    elif dtype in [pl.Boolean]:
        return pl.Series(series.name, np.random.choice([True, False], size=n_rows))
    else:
        # Categorical / String
        unique_vals = series.drop_nulls().unique().to_list()
        if not unique_vals:
            unique_vals = ["unknown"]
        return pl.Series(series.name, np.random.choice(unique_vals, size=n_rows))


def introduce_missing_values(df: pl.DataFrame, missing_fraction=0.1) -> pl.DataFrame:
    """Randomly injects null values and messy strings into the dataframe."""
    exprs = []
    # Common real-world messy strings
    messy_strings = [None, "-", "unknown", "N/A", "not found", "None", ""]

    for col in df.columns:
        series = df[col]
        dtype = series.dtype
        mask = pl.Series(np.random.rand(df.height) < missing_fraction)

        if dtype in [pl.Categorical, pl.String, pl.Utf8]:
            random_messy = pl.Series(
                np.random.choice(messy_strings, size=df.height))
            expr = pl.when(mask).then(random_messy).otherwise(
                pl.col(col)).alias(col)
        else:
            expr = pl.when(mask).then(None).otherwise(pl.col(col)).alias(col)
        exprs.append(expr)

    return df.with_columns(exprs)


def main():
    parser = argparse.ArgumentParser(
        description="AquaSynthesizer: Agnostic Synthetic Data Production Engine.")

    # Agnostic Test Lab Mode
    parser.add_argument("--generate_only", nargs='+',
                        help="Quick generate mode: provide headers as list")
    parser.add_argument("--n_rows", type=int, default=50,
                        help="Number of rows for quick generate")

    # Standard Anonymization Mode
    parser.add_argument(
        "--data_dir", help="Path to directory containing real data.")
    parser.add_argument("--data_files", nargs='+',
                        help="Specific data file(s).")
    parser.add_argument("--metadata_file", help="Path to real metadata file.")
    parser.add_argument("--primary_key_data", nargs='+',
                        help="Primary key column(s) in data files.")
    parser.add_argument("--primary_key_metadata",
                        help="Primary key in metadata.")
    parser.add_argument("--output_primary_key",
                        help="Standardized output PK name.")
    parser.add_argument("--mismatches", action="store_true",
                        help="Inject PK mismatches.")
    parser.add_argument("--duplicates", action="store_true",
                        help="Inject PK duplicates.")
    parser.add_argument("--missing_values",
                        action="store_true", help="Inject nulls.")
    parser.add_argument("--out_dir", default=".", help="Output directory.")

    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- Mode 1: Quick Generate ---
    if args.generate_only:
        headers = args.generate_only
        n = args.n_rows
        target_file = out_dir / f"synthetic_gen_{timestamp}.tsv"

        with open(target_file, "w") as f:
            f.write("\t".join(headers) + "\n")
            for i in range(n):
                row_vals = []
                for h in headers:
                    if "id" in h.lower() or "pk" in h.lower():
                        row_vals.append(f"REC_{i}")
                    else:
                        row_vals.append(f"value_{i}")
                f.write("\t".join(row_vals) + "\n")
        print(f"✅ Generated {n} records to {target_file}")
        return

    # --- Mode 2: Real Data Anonymization ---
    if not (args.data_files or args.data_dir):
        # Allow running without args to show help if no mode selected
        if not any(vars(args).values()):
            parser.print_help()
        return

    all_data_files = []
    if args.data_dir:
        dpath = Path(args.data_dir)
        if args.data_files:
            for f_name in args.data_files:
                all_data_files.append(str(dpath / f_name))
        else:
            found_files = list(dpath.glob("*.tsv")) + list(dpath.glob("*.csv"))
            all_data_files.extend([str(p) for p in found_files])
    elif args.data_files:
        all_data_files.extend(args.data_files)

    global_keys = set()
    data_dfs = []
    for d_file in all_data_files:
        if not Path(d_file).exists():
            continue
        df = pl.read_csv(
            d_file, separator='\t' if d_file.endswith('.tsv') else ',')
        actual_key = next(
            (k for k in (args.primary_key_data or []) if k in df.columns), None)
        data_dfs.append((Path(d_file), df, actual_key))
        if actual_key:
            global_keys.update(df[actual_key].drop_nulls().to_list())

    if not global_keys and data_dfs:
        n_rows_sum = sum(df.height for _, df, _ in data_dfs)
        global_keys.update([str(x) for x in range(n_rows_sum)])

    n_unique = len(global_keys)
    fake_ids_ints = random.sample(range(10000000, 99999999), n_unique)
    id_map = dict(zip(global_keys, [str(x) for x in fake_ids_ints]))

    for filepath, df_real, actual_key in data_dfs:
        n_rows = df_real.height
        file_ids = [id_map.get(x, str(random.randint(10000000, 99999999))) for x in (
            df_real[actual_key].to_list() if actual_key else range(n_rows))]

        target_key_name = args.output_primary_key or actual_key or "id"
        fake_data_cols = []
        for col in df_real.columns:
            if col == actual_key:
                fake_data_cols.append(pl.Series(target_key_name, file_ids))
            else:
                fake_data_cols.append(generate_fake_column(
                    df_real[col], n_rows).alias(clean_header(col)))

        df_fake = pl.DataFrame(fake_data_cols)
        if args.missing_values:
            df_fake = introduce_missing_values(df_fake, 0.05)

        out_path = out_dir / f"test_data_{filepath.stem}_{timestamp}.tsv"
        df_fake.write_csv(out_path, separator='\t')
        print(f"Created: {out_path}")


if __name__ == "__main__":
    main()
