"""G10 of `.claude/design/home_guardrail_gaps.md`: a recipe formula that tries to leave the list of allowed names is refused, and nothing runs.

The twelve tries were run on 2026-11-28 (`evaluate_formula`: the check, then `eval` with no builtins and only `pl`). This pins them. MUTATION: in
`evaluate_formula`, skip the problems check (`if False and problems`): the canary try writes its file or fails with another error, and this test fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_formula_escape_tries.py -q
"""
import pytest

from utils.formula_check import FormulaError, evaluate_formula

TRIES = [
    "__import__('pathlib').Path({canary!r}).write_text('x')",
    "pl.col('a').__class__.__mro__[1].__subclasses__()",
    "pl.col('a').__init__.__globals__",
    "pl.lit(1).__reduce__()",
    "(lambda: 1)()",
    "[c for c in ().__class__.__bases__[0].__subclasses__()]",
    "pl.col('a').map_elements(lambda x: __import__('os').getcwd())",
    "pl.col('a').map_batches(open)",
    "getattr(pl, 'read_csv')('/etc/passwd')",
    "pl.read_csv('/etc/passwd')",
    "pl.col('a').pipe(print)",
    "pl.col('a').eval(pl.element().cast(pl.Int8))",
]


@pytest.mark.parametrize("text", TRIES)
def test_an_escape_try_is_refused_with_a_formula_error_and_nothing_is_written(text, tmp_path):
    canary = tmp_path / "canary"
    with pytest.raises(FormulaError):
        evaluate_formula(text.format(canary=str(canary)) if "{canary" in text else text)
    assert not canary.exists()


def test_the_control_a_plain_expression_is_allowed():
    assert type(evaluate_formula("pl.col('a').cast(pl.Int8)")).__name__ == "Expr"
