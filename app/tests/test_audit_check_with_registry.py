"""The checker's audit profile run with the REAL registries of the app (D-0332, D-0322, D-0297; piece C-1, reviewer's points 2 and 3).

The unit tests of `utils` drive the checker with a hand-made catalog. These drive it with `checker_catalogs()` (every registered action) and the recipe graph of
`_graph_of`, as HOME's gate does, on a recipe made by `utils.recipe_factory` that passes profile `run`.

What is proved:
- a wrong-typed filter value in an AUDIT step is reported before any run (ST12), naming the audit step by its id and its place; the same step with a right value passes;
  the same wrong value written by the author is reported too (the two lists are judged alike);
- the audit tier is walked after the author's steps: an audit drop of a column of an ingredient (the column knowledge of the tier) does not hide the check of a later audit
  filter at the join; a filter on a column an earlier audit step dropped is not judged by ST12 (the engine says it);
- a `polars_drop` of a column that a join step LATER reads as a key is refused BY PLACE (D-0358, which modulates D-0297) by the copy (`add_step`), by `integrity_errors` and by
  the audit profile (AU04) with ONE sentence (`utils.key_drop.key_drop_problem`); where no later join reads it the drop is allowed. The join keys HOME's `extract_primary_keys`
  gives (for the warning of a filter on a key) are still the keys of the join steps, on every shipped recipe and on the staged ones.

Mutation index (each seen failing, see the report): V1 `filter_value_problems` does not read the audit list; V2 `declared_fields` does not follow an audit drop; D1 `add_step` does not
ask the key rule; D2 `integrity_errors` does not; D3 the checker's AU04 is off.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_check_with_registry.py -q
"""
import glob
from pathlib import Path

import pytest

from app.modules.data_analysis_recipe_validator import _graph_of, checker_catalogs
from app.modules.session_manager import extract_primary_keys
from utils import join_keys, key_drop
from utils.audit_copy import AuditCopyError, add_step, integrity_errors, start_audit
from utils.recipe_check import check_recipe
from utils.recipe_factory import minimal_join, minimal_recipe, minimal_schema
from utils.recipe_graph import build_graph
from utils.recipe_loader import load_recipe
from utils.recipe_tiers import AUDIT_COMMENT, AUDIT_STEPS

ROOT = Path(__file__).resolve().parents[2]
AUD = "1a2b3c4d"
FILTER_WRONG = {"action": "modif_filter", "column": "v", "op": "gt", "value": "abc", "na": "remove"}
FILTER_RIGHT = {"action": "modif_filter", "column": "v", "op": "gt", "value": 1.5, "na": "remove"}
CATALOGS = checker_catalogs()


def recipe() -> dict:
    """A, B (joined on `sample_id`, J) and a plot on J; A has `v` (Float64), B has `w` (Int64) and `g` (String, not a key)."""
    a = minimal_schema("data/A.tsv", {"sample_id": "String", "v": "Float64"}, entity_key="sample_id")
    b = minimal_schema("data/B.tsv", {"sample_id": "String", "w": "Int64", "g": "String"}, entity_key="sample_id")
    j = minimal_join(["A", "B"], [{"action": "polars_join", "right_ingredient": "B", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"}])
    plots = {"p": {"ui_label": "P", "target_dataset": "J", "mapping": {"x": "sample_id"}, "layers": [{"name": "geom_bar"}]}}
    return minimal_recipe("r", schemas={"A": a, "B": b}, joins={"J": j}, plots=plots)


def check(raw: dict, profile: str):
    result = check_recipe(raw, profile, catalogs=CATALOGS, graph=_graph_of(raw), file_stem=raw["id"])
    return result.errors


def codes(errors) -> list:
    return [p.code for p in errors]


def test_the_staged_recipe_passes_the_run_profile_with_the_real_registries_and_so_does_an_empty_audit():
    raw = recipe()
    assert check(raw, "run") == []
    assert check(start_audit(raw, AUD).recipe, "audit") == []


# ---- point 2: the typed value of a filter in an audit step -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("place, plain", [("T1:A", "data_schemas.A.tier1.audit_steps[1].value"), ("T1:J", "joins.J.tier1.audit_steps[1].value"),
                                          ("T2:J", "joins.J.tier2.audit_steps[1].value")])
def test_a_wrong_typed_filter_value_in_an_audit_step_is_reported_before_the_run_naming_the_step(place, plain):
    audit = start_audit(recipe(), AUD)
    add_step(audit, place, FILTER_WRONG, "why")
    found = [p for p in check(audit.recipe, "audit") if p.code == "ST12"]
    assert [p.path for p in found] == [plain], found
    assert f"audit step audit_{AUD}_1 at {place}" in found[0].message and "'abc'" in found[0].message and "Float64" in found[0].message


@pytest.mark.parametrize("place", ["T1:A", "T1:J", "T2:J"])
def test_a_correct_filter_value_in_an_audit_step_passes(place):
    audit = start_audit(recipe(), AUD)
    add_step(audit, place, FILTER_RIGHT, "why")
    assert check(audit.recipe, "audit") == []


def test_the_same_wrong_value_written_by_the_author_is_reported_at_the_same_check():
    raw = recipe()
    raw["data_schemas"]["A"]["tier1"]["steps"].append(FILTER_WRONG)
    assert codes(check(raw, "run")) == ["ST12"]


def test_the_audit_steps_are_judged_after_the_authors_an_audit_drop_in_an_ingredient_does_not_hide_the_check_at_the_join():
    """V2: the join `J` reads the declared columns of its ingredient B (`declared_fields`); with an audit drop at B's tier 1 those columns used to be 'unknown' and the check
    of the audit filter at J stopped at the join step. Now the audit drop is followed."""
    audit = start_audit(recipe(), AUD)
    add_step(audit, "T1:B", {"action": "polars_drop", "columns": ["g"]}, "why")
    add_step(audit, "T1:J", FILTER_WRONG, "why")
    assert [p.path for p in check(audit.recipe, "audit") if p.code == "ST12"] == ["joins.J.tier1.audit_steps[1].value"]


def test_an_audit_drop_in_an_ingredient_takes_the_column_out_of_the_known_columns_of_the_join():
    """V2: the declared columns of B after its tier 1 follow the audit drop. A filter at J on `g` with a number is a type error while `g` is there (ST12) and is not
    judged once an audit step dropped `g` in B (the column is gone: the engine says it)."""
    audit = start_audit(recipe(), AUD)
    add_step(audit, "T1:J", {"action": "modif_filter", "column": "g", "op": "eq", "value": 5, "na": "remove"}, "why")
    assert [p.path for p in check(audit.recipe, "audit") if p.code == "ST12"] == ["joins.J.tier1.audit_steps[1].value"]
    dropped = start_audit(recipe(), AUD)
    add_step(dropped, "T1:B", {"action": "polars_drop", "columns": ["g"]}, "why")
    add_step(dropped, "T1:J", {"action": "modif_filter", "column": "g", "op": "eq", "value": 5, "na": "remove"}, "why")
    assert "ST12" not in codes(check(dropped.recipe, "audit"))


def test_a_filter_on_a_column_an_earlier_audit_step_dropped_is_not_judged_by_the_typed_value_check():
    audit = start_audit(recipe(), AUD)
    add_step(audit, "T1:A", {"action": "polars_drop", "columns": ["v"]}, "why")
    add_step(audit, "T1:A", FILTER_WRONG, "why")
    assert "ST12" not in codes(check(audit.recipe, "audit")), "the column is gone: the engine says so at the run, the declared type is no longer a fact"


def test_the_typed_value_check_does_not_read_the_audit_list_outside_the_audit_profile():
    audit = start_audit(recipe(), AUD)
    add_step(audit, "T1:A", FILTER_WRONG, "why")
    assert "ST12" not in codes(check(audit.recipe, "run")) and "AU01" in codes(check(audit.recipe, "run"))


# ---- point 3: a key column cannot be dropped through the audit ----------------------------------------------------------------------------------------

KEY_DROP = {"action": "polars_drop", "columns": ["sample_id"]}


@pytest.mark.parametrize("place", ["T1:A", "T1:B"])
def test_the_copy_refuses_to_drop_a_column_a_later_join_reads_as_a_key_and_changes_nothing(place):
    """ADAPTED to the decided design (D-0358: "refused by place"; D-0297): before, a join key was refused at every place by its NAME, here also at T1:J and T2:J; now it is
    refused where the join J (step 1 of T1:J) is still to come, T1:A and T1:B, and the sentence names that join."""
    audit = start_audit(recipe(), AUD)
    before = audit.recipe.copy()
    with pytest.raises(AuditCopyError, match=f"Cannot drop the column 'sample_id' at {place}: it is read as a join key by step 1 of T1:J.*row filter or a removal by key"):
        add_step(audit, place, KEY_DROP, "why")
    assert audit.created == 0 and audit.recipe == before and AUDIT_STEPS not in str(audit.recipe)


@pytest.mark.parametrize("place", ["T1:J", "T2:J", "T3:p"])
def test_the_same_key_dropped_after_the_join_that_reads_it_is_allowed(place):
    """D-0358: "we can have aggregations by count in a plot where the key does not matter": after the join, and in a plot's own steps, nothing reads the key as a key."""
    audit = start_audit(recipe(), AUD)
    assert add_step(audit, place, KEY_DROP, "why") == f"audit_{AUD}_1" and audit.created == 1


def test_the_declared_key_of_a_table_that_no_join_uses_is_not_refused_for_being_declared_PROVISIONAL():
    """ADAPTED (D-0358, D-0297): D-0297 names JOIN keys, D-0358 says by place, so the declared key of a table is no reason to refuse (the walk records it as information)."""
    raw = recipe()
    raw["data_schemas"]["C"] = minimal_schema("data/C.tsv", {"cid": "String", "x": "Float64"}, entity_key="cid")
    assert "cid" not in join_keys.recipe_join_keys(raw)
    audit = start_audit(raw, AUD)
    add_step(audit, "T1:C", {"action": "polars_drop", "columns": ["cid"]}, "why")
    add_step(audit, "T1:C", {"action": "polars_drop", "columns": ["x"]}, "why")
    assert audit.created == 2


def test_a_drop_of_other_columns_is_allowed_and_a_drop_with_one_key_among_them_is_refused():
    audit = start_audit(recipe(), AUD)
    add_step(audit, "T1:B", {"action": "polars_drop", "columns": ["g", "w"]}, "why")
    with pytest.raises(AuditCopyError, match="sample_id"):
        add_step(audit, "T1:B", {"action": "polars_drop", "columns": ["g", "sample_id"]}, "why")
    assert audit.created == 1


def test_a_join_key_that_is_not_the_declared_key_is_refused_before_its_join_and_allowed_after_it():
    """ADAPTED (D-0358): `v` is the key of A and `w` the key of B in J; each is refused in its own table, whose join is still to come, and allowed at J (the join has run)."""
    raw = recipe()
    raw["joins"]["J"]["tier1"]["steps"][0].update(left_on=["v"], right_on=["w"])
    del raw["joins"]["J"]["tier1"]["steps"][0]["on"]
    assert join_keys.recipe_join_keys(raw) == ["v", "w"]
    audit = start_audit(raw, AUD)
    for column, place in (("v", "T1:A"), ("w", "T1:B")):
        with pytest.raises(AuditCopyError, match=f"column '{column}' at {place}"):
            add_step(audit, place, {"action": "polars_drop", "columns": [column]}, "why")
    for column in ("v", "w"):
        add_step(audit, "T1:J", {"action": "polars_drop", "columns": [column]}, "why")


def test_a_hand_made_key_drop_is_named_by_the_integrity_check_and_by_the_audit_profile_of_the_checker():
    audit = start_audit(recipe(), AUD)
    add_step(audit, "T1:A", {"action": "polars_drop", "columns": ["v"]}, "why")
    audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS][0]["columns"] = ["sample_id"]
    errors = integrity_errors(audit.recipe, recipe())
    assert any(f"audit_{AUD}_1" in e and "Cannot drop the column 'sample_id' at T1:A" in e for e in errors), errors
    found = [p for p in check(audit.recipe, "audit") if p.code == "AU04"]
    assert [p.path for p in found] == ["data_schemas.A.tier1.audit_steps[1].columns"] and "is read as a join key by" in found[0].message
    # the same hand-made step at a place after the join is no problem: by place
    ok = start_audit(recipe(), AUD)
    add_step(ok, "T1:J", {"action": "polars_drop", "columns": ["v"]}, "why")
    ok.recipe["joins"]["J"]["tier1"][AUDIT_STEPS][0]["columns"] = ["sample_id"]
    assert [e for e in integrity_errors(ok.recipe, recipe()) if "Cannot drop" in e] == []
    assert [p for p in check(ok.recipe, "audit") if p.code == "AU04"] == []


def test_the_sentence_is_one_text_for_the_copy_the_integrity_check_and_the_checker():
    raw = recipe()
    sentence = key_drop.key_drop_problem(raw, "T1:A", ["sample_id"])
    audit = start_audit(raw, AUD)
    with pytest.raises(AuditCopyError) as raised:
        add_step(audit, "T1:A", KEY_DROP, "why")
    assert str(raised.value) == sentence
    assert key_drop.key_drop_problem(raw, "T1:A", ["v"]) is None and key_drop.key_drop_problem(raw, "T1:A", "sample_id") is None and key_drop.key_drop_problem(raw, "T1:A", [3]) is None
    assert key_drop.key_drop_problem(raw, "T1:J", ["sample_id"]) is None and key_drop.key_drop_problem(raw, "T3:p", ["sample_id"]) is None


def _shipped():
    return sorted(glob.glob(str(ROOT / "config" / "data_analysis_recipes" / "*" / "*.yaml")))


# the join keys of the shipped recipes that have any, read once from their own join steps (the key columns of `polars_join*` steps in `joins.*.tier1/tier2`); a recipe not
# listed has none. Pinned by hand, so a change of the rule (or of a recipe) shows here.
SHIPPED_JOIN_KEYS = {
    "pipelines/1_Abromics_general_pipeline.yaml": ["Gene_name", "VF_gene", "sample_id"],
    "pipelines/1_test_data_ST22_dummy.yaml": ["Gene_name", "VF_gene", "sample_id"],
    "pipelines/2_test_data_ST22_dummy.yaml": ["sample_id"],
    "pipelines/demo_abromics.yaml": ["sample_id"],
    "pipelines/figshare_integration.yaml": ["sample_id"],
    "templates/complex_template.yaml": ["sample_id"],
    "templates/e_coli.yaml": ["sample_id"],
    "templates/left_join_lesson.yaml": ["sample_id"],
    "templates/simple_template.yaml": ["sample_id"],
}


def _keys_read_independently(raw: dict) -> list:
    """The join keys of a recipe by a small separate reading (it does not call `recipe_join_keys`): every `on`, `left_on`, `right_on`, `by` of a join step."""
    found = set()
    for join in (raw.get("joins") or {}).values():
        for tier in ("tier1", "tier2"):
            for step in (join.get(tier) or {}).get("steps") or []:
                if "join" in str(step.get("action")):
                    for key in ("on", "left_on", "right_on", "by"):
                        value = step.get(key)
                        found.update([value] if isinstance(value, str) else value or [])
    return sorted(found)


@pytest.mark.parametrize("path", _shipped(), ids=lambda p: Path(p).name)
def test_the_join_keys_of_every_shipped_recipe_are_the_pinned_ones(path):
    """The rule (`utils.join_keys.recipe_join_keys`, also HOME's `extract_primary_keys`) gives, on every shipped recipe, the keys read by hand from its join steps and pinned
    above; a recipe that is not pinned has none. It can fail: a rule that misses a key, adds one, or reads the wrong list gives another set."""
    raw, _ = load_recipe(path)
    if not isinstance(raw, dict):
        pytest.skip("no recipe")
    expected = SHIPPED_JOIN_KEYS.get(str(Path(path).relative_to(ROOT / "config" / "data_analysis_recipes")), [])
    assert _keys_read_independently(raw) == expected
    assert join_keys.recipe_join_keys(raw) == expected
    assert extract_primary_keys(raw) == expected


def test_the_declared_entity_key_of_a_shipped_recipe_is_the_pinned_one():
    """ADAPTED: `join_keys.entity_key_columns` (the declared keys by name over the recipe) is gone with the refusal by name (D-0358); the graph says which table declares which key."""
    raw, _ = load_recipe(str(ROOT / "config" / "data_analysis_recipes" / "pipelines" / "1_Abromics_general_pipeline.yaml"))
    graph = build_graph(raw)
    declared = sorted({k for table in graph.collections() for k in graph.declared_entity_keys(table)})
    assert declared == ["sample_id"]
    assert "Gene_name" in join_keys.recipe_join_keys(raw) and "Gene_name" not in declared


def test_the_rule_gives_the_join_keys_home_gives_on_the_staged_recipes():
    raw = recipe()
    assert join_keys.recipe_join_keys(raw) == extract_primary_keys(raw) == ["sample_id"]
    raw["joins"]["J"]["tier2"] = {"steps": [{"action": "polars_join_asof", "right_ingredient": "B", "by": ["g"], "left_on": "v", "right_on": "w", "maintain_order": "left_right"}]}
    assert join_keys.recipe_join_keys(raw) == extract_primary_keys(raw)
    assert set(join_keys.recipe_join_keys(raw)) >= {"g", "v", "w"}
