"""The formula check: a recipe formula may build a Polars expression and nothing else (spec section 15, check ST06).

A recipe from outside (a bundle, an upload) must not run code with the app's rights. The check reads a formula as
syntax, never runs it; `evaluate_formula` then runs it with empty builtins as a second layer.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_formula_check.py -q
"""
import re
from pathlib import Path

import polars as pl
import pytest

from utils.formula_check import (
    FormulaError,
    MATH_FUNCTIONS,
    denied_methods,
    evaluate_formula,
    formula_problems,
    function_string_problems,
)

REPO = Path(__file__).resolve().parents[3]

ALLOWED = [
    "pl.col('x') * 2",
    "pl.col('x') + 1",
    "pl.lit(0.5)",
    "pl.col('year').cast(pl.Int64).cast(pl.String)",
    "pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowercase()",
    "pl.col('predicted_phenotype_clean').n_unique().over('sample_id') > 1",
    "pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl.lit('No'))",
    "pl.when(pl.col('year') < 2024).then(pl.lit('Early')).otherwise(pl.lit('Recent'))",
    "pl.col('a').is_in(['x', 'y'])",
    "pl.col('a').str.replace_all('_', '-')",
    "pl.col('a').list.len()",
    "pl.col('a').dt.year()",
    "pl.col('a').fill_null(0).round(2)",
    "(pl.col('a') + pl.col('b')) / 2",
    "-pl.col('a')",
    "pl.col('a') > 1",
    "pl.col('a').cast(pl.Enum(['low', 'high']))",
    "pl.sum_horizontal('a', 'b')",
]

ATTACKS = [
    "__import__('os').system('echo hacked')",
    "__import__('os')",
    "().__class__.__bases__[0].__subclasses__()",
    "pl.col('a').__class__",
    "pl.__builtins__",
    "(lambda: 1)()",
    "lambda x: x",
    "[x for x in range(3)]",
    "getattr(pl, 'read_csv')('/etc/passwd')",
    "eval('1+1')",
    "exec('x = 1')",
    "open('/etc/passwd').read()",
    "pl.read_csv('/etc/passwd')",
    "pl.scan_parquet('/tmp/x.parquet')",
    "pl.read_parquet('/tmp/x.parquet')",
    "pl.from_dict({'a': [1]})",
    "pl.Config.set_tbl_rows(1)",
    "pl.col('a').map_elements(lambda v: v)",
    "pl.col('a').map_elements(str)",
    "pl.col('a').map_batches(print)",
    "pl.col('a').pipe(print)",
    "pl.col('a').rolling_map(print, window_size=2)",
    "pl.col('a').meta.serialize()",
    "pl.col('a').list.to_struct(fields=print)",
    "pl.col('a').name.map(str)",
    "pl.col('a').write_csv('/tmp/x')",
    "pl.col('a')._pyexpr",
    "pl.col('a').str.__class__",
    "'{0.__class__}'.format(pl)",
    "f'{pl.__name__}'",
    "pl",
    "os.system('x')",
    "pl.col('a') if os else 1",
    "x := 1",
    "import os",
    "pl.col('a'); 1",
    "pl.col(*['a'], **{'__x': 1})",
    "'a' * 10 ** 9",
    "[0] * 10 ** 9",
    "9 ** 9 ** 9",
    "1 << 10 ** 9",
    "pl.col('a') ** 10 ** 9",
    "",
    "   ",
    "pl.col('a'",
]


@pytest.mark.parametrize("text", ALLOWED)
def test_a_polars_expression_is_allowed_and_runs(text):
    assert formula_problems(text) == []
    expr = evaluate_formula(text)
    assert isinstance(expr, (pl.Expr, pl.Series, int, float)) or expr is not None


@pytest.mark.parametrize("text", ATTACKS)
def test_an_attack_is_refused(text):
    assert formula_problems(text), f"allowed but must be refused: {text!r}"


@pytest.mark.parametrize("text", ATTACKS)
def test_an_attack_never_runs(text):
    """The run path refuses before it evaluates: nothing in `text` is executed."""
    with pytest.raises(FormulaError):
        evaluate_formula(text)


def test_the_second_layer_has_no_builtins():
    """Even if the syntax check were bypassed, the evaluation namespace holds only `pl`."""
    from utils import formula_check
    assert formula_check.EVAL_GLOBALS["__builtins__"] == {}
    assert set(formula_check.EVAL_GLOBALS) == {"__builtins__", "pl"}


def test_a_refused_formula_says_what_is_wrong_and_the_fix():
    problems = formula_problems("__import__('os')")
    assert problems and "Fix:" in problems[0]


def test_a_formula_that_is_too_long_or_too_deep_is_refused():
    assert formula_problems("pl.col('a')" + " + pl.col('a')" * 5000)
    assert formula_problems("(" * 400 + "1" + ")" * 400)


def test_the_deny_set_is_read_from_the_installed_polars():
    """Every Expr method with a Callable parameter is denied, found by reading the signatures, not by a list."""
    denied = denied_methods()
    assert {"map_batches", "map_elements", "pipe", "rolling_map"} <= denied["expr"]
    assert "to_struct" in denied["list"]
    assert {"map", "map_fields"} <= denied["name"]


def test_every_formula_in_the_shipped_recipes_is_allowed():
    """The allow-list must keep the shipped recipes working: every `expression:` of config, assets and the libs' tests."""
    found = []
    for root in ("config", "assets", "libs"):
        for path in (REPO / root).rglob("*.yaml"):
            if ".venv" in path.parts or "outdated" in path.parts:
                continue
            for line in path.read_text(errors="ignore").splitlines():
                match = re.match(r"\s*(?:- )?expression:\s*(.+)$", line)
                if match:
                    text = match.group(1).strip().strip("'\"")
                    found.append((str(path.relative_to(REPO)), text))
    assert found, "no shipped formula found: the search is broken"
    refused = [(p, t, formula_problems(t)) for p, t in found if formula_problems(t)]
    assert not refused, refused


# ---- the function string of stat_function -------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "lambda x: x * 2",
    "lambda x: 2 * x ** 2 + 1",
    "lambda x: sin(x)",
    "lambda t: exp(-t) / (1 + exp(-t))",
    "lambda x: np.sqrt(x) + math.pi",
    "sin",
])
def test_a_function_string_over_numbers_is_allowed(text):
    assert function_string_problems(text) == []


@pytest.mark.parametrize("text", [
    "lambda x: __import__('os')",
    "lambda x: x.__class__",
    "lambda x, y: x",
    "lambda: 1",
    "lambda x: open('/etc/passwd')",
    "lambda x: getattr(x, 'real')",
    "lambda x: [i for i in x]",
    "lambda x: np.load('/etc/passwd')",
    "lambda x: np.ones(10 ** 12)",
    "lambda x: x if True else 1",
    "lambda x: 9 ** 9 ** 9",
    "lambda x: x ** 1000000",
    "os.system",
    "__import__",
    "print",
    "dnorm; 1",
    "",
])
def test_a_function_string_that_does_more_is_refused(text):
    assert function_string_problems(text), f"allowed but must be refused: {text!r}"


def test_the_math_functions_are_a_short_list_of_pure_functions():
    assert {"sin", "cos", "exp", "log", "sqrt"} <= set(MATH_FUNCTIONS)
    assert not {"load", "save", "fromfile", "ones", "zeros", "empty", "arange", "frompyfunc", "vectorize"} & set(MATH_FUNCTIONS)
