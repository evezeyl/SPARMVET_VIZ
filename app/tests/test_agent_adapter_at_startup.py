"""The Blueprint agent adapter is built when the app starts, never inside a render (CONTROLS-FIX-1, A).

Why: `ClaudeCliAdapter` runs `claude -p ok` as an auth probe (several seconds). Built lazily from
`blueprint_agent_panel_ui`, the probe ran in the first session that opened Blueprint: it blocked the event loop of every
session and held Shiny's reactive lock, so the timer task of the load-gate poll (GATE-GAP-1) was still waiting for the
lock when the session ended and Shiny printed a Traceback into the server log (browser test
`test_every_app_features_starts.py`, developer case).
"""
import subprocess
import sys
import textwrap
from pathlib import Path

from app.tests.subprocess_env import app_env

REPO = Path(__file__).resolve().parents[2]
LOCAL = "config/deployment/local/local.yaml"

# runs in a child process: a recording make_adapter stands in for the real one (no `claude` is started)
CHILD = textwrap.dedent("""
    import blueprint_arch.agent_adapter as aa
    calls = []
    def recording(**kw):
        calls.append(kw["backend"])
        return aa.DisabledAdapter("recorded")
    aa.make_adapter = recording
    import app.src.main as main
    after_import = list(calls)
    from app.src.bootloader import bootloader
    bootloader.get_agent_adapter()
    bootloader.get_agent_adapter()
    print("AFTER_IMPORT", after_import, "AFTER_USE", calls)
""")


def _run(app_features):
    env = app_env(SPARMVET_APP_FEATURES=app_features, SPARMVET_DEPLOYMENT=LOCAL)
    out = subprocess.run([sys.executable, "-c", CHILD], cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-1500:]
    return [line for line in out.stdout.splitlines() if line.startswith("AFTER_IMPORT")][-1]


def test_developer_builds_the_adapter_once_when_the_app_is_imported():
    assert _run("developer") == "AFTER_IMPORT ['claude_cli'] AFTER_USE ['claude_cli']"


def test_an_app_features_without_the_agent_builds_none():
    assert _run("standalone") == "AFTER_IMPORT [] AFTER_USE []"
