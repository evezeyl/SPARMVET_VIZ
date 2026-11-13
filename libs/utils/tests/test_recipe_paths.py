"""The paths a recipe may name (checks PA01 and PA02; spec section 15, decision DEC30).

The shape rule always applies to a development path (`source.path`, `reference_file`); containment applies when the
caller passes the roots it allows. The checker is pure: it never reads the deployment itself.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_paths.py -q
"""
import os

import pytest

from utils.recipe_paths import containment_problems, shape_problems


@pytest.mark.parametrize("path", [
    "assets/test_data/a.tsv",
    "./assets/test_data/a.tsv",
    "config/references/amr/test.tsv",
    "example_data.tsv",
    "a b/c.tsv",
])
def test_a_relative_path_inside_the_project_has_the_right_shape(path):
    assert shape_problems(path) == []


@pytest.mark.parametrize("path", [
    "/etc/passwd",
    "/home/someone/data.tsv",
    "../data.tsv",
    "assets/../../data.tsv",
    "assets/test_data/../../../x",
    "~/data.tsv",
    "~root/data.tsv",
    "http://example.org/data.tsv",
    "https://example.org/data.tsv",
    "file:///etc/passwd",
    "s3://bucket/key",
    "C:\\data\\a.tsv",
    "\\\\server\\share\\a.tsv",
    "a\x00b.tsv",
    "",
    "   ",
])
def test_an_absolute_parent_home_url_or_empty_path_is_refused(path):
    assert shape_problems(path), f"allowed but must be refused: {path!r}"


@pytest.mark.parametrize("path", [None, 5, ["a"], {"a": 1}])
def test_a_path_that_is_not_text_is_refused(path):
    assert shape_problems(path)


def test_a_refused_path_says_the_fix():
    assert "Fix:" in shape_problems("/etc/passwd")[0]


def test_containment_accepts_a_path_inside_an_allowed_root(tmp_path):
    root = tmp_path / "assets" / "test_data"
    root.mkdir(parents=True)
    assert containment_problems("assets/test_data/a.tsv", [root], base=tmp_path) == []


def test_containment_refuses_a_path_outside_every_root(tmp_path):
    root = tmp_path / "assets" / "test_data"
    root.mkdir(parents=True)
    other = tmp_path / "secret"
    other.mkdir()
    assert containment_problems("secret/a.tsv", [root], base=tmp_path)


def test_containment_accepts_any_of_several_roots(tmp_path):
    one, two = tmp_path / "one", tmp_path / "two"
    one.mkdir(), two.mkdir()
    assert containment_problems("two/a.tsv", [one, two], base=tmp_path) == []


def test_containment_refuses_a_symlink_that_leaves_the_root(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "a.tsv").write_text("x")
    os.symlink(outside, root / "link")
    assert containment_problems("data/link/a.tsv", [root], base=tmp_path)


def test_containment_with_no_roots_is_not_judged(tmp_path):
    """No roots passed means the caller did not ask for containment; the shape rule still applies elsewhere."""
    assert containment_problems("anything/a.tsv", None, base=tmp_path) == []


def test_a_root_that_is_a_prefix_of_another_folder_does_not_match(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data_other").mkdir()
    assert containment_problems("data_other/a.tsv", [tmp_path / "data"], base=tmp_path)
