"""The audit step written at a result table no plot reads, from the lineage panel (LINEAGE-VIEW-G step 3, D-0627, D-0630), and the staging of pending steps.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_lineage_step.py -q

What is proved (the design expects: a table that nothing reads is a place in itself; a step written there changes that table and no figure, is staged like every audit step, needs its
reason, and is in the export of an Audit-mode export beside the original; the value is read in the type of the column and refused in plain words when it cannot be):
- the form reads the engine's (name, type) pairs: the columns it offers and the ones it leaves out, said by name;
- the value text: one value, a list with a comma, between with two values put in order, true or false, a date, trimmed spaces (D-0626), an empty item or no value refused in plain words,
  "equals" on text means "any of";
- `na` is the default of the operator (told by `stage_sentence`);
- `stage_nodes` stages one pending node for each place with the id of the decision, the bucket and the place, with no reason;
- on the demo recipe: the table Quality_metrics is a result table no plot reads; a step written there is run by the audit copy: the table has fewer rows, no plot is affected, `audited_frames`
  holds it; a step with no reason is refused;
- in the export (the real download generator, headless) of a recipe with a table no plot reads (U), an export made in Audit mode writes `U/T1_data_audited.tsv` beside `U/T1_data.tsv`;
  an export made in Exploration mode does not.

Mutation index (each seen failing): MUTATION S1 `stage_nodes` drops the place; MUTATION S2 `form_columns` offers every column.
"""
import io
import json
import zipfile
from pathlib import Path

import polars as pl
import pytest

from app.modules.audit_places import PLACES_BUCKET, audit_copy_for
from app.modules.audit_view import PlaceAudit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.lineage_step import FORM_KINDS, form_columns, form_ops, parse_value, stage_nodes, stage_sentence, step_params
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from app.modules.session_manager import make_audit_step
from app.tests.audit_export_harness import FLAGS, audit_kwargs
from app.tests.test_export_download_path import _download_function, _run
from app.tests.test_export_unread_tables import Wide
from utils.audit_copy import AuditCopyError
from utils.filter_values import FilterValueError
from utils.lineage_data import lineage_of

ROOT = Path(__file__).resolve().parents[2]
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text(encoding="utf-8"))
RECIPES, RAW = ROOT / BASELINE["recipes_dir"], ROOT / BASELINE["raw_data"]
DEMO = "1_test_data_ST22_dummy"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


# ---------------------------------------------------------------- the form's columns and values

def test_the_form_offers_the_columns_it_can_read_and_says_which_it_leaves_out():
    cols = [("sample_id", "String"), ("n", "Int64"), ("w", "Float64"), ("ok", "Boolean"), ("day", "Date"), ("seen", "Datetime(time_unit='us', time_zone=None)"),
            ("t", "Duration(time_unit='us')"), ("tags", "List(String)"), ("kind", "Categorical")]
    offered, left_out = form_columns(cols)
    assert [c for c, _ in offered] == ["sample_id", "n", "w", "ok", "day", "kind"]
    assert left_out == ["seen", "t", "tags"]
    assert form_columns(None) == ([], []) and form_columns([]) == ([], [])
    assert set(FORM_KINDS) == {"int", "float", "text", "category", "bool", "date"}
    assert form_ops("Int64")[:2] == ["eq", "ne"] and "between" in form_ops("Int64") and "gt" not in form_ops("String")


def test_the_value_is_read_in_the_type_of_the_column():
    assert parse_value("n", "gt", "Int64", " 5 ") == ("gt", 5)                               # D-0626: the spaces round a typed value are removed
    assert parse_value("w", "lt", "Float64", "2.5") == ("lt", 2.5)
    assert parse_value("n", "between", "Int64", "9, 3") == ("between", [3, 9])              # put in order, never refused
    assert parse_value("s", "in", "String", " a ,  b") == ("in", ["a", "b"])
    assert parse_value("s", "eq", "String", "x") == ("in", ["x"])                           # "equals" on text is "any of", as the dialog does
    assert parse_value("s", "ne", "Categorical", "x") == ("not_in", ["x"])
    assert parse_value("ok", "eq", "Boolean", "TRUE") == ("eq", True)
    assert parse_value("day", "ge", "Date", "2024-01-31") == ("ge", "2024-01-31")


@pytest.mark.parametrize("op,dtype,text,needle", [
    ("gt", "Int64", "", "No value"),
    ("gt", "Int64", "abc", ""),
    ("gt", "Int64", "5, 6", "one value"),
    ("between", "Int64", "5", "two values"),
    ("in", "String", "a,,b", "empty item"),
    ("eq", "Date", "31/01/2024", ""),
    ("eq", "Boolean", "maybe", ""),
])
def test_a_value_that_cannot_be_read_is_refused_in_plain_words(op, dtype, text, needle):
    with pytest.raises(FilterValueError) as err:
        parse_value("c", op, dtype, text)
    assert needle in str(err.value)


def test_a_whole_number_column_refuses_a_decimal():
    with pytest.raises(FilterValueError):
        parse_value("n", "gt", "Int64", "2.5")


def test_na_is_the_default_of_the_operator_and_is_told():
    keep = step_params("s", "ne", "String", "x")
    remove = step_params("s", "eq", "String", "x")
    assert keep["na"] == "keep" and remove["na"] == "remove"
    assert keep["op"] == "not_in" and keep["dtype"] == "String" and keep["column"] == "s"
    assert "rows with no s record are kept" in stage_sentence(keep) and "rows with no s record are removed" in stage_sentence(remove)


# ---------------------------------------------------------------- the staging

def test_stage_nodes_writes_one_pending_node_for_each_place_with_the_id_of_the_decision():
    scratch = make_audit_step("filter_row", {"column": "c", "op": "eq", "value": 1, "na": "remove"}, plot_scope=PLACES_BUCKET, reason="")
    state = {"x": 1, "_pending_t3_nodes": [{"id": "old"}]}
    new = stage_nodes(state, [(scratch, "T1:A"), (scratch, "T1:B")], "subtab_p")
    assert state["_pending_t3_nodes"] == [{"id": "old"}] and new["x"] == 1, "the input state is not changed"
    pend = new["_pending_t3_nodes"]
    assert [n.get("id") for n in pend] == ["old", scratch["id"], scratch["id"]]
    assert [n["place"] for n in pend[1:]] == ["T1:A", "T1:B"]
    assert all(n["plot_scope"] == PLACES_BUCKET and n["reason"] == "" and n["started_from"] == "subtab_p" for n in pend[1:])
    assert stage_nodes({}, [], "")["_pending_t3_nodes"] == []


# ---------------------------------------------------------------- the demo: a table no plot reads

@pytest.fixture(scope="module")
def demo():
    clear_data_analysis_recipe_cache()
    orch = DataOrchestrator(RECIPES, RAW)
    loaded = load_data_analysis_recipe(RECIPES / f"{DEMO}.yaml")
    book = compose_plan_book(orch, DEMO, loaded)
    yield orch, loaded, book, lineage_of(loaded.raw, book)
    clear_data_analysis_recipe_cache()


def _leaf_step(lineage, reason="drop the rows of the first entity"):
    node = lineage.node("T1:Quality_metrics")
    assert node.kind == "result" and node.choosable and node.columns
    column, dtype = next((c, t) for c, t in node.columns if t in ("String", "Categorical"))
    params = step_params(column, "ne", dtype, "zzz-not-there")
    return make_audit_step("filter_row", params, plot_scope=PLACES_BUCKET, reason=reason, place=node.id, started_from=""), column


def test_a_step_at_a_table_no_plot_reads_changes_that_table_and_no_plot(demo, tmp_path):
    orch, loaded, book, lineage = demo
    node = lineage.node("T1:Quality_metrics")
    column, dtype = next((c, t) for c, t in node.columns if t in ("String", "Categorical"))
    original = orch.materialize_tier1(DEMO, "Quality_metrics", tmp_path / "o.parquet").collect()
    value = str(original[column][0])
    params = step_params(column, "eq", dtype, value)                                         # keep the rows of the first value
    step = make_audit_step("filter_row", params, plot_scope=PLACES_BUCKET, reason="keep one entity", place=node.id, started_from="")
    audit = PlaceAudit(orch, tmp_path / "anchors", tmp_path / "audit")
    run = audit.run_of(DEMO, [step], book)
    assert run.affected_plots == [], "no plot reads that table"
    frames = run.audited_frames()
    assert set(frames) >= {"Quality_metrics"} and 0 < frames["Quality_metrics"]["T1"].height < original.height
    assert set(frames["Quality_metrics"]["T1"][column]) == {value}
    # a table beside it is not changed
    assert "ResFinder" not in frames and "ST22_Anchor" not in frames


def test_a_step_with_no_reason_is_refused_by_the_audit_copy(demo):
    _, loaded, book, lineage = demo
    step, _ = _leaf_step(lineage, reason="")
    with pytest.raises(AuditCopyError):
        audit_copy_for(loaded.raw, [step], book)


def test_the_lineage_says_the_table_is_a_leaf_and_the_form_offers_its_plan_columns(demo):
    lineage = demo[3]
    node = lineage.node("T1:Quality_metrics")
    offered, left_out = form_columns(node.columns)
    assert offered and {c for c, _ in offered} | set(left_out) == {c for c, _ in node.columns}


# ---------------------------------------------------------------- the export

def _export(root, monkeypatch, nodes, in_audit):
    world = Wide(root)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, [], monkeypatch, flags=FLAGS, **audit_kwargs(world, nodes, in_audit=in_audit)))
    archive = zipfile.ZipFile(io.BytesIO(yielded[0]))
    assert "EXPORT_NOT_CREATED.txt" not in archive.namelist(), archive.namelist()
    return {n.split("/", 1)[-1]: archive.read(n) for n in archive.namelist()}


def _u_step():
    params = step_params("weight", "gt", "Float64", "2")
    return make_audit_step("filter_row", params, plot_scope=PLACES_BUCKET, reason="heavier than 2", place="T1:U", started_from="")


def test_an_export_made_in_audit_mode_writes_the_audited_file_of_a_table_no_plot_reads(tmp_path, monkeypatch):
    plain = _export(tmp_path / "plain", monkeypatch, [], in_audit=True)
    members = _export(tmp_path / "audit", monkeypatch, [_u_step()], in_audit=True)
    assert "U/T1_data_audited.tsv" in members and "U/T1_data_audited.tsv" not in plain
    original = pl.read_csv(io.BytesIO(members["U/T1_data.tsv"]), separator="\t")
    audited = pl.read_csv(io.BytesIO(members["U/T1_data_audited.tsv"]), separator="\t")
    assert members["U/T1_data.tsv"] == plain["U/T1_data.tsv"], "the original is what an export with no audit step writes"
    assert original.height > audited.height > 0 and audited["weight"].min() > 2, "the ids are completed first (rows with no weight are added): the audited table keeps only the heavier ones"
    # no other table has an audited file
    assert [n for n in members if n.endswith("_audited.tsv")] == ["U/T1_data_audited.tsv"]


def test_an_export_made_in_exploration_mode_keeps_the_original_of_that_table(tmp_path, monkeypatch):
    members = _export(tmp_path, monkeypatch, [_u_step()], in_audit=False)
    assert "U/T1_data.tsv" in members and not [n for n in members if n.endswith("_audited.tsv")]
