# Audit findings of 2026-11-07 that the rename did not cause: plan (CONFIG-AUDIT-FIXES-1)

Source: the scheduled audit scripts in `scripts/`, run on `rename/config-vocabulary` after ADR-092
(output kept in `tmpAI/rename/audits/`, not committed). Each step is one small commit with a green test run;
rerun the named audit after each step.

| # | Finding | Fix | Check | Tag |
|---|---|---|---|---|
| 1 | `libs/viz_factory/src/viz_factory/viz_factory.py` has no `@deps` block (`audit_deps_verify`) | Add the block (provides: the `VizFactory` render contract, consumes: plotnine, polars, `utils`, consumed_by: `app/handlers/home_theater.py`, `app/handlers/export_handlers.py`, `app/src/server.py`, tests), then run `build_dep_graph.py` | `audit_deps_verify.py` exits 0 | `[haiku/low]` |
| 2 | 14 backtick paths in docs point to files that do not exist (`audit_docs_sync`). About 10 are placeholders or examples: `{lib}`, `{{ACTION_NAME}}`, `foo.py`, `docs/**/*.qmd`, `{slug}`, `tests/test_*.py`, `adapters_?.py` | Teach the audit to skip paths that contain `{`, `*`, `?` or sit in a fenced example; do not edit the docs for these | the count drops to the real ones | `[sonnet/low]` |
| 3 | Real broken references: `assets/scripts/create_test_data.py` (`docs/reference/testing.qmd`), `docs/vision/gallery.qmd` (`docs/vision/platform_evolution.qmd`) | Point to the script that exists (`create_data_analysis_recipe.py` / `libs/test_lab`) or remove the sentence; create or drop the gallery page link | `audit_docs_sync.py` | `[sonnet/low]` |
| 4 | 5 stale Violet Law references: `GalleryMaterializer (materialize_data_analysis_recipe_plots.py)` in `FAQ.qmd`, `Polars (transformer.py)` in `dashboard_app.qmd`, and 3 example names (`ClassName (filename.py)`) | Use the real class and file; skip the example pattern in the audit | `audit_docs_sync.py` | `[sonnet/low]` |
| 5 | Task `TOOLS-TOOLCHAIN-1` names `.claude/rules/rules_toolchain.md`, which does not exist (`audit_task_drift`) | Create the file (tools needed to build and run SPARMVET_VIZ: uv, Python version, Quarto, Playwright browsers, podman) or mark the task deferred in `tasks.md` | `audit_task_drift.py` | `[sonnet/low]` |
| 6 | `config/data_analysis_recipes/templates/complex_template.yaml` does not load: no `analysis_groups:` block (found by the new id check). No test loads the templates | Add an `analysis_groups:` block with one plot; add a test that every template validates (`validate_data_analysis_recipe`) | the new test passes and fails when the block is removed | `[sonnet/medium]` |
| 7 | `scripts/audit_palette_registry.py` does not accept `--project-root`, unlike its siblings | Add the argument (or document that it has none) | `run_audits.sh all` | `[haiku/low]` |
| 8 | 61 outdated packages, 11 major (polars 1.40 to 2.1, pyarrow, pillow ...) (`audit_package_deps`) | Not a rename matter: a separate dependency review, polars 2 first (ADR-035 parity audit) | own task | `[opus/medium]` |

Order: 1, 3, 4, 5, 6 (small and real), then 2 and 7 (audit tooling), 8 later.
