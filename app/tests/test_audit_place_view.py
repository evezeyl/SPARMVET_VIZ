"""The place reader (`app/modules/audit_place_view.py`): what is on screen, the one table reader with audit steps, the identity of the view for the filters, the check that a condition fits a place
(HOME audit, demo slice 2; nothing on screen reads the module yet).

The design expects (header-strip design page, 2026-11-26): in Audit mode the table shown is the table of the place chosen in the lineage panel, the AUDITED one where an audit step changes it and the
original where none does (D-0622), and it is the very table the export writes for that place; a place the open plot is not built from is said so; a stale or forbidden place never raises, it gives the default
and a reason (D-0632); a filter built on a table is kept when the table shown is the same and cleared when it is another (D-0311, D-0505, D-0506).

What is proved:
- `viewed`: Exploration for each data choice; Audit with no place, one place, several (the first valid is shown, the others counted), a stale id, the metadata, an empty tier 2, a node that cannot be
  chosen, a place outside the open plot (`from_open_plot` equals what the graph says: the plot is among the plots read from the place);
- `table_for` with audit steps on the demo recipe (a step at a tier 1, a tier 2, a plot's tier 3, a table no plot reads, and all of them together): for EVERY place of the lineage the table equals the one the
  audit run writes for it (`AuditRun.audited_frames`, `plot_table`), the original where the run leaves it, and `facts.audited` and its reason are right;
- the same on a real export: the real download generator is run on the small recipe of `test_export_unread_tables.Wide` (a table nobody reads, a join nobody reads, a plot) and every place shows the same
  rows as the file the export wrote for it (`T1_data.tsv`, `T1_data_audited.tsv`, `T3_data_p.tsv`);
- `view_identity` equals HOME's own key (`view_key` with `viewed_table`), is the same for two plots that read one table, differs for another table, another tier, another mode, and for a plot with tier-3 steps of its own;
- `condition_fits`: column absent, another type, the same, a place not in the lineage, columns not known.

Mutation index (each seen failing): MUTATION Q1 `table_for` reads the tier-2 reader for a T1 place (walk file); Q2 `table_for` returns the original even when the audit reader answers (the audited
cases and the export case); Q3 `viewed` ignores the first chosen place (the walk file and here); Q4 `table_for` swaps the T1 and T2 audited reads (the audited cases).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_place_view.py -q
"""
import dataclasses
import io
import zipfile

import polars as pl
import pytest

from app.modules.audit_place_view import (AUDIT, EXPLORATION, NothingToShow, Readers, condition_fits, table_for, view_identity, viewed)
from app.modules.audit_places import PLACES_BUCKET
from app.modules.audit_view import PlaceAudit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.plan_composer import compose_plan_book
from app.modules.session_manager import make_audit_step
from app.modules.t3_audit_engine import view_key, viewed_table
from app.tests.audit_export_harness import FLAGS, audit_kwargs
from app.tests.test_audit_view import RECIPE_ID, World
from app.tests.test_export_download_path import _download_function, _run
from app.tests.test_export_unread_tables import Wide
from utils import recipe_tiers
from utils.lineage_data import lineage_of
from utils.recipe_graph import build_graph


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    clear_data_analysis_recipe_cache()
    made = World(tmp_path_factory.mktemp("place_view"))
    made.lineage = lineage_of(made.loaded.raw, made.plans)
    yield made
    clear_data_analysis_recipe_cache()


def readers_of(world, nodes, audit=None):
    audit = audit or world.audit()
    return Readers(
        source=lambda t: world.orch.read_source(RECIPE_ID, t),
        tier1=lambda t: world.orch.materialize_tier1(RECIPE_ID, t, world.anchors / f"{t}.parquet"),
        tier2=lambda t: world.orch.materialize_tier2(RECIPE_ID, t, world.anchors / f"{t}.parquet"),
        plot=lambda p: world.orch.materialize_tier3(RECIPE_ID, p, world.anchors),
        audited_table=lambda t, tier: audit.table_lazy(RECIPE_ID, t, tier, nodes, world.plans),
        audited_plot=lambda p: audit.plot_lazy(RECIPE_ID, p, nodes, world.plans),
        committed_steps=len(nodes))


def original_of(world, node):
    if node.kind == "T3":
        return world.orch.materialize_tier3(RECIPE_ID, node.name, world.anchors).collect()
    build = world.orch.materialize_tier2 if node.kind == "T2" else world.orch.materialize_tier1
    return build(RECIPE_ID, node.name, world.anchors / f"{node.name}.parquet").collect()


# ------------------------------------------------------------------------------------------------ viewed
def test_exploration_follows_the_data_choice_and_never_names_a_place(world):
    for choice, tier in (("T1", "T1"), ("T2", "T2"), ("T3", "T3")):
        shown = viewed(EXPLORATION, choice, None, "amr_heatmap", ["T1:MLST"], world.graph, world.lineage)
        target = world.graph.plot_target("amr_heatmap")
        assert (shown.mode, shown.tier, shown.table, shown.place, shown.plot) == (EXPLORATION, tier, target, None, "amr_heatmap")
        assert shown.shown_plot == ("amr_heatmap" if tier == "T3" else None) and shown.is_default is False and shown.from_open_plot is True
        assert shown.others == 0 and shown.refused == (), "a chosen place means nothing in Exploration"
    source = viewed(EXPLORATION, "SRC", "ResFinder", "amr_heatmap", [], world.graph, world.lineage)
    assert (source.tier, source.table, source.place, source.shown_plot) == ("Source", "ResFinder", None, None)
    nothing = viewed(EXPLORATION, "T3", None, None, [], world.graph, world.lineage)
    assert nothing.table is None and nothing.from_open_plot is None
    with pytest.raises(NothingToShow):
        table_for(nothing, readers_of(world, []))


def test_audit_with_no_place_shows_the_table_the_open_plot_reads(world):
    shown = viewed(AUDIT, "T1", None, "amr_heatmap", [], world.graph, world.lineage)
    assert shown.is_default and shown.place == "T3:amr_heatmap" and shown.tier == "T3" and shown.table == world.graph.plot_target("amr_heatmap")
    assert shown.shown_plot == "amr_heatmap" and shown.from_open_plot is True and shown.others == 0 and shown.refused == ()
    # the data choice does not matter in Audit mode: the strip is hidden
    assert shown == viewed(AUDIT, "SRC", "ResFinder", "amr_heatmap", [], world.graph, world.lineage)
    frame, facts = table_for(shown, readers_of(world, []))
    assert frame.collect().equals(world.original_table("amr_heatmap")) and facts.audited is False
    no_plot = viewed(AUDIT, "T3", None, None, [], world.graph, world.lineage)
    assert no_plot.table is None and no_plot.from_open_plot is None
    with pytest.raises(NothingToShow, match="no table to show"):
        table_for(no_plot, readers_of(world, []))


def test_a_chosen_place_is_shown_and_says_whether_the_open_plot_is_built_from_it(world):
    for open_plot in ("amr_heatmap", "mlst_bar"):
        for node in world.lineage.nodes:
            if not node.choosable:
                continue
            shown = viewed(AUDIT, "T3", None, open_plot, [node.id], world.graph, world.lineage)
            assert shown.place == node.id and shown.is_default is False
            assert shown.from_open_plot == (open_plot in world.graph.plots_reading(node.id)), (open_plot, node.id)
    outside = viewed(AUDIT, "T3", None, "mlst_bar", ["T1:ResFinder"], world.graph, world.lineage)
    assert outside.from_open_plot is False and outside.plot == "mlst_bar" and outside.tier == "T1" and outside.table == "ResFinder" and outside.shown_plot is None
    own = viewed(AUDIT, "T3", None, "mlst_bar", ["T3:amr_heatmap"], world.graph, world.lineage)
    assert own.tier == "T3" and own.shown_plot == "amr_heatmap" and own.table == world.graph.plot_target("amr_heatmap") and own.from_open_plot is False


def test_with_several_places_the_first_valid_one_is_shown_and_the_others_are_counted(world):
    shown = viewed(AUDIT, "T3", None, "amr_heatmap", ["T1:MLST", "T1:ResFinder", "T2:ResFinder", "T1:MLST"], world.graph, world.lineage)
    assert shown.place == "T1:MLST" and shown.others == 2 and shown.refused == (), "a place named twice counts once"
    stale_first = viewed(AUDIT, "T3", None, "amr_heatmap", ["T1:NoSuchTable", "T1:ResFinder"], world.graph, world.lineage)
    assert stale_first.place == "T1:ResFinder" and stale_first.others == 0 and [p for p, _ in stale_first.refused] == ["T1:NoSuchTable"]


def test_a_place_that_cannot_be_shown_gives_the_default_and_a_reason_never_an_exception(world):
    meta = f"T1:{recipe_tiers.METADATA_SCHEMA}"
    assert world.graph.has_node(meta), "the demo has a metadata table: the case is real"
    cases = {"T1:NoSuchTable": "not a place of this recipe", meta: recipe_tiers.METADATA_NOT_A_PLACE, "DS:ResFinder": "file as read"}
    for place, words in cases.items():
        shown = viewed(AUDIT, "T3", None, "amr_heatmap", [place], world.graph, world.lineage)
        assert shown.is_default and shown.place == "T3:amr_heatmap" and shown.others == 0, place
        assert len(shown.refused) == 1 and shown.refused[0][0] == place and words in shown.refused[0][1], (place, shown.refused)
    empty_t2 = next(n for n in world.graph.places() if n.startswith("T2:") and not world.graph.node(n).steps)
    shown = viewed(AUDIT, "T3", None, "amr_heatmap", [empty_t2], world.graph, world.lineage)
    assert shown.is_default and "no tier-2 steps" in shown.refused[0][1] and "tier 1" in shown.refused[0][1]
    # a node of the lineage that cannot be chosen (a tier 2 no plot reads) is refused with the lineage's own reason
    node = next(n for n in world.lineage.nodes if n.kind == "T2")
    blocked = dataclasses.replace(world.lineage, nodes=tuple(dataclasses.replace(n, choosable=False, not_choosable_reason="no plot reads this tier 2") if n.id == node.id else n
                                                              for n in world.lineage.nodes))
    shown = viewed(AUDIT, "T3", None, "amr_heatmap", [node.id], world.graph, blocked)
    assert shown.is_default and shown.refused == ((node.id, "no plot reads this tier 2"),)


def test_a_bad_call_is_refused_in_plain_words(world):
    with pytest.raises(KeyError, match="no plot 'ghost'"):
        viewed(AUDIT, "T3", None, "ghost", [], world.graph, world.lineage)
    with pytest.raises(ValueError, match="mode is"):
        viewed("both", "T3", None, "amr_heatmap", [], world.graph, world.lineage)
    with pytest.raises(ValueError, match="data_view"):
        viewed(EXPLORATION, "T4", None, "amr_heatmap", [], world.graph, world.lineage)


# ------------------------------------------------------------------------------------------------ the one reader, with audit steps on the demo
CASES = {
    "a step at the tier 1 of ResFinder": [("T1:ResFinder", {})],
    "a step at the tier 2 of ResFinder": [("T2:ResFinder", {})],
    "a step at the tier 3 of a plot": [("T3:amr_heatmap", {})],
    "a step at a table no plot reads": [("T1:ResFinder_with_metadata", {})],
    "the four together": [("T1:ResFinder", {}), ("T2:ResFinder", {}), ("T3:amr_heatmap", {}), ("T1:ResFinder_with_metadata", {})],
}


@pytest.mark.parametrize("label", list(CASES))
def test_with_audit_steps_every_place_shows_the_table_the_audit_run_writes_for_it(world, label):
    nodes = [world.node(place=place, value=world.victim) for place, _ in CASES[label]]
    audit = world.audit()
    run = audit.run_of(RECIPE_ID, nodes, world.plans)
    readers = readers_of(world, nodes, audit)
    audited_places, original_places = [], []
    for node in world.lineage.nodes:
        shown = viewed(AUDIT, "T3", None, "amr_heatmap", [node.id], world.graph, world.lineage)
        frame, facts = table_for(shown, readers)
        got = frame.collect()
        if node.kind == "T3":
            plot = run.plot_table(node.name)
            expected = None if plot is None else plot.collect()
        else:
            expected = run.audited_frames().get(node.name, {}).get("T2" if node.kind == "T2" else "T1")
        if expected is None:
            assert got.equals(original_of(world, node)) and facts.audited is False, f"{label}: {node.id} must be the original"
            assert "No audit step changes this table" in facts.why_original, node.id
            original_places.append(node.id)
        else:
            assert got.equals(expected) and facts.audited is True and facts.why_original == "", f"{label}: {node.id} must be the audited table"
            assert not got.equals(original_of(world, node)), f"{label}: {node.id} the audited table must differ from the original"
            audited_places.append(node.id)
    assert audited_places and original_places, "a case that audits nothing, or everything, proves nothing"
    for place, _ in CASES[label]:
        assert place in audited_places, (label, place, "the place of a step shows the audited table")
    assert "T1:MLST" in original_places, "a table beside every step reads the original"


def test_a_step_at_resfinder_leaves_the_tables_beside_it_as_the_original_and_changes_the_ones_built_from_it(world):
    nodes = [world.node(place="T1:ResFinder", value=world.victim)]
    audit = world.audit()
    readers = readers_of(world, nodes, audit)
    changed = {"T1:ResFinder", "T2:ResFinder", "T1:ResFinder_with_metadata"} & {n.id for n in world.lineage.nodes}
    beside = {"T1:MLST"}
    assert changed == {"T1:ResFinder", "T2:ResFinder", "T1:ResFinder_with_metadata"}
    for place in changed | beside:
        frame, facts = table_for(viewed(AUDIT, "T3", None, "amr_heatmap", [place], world.graph, world.lineage), readers)
        assert facts.audited == (place in changed), place
        if place in changed:
            assert world.victim not in frame.collect()["sample_id"].to_list(), place


def test_without_a_committed_step_every_place_is_the_original_and_the_words_say_no_step_was_added(world):
    readers = readers_of(world, [])
    for node in world.lineage.nodes:
        frame, facts = table_for(viewed(AUDIT, "T3", None, "amr_heatmap", [node.id], world.graph, world.lineage), readers)
        assert facts.audited is False and "No audit step has been added yet" in facts.why_original
        assert frame.collect().equals(original_of(world, node)), node.id


def test_a_step_that_cannot_run_is_raised_at_the_places_it_reaches_and_not_at_the_others(world):
    from app.modules.audit_run import AuditRunError
    broken = [world.node(place="T1:ResFinder", params={"column": "no_such_column", "op": "ne", "value": "x", "na": "keep"})]
    readers = readers_of(world, broken)
    with pytest.raises(AuditRunError):
        table_for(viewed(AUDIT, "T3", None, "amr_heatmap", ["T1:ResFinder"], world.graph, world.lineage), readers)
    with pytest.raises(AuditRunError):
        table_for(viewed(AUDIT, "T3", None, "amr_heatmap", [], world.graph, world.lineage), readers)
    frame, facts = table_for(viewed(AUDIT, "T3", None, "amr_heatmap", ["T1:MLST"], world.graph, world.lineage), readers)
    assert facts.audited is False and frame.collect().equals(original_of(world, world.lineage.node("T1:MLST")))


def test_a_table_with_no_tier2_steps_asked_at_t2_in_exploration_is_its_tier1(world):
    readers = readers_of(world, [])
    plot = next(p for p in world.graph.plots() if not world.graph.node(f"T2:{world.graph.plot_target(p)}").steps)
    target = world.graph.plot_target(plot)
    frame, _ = table_for(viewed(EXPLORATION, "T2", None, plot, [], world.graph, world.lineage), readers)
    assert frame.collect().equals(world.orch.materialize_tier1(RECIPE_ID, target, world.anchors / f"{target}.parquet").collect())


# ------------------------------------------------------------------------------------------------ the same on a real export
def step(place, column="group", op="eq", value="A", dtype="String", reason="keep group A"):
    return make_audit_step("filter_row", {"column": column, "op": op, "value": value, "dtype": dtype, "na": "remove"}, plot_scope=PLACES_BUCKET, reason=reason, place=place, started_from="subtab_p")


def as_text(frame):
    return frame.with_columns(pl.all().cast(pl.String))


def tsv(members, name):
    return pl.read_csv(io.BytesIO(members[name]), separator="\t", infer_schema_length=0)


EXPORT_CASES = {
    "no step": [],
    "a step at the tier 1 of T": [step("T1:T")],
    "a step at a table no plot reads": [step("T1:D", column="color", value="red", reason="red only")],
    "a step at a source nobody reads": [step("T1:U", column="weight", op="gt", value=2, dtype="Float64", reason="weights above 2")],
    "tier 1 of T and tier 3 of the plot": [step("T1:T"), step("T3:p", column="sample_id", op="ne", value="s2", reason="s2 failed")],
}


@pytest.mark.parametrize("label", list(EXPORT_CASES))
def test_every_place_shows_the_rows_of_the_file_the_export_wrote_for_it(tmp_path, monkeypatch, label):
    nodes = EXPORT_CASES[label]
    clear_data_analysis_recipe_cache()
    wide = Wide(tmp_path)
    view = wide.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(wide, view, [], monkeypatch, flags=FLAGS, **audit_kwargs(wide, nodes, in_audit=True)))
    archive = zipfile.ZipFile(io.BytesIO(yielded[0]))
    assert "EXPORT_NOT_CREATED.txt" not in archive.namelist(), archive.namelist()
    members = {n.split("/", 1)[-1]: archive.read(n) for n in archive.namelist()}
    loaded = load_data_analysis_recipe(wide.data_analysis_recipes_dir / "tiny.yaml")
    graph = build_graph(loaded.raw)
    plans = compose_plan_book(wide.orch, "tiny", loaded, graph)
    lineage = lineage_of(loaded.raw, plans)
    anchors = wide.root / "user" / "anchors"
    audit = PlaceAudit(wide.orch, anchors, wide.root / "user" / "audit_anchors")
    readers = Readers(
        source=lambda t: wide.orch.read_source("tiny", t),
        tier1=lambda t: wide.orch.materialize_tier1("tiny", t, anchors / f"{t}.parquet"),
        tier2=lambda t: wide.orch.materialize_tier2("tiny", t, anchors / f"{t}.parquet"),
        plot=lambda p: wide.orch.materialize_tier3("tiny", p, anchors),
        audited_table=lambda t, tier: audit.table_lazy("tiny", t, tier, nodes, plans),
        audited_plot=lambda p: audit.plot_lazy("tiny", p, nodes, plans),
        committed_steps=len(nodes))
    audited_seen = 0
    for node in lineage.nodes:
        shown = viewed(AUDIT, "T3", None, "p", [node.id], graph, lineage)
        frame, facts = table_for(shown, readers)
        if node.kind == "T3":
            written = "C/T3_data_p.tsv" if "C/T3_data_p.tsv" in members else "C/T1_data.tsv"     # T3 equals T1 when no step reaches the plot (it has no tier-2 or tier-3 steps of the recipe)
        else:
            audited_name = f"{node.name}/T1_data_audited.tsv"
            written = audited_name if audited_name in members else f"{node.name}/T1_data.tsv"
        assert as_text(frame.collect()).equals(tsv(members, written)), f"{label}: {node.id} shows other rows than {written}"
        if node.kind != "T3":
            assert facts.audited == (written.endswith("_audited.tsv")), (label, node.id)
        else:
            assert facts.audited == ("C/T3_data_p.tsv" in members), (label, node.id)
        audited_seen += facts.audited
    if nodes:
        assert audited_seen >= 1, "an audit step that changes no place proves nothing"
    else:
        assert audited_seen == 0
    clear_data_analysis_recipe_cache()


# ------------------------------------------------------------------------------------------------ view_identity
def home_key(recipe_id, mode, choice, source, target, plot, has_steps):
    """The key HOME builds today (`home_theater._current_view_key`), written out here."""
    return view_key(recipe_id, mode, choice, source if choice == "SRC" else None, viewed_table(choice, target, plot, has_steps) if choice != "SRC" else None)


def test_the_identity_is_the_key_home_builds_today_in_exploration(world):
    target = world.graph.plot_target("amr_heatmap")
    for choice in ("SRC", "T1", "T2", "T3"):
        for has_steps in (False, True):
            shown = viewed(EXPLORATION, choice, "ResFinder", "amr_heatmap", [], world.graph, world.lineage)
            assert view_identity(shown, RECIPE_ID, has_steps) == home_key(RECIPE_ID, "exploration", choice, "ResFinder", target, "amr_heatmap", has_steps), (choice, has_steps)
    t1 = viewed(EXPLORATION, "T1", None, "amr_heatmap", [], world.graph, world.lineage)
    t2 = viewed(EXPLORATION, "T2", None, "amr_heatmap", [], world.graph, world.lineage)
    assert view_identity(t1, RECIPE_ID) != view_identity(t2, RECIPE_ID), "today's rule (PROVISIONAL in the contract): T1 and T2 are different views, also of a table with no tier-2 steps"


def test_two_places_that_show_the_same_table_keep_the_filters_and_another_table_clears_them(world):
    reading = {}
    for plot in world.graph.plots():
        reading.setdefault(world.graph.plot_target(plot), []).append(plot)
    target, (first, second, *_) = next((t, p) for t, p in reading.items() if len(p) >= 2)
    one = viewed(AUDIT, "T3", None, first, [f"T3:{first}"], world.graph, world.lineage)
    other = viewed(AUDIT, "T3", None, first, [f"T3:{second}"], world.graph, world.lineage)
    assert view_identity(one, RECIPE_ID) == view_identity(other, RECIPE_ID), "two plots on one table, neither with tier-3 steps of its own: one table, one key (D-0505, D-0506)"
    assert view_identity(one, RECIPE_ID, True) != view_identity(other, RECIPE_ID, False), "a plot with tier-3 steps of its own reads a table of its own"
    elsewhere = viewed(AUDIT, "T3", None, first, ["T1:MLST"], world.graph, world.lineage)
    assert view_identity(elsewhere, RECIPE_ID) != view_identity(one, RECIPE_ID), "another table: another key"
    default = viewed(AUDIT, "T3", None, first, [], world.graph, world.lineage)
    assert view_identity(default, RECIPE_ID) == view_identity(one, RECIPE_ID), "choosing the open plot's own place changes nothing"
    t1, t2 = (viewed(AUDIT, "T3", None, first, [f"{tier}:ResFinder"], world.graph, world.lineage) for tier in ("T1", "T2"))
    assert view_identity(t1, RECIPE_ID) != view_identity(t2, RECIPE_ID), "a table with tier-2 steps: its T1 and its T2 are two views"
    expl = viewed(EXPLORATION, "T3", None, first, [], world.graph, world.lineage)
    assert view_identity(expl, RECIPE_ID) != view_identity(one, RECIPE_ID), "a switch of mode is a new view (D-0361)"
    assert view_identity(one, RECIPE_ID) != view_identity(one, "another_recipe")


# ------------------------------------------------------------------------------------------------ condition_fits
def test_a_condition_fits_a_place_only_when_the_column_is_there_with_the_same_type(world):
    node = world.lineage.node("T1:ResFinder")
    assert node.columns, "the demo gives the engine's plan for ResFinder"
    column, kind = node.columns[0]
    assert condition_fits("T1:ResFinder", column, kind, world.lineage) == (True, "")
    assert condition_fits("T1:ResFinder", column, "NoSuchType", world.lineage)[0] is False
    absent_ok, absent = condition_fits("T1:MLST", "no_such_column", "String", world.lineage)
    assert absent_ok is False and "no_such_column" in absent and "not in" in absent and "MLST" in absent
    other_ok, other = condition_fits("T1:ResFinder", column, "Int8" if kind != "Int8" else "String", world.lineage)
    assert other_ok is False and kind in other and ("Int8" in other or "String" in other)
    assert condition_fits("T1:ResFinder", column, pl.String if kind == "String" else kind, world.lineage)[0] is True, "the engine's own type is accepted as well as its text"
    ghost_ok, ghost = condition_fits("T1:Nothing", column, kind, world.lineage)
    assert ghost_ok is False and "not a place" in ghost
    unknown = dataclasses.replace(world.lineage, nodes=tuple(dataclasses.replace(n, columns=None, columns_note="the engine failed here") if n.id == "T1:ResFinder" else n for n in world.lineage.nodes))
    unknown_ok, why = condition_fits("T1:ResFinder", column, kind, unknown)
    assert unknown_ok is False and "not known" in why and "the engine failed here" in why


def test_a_column_every_place_of_a_plot_holds_fits_each_of_them(world):
    """A column of the table a plot reads, checked against the places it is built from: it fits where it is there with its type, and says why where it is not."""
    plot_node = world.lineage.node("T3:amr_heatmap")
    column, kind = plot_node.columns[0]
    verdicts = {n.id: condition_fits(n.id, column, kind, world.lineage) for n in world.lineage.nodes if n.choosable}
    assert verdicts["T3:amr_heatmap"] == (True, "")
    assert any(ok for ok, _ in verdicts.values()) and any(not ok for ok, _ in verdicts.values())
    assert all(why for ok, why in verdicts.values() if not ok) and all(why == "" for ok, why in verdicts.values() if ok)


def test_the_words_returned_use_the_owners_names_for_the_tables(world):
    """Result data (T3) and the table the plot reads (T1, T2 or T3); never "plot data" or "the plot's table" (owner, 2026-11-26)."""
    plot_node = world.lineage.node("T3:amr_heatmap")
    sentences = [condition_fits("T3:amr_heatmap", "no_such_column", "String", world.lineage)[1],
                 condition_fits("T3:amr_heatmap", plot_node.columns[0][0], "NoSuchType", world.lineage)[1],
                 condition_fits("T1:MLST", "no_such_column", "String", world.lineage)[1]]
    for place in ("T1:NoSuchTable", "DS:ResFinder", f"T1:{recipe_tiers.METADATA_SCHEMA}"):
        sentences += [why for _, why in viewed(AUDIT, "T3", None, "amr_heatmap", [place], world.graph, world.lineage).refused]
    readers = readers_of(world, [])
    for shown in (viewed(AUDIT, "T3", None, "amr_heatmap", [], world.graph, world.lineage), viewed(AUDIT, "T3", None, "amr_heatmap", ["T1:MLST"], world.graph, world.lineage)):
        sentences.append(table_for(shown, readers)[1].why_original)
    assert "Result data (T3) of the plot amr_heatmap" in sentences[0]
    for text in sentences:
        assert "plot data" not in text.lower() and "plot's table" not in text.lower(), text
