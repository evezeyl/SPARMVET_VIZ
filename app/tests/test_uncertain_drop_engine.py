"""A drop the walk cannot follow to the end is ALLOWED with a warning (D-0449, "Right now od go for B"); the real engine says what each such drop does (D-0449's condition, her words:
"do not get wrong results because we did not select the correct scope"): the outcome is the table the user meant, or a plain error, never a different table with no word.

Every case below is a small recipe written to disk by `uncertain_drop_world.World`, the audit copy made by `add_step` (the engine's plan handed to the gate, as HOME does), run by
`run_audit` and built by the app's own `materialize_tier1/2/3`. Nothing is stubbed and no shipped recipe changes (D-0373). Each case is classified:

  INTENDED   the table the user meant: the column is gone where it was dropped, every other column holds the same values;
  PLAIN      the build stops with an error that names the audit step, the table, the tier, the step that needs the column and the column, in one line, with no dump of the engine's plan;
  MESSAGE    a different table than the one before, WITH a word: the warning names it before the user confirms;
  SILENT     a different table with no word: the one class the gate cannot see (a formula is never read, D-0356). Pinned here with its evidence, and the warning's standing sentence
             says it. It exists for every drop at every place, the ones the walk follows included (it is not new with D-0449).

| case                                                                    | place        | uncertain | outcome                                   |
|-------------------------------------------------------------------------|--------------|-----------|-------------------------------------------|
| a  drop after an unpivot (the column is no longer a column there)       | T1:T         | no        | PLAIN ("a" not found)                     |
| b  drop before an unpivot that names the column                          | T1:T         | yes       | PLAIN                                     |
| b2 drop before an unpivot that does not name it (it vanishes there)       | T1:T         | yes       | INTENDED (no table after it changes)      |
| c1 reshape back to wide, the column is back, drop it                      | T2:T         | no        | INTENDED                                  |
| c2 the same column dropped before the reshape back                        | T1:T         | no        | PLAIN                                     |
| c4 drop before an unpivot, a pivot after it (plot's own steps)            | T1:T         | yes       | PLAIN                                     |
| d  a later formula, select, join on the column                            | T1:T         | no / yes  | PLAIN (the join: refused with the plan)   |
| e  the steps the walk does not read (unpivot, str_split, explode, fill, describe, pivot) | T1:T | yes   | PLAIN or INTENDED, per step               |
| f  the shipped recipes: 8 places only blind, 15 uncertain with the plan    | T1:*         | yes       | refused with the plan / 6 INTENDED / 9 PLAIN |
| h  a same-named column of a join that changes meaning                    | T1:T         | yes       | MESSAGE (the warning names it)            |
| i  a formula that takes every column (pl.all())                          | T1:T         | yes       | SILENT (the standing sentence only)       |
| g  every INTENDED case: the other columns hold the same values            |              |           | asserted in each                          |

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_uncertain_drop_engine.py -q
"""
import json
from pathlib import Path

import polars as pl
import pytest

from app.modules.audit_run import AuditRunError, run_audit
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_plan_composer import ABROMICS, DEMO, shipped
from app.tests.uncertain_drop_world import World, lost_and_rest, step_drop, tsv_frame
from utils import key_drop
from utils.audit_copy import AuditCopyError, add_step, remove_step, start_audit

T = tsv_frame(sample_id=["s1", "s2", "s3"], a=["a1", "a2", "a3"], b=["b1", "b2", "b3"], c=["c1", "c2", "c3"])
B = tsv_frame(sample_id=["s1", "s2", "s3"], lab=["X", "Y", "Z"])


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def unpivot(on, index):
    return {"action": "polars_unpivot", "on": list(on), "index": list(index), "variable_name": "variable", "value_name": "value"}


def pivot(index):
    return {"action": "polars_pivot", "on": ["variable"], "index": list(index), "values": ["value"], "aggregate_function": "first"}


def join_step(right, on="sample_id"):
    return {"action": "polars_join", "right_ingredient": right, "on": [on], "how": "left", "maintain_order": "left_right"}


def with_columns(**formulas):
    return {"action": "polars_with_columns", "named_exprs": dict(formulas)}


def plot(target, x="sample_id", tier3=None):
    return {"target_dataset": target, "mapping": {"x": x}, "layers": [{"name": "geom_bar", "params": {}}], **({"tier3": {"steps": list(tier3)}} if tier3 else {})}


def join_of(*tables, steps=()):
    return {"ingredients": [{"dataset_id": t} for t in tables], "tier1": {"steps": list(steps)}}


def world(tmp_path, tables, schemas, joins=None, plots=None):
    return World(tmp_path, tables, schemas, joins, plots)


def assert_plain(error: AuditRunError, column: str):
    """The sentence a person reads: one line, the audit step, the column, no plan of the engine."""
    text = str(error)
    assert text.startswith("The audit step audit_1a2b3c4d_1 at ") and column in text, text
    assert "\n" not in text and "Resolved plan" not in text and "Traceback" not in text and "polars.exceptions" not in text, text


def run_error(w, audit) -> AuditRunError:
    with pytest.raises(AuditRunError) as raised:
        w.run(audit)
    return raised.value


# ------------------------------------------------------------------------------------------------------------------- a and b: the place of the drop against the unpivot

def test_a_drop_after_an_unpivot_names_a_column_that_is_no_longer_there_and_ends_as_a_plain_error(tmp_path):
    """Case a. After the unpivot `a` is a value of `variable`, not a column: the facts are empty (nothing to follow), the drop is written, the build says so."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [unpivot(["a", "b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    facts = w.facts("T1:T", "a")
    assert not facts.refused and not facts.uncertain and not facts.needs
    assert w.original_built().tables["T1:T"].columns == ["sample_id", "c", "variable", "value"]
    audit = w.copy_with("T1:T", step_drop("a"))
    assert w.audit_built(audit).error and '"a" not found' in w.audit_built(audit).error
    error = run_error(w, audit)
    assert_plain(error, '"a" not found') and "T1:T" in str(error) and "polars_drop" in str(error)


def test_a_drop_before_an_unpivot_that_names_the_column_is_allowed_with_a_warning_and_ends_as_a_plain_error(tmp_path):
    """Case b: the unpivot is in tier 2 and names `a`; the drop (end of tier 1) is before it. The walk cannot read the unpivot: the drop is allowed, the warning says where it
    lost the column, the build says which step needs it."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["a", "b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    facts = w.facts("T1:T", "a")
    assert facts.uncertain and [(r.code, r.get("action")) for r in facts.unfollowed] == [("step_not_read", "polars_unpivot")]
    assert key_drop.key_drop_problem(w.original.raw, "T1:T", ["a"], w.plans) is None
    said = key_drop.key_drop_warning(w.original.raw, "T1:T", ["a"], w.plans)
    assert "step 1 of T2:T (polars_unpivot)" in said and "may fail" in said
    audit = w.copy_with("T1:T", step_drop("a"))
    assert audit.created == 1
    error = run_error(w, audit)
    assert_plain(error, '"a" not found') and "tier 2 of the table 'T'" in str(error) and "polars_unpivot" in str(error)


def test_a_drop_before_an_unpivot_that_does_not_name_the_column_is_the_intended_table_and_changes_nothing_else(tmp_path):
    """Case b2: `a` is neither in `on` nor in `index`, so the unpivot drops it anyway. The drop is uncertain for the walk and harmless for the data: the table of tier 1 loses `a`,
    every table after the unpivot is the same as before, no plot changes, no other column changes (case g)."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    assert w.facts("T1:T", "a").uncertain
    audit = w.copy_with("T1:T", step_drop("a"))
    before, after = w.original_built(), w.audit_built(audit)
    assert not before.error and not after.error
    lost, gained, same = lost_and_rest(before.tables["T1:T"], after.tables["T1:T"])
    assert (lost, gained, same) == ({"a"}, set(), True)
    for table in ("T2:T", "T3:Q", "T1:B"):
        assert before.tables[table].equals(after.tables[table]), table
    assert w.run(audit).affected_plots == []


# ------------------------------------------------------------------------------------------------------------------- c: reshape back to wide

def wide_world(tmp_path, tier2=(), tier3=()):
    return world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [unpivot(["a", "b"], ["sample_id", "c"])], "tier2": list(tier2)}, "B": {}}, {}, {"Q": plot("T", tier3=tier3)})


def test_after_a_reshape_back_to_wide_the_column_is_a_column_again_and_its_drop_is_the_intended_table(tmp_path):
    """Case c1: the unpivot is in tier 1, the pivot in tier 2: `a` is back at the end of tier 2. The drop there is certain (nothing is built after it), allowed, and gives the wide
    table without `a`; the long table of tier 1 and every other column are unchanged."""
    w = wide_world(tmp_path, tier2=[pivot(["sample_id", "c"])])
    before = w.original_built()
    assert before.tables["T2:T"].columns == ["sample_id", "c", "a", "b"]
    assert not w.facts("T2:T", "a").uncertain and key_drop.key_drop_warning(w.original.raw, "T2:T", ["a"], w.plans) is None
    audit = w.copy_with("T2:T", step_drop("a"))
    after = w.audit_built(audit)
    assert not after.error
    assert lost_and_rest(before.tables["T2:T"], after.tables["T2:T"]) == ({"a"}, set(), True)
    assert lost_and_rest(before.tables["T3:Q"], after.tables["T3:Q"]) == ({"a"}, set(), True)
    assert before.tables["T1:T"].equals(after.tables["T1:T"])
    assert w.run(audit).affected_plots == ["Q"]


def test_the_same_column_dropped_before_the_reshape_is_not_a_column_there_and_ends_as_a_plain_error(tmp_path):
    """Case c2: the name `a` comes back only after the pivot; at the end of tier 1 it is a value, so the drop names something that is not there: plain error, no table."""
    w = wide_world(tmp_path, tier2=[pivot(["sample_id", "c"])])
    assert not w.facts("T1:T", "a").uncertain
    error = run_error(w, w.copy_with("T1:T", step_drop("a")))
    assert_plain(error, '"a" not found') and "tier 1 of the table 'T'" in str(error)


def test_a_drop_before_an_unpivot_that_a_pivot_in_the_plots_own_steps_undoes_ends_as_a_plain_error(tmp_path):
    """Case c4: unpivot in tier 2, pivot in the plot's tier 3: the plot would show `a` as a column again, but the unpivot needs it first: the build stops at the unpivot."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["a", "b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T", tier3=[pivot(["sample_id", "c"])])})
    assert w.original_built().tables["T3:Q"].columns == ["sample_id", "c", "a", "b"]
    assert w.facts("T1:T", "a").uncertain
    error = run_error(w, w.copy_with("T1:T", step_drop("a")))
    assert_plain(error, '"a" not found') and "polars_unpivot" in str(error)


# ------------------------------------------------------------------------------------------------------------------- d: a later step needs the column

def test_a_later_formula_or_select_that_needs_the_dropped_column_ends_as_a_plain_error(tmp_path):
    for later, shown in (({"action": "polars_with_columns", "named_exprs": {"z": "pl.col('a') + pl.col('b')"}}, '"a"'),
                         ({"action": "polars_select", "exprs": ["sample_id", "a"]}, '"a"')):
        w = world(tmp_path / later["action"], {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [later]}, "B": {}}, {}, {"P": plot("T")})
        assert not w.facts("T1:T", "a").refused
        error = run_error(w, w.copy_with("T1:T", step_drop("a")))
        assert_plain(error, shown) and "tier 2 of the table 'T'" in str(error) and later["action"] in str(error)


def join_world(tmp_path, left_steps, key="k"):
    left = tsv_frame(sample_id=["s1", "s2", "s3"], k=["k1", "k2", "k3"], a=["a1", "a2", "a3"])
    right = tsv_frame(k=["k1", "k2", "k3"], lab=["X", "Y", "Z"])
    return world(tmp_path, {"T": left, "B": right}, {"T": {"tier1": list(left_steps)}, "B": {}}, {"J": join_of("T", "B", steps=[join_step("B", key)])}, {"P": plot("J")})


FILL = {"action": "polars_fill_null", "columns": ["a"], "value": "zz"}


def test_a_join_key_behind_a_step_the_walk_cannot_read_is_refused_with_the_plan_and_allowed_blind_then_refused_by_the_run(tmp_path):
    """Case d, the join: the key `k` of the join in J, the table T has a step the walk does not read before it (a fill). With the engine's plan: refused, by the join that needs it.
    Blind (no engine): the walk cannot follow, so the drop is allowed with a warning; the run composes the plan itself and refuses it before building anything: a plain refusal."""
    w = join_world(tmp_path, [FILL])
    assert w.facts("T1:T", "k").refused
    with pytest.raises(AuditCopyError, match="read as a join key by step 1 of T1:J"):
        w.copy_with("T1:T", step_drop("k"))
    blind = key_drop.DropGate(w.original.raw).facts("T1:T", "k")
    assert blind.uncertain and not blind.refused
    audit = w.copy_with("T1:T", step_drop("k"), blind=True)
    assert audit.created == 1
    error = run_error(w, audit)
    assert "read as a join key by step 1 of T1:J" in str(error) and "Resolved plan" not in str(error) and "\n" not in str(error)
    assert not (w.root / "run_audit").exists() or list((w.root / "run_audit").glob("*.parquet")) == [], "nothing was built"


def test_a_drop_of_a_column_a_join_does_not_read_keeps_the_joined_table_and_changes_nothing_else(tmp_path):
    w = join_world(tmp_path, [FILL])
    before = w.original_built()
    audit = w.copy_with("T1:T", step_drop("a"))
    after = w.audit_built(audit)
    assert not after.error
    for table in ("T1:T", "T1:J", "T3:P"):
        assert lost_and_rest(before.tables[table], after.tables[table]) == ({"a"}, set(), True), table


# ------------------------------------------------------------------------------------------------------------------- e: the steps the walk does not read

NUMBERS = tsv_frame(sample_id=["s1", "s2", "s3"], q1=[1, 2, 3], q2=[10, 20, 30], q3=[100, 200, 300])


@pytest.mark.parametrize("name, tier1, tier2, dropped, needs_it", [
    ("unpivot", [], [unpivot(["a", "b"], ["sample_id", "c"])], "a", True),
    ("unpivot_index", [], [unpivot(["b"], ["sample_id", "c"])], "c", True),
    ("str_split", [], [{"action": "polars_str_split", "columns": ["a"], "by": "1"}], "a", True),
    ("explode", [{"action": "polars_str_split", "columns": ["a"], "by": "1"}], [{"action": "polars_explode", "columns": ["a"]}], "a", True),
    ("fill_null", [], [{"action": "polars_fill_null", "columns": ["a"], "value": "zz"}], "a", True),
    ("fill_null_other", [], [{"action": "polars_fill_null", "columns": ["a"], "value": "zz"}], "b", False),
])
def test_the_steps_the_walk_does_not_read_end_as_a_plain_error_where_they_need_the_column_and_as_the_intended_table_where_they_do_not(tmp_path, name, tier1, tier2, dropped, needs_it):
    """Case e. An unread step that NAMES the dropped column stops the build, named; one that does not name it passes the drop through: the column is gone, the rest holds."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": tier1, "tier2": tier2}, "B": {}}, {}, {"Q": plot("T")})
    audit = w.copy_with("T1:T", step_drop(dropped))
    if needs_it:
        error = run_error(w, audit)
        assert_plain(error, dropped)
        return
    before, after = w.original_built(), w.audit_built(audit)
    assert not after.error
    assert lost_and_rest(before.tables["T2:T"], after.tables["T2:T"]) == ({dropped}, set(), True)
    assert w.run(audit).affected_plots == ["Q"]


def test_a_describe_after_a_drop_is_the_intended_table_with_the_column_gone_from_the_statistics(tmp_path):
    """Case e, describe: the step turns every column into statistics (the types change, so the walk is unsure). The statistics of the dropped column are gone and those of the other
    columns are the same numbers."""
    w = world(tmp_path, {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [{"action": "polars_describe"}]}, "B": {}}, {}, {"P": plot("T")})
    audit = w.copy_with("T1:T", step_drop("q2"))
    before, after = w.original_built().tables["T2:T"], w.audit_built(audit).tables["T2:T"]
    assert lost_and_rest(before, after) == ({"q2"}, set(), True)


def test_a_pivot_after_an_unpivot_needs_the_column_the_index_names_and_ends_as_a_plain_error(tmp_path):
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [unpivot(["a", "b"], ["sample_id", "c"])], "tier2": [pivot(["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    audit = w.copy_with("T1:T", step_drop("variable"))
    error = run_error(w, audit)
    assert_plain(error, "variable")


# ------------------------------------------------------------------------------------------------------------------- the warning is shown before the user confirms; the audit is undone by removing the step

def test_removing_the_audit_step_gives_the_recipe_and_its_tables_back(tmp_path):
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    audit = start_audit(w.original.raw, "1a2b3c4d")
    step_id = add_step(audit, "T1:T", step_drop("a"), "because", plans=w.plans)
    assert audit.recipe != w.original.raw
    remove_step(audit, step_id)
    assert audit.recipe == w.original.raw
    assert w.audit_built(audit).tables["T1:T"].equals(w.original_built().tables["T1:T"])


def test_a_drop_of_two_columns_judges_each_and_the_warning_names_only_the_unsure_one(tmp_path):
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["a"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    said = key_drop.key_drop_warning(w.original.raw, "T1:T", ["a", "c"], w.plans)
    assert said and "the column 'a' at T1:T" in said and "'c'" not in said, "c passes the unpivot as an index: it is followed"


# ------------------------------------------------------------------------------------------------------------------- h and i: what changes without an error

def test_a_same_named_column_of_a_join_changes_meaning_after_the_drop_and_the_warning_says_so_before_the_user_confirms(tmp_path):
    """Case h, the one that a build does not stop on: A and B both have `lab`; the join gave B's the suffix `_right`. Dropped from A, B's `lab` keeps its name, and a plot that draws
    `lab` now draws B's values. Here the walk is unsure too (an unpivot of another column in tier 2 of A), so the drop is only allowed because the warning names the clash."""
    left = tsv_frame(sample_id=["s1", "s2", "s3"], lab=["A1", "A2", "A3"], x=["x1", "x2", "x3"])
    right = tsv_frame(sample_id=["s1", "s2", "s3"], lab=["B1", "B2", "B3"])
    w = world(tmp_path, {"T": left, "B": right}, {"T": {"tier1": [], "tier2": [unpivot(["x"], ["sample_id"])]}, "B": {}},
              {"J": join_of("T", "B", steps=[join_step("B")])}, {"P": plot("J", x="lab"), "Q": plot("T")})
    assert w.facts("T1:T", "lab").uncertain
    said = key_drop.key_drop_warning(w.original.raw, "T1:T", ["lab"], w.plans)
    assert "'lab_right'" in said and "keeps the name 'lab'" in said and "reads the column of B, with no error" in said
    audit = w.copy_with("T1:T", step_drop("lab"))
    before, after = w.original_built().tables["T3:P"], w.audit_built(audit).tables["T3:P"]
    assert before["lab"].to_list() == ["A1", "A2", "A3"] and "lab_right" in before.columns
    assert after["lab"].to_list() == ["B1", "B2", "B3"] and "lab_right" not in after.columns, "a different table with the same column name: the word is in the warning above"


TOTAL = with_columns(total="pl.sum_horizontal(pl.all().exclude('sample_id'))")


def test_SILENT_a_formula_that_takes_every_column_computes_on_one_column_less_with_no_error_and_only_the_standing_sentence_says_it(tmp_path):
    """Case i, the class the gate cannot see: a formula is never read (D-0356). `pl.all()`, `pl.exclude(..)` and `pl.col(<type>)` take the columns that exist when the step runs,
    so the total of three columns becomes the total of two, and nothing fails. It is true for a drop at ANY place whatever the walk knows (it is not new with D-0449): the certain
    drop below does it too. The warning of an unsure drop says it in a standing sentence; it cannot say which formula, because it does not read formulas. Reported to the owner."""
    certain = world(tmp_path / "certain", {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL]}, "B": {}}, {}, {"P": plot("T")})
    assert not certain.facts("T1:T", "q2").uncertain and key_drop.key_drop_warning(certain.original.raw, "T1:T", ["q2"], certain.plans) is None
    before, after = certain.original_built().tables["T2:T"], certain.audit_built(certain.copy_with("T1:T", step_drop("q2"))).tables["T2:T"]
    assert before["total"].to_list() == [111, 222, 333] and after["total"].to_list() == [101, 202, 303], "a certain drop: the total changes, no error, no word (exists today)"
    unsure = world(tmp_path / "unsure", {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL]}, "B": {}}, {},
                   {"P": plot("T"), "R": plot("T", tier3=[unpivot(["q1"], ["sample_id"])])})
    assert unsure.facts("T1:T", "q2").uncertain, "q2 also flows into the plot R, whose unpivot the walk does not read"
    said = key_drop.key_drop_warning(unsure.original.raw, "T1:T", ["q2"], unsure.plans)
    assert "pl.all()" in said and "with no error" in said
    after = unsure.audit_built(unsure.copy_with("T1:T", step_drop("q2"))).tables["T2:T"]
    assert after["total"].to_list() == [101, 202, 303]


# ------------------------------------------------------------------------------------------------------------------- f: the shipped recipes

SHIPPED = ("1_test_data_ST22_dummy", ABROMICS, "2_test_data_ST22_dummy", "1_Abromics_general_pipeline", "figshare_integration")


def uncertain_places(recipe_id, with_plan):
    orch, loaded, graph, book = shipped(recipe_id)
    gate = key_drop.DropGate(loaded.raw, book if with_plan else None)
    found = []
    for nid in graph.nodes():
        if graph.node(nid).kind == "DS":
            continue
        for name in book.get(nid, len(graph.node(nid).steps)).names:
            facts = gate.facts(nid, name)
            if facts.uncertain:
                found.append((nid, name))
    return orch, loaded, book, found


def blind_only_places():
    """The places that only a gate with no plan finds unsure and that the plan shows to be join keys: found by running the walk on every shipped recipe, read-only."""
    out = []
    for recipe_id in SHIPPED:
        orch, loaded, book, blind = uncertain_places(recipe_id, with_plan=False)
        certain = key_drop.DropGate(loaded.raw, book)
        out += [(recipe_id, nid, name) for nid, name in blind if certain.facts(nid, name).refused]
    return out


def test_the_places_of_the_shipped_recipes_that_the_walk_cannot_follow_without_the_plan_are_eight_and_the_run_refuses_each_as_a_join_key(tmp_path):
    """Case f, part 1: the five of the review of 2026-11-20 and three more of `1_Abromics_general_pipeline`. Blind, the gate allows each with a warning; the run composes the plan and
    refuses it before building anything, with the join that reads the key: never a table, always a plain sentence."""
    places = blind_only_places()
    assert len(places) == 8 and {r for r, _, _ in places} == {DEMO, ABROMICS, "1_Abromics_general_pipeline"}
    for index, (recipe_id, place, column) in enumerate(places):
        orch, loaded, book, _ = uncertain_places(recipe_id, with_plan=False)
        audit = start_audit(loaded.raw, "1a2b3c4d")
        add_step(audit, place, step_drop(column), "because")                         # blind: written (D-0449)
        with pytest.raises(AuditRunError) as raised:
            run_audit(orch, recipe_id, audit.recipe, tmp_path / recipe_id / "orig", tmp_path / recipe_id / f"aud{index}")
        text = str(raised.value)
        assert "read as a join key by" in text and f"the column {column!r} at {place}" in text and "Resolved plan" not in text and "\n" not in text, text


# the fifteen places of `1_test_data_ST22_dummy` that stay unsure WITH the plan (the columns that flow into an unpivot the walk does not read): six drops vanish at the unpivot and
# change nothing after it (INTENDED), nine are named by an unpivot or a later step and stop the build (PLAIN)
INTENDED = {("T1:Summary_quality", c) for c in ("quality_module", "taxon", "genotype", "phenotype", "cge_phenotype", "plasmid")}


def test_the_fifteen_places_of_the_demo_recipe_that_stay_unsure_with_the_plan_are_six_intended_tables_and_nine_plain_errors(tmp_path):
    """Case f, part 2, on the shipped demo recipe and its data, read only (the anchors and the audit folders are in `tmp_path`)."""
    orch, loaded, book, places = uncertain_places(DEMO, with_plan=True)
    assert len(places) == 15 and INTENDED <= set(places)
    intended, plain = [], []
    for index, (place, column) in enumerate(places):
        audit = start_audit(loaded.raw, "1a2b3c4d")
        add_step(audit, place, step_drop(column), "because", plans=book)
        assert key_drop.key_drop_warning(loaded.raw, place, [column], book), (place, column)
        try:
            run = run_audit(orch, DEMO, audit.recipe, tmp_path / "orig", tmp_path / f"aud{index}")
        except AuditRunError as error:
            text = str(error)
            assert text.startswith("The audit step audit_1a2b3c4d_1 at ") and column in text and "Resolved plan" not in text and "\n" not in text, text
            plain.append((place, column))
            continue
        table = place.split(":", 1)[1]
        original, after = (pl.read_parquet(tmp_path / "orig" / f"{table}.parquet"), pl.read_parquet(run.tables[table].t1_path))
        assert lost_and_rest(original, after) == ({column}, set(), True), (place, column)
        assert run.affected_plots == [], "the unpivot takes the column away anyway: no plot differs"
        intended.append((place, column))
    assert set(intended) == INTENDED and len(plain) == 9


def test_the_run_of_a_shipped_recipe_without_audit_steps_still_reuses_the_originals(tmp_path):
    orch, loaded, book, _ = uncertain_places(DEMO, with_plan=True)
    run = run_audit(orch, DEMO, start_audit(loaded.raw, "1a2b3c4d").recipe, tmp_path / "orig", tmp_path / "aud")
    assert run.affected_plots == [] and run.built_tables == []
