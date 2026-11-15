"""
Which arguments a plot component accepts: its schema's parameters plus what the wrapped plotnine function accepts.

# @deps
# provides: function:allowed_arguments, function:unknown_arguments, function:argument_catalog
# consumes: libs/viz_factory/src/viz_factory/registry.py (COMPONENT_SCHEMAS), libs/viz_factory/src/viz_factory/parameters.py (accepted_names), plotnine
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
from typing import Iterable, Optional

from viz_factory.parameters import accepted_names, is_geom, is_layer
from viz_factory.registry import COMPONENT_SCHEMAS


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
    wrapped = _wrapped_object(name)
    if wrapped is None:
        return None
    # One reading of plotnine for the schema and for the checker (`viz_factory.parameters`): the list a form offers and
    # the names the checker accepts cannot drift apart.
    accepted = accepted_names(name, schema)
    if accepted is None:
        return None
    if is_layer(wrapped):
        # a geom accepts `colour` wherever it accepts `color` (it renames the spelling on the way in); a stat only as the aesthetic
        return accepted | frozenset(n.replace("color", "colour") for n in accepted if "color" in n and (is_geom(wrapped) or n == "color"))
    return frozenset(schema.get("params") or {}) | accepted


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
