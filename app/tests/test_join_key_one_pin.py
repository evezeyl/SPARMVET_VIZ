"""The three callers of the join-key rule say what they said before the rule became one function (JOIN-KEY-ONE-1).

The build (DataAssembler._check_join_key_types), the Blueprint preview (check_join_keys) and the checker
(join_key_problems, codes J09, J10, J11) are run on the same table of cases: every pair of key types, one and several
keys, `on` and `left_on` / `right_on`, a key missing on one side, a self-join. What each one says (kind, text, fix) is
compared with the snapshot `app/tests/golden/join_key_one_pin.json`, written before the refactor from the old code.
Where the three answered differently, the snapshot keeps each answer: those cases are listed in DISAGREEMENTS.

Regenerate the snapshot (only on purpose): JOIN_KEY_PIN_WRITE=1 PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_join_key_one_pin.py -q
Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_join_key_one_pin.py -q
"""
import copy
import itertools
import json
import os
from pathlib import Path

import polars as pl
import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from blueprint_arch.join_designer import check_join_keys
from transformer.data_assembler import DataAssembler
from utils.action_names import JOIN
from utils.errors import TransformationError
from utils.polars_types import dtype_with_parameters
from utils.recipe_check import check_recipe

SNAPSHOT = Path(__file__).parent / "golden" / "join_key_one_pin.json"

TYPES = {
    "String": {"type": "String"}, "Categorical": {"type": "Categorical"},
    "Enum_a": {"type": "Enum", "categories": ["a"]}, "Enum_ab": {"type": "Enum", "categories": ["a", "b"]},
    "Int8": {"type": "Int8"}, "Int16": {"type": "Int16"}, "Int32": {"type": "Int32"}, "Int64": {"type": "Int64"},
    "UInt32": {"type": "UInt32"}, "UInt64": {"type": "UInt64"}, "Float32": {"type": "Float32"}, "Float64": {"type": "Float64"},
    "Boolean": {"type": "Boolean"}, "Date": {"type": "Date"},
    "Datetime_us": {"type": "Datetime", "time_unit": "us"}, "Datetime_ms": {"type": "Datetime", "time_unit": "ms"},
}


def _dtype(name):
    return dtype_with_parameters(TYPES[name]["type"], TYPES[name])


def _cases():
    cases = []
    for left, right in itertools.product(TYPES, TYPES):
        cases.append((f"types_{left}__{right}", {"id": left}, {"id": right}, ["id"], ["id"], "on"))
    S, I, C = "String", "Int64", "Categorical"
    cases += [
        ("left_right_equal", {"a": S}, {"b": S}, ["a"], ["b"], "lr"),
        ("left_right_differ", {"a": S}, {"b": C}, ["a"], ["b"], "lr"),
        ("two_keys_equal_on", {"x": S, "y": I}, {"x": S, "y": I}, ["x", "y"], ["x", "y"], "on"),
        ("two_keys_one_differs_on", {"x": S, "y": C}, {"x": S, "y": S}, ["x", "y"], ["x", "y"], "on"),
        ("two_keys_both_differ_lr", {"a": S, "b": I}, {"c": C, "d": S}, ["a", "b"], ["c", "d"], "lr"),
        ("mixed_widths_two_keys", {"x": "Int32", "y": "Int64"}, {"x": "Int64", "y": "Int64"}, ["x", "y"], ["x", "y"], "on"),
        ("missing_left", {"a": S}, {"o": S}, ["no_such"], ["o"], "lr"),
        ("missing_right", {"id": S}, {"id": S}, ["id"], ["no_such"], "lr"),
        ("missing_both_on", {"id": S}, {"id": S}, ["no_such"], ["no_such"], "on"),
        ("missing_two_keys", {"a": S}, {"a": S}, ["x", "y"], ["x", "y"], "on"),
        ("missing_left_and_types_differ", {"id": S, "k": S}, {"id": C, "k": S}, ["id", "no_such"], ["id", "k"], "lr"),
        ("unequal_lists", {"a": S, "b": S}, {"a": S}, ["a", "b"], ["a"], "lr"),
        ("unequal_lists_other_way", {"a": S}, {"a": S, "b": S}, ["a"], ["a", "b"], "lr"),
        ("empty_lists", {"a": S}, {"a": S}, [], [], "lr"),
        ("self_join_equal", {"id": S}, {"id": S}, ["id"], ["id"], "self"),
        ("self_join_lr_equal", {"id": S, "parent": S}, {"id": S, "parent": S}, ["id"], ["parent"], "self_lr"),
        ("self_join_lr_differ", {"id": S, "parent": I}, {"id": S, "parent": I}, ["id"], ["parent"], "self_lr"),
    ]
    return cases


CASES = _cases()


def _assembler_says(left_cols, right_cols, left_keys, right_keys, form):
    left = pl.LazyFrame(schema={n: _dtype(t) for n, t in left_cols.items()})
    right = pl.LazyFrame(schema={n: _dtype(t) for n, t in right_cols.items()})
    step = {"action": JOIN, "right_ingredient": "B", "how": "left"}
    if form == "on":
        step["on"] = left_keys if len(left_keys) != 1 else left_keys[0]
    else:
        step["left_on"], step["right_on"] = left_keys, right_keys
    assembler = DataAssembler({"A": left, "B": right}, recipe_id="r", join_id="AB")
    try:
        assembler._check_join_key_types(step, 1, left, right)
    except TransformationError as exc:
        return {"refused": True, "problem": str(exc), "fix": exc.tip}
    return {"refused": False}


def _preview_says(left_cols, right_cols, left_keys, right_keys):
    v = check_join_keys({n: str(_dtype(t)) for n, t in left_cols.items()}, {n: str(_dtype(t)) for n, t in right_cols.items()},
                        left_keys, right_keys, right_id="B")
    return {"refused": not v["ok"], "kind": v["kind"], "problem": v["problem"], "fix": v["fix"]}


def _checker_says(left_cols, right_cols, left_keys, right_keys, form, self_join):
    right_id = "A" if self_join else "B"

    def fields(cols):
        return {n: dict(TYPES[t]) for n, t in cols.items()}

    def schema(label, cols):
        return {"ui_label": label, "description": "One row per sample.", "source": {"type": "local_tsv", "path": f"assets/test_data/{label.lower()}.tsv"},
                "null_values": [], "strip": True, "input_fields": fields(cols), "tier1": {"steps": []}}

    step = {"action": "polars_join", "right_ingredient": right_id, "how": "left"}
    if form == "on":
        step["on"] = left_keys if len(left_keys) != 1 else left_keys[0]
    else:
        step["left_on"], step["right_on"] = left_keys, right_keys
    schemas = {"A": schema("A", left_cols)}
    ingredients = [{"dataset_id": "A"}]
    if not self_join:
        schemas["B"] = schema("B", right_cols)
        ingredients.append({"dataset_id": "B"})
    raw = {"id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine",
           "info": {"ui_label": "R", "description": "What it answers", "contact": "me"},
           "data_schemas": schemas,
           "joins": {"AB": {"ui_label": "AB", "description": "d", "ingredients": ingredients, "tier1": {"steps": [step]}, "labels": {}}},
           "analysis_groups": {"g": {"ui_label": "G", "description": "Q.", "plots": {"p": {"ui_label": "P", "description": "D.",
               "target_dataset": "AB", "mapping": {"x": "id"}, "layers": [{"name": "geom_col"}]}}}}}
    problems = check_recipe(raw, "run").problems
    return [{"code": p.code, "message": p.message, "fix": p.fix} for p in problems if p.code in {"J09", "J10", "J11"}]


def _answers():
    out = {}
    for name, left_cols, right_cols, left_keys, right_keys, form in CASES:
        self_join = form in ("self", "self_lr")
        form_kind = "on" if form in ("on", "self") else "lr"
        if self_join:
            right_cols = left_cols
        out[name] = {
            "build": _assembler_says(left_cols, right_cols, left_keys, right_keys, form_kind),
            "preview": _preview_says(left_cols, right_cols, left_keys, right_keys),
            "checker": _checker_says(left_cols, right_cols, left_keys, right_keys, form_kind, self_join),
        }
    return out


# case name -> what the three said differently before JOIN-KEY-ONE-1 (from the snapshot run on the old code). Marked for Eve.
# The preview refuses two empty lists of keys (kind "length": a pick of no column is no join); the build and the checker accept them
# (a join without key columns, such as a cross join, has none). Each caller keeps its answer: the rule has the parameter `empty_is_problem`.
DISAGREEMENTS = {"empty_lists": "preview refuses (length); build and checker accept"}


def test_the_three_callers_say_what_they_said_before():
    answers = _answers()
    if os.environ.get("JOIN_KEY_PIN_WRITE"):
        SNAPSHOT.parent.mkdir(exist_ok=True)
        SNAPSHOT.write_text(json.dumps(answers, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert set(answers) == set(expected)
    wrong = [name for name in expected if json.loads(json.dumps(answers[name])) != expected[name]]
    assert wrong == []


def _verdict(entry):
    """What the three say about the case, reduced to refused / accepted and the kind of problem."""
    build = entry["build"]["refused"]
    preview = entry["preview"]["refused"]
    checker = bool(entry["checker"])
    return build, preview, checker


def test_which_cases_the_three_callers_disagree_on_is_recorded():
    expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    disagree = sorted(name for name, entry in expected.items() if len(set(_verdict(entry))) > 1)
    assert disagree == sorted(DISAGREEMENTS)


# -- the three callers pass through the one function (a change of it changes all three)

@pytest.mark.parametrize("name", ["empty_lists", "types_String__Int64"])
def test_a_change_of_the_one_rule_changes_all_three_callers(name, monkeypatch):
    import utils.join_keys as one_rule
    case = next(c for c in CASES if c[0] == name)
    _, left_cols, right_cols, left_keys, right_keys, form = case
    before = {"build": _assembler_says(left_cols, right_cols, left_keys, right_keys, "lr"),
              "preview": _preview_says(left_cols, right_cols, left_keys, right_keys),
              "checker": _checker_says(left_cols, right_cols, left_keys, right_keys, "lr", False)}
    # the rule is made to find nothing: every caller must now accept the join
    monkeypatch.setattr(one_rule, "join_key_problem", lambda *a, **k: None)
    monkeypatch.setattr(one_rule, "key_length_problem", lambda *a, **k: None)
    after = {"build": _assembler_says(left_cols, right_cols, left_keys, right_keys, "lr"),
             "preview": _preview_says(left_cols, right_cols, left_keys, right_keys),
             "checker": _checker_says(left_cols, right_cols, left_keys, right_keys, "lr", False)}
    assert after["build"] == {"refused": False} and after["preview"]["refused"] is False and after["checker"] == []
    if name == "types_String__Int64":
        assert before["build"]["refused"] and before["preview"]["refused"] and before["checker"]
