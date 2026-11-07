"""Keys that nothing reads must not come back (ADR-091, issue evezeyl/SPARMVET_VIZ#27, phase 2).

Each key below was found by the inventory (assets/scripts/inventory_config_keys.py) to have no
reader. Documentation of a timed autosave (ghost_save.frequency_minutes) described a feature
that was never built: the saving is event-driven (Apply, leaving Home, assembly).
"""
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader

REPO = Path(__file__).resolve().parents[2]


class _Loader(yaml.SafeLoader):
    pass


_Loader.add_constructor("!include", lambda loader, node: loader.construct_scalar(node))


def _load(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=_Loader) or {}


FEATURE_FILES = sorted((REPO / "config" / "ui" / "templates").glob("*_template.yaml"))
DEPLOYMENT_FILES = sorted((REPO / "config" / "deployment").glob("*/*.yaml"))


def test_files_were_found():
    assert len(FEATURE_FILES) >= 8 and len(DEPLOYMENT_FILES) >= 3


@pytest.mark.parametrize("path", FEATURE_FILES, ids=lambda p: p.name)
def test_feature_file_has_no_dead_keys(path):
    data = _load(path)
    assert "logic_access" not in data
    assert "persona_name" not in data
    assert "frequency_minutes" not in data.get("automation", {}).get("ghost_save", {})


@pytest.mark.parametrize("path", DEPLOYMENT_FILES, ids=lambda p: p.parent.name + "/" + p.name)
def test_deployment_file_has_no_scripts_block(path):
    assert "scripts" not in _load(path)


def test_bootloader_has_no_script_path_reader():
    assert not hasattr(Bootloader, "get_script_path")
