# Audit Triage Protocol

**Authority:** @dasharch  
**Purpose:** Defines how audit reports are read, triaged, and converted to tasks.  
**Scan command:** `grep -rL "^Status: PROCESSED" .claude/logs/audits/*.md 2>/dev/null`

---

## 1. The Problem This Solves

Audit scripts write markdown reports to `.claude/logs/audits/`. Without a triage step those
reports accumulate unread. This protocol makes triage **automatic at session start** and
**deterministic at any other time** — an agent always knows which reports need action.

---

## 2. Report Status Convention

Every audit report gets a `Status:` line inserted **at the top** (line 1) when triage is
complete. Until that line exists, the report is **UNPROCESSED**.

```
Status: PROCESSED 2026-05-14 — 3 tasks created, 1 false positive skipped, 0 acceptable debt noted
```

Format: `Status: PROCESSED YYYY-MM-DD — <N> tasks created, <N> false positive[s] skipped, <N> acceptable debt noted`

An UNPROCESSED report has no `Status:` line at line 1 (the `# Audit Report:` heading is line 1 for
all scripts in this suite).

---

## 3. Session-Start Hook (Mandatory)

At the **start of every session**, after reading `tasks.md` and `architecture_decisions.md`,
run the scan and triage any unprocessed reports:

```bash
grep -rL "^Status: PROCESSED" .claude/logs/audits/*.md 2>/dev/null
```

If the command returns files: **triage them before any other work** (§4).  
If the command returns nothing: proceed normally.

This rule is non-negotiable. Unprocessed audit findings are invisible debt.

---

## 4. Triage Steps (Per Report)

For each unprocessed report:

### 4-A. Read and categorise each finding

| Finding type | Decision |
|---|---|
| Violation already tracked in `tasks.md` | **Duplicate** — skip, note it |
| Violation references a file that no longer exists | **False positive** — skip, note it |
| Known acceptable tech debt (in `KNOWN_VIOLATIONS` or explicitly accepted) | **Acceptable debt** — skip, note it |
| Real violation not yet tracked | **Create task** (§4-B) |

### 4-B. Create tasks for real violations

Tasks go in `.claude/tasks/tasks.md` under the appropriate section header. Use the
violation category to choose priority and model tag:

| Category | Priority marker | Model tag | Section |
|---|---|---|---|
| Dependency conflict / fatal cascade | `[P0]` | `[sonnet/high]` | `### 🔴 @dasharch Handoffs` |
| New ADR violation / blocking import | `[BLOCKER]` | `[sonnet/high]` | `### 🔴 @dasharch Handoffs` |
| Missing core test infrastructure | Unlabeled | `[sonnet/medium]` | `### 🔴 @dasharch Handoffs` |
| Stale doc path / broken @deps link | `[AUDIT]` | `[haiku/low]` | `### 🔴 Fixes` (or `### 🟡 Pending`) |
| Missing @deps block | `[AUDIT]` | `[haiku/low]` | `### 🟡 Pending` |
| Parity mandate gap | `[PARITY]` | `[sonnet/medium]` | `### 🟡 Pending Enhancements` |
| Documentation drift | `[AUDIT]` | `[haiku/low]` | `### 🟡 Pending` |
| Outdated package (MINOR/PATCH) | `[AUDIT]` | `[haiku/low]` | `### 🟡 Pending` |
| MAJOR package update | `[AUDIT]` | `[sonnet/medium]` | `### 🟡 Pending` |

Task format:
```
- [ ] [AUDIT] <short description> — from audit_NAME_YYYY-MM-DD.md [model/effort]
```

Include the source report filename so the task is traceable.

### 4-C. Mark the report as processed

Insert `Status: PROCESSED ...` as the **first line** of the report file:

```
Status: PROCESSED 2026-05-14 — 3 tasks created, 1 false positive skipped, 0 acceptable debt noted
```

Then update the status matrix in `audit_routine_registry.md`:
- Set **Last Result** to `PASS` / `FAIL N` (from the report's own summary line)
- Set **Last Run** date

### 4-D. Commit

```
audit: triage YYYY-MM-DD — <routine names> processed, <N> tasks created
```

---

## 5. When Not to Create a Task

Do **not** create a task for:

- A violation listed in `KNOWN_VIOLATIONS` in `audit_cross_lib.py` — these are accepted tech debt
- A path that no longer exists on disk — the violation is stale, the audit script will not surface it again once the source is fixed
- A violation identical to an open task already in `tasks.md` (check by file path + issue type)
- Documentation backtick paths inside code-block examples in `.qmd` files — those are illustrative, not real paths
- PATCH package updates for packages with no history of breakage — acceptable to batch at next release; note as acceptable debt

If in doubt, create the task with `[haiku/low]` and let the user decide.

---

## 6. Handling a Backlog of Unprocessed Reports

If multiple reports are unprocessed, process them in this priority order:

1. Any report with `❌` in its summary (conflicts, fatal cascade, test failures)
2. `audit_cross_lib_*.md` — ADR-011 violations are blockers
3. `audit_template_flags_*.md` — fatal cascades block app startup
4. `audit_manifest_integrity_*.md` — broken manifests break the app
5. `audit_deps_verify_*.md`, `audit_task_drift_*.md` — hygiene
6. `audit_phase_order_*.md`, `audit_changelog_sync_*.md` — documentation
7. `audit_docs_sync_*.md`, `audit_library_tests_*.md`, `audit_package_deps_*.md` — lower urgency

Triage all of them before starting any implementation work.

---

## 7. Fast-Scan for Audit Debt (Status Overview)

To see the current state of all audit logs at a glance:

```bash
# Unprocessed reports (need triage)
echo "=== UNPROCESSED ===" && grep -rL "^Status: PROCESSED" .claude/logs/audits/*.md 2>/dev/null

# Processed reports (already triaged)
echo "=== PROCESSED ===" && grep -rl "^Status: PROCESSED" .claude/logs/audits/*.md 2>/dev/null | xargs -I{} head -1 {}
```

Or in one command for a dashboard view:
```bash
for f in .claude/logs/audits/*.md; do
  status=$(head -1 "$f" | grep -o "PROCESSED.*" || echo "UNPROCESSED")
  echo "$(basename $f): $status"
done
```

---

## 8. Adding New Audit Scripts

When a new `scripts/audit_*.py` is added:

1. Add its output path to the quick test commands in `schedule_commands.md`
2. Add a row to the status matrix in `audit_routine_registry.md`
3. The triage protocol (this file) applies automatically — no changes needed here
