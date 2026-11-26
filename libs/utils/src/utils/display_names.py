"""The names the app shows for the tables and plots of a recipe: one function for every place (the lineage list and map, its text area, the "Chosen" line, the audit cards).

Rule (the owner, 2026-11-26): the name shown is the human label of the recipe (`ui_label`) where it has one, else the id with its underscores replaced by spaces. Two different tables or
plots whose shown names would be equal are told apart by their id in brackets, and only those. The names are the recipe's: nothing is invented. Stdlib and `recipe_tiers` only.

PROVISIONAL words and form (the builder's reading of the owner's remark).

# @deps
# provides: function:readable_name, function:shown_names, function:shown_name, function:kind_tag, function:short_tag, function:tagged_name
# consumes: libs/utils/src/utils/recipe_tiers.py
# consumed_by: libs/utils/src/utils/lineage_data.py, app/modules/lineage_view.py, app/modules/audit_places.py, app/handlers/audit_stack.py
# doc: .claude/rules/ui_implementation_contract.md#2
# @end_deps
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from utils import recipe_tiers

TABLE, PLOT = "table", "plot"


def readable_name(label: Any, ident: str) -> str:
    """The label of the recipe when it has one (trimmed), else the id with underscores written as spaces."""
    text = str(label).strip() if isinstance(label, str) else ""
    return text or ident.replace("_", " ")


def shown_names(raw: Any) -> Dict[Tuple[str, str], str]:
    """`{(kind, id): shown name}` for every table (kind "table": data schemas, additional datasets and joins, not the metadata) and every plot (kind "plot") of the recipe.

    Two different entries whose readable names are equal (case does not matter) both get their id in brackets after the name: "ResFinder (ResFinder_2)"; when the id only repeats the name
    (label equal to the id) the kind is shown instead: "ResFinder (table)", "ResFinder (plot)". If they are still equal (two ids that both repeat the name) the kind is added: "ResFinder (table ResFinder)"."""
    if not isinstance(raw, dict):
        return {}
    entries: List[Tuple[Tuple[str, str], str]] = []
    ids = [i for i in recipe_tiers.schema_bodies(raw) if i != recipe_tiers.METADATA_SCHEMA]
    joins = raw.get("joins")
    if isinstance(joins, dict):
        ids += [i for i in joins if i not in ids]
    for ident in ids:
        body = recipe_tiers.collection_body(raw, ident)
        entries.append(((TABLE, ident), readable_name(body.get("ui_label") if isinstance(body, dict) else None, ident)))
    for ident, entry in recipe_tiers.plot_entries(raw).items():
        entries.append(((PLOT, ident), readable_name(entry.get("ui_label"), ident)))
    shown = dict(entries)

    def clashes(names: Dict[Tuple[str, str], str]) -> set:
        seen: Dict[str, List[Tuple[str, str]]] = {}
        for key, name in names.items():
            seen.setdefault(name.casefold(), []).append(key)
        return {key for keys in seen.values() if len(keys) > 1 for key in keys}

    for key in clashes(shown):
        # a bracket that only repeats the name tells nothing: the kind is shown instead ("A (table)", "A (plot)")
        repeats = readable_name(None, key[1]).casefold() == shown[key].casefold()
        shown[key] = f"{shown[key]} ({key[0] if repeats else key[1]})"
    for key in clashes(shown):
        shown[key] = f"{shown[key].rsplit(' (', 1)[0]} ({key[0]} {key[1]})"
    return shown


def shown_name(names: Dict[Tuple[str, str], str], kind: str, ident: str) -> str:
    """The shown name of one table or plot; an id the recipe does not have gets its readable id (never an error: a stale place still reads)."""
    return names.get((kind, ident)) or readable_name(None, ident)


def kind_tag(is_plot: bool) -> str:
    """"Result data" for a plot, "Table" for a table: the word before the tier tag in a list line."""
    return "Result data" if is_plot else "Table"


def tagged_name(shown: str, is_plot: bool, tier: int) -> str:
    """The text every place uses for a table or a plot: "<shown name>: Table, T1" or "<shown name>: Result data, T3"."""
    return f"{shown}: {kind_tag(is_plot)}, {short_tag(tier)}"


def short_tag(tier: int) -> str:
    """The tier as one short tag: T1, T2, T3."""
    return f"T{tier}"
