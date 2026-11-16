"""`assets/scripts/decision_ledger.py` reads the tracked decision ledger and checks that cited numbers exist.

The hook `.claude/hooks/coordinator_guard.py` uses the same reading function, so these tests also guard
what the hook accepts. The last tests read the real ledger that ships in `.claude/knowledge/`.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("decision_ledger", ROOT / "assets/scripts/decision_ledger.py")
dl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dl)

REAL_LEDGER = ROOT / ".claude/knowledge/decision_ledger.md"


def line(number="D-0001", taken_by="EVE", status="DECIDED", **over):
    f = dict(number=number, date="2026-11-05", area="area", decision="a decision", source="src", taken_by=taken_by,
             status=status, relation="-", evidence="her words", old_key="L01")
    f.update(over)
    return " | ".join(f[k] for k in dl.FIELDS)


def write(tmp_path, *lines, header="# ledger\n\nsome text that is not a decision\n"):
    p = tmp_path / "ledger.md"
    p.write_text(header + "\n".join(lines) + "\n\nD-0099 is mentioned in text, not a line of the ledger.\n", encoding="utf-8")
    return p


def test_read_ledger_reads_every_decision_line_and_ignores_text(tmp_path):
    p = write(tmp_path, line("D-0001"), line("D-0002", "AGENT", "PROVISIONAL"), line("D-0003", "NOT STATED", "NOT-STATED"),
              line("D-0004", "REVIEW SESSION", "RELAYED"))
    entries = dl.read_ledger(p)
    assert list(entries) == ["D-0001", "D-0002", "D-0003", "D-0004"]
    assert entries["D-0002"]["status"] == "PROVISIONAL"
    assert entries["D-0004"]["status"] == "RELAYED"
    assert entries["D-0001"]["evidence"] == "her words"


def test_missing_numbers_names_the_missing_ones_in_order_and_a_malformed_number(tmp_path):
    p = write(tmp_path, line("D-0001"), line("D-0002"))
    assert dl.missing_numbers(["D-0002", "D-0007", "D-0001", "D-12", "D-0099", "d-0001"], p) == ["D-0007", "D-12", "D-0099", "d-0001"]
    assert dl.missing_numbers([], p) == []


def test_a_number_cited_in_text_is_not_in_the_ledger(tmp_path):
    p = write(tmp_path, line("D-0001"))
    assert dl.missing_numbers(["D-0099"], p) == ["D-0099"]


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        dl.read_ledger(tmp_path / "nope.md")


@pytest.mark.parametrize("bad, why", [
    (line("D-0001").replace(" | ", " | x | ", 1), "fields"),
    ("D-0001 | too | few", "fields"),
    (line("D-0001", "EVE", "PROVISIONAL"), "must have status DECIDED"),
    (line("D-0001", "AGENT", "DECIDED"), "must have status PROVISIONAL"),
    (line("D-0001", "NOT STATED", "DECIDED"), "must have status NOT-STATED"),
    (line("D-0001", "REVIEW SESSION", "DECIDED"), "must have status RELAYED"),
    (line("D-0001", "EVE", "RELAYED"), "must have status DECIDED"),
    (line("D-0001", "SOMEONE", "DECIDED"), "taken by"),
    (line("D-0001", "EVE", "MAYBE"), "status"),
])
def test_a_malformed_line_is_refused_and_named(tmp_path, bad, why):
    p = write(tmp_path, bad)
    with pytest.raises(ValueError, match=why):
        dl.read_ledger(p)


def test_a_repeated_number_is_refused(tmp_path):
    p = write(tmp_path, line("D-0001"), line("D-0001"))
    with pytest.raises(ValueError, match="appears twice"):
        dl.read_ledger(p)


def run(*args):
    return subprocess.run([sys.executable, str(ROOT / "assets/scripts/decision_ledger.py"), *args], capture_output=True, text=True)


def test_cli_check_exit_codes(tmp_path):
    p = write(tmp_path, line("D-0001"), line("D-0002"))
    ok = run("--ledger", str(p), "check", "D-0001", "D-0002")
    assert ok.returncode == 0 and "OK" in ok.stdout
    bad = run("--ledger", str(p), "check", "D-0001", "D-0003", "D-9")
    assert bad.returncode == 1
    named = bad.stderr.strip().rsplit(": ", 1)[-1]
    assert named == "D-0003, D-9"
    gone = run("--ledger", str(tmp_path / "nope.md"), "check", "D-0001")
    assert gone.returncode == 2 and "cannot read the ledger" in gone.stderr


def test_cli_list_filters_by_status(tmp_path):
    p = write(tmp_path, line("D-0001"), line("D-0002", "AGENT", "PROVISIONAL"))
    everything = run("--ledger", str(p), "list")
    assert "D-0001" in everything.stdout and "D-0002" in everything.stdout
    only = run("--ledger", str(p), "list", "--status", "PROVISIONAL")
    assert "D-0002" in only.stdout and "D-0001" not in only.stdout


def test_cli_help_works():
    out = run("--help")
    assert out.returncode == 0 and "--ledger" in out.stdout


BASELINE_COMMIT = "77b663f1"
BASELINE_LAST = 142
LEDGER_REL = ".claude/knowledge/decision_ledger.md"
STATUS_OF = {"EVE": "DECIDED", "AGENT": "PROVISIONAL", "NOT STATED": "NOT-STATED", "REVIEW SESSION": "RELAYED"}


def check_numbering(path):
    numbers = list(dl.read_ledger(path))
    assert numbers == ["D-%04d" % i for i in range(1, len(numbers) + 1)], "numbers have a gap or are out of order"


def check_statuses(path):
    for number, e in dl.read_ledger(path).items():
        assert e["status"] == STATUS_OF[e["taken_by"]], number


def check_header_counts(path):
    """The counts written in the ledger header equal the counts computed from its lines."""
    entries = dl.read_ledger(path)
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r"\*\*Total (\d+): EVE (\d+), AGENT (\d+), NOT STATED (\d+), REVIEW SESSION (\d+)\.\*\*", text)
    assert m, "the header has no total line"
    written = tuple(int(x) for x in m.groups())
    by = lambda k: sum(1 for e in entries.values() if e["taken_by"] == k)
    computed = (len(entries), by("EVE"), by("AGENT"), by("NOT STATED"), by("REVIEW SESSION"))
    assert written == computed, (written, computed)


def check_relations(path):
    entries = dl.read_ledger(path)
    for number, e in entries.items():
        for cited in dl.NUMBER.findall(e["relation"]):
            assert cited in entries and cited != number, (number, e["relation"])


def _first_words(e):
    return " ".join(e["decision"].split()[:8])


def baseline_entries(tmp_path):
    out = subprocess.run(["git", "show", "%s:%s" % (BASELINE_COMMIT, LEDGER_REL)], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    p = tmp_path / "baseline_ledger.md"
    p.write_text(out.stdout, encoding="utf-8")
    return dl.read_ledger(p)


def check_old_lines_unchanged(path, baseline):
    entries = dl.read_ledger(path)
    for number, old in baseline.items():
        assert number in entries, "%s was lost" % number
        new = entries[number]
        assert new["date"] == old["date"], "%s changed its date" % number
        assert _first_words(new) == _first_words(old), "%s changed its decision" % number
        assert new["old_key"] == old["old_key"], "%s changed its old key" % number


def test_real_ledger_parses_and_is_numbered_without_gaps():
    check_numbering(REAL_LEDGER)
    assert len(dl.read_ledger(REAL_LEDGER)) >= BASELINE_LAST


def test_real_ledger_header_counts_equal_the_computed_counts():
    check_header_counts(REAL_LEDGER)


def test_real_ledger_status_follows_taken_by():
    check_statuses(REAL_LEDGER)
    entries = dl.read_ledger(REAL_LEDGER)
    assert any(e["taken_by"] == "EVE" for e in entries.values())


def test_real_ledger_earlier_lines_keep_number_date_and_first_words(tmp_path):
    baseline = baseline_entries(tmp_path)
    assert len(baseline) == BASELINE_LAST
    check_old_lines_unchanged(REAL_LEDGER, baseline)


def _mutated(tmp_path, fn):
    text = REAL_LEDGER.read_text(encoding="utf-8")
    p = tmp_path / "mut.md"
    p.write_text(fn(text), encoding="utf-8")
    return p


def _has_failure(check, p, *args):
    try:
        check(p, *args)
    except (AssertionError, ValueError):
        return True
    return False


def test_mutations_of_a_copy_of_the_ledger_are_caught(tmp_path):
    baseline = baseline_entries(tmp_path)

    def dup(t):
        return t.replace("\nD-0003 |", "\nD-0002 |", 1)

    def gap(t):
        return re.sub(r"\nD-0003 \|[^\n]*", "", t, count=1)

    def wrong_status(t):
        return re.sub(r"(\nD-0001 \|(?:[^|]*\|){5}) DECIDED", r"\1 PROVISIONAL", t, count=1)

    def header_off(t):
        return re.sub(r"\*\*Total (\d+):", lambda m: "**Total %d:" % (int(m.group(1)) + 1), t, count=1)

    def renumbered(t):
        return t.replace("\nD-0005 |", "\nD-0500 |", 1)

    assert _has_failure(check_numbering, _mutated(tmp_path, dup))
    assert _has_failure(check_numbering, _mutated(tmp_path, gap))
    assert _has_failure(check_statuses, _mutated(tmp_path, wrong_status))
    assert _has_failure(check_header_counts, _mutated(tmp_path, header_off))
    assert _has_failure(check_old_lines_unchanged, _mutated(tmp_path, renumbered), baseline)
    # the unmutated copy passes every check
    ok = _mutated(tmp_path, lambda t: t)
    for check in (check_numbering, check_statuses, check_header_counts, check_relations):
        check(ok)
    check_old_lines_unchanged(ok, baseline)


def test_a_decision_of_her_own_turns_names_the_transcript_line_and_was_compared():
    entries = dl.read_ledger(REAL_LEDGER)
    for number in ["D-%04d" % i for i in range(108, 130)]:
        e = entries[number]
        assert e["taken_by"] == "EVE", number
        assert re.search(r"cd1b0ac7 #\d{4}", e["source"]), (number, e["source"])
        assert "was not compared" not in e["evidence"], number


def test_the_review_sessions_plan_is_on_its_own_lines_that_are_not_decided():
    entries = dl.read_ledger(REAL_LEDGER)
    relayed = [e for e in entries.values() if e["taken_by"] == "REVIEW SESSION"]
    assert relayed
    for e in relayed:
        assert e["status"] == "RELAYED"
        assert e["date"] == "2026-11-16"
        splits = dl.NUMBER.findall(e["relation"])
        assert e["relation"].startswith("split from D-") and splits, e["number"]
        assert all(entries[n]["status"] == "DECIDED" for n in splits), e["number"]
        assert "not her words" in e["evidence"], e["number"]


def test_a_line_keeps_the_colon_of_the_old_ledger_after_hedged():
    assert "| (hedged): ADR-100 point 7" in REAL_LEDGER.read_text(encoding="utf-8")


def test_real_ledger_relations_name_numbers_that_exist():
    check_relations(REAL_LEDGER)
