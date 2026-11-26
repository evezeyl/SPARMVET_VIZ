"""Every step card of the Pipeline Audit panel says at which table or plot, and tier, the step was written, in a section of its own (the owner, 2026-11-26).

What the panel looked like before: the recipe's own tier-2 steps were listed under "Inherited (Tier 2)" in blue; the audit steps were cards under "My Adjustments - <plot id>" (the heading was
drawn only when a card existed), and the line that said where a card was written was drawn only for a step at a table (`place and not place.startswith("T3:")`): a step at a plot's own tier 3
(the plot "Year Distribution") showed no place at all, and the line was small grey text. Now: the section heading is always shown, below the recipe steps and set apart; every card, pending or
committed, says "Written at <name>: Table, T1" or "Written at <name>: Result data, T3" (the lineage panel's text, `utils.display_names`), a table also how many plots are built from there.

Mutation (seen failing): MUTATION P1 `_place_banner` returns an empty span for a place that starts with "T3:" (the old behaviour).
"""
import re

from app.handlers.audit_stack import _place_banner
from app.modules.audit_places import place_line

RAW = {
    "data_schemas": {"ResFinder": {"ui_label": "ResFinder results", "tier1": {"steps": []}}, "Bare_table": {"tier1": {"steps": []}}},
    "joins": {"MLST_with_metadata": {"ui_label": "MLST with metadata", "tier1": {"steps": []}}},
    "analysis_groups": {"g": {"ui_label": "G", "plots": {"year_distribution": {"ui_label": "Year Distribution", "target_dataset": "MLST_with_metadata"}, "no_label": {"target_dataset": "Bare_table"}}}},
}


def _text(tag) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(tag))).strip()


def test_a_step_at_a_plot_says_the_plot_by_its_label_the_kind_and_the_tier():
    assert _text(_place_banner("T3:year_distribution", {}, RAW)) == "Written at Year Distribution: Result data, T3"


def test_a_step_at_a_table_says_the_table_the_tier_and_how_many_plots():
    text = _text(_place_banner("T1:ResFinder", {"T1:ResFinder": ["a", "b", "c"]}, RAW))
    assert text == "Written at ResFinder results: Table, T1 3 plots are built from there."
    assert _text(_place_banner("T2:MLST_with_metadata", {"T2:MLST_with_metadata": ["p"]}, RAW)) == "Written at MLST with metadata: Table, T2 1 plot is built from there."


def test_a_table_no_plot_reads_says_that_no_figure_changes():
    text = _text(_place_banner("T1:Bare_table", {"T1:Bare_table": []}, RAW))
    assert text.startswith("Written at Bare table: Table, T1 No plot is built from there, so no figure changes.")


def test_the_line_is_the_text_of_the_lineage_panel_and_falls_back_to_the_readable_id():
    assert place_line("T3:no_label", RAW) == "no label: Result data, T3"
    assert place_line("T1:Nope_table", RAW) == "Nope table: Table, T1"
    assert place_line("T3:year_distribution", None) == "year distribution: Result data, T3"
    assert place_line("", RAW) == "" and place_line("garbage", RAW) == "garbage"


def test_two_tables_with_the_same_label_are_told_apart_on_the_card_too():
    raw = {"data_schemas": {"a": {"ui_label": "Same"}, "b": {"ui_label": "Same"}}}
    assert place_line("T1:a", raw) == "Same (a): Table, T1" and place_line("T1:b", raw) == "Same (b): Table, T1"


def test_a_step_with_no_place_is_not_silent():
    assert "no place is recorded" in _text(_place_banner("", {}, RAW))
