"""The multi-resistance flag of `2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml` (RECIPE-FIXES-1, item A1).

Rule written in the recipe: a sample is multi-resistant when its hits name more than one distinct predicted phenotype
(a drug, not a drug class); a missing phenotype is not counted as one. This file runs the real shipped steps on a small
made-up table where the missing value decides the answer, and on the shipped data (16 of 38 samples, listed).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_amr_multiresistance_formula.py -q
"""
import contextlib
import io
from pathlib import Path

import polars as pl
import pytest
import yaml

import transformer.actions  # noqa: F401  (loads the registry)
from transformer.data_assembler import DataAssembler

ROOT = Path(__file__).resolve().parents[2]
FRAGMENT = ROOT / "config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml"
RAW = ROOT / "assets/test_data/1_test_data_ST22_dummy"


def _steps():
    return yaml.safe_load(FRAGMENT.read_text())["steps"]


def _flags(hits):
    """Run the shipped steps on {sample: [phenotype or None, ...]} and return {sample: Multiresistant}."""
    rows = [(s, f"g{i}", p, f"a{i}") for s, phenos in hits.items() for i, p in enumerate(phenos)]
    amr = pl.DataFrame(rows, schema={"sample_id": pl.String, "gene": pl.String, "predicted_phenotype": pl.String,
                                     "accession": pl.String}, orient="row")
    meta = pl.DataFrame({"sample_id": list(hits), "Source": "Layer", "Year": [2024.0] * len(hits), "Country": "Norway"})
    assembler = DataAssembler({"amr_data": amr.lazy(), "metadata_schema": meta.lazy()}, recipe_id="t", join_id="t")
    with contextlib.redirect_stdout(io.StringIO()):
        out = assembler.assemble(_steps()).collect()
    return {s: set(g["Multiresistant"]) for (s,), g in out.group_by("sample_id")}


def test_the_comment_and_the_formula_say_the_same():
    text = FRAGMENT.read_text()
    assert "more than one distinct predicted phenotype" in text and "missing phenotype is not counted" in text
    assert ".drop_nulls().n_unique().over('sample_id') > 1" in text


def test_a_missing_phenotype_does_not_count_by_itself():
    """The case the formula changed for: one drug plus one missing value is NOT multi-resistant."""
    assert _flags({"s1": ["tetracycline", None]}) == {"s1": {"No"}}


def test_cases_around_the_missing_value():
    flags = _flags({
        "two_drugs": ["tetracycline", "ampicillin"],
        "one_drug": ["tetracycline"],
        "one_drug_twice": ["tetracycline", "tetracycline"],
        "all_missing": [None, None],
        "two_drugs_and_missing": ["tetracycline", "ampicillin", None],
        "spelling_and_blanks": ["Tetracycline", " tetracycline "],
    })
    assert flags == {"two_drugs": {"Yes"}, "one_drug": {"No"}, "one_drug_twice": {"No"}, "all_missing": {"No"},
                     "two_drugs_and_missing": {"Yes"}, "spelling_and_blanks": {"No"}}


def test_the_flag_is_the_same_on_every_row_of_a_sample():
    assert _flags({"s": ["a", "b", None]}) == {"s": {"Yes"}}


def _plain_flags(missing_counts: bool) -> dict:
    """Per sample, from the raw files with plain Polars (no recipe, no engine): more than one distinct phenotype, among the samples in the metadata."""
    raw = pl.read_csv(RAW / "test_data_ResFinder_20260307_105756.tsv", separator="\t", infer_schema_length=0)
    meta = pl.read_csv(RAW / "test_metadata_20260307_105756.tsv", separator="\t", infer_schema_length=0)
    p = pl.col("Predicted Phenotype").str.strip_chars().str.to_lowercase()
    column = p if missing_counts else p.drop_nulls()
    per_sample = raw.filter(pl.col("sample_id").is_in(meta["sample_id"].implode())).group_by("sample_id").agg((column.n_unique() > 1).alias("multi"))
    return dict(per_sample.iter_rows())


def test_shipped_data_the_change_moves_no_sample_16_of_38_per_sample():
    """Plain Polars from the raw files, with and without counting a missing phenotype, and the engine: the same flag for each of the 38 samples."""
    from app.tests.equality.engine_black_box import run_engine
    old, new = _plain_flags(missing_counts=True), _plain_flags(missing_counts=False)
    assert len(new) == 38 and sum(new.values()) == 16
    assert old == new  # no missing phenotype in the shipped file: the change moves nothing
    table = run_engine(ROOT / "config/data_analysis_recipes/pipelines", "2_test_data_ST22_dummy", ["AMR_Profile_Joint"], {}).t1["AMR_Profile_Joint"]
    assert not isinstance(table, BaseException)
    engine = {s: set(g["Multiresistant"]) for (s,), g in table.group_by("sample_id")}
    assert engine == {s: {"Yes" if flag else "No"} for s, flag in new.items()}
