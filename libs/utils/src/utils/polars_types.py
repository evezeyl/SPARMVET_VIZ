"""The Polars dtypes that a text file can hold, read from the installed Polars by trying each one on the CSV reader.

A recipe declares the type of a column with a Polars dtype name, and the declared dtype is handed to the CSV reader (spec
decision DEC27). The list is not kept by hand: each dtype is tried on sample text with the real reader, so a Polars upgrade
that adds or removes a readable dtype shows in `test_polars_types.py`, which pins the result.

# @deps
# provides: function:text_dtype_names, function:dtype_with_parameters, constant:PARAMETER_KEYS
# consumed_by: libs/utils/src/utils/recipe_check.py, libs/utils/tests/test_polars_types.py
# doc: .claude/design/recipe_format_spec.md (7.4; check FD02; R9)
# @end_deps
"""
import io
from functools import lru_cache
from typing import Dict, Tuple

import polars as pl

# Field keys that carry the parameters a dtype needs, and the dtypes that use them.
PARAMETER_KEYS: Dict[str, Tuple[str, ...]] = {
    "categories": ("Enum",),
    "precision": ("Decimal",),
    "scale": ("Decimal",),
    "format": ("Date", "Datetime", "Time"),
    "time_unit": ("Datetime",),
    "time_zone": ("Datetime",),
}

_SAMPLES = {"Boolean": "true", "Date": "2024-01-02", "Datetime": "2024-01-02 03:04:05", "Time": "03:04:05", "Decimal": "1.5"}


def _probe_dtype(name: str):
    cls = getattr(pl, name)
    if name == "Enum":
        return pl.Enum(["a"]), "a"
    if name == "Decimal":
        return pl.Decimal(10, 2), _SAMPLES[name]
    sample = _SAMPLES.get(name, "1" if ("Int" in name or "Float" in name) else "a")
    return cls(), sample


@lru_cache(maxsize=1)
def text_dtype_names() -> Tuple[str, ...]:
    """The canonical names of the dtypes the installed Polars can read from text, sorted."""
    found = []
    for name in dir(pl):
        cls = getattr(pl, name)
        if not (isinstance(cls, type) and issubclass(cls, pl.DataType)) or cls is pl.DataType or cls.__name__ != name:
            continue
        try:
            dtype, sample = _probe_dtype(name)
            pl.read_csv(io.BytesIO(f"a\n{sample}\n".encode()), schema_overrides={"a": dtype})
        except Exception:  # a dtype that cannot be built without arguments or cannot be read from text
            continue
        found.append(name)
    return tuple(sorted(found))


def dtype_with_parameters(name: str, field: dict):
    """The Polars dtype for a field: its name and the parameter keys of the field (categories, precision, scale, ...)."""
    cls = getattr(pl, name)
    if name == "Enum":
        return pl.Enum(field["categories"])
    if name == "Decimal":
        return pl.Decimal(field.get("precision"), field.get("scale", 0))
    if name == "Datetime":
        return pl.Datetime(field.get("time_unit", "us"), field.get("time_zone"))
    return cls()
