#!/usr/bin/env python3
"""Draw every plot of every recipe by the app's own path, store the pictures, and later prove they did not change.

Why: a change of the recipe format must leave every picture identical. The golden baseline compares tables and the data
behind a plot, not pictures; the gallery preview check compares only the gallery pictures. This tool compares the
pictures of ALL plots of ALL recipes, pixel by pixel.

Which recipes: every `*.yaml` directly inside each recipe folder, the way the app finds them (sub-folders hold fragments and
plot files, they are not recipes; each is listed as skipped). A recipe that the load gate rejects (structure check, then data
against its contract: the two checks of HOME's gate) is not drawn, and is listed with its reason, never dropped silently.
A plot that cannot be drawn is recorded with its error text. Each plot is drawn as HOME draws the Result plot: the
orchestrator builds the tier 1 and tier 2 table of the plot's target, and `VizFactory.render` draws it. Every picture has
the same fixed size and dpi (default 8 x 5 inches at 120 dpi, 960 x 600 pixels).

A plot is identified by recipe id + analysis group id + plot id (never by a file shape or a file hash), so the same check
can compare an old and a new recipe file format.

Modes:
  --write DIR   draw all plots into DIR (one PNG per plot) and write DIR/manifest.json: recipe, group, plot, picture file,
                size, pixel hash, status. Each plot is drawn --repeat times (default 2); if two draws of one plot are not
                pixel-identical the plot is named "unstable" in the manifest, with the number of differing pixels.
  --check DIR   draw again and compare with the pictures stored in DIR. Per plot: identical, different (number of differing
                pixels; a picture with the stored one, the new one and the difference side by side is saved in --out),
                missing (stored, not drawn now), new (drawn now, not stored), error-changed (drawn before, error now, or
                the other way, or another error text). Exit code 0 only when everything is identical and the set of plots
                is the same. A plot stored as unstable is reported "unstable, not compared" and does not fail the check.

Run from the root of the checkout that holds this script (the data path of a recipe is relative to it). Defaults: recipe
folders are the four folders of `config/data_analysis_recipes` and `app/tests/equality/recipes`; data root `assets/test_data`.

Which code draws: the shared `.venv` has editable installs of the libraries that point at the MAIN folder. With a plain
`PYTHONPATH=.` only `app/` and `assets/` come from this checkout and `libs/` comes from the main folder, so after a change in
`libs/` the check would compare pictures drawn by the OLD library code and prove nothing. The tool therefore looks, before it
draws, where `app` and every package of `libs/*/src` would be imported from. If one comes from outside the checkout this script
lives in, it STOPS with a plain message (exit code 2), unless `--allow-outside-checkout` is given. The folder of every library is
printed and written to the manifest under "libraries". Put the checkout's libraries first with this command (`$PY` is the
python of the shared `.venv`, here the one of the main folder):

  PYTHONHASHSEED=0 PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" $PY assets/scripts/recipe_pictures.py --check DIR

Why `PYTHONHASHSEED=0` (a known defect, found 2026-11-18): the plot `complex_template::Overview::gene_presence_by_country`
(a stacked bar with a missing-value group) is drawn with the missing-value group at the bottom of a stack or at the top
depending on Python's hash seed (the table and the data frame given to the plot are identical; verified: seed 4 differs, seeds
0, 1, 2, 3, 5 are the same). It is in the drawing step, not in this tool. Until it is decided what to do, the documented command
fixes the seed so that a check is repeatable; the seed used is printed and written to the manifest ("python_hash_seed"), and
a check made with another seed says so. A random seed (variable not set) gives a failing check for that plot on some runs.

Examples (the prefix is the same for every mode):
  PYTHONHASHSEED=0 PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" $PY assets/scripts/recipe_pictures.py --write tmpAI/pictures_before
  PYTHONHASHSEED=0 PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" $PY assets/scripts/recipe_pictures.py --check tmpAI/pictures_before --out tmpAI/pictures_check
  PYTHONHASHSEED=0 PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" $PY assets/scripts/recipe_pictures.py --write /tmp/p --recipe-dir config/data_analysis_recipes/retest

# @deps
# provides: script:recipe_pictures
# consumes: app/modules/orchestrator.py, app/modules/cache_keys.py, app/modules/data_analysis_recipe_validator.py, libs/utils/src/utils/config_loader.py, libs/viz_factory/src/viz_factory/viz_factory.py
# consumed_by: app/tests/test_recipe_pictures.py
# doc: .claude/rules/rules_asset_scripts.md
# @end_deps
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

import numpy as np
import yaml
from PIL import Image

DEFAULT_RECIPE_DIRS = [
    "config/data_analysis_recipes/pipelines",
    "config/data_analysis_recipes/templates",
    "config/data_analysis_recipes/retest",
    "config/data_analysis_recipes/experimental",
    "app/tests/equality/recipes",
]
DEFAULT_DATA_ROOT = "assets/test_data"
DEFAULT_PALETTES = "config/palettes.yaml"
DEFAULT_SIZE = {"width": 8, "height": 5, "dpi": 120}
MANIFEST = "manifest.json"
SEP = "::"
CHECKOUT = Path(__file__).resolve().parents[2]


def plot_key(recipe: str, group: str, plot: str) -> str:
    """The identity of a plot (or, with empty group and plot, of a recipe that could not be drawn at all)."""
    return f"{recipe}{SEP}{group}{SEP}{plot}"


def short(error: BaseException) -> str:
    return f"{type(error).__name__}: {' '.join(str(error).split())[:400]}"


def checkout_packages(checkout: Path = CHECKOUT) -> List[str]:
    """`app` and every package of the libraries of this checkout (`libs/*/src/<package>`)."""
    found = {p.name for src in (checkout / "libs").glob("*/src") for p in src.iterdir()
             if p.is_dir() and not p.name.startswith((".", "_")) and not p.name.endswith(".egg-info")}
    return ["app"] + sorted(found)


def origin_of(name: str) -> str:
    """The folder a package is (or would be) imported from; "not found" when Python cannot find it.

    A package that is already imported answers from the module itself. Otherwise the import system is asked without importing
    (`find_spec`): the first entry of the search path wins, as for a namespace package (today `viz_gallery`), whose search path
    also lists other copies behind the first one.
    """
    module = sys.modules.get(name)
    if module is not None and getattr(module, "__file__", None):
        return str(Path(module.__file__).resolve().parent)
    if module is not None and getattr(module, "__path__", None):
        return str(Path(list(module.__path__)[0]).resolve())
    spec = importlib.util.find_spec(name)
    if spec is None:
        return "not found"
    if spec.origin and spec.origin != "namespace" and spec.has_location:
        return str(Path(spec.origin).resolve().parent)
    return str(Path(list(spec.submodule_search_locations)[0]).resolve())


def library_origins(checkout: Path = CHECKOUT) -> dict:
    """{package: folder it is imported from} for every package of this checkout."""
    return {name: origin_of(name) for name in checkout_packages(checkout)}


def outside_checkout(origins: dict, checkout: Path = CHECKOUT) -> dict:
    """The packages whose folder is not inside `checkout` (a package that cannot be found counts as outside)."""
    return {name: where for name, where in origins.items() if where == "not found" or checkout.resolve() not in Path(where).parents}


def outside_message(outside: dict, checkout: Path = CHECKOUT) -> str:
    """Plain message: which packages, where they come from, what to do (D-0050: never draw with another copy of the code)."""
    lines = [f"  {name}: {where}" for name, where in sorted(outside.items())]
    return ("STOPPED: these packages are imported from outside this checkout (" + str(checkout) + "):\n" + "\n".join(lines) +
            "\nThe pictures would be drawn by another copy of the code, so the check would prove nothing about this checkout."
            "\nSuggestion: put the libraries of this checkout first, from its root:"
            "\n  PYTHONPATH=\".:$(ls -d libs/*/src | paste -sd:)\" <venv python> assets/scripts/recipe_pictures.py ..."
            "\nOnly if you know the other copy is the one you mean, add --allow-outside-checkout.")


def hash_seed() -> str:
    """The value of PYTHONHASHSEED, or "random" when it is not set (Python then takes a new seed at every start)."""
    return os.environ.get("PYTHONHASHSEED") or "random"


def seed_note(stored_seed: Optional[str], now_seed: str) -> str:
    """One plain line about the hash seed of this run and of the stored set (a known plot depends on it, see --help)."""
    if stored_seed is None:
        return f"hash seed of this run: {now_seed}; the stored manifest does not record its seed"
    if stored_seed == now_seed:
        return f"hash seed of this run: {now_seed} (same as the stored set)"
    return (f"hash seed of this run: {now_seed}; the stored set was drawn with: {stored_seed}. A plot with a missing-value group "
            f"is known to change with the seed (see --help); if only it differs, rerun with PYTHONHASHSEED={stored_seed if stored_seed != 'random' else 0}")


def discover(recipe_dirs: List[Path]) -> tuple[list, list]:
    """Recipes the way the app finds them: `*.yaml` directly inside a folder. Returns (recipes, skipped)."""
    recipes, skipped = [], []
    seen: dict = {}
    for folder in recipe_dirs:
        if not folder.is_dir():
            skipped.append({"path": str(folder), "reason": "the recipe folder does not exist"})
            continue
        for entry in sorted(folder.iterdir()):
            if entry.is_dir():
                skipped.append({"path": str(entry), "reason": "sub-folder: holds the fragments and plot files of a recipe, not recipes"})
            elif entry.suffix == ".yaml":
                if entry.stem in seen:
                    skipped.append({"path": str(entry), "reason": f"same recipe id as {seen[entry.stem]}; one id names one recipe"})
                    continue
                seen[entry.stem] = str(entry)
                recipes.append((entry.stem, entry))
            else:
                skipped.append({"path": str(entry), "reason": "not a .yaml file"})
    return recipes, skipped


def gate_problems(path: Path, data_root: Path) -> List[str]:
    """The two checks of HOME's load gate: structure, then the data against the declared contract."""
    from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe, validate_data_analysis_recipe_data
    problems = validate_data_analysis_recipe(path)
    if not problems:
        try:
            problems = validate_data_analysis_recipe_data(path, data_root)
        except Exception as error:  # noqa: BLE001
            problems = [f"data-vs-contract check could not run: {short(error)}"]
    return [str(p) for p in problems]


def plots_of(raw: dict) -> list:
    """(group id, plot id, target collection) of every plot, in file order. The one place that knows the recipe shape."""
    found = []
    for group_id, group in (raw.get("analysis_groups") or {}).items():
        for plot_id, entry in ((group or {}).get("plots") or {}).items():
            found.append((str(group_id), str(plot_id), ((entry or {}).get("spec") or {}).get("target_dataset")))
    return found


def collections_of(raw: dict) -> list:
    found = set((raw.get("joins") or {}).keys())
    found.update(target for _, _, target in plots_of(raw) if target)
    return sorted(found)


def load_palettes(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("palettes") or None


def pixels(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB")).astype(np.int16)


def pixel_hash(array: np.ndarray) -> str:
    return hashlib.sha256(f"{array.shape}".encode() + array.astype(np.uint8).tobytes()).hexdigest()


def differing_pixels(a: np.ndarray, b: np.ndarray) -> int:
    """Number of pixels that differ; pictures of another size differ in all the pixels of the larger one."""
    if a.shape != b.shape:
        return int(max(a.shape[0] * a.shape[1], b.shape[0] * b.shape[1]))
    return int((np.abs(a - b).sum(axis=2) > 0).sum())


def draw_recipe(recipe_id: str, path: Path, data_root: Path, palettes: Optional[dict], out: Path, size: dict, repeat: int) -> list:
    """Draw every plot of one recipe. Returns the records (one per plot; one for the recipe if it cannot be drawn at all)."""
    import matplotlib
    matplotlib.use("Agg")
    import polars as pl
    from app.modules.cache_keys import clear_data_analysis_recipe_cache
    from app.modules.orchestrator import DataOrchestrator
    from utils.config_loader import ConfigManager
    from viz_factory.viz_factory import VizFactory

    def failure(group: str, plot: str, status: str, error: str) -> dict:
        return {"key": plot_key(recipe_id, group, plot), "recipe": recipe_id, "group": group, "plot": plot, "status": status, "error": error}

    problems = gate_problems(path, data_root)
    if problems:
        return [failure("", "", "rejected", " | ".join(problems)[:1500])]
    work = Path(tempfile.mkdtemp(prefix="recipe_pictures_"))
    try:
        clear_data_analysis_recipe_cache()
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                raw = ConfigManager(str(path)).raw_config
                orchestrator = DataOrchestrator(path.parent, data_root)
                keys = orchestrator.compute_data_analysis_recipe_keys(recipe_id)
        except BaseException as error:  # noqa: BLE001 - a recipe that cannot load is part of the record
            return [failure("", "", "error", "load: " + short(error))]
        tables: dict = {}
        table_errors: dict = {}
        for collection in collections_of(raw):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    anchor = work / f"{collection}.parquet"
                    orchestrator.materialize_tier1(recipe_id, collection, anchor, keys=keys)
                    tables[collection] = orchestrator.materialize_tier2(recipe_id, collection, anchor, keys=keys)
            except BaseException as error:  # noqa: BLE001
                table_errors[collection] = short(error)
        records = []
        for group, plot, target in plots_of(raw):
            if target not in tables:
                records.append(failure(group, plot, "error", f"no table for collection {target!r}: " + table_errors.get(target, "not built")))
                continue
            file_name = f"{recipe_id}__{group}__{plot}.png".replace("/", "_").replace(" ", "_")
            try:
                hashes, arrays = [], []
                for attempt in range(repeat):
                    target_file = out / file_name if attempt == 0 else work / f"again_{attempt}.png"
                    with contextlib.redirect_stdout(io.StringIO()):
                        ggplot = VizFactory(palette_registry=palettes).render(tables[target], raw, plot)
                        ggplot.save(target_file, verbose=False, **size)
                    arrays.append(pixels(target_file))
                    hashes.append(pixel_hash(arrays[-1]))
                record = {"key": plot_key(recipe_id, group, plot), "recipe": recipe_id, "group": group, "plot": plot,
                          "status": "drawn", "file": file_name, "width_px": int(arrays[0].shape[1]), "height_px": int(arrays[0].shape[0]),
                          "pixel_sha256": hashes[0]}
                unstable = [differing_pixels(arrays[0], other) for other in arrays[1:] if differing_pixels(arrays[0], other)]
                if unstable:
                    record["status"] = "unstable"
                    record["error"] = f"two draws of the same plot differ in {max(unstable)} pixels"
                records.append(record)
            except BaseException as error:  # noqa: BLE001 - one plot that cannot be drawn must not stop the others
                records.append(failure(group, plot, "error", short(error)))
        return records
    finally:
        shutil.rmtree(work, ignore_errors=True)


def draw_all(recipe_dirs: List[Path], data_root: Path, palettes: Optional[dict], out: Path, size: dict, repeat: int, only: Optional[List[str]] = None) -> dict:
    """Draw everything; returns the manifest (not yet written)."""
    out.mkdir(parents=True, exist_ok=True)
    recipes, skipped = discover(recipe_dirs)
    records = []
    for recipe_id, path in recipes:
        if only and recipe_id not in only:
            continue
        records += draw_recipe(recipe_id, path, data_root, palettes, out, size, repeat)
    return {"size": size, "repeat": repeat, "recipe_dirs": [str(d) for d in recipe_dirs], "skipped": skipped,
            "libraries": library_origins(), "python_hash_seed": hash_seed(), "plots": sorted(records, key=lambda r: r["key"])}


def side_by_side(old: Path, new: Path, target: Path) -> None:
    """Save the stored picture, the new picture and the difference (red where a pixel differs) in one image."""
    a, b = pixels(old).astype(np.uint8), pixels(new).astype(np.uint8)
    height, width = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])

    def pad(array: np.ndarray) -> np.ndarray:
        canvas = np.full((height, width, 3), 255, dtype=np.uint8)
        canvas[:array.shape[0], :array.shape[1]] = array
        return canvas

    a, b = pad(a), pad(b)
    mask = (np.abs(a.astype(int) - b.astype(int)).sum(axis=2) > 0)
    diff = np.full_like(a, 255)
    diff[mask] = (220, 0, 0)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.concatenate([a, b, diff], axis=1)).save(target)


def compare(stored: dict, now: dict, stored_dir: Path, now_dir: Path, report_dir: Path) -> dict:
    """The verdict for every plot key. `stored` and `now` are manifests; pictures are read from their folders."""
    old = {r["key"]: r for r in stored["plots"]}
    new = {r["key"]: r for r in now["plots"]}
    rows = []
    recipe_level_now = {r["recipe"]: r for r in now["plots"] if not r["group"] and not r["plot"]}
    recipe_level_before = {r["recipe"]: r for r in stored["plots"] if not r["group"] and not r["plot"]}
    for key in sorted(set(old) | set(new)):
        before, after = old.get(key), new.get(key)
        recipe = (before or after)["recipe"]
        if after is None and before is not None and recipe in recipe_level_now and recipe not in recipe_level_before:
            fail = recipe_level_now[recipe]
            rows.append({"key": key, "verdict": "error-changed", "detail": f"drawn before; the whole recipe now gives {fail['status']}: {fail.get('error', '')[:200]}"})
            continue
        if before is None and recipe in recipe_level_before and recipe not in recipe_level_now and not (after["group"] == "" and after["plot"] == ""):
            rows.append({"key": key, "verdict": "new", "detail": f"drawn now; the stored set had the whole recipe as {recipe_level_before[recipe]['status']}"})
            continue
        if before is None and not after["group"] and not after["plot"]:
            rows.append({"key": key, "verdict": "error-changed", "detail": f"the whole recipe now gives {after['status']}: {after.get('error', '')[:200]}"})
            continue
        if before is None:
            rows.append({"key": key, "verdict": "new", "detail": "drawn now, not in the stored set"})
        elif after is None:
            rows.append({"key": key, "verdict": "missing", "detail": "stored, but not drawn now"})
        elif before["status"] == "unstable":
            rows.append({"key": key, "verdict": "unstable", "detail": "stored as unstable (" + before.get("error", "") + "); not compared"})
        elif before["status"] in ("error", "rejected") or after["status"] in ("error", "rejected"):
            if before["status"] == after["status"] and before.get("error") == after.get("error"):
                rows.append({"key": key, "verdict": "identical", "detail": f"the same {before['status']} as stored: {before.get('error', '')[:120]}"})
            else:
                rows.append({"key": key, "verdict": "error-changed",
                             "detail": f"stored: {before['status']} {before.get('error', '')[:200]} | now: {after['status']} {after.get('error', '')[:200]}"})
        else:
            a, b = pixels(stored_dir / before["file"]), pixels(now_dir / after["file"])
            count = differing_pixels(a, b)
            if after["status"] == "unstable":
                rows.append({"key": key, "verdict": "unstable", "detail": "unstable now: " + after.get("error", "")})
            elif count == 0:
                rows.append({"key": key, "verdict": "identical", "detail": ""})
            else:
                picture = report_dir / (before["file"].removesuffix(".png") + "_diff.png")
                side_by_side(stored_dir / before["file"], now_dir / after["file"], picture)
                same_size = a.shape == b.shape
                rows.append({"key": key, "verdict": "different",
                             "detail": f"{count} pixels differ" + ("" if same_size else f" (size {a.shape[1]}x{a.shape[0]} before, {b.shape[1]}x{b.shape[0]} now)") + f"; see {picture}"})
    return {"rows": rows}


def passes(result: dict) -> bool:
    """True only when every plot is identical (an unstable plot is named but does not fail)."""
    return all(row["verdict"] in ("identical", "unstable") for row in result["rows"])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", metavar="DIR", help="draw all plots into DIR and write DIR/manifest.json")
    mode.add_argument("--check", metavar="DIR", help="draw again and compare with the pictures stored in DIR")
    parser.add_argument("--recipe-dir", action="append", metavar="DIR", help="a folder with recipes (*.yaml directly inside); repeat for several (default: the five folders named above)")
    parser.add_argument("--data-root", default=DEFAULT_DATA_ROOT, help=f"data folder given to the orchestrator (default: {DEFAULT_DATA_ROOT})")
    parser.add_argument("--palettes", default=DEFAULT_PALETTES, help=f"deployment palette file, as the app reads it (default: {DEFAULT_PALETTES})")
    parser.add_argument("--only", nargs="+", metavar="ID", help="only these recipe ids")
    parser.add_argument("--repeat", type=int, default=2, help="draws per plot in --write; two draws that differ mark the plot unstable (default: 2)")
    parser.add_argument("--out", default="tmpAI/recipe_pictures_check", help="--check: where the new pictures and the difference pictures go (default: tmpAI/recipe_pictures_check)")
    parser.add_argument("--allow-outside-checkout", action="store_true",
                        help="draw even when a package is imported from outside this checkout (the default is to stop, D-0050)")
    args = parser.parse_args(argv)
    origins = library_origins()
    print("libraries imported from:")
    for name, where in origins.items():
        print(f"  {name}: {where}")
    print(f"python hash seed: {hash_seed()}")
    outside = outside_checkout(origins)
    if outside:
        if not args.allow_outside_checkout:
            print(outside_message(outside))
            return 2
        print("WARNING: " + ", ".join(sorted(outside)) + " come from outside this checkout (allowed by --allow-outside-checkout); the manifest records it.")
    recipe_dirs = [Path(d) for d in (args.recipe_dir or DEFAULT_RECIPE_DIRS)]
    palettes = load_palettes(Path(args.palettes))
    size = dict(DEFAULT_SIZE)
    if args.write:
        out = Path(args.write)
        manifest = draw_all(recipe_dirs, Path(args.data_root), palettes, out, size, max(1, args.repeat), args.only)
        (out / MANIFEST).write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        counts: dict = {}
        for record in manifest["plots"]:
            counts[record["status"]] = counts.get(record["status"], 0) + 1
        print(f"written: {out / MANIFEST}; " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + f"; skipped entries: {len(manifest['skipped'])}")
        for record in manifest["plots"]:
            if record["status"] != "drawn":
                print(f"  {record['status']}: {record['key']}: {record.get('error', '')[:200]}")
        return 0
    stored_dir = Path(args.check)
    if not (stored_dir / MANIFEST).is_file():
        print(f"No {MANIFEST} in {stored_dir}. Suggestion: run --write {stored_dir} first.")
        return 2
    stored = json.loads((stored_dir / MANIFEST).read_text(encoding="utf-8"))
    if stored.get("libraries"):
        moved = {n: (w, origins.get(n)) for n, w in stored["libraries"].items() if origins.get(n) != w}
        print("libraries of the stored set differ from now (information, not a failure): " + ", ".join(sorted(moved)) if moved
              else "libraries of the stored set: same folders as now")
    else:
        print("the stored manifest has no record of the folders of its libraries")
    print(seed_note(stored.get("python_hash_seed"), hash_seed()))
    out = Path(args.out)
    now_dir = out / "now"
    now = draw_all(recipe_dirs, Path(args.data_root), palettes, now_dir, stored.get("size", size), 1, args.only)
    if args.only:
        stored["plots"] = [r for r in stored["plots"] if r["recipe"] in args.only]
    result = compare(stored, now, stored_dir, now_dir, out / "differences")
    counts = {}
    for row in result["rows"]:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        if row["verdict"] != "identical":
            print(f"{row['verdict']:14} {row['key']}  {row['detail']}")
    print(", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    ok = passes(result)
    print("PICTURES IDENTICAL" if ok else "PICTURES NOT IDENTICAL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
