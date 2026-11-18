"""Gallery guidance links open in a new tab; the Gallery texts say only what is true (D-0008, D-0046)."""
from pathlib import Path

from shiny import ui

from app.modules.gallery_listing import external_links_new_tab

ROOT = Path(__file__).resolve().parents[2]


def test_every_external_link_opens_in_new_tab():
    html = external_links_new_tab(str(ui.markdown(
        "[a](https://r-graph-gallery.com/x.html) and [b](http://z.y) and <a href=\"https://q.r\" target=\"_self\">c</a>")))
    assert html.count('target="_blank" rel="noopener noreferrer"') == 3
    assert "_self" not in html


def test_internal_anchor_and_relative_link_untouched():
    html = external_links_new_tab('<a href="#sec">i</a> <a href="rel/page.html">r</a>')
    assert "target" not in html


def test_every_shipped_guidance_link_is_fixed():
    for md in sorted((ROOT / "assets/gallery_data").glob("*/example_meta.md")):
        html = external_links_new_tab(str(ui.markdown(md.read_text())))
        assert html.count("<a ") == html.count('rel="noopener noreferrer"') or "href=\"#" in html, md


def test_removed_promises_are_gone():
    home = (ROOT / "app/handlers/home_theater.py").read_text()
    viewer = (ROOT / "app/modules/gallery_viewer.py").read_text()
    assert "Architect sandbox" not in home
    assert "copy the recipe text by hand" in home
    assert "request for example implementation" not in viewer
    assert "Open an issue with the GitHub button" in viewer


def test_dead_submission_form_is_gone():
    from app.modules.gallery_viewer import GalleryViewer
    assert not hasattr(GalleryViewer, "submission_modal_ui")
    assert not hasattr(GalleryViewer, "autofill_meta_from_audit")
    from viz_gallery.gallery_manager import GalleryManager  # submit_example stays (D-0046)
    assert callable(GalleryManager.submit_example)
