---
trigger: always_on
deps:
  provides: [rule:legacy_management, rule:deprecation_markers, rule:historical_preservation]
  documents: []
  consumed_by: [.claude/rules/workspace_standard.md]
---

# Legacy & Deprecation Management (rules_legacy_management.md)

**Authority:** @dasharch
**Status:** ACTIVE — enforced immediately (2026-05-20).

**The core principle:** History is valuable. Confusion is not. Any content that is no longer
active MUST be visibly marked so no agent or author mistakes archaeology for current practice.

**The quality standard:** This project promotes clarity, maintainability, and clean feature
development above all else. Fuzzy shortcuts and half-finished deprecations are explicitly
forbidden — they accumulate silently and become the hardest maintenance problems to fix later.
The rule is: **do it properly or do not do it at all.**

- One authoritative way to do each thing — not two with one "for backwards compat".
- Every deprecated item has a removal task. No orphaned deprecations.
- Every removed item has a clear tombstone. No silent disappearances.
- Compatibility shims that have no removal plan are tech debt in disguise — name them and schedule them.

---

## 1. The Four Document States

Every piece of content in rules, knowledge, docs, and code belongs to exactly one state.
If the state is not obvious from context, it must be declared explicitly.

| State | In code? | Enforced? | Keep? | Marker required |
|---|---|---|---|---|
| **Active** | Yes | Yes | Yes | None — unmarked = active |
| **Deprecated** | Yes | No (warns) | Yes, until task ships | `> DEPRECATED` banner + task ID |
| **Historical** | No | No | Yes, indefinitely | `> HISTORICAL` banner |
| **Tombstone** | No | No | Temporarily | `> REMOVED` banner + expiry phase |

**Unmarked = Active.** If content has no marker, agents treat it as current and enforced.
This means every non-active item MUST carry its marker — no exceptions.

---

## 2. Standard Markers

### 2a. Deprecated

Content still present in code or rules but scheduled for removal. The item works but is
being phased out. Agents should warn when it is used.

**In rule/knowledge `.md` files** — blockquote banner at the top of the affected section:

```markdown
> **DEPRECATED (ADR-083, 2026-05-20):** `factory_id` shorthand is removed in Phase 33.
> Use explicit `geom_*` layers in `layers:` and aesthetics in `mapping:`.
> Engine raises `PipelineError` when encountered. Migration: `assets/scripts/migrate_plot_specs.py`.
> **Removal task:** BP-PLOT-LEGACY-REMOVE-1
```

**In Python** — comment immediately before the deprecated block:

```python
# DEPRECATED (ADR-083): factory_id expansion — raises PipelineError. Removal: BP-PLOT-LEGACY-REMOVE-1
```

**In YAML** — comment on the deprecated key:

```yaml
# DEPRECATED (ADR-083): factory_id — use explicit geom layer. Removal: BP-PLOT-LEGACY-REMOVE-1
factory_id: bar_logic
```

**Required fields in every `DEPRECATED` marker:**
- The ADR or decision that deprecated it
- The date deprecated
- What to use instead
- The tasks.md entry that will remove it (`BP-*`, `ACTION-*`, etc.)

A deprecation with no removal task is **forbidden** — it becomes invisible debt.

---

### 2b. Historical

Content that is no longer active but is kept because it explains *why* a decision was made,
records a prior approach, or provides useful context for understanding the current design.
Historical content is **never instructions** — it is documentation of the past.

**In rule/knowledge `.md` files** — blockquote banner wrapping the historical section:

```markdown
> **HISTORICAL (superseded by ADR-083, 2026-05-20):**
> The following describes the previous `factory_id` abstraction. It is no longer
> active — kept here to explain the migration rationale.
>
> [historical content follows, indented or in a fenced block]
```

**In ADR entries** — the ADR log already has date and decision context. Mark the
*specific section* that describes a superseded approach:

```markdown
> **HISTORICAL:** This section describes the pre-ADR-083 plot authoring model.
> Current authoring rules are in `rules_manifest_structure.md §8`.
```

**Rules for Historical content:**
- Never contains instructions (no "you MUST", "always use", "the rule is")
- Never contains code that should be copied into new work
- Always links to the current active replacement
- Has no expiry — historical context can be kept indefinitely

---

### 2c. Tombstone (post-removal migration notice)

Content that existed, was removed, and whose tombstone exists only to help authors who
encounter old manifests, scripts, or specs that reference the removed feature.

```markdown
> **REMOVED (ADR-083, Phase 33, 2026-05-20):**
> `factory_id` has been removed from the engine. Manifests using it will receive a
> `PipelineError` with migration instructions.
> **Migration tool:** `assets/scripts/migrate_plot_specs.py --apply`
> **Tombstone expires:** Phase 35 (delete this block after two phases)
```

**Tombstone expiry:** After two major phases, tombstones are deleted. They are not
permanent documentation — that role belongs to the ADR and Historical markers.
Add a tasks.md entry when creating a tombstone: `- [ ] Delete factory_id tombstone (Phase 35)`.

---

## 3. Where Each State Appears

| Location | Active | Deprecated | Historical | Tombstone |
|---|---|---|---|---|
| `.claude/rules/*.md` | Yes | Yes (banner) | Yes (banner) | Yes (banner + expiry) |
| `.claude/knowledge/architecture_decisions.md` | ADR context | ADR notes | ADR superseded sections | Rare |
| `.claude/knowledge/*.md` | Yes | Yes (banner) | Yes (banner) | Yes (banner + expiry) |
| `docs/appendix/*.yaml` | Yes | Yes (comment) | No — docs should stay current | Yes (comment + expiry) |
| `libs/**/*.py` | Yes | Yes (comment + warning) | No — delete, use git history | No — delete |
| `config/manifests/**/*.yaml` | Yes | No — migrate or delete | No — delete | No — delete |
| `assets/scripts/*.py` | Yes | Yes (comment) | No — delete | No — delete |
| `tasks.md` | Current tasks | Task for removal | No | No |

**Python and YAML files do not get Historical markers.** For code, git history is the
archive. Historical context belongs in ADR entries and knowledge files, not in source.

---

## 4. Mandatory Removal Task Rule

Every `DEPRECATED` marker MUST be paired with an open task in `tasks.md`:

```
- [ ] **[TASK-ID]** `[model/effort]`: Remove deprecated `factory_id` from `normalise_plot_spec`.
  Replace with PipelineError. Gate: BP-PLOT-DOCS-1 done.
```

**An agent that adds a `DEPRECATED` marker without a linked tasks.md entry is in violation.**

If the removal is gated on another task, document the gate in both places:
- In the deprecated marker: `Removal gated on: BP-PLOT-DOCS-1`
- In the tasks.md entry: `Depends: BP-PLOT-DOCS-1`

---

## 5. Audit Checklist (run at session end when rules/knowledge files were modified)

```bash
# 1. Find "not supported" without a deprecation banner (likely unmarked deprecated)
grep -rn "not supported\|no longer\|removed\|legacy" \
  .claude/rules/ .claude/knowledge/ docs/appendix/ \
  | grep -v "DEPRECATED\|HISTORICAL\|REMOVED\|architecture_decisions"

# 2. Find DEPRECATED markers with no task ID
grep -rn "DEPRECATED" .claude/rules/ .claude/knowledge/ docs/ \
  | grep -v "BP-\|ACTION-\|TASK-\|SIDEBAR-\|VIZFAC-"

# 3. Find tombstones past their expiry phase
grep -rn "Tombstone expires" .claude/rules/ .claude/knowledge/ docs/
```

Any hits from check 1 or 2 are protocol violations — fix before ending the session.
Check 3 is a reminder, not a blocker.

---

## 6. The Full Deprecation Protocol (mandatory when creating any DEPRECATED marker)

Adding a `DEPRECATED` marker is not the end — it is the beginning of a tracked removal
process. Every deprecation MUST produce a tasks.md entry that covers all seven steps below.
Steps 1–3 happen when the marker is added. Steps 4–7 happen in the removal task.

**Do not declare a deprecation "done" until all seven steps are complete or explicitly
scheduled as sub-tasks with their own task IDs.**

### Step 1 — Dependency sweep (do this first, before the marker)

```bash
# What directly references the deprecated item by name?
grep -rn "<deprecated_name>" \
  libs/ app/ config/ assets/scripts/ docs/ .claude/rules/ .claude/knowledge/ \
  --include="*.py" --include="*.yaml" --include="*.md" --include="*.qmd"

# What does the @deps graph say consumes it?
grep -rn "consumes:.*<deprecated_name>" \
  libs/ app/ config/ .claude/ --include="*.py" --include="*.yaml" --include="*.md"
```

Produce a list: **who consumes this, and what breaks if it is removed today?**
This list drives the scope of the removal task.

### Step 2 — Impact assessment

For each consumer found in Step 1, classify:

| Consumer type | Action required |
|---|---|
| Rule / knowledge doc | Update to canonical form, or add DEPRECATED marker if it too is deprecated |
| Python code (engine) | Update to use replacement, or gate on removal task |
| YAML manifest / config | Migrate to canonical form (use migration script if one exists) |
| Test | Update or remove test; add test for the replacement behaviour |
| User doc (README, .qmd) | Update to canonical form |
| ADR | Mark section HISTORICAL if it described the deprecated approach |

### Step 3 — Migration path

Before marking anything DEPRECATED, confirm the replacement exists and is documented:
- The canonical replacement is named in the DEPRECATED banner
- A migration script or guide exists if the change is non-trivial
- The replacement is tested and verified before the deprecated path is removed

### Step 4 — Code removal (in the removal task)

Remove the deprecated code path. Replace with a `PipelineError` or `ConfigurationError`
that names the deprecated item, links to the replacement, and (if applicable) names
the migration tool. No silent failures — the error must be actionable.

### Step 5 — Test sweep (in the removal task)

- Remove all tests that tested the deprecated behaviour
- Add at least one test that verifies the error is raised correctly
- Run the full test suite and confirm it passes

### Step 6 — Documentation consistency sweep (in the removal task)

Run this checklist across every location that referenced the deprecated item:

- [ ] All `.claude/rules/*.md` files — no authoring examples, no active instructions
- [ ] All `.claude/knowledge/*.md` files — historical sections marked HISTORICAL
- [ ] All `docs/appendix/*.yaml` and `docs/appendix/*.qmd` files — canonical examples only
- [ ] All `docs/**/*.qmd` user documentation — no deprecated patterns in tutorials
- [ ] All `libs/*/README.md` files — function/class names up to date
- [ ] All `assets/template_manifests/` — templates use canonical format only
- [ ] `CLAUDE.md` and `AGENT_GUIDE.md` if they referenced the deprecated item

### Step 7 — ADR and architecture record

If the deprecation represents a significant architectural decision:
- Add or update an ADR entry confirming the removal is complete
- Update the DEPRECATED marker in the relevant rule file to a REMOVED / HISTORICAL marker
- Convert the tombstone text: explain what was removed and where to find the replacement

---

## 7. Applying This Rule to Existing Content

This rule takes effect immediately (2026-05-20). Existing violations are not retroactively
blocking — they are tracked as the audit routine surfaces them. Priority order for cleanup:

1. **Agent rule files** (`.claude/rules/`) — highest priority, agents read these every session
2. **Knowledge files** (`.claude/knowledge/`) — high priority
3. **Appendix docs** (`docs/appendix/`) — medium priority
4. **Library README files** — low priority, batch during documentation sprint

When an audit surfaces a violation during any session, fix it immediately (it is a small
change) rather than scheduling it. Do not let violations accumulate.
