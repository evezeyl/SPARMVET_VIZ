"""Blueprint's plot-defaults form writes only keys the checker accepts and keeps what the user did not touch (D-0246, D-0258).

Found 2026-11-18: the form wrote the four removed keys, dropped the seed and the layers of the block when it saved,
and wrote `theme_light` when the user chose no theme.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_plot_defaults_form.py -q
"""
import copy
import inspect
import re
from pathlib import Path

import pytest

from app.modules.plot_defaults_form import FORM_KEYS, NO_THEME, form_values, merged_plot_defaults, theme_choices
from utils.config_loader import ConfigManager
from utils.recipe_check import check_recipe, plot_defaults_keys

ROOT = Path(__file__).resolve().parents[2]
RECIPE = ROOT / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"
REMOVED = ["default_font_family", "facet_panel_spacing", "legend_position", "optimisation"]
BLOCK = {
    "palette": "sparmvet_brand",
    "theme": "theme_minimal",
    "random_state": 7,
    "layers": [{"name": "theme_custom", "params": {"legend_position": "bottom"}}],
}


def test_the_form_fields_are_accepted_keys_and_none_is_a_removed_one():
    allowed, removed = plot_defaults_keys()
    assert set(FORM_KEYS) <= set(allowed)
    assert not set(FORM_KEYS) & set(removed)
    assert sorted(removed) == sorted(REMOVED)


def test_the_handler_names_no_removed_key():
    from app.handlers import blueprint_handlers
    source = inspect.getsource(blueprint_handlers)
    start = source.index("bp_plot_defaults_form_ui")
    region = source[start - 800:start + 4500]
    for key in REMOVED:
        assert not re.search(rf"\b{key}\b", region), f"the form still names {key}"
    assert "bp_pd_font" not in region and "bp_pd_spacing" not in region and "bp_pd_legend" not in region


def test_a_save_with_nothing_touched_gives_the_same_block():
    values = form_values(BLOCK)
    assert merged_plot_defaults(BLOCK, values["palette"], values["theme"]) == BLOCK


def test_the_seed_the_layers_and_an_unshown_key_survive_a_save():
    saved = merged_plot_defaults(BLOCK, "viridis", "theme_bw")
    assert saved["random_state"] == 7
    assert saved["layers"] == BLOCK["layers"]


def test_changing_one_field_changes_only_that_key():
    changed = merged_plot_defaults(BLOCK, "viridis", BLOCK["theme"])
    assert changed == {**BLOCK, "palette": "viridis"}
    changed = merged_plot_defaults(BLOCK, BLOCK["palette"], "theme_bw")
    assert changed == {**BLOCK, "theme": "theme_bw"}


def test_no_theme_chosen_writes_no_theme():
    assert "theme" not in merged_plot_defaults({"palette": "viridis"}, "viridis", NO_THEME)
    assert "theme" not in merged_plot_defaults({}, "", NO_THEME)
    assert merged_plot_defaults({}, "", NO_THEME) == {}


def test_choosing_no_theme_removes_a_theme_the_block_had():
    assert "theme" not in merged_plot_defaults(BLOCK, BLOCK["palette"], NO_THEME)


def test_a_block_with_no_theme_shows_no_theme_and_a_save_does_not_add_one():
    block = {"random_state": 3}
    assert form_values(block)["theme"] == NO_THEME
    assert merged_plot_defaults(block, "", form_values(block)["theme"]) == block


def test_a_theme_the_form_does_not_know_is_offered_and_kept():
    block = {"theme": "theme_seaborn"}
    assert "theme_seaborn" in theme_choices(block)
    assert merged_plot_defaults(block, "", form_values(block)["theme"]) == block


def test_the_input_block_is_not_changed():
    before = copy.deepcopy(BLOCK)
    merged_plot_defaults(BLOCK, "viridis", "theme_bw")
    assert BLOCK == before


def test_a_removed_key_already_in_the_block_is_not_hidden_by_the_form():
    # the form does not clean what it does not show: the checker names the key, the user decides (D-0050)
    block = {"legend_position": "top"}
    assert merged_plot_defaults(block, "", NO_THEME) == block


@pytest.mark.parametrize("palette,theme", [("viridis", "theme_bw"), ("", NO_THEME), ("Blues", "theme_light")])
def test_the_saved_block_passes_the_checker(palette, theme):
    raw = copy.deepcopy(ConfigManager(str(RECIPE)).raw_config)
    raw["plot_defaults"] = merged_plot_defaults(BLOCK, palette, theme)
    codes = check_recipe(raw, "run", file_stem=RECIPE.stem).codes()
    assert not [c for c in codes if c.startswith("PD")], codes


def test_the_checker_still_refuses_a_removed_key_so_the_test_above_can_fail():
    raw = copy.deepcopy(ConfigManager(str(RECIPE)).raw_config)
    raw["plot_defaults"] = {**BLOCK, "legend_position": "top"}
    assert "PD02" in check_recipe(raw, "run", file_stem=RECIPE.stem).codes()
