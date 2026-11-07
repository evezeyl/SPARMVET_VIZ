# @deps
# provides: safe_input, DEFAULT_HOME_STATE
# consumes: —
# consumed_by: app.src.server
# doc: ADR-045 (Two-Category Law §5 — shared utility functions)
# @end_deps
"""Pure helper functions and constants shared across server.py and all handler modules.

These are dependency-free utilities that carry no Shiny state and no reactive logic.
They live here rather than in server.py to keep that file within the 250-line cap.
"""


def safe_input(input_obj, key, default):
    """Return input_obj.<key>() or default when the input is missing or raises."""
    try:
        val = getattr(input_obj, key)()
        return val if val is not None else default
    except Exception:
        return default


# Default home module state — see ui_implementation_contract.md §13.
# server.py initialises: home_state = reactive.Value(dict(DEFAULT_HOME_STATE))
DEFAULT_HOME_STATE: dict = {
    # Navigation
    "active_group_tab": None,
    "active_plot_subtab": None,
    "tier_toggle": "T1",
    # Accordion collapse states
    "accordion_plots_expanded": True,
    "accordion_data_expanded": True,
    # Row filters (left sidebar)
    "_pending_filters": [],
    "applied_filters": [],
    # T3 recipe — Phase 22-J / ADR-049: per-plot stacks.
    # Each plot subtab id maps to a list of committed RecipeNodes.
    # Propagated nodes appear in multiple stacks but share the same `id`
    # for linked deletion.
    "t3_recipe_by_plot": {},               # {plot_subtab_id: [RecipeNode]}
    "_pending_t3_nodes": [],               # pending nodes (carry plot_scopes_intent)
    "t3_apply_count": 0,                   # bumps on commit — triggers filter clear
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
