"""A data schema that a plot reads directly runs its own tier-2 list (RECIPE-DATASET-TIER2-1, issue #77, DEC16).

Decided by Eve 2026-11-12: every table has T1, T2 and T3, with or without a join; T2 and T3 can be empty. A schema
plotted directly is a collection and its tier-2 list is its T2: stored as `<name>__T2.parquet` with the chained key
`tier2_key(tier1_key, steps, engine)` exactly as for a join (ADR-089 point 6); an empty list means T2 equals T1 and nothing is
stored. Before the fix the engine ran the tier 1 only (`prepare_ingredient`) and read tier-2 steps of joins only, so
the steps were silently ignored (verified on `ResFinder` of `1_test_data_ST22_dummy`).

The same schema used as an ingredient of a join gives the join its T1 (spec line 357: the tier 2 of a schema applies
only when the schema is plotted directly). A tier-2 list on a schema that is only an ingredient is run nowhere, so it
is an error at load (S07, `home_audit_steps.md` 5a point 19): HOME refuses the recipe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_schema_tier2.py -q
"""
import json
import os
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, tier1_material, tier2_key, tier2_steps
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
from app.modules.orchestrator import TIER2_KEY_META, DataOrchestrator, tier2_path_for
from app.modules.view_badge import has_tier2_steps
from utils.config_loader import ConfigManager
from utils.hashing import get_parquet_metadata_hash
from utils.recipe_factory import minimal_join, minimal_plot, minimal_recipe, minimal_schema, write_recipe

OLD_MTIME_NS = 1_000_000_000 * 10**9
KEEP_A = {"action": "modif_filter", "column": "group", "op": "eq", "value": "A", "na": "remove"}
KEEP_B = {"action": "modif_filter", "column": "group", "op": "eq", "value": "B", "na": "remove"}


class SchemaWorld:
    """Schema T (3 rows, groups A A B) with its wrangling in an included file; plot `p_t` reads T directly and plot
    `p_c` reads the join C, whose only ingredient is T."""

    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / "data"
        self.recipes = root / "recipes"
        self.anchors = root / "user" / "anchors"
        for d in (self.data_dir, self.recipes, self.anchors):
            d.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "T.tsv"
        self.data_file.write_text("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\n")
        self.write(tier2=[KEEP_A])
        self.orch = DataOrchestrator(self.recipes, self.data_dir)

    def write(self, *, tier2, plot_t=True) -> None:
        frag = self.recipes / "tiny" / "wrangling"
        frag.mkdir(parents=True, exist_ok=True)
        # a tier is its own key; an include holds the content of the tier, `steps` (D-0250)
        tier2_file = frag / "T_tier2.yaml"
        tier2_file.write_text(json.dumps({"steps": list(tier2)}))
        plot_t_text = """
      p_t:
        ui_label: T directly
        target_dataset: T
        mapping: {x: group}
        layers:
          - name: geom_bar
            params: {}""" if plot_t else ""
        entry = self.recipes / "tiny.yaml"
        entry.write_text(f"""id: tiny
info: {{label: Tiny}}
data_engine: python-polars
plot_engine: python-plotnine
data_schemas:
  T:
    source: {{type: local_tsv, path: {self.data_file}}}
    null_values: []
    strip: false
    input_fields:
      sample_id: {{original_name: sample_id, type: String, label: Sample, is_entity_key: true}}
      group: {{original_name: group, type: String, label: Group}}
    tier1: {{steps: []}}
    tier2: !include 'tiny/wrangling/T_tier2.yaml'
joins:
  C:
    ingredients:
      - dataset_id: T
    tier1: {{steps: []}}
analysis_groups:
  g:
    ui_label: G
    plots:{plot_t_text}
      p_c:
        ui_label: C
        target_dataset: C
        mapping: {{x: group}}
        layers:
          - name: geom_bar
            params: {{}}
""")
        for f in (entry, tier2_file):
            st = os.stat(f)
            os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
        clear_data_analysis_recipe_cache()

    def anchor(self, collection: str) -> Path:
        return self.anchors / f"{collection}.parquet"

    def keys(self):
        return self.orch.compute_data_analysis_recipe_keys("tiny")

    def t1(self, collection: str) -> list[str]:
        lf = self.orch.materialize_tier1("tiny", collection, self.anchor(collection), keys=self.keys())
        return sorted(r["sample_id"] for r in lf.collect().to_dicts())

    def t2(self, collection: str) -> list[str]:
        lf = self.orch.materialize_tier2("tiny", collection, self.anchor(collection), keys=self.keys())
        return sorted(r["sample_id"] for r in lf.collect().to_dicts())

    def raw(self) -> dict:
        return ConfigManager(str(self.recipes / "tiny.yaml")).raw_config


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


@pytest.fixture
def world(tmp_path):
    return SchemaWorld(tmp_path)


# -- the engine -------------------------------------------------------------------------------

def test_a_schema_plotted_directly_runs_its_tier2(world):
    assert world.t1("T") == ["s1", "s2", "s3"], "tier 1 of T has no step"
    assert world.t2("T") == ["s1", "s2"], "the tier-2 step (keep group A) must run"


def test_the_tier2_of_a_schema_is_stored_with_the_chained_key(world):
    world.t2("T")
    stored = tier2_path_for(world.anchor("T"))
    assert stored.name == "T__T2.parquet" and stored.exists()
    assert get_parquet_metadata_hash(str(stored), TIER2_KEY_META) == tier2_key(world.keys().tier1_key, [KEEP_A], "python-polars")


def test_a_second_read_uses_the_stored_tier2(world):
    world.t2("T")
    stored = tier2_path_for(world.anchor("T"))
    os.utime(stored, ns=(OLD_MTIME_NS, OLD_MTIME_NS))
    assert world.t2("T") == ["s1", "s2"]
    assert os.stat(stored).st_mtime_ns == OLD_MTIME_NS, "a valid stored Tier 2 is read, not recomputed"


def test_a_changed_schema_tier2_changes_only_the_tier2(world):
    t1_key_before = world.keys().tier1_key
    world.t2("T")
    os.utime(world.anchor("T"), ns=(OLD_MTIME_NS, OLD_MTIME_NS))
    world.write(tier2=[KEEP_B])
    assert world.keys().tier1_key == t1_key_before, "a schema's tier 2 is downstream of Tier 1 (ADR-089 point 3)"
    assert world.t2("T") == ["s3"]
    assert os.stat(world.anchor("T")).st_mtime_ns == OLD_MTIME_NS, "the Tier 1 file is only checked, not rebuilt"


def test_an_empty_schema_tier2_stores_nothing_and_equals_tier1(world):
    world.write(tier2=[])
    assert world.t2("T") == ["s1", "s2", "s3"]
    assert not tier2_path_for(world.anchor("T")).exists()


def test_removing_the_schema_tier2_removes_the_stored_file(world):
    world.t2("T")
    assert tier2_path_for(world.anchor("T")).exists()
    world.write(tier2=[])
    assert world.t2("T") == ["s1", "s2", "s3"]
    assert not tier2_path_for(world.anchor("T")).exists(), "a Tier 2 file that no longer exists in the recipe must go"


def test_a_tier2_that_removes_every_row_gives_an_empty_table(world):
    world.write(tier2=[{"action": "modif_filter", "column": "group", "op": "eq", "value": "Z", "na": "remove"}])
    assert world.t2("T") == []


def test_the_join_reads_the_tier1_of_its_ingredient(world):
    """The ingredient case (spec line 357, DEC16): T is plotted directly AND is the ingredient of C. The join is built
    from T's Tier 1; T's tier 2 belongs to T's own T2 only."""
    assert world.t2("T") == ["s1", "s2"]
    assert world.t1("C") == ["s1", "s2", "s3"]
    assert world.t2("C") == ["s1", "s2", "s3"]


# -- one reading everywhere -------------------------------------------------------------------

def test_the_shared_reading_and_the_badge_see_the_schema_tier2(world):
    raw = world.raw()
    assert tier2_steps(raw, "T") == [KEEP_A]
    assert tier2_steps(raw, "C") == []
    assert has_tier2_steps(raw, "T") is True, "HOME's badge 'T2 identical to T1' would be wrong for T"
    assert has_tier2_steps(raw, "C") is False


def test_the_tier1_material_holds_no_schema_tier2(world):
    material = tier1_material(world.raw())
    assert "tier2" not in material["data_schemas"]["T"]


# -- the load gate: a tier-2 list that is run nowhere is an error ----------------------------------

def _gate_recipe(tmp_path: Path, *, plot_schema: bool) -> Path:
    schema = minimal_schema("data/T.tsv", {"sample_id": "String", "group": "String"}, entity_key="sample_id",
                            tier2=[KEEP_A])
    schema["description"] = "one row per sample"
    join = minimal_join(["T"], [])
    join["description"] = "the samples"
    plots = {"p_c": minimal_plot("C", {"x": "group"})}
    if plot_schema:
        plots["p_t"] = minimal_plot("T", {"x": "group"})
    recipe = minimal_recipe("gate", schemas={"T": schema}, joins={"C": join}, plots=plots)
    return write_recipe(tmp_path / "gate.yaml", recipe)


def test_home_refuses_a_tier2_on_a_schema_that_is_only_an_ingredient(tmp_path):
    problems = validate_data_analysis_recipe(_gate_recipe(tmp_path, plot_schema=False))
    assert any("[S07]" in str(p) for p in problems), [str(p) for p in problems]


def test_home_accepts_a_tier2_on_a_schema_that_a_plot_reads(tmp_path):
    problems = validate_data_analysis_recipe(_gate_recipe(tmp_path, plot_schema=True))
    assert not any("[S07]" in str(p) for p in problems), [str(p) for p in problems]


def test_home_refuses_a_join_tier2_that_no_plot_reads(tmp_path):
    schema = minimal_schema("data/T.tsv", {"sample_id": "String", "group": "String"}, entity_key="sample_id")
    schema["description"] = "one row per sample"
    join = minimal_join(["T"], [])
    join["description"] = "the samples"
    join["tier2"] = {"steps": [KEEP_A]}
    recipe = minimal_recipe("gate_join", schemas={"T": schema}, joins={"C": join},
                            plots={"p_t": minimal_plot("T", {"x": "group"})})
    problems = validate_data_analysis_recipe(write_recipe(tmp_path / "gate_join.yaml", recipe))
    assert any("[J14]" in str(p) for p in problems), [str(p) for p in problems]
