# Fix report, task/one-python
Commit: 5bb9f719 (on c6c4947f).
Remaining hits of python_interpreter in docs, README.md, config, assets: only docs/deployment/deployment_guide.qmd:55 (the sentence saying the key is gone). ADR (not edited): .claude/knowledge/architecture_decisions.md:1102-1103.
Task line for the scribe: ONE-PYTHON-TOMBSTONE-1 [haiku/low]: delete REMOVED_DEPLOYMENT_KEYS and removed_deployment_key_errors in app/modules/renamed_keys.py (and their test) when the tombstone expires; expiry phase to be confirmed by Eve.
Rule section 5 on dev (before): path MUST be defined in deployment file (runtime: {python_interpreter: ...}); scripts MUST fetch it via the Bootloader.
Rule section 5 on branch (now, unchanged by me): "The Python that runs the app is the only interpreter. / Any child process the app starts that runs Python uses sys.executable. No code names a path such as ./.venv/bin/python or the bare word python for this. / A deployment file has no python_interpreter key (removed 2026-11-18, D-0263). The app refuses a deployment file that still has it and says to delete it."
Tests: test_python_interpreter_key_removed.py + test_source_no_venv_path.py = 16 passed. check_doc_links.py takes no file argument (only --root), not run.
Other paths report: tmpAI/panel/one_python/OTHER_PATHS.md.
git status --short: clean.
git merge-tree --write-tree dev HEAD: ebf2138e8d7ba018ddbded6677a82cce45a4d25e (no conflict).
