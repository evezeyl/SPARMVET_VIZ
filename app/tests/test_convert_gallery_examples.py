"""The gallery examples of the old compact form are converted to standard recipes (spec section 9, GALLERY-RIGOR-1).

`assets/scripts/convert_gallery_examples.py` rewrites an example as a standard recipe, generates its data contract
from the data file, and sets the tag strip of `example_meta.md` from the taxonomy. It converts only what the checker
accepts, writes nothing without --apply, and never touches an example it cannot convert.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_convert_gallery_examples.py -q
"""
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

from utils.recipe_loader import check_recipe_file

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("convert_gallery_examples", ROOT / "assets/scripts/convert_gallery_examples.py")
cge = importlib.util.module_from_spec(_spec)
sys.modules["convert_gallery_examples"] = cge
_spec.loader.exec_module(cge)

OLD = """info:
  name: Dumbbell Chart
  submission_date: '2026-05-03'
  family: Comparison
  pattern: 1 Numeric, 2 Categorical
  difficulty: Intermediate
  geom: geom_segment
  show: change
  sample_size: any
data_path: example_data.tsv
plots:
  dumbbell:
    layers:
    - params:
        color: '#b3b3b3'
      name: geom_line
    - params:
        size: 4
      name: geom_point
    mapping:
      x: rate
      y: species
wrangling:
  tier1: []
  tier2: []
  tier3: []
"""
DATA = "species\tyear\trate\nE. coli\t2015\t1.5\nE. coli\t2023\t2.5\n"
META = ("## Dumbbell Chart\n\n> 📊 Comparison · 🔢 1 Numeric, 2 Categorical · 📈 Intermediate · ⚙️ geom_segment · 🎯 change · 📏 any\n\n"
        "### Suitability\nShows change between two states.\nThe second line of the paragraph.\n\n### Interpretation\nLonger is bigger.\n")
NEW_STRIP = "> 📊 Comparison · 🔢 1 Numeric, 2 Categorical · 📈 Intermediate · ⚙️ geom_line · 🎯 change · 📏 any"


def _example(root: Path, name: str = "dumbbell", recipe: str = OLD) -> Path:
    folder = root / "assets" / "gallery_data" / name
    folder.mkdir(parents=True)
    (folder / "data_analysis_recipe.yaml").write_text(recipe.replace("dumbbell:", f"{name}:"))
    (folder / "example_data.tsv").write_text(DATA)
    (folder / "example_meta.md").write_text(META)
    (folder / "preview_plot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return folder


def _convert(root: Path, **arguments):
    return cge.convert(root / "assets" / "gallery_data", root, **arguments)


def test_a_dry_run_writes_nothing(tmp_path):
    folder = _example(tmp_path)
    outcome, = _convert(tmp_path)
    assert outcome.status == "converted" and outcome.recipe_text and outcome.meta_text
    assert (folder / "data_analysis_recipe.yaml").read_text() == OLD
    assert (folder / "example_meta.md").read_text() == META


def test_apply_writes_a_standard_recipe_that_passes_the_gallery_check(tmp_path):
    folder = _example(tmp_path)
    _convert(tmp_path, apply=True)
    recipe_path = folder / "data_analysis_recipe.yaml"
    assert check_recipe_file(recipe_path, "gallery", file_stem="dumbbell").errors == []
    recipe = yaml.safe_load(recipe_path.read_text())
    assert recipe["id"] == "dumbbell" and recipe["spec_version"] == 1
    assert recipe["info"] == {"label": "Dumbbell Chart", "submission_date": "2026-05-03",
                              "description": "Shows change between two states. The second line of the paragraph."}
    schema = recipe["data_schemas"]["example"]
    assert schema["source"] == {"type": "local_tsv", "path": "./assets/gallery_data/dumbbell/example_data.tsv"}
    assert schema["null_values"] == [] and schema["strip"] is True and schema["wrangling"] == {"tier1": []}
    assert schema["input_fields"] == {"species": {"type": "String"}, "year": {"type": "Int64"}, "rate": {"type": "Float64"}}
    plot = recipe["analysis_groups"]["example"]["plots"]["dumbbell"]
    assert plot["taxonomy"] == {"family": "Comparison", "pattern": "1 Numeric, 2 Categorical", "difficulty": "Intermediate",
                                "show": "change", "sample_size": "any"}
    assert plot["spec"] == {"target_dataset": "example", "mapping": {"x": "rate", "y": "species"},
                            "layers": [{"name": "geom_line", "params": {"color": "#b3b3b3"}}, {"name": "geom_point", "params": {"size": 4}}]}
    assert "steps" not in plot and "plots" not in recipe and "data_path" not in recipe


def test_the_typed_geom_is_replaced_by_the_derived_one_and_reported(tmp_path):
    folder = _example(tmp_path)
    outcome, = _convert(tmp_path, apply=True)
    assert any("geom_segment" in line and "geom_line" in line for line in outcome.lines)
    assert any(line.startswith("data contract (review it): species: String, year: Int64, rate: Float64") for line in outcome.lines)
    meta = (folder / "example_meta.md").read_text()
    assert meta.split("\n")[2] == NEW_STRIP
    assert meta.replace(NEW_STRIP, "") == META.replace(META.split("\n")[2], "")   # the teaching text is untouched


def test_a_second_run_changes_nothing(tmp_path):
    folder = _example(tmp_path)
    _convert(tmp_path, apply=True)
    first = {path.name: path.read_bytes() for path in folder.iterdir()}
    outcome, = _convert(tmp_path, apply=True)
    assert outcome.status == "standard" and outcome.recipe_text is None and outcome.meta_text is None
    assert {path.name: path.read_bytes() for path in folder.iterdir()} == first


def test_a_stale_tag_strip_of_a_standard_example_is_set_again(tmp_path):
    folder = _example(tmp_path)
    _convert(tmp_path, apply=True)
    recipe = (folder / "data_analysis_recipe.yaml").read_text()
    (folder / "example_meta.md").write_text(META)
    outcome, = _convert(tmp_path, apply=True)
    assert outcome.status == "standard"
    assert (folder / "example_meta.md").read_text().split("\n")[2] == NEW_STRIP
    assert (folder / "data_analysis_recipe.yaml").read_text() == recipe


@pytest.mark.parametrize("change,reason", [
    (lambda text: text.replace("  tier3: []", "  tier3:\n  - action: filter_rows\n    column: rate\n    operator: '>'\n    value: 0"), "P05"),
    (lambda text: "# a note of the author\n" + text, "comments"),
    (lambda text: text + "extra_key: 1\n", "extra_key"),
    (lambda text: text.replace("  sample_size: any", "  sample_size: any\n  author: me"), "info.author"),
    (lambda text: text.replace("data_path: example_data.tsv", "data_path: other.tsv"), "data_path"),
    (lambda text: text.replace("  family: Comparison", "  family: Numeric-Numeric"), "GP03"),
    (lambda text: text.replace("  show: change\n", ""), "GP02"),
    (lambda text: text + "  second:\n    layers: []\n    mapping: {}\n", "wrangling"),
    (lambda text: "- a list\n", "not a YAML mapping"),
])
def test_an_example_that_cannot_be_converted_is_left_as_it_is_with_the_reason(tmp_path, change, reason):
    text = change(OLD)
    folder = _example(tmp_path, recipe=text)
    outcome, = _convert(tmp_path, apply=True)
    assert outcome.status == "not converted" and outcome.recipe_text is None
    assert any(reason in line for line in outcome.lines), outcome.lines
    assert (folder / "data_analysis_recipe.yaml").read_text() == text
    assert (folder / "example_meta.md").read_text() == META


def test_two_plots_or_a_missing_data_file_are_not_converted(tmp_path):
    two = _example(tmp_path, "two_plots", OLD.replace("wrangling:", "  second:\n    layers: []\n    mapping: {}\nwrangling:"))
    no_data = _example(tmp_path, "no_data")
    (no_data / "example_data.tsv").unlink()
    good = _example(tmp_path, "good")
    by_name = {outcome.name: outcome for outcome in _convert(tmp_path, apply=True)}
    assert by_name["two_plots"].status == "not converted" and "exactly one plot" in by_name["two_plots"].lines[0]
    assert by_name["no_data"].status == "not converted" and "example_data.tsv is missing" in by_name["no_data"].lines[-1]
    assert by_name["good"].status == "converted"
    assert yaml.safe_load((good / "data_analysis_recipe.yaml").read_text())["id"] == "good"
    assert "spec_version" not in (two / "data_analysis_recipe.yaml").read_text()


def test_only_names_the_examples_to_convert_and_an_unknown_name_is_an_error(tmp_path):
    first, second = _example(tmp_path, "first"), _example(tmp_path, "second")
    outcomes = _convert(tmp_path, only=["first"], apply=True)
    assert [outcome.name for outcome in outcomes] == ["first"]
    assert "spec_version" in (first / "data_analysis_recipe.yaml").read_text()
    assert "spec_version" not in (second / "data_analysis_recipe.yaml").read_text()
    with pytest.raises(ValueError, match="no such example folder"):
        _convert(tmp_path, only=["missing"])


def test_a_missing_value_text_in_the_data_is_declared_on_its_field_and_named(tmp_path):
    folder = _example(tmp_path)
    (folder / "example_data.tsv").write_text("species\tyear\trate\nE. coli\t2015\tNA\nE. coli\t2023\t2.5\n")
    outcome, = _convert(tmp_path, apply=True)
    schema = yaml.safe_load((folder / "data_analysis_recipe.yaml").read_text())["data_schemas"]["example"]
    assert schema["null_values"] == []
    assert schema["input_fields"]["rate"] == {"type": "Float64", "null_values": ["NA"]}
    assert "null_values" not in schema["input_fields"]["species"]
    assert any(line.startswith("review: rate:") for line in outcome.lines)


def test_a_gallery_outside_the_project_root_is_refused(tmp_path):
    _example(tmp_path)
    with pytest.raises(ValueError, match="outside the project root"):
        cge.convert(tmp_path / "assets" / "gallery_data", tmp_path / "another_project")


def test_the_command_line_reports_and_returns_one_when_an_example_is_not_converted(tmp_path, capsys):
    _example(tmp_path, "good")
    _example(tmp_path, "waiting", OLD.replace("  tier3: []", "  tier3:\n  - action: filter_rows\n    column: rate"))
    code = cge.main(["--gallery", str(tmp_path / "assets" / "gallery_data"), "--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1 and "good: would convert" in out and "waiting: NOT converted" in out and "Run again with --apply" in out
    assert cge.main(["--gallery", str(tmp_path / "missing")]) == 2
