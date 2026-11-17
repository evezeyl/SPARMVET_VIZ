"""A recipe formula builds an expression from the recipe's own text; it never reads a file or serialised data (D-0030, D-0050).

Found by a security review (2026-11-17): the allowed members were "every public Expr method except the ones that take a
Callable". Two members slipped through, `Expr.deserialize` (reads any file path) and `Expr.from_json` (inline JSON), and
the Polars documentation says that deserialising can execute arbitrary code. `Expr.register_plugin` (loads a native
library from a path) was open too. The rule now is structural: a member is allowed by what it is.

Every input here is harmless: the only file is a plain expression written by the test, never a payload with a function.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_formula_reads_no_outside_data.py -q
"""
import inspect
import re

import polars as pl
import pytest

from utils import formula_check
from utils.formula_check import FormulaError, evaluate_formula, formula_problems

JSON_EXPRESSION = pl.col("a").meta.serialize(format="json")  # a plain expression: no Python function inside


@pytest.fixture
def expression_file(tmp_path):
    path = tmp_path / "plain_expression.json"
    path.write_text(JSON_EXPRESSION)
    return path


SPELLINGS = [
    "pl.col('b').deserialize({path!r}, format='json')",
    "pl.col('b').deserialize(source={path!r}, format='json')",
    "pl.col('b').deserialize({path!r})",
    "pl.lit(1).deserialize({path!r})",
    "pl.all().deserialize({path!r})",
    "pl.len().deserialize({path!r})",
    "(pl.col('b') + 1).deserialize({path!r})",
    "pl.col('b').cast(pl.Int64).fill_null(0).deserialize({path!r})",
    "pl.when(pl.col('b')).then(1).otherwise(0).deserialize({path!r})",
    "pl.when(pl.col('b')).then(1).deserialize({path!r})",
    "pl.col('b')[0].deserialize({path!r})",
    "pl.col('b').over('c').deserialize({path!r})",
    "pl.col('b').deserialize({path!r}) + 1",
    "pl.col('b').fill_null(pl.col('b').deserialize({path!r}))",
    "pl.sum_horizontal('a', pl.col('b').deserialize({path!r}))",
    "pl.col('b').from_json({json!r})",
    "pl.col('b').from_json(value={json!r})",
    "pl.lit(1).from_json({json!r})",
    "(pl.col('b') * 2).from_json({json!r})",
    "pl.col('b').str.strip_chars().from_json({json!r})",
    "pl.col('b').register_plugin(lib={path!r}, symbol='f')",
    "pl.col('b').cast(pl.Int64).register_plugin(lib='libx.so', symbol='f')",
    "pl.Expr.deserialize({path!r})",
    "pl.Expr.from_json({json!r})",
    "pl.Expr.register_plugin(pl.col('b'), lib='x', symbol='f')",
]


@pytest.mark.parametrize("spelling", SPELLINGS)
def test_a_member_that_reads_a_file_or_serialised_data_is_refused(spelling, expression_file):
    text = spelling.format(path=str(expression_file), json=JSON_EXPRESSION)
    problems = formula_problems(text)
    assert problems, f"allowed but must be refused: {text!r}"


@pytest.mark.parametrize("spelling", [s for s in SPELLINGS if "pl.Expr" not in s])
def test_the_refusal_names_the_member_and_the_reason(spelling, expression_file):
    problems = formula_problems(spelling.format(path=str(expression_file), json=JSON_EXPRESSION))
    text = " ".join(problems)
    member = re.search(r"\.(deserialize|from_json|register_plugin)\(", spelling).group(1)
    assert member in text, problems
    assert "may not" in text and ("file" in text or "library" in text), problems
    assert "Fix:" in text


def test_a_formula_that_would_read_a_file_never_reads_it(expression_file):
    text = f"pl.col('a').deserialize({str(expression_file)!r}, format='json')"
    with pytest.raises(FormulaError, match="deserialize"):
        evaluate_formula(text)


def test_a_formula_with_inline_json_is_refused_at_run_time():
    with pytest.raises(FormulaError, match="from_json"):
        evaluate_formula(f"pl.col('a').from_json({JSON_EXPRESSION!r})")


def test_a_missing_file_is_refused_by_the_check_not_by_the_operating_system(tmp_path):
    text = f"pl.col('a').deserialize({str(tmp_path / 'nothing.json')!r})"
    with pytest.raises(FormulaError):
        evaluate_formula(text)


# ---- edge cases: the words alone are not a problem --------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "pl.col('deserialize') * 2",
    "pl.col('from_json') + pl.col('register_plugin')",
    "pl.col('a').alias('deserialize')",
    "pl.col('a').str.contains('deserialize')",
    "pl.col('a').str.contains('x.deserialize(')",
    "pl.lit('pl.col(a).from_json(b)')",
    "pl.col('a').is_in(['deserialize', 'from_json'])",
    "pl.col('a').replace_strict({'deserialize': 'from_json'}, default=pl.col('a'))",
    "pl.col('a').cast(pl.Int64).fill_null(0).round(2)",
])
def test_the_name_of_a_member_as_a_column_or_a_text_is_allowed(text):
    assert formula_problems(text) == []


def test_a_column_named_like_a_member_still_runs():
    frame = pl.DataFrame({"deserialize": [1, 2]})
    assert frame.select(evaluate_formula("pl.col('deserialize') * 2")).to_series().to_list() == [2, 4]


# ---- the rule is structural: a library upgrade cannot reopen the hole silently ---------------------------------

# Members whose signature or documentation (the whole text above "Examples") mention a word that points outside the
# expression, reviewed on 2026-11-17 and found to work on the column's own data. A member that is not here and is not
# refused by the rule makes the walk below fail: someone must read it and decide (add it here with the reason, or extend
# the rule). The walk is a net with holes: it reads words, not effects (see `member_refusal`).
_OWN = "works on the column's own values"
REVIEWED = {
    ("bin", "head"): "first bytes of a binary column's own values",
    ("bin", "tail"): "last bytes of a binary column's own values",
    ("bin", "reinterpret"): "reads the column's own bytes as numbers",
    ("cat", "len_bytes"): "number of bytes of each category text in the column",
    ("cat", "len_chars"): "counts characters; the doc says how it differs from bytes",
    ("cat", "slice"): "cuts each category text; the doc says the offsets are in characters, not bytes",
    ("expr", "search_sorted"): "'location' is the position found in the column's own values",
    ("expr", "set_sorted"): "'paths' is polars' fast code paths for sorted data; it only sets a flag",
    ("str", "find"): "text search; the word 'bytes' is about the match",
    ("str", "find_many"): "text search over the column's own values; 'bytes' is about the match",
    ("str", "head"): "first characters; the doc says the offsets are in characters, not bytes",
    ("str", "tail"): "last characters; the doc says the offsets are in characters, not bytes",
    ("str", "slice"): "cuts each text; the doc says the offsets are in characters, not bytes",
    ("str", "len_chars"): "counts characters; the doc says how it differs from bytes",
    ("str", "len_bytes"): "number of bytes of each text in the column",
    ("str", "json_decode"): "parses the JSON text held in the column's own values",
    ("str", "json_path_match"): "a JSONPath expression applied to the column's own text, no file",
    ("struct", "json_encode"): "writes a struct column to JSON text in the column",
}
RISK_WORDS = re.compile(
    r"\b(path|paths|file|files|filename|bytes|pickle|pickled|json|IO|IOBase|BytesIO|url|uri|environ|environment|plugin|"
    r"plugins|serialize|serialized|serialise|deserialize|deserializing|stream|source|buffer|lib|library|symbol|location|"
    r"directory|folder|disk|network|socket|stdout|stderr|print|prints|write|writes|written|open|shell|subprocess|"
    r"arbitrary|unsafe|untrusted|trusted)\b", re.I)


def _classes():
    return {"expr": pl.Expr, **formula_check._namespace_classes()}


def _allowed_members():
    allowed = formula_check._allowed()
    classes = _classes()
    return [(ns, name) for ns, names in sorted(allowed.items()) for name in sorted(names)]


def test_every_allowed_member_is_an_instance_method_that_returns_an_expression():
    classes = _classes()
    wrong = []
    for ns, name in _allowed_members():
        static = inspect.getattr_static(classes[ns], name)
        if isinstance(static, (staticmethod, classmethod)) or not inspect.isfunction(static):
            wrong.append((ns, name, "not an instance method"))
            continue
        returns = str(inspect.signature(getattr(classes[ns], name)).return_annotation).strip("'\"")
        if returns != "Expr":
            wrong.append((ns, name, f"returns {returns}"))
    assert not wrong, wrong


def test_no_allowed_member_takes_a_function_a_file_or_bytes():
    classes = _classes()
    bad = []
    for ns, name in _allowed_members():
        for p in inspect.signature(getattr(classes[ns], name)).parameters.values():
            annotation = str(p.annotation)
            if re.search(r"\b(Callable|Path|PathLike|IO|IOBase|BytesIO|bytes|bytearray|memoryview)\b", annotation):
                bad.append((ns, name, p.name, annotation))
    assert not bad, bad


def test_every_allowed_member_that_mentions_the_outside_has_been_reviewed():
    """Fails when a Polars version adds an allowed member whose parameters or whole documentation point to a file, a library,
    serialised data or bytes and nobody has decided it. Read the member, then refuse it (extend `member_refusal`) or
    add it to REVIEWED with the reason."""
    classes = _classes()
    unreviewed = []
    for ns, name in _allowed_members():
        member = getattr(classes[ns], name)
        signature = inspect.signature(member)
        text = " ".join(f"{p.name} {p.annotation}" for p in signature.parameters.values())
        text += " " + (inspect.getdoc(member) or "").split("Examples\n")[0]  # the whole text; the examples are code
        if RISK_WORDS.search(text) and (ns, name) not in REVIEWED:
            unreviewed.append((ns, name, sorted({m.group(0).lower() for m in RISK_WORDS.finditer(text)})))
    assert not unreviewed, unreviewed


def test_the_reviewed_list_holds_only_members_that_are_still_allowed():
    allowed = set(_allowed_members())
    stale = [key for key in REVIEWED if key not in allowed]
    assert not stale, stale


def test_the_walk_can_fail_on_a_new_member_that_reads_a_file_or_bytes():
    """The rule itself, on classes that stand for a future Polars: each of these must be refused."""
    from utils.formula_check import member_refusal

    class FutureExpr:
        @classmethod
        def read_expr(cls, source: "str | Path"): ...
        @staticmethod
        def from_bytes(data: bytes): ...
        def load(self, path: "Path") -> "Expr": ...
        def attach(self, lib: str, symbol: str) -> "Expr": ...
        def apply(self, function: "Callable[[int], int]") -> "Expr": ...
        def to_series_values(self) -> "Series": ...
        def untyped(self): ...
        @property
        def namespace(self): ...
        def fine(self, n: int = 1) -> "Expr": ...

    refusals = {name: member_refusal(FutureExpr, name) for name in ("read_expr", "from_bytes", "load", "attach", "apply",
                                                                      "to_series_values", "untyped", "namespace", "fine")}
    assert refusals["fine"] is None
    assert all(reason for name, reason in refusals.items() if name != "fine"), refusals


def test_the_refused_members_include_the_whole_class_found_today():
    from utils.formula_check import refused_members
    refused = refused_members()
    assert {"deserialize", "from_json", "register_plugin"} <= set(refused["expr"])
    assert {"map_batches", "map_elements", "pipe", "rolling_map"} <= set(refused["expr"])
    assert "meta" in refused["expr"]


# ---- the second place that evaluates recipe text: the function string of `stat_function` ---------------------------
# Checked 2026-11-17 with harmless probes: an attribute of `np`, `numpy` or `math` is allowed only when it is a name of
# MATH_FUNCTIONS or MATH_CONSTANTS, so no file reader, no module object and no `__dict__` can be reached. These tests
# keep it so.

@pytest.mark.parametrize("text", [
    "lambda x: np.load('/tmp/x.npy')",
    "lambda x: np.fromfile('/tmp/x.bin')",
    "lambda x: np.memmap('/tmp/x.bin')",
    "lambda x: np.loadtxt('/tmp/x.txt')",
    "lambda x: np.lib",
    "lambda x: np.lib.npyio.load",
    "lambda x: np.ctypeslib",
    "lambda x: np.core",
    "lambda x: math.__dict__",
    "lambda x: np.__dict__",
    "lambda x: np.sin.__self__",
    "lambda x: np.sin.__call__(x)",
    "lambda x: np.sin(x).tofile('/tmp/x')",
    "lambda x: np.sin(x).__class__",
    "lambda x: np.sin(np.load)",
    "lambda x: np.vectorize",
    "lambda x: np.frompyfunc",
    "lambda x: numpy.load('/tmp/x.npy')",
    "np.load",
    "np.lib",
])
def test_a_function_string_cannot_reach_a_file_reader_or_a_module_object(text):
    from utils.formula_check import function_string_problems
    assert function_string_problems(text), f"allowed but must be refused: {text!r}"


def test_every_math_function_of_a_function_string_is_a_pure_elementwise_numpy_function():
    """If a name is added to MATH_FUNCTIONS it must be a numpy ufunc: elementwise, no file, no state."""
    import numpy as np
    from utils.formula_check import MATH_FUNCTIONS
    not_ufunc = [name for name in MATH_FUNCTIONS if not isinstance(getattr(np, name, None), np.ufunc)]
    assert not not_ufunc, not_ufunc


# ---- members refused by name: their danger shows only in what they DO --------------------------------------------
# Decided by Eve, 2026-11-17 (D-0229): `inspect` takes a text that `str.format` runs on the column, so
# '{0.__init__.__globals__[...]}' reaches objects outside the expression and prints them to the server output.
# No shipped formula uses it (checked below).

INSPECT_SPELLINGS = [
    "pl.col('a').inspect()",
    "pl.col('a').inspect('{}')",
    "pl.col('a').inspect(fmt='{}')",
    "pl.col('a').inspect('{0.__class__}')",
    "pl.col('a').cast(pl.Int64).fill_null(0).inspect('{0.__class__}')",
    "pl.col('a').str.strip_chars().inspect()",
    "(pl.col('a') + 1).inspect('{}')",
    "pl.lit(1).inspect('{}')",
    "pl.when(pl.col('a')).then(1).otherwise(0).inspect('{}')",
    "pl.col('a').inspect('{}') + 1",
    "pl.sum_horizontal('a', pl.col('b').inspect())",
]


@pytest.mark.parametrize("text", INSPECT_SPELLINGS)
def test_inspect_is_refused_with_a_plain_reason(text):
    problems = formula_problems(text)
    joined = " ".join(problems)
    assert problems, f"allowed but must be refused: {text!r}"
    assert "inspect prints the column to the server output with a text that can read outside the expression" in joined
    assert "a recipe formula may not do that" in joined and "Fix:" in joined


def test_inspect_never_prints(capsys):
    with pytest.raises(FormulaError, match="inspect"):
        evaluate_formula("pl.col('a').inspect('{0.__class__}')")
    assert capsys.readouterr().out == ""


def test_the_refused_by_name_members_are_still_polars_members_and_are_refused():
    """A by-name entry that Polars no longer has is stale and must be removed; each entry must be refused."""
    from utils.formula_check import REFUSED_BY_NAME, member_refusal
    assert ("expr", "inspect") in {(label, name) for (label, name) in REFUSED_BY_NAME}
    for (label, name), reason in REFUSED_BY_NAME.items():
        cls = _classes()[label]
        assert hasattr(cls, name), f"{label}.{name} no longer exists in Polars: remove it from REFUSED_BY_NAME"
        assert reason and member_refusal(cls, name) == reason


def test_no_shipped_formula_uses_a_member_that_is_refused_by_name():
    """The by-name set must not break a shipped recipe: the shipped formulas are read from the YAML files."""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[3]
    from utils.formula_check import REFUSED_BY_NAME
    names = {name for (_, name) in REFUSED_BY_NAME if name != "meta"}
    hits = []
    for root in ("config", "assets", "libs"):
        for path in (repo / root).rglob("*.yaml"):
            if ".venv" in path.parts or "outdated" in path.parts:
                continue
            text = path.read_text(errors="ignore")
            hits += [(str(path.relative_to(repo)), n) for n in names if f".{n}(" in text]
    assert not hits, hits


def test_a_refused_property_says_why():
    for text, word in (("pl.col('a').meta.serialize()", "meta"), ("pl.col('a').meta.write_json('/tmp/x')", "meta")):
        joined = " ".join(formula_problems(text))
        assert "meta reads the structure of an expression" in joined and "may not do that" in joined, joined


# ---- the module-level functions are a closed, hand-kept list: each entry is reviewed ------------------------------

MODULE_REVIEWED = {
    "col": "names a column; takes names, a regex or dtypes, no file",
    "lit": "a constant; bytes and complex constants are refused by the check",
    "when": "starts when/then/otherwise",
    "all": "all columns, or an aggregation over booleans", "any": "aggregation over booleans",
    "len": "row count", "count": "non-null count", "first": "first value", "last": "last value", "nth": "column by position",
    "exclude": "all columns but the named", "coalesce": "first non-null",
    "concat_str": "joins texts", "concat_list": "joins into a list", "struct": "builds a struct from expressions",
    "format": "fills {} in a text with expressions; no Python format fields",
    "sum": "aggregation", "mean": "aggregation", "median": "aggregation", "min": "aggregation", "max": "aggregation",
    "std": "aggregation", "var": "aggregation", "n_unique": "aggregation", "approx_n_unique": "aggregation",
    "quantile": "aggregation", "corr": "aggregation over two columns", "cov": "aggregation over two columns",
    "sum_horizontal": "row-wise", "min_horizontal": "row-wise", "max_horizontal": "row-wise", "mean_horizontal": "row-wise",
    "all_horizontal": "row-wise", "any_horizontal": "row-wise",
    "date": "builds a date from numbers", "datetime": "builds a datetime from numbers",
    "duration": "builds a duration from numbers", "time": "builds a time from numbers",
}


def test_every_module_function_has_a_review_line_and_none_takes_a_file_or_a_function():
    """`MODULE_FUNCTIONS` is a closed list kept by hand: an entry added without a line here fails, and so does a line
    for an entry that is gone. Each entry must also be an Expr-building function with no file, bytes or function parameter."""
    from utils.formula_check import MODULE_FUNCTIONS
    assert set(MODULE_REVIEWED) == set(MODULE_FUNCTIONS), (
        sorted(set(MODULE_FUNCTIONS) - set(MODULE_REVIEWED)), sorted(set(MODULE_REVIEWED) - set(MODULE_FUNCTIONS)))
    outside_names = {"path", "file", "filepath", "source", "lib", "symbol", "url", "uri", "fname", "filename", "plugin_path",
                     "function", "fun", "buffer"}
    bad = []
    for name in sorted(MODULE_FUNCTIONS):
        target = getattr(pl, name)
        target = getattr(target, "__call__", target) if not inspect.isfunction(target) else target
        for p in inspect.signature(target).parameters.values():
            if re.search(r"\b(Callable|Path|PathLike|IO|IOBase|BytesIO|bytes|bytearray|memoryview)\b", str(p.annotation)) \
                    or p.name in outside_names:
                bad.append((name, p.name, str(p.annotation)))
    assert not bad, bad
