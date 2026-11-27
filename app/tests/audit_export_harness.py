"""audit_export_harness.py - what HOME hands the export when audit steps are committed, for the tests that run the real download generator headless.

# @deps
# consumes: app/modules/audit_view.py (PlaceAudit)
# consumed_by: app/tests/test_tier3_reader.py, app/tests/test_export_audited_tables.py
# @end_deps

`audit_kwargs(world, nodes, in_audit=True)` gives the keyword arguments of `define_export_server` that HOME gives it (`home_state` with the committed nodes, `audited_plot_table`,
`audit_run`, `in_audit`), made from the same `PlaceAudit` HOME uses. The harness's bootloader needs the flag `t3_sandbox_enabled` (`flags=("t3_sandbox_enabled",)`).
"""
from types import SimpleNamespace

from app.modules.audit_view import PlaceAudit

FLAGS = ("t3_sandbox_enabled",)


def audit_kwargs(world, nodes, in_audit=True, recipe_id="tiny"):
    """The kwargs of the audit for `define_export_server`: the committed `nodes` (each with its `place`), the audit copy made from them, the mode."""
    audit = PlaceAudit(world.orch, world.root / "user" / "anchors", world.root / "user" / "audit_anchors")   # the folder the harness bootloader gives the export: <root>/user/anchors
    state = {"audit_pipeline": list(nodes)}
    return dict(
        home_state=SimpleNamespace(get=lambda: state),
        audited_plot_table=lambda plot_id, told: audit.plot_lazy(recipe_id, plot_id, nodes, None, told),
        audit_run=lambda told: audit.run_of(recipe_id, nodes),
        in_audit=lambda: in_audit,
    )
