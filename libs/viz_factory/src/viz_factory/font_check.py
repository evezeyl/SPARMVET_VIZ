"""Which font families of a plot are not installed on this machine (D-0050).

# @deps
# provides: function:missing_fonts, function:font_problems
# consumes: matplotlib.font_manager
# consumed_by: libs/viz_factory/src/viz_factory/viz_factory.py
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

When a family is not installed, matplotlib draws with another font and only writes a log line; the picture changes without a
message to the user. Here the font manager is asked directly: `findfont(..., fallback_to_default=False)` raises when no font
matches. This is the more robust way: a log text depends on the matplotlib version and on its language and is written once
per process (the lookup is cached), so a check that reads it would miss the second plot.
"""
from __future__ import annotations

from typing import Any, Optional, Tuple

from matplotlib import font_manager


def missing_fonts(family: Any) -> Optional[Tuple[Any, str]]:
    """None when the family (a name or a list of names, the first installed one wins) is installed;
    else (what was asked for, the name of the font matplotlib uses instead)."""
    # a list, always: matplotlib reads a lone string as a fontconfig pattern, which cannot parse 'sans-serif'
    properties = font_manager.FontProperties(family=[family] if isinstance(family, str) else list(family))
    try:
        font_manager.findfont(properties, fallback_to_default=False)
        return None
    except ValueError:
        pass
    used = font_manager.get_font(font_manager.findfont(properties)).family_name
    return family, used


def font_problems(theme: Any) -> list:
    """For a plotnine theme: a list of (theme setting, asked-for family, font used instead) for every family not installed."""
    found = []
    themeables = getattr(theme, "themeables", None) or {}
    for name, themeable in themeables.items():
        family = (getattr(themeable, "properties", None) or {}).get("family")
        if not family:
            continue
        result = missing_fonts(family)
        if result is not None:
            found.append((name, result[0], result[1]))
    return found
