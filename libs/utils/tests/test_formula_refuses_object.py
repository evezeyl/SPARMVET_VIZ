"""`pl.Object` is refused in a formula at the check, in every spelling (D-0230, Eve 2026-11-17).

Before, `pl.col('a').str.json_decode(pl.Object)` passed the check and the calculation stopped with a Polars panic
(`PanicException: not implemented: Deserialization from JSON not implemented for FixedSizeBinary(8)`). Eve: "park it and
refuse. With a note of possibility to re evaluate if request or necessity later on." Panics are not caught.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_formula_refuses_object.py -q
"""
from utils.fix_text import split_fix
import polars as pl
import pytest

from utils.formula_check import FormulaError, evaluate_formula, formula_problems

DATA = pl.DataFrame({"a": ['{"x": 1}', '{"x": 2}'], "n": [1, 2]})

# Every way the type can be named in a formula (read from the check: all of them go through `pl.<name>`).
OBJECT_SPELLINGS = [
    "pl.col('a').str.json_decode(pl.Object)",
    "pl.col('a').str.json_decode(pl.Object())",
    "pl.col('a').str.json_decode(dtype=pl.Object)",
    "pl.col('a').str.json_decode(pl.List(pl.Object))",
    "pl.col('a').str.json_decode(pl.Struct({'x': pl.Object}))",
    "pl.col('a').str.json_decode(pl.List(pl.Struct({'x': pl.Object})))",
    "pl.col('n').cast(pl.Object)",
    "pl.col('n').cast(pl.List(pl.Object))",
    "pl.col('n').cast(pl.Array(pl.Object, 2))",
    "pl.col('n').cast(dtype=pl.Object)",
    "pl.col('n').cast([pl.Object][0])",
    "pl.lit(None, dtype=pl.Object)",
    "pl.lit(1, pl.Object)",
    "pl.col('n').fill_null(0).cast(pl.Object) + 1",
    "pl.when(pl.col('n') > 1).then(pl.col('n').cast(pl.Object)).otherwise(0)",
    "pl.sum_horizontal('n', pl.col('n').cast(pl.Object))",
]


@pytest.mark.parametrize("text", OBJECT_SPELLINGS)
def test_object_is_refused_in_every_spelling(text):
    problems = formula_problems(text)
    assert problems, f"allowed but must be refused: {text!r}"
    assert any("pl.Object" in p for p in problems), problems


@pytest.mark.parametrize("text", OBJECT_SPELLINGS)
def test_a_refused_object_formula_never_reaches_polars(text):
    """The refusal is a FormulaError from the check, so no Polars panic can happen."""
    with pytest.raises(FormulaError):
        evaluate_formula(text)


def test_the_message_says_what_why_and_a_suggestion():
    [message] = formula_problems("pl.col('a').str.json_decode(pl.Object)")
    what, fix = split_fix(message)
    assert "Fix:" not in message
    assert what.startswith("pl.Object holds any Python object")
    assert "normal table columns" in what
    assert fix.startswith("Suggestion: use a type a table can hold")


def test_each_use_of_object_is_listed_once_and_the_rest_of_the_formula_still_checked():
    problems = formula_problems("pl.col('n').cast(pl.Object) + pl.col('n').map_elements(lambda v: v)")
    assert sum("pl.Object" in p for p in problems) == 1
    assert any("map_elements" in p for p in problems)


@pytest.mark.parametrize("name", ["Object", "object", "OBJECT", "pl.Object", "Python object"])
def test_polars_does_not_read_a_dtype_written_as_text(name):
    """If a Polars upgrade starts to read text as a data type, this fails: the check would then need a text rule."""
    for call in (lambda: pl.col("n").cast(name), lambda: pl.lit(1, dtype=name), lambda: pl.col("a").str.json_decode(name),
                 lambda: pl.col("n").cast(pl.List(name))):
        try:
            schema = DATA.select(call().alias("r")).schema
        except TypeError:
            continue
        assert "Object" not in str(schema), (name, schema)


@pytest.mark.parametrize("text", [
    "pl.col('a').str.json_decode(pl.Struct({'x': pl.Int64}))",
    "pl.col('n').cast(pl.List(pl.Int64))",
    "pl.col('n').cast(pl.Float64) + 1",
    "pl.lit(None, dtype=pl.String)",
])
def test_the_other_types_are_still_allowed_and_run(text):
    assert formula_problems(text) == []
    DATA.select(evaluate_formula(text).alias("r"))


def test_the_parked_list_holds_only_object_today():
    """A new entry is a decision of Eve: this test makes a silent addition visible."""
    from utils.formula_check import REFUSED_DTYPES
    assert set(REFUSED_DTYPES) == {"Object"}
    assert all(hasattr(pl, name) for name in REFUSED_DTYPES)
