
# Restoring the gallery layout

"@Agent: @dasharch - SURGICAL UI REVERSION (Gallery Aesthetic Restore).

GOAL: Restore the Gallery Split-Pane layout (ADR-033) while retaining the new static-loading backend (TBD-03).

1. FORENSIC DIFF:
   - Compare app/modules/gallery_viewer.py between commit 9cefea45b63d7f1d2241afa911905af8a96be1b3, 033edcbf4ee77cceb4c8540c7dec92123559401a, 830c7e17498e23d42fa0501d9c7cd57a76599d76, aa0fe2f53358d8a50f607215904d9033e804aabf, 0679fa9f0f26f8c320bc8af2331d46e26d3b94c8,
   - Identify where the major change of the layout was done, where the 50/50 Split-Pane with 3 panes left (Technical vs. Educational) logic was removed.

2. RE-IMPLEMENTATION RULES:
   - RESTORE: The two-pane layout with its tabs, the markdown rendering for 'recipe_meta.md', and the flex-centering aesthetics mandated in ADR-033.
   - RETAIN: The recent logic that loads assets directly from Location 5 (Location 5 = assets/gallery_data/ per ADR-031).
   - RETAIN: The 'Copy to Tier 3' functionality.

3. ALIGNMENT CHECK:
   - Ensure 'Violet Law' formatting is used for any component labels in the UI [ADR-022].
   - Verify that the 'Educational Pane' sections (Suitability, Schema, Interpretations) are present [ADR-033].

REPORT: Summarize the changes restored from the old commit.
HALT: Once the file is modified, run app/tests/test_ui_persona_masking.py and provide a screenshot/preview of the restored Gallery." And launch the ui in developper persona so the user can inspect the restored gallery.

# First

--- Sync ----

@Agent: @dasharch - SYSTEM INITIALIZATION & TASK DECOMPOSITION.

1. PERMANENT CONTEXT (Read immediately):

- ./.claude/rules/workspace_standard.md (Authority map & VENV enforcement)
- ./.claude/tasks/tasks.md (Current execution status)
- ./.claude/knowledge/project_conventions.md (Path registry & terminology)

1. MANDATORY SEARCH & RETRIEVAL PROTOCOL:
You are equipped with a modular rule system. Do not guess logic. You MUST identify and read the relevant files from the following directories BEFORE executing a task. Attached file describes this logic. (see PATH_INITIATION.md attached)

Halt and wait for other instructions.

"@Agent: @dasharch - SYSTEM ALIGNMENT & ARCHITECTURAL RECONCILIATION.

The session cache is clean. You must rebuild your project 'brain' from the source of truth.

1. MANDATORY DISPATCH (Read Order):
   - Read ./.claude/rules/workspace_standard.md to map governing authority.
   - Read ./.claude/knowledge/project_conventions.md to identify the 'Who/Where/How'.
   - Read ./.claude/plans/implementation_plan_master.md to identify the current Phase.

2. MANDATORY SEARCH & RETRIEVAL PROTOCOL:
You are equipped with a modular rule system. Do not guess logic. You MUST identify and read the relevant files from the following directories BEFORE executing a task. Attached file describes this logic. (see PATH_INITIATION.md attached)

3. SEARCH & RETRIEVAL (No-Discovery Rule):
   - Use tree.txt and PATH_INITIATION.md to locate all active library and app files.
   - Do not perform exploratory reads. If a file is missing, HALT and report.

4. COMPREHENSIVE AUDIT CATEGORIES and FOUNDATIONAL CHECK:
   - Verify that all core libraries (libs/transformer, libs/viz_factory, etc.) are in 'Editable Mode' (-e) [ADR-011].
   - Confirm that sys.path.append is NOT used, and package-first authority is maintained [ADR-016].
   - FUNCTIONALITY: Identify implemented vs. planned features for Phase 11/12. Specifically check app/src/ui.py and server.py for ADR-029a (Theater Layout) and ADR-036 (ID Sanitation).
   - CONSISTENCY: Compare the 't3_recipe' logic in WrangleStudio against the Tiered Data Lifecycle [ADR-024]. Ensure Tier 1/2 are immutable and Tier 3 is transient.
   - Verify implementation of hash to avoid recalculations of data
   - DISCREPANCIES: Identify 'Ghost Logic' (code without an ADR or Task) and 'Ghost Plans' (Tasks marked [x] but not physically present).
   - DOCUMENTATION INTEGRITY:
      - Check all ./libs/ READMEs for sync with current src/ logic.
      - Verify 'Violet Law' compliance in ./docs/ (.qmd files).
      - Ensure 'Split-Documentation Strategy' (Foundations vs Appendix) is maintained.
   - The UI was quite slow: ADVISE on improvements that could make the UI snappier.

5. A part of your plan should  present a Table with:
   - Component | Status (Implemented/Partial/Planned) | Logic Discrepancy | Doc Sync Status.
   - List of identified Technical Debt items.
   - Confirmation of ./.venv/bin/python interpreter lock.

HALT: Only provide the audit report. Do not modify files. Waiting for @verify to align foundations."
