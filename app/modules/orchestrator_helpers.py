# @deps
# provides: safe_input, blueprint_is_open, DEFAULT_HOME_STATE
# consumes: app/modules/frame_widths.py (HOME, BLUEPRINT: the nav values)
# consumed_by: app.src.server, app/modules/wrangle_studio.py (blueprint_is_open), app/handlers/blueprint_handlers.py (blueprint_is_open)
# doc: ADR-045 (Two-Category Law §5 — shared utility functions)
# @end_deps
"""Pure helper functions and constants shared across server.py and all handler modules.

These are plain utilities that carry no Shiny state and no reactive logic; the only import is
`frame_widths` (the nav values), inside `blueprint_is_open`.
They live here rather than in server.py to keep that file within the 250-line cap.
"""


def safe_input(input_obj, key, default):
    """Return input_obj.<key>() or default when the input is missing or raises."""
    try:
        val = getattr(input_obj, key)()
        return val if val is not None else default
    except Exception:
        return default


def blueprint_is_open(input_obj, read=safe_input) -> bool:
    """True only while BLUEPRINT is the open user space.

    Reads the nav input, so a reactive function that calls it is invalidated when the user space
    changes and computes again when BLUEPRINT is opened. `read` is the handler's own safe_input. A BLUEPRINT output that reads HOME state
    (the active recipe, its tables) calls this first: hidden, it must not compute on another recipe's
    table (its stale error would make the browser drop HOME's whole update; ADR-094, ADR-104).
    """
    from app.modules import frame_widths
    return read(input_obj, "sidebar_nav", frame_widths.HOME) == frame_widths.BLUEPRINT


# Default home module state — see ui_implementation_contract.md §13.
# server.py initialises: home_state = reactive.Value(dict(DEFAULT_HOME_STATE))
DEFAULT_HOME_STATE: dict = {
    # Navigation
    "active_group_tab": None,
    "active_plot_subtab": None,
    # Audit mode: the lineage node of the item shown ("T3:<plot>", "T1:<table>", "T2:<table>"), None in Exploration (slice 3b; the right panel follows it)
    "audit_shown_place": None,
    # Accordion collapse states
    "accordion_plots_expanded": True,
    "accordion_data_expanded": True,
    # Row filters (left sidebar)
    "_pending_filters": [],
    "applied_filters": [],
    # audit steps — Phase 22-J / ADR-049: per-plot stacks.
    # Each plot subtab id maps to a list of committed AuditSteps.
    # Propagated nodes appear in multiple stacks but share the same `id`
    # for linked deletion.
    "audit_pipeline": [],                          # the audit steps that were added, ONE flat list in the order added; each carries its `place`
    "audit_saves_count": 0,                   # bumps at each save of the session (an Add, a removal): the session panel counts the saves
    "primary_keys": [],                    # union of all join keys (§12g.2)
    "orphaned_t3_nodes": [],               # legacy/orphan nodes from ghost restore
    # T3 plot aesthetic overrides {plot_subtab_id: {fill, colour, alpha, shape}}
    "t3_plot_overrides": {},
    # Assembly provenance
    "data_analysis_recipe_sha256": None,
    "assembly_timestamp": None,
    # Session ghost provenance
    "t3_ghost_file": None,
    "t3_ghost_saved_at": None,
}
