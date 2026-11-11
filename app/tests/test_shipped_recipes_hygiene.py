"""Shipped recipes must not carry keys the engine silently ignores, or schemas that cannot be built.

Found on 2026-11-11 (data-scientist review of 1_test_data_ST22_dummy): `facet_scales`, `labs` and
`coordinate_flip` at the top of a plot spec and `height` / `show_legend` in `plot_defaults` were
ignored without any message, and the data schema `Detailed_summary` could not be built while every
existing check passed. This file makes those three classes fail loudly for every shipped recipe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_shipped_recipes_hygiene.py -q
"""
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager
from viz_factory.plot_config_resolver import _CANONICAL_SPEC_KEYS, _VALID_PLOT_DEFAULTS_KEYS

ROOT = Path(__file__).resolve().parents[2]
RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RECIPE_IDS = sorted(p.stem for p in RECIPES_DIR.glob("*.yaml"))
# Descriptive keys of a plot spec that the engine keeps as passthrough metadata on purpose (gallery taxonomy,
# author notes). Any other key outside the canonical spec keys is dropped by the engine without a message.
PASSTHROUGH_SPEC_KEYS = {"family", "pattern", "difficulty", "description", "info"}


def _raw(recipe_id):
    return ConfigManager(str(RECIPES_DIR / f"{recipe_id}.yaml")).raw_config


def _plot_specs(raw):
    for group in (raw.get("analysis_groups") or {}).values():
        for plot_id, entry in (group.get("plots") or {}).items():
            yield plot_id, entry.get("spec") or {}


@pytest.mark.parametrize("recipe_id", RECIPE_IDS)
def test_plot_defaults_has_only_known_keys(recipe_id):
    unknown = sorted(set(_raw(recipe_id).get("plot_defaults") or {}) - _VALID_PLOT_DEFAULTS_KEYS - {"layers"})
    assert not unknown, f"{recipe_id}: plot_defaults keys the engine ignores (a warning is printed for every plot): {unknown}"


@pytest.mark.parametrize("recipe_id", RECIPE_IDS)
def test_plot_specs_have_no_silently_ignored_keys(recipe_id):
    problems = {}
    for plot_id, spec in _plot_specs(_raw(recipe_id)):
        ignored = sorted(set(spec) - _CANONICAL_SPEC_KEYS - PASSTHROUGH_SPEC_KEYS)
        if ignored:
            problems[plot_id] = ignored
    assert not problems, (
        f"{recipe_id}: plot spec keys that are dropped without a message "
        f"(use a layer such as facet_wrap with scales, labs or coord_flip instead): {problems}"
    )


@pytest.mark.parametrize("recipe_id", RECIPE_IDS)
def test_every_data_schema_builds(recipe_id):
    """Execute the tier-1 wrangling of every data schema, not only read its column names."""
    clear_data_analysis_recipe_cache()
    raw = _raw(recipe_id)
    orchestrator = DataOrchestrator(RECIPES_DIR, ROOT / "assets" / "test_data")
    schemas = []
    for section in ("data_schemas", "additional_datasets_schemas"):
        schemas += list((raw.get(section) or {}).items())
    if isinstance(raw.get("metadata_schema"), dict):
        schemas.append(("metadata_schema", raw["metadata_schema"]))
    failures = {}
    for dataset_id, spec in schemas:
        try:
            orchestrator.prepare_ingredient(dataset_id, spec).collect()
        except Exception as exc:  # noqa: BLE001 - report every schema that fails, with its reason
            failures[dataset_id] = f"{type(exc).__name__}: {str(exc)[:120]}"
    assert not failures, f"{recipe_id}: data schemas that cannot be built: {failures}"
