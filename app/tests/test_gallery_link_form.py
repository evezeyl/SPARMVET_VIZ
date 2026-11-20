"""Every guidance link of every Gallery example has a sound form (offline; D-0379).

Form only: https, a known host, a page path, no empty link. Whether a page still answers is checked online by
`assets/scripts/check_gallery_links.py` (a network check is never part of the test suite).
"""
import re
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[2]
GALLERY = ROOT / "assets/gallery_data"
KNOWN_HOSTS = {"r-graph-gallery.com"}
METAS = sorted(GALLERY.glob("*/example_meta.md"))
_MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_BARE = re.compile(r"https?://[^\s)>\"]+")


def _links(text: str) -> list:
    return [target.strip() for _, target in _MD_LINK.findall(text)] + _BARE.findall(text)


def _problem(url: str):
    if not url:
        return "empty link"
    parts = urlparse(url)
    if parts.scheme != "https":
        return "not https"
    if parts.netloc not in KNOWN_HOSTS:
        return f"unknown host {parts.netloc!r}"
    if parts.path in ("", "/") or any(c.isspace() for c in url):
        return "no page path or whitespace"
    return None


def test_there_are_examples_and_links():
    assert METAS
    assert sum(len(_links(m.read_text(encoding="utf-8"))) for m in METAS) > 0


@pytest.mark.parametrize("meta", METAS, ids=lambda m: m.parent.name)
def test_every_link_of_the_example_has_a_sound_form(meta):
    for url in _links(meta.read_text(encoding="utf-8")):
        if url.startswith("#"):
            continue
        assert _problem(url) is None, (meta.parent.name, url, _problem(url))


def test_the_form_check_can_fail():
    for bad in ("", "http://r-graph-gallery.com/x.html", "https://example.org/x.html", "https://r-graph-gallery.com/"):
        assert _problem(bad), bad
    assert _problem("https://r-graph-gallery.com/x.html") is None
    assert "" in _links("an empty one: [a]()")
