"""A schema that breaks the rules of an `exact` component is refused at registration, with the component named.

Each test registers a bad schema through the decorator itself (`register_plot_component`), as a component file would,
and expects the error; the registries must be left as they were. One test per rule of `registry._read_exact_parameters`
and `parameters.exact_parameters` (VIZ-STANDARD-1, ADR-106 V3).

# @deps
# consumes: libs/viz_factory/src/viz_factory/registry.py, libs/viz_factory/src/viz_factory/parameters.py
# @end_deps
"""
import copy

import pytest

import viz_factory  # noqa: F401  (registers the components)
from viz_factory.parameters import ComponentParameterError
from viz_factory.registry import COMPONENT_SCHEMAS, PLOT_COMPONENTS, register_plot_component

NAME = "geom_point_registration_probe"


def exact_schema(**change):
    """The schema of geom_point as written in the component file (overlay, no params), with `change` applied."""
    base = {k: copy.deepcopy(v) for k, v in COMPONENT_SCHEMAS["geom_point"].items() if k not in ("params", "not_exposed")}
    return {**base, **change}


def modified_schema(**change):
    base = {k: copy.deepcopy(v) for k, v in COMPONENT_SCHEMAS["geom_jitter"].items()}
    return {**base, **change}


def register(schema):
    @register_plot_component(NAME, ui_schema=schema)
    def probe(p, spec):
        return p
    return probe


@pytest.fixture(autouse=True)
def registries_untouched():
    before = (set(PLOT_COMPONENTS), set(COMPONENT_SCHEMAS))
    yield
    assert (set(PLOT_COMPONENTS), set(COMPONENT_SCHEMAS)) == before, "a refused schema left a trace in a registry"


def test_a_good_exact_schema_registers_and_is_filled_in_from_plotnine():
    register(exact_schema())
    try:
        assert "na_rm" in COMPONENT_SCHEMAS[NAME]["params"] and "data" in COMPONENT_SCHEMAS[NAME]["not_exposed"]
    finally:
        PLOT_COMPONENTS.pop(NAME, None)
        COMPONENT_SCHEMAS.pop(NAME, None)


def test_an_exact_component_with_a_hand_written_params_list_is_refused():
    with pytest.raises(ComponentParameterError, match=f"{NAME}.*does not write `params`"):
        register(exact_schema(params={"size": {"widget": "number", "label": "Size"}}))


def test_an_exact_component_with_a_wrong_wraps_is_refused():
    with pytest.raises(ComponentParameterError, match=f"{NAME}.*cannot be imported"):
        register(exact_schema(wraps=[{"lib": "plotnine", "attr_path": ["geom_nope"]}]))
    with pytest.raises(ComponentParameterError, match=f"{NAME}.*wraps"):
        register(exact_schema(wraps=[]))


def test_an_overlay_naming_a_parameter_plotnine_does_not_accept_is_refused():
    with pytest.raises(ComponentParameterError, match=f"{NAME}.*'zzz'"):
        register(exact_schema(overlay={"zzz": {"widget": "number", "label": "z"}}))


def test_an_overlay_stating_a_default_or_a_requirement_is_refused():
    for key, value in (("default", 3), ("required", True)):
        with pytest.raises(ComponentParameterError, match=f"{NAME}.*{key}"):
            register(exact_schema(overlay={"size": {"widget": "number", "label": "Size", key: value}}))


def test_a_widget_contradicting_plotnines_default_is_refused():
    with pytest.raises(ComponentParameterError, match=f"{NAME}.*'shape'.*'o'"):
        register(exact_schema(overlay={"shape": {"widget": "number", "label": "Shape"}}))


def test_a_not_exposed_entry_without_a_reason_is_refused():
    with pytest.raises(ComponentParameterError, match=f"{NAME}.*'size'.*reason"):
        register(exact_schema(not_exposed={"size": ""}))


@pytest.mark.parametrize("kind", ["modified", "own"])
@pytest.mark.parametrize("key, value", [("overlay", {"alpha": {"widget": "number", "label": "a"}}), ("not_exposed", {"size": "a reason that explains it"})])
def test_an_overlay_or_not_exposed_on_a_modified_or_own_component_is_refused(kind, key, value):
    with pytest.raises(ComponentParameterError, match=f"{NAME}.*belong to an `exact` component"):
        register(modified_schema(plotnine=kind, **{key: value}))


def test_a_modified_component_with_its_own_params_is_accepted():
    schema = modified_schema()
    register(schema)
    try:
        assert COMPONENT_SCHEMAS[NAME]["params"] == schema["params"]
    finally:
        PLOT_COMPONENTS.pop(NAME, None)
        COMPONENT_SCHEMAS.pop(NAME, None)
