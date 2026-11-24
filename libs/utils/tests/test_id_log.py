"""The log of the ids (D-0575, D-0576, D-0581, D-0582, D-0592): written automatically, one entry per state, never a stop, the click recorded by a function.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_id_log.py -q
"""
import yaml
import pytest

from utils.id_completion import Participant, TableIds, build_report
from utils.id_log import AUTOMATIC, build_entry, entry_text, log_path, read_log, record_read, write_entry

WHEN = "2026-11-24T10:00:00+01:00"


def report(extra=()):
    parts = [Participant("metadata_schema", "metadata", "sample_id", "metadata_schema_not_in_original_data", "unknown"), Participant("A", "data", "sample_id", "A_not_in_original_data", "The tool did not run on this entity.")]
    meta = TableIds("metadata_schema", "metadata", "sample_id", 3, ("S1", "S2", "S3"), ())
    a = TableIds("A", "data", "sample_id", 2 + len(extra), ("S1", "S2"), tuple(extra))
    return build_report(parts, [meta, a], [meta, TableIds("A", "data", "sample_id", 3, ("S1", "S2", "S3"), ())])


def entry(sha="r1", batch="d1", **kw):
    return build_entry(report(), "rec", sha * 8, batch * 8, when=WHEN, **kw)


def test_an_entry_has_the_date_the_fingerprints_the_report_and_says_it_is_automatic():
    e = entry()
    assert e["who"] == AUTOMATIC == "automatic, no user" and e["when"] == WHEN and e["kind"] == "checks"
    assert e["recipe_sha256"] == "r1" * 8 and e["data_batch_hash"] == "d1" * 8
    assert e["ids"]["tables"][1]["ids_added"] == {"count": 1, "ids": ["S3"]}
    assert e["ids"]["check_3"] == "passed"


def test_the_entry_in_plain_words_names_the_added_lines_the_marker_the_apps_words_and_the_recipe_makers_sentence():
    text = entry_text(entry())
    assert "automatic, no user" in text and "A (data)" in text and '1 line(s) added, marked "missing in original table" in A_not_in_original_data' in text
    # the sentence of the recipe maker is shown beside the app's own words (the owner, 2026-11-24)
    assert "in the words of the recipe maker: The tool did not run on this entity" in text and "S3" in text
    assert "Check of the equal sets after the completion: passed" in text


def test_the_data_of_the_entry_holds_the_apps_words_and_the_sentence_per_table():
    table = entry()["ids"]["tables"][1]
    assert table["added_line_words"] == "missing in original table" and table["meaning"] == "The tool did not run on this entity." and table["marker"] == "A_not_in_original_data"


def test_the_first_write_creates_the_folder_and_the_file_with_a_format_number(tmp_path):
    folder = tmp_path / "user" / "_id_logs"
    out = write_entry(folder, entry())
    assert out.written and out.new and out.path == log_path(folder, "rec")
    data = yaml.safe_load(out.path.read_text())
    assert data["format"] == 1 and len(data["entries"]) == 1 and data["entries"][0]["ids"]["ids_in_the_union"] == 3


def test_the_same_recipe_on_the_same_data_adds_nothing_the_log_records_states_not_visits(tmp_path):
    write_entry(tmp_path, entry())
    again = write_entry(tmp_path, entry())
    assert again.written and not again.new
    assert len(read_log(log_path(tmp_path, "rec"))["entries"]) == 1


def test_another_data_batch_or_another_recipe_state_adds_an_entry(tmp_path):
    write_entry(tmp_path, entry())
    assert write_entry(tmp_path, entry(batch="d2")).new
    assert write_entry(tmp_path, entry(sha="r2")).new
    assert [e["data_batch_hash"][:2] for e in read_log(log_path(tmp_path, "rec"))["entries"]] == ["d1", "d2", "d1"]


def test_the_logs_of_two_recipes_are_two_files(tmp_path):
    write_entry(tmp_path, entry())
    other = build_entry(report(), "other", "x", "y", when=WHEN)
    write_entry(tmp_path, other)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["other.id_log.yaml", "rec.id_log.yaml"]


def test_a_folder_that_cannot_be_written_warns_on_the_console_returns_the_text_and_raises_nothing(tmp_path, capsys):
    blocker = tmp_path / "file"
    blocker.write_text("x")     # a file where the folder should be: mkdir fails with an OSError
    out = write_entry(blocker / "_id_logs", entry())
    assert not out.written and out.path is None and out.problem and "could not be written" in out.problem
    assert "A (data)" in out.text and "could not be written" in capsys.readouterr().out


def test_a_log_file_of_another_format_is_left_alone_and_nothing_is_added(tmp_path):
    path = log_path(tmp_path, "rec")
    path.write_text("format: 2\nentries: []\n")
    out = write_entry(tmp_path, entry())
    assert not out.written and "format" in out.problem
    assert path.read_text() == "format: 2\nentries: []\n"


def test_a_file_that_is_not_a_log_is_refused_not_overwritten(tmp_path):
    path = log_path(tmp_path, "rec")
    path.write_text("- just\n- a list\n")
    out = write_entry(tmp_path, entry())
    assert not out.written and path.read_text() == "- just\n- a list\n"


def test_no_temporary_file_is_left_behind(tmp_path):
    write_entry(tmp_path, entry())
    write_entry(tmp_path, entry(batch="d2"))
    assert [p.name for p in tmp_path.iterdir()] == ["rec.id_log.yaml"]


def test_the_click_i_have_read_this_is_recorded_with_who_and_when_and_never_by_the_automatic_name(tmp_path):
    write_entry(tmp_path, entry())
    out = record_read(tmp_path, "rec", "r1" * 8, "d1" * 8, who="EZ", when=WHEN)
    assert out.written and out.new
    kinds = [(e["kind"], e["who"]) for e in read_log(log_path(tmp_path, "rec"))["entries"]]
    assert kinds == [("checks", AUTOMATIC), ("read", "EZ")]
    assert "EZ has read the log" in out.text
    for bad in ("", "   ", AUTOMATIC):
        with pytest.raises(ValueError):
            record_read(tmp_path, "rec", "r1", "d1", who=bad)
    assert len(read_log(log_path(tmp_path, "rec"))["entries"]) == 2


def test_a_read_entry_does_not_hide_a_new_state(tmp_path):
    write_entry(tmp_path, entry())
    record_read(tmp_path, "rec", "r1" * 8, "d1" * 8, who="EZ", when=WHEN)
    assert not write_entry(tmp_path, entry()).new        # same state: still one checks entry
    assert write_entry(tmp_path, entry(batch="d2")).new   # new data: a new entry, to be read again


def test_reading_a_log_that_does_not_exist_is_an_empty_log(tmp_path):
    assert read_log(tmp_path / "none.id_log.yaml") == {"format": 1, "entries": []}
