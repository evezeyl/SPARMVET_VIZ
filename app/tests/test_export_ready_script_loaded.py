"""D-0270 and ADR-071 rule 2: the Export button script is on the page only when export_enabled is on."""
from app.src.bootloader import bootloader
from app.src.ui import export_ready_script_tags


def _html(tags) -> str:
    return "".join(str(t) for t in tags)


def test_with_export_enabled_the_page_has_the_script_tag(monkeypatch):
    monkeypatch.setitem(bootloader.flags, "export_enabled", True)
    assert "export_ready.js" in _html(export_ready_script_tags())


def test_with_export_disabled_the_page_has_no_script_tag(monkeypatch):
    monkeypatch.setitem(bootloader.flags, "export_enabled", False)
    assert export_ready_script_tags() == []
