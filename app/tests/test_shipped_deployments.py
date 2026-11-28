"""Every deployment file that ships with the app starts the app (ADR-091).

A deployment that hides the recipe selector must name its recipe; a branding block must
point at files that exist; the default app features must exist. These were each found by
hand once (a damaged comment in pipeline_test.yaml swallowed the default recipe key).
"""
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader

REPO = Path(__file__).resolve().parents[2]
# Tested by its own file: it names no default recipe and its user directory is not in a fresh clone (test_demo_deployment_file.py).
TESTED_ELSEWHERE = {"202612_demo_deployment.yaml"}
SHIPPED = sorted(p for p in (REPO / "config" / "deployment").glob("*/*.yaml")
                 if not p.name.endswith("_template.yaml") and p.name not in TESTED_ELSEWHERE)


@pytest.fixture(autouse=True)
def start_from_repo(monkeypatch):
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(REPO)


def test_deployment_files_were_found():
    assert len(SHIPPED) >= 5


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_shipped_deployment_starts_with_no_other_setting(path, monkeypatch):
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(path))
    if "default_app_features" not in yaml.safe_load(path.read_text()):
        # a deployment made for several app features (pipeline_test): name one, as a launch would
        monkeypatch.setenv("SPARMVET_APP_FEATURES", "pipeline-static")
    b = Bootloader()
    assert b.app_features_path.exists()
    assert b.get_default_data_analysis_recipe() in b.available_data_analysis_recipes
    branding = yaml.safe_load(path.read_text()).get("branding") or {}
    if branding.get("theme_css"):
        assert Path(branding["theme_css"]).exists()
    logo = (branding.get("banner") or {}).get("logo_url")
    if logo and not logo.startswith("http"):
        assert Path(logo).exists()


@pytest.mark.parametrize("path", sorted(REPO.glob("config/deployment/*/*_template.yaml")), ids=lambda p: p.name)
def test_deployment_templates_are_valid_yaml_and_use_the_new_keys(path):
    data = yaml.safe_load(path.read_text())
    assert "locations" in data and "data_analysis_recipes" in data["locations"]
    for old in ("default_manifest", "default_persona", "prefer_discovery", "scripts"):
        assert old not in data
