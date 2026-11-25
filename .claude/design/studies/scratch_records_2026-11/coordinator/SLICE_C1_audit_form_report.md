# Slice C, piece 1: the audit recipe in memory in the decided form (builder report, digest by the coordinator, 2026-11-20)

Branch `task/slice-c-audit-form`, worktree `.claude/worktrees/slice-c-audit-form`, base dev `bd9df88e`, head `36943b4b`. No screen, no file written. Under review (scratch `slice_c1_review/`).

## Built
- Form: each tier body `{steps: [author's], audit_steps: [...]}`; an audit step `{operation, id: audit_<8hex>_<k>, audit_comment}`; the engine runs `steps`, then `audit_steps`. The slice A form is gone (no shim).
- One place for the names and readers: `libs/utils/src/utils/recipe_tiers.py` (`AUDIT_STEPS`, `AUDIT_COMMENT`, `AUDIT_ID`; `step_list` = author's then audit; `author_steps`; `audit_steps_of`; `tier2_parts`, `tier3_parts`; `without_audit_steps`). Allowed audit actions in ONE place: `libs/utils/src/utils/action_names.py:62` `AUDIT_ACTIONS = (modif_filter, polars_drop)`.
- The copy `libs/utils/src/utils/audit_copy.py`: a handle `AuditCopy` (`.recipe`, `.original`, `.audit_id`, `.created`); `start_audit`, `add_step(audit, place, step, comment) -> id`, `remove_step(audit, step_id)` (any step; exact add-then-remove), `integrity_errors`. The number k is a counter in the handle that never goes down.
- Keys `app/modules/cache_keys.py`: `audit_steps` out of the original's parts; a1, a2, a3 from the audit lists (operations only, in order). Keys of the 54 shipped recipes (334 keys) byte-identical before and after (builder RAN old and new code).
- Checker: new codes AU01 (`audit_steps` or `audit_comment` outside an audit recipe), AU02 (an audit step that is not allowed), AU03 (no audit id, id twice, no reason). PROVISIONAL codes and texts.
- Engine: `DataWrangler.tier_steps(body, tier, audit=False)`; an ordinary recipe holding `audit_steps` is refused by the engine too (`orchestrator.py:58` `refuse_audit_steps_outside_an_audit`); `LoadedDataAnalysisRecipe.is_audit_copy` true only for a recipe handed in memory.
- Scan test `app/tests/test_tier_steps_one_reader.py` (13 files allowed with a count and a reason).

## Tests (builder RAN)
6748 passed, 9 skipped, 0 failed on the set it ran (libs/utils, transformer, blueprint_arch, the audit, key, gate, session, recipe tests); the real case of slice A reproduced (221 of 623 rows; 26 of 28 tables reused, 2 built; 1 of 17 plots affected). 17 breaks seen failing. NOT run: the whole suite, browser tests, the audits.

## Texts a user reads (PROVISIONAL; for the owner later)
"only an audit recipe has audit steps (an audit recipe is the copy the audit made of a recipe; the app writes it, an author never does)"; "the audit step is '<action>'; an audit step is a filter, a column drop or a removal by key: modif_filter, polars_drop (a removal by key is the filter on the key column)"; "the audit step has no reason (audit_comment is a text that is not empty)"; and the copy's refusals.

## Open points (the builder decided none)
1. The recipe format version: the spec says a new key changes the number, and the number is global (all 54 recipes say `spec_version: 1`; four writers emit 1). Built: number unchanged, the new keys exist only in the audit profile (PROVISIONAL). Question for the owner: is an audit recipe a recipe of format 1?
2. "A removal by key" is a `modif_filter` on the key column; the check does not verify the column or the operator, so any filter passes as "a filter" (which her sentence "only filter and drops" allows).
3. The typed-value check of a filter is not run on audit steps by the checker (the engine's strict filter still judges at run).
4. Where the counter and the 8 hex live when the audit is a FILE: the audit record (D-0333) is the natural place; re-opening an audit from a file is NOT built.
5. Wording of AU01 to AU03.

## For the next piece (the file)
`is_audit_copy` must become true for an audit recipe read from its file (the key `info.audit_of`, D-0339); the counter restored from the record; the export fork `t3_translator.py:277` still appends to the author's tier 2 and goes with slice D.

## Out-of-date sentences (need the owner's yes: spec, design, ADR)
`recipe_format_spec.md` 122, 232, 422-441, 433, 689, section 11 (AU codes), 4.1; `home_stage2_mechanism_spec.md` 55, 110, 122, 167; `home_audit_steps.md:543`; ADR-105 point 6 (`architecture_decisions.md:5339`); `docs/foundations/reproducibility_hash_schema.qmd:12`; tasks.md AUDIT-SLICE-A5 text; the dependency index (regenerate).
