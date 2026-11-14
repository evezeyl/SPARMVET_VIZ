"""A column that is entirely "not recorded" is kept as missing, and only an explicit step removes it (DATA-NA-ISOLATION-1).

Eve 2026-11-14: `metadata_isolation_method` holds `NA` in all 1315 rows of the delivered VirulenceFinder file because
the user did not record it. `NA` there means "not recorded", an inconclusive answer that must be kept as missing, not
guessed and not dropped silently. The recipe may drop the column with a `polars_drop` step: this is the real-data test
of that step.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_all_missing_column.py -q
"""
from pathlib import Path

import polars as pl

import transformer.actions  # noqa: F401
from ingestion.ingestor import DataIngestor
from transformer.data_wrangler import DataWrangler

FILE = Path(__file__).resolve().parents[3] / "assets/test_data/duplicated_1_test_data_ST22_dummy/VirulenceFinder.tsv"
COLUMN = "metadata_isolation_method"


def _schema(null_values):
    return {
        "source": {"type": "local_tsv", "path": str(FILE)},
        "null_values": null_values, "strip": False,
        "input_fields": {"sample_id": {"type": "String"}, COLUMN: {"type": "String"}},
    }


def _ingest(null_values):
    lf, _ = DataIngestor(str(FILE.parent)).ingest("VirulenceFinder", _schema(null_values))
    return lf.collect()


def test_the_all_na_column_is_read_as_missing_and_kept():
    df = _ingest(["NA"])
    assert COLUMN in df.columns and df.height == 1315
    assert df[COLUMN].null_count() == 1315


def test_without_na_in_the_missing_values_the_text_is_kept_as_it_is():
    df = _ingest([""])
    assert df[COLUMN].null_count() == 0 and df[COLUMN].unique().to_list() == ["NA"]


def test_an_explicit_drop_step_removes_the_column_and_nothing_else():
    lf, _ = DataIngestor(str(FILE.parent)).ingest("VirulenceFinder", _schema(["NA"]))
    out = DataWrangler().run(lf, [{"action": "polars_drop", "columns": [COLUMN], "strict": True}]).collect()
    assert out.columns == ["sample_id"] and out.height == 1315


def test_the_recipe_can_say_that_na_is_missing_for_this_field_only():
    """The per-field override: the schema keeps `NA` as text, the field says it is a real missing value (not recorded)."""
    schema = _schema([""])
    schema["input_fields"][COLUMN] = {"type": "String", "null_values": ["NA"]}
    lf, _ = DataIngestor(str(FILE.parent)).ingest("VirulenceFinder", schema)
    df = lf.collect()
    assert df[COLUMN].null_count() == 1315
