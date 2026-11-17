#!/usr/bin/env python3
# @deps
# provides: script:make_left_join_lesson_data
# consumes: nothing (the values are invented; plain random.Random(seed))
# consumed_by: app/tests/test_left_join_lesson.py
# doc: .claude/rules/rules_asset_scripts.md
# @end_deps
"""
make_left_join_lesson_data.py
-----------------------------
Writes the two small synthetic tables that `config/data_analysis_recipes/templates/left_join_lesson.yaml` reads:
`left_join_lesson_sequenced.tsv` (Accession, Gene) and `left_join_lesson_metadata.tsv` (ID, Country).

No real data. The two tables name the sample id with DIFFERENT column names (Accession and ID) on purpose: the
recipe declares which column is the sample id (`is_entity_key`), it is not guessed from a name.

The ids do NOT match on purpose, in both directions, to teach what a left join does:
- 10 sequenced samples (the left table): ACC0001 to ACC0010;
- 10 metadata rows (the right table): ACC0003 to ACC0012;
- ACC0001 and ACC0002 are only in the left table: the left join keeps them with an empty country;
- ACC0011 and ACC0012 are only in the right table: the left join leaves them out.
The genes and the countries are drawn with the seed; the ids are fixed (the lesson counts them).

Same seed, same files (byte for byte). The seed is written below and printed. Files that exist are not replaced
unless `--overwrite`.

Usage:
  ./.venv/bin/python assets/scripts/make_left_join_lesson_data.py --help
  ./.venv/bin/python assets/scripts/make_left_join_lesson_data.py --out-dir tmpAI/lesson --seed 7
"""
import argparse
import random
import sys
from pathlib import Path

GENES = ["blaTEM-1", "sul1", "sul2", "tet(A)", "dfrA17", "strA"]
COUNTRIES = ["Norway", "Sweden", "Denmark", "Finland"]
DEFAULT_SEED = 20261117
LEFT_IDS = [f"ACC{i:04d}" for i in range(1, 11)]
RIGHT_IDS = [f"ACC{i:04d}" for i in range(3, 13)]
LEFT_FILE = "left_join_lesson_sequenced.tsv"
RIGHT_FILE = "left_join_lesson_metadata.tsv"


def build(seed: int) -> tuple[list[list[str]], list[list[str]]]:
    """Return (left rows, right rows), each without header."""
    rng = random.Random(seed)
    left = [[acc, rng.choice(GENES)] for acc in LEFT_IDS]
    right = [[acc, rng.choice(COUNTRIES)] for acc in RIGHT_IDS]
    return left, right


def write(path: Path, header: list[str], rows: list[list[str]]) -> None:
    """Plain tab-separated text, written as is."""
    lines = ["\t".join(row) for row in [header, *rows]]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=Path("assets/test_data/left_join_lesson"),
                        help="folder for the two files (default: assets/test_data/left_join_lesson)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"random seed (default: {DEFAULT_SEED})")
    parser.add_argument("--overwrite", action="store_true", help="replace files that already exist (default: stop)")
    args = parser.parse_args()
    targets = [args.out_dir / LEFT_FILE, args.out_dir / RIGHT_FILE]
    existing = [str(t) for t in targets if t.exists()]
    if existing and not args.overwrite:
        print(f"Not written: {existing} exist. Use --overwrite to replace them.", file=sys.stderr)
        return 2
    left, right = build(args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write(targets[0], ["Accession", "Gene"], left)
    write(targets[1], ["ID", "Country"], right)
    print(f"seed {args.seed}: wrote {targets[0]} ({len(left)} rows) and {targets[1]} ({len(right)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
