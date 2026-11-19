"""The navigator reads a recipe once when the caller passes the structure it built (export lineage, Blueprint refresh).

Held here:
- with a passed structure every navigator function returns exactly what it returns without one, on every shipped recipe;
- tracing every plot of a recipe with one passed structure loads the recipe once (the structure build); without it, once per plot;
- nothing is cached by file name: the structure is an object the caller passes (no test needed: there is no cache to go stale).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_structure_passed_once.py -q

# @deps
# consumes: libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py
# doc: .claude/knowledge/decision_ledger.md (D-0031)
# @end_deps
"""
import pytest

from blueprint_arch import data_analysis_recipe_navigator as navigator
from blueprint_arch.data_analysis_recipe_navigator import (
    build_plot_lineage, build_schema_registry, build_sibling_map, recipe_structure_of_file)

from test_navigator_on_graph import SHIPPED


def plot_ids(path):
    import yaml
    tree = navigator.recipe_structure_of_file(path)
    ids = []
    try:
        raw = open(path, encoding="utf-8").read()
        class L(yaml.SafeLoader):
            pass
        L.add_constructor("!include", lambda loader, node: None)
        t = yaml.load(raw, Loader=L)
        for g in (t.get("analysis_groups") or {}).values():
            if isinstance(g, dict):
                ids += list((g.get("plots") or {}).keys())
    except Exception:
        pass
    return ids


@pytest.mark.parametrize("path", SHIPPED)
def test_same_output_with_passed_structure(path):
    structure = recipe_structure_of_file(path)
    assert build_sibling_map(path) == build_sibling_map(path, structure)
    assert build_schema_registry(path, {}) == build_schema_registry(path, {}, structure)
    for pid in plot_ids(path):
        assert build_plot_lineage(pid, path) == build_plot_lineage(pid, path, structure)


def test_the_loader_runs_once_for_all_plots(monkeypatch):
    path = next(p for p in SHIPPED if "1_test_data_ST22_dummy" in p)
    ids = plot_ids(path)
    assert len(ids) > 3
    calls = []
    real = navigator.load_recipe
    monkeypatch.setattr(navigator, "load_recipe", lambda *a, **k: (calls.append(1), real(*a, **k))[1])
    structure = recipe_structure_of_file(path)
    for pid in ids:
        assert build_plot_lineage(pid, path, structure)
    build_sibling_map(path, structure)
    build_schema_registry(path, {}, structure)
    assert len(calls) == 1
    calls.clear()
    for pid in ids:
        build_plot_lineage(pid, path)
    assert len(calls) == len(ids)
