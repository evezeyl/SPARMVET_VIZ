"""The filter dialog acts on the table after the plot's audited steps (DECIDED 2026-11-15, Eve, S2-1 (a)).

A column that an earlier audit step dropped is not offered, on T3 in Audit mode only (T1 and T2 are the tables as they are), and the
values the dialog lists are the rows that are still there. The list comes from the same function as the table, the plot
and the export (`audited_frame`, through `dialog_frame`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_dialog_after_audit.py -q
"""
import polars as pl
import pytest

from app.modules.t3_audit_engine import AuditStepError, column_types, dialog_frame, value_choices

FRAME = pl.LazyFrame({"id": ["a", "b", "c", "d"], "score": [1, 2, 3, 4], "group": ["x", "x", "y", "y"]})


def drop(column):
    return {"id": f"d_{column}", "node_type": "drop_column", "params": {"column": column}, "reason": "r"}


def keep_high():
    return {"id": "f", "node_type": "filter_row", "params": {"column": "score", "op": "ge", "value": 3}, "reason": "r"}


def test_a_dropped_column_is_not_offered_in_my_view():
    assert list(column_types(dialog_frame(FRAME, [drop("score")], True))) == ["id", "group"]


def test_a_dropped_column_is_still_offered_in_t1_and_t2():
    assert list(column_types(dialog_frame(FRAME, [drop("score")], False))) == ["id", "score", "group"]


def test_the_values_listed_are_the_rows_that_are_still_there():
    lf = dialog_frame(FRAME, [keep_high()], True)
    assert list(value_choices(lf, "group")) == ["y"], "the rows with group x were filtered out by the earlier step"
    assert list(value_choices(dialog_frame(FRAME, [keep_high()], False), "group")) == ["x", "y"]


def test_without_audit_steps_the_dialog_sees_the_table_as_it_is():
    assert list(column_types(dialog_frame(FRAME, [], True))) == ["id", "score", "group"]


def test_two_drops_leave_the_rest():
    assert list(column_types(dialog_frame(FRAME, [drop("score"), drop("group")], True))) == ["id"]


def test_a_list_that_cannot_run_raises_in_my_view_and_not_elsewhere():
    broken = [drop("score"), keep_high()]
    with pytest.raises(AuditStepError, match="audit step 2 of the plot 'p'"):
        dialog_frame(FRAME, broken, True, "p")
    assert list(column_types(dialog_frame(FRAME, broken, False))) == ["id", "score", "group"]
