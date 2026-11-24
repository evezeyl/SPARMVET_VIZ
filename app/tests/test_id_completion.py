"""The completion of the ids and the three checks, through the real engine path (D-0572 to D-0599, D-0613).

What is checked, on the demo recipe `1_test_data_ST22_dummy` (the ResFinder file lists 38 of the 42 ids of the metadata: the completion adds 4 lines to it and nothing
to any other table, and no data file is changed) and on small recipes written in a temporary folder: the lines are added in the table the build reads (before the
steps of tier 1), both ways (the metadata too), with no metadata the tables complete each other, a line with no usable id stays, a look-up table is untouched, the
Source view shows the file as read, the three checks and their numbers, check 3 passes on every shipped recipe, the cache key of a table moves when another table
that takes part changes (and does not move for a table that reads none of them), a recipe whose table has no `completion` block is not run, and the data check
returns the ids as warnings, never as a problem.

PROVISIONAL (D-0613): the form of the block, the marker as a yes/no column, the Source view without the added lines.

# @deps
# consumes: app/modules/orchestrator.py (id_report, _read_source, read_source), app/modules/data_analysis_recipe_validator.py (check_data_analysis_recipe_data), libs/utils/src/utils/id_completion.py, app/modules/cache_keys.py
# doc: .claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md
# @end_deps

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_id_completion.py -q
"""
import contextlib
import hashlib
import io
from pathlib import Path

import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.data_analysis_recipe_validator import check_data_analysis_recipe_data, validate_data_analysis_recipe_data
from app.modules.orchestrator import DataOrchestrator
from utils.errors import DataAnalysisRecipeError
from utils.id_completion import report_lines
from utils.recipe_factory import minimal_recipe, minimal_schema, write_recipe

ROOT = Path(__file__).resolve().parents[2]
PIPELINES = ROOT / "config" / "data_analysis_recipes" / "pipelines"
DEMO = "1_test_data_ST22_dummy"
NOT_IN_ORIGINAL = ["40503315", "52676003", "75442817", "87836481"]
MARKER = "ResFinder_not_in_original_data"   # the demo writes one marker per table (two tables never share one, E06)


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def quiet(function, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args, **kwargs)


def demo():
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    raw = load_data_analysis_recipe(PIPELINES / f"{DEMO}.yaml").raw
    return orchestrator, raw


# -- the demo ------------------------------------------------------------------------------------

def test_the_resfinder_file_lacks_4_of_the_42_ids_and_only_it():
    orchestrator, raw = demo()
    report = quiet(orchestrator.id_report, DEMO, raw)
    by = {t.table: t for t in report.tables}
    assert report.union_count == 42 and report.has_metadata and report.completed
    assert set(by["ResFinder"].added) == set(NOT_IN_ORIGINAL) and by["ResFinder"].missing_from_table == tuple(sorted(NOT_IN_ORIGINAL))
    assert by["ResFinder"].not_in_metadata == ()
    assert [t.table for t in report.tables if t.added] == ["ResFinder"], "every other table of the demo has all 42 ids"
    assert report.check3_ok and all(t.no_id_lines == 0 for t in report.tables)


def test_the_demo_has_ten_tables_that_take_part_and_the_look_ups_do_not():
    orchestrator, raw = demo()
    report = quiet(orchestrator.id_report, DEMO, raw)
    names = [t.table for t in report.tables]
    assert names[0] == "metadata_schema" and len(names) == 10
    assert "VirulenceFinder" not in names and "APEC_STEC_virulence_genes" not in names   # additional tables: never completed


def test_the_table_the_build_reads_has_4_more_lines_marked_and_empty_except_the_id():
    orchestrator, raw = demo()
    schema = raw["data_schemas"]["ResFinder"]
    plain = quiet(orchestrator._read_plain, "ResFinder", schema, DEMO)[0].collect()
    done = quiet(orchestrator._read_source, "ResFinder", schema, DEMO, raw)[0].collect()
    assert done.height == plain.height + 4 and done.columns == plain.columns + [MARKER]
    assert done.head(plain.height).drop(MARKER).equals(plain), "the own lines are unchanged and keep their order"
    added = done.filter(pl.col(MARKER))
    assert added["sample_id"].to_list() == sorted(NOT_IN_ORIGINAL)
    assert all(added[c].null_count() == 4 for c in plain.columns if c != "sample_id")
    assert done.filter(~pl.col(MARKER)).height == plain.height and done.schema[MARKER] == pl.Boolean


def test_a_table_that_is_complete_gets_the_marker_column_all_false_and_no_line():
    orchestrator, raw = demo()
    schema = raw["data_schemas"]["Quast"]
    plain = quiet(orchestrator._read_plain, "Quast", schema, DEMO)[0].collect()
    done = quiet(orchestrator._read_source, "Quast", schema, DEMO, raw)[0].collect()
    assert done.height == plain.height and done["Quast_not_in_original_data"].to_list() == [False] * plain.height


def test_the_metadata_table_is_completed_with_its_own_marker_and_here_nothing_is_added():
    orchestrator, raw = demo()
    done = quiet(orchestrator._read_source, "metadata_schema", raw["metadata_schema"], DEMO, raw)[0].collect()
    assert "metadata_schema_not_in_original_data" in done.columns and done["metadata_schema_not_in_original_data"].sum() == 0


def test_a_look_up_table_is_read_as_it_is():
    orchestrator, raw = demo()
    schema = raw["additional_datasets_schemas"]["VirulenceFinder"]
    plain = quiet(orchestrator._read_plain, "VirulenceFinder", schema, DEMO)[0].collect()
    done = quiet(orchestrator._read_source, "VirulenceFinder", schema, DEMO, raw)[0].collect()
    assert done.equals(plain)


def test_the_source_view_shows_the_file_as_read_without_the_added_lines():
    orchestrator, _ = demo()
    shown = quiet(orchestrator.read_source, DEMO, "ResFinder").collect()
    plain = quiet(orchestrator._read_plain, "ResFinder", demo()[1]["data_schemas"]["ResFinder"], DEMO)[0].collect()
    assert shown.equals(plain) and MARKER not in shown.columns


def test_no_data_file_is_changed_by_the_build(tmp_path):
    orchestrator, raw = demo()
    files = orchestrator.get_source_files(DEMO)
    before = {k: hashlib.sha256(Path(v).read_bytes()).hexdigest() for k, v in files.items()}
    quiet(orchestrator.materialize_tier1, DEMO, "ResFinder", tmp_path / "ResFinder.parquet")
    assert {k: hashlib.sha256(Path(v).read_bytes()).hexdigest() for k, v in files.items()} == before


def test_the_built_tier_1_of_resfinder_holds_the_four_added_lines(tmp_path):
    orchestrator, _ = demo()
    table = quiet(orchestrator.materialize_tier1, DEMO, "ResFinder", tmp_path / "ResFinder.parquet").collect()
    assert set(NOT_IN_ORIGINAL) <= set(table["sample_id"].to_list())


@pytest.mark.xfail(strict=True, reason=(
    "KNOWN, not fixed here (the recipes' own steps are the next step, D-0613): `ResFinder_wrangling_tier1.yaml` stamps status 'Detected' on EVERY line of the table, the lines the completion "
    "adds included, so an entity that has no ResFinder result reads 'Detected' in ST22_Anchor (31 rows of the entity 87836481) and in the plots built on it. A marker is not a zero (D-0573): "
    "the recipe must say what an added line means. The test states what the design expects; the day the recipe is corrected it passes, and this mark is removed."))
def test_an_entity_with_no_resfinder_result_does_not_read_detected_in_the_anchor(tmp_path):
    orchestrator, _ = demo()
    anchor = quiet(orchestrator.materialize_tier1, DEMO, "ST22_Anchor", tmp_path / "ST22_Anchor.parquet").collect()
    rows = anchor.filter(pl.col("sample_id") == NOT_IN_ORIGINAL[3])
    assert rows.height > 0 and rows["status"].null_count() == rows.height


def test_the_data_check_returns_the_ids_as_warnings_and_never_as_a_problem():
    check = quiet(check_data_analysis_recipe_data, PIPELINES / f"{DEMO}.yaml", ROOT, "data_analysis_recipe_paths", None)
    assert check.problems == [] and check.ids_error is None
    assert check.ids is not None and [t.table for t in check.ids.tables if t.added] == ["ResFinder"]
    assert any("ResFinder" in line and "4 line(s) were added" in line for line in report_lines(check.ids))


def test_the_plain_data_check_does_not_make_the_checks_of_the_ids():
    assert quiet(validate_data_analysis_recipe_data, PIPELINES / f"{DEMO}.yaml", ROOT) == []
    check = quiet(check_data_analysis_recipe_data, PIPELINES / f"{DEMO}.yaml", ROOT, "data_analysis_recipe_paths", None, False)
    assert check.ids is None and check.problems == []


SHIPPED = sorted(p.stem for p in PIPELINES.glob("*.yaml"))


@pytest.mark.parametrize("recipe_id", SHIPPED)
def test_check_3_passes_on_every_shipped_recipe_and_nothing_is_a_problem(recipe_id):
    """After the completion every table that takes part holds the same ids: a difference is a bug of the app (D-0590)."""
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    raw = load_data_analysis_recipe(PIPELINES / f"{recipe_id}.yaml").raw
    report = quiet(orchestrator.id_report, recipe_id, raw)
    if report is not None:
        assert report.check3_ok, report.as_dict()


def test_demo_abromics_lists_its_three_lines_with_no_id_and_the_completion_adds_the_other_ids_to_mlst():
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    raw = load_data_analysis_recipe(PIPELINES / "demo_abromics.yaml").raw
    report = quiet(orchestrator.id_report, "demo_abromics", raw)
    by = {t.table: t for t in report.tables}
    assert by["metadata_schema"].no_id_lines == 3 and by["metadata_schema"].no_id_line_numbers == (4, 5, 10)
    assert report.union_count == 27 and len(by["MLST"].added) == 12 and report.check3_ok
    lines = " ".join(report_lines(report))
    assert "3 line(s) have no usable id" in lines


# -- small recipes -------------------------------------------------------------------------------

def world(tmp_path, tables, metadata=None, additional=None, blocks=True):
    """A recipe `w` with the data tables `tables` ({id: [ids]}), an optional metadata ({ids} or a list that may hold missing ids) and an optional look-up."""
    data = tmp_path / "data"
    data.mkdir(parents=True, exist_ok=True)

    def table(name, ids, entity=True, meta=False):
        (data / f"{name}.tsv").write_text("sample_id\tv\n" + "".join(f"{i if i is not None else ''}\t{k}\n" for k, i in enumerate(ids)))
        out = minimal_schema(str(data / f"{name}.tsv"), {"sample_id": "String", "v": "Float64"}, entity_key="sample_id" if entity else None, table_id="metadata_schema" if meta else None)
        if not blocks:
            out.pop("completion", None)
        return out

    schemas = {name: table(name, ids) for name, ids in tables.items()}
    recipe = minimal_recipe("w", schemas=schemas)
    if metadata is not None:
        recipe["metadata_schema"] = table("meta", metadata, meta=True)
    if additional is not None:
        recipe["additional_datasets_schemas"] = {"L": table("L", additional, entity=False)}
    write_recipe(tmp_path / "w.yaml", recipe)
    return DataOrchestrator(tmp_path, tmp_path), recipe


def table_of(orchestrator, recipe, name):
    schema = recipe["metadata_schema"] if name == "metadata_schema" else recipe["data_schemas"][name]
    return quiet(orchestrator._read_source, name, schema, "w", recipe)[0].collect()


def test_both_ways_the_metadata_gets_the_ids_of_the_data_and_the_data_get_the_ids_of_the_metadata(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1", "s2"], "B": ["s2", "s9"]}, metadata=["s1", "s2", "s3"])
    meta, a, b = (table_of(orchestrator, recipe, n) for n in ("metadata_schema", "A", "B"))
    assert meta["sample_id"].to_list()[3:] == ["s9"] and meta["metadata_schema_not_in_original_data"].to_list() == [False, False, False, True]
    assert a["sample_id"].to_list()[2:] == ["s3", "s9"] and b["sample_id"].to_list()[2:] == ["s1", "s3"]
    report = quiet(orchestrator.id_report, "w", recipe)
    by = {t.table: t for t in report.tables}
    assert by["B"].not_in_metadata == ("s9",) and by["B"].missing_from_table == ("s1", "s3") and report.check3_ok and report.union_count == 4


def test_with_no_metadata_the_data_tables_complete_each_other(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]})
    assert table_of(orchestrator, recipe, "A")["sample_id"].to_list() == ["s1", "s2"]
    assert table_of(orchestrator, recipe, "B")["sample_id"].to_list() == ["s2", "s1"]
    report = quiet(orchestrator.id_report, "w", recipe)
    assert not report.has_metadata and report.check3_ok and report.tables[0].not_in_metadata is None


def test_a_line_with_no_usable_id_stays_is_listed_and_is_given_to_no_other_table(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, metadata=["s1", None, "s2"])
    meta, a = table_of(orchestrator, recipe, "metadata_schema"), table_of(orchestrator, recipe, "A")
    assert meta.height == 3 and a["sample_id"].to_list() == ["s1", "s2"], "the empty id is not an id: it is not added to A"
    report = quiet(orchestrator.id_report, "w", recipe)
    assert report.tables[0].no_id_lines == 1 and report.tables[0].no_id_line_numbers == (2,) and report.union_count == 2 and report.check3_ok


def test_a_look_up_table_with_ids_is_not_completed_and_does_not_widen_the_union(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, metadata=["s1"], additional=["zz1", "zz2"])
    done = quiet(orchestrator._read_source, "L", recipe["additional_datasets_schemas"]["L"], "w", recipe)[0].collect()
    assert done["sample_id"].to_list() == ["zz1", "zz2"] and not [c for c in done.columns if c.endswith("not_in_original_data")]
    assert quiet(orchestrator.id_report, "w", recipe).union_count == 1


def test_an_empty_data_table_is_completed_to_the_whole_union(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": []}, metadata=["s1", "s2"])
    done = table_of(orchestrator, recipe, "A")
    assert done["sample_id"].to_list() == ["s1", "s2"] and done["A_not_in_original_data"].to_list() == [True, True]


def test_a_recipe_with_no_entity_id_is_read_as_before_and_has_no_report(tmp_path):
    data = tmp_path / "d"
    data.mkdir()
    (data / "t.tsv").write_text("x\n1\n")
    recipe = minimal_recipe("w", schemas={"T": minimal_schema(str(data / "t.tsv"), {"x": "Int64"})}, plots={})
    write_recipe(tmp_path / "w.yaml", recipe)
    orchestrator = DataOrchestrator(tmp_path, tmp_path)
    assert quiet(orchestrator.id_report, "w", recipe) is None
    assert quiet(orchestrator._read_source, "T", recipe["data_schemas"]["T"], "w", recipe)[0].collect().columns == ["x"]


def test_a_table_with_an_entity_id_and_no_block_is_not_read_by_the_engine(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, blocks=False)
    with pytest.raises(DataAnalysisRecipeError) as error:
        quiet(orchestrator._read_source, "A", recipe["data_schemas"]["A"], "w", recipe)
    assert "completion" in str(error.value) and "'A'" in str(error.value)


def test_a_table_that_cannot_be_read_stops_the_completion_of_the_others_and_names_itself(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]})
    (tmp_path / "data" / "B.tsv").unlink()
    with pytest.raises(Exception) as error:
        quiet(orchestrator._read_source, "A", recipe["data_schemas"]["A"], "w", recipe)
    assert "'B'" in str(error.value) and "ids" in str(error.value)


def test_the_marker_column_is_a_normal_column_that_the_steps_of_tier_1_can_read(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    recipe["data_schemas"]["A"]["tier1"] = {"steps": [{"action": "polars_with_columns", "named_exprs": {"flag": "pl.col('A_not_in_original_data')"}}]}
    table = quiet(orchestrator.prepare_ingredient, "A", recipe["data_schemas"]["A"], "w", recipe).collect()
    assert table["sample_id"].to_list() == ["s1", "s2"] and table["flag"].to_list() == [False, True]


# -- the keys of the stored tables ---------------------------------------------------------------

def keys(orchestrator):
    clear_data_analysis_recipe_cache()
    return quiet(orchestrator.compute_data_analysis_recipe_keys, "w")


def test_a_change_in_another_table_that_takes_part_moves_the_key_of_a_table_that_reads_one_and_not_the_key_of_a_table_that_reads_none(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]}, metadata=["s1"], additional=["zz"])
    recipe["joins"] = {"J": {"ui_label": "J", "ingredients": [{"dataset_id": "A"}], "tier1": {"steps": []}}}
    recipe["data_schemas"]["B"]["tier1"] = {"steps": []}
    write_recipe(tmp_path / "w.yaml", recipe)
    before = keys(orchestrator)
    (tmp_path / "data" / "B.tsv").write_text("sample_id\tv\ns2\t0\ns7\t1\n")   # B takes part: A and J now lack a line for s7
    after = keys(orchestrator)
    assert after.tier1_key_of("A") != before.tier1_key_of("A") and after.tier1_key_of("J") != before.tier1_key_of("J")
    assert after.tier1_key_of("L") == before.tier1_key_of("L"), "a look-up reads no table that takes part: its stored table stays valid"


def test_a_change_of_the_meaning_or_the_marker_moves_the_key(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, metadata=["s1"])
    before = keys(orchestrator)
    recipe["data_schemas"]["A"]["completion"]["meaning"] = "unknown"
    write_recipe(tmp_path / "w.yaml", recipe)
    assert keys(orchestrator).tier1_key_of("A") != before.tier1_key_of("A")


def test_a_table_that_reads_a_participant_depends_on_the_data_file_of_every_participant(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]})
    parts = load_data_analysis_recipe(tmp_path / "w.yaml").table_parts
    assert set(parts["A"].datasets) == {"A", "B"} and set(parts["B"].datasets) == {"A", "B"}
