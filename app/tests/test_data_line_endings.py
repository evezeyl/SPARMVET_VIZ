"""Data and recipe files are byte-exact with LF line ends (D-0349, D-0195: no silent difference between checkouts).

A CRLF copy of a data file gives another data hash and other table keys than a fresh clone. `core.autocrlf=input` hides
such a copy from `git status`; `.gitattributes` (`-text`) shows it. These tests check the bytes on disk and the tracked
blobs, and pin how the ingestion reads CRLF text.

Mutation: put a CRLF into a tracked data file -> test_no_tracked_data_file_holds_crlf and test_the_scan_finds_a_crlf_file fail.
Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_data_line_endings.py -q
"""
import subprocess
from pathlib import Path

import polars as pl

from ingestion.ingestor import DataIngestor

ROOT = Path(__file__).resolve().parents[2]
DATA_SUFFIXES = {".tsv", ".csv", ".yaml", ".yml", ".json"}
# Known, not converted: 10 text values of this file END with CR CR LF INSIDE a quoted field (stray CR in the value, not a line
# ending). Converting would change values; the owner decides (reported, D-0349 task). No fixture tests Windows endings.
INTENDED_CRLF: set[str] = {"assets/test_data/figshare.21737288/csv/fg_metadata.csv"}


def files_with_crlf(paths, root: Path) -> list[str]:
    return sorted(str(p) for p in paths if b"\r" in (root / p).read_bytes())


def _tracked_data_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "--", "assets", "config"], cwd=ROOT, capture_output=True, check=True)
    names = [n for n in out.stdout.decode().split("\0") if n]
    return [n for n in names if Path(n).suffix in DATA_SUFFIXES and n not in INTENDED_CRLF and (ROOT / n).is_file()]


def test_no_tracked_data_file_holds_crlf():
    found = files_with_crlf(_tracked_data_files(), ROOT)
    assert not found, f"CRLF in tracked data files (bring them to LF, D-0349): {found}"


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
