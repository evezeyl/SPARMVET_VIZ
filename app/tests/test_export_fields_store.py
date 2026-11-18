"""The store of the Export fields per session (D-0288, D-0291, D-0294, D-0296): pure, no browser.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_fields_store.py -q
"""
import pytest

from app.modules.export_fields_store import (
    EXPORT_FIELD_DEFAULTS, EXPORT_LABEL_DEFAULT, EXPORT_LABEL_FIELD, REMEMBERED_EXPORT_FIELDS, ExportFieldsStore,
)

A, B = "aaaaaaaaaaaa:111111111111", "bbbbbbbbbbbb:222222222222"


def test_a_first_visit_shows_the_defaults_and_the_defaults_are_the_decided_ones():
    got = ExportFieldsStore().fields_for(A)
    assert got == EXPORT_FIELD_DEFAULTS
    assert got["export_plot_format"] == "svg", "D-0294: plot format SVG"
    assert got["export_report_format"] == "html", "D-0294: report format HTML"
    assert got["export_include_reproducibility"] is False


def test_the_fields_of_a_session_read_back_as_set():
    store = ExportFieldsStore()
    store.set_field(A, "export_preset", "publication")
    store.set_field(A, "export_plot_width", 12)
    store.set_field(A, "export_include_reproducibility", True)
    got = store.fields_for(A)
    assert (got["export_preset"], got["export_plot_width"], got["export_include_reproducibility"]) == ("publication", 12, True)
    assert got["export_plot_format"] == "svg", "a field that was not set keeps its default"


def test_two_sessions_do_not_leak_into_each_other():
    store = ExportFieldsStore()
    store.set_field(A, "export_plot_format", "png")
    assert store.fields_for(B)["export_plot_format"] == "svg", "B has not been visited: defaults"
    store.set_field(B, "export_plot_format", "pdf")
    assert store.fields_for(A)["export_plot_format"] == "png" and store.fields_for(B)["export_plot_format"] == "pdf"


def test_the_label_is_never_remembered():
    store = ExportFieldsStore()
    with pytest.raises(ValueError, match="never remembered"):
        store.set_field(A, EXPORT_LABEL_FIELD, "my label")
    assert EXPORT_LABEL_FIELD not in store.fields_for(A) and EXPORT_LABEL_FIELD not in REMEMBERED_EXPORT_FIELDS
    assert EXPORT_LABEL_DEFAULT == ""


def test_an_unknown_field_and_a_missing_key_are_refused_not_ignored():
    store = ExportFieldsStore()
    with pytest.raises(ValueError):
        store.set_field(A, "export_scope", "plot")           # the removed scope is not a field any more
    with pytest.raises(ValueError):
        store.set_field("", "export_preset", "web")


def test_what_the_caller_changes_in_a_read_does_not_change_the_store():
    store = ExportFieldsStore()
    store.set_field(A, "export_preset", "publication")
    store.fields_for(A)["export_preset"] = "web"
    store.fields_for(B)["export_plot_format"] = "pdf"
    assert store.fields_for(A)["export_preset"] == "publication"
    assert store.fields_for(B)["export_plot_format"] == "svg"
    assert EXPORT_FIELD_DEFAULTS["export_plot_format"] == "svg"


def test_a_new_store_remembers_nothing_of_another_store():
    """In memory only, one store per page session: nothing is shared between stores and nothing is on disk."""
    first, second = ExportFieldsStore(), ExportFieldsStore()
    first.set_field(A, "export_preset", "publication")
    assert second.fields_for(A)["export_preset"] == "web"
