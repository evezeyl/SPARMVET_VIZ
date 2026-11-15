"""Plain words for a join whose `validate` Polars refuses (D35b, PROVISIONAL).

Polars checks `validate` when the plan runs and answers "join keys did not fulfill 1:1 validation". POLARS decides whether the
join fails; this module only explains afterwards, by looking at the key columns of the joins the assembler listed
(`JoinCheck`, one per join step that writes `validate`). It runs at the place where the engine runs the plan
(`transformer.anchor.write_anchor`), never before.

Consumed by: transformer.anchor, transformer.data_assembler. If deleted: the raw Polars message reaches the user.

# @deps
# provides: class:JoinCheck, function:explain_validation_error
# consumed_by: libs/transformer/src/transformer/anchor.py, libs/transformer/src/transformer/data_assembler.py
# @end_deps
"""
import re
from dataclasses import dataclass
from typing import List, Optional

import polars as pl

from utils.errors import TransformationError

_UNSUPPORTED = re.compile(r"(1:1|1:m|m:1) validation on a (\w+) join is not supported")
_REFUSED = re.compile(r"did not fulfill (1:1|1:m|m:1|m:m) validation")


@dataclass
class JoinCheck:
    """One join step that writes `validate`: where it is and the two tables as they were before the join (lazy)."""
    location: str
    right_id: str
    left: pl.LazyFrame
    right: pl.LazyFrame
    validate: str
    left_keys: List[str]
    right_keys: List[str]
    nulls_equal: bool = False
    how: str = "left"


def _repeated(frame: pl.LazyFrame, keys: List[str], nulls_equal: bool) -> pl.DataFrame:
    keyed = frame.select(keys)
    if not nulls_equal:
        keyed = keyed.drop_nulls()  # a null key is a repeat only with nulls_equal, as in Polars
    return keyed.group_by(keys).len().filter(pl.col("len") > 1).sort("len", descending=True).collect()


def explain_validation_error(exc: BaseException, checks: Optional[List[JoinCheck]]) -> Optional[TransformationError]:
    """The plain error for a Polars validation error, or None when the error is something else or no listed join explains it."""
    if not checks:
        return None
    unsupported = _UNSUPPORTED.search(str(exc))
    if unsupported:
        wanted, how = unsupported.group(1), unsupported.group(2).lower()
        check = next((c for c in checks if c.validate == wanted and c.how == how), checks[0])
        return TransformationError(
            f"{check.location}: polars_join with the second table {check.right_id!r}: validate '{wanted}' cannot be used with how '{how}'; Polars cannot check the keys of a {how} join with this validate",
            tip=f"Remove validate (or write 'm:m') from this step, or join with another how (for example inner or left)")
    found = _REFUSED.search(str(exc))
    if not found:
        return None
    wanted = found.group(1)
    for check in checks:
        if check.validate != wanted:
            continue
        sides = []
        if wanted in ("1:1", "1:m"):
            sides.append((f"first table (the table of the step)", check.left, check.left_keys))
        if wanted in ("1:1", "m:1"):
            sides.append((f"second table {check.right_id!r}", check.right, check.right_keys))
        # a missing key value counts as a repeat only with nulls_equal in most joins, but Polars also counts it in a full join: look without, then with
        for with_nulls in (check.nulls_equal, True):
            for name, frame, keys in sides:
                try:
                    repeated = _repeated(frame, keys, with_nulls)
                except Exception:  # noqa: BLE001 - a side that cannot be read here is not the one to name
                    continue
                if repeated.height:
                    example = repeated.row(0, named=True)
                    value = ", ".join(f"{k}={example[k]!r}" for k in keys)
                    nulls = "" if with_nulls == check.nulls_equal else " (a missing key value counts as a value in this join)"
                    return TransformationError(
                        f"{check.location}: polars_join with the second table {check.right_id!r}: validate '{wanted}' asks that the key {keys} appears at most once in the {name}, "
                        f"but {repeated.height} key value(s) repeat there (for example {value} appears {example['len']} times){nulls}",
                        tip=f"Remove or merge the repeated rows of the {name} before the join, or write the validate that matches the data "
                            "('m:m' asks nothing; '1:m' asks the first table to be unique; 'm:1' asks the second table to be unique)")
        return TransformationError(
            f"{check.location}: polars_join with the second table {check.right_id!r}: Polars refused validate '{wanted}' for the key {check.left_keys}, "
            "and the repeated key values could not be found in the tables as they are before the join",
            tip="Check the key columns of both tables for repeated or missing values, or write validate 'm:m' (it asks nothing)")
    return None
