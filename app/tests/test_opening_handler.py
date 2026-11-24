"""HOME's opening of a recipe: the effect, the progress line, the refusal through the load gate (opening-build, D-0326, D-0334, D-0335, D-0336, D-0327).

`app/handlers/opening_handlers.py` run headless: Shiny's `Effect` is replaced by a function that records the effect, `ui.Progress` by a recorder, `notify` by a
list. The recipe, the data, the orchestrator, the keys and the stored tables are real. The refusal tests use the REAL `Bootloader` (its load gate), on a recipe
that passes the gate and fails when it is drawn.

What is proved:
- the first opening builds and stores, draws every plot, sets the state, and shows a progress line that moves from "tables 0 of N, plots 0 of M" to the end and is
  closed (the line goes) when it is done;
- the same opening again (same state) does nothing at all; a new session (empty state) with the same signature reads the tables, builds nothing and does not draw again
  what was drawn in this process (`ProvenDrawings`); a new signature (changed data) builds and draws;
- nothing happens in another workspace, for a recipe HOME cannot open, or when the keys cannot be read; the effect writes the state with a guard;
- a large plot is warned about through the Alerts notifier, nothing is refused (the constant `LARGE_PLOT_ROWS` read when the opening runs);
- a recipe with a plot that cannot be drawn is refused through the real gate: not available, rejected with its problems, its contact, `when: opening`; the gate
  version moved and the shared `recipe_gate_version` with it; the text says it could not be opened; it comes back when its files change (and is refused again if
  it still fails); a recipe whose plots all draw opens and stays available.

Mutation index (each seen failing): MUTATION H1 the effect does not call `reject_after_opening` -> the refusal tests fail; MUTATION H2 the progress is not closed (no `with`)
-> the progress test fails; MUTATION H3 `ProvenDrawings.has` is always False -> the no-second-drawing test fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_opening_handler.py -q
"""
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import matplotlib
matplotlib.use("Agg")
import pytest
import yaml
from shiny import reactive

import app.handlers.opening_handlers as handlers
import app.modules.opening_build as opening_build
from app.handlers.opening_handlers import ProvenDrawings, define_server, opening_waits
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import rejected_recipe_text
from app.modules.engine_registry import PlotEngines
from app.modules.opening_build import opening_signature
from app.src.bootloader import Bootloader
from app.tests.test_tier3_reader import KEEP_FROM_2, Tier3World

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class FakeProgress:
    """Records what the progress line shows: each message, and that it was closed."""
    instances: list = []

    def __init__(self, min=0, max=1):
        self.min, self.max, self.messages, self.values, self.closed = min, max, [], [], False
        FakeProgress.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.closed = True

    def set(self, value=None, message=None, detail=None):
        self.values.append(value)
        self.messages.append(message)


class Opening:
    """The effect of `opening_handlers.define_server` over a staged world, with fakes for what is the screen's."""

    def __init__(self, world, monkeypatch, *, available=("tiny",), workspace="Home", proven=None, state=None, bootloader=None, drawn=None, id_run_state=None):
        FakeProgress.instances = []
        self.world, self.notes, self.drawn = world, [], drawn if drawn is not None else []
        monkeypatch.setattr(handlers.ui, "Progress", FakeProgress)
        # the cover (HOME-WALK A): the calls are recorded, in order, with the progress line's opening among them
        self.ui_calls = []
        monkeypatch.setattr(handlers.ui, "insert_ui", lambda content, selector, where="beforeEnd", immediate=False, **kw:
                            self.ui_calls.append(("insert", selector, where, immediate, str(content))))
        monkeypatch.setattr(handlers.ui, "remove_ui", lambda selector, immediate=False, **kw: self.ui_calls.append(("remove", selector, immediate)))
        self.session = mock.MagicMock()
        self.effects = {}
        monkeypatch.setattr(reactive, "Effect", lambda fn: self.effects.setdefault(fn.__name__, fn) and fn)
        self.inputs = {"sidebar_nav": workspace, "data_analysis_recipe_id": "tiny"}
        self.bootloader = bootloader or mock.MagicMock()
        if bootloader is None:
            self.bootloader.available_data_analysis_recipes = {name: "x" for name in available}
            self.bootloader.get_location.return_value = world.root / "user"
            self.bootloader.data_analysis_recipe_gate_version = 0
        self.state = reactive.Value(state or {})
        self.gate_version = reactive.Value(0)
        self.proven = proven if proven is not None else ProvenDrawings()
        self.factory = mock.MagicMock()
        self.factory.render.side_effect = lambda lf, recipe, plot_id, **kw: self.drawn.append(plot_id) or "plot"
        monkeypatch.setattr(handlers, "draw_plot_proof", lambda factory, raw, plot_id, table: self.drawn.append(plot_id))
        self.keys_error = None

        def view_keys():
            if self.keys_error:
                raise self.keys_error
            return world.orch.compute_data_analysis_recipe_keys("tiny")

        define_server(mock.MagicMock(), mock.MagicMock(), self.session, bootloader=self.bootloader, orchestrator=world.orch, viz_factory=self.factory,
                      safe_input=lambda i, k, d: self.inputs.get(k, d), view_keys=view_keys, recipe_gate_version=self.gate_version,
                      opening_state=self.state, notify=lambda text, type="message", duration=5: self.notes.append((type, text)), proven=self.proven,
                      id_run_state=id_run_state)

    def run(self):
        with reactive.isolate():
            self.effects["_open_recipe"]()

    def current(self) -> dict:
        with reactive.isolate():
            return self.state.get()


def stores_during(action) -> list:
    from transformer import anchor
    written: list = []
    real = anchor.write_anchor

    def counting(lf, path, *args, **kwargs):
        written.append(Path(str(path)).name)
        return real(lf, path, *args, **kwargs)

    with mock.patch("app.modules.orchestrator.write_anchor", side_effect=counting):
        action()
    return sorted(written)


def test_the_first_opening_builds_draws_and_shows_a_progress_line_that_moves_and_goes(tmp_path, monkeypatch):
    """MUTATION H2: a progress that is never closed stays on the page."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    opening = Opening(world, monkeypatch)
    written = stores_during(opening.run)
    assert written == ["C.parquet", "C__T2.parquet", "C__T3_p_steps.parquet"]
    assert opening.drawn == ["p_steps", "p_plain"]
    assert opening.current()["status"] == "ready" and opening.notes == []
    (bar,) = FakeProgress.instances
    assert bar.messages[0] == "Opening 'tiny': tables 0 of 3, plots 0 of 2"
    assert bar.messages[-1] == "Opening 'tiny': tables 3 of 3, plots 2 of 2"
    assert bar.values == sorted(bar.values) and bar.values[0] == 0 and bar.values[-1] == 5 and bar.max == 5
    assert len(bar.messages) == 6 and bar.closed, "one call per item, then the line is closed: it goes"


def test_the_same_opening_again_does_nothing_at_all(tmp_path, monkeypatch):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    opening = Opening(world, monkeypatch)
    opening.run()
    FakeProgress.instances.clear()
    opening.drawn.clear()
    assert stores_during(opening.run) == [] and opening.drawn == [] and FakeProgress.instances == [], "no build, no drawing, no progress line"


def test_a_new_session_with_the_same_signature_reads_the_tables_and_does_not_draw_again(tmp_path, monkeypatch):
    """MUTATION H3: without the memory every session draws every plot again."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    memory = ProvenDrawings()
    Opening(world, monkeypatch, proven=memory).run()
    again = Opening(world, monkeypatch, proven=memory)
    assert stores_during(again.run) == [] and again.drawn == []
    assert again.current()["status"] == "ready"
    other_process = Opening(world, monkeypatch, proven=ProvenDrawings())
    other_process.run()
    assert other_process.drawn == ["p_steps", "p_plain"], "a restart proves again"


def test_a_changed_data_file_builds_and_draws_again(tmp_path, monkeypatch):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    opening = Opening(world, monkeypatch)
    opening.run()
    opening.drawn.clear()
    world.write_data("sample_id\tgroup\tscore\ns1\tA\t1\ns2\tA\t2\ns3\tB\t3\ns4\tB\t4\ns5\tB\t5\ns6\tB\t6\n")
    clear_data_analysis_recipe_cache()
    written = stores_during(opening.run)
    assert written == ["C.parquet", "C__T2.parquet", "C__T3_p_steps.parquet"] and opening.drawn == ["p_steps", "p_plain"]


def test_nothing_happens_in_another_workspace_for_a_recipe_home_cannot_open_or_when_the_keys_cannot_be_read(tmp_path, monkeypatch):
    world = Tier3World(tmp_path)
    for label, kwargs in (("blueprint", {"workspace": "Wrangle Studio"}), ("not available", {"available": ()})):
        opening = Opening(world, monkeypatch, **kwargs)
        assert stores_during(opening.run) == [] and opening.current() == {} and FakeProgress.instances == [], label
    unreadable = Opening(world, monkeypatch)
    unreadable.keys_error = RuntimeError("data cannot be read")
    assert stores_during(unreadable.run) == [] and unreadable.current() == {}, "the theater shows why; nothing is opened from it"


def test_the_waiting_rule_is_one_definition_for_the_theater_and_the_effect():
    sig = ("tiny", "a", "b")
    assert opening_waits({}, {"tiny": 1}, "tiny", sig)
    assert opening_waits({"signature": ("tiny", "a", "OTHER")}, {"tiny": 1}, "tiny", sig), "a state for other data does not release the theater"
    assert not opening_waits({"signature": sig, "status": "ready"}, {"tiny": 1}, "tiny", sig)
    assert not opening_waits({}, {}, "tiny", sig) and not opening_waits({}, {"tiny": 1}, None, sig), "a recipe HOME cannot open is not waited for"


def test_a_large_plot_is_warned_about_and_nothing_is_refused(tmp_path, monkeypatch):
    world = Tier3World(tmp_path, tier2=[], tier3=None)
    monkeypatch.setattr(opening_build, "LARGE_PLOT_ROWS", 2)     # the one constant
    opening = Opening(world, monkeypatch)
    opening.run()
    warnings = [text for kind, text in opening.notes if kind == "warning"]
    assert len(warnings) == 2 and "'p_steps'" in warnings[0] and "nothing is refused" in warnings[0]
    assert opening.current()["status"] == "ready" and opening.drawn == ["p_steps", "p_plain"]


def test_a_stop_of_the_opening_itself_is_told_and_home_goes_on(tmp_path, monkeypatch):
    world = Tier3World(tmp_path)
    opening = Opening(world, monkeypatch)
    monkeypatch.setattr(handlers, "run_opening", mock.Mock(side_effect=ValueError("a fault")))
    opening.run()
    assert opening.current()["status"] == "error" and any(kind == "error" and "a fault" in text for kind, text in opening.notes)


# ---------------------------------------------------------------------------------------------------------------------
# The refusal through the REAL load gate
# ---------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def gate(tmp_path, monkeypatch):
    """A real Bootloader whose recipes folder holds ONE recipe (`tiny`, 3 rows) that passes the gate, with a plot on a column the data does not have only
    when `break_plot()` is called."""
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE", "SPARMVET_CONNECTOR", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)
    root = tmp_path / "dep"
    locations = {}
    for key in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    (tmp_path / "dep.yaml").write_text(yaml.safe_dump({"deployment_type": "filesystem", "default_app_features": "qa",
                                                       "locations": locations, "data_lookup": "by_dataset_id", "branding": {"contact": "lab@example.org"}}))
    from app.tests.tiny_recipe import tiny_recipe, write_tiny
    data = root / "raw_data" / "A.tsv"
    data.write_text("a\nx\ny\nx\n")
    recipe = tiny_recipe("tiny")   # its path stays the one of the repository (the checker refuses an absolute path, PA01); `data_lookup: by_dataset_id` reads `A.tsv` of raw_data
    folder = root / "data_analysis_recipes"
    path = write_tiny(folder, recipe)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(tmp_path / "dep.yaml"))
    boot = Bootloader()

    def set_plot_column(column):
        recipe["analysis_groups"]["g"]["plots"]["p"]["mapping"] = {"x": column}
        write_tiny(folder, recipe)

    return SimpleNamespace(boot=boot, folder=folder, data=data, path=path, set_plot_column=set_plot_column, root=root)


def real_opening(gate_world, tmp_path, monkeypatch):
    """The effect over the real gate, with the real plot engine drawing."""
    from app.modules.orchestrator import DataOrchestrator
    FakeProgress.instances = []
    monkeypatch.setattr(handlers.ui, "Progress", FakeProgress)
    monkeypatch.setattr(handlers.ui, "insert_ui", lambda *a, **kw: None)   # the cover is the page's (its own test above)
    monkeypatch.setattr(handlers.ui, "remove_ui", lambda *a, **kw: None)
    effects = {}
    monkeypatch.setattr(reactive, "Effect", lambda fn: effects.setdefault(fn.__name__, fn) and fn)
    orchestrator = DataOrchestrator(gate_world.folder, gate_world.root / "raw_data", data_lookup="by_dataset_id")
    notes, state, version, shown = [], reactive.Value({}), reactive.Value(0), reactive.Value(None)
    define_server(mock.MagicMock(), mock.MagicMock(), mock.MagicMock(), bootloader=gate_world.boot, orchestrator=orchestrator, viz_factory=PlotEngines(),
                  safe_input=lambda i, k, d: {"sidebar_nav": "Home", "data_analysis_recipe_id": "tiny"}.get(k, d),
                  view_keys=lambda: orchestrator.compute_data_analysis_recipe_keys("tiny"), recipe_gate_version=version, opening_state=state,
                  notify=lambda text, type="message", duration=5: notes.append((type, text)), proven=ProvenDrawings(), shown_recipe=shown)

    def run():
        clear_data_analysis_recipe_cache()
        with reactive.isolate():
            effects["_open_recipe"]()
            return state.get(), version.get()
    run.shown = shown
    return run, notes


def test_a_recipe_whose_plots_all_draw_opens_and_stays_available(gate, tmp_path, monkeypatch):
    assert "tiny" in gate.boot.available_data_analysis_recipes
    run, notes = real_opening(gate, tmp_path, monkeypatch)
    state, version = run()
    assert state["status"] == "ready" and "tiny" in gate.boot.available_data_analysis_recipes and not gate.boot.rejected_data_analysis_recipes
    assert version == 0 and notes == []


def test_a_recipe_with_a_plot_that_cannot_be_drawn_is_refused_through_the_gate_with_a_plain_reason(gate, tmp_path, monkeypatch):
    """MUTATION H1: without `reject_after_opening` the recipe stays available."""
    gate.set_plot_column("no_such_column")
    gate.boot.recheck_changed_data_analysis_recipes()
    assert "tiny" in gate.boot.available_data_analysis_recipes, "the load gate passes it: the data check does not draw the plots"
    run, notes = real_opening(gate, tmp_path, monkeypatch)
    before = gate.boot.data_analysis_recipe_gate_version
    state, version = run()
    assert state["status"] == "refused"
    assert "tiny" not in gate.boot.available_data_analysis_recipes
    record = gate.boot.rejected_data_analysis_recipes["tiny"]
    assert record["when"] == "opening" and record["contact"] == "lab@example.org"
    assert len(record["problems"]) == 1 and "'p'" in record["problems"][0] and "no_such_column" in record["problems"][0]
    assert gate.boot.data_analysis_recipe_gate_version == before + 1 and version == before + 1, "the gate moved and the shared value with it"
    assert any(kind == "error" and "could not be opened" in text and "'p'" in text for kind, text in notes)
    text = rejected_recipe_text("tiny", record)
    assert "could not be opened" in text and "'p'" in text and "lab@example.org" in text and "after its files changed" not in text


def test_a_recipe_refused_on_the_first_screen_is_named_in_the_fall_back_notice(gate, tmp_path, monkeypatch):
    """The first screen: the selector value has not reached the server (`current` None) and nothing was remembered. The opening writes the recipe it opens into the
    shared `shown_recipe`, so the follower names it. MUTATION F1: an opening that does not write it leaves the notice empty (the recipe is switched silently)."""
    from app.handlers.recipe_gate_handlers import follow_step
    gate.set_plot_column("no_such_column")
    gate.boot.recheck_changed_data_analysis_recipes()
    run, _ = real_opening(gate, tmp_path, monkeypatch)
    with reactive.isolate():
        assert run.shown.get() is None, "first screen: nothing remembered yet"
    state, _ = run()
    assert state["status"] == "refused"
    with reactive.isolate():
        remembered = run.shown.get()
    assert remembered == "tiny"
    choices, selected, notice, announce = follow_step(["other"], None, remembered, None)
    assert (choices, selected, notice, announce) == (["other"], "other", ("tiny", "other"), True)


def test_a_refused_recipe_comes_back_when_its_files_change_and_is_refused_again_if_it_still_fails(gate, tmp_path, monkeypatch):
    gate.set_plot_column("no_such_column")
    gate.boot.recheck_changed_data_analysis_recipes()
    run, _ = real_opening(gate, tmp_path, monkeypatch)
    run()
    assert gate.boot.recheck_changed_data_analysis_recipes() == [], "nothing changed: it stays refused"
    gate.set_plot_column("other_missing_column")
    assert gate.boot.recheck_changed_data_analysis_recipes() == ["tiny"] and "tiny" in gate.boot.available_data_analysis_recipes
    state, _ = run()
    assert state["status"] == "refused" and "other_missing_column" in gate.boot.rejected_data_analysis_recipes["tiny"]["problems"][0]
    gate.set_plot_column("a")
    gate.boot.recheck_changed_data_analysis_recipes()
    state, _ = run()
    assert state["status"] == "ready" and "tiny" in gate.boot.available_data_analysis_recipes


def test_a_recipe_refused_for_its_data_comes_back_when_the_data_file_changes(gate, tmp_path, monkeypatch):
    """The data files are watched by size and modification time (never read by the poll): a fixed data file brings the recipe back to the gate."""
    gate.set_plot_column("no_such_column")
    gate.boot.recheck_changed_data_analysis_recipes()
    run, _ = real_opening(gate, tmp_path, monkeypatch)
    run()
    assert "tiny" in gate.boot.rejected_data_analysis_recipes
    assert gate.boot.recheck_changed_data_analysis_recipes() == []
    gate.data.write_text("a\nx\ny\nx\nz\n")
    assert gate.boot.recheck_changed_data_analysis_recipes() == ["tiny"], "the data file changed: the gate looks at the recipe again"
    assert "tiny" in gate.boot.available_data_analysis_recipes and "tiny" not in gate.boot.rejected_data_analysis_recipes


def test_reject_after_opening_ignores_a_name_that_is_not_a_recipe_and_replaces_the_dictionaries(gate):
    before_available, before_rejected = gate.boot.available_data_analysis_recipes, gate.boot.rejected_data_analysis_recipes
    gate.boot.reject_after_opening("no_such_recipe", ["x"])
    assert gate.boot.available_data_analysis_recipes is before_available and gate.boot.data_analysis_recipe_gate_version == 0
    gate.boot.reject_after_opening("tiny", ["problem one", "problem two"])
    assert before_available == {"tiny": str(gate.path)}, "other sessions that read the old dictionary are not changed under their hands"
    assert gate.boot.rejected_data_analysis_recipes is not before_rejected and gate.boot.rejected_data_analysis_recipes["tiny"]["problems"] == ["problem one", "problem two"]




def test_the_cover_is_sent_at_once_before_the_build_and_removed_after_the_flush(tmp_path, monkeypatch):
    """HOME-WALK A (D-0334): while the opening blocks the server the screen already says which recipe is opened (inserted `immediate`, before the progress line
    opens), and the cover is removed by a callback of the flush that sends the new theater, not by the effect (the old theater would show again for the rest of the flush).
    MUTATION A1: without the insert the screen keeps the previous recipe for the whole build; this fails."""
    opening = Opening(Tier3World(tmp_path), monkeypatch)
    opening.run()
    inserts = [c for c in opening.ui_calls if c[0] == "insert"]
    assert len(inserts) == 1 and inserts[0][1:4] == ("#dynamic_tabs", "beforeBegin", True), opening.ui_calls
    assert handlers.COVER_ID in inserts[0][4] and "tiny" in inserts[0][4]
    assert opening.ui_calls[0] == ("remove", f"#{handlers.COVER_ID}", True)   # never two covers: the one of an earlier opening goes first
    assert ("remove", f"#{handlers.COVER_ID}", True) not in opening.ui_calls[1:], "the effect itself does not remove the cover"
    (callback,), kwargs = opening.session.on_flushed.call_args
    assert kwargs == {"once": True}
    callback()
    assert opening.ui_calls[-1] == ("remove", f"#{handlers.COVER_ID}", True)


def test_no_cover_when_the_opening_is_already_done_or_not_for_this_workspace(tmp_path, monkeypatch):
    opening = Opening(Tier3World(tmp_path), monkeypatch)
    opening.run()
    opening.ui_calls.clear()
    opening.run()   # the same signature: nothing at all
    assert opening.ui_calls == []
    other = Opening(Tier3World(tmp_path / "other"), monkeypatch, workspace="Blueprint Architect")
    other.run()
    assert other.ui_calls == []
