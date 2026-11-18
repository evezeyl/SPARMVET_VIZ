"""The formula check: a recipe formula may build a Polars expression and nothing else (check ST06).

A recipe formula (`polars_with_columns`, ID reconciliation `mutate`) and a plot function string (`stat_function`) were
run with Python `eval`; a formula such as `__import__('os')` ran code with the app's rights. A recipe that comes from
outside (a bundle, an upload in Blueprint) must not be able to do that.

The check reads the formula as syntax and never runs it. What it allows is read from the installed Polars, not from a
list kept by hand:
- `pl.<name>` only for the names in MODULE_FUNCTIONS (a short explicit list) and the Polars dtypes; the module level is
  where file input and output live (`read_*`, `scan_*`, `write_*`, `sink_*`, `Config`), so it is a closed list;
- a public `Expr` method or namespace method that is allowed by what it is (`member_refusal`): an instance method that
  returns an expression, takes no function (`Callable`), no file, no bytes and no library path, so it works on the
  column's own values and on nothing outside the recipe. Every constructor that builds an expression from outside
  data (`Expr.deserialize`, `Expr.from_json`: class methods), `Expr.register_plugin` (loads a native library), the
  namespace `meta`, `Expr.inspect` (refused by name, `REFUSED_BY_NAME`) and any name that starts with `_` are refused. The list is read from the installed Polars at run
  time and `libs/utils/tests/test_formula_reads_no_outside_data.py` fails when a Polars upgrade adds a member that
  nobody has judged (a member allowed by name only, as before 2026-11-17, let `deserialize` read any file);
- `pl.<dtype>` for the Polars dtypes, except `pl.Object`, `pl.Unknown` and `pl.Binary` (REFUSED_DTYPES, D-0230, D-0259);
- constants, arithmetic, comparison and boolean operators, lists, tuples, dictionaries and subscripts.
Refused: any other name, `lambda`, comprehensions, f-strings, starred arguments, conditional expressions, a string or
list multiplied (memory), an exponent that is not a small constant (processor time).

`function_string_problems` (the `stat_function` string) accepts a function only as a call of a name that the module of its prefix has
(`PLOT_FUNCTION_MODULES`, `PLOT_FUNCTION_NAMES`: `np.` and `numpy.` are numpy, `math.` is Python's `math`); the drawing builds
its namespace from the same tables, so a name that passes the check exists when the plot is drawn (D-0232).

`smoother_formula_problems` is a third grammar, for the `formula` of a smoother (`geom_smooth`, `stat_smooth`): plotnine hands
that text to patsy, which runs it as Python (PLOT-TEXT-RUNS-CODE-1). It is read as syntax and never run before it passes:
the variables `x` and `y`, numbers, the operators of a model formula, `I`, `C`, the patsy functions `bs`, `cr`, `cc`, `te`,
`center`, `standardize`, `scale`, and the names of MATH_FUNCTIONS (bare or as `np.name`, `numpy.name`, `math.name`).

`evaluate_formula` runs a checked formula with empty builtins as a second layer. A formula that is allowed can still be
slow or large: nothing here stops heavy computation (spec section 15, known limit).

# @deps
# provides: function:formula_problems, function:evaluate_formula, function:function_string_problems, function:smoother_formula_problems, constant:SMOOTHER_FUNCTIONS, function:denied_methods, function:member_refusal, function:refused_members, constant:REFUSED_BY_NAME, constant:REFUSED_BY_NAME_SUGGESTION, constant:RANDOM_REFUSAL, constant:REFUSED_DTYPES, constant:MODULE_FUNCTIONS, constant:MATH_FUNCTIONS, constant:PLOT_FUNCTION_MODULES, constant:PLOT_FUNCTION_NAMES, constant:PYTHON_MATH_FUNCTIONS, constant:MATH_CONSTANTS, class:FormulaError
# consumed_by: libs/utils/tests/test_formula_check.py, libs/utils/tests/test_formula_element_field.py, libs/utils/tests/test_formula_refuses_object.py, libs/utils/tests/test_formula_reads_no_outside_data.py, libs/utils/tests/test_plot_text_check.py, libs/utils/tests/test_stat_function_names.py, libs/utils/src/utils/plot_text_check.py, libs/utils/src/utils/recipe_check.py, libs/viz_factory/src/viz_factory/checked_plot.py, libs/viz_factory/src/viz_factory/geoms/core.py, libs/transformer/src/transformer/actions/polars_calls.py, libs/id_reconciliation/src/id_reconciliation/core.py, libs/viz_factory/tests/test_stat_function_names_drawn.py
# doc: .claude/design/recipe_format_spec.md (section 15; check ST06)
# @end_deps
"""
import ast
import inspect
import re
from functools import lru_cache
from typing import Dict, List, Set

import polars as pl
from utils.fix_text import SUGGESTION

MAX_LENGTH = 2000
MAX_NODES = 400
MAX_EXPONENT = 100

# Module-level functions a formula may call. A short explicit list: extend it by an entry, with its reason.
MODULE_FUNCTIONS = frozenset({
    "col", "lit", "when", "all", "any", "len", "count", "first", "last", "nth", "exclude", "coalesce",
    "concat_str", "concat_list", "struct", "format",
    # D-0231 (Eve, 2026-11-17): the inner value of a list or struct cell. `element()` takes nothing and `field(name)` a
    # field name; both are the same as `pl.col('')` (already allowed) inside `list.eval` / `struct.with_fields`, and the
    # expression around them is walked like any other.
    "element", "field",
    "sum", "mean", "median", "min", "max", "std", "var", "n_unique", "approx_n_unique", "quantile", "corr", "cov",
    "sum_horizontal", "min_horizontal", "max_horizontal", "mean_horizontal", "all_horizontal", "any_horizontal",
    "date", "datetime", "duration", "time",
})

# Pure maths for a plot function string (`stat_function`); names only, the plot library supplies the functions.
MATH_FUNCTIONS = frozenset({
    "sin", "cos", "tan", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
    "exp", "log", "log10", "log2", "sqrt", "abs", "floor", "ceil", "sign",
})
MATH_CONSTANTS = {"pi": 3.141592653589793, "e": 2.718281828459045}
# The module prefixes of a smoother formula (`geom_smooth`); there `math` is numpy as well (`checked_plot.plot_environment`).
# A `stat_function` string has its own table below.
_MATH_MODULES = ("np", "math", "numpy")

# `stat_function` (D-0232, Eve 2026-11-17: a name that passes the check must also work at drawing). ONE table that the check
# and the drawing both read: which module each prefix is, and which names of it a string may use. The drawing namespace
# (`viz_factory.geoms.core.function_string_namespace`) is built from these tables with `getattr`, so a name that is not in the
# module fails when the plot library starts, never in a recipe; a test checks every entry against the real modules.
# Bare names (`sin`, `arcsin`, ...) are numpy's: MATH_FUNCTIONS. `numpy.` is the same module as `np.` (option b of the
# builder's choice: the spec already lists `numpy.name` for a smoother, one vocabulary for both places). `math` is Python's own
# `math`, which has other names (`asin`, not `arcsin`; `fabs`, not `abs`; no `sign`) and takes one number at a time.
PLOT_FUNCTION_MODULES = {"np": "numpy", "numpy": "numpy", "math": "math"}
PYTHON_MATH_FUNCTIONS = frozenset({
    "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh",
    "exp", "log", "log10", "log2", "sqrt", "fabs", "floor", "ceil",
})
PLOT_FUNCTION_NAMES = {"numpy": MATH_FUNCTIONS, "math": PYTHON_MATH_FUNCTIONS}
# What a numpy name is called in `math` (for the message); a name that is not here has no equal in `math`.
_PYTHON_MATH_NAME = {"arcsin": "asin", "arccos": "acos", "arctan": "atan", "abs": "fabs"}
# How many numbers a call takes, per (module, name); every other function takes exactly one.
_PLOT_FUNCTION_ARGUMENTS = {("math", "log"): (1, 2)}

# Namespaces of an expression that a formula may use, by their name on `Expr`.
_NAMESPACES = ("str", "dt", "list", "arr", "cat", "struct", "name", "bin")


class FormulaError(ValueError):
    """A formula that the check refuses; the message holds every problem."""


def _namespace_classes() -> Dict[str, type]:
    probe = pl.col("x")
    return {name: type(getattr(probe, name)) for name in _NAMESPACES + ("meta",) if hasattr(probe, name)}


def _public(cls: type) -> Set[str]:
    return {n for n in dir(cls) if not n.startswith("_")}


def _parameters(member):
    try:
        return list(inspect.signature(member).parameters.values())
    except (TypeError, ValueError):
        return None


def _takes_a_function(member) -> bool:
    parameters = _parameters(member) or []
    return any("Callable" in str(p.annotation) or "Callable" in repr(p.annotation) for p in parameters)


# A parameter typed as one of these hands the member a file, a stream or raw bytes.
_OUTSIDE_TYPES = re.compile(r"\b(Path|PathLike|IO|IOBase|BytesIO|RawIOBase|BufferedIOBase|bytes|bytearray|memoryview)\b")
# A parameter named like this points the member at something outside the expression (a file, a library to load).
# Types cannot show it (`register_plugin(lib: str, symbol: str)` has only strings), so the names are listed, with the
# test that reads every allowed member (`test_every_allowed_member_that_mentions_the_outside_has_been_reviewed`) as the net.
_OUTSIDE_NAMES = frozenset({"lib", "symbol", "plugin_path", "path", "file", "filepath", "file_path", "source", "buffer",
                            "url", "uri", "fname", "filename"})

NOT_A_METHOD = "is not an expression method"
CALLS_A_FUNCTION = "runs a Python function and is not allowed"
READS_OUTSIDE_DATA = "builds an expression from a file or from serialised data; a recipe formula may not read files"
TAKES_OUTSIDE_DATA = "takes a file, a stream or bytes; a recipe formula may not read files"
LOADS_OUTSIDE = "loads or reads something outside the expression (a file or a library); a recipe formula may not do that"
PRINTS_OUTSIDE = ("prints the column to the server output with a text that can read outside the expression; "
                  "a recipe formula may not do that")
META_OUTSIDE = ("reads the structure of an expression and can write it to a file or to serialised data; "
                "a recipe formula may not do that")

# Members refused by NAME because their danger shows only in what they DO, not in their signature. A small, reviewed
# set; every entry must still exist in Polars (a test fails on a stale entry).
# `Expr.inspect` is refused by decision of Eve, 2026-11-17 (D-0229): it takes a text that `str.format` runs on the
# column, so a recipe could write '{0.__init__.__globals__[...]}' and print objects of the running program (including
# the process environment) to the server output. No shipped formula uses it.
# `set_sorted` and `search_sorted` are refused by decision of Eve, 2026-11-18 (D-0257): each gives a wrong result with
# no message when misused (a flag that says "sorted" for data that is not; a search that assumes sorted data). They can
# be added later on a real need.
RANDOM_REFUSAL = ("draws at random, so the result would differ at each run and the same recipe and data would not give the same "
                  "table; it is refused for now, also with a seed, until a seed rule for formulas exists")
RANDOM_SUGGESTION = ("Suggestion: to take a random sample of rows use the step polars_sample with a seed written in the step "
                     "(for example `fraction: 0.1`, `seed: 1`); for any other random use there is no formula, ask for it to be added")
REFUSED_BY_NAME = {
    ("expr", "inspect"): PRINTS_OUTSIDE,
    ("expr", "meta"): META_OUTSIDE,
    ("expr", "set_sorted"): ("only sets a flag that says the column is sorted, without checking it; "
                             "if the column is not sorted, later results are wrong with no message, so it is not allowed"),
    ("expr", "search_sorted"): ("assumes the column is sorted and does not check it; "
                                "if it is not sorted, the answer is wrong with no message, so it is not allowed"),
    # `shuffle` and `sample` are refused by decision of Eve, 2026-11-18 (D-0278, D-0279): the result differs at each run, and
    # a seed rule for formulas does not exist yet; a member with a `seed` argument is refused too. They come back when a
    # recipe needs one and a seed rule for formulas exists. `rank`, `rolling_rank` and `rolling_rank_by` with method "random" are the same and are refused in
    # `_check_random_rank`.
    ("expr", "shuffle"): RANDOM_REFUSAL,
    ("expr", "sample"): RANDOM_REFUSAL,
    ("list", "sample"): RANDOM_REFUSAL,
}

# A "Suggestion: ..." for a member of REFUSED_BY_NAME that has a correct alternative (the others keep the default fix).
REFUSED_BY_NAME_SUGGESTION = {
    ("expr", "set_sorted"): "Suggestion: sort the table with a sort step before the step that needs sorted data",
    ("expr", "search_sorted"): ("Suggestion: there is no formula for this; ask for the function to be added"),
    ("expr", "shuffle"): RANDOM_SUGGESTION,
    ("expr", "sample"): RANDOM_SUGGESTION,
    ("list", "sample"): RANDOM_SUGGESTION,
}


# Data types a formula may not name. PARKED by Eve, 2026-11-17 (D-0230): "park it and refuse. With a note of possibility
# to re evaluate if request or necessity later on." `pl.Object` holds any Python object, which a normal table does not
# (`str.json_decode(pl.Object)` passed the check and stopped the calculation with a Polars panic). Every way to name
# the type goes through `pl.<name>`, so one refusal there covers `pl.Object`, `pl.Object()`, `pl.List(pl.Object)`,
# `pl.Struct({'x': pl.Object})` and a keyword value; Polars does not accept a dtype written as a string (tested). Panics
# are not caught: a type that panics is refused here. Re-evaluate if a request or a necessity comes.
REFUSED_DTYPES = {
    "Object": "pl.Object holds any Python object, which a table column does not; a recipe works on normal table columns",
    # D-0259 (Eve, 2026-11-18): the same rule. Each stops the calculation with a Polars panic in `str.json_decode`
    # (checked 2026-11-18: pl.Unknown, pl.Array(pl.Unknown, n) and pl.Binary panic; pl.List(...) of them is a plain error).
    # Refusing the name covers every spelling that goes through `pl.<name>`, also inside pl.List and pl.Array.
    "Unknown": ("pl.Unknown is not a real type for a column: a cast to it silently gives another type, "
                "and decoding text to it (or to an array of it) stops the calculation; it is not allowed in formulas"),
    "Binary": ("pl.Binary holds raw bytes, which a recipe table does not hold; it is not allowed in formulas "
               "(decoding text to it stops the calculation)"),
}

REFUSED_DTYPE_SUGGESTION = ("Suggestion: use a type a table can hold, for example pl.String, pl.Int64, pl.Float64, pl.Boolean, "
                            "pl.List(...) or pl.Struct({...}) of those")


def member_refusal(cls: type, name: str) -> "str | None":
    """Why a member of `cls` may not be called in a formula, or None when it is allowed (by what it is, not by its name).

    Allowed: an instance method that returns an expression and takes no function, no file, no bytes and no library path.
    The reason, when there is one, is a sentence that follows the member name.

    What this cannot see (read it before trusting it): the rule reads signatures, annotations and parameter names, and
    the walk test reads the words of the documentation. A danger that shows in neither is invisible to both: a
    parameter that names a file in unlisted words (`location: str`), a text that a member interprets (`inspect`), a
    member that is dangerous only by its effect, and a danger written only in a part of the documentation the test
    does not read. Those are caught only by a person reading each new member, which the walk forces for the words it
    knows. `REFUSED_BY_NAME` holds the members found that way. This is a net with holes, not a proof.
    """
    for label, owner in [("expr", pl.Expr)] + list(_namespace_classes().items()):
        if cls is owner and (label, name) in REFUSED_BY_NAME:
            return REFUSED_BY_NAME[(label, name)]
    static = inspect.getattr_static(cls, name)
    if isinstance(static, (classmethod, staticmethod)):
        return READS_OUTSIDE_DATA  # a constructor that builds an expression from data outside the recipe
    if not inspect.isfunction(static):
        return NOT_A_METHOD  # a property (the namespaces are read apart), a constant, a class
    member = getattr(cls, name)
    parameters = _parameters(member)
    if parameters is None:
        return NOT_A_METHOD  # a signature that cannot be read cannot be judged: refused
    if _takes_a_function(member):
        return CALLS_A_FUNCTION
    if any(_OUTSIDE_TYPES.search(str(p.annotation)) for p in parameters):
        return TAKES_OUTSIDE_DATA
    if any(p.name in _OUTSIDE_NAMES for p in parameters):
        return LOADS_OUTSIDE
    if str(inspect.signature(member).return_annotation).strip("'\"") != "Expr":
        return NOT_A_METHOD  # it does not return an expression
    return None


@lru_cache(maxsize=1)
def refused_members() -> Dict[str, Dict[str, str]]:
    """Per namespace ('expr' for Expr itself), every public member that is refused, with the reason."""
    result: Dict[str, Dict[str, str]] = {}
    for label, cls in [("expr", pl.Expr)] + list(_namespace_classes().items()):
        result[label] = {n: why for n in sorted(_public(cls)) if (why := member_refusal(cls, n))}
    return result


@lru_cache(maxsize=1)
def denied_methods() -> Dict[str, Set[str]]:
    """Per namespace, the public methods that take a function, read from the signatures (a part of `refused_members`)."""
    return {label: {n for n, why in refusals.items() if why == CALLS_A_FUNCTION} for label, refusals in refused_members().items()}


@lru_cache(maxsize=1)
def _allowed() -> Dict[str, Set[str]]:
    """Per namespace, the members a formula may call; the keys other than 'expr' are the namespaces a formula may enter."""
    refused = refused_members()
    allowed = {"expr": _public(pl.Expr) - set(refused["expr"])}
    for name, cls in _namespace_classes().items():
        if name == "meta":
            continue
        allowed[name] = _public(cls) - set(refused[name])
    return allowed


@lru_cache(maxsize=1)
def _dtypes() -> Set[str]:
    return {n for n in dir(pl) if isinstance(getattr(pl, n), type) and issubclass(getattr(pl, n), pl.DataType)}


def _fix(text: str) -> str:
    """The fix after a problem, with ONE label: `Fix: ...`, or the text as it is when it starts with `Suggestion:`."""
    return f" {text}" if text.startswith(SUGGESTION) else f" Fix: {text}"


def _sentence(problem: str) -> str:
    """A problem text that ends with a period, so that two problems read as two sentences."""
    problem = problem.rstrip()
    return problem if problem[-1:] in (".", "!", "?") else problem + "."


def _node_count(tree: ast.AST) -> int:
    return sum(1 for _ in ast.walk(tree))


class _Checker:
    """Walks the syntax tree; `kind` of an expression is 'module', 'expr', or a namespace name."""

    def __init__(self) -> None:
        self.problems: List[str] = []

    def refuse(self, what: str, fix: str = "build the column with pl.col, pl.lit, pl.when and the Polars expression methods") -> None:
        self.problems.append(what + "." + _fix(fix))

    def visit(self, node: ast.AST) -> str:
        method = getattr(self, "visit_" + type(node).__name__, None)
        if method is None:
            self.refuse(f"{type(node).__name__} is not allowed in a formula")
            return "value"
        return method(node)

    # -- leaves
    def visit_Constant(self, node: ast.Constant) -> str:
        if node.value is Ellipsis or isinstance(node.value, (bytes, complex)):
            self.refuse(f"the constant {node.value!r} is not allowed")
        return "value"

    def visit_Name(self, node: ast.Name) -> str:
        if node.id == "pl":
            return "module"
        self.refuse(f"the name {node.id!r} is not allowed; only pl is known", "write pl.<function>")
        return "value"

    # -- structure
    def visit_Attribute(self, node: ast.Attribute) -> str:
        kind = self.visit(node.value)
        name = node.attr
        if name.startswith("_"):
            self.refuse(f"the attribute {name!r} starts with an underscore")
            return "value"
        allowed = _allowed()
        if kind == "module":
            if name in MODULE_FUNCTIONS:
                return "function:" + name
            if name in REFUSED_DTYPES:
                self.refuse(REFUSED_DTYPES[name], REFUSED_DTYPE_SUGGESTION)
                return "dtype"
            if name in _dtypes():
                return "dtype"
            self.refuse(f"pl.{name} is not allowed", "use one of: " + ", ".join(sorted(MODULE_FUNCTIONS)))
            return "value"
        if kind == "when":  # pl.when(...) is followed by .then(...)
            if name == "then":
                return "method:then"
            self.refuse(f"after pl.when(...) only .then(...) is allowed, not {name}")
            return "value"
        if kind == "then":  # .then(...) continues with .when(...), .otherwise(...) or any expression method
            if name == "when":
                return "method:when"
            if name == "otherwise":
                return "method:otherwise"
            kind = "expr"
        if kind.startswith("function:") or kind.startswith("method:") or kind == "dtype":
            self.refuse(f"an attribute of {kind.split(':')[-1]} is not allowed")
            return "value"
        if kind in ("expr", "value"):
            if name in _NAMESPACES and name in allowed:
                return name
            if name in allowed["expr"]:
                return "method:" + name
            suggestion = REFUSED_BY_NAME_SUGGESTION.get(("expr", name))
            self.refuse(f"{name} {refused_members()['expr'].get(name, NOT_A_METHOD)}", *([suggestion] if suggestion else []))
            return "value"
        if kind in allowed:  # a namespace
            if name in allowed[kind]:
                return "method:" + name
            suggestion = REFUSED_BY_NAME_SUGGESTION.get((kind, name))
            self.refuse(f"{kind}.{name} {refused_members().get(kind, {}).get(name, NOT_A_METHOD)}", *([suggestion] if suggestion else []))
            return "value"
        self.refuse(f"{name} cannot be used here")
        return "value"

    def visit_Call(self, node: ast.Call) -> str:
        kind = self.visit(node.func)
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                self.refuse("starred arguments are not allowed")
            else:
                self.visit(arg)
        for keyword in node.keywords:
            if keyword.arg is None:
                self.refuse("** arguments are not allowed")
            elif keyword.arg.startswith("_"):
                self.refuse(f"the argument name {keyword.arg!r} starts with an underscore")
            self.visit(keyword.value)
        self._check_inner_value_call(kind, node)
        self._check_random_rank(kind, node)
        if kind == "dtype":
            return "dtype"
        if kind == "function:when" or kind == "method:when":
            return "when"
        if kind == "method:then":
            return "then"
        return "expr"

    def _check_random_rank(self, kind: str, node: ast.Call) -> None:
        """`rank(method='random')` breaks ties at random: refused like `shuffle` (D-0278, D-0279)."""
        if kind not in ("method:rank", "method:rolling_rank", "method:rolling_rank_by"):
            return
        values = list(node.args) + [k.value for k in node.keywords if k.arg == "method"]
        if any(isinstance(v, ast.Constant) and v.value == "random" for v in values):
            self.refuse((f"{kind.split(':')[1]} with method 'random' breaks ties at random, so the result would differ at each run and the same recipe and data "
                         "would not give the same table; it is refused for now, also with a seed, until a seed rule for formulas exists"), RANDOM_SUGGESTION)

    def _check_inner_value_call(self, kind: str, node: ast.Call) -> None:
        """`pl.element()` takes nothing and `pl.field` one name or a list of names (checked against the installed Polars)."""
        if kind == "function:element" and (node.args or node.keywords):
            self.refuse("pl.element() takes no argument", "write pl.element()")
        elif kind == "function:field":
            names = node.args[0] if len(node.args) == 1 else None
            texts = isinstance(names, ast.Constant) and isinstance(names.value, str) or (
                isinstance(names, ast.List) and all(isinstance(n, ast.Constant) and isinstance(n.value, str) for n in names.elts))
            if node.keywords or not texts:
                self.refuse("pl.field takes one field name as text, or a list of names as texts",
                            "write pl.field('x') or pl.field(['x', 'y'])")

    def visit_Subscript(self, node: ast.Subscript) -> str:
        self.visit(node.value)
        self.visit(node.slice)
        return "expr"

    def visit_Slice(self, node: ast.Slice) -> str:
        for part in (node.lower, node.upper, node.step):
            if part is not None:
                self.visit(part)
        return "value"

    # -- operators and containers
    def visit_BinOp(self, node: ast.BinOp) -> str:
        operator = type(node.op)
        if operator is ast.LShift:
            self.refuse("<< is not allowed")
        if operator is ast.Pow:
            exponent = node.right
            if not (isinstance(exponent, ast.Constant) and isinstance(exponent.value, (int, float))
                    and abs(exponent.value) <= MAX_EXPONENT):
                self.refuse(f"an exponent must be a constant number up to {MAX_EXPONENT}")
        if operator in (ast.Mult, ast.Mod):
            for side in (node.left, node.right):
                if isinstance(side, (ast.List, ast.Tuple)) or (isinstance(side, ast.Constant) and isinstance(side.value, str)):
                    self.refuse("a text or a list cannot be multiplied or formatted with an operator")
        self.visit(node.left)
        self.visit(node.right)
        return "expr"

    def visit_UnaryOp(self, node: ast.UnaryOp) -> str:
        self.visit(node.operand)
        return "expr"

    def visit_BoolOp(self, node: ast.BoolOp) -> str:
        for value in node.values:
            self.visit(value)
        return "expr"

    def visit_Compare(self, node: ast.Compare) -> str:
        self.visit(node.left)
        for comparator in node.comparators:
            self.visit(comparator)
        return "expr"

    def visit_List(self, node: ast.List) -> str:
        for item in node.elts:
            self.visit(item)
        return "value"

    visit_Tuple = visit_List

    def visit_Dict(self, node: ast.Dict) -> str:
        for key, value in zip(node.keys, node.values):
            if key is None:
                self.refuse("** in a dictionary is not allowed")
            else:
                self.visit(key)
            self.visit(value)
        return "value"

    def visit_Load(self, node: ast.AST) -> str:
        return "value"


def _parse(text) -> "ast.Expression | List[str]":
    if not isinstance(text, str) or not text.strip():
        return ["the formula is empty." + _fix("write a Polars expression, for example pl.col('x') * 2")]
    if len(text) > MAX_LENGTH:
        return [f"the formula is longer than {MAX_LENGTH} characters." + _fix("split it into several steps")]
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except (SyntaxError, ValueError, RecursionError, MemoryError) as error:
        return [f"the formula is not a valid expression ({type(error).__name__})." + _fix("write one Python expression")]
    if _node_count(tree) > MAX_NODES:
        return [f"the formula has more than {MAX_NODES} parts." + _fix("split it into several steps")]
    return tree


def formula_problems(text) -> List[str]:
    """Every reason a Polars formula is refused, as 'what is wrong. Fix: what to write.'; an empty list means allowed."""
    tree = _parse(text)
    if isinstance(tree, list):
        return tree
    checker = _Checker()
    try:
        kind = checker.visit(tree.body)
    except RecursionError:
        return ["the formula is nested too deeply." + _fix("split it into several steps")]
    uncalled = kind in ("module", "dtype", "when") or kind in _NAMESPACES or kind.startswith(("function:", "method:"))
    if not checker.problems and uncalled:
        checker.refuse("the formula does not build an expression (a name is left uncalled)", "call it, for example pl.col('x')")
    return checker.problems


# The only names a checked formula can see; there are no builtins.
EVAL_GLOBALS = {"__builtins__": {}, "pl": pl}


def evaluate_formula(text):
    """Check, then run a formula with empty builtins; raises FormulaError with every problem if it is refused."""
    problems = formula_problems(text)
    if problems:
        raise FormulaError(" ".join(_sentence(p) for p in problems))
    try:
        return eval(compile(ast.parse(text.strip(), mode="eval"), "<formula>", "eval"), dict(EVAL_GLOBALS))  # noqa: S307
    except (TypeError, ValueError) as error:
        # Polars refused the arguments while the expression was being built; the check could not know it from the text.
        raise FormulaError(f"the formula {text.strip()!r} could not be built: {error}. Suggestion: check the arguments of each call "
                           "against the Polars documentation") from error


# ---- the function string of a plot (`stat_function`) --------------------------------------------------------------

class _FunctionChecker(ast.NodeVisitor):
    """`lambda x: <numbers, x, arithmetic, calls of the allowed functions>` or a bare math function name.

    A function is allowed only as `name(...)` for a name of MATH_FUNCTIONS (numpy's, bare), or as `prefix.name(...)` when
    `prefix` is a key of PLOT_FUNCTION_MODULES and `name` is in that module's list (PLOT_FUNCTION_NAMES): what is accepted
    here is what the drawing namespace has, per module.
    """

    def __init__(self, argument: str) -> None:
        self.argument = argument
        self.problems: List[str] = []

    def refuse(self, what: str, fix: "str | None" = None) -> None:
        if fix is None:
            fix = ("write a lambda of one argument over numbers, the argument and "
                   + ", ".join(sorted(MATH_FUNCTIONS)[:6]) + " and the like")
        self.problems.append(what + "." + _fix(fix))

    def generic_visit(self, node: ast.AST) -> None:
        self.refuse(f"{type(node).__name__} is not allowed in a plot function")

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            self.refuse(f"the constant {node.value!r} is not a number")

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == self.argument or node.id in MATH_CONSTANTS:
            return
        if node.id in MATH_FUNCTIONS:
            self.refuse(f"{node.id} is a function and is not called", f"Suggestion: write {node.id}({self.argument})")
            return
        self.refuse(f"the name {node.id!r} is not allowed")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """`np.pi`, `math.e`: a constant of a known module; a function must be called."""
        module = node.value.id if isinstance(node.value, ast.Name) else None
        if module not in PLOT_FUNCTION_MODULES:
            self.refuse(f"the attribute {node.attr!r} is not allowed")
        elif node.attr in MATH_CONSTANTS:
            return
        elif node.attr in PLOT_FUNCTION_NAMES[PLOT_FUNCTION_MODULES[module]]:
            self.refuse(f"{module}.{node.attr} is a function and is not called", f"Suggestion: write {module}.{node.attr}({self.argument})")
        else:
            self.refuse(f"the attribute {module}.{node.attr} is not allowed")

    def _module_function(self, func: ast.Attribute) -> None:
        """`prefix.name(...)`: say what exists when the name is not in the module of that prefix."""
        module = func.value.id if isinstance(func.value, ast.Name) else None
        name = func.attr
        if module not in PLOT_FUNCTION_MODULES:
            shown = ast.unparse(func)
            self.refuse(f"the function {shown!r} is not allowed" if module is None else f"the module {module!r} is not allowed",
                        "Suggestion: use " + ", ".join(sorted(PLOT_FUNCTION_MODULES)) + ", for example np.sqrt(x)")
            return
        real = PLOT_FUNCTION_MODULES[module]
        allowed = PLOT_FUNCTION_NAMES[real]
        if name in allowed:
            return
        if name in MATH_CONSTANTS:
            self.refuse(f"{module}.{name} is a number, not a function", f"Suggestion: write {module}.{name} without brackets")
        elif real == "math" and name in MATH_FUNCTIONS:
            equal = _PYTHON_MATH_NAME.get(name)
            if equal:
                self.refuse(f"math.{name} does not exist: math has {equal}, not {name}",
                            f"Suggestion: write math.{equal}, or np.{name}")
            else:
                self.refuse(f"math.{name} does not exist: math has no {name}", f"Suggestion: write np.{name}")
        else:
            self.refuse(f"the function {module}.{name} is not allowed",
                        f"Suggestion: {module} may use " + ", ".join(sorted(allowed)))

    def visit_Call(self, node: ast.Call) -> None:
        if node.keywords:
            self.refuse("keyword arguments are not allowed")
        func = node.func
        if isinstance(func, ast.Name):
            if func.id not in MATH_FUNCTIONS:
                self.refuse(f"the function {func.id!r} is not allowed",
                            "Suggestion: use one of " + ", ".join(sorted(MATH_FUNCTIONS)))
            module, real = None, "numpy"
        elif isinstance(func, ast.Attribute):
            self._module_function(func)
            module = func.value.id if isinstance(func.value, ast.Name) else None
            real = PLOT_FUNCTION_MODULES.get(module)
        else:
            self.refuse("only a named math function can be called")
            module, real = None, None
        name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
        if real is not None:
            low, high = _PLOT_FUNCTION_ARGUMENTS.get((real, name), (1, 1))
            if not low <= len(node.args) <= high:
                shown = f"{module}.{name}" if module else name
                count = f"{low}" if low == high else f"{low} or {high}"
                self.refuse(f"{shown} takes {count} number{'s' if high > 1 else ''}, not {len(node.args)}",
                            f"Suggestion: write {shown}({', '.join([self.argument] * low)})")
        for arg in node.args:
            self.visit(arg)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if isinstance(node.op, ast.Pow):
            exponent = node.right
            if not (isinstance(exponent, ast.Constant) and isinstance(exponent.value, (int, float))
                    and not isinstance(exponent.value, bool) and abs(exponent.value) <= MAX_EXPONENT):
                self.refuse(f"an exponent must be a constant number up to {MAX_EXPONENT}")
        elif not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.FloorDiv)):
            self.refuse(f"the operator {type(node.op).__name__} is not allowed")
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if not isinstance(node.op, (ast.UAdd, ast.USub)):
            self.refuse("only + and - in front of a number are allowed")
        self.visit(node.operand)


def function_string_problems(text) -> List[str]:
    """Reasons a `stat_function` string is refused; an empty list means a bare math name or a pure lambda over numbers."""
    tree = _parse(text)
    if isinstance(tree, list):
        return tree
    body = tree.body
    if isinstance(body, ast.Name):
        if body.id in MATH_FUNCTIONS:
            return []
        return [f"the name {body.id!r} is not allowed." + _fix("write a lambda of one argument, or one of " + ", ".join(sorted(MATH_FUNCTIONS)))]
    if not isinstance(body, ast.Lambda):
        return ["the plot function must be a lambda of one argument or a math function name." + _fix("write lambda x: x * 2")]
    arguments = body.args
    if len(arguments.args) != 1 or arguments.vararg or arguments.kwarg or arguments.kwonlyargs \
            or arguments.defaults or arguments.posonlyargs:
        return ["the lambda must take exactly one plain argument." + _fix("write lambda x: ...")]
    checker = _FunctionChecker(arguments.args[0].arg)
    try:
        checker.visit(body.body)
    except RecursionError:
        return ["the plot function is nested too deeply." + _fix("simplify it")]
    return checker.problems


# ---- the formula of a smoother (`geom_smooth`, `stat_smooth`, `*_quantile`) ------------------------------------------

# patsy functions a smoother formula may call; `I` and `C` are patsy's own, the rest build a design matrix.
SMOOTHER_FUNCTIONS = frozenset({"I", "C", "bs", "cr", "cc", "te", "center", "standardize", "scale"})
SMOOTHER_VARIABLES = frozenset({"x", "y"})
SMOOTHER_CONSTANTS = frozenset(MATH_CONSTANTS)
_KEYWORD_VALUES = ("True", "False")
_FORMULA_TOKEN = re.compile(
    r"\s*(?:(?P<number>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)"
    r"|(?P<name>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
    r"|(?P<op>\*\*|==|!=|>=|<=|[-+*/:(),~=<>]))")
_BINARY_OPERATORS = ("+", "-", "*", "/", ":", "**", "==", "!=", ">=", "<=", "<", ">")


def _suggest(text: str) -> str:
    return f" Suggestion: {text}"


_SMOOTHER_HELP = "write a model formula over x and y, for example y ~ x + I(x**2) or y ~ np.log(x)"
_FUNCTIONS_HELP = ("write one of the allowed functions: " + ", ".join(sorted(SMOOTHER_FUNCTIONS)) + ", or a math function ("
                   + ", ".join(sorted(MATH_FUNCTIONS)) + ") alone or as np.<name>, for example y ~ np.log(x)")


class _Stop(Exception):
    """The shape of the formula is wrong: the rest cannot be read, so no further problem is listed."""


class _FormulaParser:
    """Recursive descent over the tokens of a smoother formula; collects every problem, never evaluates anything."""

    def __init__(self, text: str) -> None:
        self.problems: List[str] = []
        self.tokens: List[tuple] = []
        self.position = 0
        self._tokenize(text)

    def refuse(self, what: str, suggestion: str = _SMOOTHER_HELP, stop: bool = True) -> None:
        message = what + "." + _suggest(suggestion)
        if message not in self.problems:
            self.problems.append(message)
        if stop:
            raise _Stop()

    def _tokenize(self, text: str) -> None:
        index = 0
        text = text.rstrip()
        while index < len(text):
            match = _FORMULA_TOKEN.match(text, index)
            if match is None:
                start = index + (len(text[index:]) - len(text[index:].lstrip()))
                bad = text[start:start + 1]
                near = text[max(0, start - 20):start + 20].strip()
                kind = "a text in quotes" if bad in "'\"" else f"the character {bad!r}"
                self.refuse(f"{kind} is not allowed in a smoother formula (near {near!r})", stop=False)
                self.tokens = []
                return
            kind = match.lastgroup
            self.tokens.append((kind, match.group(kind)))
            index = match.end()
        if len(self.tokens) > MAX_NODES:
            self.refuse(f"the formula has more than {MAX_NODES} parts", "split the model into a simpler formula", stop=False)
            self.tokens = []

    # -- token helpers
    def peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else (None, None)

    def take(self):
        token = self.peek()
        self.position += 1
        return token

    def at(self, value: str) -> bool:
        return self.peek()[1] == value and self.peek()[0] == "op"

    # -- grammar
    def formula(self) -> None:
        if not self.tokens:
            return
        if sum(1 for kind, value in self.tokens if kind == "op" and value == "~") != 1:
            self.refuse("a smoother formula has exactly one ~, with y on the left and the model on the right, as in y ~ x")
            return
        self.expression()
        if not self.at("~"):
            self.refuse("the left side of ~ is not a valid expression" if self.position < len(self.tokens) else "the formula has no ~")
            return
        self.take()
        if self.position >= len(self.tokens):
            self.refuse("the model on the right of ~ is empty")
            return
        self.expression()
        if self.position < len(self.tokens):
            kind, value = self.peek()
            self.refuse(f"the part {value!r} is not allowed here")

    def expression(self) -> None:
        self.unary()
        while self.peek()[0] == "op" and self.peek()[1] in _BINARY_OPERATORS:
            _, operator = self.take()
            if operator == "**":
                self.exponent()
            else:
                self.unary()

    def exponent(self) -> None:
        if self.at("-") or self.at("+"):
            self.take()
        kind, value = self.peek()
        if kind != "number" or abs(float(value)) > MAX_EXPONENT:
            self.refuse(f"an exponent must be a number up to {MAX_EXPONENT}, not {value if value is not None else 'nothing'!r}",
                        "write the exponent as a number, for example I(x**2)")
            return
        self.take()
        if self.at("**"):
            self.refuse("a power of a power is not allowed", "write the exponent once, for example I(x**4)")

    def unary(self) -> None:
        if self.at("-") or self.at("+"):
            self.take()
            self.unary()
            return
        self.atom()

    def atom(self) -> None:
        kind, value = self.take()
        if kind == "number":
            return
        if kind == "op" and value == "(":
            self.expression()
            if not self.at(")"):
                self.refuse("a bracket is not closed")
                return
            self.take()
            return
        if kind == "name":
            if self.at("("):
                self.call(value)
            else:
                self.variable(value)
            return
        self.refuse(f"{value!r} is not allowed here" if value is not None else "the formula ends where a term is expected",
                    "write a term such as x, a number, or a function of x")

    def variable(self, name: str) -> None:
        if name in SMOOTHER_VARIABLES or name in SMOOTHER_CONSTANTS:
            return
        if "." in name and name.split(".")[0] in _MATH_MODULES and name.split(".")[-1] in MATH_CONSTANTS:
            return
        self.refuse(f"the name {name!r} is not allowed in a smoother formula; only x and y are known",
                    "write x or y (a smoother sees only the two plotted variables), for example y ~ x + I(x**2)", stop=False)

    def function_allowed(self, name: str) -> bool:
        if name in SMOOTHER_FUNCTIONS or name in MATH_FUNCTIONS:
            return True
        head, _, tail = name.partition(".")
        return head in _MATH_MODULES and tail in MATH_FUNCTIONS

    def call(self, name: str) -> None:
        if not self.function_allowed(name):
            self.refuse(f"the function {name!r} is not allowed in a smoother formula", _FUNCTIONS_HELP, stop=False)
        self.take()  # "("
        if self.at(")"):
            self.take()
            return
        while True:
            self.argument()
            if self.at(","):
                self.take()
                continue
            break
        if not self.at(")"):
            self.refuse(f"the call of {name!r} is not closed")
            return
        self.take()

    def argument(self) -> None:
        kind, value = self.peek()
        following = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else (None, None)
        if kind == "name" and following == ("op", "="):
            self.take()
            self.take()
            sign = self.at("-")
            if sign:
                self.take()
            kind, value = self.peek()
            if kind == "number" or (kind == "name" and value in _KEYWORD_VALUES and not sign):
                self.take()
                return
            self.refuse(f"the value of an option must be a number or True or False, not {value!r}", "write a number, for example df=4")
            return
        self.expression()


def smoother_formula_problems(text) -> List[str]:
    """Reasons the `formula` of a smoother is refused, as 'what. Suggestion: what to write.'; an empty list means allowed."""
    if not isinstance(text, str) or not text.strip():
        return ["the formula is empty or is not text." + _suggest("write a model formula, for example y ~ x + I(x**2)")]
    if len(text) > MAX_LENGTH:
        return [f"the formula is longer than {MAX_LENGTH} characters." + _suggest("write a shorter model")]
    parser = _FormulaParser(text)
    try:
        parser.formula()
    except _Stop:
        pass
    except RecursionError:
        return ["the formula is nested too deeply." + _suggest("write a simpler model")]
    return parser.problems
