"""The ID cleaning steps that Test Lab writes into a data analysis recipe are real steps (task ID-RECON-STEPS-1).

The ID reconciliation library has its own small step language (`lowercase`, `regex_replace`, ...), run by its own
`apply_recode_step`. Those names are not registered actions. Wherever such a step becomes a step of a recipe it must be
a format 1 step: a registered action, with exactly the parameters of that action, that gives the same IDs.

Three levels are checked here, because they need the action registry and the app together:
  1. every step of the library's language, translated, passes the action's own check and gives the same IDs;
  2. every step the library suggests after a reconciliation does the same;
  3. the path the app takes (uploaded files -> scaffold ZIP) writes those steps into the right file of the recipe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_id_cleaning_steps_reach_a_recipe.py -q
"""
import ast
import inspect
import io
import zipfile
from pathlib import Path

import polars as pl
import pytest
import yaml

import transformer  # noqa: F401  (registers the actions)
from app.modules.test_lab_studio import scaffold_from_uploads
from id_reconciliation import IDReconciliationEngine, IdTransformation, apply_recode_step, recipe_steps
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS
from utils.ui_schema import step_problems

REPO = Path(__file__).resolve().parents[2]
COLUMN = "sample_id"

# One valid step of every action that `apply_recode_step` runs, with IDs on which the step changes something.
INTERNAL_STEPS = {
    "strip_whitespace": ({"action": "strip_whitespace"}, ["  a1 ", "b2\t", "c3"]),
    "cast_string": ({"action": "cast_string"}, [1, 2, 3]),
    "regex_replace": ({"action": "regex_replace", "pattern": "^.{2}", "replacement": ""}, ["x_a1", "x_b2", "x"]),
    "lowercase": ({"action": "lowercase"}, ["A1", "b2", "C3"]),
    "mutate": ({"action": "mutate", "expression": f"pl.col('{COLUMN}').str.slice(0, 2)"}, ["a1_r", "b2_r", "c"]),
    "drop_duplicates": ({"action": "drop_duplicates"}, ["a1", "b2", "a1", "c3", "b2"]),
    "null_if": ({"action": "null_if", "value": "NA"}, ["a1", "NA", "c3"]),
    "drop_nulls": ({"action": "drop_nulls"}, ["a1", None, "c3"]),
}

# IDs for which the reconciliation suggests one cleaning pattern: name -> (IDs to clean, IDs to reach).
SUGGESTIONS = {
    "remove a prefix": ([f"sample_{i:03d}" for i in range(1, 6)], [f"{i:03d}" for i in range(1, 6)]),
    "remove a suffix": ([f"{i:03d}_R1" for i in range(1, 6)], [f"{i:03d}" for i in range(1, 6)]),
    "lower case": ([f"ABC{i}" for i in range(1, 6)], [f"abc{i}" for i in range(1, 6)]),
    "underscore to hyphen": ([f"a_{i}" for i in range(1, 6)], [f"a-{i}" for i in range(1, 6)]),
}


def _problems(step: dict) -> list:
    action = step["action"]
    assert action in AVAILABLE_WRANGLING_ACTIONS, f"{action} is not a registered action"
    return [p.text() for p in step_problems(action, step, ACTION_SCHEMAS[action])]


def _run(steps: list, frame: pl.DataFrame) -> pl.DataFrame:
    """Run recipe steps the way the engine does: each registered action on the table the previous step left."""
    lf = frame.lazy()
    for step in steps:
        lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, step)
    return lf.collect()


def _suggested(refs, targets) -> IdTransformation:
    engine = IDReconciliationEngine()
    return engine.generate_transformation(engine.reconcile(refs, targets), COLUMN, "ID")


# ---- 1. every step of the library's language ---------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(INTERNAL_STEPS))
def test_the_step_is_not_a_registered_action_before_it_is_translated(name):
    """Why the translation exists: written as it is into a recipe, the step would be an unknown action."""
    assert INTERNAL_STEPS[name][0]["action"] not in AVAILABLE_WRANGLING_ACTIONS


@pytest.mark.parametrize("name", sorted(INTERNAL_STEPS))
def test_a_translated_step_passes_the_check_of_its_action(name):
    step, _ = INTERNAL_STEPS[name]
    translated = recipe_steps(IdTransformation(COLUMN, "ID", [step]), COLUMN)
    assert translated, "the step was dropped"
    for recipe_step in translated:
        assert _problems(recipe_step) == []


@pytest.mark.parametrize("name", sorted(INTERNAL_STEPS))
def test_a_translated_step_gives_the_same_ids_as_the_library(name):
    step, ids = INTERNAL_STEPS[name]
    transformation = IdTransformation(COLUMN, "ID", [step])
    frame = pl.DataFrame({COLUMN: ids, "other": list(range(len(ids)))})
    expected = apply_recode_step(frame, COLUMN, transformation)
    got = _run(recipe_steps(transformation, COLUMN), frame)
    assert expected[COLUMN].to_list() != ids or name == "cast_string", "the example must change something"
    # apply_recode_step promises no row order after drop_duplicates; the recipe step keeps the order of the file
    if name == "drop_duplicates":
        assert got[COLUMN].to_list() == ["a1", "b2", "c3"]
        assert sorted(expected[COLUMN].to_list()) == sorted(got[COLUMN].to_list())
    else:
        assert got.equals(expected), f"\nlibrary: {expected}\nrecipe: {got}"
    assert got.schema == expected.schema
    assert got["other"].to_list() == expected.sort("other")["other"].to_list(), "no other column is touched"


def test_all_steps_in_one_list_give_the_same_ids_as_the_library():
    steps = [INTERNAL_STEPS[n][0] for n in ("strip_whitespace", "lowercase", "regex_replace", "null_if", "drop_nulls")]
    transformation = IdTransformation(COLUMN, "ID", steps)
    frame = pl.DataFrame({COLUMN: ["  X_A1 ", "x_b2", "x_NA", None, "X_NA"]})
    got = _run(recipe_steps(transformation, COLUMN), frame)
    assert got.equals(apply_recode_step(frame, COLUMN, transformation))
    assert got[COLUMN].to_list() == ["a1", "b2", "na", "na"], "lower case runs before null_if, as the list says"


# ---- 2. every step the library suggests ------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(SUGGESTIONS))
def test_a_suggested_step_reaches_the_recipe_as_a_sound_step_that_gives_the_matched_ids(name):
    refs, targets = SUGGESTIONS[name]
    transformation = _suggested(refs, targets)
    assert transformation.steps, "the reconciliation matched by a pattern but suggested no step"
    translated = recipe_steps(transformation, COLUMN)
    assert len(translated) == len(transformation.steps)
    for recipe_step in translated:
        assert _problems(recipe_step) == []
    frame = pl.DataFrame({COLUMN: refs})
    assert _run(translated, frame)[COLUMN].to_list() == targets
    assert apply_recode_step(frame, COLUMN, transformation)[COLUMN].to_list() == targets


def test_ids_that_already_match_suggest_no_step():
    ids = [f"{i:03d}" for i in range(1, 6)]
    assert recipe_steps(_suggested(ids, ids), COLUMN) == []


# ---- 3. the path the app takes: uploaded files -> scaffold ZIP -----------------------------------------------------

@pytest.fixture
def uploads(tmp_path):
    """Two uploaded files as Shiny hands them over: the name the user gave, and a path named by the upload order."""
    first = tmp_path / "0.tsv"
    first.write_text("Sample ID\tspecies\n" + "".join(f"sample_{i:03d}\tE. coli\n" for i in range(1, 6)))
    second = tmp_path / "1.tsv"
    second.write_text("ID\tgene\n" + "".join(f"{i:03d}\tblaTEM\n" for i in range(1, 6)))
    return [{"name": "isolates.tsv", "datapath": str(first)}, {"name": "amr_results.tsv", "datapath": str(second)}]


def _wrangling(zip_bytes: bytes) -> dict:
    """The wrangling fragments of a scaffold ZIP: file name in the ZIP -> its content."""
    out = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            if name.endswith("_wrangling.yaml"):
                out[name] = yaml.safe_load(zf.read(name).decode())
    return out


def _fragment_of(zip_bytes: bytes, upload: dict) -> dict:
    stem = Path(upload["datapath"]).stem
    matches = [content for name, content in _wrangling(zip_bytes).items() if name.endswith(f"/{stem}_wrangling.yaml")]
    assert len(matches) == 1, sorted(_wrangling(zip_bytes))
    return matches[0]


def _prefix_transformation() -> IdTransformation:
    engine = IDReconciliationEngine()
    refs = [f"sample_{i:03d}" for i in range(1, 6)]
    targets = [f"{i:03d}" for i in range(1, 6)]
    return engine.generate_transformation(engine.reconcile(refs, targets), "Sample ID", "ID")


def test_the_steps_are_written_into_the_file_the_user_chose_and_only_there(uploads):
    zb = scaffold_from_uploads(uploads, "proj", "sample_id",
                               id_transformation=_prefix_transformation(), id_file_name="isolates.tsv")
    chosen = _fragment_of(zb, uploads[0])
    assert len(chosen["tier1"]) == 1
    assert _fragment_of(zb, uploads[1])["tier1"] == [], "the other file takes no step"
    for step in chosen["tier1"]:
        assert _problems(step) == []


def test_the_written_steps_clean_the_column_of_the_file_under_its_recipe_name(uploads):
    """The recipe names a column by its slug (`Sample ID` -> `sample_id`); the steps must name the same column."""
    zb = scaffold_from_uploads(uploads, "proj", "sample_id",
                               id_transformation=_prefix_transformation(), id_file_name="isolates.tsv")
    steps = _fragment_of(zb, uploads[0])["tier1"]
    as_read_by_the_recipe = pl.read_csv(uploads[0]["datapath"], separator="\t").rename({"Sample ID": "sample_id"})
    cleaned = _run(steps, as_read_by_the_recipe)
    assert cleaned["sample_id"].to_list() == pl.read_csv(uploads[1]["datapath"], separator="\t",
                                                         infer_schema_length=0)["ID"].to_list()


def test_choosing_the_other_file_moves_the_steps(uploads):
    """Two files that must stay separate: the steps follow the choice, not the upload order."""
    engine = IDReconciliationEngine()
    transformation = engine.generate_transformation(
        engine.reconcile([f"{i:03d}_R1" for i in range(1, 6)], [f"{i:03d}" for i in range(1, 6)]), "ID", "Sample ID")
    zb = scaffold_from_uploads(uploads, "proj", "sample_id",
                               id_transformation=transformation, id_file_name="amr_results.tsv")
    assert _fragment_of(zb, uploads[0])["tier1"] == []
    assert [s["columns"] for s in _fragment_of(zb, uploads[1])["tier1"]] == [["id"]]


def test_without_a_reconciliation_no_step_is_written(uploads):
    zb = scaffold_from_uploads(uploads, "proj", "sample_id")
    assert [content["tier1"] for content in _wrangling(zb).values()] == [[], []]


def test_a_reconciliation_that_needs_no_cleaning_writes_no_step(uploads):
    nothing_to_do = IdTransformation("Sample ID", "ID", [])
    zb = scaffold_from_uploads(uploads, "proj", "sample_id",
                               id_transformation=nothing_to_do, id_file_name="isolates.tsv")
    assert [content["tier1"] for content in _wrangling(zb).values()] == [[], []]


def test_a_file_without_the_id_column_is_refused_and_named(uploads):
    """The steps clean `Sample ID`; `amr_results.tsv` has no such column, so nothing may be written for it."""
    with pytest.raises(ValueError, match="amr_results.tsv") as error:
        scaffold_from_uploads(uploads, "proj", "sample_id",
                              id_transformation=_prefix_transformation(), id_file_name="amr_results.tsv")
    assert "Sample ID" in str(error.value)


def test_a_file_that_was_not_uploaded_is_refused(uploads):
    with pytest.raises(ValueError, match="other.tsv"):
        scaffold_from_uploads(uploads, "proj", "sample_id",
                              id_transformation=_prefix_transformation(), id_file_name="other.tsv")


def test_two_uploads_with_one_name_are_refused(uploads):
    uploads[1]["name"] = "isolates.tsv"
    with pytest.raises(ValueError, match="isolates.tsv"):
        scaffold_from_uploads(uploads, "proj", "sample_id",
                              id_transformation=_prefix_transformation(), id_file_name="isolates.tsv")


@pytest.mark.parametrize("given", [{"id_transformation": IdTransformation("Sample ID", "ID", [])},
                                   {"id_file_name": "isolates.tsv"}])
def test_the_transformation_and_its_file_come_together(uploads, given):
    with pytest.raises(ValueError, match="together"):
        scaffold_from_uploads(uploads, "proj", "sample_id", **given)


def test_the_handler_calls_the_scaffold_with_parameters_it_has():
    """The Scaffold button raised a TypeError: the handler passed a keyword the scaffolder did not have.

    The handler runs only in a browser, so this reads its source: every call of `scaffold_from_uploads` must fit the
    function's signature.
    """
    source = (REPO / "app/handlers/test_lab_handlers.py").read_text(encoding="utf-8")
    calls = [node for node in ast.walk(ast.parse(source))
             if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "scaffold_from_uploads"]
    assert calls, "the handler no longer calls scaffold_from_uploads: this test looks at nothing"
    signature = inspect.signature(scaffold_from_uploads)
    for call in calls:
        signature.bind(*[None] * len(call.args), **{keyword.arg: None for keyword in call.keywords})
