"""The gallery check at app start (spec section 9: G3, DEC48): the same check as the index rebuild, only when the Gallery is on.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_check_at_start.py -q
"""
import json
import os
import shutil
from pathlib import Path

import pytest

from app.modules import gallery_examples
from app.modules.gallery_examples import check_gallery_at_start, rebuild_gallery_index
from app.src.bootloader import Bootloader

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "assets" / "gallery_data"
RECIPE = "data_analysis_recipe.yaml"


def _gallery(tmp_path: Path, *names: str) -> Path:
    work = tmp_path / "gallery_data"
    for name in names:
        shutil.copytree(SHIPPED / name, work / name)
    rebuild_gallery_index(work)
    return work


def _add_broken(work: Path) -> None:
    shutil.copytree(work / "bar_simple", work / "bar_wrong")
    text = (work / "bar_wrong" / RECIPE).read_text().replace("bar_simple", "bar_wrong").replace("name: geom_bar", "name: geom_barr")
    (work / "bar_wrong" / RECIPE).write_text(text)


def _stub_bootloader(monkeypatch, gallery: Path, enabled: bool) -> Bootloader:
    """A Bootloader without the deployment: only what the gallery step reads."""
    boot = object.__new__(Bootloader)
    boot.flags = {"gallery_enabled": enabled}
    monkeypatch.setattr(Bootloader, "get_location", lambda self, key: gallery)
    return boot


def test_all_valid_nothing_is_left_out_and_the_index_file_is_not_touched(tmp_path):
    work = _gallery(tmp_path, "bar_simple", "histogram_simple" if (SHIPPED / "histogram_simple").exists() else "bar_simple")
    before = (work / "gallery_index.json").read_bytes()
    examples, status = check_gallery_at_start(work)
    assert examples.rejected == {} and status == "unchanged"
    assert (work / "gallery_index.json").read_bytes() == before


def test_one_broken_example_is_left_out_with_its_reason_and_nothing_raises(tmp_path):
    work = _gallery(tmp_path, "bar_simple")
    _add_broken(work)
    examples, status = check_gallery_at_start(work)
    assert list(examples.accepted) == ["bar_simple"] and status == "rewritten"
    assert any("[PS04]" in reason for reason in examples.rejected["bar_wrong"])
    index = json.loads((work / "gallery_index.json").read_text())
    assert list(index["registry"]) == ["bar_simple"] and "bar_wrong" in index["metadata"]["rejected"]
    # an example that breaks later is also removed from an index that still lists it, and a second start has nothing to do
    assert check_gallery_at_start(work)[1] == "unchanged"


def test_a_folder_that_cannot_be_written_keeps_the_app_running(tmp_path):
    if os.geteuid() == 0:
        pytest.skip("root can write everywhere")
    work = _gallery(tmp_path, "bar_simple")
    _add_broken(work)
    (work / "gallery_index.json").chmod(0o444)
    work.chmod(0o555)
    try:
        examples, status = check_gallery_at_start(work)
    finally:
        work.chmod(0o755)
    assert status == "not_writable" and "bar_wrong" in examples.rejected


def test_the_bootloader_runs_the_check_when_the_gallery_is_enabled(tmp_path, monkeypatch):
    work = _gallery(tmp_path, "bar_simple")
    _add_broken(work)
    boot = _stub_bootloader(monkeypatch, work, enabled=True)
    boot._check_gallery_if_enabled()
    assert list(boot.rejected_gallery_examples) == ["bar_wrong"] and boot.gallery_index_status == "rewritten"


def test_the_bootloader_does_not_touch_the_gallery_when_it_is_off(tmp_path, monkeypatch):
    work = _gallery(tmp_path, "bar_simple")
    _add_broken(work)
    calls = []
    monkeypatch.setattr(gallery_examples, "check_gallery_at_start", lambda d: calls.append(d))
    boot = _stub_bootloader(monkeypatch, work, enabled=False)
    boot._check_gallery_if_enabled()
    assert calls == [] and boot.gallery_index_status == "not_run" and boot.rejected_gallery_examples == {} and "bar_wrong" not in json.loads((work / "gallery_index.json").read_text())["metadata"]["rejected"]


def test_a_failing_check_never_stops_the_app(tmp_path, monkeypatch):
    boot = _stub_bootloader(monkeypatch, tmp_path / "missing", enabled=True)
    monkeypatch.setattr(gallery_examples, "check_gallery_at_start", lambda d: (_ for _ in ()).throw(RuntimeError("boom")))
    boot._check_gallery_examples()
    assert boot.gallery_index_status == "failed"


@pytest.mark.parametrize("app_features, expected_calls", [("qa", 1), ("pipeline-exploration-advanced", 0)])
def test_the_real_constructor_calls_the_check_only_when_the_gallery_flag_is_on(monkeypatch, app_features, expected_calls):
    """The wiring itself: a real Bootloader (no stub) reaches the check at start, gated by `gallery_enabled`."""
    calls = []
    monkeypatch.setattr(gallery_examples, "check_gallery_at_start", lambda d: (calls.append(d), (gallery_examples.Examples({}, {}, frozenset()), "unchanged"))[1])
    boot = Bootloader(app_features=app_features)
    assert boot.is_enabled("gallery_enabled") == bool(expected_calls)
    assert len(calls) == expected_calls


def test_the_index_write_is_atomic(tmp_path, monkeypatch):
    """A write that fails in the middle leaves the old index whole and no temporary file."""
    import viz_gallery.gallery_manager as manager
    work = _gallery(tmp_path, "bar_simple")
    before = (work / "gallery_index.json").read_bytes()
    _add_broken(work)

    def broken_dump(obj, handle, **kwargs):
        handle.write('{"registry": ')
        raise OSError("disk full")
    monkeypatch.setattr(manager.json, "dump", broken_dump)
    with pytest.raises(OSError):
        rebuild_gallery_index(work)
    assert (work / "gallery_index.json").read_bytes() == before
    assert [p.name for p in work.iterdir() if p.name.endswith(".tmp")] == []
    assert check_gallery_at_start(work)[1] == "not_writable"
