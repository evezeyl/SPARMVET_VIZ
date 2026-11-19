"""The default tip of DataAnalysisRecipeError names the required keys of a recipe as the specification lists them."""
from utils.errors import DataAnalysisRecipeError
from utils.recipe_check import spec


def test_the_default_tip_names_every_required_top_key_and_no_removed_one():
    tip = DataAnalysisRecipeError("x").tip
    for key in spec()["elements"]["top"]["required"]:
        assert key in tip
    for old in ("wrangling", "output_fields"):
        assert old not in tip
