"""A session written before the real value was kept gives the same rows in every view (ADR-104 point 7, Eve 2026-11-14).

`data/old_session_text_values.json` is a T3 ghost in the shape the panel wrote before the change: every value is text
(`"2000"`, `["2003", "2004"]`, `["True"]`), each step carries the `dtype` of its column, and no step has the choice `na`.
Restored today, the steps are read from their dtype: the HOME table, the results bundle, the plot and the re-run of the
exported recipe keep the same rows. No result changes; the old Boolean step, which kept no rows before (the text "True" was
compared with "true"), now keeps the rows it meant.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_old_session_typed_values.py -q
"""
import json
from pathlib import Path

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.handlers.export_handlers import audited_frame
from app.modules.t3_audit_engine import _apply_filter_rows, filter_rows_from_nodes
from blueprint_arch.t3_translator import build_mode2_recipe, translate_plot_steps
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from viz_factory.viz_factory import VizFactory

GHOST = json.loads((Path(__file__).parent / "data" / "old_session_text_values.json").read_text(encoding="utf-8"))
NODES = GHOST["t3_audit_steps_by_plot"]["subtab_samples_plot"]
FRAME = pl.DataFrame({
    "s": list("abcdefgh"), "n": list(range(1, 9)),
    "year": [1999, 2000, 2001, 2002, 2003, 2005, 2006, 2007],
    "weight": [80.0, 80.0, 91.0, 85.5, 85.0, 70.0, 60.0, 89.9],
    "country": ["NO", "NO", "NO", "SE", "SE", "DK", "NO", "SE"],
    "passed": [True, True, True, True, True, True, False, True],
})


def views(nodes):
    rows = filter_rows_from_nodes(nodes)
    lf = FRAME.lazy()
    for step in translate_plot_steps(nodes):
        lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
    recipe = {"plots": {"p": {"mapping": {"x": "s", "y": "n"}, "layers": [{"name": "geom_col", "params": {}}], "filters": rows}}}
    return {
        "home table": _apply_filter_rows(FRAME.lazy(), rows).collect()["s"].to_list(),
        "bundle": audited_frame(FRAME.lazy(), rows, []).collect()["s"].to_list(),
        "plot": VizFactory().render(FRAME.lazy(), recipe, "p").data["s"].to_list(),
        "re-run": lf.collect()["s"].to_list(),
    }


def test_the_old_session_really_holds_text_values_and_no_na():
    assert [type(n["params"]["value"]) for n in NODES] == [str, str, list, list, list]
    assert all("na" not in n["params"] for n in NODES)


def test_the_old_session_keeps_the_same_rows_in_every_view():
    assert views(NODES) == {k: ["b", "d", "h"] for k in ("home table", "bundle", "plot", "re-run")}


def test_the_steps_that_never_went_wrong_keep_exactly_the_rows_they_always_kept():
    """Without the Boolean step (which kept no rows before): the rows the engine of before the change returned."""
    assert views(NODES[:4]) == {k: ["b", "d", "g", "h"] for k in ("home table", "bundle", "plot", "re-run")}


def test_the_export_writes_the_values_typed_not_as_the_text_of_the_session():
    steps = translate_plot_steps(NODES)
    assert [s["value"] for s in steps] == [2000, 90.5, [2003, 2004], ["NO", "SE"], [True]]
    assert all(s["na"] == "remove" for s in steps)  # an old step removed the rows with no value


def test_the_exported_recipe_is_written_with_typed_values():
    raw = {"analysis_groups": {"g": {"plots": {"p": {"spec": {"target_dataset": "j"}}}}},
           "joins": {"j": {"ingredients": [{"dataset_id": "t"}], "steps": {"tier1": [], "tier2": []}}}}
    forked, _skipped = build_mode2_recipe(raw, {"p": NODES})[:2]
    written = [s["value"] for s in forked["joins"][next(k for k in forked["joins"] if k != "j")]["steps"]["tier2"]]
    assert written == [2000, 90.5, [2003, 2004], ["NO", "SE"], [True]]


def test_a_value_that_cannot_be_read_from_its_dtype_is_reported_never_guessed():
    from blueprint_arch.t3_translator import UntranslatableNode
    bad = [{"node_type": "filter_row", "params": {"column": "year", "op": "ge", "value": "last year", "dtype": "Int64"}}]
    with pytest.raises(UntranslatableNode) as exc:
        translate_plot_steps(bad)
    assert "'last year'" in str(exc.value) and "whole numbers" in str(exc.value)
    with pytest.raises(Exception) as home:
        _apply_filter_rows(FRAME.lazy(), filter_rows_from_nodes(bad))
    assert "'last year'" in str(home.value) and "whole numbers" in str(home.value)
