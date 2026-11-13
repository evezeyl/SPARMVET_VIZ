"""The formula check: a recipe formula may build a Polars expression and nothing else (check ST06).

A recipe formula (`polars_with_columns`, ID reconciliation `mutate`) and a plot function string (`stat_function`) were
run with Python `eval`; a formula such as `__import__('os')` ran code with the app's rights. A recipe that comes from
outside (a bundle, an upload in Blueprint) must not be able to do that.

The check reads the formula as syntax and never runs it. What it allows is read from the installed Polars, not from a
list kept by hand:
- `pl.<name>` only for the names in MODULE_FUNCTIONS (a short explicit list) and the Polars dtypes; the module level is
  where file input and output live (`read_*`, `scan_*`, `write_*`, `sink_*`, `Config`), so it is a closed list;
- any public `Expr` method or namespace method, except every method that takes a function (found by reading the
  signatures: a parameter annotated `Callable`), the namespace `meta`, and any name that starts with `_`;
- constants, arithmetic, comparison and boolean operators, lists, tuples, dictionaries and subscripts.
Refused: any other name, `lambda`, comprehensions, f-strings, starred arguments, conditional expressions, a string or
list multiplied (memory), an exponent that is not a small constant (processor time).

`evaluate_formula` runs a checked formula with empty builtins as a second layer. A formula that is allowed can still be
slow or large: nothing here stops heavy computation (spec section 15, known limit).

# @deps
# provides: function:formula_problems, function:evaluate_formula, function:function_string_problems, function:denied_methods, constant:MODULE_FUNCTIONS, constant:MATH_FUNCTIONS, class:FormulaError
# consumed_by: libs/utils/tests/test_formula_check.py
# doc: .claude/design/recipe_format_spec.md (section 15; check ST06)
# @end_deps
"""
import ast
import inspect
from functools import lru_cache
from typing import Dict, List, Set

import polars as pl

MAX_LENGTH = 2000
MAX_NODES = 400
MAX_EXPONENT = 100

# Module-level functions a formula may call. A short explicit list: extend it by an entry, with its reason.
MODULE_FUNCTIONS = frozenset({
    "col", "lit", "when", "all", "any", "len", "count", "first", "last", "nth", "exclude", "coalesce",
    "concat_str", "concat_list", "struct", "format",
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
_MATH_MODULES = ("np", "math", "numpy")

# Namespaces of an expression that a formula may use, by their name on `Expr`.
_NAMESPACES = ("str", "dt", "list", "arr", "cat", "struct", "name", "bin")


class FormulaError(ValueError):
    """A formula that the check refuses; the message holds every problem."""


def _namespace_classes() -> Dict[str, type]:
    probe = pl.col("x")
    return {name: type(getattr(probe, name)) for name in _NAMESPACES + ("meta",) if hasattr(probe, name)}


def _public(cls: type) -> Set[str]:
    return {n for n in dir(cls) if not n.startswith("_")}


def _takes_a_function(member) -> bool:
    try:
        parameters = inspect.signature(member).parameters.values()
    except (TypeError, ValueError):
        return False
    return any("Callable" in str(p.annotation) or "Callable" in repr(p.annotation) for p in parameters)


@lru_cache(maxsize=1)
def denied_methods() -> Dict[str, Set[str]]:
    """Per namespace ('expr' for Expr itself), the public methods that take a function, read from the signatures."""
    result: Dict[str, Set[str]] = {}
    for label, cls in [("expr", pl.Expr)] + list(_namespace_classes().items()):
        result[label] = {n for n in _public(cls) if callable(getattr(cls, n)) and _takes_a_function(getattr(cls, n))}
    return result


@lru_cache(maxsize=1)
def _allowed() -> Dict[str, Set[str]]:
    denied = denied_methods()
    allowed = {"expr": _public(pl.Expr) - denied["expr"]}
    for name, cls in _namespace_classes().items():
        if name == "meta":
            continue
        allowed[name] = _public(cls) - denied[name]
    return allowed


@lru_cache(maxsize=1)
def _dtypes() -> Set[str]:
    return {n for n in dir(pl) if isinstance(getattr(pl, n), type) and issubclass(getattr(pl, n), pl.DataType)}


def _fix(text: str) -> str:
    return f" Fix: {text}"


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
            if name in denied_methods()["expr"]:
                self.refuse(f"{name} runs a Python function and is not allowed")
            elif name == "meta":
                self.refuse("meta is not allowed")
            else:
                self.refuse(f"{name} is not an expression method")
            return "value"
        if kind in allowed:  # a namespace
            if name in allowed[kind]:
                return "method:" + name
            if name in denied_methods().get(kind, set()):
                self.refuse(f"{kind}.{name} runs a Python function and is not allowed")
            else:
                self.refuse(f"{kind}.{name} is not an expression method")
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
        if kind == "dtype":
            return "dtype"
        if kind == "function:when" or kind == "method:when":
            return "when"
        if kind == "method:then":
            return "then"
        return "expr"

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
        raise FormulaError(" ".join(problems))
    return eval(compile(ast.parse(text.strip(), mode="eval"), "<formula>", "eval"), dict(EVAL_GLOBALS))  # noqa: S307


# ---- the function string of a plot (`stat_function`) --------------------------------------------------------------

class _FunctionChecker(ast.NodeVisitor):
    """`lambda x: <numbers, x, arithmetic, MATH_FUNCTIONS>` or a bare MATH_FUNCTIONS name."""

    def __init__(self, argument: str) -> None:
        self.argument = argument
        self.problems: List[str] = []

    def refuse(self, what: str) -> None:
        self.problems.append(what + "." + _fix("write a lambda of one argument over numbers, the argument and "
                                               + ", ".join(sorted(MATH_FUNCTIONS)[:6]) + " and the like"))

    def generic_visit(self, node: ast.AST) -> None:
        self.refuse(f"{type(node).__name__} is not allowed in a plot function")

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            self.refuse(f"the constant {node.value!r} is not a number")

    def visit_Name(self, node: ast.Name) -> None:
        if node.id != self.argument and node.id not in MATH_CONSTANTS and node.id not in MATH_FUNCTIONS:
            self.refuse(f"the name {node.id!r} is not allowed")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        ok = isinstance(node.value, ast.Name) and node.value.id in _MATH_MODULES \
            and (node.attr in MATH_FUNCTIONS or node.attr in MATH_CONSTANTS)
        if not ok:
            self.refuse(f"the attribute {node.attr!r} is not allowed")

    def visit_Call(self, node: ast.Call) -> None:
        if node.keywords:
            self.refuse("keyword arguments are not allowed")
        func = node.func
        named = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        if named not in MATH_FUNCTIONS:
            self.refuse(f"the function {named!r} is not allowed")
        elif isinstance(func, ast.Attribute):
            self.visit_Attribute(func)
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
