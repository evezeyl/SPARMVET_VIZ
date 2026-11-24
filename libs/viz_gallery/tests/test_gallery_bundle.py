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
from viz_gallery.taxonomy import (display_axes, example_name, example_taxonomy, filter_panels, first_geom, tag_strip, the_plot,
                                  with_tag_strip)

RECIPE = "data_analysis_recipe.yaml"
AXES = ["family", "pattern", "difficulty", "geom", "show", "sample_size"]
TAXONOMY = {"family": "Ranking", "pattern": "1 Numeric, 1 Categorical", "difficulty": "Simple", "show": "ranking", "sample_size": "any"}
SPEC = {"mapping": {"x": "species", "y": "value"}, "layers": [{"name": "labs", "params": {"title": "T"}}, {"name": "geom_col", "params": {}}]}
META = "## My Plot\n\n> an old strip\n\n### Suitability\nUse it to compare.\n"
PNG = b"\x89PNG\r\n\x1a\n"
CATALOGS = {"actions": {}, "components": {"geom_col", "labs"}, "component_arguments": {"geom_col": None, "labs": None}}


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

def test_the_plot_of_an_example_holds_its_content_in_the_entry_with_the_ui_names_first():
    recipe = _recipe()
    entry = the_plot(recipe)[1]
    assert "spec" not in entry and "label" not in entry and "title" not in entry
    keys = list(entry)
    assert keys[0] == "ui_label" and keys.index("taxonomy") < keys.index("target_dataset") < keys.index("mapping") < keys.index("layers")
    assert next(iter(recipe["analysis_groups"].values()))["ui_label"] == "Example"


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
    assert schema["tier1"] == {"steps": [step]} and schema["tier2"] == {"steps": [step]}
    assert "wrangling" not in schema
    assert the_plot(recipe)[1]["tier3"] == {"steps": [step]}
    assert "steps" not in the_plot(recipe)[1] and "spec" not in the_plot(recipe)[1]
    plain = _recipe()
    assert "tier3" not in the_plot(plain)[1] and plain["data_schemas"]["example"]["tier1"] == {"steps": []}
    assert "tier2" not in plain["data_schemas"]["example"]
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
                     description="Use it to compare.", catalogs=CATALOGS)
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


def test_a_submission_with_an_unknown_layer_name_is_refused_and_leaves_nothing(tmp_path, monkeypatch):
    """The same catalogs as the app: a layer name that is not a registered component is not called valid (D-0050)."""
    monkeypatch.chdir(tmp_path)
    manager = GalleryManager("assets/gallery_data")
    spec = {**SPEC, "layers": [{"name": "labs", "params": {"title": "T"}}, {"name": "geom_colum", "params": {}}]}
    with pytest.raises(ValueError, match="geom_colum"):
        _submit(manager, tmp_path, plot_spec=spec)
    assert list(Path("assets/gallery_data").iterdir()) == []


@pytest.mark.parametrize("catalogs", [{}, {"actions": {}}, {"components": {"geom_col", "labs"}}], ids=["none", "no-components", "no-actions"])
def test_a_check_that_did_not_cover_the_actions_and_the_components_is_refused(tmp_path, monkeypatch, catalogs):
    monkeypatch.chdir(tmp_path)
    manager = GalleryManager("assets/gallery_data")
    with pytest.raises(ValueError, match="was not checked against"):
        _submit(manager, tmp_path, catalogs=catalogs)
    assert list(Path("assets/gallery_data").iterdir()) == []


# ---- the name of an example is the ui_label of its plot entry (D-0387) -------------------------------------------------

def test_the_name_is_the_ui_label_of_the_plot_entry_not_info_ui_label(tmp_path):
    folder = _write_example(tmp_path, "my_plot")
    recipe = _recipe("my_plot")
    recipe["info"]["ui_label"] = "Name for the recipe maker"
    the_plot(recipe)[1]["ui_label"] = "Name for the user"
    (folder / RECIPE).write_text(dump_example(recipe))
    manager = GalleryManager(str(tmp_path))
    index = manager.rebuild_index(CATALOGS)
    assert index["registry"]["my_plot"]["name"] == "Name for the user"
    assert example_name(recipe) == "Name for the user"


def test_a_plot_entry_without_ui_label_is_refused_by_the_check_and_has_no_name(tmp_path):
    folder = _write_example(tmp_path, "my_plot")
    recipe = _recipe("my_plot")
    del the_plot(recipe)[1]["ui_label"]
    (folder / RECIPE).write_text(dump_example(recipe))
    examples = GalleryManager(str(tmp_path)).check_examples(CATALOGS)
    assert "my_plot" in examples.rejected and any("ui_label" in text for text in examples.rejected["my_plot"])
    with pytest.raises(ValueError, match="ui_label"):
        example_name(recipe)


# ---- the index at start follows the examples (the six cases of the Gallery study, architect section 7) ---------------

def _synced_gallery(tmp_path, *names):
    for name in names or ("my_plot",):
        _write_example(tmp_path, name, label=f"Plot {name}")   # one name each: a repeated name is left out
    manager = GalleryManager(str(tmp_path))
    manager.rebuild_index(CATALOGS)
    return manager


def _rewrite_recipe(tmp_path, name, change):
    recipe = _recipe(name, label=f"Plot {name}")
    change(recipe)
    (tmp_path / name / RECIPE).write_text(dump_example(recipe))


def _index(tmp_path):
    return json.loads((tmp_path / "gallery_index.json").read_text(encoding="utf-8"))


def test_sync_of_an_unchanged_gallery_does_not_touch_the_file(tmp_path):
    manager = _synced_gallery(tmp_path)
    before = (tmp_path / "gallery_index.json").stat()
    content = (tmp_path / "gallery_index.json").read_bytes()
    _, outcome = manager.sync_index(CATALOGS)
    after = (tmp_path / "gallery_index.json").stat()
    assert outcome == "unchanged"
    assert (tmp_path / "gallery_index.json").read_bytes() == content and after.st_mtime_ns == before.st_mtime_ns


def test_sync_rewrites_the_index_when_a_name_changed(tmp_path):
    manager = _synced_gallery(tmp_path)
    _rewrite_recipe(tmp_path, "my_plot", lambda r: the_plot(r)[1].update(ui_label="A new name"))
    _, outcome = manager.sync_index(CATALOGS)
    assert outcome == "rewritten"
    assert _index(tmp_path)["registry"]["my_plot"]["name"] == "A new name"


def test_sync_rewrites_the_index_when_a_taxonomy_value_changed(tmp_path):
    manager = _synced_gallery(tmp_path)
    _rewrite_recipe(tmp_path, "my_plot", lambda r: the_plot(r)[1]["taxonomy"].update(family="Comparison"))
    _, outcome = manager.sync_index(CATALOGS)
    index = _index(tmp_path)
    assert outcome == "rewritten"
    assert index["registry"]["my_plot"]["taxonomy"]["family"] == "Comparison"
    assert index["pivot"]["by_family"] == {"Comparison": ["my_plot"]}


def test_sync_rewrites_the_index_when_the_thumbnail_appears(tmp_path):
    # a missing preview_plot.png makes the example fail the check (GP05), so the picture flag that can change alone is the thumbnail
    manager = _synced_gallery(tmp_path)
    assert _index(tmp_path)["registry"]["my_plot"]["has_thumb"] is False
    (tmp_path / "my_plot" / "preview_thumb.png").write_bytes(PNG)
    assert manager.sync_index(CATALOGS)[1] == "rewritten"
    assert _index(tmp_path)["registry"]["my_plot"]["has_thumb"] is True


def test_sync_rewrites_the_index_when_an_example_is_added(tmp_path):
    manager = _synced_gallery(tmp_path)
    _write_example(tmp_path, "second_plot", label="Plot second_plot")
    assert manager.sync_index(CATALOGS)[1] == "rewritten"
    assert set(_index(tmp_path)["registry"]) == {"my_plot", "second_plot"}


def test_sync_rewrites_the_index_when_an_example_is_removed(tmp_path):
    import shutil
    manager = _synced_gallery(tmp_path, "my_plot", "second_plot")
    shutil.rmtree(tmp_path / "second_plot")
    assert manager.sync_index(CATALOGS)[1] == "rewritten"
    assert set(_index(tmp_path)["registry"]) == {"my_plot"}


def test_sync_leaves_out_an_example_that_fails_the_check_with_its_reason(tmp_path):
    manager = _synced_gallery(tmp_path, "my_plot", "second_plot")
    _rewrite_recipe(tmp_path, "second_plot", lambda r: the_plot(r)[1].pop("ui_label"))
    examples, outcome = manager.sync_index(CATALOGS)
    index = _index(tmp_path)
    assert outcome == "rewritten" and "second_plot" in examples.rejected
    assert set(index["registry"]) == {"my_plot"}
    assert any("ui_label" in text for text in index["metadata"]["rejected"]["second_plot"])
    assert manager.sync_index(CATALOGS)[1] == "unchanged"


def test_build_index_is_pure_and_the_write_is_separate(tmp_path):
    manager = _synced_gallery(tmp_path)
    before = (tmp_path / "gallery_index.json").read_bytes()
    built = manager.build_index(manager.check_examples(CATALOGS))
    assert built["registry"] == _index(tmp_path)["registry"] and built["pivot"] == _index(tmp_path)["pivot"]
    assert (tmp_path / "gallery_index.json").read_bytes() == before


# ---- a name or a plot id repeated across examples (the set check) -------------------------------------------------------

def test_a_later_example_with_the_same_name_is_left_out_with_its_reason(tmp_path):
    _write_example(tmp_path, "a_first")
    _write_example(tmp_path, "b_second")   # both are called "My Plot"
    examples = GalleryManager(str(tmp_path)).check_examples(CATALOGS)
    assert set(examples.accepted) == {"a_first"}
    assert any("My Plot" in text and "a_first" in text for text in examples.rejected["b_second"])


def test_a_later_example_with_the_same_plot_id_is_left_out_with_its_reason(tmp_path):
    _write_example(tmp_path, "a_first", plot_id="shared_id", label="First")
    _write_example(tmp_path, "b_second", plot_id="shared_id", label="Second")
    examples = GalleryManager(str(tmp_path)).check_examples(CATALOGS)
    assert set(examples.accepted) == {"a_first"}
    assert any("X5" in text and "shared_id" in text for text in examples.rejected["b_second"])


def test_examples_with_their_own_name_and_plot_id_are_all_kept_and_the_reason_reaches_the_index(tmp_path):
    _write_example(tmp_path, "a_first", label="First")
    _write_example(tmp_path, "b_second", label="Second")
    _write_example(tmp_path, "c_third")
    _write_example(tmp_path, "d_fourth")   # "My Plot" again, repeats c_third
    manager = GalleryManager(str(tmp_path))
    index = manager.rebuild_index(CATALOGS)
    assert set(index["registry"]) == {"a_first", "b_second", "c_third"}
    assert "d_fourth" in index["metadata"]["rejected"]
