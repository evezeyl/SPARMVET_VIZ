"""The demo recipe keeps every sample of its metadata (DEMO-JOIN-1, Eve 2026-11-16, ledger D-0167).

Her words: "No MLST is not an NA its a unknown result / non determined. Those 12 samples should not be gone.
Raws without sample id must go. Must be a warning". So in `demo_abromics`:
- the join is a left join from the metadata: a sample without an MLST result stays, with the sequence type "Non Determined"
  (a visible step of the recipe, not a silent missing value);
- the metadata lines without a sample id are removed by a visible step;
- the description of the join says it in words, with the numbers (the recipe's own warning), and the numbers are true.

The expected numbers are read from the raw files with plain Polars, not from the engine.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_demo_join_keeps_every_sample.py -q
"""
import re
from pathlib import Path

import matplotlib
import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager
from viz_factory.viz_factory import VizFactory

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RAW = ROOT / "assets" / "test_data"
DEMO_DATA = RAW / "demo_high_integrity"
NOT_DETERMINED = "Non Determined"
NO_ID = {"", "-", '""'}


def _raw_tables():
    """The two files as plain text (every column a string), the way a person reads them."""
    mlst = pl.read_csv(next(DEMO_DATA.glob("*MLST_results*.tsv")), separator="\t", infer_schema=False)
    meta = pl.read_csv(next(DEMO_DATA.glob("*_metadata_*.tsv")), separator="\t", infer_schema=False)
    return mlst, meta


def _expected():
    mlst, meta = _raw_tables()
    meta_ids = [i for i in meta["sample_id"].to_list() if i is not None and i not in NO_ID]
    mlst_ids = set(mlst["sample_id"].to_list())
    without_mlst = sorted(set(meta_ids) - mlst_ids)
    mlst_rows_kept = sum(1 for i in mlst["sample_id"].to_list() if i in set(meta_ids))
    return {
        "samples": sorted(set(meta_ids)),
        "without_mlst": without_mlst,
        "rows": mlst_rows_kept + len(without_mlst),
        "no_id_lines": meta.height - len(meta_ids),
        "mlst_only_samples": sorted(mlst_ids - set(meta_ids)),
        "mlst_only_rows": mlst.height - mlst_rows_kept,
    }


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    work = tmp_path_factory.mktemp("demo_join")
    clear_data_analysis_recipe_cache()
    raw = ConfigManager(str(RECIPES_DIR / "demo_abromics.yaml")).raw_config
    orchestrator = DataOrchestrator(RECIPES_DIR, RAW)
    keys = orchestrator.compute_data_analysis_recipe_keys("demo_abromics")
    t1 = orchestrator.materialize_tier1("demo_abromics", "demo_join", work / "demo_join.parquet", keys=keys).collect()
    t2_lf = orchestrator.materialize_tier2("demo_abromics", "demo_join", work / "demo_join.parquet", keys=keys)
    plot = VizFactory().render(t2_lf, raw, "demo_st_by_source")
    return {"raw": raw, "t1": t1, "t2": t2_lf.collect(), "plot": pl.from_pandas(plot.data)}


def test_the_expected_numbers_are_the_ones_of_the_decision():
    expected = _expected()
    assert (len(expected["samples"]), len(expected["without_mlst"]), expected["rows"]) == (27, 12, 40)
    assert expected["no_id_lines"] == 3


def test_every_sample_of_the_metadata_is_in_the_table(built):
    expected = _expected()
    assert sorted(built["t1"]["sample_id"].unique().to_list()) == expected["samples"]
    assert built["t2"].height == built["t1"].height


def test_the_samples_without_an_mlst_result_are_there_as_not_determined(built):
    expected = _expected()
    table = built["t1"]
    for sample in expected["without_mlst"]:
        rows = table.filter(pl.col("sample_id") == sample)
        assert rows.height == 1, sample
        assert rows["sequence_type"].to_list() == [NOT_DETERMINED], sample


def test_no_sequence_type_is_missing_it_is_not_determined(built):
    assert built["t1"]["sequence_type"].null_count() == 0


def test_no_row_without_a_sample_id(built):
    assert built["t1"]["sample_id"].null_count() == 0
    assert (built["t1"]["sample_id"] == "").sum() == 0


def test_the_row_count_is_one_row_per_mlst_result_plus_one_per_sample_without_one(built):
    assert built["t1"].height == _expected()["rows"]


def test_a_sample_with_several_mlst_results_keeps_all_its_rows(built):
    mlst, _ = _raw_tables()
    most = mlst.group_by("sample_id").len().sort("len", descending=True).row(0)
    assert most[1] == 6
    assert built["t1"].filter(pl.col("sample_id") == most[0]).height == 6


def test_the_two_mlst_only_samples_are_not_in_the_table_the_description_says_so(built):
    expected = _expected()
    assert len(expected["mlst_only_samples"]) == 2 and expected["mlst_only_rows"] == 2
    present = set(built["t1"]["sample_id"].to_list())
    assert not present & set(expected["mlst_only_samples"])
    description = built["raw"]["joins"]["demo_join"]["description"]
    for sample in expected["mlst_only_samples"]:
        assert sample in description


def test_the_year_is_still_text(built):
    assert built["t1"].schema["year"] == pl.String
    assert "2024.0" not in built["t1"]["year"].drop_nulls().to_list()


def test_the_plot_is_drawn_from_every_row_and_shows_the_not_determined_bar(built):
    expected = _expected()
    plotted = built["plot"]
    assert plotted.height == expected["rows"]
    mlst, _ = _raw_tables()
    unknown_in_mlst = sum(1 for v in mlst["Sequence Type"].to_list() if v in (None, "-", "unknown"))
    assert plotted.filter(pl.col("sequence_type") == NOT_DETERMINED).height == len(expected["without_mlst"]) + unknown_in_mlst


def test_the_description_numbers_are_true(built):
    """The description of the join is the recipe's own warning: a number in it that is not true is worse than none."""
    expected = _expected()
    text = built["raw"]["joins"]["demo_join"]["description"]
    assert f"{len(expected['without_mlst'])} of the {len(expected['samples'])} samples have no MLST result" in text
    assert f"{expected['rows']} rows for {len(expected['samples'])} samples" in text
    assert f"the {expected['no_id_lines']} metadata lines that have no sample id" in text
    assert f"the {expected['mlst_only_rows']} MLST rows of {len(expected['mlst_only_samples'])} samples" in text


def test_the_recipe_description_shown_in_home_says_the_same_numbers(built):
    """HOME shows the `info:` block of the recipe (Info panel) and no join description: the warning must be there too."""
    expected = _expected()
    text = built["raw"]["info"]["description"]
    assert f"{len(expected['without_mlst'])} samples have no MLST result" in text
    assert f"{expected['rows']} rows for {len(expected['samples'])} samples" in text
    assert f"the {expected['no_id_lines']} metadata lines that have no sample id" in text
    assert f"the {expected['mlst_only_rows']} MLST rows of {len(expected['mlst_only_samples'])} samples" in text


def test_the_recipe_says_why_in_a_comment_next_to_each_step():
    """Her decision asks for visible steps: each of the three steps carries a `#` comment that says why."""
    lines = (RECIPES_DIR / "demo_abromics.yaml").read_text(encoding="utf-8").splitlines()

    def comment_above(action_line_start):
        index = next(i for i, line in enumerate(lines) if line.strip().startswith(action_line_start))
        return lines[index - 1].strip().startswith("#")

    assert comment_above("- action: polars_drop_nulls")
    assert comment_above("- action: polars_join")
    assert comment_above("- action: polars_fill_null")
    assert re.search(r"how: left", "\n".join(lines))
