# Quality goals

What the app must get right, in priority order. Each goal is backed by at least one requirement in
`REQ-CORE` (`docs/UML/app.mdj`) with a `Satisfy` link to the component and a `Verify` link to a test.
Checked by `assets/scripts/audit_uml_model.py`.

## 1. Science must be correct

What the user sees and does is what the export contains, and nothing more (`rules_verification_testing.md`
section 9). This is the top goal: a wrong plot or a wrong exported number is worse than a missing feature.

- **REQ-VIZ-EXP-02** Exploration filters are never exported, from any view.
- **REQ-VIZ-EXP-03** Audited steps are always applied to the export of that plot and recorded.
- **REQ-VIZ-EXP-01** If the files or the data changed since the view opened, nothing is exported and
  the user is told why — never export silently from different data than the user looked at.
- **REQ-VIZ-EXP-04** The bundle records the hashes and the keys of each dataset, so a reviewer can
  check what produced it.

## 2. Reproducibility

The same data and the same data analysis recipe give the same picture, every time, on any machine.

- **REQ-VIZ-REPRO-01** The same data and steps give the same rows in the same order (`DataOrchestrator`,
  ADR-090: an action that can reorder rows states its order rule and has a test of it).
- **REQ-VIZ-REPRO-02** The same data gives the same picture — random components (jitter) are seeded by
  default, with an explicit opt-out for a different arrangement.

## 3. A stored result is never served stale

- **REQ-VIZ-DATA-01** A stored stage (Tier 1 or Tier 2 parquet) is served only while its chained
  content key matches the data analysis recipe and the data it was built from (ADR-089). A key
  mismatch removes the stale file rather than serving it — see `STM-STAGE`.

## 4. An audit decision is never silent

- **REQ-VIZ-AUDIT-01** An audited step (a filter, a row exclusion, a column drop) needs a non-empty
  reason before Apply (ADR-085). The reason is part of the record, not a UI formality: it is what makes
  the export report's Methods section meaningful to someone who was not in the room.

## 5. A wrong configuration stops the app, loudly, with the fix

- **REQ-VIZ-CFG-01** A wrong or old configuration (an old launch variable, a renamed key, a hidden
  recipe selector with nothing named) stops the app with a message that names the fix (ADR-077,
  ADR-091, ADR-092: fail-fast over silent suppression). It must never half-start with the wrong data.

## 6. The interface works for every shipped configuration

- **REQ-VIZ-UI-01** Every shipped app features file starts the app and shows HOME without a server
  error. Found and fixed once already (`standalone` and `pipeline-exploration-advanced` both showed a
  blank page, ADR-092) because nothing checked this until `test_every_app_features_starts.py` was
  written.

## What is explicitly not a quality goal yet

Performance at large data sizes, concurrent multi-user access, and security against a hostile user on
a shared deployment are not covered by a requirement today. The last one is a known gap — see
`risks_and_technical_debt.md` and task `SECURITY-DEPLOY-1`.
