"""The open findings are not part of the default run (EQUALITY-CHECK-1, PROVISIONAL).

`test_findings_open.py` holds the comparisons where the engine and the hand-written side differ today. They are left
failing on purpose (a difference is a finding, `FINDINGS.md`). The default headless command does not collect them;
to run them:  EQUALITY_FINDINGS=1 PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/equality/test_findings_open.py
"""
import os

collect_ignore = [] if os.environ.get("EQUALITY_FINDINGS") else ["test_findings_open.py"]
