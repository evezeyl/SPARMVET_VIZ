# @deps
# provides: script:engine_map_table
# consumes: libs/utils/src/utils/engine_boundary.py (PLACES, KINDS)
# consumed_by: libs/utils/tests/test_engine_map_table.py, .claude/design/engine_boundary_map.md
# doc: .claude/knowledge/decision_ledger.md (D-0455, D-0458)
# @end_deps
"""Print the table of engine places per engine and kind, generated from the list `utils.engine_boundary.PLACES`.

The one-page engine map (`.claude/design/engine_boundary_map.md`) holds this table between two marker lines; a test
(`libs/utils/tests/test_engine_map_table.py`) fails when the page and this output differ, so the counts cannot drift.

Examples:
  ./.venv/bin/python assets/scripts/engine_map_table.py
  ./.venv/bin/python assets/scripts/engine_map_table.py --list     # also print one line per place
"""
import argparse
from collections import Counter
from typing import List

from utils.engine_boundary import KINDS, PLACES


def _engines(place) -> str:
    """The engines of a place as one label, in a fixed order, so that the order written in the list does not split a column."""
    return "+".join(sorted(place.engines))


def table_lines() -> List[str]:
    """The markdown table of counts: one row per kind, one column per engine set, and the totals."""
    engine_sets = sorted({_engines(p) for p in PLACES}, key=lambda s: (s.count("+"), s))
    counts = Counter((_engines(p), p.kind) for p in PLACES)
    lines = ["| Kind | " + " | ".join(engine_sets) + " | All |", "|---|" + "---|" * (len(engine_sets) + 1)]
    for kind in KINDS:
        row = [counts[(e, kind)] for e in engine_sets]
        lines.append(f"| {kind} | " + " | ".join(str(n) for n in row) + f" | {sum(row)} |")
    totals = [sum(counts[(e, k)] for k in KINDS) for e in engine_sets]
    lines.append("| All | " + " | ".join(str(n) for n in totals) + f" | {sum(totals)} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="also print one line per place: path, engines, kind")
    args = parser.parse_args()
    print("\n".join(table_lines()))
    if args.list:
        print()
        for p in PLACES:
            print(f"{p.path}\t{'+'.join(p.engines)}\t{p.kind}")


if __name__ == "__main__":
    main()
