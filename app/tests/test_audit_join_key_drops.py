"""A column that is a join key cannot be dropped through the audit, at every place a drop can be made or can come in (D-0297).

The rule (`ui_implementation_contract.md` section 12g.2 and 12g.3): the key set is the union of every join key of any join step of the
recipe (`on`, `left_on`, `right_on`, and the `by` groups of an as-of join); a drop of a key is refused and the app says why; never silently.

Places where a drop is CREATED or ENTERS the app, and what each one does (the table of the report of this task):
  1. the column box of the data preview, "drop via audit" (`_col_drop_to_audit`)            refuses a key (these tests; also `test_home_join_keys.py`)
  2. the propagation dialog (`_handle_propagation_confirm`)                                  carries the steps of 1, creates none
  3. the audit panel's Apply (`audit_stack.handle_apply`)                                    carries the pending steps, creates none
  4. a RESTORED session (`session_handlers._restore_session`)                               refuses a stored key drop, restores the rest (these tests)
  5. an IMPORTED session zip, then restored                                                  the same as 4 (the zip is only unpacked)
  6. an imported reproducibility bundle                                                      holds no audit steps of the app: the audit is written into the frozen recipe by the export
  7. the export (`audited_frame`)                                                            applies the steps it is given; it is given the steps of the view

`test_only_one_place_creates_a_column_drop` fails when a seventh place that makes a `drop_column` step appears: a new place must
come here with its own test.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_join_key_drops.py -q

Mutation index (grep "MUTATION"; each seen failing, `tmpAI/breakonce_keys.py`, 7 of 7):
  MUTATION K1  `split_key_drops` keeps a key drop
  MUTATION K2  `_restore_session` does not call `split_key_drops` (this is the state before the repair: the key is dropped, nothing is said)
  MUTATION K3  `_restore_session` restores nothing when one step is refused
  MUTATION K4  `_col_drop_to_audit` does not refuse a key
  MUTATION K5  `extract_primary_keys` does not read the right-hand names of a join (`right_on`)
  MUTATION K6  a second place that creates a `drop_column` step
  MUTATION K7  the notice leaves out the reason the user wrote
"""
import ast
import asyncio
import io
import zipfile
from pathlib import Path
from types import SimpleNamespace

import polars as pl
import pytest
from shiny import reactive, render, ui
from shiny.types import SilentException

import app.handlers.session_handlers as session_handlers
from app.handlers import filter_and_audit_handlers as handlers
from app.modules.session_manager import SessionManager, extract_primary_keys, make_audit_step, split_key_drops
from app.modules.t3_audit_engine import audited_frame

APP = Path(handlers.__file__).resolve().parents[1]


def join(**keys):
    return {"action": "polars_join", "right_ingredient": "R", "how": "left", **keys}


def recipe(*steps, tier2=()):
    """The part of a recipe `extract_primary_keys` reads: one join with its tier-1 steps and its tier-2 steps."""
    return {"joins": {"J": {"tier1": {"steps": list(steps)}, "tier2": {"steps": list(tier2)}}}}


def drop_step(column, plot="subtab_p1", reason="", step_id=None):
    return make_audit_step("drop_column", {"column": column}, plot_scope=plot, reason=reason, node_id=step_id)


def filter_step(column, plot="subtab_p1"):
    return make_audit_step("filter_row", {"column": column, "op": "eq", "value": 1, "dtype": "Int64"}, plot_scope=plot, reason="r")


# ---------------------------------------------------------------------------------------------------- which columns are keys

def test_a_join_on_two_columns_makes_both_keys():
    assert extract_primary_keys(recipe(join(**{"on": ["sample_id", "gene"]}))) == ["gene", "sample_id"]


def test_a_join_with_two_names_makes_both_names_keys():
    """`left_on` and `right_on` with different names: the key set is the union of both (section 12g.2), so a column that only the
    right table has under that name, and the column of the left table, are keys. MUTATION K5 fails here."""
    assert extract_primary_keys(recipe(join(left_on=["VF_gene"], right_on=["Gene_name"]))) == ["Gene_name", "VF_gene"]


def test_the_keys_of_every_step_and_of_the_second_tier_are_one_union():
    steps = recipe(join(**{"on": "sample_id"}), join(left_on="a", right_on="b"), tier2=[join(**{"on": ["c"]})])
    assert extract_primary_keys(steps) == ["a", "b", "c", "sample_id"]


def test_the_by_groups_of_an_as_of_join_are_keys():
    asof = {"action": "polars_join_asof", "right_ingredient": "R", "on": "time", "by": ["sample_id"]}
    assert extract_primary_keys(recipe(asof)) == ["sample_id", "time"]


def test_a_column_of_a_step_that_is_not_a_join_is_not_a_key():
    group = {"action": "polars_group_by", "by": ["species"], "on": ["x"]}
    assert extract_primary_keys(recipe(join(**{"on": "sample_id"}), group)) == ["sample_id"]


def test_a_recipe_without_joins_has_no_keys():
    assert extract_primary_keys({}) == []
    assert extract_primary_keys({"joins": {}}) == []


# ---------------------------------------------------------------------------------------------- place 1: the column box

class Val:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


SOURCE = Path(handlers.__file__)


def closure(name: str, source: Path = SOURCE, outer: str = "define_filter_audit_server", **stand_ins):
    ns = dict(vars(handlers))
    define = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == outer)
    fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == name)
    fn.decorator_list = []
    ns.update(stand_ins)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)
    return ns[name]


class Box:
    """What `_col_drop_to_audit` needs from the app."""

    def __init__(self, keys, columns):
        self.notes, self.opened = [], []
        self.scratch = Val()
        self.state = Val({"primary_keys": keys, "active_plot_subtab": "subtab_p1"})
        self.frame = pl.DataFrame({c: ["x"] for c in columns})

    def drop(self, kept):
        closure(
            "_col_drop_to_audit",
            bootloader=SimpleNamespace(is_enabled=lambda flag: True), home_state=self.state, _can_write_audit_step=lambda: True,
            active_home_subtab=Val("subtab_p1"),
            _notify=lambda message, **kw: self.notes.append((message, kw.get("type"))),
            _propagation_scratch=self.scratch,
            _open_propagation_modal=lambda nodes, subtab, kind: self.opened.append((nodes, kind)),
            _resolve_active_spec=lambda p_id: {}, _resolve_active_lf=lambda spec, tier=None: self.frame.lazy(),
            _t3_drop_columns=lambda: [], safe_input=lambda i, k, d=None: i.get(k, d), input={"preview_col_selector": kept},
            ui=SimpleNamespace(update_selectize=lambda *a, **k: None),
        )()


COLUMNS = ["sample_id", "gene", "VF_gene", "Gene_name", "year", "source"]
COMPOSITE = extract_primary_keys(recipe(join(**{"on": ["sample_id", "gene"]})))
TWO_NAMES = extract_primary_keys(recipe(join(left_on=["VF_gene"], right_on=["Gene_name"])))


@pytest.mark.parametrize("dropped", ["sample_id", "gene"])
def test_with_a_two_column_key_dropping_either_column_is_refused(dropped):
    """MUTATION K4 fails here."""
    box = Box(COMPOSITE, COLUMNS)
    box.drop(kept=[c for c in COLUMNS if c != dropped])
    assert box.opened == [] and box.scratch.get() is None
    assert [t for _, t in box.notes] == ["error"]
    assert f"Cannot drop join key column(s): {dropped}" in box.notes[0][0]
    assert "row filter or row exclusion" in box.notes[0][0]


@pytest.mark.parametrize("dropped", ["VF_gene", "Gene_name"])
def test_with_two_names_for_the_key_each_name_is_refused(dropped):
    box = Box(TWO_NAMES, COLUMNS)
    box.drop(kept=[c for c in COLUMNS if c != dropped])
    assert box.opened == [] and f"Cannot drop join key column(s): {dropped}" in box.notes[0][0]


def test_a_column_next_to_a_composite_key_is_still_dropped_through_the_dialog():
    box = Box(COMPOSITE, COLUMNS)
    box.drop(kept=[c for c in COLUMNS if c != "year"])
    assert box.notes == []
    (nodes, kind), = box.opened
    assert kind == "drop" and [n["params"]["column"] for n in nodes] == ["year"]
    assert [n["node_type"] for n in nodes] == ["drop_column"]


def test_several_columns_at_once_with_one_key_among_them_refuse_the_whole_drop():
    """What the code does today (reported, not changed): one key among the deselected columns refuses ALL of them, the message
    names only the key, and the non-key columns of the same click are NOT sent to the dialog either."""
    box = Box(COMPOSITE, COLUMNS)
    box.drop(kept=[c for c in COLUMNS if c not in ("sample_id", "year", "source")])
    assert box.opened == [] and box.scratch.get() is None
    assert len(box.notes) == 1 and box.notes[0][1] == "error"
    assert "Cannot drop join key column(s): sample_id." in box.notes[0][0]
    assert "year" not in box.notes[0][0] and "source" not in box.notes[0][0]


def test_several_non_key_columns_at_once_go_to_the_dialog():
    box = Box(COMPOSITE, COLUMNS)
    box.drop(kept=["sample_id", "gene", "VF_gene", "Gene_name"])
    (nodes, kind), = box.opened
    assert [n["params"]["column"] for n in nodes] == ["year", "source"]


def test_a_filter_on_either_column_of_a_two_name_key_carries_the_warning():
    state = Val({"primary_keys": TWO_NAMES, "active_plot_subtab": "subtab_p1"})
    for column, expected in (("VF_gene", True), ("Gene_name", True), ("year", False)):
        opened, notes = [], []
        closure(
            "_filter_send_to_audit",
            bootloader=SimpleNamespace(is_enabled=lambda flag: True), home_state=state, _can_write_audit_step=lambda: True,
            _pending_filters=Val([{"column": column, "op": "eq", "value": "x", "dtype": "String", "na": "remove"}]),
            active_home_subtab=Val("subtab_p1"), _notify=lambda message, **kw: notes.append(message),
            _propagation_scratch=Val(), _open_propagation_modal=lambda nodes, subtab, kind: opened.append(nodes),
            _clear_exploration_filters=lambda: None, audit_params_from_row=lambda row: {"column": row["column"], "op": row["op"], "value": row["value"]},
        )()
        (nodes,) = opened
        assert nodes[0]["node_type"] == "filter_row" and bool(nodes[0].get("primary_key_warning")) is expected, column


# ------------------------------------------------------------------------------------------------ place 2 to 3: they only carry

def test_the_dialog_carries_the_non_key_drop_into_the_pending_steps_of_the_chosen_plots():
    """Place 2: the steps created by the column box go on as they are. A non-key drop works all the way to the pending list."""
    box = Box(COMPOSITE, COLUMNS)
    box.drop(kept=[c for c in COLUMNS if c != "year"])
    (nodes, _), = box.opened
    state = Val({"active_plot_subtab": "subtab_p1", "_pending_t3_nodes": []})
    notes = []
    closure(
        "_handle_propagation_confirm",
        home_state=state, _propagation_scratch=Val({"nodes": nodes, "kind": "drop"}),
        safe_input=lambda i, k, d=None: {"propagation_choice": "all"}.get(k, d), input={},
        active_home_subtab=Val("subtab_p1"), _all_plot_subtab_ids=lambda: ["subtab_p1", "subtab_p2"],
        _plot_has_column=lambda plot, column: True, _plot_label=lambda s: s,
        _notify=lambda message, **kw: notes.append(message), ui=SimpleNamespace(modal_remove=lambda: None),
    )()
    pending = state.get()["_pending_t3_nodes"]
    assert sorted((n["plot_scope"], n["node_type"], n["params"]["column"]) for n in pending) == [
        ("subtab_p1", "drop_column", "year"), ("subtab_p2", "drop_column", "year")]
    assert len({n["id"] for n in pending}) == 1, "the copies of one decision share one id"


def test_only_one_place_creates_a_column_drop():
    """The five places that could create a `drop_column` step were read; one does. A new place fails this test, so that it comes with
    its own refusal and its own test. A step is created by `make_audit_step("drop_column", ...)` or by a dict with that node type."""
    class Finder(ast.NodeVisitor):
        """Collects the innermost function around each place that makes a drop step."""

        def __init__(self, name):
            self.name, self.stack, self.found = name, [], []

        def visit_FunctionDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            if (getattr(node.func, "id", getattr(node.func, "attr", "")) == "make_audit_step"
                    and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "drop_column"):
                self.found.append((self.name, self.stack[-1] if self.stack else "<module>"))
            self.generic_visit(node)

        def visit_Dict(self, node):
            if any(isinstance(k, ast.Constant) and k.value == "node_type" and isinstance(v, ast.Constant) and v.value == "drop_column"
                   for k, v in zip(node.keys, node.values)):
                self.found.append((self.name, self.stack[-1] if self.stack else "<module>"))
            self.generic_visit(node)

    sites = []
    for path in sorted((APP / "handlers").glob("*.py")) + sorted((APP / "modules").glob("*.py")) + sorted((APP / "src").glob("*.py")):
        finder = Finder(path.name)
        finder.visit(ast.parse(path.read_text()))
        sites += finder.found
    assert sorted(set(sites)) == [("filter_and_audit_handlers.py", "_col_drop_to_audit")], sites


# --------------------------------------------------------------------------------------------- the pure split used by Restore

def test_split_removes_only_the_key_drops_and_keeps_the_order_of_the_rest():
    """MUTATION K1 fails here."""
    by_plot = {
        "subtab_p1": [filter_step("year"), drop_step("sample_id", reason="old"), drop_step("source"), filter_step("sample_id")],
        "subtab_p2": [drop_step("gene", plot="subtab_p2")],
    }
    kept, refused = split_key_drops(by_plot, ["sample_id", "gene"])
    assert [(n["node_type"], n["params"]["column"]) for n in kept["subtab_p1"]] == [
        ("filter_row", "year"), ("drop_column", "source"), ("filter_row", "sample_id")]
    assert kept["subtab_p2"] == []
    assert [(r["plot"], r["column"], r["reason"]) for r in refused] == [("subtab_p1", "sample_id", "old"), ("subtab_p2", "gene", "")]


def test_split_does_not_change_its_argument_and_a_non_key_drop_stays():
    by_plot = {"subtab_p1": [drop_step("sample_id"), drop_step("year")]}
    before = [dict(n) for n in by_plot["subtab_p1"]]
    kept, refused = split_key_drops(by_plot, ["sample_id"])
    assert by_plot["subtab_p1"] == before
    assert [n["params"]["column"] for n in kept["subtab_p1"]] == ["year"] and len(refused) == 1


def test_split_with_no_keys_or_no_steps_refuses_nothing():
    by_plot = {"subtab_p1": [drop_step("sample_id")], "subtab_p2": []}
    assert split_key_drops(by_plot, []) == (by_plot, [])
    assert split_key_drops(by_plot, None)[1] == []
    assert split_key_drops({}, ["sample_id"]) == ({}, [])
    assert split_key_drops(None, ["sample_id"]) == ({}, [])


def test_split_lists_every_copy_of_a_propagated_step_and_keeps_a_style_step():
    style = make_audit_step("aesthetic_override", {"alpha": 0.5}, plot_scope="subtab_p1")
    by_plot = {"subtab_p1": [style, drop_step("sample_id", step_id="same")], "subtab_p2": [drop_step("sample_id", plot="subtab_p2", step_id="same")]}
    kept, refused = split_key_drops(by_plot, ["sample_id"])
    assert kept["subtab_p1"] == [style]
    assert [(r["plot"], r["id"]) for r in refused] == [("subtab_p1", "same"), ("subtab_p2", "same")]


def test_split_refuses_a_switched_off_key_drop_too():
    off = {**drop_step("sample_id"), "active": False}
    assert split_key_drops({"subtab_p1": [off]}, ["sample_id"])[1][0]["column"] == "sample_id"


# ------------------------------------------------------------------------ places 4 and 5: the real session screen, real files

KEY = "aaaaaaaaaaaa:bbbbbbbbbbbb"
SAFE = KEY.replace(":", "_")
LIMIT = 40


class LiveInput:
    MISSING = object()

    def __init__(self):
        self.values = {}

    def _value(self, name):
        return self.values.setdefault(name, reactive.Value(self.MISSING))

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)

        def read():
            value = self._value(name).get()
            if value is self.MISSING:
                raise SilentException()
            return value
        return read

    def set(self, name, value):
        self._value(name).set(value)


class Screen:
    """The real `define_session_server` over a real `SessionManager` folder; the notifications are collected."""

    def __init__(self, tmp_path, monkeypatch, keys, name="user"):
        self.notes, self.effects = [], []
        real_effect = reactive.Effect

        def effect(fn):
            made = real_effect(fn)
            self.effects.append(made)
            return made

        def shown(message, **kw):
            self.notes.append((kw.get("type"), str(message)))
            if len(self.notes) > LIMIT:
                for made in self.effects:
                    made.destroy()
        monkeypatch.setattr(reactive, "Effect", effect)
        monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
        monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(ui, "notification_show", shown)
        monkeypatch.setattr(ui, "modal_show", lambda *a, **k: None)
        monkeypatch.setattr(ui, "modal_remove", lambda *a, **k: None)
        monkeypatch.setattr(session_handlers, "bootloader", SimpleNamespace(is_enabled=lambda flag: True))
        self.manager = SessionManager(tmp_path / name)
        self.input = LiveInput()
        for n in ("session_import_upload", "session_delete_all_btn", "session_delete_all_confirm"):
            self.input.set(n, None)
        self.home_state = reactive.Value({"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64, "primary_keys": keys})
        self.log, self.issues = reactive.Value([]), reactive.Value([])
        session_handlers.define_session_server(
            self.input, lambda fn: fn, SimpleNamespace(on_flushed=lambda fn, once=True: fn()), session_manager=self.manager,
            current_app_features=None, home_state=self.home_state, notification_log=self.log, session_processing_issues=self.issues,
            safe_input=lambda i, k, d: "tiny" if k == "data_analysis_recipe_id" else d)

    def write(self, by_plot):
        self.manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
        self.manager.write_t3_ghost(KEY, "tiny", "a" * 64, "b" * 64, t3_audit_steps_by_plot=by_plot)

    def texts(self, word):
        return [m for _, m in self.notes if word in m]

    def state(self):
        with reactive.isolate():
            return self.home_state.get()

    async def restore(self):
        for _ in range(3):
            await reactive.flush()
        self.input.set(f"session_restore_{SAFE}", 1)
        for _ in range(6):
            await reactive.flush()


SAVED = {
    "subtab_p1": [filter_step("year"), drop_step("sample_id", reason="not needed", step_id="k1"), drop_step("source", reason="noise", step_id="n1")],
    "subtab_p2": [drop_step("sample_id", plot="subtab_p2", reason="not needed", step_id="k1")],
}


def steps_of(state):
    return {plot: [(n["node_type"], n["params"].get("column")) for n in nodes] for plot, nodes in state["t3_audit_steps_by_plot"].items()}


def test_a_restored_session_with_a_key_drop_restores_the_rest_and_tells_which_step_and_why(tmp_path, monkeypatch):
    """MUTATION K2 and MUTATION K3 fail here."""
    async def scenario():
        s = Screen(tmp_path, monkeypatch, keys=["sample_id"])
        s.write(SAVED)
        await s.restore()
        assert steps_of(s.state()) == {"subtab_p1": [("filter_row", "year"), ("drop_column", "source")], "subtab_p2": []}
        told = s.texts("join key")
        assert len(told) == 1, s.notes
        assert "sample_id" in told[0] and "subtab_p1" in told[0] and "subtab_p2" in told[0]
        assert "not needed" in told[0], "the reason the user wrote is in the message"
        assert "row filter or row exclusion" in told[0]
        assert any(t == "warning" for t, m in s.notes if "join key" in m)
        assert len(s.texts("Session restored")) == 1, "the rest of the session is restored, with its own notice"
    asyncio.run(scenario())


def test_a_restored_session_without_a_key_drop_says_nothing_about_keys(tmp_path, monkeypatch):
    async def scenario():
        s = Screen(tmp_path, monkeypatch, keys=["sample_id"])
        s.write({"subtab_p1": [filter_step("sample_id"), drop_step("source", reason="noise")]})
        await s.restore()
        assert steps_of(s.state())["subtab_p1"] == [("filter_row", "sample_id"), ("drop_column", "source")]
        assert s.texts("join key") == []
    asyncio.run(scenario())


def test_a_restore_when_the_recipe_has_no_known_join_key_applies_the_steps_as_saved(tmp_path, monkeypatch):
    """No key known (a recipe without joins, or the keys not read yet): nothing can be called a key, so nothing is refused. The user
    is not told either, because there is nothing to tell: pinned so that a change of this is a decision."""
    async def scenario():
        s = Screen(tmp_path, monkeypatch, keys=[])
        s.write(SAVED)
        await s.restore()
        assert ("drop_column", "sample_id") in steps_of(s.state())["subtab_p1"]
        assert s.texts("join key") == []
    asyncio.run(scenario())


def test_an_imported_session_zip_with_a_key_drop_is_restored_the_same_way(tmp_path, monkeypatch):
    """Place 5: another machine's session zip is unpacked as it is, then restored by the same screen."""
    async def scenario():
        source = Screen(tmp_path, monkeypatch, keys=[], name="other_machine")
        source.write(SAVED)
        zip_bytes = source.manager.export_session_zip(KEY)
        target = Screen(tmp_path, monkeypatch, keys=["sample_id"], name="this_machine")
        assert target.manager.import_session_zip(zip_bytes) == KEY
        assert any(n["node_type"] == "drop_column" and n["params"]["column"] == "sample_id"
                   for n in target.manager.list_t3_ghosts(KEY)[0]["t3_audit_steps_by_plot"]["subtab_p1"]), "the import itself keeps the file as it is"
        await target.restore()
        assert steps_of(target.state()) == {"subtab_p1": [("filter_row", "year"), ("drop_column", "source")], "subtab_p2": []}
        assert len(target.texts("join key")) == 1
    asyncio.run(scenario())


def test_restore_does_not_change_the_saved_file(tmp_path, monkeypatch):
    """The refusal is in the view: the saved file is left as it is (the user can still read what was saved); the next save writes the view."""
    async def scenario():
        s = Screen(tmp_path, monkeypatch, keys=["sample_id"])
        s.write(SAVED)
        before = sorted(p.read_bytes() for p in (tmp_path / "user").rglob("t3_*.json"))
        await s.restore()
        assert sorted(p.read_bytes() for p in (tmp_path / "user").rglob("t3_*.json")) == before
    asyncio.run(scenario())


# --------------------------------------------------------------------------------------------- place 7: the export and the view

def test_the_export_and_the_view_apply_the_steps_they_are_given_a_key_drop_that_reached_them_would_be_applied():
    """Pins today's behaviour (a decision for Eve, see the report): `audited_frame` does not know the join keys; it drops what the
    list says. After the repair a key drop cannot reach the list (the column box and Restore refuse it), so the list never holds one.
    A defence inside `audited_frame` would need the keys as an argument of every caller."""
    lf = pl.DataFrame({"sample_id": ["a"], "year": [1]}).lazy()
    assert audited_frame(lf, [drop_step("sample_id")], "p1").collect_schema().names() == ["year"]
    assert audited_frame(lf, [drop_step("year")], "p1").collect_schema().names() == ["sample_id"]
