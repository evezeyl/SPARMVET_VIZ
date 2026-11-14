"""The recipe that Blueprint's "new recipe" form writes is a draft in recipe format 1 (work order W8, BP-NEW-1).

A new recipe has no table and no plot yet, so it is judged in profile `build` (a draft); profile `run` refuses it
with one problem only, "no plot yet" (T09).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_new_recipe.py -q
"""
import pytest

from utils.recipe_check import check_recipe
from utils.recipe_factory import write_recipe
from utils.recipe_loader import check_recipe_file, load_recipe

from blueprint_arch.new_recipe import new_recipe_draft


def draft(**changes):
    values = {"recipe_id": "my_analysis", "label": "My analysis", "description": "What it answers",
              "author": "The team", "created": "2026-11-14"}
    values.update(changes)
    return new_recipe_draft(**values)


def test_the_draft_has_no_error_in_profile_build():
    assert check_recipe(draft(), "build", file_stem="my_analysis").errors == []


def test_the_only_problem_in_profile_run_is_that_there_is_no_plot_yet():
    assert [p.code for p in check_recipe(draft(), "run", file_stem="my_analysis").errors] == ["T09"]


def test_the_keys_of_format_1_come_first_and_in_order():
    assert list(draft()) == ["id", "spec_version", "data_engine", "plot_engine", "info", "data_schemas", "joins", "analysis_groups"]
    recipe = draft()
    assert recipe["id"] == "my_analysis" and recipe["spec_version"] == 1
    assert recipe["data_engine"] == "python-polars" and recipe["plot_engine"] == "python-plotnine"
    assert recipe["data_schemas"] == {} and recipe["joins"] == {} and recipe["analysis_groups"] == {}


def test_the_name_typed_in_the_form_is_the_label_not_an_old_key():
    info = draft()["info"]
    assert info["label"] == "My analysis"
    assert "name" not in info and "display_name" not in info
    assert list(info) == ["label", "description", "author", "version", "created", "tags"]
    assert info["description"] == "What it answers" and info["author"] == "The team"
    assert info["version"] == "1.0.0" and info["created"] == "2026-11-14" and info["tags"] == []


def test_an_empty_label_is_refused_because_the_format_requires_one():
    with pytest.raises(ValueError, match="label"):
        draft(label="")
    with pytest.raises(ValueError, match="label"):
        draft(label="   ")


def test_a_form_left_empty_still_gives_a_valid_draft():
    """The description and the author are optional in the form; the keys are written empty, as the form always did."""
    recipe = draft(description="", author="")
    assert recipe["info"]["description"] == "" and recipe["info"]["author"] == ""
    assert check_recipe(recipe, "build", file_stem="my_analysis").errors == []


def test_the_written_file_passes_the_checker_and_keeps_the_order(tmp_path):
    path = write_recipe(tmp_path / "my_analysis.yaml", draft(label="Prøver: the \"good\" ones"))
    assert check_recipe_file(path, "build").errors == []
    raw, problems = load_recipe(path)
    assert problems == [] and raw["info"]["label"] == "Prøver: the \"good\" ones"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("id: my_analysis\nspec_version: 1\ndata_engine: python-polars\nplot_engine: python-plotnine\ninfo:\n  label:")
    assert text.index("data_schemas:") < text.index("joins:") < text.index("analysis_groups:")
