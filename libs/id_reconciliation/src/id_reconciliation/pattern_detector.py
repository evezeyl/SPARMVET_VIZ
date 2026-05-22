from __future__ import annotations

from utils.id_patterns import PatternSuggestion, detect_patterns, apply_pattern, suggest_regex

# @deps
# provides: detect_patterns, apply_pattern, suggest_regex (re-exported from utils.id_patterns)
# consumes: libs/utils/src/utils/id_patterns.py
# consumed_by: libs/id_reconciliation/src/id_reconciliation/core.py
# @end_deps

__all__ = ["PatternSuggestion", "detect_patterns", "apply_pattern", "suggest_regex"]
