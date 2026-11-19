"""Every registered action carries the field `engine` (D-0238), and the library names its engine in one small entry file (D-0247).

The field is stored by the registering decorator, next to the form schema. A name with the prefix of an engine (`polars_`)
and another engine in the field is a fault; `modif_` and `step_` carry the engine in the field only. The entry file
`engine_python_polars.py` names the engine and exposes ENTRY, the classes the app calls to run the tiers of a recipe.

# @deps
# consumes: libs/transformer/src/transformer/actions/base.py, libs/transformer/src/transformer/engine_python_polars.py, libs/utils/src/utils/engines.py
# doc: .claude/knowledge/decision_ledger.md (D-0238, D-0247)
# @end_deps
"""
import importlib

import pytest

import transformer.actions  # noqa: F401  (importing it registers the actions)
from transformer.actions import base
from utils import engines


def test_every_registered_action_has_an_engine_and_no_engine_belongs_to_a_name_that_is_not_registered():
    assert base.AVAILABLE_WRANGLING_ACTIONS, "no action registered: the test would prove nothing"
    assert set(base.ACTION_ENGINES) == set(base.AVAILABLE_WRANGLING_ACTIONS)


def test_every_engine_of_an_action_is_a_data_engine_the_app_has():
    assert set(base.ACTION_ENGINES.values()) <= set(engines.engines_of("data_engine"))


def test_the_field_and_the_prefix_agree_for_every_action():
    assert engines.prefix_problems(base.ACTION_ENGINES) == []


def test_the_actions_with_a_prefix_exist_and_the_modif_and_step_ones_carry_the_engine_in_the_field():
    names = list(base.ACTION_ENGINES)
    assert any(n.startswith("polars_") for n in names)
    assert any(n.startswith("modif_") for n in names) and any(n.startswith("step_") for n in names)
    for name in names:
        if name.startswith(("modif_", "step_")):
            assert base.ACTION_ENGINES[name] == "python-polars", name


# -- the decorator --------------------------------------------------------------------------------------------------------------

@pytest.fixture
def scratch_registry():
    """A registration made by a test is removed again: the registries are the app's."""
    before = (dict(base.AVAILABLE_WRANGLING_ACTIONS), dict(base.ACTION_SCHEMAS), dict(base.ACTION_ENGINES))
    yield
    for registry, saved in zip((base.AVAILABLE_WRANGLING_ACTIONS, base.ACTION_SCHEMAS, base.ACTION_ENGINES), before):
        registry.clear()
        registry.update(saved)


def test_the_decorator_stores_the_engine_of_the_library_when_none_is_written(scratch_registry):
    @base.register_action("polars_scratch_demo")
    def scratch(lf, spec):
        return lf

    assert base.ACTION_ENGINES["polars_scratch_demo"] == "python-polars"


def test_the_decorator_stores_the_engine_it_is_given(scratch_registry, monkeypatch):
    monkeypatch.setattr(engines, "ENGINES", {**engines.ENGINES, "data_engine": ("python-polars", "python-other")})
    base.register_action("step_scratch_demo", engine="python-other")(lambda lf, spec: lf)
    assert base.ACTION_ENGINES["step_scratch_demo"] == "python-other"


def test_an_engine_the_app_has_no_library_for_cannot_be_registered(scratch_registry):
    with pytest.raises(ValueError) as caught:
        base.register_action("polars_scratch_bad", engine="python-pandas")(lambda lf, spec: lf)
    assert "no library for this engine in this app" in str(caught.value) and "polars_scratch_bad" in str(caught.value)
    assert "polars_scratch_bad" not in base.AVAILABLE_WRANGLING_ACTIONS and "polars_scratch_bad" not in base.ACTION_ENGINES


def test_an_engine_written_empty_cannot_be_registered(scratch_registry):
    with pytest.raises(ValueError):
        base.register_action("polars_scratch_empty", engine=None)(lambda lf, spec: lf)
    assert "polars_scratch_empty" not in base.AVAILABLE_WRANGLING_ACTIONS


def test_a_second_registration_of_a_name_replaces_its_engine_with_it(scratch_registry, monkeypatch):
    monkeypatch.setattr(engines, "ENGINES", {**engines.ENGINES, "data_engine": ("python-polars", "python-other")})
    base.register_action("polars_scratch_twice")(lambda lf, spec: lf)
    base.register_action("polars_scratch_twice", engine="python-other")(lambda lf, spec: lf)
    assert base.ACTION_ENGINES["polars_scratch_twice"] == "python-other"


# -- the entry file -------------------------------------------------------------------------------------------------------------

def test_the_entry_file_exists_names_its_engine_and_exposes_entry():
    module = importlib.import_module("transformer." + engines.entry_module_name("python-polars"))
    assert module.ENTRY.engine == "python-polars" == engines.DATA_ENGINE
    from transformer import DataAssembler, DataWrangler
    assert module.ENTRY.wrangler is DataWrangler and module.ENTRY.assembler is DataAssembler
    assert isinstance(module.ENTRY, engines.DataEngineEntry)


def test_the_entry_file_is_the_file_the_table_names():
    row = next(r for r in engines.ENGINE_TABLE if r.engine == "python-polars")
    assert row.library == "transformer"
    module = importlib.import_module(f"{row.library}.{engines.entry_module_name(row.engine)}")
    assert module.__name__ == "transformer.engine_python_polars"
