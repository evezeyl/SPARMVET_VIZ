"""
Which arguments a plot component accepts: its schema's parameters plus what the wrapped plotnine function accepts.

# @deps
# provides: function:allowed_arguments, function:unknown_arguments, function:argument_catalog
# consumes: libs/viz_factory/src/viz_factory/registry.py (COMPONENT_SCHEMAS), plotnine
# consumed_by: app/modules/data_analysis_recipe_validator.py (the recipe checker's catalogs), libs/viz_factory/tests/test_component_arguments.py
# doc: .claude/design/recipe_format_spec.md (section 8, RG5; check PS04), libs/viz_factory/README.md (allow_extra_params)
# @end_deps

Plot instructions are part of the recipe, so an unknown argument in a layer is found before the plot is drawn.
The schemas list only the common arguments and every component sets `allow_extra_params: true` on purpose (the
layer's params are passed on to plotnine), so the schema alone would refuse valid arguments such as `color`.

What a component accepts, by what it wraps (`wraps` of its schema):

- a plotnine geom or stat: only what plotnine accepts, namely the aesthetics and parameters of its geom and of its stat, and the layer arguments
  (`data`, `mapping`, `show_legend`, `inherit_aes`, `raster`). This is the rule plotnine itself applies when it
  builds the layer (`geom._verify_arguments`); `tests/test_component_arguments.py` checks every enumerated name
  against plotnine, so a plotnine release that changes the rule fails a test here.
- any other plotnine class or function (scales, themes, coords, facets, guides, positions): its signature.
- a function that takes `**kwargs` (`annotate`, `element_*`, `theme_custom`), or a component that wraps nothing:
  the names cannot be listed, `None` is returned and nothing is flagged.

The result is plain data (`argument_catalog`), so the recipe checker in `libs/utils` can receive it without
importing this library (spec section 14).
"""
import importlib
import inspect
from typing import Iterable, Optional

from plotnine.geoms.geom import geom as _Geom
from plotnine.stats.stat import stat as _Stat

from viz_factory.registry import COMPONENT_SCHEMAS

# Arguments of the layer itself, accepted by every geom and stat (plotnine `geom._verify_arguments`).
_LAYER_ARGUMENTS = frozenset({"data", "mapping", "show_legend", "inherit_aes", "raster"})


def _wrapped_object(name: str):
    wraps = COMPONENT_SCHEMAS[name].get("wraps") or []
    if not wraps:
        return None
    obj = importlib.import_module(wraps[0]["lib"])
    for attr in wraps[0]["attr_path"]:
        obj = getattr(obj, attr)
    return obj


def allowed_arguments(name: str) -> Optional[frozenset]:
    """The argument names a component accepts, or None when they cannot be listed (free-form). KeyError if unknown."""
    schema = COMPONENT_SCHEMAS[name]
    declared = frozenset((schema.get("params") or {}))
    wrapped = _wrapped_object(name)
    if wrapped is None:
        return None
    if inspect.isclass(wrapped) and issubclass(wrapped, (_Geom, _Stat)):
        # Only what plotnine accepts, not the schema: a schema parameter that plotnine refuses (13 today, issue #88)
        # makes the plot fail, so it must not be reported as valid.
        layer = wrapped().to_layer()
        return _LAYER_ARGUMENTS | frozenset(
            set(layer.geom.aesthetics()) | set(layer.geom.DEFAULT_PARAMS)
            | set(layer.stat.aesthetics()) | set(layer.stat.DEFAULT_PARAMS)
        )
    try:
        parameters = inspect.signature(wrapped).parameters.values()
    except (TypeError, ValueError):
        return None
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in parameters):
        return None
    return declared | frozenset(p.name for p in parameters if p.kind is not inspect.Parameter.VAR_POSITIONAL)


def unknown_arguments(name: str, names: Iterable[str]) -> list:
    """The given argument names that the component does not accept (empty for a free-form component)."""
    allowed = allowed_arguments(name)
    if allowed is None:
        return []
    return [n for n in names if n not in allowed]


def argument_catalog() -> dict:
    """{component: sorted argument names, or None when free-form}: plain data for the recipe checker."""
    catalog = {}
    for name in sorted(COMPONENT_SCHEMAS):
        allowed = allowed_arguments(name)
        catalog[name] = None if allowed is None else sorted(allowed)
    return catalog
