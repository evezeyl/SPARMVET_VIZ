"""The Gallery viewer reads the taxonomy from the specification data (spec section 9, finding G1).

The terms, labels and icons of the six filter axes were copied in the viewer and in the handlers, and the copies
disagreed with the cheat sheet. They now come from `utils/recipe_spec.yaml` through `viz_gallery.taxonomy`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_viewer_taxonomy.py -q
"""
from pathlib import Path

from utils.recipe_check import spec

ROOT = Path(__file__).resolve().parents[2]


def test_the_filter_panels_of_the_viewer_come_from_the_specification(monkeypatch):
    from app.modules.gallery_viewer import GalleryViewer
    pivot = {"by_difficulty": {"Advanced": ["a"], "Simple": ["b"], "Intermediate": ["c"]}, "by_geom": {"geom_point": ["a"]},
             "by_pattern": {"Numeric-Numeric": ["a"], "2 Numeric": ["b"]}}
    monkeypatch.setattr(GalleryViewer, "_load_pivot", lambda self: pivot)
    html = str(GalleryViewer().build_sidebar_ui())
    for item in spec()["gallery"]["display"]:
        assert f"{item['icon']} {item['label']}" in html
        assert f'id="gallery_filter_{item["axis"]}"' in html and f'id="gallery_all_{item["axis"]}"' in html
    assert html.index('value="Simple"') < html.index('value="Intermediate"') < html.index('value="Advanced"')
    assert 'value="geom_point"' in html and 'value="2 Numeric"' in html
    assert "Numeric-Numeric" not in html   # not a term of the vocabulary: the old fallback lists offered it


def test_the_gallery_app_files_hold_no_copy_of_the_taxonomy_terms():
    terms = {term for values in spec()["gallery"]["terms"].values() for term in values} | {"Numeric-Numeric", "geom_bin_2d"}
    panel_labels = {f"{item['icon']} {item['label']}" for item in spec()["gallery"]["display"]}
    for path in (ROOT / "app/modules/gallery_viewer.py", ROOT / "app/handlers/gallery_handlers.py"):
        text = path.read_text()
        copies = sorted(word for word in terms if f'"{word}"' in text or f"'{word}'" in text) + sorted(label for label in panel_labels if label in text)
        assert copies == [], f"{path.name} holds taxonomy terms or labels that belong to the specification data: {copies}"
