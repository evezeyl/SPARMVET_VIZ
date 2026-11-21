# engine: python-plotnine (reads the parameter list of an exact plot component from plotnine)
"""The parameter list of an `exact` plot component, read from plotnine at registration (VIZ-STANDARD-1, ADR-106 V3).

An `exact` component only passes its parameters to the plotnine object of the same name, so its list is not written by
hand: it is what plotnine accepts. A hand-written list drifts (a parameter plotnine refuses, a parameter plotnine
accepts that the form never offers); a read list follows plotnine's releases and a test compares the two.

What is read, by what the component wraps (`wraps` of its schema):

- a plotnine geom or stat class: the aesthetics and the parameters of its geom and of its stat, and the layer arguments
  (`show_legend`, `inherit_aes`, `raster`); plotnine itself accepts exactly this set (`geom._verify_arguments`).
  plotnine spells every name with `color`. A geom also accepts `colour` anywhere in a name (`rename_aesthetics`); a stat
  accepts `colour` only as the aesthetic. The list holds the `color` spelling and `canonical_name` maps the other one onto it.
- any other plotnine function or class (scales, coords, facets, labs): its signature (`utils.signature_params`).

A small hand overlay (`overlay` of the schema, keyed by parameter name) adds what plotnine does not say: the label, a
widget more exact than the type of the default, the allowed values (`options`) and a hint. It never changes what is
accepted: it cannot add a name, and it cannot state a default or a requirement (both are read). What is not exposed is
listed with its reason (`not_exposed`), never left out silently. A parameter that cannot be read, an overlay that
names a parameter plotnine does not have, or a widget that contradicts the default is an error that names the component.

# @deps
# provides: function:exact_parameters, function:accepted_names, function:canonical_name, function:is_layer, function:is_geom, class:ComponentParameterError, constant:LAYER_ARGUMENTS
# consumes: libs/utils/src/utils/signature_params.py, plotnine
# consumed_by: libs/viz_factory/src/viz_factory/registry.py, libs/viz_factory/src/viz_factory/arguments.py, libs/viz_factory/tests/test_exact_parameters_equal_plotnine.py
# doc: .claude/design/decisions_2026-11-14/viz_plan_for_eve.md (V3, V4)
# @end_deps
"""
import importlib
import inspect
import math
from typing import Any, Dict, Optional, Tuple

from plotnine.geoms.geom import geom as _Geom
from plotnine.stats.stat import stat as _Stat

from utils.signature_params import EMPTY, ParameterReadError, read_parameters

# Arguments of the layer itself, accepted by every geom and stat (plotnine `geom._verify_arguments`).
LAYER_ARGUMENTS = frozenset({"data", "mapping", "show_legend", "inherit_aes", "raster"})

# Accepted by plotnine, not offered in a recipe, and why (every `exact` layer component).
LAYER_NOT_EXPOSED = {
    "data": "the table of a layer is the plot's table (`target_dataset`); a recipe holds no table",
    "mapping": "the aesthetic mapping is written once, in the plot's `mapping:` (rules_gallery_standards section 4)",
}
# The same, by the name of a signature parameter: a Python function cannot be written in a recipe.
FUNCTION_ONLY = "takes a Python function; a recipe holds data, not code"
SIGNATURE_NOT_EXPOSED = {"rescaler": FUNCTION_ONLY, "oob": FUNCTION_ONLY}

# Keys an overlay entry may hold. `default` and `required` are not among them: plotnine says both.
OVERLAY_KEYS = frozenset({"widget", "label", "options", "hint", "multi", "items", "value_widget", "min_items", "preview"})
SIMPLE_ANNOTATIONS = {"bool": "bool", "int": "number", "float": "number", "str": "string"}


class ComponentParameterError(ValueError):
    """The parameters of a component cannot be read or its overlay contradicts plotnine; the message names the component."""


def canonical_name(name: str) -> str:
    """plotnine's spelling of a layer parameter name: `colour` anywhere in the name becomes `color`."""
    return name.replace("colour", "color")


def _wrapped(component: str, schema: Dict[str, Any]):
    wraps = schema.get("wraps") or []
    if not wraps:
        raise ComponentParameterError(f"{component}: an `exact` component must say what it wraps (`wraps`), to read its parameters from plotnine")
    try:
        obj = importlib.import_module(wraps[0]["lib"])
        for attr in wraps[0]["attr_path"]:
            obj = getattr(obj, attr)
    except (ImportError, AttributeError) as exc:
        raise ComponentParameterError(f"{component}: `wraps` names {wraps[0]} that cannot be imported ({exc})") from exc
    return obj


def is_layer(wrapped: Any) -> bool:
    return inspect.isclass(wrapped) and issubclass(wrapped, (_Geom, _Stat))


def is_geom(wrapped: Any) -> bool:
    return inspect.isclass(wrapped) and issubclass(wrapped, _Geom)


def _plain(value: Any) -> Tuple[bool, Any]:
    """(True, value) when a default can be written in a recipe and stored as plain data, else (False, None)."""
    if isinstance(value, bool) or isinstance(value, str):
        return True, value
    if isinstance(value, int) or (isinstance(value, float) and math.isfinite(value)):
        return True, value
    if isinstance(value, (tuple, list)) and all(_plain(v)[0] for v in value):
        return True, list(value)
    return False, None


def _layer_definitions(component: str, wrapped: Any) -> Dict[str, dict]:
    """{name: definition} of a geom or stat: aesthetics and parameters of its geom and stat, and the layer arguments."""
    try:
        layer = wrapped().to_layer()
    except Exception as exc:  # noqa: BLE001 - whatever plotnine raises, the component is named
        raise ComponentParameterError(f"{component}: plotnine cannot build {wrapped.__name__}() to read its parameters ({exc})") from exc
    defaults: Dict[str, Any] = {}
    for source in (layer.stat.DEFAULT_AES, layer.stat.DEFAULT_PARAMS, layer.geom.DEFAULT_AES, layer.geom.DEFAULT_PARAMS):
        defaults.update(source)  # the geom wins over the stat, as in plotnine
    names = set(layer.geom.aesthetics()) | set(layer.geom.DEFAULT_PARAMS) | set(layer.stat.aesthetics()) | set(layer.stat.DEFAULT_PARAMS)
    names = {canonical_name(n) for n in names} | (LAYER_ARGUMENTS - {"data", "mapping"}) | set(LAYER_NOT_EXPOSED)
    definitions = {}
    for name in sorted(names):
        definition: Dict[str, Any] = {"widget": "bool" if isinstance(defaults.get(name), bool) else "any", "label": name, "required": False}
        ok, value = _plain(defaults.get(name))
        if ok:
            definition["default"] = value
        definitions[name] = definition
    return definitions


def _signature_definitions(component: str, wrapped: Any) -> Dict[str, dict]:
    definitions = {}
    for p in read_parameters(wrapped, component):
        if p.variadic:
            continue
        if p.positional_only:
            raise ComponentParameterError(f"{component}: parameter {p.name!r} of the plotnine object is positional only, so a recipe cannot pass it by name")
        # The widget follows the declared type only when it is one plain type: `expand: True` would otherwise become a
        # bool widget although plotnine also takes a pair of numbers there.
        widget = SIMPLE_ANNOTATIONS.get(str(p.annotation).replace("'", "").replace(" | None", "").strip(), "any")
        definition: Dict[str, Any] = {"widget": widget, "label": p.name, "required": p.required_by_signature}
        ok, value = _plain(p.default) if p.has_default else (False, None)
        if ok:
            definition["default"] = value
        definitions[p.name] = definition
    return definitions


def accepted_names(component: str, schema: Dict[str, Any]) -> Optional[frozenset]:
    """Every name plotnine accepts for the component, or None when it takes `**kwargs` (free-form)."""
    wrapped = _wrapped(component, schema)
    if is_layer(wrapped):
        return frozenset(_layer_definitions(component, wrapped))
    parameters = read_parameters(wrapped, component)
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in parameters):
        return None
    return frozenset(p.name for p in parameters if not p.variadic)


def _check_overlay_entry(component: str, name: str, entry: Dict[str, Any], read: Dict[str, Any]) -> None:
    unknown = sorted(set(entry) - OVERLAY_KEYS)
    if unknown:
        hint = " (plotnine says the default and whether it is required; the overlay does not)" if {"default", "required"} & set(unknown) else ""
        raise ComponentParameterError(f"{component}: the overlay of {name!r} holds {unknown}, which an overlay does not carry{hint}")
    widget, default = entry.get("widget", read["widget"]), read.get("default")
    narrow = {"number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool), "bool": lambda v: isinstance(v, bool)}
    if default is not None and widget in narrow and not narrow[widget](default):
        raise ComponentParameterError(
            f"{component}: the overlay gives {name!r} the widget {widget!r}, but plotnine's default is {default!r}; "
            f"a form of that type would refuse a value plotnine accepts. Write the widget `any` or `string`")
    if widget == "enum" and default is not None and isinstance(default, str) and default not in entry.get("options", []):
        raise ComponentParameterError(f"{component}: the options of {name!r} do not contain plotnine's default {default!r}")


def exact_parameters(component: str, schema: Dict[str, Any]) -> Tuple[Dict[str, dict], Dict[str, str]]:
    """(params, not_exposed) of an `exact` component: every name plotnine accepts, minus what is not exposed, plus the overlay."""
    wrapped = _wrapped(component, schema)
    layer = is_layer(wrapped)
    try:
        read = _layer_definitions(component, wrapped) if layer else _signature_definitions(component, wrapped)
    except ParameterReadError as exc:
        raise ComponentParameterError(str(exc)) from exc
    not_exposed: Dict[str, str] = dict(LAYER_NOT_EXPOSED if layer else {k: v for k, v in SIGNATURE_NOT_EXPOSED.items() if k in read})
    for name, reason in (schema.get("not_exposed") or {}).items():
        key = canonical_name(name) if layer else name
        if key not in read:
            raise ComponentParameterError(f"{component}: `not_exposed` names {name!r}, which plotnine does not accept for it")
        if not isinstance(reason, str) or not reason.strip():
            raise ComponentParameterError(f"{component}: `not_exposed` for {name!r} needs a reason")
        not_exposed[key] = reason
    overlay: Dict[str, dict] = {}
    for name, entry in (schema.get("overlay") or {}).items():
        key = canonical_name(name) if layer else name
        if key not in read:
            raise ComponentParameterError(f"{component}: the overlay names {name!r}, which plotnine does not accept for it (accepted: {', '.join(sorted(read))})")
        if key in overlay:
            raise ComponentParameterError(f"{component}: the overlay names {key!r} twice (`color` and `colour` are one parameter)")
        _check_overlay_entry(component, key, entry, read[key])
        overlay[key] = entry
    params = {}
    for name, definition in read.items():
        if name in not_exposed:
            continue
        params[name] = {**definition, **overlay.get(name, {})}
    return params, not_exposed
