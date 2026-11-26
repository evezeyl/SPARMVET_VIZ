"""Every step card of the Pipeline Audit panel says where the step was written (the owner did not see it for a step on the plot "Year Distribution", 2026-11-26).

The design expects (ui_implementation_contract.md 12g.6): a step at a table reads "Written at Table X (tier 1): N plots are built from there"; a step at a plot's own tier 3 reads
"Written at Plot P (tier 3)". Before this change the line was drawn only for a table (`place and not place.startswith("T3:")`), so a step on a plot showed no place at all.
The name is the recipe's `ui_label` where there is one. Words PROVISIONAL.

Mutation (seen failing): MUTATION P1 `_place_banner` returns an empty span for a place that starts with "T3:" (the old behaviour).
"""
from app.handlers.audit_stack import _place_banner
from app.modules.audit_places import place_words_labelled

RAW = {
    "data_schemas": {"ResFinder": {"ui_label": "ResFinder results", "tier1": {"steps": []}}, "Bare": {"tier1": {"steps": []}}},
    "joins": {"MLST_with_metadata": {"ui_label": "MLST with metadata", "tier1": {"steps": []}}},
    "analysis_groups": {"g": {"ui_label": "G", "plots": {"year_distribution": {"ui_label": "Year Distribution", "target_dataset": "MLST_with_metadata"}, "no_label": {"target_dataset": "Bare"}}}},
}


def _text(tag) -> str:
    import re
    return re.sub(r"<[^>]+>", "", str(tag)).strip()


def test_a_step_at_a_plot_says_the_plot_by_its_label():
    text = _text(_place_banner("T3:year_distribution", {}, RAW))
    assert text == "Written at Plot Year Distribution (tier 3)."


def test_a_step_at_a_table_says_the_table_the_tier_and_how_many_plots():
    text = _text(_place_banner("T1:ResFinder", {"T1:ResFinder": ["a", "b", "c"]}, RAW))
    assert text == "Written at Table ResFinder results (tier 1): 3 plots are built from there."
    assert _text(_place_banner("T2:MLST_with_metadata", {"T2:MLST_with_metadata": ["p"]}, RAW)).endswith("1 plot is built from there.")


def test_a_table_no_plot_reads_says_that_no_figure_changes():
    text = _text(_place_banner("T1:Bare", {"T1:Bare": []}, RAW))
    assert text.startswith("Written at Table Bare (tier 1): no plot is built from there, so no figure changes.")


def test_a_place_with_no_label_or_an_unreadable_recipe_falls_back_to_the_ids():
    assert place_words_labelled("T3:no_label", RAW) == "Plot no_label (tier 3)"
    assert place_words_labelled("T3:year_distribution", None) == "Plot year_distribution (tier 3)"
    assert place_words_labelled("T1:Nope", RAW) == "Table Nope (tier 1)"
    assert place_words_labelled("", RAW) == ""


def test_a_step_with_no_place_is_not_silent():
    assert "no place is recorded" in _text(_place_banner("", {}, RAW))
