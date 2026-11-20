"""HOME and the join keys of the recipe (step 4b made this alive; D-0250).

`extract_primary_keys` reads the keys of every join step of `joins.*.tier1.steps` and `tier2.steps`. On dev it read a place that no
recipe had, so it always gave `[]` and nothing was ever refused. Now, for the demo recipe, it gives `Gene_name`, `VF_gene` and
`sample_id`, and HOME uses them (`home_state["primary_keys"]`):

- "Send to audit" of a column drop that names a join key is REFUSED with the message "Cannot drop join key column(s): ...";
  a column that is not a key still goes to the propagation dialog (so the refusal is by key, not for every drop);
- a filter on a join key is ALLOWED; the audit step it makes carries `primary_key_warning=True` (the yellow banner in the dialog and
  the audit panel, a marker in the report); a filter on another column does not carry it.

The closures `_col_drop_to_audit` and `_filter_send_to_audit` of `define_filter_audit_server` are cut out by `ast` and run with
stand-ins for the session (as in `test_blueprint_tier_files.py`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_join_keys.py -q
"""
import pytest
import ast
from pathlib import Path
from types import SimpleNamespace

import polars as pl

from app.handlers import filter_and_audit_handlers as handlers
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.session_manager import extract_primary_keys

SOURCE = Path(handlers.__file__)
DEMO = Path(__file__).resolve().parents[2] / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"


class Val:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def closure(name: str, **stand_ins):
    ns = dict(vars(handlers))
    define = next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "define_filter_audit_server")
    fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == name)
    fn.decorator_list = []
    ns.update(stand_ins)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)
    return ns[name]


def demo_keys() -> list:
    return extract_primary_keys(load_data_analysis_recipe(DEMO).config.raw_config)


def test_the_demo_recipe_gives_its_join_keys():
    assert demo_keys() == ["Gene_name", "VF_gene", "sample_id"]


class Session:
    """What the two handlers need from the app: notifications, the propagation dialog and the scratch they fill."""

    def __init__(self, keys, frame):
        self.notes, self.opened = [], []
        self.scratch = Val()
        self.state = Val({"primary_keys": keys, "active_plot_subtab": "subtab_p1"})
        self.frame = frame

    def stand_ins(self, **extra):
        base = dict(
            bootloader=SimpleNamespace(is_enabled=lambda flag: True),
            home_state=self.state, active_home_subtab=Val("subtab_p1"),
            _notify=lambda message, **kw: self.notes.append((message, kw.get("type"))),
            _propagation_scratch=self.scratch,
            _open_propagation_modal=lambda nodes, subtab, kind: self.opened.append((nodes, kind)),
            _clear_exploration_filters=lambda: (0, 0),
            _can_write_audit_step=lambda: True,
            _resolve_active_spec=lambda p_id: {}, _resolve_active_lf=lambda spec, tier=None: (self.frame.lazy() if tier == "T3" else pytest.fail(f"read tier {tier!r}, not T3: an audit step is written at the plot's table")),
            _t3_drop_columns=lambda: [], safe_input=lambda i, k, d=None: i.get(k, d),
            input={},
            ui=SimpleNamespace(update_selectize=lambda *a, **k: None, update_text=lambda *a, **k: None),   # no live session here
        )
        base.update(extra)
        return base


FRAME = pl.DataFrame({"sample_id": ["a"], "Gene_name": ["g"], "VF_gene": ["v"], "year": [2024], "source": ["x"]})


def drop(session, kept):
    session.state.set(dict(session.state.get()))
    stand = session.stand_ins(input={"preview_col_selector": kept})
    closure("_col_drop_to_audit", **stand)()


def test_dropping_a_join_key_column_is_refused_with_the_message_and_nothing_is_sent():
    s = Session(demo_keys(), FRAME)
    drop(s, kept=["Gene_name", "VF_gene", "year", "source"])      # `sample_id` is deselected
    assert s.opened == [] and s.scratch.get() is None
    assert len(s.notes) == 1 and s.notes[0][1] == "error"
    assert "Cannot drop join key column(s): sample_id" in s.notes[0][0]
    assert "row filter or row exclusion" in s.notes[0][0]


def test_every_deselected_key_is_named_in_the_refusal():
    s = Session(demo_keys(), FRAME)
    drop(s, kept=["year", "source"])
    assert "Cannot drop join key column(s): sample_id, Gene_name, VF_gene" in s.notes[0][0]


def test_dropping_a_column_that_is_not_a_key_goes_to_the_dialog():
    s = Session(demo_keys(), FRAME)
    drop(s, kept=["sample_id", "Gene_name", "VF_gene", "source"])   # `year` is deselected
    assert s.notes == []
    (nodes, kind), = s.opened
    assert kind == "drop" and [n["params"]["column"] for n in nodes] == ["year"]


def test_with_no_join_keys_nothing_is_refused_the_state_before_step_4b():
    """On dev `extract_primary_keys` gave [] for every recipe, so even `sample_id` was dropped without a word."""
    s = Session([], FRAME)
    drop(s, kept=["Gene_name", "VF_gene", "year", "source"])
    assert s.notes == [] and len(s.opened) == 1


def send_filters(session, rows):
    pending = Val(rows)
    closure("_filter_send_to_audit", **session.stand_ins(_pending_filters=pending))()


def test_a_filter_on_a_join_key_is_allowed_and_its_audit_step_carries_the_warning():
    s = Session(demo_keys(), FRAME)
    send_filters(s, [{"column": "sample_id", "op": "eq", "value": "a", "dtype": "String"}])
    assert s.notes == []
    (nodes, kind), = s.opened
    assert kind == "filter" and len(nodes) == 1
    assert nodes[0]["node_type"] == "filter_row"                 # kept as a filter, not turned into an exclusion (AUDIT-1)
    assert nodes[0].get("primary_key_warning") is True
    assert nodes[0]["params"]["column"] == "sample_id" and nodes[0]["params"]["op"] == "eq"


def test_a_filter_on_another_column_carries_no_warning_and_a_mixed_send_marks_only_the_key():
    s = Session(demo_keys(), FRAME)
    send_filters(s, [{"column": "year", "op": "gt", "value": 2020, "dtype": "Int64"},
                     {"column": "VF_gene", "op": "ne", "value": "z", "dtype": "String"}])
    (nodes, _), = s.opened
    assert [(n["params"]["column"], n.get("primary_key_warning", False)) for n in nodes] == [("year", False), ("VF_gene", True)]
