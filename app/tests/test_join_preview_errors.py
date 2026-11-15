"""The Blueprint join preview shows only expected errors as "Preview failed" (D13).

A programming error (a missing import once was shown as the user's mistake) must not be swallowed.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_join_preview_errors.py -q
"""
import polars as pl
import pytest

from app.handlers.blueprint_handlers import JOIN_PREVIEW_INTERNAL_ERROR, run_join_preview, safe_join_preview
from pathlib import Path

from app.modules.orchestrator import DataOrchestrator
from app.tests.tiny_recipe import tiny_recipe, write_tiny
from utils.errors import DataAnalysisRecipeError, IngestionError
from utils.recipe_factory import minimal_join


def _frame(rows):
    lf = pl.LazyFrame(rows)
    return lf, {k: str(v) for k, v in lf.collect_schema().items()}


def _rows(lf, keys):
    return lf.select([pl.col(k) for k in keys]).unique().collect().rows()


def _ok(ingredient_id):
    return _frame({"sample_id": ["a", "b"]})


def test_a_good_preview_has_the_match_stats():
    result = run_join_preview(_ok, _rows, "l", "r", ["sample_id"], ["sample_id"])
    assert result["error"] is None and result["verdict"]["ok"]
    assert result["_meta"]["left_ing"] == "l"


@pytest.mark.parametrize("error", [IngestionError("Dataset 'x' could not be loaded"),
                                   FileNotFoundError("recipe gone"),
                                   pl.exceptions.ColumnNotFoundError("key")])
def test_an_expected_error_is_shown_with_its_message(error):
    def materialise(ingredient_id):
        raise error
    result = run_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result["error"].startswith("Preview failed: ") and str(error) in result["error"]


@pytest.mark.parametrize("error", [NameError("check_join_keys"), AttributeError("x"), TypeError("x"), ImportError("x"), KeyError("x"),
                                   ValueError("bad int()")])
def test_a_programming_error_is_not_shown_as_the_users_mistake(error):
    def materialise(ingredient_id):
        raise error
    with pytest.raises(type(error)):
        run_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])


# -- the effect: no exception may escape it (Shiny closes the session of the user otherwise)

@pytest.mark.parametrize("error", [NameError("check_join_keys"), AttributeError("x"), TypeError("x"), KeyError("x"),
                                   ValueError("bad int()")])
def test_the_effect_catches_a_programming_error_and_says_it_is_internal(error, caplog):
    def materialise(ingredient_id):
        raise error
    result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result == {"error": JOIN_PREVIEW_INTERNAL_ERROR}
    assert any(r.exc_info and r.exc_info[1] is error for r in caplog.records)  # the traceback is in the log


def test_the_two_messages_differ():
    def user_error(ingredient_id):
        raise IngestionError("Dataset 'x' could not be loaded")
    def bug(ingredient_id):
        raise NameError("x")
    mine = safe_join_preview(user_error, _rows, "l", "r", ["k"], ["k"])["error"]
    internal = safe_join_preview(bug, _rows, "l", "r", ["k"], ["k"])["error"]
    assert mine != internal
    assert "internal error" in internal and "internal error" not in mine
    assert "Dataset 'x' could not be loaded" in mine


# -- the two recipe mistakes the orchestrator names: the user must see them as their mistake, not as an internal error

def _materialise_through_the_orchestrator(tmp_path, recipe, collection):
    write_tiny(tmp_path, recipe)
    orchestrator = DataOrchestrator(tmp_path, Path("."))

    def materialise(ingredient_id):
        out = tmp_path / f"{ingredient_id}.parquet"
        orchestrator.materialize_tier1(data_analysis_recipe_id=recipe["id"], collection_id=collection, output_path=out)
        return _frame({"k": ["a"]})
    return materialise


def test_an_unknown_join_id_is_shown_as_the_users_mistake(tmp_path):
    materialise = _materialise_through_the_orchestrator(tmp_path, tiny_recipe("m"), "NoSuchJoin")
    result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result["error"].startswith("Preview failed: No join or data schema 'NoSuchJoin'")
    assert result["error"] != JOIN_PREVIEW_INTERNAL_ERROR


def test_a_join_that_names_an_unknown_schema_is_shown_as_the_users_mistake(tmp_path):
    recipe = tiny_recipe("m")
    recipe["joins"] = {"J": minimal_join(["A", "NoSuchSchema"], [])}
    materialise = _materialise_through_the_orchestrator(tmp_path, recipe, "J")
    result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert "which is not a data schema of this recipe" in result["error"] and "'NoSuchSchema'" in result["error"]
    assert result["error"] != JOIN_PREVIEW_INTERNAL_ERROR


def test_the_orchestrator_raises_the_recipe_error_type(tmp_path):
    write_tiny(tmp_path, tiny_recipe("m"))
    with pytest.raises(DataAnalysisRecipeError, match="No join or data schema"):
        DataOrchestrator(tmp_path, Path(".")).materialize_tier1(
            data_analysis_recipe_id="m", collection_id="Nope", output_path=tmp_path / "x.parquet")


# -- a recipe file that cannot be read or parsed is the user's mistake, and nothing may escape the effect

def test_an_unreadable_data_file_is_shown_as_the_users_mistake(tmp_path):
    """PermissionError is an OSError: a file the user cannot read is a data problem, not an internal error."""
    def materialise(ingredient_id):
        raise PermissionError(13, "Permission denied", str(tmp_path / "data.tsv"))
    result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result["error"].startswith("Preview failed: ") and "Permission denied" in result["error"]
    assert result["error"] != JOIN_PREVIEW_INTERNAL_ERROR


def test_a_file_made_unreadable_in_a_temporary_folder(tmp_path):
    import os
    if os.geteuid() == 0:
        pytest.skip("root reads every file")
    data = tmp_path / "data.tsv"
    data.write_text("k\na\n")
    data.chmod(0)

    def materialise(ingredient_id):
        data.read_text()
    try:
        result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    finally:
        data.chmod(0o600)
    assert "Permission denied" in result["error"] and result["error"] != JOIN_PREVIEW_INTERNAL_ERROR


def test_a_broken_yaml_is_shown_as_the_recipe_problem_not_an_exit(tmp_path):
    """ConfigManager calls sys.exit(1) on a broken file; SystemExit is not an Exception and would escape the effect."""
    (tmp_path / "m.yaml").write_text("id: m\nanalysis_groups: [unclosed\n  - : :\n", encoding="utf-8")
    orchestrator = DataOrchestrator(tmp_path, Path("."))

    def materialise(ingredient_id):
        orchestrator.materialize_tier1(data_analysis_recipe_id="m", collection_id="A", output_path=tmp_path / "x.parquet")
    result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result["error"].startswith("Preview failed: cannot load data analysis recipe")
    assert "Malformed YAML" in result["error"]
    assert result["error"] != JOIN_PREVIEW_INTERNAL_ERROR


def test_a_system_exit_from_anywhere_else_does_not_escape_the_effect():
    def materialise(ingredient_id):
        raise SystemExit(2)
    result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert "error" in result
