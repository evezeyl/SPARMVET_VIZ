"""Every program that WRITES a recipe writes recipe format 1 (work order W8): one test per writer.

Each writer is run for real, and what it wrote is judged three ways:
  1. the recipe checker `check_recipe_file`, with the REAL registries (actions, plot components) as catalogs;
  2. the loader of the app (`validate_data_analysis_recipe`, which loads through `ConfigManager`);
  3. where the recipe has data, the engine (`validate_data_analysis_recipe_data`, `DataOrchestrator`).

The writers: `utils.recipe_factory` (the shared helper), the forked recipe of an export (`build_mode2_recipe`, written
the way `export_handlers.py` writes it), Blueprint's new-recipe form (`new_recipe_draft`), Blueprint's branch
(`generate_branch_plan`) and the script `assets/scripts/create_data_analysis_recipe.py`. The Test Lab writers have their
own tests in `libs/test_lab/tests` (`TestWritersEmitFormatOne`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_writers_emit_format_one.py -q
"""
import importlib.util
from pathlib import Path

import pytest
import yaml

import transformer.actions  # noqa: F401  (registers the actions)
import viz_factory.viz_factory  # noqa: F401  (registers the plot components)
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe, validate_data_analysis_recipe_data
from app.modules.orchestrator import DataOrchestrator
from blueprint_arch.data_analysis_recipe_navigator import generate_branch_plan
from blueprint_arch.new_recipe import new_recipe_draft
from blueprint_arch.t3_translator import build_mode2_recipe
from transformer.actions.base import ACTION_SCHEMAS
from utils import action_names
from utils.config_loader import ConfigManager
from utils.recipe_factory import minimal_join, minimal_plot, minimal_recipe, minimal_schema, write_recipe
from utils.recipe_loader import check_recipe_file, load_recipe
from viz_factory.arguments import argument_catalog
from viz_factory.registry import COMPONENT_SCHEMAS

ROOT = Path(__file__).resolve().parents[2]
OLD_WORDS = ("output_fields", "final_contract", "display_name", "is_primary_key", "source_name", "_t3_origin",
             "categorical", "numeric", "mandatory", "show_legend", "height")


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "assets" / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


create_script = _load_script("create_data_analysis_recipe")


@pytest.fixture(scope="module")
def catalogs():
    """The registries as plain data, the way the recipe checker receives them (spec section 14)."""
    return {
        "actions": dict(ACTION_SCHEMAS),
        "components": set(COMPONENT_SCHEMAS),
        "component_arguments": argument_catalog(),
        "themes": {name for name in COMPONENT_SCHEMAS if name.startswith("theme_")},
    }


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A small project: the working folder is its root, so the data paths of a recipe are relative, as the format asks."""
    (tmp_path / "data").mkdir()
    (tmp_path / "recipes").mkdir()
    (tmp_path / "data" / "samples.tsv").write_text(
        "sample_id\tcountry\treads\ns1\tNO\t10\ns2\tSE\t20\ns3\tNO\t30\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def judged(path: Path, catalogs: dict, profile: str = "run"):
    """The errors of the checker with every check switched on; fails the test if a registry check did not run."""
    result = check_recipe_file(path, profile, catalogs=catalogs, roots=[Path.cwd()], base=Path.cwd())
    assert {"structure", "actions", "components"} <= result.coverage
    return [problem.text() for problem in result.errors]


def tiny_recipe() -> dict:
    """One table, one step, one join that publishes two columns, one plot: built with the factory only."""
    schemas = {"samples": minimal_schema(
        "data/samples.tsv", {"sample_id": "String", "country": "String", "reads": "Int64"}, entity_key="sample_id",
        tier1=[{"action": action_names.FILTER, "column": "reads", "op": "ge", "value": 15, "na": "remove"}])}
    joins = {"C": minimal_join(["samples"], [{"action": action_names.SELECT, "exprs": ["sample_id", "country"]}], label="Samples")}
    plots = {"tiny_plot": minimal_plot("C", {"x": "country"}, label="Samples per country")}
    return minimal_recipe("tiny", schemas=schemas, joins=joins, plots=plots)


def rows(frame):
    return sorted(frame.collect().to_dicts(), key=lambda row: row["sample_id"])


# -- 1. the factory

def test_a_recipe_of_the_factory_passes_the_checker_loads_and_runs(project, catalogs):
    path = write_recipe(project / "recipes" / "tiny.yaml", tiny_recipe())
    assert judged(path, catalogs) == []
    assert validate_data_analysis_recipe(path) == []
    assert validate_data_analysis_recipe_data(path, project / "data") == []
    orchestrator = DataOrchestrator(project / "recipes", project / "data")
    table = orchestrator.materialize_tier1("tiny", "C", project / "anchors" / "C.parquet")
    assert rows(table) == [{"sample_id": "s2", "country": "SE"}, {"sample_id": "s3", "country": "NO"}]


def test_the_default_recipe_of_the_factory_passes_the_checker_with_the_real_registries(project, catalogs):
    path = write_recipe(project / "recipes" / "minimal.yaml", minimal_recipe())
    assert judged(path, catalogs) == []
    assert validate_data_analysis_recipe(path) == []


# -- 2. the forked recipe of an export

T3_OF_THE_PLOT = {"tiny_plot": [
    {"id": "n1", "node_type": "filter_row", "params": {"column": "country", "op": "eq", "value": "NO"}, "reason": "one country"},
    {"id": "n2", "node_type": "exclusion_row", "params": {"column": "sample_id", "op": "not_in", "value": ["s9"]}, "reason": "a bad sample"},
    {"id": "n3", "node_type": "drop_column", "params": {"column": "country"}, "reason": "not needed"},
]}


def export_fork(project: Path, t3_by_plot: dict) -> Path:
    """What the export does (export_handlers.py, "Mode 2 add-on"): load, fork, write as YAML into the bundle."""
    source = write_recipe(project / "recipes" / "tiny.yaml", tiny_recipe())
    forked, skipped = build_mode2_recipe(ConfigManager(str(source)).raw_config, t3_by_plot)
    assert skipped == {}
    bundle = project / "bundle" / "data_analysis_recipes_reproducibility"
    bundle.mkdir(parents=True)
    path = bundle / "tiny.yaml"
    path.write_text(yaml.safe_dump(forked, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def test_the_forked_recipe_of_an_export_passes_the_checker_and_loads(project, catalogs):
    path = export_fork(project, T3_OF_THE_PLOT)
    assert judged(path, catalogs) == []
    assert validate_data_analysis_recipe(path) == []
    text = path.read_text(encoding="utf-8")
    assert text.startswith("id: tiny\nspec_version: 1\n")
    assert not [word for word in OLD_WORDS if word in text]


def test_the_forked_recipe_gives_the_audited_table_when_it_is_run(project, catalogs):
    """The steps of the audit are in the fork, so the engine alone rebuilds what the user validated."""
    path = export_fork(project, T3_OF_THE_PLOT)
    raw, problems = load_recipe(path)
    assert problems == []
    fork_id = raw["analysis_groups"]["main"]["plots"]["tiny_plot"]["spec"]["target_dataset"]
    assert fork_id == "C__t3_tiny_plot"
    orchestrator = DataOrchestrator(path.parent, project / "data")
    anchor = project / "anchors" / "fork.parquet"
    assert rows(orchestrator.materialize_tier2("tiny", fork_id, anchor)) == [{"sample_id": "s3"}]
    # the join the fork was copied from is still there and gives the table without the audit steps
    assert rows(orchestrator.materialize_tier2("tiny", "C", project / "anchors" / "C.parquet")) == [
        {"sample_id": "s2", "country": "SE"}, {"sample_id": "s3", "country": "NO"}]


def test_an_export_without_audit_steps_writes_the_recipe_unchanged(project, catalogs):
    path = export_fork(project, {})
    assert judged(path, catalogs) == []
    raw, _ = load_recipe(path)
    assert raw == tiny_recipe()


# -- 3. Blueprint's new-recipe form

def new_draft(project: Path) -> Path:
    recipe = new_recipe_draft("my_analysis", "My analysis", description="", author="", created="2026-11-14")
    return write_recipe(project / "recipes" / "my_analysis.yaml", recipe)


def test_the_new_recipe_of_blueprint_is_a_valid_draft(project, catalogs):
    path = new_draft(project)
    assert judged(path, catalogs, profile="build") == []
    # the only thing a draft lacks to be shown in HOME is a plot
    assert [problem.code for problem in check_recipe_file(path, "run", catalogs=catalogs).errors] == ["T09"]
    text = path.read_text(encoding="utf-8")
    assert not [word for word in OLD_WORDS if word in text] and "\n  name:" not in text


@pytest.mark.xfail(strict=True, reason="ConfigManager refuses a recipe without a plot (it exits), so a draft that is "
                   "valid in profile build cannot be loaded by the app; needs a decision (reported with work order W8)")
def test_the_new_recipe_of_blueprint_loads_through_the_loader_of_the_app(project):
    assert validate_data_analysis_recipe(new_draft(project)) == []


# -- 4. Blueprint's branch

def apply_plan(master: Path, plan: dict) -> None:
    assert plan["ok"], plan["error"]
    for fragment in plan["fragments"]:
        target = Path(fragment["abs_path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(fragment["content"], encoding="utf-8")
    master.write_text(plan["new_master_text"], encoding="utf-8")


@pytest.mark.parametrize("node, role, new_id", [
    ("samples", "wrangling", "samples_b"), ("C", "join", "C_b"), ("tiny_plot", "plot_spec", "tiny_plot_b")])
def test_a_branch_of_blueprint_passes_the_checker_loads_and_reads_its_data(project, catalogs, node, role, new_id):
    path = write_recipe(project / "recipes" / "tiny.yaml", tiny_recipe())
    apply_plan(path, generate_branch_plan(str(path), node, role, new_id))
    assert judged(path, catalogs) == []
    assert validate_data_analysis_recipe(path) == []
    assert validate_data_analysis_recipe_data(path, project / "data") == []
    assert "output_fields" not in path.read_text(encoding="utf-8")


def test_a_join_branch_runs_and_gives_the_table_of_its_base(project, catalogs):
    path = write_recipe(project / "recipes" / "tiny.yaml", tiny_recipe())
    apply_plan(path, generate_branch_plan(str(path), "C", "join", "C_b"))
    orchestrator = DataOrchestrator(project / "recipes", project / "data")
    table = orchestrator.materialize_tier1("tiny", "C_b", project / "anchors" / "C_b.parquet")
    assert [row["sample_id"] for row in rows(table)] == ["s2", "s3"]
    assert table.collect_schema().names() == ["sample_id", "country", "reads"]


# -- 5. the script create_data_analysis_recipe.py

def run_script(*arguments: str) -> int:
    try:
        create_script.main(list(arguments))
    except SystemExit as stop:
        return int(stop.code or 0)
    return 0


def written_files(folder: Path):
    return sorted(str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file())


def test_the_script_writes_a_recipe_that_passes_the_checker_loads_and_reads_its_data(project, catalogs):
    (project / "data" / "meta.tsv").write_text("sample_id\tyear\ns1\t2020\ns2\t2021\n", encoding="utf-8")
    code = run_script("--data_files", "data/samples.tsv", "--metadata_file", "data/meta.tsv",
                      "--primary_key_data", "sample_id", "--primary_key_metadata", "sample_id",
                      "--out_file", "recipes/scaffold.yaml")
    assert code == 0
    path = project / "recipes" / "scaffold.yaml"
    assert judged(path, catalogs) == []
    assert validate_data_analysis_recipe(path) == []
    assert validate_data_analysis_recipe_data(path, project / "data") == []
    raw, problems = load_recipe(path)
    assert problems == []
    assert list(raw)[:5] == ["id", "spec_version", "data_engine", "plot_engine", "info"]
    assert raw["id"] == "scaffold" and raw["info"]["label"]
    samples = raw["data_schemas"]["samples"]
    assert samples["source"] == {"type": "local_tsv", "path": "data/samples.tsv"}
    assert samples["null_values"] == [] and samples["strip"] is False
    assert {name: field["type"] for name, field in samples["input_fields"].items()} == {
        "sample_id": "String", "country": "String", "reads": "Int64"}
    assert samples["input_fields"]["sample_id"]["is_entity_key"] is True
    assert "is_entity_key" not in samples["input_fields"]["country"]
    assert raw["metadata_schema"]["input_fields"]["year"]["type"] == "Int64"
    assert raw["metadata_schema"]["input_fields"]["sample_id"]["is_entity_key"] is True


def test_the_script_writes_no_old_word_in_any_file(project):
    assert run_script("--data_files", "data/samples.tsv", "--primary_key_data", "sample_id", "--out_file", "recipes/scaffold.yaml") == 0
    files = written_files(project / "recipes")
    assert files == ["scaffold.yaml", "scaffold/samples_fields.yaml", "scaffold/samples_wrangling.yaml"]
    for name in files:
        text = (project / "recipes" / name).read_text(encoding="utf-8")
        assert not [word for word in OLD_WORDS if word in text], name


def test_the_fragments_of_the_script_hold_the_value_itself_and_keep_their_comment(project):
    assert run_script("--data_files", "data/samples.tsv", "--primary_key_data", "sample_id", "--out_file", "recipes/scaffold.yaml") == 0
    wrangling = (project / "recipes" / "scaffold" / "samples_wrangling.yaml").read_text(encoding="utf-8")
    assert wrangling.startswith("# ")
    assert yaml.safe_load(wrangling) == {"tier1": []}
    fields = yaml.safe_load((project / "recipes" / "scaffold" / "samples_fields.yaml").read_text(encoding="utf-8"))
    assert list(fields) == ["sample_id", "country", "reads"]


def test_a_column_header_that_is_not_a_plain_name_keeps_its_original_name(project, catalogs):
    (project / "data" / "odd.tsv").write_text("Sample ID\tRead-Count (n)\ns1\t10\n", encoding="utf-8")
    assert run_script("--data_files", "data/odd.tsv", "--primary_key_data", "Sample ID", "--out_file", "recipes/scaffold.yaml") == 0
    path = project / "recipes" / "scaffold.yaml"
    assert judged(path, catalogs) == []
    fields = load_recipe(path)[0]["data_schemas"]["odd"]["input_fields"]
    assert fields["sample_id"] == {"type": "String", "original_name": "Sample ID", "label": "Sample Id", "is_entity_key": True}
    assert fields["read_count_n"]["original_name"] == "Read-Count (n)"
    assert validate_data_analysis_recipe_data(path, project / "data") == []


def test_a_table_with_a_header_and_no_row_gives_a_valid_recipe(project, catalogs):
    (project / "data" / "empty_rows.tsv").write_text("sample_id\tvalue\n", encoding="utf-8")
    assert run_script("--data_files", "data/empty_rows.tsv", "--primary_key_data", "sample_id", "--out_file", "recipes/scaffold.yaml") == 0
    assert judged(project / "recipes" / "scaffold.yaml", catalogs) == []


@pytest.mark.parametrize("make, arguments, word", [
    # a comma-separated file: the recipe format reads tab-separated files and parquet only
    (lambda p: (p / "data" / "table.csv").write_text("a,b\n1,2\n"), ["--data_files", "data/table.csv"], "tab-separated"),
    # a file that does not exist
    (lambda p: None, ["--data_files", "data/none.tsv"], "not found"),
    # an empty file has no column to describe
    (lambda p: (p / "data" / "nothing.tsv").write_text(""), ["--data_files", "data/nothing.tsv"], "nothing.tsv"),
    # two files that give the same table id
    (lambda p: (p / "data" / "test_data_samples.tsv").write_text("x\n1\n"),
     ["--data_files", "data/samples.tsv", "data/test_data_samples.tsv"], "same table id"),
    # no data file at all
    (lambda p: None, [], "--data_files"),
])
def test_what_the_script_refuses_is_said_and_nothing_is_written(project, capsys, make, arguments, word):
    make(project)
    code = run_script(*arguments, "--primary_key_data", "sample_id", "--out_file", "recipes/scaffold.yaml")
    assert code != 0
    assert word in capsys.readouterr().out
    assert written_files(project / "recipes") == []


def test_a_data_file_outside_the_project_is_refused(project, tmp_path_factory, capsys):
    outside = tmp_path_factory.mktemp("elsewhere") / "far.tsv"
    outside.write_text("sample_id\ns1\n", encoding="utf-8")
    code = run_script("--data_files", str(outside), "--primary_key_data", "sample_id", "--out_file", "recipes/scaffold.yaml")
    assert code != 0 and "inside the project" in capsys.readouterr().out
    assert written_files(project / "recipes") == []


def test_the_script_does_not_replace_a_recipe_that_exists(project, capsys):
    arguments = ("--data_files", "data/samples.tsv", "--primary_key_data", "sample_id", "--out_file", "recipes/scaffold.yaml")
    assert run_script(*arguments) == 0
    (project / "recipes" / "scaffold.yaml").write_text("# the work of the author\n", encoding="utf-8")
    assert run_script(*arguments) != 0
    assert "already exist" in capsys.readouterr().out
    assert (project / "recipes" / "scaffold.yaml").read_text(encoding="utf-8") == "# the work of the author\n"


def test_a_table_without_the_key_column_is_written_without_a_key_and_the_script_says_so(project, catalogs, capsys):
    code = run_script("--data_files", "data/samples.tsv", "--primary_key_data", "isolate", "--out_file", "recipes/scaffold.yaml")
    assert code == 0
    said = capsys.readouterr().out
    assert "isolate" in said and "samples.tsv" in said
    path = project / "recipes" / "scaffold.yaml"
    assert judged(path, catalogs) == []
    fields = load_recipe(path)[0]["data_schemas"]["samples"]["input_fields"]
    assert not [name for name, field in fields.items() if "is_entity_key" in field]


def test_the_help_of_the_script_says_what_it_writes(capsys):
    assert run_script("--help") == 0
    text = capsys.readouterr().out
    assert "format 1" in text and "--data_files" in text and "--out_file" in text
