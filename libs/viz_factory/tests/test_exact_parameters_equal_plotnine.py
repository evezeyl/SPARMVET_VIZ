"""The parameters of an `exact` component are what plotnine accepts (VIZ-STANDARD-1, ADR-106 V3).

Driven by the registry: every component whose schema says `plotnine: exact` is compared with plotnine itself. The oracle
here is written apart from the code under test (`viz_factory.parameters`): it reads the signature, `DEFAULT_PARAMS`, the
aesthetics and the defaults of plotnine directly, and it asks plotnine whether it accepts a name by building the layer.

  declared parameters == what plotnine accepts - what the schema lists as not exposed (with a reason)

so a parameter plotnine refuses, a parameter plotnine accepts that the form never offers, and a default that plotnine
does not use each fail a test. `modified` and `own` components keep their own hand-written list.

# @deps
# consumes: libs/viz_factory/src/viz_factory/parameters.py, libs/viz_factory/src/viz_factory/registry.py, plotnine
# doc: .claude/design/decisions_2026-11-14/viz_plan_for_eve.md (V3)
# @end_deps
"""
import importlib
import inspect
import math

import plotnine
import pytest
from plotnine.exceptions import PlotnineError
from plotnine.geoms.geom import geom as Geom
from plotnine.stats.stat import stat as Stat

import viz_factory  # noqa: F401  (loads the registry)
from utils.signature_params import ParameterReadError
from utils.ui_schema import WIDGETS
from viz_factory.parameters import ComponentParameterError, accepted_names, canonical_name, exact_parameters
from viz_factory.registry import COMPONENT_SCHEMAS

EXACT = sorted(n for n, s in COMPONENT_SCHEMAS.items() if s["plotnine"] == "exact")
NOT_EXACT = sorted(n for n, s in COMPONENT_SCHEMAS.items() if s["plotnine"] != "exact")
LAYER_ARGUMENTS = {"data", "mapping", "show_legend", "inherit_aes", "raster"}


def wrapped(name):
    entry = COMPONENT_SCHEMAS[name]["wraps"][0]
    obj = importlib.import_module(entry["lib"])
    for attr in entry["attr_path"]:
        obj = getattr(obj, attr)
    return obj


def is_layer(obj):
    return inspect.isclass(obj) and issubclass(obj, (Geom, Stat))


def plotnine_names_and_defaults(name):
    """What plotnine accepts for the component, with its defaults: read straight from plotnine (the oracle)."""
    obj = wrapped(name)
    if is_layer(obj):
        layer = obj().to_layer()
        names = (set(layer.geom.aesthetics()) | set(layer.geom.DEFAULT_PARAMS) | set(layer.stat.aesthetics())
                 | set(layer.stat.DEFAULT_PARAMS))
        defaults = {**layer.stat.DEFAULT_AES, **layer.stat.DEFAULT_PARAMS, **layer.geom.DEFAULT_AES, **layer.geom.DEFAULT_PARAMS}
        return ({n.replace("colour", "color") for n in names} | LAYER_ARGUMENTS,
                {k.replace("colour", "color"): v for k, v in defaults.items()}, set())
    parameters = inspect.signature(obj).parameters
    kinds = (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    names = {n for n, p in parameters.items() if p.kind not in kinds}
    defaults = {n: p.default for n, p in parameters.items() if p.default is not inspect.Parameter.empty}
    required = {n for n, p in parameters.items() if p.default is inspect.Parameter.empty and p.kind not in kinds}
    return names, defaults, required


def plotnine_accepts(name, argument):
    obj = wrapped(name)
    if is_layer(obj):
        try:
            obj(**{argument: None}).to_layer()
            return True
        except PlotnineError as err:
            return "not understood" not in str(err)
        except Exception:  # noqa: BLE001  (a value problem, not a name problem)
            return True
    return argument in inspect.signature(obj).parameters


def same(a, b):
    if isinstance(b, (tuple, list)):
        return list(a) == list(b)
    return a == b


def test_there_are_exact_components_to_compare():
    assert len(EXACT) >= 100


@pytest.mark.parametrize("name", EXACT)
def test_the_declared_parameters_are_exactly_what_plotnine_accepts_less_what_is_not_exposed(name):
    schema = COMPONENT_SCHEMAS[name]
    accepted, _, _ = plotnine_names_and_defaults(name)
    not_exposed = schema.get("not_exposed") or {}
    declared = set(schema["params"])
    assert declared == accepted - set(not_exposed), (
        f"{name}: declared but refused by plotnine {sorted(declared - accepted)}; "
        f"accepted by plotnine, neither declared nor listed as not exposed {sorted(accepted - declared - set(not_exposed))}")
    assert set(not_exposed) <= accepted, f"{name}: not_exposed lists names plotnine does not accept"
    assert all(isinstance(r, str) and len(r.strip()) >= 20 for r in not_exposed.values()), f"{name}: a not_exposed entry needs a reason"


@pytest.mark.parametrize("name", EXACT)
def test_every_declared_name_is_accepted_by_plotnine_when_asked(name):
    """Not only by the lists above: plotnine itself is asked, one name at a time."""
    refused = [p for p in COMPONENT_SCHEMAS[name]["params"] if not plotnine_accepts(name, p)]
    assert refused == []


@pytest.mark.parametrize("name", EXACT)
def test_defaults_and_required_are_plotnines_not_a_hand_written_claim(name):
    _, defaults, required = plotnine_names_and_defaults(name)
    wrong = []
    for param, definition in COMPONENT_SCHEMAS[name]["params"].items():
        assert definition["widget"] in WIDGETS and definition["label"], f"{name}.{param}"
        if "default" in definition and not same(definition["default"], defaults.get(param)):
            wrong.append((param, definition["default"], defaults.get(param)))
        if "default" not in definition and isinstance(defaults.get(param), (bool, str)):
            wrong.append((param, "missing", defaults[param]))
        if bool(definition["required"]) != (param in required):
            wrong.append((param, "required", definition["required"]))
        d = definition.get("default")
        if isinstance(d, float):
            assert math.isfinite(d)
    assert wrong == []


@pytest.mark.parametrize("name", EXACT)
def test_the_overlay_carries_no_default_and_no_requirement_and_names_only_accepted_parameters(name):
    accepted, _, _ = plotnine_names_and_defaults(name)
    for param, entry in (COMPONENT_SCHEMAS[name].get("overlay") or {}).items():
        assert canonical_name(param) in accepted, f"{name}: overlay names {param!r}, which plotnine does not accept"
        assert not {"default", "required"} & set(entry), f"{name}.{param}: plotnine says the default and the requirement"


@pytest.mark.parametrize("name", NOT_EXACT)
def test_a_modified_or_own_component_keeps_its_own_list_and_has_no_overlay(name):
    schema = COMPONENT_SCHEMAS[name]
    assert "overlay" not in schema and "not_exposed" not in schema
    assert isinstance(schema.get("params"), dict)


def test_the_accepted_names_of_the_library_agree_with_the_oracle():
    wrong = {}
    for name in EXACT:
        names = accepted_names(name, COMPONENT_SCHEMAS[name])
        oracle, _, _ = plotnine_names_and_defaults(name)
        if names != oracle:
            wrong[name] = (sorted(names - oracle), sorted(oracle - names))
    assert wrong == {}


# -- the registration errors name the component ----------------------------------------------------------------------

def schema_of(name, **change):
    base = {k: v for k, v in COMPONENT_SCHEMAS[name].items() if k not in ("params", "not_exposed", "overlay")}
    return {**base, **change}


def test_an_overlay_naming_a_parameter_plotnine_does_not_accept_is_an_error_that_names_the_component():
    with pytest.raises(ComponentParameterError, match="geom_point.*'zzz'"):
        exact_parameters("geom_point", schema_of("geom_point", overlay={"zzz": {"widget": "number", "label": "z"}}))


def test_an_overlay_cannot_state_a_default_or_a_requirement():
    for key, value in (("default", 3), ("required", True)):
        with pytest.raises(ComponentParameterError, match=f"geom_point.*{key}"):
            exact_parameters("geom_point", schema_of("geom_point", overlay={"size": {"widget": "number", "label": "s", key: value}}))


def test_a_widget_that_contradicts_plotnines_default_is_an_error():
    with pytest.raises(ComponentParameterError, match="geom_point.*'shape'.*'o'"):
        exact_parameters("geom_point", schema_of("geom_point", overlay={"shape": {"widget": "number", "label": "shape"}}))
    with pytest.raises(ComponentParameterError, match="geom_point.*'size'"):
        exact_parameters("geom_point", schema_of("geom_point", overlay={"size": {"widget": "bool", "label": "size"}}))


def test_enum_options_must_contain_plotnines_default():
    with pytest.raises(ComponentParameterError, match="geom_point.*'stat'.*identity"):
        exact_parameters("geom_point", schema_of("geom_point", overlay={"stat": {"widget": "enum", "label": "stat", "options": ["count"]}}))


def test_both_spellings_of_colour_in_one_overlay_are_an_error():
    with pytest.raises(ComponentParameterError, match="geom_point.*twice"):
        exact_parameters("geom_point", schema_of("geom_point", overlay={"colour": {"widget": "color", "label": "a"},
                                                                        "color": {"widget": "color", "label": "b"}}))


def test_the_colour_spelling_of_an_overlay_entry_describes_the_color_parameter():
    params, _ = exact_parameters("geom_point", schema_of("geom_point", overlay={"colour": {"widget": "color", "label": "Point colour"}}))
    assert params["color"]["label"] == "Point colour" and "colour" not in params


def test_not_exposed_must_name_an_accepted_parameter_and_give_a_reason():
    with pytest.raises(ComponentParameterError, match="geom_point.*'zzz'"):
        exact_parameters("geom_point", schema_of("geom_point", not_exposed={"zzz": "because"}))
    with pytest.raises(ComponentParameterError, match="geom_point.*'size'.*reason"):
        exact_parameters("geom_point", schema_of("geom_point", not_exposed={"size": " "}))


def test_a_listed_not_exposed_parameter_is_left_out_with_its_reason():
    params, not_exposed = exact_parameters("geom_point", schema_of("geom_point", not_exposed={"size": "a reason that explains it"}))
    assert "size" not in params and not_exposed["size"] == "a reason that explains it"
    assert {"data", "mapping"} <= set(not_exposed)


def test_an_exact_component_without_wraps_or_with_a_wrong_wraps_is_an_error_that_names_it():
    with pytest.raises(ComponentParameterError, match="geom_point.*wraps"):
        exact_parameters("geom_point", schema_of("geom_point", wraps=[]))
    with pytest.raises(ComponentParameterError, match="geom_point.*cannot be imported"):
        exact_parameters("geom_point", schema_of("geom_point", wraps=[{"lib": "plotnine", "attr_path": ["geom_nope"]}]))


def test_an_object_whose_signature_cannot_be_read_is_an_error_that_names_the_component(monkeypatch):
    def broken(*args, **kwargs):
        raise ValueError("no signature found")
    monkeypatch.setattr(inspect, "signature", broken)
    with pytest.raises((ComponentParameterError, ParameterReadError), match="coord_flip"):
        exact_parameters("coord_flip", schema_of("coord_flip"))


def test_a_geom_plotnine_cannot_build_is_an_error_that_names_the_component(monkeypatch):
    monkeypatch.setattr(plotnine.geom_point, "to_layer", lambda self: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(ComponentParameterError, match="geom_point.*boom"):
        exact_parameters("geom_point", schema_of("geom_point"))


# -- the list follows plotnine: it is read, not copied ----------------------------------------------------------------

def test_a_parameter_plotnine_adds_appears_without_any_change_here(monkeypatch):
    monkeypatch.setitem(plotnine.geom_point.DEFAULT_PARAMS, "brand_new_parameter", 7)
    params, _ = exact_parameters("geom_point", schema_of("geom_point"))
    assert params["brand_new_parameter"]["default"] == 7
    assert "brand_new_parameter" in accepted_names("geom_point", COMPONENT_SCHEMAS["geom_point"])


def test_a_parameter_plotnine_removes_disappears_and_an_overlay_for_it_fails(monkeypatch):
    monkeypatch.delitem(plotnine.geom_boxplot.DEFAULT_PARAMS, "notch")
    params, _ = exact_parameters("geom_boxplot", schema_of("geom_boxplot"))
    assert "notch" not in params
    with pytest.raises(ComponentParameterError, match="geom_boxplot.*'notch'"):
        exact_parameters("geom_boxplot", schema_of("geom_boxplot", overlay={"notch": {"widget": "bool", "label": "x"}}))


def test_the_widget_follows_a_plain_type_and_stays_open_otherwise():
    params = COMPONENT_SCHEMAS["geom_point"]["params"]
    assert params["na_rm"]["widget"] == "bool" and params["na_rm"]["default"] is False
    assert COMPONENT_SCHEMAS["coord_cartesian"]["params"]["expand"]["widget"] == "bool"  # plotnine annotates it `bool`
    breaks = COMPONENT_SCHEMAS["scale_x_log10"]["params"]["breaks"]
    assert breaks["widget"] == "string"  # the overlay chose this one; read alone it is `any`, plotnine types it as a union
    assert COMPONENT_SCHEMAS["scale_x_log10"]["params"]["minor_breaks"]["widget"] == "any"
    assert COMPONENT_SCHEMAS["scale_color_manual"]["params"]["values"]["required"] is True


def test_a_function_valued_parameter_is_not_exposed_with_its_reason():
    schema = COMPONENT_SCHEMAS["scale_x_log10"]
    assert "oob" not in schema["params"] and "rescaler" not in schema["params"]
    assert "function" in schema["not_exposed"]["oob"]
