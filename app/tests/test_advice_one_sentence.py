"""Every reader of an advice shows "what happens. Suggestion: ..." with exactly one period (D-0099, D-0183, fix round 2026-11-16).

An advice has two fields, the problem and its tip (the remedy). Four readers show them: the command line (`Problem.text()` of the
checker), HOME's recipe choice panel (the gate notes, `Bootloader._gate_one`), Blueprint's Validate (`validate_advice_entries`)
and the upload reports. Before, each built the sentence itself: HOME joined problem and tip with a space, so a text that the
checker wrote without a final period read "...the result is empty Suggestion: remove the step", and J13 (which wrote its own
period) read ".. Suggestion:". The one function is `utils.fix_text.with_fix`; no reader builds the sentence.

This file tests the string each reader shows, for every advice code the app shows (`SHOWN_ADVICES`: J12, J13, ST13, ST14, ST15),
on real recipes with the real catalogs: one period, then a space, then "Suggestion:"; never ".." and never no period. The
command line is tested for every code of the checker in `libs/utils/tests/test_with_fix_one_period.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_advice_one_sentence.py -q
"""
import re
from pathlib import Path

import pytest

import app.src.bootloader as bootloader_module
from app.modules.data_analysis_recipe_validator import SHOWN_ADVICES, checker_advices, checker_catalogs, validate_advice_entries
from app.src.bootloader import Bootloader
from app.tests.test_data_analysis_recipe_load_gate import _deployment, clean_launch_env  # noqa: F401
from app.tests.tiny_recipe import tiny_recipe, write_tiny
from utils.recipe_loader import check_recipe_file

ROOT = Path(__file__).resolve().parents[2]
JOIN_ANTI = {"AA": {"ui_label": "AA", "description": "A with itself.", "ingredients": [{"dataset_id": "A"}],
                    "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "A", "on": ["a"], "how": "anti", "maintain_order": "left_right"}]}}}


def tiny(steps=None, fields=None, joins=None, float_key=False, recipe_id="t"):
    recipe = tiny_recipe(recipe_id)
    if steps is not None:
        recipe["data_schemas"]["A"]["tier1"] = {"steps": steps}
    recipe["data_schemas"]["A"]["input_fields"].update(fields or {})
    if float_key:
        recipe["data_schemas"]["A"]["input_fields"]["a"]["type"] = "Float64"
    if joins:
        recipe["joins"] = joins
    return recipe


# the recipe that gives each advice code the app shows (real catalogs)
RECIPES = {
    "J12": tiny(joins=JOIN_ANTI),
    "J13": tiny(joins=JOIN_ANTI, float_key=True),
    "ST13": tiny(steps=[{"action": "polars_sort", "by": ["a"], "maintain_order": False}, {"action": "polars_head", "n": 2}]),
    "ST14": tiny(steps=[{"action": "polars_top_k", "k": 2, "by": ["a"]}]),
    "ST15": tiny(steps=[{"action": "polars_sum"}], fields={"n": {"type": "Int32"}}),
}


def one_sentence(text):
    """One period (or ! or ?) between what happens and the first suggestion, never two, never none."""
    assert re.search(r"[.!?] Suggestion: ", text), text
    assert not re.search(r"[^.!?\s] Suggestion:", text), f"no period before Suggestion: {text}"
    assert not re.search(r"(?<!\.)\.\.(?!\.)", text), f"doubled period: {text}"


def written(tmp_path, code):
    return write_tiny(tmp_path, RECIPES[code], name=f"{code.lower()}.yaml")


def test_the_five_recipes_give_the_five_shown_codes(tmp_path):
    for code in RECIPES:
        assert code in {a.problem[1:].split("]")[0] for a in checker_advices(written(tmp_path, code))}, code
    assert set(RECIPES) == set(SHOWN_ADVICES)


@pytest.mark.parametrize("code", sorted(RECIPES))
def test_the_command_line_text_has_one_period_before_suggestion(tmp_path, code):
    result = check_recipe_file(written(tmp_path, code), "run", catalogs=checker_catalogs())
    texts = [p.text() for p in result.advices if p.code == code]
    assert texts
    for text in texts:
        one_sentence(text)


class _Gate:
    """What `Bootloader._gate_one` needs of a bootloader, for a recipe that was already checked (the data is not under test here)."""
    data_lookup = None

    def get_location(self, key):
        return Path(".")

    def get_imports_dir(self):
        return None


@pytest.mark.parametrize("code", sorted(RECIPES))
def test_homes_gate_note_has_one_period_before_suggestion(tmp_path, monkeypatch, code):
    monkeypatch.setattr(bootloader_module, "validate_data_analysis_recipe", lambda path: [])
    monkeypatch.setattr(bootloader_module, "validate_data_analysis_recipe_data", lambda *a, **k: [])
    problems, advices, contact = Bootloader._gate_one(_Gate(), str(written(tmp_path, code)))
    assert problems == [] and contact is None
    mine = [text for text in advices if text.startswith(f"[{code}]")]
    assert mine
    for text in mine:
        one_sentence(text)


@pytest.mark.parametrize("code", sorted(RECIPES))
def test_blueprints_validate_entry_has_one_period_before_suggestion(tmp_path, code):
    entries = validate_advice_entries([{"location": a.location, "problem": a.problem, "tip": a.tip} for a in checker_advices(written(tmp_path, code))])
    mine = [text for heading, text in entries if text.startswith(f"[{code}]")]
    assert mine and all(len(entry) == 2 for entry in entries)
    for text in mine:
        one_sentence(text)


@pytest.mark.parametrize("code", sorted(RECIPES))
def test_home_and_blueprint_show_the_same_string(tmp_path, monkeypatch, code):
    monkeypatch.setattr(bootloader_module, "validate_data_analysis_recipe", lambda path: [])
    monkeypatch.setattr(bootloader_module, "validate_data_analysis_recipe_data", lambda *a, **k: [])
    path = written(tmp_path, code)
    home = Bootloader._gate_one(_Gate(), str(path))[1]
    blueprint = [text for _, text in validate_advice_entries([{"location": a.location, "problem": a.problem, "tip": a.tip} for a in checker_advices(path)])]
    assert home == blueprint


def test_the_anti_case_word_for_word_on_the_three_readers(tmp_path, monkeypatch):
    """The anti-join of a table with itself, as each reader shows it."""
    monkeypatch.setattr(bootloader_module, "validate_data_analysis_recipe", lambda path: [])
    monkeypatch.setattr(bootloader_module, "validate_data_analysis_recipe_data", lambda *a, **k: [])
    path = written(tmp_path, "J12")
    what = ("[J12] The join of 'A' with itself on the same key ['a'] with how 'anti' keeps only the rows whose key is missing, "
            "because a missing key never matches. If no row has a missing key, the result is empty. ")
    fix = ("Suggestion: remove the step if you did not mean this. Suggestion: to find the rows of 'A' that have no partner in another table, "
           "write that other table as right_ingredient.")
    home = Bootloader._gate_one(_Gate(), str(path))[1]
    assert home == [what + fix]
    result = check_recipe_file(path, "run", catalogs=checker_catalogs())
    assert [p.text() for p in result.advices if p.code == "J12"] == ["joins.AA.tier1.steps[1] : " + what + fix]
    entries = validate_advice_entries([{"location": a.location, "problem": a.problem, "tip": a.tip} for a in checker_advices(path)])
    assert [(heading, text) for heading, text in entries if text.startswith("[J12]")] == [("Advice: joins.AA.tier1.steps[1]", what + fix)]


def test_no_reader_builds_the_sentence_itself():
    """The readers call `with_fix` (or a method that does); none joins a problem and a tip with an f-string."""
    boot = (ROOT / "app" / "src" / "bootloader.py").read_text()
    assert "a.tip" not in boot and "a.text()" in boot
    validator = (ROOT / "app" / "modules" / "data_analysis_recipe_validator.py").read_text()
    assert "fix_label" not in validator and validator.count("with_fix(") >= 6
    assert 'ui.tags.div(tip' not in (ROOT / "app" / "handlers" / "blueprint_handlers.py").read_text().split("advice_rows = [")[1].split("]")[0]


def test_the_real_bootloader_lists_the_anti_advice_of_a_recipe_in_the_deployment(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path)
    write_tiny(root / "data_analysis_recipes", tiny(joins=JOIN_ANTI, recipe_id="selfjoin"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    notes = Bootloader().data_analysis_recipe_advices
    assert list(notes) == ["selfjoin"] and len(notes["selfjoin"]) == 1
    for text in notes["selfjoin"]:
        one_sentence(text)
