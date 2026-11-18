"""The table of the engines the app has, and the one way to say which engine a block uses (D-0219, D-0238, D-0239, D-0247).

The names are stated once (`utils.engines.ENGINE_TABLE`): the engine value, the recipe key it fills, the library that holds
it, and the prefix of the names its own entries carry. The module of a library that holds an engine is named from the value
(`engine_` plus the value with `-` turned into `_`); the app finds it from the table. The engine of a tier or of a plot is
the block's own value, else the recipe's (D-0219); a recipe that writes none is refused, never given one (D-0050).

# @deps
# consumes: libs/utils/src/utils/engines.py
# doc: .claude/knowledge/decision_ledger.md (D-0219, D-0238, D-0239, D-0247)
# @end_deps
"""
import pytest

from utils import engines
from utils.errors import DataAnalysisRecipeError


def test_the_table_holds_the_two_built_engines_with_their_libraries_and_prefixes():
    rows = {row.engine: row for row in engines.ENGINE_TABLE}
    assert set(rows) == {"python-polars", "python-plotnine"}
    assert (rows["python-polars"].key, rows["python-polars"].library, rows["python-polars"].prefix) == ("data_engine", "transformer", "polars_")
    assert (rows["python-plotnine"].key, rows["python-plotnine"].library, rows["python-plotnine"].prefix) == ("plot_engine", "viz_factory", "plotnine_")


def test_the_allowed_values_of_a_key_come_from_the_table():
    assert engines.ENGINES == {"data_engine": ("python-polars",), "plot_engine": ("python-plotnine",)}
    assert engines.engines_of("data_engine") == ("python-polars",)


@pytest.mark.parametrize("value, module", [("python-polars", "engine_python_polars"), ("python-plotnine", "engine_python_plotnine"),
                                           ("r-ggplot2", "engine_r_ggplot2"), ("python-R-dplyr", "engine_python_R_dplyr")])
def test_the_module_of_an_engine_is_engine_plus_the_value_with_dashes_turned_into_underscores(value, module):
    assert engines.entry_module_name(value) == module


# -- which engine a block uses ------------------------------------------------------------------------------------------------------

def test_the_engine_of_a_tier_is_its_own_value_else_the_recipes():
    recipe = {"data_engine": "python-polars"}
    assert engines.effective_engine("data_engine", {"data_engine": "python-other"}, recipe) == "python-other"
    assert engines.effective_engine("data_engine", {"steps": []}, recipe) == "python-polars"
    assert engines.effective_engine("data_engine", None, recipe) == "python-polars"


def test_a_recipe_that_writes_no_engine_gives_none_and_never_a_default():
    assert engines.effective_engine("data_engine", {"steps": []}, {}) is None
    assert engines.effective_engine("plot_engine", {}, {}) is None  # the block, then the recipe
    assert engines.effective_engine("plot_engine", None, None) is None


def test_a_level_that_writes_the_key_with_no_value_is_the_engine_the_app_must_refuse():
    # the key is written, so it is the block's engine; falling back to the recipe's would hide the empty line (D-0050)
    assert engines.effective_engine("plot_engine", {"plot_engine": None}, {"plot_engine": "python-plotnine"}) is None
    assert engines.engine_known("plot_engine", None) is False


def test_the_effective_engine_of_a_tier_reads_the_tier_of_the_body():
    body = {"tier1": {"data_engine": "python-other", "steps": []}, "tier2": {"steps": []}}
    recipe = {"data_engine": "python-polars"}
    assert engines.tier_engine(recipe, body, "tier1") == "python-other"
    assert engines.tier_engine(recipe, body, "tier2") == "python-polars"
    assert engines.tier_engine(recipe, body, "tier3") == "python-polars"
    assert engines.tier_engine({}, body, "tier2") is None
    assert engines.tier_engine(recipe, None, "tier1") == "python-polars"


# -- the refusal ------------------------------------------------------------------------------------------------------------------------

def test_the_refusal_says_the_decided_words_and_lists_the_engines_of_the_app():
    what, fix = engines.engine_problem("plot_engine", "r-ggplot2")
    assert "no library for this engine in this app" in what and "'r-ggplot2'" in what and "plot_engine" in what
    assert "python-plotnine" in what
    assert fix == "write plot_engine: python-plotnine"
    what, fix = engines.engine_problem("data_engine", "python-pandas")
    assert "no library for this engine in this app" in what and "python-polars" in what


def test_a_missing_engine_is_told_as_missing_not_as_unknown():
    what, fix = engines.engine_problem("plot_engine", None)
    assert "no library for this engine" not in what and "names no plot_engine" in what
    assert fix == "write plot_engine: python-plotnine"


def test_the_error_for_a_run_is_the_recipe_error_with_the_same_words():
    error = engines.engine_error("data_engine", "python-pandas", where="the tier1 of the table 'A'")
    assert isinstance(error, DataAnalysisRecipeError)
    assert "no library for this engine in this app" in error.message and "tier1 of the table 'A'" in error.message
    assert error.tip == "write data_engine: python-polars"


# -- the names of the entries carry the engine in the field, the prefix is for people -------------------------------------

def test_a_name_with_the_prefix_of_an_engine_must_carry_that_engine():
    registry = {"polars_filter": "python-polars", "modif_filter": "python-polars", "step_top_n": "python-polars"}
    assert engines.prefix_problems(registry) == []


def test_a_name_with_the_prefix_of_one_engine_and_the_field_of_another_is_reported():
    registry = {"polars_filter": "python-plotnine", "plotnine_geom_point": "python-polars", "modif_geom_point": "python-plotnine"}
    assert sorted(engines.prefix_problems(registry)) == [
        ("plotnine_geom_point", "python-polars", "python-plotnine"), ("polars_filter", "python-plotnine", "python-polars")]


def test_a_name_without_any_engine_prefix_is_not_judged_by_its_name():
    assert engines.prefix_problems({"modif_x": "python-polars", "step_y": "python-plotnine", "geom_point": "python-plotnine"}) == []


# -- the libraries behind an engine, and their versions read when the record is written (D-0248) ------------------------------------

def test_every_engine_of_the_table_names_the_libraries_behind_it_and_they_are_installed():
    from importlib import metadata
    for row in engines.ENGINE_TABLE:
        assert row.packages, f"{row.engine}: no library named behind the engine"
        for package in row.packages:
            metadata.version(package)       # raises when it is not installed: the record would hold "unknown" for it


def test_the_versions_of_an_engine_are_read_from_the_installed_libraries_not_typed_in():
    from importlib import metadata
    versions = engines.engine_versions("python-polars")
    assert versions == {package: metadata.version(package) for package in ("polars", "transformer")}


def test_an_engine_the_app_has_no_library_for_has_no_versions_and_a_library_that_is_not_installed_says_unknown(monkeypatch):
    assert engines.engine_versions("r-ggplot2") is None
    monkeypatch.setattr(engines, "ENGINE_TABLE", (engines.EngineRow("python-ghost", "data_engine", "ghost", "ghost_", ("no-such-package-installed",)),))
    assert engines.engine_versions("python-ghost") == {"no-such-package-installed": "unknown"}
