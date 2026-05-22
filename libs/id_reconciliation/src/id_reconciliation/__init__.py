"""
ID Reconciliation library — headless, Shiny-free, Tier 1 domain library.

Public API: import only from this module. Internal sub-modules are implementation details.
"""
# @deps
# provides: IDReconciliationEngine, IDPair, MatchResult, PatternSuggestion,
#           TransformationRecipe, detect_many_to_many, format_match_table, apply_recode_step
# consumes: libs/id_reconciliation/src/id_reconciliation/data_structures.py,
#           libs/id_reconciliation/src/id_reconciliation/core.py
# consumed_by: app/handlers/test_lab_handlers.py (future)
# @end_deps

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
