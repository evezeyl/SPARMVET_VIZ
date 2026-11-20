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


class TestTheAuditList:
    """D-0332: in an audit recipe a tier holds `steps` (the author's) and `audit_steps` (the audit's); the engine runs the first, then the second. Only an
    audit copy has the second list: the caller says so (`audit=True`), and in any other recipe the key is refused, never run and never skipped."""

    AUDIT_FILTER = {"action": "modif_filter", "column": "v", "op": "gt", "value": 1, "na": "keep", "id": "audit_1a2b3c4d_1", "audit_comment": "why"}
    AUDIT_DROP = {"action": "polars_drop", "columns": ["w"], "id": "audit_1a2b3c4d_2", "audit_comment": "why"}

    def body(self):
        return {"tier1": {"steps": [SORT], "audit_steps": [self.AUDIT_FILTER, self.AUDIT_DROP]}, "tier2": {"steps": [CAST]}}

    def test_an_audit_recipe_runs_the_authors_steps_then_the_audit_steps_in_list_order(self):
        assert DataWrangler.tier_steps(self.body(), "tier1", audit=True) == [SORT, self.AUDIT_FILTER, self.AUDIT_DROP]
        assert DataWrangler.tier_steps(self.body(), "tier2", audit=True) == [CAST], "a tier with no audit list is as it was"

    def test_an_empty_audit_list_gives_the_authors_steps_and_nothing_else(self):
        assert DataWrangler.tier_steps({"tier1": {"steps": [SORT], "audit_steps": []}}, "tier1", audit=True) == [SORT]

    def test_a_tier_that_holds_only_audit_steps_runs_them(self):
        assert DataWrangler.tier_steps({"tier2": {"steps": [], "audit_steps": [self.AUDIT_FILTER]}}, "tier2", audit=True) == [self.AUDIT_FILTER]

    @pytest.mark.parametrize("tier", ["tier1", "tier2", "tier3"])
    def test_in_a_recipe_that_is_not_an_audit_copy_the_audit_list_is_refused_in_plain_words(self, tier):
        with pytest.raises(DataAnalysisRecipeError, match="only an audit recipe has audit steps") as caught:
            DataWrangler.tier_steps({tier: {"steps": [SORT], "audit_steps": [self.AUDIT_FILTER]}}, tier)
        assert "audit_steps" in str(caught.value) and caught.value.tip
        with pytest.raises(DataAnalysisRecipeError, match="only an audit recipe"):
            DataWrangler.tier_steps({tier: {"steps": [], "audit_steps": []}}, tier)   # even an empty list: the key is not for an ordinary recipe

    def test_an_audit_list_that_is_not_a_list_is_refused(self):
        with pytest.raises(DataAnalysisRecipeError, match="is not a list of steps"):
            DataWrangler.tier_steps({"tier1": {"steps": [], "audit_steps": "x"}}, "tier1", audit=True)

    def test_another_key_in_a_tier_is_still_refused_in_an_audit_recipe(self):
        with pytest.raises(DataAnalysisRecipeError, match="a tier holds data_engine and steps only"):
            DataWrangler.tier_steps({"tier1": {"steps": [], "audit_steps": [], "comment": "x"}}, "tier1", audit=True)

    def test_the_audit_steps_run_after_the_authors_steps_on_data(self):
        """Head 1 of the sorted rows, THEN the audit filter: the filter sees the one row the author's steps left."""
        import polars as pl
        body = {"tier1": {"steps": [{"action": "polars_sort", "by": ["v"], "descending": [True], "maintain_order": True}, {"action": "polars_head", "n": 1}],
                          "audit_steps": [{"action": "modif_filter", "column": "v", "op": "eq", "value": 1, "na": "remove", "id": "audit_1a2b3c4d_1", "audit_comment": "w"}]}}
        lf = pl.LazyFrame({"v": [1, 2, 3]})
        steps = DataWrangler.tier_steps(body, "tier1", audit=True)
        assert DataWrangler().run(lf, steps).collect()["v"].to_list() == [], "3 is the only row after head 1; the audit filter v = 1 then leaves nothing"
        swapped = steps[2:] + steps[:2]
        assert DataWrangler().run(lf, swapped).collect()["v"].to_list() == [1], "the reverse order would give another table: the order is the format's, not free"
