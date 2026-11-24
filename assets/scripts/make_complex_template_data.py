#!/usr/bin/env python3
"""
make_complex_template_data.py
-----------------------------
Writes the two small synthetic tables that `config/data_analysis_recipes/templates/complex_template.yaml` reads:
`genomics_data.tsv` (Accession, Gene_List) and `metadata.tsv` (ID, Location).

No real data. The values are invented but plausible, and the files hold the cases the template's steps act on:
a gene list split on ";" with stray spaces and quotes (the strip step), a missing gene list (explode of a missing
value), a missing country, and two countries with the same number of isolates (a tie). Both tables hold exactly the
same sample ids (Eve, 2026-11-17, ledger D-0205: one set of ids for all the datasets of a recipe).

Same seed, same files: the seed is fixed by default.

Usage:
  ./.venv/bin/python assets/scripts/make_complex_template_data.py
  ./.venv/bin/python assets/scripts/make_complex_template_data.py --out-dir tmpAI/x --seed 7
"""
import argparse
import random
from pathlib import Path

GENES = ["blaTEM-1", "sul1", "sul2", "tet(A)", "dfrA17", "aph(3')-Ia", "strA", "strB", "catA1"]
COUNTRIES = ["Norway", "Sweden", "Denmark", "Finland"]
DEFAULT_SEED = 20261115


def build(n_samples: int, seed: int) -> tuple[list[list[str]], list[list[str]]]:
    """Return (genomics rows, metadata rows), each without header."""
    rng = random.Random(seed)
    accessions = [f"ACC{i:04d}" for i in range(1, n_samples + 1)]
    genomics, metadata = [], []
    for i, acc in enumerate(accessions):
        genes = rng.sample(GENES, rng.randint(1, 4))
        if i % 7 == 3:
            genes = [f" {g}" for g in genes]          # stray leading space, removed by the strip step
        if i % 11 == 5:
            genes = [f'"{g.strip()}"' for g in genes]  # quoted, the strip step removes the quotes
        sep = "; " if i % 5 == 2 else ";"
        genomics.append([acc, sep.join(genes)])
    genomics[8][1] = ""                                 # one sample without a gene list
    # countries: two of them get the same number of isolates (a tie), one value is missing
    pool = ["Norway"] * 9 + ["Sweden"] * 7 + ["Denmark"] * 7 + ["Finland"] * (n_samples - 24)
    rng.shuffle(pool)
    # the pool holds one country fewer than there are samples (kept so that the committed countries of the first
    # samples do not move: the change of 2026-11-17 touches only the last sample); the last sample gets one more draw
    pool.append(rng.choice(COUNTRIES))
    for acc, country in zip(accessions, pool):
        metadata.append([acc, country])
    metadata[13][1] = ""                                # one sample with no country recorded
    return genomics, metadata


def write(path: Path, header: list[str], rows: list[list[str]]) -> None:
    """Plain tab-separated text, written as is (a quote in a cell stays a quote)."""
    lines = ["\t".join(row) for row in [header, *rows]]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=Path("assets/test_data"),
                        help="folder for genomics_data.tsv and metadata.tsv (default: assets/test_data)")
    parser.add_argument("--n-samples", type=int, default=30, help="number of genomics samples, at least 25 (default: 30)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"random seed (default: {DEFAULT_SEED})")
    args = parser.parse_args()
    if args.n_samples < 25:
        parser.error("--n-samples must be at least 25 (the country counts of the tie need it)")
    genomics, metadata = build(args.n_samples, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write(args.out_dir / "genomics_data.tsv", ["Accession", "Gene_List"], genomics)
    write(args.out_dir / "metadata.tsv", ["ID", "Location"], metadata)
    print(f"wrote {args.out_dir / 'genomics_data.tsv'} ({len(genomics)} rows) and {args.out_dir / 'metadata.tsv'} ({len(metadata)} rows)")


if __name__ == "__main__":
    main()
