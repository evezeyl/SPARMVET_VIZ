# engine: python-plotnine (puts the installed plotnine version into the key of a gallery picture)
"""The key that says whether the stored picture of a Gallery example is current (D-0400, built).

The picture `preview_plot.png` of an example is drawn by `assets/scripts/gallery_previews.py`. At the moment that script
draws (or confirms) a picture it writes a small file beside it, `preview_plot.picture_key.json`, that holds the key of
what the picture was drawn from. At app start the Gallery compares the stored key with the key of the files now. A
different key, a missing file or an unreadable file means "picture not current". Nothing is drawn and no pixel is
compared at start, and the key is written by no other code than the drawing script.

The key is made of three labelled parts, so that the notice can say which one changed:
  recipe    SHA256 of the bytes of `data_analysis_recipe.yaml`
  data      SHA256 of the bytes of `example_data.tsv`
  plotnine  the installed version of plotnine (decided to be in: a new version triggers a redraw and a look)

PROVISIONAL (D-0400 leaves open "which inputs enter the key"; the owner may change this): matplotlib, the fonts, the
polars and transformer versions, the picture size and dpi (`PREVIEW_SIZE`), the code of VizFactory and its default theme,
and the seed are NOT in the key. Evidence and reasons: the report of the task GALLERY-PICTURE-CURRENT. A recipe that
`!include`s another file is not covered (no shipped example does; a test fails if one appears).

The hashing is plain SHA256 as in `app/modules/cache_keys.py` (`hash_text`); a library may not import `app/`
(rules_runtime_environment.md section 4), so the three lines are written here, not shared.

No Shiny import. If deleted: the Gallery cannot say whether a picture is current.

# @deps
# provides: function:picture_key_parts, function:write_picture_key, function:picture_status, function:stale_pictures, constant:KEY_FILE
# consumes: libs/viz_gallery/src/viz_gallery/example_recipe.py (DATA_FILE)
# consumed_by: assets/scripts/gallery_previews.py, app/src/bootloader.py, app/modules/gallery_listing.py, app/tests/test_gallery_picture_key.py
# doc: .claude/knowledge/decision_ledger.md (D-0400), .claude/rules/rules_gallery_standards.md (section 6)
# @end_deps
"""
import hashlib
import json
from importlib import metadata
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple, Union

from viz_gallery.example_recipe import DATA_FILE

RECIPE_FILE = "data_analysis_recipe.yaml"
# Not `*.key`: the repository ignores that pattern (secrets).
KEY_FILE = "preview_plot.picture_key.json"
# The words of the parts as the notice says them.
PART_WORDS = {"recipe": "recipe", "data": "data", "plotnine": "plot library (plotnine)"}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plotnine_version() -> str:
    try:
        return metadata.version("plotnine")
    except metadata.PackageNotFoundError:
        return "unknown"


def picture_key_parts(example_dir: Union[str, Path], plotnine: Optional[str] = None) -> Dict[str, str]:
    """The three parts of the key of an example; raises OSError when the recipe or the data file cannot be read.

    `plotnine` is given only by tests, to stand in for another installed version.
    """
    folder = Path(example_dir)
    return {"recipe": _digest(folder / RECIPE_FILE), "data": _digest(folder / DATA_FILE),
            "plotnine": plotnine if plotnine is not None else plotnine_version()}


def key_of(parts: Dict[str, str]) -> str:
    """The one key: SHA256 of the labelled parts."""
    return hashlib.sha256("\n".join(f"{name}={parts[name]}" for name in sorted(parts)).encode("utf-8")).hexdigest()


def write_picture_key(example_dir: Union[str, Path], parts: Dict[str, str]) -> Path:
    """Store the key beside the picture. Called by the drawing script only, with the parts it took before it drew."""
    target = Path(example_dir) / KEY_FILE
    target.write_text(json.dumps({"key": key_of(parts), "parts": parts}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def picture_status(example_dir: Union[str, Path], plotnine: Optional[str] = None) -> Tuple[bool, str]:
    """`(current, reason)` of one picture; `reason` is a plain phrase (wording PROVISIONAL), empty when current. Never raises."""
    folder = Path(example_dir)
    try:
        stored = json.loads((folder / KEY_FILE).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False, "no key is stored with it"
    except (OSError, ValueError):
        return False, "the key stored with it cannot be read"
    stored_parts = stored.get("parts") if isinstance(stored, dict) else None
    if not isinstance(stored_parts, dict) or not isinstance(stored.get("key"), str) or key_of(stored_parts) != stored["key"]:
        return False, "the key stored with it cannot be read"
    try:
        now = picture_key_parts(folder, plotnine)
    except OSError:
        return False, "the recipe or the data cannot be read"
    if set(stored_parts) == set(now) and key_of(now) == stored["key"]:
        return True, ""
    changed = [PART_WORDS[name] for name in now if stored_parts.get(name) != now[name]] or ["inputs"]
    return False, f"the {' and '.join(changed)} changed since it was drawn"


def stale_pictures(gallery_dir: Union[str, Path], names: Iterable[str]) -> Dict[str, str]:
    """The examples among `names` whose picture is not current, as `{name: reason}`."""
    stale: Dict[str, str] = {}
    for name in sorted(names):
        current, reason = picture_status(Path(gallery_dir) / name)
        if not current:
            stale[name] = reason
    return stale
