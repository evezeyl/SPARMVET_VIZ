"""Golden baseline of the shipped data analysis recipes (GOLDEN-BASELINE-1, P0).

Records, for every recipe, what the engine produces today: the Tier 1 table, the Tier 2 table and the
table each plot is drawn from (after the plot's own filters), as row count, ordered columns with
their types, and a content hash. A later change that must be "result-identical" (the recipe
migration, run A) is checked against this file: the hashes must not move. A recipe that fails to
load or build is recorded with its error, so the same failure must stay the same failure.

The hash is the SHA-256 of the table written as CSV (header included, row order kept). It
depends on the Polars version, which is recorded in the file; regenerate the baseline when
Polars changes, and say why in the commit.

Usage:
  PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --out tmpAI/golden_baseline.json
  PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json
"""
import argparse
import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

import polars as pl

DEFAULT_RECIPES_DIR = "config/data_analysis_recipes/pipelines"
DEFAULT_RAW_DATA = "assets/test_data"
SECTION_KEYS = ("t1", "t2", "plots")


def table_record(frame: pl.DataFrame) -> dict:
    """Row count, ordered columns with types and the content hash of one table."""
    csv_bytes = frame.write_csv().encode("utf-8")
    return {
        "rows": frame.height,
        "columns": [f"{name}:{dtype}" for name, dtype in frame.schema.items()],
        "sha256": hashlib.sha256(csv_bytes).hexdigest(),
    }


def error_record(exc: BaseException) -> dict:
    return {"error": f"{type(exc).__name__}: {str(exc)[:160]}"}


def recipe_ids(recipes_dir: Path) -> list[str]:
    return sorted(p.stem for p in recipes_dir.glob("*.yaml"))


def collections_of(raw: dict) -> list[str]:
    """Every collection a plot reads, plus every declared join, in a fixed order."""
    found = set((raw.get("joins") or {}).keys())
    for group in (raw.get("analysis_groups") or {}).values():
        for entry in (group.get("plots") or {}).values():
            target = (entry.get("spec") or {}).get("target_dataset")
            if target:
                found.add(target)
    return sorted(found)


def plots_of(raw: dict) -> list[tuple[str, str]]:
    """(plot id, target collection) for every plot, in a fixed order."""
    found = []
    for group in (raw.get("analysis_groups") or {}).values():
        for plot_id, entry in (group.get("plots") or {}).items():
            found.append((plot_id, (entry.get("spec") or {}).get("target_dataset")))
    return sorted(found)


def build_recipe(recipe_id: str, recipes_dir: Path, raw_data: Path, with_plots: bool) -> dict:
    """The record of one recipe: T1 and T2 per collection, and the table of every plot."""
    from app.modules.cache_keys import clear_data_analysis_recipe_cache
    from app.modules.orchestrator import DataOrchestrator
    from utils.config_loader import ConfigManager
    from viz_factory.viz_factory import VizFactory

    record: dict = {"t1": {}, "t2": {}, "plots": {}}
    clear_data_analysis_recipe_cache()
    work = Path(tempfile.mkdtemp(prefix="golden_baseline_"))
    try:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                raw = ConfigManager(str(recipes_dir / f"{recipe_id}.yaml")).raw_config
        except BaseException as exc:  # noqa: BLE001 - a recipe that cannot load is part of the baseline
            return {"load": error_record(exc)}
        orchestrator = DataOrchestrator(recipes_dir, raw_data)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                keys = orchestrator.compute_data_analysis_recipe_keys(recipe_id)
        except BaseException as exc:  # noqa: BLE001
            return {"load": error_record(exc)}
        frames: dict[str, pl.LazyFrame] = {}
        for collection in collections_of(raw):
            anchor = work / f"{collection}.parquet"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    t1 = orchestrator.materialize_tier1(recipe_id, collection, anchor, keys=keys).collect()
                    t2_lf = orchestrator.materialize_tier2(recipe_id, collection, anchor, keys=keys)
                    t2 = t2_lf.collect()
                record["t1"][collection] = table_record(t1)
                record["t2"][collection] = table_record(t2)
                frames[collection] = t2_lf
            except BaseException as exc:  # noqa: BLE001
                record["t1"][collection] = error_record(exc)
        if not with_plots:
            return record
        import matplotlib
        matplotlib.use("Agg")
        for plot_id, target in plots_of(raw):
            if target not in frames:
                record["plots"][plot_id] = {"error": f"no table for collection {target!r}"}
                continue
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    plot = VizFactory().render(frames[target], raw, plot_id)
                    plotted = pl.from_pandas(plot.data)
                record["plots"][plot_id] = table_record(plotted)
            except BaseException as exc:  # noqa: BLE001
                record["plots"][plot_id] = error_record(exc)
        return record
    finally:
        shutil.rmtree(work, ignore_errors=True)


def build(recipes_dir: Path, raw_data: Path, ids: list[str], with_plots: bool) -> dict:
    return {
        "polars": pl.__version__,
        "recipes_dir": str(recipes_dir),
        "raw_data": str(raw_data),
        "recipes": {rid: build_recipe(rid, recipes_dir, raw_data, with_plots) for rid in ids},
    }


def describe_change(expected: dict | None, found: dict | None) -> str:
    """A short sentence about what moved between two table records."""
    if expected is None or found is None:
        return "present only in the baseline" if found is None else "present only now"
    if "error" in expected or "error" in found:
        return f"{expected.get('error', 'built')} -> {found.get('error', 'built')}"
    parts = []
    if expected["rows"] != found["rows"]:
        parts.append(f"rows {expected['rows']} -> {found['rows']}")
    if expected["columns"] != found["columns"]:
        parts.append("columns or types differ")
    if expected["sha256"] != found["sha256"]:
        parts.append("content hash differs")
    return ", ".join(parts)


def differences(expected: dict, found: dict) -> list[str]:
    """One line per table whose record is not the same; an empty list means result-identical."""
    out: list[str] = []
    if expected.get("polars") != found.get("polars"):
        out.append(f"Polars version differs: baseline {expected.get('polars')}, now {found.get('polars')} (hashes may move)")
    for rid, exp in sorted(expected["recipes"].items()):
        got = found["recipes"].get(rid)
        if got is None:
            out.append(f"{rid}: not built now")
            continue
        if "load" in exp or "load" in got:
            if exp.get("load") != got.get("load"):
                out.append(f"{rid}: load outcome differs: {exp.get('load')} -> {got.get('load')}")
            continue
        for section in SECTION_KEYS:
            names = sorted(set(exp.get(section, {})) | set(got.get(section, {})))
            for name in names:
                if exp.get(section, {}).get(name) != got.get(section, {}).get(name):
                    out.append(f"{rid}: {section} {name}: {describe_change(exp.get(section, {}).get(name), got.get(section, {}).get(name))}")
    for rid in sorted(set(found["recipes"]) - set(expected["recipes"])):
        out.append(f"{rid}: new in this run, not in the baseline")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record or check the tables the engine builds from the shipped recipes (golden baseline).",
        epilog="Without --check the baseline is written to --out. With --check the tables are rebuilt and compared; the exit code is 1 on any difference.",
    )
    parser.add_argument("--recipes-dir", default=DEFAULT_RECIPES_DIR, help=f"folder of the recipe files (default {DEFAULT_RECIPES_DIR})")
    parser.add_argument("--raw-data", default=DEFAULT_RAW_DATA, help=f"folder of the data files (default {DEFAULT_RAW_DATA})")
    parser.add_argument("--recipe-ids", nargs="*", help="recipe ids (file names without .yaml); default every recipe of the folder")
    parser.add_argument("--no-plots", action="store_true", help="skip the table of each plot (faster)")
    parser.add_argument("--out", help="write the baseline to this JSON file")
    parser.add_argument("--check", help="compare the tables built now with this baseline JSON file")
    args = parser.parse_args()
    if not args.out and not args.check:
        parser.error("give --out to record a baseline or --check to compare with one")
    recipes_dir, raw_data = Path(args.recipes_dir), Path(args.raw_data)
    ids = args.recipe_ids or recipe_ids(recipes_dir)
    found = build(recipes_dir, raw_data, ids, with_plots=not args.no_plots)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(found, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        tables = sum(len(r.get(s, {})) for r in found["recipes"].values() for s in SECTION_KEYS)
        print(f"baseline written: {args.out} ({len(found['recipes'])} recipes, {tables} table records)")
    if args.check:
        expected = json.loads(Path(args.check).read_text(encoding="utf-8"))
        if args.recipe_ids:
            expected["recipes"] = {k: v for k, v in expected["recipes"].items() if k in ids}
        problems = differences(expected, found)
        for line in problems:
            print(line)
        print("result-identical" if not problems else f"{len(problems)} difference(s)")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
