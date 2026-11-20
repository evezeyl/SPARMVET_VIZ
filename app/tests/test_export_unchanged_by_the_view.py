"""The export holds the Result plus the audited steps whatever the mode and the data choice on screen (slice B; ui_implementation_contract 7.2).

The real export generator (run as `test_export_download_path.py` runs it) is called three times on the same recipe, data and audited steps with a
different record of the screen (`screen_view`): "Exploration mode, data view T3", "Audit mode, data view Source (table 'T')", "Audit mode, data
view T1". Every data file, the audit trail files and the pictures are the same; only the README line "Screen view" differs, and it says the
mode and the data choice. Exploration is never exported: nothing of the view is part of the content.

MUTATION E1 (the export reads the view: no audited T3 file when the view is Exploration): `test_the_content_does_not_depend_on_the_view` fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_unchanged_by_the_view.py -q
"""
import io
import zipfile
from types import SimpleNamespace

import pytest
from PIL import Image

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.audit_nodes import filter_nodes
from app.tests.test_export_download_path import _download_function, _run
from app.tests.test_tier3_reader import Tier3World

VIEWS = ["Exploration mode, data view T3", "Audit mode, data view Source (table 'T')", "Audit mode, data view T1"]


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _export(tmp_path, monkeypatch, screen_view: str) -> zipfile.ZipFile:
    world = Tier3World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    home_state = SimpleNamespace(get=lambda: {"t3_audit_steps_by_plot": {"subtab_p_steps": filter_nodes(
        [{"column": "score", "op": "le", "value": 4, "dtype": "Int64", "na": "remove"}])}})
    yielded = _run(_download_function(world, view, [], monkeypatch, home_state=home_state, screen_view=lambda: screen_view,
                                      t3_filter_rows=lambda subtab: [{"column": "score"}] if subtab == "subtab_p_steps" else [],
                                      t3_drop_columns=lambda subtab: []))
    return zipfile.ZipFile(io.BytesIO(yielded[0]))


def _content(bundle: zipfile.ZipFile) -> dict:
    """Every file by name, with what must be equal: tables and trail as text, pictures as pixels (their metadata holds a time)."""
    out = {}
    for full in bundle.namelist():
        name = full.split("/", 1)[-1]   # the first folder is named with the time of the export
        data = bundle.read(full)
        if name.endswith(".png"):
            out[name] = Image.open(io.BytesIO(data)).convert("RGB").tobytes()
        elif name.endswith((".tsv", "t3_steps.yaml")):
            out[name] = data
        else:
            out[name] = None   # present is what is compared (the timestamps inside differ)
    return out


def test_the_content_does_not_depend_on_the_view(tmp_path, monkeypatch):
    bundles = [_export(tmp_path / str(i), monkeypatch, text) for i, text in enumerate(VIEWS)]
    contents = [_content(b) for b in bundles]
    assert any(n.endswith("T3_data_p_steps.tsv") for n in contents[0]), "the audited steps are always exported"
    assert not any("EXPORT_NOT_CREATED" in n for n in contents[0])
    for other in contents[1:]:
        assert other == contents[0], "the export differs with the view on screen"


def test_the_readme_records_the_mode_and_the_data_choice(tmp_path, monkeypatch):
    for i, text in enumerate(VIEWS):
        bundle = _export(tmp_path / f"r{i}", monkeypatch, text)
        readme = bundle.read(next(n for n in bundle.namelist() if n.endswith("/README.txt"))).decode()
        assert f"Screen view      : {text}" in readme
        assert "Active tier" not in readme


def test_the_readme_differs_only_in_the_timestamp_and_the_screen_view_line(tmp_path, monkeypatch):
    lines = []
    for i, text in enumerate(VIEWS[:2]):
        bundle = _export(tmp_path, monkeypatch, text)   # the same folder: the keys hold the path of the data file
        readme = bundle.read(next(n for n in bundle.namelist() if n.endswith("/README.txt"))).decode().splitlines()
        lines.append([l for l in readme if not l.startswith(("Timestamp", "Screen view"))])
    assert lines[0] == lines[1]
