"""Turn the `info:` mapping of a data analysis recipe into lines to display.

Serves the "Info" panel of the HOME left sidebar. The data analysis recipe author writes any YAML under `info:`;
nothing is required and no field is special here, so adding `contact:` or a nested `study:` block
needs no code change. Pure Python (Two-Category Law, ADR-045): no Shiny import.

Consumed by: app/handlers/home_theater.py (panel type data_analysis_recipe_info).
If deleted: the Info panel has nothing to show.
"""
from __future__ import annotations

from typing import Any

# One line to show: (depth, label, value). value is None for a heading line that has nested lines under it.
InfoLine = tuple[int, str, "str | None"]


def info_lines(info: Any, depth: int = 0) -> list[InfoLine]:
    """Flatten the info mapping, nested mappings and lists keep their indentation as depth."""
    lines: list[InfoLine] = []
    if isinstance(info, dict):
        for key, value in info.items():
            if isinstance(value, (dict, list)) and value:
                lines.append((depth, str(key), None))
                lines.extend(info_lines(value, depth + 1))
            else:
                lines.append((depth, str(key), _scalar(value)))
    elif isinstance(info, list):
        for item in info:
            if isinstance(item, (dict, list)) and item:
                lines.extend(info_lines(item, depth))
            else:
                lines.append((depth, "-", _scalar(item)))
    elif info not in (None, ""):
        lines.append((depth, "-", _scalar(info)))
    return lines


def _scalar(value: Any) -> str:
    if value is None or value == [] or value == {}:
        return ""
    return str(value)
