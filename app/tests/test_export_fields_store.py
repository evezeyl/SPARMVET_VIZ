"""The store of the Export fields per session (D-0288, D-0291, D-0294, D-0296): pure, no browser.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_fields_store.py -q
"""
import pytest

from app.modules.export_fields_store import (
    EXPORT_FIELD_DEFAULTS, EXPORT_LABEL_DEFAULT, EXPORT_LABEL_FIELD, REMEMBERED_EXPORT_FIELDS, ExportFieldsStore,
)

A, B = "aaaaaaaaaaaa:111111111111", "bbbbbbbbbbbb:222222222222"


def _store(*keys):
    """A store that knows the given sessions, as the server does when it tells the page which session is shown."""
    store = ExportFieldsStore()
    for key in keys:
        store.begin_session(key)
    return store


def test_a_first_visit_shows_the_defaults_and_the_defaults_are_the_decided_ones():
    got = ExportFieldsStore().fields_for(A)
    assert got == EXPORT_FIELD_DEFAULTS
    assert got["export_plot_format"] == "svg", "D-0294: plot format SVG"
    assert got["export_report_format"] == "html", "D-0294: report format HTML"
    assert got["export_include_reproducibility"] is False


def test_the_fields_of_a_session_read_back_as_set():
    store = _store(A)
    store.remember(A, "export_preset", "publication")
    store.remember(A, "export_plot_width", 12)
    store.remember(A, "export_include_reproducibility", True)
    got = store.fields_for(A)
    assert (got["export_preset"], got["export_plot_width"], got["export_include_reproducibility"]) == ("publication", 12, True)
    assert got["export_plot_format"] == "svg", "a field that was not set keeps its default"


def test_two_sessions_do_not_leak_into_each_other():
    store = _store(A, B)
    store.remember(A, "export_plot_format", "png")
    assert store.fields_for(B)["export_plot_format"] == "svg", "B has not been visited: defaults"
    store.remember(B, "export_plot_format", "pdf")
    assert store.fields_for(A)["export_plot_format"] == "png" and store.fields_for(B)["export_plot_format"] == "pdf"


def test_the_label_is_never_remembered():
    store = _store(A)
    with pytest.raises(ValueError, match="never remembered"):
        store.remember(A, EXPORT_LABEL_FIELD, "my label")
    assert EXPORT_LABEL_FIELD not in store.fields_for(A) and EXPORT_LABEL_FIELD not in REMEMBERED_EXPORT_FIELDS
    assert EXPORT_LABEL_DEFAULT == ""


def test_an_unknown_field_is_refused_not_ignored():
    store = _store(A)
    with pytest.raises(ValueError):
        store.remember(A, "export_scope", "plot")           # the removed scope is not a field any more
    with pytest.raises(ValueError):
        store.begin_session("")


def test_a_value_for_a_key_the_page_did_not_show_never_lands_under_another_key():
    """The page reports the key it was showing when the user set the value (D-0050, race of two quick recipe switches: A, B, A).
    A value that names B lands under B only; a value that names an unknown or empty key is dropped and lands nowhere, and the
    caller is told (False)."""
    store = _store(A, B)
    assert store.remember(B, "export_plot_format", "pdf") is True
    assert store.fields_for(A)["export_plot_format"] == "svg", "a value reported for B never lands under A"
    assert store.fields_for(B)["export_plot_format"] == "pdf"
    assert store.remember("cccccccccccc:333333333333", "export_plot_format", "png") is False, "a key the server never issued"
    assert store.remember("", "export_plot_format", "png") is False, "the page had no session yet"
    assert store.fields_for(A)["export_plot_format"] == "svg" and store.fields_for(B)["export_plot_format"] == "pdf"
    assert store.fields_for("cccccccccccc:333333333333") == EXPORT_FIELD_DEFAULTS, "nothing was stored under the unknown key either"


def test_rapid_switches_a_b_a_leave_the_remembered_choices_as_they_were():
    """What the server does when A, B, A come within a few ms: it begins B and A in order and the page's reports carry its own
    key. A's choices, remembered before, stay; B's late report is B's."""
    store = _store(A)
    store.remember(A, "export_preset", "publication")
    store.remember(A, "export_plot_width", 9)
    store.begin_session(B)
    store.begin_session(A)
    store.remember(B, "export_plot_format", "pdf")      # the page's report for B arrives after the switch back to A
    assert store.fields_for(A)["export_preset"] == "publication" and store.fields_for(A)["export_plot_width"] == 9
    assert store.fields_for(A)["export_plot_format"] == "svg"
    assert store.fields_for(B)["export_plot_format"] == "pdf" and store.fields_for(B)["export_preset"] == "web"


def test_what_the_caller_changes_in_a_read_does_not_change_the_store():
    store = _store(A, B)
    store.remember(A, "export_preset", "publication")
    store.fields_for(A)["export_preset"] = "web"
    store.fields_for(B)["export_plot_format"] = "pdf"
    assert store.fields_for(A)["export_preset"] == "publication"
    assert store.fields_for(B)["export_plot_format"] == "svg"
    assert EXPORT_FIELD_DEFAULTS["export_plot_format"] == "svg"


def test_a_new_store_remembers_nothing_of_another_store():
    """In memory only, one store per page session: nothing is shared between stores and nothing is on disk."""
    first, second = _store(A), _store(A)
    first.remember(A, "export_preset", "publication")
    assert second.fields_for(A)["export_preset"] == "web"
