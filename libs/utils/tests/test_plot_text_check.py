"""A text written in a plot of a recipe must not be able to run code (PLOT-TEXT-RUNS-CODE-1; spec section 15, check PS06).

plotnine hands the `formula` of a smoother to patsy, which runs it as Python, and evaluates a facet variable that is
not a column as an expression. A recipe that comes from outside must not run code with the app's rights.
The check reads the text as syntax and never runs it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_plot_text_check.py -q
"""
import pytest

from utils.formula_check import smoother_formula_problems
from utils.plot_text_check import STAT_FUNCTION_TEXT_BLOCKED, STAT_FUNCTION_TEXT_SUGGESTION, layer_text_problems

CODE = "__import__('os').system('echo hacked')"

# what a scientist writes for a smoother; each was run through plotnine (see the evidence file)
ALLOWED_FORMULAS = [
    "y ~ x",
    "y ~ x + I(x**2)",
    "y ~ x + I(x**2) + I(x**3)",
    "y ~ x - 1",
    "y ~ 0 + x",
    "y ~ 1 + x",
    "y ~ x ** 2",
    "y ~ I(x ** 2)",
    "y ~ I(x**0.5)",
    "y ~ I(1/x)",
    "y ~ I(x > 5)",
    "y ~ (x + 1)",
    "y ~ bs(x, df=4)",
    "y ~ cr(x, df=4)",
    "y ~ center(x)",
    "y ~ standardize(x)",
    "y ~ scale(x)",
    "y ~ np.log(x)",
    "y ~ log(x)",
    "np.log(y) ~ np.log(x)",
    "y ~ I(np.sqrt(x))",
    "y ~ np.exp(x / 10)",
    "y ~ math.sqrt(x)",
    "y ~ numpy.log10(x + 1)",
    "y ~ bs(np.log(x), df=3, degree=2)",
    "y ~ x + I(x * pi)",
]

ATTACKS = [
    "y ~ I(__import__('os').system('echo hacked'))",
    "y ~ " + CODE,
    "y ~ I(len(__import__('pathlib').Path('/tmp/x').write_text('x')) * 0 + x)",
    "y ~ I(().__class__.__bases__[0].__subclasses__())",
    "y ~ I(x.__class__)",
    "y ~ I(open('/etc/passwd').read())",
    "y ~ I(eval('1+1'))",
    "y ~ I(getattr(x, 'real'))",
    "y ~ I(getattr(x))",
    "y ~ I(eval(x))",
    "y ~ I(exec(x))",
    "y ~ I(compile(x))",
    "y ~ I(open(x))",
    "y ~ I(__import__(x))",
    "y ~ I(print(x))",
    "y ~ I(len(x))",
    "y ~ I(sum(x))",
    "y ~ I(max(x))",
    "y ~ I(type(x))",
    "y ~ I(vars(x))",
    "y ~ I(globals())",
    "y ~ I(locals())",
    "y ~ I(dir(x))",
    "y ~ I(input())",
    "y ~ I(breakpoint())",
    "y ~ np.load(x)",
    "y ~ np.fromfile(x)",
    "y ~ np.savetxt(x)",
    "y ~ numpy.lib.npyio.save(x)",
    "y ~ pd.read_csv(x)",
    "y ~ patsy.dmatrix(x)",
    "y ~ os.system(x)",
    "y ~ math.__class__(x)",
    "y ~ np.load('/etc/passwd')",
    "y ~ np.os.system('echo hacked')",
    "y ~ np.log.__call__(x)",
    "y ~ I((lambda: 1)())",
    "y ~ I([i for i in range(3)])",
    "y ~ I(x[0])",
    "y ~ I(x if x else 1)",
    "y ~ I('a' * 10)",
    "y ~ I(x ** 1000000)",
    "y ~ I(9 ** 9 ** 9)",
    "y ~ I(x ** x)",
    "y ~ g",
    "y ~ df",
    "y ~ self",
    "y ~ C(x, Treatment)",
    "y ~ bs(x, df=len('abc'))",
    "y ~ bs(x, knots=[1, 2])",
    "y ~ bs(x, **{'df': 3})",
    "y ~ bs(*[x])",
    "y ~ log.__class__",
    "y ~ x; import os",
    "y ~ x\nimport os",
    "~ x",
    "x",
    "y ~ x ~ x",
    "y ~",
    "~",
    "",
    "   ",
    "y ~ x + " * 300 + "x",
    "y ~ " + "(" * 200 + "x" + ")" * 200,
]


@pytest.mark.parametrize("text", ALLOWED_FORMULAS)
def test_a_formula_a_scientist_writes_is_allowed(text):
    assert smoother_formula_problems(text) == []


@pytest.mark.parametrize("text", ATTACKS)
def test_a_formula_that_could_run_code_or_is_not_a_model_formula_is_refused(text):
    problems = smoother_formula_problems(text)
    assert problems, text
    assert all("Suggestion:" in p for p in problems)


def test_a_non_text_formula_is_refused():
    for value in (None, 3, ["y ~ x"], {"a": 1}):
        assert smoother_formula_problems(value)


def test_the_message_names_the_offending_part():
    problems = smoother_formula_problems("y ~ I(getattr(x, 'real'))")
    assert any("getattr" in p for p in problems)
    problems = smoother_formula_problems("y ~ g")
    assert any("'g'" in p and "x" in p and "y" in p for p in problems)


# ---- the layer level: which parameters of which component are texts that something evaluates ----------------------

def parameters_with_problems(component, params, columns=None):
    return [p for p, _what, _suggestion in layer_text_problems(component, params, columns)]


@pytest.mark.parametrize("component", ["geom_smooth", "stat_smooth", "geom_quantile", "stat_quantile"])
def test_a_formula_parameter_is_checked_on_every_component(component):
    assert parameters_with_problems(component, {"formula": "y ~ I(" + CODE + ")"}) == ["formula"]
    assert parameters_with_problems(component, {"formula": "y ~ x + I(x**2)"}) == []
    assert parameters_with_problems(component, {"method": "lm"}) == []


@pytest.mark.parametrize("params", [
    {"facets": "~ metric"},
    {"facets": "col_group"},
    {"facets": ["a", "b"]},
    {"facets": "row_group ~ col_group"},
    {"facets": "a + b ~ c"},
    {"facets": ". ~ b"},
    {"rows": "Year", "cols": "Country"},
    {"rows": ["Year", "Source"], "cols": "Country"},
    {"facets": "Collection year"},
    {"facets": "a-b"},
    {"facets": "a.b"},
    {"rows": "a", "cols": None},
    {"rows": [], "cols": "b"},
])
@pytest.mark.parametrize("component", ["facet_wrap", "facet_grid", "facet_rows", "facet_cols"])
def test_plain_column_names_are_allowed_as_facet_variables(component, params):
    assert parameters_with_problems(component, params) == []


@pytest.mark.parametrize("params", [
    {"facets": CODE},
    {"facets": "len(" + CODE + ")"},
    {"facets": "~ " + CODE},
    {"facets": [CODE]},
    {"facets": ["a", CODE]},
    {"facets": "a ~ " + CODE},
    {"facets": "f(a + b)"},
    {"rows": CODE},
    {"cols": CODE},
    {"rows": ["a", CODE]},
    {"facets": "I(a > 3)"},
    {"facets": "a[0]"},
    {"facets": "'a'"},
    {"facets": 3},
])
@pytest.mark.parametrize("component", ["facet_wrap", "facet_grid", "facet_rows", "facet_cols"])
def test_a_facet_variable_that_is_not_a_plain_name_is_refused(component, params):
    assert parameters_with_problems(component, params), params


def test_with_the_columns_known_a_facet_variable_must_be_a_column():
    columns = ["country", "year", "Sample (n)"]
    assert parameters_with_problems("facet_wrap", {"facets": "country"}, columns) == []
    assert parameters_with_problems("facet_wrap", {"facets": "~ country + year"}, columns) == []
    assert parameters_with_problems("facet_grid", {"facets": "country ~ year"}, columns) == []
    assert parameters_with_problems("facet_wrap", {"facets": "Sample (n)"}, columns) == []   # a real column, any characters
    assert parameters_with_problems("facet_wrap", {"facets": "continent"}, columns) == ["facets"]
    assert parameters_with_problems("facet_wrap", {"facets": "country + year"}, ["country + year"]) == []  # the whole text is a column


def test_the_message_for_a_facet_names_the_part_and_lists_the_columns():
    [(param, what, suggestion)] = layer_text_problems("facet_wrap", {"facets": "continent"}, ["country", "year"])
    assert param == "facets" and "'continent'" in what
    assert suggestion.startswith("Suggestion:") and "country" in suggestion


@pytest.mark.parametrize("fun", ["lambda x: x ** 2", "sin", "__import__('os').getcwd()", "", "lambda x: 2 * x"])
def test_any_function_text_of_stat_function_is_refused_with_the_one_message(fun):
    assert parameters_with_problems("stat_function", {"fun": fun}) == ["fun"]
    [(param, what, suggestion)] = layer_text_problems("stat_function", {"fun": fun})
    assert what == STAT_FUNCTION_TEXT_BLOCKED and suggestion == STAT_FUNCTION_TEXT_SUGGESTION
    assert "blocked for now" in what and suggestion.startswith("Suggestion: compute the values in a step")


def test_a_stat_function_without_a_text_is_not_judged_here():
    assert parameters_with_problems("stat_function", {"n": 50}) == []
    assert parameters_with_problems("stat_function", {"fun": abs}) == []


def test_other_parameters_are_not_judged_here():
    assert layer_text_problems("geom_point", {"color": CODE, "size": 3}) == []
    assert layer_text_problems("scale_x_continuous", {"trans": CODE}) == []   # plotnine refuses it, nothing evaluates it
    assert layer_text_problems("geom_smooth", None) == []
