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
from transformer.anchor import read_anchor_if_key
path, stop, rows = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
good = bad = hits = 0
problems = set()
while time.time() < stop:
    try:
        df = pl.scan_parquet(path).collect()                       # a plain scan by name: never half-written
        assert df.height == rows and df["v"].n_unique() == 1, "half-written table"
        for expected in ("K0", "K1"):                              # the app's own read path: the key, then the table
            table = read_anchor_if_key(path, "sparmvet_tier1_key", expected)
            if table is not None:
                content = table.collect()
                hits += 1
                assert content.height == rows and content["v"].n_unique() == 1 and content["v"][0] == expected, \
                    "the key %s was served with the content of %s" % (expected, content["v"][0])
        good += 1
    except Exception as exc:
        bad += 1
        problems.add(type(exc).__name__ + ": " + str(exc)[:80])
print(good, bad, hits, sorted(problems))
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
    good, bad, hits, problems = reader_out.split(" ", 3)
    assert int(writer_out) >= 5, "the writer must rewrite the table many times while the reader reads"
    assert int(good) >= 20, "the reader must read many times"
    assert int(bad) == 0, problems
    assert int(hits) >= 20, "the key check must serve the table many times"


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


def _plant(folder, name, age_seconds):
    path = folder / name
    path.write_bytes(b"x" * 1000)
    old = time.time() - age_seconds
    os.utime(path, (old, old))
    return path


def test_leftovers_of_a_killed_writer_are_removed_at_the_next_write_of_the_same_table_but_a_fresh_one_is_kept(tmp_path):
    from transformer.anchor import ORPHAN_AGE_SECONDS
    old = _plant(tmp_path, ".C.parquet.abc123.tmp", ORPHAN_AGE_SECONDS + 60)          # a killed writer, long ago
    fresh = _plant(tmp_path, ".C.parquet.def456.tmp", 5)                              # a write in progress by another process
    other_table = _plant(tmp_path, ".D.parquet.zzz999.tmp", ORPHAN_AGE_SECONDS + 60)  # another table: not this write's business
    not_ours = _plant(tmp_path, "notes.tmp", ORPHAN_AGE_SECONDS + 60)                 # a file that is not a temporary of the store
    write_anchor(pl.DataFrame({"a": [1]}).lazy(), str(tmp_path / "C.parquet"), decision_hash="K", metadata={"sparmvet_tier1_key": "K"})
    assert not old.exists(), "a leftover older than the age limit must be removed"
    assert fresh.exists(), "a recent temporary file may be a write in progress and must not be touched"
    assert other_table.exists() and not_ours.exists()


def test_the_start_cleanup_removes_every_old_leftover_and_only_those(tmp_path):
    from transformer.anchor import ORPHAN_AGE_SECONDS, remove_orphan_temporaries
    table = tmp_path / "C.parquet"
    write_anchor(pl.DataFrame({"a": [1]}).lazy(), str(table), decision_hash="K", metadata={"sparmvet_tier1_key": "K"})
    old_one = _plant(tmp_path, ".C.parquet.abc123.tmp", ORPHAN_AGE_SECONDS + 1)
    old_two = _plant(tmp_path, ".C__T2.parquet.qwe789.tmp", ORPHAN_AGE_SECONDS * 5)
    fresh = _plant(tmp_path, ".D.parquet.def456.tmp", 1)
    removed = remove_orphan_temporaries(tmp_path)
    assert sorted(removed) == sorted([old_one.name, old_two.name])
    assert fresh.exists() and table.exists()
    assert remove_orphan_temporaries(tmp_path / "does_not_exist") == []


def test_a_leftover_is_never_read_as_a_table(tmp_path):
    from transformer.anchor import ORPHAN_AGE_SECONDS, read_anchor_if_key
    leftover = tmp_path / ".C.parquet.abc123.tmp"
    pl.DataFrame({"a": [1]}).write_parquet(leftover, metadata={"sparmvet_tier1_key": "K"})
    old = time.time() - ORPHAN_AGE_SECONDS - 1
    os.utime(leftover, (old, old))
    assert read_anchor_if_key(tmp_path / "C.parquet", "sparmvet_tier1_key", "K") is None
    assert list(tmp_path.glob("*.parquet")) == []


def test_a_stored_table_is_served_only_with_its_own_key_and_an_unreadable_one_is_not_served(tmp_path):
    from transformer.anchor import read_anchor_if_key
    path = tmp_path / "C.parquet"
    write_anchor(pl.DataFrame({"a": [1, 2]}).lazy(), str(path), decision_hash="K", metadata={"sparmvet_tier1_key": "K"})
    assert read_anchor_if_key(path, "sparmvet_tier1_key", "K").collect()["a"].to_list() == [1, 2]
    assert read_anchor_if_key(path, "sparmvet_tier1_key", "OTHER") is None
    assert read_anchor_if_key(tmp_path / "missing.parquet", "sparmvet_tier1_key", "K") is None
    path.write_bytes(b"not a parquet file")
    assert read_anchor_if_key(path, "sparmvet_tier1_key", "K") is None


def test_the_scan_given_back_is_the_file_just_written_even_if_the_name_is_replaced_at_once(tmp_path):
    path = tmp_path / "C.parquet"
    lf = write_anchor(pl.DataFrame({"a": [1, 2]}).lazy(), str(path), decision_hash="K", metadata={"sparmvet_tier1_key": "K"})
    write_anchor(pl.DataFrame({"a": [9]}).lazy(), str(path), decision_hash="L", metadata={"sparmvet_tier1_key": "L"})
    assert lf.collect()["a"].to_list() == [1, 2]
