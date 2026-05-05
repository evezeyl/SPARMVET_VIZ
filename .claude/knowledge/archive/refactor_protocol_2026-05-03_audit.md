# Refactor Protocol — Audit Remediation (2026-05-03)

**Status:** ACTIVE (2026-05-03)
**Origin:** Adapted from `refactor_protocol_phase24.md` (Phase 24 home_theater decomposition).
**Scope:** Wave 1 mechanical fixes from `audit_final_exhaustive_2026-05-03.md`.
**Driver:** [.antigravity/logs/2026-05-03_solving_problems_detected_audit.md](.antigravity/logs/2026-05-03_solving_problems_detected_audit.md)

> Phase 24 protocol's discipline (manifest → move → verify → cleanup → verify → commit) is generic. This document scopes it to the current audit-remediation refactors. Phase 24-specific text (LOC budgets, shiny smoke tests, public define_server signature) is dropped or replaced.

---

## Active scope (this protocol covers ONLY these)

| ID | Refactor | Risk | Files touched | Audit § |
|---|---|---|---|---|
| **R-A** | Strip `sys.path.*` insertions from 6 non-test/test debug files | Low | 6 files (one commit per file) | §3A |
| **R-B** | Remove `ingestion.ingestor` import from `transformer/pipeline.py` | Medium | `libs/transformer/src/transformer/pipeline.py` + any caller that depended on the old surface | §2C Task A |

Other Wave 1 tasks (Boolean Manifest Trap, Violet Law, terminology) are **not** part of this protocol — they are doc/manifest edits, not code refactors.

---

## R-A — sys.path removal

### Targets (verified)

| # | File | Current line | Hack |
|---|---|---|---|
| A1 | [libs/viz_gallery/tests/debug_gallery_ui_logic.py:12](libs/viz_gallery/tests/debug_gallery_ui_logic.py#L12) | `sys.path.append(str(project_root))` | append |
| A2 | [libs/utils/tests/debug_blueprint_mapper.py:8](libs/utils/tests/debug_blueprint_mapper.py#L8) | `sys.path.append(str(Path(__file__).parent.parent / "src"))` | append |
| A3 | [app/tests/debug_pipeline_connector.py:25](app/tests/debug_pipeline_connector.py#L25) | `sys.path.insert(0, str(ROOT))` | insert |
| A4 | [app/tests/debug_home_theater.py:36](app/tests/debug_home_theater.py#L36) | `sys.path.insert(0, str(Path(__file__).parents[2]))` | insert |
| A5 | [app/tests/debug_session_flow.py:28](app/tests/debug_session_flow.py#L28) | `sys.path.insert(0, str(Path(__file__).parents[2]))` | insert |
| A6 | [libs/viz_gallery/assets/generate_previews.py:26-27](libs/viz_gallery/assets/generate_previews.py#L26-L27) | two `sys.path.insert` | insert × 2 |

### Per-file change manifest (post before each edit)

```
CHANGE MANIFEST — R-A.<n> (<file>)
Lines being REMOVED: <line numbers + exact text>
Imports kept (verify still resolvable via editable installs): <list>
Adjacent dead code to remove: <import sys / Path-juggling-only-for-sys.path>
Verification: `./.venv/bin/python <file> --help` (or appropriate CLI flag) must execute and show usage.
              For test runners that have no CLI: `./.venv/bin/python <file>` must run to completion (or fail for a domain reason, not ImportError).
```

### Commit discipline (per file)

One commit per file. Single, focused diff:

- `git diff --stat`: only the targeted file. If anything else shows up, abort.
- Commit message format:
  ```
  refactor(<area>): drop sys.path hack in <basename>

  ADR-016 forbids sys.path manipulation; <pkg> is editable-installed,
  so the direct import resolves without it.

  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
  ```

### Verification gate (after EACH file edit, BEFORE commit)

```bash
# 1. Run the file directly — must succeed (or fail for a domain reason, NOT ImportError)
PYTHONPATH=. ./.venv/bin/python <file>            # for runners
PYTHONPATH=. ./.venv/bin/python -c "import <pkg>" # for the affected package

# 2. App import sanity (only for app/tests/ files)
./.venv/bin/python -c "from app.src.main import app; print('OK')"

# 3. Targeted unit tests for the area
PYTHONPATH=. ./.venv/bin/python -m pytest <area>/tests/ -q

# 4. Smoke (only re-run for app/* changes — full smoke is heavy)
PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v
```

If any gate fails:
1. Diagnose. The most likely cause is a missing editable install (`pip install -e libs/<pkg>`).
2. If the package IS editable-installed and import still fails, the import path was wrong before too (the `sys.path` hack was masking it). Fix the import statement, document in the commit message.
3. If the failure is unrelated and pre-existing, capture it in `.antigravity/baselines/audit_2026-05-03_pre.txt` and proceed — but only after confirming it was already failing in the pre-flight baseline.

---

## R-B — `transformer/pipeline.py` cross-library import

### Goal

Remove the unambiguous "Clear Lines" violation: `from ingestion.ingestor import DataIngestor` in [libs/transformer/src/transformer/pipeline.py:12](libs/transformer/src/transformer/pipeline.py#L12).

### Pre-step diagnostic (mandatory)

Before touching code, answer in writing (post to chat + commit a `R-B-pre.md` note in `tmpAI/2026-05-03/`):

1. What public function(s) in `pipeline.py` actually USE `DataIngestor`? (Grep the file, list call-sites with line numbers.)
2. Who calls those `pipeline.py` functions? (`grep -rn "from transformer.pipeline\|from transformer import pipeline\|transformer\.pipeline" --include="*.py"`)
3. Are any of those callers in `app/` (acceptable target for orchestration relocation) or in `libs/transformer/tests/` (need a test-side fix)?

The answers determine whether step R-B is a **single move** (orchestration migrates to `app/`) or a **dependency-injection refactor** (pipeline accepts an injected ingestor instance).

### Decision tree

- **Case 1: pipeline.py is only called from `app/` modules** → migrate the orchestration logic up to `app/modules/orchestrator.py`. `pipeline.py` becomes a pure wrangling surface; `DataIngestor` instantiation moves to `app/`.
- **Case 2: pipeline.py is called from tests or libs** → refactor `pipeline.py` to accept `ingestor` as a constructor/function argument (dependency injection). Tests/callers create the `DataIngestor` themselves.

Document the chosen case in the change manifest before editing.

### Change manifest template

```
CHANGE MANIFEST — R-B
Decision case: <1 or 2>
Names being MOVED out of pipeline.py: [list]
Names being KEPT in pipeline.py: [list]
New signature(s): [exact def lines]
Callers to update: [paths + line numbers]
Risk level: medium (cross-library, test-covered)
```

### Commit discipline

Two commits:

- **Commit 1** (`refactor`): apply the new signature in `pipeline.py` AND update all callers in the same commit. (This is different from Phase 24's "move-then-cleanup" because here the surface changes; partial state would break callers.)
- **Commit 2** (`docs`): if rule wording in `rules_runtime_environment.md` needs updating to reflect the actually-clean state, do it here. Often empty — skip if not needed.

### Verification gate (after Commit 1, BEFORE pushing)

```bash
# 1. Transformer imports clean
PYTHONPATH=. ./.venv/bin/python -c "from transformer.pipeline import *; print('OK')"

# 2. No residual cross-library import
grep -nE "^(from|import) (ingestion|viz_factory|viz_gallery|connector|generator_utils)" libs/transformer/src/transformer/*.py
# Expected: empty output

# 3. Transformer-side debug runners still execute end-to-end
PYTHONPATH=. ./.venv/bin/python libs/transformer/tests/debug_assembler.py 2>&1 | tail -20
PYTHONPATH=. ./.venv/bin/python libs/transformer/tests/debug_wrangler.py 2>&1 | tail -20

# 4. App import still clean
./.venv/bin/python -c "from app.src.main import app; print('OK')"

# 5. Smoke tests
PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v

# 6. Full test gate (compare to baseline)
PYTHONPATH=. ./.venv/bin/python -m pytest libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py app/tests/test_filter_operators.py -q
```

If any gate fails twice → STOP, post a blocker report, do not retry on top.

---

## Pre-flight checklist (do ONCE before any R-A or R-B edit)

```bash
# 1. Tag working tree
git tag pre-audit-remediation-$(date +%Y%m%d)

# 2. Capture baseline test results
mkdir -p .antigravity/baselines
{
  echo "=== pytest libs/ + app/tests ==="
  PYTHONPATH=. ./.venv/bin/python -m pytest libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py app/tests/test_filter_operators.py -q 2>&1
  echo ""
  echo "=== app import ==="
  ./.venv/bin/python -c "from app.src.main import app; print('import OK')" 2>&1
  echo ""
  echo "=== shiny smoke ==="
  PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v 2>&1
} | tee .antigravity/baselines/audit_2026-05-03_pre.txt

# 3. Snapshot pre-existing failures explicitly
grep -E "FAIL|ERROR" .antigravity/baselines/audit_2026-05-03_pre.txt > .antigravity/baselines/audit_2026-05-03_known_failures.txt || true
```

**Gate:** If the baseline shows new failures vs Phase 25's `phase25_pre.txt`, STOP and ask user. Pre-existing failures are acceptable; new ones are not.

---

## Hard rules — no exceptions without asking

1. **One file per commit for R-A.** No batching.
2. **No mixing of R-A and R-B in the same commit.**
3. **Never silence an ImportError by re-adding `sys.path`** — diagnose missing editable installs instead.
4. **Never edit YAML manifests, READMEs, or `.qmd` files in a R-A or R-B commit.** Those are separate Wave 1 tasks with their own commits.
5. **Never bypass `Verification gate`.** If gate fails, hard reset, do not patch on top.
6. **Smoke test must remain at 10 passed, 2 skipped after every commit** (the Phase 25 baseline).
7. **Do not edit `rules_runtime_environment.md` or any ADR file** without user confirmation.
8. **No git push** until the user explicitly approves.

---

## Reporting cadence

After every commit:

```
PROGRESS REPORT — Audit Remediation R-A / R-B
Commit: <hash> — <one-line subject>
File touched: <path>
Tests: <result vs baseline>
Smoke: <result vs baseline>
Next step: <id + brief description>
Blockers: [none / describe]
```

After R-A complete (6 commits): 1-line summary post.
After R-B complete: progress report + diff stats.

---

## Stopping conditions — agent halts and asks user

- Any verification gate fails twice on the same step.
- The R-B pre-step diagnostic uncovers callers in unexpected locations (e.g. inside `libs/ingestion/` or `libs/viz_factory/`).
- An import path post-cleanup turns out to require a new editable install (`pip install -e libs/X`) that wasn't already wired up — user confirms before installing.
- The smoke test baseline (10 pass, 2 skipped) regresses by even one test.
- Total LOC change in any single R-A commit exceeds 20 lines (indicates the agent did more than promised).

---

## Out of scope (do NOT touch in this protocol)

- `app/modules/` shiny refactor (audit §4A) — separate protocol needed.
- `utils/` relocation (audit §9) — needs user decision first.
- `@deps` block injection (audit §5) — separate batch protocol.
- Any test under `libs/utils/tests/` or `libs/generator_utils/tests/` is "pre-existing import errors — always exclude" per phase24 protocol §verification gate. Do not try to fix them in this protocol.
