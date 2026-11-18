"""The app chooses the engine with the value the recipe writes (D-0219), from the engines it has a library for (D-0247, D-0239).

What is held here:
- the table of the engines (`utils.engines.ENGINE_TABLE`) and the registry of the app agree, and each row has its entry file that
  names the engine and exposes `ENTRY` (D-0247); the libraries do not import each other;
- the checker is given the engine of every action and component (`engine_tables`, D-0238), HOME's gate needs that coverage, and the
  checker refuses a step under the block of another engine, an engine name the app has no library for (the decided words), and
  an engine written on one tier only is judged for that tier only;
- the code CHOOSES: a tier whose engine is a stand-in is run by the stand-in's code, a tier without a line by the recipe's engine,
  a plot with its own engine by the plot's engine; an engine the app does not have, or none written, is refused with plain words
  and nothing is run or stored (no fall back to the one engine that exists, D-0050);
- no code of the app builds a factory, a wrangler or an assembler by itself outside the registry.

# @deps
# consumes: app/modules/engine_registry.py, app/modules/orchestrator.py, app/modules/data_analysis_recipe_validator.py, libs/utils/src/utils/engines.py, libs/utils/src/utils/recipe_factory.py, libs/transformer/src/transformer/engine_python_polars.py, libs/viz_factory/src/viz_factory/engine_python_plotnine.py
# doc: .claude/knowledge/decision_ledger.md (D-0219, D-0238, D-0239, D-0247, D-0050)
# @end_deps
"""
import ast
import importlib
from pathlib import Path

import polars as pl
import pytest

from app.modules import engine_registry
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import REQUIRED_COVERAGE, checker_catalogs, checker_problems
from app.modules.engine_registry import PlotEngines, REGISTRY, data_entry, engine_tables, plot_entry
from app.modules.orchestrator import DataOrchestrator
from transformer import DataWrangler
from utils import engines
from utils.engines import DataEngineEntry, PlotEngineEntry
from utils.errors import DataAnalysisRecipeError, IngestionError, VisualizationError
from utils.recipe_check import check_recipe
from utils.recipe_factory import minimal_join, minimal_plot, minimal_recipe, minimal_schema, write_recipe

ROOT = Path(__file__).resolve().parents[2]
WORDS = "no library for this engine in this app"


# -- the table, the registry, the entry files -------------------------------------------------------------------------------------

def test_the_registry_has_exactly_the_engines_of_the_table():
    assert set(REGISTRY) == {row.engine for row in engines.ENGINE_TABLE}


@pytest.mark.parametrize("row", engines.ENGINE_TABLE, ids=lambda row: row.engine)
def test_every_row_of_the_table_has_its_entry_file_that_names_the_engine_and_exposes_entry(row):
    module_name = engines.entry_module_name(row.engine)
    path = ROOT / "libs" / row.library / "src" / row.library / f"{module_name}.py"
    assert path.is_file(), f"the engine {row.engine} has no entry file {path}"
    module = importlib.import_module(f"{row.library}.{module_name}")
    assert module.ENTRY.engine == row.engine
    assert isinstance(module.ENTRY, DataEngineEntry if row.key == "data_engine" else PlotEngineEntry)
    assert REGISTRY[row.engine] is module.ENTRY


def test_an_entry_file_imports_only_its_own_library_and_the_names_of_utils():
    for row in engines.ENGINE_TABLE:
        source = (ROOT / "libs" / row.library / "src" / row.library / f"{engines.entry_module_name(row.engine)}.py").read_text(encoding="utf-8")
        imported = {n.module.split(".")[0] if isinstance(n, ast.ImportFrom) else a.name.split(".")[0]
                    for n in ast.walk(ast.parse(source)) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in getattr(n, "names", [n])}
        others = {r.library for r in engines.ENGINE_TABLE} - {row.library}
        assert not (imported & others), f"{row.library} imports another engine library: {imported & others}"


# -- what the checker is given -----------------------------------------------------------------------------------------------------

def test_every_registered_name_has_an_engine_in_the_tables_given_to_the_checker():
    catalogs = checker_catalogs()
    assert set(catalogs["action_engines"]) == set(catalogs["actions"]) | set(engine_tables()["action_engines"])
    assert set(catalogs["component_engines"]) == catalogs["components"]
    assert set(catalogs["action_engines"].values()) == {"python-polars"}
    assert set(catalogs["component_engines"].values()) == {"python-plotnine"}


def test_the_gate_needs_the_engine_coverage_and_a_recipe_checked_without_it_is_not_accepted(monkeypatch, tmp_path):
    assert "engines" in REQUIRED_COVERAGE
    path = write_recipe(tmp_path / "r.yaml", minimal_recipe("r", plots={"p": minimal_plot("table", {"x": "sample_id"})}))
    from app.modules import data_analysis_recipe_validator as module
    assert [p for p in checker_problems(path) if "did not cover" in p.problem] == []
    monkeypatch.setattr(module, "engine_tables", lambda: {})
    problems = [p for p in checker_problems(path) if "did not cover" in p.problem]
    assert problems and "engines" in problems[0].problem


# -- the checker with the real tables ------------------------------------------------------------------------------------------------

def recipe(**changes):
    raw = minimal_recipe("r", schemas={"A": minimal_schema("assets/test_data/a.tsv", {"sample_id": "String", "v": "Float64"}, entity_key="sample_id",
                                                         tier1=[{"action": "polars_head", "n": 5}])},
                         plots={"p": minimal_plot("A", {"x": "v"}, [{"name": "geom_point"}])})
    for key, value in changes.items():
        raw[key] = value
    return raw


def found(raw, code):
    return [p for p in check_recipe(raw, "build", catalogs=checker_catalogs(), file_stem="r").problems if p.code == code]


def test_the_recipe_the_tests_start_from_passes_with_the_engine_coverage():
    result = check_recipe(recipe(), "build", catalogs=checker_catalogs(), file_stem="r")
    assert "engines" in result.coverage
    assert [p for p in result.problems if p.code in ("T06", "EN02", "EN03", "T04")] == []


def test_a_step_under_a_tier_of_another_engine_is_refused_with_the_step_and_both_engines():
    raw = recipe()
    raw["data_schemas"]["A"]["tier1"]["data_engine"] = "python-plotnine"
    problems = found(raw, "EN02")
    assert [p.path for p in problems] == ["data_schemas.A.tier1.steps[1]"]
    message = problems[0].message
    assert "polars_head" in message and "python-polars" in message and "python-plotnine" in message
    assert problems[0].fix and "python-polars" in problems[0].fix
    assert found(raw, "T06"), "a plot engine is not a data engine: refused too"


def test_a_layer_in_a_plot_of_another_engine_is_refused_with_the_layer_and_both_engines():
    raw = recipe()
    raw["analysis_groups"]["main"]["plots"]["p"]["plot_engine"] = "python-polars"
    problems = found(raw, "EN02")
    assert [p.path for p in problems] == ["analysis_groups.main.plots.p.layers[1]"]
    assert "geom_point" in problems[0].message and "python-plotnine" in problems[0].message and "python-polars" in problems[0].message


def test_an_engine_name_the_app_has_no_library_for_is_refused_with_the_decided_words_and_the_engines_of_the_app():
    raw = recipe(data_engine="python-pandas")
    problems = found(raw, "T06")
    assert [p.path for p in problems] == ["data_engine"]
    assert WORDS in problems[0].message and "python-polars" in problems[0].message


def test_an_engine_written_on_one_tier_only_is_refused_there_and_not_on_the_other_tier():
    raw = recipe()
    raw["data_schemas"]["A"]["tier1"]["data_engine"] = "python-pandas"
    raw["data_schemas"]["A"]["tier2"] = {"steps": []}
    problems = found(raw, "T06")
    assert [p.path for p in problems] == ["data_schemas.A.tier1.data_engine"]


def test_a_plot_with_its_own_unknown_engine_is_refused_at_the_plot():
    raw = recipe()
    raw["analysis_groups"]["main"]["plots"]["p"]["plot_engine"] = "r-ggplot2"
    problems = found(raw, "T06")
    assert [p.path for p in problems] == ["analysis_groups.main.plots.p.plot_engine"]
    assert WORDS in problems[0].message and "python-plotnine" in problems[0].message


def test_tier_3_of_a_plot_refuses_an_engine_the_app_has_no_library_for():
    # PROVISIONAL (not decided): the rule for a tier 3 engine that the app HAS a library for but the audit cannot write
    # (the audit writes Polars steps) is not stated in the ledger; with one data engine the case cannot occur, and nothing is built for it.
    raw = recipe()
    raw["analysis_groups"]["main"]["plots"]["p"]["tier3"] = {"data_engine": "python-pandas", "steps": []}
    assert [p.path for p in found(raw, "T06")] == ["analysis_groups.main.plots.p.tier3.data_engine"]


def test_a_recipe_with_no_engine_line_is_refused_for_both_and_given_no_default():
    raw = recipe()
    del raw["data_engine"], raw["plot_engine"]
    assert sorted(p.path for p in found(raw, "T04")) == ["data_engine", "plot_engine"]
    assert [p for p in check_recipe(raw, "build", catalogs=checker_catalogs(), file_stem="r").problems if p.code in ("EN02", "EN03")] == []


def test_an_empty_steps_list_is_a_tier_without_a_step_and_its_engine_is_still_judged():
    raw = recipe()
    raw["data_schemas"]["A"]["tier1"] = {"data_engine": "python-pandas", "steps": []}
    assert [p.path for p in found(raw, "T06")] == ["data_schemas.A.tier1.data_engine"]
    assert found(raw, "EN02") == []


# -- the code chooses: the data side -----------------------------------------------------------------------------------------------

MARKER = "engine_used"


class StandInWrangler(DataWrangler):
    """A second data engine for the test: it runs the steps like Polars and marks the table, so a table shows who made it."""

    def run(self, lf, wrangling_rules):
        return super().run(lf, wrangling_rules).with_columns(pl.lit("stand-in").alias(MARKER))


@pytest.fixture
def stand_in(monkeypatch):
    """The app with a second data engine `python-standin`, in the registry and in the names of the table."""
    entry = DataEngineEntry(engine="python-standin", wrangler=StandInWrangler, assembler=REGISTRY["python-polars"].assembler)
    monkeypatch.setitem(REGISTRY, "python-standin", entry)
    monkeypatch.setattr(engines, "ENGINES", {**engines.ENGINES, "data_engine": ("python-polars", "python-standin")})
    return entry


class World:
    """Two tables A and B (3 rows each) in a recipe built with the factory; `edit` changes the raw recipe before it is written."""

    def __init__(self, root: Path, edit=None, drop=()):
        self.data = root / "data"
        self.data.mkdir()
        self.recipes = root / "recipes"
        self.recipes.mkdir()
        for name in ("A", "B"):
            (self.data / f"{name}.tsv").write_text("sample_id\tv\ns1\t1\ns2\t2\ns3\t3\n")
        head1 = [{"action": "polars_head", "n": 2}]
        schemas = {name: minimal_schema(str(self.data / f"{name}.tsv"), {"sample_id": "String", "v": "Int64"}, entity_key="sample_id",
                                       tier1=head1, tier2=head1) for name in ("A", "B")}
        raw = minimal_recipe("w", schemas=schemas, joins={"AB": minimal_join(["A", "B"], [])},
                             plots={"pa": minimal_plot("A", {"x": "v"}), "pb": minimal_plot("B", {"x": "v"})})
        for key in drop:
            raw.pop(key, None)
        if edit:
            edit(raw)
        write_recipe(self.recipes / "w.yaml", raw)
        clear_data_analysis_recipe_cache()
        self.orchestrator = DataOrchestrator(self.recipes, self.data)
        self.anchors = root / "anchors"
        self.anchors.mkdir()

    def tier1(self, name):
        return self.orchestrator.materialize_tier1("w", name, self.anchors / f"{name}.parquet").collect()

    def tier2(self, name):
        self.orchestrator.materialize_tier1("w", name, self.anchors / f"{name}.parquet")
        return self.orchestrator.materialize_tier2("w", name, self.anchors / f"{name}.parquet").collect()


def test_without_any_override_every_tier_is_run_by_the_engine_of_the_recipe(tmp_path):
    world = World(tmp_path)
    assert world.tier1("A").height == 2 and MARKER not in world.tier1("A").columns
    assert world.tier2("B").height == 2 and MARKER not in world.tier2("B").columns


def test_the_engine_written_on_a_tier_selects_the_code_of_that_tier_only(tmp_path, stand_in):
    def edit(raw):
        raw["data_schemas"]["A"]["tier1"]["data_engine"] = "python-standin"
    world = World(tmp_path, edit)
    assert world.tier1("A")[MARKER].to_list() == ["stand-in"] * 2   # A's tier 1 ran with the stand-in
    assert MARKER not in world.tier1("B").columns                      # B's tier 1 ran with the recipe's engine


def test_the_tier_2_engine_is_its_own_and_a_tier_1_engine_does_not_reach_it(tmp_path, stand_in):
    def edit(raw):
        raw["data_schemas"]["A"]["tier1"]["data_engine"] = "python-standin"
        raw["data_schemas"]["B"]["tier2"]["data_engine"] = "python-standin"
    world = World(tmp_path, edit)
    a2, b2 = world.tier2("A"), world.tier2("B")
    # A: tier 1 was run by the stand-in, which wrote the marker; tier 2 (the recipe's engine) kept the column and ran its head
    assert MARKER in a2.columns and a2.height == 2
    # B: tier 1 by the recipe's engine, tier 2 by the stand-in
    assert b2[MARKER].to_list() == ["stand-in"] * 2


def test_the_engine_of_the_recipe_is_the_default_of_every_tier(tmp_path, stand_in):
    world = World(tmp_path, lambda raw: raw.update(data_engine="python-standin"))
    assert world.tier1("A")[MARKER].to_list() == ["stand-in"] * 2
    assert world.tier1("B")[MARKER].to_list() == ["stand-in"] * 2


def test_a_tier_that_names_the_default_engine_back_runs_it_although_the_recipe_default_is_the_stand_in(tmp_path, stand_in):
    def edit(raw):
        raw["data_engine"] = "python-standin"
        raw["data_schemas"]["B"]["tier1"]["data_engine"] = "python-polars"
    world = World(tmp_path, edit)
    assert MARKER not in world.tier1("B").columns and MARKER in world.tier1("A").columns


def test_a_join_runs_its_steps_with_the_engine_of_its_own_tier_1(tmp_path, stand_in):
    class StandInAssembler(REGISTRY["python-polars"].assembler):
        def assemble(self, steps):
            return super().assemble(steps).with_columns(pl.lit("stand-in").alias(MARKER))
    entry = DataEngineEntry(engine="python-standin", wrangler=StandInWrangler, assembler=StandInAssembler)
    REGISTRY["python-standin"] = entry  # the fixture removes the key again
    def edit(raw):
        raw["joins"]["AB"]["tier1"]["data_engine"] = "python-standin"
        raw["joins"]["AB"]["tier1"]["steps"] = [{"action": "polars_join", "right_ingredient": "B", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"}]
    world = World(tmp_path, edit)
    assert MARKER in world.tier1("AB").columns


# -- the code refuses: an engine the app has no library for, or none ---------------------------------------------------------

@pytest.mark.parametrize("name, edit, where", [
    ("tier 1 of a table", lambda raw: raw["data_schemas"]["A"]["tier1"].update(data_engine="python-pandas"), "tier1 of the table 'A'"),
    ("the default of the recipe", lambda raw: raw.update(data_engine="python-pandas"), "tier1 of the table"),
    ("a plot engine in a data slot", lambda raw: raw["data_schemas"]["A"]["tier1"].update(data_engine="python-plotnine"), "tier1 of the table 'A'"),
    ("an empty value", lambda raw: raw["data_schemas"]["A"]["tier1"].update(data_engine=None), "tier1 of the table 'A'"),
])
def test_a_table_whose_tier_names_an_engine_the_app_has_no_library_for_is_not_built_and_nothing_is_stored(tmp_path, name, edit, where):
    world = World(tmp_path, edit)
    with pytest.raises(IngestionError) as caught:
        world.tier1("A")
    text = str(caught.value)
    assert where in text and ("empty value" in name or WORDS in text) and "python-polars" in text + caught.value.tip
    assert not (world.anchors / "A.parquet").exists()


def test_a_tier_2_that_names_an_engine_the_app_has_no_library_for_is_refused_also_when_it_has_no_steps(tmp_path):
    def edit(raw):
        raw["data_schemas"]["A"]["tier2"] = {"data_engine": "python-pandas", "steps": []}
    world = World(tmp_path, edit)
    world.orchestrator.materialize_tier1("w", "A", world.anchors / "A.parquet")
    with pytest.raises(DataAnalysisRecipeError) as caught:
        world.orchestrator.materialize_tier2("w", "A", world.anchors / "A.parquet")
    assert "tier2 of 'A'" in str(caught.value) and WORDS in str(caught.value)


def test_a_recipe_that_writes_no_data_engine_is_refused_when_a_tier_is_built_and_gets_no_default(tmp_path):
    world = World(tmp_path, drop=("data_engine",))
    with pytest.raises(IngestionError) as caught:
        world.tier1("A")
    assert "names no data_engine" in str(caught.value) and WORDS not in str(caught.value)
    assert not (world.anchors / "A.parquet").exists()


def test_the_entry_of_a_data_tier_is_chosen_from_the_tier_then_the_recipe_and_refused_when_neither_is_known():
    body = {"tier1": {"steps": []}}
    assert data_entry({"data_engine": "python-polars"}, body, "tier1", where="x").engine == "python-polars"
    with pytest.raises(DataAnalysisRecipeError):
        data_entry({}, body, "tier1", where="x")
    with pytest.raises(DataAnalysisRecipeError):
        data_entry({"data_engine": "python-polars"}, {"tier1": {"data_engine": 3}}, "tier1", where="x")
    with pytest.raises(DataAnalysisRecipeError):
        data_entry({"data_engine": "python-plotnine"}, body, "tier1", where="x")


# -- the code chooses: the plot side ---------------------------------------------------------------------------------------------------

class Recorder:
    """A plot factory that only records the call; it stands for an engine that draws elsewhere."""
    built = []

    def __init__(self, **arguments):
        self.arguments = arguments
        Recorder.built.append(self)
        self.calls = []

    default_random_state = 99

    def render(self, df, recipe, plot_id, **kwargs):
        self.calls.append((recipe, plot_id, kwargs))
        return f"drawn by the recorder: {plot_id}"


@pytest.fixture
def plot_stand_in(monkeypatch):
    Recorder.built = []
    monkeypatch.setitem(REGISTRY, "python-recorder", PlotEngineEntry(engine="python-recorder", factory=Recorder))
    monkeypatch.setattr(engines, "ENGINES", {**engines.ENGINES, "plot_engine": ("python-plotnine", "python-recorder")})


TABLE = pl.DataFrame({"x": ["a", "b", "a"]})


def plot_recipe(**plots):
    base = {"target_dataset": "A", "mapping": {"x": "x"}, "layers": [{"name": "geom_bar"}], "ui_label": "P"}
    return {"plot_engine": "python-plotnine", "plot_defaults": {}, "plots": {pid: {**base, **own} for pid, own in plots.items()}}


def test_a_plot_without_an_own_engine_is_drawn_by_the_engine_of_the_recipe(plot_stand_in):
    drawn = PlotEngines().render(TABLE, plot_recipe(p={}), "p")
    assert hasattr(drawn, "data") and Recorder.built == []     # the plotnine factory drew it: it returns a plot object


def test_a_plot_with_its_own_engine_is_drawn_by_that_engine_and_the_next_plot_by_the_default(plot_stand_in):
    recipe = plot_recipe(p={"plot_engine": "python-recorder"}, q={})
    dispatcher = PlotEngines(palette_registry={"mine": ["#000000"]})
    assert dispatcher.render(TABLE, recipe, "p") == "drawn by the recorder: p"
    assert hasattr(dispatcher.render(TABLE, recipe, "q"), "data")
    (recorder,) = Recorder.built
    assert recorder.arguments == {"palette_registry": {"mine": ["#000000"]}}
    sent, plot_id, _ = recorder.calls[0]
    assert plot_id == "p" and sent["plot_engine"] == "python-recorder" and "plots" in sent
    assert recipe["plot_engine"] == "python-plotnine", "the recipe of the caller is not changed"


def test_the_default_engine_of_the_recipe_selects_the_factory_when_the_plot_names_none(plot_stand_in):
    recipe = {**plot_recipe(p={}), "plot_engine": "python-recorder"}
    assert PlotEngines().render(TABLE, recipe, "p") == "drawn by the recorder: p"


def test_the_arguments_of_the_call_reach_the_factory(plot_stand_in):
    recipe = plot_recipe(p={"plot_engine": "python-recorder"})
    dispatcher = PlotEngines()
    dispatcher.render(TABLE, recipe, "p", aesthetic_override={"alpha": 0.5})
    assert Recorder.built[0].calls[0][2] == {"aesthetic_override": {"alpha": 0.5}}


def test_a_factory_is_built_once_for_all_the_plots_of_its_engine(plot_stand_in):
    recipe = plot_recipe(p={"plot_engine": "python-recorder"}, q={"plot_engine": "python-recorder"})
    dispatcher = PlotEngines()
    dispatcher.render(TABLE, recipe, "p")
    dispatcher.render(TABLE, recipe, "q")
    assert len(Recorder.built) == 1


@pytest.mark.parametrize("name, recipe_changes, own, text", [
    ("an engine in the plot", {}, {"plot_engine": "r-ggplot2"}, WORDS),
    ("an engine in the recipe", {"plot_engine": "r-ggplot2"}, {}, WORDS),
    ("a data engine in a plot slot", {}, {"plot_engine": "python-polars"}, WORDS),
    ("an empty value in the plot", {}, {"plot_engine": None}, "names no plot_engine"),
])
def test_a_plot_whose_engine_the_app_has_no_library_for_is_refused_and_not_drawn_by_the_other_engine(name, recipe_changes, own, text):
    recipe = {**plot_recipe(p=own), **recipe_changes}
    with pytest.raises(VisualizationError) as caught:
        PlotEngines().render(TABLE, recipe, "p")
    assert text in str(caught.value) and "Plot 'p'" in str(caught.value) and "python-plotnine" in str(caught.value) + caught.value.tip


def test_a_recipe_with_no_plot_engine_anywhere_is_refused_and_gets_no_default():
    recipe = plot_recipe(p={})
    del recipe["plot_engine"]
    with pytest.raises(VisualizationError) as caught:
        PlotEngines().render(TABLE, recipe, "p")
    assert "names no plot_engine" in str(caught.value)


def test_a_plot_the_recipe_does_not_hold_is_left_to_the_factory_to_name():
    with pytest.raises(VisualizationError) as caught:
        PlotEngines().render(TABLE, plot_recipe(p={}), "missing")
    assert "missing" in str(caught.value) and WORDS not in str(caught.value)


def test_the_default_seed_is_the_one_of_the_plot_library():
    from viz_factory.viz_factory import DEFAULT_RANDOM_STATE
    assert PlotEngines().default_random_state == DEFAULT_RANDOM_STATE


def test_plot_entry_reads_the_entry_then_the_recipe():
    assert plot_entry({"plot_engine": "python-plotnine"}, {}, "p").engine == "python-plotnine"
    assert plot_entry(None, {"plot_engine": "python-plotnine"}, "p").engine == "python-plotnine"
    with pytest.raises(VisualizationError):
        plot_entry({}, {}, "p")


# -- every place that draws or runs goes through the registry -----------------------------------------------------------------------------

DIRECT = {"VizFactory", "DataWrangler", "DataAssembler"}
# the one-off migration of the old recipe format (format 0) runs Polars on purpose, to prove that the migrated recipe gives the same table
ALLOWED = {"assets/scripts/migrate_recipe_format.py"}


def test_no_code_of_the_app_or_of_the_scripts_builds_a_factory_a_wrangler_or_an_assembler_by_itself():
    offenders = []
    files = [p for folder in ("app/handlers", "app/modules", "app/src") for p in (ROOT / folder).rglob("*.py")] + list((ROOT / "assets/scripts").glob("*.py"))
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in ALLOWED:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
                if name in DIRECT:
                    offenders.append(f"{relative}:{node.lineno} {name}(")
    assert offenders == [], "build it through app/modules/engine_registry.py: " + ", ".join(offenders)


def test_the_server_gives_the_handlers_the_dispatcher_not_a_factory():
    source = (ROOT / "app/src/server.py").read_text(encoding="utf-8")
    assert "viz_factory = PlotEngines(" in source and "VizFactory" not in source


def test_an_unknown_engine_at_the_top_gives_one_t06_and_no_en02_per_step():
    # PROVISIONAL (plain-message rule): the one real message is not hidden among one line per step
    raw = recipe()
    raw["data_engine"] = "python-pandas"
    assert len(found(raw, "T06")) == 1 and found(raw, "EN02") == []
