# Other hardcoded interpreter paths (outside app/ and libs/*/src). Report only. For Eve to decide.

Lines read in the worktree one-python (c6c4947f plus this fix).

| file:line | what it writes | who runs it | what would change with the running interpreter |
|---|---|---|---|
| scripts/audit_package_deps.py:353 | python_bin = root/.venv/bin/python; children at :111, :127, :160 (pip list, pip list --outdated, pip check); hint text :313-328 | a person (audit), or validate_runner via sys.executable | The audit would query the Python that started it, which is already the venv Python when started as the hint says. The .venv existence check would fall away. |
| scripts/audit_library_tests.py:312 | python_bin; children :89 (pytest), :109 (suite) | a person | Same: tests would run in the starting interpreter. |
| scripts/audit_data_analysis_recipe_integrity.py:144 | python_bin; child :53 (assembler); error text :149 | a person | Same. |
| scripts/audit_app_features_flags.py:117 | python_bin; child :41 (validate script); error text :121 | a person | Same. |
| scripts/audit_parity_coverage.py:393 | python_bin; children :112, :122, :151, :165 (-c snippets for plotnine and polars) | a person | Same. Versions reported would be those of the starting interpreter. |
| scripts/run_audits.sh:16 | PYTHON=root/.venv/bin/python, used :47 for every audit; check :23-24 | a person | A shell script cannot use sys.executable; it would need the caller to name the Python. |
| assets/scripts/retest_walkthrough.py:140 | starts the app with REPO/.venv/bin/shiny (a venv binary, not python) | a person | It would start `sys.executable -m shiny run ...` in the same Python. |
| assets/scripts/bundle_connect.sh:25 | PYTHON="./.venv/bin/python" | a person (Posit Connect bundle) | Same as run_audits.sh. |
| assets/containers/Dockerfile:32, :89 | FROM python:3.12-slim; CMD ["python", "-m", "shiny", ...] | podman/docker build and run | In a container the image Python is the only one; the bare word is correct there. Deferred earlier. |
| scripts/install_libs.sh:17 | text: python -m venv .venv && .venv/bin/pip install | a person (printed hint) | Text only. |
| scripts/audit_hardcoded_config.py:108-112 | regex patterns that look for python3 in subprocess | a person (audit) | They are patterns, not interpreter use. Text at :236 corrected in this task. |
| libs/*/tests/*.py and scripts/*.py docstrings | usage lines such as "PYTHONPATH=. ./.venv/bin/python -m pytest ..." (dozens of files) | a person reads them | Text only; no process is started. |
| app/tests/test_source_no_venv_path.py:39, test_browser_tests_no_venv_path.py:41 | the old forms inside test strings | the tests themselves | They are test data for the guard. |

No test starts a child process with a hardcoded interpreter (grep of subprocess lines in app/tests, libs/*/tests).
