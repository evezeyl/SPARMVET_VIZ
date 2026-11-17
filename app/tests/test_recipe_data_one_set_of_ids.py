"""Every dataset of a shipped recipe uses ids of ONE common set (DATA-IDS-FIX-1, Eve 2026-11-17, ledger D-0205).

Her words: "The same set of ids is used across all the datasets of the recipes, so there is a logical correspondence:
the datasets reflect analyses on the same samples". Before this test nothing compared the ids of the tables of a recipe:
the demo MLST table held 13 repeated rows (one sample with six sequence types under one scheme) and 2 samples that the
metadata did not know, and the recipe check, the data check and the build said nothing.

What is checked, on the raw files with plain text reading (not through the engine), for every shipped recipe that reads
two or more datasets that have a sample id:
1. the common set is the ids of one table: `metadata_schema`, or the table named in COMMON_SET_TABLE;
2. every id of every other table is in that set (the metadata's own lines without an id are the one allowed exception:
   the demo recipe has a visible step that removes them, D-0167); ALLOWED_OUTSIDE names, with a reason, ids that a recipe
   keeps outside the set on purpose (the template that teaches a left join);
3. a table that is meant to have one row per sample, or per sample and scheme, has no repeat (UNIQUE_BY); the table of
   the common set has one row per sample. A long table (ResFinder, PlasmidFinder, VirulenceFinder) may repeat an id.

A test that fails names the file and the ids. The checker is also run on a broken copy of the demo data, to prove it can fail.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_recipe_data_one_set_of_ids.py -q
"""
import contextlib
import csv
import io
import shutil
import sys
from collections import Counter
from pathlib import Path

import pytest

from utils.config_loader import ConfigManager

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
RECIPE_DIRS = ["pipelines", "retest", "templates"]
NO_ID = {"", "-", '""'}

# The table that holds the samples of a recipe, when it is not `metadata_schema`.
COMMON_SET_TABLE = {"figshare_integration": "fg_metadata"}

# Ids a recipe keeps outside the set on purpose: {(recipe, table): (ids, reason)}.
ALLOWED_OUTSIDE = {
    ("complex_template", "genomics"): (
        {"ACC0029", "ACC0030"},
        "template data made on purpose with 'a sample without a metadata row' to teach what a left join does "
        "(assets/scripts/make_complex_template_data.py, app/tests/test_complex_template_runs.py); "
        "open for Eve: D-0205 says one set of ids for all datasets",
    ),
}

# Tables meant to have one row per sample (and scheme): {(recipe, table): key columns of the file}.
UNIQUE_BY = {
    ("demo_abromics", "MLST"): ("sample_id", "Scheme"),
    ("1_test_data_ST22_dummy", "MLST"): ("sample_id", "Scheme"),
    ("1_test_data_ST22_dummy", "Summary"): ("sample_id",),
    ("1_test_data_ST22_dummy", "Quality_metrics"): ("sample_id",),
    ("1_test_data_ST22_dummy", "FastP"): ("sample_id",),
    ("1_test_data_ST22_dummy", "Quast"): ("sample_id",),
    ("1_test_data_ST22_dummy", "Bracken"): ("sample_id",),
    ("1_Abromics_general_pipeline", "MLST"): ("sample_id", "Scheme"),
}

EXPECTED_CHECKED = {
    "demo_abromics", "1_test_data_ST22_dummy", "2_test_data_ST22_dummy", "1_Abromics_general_pipeline",
    "figshare_integration", "complex_template",
}


def read_file(path):
    """Header and rows of a TSV, every value as text (quotes read as a spreadsheet would)."""
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    return rows[0], rows[1:]


def id_column_of(table):
    """The file column that holds the sample id: the field declared `is_entity_key`, else the field `sample_id`."""
    fields = table.get("input_fields") or {}
    for key, spec in fields.items():
        if isinstance(spec, dict) and spec.get("is_entity_key"):
            return spec.get("original_name", key)
    for key, spec in fields.items():
        name = spec.get("original_name", key) if isinstance(spec, dict) else key
        if str(name).lower() == "sample_id":
            return name
    return None


def tables_of(raw, root=ROOT, redirect=None):
    """{table name: (path, id column)} for the datasets of a recipe that have a readable file and a sample id.

    `redirect` maps a file name to another path (used to run the checker on a broken copy).
    """
    found = {}
    sections = [(n, t) for sec in ("data_schemas", "additional_datasets_schemas") for n, t in (raw.get(sec) or {}).items()]
    if raw.get("metadata_schema"):
        sections.append(("metadata_schema", raw["metadata_schema"]))
    for name, table in sections:
        source = (table.get("source") or {}).get("path")
        column = id_column_of(table)
        if not source or column is None:
            continue
        path = Path(root) / source
        if redirect and path.name in redirect:
            path = Path(redirect[path.name])
        if path.exists():
            found[name] = (path, column)
    return found


def problems_of(recipe_id, tables, set_table, allowed_outside=None, unique_by=None):
    """The inconsistencies of the ids of one recipe, as sentences that name the file and the ids."""
    allowed_outside = ALLOWED_OUTSIDE if allowed_outside is None else allowed_outside
    unique_by = UNIQUE_BY if unique_by is None else unique_by
    found = []
    if set_table not in tables:
        return [f"{recipe_id}: the table that holds the samples ({set_table}) has no readable file or no sample id column: "
                f"name the right table in COMMON_SET_TABLE"]
    read = {name: read_file(path) for name, (path, _) in tables.items()}

    def ids(name):
        header, rows = read[name]
        column = header.index(tables[name][1])
        return [row[column] for row in rows]

    set_ids = [i for i in ids(set_table) if i not in NO_ID]
    common = set(set_ids)
    repeated = sorted(i for i, n in Counter(set_ids).items() if n > 1)
    if repeated:
        found.append(f"{recipe_id}: {tables[set_table][0].name} (the table of the samples) repeats ids: {repeated}")
    for name in tables:
        if name == set_table:
            continue
        outside = {i for i in ids(name)} - common
        allowed = allowed_outside.get((recipe_id, name), (set(), ""))[0]
        outside -= allowed
        if outside:
            found.append(f"{recipe_id}: {tables[name][0].name} ({name}) has {len(outside)} ids that are not in the set of "
                         f"{tables[set_table][0].name}: {sorted(outside)}")
    for (rec, name), key in unique_by.items():
        if rec != recipe_id or name not in tables:
            continue
        header, rows = read[name]
        positions = [header.index(k) for k in key]
        counts = Counter(tuple(row[p] for p in positions) for row in rows)
        again = sorted(k for k, n in counts.items() if n > 1)
        if again:
            found.append(f"{recipe_id}: {tables[name][0].name} ({name}) should have one row per {' and '.join(key)}, "
                         f"repeated: {again}")
    return found


def _load(recipe_file):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return ConfigManager(str(recipe_file)).raw_config


def _shipped_recipes_with_several_id_tables():
    checked = {}
    for sub in RECIPE_DIRS:
        for recipe_file in sorted((ROOT / "config" / "data_analysis_recipes" / sub).glob("*.yaml")):
            try:
                raw = _load(recipe_file)
            except BaseException:  # noqa: BLE001 - a recipe that is broken on purpose is not a sample data set
                continue
            tables = tables_of(raw)
            if len(tables) >= 2:
                checked[raw["id"]] = tables
    return checked


CHECKED = _shipped_recipes_with_several_id_tables()


def test_the_known_multi_dataset_recipes_are_all_checked():
    """A recipe that fails to load or loses its id column must not drop out of the check silently."""
    assert EXPECTED_CHECKED <= set(CHECKED), sorted(EXPECTED_CHECKED - set(CHECKED))


@pytest.mark.parametrize("recipe_id", sorted(CHECKED))
def test_every_table_of_a_recipe_uses_ids_of_the_one_common_set(recipe_id):
    set_table = COMMON_SET_TABLE.get(recipe_id, "metadata_schema")
    found = problems_of(recipe_id, CHECKED[recipe_id], set_table)
    assert not found, "\n".join(found)


def test_the_shipped_demo_folder_is_one_consistent_set():
    """The demo ResFinder file is read by no recipe today; it must still hold the ids of the demo metadata."""
    demo = ROOT / "assets" / "test_data" / "demo_high_integrity"
    metadata = next(demo.glob("*_metadata_*.tsv"))
    tables = {
        "metadata_schema": (metadata, "sample_id"),
        "MLST": (next(demo.glob("*MLST_results*.tsv")), "sample_id"),
        "ResFinder": (next(demo.glob("*ResFinder*.tsv")), "sample_id"),
    }
    found = problems_of("demo_high_integrity", tables, "metadata_schema",
                        unique_by={("demo_high_integrity", "MLST"): ("sample_id", "Scheme")})
    assert not found, "\n".join(found)


# --- the checker can fail ---------------------------------------------------------------------------------

def _demo_copy(tmp_path):
    demo = ROOT / "assets" / "test_data" / "demo_high_integrity"
    for f in demo.glob("*.tsv"):
        shutil.copy(f, tmp_path / f.name)
    return {f.name: tmp_path / f.name for f in tmp_path.glob("*.tsv")}


def _demo_problems(redirect):
    raw = _load(ROOT / "config" / "data_analysis_recipes" / "pipelines" / "demo_abromics.yaml")
    return problems_of("demo_abromics", tables_of(raw, redirect=redirect), "metadata_schema")


def test_the_unbroken_copy_passes(tmp_path):
    assert _demo_problems(_demo_copy(tmp_path)) == []


def test_a_foreign_id_in_mlst_is_named_with_the_file(tmp_path):
    copy = _demo_copy(tmp_path)
    mlst = copy["test_data_test_data_MLST_results_20260307_105756.tsv"]
    lines = mlst.read_text(encoding="utf-8").split("\n")
    first = lines[1].split("\t")
    first[0] = "SYN_00000000"
    lines[1] = "\t".join(first)
    mlst.write_text("\n".join(lines), encoding="utf-8")
    found = _demo_problems(copy)
    assert any("SYN_00000000" in p and "test_data_test_data_MLST_results_20260307_105756.tsv" in p for p in found), found


def test_a_repeated_sample_and_scheme_in_mlst_is_named(tmp_path):
    copy = _demo_copy(tmp_path)
    mlst = copy["test_data_test_data_MLST_results_20260307_105756.tsv"]
    lines = mlst.read_text(encoding="utf-8").split("\n")
    lines.insert(2, lines[1])  # the same sample and scheme twice
    mlst.write_text("\n".join(lines), encoding="utf-8")
    sample = lines[1].split("\t")[0]
    found = _demo_problems(copy)
    assert any("one row per sample_id and Scheme" in p and sample in p for p in found), found


def test_a_repeated_id_in_the_metadata_is_named(tmp_path):
    copy = _demo_copy(tmp_path)
    meta = copy["test_data_test_metadata_20260307_105756.tsv"]
    lines = meta.read_text(encoding="utf-8").split("\n")
    lines.insert(3, lines[1])
    meta.write_text("\n".join(lines), encoding="utf-8")
    found = _demo_problems(copy)
    assert any("repeats ids" in p and lines[1].split("\t")[0] in p for p in found), found


def test_an_unreadable_set_table_is_reported_not_skipped():
    found = problems_of("x", {"MLST": (Path("a.tsv"), "sample_id")}, "metadata_schema")
    assert found and "COMMON_SET_TABLE" in found[0]


def test_the_allowed_outside_ids_are_only_the_declared_ones():
    """The template's two foreign ids are allowed; a third one is not (the exception is not a free pass)."""
    tables = CHECKED["complex_template"]
    assert problems_of("complex_template", tables, "metadata_schema") == []
    found = problems_of("complex_template", tables, "metadata_schema", allowed_outside={("complex_template", "genomics"): ({"ACC0029"}, "x")})
    assert any("ACC0030" in p for p in found), found
