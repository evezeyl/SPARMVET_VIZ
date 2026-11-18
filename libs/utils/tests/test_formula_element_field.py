"""`pl.element()` and `pl.field()` in a formula (D-0231, Eve 2026-11-17).

Eve: "sometimes we might have data stored with one column that might need transformation" (a column that holds
"gene1, gene2, gene3"). `pl.element()` names the inner value of a list cell (inside `list.eval`), `pl.field(name)` a field
of a struct cell (inside `struct.with_fields`). Safety check done first (2026-11-17): `element()` takes nothing, `field`
takes a field name; both are `pl.col('')` / a field name, never a function, a file, bytes or a library path; the object
they return is an `Expr`, and the argument of `list.eval` and `struct.with_fields` is walked by the same check as any
other expression, so every refused member stays refused inside them. These tests keep it so.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_formula_element_field.py -q
"""
import inspect

import polars as pl
import pytest

from utils.formula_check import FormulaError, evaluate_formula, formula_problems

DATA = pl.DataFrame({
    "genes": [[" gene1", "gene2 ", ""], [], ["gene3"]],
    "cell": [{"x": 5, "y": 2}, {"x": 3, "y": 4}, {"x": 1, "y": 0}],
    "n": [1, 2, 3],
})


def run(text):
    return DATA.select(evaluate_formula(text).alias("r"))["r"].to_list()


# ---- allowed, and they work on data -------------------------------------------------------------------------------

def test_element_works_inside_list_eval():
    assert run("pl.col('genes').list.eval(pl.element().str.strip_chars())") == [["gene1", "gene2", ""], [], ["gene3"]]


def test_element_works_in_a_filter_and_in_a_chain_of_two_evals():
    text = "pl.col('genes').list.eval(pl.element().str.strip_chars().filter(pl.element().str.strip_chars() != ''))"
    assert formula_problems(text) == []
    assert run(text) == [["gene1", "gene2"], [], ["gene3"]]
    assert run("pl.col('genes').list.eval(pl.element().str.strip_chars()).list.eval(pl.element().str.to_uppercase())") \
        == [["GENE1", "GENE2", ""], [], ["GENE3"]]


def test_element_works_in_list_filter():
    assert run("pl.col('genes').list.filter(pl.element().str.strip_chars() != '')") == [[" gene1", "gene2 "], [], ["gene3"]]


def test_field_works_inside_struct_with_fields():
    assert run("pl.col('cell').struct.with_fields(pl.field('x') ** 2)") == [{"x": 25, "y": 2}, {"x": 9, "y": 4}, {"x": 1, "y": 0}]
    assert run("pl.col('cell').struct.with_fields(pl.field(['x', 'y']) * 10)") == [{"x": 50, "y": 20}, {"x": 30, "y": 40}, {"x": 10, "y": 0}]
    assert run("pl.col('cell').struct.with_fields((pl.field('x') + pl.col('n')).alias('x'))") == [{"x": 6, "y": 2}, {"x": 5, "y": 4}, {"x": 4, "y": 0}]


@pytest.mark.parametrize("text", [
    "pl.col('genes').list.eval(pl.element().str.strip_chars())",
    "pl.col('cell').struct.with_fields(pl.field('x'))",
    "pl.col('n').cumulative_eval(pl.element().sum())",
])
def test_the_check_accepts_them(text):
    assert formula_problems(text) == []


# ---- they name a value and nothing else ---------------------------------------------------------------------------

def test_they_take_no_function_no_file_no_bytes_no_library_path():
    assert list(inspect.signature(pl.element).parameters) == []
    assert list(inspect.signature(pl.field).parameters) == ["name"]
    assert str(inspect.signature(pl.field).parameters["name"].annotation) in ("str | list[str]", "'str | list[str]'")


@pytest.mark.parametrize("text", ["pl.element", "pl.field", "pl.element.str", "pl.field.__call__", "pl.element().__class__",
                                  "pl.element()._pyexpr", "pl.field('x').__dict__"])
def test_an_uncalled_name_or_an_underscore_member_is_refused(text):
    assert formula_problems(text), text


@pytest.mark.parametrize("text", [
    "pl.field(lambda v: v)",
    "pl.field(open('/etc/passwd'))",
    "pl.field(pl.col('n').map_elements(lambda v: v))",
    "pl.element(lambda v: v)(1)",
])
def test_an_argument_of_them_is_checked_like_any_other(text):
    assert formula_problems(text), text


def test_outside_a_list_or_struct_polars_gives_a_plain_error_not_a_panic():
    """If a Polars upgrade turns these into a panic, this fails and the check needs a rule (like pl.Object, D-0230)."""
    for text in ("pl.element()", "pl.field('x')", "pl.element() + 1"):
        with pytest.raises(pl.exceptions.InvalidOperationError):
            DATA.select(evaluate_formula(text))


# ---- hostile inner expressions: every refused member stays refused inside list.eval and struct.with_fields ----------

HOSTILE_MEMBERS = {
    "deserialize": ".deserialize('/tmp/x')",
    "from_json": ".from_json('{}')",
    "register_plugin": ".register_plugin(lib='/tmp/x.so', symbol='f')",
    "inspect": ".inspect('{0.__class__}')",
    "map_elements": ".map_elements()",
    "map_batches": ".map_batches()",
    "pipe": ".pipe()",
    "rolling_map": ".rolling_map()",
    "meta": ".meta.serialize()",
}
INNER = {"element": "pl.element()", "field": "pl.field('x')"}
WRAPPERS = {
    "list.eval": "pl.col('genes').list.eval({inner})",
    "struct.with_fields": "pl.col('cell').struct.with_fields({inner})",
    "list.filter": "pl.col('genes').list.filter({inner})",
    "cumulative_eval": "pl.col('n').cumulative_eval({inner})",
}


@pytest.mark.parametrize("member", sorted(HOSTILE_MEMBERS))
@pytest.mark.parametrize("wrapper", sorted(WRAPPERS))
@pytest.mark.parametrize("start", sorted(INNER))
def test_a_refused_member_is_refused_inside_a_list_or_struct_expression(member, wrapper, start):
    text = WRAPPERS[wrapper].format(inner=INNER[start] + HOSTILE_MEMBERS[member])
    problems = formula_problems(text)
    assert problems, f"allowed but must be refused: {text!r}"
    assert any(member in p for p in problems), (text, problems)
    with pytest.raises(FormulaError):
        evaluate_formula(text)


def test_a_hostile_member_deep_inside_a_nested_inner_expression_is_refused():
    text = "pl.col('genes').list.eval(pl.element().str.strip_chars().pipe(pl.element()) + pl.element().inspect('{}'))"
    problems = " ".join(formula_problems(text))
    assert "pipe" in problems and "inspect" in problems


def test_pl_object_stays_refused_inside_them():
    assert formula_problems("pl.col('genes').list.eval(pl.element().str.json_decode(pl.Object))")


def test_the_new_names_do_not_open_the_module_level():
    for text in ("pl.element().read_csv('x')", "pl.read_csv('x')", "pl.Expr.deserialize('x')", "pl.field('x').meta.write_json('x')"):
        assert formula_problems(text), text


def test_a_column_still_cannot_be_named_inside_list_eval_by_polars_but_the_check_is_not_the_judge():
    """Polars itself refuses a named column inside list.eval ('consider using element'): a plain error, not a panic."""
    text = "pl.col('genes').list.eval(pl.col('n'))"
    assert formula_problems(text) == []
    with pytest.raises(pl.exceptions.ComputeError):
        DATA.select(evaluate_formula(text))


# ---- FORMULA-FIELD-PLAIN-ERROR and the one-label rule (night of 2026-11-17, review findings 3 and 4) ------------------

import pytest as _pytest
from utils.formula_check import FormulaError, evaluate_formula, formula_problems, function_string_problems


@_pytest.mark.parametrize("text", ["pl.field(1)", "pl.field(pl.col('b'))", "pl.field('a', 'b')", "pl.field()", "pl.element(1)",
                                   "pl.field(['a', 1])", "pl.field(name='a')"])
def test_inner_value_calls_with_wrong_arguments_are_refused_by_the_check(text):
    assert formula_problems(text)
    with _pytest.raises(FormulaError):
        evaluate_formula(text)


@_pytest.mark.parametrize("text", ["pl.field('x')", "pl.field(['x', 'y'])", "pl.element()"])
def test_valid_inner_value_calls_still_work(text):
    assert formula_problems(text) == []
    evaluate_formula(text)


def test_a_build_error_becomes_the_formula_error_with_a_suggestion():
    with _pytest.raises(FormulaError, match="Suggestion:"):
        evaluate_formula("pl.col('a').round('x')")


def test_one_label_and_a_separator_between_problems():
    problems = function_string_problems("lambda x: np.load('a') + open('f')")
    assert problems and not any("Fix: Suggestion:" in p for p in problems)


def test_two_problems_read_as_two_sentences():
    from utils.formula_check import _sentence
    assert _sentence("a. Suggestion: x") == "a. Suggestion: x."
    assert _sentence("a.") == "a."
    with _pytest.raises(FormulaError) as error:
        evaluate_formula("pl.field(1) + pl.element(2)")
    assert "Fix: write pl.field('x') or pl.field(['x', 'y']). pl.element()" in str(error.value) or str(error.value).count("Fix:") == 2
