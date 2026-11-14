"""The @verify runner `debug_assembler.py` writes what the engine gives for a pipeline recipe (ACTION-RECIPES-1).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_debug_assembler.py -q
"""
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

import debug_assembler

ROOT = Path(__file__).resolve().parents[3]
JOIN_PAIR = "libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml"
SHIPPED = "config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml"


def test_it_writes_the_join_of_the_pair(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    debug_assembler.run_assembler_debug(JOIN_PAIR, None, str(tmp_path))
    got = pl.read_parquet(tmp_path / "EVE_contracted_polars_join.parquet")
    left = pl.read_csv(ROOT / "libs/transformer/tests/data/polars_join_test.tsv", separator="\t", infer_schema_length=0)
    right = pl.read_csv(ROOT / "libs/transformer/tests/data/polars_join_test_right.tsv", separator="\t", infer_schema_length=0)
    assert got.columns == ["id", "g", "n", "f", "s", "v"] and got["id"].to_list() == ["a", "b", "c", "d"]
    assert got["v"].to_list() == [10, 20, None, None] and left.height == 4 and right.height == 3
    assert (tmp_path / "EVE_assembly_polars_join.parquet").exists() and (tmp_path / "EVE_contracted_polars_join.tsv").exists()


def test_a_step_that_names_a_missing_ingredient_fails_and_is_not_skipped(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    bad = tmp_path / "bad_data_analysis_recipe.yaml"
    bad.write_text((ROOT / JOIN_PAIR).read_text().replace("right_ingredient: polars_join_right", "right_ingredient: nothing_like_it"))
    with pytest.raises(Exception, match="nothing_like_it"):
        debug_assembler.run_assembler_debug(str(bad), None, str(tmp_path / "o"))


def test_a_shipped_pipeline_recipe_is_assembled_for_every_join(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    debug_assembler.run_assembler_debug(SHIPPED, None, str(tmp_path))
    files = sorted(tmp_path.glob("EVE_contracted_*.parquet"))
    assert len(files) >= 5 and all(pl.read_parquet(f).height > 0 for f in files)
