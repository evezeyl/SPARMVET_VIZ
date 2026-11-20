"""ADR-071 rule 2: the Gallery filter script is on the page only when gallery_enabled is on."""
from app.src.bootloader import bootloader
from app.src.ui import gallery_script_tags


def _html(tags) -> str:
    return "".join(str(t) for t in tags)


def test_with_gallery_enabled_the_page_has_the_script_tag(monkeypatch):
    monkeypatch.setitem(bootloader.flags, "gallery_enabled", True)
    assert "gallery_select_all.js" in _html(gallery_script_tags())


def test_with_gallery_disabled_the_page_has_no_script_tag(monkeypatch):
    monkeypatch.setitem(bootloader.flags, "gallery_enabled", False)
    assert gallery_script_tags() == []
