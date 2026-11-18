"""Every registered plot component carries the field `engine` (D-0238), and the library names its engine in one small entry file (D-0247).

The field is stored by the registering decorator, next to the form schema. A name with the prefix of an engine (`plotnine_`,
none registered yet: the rename is on hold) and another engine in the field is a fault; `modif_` and `step_` carry the engine in
the field only. The entry file `engine_python_plotnine.py` names the engine and exposes ENTRY, the factory the app calls.

# @deps
# consumes: libs/viz_factory/src/viz_factory/registry.py, libs/viz_factory/src/viz_factory/engine_python_plotnine.py, libs/utils/src/utils/engines.py
# doc: .claude/knowledge/decision_ledger.md (D-0238, D-0247)
# @end_deps
"""
import importlib

import pytest

import viz_factory  # noqa: F401  (importing it registers the components)
from viz_factory import registry
from utils import engines


def test_every_registered_component_has_an_engine_and_no_engine_belongs_to_a_name_that_is_not_registered():
    assert registry.PLOT_COMPONENTS, "no component registered: the test would prove nothing"
    assert set(registry.COMPONENT_ENGINES) == set(registry.PLOT_COMPONENTS)


def test_every_engine_of_a_component_is_a_plot_engine_the_app_has():
    assert set(registry.COMPONENT_ENGINES.values()) <= set(engines.engines_of("plot_engine"))


def test_the_field_and_the_prefix_agree_for_every_component():
    assert engines.prefix_problems(registry.COMPONENT_ENGINES) == []


def test_the_modif_and_step_components_carry_the_engine_in_the_field():
    named = [n for n in registry.COMPONENT_ENGINES if n.startswith(("modif_", "step_"))]
    for name in named:
        assert registry.COMPONENT_ENGINES[name] == "python-plotnine", name


# -- the decorator --------------------------------------------------------------------------------------------------------------

@pytest.fixture
def scratch_registry():
    before = (dict(registry.PLOT_COMPONENTS), dict(registry.COMPONENT_SCHEMAS), dict(registry.COMPONENT_ENGINES))
    yield
    for reg, saved in zip((registry.PLOT_COMPONENTS, registry.COMPONENT_SCHEMAS, registry.COMPONENT_ENGINES), before):
        reg.clear()
        reg.update(saved)
    registry._CHECKED.clear()


def test_the_decorator_stores_the_engine_of_the_library_when_none_is_written(scratch_registry):
    registry.register_plot_component("scratch_demo")(lambda p, spec: p)
    assert registry.COMPONENT_ENGINES["scratch_demo"] == "python-plotnine"


def test_the_decorator_stores_the_engine_it_is_given(scratch_registry, monkeypatch):
    monkeypatch.setattr(engines, "ENGINES", {**engines.ENGINES, "plot_engine": ("python-plotnine", "python-other")})
    registry.register_plot_component("scratch_other", engine="python-other")(lambda p, spec: p)
    assert registry.COMPONENT_ENGINES["scratch_other"] == "python-other"


def test_an_engine_the_app_has_no_library_for_cannot_be_registered(scratch_registry):
    with pytest.raises(ValueError) as caught:
        registry.register_plot_component("scratch_bad", engine="r-ggplot2")(lambda p, spec: p)
    assert "no library for this engine in this app" in str(caught.value) and "scratch_bad" in str(caught.value)
    assert "scratch_bad" not in registry.PLOT_COMPONENTS and "scratch_bad" not in registry.COMPONENT_ENGINES


def test_an_engine_written_empty_cannot_be_registered(scratch_registry):
    with pytest.raises(ValueError):
        registry.register_plot_component("scratch_empty", engine=None)(lambda p, spec: p)
    assert "scratch_empty" not in registry.PLOT_COMPONENTS


def test_a_refused_schema_leaves_no_engine_behind(scratch_registry):
    with pytest.raises(Exception):
        registry.register_plot_component("scratch_bad_schema", ui_schema={"plotnine": "exact", "params": {}})(lambda p, spec: p)
    assert "scratch_bad_schema" not in registry.COMPONENT_ENGINES


# -- the entry file -------------------------------------------------------------------------------------------------------------

def test_the_entry_file_exists_names_its_engine_and_exposes_entry():
    module = importlib.import_module("viz_factory." + engines.entry_module_name("python-plotnine"))
    assert module.ENTRY.engine == "python-plotnine" == engines.PLOT_ENGINE
    from viz_factory.viz_factory import VizFactory
    assert module.ENTRY.factory is VizFactory
    assert isinstance(module.ENTRY, engines.PlotEngineEntry)


def test_the_entry_file_is_the_file_the_table_names():
    row = next(r for r in engines.ENGINE_TABLE if r.engine == "python-plotnine")
    assert row.library == "viz_factory"
    module = importlib.import_module(f"{row.library}.{engines.entry_module_name(row.engine)}")
    assert module.__name__ == "viz_factory.engine_python_plotnine"
