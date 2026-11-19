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


def test_valid_tiers_fragment_gives_no_line():
    step = {"action": "polars_cast", "columns": ["a"], "dtype": "Int64"}
    raw = {"tier1": {"steps": [step]}, "tier2": {"steps": []}}
    assert uploaded_recipe_report(raw) == []


def test_valid_tier_file_gives_no_line():
    assert uploaded_recipe_report({"steps": [{"action": "polars_cast", "columns": ["a"], "dtype": "Int64"}]}) == []


def test_bad_step_in_fragment_names_step_and_problem():
    raw = {"tier1": {"steps": [{"action": "polars_cast", "columns": ["a"], "dtype": "Int64"}, {"action": "polars_cast", "nope": 1}]}}
    lines = uploaded_recipe_report(raw)
    assert any(l.startswith("[ST03] tier1[2] (polars_cast)") and "nope" in l for l in lines)
    assert any(l.startswith("[ST04] tier1[2] (polars_cast)") for l in lines)
    assert not any("tier1[1]" in l for l in lines)


def test_unknown_action_in_fragment():
    lines = uploaded_recipe_report({"steps": [{"action": "no_such_action"}]})
    assert lines and lines[0].startswith("[ST02] steps[1]")


def test_old_shape_upload_is_refused_with_UP02_and_nothing_is_read():
    """The old `wrangling:` shape and a tier written as a list are refused with [UP02]; no step of them is checked."""
    step = {"action": "polars_cast", "columns": ["a"], "dtype": "Int64"}
    for old in ({"wrangling": {"tier1": [step], "tier2": []}}, {"wrangling": [step]}, {"tier1": [step]}):
        lines = uploaded_recipe_report(old)
        assert len(lines) == 1 and lines[0].startswith("[UP02]"), (old, lines)


def test_empty_mapping_and_empty_file_say_nothing_to_import():
    assert uploaded_recipe_report({})[0].startswith("[UP01]")
    assert uploaded_recipe_report(None)[0].startswith("[UP01]")


def test_whole_recipe_with_bad_key_gives_the_exact_code():
    raw = minimal_recipe("up")
    raw["bogus_key"] = 1
    assert any(l.startswith("[RC") or l.startswith("[T0") for l in uploaded_recipe_report(raw))


def test_warn_on_upload_does_not_raise_when_notification_fails(monkeypatch):
    from app.handlers import blueprint_handlers as bh

    def boom(*a, **k):
        raise RuntimeError("no session")
    monkeypatch.setattr(bh.ui, "notification_show", boom)
    bh._warn_on_upload({"steps": [{"action": "no_such_action"}]}, "f.yaml")
