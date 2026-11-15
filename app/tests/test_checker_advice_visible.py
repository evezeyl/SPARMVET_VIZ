"""An advice of the recipe checker is shown and never blocks (JOIN-FLOAT-1, JOIN-SELF-1; Eve 2026-11-14: no silent error).

A recipe that gets an advice (J12 self-join on the same key, J13 float join key) still loads: it is not refused by
`validate_data_analysis_recipe` (HOME's gate and Blueprint's rules check), it stays in `available_data_analysis_recipes`,
and its advice is listed where the recipe problems are shown: HOME's recipe choice panel (`data_analysis_recipe_advices` of
the bootloader) and Blueprint's Validate result (`checker_advices`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_checker_advice_visible.py -q
"""
import shutil
from pathlib import Path

import yaml

from app.modules.data_analysis_recipe_validator import checker_advices, validate_data_analysis_recipe
from app.src.bootloader import Bootloader
from app.tests.test_data_analysis_recipe_load_gate import _deployment, clean_launch_env  # noqa: F401
from app.tests.tiny_recipe import tiny_recipe, write_tiny

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "config" / "data_analysis_recipes" / "templates"


def _template_with_float_key(tmp_path) -> Path:
    """The shipped complex template, copied, with the key of its two tables declared Float64 again (as it was before JOIN-FLOAT-1)."""
    shutil.copy(TEMPLATES / "complex_template.yaml", tmp_path / "complex_template.yaml")
    shutil.copytree(TEMPLATES / "complex_template", tmp_path / "complex_template")
    for name in ("metadata_input.yaml", "genomics_input.yaml"):
        path = tmp_path / "complex_template" / name
        path.write_text(path.read_text().replace('type: "String"', 'type: "Float64"', 1))
    return tmp_path / "complex_template.yaml"


def test_the_shipped_template_with_a_float_key_is_advised_and_not_refused(tmp_path):
    path = _template_with_float_key(tmp_path)
    assert validate_data_analysis_recipe(path) == [], "an advice must not refuse the recipe"
    advices = checker_advices(path)
    assert advices and all(a.problem.startswith("[J13]") for a in advices)
    assert "text type" in advices[0].tip and "001" in advices[0].problem


def test_the_shipped_template_has_no_advice():
    assert checker_advices(TEMPLATES / "complex_template.yaml") == []


def test_a_recipe_with_an_advice_stays_available_and_its_advice_is_listed_for_home(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path)
    recipe = tiny_recipe("selfjoin")
    recipe["joins"] = {"AA": {"label": "AA", "description": "A with itself.", "ingredients": [{"dataset_id": "A"}],
                              "steps": {"tier1": [{"action": "polars_join", "right_ingredient": "A", "on": ["a"], "how": "left", "maintain_order": "left_right"}]}}}
    write_tiny(root / "data_analysis_recipes", recipe)
    write_tiny(root / "data_analysis_recipes", tiny_recipe("plain"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert sorted(b.available_data_analysis_recipes) == ["plain", "selfjoin"] and not b.rejected_data_analysis_recipes
    assert [t for t in b.data_analysis_recipe_advices["selfjoin"] if t.startswith("[J12]")]
    assert "plain" not in b.data_analysis_recipe_advices


def test_no_shipped_recipe_gets_a_join_advice():
    """The shipped recipes and templates are written so that J12 and J13 do not fire on them."""
    recipes = REPO / "config" / "data_analysis_recipes"
    files = [*recipes.glob("pipelines/*.yaml"), *recipes.glob("templates/*.yaml"),
             *(REPO / "assets" / "gallery_data").rglob("data_analysis_recipe.yaml")]
    assert files, "no shipped recipe found"
    found = {f.name: [a.problem[:6] for a in checker_advices(f)] for f in files}
    assert {name: codes for name, codes in found.items() if codes} == {}


# -- the display: the pure functions, and the screens that call them ------------------------------

def test_home_advice_entries_are_sorted_and_skip_empty():
    from app.modules.data_analysis_recipe_validator import home_advice_entries
    assert home_advice_entries({"b": ["x"], "a": ["y", "z"], "c": []}) == [("a", ["y", "z"]), ("b", ["x"])]
    assert home_advice_entries({}) == []


def test_validate_advice_entries_keep_heading_text_and_tip():
    from app.modules.data_analysis_recipe_validator import validate_advice_entries
    rows = validate_advice_entries([{"location": "joins.AA", "problem": "p", "tip": "t"},
                                    {"location": "q", "problem": "p2", "tip": None}])
    assert rows == [("Advice: joins.AA", "p", "t"), ("Advice: q", "p2", None)]
    assert validate_advice_entries([]) == []


def test_home_recipe_choice_renders_the_advice_entries():
    source = (REPO / "app" / "handlers" / "home_theater.py").read_text()
    assert "home_advice_entries(getattr(bootloader" in source and "for name, texts in advices" in source
    assert "Advice (these recipes load and run)" in source


def test_blueprint_validate_renders_the_advice_entries():
    source = (REPO / "app" / "handlers" / "blueprint_handlers.py").read_text()
    assert "validate_advice_entries(result.get(\"advice_problems\"" in source and "*advice_rows," in source


def test_st12_the_order_advice_is_one_of_the_advices_shown_to_the_author_and_never_refuses(tmp_path):
    """DECIDED 4 (Eve, 2026-11-15): a position step after a step that does not fix the row order is advised, not refused."""
    from app.modules.data_analysis_recipe_validator import SHOWN_ADVICES
    assert "ST12" in SHOWN_ADVICES
    path = _template_with_float_key(tmp_path)
    assert all(not a.problem.startswith("[ST12]") for a in checker_advices(path))
