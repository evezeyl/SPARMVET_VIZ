# engine: python-polars (reads the declared types and missing-value texts into Polars)
"""Declared types and explicit missing values: what a data schema says is what is read (W5, DEC27, DEC28).

The file is read as text (nothing is inferred). For every declared field the recipe states, in the schema and optionally
per field: `strip` (strip whitespace of the text first) and `null_values` (the texts that mean "missing"); then the
declared Polars dtype is applied. Nothing is hidden: no list of words, no guessed type (`2022.0` read as an
integer fails and names the value). An empty cell is a null, as in Polars itself.

Why a module of its own: the order is part of the meaning (strip, then the words, then the type) and the checker
(`utils.recipe_check`) and the engine must read the same keys.

Consumed by: DataIngestor.ingest_declared (ingestor.py). If deleted: no recipe in format 1 can be read.
"""
from typing import Any, Dict, List

import polars as pl

from utils.errors import IngestionError
from utils.polars_types import dtype_with_parameters, text_dtype_names
from utils.recipe_check import spec as recipe_spec

# @deps
# provides: function:apply_declared
# consumes: libs/utils/src/utils/polars_types.py, libs/utils/src/utils/recipe_check.py
# consumed_by: libs/ingestion/src/ingestion/ingestor.py
# doc: .claude/design/recipe_format_spec.md (7.3, 7.4; DEC27, DEC28)
# @end_deps

EXAMPLES = 3   # offending values named in an error


def _fail(message: str, tip: str) -> IngestionError:
    return IngestionError(message, tip=tip)


def schema_keys(dataset_name: str, schema: Dict[str, Any]) -> None:
    """The two keys a data schema must state (no default): `null_values` (a list of texts) and `strip` (true or false)."""
    nulls, strip = schema.get("null_values"), schema.get("strip")
    if not (isinstance(nulls, list) and all(isinstance(w, str) for w in nulls)):
        raise _fail(f"Data schema '{dataset_name}': null_values is missing or is not a list of texts",
                    "Write null_values on the schema: the texts that mean missing, or [] for none. NA is Namibia: list it only if it means missing here.")
    if not isinstance(strip, bool):
        raise _fail(f"Data schema '{dataset_name}': strip is missing or is not true or false",
                    "Write strip: true or false on the schema (whether whitespace around a text is removed before the null words are applied).")


def field_dtype(dataset_name: str, slug: str, field: Dict[str, Any]):
    """The Polars dtype of a field, or an IngestionError that names the field and what to write."""
    name = (field or {}).get("type")
    if name is None:
        raise _fail(f"Data schema '{dataset_name}', field '{slug}': type is missing",
                    f"Write a Polars dtype for '{slug}', for example type: String. Allowed: {', '.join(text_dtype_names())}.")
    if name not in text_dtype_names():
        spec = recipe_spec()
        advice = spec.get("type_suggestions", {}).get(name)
        replacement = spec.get("renamed_types", {}).get(name)
        hint = " " + " ".join(advice) if advice else f" Write {replacement}." if replacement else ""
        raise _fail(f"Data schema '{dataset_name}', field '{slug}': '{name}' is not a Polars dtype that a text file can hold.{hint}",
                    f"Allowed: {', '.join(text_dtype_names())}.")
    try:
        return name, dtype_with_parameters(name, field)
    except KeyError as exc:
        raise _fail(f"Data schema '{dataset_name}', field '{slug}': type {name} needs the key {exc}",
                    "Enum needs categories (the levels, in order); Decimal needs precision (and scale).")


def _parse(column: pl.Expr, name: str, dtype, field: Dict[str, Any]) -> pl.Expr:
    """The parse of a cleaned text column; a value that does not fit becomes null here and is reported by the caller."""
    text = column
    if name == "String":
        return text
    if name == "Boolean":
        return text.str.to_lowercase().replace_strict({"true": True, "false": False}, default=None, return_dtype=pl.Boolean)
    if name == "Date":
        return text.str.to_date(format=field.get("format"), strict=False)
    if name == "Datetime":
        return text.str.to_datetime(format=field.get("format"), time_unit=field.get("time_unit", "us"),
                                    time_zone=field.get("time_zone"), strict=False)
    if name == "Time":
        return text.str.to_time(format=field.get("format"), strict=False)
    return text.cast(dtype, strict=False)


def _what_is_held(shown: List[str], count: int) -> str:
    """'the value X' for one value, 'the values X, Y' for several."""
    return f"the value {shown}" if count == 1 else f"the values {shown}"


def _type_hint(slug: str, type_name: str) -> str:
    """What to try when a column's values do not fit its type: the suggestion that makes sense for that type."""
    base = f"Suggestion: correct the data, or declare the type that column '{slug}' really has"
    if type_name in ("Float64", "Float32", "Float16", "Decimal"):
        return f"{base} (String if it is text). "
    if type_name.startswith(("Int", "UInt")):
        return f"{base} (Float64 for decimals, String if it is text). "
    if type_name in ("Date", "Datetime", "Time"):
        return f"{base} (String if it is text). Suggestion: write `format` for '{slug}' if the dates are written in a form other than year-month-day, for example %d/%m/%Y. "
    if type_name == "Boolean":
        return f"{base} (String if it is text). Suggestion: a Boolean reads the words true and false (upper or lower case); change the data. "
    return f"{base}. "


def apply_declared(lf: pl.LazyFrame, dataset_name: str, schema: Dict[str, Any], fields: Dict[str, Any]) -> pl.LazyFrame:
    """Strip, apply the null words, then parse each declared column with its declared dtype (all text on entry)."""
    schema_keys(dataset_name, schema)
    present = lf.collect_schema().names()
    cleaned: List[pl.Expr] = []
    parsed: List[pl.Expr] = []
    checks: Dict[str, pl.Expr] = {}
    for slug, field in fields.items():
        field = field or {}
        name, dtype = field_dtype(dataset_name, slug, field)
        if slug not in present:
            continue
        words = field.get("null_values", schema["null_values"])
        strip = field.get("strip", schema["strip"])
        text = pl.col(slug).str.strip_chars() if strip else pl.col(slug)
        if words:
            text = pl.when(text.is_in(words)).then(None).otherwise(text)
        cleaned.append(text.alias(slug))
    lf = lf.with_columns(cleaned)
    for slug, field in fields.items():
        field = field or {}
        if slug not in present:
            continue
        name, dtype = field_dtype(dataset_name, slug, field)
        if name == "String":
            continue
        parsed.append(_parse(pl.col(slug), name, dtype, field).alias(slug))
        checks[slug] = pl.col(slug).is_not_null() & _parse(pl.col(slug), name, dtype, field).is_null()
    if not parsed:
        return lf
    # one pass finds every value that the declared type cannot read, so the error names the column and the values
    bad = lf.select([pl.col(slug).filter(flag).unique(maintain_order=True).head(EXAMPLES).implode().alias(slug) for slug, flag in checks.items()]).collect()
    problems, tips = [], []
    for slug in checks:
        values = bad[slug][0].to_list()
        if not values:
            continue
        shown = ", ".join(repr(v) for v in values)
        if fields[slug]["type"] == "Enum":
            levels = ", ".join(str(c) for c in fields[slug]["categories"])
            plural = len(values) != 1
            problems.append(f"The column '{slug}' is declared as Enum with the values {levels}. The data holds {_what_is_held(shown, len(values))}, "
                            f"which {'are' if plural else 'is'} not in that list.")
            tips.append(f"Suggestion: add the value to `categories` of '{slug}' in the recipe if it is a real level. "
                        "Suggestion: correct the data if it is a typing error (the values are compared exactly, upper and lower case differ).")
        else:
            problems.append(f"The column '{slug}' is declared as {fields[slug]['type']}. The data holds {_what_is_held(shown, len(values))}, "
                            "which cannot be read as that type.")
            tips.append(_type_hint(slug, fields[slug]["type"]) + "Suggestion: list the word in null_values if it means missing.")
    if problems:
        raise _fail(f"Data schema '{dataset_name}': values that do not fit the declared type. " + " ".join(problems), " ".join(dict.fromkeys(tips)))
    return lf.with_columns(parsed)
