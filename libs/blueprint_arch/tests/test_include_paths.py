"""Every `!include` target of a recipe text is found, quoted or not.

The recipe writer leaves a plain path unquoted (`mlst_bar: !include d/plots/x.yaml`); an author may quote it. Blueprint builds its
map of the files of a recipe from this list, and a plot node opens only when the file of its entry is in the map: a scan that
found the quoted paths only made every plot of the demo recipe open as "0 steps".

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_include_paths.py -q
"""
from pathlib import Path

import pytest
import yaml

from blueprint_arch.data_analysis_recipe_navigator import build_sibling_map, include_paths

DEMO = Path(__file__).resolve().parents[3] / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"

TEXT = """
a: !include 'dir/single.yaml'
b: !include "dir/double.yaml"
c: !include dir/plain.yaml
d:
  - !include dir/in_a_list.yaml
e: !include dir/plain.yaml   # the same file twice
# f: !include dir/in_a_comment.yaml
g: "text that says !include dir/in_a_string.yaml"
"""


def test_quoted_and_plain_paths_are_found_each_once_in_the_order_of_the_file():
    assert include_paths(TEXT) == ["dir/single.yaml", "dir/double.yaml", "dir/plain.yaml", "dir/in_a_list.yaml"]


def test_a_comment_and_a_string_are_not_includes():
    found = include_paths(TEXT)
    assert "dir/in_a_comment.yaml" not in found and "dir/in_a_string.yaml" not in found


def test_a_text_without_include_gives_an_empty_list():
    assert include_paths("a: 1\n") == [] and include_paths("") == []


def test_a_text_that_is_not_yaml_is_refused_not_guessed():
    with pytest.raises(yaml.YAMLError):
        include_paths("a: [1, 2\n")


def test_every_file_a_recipe_registers_is_in_its_includes():
    """The map of the files (build_sibling_map) and the list of includes must agree: a file of the map missing here cannot open."""
    registered = {rel for rel in build_sibling_map(str(DEMO)) if rel.endswith(".yaml") and "/" in rel}
    assert registered, "the demo recipe registers no file"
    assert registered <= set(include_paths(DEMO.read_text(encoding="utf-8")))


def test_the_demo_recipe_includes_the_file_of_each_of_its_17_plots():
    found = set(include_paths(DEMO.read_text(encoding="utf-8")))
    plot_files = {rel for rel in found if "/plots/" in rel}
    assert len(plot_files) == 17
    assert all((DEMO.parent / rel).is_file() for rel in plot_files)
