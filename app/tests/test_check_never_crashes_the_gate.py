"""A recipe the check cannot read is refused with a visible reason, never accepted and never a crash of the app.

Before: a join key that was not text (`on: [{x: 1}]`) made J08 raise `TypeError` in the checker; the exception passed through the
validator and `Bootloader._gate_one` (one dropped-in recipe could stop the start of the app), and on dev the same recipe was
accepted. Now a join key that is not text is a problem of the recipe (J05), a bad shape of an action or layer name is a problem of the
recipe (ST01, PS04), and any other exception of the check ends as ONE problem that rejects the recipe (`[CHECK] ...`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_check_never_crashes_the_gate.py -q

# @deps
# consumes: app/modules/data_analysis_recipe_validator.py (checker_problems, checker_advices, validate_data_analysis_recipe), app/src/bootloader.py (Bootloader._gate_one), libs/utils/src/utils/recipe_check.py (J05, ST01, PS04)
# doc: .claude/rules/rules_data_analysis_recipe_structure.md#11, .claude/knowledge/decision_ledger.md (D-0029)
# @end_deps
"""
import copy

import pytest

from app.modules import data_analysis_recipe_validator as validator
from app.modules.data_analysis_recipe_validator import checker_advices, checker_problems, validate_data_analysis_recipe
from app.tests.test_validator_runs_column_checks import JOIN_STEP, two_tables
from utils.recipe_factory import write_recipe


def with_on(value):
    raw = two_tables(shared_column=False)
    step = copy.deepcopy(JOIN_STEP)
    step["on"] = value
    raw["joins"]["AB"]["tier1"]["steps"] = [step]
    return raw


@pytest.mark.parametrize("bad", [[{"x": 1}], 7, [["sample_id"]], {"a": 1}, [1, 2]])
def test_a_join_key_that_is_not_text_is_reported_and_nothing_raises(tmp_path, bad):
    path = write_recipe(tmp_path / "r.yaml", with_on(bad))
    for problems in (checker_problems(path), validate_data_analysis_recipe(path)):
        found = [p for p in problems if p.problem.startswith("[J05]")]
        assert found, f"{bad!r}: the recipe was accepted or reported with no join key problem"
        assert "on" in found[0].problem and "column name" in found[0].problem
        assert not any("[CHECK]" in p.problem for p in problems), "the check itself must not fail on it"


def test_a_good_join_key_is_still_accepted(tmp_path):
    assert checker_problems(write_recipe(tmp_path / "r.yaml", with_on(["sample_id"]))) == []


def test_a_name_that_is_not_text_in_a_step_or_a_layer_is_reported_by_the_checker(tmp_path):
    raw = two_tables(shared_column=False)
    raw["joins"]["AB"]["tier1"]["steps"] = [{"action": {"x": 1}}]
    raw["analysis_groups"]["main"]["plots"]["p"]["layers"] = [{"name": ["geom_point"]}]
    text = " ".join(p.problem for p in checker_problems(write_recipe(tmp_path / "r.yaml", raw)))
    assert "[ST01]" in text and "[PS04]" in text and "[CHECK]" not in text


@pytest.fixture
def broken_check(monkeypatch):
    def boom(path, profile):
        raise RuntimeError("boom on this shape")
    monkeypatch.setattr(validator, "_check_file", boom)


def test_a_check_that_raises_rejects_the_recipe_with_a_visible_reason(tmp_path, broken_check):
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=False))
    for problems in (checker_problems(path), validate_data_analysis_recipe(path), checker_advices(path)):
        assert len(problems) == 1
        text = str(problems[0])
        assert "r.yaml" in text and "[CHECK]" in text and "RuntimeError: boom on this shape" in text and "not accepted" in text


def test_an_engine_load_that_raises_also_rejects(tmp_path, monkeypatch):
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=False))
    monkeypatch.setattr(validator, "engine_load_problems", lambda p: (_ for _ in ()).throw(ValueError("odd")))
    problems = validate_data_analysis_recipe(path)
    assert len(problems) == 1 and "[CHECK]" in problems[0].problem and "ValueError: odd" in problems[0].problem


def test_the_gate_rejects_a_recipe_the_check_fails_on_and_does_not_raise(tmp_path, broken_check):
    from app.src.bootloader import Bootloader
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=False))
    gate = Bootloader.__new__(Bootloader)
    gate.get_location = lambda key: str(tmp_path)
    gate.get_contact = lambda: None
    gate.get_imports_dir = lambda: None
    gate.data_lookup = None
    problems, advices, contact = gate._gate_one(str(path))
    assert problems and "[CHECK]" in str(problems[0]) and "boom on this shape" in str(problems[0])


def test_the_gate_rejects_a_recipe_with_a_bad_join_key(tmp_path):
    from app.src.bootloader import Bootloader
    path = write_recipe(tmp_path / "r.yaml", with_on([{"x": 1}]))
    gate = Bootloader.__new__(Bootloader)
    gate.get_location = lambda key: str(tmp_path)
    gate.get_contact = lambda: None
    gate.get_imports_dir = lambda: None
    gate.data_lookup = None
    problems, _, _ = gate._gate_one(str(path))
    assert any("[J05]" in str(p) for p in problems)


@pytest.mark.parametrize("exc", [TypeError("t"), KeyError("k"), AttributeError("a"), ValueError("v"), IndexError("i")])
def test_a_shape_exception_says_the_check_failed_on_the_shape_of_the_recipe(tmp_path, monkeypatch, exc):
    monkeypatch.setattr(validator, "_check_file", lambda path, profile: (_ for _ in ()).throw(exc))
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=False))
    problems = checker_problems(path)
    assert len(problems) == 1
    assert "failed on the shape of this recipe" in problems[0].problem and type(exc).__name__ in problems[0].problem
    assert "not accepted" in problems[0].problem


@pytest.mark.parametrize("exc", [ImportError("no module x"), OSError("disk gone"), RuntimeError("boom")])
def test_any_other_exception_says_the_check_could_not_run_and_never_blames_the_recipe(tmp_path, monkeypatch, exc):
    monkeypatch.setattr(validator, "_check_file", lambda path, profile: (_ for _ in ()).throw(exc))
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=False))
    for problems in (checker_problems(path), validate_data_analysis_recipe(path), checker_advices(path)):
        assert len(problems) == 1, "the recipe must still be refused"
        text = problems[0].problem
        assert "the check could not run" in text and type(exc).__name__ in text and str(exc) in text and "not accepted" in text
        assert "shape of this recipe" not in text
        assert "fault of the app or of its installation" in problems[0].tip
