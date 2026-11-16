"""A stored table is replaced in one step: a reader sees the old file or the new one, never a half-written one (STALE-KEY-STORE-1).

Before: `write_anchor` wrote the Parquet straight to the final name. A second process that read the same stored table while
it was rewritten was killed by the operating system (SIGBUS, an mmap of a file that shrank) in 3 of 3 runs, and one process
serves every session of the app. The key is in the footer of the same file, so the table and its key are replaced together.

The reader and the writer are two separate processes, as in the app with two sessions.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_anchor_atomic.py -q
"""
import os
import subprocess
import sys
import time

import polars as pl
import pytest

from transformer.anchor import write_anchor

ROWS = 300_000
SECONDS = 4.0

WRITER = """
import sys, time
import polars as pl
from transformer.anchor import write_anchor
path, stop, rows = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
n = 0
while time.time() < stop:
    marker = "K%d" % (n % 2)
    lf = pl.DataFrame({"v": [marker] * rows, "i": list(range(rows))}).lazy()
    write_anchor(lf, path, decision_hash=marker, metadata={"sparmvet_tier1_key": marker})
    n += 1
print(n)
"""

READER = """
import sys, time
import polars as pl
path, stop, rows = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
good = bad = 0
problems = set()
while time.time() < stop:
    try:
        df = pl.scan_parquet(path).collect()                       # the path the app reads by
        assert df.height == rows and df["v"].n_unique() == 1, "half-written table"
        with open(path, "rb") as one_file:                         # one file: its key and its content together
            key = pl.read_parquet_metadata(one_file)["sparmvet_tier1_key"]
            one_file.seek(0)
            content = pl.read_parquet(one_file)
        assert content["v"][0] == key and content.height == rows, "key and table of different files"
        good += 1
    except Exception as exc:
        bad += 1
        problems.add(type(exc).__name__ + ": " + str(exc)[:80])
print(good, bad, sorted(problems))
"""


def test_a_reader_never_sees_a_half_written_stored_table(tmp_path):
    path = str(tmp_path / "C.parquet")
    write_anchor(pl.DataFrame({"v": ["K0"] * ROWS, "i": list(range(ROWS))}).lazy(), path, decision_hash="K0",
                 metadata={"sparmvet_tier1_key": "K0"})
    stop = str(time.time() + SECONDS)
    env = {**os.environ}
    writer = subprocess.Popen([sys.executable, "-c", WRITER, path, stop, str(ROWS)], stdout=subprocess.PIPE, text=True, env=env)
    reader = subprocess.Popen([sys.executable, "-c", READER, path, stop, str(ROWS)], stdout=subprocess.PIPE, text=True, env=env)
    reader_out, _ = reader.communicate(timeout=120)
    writer_out, _ = writer.communicate(timeout=120)
    assert reader.returncode == 0, f"the reader process was killed (exit {reader.returncode}); it read a file that was being rewritten"
    assert writer.returncode == 0
    good, bad, problems = reader_out.split(" ", 2)
    assert int(writer_out) >= 5, "the writer must rewrite the table many times while the reader reads"
    assert int(good) >= 20, "the reader must read many times"
    assert int(bad) == 0, problems


def test_a_failed_write_leaves_the_stored_table_and_no_temporary_file(tmp_path):
    path = tmp_path / "C.parquet"
    write_anchor(pl.DataFrame({"a": [1, 2]}).lazy(), str(path), decision_hash="OLD", metadata={"sparmvet_tier1_key": "OLD"})
    broken = pl.DataFrame({"a": [1]}).lazy().select(pl.col("missing"))
    with pytest.raises(Exception):
        write_anchor(broken, str(path), decision_hash="NEW", metadata={"sparmvet_tier1_key": "NEW"})
    assert pl.read_parquet_metadata(str(path))["sparmvet_tier1_key"] == "OLD"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["C.parquet"]


def test_a_rewrite_keeps_the_file_mode_and_leaves_no_temporary_file(tmp_path):
    path = tmp_path / "C.parquet"
    write_anchor(pl.DataFrame({"a": [1]}).lazy(), str(path), decision_hash="K1", metadata={"sparmvet_tier1_key": "K1"})
    os.chmod(path, 0o640)
    write_anchor(pl.DataFrame({"a": [2]}).lazy(), str(path), decision_hash="K2", metadata={"sparmvet_tier1_key": "K2"})
    assert (os.stat(path).st_mode & 0o777) == 0o640
    assert pl.read_parquet_metadata(str(path))["sparmvet_tier1_key"] == "K2"
    assert [p.name for p in tmp_path.iterdir()] == ["C.parquet"]


def test_without_a_key_the_table_is_still_replaced_in_one_step(tmp_path):
    path = tmp_path / "C.parquet"
    write_anchor(pl.DataFrame({"a": [1, 2, 3]}).lazy(), str(path))
    write_anchor(pl.DataFrame({"a": [9]}).lazy(), str(path))
    assert pl.read_parquet(str(path))["a"].to_list() == [9]
    assert [p.name for p in tmp_path.iterdir()] == ["C.parquet"]


def test_a_table_whose_key_stopped_being_true_is_returned_but_not_stored(tmp_path):
    """`still_valid` is asked once the table is complete: False means the inputs changed while it was built (STALE-KEY-STORE-1)."""
    path = tmp_path / "C.parquet"
    write_anchor(pl.DataFrame({"a": [1]}).lazy(), str(path), decision_hash="OLD", metadata={"sparmvet_tier1_key": "OLD"})
    table = write_anchor(pl.DataFrame({"a": [7, 8]}).lazy(), str(path), decision_hash="NEW", metadata={"sparmvet_tier1_key": "NEW"},
                         still_valid=lambda: False)
    assert table.collect()["a"].to_list() == [7, 8]
    assert pl.read_parquet_metadata(str(path))["sparmvet_tier1_key"] == "OLD"     # the stored table is untouched
    assert [p.name for p in tmp_path.iterdir()] == ["C.parquet"]
    write_anchor(pl.DataFrame({"a": [7, 8]}).lazy(), str(path), decision_hash="NEW", metadata={"sparmvet_tier1_key": "NEW"},
                 still_valid=lambda: True)
    assert pl.read_parquet_metadata(str(path))["sparmvet_tier1_key"] == "NEW"
