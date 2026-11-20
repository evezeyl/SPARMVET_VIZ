"""HOME and the join keys of the recipe (step 4b made this alive; D-0250).

`extract_primary_keys` reads the keys of every join step of `joins.*.tier1.steps` and `tier2.steps`. On dev it read a place that no
recipe had, so it always gave `[]` and nothing was ever refused. Now, for the demo recipe, it gives `Gene_name`, `VF_gene` and
`sample_id`, and HOME uses them (`home_state["primary_keys"]`):

- a column drop is written in the plot's own steps (the place `T3:<plot>`), after every join, so a join key dropped there is NOT refused any more: the refusal is by PLACE
  (D-0358, which modulates D-0297; the rule is `utils.key_drop`, its tests `libs/utils/tests/test_key_drop.py`), the handler asks it with the place it has (ADAPTED: before, a key
  was refused by its name with "Cannot drop join key column(s): ...");
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
from utils import key_drop

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


def demo_raw() -> dict:
    return load_data_analysis_recipe(DEMO).config.raw_config


def demo_keys() -> list:
    return extract_primary_keys(demo_raw())


DEMO_PLOT = "mlst_bar"      # a plot of the demo recipe: the subtab of the session below is `subtab_mlst_bar`


def test_the_demo_recipe_gives_its_join_keys():
    assert demo_keys() == ["Gene_name", "VF_gene", "sample_id"]


class Session:
    """What the two handlers need from the app: notifications, the propagation dialog and the scratch they fill."""

    def __init__(self, keys, frame, raw=None, plans=None):
        self.notes, self.opened = [], []
        self.plans = plans
        self.scratch = Val()
        self.raw = raw
        self.state = Val({"primary_keys": keys, "active_plot_subtab": f"subtab_{DEMO_PLOT}"})
        self.frame = frame

    def stand_ins(self, **extra):
        base = dict(
            bootloader=SimpleNamespace(is_enabled=lambda flag: True),
            home_state=self.state, active_home_subtab=Val(f"subtab_{DEMO_PLOT}"), recipe_raw=(lambda: self.raw) if self.raw is not None else None, recipe_plans=lambda: self.plans,
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


def test_dropping_a_join_key_column_in_a_plots_own_steps_goes_to_the_dialog():
    """ADAPTED (D-0358): the demo recipe joins on `sample_id`; the drop is at `T3:mlst_bar`, after every join, so nothing is refused (before: refused by name)."""
    s = Session(demo_keys(), FRAME, demo_raw())
    drop(s, kept=["Gene_name", "VF_gene", "year", "source"])      # `sample_id` is deselected
    assert s.notes == []
    (nodes, kind), = s.opened
    assert kind == "drop" and [n["params"]["column"] for n in nodes] == ["sample_id"]


def test_the_handler_asks_the_rule_with_the_place_of_the_open_plot_and_follows_its_refusal(monkeypatch):
    """MUTATION K4 fails here: the real rule refuses nothing at a plot, so a stand-in answer proves the handler asks `T3:<open plot>` for the deselected columns and obeys."""
    asked = []

    def answer(self, place, columns):
        asked.append((place, list(columns)))
        return "STAND-IN refusal"
    monkeypatch.setattr(key_drop.DropGate, "problem", answer)
    s = Session(demo_keys(), FRAME, demo_raw())
    drop(s, kept=["year", "source"])
    assert asked == [(f"T3:{DEMO_PLOT}", ["sample_id", "Gene_name", "VF_gene"])]
    assert s.opened == [] and s.scratch.get() is None and s.notes == [("⛔ STAND-IN refusal", "error")]


def test_dropping_a_column_that_is_not_a_key_goes_to_the_dialog():
    s = Session(demo_keys(), FRAME, demo_raw())
    drop(s, kept=["sample_id", "Gene_name", "VF_gene", "source"])   # `year` is deselected
    assert s.notes == []
    (nodes, kind), = s.opened
    assert kind == "drop" and [n["params"]["column"] for n in nodes] == ["year"]


def test_with_no_recipe_nothing_is_judged_and_the_drop_goes_to_the_dialog():
    """Without an open recipe (`recipe_raw` absent) the handler cannot ask the rule: nothing is refused, as on dev before the join keys were read."""
    s = Session([], FRAME, None)
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
