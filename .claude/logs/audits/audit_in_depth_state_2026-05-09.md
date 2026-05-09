Status: PROCESSED 2026-05-09 — pre-protocol session log; findings absorbed into current codebase and tasks.md
# In-Depth Project State Audit — SPARMVET_VIZ

**Date:** 2026-05-09
**Auditor:** @dasharch (read-only)
**Scope:** Whole repository, excluding `tmp/`, `tmpAI/`, and `.gitignore`-listed paths
**Prior session log:** `audit_2026-05-09.md` (Waves 1–9 of design/decision work — separate document)
**Branch:** `dev` (working tree clean, up to date with `origin/dev`)
**Audit method:** 4 parallel exploration agents + targeted manual verification (grep, file inspection, mtime checks)

---

## Executive Summary

SPARMVET_VIZ is in **strong overall health** as a feature-rich Shiny-Polars-Plotnine dashboard with mature manifest tooling and a recently expanded BLUEPRINT IDE design (ADRs-073..076 authored today). The codebase passes 97 unit tests, app imports cleanly, and the Phase 31 sidebar slot registry refactor (ADR-073) is now implemented and validated.

However, the audit surfaces **4 CRITICAL**, **6 HIGH**, **12 MEDIUM**, and **10 LOW** issues that range from explicit ADR violations (Two-Category Law, CSS externalisation) through documentation hygiene (ADR numbering gap, stale handoff/changelog) to incomplete recent decisions (`manifest_edit_enabled` flag still absent from templates, despite ADR-075 having been decided today).

The two most consequential blockers for project success are:
1. **ADR-045 Two-Category Law violations** — 4 modules in `app/modules/` import `shiny`, breaking the headless/reusable-library promise that underpins the deployment-flexibility roadmap (Galaxy / IRIDA / standalone server).
2. **BLUEPRINT IDE Build Mode (ADR-075) is decided but not implemented** — 7 of 9 sub-tasks are open. This is the next major milestone (Phase 32) and currently has no functional UI.

The project does NOT have any data-corruption risks, security regressions, or test-suite breakage. Nothing here is on fire — but several silent inconsistencies between `rules/`, `tasks.md`, and the actual code state will mislead future agents and slow development if not reconciled.

---

## 1. CRITICAL Findings

### 1.1 ADR-045 Two-Category Law Violations — 4 files in `app/modules/`

**Severity:** CRITICAL
**Authority:** [`rules_app_structure.md §1`](.claude/rules/rules_app_structure.md), ADR-045
**Evidence:** `grep "from shiny import" app/modules/*.py`

The Two-Category Law mandates that `app/modules/` files be **headless-safe** (zero Shiny imports). The following 4 files violate this:

| File | Violation | Lines | Why this matters |
|---|---|---|---|
| `app/modules/wrangle_studio.py` | `from shiny import ui, reactive, render` | 11 | Class is the BLUEPRINT IDE driver — heavily reactive |
| `app/modules/gallery_viewer.py` | `from shiny import ui, reactive, render` | 7 | Gallery browser; mixes view + reactive logic |
| `app/modules/test_lab_studio.py` | `from shiny import ui, reactive, render` | 9 | Test Lab UI class; same pattern |
| `app/modules/help_registry.py` | `from shiny import module, ui, render` | 9 | Uses Shiny `module` (a Shiny-specific construct) |

Per ADR-045 §1 these files MUST split into:
- pure-Python view-builder helpers (kept in `app/modules/`), and
- Shiny `define_*_server(...)` registrations (moved to `app/handlers/`).

**Why CRITICAL:** This is the #1 blocker for headless reuse (CLI tools, Galaxy XML wrappers, future API endpoints). It's also the explicitly-tracked task `ADR045-REFACTOR [opus/high]` (open in `tasks.md` line 126).

**Proposed fix:**
- For each of the 4 modules, audit which methods are pure (return `ui.div(...)`/dataframe transforms) vs reactive (`@render.*`, `@reactive.Effect`).
- Pure methods stay; reactive registrations move into a new `app/handlers/<concern>_handlers.py` with an explicit `define_<concern>_server(input, output, session, *, ...)` entry point.
- `wrangle_studio.py` is the largest case — likely worth a dedicated `[opus/high]` session.

---

### 1.2 ADR-076 BLUEPRINT AI Agent Helper — large new feature, all 10 tasks open

**Severity:** CRITICAL (scope risk)
**Authority:** [`architecture_decisions.md` line 2706 — ADR-076](.claude/knowledge/architecture_decisions.md), [`tasks.md` lines 339–349](.claude/tasks/tasks.md)

ADR-076 was authored today (2026-05-09). It introduces:
- A new `AgentAdapter` protocol (4 backend variants — CLI, API, local model, disabled)
- 7 agent tools (`get_available_actions`, `validate_manifest_fragment`, `propose_manifest_diff`, etc.)
- HTML-comment fenced JSON tool-call protocol
- New chat panel sidebar slot
- Subprocess isolation strategy (`flock`-based, dedicated `cwd` per session)
- Session bundle artifacts (`conversation.jsonl`, `report.qmd`, `manifest_sha256.txt`)

All 10 implementation sub-tasks are open: `BP-AGENT-FLAG-1`, `BP-AGENT-1`, `BP-AGENT-PARSER-1`, `BP-AGENT-TOOLS-1`, `BP-AGENT-INSTRUCT-1`, `BP-AGENT-PANEL-1`, `BP-AGENT-UI-1`, `BP-AGENT-CSS-1`, `BP-AGENT-REPORT-1`.

**Why CRITICAL:** This is a substantial feature surface (subprocess management, tool dispatch, JSON parsing, chat UI, persona integration) that was scoped to a single ADR with no decomposed delivery slices. Without breaking it into MVP / v2 / v3 increments, it risks becoming a multi-week sink. The dependency on a working `claude` CLI binary at deployment also creates an air-gap concern that the ADR acknowledges but doesn't fully resolve.

**Proposed fix:**
- Define an MVP-1 scope: `DisabledAdapter` + `ClaudeCliAdapter` only, schema/component listing tools only, no tool-driven `propose_manifest_diff` yet — produce-only "Q&A about the manifest" mode.
- Defer `BP-AGENT-REPORT-1` (session bundle) until MVP-1 is in production for at least one demo cycle.
- Validate the subprocess isolation discipline against the user's local Claude Code session BEFORE writing UI code — a single live test of `cwd={uuid}/` + `flock` will surface blockers cheaper than a full UI build.

---

### 1.3 ADR-075 BLUEPRINT IDE Build Mode — 7 of 9 sub-tasks open; flag absent from all templates

**Severity:** CRITICAL (silent contradiction)
**Authority:** ADR-075, [`rules_persona_feature_flags.md`](.claude/rules/rules_persona_feature_flags.md)
**Evidence:**
- `grep manifest_edit_enabled config/ui/templates/*.yaml` → **0 matches**
- `grep manifest_edit_enabled app/src/bootloader.py app/modules/persona_validator.py` → **0 matches**
- `tasks.md` lines 332–337: `BP-FORMS-1`, `BP-ESCAPE-1`, `BP-UNDO-1`, `BP-HELP-1`, `BP-COLOR-1`, `BP-FLAG-1` are open.
- The "Full Flag Matrix" in `rules_persona_feature_flags.md` lists `manifest_edit_enabled` for every persona — but no template declares it.

**Why CRITICAL:** Documentation says this flag drives the BLUEPRINT YAML escape hatch (read-only vs editable). Code says nothing. Any agent reading the rules and trying to implement gating will conclude the flag exists, write `bootloader.is_enabled("manifest_edit_enabled")`, and silently get `False` for every persona — including `developer`. This is a textbook silent-failure-mode trap.

Two of the 9 sub-tasks (`LINEAGE-NAV-1`, `LINEAGE-EXPORT-1`) ARE complete (commit `9269ebb` and `4acfc59`), and `BP-SCHEMA-1` + verification (`SCHEMA-VERIFY-ACTIONS-1`, `SCHEMA-VERIFY-GEOMS-1`) are also done. So the lineage half of ADR-074/ADR-075 is shipped; the IDE-form half is not.

**Proposed fix:**
- File **BP-FLAG-1 first** (simplest task — 5-line template edits + bootloader cascade rule). This unblocks downstream gating without requiring any UI work.
- Then BP-FORMS-1 + BP-ESCAPE-1 in one session (both touch the same blueprint UI surface).
- BP-UNDO-1 / BP-COLOR-1 can wait until the form renderer is real.

---

### 1.4 ADR Numbering Gap — ADR-072 was never authored

**Severity:** CRITICAL (documentation integrity)
**Evidence:** `grep "ADR-07[0-9]" architecture_decisions.md`

The ADR sequence in `architecture_decisions.md` jumps:
- ADR-070 (Functionality-First Deployment Model, 2026-05-05)
- ADR-071 (Deployment Hardening Standard, 2026-05-05)
- ADR-069 (Complete Export Audit Trail Standard, 2026-05-05) — **inserted out of order**
- ADR-073 (Sidebar Slot Registry, 2026-05-09)

ADR-072 is **completely absent** — no entry, no reference anywhere in `.claude/`. The numbering jump is silent.

Additionally, ADR-069 appears AFTER ADR-070/071 in the file (line 2188 vs lines 2036/2068), indicating ADRs are not maintained in numerical order.

**Why CRITICAL:** This is the canonical decision log. Future agents reading sequentially will assume ADR-072 was withdrawn or skipped intentionally. There's no annotation explaining which.

**Proposed fix:**
- Add an "ADR-072: RESERVED / WITHDRAWN" stub at the appropriate position with a one-line explanation (e.g., "Numbering accidentally skipped; not used"), OR
- Renumber 073..076 down by one. Renumbering is risky because external references (commit messages, task IDs) point to ADR-073 already — the stub option is safer.
- Sort ADRs by number: ADR-069 should be moved before ADR-070.

---

## 2. HIGH Findings

### 2.1 `rules_persona_feature_flags.md` "Known violations" list is OUT OF DATE

**Severity:** HIGH
**Evidence:** Lines 191–199 of `rules_persona_feature_flags.md` list five specific persona-name string-comparison violations:
- `app/src/ui.py:410` — `persona in ("pipeline-static", "pipeline-exploration-simple")`
- `app/handlers/gallery_handlers.py:35` — `_T3_PERSONAS = {...}`
- `app/handlers/export_handlers.py:240` — `persona in (advanced, ...)`
- `app/handlers/home_theater.py:538` — `persona in (advanced, ...)`
- `app/handlers/home_theater.py:1134` — `persona in hidden_personas`

`grep "persona ==\|persona in (" app/handlers/*.py app/src/ui.py app/src/server.py` returns **zero runtime matches**. All occurrences in those files are now docstring or comment references, not control flow.

**Why HIGH:** This means task `25-O` (eliminate persona-name comparisons) is effectively complete in code, but `tasks.md` and `rules_persona_feature_flags.md` still describe it as open tech debt. An agent reading the rules will spend time hunting for violations that don't exist. Conversely, if a violation is reintroduced, the rule provides false confidence ("the audit list says these specific files only").

**Proposed fix:**
- Replace the "Known violations" table with a single line: "Verified clean as of 2026-05-09 — bootloader-resolved flags only. Re-run `grep -E 'persona\s*==\|persona\s+in\s*\(' app/handlers/ app/src/` before each release."
- Mark `25-O` as complete in `tasks.md` (it's not currently — the file still implies pending work for ADR-073/SIDEBAR-REGISTRY-1 to "fix" this).

---

### 2.2 ADR-055 CSS externalisation — 101 inline `style=` attributes in handlers

**Severity:** HIGH
**Evidence:** `grep -c "style=" app/handlers/*.py` → 101 total

| File | Inline styles | Notes |
|---|---|---|
| `filter_and_audit_handlers.py` | 22 | Highest density; filter UI + audit cards |
| `home_theater.py` | 22 | Plot panels + sidebar tweaks |
| `data_import_handlers.py` | 20 | Import controls |
| `audit_stack.py` | 18 | Recipe nodes — likely per-state colour (Violet/Yellow) |
| `session_handlers.py` | 6 | Session cards |
| Others | <5 each | |

ADR-055 mandates: "All UI styling MUST go in `config/ui/theme.css`. Do not add `style=` attributes on individual components unless the value is truly one-off."

`config/ui/theme.css` exists at 38 KB (well-maintained), but handlers still rely heavily on inline styling. Sample lines from `filter_and_audit_handlers.py`: `style="font-size:0.8em;"` (76), `style="font-size:0.75em;"` (87), `style="font-size:0.95em; color:#dc3545; line-height:1;"` (135), `style="flex:1;"` (240).

**Why HIGH:** This isn't a runtime bug, but it (a) violates an explicit ADR, (b) makes per-persona theming impossible without code changes, and (c) duplicates rules that should be class-based. The `bp-agent-*` rules requested in `BP-AGENT-CSS-1` cannot be added cleanly while the existing handlers are still spiking inline rules.

**Proposed fix:**
- Audit all 101 inline styles. Categorise: (a) one-off truly-unique values (keep), (b) repeated patterns (extract to a CSS class — e.g., `.filter-row-trash-icon`).
- Extract patterns first (highest-leverage), one handler at a time, starting with `filter_and_audit_handlers.py` (22 styles, mostly font-sizing patterns).
- This is `[haiku/low]` per-file work — could be a one-session sweep.

---

### 2.3 `handoff_active.md` is 4 days stale and refers to "Monday demo" already past

**Severity:** HIGH
**Evidence:** mtime 2026-05-05 08:51; current date 2026-05-09. File header says "2026-04-30 Session 10".

The handoff document still describes:
- "Monday demo blockers DEMO-1..DEMO-4 all RESOLVED" (the demo was run; this is historical)
- "Phase 22 implemented; 22-J live-UI test §1 PASSED 2026-04-30" (also historical)
- A "Next Steps" priority list dated April 30 that is largely now done or superseded.

The companion handoff segment dated 2026-04-30 Session 11 (in the same file) is similarly stale.

**Why HIGH:** `CLAUDE.md` §7 says: "Before stopping: write current status, modified file paths, and next step to the handoff file. Upon starting: read handoff_active.md to resume context." A new agent reading this file today will think Phase 22 just shipped and Phase 23 is next, missing 9 days of architectural work (Phases 26 CSS, 27 Gallery, 28 Export Redesign, 29 Library Extraction, 31 Sidebar Registry, 32 BLUEPRINT IDE).

**Proposed fix:**
- Replace the body of `handoff_active.md` with a current snapshot:
  - State: ADRs 073/074/075/076 authored 2026-05-09; LINEAGE-NAV-1 + LINEAGE-EXPORT-1 + BP-SCHEMA-1 implemented today; BLUEPRINT IDE form/escape/undo/help/color/flag tasks open.
  - Next step: BP-FLAG-1 first (low cost, unblocks gating), then BP-FORMS-1.
  - Reference today's session audit `audit_2026-05-09.md` for the design decisions narrative.

---

### 2.4 `pyproject.toml` files do not declare `utils` as a dependency

**Severity:** HIGH
**Authority:** [`rules_runtime_environment.md §4`](.claude/rules/rules_runtime_environment.md) — "Any domain library that imports from `libs/utils/` MUST declare it in its own `pyproject.toml` `[project.dependencies]`."
**Evidence:** Sampled three libraries:

| Library | pyproject.toml deps | utils import? | Compliant? |
|---|---|---|---|
| `libs/transformer/` | `polars`, `pyarrow`, `pyyaml` | YES (`utils.errors`, `utils.hashing`) | **NO** |
| `libs/viz_factory/` | `plotnine`, `polars`, `pandas`, `pyyaml` | YES (`utils.errors`) | **NO** |
| `libs/blueprint_arch/` | `pyyaml` | NO | YES |

This is tracked as `PYPROJECT-DEPS-1 [haiku/low]` in `tasks.md` line 290 — open.

**Why HIGH:** The two-tier dependency model (just formalised today, Wave 6 of audit_2026-05-09.md) was the headline architectural clarification of the session. Two days from now, `DEPLOY-CONNECT-1` will run `pip install -r requirements.txt` against a fresh Connect environment — at that point, the Connect bundler must explicitly know that `transformer` depends on `utils`. The current `pyproject.toml` files lie about their dependencies. Connect *might* still work because all libs are in the `requirements.txt` editable list, but this is fragile — if anyone changes the install order, transformer will fail to import `utils.errors` because the install resolver has no signal.

**Proposed fix:**
- For each of the 5 libs that import `utils.*`: add `"utils"` (or path-based pip dep) to `[project.dependencies]`. Verified imports (from §1.2 of `rules_runtime_environment.md`):
  - `libs/transformer/` → utils
  - `libs/blueprint_arch/` → utils (also transformer + viz_factory, the documented exceptions)
  - `libs/viz_factory/` → utils
  - `libs/transformer/data_assembler.py` → utils.hashing
  - `libs/transformer/data_wrangler.py`, `metadata_validator.py` → utils.errors

---

### 2.5 `tree.txt` is 5 days stale; `dependency_index.md` 4 days stale

**Severity:** HIGH (informational drift)
**Evidence:**
- `tree.txt` mtime 2026-05-04 (5 days old)
- `dependency_index.md` mtime 2026-05-05 (4 days old)
- `architecture_decisions.md` mtime 2026-05-09 (today)

ADRs 073/074/075/076 introduced new files (`app/modules/sidebar_registry.py`, `app/modules/sidebar_validator.py`, `scripts/validate_persona_config.py`, plus 8 sidebar YAML files in `config/ui/sidebars/`). None of these are reflected in `tree.txt`.

`dependency_index.md` claims to be auto-generated from `@deps` blocks. The new files were created today and have `@deps` blocks (verified for `sidebar_registry.py`, `sidebar_validator.py`). The dependency graph wasn't rebuilt.

**Authority:** [`workspace_standard.md §5-E`](.claude/rules/workspace_standard.md) — "Run `build_dep_graph.py` as the final step of any session that touched annotated files. An agent that ends a session without completing this protocol is in violation of workspace standards."

**Why HIGH:** Today's session-end mandate (§5-E) was not satisfied. New `@deps` blocks are not in the index; the impact-analysis tool is incorrect.

**Proposed fix:**
- Run `.venv/bin/python assets/scripts/build_dep_graph.py` (single command).
- Regenerate `tree.txt` (gitignored, but should be current — `tree -I '__pycache__|.venv|tmp*|node_modules' > tree.txt` or whatever the project's recipe is).

---

### 2.6 `changelog.md` last updated 2026-05-01

**Severity:** HIGH
**Evidence:** mtime 2026-05-01 21:43

Per `CLAUDE.md` (project conventions §3.4), `changelog.md` is the "Breaking changes and notable renames" log. Phase 28 (Export Redesign + assembly→join Rename) was completed 2026-05-04, Phase 29 (Library Extraction) 2026-05-05, ADR-073/074/075/076 today (2026-05-09) — all major surface changes. None should be silently absent from changelog.

**Why HIGH:** Anyone debugging "where did `assembly_manifests` go?" or "why is `dev_studio` called `test_lab_studio`?" will check `changelog.md` first. It will give them stale answers.

**Proposed fix:** Append entries for Phases 28, 29, 31, 32 (in progress). Roll up ADRs 066, 067, 068, 073, 074, 075, 076 with one-line summaries each.

---

## 3. MEDIUM Findings

### 3.1 `manifest_edit_enabled` flag absent from all templates AND from validators

**Severity:** MEDIUM (covered by 1.3 — listed separately for tracking)
**Evidence:** `grep manifest_edit_enabled config/ui/templates/*.yaml` → 0 matches. Not in `persona_validator._REQUIRED_FLAGS`. Not in `bootloader._load_persona_config()` cascade rules.

The `BP-FLAG-1` task addresses this; tracked. No additional action beyond §1.3 above.

---

### 3.2 `wrangle_studio_enabled` used in templates but not in `_REQUIRED_FLAGS`

**Severity:** MEDIUM
**Evidence:** Found in 7/8 templates (e.g., `developer_template.yaml:13: wrangle_studio_enabled: true`); absent from `pipeline-static_template.yaml`. `app/modules/persona_validator.py` does NOT list it in `_REQUIRED_FLAGS`.

**Why MEDIUM:** A persona could legally omit this flag (validator won't catch it) but it's clearly intended to be required. Inconsistent treatment vs. peer flags.

**Proposed fix:** Add `wrangle_studio_enabled` to `_REQUIRED_FLAGS` in `persona_validator.py`. Audit all 8 templates and ensure each declares it explicitly.

---

### 3.3 Demo personas (`demo-vetinst`, `web-demo`) undocumented in flag matrix

**Severity:** MEDIUM
**Evidence:** `rules_persona_feature_flags.md` line 102: "Six personas exist". Actual templates: 8. The demo personas have all the structure (sidebars, flags, theme_css) but are not in the canonical Full Flag Matrix table.

**Why MEDIUM:** Both personas are functional and validated by `validate_persona_config.py`. But: an architect comparing personas using only the rules will miss the demo set. Future template-modification rules ("update all personas to add flag X") will silently skip demo personas.

**Proposed fix:** Add a section "§Demo personas" to `rules_persona_feature_flags.md` with a small flag-value table for `demo-vetinst` and `web-demo`. Or, integrate into the main matrix as columns 7–8.

---

### 3.4 `Quality_metrics_wrangling.yaml` is a flat empty list (`wrangling: []`)

**Severity:** MEDIUM
**Authority:** [`rules_data_engine.md §3 — Tiered Manifest Mandate`](.claude/rules/rules_data_engine.md), [`rules_persona_bioscientist.md §3-A`](.claude/rules/rules_persona_bioscientist.md)
**File:** `config/manifests/pipelines/1_test_data_ST22_dummy/wrangling/Quality_metrics_wrangling.yaml` (14 bytes)
**Content:** `wrangling: []`

**Why MEDIUM:** This is a legacy flat list — must be `tier1: []` + optional `tier2: []`. The engine should silently treat it as identity (no-op), but the rule says the agent MUST proactively suggest refactoring when encountering legacy flat lists. The file looks abandoned (size suggests it was emptied without restructuring).

**Proposed fix:** Convert to `tier1: []` (identity) or delete the file if no schema needs it. Cross-check `1_test_data_ST22_dummy.yaml` for `Quality_metrics`-related includes.

---

### 3.5 Two top-level manifests don't follow basename mirroring

**Severity:** MEDIUM
**Authority:** [`rules_manifest_structure.md §1`](.claude/rules/rules_manifest_structure.md)
**Evidence:**
- `1_Abromics_general_pipeline.yaml` (119 lines, exceeds the 150-line ceiling rule of thumb but barely) — no paired directory
- `demo_abromics.yaml` (41 lines, under threshold — inline acceptable)

**Why MEDIUM:** `demo_abromics.yaml` is below the 150-line trigger so inline form is technically allowed. `1_Abromics_general_pipeline.yaml` at 119 lines is borderline but has 3+ data sources (need to verify); rule says "any manifest exceeding ~150 lines OR involving more than 3 data sources MUST transition to the Mirrored Directory standard."

**Proposed fix:**
- Re-read `1_Abromics_general_pipeline.yaml`. Count data sources. If >3, restructure into `1_Abromics_general_pipeline/` directory with `!include` blocks.
- For `demo_abromics.yaml`: confirm it's a small demo and leave as-is, OR add a comment at the top noting it's intentional inline form.

---

### 3.6 Phantom file reference: `libs/utils/tests/test_config_loader.py` listed as broken in rules

**Severity:** MEDIUM
**Authority:** [`rules_verification_testing.md §8`](.claude/rules/rules_verification_testing.md)
**Evidence:**
- Rule lists `libs/utils/tests/test_config_loader.py` as a known broken test.
- Actual filesystem: `libs/utils/tests/debug_config_loader.py` (2.7 KB, dated 2026-05-03), `debug_gallery_submission.py` (2.0 KB), and a `placeholder/` subdir.
- No file named `test_config_loader.py` exists.

**Why MEDIUM:** Either the rule references an obsolete name (file was renamed `test_*.py` → `debug_*.py`) or it pointed at a file that was deleted. Either way, the rule is wrong.

**Proposed fix:**
- Update `rules_verification_testing.md §8` "Pre-existing broken libs" to either drop the line or replace it with `debug_config_loader.py` (and confirm if it's still broken — the rule's premise was an ImportError, which may be obsolete).

---

### 3.7 Implementation plan master is not chronologically ordered

**Severity:** MEDIUM
**File:** `.claude/plans/implementation_plan_master.md` (736 lines)
**Evidence:** Phase headings appear in order:
- Line 415: Phase 24 — IMPLEMENTED 2026-05-01
- Line 465: Phase 26 — COMPLETE 2026-05-02
- Line 500: Phase 27 — COMPLETE 2026-05-03
- Line 531: Phase 28 — COMPLETE 2026-05-04
- Line 567: **Phase 31 — PLANNED 2026-05-09** (out of order)
- Line 607: Phase 29 — COMPLETE 2026-05-05
- Line 641: **Phase 25** — COMPLETE 2026-05-01 (way out of order)
- Line 681: Phase 32 — PLANNED 2026-05-09
- Line 728: Phase 23 — ACTIVE 2026-04-23

**Why MEDIUM:** `implementation_plan_master.md` is supposed to be the "high-level roadmap — authoritative phases" (per `CLAUDE.md`). Reading it from top to bottom now gives a confusing zig-zag through time.

**Proposed fix:** Sort phases by number (or by completion-date if that's the intended scheme) once the file is next edited. Alternatively, reorganise into "Completed phases" and "Planned phases" sections with explicit chronological subsections.

---

### 3.8 Plasmid Dynamics lineage actually 95% complete; tasks.md still says open

**Severity:** MEDIUM (status drift)
**Evidence:**
- `tasks.md` lines 61–65: marked open — `Create 2_test_data_ST22_dummy/input_fields/plasmid_data.yaml`, etc.
- Filesystem: `2_test_data_ST22_dummy/input_fields/plasmid_data.yaml` exists (477 bytes), `wrangling/plasmid_data.yaml` exists, `Plasmid_Profile_Joint.yaml` exists, manifest references plasmid plot.

**Why MEDIUM:** Either the user is mid-task and the listed remaining steps are real (tier 2 polish), or the task should be closed. Without running `debug_assembler.py` we can't verify the lineage produces correct output.

**Proposed fix:** Run a verification pass:
```
.venv/bin/python libs/transformer/tests/debug_assembler.py \
  --manifest config/manifests/pipelines/2_test_data_ST22_dummy.yaml \
  --tmp tmpAI/2026-05-09/2_test_data_ST22_dummy/
```
If output is correct, mark the task `[x]` with the date. If it fails, write the actual remaining steps as concrete sub-tasks.

---

### 3.9 `server.py` is 302 lines — over the 250 ADR-051 target

**Severity:** MEDIUM
**Authority:** [`rules_app_structure.md §3`](.claude/rules/rules_app_structure.md) — "Hard limit: server.py MUST NOT grow beyond ~250 lines."

302 / 250 = 21% over. The agent audit confirmed all content is legitimate (imports, init, shared state, calc, delegation), so the over-cap isn't a structural violation — it's a smell that some shared logic could be promoted to a helper module.

**Why MEDIUM:** The rule says "MUST NOT". 302 is outside that bound.

**Proposed fix:** Extract `_safe_input` and `_apply_tier2_transforms` (and similar shared helpers) into `app/modules/orchestrator_helpers.py`. Reduces server.py by ~50 lines.

---

### 3.10 transformer @register_action total = 65, well below the rules' ~175 expectation

**Severity:** MEDIUM
**Authority:** [`rules_data_engine.md §5 — Polars Parity Mandate`](.claude/rules/rules_data_engine.md)
**Evidence:** `grep -rh "@register_action" libs/transformer/src/ | wc -l` → **65** (cleaning: 49, reshaping: 7, relational: 2, persistence: 2, performance: 2, base: 2, plus a duplicate count). The Bio-Scientist persona rule §8 lists ~95 distinct named actions — even that's 30 short.

The cumulative "Action Registry Parity" task (`tasks.md` line 353) calls for 175+ actions for full Polars parity. This is tracked as `[sonnet/high]`.

**Why MEDIUM:** Not a bug, but a substantial scope gap between aspiration and reality. The 65 actions cover the most common bioinformatics workflows, but the BLUEPRINT IDE form generator (BP-FORMS-1) will surface this directly — user will see "65 actions" instead of "175". `BP-AGENT-TOOLS-1` `get_available_actions` will be limited too.

**Proposed fix:**
- Run an inventory: which of the 175+ Polars top-level functions are most-needed for AMR/MLST workflows?
- Prioritise the next ~20 actions (e.g., `with_columns_seq`, `unique_keep_first`, `lazy_groupby_dynamic`, etc.) for a concentrated parity sprint.
- This connects to `ACTION-RENAME-1` — best to do parity expansion AFTER the rename, so renames hit fewer files.

---

### 3.11 `viz_factory` reports 195 components — matches expectation (Plotnine parity)

**Severity:** LOW (positive finding noted for completeness)
**Evidence:** `grep -rh "@register_plot_component" libs/viz_factory/src/ | wc -l` → 195

Plotnine 0.15.3 has roughly 35 geoms + 40 scales + 20 themes + 8 facets + 6 coords + 5 positions + 10+ guides + 30+ stats ≈ 154–180. 195 is over the upper bound, suggesting some compound/duplicated components — but this is healthy. ADR-036 Artist Parity Mandate is satisfied.

---

### 3.12 Gallery: 34 bundles, all 4 mandatory files present, all 6 taxonomy fields verified on sample

**Severity:** LOW (positive finding)

100% file-presence compliance (4 × 34 = 136 files). Spot-check on `bar_simple` shows all 6 taxonomy fields populated with canonical values. `gallery_index.json` mtime within 2 minutes of latest manifest. Excellent shape.

Only caveat: `Taxonomy Data Audit [@user]` task in `tasks.md` line 257 — full re-verification across all 34 bundles is owed.

---

## 4. LOW Findings

### 4.1 No stale Python files in `app/modules/__pycache__` issues — clean

`__pycache__/` directories present in app/, app/handlers/, app/modules/, app/src/, app/tests/ — normal artifacts, gitignored.

### 4.2 `area_simple` gallery example_data.tsv is 7 lines

Not a bug — legitimate minimal example for area-chart demonstration. `wc -l` = 7 (header + 6 rows).

### 4.3 ADR file (3022 lines) is becoming a single-file behemoth

`architecture_decisions.md` is 3022 lines. Not blocking, but searchability degrades. Future option: split by year (`architecture_decisions_2026Q1.md`, etc.) once the file crosses ~5000 lines. Current size is still navigable.

### 4.4 `_book/` directory present in project root

`/_book/` listed in root `ls`. Standard Quarto build artifact, gitignored. Consider whether to delete from working tree (it's stale build output).

### 4.5 `manifest.json` and `tree.txt` both gitignored but tracked-as-stale

Both are listed in `.gitignore`, which is correct for ephemeral artifacts. But both are referenced by docs/agents as authoritative. Consider whether either should be checked in OR explicitly regenerated as a session-end mandate (similar to `build_dep_graph.py`).

### 4.6 `app/handlers/notification_utils.py` is in handlers/ but might be a pure utility

The file has `@deps` (line 1) and is imported by handler modules. If it has no `@render.*`/`@reactive.*` decorators, it would more accurately live in `app/modules/`. Quick check needed.

### 4.7 `app/handlers/single_graph_export_handlers.py` likely deprecated by 3-way scope toggle

`tasks.md` line 17–18: "Removed Single Graph Export accordion panel from sidebar (superseded by scope toggle)" 2026-05-04. But `single_graph_export_handlers.py` still exists (per `ls`). Possibly dead code — verify whether anything still imports it.

### 4.8 `app/tests/test_skeleton_flow.py`, `test_session_manager.py`, `test_persona_validator.py` not in baseline test commands

Per `rules_ui_dashboard.md §6`: baseline `pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py`. Three other app tests exist but aren't run in the documented baseline. Either they run separately, or they're optional/known-broken.

### 4.9 `_HELP/` (vault path) is referenced by user config — but user is in SPARMVET_VIZ subdir

The CeVe agent definition (vault-level CLAUDE.md) references `_HELP/`, `_bin/`, etc. These don't apply inside SPARMVET_VIZ, but the inheriting CLAUDE.md (project-level) is correctly the active one. Confirmed no cross-contamination — just noting for completeness.

### 4.10 `.claude/logs/sessions/` contains 6 historic session logs back to 2026-03-21

The directory holds session logs going back to March. Per the `.gitignore`: `.claude/logs/sessions/` is ignored. So these are local-only artifacts. Should they be auto-archived after N days? Currently grows unbounded.

---

## 5. Pending Work — Critical Path

This section consolidates open work that blocks "making this project a success" — i.e., pending items the user has explicitly invested in via ADRs or recent decisions.

### 5.1 Phase 32 (BLUEPRINT IDE Build Mode) — 6 open tasks

`BP-FLAG-1` (haiku/low — DO FIRST), `BP-FORMS-1` (sonnet/high), `BP-ESCAPE-1` (sonnet/medium), `BP-UNDO-1` (haiku/low), `BP-HELP-1` (sonnet/medium), `BP-COLOR-1` (sonnet/medium).

### 5.2 Phase 31 (Sidebar + Export Provenance) — partially shipped

| Task | Status |
|---|---|
| `SIDEBAR-CONFIGS-1` | ✅ Done today |
| `SIDEBAR-REGISTRY-1` | ✅ Done today |
| `SIDEBAR-VALIDATE-1` | ✅ Done today |
| `EXPORT-HASH-2` | Open (sonnet/medium) — Parquet metadata read |
| `EXPORT-VERSION-1` | Open (haiku/low) — git_commit + release_version |
| `EXPORT-IMG-META-1` | Open (sonnet/medium) — embed provenance in PNG/SVG/PDF |
| `EXPORT-AUDIT-COMPLETE-1` | Open (sonnet/medium) — full provenance dict |

ADR-069 was authored 2026-05-05 and its 4 implementation tasks are still open. This is a coherent cluster — one focused session could close all four.

### 5.3 ADR045-REFACTOR — Two-Category Law fix

Open `[opus/high]` task. Required to unblock ADR-045 compliance and headless-reuse story. See §1.1.

### 5.4 ADR-076 BLUEPRINT AI Agent Helper — 10 open sub-tasks

See §1.2. Recommend MVP scoping before starting.

### 5.5 DEPLOY-CONNECT-1 — Posit Connect deployment

Decided 2026-05-09. 5 open sub-tasks. Cleanly bounded — not blocked by anything except `PYPROJECT-DEPS-1` (the editable-libs declarations).

### 5.6 IMPORT-UI-1 + UI-TITLE-1 — UX polish decided 2026-05-05

Both open `[sonnet/medium]` and `[sonnet/high]`. User-facing work that has been waiting since May 5. Could ship in a single combined session.

### 5.7 Lineage 2 (Plasmid Dynamics) — verify 95% complete

See §3.8.

### 5.8 INGEST-SANITIZE-1 — `DataSanitizer` not wired into `IngestorOrchestrator`

Open `[sonnet/medium]` task in `tasks.md` line 86. Real bug — sanitisation exists but is bypassed in production path. Audit reference: `audit_final_exhaustive_2026-05-03.md §1A`.

### 5.9 ACTION-RENAME-1 — naming alignment with Polars

Open `[sonnet/medium]`. Should happen BEFORE adding more `@register_action` entries to avoid double-renames.

### 5.10 Documentation regeneration

- `tree.txt`
- `dependency_index.md` via `build_dep_graph.py`
- `changelog.md` — 8 days of phase work to backfill
- `handoff_active.md` — replace with current state

---

## 6. Architectural Health Assessment

### 6.1 What is working WELL

| Area | Strength |
|---|---|
| **Manifest engine** | 65 actions registered, all use canonical `action:` syntax (no shorthand violations found across all manifests) |
| **VizFactory** | 195 components, full Plotnine parity |
| **Gallery** | 34 bundles, 100% taxonomy compliance, fresh index |
| **Persona infrastructure** | 8 templates, sidebar slot registry shipped, 2 validators run at startup |
| **Test coverage** | 97 unit tests pass; Playwright smoke suite stable; filter operator regression locked down (21 cases) |
| **ADR cadence** | 76 ADRs over ~3 months — disciplined decision logging |
| **Lineage tooling** | Today's LINEAGE-NAV-1 + LINEAGE-EXPORT-1 ship `build_plot_lineage` + Mermaid graph |
| **Dependency tracking** | `@deps` blocks present on all 12 handlers + most modules; auto-generated index works |

### 6.2 What is FRAGILE

| Area | Risk |
|---|---|
| **app/modules/ ↔ app/handlers/ split** | Two-Category Law violations break the headless-reuse promise |
| **Persona rules vs. code** | Rules document violations that have already been fixed; flag definitions ahead of code |
| **Documentation freshness** | 4 days+ stale on multiple critical files; agents will resume with wrong context |
| **CSS architecture** | 101 inline styles still in handlers; theme.css is the rule but not the practice |
| **ADR registry** | Numbering gap (072 missing), out-of-sequence ordering |
| **server.py size** | Over the explicit 250-line cap; trending toward continued growth |

### 6.3 Strategic gaps

| Gap | Impact |
|---|---|
| **MVP slicing for ADR-076** | The agent helper feature is a multi-week scope without an MVP definition |
| **Polars action parity** | 65 of ~175 — direct constraint on what bio-scientists can express in YAML |
| **In-app help system (HELP-INLINE-1, HELP-DOCS-1)** | Decided today, no implementation. Required for non-technical users |
| **LIMS integration (RESEARCH-LIMS-1)** | Deferred. Required for any production lab deployment |

---

## 7. Top-10 Prioritised Recommendations

These are ordered by **(blast radius × ease) / cost** — high-leverage, low-cost first.

| # | Action | Severity addressed | Cost | Why this rank |
|---|---|---|---|---|
| 1 | Run `build_dep_graph.py` + regenerate `tree.txt` + update `handoff_active.md` | §2.5, §2.3 | 5 min | Removes stale-context trap for next agent session |
| 2 | Update `rules_persona_feature_flags.md` "Known violations" → "Verified clean" | §2.1 | 5 min | Stops misleading future agents |
| 3 | Implement `BP-FLAG-1` — add `manifest_edit_enabled` to all 8 templates + bootloader cascade | §1.3, §3.1 | 30 min | Unblocks all downstream BLUEPRINT IDE work |
| 4 | Append phase 28/29/31/32 + ADRs 066–076 to `changelog.md` | §2.6 | 30 min | Restores breakage-tracking authority |
| 5 | Convert `Quality_metrics_wrangling.yaml` to `tier1: []` or delete | §3.4 | 5 min | Removes legacy contamination |
| 6 | Insert ADR-072 stub + sort ADRs numerically | §1.4 | 15 min | Closes documentation integrity gap |
| 7 | Add `utils` to pyproject.toml of transformer + viz_factory + (any other importers) | §2.4 | 15 min | Unblocks DEPLOY-CONNECT-1 |
| 8 | Verify Plasmid Dynamics lineage via debug_assembler.py; close or refine task | §3.8 | 15 min | Closes a phantom-open task |
| 9 | Sweep `filter_and_audit_handlers.py` inline styles into theme.css classes (22 styles) | §2.2 | 1 session | Highest-density CSS violation; sets pattern for other files |
| 10 | Plan ADR-076 MVP-1 scope (1-page spec) | §1.2 | 1 session | Prevents multi-week scope sink |

The first 8 items are <2 hours total and immediately reduce drift between docs / rules / code. Items 9 and 10 require focused sessions but are the structural prerequisites for the next major milestones (BLUEPRINT IDE form work and the AI Agent Helper).

---

## 8. What this audit did NOT cover

Honest accounting of audit scope limits:

- **Runtime behaviour**: No app launch performed. UI smoke tests not re-run. Could not verify whether ADR-075 schema_registry actually loads the 19+7 schemas at startup.
- **Manifest data correctness**: Did not run `debug_assembler.py` against any manifest. Plasmid Dynamics completion estimate (95%) is structural, not behavioural.
- **Test pass rate**: Did not run `pytest`. The "97 tests pass" figure is from today's session log; not independently verified in this audit.
- **CSS visual review**: Did not load the theme to compare to ADR-055 Deep Violet / SPARMVET Blue requirements visually.
- **Vendor manifest staleness**: Did not check whether `app/src/www/vendor/VENDOR_MANIFEST.md` is current vs. what's in `vendor/` directory.
- **Quarto build correctness**: Did not run `quarto render docs/` to confirm docs build cleanly.
- **Subprocess/fcntl/flock isolation for ADR-076**: Did not test whether the proposed `cwd={uuid}/` discipline survives an actual concurrent Claude CLI session.
- **External system dependencies**: Did not verify Galaxy / IRIDA / Connect deployment paths.

These are all good candidates for follow-up @verify cycles when the corresponding implementation work begins.

---

## 9. Closing observation

The project is in a **mature mid-stage**: the engine works, the UI works, the persona system works, the gallery works. The friction now comes from **decisions outpacing implementation** (ADR-075/076 today, not yet coded) and **documentation lagging code** (rules talk about violations that no longer exist, changelog is 8 days behind, handoff is 4 days behind).

A 2-hour documentation-reconciliation session followed by `BP-FLAG-1` would set up a clean slate for the next major sprint (BLUEPRINT IDE forms). That's the highest-leverage near-term move.

Beyond that, the main risk to project success is **scope discipline on ADR-076** (the AI Agent Helper). Without an MVP carve-out, this single feature could absorb 4–6 weeks of single-developer time and crowd out the lineage / export-provenance / persona / gallery work that's already 80% shipped.

---

**End of audit.**
