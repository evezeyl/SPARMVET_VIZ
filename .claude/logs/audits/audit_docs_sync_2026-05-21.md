Status: PROCESSED
# Audit Report: Documentation and README Sync
Generated: 2026-05-21T16:09:57
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: docs_documentation_aesthetics.md §1 — Code-Documentation Synchronization Mandate

- README coverage violations: 0
- @deps documents: broken links: 1
- Doc backtick path violations: 15
- Violet Law stale references: 5
- **Total violations: 21**

## Result: ❌ FAIL

## ✅ README Coverage — No violations

## ❌ @deps documents: Links

- **`.claude/rules/rules_ui_dashboard.md`**
  @deps `documents:` references missing file: `libs/utils/src/utils/blueprint_mapper.py`
  *Fix: Update the `documents:` entry in the @deps block to point to the correct (current) file path.*

## ❌ Doc Backtick File Paths

- **`docs/deployment/deployment_guide.qmd`**
  Backtick path not found on disk: `config/connectors/local/local_connector.yaml`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/foundations/verification_protocol.qmd`**
  Backtick path not found on disk: `libs/transformer/tests/data/{{ACTION_NAME}}_manifest.yaml`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/reference/development_rules.qmd`**
  Backtick path not found on disk: `tests/{lib}_integrity_suite.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/reference/development_rules.qmd`**
  Backtick path not found on disk: `libs/ingestion/adapters_?.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/reference/development_rules.qmd`**
  Backtick path not found on disk: `config/manifests/species/species_X.yaml`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/reference/testing.qmd`**
  Backtick path not found on disk: `libs/{lib}/tests/debug_{component}.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/reference/testing.qmd`**
  Backtick path not found on disk: `libs/{lib}/tests/{lib}_integrity_suite.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/reference/testing.qmd`**
  Backtick path not found on disk: `assets/scripts/create_test_data.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/vision/platform_evolution.qmd`**
  Backtick path not found on disk: `docs/vision/gallery.qmd`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/workflows/audit_scripts.qmd`**
  Backtick path not found on disk: `app/handlers/foo.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/workflows/audit_scripts.qmd`**
  Backtick path not found on disk: `docs/**/*.qmd`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`docs/workflows/blueprint_architect.qmd`**
  Backtick path not found on disk: `config/manifests/pipelines/{slug}.yaml`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`libs/viz_factory/README.md`**
  Backtick path not found on disk: `tests/test_deco2_components.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`libs/viz_factory/README.md`**
  Backtick path not found on disk: `tests/test_data/{name}_test.yaml`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*
- **`libs/viz_factory/README.md`**
  Backtick path not found on disk: `tests/test_*.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*

## ❌ Violet Law Stale References

- **`docs/appendix/FAQ.qmd`**
  Violet Law reference `GalleryMaterializer (materialize_manifest_plots.py)` — `materialize_manifest_plots.py` not found under libs/ or app/
  *Fix: Update `ClassName (filename.py)` to use the current filename. Violet Law applies to human-facing .qmd files only — not code.*
- **`docs/reference/development_rules.qmd`**
  Violet Law reference `ClassName (filename.py)` — `filename.py` not found under libs/ or app/
  *Fix: Update `ClassName (filename.py)` to use the current filename. Violet Law applies to human-facing .qmd files only — not code.*
- **`docs/workflows/audit_scripts.qmd`**
  Violet Law reference `ClassName (filename.py)` — `filename.py` not found under libs/ or app/
  *Fix: Update `ClassName (filename.py)` to use the current filename. Violet Law applies to human-facing .qmd files only — not code.*
- **`docs/workflows/dashboard_app.qmd`**
  Violet Law reference `Polars (transformer.py)` — `transformer.py` not found under libs/ or app/
  *Fix: Update `ClassName (filename.py)` to use the current filename. Violet Law applies to human-facing .qmd files only — not code.*
- **`docs/workflows/visualisation_factory.qmd`**
  Violet Law reference `ClassName (file_name.py)` — `file_name.py` not found under libs/ or app/
  *Fix: Update `ClassName (filename.py)` to use the current filename. Violet Law applies to human-facing .qmd files only — not code.*

## References
- `rules_documentation_aesthetics.md §1` — Code-Documentation Synchronization Mandate
- `rules_documentation_aesthetics.md §3` — The Violet Law
- `workspace_standard.md §5` — @deps annotation format
- Routine 9 (Documentation sync) in `.claude/workflows/audit_routine_registry.md`