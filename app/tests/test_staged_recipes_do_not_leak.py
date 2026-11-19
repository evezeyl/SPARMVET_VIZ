"""A staged recipe in the tracked recipe folder (Blueprint tests) is told apart by its owner and never survives its run.

The name is `zz_gate_gap_stage_p<pid>_<hex>`: two files or workers never share one, a run removes the leftovers of runs
whose process is gone and never touches those of a live process, and `conftest.py` fails the session of a process that
leaves one behind.
"""
import os
import subprocess
import sys

from app.tests import gate_stage as g


def _dead_pid() -> int:
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    return child.pid


def test_each_stage_has_its_own_name(tmp_path):
    first = g.stage(blueprint=True)
    name_one = g.STAGE
    try:
        assert (g.PIPELINES / f"{name_one}.yaml").exists()
        assert f"_p{os.getpid()}_" in name_one
        assert g.own_leftovers()
    finally:
        g.unstage()
    g.stage(blueprint=True)
    try:
        assert g.STAGE != name_one
    finally:
        g.unstage()
    assert not g.own_leftovers()
    assert first.name == "deployment.yaml"


def test_leftovers_of_a_dead_run_are_removed_and_a_live_one_is_kept():
    dead, live = _dead_pid(), os.getppid()
    paths = []
    for pid in (dead, live):
        name = f"{g.STAGE_PREFIX}_p{pid}_deadbeef"
        (g.PIPELINES / f"{name}.yaml").write_text("id: x\n")
        (g.PIPELINES / name).mkdir()
        paths += [g.PIPELINES / f"{name}.yaml", g.PIPELINES / name]
    try:
        removed = g.remove_dead_leftovers()
        assert {p.name for p in removed} == {f"{g.STAGE_PREFIX}_p{dead}_deadbeef.yaml", f"{g.STAGE_PREFIX}_p{dead}_deadbeef"}
        assert not paths[0].exists() and not paths[1].exists()
        assert paths[2].exists() and paths[3].exists()
    finally:
        for path in paths:
            g.remove_path(path)


def test_a_failed_run_leaves_nothing(tmp_path):
    try:
        with g.running_app(tmp_path, blueprint=True):
            raise RuntimeError("the test failed")
    except RuntimeError:
        pass
    assert not g.own_leftovers()


def test_the_end_of_session_guard_sees_a_leak():
    leak = g.PIPELINES / f"{g.STAGE_PREFIX}_p{os.getpid()}_00000000.yaml"
    leak.write_text("id: x\n")
    try:
        assert g.own_leftovers() == [leak]
    finally:
        leak.unlink()
