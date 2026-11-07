# Risks and technical debt

Known problems with the app and its documents, sorted by what they could cost if ignored. Most come
from `.claude/tasks/uml_findings.md`, built while modelling; this page is the short, sorted summary.
The register has the full detail and the evidence for each.

## High: could produce a wrong result or a security hole

| Risk | Where | Task |
|---|---|---|
| Data analysis recipe text runs as Python via `eval()` with few limits; the app has no login | `expressions.py:221`, `geoms/core.py:1335`, `id_reconciliation/core.py:239` (F-13) | `SECURITY-DEPLOY-1` |
| 61 outdated packages, 11 with a major update (polars 1.40 → 2.1, pyarrow, pillow...); polars and plotnine are under parity mandates (ADR-035§ parity, ADR-036) | `audit_package_deps.py` | `DEPS-REVIEW-1` |

## Medium: wrong or contradictory documentation, likely to mislead the next person

| Risk | Where | Finding |
|---|---|---|
| Three different descriptions of where sessions are saved (code, a rule, the UI contract) | `session_manager.py`, `rules_ui_dashboard.md`, `ui_implementation_contract.md` §7.1/13 | F-02 |
| Rules contradict each other on whether `libs/test_lab/` may import a peer domain lib, and its declared dependencies don't match `pyproject.toml` | `rules_runtime_environment.md` §4, `rules_test_lab.md` §8 | F-03, F-17 |
| One rule file says both "suppressed silently" and "fatal" for the same Group D cascade | `rules_app_features_flags.md` | F-04 |
| Cascade rule 6 claims a name comparison decides the right sidebar; it's actually the slot registry (ADR-073) | `rules_app_features_flags.md` | F-05 |
| T3 scope says "locked to four node types" above a table listing five | `ui_implementation_contract.md` §12a | F-06 |
| Deleting an audit node: the contract says two different things (mark inactive vs. remove); unclear what sets `active: false` in practice | `ui_implementation_contract.md` §12c/12g.10 | F-07 |
| The app structure directory map and ownership matrix list 5 handlers; 10 exist, and export's real location is wrong | `rules_app_structure.md` §2/§6 | F-08 |
| Mandatory read-order points at `./AGENT_GUIDE.md`, which does not exist | `workspace_standard.md` §0 | F-09 |
| The "official structural standard" data analysis recipe template file does not exist | `rules_data_analysis_recipe_structure.md` §3 | F-10 |
| `rules_ui_dashboard.md` and deployment guide claim things about IRIDA/Galaxy or a sidebar that the code contradicts | `deployment_guide.qmd`, `irida.py` (F-15); `testlab_standard_left.yaml` vs issue #33 (F-01) | F-15, F-01 |

## Low: dead or unused code; gaps that are known and already scheduled

| Risk | Where | Task |
|---|---|---|
| IRIDA and Galaxy are not working integrations: `fetch_data` raises `NotImplementedError` / never run there | `libs/connector/src/connector/irida.py`, `galaxy.py` | tracked, not scheduled |
| No Docker release yet; the Dockerfile pins Python 3.12 while development is on 3.14 | `assets/containers/Dockerfile:32` | `DOCKER-RELEASE-1` |
| `help_registry.py` is imported by nothing; `exporter.py` is imported only by tests (the real export report is built in `export_handlers.py`) | import scan of `app/` | `HELP-FROM-DOCS-1` |
| Possibly dead code with no importer found: `old_app_entry_legacy.py`, `connector/adapter_A..D.py`, `adapter_metadata.py` | as named | F-12, not yet scheduled |
| `libs/ingestion` has no `test_*.py`; only debug scripts, so `pytest libs` runs nothing there | `libs/ingestion/tests/` | F-11, not yet scheduled |
| The app never imports `viz_gallery`; Gallery logic may be duplicated between `app/modules/gallery_viewer.py` and the library | import scan, `PKG-TIERS` | F-18, not yet scheduled |

## A structural risk, not a bug

`blueprint_handlers.py` plus `wrangle_studio.py` together are roughly 5,100 lines — by far the largest
part of the app (`C4-COMP-APP`). No single bug is known there, but it is the part most likely to hide
one, and the part most expensive to change safely. Worth a closer look before any large BLUEPRINT
change.

## Already fixed, kept here as the lesson

- **ADR-037 never existed.** Cited by number in 4 files since 2026-04-19; traced with
  `git log --all -S` to a commit whose own message claimed the ADR was "established" and its links
  "verified," with no heading ever written. A citation is not evidence that the thing exists — this
  is why `audit_uml_model.py` checks every `adr` tag against a real heading, not against another
  document's say-so (F-21, resolved).
- **A blank page in two app features files** (`standalone`, `pipeline-exploration-advanced`) because a
  shared state object was gated on the wrong flag — found only once every shipped app features was
  actually started in a browser test (ADR-092).
