"""HOME, the audit panel, the sessions and the seeds read the plot ENTRY as the plot content (D-0237, D-0250, D-0253).

A plot entry has no `spec` key: the content (`target_dataset`, `mapping`, `layers`, ...) is written in the entry, next to the
app-side keys (`ui_label`, `ui_title`, `description`, `comment`, `taxonomy`, `plot_engine`, `tier3`). The group tab and the plot
tab read `ui_label`. A reader that still looked for `spec` or `label` would find nothing and draw nothing, so each reader
has a test that fails when it goes back.

# @deps
# consumes: app/handlers/home_theater.py (group_tab_label, plot_tab_label, plot_list_label, _collect_all_group_plot_ids), app/handlers/audit_stack.py (plot_target_dataset), app/modules/session_manager.py (extract_primary_keys)
# @end_deps
"""
from pathlib import Path

import pytest

from app.handlers.audit_stack import plot_target_dataset
from app.handlers.home_theater import _collect_all_group_plot_ids, group_tab_label, plot_list_label, plot_tab_label
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.session_manager import extract_primary_keys
from utils import action_names

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"


def test_a_group_tab_reads_ui_label_then_description_then_the_group_id():
    assert group_tab_label("qc", {"ui_label": "Quality Control", "description": "d"}) == "Quality Control"
    assert group_tab_label("qc", {"description": "the description"}) == "the description"
    assert group_tab_label("qc", {}) == "qc"
    assert group_tab_label("qc", {"label": "old key"}) == "qc", "the old key `label` is not read any more"


def test_a_plot_tab_reads_ui_label_then_the_plot_id_in_title_case():
    assert plot_tab_label("qc_reads_plot", {"ui_label": "QC Reads"}) == "QC Reads"
    assert plot_tab_label("qc_reads_plot", {}) == "Qc Reads Plot"
    assert plot_tab_label("qc_reads_plot", {"label": "old key"}) == "Qc Reads Plot"


def test_the_list_of_plots_in_the_audit_dialogs_reads_ui_label_then_the_plot_id():
    assert plot_list_label("p_one", {"ui_label": "Plot one"}) == "Plot one"
    assert plot_list_label("p_one", {"label": "old key"}) == "p_one"
    assert plot_list_label("p_one", None) == "p_one"


class _Boot:
    discovered_data_analysis_recipes = {"demo": DEMO}


def test_the_plot_slots_of_home_carry_the_entry_with_its_content():
    slots = dict(_collect_all_group_plot_ids(_Boot()))
    assert len(slots) == 17
    for p_id, entry in slots.items():
        assert entry is not None, f"{p_id}: the plot entry must be handed over, not a missing `spec`"
        assert "spec" not in entry and entry.get("ui_label") and entry.get("target_dataset") and entry.get("layers")


def test_the_audit_panel_reads_the_target_dataset_from_the_entry():
    raw = load_data_analysis_recipe(DEMO).config.raw_config
    assert plot_target_dataset(raw, "qc_reads_horizontal_barplot") == "QC_Reads_Anchor"
    assert plot_target_dataset(raw, "no_such_plot") is None
    assert plot_target_dataset({"analysis_groups": {"g": {"plots": {"p": {"ui_label": "P"}}}}}, "p") is None
    assert plot_target_dataset({"analysis_groups": {"g": {"plots": {"p": {"spec": {"target_dataset": "T"}}}}}}, "p") is None, \
        "a plot written the old way (a `spec` key) is not read"


def test_the_join_keys_come_from_the_tier_steps_of_the_joins_and_only_from_join_steps():
    raw = {"joins": {
        "J": {"tier1": {"steps": [{"action": action_names.JOIN, "right_ingredient": "M", "on": ["sample_id"], "how": "left"},
                                   {"action": "polars_unpivot", "on": ["n50", "length"]}]},
              "tier2": {"steps": [{"action": action_names.JOIN, "left_on": "gene", "right_on": ["gene_id"]}]}},
        "K": {"tier1": {"steps": []}},
    }}
    assert extract_primary_keys(raw) == ["gene", "gene_id", "sample_id"], "an unpivot's `on` names columns, not keys"
    assert extract_primary_keys({"joins": {"J": {"steps": [{"action": action_names.JOIN, "on": "x"}]}}}) == [], \
        "a join written the old way (a `steps` container) is not read"
    assert extract_primary_keys({}) == [] and extract_primary_keys({"joins": None}) == []


def test_the_demo_recipe_has_its_join_keys():
    raw = load_data_analysis_recipe(DEMO).config.raw_config
    assert extract_primary_keys(raw) == ["Gene_name", "VF_gene", "sample_id"]

