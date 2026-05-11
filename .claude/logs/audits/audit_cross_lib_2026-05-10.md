Status: PROCESSED 2026-05-11 — 0 tasks created, 0 false positives, 1 acceptable debt noted (existing tech debt)

# Audit Report: ADR-011 Cross-Lib Violation Scan
Generated: 2026-05-10T23:00:50
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-011 / ADR-016 — Two-Tier Dependency Model

## Result: ⚠️ KNOWN DEBT ONLY

- New violations (blockers): 0
- Known tech-debt violations: 1

## ⚠️ Known Tech-Debt Violations (tracked, do not expand)

- `libs/transformer/src/transformer/pipeline.py:20` — `transformer` → `ingestion` (`ingestion.ingestor`)

These are tracked in tasks.md. Do not add new violations to this category.

## References
- `.claude/rules/rules_runtime_environment.md §4` — Two-Tier Dependency Model
- `.claude/knowledge/architecture_decisions.md` ADR-011, ADR-016
- `.claude/tasks/tasks.md` — `ADR-011 cross-lib violations` tech-debt block