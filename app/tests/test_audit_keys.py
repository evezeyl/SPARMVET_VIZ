"""The keys of an audit copy: the audit parts `a1`, `a2`, `a3` (piece A5 of slice A, changed over to the second list `audit_steps` in piece C-1 of slice C of
the HOME audit redesign; ADR-101 point 2, D-0025, D-0332).

    T1 = E . rC . dC . [a1]       T2 = key(T1) . [s2] . [a2]       T3 = key(T2) . [s3] . [a3]

The `audit_steps` lists of a copy are NOT part of the definition parts (`rC`, `s2`, `s3`: they hold the author's lists only): they enter as the audit parts,
built from the audit operations of that tier of that table or plot "without reasons, dates or initials" (the steps without their `id`, `audit_comment` and
`comment`, in list order). An empty part is left out. An audit step at the tier 1 of a table reaches the keys downstream of it the way an upstream definition does.
There is no position in a part: an audit step always runs after every author's step of its tier, so the position is never a difference between two copies.

What is proved, on a staged recipe (tables A and B, a join J of them with a tier 2, a table X plotted directly with a tier 2, a plot on J, on X
and on A; the plot on A has a tier 3 of its own) and on EVERY shipped recipe:
- a copy with no audit step, or with an EMPTY `audit_steps` in every tier, has exactly the keys of the original, for every table and plot;
- a step at tier 1 of a table moves the keys of that table and of everything downstream of it and no other; at tier 2 the table's tier-2 key and its
  plots; at tier 3 that plot only (the sets are read from the recipe graph, not from the code under test);
- the form of each key (the labelled parts, in order); the empty parts left out;
- a change of the reason, of the id or of the author's note only moves no key; a change of the operation, of its place or of the order of two steps does;
- two different audits never share a key (a pool of audits, the keys of every node compared);
- computing the keys never changes the copy (a reason is never lost on the way); removing the step gives the original keys back; the coarse (fail-safe)
  keys hold the audit steps too.

Mutation index (each seen failing, see the report): MUTATION K1 the audit parts are left out of the keys (a copy has the keys of the original); K2 `audit_steps`
is left IN the definition of a table (a copy with an empty list has other keys than its original).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_keys.py -q
"""
import copy
import re
from pathlib import Path

import pytest

from app.modules.cache_keys import (
    clear_data_analysis_recipe_cache, collection_tier2_key, plot_tier3_key, table_definition_for_key, table_key_parts, tier1_key)
from app.tests.test_table_keys import FILES, FILTER_A, FILTER_B, ROOT, SHIPPED, broken_graph, load_raw, recipe
from utils.audit_copy import AuditCopyError, add_step, all_audit_steps, remove_step, start_audit
from utils.recipe_graph import build_graph
from utils.recipe_tiers import AUDIT_COMMENT, AUDIT_STEPS, collection_bodies, plot_entries, plot_targets

HEX = "[0-9a-f]{32}"
T1_AUDIT = re.compile(rf"^E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}$")
DROP = {"action": "polars_drop", "columns": ["group"]}
AUD = "1a2b3c4d"
ID1, ID2, ID3 = f"audit_{AUD}_1", f"audit_{AUD}_2", f"audit_{AUD}_3"
WHY = "the reason"


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


def with_step(raw: dict, place: str, step=FILTER_B, comment=WHY) -> dict:
    """The audit copy (a dictionary) of the recipe with ONE audit step at `place`."""
    audit = start_audit(raw, AUD)
    add_step(audit, place, step, comment)
    return audit.recipe


def with_steps(raw: dict, *added) -> dict:
    """The audit copy with the steps `(place, step)` added in that order."""
    audit = start_audit(raw, AUD)
    for place, step in added:
        add_step(audit, place, step, WHY)
    return audit.recipe


def with_empty_audit_lists(raw: dict) -> dict:
    """The recipe with an empty `audit_steps` written in every tier of every table, join and plot (an audit that has not added a step, or took them all out)."""
    out = copy.deepcopy(raw)
    for body in list(collection_bodies(out).values()) + list(plot_entries(out).values()):
        for tier in ("tier1", "tier2", "tier3"):
            if isinstance(body.get(tier), dict):
                body[tier][AUDIT_STEPS] = []
    return out


def downstream(raw: dict, node: str) -> set:
    """The node and every table node and plot that reads it, from the recipe graph."""
    graph = build_graph(raw)
    return {node} | {n for n in graph.lineage_forward(node) if n.split(":")[0] in ("T1", "T2", "T3")}


# =====================================================================================================================
# A copy with no audit step has the keys of the original
# =====================================================================================================================


def test_a_copy_with_no_audit_step_has_exactly_the_keys_of_the_original():
    raw = staged_recipe()
    assert all_keys(start_audit(raw, AUD).recipe) == all_keys(raw)


def test_a_copy_with_an_empty_audit_list_in_every_tier_has_exactly_the_keys_of_the_original():
    """MUTATION K2: with `audit_steps` left in the definition of a table, or an empty list counted as a part, the keys move."""
    raw = staged_recipe()
    empty = with_empty_audit_lists(raw)
    assert empty != raw and sum(1 for _ in plot_entries(empty)) >= 3
    assert all_keys(empty) == all_keys(raw)
    assert table_key_parts(empty) == table_key_parts(raw)


def test_the_audit_steps_are_out_of_the_definition_of_a_table():
    raw = staged_recipe()
    audit = with_step(raw, "T1:A")
    assert AUDIT_STEPS in audit["data_schemas"]["A"]["tier1"]
    assert table_definition_for_key(audit["data_schemas"]["A"]) == table_definition_for_key(raw["data_schemas"]["A"])
    assert AUDIT_STEPS not in table_definition_for_key(audit["data_schemas"]["A"])["tier1"]


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_on_every_shipped_recipe_a_copy_with_no_audit_step_has_the_keys_of_the_original(path):
    raw = load_raw(path)
    if not raw:
        pytest.skip("the file holds no recipe")
    files = {ds: f"hash-{ds}" for ds in collection_bodies(raw)}
    audit = start_audit(raw, AUD).recipe
    assert all_audit_steps(audit) == []
    assert all_keys(audit, files) == all_keys(raw, files)
    assert table_key_parts(audit) == table_key_parts(raw)
    empty = with_empty_audit_lists(raw)
    assert all_keys(empty, files) == all_keys(raw, files), "an empty audit_steps in every tier changes no key"
    assert table_key_parts(empty) == table_key_parts(raw)


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
    every = with_steps(raw, ("T1:A", FILTER_B), ("T2:A", FILTER_B), ("T3:pa", FILTER_B))
    key = all_keys(every)["T3:pa"]
    assert re.fullmatch(rf"E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}\.a2-{HEX}\.s3-{HEX}\.a3-{HEX}", key), key
    assert re.fullmatch(rf"E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}\.a2-{HEX}", all_keys(every)["T2:A"])


def test_every_part_is_128_bits_and_the_order_is_the_execution_order_with_both_tiers_written():
    raw = staged_recipe()
    audit = with_steps(raw, ("T1:J", FILTER_B), ("T2:J", FILTER_B))
    key = all_keys(audit)["T2:J"]
    assert re.fullmatch(rf"E-{HEX}\.rC-{HEX}\.dC-{HEX}\.a1-{HEX}\.s2-{HEX}\.a2-{HEX}", key), key


# =====================================================================================================================
# What the audit part is made of
# =====================================================================================================================


def test_a_change_of_the_reason_of_the_id_or_of_a_note_only_moves_no_key():
    raw = staged_recipe()
    one = with_step(raw, "T1:A", comment="first reason")
    other = copy.deepcopy(one)
    step = other["data_schemas"]["A"]["tier1"][AUDIT_STEPS][-1]
    step[AUDIT_COMMENT] = "an entirely different reason"
    step["id"] = "audit_ffffffff_42"
    assert all_keys(one) == all_keys(other)
    step["comment"] = "a note of the author"
    assert all_keys(one) == all_keys(other), "a note changes no data, so no key"


def test_computing_the_keys_never_changes_the_copy_so_a_reason_is_never_lost_on_the_way():
    raw = staged_recipe()
    audit = with_steps(raw, ("T1:A", FILTER_B), ("T2:J", FILTER_A), ("T3:pa", DROP))
    before = copy.deepcopy(audit)
    all_keys(audit)
    table_key_parts(audit)
    table_definition_for_key(audit["data_schemas"]["A"])
    assert audit == before
    assert [s.step[AUDIT_COMMENT] for s in all_audit_steps(audit)] == [WHY] * 3


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
    forward = with_steps(raw, ("T1:A", FILTER_B), ("T1:A", DROP))
    backward = with_steps(raw, ("T1:A", DROP), ("T1:A", FILTER_B))
    single = with_step(raw, "T1:A", FILTER_B)
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
    audit = with_steps(raw, ("T2:A", FILTER_B), ("T3:pj", FILTER_B))
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
    audit = start_audit(raw, AUD)
    add_step(audit, place, FILTER_B, WHY)
    assert all_keys(audit.recipe) != all_keys(raw)
    remove_step(audit, ID1)
    assert all_keys(audit.recipe) == all_keys(raw)


def test_a_recipe_the_graph_cannot_draw_has_coarse_keys_that_hold_the_audit_steps_too():
    """The fail-safe form (ADR-101 point 3): the definition is the whole recipe; the audit part is that of every table."""
    raw = broken_graph()
    assert all(p.coarse for p in table_key_parts(raw)[0].values())
    base = all_keys(raw)
    for place in ("T1:A", "T1:B", "T1:X", "T1:J"):
        audit = with_step(raw, place)
        assert moved(base, all_keys(audit)) >= {f"T1:{t}" for t in ("A", "B", "X", "J")}, "a coarse key holds every table's audit steps"
        assert all(T1_AUDIT.match(all_keys(audit)[f"T1:{t}"]) for t in ("A", "B", "X", "J"))
    assert all_keys(start_audit(raw, AUD).recipe) == base
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
    # D-0632: the metadata table is not an audit place, so it is left out of the places walked
    places = [f"T1:{t}" for t in collection_bodies(raw) if t != "metadata_schema"]
    places += [f"T2:{t}" for t in sorted(plot_targets(raw)) if t in collection_bodies(raw) and t != "metadata_schema"]
    places += [f"T3:{p}" for p in plot_entries(raw)]
    for place in places:
        audit = start_audit(raw, AUD)
        add_step(audit, place, FILTER_B, WHY)
        expected = {n for n in downstream(raw, place) if n in base}
        assert moved(base, all_keys(audit.recipe, files)) == expected, place
        remove_step(audit, ID1)
        assert all_keys(audit.recipe, files) == base, f"{place}: removing the step gives the original keys back"


# =====================================================================================================================
# Two audits never share a key, and the order inside a tier is the engine's: the author's steps, then the audit's
# =====================================================================================================================


def _staged_with_original_steps() -> dict:
    raw = staged_recipe()
    raw["data_schemas"]["A"]["tier1"]["steps"] = [DROP]
    raw["joins"]["J"]["tier1"] = {"steps": [DROP]}
    return raw


def _signature(audit: dict) -> tuple:
    """What an audit adds, as a comparable value: for every place the list of its audit operations in order (no id, no reason)."""
    return tuple((s.place, tuple(sorted((k, repr(v)) for k, v in s.step.items() if k not in ("id", AUDIT_COMMENT)))) for s in all_audit_steps(audit))


def test_two_different_audits_never_share_a_key():
    """The key says which audit steps the table has: the operations, their places and their order. A pool of audits over a recipe that has author's steps in the
    same tiers; every pair that differs in what it adds differs in at least one key, and equal additions give equal keys (the keys are not about the audit's id)."""
    raw = _staged_with_original_steps()
    pool = [
        [("T1:A", FILTER_A)], [("T1:A", FILTER_B)], [("T1:A", DROP)], [("T1:B", FILTER_A)], [("T1:J", FILTER_A)], [("T2:J", FILTER_A)], [("T2:A", FILTER_A)],
        [("T3:pa", FILTER_A)], [("T1:A", FILTER_A), ("T1:A", FILTER_B)], [("T1:A", FILTER_B), ("T1:A", FILTER_A)], [("T1:A", FILTER_A), ("T2:A", FILTER_A)],
        [("T1:A", FILTER_A), ("T1:B", FILTER_A)], [("T1:A", FILTER_A), ("T1:A", FILTER_A)], [],
    ]
    audits = [with_steps(raw, *added) for added in pool]
    assert all_keys(audits[-1]) == all_keys(raw)
    seen = {}
    for audit in audits:
        key = tuple(sorted(all_keys(audit).items()))
        signature = _signature(audit)
        if signature in seen:
            assert seen[signature] == key
        seen[signature] = key
    assert len(set(seen.values())) == len(seen), "two different audits gave the same keys"
    elsewhere = start_audit(raw, "ffffffff")
    add_step(elsewhere, "T1:A", FILTER_A, "another reason")
    assert all_keys(elsewhere.recipe) == all_keys(with_step(raw, "T1:A", FILTER_A)), "the audit id and the reason are in no key"


@pytest.mark.parametrize("place", ["T1:A", "T1:J", "T2:J", "T3:pa"])
def test_an_operation_written_by_the_author_at_the_end_of_a_list_and_the_same_one_added_by_the_audit_are_two_keys(place):
    """The same operation in the author's list (in the definition) and in the audit list is two different recipes for the audit (the audit is visible in
    the key), and the author's list and the audit list are in different parts: there is no position to confuse."""
    raw = _staged_with_original_steps()
    written = copy.deepcopy(raw)
    kind, name = place.split(":")
    holder = plot_entries(written)[name] if kind == "T3" else collection_bodies(written)[name]
    holder.setdefault(f"tier{kind[1]}", {"steps": []})["steps"].append(FILTER_B)
    assert all_keys(written)[place] != all_keys(with_step(raw, place, FILTER_B))[place]


def test_a_step_moved_from_the_authors_list_to_the_audit_list_is_another_key():
    raw = _staged_with_original_steps()
    moved_copy = copy.deepcopy(raw)
    moved_copy["data_schemas"]["A"]["tier1"]["steps"] = []
    moved_copy["data_schemas"]["A"]["tier1"][AUDIT_STEPS] = [{**DROP, "id": ID1, AUDIT_COMMENT: WHY}]
    assert all_keys(moved_copy)["T1:A"] != all_keys(raw)["T1:A"]
    assert all_keys(moved_copy)["T1:A"] != all_keys(start_audit(raw, AUD).recipe)["T1:A"]


def test_with_the_author_steps_in_place_the_reason_and_the_id_move_no_key_and_removing_gives_the_original_back():
    raw = _staged_with_original_steps()
    base = all_keys(raw)
    for place in MOVES:
        one = all_keys(with_step(raw, place, comment="a"))
        assert one == all_keys(with_step(raw, place, comment="another reason")), place
        audit = start_audit(raw, AUD)
        add_step(audit, place, FILTER_B, WHY)
        remove_step(audit, ID1)
        assert all_keys(audit.recipe) == base, place


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_on_every_shipped_recipe_add_then_remove_gives_back_exactly_the_copy_at_every_place(path):
    """A tier that existed before the add stays, a tier the add created goes, at every place `add_step` accepts a step."""
    raw = load_raw(path)
    if not raw:
        pytest.skip("the file holds no recipe")
    places = [f"T1:{t}" for t in collection_bodies(raw)] + [f"T2:{t}" for t in collection_bodies(raw)] + [f"T3:{p}" for p in plot_entries(raw)]
    done = 0
    for place in places:
        audit = start_audit(raw, AUD)
        try:
            add_step(audit, place, FILTER_B, WHY)
        except AuditCopyError:
            continue
        remove_step(audit, ID1)
        assert audit.recipe == raw, place
        done += 1
    assert done >= 1 or not places
