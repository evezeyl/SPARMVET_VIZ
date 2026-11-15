"""GATE-GAP-1: the export of a recipe that is not available says so plainly and hands over EXPORT_NOT_CREATED.txt.

Before: with a missing `!include` or a YAML syntax error, `compute_data_analysis_recipe_keys` raised inside the download and
the user got a failed download with no message ("Exception in ASGI application" in the log).
"""
import io
import zipfile
from pathlib import Path

import pytest

from app.modules.export_refusal import export_refusal, unavailable_export_text
from app.modules.orchestrator import DataOrchestrator

REPO = Path(__file__).resolve().parents[2]


class Notes:
    def __init__(self):
        self.calls = []

    def __call__(self, message, **kwargs):
        self.calls.append((kwargs.get("type"), message))


class FakeBootloader:
    def __init__(self, rejected=None):
        self.rejected_data_analysis_recipes = rejected or {}


def _write(tmp_path, kind):
    path = tmp_path / "broken.yaml"
    if kind == "yaml_syntax":
        path.write_text("id: broken\ninfo: [unclosed\n  - : :\n")
    else:
        path.write_text("id: broken\ndata_schemas:\n  A:\n    input_fields: !include 'broken/missing.yaml'\n")
    return path


@pytest.mark.parametrize("kind", ["yaml_syntax", "missing_include"])
def test_a_recipe_that_cannot_be_read_gives_the_not_created_file_not_a_crash(tmp_path, kind):
    _write(tmp_path, kind)
    orchestrator = DataOrchestrator(data_analysis_recipes_dir=tmp_path, raw_data_dir=REPO / "assets" / "test_data")
    with pytest.raises((ValueError, FileNotFoundError)) as raised:   # what the download used to die of
        orchestrator.compute_data_analysis_recipe_keys("broken")
    notes = Notes()

    refusal = export_refusal(FakeBootloader(), "broken", raised.value, notes)

    assert refusal is not None
    archive = zipfile.ZipFile(io.BytesIO(refusal))
    assert archive.namelist() == ["EXPORT_NOT_CREATED.txt"]
    text = archive.read("EXPORT_NOT_CREATED.txt").decode()
    assert "'broken'" in text and "not available" in text and "nothing was exported" in text
    assert "cannot be read any more" in text and "Blueprint" in text
    assert notes.calls and notes.calls[0][0] == "error" and "broken" in notes.calls[0][1]


def test_a_recipe_rejected_by_the_gate_is_refused_with_its_problems_and_contact():
    record = {"problems": ["[ST02] unknown action 'zz'"], "contact": "lab@example.org"}
    notes = Notes()

    refusal = export_refusal(FakeBootloader({"r": record}), "r", None, notes)

    text = zipfile.ZipFile(io.BytesIO(refusal)).read("EXPORT_NOT_CREATED.txt").decode()
    assert "[ST02]" in text and "lab@example.org" in text and "'r'" in text


def test_a_recipe_that_reads_and_passes_is_not_refused():
    notes = Notes()
    assert export_refusal(FakeBootloader(), "fine", None, notes) is None
    assert notes.calls == []


def test_the_text_names_what_to_do():
    assert "fix it, and save" in unavailable_export_text("x", ValueError("boom"), None)


def test_the_export_download_asks_before_it_uses_the_keys():
    """The guard sits where the download starts: the refusal comes before anything is computed from the recipe."""
    source = (REPO / "app" / "handlers" / "export_handlers.py").read_text()
    start = source.index("async def export_bundle_download")
    body = source[start:]
    assert body.index("export_refusal(") < body.index("changed_since_view(")
