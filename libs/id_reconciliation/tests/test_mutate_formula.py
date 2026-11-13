"""The `mutate` step of an ID transformation takes a Polars formula from a recipe: checked, never run as Python.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/id_reconciliation/tests/test_mutate_formula.py -q
"""
import polars as pl
import pytest

from id_reconciliation.core import apply_recode_step
from id_reconciliation.data_structures import IdTransformation


def run(step, values=("A_1", "B_2")):
    df = pl.DataFrame({"id": list(values)})
    return apply_recode_step(df, "id", IdTransformation(ref_column="id", target_column="id", steps=[step]))


def test_a_polars_formula_works():
    out = run({"action": "mutate", "expression": "pl.col('id').str.to_lowercase()"})
    assert out["id"].to_list() == ["a_1", "b_2"]


@pytest.mark.parametrize("expression", [
    "__import__('os').system('echo hacked')",
    "pl.read_csv('/etc/passwd')",
    "pl.col('id').map_elements(str)",
])
def test_an_attack_is_refused_before_it_runs(expression):
    with pytest.raises(ValueError):
        run({"action": "mutate", "expression": expression})
