## Working in a git worktree

A git worktree is a second checkout of the repository in another folder. The shared `.venv` has the libraries installed as editable, and those installs point at the main folder. Without a setting, a test run in a worktree imports the main folder's code and reports on it as if it were the worktree's.

**Tests:** run `pytest` from the root of the worktree. The `pythonpath` setting in `pyproject.toml` puts that worktree's `.` and `libs/*/src` first. `app/tests/test_imports_from_checkout.py` fails if the code comes from another folder.

**Scripts that pytest does not run:** set the path by hand, with the worktree as the root:

```bash
ROOT="$(git rev-parse --show-toplevel)"
export PYTHONPATH="$ROOT$(printf ':%s' "$ROOT"/libs/*/src)${PYTHONPATH:+:$PYTHONPATH}"
```

**Safety:** use absolute paths of your own checkout only. Never leave an empty entry (a trailing or leading colon): Python reads it as the current folder.
