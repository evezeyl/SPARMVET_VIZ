"""The Blueprint join preview gives the same verdict as the build (JOIN-PREVIEW-STRICT-1).

The rule lives twice, in `blueprint_arch.join_designer.check_join_keys` (preview) and in
`transformer.data_assembler.DataAssembler` (build), because a domain library may not import another one.
This test is the place where both are run on the same pair of tables: the cases are those of
libs/transformer/tests/test_join_key_types.py. For each case, the preview is "not joinable" exactly when the
build raises, and the kind of problem (type, missing column, unequal lists) is the same.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_join_preview_parity.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from blueprint_arch.join_designer import check_join_keys
from transformer.data_assembler import DataAssembler
from utils.action_names import JOIN
from utils.errors import TransformationError


def _table(**cols):
    """cols: name -> polars dtype; three rows of text-like values cast to the dtype."""
    values = {"String": ["s1", "s2", "s3"], "Categorical": ["s1", "s2", "s3"], "Int64": [1, 2, 3]}
    return pl.LazyFrame({n: values[str(t)] for n, t in cols.items()}).with_columns(
        [pl.col(n).cast(t) for n, t in cols.items()])


S, C, I = pl.String, pl.Categorical, pl.Int64

# (id, left columns, right columns, left keys, right keys, expected kind)
CASES = [
    ("equal_string", {"sample_id": S}, {"sample_id": S}, ["sample_id"], ["sample_id"], None),
    ("equal_categorical", {"sample_id": C}, {"sample_id": C}, ["sample_id"], ["sample_id"], None),
    ("equal_int", {"sample_id": I}, {"sample_id": I}, ["sample_id"], ["sample_id"], None),
    ("string_vs_categorical", {"sample_id": S}, {"sample_id": C}, ["sample_id"], ["sample_id"], "type"),
    ("categorical_vs_string", {"sample_id": C}, {"sample_id": S}, ["sample_id"], ["sample_id"], "type"),
    ("number_vs_text", {"sample_id": I}, {"sample_id": S}, ["sample_id"], ["sample_id"], "type"),
    ("left_on_right_on_types", {"a": S}, {"b": C}, ["a"], ["b"], "type"),
    ("left_on_right_on_equal", {"a": S}, {"b": S}, ["a"], ["b"], None),
    ("two_keys_one_differs", {"x": S, "y": C}, {"x": S, "y": S}, ["x", "y"], ["x", "y"], "type"),
    ("two_keys_equal", {"x": S, "y": I}, {"x": S, "y": I}, ["x", "y"], ["x", "y"], None),
    ("missing_left", {"sample_id": S}, {"other": S}, ["no_such"], ["other"], "missing"),
    ("missing_right", {"sample_id": S}, {"sample_id": S}, ["sample_id"], ["no_such"], "missing"),
    ("missing_both", {"sample_id": S}, {"sample_id": S}, ["no_such"], ["no_such"], "missing"),
    ("unequal_lists", {"a": S, "b": S}, {"a": S}, ["a", "b"], ["a"], "length"),
]


def _schema(columns):
    return {name: str(dtype) for name, dtype in columns.items()}


def _build_step(left_keys, right_keys):
    if left_keys == right_keys:
        return {"action": JOIN, "right_ingredient": "R", "how": "left", "maintain_order": "left_right", "on": left_keys}
    return {"action": JOIN, "right_ingredient": "R", "how": "left", "maintain_order": "left_right", "left_on": left_keys, "right_on": right_keys}


def _build_fails(left_cols, right_cols, left_keys, right_keys):
    assembler = DataAssembler({"L": _table(**left_cols), "R": _table(**right_cols)}, recipe_id="demo", join_id="J")
    try:
        assembler.assemble([_build_step(left_keys, right_keys)]).collect()
    except TransformationError:
        return True
    return False


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_the_preview_verdict_equals_the_build_verdict(case):
    _, left_cols, right_cols, left_keys, right_keys, kind = case
    preview = check_join_keys(_schema(left_cols), _schema(right_cols), left_keys, right_keys, right_id="R")
    assert preview["kind"] == kind
    assert preview["ok"] is (not _build_fails(left_cols, right_cols, left_keys, right_keys))
