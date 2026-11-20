"""Every reader of a tier's steps that is not the engine sees the audit steps (D-0332, piece C-1, reviewer's point 1).

`app/tests/test_tier_steps_one_reader.py` counts the calls of the helper per file; these tests prove the BEHAVIOUR of each reader with an audit step at the place
it reads, so a reader that is switched to the author's steps alone (`author_steps`) fails here. Each was seen failing once with that switch (see the report).

- the engine record (`engine_record.py:42`, `:78`) lists the tier 2 and the tier 3 whose only steps are audit steps;
- the join keys of HOME (`session_manager.extract_primary_keys`, l.143) read the steps a join runs: a join step in `audit_steps` is read (an audit never adds one; the test uses
  a hand-made one only to tell the two readers apart);
- the badge (`view_badge.has_tier2_steps` / `has_plot_steps`, l.51 and l.58) says "has steps" when only audit steps exist;
- the run of an audit copy (`audit_run.py`, l.154 and l.170) builds the tier 2 of a table whose only tier-2 step is an audit step: `test_audit_run.py::
  test_the_run_reads_the_audit_steps_of_tier_2_of_a_table_that_has_none_of_its_own`.
- NOT reachable headless: `app/handlers/audit_stack.py:326` is inside a `@render.ui` of `define_server` (it needs a Shiny session). It reads `tier2_steps(cfg.raw_config, ...)` of the
  ACTIVE recipe, which HOME opens from the recipe file, an original with no audit list, so the audit steps are not there to be seen yet; the name test counts its call.
- Blueprint's writer refuses a file that holds audit steps (it would drop the list).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_readers_see_audit_steps.py -q
"""
import ast
from pathlib import Path

import pytest
import yaml

from app.handlers import blueprint_handlers
from app.modules.engine_record import NOT_RUN, engine_record
from app.modules.session_manager import extract_primary_keys
from app.modules.view_badge import has_plot_steps, has_tier2_steps
from app.tests.test_blueprint_failed_load import _closure
from utils.recipe_tiers import AUDIT_STEPS

AUDIT_FILTER = {"action": "modif_filter", "column": "v", "op": "gt", "value": 1, "na": "keep", "id": "audit_1a2b3c4d_1", "audit_comment": "why"}
HAND_MADE_JOIN = {"action": "polars_join", "right_ingredient": "B", "on": ["k"], "how": "left", "id": "audit_1a2b3c4d_2", "audit_comment": "why"}


def raw_with(tier2=None, tier3=None, tier1=None):
    plot = {"target_dataset": "T", "mapping": {"x": "v"}, "layers": [{"name": "geom_bar"}]}
    if tier3 is not None:
        plot["tier3"] = tier3
    table = {"tier1": tier1 if tier1 is not None else {"steps": []}}
    if tier2 is not None:
        table["tier2"] = tier2
    return {"data_engine": "python-polars", "plot_engine": "python-plotnine", "data_schemas": {"T": table},
            "analysis_groups": {"g": {"ui_label": "G", "plots": {"p": plot}}}}


# ---- engine_record.py:42 and :78 -----------------------------------------------------------------------------------------------------------------

def test_the_engine_record_lists_a_tier_2_whose_only_steps_are_audit_steps():
    raw = raw_with(tier2={"steps": [], AUDIT_STEPS: [AUDIT_FILTER]})
    record = engine_record(raw, [("p", raw["analysis_groups"]["g"]["plots"]["p"])], {})
    assert record["tables"]["T"]["tier2"] != NOT_RUN and record["tables"]["T"]["tier2"] == "python-polars"
    plain = raw_with(tier2={"steps": []})
    assert engine_record(plain, [("p", plain["analysis_groups"]["g"]["plots"]["p"])], {})["tables"]["T"]["tier2"] == NOT_RUN


def test_the_engine_record_lists_the_tier_3_of_a_plot_whose_only_steps_are_audit_steps():
    raw = raw_with(tier3={"steps": [], AUDIT_STEPS: [AUDIT_FILTER]})
    record = engine_record(raw, [("p", raw["analysis_groups"]["g"]["plots"]["p"])], {})
    assert record["plots"]["p"]["tier3"] == "python-polars"
    plain = raw_with(tier3={"steps": []})
    assert "tier3" not in engine_record(plain, [("p", plain["analysis_groups"]["g"]["plots"]["p"])], {})["plots"]["p"]


# ---- session_manager.py:48, :143 -----------------------------------------------------------------------------------------------------------------

def test_the_join_keys_of_home_are_read_from_the_steps_a_join_runs():
    """A join step that only the audit list holds is read as the engine would run it; with the author's steps alone it would be missed."""
    raw = {"joins": {"J": {"tier1": {"steps": [], AUDIT_STEPS: [HAND_MADE_JOIN]}, "tier2": {"steps": []}}}}
    assert extract_primary_keys(raw) == ["k"]
    raw["joins"]["J"]["tier2"] = {"steps": [], AUDIT_STEPS: [{**HAND_MADE_JOIN, "on": ["m"]}]}
    assert extract_primary_keys(raw) == ["k", "m"]
    assert extract_primary_keys({"joins": {"J": {"tier1": {"steps": []}}}}) == []


# ---- view_badge.py:51, :58 -----------------------------------------------------------------------------------------------------------------------

def test_the_badge_says_has_steps_when_only_audit_steps_exist_at_tier_2_and_tier_3():
    raw = raw_with(tier2={"steps": [], AUDIT_STEPS: [AUDIT_FILTER]}, tier3={"steps": [], AUDIT_STEPS: [AUDIT_FILTER]})
    assert has_tier2_steps(raw, "T") is True and has_plot_steps(raw, "p") is True
    plain = raw_with(tier2={"steps": []}, tier3={"steps": []})
    assert has_tier2_steps(plain, "T") is False and has_plot_steps(plain, "p") is False
    assert has_tier2_steps(raw, None) is False and has_plot_steps(raw, None) is False


# ---- Blueprint's writer (point 6) ----------------------------------------------------------------------------------------------------------------

SOURCE = Path(blueprint_handlers.__file__)


def save(raw_text):
    ns = dict(vars(blueprint_handlers))
    fn = _closure(ast.parse(SOURCE.read_text()), "_serialise_component_for_save")
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "s", "exec"), ns)
    nodes = [{"action": "modif_filter", "params": {"column": "v", "op": "gt", "value": 1, "na": "keep"}, "_tier": "tier1"}]
    return ns["_serialise_component_for_save"]("wrangling", nodes, raw_text, "tier1")


def test_blueprint_refuses_to_save_a_tier_file_that_holds_audit_steps_and_does_not_drop_them_silently():
    """The writer builds a new block of `data_engine` and `steps` only: a file with `audit_steps` is refused, nothing is written."""
    text = yaml.safe_dump({"steps": [], AUDIT_STEPS: [AUDIT_FILTER]})
    with pytest.raises(ValueError, match="holds audit steps"):
        save(text)
    assert save(yaml.safe_dump({"steps": []}))["steps"][0]["action"] == "modif_filter"
