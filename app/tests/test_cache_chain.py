"""End-to-end tests of the Tier 1 cache chain (ADR-089, fork issue evezeyl/SPARMVET_VIZ#9).

A real (tiny) data analysis recipe, real data and real parquet files in a temporary folder. Each test
changes one thing and checks whether the stored Tier 1 parquet is rebuilt or kept, and that
the rows that come out reflect what is on disk. The case that started it all, a change in an
INCLUDED file, is test_change_in_an_included_file_is_picked_up.

Rebuild detection: after the first build the parquet's modification time is set far in the
past; a rewrite shows as a different modification time.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_cache_chain.py -q
"""
import json
import os
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import TIER1_KEY_META, DataOrchestrator
from utils.hashing import get_parquet_metadata_hash

OLD_MTIME_NS = 1_000_000_000 * 10**9  # an old, fixed time (year 2001)
FILTER_A = {"action": "filter_eq", "column": "group", "value": "A"}
FILTER_B = {"action": "filter_eq", "column": "group", "value": "B"}


class World:
    """A tiny project: data file, data analysis recipe with two included files, and an orchestrator."""

    def __init__(self, root: Path, data_lookup: str = "data_analysis_recipe_paths"):
        self.root = root
        self.data_dir = root / "data"
        self.data_analysis_recipes_dir = root / "data_analysis_recipes"
        self.anchor = root / "user" / "anchors" / "C.parquet"
        for d in (self.data_dir, self.data_analysis_recipes_dir, self.anchor.parent):
            d.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "T.tsv"
        self.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\n")
        self.write_data_analysis_recipe()
        self.orch = DataOrchestrator(self.data_analysis_recipes_dir, self.data_dir, data_lookup=data_lookup)

    # -- things a test can change ------------------------------------------------------------
    def write_data(self, text: str) -> None:
        self.data_file.write_text(text)
        bump(self.data_file)

    def write_data_analysis_recipe(self, *, wrangling_tier1=(), recipe_tier1=(), recipe_tier2=(), plot_label="P",
                       group_type="categorical", final_contract=None, source_path=None) -> None:
        frag = self.data_analysis_recipes_dir / "tiny" / "wrangling"
        frag.mkdir(parents=True, exist_ok=True)
        (frag / "T_wrangling.yaml").write_text(json.dumps({"tier1": list(wrangling_tier1), "tier2": []}))
        (frag / "C_recipe.yaml").write_text(json.dumps({"tier1": list(recipe_tier1), "tier2": list(recipe_tier2)}))
        contract = f"    final_contract: {json.dumps(final_contract)}\n" if final_contract else ""
        entry = self.data_analysis_recipes_dir / "tiny.yaml"
        entry.write_text(f"""id: tiny
info: {{display_name: Tiny}}
data_schemas:
  T:
    source: {{type: local_tsv, path: {source_path or self.data_file}}}
    input_fields:
      sample_id: {{original_name: sample_id, type: categorical, label: Sample, is_primary_key: true}}
      group: {{original_name: group, type: {group_type}, label: Group}}
    wrangling: !include 'tiny/wrangling/T_wrangling.yaml'
joins:
  C:
    ingredients:
      - dataset_id: T
    recipe: !include 'tiny/wrangling/C_recipe.yaml'
{contract}analysis_groups:
  g:
    label: G
    plots:
      p:
        label: {plot_label}
        spec:
          target_dataset: C
          mapping: {{x: group}}
          layers:
            - name: geom_bar
              params: {{}}
""")
        for f in (entry, frag / "T_wrangling.yaml", frag / "C_recipe.yaml"):
            bump(f)

    # -- what a session does ---------------------------------------------------------------
    def build(self):
        """One session start: compute the keys, then materialize. Returns the rows as dicts."""
        keys = self.orch.compute_project_keys("tiny")
        lf = self.orch.materialize_tier1("tiny", "C", self.anchor, keys=keys)
        return sorted(lf.collect().to_dicts(), key=lambda r: r["sample_id"])

    def pin_mtime(self) -> None:
        os.utime(self.anchor, ns=(OLD_MTIME_NS, OLD_MTIME_NS))

    def was_rewritten(self) -> bool:
        return os.stat(self.anchor).st_mtime_ns != OLD_MTIME_NS

    def stored_key(self):
        return get_parquet_metadata_hash(str(self.anchor), TIER1_KEY_META)


def bump(path: Path) -> None:
    """A different modification time, so a quick rewrite is seen by the size/mtime check."""
    st = os.stat(path)
    os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


@pytest.fixture
def world(tmp_path):
    w = World(tmp_path)
    assert len(w.build()) == 3
    w.pin_mtime()
    return w


def test_first_build_stores_the_chained_key(world):
    assert world.stored_key() == world.orch.compute_project_keys("tiny").tier1_key


def test_nothing_changed_keeps_the_anchor(world):
    assert len(world.build()) == 3
    assert not world.was_rewritten()


def test_data_change_rebuilds_with_the_new_rows(world):
    world.write_data("sample_id\tgroup\ns1\tC\ns2\tA\ns3\tB\ns4\tB\ns5\tB\n")
    rows = world.build()
    assert world.was_rewritten()
    assert [r["sample_id"] for r in rows] == ["s1", "s2", "s3", "s4", "s5"]
    assert rows[0]["group"] == "C"


def test_change_in_the_entry_file_rebuilds(world):
    world.write_data_analysis_recipe(group_type="utf8")
    world.build()
    assert world.was_rewritten()


def test_change_in_an_included_file_is_picked_up(world):
    """The bug of issue #9: only an included file changes (a Tier 1 filter keeping group A)."""
    world.write_data_analysis_recipe(wrangling_tier1=[FILTER_A])
    rows = world.build()
    assert world.was_rewritten(), "the stored anchor was served although an included file changed"
    assert [r["sample_id"] for r in rows] == ["s1", "s2"]


def test_change_in_the_assembly_recipe_tier1_rebuilds(world):
    world.write_data_analysis_recipe(recipe_tier1=[FILTER_B])
    rows = world.build()
    assert world.was_rewritten()
    assert [r["sample_id"] for r in rows] == ["s3"]


def test_tier2_only_change_keeps_the_tier1_anchor(world):
    world.write_data_analysis_recipe(recipe_tier2=[FILTER_A])
    assert len(world.build()) == 3
    assert not world.was_rewritten(), "a Tier 2 step must not force a Tier 1 rebuild"


def test_plot_only_change_keeps_the_tier1_anchor(world):
    world.write_data_analysis_recipe(plot_label="Another title")
    world.build()
    assert not world.was_rewritten()


def test_unknown_data_analysis_recipe_section_rebuilds_tier1(world):
    entry = world.data_analysis_recipes_dir / "tiny.yaml"
    entry.write_text(entry.read_text() + "some_future_section: {a: 1}\n")
    bump(entry)
    world.build()
    assert world.was_rewritten(), "fail-safe: an unknown section must invalidate Tier 1"


def test_an_anchor_without_a_key_is_rebuilt(world):
    """Anchors written before the cache chain have no key: they are rebuilt once, never trusted."""
    import polars as pl
    pl.scan_csv(world.data_file, separator="\t").collect().write_parquet(world.anchor)
    world.pin_mtime()
    assert world.stored_key() is None
    world.build()
    assert world.was_rewritten()
    assert world.stored_key() == world.orch.compute_project_keys("tiny").tier1_key


def test_final_contract_is_applied_the_same_on_a_fresh_and_a_reused_anchor(tmp_path):
    w = World(tmp_path)
    w.write_data_analysis_recipe(final_contract={"sample_id": "categorical"})
    fresh = w.build()
    w.pin_mtime()
    reused = w.build()
    assert not w.was_rewritten()
    assert fresh == reused
    assert set(fresh[0].keys()) == {"sample_id"}


# --- data location: data_lookup by_dataset_id (ADR-088 point 5) -----------------------------------------


def test_with_data_lookup_by_dataset_id_the_data_hash_follows_the_delivered_data(tmp_path):
    """Production: the data analysis recipe's source.path is only default data; raw_data/T.tsv is what counts."""
    default_data = tmp_path / "default_data.tsv"
    default_data.write_text("sample_id\tgroup\nx1\tA\n")
    w = World(tmp_path / "w", data_lookup="by_dataset_id")
    w.write_data_analysis_recipe(source_path=default_data)
    before = w.orch.compute_project_keys("tiny").data_batch_hash

    default_data.write_text("sample_id\tgroup\nx1\tA\nx2\tB\n")   # the default data changes
    assert w.orch.compute_project_keys("tiny").data_batch_hash == before

    w.write_data("sample_id\tgroup\ns1\tA\n")                        # the delivered data changes
    assert w.orch.compute_project_keys("tiny").data_batch_hash != before
    assert [r["sample_id"] for r in w.build()] == ["s1"]
