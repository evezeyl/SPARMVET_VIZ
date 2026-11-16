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


def test_not_decided_names_the_numbers_that_exist_but_are_not_hers_with_their_status(tmp_path):
    p = write(tmp_path, line("D-0001"), line("D-0002", "AGENT", "PROVISIONAL"), line("D-0003", "NOT STATED", "NOT-STATED"),
              line("D-0004", "REVIEW SESSION", "RELAYED"))
    entries = dl.read_ledger(p)
    assert dl.not_decided(["D-0001", "D-0002", "D-0003", "D-0004", "D-0099"], entries) == [
        ("D-0002", "PROVISIONAL"), ("D-0003", "NOT-STATED"), ("D-0004", "RELAYED")]
    assert dl.not_decided([], entries) == [] and dl.not_decided(["D-0001"], entries) == []


def test_cli_check_decided_refuses_a_line_that_is_not_hers(tmp_path):
    p = write(tmp_path, line("D-0001"), line("D-0004", "REVIEW SESSION", "RELAYED"))
    assert run("--ledger", str(p), "check", "D-0001", "D-0004").returncode == 0
    ok = run("--ledger", str(p), "check", "--decided", "D-0001")
    assert ok.returncode == 0 and "OK" in ok.stdout
    bad = run("--ledger", str(p), "check", "--decided", "D-0001", "D-0004")
    assert bad.returncode == 1 and "D-0004 (RELAYED)" in bad.stderr and "D-0001 (" not in bad.stderr
    assert run("--ledger", str(p), "check", "--decided", "D-0009").returncode == 1


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


CONFIRMED = re.compile(r"; confirmed by (D-\d{4})$")
REPLACED = re.compile(r"; replaced by (D-\d{4}) \(recorded by (D-\d{4})\)$")
MAY_CHANGE = {"taken_by", "status", "relation"}


def _after(a, b):
    return int(a[2:]) < int(b[2:])


def _later_line_records(entries, number, later, verb, *cited):
    """A later line that exists, is taken by EVE and, in the clause of its relation that starts with `verb`, names the old number."""
    assert later in entries and _after(number, later), "%s: the line %s does not exist or is not later" % (number, later)
    line_ = entries[later]
    assert line_["taken_by"] == "EVE" and line_["status"] == "DECIDED", "%s: %s is not taken by EVE" % (number, later)
    clauses = [c.strip() for c in line_["relation"].split(";") if c.strip().startswith(verb + " ")]
    named = [n for c in clauses for n in dl.NUMBER.findall(c)]
    assert number in named and all(c in named for c in cited), "%s: %s does not record it in its relation" % (number, later)


def git_versions(tmp_path, upto="HEAD"):
    """Every version of the ledger in git from the baseline commit to `upto`, oldest first, as [(label, path)].

    Why this form: the commits of the first-parent line that touched the ledger file are the versions that
    follow each other, so no line count is pinned and a line added in the future is guarded from the commit that adds it.
    """
    out = subprocess.run(["git", "rev-list", "--reverse", "--first-parent", "%s..%s" % (BASELINE_COMMIT, upto), "--", LEDGER_REL],
                         cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    versions = []
    for commit in [BASELINE_COMMIT] + out.stdout.split():
        shown = subprocess.run(["git", "show", "%s:%s" % (commit, LEDGER_REL)], cwd=ROOT, capture_output=True, text=True)
        assert shown.returncode == 0, shown.stderr
        path = tmp_path / ("ledger_%s.md" % commit[:8])
        path.write_text(shown.stdout, encoding="utf-8")
        versions.append((commit[:8], path))
    return versions


def check_old_lines_unchanged(path, baseline):
    """No earlier line changes, with ONE exception (Eve, 2026-11-16, D-0161).

    A line that was RELAYED (taken by REVIEW SESSION) may become taken by EVE / DECIDED, or be marked replaced,
    only when a later line that exists records it. Then its taken by, status and relation change, and only the
    relation by the added ending "; confirmed by D-M" or "; replaced by D-R (recorded by D-M)". The decision
    words and every other field stay equal to the baseline commit.
    """
    entries = dl.read_ledger(path)
    for number, old in baseline.items():
        assert number in entries, "%s was lost" % number
        new = entries[number]
        changed = {f for f in dl.FIELDS if new[f] != old[f]}
        if not changed:
            continue
        assert changed <= MAY_CHANGE, "%s changed its field %s" % (number, sorted(changed - MAY_CHANGE))
        assert old["taken_by"] == "REVIEW SESSION" and old["status"] == "RELAYED", "%s was not a relayed line, it may not change" % number
        if new["taken_by"] != old["taken_by"]:
            assert new["taken_by"] == "EVE", "%s changed its taken by to %s" % (number, new["taken_by"])
            m = CONFIRMED.search(new["relation"])
            assert m and new["relation"] == old["relation"] + m.group(0), "%s: the relation does not end with the confirming line" % number
            _later_line_records(entries, number, m.group(1), "confirms")
        else:
            assert new["status"] == old["status"], "%s changed its status without its taken by" % number
            m = REPLACED.search(new["relation"])
            assert m and new["relation"] == old["relation"] + m.group(0), "%s: the relation does not end with the replacement" % number
            _later_line_records(entries, number, m.group(2), "records", m.group(1))
            assert entries[m.group(1)]["status"] == "DECIDED" and _after(number, m.group(1)), "%s: the replacing line is not decided or not later" % number


def test_every_version_of_the_ledger_in_git_follows_the_one_before_it(tmp_path):
    """Each pair of versions that follow each other, and HEAD against the working tree, obeys the rule of the earlier lines."""
    versions = git_versions(tmp_path) + [("working tree", REAL_LEDGER)]
    assert len(versions) >= 3
    for (old_label, old_path), (new_label, new_path) in zip(versions, versions[1:]):
        try:
            check_old_lines_unchanged(new_path, dl.read_ledger(old_path))
        except AssertionError as exc:
            raise AssertionError("%s -> %s: %s" % (old_label, new_label, exc))
        check_numbering(new_path)
        check_statuses(new_path)
        check_header_counts(new_path)


def test_real_ledger_parses_and_is_numbered_without_gaps():
    check_numbering(REAL_LEDGER)
    assert len(dl.read_ledger(REAL_LEDGER)) >= BASELINE_LAST


def test_real_ledger_header_counts_equal_the_computed_counts():
    check_header_counts(REAL_LEDGER)


def test_real_ledger_status_follows_taken_by():
    check_statuses(REAL_LEDGER)
    entries = dl.read_ledger(REAL_LEDGER)
    assert any(e["taken_by"] == "EVE" for e in entries.values())


def test_real_ledger_earlier_lines_are_unchanged_in_every_field(tmp_path):
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

    def late_word(t):
        m = re.search(r"\nD-0003 \|(?:[^|]*\|){2} ([^|]*) \|", t)
        assert len(m.group(1).split()) > 8
        return t[:m.start(1)] + m.group(1) + " extra" + t[m.end(1):]

    def evidence(t):
        return re.sub(r"(\nD-0003 \|[^\n]*?) \| ([^|\n]*) \| ([^|\n]*)\n", r"\1 | \2 changed | \3\n", t, count=1)

    assert _has_failure(check_old_lines_unchanged, _mutated(tmp_path, late_word), baseline)
    assert _has_failure(check_old_lines_unchanged, _mutated(tmp_path, evidence), baseline)
    # the unmutated copy passes every check
    ok = _mutated(tmp_path, lambda t: t)
    for check in (check_numbering, check_statuses, check_header_counts, check_relations):
        check(ok)
    check_old_lines_unchanged(ok, baseline)


def _set_fields(text, number, **fields):
    """Return the ledger text with the named fields of one line replaced."""
    m = re.search(r"^%s \|[^\n]*$" % number, text, re.M)
    parts = m.group(0).split(" | ")
    for key, value in fields.items():
        parts[dl.FIELDS.index(key)] = value(parts[dl.FIELDS.index(key)]) if callable(value) else value
    return text[:m.start()] + " | ".join(parts) + text[m.end():]


def test_the_one_exception_to_the_earlier_lines_is_allowed_and_nothing_more(tmp_path):
    baseline = baseline_entries(tmp_path)
    real = REAL_LEDGER.read_text(encoding="utf-8")
    entries = dl.read_ledger(REAL_LEDGER)
    agent_line = next(n for n, e in baseline.items() if e["taken_by"] == "AGENT")

    def bad(fn):
        p = tmp_path / "m.md"
        p.write_text(fn(real), encoding="utf-8")
        try:
            check_old_lines_unchanged(p, baseline)
        except AssertionError:      # a ValueError (an unreadable ledger) would be the wrong reason and is not caught
            return True
        return False

    # what the real ledger holds: 12 lines confirmed, D-0140 replaced
    changed = [n for n in baseline if any(entries[n][f] != baseline[n][f] for f in dl.FIELDS)]
    assert changed == ["D-%04d" % i for i in list(range(130, 140)) + [140, 141, 142]]
    assert entries["D-0130"]["taken_by"] == "EVE" and entries["D-0140"]["taken_by"] == "REVIEW SESSION"
    # a changed decision word of a confirmed line
    assert bad(lambda t: _set_fields(t, "D-0130", decision=lambda d: d.replace("role statement", "role sentence")))
    # her words of a confirmed line
    assert bad(lambda t: _set_fields(t, "D-0131", evidence=lambda d: d + " x"))
    # a status raised with no confirming line named
    assert bad(lambda t: _set_fields(t, "D-0131", relation=lambda r: r.replace("; confirmed by D-0161", "")))
    # the old part of the relation rewritten while the ending is right
    assert bad(lambda t: _set_fields(t, "D-0131", relation=lambda r: r.replace("split from D-0109", "split from D-0110")))
    # a confirming line that does not exist, is not later, is not hers, or does not record the number
    assert bad(lambda t: _set_fields(t, "D-0131", relation=lambda r: r.replace("D-0161", "D-0999")))
    assert bad(lambda t: _set_fields(t, "D-0131", relation=lambda r: r.replace("D-0161", "D-0129")))
    assert bad(lambda t: _set_fields(t, "D-0131", relation=lambda r: r.replace("D-0161", "D-0162")))
    assert bad(lambda t: _set_fields(t, "D-0161", taken_by="AGENT", status="PROVISIONAL"))
    # an AGENT line raised, with a confirming line named
    assert bad(lambda t: _set_fields(t, agent_line, taken_by="EVE", status="DECIDED", relation=lambda r: r + "; confirmed by D-0161"))
    # an AGENT line raised through an edited D-0161 that now names it: only "the old line was RELAYED" can refuse this
    assert bad(lambda t: _set_fields(_set_fields(t, agent_line, taken_by="EVE", status="DECIDED", relation=lambda r: r + "; confirmed by D-0161"),
                                     "D-0161", relation=lambda r: r.replace("confirms ", "confirms %s, " % agent_line, 1)))
    # D-0140's old relation text rewritten, its ending kept: only "the relation is the old text plus the ending" can refuse this
    assert bad(lambda t: _set_fields(t, "D-0140", relation=lambda r: r.replace("split from D-0127", "split from D-0128")))
    # a decided line of hers whose relation is extended
    assert bad(lambda t: _set_fields(t, "D-0001", relation=lambda r: r + "; confirmed by D-0161"))
    # D-0140 was replaced, not confirmed: raising it with the confirming ending is refused
    assert bad(lambda t: _set_fields(t, "D-0140", taken_by="EVE", status="DECIDED", relation=lambda r: r.split("; replaced by")[0] + "; confirmed by D-0161"))
    # D-0140 marked replaced by a line that is not decided
    assert bad(lambda t: _set_fields(t, "D-0140", relation=lambda r: r.replace("D-0141", "D-0151")))
    assert bad(lambda t: _set_fields(t, "D-0140", relation=lambda r: r.replace("D-0141 (recorded", "D-0999 (recorded")))
    # and an old line that is lost
    assert bad(lambda t: re.sub(r"^D-0130 \|[^\n]*\n", "", t, flags=re.M))


def test_lines_that_were_added_after_the_baseline_are_guarded_against_the_version_in_git(tmp_path):
    """The earlier lines of the checked-in ledger are the base: D-0143 to D-0163 and every later line cannot change either."""
    head = dl.read_ledger(git_versions(tmp_path)[-1][1])
    assert "D-0163" in head
    real = REAL_LEDGER.read_text(encoding="utf-8")

    def bad(fn):
        p = tmp_path / "m2.md"
        p.write_text(fn(real), encoding="utf-8")
        try:
            check_old_lines_unchanged(p, head)
        except AssertionError:
            return True
        return False

    assert not bad(lambda t: t)
    assert bad(lambda t: _set_fields(t, "D-0150", decision=lambda d: d.replace("have been refactored", "have been changed")))
    assert bad(lambda t: _set_fields(t, "D-0145", evidence=lambda d: d + " x"))
    assert bad(lambda t: _set_fields(t, "D-0152", taken_by="EVE", status="DECIDED"))
    assert bad(lambda t: _set_fields(t, "D-0152", taken_by="EVE", status="DECIDED", relation=lambda r: r + "; confirmed by D-0161"))
    assert bad(lambda t: _set_fields(t, "D-0163", taken_by="EVE", status="DECIDED", relation=lambda r: r + "; confirmed by D-0162"))
    assert bad(lambda t: _set_fields(t, "D-0160", decision=lambda d: d.replace("should not have strict", "should have strict")))
    assert bad(lambda t: re.sub(r"^D-0158 \|[^\n]*\n", "", t, flags=re.M))


def test_the_answers_of_her_turns_of_2026_11_16_are_decided_lines_and_the_passes_are_not():
    entries = dl.read_ledger(REAL_LEDGER)
    for number in ["D-%04d" % i for i in range(153, 163)]:
        e = entries[number]
        assert e["taken_by"] == "EVE" and e["status"] == "DECIDED", number
        assert re.search(r"cd1b0ac7 #\d{4}", e["source"]), (number, e["source"])
    assert entries["D-0163"]["taken_by"] == "REVIEW SESSION"
    assert "records D-0140 replaced by D-0141" in entries["D-0161"]["relation"]
    for n in ["D-%04d" % i for i in list(range(130, 140)) + [141, 142]]:
        assert entries[n]["taken_by"] == "EVE" and entries[n]["relation"].endswith("; confirmed by D-0161"), n


def test_the_answers_of_points_5_and_6_and_of_the_verification_questions_are_decided_lines_of_her_turns():
    entries = dl.read_ledger(REAL_LEDGER)
    for number in ["D-%04d" % i for i in range(164, 177)]:
        e = entries[number]
        assert e["taken_by"] == "EVE" and e["status"] == "DECIDED", number
        assert re.search(r"cd1b0ac7 #\d{4}", e["source"]), (number, e["source"])
        assert "(#2" in e["evidence"], number          # her words are quoted with the line of the transcript
    text = REAL_LEDGER.read_text(encoding="utf-8")
    # her proposal of the reset was decided by her next turns (D-0177, D-0178); the entry says so and keeps the old text
    assert "NOW DECIDED by `D-0177` and `D-0178`" in text
    assert "HER PROPOSAL, waited for her confirmation, not decided at the time" in text
    for number in ["D-0177", "D-0178", "D-0179", "D-0180", "D-0181"]:
        e = entries[number]
        assert e["taken_by"] == "EVE" and e["status"] == "DECIDED", number
        assert re.search(r"cd1b0ac7 #\d{4}", e["source"]), (number, e["source"])
        assert "(#2" in e["evidence"], number
    assert "D-0014" in entries["D-0178"]["relation"] and "D-0014" in entries["D-0179"]["relation"]


MOVED_OUT_OF_THE_DECISION_FIELD = {
    "D-0160": ["as long as needed", "no padding", "cleaned by its owner"],
    "D-0165": ["NONE-CHECKED"],
    "D-0168": ["recipe's own"],
    "D-0171": ["identifier"],
    "D-0173": ["Nothing is reverted", "confirmed by her", "comes back as a question"],
    "D-0155": ["no agent file"],
    "D-0156": ["builder-opus"],
    "D-0162": ["2026-11-09"],
    "D-0169": ["as built", "closed"],
    "D-0174": ["YAML writer"],
}


def test_the_decision_field_of_the_lines_of_this_branch_holds_only_what_she_said_and_the_rest_is_marked_as_not_hers():
    """D-0153 to D-0176: what the review session or the builder added is in the evidence field, marked (D-0125: her words, never paraphrased)."""
    entries = dl.read_ledger(REAL_LEDGER)
    for number, words in MOVED_OUT_OF_THE_DECISION_FIELD.items():
        for w in words:
            assert w not in entries[number]["decision"], (number, w)
        assert "[Not her words, added by " in entries[number]["evidence"], number
    # her unfinished sentence stays unfinished
    assert entries["D-0168"]["decision"].endswith("so it is - [her sentence stops here]")
    # her spelling inside quotation marks
    assert '"a lot of that is more tasks so we can decided than actually rules"' in entries["D-0161"]["decision"]


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
