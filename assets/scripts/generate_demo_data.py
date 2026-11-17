#!/usr/bin/env python3
# @deps
# provides: script:generate_demo_data
# consumes: assets/test_data/1_test_data_ST22_dummy/ (ground truth TSVs: the values are drawn from them)
# consumed_by: app/tests/test_demo_data_generator.py
# doc: .claude/rules/rules_asset_scripts.md
# @end_deps
"""
generate_demo_data.py
---------------------
Writes a synthetic demo data set of three tables (metadata, MLST, ResFinder) in which ALL ids come
from ONE common set of sample ids (Eve, 2026-11-17, ledger D-0205: "The same set of ids is used across
all the datasets of the recipes, so there is a logical correspondence: the datasets reflect analyses
on the same samples").

How the data is made (plain `random.Random(seed)` and the plain text; `AquaSynthesizer` of
`libs/test_lab` is not used because it generates ONE table at a time from a column config and keeps no
shared set of ids, so it cannot promise a common set or one row per sample and scheme):

1. One set of `--n-samples` ids `SYN_<8 digits>`, drawn without repeat.
2. metadata: one row per sample of the set; Source, Year and Country are taken from random rows of the
   ground-truth metadata. `--metadata-lines-without-id` lines WITHOUT a sample id are added on purpose
   (an empty id, a dash, two quote marks): the demo recipe has a visible step that removes them
   (ledger D-0167). They are not part of the set.
3. MLST: a random pick of `--mlst-share` of the set; ONE row per sample and scheme (a sample has one
   sequence type per scheme); the row is a random row of the ground-truth MLST file.
4. ResFinder: a random pick of `--resfinder-share` of the set; 1 to `--max-genes-per-sample` rows per
   sample (several genes per sample is normal); the rows are distinct random rows of the ground truth.
5. `--messy-fraction` of the values of the other columns (never the id, never the scheme) become a
   messy value (empty, dash, unknown, N/A), as in real exports.

The same command (same arguments, same seed) writes the same files, byte for byte. The seed is printed.
The output folder defaults to `tmp/`; files that already exist are not replaced unless `--overwrite`.

Usage:
  ./.venv/bin/python assets/scripts/generate_demo_data.py --help
  ./.venv/bin/python assets/scripts/generate_demo_data.py --seed 20261117 --out-dir tmp/demo_data
"""
import argparse
import random
import sys
from pathlib import Path

ID_COLUMN = "sample_id"
SCHEME_COLUMN = "Scheme"
MESSY_VALUES = ["", "-", "unknown", "N/A"]
NO_ID_MARKERS = ["", "-", '""']  # the three ways a line can have no sample id (as in the shipped demo metadata)
SUFFIX = "_20260307_105756.tsv"
GROUND_TRUTH_NAMES = {
    "metadata": "test_metadata" + SUFFIX,
    "mlst": "test_data_MLST_results" + SUFFIX,
    "resfinder": "test_data_ResFinder" + SUFFIX,
}
OUTPUT_NAMES = {
    "metadata": "test_data_test_metadata" + SUFFIX,
    "mlst": "test_data_test_data_MLST_results" + SUFFIX,
    "resfinder": "test_data_test_data_ResFinder" + SUFFIX,
}


def read_tsv(path):
    """Header and rows of a TSV as plain strings, every value kept exactly as written (no quote handling)."""
    with open(path, encoding="utf-8", newline="") as handle:
        lines = handle.read().split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    rows = [line.split("\t") for line in lines]
    widths = {len(r) for r in rows}
    if len(widths) != 1:
        raise ValueError(f"{path}: rows do not all have the same number of columns ({sorted(widths)})")
    return rows[0], rows[1:]


def write_tsv(path, header, rows):
    """Write with Unix line ends, the same way on every machine."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        for row in [header] + rows:
            handle.write("\t".join(row) + "\n")


def make_messy(rows, header, fraction, rng, protected):
    """Replace a fraction of the values of the unprotected columns by a messy value."""
    free = [i for i, name in enumerate(header) if name not in protected]
    for row in rows:
        for i in free:
            if rng.random() < fraction:
                row[i] = rng.choice(MESSY_VALUES)
    return rows


def generate(ground_truth_dir, n_samples, seed, mlst_share, resfinder_share, max_genes,
             lines_without_id, messy_fraction):
    """Return {"ids": [...], "metadata": (header, rows), "mlst": (...), "resfinder": (...)}."""
    rng = random.Random(seed)
    meta_header, meta_source = read_tsv(Path(ground_truth_dir) / GROUND_TRUTH_NAMES["metadata"])
    mlst_header, mlst_source = read_tsv(Path(ground_truth_dir) / GROUND_TRUTH_NAMES["mlst"])
    res_header, res_source = read_tsv(Path(ground_truth_dir) / GROUND_TRUTH_NAMES["resfinder"])

    ids = ["SYN_%08d" % n for n in rng.sample(range(10_000_000, 100_000_000), n_samples)]

    metadata = []
    for sample in ids:
        source_row = rng.choice(meta_source)
        metadata.append([sample] + source_row[1:])
    make_messy(metadata, meta_header, messy_fraction, rng, {ID_COLUMN})
    for k in range(lines_without_id):
        source_row = rng.choice(meta_source)
        line = [NO_ID_MARKERS[k % len(NO_ID_MARKERS)]] + source_row[1:]
        metadata.insert(rng.randrange(len(metadata) + 1), line)

    mlst = []
    for sample in rng.sample(ids, round(mlst_share * n_samples)):
        mlst.append([sample] + rng.choice(mlst_source)[1:])
    make_messy(mlst, mlst_header, messy_fraction, rng, {ID_COLUMN, SCHEME_COLUMN})

    resfinder = []
    for sample in rng.sample(ids, round(resfinder_share * n_samples)):
        genes = rng.randint(1, max_genes)
        for source_row in rng.sample(res_source, min(genes, len(res_source))):
            resfinder.append([sample] + source_row[1:])
    make_messy(resfinder, res_header, messy_fraction, rng, {ID_COLUMN})

    return {"ids": ids, "metadata": (meta_header, metadata), "mlst": (mlst_header, mlst),
            "resfinder": (res_header, resfinder)}


def check_one_set(tables, ids):
    """The problems of the generated tables against the common set (empty list = consistent)."""
    problems = []
    common = set(ids)
    for name, (header, rows) in tables.items():
        column = header.index(ID_COLUMN)
        foreign = sorted({r[column] for r in rows} - common - (set(NO_ID_MARKERS) if name == "metadata" else set()))
        if foreign:
            problems.append(f"{name}: ids outside the common set: {foreign}")
    header, rows = tables["mlst"]
    key = (header.index(ID_COLUMN), header.index(SCHEME_COLUMN))
    seen = {}
    for r in rows:
        seen[(r[key[0]], r[key[1]])] = seen.get((r[key[0]], r[key[1]]), 0) + 1
    repeated = sorted(k for k, n in seen.items() if n > 1)
    if repeated:
        problems.append(f"mlst: sample and scheme repeated: {repeated}")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ground-truth-dir", type=Path, default=Path("assets/test_data/1_test_data_ST22_dummy"),
                        help="Folder of the ground-truth TSVs the values are drawn from "
                             "(default: assets/test_data/1_test_data_ST22_dummy)")
    parser.add_argument("--out-dir", type=Path, default=Path("tmp/demo_data_generated"),
                        help="Output folder (default: tmp/demo_data_generated). To replace the shipped demo "
                             "files give assets/test_data/demo_high_integrity together with --overwrite")
    parser.add_argument("--seed", type=int, default=20261117,
                        help="Seed of the random draws; the same seed and arguments give the same files "
                             "(default: 20261117)")
    parser.add_argument("--n-samples", type=int, default=27,
                        help="Size of the common set of sample ids (default: 27)")
    parser.add_argument("--mlst-share", type=float, default=0.55,
                        help="Share of the samples that get an MLST row, one per sample (default: 0.55)")
    parser.add_argument("--resfinder-share", type=float, default=0.8,
                        help="Share of the samples that get ResFinder rows (default: 0.8)")
    parser.add_argument("--max-genes-per-sample", type=int, default=4,
                        help="A ResFinder sample gets 1 to this many rows, one per gene (default: 4)")
    parser.add_argument("--metadata-lines-without-id", type=int, default=3,
                        help="Metadata lines with no sample id added on purpose, to show the recipe step "
                             "that removes them (default: 3; 0 for none)")
    parser.add_argument("--messy-fraction", type=float, default=0.05,
                        help="Fraction of the values of the other columns made messy, 0.0 to 1.0 (default: 0.05)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace files that already exist in the output folder")
    args = parser.parse_args(argv)

    if not 0 <= args.messy_fraction <= 1:
        parser.error("--messy-fraction must be between 0 and 1")
    for name in ("mlst_share", "resfinder_share"):
        if not 0 < getattr(args, name) <= 1:
            parser.error(f"--{name.replace('_', '-')} must be above 0 and at most 1")
    if args.n_samples < 1 or args.max_genes_per_sample < 1 or args.metadata_lines_without_id < 0:
        parser.error("--n-samples and --max-genes-per-sample must be at least 1, --metadata-lines-without-id at least 0")

    targets = {k: args.out_dir / v for k, v in OUTPUT_NAMES.items()}
    existing = [str(p) for p in targets.values() if p.exists()]
    if existing and not args.overwrite:
        parser.error("these files exist, add --overwrite to replace them: " + ", ".join(existing))

    print(f"[1] seed {args.seed}, {args.n_samples} samples, ground truth {args.ground_truth_dir}")
    data = generate(args.ground_truth_dir, args.n_samples, args.seed, args.mlst_share, args.resfinder_share,
                    args.max_genes_per_sample, args.metadata_lines_without_id, args.messy_fraction)
    tables = {k: data[k] for k in OUTPUT_NAMES}
    problems = check_one_set(tables, data["ids"])
    if problems:
        print("The generated data is not consistent:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, (header, rows) in tables.items():
        write_tsv(targets[name], header, rows)
        print(f"[2] wrote {targets[name]}: {len(rows)} rows")
    print(f"[3] CHECK: all ids of the three tables are in the common set of {len(data['ids'])} ids; "
          f"MLST has one row per sample and scheme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
