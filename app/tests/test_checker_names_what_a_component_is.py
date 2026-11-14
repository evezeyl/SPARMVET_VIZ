"""The checker's catalogues carry what each plot component is to plotnine, and a wrong argument says it (ADR-106 V1).

# @deps
# consumes: app/modules/data_analysis_recipe_validator.py (checker_catalogs), libs/utils/src/utils/recipe_check.py
# @end_deps
"""
from app.modules.data_analysis_recipe_validator import checker_catalogs
from utils.recipe_check import check_recipe


def _recipe(layer):
    return {
        "id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine",
        "info": {"label": "R", "description": "d", "contact": "c"},
        "data_schemas": {"A": {"label": "A", "description": "d", "source": {"type": "local_tsv", "path": "assets/test_data/a.tsv"},
                               "null_values": [], "strip": True,
                               "input_fields": {"v": {"type": "Float64"}}, "wrangling": {"tier1": []}}},
        "analysis_groups": {"g": {"label": "G", "description": "d", "plots": {"p": {
            "label": "P", "description": "d",
            "spec": {"target_dataset": "A", "mapping": {"x": "v"}, "layers": [{"name": "geom_point"}, layer]}}}}},
    }


def test_the_catalogues_carry_the_kind_of_every_component():
    catalogs = checker_catalogs()
    assert set(catalogs["component_kinds"]) == catalogs["components"]
    assert set(catalogs["component_kinds"].values()) == {"exact", "modified", "own"}


def test_a_wrong_argument_of_an_exact_and_of_a_modified_component_says_what_it_is():
    catalogs = checker_catalogs()
    for layer, expected in [({"name": "geom_point", "params": {"colr": "red"}}, "exactly plotnine's geom_point"),
                            ({"name": "theme_bw", "params": {"colr": "red"}}, "changes plotnine's theme_bw")]:
        problems = [p for p in check_recipe(_recipe(layer), "run", catalogs=catalogs, file_stem="r").problems
                    if p.code == "PS04" and "colr" in p.message]
        assert problems and expected in problems[0].message, problems
