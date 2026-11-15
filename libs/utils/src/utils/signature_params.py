"""Read the parameters of a wrapped object from its signature (one source for the Polars actions and the plotnine components).

A registry entry that wraps a library call (a `polars_` action, an `exact` plot component) does not write the parameter
list by hand: the names and defaults come from the wrapped object, so a library release that adds, renames or removes a
parameter shows up here instead of being missed. What is specific to one library (which names are renamed, merged or not
exposed, which widget a name gets) stays in the registry that wraps it; this module only reads and says what it cannot read.

# @deps
# provides: function:read_parameters, function:call_arguments, function:widget_for_default, class:ReadParameter, class:ParameterReadError
# consumed_by: libs/transformer/src/transformer/actions/polars_calls.py, libs/viz_factory/src/viz_factory/parameters.py, libs/utils/tests/test_signature_params.py
# doc: .claude/design/decisions_2026-11-14/viz_plan_for_eve.md (V3)
# @end_deps
"""
import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

EMPTY = inspect.Parameter.empty


class ParameterReadError(ValueError):
    """The parameters of a wrapped object cannot be read; the message names the registry entry (`owner`)."""


@dataclass(frozen=True)
class ReadParameter:
    """One parameter of a wrapped object: `source` is its name in the signature, `name` the name a recipe writes."""
    source: str
    name: str
    kind: Any
    default: Any

    @property
    def has_default(self) -> bool:
        return self.default is not EMPTY

    @property
    def variadic(self) -> bool:
        return self.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)

    @property
    def positional_only(self) -> bool:
        return self.kind is inspect.Parameter.POSITIONAL_ONLY

    @property
    def required_by_signature(self) -> bool:
        """No default and not `*args` / `**kwargs`: the wrapped call fails without it."""
        return not self.has_default and not self.variadic


def read_parameters(target: Any, owner: str, rename: Optional[Mapping[str, str]] = None) -> List[ReadParameter]:
    """Every parameter of `target` in signature order (`self` and `cls` left out), under the recipe name `rename` gives it.

    `owner` is the registry entry that wraps `target` (an action or a component name): an object whose signature cannot
    be read raises `ParameterReadError` naming it, never an empty list.
    """
    rename = rename or {}
    try:
        parameters = inspect.signature(target).parameters
    except (TypeError, ValueError) as exc:
        raise ParameterReadError(f"{owner}: the parameters of {target!r} cannot be read from its signature ({exc})") from exc
    return [ReadParameter(source, rename.get(source, source), p.kind, p.default)
            for source, p in parameters.items() if source not in ("self", "cls")]


def call_arguments(target: Any, spec: Mapping[str, Any], owner: str, rename: Optional[Mapping[str, str]] = None,
                   skip: Tuple[str, ...] = ()) -> Dict[str, Any]:
    """The keyword arguments of the call: every parameter the step gave (not None), under its name in the signature.

    `**kwargs` and the parameters in `skip` (signature names) are not read from the step.
    """
    out = {}
    for p in read_parameters(target, owner, rename):
        if p.kind is inspect.Parameter.VAR_KEYWORD or p.source in skip or spec.get(p.name) is None:
            continue
        out[p.source] = spec[p.name]
    return out


def widget_for_default(default: Any) -> Optional[str]:
    """`bool` or `number` for a default of that type, else None (the registry decides what the rest gets)."""
    if isinstance(default, bool):
        return "bool"
    if isinstance(default, (int, float)):
        return "number"
    return None
