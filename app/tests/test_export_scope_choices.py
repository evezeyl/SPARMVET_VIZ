"""The Scope choices of the Export panel for the plot tab that is open (pure function, no browser).

`export_scope_choices` is what `_sync_export_scope_choices` puts on the radio when the plot tab or the recipe changes
(EXPORT-FLAKE-1). Edge cases: no groups, groups and no tab open, a tab open, a tab that belongs to no group, a tab prefix
that is not a plot tab.
"""
from app.handlers.export_handlers import export_scope_choices

GROUPS = {"qc": {"plots": {"p1": {}, "p2": {}}}, "amr": {"plots": {"p3": {}}}}


def test_with_groups_and_no_tab_open_group_and_plot_are_dimmed():
    c = export_scope_choices(GROUPS, "")
    assert list(c) == ["global", "group", "plot"]
    assert c["global"]["dimmed"] is False
    assert c["group"] == {"label": "Active group", "title": "Switch to a plot tab to enable scoped export.", "dimmed": True}
    assert c["plot"]["dimmed"] is True and c["plot"]["label"] == "Active plot"


def test_with_a_tab_open_the_labels_name_the_group_and_the_plot():
    c = export_scope_choices(GROUPS, "subtab_p3")
    assert c["group"]["label"] == "Active group (amr)" and c["group"]["dimmed"] is False
    assert c["plot"]["label"] == "Active plot (p3)" and c["plot"]["dimmed"] is False
    assert export_scope_choices(GROUPS, "subtab_p1")["group"]["label"] == "Active group (qc)"


def test_a_tab_that_belongs_to_no_group_offers_no_group_choice():
    c = export_scope_choices(GROUPS, "subtab_unknown")
    assert list(c) == ["global", "plot"]
    assert c["plot"]["label"] == "Active plot (unknown)"


def test_a_recipe_without_groups_offers_global_and_plot_only():
    c = export_scope_choices({}, "subtab_p1")
    assert list(c) == ["global", "plot"]
    assert export_scope_choices({}, "")["plot"]["dimmed"] is True


def test_a_name_that_is_not_a_plot_tab_counts_as_no_tab():
    c = export_scope_choices(GROUPS, "something_else")
    assert c["plot"]["dimmed"] is True and c["group"]["dimmed"] is True
