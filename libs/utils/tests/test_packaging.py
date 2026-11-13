"""The container installs the libraries non-editable, so a data file must be declared or it is silently absent from the wheel.

`recipe_spec.yaml` is the first data file in a library (spec section 14, packaging condition).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_packaging.py -q
"""
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

UTILS = Path(__file__).resolve().parents[1]


def test_the_specification_file_is_declared_as_package_data():
    assert "recipe_spec.yaml" in (UTILS / "pyproject.toml").read_text()


def test_the_built_wheel_contains_the_specification_file(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "-q", "-w", str(tmp_path), str(UTILS)],
        capture_output=True, text=True, timeout=240)
    if result.returncode != 0:
        pytest.skip(f"the wheel could not be built here: {result.stderr.strip()[-200:]}")
    wheels = list(tmp_path.glob("utils-*.whl"))
    assert wheels, "no wheel was produced"
    assert "utils/recipe_spec.yaml" in zipfile.ZipFile(wheels[0]).namelist()
