"""Only an AUDIT step is refused for dropping a key column; the recipe's OWN steps may drop it anywhere (D-0358, the owner's answer of 2026-11-20).

Her words: "what if we have a eg count step on T3 and no more need on an ID we can still drop it in the recipe - that is only the audit that will block the key that is
used correct ?" The answer was yes. So: an author's `polars_drop` of an ID or key column is never refused (not by the checker in the run profile, not by the build, not by the
walk); if a later step still needs the column, the recipe fails as any recipe fault does (here: the plain-Polars replay raises at the join). The place-aware rule
(`utils.key_drop`) is asked only for audit steps (`add_step`, `integrity_errors`, the checker's audit profile, HOME's drop and restore); the last test proves by the source
that no other caller exists.

The staged recipe is the one of `test_audit_check_with_registry.py` (A and B joined on `sample_id` into J, a plot p on J), checked with the real registries of the app. The
"plain-Polars oracle" here is a few lines of Polars written in this file: it replays the tables, the join, the tier 2 and the plot's tier 3 and knows nothing of the rule.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_author_drops.py -q
"""
import ast
from pathlib import Path

import polars as pl
import pytest

from app.tests.test_audit_check_with_registry import check
from app.tests.test_audit_check_with_registry import recipe as staged
from utils.audit_copy import AuditCopyError, add_step, integrity_errors, start_audit

COUNT = {"action": "polars_with_columns", "named_exprs": {"n": "pl.len()"}}
DROP_KEY = {"action": "polars_drop", "columns": ["sample_id"]}
A = pl.DataFrame({"sample_id": ["s1", "s2", "s3"], "v": [1.0, 2.0, 3.0]})
B = pl.DataFrame({"sample_id": ["s1", "s2", "s3"], "w": [1, 2, 3], "g": ["x", "y", "z"]})
ROOT = Path(__file__).resolve().parents[2]


def recipe(a_tier1=(), tier2=(), tier3=()):
    raw = staged()
    plot = next(iter(raw["analysis_groups"].values()))["plots"]["p"]
    plot["mapping"] = {"x": "v"}                                                        # the plot draws `v`, not the key
    raw["data_schemas"]["A"]["tier1"]["steps"] = list(a_tier1)
    if tier2:
        raw["joins"]["J"]["tier2"] = {"steps": list(tier2)}
    if tier3:
        plot["tier3"] = {"steps": list(tier3)}
    return raw


def apply(df, step):
    if step["action"] == "polars_drop":
        return df.drop(*step["columns"])
    if step["action"] == "polars_with_columns":
        return df.with_columns(**{name: eval(text, {"pl": pl}) for name, text in step["named_exprs"].items()})   # noqa: S307 - test formulas
    raise ValueError(step["action"])


def replay(raw):
    """Plain Polars: A, then the join with B on `sample_id`, then tier 2 of J, then tier 3 of p. Returns {table: frame}; a step that cannot run raises, as a recipe fault does."""
    a = A
    for step in raw["data_schemas"]["A"]["tier1"]["steps"]:
        a = apply(a, step)
    joined = a.join(B, on="sample_id", how="left", maintain_order="left")
    t2 = joined
    for step in (raw["joins"]["J"].get("tier2") or {}).get("steps", []):
        t2 = apply(t2, step)
    t3 = t2
    for step in (next(iter(raw["analysis_groups"].values()))["plots"]["p"].get("tier3") or {}).get("steps", []):
        t3 = apply(t3, step)
    return {"T1:J": joined, "T2:J": t2, "T3:p": t3}


def test_the_recipe_without_any_drop_is_accepted_and_builds_the_reference_for_the_next_tests():
    raw = recipe()
    assert check(raw, "run") == [] and set(replay(raw)) == {"T1:J", "T2:J", "T3:p"}


def test_1_own_tier3_steps_that_count_rows_and_then_drop_the_key_are_accepted_and_built():
    """A plot counts the rows, then no longer needs the ID and drops it: the checker accepts it in the run profile, and plain Polars builds it with `sample_id` gone and `n` there."""
    raw = recipe(tier3=[COUNT, DROP_KEY])
    assert check(raw, "run") == []
    built = replay(raw)
    assert "sample_id" not in built["T3:p"].columns and "n" in built["T3:p"].columns
    assert "sample_id" in built["T1:J"].columns                                              # the join before it still had the key


def test_2_own_tier2_steps_that_drop_the_key_after_the_last_join_are_accepted_and_built():
    raw = recipe(tier2=[DROP_KEY])
    assert check(raw, "run") == []
    built = replay(raw)
    assert "sample_id" not in built["T2:J"].columns and "v" in built["T3:p"].columns


def test_the_checker_never_refuses_an_authors_drop_of_a_key_in_the_run_profile_the_audit_codes_are_for_audit_steps():
    for raw in (recipe(tier3=[COUNT, DROP_KEY]), recipe(tier2=[DROP_KEY])):
        assert [e.code for e in check(raw, "run") if e.code.startswith("AU")] == []


def test_an_authors_drop_of_a_key_before_the_join_that_needs_it_is_an_ordinary_recipe_fault_not_a_refusal():
    """If a later step still needs the column, the recipe fails as any recipe fault: plain Polars raises at the join, and no rule of keys refused it."""
    raw = recipe(a_tier1=[DROP_KEY])
    assert [e.code for e in check(raw, "run") if e.code.startswith("AU")] == []
    with pytest.raises(pl.exceptions.ColumnNotFoundError, match="sample_id"):
        replay(raw)


def test_3_the_same_drop_as_an_audit_step_where_a_later_join_uses_the_key_is_refused_naming_the_join():
    audit = start_audit(recipe(), "1a2b3c4d")
    for place in ("T1:A", "T1:B"):
        with pytest.raises(AuditCopyError, match=f"column 'sample_id' at {place}: it is read as a join key by step 1 of T1:J"):
            add_step(audit, place, DROP_KEY, "why")
    assert audit.created == 0


@pytest.mark.parametrize("place", ["T1:J", "T2:J", "T3:p"])
def test_4_the_same_drop_as_an_audit_step_where_no_later_join_uses_the_key_is_accepted(place):
    audit = start_audit(recipe(), "1a2b3c4d")
    add_step(audit, place, DROP_KEY, "no longer needed")
    assert integrity_errors(audit.recipe, recipe()) == []
    assert [e.code for e in check(audit.recipe, "audit") if e.code.startswith("AU")] == []


def test_the_rule_is_asked_only_for_audit_steps_by_the_source():
    """No caller of `utils.key_drop` outside the audit paths: in `utils`, `audit_copy` (add_step, integrity_errors) and the checker's `audit_step_keys` (plus the annotation of
    `__init__`) only; in `app`, the drop of the column box (`_col_drop_to_audit`, inside `define_filter_audit_server`) and the restore of stored audit steps. The author's steps are walked by `_Check.steps` with `audit=False` and never
    reach the rule."""
    users = {}
    for path in list((ROOT / "libs/utils/src/utils").glob("*.py")) + list((ROOT / "app").rglob("*.py")):
        if "tests" in path.parts or path.name == "key_drop.py":
            continue
        for fn in [n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if any(isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) and a.value.id == "key_drop" for a in ast.walk(fn)):
                users.setdefault(path.name, set()).add(fn.name)
    assert users == {"audit_copy.py": {"_key_drop", "integrity_errors"}, "recipe_check.py": {"__init__", "audit_step_keys"},
                     "session_manager.py": {"split_key_drops"}, "filter_and_audit_handlers.py": {"_col_drop_to_audit", "define_filter_audit_server"}}, users
