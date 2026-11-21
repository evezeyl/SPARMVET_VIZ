# engine: python-polars (plain words for a join that Polars refuses)
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


def _polars_refuses(check: JoinCheck) -> bool:
    """Ask POLARS: does this join, run alone on the key columns only with the same how, validate and nulls_equal, fail its validation?

    Polars' rule for missing key values is not simple (it differs between how and validate), so it is never rebuilt here.
    """
    try:
        check.left.select(check.left_keys).join(check.right.select(check.right_keys), left_on=check.left_keys, right_on=check.right_keys,
                                                how=check.how, validate=check.validate, nulls_equal=check.nulls_equal).collect()
        return False
    except pl.exceptions.ComputeError as exc:
        return "did not fulfill" in str(exc)
    except Exception:  # noqa: BLE001 - another failure is not a refused validation of this join
        return False


def _explain(check: JoinCheck, wanted: str) -> tuple:
    """(message, tip) for a join that Polars refuses: the repeated key value is counted from the keys when one can be shown, no reason is guessed."""
    sides = []
    if wanted in ("1:1", "1:m"):
        sides.append(("first table (the table of the step)", check.left, check.left_keys))
    if wanted in ("1:1", "m:1"):
        sides.append((f"second table {check.right_id!r}", check.right, check.right_keys))
    head = f"{check.location}: polars_join with the second table {check.right_id!r}: validate '{wanted}'"
    tip = ("Check the key columns of the tables for repeated values, or write the validate that matches the data "
           "('m:m' asks nothing; '1:m' asks the first table to be unique; 'm:1' asks the second table to be unique)")
    for with_nulls in dict.fromkeys((check.nulls_equal, True)):  # the second pass only shows a repeated missing value, as a fact
        for name, frame, keys in sides:
            try:
                repeated = _repeated(frame, keys, with_nulls)
            except Exception:  # noqa: BLE001 - a side that cannot be read here shows no example
                continue
            if repeated.height:
                example = repeated.row(0, named=True)
                value = ", ".join(f"{k}={example[k]!r}" for k in keys)
                return (f"{head} asks that the key {keys} appears at most once in the {name}, but {repeated.height} key value(s) repeat there "
                        f"(for example {value} appears {example['len']} times)",
                        f"Remove or merge the repeated rows of the {name} before the join, or write the validate that matches the data "
                        "('m:m' asks nothing; '1:m' asks the first table to be unique; 'm:1' asks the second table to be unique)")
    return (f"{head} was refused by Polars for the key {check.left_keys}; no repeated key value could be shown in the tables as they are before the join", tip)


def explain_validation_error(exc: BaseException, checks: Optional[List[JoinCheck]]) -> Optional[TransformationError]:
    """The plain error for a Polars validation error, or None when the error is something else or no listed join explains it.

    Every listed join is tried: each one whose keys really repeat is named (several are all named). The generic text is the
    last resort, only when none of them can be shown to repeat.
    """
    if not checks:
        return None
    unsupported = _UNSUPPORTED.search(str(exc))
    if unsupported:
        wanted, how = unsupported.group(1), unsupported.group(2).lower()
        matching = [c for c in checks if c.validate == wanted and c.how == how] or checks[:1]
        parts = [f"{c.location}: polars_join with the second table {c.right_id!r}: validate '{wanted}' cannot be used with how '{how}'; "
                 f"Polars cannot check the keys of a {how} join with this validate" for c in matching]
        return TransformationError("; and ".join(parts),
                                   tip="Remove validate (or write 'm:m') from this step, or join with another how (for example inner or left)")
    found = _REFUSED.search(str(exc))
    if not found:
        return None
    wanted = found.group(1)
    # Polars reports one refusal; every listed join is asked, each with its own validate, and each one Polars refuses is named (the recipe's own order)
    candidates = list(checks)
    refused = [c for c in candidates if _polars_refuses(c)]
    if refused:
        explained = [_explain(c, c.validate) for c in refused]
        return TransformationError("; and ".join(m for m, _ in explained), tip=explained[0][1])
    if not candidates:
        return None
    named = "; ".join(f"{c.location} (second table {c.right_id!r}, key {c.left_keys})" for c in candidates)
    return TransformationError(
        f"polars_join: Polars refused validate '{wanted}' in one of these joins: {named}",
        tip="Check the key columns of the tables for repeated values, or write validate 'm:m' (it asks nothing)")
