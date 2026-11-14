#!/usr/bin/env python3
"""Draw the preview picture of the gallery examples by the app's own path, and compare with the committed pictures.

The picture of an example is drawn exactly as HOME draws a plot: the recipe is loaded by ConfigManager, its table is
built by DataOrchestrator, the plot is rendered by VizFactory (spec section 9, finding G2). An example that fails the
gallery check, or that the app cannot load, gets no picture and its reason is printed. Every picture has one standard
size, 960 x 600 pixels (finding G5).

Without --apply nothing in the gallery changes: the new pictures are written to --out and each is compared, pixel by
pixel, with the committed `preview_plot.png` of its example:

  identical   same size, every pixel equal
  size only   another size; drawn again at the old size, every pixel is equal (the content did not change)
  differs N%  the content changed: N percent of the pixels differ (compared at the old size)
  new         the example had no picture

With --apply the new `preview_plot.png` and `preview_thumb.png` are written into the example folders, but only for the
pictures whose content did not change (identical, size only) and for new ones. A picture whose content differs is
written only with --changed as well: look at it first, a figure must never change without a person seeing it.

Run from the project root (the data path of a recipe is relative to it).

Examples:
  PYTHONPATH=. .venv/bin/python assets/scripts/gallery_previews.py
  PYTHONPATH=. .venv/bin/python assets/scripts/gallery_previews.py --only bar_simple dumbbell
  PYTHONPATH=. .venv/bin/python assets/scripts/gallery_previews.py --apply
  PYTHONPATH=. .venv/bin/python assets/scripts/gallery_previews.py --apply --changed --only jitter_strip
"""
import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np
from PIL import Image

from app.modules.gallery_examples import PREVIEW_SIZE, check_gallery, render_example
from viz_gallery.gallery_manager import PREVIEW_FILE, THUMB_FILE

THUMB_BOX = (100, 75)


@dataclass
class Row:
    """The comparison of one example."""
    name: str
    verdict: str            # identical, size only, differs, new, error
    detail: str = ""
    new_picture: Optional[Path] = None

    @property
    def content_unchanged(self) -> bool:
        return self.verdict in ("identical", "size only", "new")


def _pixels(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB")).astype(int)


def percent_different(first: Path, second: Path) -> float:
    """The percentage of pixels that differ between two pictures of the same size."""
    a, b = _pixels(first), _pixels(second)
    if a.shape != b.shape:
        raise ValueError(f"the pictures have different sizes: {a.shape[1]}x{a.shape[0]} and {b.shape[1]}x{b.shape[0]}")
    return 100.0 * float((np.abs(a - b).sum(axis=2) > 0).mean())


def size_of(path: Path) -> dict:
    """How a committed picture was drawn: `{width, height, dpi}` read from the file (pixels and dots per inch)."""
    with Image.open(path) as image:
        width, height = image.size
        dpi = round(float(image.info.get("dpi", (PREVIEW_SIZE["dpi"],))[0]))
    return {"width": width / dpi, "height": height / dpi, "dpi": dpi}


def compare(name: str, new_picture: Path, old_picture: Path, redraw: Callable[[dict, Path], Path]) -> Row:
    """Compare the new picture of an example with its committed one; `redraw(size, path)` draws it at another size."""
    if not old_picture.is_file():
        return Row(name, "new", "the example had no picture", new_picture)
    with Image.open(new_picture) as new, Image.open(old_picture) as old:
        new_size, old_size = new.size, old.size
    if new_size == old_size:
        percent = percent_different(new_picture, old_picture)
        return Row(name, "identical" if percent == 0 else "differs", "" if percent == 0 else f"{percent:.2f}% of the pixels", new_picture)
    was = f"{old_size[0]}x{old_size[1]} before, {new_size[0]}x{new_size[1]} now"
    at_old_size = redraw(size_of(old_picture), new_picture.with_name(f"{name}_at_old_size.png"))
    with Image.open(at_old_size) as again:
        if again.size != old_size:
            return Row(name, "differs", f"{was}; the old size could not be drawn again, so the content was not compared", new_picture)
    percent = percent_different(at_old_size, old_picture)
    if percent == 0:
        return Row(name, "size only", f"{was}; identical when drawn at the old size", new_picture)
    return Row(name, "differs", f"{percent:.2f}% of the pixels at the old size ({was})", new_picture)


def write_thumb(picture: Path, thumb: Path) -> None:
    with Image.open(picture) as image:
        image.thumbnail(THUMB_BOX, Image.LANCZOS)
        image.save(thumb)


def run(gallery: Path, out: Path, only: Optional[List[str]] = None, apply: bool = False, changed: bool = False) -> List[Row]:
    """Draw and compare the pictures of the examples; with `apply` write them into the gallery (see the module text)."""
    examples = check_gallery(gallery)
    known = set(examples.accepted) | set(examples.rejected)
    unknown = sorted(set(only or []) - known)
    if unknown:
        raise ValueError(f"no such example folder in {gallery}: {', '.join(unknown)}")
    rows: List[Row] = []
    work = out / "work"
    for name in sorted(known):
        if only and name not in only:
            continue
        if name in examples.rejected:
            rows.append(Row(name, "error", "not drawn, the example fails the gallery check: " + " | ".join(examples.rejected[name])))
            continue
        folder = gallery / name

        def redraw(size: dict, path: Path, folder: Path = folder) -> Path:
            return render_example(folder, work, path, size=size)

        try:
            new_picture = render_example(folder, work, out / f"{name}.png")
            row = compare(name, new_picture, folder / PREVIEW_FILE, redraw)
        except Exception as error:  # noqa: BLE001 - one example that cannot be drawn must not stop the others
            row = Row(name, "error", f"not drawn: {type(error).__name__}: {' '.join(str(error).split())[:300]}")
        if apply and row.new_picture is not None and (row.content_unchanged or changed):
            if row.verdict != "identical":
                shutil.copyfile(row.new_picture, folder / PREVIEW_FILE)
            if row.verdict != "identical" or not (folder / THUMB_FILE).is_file():
                write_thumb(folder / PREVIEW_FILE, folder / THUMB_FILE)
            row.detail = (row.detail + "; " if row.detail else "") + ("kept" if row.verdict == "identical" else "written")
        rows.append(row)
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gallery", default="assets/gallery_data", help="the gallery folder, one example per subfolder (default: assets/gallery_data)")
    parser.add_argument("--out", default="tmpAI/gallery_previews", help="where the new pictures are drawn for comparison (default: tmpAI/gallery_previews)")
    parser.add_argument("--only", nargs="+", metavar="NAME", help="only these example folders")
    parser.add_argument("--apply", action="store_true", help="write the new pictures whose content did not change, and the new ones, into the gallery")
    parser.add_argument("--changed", action="store_true", help="with --apply: also write the pictures whose content differs (look at them first)")
    args = parser.parse_args(argv)
    gallery = Path(args.gallery)
    if not gallery.is_dir():
        print(f"The gallery folder {gallery} does not exist. Fix: pass --gallery")
        return 2
    if args.changed and not args.apply:
        print("--changed needs --apply")
        return 2
    try:
        rows = run(gallery, Path(args.out), args.only, args.apply, args.changed)
    except ValueError as error:
        print(str(error))
        return 2
    width = max((len(row.name) for row in rows), default=7)
    print(f"{'example'.ljust(width)}  verdict    detail")
    for row in rows:
        print(f"{row.name.ljust(width)}  {row.verdict.ljust(9)}  {row.detail}")
    counts = {verdict: sum(1 for row in rows if row.verdict == verdict) for verdict in ("identical", "size only", "differs", "new", "error")}
    print("; ".join(f"{verdict}: {count}" for verdict, count in counts.items()) + f". New pictures are in {args.out}.")
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
