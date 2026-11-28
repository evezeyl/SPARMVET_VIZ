"""G1 guard (Eve 2026-11-28: audit steps never mix across data): a Restore of a session made on OTHER DATA is refused.

Nothing of the session reaches the state (no steps, no overrides, no ghost file name); one error says what the session's data were and
what the data now loaded are, and what the user can do. The rule is the pure function `session_data_refusal` (tested first, headless);
the handler is tested through the same screen harness as the other Restore tests.

Mutation index (each seen failing):
  MUTATION G1a  `session_data_refusal` returns None for another batch hash (the old warning-only behaviour)
  MUTATION G1b  the handler ignores the refusal and goes on (the steps are applied again)
  MUTATION G1c  a missing key is taken as "same" (the careful answer is to refuse)

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_restore_on_other_data_refused.py -q
"""
from shiny import reactive

from app.modules.session_manager import session_data_refusal
from app.tests.test_session_errors_visible import RESTORE, Screen
from app.tests.test_session_unreadable_files_told import _save

GHOST = {"session_key": "k", "data_batch_hash": "b" * 64, "assembled_at": "2026-11-20T10:00:00",
         "source_files": {"Summary": {"path": "/data/old/summary_v1.tsv", "sha256": "1" * 64}, "meta": {"path": "/data/old/meta.tsv", "sha256": "2" * 64}}}
NOW = {"Summary": {"path": "/data/new/summary_v2.tsv", "sha256": "3" * 64}, "meta": {"path": "/data/old/meta.tsv", "sha256": "2" * 64}}


# -- the pure rule ------------------------------------------------------------------------------------------------------

def test_the_same_data_is_allowed():
    assert session_data_refusal(GHOST, "b" * 64, GHOST["source_files"]) is None


def test_another_batch_hash_is_refused_and_names_the_table_that_differs_on_both_sides():
    text = session_data_refusal(GHOST, "c" * 64, NOW)            # MUTATION G1a fails here
    assert text and "was made on other data" in text and "not restored" in text
    assert "summary_v1.tsv, 11111111" in text and "summary_v2.tsv, 33333333" in text, text
    assert "meta.tsv" not in text, "a table whose file did not change is not listed"
    assert "2026-11-20" in text and "bbbbbbbb" in text and "cccccccc" in text
    assert ". Suggestion: upload the same data files again" in text and "start a new session" in text
    assert "carry" not in text.lower(), "nothing promises a later feature"


def test_a_record_without_per_file_hashes_is_refused_on_the_batch_hash_alone():
    text = session_data_refusal({"data_batch_hash": "b" * 64}, "c" * 64, None)
    assert text and "no per-file record" in text and "bbbbbbbb" in text and "cccccccc" in text


def test_a_missing_key_on_either_side_cannot_be_compared_and_is_refused():
    for ghost, current in ((GHOST, ""), ({**GHOST, "data_batch_hash": ""}, "b" * 64)):
        text = session_data_refusal(ghost, current, NOW)         # MUTATION G1c fails here
        assert text and "could not be compared" in text and "load the recipe and its data" in text, text


# -- the handler --------------------------------------------------------------------------------------------------------

def _restore(tmp_path, monkeypatch, state):
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _save(screen.manager, "steps made on the first batch")
    with reactive.isolate():
        screen.home_state.set(state)
    screen.run("_handle_session_actions")
    with reactive.isolate():
        return screen, screen.home_state.get()


def test_restore_on_other_data_is_refused_and_nothing_reaches_the_state(tmp_path, monkeypatch):
    """Before the guard this restored the steps after a warning."""
    screen, state = _restore(tmp_path, monkeypatch, {"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "c" * 64, "data_files": NOW})
    errors = screen.texts("error")
    assert len(errors) == 1 and "other data" in errors[0], screen.notes
    assert not state.get("audit_pipeline") and "t3_ghost_file" not in state, "MUTATION G1b fails here: nothing of the session is applied"
    assert screen.texts("message") == [], "no 'Session restored'"


def test_restore_on_the_same_data_applies_the_steps_without_a_data_warning(tmp_path, monkeypatch):
    """The control."""
    screen, state = _restore(tmp_path, monkeypatch, {"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64})
    assert screen.texts("warning") == [] and screen.texts("error") == []
    assert len(state["audit_pipeline"]) == 1
