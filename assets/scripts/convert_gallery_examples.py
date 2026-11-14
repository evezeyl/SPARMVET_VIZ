#!/usr/bin/env python3
"""Convert the gallery examples from the old compact form to standard recipes (format 1, spec section 9).

The old `data_analysis_recipe.yaml` of an example had its own shape: `info` with the name, the date and six taxonomy
values, `data_path`, one plot under a root-level `plots`, and `wrangling`. This script rewrites it as a standard
recipe, the same format as every other recipe:

  - `id` is the folder name; `spec_version`, `data_engine` and `plot_engine` are written;
  - `info.label` is the old name; `info.description` is the "Suitability" paragraph of `example_meta.md`;
  - one data schema `example` reads the example's own `example_data.tsv`, with `null_values`, `strip` and a typed
    data contract (`input_fields`) GENERATED from the file and printed here so that a person reviews it;
  - one group, one plot; the five taxonomy values go to `taxonomy` on the plot entry. `geom` is not written any more:
    it is read from the first geom_ or stat_ layer of the plot;
  - steps: `tier1` and `tier2` go to the schema, `tier3` goes to `steps: {tier3: [...]}` on the plot entry.

The result is checked with `check_recipe` (profile `gallery`) before it is written. An example that the checker
refuses is NOT converted and its reasons are printed (for example steps in tier 3: the engine does not read tier 3
yet). A file with `#` comments is not converted either: a rewrite would lose them.

It also sets the tag strip of every `example_meta.md` (the `> ...` line under the heading) from the taxonomy of the
recipe, for converted and for already standard examples. No other line of that file is touched.

Without --apply nothing is written: the script lists what it would do. Safe to run twice.

Examples:
  .venv/bin/python assets/scripts/convert_gallery_examples.py
  .venv/bin/python assets/scripts/convert_gallery_examples.py --only bar_simple dumbbell
  .venv/bin/python assets/scripts/convert_gallery_examples.py --apply
"""
import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml

from utils.recipe_check import check_recipe
from viz_gallery.example_recipe import DATA_FILE, data_contract, data_summary, dump_example, example_recipe, plot_summary
from viz_gallery.gallery_manager import META_FILE, RECIPE_FILE
from viz_gallery.taxonomy import example_taxonomy, first_geom, tag_strip, with_tag_strip

OLD_TOP_KEYS = {"info", "data_path", "plots", "wrangling"}
OLD_INFO_KEYS = {"name", "submission_date", "family", "pattern", "difficulty", "geom", "show", "sample_size"}
OLD_TIERS = {"tier1", "tier2", "tier3"}
_COMMENT = re.compile(r"(^|\s)#")


@dataclass
class Outcome:
    """What the script found for one example folder."""
    name: str
    status: str                                   # converted, standard, not converted
    lines: List[str] = field(default_factory=list)  # what a person must read
    recipe_text: Optional[str] = None             # the new recipe, when converted
    meta_text: Optional[str] = None               # the new example_meta.md, when its tag strip changes


def suitability(markdown: str) -> str:
    """The first paragraph under the `### Suitability` heading of an `example_meta.md`, on one line; empty if none."""
    lines = markdown.split("\n")
    start = next((i for i, line in enumerate(lines) if line.strip().lower().startswith("### suitability")), None)
    if start is None:
        return ""
    paragraph: List[str] = []
    for line in lines[start + 1:]:
        if line.startswith("#") or (paragraph and not line.strip()):
            break
        if line.strip():
            paragraph.append(line.strip())
    return " ".join(paragraph)


def old_form_problems(raw: object, text: str) -> List[str]:
    """Why this old file cannot be converted mechanically; an empty list means it has the known shape."""
    if not isinstance(raw, dict):
        return ["the file is not a YAML mapping"]
    problems = []
    if any(_COMMENT.search(line) for line in text.split("\n")):
        problems.append("the file has # comments and a rewrite would lose them. Fix: convert this example by hand")
    for key in sorted(set(raw) - OLD_TOP_KEYS):
        problems.append(f"the key {key!r} is not part of the old gallery form. Fix: convert this example by hand")
    info = raw.get("info")
    if not isinstance(info, dict) or not info.get("name"):
        problems.append("info.name is missing")
    else:
        for key in sorted(set(info) - OLD_INFO_KEYS):
            problems.append(f"info.{key} is not part of the old gallery form. Fix: convert this example by hand")
    plots = raw.get("plots")
    if not isinstance(plots, dict) or len(plots) != 1 or not isinstance(next(iter(plots.values())), dict):
        problems.append("the example must hold exactly one plot under plots")
    if raw.get("data_path") != DATA_FILE:
        problems.append(f"data_path is {raw.get('data_path')!r}; the data of an example is its own {DATA_FILE}")
    wrangling = raw.get("wrangling", {})
    if not isinstance(wrangling, dict) or set(wrangling) - OLD_TIERS or any(not isinstance(v, list) for v in wrangling.values()):
        problems.append("wrangling must be a mapping of tier1, tier2, tier3 to lists")
    return problems


def data_path_for(folder: Path, root: Path) -> str:
    """The `source.path` of an example: its own data file, written relative to the project root."""
    relative = os.path.relpath(folder.resolve(), root.resolve()).replace(os.sep, "/")
    if relative.startswith(".."):
        raise ValueError(f"the gallery folder {folder} is outside the project root {root}. Fix: pass --root")
    return f"./{relative}/{DATA_FILE}"


def convert_bundle(folder: Path, root: Path) -> Outcome:
    """Read one example folder and say what to write; nothing is written here."""
    name = folder.name
    recipe_path, meta_path, data_file = folder / RECIPE_FILE, folder / META_FILE, folder / DATA_FILE
    if not recipe_path.is_file():
        return Outcome(name, "not converted", [f"no {RECIPE_FILE} in the folder"])
    text = recipe_path.read_text(encoding="utf-8")
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as error:
        return Outcome(name, "not converted", [f"{RECIPE_FILE} is not valid YAML: {' '.join(str(error).split())}"])
    meta = meta_path.read_text(encoding="utf-8") if meta_path.is_file() else None

    if isinstance(raw, dict) and "spec_version" in raw:
        outcome = Outcome(name, "standard")
        recipe = raw
    else:
        problems = old_form_problems(raw, text)
        if not data_file.is_file():
            problems.append(f"{DATA_FILE} is missing")
        if problems:
            return Outcome(name, "not converted", problems)
        info, wrangling = raw["info"], raw.get("wrangling") or {}
        plot_id, plot_spec = next(iter(raw["plots"].items()))
        fields, notes = data_contract(data_file)
        description = suitability(meta) if meta else ""
        recipe = example_recipe(
            example_id=name, label=info["name"], description=description, submission_date=info.get("submission_date"),
            data_path=data_path_for(folder, root), fields=fields, taxonomy=info, plot_id=plot_id, plot_spec=plot_spec,
            data_description=data_summary(data_file), plot_description=plot_summary(plot_spec),
            tier1=wrangling.get("tier1"), tier2=wrangling.get("tier2"), tier3=wrangling.get("tier3"))
        errors = check_recipe(recipe, "gallery", file_stem=name).errors
        if errors:
            return Outcome(name, "not converted", [problem.text() for problem in errors])
        outcome = Outcome(name, "converted", recipe_text=dump_example(recipe))
        outcome.lines.append("data contract (review it): " + ", ".join(
            f"{column}: {definition['type']}" for column, definition in fields.items()))
        outcome.lines += [f"review: {note}" for note in notes]
        if not description:
            outcome.lines.append("review: no '### Suitability' paragraph was found, so info.description is not written")
        derived = first_geom(plot_spec)
        if info.get("geom") != derived:
            outcome.lines.append(f"review: the typed geom was {info.get('geom')!r}; the geom read from the layers is {derived!r}")

    if meta is None:
        outcome.lines.append(f"{META_FILE} is missing, so its tag strip cannot be set")
        return outcome
    try:
        strip = tag_strip(example_taxonomy(recipe))
        new_meta = with_tag_strip(meta, strip)
    except (ValueError, KeyError, TypeError) as error:
        outcome.lines.append(f"the tag strip of {META_FILE} cannot be set: {error}")
        return outcome
    if new_meta != meta:
        outcome.meta_text = new_meta
        outcome.lines.append(f"tag strip: {strip}")
    return outcome


def convert(gallery: Path, root: Path, only: Optional[List[str]] = None, apply: bool = False) -> List[Outcome]:
    """Convert the example folders of `gallery` (all, or the ones named in `only`); write only with `apply`."""
    folders = sorted(d for d in gallery.iterdir() if d.is_dir())
    unknown = sorted(set(only or []) - {d.name for d in folders})
    if unknown:
        raise ValueError(f"no such example folder in {gallery}: {', '.join(unknown)}")
    outcomes = []
    for folder in folders:
        if only and folder.name not in only:
            continue
        outcome = convert_bundle(folder, root)
        if apply:
            if outcome.recipe_text is not None:
                (folder / RECIPE_FILE).write_text(outcome.recipe_text, encoding="utf-8")
            if outcome.meta_text is not None:
                (folder / META_FILE).write_text(outcome.meta_text, encoding="utf-8")
        outcomes.append(outcome)
    return outcomes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gallery", default="assets/gallery_data", help="the gallery folder, one example per subfolder (default: assets/gallery_data)")
    parser.add_argument("--root", default=".", help="the project root that the data path of a recipe is relative to (default: here)")
    parser.add_argument("--only", nargs="+", metavar="NAME", help="convert only these example folders")
    parser.add_argument("--apply", action="store_true", help="write the changes (default: only list them)")
    args = parser.parse_args(argv)
    gallery = Path(args.gallery)
    if not gallery.is_dir():
        print(f"The gallery folder {gallery} does not exist. Fix: pass --gallery")
        return 2
    try:
        outcomes = convert(gallery, Path(args.root), args.only, args.apply)
    except ValueError as error:
        print(str(error))
        return 2
    verb = {"converted": "converted" if args.apply else "would convert", "standard": "already a standard recipe",
            "not converted": "NOT converted"}
    for outcome in outcomes:
        strip_changed = outcome.meta_text is not None
        if outcome.status == "standard" and not strip_changed and not outcome.lines:
            continue
        print(f"{outcome.name}: {verb[outcome.status]}")
        for line in outcome.lines:
            print(f"    {line}")
    counts = {status: sum(1 for o in outcomes if o.status == status) for status in verb}
    strips = sum(1 for o in outcomes if o.meta_text is not None)
    print(f"{verb['converted']}: {counts['converted']}; already standard: {counts['standard']}; "
          f"not converted: {counts['not converted']}; tag strips {'set' if args.apply else 'to set'}: {strips}."
          + ("" if args.apply else " Run again with --apply to write."))
    return 1 if counts["not converted"] else 0


if __name__ == "__main__":
    sys.exit(main())
