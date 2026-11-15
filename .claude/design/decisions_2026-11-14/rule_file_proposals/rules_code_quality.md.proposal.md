# Proposal: `.claude/rules/rules_code_quality.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked against: the file list of `libs/transformer/tests/` (no `transformer_integrity_suite.py`), `libs/utils/src/utils/recipe_spec.yaml` (`renamed.schema.output_fields`), `rules_viz_factory.md` section 1.

## 1. Lines 40-41, the debug-script exception (FACT)

Today: `Scripts like \`debug_wrangler.py\` and \`transformer_integrity_suite.py\` produce terminal tables for developer review ...`
Proposed: `Scripts like \`debug_wrangler.py\` and \`debug_assembler.py\` produce terminal tables for developer review ...`
Why: the transformer has no integrity suite any more (ACTION-RECIPES-1, `rules_verification_testing.md` line 22, Eve 2026-11-14). The two scripts named exist and run (2026-11-15).

## 2. Lines 63-65, the "Good" comment example (FACT)

Today (lines 63-65):
```python
# output_fields may be absent if the schema uses identity passthrough (ADR-014)
for schema_id, schema in schemas.items():
    fields.update(schema.get("input_fields", schema.get("output_fields", {})).keys())
```
Proposed (same purpose, a constraint that is true today):
```python
# a key written unquoted as on is read by YAML as the boolean True: take both spellings (check T07 refuses it in recipes)
on_columns = step.get("on", step.get(True))
```
Why: `output_fields` is removed (ADR-100 point 5; ADR-014 superseded by DEC23/DEC24/DEC45), so the example teaches a removed key and cites a superseded ADR. The replacement example comes from `recipe_check.py:532` (`on = step.get("on", step.get(True))`). Any other true "constraint note" example would do; Eve may pick another.

## 3. Line 106, the Tier C example text (no change)
`percentiles` appears in a descriptive module docstring example (not an action name). Left as it is; it is an illustration of a module header, not a registry claim. (The action `percentile` was removed, DEC40; the word is plain English there.)

## Not settled
None.
