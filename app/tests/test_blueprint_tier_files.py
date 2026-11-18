"""What Blueprint reads from and writes to the file of a tier (D-0250) and to the file of a plot (D-0252).

A table or a join writes each tier as its own key; when a tier is an `!include`, its file holds `{data_engine?, steps}` (one tier).
A plot written as `!include` holds the whole entry. Blueprint loads a file as the nodes of that one tier and saves the nodes back in
the same shape; a step of another tier is refused (it would change a result silently). The upload of a fragment reads a tier file
(`steps:`) or the tiers of a table (`tier1: {steps: [...]}`), never a `wrangling` key or a tier written as a list.

The closures of `define_server` are cut out by `ast` and run (as in `test_blueprint_failed_load.py`): `define_server` needs a session.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_tier_files.py -q
"""
import ast
from pathlib import Path

import pytest
import yaml

from app.handlers import blueprint_handlers
from app.modules.data_analysis_recipe_validator import fragment_old_shape, fragment_tiers, uploaded_recipe_report
from utils.recipe_factory import Include, minimal_join, minimal_plot, minimal_recipe, minimal_schema, write_fragment, write_recipe
from utils.recipe_loader import check_recipe_file

SOURCE = Path(blueprint_handlers.__file__)
NAMES = ("_parse_logic_to_nodes", "_upload_tiers", "_serialise_component_for_save", "_extract_wrangling_for_id")


def closures() -> dict:
    ns = dict(vars(blueprint_handlers))
    define = next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    for name in NAMES:
        fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == name)
        fn.decorator_list = []
        exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)
    return ns


@pytest.fixture(scope="module")
def fn():
    return closures()


STEP = {"action": "polars_select", "exprs": ["sample_id"]}
FILTER = {"action": "modif_filter", "column": "reads", "op": "ge", "value": 15, "na": "remove", "comment": "low reads"}


# -- reading a tier file or a table

def test_the_nodes_of_a_tier_file_are_tagged_with_its_tier(fn):
    nodes = fn["_parse_logic_to_nodes"]({"tier2": [dict(FILTER)]}, "f.yaml")
    assert nodes == [{"action": "modif_filter", "comment": "low reads", "_tier": "tier2",
                      "params": {"column": "reads", "op": "ge", "value": 15, "na": "remove"}}]


def test_a_step_without_a_comment_gets_the_name_of_its_source_as_comment(fn):
    assert fn["_parse_logic_to_nodes"]({"tier1": [dict(STEP)]}, "samples_t1.yaml")[0]["comment"] == "samples_t1.yaml"


def test_both_tiers_of_a_table_written_in_the_recipe_are_read_in_order(fn):
    cfg = type("Cfg", (), {"raw_config": {"data_schemas": {"s": {"tier1": {"steps": [dict(STEP)]}, "tier2": {"steps": [dict(FILTER)]}}}}})()
    tiers = fn["_extract_wrangling_for_id"](cfg, "s")
    assert tiers == {"tier1": [STEP], "tier2": [FILTER]}
    assert [n["_tier"] for n in fn["_parse_logic_to_nodes"](tiers, "Master: s")] == ["tier1", "tier2"]


@pytest.mark.parametrize("raw_config, wanted", [
    ({"joins": {"j": {"tier1": {"steps": [{"action": "polars_select", "exprs": ["a"]}]}}}}, "j"),
    ({"metadata_schema": {"tier1": {"steps": [{"action": "polars_select", "exprs": ["a"]}]}}}, "metadata_schema"),
    ({"additional_datasets_schemas": {"x": {"tier1": {"steps": [{"action": "polars_select", "exprs": ["a"]}]}}}}, "x"),
])
def test_a_join_a_metadata_table_and_an_additional_table_are_read_too(fn, raw_config, wanted):
    tiers = fn["_extract_wrangling_for_id"](type("Cfg", (), {"raw_config": raw_config})(), wanted)
    assert len(tiers["tier1"]) == 1 and tiers["tier2"] == []


def test_a_node_that_is_not_a_table_or_a_join_has_no_steps(fn):
    assert fn["_extract_wrangling_for_id"](type("Cfg", (), {"raw_config": {"data_schemas": {}}})(), "a_plot") == {"tier1": [], "tier2": []}


# -- the upload of a fragment

def test_an_upload_of_a_tier_file_goes_to_tier_one(fn):
    assert fn["_upload_tiers"]({"data_engine": "python-polars", "steps": [dict(STEP)]}) == {"tier1": [STEP]}


def test_an_upload_of_the_tiers_of_a_table_keeps_each_tier(fn):
    raw = {"tier1": {"steps": [dict(STEP)]}, "tier2": {"steps": [dict(FILTER)]}}
    assert fn["_upload_tiers"](raw) == {"tier1": [STEP], "tier2": [FILTER]}


@pytest.mark.parametrize("raw", [
    {"wrangling": {"tier1": [{"action": "polars_select", "exprs": ["a"]}]}},     # the old container
    {"tier1": [{"action": "polars_select", "exprs": ["a"]}]},                       # a tier written as a list
    {"tier3": {"steps": [{"action": "polars_select", "exprs": ["a"]}]}},           # a plot's tier: Blueprint never authors it
    {},
])
def test_an_old_shape_or_a_tier_of_a_plot_gives_no_steps_and_the_report_says_why(fn, raw):
    assert fn["_upload_tiers"](raw) == {}
    report = uploaded_recipe_report(raw)
    assert len(report) == 1 and report[0].startswith(("[UP01]", "[UP02]"))


def test_the_report_of_an_old_container_names_the_key_and_the_rewrite_tool():
    (line,) = uploaded_recipe_report({"wrangling": {"tier1": []}})
    assert "[UP02]" in line and "'wrangling'" in line and "migrate_recipe_engine_keys.py" in line
    assert fragment_old_shape({"tier2": []}).startswith("tier2 written as a list")
    assert fragment_old_shape({"tier1": {"steps": []}}) is None and fragment_old_shape(None) is None


def test_the_steps_of_an_uploaded_fragment_are_checked_one_by_one_with_their_place():
    raw = {"tier1": {"steps": [dict(STEP), {"action": "no_such_action"}]}, "tier2": {"steps": [{"column": "a"}]}}
    lines = uploaded_recipe_report(raw)
    assert any("tier1[2]" in line and "no_such_action" in line for line in lines)
    assert any("tier2[1]" in line and "[ST01]" in line for line in lines)
    assert [line for line in uploaded_recipe_report({"steps": [dict(STEP), {"action": "no_such_action"}]}) if "steps[2]" in line]


def test_the_places_of_a_fragment_are_the_tier_keys_and_steps():
    assert fragment_tiers({"steps": [1], "tier1": {"steps": [2]}, "tier2": {"steps": [3]}, "tier3": {"steps": [4]}}) == {
        "steps": [1], "tier1": [2], "tier2": [3]}
    assert fragment_tiers({"tier1": {"steps": "not a list"}}) == {}
    assert fragment_tiers([]) == {}


# -- saving a tier file

def test_a_tier_file_is_saved_as_data_engine_and_steps(fn):
    nodes = fn["_parse_logic_to_nodes"]({"tier1": [{**STEP, "comment": "keep the id"}, dict(FILTER)]}, "f.yaml")
    saved = fn["_serialise_component_for_save"]("wrangling", nodes, "data_engine: python-polars\nsteps: []\n", "tier1")
    assert list(saved) == ["data_engine", "steps"]
    assert saved["steps"] == [{**STEP, "comment": "keep the id"}, FILTER]


def test_a_tier_file_without_a_data_engine_is_saved_without_one(fn):
    nodes = fn["_parse_logic_to_nodes"]({"tier1": [dict(STEP)]}, "f.yaml")
    assert list(fn["_serialise_component_for_save"]("wrangling", nodes, "steps: []\n", "tier1")) == ["steps"]


def test_a_tier_file_with_no_step_left_is_saved_as_an_empty_list(fn):
    assert fn["_serialise_component_for_save"]("wrangling", [], "steps: []\n", "tier2") == {"steps": []}


def test_a_step_of_another_tier_is_refused_and_named(fn):
    nodes = fn["_parse_logic_to_nodes"]({"tier1": [dict(STEP)], "tier2": [dict(FILTER)]}, "x")
    with pytest.raises(ValueError, match="modif_filter.*tier2.*this file is tier1"):
        fn["_serialise_component_for_save"]("wrangling", nodes, "steps: []\n", "tier1")


def test_a_new_step_defaults_to_tier_one_so_a_tier_one_file_saves_it(fn):
    stub = {"action": "polars_select", "params": {"exprs": ["a"]}, "comment": "", "_tier": "tier1"}
    assert fn["_serialise_component_for_save"]("wrangling", [stub], "steps: []\n", "tier1") == {
        "steps": [{"action": "polars_select", "exprs": ["a"]}]}


@pytest.mark.parametrize("tier", [None, "tier3", ""])
def test_a_file_that_is_not_a_tier_cannot_be_saved(fn, tier):
    with pytest.raises(ValueError, match="not the tier 1 or the tier 2"):
        fn["_serialise_component_for_save"]("wrangling", [], "steps: []\n", tier)


def test_the_file_of_a_join_and_unknown_roles_are_not_saved_from_here(fn):
    for role in ("join", "input_fields", "output_fields", "plot_wrangling"):
        with pytest.raises(ValueError, match="not supported"):
            fn["_serialise_component_for_save"](role, [], "steps: []\n", "tier1")


# -- saving a plot

ENTRY_TEXT = ("plot_engine: python-plotnine\nui_label: Per year\nui_title: Samples per year\ndescription: d\n"
              "taxonomy: {family: Distribution}\ntarget_dataset: C\nmapping: {x: year}\nlayers:\n- name: geom_bar\n  params: {}\n")


def test_a_plot_is_saved_as_the_whole_entry_with_the_keys_of_the_app_first(fn):
    nodes = [{"component": "__mapping__", "params": {"x": "country"}, "comment": ""},
             {"component": "geom_bar", "params": {}, "comment": ""}, {"component": "geom_point", "params": {}, "comment": ""}]
    saved = fn["_serialise_component_for_save"]("plot_spec", nodes, ENTRY_TEXT, "tier1")
    assert list(saved) == ["plot_engine", "ui_label", "ui_title", "description", "taxonomy", "target_dataset", "mapping", "layers"]
    assert saved["mapping"] == {"x": "country"} and [layer["name"] for layer in saved["layers"]] == ["geom_bar", "geom_point"]
    assert saved["ui_title"] == "Samples per year" and saved["taxonomy"] == {"family": "Distribution"}
    assert not {"spec", "label", "title"} & set(saved)


def test_a_plot_with_tier3_keeps_it_last(fn):
    text = ENTRY_TEXT + "tier3:\n  steps: []\n"
    saved = fn["_serialise_component_for_save"]("plot_spec", [{"component": "geom_bar", "params": {}, "comment": ""}], text, None)
    assert list(saved)[-1] == "tier3" and saved["tier3"] == {"steps": []}


# -- the whole round trip on files: what Blueprint saves, the checker accepts

def test_a_tier_file_and_a_plot_file_saved_by_blueprint_give_a_recipe_the_checker_accepts(fn, tmp_path):
    samples = minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "Int64"}, entity_key="sample_id", label="Samples")
    samples["tier1"] = Include("tiny/wrangling/samples_t1.yaml")
    plots = {"per_year": Include("tiny/plots/per_year.yaml")}
    recipe = minimal_recipe("tiny", schemas={"samples": samples}, plots=plots)
    write_fragment(tmp_path / "tiny" / "wrangling" / "samples_t1.yaml", {"data_engine": "python-polars", "steps": []})
    write_fragment(tmp_path / "tiny" / "plots" / "per_year.yaml", minimal_plot("samples", {"x": "year"}, label="Per year"))
    master = write_recipe(tmp_path / "tiny.yaml", recipe)
    assert check_recipe_file(master, "build").errors == []

    tier_file = tmp_path / "tiny" / "wrangling" / "samples_t1.yaml"
    nodes = fn["_parse_logic_to_nodes"]({"tier1": [{**STEP, "comment": "keep the id"}]}, "x")
    tier_file.write_text(blueprint_handlers.safe_dump_recipe(
        fn["_serialise_component_for_save"]("wrangling", nodes, tier_file.read_text(), "tier1")), encoding="utf-8")
    plot_file = tmp_path / "tiny" / "plots" / "per_year.yaml"
    plot_nodes = [{"component": "__mapping__", "params": {"x": "year"}, "comment": ""}, {"component": "geom_bar", "params": {}, "comment": ""}]
    plot_file.write_text(blueprint_handlers.safe_dump_recipe(
        fn["_serialise_component_for_save"]("plot_spec", plot_nodes, plot_file.read_text(), None)), encoding="utf-8")

    assert yaml.safe_load(tier_file.read_text()) == {"data_engine": "python-polars", "steps": [{**STEP, "comment": "keep the id"}]}
    assert check_recipe_file(master, "build").errors == []


# -- the inventory of groups and plots (a plot in its own file is named by its file)

class Val:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def inventory_html(master: Path) -> str:
    ns = dict(vars(blueprint_handlers))
    define = next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == "bp_groups_inventory_ui")
    fn.decorator_list = []
    ns.update(input={"stored_data_analysis_recipe_selector": str(master)}, safe_input=lambda i, k, d=None: i.get(k, d), _groups_refresh=Val(0))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "bp_groups_inventory_ui", "exec"), ns)
    return str(ns["bp_groups_inventory_ui"]())


def test_the_inventory_names_the_groups_and_the_plots_by_their_ui_label_in_the_recipe_or_in_the_file(tmp_path):
    samples = minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "Int64"}, entity_key="sample_id", label="Samples")
    plots = {"inline_plot": minimal_plot("samples", {"x": "year"}, label="Written in the recipe"),
             "file_plot": Include("tiny/plots/file_plot.yaml"), "lost_plot": Include("tiny/plots/lost.yaml")}
    recipe = minimal_recipe("tiny", schemas={"samples": samples}, plots=plots)
    recipe["analysis_groups"]["main"]["ui_label"] = "The group name"
    write_fragment(tmp_path / "tiny" / "plots" / "file_plot.yaml", minimal_plot("samples", {"x": "year"}, label="Written in its file"))
    html = inventory_html(write_recipe(tmp_path / "tiny.yaml", recipe))
    assert "The group name" in html and "Written in the recipe" in html and "Written in its file" in html
    assert "lost_plot" in html          # a plot whose file is missing is listed by its id, not hidden
