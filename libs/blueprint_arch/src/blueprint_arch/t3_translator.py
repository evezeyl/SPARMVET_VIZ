# engine: python-polars (writes the Polars filter and drop actions of an audit step)
"""
Audit node -> recipe-action translator (ADR-097 decision 4, REPRO-TRANSLATOR-1, issue #47; the only translation, shared by the audit copy and the export).

Translates ONE committed audit node of HOME (a row filter, an exclusion by key or a column drop) into the registered wrangling action (or actions) that stand for it. The audit
copy of the recipe (`utils.audit_copy`, built by `app/modules/audit_places.py`) writes the result as the audit step of the node, at the place of the node (the tier 1 or tier 2
of a table, the tier 3 of a plot); the reproducibility part of the export writes the same actions as plain steps at the same places (`audit_places.bake_place_steps`). The three
tiers are one mechanism: the former fork of a join per plot (`build_mode2_recipe`, which wrote the steps of a plot into a private copy of its join) is gone, and with it the
"skipped" plots: a node that cannot be translated raises `UntranslatableNode` where the step is written, so no step is ever left out.

Pure (stdlib and the shared `utils.filter_values`, which reads a value against a dtype name; it builds no table) - Two-Category Law, no Shiny.

Engine-coverage note (closed in #52): all eight filter ops (`eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in`, `not_in`) and `between` are translatable; the approximation of a strict `gt`
as an inclusive `ge` is not made (it would silently include one boundary value).
"""
from __future__ import annotations

from utils import action_names
from utils.filter_values import FilterValueError, read_filter_value
from utils.na_choice import na_of

# @deps
# provides: function:translate_t3_node, class:UntranslatableNode
# consumes: libs/utils/src/utils/na_choice.py (stdlib only), libs/utils/src/utils/filter_values.py
# consumed_by: app/modules/audit_places.py (audit_copy_for, bake_place_steps), libs/blueprint_arch/tests/test_t3_translator.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-097, .claude/design/reproducible_export_design.md#4D
# @end_deps


class UntranslatableNode(Exception):
    """An audit node whose type/op has no registered-action equivalent today.

    Callers must treat this as "the step cannot be written, surface why" - never as a cue to
    approximate and never as a step to leave out. Carries the plain-text reason in its message.
    """


# Ops that `modif_filter` represents EXACTLY (libs/transformer/src/transformer/actions/modified.py): the audit dialog and the
# recipe filter share one vocabulary (`between` included: bounds as [low, high], the ends in `closed`).
FILTER, DROP = action_names.FILTER, action_names.DROP
_TRANSLATABLE_OPS = {"eq", "ne", "gt", "ge", "lt", "le", "in", "not_in", "between"}


def translate_t3_node(node: dict) -> list[dict]:
    """One T3 audit node -> one or more canonical wrangling actions (`action:` key
    format, rules_data_analysis_recipe_structure.md §7).

    Raises UntranslatableNode when the node's type/op has no registered-action
    equivalent today. An `aesthetic_override` node is cosmetic, never translated (ADR-097 decision 4) and is
    not an audit step on data: passing one here raises, it is not silently skipped.
    """
    node_type = node.get("node_type")
    params = node.get("params", {}) or {}

    if node_type in ("filter_row", "exclusion_row"):
        column = params.get("column")
        op = params.get("op", "eq")
        value = params.get("value")
        if not column:
            raise UntranslatableNode(f"{node_type} node has no column: {node!r}")
        # Same auto-promotion viz_factory.render() applies at render time (eq/in -> in,
        # ne/not_in -> not_in, when the stored value is a list) — a committed node can
        # carry op="eq" with a list value and only be promoted at render time, so this
        # translator must apply the identical rule or it would mistranslate it as a
        # single-value eq filter on a list, which polars would not evaluate as intended.
        if isinstance(value, list):
            if op in ("eq", "in"):
                op = "in"
            elif op in ("ne", "not_in"):
                op = "not_in"
        if op not in _TRANSLATABLE_OPS:
            raise UntranslatableNode(
                f"op '{op}' has no registered wrangling action — not one of "
                f"{sorted(_TRANSLATABLE_OPS)} — node: {node!r}"
            )
        if op in ("in", "not_in"):
            value = value if isinstance(value, list) else [value]
        if op == "between" and not (isinstance(value, (list, tuple)) and len(value) == 2):
            raise UntranslatableNode(f"op 'between' needs the two bounds [low, high] - node: {node!r}")
        # ADR-104 point 7: the value has the type of the column. A step an older panel stored with the value as text is typed
        # here from the dtype it carries; a value that cannot be read is reported, never guessed. No dtype: left as written.
        dtype = params.get("dtype")
        if dtype:
            try:
                value = ([read_filter_value(v, dtype) for v in value] if isinstance(value, list)
                         else read_filter_value(value, dtype))
            except FilterValueError as exc:
                raise UntranslatableNode(f"column {column!r}: {exc} - node: {node!r}") from exc
        # `na` is the choice the user made in the HOME dialog (keep or remove the rows with no value). A step
        # written before the choice existed has none and always removed them, so it is exported as "remove".
        try:
            na = na_of(params)
        except ValueError as exc:
            raise UntranslatableNode(f"{exc} (na of the node) - node: {node!r}") from exc
        step = {"action": FILTER, "column": column, "op": op, "value": list(value) if op == "between" else value, "na": na}
        if op == "between":
            # the ends the user chose (both or none in the dialog); never lost on the way to the recipe
            step = {**step, "closed": params.get("closed", "both")}
        return [step]

    if node_type == "drop_column":
        column = params.get("column")
        if not column:
            raise UntranslatableNode(f"drop_column node has no column: {node!r}")
        return [{"action": DROP, "columns": [column]}]

    raise UntranslatableNode(f"node_type {node_type!r} is not translatable: {node!r}")
