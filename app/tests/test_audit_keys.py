"""The keys of an audit copy: the audit parts `a1`, `a2`, `a3` (piece A5 of slice A of the HOME audit redesign; ADR-101 point 2, D-0025).

    T1 = E . rC . dC . [a1]       T2 = key(T1) . [s2] . [a2]       T3 = key(T2) . [s3] . [a3]

The marked audit steps of a copy are NOT part of the definition parts (`rC`, `s2`, `s3`): they enter as the audit parts, built from the audit
operations of that tier of that table or plot "without reasons, dates or initials" (the steps without their `id` and `comment`, in list order).
An empty part is left out. An audit step at the tier 1 of a table reaches the keys downstream of it the way an upstream definition does.

What is proved, on a staged recipe (tables A and B, a join J of them with a tier 2, a table X plotted directly with a tier 2, a plot on J, on X
and on A; the plot on A has a tier 3 of its own) and on EVERY shipped recipe:
- a copy with no audit step has exactly the keys of the original, for every table and plot;
- a step at tier 1 of a table moves the keys of that table and of everything downstream of it and no other; at tier 2 the table's tier-2 key and its
  plots; at tier 3 that plot only (the sets are read from the recipe graph, not from the code under test);
- the form of each key (the labelled parts, in order); the empty parts left out;
- a change of the reason or of the id only moves no key; a change of the operation, of its place or of the order of two steps does;
- removing the step gives the original keys back; the coarse (fail-safe) keys hold the audit steps too.

Mutation index (each seen failing, see the report): MUTATION K1 the audit parts are left out of the keys (a copy has the keys of the original).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_keys.py -q
"""
import copy
import re
from pathlib import Path

import pytest

from app.modules.cache_keys import (
    clear_data_analysis_recipe_cache, collection_tier2_key, plot_tier3_key, table_definition_for_key, table_key_parts, tier1_key)
from app.tests.test_table_keys import FILES, FILTER_A, FILTER_B, ROOT, SHIPPED, broken_graph, load_raw, recipe
from utils.audit_copy import add_step, audit_recipe_of, marked_steps, remove_step
from utils.recipe_graph import build_graph
from utils.recipe_tiers import collection_bodies, plot_entries, plot_targets

HEX = "[0-9a-f]{32}"
T1_AUDIT = re.compile(rf"^E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}$")
DROP = {"action": "polars_drop", "columns": ["group"]}
ID1, ID2, ID3 = "audit_1a2b3c4d_1", "audit_1a2b3c4d_2", "audit_00ff00ff_3"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def staged_recipe() -> dict:
    raw = recipe()
    raw["analysis_groups"]["g"]["plots"]["pa"] = {"target_dataset": "A", "mapping": {"x": "group"}, "layers": [{"name": "geom_bar", "params": {}}],
                                                  "tier3": {"steps": [FILTER_A]}}
    return raw


def all_keys(raw: dict, files=None) -> dict:
    """{node id: key} of every table (T1, T2) and every plot (T3) of a recipe, computed as `data_analysis_recipe_keys` computes them."""
    files = FILES if files is None else files
    parts, _ = table_key_parts(raw)
    found = {}
    for table, part in parts.items():
        found[f"T1:{table}"] = tier1_key(part, files)
        found[f"T2:{table}"] = collection_tier2_key(raw, table, found[f"T1:{table}"])
    for plot_id, entry in plot_entries(raw).items():
        if f"T2:{entry.get('target_dataset')}" in found:
            found[f"T3:{plot_id}"] = plot_tier3_key(raw, plot_id, found[f"T2:{entry['target_dataset']}"])
    return found


def moved(before: dict, after: dict) -> set:
    return {name for name in before if before[name] != after[name]}


def with_step(raw: dict, place: str, step=FILTER_B, step_id=ID1, comment=None) -> dict:
    audit = audit_recipe_of(raw)
    add_step(audit, place, step, step_id, comment)
    return audit


def downstream(raw: dict, node: str) -> set:
    """The node and every table node and plot that reads it, from the recipe graph."""
    graph = build_graph(raw)
    return {node} | {n for n in graph.lineage_forward(node) if n.split(":")[0] in ("T1", "T2", "T3")}


# =====================================================================================================================
# A copy with no audit step has the keys of the original
# =====================================================================================================================


def test_a_copy_with_no_audit_step_has_exactly_the_keys_of_the_original():
    raw = staged_recipe()
    assert all_keys(audit_recipe_of(raw)) == all_keys(raw)


def test_the_marked_audit_steps_are_out_of_the_definition_of_a_table():
    raw = staged_recipe()
    audit = with_step(raw, "T1:A")
    assert table_definition_for_key(audit["data_schemas"]["A"]) == table_definition_for_key(raw["data_schemas"]["A"])


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_on_every_shipped_recipe_a_copy_with_no_audit_step_has_the_keys_of_the_original(path):
    raw = load_raw(path)
    if not raw:
        pytest.skip("the file holds no recipe")
    files = {ds: f"hash-{ds}" for ds in collection_bodies(raw)}
    audit = audit_recipe_of(raw)
    assert marked_steps(audit) == []
    assert all_keys(audit, files) == all_keys(raw, files)
    assert table_key_parts(audit) == table_key_parts(raw)


# =====================================================================================================================
# Which keys a step moves, on the staged recipe
# =====================================================================================================================

MOVES = {
    "T1:A": {"T1:A", "T2:A", "T1:J", "T2:J", "T3:pj", "T3:pa"},
    "T1:B": {"T1:B", "T2:B", "T1:J", "T2:J", "T3:pj"},
    "T1:J": {"T1:J", "T2:J", "T3:pj"},
    "T1:X": {"T1:X", "T2:X", "T3:px"},
    "T2:A": {"T2:A", "T3:pa"},
    "T2:J": {"T2:J", "T3:pj"},
    "T2:X": {"T2:X", "T3:px"},
    "T3:pj": {"T3:pj"},
    "T3:pa": {"T3:pa"},
    "T3:px": {"T3:px"},
}


@pytest.mark.parametrize("place", sorted(MOVES))
def test_a_step_moves_the_keys_after_it_and_no_other(place):
    """MUTATION K1: with the audit parts left out of the keys nothing moves and every case fails."""
    raw = staged_recipe()
    base = all_keys(raw)
    assert moved(base, all_keys(with_step(raw, place))) == MOVES[place]


def test_the_sets_of_the_staged_recipe_are_the_ones_the_recipe_graph_gives():
    raw = staged_recipe()
    for place, expected in MOVES.items():
        assert expected == downstream(raw, place), place


def test_a_step_at_tier_1_of_a_table_reaches_the_join_that_reads_it_as_an_upstream_definition_does():
    """The reach of `a1` is that of `rC`: the join's key moves for a step at either ingredient and at the join itself, and an unrelated table's does not."""
    raw = staged_recipe()
    changed_definition = copy.deepcopy(raw)
    changed_definition["data_schemas"]["A"]["tier1"]["steps"] = [FILTER_B]
    audit = with_step(raw, "T1:A")
    assert moved(all_keys(raw), all_keys(changed_definition)) == moved(all_keys(raw), all_keys(audit))


# =====================================================================================================================
# The form of a key
# =====================================================================================================================


def test_the_audit_part_of_tier_1_comes_after_the_data_part_and_only_when_there_is_a_step():
    raw = staged_recipe()
    keys = all_keys(with_step(raw, "T1:A"))
    assert T1_AUDIT.match(keys["T1:A"]) and T1_AUDIT.match(keys["T1:J"])
    assert not T1_AUDIT.match(keys["T1:B"]) and not T1_AUDIT.match(keys["T1:X"])
    assert keys["T1:A"].startswith(all_keys(raw)["T1:A"] + ".a1-")


def test_the_audit_part_of_tier_2_comes_after_s2_and_alone_when_the_table_has_no_tier_2_steps_of_its_own():
    raw = staged_recipe()
    keys = all_keys(with_step(raw, "T2:J"))
    base = all_keys(raw)
    assert re.fullmatch(rf"{re.escape(base['T2:J'])}\.a2-{HEX}", keys["T2:J"]), "after the s2 part"
    assert keys["T1:J"] == base["T1:J"], "a tier-2 step moves no tier-1 key"
    alone = all_keys(with_step(raw, "T2:A"))
    assert re.fullmatch(rf"{re.escape(base['T1:A'])}\.a2-{HEX}", alone["T2:A"]), "no s2 part: a2 follows the tier-1 key"


def test_the_audit_part_of_tier_3_comes_after_s3_and_after_a_tier_2_audit_part():
    raw = staged_recipe()
    base = all_keys(raw)
    assert re.fullmatch(rf"{re.escape(base['T3:pa'])}\.a3-{HEX}", all_keys(with_step(raw, "T3:pa"))["T3:pa"])
    alone = all_keys(with_step(raw, "T3:pj"))["T3:pj"]
    assert re.fullmatch(rf"{re.escape(base['T3:pj'])}\.a3-{HEX}", alone), "no s3 part: a3 follows the key of the table"
    every = audit_recipe_of(raw)
    add_step(every, "T1:A", FILTER_B, ID1)
    add_step(every, "T2:A", FILTER_B, ID2)
    add_step(every, "T3:pa", FILTER_B, ID3)
    key = all_keys(every)["T3:pa"]
    assert re.fullmatch(rf"E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}\.a2-{HEX}\.s3-{HEX}\.a3-{HEX}", key), key
    assert re.fullmatch(rf"E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}\.a2-{HEX}", all_keys(every)["T2:A"])


def test_every_part_is_128_bits_and_the_order_is_the_execution_order_with_both_tiers_written():
    raw = staged_recipe()
    audit = audit_recipe_of(raw)
    add_step(audit, "T1:J", FILTER_B, ID1)
    add_step(audit, "T2:J", FILTER_B, ID2)
    key = all_keys(audit)["T2:J"]
    assert re.fullmatch(rf"E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}\.s2-{HEX}\.a2-{HEX}", key), key


# =====================================================================================================================
# What the audit part is made of
# =====================================================================================================================


def test_a_change_of_the_reason_or_of_the_id_only_moves_no_key():
    raw = staged_recipe()
    one = with_step(raw, "T1:A", comment="first reason")
    other = copy.deepcopy(one)
    step = other["data_schemas"]["A"]["tier1"]["steps"][-1]
    step["comment"] = "an entirely different reason"
    step["id"] = "audit_ffffffff_42"
    assert all_keys(one) == all_keys(other)
    del step["comment"]
    assert all_keys(one) == all_keys(other), "a step with no reason has the same keys as one with a reason"


@pytest.mark.parametrize("place", sorted(MOVES))
def test_a_change_of_the_operation_moves_the_same_keys(place):
    raw = staged_recipe()
    first, second = with_step(raw, place, FILTER_A), with_step(raw, place, FILTER_B)
    assert moved(all_keys(first), all_keys(second)) == MOVES[place]


def test_the_place_is_part_of_the_key_the_same_step_at_two_places_is_two_keys():
    raw = staged_recipe()
    assert all_keys(with_step(raw, "T1:A"))["T1:A"] != all_keys(with_step(raw, "T1:B"))["T1:B"]
    assert all_keys(with_step(raw, "T2:J"))["T2:J"] != all_keys(with_step(raw, "T3:pj"))["T3:pj"]
    one, other = all_keys(with_step(raw, "T1:A")), all_keys(with_step(raw, "T2:A"))
    assert one["T2:A"] != other["T2:A"], "the same step at tier 1 and at tier 2 of a table is not the same table"


def test_the_order_of_two_audit_steps_matters_and_two_steps_are_not_one():
    raw = staged_recipe()
    forward, backward, single = audit_recipe_of(raw), audit_recipe_of(raw), with_step(raw, "T1:A", FILTER_B)
    add_step(forward, "T1:A", FILTER_B, ID1)
    add_step(forward, "T1:A", DROP, ID2)
    add_step(backward, "T1:A", DROP, ID2)
    add_step(backward, "T1:A", FILTER_B, ID1)
    keys = [all_keys(x)["T1:A"] for x in (forward, backward, single)]
    assert len(set(keys)) == 3


def test_an_audit_step_and_an_original_step_that_look_alike_are_not_the_same_key():
    """The same operation written by the recipe's author (in the definition, `rC`) and added by the audit (`a1`) give different keys: the audit is
    visible in the key."""
    raw = staged_recipe()
    written = copy.deepcopy(raw)
    written["data_schemas"]["A"]["tier1"]["steps"].append(FILTER_B)
    assert all_keys(written)["T1:A"] != all_keys(with_step(raw, "T1:A", FILTER_B))["T1:A"]


def test_the_engine_of_the_tier_is_an_argument_of_the_audit_part_of_tier_2_and_tier_3():
    raw = staged_recipe()
    audit = audit_recipe_of(raw)
    add_step(audit, "T2:A", FILTER_B, ID1)
    add_step(audit, "T3:pj", FILTER_B, ID2)
    other = copy.deepcopy(audit)
    other["data_schemas"]["A"]["tier2"]["data_engine"] = "engine-x"
    other["analysis_groups"]["g"]["plots"]["pj"]["tier3"]["data_engine"] = "engine-y"
    moves = moved(all_keys(audit), all_keys(other))
    assert {"T2:A", "T3:pa", "T3:pj"} <= moves


# =====================================================================================================================
# Remove, and the fail-safe keys
# =====================================================================================================================


@pytest.mark.parametrize("place", sorted(MOVES))
def test_removing_the_step_gives_the_original_keys_back(place):
    raw = staged_recipe()
    audit = with_step(raw, place)
    assert all_keys(audit) != all_keys(raw)
    remove_step(audit, ID1)
    assert all_keys(audit) == all_keys(raw)


def test_a_recipe_the_graph_cannot_draw_has_coarse_keys_that_hold_the_audit_steps_too():
    """The fail-safe form (ADR-101 point 3): the definition is the whole recipe; the audit part is that of every table."""
    raw = broken_graph()
    assert all(p.coarse for p in table_key_parts(raw)[0].values())
    base = all_keys(raw)
    for place in ("T1:A", "T1:B", "T1:X", "T1:J"):
        audit = with_step(raw, place)
        assert moved(base, all_keys(audit)) >= {f"T1:{t}" for t in ("A", "B", "X", "J")}, "a coarse key holds every table's audit steps"
        assert all(T1_AUDIT.match(all_keys(audit)[f"T1:{t}"]) for t in ("A", "B", "X", "J"))
    assert all_keys(audit_recipe_of(raw)) == base
    first, second = with_step(raw, "T1:A", FILTER_A), with_step(raw, "T1:A", FILTER_B)
    assert all_keys(first) != all_keys(second)


# =====================================================================================================================
# Every shipped recipe: the sets of moved keys are the ones of the recipe graph
# =====================================================================================================================


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_on_every_shipped_recipe_a_step_moves_the_keys_after_it_and_no_other(path):
    raw = load_raw(path)
    if not raw:
        pytest.skip("the file holds no recipe")
    files = {ds: f"hash-{ds}" for ds in collection_bodies(raw)}
    base = all_keys(raw, files)
    places = [f"T1:{t}" for t in collection_bodies(raw)]
    places += [f"T2:{t}" for t in sorted(plot_targets(raw)) if t in collection_bodies(raw)]
    places += [f"T3:{p}" for p in plot_entries(raw)]
    for place in places:
        audit = with_step(raw, place)
        expected = {n for n in downstream(raw, place) if n in base}
        assert moved(base, all_keys(audit, files)) == expected, place
        remove_step(audit, ID1)
        assert all_keys(audit, files) == base, f"{place}: removing the step gives the original keys back"


# =====================================================================================================================
# The position of a marked step among the original steps is in the audit part (F1)
# =====================================================================================================================


def _tier_steps(audit: dict, place: str) -> list:
    kind, name = place.split(":")
    body = plot_entries(audit)[name] if kind == "T3" else collection_bodies(audit)[name]
    return body[f"tier{kind[1]}"]["steps"]


def _with_marked_at(raw: dict, place: str, index: int, step_id=ID1) -> dict:
    """A copy that was NOT built with `add_step` (a later caller that did not check it): the marked step is written at `index` of its list."""
    audit = audit_recipe_of(raw)
    _tier_steps(audit, place).insert(index, {**FILTER_B, "id": step_id})
    return audit


def _staged_with_original_steps() -> dict:
    raw = staged_recipe()
    raw["data_schemas"]["A"]["tier1"]["steps"] = [DROP]
    raw["joins"]["J"]["tier1"] = {"steps": [DROP]}
    return raw


@pytest.mark.parametrize("place", ["T1:A", "T1:J", "T2:J", "T3:pa"])
def test_a_marked_step_before_an_original_step_and_the_same_step_after_it_give_different_keys(place):
    """MUTATION F1: with the position left out of the audit part the two copies have one key. Tier 1, tier 2 and tier 3 are all covered."""
    raw = _staged_with_original_steps()
    assert len(_tier_steps(raw, place)) >= 1, "the list has an original step to stand before or after"
    before = all_keys(_with_marked_at(raw, place, 0))
    after = all_keys(_with_marked_at(raw, place, len(_tier_steps(raw, place))))
    assert before[place] != after[place]
    assert moved(before, after) >= {place}


def test_a_marked_step_in_the_middle_of_an_upstream_table_moves_the_downstream_keys_too():
    raw = _staged_with_original_steps()
    before = all_keys(_with_marked_at(raw, "T1:A", 0))
    after = all_keys(_with_marked_at(raw, "T1:A", 1))
    assert moved(before, after) == MOVES["T1:A"]


def test_the_position_is_the_number_of_original_steps_before_the_marked_step():
    raw = _staged_with_original_steps()
    raw["data_schemas"]["A"]["tier1"]["steps"] = [DROP, FILTER_A]
    keys = [all_keys(_with_marked_at(raw, "T1:A", i))["T1:A"] for i in (0, 1, 2)]
    assert len(set(keys)) == 3


def test_two_marked_steps_keep_their_order_and_their_places_among_the_original_steps():
    raw = _staged_with_original_steps()

    def two(order, at):
        audit = audit_recipe_of(raw)
        steps = _tier_steps(audit, "T1:A")
        for offset, (step_id, step) in enumerate(order):
            steps.insert(at[offset] + offset, {**step, "id": step_id})
        return all_keys(audit)["T1:A"]

    ab = [(ID1, FILTER_A), (ID2, FILTER_B)]
    assert two(ab, [1, 1]) != two(ab[::-1], [1, 1]), "order among marked steps matters"
    assert two(ab, [0, 1]) != two(ab, [1, 1]), "a marked step moved before an original step"


def test_with_every_marked_step_at_the_end_the_reason_and_the_id_move_no_key_and_removing_gives_the_original_back():
    raw = _staged_with_original_steps()
    base = all_keys(raw)
    for place in MOVES:
        one = all_keys(with_step(raw, place, step_id=ID1, comment="a"))
        assert one == all_keys(with_step(raw, place, step_id=ID3, comment="another reason")), place
        audit = with_step(raw, place)
        remove_step(audit, ID1)
        assert all_keys(audit) == base, place
