VERDICT: merge. No blocker. Two findings (one worth a follow-up task, one a text fix) are listed below.

Proof the worktree code ran: a temporary test inside the worktree printed `validate_runner.py` and `utils/__init__.py` under `.claude/worktrees/validate-interpreter/...`. The same held with `PYTHONPATH=.`. I removed that test file. `git status` is clean in the worktree.

1. Layering and leftovers: OK.
- `validate_runner.py` and `error_notice.py` have no Shiny import (grep found none). The module imports only os, subprocess, sys, pathlib and `app.modules.error_notice`.
- The handler has no `import subprocess` and no `.venv/bin/python` left. The only remaining "subprocess" hits are comments and the @deps text (`blueprint_handlers.py:23, 2854, 2958`). The call site is `blueprint_handlers.py` around line 2989.

2. Child environment: right for a normal install and a worktree, with one limit.
- `child_env` puts the checkout root and `REPO/libs/*/src` first, and the caller's PYTHONPATH last (`validate_runner.py:41-46`).
  - Worktree: this is needed. In a plain probe without PYTHONPATH, `utils` imported from the MAIN checkout's `libs` through the editable installs. The prepend makes the child use the worktree's libs, the same as the app.
  - Normal install: the paths are the same as the editable installs, so there is no difference.
- A container without `libs/*/src` gives an empty glob. Then only `REPO` and the inherited PYTHONPATH apply, so packages come from site-packages and nothing is shadowed wrongly.
- The parent's full `os.environ` passes to the child. The child is our own script on the same machine, so I found no harm.
- Working folder `cwd=REPO` is right. The script joins a relative recipe path to its own project root (`audit_data_analysis_recipe_coherence.py:~578`), not to the current folder.
- Finding F1 (medium, not caused by this change): the script's `find_project_root` (`:516`) looks for `CLAUDE.md` or `.venv` upward. A container with neither falls back to `scripts/` as the project root, so the libs paths under it would not exist. I did not run this case. The script's own behaviour is unchanged by this diff.

3. Security: no injection.
- The command is a list with no shell (`validate_runner.py:~47`).
- A path starting with `-` (`-evil.yaml`, `--skip-join`) gave exit code 2, argparse "expected one argument", and the "could not run" message. It is not read as an option and nothing runs. A path with spaces and unicode works: `tmpAI/sp ace é/-r é.yaml` gave PASS, also with a `./` prefix.
- Finding F2 (low): the dash case gives the Suggestion "the app installation is incomplete", which is wrong for that cause. The real handler passes a path that exists, so this is rare.

4. The three "could not run" cases, reproduced headless:
- Cannot start: "(FileNotFoundError: [Errno 2] ... '/nonexistent/py'). Suggestion: check that the app was installed completely ...".
- Timeout: "(timed out after 1 seconds). Suggestion: run Validate again; ...".
- Unreadable output: exit code 3 with stderr "boom" is reported with the reason. Exit code 0 with no report says "it printed no report".
- Every message says "could not run, so the recipe was neither passed nor failed" and has the reason and "Suggestion:". The panel box is built in `bp_validate_ui` and returns before the PASS/FAIL code. The result carries `could_not_run`, `checks: []` and `pass: False`.
- Regression: a recipe with an unknown action and component inside the checkout gave `## Result: ❌ FAIL`, so a real fail still shows FAIL. A shipped recipe gave PASS.
- Finding F3 (medium): a recipe outside the checkout (I tested a temp folder) makes the script crash with `ValueError ... is not in the subpath of <repo>`. The panel now says "could not run", which is true and better than the old silent FAIL. But the Suggestion ("installation incomplete") is misleading. If uploaded or user-folder recipes can be selected in `stored_data_analysis_recipe_selector`, this will show. I did not check where the selector paths come from. Suggestion: a follow-up task to make the script accept an absolute path outside its root, or to say so in the message.
- I did not drive the panel in a browser for the three failure cases. I checked the rendering code by reading it.

5. Guard `test_source_no_venv_path.py`: it can fail, with a limit.
- Break once: I changed `sys.executable` back to `".venv/bin/python"` in `validate_runner.py`. Three tests failed (the command test, `test_runs_from_a_folder_without_venv` and the guard). I restored the file with `git checkout`.
- The ALLOWED list is justified. Both entries match real lines: `main.py:40` and `CONVERT_HINT` at `gallery_manager.py:43`. A grep of app and libs source found no other `.venv/bin/python`.
- Limit: the guard matches only the exact text `.venv/bin/python`. It does not catch `python3`, `.venv/bin/pytest`, or a path built with `Path`.
- Finding F4 (low, not a blocker): the banner `print(f"Venv: ./.venv/bin/python")` at `app/src/main.py:40` is false in a worktree or container. It should say `sys.executable`. It sits in ALLOWED, so correcting it later needs the ALLOWED entry removed too.

6. Test runs, all from the worktree:
- `TestBlueprintEscapeAndValidate` with `SPARMVET_APP_FEATURES=qa`: 7 passed.
- Whole `test_shiny_smoke_blueprint.py` with qa: 17 passed.
- The two new files: 9 passed (7 + 2).
- Headless `app/tests` files that name blueprint or validate, plus the two new files: 76 passed, 0 failed.

7. Facts for Eve on the rule versus the code:
- `rules_runtime_environment.md` section 5 says the interpreter path MUST come from the deployment file and be fetched through the Bootloader, not hardcoded.
- `Bootloader.get_python_path()` is at `app/src/bootloader.py:819`. It reads `runtime.python_interpreter` and raises KeyError if it is missing.
- A grep over app, libs, scripts and assets finds no caller. The only mention is a hint text in `scripts/audit_hardcoded_config.py:108`.
- Shipped deployments set the relative `"./.venv/bin/python"`: `deployment_template.yaml:88`, `local/retest.yaml:26`, `pipeline_test/pipeline_test.yaml:35`, `demo/web-demo.yaml:25`, `local/local.yaml:31`, `demo/demo-vetinst.yaml:29`. `connect/connect_template.yaml:61` sets `"python"`.
- The builder used `sys.executable`, which differs from the rule's wording. I did not judge the rule.

Not checked: a real container or server install; the browser panel for the three "could not run" cases; the full test suite; `export_handlers.py` and `agent_adapter.py`, which start `quarto`, `git` and `claude` by PATH name (I did not check those; the builder left them as PATH tools).
