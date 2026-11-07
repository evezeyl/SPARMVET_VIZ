"""Tests for the cache chain keys (ADR-089, fork issue evezeyl/SPARMVET_VIZ#9).

Each test builds a tiny data analysis recipe in a temporary folder, changes one thing, and checks which
keys move. The rules under test:
  - a change anywhere upstream changes every key after it (chain);
  - a change that touches only one stage leaves the earlier keys alone;
  - unknown data analysis recipe sections count as Tier 1 (fail-safe);
  - how the data analysis recipe is split into files, and comments, do not change the cache keys;
  - data_analysis_recipe_sha256 (the file set) does change when any file changes.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_cache_keys.py -q
"""
import json
import os
import shutil
from pathlib import Path

import pytest

from app.modules import cache_keys
from app.modules.cache_keys import (
    clear_data_analysis_recipe_cache, load_data_analysis_recipe, data_analysis_recipe_fileset_hash,
    tier1_key, tier2_key, tier2_steps,
)

DATA_PATH = "/nonexistent/tiny.tsv"  # the data analysis recipe is only parsed here, the data is never read
FILTER_A = {"action": "filter_eq", "column": "group", "value": "A"}
FILTER_B = {"action": "filter_eq", "column": "group", "value": "B"}


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _yaml_value(value) -> str:
    return json.dumps(value)  # JSON is valid YAML


def make_project(root: Path, *, split=True, comment="", wrangling_tier1=(), steps_tier1=(),
                 steps_tier2=(), plot_label="P", extra_section=None) -> Path:
    """Write tiny.yaml (and, when split, its included fragments) under root; return the entry path."""
    root.mkdir(parents=True, exist_ok=True)
    wrangling = {"tier1": list(wrangling_tier1), "tier2": []}
    steps = {"tier1": list(steps_tier1), "tier2": list(steps_tier2)}
    if split:
        (root / "tiny" / "wrangling").mkdir(parents=True, exist_ok=True)
        (root / "tiny" / "wrangling" / "T_wrangling.yaml").write_text(_yaml_value(wrangling))
        (root / "tiny" / "wrangling" / "C_steps.yaml").write_text(_yaml_value(steps))
        wrangling_text = "!include 'tiny/wrangling/T_wrangling.yaml'"
        steps_text = "!include 'tiny/wrangling/C_steps.yaml'"
    else:
        wrangling_text = _yaml_value(wrangling)
        steps_text = _yaml_value(steps)
    extra = f"{extra_section}\n" if extra_section else ""
    entry = root / "tiny.yaml"
    entry.write_text(f"""{comment}id: tiny
info: {{display_name: Tiny}}
data_schemas:
  T:
    source: {{type: local_tsv, path: {DATA_PATH}}}
    input_fields:
      sample_id: {{original_name: sample_id, type: categorical, label: Sample, is_primary_key: true}}
      group: {{original_name: group, type: categorical, label: Group}}
    wrangling: {wrangling_text}
joins:
  C:
    ingredients:
      - dataset_id: T
    steps: {steps_text}
{extra}analysis_groups:
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
    return entry


def bump(path: Path) -> None:
    """Make the modification time differ, so a quick rewrite is seen by the size/mtime check."""
    st = os.stat(path)
    os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))


def keys_of(entry: Path, data_hash="d1", join_id="C"):
    loaded = load_data_analysis_recipe(entry)
    t1 = tier1_key(loaded.material_hash, data_hash)
    t2 = tier2_key(t1, tier2_steps(loaded.raw, join_id))
    return loaded, t1, t2


# --- chain: what moves when one thing changes ---------------------------------------------


def test_nothing_changes_gives_the_same_keys(tmp_path):
    entry = make_project(tmp_path)
    first = keys_of(entry)
    clear_data_analysis_recipe_cache()
    assert keys_of(entry)[1:] == first[1:]
    assert keys_of(entry)[0].data_analysis_recipe_sha256 == first[0].data_analysis_recipe_sha256


def test_data_change_moves_tier1_and_tier2(tmp_path):
    entry = make_project(tmp_path)
    _, t1a, t2a = keys_of(entry, data_hash="d1")
    _, t1b, t2b = keys_of(entry, data_hash="d2")
    assert t1a != t1b and t2a != t2b


def test_change_in_an_included_tier1_file_moves_tier1_and_tier2(tmp_path):
    entry = make_project(tmp_path)
    loaded_a, t1a, t2a = keys_of(entry)
    make_project(tmp_path, wrangling_tier1=[FILTER_A])
    bump(tmp_path / "tiny" / "wrangling" / "T_wrangling.yaml")
    loaded_b, t1b, t2b = keys_of(entry)
    assert t1a != t1b and t2a != t2b
    assert loaded_a.data_analysis_recipe_sha256 != loaded_b.data_analysis_recipe_sha256


def test_change_in_the_entry_file_tier1_part_moves_tier1(tmp_path):
    entry = make_project(tmp_path)
    _, t1a, _ = keys_of(entry)
    text = entry.read_text().replace("type: categorical, label: Group", "type: utf8, label: Group")
    entry.write_text(text)
    bump(entry)
    _, t1b, _ = keys_of(entry)
    assert t1a != t1b


def test_tier2_only_change_keeps_tier1_and_moves_tier2(tmp_path):
    entry = make_project(tmp_path)
    loaded_a, t1a, t2a = keys_of(entry)
    make_project(tmp_path, steps_tier2=[FILTER_A])
    bump(tmp_path / "tiny" / "wrangling" / "C_steps.yaml")
    loaded_b, t1b, t2b = keys_of(entry)
    assert t1a == t1b, "a Tier 2 step must not force a Tier 1 rebuild"
    assert t2a != t2b
    assert loaded_a.data_analysis_recipe_sha256 != loaded_b.data_analysis_recipe_sha256


def test_tier1_change_moves_tier2_even_when_tier2_steps_are_the_same(tmp_path):
    entry = make_project(tmp_path, steps_tier2=[FILTER_A])
    _, t1a, t2a = keys_of(entry)
    make_project(tmp_path, steps_tier1=[FILTER_B], steps_tier2=[FILTER_A])
    bump(tmp_path / "tiny" / "wrangling" / "C_steps.yaml")
    _, t1b, t2b = keys_of(entry)
    assert t1a != t1b and t2a != t2b


def test_plot_only_change_keeps_tier1_and_tier2(tmp_path):
    entry = make_project(tmp_path, plot_label="P")
    _, t1a, t2a = keys_of(entry)
    make_project(tmp_path, plot_label="A different plot title")
    bump(entry)
    _, t1b, t2b = keys_of(entry)
    assert (t1a, t2a) == (t1b, t2b), "editing a plot must not rebuild Tier 1 or Tier 2"


def test_unknown_new_section_counts_as_tier1(tmp_path):
    entry = make_project(tmp_path)
    _, t1a, _ = keys_of(entry)
    make_project(tmp_path, extra_section="some_future_section: {a: 1}")
    bump(entry)
    _, t1b, _ = keys_of(entry)
    assert t1a != t1b, "fail-safe: an unknown section must invalidate Tier 1, never be ignored"


def test_engine_version_moves_the_keys(tmp_path, monkeypatch):
    entry = make_project(tmp_path)
    _, t1a, t2a = keys_of(entry)
    monkeypatch.setattr(cache_keys, "ENGINE_CACHE_VERSION", "999")
    _, t1b, t2b = keys_of(entry)
    assert t1a != t1b and t2a != t2b


# --- what must NOT move the cache keys ------------------------------------------------------


def test_one_file_and_split_data_analysis_recipe_have_the_same_cache_key_material(tmp_path):
    split = make_project(tmp_path / "split", split=True, wrangling_tier1=[FILTER_A], steps_tier2=[FILTER_B])
    single = make_project(tmp_path / "single", split=False, wrangling_tier1=[FILTER_A], steps_tier2=[FILTER_B])
    loaded_split, t1_split, t2_split = keys_of(split)
    loaded_single, t1_single, t2_single = keys_of(single)
    assert (t1_split, t2_split) == (t1_single, t2_single)
    assert loaded_split.data_analysis_recipe_sha256 != loaded_single.data_analysis_recipe_sha256, "the file sets differ"


def test_a_comment_changes_the_file_set_hash_but_not_the_cache_keys(tmp_path):
    entry = make_project(tmp_path)
    loaded_a, t1a, t2a = keys_of(entry)
    make_project(tmp_path, comment="# a note for the next person\n")
    bump(entry)
    loaded_b, t1b, t2b = keys_of(entry)
    assert (t1a, t2a) == (t1b, t2b)
    assert loaded_a.data_analysis_recipe_sha256 != loaded_b.data_analysis_recipe_sha256


# --- the file set hash and the in-memory data analysis recipe -------------------------------------------


def test_loaded_files_lists_the_entry_and_every_include(tmp_path):
    entry = make_project(tmp_path)
    loaded = load_data_analysis_recipe(entry)
    names = sorted(Path(f).name for f in loaded.files)
    assert names == ["C_steps.yaml", "T_wrangling.yaml", "tiny.yaml"]


def test_file_set_hash_does_not_depend_on_where_the_folder_is(tmp_path):
    a = make_project(tmp_path / "one")
    shutil.copytree(tmp_path / "one", tmp_path / "two")
    b = tmp_path / "two" / "tiny.yaml"
    assert load_data_analysis_recipe(a).data_analysis_recipe_sha256 == load_data_analysis_recipe(b).data_analysis_recipe_sha256


def test_file_set_hash_matches_the_documented_steps(tmp_path):
    entry = make_project(tmp_path)
    loaded = load_data_analysis_recipe(entry)
    assert loaded.data_analysis_recipe_sha256 == data_analysis_recipe_fileset_hash(loaded.files, tmp_path)


def test_data_analysis_recipe_in_memory_is_reused_when_nothing_changed(tmp_path):
    entry = make_project(tmp_path)
    assert load_data_analysis_recipe(entry) is load_data_analysis_recipe(entry)


def test_data_analysis_recipe_in_memory_is_reloaded_when_an_included_file_changed(tmp_path):
    entry = make_project(tmp_path)
    before = load_data_analysis_recipe(entry)
    make_project(tmp_path, steps_tier2=[FILTER_A])
    bump(tmp_path / "tiny" / "wrangling" / "C_steps.yaml")
    after = load_data_analysis_recipe(entry)
    assert after is not before
    assert tier2_steps(after.raw, "C") == [FILTER_A]
