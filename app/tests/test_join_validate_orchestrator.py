"""A refused `validate` of a join reaches the caller of the real orchestrator in plain words (D35b, PROVISIONAL).

The unit tests of `join_diagnosis` prove the message; this one proves the wiring: `DataOrchestrator.materialize_tier1` hands the
assembler's `join_checks` to `write_anchor`, so the message names the right recipe, join and step. Without the wiring the caller gets
Polars' raw "join keys did not fulfill" text.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_join_validate_orchestrator.py -q
"""
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import bump
from app.tests.test_orchestrator_fails_loudly import _build, _two_tables


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _with_validate(tmp_path, right_rows, validate="m:1"):
    world = _two_tables(tmp_path)
    (world.data_dir / "R.tsv").write_text("sample_id\tyear\n" + "".join(f"{k}\t{y}\n" for k, y in right_rows))
    entry = world.data_analysis_recipes_dir / "tiny.yaml"
    text = entry.read_text()
    assert "how: left\n" in text
    entry.write_text(text.replace("how: left\n", f"how: left\n          validate: {validate}\n", 1))
    bump(entry)
    return world


def test_a_refused_validate_names_the_recipe_the_join_the_step_and_the_table(tmp_path):
    world = _with_validate(tmp_path, [("s1", 2020), ("s1", 2021), ("s2", 2022)])
    with pytest.raises(Exception) as caught:
        _build(world)
    text = f"{caught.value} {getattr(caught.value, 'tip', '')}"
    assert "did not fulfill" not in text, text
    for part in ("tiny", "join 'C'", "assembly step 1", "'R'", "validate 'm:1'", "sample_id", "s1", "2 times"):
        assert part in text, f"{part!r} is not in: {text}"


def test_a_validate_that_is_met_builds(tmp_path):
    world = _with_validate(tmp_path, [("s1", 2020), ("s2", 2021), ("s3", 2022)])
    assert _build(world).height == 3
