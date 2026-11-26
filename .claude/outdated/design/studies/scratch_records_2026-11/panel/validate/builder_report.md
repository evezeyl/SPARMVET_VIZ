DONE. Commit d4e24bca on task/validate-interpreter. Worktree: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/worktrees/validate-interpreter

CHANGES
- New app/modules/validate_runner.py (headless, no Shiny, has @deps).
  - The child starts with sys.executable (line 47, structure_check_command).
  - The script path comes from the location of the code: REPO/scripts/audit_data_analysis_recipe_coherence.py. The child's cwd is REPO.
  - The child env sets PYTHONPATH to REPO plus this checkout's libs/*/src. The caller's PYTHONPATH is kept after them, as in app/tests/subprocess_env.py. Without this, the child in a worktree would import the main checkout's libs through the editable installs.
  - run_structure_check() raises StructureCheckError when the child cannot start (OSError), times out, or prints no "## Result:" report (it gives the exit code and the stderr tail). The text is built with app/modules/error_notice.notice, so it has the "what, reason, Suggestion:" form.
  - could_not_run_result() builds the panel content.
- app/handlers/blueprint_handlers.py:
  - Removed `import subprocess` and the call with ".venv/bin/python" (old lines ~2975-2976). _handle_validate now calls run_structure_check and, on StructureCheckError, stores could_not_run_result and shows an error toast of 15 s.
  - bp_validate_ui now renders a distinct amber box titled "Validation could not run" with the text, and no PASS/FAIL. A recipe that fails the checks still shows FAIL.
  - @deps consumes line added.
- New tests, all headless:
  - app/tests/test_validate_runner.py (7 tests): command uses sys.executable; runs from a folder with no .venv and no scripts/; PYTHONPATH names this checkout; missing interpreter; timeout; unreadable output; panel content.
  - app/tests/test_source_no_venv_path.py (2 tests): the guard on app/ and libs/*/src. It has an explicit ALLOWED list with a reason per entry.

MESSAGE THE USER NOW SEES (what, reason, Suggestion; the reason in brackets varies)
"The structure check of the recipe could not run, so the recipe was neither passed nor failed (FileNotFoundError: [Errno 2] No such file or directory: ...). Suggestion: check that the app was installed completely (the file scripts/audit_data_analysis_recipe_coherence.py and the Python that runs the app), then run Validate again"
- Timeout: "... (timed out after 30 seconds). Suggestion: run Validate again; if it keeps timing out after 30 seconds, check the recipe for a very large include or ask the person who runs the app"
- Unreadable output: "... (the check ended with code N and no readable report: <stderr tail>). Suggestion: read the reason and fix it; if it names a missing package, the app installation is incomplete"

VERIFIED
- TestBlueprintEscapeAndValidate, run from the worktree with SPARMVET_APP_FEATURES=qa and no PYTHONPATH: 7 passed, 10 deselected. This includes the two target tests. I ran it twice, the second time without PYTHONPATH.
- Headless app/tests files named *blueprint* or *validat*, excluding smoke: 89 passed, 1 xfailed.
- app/tests/test_imports_from_checkout.py: passes, with test_validate_runner and test_source_no_venv_path (21 passed together).
- Break-once: I set the interpreter back to ".venv/bin/python". 3 tests failed: the command test, runs_from_a_folder_without_venv, and the guard. I restored it, and all pass again.

SWEEP of app/ and libs/*/src (not tests, docs or assets/scripts)
- FIXED (the same defect, a hardcoded project interpreter): blueprint_handlers.py:2975 only.
- LEFT, not this defect:
  - app/handlers/export_handlers.py:1911 starts `quarto render`. A PATH tool, and its failure already gives a message with "Suggestion: install Quarto".
  - app/handlers/export_handlers.py:~90 and app/modules/bundle_importer.py:45 call `git`, as a PATH tool.
  - libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:156,177,284 starts the `claude` CLI, as a PATH tool.
  - app/src/main.py:40 prints "Venv: ./.venv/bin/python" in the start-up banner. Text only, and false in a worktree. It is in the guard's ALLOWED list.
  - libs/viz_gallery/src/viz_gallery/gallery_manager.py:43 CONVERT_HINT is a command text shown to a person. It is in ALLOWED.
  - aqua_synthesizer.py:7 and excel_handler.py:1 have a `#!/usr/bin/env python3` shebang only.
  - No hit for Rscript in app or libs source.
  - `python3` appears nowhere else.

RULE vs CODE DISAGREEMENT (not edited)
- rules_runtime_environment.md section 5 says the interpreter path comes from the bootloader. Bootloader.get_python_path() (app/src/bootloader.py:819) returns deployment runtime.python_interpreter. Every shipped deployment sets it to "./.venv/bin/python" (relative), except connect_template, which sets "python".
- Nobody calls get_python_path(). Using it would reproduce this defect, so I used sys.executable. The rule and the deployment values need Eve's decision, or a rule amendment.
- The bootloader's project_root is optional, comes from the deployment and may be None. So I resolved the script from the code location, not from project_root.

NOT CHECKED / OPEN
- Failures of the other two checks (recipe rules, data vs contract) still show as a failed check plus a warning toast, as before. The task named the child process only. Say if you want those moved to the same "could not run" box.
- I did not run the full browser suite or the full test suite. I did not run the `qa` features through a real container or server install.
- Not run: the two checks in a worktree-less install where libs/*/src does not exist. The code then relies on the inherited PYTHONPATH or installed packages.
- The stale pre-existing "provides" and "consumed_by" @deps lines of blueprint_handlers.py were not touched.
