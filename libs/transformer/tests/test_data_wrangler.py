"""
Tests for DataWrangler.tier_steps(): the steps of one tier of a table or a join (D-0250).

A tier is its own key, a mapping with `steps` (and an optional `data_engine`). The old shapes are refused with the key
named; none is read.

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/transformer/tests/test_data_wrangler.py -v
"""
import pytest

from transformer.data_wrangler import DataWrangler
from utils.errors import DataAnalysisRecipeError

SORT = {"action": "polars_sort", "by": ["Year"]}
CAST = {"action": "polars_cast", "columns": ["Year"], "dtype": "String"}


class TestOldShapesAreRefused:
    """The old shapes raise DataAnalysisRecipeError with the key named; the steps are not read from them (D-0050)."""

    def test_a_wrangling_key_is_refused_and_named(self):
        with pytest.raises(DataAnalysisRecipeError) as caught:
            DataWrangler.tier_steps({"wrangling": {"tier1": [SORT]}}, "tier1")
        assert "wrangling" in str(caught.value)
        assert "migrate_recipe_engine_keys" in caught.value.tip

    def test_a_steps_container_of_a_join_is_refused_and_named(self):
        with pytest.raises(DataAnalysisRecipeError) as caught:
            DataWrangler.tier_steps({"ingredients": [], "steps": {"tier1": [SORT]}}, "tier1")
        assert "'steps'" in str(caught.value)

    @pytest.mark.parametrize("tier", ["tier1", "tier2"])
    def test_a_tier_written_as_a_list_is_refused(self, tier):
        with pytest.raises(DataAnalysisRecipeError) as caught:
            DataWrangler.tier_steps({tier: [SORT]}, tier)
        assert tier in str(caught.value) and "list" in str(caught.value)

    def test_a_tier_that_is_empty_in_the_file_is_refused_not_read_as_no_steps(self):
        with pytest.raises(DataAnalysisRecipeError):
            DataWrangler.tier_steps({"tier1": None}, "tier1")

    def test_a_tier_without_a_steps_list_is_refused(self):
        with pytest.raises(DataAnalysisRecipeError):
            DataWrangler.tier_steps({"tier1": {"data_engine": "python-polars"}}, "tier1")

    def test_an_unknown_key_inside_a_tier_is_refused(self):
        with pytest.raises(DataAnalysisRecipeError) as caught:
            DataWrangler.tier_steps({"tier1": {"steps": [], "tier2": {"steps": []}}}, "tier1")
        assert "tier2" in str(caught.value)

    def test_a_body_that_is_not_a_mapping_is_refused(self):
        with pytest.raises(DataAnalysisRecipeError):
            DataWrangler.tier_steps([SORT], "tier1")

    def test_a_tier_name_other_than_tier1_and_tier2_is_a_programming_error(self):
        with pytest.raises(ValueError):
            DataWrangler.tier_steps({"tier1": {"steps": []}}, "all")


class TestTheNewShape:
    """Tiers written as their own keys are read."""

    def test_an_empty_body_gives_no_steps(self):
        assert DataWrangler.tier_steps(None, "tier1") == []
        assert DataWrangler.tier_steps({}, "tier1") == []

    def test_tier1_is_returned(self):
        result = DataWrangler.tier_steps({"tier1": {"steps": [SORT]}, "tier2": {"steps": []}}, "tier1")
        assert result == [SORT]

    def test_the_two_tiers_stay_separate(self):
        body = {"tier1": {"steps": [SORT]}, "tier2": {"steps": [CAST]}}
        assert DataWrangler.tier_steps(body, "tier1") == [SORT]
        assert DataWrangler.tier_steps(body, "tier2") == [CAST]

    def test_a_tier_that_is_not_written_gives_no_steps(self):
        assert DataWrangler.tier_steps({"tier1": {"steps": [SORT]}}, "tier2") == []

    def test_an_empty_tier_gives_no_steps(self):
        assert DataWrangler.tier_steps({"tier1": {"steps": []}}, "tier1") == []

    def test_the_engine_of_a_tier_is_not_a_step(self):
        body = {"tier1": {"data_engine": "python-polars", "steps": [SORT]}}
        assert DataWrangler.tier_steps(body, "tier1") == [SORT]


class TestPerformanceHeuristic:
    def test_a_join_in_tier2_is_refused(self):
        with pytest.raises(DataAnalysisRecipeError) as caught:
            DataWrangler.tier_steps({"tier2": {"steps": [{"action": "polars_join", "right_ingredient": "B"}]}}, "tier2")
        assert "Tier 2" in str(caught.value)

    def test_a_join_in_tier1_is_fine(self):
        step = {"action": "polars_join", "right_ingredient": "B"}
        assert DataWrangler.tier_steps({"tier1": {"steps": [step]}}, "tier1") == [step]
