"""What the bootloader gives for the branding of every shipped deployment (headless).

The proof that the customized deployments (demo-vetinst and web-demo) still show what they showed before the rename of the banner
keys (D-0411: `title` -> `ui_label`, `subtitle` -> `description`): the values below are the ones recorded before the rename. The keys are
read through `deployment_branding_keys`. The expected values are read from the YAML file, so a test fails when the reader of the
bootloader stops reading a key that the file sets. A deployment has no name key any more (D-0479).
"""
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader
from app.tests.deployment_branding_keys import banner_line, banner_logo, banner_title

REPO = Path(__file__).resolve().parents[2]
# The demo file starts only where its user directory exists (not in a fresh clone): test_demo_deployment_file.py starts a copy of it.
TESTED_ELSEWHERE = {"202612_demo_deployment.yaml"}
SHIPPED = sorted(p for p in (REPO / "config" / "deployment").glob("*/*.yaml")
                 if not p.name.endswith("_template.yaml") and p.name not in TESTED_ELSEWHERE)
CUSTOMIZED = {"demo/demo-vetinst.yaml", "demo/web-demo.yaml"}
DEFAULT_CSS = "config/ui/theme.css"


def _rel(p):
    return f"{p.parent.name}/{p.name}"


@pytest.fixture(autouse=True)
def start_from_repo(monkeypatch):
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(REPO)


def _boot(path, monkeypatch):
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(path))
    if "default_app_features" not in yaml.safe_load(path.read_text()):
        monkeypatch.setenv("SPARMVET_APP_FEATURES", "pipeline-static")
    return Bootloader()


def test_the_two_customized_deployments_are_among_the_shipped_ones():
    assert CUSTOMIZED <= {_rel(p) for p in SHIPPED}


@pytest.mark.parametrize("path", SHIPPED, ids=_rel)
def test_branding_the_bootloader_gives_equals_what_the_file_sets(path, monkeypatch):
    file_data = yaml.safe_load(path.read_text())
    branding = file_data.get("branding") or {}
    banner = branding.get("banner") or {}
    b = _boot(path, monkeypatch)
    assert b.get_ui_banner() == (banner or None)
    assert banner_title(b.get_ui_banner()) == banner_title(banner)
    assert banner_line(b.get_ui_banner()) == banner_line(banner)
    assert banner_logo(b.get_ui_banner()) == banner_logo(banner)
    assert str(b.get_theme_css_path()) == branding.get("theme_css", DEFAULT_CSS)
    assert b.get_contact() == (branding.get("contact") or None)
    assert not hasattr(b, "deployment_name")
    assert b.show_recipe_name() is (branding.get("show_recipe_name", True) is not False)
    # the files named exist
    assert b.get_theme_css_path().exists()
    if banner_logo(banner) and not banner_logo(banner).startswith("http"):
        assert Path(banner_logo(banner)).exists()


@pytest.mark.parametrize("path", [p for p in SHIPPED if _rel(p) not in CUSTOMIZED], ids=_rel)
def test_the_other_deployments_have_the_defaults(path, monkeypatch):
    b = _boot(path, monkeypatch)
    # no banner, the base stylesheet
    assert b.get_ui_banner() is None
    assert str(b.get_theme_css_path()) == DEFAULT_CSS


def test_demo_vetinst_values_as_they_are_today(monkeypatch):
    b = _boot(REPO / "config/deployment/demo/demo-vetinst.yaml", monkeypatch)
    assert banner_title(b.get_ui_banner()) == "AMR Surveillance — Overview"
    assert banner_line(b.get_ui_banner()) == "Norwegian Veterinary Institute"
    assert banner_logo(b.get_ui_banner()) == "assets/demo/logo-no.svg"
    assert str(b.get_theme_css_path()) == "assets/demo/demo_vetinst.css"
    assert b.get_contact() == "amr-surveillance@vetinst.no"


def test_web_demo_values_as_they_are_today(monkeypatch):
    b = _boot(REPO / "config/deployment/demo/web-demo.yaml", monkeypatch)
    # the banner holds a logo and empty text
    assert banner_title(b.get_ui_banner()) == "" and banner_line(b.get_ui_banner()) == ""
    assert banner_logo(b.get_ui_banner()) == "assets/demo/logo-no.svg"
    assert str(b.get_theme_css_path()) == "assets/demo/web_demo.css"
    assert b.get_contact() is None


def test_the_keys_of_the_banner_are_the_new_ones_in_both_customized_files():
    for rel in CUSTOMIZED:
        banner = yaml.safe_load((REPO / "config/deployment" / rel).read_text())["branding"]["banner"]
        assert set(banner) == {"logo_url", "ui_label", "description"}, (rel, banner)
