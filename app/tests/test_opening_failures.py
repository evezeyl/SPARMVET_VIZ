"""A failure of the machine is not a fault of the recipe (opening-build fixes, finding 4; D-0326, D-0327).

The opening refuses a recipe only when the recipe or its data is at fault. A full disk, a folder that cannot be written, no memory, or a failure the app does not know
is not the recipe's: the opening stops, says so in plain words, refuses nothing (for any session), and the recipe opens when it is tried again after the machine is
right. The list of the error types that are the recipe's is in ONE place: `build_failure.RECIPE_FAULT_TYPES` (PROVISIONAL), the machine's in `MACHINE_ERRNOS`.

What is proved, headless on a real world (`Tier3World`) and, for the handler, on the REAL `Bootloader`:
- `failure_kind` says MACHINE for no memory, for an operating-system error of a disk (no space, no right, read-only), also when it is the cause of the engine's own error, and
  for the text Polars writes ("(os error 28)"); RECIPE for the engine's and the checkers' error types and Polars' errors on a step; UNKNOWN for the rest;
- a read-only store folder, a store folder under a file, a store folder that cannot be made: the opening builds nothing, `stopped` says why, no problem is invented;
- a missing store folder that can be made is made: the recipe opens;
- no memory while a table is built, while a plot is drawn, and a disk full while a table is written (through the real orchestrator: the chain is read): stopped, not refused;
- an error of an unknown type in a table build: stopped, not refused; a plot that cannot be drawn and a step that cannot be built still refuse;
- the handler: stopped means status "error", `reject_after_opening` is NOT called, the gate does not move, the page is told; a fresh session after the machine is right opens the recipe;
  the recipe problems found before the stop are told.

Mutation index (each seen failing): MUTATION M1 `failure_kind` returns RECIPE for everything -> the machine and unknown tests fail; MUTATION M2 `check_store` removed ->
the store tests fail; MUTATION M3 the handler refuses when `stopped` -> the handler test fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_opening_failures.py -q
"""
import errno
import os
import stat
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import matplotlib
matplotlib.use("Agg")
import polars as pl
import pytest
from shiny import reactive

import app.handlers.opening_handlers as handlers
from app.handlers.opening_handlers import ProvenDrawings, define_server
from app.modules import build_failure
from app.modules.build_failure import MACHINE, RECIPE, UNKNOWN, failure_kind
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.engine_registry import PlotEngines
from app.modules.opening_build import draw_plot_proof, opening_signature, run_opening
from app.tests.test_opening_handler import FakeProgress, Opening, real_opening, gate  # noqa: F401  (the fixture too)
from app.tests.test_tier3_reader import KEEP_FROM_2, Tier3World
from utils.errors import IngestionError, TransformationError, VisualizationError

ENGINES = PlotEngines()
NOT_ROOT = pytest.mark.skipif(os.geteuid() == 0, reason="root can write to a read-only folder")


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def no_draw(plot_id, table):
    return None


def opening_of(world, **kwargs):
    return run_opening(world.orch, "tiny", world.raw(), world.keys(), kwargs.pop("anchors", world.anchors), draw=kwargs.pop("draw", no_draw), **kwargs)


def real_draw(world):
    return lambda plot_id, table: draw_plot_proof(ENGINES, world.raw(), plot_id, table)


def stored(folder: Path) -> list:
    return sorted(p.name for p in folder.iterdir() if p.suffix == ".parquet") if folder.exists() else []


# ---------------------------------------------------------------------------------------------------------------------
# Whose fault: one function, one list
# ---------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("error, kind", [
    (MemoryError(), MACHINE),
    (PermissionError(errno.EACCES, "Permission denied"), MACHINE),
    (OSError(errno.ENOSPC, "No space left on device"), MACHINE),
    (OSError(errno.EROFS, "Read-only file system"), MACHINE),
    (pl.exceptions.ComputeError("parquet: File out of specification: underlying IO error: No space left on device (os error 28)"), MACHINE),
    (pl.exceptions.ComputeError("something about a value that does not fit a cast"), RECIPE),
    (TransformationError("a step failed"), RECIPE),
    (IngestionError("a dataset could not be loaded"), RECIPE),
    (VisualizationError("a plot cannot be drawn"), RECIPE),
    (FileNotFoundError(errno.ENOENT, "No such file or directory"), UNKNOWN),   # a data file the recipe names is the ENGINE's to say (an ingestion error); a bare one is not known
    (KeyError("x"), UNKNOWN),
    (RuntimeError("boom"), UNKNOWN),
])
def test_failure_kind_says_whose_fault_it_is(error, kind):
    assert failure_kind(error) == kind


def test_the_machine_is_found_under_the_engines_own_error():
    """The engine wraps what Polars raised when it wrote a table into its own error: the chain is read, not only the error on top."""
    try:
        try:
            raise OSError(errno.ENOSPC, "No space left on device")
        except OSError as inner:
            raise TransformationError("The tier 2 of the table 'C' cannot be built") from inner
    except TransformationError as wrapped:
        assert isinstance(wrapped, build_failure.RECIPE_FAULT_TYPES), "on its own that error says the recipe"
        assert failure_kind(wrapped) == MACHINE, "but its cause is the disk"


def test_the_list_of_the_recipe_fault_types_is_one_tuple_and_names_the_engines_and_checkers_errors():
    from utils.errors import SPARMVET_Error
    assert SPARMVET_Error in build_failure.RECIPE_FAULT_TYPES and pl.exceptions.PolarsError in build_failure.RECIPE_FAULT_TYPES
    assert errno.ENOSPC in build_failure.MACHINE_ERRNOS and errno.ENOENT not in build_failure.MACHINE_ERRNOS


# ---------------------------------------------------------------------------------------------------------------------
# The store folder
# ---------------------------------------------------------------------------------------------------------------------


@NOT_ROOT
def test_a_read_only_store_folder_stops_the_opening_and_refuses_nothing_and_the_recipe_opens_when_it_is_fixed(tmp_path):
    """MUTATION M2: without `check_store` the first table fails and is blamed on the recipe."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    world.anchors.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        result = opening_of(world, draw=real_draw(world))
        assert result.stopped and "not because of the recipe" in result.stopped and "Nothing is refused" in result.stopped and str(world.anchors) in result.stopped
        assert result.problems == [] and not result.ok and stored(world.anchors) == []
    finally:
        world.anchors.chmod(stat.S_IRWXU)
    again = opening_of(world, draw=real_draw(world))
    assert again.ok and again.stopped is None and stored(world.anchors) == ["C.parquet", "C__T2.parquet", "C__T3_p_steps.parquet"]


def test_a_store_folder_that_cannot_be_made_stops_the_opening(tmp_path):
    world = Tier3World(tmp_path)
    blocker = tmp_path / "a_file"
    blocker.write_text("not a folder")
    result = opening_of(world, anchors=blocker / "anchors")
    assert result.stopped and "not because of the recipe" in result.stopped and result.problems == []


def test_a_store_folder_that_does_not_exist_yet_is_made_and_the_recipe_opens(tmp_path):
    world = Tier3World(tmp_path)
    folder = tmp_path / "not" / "yet" / "anchors"
    result = opening_of(world, anchors=folder, draw=real_draw(world))
    assert result.ok and folder.is_dir() and stored(folder), "the folder is made, the tables are stored in it"


# ---------------------------------------------------------------------------------------------------------------------
# During the build and the drawing
# ---------------------------------------------------------------------------------------------------------------------


def test_no_memory_while_a_table_is_built_stops_the_opening_and_blames_nobody(tmp_path):
    world = Tier3World(tmp_path)
    with mock.patch.object(type(world.orch), "materialize_tier1", side_effect=MemoryError()):
        result = opening_of(world)
    assert result.stopped and "not because of the recipe" in result.stopped and result.problems == []


def test_no_memory_while_a_plot_is_drawn_is_the_machines_not_a_plot_that_cannot_be_drawn(tmp_path):
    world = Tier3World(tmp_path)

    def draw(plot_id, table):
        raise MemoryError()

    result = opening_of(world, draw=draw)
    assert result.stopped and result.problems == []


def test_a_full_disk_while_a_table_is_written_is_found_through_the_engines_own_error(tmp_path):
    """The real orchestrator: Polars raises its error when the file is written, the engine turns it into a transformation error, the chain says 'os error 28'."""
    world = Tier3World(tmp_path)
    full = pl.exceptions.ComputeError("parquet: File out of specification: underlying IO error: No space left on device (os error 28)")
    with mock.patch.object(pl.DataFrame, "write_parquet", side_effect=full):
        result = opening_of(world)
    assert result.stopped and "No space left on device" in result.stopped and result.problems == [], result
    assert stored(world.anchors) == []


def test_an_error_of_a_type_the_app_does_not_know_stops_the_opening_and_refuses_nothing(tmp_path):
    world = Tier3World(tmp_path)
    with mock.patch.object(type(world.orch), "materialize_tier1", side_effect=KeyError("surprise")):
        result = opening_of(world)
    assert result.stopped and "could not finish the opening" in result.stopped and "not refused" in result.stopped and result.problems == []


def test_a_fault_of_the_recipe_still_refuses_it(tmp_path):
    """MUTATION M1 (failure_kind says RECIPE for everything) would pass this one; the two tests above would not."""
    world = Tier3World(tmp_path, tier2=[{"action": "polars_drop", "columns": ["no_such_column"]}])
    result = opening_of(world, draw=real_draw(world))
    assert result.stopped is None and len(result.problems) == 1 and "tier 2 of the table 'C'" in result.problems[0]

    def draw(plot_id, table):
        raise RuntimeError("the engine says boom")

    result = opening_of(Tier3World(tmp_path / "w2"), draw=draw)
    assert result.stopped is None and result.problems[0].startswith("The plot 'p_steps' cannot be drawn")


def test_the_problems_found_before_the_stop_are_kept(tmp_path):
    world = Tier3World(tmp_path)
    seen = []

    def draw(plot_id, table):
        seen.append(plot_id)
        if plot_id == "p_steps":
            raise RuntimeError("boom")
        raise MemoryError()

    result = opening_of(world, draw=draw)
    assert seen == ["p_steps", "p_plain"]
    assert result.problems and "'p_steps'" in result.problems[0] and result.stopped


# ---------------------------------------------------------------------------------------------------------------------
# The handler: nothing is refused, for any session
# ---------------------------------------------------------------------------------------------------------------------


def test_a_stopped_opening_refuses_nothing_tells_the_page_and_a_later_session_opens_the_recipe(tmp_path, monkeypatch):
    """MUTATION M3: a handler that refuses when `stopped` hides the recipe from every session for a fault of the disk."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    opening = Opening(world, monkeypatch)
    with mock.patch.object(type(world.orch), "materialize_tier1", side_effect=MemoryError()):
        opening.run()
    assert opening.current()["status"] == "error"
    opening.bootloader.reject_after_opening.assert_not_called()
    with reactive.isolate():
        assert opening.gate_version.get() == 0, "the gate did not move"
    errors = [text for kind, text in opening.notes if kind == "error"]
    assert len(errors) == 1 and "not because of the recipe" in errors[0] and "Nothing is refused" in errors[0] and "reload the page" in errors[0]
    assert not opening.proven.has(opening_signature("tiny", world.keys())), "an opening that stopped is not remembered as proven"
    later = Opening(world, monkeypatch, proven=ProvenDrawings())
    later.run()
    assert later.current()["status"] == "ready" and later.notes == [], "the machine is right: the same recipe opens"


def test_a_stop_with_a_recipe_problem_found_before_it_tells_both_and_refuses_nothing(tmp_path, monkeypatch):
    world = Tier3World(tmp_path)
    opening = Opening(world, monkeypatch)
    calls = []

    def draw(factory, raw, plot_id, table):
        calls.append(plot_id)
        raise (RuntimeError("boom") if plot_id == "p_steps" else MemoryError())

    monkeypatch.setattr(handlers, "draw_plot_proof", draw)
    opening.run()
    opening.bootloader.reject_after_opening.assert_not_called()
    (text,) = [t for kind, t in opening.notes if kind == "error"]
    assert "not because of the recipe" in text and "1 problem(s) of the recipe were found" in text and "'p_steps'" in text


def test_a_stop_through_the_real_gate_leaves_the_recipe_available(gate, tmp_path, monkeypatch):
    run, notes = real_opening(gate, tmp_path, monkeypatch)
    with mock.patch("app.modules.opening_build.check_store", side_effect=PermissionError(errno.EACCES, "Permission denied")):
        state, version = run()
    assert state["status"] == "error" and version == 0
    assert "tiny" in gate.boot.available_data_analysis_recipes and not gate.boot.rejected_data_analysis_recipes
    assert any(kind == "error" and "not because of the recipe" in text for kind, text in notes)
