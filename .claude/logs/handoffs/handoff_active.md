# Handoff — Active State (2026-05-09 afternoon)

**Branch:** dev
**Last commit on disk:** check `git log -1 --format=%h%x09%s` — work below is uncommitted.
**Active agent:** @dasharch
**Previous handoff:** archived at `.claude/logs/handoffs/archive/handoff_2026-05-09_morning.md` (move it there before starting fresh work)

---

## What just landed (uncommitted)

Four ADRs authored + two tasks closed in a single afternoon session. The thread was:
**BP-AGENT-FLAG-1 → user pushback on silent cascades → ADR-077 → user request for fail-fast diagnostics → ADR-078 + ADR-079 placeholder → DIAG-CORE-1 implementation.**

### ADRs

| ADR | Title | Status | Location |
|---|---|---|---|
| **ADR-076** (revised) | BLUEPRINT AI Agent Helper | DECIDED | `architecture_decisions.md` ~L2706 |
| **ADR-077** | No-Silent-Suppression Principle (Group D fatal cascades) | DECIDED + APPLIED | `architecture_decisions.md` ~L3035 |
| **ADR-078** | Diagnostic Error Discipline (`DeploymentError`) | DECIDED, Phase B applied | `architecture_decisions.md` ~L3100 |
| **ADR-079** | Runtime Error Discipline | PLACEHOLDER | `architecture_decisions.md` ~L3260 |

### Tasks closed

- ✅ **BP-AGENT-FLAG-1** `[haiku/low]` — `blueprint_agent_enabled` flag + `blueprint_agent:` config block in 8 templates; cascade is fatal via `PersonaValidator` Rule 7.
- ✅ **DIAG-CORE-1** `[sonnet/medium]` — `DeploymentError` dataclass + helpers + PersonaValidator retrofit + `server.py` startup gate + CLI script.

### Files touched (all uncommitted)

**New:**
- `app/modules/deployment_error.py` — load-bearing for ADR-078

**Modified:**
- `config/ui/templates/*.yaml` (×8 — flag + 2× config blocks)
- `app/modules/persona_validator.py` — Rule 7 + return type changed to `list[DeploymentError]`
- `app/src/server.py` — `exit_if_errors()` replaces `raise ValueError`
- `app/src/bootloader.py` — Group D silent cascade explicitly NOT applied (docstring updated)
- `scripts/validate_persona_config.py` — uses `format_errors_block()`
- `.claude/knowledge/architecture_decisions.md` — 4 ADRs (~700 lines added)
- `.claude/knowledge/project_conventions.md` — new §17 (fail-fast cascade) + §18 (DeploymentError)
- `.claude/knowledge/changelog.md` — afternoon entry
- `.claude/rules/rules_persona_feature_flags.md` — Group D, matrix row, Cascade Enforcement §4–5, misconfig table, files governed
- `.claude/tasks/tasks.md` — 2 tasks closed; new "Diagnostic Error Discipline" + "Runtime Error Discipline" task blocks (13 new tasks)
- `.claude/logs/audits/audit_2026-05-09.md` — afternoon entry appended

### Verification done in-session

- `scripts/validate_persona_config.py --all` → 8/8 PASS, 0 errors
- Synthetic 3-violation config → clean formatted block to stderr (3 fatal errors with all 5 fields populated)
- `python -c "from app.src.main import app"` → imports cleanly under default persona
- Bootloader cascade verified: developer → agent on; static → agent off; synthetic contradiction → fatal validator error

---

## Next up — recommended order

User asked for "lowest-conflict-risk block, one task at a time". BP-AGENT-FLAG-1 is done. Remaining in that block:

| Task | Effort | Notes |
|---|---|---|
| **BP-AGENT-PANEL-1** | `[haiku/low]` | Register `blueprint_agent_chat` in `app/modules/sidebar_registry.py` + add to BLUEPRINT right_sidebar slot list in developer/qa templates (after `blueprint_logic`). Pure config; safe. |
| **BP-AGENT-CSS-1** | `[haiku/low]` | `.bp-agent-*` rules in `config/ui/theme.css`. Pure CSS; safe. |
| `HELP-DOCS-1` | `[haiku/low]` | Bundle `docs/_site/` as Shiny static assets. Conditional on presence. |
| `21-F-7` | `[haiku/low]` | Add `scale_x_discrete` / `scale_y_discrete` to test manifests for Year/ST columns. |
| `TubeMap aesthetics` | `[haiku/low]` | Cytoscape style + rename "ref" → "Add". Touches `libs/blueprint_arch/blueprint_mapper.py`. |

**Caveat:** a parallel audit-fix agent is running. Avoid touching `libs/ingestion/`, `libs/transformer/`, `app/modules/` Two-Category violations, repo-hygiene tasks (`UTILS-RELOC-2`, `PYPROJECT-DEPS-1`, `ACTION-RENAME-1`, `ADR-011 cross-lib violations`, `INGEST-SANITIZE-1`, `ADR045-REFACTOR`).

---

## Open questions / decisions parked

1. **`DeploymentError` placement for `libs/connector/` retrofit (DIAG-CONNECTOR-1).** Current location is `app/modules/deployment_error.py` — connectors can't import from `app.*` (cross-lib violation, ADR-011). Decision when DIAG-CONNECTOR-1 lands: move to `libs/utils/` (canonical fix) OR copy the dataclass shape into `libs/utils/errors.py`. Flagged in the task description.

2. **`audit_report_enabled` flag.** Listed in templates and validator but no longer used by any UI code as of 2026-05-04 export redesign. Could be removed in a future cleanup task — not urgent.

3. **Streaming for the agent.** User explicitly dropped Phase 1 streaming. ADR-076 §9 records this as a deferral, not a rejection — re-evaluate if buffered tempo feels sluggish in practice.

4. **`testing_mode` field semantics on pipeline personas.** Pipeline personas (static, simple) are forced `testing_mode=false`. If someone later argues for a "test the pipeline persona" use case, the answer is "use a more capable persona" (memory note). Don't add a `testing_mode` flag to pipeline personas.

---

## Mandatory session-end protocol (NOT YET DONE)

Per `workspace_standard.md` §5-E:

1. ⏳ **Run `build_dep_graph.py`** to refresh `dependency_index.md` after touching `deployment_error.py`, `persona_validator.py`, `server.py`. (User asked for handoff before this — should be the new agent's first action OR run now before commit.)
2. ⏳ **Verify @deps blocks** on every modified file. `app/src/server.py` likely needs its consumes list updated (now imports `deployment_error.py`).

Suggested first-action checklist for the new agent:

```bash
# 1. Verify in-flight state
git status
git log -1 --format=%h%x09%s

# 2. Run dep-graph refresh (idempotent)
.venv/bin/python assets/scripts/build_dep_graph.py

# 3. Sanity check
./.venv/bin/python -m pytest app/tests/test_filter_operators.py libs/connector/tests/ -q
./.venv/bin/python scripts/validate_persona_config.py --all
./.venv/bin/python -c "from app.src.main import app; print('OK')"

# 4. Commit if green (do NOT push without confirmation):
git add -A && git commit  # see suggested commit message below
```

### Suggested commit message

```
feat(adr-076 / adr-077 / adr-078): BLUEPRINT agent flags + fail-fast cascades + DeploymentError

* ADR-076 BP-AGENT-FLAG-1: blueprint_agent_enabled flag + blueprint_agent: config
  block added to all 8 persona templates. Developer + qa default true; others false.
* ADR-077: Group D cascades (manifest_edit_enabled, blueprint_agent_enabled) are
  now fatal validator errors, not silent bootloader suppression. Establishes the
  general no-silent-suppression principle for future config decisions.
* ADR-078 DIAG-CORE-1: DeploymentError dataclass + format_errors_block /
  exit_if_errors / raise_if_errors helpers in app/modules/deployment_error.py.
  PersonaValidator retrofitted to return list[DeploymentError]. server.py and
  validate_persona_config.py CLI use the new format.
* ADR-079 placeholder authored to lock in the runtime-error problem (ingestion /
  assembler / wrangler / viz_factory / T3 apply / Blueprint manifest validation).

Phase C of ADR-078 (committed work, 6 tasks) and ADR-079's full design + 6
deferred runtime-error retrofit tasks added to .claude/tasks/tasks.md.

Verified: 8/8 templates pass validate_persona_config.py; synthetic contradictory
config produces clean formatted error block; app imports cleanly.
```

---

## Pointers for continuity

- **For BLUEPRINT agent next steps:** read ADR-076 in full before starting BP-AGENT-PANEL-1 onwards. Particularly §10 (tool-call) and §11 (subprocess isolation) — those are the load-bearing constraints for BP-AGENT-1.
- **For Phase C of ADR-078:** start with `DIAG-VALIDATE-SIDEBAR-1` — same pattern as PersonaValidator retrofit, smallest delta. Then `DIAG-BOOTLOADER-1`. Defer `DIAG-CONNECTOR-1` until after the `libs/utils/` placement decision is made.
- **For ADR-079:** trigger to author the full ADR is "Phase C largely complete OR first runtime-error pain point becomes blocking". Don't pre-author.

@dasharch out.
