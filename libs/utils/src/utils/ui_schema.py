"""
The vocabulary of `ui_schema` widgets, and the value shape each widget stands for.

# @deps
# provides: constant:WIDGETS, function:expected_shape, function:shape_problem, function:step_problems, function:schema_declaration_problems, class:StepProblem
# consumed_by: libs/utils/tests/test_step_problems.py, libs/transformer/tests/test_ui_schemas.py, libs/transformer/tests/test_action_schema_examples.py, libs/blueprint_arch/src/blueprint_arch/widget_text.py, libs/blueprint_arch/tests/test_schema_registry.py
# doc: .claude/design/recipe_format_spec.md (section 8; checks ST03, ST04, ST07, ST09, ST10, ST11; R3), .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps

Two registries (`transformer` actions, `viz_factory` components) describe their parameters with these widgets; the
Blueprint form renders them and the recipe checker tests values against them. One list here, read by all, so the
registries, the form and the checker cannot disagree.

A parameter's shape is what the recipe holds: a scalar, a list, a mapping, or a list of mappings.
"""
import difflib
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional

WIDGETS = (
    "column_selector",     # one column, or several when `multi`
    "expression",         # a Polars expression as text
    "enum",               # one of `options`, or several when `multi`
    "dtype_picker",       # a Polars dtype name
    "number",
    "string",             # plain text, a scalar
    "color",              # hex, name, or a mapping to a column or palette (Blueprint)
    "column_or_literal",  # a column name or a literal value
    "bool",
    "list",               # a YAML list; `items: mapping` when every item is a mapping
    "mapping",            # a YAML mapping, for example old name to new name
    "any",                # a value of any form; the schema `rules` (`shape`) say which form the other parameters make it
)


def expected_shape(param_def: dict) -> str:
    """'scalar', 'list', 'mapping' or 'list_of_mapping' for one parameter declaration."""
    widget = param_def.get("widget")
    if widget == "mapping":
        return "mapping"
    if widget == "any":
        return "any"
    if widget == "list":
        return "list_of_mapping" if param_def.get("items") == "mapping" else "list"
    if widget in ("column_selector", "enum") and param_def.get("multi"):
        return "list"
    return "scalar"


def shape_problem(param_def: dict, value: Any) -> Optional[str]:
    """What is wrong with a value for a `list` or `mapping` parameter, or None. Scalar widgets are not judged here."""
    shape = expected_shape(param_def)
    if shape == "mapping" and not isinstance(value, dict):
        return "write a mapping, for example {old_name: new_name}"
    if shape in ("list", "list_of_mapping"):
        if not isinstance(value, list):
            return "write a list, for example [a, b]"
        if shape == "list_of_mapping" and not all(isinstance(item, dict) for item in value):
            return "every item of the list must be a mapping, for example {matches: S, value: 0}"
    return None


# ---- the one rule set that judges a step against its action's schema -------------------------------------------

# Keys every step may carry besides the action's own parameters (spec 7.5): the author's note and the audit marker.
STEP_KEYS = ("action", "id", "comment")

# Old spellings of the column selector that the wrangler used to guess (spec 7.5, decision DEC14).
_COLUMN_ALIASES = ("column", "source", "source_column", "target_column")

_SCALAR_WIDGETS = ("string", "number", "bool", "enum", "dtype_picker", "expression", "column_selector")


@dataclass(frozen=True)
class StepProblem:
    """One problem found in one step: a check code of the catalogue, the parameter, what is wrong and the fix."""
    code: str
    param: str
    message: str
    fix: str = ""

    def text(self) -> str:
        """'what is wrong. Fix: what to write.' (the message style of spec P5)."""
        return f"{self.message}. Fix: {self.fix}" if self.fix else self.message


def _present(spec: dict, name: str) -> bool:
    return spec.get(name) is not None


def _is_reserved(key: Any) -> bool:
    return isinstance(key, str) and key.startswith("__") and key.endswith("__") and len(key) > 4


def _single_value_problem(param_def: dict, value: Any) -> Optional[str]:
    """What is wrong with a value for a scalar widget, or None."""
    widget = param_def.get("widget")
    multi = bool(param_def.get("multi"))
    if widget in ("column_selector", "enum") and multi:
        return None
    if widget not in _SCALAR_WIDGETS:
        return None
    if isinstance(value, (list, dict)):
        return "write a single value"
    if widget == "bool" and not isinstance(value, bool):
        return "write true or false"
    if widget == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
        return "write a number"
    return None


def _options_problem(param_def: dict, value: Any) -> Optional[str]:
    options = param_def.get("options")
    if param_def.get("widget") != "enum" or not options:
        return None
    values = value if param_def.get("multi") and isinstance(value, list) else [value]
    for item in values:
        if item not in options:
            return "write one of " + ", ".join(str(o) for o in options)
    return None


def _shape_label(shape: str) -> str:
    return {"list": "a list, for example [a, b]", "pair": "a list of two values, [low, high]",
            "scalar": "a single value", "mapping": "a mapping, for example {old_name: new_name}"}[shape]


def _fits(shape: str, value: Any) -> bool:
    if shape == "list":
        return isinstance(value, list)
    if shape == "pair":
        return isinstance(value, list) and len(value) == 2
    if shape == "mapping":
        return isinstance(value, dict)
    return not isinstance(value, (list, dict))


def _as_list(value: Any) -> list:
    return list(value) if isinstance(value, (list, tuple)) else [value]


def _rule_problems(spec: dict, rules: Iterable[dict]) -> List[StepProblem]:
    problems: List[StepProblem] = []
    for rule in rules:
        if "one_of" in rule:
            names = rule["one_of"]
            given = [n for n in names if _present(spec, n)]
            if len(given) != 1:
                problems.append(StepProblem(
                    "ST11", "", "exactly one of " + ", ".join(names) + " is wanted, " + (
                        "none was given" if not given else "several were given: " + ", ".join(given)),
                    "keep one of " + ", ".join(names)))
        elif "exclusive" in rule:
            names = rule["exclusive"]
            given = [n for n in names if _present(spec, n)]
            if len(given) > 1:
                problems.append(StepProblem(
                    "ST11", given[1], "these cannot be given together: " + ", ".join(given),
                    "keep only one of " + ", ".join(names)))
        elif "when" in rule:
            if not all(name in spec and spec[name] in _as_list(wanted) for name, wanted in rule["when"].items()):
                continue
            condition = ", ".join(f"{name} is {spec[name]}" for name in rule["when"])
            for name in rule.get("require", []):
                if not _present(spec, name):
                    problems.append(StepProblem("ST11", name, f"{name} is required when {condition}", f"add {name}"))
            for name in rule.get("forbid", []):
                if _present(spec, name):
                    problems.append(StepProblem("ST11", name, f"{name} cannot be given when {condition}", f"remove {name}"))
            for name, shape in rule.get("shape", {}).items():
                if _present(spec, name) and not _fits(shape, spec[name]):
                    problems.append(StepProblem(
                        "ST11", name, f"{name} has the wrong form when {condition}", f"write {_shape_label(shape)}"))
    return problems


def step_problems(action: str, spec: dict, schema: Optional[dict]) -> List[StepProblem]:
    """Every problem of one step against its action's schema, in a fixed order; an empty list means the step is sound.

    The checker (before a run) and the engine (during a run) both call this, so a recipe cannot pass one and fail
    the other. It needs the schema: the caller decides what to do about an action that has none.
    """
    if not isinstance(schema, dict):
        raise ValueError(f"action {action!r} has no schema: its parameters cannot be checked")
    params = schema.get("params", {})
    extra = set(schema.get("allowed_extra_names", ()))
    problems: List[StepProblem] = []

    for key in spec:
        if _is_reserved(key):
            problems.append(StepProblem(
                "ST09", str(key), f"{key} is an engine key and cannot be written in a recipe", f"remove {key}"))
        elif key not in params and key not in STEP_KEYS and key not in extra:
            fix = _unknown_fix(str(key), params, spec)
            problems.append(StepProblem("ST03", str(key), f"{key} is not a parameter of {action}", fix))

    for name, definition in params.items():
        if definition.get("required") and not _present(spec, name):
            problems.append(StepProblem("ST04", name, f"{name} is required by {action}", f"add {name}"))

    for name, definition in params.items():
        if not _present(spec, name):
            continue
        value = spec[name]
        if expected_shape(definition) == "list" and definition.get("widget") in ("column_selector", "enum") \
                and not isinstance(value, list):
            problems.append(StepProblem("ST07", name, f"{name} takes a list", f"write [{value}]"))
            continue
        wrong = shape_problem(definition, value) or _single_value_problem(definition, value) \
            or _options_problem(definition, value)
        if wrong:
            problems.append(StepProblem("ST10", name, f"{name} has the wrong form", wrong))

    problems.extend(_rule_problems(spec, schema.get("rules", [])))
    return problems


def _unknown_fix(key: str, params: dict, spec: dict) -> str:
    if key in _COLUMN_ALIASES and "columns" in params and "columns" not in spec:
        return "write columns"
    close = difflib.get_close_matches(key, list(params), n=1, cutoff=0.6)
    if close:
        return f"write {close[0]}"
    return "remove it, or write one of " + ", ".join(params) if params else "remove it"


# ---- the registry checks its own declarations ------------------------------------------------------------------

_RULE_FORMS = {"one_of", "exclusive", "when"}
_WHEN_KEYS = {"when", "require", "forbid", "shape"}


def schema_declaration_problems(schema: dict) -> List[str]:
    """What is wrong in a schema's own `rules`: an unknown form, or a parameter the schema does not declare."""
    params = set(schema.get("params", {}))
    found: List[str] = []
    for index, rule in enumerate(schema.get("rules", [])):
        forms = _RULE_FORMS & set(rule)
        if len(forms) != 1:
            found.append(f"rule {index} must be one of {sorted(_RULE_FORMS)}, it is {sorted(rule)}")
            continue
        if "when" in rule:
            unknown_keys = set(rule) - _WHEN_KEYS
            if unknown_keys:
                found.append(f"rule {index} has unknown keys {sorted(unknown_keys)}")
            names = list(rule["when"]) + list(rule.get("require", [])) + list(rule.get("forbid", [])) \
                + list(rule.get("shape", {}))
            for shape in rule.get("shape", {}).values():
                if shape not in ("list", "pair", "scalar", "mapping"):
                    found.append(f"rule {index} has the unknown shape {shape!r}")
        else:
            names = list(rule[next(iter(forms))])
        for name in names:
            if name not in params:
                found.append(f"rule {index} names {name}, which the schema does not declare")
    return found
