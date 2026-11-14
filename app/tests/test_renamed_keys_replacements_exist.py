"""The replacements that renamed_keys.py names must be names that exist now.

Covers: every replacement that is a bare identifier (a key, flag, panel type, file name or
variable) is found in the code, the config files or the shipped app features files, and the
values named for data_lookup are the choices of the orchestrator. It cannot check a
replacement written as a sentence (for example "branding.banner in the deployment file");
those are checked only for their identifiers in the data_lookup case.
"""
import re
from pathlib import Path

import pytest

from app.modules import renamed_keys as rk
from app.modules.orchestrator import DATA_LOOKUP_CHOICES

ROOT = Path(__file__).resolve().parents[2]
SEARCHED = [p for d in ("app", "config", "libs") for p in (ROOT / d).rglob("*")
            if p.suffix in {".py", ".yaml"} and "tests" not in p.parts]
CORPUS = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in SEARCHED)

TABLES = [rk.RENAMED_DEPLOYMENT_KEYS, rk.RENAMED_LOCATION_KEYS, rk.RENAMED_APP_FEATURES_KEYS,
          rk.RENAMED_FLAG_KEYS, rk.RENAMED_APP_FEATURES_NAMES, rk.RENAMED_PANEL_TYPES,
          rk.RENAMED_SESSION_KEYS, rk.RENAMED_ENV_VARS]
BARE = [new for t in TABLES for new in t.values() if new and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", new)]


@pytest.mark.parametrize("name", sorted(set(BARE)))
def test_a_bare_replacement_exists_in_the_project(name):
    last = name.split(".")[-1]
    assert last in CORPUS, f"renamed_keys.py names {name!r} as the new name, but it is found nowhere"


def test_the_data_lookup_values_named_exist():
    message = rk.RENAMED_DEPLOYMENT_KEYS["prefer_discovery"]
    named = re.search(r"\((\w+) or (\w+)\)", message).groups()
    assert set(named) <= set(DATA_LOOKUP_CHOICES), (named, DATA_LOOKUP_CHOICES)
    assert set(named) == set(DATA_LOOKUP_CHOICES)
