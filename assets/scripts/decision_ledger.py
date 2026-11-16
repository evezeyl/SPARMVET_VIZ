"""Read the decision ledger of Eve's numbered decisions and check that cited numbers exist.

The ledger is `.claude/knowledge/decision_ledger.md`. Every decision is one line that starts with
its number and has ten fields separated by " | " (the layout is explained at the top of that file):

  D-0001 | date | area | decision | source | taken by | status | relation | her words and evidence | old key

Only a line taken by EVE is DECIDED. A line taken by an AGENT is PROVISIONAL. A line whose
record does not say who decided is NOT-STATED. A brief that starts a builder or a reviewer quotes the numbers
it depends on (`.claude/workflows/decision_compliance.md`); the hook `.claude/hooks/coordinator_guard.py`
reads them with `read_ledger` of this file, so there is one reading function.

Why: one source of truth for what Eve decided, readable by a script, so that a brief cannot cite
a decision that does not exist.

Examples:
  ./.venv/bin/python assets/scripts/decision_ledger.py list
  ./.venv/bin/python assets/scripts/decision_ledger.py list --status PROVISIONAL
  ./.venv/bin/python assets/scripts/decision_ledger.py check D-0001 D-0108
  ./.venv/bin/python assets/scripts/decision_ledger.py --ledger /path/to/other_ledger.md check D-0001
"""
import argparse
import re
import sys
from pathlib import Path

DEFAULT_LEDGER = Path(__file__).resolve().parents[2] / ".claude" / "knowledge" / "decision_ledger.md"
NUMBER = re.compile(r"D-\d{4}")
LINE = re.compile(r"^D-\d{4} \| ")
FIELDS = ("number", "date", "area", "decision", "source", "taken_by", "status", "relation", "evidence", "old_key")
TAKEN_BY = {"EVE", "AGENT", "NOT STATED"}
STATUS = {"DECIDED", "PROVISIONAL", "NOT-STATED"}


def read_ledger(path: Path) -> dict:
    """Return {number: {field: text}} for every decision line of the ledger.

    Raises FileNotFoundError when the file is missing and ValueError (naming the line)
    for a line that does not have the ten fields, a repeated number, an unknown "taken by" or status, or a
    status that does not follow the rule (EVE is DECIDED, AGENT is PROVISIONAL, NOT STATED is NOT-STATED).
    """
    entries = {}
    for lineno, line in enumerate(Path(path).read_text(encoding="utf-8").split("\n"), start=1):
        if not LINE.match(line):
            continue
        parts = line.split(" | ")
        if len(parts) != len(FIELDS):
            raise ValueError(f"{path}:{lineno}: {len(parts)} fields, expected {len(FIELDS)}: {line[:80]}")
        entry = dict(zip(FIELDS, (p.strip() for p in parts)))
        if entry["number"] in entries:
            raise ValueError(f"{path}:{lineno}: number {entry['number']} appears twice")
        if entry["taken_by"] not in TAKEN_BY:
            raise ValueError(f"{path}:{lineno}: taken by '{entry['taken_by']}' is not one of {sorted(TAKEN_BY)}")
        if entry["status"] not in STATUS:
            raise ValueError(f"{path}:{lineno}: status '{entry['status']}' is not one of {sorted(STATUS)}")
        expected = {"EVE": "DECIDED", "AGENT": "PROVISIONAL", "NOT STATED": "NOT-STATED"}[entry["taken_by"]]
        if entry["status"] != expected:
            raise ValueError(f"{path}:{lineno}: taken by {entry['taken_by']} must have status {expected}, found {entry['status']}")
        entries[entry["number"]] = entry
    return entries


def _missing(numbers, entries: dict) -> list:
    return [n for n in numbers if not NUMBER.fullmatch(n) or n not in entries]


def missing_numbers(numbers, path: Path) -> list:
    """Return the cited numbers that are not in the ledger (a malformed number counts as missing), in the order given."""
    return _missing(numbers, read_ledger(path))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER, help="ledger file (default: .claude/knowledge/decision_ledger.md)")
    sub = ap.add_subparsers(dest="mode", required=True)
    lst = sub.add_parser("list", help="print one line per decision: number, status, taken by, date, area, start of the decision")
    lst.add_argument("--status", choices=sorted(STATUS), help="only decisions with this status")
    chk = sub.add_parser("check", help="exit 0 when every number exists in the ledger, else exit 1 and name the missing ones")
    chk.add_argument("numbers", nargs="+", help="numbers such as D-0001")
    args = ap.parse_args(argv)
    try:
        entries = read_ledger(args.ledger)
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot read the ledger: {exc}", file=sys.stderr)
        return 2
    if args.mode == "list":
        for number, e in entries.items():
            if args.status and e["status"] != args.status:
                continue
            print(f"{number} {e['status']} {e['taken_by']} {e['date']} {e['area']}: {e['decision'][:100]}")
        return 0
    missing = _missing(args.numbers, entries)
    if missing:
        print("MISSING from the ledger " + str(args.ledger) + ": " + ", ".join(missing), file=sys.stderr)
        return 1
    print("OK: " + ", ".join(args.numbers))
    return 0


if __name__ == "__main__":
    sys.exit(main())
