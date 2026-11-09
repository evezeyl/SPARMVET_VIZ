"""issue #36 — `breaks_integer: true` must give whole-number ticks even on a narrow
range, e.g. after a T3 filter narrows the data to one or two years.

`MaxNLocator(integer=True)` (the thing `_integer_breaks` used to delegate to
unconditionally) only *prefers* integer ticks: on a span under ~1 unit it falls back
to fractional ones because no "nice" step (1/2/5/10...) fits inside the span. That is
exactly what produced the bug's "2023.6, 2023.7, ... 2024.4" axis.
"""
from viz_factory.scales.core import _integer_breaks


def test_narrow_range_after_a_filter_gives_whole_numbers():
    """The issue's own repro: filtering to year >= 2024 narrows the axis limits to a
    sub-1-unit span. MaxNLocator alone would answer with fractional ticks here."""
    breaks = _integer_breaks((2023.6, 2024.4))
    assert all(float(b).is_integer() for b in breaks)
    assert list(breaks) == [2023, 2024, 2025]


def test_very_narrow_range_single_point():
    breaks = _integer_breaks((2023.9, 2024.3))
    assert all(float(b).is_integer() for b in breaks)


def test_zero_width_range():
    assert list(_integer_breaks((2024.0, 2024.0))) == [2024]


def test_normal_multi_year_range_unaffected():
    assert list(_integer_breaks((2023.0, 2025.0))) == [2023, 2024, 2025]


def test_wide_range_still_sparse_not_one_tick_per_year():
    """For a genuinely large span, MaxNLocator's own step selection already lands on
    integers — don't force a tick per year (125 ticks for 1900-2024 would be useless)."""
    breaks = list(_integer_breaks((1900.0, 2024.0)))
    assert all(float(b).is_integer() for b in breaks)
    assert len(breaks) < 20
