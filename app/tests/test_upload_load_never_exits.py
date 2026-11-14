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


# --- one strict reader for a fragment (BP-UPLOAD-EXIT-1, review point 1) ---

def _fragment(tmp_path, text):
    p = tmp_path / "frag.yaml"
    p.write_text(text)
    return load_uploaded_recipe(p)


def test_fragment_with_a_repeated_key_is_refused_and_names_the_key(tmp_path):
    raw, problems = _fragment(tmp_path, "wrangling:\n  tier1:\n    - action: polars_join\n      how: left\n      how: inner\n")
    assert raw is None
    assert problems and all(t.startswith("[LOAD]") for t in problems)
    assert any("how" in t and "twice" in t for t in problems)


def test_fragment_with_an_unquoted_on_says_to_quote_it(tmp_path):
    raw, problems = _fragment(
        tmp_path, "wrangling:\n  tier1:\n    - action: polars_join\n      right_ingredient: m\n      on: sample_id\n")
    assert raw is None
    assert any("quote" in t for t in problems), problems


def test_fragment_with_an_include_inside_the_project_still_loads(tmp_path):
    (tmp_path / "t1.yaml").write_text("- action: polars_cast\n  columns: [a]\n  dtype: Int64\n")
    raw, problems = _fragment(tmp_path, "wrangling:\n  tier1: !include t1.yaml\n")
    assert problems == [] and raw["wrangling"]["tier1"][0]["action"] == "polars_cast"


# --- the other ConfigManager calls of the Blueprint handlers (review point 2) ---

from app.modules.data_analysis_recipe_validator import load_config_or_problems


@pytest.mark.parametrize("name", sorted(set(BAD) - {"empty", "only_comment", "list_root", "bad_yaml"}))
def test_config_helper_never_exits_on_a_contradictory_file(tmp_path, name):
    p = tmp_path / f"{name}.yaml"
    p.write_text(BAD[name])
    try:
        cfg, problems = load_config_or_problems(p)
    except BaseException as exc:
        pytest.fail(f"escaped: {type(exc).__name__}")
    assert cfg is None and problems and problems[0].startswith("[LOAD]")


def test_config_helper_returns_the_config_of_a_good_recipe(tmp_path):
    from utils.recipe_factory import minimal_recipe, write_recipe
    p = write_recipe(tmp_path / "good.yaml", minimal_recipe("good"))
    cfg, problems = load_config_or_problems(p)
    assert problems == [] and "data_schemas" in cfg.raw_config


def test_blueprint_handlers_call_no_bare_configmanager():
    import ast
    from pathlib import Path
    src = Path(__file__).resolve().parents[1] / "handlers" / "blueprint_handlers.py"
    calls = [n.lineno for n in ast.walk(ast.parse(src.read_text()))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "ConfigManager"]
    assert calls == [], f"bare ConfigManager( at lines {calls}: use load_config_or_problems"
