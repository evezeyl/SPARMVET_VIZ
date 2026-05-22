"""Unit tests for PersonaValidator (25-B)."""
import pytest
from app.modules.persona_validator import PersonaValidator

V = PersonaValidator()

_FULL_FEATURES = {
    "interactivity_enabled": True,
    "t3_sandbox_enabled": False,
    "developer_mode_enabled": False,
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


def _tmpl(overrides=None, ms_visible=True, ms_fixed=None, testing_mode=True, persona_id=None, path="developer_template"):
    t = {
        "persona_id": persona_id or path.replace("_template", ""),
        "features": {**_FULL_FEATURES, **(overrides or {})},
        "manifest_selector": {"visible": ms_visible, "fixed_manifest": ms_fixed},
        "testing_mode": testing_mode,
    }
    return t, path


# --- Rule 1: persona_id must match filename ---

def test_persona_id_matches_filename_valid():
    t, path = _tmpl(path="developer_template", persona_id="developer")
    assert V.validate(t, path) == []


def test_persona_id_mismatch_no_longer_raises_error():
    # ADR-054 (2026-05-02) removed Rule 1: persona_id/filename coupling dropped
    # so persona configs can live anywhere and be referenced by absolute path.
    t, path = _tmpl(path="developer_template", persona_id="qa")
    errors = V.validate(t, path)
    assert not any("does not match filename" in e for e in errors)


# --- Rule 2: persona_id must use hyphens ---

def test_persona_id_underscore_raises_error():
    t, path = _tmpl(path="pipeline_exploration_advanced_template",
                    persona_id="pipeline_exploration_advanced")
    errors = V.validate(t, path)
    assert any("underscores" in e for e in errors)


def test_persona_id_hyphen_is_valid():
    t, path = _tmpl(path="pipeline-exploration-advanced_template",
                    persona_id="pipeline-exploration-advanced")
    assert V.validate(t, path) == []


# --- Rule 3: missing flags produce warnings only (not errors) ---

def test_missing_flag_no_error(capsys):
    t = {
        "persona_id": "developer",
        "features": {},  # all missing
        "manifest_selector": {"visible": True, "fixed_manifest": None},
        "testing_mode": True,
    }
    errors = V.validate(t, "developer_template")
    assert errors == []
    captured = capsys.readouterr()
    assert "WARNING" in captured.out


# --- Rule 4: manifest_selector.visible=false requires fixed_manifest ---

def test_manifest_selector_hidden_no_fixed_manifest_warns(capsys):
    t, path = _tmpl(path="pipeline-static_template",
                    persona_id="pipeline-static",
                    ms_visible=False, ms_fixed=None)
    errors = V.validate(t, path)
    assert errors == [], "null fixed_manifest is a warning, not an error (dev/template default)"
    captured = capsys.readouterr()
    assert "fixed_manifest" in captured.out


def test_manifest_selector_hidden_with_fixed_manifest_ok():
    t, path = _tmpl(path="pipeline-static_template",
                    persona_id="pipeline-static",
                    ms_visible=False, ms_fixed="/data/manifests/project.yaml")
    assert V.validate(t, path) == []


def test_manifest_selector_visible_no_fixed_manifest_ok():
    t, path = _tmpl(path="developer_template", persona_id="developer",
                    ms_visible=True, ms_fixed=None)
    assert V.validate(t, path) == []


# --- validate_file: real template files ---

def test_validate_real_developer_template():
    errors = V.validate_file("config/ui/templates/developer_template.yaml")
    assert errors == [], f"developer_template errors: {errors}"


def test_validate_real_pipeline_static_template():
    # fixed_manifest is set in the template, so no fixed_manifest warning expected
    errors = V.validate_file("config/ui/templates/pipeline-static_template.yaml")
    assert errors == [], f"pipeline-static_template errors: {errors}"


def test_validate_real_qa_template():
    errors = V.validate_file("config/ui/templates/qa_template.yaml")
    assert errors == [], f"qa_template errors: {errors}"


def test_validate_missing_file():
    errors = V.validate_file("config/ui/templates/nonexistent_template.yaml")
    assert any("not found" in e for e in errors)


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
