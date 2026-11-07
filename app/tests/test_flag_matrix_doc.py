"""The flag matrix in .claude/rules/rules_app_features_flags.md says what the app features files say.

The table is the reference people read before changing a flag; it had drifted from the files
(wrangle_studio_enabled, session_management_enabled) without any test noticing.
"""
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
COLUMN_TO_FILE = {"static": "pipeline-static", "demo-vetinst": "demo-vetinst", "simple": "pipeline-exploration-simple",
                  "web-demo": "web-demo", "advanced": "pipeline-exploration-advanced", "independent": "standalone",
                  "developer": "developer", "qa": "qa"}


class _Loader(yaml.SafeLoader):
    pass


_Loader.add_constructor("!include", lambda loader, node: None)


def _documented_matrix() -> dict[tuple[str, str], str]:
    text = (REPO / ".claude/rules/rules_app_features_flags.md").read_text(encoding="utf-8")
    rows = [line for line in text[text.index("| Flag | static"):].split("\n") if line.startswith("|")]
    columns = [c.strip() for c in rows[0].strip("|").split("|")][1:]
    matrix = {}
    for row in rows[2:]:
        cells = [c.strip().strip("*") for c in row.strip("|").split("|")]
        if not cells[0].startswith("`"):
            break
        for column, value in zip(columns, cells[1:]):
            matrix[(column, cells[0].strip("`"))] = value.lower()
    return matrix


MATRIX = _documented_matrix()


def test_the_matrix_was_read_and_covers_every_shipped_file():
    assert {c for c, _ in MATRIX} == set(COLUMN_TO_FILE)
    assert {p.stem for p in (REPO / "config/app_features").glob("*.yaml")} == set(COLUMN_TO_FILE.values())
    assert len(MATRIX) > 100


@pytest.mark.parametrize("column, flag", sorted(MATRIX))
def test_documented_flag_equals_the_file(column, flag):
    flags = yaml.load((REPO / f"config/app_features/{COLUMN_TO_FILE[column]}.yaml").read_text(encoding="utf-8"), _Loader)["flags"]
    assert str(flags.get(flag)).lower() == MATRIX[(column, flag)], f"{COLUMN_TO_FILE[column]}: {flag}"
