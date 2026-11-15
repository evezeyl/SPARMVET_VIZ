# Proposal: `.claude/rules/rules_toolchain.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked: every path in the table exists (`ls`: `scripts/install_libs.sh`, `scripts/run_audits.sh`, the four `assets/scripts/` tools); the file's own rule says "A new tool is added here ... in the same commit that starts to use it", and four tools used this week are not listed. Read: docstrings and arguments of `assets/scripts/migrate_recipe_format.py`, `golden_baseline.py`, `gallery_previews.py`.

## 1. Add four rows to the table (FACT; the file's own rule)
Proposed rows (after the `audit_uml_model.py` row, line 24):
```
| `libs/utils` function `check_recipe` | Judge a recipe in format 1 (profiles `run`, `build`, `gallery`, `audit`), no data read | `PYTHONPATH=. ./.venv/bin/python -c "from utils.recipe_check import check_recipe_file ..."` (the app calls it through `app/modules/data_analysis_recipe_validator.py`) | every recipe change |
| `assets/scripts/migrate_recipe_format.py` | Convert recipes from format 0 to format 1 (runs A to D); without `--apply` it only lists | `./.venv/bin/python assets/scripts/migrate_recipe_format.py PATH [--run A|B|C|D] [--apply]` | recipe migration |
| `assets/scripts/golden_baseline.py` | Record and compare the tables every shipped recipe produces (a result-identical change must not move a hash) | `./.venv/bin/python assets/scripts/golden_baseline.py [--out FILE] [--check FILE]` | before and after a change that must not change results |
| `assets/scripts/gallery_previews.py` | Draw the gallery previews by the app's own path and compare them with the committed pictures | `PYTHONPATH=. ./.venv/bin/python assets/scripts/gallery_previews.py [--only NAME ...] [--apply] [--changed]` | gallery examples |
```
Why: those commands come from the argparse definitions read. The first row's exact call line was not run by me; Eve or a reviewer should run it before it is pasted ("Commands in this file are checked: a documented command that does not run is a defect"). `check_launch_commands.py` checks only launch commands.

## 2. "Not installed" table (no change), checked
`ruff` configuration in `pyproject.toml` is still commented out (`pyproject.toml:29, 33`); `mmdc` not checked (not installed claims are not verifiable here). No change.

## Not settled
1. The exact documented call of `check_recipe` (row 1) was not run.
