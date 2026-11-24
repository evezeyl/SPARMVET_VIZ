"""Unit tests for AppFeaturesValidator (25-B)."""
import pytest
from app.modules.app_features_validator import AppFeaturesValidator

V = AppFeaturesValidator()

_FULL_FEATURES = {
    "interactivity_enabled": True,
    "t3_sandbox_enabled": False,
    "gallery_enabled": False,
    "blueprint_enabled": False,
    "test_lab_enabled": False,
    "comparison_mode_enabled": False,
    "session_management_enabled": False,
    "import_helper_enabled": False,
    "export_enabled": True,
    "metadata_ingestion_enabled": False,
    "data_ingestion_enabled": False,
}


def _tmpl(overrides=None, ms_visible=True, ms_fixed=None, testing_mode=True, path="developer"):
    t = {
        "flags": {**_FULL_FEATURES, **(overrides or {})},
        "data_analysis_recipe_selector": {"visible": ms_visible},
        "testing_mode": testing_mode,
    }
    return t, path


# --- The id of an app features file is its file name; both hyphens and underscores are free (D-0481, D-0483) ---

def test_an_underscore_in_the_file_name_is_not_an_error():
    t, path = _tmpl(path="pipeline_exploration_advanced")
    assert V.validate(t, path) == []


def test_the_hyphen_in_the_file_name_is_not_an_error():
    t, path = _tmpl(path="pipeline-exploration-advanced")
    assert V.validate(t, path) == []


# --- Rule 3: missing flags produce warnings only (not errors) ---

def test_missing_flag_no_error(capsys):
    t = {
        "flags": {},  # all missing
        "data_analysis_recipe_selector": {"visible": True},
        "testing_mode": True,
    }
    errors = V.validate(t, "developer")
    assert errors == []
    captured = capsys.readouterr()
    assert "WARNING" in captured.out


# --- Rule 4 (removed, ADR-091): a hidden selector needs no data analysis recipe name in the app features file ---

def test_hidden_selector_is_fine_in_the_app_features_file():
    t, path = _tmpl(path="pipeline-static", ms_visible=False)
    errors = V.validate(t, path)
    assert errors == []


# --- validate_file: real template files ---

def test_validate_real_developer_app_features_file():
    errors = V.validate_file("config/app_features/developer.yaml")
    assert errors == [], f"developer errors: {errors}"


def test_validate_real_pipeline_static_app_features_file():
    # the app features file names no data analysis recipe (the deployment does) expected
    errors = V.validate_file("config/app_features/pipeline-static.yaml")
    assert errors == [], f"pipeline-static errors: {errors}"


def test_validate_real_qa_app_features_file():
    errors = V.validate_file("config/app_features/qa.yaml")
    assert errors == [], f"qa errors: {errors}"


def test_validate_missing_file():
    errors = V.validate_file("config/app_features/nonexistent.yaml")
    assert any("not found" in e.problem for e in errors)


# --- Rule 5: child flags must not be True when master gate is False ---

def test_child_true_master_false_warns_interactivity(capsys):
    """comparison_mode_enabled=True with interactivity_enabled=False → warning."""
    t, path = _tmpl(overrides={
        "interactivity_enabled": False,
        "comparison_mode_enabled": True,
        "t3_sandbox_enabled": True,
        "session_management_enabled": True,
    })
    errors = V.validate(t, path)
    assert errors == [], "Rule 5 violation is a warning, not an error"
    captured = capsys.readouterr()
    assert "comparison_mode_enabled" in captured.out
    assert "interactivity_enabled" in captured.out


def test_multiple_children_warn_when_master_false(capsys):
    """Child flag True with interactivity_enabled=False → warning."""
    t, path = _tmpl(overrides={
        "interactivity_enabled": False,
        "session_management_enabled": True,
    })
    V.validate(t, path)
    captured = capsys.readouterr()
    assert "session_management_enabled" in captured.out


def test_data_ingestion_true_import_helper_false_warns(capsys):
    """data_ingestion_enabled=True with import_helper_enabled=False → warning."""
    t, path = _tmpl(overrides={
        "import_helper_enabled": False,
        "data_ingestion_enabled": True,
    })
    errors = V.validate(t, path)
    assert errors == []
    captured = capsys.readouterr()
    assert "data_ingestion_enabled" in captured.out
    assert "import_helper_enabled" in captured.out


def test_no_cascade_warning_when_master_true(capsys):
    """No Rule 5 warning when master gate is True."""
    t, path = _tmpl(overrides={
        "interactivity_enabled": True,
        "comparison_mode_enabled": True,
        "session_management_enabled": True,
        "import_helper_enabled": True,
        "data_ingestion_enabled": True,
    })
    V.validate(t, path)
    captured = capsys.readouterr()
    # Should NOT contain cascade warnings
    assert "has no effect" not in captured.out


def test_child_false_master_false_no_warning(capsys):
    """No Rule 5 warning when child is already False (correct configuration)."""
    t, path = _tmpl(overrides={
        "interactivity_enabled": False,
        "comparison_mode_enabled": False,
        "session_management_enabled": False,
    })
    V.validate(t, path)
    captured = capsys.readouterr()
    assert "has no effect" not in captured.out


# --- Rule 6 (D-0018): the audit requires comparison, sessions and export; comparison requires the audit ---

_AUDIT_ON = {"t3_sandbox_enabled": True, "comparison_mode_enabled": True,
             "session_management_enabled": True, "export_enabled": True}


def test_audit_with_all_companions_is_valid():
    t, path = _tmpl(overrides=_AUDIT_ON)
    assert V.validate(t, path) == []


@pytest.mark.parametrize("missing", ["comparison_mode_enabled", "session_management_enabled", "export_enabled"])
def test_audit_without_a_companion_refuses_the_start(missing):
    t, path = _tmpl(overrides={**_AUDIT_ON, missing: False})
    errors = V.validate(t, path)
    assert len(errors) == 1
    e = errors[0]
    assert f"t3_sandbox_enabled is true but {missing} is false" in e.problem
    assert "requires comparison, sessions and export" in e.problem
    assert missing in e.fix and "t3_sandbox_enabled" in e.fix
    assert path in e.location


def test_comparison_without_audit_refuses_the_start():
    t, path = _tmpl(overrides={"comparison_mode_enabled": True})
    errors = V.validate(t, path)
    assert len(errors) == 1
    assert errors[0].problem == ("comparison_mode_enabled is true but t3_sandbox_enabled is false: "
                                 "comparison requires the audit")
    assert "t3_sandbox_enabled: true" in errors[0].fix and "comparison_mode_enabled: false" in errors[0].fix


def test_a_deployment_override_that_breaks_the_pair_is_refused():
    t, path = _tmpl(overrides=_AUDIT_ON)
    assert V.validate(t, path) == []
    errors = V.validate(t, path, flag_overrides={"comparison_mode_enabled": False})
    assert len(errors) == 1
    assert "app_features_override" in errors[0].location
    errors = V.validate(*_tmpl(), flag_overrides={"comparison_mode_enabled": True})
    assert len(errors) == 1 and "app_features_override" in errors[0].location


def test_a_deployment_override_that_repairs_the_pair_passes():
    t, path = _tmpl(overrides={"comparison_mode_enabled": True})
    assert V.validate(t, path, flag_overrides={"t3_sandbox_enabled": True,
                                               "session_management_enabled": True}) == []


def test_the_file_is_never_silently_rewritten():
    t, path = _tmpl(overrides={"comparison_mode_enabled": True})
    V.validate(t, path)
    assert t["flags"]["comparison_mode_enabled"] is True


def test_every_shipped_app_features_file_passes_the_pair_rule():
    from pathlib import Path
    for f in sorted(Path("config/app_features").glob("*.yaml")):
        assert V.validate_file(str(f)) == [], f.name


def test_the_simple_setup_has_no_comparison_and_no_audit():
    text = open("config/app_features/pipeline-exploration-simple.yaml").read()
    assert "\n  comparison_mode_enabled: false" in text and "\n  t3_sandbox_enabled: false" in text


# --- one thing said per flag: a fatal rule and the soft-cascade warning never both name the same flag (D-0018) ---

def test_interactivity_off_comparison_on_audit_off_prints_only_the_fatal_line(capsys):
    t, path = _tmpl(overrides={"interactivity_enabled": False, "comparison_mode_enabled": True})
    errors = V.validate(t, path)
    assert [e.problem for e in errors] == [
        "comparison_mode_enabled is true but t3_sandbox_enabled is false: comparison requires the audit"]
    out = capsys.readouterr().out
    assert "comparison_mode_enabled" not in out and "no effect" not in out, out


def test_interactivity_off_audit_on_comparison_off_prints_only_the_fatal_line_for_the_audit(capsys):
    t, path = _tmpl(overrides={"interactivity_enabled": False, "t3_sandbox_enabled": True, "comparison_mode_enabled": False,
                               "session_management_enabled": True})
    errors = V.validate(t, path)
    assert [e.problem for e in errors] == [
        "t3_sandbox_enabled is true but comparison_mode_enabled is false: the audit requires comparison, sessions and export"]
    out = capsys.readouterr().out
    assert "t3_sandbox_enabled" not in out
    # a flag no fatal rule names keeps its warning
    lines = [l for l in out.splitlines() if "no effect" in l]
    assert lines == ["[AppFeaturesValidator] WARNING: 'session_management_enabled=True' has no effect — "
                     "'interactivity_enabled=False' (bootloader cascade will suppress it at runtime). Fix the template."]


def test_a_consistent_file_with_interactivity_off_still_warns_for_each_flag(capsys):
    t, path = _tmpl(overrides={"interactivity_enabled": False, **_AUDIT_ON})
    assert V.validate(t, path) == []
    out = capsys.readouterr().out
    for flag in ("t3_sandbox_enabled", "comparison_mode_enabled", "session_management_enabled"):
        assert f"'{flag}=True' has no effect" in out
