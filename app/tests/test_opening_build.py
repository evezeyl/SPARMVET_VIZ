"""The opening of a recipe builds and stores everything by key, draws every plot once, refuses a recipe that cannot be drawn (opening-build).

D-0326: at the opening every tier 1 table, every tier 2 table of a collection that has tier-2 steps, the tier 3 table of every plot with tier-3 steps
(D-0343) is built and stored by key; a later opening with equal keys builds nothing. D-0335: every plot is drawn once, from its table, as the proof that
it draws; nothing is stored of it. D-0336: a plot that receives very many rows gets a warning, nothing is refused (the number, 1,000,000, is decided by the owner on 2026-11-20 and kept in one
constant). D-0327: a recipe with a plot that cannot be drawn is refused with a plain reason, and a recipe whose plots all draw opens. D-0334: the
progress is counted from the plan.

What is proved (pure engine, `app/modules/opening_build.py`; the screen is in `test_opening_handler.py` and the browser tests):
- the plan: the order, the keys, no item for a tier a collection or plot does not have (T2 = T1, T3 = T2), one function;
- on EVERY shipped recipe: it opens (every table builds, every plot draws), every stored table equals the table the golden baseline recorded, and
  nothing is stored for a collection without tier-2 steps beyond its tier 1;
- a second opening with equal keys builds nothing and stores nothing; a changed tier-3 step rebuilds only that plot's table; a changed tier-2 step
  rebuilds Tier 2 and the Tier 3 of the plots that read it; a corrupt or missing stored file is rebuilt, not served;
- the fall-backs add no file: no tier 3 -> T3 = T2, no tier 2 -> T2 = T1;
- a plot that cannot be drawn refuses the recipe with a sentence that names the plot (and the column); the other plots still draw; a recipe whose plots
  all draw opens; a table that cannot be built is named once and its plots are not blamed again;
- the warning: above the number, not at it, never a refusal; a recipe with no plot and a recipe with no table are opened;
- the progress is called with counts that move from 0 to the totals;
- an exploration filter changes no stored table and no plot built at opening (the view applies it to a copy in memory).

Mutation index (each seen failing): MUTATION O1 `build_plan` leaves the tier-3 items out -> the tier-3 file test fails; MUTATION O2 `run_opening` does not
draw -> the refusal test fails; MUTATION O3 the warning uses `>=` -> the boundary test fails; MUTATION O4 a refused plot is not named -> the sentence test fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_opening_build.py -q
"""
import hashlib
import importlib.util
import json
from pathlib import Path
from unittest import mock

import matplotlib
matplotlib.use("Agg")
import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.engine_registry import PlotEngines
from app.modules.opening_build import (
    LARGE_PLOT_ROWS, PLOT, TIER1, TIER2, TIER3, build_plan, collections_of, draw_plot_proof, large_plot_warning, opening_signature,
    progress_text, run_opening)
from app.modules.orchestrator import DataOrchestrator
from app.tests.test_tier3_reader import DROP_GROUP, KEEP_FROM_2, KEEP_FROM_3, KEEP_UP_TO_4, Tier3World

ROOT = Path(__file__).resolve().parents[2]
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text(encoding="utf-8"))


def _golden():
    spec = importlib.util.spec_from_file_location("golden_baseline", ROOT / "assets" / "scripts" / "golden_baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gb = _golden()
ENGINES = PlotEngines()


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def no_draw(plot_id, table):
    return None


def open_world(world, **kwargs):
    raw = world.raw()
    keys = world.keys()
    return run_opening(world.orch, "tiny", raw, keys, world.anchors, draw=kwargs.pop("draw", no_draw), **kwargs)


def real_draw(world):
    return lambda plot_id, table: draw_plot_proof(ENGINES, world.raw(), plot_id, table)


def stores_during(action) -> list:
    from transformer import anchor
    written: list = []
    real = anchor.write_anchor

    def counting(lf, path, *args, **kwargs):
        written.append(Path(str(path)).name)
        return real(lf, path, *args, **kwargs)

    with mock.patch("app.modules.orchestrator.write_anchor", side_effect=counting):
        action()
    return sorted(written)


def stored(world) -> list:
    return sorted(p.name for p in world.anchors.iterdir() if p.suffix == ".parquet")


# ---------------------------------------------------------------------------------------------------------------------
# The plan: one function, the order, the keys, no item for a tier that is not there
# ---------------------------------------------------------------------------------------------------------------------


def test_the_plan_lists_tier1_then_tier2_then_tier3_then_every_plot_with_the_keys(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    keys = world.keys()
    plan = build_plan(world.raw(), keys)
    assert [(i.kind, i.ident) for i in plan] == [(TIER1, "C"), (TIER2, "C"), (TIER3, "p_steps"), (PLOT, "p_steps"), (PLOT, "p_plain")]
    by = {(i.kind, i.ident): i for i in plan}
    assert by[(TIER1, "C")].key == keys.tier1_key_of("C") and by[(TIER2, "C")].key == keys.tier2_key_of("C")
    assert by[(TIER3, "p_steps")].key == keys.plot_key_of("p_steps") == by[(PLOT, "p_steps")].key
    assert by[(PLOT, "p_plain")].key == keys.tier2_key_of("C"), "a plot without tier-3 steps reads its Tier 2 table: its key is that table's key"
    assert by[(TIER3, "p_steps")].target == "C" and all(i.is_table for i in plan if i.kind in (TIER1, TIER2, TIER3))


def test_no_tier2_and_no_tier3_means_no_item_for_them(tmp_path):
    world = Tier3World(tmp_path, tier2=[], tier3=None)
    assert [(i.kind, i.ident) for i in build_plan(world.raw(), world.keys())] == [(TIER1, "C"), (PLOT, "p_steps"), (PLOT, "p_plain")]


def test_a_recipe_with_no_plot_has_only_its_tables_and_a_recipe_with_nothing_has_an_empty_plan(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    raw = world.raw()
    raw["analysis_groups"] = {}
    assert [(i.kind, i.ident) for i in build_plan(raw, world.keys())] == [(TIER1, "C"), (TIER2, "C")]
    raw["joins"] = {}
    assert build_plan(raw, world.keys()) == []
    assert collections_of(raw) == []


def test_a_table_a_plot_reads_directly_is_a_collection_too(tmp_path):
    world = Tier3World(tmp_path)
    raw = world.raw()
    raw["analysis_groups"]["g"]["plots"]["p_plain"]["target_dataset"] = "T"
    assert collections_of(raw) == ["C", "T"]


def test_the_opening_signature_moves_with_the_recipe_and_with_the_data(tmp_path):
    world = Tier3World(tmp_path)
    before = opening_signature("tiny", world.keys())
    world.write_data("sample_id\tgroup\tscore\ns1\tA\t1\n")
    clear_data_analysis_recipe_cache()
    assert opening_signature("tiny", world.keys()) != before
    other = Tier3World(tmp_path / "other", tier3=[KEEP_UP_TO_4])
    assert opening_signature("tiny", other.keys())[1] != before[1]


# ---------------------------------------------------------------------------------------------------------------------
# What is built and stored, and that a second opening builds nothing
# ---------------------------------------------------------------------------------------------------------------------


def test_the_opening_stores_every_table_by_key_and_the_tier3_only_for_the_plot_that_has_steps(tmp_path):
    """MUTATION O1: without the tier-3 items the file of `p_steps` is not there."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    result = open_world(world)
    assert result.ok and result.warnings == []
    assert stored(world) == ["C.parquet", "C__T2.parquet", "C__T3_p_steps.parquet"]
    assert result.tables_done == 3


def test_a_second_opening_with_equal_keys_builds_nothing(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    open_world(world)
    drawn: list = []
    written = stores_during(lambda: open_world(world, draw=lambda plot_id, table: drawn.append(plot_id)))
    assert written == [], "every table is read from its stored file"
    assert drawn == ["p_steps", "p_plain"], "the engine draws what it is given: that a drawn recipe is not drawn again is `ProvenDrawings` (the handler)"


def test_the_fallbacks_add_no_file(tmp_path):
    """No recipe step for T3 then T3 = T2; none for T2 then T2 = T1: nothing extra is stored."""
    only_tier1 = Tier3World(tmp_path / "a", tier2=[], tier3=None)
    open_world(only_tier1)
    assert stored(only_tier1) == ["C.parquet"]
    tier2_only = Tier3World(tmp_path / "b", tier2=[KEEP_FROM_2], tier3=None)
    open_world(tier2_only)
    assert stored(tier2_only) == ["C.parquet", "C__T2.parquet"]


def test_a_changed_tier3_step_rebuilds_only_that_plots_table(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2], tier3=[KEEP_FROM_3])
    open_world(world)
    world.write(tier2=[KEEP_FROM_2], tier3=[KEEP_UP_TO_4])
    assert stores_during(lambda: open_world(world)) == ["C__T3_p_steps.parquet"]


def test_a_changed_tier2_step_rebuilds_tier2_and_the_tier3_that_reads_it_not_tier1(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2], tier3=[DROP_GROUP])
    open_world(world)
    world.write(tier2=[KEEP_FROM_3], tier3=[DROP_GROUP])
    assert stores_during(lambda: open_world(world)) == ["C__T2.parquet", "C__T3_p_steps.parquet"]


@pytest.mark.parametrize("damage", ["missing", "corrupt"])
@pytest.mark.parametrize("which, rebuilt", [
    ("C__T3_p_steps.parquet", ["C__T3_p_steps.parquet"]),
    ("C__T2.parquet", ["C__T2.parquet"]),
    ("C.parquet", ["C.parquet", "C__T2.parquet"]),   # a rebuilt Tier 1 removes the Tier 2 stored on top of it (`_materialize_tier1`); the Tier 3 key still matches
])
def test_a_missing_or_corrupt_stored_table_is_rebuilt_not_served(tmp_path, damage, which, rebuilt):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    open_world(world)
    before = {p.name: pl.read_parquet(p) for p in world.anchors.glob("*.parquet")}
    if damage == "missing":
        (world.anchors / which).unlink()
    else:
        (world.anchors / which).write_bytes(b"not a parquet file")
    assert stores_during(lambda: open_world(world)) == rebuilt
    assert {p.name for p in world.anchors.glob("*.parquet")} == set(before)
    assert all(pl.read_parquet(world.anchors / n).equals(frame) for n, frame in before.items()), "what was rebuilt is what was stored before"


def test_the_stored_tables_equal_what_the_old_way_gives(tmp_path):
    """The table of a plot with steps, read from its stored file, is the table `materialize_tier3` computes in memory for a recipe handed in."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    open_world(world)
    from app.modules.cache_keys import loaded_from_resolved
    original = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml")
    handed = loaded_from_resolved(original, original.raw)
    in_memory = world.orch.materialize_tier3("tiny", "p_steps", tmp_path / "other_anchors", keys=world.orch.compute_data_analysis_recipe_keys("tiny", loaded=handed),
                                             loaded=handed).collect()
    assert pl.read_parquet(world.anchors / "C__T3_p_steps.parquet").equals(in_memory)
    assert pl.read_parquet(world.anchors / "C__T2.parquet").equals(world.orch.materialize_tier2("tiny", "C", world.anchors / "C.parquet", keys=world.keys()).collect())


# ---------------------------------------------------------------------------------------------------------------------
# Every shipped recipe
# ---------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("recipe_id", sorted(BASELINE["recipes"]))
def test_every_shipped_recipe_opens_and_its_stored_tables_are_the_golden_tables(tmp_path, recipe_id):
    """The opening of a shipped recipe builds every table and draws every plot (the real plot engine); each stored file has the record the golden baseline
    holds for that table (rows, columns, content hash), and a collection with no tier-2 steps has no Tier 2 file."""
    recipes_dir, raw_data = ROOT / BASELINE["recipes_dir"], ROOT / BASELINE["raw_data"]
    orchestrator = DataOrchestrator(recipes_dir, raw_data)
    raw = load_data_analysis_recipe(recipes_dir / f"{recipe_id}.yaml").raw
    keys = orchestrator.compute_data_analysis_recipe_keys(recipe_id)
    anchors = tmp_path / "anchors"
    result = run_opening(orchestrator, recipe_id, raw, keys, anchors, draw=lambda plot_id, table: draw_plot_proof(ENGINES, raw, plot_id, table))
    assert result.problems == [], result.problems
    expected = BASELINE["recipes"][recipe_id]
    plan = build_plan(raw, keys)
    for collection in collections_of(raw):
        assert gb.table_record(pl.read_parquet(anchors / f"{collection}.parquet")) == expected["t1"][collection], f"{recipe_id} {collection} tier 1"
        has_tier2 = any(i.kind == TIER2 and i.ident == collection for i in plan)
        assert (anchors / f"{collection}__T2.parquet").exists() == has_tier2
        if has_tier2:
            assert gb.table_record(pl.read_parquet(anchors / f"{collection}__T2.parquet")) == expected["t2"][collection], f"{recipe_id} {collection} tier 2"
        else:
            assert expected["t2"][collection] == expected["t1"][collection], "T2 = T1 in the baseline too"
    # a tier 3 file exists for a plot that writes tier-3 steps and for no other, and holds the golden table of that plot (a plot without them adds no file, D-0343)
    wanted = {f"{plot['target_dataset']}__T3_{pid}.parquet": pid for g in (raw.get("analysis_groups") or {}).values() for pid, plot in (g.get("plots") or {}).items() if plot.get("tier3", {}).get("steps")}
    assert {p.name for p in anchors.glob("*__T3_*")} == set(wanted)
    for name, pid in wanted.items():
        assert gb.table_record(pl.read_parquet(anchors / name)) == expected["plots"][pid], f"{recipe_id} plot {pid} tier 3"
    # the second opening of the same recipe builds nothing
    assert stores_during(lambda: run_opening(orchestrator, recipe_id, raw, keys, anchors, draw=no_draw)) == []


# ---------------------------------------------------------------------------------------------------------------------
# A plot that cannot be drawn refuses the recipe; a recipe whose plots all draw opens
# ---------------------------------------------------------------------------------------------------------------------


def break_plot(world, plot_id="p_plain", column="no_such_column"):
    path = world.data_analysis_recipes_dir / "tiny.yaml"
    text = path.read_text()
    marker = f"      {plot_id}:\n"
    head, tail = text.split(marker)
    tail = tail.replace("mapping: {x: group}", f"mapping: {{x: {column}}}", 1).replace("mapping: {x: sample_id}", f"mapping: {{x: {column}}}", 1)
    path.write_text(head + marker + tail)
    clear_data_analysis_recipe_cache()


def test_a_recipe_whose_plots_all_draw_opens(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    result = open_world(world, draw=real_draw(world))
    assert result.ok and result.problems == []


def test_a_plot_that_cannot_be_drawn_refuses_the_recipe_with_a_sentence_that_names_it(tmp_path):
    """MUTATION O2 (the engine does not draw) and MUTATION O4 (the plot is not named): both make this fail."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    break_plot(world, "p_plain")
    drawn: list = []

    def draw(plot_id, table):
        drawn.append(plot_id)
        real_draw(world)(plot_id, table)

    result = open_world(world, draw=draw)
    assert not result.ok and len(result.problems) == 1
    sentence = result.problems[0]
    assert "'p_plain'" in sentence and "no_such_column" in sentence and "Resolved plan" not in sentence, sentence
    assert drawn == ["p_steps", "p_plain"], "the plot that draws is drawn; the broken one is tried and named, nothing stops the others"
    assert "p_steps" not in sentence


def test_an_error_that_does_not_name_the_plot_gets_the_plot_in_front_of_it(tmp_path):
    """MUTATION O4: without the plot in front, a bare error of the engine would refuse the recipe without saying which plot."""
    world = Tier3World(tmp_path)

    def draw(plot_id, table):
        if plot_id == "p_plain":
            raise RuntimeError("the engine says boom")

    result = open_world(world, draw=draw)
    assert result.problems == ["The plot 'p_plain' cannot be drawn: the engine says boom"]


def test_two_broken_plots_are_both_named(tmp_path):
    world = Tier3World(tmp_path)
    break_plot(world, "p_plain")
    break_plot(world, "p_steps")
    result = open_world(world, draw=real_draw(world))
    assert len(result.problems) == 2
    assert any("'p_plain'" in p for p in result.problems) and any("'p_steps'" in p for p in result.problems)


def test_a_table_that_cannot_be_built_is_named_once_and_its_plots_are_not_blamed_again(tmp_path):
    world = Tier3World(tmp_path, tier2=[{"action": "polars_drop", "columns": ["no_such_column"]}])
    result = open_world(world, draw=real_draw(world))
    assert len(result.problems) == 1, result.problems
    assert "tier 2 of the table 'C'" in result.problems[0] and "step 1 ('polars_drop')" in result.problems[0]
    assert "C__T2.parquet" not in stored(world)


def test_a_tier3_step_that_cannot_be_applied_is_named_by_the_plot_and_the_step(tmp_path):
    world = Tier3World(tmp_path, tier3=[KEEP_FROM_3, {"action": "polars_drop", "columns": ["nope"]}])
    result = open_world(world, draw=real_draw(world))
    assert len(result.problems) == 1 and "'p_steps'" in result.problems[0] and "step 2" in result.problems[0], result.problems


def test_a_failure_outside_the_exceptions_class_is_not_swallowed(tmp_path):
    world = Tier3World(tmp_path)

    def interrupted(plot_id, table):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        open_world(world, draw=interrupted)


# ---------------------------------------------------------------------------------------------------------------------
# The large-data warning, the progress, the exploration filter
# ---------------------------------------------------------------------------------------------------------------------


def test_the_constant_is_one_place_and_the_warning_says_plot_rows_and_what_to_do():
    assert LARGE_PLOT_ROWS == 1_000_000
    text = large_plot_warning("p", 1_234_567, LARGE_PLOT_ROWS)
    assert "'p'" in text and "1,234,567" in text and "1,000,000" in text and "nothing is refused" in text and "Suggestion" in text


def test_the_warning_is_above_the_number_not_at_it_and_nothing_is_refused(tmp_path):
    """MUTATION O3: `>=` instead of `>` warns at the number."""
    world = Tier3World(tmp_path, tier2=[], tier3=None)     # both plots read the 5 rows of C
    below = open_world(world, large_rows=5)
    assert below.warnings == [] and below.ok
    above = open_world(world, large_rows=4, draw=real_draw(world))
    assert above.ok, "nothing is refused"
    assert len(above.warnings) == 2 and "'p_steps'" in above.warnings[0] and "5 rows" in above.warnings[0]


def test_the_plot_is_drawn_even_when_it_gets_the_warning(tmp_path):
    world = Tier3World(tmp_path)
    drawn: list = []
    result = open_world(world, large_rows=1, draw=lambda plot_id, table: drawn.append(plot_id))
    assert result.warnings and drawn == ["p_steps", "p_plain"]


def test_the_progress_moves_from_zero_to_the_totals_in_plan_order(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    seen: list = []
    open_world(world, progress=lambda *counts: seen.append(counts))
    assert seen[0] == (0, 3, 0, 2) and seen[-1] == (3, 3, 2, 2)
    assert len(seen) == 1 + 5, "one call per item of the plan, after the item"
    assert all(a <= b for a, b in zip(seen, seen[1:])), "the counts only go up"
    assert [c[0] for c in seen] == [0, 1, 2, 3, 3, 3] and [c[2] for c in seen] == [0, 0, 0, 0, 1, 2]
    assert progress_text("tiny", 12, 24, 5, 17) == "Opening 'tiny': tables 12 of 24, plots 5 of 17"


def test_a_failed_item_still_moves_the_progress_to_its_end(tmp_path):
    world = Tier3World(tmp_path, tier2=[{"action": "polars_drop", "columns": ["nope"]}])
    seen: list = []
    open_world(world, progress=lambda *counts: seen.append(counts))
    assert seen[-1] == (3, 3, 2, 2)


def test_an_exploration_filter_changes_no_stored_table_and_no_plot_built_at_opening(tmp_path):
    """D-0327: exploration filters are never applied to stored tables or to the plots built at opening. The view applies a filter to a copy in memory."""
    from app.modules.t3_audit_engine import _apply_filter_rows
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    open_world(world)
    digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in world.anchors.glob("*.parquet")}
    table = world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys())
    shown = _apply_filter_rows(table, [{"column": "sample_id", "op": "eq", "value": "s3", "dtype": "String"}]).collect()
    assert shown.height == 1 and table.collect().height > 1, "the view changed, the table did not"
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in world.anchors.glob("*.parquet")} == digests
    assert stores_during(lambda: open_world(world)) == [], "nothing to rebuild: the filter touched no stored table"
    assert world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys()).collect().height == table.collect().height


# ---------------------------------------------------------------------------------------------------------------------
# A build reads only the sources it needs (the control found no test that could fail on this)
# ---------------------------------------------------------------------------------------------------------------------


def _with_an_unused_source(world):
    """The recipe of `world` plus a second data schema `U` (its own file) that no join and no plot reads."""
    (world.data_dir / "U.tsv").write_text("k\nx\ny\n")
    path = world.data_analysis_recipes_dir / "tiny.yaml"
    text = path.read_text()
    unused = (f"  U:\n    source: {{type: local_tsv, path: {world.data_dir / 'U.tsv'}}}\n    null_values: []\n    strip: false\n"
              "    input_fields:\n      k: {original_name: k, type: String, ui_label: K}\n    tier1: {steps: []}\n")
    assert "joins:\n" in text
    path.write_text(text.replace("joins:\n", unused + "joins:\n", 1))
    clear_data_analysis_recipe_cache()


def _sources_read_during(world, action) -> list:
    """The ids of the source tables the orchestrator reads while `action` runs, in order."""
    read: list = []
    real = DataOrchestrator.prepare_ingredient

    def counting(self, ds_id, *args, **kwargs):
        read.append(ds_id)
        return real(self, ds_id, *args, **kwargs)

    with mock.patch.object(DataOrchestrator, "prepare_ingredient", counting):
        action()
    return read


def test_the_opening_reads_only_the_source_tables_the_recipe_uses_once_per_table_it_builds(tmp_path):
    """MUTATION S1: a build that reads every source table of the recipe (as the code did before) reads `U` too, once per table built; this fails."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    _with_an_unused_source(world)
    read = _sources_read_during(world, lambda: open_world(world))
    assert read == ["T"], f"the opening built the tables of C once and read only its source T; it read {read}"


def test_a_table_that_is_a_source_reads_that_source_and_only_that_one(tmp_path):
    """The positive control of the test above: a source that is needed is read (a build that reads nothing would fail here), and the other is not."""
    world = Tier3World(tmp_path)
    _with_an_unused_source(world)
    read = _sources_read_during(world, lambda: world.orch.materialize_tier1("tiny", "U", world.anchors / "U.parquet", keys=world.keys()))
    assert read == ["U"]


def test_a_second_opening_reads_no_source_table_at_all(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    _with_an_unused_source(world)
    open_world(world)
    assert _sources_read_during(world, lambda: open_world(world)) == [], "every table is read from its stored file"


# ---------------------------------------------------------------------------------------------------------------------
# A plot taken out of the recipe leaves no stored table behind (rules_verification_testing.md section 9)
# ---------------------------------------------------------------------------------------------------------------------


def _rename_plot(world, old, new):
    path = world.data_analysis_recipes_dir / "tiny.yaml"
    path.write_text(path.read_text().replace(f"      {old}:\n", f"      {new}:\n"))
    clear_data_analysis_recipe_cache()


def test_the_stored_table_of_a_plot_that_is_not_in_the_recipe_any_more_is_removed_at_the_opening(tmp_path):
    """MUTATION P1: without the sweep the file of the plot that is gone stays for ever (nothing reads it, nothing removes it)."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    open_world(world)
    assert "C__T3_p_steps.parquet" in stored(world)
    _rename_plot(world, "p_steps", "p_renamed")
    result = open_world(world)
    assert result.ok and result.swept == ["C__T3_p_steps.parquet"]
    assert stored(world) == ["C.parquet", "C__T2.parquet", "C__T3_p_renamed.parquet"], "the old file is gone, the file of the plot that is in the recipe is stored"


def test_the_sweep_leaves_the_files_it_must_leave(tmp_path):
    """A second opening removes nothing; a file of a table this recipe does not name (another recipe of the deployment) and a table whose own name holds the
    mark are not orphans; the files of the plots of the plan stay."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    open_world(world)
    stranger = world.anchors / "OtherRecipeTable__T3_q.parquet"
    stranger.write_bytes(b"belongs to another recipe")
    assert open_world(world).swept == [] and stranger.exists()
    assert "C__T3_p_steps.parquet" in stored(world)


def test_orphan_tier3_files_never_names_a_planned_table(tmp_path):
    from app.modules.opening_build import BuildItem, orphan_tier3_files
    folder = tmp_path
    for name in ("A__T3_p.parquet", "A__T3_gone.parquet", "A__T2.parquet", "A.parquet", "B__T3_x.parquet"):
        (folder / name).write_bytes(b"x")
    plan = [BuildItem(TIER1, "A", "k"), BuildItem(TIER1, "A__T3_p", "k"), BuildItem(TIER3, "p2", "k", "A"), BuildItem(PLOT, "p2", "k", "A")]
    found = sorted(path.name for path in orphan_tier3_files(folder, plan, ["A"]))
    assert found == ["A__T3_gone.parquet"], "A__T3_p.parquet is the Tier 1 table of a table named A__T3_p; B is not a table of this recipe"


# ---------------------------------------------------------------------------------------------------------------------
# The check before a Tier 3 table is stored reads only the data files its table reads
# ---------------------------------------------------------------------------------------------------------------------


def _files_hashed_during(action) -> list:
    """The file names `dataset_file_hashes` reads while `action` runs, one list per call."""
    import app.modules.orchestrator as orchestrator_module
    calls: list = []
    real = orchestrator_module.dataset_file_hashes

    def counting(files):
        calls.append(sorted(Path(p).name for p in files.values()))
        return real(files)

    with mock.patch.object(orchestrator_module, "dataset_file_hashes", counting):
        action()
    return calls


def test_the_check_before_a_tier3_store_reads_only_the_files_of_the_table_the_plot_reads(tmp_path):
    """MUTATION H1: the check hashing every file of the recipe (as `compute_data_analysis_recipe_keys` does) also reads `U.tsv` here. The checks of the tier 1
    and tier 2 tables still read every file (not changed: reported as a proposal)."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    _with_an_unused_source(world)
    keys = world.keys()
    calls = _files_hashed_during(lambda: world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=keys))
    assert len(calls) >= 2 and all(names == ["T.tsv", "U.tsv"] for names in calls[:-1]), f"the checks of the tier 1 and tier 2 tables read every file: {calls}"
    assert calls[-1] == ["T.tsv"], f"the tier 3 check read a file its table does not read: {calls[-1]}"
    assert (world.anchors / "C__T3_p_steps.parquet").exists()


def test_a_file_that_changes_after_the_narrowed_check_read_it_gives_another_key_at_the_next_opening(tmp_path):
    """The narrowed check still reads the file the table reads (the change DURING a build is told: `test_tier3_store.py`, the table built while its inputs changed)."""
    import app.modules.orchestrator as orchestrator_module
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    _with_an_unused_source(world)
    real = orchestrator_module.dataset_file_hashes

    def hashes_then_change(files):
        found = real(files)
        if set(files) == {"T"}:   # the check of the tier 3 table (the narrowed one): the data changes right after it read the file
            world.write_data("sample_id\tgroup\tscore\ns1\tA\t9\n")
        return found

    told: list = []
    keys = world.keys()
    with mock.patch.object(orchestrator_module, "dataset_file_hashes", hashes_then_change):
        # the check reads the file as it is before the change, so it sees nothing: the table IS stored under the key of the data it was built from, and the
        # next opening (the data is another now) has another key and builds again
        world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=keys, on_inputs_changed=told.append)
    assert told == [] and (world.anchors / "C__T3_p_steps.parquet").exists()
    clear_data_analysis_recipe_cache()
    assert world.orch.compute_data_analysis_recipe_keys("tiny").plot_key_of("p_steps") != keys.plot_key_of("p_steps"), "the key of the next opening is not the stored one"
    assert stores_during(lambda: world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys())) == ["C.parquet", "C__T2.parquet", "C__T3_p_steps.parquet"]
