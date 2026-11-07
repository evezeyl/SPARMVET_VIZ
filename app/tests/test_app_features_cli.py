"""The command-line gate for app features files runs for one file and for all (ADR-073, ADR-091)."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "validate_app_features_config.py"


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=REPO, capture_output=True, text=True)


def test_all_shipped_files_pass_strictly():
    r = _run("--all", "--strict")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: PASS" in r.stdout


def test_one_file_by_short_name_passes():
    r = _run("--app-features", "qa", "--strict")
    assert r.returncode == 0, r.stdout + r.stderr


def test_unknown_name_fails_with_a_message():
    r = _run("--app-features", "no-such-file")
    assert r.returncode != 0
    assert "not found" in (r.stdout + r.stderr).lower()
