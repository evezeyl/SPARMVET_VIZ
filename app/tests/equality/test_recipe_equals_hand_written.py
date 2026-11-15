"""Each table the engine builds from the recipe `2_test_data_ST22_dummy` equals the one written by hand (EQUALITY-CHECK-1).

PROVISIONAL. The hand-written side (`reference_2_test_data_ST22_dummy.py`) is plain Polars and plotnine, written from
the meaning of the recipe; see `README.md` for the independence rule. Data: the shipped clean files, and a deliberately
dirty copy (`make_dirty_data.py`). A case that differs today is not hidden here: it runs in `test_findings_open.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/equality -q
"""
import polars as pl
import pytest

from app.tests.equality import scenarios
from app.tests.equality.checks import all_cases, check
from app.tests.equality.open_findings import OPEN_FINDINGS

CASES = [c for c in all_cases() if c.id not in OPEN_FINDINGS]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_engine_equals_hand_written(case):
    check(case)


def test_emptied_table_is_really_empty():
    """The scenario is only useful if the filter did empty the plasmid table (and nothing else)."""
    hand = lambda name: scenarios.hand_table("emptied", name)  # noqa: E731
    assert hand("plasmid_data").height == 0 and hand("Plasmid_Profile_Joint").height == 0
    assert hand("amr_data").height > 0 and hand("AMR_Profile_Joint").height > 0


def test_the_dirty_data_exercises_what_the_clean_data_does_not():
    """The dirty data must change the result: filters remove rows, keys are lost, values are missing."""
    clean = lambda name: scenarios.hand_table("clean", name)  # noqa: E731
    dirty = lambda name: scenarios.hand_table("dirty", name)  # noqa: E731
    assert clean("amr_data").height == 70 and clean("plasmid_data").height == 163  # the shipped filters remove nothing
    assert dirty("amr_data").height < 70 + 2  # rows removed by the filters although 2 were added
    assert dirty("plasmid_data").height < 163 + 3
    assert dirty("metadata_schema").null_count().row(0) != (0, 0, 0, 0)  # missing values in the metadata
    assert dirty("metadata_schema").filter(pl.col("sample_id").is_not_null())["sample_id"].is_duplicated().any()
    assert dirty("amr_data").filter(pl.col("identity").is_nan()).height > 0  # a NaN is kept by a >= filter
    assert dirty("AMR_Profile_Joint").height < dirty("amr_data").height + 1  # keys lost in the join
    assert dirty("amr_data").join(dirty("metadata_schema"), on="sample_id", how="anti").height > 0
