"""Which arguments a plot component accepts: the schema's parameters plus what the wrapped plotnine function accepts.

Plot instructions are part of the recipe, so an unknown argument in a layer must be found before the plot is drawn
(check PS04 of the recipe format specification, section 8, R5). The schemas list only the common arguments and every
component sets `allow_extra_params: true` on purpose (the spec dict is passed to plotnine), so the schema alone would
refuse valid arguments such as `color`. Plotnine is the oracle: for geoms and stats the enumerated names are checked
against plotnine's own acceptance.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_component_arguments.py -q
"""
import importlib
import inspect
import json

import pytest
from plotnine.exceptions import PlotnineError
from plotnine.geoms.geom import geom as Geom
from plotnine.stats.stat import stat as Stat

import viz_factory  # noqa: F401  (loads the registry)
from viz_factory.arguments import allowed_arguments, argument_catalog, unknown_arguments
from viz_factory.registry import COMPONENT_SCHEMAS

BOGUS = "zzz_not_an_argument"


def _wrapped(name):
    wraps = (COMPONENT_SCHEMAS[name].get("wraps") or [None])[0]
    if not wraps:
        return None
    obj = importlib.import_module(wraps["lib"])
    for attr in wraps["attr_path"]:
        obj = getattr(obj, attr)
    return obj


def _layer_components():
    return sorted(n for n in COMPONENT_SCHEMAS
                  if inspect.isclass(_wrapped(n) or 0) and issubclass(_wrapped(n), (Geom, Stat)))


def _plotnine_rejects(cls, argument):
    """Ask plotnine itself: geoms check at construction, stats when their layer is made."""
    try:
        cls(**{argument: None}).to_layer()
        return False
    except PlotnineError as err:
        return "not understood" in str(err)
    except Exception:  # noqa: BLE001  (a value problem, not a name problem)
        return False


def test_color_and_colour_are_accepted_and_an_invented_name_is_not():
    assert unknown_arguments("geom_point", ["color", "colour", "alpha", "size"]) == []
    assert unknown_arguments("geom_point", ["color", BOGUS]) == [BOGUS]


def test_arguments_shipped_recipes_use_are_accepted():
    """The 10 layer parameters of the shipped recipes that are outside the schemas (all valid plotnine arguments)."""
    used = {"geom_boxplot": ["outlier_alpha"], "geom_line": ["color"], "geom_point": ["color"], "geom_segment": ["color"],
            "geom_smooth": ["color"], "geom_text": ["color"], "geom_tile": ["color"], "stat_ecdf": ["size"]}
    for component, names in used.items():
        assert unknown_arguments(component, names) == [], component


def test_a_fixed_signature_component_accepts_its_signature_and_its_schema():
    assert unknown_arguments("coord_flip", ["expand"]) == []
    assert unknown_arguments("coord_flip", [BOGUS]) == [BOGUS]


def test_a_free_form_component_cannot_be_enumerated_and_flags_nothing():
    for name in ("annotate", "element_text", "theme_custom"):
        assert allowed_arguments(name) is None
        assert unknown_arguments(name, [BOGUS]) == []


def test_an_unknown_component_is_a_key_error():
    with pytest.raises(KeyError):
        allowed_arguments("geom_does_not_exist")


@pytest.mark.parametrize("name", _layer_components())
def test_the_enumerated_names_of_a_geom_or_stat_agree_with_plotnine(name):
    cls = _wrapped(name)
    allowed = allowed_arguments(name)
    assert allowed, name
    assert BOGUS not in allowed
    rejected = sorted(a for a in allowed if _plotnine_rejects(cls, a))
    assert rejected == [], f"{name}: plotnine refuses {rejected}"
    assert _plotnine_rejects(cls, BOGUS), f"{name}: plotnine should refuse an invented name"


def test_the_catalog_has_every_component_and_is_plain_data():
    catalog = argument_catalog()
    assert set(catalog) == set(COMPONENT_SCHEMAS)
    assert json.loads(json.dumps(catalog)) == catalog
    assert catalog["geom_point"] == sorted(catalog["geom_point"])
    assert catalog["annotate"] is None


# Schema parameters that plotnine refuses (the form offers them and the plot fails): ggplot2 names, not plotnine's.
# A ratchet: a new wrong declaration fails the test, and fixing one forces this list to shrink. Issue #88.
KNOWN_REFUSED_SCHEMA_PARAMETERS = {
    "geom_density_2d": ["contour_var"],
    "geom_label": ["fontface", "hjust", "vjust"],
    "geom_quantile": ["method"],
    "geom_rug": ["outside"],
    "geom_text": ["check_overlap", "fontface", "hjust", "vjust"],
    "stat_density_2d": ["adjust", "h"],
    "stat_quantile": ["method"],
}


def test_the_schema_parameters_of_geoms_and_stats_are_accepted_by_plotnine():
    refused = {}
    for name in _layer_components():
        cls = _wrapped(name)
        bad = sorted(p for p in COMPONENT_SCHEMAS[name]["params"] if _plotnine_rejects(cls, p))
        if bad:
            refused[name] = bad
    assert refused == KNOWN_REFUSED_SCHEMA_PARAMETERS


def test_a_refused_schema_parameter_is_reported_as_unknown_by_the_checker_data():
    assert unknown_arguments("geom_text", ["hjust"]) == ["hjust"]
