# id_reconciliation

Headless, Shiny-free Tier 1 domain library for pairwise ID reconciliation.

## Public API

```python
from id_reconciliation import (
    IDReconciliationEngine,
    IDPair,
    MatchResult,
    TransformationRecipe,
    detect_many_to_many,
    format_match_table,
    apply_recode_step,
)

# PatternSuggestion and pattern primitives live in utils — canonical import:
from utils.id_patterns import PatternSuggestion, detect_patterns, apply_pattern, suggest_regex
```

## Usage

```python
engine = IDReconciliationEngine()
results = engine.reconcile(ref_ids=["ABCD_001", "ABCD_002"], target_ids=["001_ABCD", "ABCD_002"])
df = format_match_table(results)
```

## Dependencies

- `polars >= 1.0`
- `utils` (SPARMVET Tier 1 base)
- `rapidfuzz` (token-set ratio fuzzy matching)

## Rules

- No Shiny imports. No peer domain lib imports. See `rules_test_lab.md §2`.
- All imports resolve via `pip install -e libs/id_reconciliation/`.
