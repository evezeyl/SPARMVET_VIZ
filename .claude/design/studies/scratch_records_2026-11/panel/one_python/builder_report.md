# One Python (D-0263): builder report

Commit: c6c4947f on task/one-python (one commit). No push, no merge.

## What the operator sees now (first)
- A deployment file with `runtime: python_interpreter:` no longer starts. The app stops at startup with: "The deployment key 'runtime.python_interpreter' was removed: nothing read it. The app uses the Python that runs it, and every child process it starts uses the same Python (sys.executable)." Fix line: "Delete the key 'runtime.python_interpreter' from <file>." (same DeploymentError form as the ADR-091 renamed keys).
- The five shipped deployment files and the two templates no longer carry the key. Nothing else changes for the user.

## Child processes (table; all read, none ran Python by path)
| file:line | starts | interpreter / how found |
|---|---|---|
| app/handlers/export_handlers.py:89, :96 (`_sp.check_output`) | `git rev-parse`, `git describe` | not Python; `git` found on PATH |
| app/handlers/export_handlers.py:1964 (`_sp.run`) | `quarto render` | not Python; `quarto` found on PATH. Listed, not changed |
| app/handlers/export_handlers.py:1152 | `shutil.which("rsvg-convert")` only (lookup) | PATH |
| app/modules/bundle_importer.py:90 | `git rev-parse` | not Python; PATH |
| app/modules/validate_runner.py:47,53 | `scripts/audit_data_analysis_recipe_coherence.py` | `sys.executable` (built 2026-11-17) |
| libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:156,177,284 | the `claude` CLI | not Python; `ClaudeCliAdapter.BINARY` on PATH |
| assets/scripts/*.py (audit_old_words, check_doc_links, rename_vocabulary) | `git` | not Python; offline developer scripts, not called by the app |
No hit for `Popen`, `os.system`, `os.exec`, `multiprocessing`, `runpy`, or a bare `python`/`python3` in a process call in `app/` and `libs/` sources. Finding: none needed a change to `sys.executable`. Note: `Bootloader.get_python_path()` read the key but had NO caller; it is deleted. `export_handlers.py:104` only records `sys.version` (no process).
Quarto: if it runs Python cells it picks its own Python; the app uses `--no-execute`, so no Python starts there.

## Rule section before / after (`.claude/rules/rules_runtime_environment.md` section 5; nothing else changed in the file)
Before:
- The path to the active Python interpreter MUST be defined in the deployment file in config/deployment/ (e.g., `runtime: {python_interpreter: "./.venv/bin/python"}`).
- UI components and scripts MUST fetch this path via the Bootloader rather than hardcoding environment-specific strings.

After:
- The Python that runs the app is the only interpreter.
- Any child process the app starts that runs Python uses `sys.executable`. No code names a path such as `./.venv/bin/python` or the bare word `python` for this.
- A deployment file has no `python_interpreter` key (removed 2026-11-18, D-0263). The app refuses a deployment file that still has it and says to delete it.

## Files changed
Config: config/deployment/{demo/demo-vetinst,demo/web-demo,local/local,local/retest,pipeline_test/pipeline_test}.yaml; templates/deployment_template.yaml; connect/connect_template.yaml (had `python_interpreter: "python"`, a bare python word; also removed). Code: app/src/bootloader.py (get_python_path removed), app/modules/renamed_keys.py (REMOVED_DEPLOYMENT_KEYS + refusal, wired through `renamed_deployment_key_errors`, no new call site), libs/utils/src/utils/path_expansion.py (PATH_KEYS entry), assets/scripts/create_test_deployment.py (stopped writing the key), scripts/audit_hardcoded_config.py (messages now say sys.executable). Docs: docs/deployment/deployment_guide.qmd, docs/workflows/connector.qmd, docs/reference/environment_variables.qmd. Rule: .claude/rules/rules_runtime_environment.md. Tests: app/tests/test_python_interpreter_key_removed.py (new), app/tests/test_source_no_venv_path.py (extended).
`@deps`: no interface change that a `@deps` block lists (get_python_path was in none; checked by grep).

## Tests
- Targeted: 151 passed (path_expansion, app_features_validator, recipe_validator, browser_tests_no_venv_path, new key test, source guard, shipped deployments, renamed keys, bootloader launch/store, validate_runner).
- `test_every_app_features_starts.py`: 9 passed (1 min 45 s) = the app starts under every shipped app features.
- `from app.src.main import app` prints OK.
- The wide run (`libs/utils app/tests` without browser files) did not finish in 11 minutes (slow or a hung test, machine shared with another session's run); I killed it (my PID 62447). Not a pass: the full headless baseline is NOT shown by me. The reviewer should run it.
- New tests: every deployment YAML under config/deployment lacks the key and a `runtime` block (7 files); a dict with the key gives one DeploymentError with plain text; without the key none; the Bootloader exits on a deployment copy with the key; get_python_path is gone; source guard: no bare `python`/`python3` (also `/usr/bin/python`, `/usr/bin/env python`) in a process call in app/ and libs/ sources, multi-line calls included, plus a self-test of the guard.
- Break once: (1) added the key back to local.yaml: the app refused to start, the new test and shipped-deployment test could not run (INTERNALERROR SystemExit 1 from the refusal); restored. (2) changed bundle_importer.py:90 to `["python3", ...]`: the guard first MISSED it (call split over two lines), I fixed the regex to scan the whole text, then it failed as expected; restored (git diff of that file empty).

## Decisions table
| Decision | How complied | file:line / test |
|---|---|---|
| D-0263 one Python, sys.executable | no process starts Python by path; key removed from 5 files (+2 templates); rule text changed as she decided; other paths checked and listed | table above; test_source_no_venv_path.py; test_python_interpreter_key_removed.py |
| D-0050 no silent error | an old file with the key is refused loudly, not ignored | app/modules/renamed_keys.py `removed_deployment_key_errors`; test_the_app_refuses_to_start_with_the_key |
| D-0165 report needed missing decisions | see open items | below |

## Task line for the scribe (tasks.md)
- [ ] **ONE-PYTHON-TOMBSTONE-1** `[haiku/low]`: delete `REMOVED_DEPLOYMENT_KEYS` / `removed_deployment_key_errors` in `app/modules/renamed_keys.py` and its tests in `app/tests/test_python_interpreter_key_removed.py` when the tombstone expires. Expiry written in the code comment as "Phase 42" (PROVISIONAL, see below).
- Deferred container task (Dockerfile untouched): `assets/containers/Dockerfile:32` is `FROM python:3.12-slim` and line 4 says "Python 3.12", while the project is Python 3.14 (`rules_toolchain.md`). Line 89: `CMD ["python", "-m", "shiny", ...]` is the container's own entry command (not an app child process; the container Python runs the app). Task text: update the image to the project's Python version when container testing starts.

## PROVISIONAL choices / open for Eve (not decided by me)
- Tombstone expiry "Phase 42" (rules_legacy_management wants an expiry after two phases; no current phase number is stated in my files). Eve or the coordinator should confirm.
- The refusal is FATAL (app stops), like the other renamed deployment keys. Eve's message said "refused or reported"; I followed the existing ADR-091 way. A softer notice would be a different choice.
- ADR text still names the key: `.claude/knowledge/architecture_decisions.md:1102-1103` (ADR-048 example block shows `runtime: python_interpreter`). I did not touch ADR text (brief). Needs a historical marker or an amendment by whoever owns ADRs.
- `.claude/knowledge/project_conventions.md` does not name the key (grep: no hit); no change.
- Old logs/tasks/archives mention the key; left as history.

## Not done
- Dockerfile untouched. No ADR, pyproject, CI, settings, CLAUDE.md edits. tasks.md not edited. Full headless baseline not completed (above).
