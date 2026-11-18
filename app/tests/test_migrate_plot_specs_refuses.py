"""`assets/scripts/migrate_plot_specs.py` was the one-time migration of ADR-083 (factory_id and flat aesthetics, 2026-05-20).

It writes the plot under a `spec:` key, a shape the recipe checker has refused since 2026-11-17 (D-0236, D-0237), so it can
no longer produce a valid recipe. It refuses to run and names the tool that replaced it; it is listed for a removal decision.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_migrate_plot_specs_refuses.py -q
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "assets" / "scripts" / "migrate_plot_specs.py"
OLD_PLOT = "spec:\n  factory_id: bar_logic\n  mapping: {x: a}\n"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT, timeout=120)


def test_it_refuses_to_apply_and_names_the_tool_that_replaced_it(tmp_path):
    plot = tmp_path / "p.yaml"
    plot.write_text(OLD_PLOT, encoding="utf-8")
    done = run("--apply", "--root", str(tmp_path))
    assert done.returncode != 0
    assert "migrate_recipe_engine_keys.py" in done.stderr
    assert plot.read_text(encoding="utf-8") == OLD_PLOT, "a refused run must not write"


def test_the_dry_run_refuses_too(tmp_path):
    (tmp_path / "p.yaml").write_text(OLD_PLOT, encoding="utf-8")
    done = run("--root", str(tmp_path))
    assert done.returncode != 0 and "migrate_recipe_engine_keys.py" in done.stderr


def test_help_still_works():
    done = run("--help")
    assert done.returncode == 0 and "usage" in done.stdout.lower()
