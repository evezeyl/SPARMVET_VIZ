"""The names of registered actions that code outside the registry has to spell (spec R4, decision DEC31).

An action name written as a string in a consumer (the audit translator, the assembler, the bootstrapper, the checker) goes
stale when the action is renamed. Consumers read the name from here instead; a test in `libs/transformer` fails when a
constant names no registered action, and when a registered name of the new vocabulary is spelled as a string outside
the registry. The constants live in `libs/utils` (Tier 1) so that libraries that may not import `transformer`
(`test_lab`, `id_reconciliation`) can read them.

Only names that a consumer needs are listed; add one with its first consumer.

# @deps
# provides: constant:JOIN, constant:SELECT, constant:DROP, constant:WITH_COLUMNS, constant:FILTER, constant:CAST, constant:TIER1_ONLY
# consumed_by: libs/utils/src/utils/recipe_check.py, libs/transformer/tests/test_action_names.py
# doc: .claude/design/recipe_format_spec.md (R4)
# @end_deps
"""
JOIN = "polars_join"
SELECT = "polars_select"
DROP = "polars_drop"
WITH_COLUMNS = "polars_with_columns"
CAST = "polars_cast"
FILTER = "modif_filter"

# Actions that are allowed only in tier 1 (spec ST05).
TIER1_ONLY = frozenset({JOIN})

ALL = {name: value for name, value in globals().items() if name.isupper() and isinstance(value, str)}
