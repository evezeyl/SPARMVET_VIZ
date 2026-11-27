"""The pure rules of ADDING a tried audit step (FLOW-2; `app/modules/audit_add.py`; ledger D-0662, D-0669, D-0670, D-0672), and the records the export draws from the added nodes.

What it proves, in words a person can check:
- the button "Add to audit pipeline" is enabled only with a reason that is not empty or only spaces, and when it is not, one plain line says why (never a silent grey);
- the summary reads "N of M places user verified" (D-0670), and the notice after Add says how many places and how many were marked;
- the added nodes are the tried nodes with `user_verified` (True only for a place that was marked, with the time of the mark) and nothing else changed; ALL the places stay (D-0669: also the
  places not marked); the marks never reach what decides the data (`nodes_signature`: the keys of the audit copy do not move);
- a card says "User verified" or "not marked as verified" for a step that carries the field and says nothing for a step of the old way;
- the export's records carry the mark and the sentences say, for each decision, how many places were marked and which were not; an old step has no sentence.

Mutation index (each seen failing): MUTATION A1 `stamp_marks` marks every place; MUTATION A2 `can_add` accepts only spaces; MUTATION A3 `stamp_marks` drops the places that are not marked.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_add.py -q

# @deps
# consumes: app/modules/audit_add.py, app/modules/audit_places.py (nodes_signature, place_step_records), utils.recipe_graph
# doc: .claude/knowledge/decision_ledger.md (D-0669, D-0670, D-0672)
# @end_deps
"""
import copy
import json

import pytest

from app.modules.audit_add import (ADD_LABEL, NOT_MARKED, REASON_NEEDED_LINE, VERIFIED_LABEL, added_notice, can_add, marks_summary, stamp_marks, verification_sentences, verified_card_line)
from app.modules.audit_places import PLACES_BUCKET, nodes_signature, place_step_records
from app.modules.session_manager import make_audit_step
from utils.recipe_graph import build_graph


def node(place, node_id="d1", value=90):
    return make_audit_step("filter_row", {"column": "identity", "op": "lt", "value": value, "na": "remove"}, plot_scope=PLACES_BUCKET, reason="why", place=place, node_id=node_id)


PLACES = ["T1:ResFinder", "T2:ResFinder", "T3:amr_heatmap"]


def test_the_labels_are_the_decided_words():
    assert ADD_LABEL == "Add to audit pipeline" and VERIFIED_LABEL == "User verified"


@pytest.mark.parametrize("reason", ["", "   ", "\n\t ", None])
def test_add_is_disabled_without_a_reason_and_a_line_says_why(reason):
    ok, why = can_add(reason)
    assert ok is False and why == REASON_NEEDED_LINE and "reason" in why


@pytest.mark.parametrize("reason", ["x", "  poor quality  ", "é"])
def test_add_is_enabled_with_any_text_that_is_not_only_spaces(reason):
    assert can_add(reason) == (True, "")


def test_the_summary_is_n_of_m_places_user_verified():
    assert marks_summary(2, 3) == "2 of 3 places user verified"
    assert marks_summary(0, 3) == "0 of 3 places user verified"
    assert marks_summary(1, 1) == "1 of 1 place user verified"


def test_the_notice_after_add_says_the_places_and_the_marks():
    assert added_notice(3, 2) == "Step added to the audit pipeline at 3 places (2 of 3 places user verified)."
    assert added_notice(1, 0) == "Step added to the audit pipeline at 1 place (0 of 1 place user verified)."


def test_marks_are_stamped_on_the_added_nodes_and_all_the_places_stay():
    nodes = [node(p) for p in PLACES]
    before = copy.deepcopy(nodes)
    stamped = stamp_marks(nodes, {"T1:ResFinder": "2026-11-27T09:00:00", "T3:amr_heatmap": "2026-11-27T09:01:00"})
    assert nodes == before, "the argument is not changed"
    assert [n["place"] for n in stamped] == PLACES, "D-0669: written at ALL the places, also the one not marked"
    assert [n["user_verified"] for n in stamped] == [True, False, True]
    assert stamped[0]["verified_at"] == "2026-11-27T09:00:00" and "verified_at" not in stamped[1] and stamped[2]["verified_at"] == "2026-11-27T09:01:00"
    for old, new in zip(nodes, stamped):
        assert {k: v for k, v in new.items() if k not in ("user_verified", "verified_at")} == old, "nothing else of a node changed"


def test_a_mark_never_moves_what_decides_the_data():
    nodes = [node(p) for p in PLACES]
    assert nodes_signature(stamp_marks(nodes, {"T1:ResFinder": "t"})) == nodes_signature(nodes) == nodes_signature(stamp_marks(nodes, {})), "the keys of the audit copy do not read the mark"


def test_a_stale_mark_in_a_node_is_replaced_not_kept():
    stale = {**node("T1:ResFinder"), "user_verified": True, "verified_at": "old"}
    assert stamp_marks([stale], {})[0] == {**node("T1:ResFinder"), "user_verified": False, "id": stale["id"], "created_at": stale["created_at"]}


def test_nothing_marked_and_nothing_to_add_are_the_empty_cases():
    assert stamp_marks([], {"T1:ResFinder": "t"}) == []
    assert all(n["user_verified"] is False for n in stamp_marks([node(p) for p in PLACES], {}))


def test_the_card_line_for_a_step_that_carries_the_field_and_silence_for_the_old_way():
    marked, unmarked = stamp_marks([node("T1:ResFinder"), node("T2:ResFinder")], {"T1:ResFinder": "t"})
    assert verified_card_line(marked) == "User verified"
    assert verified_card_line(unmarked) == NOT_MARKED == "not marked as verified"
    assert verified_card_line(node("T1:ResFinder")) is None, "a step of the old way says nothing about it"


@pytest.fixture(scope="module")
def graph():
    from pathlib import Path
    from app.modules.cache_keys import load_data_analysis_recipe
    return build_graph(load_data_analysis_recipe(Path(__file__).resolve().parents[2] / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml").raw)


def test_the_export_records_carry_the_mark_only_for_a_step_that_has_it(graph):
    added = stamp_marks([node(p, "d1") for p in PLACES], {"T1:ResFinder": "2026-11-27T09:00:00"})
    old = node("T1:ResFinder", "old1")
    records = place_step_records(graph, added + [old])
    assert [r.get("user_verified") for r in records] == [True, False, False, None]
    assert "user_verified" not in records[3] and records[0]["verified_at"] == "2026-11-27T09:00:00" and "verified_at" not in records[1]
    json.dumps(records)    # plain data: it goes to a YAML file as it is


def test_the_sentences_name_how_many_places_were_marked_and_which_were_not(graph):
    added = stamp_marks([node(p, "d1") for p in PLACES], {"T1:ResFinder": "t", "T2:ResFinder": "t"})
    sentences = verification_sentences(place_step_records(graph, added))
    assert len(sentences) == 1, "one sentence for one decision, however many places"
    assert "2 of 3 places user verified" in sentences[0] and "not marked:" in sentences[0] and "amr_heatmap" in sentences[0] and "identity" in sentences[0]


def test_every_place_marked_has_no_not_marked_part_and_an_old_step_has_no_sentence(graph):
    every = stamp_marks([node(p, "d1") for p in PLACES], {p: "t" for p in PLACES})
    assert verification_sentences(place_step_records(graph, every)) == ["Step filter_row (column=identity; op=lt; value=90): 3 of 3 places user verified."]
    assert verification_sentences(place_step_records(graph, [node("T1:ResFinder", "old1")])) == []
    assert verification_sentences([]) == []


def test_two_decisions_make_two_sentences_in_the_order_added(graph):
    a = stamp_marks([node("T1:ResFinder", "d1", 90)], {"T1:ResFinder": "t"})
    b = stamp_marks([node("T1:ResFinder", "d2", 50)], {})
    sentences = verification_sentences(place_step_records(graph, a + b))
    assert len(sentences) == 2 and "value=90" in sentences[0] and "1 of 1 place user verified" in sentences[0] and "value=50" in sentences[1] and "0 of 1 place user verified" in sentences[1]
