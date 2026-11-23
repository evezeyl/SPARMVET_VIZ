"""The shipped `left_join_lesson` recipe teaches what a left join does when the sample ids do not match (Eve, 2026-11-17).

The recipe is the one place of the shipped recipes where ids are outside the common set ON PURPOSE (D-0205 keeps one set of
ids everywhere else). What is checked: the recipe passes the checker and the data check, it declares the sample id of each
table (`is_entity_id`, the two tables name it with different columns), it runs through the real path, the left join keeps
every left sample, the right-only ids are absent, the left-only samples have an empty country, and every number written in
`info.description` equals the data. The data files are what the generator writes with its default seed.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_left_join_lesson.py -q
"""
import csv
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
import polars as pl

matplotlib.use("Agg")

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import (
    checker_catalogs,
    validate_data_analysis_recipe,
    validate_data_analysis_recipe_data,
)
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager
from utils.recipe_loader import check_recipe_file
from viz_factory.viz_factory import VizFactory

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "config" / "data_analysis_recipes" / "templates"
TEST_DATA = ROOT / "assets" / "test_data"
LESSON_DATA = TEST_DATA / "left_join_lesson"
RECIPE = TEMPLATES / "left_join_lesson.yaml"
SCRIPT = ROOT / "assets" / "scripts" / "make_left_join_lesson_data.py"
PLOT = "samples_by_country"


def _raw():
    return ConfigManager(str(RECIPE)).raw_config


def _read(name):
    with open(LESSON_DATA / name, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    return rows[0], rows[1:]


def _ids():
    left = {r[0] for r in _read("left_join_lesson_sequenced.tsv")[1]}
    right = {r[0] for r in _read("left_join_lesson_metadata.tsv")[1]}
    return left, right


def _build(anchor_dir: Path):
    clear_data_analysis_recipe_cache()
    orchestrator = DataOrchestrator(TEMPLATES, TEST_DATA)
    keys = orchestrator.compute_data_analysis_recipe_keys("left_join_lesson")
    anchor = anchor_dir / "lesson_assembly.parquet"
    return orchestrator.materialize_tier2("left_join_lesson", "lesson_assembly", anchor, keys=keys)


def test_the_recipe_passes_the_checker_and_the_data_check():
    assert [p.text(RECIPE.name) for p in check_recipe_file(RECIPE, "run", catalogs=checker_catalogs()).errors] == []
    assert validate_data_analysis_recipe(RECIPE) == []
    assert validate_data_analysis_recipe_data(RECIPE, TEST_DATA) == []


def test_the_id_is_the_file_name():
    assert _raw()["id"] == RECIPE.stem


def test_the_recipe_declares_which_column_is_the_sample_id_in_each_table():
    raw = _raw()
    declared = {}
    for name, table in (("sequenced", raw["data_schemas"]["sequenced"]), ("metadata_schema", raw["metadata_schema"])):
        keys = [(slug, f["original_name"]) for slug, f in table["input_fields"].items() if f.get("is_entity_id")]
        assert len(keys) == 1, f"{name} must declare exactly one is_entity_id field"
        declared[name] = keys[0][1]
    assert declared == {"sequenced": "Accession", "metadata_schema": "ID"}, "the two tables name the id differently on purpose"
    assert raw["entity"]["population"] == "sequenced"
    # the declared names are the real columns of the files (the id is declared, not guessed)
    assert declared["sequenced"] in _read("left_join_lesson_sequenced.tsv")[0]
    assert declared["metadata_schema"] in _read("left_join_lesson_metadata.tsv")[0]


def test_the_ids_do_not_match_on_purpose_in_both_directions():
    left, right = _ids()
    assert sorted(left - right) == ["ACC0001", "ACC0002"]
    assert sorted(right - left) == ["ACC0011", "ACC0012"]


def test_the_left_join_keeps_every_left_sample_and_leaves_the_right_only_ids_out(tmp_path):
    frame = _build(tmp_path).collect()
    left, right = _ids()
    assert frame.columns == ["sample_id", "gene", "country"]
    assert sorted(frame["sample_id"].to_list()) == sorted(left), "a left join keeps every row of the left table, once"
    assert not (set(frame["sample_id"].to_list()) & (right - left)), "an id only in the right table is not in the result"


def test_the_left_only_samples_have_an_empty_country_and_the_others_do_not(tmp_path):
    frame = _build(tmp_path).collect()
    left, right = _ids()
    empty = set(frame.filter(pl.col("country").is_null())["sample_id"].to_list())
    assert empty == left - right
    filled = frame.filter(pl.col("country").is_not_null())
    assert set(filled["sample_id"].to_list()) == left & right


def test_every_number_in_the_description_equals_the_data(tmp_path):
    text = _raw()["info"]["description"]
    left, right = _ids()
    frame = _build(tmp_path).collect()
    left_header_rows = len(_read("left_join_lesson_sequenced.tsv")[1])
    right_rows = len(_read("left_join_lesson_metadata.tsv")[1])
    assert left_header_rows == len(left) == 10 and right_rows == len(right) == 10
    assert f"has {len(left)} samples, ACC0001 to ACC0010" in text
    assert f"has {len(right)} samples, ACC0003 to ACC0012" in text
    assert f"{len(left - right)} ids are only in the left table ({', '.join(sorted(left - right))})" in text
    assert f"{len(right - left)} ids are only in the right table ({', '.join(sorted(right - left))})" in text
    assert f"{left_header_rows} rows before and {frame.height} rows after the join" in text
    assert f"({frame['country'].null_count()} rows with an empty country)" in text
    # no other number sentence: every figure of the text is one of the checked ones
    numbers = set(re.findall(r"\b\d+\b", re.sub(r"ACC\d{4}", "", text)))
    assert numbers <= {"10", "2"}, numbers


def test_the_plot_renders(tmp_path):
    lf = _build(tmp_path)
    plot = VizFactory().render(lf, _raw(), PLOT)
    plot.draw()
    assert plot.data.shape[0] > 0 and {"country", "gene"} <= set(plot.data.columns)


def test_the_committed_files_are_what_the_generator_writes(tmp_path):
    spec = importlib.util.spec_from_file_location("make_left_join_lesson_data", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    left, right = module.build(module.DEFAULT_SEED)
    module.write(tmp_path / "l.tsv", ["Accession", "Gene"], left)
    module.write(tmp_path / "r.tsv", ["ID", "Country"], right)
    assert (tmp_path / "l.tsv").read_bytes() == (LESSON_DATA / "left_join_lesson_sequenced.tsv").read_bytes()
    assert (tmp_path / "r.tsv").read_bytes() == (LESSON_DATA / "left_join_lesson_metadata.tsv").read_bytes()
    assert module.build(1) != (left, right), "the seed changes the draw"
    assert module.build(1)[0][0][0] == "ACC0001", "the ids are fixed, only the values are drawn"


def test_the_generator_runs_from_the_command_line_and_does_not_replace_files(tmp_path):
    run = [sys.executable, str(SCRIPT), "--out-dir", str(tmp_path)]
    first = subprocess.run(run, cwd=ROOT, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    assert (tmp_path / "left_join_lesson_sequenced.tsv").read_bytes() == (LESSON_DATA / "left_join_lesson_sequenced.tsv").read_bytes()
    second = subprocess.run(run, cwd=ROOT, capture_output=True, text=True)
    assert second.returncode == 2 and "--overwrite" in second.stderr
    assert subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=ROOT, capture_output=True, text=True).returncode == 0
