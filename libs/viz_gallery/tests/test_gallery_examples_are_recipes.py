"""Every shipped gallery example is a standard recipe (format 1), checked in the profile `gallery` (spec section 9).

One rule set for every recipe: `check_recipe`. This library test runs the structure checks only (no registry is
loaded here: a library does not import its peers); the same check with the action and component catalogs runs in
`app/tests/test_gallery_full_check.py`.

`WAITING` names the examples that cannot be standard recipes yet, each with its reason. It is a ratchet: such an
example must still fail, so the entry is removed in the commit that converts it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_gallery/tests/test_gallery_examples_are_recipes.py -q
"""
from pathlib import Path

import pytest

from utils.recipe_check import spec
from utils.recipe_loader import check_recipe_file
from viz_gallery.gallery_manager import GalleryManager
from viz_gallery.taxonomy import example_taxonomy, tag_strip, with_tag_strip

SHIPPED = Path(__file__).resolve().parents[3] / "assets" / "gallery_data"
RECIPE = "data_analysis_recipe.yaml"
WAITING = {
    "beeswarm_sina": "its own step lives in tier 3 and the engine does not read tier 3 yet (spec 7.7, finding G9)",
}


def _bundles():
    return sorted(d for d in SHIPPED.iterdir() if d.is_dir())


def _check(bundle: Path):
    return check_recipe_file(bundle / RECIPE, "gallery", file_stem=bundle.name)


def test_the_gallery_has_its_examples():
    assert len(_bundles()) >= 30


@pytest.mark.parametrize("bundle", [d for d in _bundles() if d.name not in WAITING], ids=lambda d: d.name)
def test_example_is_a_standard_recipe(bundle):
    result = _check(bundle)
    assert not result.errors, "\n".join(problem.text(bundle.name) for problem in result.errors)


@pytest.mark.parametrize("name", sorted(WAITING))
def test_waiting_example_still_fails(name):
    result = _check(SHIPPED / name)
    assert result.errors, f"{name} passes the gallery check now: remove it from WAITING ({WAITING[name]})"


def test_waiting_names_only_shipped_examples():
    assert set(WAITING) <= {d.name for d in _bundles()}


def test_every_shipped_example_has_its_companion_files():
    for folder in _bundles():
        for name in (RECIPE, *spec()["gallery"]["companion_files"]):
            assert (folder / name).exists(), f"{folder.name} lacks {name}"


def test_the_check_of_the_shipped_gallery_accepts_all_but_the_waiting_examples():
    examples = GalleryManager(str(SHIPPED)).check_examples()
    assert set(examples.rejected) == set(WAITING), examples.rejected
    assert set(examples.accepted) == {d.name for d in _bundles()} - set(WAITING)


def test_the_tag_strip_of_every_shipped_example_equals_its_taxonomy():
    accepted = GalleryManager(str(SHIPPED)).check_examples().accepted
    assert accepted
    for name, recipe in accepted.items():
        text = (SHIPPED / name / "example_meta.md").read_text()
        assert with_tag_strip(text, tag_strip(example_taxonomy(recipe))) == text, f"{name}: the tag strip does not equal the taxonomy"
