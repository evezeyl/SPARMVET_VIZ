"""
ID Reconciliation library — headless, Shiny-free, Tier 1 domain library.

Public API: import only from this module. Internal sub-modules are implementation details.
"""
# @deps
# provides: IDReconciliationEngine, IDPair, MatchResult, PatternSuggestion,
#           IdTransformation, detect_many_to_many, format_match_table, apply_recode_step, recipe_steps
# consumes: libs/id_reconciliation/src/id_reconciliation/data_structures.py,
#           libs/id_reconciliation/src/id_reconciliation/core.py,
#           libs/id_reconciliation/src/id_reconciliation/recipe_steps.py
# consumed_by: app/handlers/test_lab_handlers.py, app/modules/test_lab_studio.py
# @end_deps

from .data_structures import IDPair, MatchResult, PatternSuggestion, IdTransformation
from .core import (
    IDReconciliationEngine,
    detect_many_to_many,
    format_match_table,
    apply_recode_step,
)
from .recipe_steps import recipe_steps

__all__ = [
    "IDReconciliationEngine",
    "IDPair",
    "MatchResult",
    "PatternSuggestion",
    "IdTransformation",
    "detect_many_to_many",
    "format_match_table",
    "apply_recode_step",
    "recipe_steps",
]
