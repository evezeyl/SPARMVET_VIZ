"""
ID Reconciliation library — headless, Shiny-free, Tier 1 domain library.

Public API: import only from this module. Internal sub-modules are implementation details.
"""

from .data_structures import IDPair, MatchResult, PatternSuggestion, TransformationRecipe
from .core import (
    IDReconciliationEngine,
    detect_many_to_many,
    format_match_table,
    apply_recode_step,
)

__all__ = [
    "IDReconciliationEngine",
    "IDPair",
    "MatchResult",
    "PatternSuggestion",
    "TransformationRecipe",
    "detect_many_to_many",
    "format_match_table",
    "apply_recode_step",
]
