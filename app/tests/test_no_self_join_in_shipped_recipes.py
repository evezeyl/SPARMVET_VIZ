"""No shipped recipe joins a table with itself as the first step of a join (JOIN-SELF-1).

The assembler used to skip a first join step whose right table was the base table, without a message. That skip is
removed: a join runs as written. A shipped recipe that relied on the skip was a wrong recipe and was corrected
(the first step of AR1_MLST_Serotype_Virulence joined MLST with itself). This test keeps the shipped recipes free of
the pattern, so the checker advice J12 never fires on a recipe of the project.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_no_self_join_in_shipped_recipes.py -q
"""
from pathlib import Path

import pytest

from utils.recipe_loader import load_recipe

ROOT = Path(__file__).resolve().parents[2]
RECIPE_DIRS = [ROOT / "config" / "data_analysis_recipes", ROOT / "assets" / "gallery_data"]


def _shipped_recipes():
    for base in RECIPE_DIRS:
        for path in sorted(base.rglob("*.yaml")):
            raw, _ = load_recipe(path)
            if isinstance(raw, dict) and isinstance(raw.get("joins"), dict):
                yield path, raw


def _self_joins(raw):
    found = []
    for join_id, join in raw["joins"].items():
        ingredients = (join or {}).get("ingredients") or []
        for tier in ("tier1", "tier2"):
            for index, step in enumerate(((join or {}).get(tier) or {}).get("steps") or [], start=1):
                if isinstance(step, dict) and ingredients and step.get("right_ingredient") == ingredients[0].get("dataset_id"):
                    found.append(f"{join_id}.{tier}[{index}]")
    return found


def test_the_scan_finds_recipes():
    assert len(list(_shipped_recipes())) >= 5


@pytest.mark.parametrize("path,raw", list(_shipped_recipes()), ids=lambda v: v.name if isinstance(v, Path) else "")
def test_no_join_of_the_base_table_with_itself(path, raw):
    assert _self_joins(raw) == [], f"{path.name}: a join step joins the first ingredient with itself"
