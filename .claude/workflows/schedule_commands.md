# Audit Routine `/schedule` Commands

Ready-to-paste prompts for creating each audit routine via the Claude Code CLI.
In any VS Code / Claude Code session, type `/schedule` and paste the prompt for the routine you want to create.

**Reference:** Full routine definitions and status matrix → `.claude/workflows/audit_routine_registry.md`

---

## How to use

1. Open VS Code with this project (Claude Code active).
2. Type `/schedule` and press Enter.
3. Claude will ask you questions about the routine — paste the relevant prompt below.
4. After creation, copy the Routine ID from `claude.ai/code/routines` and paste it into the status matrix in `audit_routine_registry.md`.

---

## Routine 1 — @deps Block Verification

**Schedule:** Sundays at 23:00

```
Create a weekly audit routine for the SPARMVET_VIZ project that runs every Sunday at 23:00.

Name: "SPARMVET: @deps Block Verification"

Purpose: Scan all load-bearing Python files in libs/ and app/ to verify that each carries a
current @deps annotation block, as required by workspace_standard.md §5 (Session Law).

Command to run (from project root):
  .venv/bin/python scripts/audit_deps_verify.py --output .claude/logs/audits/audit_deps_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_deps_YYYY-MM-DD.md
2. If exit code is 1 (FAIL): create tasks in .claude/tasks/tasks.md under a new section
   "### 🔴 @deps Violations YYYY-MM-DD" for each missing file. Use format:
   - [ ] [AUDIT] Add @deps block to `path/to/file.py` [haiku/low]
3. Update the status matrix in .claude/workflows/audit_routine_registry.md — set
   "Last Run" date and "Last Result" (PASS / FAIL + violation count)
4. Commit with message: "audit: @deps verification YYYY-MM-DD [PASS|FAIL]"

Exit codes: 0 = PASS, 1 = violations found, 2 = script error.
```

---

## Routine 2 — ADR-011 Cross-Lib Violation Scan

**Schedule:** Sundays at 23:00

```
Create a weekly audit routine for the SPARMVET_VIZ project that runs every Sunday at 23:00.

Name: "SPARMVET: ADR-011 Cross-Lib Scan"

Purpose: Detect peer-to-peer imports between domain libraries in libs/ using AST parsing.
Per ADR-011 / ADR-016 (Two-Tier Dependency Model), domain libs must only import from
libs/utils/ (Tier 1 base) or stdlib. Any new violations are BLOCKERS.

Command to run (from project root):
  .venv/bin/python scripts/audit_cross_lib.py --output .claude/logs/audits/audit_cross_lib_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_cross_lib_YYYY-MM-DD.md
2. If BLOCKERS found (new violations beyond KNOWN_VIOLATIONS set in the script):
   - Create tasks in .claude/tasks/tasks.md under "### 🔴 ADR-011 Violations YYYY-MM-DD":
     - [ ] [BLOCKER] Fix cross-lib import: `from_lib` → `to_lib` in `file.py:line` [sonnet/high]
   - Do NOT add to KNOWN_VIOLATIONS without explicit user confirmation
3. If KNOWN_DEBT only (no new blockers): result is ⚠️ (expected, no new tasks needed)
4. Update the status matrix in .claude/workflows/audit_routine_registry.md
5. Commit with message: "audit: cross-lib scan YYYY-MM-DD [PASS|BLOCKER|KNOWN_DEBT]"

Exit codes: 0 = PASS or known debt only, 1 = new blockers found, 2 = script error.
```

---

## Routine 3 — Manifest Structure Integrity

**Schedule:** Wednesdays at 22:00

```
Create a weekly audit routine for the SPARMVET_VIZ project that runs every Wednesday at 22:00.

Name: "SPARMVET: Manifest Integrity"

Purpose: Run all pipeline manifests in config/manifests/pipelines/ through the assembler
(debug_assembler.py) to verify they produce valid Parquet output without errors.
Catches broken wrangling steps, missing fields, YAML syntax issues, and action name typos.

Command to run (from project root):
  .venv/bin/python scripts/audit_manifest_integrity.py --output .claude/logs/audits/audit_manifest_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_manifest_YYYY-MM-DD.md
2. For each FAIL manifest:
   - Read the error output in the report carefully (assembler stderr)
   - Create a task in .claude/tasks/tasks.md:
     - [ ] [AUDIT] Fix manifest `config/manifests/pipelines/NAME.yaml`: [brief error summary] [sonnet/medium]
3. Assembler scratch artifacts are in tmpAI/audit_manifest_integrity/ — inspect TSV outputs
   for data contract issues
4. Update the status matrix in .claude/workflows/audit_routine_registry.md
5. Commit with message: "audit: manifest integrity YYYY-MM-DD [PASS|FAIL N]"

Exit codes: 0 = all pass, 1 = one or more failures, 2 = script/environment error.
```

---

## Routine 4 — Task-to-Code Drift Check

**Schedule:** Fridays at 20:00

```
Create a weekly audit routine for the SPARMVET_VIZ project that runs every Friday at 20:00.

Name: "SPARMVET: Task Drift Check"

Purpose: Scan open tasks in .claude/tasks/tasks.md for backtick-quoted file path references
(e.g. `app/handlers/foo.py`). Verify each referenced file still exists on disk.
Flags tasks that reference deleted or renamed files — these must be updated or closed.

Command to run (from project root):
  .venv/bin/python scripts/audit_task_drift.py --output .claude/logs/audits/audit_task_drift_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_task_drift_YYYY-MM-DD.md
2. For each drift violation (file referenced but missing):
   - Check git log to see if the file was renamed: git log --diff-filter=R --name-status HEAD~20..HEAD
   - If renamed: update the task's file reference in tasks.md
   - If deleted and task no longer applies: close the task with [x] and a note "File deleted, task superseded"
   - If file not yet created (task is for future work): add [DEFERRED] marker to the task
3. Update the status matrix in .claude/workflows/audit_routine_registry.md
4. Commit with message: "audit: task drift check YYYY-MM-DD [PASS|FAIL N drifts]"

Exit codes: 0 = no drift, 1 = drift violations found, 2 = tasks file not found.
```

---

## Routine 5 — Persona Template Consistency

**Schedule:** On-demand (run manually or before any release)

```
Create an on-demand audit routine for the SPARMVET_VIZ project.

Name: "SPARMVET: Persona Template Consistency"

Purpose: Run PersonaValidator + SidebarValidator in strict mode against all 8 persona
templates in config/ui/templates/. Warnings are treated as errors in strict mode.
Ensures all templates declare every required flag from rules_persona_feature_flags.md
and that cascade enforcement rules (ADR-052, ADR-077) are satisfied.

Command to run (from project root):
  .venv/bin/python scripts/audit_template_flags.py --output .claude/logs/audits/audit_templates_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_templates_YYYY-MM-DD.md
2. For each failing template:
   - Open config/ui/templates/<persona>_template.yaml
   - Fix the flagged issue (missing flag, wrong cascade, forbidden dependency)
   - Re-run validate_persona_config.py --persona <name> --strict to verify the fix
3. Fatal cascade errors (ADR-077: manifest_edit_enabled or blueprint_agent_enabled without
   blueprint_enabled) MUST be fixed before the app can start — treat as P0
4. Update the status matrix in .claude/workflows/audit_routine_registry.md
5. Commit with message: "audit: template consistency YYYY-MM-DD [PASS|FAIL N]"

Exit codes: 0 = all templates pass strict validation, 1 = one or more failures.
```

---

## Routine 6 — Phase Ordering Audit

**Schedule:** Thursdays at 21:00

```
Create a weekly audit routine for the SPARMVET_VIZ project that runs every Thursday at 21:00.

Name: "SPARMVET: Phase Ordering Audit"

Purpose: Verify that non-completed Phase N headers in implementation_plan_master.md appear
in ascending numeric order within each h2 section. Completed (archived) phases are excluded.
Catches cases where a new phase block is inserted at the wrong position in the file
(like Phase 23 being found out of order, which was caught in the P0 audit 2026-05-09).

Command to run (from project root):
  .venv/bin/python scripts/audit_phase_order.py --output .claude/logs/audits/audit_phase_order_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_phase_order_YYYY-MM-DD.md
2. For each OUT_OF_ORDER violation:
   - Open .claude/plans/implementation_plan_master.md
   - Locate the phase block (use the line number from the report)
   - Cut the entire phase block and paste it into its correct chronological position
   - The sequence must flow N-1 → N → N+1 within the section
3. For DUPLICATE violations: two active phases share the same number — one must be renamed
   or merged; discuss with user before changing
4. Update the status matrix in .claude/workflows/audit_routine_registry.md
5. Commit with message: "audit: phase ordering YYYY-MM-DD [PASS|FAIL N]"

Exit codes: 0 = in order, 1 = ordering violations found, 2 = plan file not found.
```

---

## Routine 7 — Changelog Completeness Audit

**Schedule:** Thursdays at 21:00

```
Create a weekly audit routine for the SPARMVET_VIZ project that runs every Thursday at 21:00.

Name: "SPARMVET: Changelog Completeness"

Purpose: Cross-check implementation_plan_master.md against .claude/knowledge/changelog.md.
Every phase header marked as COMPLETED/DONE/✅ in the plan must have a corresponding entry
in the changelog. Missing entries indicate undocumented breaking changes or renames that
may cause future debugging confusion.

Command to run (from project root):
  .venv/bin/python scripts/audit_changelog_sync.py --output .claude/logs/audits/audit_changelog_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_changelog_YYYY-MM-DD.md
2. For each completed phase WITHOUT a changelog entry:
   - Check git log for commits in that phase: git log --oneline --grep="Phase N"
   - Append a minimal entry to .claude/knowledge/changelog.md (append-only, never edit existing):
     ## Phase N — [Brief description]
     - [List breaking changes, renames, removed APIs, new required fields]
   - If the phase had no breaking changes, add: "Phase N — No breaking changes or renames."
3. Update the status matrix in .claude/workflows/audit_routine_registry.md
4. Commit with message: "audit: changelog sync YYYY-MM-DD [PASS|FAIL N missing]"

Exit codes: 0 = all covered, 1 = missing entries found, 2 = plan file not found.
```

---

## Routine 8 — Template Flag Completeness (Strict)

**Schedule:** Thursdays at 21:00

> Note: This is a stricter variant of Routine 5 — Routine 5 is on-demand, this runs weekly
> to catch regressions after template edits.

```
Create a weekly audit routine for the SPARMVET_VIZ project that runs every Thursday at 21:00.

Name: "SPARMVET: Template Flag Completeness (weekly)"

Purpose: Weekly strict validation of all 8 persona templates. Detects missing flags,
incorrect cascade dependencies (ADR-052/ADR-077), and sidebar slot misconfigurations
added since the last manual validation. Complements Routine 5 (on-demand) by providing
a regular automated gate.

Command to run (from project root):
  .venv/bin/python scripts/audit_template_flags.py --output .claude/logs/audits/audit_templates_weekly_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_templates_weekly_YYYY-MM-DD.md
2. Triage failures:
   - FATAL (ADR-077 cascade): must fix before next app start — P0 priority
   - WARNING promoted to error (strict mode): fix before next release
   - All others: create tasks in .claude/tasks/tasks.md [haiku/low]
3. Reference the authoritative flag matrix in rules_persona_feature_flags.md for correct values
4. After fixing: re-run scripts/validate_persona_config.py --all --strict to verify
5. Update the status matrix in .claude/workflows/audit_routine_registry.md
6. Commit with message: "audit: template flag completeness YYYY-MM-DD [PASS|FAIL N]"

Exit codes: 0 = all templates pass strict validation, 1 = one or more failures.
```

---

## Routine 9 — Documentation & README Sync

**Schedule:** On-demand (manual), or monthly if scheduled

> Run after significant refactors, before a release, or after a period of inactivity.
> Can be scheduled monthly via `/schedule` if documentation drift becomes frequent.

```
Create an on-demand audit routine for the SPARMVET_VIZ project.

Name: "SPARMVET: Documentation & README Sync"

Purpose: Verify that human-facing documentation stays in sync with the codebase.
Checks four things:
  1. README coverage: every library in libs/ has a README.md
  2. @deps documents: links in rule/knowledge files point to files that still exist
  3. Backtick file path references in docs/**/*.qmd and lib READMEs exist on disk
  4. Violet Law references — ClassName (filename.py) patterns in .qmd files point to
     .py files that still exist under libs/ or app/

Command to run (from project root):
  .venv/bin/python scripts/audit_docs_sync.py --output .claude/logs/audits/audit_docs_sync_$(date +%Y-%m-%d).md

For a faster run that skips the Violet Law check:
  .venv/bin/python scripts/audit_docs_sync.py --skip-violet --output .claude/logs/audits/audit_docs_sync_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_docs_sync_YYYY-MM-DD.md
2. Triage by violation type:

   README_MISSING:
   - Add README.md to the missing library directory
   - Use Violet Law format for key components: "DataWrangler (data_wrangler.py)"
   - Reference the library's pyproject.toml for the description

   DEPS_DOC_BROKEN:
   - Grep for the old path in rules/ and knowledge/ files
   - Update the `documents:` entry in the @deps block to the new path
   - If the file was deleted, remove the `documents:` reference

   DOC_PATH_BROKEN:
   - Open the .qmd file and find the backtick reference
   - If the file was renamed: update to the new path
   - If the file was deleted: rewrite the paragraph or remove the reference
   - Use git log to trace renames: git log --diff-filter=R --name-status HEAD~30..HEAD

   VIOLET_STALE:
   - Find the ClassName (filename.py) reference in the .qmd file
   - Update filename.py to reflect the current module name
   - If the class was removed: remove the reference from the doc

3. After fixing, re-run to confirm 0 violations
4. Update the status matrix in .claude/workflows/audit_routine_registry.md
5. Commit with message: "docs: sync documentation with current codebase YYYY-MM-DD"

Exit codes: 0 = all checks pass, 1 = violations found, 2 = configuration error.
```

---

## Routine 10 — Library Test Coverage and Testability

**Schedule:** On-demand (manual), or before any release

> Run before a release, after significant library changes, or when onboarding new contributors.
> Can be scheduled weekly if test coverage regressions become frequent.

```
Create an on-demand audit routine for the SPARMVET_VIZ project.

Name: "SPARMVET: Library Test Coverage"

Purpose: For each library in libs/, verify that the test infrastructure is complete
and that all tests pass. Reports three things:
  1. Infrastructure completeness — does the library have unit tests (pytest),
     an integrity suite (*_integrity_suite.py), and debug scripts (debug_*.py)?
  2. pytest results — runs pytest on each library's tests/ directory.
  3. Integrity suite results — runs the *_integrity_suite.py wrapper if present.

A library is FULLY TESTABLE when it has at least one pytest file AND at least
one integrity suite or debug script, and all of them pass.

Libraries missing test infrastructure are flagged as PARTIAL or MISSING — these
require a @dasharch handoff to add the missing layer.

WARNING: This routine runs the full test suite and is intentionally slow (up to
several minutes per library). Do NOT schedule it for frequent runs.

Command to run (from project root):
  .venv/bin/python scripts/audit_library_tests.py --output .claude/logs/audits/audit_library_tests_$(date +%Y-%m-%d).md

For a faster check without running test suites:
  .venv/bin/python scripts/audit_library_tests.py --skip-suites --output .claude/logs/audits/audit_library_tests_$(date +%Y-%m-%d).md

For a single library only:
  .venv/bin/python scripts/audit_library_tests.py --lib transformer --output .claude/logs/audits/audit_library_tests_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_library_tests_YYYY-MM-DD.md
2. For each library with MISSING test infrastructure:
   - File a task in .claude/tasks/tasks.md under "### 🔴 @dasharch Handoffs":
     - [ ] [HANDOFF → @dasharch]: Add test infrastructure for `libs/<name>/` — currently MISSING
       Layers needed: [list from report]
       See rules_verification_testing.md §1 for naming standards.
3. For each library with PARTIAL infrastructure:
   - File a lower-priority task under "### 🟡 Pending Enhancements":
     - [ ] [AUDIT] Complete test infrastructure for `libs/<name>/`: add [missing layers] [sonnet/medium]
4. For each pytest FAIL or suite FAIL:
   - Investigate the failure output in the report
   - Create a fix task: - [ ] [AUDIT] Fix test failure in `libs/<name>/`: [summary] [sonnet/medium]
5. Update the status matrix in .claude/workflows/audit_routine_registry.md —
   set "Last Run" date and "Last Result" (PASS/FAIL + counts)
6. Commit with message: "audit: library test coverage YYYY-MM-DD [PASS|FAIL N]"

Exit codes: 0 = all libraries pass with full infrastructure, 1 = failures or missing infra found, 2 = script error.
```

---

## Routine 11 — Package Dependency Health

**Schedule:** On-demand (manual), or before a release / after a long period without updates

> Run before a release, after a dependency freeze review, or when planning a batch update.
> Checking weekly adds little value since PyPI updates are slow relative to our release cadence.

```
Create an on-demand audit routine for the SPARMVET_VIZ project.

Name: "SPARMVET: Package Dependency Health"

Purpose: Report the health of all installed dependencies from three angles:
  1. Outdated packages — packages in .venv that have newer versions on PyPI,
     grouped by update type (PATCH / MINOR / MAJOR) and cross-referenced with
     which project library declares them.
  2. Conflict detection — runs `pip check` to find installed packages with
     incompatible dependency requirements (dependency hell detection).
  3. Parity mandate alert — for packages governed by parity mandates (Polars → ADR-035,
     Plotnine → ADR-036), flags when an update contains new API surface that should
     be reflected in the transformer/viz_factory action registries.

Local editable packages (utils, test_lab) are detected and excluded from the
outdated list to avoid false positives.

This audit is informational — it does not modify anything.

Command to run (from project root):
  .venv/bin/python scripts/audit_package_deps.py --output .claude/logs/audits/audit_package_deps_$(date +%Y-%m-%d).md

After running:
1. Read the generated report at .claude/logs/audits/audit_package_deps_YYYY-MM-DD.md
2. CRITICAL — Dependency Conflicts (❌):
   - Run `pip check` interactively to identify the conflicting packages
   - File a P0 blocker task: - [ ] [P0] Resolve pip dependency conflict: [description] [sonnet/high]
   - Do NOT deploy until conflicts are resolved
3. MAJOR updates (🔴):
   - Review the release notes for breaking API changes
   - Test locally: `.venv/bin/pip install '<package>==<latest>'` then run the full test suite
   - File a task if the upgrade is safe: - [ ] [AUDIT] Upgrade <package> MAJOR: <version> → <latest> [sonnet/medium]
4. Parity mandate packages (⚠️ — Polars / Plotnine):
   - Check the changelog for new expressions/geoms/scales added since the current version
   - File a task under "### 🟡 Pending Enhancements":
     - [ ] [PARITY ADR-035] Polars <ver>: audit new expressions against transformer action registry [sonnet/medium]
     - [ ] [PARITY ADR-036] Plotnine <ver>: audit new geoms/scales/themes against viz_factory registry [sonnet/medium]
5. MINOR / PATCH updates (🟡/🟢):
   - PATCH: low risk, batch upgrade recommended. Run `.venv/bin/pip install --upgrade <p1> <p2> ...`
     then verify: `python -c 'from app.src.main import app; print("import OK")'`
   - MINOR: review for new features, test individually before upgrading
6. Update the status matrix in .claude/workflows/audit_routine_registry.md —
   set "Last Run" date and "Last Result" (PASS/WARN + counts)
7. Commit with message: "audit: package dependency health YYYY-MM-DD [PASS|WARN N outdated|CONFLICT]"

Exit codes: 0 = no conflicts and no MAJOR updates, 1 = conflicts or MAJOR updates found, 2 = script error.
```

---

## Quick test commands (VS Code terminal)

Before scheduling a routine, verify the script works locally:

```bash
# Run all audits and write reports to the log directory
DATE=$(date +%Y-%m-%d)
.venv/bin/python scripts/audit_cross_lib.py           --output .claude/logs/audits/audit_cross_lib_${DATE}.md
.venv/bin/python scripts/audit_deps_verify.py         --output .claude/logs/audits/audit_deps_${DATE}.md
.venv/bin/python scripts/audit_manifest_integrity.py  --output .claude/logs/audits/audit_manifest_${DATE}.md
.venv/bin/python scripts/audit_task_drift.py          --output .claude/logs/audits/audit_task_drift_${DATE}.md
.venv/bin/python scripts/audit_template_flags.py      --output .claude/logs/audits/audit_templates_${DATE}.md
.venv/bin/python scripts/audit_phase_order.py         --output .claude/logs/audits/audit_phase_order_${DATE}.md
.venv/bin/python scripts/audit_changelog_sync.py      --output .claude/logs/audits/audit_changelog_${DATE}.md
.venv/bin/python scripts/audit_docs_sync.py           --output .claude/logs/audits/audit_docs_sync_${DATE}.md

# On-demand only (slow — runs full test suites)
.venv/bin/python scripts/audit_library_tests.py       --output .claude/logs/audits/audit_library_tests_${DATE}.md
.venv/bin/python scripts/audit_package_deps.py        --output .claude/logs/audits/audit_package_deps_${DATE}.md
```
