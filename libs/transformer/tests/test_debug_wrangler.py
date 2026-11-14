"""The @verify runner `debug_wrangler.py` writes what the wrangler gives for a recipe (ACTION-RECIPES-1).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_debug_wrangler.py -q
"""
from pathlib import Path

import polars as pl
import pytest

import debug_wrangler

ROOT = Path(__file__).resolve().parents[3]
PAIR = "libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml"


def test_it_writes_the_result_of_a_pair(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    out = tmp_path / "cast.tsv"
    assert debug_wrangler.main(["--data-analysis-recipe", PAIR, "--output", str(out)]) == 0
    got = pl.read_csv(out, separator="\t")
    assert got["n"].dtype == pl.Float64 and got["n"].to_list()[:3] == [1.0, 2.0, 3.0]


def test_a_data_override_replaces_the_file_of_the_recipe(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    data = tmp_path / "other.tsv"
    data.write_text("id\tg\tn\tf\ts\nz\tq\t7\t0.5\tw\n")
    out = tmp_path / "o.tsv"
    debug_wrangler.main(["--data-analysis-recipe", PAIR, "--data", str(data), "--output", str(out)])
    assert pl.read_csv(out, separator="\t")["n"].to_list() == [7.0]


def test_a_failing_step_fails_the_runner(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    bad = tmp_path / "bad_data_analysis_recipe.yaml"
    bad.write_text((ROOT / PAIR).read_text().replace("columns: [n]", "columns: [no_such_column]"))
    with pytest.raises(Exception):
        debug_wrangler.main(["--data-analysis-recipe", str(bad), "--output", str(tmp_path / "o.tsv")])
