#!/usr/bin/env python3
"""Check the gallery examples and rebuild `gallery_index.json`, the list the Gallery reads.

Every example folder is judged by the checker of the recipe format (`check_recipe`, profile `gallery`), with the
registries of the actions and of the plot components. An example that passes is listed in the index. An example that
fails is left out, and the reason is printed here and written in the index under `metadata.rejected`, so it is never
dropped silently (spec section 9, decision DEC48).

Without --apply nothing is written: the script only reports which examples pass and which fail, and why.
With --apply the index file of the gallery folder is written.

Run from the project root.

Examples:
  PYTHONPATH=. .venv/bin/python assets/scripts/refresh_gallery.py
  PYTHONPATH=. .venv/bin/python assets/scripts/refresh_gallery.py --apply
  PYTHONPATH=. .venv/bin/python assets/scripts/refresh_gallery.py --gallery assets/gallery_data --apply
"""
import argparse
import contextlib
import io
import sys
from pathlib import Path

from app.modules.gallery_examples import check_gallery, rebuild_gallery_index


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gallery", default="assets/gallery_data", help="the gallery folder, one example per subfolder (default: assets/gallery_data)")
    parser.add_argument("--apply", action="store_true", help="write gallery_index.json (default: only report)")
    args = parser.parse_args(argv)
    gallery = Path(args.gallery)
    if not gallery.is_dir():
        print(f"The gallery folder {gallery} does not exist. Fix: pass --gallery")
        return 2
    if args.apply:
        with contextlib.redirect_stdout(io.StringIO()):
            index = rebuild_gallery_index(gallery)
        accepted, rejected = list(index["registry"]), index["metadata"]["rejected"]
        coverage = index["metadata"]["coverage"]
    else:
        examples = check_gallery(gallery)
        accepted, rejected, coverage = list(examples.accepted), examples.rejected, sorted(examples.coverage)
    print(f"Checks that ran: {', '.join(coverage)}.")
    print(f"Accepted: {len(accepted)} example(s).")
    for name, reasons in rejected.items():
        print(f"Left out: {name}")
        for reason in reasons:
            print(f"    {reason}")
    print(f"{'gallery_index.json written' if args.apply else 'Nothing written. Run again with --apply to write gallery_index.json'}: "
          f"{len(accepted)} listed, {len(rejected)} left out.")
    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main())
