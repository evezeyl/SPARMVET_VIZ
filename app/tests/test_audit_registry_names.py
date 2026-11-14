"""The coherence audit reads the live action registry, not the source text (a check must follow the change it checks).

After recipe format 1 most actions are generated from the Polars signatures, so a scan for `@register_action("name")`
finds almost none of them and reported every shipped recipe as using unregistered actions.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_registry_names.py -q
"""
import importlib.util
from pathlib import Path

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS

ROOT = Path(__file__).resolve().parents[2]


def _audit():
    spec = importlib.util.spec_from_file_location("coherence", ROOT / "scripts/audit_data_analysis_recipe_coherence.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_audit_knows_every_registered_action():
    names = _audit().registered_action_names(ROOT / "libs/transformer/src/transformer/actions")
    assert set(AVAILABLE_WRANGLING_ACTIONS) <= names


def test_the_audit_passes_on_the_shipped_recipes():
    import subprocess, sys
    out = subprocess.run([sys.executable, str(ROOT / "scripts/audit_data_analysis_recipe_coherence.py"), "--project-root", str(ROOT),
                          "--output", "tmpAI/audits/coherence_test.md"], capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, (out.stdout + out.stderr)[-1500:]
