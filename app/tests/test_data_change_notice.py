"""The sentence HOME shows when a data file changed says what really happens (STALE-KEY-STORE-1, "case D").

Before it said "re-assembling". The first test runs the situation the sentence describes and checks every claim of the
words against the real behaviour; the others check the form Eve asked for (what happened, then "Suggestion: ...").

Mutation index (grep "MUTATION"): M10 = the branch "the tables follow the data" of the notice is always true
(`notice_after_data_change` returns the "follows" sentence whatever the keys) -> test_the_view_follows_the_data_only_when_...

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_data_change_notice.py -q
"""
from pathlib import Path

import pytest

from app.handlers.export_handlers import changed_since_view
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_change_notice import (data_files_changed_notice, inputs_changed_during_build_notice,
                                            notice_after_data_change)
from app.tests.test_cache_chain import World

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def test_the_words_of_a_data_file_changed_after_the_page_loaded_are_true(tmp_path):
    w = World(tmp_path)
    view = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert len(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=view).collect()) == 3
    w.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")             # a pipeline replaces the file
    # "the tables and plots on screen can still come from the earlier file"
    assert len(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=view).collect()) == 3
    # "the export is refused until the page is reloaded": the export compares the keys of the view with the keys now
    now = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert changed_since_view(view, now) == ["the data files"]
    # "reload the page to read the current files": a new page computes new keys and reads the new file
    assert len(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=now).collect()) == 4
    assert changed_since_view(now, w.orch.compute_data_analysis_recipe_keys("tiny")) == []


@pytest.mark.parametrize("follows", [True, False])
def test_the_sentence_says_what_happened_then_a_suggestion(follows):
    text = data_files_changed_notice(follows)
    happened, _, suggestion = text.partition(" Suggestion: ")
    assert happened.startswith("A source data file of this project changed") and suggestion
    assert "re-assembl" not in text.lower(), "nothing is re-assembled by HOME; the old word must not come back"


def test_the_sentence_after_an_outside_change_names_the_reload_and_the_export():
    text = data_files_changed_notice(False)
    assert "reload" in text and "export is refused" in text and "earlier file" in text
    assert "rebuilt" not in text, "the tables are not rebuilt in this case, so the words must not say so"


def test_the_sentence_after_an_import_of_this_session_says_the_tables_are_rebuilt():
    text = data_files_changed_notice(True)
    assert "rebuilt from the new files" in text and "export is refused" not in text


def test_the_view_follows_the_data_only_when_its_keys_describe_the_files_on_disk():
    """MUTATION M10: the decision HOME takes (home_theater.py, `_sync_session_provenance`) is this function; always-true must fail here."""
    assert notice_after_data_change("hash-now", "hash-now") == data_files_changed_notice(True)       # after an import of this session
    assert notice_after_data_change("hash-before", "hash-now") == data_files_changed_notice(False)   # changed from outside
    assert notice_after_data_change(None, "hash-now") == data_files_changed_notice(False)            # keys unreadable: the careful answer
    assert notice_after_data_change("", "") == data_files_changed_notice(True), "no data files on both sides is the same state"


@pytest.mark.parametrize("what", ["the data files changed", "the data analysis recipe changed",
                                  "the data analysis recipe can no longer be read (a line of the file is broken)"])
def test_the_notice_of_a_table_built_while_its_inputs_changed_says_what_then_a_suggestion(what):
    text = inputs_changed_during_build_notice(what)
    happened, _, suggestion = text.partition(" Suggestion: ")
    assert what in happened and "may not match the files" in happened and happened.startswith("While a table was being built")
    assert "reload the page (F5)" in suggestion


def test_home_tells_the_notice_when_the_orchestrator_reports_a_change():
    """The handler passes `_tell_inputs_changed` at all four places where HOME builds a table (Tier 1 twice, Tier 2, the table a plot reads; it was three before the plot's table had its own reader)."""
    source = (ROOT / "app" / "handlers" / "home_theater.py").read_text()
    assert source.count("on_inputs_changed=_tell_inputs_changed") == 4
    assert "notice_after_data_change(view_dbh, new_dbh)" in source and "view_dbh = _data_analysis_recipe_keys().data_batch_hash" in source
    assert "inputs_changed_during_build_notice(change.text)" in source and "session.on_flushed(show, once=True)" in source
