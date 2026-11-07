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


def _tmpl(overrides=None, ms_visible=True, ms_fixed=None, testing_mode=True, app_features_id=None, path="developer"):
    t = {
        "name": app_features_id or path,
        "flags": {**_FULL_FEATURES, **(overrides or {})},
        "data_analysis_recipe_selector": {"visible": ms_visible},
        "testing_mode": testing_mode,
    }
    return t, path


# --- Rule 1: name must match filename ---

def test_app_features_id_matches_filename_valid():
    t, path = _tmpl(path="developer", app_features_id="developer")
    assert V.validate(t, path) == []


def test_app_features_id_mismatch_no_longer_raises_error():
    # ADR-054 (2026-05-02) removed Rule 1: name/filename coupling dropped
    # so app features configs can live anywhere and be referenced by absolute path.
    t, path = _tmpl(path="developer", app_features_id="qa")
    errors = V.validate(t, path)
    assert not any("does not match filename" in e for e in errors)


# --- Rule 2: name must use hyphens ---

def test_app_features_id_underscore_raises_error():
    t, path = _tmpl(path="pipeline_exploration_advanced",
                    app_features_id="pipeline_exploration_advanced")
    errors = V.validate(t, path)
    assert any("underscores" in e.problem for e in errors)


def test_app_features_id_hyphen_is_valid():
    t, path = _tmpl(path="pipeline-exploration-advanced",
                    app_features_id="pipeline-exploration-advanced")
    assert V.validate(t, path) == []


# --- Rule 3: missing flags produce warnings only (not errors) ---

def test_missing_flag_no_error(capsys):
    t = {
        "name": "developer",
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
    t, path = _tmpl(path="pipeline-static", app_features_id="pipeline-static", ms_visible=False)
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
