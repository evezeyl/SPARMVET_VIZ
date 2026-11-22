"""The ingestion handler passes a display text to the bootloader as a launch value.

Finding (task INGESTION-DISPLAY-NAME-AS-LAUNCH-VALUE): `handle_ingest` calls
`bootloader.__init__(app_features=current_app_features.get())`, and `current_app_features`
holds the DISPLAY name ("QA / Test Harness"). These tests record two facts:
1. no user space mounts the button `btn_ingest` or the file input `file_ingest`, so the handler
   cannot run in the app (dead code);
2. if it did run, the display text would be read as a path and the start would fail.
"""
import re
from pathlib import Path

import pytest

from app.src.bootloader import Bootloader

REPO = Path(__file__).resolve().parents[2]
MOUNT = re.compile(r"""input_(action_button|file|action_link)\(\s*["'](btn_ingest|file_ingest)["']""")


def _sources():
    for root in ("app", "libs", "config"):
        for p in (REPO / root).rglob("*"):
            if p.suffix in (".py", ".yaml", ".js") and p.is_file() and "tests" not in p.parts:
                yield p


def test_no_user_space_mounts_the_ingest_button_or_file_input():
    mounts = [str(p.relative_to(REPO)) for p in _sources()
              if MOUNT.search(p.read_text(encoding="utf-8", errors="ignore"))]
    assert mounts == [], f"the ingest handler became reachable ({mounts}); fix its launch value first"


def test_only_the_handler_names_the_ingest_ids():
    names = [str(p.relative_to(REPO)) for p in _sources()
             if re.search(r"\b(btn_ingest|file_ingest)\b", p.read_text(encoding="utf-8", errors="ignore"))]
    assert names == ["app/handlers/ingestion_handlers.py"]


@pytest.mark.parametrize("display", ["QA / Test Harness", "Web Demo"])
def test_a_display_name_is_not_a_launch_value(display, monkeypatch):
    monkeypatch.chdir(REPO)
    for var in ("SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(SystemExit):
        Bootloader(app_features=display)
