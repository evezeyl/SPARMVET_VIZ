"""The data sample tab of the Gallery shows the table the plot is drawn from, not the file read plainly (F4 of the Gallery fixes).

The handler calls `example_sample`; this test shows that for every shipped example it is the frame `example_table` builds
for the picture (same names, same dtypes, same values), and that the handler uses it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_sample.py -q   (from the project root: the data path of a recipe is relative to it)
"""
import tempfile
from pathlib import Path

import pytest

from app.modules.gallery_examples import example_sample, example_table

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "assets" / "gallery_data"
EXAMPLES = sorted(d for d in SHIPPED.iterdir() if d.is_dir())


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda d: d.name)
def test_the_sample_is_the_table_the_picture_is_drawn_from(example, tmp_path):
    sample = example_sample(example)
    drawn = example_table(example, tmp_path)
    assert sample.columns == drawn.columns
    assert sample.dtypes == drawn.dtypes
    assert sample.equals(drawn)


def test_the_sample_leaves_no_work_files_behind(monkeypatch, tmp_path):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    example_sample(EXAMPLES[0])
    assert list(tmp_path.iterdir()) == []


def test_the_handler_reads_the_sample_through_example_sample():
    source = (ROOT / "app" / "handlers" / "gallery_handlers.py").read_text(encoding="utf-8")
    body = source[source.index("def gallery_static_data"):source.index("def gallery_yaml_preview")]
    assert "example_sample(" in body and "read_csv" not in body
