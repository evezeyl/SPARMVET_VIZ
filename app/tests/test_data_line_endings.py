"""Data and recipe files are byte-exact with LF line ends (D-0349, D-0195: no silent difference between checkouts).

A CRLF copy of a data file gives another data hash and other table keys than a fresh clone. `core.autocrlf=input` hides
such a copy from `git status`; `.gitattributes` (`-text`) shows it. These tests scan EVERY tracked data file of the
repository (`git ls-files`, the extensions `.gitattributes` names), in two places named apart: the committed blob
(`git cat-file`) and the working copy. They also pin how the ingestion reads CRLF text.

Mutation: put a CRLF into a tracked data file -> test_no_tracked_data_file_holds_crlf and test_the_scan_finds_a_crlf_file fail.
Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_data_line_endings.py -q
"""
import subprocess
from pathlib import Path

import polars as pl

from ingestion.ingestor import DataIngestor

ROOT = Path(__file__).resolve().parents[2]
DATA_SUFFIXES = {".tsv", ".csv", ".yaml", ".yml", ".json"}
# Reason: each file holds a carriage return INSIDE a value (10 text values end with CR CR LF in a quoted field), not a line
# ending; cleaning it is not decided (D-0349 task), so the files are not converted. The pinned counts (CR bytes, CR LF pairs)
# make the test fail when such a file gains a real CRLF line ending, loses its CR, or disappears: the list cannot go stale.
INSIDE_VALUE_CR: dict[str, tuple[int, int]] = {
    "assets/test_data/figshare.21737288/csv/fg_metadata.csv": (20, 10),
    "libs/transformer/tests/data/fg_metadata.tsv": (20, 10),
}


def files_with_crlf(paths, root: Path) -> list[str]:
    return sorted(str(p) for p in paths if b"\r" in (root / p).read_bytes())


def cr_counts(data: bytes) -> tuple[int, int]:
    return data.count(b"\r"), data.count(b"\r\n")


def _tracked_data_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    names = [n for n in out.stdout.decode().split("\0") if n]
    return [n for n in names if Path(n).suffix in DATA_SUFFIXES]


def _blobs(names: list[str]) -> dict[str, bytes]:
    out = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input="".join(f":{n}\n" for n in names).encode(),
                         capture_output=True, check=True).stdout
    blobs, pos = {}, 0
    for n in names:
        end = out.index(b"\n", pos)
        head = out[pos:end].split()
        size = int(head[2])
        blobs[n] = out[end + 1:end + 1 + size]
        pos = end + 1 + size + 1
    return blobs


def test_no_tracked_data_file_holds_crlf():
    names = [n for n in _tracked_data_files() if n not in INSIDE_VALUE_CR]
    in_commit = sorted(n for n, b in _blobs(names).items() if b"\r" in b)
    in_copy = sorted(n for n in files_with_crlf([n for n in names if (ROOT / n).is_file()], ROOT) if n not in in_commit)
    msg = []
    if in_commit:
        msg.append(f"the COMMITTED blob holds CR (commit it with LF, D-0349): {in_commit}")
    if in_copy:
        msg.append(f"only the WORKING COPY holds CR (the commit is right; repair with `git checkout -- <file>`): {in_copy}")
    assert not msg, "; ".join(msg)


def test_files_with_a_cr_inside_a_value_are_exactly_the_known_ones():
    tracked = set(_tracked_data_files())
    blobs = _blobs([n for n in INSIDE_VALUE_CR if n in tracked])
    for name, expected in INSIDE_VALUE_CR.items():
        assert name in tracked, f"{name} is listed in INSIDE_VALUE_CR but is no longer tracked: remove it from the list"
        assert cr_counts(blobs[name]) == expected, f"{name}: (CR, CRLF) counts in the commit are {cr_counts(blobs[name])}, pinned {expected}"
        assert (ROOT / name).is_file() and cr_counts((ROOT / name).read_bytes()) == expected, f"{name}: working copy differs (git checkout -- {name})"


def test_the_scan_finds_a_crlf_file(tmp_path):
    (tmp_path / "ok.tsv").write_bytes(b"a\tb\n1\t2\n")
    (tmp_path / "bad.tsv").write_bytes(b"a\tb\r\n1\t2\r\n")
    assert files_with_crlf(["ok.tsv", "bad.tsv"], tmp_path) == ["bad.tsv"]


def test_ingestion_reads_crlf_and_lf_to_the_same_table_with_no_cr_left(tmp_path):
    lf = b"id\tname\tnote\nr1\tK. pneumoniae\tlast text\nr2\tE. coli\t\n"
    (tmp_path / "lf.tsv").write_bytes(lf)
    (tmp_path / "crlf.tsv").write_bytes(lf.replace(b"\n", b"\r\n"))
    tables = {}
    for name in ("lf", "crlf"):
        lazy, _ = DataIngestor(str(tmp_path))._open(name, {"source": {"type": "local_tsv", "path": str(tmp_path / f"{name}.tsv")}})
        tables[name] = lazy.collect()
    assert tables["lf"].equals(tables["crlf"])
    assert not any("\r" in v for v in tables["crlf"]["note"].cast(pl.String).drop_nulls().to_list())
    assert tables["crlf"].columns == ["id", "name", "note"]
