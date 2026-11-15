"""Every seed that is used is written in the recipe (Eve, 2026-11-15, ADR-104): no shipped recipe and no gallery
example has a random layer without a number written on it.

A random layer is a jitter, a sina or a bootstrapped summary (`utils.random_layers`). The recipes read are the
pipeline recipes of `config/data_analysis_recipes` (with their `!include`d plot files) and the recipe of every gallery
example. The number must be written: `random_state: null` and the word random ask for a different arrangement.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_shipped_recipes_write_their_seeds.py -q
"""
from pathlib import Path

import pytest
import yaml

from utils.random_layers import is_random_layer

REPO = Path(__file__).resolve().parents[2]
SHIPPED = sorted((REPO / "config/data_analysis_recipes").rglob("*.yaml")) + sorted(
    (REPO / "assets/gallery_data").glob("*/data_analysis_recipe.yaml"))


class _Loader(yaml.SafeLoader):
    """Reads a recipe file on its own: an `!include` tag is kept as its text (the included files are read too)."""


_Loader.add_constructor("!include", lambda loader, node: loader.construct_scalar(node))


def layers_in(node):
    """Every list of layers (dicts with a `name`) under a key `layers`, anywhere in the file."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "layers" and isinstance(value, list):
                yield [layer for layer in value if isinstance(layer, dict) and "name" in layer]
            yield from layers_in(value)
    elif isinstance(node, list):
        for value in node:
            yield from layers_in(value)


def unseeded(path: Path):
    data = yaml.load(path.read_text(), Loader=_Loader)
    found = []
    for layers in layers_in(data):
        for index, layer in enumerate(layers, start=1):
            params = layer.get("params") or {}
            if not is_random_layer(layer["name"], params):
                continue
            written = params.get("random_state")
            if isinstance(written, bool) or not isinstance(written, int):
                found.append(f"layer {index} ({layer['name']}): random_state is {written!r}")
    return found


def test_there_are_shipped_recipes_to_read():
    assert len(SHIPPED) > 20 and any(p.name == "phenotype_genome_length_dotplot.yaml" for p in SHIPPED)
    assert any(p.parent.name == "jitter_strip" for p in SHIPPED)


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(p.relative_to(REPO)))
def test_no_random_layer_without_a_number_written(path):
    assert unseeded(path) == []


def test_the_reader_finds_what_it_looks_for(tmp_path):
    f = tmp_path / "r.yaml"
    f.write_text("plots:\n  p:\n    layers:\n      - {name: geom_jitter}\n      - {name: geom_sina, params: {random_state: null}}\n"
                 "      - {name: geom_point, params: {position: jitter, random_state: 0}}\n      - {name: geom_bar}\n")
    assert unseeded(f) == ["layer 1 (geom_jitter): random_state is None", "layer 2 (geom_sina): random_state is None"]
