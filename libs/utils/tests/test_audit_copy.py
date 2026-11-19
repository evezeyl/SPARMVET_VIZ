"""The audit copy of a recipe, in memory (piece A5 of slice A of the HOME audit redesign): `utils.audit_copy`.

What is proved, on a small recipe (tables A and B, a join AB, a plot on the join and a plot on A):
- the copy is a deep copy and the original is never changed, by any function;
- `add_step` writes ONE marked step at the END of one list (tier 1 or tier 2 of a table or join, tier 3 of a plot), creates a tier that does not
  exist in the decided container form, refuses a place that does not exist, a bad or repeated id, a step that already holds a marker;
- `remove_step` takes a marked step out and refuses an original step; a tier the copy created is removed when empty again, so the copy equals the original;
- `marked_steps` is in a fixed order, `strip_marked` leaves no marked step;
- `integrity_errors` is empty for a sound copy and names what differs otherwise: an original step changed, removed or reordered, an audit step not at the
  end of its list, a key changed anywhere else, a repeated id, an original that already holds a marked step;
- the result passes the checker in the profile "audit" when the original passes "run", and the same copy fails the profile "run" (an id is an error there).

Mutation index (each seen failing, see the report): MUTATION C1 `strip_marked` leaves a step; MUTATION C2 `remove_step` removes any step, an original one included.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_audit_copy.py -q
"""
import copy

import pytest

from utils import audit_copy, recipe_check
from utils.audit_copy import (
    AUDIT_ID, AuditCopyError, MarkedStep, add_step, audit_operation, audit_recipe_of, integrity_errors, is_marked, marked_steps, parse_place,
    remove_step, split_marked, strip_marked)
from utils.recipe_check import check_recipe

ACTIONS = {
    "modif_filter": {
        "context": ["t1", "t2", "t3"],
        "params": {
            "column": {"widget": "column_selector", "required": True},
            "op": {"widget": "enum", "options": ["eq", "ne", "gt", "ge", "lt", "le"], "required": True},
            "value": {"widget": "string", "required": True},
            "na": {"widget": "enum", "options": ["keep", "remove"], "required": True},
        },
    },
    "polars_drop": {
        "context": ["t1", "t2", "t3"],
        "params": {"columns": {"widget": "column_selector", "multi": True, "required": True}},
    },
    "polars_join": {
        "context": ["assembly"],
        "params": {
            "right_ingredient": {"widget": "string", "required": True},
            "how": {"widget": "enum", "options": ["left", "inner"], "required": True},
            "on": {"widget": "string", "required": False},
        },
    },
}
CATALOGS = {
    "actions": ACTIONS,
    "components": {"geom_col", "geom_point", "theme_bw"},
    "component_arguments": {"geom_col": {"fill", "color"}, "geom_point": None, "theme_bw": None},
    "themes": {"theme_bw", "theme_light"},
    "old_action_names": {},
}

FILTER_V = {"action": "modif_filter", "column": "v", "op": "gt", "value": "1", "na": "remove"}
FILTER_W = {"action": "modif_filter", "column": "w", "op": "gt", "value": "2", "na": "remove"}
DROP_V = {"action": "polars_drop", "columns": ["v"]}
ID1, ID2, ID3, ID4 = "audit_1a2b3c4d_1", "audit_1a2b3c4d_2", "audit_00ff00ff_1", "audit_deadbeef_7"


def original() -> dict:
    return {
        "id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine",
        "info": {"label": "R", "description": "What it answers", "contact": "me"},
        "data_schemas": {
            "A": {"label": "A", "description": "One row per sample.", "source": {"type": "local_tsv", "path": "assets/test_data/a.tsv"},
                  "null_values": [], "strip": True,
                  "input_fields": {"id": {"type": "String", "is_entity_key": True}, "v": {"type": "Float64"}},
                  "tier1": {"steps": [{"action": "polars_drop", "columns": ["nothing_here"]}]}},
            "B": {"label": "B", "description": "One row per sample.", "source": {"type": "local_tsv", "path": "assets/test_data/b.tsv"},
                  "null_values": ["NA"], "strip": False,
                  "input_fields": {"id": {"type": "String", "is_entity_key": True}, "w": {"type": "Int64"}},
                  "tier1": {"steps": []}},
        },
        "joins": {
            "AB": {"label": "AB", "description": "One row per sample, A with B.", "ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
                   "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]},
                   "tier2": {"steps": [FILTER_W]}, "labels": {"v": "Value"}},
        },
        "analysis_groups": {"g": {"ui_label": "G", "description": "Question.", "plots": {
            "p": {"ui_label": "P", "description": "Drawn.", "target_dataset": "AB", "mapping": {"x": "id", "y": "v"}, "layers": [{"name": "geom_col"}]},
            "q": {"ui_label": "Q", "description": "Drawn.", "target_dataset": "A", "mapping": {"x": "id", "y": "v"}, "layers": [{"name": "geom_col"}]}}}},
    }


@pytest.fixture
def base():
    return original()


@pytest.fixture
def snapshot(base):
    return copy.deepcopy(base)


def steps_of(raw, owner, tier):
    holder = raw["joins"][owner] if owner in raw.get("joins", {}) else raw["data_schemas"][owner]
    return holder[tier]["steps"]


# =====================================================================================================================
# The copy and the places
# =====================================================================================================================


def test_the_audit_copy_is_a_deep_copy_equal_to_the_original_and_independent_of_it(base, snapshot):
    audit = audit_recipe_of(base)
    assert audit == base and audit is not base
    audit["data_schemas"]["A"]["tier1"]["steps"].append({"action": "x"})
    audit["info"]["label"] = "changed"
    assert base == snapshot


def test_a_place_is_a_node_id_of_the_graph_and_anything_else_is_refused():
    assert parse_place("T1:A") == ("tier1", "A")
    assert parse_place("T2:AB") == ("tier2", "AB")
    assert parse_place("T3:p") == ("tier3", "p")
    for bad in ("T4:A", "A", "T1:", ":A", "", None, 3, "t1:A", "DS:A"):
        with pytest.raises(AuditCopyError, match="not a place"):
            parse_place(bad)


def test_the_id_pattern_is_the_one_of_the_checker():
    assert AUDIT_ID.pattern == recipe_check._AUDIT_ID.pattern


# =====================================================================================================================
# add_step
# =====================================================================================================================


@pytest.mark.parametrize("place, owner, tier", [("T1:A", "A", "tier1"), ("T1:B", "B", "tier1"), ("T1:AB", "AB", "tier1"), ("T2:AB", "AB", "tier2")])
def test_a_step_is_written_at_the_end_of_the_list_of_its_place_with_its_marker_and_reason(base, snapshot, place, owner, tier):
    audit = audit_recipe_of(base)
    before = list(steps_of(audit, owner, tier))
    add_step(audit, place, FILTER_V, ID1, comment="the reason")
    after = steps_of(audit, owner, tier)
    assert after[:-1] == before and len(after) == len(before) + 1
    assert after[-1] == {**FILTER_V, "id": ID1, "comment": "the reason"}
    assert base == snapshot, "the original is never changed"
    assert [m.place for m in marked_steps(audit)] == [place]


def test_a_step_without_a_reason_has_no_comment_key(base):
    audit = audit_recipe_of(base)
    add_step(audit, "T1:B", DROP_V, ID1)
    assert steps_of(audit, "B", "tier1") == [{**DROP_V, "id": ID1}]


def test_a_step_is_written_at_the_end_of_the_tier_3_of_a_plot_and_the_tier_is_created_when_absent(base):
    audit = audit_recipe_of(base)
    assert "tier3" not in audit["analysis_groups"]["g"]["plots"]["p"]
    add_step(audit, "T3:p", FILTER_V, ID1, comment="why")
    assert audit["analysis_groups"]["g"]["plots"]["p"]["tier3"] == {"steps": [{**FILTER_V, "id": ID1, "comment": "why"}]}
    add_step(audit, "T3:p", DROP_V, ID2)
    assert [s["id"] for s in audit["analysis_groups"]["g"]["plots"]["p"]["tier3"]["steps"]] == [ID1, ID2]
    assert "tier3" not in audit["analysis_groups"]["g"]["plots"]["q"], "the other plot is untouched"


def test_a_tier_2_that_does_not_exist_is_created_in_the_container_form_with_no_engine_written(base):
    audit = audit_recipe_of(base)
    assert "tier2" not in audit["data_schemas"]["A"]
    add_step(audit, "T2:A", FILTER_V, ID1)
    assert audit["data_schemas"]["A"]["tier2"] == {"steps": [{**FILTER_V, "id": ID1}]}
    assert "data_engine" not in audit["data_schemas"]["A"]["tier2"]


def test_the_step_given_is_copied_not_shared(base):
    audit = audit_recipe_of(base)
    step = {"action": "polars_drop", "columns": ["v"]}
    add_step(audit, "T1:B", step, ID1)
    audit["data_schemas"]["B"]["tier1"]["steps"][0]["columns"].append("w")
    assert step == {"action": "polars_drop", "columns": ["v"]}


@pytest.mark.parametrize("place, words", [
    ("T1:nothing", "no table or join 'nothing'"),
    ("T2:nothing", "no table or join 'nothing'"),
    ("T3:nothing", "no plot 'nothing'"),
    ("T3:A", "no plot 'A'"),
    ("T1:p", "no table or join 'p'"),
    ("T2:B", "No plot reads 'B'"),
    ("tier1:A", "not a place"),
])
def test_a_place_that_does_not_exist_is_refused_with_a_plain_message_and_nothing_changes(base, place, words):
    audit = audit_recipe_of(base)
    with pytest.raises(AuditCopyError, match=words):
        add_step(audit, place, FILTER_V, ID1)
    assert audit == base


@pytest.mark.parametrize("step, id_, comment, words", [
    ({"column": "v"}, ID1, None, "action"),
    ("modif_filter", ID1, None, "action"),
    ({"action": 3}, ID1, None, "action"),
    ({**FILTER_V, "id": ID3}, ID1, None, "already holds id"),
    ({**FILTER_V, "comment": "x"}, ID1, None, "already holds comment"),
    (FILTER_V, "audit_1", None, "not an audit id"),
    (FILTER_V, "audit_1A2B3C4D_1", None, "not an audit id"),
    (FILTER_V, "audit_1a2b3c4d_x", None, "not an audit id"),
    (FILTER_V, None, None, "not an audit id"),
    (FILTER_V, ID1, 5, "text"),
])
def test_a_bad_step_id_or_comment_is_refused_and_nothing_changes(base, step, id_, comment, words):
    audit = audit_recipe_of(base)
    with pytest.raises(AuditCopyError, match=words):
        add_step(audit, "T1:B", step, id_, comment)
    assert audit == base


def test_an_id_used_twice_is_refused_wherever_the_first_one_is(base):
    audit = audit_recipe_of(base)
    add_step(audit, "T1:A", FILTER_V, ID1)
    with pytest.raises(AuditCopyError, match="already used"):
        add_step(audit, "T3:p", FILTER_V, ID1)
    assert [m.step_id for m in marked_steps(audit)] == [ID1]


def test_a_tier_that_is_not_a_mapping_with_a_list_is_refused(base):
    audit = audit_recipe_of(base)
    audit["data_schemas"]["B"]["tier1"] = []
    with pytest.raises(AuditCopyError, match="not written as a mapping"):
        add_step(audit, "T1:B", FILTER_V, ID1)


# =====================================================================================================================
# remove_step
# =====================================================================================================================


def test_removing_the_only_step_of_a_created_tier_gives_the_original_back_exactly(base):
    audit = audit_recipe_of(base)
    add_step(audit, "T3:p", FILTER_V, ID1)
    add_step(audit, "T2:A", FILTER_V, ID2)
    assert audit != base
    remove_step(audit, ID1)
    remove_step(audit, ID2)
    assert audit == base


def test_removing_one_of_two_steps_keeps_the_other_and_the_tier(base):
    audit = audit_recipe_of(base)
    add_step(audit, "T1:B", FILTER_V, ID1)
    add_step(audit, "T1:B", DROP_V, ID2)
    remove_step(audit, ID1)
    assert steps_of(audit, "B", "tier1") == [{**DROP_V, "id": ID2}]


def test_the_tier_1_of_a_table_is_never_removed_even_when_the_copy_made_its_only_step(base):
    audit = audit_recipe_of(base)
    add_step(audit, "T1:B", FILTER_V, ID1)
    remove_step(audit, ID1)
    assert audit["data_schemas"]["B"]["tier1"] == {"steps": []}


def test_an_original_step_cannot_be_removed(base, snapshot):
    """MUTATION C2: a remove that takes any step would take the original step (shown by the first case)."""
    audit = audit_recipe_of(base)
    add_step(audit, "T1:A", FILTER_V, ID1)
    keep = copy.deepcopy(audit)
    for refused in ("polars_drop", "modif_filter", "T1:A", "0", "1", "", None, "audit_1", ID4):
        with pytest.raises(AuditCopyError):
            remove_step(audit, refused)
    assert audit == keep and steps_of(audit, "A", "tier1")[0] == {"action": "polars_drop", "columns": ["nothing_here"]}
    assert base == snapshot


def test_removing_an_id_that_no_step_has_says_so(base):
    audit = audit_recipe_of(base)
    with pytest.raises(AuditCopyError, match="No audit step of the copy has the id"):
        remove_step(audit, ID1)


def test_an_empty_tier_that_the_original_wrote_is_not_a_difference_after_an_add_and_a_remove():
    """The original wrote `tier2: {steps: []}`; the copy adds a step and takes it out: the tier is gone, which the engine reads as the same, and
    `integrity_errors` agrees. A tier with an engine written is never removed."""
    raw = original()
    raw["data_schemas"]["A"]["tier2"] = {"steps": []}
    raw["data_schemas"]["B"]["tier2"] = {"data_engine": "python-polars", "steps": []}
    audit = audit_recipe_of(raw)
    add_step(audit, "T2:A", FILTER_V, ID1)
    remove_step(audit, ID1)
    assert "tier2" not in audit["data_schemas"]["A"]
    assert integrity_errors(audit, raw) == []
    assert audit["data_schemas"]["B"]["tier2"] == {"data_engine": "python-polars", "steps": []}


# =====================================================================================================================
# marked_steps and strip_marked
# =====================================================================================================================


def test_marked_steps_are_in_a_fixed_order_each_with_its_place(base):
    audit = audit_recipe_of(base)
    add_step(audit, "T3:q", FILTER_V, ID1)
    add_step(audit, "T2:AB", FILTER_V, ID2)
    add_step(audit, "T1:AB", DROP_V, ID3)
    add_step(audit, "T1:A", FILTER_V, ID4)
    add_step(audit, "T1:A", DROP_V, "audit_1a2b3c4d_9")
    found = marked_steps(audit)
    assert [(m.place, m.step_id) for m in found] == [("T1:A", ID4), ("T1:A", "audit_1a2b3c4d_9"), ("T1:AB", ID3), ("T2:AB", ID2), ("T3:q", ID1)]
    assert all(isinstance(m, MarkedStep) for m in found)
    assert found[0].step == {**FILTER_V, "id": ID4}
    assert marked_steps(base) == []


def test_strip_marked_leaves_no_marked_step_and_changes_nothing_else(base, snapshot):
    """MUTATION C1: a strip that leaves a step is seen here."""
    audit = audit_recipe_of(base)
    add_step(audit, "T1:A", FILTER_V, ID1)
    add_step(audit, "T2:AB", DROP_V, ID2)
    add_step(audit, "T3:p", FILTER_V, ID3)
    kept = copy.deepcopy(audit)
    stripped = strip_marked(audit)
    assert marked_steps(stripped) == []
    assert audit == kept, "strip_marked does not change its argument"
    assert integrity_errors(audit, base) == []
    assert steps_of(stripped, "A", "tier1") == steps_of(base, "A", "tier1")
    assert steps_of(stripped, "AB", "tier2") == steps_of(base, "AB", "tier2")
    assert base == snapshot


def test_split_marked_and_audit_operation():
    plain = {"action": "polars_drop", "columns": ["v"]}
    marked = {**FILTER_V, "id": ID1, "comment": "r"}
    assert split_marked([plain, marked, {**plain, "id": "not_an_audit_id"}]) == ([plain, {**plain, "id": "not_an_audit_id"}], [marked])
    assert split_marked(None) == ([], []) and split_marked("x") == ([], [])
    assert is_marked(marked) and not is_marked(plain) and not is_marked({"id": ID1[:-1]}) and not is_marked("audit_1a2b3c4d_1")
    assert audit_operation(marked) == FILTER_V


# =====================================================================================================================
# integrity_errors
# =====================================================================================================================


def test_a_copy_with_no_step_and_a_copy_with_steps_added_properly_are_sound(base):
    audit = audit_recipe_of(base)
    assert integrity_errors(audit, base) == []
    add_step(audit, "T1:A", FILTER_V, ID1)
    add_step(audit, "T2:AB", FILTER_V, ID2)
    add_step(audit, "T3:q", DROP_V, ID3)
    assert integrity_errors(audit, base) == []


def test_a_changed_original_step_is_named(base):
    audit = audit_recipe_of(base)
    audit["data_schemas"]["A"]["tier1"]["steps"][0]["columns"] = ["other"]
    errors = integrity_errors(audit, base)
    assert len(errors) == 1 and "Original step 1 of data_schemas.A.tier1.steps was changed" in errors[0]


def test_a_removed_original_step_is_named(base):
    audit = audit_recipe_of(base)
    audit["data_schemas"]["A"]["tier1"]["steps"].clear()
    errors = integrity_errors(audit, base)
    assert len(errors) == 1 and "An original step was removed from data_schemas.A.tier1.steps" in errors[0]


def test_a_reordered_original_list_is_named():
    raw = original()
    raw["data_schemas"]["B"]["tier1"]["steps"] = [DROP_V, FILTER_W]
    audit = audit_recipe_of(raw)
    audit["data_schemas"]["B"]["tier1"]["steps"].reverse()
    errors = integrity_errors(audit, raw)
    assert len(errors) == 1 and "The original steps of data_schemas.B.tier1.steps were reordered" in errors[0]


def test_an_unmarked_step_added_to_the_copy_is_named(base):
    audit = audit_recipe_of(base)
    audit["data_schemas"]["B"]["tier1"]["steps"].append(DROP_V)
    errors = integrity_errors(audit, base)
    assert len(errors) == 1 and "not a marked audit step was added to data_schemas.B.tier1.steps" in errors[0]


def test_an_audit_step_before_an_original_step_is_named(base):
    audit = audit_recipe_of(base)
    audit["joins"]["AB"]["tier2"]["steps"].insert(0, {**FILTER_V, "id": ID1})
    errors = integrity_errors(audit, base)
    assert any(f"The audit step {ID1} is not at the end of T2:AB" in e for e in errors)


def test_a_key_changed_added_or_removed_anywhere_else_is_named(base):
    audit = audit_recipe_of(base)
    audit["info"]["label"] = "other"
    audit["data_schemas"]["A"]["strip"] = False
    del audit["data_schemas"]["A"]["null_values"]
    audit["joins"]["AB"]["labels"] = {"v": "Value", "w": "W"}
    audit["extra"] = 1
    errors = integrity_errors(audit, base)
    assert any("info.label was changed" in e for e in errors)
    assert any("data_schemas.A.strip was changed" in e for e in errors)
    assert any("data_schemas.A.null_values was removed from the copy" in e for e in errors)
    assert any("joins.AB.labels" in e for e in errors)
    assert any("extra was added to the copy outside the audit steps" in e for e in errors)


def test_a_table_added_or_removed_in_the_copy_is_named(base):
    audit = audit_recipe_of(base)
    del audit["data_schemas"]["B"]
    audit["data_schemas"]["C"] = copy.deepcopy(base["data_schemas"]["B"])
    errors = integrity_errors(audit, base)
    assert any("data_schemas.B was removed from the copy" in e for e in errors)
    assert any("data_schemas.C was added to the copy" in e for e in errors)


def test_an_id_used_twice_in_a_copy_is_named(base):
    audit = audit_recipe_of(base)
    add_step(audit, "T1:A", FILTER_V, ID1)
    audit["data_schemas"]["B"]["tier1"]["steps"].append({**DROP_V, "id": ID1})
    errors = integrity_errors(audit, base)
    assert any(f"The id {ID1} is used twice (T1:A and T1:B)" in e for e in errors)


def test_an_original_that_already_holds_a_marked_step_is_not_an_original(base):
    held = audit_recipe_of(base)
    add_step(held, "T1:A", FILTER_V, ID1)
    errors = integrity_errors(held, held)
    assert any(f"The original recipe already holds the audit step {ID1} at T1:A" in e for e in errors)


def test_a_marked_step_somewhere_outside_the_known_lists_is_a_difference(base):
    audit = audit_recipe_of(base)
    audit["analysis_groups"]["g"]["plots"]["p"]["layers"].append({**FILTER_V, "id": ID1})
    assert integrity_errors(audit, base)


# =====================================================================================================================
# The checker
# =====================================================================================================================


def test_the_original_passes_run_and_a_copy_with_steps_passes_audit_but_not_run(base):
    assert check_recipe(base, "run", catalogs=CATALOGS).errors == []
    audit = audit_recipe_of(base)
    add_step(audit, "T1:A", FILTER_V, ID1, comment="a reason")
    add_step(audit, "T1:AB", DROP_V, ID2)
    add_step(audit, "T2:AB", FILTER_V, ID3)
    add_step(audit, "T2:A", FILTER_V, ID4)
    add_step(audit, "T3:p", FILTER_V, "audit_1a2b3c4d_5", comment="why")
    assert [p for p in check_recipe(audit, "audit", catalogs=CATALOGS).errors] == []
    assert any(p.code == "ST08" for p in check_recipe(audit, "run", catalogs=CATALOGS).errors), "an id is an error outside the audit profile"
    assert check_recipe(audit_recipe_of(base), "audit", catalogs=CATALOGS).errors == []


def test_a_tier_2_step_of_a_table_no_plot_reads_would_fail_the_checker_so_it_is_refused_before(base):
    audit = audit_recipe_of(base)
    audit["data_schemas"]["B"]["tier2"] = {"steps": [{**FILTER_V, "id": ID1}]}
    assert any(p.code == "S07" for p in check_recipe(audit, "audit", catalogs=CATALOGS).errors)
    with pytest.raises(AuditCopyError, match="No plot reads 'B'"):
        add_step(audit_recipe_of(base), "T2:B", FILTER_V, ID1)
