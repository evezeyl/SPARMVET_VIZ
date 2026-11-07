# Toolchain (rules_toolchain.md)

**Authority:** the tools a collaborator, an agent or a CI runner needs to build, test and document SPARMVET_VIZ,
what each is for and how to call it. It does not depend on any personal setup. Personal tools (mail, reference
managers, issue trackers, personal plugins) are out of scope.

Checked on Fedora 43 on 2026-11-07. Versions are the ones that were used; the minimum is what `pyproject.toml` declares.

| Tool | Used for | How to call it | Needed by |
|---|---|---|---|
| Python 3.14 in `./.venv` | The only interpreter (`rules_runtime_environment.md` section 1); never the system Python | `./.venv/bin/python ...` | everything |
| `uv` 0.11 | Create the environment and install packages | `uv venv .venv --python 3.14`, then `uv pip install -e ".[test]"` | first setup |
| `scripts/install_libs.sh` | Install every `libs/*` package as editable (no `sys.path` hacks, ADR-011/016) | `./scripts/install_libs.sh` once after cloning and after adding a lib | first setup |
| `pytest` 9 | Headless tests | `PYTHONPATH=. ./.venv/bin/python -m pytest libs app/tests --ignore=... -q` (exact commands: `rules_verification_testing.md` section 8) | every change |
| Playwright 1.5x with Chromium | Browser tests of the Shiny app (`qa` app features) and the retest walkthrough | `./.venv/bin/playwright install chromium` once; then the browser command of `rules_verification_testing.md` | UI changes |
| `shiny` | Run the app | `PYTHONPATH=. SPARMVET_DEPLOYMENT=... SPARMVET_APP_FEATURES=... ./.venv/bin/shiny run app/src/main.py --port 8000` (variables: `docs/reference/environment_variables.qmd`) | running |
| Quarto 1.8 | Render `docs/` and the export report (`report.qmd`) | `quarto render docs --no-execute` (executing cells needs jupyter and nbformat in the venv, which are not installed) | documentation, export |
| `git` 2.5x, `gh` 2.8x | History, branches, pull requests, issues on GitHub | `git ...`, `gh pr ...`, `gh issue ...` | all |
| `podman` 5 (or `docker`) | Build and test the container image | `podman build -f assets/containers/Dockerfile .`; Posit Connect bundle: `assets/scripts/bundle_connect.sh` | deployment |
| Audit scripts | Scheduled hygiene checks | `./scripts/run_audits.sh all`; single ones: `./.venv/bin/python scripts/audit_<name>.py --project-root .` | before a merge |
| `assets/scripts/audit_old_words.py` | Retired configuration words (ADR-091, ADR-092) | `./.venv/bin/python assets/scripts/audit_old_words.py --check` | before a merge |
| `assets/scripts/check_launch_commands.py`, `check_doc_links.py` | Documented launch commands start; documented paths exist | `./.venv/bin/python assets/scripts/check_launch_commands.py README.md ...` | documentation changes |

## Not installed (pending)

| Tool | Why it would be needed | Task |
|---|---|---|
| Mermaid CLI (`mmdc`) | Render diagrams outside Quarto; Quarto renders Mermaid itself for the docs | none yet |
| StarUML | UML, SysML and C4 diagrams | pending TOOLS-UML-1 |
| `ruff` | Lint and format; the configuration in `pyproject.toml` is commented out | none yet |

## Rules

- A new tool is added here with what it is for and how it is called, in the same commit that starts to use it.
- Commands in this file are checked: a documented command that does not run is a defect (`check_launch_commands.py`).
