"""The audit copy of a recipe, in memory, in the form of D-0332 (piece C-1 of slice C of the HOME audit redesign): `utils.audit_copy`.

The form: in each tier the author's list `steps` is never touched and the audit writes a second list `audit_steps`; each audit step is the operation plus
`id: audit_<8 hex>_<k>` and `audit_comment: "<reason>"`. What is proved, on a small recipe (tables A and B, a join AB, a plot on the join and a plot on A):
- `start_audit` is a deep copy and the original is never changed, by any function;
- `add_step` writes ONE audit step in `audit_steps` of its place (the author's `steps` stays equal to the original's), gives the id itself (`k` counts the steps
  ever created in this audit, so the number of a removed step is never given again), creates a tier that does not exist (`steps: []` and the audit list, no engine),
  and refuses, changing nothing (the counter too): a place that does not exist, an action that an audit may not use, an id or a reason written in the step, a
  reason that is empty or not text;
- `remove_step` takes ANY audit step out (the one undo control), refuses an original step, removes an emptied `audit_steps` key and a tier the add created, so
  that add then remove gives back exactly the dictionary as it was;
- `all_audit_steps` is in a fixed order; `without_audit_steps` leaves no audit step and changes nothing else;
- `integrity_errors` is empty for a sound copy and names what differs otherwise: an original step changed, removed, reordered or MOVED to the audit list; an audit
  id or reason in the author's list; an audit step without an id, with a bad id, with no reason, with an action not allowed; an id used twice; a key
  changed anywhere else; an original that already holds audit steps;
- a reason can never be lost: it is `audit_comment`, required by the copy, by the integrity check and by the checker; written as `comment` it is refused;
- the result passes the checker in the profile "audit" when the original passes "run"; in any other profile the audit keys are refused.

Mutation index (each seen failing, see the report): C1 `without_audit_steps` leaves an audit list; C2 `remove_step` removes any step, an original one included;
C3 the counter goes down on a remove (the number of a removed step is given again); C4 `add_step` writes the reason as `comment`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_audit_copy.py -q
"""
import copy

import pytest

from utils import recipe_check, recipe_tiers
from utils.audit_copy import (
    AUDIT_ID, AuditCopy, AuditCopyError, add_step, all_audit_steps, audit_operation, integrity_errors, is_audit_id, parse_place, remove_step,
    start_audit, with_audit_steps, _holders)
from utils.recipe_check import check_recipe
from utils.recipe_tiers import AUDIT_COMMENT, AUDIT_STEPS, audit_steps_of, author_steps, step_list, without_audit_steps

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
AUD = "1a2b3c4d"   # the audit id (8 hex) the tests give to start_audit
ID1, ID2, ID3, ID4 = f"audit_{AUD}_1", f"audit_{AUD}_2", f"audit_{AUD}_3", f"audit_{AUD}_4"
WHY = "the reason"


def original() -> dict:
    return {
        "id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine",
        "info": {"ui_label": "R", "description": "What it answers", "contact": "me"},
        "data_schemas": {
            "A": {"ui_label": "A", "description": "One row per sample.", "source": {"type": "local_tsv", "path": "assets/test_data/a.tsv"},
                  "null_values": [], "strip": True,
                  "input_fields": {"id": {"type": "String", "is_entity_id": True}, "v": {"type": "Float64"}},
                  "tier1": {"steps": [{"action": "polars_drop", "columns": ["nothing_here"]}]}},
            "B": {"ui_label": "B", "description": "One row per sample.", "source": {"type": "local_tsv", "path": "assets/test_data/b.tsv"},
                  "null_values": ["NA"], "strip": False,
                  "input_fields": {"id": {"type": "String", "is_entity_id": True}, "w": {"type": "Int64"}},
                  "tier1": {"steps": []}},
        },
        "joins": {
            "AB": {"ui_label": "AB", "description": "One row per sample, A with B.", "ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
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


def start(raw: dict) -> AuditCopy:
    return start_audit(raw, AUD)


def owner_of(raw, owner):
    return raw["joins"][owner] if owner in raw.get("joins", {}) else raw["data_schemas"][owner]


def steps_of(raw, owner, tier):
    return owner_of(raw, owner)[tier]["steps"]


def audit_of(raw, owner, tier):
    return owner_of(raw, owner)[tier][AUDIT_STEPS]


def written(step, step_id, reason=WHY):
    return {**step, "id": step_id, AUDIT_COMMENT: reason}


# =====================================================================================================================
# The copy and the places
# =====================================================================================================================


def test_the_audit_copy_is_a_deep_copy_equal_to_the_original_and_independent_of_it(base, snapshot):
    audit = start(base)
    assert audit.recipe == base and audit.recipe is not base and audit.original == base and audit.original is not audit.recipe
    audit.recipe["data_schemas"]["A"]["tier1"]["steps"].append({"action": "x"})
    audit.recipe["info"]["ui_label"] = "changed"
    assert base == snapshot and audit.original == snapshot


def test_an_audit_starts_with_its_own_id_and_a_counter_at_zero(base):
    first, second = start_audit(base), start_audit(base)
    assert first.created == 0 and is_audit_id(f"audit_{first.audit_id}_1")
    assert first.audit_id != second.audit_id, "two audits are told apart by the 8 characters"
    assert start_audit(base, "00ff00ff").audit_id == "00ff00ff"
    for bad in ("1A2B3C4D", "1a2b3c4", "1a2b3c4d5", "zzzzzzzz", "", 12345678):
        with pytest.raises(AuditCopyError, match="not an audit identifier"):
            start_audit(base, bad)


def test_a_place_is_a_node_id_of_the_graph_and_anything_else_is_refused():
    assert parse_place("T1:A") == ("tier1", "A")
    assert parse_place("T2:AB") == ("tier2", "AB")
    assert parse_place("T3:p") == ("tier3", "p")
    for bad in ("T4:A", "A", "T1:", ":A", "", None, 3, "t1:A", "DS:A"):
        with pytest.raises(AuditCopyError, match="not a place"):
            parse_place(bad)


def test_the_form_of_an_audit_id_and_the_names_of_the_two_audit_keys_are_written_once():
    """The id form lives in `recipe_tiers` and the checker and the copy use that very object; the key names are constants, not texts spread over the code."""
    assert AUDIT_ID is recipe_tiers.AUDIT_ID and recipe_check._AUDIT_ID is recipe_tiers.AUDIT_ID
    assert (AUDIT_STEPS, AUDIT_COMMENT) == ("audit_steps", "audit_comment")
    assert is_audit_id("audit_1a2b3c4d_12") and not is_audit_id("audit_1a2b3c4d") and not is_audit_id(None)


def test_audit_operation_is_the_step_without_its_id_its_reason_and_any_note():
    assert audit_operation({**FILTER_V, "id": ID1, AUDIT_COMMENT: "r", "comment": "n"}) == FILTER_V


# =====================================================================================================================
# add_step
# =====================================================================================================================


@pytest.mark.parametrize("place, owner, tier", [("T1:A", "A", "tier1"), ("T1:B", "B", "tier1"), ("T1:AB", "AB", "tier1"), ("T2:AB", "AB", "tier2")])
def test_a_step_is_written_in_the_audit_list_of_its_place_and_the_authors_list_is_not_touched(base, snapshot, place, owner, tier):
    audit = start(base)
    step_id = add_step(audit, place, FILTER_V, WHY)
    assert step_id == ID1
    assert steps_of(audit.recipe, owner, tier) == steps_of(base, owner, tier), "the author's list is exactly the original's"
    assert audit_of(audit.recipe, owner, tier) == [written(FILTER_V, ID1)]
    assert base == snapshot, "the original is never changed"
    assert [(m.place, m.step_id) for m in all_audit_steps(audit.recipe)] == [(place, ID1)]


def test_the_number_counts_the_order_in_which_the_steps_were_created_in_the_audit_whatever_the_place(base):
    audit = start(base)
    assert add_step(audit, "T1:A", FILTER_V, WHY) == ID1
    assert add_step(audit, "T3:p", DROP_V, WHY) == ID2
    assert add_step(audit, "T1:A", FILTER_W, WHY) == ID3
    assert [s["id"] for s in audit_of(audit.recipe, "A", "tier1")] == [ID1, ID3], "the list holds them in the order they were added"
    assert audit.created == 3


def test_the_number_of_a_removed_step_is_never_given_again_in_the_same_audit(base):
    """MUTATION C3: a remove that lowers the counter, or a number taken as 'the highest present plus 1', gives _3 again after _3 was removed."""
    audit = start(base)
    for place in ("T1:A", "T1:B", "T1:AB"):
        add_step(audit, place, FILTER_V, WHY)
    remove_step(audit, ID3)                      # the highest number: the case where "highest present + 1" fails
    assert add_step(audit, "T1:AB", DROP_V, WHY) == ID4
    remove_step(audit, ID1)
    remove_step(audit, ID2)
    remove_step(audit, ID4)                      # nothing is left
    assert all_audit_steps(audit.recipe) == [] and audit.created == 4
    assert add_step(audit, "T1:A", FILTER_V, WHY) == f"audit_{AUD}_5"
    # whatever the sequence of adds and removes, the ids that were ever given are all different
    given, held = [], []
    audit = start(base)
    for action in "aarararaarrrarrraa":
        if action == "a":
            held.append(add_step(audit, "T1:B", FILTER_V, WHY))
            given.append(held[-1])
        elif held:
            remove_step(audit, held.pop(0 if len(held) % 2 else -1))
    assert len(given) == len(set(given)) and given == [f"audit_{AUD}_{n}" for n in range(1, len(given) + 1)]


def test_two_audits_of_one_recipe_give_ids_that_differ_in_their_eight_characters(base):
    a, b = start_audit(base, "00000000"), start_audit(base, "ffffffff")
    assert add_step(a, "T1:A", FILTER_V, WHY) != add_step(b, "T1:A", FILTER_V, WHY)


def test_a_step_is_written_in_the_audit_list_of_the_tier_3_of_a_plot_and_the_tier_is_created_when_absent(base):
    audit = start(base)
    plot = audit.recipe["analysis_groups"]["g"]["plots"]["p"]
    assert "tier3" not in plot
    add_step(audit, "T3:p", FILTER_V, "why")
    assert plot["tier3"] == {"steps": [], AUDIT_STEPS: [written(FILTER_V, ID1, "why")]}
    add_step(audit, "T3:p", DROP_V, WHY)
    assert [s["id"] for s in plot["tier3"][AUDIT_STEPS]] == [ID1, ID2]
    assert "tier3" not in audit.recipe["analysis_groups"]["g"]["plots"]["q"], "the other plot is untouched"


def test_a_tier_2_that_does_not_exist_is_created_with_an_empty_authors_list_and_no_engine_written(base):
    audit = start(base)
    assert "tier2" not in audit.recipe["data_schemas"]["A"]
    add_step(audit, "T2:A", FILTER_V, WHY)
    assert audit.recipe["data_schemas"]["A"]["tier2"] == {"steps": [], AUDIT_STEPS: [written(FILTER_V, ID1)]}


def test_the_step_given_is_copied_not_shared(base):
    audit = start(base)
    step = {"action": "polars_drop", "columns": ["v"]}
    add_step(audit, "T1:B", step, WHY)
    audit_of(audit.recipe, "B", "tier1")[0]["columns"].append("w")
    assert step == {"action": "polars_drop", "columns": ["v"]}


def test_an_audit_step_can_never_stand_between_two_author_steps(base):
    """The structure says it (D-0332): the author's list keeps its steps and the audit steps are in another list that the engine reads after it."""
    raw = original()
    raw["data_schemas"]["B"]["tier1"]["steps"] = [DROP_V, FILTER_W]
    audit = start(raw)
    add_step(audit, "T1:B", FILTER_V, WHY)
    assert steps_of(audit.recipe, "B", "tier1") == [DROP_V, FILTER_W]
    assert step_list(audit.recipe["data_schemas"]["B"], "tier1") == [DROP_V, FILTER_W, written(FILTER_V, ID1)]
    assert author_steps(audit.recipe["data_schemas"]["B"], "tier1") == [DROP_V, FILTER_W]
    assert audit_steps_of(audit.recipe["data_schemas"]["B"], "tier1") == [written(FILTER_V, ID1)]


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
    audit = start(base)
    with pytest.raises(AuditCopyError, match=words):
        add_step(audit, place, FILTER_V, WHY)
    assert audit.recipe == base and audit.created == 0


@pytest.mark.parametrize("step, reason, words", [
    ({"column": "v"}, WHY, "action"),
    ("modif_filter", WHY, "action"),
    ({"action": 3}, WHY, "action"),
    ({"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}, WHY, "is not one of them"),
    ({"action": "polars_sort", "by": ["v"]}, WHY, "is not one of them"),
    ({**FILTER_V, "id": ID3}, WHY, "already holds id"),
    ({**FILTER_V, AUDIT_COMMENT: "x"}, WHY, "already holds"),
    (FILTER_V, None, "reason"),
    (FILTER_V, "", "reason"),
    (FILTER_V, "   ", "reason"),
    (FILTER_V, 5, "reason"),
])
def test_a_step_that_an_audit_may_not_write_is_refused_and_nothing_changes_not_even_the_counter(base, step, reason, words):
    audit = start(base)
    with pytest.raises(AuditCopyError, match=words):
        add_step(audit, "T1:B", step, reason)
    assert audit.recipe == base and audit.created == 0


def test_a_tier_that_is_not_a_mapping_with_a_list_is_refused(base):
    audit = start(base)
    audit.recipe["data_schemas"]["B"]["tier1"] = []
    with pytest.raises(AuditCopyError, match="not written as a mapping"):
        add_step(audit, "T1:B", FILTER_V, WHY)
    audit.recipe["data_schemas"]["B"]["tier1"] = {"steps": [], AUDIT_STEPS: "x"}
    with pytest.raises(AuditCopyError, match="not a list"):
        add_step(audit, "T1:B", FILTER_V, WHY)
    assert audit.created == 0


def test_the_reason_is_written_as_audit_comment_and_never_as_comment(base):
    """MUTATION C4: the reason written as `comment` would be mistaken for the author's note and lost from the keys, the checker and the run."""
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, "excluded: poor quality")
    step = audit_of(audit.recipe, "A", "tier1")[0]
    assert step[AUDIT_COMMENT] == "excluded: poor quality" and "comment" not in step


# =====================================================================================================================
# remove_step
# =====================================================================================================================


def test_removing_the_only_step_of_a_created_tier_gives_the_original_back_exactly(base):
    audit = start(base)
    add_step(audit, "T3:p", FILTER_V, WHY)
    add_step(audit, "T2:A", FILTER_V, WHY)
    assert audit.recipe != base
    remove_step(audit, ID1)
    remove_step(audit, ID2)
    assert audit.recipe == base


def test_removing_one_of_two_steps_keeps_the_other_in_its_list(base):
    audit = start(base)
    add_step(audit, "T1:B", FILTER_V, WHY)
    add_step(audit, "T1:B", DROP_V, WHY)
    remove_step(audit, ID1)
    assert audit_of(audit.recipe, "B", "tier1") == [written(DROP_V, ID2)]


def test_any_audit_step_can_be_removed_the_first_a_middle_one_or_the_last(base):
    """The one undo control (D-0314): the user picks any step, no 'remove last' only."""
    for removed in (ID1, ID2, ID3):
        audit = start(base)
        for place in ("T1:A", "T1:A", "T1:A"):
            add_step(audit, place, FILTER_V, WHY)
        remove_step(audit, removed)
        assert [s["id"] for s in audit_of(audit.recipe, "A", "tier1")] == [i for i in (ID1, ID2, ID3) if i != removed]
        assert steps_of(audit.recipe, "A", "tier1") == steps_of(base, "A", "tier1")


def test_the_tier_1_of_a_table_is_never_removed_even_when_the_copy_made_its_only_step(base):
    audit = start(base)
    add_step(audit, "T1:B", FILTER_V, WHY)
    remove_step(audit, ID1)
    assert audit.recipe["data_schemas"]["B"]["tier1"] == {"steps": []}


def test_an_original_step_cannot_be_removed(base, snapshot):
    """MUTATION C2: a remove that takes any step would take the original step (shown by the first case)."""
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, WHY)
    keep = copy.deepcopy(audit.recipe)
    for refused in ("polars_drop", "modif_filter", "T1:A", "0", "1", "", None, "audit_1", "audit_deadbeef_7"):
        with pytest.raises(AuditCopyError):
            remove_step(audit, refused)
    assert audit.recipe == keep and steps_of(audit.recipe, "A", "tier1")[0] == {"action": "polars_drop", "columns": ["nothing_here"]}
    assert base == snapshot


def test_a_hand_made_audit_id_among_the_authors_steps_is_not_an_audit_step_to_remove(base):
    audit = start(base)
    audit.recipe["data_schemas"]["B"]["tier1"]["steps"].append({**DROP_V, "id": ID4})
    with pytest.raises(AuditCopyError, match="No audit step of the copy has the id"):
        remove_step(audit, ID4)
    assert len(steps_of(audit.recipe, "B", "tier1")) == 1


def test_removing_an_id_that_no_step_has_says_so(base):
    with pytest.raises(AuditCopyError, match="No audit step of the copy has the id"):
        remove_step(start(base), ID1)


def test_an_empty_tier_that_the_original_wrote_stays_after_an_add_and_a_remove():
    """The original wrote `tier2: {steps: []}`; the copy adds a step and takes it out: the tier is still there, exactly as before the add. A tier the add
    created goes. A tier with an engine written is never removed."""
    raw = original()
    raw["data_schemas"]["A"]["tier2"] = {"steps": []}
    raw["data_schemas"]["B"]["tier2"] = {"data_engine": "python-polars", "steps": []}
    audit = start(raw)
    before = copy.deepcopy(audit.recipe)
    add_step(audit, "T2:A", FILTER_V, WHY)
    remove_step(audit, ID1)
    assert audit.recipe["data_schemas"]["A"]["tier2"] == {"steps": []}
    assert audit.recipe == before and integrity_errors(audit.recipe, raw) == []
    assert audit.recipe["data_schemas"]["B"]["tier2"] == {"data_engine": "python-polars", "steps": []}


def _every_place(raw: dict) -> list:
    """Every place of the recipe where `add_step` accepts a step (found by trying on a copy)."""
    found = []
    for place, _, _, _ in _holders(raw):
        try:
            add_step(start(raw), place, FILTER_V, WHY)
        except AuditCopyError:
            continue
        found.append(place)
    return found


def _written_empty_tiers(raw: dict) -> dict:
    """The recipe with an empty `{steps: []}` written for every tier2 and tier3 that is absent."""
    out = copy.deepcopy(raw)
    for _, tier, _, body in _holders(out):
        if tier in ("tier2", "tier3") and tier not in body:
            body[tier] = {"steps": []}
    return out


@pytest.mark.parametrize("variant", ["as written", "every empty tier written"])
def test_add_then_remove_gives_back_exactly_the_copy_for_every_place(variant):
    """MUTATION F3: a remove that deletes every empty tier2 or tier3 fails the variant in which the original wrote them; one that leaves an emptied `audit_steps` fails both."""
    raw = original() if variant == "as written" else _written_empty_tiers(original())
    places = _every_place(raw)
    assert {"T1:A", "T2:A", "T3:p", "T1:AB"} <= set(places) and len(places) >= 6
    for place in places:
        audit = start(raw)
        before = copy.deepcopy(audit.recipe)
        add_step(audit, place, FILTER_V, WHY)
        assert audit.recipe != before, place
        remove_step(audit, ID1)
        assert audit.recipe == before, place
        assert integrity_errors(audit.recipe, raw) == [], place


def test_the_copy_minus_its_audit_steps_equals_the_original_also_where_the_audit_created_the_tier():
    """An absent tier and a created tier that holds only an empty `steps` and an audit list are the same for the integrity check: the engine runs nothing
    for either, and removing the audit list gives `steps: []`."""
    raw = original()
    place = next(p for p in _every_place(raw) if p.startswith("T2:") and "tier2" not in dict((pl, b) for pl, _, _, b in _holders(raw))[p])
    audit = start(raw)
    add_step(audit, place, FILTER_V, WHY)
    stripped = without_audit_steps(audit.recipe)
    assert all_audit_steps(stripped) == [] and stripped != raw, "an empty created tier stays in the stripped copy"
    _, name = place.split(":")
    assert (stripped["data_schemas"].get(name) or stripped["joins"][name])["tier2"] == {"steps": []}
    assert integrity_errors(audit.recipe, raw) == []


# =====================================================================================================================
# all_audit_steps, without_audit_steps, with_audit_steps
# =====================================================================================================================


def test_audit_steps_are_in_a_fixed_order_each_with_its_place(base):
    audit = start(base)
    add_step(audit, "T3:q", DROP_V, WHY)
    add_step(audit, "T2:AB", FILTER_V, WHY)
    add_step(audit, "T1:B", FILTER_W, WHY)
    add_step(audit, "T1:A", FILTER_V, WHY)
    add_step(audit, "T1:A", DROP_V, WHY)
    found = all_audit_steps(audit.recipe)
    assert [(m.place, m.step_id) for m in found] == [("T1:A", ID4), ("T1:A", "audit_%s_5" % AUD), ("T1:B", ID3), ("T2:AB", ID2), ("T3:q", ID1)]
    assert found[0].step == written(FILTER_V, ID4)


def test_without_audit_steps_leaves_no_audit_list_and_changes_nothing_else(base, snapshot):
    """MUTATION C1: a strip that leaves an `audit_steps` key (even an empty one) is caught here."""
    audit = start(base)
    add_step(audit, "T1:B", FILTER_V, WHY)
    add_step(audit, "T1:AB", DROP_V, WHY)
    add_step(audit, "T3:p", DROP_V, WHY)
    keep = copy.deepcopy(audit.recipe)
    stripped = without_audit_steps(audit.recipe)
    assert audit.recipe == keep, "the argument is not changed"
    assert all_audit_steps(stripped) == []
    assert not recipe_tiers.audit_step_places(stripped)
    assert stripped["data_schemas"]["B"]["tier1"] == {"steps": []}
    assert stripped["joins"]["AB"]["tier1"] == snapshot["joins"]["AB"]["tier1"]
    assert stripped["info"] == snapshot["info"] and stripped["data_schemas"]["A"] == snapshot["data_schemas"]["A"]
    assert without_audit_steps(base) == snapshot, "an original has nothing to strip"


def test_an_empty_audit_list_is_stripped_too_and_is_the_same_recipe(base):
    raw = copy.deepcopy(base)
    raw["data_schemas"]["B"]["tier1"][AUDIT_STEPS] = []
    assert recipe_tiers.audit_step_places(raw) == ["data_schemas.B.tier1"]
    assert without_audit_steps(raw) == base and integrity_errors(raw, base) == []


def test_with_audit_steps_puts_the_steps_as_written_into_a_copy_of_the_original(base, snapshot):
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, "r1")
    add_step(audit, "T3:p", DROP_V, "r2")
    add_step(audit, "T1:A", FILTER_W, "r3")
    found = all_audit_steps(audit.recipe)
    rebuilt = with_audit_steps(base, found[:2])
    assert [m.step_id for m in all_audit_steps(rebuilt)] == [found[0].step_id, found[1].step_id]
    assert with_audit_steps(base, found) == audit.recipe, "all of them gives the copy back"
    assert base == snapshot
    rebuilt["data_schemas"]["A"]["tier1"][AUDIT_STEPS][0]["value"] = "changed"
    assert found[0].step["value"] == "1", "the steps are copied"


# =====================================================================================================================
# integrity_errors
# =====================================================================================================================


def test_a_copy_with_no_step_and_a_copy_with_steps_added_properly_are_sound(base):
    audit = start(base)
    assert integrity_errors(audit.recipe, base) == []
    add_step(audit, "T1:A", FILTER_V, WHY)
    add_step(audit, "T1:AB", DROP_V, WHY)
    add_step(audit, "T2:AB", FILTER_V, WHY)
    add_step(audit, "T3:p", FILTER_V, WHY)
    assert integrity_errors(audit.recipe, base) == []


def test_a_changed_original_step_is_named(base):
    audit = start(base)
    audit.recipe["data_schemas"]["A"]["tier1"]["steps"][0]["columns"] = ["other"]
    errors = integrity_errors(audit.recipe, base)
    assert len(errors) == 1 and "Original step 1 of data_schemas.A.tier1.steps was changed" in errors[0]


def test_a_removed_original_step_is_named(base):
    audit = start(base)
    audit.recipe["data_schemas"]["A"]["tier1"]["steps"].clear()
    errors = integrity_errors(audit.recipe, base)
    assert len(errors) == 1 and "An original step was removed from data_schemas.A.tier1.steps" in errors[0]


def test_an_original_step_moved_into_the_audit_list_is_named(base):
    audit = start(base)
    moved = audit.recipe["data_schemas"]["A"]["tier1"]["steps"].pop(0)
    audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS] = [{**moved, "id": ID1, AUDIT_COMMENT: WHY}]
    errors = integrity_errors(audit.recipe, base)
    assert any("An original step was removed from data_schemas.A.tier1.steps" in e for e in errors)
    assert len(errors) == 1, "polars_drop is an allowed audit action: what is wrong is only that the original step left its list"


def test_a_reordered_original_list_is_named():
    raw = original()
    raw["data_schemas"]["B"]["tier1"]["steps"] = [DROP_V, FILTER_W]
    audit = start(raw)
    audit.recipe["data_schemas"]["B"]["tier1"]["steps"].reverse()
    errors = integrity_errors(audit.recipe, raw)
    assert len(errors) == 1 and "The original steps of data_schemas.B.tier1.steps were reordered" in errors[0]


def test_a_step_added_to_the_authors_list_is_named(base):
    audit = start(base)
    audit.recipe["data_schemas"]["B"]["tier1"]["steps"].append(DROP_V)
    errors = integrity_errors(audit.recipe, base)
    assert len(errors) == 1 and "not an audit step was added to data_schemas.B.tier1.steps" in errors[0]


def test_a_hand_made_audit_step_in_the_authors_list_is_refused(base):
    """The structure cannot express an audit step between two author steps, and a hand-made one (an audit id or a reason in `steps`) is named."""
    audit = start(base)
    audit.recipe["joins"]["AB"]["tier2"]["steps"].insert(0, written(FILTER_V, ID1))
    errors = integrity_errors(audit.recipe, base)
    assert any(f"carries the id {ID1}" in e and "belongs in audit_steps" in e for e in errors)
    assert any("carries audit_comment" in e for e in errors)
    plain = start(base)
    plain.recipe["joins"]["AB"]["tier2"]["steps"][0] = {**FILTER_W, AUDIT_COMMENT: WHY}
    assert any("carries audit_comment" in e for e in integrity_errors(plain.recipe, base))


def test_an_audit_step_without_a_proper_id_a_reason_or_an_allowed_action_is_named(base):
    audit = start(base)
    audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS] = [
        {**FILTER_V, AUDIT_COMMENT: WHY},                                       # no id
        {**FILTER_V, "id": "audit_zz", AUDIT_COMMENT: WHY},                     # bad id
        {**FILTER_V, "id": ID1},                                                # no reason
        {**FILTER_V, "id": ID2, AUDIT_COMMENT: "  "},                           # empty reason
        {**FILTER_V, "id": ID3, "comment": WHY},                                # the reason in the author's note key: lost
        {"action": "polars_sort", "by": ["v"], "id": ID4, AUDIT_COMMENT: WHY},  # not an audit action
        "not a mapping",
    ]
    errors = integrity_errors(audit.recipe, base)
    assert any("audit_steps 1 of T1:A has no audit id" in e for e in errors)
    assert any("audit_steps 2 of T1:A has no audit id" in e for e in errors)
    assert any("audit_steps 3 of T1:A has no reason" in e for e in errors)
    assert any("audit_steps 4 of T1:A has no reason" in e for e in errors)
    assert any("audit_steps 5 of T1:A has no reason" in e for e in errors), "a reason moved to `comment` is a reason lost, and it is named"
    assert any("audit_steps 6 of T1:A is 'polars_sort'" in e for e in errors)
    assert any("audit step 7 of T1:A is not a mapping" in e for e in errors)


def test_an_audit_list_that_is_not_a_list_is_named(base):
    audit = start(base)
    audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS] = {"a": 1}
    assert any("audit_steps of T1:A is not a list" in e for e in integrity_errors(audit.recipe, base))


def test_a_key_changed_added_or_removed_anywhere_else_is_named(base):
    audit = start(base)
    audit.recipe["info"]["ui_label"] = "other"
    audit.recipe["data_schemas"]["A"]["strip"] = False
    del audit.recipe["data_schemas"]["A"]["null_values"]
    audit.recipe["joins"]["AB"]["labels"] = {"v": "Value", "w": "W"}
    audit.recipe["extra"] = 1
    errors = integrity_errors(audit.recipe, base)
    assert any("info.ui_label was changed" in e for e in errors)
    assert any("data_schemas.A.strip was changed" in e for e in errors)
    assert any("data_schemas.A.null_values was removed from the copy" in e for e in errors)
    assert any("joins.AB.labels" in e for e in errors)
    assert any("extra was added to the copy outside the audit steps" in e for e in errors)


def test_a_table_added_or_removed_in_the_copy_is_named(base):
    audit = start(base)
    del audit.recipe["data_schemas"]["B"]
    audit.recipe["data_schemas"]["C"] = copy.deepcopy(base["data_schemas"]["B"])
    errors = integrity_errors(audit.recipe, base)
    assert any("data_schemas.B was removed from the copy" in e for e in errors)
    assert any("data_schemas.C was added to the copy" in e for e in errors)


def test_an_id_used_twice_in_a_copy_is_named(base):
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, WHY)
    audit.recipe["data_schemas"]["B"]["tier1"][AUDIT_STEPS] = [written(DROP_V, ID1)]
    errors = integrity_errors(audit.recipe, base)
    assert any(f"The id {ID1} is used twice (T1:A and T1:B)" in e for e in errors)


def test_an_original_that_already_holds_audit_steps_is_not_an_original(base):
    held = start(base)
    add_step(held, "T1:A", FILTER_V, WHY)
    errors = integrity_errors(held.recipe, held.recipe)
    assert any("The original recipe already holds audit_steps at data_schemas.A.tier1" in e for e in errors)
    handmade = copy.deepcopy(base)
    handmade["data_schemas"]["B"]["tier1"]["steps"].append({**DROP_V, "id": ID1})
    assert any(f"already holds the id {ID1} on a step at T1:B" in e for e in integrity_errors(handmade, handmade))


def test_an_audit_list_where_no_tier_reads_it_is_named_in_plain_words(base):
    """A tier 3 of a table or a join, a tier 1 or tier 2 of a plot: nothing runs those steps, so the list is inert; it is said, not left to show as 'a tier was added'."""
    audit = start(base)
    audit.recipe["data_schemas"]["B"]["tier3"] = {"steps": [], AUDIT_STEPS: [written(FILTER_V, ID1)]}
    audit.recipe["joins"]["AB"]["tier3"] = {"steps": [], AUDIT_STEPS: []}
    audit.recipe["analysis_groups"]["g"]["plots"]["q"]["tier1"] = {"steps": [], AUDIT_STEPS: [written(FILTER_V, ID2)]}
    audit.recipe["analysis_groups"]["g"]["plots"]["q"]["tier2"] = {"steps": [], AUDIT_STEPS: []}
    errors = integrity_errors(audit.recipe, base)
    for place, kind in (("B.tier3", "a table or a join has no tier 3"), ("AB.tier3", "a table or a join has no tier 3"),
                        ("plot q.tier1", "a plot has a tier 3 only"), ("plot q.tier2", "a plot has a tier 3 only")):
        assert any(f"audit_steps list is written at {place}, where no tier reads it ({kind})" in e for e in errors), (place, errors)


def test_an_audit_list_somewhere_outside_the_known_tiers_is_a_difference(base):
    audit = start(base)
    audit.recipe["analysis_groups"]["g"]["plots"]["p"]["layers"].append(written(FILTER_V, ID1))
    audit.recipe["info"][AUDIT_STEPS] = [written(FILTER_V, ID2)]
    errors = integrity_errors(audit.recipe, base)
    assert errors and any("info.audit_steps was added" in e for e in errors)


# =====================================================================================================================
# The checker
# =====================================================================================================================


def test_the_original_passes_run_and_a_copy_with_steps_passes_audit_but_not_run(base):
    assert check_recipe(base, "run", catalogs=CATALOGS).errors == []
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, "a reason")
    add_step(audit, "T1:AB", DROP_V, WHY)
    add_step(audit, "T2:AB", FILTER_V, WHY)
    add_step(audit, "T2:A", FILTER_V, WHY)
    add_step(audit, "T3:p", FILTER_V, "why")
    assert [p for p in check_recipe(audit.recipe, "audit", catalogs=CATALOGS).errors] == []
    for profile in ("run", "build", "gallery"):
        codes = check_recipe(audit.recipe, profile, catalogs=CATALOGS).codes()
        assert "AU01" in codes, (profile, "audit_steps is refused outside the audit profile")
    assert check_recipe(start(base).recipe, "audit", catalogs=CATALOGS).errors == []


def test_audit_steps_in_an_ordinary_recipe_are_refused_with_one_plain_line_per_list(base):
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, WHY)
    add_step(audit, "T1:AB", DROP_V, WHY)
    problems = [p for p in check_recipe(audit.recipe, "run", catalogs=CATALOGS).errors if p.code == "AU01"]
    assert [p.path for p in problems] == ["data_schemas.A.tier1.audit_steps", "joins.AB.tier1.audit_steps"]
    assert "only an audit recipe has audit steps" in problems[0].message


def test_a_reason_or_an_audit_id_among_the_authors_steps_is_refused_in_every_profile(base):
    for profile in ("run", "build", "audit"):
        raw = copy.deepcopy(base)
        raw["data_schemas"]["B"]["tier1"]["steps"].append({**DROP_V, AUDIT_COMMENT: "why"})
        assert any(p.code == "AU01" and p.path.endswith("steps[1].audit_comment") for p in check_recipe(raw, profile, catalogs=CATALOGS).errors), profile
        raw = copy.deepcopy(base)
        raw["data_schemas"]["B"]["tier1"]["steps"].append({**DROP_V, "id": ID1})
        assert any(p.code == "ST08" for p in check_recipe(raw, profile, catalogs=CATALOGS).errors), profile
    raw = copy.deepcopy(base)
    raw["data_schemas"]["B"]["tier1"]["steps"].append({**DROP_V, "id": ID1})
    assert any("belongs in audit_steps" in p.message for p in check_recipe(raw, "audit", catalogs=CATALOGS).errors)


def test_an_audit_step_must_have_an_audit_id_a_reason_and_an_allowed_action(base):
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, WHY)
    add_step(audit, "T1:B", FILTER_V, WHY)
    holder = audit.recipe["data_schemas"]
    steps = holder["A"]["tier1"][AUDIT_STEPS]
    steps.append({**FILTER_V, AUDIT_COMMENT: WHY})                                       # no id
    steps.append({**FILTER_V, "id": "audit_nope", AUDIT_COMMENT: WHY})                   # bad id
    steps.append({**FILTER_V, "id": ID3})                                                # no reason
    steps.append({**FILTER_V, "id": "audit_00ff00ff_9", AUDIT_COMMENT: ""})              # empty reason
    steps.append({**FILTER_V, "id": "audit_00ff00ff_8", "comment": "note"})              # the reason in `comment`
    steps.append({"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left", "id": "audit_00ff00ff_7", AUDIT_COMMENT: WHY})   # not allowed
    holder["B"]["tier1"][AUDIT_STEPS][0]["id"] = ID1                                      # an id used in two tiers
    problems = check_recipe(audit.recipe, "audit", catalogs=CATALOGS).errors
    by_path = {p.path: p for p in problems}
    assert by_path["data_schemas.A.tier1.audit_steps[2].id"].code == "AU03"
    assert by_path["data_schemas.A.tier1.audit_steps[3].id"].code == "AU03" and "audit_nope" in by_path["data_schemas.A.tier1.audit_steps[3].id"].message
    assert by_path["data_schemas.A.tier1.audit_steps[4].audit_comment"].code == "AU03"
    assert by_path["data_schemas.A.tier1.audit_steps[5].audit_comment"].code == "AU03"
    assert by_path["data_schemas.A.tier1.audit_steps[6].audit_comment"].code == "AU03", "a reason in `comment` is a reason that is still missing"
    assert by_path["data_schemas.A.tier1.audit_steps[7].action"].code == "AU02"
    message = by_path["data_schemas.A.tier1.audit_steps[7].action"].message
    assert "polars_join" in message and "modif_filter" in message and "polars_drop" in message
    assert by_path["data_schemas.B.tier1.audit_steps[1].id"].code == "AU03" and "used twice" in by_path["data_schemas.B.tier1.audit_steps[1].id"].message


def test_the_authors_note_comment_is_legal_on_an_audit_step_and_never_required(base):
    audit = start(base)
    add_step(audit, "T1:A", FILTER_V, WHY)
    audit_of(audit.recipe, "A", "tier1")[0]["comment"] = "a note"
    assert check_recipe(audit.recipe, "audit", catalogs=CATALOGS).errors == []
    del audit_of(audit.recipe, "A", "tier1")[0]["comment"]
    assert check_recipe(audit.recipe, "audit", catalogs=CATALOGS).errors == []


def test_an_audit_step_is_judged_like_any_step_against_its_action(base):
    """The parameters of an audit step are checked as for every step (here a parameter that `modif_filter` does not have)."""
    audit = start(base)
    add_step(audit, "T1:A", {**FILTER_V, "nonsense": 1}, WHY)
    assert any(p.code == "ST03" and p.path.endswith("audit_steps[1].nonsense") for p in check_recipe(audit.recipe, "audit", catalogs=CATALOGS).errors)


def test_an_audit_list_that_is_not_a_list_is_refused_by_the_checker(base):
    audit = start(base)
    audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS] = "x"
    assert any(p.code == "AU03" and "is a list of steps" in p.message for p in check_recipe(audit.recipe, "audit", catalogs=CATALOGS).errors)


def test_a_tier_2_step_of_a_table_no_plot_reads_would_fail_the_checker_so_it_is_refused_before(base):
    audit = start(base)
    audit.recipe["data_schemas"]["B"]["tier2"] = {"steps": [], AUDIT_STEPS: [written(FILTER_V, ID1)]}
    assert any(p.code == "S07" for p in check_recipe(audit.recipe, "audit", catalogs=CATALOGS).errors)
    with pytest.raises(AuditCopyError, match="No plot reads 'B'"):
        add_step(start(base), "T2:B", FILTER_V, WHY)
