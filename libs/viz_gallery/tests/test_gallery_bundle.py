"""The gallery library: the taxonomy read from the specification data, the example recipe, the check and the index.

A gallery example is a standard recipe checked in the profile `gallery` (spec section 9). These tests use small
examples written in a temporary folder; the shipped gallery is tested in `test_gallery_examples_are_recipes.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_gallery/tests/test_gallery_bundle.py -q
"""
import json
from pathlib import Path

import polars as pl
import pytest
import yaml

from utils.recipe_check import check_recipe, spec
from utils.recipe_loader import check_recipe_file
from viz_gallery.example_recipe import data_contract, dump_example, example_recipe
from viz_gallery.gallery_manager import GalleryManager
from viz_gallery.taxonomy import (display_axes, example_taxonomy, filter_panels, first_geom, tag_strip, the_plot,
                                  with_tag_strip)

RECIPE = "data_analysis_recipe.yaml"
AXES = ["family", "pattern", "difficulty", "geom", "show", "sample_size"]
TAXONOMY = {"family": "Ranking", "pattern": "1 Numeric, 1 Categorical", "difficulty": "Simple", "show": "ranking", "sample_size": "any"}
SPEC = {"mapping": {"x": "species", "y": "value"}, "layers": [{"name": "labs", "params": {"title": "T"}}, {"name": "geom_col", "params": {}}]}
META = "## My Plot\n\n> an old strip\n\n### Suitability\nUse it to compare.\n"
PNG = b"\x89PNG\r\n\x1a\n"


def _recipe(name="my_plot", gallery="assets/gallery_data", **changes):
    arguments = dict(example_id=name, label="My Plot", description="Use it to compare.",
                     data_path=f"./{gallery}/{name}/example_data.tsv",
                     fields={"species": {"type": "String"}, "value": {"type": "Float64"}}, taxonomy=TAXONOMY,
                     plot_id=name, plot_spec=SPEC)
    arguments.update(changes)
    return example_recipe(**arguments)


def _write_example(root: Path, name: str, **changes) -> Path:
    """A complete example folder: recipe, data, text and picture."""
    folder = root / name
    folder.mkdir(parents=True)
    (folder / RECIPE).write_text(dump_example(_recipe(name, **changes)))
    (folder / "example_data.tsv").write_text("species\tvalue\nE. coli\t1.5\n")
    (folder / "example_meta.md").write_text(META)
    (folder / "preview_plot.png").write_bytes(PNG)
    return folder


# ---- the taxonomy comes from the specification data ---------------------------------------------------------------

def test_the_six_axes_come_from_the_specification_in_order():
    shown = display_axes()
    assert [item["axis"] for item in shown] == AXES
    assert all(item["label"] and item["icon"] for item in shown)
    # the typed axes of the checker and the shown axes are one list: only geom is added, because it is derived
    assert [axis for axis in AXES if axis != "geom"] == spec()["gallery"]["axes"]


def test_the_geom_is_the_first_geom_or_stat_layer():
    assert first_geom(SPEC) == "geom_col"
    assert first_geom({"layers": [{"name": "stat_ecdf"}, {"name": "geom_point"}]}) == "stat_ecdf"
    assert first_geom({"layers": [{"name": "labs"}, {"name": "theme_minimal"}]}) == ""
    assert first_geom({}) == "" and first_geom(None) == ""


def test_the_taxonomy_of_an_example_holds_the_derived_geom_not_a_typed_one():
    recipe = _recipe(taxonomy={**TAXONOMY, "geom": "geom_segment"})
    assert "geom" not in the_plot(recipe)[1]["taxonomy"]
    assert example_taxonomy(recipe) == {**TAXONOMY, "geom": "geom_col"}
    assert list(example_taxonomy(recipe)) == AXES


def test_a_recipe_with_two_plots_has_no_example_taxonomy():
    recipe = _recipe()
    plots = recipe["analysis_groups"]["example"]["plots"]
    plots["second"] = dict(plots["my_plot"])
    assert the_plot(recipe) is None
    with pytest.raises(ValueError, match="exactly one plot"):
        example_taxonomy(recipe)


def test_the_tag_strip_shows_the_six_terms_with_their_icons():
    strip = tag_strip({**TAXONOMY, "geom": "geom_col"})
    assert strip == "> 📊 Ranking · 🔢 1 Numeric, 1 Categorical · 📈 Simple · ⚙️ geom_col · 🎯 ranking · 📏 any"


def test_setting_the_tag_strip_changes_that_line_only():
    new = with_tag_strip(META, "> new strip")
    assert new.split("\n")[2] == "> new strip"
    assert [line for i, line in enumerate(new.split("\n")) if i != 2] == [line for i, line in enumerate(META.split("\n")) if i != 2]
    assert with_tag_strip(new, "> new strip") == new


def test_a_missing_tag_strip_is_added_under_the_heading_and_the_text_is_kept():
    assert with_tag_strip("## Name\n\n### Suitability\nText.\n", "> strip") == "## Name\n\n> strip\n\n### Suitability\nText.\n"
    assert with_tag_strip("## Name\nText.\n", "> strip") == "## Name\n\n> strip\n\nText.\n"
    assert with_tag_strip("## Name", "> strip") == "## Name\n\n> strip"


def test_a_block_quote_further_down_is_not_taken_for_the_tag_strip():
    text = "## Name\n\nSome text.\n\n> a quotation of the author\n"
    assert with_tag_strip(text, "> strip") == "## Name\n\n> strip\n\nSome text.\n\n> a quotation of the author\n"


def test_a_text_without_heading_is_refused():
    with pytest.raises(ValueError, match="no '## ' heading"):
        with_tag_strip("Only text.\n", "> strip")


def test_filter_panels_follow_the_order_of_the_specification_and_offer_only_used_terms():
    pivot = {"by_family": {"Ranking": ["a"], "Comparison": ["b"]},
             "by_difficulty": {"Advanced": ["a"], "Simple": ["b"], "Intermediate": ["c"]},
             "by_geom": {"geom_point": ["a"], "geom_col": ["b"]},
             "by_pattern": {"Numeric-Numeric": ["a"], "2 Numeric": ["b"]}}
    panels = {panel["axis"]: panel for panel in filter_panels(pivot)}
    assert list(panels) == AXES
    assert panels["family"]["choices"] == ["Comparison", "Ranking"]
    assert panels["difficulty"]["choices"] == ["Simple", "Intermediate", "Advanced"]   # not the alphabet
    assert panels["geom"]["choices"] == ["geom_col", "geom_point"]
    assert panels["pattern"]["choices"] == ["2 Numeric"]   # "Numeric-Numeric" is not a term of the vocabulary (G1)
    assert panels["show"]["choices"] == []
    assert panels["family"]["label"] == "📊 Family (Purpose)" and panels["family"]["pivot_key"] == "by_family"


def test_filter_panels_of_an_empty_index_have_no_choices():
    assert [panel["choices"] for panel in filter_panels({})] == [[]] * 6


# ---- the example recipe and its data contract -----------------------------------------------------------------------

def test_an_example_recipe_passes_the_gallery_check_and_reads_back_from_its_text():
    recipe = _recipe()
    assert check_recipe(recipe, "gallery", file_stem="my_plot").errors == []
    text = dump_example(recipe)
    assert yaml.safe_load(text) == recipe
    assert list(yaml.safe_load(text)) == ["id", "spec_version", "data_engine", "plot_engine", "info", "data_schemas", "analysis_groups"]
    assert "description: >-" in text and "geom:" not in text


def test_the_steps_of_an_example_go_where_the_format_puts_them():
    step = {"action": "polars_drop_nulls", "subset": ["value"]}
    recipe = _recipe(tier1=[step], tier2=[step], tier3=[step])
    schema = recipe["data_schemas"]["example"]
    assert schema["wrangling"] == {"tier1": [step], "tier2": [step]}
    assert the_plot(recipe)[1]["steps"] == {"tier3": [step]}
    assert "steps" not in the_plot(_recipe())[1] and _recipe()["data_schemas"]["example"]["wrangling"] == {"tier1": []}
    assert yaml.safe_load(dump_example(recipe)) == recipe


def test_the_data_contract_is_typed_from_the_file(tmp_path):
    data = tmp_path / "example_data.tsv"
    data.write_text("name\tcount\tvalue\nA\t1\t1.5\nB\t2\t2\n")
    fields, notes = data_contract(data)
    assert fields == {"name": {"type": "String"}, "count": {"type": "Int64"}, "value": {"type": "Float64"}}
    assert notes == []


def test_a_missing_value_text_is_declared_on_its_field_only_and_named_for_review(tmp_path):
    data = tmp_path / "example_data.tsv"
    data.write_text("country\tvalue\tother\nNO\tNA\tx\nSE\t2.5\ty\n")
    fields, notes = data_contract(data)
    assert fields["value"] == {"type": "Float64", "null_values": ["NA"]}
    assert fields["country"] == {"type": "String"} and fields["other"] == {"type": "String"}
    assert [note for note in notes if note.startswith("value:")] and not [note for note in notes if note.startswith("country:")]


def test_whitespace_around_values_and_an_empty_column_are_named_for_review(tmp_path):
    data = tmp_path / "example_data.tsv"
    data.write_text("name\tcount\tempty\n A \t 1 \t\nB\t2\t\n")
    fields, notes = data_contract(data)
    assert fields["count"] == {"type": "Int64"}   # typed after the strip that the schema declares
    assert any(note.startswith("name:") and "whitespace" in note for note in notes)
    assert any(note.startswith("empty:") and "every value is missing" in note for note in notes)


# ---- the check of a gallery folder and the index --------------------------------------------------------------------

def test_a_good_example_is_accepted_and_indexed(tmp_path):
    _write_example(tmp_path, "my_plot")
    manager = GalleryManager(str(tmp_path))
    examples = manager.check_examples()
    assert list(examples.accepted) == ["my_plot"] and examples.rejected == {} and examples.coverage == {"structure"}
    index = manager.rebuild_index()
    entry = index["registry"]["my_plot"]
    assert entry["name"] == "My Plot" and entry["path"].endswith(f"my_plot/{RECIPE}")
    assert entry["taxonomy"] == {**TAXONOMY, "geom": "geom_col"}
    assert index["pivot"]["by_geom"] == {"geom_col": ["my_plot"]} and index["pivot"]["by_family"] == {"Ranking": ["my_plot"]}
    assert set(index["pivot"]) == {f"by_{axis}" for axis in AXES}
    assert index["metadata"]["count"] == 1 and index["metadata"]["rejected"] == {}
    assert json.loads((tmp_path / "gallery_index.json").read_text())["registry"] == index["registry"]


def test_a_rejected_example_is_left_out_with_its_reason_and_the_good_one_stays(tmp_path):
    _write_example(tmp_path, "good")
    _write_example(tmp_path, "bad_term", taxonomy={**TAXONOMY, "family": "Numeric-Numeric"})
    no_meta = _write_example(tmp_path, "no_meta")
    (no_meta / "example_meta.md").unlink()
    index = GalleryManager(str(tmp_path)).rebuild_index()
    assert list(index["registry"]) == ["good"]
    rejected = index["metadata"]["rejected"]
    assert set(rejected) == {"bad_term", "no_meta"}
    assert "[GP03]" in rejected["bad_term"][0] and "Numeric-Numeric" in rejected["bad_term"][0]
    assert "[GP05]" in rejected["no_meta"][0] and "example_meta.md" in rejected["no_meta"][0]
    assert "bad_term" not in json.dumps(index["pivot"])


def test_an_example_whose_id_is_not_its_folder_is_rejected(tmp_path):
    folder = _write_example(tmp_path, "my_plot")
    folder.rename(tmp_path / "renamed")
    rejected = GalleryManager(str(tmp_path)).check_examples().rejected
    assert any("[GP04]" in reason for reason in rejected["renamed"])


def test_an_example_in_the_old_form_is_rejected_and_the_message_names_the_conversion(tmp_path):
    folder = _write_example(tmp_path, "old_one")
    (folder / RECIPE).write_text("info: {name: Old}\ndata_path: example_data.tsv\nplots: {old_one: {mapping: {}, layers: []}}\n")
    rejected = GalleryManager(str(tmp_path)).check_examples().rejected
    assert rejected == {"old_one": [rejected["old_one"][0]]}
    assert "convert_gallery_examples.py --only old_one --apply" in rejected["old_one"][0]


def test_a_folder_without_recipe_and_a_folder_with_the_old_file_names_are_rejected_with_a_reason(tmp_path):
    (tmp_path / "empty_folder").mkdir()
    old = tmp_path / "old_names"
    old.mkdir()
    (old / "recipe_manifest.yaml").write_text("info: {name: Old}\n")
    rejected = GalleryManager(str(tmp_path)).check_examples().rejected
    assert f"no {RECIPE}" in rejected["empty_folder"][0]
    assert "migrate_config_vocabulary.py" in rejected["old_names"][0]


def test_an_empty_gallery_gives_an_empty_index(tmp_path):
    index = GalleryManager(str(tmp_path / "empty")).rebuild_index()
    assert index["registry"] == {} and index["metadata"]["count"] == 0 and index["metadata"]["rejected"] == {}


def test_the_catalogs_are_passed_to_the_checker_and_the_coverage_says_so(tmp_path):
    _write_example(tmp_path, "my_plot")
    catalogs = {"components": {"geom_col"}, "component_arguments": {"geom_col": None}}
    examples = GalleryManager(str(tmp_path)).check_examples(catalogs)
    assert examples.coverage == {"structure", "components"}
    assert any("[PS04]" in reason and "labs" in reason for reason in examples.rejected["my_plot"])


# ---- a new example -----------------------------------------------------------------------------------------------------

def _submit(manager, tmp_path, **changes):
    preview = tmp_path / "plot.png"
    preview.write_bytes(PNG)
    arguments = dict(name="My Plot", data=pl.DataFrame({"species": ["E. coli", "S. aureus"], "value": [1.5, 2.0]}),
                     meta_markdown=META, taxonomy=TAXONOMY, plot_spec=SPEC, preview_path=str(preview),
                     description="Use it to compare.")
    arguments.update(changes)
    return Path(manager.submit_example(**arguments))


def test_a_submitted_example_passes_the_gallery_check_and_is_indexed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manager = GalleryManager("assets/gallery_data")
    folder = _submit(manager, tmp_path)
    assert folder.name.endswith("_my_plot")
    result = check_recipe_file(folder / RECIPE, "gallery", file_stem=folder.name)
    assert result.errors == []
    assert (folder / "example_meta.md").read_text().split("\n")[2] == tag_strip({**TAXONOMY, "geom": "geom_col"})
    assert pl.read_csv(folder / "example_data.tsv", separator="\t").height == 2
    assert list(manager.rebuild_index()["registry"]) == [folder.name]


def test_a_submission_with_a_wrong_term_is_refused_and_leaves_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manager = GalleryManager("assets/gallery_data")
    with pytest.raises(ValueError, match="GP03"):
        _submit(manager, tmp_path, taxonomy={**TAXONOMY, "show": "everything"})
    assert list(Path("assets/gallery_data").iterdir()) == []


def test_a_submission_without_picture_or_with_an_absolute_gallery_folder_is_refused(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="preview picture"):
        _submit(GalleryManager("assets/gallery_data"), tmp_path, preview_path=str(tmp_path / "missing.png"))
    with pytest.raises(ValueError, match="relative to the project root"):
        _submit(GalleryManager(str(tmp_path / "absolute")), tmp_path)
    assert list((tmp_path / "absolute").iterdir()) == [] and list(Path("assets/gallery_data").iterdir()) == []
