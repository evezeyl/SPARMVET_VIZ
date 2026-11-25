"""A key per stored table: a series of labelled parts (ADR-101, piece A3 of the HOME audit redesign).

The properties, tested before and independently of the code that makes the keys (property tests first, ADR-101):
  - the key of a table is `E-<32> . rC-<32> . dC-<32>`; the key of its tier 2 adds `s2-<32>`; no tier-2 steps, no `s2` part;
  - the same inputs give the same key; ANY input of a table changes its key: a value written in its own definition or in the
    definition of anything upstream of it, the content of a data file it reads, its engine, the cache version;
  - a change in a table that this table does not depend on changes nothing of this key (two unrelated tables; a join and an
    unrelated table); a change downstream (plots) or in a tier 2 moves no tier-1 key;
  - fail-safe (ADR-101 point 3): where the graph cannot say what a table depends on, the key is COARSE (the whole recipe, every file),
    never narrower than the truth;
  - end to end through `DataOrchestrator`: one source file changes and only the tables that read it are rebuilt, the others are
    served from their stored file; a stale file is removed when the mismatch is found;
  - the export key check compares the keys of the tables in scope.

Mutation index (each is a change of the code that one named test must see fail; grep "MUTATION"):
  M1  the `dC` part reads no file (every table's data part is the same)            -> test_a_changed_input_changes_the_key_of_every_table_that_depends_on_it_and_no_other
                                                                                      test_a_data_file_moves_the_key_of_the_tables_that_read_it_and_no_other
                                                                                      test_one_changed_source_file_rebuilds_only_the_tables_that_read_it
  M2  the `rC` part holds only the table's own body (not the upstream ones)         -> test_a_changed_input_changes_the_key_of_every_table_that_depends_on_it_and_no_other
  M3  the `rC` part holds the whole recipe (a coarse part where a narrow one is due)-> test_a_change_in_one_table_does_not_move_the_key_of_a_table_that_does_not_read_it
  M4  a coarse fallback that is too narrow (uses the table's own body)              -> test_a_recipe_the_graph_cannot_draw_gives_coarse_keys_that_move_with_any_change

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_table_keys.py -q
"""
import copy
import glob
import re
from pathlib import Path
from unittest import mock

import polars as pl
import pytest
import yaml

from app.handlers.export_handlers import blocked_export_notice, changed_since_view
from app.modules import cache_keys
from app.modules.cache_keys import (
    DataAnalysisRecipeKeys, TableKeyParts, batch_hash_of, canonical_hash, clear_data_analysis_recipe_cache, collection_tier2_key,
    data_analysis_recipe_keys, dataset_file_hashes, load_data_analysis_recipe, table_definition_for_key, table_key_parts, tier1_key,
    tier2_key,
)
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, DataOrchestrator, tier2_path_for
from app.modules.session_manager import SessionManager
from utils.config_loader import ConfigManager
from utils.id_completion import plan_material
from utils.recipe_graph import build_graph
from utils.recipe_tiers import collection_bodies

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = sorted(
    glob.glob(str(ROOT / "config" / "data_analysis_recipes" / "*" / "*.yaml"))
    + glob.glob(str(ROOT / "assets" / "gallery_data" / "*" / "data_analysis_recipe.yaml"))
    + glob.glob(str(ROOT / "app" / "tests" / "equality" / "recipes" / "*.yaml")))

T1_FORM = re.compile(r"^E-[0-9a-f]{32}\.rC-[0-9a-f]{32}\.dC-[0-9a-f]{32}$")
T2_FORM = re.compile(r"^E-[0-9a-f]{32}\.rC-[0-9a-f]{32}\.dC-[0-9a-f]{32}\.s2-[0-9a-f]{32}$")

FILTER_A = {"action": "modif_filter", "column": "group", "op": "eq", "value": "A", "na": "remove"}
FILTER_B = {"action": "modif_filter", "column": "group", "op": "eq", "value": "B", "na": "remove"}


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def field(label="Group"):
    return {"original_name": "group", "type": "Categorical", "ui_label": label}


def schema(*, steps=(), tier2=()):
    """A table of the shared recipe: it declares no entity id, so it takes part in no completion of the ids (that coupling of the keys is tested in test_id_completion.py)."""
    return {"source": {"type": "local_tsv", "path": "/nowhere.tsv"}, "null_values": [], "strip": False,
            "input_fields": {"sample_id": {"original_name": "sample_id", "type": "Categorical", "ui_label": "Sample"},
                             "group": field()},
            "tier1": {"steps": list(steps)}, "tier2": {"steps": list(tier2)}}


def join(*ingredients, steps=(), tier2=()):
    return {"ingredients": [{"dataset_id": i} for i in ingredients], "tier1": {"steps": list(steps)}, "tier2": {"steps": list(tier2)}}


def recipe() -> dict:
    """Tables A and B, a join J of them (with a tier 2), a table X that reads nothing of A and B and is plotted directly (with a
    tier 2), and a plot on each."""
    return {
        "id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine", "info": {"ui_label": "R"},
        "data_schemas": {"A": schema(), "B": schema(), "X": schema(tier2=[FILTER_A])},
        "joins": {"J": join("A", "B", tier2=[FILTER_A])},
        "analysis_groups": {"g": {"ui_label": "G", "plots": {
            "pj": {"target_dataset": "J", "mapping": {"x": "group"}, "layers": [{"name": "geom_bar", "params": {}}]},
            "px": {"target_dataset": "X", "mapping": {"x": "group"}, "layers": [{"name": "geom_bar", "params": {}}]}}}},
    }


FILES = {"A": "a1", "B": "b1", "X": "x1"}


def t1_keys(raw: dict, files=None) -> dict:
    parts, _ = table_key_parts(raw)
    files = FILES if files is None else files
    return {table: tier1_key(p, files) for table, p in parts.items()}


def moved(before: dict, after: dict) -> set:
    return {name for name in before if before[name] != after[name]}


# =====================================================================================================================
# The form of a key
# =====================================================================================================================


def test_a_tier1_key_is_three_labelled_parts_of_128_bits_joined_with_dots():
    for key in t1_keys(recipe()).values():
        assert T1_FORM.match(key), key


def test_a_tier2_key_is_the_tier1_key_it_is_computed_from_and_one_more_part():
    raw = recipe()
    t1 = t1_keys(raw)["J"]
    t2 = collection_tier2_key(raw, "J", t1)
    assert T2_FORM.match(t2) and t2.startswith(t1 + ".s2-")


def test_an_empty_tier2_list_adds_no_part_so_the_key_is_the_tier1_key():
    """The empty part is left out (ADR-101 point 2): T2 equals T1, nothing is stored, and the key of T2 IS the key of T1."""
    raw = recipe()
    raw["joins"]["J"]["tier2"] = {"steps": []}
    t1 = t1_keys(raw)["J"]
    assert collection_tier2_key(raw, "J", t1) == t1
    del raw["joins"]["J"]["tier2"]
    assert collection_tier2_key(raw, "J", t1) == t1


def test_the_same_inputs_give_the_same_keys_twice():
    assert t1_keys(recipe()) == t1_keys(copy.deepcopy(recipe()))


def test_the_order_of_the_keys_written_in_the_recipe_does_not_matter_but_the_order_of_the_steps_does():
    raw = recipe()
    shuffled = dict(reversed(list(raw.items())))
    assert t1_keys(raw) == t1_keys(shuffled)
    one, other = copy.deepcopy(raw), copy.deepcopy(raw)
    one["data_schemas"]["A"]["tier1"]["steps"] = [FILTER_A, FILTER_B]
    other["data_schemas"]["A"]["tier1"]["steps"] = [FILTER_B, FILTER_A]
    assert t1_keys(one)["A"] != t1_keys(other)["A"]
    assert t1_keys(one)["J"] != t1_keys(other)["J"]


def test_a_tier2_step_order_moves_the_tier2_key_and_no_tier1_key():
    one, other = recipe(), recipe()
    one["joins"]["J"]["tier2"]["steps"] = [FILTER_A, FILTER_B]
    other["joins"]["J"]["tier2"]["steps"] = [FILTER_B, FILTER_A]
    assert t1_keys(one) == t1_keys(other)
    assert collection_tier2_key(one, "J", t1_keys(one)["J"]) != collection_tier2_key(other, "J", t1_keys(other)["J"])


# =====================================================================================================================
# A change in one table moves the tables that depend on it, and no other
# =====================================================================================================================


def test_a_change_in_one_table_does_not_move_the_key_of_a_table_that_does_not_read_it():
    """MUTATION M3 (rC is the whole recipe): the keys of A and X would move with a change in B."""
    before = recipe()
    after = copy.deepcopy(before)
    after["data_schemas"]["B"]["tier1"]["steps"] = [FILTER_B]
    assert moved(t1_keys(before), t1_keys(after)) == {"B", "J"}       # B, and J that reads B; not A, not X


def test_a_change_in_a_join_moves_the_join_and_no_table_it_reads():
    before = recipe()
    after = copy.deepcopy(before)
    after["joins"]["J"]["tier1"]["steps"] = [FILTER_B]
    assert moved(t1_keys(before), t1_keys(after)) == {"J"}


def test_a_change_in_the_ingredients_of_a_join_moves_the_join_only():
    before = recipe()
    after = copy.deepcopy(before)
    after["joins"]["J"]["ingredients"] = [{"dataset_id": "B"}, {"dataset_id": "A"}]       # the base table is the first one
    assert moved(t1_keys(before), t1_keys(after)) == {"J"}


def test_a_join_of_a_join_depends_on_everything_upstream_of_it():
    """The graph draws a join that reads a join; the key of the outer join holds the definition of both and the files of all."""
    raw = recipe()
    raw["joins"]["K"] = join("J", "X")
    before = t1_keys(raw)
    deeper = copy.deepcopy(raw)
    deeper["data_schemas"]["A"]["tier1"]["steps"] = [FILTER_A]
    assert moved(before, t1_keys(deeper)) == {"A", "J", "K"}
    assert moved(before, t1_keys(raw, {**FILES, "B": "b2"})) == {"B", "J", "K"}


def test_a_tier2_change_moves_no_tier1_key_and_a_plot_change_moves_no_key():
    """A tier-2 list and the plots are downstream of every tier-1 table (ADR-089 point 3, ADR-101)."""
    before = recipe()
    tier2_changed = copy.deepcopy(before)
    tier2_changed["data_schemas"]["X"]["tier2"]["steps"] = [FILTER_B]
    tier2_changed["joins"]["J"]["tier2"]["steps"] = [FILTER_B]
    assert t1_keys(before) == t1_keys(tier2_changed)
    plot_changed = copy.deepcopy(before)
    plot_changed["analysis_groups"]["g"]["plots"]["pj"]["mapping"] = {"x": "sample_id"}
    plot_changed["plot_defaults"] = {"theme": "theme_bw"}
    plot_changed["info"] = {"ui_label": "another"}
    plot_changed["plot_engine"] = "engine-x"
    assert t1_keys(before) == t1_keys(plot_changed)


def test_the_tier2_key_moves_with_its_steps_with_its_engine_and_with_the_tier1_it_reads():
    raw = recipe()
    base = collection_tier2_key(raw, "J", t1_keys(raw)["J"])
    steps = copy.deepcopy(raw)
    steps["joins"]["J"]["tier2"]["steps"] = [FILTER_B]
    engine = copy.deepcopy(raw)
    engine["joins"]["J"]["tier2"]["data_engine"] = "engine-x"
    assert collection_tier2_key(steps, "J", t1_keys(steps)["J"]) != base
    assert collection_tier2_key(engine, "J", t1_keys(engine)["J"]) != base
    assert collection_tier2_key(raw, "J", t1_keys(raw, {**FILES, "A": "a2"})["J"]) != base


def test_a_data_file_moves_the_key_of_the_tables_that_read_it_and_no_other():
    """MUTATION M1: with no file in the `dC` part nothing here moves."""
    raw = recipe()
    assert moved(t1_keys(raw), t1_keys(raw, {**FILES, "A": "a2"})) == {"A", "J"}
    assert moved(t1_keys(raw), t1_keys(raw, {**FILES, "X": "x2"})) == {"X"}


def test_a_source_table_with_no_file_is_part_of_the_key_and_the_key_moves_when_the_file_appears():
    raw = recipe()
    without = {"A": "a1", "X": "x1"}
    assert moved(t1_keys(raw, without), t1_keys(raw)) == {"B", "J"}


def test_the_engine_and_cache_version_move_every_table_key(monkeypatch):
    raw = recipe()
    before = t1_keys(raw)
    monkeypatch.setattr(cache_keys, "ENGINE_CACHE_VERSION", "999")
    assert moved(before, t1_keys(raw)) == set(before)


def test_a_table_key_moves_with_the_version_of_an_engine_library(monkeypatch):
    raw = recipe()
    before = t1_keys(raw)
    monkeypatch.setattr(cache_keys, "_package_version", lambda name: "0.0.0-other")
    assert moved(before, t1_keys(raw)) == set(before)


# =====================================================================================================================
# Fail-safe: a part that cannot be narrowed stays coarse
# =====================================================================================================================


def broken_graph() -> dict:
    raw = recipe()
    raw["joins"]["J"]["ingredients"].append({"dataset_id": "NOT_A_TABLE"})
    return raw


def test_a_recipe_the_graph_cannot_draw_gives_coarse_keys_that_move_with_any_change():
    """MUTATION M4: a coarse key that holds only the table's own part would not move with a change elsewhere."""
    raw = broken_graph()
    parts, coarse = table_key_parts(raw)
    assert parts and all(p.coarse for p in parts.values()) and coarse.coarse
    before = t1_keys(raw)
    other_table = copy.deepcopy(raw)
    other_table["data_schemas"]["X"]["tier1"]["steps"] = [FILTER_B]
    assert moved(before, t1_keys(other_table)) == set(before), "a coarse key holds the whole recipe"
    assert moved(before, t1_keys(raw, {**FILES, "X": "x2"})) == set(before), "a coarse key holds every data file"


def test_a_table_id_the_recipe_does_not_name_gets_the_coarse_key_not_a_narrow_one():
    loaded_parts, coarse = table_key_parts(recipe())
    keys = DataAnalysisRecipeKeys("r", "d", {t: tier1_key(p, FILES) for t, p in loaded_parts.items()}, tier1_key(coarse, FILES))
    assert keys.tier1_key_of("nowhere") == keys.coarse_tier1_key != keys.tier1_key_of("A")


def test_a_coarse_key_also_holds_a_part_of_the_recipe_that_belongs_to_no_table():
    raw = recipe()
    other = copy.deepcopy(raw)
    other["some_future_section"] = {"a": 1}
    assert moved(t1_keys(raw), t1_keys(other)) == set(t1_keys(raw)), "an unknown top-level part is part of every table (fail-safe)"


# =====================================================================================================================
# What enters the definition of a table: one function
# =====================================================================================================================


def test_the_definition_of_a_table_leaves_out_its_tier2_and_the_engine_written_on_its_tier1_and_nothing_else():
    body = schema(steps=[FILTER_A], tier2=[FILTER_B])
    body["tier1"]["data_engine"] = "python-polars"
    body["ui_label"] = "A label"
    kept = table_definition_for_key(body)
    assert "tier2" not in kept and "data_engine" not in kept["tier1"] and kept["tier1"]["steps"] == [FILTER_A]
    assert body["tier2"]["steps"] == [FILTER_B] and body["tier1"]["data_engine"] == "python-polars", "the recipe itself is not changed"


def test_labels_of_a_table_are_in_the_key_today_the_owners_open_point():
    """Kept on purpose (the owner has not decided): a change of a label rebuilds the table. To take labels out, change
    `table_definition_for_key` and this test together."""
    before = recipe()
    after = copy.deepcopy(before)
    after["data_schemas"]["A"]["input_fields"]["group"]["ui_label"] = "Another label"
    assert moved(t1_keys(before), t1_keys(after)) == {"A", "J"}
    joined = copy.deepcopy(before)
    joined["joins"]["J"]["description"] = "a new description of the join"
    assert moved(t1_keys(before), t1_keys(joined)) == {"J"}


# =====================================================================================================================
# The identity hashes stay what they are
# =====================================================================================================================


def test_the_batch_hash_is_still_the_hash_of_all_files_in_the_old_form(tmp_path):
    files = {}
    for name, text in (("B", "b"), ("A", "a")):
        files[name] = tmp_path / f"{name}.tsv"
        files[name].write_text(text)
    old_form = []
    import hashlib
    for key in sorted(files):
        old_form.append(f"{key}:{hashlib.sha256(files[key].read_bytes()).hexdigest()}")
    expected = hashlib.sha256("\n".join(old_form).encode()).hexdigest()
    assert batch_hash_of(dataset_file_hashes(files)) == SessionManager.compute_data_batch_hash(files) == expected
    files["C"] = tmp_path / "missing.tsv"
    assert dataset_file_hashes(files)["C"] == "MISSING:C"


def test_no_data_file_gives_an_empty_batch_hash_as_before():
    parts, coarse = table_key_parts(recipe())
    loaded = mock.Mock(data_analysis_recipe_sha256="r", table_parts=parts, coarse_parts=coarse)
    assert data_analysis_recipe_keys(loaded, {}).data_batch_hash == ""
    assert data_analysis_recipe_keys(loaded, FILES).data_batch_hash == batch_hash_of(FILES)


# =====================================================================================================================
# Every table of every shipped recipe: any input moves its key and nothing else does
# =====================================================================================================================


def leaves(node, path=()):
    """Every value of a tree that can be changed: (path, value), also an empty list or mapping."""
    if isinstance(node, dict) and node:
        for k, v in node.items():
            yield from leaves(v, path + (k,))
    elif isinstance(node, list) and node:
        for i, v in enumerate(node):
            yield from leaves(v, path + (i,))
    else:
        yield path, node


def changed_value(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value + 1
    if isinstance(value, str):
        return value + "~"
    if value is None:
        return "x"
    if isinstance(value, list):
        return ["x"]
    return {"x": 1}


def with_leaf_changed(raw: dict, path: tuple) -> dict:
    new = copy.deepcopy(raw)
    node = new
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = changed_value(node[path[-1]])
    return new


def load_raw(path):
    """The resolved recipe as the app reads it. Every shipped file holds a recipe (an empty file fails `test_every_recipe_follows_the_spec.py`)."""
    return ConfigManager(path).raw_config


def upstream_names(raw: dict) -> dict:
    """{table: the table and everything upstream of it}, read from the graph (not from the code under test)."""
    graph = build_graph(raw)
    return {t: {graph.node(n).name for n in graph.lineage_back(f"T1:{t}") if graph.node(n).kind == "T1"} | {t} for t in graph.collections()}


# What the completion of the ids reads of a table that takes part (`utils.id_completion.plan_material`): a change there moves the key of every table that reads ANY table
# that takes part, not only of the tables built from this one (the union of the ids is made from all of them).
COMPLETION_KEYS = ("null_values", "strip", "source", "completion")


def decides_the_ids(raw: dict, table: str, leaf: tuple) -> bool:
    """True when the value at `leaf` of the table decides which ids the table holds: the schema's own words (`null_values`, `strip`, `source`, `completion`) or a field
    that declares the entity id (any other field of the table does not)."""
    if not leaf:
        return False
    if leaf[0] in COMPLETION_KEYS:
        return True
    body = collection_bodies(raw)[table]
    return leaf[0] == "input_fields" and len(leaf) > 1 and isinstance(body.get("input_fields", {}).get(leaf[1]), dict) and body["input_fields"][leaf[1]].get("is_entity_id") is True


def coupled_tables(raw: dict) -> set:
    """The tables that read at least one table that takes part in the completion of the ids, read from the graph (not from the code under test)."""
    taking_part = set(plan_material(raw))
    if not taking_part:
        return set()
    graph = build_graph(raw)
    return {t for t in graph.collections() if {graph.node(n).name for n in graph.source_tables(f"T1:{t}")} & taking_part}


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_a_changed_input_changes_the_key_of_every_table_that_depends_on_it_and_no_other(path):
    """The gate of ADR-101 point 3, over every table of every shipped recipe: each value written in a table's definition is changed
    in turn; the key of that table and of every table built from it moves, the key of every other table does not. A value in a
    tier 2 or under a downstream section moves no tier-1 key. MUTATION M1, M2, M3."""
    raw = load_raw(path)
    assert raw, f"{path} holds no recipe"
    files = {ds: f"hash-{ds}" for ds in collection_bodies(raw)}
    base = t1_keys(raw, files)
    assert base, "a recipe has tables"
    upstream = upstream_names(raw)
    bodies = collection_bodies(raw)
    checked = 0
    for table, body in bodies.items():
        readers = {t for t, names in upstream.items() if table in names}
        for leaf, _ in leaves(body):
            section = next((s for s in ("data_schemas", "additional_datasets_schemas", "joins") if table in (raw.get(s) or {})), None)
            full = (section, table) + leaf if section else ("metadata_schema",) + leaf
            mutated = with_leaf_changed(raw, full)
            after = t1_keys(mutated, files)
            if leaf and leaf[0] == "tier2":
                assert moved(base, after) == set(), f"{table}: a tier-2 value {leaf} moved a tier-1 key"
            elif leaf == ("tier1", "data_engine") or (leaf and leaf[0] == "tier1" and leaf[-1] == "data_engine"):
                assert readers <= moved(base, after), f"{table}: its tier-1 engine must move the tables built from it"
            else:
                try:
                    build_graph(mutated)
                    graph_ok = True
                except Exception:
                    graph_ok = False
                if graph_ok:
                    # a value that decides the ids of a table that takes part also moves every table that reads any table that takes part (the completion)
                    coupled = (coupled_tables(raw) | coupled_tables(mutated)) if table in plan_material(raw) and decides_the_ids(raw, table, leaf) else set()
                    assert moved(base, after) == readers | coupled, f"{table}: changing {leaf} moved {sorted(moved(base, after))}, expected {sorted(readers | coupled)}"
                else:
                    assert readers <= moved(base, after), f"{table}: changing {leaf} must move at least {sorted(readers)}"
            checked += 1
    assert checked
    for name in ("info", "analysis_groups", "plot_defaults", "plot_engine"):
        if name in raw:
            for leaf, _ in leaves(raw[name]):
                mutated = with_leaf_changed(raw, (name,) + leaf)
                try:
                    build_graph(mutated)
                except Exception:
                    continue          # a plot that names a table the recipe has: the graph cannot be drawn, every key is coarse (fail-safe)
                assert t1_keys(mutated, files) == base, f"a downstream value {name}{leaf} moved a table key"


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_a_data_file_moves_the_key_of_the_tables_that_read_it_and_no_other_on_every_shipped_recipe(path):
    raw = load_raw(path)
    assert raw, f"{path} holds no recipe"
    graph = build_graph(raw)
    files = {ds: f"hash-{ds}" for ds in collection_bodies(raw)}
    base = t1_keys(raw, files)
    sources = {graph.node(n).name for n in graph.nodes() if graph.node(n).kind == "DS"}
    for source in sources:
        readers = {t for t in graph.collections() if source in {graph.node(n).name for n in graph.source_tables(f"T1:{t}")}}
        coupled = coupled_tables(raw) if source in plan_material(raw) else set()   # the file of a table that takes part is read by every table that reads one (the completion)
        assert moved(base, t1_keys(raw, {**files, source: "changed"})) == readers | coupled, f"file of {source}"


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_the_keys_of_every_shipped_recipe_are_narrow_and_well_formed(path):
    """Which tables fall back to a coarse key on shipped recipes: none (the graph draws every one of them)."""
    raw = load_raw(path)
    assert raw, f"{path} holds no recipe"
    parts, coarse = table_key_parts(raw)
    assert set(parts) == set(collection_bodies(raw))
    assert not any(p.coarse for p in parts.values()), [t for t, p in parts.items() if p.coarse]
    assert all(T1_FORM.match(k) for k in t1_keys(raw, {ds: "h" for ds in parts}).values())
    assert len(set(t1_keys(raw, {ds: "h" for ds in parts}).values())) == len(parts), "no two tables of a recipe share a key"


# =====================================================================================================================
# End to end through the orchestrator: one source file changes and only the tables that read it are rebuilt
# =====================================================================================================================


class Staged:
    """A staged recipe on disk: files A, B, X (one table each), the join J = A + B with a tier 2, X plotted directly."""

    def __init__(self, root: Path):
        self.root = root
        self.data = root / "data"
        self.recipes = root / "recipes"
        self.anchors = root / "anchors"
        for d in (self.data, self.recipes, self.anchors):
            d.mkdir(parents=True, exist_ok=True)
        for name in ("A", "B", "X"):
            self.write_data(name, "sample_id\tgroup\ns1\tA\ns2\tB\n")
        self.write_recipe()
        self.orch = DataOrchestrator(self.recipes, self.data)

    def write_data(self, name: str, text: str) -> None:
        (self.data / f"{name}.tsv").write_text(text)

    def write_recipe(self, **changes) -> None:
        raw = recipe()
        for name in ("A", "B", "X"):
            raw["data_schemas"][name]["source"] = {"type": "local_tsv", "path": str(self.data / f"{name}.tsv")}
        # the join of two tables with the same columns: keep the columns of the first by selecting them on each side is not needed,
        # the tables share `sample_id` (the key) and `group` (declared once per side): a shared non-key column is refused (J08),
        # so the second ingredient publishes only its key and one new column.
        raw["data_schemas"]["B"]["input_fields"] = {
            "sample_id": {"original_name": "sample_id", "type": "Categorical", "ui_label": "Sample"},
            "group": {"original_name": "group", "type": "Categorical", "ui_label": "Group B"}}
        raw["data_schemas"]["B"]["tier1"]["steps"] = [{"action": "polars_rename", "mapping": {"group": "group_b"}}]
        raw["joins"]["J"]["tier1"]["steps"] = [{"action": "polars_join", "right_ingredient": "B", "on": ["sample_id"], "how": "left",
                                                 "maintain_order": "left_right"}]
        for path, value in changes.items():
            node = raw
            keys = path.split("/")
            for k in keys[:-1]:
                node = node[k]
            node[keys[-1]] = value
        (self.recipes / "staged.yaml").write_text(yaml.safe_dump(raw, sort_keys=False))
        clear_data_analysis_recipe_cache()

    def keys(self):
        return self.orch.compute_data_analysis_recipe_keys("staged")

    def anchor(self, table):
        return self.anchors / f"{table}.parquet"

    def build_all(self):
        keys = self.keys()
        for table in ("A", "B", "X", "J"):
            self.orch.materialize_tier1("staged", table, self.anchor(table), keys=keys)
        self.orch.materialize_tier2("staged", "J", self.anchor("J"), keys=keys)
        self.orch.materialize_tier2("staged", "X", self.anchor("X"), keys=keys)


def stores_during(staged: Staged, action):
    """The file names the orchestrator stores while `action()` runs: a counter of builds."""
    from transformer import anchor
    stored: list[str] = []
    real = anchor.write_anchor

    def counting(lf, path, *args, **kwargs):
        stored.append(Path(str(path)).name)
        return real(lf, path, *args, **kwargs)

    with mock.patch("app.modules.orchestrator.write_anchor", side_effect=counting):
        action()
    return sorted(stored)


def test_the_staged_recipe_builds_and_stores_every_table_under_its_own_key(tmp_path):
    s = Staged(tmp_path)
    s.build_all()
    keys = s.keys()
    for table in ("A", "B", "X", "J"):
        assert pl.read_parquet_metadata(str(s.anchor(table)))[TIER1_KEY_META] == keys.tier1_key_of(table)
    raw = load_data_analysis_recipe(s.recipes / "staged.yaml").raw
    assert pl.read_parquet_metadata(str(tier2_path_for(s.anchor("J"))))[TIER2_KEY_META] == collection_tier2_key(raw, "J", keys.tier1_key_of("J"))
    assert len({keys.tier1_key_of(t) for t in ("A", "B", "X", "J")}) == 4


def test_one_changed_source_file_rebuilds_only_the_tables_that_read_it(tmp_path):
    """MUTATION M1: with no data part in the key, a stale table would be served (or every table rebuilt by a coarse part)."""
    s = Staged(tmp_path)
    s.build_all()
    s.write_data("B", "sample_id\tgroup\ns1\tB\ns2\tB\n")
    assert stores_during(s, s.build_all) == ["B.parquet", "J.parquet", "J__T2.parquet"]
    s.write_data("X", "sample_id\tgroup\ns1\tB\ns2\tB\ns3\tA\n")
    assert stores_during(s, s.build_all) == ["X.parquet", "X__T2.parquet"]
    assert stores_during(s, s.build_all) == [], "nothing changed: every table is served"


def test_a_changed_step_of_one_table_rebuilds_that_table_and_what_is_built_from_it_only(tmp_path):
    s = Staged(tmp_path)
    s.build_all()
    s.write_recipe(**{"data_schemas/A/tier1/steps": [FILTER_A]})
    assert stores_during(s, s.build_all) == ["A.parquet", "J.parquet", "J__T2.parquet"]


def test_a_changed_tier2_step_rebuilds_the_tier2_only(tmp_path):
    s = Staged(tmp_path)
    s.build_all()
    s.write_recipe(**{"joins/J/tier2/steps": [FILTER_B]})
    assert stores_during(s, s.build_all) == ["J__T2.parquet"]


def test_a_change_in_a_plot_or_a_comment_rebuilds_nothing(tmp_path):
    s = Staged(tmp_path)
    s.build_all()
    before = s.keys()
    s.write_recipe(**{"analysis_groups/g/ui_label": "another label"})
    assert s.keys().data_analysis_recipe_sha256 != before.data_analysis_recipe_sha256, "the recipe file set did change"
    assert stores_during(s, s.build_all) == []


def test_a_stale_table_is_removed_when_the_mismatch_is_found_even_if_the_rebuild_then_fails(tmp_path):
    """Section 9 of rules_verification_testing.md: the stale file is removed at detection; the file of a table that does not depend on
    the change is kept."""
    s = Staged(tmp_path)
    s.build_all()
    s.write_data("B", "sample_id\tnot_the_declared_column\ns1\tx\n")      # a file that no longer fits its declared columns
    keys = s.keys()
    with pytest.raises(Exception):
        s.orch.materialize_tier1("staged", "J", s.anchor("J"), keys=keys)
    assert not s.anchor("J").exists() and not tier2_path_for(s.anchor("J")).exists()
    assert s.anchor("A").exists() and s.anchor("X").exists()
    assert pl.read_parquet_metadata(str(s.anchor("A")))[TIER1_KEY_META] == keys.tier1_key_of("A")


def test_a_stored_table_is_served_under_the_key_of_its_own_table_only(tmp_path):
    """The file of table A is not served for table X even when the two are stored under the same name by mistake."""
    s = Staged(tmp_path)
    s.build_all()
    stolen = tmp_path / "stolen.parquet"
    stolen.write_bytes(s.anchor("A").read_bytes())
    assert stores_during(s, lambda: s.orch.materialize_tier1("staged", "X", stolen, keys=s.keys())) == ["stolen.parquet"]


def test_the_keys_are_computed_once_from_one_reading_of_the_data_files(tmp_path):
    s = Staged(tmp_path)
    with mock.patch("app.modules.cache_keys.Path.read_bytes", autospec=True, side_effect=lambda self: b"x" if self.suffix == ".tsv" else b"") as read:
        s.keys()
    assert sum(1 for c in read.call_args_list if c.args[0].suffix == ".tsv") == 3, "each of the three data files is read once"


# =====================================================================================================================
# The export key check compares the tables in scope
# =====================================================================================================================


def keys_object(tier1: dict, sha="r", data="d") -> DataAnalysisRecipeKeys:
    return DataAnalysisRecipeKeys(sha, data, dict(tier1), "coarse")


def test_the_export_check_sees_a_changed_table_in_scope_and_not_one_out_of_scope():
    view = keys_object({"J": "kj", "X": "kx"})
    now = keys_object({"J": "kj", "X": "kx2"})           # same recipe file set and data, the processing of X is not the same
    assert changed_since_view(view, now, ["J", "X"]) == ["the processing rules (the engine version or the Tier 1 parts of the data analysis recipe)"]
    assert changed_since_view(view, now, ["J"]) == []
    assert changed_since_view(view, now) != []            # no scope given: every table of the view


def test_the_export_check_still_compares_the_identity_hashes():
    view = keys_object({"J": "kj"})
    assert changed_since_view(view, keys_object({"J": "kj"}, sha="other")) == ["the data analysis recipe (the data analysis recipe file or a file it includes)"]
    assert changed_since_view(view, keys_object({"J": "kj"}, data="other")) == ["the data files"]
    assert changed_since_view(view, keys_object({"J": "kj"}), ["J"]) == [] and changed_since_view(None, None) == []


def test_the_export_notice_lists_the_key_of_each_table_in_scope():
    view, now = keys_object({"J": "kj", "X": "kx"}), keys_object({"J": "kj", "X": "kx2"})
    text = blocked_export_notice(["the processing rules"], view, now, tables=["J", "X"])
    assert "tier1    X: kx" in text and "tier1    X: kx2" in text and "tier1    J: kj" in text


def test_a_change_after_the_view_was_built_is_detected_for_a_table_in_scope_on_real_keys(tmp_path):
    s = Staged(tmp_path)
    view = s.keys()
    s.write_data("X", "sample_id\tgroup\ns1\tA\n")
    now = s.keys()
    assert changed_since_view(view, now, ["X"]) == ["the data files"]
    assert view.tier1_key_of("J") == now.tier1_key_of("J") and view.tier1_key_of("X") != now.tier1_key_of("X")


def test_the_installed_versions_are_read_once_per_process_not_once_per_key():
    """The engine fingerprint is part of every table key (several per opening). Reading the package files for each one was nine tenths of the time of the keys.
    MUTATION K1: without the memory of `_package_version` the number of reads grows with the number of keys."""
    from unittest import mock
    from app.modules import cache_keys
    cache_keys._package_version.cache_clear()
    with mock.patch.object(cache_keys.metadata, "version", wraps=cache_keys.metadata.version) as reads:
        first = cache_keys.engine_fingerprint()
        for _ in range(50):
            assert cache_keys.engine_fingerprint() == first
    assert reads.call_count == 2, "polars and transformer, each read once"
    assert "polars=" in first and "transformer=" in first
