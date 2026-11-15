# Proposal: `.claude/rules/workspace_standard.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked by `grep` of the file for action names, parity and ADR numbers, against `libs/transformer/src/transformer/actions/modified.py:19` and `polars_rows.py:27` (the `@deps` lines of today's actions), ADR-106.

## 1. Line 34, the Viz Factory row (FACT; follows `rules_viz_factory.md.proposal.md` change 1)

Today (line 34): `| **Viz Factory** | Artist Pillar, Plotnine Parity, Core Geoms | [rules_viz_factory.md](...) |`
Proposed: `| **Viz Factory** | Artist Pillar, how the library follows the recipe standard (exact / modified / own components), Core Geoms | [rules_viz_factory.md](...) |`
Why: the parity mandate is replaced (ADR-106 V9, approved by Eve).

## 2. Lines 76, 96, 109, the `@deps` examples (FACT)

Today: line 76 `grep -r "consumes:.*action:cast" ...`; line 96 `# provides: action:cast, action:coalesce`; line 109 `# consumes: action:mutate, action:join, action:cast, dataset:metadata_schema`.
Proposed: line 76 `action:polars_cast`; line 96 `# provides: action:polars_cast, action:polars_coalesce`; line 109 `# consumes: action:polars_with_columns, action:polars_join, action:polars_cast, dataset:metadata_schema`.
Why: `cast`, `coalesce`, `mutate`, `join` are not registered names (68 registered; `@deps` of today's actions read `action:polars_head`, `action:modif_filter`). An agent copying the example would write a name that nothing provides.

## 3. Line 168 (no change)

`All assembly steps files (assembly/*.yaml)` stays true: both shipped recipe folders that have joins use `assembly/`.

## 4. Lines 18-30 (no change), checked
The Master Index table cites no ADR number that is wrong (checked by grep: the only ADR numbers are none in the table). No other change.

## Not settled
None.
