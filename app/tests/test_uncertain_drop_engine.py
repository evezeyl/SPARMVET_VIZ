"""A drop the walk cannot follow to the end is REFUSED, red and not tickable (D-0460; it replaces D-0449, which allowed it with a warning). These tests keep what the real engine
says about each such drop, as facts, so that the owner can decide later which steps the app learns to follow (the catalogue she ordered): the drop is written as a step of the recipe's
own author (`World.drop_built`, the only way to ask the engine, since the gate no longer writes it as an audit step), and the engine's tables are compared with the recipe's own.
Her condition stays (D-0450, "do not get wrong results because we did not select the correct scope"): the refusal is the answer; these tests record what would have happened.

Every case is a small recipe written to disk by `uncertain_drop_world.World` (no shipped recipe changes, D-0373) and built by the app's own `materialize_tier1/2/3`. Each case is classified:

  INTENDED   the table the user meant: the column is gone where it was dropped, every other column holds the same values;
  PLAIN      the build stops with an error that names the column and the step that needs it;
  MESSAGE    a different table than the one before, which the refusal sentence names before anything is written (a same-named column of a join);
  SILENT     a different table with no word: the one class the gate cannot see (a formula is never read, D-0356). Pinned here as KNOWN OPEN BEHAVIOUR, not approved behaviour (the
             catalogue study of the uncertainties decides what to do): it exists today for every drop the app CAN follow too (it is not new).

| case                                                                    | place        | uncertain | what the engine does with the drop       | the drop           |
|-------------------------------------------------------------------------|--------------|-----------|------------------------------------------|--------------------|
| a  drop after an unpivot (the column is no longer a column there)       | T1:T         | no        | PLAIN ("a" not found)                    | written, plain run |
| b  drop before an unpivot that names the column                          | T1:T         | yes       | PLAIN                                    | refused            |
| b2 drop before an unpivot that does not name it (it vanishes there)       | T1:T         | yes       | INTENDED (no table after it changes)     | refused            |
| c1 reshape back to wide, the column is back, drop it                      | T2:T         | no        | INTENDED                                 | written            |
| c2 the same column dropped before the reshape back                        | T1:T         | no        | PLAIN                                    | written, plain run |
| c4 drop before an unpivot, a pivot after it (plot's own steps)            | T1:T         | yes       | PLAIN                                    | refused            |
| d  a later formula, select, join on the column                            | T1:T         | no / yes  | PLAIN (the join: refused with the plan)  | written / refused  |
| e  the steps the walk does not read (unpivot, str_split, explode, fill, describe, pivot) | T1:T | yes | PLAIN or INTENDED, per step              | refused            |
| f  the shipped recipes: 8 places only blind, 18 uncertain with the plan   | T1:*         | yes       | refused with the plan / 9 INTENDED / 9 PLAIN | refused        |
| h  a same-named column of a join that changes meaning                    | T1:T         | yes       | MESSAGE (the refusal names it)           | refused            |
| i  a formula that takes every column (pl.all())                          | T1:T         | yes / no  | SILENT                                   | refused / written  |
| g  every INTENDED case: the other columns hold the same values            |              |           | asserted in each                         |                    |

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_uncertain_drop_engine.py -q
"""
import json
from pathlib import Path

import polars as pl
import pytest

from app.modules.audit_run import AuditRunError, run_audit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, loaded_from_resolved
from app.tests.test_plan_composer import ABROMICS, DEMO, shipped
from app.tests.uncertain_drop_world import World, author_version, build_all, changed_tables, lost_and_rest, step_drop, tsv_frame, with_author_step
from utils import key_drop
from utils.lineage_records import PLOT_USES_COLUMN
from utils.audit_copy import AuditCopyError, AuditStep, add_step, remove_step, start_audit, with_audit_steps
from utils.recipe_tiers import AUDIT_COMMENT

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


def refusal(w, place: str, column: str, *, blind: bool = False) -> str:
    """The sentence the gate gives for the drop, through the way every caller writes a step (`add_step`): the red line, nothing written. With and without the engine's plan the text holds the
    capital YET, and the copy stays as it was."""
    audit = start_audit(w.original.raw, "1a2b3c4d")
    with pytest.raises(AuditCopyError) as raised:
        add_step(audit, place, step_drop(column), "because", plans=None if blind else w.plans)
    text = str(raised.value)
    assert text.startswith(f"The app cannot YET follow the column {column!r} at {place} to the end"), text
    assert "the drop is not written" in text and "may fail" not in text and "Warning" not in text
    assert audit.created == 0 and audit.recipe == w.original.raw, "a refused call changes nothing"
    assert w.hand_made_audit(place, step_drop(column)).created == 1
    return text


def the_run_refuses_a_hand_made_drop(w, place: str, column: str) -> str:
    """What `run_audit` says to a drop that a file or an old session holds past the gate: the same refusal, before anything is built."""
    error = str(run_error(w, w.hand_made_audit(place, step_drop(column))))
    assert "cannot YET follow" in error and "\n" not in error and "Resolved plan" not in error, error
    return error


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


def test_the_error_of_a_failed_audit_step_is_one_line_without_the_engines_plan_while_the_engine_itself_prints_its_plan(tmp_path):
    """Review point 3 of 2026-11-21, a direct test with the real engine: an audit step written at a plot (where HOME writes a drop) that names a column the plot's table does not have fails
    when the plot's table is collected, and the engine's own text then holds its plan on several lines. The error the run gives (`short_engine_text` in `audit_run`) is the step, the
    place and the column, in one line. MUTATION AR1 (the run puts `str(error)` back) fails here."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": []}, "B": {}}, {}, {"Q": plot("T")})
    assert w.facts("T3:Q", "nope") is not None and not w.facts("T3:Q", "nope").uncertain, "a plot is never refused: the engine says the column is missing"
    audit = w.copy_with("T3:Q", step_drop("nope"))
    engine_text = w.audit_built(audit).error
    assert engine_text and "Resolved plan" in engine_text and "\n" in engine_text, "the premise: the engine's own text carries its plan"
    text = str(run_error(w, audit))
    assert text.startswith("The audit step audit_1a2b3c4d_1 at T3:Q cannot be applied: ") and '"nope"' in text
    assert "Resolved plan" not in text and "\n" not in text and len(text) < 600, text


def test_a_drop_before_an_unpivot_that_names_the_column_is_refused_and_the_engine_would_have_stopped_with_a_plain_error(tmp_path):
    """Case b: the unpivot is in tier 2 and names `a`; the drop (end of tier 1) is before it. The walk cannot read the unpivot: the drop is refused, the sentence says where it lost the
    column; had it been written, the build would have said which step needs it."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["a", "b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    facts = w.facts("T1:T", "a")
    assert facts.uncertain and [(r.code, r.get("action")) for r in facts.unfollowed] == [("step_not_read", "polars_unpivot")]
    said = key_drop.key_drop_problem(w.original.raw, "T1:T", ["a"], w.plans)
    assert "it reaches step 1 of T2:T (polars_unpivot), a step the app cannot read" in said and "'a'" in said
    assert refusal(w, "T1:T", "a") == said
    the_run_refuses_a_hand_made_drop(w, "T1:T", "a")
    built = w.drop_built("T1:T", "a")
    assert built.error and '"a" not found' in built.error


def test_a_drop_before_an_unpivot_that_does_not_name_the_column_is_refused_and_the_engine_would_have_given_the_intended_table(tmp_path):
    """Case b2: `a` is neither in `on` nor in `index`, so the unpivot drops it anyway. The drop is uncertain for the walk and harmless for the data: the table of tier 1 loses `a`, every
    table after the unpivot is the same as before, no plot changes, no other column changes (case g). The app still cannot say so, so the line is red: it is the price of not guessing."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    assert w.facts("T1:T", "a").uncertain
    refusal(w, "T1:T", "a")
    before, after = w.original_built(), w.drop_built("T1:T", "a")
    assert not before.error and not after.error
    assert lost_and_rest(before.tables["T1:T"], after.tables["T1:T"]) == ({"a"}, set(), True)
    assert changed_tables(before, after) == {"T1:T"}, "no table after the unpivot, no plot, no other table changes"


# ------------------------------------------------------------------------------------------------------------------- c: reshape back to wide

def wide_world(tmp_path, tier2=(), tier3=()):
    return world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [unpivot(["a", "b"], ["sample_id", "c"])], "tier2": list(tier2)}, "B": {}}, {}, {"Q": plot("T", tier3=tier3)})


def test_after_a_reshape_back_to_wide_the_column_is_a_column_again_and_its_drop_is_the_intended_table(tmp_path):
    """Case c1: the unpivot is in tier 1, the pivot in tier 2: `a` is back at the end of tier 2. The drop there is certain (nothing is built after it), allowed, and gives the wide
    table without `a`; the long table of tier 1 and every other column are unchanged."""
    w = wide_world(tmp_path, tier2=[pivot(["sample_id", "c"])])
    before = w.original_built()
    assert before.tables["T2:T"].columns == ["sample_id", "c", "a", "b"]
    assert not w.facts("T2:T", "a").uncertain and key_drop.key_drop_problem(w.original.raw, "T2:T", ["a"], w.plans) is None
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


def test_a_drop_before_an_unpivot_that_a_pivot_in_the_plots_own_steps_undoes_is_refused_and_the_engine_would_stop_with_a_plain_error(tmp_path):
    """Case c4: unpivot in tier 2, pivot in the plot's tier 3: the plot would show `a` as a column again, but the unpivot needs it first: the build stops at the unpivot."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["a", "b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T", tier3=[pivot(["sample_id", "c"])])})
    assert w.original_built().tables["T3:Q"].columns == ["sample_id", "c", "a", "b"]
    assert w.facts("T1:T", "a").uncertain
    refusal(w, "T1:T", "a")
    built = w.drop_built("T1:T", "a")
    assert built.error and '"a" not found' in built.error


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


def test_a_join_key_behind_a_step_the_walk_cannot_read_is_refused_as_a_key_with_the_plan_and_as_not_followed_blind_and_the_run_refuses_a_hand_made_one(tmp_path):
    """Case d, the join: the key `k` of the join in J, the table T has a step the walk does not read before it (a fill). With the engine's plan: refused, by the join that needs it.
    Blind (no engine): the walk cannot follow, so the drop is refused as not followed (D-0460); a copy that holds it past the gate is refused by the run, which composes the plan
    itself: before anything is built, by the join that reads the key."""
    w = join_world(tmp_path, [FILL])
    assert w.facts("T1:T", "k").refused
    with pytest.raises(AuditCopyError, match="read as a join key by step 1 of T1:J"):
        w.copy_with("T1:T", step_drop("k"))
    blind = key_drop.DropGate(w.original.raw).facts("T1:T", "k")
    assert blind.uncertain and not blind.refused
    refusal(w, "T1:T", "k", blind=True)
    error = run_error(w, w.hand_made_audit("T1:T", step_drop("k")))
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


@pytest.mark.parametrize("name, tier1, tier2, dropped, needs_it, unsure", [
    ("unpivot", [], [unpivot(["a", "b"], ["sample_id", "c"])], "a", True, True),
    ("unpivot_index", [], [unpivot(["b"], ["sample_id", "c"])], "c", True, False),
    ("str_split", [], [{"action": "polars_str_split", "columns": ["a"], "by": "1"}], "a", True, False),
    ("explode", [{"action": "polars_str_split", "columns": ["a"], "by": "1"}], [{"action": "polars_explode", "columns": ["a"]}], "a", True, False),
    ("fill_null", [], [{"action": "polars_fill_null", "columns": ["a"], "value": "zz"}], "a", True, False),
    ("fill_null_other", [], [{"action": "polars_fill_null", "columns": ["a"], "value": "zz"}], "b", False, False),
])
def test_the_steps_after_a_drop_end_as_a_plain_error_where_they_need_the_column_and_as_the_intended_table_where_they_do_not_and_the_unread_one_is_refused(
        tmp_path, name, tier1, tier2, dropped, needs_it, unsure):
    """Case e. A step after the drop that NAMES the dropped column stops the build, named; one that does not name it passes the drop through: the column gone, the rest holds. Of these
    steps only the unpivot is one the walk does not follow for the column: its drop is refused (the engine's answer is kept through `drop_built`); the others are followed (the column is
    found through them), so the drop is written and the run says the same plain thing."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": tier1, "tier2": tier2}, "B": {}}, {}, {"Q": plot("T")})
    assert w.facts("T1:T", dropped).uncertain is unsure
    before = w.original_built()
    if unsure:
        refusal(w, "T1:T", dropped)
        after = w.drop_built("T1:T", dropped)
    else:
        audit = w.copy_with("T1:T", step_drop(dropped))
        after = w.audit_built(audit)
        if needs_it:
            assert_plain(run_error(w, audit), dropped)
    if needs_it:
        assert after.error and f'"{dropped}"' in after.error, after.error
        return
    assert not after.error
    assert lost_and_rest(before.tables["T2:T"], after.tables["T2:T"]) == ({dropped}, set(), True)
    assert "T3:Q" in changed_tables(before, after)


def test_a_describe_after_a_drop_is_followed_and_gives_the_intended_table_with_the_column_gone_from_the_statistics(tmp_path):
    """Case e, describe: the step turns every column into statistics (the types change). The walk follows the column through it: the drop is written; the statistics of the dropped column
    are gone and those of the other columns are the same numbers."""
    w = world(tmp_path, {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [{"action": "polars_describe"}]}, "B": {}}, {}, {"P": plot("T")})
    assert not w.facts("T1:T", "q2").uncertain
    before, after = w.original_built().tables["T2:T"], w.audit_built(w.copy_with("T1:T", step_drop("q2"))).tables["T2:T"]
    assert lost_and_rest(before, after) == ({"q2"}, set(), True)


def test_a_pivot_after_an_unpivot_needs_the_column_the_index_names_and_the_drop_is_refused_with_a_plain_error_behind_it(tmp_path):
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [unpivot(["a", "b"], ["sample_id", "c"])], "tier2": [pivot(["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    refusal(w, "T1:T", "variable")
    built = w.drop_built("T1:T", "variable")
    assert built.error and "variable" in built.error


# ------------------------------------------------------------------------------------------------------------------- the refusal names the columns it could not follow; the audit is undone by removing the step

def test_removing_a_written_audit_step_gives_the_recipe_and_its_tables_back(tmp_path):
    """A drop the app CAN follow (the column `c` passes the unpivot as an index) is written; removing the step gives the recipe back unchanged."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    audit = start_audit(w.original.raw, "1a2b3c4d")
    assert not w.facts("T1:T", "c").uncertain
    step_id = add_step(audit, "T1:T", step_drop("c"), "because", plans=w.plans)
    assert audit.recipe != w.original.raw
    remove_step(audit, step_id)
    assert audit.recipe == w.original.raw
    assert w.audit_built(audit).tables["T1:T"].equals(w.original_built().tables["T1:T"])


def test_a_drop_of_two_columns_names_only_the_one_the_app_cannot_follow(tmp_path):
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["a"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    said = key_drop.key_drop_problem(w.original.raw, "T1:T", ["a", "c"], w.plans)
    assert said and "the column 'a' at T1:T" in said and "'c'" not in said, "c passes the unpivot as an index: it is followed"


# ------------------------------------------------------------------------------------------------------------------- h and i: what changes without an error

def test_a_same_named_column_of_a_join_changes_meaning_after_the_drop_and_the_refusal_says_so_before_anything_is_written(tmp_path):
    """Case h, the one that a build does not stop on: A and B both have `lab`; the join gave B's the suffix `_right`. Dropped from A, B's `lab` keeps its name, and a plot that draws
    `lab` now draws B's values (the plot IS drawn). Here the walk is unsure too (an unpivot of another column in tier 2 of A), so the drop is refused and the sentence names the clash:
    a plot would read the other table's column under the same name, never that the plot cannot be drawn (the review of 2026-11-21 found that false sentence)."""
    left = tsv_frame(sample_id=["s1", "s2", "s3"], lab=["A1", "A2", "A3"], x=["x1", "x2", "x3"])
    right = tsv_frame(sample_id=["s1", "s2", "s3"], lab=["B1", "B2", "B3"])
    w = world(tmp_path, {"T": left, "B": right}, {"T": {"tier1": [], "tier2": [unpivot(["x"], ["sample_id"])]}, "B": {}},
              {"J": join_of("T", "B", steps=[join_step("B")])}, {"P": plot("J", x="lab"), "Q": plot("T")})
    assert w.facts("T1:T", "lab").uncertain
    said = refusal(w, "T1:T", "lab")
    assert "'lab_right'" in said and "table B" in said and "under the name 'lab'" in said and "the plot 'P' draws 'lab'" in said
    assert "cannot be drawn" not in said and "with no error" not in said
    before, after = w.original_built().tables["T3:P"], w.drop_built("T1:T", "lab").tables["T3:P"]
    assert before["lab"].to_list() == ["A1", "A2", "A3"] and "lab_right" in before.columns
    assert after["lab"].to_list() == ["B1", "B2", "B3"] and "lab_right" not in after.columns, "a plot that draws lab is still drawn, with the other table's values: that is what the sentence says"


TOTAL = with_columns(total="pl.sum_horizontal(pl.all().exclude('sample_id'))")


def test_KNOWN_OPEN_BEHAVIOUR_a_formula_that_takes_every_column_computes_on_one_column_less_with_no_error_for_a_drop_the_app_can_follow(tmp_path):
    """Case i, the class the gate cannot see: a formula is never read (D-0356). `pl.all()`, `pl.exclude(..)` and `pl.col(<type>)` take the columns that exist when the step runs,
    so the total of three columns becomes the total of two, and nothing fails. It is true for a drop at ANY place whatever the walk knows (it is not new): the drop below is one
    the app CAN follow, it is written, and the total changes with no error and no word. KNOWN OPEN BEHAVIOUR, NOT APPROVED: it is pinned here with its evidence for the catalogue study
    of the uncertainties (D-0460); no warning is added for a drop the app can follow (not decided)."""
    certain = world(tmp_path / "certain", {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL]}, "B": {}}, {}, {"P": plot("T")})
    assert not certain.facts("T1:T", "q2").uncertain and key_drop.key_drop_problem(certain.original.raw, "T1:T", ["q2"], certain.plans) is None
    before, after = certain.original_built().tables["T2:T"], certain.audit_built(certain.copy_with("T1:T", step_drop("q2"))).tables["T2:T"]
    assert before["total"].to_list() == [111, 222, 333] and after["total"].to_list() == [101, 202, 303], "a followed drop: the total changes, no error, no word (exists today)"


def test_a_formula_that_takes_every_column_after_a_drop_the_app_cannot_follow_is_refused_and_would_have_changed_the_same_way(tmp_path):
    unsure = world(tmp_path / "unsure", {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL]}, "B": {}}, {},
                   {"P": plot("T"), "R": plot("T", tier3=[unpivot(["q1"], ["sample_id"])])})
    assert unsure.facts("T1:T", "q2").uncertain, "q2 also flows into the plot R, whose unpivot the walk does not read"
    said = refusal(unsure, "T1:T", "q2")
    assert "step 1 of T3:R (polars_unpivot)" in said
    assert unsure.drop_built("T1:T", "q2").tables["T2:T"]["total"].to_list() == [101, 202, 303]


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


def test_the_places_of_the_shipped_recipes_that_the_walk_cannot_follow_without_the_plan_are_eight_refused_blind_and_refused_as_join_keys_by_the_run(tmp_path):
    """Case f, part 1: the five of the review of 2026-11-20 and three more of `1_Abromics_general_pipeline`. Blind, the gate refuses each as a column the app cannot follow; a copy that
    holds it past the gate is refused by the run, which composes the plan and says the join that reads the key, before building anything: always a plain sentence, never a table."""
    places = blind_only_places()
    assert len(places) == 8 and {r for r, _, _ in places} == {DEMO, ABROMICS, "1_Abromics_general_pipeline"}
    for index, (recipe_id, place, column) in enumerate(places):
        orch, loaded, book, _ = uncertain_places(recipe_id, with_plan=False)
        audit = start_audit(loaded.raw, "1a2b3c4d")
        with pytest.raises(AuditCopyError, match=f"The app cannot YET follow the column '{column}' at {place}"):
            add_step(audit, place, step_drop(column), "because")
        assert audit.created == 0
        held = start_audit(loaded.raw, "1a2b3c4d")
        held.recipe = with_audit_steps(loaded.raw, [AuditStep(place, "audit_1a2b3c4d_1", {**step_drop(column), "id": "audit_1a2b3c4d_1", AUDIT_COMMENT: "because"})])
        with pytest.raises(AuditRunError) as raised:
            run_audit(orch, recipe_id, held.recipe, tmp_path / recipe_id / "orig", tmp_path / recipe_id / f"aud{index}")
        text = str(raised.value)
        assert "read as a join key by" in text and f"the column {column!r} at {place}" in text and "Resolved plan" not in text and "\n" not in text, text


# the eighteen places of `1_test_data_ST22_dummy` that stay unsure WITH the plan (the columns that flow into an unpivot the walk does not read): nine drops are INTENDED (six vanish at
# the unpivot and change nothing after it; three are the marker columns of the completion of the ids, which flow on to the tables the joins publish and are gone there, D-0613), nine are
# named by an unpivot or a later step and stop the build (PLAIN). The marker columns were not there before the completion of the ids: they are the three places added to the fifteen.
INTENDED_UNPIVOT = {("T1:Summary_quality", c) for c in ("quality_module", "taxon", "genotype", "phenotype", "cge_phenotype", "plasmid")}
MARKER_PLACES = {("T1:Summary_quality", "Summary_quality_not_in_original_data"), ("T1:Quast", "Quast_not_in_original_data"), ("T1:metadata_schema", "not_in_metadata")}
INTENDED = INTENDED_UNPIVOT | MARKER_PLACES


def test_the_eighteen_places_of_the_demo_recipe_that_stay_unsure_with_the_plan_are_all_refused_and_the_engine_would_give_nine_intended_tables_and_nine_plain_errors(tmp_path):
    """Case f, part 2, on the shipped demo recipe and its data, read only (the stored tables of each build are in `tmp_path`). Each place is refused by `add_step` with the plan; the engine's
    verdict on the drop, written as a step of the author in a copy of the recipe held in memory, is kept as a fact: six drops vanish at the unpivot and change nothing after it, three
    are marker columns of the completion of the ids (gone from the tables that carry them, also from the table of a plot), nine are named by an unpivot or a later step and stop the build."""
    orch, loaded, book, places = uncertain_places(DEMO, with_plan=True)
    assert len(places) == 18 and INTENDED <= set(places)
    before = build_all(orch, DEMO, loaded, tmp_path / "orig")
    assert not before.error
    intended, plain = [], []
    for index, (place, column) in enumerate(places):
        audit = start_audit(loaded.raw, "1a2b3c4d")
        with pytest.raises(AuditCopyError, match=f"The app cannot YET follow the column '{column}' at {place}"):
            add_step(audit, place, step_drop(column), "because", plans=book)
        assert audit.created == 0 and audit.recipe == loaded.raw
        after = build_all(orch, DEMO, author_version(loaded, with_author_step(loaded.raw, place, step_drop(column))), tmp_path / f"drop{index}")
        if after.error:
            assert column in after.error, (place, column, after.error)
            plain.append((place, column))
            continue
        table = place.split(":", 1)[1]
        changed = changed_tables(before, after)
        assert f"T1:{table}" in changed, (place, column, changed)
        if (place, column) not in MARKER_PLACES:   # a marker column is published to the tables of the plots that read it: it is gone from them too
            assert not any(name.startswith("T3:") for name in changed), (place, column, changed)
        assert all(lost_and_rest(before.tables[name], after.tables[name]) == ({column}, set(), True) for name in changed), (place, column, changed)
        intended.append((place, column))
    assert set(intended) == INTENDED and len(plain) == 9


def test_the_run_of_a_shipped_recipe_without_audit_steps_still_reuses_the_originals(tmp_path):
    orch, loaded, book, _ = uncertain_places(DEMO, with_plan=True)
    run = run_audit(orch, DEMO, start_audit(loaded.raw, "1a2b3c4d").recipe, tmp_path / "orig", tmp_path / "aud")
    assert run.affected_plots == [] and run.built_tables == []


# ------------------------------------------------------------------------------------------------------------------- the way out the refusal offers is built from facts (round 3, review 2 of 2026-11-21)

def suggestion_of(said: str) -> str:
    """The remedy part of a refusal: the text after the label."""
    assert said.count("Suggestion:") == 1 and said.endswith("."), said
    return said.split("Suggestion:", 1)[1]


def offered_places(w, place: str, column: str, *, blind: bool = False):
    """The ways out the gate offers for the refused drop (`DropGate.ways_out`): `(place, the name of the column there)`, plots' own tables only."""
    return key_drop.DropGate(w.original.raw, None if blind else w.plans).ways_out(place, column)


def assert_every_way_out_is_written_and_builds(w, place: str, column: str):
    """The sentence may never advise a step that fails: each offered place takes the drop of the column under the name it has there (`add_step`) and the engine builds the table meant,
    with that column gone from THAT plot's table and every other column of every other table as before."""
    ways = offered_places(w, place, column)
    assert ways, "the case needs a way out"
    before = w.original_built()
    for way, name in ways:
        assert way.startswith("T3:"), "only a plot's own table is ever offered"
        audit = start_audit(w.original.raw, "1a2b3c4d")
        add_step(audit, way, step_drop(name), "because", plans=w.plans)
        after = w.audit_built(audit)
        assert not after.error, (way, after.error)
        assert changed_tables(before, after) == {way}, (way, changed_tables(before, after))
        assert lost_and_rest(before.tables[way], after.tables[way]) == ({name}, set(), True)
    return ways


NO_PLACE = "the app finds no place where it can show that this drop works, so none can be written for now"
SCOPE = "removes the column for that plot only; the column stays in the other tables and plots"


def test_the_refusal_of_a_melted_column_offers_nothing_and_does_not_claim_what_it_cannot_prove(tmp_path):
    """`a` is melted by the unpivot of the tier 2, so after it `a` is a value of `variable`. No place is offered (a drop at the plot's table is an engine error, run here); the sentence
    says only that the app finds no place it can show, with no claim about tables and no scope clause (there is no place to be scoped)."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [unpivot(["a", "b"], ["sample_id", "c"])]}, "B": {}}, {}, {"Q": plot("T")})
    assert offered_places(w, "T1:T", "a") == ()
    built = w.drop_built("T3:Q", "a")
    assert built.error and '"a" not found' in built.error, "the premise: a drop of a melted column at the plot's table fails"
    said = refusal(w, "T1:T", "a")
    advice = suggestion_of(said)
    assert NO_PLACE in advice and "YET" in said
    assert "no longer a column" not in said and "only possible before" not in said and "of any table" not in said
    assert SCOPE not in said and "T3:Q" not in advice and "cannot be drawn" not in said and "row filter" not in said


def test_the_refusal_of_a_column_that_survives_at_one_plot_offers_only_that_plot_and_says_the_scope(tmp_path):
    """`q2` is refused at T1:T because the unpivot of plot R is not read, but it still exists in the table of plot P, which nothing is built after. That plot's table is the only place named
    (never T1 or T2 places, never R where it is gone); the drop is written there and the engine builds the table meant. The sentence says the drop removes the column for that plot only."""
    w = world(tmp_path, {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL]}, "B": {}}, {},
              {"P": plot("T"), "R": plot("T", tier3=[unpivot(["q1"], ["sample_id"])])})
    assert assert_every_way_out_is_written_and_builds(w, "T1:T", "q2") == (("T3:P", "q2"),)
    said = refusal(w, "T1:T", "q2")
    advice = suggestion_of(said)
    assert "T3:P" in advice and SCOPE in advice and "T3:R" not in advice and "T2:" not in advice and "T1:" not in advice
    assert "no longer a column" not in said and NO_PLACE not in advice


def test_a_renamed_column_is_offered_at_the_plot_under_the_name_it_has_there_and_the_drop_builds(tmp_path):
    """`q2` renamed to `w` in tier 2: the sentence never says the column is no longer a column; it offers the plot's table only because the walk links `w` to `q2` and the plan shows it there,
    and the suggestion names `w`, the name at that table; a drop of `w` there builds with exactly that column gone."""
    rename = {"action": "polars_rename", "mapping": {"q2": "w"}}
    w = world(tmp_path, {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL, rename]}, "B": {}}, {},
              {"P": plot("T"), "R": plot("T", tier3=[unpivot(["q1"], ["sample_id"])])})
    assert assert_every_way_out_is_written_and_builds(w, "T1:T", "q2") == (("T3:P", "w"),)
    said = refusal(w, "T1:T", "q2")
    assert "T3:P" in said and "'w'" in suggestion_of(said) and SCOPE in said
    assert "no longer a column" not in said and "of any table" not in said


def test_a_plot_that_draws_the_column_is_not_offered_and_the_sentence_says_no_place(tmp_path):
    """P draws q2: a drop of q2 at P's table would stop the plot, so it is not offered."""
    w = world(tmp_path, {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL]}, "B": {}}, {},
              {"P": plot("T", x="q2"), "R": plot("T", tier3=[unpivot(["q1"], ["sample_id"])])})
    assert offered_places(w, "T1:T", "q2") == (), "P draws q2"
    assert any(c.code == PLOT_USES_COLUMN for c in key_drop.DropGate(w.original.raw, w.plans)._index.drop_consequences("T3:P", "q2")), "the walk reads the plot that draws it"
    said = refusal(w, "T1:T", "q2")
    assert NO_PLACE in said and SCOPE not in said


def test_without_the_engines_plan_nothing_is_offered_and_the_sentence_says_the_app_finds_no_place(tmp_path):
    """The declared plan is not proof enough: blind, even a case where the recipe itself shows the column at a plot's table offers nothing."""
    w = world(tmp_path, {"T": NUMBERS, "B": B}, {"T": {"tier1": [], "tier2": [TOTAL]}, "B": {}}, {},
              {"P": plot("T"), "R": plot("T", tier3=[unpivot(["q1"], ["sample_id"])])})
    assert offered_places(w, "T1:T", "q2", blind=True) == ()
    said = refusal(w, "T1:T", "q2", blind=True)
    assert NO_PLACE in suggestion_of(said) and SCOPE not in said and "T3:P" not in suggestion_of(said)
    w2 = join_world(tmp_path / "j", [FILL])
    said2 = refusal(w2, "T1:T", "a", blind=True)
    assert NO_PLACE in suggestion_of(said2) and SCOPE not in said2


def test_no_t1_or_t2_place_is_ever_offered_because_a_later_formula_may_read_the_column(tmp_path):
    """The review's case on the demo recipe: `n50` at T1:Quast no longer offers T1:QA_population_zscore (a later formula reads it, never read by the app, D-0356), nor any T1 or T2 place."""
    orch, loaded, book, found = uncertain_places(DEMO, with_plan=True)
    gate = key_drop.DropGate(loaded.raw, book)
    assert ("T1:Quast", "n50") in found
    assert all(p.startswith("T3:") for p, _ in gate.ways_out("T1:Quast", "n50"))
    said = gate.problem("T1:Quast", ["n50"])
    assert "T1:QA_population_zscore" not in suggestion_of(said) and "T2:" not in suggestion_of(said)
    for place, column in found:
        assert all(p.startswith("T3:") for p, _ in gate.ways_out(place, column)), (place, column)


def test_every_way_out_of_every_refusal_of_the_demo_recipe_is_written_and_built_and_changes_only_that_plots_table(tmp_path):
    """The shipped demo recipe with the engine's plan: for EVERY refusal, EVERY offered plot table takes the drop (written), the engine builds, and the result against the original is exactly
    that column gone from that plot's table and nothing else changed (every other table and column identical). The count is asserted above zero so that the test cannot pass empty."""
    orch, loaded, book, found = uncertain_places(DEMO, with_plan=True)
    assert found
    gate = key_drop.DropGate(loaded.raw, book)
    before = build_all(orch, DEMO, loaded, tmp_path / "orig")
    assert not before.error
    offered = 0
    for index, (place, column) in enumerate(found):
        for j, (way, name) in enumerate(gate.ways_out(place, column)):
            audit = start_audit(loaded.raw, "1a2b3c4d")
            add_step(audit, way, step_drop(name), "because", plans=book)
            after = build_all(orch, DEMO, loaded_from_resolved(loaded, audit.recipe, book), tmp_path / f"a{index}_{j}")
            assert not after.error, (place, column, way, after.error)
            assert changed_tables(before, after) == {way}, (place, column, way, changed_tables(before, after))
            assert lost_and_rest(before.tables[way], after.tables[way]) == ({name}, set(), True), (place, column, way)
            offered += 1
    assert offered > 0


# ------------------------------------------------------------------------------------------------------------------- a plot broken by an audit step upstream (review 2, finding F1)

SELECT_C = {"action": "polars_select", "exprs": ["sample_id", "c"]}


def assert_one_line_without_plan(text: str):
    assert "\n" not in text and "Resolved plan" not in text and "SCAN" not in text and "PROJECT" not in text and "Traceback" not in text, text


def test_a_plot_broken_by_an_audit_step_of_its_tables_gives_the_plain_line_that_names_the_step_the_place_the_plot_and_the_column(tmp_path):
    """The plot Q has its own tier 3 step that selects `c`; an audit step at T2:T drops `c`. The plot's table then fails when it is collected. The run says which audit step caused it, in
    one line, as it does for a table (before this round the plot passed only its own place, so the step was not found and the engine's text, with its plan, was raised).
    MUTATION RF1 (the plot passes only [T3:Q] again) fails here."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [with_columns(z="pl.lit(1)")]}, "B": {}}, {}, {"Q": plot("T", tier3=[SELECT_C])})
    audit = w.copy_with("T2:T", step_drop("c"))
    error = run_error(w, audit)
    text = str(error)
    assert isinstance(error, AuditRunError) and error.step_id == "audit_1a2b3c4d_1" and error.place == "T2:T"
    assert text.startswith("The audit step audit_1a2b3c4d_1 at T2:T cannot be applied: ") and "plot 'Q'" in text and '"c"' in text, text
    assert_one_line_without_plan(text)


def test_a_plot_that_fails_on_its_own_step_names_the_plot_and_that_step_and_blames_no_audit_step(tmp_path):
    """The author's own tier 3 step names a column that does not exist; an unrelated audit step (a row filter at T1:T) changes the plot's key so the plot is built. The failure is the author's:
    the message names the plot and the step, in one line without the plan, and no audit step."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [with_columns(z="pl.lit(1)")]}, "B": {}}, {},
              {"Q": plot("T", tier3=[{"action": "polars_select", "exprs": ["sample_id", "nope"]}])})
    error = run_error(w, w.copy_with("T1:T", {"action": "modif_filter", "column": "a", "op": "ne", "value": "zz", "na": "keep"}))
    text = str(error)
    assert "plot 'Q'" in text and "polars_select" in text and '"nope"' in text, text
    assert "audit_1a2b3c4d" not in text and "audit step" not in text and error.step_id is None, text
    assert_one_line_without_plan(text)


def test_the_refusal_sentence_carries_the_engines_plain_sentence_without_its_plan(tmp_path):
    """When the engine's plan of a place failed, the refusal quotes the engine's own sentence but never its plan dump (several lines of `SCAN` and `PROJECT`)."""
    w = world(tmp_path, {"T": T, "B": B}, {"T": {"tier1": [], "tier2": [with_columns(z="pl.lit(1)")]}, "B": {}}, {},
              {"Q": plot("T", tier3=[{"action": "polars_select", "exprs": ["sample_id", "nope"]}])})
    audit = start_audit(w.original.raw, "1a2b3c4d")
    with pytest.raises(AuditCopyError) as raised:
        add_step(audit, "T1:T", step_drop("b"), "because", plans=w.plans)
    text = str(raised.value)
    assert text.startswith("The app cannot YET follow") and '"nope"' in text
    assert_one_line_without_plan(text)
