"""What the bootloader gives for the branding of every shipped deployment (headless).

TODAY'S BEHAVIOUR, RECORDED BEFORE THE RENAME OF D-0411. The owner decided to rename the banner keys of the deployment
(`title` -> `ui_label`, `subtitle` -> `description`) on the condition that the customized deployments (demo-vetinst and
web-demo) still show what they show today. These tests must stay green after that rename; the keys are read through
`deployment_branding_keys`, the single place to change. The expected values are read from the YAML file, so a test
fails when the reader of the bootloader stops reading a key that the file sets.
"""
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader
from app.tests.deployment_branding_keys import banner_line, banner_logo, banner_title

REPO = Path(__file__).resolve().parents[2]
SHIPPED = sorted(p for p in (REPO / "config" / "deployment").glob("*/*.yaml") if not p.name.endswith("_template.yaml"))
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
    # today's behaviour, recorded before the rename of D-0411
    assert b.get_ui_banner() == (banner or None)
    assert banner_title(b.get_ui_banner()) == banner_title(banner)
    assert banner_line(b.get_ui_banner()) == banner_line(banner)
    assert banner_logo(b.get_ui_banner()) == banner_logo(banner)
    assert str(b.get_theme_css_path()) == branding.get("theme_css", DEFAULT_CSS)
    assert b.get_contact() == (branding.get("contact") or None)
    assert b.deployment_name == file_data.get("deployment_name", "SPARMVET_VIZ (Local Dev)")
    # the files named exist
    assert b.get_theme_css_path().exists()
    if banner_logo(banner) and not banner_logo(banner).startswith("http"):
        assert Path(banner_logo(banner)).exists()


@pytest.mark.parametrize("path", [p for p in SHIPPED if _rel(p) not in CUSTOMIZED], ids=_rel)
def test_the_other_deployments_have_the_defaults(path, monkeypatch):
    b = _boot(path, monkeypatch)
    # today's behaviour, recorded before the rename of D-0411: no banner, the base stylesheet
    assert b.get_ui_banner() is None
    assert str(b.get_theme_css_path()) == DEFAULT_CSS


def test_demo_vetinst_values_as_they_are_today(monkeypatch):
    b = _boot(REPO / "config/deployment/demo/demo-vetinst.yaml", monkeypatch)
    # today's behaviour, recorded before the rename of D-0411
    assert banner_title(b.get_ui_banner()) == "AMR Surveillance — Overview"
    assert banner_line(b.get_ui_banner()) == "Norwegian Veterinary Institute"
    assert banner_logo(b.get_ui_banner()) == "assets/demo/logo-no.svg"
    assert str(b.get_theme_css_path()) == "assets/demo/demo_vetinst.css"
    assert b.get_contact() == "amr-surveillance@vetinst.no"
    assert b.deployment_name == "SPARMVET demo (demo-vetinst)"


def test_web_demo_values_as_they_are_today(monkeypatch):
    b = _boot(REPO / "config/deployment/demo/web-demo.yaml", monkeypatch)
    # today's behaviour, recorded before the rename of D-0411: the banner holds a logo and empty text
    assert banner_title(b.get_ui_banner()) == "" and banner_line(b.get_ui_banner()) == ""
    assert banner_logo(b.get_ui_banner()) == "assets/demo/logo-no.svg"
    assert str(b.get_theme_css_path()) == "assets/demo/web_demo.css"
    assert b.get_contact() is None
    assert b.deployment_name == "SPARMVET demo (web-demo)"
