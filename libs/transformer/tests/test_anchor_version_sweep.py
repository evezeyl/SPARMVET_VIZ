"""`remove_tables_of_other_version`: the stored tables of another cache version are removed, nothing else is (D-0240).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_anchor_version_sweep.py -q
"""
import polars as pl

from transformer.anchor import remove_tables_of_other_version, write_anchor

MARK = "sparmvet_cache_version"


def store(path, mark):
    metadata = {"sparmvet_tier1_key": "k"}
    if mark is not None:
        metadata[MARK] = mark
    write_anchor(pl.DataFrame({"a": [1]}).lazy(), str(path), decision_hash="k", metadata=metadata)


def test_a_table_with_another_mark_or_none_is_removed_and_one_with_the_current_mark_stays(tmp_path):
    store(tmp_path / "none.parquet", None)
    store(tmp_path / "four.parquet", "4")
    store(tmp_path / "five.parquet", "5")
    assert remove_tables_of_other_version(tmp_path, MARK, "5") == ["four.parquet", "none.parquet"]
    assert [p.name for p in tmp_path.iterdir()] == ["five.parquet"]


def test_a_parquet_that_carries_no_key_a_broken_file_a_temporary_file_and_other_files_are_left(tmp_path):
    pl.DataFrame({"a": [1]}).write_parquet(tmp_path / "plain.parquet")
    (tmp_path / "broken.parquet").write_bytes(b"x")
    (tmp_path / ".C.parquet.x.tmp").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("x")
    assert remove_tables_of_other_version(tmp_path, MARK, "5") == []
    assert len(list(tmp_path.iterdir())) == 4


def test_a_missing_or_empty_folder_gives_nothing(tmp_path):
    assert remove_tables_of_other_version(tmp_path / "nowhere", MARK, "5") == []
    assert remove_tables_of_other_version(tmp_path, MARK, "5") == []
