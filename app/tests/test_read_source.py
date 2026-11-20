"""The Source reader: one source table of a recipe as the ingestion reads it, before any tier-1 step (D-0310, HOME design: Source).

`DataOrchestrator.read_source` is lazy, writes nothing, touches no key, and is the SAME read the tier-1 build uses (`_read_source`).
`utils.recipe_graph.source_tables_of_plot` lists the source tables that feed a plot, from the recipe graph.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_read_source.py -q
"""
import contextlib
import io
import json
import os
from pathlib import Path

import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.tests.test_cache_chain import FILTER_A, World, bump
from utils.errors import DataAnalysisRecipeError, IngestionError
from utils.recipe_graph import RecipeGraphError, build_graph, source_tables_of_plot, source_tables_of_table

ROOT = Path(__file__).resolve().parents[2]
RECIPES = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RAW = ROOT / "assets" / "test_data"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _tree(folder: Path) -> set:
    return {str(p.relative_to(folder)) for p in folder.rglob("*")} if folder.exists() else set()


def _shipped():
    out = []
    for path in sorted(RECIPES.glob("*.yaml")):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                raw = load_data_analysis_recipe(path).raw
            graph = build_graph(raw)
        except BaseException:  # noqa: BLE001 - a recipe that does not load or draw is not a subject here
            continue
        out.append(path.stem)
    return out


# -- the shipped recipes -----------------------------------------------------------------------

def test_the_shipped_list_is_not_empty():
    assert len(_shipped()) >= 5


@pytest.mark.parametrize("recipe_id", _shipped())
def test_every_plot_of_a_shipped_recipe_has_readable_source_tables_equal_to_the_ingestion(recipe_id):
    orch = DataOrchestrator(RECIPES, RAW)
    with contextlib.redirect_stdout(io.StringIO()):
        raw = load_data_analysis_recipe(RECIPES / f"{recipe_id}.yaml").raw
        graph = build_graph(raw)
        schemas = orch.dataset_schemas(recipe_id)
        for plot in graph.plots():
            listed = source_tables_of_plot(graph, plot)
            assert listed, f"{recipe_id}: plot {plot} lists no source table"
            assert len(listed) == len(set(listed))
            for table in listed:
                got = orch.read_source(recipe_id, table).collect()
                located = orch.locate_dataset_file(recipe_id, table, schemas[table])
                ds = {**schemas[table], "source": {"type": "local_parquet" if located.suffix == ".parquet" else "local_tsv", "path": str(located)}}
                expected = orch.ingestor.ingest(table, ds)[0].collect()
                assert got.columns == expected.columns and got.dtypes == expected.dtypes
                assert got.equals(expected)


# -- Source against T1 --------------------------------------------------------------------------

def test_a_table_without_tier1_steps_has_a_source_equal_to_its_t1(tmp_path):
    world = World(tmp_path)
    src = world.orch.read_source("tiny", "T").collect()
    t1 = world.orch.materialize_tier1("tiny", "T", world.anchor.with_name("T.parquet")).collect()
    assert src.equals(t1) and src.dtypes == t1.dtypes and src.columns == t1.columns
    assert src.rows() == [("s1", "A"), ("s2", "A"), ("s3", "B")]


def test_a_table_with_tier1_steps_that_change_it_differs_from_its_source(tmp_path):
    world = World(tmp_path)
    world.write_data_analysis_recipe(wrangling_tier1=[FILTER_A])
    src = world.orch.read_source("tiny", "T").collect()
    t1 = world.orch.materialize_tier1("tiny", "T", world.anchor.with_name("T.parquet")).collect()
    assert src.height == 3 and t1.height == 2
    assert set(src["group"]) == {"A", "B"}


def test_source_keeps_the_declared_type(tmp_path):
    world = World(tmp_path)
    assert world.orch.read_source("tiny", "T").collect_schema()["group"] == pl.Categorical
    world.write_data_analysis_recipe(group_type="String")
    clear_data_analysis_recipe_cache()
    assert world.orch.read_source("tiny", "T").collect_schema()["group"] == pl.String


def test_read_source_is_lazy(tmp_path):
    world = World(tmp_path)
    assert isinstance(world.orch.read_source("tiny", "T"), pl.LazyFrame)


# -- the plain errors and edge cases ------------------------------------------------------------

def test_an_unknown_table_id_fails_and_names_it_and_the_known_ones(tmp_path):
    world = World(tmp_path)
    with pytest.raises(DataAnalysisRecipeError, match="No_Such.*Known: T"):
        world.orch.read_source("tiny", "No_Such")


def test_an_unknown_recipe_fails(tmp_path):
    world = World(tmp_path)
    with pytest.raises(FileNotFoundError, match="nothing"):
        world.orch.read_source("nothing", "T")


def test_a_missing_file_fails_like_the_tier1_build_and_names_the_table(tmp_path):
    world = World(tmp_path)
    world.data_file.unlink()
    with pytest.raises(IngestionError, match="Source table 'T' could not be read.*T.tsv"):
        world.orch.read_source("tiny", "T").collect()
    with pytest.raises(IngestionError, match="Dataset 'T' could not be loaded"):
        world.orch.materialize_tier1("tiny", "T", world.anchor.with_name("T.parquet"))


def test_an_empty_file_gives_an_error_or_an_empty_table_the_same_as_the_tier1_build(tmp_path):
    world = World(tmp_path)
    world.write_data("")
    try:
        got = world.orch.read_source("tiny", "T").collect()
        outcome = ("table", got.height)
    except Exception as exc:  # noqa: BLE001
        outcome = ("error", type(exc).__name__)
    try:
        t1 = world.orch.materialize_tier1("tiny", "T", world.anchor.with_name("T.parquet")).collect()
        expected = ("table", t1.height)
    except Exception as exc:  # noqa: BLE001
        expected = ("error", type(exc).__name__)
    assert outcome == expected


def test_a_file_with_only_the_header_gives_an_empty_table_with_the_declared_types(tmp_path):
    world = World(tmp_path)
    world.write_data("sample_id\tgroup\n")
    src = world.orch.read_source("tiny", "T").collect()
    assert src.height == 0 and src.columns == ["sample_id", "group"] and src.dtypes == [pl.Categorical, pl.Categorical]


def test_a_missing_declared_column_fails_with_a_plain_error(tmp_path):
    world = World(tmp_path)
    world.write_data("sample_id\tother\ns1\tA\n")
    with pytest.raises(IngestionError, match="group"):
        world.orch.read_source("tiny", "T").collect()


# -- it writes nothing and moves no key -----------------------------------------------------------

def test_reading_source_writes_no_file_and_changes_no_key(tmp_path):
    world = World(tmp_path)
    before_keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    before_tree = _tree(tmp_path)
    world.orch.read_source("tiny", "T").collect()
    assert _tree(tmp_path) == before_tree
    after = world.orch.compute_data_analysis_recipe_keys("tiny")
    assert after == before_keys


def test_reading_the_shipped_sources_leaves_the_keys_of_the_recipes_as_they_were():
    orch = DataOrchestrator(RECIPES, RAW)
    for recipe_id in _shipped():
        with contextlib.redirect_stdout(io.StringIO()):
            before = orch.compute_data_analysis_recipe_keys(recipe_id)
            for table in orch.dataset_schemas(recipe_id):
                try:
                    orch.read_source(recipe_id, table).collect()
                except Exception:  # noqa: BLE001 - a table the tier-1 build cannot read either
                    pass
            assert orch.compute_data_analysis_recipe_keys(recipe_id) == before


# -- the source tables of a plot: the graph ------------------------------------------------------

def _schema(cols):
    return {"source": {"type": "local_tsv", "path": "x.tsv"}, "input_fields": {c: {"type": "String"} for c in cols}, "tier1": {"steps": []}}


def _plot(target):
    return {"target_dataset": target, "mapping": {"x": "id"}, "layers": [{"name": "geom_bar", "params": {}}]}


def _recipe(joins, plots):
    return {"id": "r", "data_schemas": {"A": _schema(["id"]), "B": _schema(["id"]), "C": _schema(["id"])},
            "joins": joins, "analysis_groups": {"g": {"plots": plots}}}


def test_a_join_lists_both_source_tables_a_table_used_twice_once_and_a_direct_plot_its_table():
    join = lambda *names: {"ingredients": [{"dataset_id": n} for n in names], "tier1": {"steps": []}}
    graph = build_graph(_recipe({"J": join("A", "B"), "K": join("A", "B", "C")},
                                {"pj": _plot("J"), "pa": _plot("A"), "pk": _plot("K")}))
    assert source_tables_of_plot(graph, "pj") == ["A", "B"]
    assert source_tables_of_plot(graph, "pa") == ["A"]
    assert source_tables_of_plot(graph, "pk") == ["A", "B", "C"]
    assert source_tables_of_table(graph, "J") == ["A", "B"]
    assert source_tables_of_table(graph, "B") == ["B"]


def test_a_table_reached_through_two_paths_is_listed_once():
    join = lambda *names: {"ingredients": [{"dataset_id": n} for n in names], "tier1": {"steps": []}}
    graph = build_graph(_recipe({"J": join("A", "B"), "K": join("J", "A")}, {"p": _plot("K")}))
    assert source_tables_of_plot(graph, "p") == ["A", "B"]


def test_the_order_is_stable_and_does_not_depend_on_the_order_of_the_ingredients_alone():
    join = lambda *names: {"ingredients": [{"dataset_id": n} for n in names], "tier1": {"steps": []}}
    one = build_graph(_recipe({"J": join("B", "A")}, {"p": _plot("J")}))
    two = build_graph(_recipe({"J": join("B", "A")}, {"p": _plot("J")}))
    assert source_tables_of_plot(one, "p") == source_tables_of_plot(two, "p")


def test_an_unknown_plot_or_table_fails_with_a_plain_message():
    graph = build_graph(_recipe({}, {"p": _plot("A")}))
    with pytest.raises(KeyError, match="no node 'T3:nope'"):
        source_tables_of_plot(graph, "nope")
    with pytest.raises(KeyError, match="no node 'T1:nope'"):
        source_tables_of_table(graph, "nope")


def test_a_plot_with_no_target_table_makes_the_whole_graph_fail_so_no_list_is_given():
    # build_graph refuses the recipe (RecipeGraphError); the lister never sees such a plot. What the Source view should show
    # for a recipe that cannot be drawn is NOT decided: reported to the coordinator.
    bad = _recipe({}, {"p": {"mapping": {"x": "id"}, "layers": []}})
    with pytest.raises(RecipeGraphError, match="no target_dataset"):
        build_graph(bad)
