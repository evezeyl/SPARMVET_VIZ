# @deps
# provides: class:DataSanitizer, method:apply
# consumed_by: libs/ingestion/src/ingestion/ingestor.py
# doc: .claude/tasks/tasks.md#INGEST-SANITIZE-1
# @end_deps
import polars as pl

_NULL_TOKENS: frozenset[str] = frozenset({
    "", "NA", "N/A", "None", "null", "NaN", "-",
    "na", "n/a", "none", "nan", "NULL", "n.a.", "N.A.",
})


class DataSanitizer:
    """Lightweight pre-wrangling sanitization applied at ingestion time.

    Runs after column rename, before type casting, so null normalization
    happens on String columns before they are cast to numeric or date types.
    Two operations only — both non-destructive and lazy-safe:
    - Strip leading/trailing whitespace from all String columns.
    - Replace common null sentinel strings with actual Polars nulls.
    """

    def __init__(self, extra_null_tokens: set[str] | None = None):
        self._null_tokens = _NULL_TOKENS | (extra_null_tokens or set())

    def strip_whitespace(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        string_cols = [
            name for name, dtype in lf.collect_schema().items()
            if dtype == pl.String
        ]
        if not string_cols:
            return lf
        return lf.with_columns([pl.col(c).str.strip_chars() for c in string_cols])

    def normalize_nulls(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        # collect_schema() is used (not collect()) — stays lazy
        string_cols = [
            name for name, dtype in lf.collect_schema().items()
            if dtype == pl.String
        ]
        if not string_cols:
            return lf
        null_list = list(self._null_tokens)
        return lf.with_columns([
            pl.when(pl.col(c).is_in(null_list))
            .then(None)
            .otherwise(pl.col(c))
            .alias(c)
            for c in string_cols
        ])

    def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        lf = self.strip_whitespace(lf)
        lf = self.normalize_nulls(lf)
        return lf
