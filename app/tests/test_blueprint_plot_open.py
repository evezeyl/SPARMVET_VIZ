"""Blueprint opens a plot node in recipe format 1 (D-0252) and saves it back in the same shape.

The branch change moved a plot to one whole entry (the content, no `spec:` key), written inline or as an `!include`d file of its own,
and the demo recipe (written by the migration tool, as an author writes by hand) leaves the path of that include unquoted, while the
recipe factory of the tests (`yaml.dump`) quotes it. Blueprint finds the file of a node through the list of includes of
the recipe: with a scan that saw quoted paths only, every plot of the demo recipe opened as "Imported 0 steps" (no mapping, no
layers, no table). The tests below run the real closures of `define_server` on the real demo recipe and on small recipes:

  - the tap of each of the 17 plots of `1_test_data_ST22_dummy` opens its own file, with its mapping, its layers and its table;
  - a plot written inline opens with the same mapping and layers (nothing is saved from it: there is no file);
  - an edit of a mapping value and of a layer value, saved through the save closure, writes the plot file in the same shape,
    changes only that value, and the checker still accepts the recipe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_plot_open.py -q
"""
import ast
import os
import shutil
from pathlib import Path

import pytest
import yaml

from app.handlers import blueprint_handlers
from app.modules.blueprint_plot_view import MAPPING_NODE, plot_view
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
from app.tests.test_blueprint_failed_load import Harness, Val, _closure
from utils.recipe_factory import Include, minimal_plot, minimal_recipe, minimal_schema, write_fragment, write_recipe

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(blueprint_handlers.__file__)
DEMO = "1_test_data_ST22_dummy"
PIPELINES = ROOT / "config" / "data_analysis_recipes" / "pipelines"


# -- the pure reading of a plot entry

ENTRY = {"ui_label": "P", "target_dataset": "samples", "plot_engine": "python-plotnine",
         "mapping": {"x": "year", "fill": "country"},
         "layers": [{"name": "geom_bar", "params": {}}, {"name": "labs", "params": {"title": "T"}}]}


def test_the_view_of_an_entry_is_its_table_then_the_mapping_then_each_layer():
    target, nodes = plot_view(ENTRY)
    assert target == "samples"
    assert [n["component"] for n in nodes] == [MAPPING_NODE, "geom_bar", "labs"]
    assert nodes[0]["params"] == {"x": "year", "fill": "country"} and nodes[2]["params"] == {"title": "T"}


@pytest.mark.parametrize("entry", [None, [], "text", 3])
def test_what_is_not_an_entry_has_no_table_and_no_nodes(entry):
    assert plot_view(entry) == (None, [])


def test_an_entry_without_a_mapping_or_layers_gives_no_nodes_not_an_error():
    assert plot_view({"target_dataset": "samples"}) == ("samples", [])


def test_the_keys_of_the_app_are_not_nodes():
    _, nodes = plot_view(ENTRY)
    assert not [n for n in nodes if n["component"] in ("ui_label", "plot_engine")]


def test_the_old_spec_key_is_not_read_as_the_content():
    """An entry written in the old shape has no mapping at the top: the view is empty (the checker refuses such a recipe)."""
    assert plot_view({"spec": {"target_dataset": "samples", "mapping": {"x": "a"}, "layers": [{"name": "geom_bar"}]}})[1] == []


# -- the closures of Blueprint, run for real

class Orchestrator:
    def __init__(self):
        self.collections = []

    def materialize_tier1(self, **kwargs):
        self.collections.append(kwargs["collection_id"])


class Bootloader:
    def __init__(self, folder):
        self.folder = folder

    def get_location(self, key):
        return self.folder


class Input:
    """`input.<name>()` for the reactive inputs and `.get` for safe_input."""

    def __init__(self, **values):
        self.values = values

    def __getattr__(self, name):
        return lambda: self.values.get(name)

    def get(self, key, default=None):
        return self.values.get(key, default)


class Blueprint(Harness):
    def __init__(self, folder):
        super().__init__()
        self.orchestrator = Orchestrator()
        self.ws.active_viz_id = Val(None)
        self.ws.active_anchor_path = Val("")
        self.ns.update(orchestrator=self.orchestrator, bootloader=Bootloader(folder), tell_inputs_changed=lambda *a, **k: None,
                       _snapshot_state=lambda: None, _tell_save_outcome=lambda: None,
                       _selection_signal=None)
        tree = ast.parse(SOURCE.read_text())
        for name in ("_parse_logic_to_nodes", "_extract_wrangling_for_id", "_serialise_component_for_save",
                     "_sync_selector_from_node_click", "_handle_data_analysis_recipe_save_internal", "_bp_apply_node_handler"):
            exec(compile(ast.fix_missing_locations(ast.Module(body=[_closure(tree, name)], type_ignores=[])), name, "exec"), self.ns)

    def open_recipe(self, path):
        self.ns["input"] = Input(stored_data_analysis_recipe_selector=str(path))
        assert self.ns["_do_refresh_blueprint"](str(path)) is not None, self.ui.notifications
        self.recipe_path = str(path)

    def tap(self, node_id):
        self.ui.notifications.clear()
        self.ns["input"] = Input(blueprint_node_clicked=node_id, stored_data_analysis_recipe_selector=self.recipe_path)
        self.ns["_sync_selector_from_node_click"]()

    def shown(self):
        stack = self.ws.logic_stack.get()
        return {
            "mapping": next((n["params"] for n in stack if n.get("component") == MAPPING_NODE), None),
            "layers": [n["component"] for n in stack if n.get("component") not in (None, MAPPING_NODE)],
            "info": self.ws.active_component_info.get(),
            "file": self.ws.active_component_path.get(),
        }

    def imported_zero(self):
        return [m for _, m in self.ui.notifications if "Imported 0 steps" in m]


@pytest.fixture()
def blueprint(monkeypatch, tmp_path):
    b = Blueprint(tmp_path)
    monkeypatch.setattr(blueprint_handlers, "ui", b.ui)
    return b


def plot_ids_and_files():
    """(plot id, file of its entry) of each plot of the demo recipe, read straight from the recipe file."""
    recipe = yaml.load((PIPELINES / f"{DEMO}.yaml").read_text(), Loader=_IncludeLoader)
    return [(pid, entry) for group in recipe["analysis_groups"].values() for pid, entry in group["plots"].items()]


class _IncludeLoader(yaml.SafeLoader):
    pass


_IncludeLoader.add_constructor("!include", lambda loader, node: Include(loader.construct_scalar(node)))


def test_the_demo_recipe_has_17_plots_each_in_a_file_of_its_own():
    plots = plot_ids_and_files()
    assert len(plots) == 17 and all(isinstance(entry, Include) for _, entry in plots)


@pytest.mark.parametrize("plot_id, include", plot_ids_and_files(), ids=[p for p, _ in plot_ids_and_files()])
def test_the_tap_of_a_demo_plot_opens_its_file_with_its_mapping_its_layers_and_its_table(blueprint, plot_id, include):
    path = PIPELINES / f"{DEMO}.yaml"
    entry = yaml.safe_load((PIPELINES / include.path).read_text())
    blueprint.open_recipe(path)

    blueprint.tap(plot_id)

    shown = blueprint.shown()
    assert not blueprint.imported_zero(), blueprint.ui.notifications
    assert shown["info"]["role"] == "plot_spec" and shown["info"]["schema_id"] == plot_id
    assert Path(shown["file"]) == (PIPELINES / include.path).resolve()
    assert shown["mapping"] == entry["mapping"]
    assert shown["layers"] == [layer["name"] for layer in entry["layers"]] and shown["layers"]
    assert blueprint.orchestrator.collections == [entry["target_dataset"]]
    assert blueprint.ws.active_viz_id.get() == plot_id


# -- an inline plot

@pytest.fixture()
def small_recipe(tmp_path):
    """samples with two plots: `inline` written in the recipe, `filed` as the whole entry in its own file."""
    schema = minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "Int64", "country": "String"},
                            entity_key="sample_id", label="Samples")
    plots = {
        "inline": minimal_plot("samples", {"x": "year", "fill": "country"}, [{"name": "geom_bar", "params": {}}], label="Inline"),
        "filed": Include("small/plots/filed.yaml"),
    }
    recipe = minimal_recipe("small", schemas={"samples": schema}, plots=plots)
    write_fragment(tmp_path / "small" / "plots" / "filed.yaml",
                   minimal_plot("samples", {"x": "country"}, [{"name": "geom_bar", "params": {}}], label="Filed"))
    return write_recipe(tmp_path / "small.yaml", recipe)


def test_an_inline_plot_opens_with_its_mapping_and_layers(blueprint, small_recipe):
    blueprint.open_recipe(small_recipe)

    blueprint.tap("inline")

    shown = blueprint.shown()
    assert shown["mapping"] == {"x": "year", "fill": "country"} and shown["layers"] == ["geom_bar"]
    assert shown["file"] == ""                      # nothing to save into: the entry is part of the recipe
    assert shown["info"]["role"] == "plot_spec"
    assert blueprint.orchestrator.collections == ["samples"]


def test_a_plot_in_its_own_file_opens_the_file_when_its_include_is_unquoted(blueprint, small_recipe):
    # the factory quotes the path; the demo recipe does not: this is the form that failed
    small_recipe.write_text(small_recipe.read_text().replace("!include 'small/plots/filed.yaml'", "!include small/plots/filed.yaml"))
    assert "!include small/plots/filed.yaml" in small_recipe.read_text()
    blueprint.open_recipe(small_recipe)

    blueprint.tap("filed")

    shown = blueprint.shown()
    assert Path(shown["file"]).name == "filed.yaml"
    assert shown["mapping"] == {"x": "country"} and shown["layers"] == ["geom_bar"]
    assert not blueprint.imported_zero()


def test_a_plot_in_its_own_file_opens_the_file_when_its_include_is_quoted(blueprint, small_recipe):
    assert "!include 'small/plots/filed.yaml'" in small_recipe.read_text()
    blueprint.open_recipe(small_recipe)

    blueprint.tap("filed")

    assert blueprint.shown()["mapping"] == {"x": "country"} and not blueprint.imported_zero()


# -- the round trip: edit, save, check

@pytest.fixture()
def scratch_demo(tmp_path):
    """A copy of the demo recipe in a project root of its own (config and assets linked), so that a save changes no shipped file."""
    root = tmp_path / "root"
    pipelines = root / "config" / "data_analysis_recipes" / "pipelines"
    pipelines.mkdir(parents=True)
    for child in (ROOT / "config").iterdir():
        if child.name != "data_analysis_recipes":
            os.symlink(child, root / "config" / child.name)
    os.symlink(ROOT / "assets", root / "assets")
    shutil.copy2(PIPELINES / f"{DEMO}.yaml", pipelines)
    shutil.copytree(PIPELINES / DEMO, pipelines / DEMO)
    return pipelines / f"{DEMO}.yaml"


def save(blueprint, recipe_path, plot_id, edit):
    """Open a plot of the copy, let `edit(stack)` change the stack, press Save; returns (file path, text before, text after)."""
    blueprint.open_recipe(recipe_path)
    blueprint.tap(plot_id)
    file = Path(blueprint.ws.active_component_path.get())
    before = file.read_text()
    blueprint.ws.logic_stack.set(edit(blueprint.ws.logic_stack.get()))
    blueprint.ns["_handle_data_analysis_recipe_save_internal"]()
    return file, before, file.read_text()


def test_saving_a_plot_without_a_change_keeps_every_value_and_the_checker_accepts_the_recipe(blueprint, scratch_demo):
    assert validate_data_analysis_recipe(scratch_demo) == []
    file, before, after = save(blueprint, scratch_demo, "mlst_bar", lambda stack: stack)

    assert yaml.safe_load(after) == yaml.safe_load(before)
    assert validate_data_analysis_recipe(scratch_demo) == []


def test_a_changed_layer_value_is_the_only_change_of_the_plot_file(blueprint, scratch_demo):
    def edit(stack):
        labs = next(n for n in stack if n.get("component") == "labs")
        labs["params"] = {**labs["params"], "title": "A new title"}
        return stack

    file, before, after = save(blueprint, scratch_demo, "mlst_bar", edit)

    changed, original = yaml.safe_load(after), yaml.safe_load(before)
    assert changed["layers"][-1]["params"]["title"] == "A new title"
    changed["layers"][-1]["params"]["title"] = original["layers"][-1]["params"]["title"]
    assert changed == original                                  # nothing else moved, nothing was lost
    # the save writes the keys in the order of the specification (mapping before layers), not the order of the old file: the values are equal
    assert "spec" not in yaml.safe_load(after)                  # the whole entry, not a spec
    assert validate_data_analysis_recipe(scratch_demo) == []


def test_a_changed_mapping_value_is_saved_through_the_form_and_is_the_only_change(blueprint, scratch_demo):
    blueprint.open_recipe(scratch_demo)
    blueprint.tap("mlst_bar")
    file = Path(blueprint.ws.active_component_path.get())
    before = yaml.safe_load(file.read_text())
    blueprint.ws.selected_node_idx = Val(0)                     # the mapping node is the first of the stack
    blueprint.ws.invalidated_from = Val(None)
    blueprint.ns["input"] = Input(bp_map_x="year", bp_map_fill="country", bp_form_comment="")

    blueprint.ns["_bp_apply_node_handler"]()
    blueprint.ns["_handle_data_analysis_recipe_save_internal"]()

    after = yaml.safe_load(file.read_text())
    assert after["mapping"] == {"x": "year", "fill": "country"} and before["mapping"]["x"] == "sequence_type"
    after["mapping"] = before["mapping"]
    assert after == before
    assert validate_data_analysis_recipe(scratch_demo) == []
