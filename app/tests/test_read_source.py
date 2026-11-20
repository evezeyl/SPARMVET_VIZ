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


# The recipes that must load and draw as a graph. A recipe that drops out fails the test (it is not skipped). A recipe that is expected not
# to draw would be named in EXPECTED_NOT_TO_DRAW with its reason; none is today.
SHIPPED = ["1_Abromics_general_pipeline", "1_test_data_ST22_dummy", "2_test_data_ST22_dummy", "3_test_no_joins", "demo_abromics",
           "figshare_integration", "stress_test_master"]
EXPECTED_NOT_TO_DRAW: dict[str, str] = {}


def _shipped():
    return SHIPPED


# -- the shipped recipes -----------------------------------------------------------------------

def test_the_pinned_shipped_recipes_are_exactly_the_recipes_of_the_folder_that_load_and_draw():
    on_disk = sorted(p.stem for p in RECIPES.glob("*.yaml"))
    assert sorted(SHIPPED + list(EXPECTED_NOT_TO_DRAW)) == on_disk, "a recipe was added or removed: update SHIPPED"
    for recipe_id in SHIPPED:
        with contextlib.redirect_stdout(io.StringIO()):
            raw = load_data_analysis_recipe(RECIPES / f"{recipe_id}.yaml").raw
            build_graph(raw)


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


def test_the_returned_frame_is_a_lazy_scan_of_the_file_not_a_collected_table(tmp_path):
    world = World(tmp_path)
    frame = world.orch.read_source("tiny", "T")
    plan = frame.explain()
    assert "SCAN" in plan and "T.tsv" in plan
    assert "DF [" not in plan                      # the plan of an eagerly collected frame
    assert "DF [" in frame.collect().lazy().explain()   # the check can tell the two apart


def test_the_call_validates_the_file_before_any_collect(tmp_path):
    world = World(tmp_path)
    world.write_data("sample_id\tother\ns1\tA\n")
    with pytest.raises(IngestionError):
        world.orch.read_source("tiny", "T")   # no .collect()


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
    with pytest.raises(IngestionError, match=r"Source table 'T' could not be read.*group"):
        world.orch.read_source("tiny", "T").collect()


def test_a_value_that_does_not_fit_its_declared_type_fails_and_names_the_table_and_the_column(tmp_path):
    world = World(tmp_path)
    world.write_data_analysis_recipe(group_type="Int64")
    clear_data_analysis_recipe_cache()
    with pytest.raises(IngestionError, match=r"Source table 'T' could not be read.*group"):
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


# -- a pinned recipe, the import folder, by_dataset_id --------------------------------------------

def _pinned(world, mutate):
    """A pinned recipe (an audit copy) made from the one on disk, changed by `mutate`; the file on disk is not changed."""
    from app.modules.cache_keys import loaded_from_resolved
    import copy
    original = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml")
    raw = copy.deepcopy(dict(original.raw))
    mutate(raw)
    return loaded_from_resolved(original, raw)


def test_a_pinned_recipe_with_another_source_path_gives_the_table_of_the_pinned_text(tmp_path):
    world = World(tmp_path)
    other = tmp_path / "other.tsv"
    other.write_text("sample_id\tgroup\nz1\tB\n")
    pinned = _pinned(world, lambda raw: raw["data_schemas"]["T"]["source"].update(path=str(other)))
    assert world.orch.read_source("tiny", "T", loaded=pinned).collect().rows() == [("z1", "B")]
    assert world.orch.read_source("tiny", "T").collect().height == 3   # the file on disk is unchanged


def test_a_pinned_recipe_can_hold_a_table_the_file_on_disk_does_not_have(tmp_path):
    world = World(tmp_path)
    extra = tmp_path / "extra.tsv"
    extra.write_text("sample_id\tgroup\nq1\tA\n")

    def add(raw):
        raw["data_schemas"]["X"] = {**raw["data_schemas"]["T"], "source": {"type": "local_tsv", "path": str(extra)}}
    pinned = _pinned(world, add)
    assert world.orch.read_source("tiny", "X", loaded=pinned).collect().rows() == [("q1", "A")]
    with pytest.raises(DataAnalysisRecipeError, match="No source table 'X'"):
        world.orch.read_source("tiny", "X")


def test_a_pinned_recipe_does_not_need_a_recipe_file_on_disk(tmp_path):
    world = World(tmp_path)
    pinned = _pinned(world, lambda raw: None)
    (world.data_analysis_recipes_dir / "tiny.yaml").unlink()
    assert world.orch.read_source("tiny", "T", loaded=pinned).collect().height == 3
    with pytest.raises(FileNotFoundError):
        world.orch.read_source("tiny", "T")


def test_an_unknown_table_in_a_pinned_recipe_gives_the_plain_error(tmp_path):
    world = World(tmp_path)
    pinned = _pinned(world, lambda raw: raw["data_schemas"].pop("T") and None)
    with pytest.raises(DataAnalysisRecipeError, match="No source table 'T'.*Known: none"):
        world.orch.read_source("tiny", "T", loaded=pinned)


def test_a_table_not_in_the_import_folder_fails_and_raw_data_is_never_read(tmp_path):
    world = World(tmp_path)
    imports = tmp_path / "imports"
    (imports / "tiny" / "data").mkdir(parents=True)
    orch = DataOrchestrator(world.data_analysis_recipes_dir, world.data_dir, imports_dir=imports)
    assert world.data_file.exists()   # raw_data and the recipe path HOLD a file for T
    with pytest.raises(IngestionError, match="has no file in the data folder of the import of 'tiny'") as caught:
        orch.read_source("tiny", "T")
    assert "Source table 'T' could not be read" in str(caught.value)
    (imports / "tiny" / "data" / "T.tsv").write_text("sample_id\tgroup\nonly\tA\n")
    assert orch.read_source("tiny", "T").collect().rows() == [("only", "A")]   # now the import's file, not raw_data's


def test_by_dataset_id_finds_the_file_by_the_table_id_and_ignores_the_recipe_path(tmp_path):
    world = World(tmp_path)
    raw_data = tmp_path / "delivered"
    raw_data.mkdir()
    (raw_data / "T.tsv").write_text("sample_id\tgroup\nd1\tB\n")
    orch = DataOrchestrator(world.data_analysis_recipes_dir, raw_data, data_lookup="by_dataset_id")
    assert orch.read_source("tiny", "T").collect().rows() == [("d1", "B")]
    (raw_data / "T.tsv").unlink()
    with pytest.raises(IngestionError, match="Source table 'T' could not be read"):
        orch.read_source("tiny", "T")   # the recipe's own path (which exists) is not used


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


def test_the_list_follows_the_graph_order_not_the_order_the_ingredients_are_written_in():
    """Graph order: the order the tables are declared in `data_schemas` (a table after those it depends on)."""
    join = lambda *names: {"ingredients": [{"dataset_id": n} for n in names], "tier1": {"steps": []}}
    ab = build_graph(_recipe({"J": join("A", "B")}, {"p": _plot("J")}))
    ba = build_graph(_recipe({"J": join("B", "A")}, {"p": _plot("J")}))
    assert source_tables_of_plot(ab, "p") == source_tables_of_plot(ba, "p") == ["A", "B"]
    reordered = _recipe({"J": join("A", "B")}, {"p": _plot("J")})
    reordered["data_schemas"] = {k: reordered["data_schemas"][k] for k in ("C", "B", "A")}
    assert source_tables_of_plot(build_graph(reordered), "p") == ["B", "A"]


def test_an_unknown_plot_or_table_fails_with_a_plain_message():
    graph = build_graph(_recipe({}, {"p": _plot("A")}))
    with pytest.raises(KeyError, match="The recipe has no plot 'nope'"):
        source_tables_of_plot(graph, "nope")
    with pytest.raises(KeyError, match="The recipe has no table or join 'nope'"):
        source_tables_of_table(graph, "nope")
    with pytest.raises(KeyError, match="no table or join 'p'"):
        source_tables_of_table(graph, "p")   # a plot id is not a table id
    with pytest.raises(KeyError, match="no plot 'A'"):
        source_tables_of_plot(graph, "A")


def test_a_plot_with_no_target_table_makes_the_whole_graph_fail_so_no_list_is_given():
    # build_graph refuses the recipe (RecipeGraphError); the lister never sees such a plot. What the Source view should show
    # for a recipe that cannot be drawn is NOT decided: reported to the coordinator.
    bad = _recipe({}, {"p": {"mapping": {"x": "id"}, "layers": []}})
    with pytest.raises(RecipeGraphError, match="no target_dataset"):
        build_graph(bad)
