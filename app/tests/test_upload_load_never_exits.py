"""Blueprint upload load: a bad uploaded file is reported as problems and never ends the program (BP-UPLOAD-EXIT-1).

ConfigManager calls sys.exit on a contradictory file; SystemExit is not an Exception and would escape a Shiny
effect and freeze the session. These tests use the real ConfigManager."""
import pytest

from app.modules.data_analysis_recipe_validator import load_uploaded_recipe

BAD = {
    "bad_yaml": "a: [1, 2\nb: {",
    "recipe_without_groups": "id: x\ndata_schemas:\n  d:\n    source: {type: tsv, path: a.tsv}\n",
    "missing_include": "data_schemas: !include nothere.yaml\nanalysis_groups: {}\n",
    "fragment_missing_include": "wrangling:\n  tier1: !include nothere.yaml\n",
    "empty": "",
    "only_comment": "# nothing\n",
    "list_root": "- a\n- b\n",
}


@pytest.mark.parametrize("name", sorted(BAD))
def test_bad_file_gives_problems_and_no_exception(tmp_path, name):
    p = tmp_path / f"{name}.yaml"
    p.write_text(BAD[name])
    try:
        raw, problems = load_uploaded_recipe(p)
    except BaseException as exc:  # SystemExit included
        pytest.fail(f"escaped: {type(exc).__name__}")
    assert raw is None
    assert problems and all(isinstance(t, str) and t for t in problems)


def test_missing_file_is_a_problem(tmp_path):
    raw, problems = load_uploaded_recipe(tmp_path / "gone.yaml")
    assert raw is None and problems


def test_good_fragment_loads_with_no_problem(tmp_path):
    p = tmp_path / "frag.yaml"
    p.write_text("wrangling:\n  tier1:\n    - action: polars_cast\n      columns: [a]\n      dtype: Int64\n")
    raw, problems = load_uploaded_recipe(p)
    assert problems == [] and raw["wrangling"]["tier1"][0]["action"] == "polars_cast"


def test_fragment_with_unknown_action_loads_and_is_reported_by_the_check(tmp_path):
    from app.modules.data_analysis_recipe_validator import uploaded_recipe_report
    p = tmp_path / "frag.yaml"
    p.write_text("wrangling:\n  tier1:\n    - action: nope_zzz\n")
    raw, problems = load_uploaded_recipe(p)
    assert problems == []
    assert any("nope_zzz" in line for line in uploaded_recipe_report(raw))


def test_good_whole_recipe_loads(tmp_path):
    from utils.recipe_factory import minimal_recipe, write_recipe
    p = write_recipe(tmp_path / "good.yaml", minimal_recipe("good"))
    raw, problems = load_uploaded_recipe(p)
    assert problems == [] and isinstance(raw, dict) and "data_schemas" in raw
