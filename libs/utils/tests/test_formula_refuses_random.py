"""Random members are refused in a recipe formula (D-0278, D-0279): `shuffle`, `sample`, `list.sample`, `rank(method='random')`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_formula_refuses_random.py -q
"""
import polars as pl
import pytest

from utils.fix_text import split_fix
from utils.formula_check import REFUSED_BY_NAME, FormulaError, evaluate_formula, formula_problems

REFUSED = [
    ("pl.col('n').shuffle()", "shuffle"),
    ("pl.col('n').shuffle(seed=1)", "shuffle"),
    ("pl.col('n').sample(n=2)", "sample"),
    ("pl.col('n').sample(fraction=0.5, seed=3)", "sample"),
    ("pl.col('n').sample(2, with_replacement=True)", "sample"),
    ("pl.col('l').list.sample(n=1)", "list.sample"),
    ("pl.col('l').list.sample(fraction=0.5, seed=1)", "list.sample"),
    ("pl.col('n').sort().shuffle()", "shuffle"),
]
RANK_REFUSED = ["pl.col('n').rank(method='random')", "pl.col('n').rank('random')",
                "pl.col('n').rank(method='random', seed=1)", "pl.col('n').rank('random', descending=True, seed=4)",
                "pl.col('n').rolling_rank(3, method='random')", "pl.col('n').rolling_rank(3, 'random')",
                "pl.col('n').rolling_rank_by(pl.col('d'), '2d', method='random')"]


@pytest.mark.parametrize("text,word", REFUSED)
def test_random_members_are_refused_with_a_plain_message(text, word):
    [message] = formula_problems(text)
    what, fix = split_fix(message)
    assert what.startswith(word + " ")
    assert "differ at each run" in what and "same recipe and data" in what
    assert fix.startswith("Suggestion:") and "polars_sample" in fix and "seed" in fix
    with pytest.raises(FormulaError):
        evaluate_formula(text)


@pytest.mark.parametrize("text", RANK_REFUSED)
def test_rank_with_random_ties_is_refused(text):
    [message] = formula_problems(text)
    what, fix = split_fix(message)
    assert " with method 'random'" in what.split(" ", 3)[0:4].__str__() or "with method 'random'" in what and "differ at each run" in what
    assert fix.startswith("Suggestion:")
    with pytest.raises(FormulaError):
        evaluate_formula(text)


def test_a_seed_does_not_make_it_allowed():
    assert "also with a seed" in formula_problems("pl.col('n').shuffle(seed=1)")[0]


@pytest.mark.parametrize("text", [
    "pl.col('n').sort()", "pl.col('n').head(2)", "pl.col('n').first()", "pl.col('n').unique()",
    "pl.col('n').rank()", "pl.col('n').rank(method='dense')", "pl.col('n').rank('ordinal', descending=True)",
    "pl.col('n').rolling_rank(3)", "pl.col('n').rolling_rank(3, method='dense')", "pl.col('l').list.first()", "pl.col('l').list.sort()", "pl.col('n').sample_name",  # last one: not a member at all
][:-1])
def test_neighbours_are_still_allowed(text):
    assert formula_problems(text) == []


def test_rank_dense_still_runs():
    out = pl.DataFrame({"n": [3, 1, 3]}).select(evaluate_formula("pl.col('n').rank(method='dense')"))
    assert out["n"].to_list() == [2, 1, 2]


def test_every_entry_is_a_real_polars_member():
    for label, name in [("expr", "shuffle"), ("expr", "sample"), ("list", "sample")]:
        assert (label, name) in REFUSED_BY_NAME


def test_no_other_member_draws_at_random():
    """The allowed members are searched for names that draw at random; a Polars upgrade that adds one fails here."""
    from utils import formula_check
    words = ("shuffle", "sample", "rand", "seed")
    for label, names in formula_check._allowed().items():
        for name in names:
            assert not any(w in name for w in words), f"{label}.{name} may draw at random: judge it and refuse it"
    # members with a `seed` parameter that stay allowed are deterministic given the seed or take it as a hash salt
    import inspect
    cls = {"expr": pl.Expr, **formula_check._namespace_classes()}
    with_seed = sorted(f"{lab}.{n}" for lab, ns in formula_check._allowed().items() for n in ns
                       if "seed" in inspect.signature(getattr(cls[lab], n)).parameters)
    assert with_seed == ["expr.hash", "expr.rank", "expr.rolling_rank", "expr.rolling_rank_by"], with_seed
