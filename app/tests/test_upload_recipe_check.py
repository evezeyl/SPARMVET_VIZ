"""Blueprint upload check: the uploaded recipe is judged in profile build, reported, never blocked (BP-VALIDATE-1)."""
from app.modules.data_analysis_recipe_validator import uploaded_recipe_report
from utils.recipe_factory import minimal_recipe


def test_valid_recipe_gives_no_lines():
    assert uploaded_recipe_report(minimal_recipe("up")) == []


def test_broken_recipe_lists_errors_with_codes():
    raw = minimal_recipe("up")
    raw["bogus_key"] = 1
    lines = uploaded_recipe_report(raw)
    assert lines and all(line.startswith("[") for line in lines)


def test_non_mapping_is_reported_not_raised():
    assert uploaded_recipe_report(["not", "a", "recipe"])


def test_build_profile_accepts_empty_placeholders():
    raw = minimal_recipe("up")
    raw["analysis_groups"] = {}
    assert uploaded_recipe_report(raw) == []
