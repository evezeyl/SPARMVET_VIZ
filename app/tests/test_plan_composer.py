"""The plan of every place of a recipe is composed by the build's own code, equals the real run, and reaches every gate of a key drop (LBFB step 0b, D-0325).

D-0325: the places where a column exists are found by asking the engine for the plan of every place (names and types). `app/modules/plan_composer.py` does it with the
functions the build calls (`orchestrator.ingredient_parts`, `join_parts`, `tier2_parts`, `tier3_parts`, `tier3_frames`), reading `collect_schema()` after each step and
building nothing. D-0351: each reading is checked against the engine's plan, the plan stays the authority. D-0358: a key drop is refused by place. D-0195: no silent failure.

What is proved:
- the standing test: on EVERY shipped recipe the plan at every place of every table equals the table really built (the stored parquet file of each stored table, the real
  `collect()` of every step of tier 1 of a table, of a join and of tier 2), names and types; the number of places compared is counted so that an empty comparison cannot pass;
  a tier 3 with steps (the staged world) too;
- the book has an entry for every (node, k) of the graph, also when places fail; a failure is a VALUE: the engine's sentence, where it first failed, and every place below it
  (the places that read it included, k = 0 too); the other places keep their plans; nothing is raised for a fault of the recipe or its data (a step that names a missing column in
  each of tier 1, tier 2 and tier 3, a missing data file, a refused audit key in a recipe that is not an audit copy);
- the composer builds and stores nothing (no `write_anchor`, no file in the folder of the stored tables) and composes each source once;
- an audit copy: the plan follows the audit steps and the original's plan does not move;
- the five places of the shipped recipes that the names-only gate allowed (the review of 2026-11-20, finding F2): with the engine's plan the gate refuses them as join keys;
  without a plan the gate cannot see them as keys: it ALLOWS the drop with a warning (D-0449; it was "Cannot tell" and not written, the builder's), through `add_step`, the integrity
  check, the engine's own check of a copy and the checker's AU04, and the audit run (which composes the plan itself) refuses them before building; every caller of the gate in
  the app hands it the plan (HOME's column box, the session restore, the audit run, the engine's check of a copy);
- candidate plans: the plan of the recipe with one more audit step; a drop of a column that a later filter needs fails there and the walk reports `build_fails`; a refused drop
  makes no candidate; the audit copy given is not changed.

Mutation index (each seen failing, see the report): MUTATION PC1 the composer leaves a step out; PC2 a failure is swallowed (the place keeps the plan before); PC3 the plan after
every step is the plan at the end of the tier; PC4 `run_audit` asks the check without the plan; PC5 the candidate recomposes the recipe without the new step; PC6 the places below a
failure are left out of the book.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_plan_composer.py -q
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import polars as pl
import pytest

from app.modules import plan_composer
from app.modules.audit_run import AuditRunError, run_audit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe, loaded_from_resolved
from app.modules.opening_build import plan_places
from app.modules.orchestrator import DataOrchestrator, tier2_parts
from app.modules.plan_composer import compose_candidate_plan_book, compose_plan_book
from app.tests.test_audit_run import World
from app.tests.test_tier3_reader import DROP_GROUP, KEEP_FROM_2, KEEP_FROM_3, Tier3World
from utils import audit_copy, key_drop
from utils.audit_copy import AuditCopyError, add_step, integrity_errors, start_audit
from utils.lineage_records import BUILD_FAILS, Start
from utils.lineage_walk import walk
from utils.plan_book import Plan, PlanBook, PlanFailure
from utils.recipe_check import check_recipe
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text(encoding="utf-8"))
RECIPES, RAW = ROOT / BASELINE["recipes_dir"], ROOT / BASELINE["raw_data"]
DEMO, ABROMICS = "1_test_data_ST22_dummy", "demo_abromics"
# the five places the names-only gate allowed (review 3, finding F2): a source whose own tier 1 holds a step the walk does not read
FIVE = [(DEMO, "T1:Summary", "sample_id"), (DEMO, "T1:MLST", "sample_id"), (DEMO, "T1:VirulenceFinder", "sample_id"), (DEMO, "T1:VirulenceFinder", "VF_gene"),
        (ABROMICS, "T1:MLST", "sample_id")]


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def shipped(recipe_id):
    orch = DataOrchestrator(RECIPES, RAW)
    loaded = load_data_analysis_recipe(RECIPES / f"{recipe_id}.yaml")
    graph = build_graph(loaded.raw)
    return orch, loaded, graph, compose_plan_book(orch, recipe_id, loaded, graph)


def pairs(schema):
    return [(name, str(kind)) for name, kind in schema.items()]


def entries_of(graph):
    return [(nid, k) for nid in graph.nodes() for k in range(len(graph.node(nid).steps) + 1)]


def failures_of(book, graph):
    return {key for key in entries_of(graph) if isinstance(book.get(*key), PlanFailure)}


# ---------------------------------------------------------------------------------------------------------------------
# The standing test: the plan equals the real run, on every shipped recipe
# ---------------------------------------------------------------------------------------------------------------------


def real_schema_after(orch, recipe_id, loaded, graph, nid, k, tmp_path):
    """The columns of the table after k steps of the node, from a REAL run: the real data, the prefix of the steps run and collected."""
    raw, node = loaded.raw, graph.node(nid)
    schemas = orch._schemas_of(raw)
    if node.kind == "DS":
        lf, _, _ = orch.ingredient_parts(node.name, schemas[node.name], recipe_id, raw)
        return pairs(lf.collect().schema)
    if node.kind == "T1" and node.collection_kind == "schema":
        lf, engine, rules = orch.ingredient_parts(node.name, schemas[node.name], recipe_id, raw)
        return pairs(engine.wrangler().run(lf, copy.deepcopy(rules[:k])).collect().schema)
    if node.kind == "T1":
        spec = raw["joins"][node.name]
        ids = [i.get("dataset_id") if isinstance(i, dict) else i for i in spec["ingredients"]]
        frames = {ds: orch.prepare_ingredient(ds, schemas[ds], recipe_id, raw) for ds in ids}
        parts = orch.join_parts(recipe_id, raw, node.name, spec, frames, schemas)
        if k == 0:
            return pairs(frames[ids[0]].collect().schema)
        return pairs(parts.new_assembler().assemble(copy.deepcopy(parts.steps[:k])).collect().schema)
    if node.kind == "T2":
        engine, steps = tier2_parts(raw, node.name)
        t1 = orch.materialize_tier1(recipe_id, node.name, tmp_path / f"{node.name}.parquet")
        return pairs(engine.wrangler().run(t1, copy.deepcopy(steps[:k])).collect().schema)
    raise AssertionError(nid)


@pytest.mark.parametrize("recipe_id", sorted(BASELINE["recipes"]))
def test_the_plan_equals_the_real_run_at_every_place_of_every_shipped_recipe(tmp_path, recipe_id):
    orch, loaded, graph, book = shipped(recipe_id)
    assert failures_of(book, graph) == set(), "a shipped recipe plans everywhere"
    compared = 0
    for nid, k in entries_of(graph):
        if graph.node(nid).kind == "T3":
            continue                                     # no shipped recipe has a tier 3 step: the staged world below
        assert book.get(nid, k).columns == tuple(real_schema_after(orch, recipe_id, loaded, graph, nid, k, tmp_path)), (recipe_id, nid, k)
        compared += 1
    assert compared == len([key for key in entries_of(graph) if graph.node(key[0]).kind != "T3"]) and compared >= 6


@pytest.mark.parametrize("recipe_id", sorted(BASELINE["recipes"]))
def test_the_plan_equals_every_table_the_opening_stores_on_every_shipped_recipe(tmp_path, recipe_id):
    """The stored parquet files (what the opening builds and keeps) have exactly the columns and types the plan gave for the end of that place; a plot reads the end of its target."""
    orch, loaded, graph, book = shipped(recipe_id)
    keys = orch.compute_data_analysis_recipe_keys(recipe_id)
    stored = 0
    for kind, ident, _ in plan_places(loaded.raw):
        if kind == "tier1":
            orch.materialize_tier1(recipe_id, ident, tmp_path / f"{ident}.parquet", keys=keys)
            file = tmp_path / f"{ident}.parquet"
        elif kind == "tier2":
            orch.materialize_tier2(recipe_id, ident, tmp_path / f"{ident}.parquet", keys=keys)
            file = tmp_path / f"{ident}__T2.parquet"
        else:
            continue
        end = book.get(f"{'T1' if kind == 'tier1' else 'T2'}:{ident}", len(graph.node(f"{'T1' if kind == 'tier1' else 'T2'}:{ident}").steps))
        assert end.columns == tuple(pairs(pl.scan_parquet(file).collect_schema())), (recipe_id, kind, ident)
        stored += 1
    assert stored == len([1 for kind, _, _ in plan_places(loaded.raw) if kind in ("tier1", "tier2")]) and stored >= 1


def test_a_tier3_with_steps_is_planned_as_it_is_built(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    loaded = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml")
    graph = build_graph(loaded.raw)
    book = compose_plan_book(world.orch, "tiny", loaded, graph)
    assert failures_of(book, graph) == set()
    built = pairs(world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys()).collect().schema)
    assert book.get("T3:p_steps", 2).columns == tuple(built) and "group" not in book.get("T3:p_steps", 2).names and book.get("T3:p_steps", 1).has("group")
    assert book.get("T3:p_steps", 0).columns == book.get("T2:C", len(graph.node("T2:C").steps)).columns
    plain = pairs(world.orch.materialize_tier3("tiny", "p_plain", world.anchors, keys=world.keys()).collect().schema)
    assert book.get("T3:p_plain", 0).columns == tuple(plain), "a plot without tier-3 steps reads its Tier 2 as it is"


def test_the_book_has_an_entry_for_every_node_and_k_and_the_order_of_the_places_is_the_openings():
    orch, loaded, graph, book = shipped(DEMO)
    assert all(book.has(nid, k) for nid, k in entries_of(graph)) and len(entries_of(graph)) == 164
    order = plan_composer.composition_order(loaded.raw, graph)
    named = [f"{ {'tier1': 'T1', 'tier2': 'T2', 'tier3': 'T3'}[kind] }:{ident}" for kind, ident, _ in plan_places(loaded.raw) if kind in ("tier1", "tier2", "tier3")]
    assert order[:len(named)] == named, "the places the opening builds come first, in the opening's order: one ordering"
    assert sorted(order) == sorted(graph.nodes()) and len(set(order)) == len(order), "every node once"


# ---------------------------------------------------------------------------------------------------------------------
# A failure is a value
# ---------------------------------------------------------------------------------------------------------------------

BAD_FILTER = {"action": "modif_filter", "column": "no_such_column", "op": "eq", "value": "x", "na": "remove"}


def planned(world_root, **kwargs):
    world = Tier3World(world_root, **kwargs)
    loaded = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml")
    graph = build_graph(loaded.raw)
    return world, loaded, graph, compose_plan_book(world.orch, "tiny", loaded, graph)


def test_a_tier3_step_that_cannot_be_planned_fails_that_place_and_the_ones_below_and_nothing_else(tmp_path):
    world, loaded, graph, book = planned(tmp_path, tier3=[KEEP_FROM_3, BAD_FILTER, DROP_GROUP])
    assert failures_of(book, graph) == {("T3:p_steps", 2), ("T3:p_steps", 3)}
    first = book.get("T3:p_steps", 2)
    assert "no_such_column" in first.sentence and "step 2" in first.sentence and (first.node, first.step) == ("T3:p_steps", 2)
    assert book.get("T3:p_steps", 3) is first, "the places below keep the engine's sentence and where it first failed"
    assert isinstance(book.get("T3:p_steps", 1), Plan) and isinstance(book.get("T3:p_plain", 0), Plan)
    with pytest.raises(Exception):
        world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys())     # the build fails there too: the plan says what the build says


def test_a_tier2_step_that_cannot_be_planned_fails_the_places_that_read_it_k_zero_too(tmp_path):
    world, loaded, graph, book = planned(tmp_path, tier2=[BAD_FILTER])
    bad = failures_of(book, graph)
    assert ("T2:C", 1) in bad and ("T2:C", 0) not in bad and not any(nid.startswith("T1:") for nid, _ in bad)
    below = {("T3:p_steps", k) for k in range(3)} | {("T3:p_plain", 0)}
    assert below <= bad, "a place that reads a failed table fails at every k, k = 0 included"
    assert {book.get(*key).sentence for key in bad} == {book.get("T2:C", 1).sentence} and "no_such_column" in book.get("T2:C", 1).sentence
    assert isinstance(book.get("T1:T", 0), Plan) and isinstance(book.get("T2:C", 0), Plan)


def test_a_join_step_that_cannot_be_planned_fails_the_join_and_what_reads_it(tmp_path):
    w = World(tmp_path)
    raw = copy.deepcopy(w.original_raw())
    raw["joins"]["J"]["tier1"]["steps"][0]["on"] = ["no_such_key"]
    loaded = loaded_from_resolved(load_data_analysis_recipe(w.recipes / "staged.yaml"), raw)
    loaded_plain = SimpleNamespace(raw=raw, is_audit_copy=False)
    graph = build_graph(raw)
    book = compose_plan_book(w.orch, "staged", loaded_plain, graph)
    bad = failures_of(book, graph)
    assert ("T1:J", 1) in bad and {("T2:J", k) for k in range(2)} <= bad and ("T3:pj", 0) in bad
    assert isinstance(book.get("T1:A", 0), Plan) and isinstance(book.get("T3:px", 0), Plan) and isinstance(book.get("T3:pa", 1), Plan), "tables that do not read the join are planned"
    assert "no_such_key" in book.get("T1:J", 1).sentence


def test_a_missing_data_file_fails_that_source_and_only_what_depends_on_it(tmp_path):
    w = World(tmp_path)
    (w.data / "B.tsv").unlink()
    loaded = load_data_analysis_recipe(w.recipes / "staged.yaml")
    graph = build_graph(loaded.raw)
    book = compose_plan_book(w.orch, "staged", loaded, graph)
    bad = failures_of(book, graph)
    assert ("DS:B", 0) in bad and ("T1:B", 0) in bad and ("T1:J", 0) in bad and ("T3:pj", 0) in bad
    assert not any(nid.endswith(":A") or nid.endswith(":X") or nid in ("T3:px", "T3:pa") for nid, _ in bad)
    assert "B" in book.get("DS:B", 0).sentence


def test_audit_steps_in_a_recipe_that_is_not_an_audit_copy_fail_every_place_with_the_engines_sentence(tmp_path):
    w = World(tmp_path)
    raw = copy.deepcopy(w.original_raw())
    raw["data_schemas"]["A"]["tier1"]["audit_steps"] = [{"action": "polars_drop", "columns": ["group"], "id": "audit_1a2b3c4d_1", "audit_comment": "x"}]
    loaded = SimpleNamespace(raw=raw, is_audit_copy=False)
    # the engine refuses it by `refuse_audit_steps_outside_an_audit(loaded, ...)`, which reads `loaded.raw` and `is_audit_copy`
    graph = build_graph(raw)
    book = compose_plan_book(w.orch, "staged", loaded, graph)
    assert failures_of(book, graph) == set(entries_of(graph)) and "audit" in book.get("T1:A", 0).sentence.lower()


def test_the_composer_never_raises_for_a_recipe_that_cannot_be_planned_and_an_undrawable_recipe_has_no_places(tmp_path):
    w = World(tmp_path)
    raw = copy.deepcopy(w.original_raw())
    raw["analysis_groups"]["g"]["plots"]["pj"]["target_dataset"] = "nowhere"
    with pytest.raises(Exception) as caught:
        compose_plan_book(w.orch, "staged", SimpleNamespace(raw=raw, is_audit_copy=False))
    assert type(caught.value).__name__ == "RecipeGraphError", "no graph, no places: the walk needs the graph too, and says so; not a failure value"


# ---------------------------------------------------------------------------------------------------------------------
# Nothing is built or stored; each source is read once
# ---------------------------------------------------------------------------------------------------------------------


def test_the_composer_stores_nothing_and_reads_each_source_once(tmp_path):
    w = World(tmp_path)
    loaded = load_data_analysis_recipe(w.recipes / "staged.yaml")
    real = DataOrchestrator.ingredient_parts
    with mock.patch("app.modules.orchestrator.write_anchor", side_effect=AssertionError("the plan stores nothing")), \
            mock.patch("app.modules.orchestrator.read_anchor_if_key", side_effect=AssertionError("the plan reads no stored table")), \
            mock.patch.object(DataOrchestrator, "ingredient_parts", autospec=True, side_effect=real) as read:
        compose_plan_book(w.orch, "staged", loaded)
    assert sorted(call.args[1] for call in read.call_args_list) == ["A", "B", "X"], "each source once"
    assert list(w.anchors.iterdir()) == []


# ---------------------------------------------------------------------------------------------------------------------
# An audit copy
# ---------------------------------------------------------------------------------------------------------------------


def test_the_plan_of_an_audit_copy_follows_its_audit_steps_and_the_originals_does_not_move(tmp_path):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    base = compose_plan_book(w.orch, "staged", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    add_step(audit, "T1:A", {"action": "polars_drop", "columns": ["group"]}, "not needed", plans=base)
    copy_loaded = loaded_from_resolved(original, audit.recipe, base)
    graph = build_graph(audit.recipe)
    audited = compose_plan_book(w.orch, "staged", copy_loaded, graph)
    n = len(graph.node("T1:A").steps)
    assert n == len(build_graph(original.raw).node("T1:A").steps) + 1
    assert base.get("T1:A", n - 1).has("group") and not audited.get("T1:A", n).has("group") and audited.get("T1:A", n - 1) == base.get("T1:A", n - 1)
    assert not audited.get("T1:J", len(graph.node("T1:J").steps)).has("group"), "the join that reads A has no `group` any more"
    assert base.get("T1:J", len(build_graph(original.raw).node("T1:J").steps)).has("group"), "the original's plan did not move"
    again = compose_plan_book(w.orch, "staged", original)
    assert all(again.get(*key) == base.get(*key) for key in entries_of(build_graph(original.raw)))


def test_a_filter_audit_step_changes_no_column_and_its_plan_is_the_one_before(tmp_path):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    base = compose_plan_book(w.orch, "staged", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    add_step(audit, "T1:A", {"action": "modif_filter", "column": "sample_id", "op": "eq", "value": "s1", "na": "remove"}, "one sample", plans=base)
    graph = build_graph(audit.recipe)
    book = compose_plan_book(w.orch, "staged", loaded_from_resolved(original, audit.recipe, base), graph)
    n = len(graph.node("T1:A").steps)
    assert n >= 1 and book.get("T1:A", n).columns == book.get("T1:A", n - 1).columns


# ---------------------------------------------------------------------------------------------------------------------
# The gate of a key drop gets the engine's plan: the five places
# ---------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("recipe_id, place, column", FIVE)
def test_the_five_places_are_refused_as_join_keys_with_the_engines_plan(recipe_id, place, column):
    orch, loaded, graph, book = shipped(recipe_id)
    with_plan = key_drop.DropGate(loaded.raw, book).facts(place, column)
    assert with_plan.refused and with_plan.needs and all(n.certain for n in with_plan.needs[:1])
    sentence = key_drop.key_drop_problem(loaded.raw, place, [column], book)
    assert sentence and f"the column {column!r} at {place}" in sentence and "it is read as a join key by" in sentence and "Cannot tell" not in sentence


@pytest.mark.parametrize("recipe_id, place, column", FIVE)
def test_the_five_places_without_the_plan_are_allowed_with_a_warning_that_says_the_app_could_not_follow(recipe_id, place, column):
    """The blind gate (names only) cannot follow the five: it does not claim they are keys, it does not refuse them (D-0449) and it says so in a warning, before the user confirms."""
    orch, loaded, graph, book = shipped(recipe_id)
    blind = key_drop.DropGate(loaded.raw).facts(place, column)
    assert not blind.refused and blind.uncertain
    assert key_drop.key_drop_problem(loaded.raw, place, [column]) is None
    sentence = key_drop.key_drop_warning(loaded.raw, place, [column])
    assert sentence and sentence.startswith(f"Warning: the app cannot follow the column {column!r} at {place} to the end.") and "may fail" in sentence
    assert key_drop.key_drop_warning(loaded.raw, place, [column], book) is None, "with the plan it is a refusal, not a warning"


def test_with_the_plan_the_gate_refuses_everything_the_blind_gate_refuses_and_what_stays_unsure_is_pinned_on_the_shipped_recipes():
    """With the engine's plan: every refusal of the names-only gate stays a refusal, more places are refused (the five and others), and the only places the gate still cannot follow
    are columns that flow into an `unpivot` the walk does not read yet (15 on the demo recipe, none on the other shipped ones). The figure is pinned: a step reading that lands (an unpivot
    is a step of its own, LBFB step 5) makes them certain and the pin must be moved with a note."""
    seen = {}
    for recipe_id in ("1_test_data_ST22_dummy", ABROMICS, "2_test_data_ST22_dummy", "1_Abromics_general_pipeline", "figshare_integration"):
        orch, loaded, graph, book = shipped(recipe_id)
        blind, real = key_drop.DropGate(loaded.raw), key_drop.DropGate(loaded.raw, book)
        counts = dict(pairs=0, refused_blind=0, refused_plan=0, unsure_blind=0, unsure_plan=0)
        for nid in graph.nodes():
            if graph.node(nid).kind == "DS":
                continue
            for name in book.get(nid, len(graph.node(nid).steps)).names:
                a, b = blind.facts(nid, name), real.facts(nid, name)
                counts["pairs"] += 1
                counts["refused_blind"] += a.refused
                counts["refused_plan"] += b.refused
                counts["unsure_blind"] += a.uncertain
                counts["unsure_plan"] += b.uncertain
                assert not a.refused or b.refused, (recipe_id, nid, name)
                if b.uncertain:
                    assert {(r.code, r.get("action")) for r in b.unfollowed} == {("step_not_read", "polars_unpivot")}, (recipe_id, nid, name, b.unfollowed)
        seen[recipe_id] = counts
    assert seen[DEMO] == dict(pairs=438, refused_blind=7, refused_plan=11, unsure_blind=122, unsure_plan=15)
    assert seen[ABROMICS] == dict(pairs=29, refused_blind=1, refused_plan=2, unsure_blind=16, unsure_plan=0)
    assert all(c["unsure_plan"] == 0 for k, c in seen.items() if k != DEMO)


def drop_step(column):
    return {"action": "polars_drop", "columns": [column]}


@pytest.mark.parametrize("recipe_id, place, column", FIVE[:2])
def test_add_step_refuses_the_five_with_the_plan_and_writes_them_without_it(recipe_id, place, column):
    orch, loaded, graph, book = shipped(recipe_id)
    audit = start_audit(loaded.raw, "1a2b3c4d")
    with pytest.raises(AuditCopyError, match="read as a join key"):
        add_step(audit, place, drop_step(column), "because", plans=book)
    assert audit.created == 0 and audit.recipe == loaded.raw, "a refused call changes nothing"
    assert add_step(audit, place, drop_step(column), "because") == "audit_1a2b3c4d_1" and audit.created == 1    # D-0449: allowed where the walk cannot see the key


def audit_recipe_with(loaded, place, column):
    trial = start_audit(loaded.raw, "1a2b3c4d")
    tier, name = audit_copy.parse_place(place)
    body = loaded.raw["data_schemas"][name] if name in loaded.raw["data_schemas"] else loaded.raw["joins"][name]
    holder = trial.recipe["data_schemas"][name] if name in loaded.raw["data_schemas"] else trial.recipe["joins"][name]
    holder[tier].setdefault("audit_steps", []).append({**drop_step(column), "id": "audit_1a2b3c4d_1", "audit_comment": "because"})
    return trial.recipe


def test_the_integrity_check_and_the_checkers_AU04_see_the_five_with_the_plan_and_refuse_them_without(tmp_path):
    orch, loaded, graph, book = shipped(DEMO)
    hand_made = audit_recipe_with(loaded, "T1:MLST", "sample_id")
    with_plan = integrity_errors(hand_made, loaded.raw, book)
    without = integrity_errors(hand_made, loaded.raw)
    assert len(with_plan) == 1 and "read as a join key" in with_plan[0] and without == [], "blind, the key is not seen (D-0449: allowed with a warning); the run composes the plan and refuses it"
    au04_plan = [p for p in check_recipe(hand_made, "audit", plans=book).problems if p.code == "AU04"]
    au04_blind = [p for p in check_recipe(hand_made, "audit").problems if p.code == "AU04"]
    assert len(au04_plan) == 1 and "read as a join key" in au04_plan[0].message and au04_blind == []


def test_the_engines_own_check_of_a_copy_carries_the_plan_and_refuses_the_five(tmp_path):
    orch, loaded, graph, book = shipped(DEMO)
    hand_made = audit_recipe_with(loaded, "T1:MLST", "sample_id")
    with_plan = loaded_from_resolved(loaded, hand_made, book)
    problems = with_plan.config.integrity_problems()
    assert len(problems) == 1 and "read as a join key" in problems[0]
    with pytest.raises(Exception, match="read as a join key"):
        orch.materialize_tier1(DEMO, "MLST", tmp_path / "MLST.parquet", loaded=with_plan)
    blind = loaded_from_resolved(loaded, hand_made)
    assert blind.config.integrity_problems() == [], "without the plan the engine's own check does not see the key (D-0449); the table of MLST itself builds, the join that reads it is what fails"
    assert "sample_id" not in orch.materialize_tier1(DEMO, "MLST", tmp_path / "MLST.parquet", loaded=blind).collect_schema().names()


def test_the_audit_run_composes_the_plan_of_the_original_and_refuses_the_five_before_building(tmp_path):
    orch = DataOrchestrator(RECIPES, RAW)
    loaded = load_data_analysis_recipe(RECIPES / f"{DEMO}.yaml")
    hand_made = audit_recipe_with(loaded, "T1:MLST", "sample_id")
    with pytest.raises(AuditRunError, match="read as a join key"):
        run_audit(orch, DEMO, hand_made, tmp_path / "original", tmp_path / "audit")
    assert not (tmp_path / "audit").exists() or not list((tmp_path / "audit").glob("*.parquet")), "nothing was built"


def test_the_audit_run_hands_the_plan_of_the_original_to_the_check_of_the_copy(tmp_path):
    w = World(tmp_path)
    w.build_all()
    seen = []
    from app.modules import audit_run
    real = audit_run.integrity_errors
    with mock.patch.object(audit_run, "integrity_errors", side_effect=lambda *a, **k: (seen.append(a), real(*a, **k))[1]):
        w.run(w.copy_with(("T1:A", {"action": "modif_filter", "column": "sample_id", "op": "eq", "value": "s1", "na": "remove"})))
    assert seen and isinstance(seen[0][2], PlanBook), "run_audit asks the check with the engine's plan of the original"


def test_the_session_restore_and_HOMEs_column_box_hand_the_rule_the_plan(monkeypatch):
    from app.modules.session_manager import split_key_drops
    given = []
    real = key_drop.DropGate.__init__

    def init(self, raw, plans=None):
        given.append(plans)
        real(self, raw, plans)
    monkeypatch.setattr(key_drop.DropGate, "__init__", init)
    orch, loaded, graph, book = shipped("3_test_no_joins")
    split_key_drops({"subtab_x": [{"node_type": "drop_column", "params": {"column": "sample_id"}, "id": "n1"}]}, loaded.raw, book)
    assert given == [book]


# ---------------------------------------------------------------------------------------------------------------------
# Candidate plans
# ---------------------------------------------------------------------------------------------------------------------


def test_a_candidate_plan_is_the_plan_of_the_recipe_with_one_more_step_and_changes_nothing_given(tmp_path):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    base = compose_plan_book(w.orch, "staged", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    before = copy.deepcopy((audit.recipe, audit.created))
    cand = compose_candidate_plan_book(w.orch, "staged", original, audit, "T1:A", drop_step("group"), base)
    assert (audit.recipe, audit.created) == before, "the audit copy given is not changed"
    n = len(build_graph(original.raw).node("T1:A").steps)
    assert cand.get("T1:A", n + 1).names == tuple(x for x in base.get("T1:A", n).names if x != "group")
    assert cand.get("T1:B", len(build_graph(original.raw).node("T1:B").steps)) == base.get("T1:B", len(build_graph(original.raw).node("T1:B").steps))


def test_a_drop_of_a_column_a_later_filter_needs_fails_in_its_candidate_plan_and_the_walk_says_the_build_fails(tmp_path):
    """J's tier 2 filters on `group`, which comes from A: dropping `group` at A's tier 1 breaks that filter. The readings do not see a filter's column (D-0351), the plan does."""
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    graph = build_graph(original.raw)
    base = compose_plan_book(w.orch, "staged", original, graph)
    audit = start_audit(original.raw, "1a2b3c4d")
    cand = compose_candidate_plan_book(w.orch, "staged", original, audit, "T1:A", drop_step("group"), base)
    assert isinstance(cand.get("T2:J", 1), PlanFailure) and "group" in cand.get("T2:J", 1).sentence and isinstance(cand.get("T1:J", 1), Plan)
    result = walk(graph, base, Start("T1:A", "group"), levels=("source", "T1", "T2", "T3"), kind="drop", candidates={"T1:A": cand})
    line = next(x for x in result.lines if x.place == "T1:A")
    assert line.consequences_checked
    broken = [c for c in line.consequences if c.code == BUILD_FAILS]
    assert broken and broken[0].place == "T2:J" and "group" in broken[0].get("sentence")
    unchecked = walk(graph, base, Start("T1:A", "group"), levels=("source", "T1", "T2", "T3"), kind="drop")
    assert not next(x for x in unchecked.lines if x.place == "T1:A").consequences_checked, "without candidate plans the walk says it did not check"


def test_a_candidate_for_a_drop_the_gate_refuses_is_not_made(tmp_path):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    base = compose_plan_book(w.orch, "staged", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    with pytest.raises(AuditCopyError, match="read as a join key"):
        compose_candidate_plan_book(w.orch, "staged", original, audit, "T1:A", drop_step("sample_id"), base)


# ---------------------------------------------------------------------------------------------------------------------
# HOME's `_recipe_plans`: composed once per recipe, files and data; None where nothing can be composed
# ---------------------------------------------------------------------------------------------------------------------


def home_plans_closure(**stand_ins):
    import ast
    from app.handlers import home_theater
    source = Path(home_theater.__file__)
    define = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == "_recipe_plans")
    ns = dict(vars(home_theater))
    ns.update(_plans_memo={}, **stand_ins)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "_recipe_plans", "exec"), ns)
    return ns["_recipe_plans"]


def test_HOMEs_plan_of_the_open_recipe_is_composed_once_per_recipe_files_and_data_and_never_raises(tmp_path):
    w = World(tmp_path)
    calls = []
    keys = SimpleNamespace(data_batch_hash="batch1")
    real = compose_plan_book

    def counting(orch, recipe_id, loaded, graph=None):
        calls.append(recipe_id)
        return real(orch, recipe_id, loaded, graph)
    state = {"keys": keys}
    recipe_plans = home_plans_closure(orchestrator=w.orch, _open_recipe_id=lambda: "staged", _data_analysis_recipe_keys=lambda: state["keys"], compose_plan_book=counting)
    first = recipe_plans()
    assert isinstance(first, PlanBook) and recipe_plans() is first and calls == ["staged"], "once"
    state["keys"] = SimpleNamespace(data_batch_hash="batch2")
    assert recipe_plans() is not first and calls == ["staged", "staged"], "other data, another composition"
    broken = home_plans_closure(orchestrator=w.orch, _open_recipe_id=lambda: (_ for _ in ()).throw(RuntimeError("No data analysis recipe is open")),
                                _data_analysis_recipe_keys=lambda: keys, compose_plan_book=counting)
    assert broken() is None, "no recipe open: no plan, never an exception in a handler"


# ---------------------------------------------------------------------------------------------------------------------
# A candidate that reuses the composition of the audit as it is: the same book, far fewer reads
# ---------------------------------------------------------------------------------------------------------------------


def same_book(a, b, graph):
    return all(a.get(*key) == b.get(*key) for key in entries_of(graph)) and all(a.has(*key) == b.has(*key) for key in entries_of(graph))


def candidate_graph(original, audit, place, step, plans):
    trial = audit_copy.AuditCopy(copy.deepcopy(audit.original), copy.deepcopy(audit.recipe), audit.audit_id, audit.created)
    add_step(trial, place, copy.deepcopy(step), "candidate", plans=plans)
    return build_graph(trial.recipe)


@pytest.mark.parametrize("place, column", [("T1:A", "group"), ("T1:B", "group_b"), ("T1:J", "group"), ("T2:J", "group_b"), ("T1:X", "group"), ("T3:pa", "sample_id"), ("T3:pj", "group")])
def test_a_candidate_that_reuses_the_composition_gives_the_book_of_a_full_recomposition(tmp_path, place, column):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    base = plan_composer.compose(w.orch, "staged", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    step = drop_step(column)
    fresh = compose_candidate_plan_book(w.orch, "staged", original, audit, place, step, base.book)
    cheap = compose_candidate_plan_book(w.orch, "staged", original, audit, place, step, base.book, base=base)
    assert same_book(cheap, fresh, candidate_graph(original, audit, place, step, base.book))


def test_the_reuse_reads_only_the_source_the_place_needs(tmp_path):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    base = plan_composer.compose(w.orch, "staged", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    real = DataOrchestrator.ingredient_parts

    def reads(place, column, **kwargs):
        with mock.patch.object(DataOrchestrator, "ingredient_parts", autospec=True, side_effect=real) as read:
            compose_candidate_plan_book(w.orch, "staged", original, audit, place, drop_step(column), base.book, **kwargs)
        return sorted(call.args[1] for call in read.call_args_list)
    assert reads("T2:J", "group_b", base=base) == [], "a tier 2: no source is read again"
    assert reads("T1:A", "group", base=base) == ["A"], "a tier 1 of a source: that source only"
    assert reads("T1:A", "group") == ["A", "B", "X"], "without the base everything is read again"


def test_a_base_that_differs_in_more_places_than_the_candidate_gives_less_reuse_and_never_a_wrong_plan(tmp_path):
    """The base is the composition of ANOTHER recipe (A drops `group` in its own tier 1): the places that are not the same by definition are planned again."""
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    other = copy.deepcopy(w.original_raw())
    other["data_schemas"]["A"]["tier1"]["steps"] = other["data_schemas"]["A"]["tier1"]["steps"] + [drop_step("group")]
    other_base = plan_composer.compose(w.orch, "staged", SimpleNamespace(raw=other, is_audit_copy=False))
    assert not other_base.book.get("T1:A", len(other_base.graph.node("T1:A").steps)).has("group")
    audit = start_audit(original.raw, "1a2b3c4d")
    own = plan_composer.compose(w.orch, "staged", original)
    fresh = compose_candidate_plan_book(w.orch, "staged", original, audit, "T1:B", drop_step("group_b"), own.book)
    cheap = compose_candidate_plan_book(w.orch, "staged", original, audit, "T1:B", drop_step("group_b"), own.book, base=other_base)
    assert same_book(cheap, fresh, candidate_graph(original, audit, "T1:B", drop_step("group_b"), own.book))
    assert cheap.get("T1:A", len(own.graph.node("T1:A").steps)).has("group"), "A was not taken from the base that does not hold the same A"
    assert cheap.get("T1:J", len(own.graph.node("T1:J").steps)).has("group"), "nor J, which reads A"


def test_a_recipe_wide_engine_that_differs_gives_no_reuse(tmp_path):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    base = plan_composer.compose(w.orch, "staged", original)
    changed = SimpleNamespace(raw={**original.raw, "data_engine": "no-such-engine"}, is_audit_copy=False)
    again = plan_composer.compose(w.orch, "staged", changed, reuse=base)
    assert failures_of(again.book, again.graph), "the engine of the recipe is read again, not taken from a base that had another one"


def test_a_base_whose_place_has_the_same_steps_but_another_definition_is_not_taken(tmp_path):
    """A's declaration of its source differs (`strip`), its steps do not: it is not the same place, so its source is read again (what shows is the read)."""
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    other = copy.deepcopy(w.original_raw())
    other["data_schemas"]["A"]["strip"] = not bool(other["data_schemas"]["A"].get("strip", False))
    other_base = plan_composer.compose(w.orch, "staged", SimpleNamespace(raw=other, is_audit_copy=False))
    own = plan_composer.compose(w.orch, "staged", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    real = DataOrchestrator.ingredient_parts
    with mock.patch.object(DataOrchestrator, "ingredient_parts", autospec=True, side_effect=real) as read:
        compose_candidate_plan_book(w.orch, "staged", original, audit, "T1:B", drop_step("group_b"), own.book, base=other_base)
    assert sorted(call.args[1] for call in read.call_args_list) == ["A", "B"], "B because the step is written there, A because the base holds another A"


def test_a_base_composed_for_another_recipe_id_is_not_reused(tmp_path):
    w = World(tmp_path)
    original = load_data_analysis_recipe(w.recipes / "staged.yaml")
    elsewhere = plan_composer.compose(w.orch, "another_id", original)
    audit = start_audit(original.raw, "1a2b3c4d")
    own = plan_composer.compose(w.orch, "staged", original)
    real = DataOrchestrator.ingredient_parts
    with mock.patch.object(DataOrchestrator, "ingredient_parts", autospec=True, side_effect=real) as read:
        compose_candidate_plan_book(w.orch, "staged", original, audit, "T2:J", drop_step("group_b"), own.book, base=elsewhere)
    assert sorted(call.args[1] for call in read.call_args_list) == ["A", "B", "X"], "the data of a recipe is located by its id: nothing is taken from another id"


def test_a_join_with_several_ingredients_and_no_step_has_no_plan_and_says_what_the_build_says(tmp_path):
    """The build refuses it ("No step list and no ingredients ..."): the place is a failure value, the tables that do not read the join keep their plans."""
    w = World(tmp_path)
    raw = copy.deepcopy(w.original_raw())
    raw["joins"]["J"]["tier1"]["steps"] = []
    graph = build_graph(raw)
    book = compose_plan_book(w.orch, "staged", SimpleNamespace(raw=raw, is_audit_copy=False), graph)
    assert isinstance(book.get("T1:J", 0), PlanFailure) and "No step list" in book.get("T1:J", 0).sentence
    assert isinstance(book.get("T3:pj", 0), PlanFailure) and isinstance(book.get("T2:J", 0), PlanFailure) and isinstance(book.get("T1:A", 0), Plan) and isinstance(book.get("T3:px", 0), Plan)


# ---- the plan for the gate: a bug of the composer is an error, never "cannot tell" ------------------------------------------------------------------------------------

def test_a_composer_bug_is_logged_notified_and_raised_never_none(caplog):
    import pytest
    from app.modules.plan_composer import BUG_NOTICE, PlanComposerBug, plan_book_for_the_gate
    told = []

    def compose():
        raise PlanComposerBug("no plan for T1:X after 2 step(s)")
    with caplog.at_level("ERROR"), pytest.raises(PlanComposerBug):
        plan_book_for_the_gate(compose, told.append)
    assert told == [BUG_NOTICE] and "error of the app, not of your recipe" in told[0]
    assert any("no plan for T1:X" in (r.exc_text or "") for r in caplog.records), "the cause is in the log"


def test_the_cases_that_stay_none_are_those_of_the_recipe_or_the_caller():
    from app.modules.plan_composer import plan_book_for_the_gate
    from utils.errors import RecipeLoadError
    from utils.recipe_graph import RecipeGraphError
    told = []
    for error in (RuntimeError("No data analysis recipe is open"), RecipeLoadError("cannot be read"), RecipeGraphError([]), OSError("file")):
        def compose(error=error):
            raise error
        assert plan_book_for_the_gate(compose, told.append) is None
    assert told == [], "no notice for the cases the rule reads from the recipe's names alone"
    assert plan_book_for_the_gate(lambda: "book", told.append) == "book"
