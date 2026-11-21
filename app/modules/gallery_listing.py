"""What the gallery lists, and what it says about the examples it left out.

The gallery check (at rebuild, at app start, in tests) names the examples that failed. This module is the one place
that turns the stored index plus that check result into the list the viewer shows: an example that failed is never
listed nor opened, whether the index could be rewritten or not (a read-only gallery folder keeps the old index, which
may still list it). It also builds the lines of the block "not shown, failed the check" (same idea as the rejected
recipes block of HOME). No Shiny import (Two-Category Law); the handler only renders what is returned here.

Consumed by: app/handlers/gallery_handlers.py. App features gate: none here; the gallery is gated by `gallery_enabled`.
If deleted: the viewer would list whatever the stored index lists, failed examples included.

# @deps
# provides: function:matching_examples, constant:FILTER_AXES, constant:NO_MATCH_TEXT, constant:APPLY_RULE_TEXT, function:external_links_new_tab, function:build_listing, function:read_listing, class:GalleryListing, constant:READ_ONLY_LINE, constant:FAILED_LINE, constant:NOTE_LINES
# consumes: app/src/bootloader.py (rejected_gallery_examples, gallery_index_status, stale_gallery_pictures, as data given by the caller)
# consumed_by: app/handlers/gallery_handlers.py, app/tests/test_gallery_listing.py
# doc: .claude/design/recipe_format_spec.md (section 9: D4, DEC48), .claude/design/decisions_2026-11-14/proposals_for_eve.md (G-a, G-b)
# @end_deps
"""
import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

READ_ONLY_LINE = "The gallery folder is read-only, so the list was not rewritten."
FAILED_LINE = "The gallery check could not run, so the list may be out of date."
# Lines that are notes, not the title or an example line; the handler styles them apart.
NOTE_LINES = (READ_ONLY_LINE, FAILED_LINE)


@dataclass(frozen=True)
class GalleryListing:
    """`registry` and `pivot` hold only examples that passed the check; `notice` is empty when nothing was left out."""
    registry: dict = field(default_factory=dict)
    pivot: dict = field(default_factory=dict)
    notice: list = field(default_factory=list)
    # The same lines in blocks, `(title, lines)`; `title` is None for a lone note. The handler styles what is marked here.
    blocks: list = field(default_factory=list)


def build_listing(index: dict, rejected: dict, status: str, stale: Optional[dict] = None) -> GalleryListing:
    """Filter the index by the rejected examples and build the lines to show; the given index is not changed.

    `stale` is `{name: reason}` for the examples whose stored picture is not current (D-0400). Such an
    example stays listed and shown; the notice only says that its picture may not match its recipe and data.
    A name that is also rejected is not repeated here.
    """
    registry = {name: entry for name, entry in index.get("registry", {}).items() if name not in rejected}
    pivot = {
        axis: {term: kept for term, names in terms.items() if (kept := [n for n in names if n not in rejected])}
        for axis, terms in deepcopy(index.get("pivot", {})).items()
    }
    blocks: list = []
    if rejected:
        lines = [f"{name}, {reasons[0] if reasons else 'no reason recorded'}." for name, reasons in sorted(rejected.items())]
        if status == "not_writable":
            lines.append(READ_ONLY_LINE)
        blocks.append((f"{len(rejected)} example(s) not shown, failed the check:", lines))
    stale_shown = {name: reason for name, reason in sorted((stale or {}).items()) if name not in rejected}
    if stale_shown:
        # wording PROVISIONAL (plain words; the owner may change it)
        blocks.append((f"{len(stale_shown)} example(s) shown with a picture that is not current:",
                       [f"{name}: the picture is not current ({reason})." for name, reason in stale_shown.items()]))
    if status == "failed":
        blocks.append((None, [FAILED_LINE]))
    notice = [line for title, lines in blocks for line in ([title] if title else []) + lines]
    return GalleryListing(registry, pivot, notice, blocks)


def read_listing(gallery_dir: Union[str, Path], rejected: dict, status: str, stale: Optional[dict] = None) -> GalleryListing:
    """Read `gallery_index.json` (the only source of what is listed, rules_gallery_standards.md section 5) and filter it.

    A missing or unreadable index gives an empty listing of the stored examples, but the lines about rejected
    examples are still returned, so nothing is left out silently.
    """
    try:
        index = json.loads((Path(gallery_dir) / "gallery_index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        index = {}
    return build_listing(index if isinstance(index, dict) else {}, rejected, status, stale)


# The six taxonomy groups, as the ids of the filter inputs write them (gallery_filter_<axis>); the index pivot calls them by_<axis>.
FILTER_AXES = ("family", "pattern", "difficulty", "geom", "show", "sample_size")

# Texts of the screen (wording PROVISIONAL, owner to confirm).
APPLY_RULE_TEXT = "Ticks act only after you press Apply."
NO_MATCH_TEXT = ("Nothing within this selection. No example matches the ticked filters: tick more values "
                 'or use "Select all" in the filter groups, then press Apply.')


def matching_examples(listing: GalleryListing, applied) -> dict:
    """The examples that match the applied filters as `{id: name}`, sorted by name.

    `applied` maps an axis to the ticked terms; None means no filter was applied yet. A group with nothing ticked does
    not filter (all examples stay), the groups combine by intersection, and the terms of one group by union.
    """
    registry = listing.registry
    valid = set(registry)
    for axis in FILTER_AXES:
        terms = (applied or {}).get(axis)
        if not terms:
            continue
        found: set = set()
        for term in terms:
            found.update(listing.pivot.get(f"by_{axis}", {}).get(term, []))
        valid &= found
    return dict(sorted(((rid, registry[rid]["name"]) for rid in valid), key=lambda item: item[1]))


_A_OPEN = re.compile(r"<a\b([^>]*)>", re.IGNORECASE)
_HREF = re.compile(r"""\bhref\s*=\s*["']?\s*https?://""", re.IGNORECASE)


def external_links_new_tab(html: str) -> str:
    """Make every external (http/https) link of a guidance text open in a new tab, so the user keeps the app page.

    An internal anchor (``#section``) or a relative link is left as it is. Any target or rel the
    text already had on an external link is replaced by ``_blank`` and ``noopener noreferrer``.
    """

    def _fix(m: "re.Match[str]") -> str:
        attrs = m.group(1)
        if not _HREF.search(attrs):
            return m.group(0)
        attrs = re.sub(r"""\s(target|rel)\s*=\s*("[^"]*"|'[^']*'|\S+)""", "", attrs, flags=re.IGNORECASE)
        return f'<a{attrs} target="_blank" rel="noopener noreferrer">'

    return _A_OPEN.sub(_fix, html)
