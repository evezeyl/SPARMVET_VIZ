# Audit Routine Registry

**Authority:** Operational workflow for automated hygiene checks across the SPARMVET_VIZ repository.

**Purpose:** Define, schedule, and track recurring audit routines that verify code health, ADR compliance, manifest integrity, and documentation drift without manual intervention.

**Last Updated:** 2026-05-09  
**Execution Guide:** `.claude/workflows/schedule_commands.md` — how to run audits locally (session-end, cron, single-script, on-demand). Read that file before setting up any new routine.

**Execution model:** All audit scripts run locally via `.venv/bin/python`. They need the local virtual environment, local data files, and see uncommitted work. Cloud `/schedule` routines are not suitable for most of these scripts. See `schedule_commands.md §Part 1` for the full local execution guide.

---

## 1. Status Matrix — All Audit Routines

| Routine | Frequency | Schedule | Status | Last Run | Next Run | Routine ID | Owner |
|---------|-----------|----------|--------|----------|----------|---|---|
| @deps block verification | Weekly | Sundays 23:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-11 | — | Local (systemd) |
| ADR-011 cross-lib violation scan | Weekly | Sundays 23:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-11 | — | Local (systemd) |
| Manifest structure integrity | Weekly | Wednesdays 22:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-14 | — | Local (systemd) |
| Task-to-code drift check | Weekly | Fridays 20:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-16 | — | Local (systemd) |
| Persona template consistency | On-demand | Manual trigger | `[x] Active` | 2026-05-09 ✅ | — | — | Local (manual) |
| Phase ordering audit | Weekly | Thursdays 21:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-15 | — | Local (systemd) |
| Changelog completeness audit | Weekly | Thursdays 21:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-15 | — | Local (systemd) |
| Template flag completeness | Weekly | Thursdays 21:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-15 | — | Local (systemd) |
| CSS design token compliance | Weekly | Thursdays 21:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-15 | — | Local (systemd) |
| Hardcoded config/path violations | Weekly | Thursdays 21:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-15 | — | Local (systemd) |
| Documentation & README sync | On-demand | Manual trigger (or monthly) | `[ ] Planned` | — | — | — | Local (manual) |
| Library test coverage | On-demand | Manual trigger (or pre-release) | `[ ] Planned` | — | — | — | Local (manual) |
| Package dependency health | On-demand | Manual trigger (or monthly) | `[ ] Planned` | — | — | — | Local (manual) |
| Parity mandate coverage | On-demand | Manual trigger (or after lib update) | `[ ] Planned` | — | — | — | Local (manual) |
| Manifest coherence | Weekly | Wednesdays 22:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-14 | — | Local (systemd) |
| Palette registry validity | Weekly | Thursdays 21:00 | `[x] Active` | 2026-05-09 ✅ | 2026-05-15 | — | Local (systemd) |

**Status codes:**
- `[ ] Planned` — Routine designed but not yet created in [claude.ai/code/routines](https://claude.ai/code/routines)
- `[x] Active` — Routine is created and running on schedule (or available for manual execution)
- `[!] Paused` — Routine is paused in the web UI (will not run until resumed)
- `[x] Complete (legacy)` — Routine ran once for a specific audit goal; not recurring

**Update protocol:** After each run completes, review the routine's run session and update this matrix with:
- Actual run timestamp (from session start time)
- Next scheduled execution date
- Result summary (PASS / FAIL / N violations) as a brief comment

---

## 2. How to Add a New Audit Routine

### Step 1: Define the Audit Logic

Write either a standalone script or a grep/find command. Examples:

**Option A — Standalone script** (`scripts/audit_*.py`):
```python
#!/usr/bin/env python3
"""Audit routine: [short description]

Run via:
  .venv/bin/python scripts/audit_ROUTINE_NAME.py --output tmp/audit_ROUTINE_NAME_2026-MM-DD.md
"""
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

def main(output_path):
    report = []
    report.append(f"# Audit: [Name]\n")
    report.append(f"Generated: {datetime.now().isoformat()}\n\n")
    
    # Your audit logic here
    # ...
    
    with open(output_path, "w") as f:
        f.write("\n".join(report))
    print(f"✅ Audit complete. Report: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()
    main(args.output)
```

**Option B — Grep/find command** (for simple checks):
```bash
# Find all files missing @deps blocks
find app/ libs/ -name "*.py" -type f ! -path "*/test*" | xargs grep -L "@deps" | head -20
```

### Step 2: Register in the Status Matrix

Add a row to the table at the top:
- **Routine:** short name (snake_case)
- **Frequency:** "Weekly" / "Daily" / "On-demand"
- **Schedule:** time (e.g., "Sundays 23:00") or "Manual trigger"
- **Status:** `[ ] Planned`
- **Last Run:** `—` (empty until first execution)
- **Routine ID:** `—` (filled in after routine is created in Step 3)

### Step 3: Create the Routine (Schedule It)

Create the routine at [claude.ai/code/routines](https://claude.ai/code/routines):

**Web UI steps:**
1. Click **New routine**
2. **Name:** `[Audit Name]` (e.g., "@deps block verification")
3. **Prompt:** Use the routine prompt template from Section 5 above
4. **Repositories:** `SPARMVET_VIZ` (main branch)
5. **Environment:** **Default**
6. **Trigger → Schedule:** Pick frequency (Weekly / Daily / etc.) and time
   - For **Sundays 23:00**, select "Weekly" and set the time
7. **Connectors:** Remove any not needed
8. Click **Create**

**Or use CLI:**
```bash
/schedule weekly on Sundays at 11pm, run [Audit Name] audit
```

After creation, the routine ID (looks like `routine_01ABCDEFGHJKLMNOP...`) appears on the routine detail page. Record it in the Status matrix.

**For on-demand routines:**

Don't create a scheduled routine in the web UI. Instead, document the manual command in the routine definition below, and users run it directly.

### Step 4: Define the Routine (Add to Section 3 Below)

Create a subsection for your routine:

```markdown
### [N]. [Routine Name]

- **Purpose:** [What does this check for?]
- **Frequency:** [Daily / Weekly / On-demand]
- **Schedule:** [time/frequency (e.g. "Sundays 23:00") or "Manual trigger"]
- **Command:** [exact CLI command or script path]
- **Output:** [where results are written; e.g., `.claude/logs/audits/audit_name_YYYY-MM-DD.md`]
- **Violations checked:** [list of specific things that trigger a FAIL]
- **Status:** `[ ] Planned` → `[x] Active` (after first successful run)
- **Owner:** [Agent (scheduled) or Manual (CLI)]
```

### Step 5: Test It Manually First

Before scheduling, run the routine once locally:

```bash
.venv/bin/python scripts/audit_ROUTINE_NAME.py --output tmp/audit_test.md
cat tmp/audit_test.md
```

Verify:
- No errors or crashes
- Output file is readable and useful
- Report format is clear (markdown, JSON, or plain text — your choice)

### Step 6: Activate

Once manual test passes:
1. Update Status matrix: `[ ] Planned` → `[x] Active`
2. If scheduling (Step 3), note the Routine ID from the routine detail page
3. Set "Next Run" date to the next scheduled execution
4. Commit both the script and the registry update

---

## 3. Pilot Audit Routine Definitions

### 1. @deps Block Verification

- **Purpose:** Verify that `@deps` annotations are present on all load-bearing files and reflect current dependencies accurately.
- **Frequency:** Weekly
- **Schedule:** Sundays 23:00 local time (cron: `0 23 * * 0`)
- **Command:** `.venv/bin/python scripts/audit_deps_verify.py --output tmp/audit_deps_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_deps_YYYY-MM-DD.md`
- **Violations checked:**
  - Files in `app/`, `libs/*/src/*/` without `@deps` block (non-test files)
  - `@deps` blocks with stale `consumes:` / `provides:` entries (detectable via grep against actual imports)
  - `@deps` blocks missing `@end_deps` terminator (malformed)
- **Owner:** Agent (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS, 27 files verified)
- **Next Run:** 2026-05-11

**Implementation notes:**
- Read `build_dep_graph.py` output from last run (or regenerate)
- Compare file mtimes against graph.json mtime to detect drift
- Flag files modified since last graph run that should have updated @deps

---

### 2. ADR-011 Cross-Lib Violation Scan

- **Purpose:** Detect peer-to-peer imports between domain libraries (transformer ↔ ingestion, blueprint_arch ↔ utils, etc.). These violate the Two-Tier Dependency Model (ADR-011, ADR-016).
- **Frequency:** Weekly
- **Schedule:** Sundays 23:00 local time (same as routine 1)
- **Command:** `.venv/bin/python scripts/audit_cross_lib.py --output tmp/audit_cross_lib_$(date +%Y-%m-%d).json`
- **Output:** `.claude/logs/audits/audit_cross_lib_YYYY-MM-DD.json` (machine-readable) + `.claude/logs/audits/audit_cross_lib_YYYY-MM-DD.md` (human-readable summary)
- **Violations checked:**
  - Any `from libs/X/` import inside `libs/Y/` where X and Y are both domain libraries (not utils)
  - Exception: `from libs/utils/` is always allowed (Tier 1 base layer)
  - Imports inside `app/` are allowed (orchestration layer)
  - Test files are scanned (test interdependencies matter for CI)
- **Owner:** Agent (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ⚠️ KNOWN DEBT ONLY, tests/assets exclusion + schema_registry injection pattern fixed)
- **Next Run:** 2026-05-11

**Expected output (JSON):**
```json
{
  "generated": "2026-05-12T23:00:00Z",
  "violations": [
    {
      "file": "libs/transformer/src/transformer/data_assembler.py",
      "line": 42,
      "import": "from libs.ingestion.src.ingestion.ingestor import Ingestor",
      "from_lib": "transformer",
      "to_lib": "ingestion",
      "severity": "BLOCKER"
    }
  ],
  "summary": "0 violations found. ✅ PASS"
}
```

---

### 3. Manifest Structure Integrity Check

- **Purpose:** Run all manifests in `config/manifests/pipelines/` through the assembler + gallery validator to detect structural errors before they surface at runtime.
- **Frequency:** Weekly
- **Schedule:** Wednesdays 22:00 local time (cron: `0 22 * * 3`)
- **Command:** `.venv/bin/python scripts/audit_manifest_integrity.py --output tmp/audit_manifests_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_manifests_YYYY-MM-DD.md`
- **Violations checked:**
  - Manifest file format (valid YAML)
  - Missing required keys (`input_fields`, `wrangling`, `output_fields`)
  - Broken `!include` references (file not found)
  - Undefined actions in wrangling steps (not in `@register_action` registry)
  - Undefined plot components (not in `@register_plot_component` registry)
  - Join key type mismatches (assembly `action: join` between mismatched column types)
  - `final_contract` whitelist mismatch (column declared but not produced)
- **Owner:** Agent (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS, 6/6 manifests)
- **Next Run:** 2026-05-14

**Implementation notes:**
- Call `debug_assembler.py` on each manifest
- Call `debug_gallery.py` on each manifest
- Collect errors into a summary report

---

### 4. Task-to-Code Drift Check

- **Purpose:** Verify that tasks referenced in `.claude/tasks/tasks.md` still have corresponding code/files. Flag orphaned task references (code removed but task not marked `[x] DONE`).
- **Frequency:** Weekly
- **Schedule:** Fridays 20:00 local time (cron: `0 20 * * 5`)
- **Command:** `.venv/bin/python scripts/audit_task_drift.py --output tmp/audit_tasks_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_tasks_YYYY-MM-DD.md`
- **Violations checked:**
  - Task references a specific file that no longer exists
  - Task references a function `foo()` that has been renamed or removed
  - Task description mentions "in file X line 42" but file/line has changed
  - Completed tasks `[x]` that have newer subsequent task with same/overlapping scope (possible duplicate)
- **Owner:** Agent (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS, 5 stale refs resolved)
- **Next Run:** 2026-05-16

---

### 5. Persona Template Consistency

- **Purpose:** Verify all 8 persona templates (`config/ui/templates/*_template.yaml`) have the same structure, matching the authoritative flag matrix in `rules_persona_feature_flags.md`.
- **Frequency:** On-demand (or can be scheduled daily)
- **Schedule:** Manual trigger via CLI
- **Command:** `.venv/bin/python scripts/validate_persona_config.py --all`
- **Output:** stdout + stderr (errors only); can redirect to file
- **Violations checked:**
  - Missing flags (template missing a flag that the matrix declares)
  - Stale flags (template has a flag that no longer exists)
  - Incorrect flag values (flag value doesn't match the matrix for that persona)
  - Cascade violations (soft: warning; fatal: error blocking startup)
  - Sidebar config mismatches (missing workspaces, invalid panel types)
- **Owner:** Manual (CLI) — but can be wrapped by scheduled agent
- **Status:** `[x] Active`
- **Last Run:** 2026-05-09 (verified in session)
- **Next Run:** On-demand or daily if scheduled

---

### 6. Phase Ordering Audit

- **Purpose:** Verify that `implementation_plan_master.md` phase blocks are in ascending chronological order (Phase 23 → Phase 24 → ... → Phase 32). Detects phases that have been inserted out of order during edits.
- **Frequency:** Weekly
- **Schedule:** Thursdays 21:00 local time (cron: `0 21 * * 4`)
- **Command:** `.venv/bin/python scripts/audit_phase_order.py --output tmp/audit_phases_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_phases_YYYY-MM-DD.md`
- **Violations checked:**
  - Phase numbers not in ascending order (e.g., Phase 24 appears before Phase 23)
  - Phase headers malformed or missing
  - Duplicate phase numbers
  - Phase numbers outside expected range [23–32]
- **Owner:** Cloud (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS, 19 phases in order)
- **Next Run:** 2026-05-15

**Implementation notes:**
- Parse `implementation_plan_master.md` to extract all `## Phase [N]` headers
- Verify sequence is strictly ascending
- Report any out-of-order or duplicate entries with line numbers

---

### 7. Changelog Completeness Audit

- **Purpose:** Verify that `.claude/knowledge/changelog.md` contains entries for all phases declared in `implementation_plan_master.md`. Detects documentation drift when phases are added but changelog is not updated.
- **Frequency:** Weekly
- **Schedule:** Thursdays 21:00 local time (cron: `0 21 * * 4`)
- **Command:** `.venv/bin/python scripts/audit_changelog_sync.py --output tmp/audit_changelog_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_changelog_YYYY-MM-DD.md`
- **Violations checked:**
  - Phases in implementation_plan_master.md missing from changelog.md
  - Changelog entries that reference non-existent phases
  - Missing section headers (e.g., `## [Phase N]` or `## [YYYY-MM-DD]`)
  - Stale entries (phases marked as "in progress" but no longer in active plan)
- **Owner:** Cloud (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS after range-delegation fix in script)
- **Next Run:** 2026-05-15

**Implementation notes:**
- Extract phase numbers from both files
- Compute symmetric difference (missing in one or the other)
- Report by phase name, line number, and recommended fix

---

### 8. Template Flag Completeness Audit

- **Purpose:** Strict version of Routine 5. Verify all 8 persona templates declare all flags in the authoritative flag matrix (`rules_persona_feature_flags.md`). Detects missing flags before they become deployment issues.
- **Frequency:** Weekly
- **Schedule:** Thursdays 21:00 local time (cron: `0 21 * * 4`)
- **Command:** `.venv/bin/python scripts/audit_template_flags.py --output tmp/audit_template_flags_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_template_flags_YYYY-MM-DD.md`
- **Violations checked:**
  - Template missing a flag that matrix declares (per-persona)
  - Template has a flag not in the matrix (stale or incorrect)
  - Flag value incorrect for that persona (e.g., `true` when matrix expects `false`)
  - Cascade violations (soft: parent false, child true silently suppressed; fatal: parent false, child true not suppressed)
  - Missing `blueprint_agent:` config block when `blueprint_agent_enabled: true`
- **Owner:** Cloud (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS 8/8 after SidebarValidator gate-disabled NOTE removed)
- **Next Run:** 2026-05-15

**Implementation notes:**
- Load the flag matrix from `rules_persona_feature_flags.md`
- For each of 8 templates, verify every flag matches matrix expectations
- Wrap with PersonaValidator to catch cascade violations
- Report as a table: Persona × Flag × Expected × Actual × Status

---

### 9. Documentation & README Sync

- **Purpose:** Verify that human-facing documentation stays in sync with the codebase. Checks four things: (1) every library in `libs/` has a `README.md`; (2) `@deps documents:` links in rule/knowledge files point to files that exist; (3) backtick-quoted file paths in `docs/**/*.qmd` and library READMEs exist on disk; (4) Violet Law `ClassName (filename.py)` references in `.qmd` files point to `.py` files that exist under `libs/` or `app/`.
- **Frequency:** On-demand — run after significant refactors, before releases, or after long periods of inactivity.
- **Schedule:** Manual trigger. Can optionally be scheduled monthly.
- **Command:** `.venv/bin/python scripts/audit_docs_sync.py --output .claude/logs/audits/audit_docs_sync_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_docs_sync_YYYY-MM-DD.md`
- **Violations checked:**
  - `README_MISSING` — `libs/<name>/` has no `README.md`
  - `DEPS_DOC_BROKEN` — `documents:` entry in a `@deps` block references a non-existent file
  - `DOC_PATH_BROKEN` — backtick file path in a `.qmd` or `README.md` not found on disk
  - `VIOLET_STALE` — Violet Law reference `ClassName (filename.py)` where `filename.py` does not exist under `libs/` or `app/`
- **Owner:** Manual (CLI) — escalate to Cloud routine if docs diverge frequently
- **Status:** `[ ] Planned`
- **Flags:** `--skip-violet` omits the Violet Law check (faster for large doc trees)

---

### 10. Library Test Coverage

- **Purpose:** For each library in `libs/`, verify the test infrastructure is complete (pytest files, integrity suite, debug scripts) and run the full suite. Reports per-library testability level: FULL (all layers present and passing), PARTIAL (missing one layer), or MISSING (no tests at all). MISSING libraries must receive a `@dasharch` handoff to add the missing test layer before they can be considered production-ready.
- **Frequency:** On-demand — before releases, after adding a new library, or after significant refactors.
- **Command:** `.venv/bin/python scripts/audit_library_tests.py --output .claude/logs/audits/audit_library_tests_$(date +%Y-%m-%d).md`
- **Fast variants:**
  - `--skip-suites` — run pytest only (faster; skips integrity suites)
  - `--skip-pytest` — infrastructure check only, no test execution (fastest)
  - `--lib transformer` — single library only
- **Output:** `.claude/logs/audits/audit_library_tests_YYYY-MM-DD.md`
- **Violations checked:**
  - Library missing `tests/` directory or any test files (MISSING)
  - Library has pytest but no integrity suite or debug scripts (PARTIAL)
  - pytest exits non-zero (test failures)
  - Integrity suite exits non-zero (pipeline failures)
- **Owner:** Manual (CLI)
- **Status:** `[ ] Planned`

---

### 11. Package Dependency Health

- **Purpose:** Report the health of all installed packages: outdated packages (grouped MAJOR/MINOR/PATCH), dependency conflicts (`pip check`), and parity mandate alerts (Polars → ADR-035, Plotnine → ADR-036). Filters out local editable packages that would otherwise appear as false positives. Provides an upgrade protocol tailored to each update category.
- **Frequency:** On-demand — monthly, or when considering a dependency freeze review.
- **Command:** `.venv/bin/python scripts/audit_package_deps.py --output .claude/logs/audits/audit_package_deps_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_package_deps_YYYY-MM-DD.md`
- **Violations checked:**
  - `pip check` reports incompatible requirements → CONFLICT (exit 1)
  - MAJOR version updates available → flagged for review (exit 1)
  - Parity mandate packages (polars, plotnine) have updates → action required note
  - MINOR / PATCH updates → informational (exit 0)
- **Owner:** Manual (CLI)
- **Status:** `[ ] Planned`

---

### 12. Parity Mandate Coverage

- **Purpose:** Verify that the `viz_factory` and `transformer` libraries maintain 1:1 functional parity with their upstream dependencies (ADR-035: Polars API parity; ADR-036: Plotnine/ggplot2 parity). Reports new upstream symbols that have no registered wrapper, and stale registrations for symbols that no longer exist upstream. Uses `audit_exclusions.yaml` to filter known false positives (custom components, accepted tech debt).
- **Frequency:** On-demand — run after any Polars or Plotnine library update, or before releases.
- **Schedule:** Manual trigger (or triggered by `audit_package_deps` MAJOR/parity alert)
- **Command:** `.venv/bin/python scripts/audit_parity_coverage.py --output .claude/logs/audits/audit_parity_coverage_$(date +%Y-%m-%d).md`
- **Fast variants:**
  - `--skip-polars` — check plotnine only
  - `--skip-plotnine` — check polars only
- **Output:** `.claude/logs/audits/audit_parity_coverage_YYYY-MM-DD.md`
- **Violations checked:**
  - `NEW` — upstream symbol with no registered wrapper and not in exclusions → PARITY gap
  - `STALE (unresolved)` — registered wrapper for symbol that no longer exists upstream and not in exclusions → exit 1
  - `STALE (accepted)` — stale wrapper acknowledged in `audit_exclusions.yaml` → informational only
  - `CUSTOM` — registration flagged as intentional SPARMVET extension (in exclusions) → informational
- **Exclusions:** `.claude/workflows/audit_exclusions.yaml` (key: `parity_coverage`)
- **Owner:** Manual (CLI)
- **Status:** `[ ] Planned`

---

### 13. Manifest Coherence

- **Purpose:** Static validation of all manifests in `config/manifests/pipelines/` without running the assembler. Checks four things: (1) TSV source column headers match `input_fields` slugs; (2) all wrangling `action:` names are registered; (3) all `layers: name:` values in plot specs are registered; (4) join `'on':` keys are valid (catches the YAML boolean trap: bare `on:` key). Uses `audit_exclusions.yaml` for known false positives (e.g. assembly-derived join keys not in `input_fields`).
- **Frequency:** Weekly (Wednesdays 22:00) — same slot as Routine 3 (Manifest Structure Integrity).
- **Schedule:** Wednesdays 22:00 local time (cron: `0 22 * * 3`)
- **Command:** `.venv/bin/python scripts/audit_manifest_coherence.py --output .claude/logs/audits/audit_manifest_coherence_$(date +%Y-%m-%d).md`
- **Fast variants:**
  - `--skip-tsv` — skip TSV column vs input_fields check (faster if no source data changes)
  - `--skip-join` — skip join key validation
  - `--manifest config/manifests/pipelines/foo.yaml` — single manifest only
- **Output:** `.claude/logs/audits/audit_manifest_coherence_YYYY-MM-DD.md`
- **Violations checked:**
  - `FIELD_MISSING` — `input_fields` slug not found in source TSV header
  - `FIELD_EXTRA` — TSV column has no corresponding `input_fields` declaration
  - `ACTION_UNKNOWN` — `action:` name not in `@register_action` registry
  - `COMPONENT_UNKNOWN` — `layers: name:` not in `@register_plot_component` registry
  - `JOIN_BARE_ON` — join step uses bare `on:` (YAML boolean trap) instead of quoted `'on':`
  - `JOIN_KEY_UNDECLARED` — join key not declared in any schema's `input_fields` (unless in exclusions)
- **Exclusions:** `.claude/workflows/audit_exclusions.yaml` (key: `manifest_coherence`)
- **Owner:** Cloud (scheduled)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS, false positive in old report; script already correct)

---

### Routine 14: CSS Design Token Compliance

- **Script:** `scripts/audit_css_style.py`
- **Schedule:** Thursdays 21:00 (with existing Thursday group)
- **Command:** `.venv/bin/python scripts/audit_css_style.py --output .claude/logs/audits/audit_css_style_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_css_style_YYYY-MM-DD.md`
- **Purpose:** Verify that `config/ui/theme.css` uses only colors, font-sizes, and border-radius values defined in the SPARMVET design system. Catches off-palette hex values, out-of-scale font sizes, and forbidden Bootstrap defaults introduced by agents who did not read the style spec before writing CSS.
- **Rule source:** `.claude/rules/rules_css_style_spec.md` | ADR-055
- **Checks:**
  - Any hex color not in `ALLOWED_HEX` or `KNOWN_DEBT_HEX` → BLOCKER
  - Explicitly forbidden Bootstrap defaults (`#0d6efd`, `#198754`, etc.) → BLOCKER (highest priority)
  - `font-size` values outside the approved typography scale → BLOCKER
  - `0.9rem` → BLOCKER (specifically excluded from scale, common agent error)
- **Known debt:** `.spv-badge-propagation` `#cfe2ff`/`#0a3678` — tracked as CSS-BADGE-PROPAG-1 in tasks.md
- **Owner:** Local (cron/manual)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS)

---

### Routine 15: Hardcoded Configuration & Path Violations

- **Script:** `scripts/audit_hardcoded_config.py`
- **Schedule:** Thursdays 21:00 (with existing Thursday group)
- **Command:** `.venv/bin/python scripts/audit_hardcoded_config.py --output .claude/logs/audits/audit_hardcoded_config_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_hardcoded_config_YYYY-MM-DD.md`
- **Purpose:** Detect hardcoded deployment-specific values in `app/` and `libs/` Python source that would break the app in Galaxy, IRIDA, or other deployment environments. Five violation categories.
- **Rule source:** ADR-048 (deployment profile), ADR-031 (bootloader), ADR-053 (no persona name checks)
- **Checks:**
  1. **Absolute path strings** — `/home/`, `/etc/`, `/usr/`, `/var/`, `/mnt/`, `/opt/`, `/data/`, `/srv/`, `/galaxy/` literals in non-connector Python
  2. **Direct location dict reads** — `profile["locations"]`, `locations["raw_data"]`, `profile.get("locations")` bypassing bootloader
  3. **Persona name comparisons** — `persona == "..."`, `persona in (...)`, `persona in [...]` (use `bootloader.is_enabled()` instead)
  4. **Direct env-var reads** — `os.environ.get("SPARMVET_PERSONA/PROFILE")` outside bootloader
  5. **Hardcoded Python interpreter** — `subprocess` calls with `"python3"`, `/usr/bin/python`, `/usr/bin/env python`
- **Scan scope:** `app/`, `libs/` — excludes `tests/`, `tmpAI/`, `tmp/`, `scripts/`, `assets/scripts/`, `config/`
- **Skip files:** `bootloader.py`, `connector.py`, `local_connector.py`, `filesystem.py`, `galaxy.py`, `galaxy_connector.py`, `irida.py`, `base.py` (connector implementations legitimately access raw profile)
- **Owner:** Local (cron/manual)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS)

---

### Routine 16: Palette Registry Validity

- **Script:** `scripts/audit_palette_registry.py`
- **Schedule:** Thursdays 21:00 (with existing Thursday group)
- **Command:** `.venv/bin/python scripts/audit_palette_registry.py --output .claude/logs/audits/audit_palette_$(date +%Y-%m-%d).md`
- **Output:** `.claude/logs/audits/audit_palette_YYYY-MM-DD.md`
- **Purpose:** Verify that `config/palettes.yaml` (if present) is valid YAML and follows the expected format: a top-level `palettes:` key containing named palettes as lists of hex color strings. Catches malformed files that `bootloader.get_palettes()` would silently fall back to built-ins for, giving a confusing "no project palettes" symptom at runtime.
- **Rule source:** `.claude/rules/rules_viz_factory.md §6` | ADR-081
- **Checks:**
  - File absent → INFO (normal; built-ins only)
  - File present but not valid YAML → FAIL with `resolve()` path + exact parse error
  - Top-level `palettes:` key missing or wrong type → FAIL
  - Any palette value not a list → FAIL (TYPE_ERROR)
  - Any palette with zero colors → FAIL (EMPTY_PALETTE)
  - Any color not matching `#rrggbb` or `#rgb` → FAIL (INVALID_HEX)
  - Palette name shadows a built-in (`sparmvet_brand`) → WARNING
- **Owner:** Local (systemd Thursday slot)
- **Status:** `[x] Active` (first run: 2026-05-09 — ✅ PASS, 3 palettes)

---

## 4. How Results Are Stored & Reviewed

### Output directory structure

```
.claude/logs/audits/
├── audit_deps_2026-05-12.md              ← @deps routine output
├── audit_cross_lib_2026-05-12.json       ← ADR-011 routine (machine)
├── audit_cross_lib_2026-05-12.md         ← ADR-011 routine (human)
├── audit_manifests_2026-05-08.md         ← Manifest integrity routine
├── audit_tasks_2026-05-10.md             ← Task drift routine
└── audit_YYYY-MM-DD.md                   ← General session audit (existing pattern)
```

### Reading results

After a routine completes:
1. Agent automatically updates `.claude/workflows/audit_routine_registry.md` (this file):
   - Sets "Last Run" to today's date
   - Sets "Next Run" to the next scheduled execution
   - If violations found, adds a 1-line summary in the Status matrix comment
2. User can review the full report:
   ```bash
   cat .claude/logs/audits/audit_NAME_YYYY-MM-DD.md
   ```
3. If violations, a new task is automatically created in `tasks.md` (or user is notified)

### Failure handling

If a routine fails (script crash, timeout, network issue):
1. Agent catches the error and writes to `.claude/logs/audits/audit_NAME_YYYY-MM-DD_ERROR.md`
2. Status matrix entry is updated: Status `[ ] Planned` or `[x] Active` (unchanged), but "Last Run" is marked with `(ERROR)`
3. On next scheduled run, the routine retries automatically
4. If the same routine fails 3+ times in a row, a blocking task is created in `tasks.md` requiring human investigation

---

## 5. Integration with Claude Code Routines

Routines are cloud-hosted automation managed at **[claude.ai/code/routines](https://claude.ai/code/routines)**. They run on Anthropic's infrastructure, so they keep working when your laptop is closed.

**Documentation:** See [code.claude.com/docs/en/routines](https://code.claude.com/docs/en/routines) for full reference.

### Create a routine (web or CLI)

**From web:**
1. Go to [claude.ai/code/routines](https://claude.ai/code/routines) → **New routine**
2. **Name:** `[Audit Name]` (e.g., "@deps block verification")
3. **Prompt:** Use the template below
4. **Repositories:** Add `SPARMVET_VIZ` (main branch, default)
5. **Environment:** **Default** (or custom if routine needs special network access)
6. **Trigger → Schedule:** Pick frequency (weekly, daily, etc.) and time (e.g., "Sundays 23:00")
7. **Connectors:** Remove any not needed (default includes all yours)
8. Click **Create**

**From CLI:**
```bash
/schedule weekly on Sundays at 11pm, run @deps verification audit
# Claude walks you through the steps conversationally
```

### Routine prompt template

```
Run the [Audit Name] audit check.

Execute from project root:
  .venv/bin/python scripts/audit_ROUTINE_NAME.py --output tmp/audit_ROUTINE_NAME_$(date +%Y-%m-%d).md

After completion:
1. Review the output: tmp/audit_ROUTINE_NAME_YYYY-MM-DD.md
2. If violations found:
   - Create a task in .claude/tasks/tasks.md (one task per violation category)
   - Include a link to this routine's run session
3. Move result to .claude/logs/audits/audit_ROUTINE_NAME_YYYY-MM-DD.md
4. Update .claude/workflows/audit_routine_registry.md:
   - Set Status to [x] Active (if Planned)
   - Update "Last Run" to today's date
   - Update "Next Run" to next scheduled execution
   - If violations > 0, add brief summary in matrix comment
5. Commit changes:
   git add .claude/logs/audits/ .claude/workflows/audit_routine_registry.md .claude/tasks/tasks.md
   git commit -m "chore: audit [name] YYYY-MM-DD — PASS|FAIL (N violations)"
```

### Manage routines

From **[claude.ai/code/routines](https://claude.ai/code/routines)** detail page:
- **Run now** — start a run immediately without waiting for schedule
- **Pause/resume** — disable schedule temporarily
- **Edit** — change prompt, schedule, repositories, connectors, or triggers
- **Delete** — remove routine (existing run sessions remain)
- **View runs** — click any past run to see full transcript, review changes, continue conversation

Each run is a full Claude Code session — you can watch it live, review what changed, open pull requests, or continue the conversation.

### Manual execution anytime

Run commands directly in any Claude Code session (independent of routines):
```bash
# Run routine 5 (on-demand)
.venv/bin/python scripts/validate_persona_config.py --all

# Run routine 1 manually
.venv/bin/python scripts/audit_deps_verify.py --output tmp/audit_deps_manual_$(date +%Y-%m-%d).md
```

### One-off audits

Create a **one-off routine** to run at a specific future time (not recurring):
```bash
/schedule in 2 weeks, run full ADR-011 cross-lib audit and create tasks for violations
```

One-off runs do NOT count against daily routine caps — they consume regular subscription usage only.

---

## 6. Naming Conventions

Follow these patterns for consistency:

| Item | Pattern | Example |
|------|---------|---------|
| Script name | `audit_ROUTINE_NAME.py` | `audit_deps_verify.py`, `audit_cross_lib.py` |
| Output filename | `audit_ROUTINE_NAME_YYYY-MM-DD.{md\|json}` | `audit_deps_2026-05-12.md` |
| Error filename | `audit_ROUTINE_NAME_YYYY-MM-DD_ERROR.md` | `audit_cross_lib_2026-05-12_ERROR.md` |
| Routine ID | `routine_XXXXXXXXXXXXXXXXXXXXXXXX` | `routine_01ABCDEFGHJKLMNOP...` |
| Task created on violations | `[AUDIT-NAME-VIOLATIONS-DATE]` | `[AUDIT-CROSS-LIB-2026-05-12]` |

---

## 7. Decision Table — Which Routine to Add Next

| Need | Routine | Effort | Owner |
|------|---------|--------|-------|
| Ensure @deps are current | @deps verification | Low | Agent (scheduled) |
| Catch cross-lib violations early | ADR-011 scan | Low | Agent (scheduled) |
| Catch manifest errors before runtime | Manifest integrity | Medium | Agent (scheduled) |
| Detect orphaned tasks | Task drift check | Medium | Agent (scheduled) |
| Verify persona consistency | Persona template check | Low | Manual (CLI) or Agent |
| Verify phase order in roadmap | Phase ordering audit | Medium | Agent (scheduled) |
| Verify changelog has all phases | Changelog completeness | Low | Agent (scheduled) |
| Strict persona template validation | Template flag completeness | Medium | Agent (scheduled) |
| —— | —— | —— | —— |
| Check SQL injection / XSS vectors | Security linter (SAST) | High | Not yet planned |
| Verify test coverage > threshold | Coverage report | Medium | Not yet planned |
| Check for hardcoded secrets (env vars) | Secret scanner | Low | Not yet planned |
| Audit file permissions / .gitignore | Permissions audit | Low | Not yet planned |

---

## 8. Session-End Protocol for Routine Changes

If you add or modify a routine during development:

1. **Write the script** (if not just a CLI command) — place in `scripts/audit_*.py`
2. **Test manually** — verify the script runs without error
3. **Update this file** (`.claude/workflows/audit_routine_registry.md`) — add/modify routine definition and status matrix
4. **Create the routine** (if periodic) — go to [claude.ai/code/routines](https://claude.ai/code/routines) and follow the web UI steps or use `/schedule` in CLI
5. **Document it** — update the status matrix with:
   - Routine ID (from the routine detail page)
   - Schedule (e.g., "Sundays 23:00")
   - Owner (Cloud or Manual)
6. **Commit together** — one commit with script + registry update

Example commit message:
```
chore: add audit routine for ADR-011 cross-lib violations

- Add audit_cross_lib.py script with full registry of domain libs
- Register routine in audit_routine_registry.md
- Create routine at claude.ai/code/routines (routine_01ABCD...)
- Schedule: weekly Sundays 23:00
- Output routed to .claude/logs/audits/
```

---

## 9. Glossary & Links

| Term | Definition |
|------|-----------|
| **Routine** | A saved Claude Code configuration (prompt + repos + triggers) that runs autonomously on Anthropic-managed cloud infrastructure. Managed at [claude.ai/code/routines](https://claude.ai/code/routines). |
| **Trigger** | How a routine starts: Schedule (recurring or one-off), API (HTTP POST), or GitHub event. |
| **Routine ID** | Identifier of the routine, visible on its detail page at [claude.ai/code/routines](https://claude.ai/code/routines). |
| **Violation** | A check failure. Examples: missing @deps, cross-lib import, broken manifest. |
| **Run** | A single execution of a routine. Each run is a full Claude Code session with a transcript, visible at [claude.ai/code/routines](https://claude.ai/code/routines). |
| **Run now** | Trigger a routine immediately from its detail page, without waiting for the schedule. |
| **Pause** | Temporarily disable a routine's schedule. The routine keeps its configuration but does not run until resumed. |

**Documentation:** [code.claude.com/docs/en/routines](https://code.claude.com/docs/en/routines) — Full Routines reference (triggers, environments, connectors, usage limits)

**Related files:**
- [workspace_standard.md](./../rules/workspace_standard.md) — Master index & project authority
- [project_conventions.md](./../knowledge/project_conventions.md) — Patterns & terminology
- [rules_verification_testing.md](./../rules/rules_verification_testing.md) — Test naming & @verify protocol
- [.claude/logs/audits/](./../logs/audits/) — Historical audit reports

---

**Status:** 16 routines designed and documented. All 10 weekly routines now `[x] Active` via systemd user timers (installed 2026-05-09). Routines 11–14 (on-demand) remain `[ ] Planned` — run manually via `./scripts/run_audits.sh ondemand`.  
**Last Updated:** 2026-05-09  
**Note:** Systemd timer installation activated Sunday/Wednesday/Thursday/Friday slots on 2026-05-09. Routine 16 (palette registry validity) added to Thursday slot alongside CSS/hardcoded-config/template-flags audits. All session-end quick-run scripts (cross-lib, deps, task-drift, template-flags) passed ✅ on 2026-05-09.
**Next Review:** After first automated run (Sunday 2026-05-11 for cross-lib + deps; Thursday 2026-05-15 for full Thursday group)
