# engine: python-plotnine (asks matplotlib which font families are installed)
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


def _is_family(value: Any) -> bool:
    """A text, or a non-empty list of texts: the only shapes this check can judge; anything else is left to plotnine."""
    if isinstance(value, str):
        return value != ""
    return isinstance(value, (list, tuple)) and len(value) > 0 and all(isinstance(v, str) and v != "" for v in value)


def family_text(family: Any) -> str:
    """The family as a person reads it: 'Foo', or 'Foo, Bar' for a list."""
    return family if isinstance(family, str) else ", ".join(family)


def font_problems(theme: Any) -> list:
    """For a plotnine theme: one (theme settings, asked-for family, font used instead) per missing family, never raises.

    Plotnine copies a family set on the general setting 'text' into many settings; they are grouped here so that the
    user is told once per missing font. A value that is not a text or a list of texts is skipped (plotnine refuses it).
    """
    groups: dict = {}
    themeables = getattr(theme, "themeables", None) or {}
    for name, themeable in themeables.items():
        properties = getattr(themeable, "properties", None)
        family = properties.get("family") if isinstance(properties, dict) else None
        if not _is_family(family):
            continue
        result = missing_fonts(family)
        if result is not None:
            key = family_text(family)
            groups.setdefault(key, (result[0], result[1], []))[2].append(name)
    return [(names, asked, used) for asked, used, names in groups.values()]


def settings_text(names: list) -> str:
    """The settings as one short list. When the general setting 'text' is among them it is the origin (plotnine copies it
    to the others): it is named, with the number of settings it reached. Else up to three, then 'and N more'."""
    if "text" in names and len(names) > 1:
        return f"the general setting 'text' (reaches {len(names) - 1} more settings)"
    if len(names) <= 3:
        return ", ".join(f"'{n}'" for n in names)
    return ", ".join(f"'{n}'" for n in names[:3]) + f" and {len(names) - 3} more"
