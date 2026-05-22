"""
Tests for DataWrangler._resolve_tier() structural validation.

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/transformer/tests/test_data_wrangler.py -v
"""
import pytest

from transformer.data_wrangler import DataWrangler
from utils.errors import ManifestError


class TestResolveTierFlatListRejection:
    """Flat wrangling list must raise ManifestError (LEGACY-FLAT-WRANGLING-1)."""

    def test_flat_list_raises_manifest_error(self):
        steps = [{"action": "cast", "columns": ["Year"], "dtype": "String"}]
        with pytest.raises(ManifestError):
            DataWrangler._resolve_tier(steps, "tier1")

    def test_flat_list_error_message_is_actionable(self):
        steps = [{"action": "cast", "columns": ["Year"], "dtype": "String"}]
        with pytest.raises(ManifestError) as exc_info:
            DataWrangler._resolve_tier(steps, "tier1")
        assert "tier1" in str(exc_info.value).lower() or "tiered" in str(exc_info.value).lower()

    def test_flat_list_all_tier_also_rejected(self):
        steps = [{"action": "sort", "columns": ["Year"]}]
        with pytest.raises(ManifestError):
            DataWrangler._resolve_tier(steps, "all")

    def test_flat_list_tier2_also_rejected(self):
        steps = [{"action": "sort", "columns": ["Year"]}]
        with pytest.raises(ManifestError):
            DataWrangler._resolve_tier(steps, "tier2")


class TestResolveTierValidPaths:
    """Tiered and empty blocks must continue to work correctly."""

    def test_empty_block_returns_empty_list(self):
        assert DataWrangler._resolve_tier(None, "tier1") == []
        assert DataWrangler._resolve_tier([], "tier1") == []
        assert DataWrangler._resolve_tier({}, "tier1") == []

    def test_tiered_block_tier1_returned(self):
        block = {"tier1": [{"action": "sort", "columns": ["Year"]}], "tier2": []}
        result = DataWrangler._resolve_tier(block, "tier1")
        assert len(result) == 1
        assert result[0]["action"] == "sort"

    def test_tiered_block_tier2_empty(self):
        block = {"tier1": [{"action": "sort", "columns": ["Year"]}], "tier2": []}
        assert DataWrangler._resolve_tier(block, "tier2") == []

    def test_tiered_block_all_concatenates(self):
        block = {
            "tier1": [{"action": "sort", "columns": ["Year"]}],
            "tier2": [{"action": "cast", "columns": ["Year"], "dtype": "String"}],
        }
        result = DataWrangler._resolve_tier(block, "all")
        assert len(result) == 2
