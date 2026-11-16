"""audit_nodes.py - the audit list of a plot as the tests write it: filter rows and column drops as audit steps (nodes).

# @deps
# consumes: app/modules/t3_audit_engine.py (audited_frame reads the nodes in their recorded order)
# consumes: libs/viz_factory (home_plot_data)
# consumed_by: app/tests/test_filter_four_way.py, app/tests/test_filter_datetime_four_way.py, app/tests/test_old_session_typed_values.py, app/tests/test_na_choice.py, app/tests/test_export_view_consistency.py
# @end_deps

`audited_frame(lf, nodes)` takes the audit steps of a plot in their recorded order (PLOT-TABLE-ORDER-1). A test that has a
filter row (`column`, `op`, `value`, `dtype`, `na`, `closed`) builds the step from it here: the row is the step's params.
"""


def filter_nodes(rows: list, drops: list = ()) -> list:
    """Filter rows first, then column drops, as audit steps (the order a test that gives both lists means)."""
    nodes = [{"id": f"f{i}", "node_type": "filter_row", "params": dict(row), "reason": "test"} for i, row in enumerate(rows)]
    nodes += [{"id": f"d{i}", "node_type": "drop_column", "params": {"column": column}, "reason": "test"} for i, column in enumerate(drops)]
    return nodes


def home_plot_data(lf, rows: list, spec: dict, drops: list = ()):
    """The data of a plot as HOME and the bundle build it: the audit steps applied to the frame (`audited_frame`), then the real
    VizFactory draws it. The spec carries no `filters` key: the factory's own filter path is for what a recipe's plot spec writes."""
    from app.modules.t3_audit_engine import audited_frame
    from viz_factory.viz_factory import VizFactory
    return VizFactory().render(audited_frame(lf, filter_nodes(rows, drops)), {"plots": {"p": spec}}, "p").data
