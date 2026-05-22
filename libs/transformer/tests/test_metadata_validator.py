"""Tests for MetadataValidator type alias removal (LEGACY-TYPE-ALIASES-1).

Run with:
    .venv/bin/python -m pytest libs/transformer/tests/test_metadata_validator.py -v
"""
from __future__ import annotations

import pytest
import polars as pl

from transformer.metadata_validator import MetadataValidator
from utils.errors import TransformationError


def _lf():
    return pl.DataFrame({"sample_id": ["S1", "S2"], "species": ["cat", "dog"]}).lazy()


def test_string_type_alias_raises():
    """MetadataValidator must raise TransformationError for removed 'string' alias.

    LEGACY-TYPE-ALIASES-1: 'string' was removed in Phase 34. Use 'categorical' or 'utf8'.
    """
    contract = {"sample_id": {"type": "string"}}
    validator = MetadataValidator()
    with pytest.raises(TransformationError, match="string.*removed"):
        validator.enforce_schema(_lf(), contract)


def test_character_type_alias_raises():
    """MetadataValidator must raise TransformationError for removed 'character' alias.

    LEGACY-TYPE-ALIASES-1: 'character' was removed in Phase 34. Use 'categorical' or 'utf8'.
    """
    contract = {"sample_id": {"type": "character"}}
    validator = MetadataValidator()
    with pytest.raises(TransformationError, match="character.*removed"):
        validator.enforce_schema(_lf(), contract)


def test_categorical_type_accepted():
    """MetadataValidator must accept the canonical 'categorical' type without error."""
    contract = {"sample_id": {"type": "categorical"}, "species": {"type": "categorical"}}
    validator = MetadataValidator()
    result = validator.enforce_schema(_lf(), contract)
    assert result is not None


def test_utf8_type_accepted():
    """MetadataValidator must accept 'utf8' as the canonical free-text type."""
    contract = {"sample_id": {"type": "utf8"}}
    validator = MetadataValidator()
    result = validator.enforce_schema(_lf(), contract)
    assert result is not None
