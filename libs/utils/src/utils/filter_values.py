"""Coercion of a filter value to the dtype of its column (one implementation, issue #62).

The filter panel stores values as text. The HOME filter engine (`t3_audit_engine._apply_filter_rows`) and the plot
filter of VizFactory both turn that text into a number before comparing it with a numeric column. They used to hold
two copies that truncated a non-integer threshold on an integer column (`>= 90.5` was read as `>= 90`); this module is
the single copy. A value is compared as a number: an integer-valued value on an integer column stays an integer, any
other numeric value becomes a float and Polars compares it exactly.

Consumed by: app/modules/t3_audit_engine.py, libs/viz_factory/src/viz_factory/viz_factory.py.
If deleted: both filters fail to import.
"""
# @deps
# provides: function:coerce_filter_value
# consumes: —
# consumed_by: app/modules/t3_audit_engine.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/utils/tests/test_filter_values.py
# doc: .claude/tasks/home_exploration_build_brief.md#P1
# @end_deps
from typing import Any


def coerce_filter_value(value: Any, dtype: Any) -> Any:
    """Return `value` as the number a numeric column of `dtype` is compared with; anything else comes back unchanged.

    Float or Decimal column: a float. Integer column: an int when the value is integer-valued ("90", "90.0"),
    else a float ("90.5"), never truncated. Text that is not a number is returned as it is, so the comparison
    fails visibly instead of changing the filter.
    """
    s = str(dtype) if dtype is not None else ""
    is_float = "Float" in s or "Decimal" in s
    is_int = "Int" in s
    if not (is_float or is_int):
        return value
    try:
        if is_int and not isinstance(value, float):
            try:
                return int(str(value).strip())  # exact for integers a float cannot hold
            except ValueError:
                pass
        number = float(value)
    except (ValueError, TypeError):
        return value
    if is_int and number.is_integer():
        return int(number)
    return number
