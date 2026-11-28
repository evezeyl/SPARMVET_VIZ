"""G1 guard (Eve 2026-11-28: audit steps never mix across data): a Restore of a session made on OTHER DATA is refused.

Nothing of the session reaches the state (no steps, no overrides, no ghost file name); one error says what the session's data were and
what the data now loaded are, and what the user can do. The rule is the pure function `session_data_refusal` (tested first, headless);
the handler is tested through the same screen harness as the other Restore tests.

THE METADATA IS DIFFERENT (Eve 2026-11-28): the table `metadata_schema` is updatable; when only it differs the Restore goes on, with one notice.

Mutation index (each seen failing):
  MUTATION G1a  `session_data_refusal` returns None for another batch hash (the old warning-only behaviour)
  MUTATION G1b  the handler ignores the refusal and goes on (the steps are applied again)
  MUTATION G1c  a missing key is taken as "same" (the careful answer is to refuse)

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_restore_on_other_data_refused.py -q
"""
from shiny import reactive

from app.modules.session_manager import session_data_refusal, session_metadata_change
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


# -- the metadata is updatable (Eve 2026-11-28) ---------------------------------------------------------------------------

META = {"path": "/data/meta_v1.tsv", "sha256": "4" * 64}
META_NEW = {"path": "/data/meta_v2.tsv", "sha256": "5" * 64}
G_META = {**GHOST, "source_files": {**GHOST["source_files"], "metadata_schema": META}}
NOW_SAME_DATA = {**{k: v for k, v in G_META["source_files"].items()}, "metadata_schema": META_NEW}


def test_only_the_metadata_differs_is_not_refused_and_the_change_is_named():
    assert session_data_refusal(G_META, "c" * 64, NOW_SAME_DATA) is None          # MUTATION G1d (treat metadata as data) fails here
    assert session_metadata_change(G_META, NOW_SAME_DATA) == ("44444444", "55555555")


def test_a_data_file_and_the_metadata_both_differ_is_refused_and_lists_the_data_only():
    now = {**NOW_SAME_DATA, "Summary": NOW["Summary"]}
    text = session_data_refusal(G_META, "c" * 64, now)
    assert text and "summary_v2.tsv" in text and "meta_v" not in text, text


def test_a_data_file_missing_now_is_refused_even_when_the_metadata_also_differs():
    now = {k: v for k, v in NOW_SAME_DATA.items() if k != "Summary"}
    assert session_data_refusal(G_META, "c" * 64, now)


def test_the_metadata_missing_now_is_a_metadata_change_not_a_refusal():
    now = {k: v for k, v in NOW_SAME_DATA.items() if k != "metadata_schema"}
    assert session_data_refusal(G_META, "c" * 64, now) is None
    assert session_metadata_change(G_META, now) == ("44444444", "no metadata file")


def test_no_metadata_change_when_the_metadata_is_the_same():
    assert session_metadata_change(G_META, G_META["source_files"]) is None


def test_without_per_file_hashes_a_different_batch_is_still_refused_even_if_only_the_metadata_changed():
    assert session_data_refusal({"data_batch_hash": "b" * 64}, "c" * 64, NOW_SAME_DATA)


def test_the_handler_restores_when_only_the_metadata_differs_and_says_so_once(tmp_path, monkeypatch):
    from app.tests.test_session_errors_visible import KEY
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    data = tmp_path / "data.tsv"; meta = tmp_path / "meta.tsv"
    data.write_text("a\n1\n"); meta.write_text("id\nx\n")
    screen.manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {"Summary": data, "metadata_schema": meta}, {})
    _save(screen.manager, "kept steps")
    import hashlib
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()   # noqa: E731
    meta.write_text("id\nx\ny\n")                                    # the metadata is completed
    now = {"Summary": {"path": str(data), "sha256": sha(data)}, "metadata_schema": {"path": str(meta), "sha256": sha(meta)}}
    with reactive.isolate():
        screen.home_state.set({"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "c" * 64, "data_files": now})
    screen.run("_handle_session_actions")
    warnings = screen.texts("warning")
    assert len(warnings) == 1 and "other metadata" in warnings[0], screen.notes
    with reactive.isolate():
        assert len(screen.home_state.get()["audit_pipeline"]) == 1, "the steps are restored"
    assert screen.texts("error") == []
