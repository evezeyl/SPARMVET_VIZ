"""audit_nodes.py - the audit steps of a plot as the tests write them: filter rows and column drops as audit steps (nodes).

# @deps
# consumes: libs/blueprint_arch/src/blueprint_arch/t3_translator.py (translate_t3_node: the one translation of a node into the registered action), libs/transformer/src/transformer/registry.py (get_action_function: the registered actions the engine runs)
# consumes: libs/viz_factory (home_plot_data)
# consumed_by: app/tests/test_filter_four_way.py, app/tests/test_filter_datetime_four_way.py, app/tests/test_old_session_typed_values.py, app/tests/test_na_choice.py, app/tests/test_export_view_consistency.py
# @end_deps

HOME, the export and the filter dialog read the audited table from the audit copy, in which the engine runs the audit steps (`utils.audit_copy`, run by
`app/modules/audit_view.py`). A test that has no recipe and no orchestrator, only a frame and some nodes, applies the steps the way the engine does: each node is
translated into its registered action (`translate_t3_node`, the translation the audit copy uses) and the action is run on the frame, in the order of the list
(`get_action_function`, the registry the data assembler reads). The test says what a step does to a table, with the engine's own action: no second implementation of a filter.

A test that has a filter row (`column`, `op`, `value`, `dtype`, `na`, `closed`) builds the step from it here: the row is the step's params.
"""
from blueprint_arch.t3_translator import translate_t3_node
from transformer.registry import get_action_function


def filter_nodes(rows: list, drops: list = ()) -> list:
    """Filter rows first, then column drops, as audit steps (the order a test that gives both lists means)."""
    nodes = [{"id": f"f{i}", "node_type": "filter_row", "params": dict(row), "reason": "test"} for i, row in enumerate(rows)]
    nodes += [{"id": f"d{i}", "node_type": "drop_column", "params": {"column": column}, "reason": "test"} for i, column in enumerate(drops)]
    return nodes


def audited_lf(lf, nodes: list):
    """The table after the audit steps `nodes`, in the order of the list: each node translated into its registered action and run by the engine's action.
    A step on a column the table does not have raises (Polars `ColumnNotFoundError` when the plan is read or collected), never skips; a node with no
    translation raises `UntranslatableNode`."""
    for node in nodes:
        if not node.get("active", True):
            continue
        for step in translate_t3_node(node):
            lf = get_action_function(step["action"])(lf, dict(step))
    return lf


def home_plot_data(lf, rows: list, spec: dict, drops: list = ()):
    """The data of a plot as HOME and the bundle build it: the audit steps applied to the frame (`audited_lf`), then the real
    VizFactory draws it. The spec carries no `filters` key: the factory's own filter path is for what a recipe's plot spec writes."""
    from viz_factory.viz_factory import VizFactory
    return VizFactory().render(audited_lf(lf, filter_nodes(rows, drops)), {"plots": {"p": spec}}, "p").data


def filter_rows_of(nodes: list) -> list:
    """The filter rows (`column`, `op`, `value`, `dtype`, `na`, `closed`) of the active filter steps of a list: what the exploration filter `_apply_filter_rows` reads, so that a
    test can ask the same rows of the exploration path and of the audit path (`audited_lf`). A step written before the choice `na` existed is carried as "remove"."""
    from utils.na_choice import na_of
    rows = []
    for node in nodes:
        if not node.get("active", True) or node.get("node_type") not in ("filter_row", "exclusion_row"):
            continue
        params = node.get("params", {})
        if "column" not in params:
            continue
        row = {"column": params.get("column"), "op": params.get("op", "eq"), "value": params.get("value"), "dtype": params.get("dtype", "Utf8"), "na": na_of(params)}
        if row["op"] == "between":
            row["closed"] = params.get("closed", "both")
        rows.append(row)
    return rows


def audit_state(plot: str, nodes: list) -> dict:
    """The part of HOME's state that holds committed audit steps written at the tier 3 of `plot` (a plot id, or its sub-tab id): the one flat list `audit_pipeline`, every step with its place."""
    plot_id = plot.removeprefix("subtab_")
    return {"audit_pipeline": [{**n, "place": f"T3:{plot_id}", "created_at": n.get("created_at", f"2026-11-24T10:00:0{i}")}
                                                      for i, n in enumerate(nodes)]}
