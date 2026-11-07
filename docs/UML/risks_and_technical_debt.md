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

Findings F-01 through F-10, F-17 below were all **resolved on 2026-11-07** — fixed in place
(doc text corrected to match code, or code/doc both corrected), proven by the relevant test
suite and `audit_uml_model.py`, each its own commit. Kept here as the lesson, not as open
risk; see `.claude/tasks/uml_findings.md` for what each fix actually was.

| Risk (as found) | Where | Finding |
|---|---|---|
| Test Lab's left sidebar had no dedicated branch and fell through to Home's full panel set | `home_theater.py` | F-01 (resolved) |
| Three different descriptions of where sessions are saved (code, a rule, the UI contract) | `session_manager.py`, `rules_ui_dashboard.md`, `ui_implementation_contract.md` §7.1/13 | F-02 (resolved) |
| Rules contradicted each other on whether `libs/test_lab/` may import a peer domain lib; a dead, undeclared `id_reconciliation` import existed | `rules_runtime_environment.md` §4, `rules_test_lab.md` §8, `scaffolder.py` | F-03, F-17 (resolved) |
| One rule file said both "suppressed silently" and "fatal" for the same Group D cascade | `rules_app_features_flags.md` | F-04 (resolved) |
| Cascade rule 6 claimed a name comparison decides the right sidebar; it's actually the slot registry (ADR-073) | `rules_app_features_flags.md` | F-05 (resolved) |
| T3 scope said "locked to four node types" above a table listing five | `ui_implementation_contract.md` §12a | F-06 (resolved) |
| Deleting an audit node: the contract said two different things (mark inactive vs. remove); nothing in the code ever sets `active: false` — the "disable" feature was designed but never built | `ui_implementation_contract.md` §12c/12g.10, `audit_stack.py` | F-07 (resolved, see task `STM-NODE`) |
| The app structure directory map and ownership matrix listed 5 handlers; 10 exist, and export's real location was wrong | `rules_app_structure.md` §2/§6 | F-08 (resolved) |
| Mandatory read-order pointed at `./AGENT_GUIDE.md`, which does not exist | `workspace_standard.md` §0 | F-09 (resolved) |
| The "official structural standard" data analysis recipe template file did not exist | `rules_data_analysis_recipe_structure.md` §3 | F-10 (resolved) |

Still open:

| Risk | Where | Finding |
|---|---|---|
| `rules_ui_dashboard.md` and deployment guide claim things about IRIDA/Galaxy or a sidebar that the code contradicts | `deployment_guide.qmd`, `irida.py` | F-15 |

## Low: dead or unused code; gaps that are known and already scheduled

| Risk | Where | Task |
|---|---|---|
| IRIDA and Galaxy are not working integrations: `fetch_data` raises `NotImplementedError` / never run there | `libs/connector/src/connector/irida.py`, `galaxy.py` | tracked, not scheduled |
| No Docker release yet; the Dockerfile pins Python 3.12 while development is on 3.14 | `assets/containers/Dockerfile:32` | `DOCKER-RELEASE-1` |
| `help_registry.py` is imported by nothing; `exporter.py` is imported only by tests (the real export report is built in `export_handlers.py`) | import scan of `app/` | `HELP-FROM-DOCS-1` |
| `libs/ingestion` has no `test_*.py`; only debug scripts, so `pytest libs` runs nothing there | `libs/ingestion/tests/` | F-11, `TEST-INGESTION-1` |
| `GalleryViewer.submission_modal_ui()` is defined but called nowhere | `app/modules/gallery_viewer.py:22` | F-18, not yet scheduled |

**Resolved 2026-11-07:** F-18's premise (the app never imports `viz_gallery`, so gallery logic
might be duplicated) checked and found not to be a duplication — `viz_gallery.GalleryManager`
is an offline Pivot-Index maintenance tool (`refresh_gallery.py`), `gallery_viewer.py` only
reads the already-built index. Two different responsibilities, not two copies of the same one.

**Resolved 2026-11-07:** `old_app_entry_legacy.py` (imported `create_ui`/`server_logic`, names
that don't exist — it could never have run) and `connector/adapter_A..D.py`/`adapter_metadata.py`
(stub files whose own `@deps` block claimed importers that didn't actually import them) were
confirmed as genuinely dead — zero real importers — and deleted. F-12.

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
