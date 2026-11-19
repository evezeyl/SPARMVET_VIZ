"""A stored table carries the key of the files it was REALLY built from (STALE-KEY-STORE-1, ADR-089).

HOME computes its keys once and keeps them while the recipe or the data change on disk. A table that is not stored yet is
then built from the files of NOW. It must be stored under the key of those files, never under the key HOME holds: the next
read with the held key (or after the author changed the recipe back) would serve the wrong table as valid.

Mutation index (each is a change of the code that one named test must see fail; grep "MUTATION"):
  M6   Tier 2 `unchanged` ignores the check of the Tier 1 inputs     -> test_a_tier2_whose_tier1_was_built_just_now_is_not_stored_...
  M6b  Tier 2 `unchanged` ignores that the Tier 1 itself saw a change -> test_a_tier1_built_from_a_mix_makes_its_tier2_unstorable_...
  M7   Tier 2 `unchanged` ignores the comparison of the tier-2 steps   -> test_a_tier2_is_not_stored_when_its_own_steps_change_...
  M9   `inputs_changed` says "nothing changed" when the recipe can no longer be read or its file is gone
                                                                       -> test_a_recipe_that_can_no_longer_be_read_is_a_change_...
  M9c  the Tier 2 check ignores a recipe that cannot be read           -> test_a_recipe_that_cannot_be_read_when_tier2_is_about_to_be_stored_...
  (M10, the notice branch "the tables follow", is in test_data_change_notice.py)

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_stale_key_store.py -q
"""
from unittest import mock

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, tier2_key
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, tier2_path_for
from app.tests.test_cache_chain import FILTER_A, FILTER_B, World
from utils.hashing import get_parquet_metadata_hash


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def ids(lf):
    return sorted(lf.collect()["sample_id"].to_list())


def stored(path, meta):
    return get_parquet_metadata_hash(str(path), meta)


def test_a_table_built_after_a_recipe_change_is_stored_under_the_key_of_the_new_recipe(tmp_path):
    w = World(tmp_path)
    held = w.orch.compute_data_analysis_recipe_keys("tiny")           # the view is opened
    w.write_data_analysis_recipe(steps_tier1=[FILTER_B])               # the recipe changes under it
    other = w.anchor.parent / "D.parquet"
    rows = ids(w.orch.materialize_tier1("tiny", "C", other, keys=held))
    now = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert rows == ["s3"]
    assert stored(other, TIER1_KEY_META) == now.tier1_key != held.tier1_key


def test_the_author_changes_the_recipe_back_and_the_table_of_the_other_recipe_is_not_served(tmp_path):
    w = World(tmp_path)
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.write_data_analysis_recipe(steps_tier1=[FILTER_B])
    other = w.anchor.parent / "D.parquet"
    w.orch.materialize_tier1("tiny", "C", other, keys=held)           # built from the new recipe
    w.write_data_analysis_recipe()                                     # back to the first text
    back = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert back.tier1_key == held.tier1_key
    assert ids(w.orch.materialize_tier1("tiny", "C", other, keys=back)) == ["s1", "s2", "s3"]


def test_a_table_built_after_a_data_change_is_stored_under_the_key_of_the_new_data(tmp_path):
    w = World(tmp_path)
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")
    rows = ids(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=held))
    now = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert rows == ["s1", "s2", "s3", "s4"]
    assert stored(w.anchor, TIER1_KEY_META) == now.tier1_key != held.tier1_key


def test_tier2_built_on_a_new_tier1_is_stored_under_the_chain_of_the_new_tier1(tmp_path):
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.write_data_analysis_recipe(steps_tier1=[FILTER_B], steps_tier2=[FILTER_A])    # tier 1 AND tier 2 changed
    rows = ids(w.orch.materialize_tier2("tiny", "C", w.anchor, keys=held))
    now = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert rows == []                                                   # B rows then kept A only: nothing
    t2 = tier2_path_for(w.anchor)
    assert stored(w.anchor, TIER1_KEY_META) == now.tier1_key
    assert stored(t2, TIER2_KEY_META) == tier2_key(now.tier1_key, [FILTER_A], "python-polars")


def test_matching_keys_still_reuse_the_stored_table(tmp_path):
    """The normal path is untouched: keys that match the stored key serve the file, nothing is rebuilt."""
    w = World(tmp_path)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    with mock.patch("app.modules.orchestrator.write_anchor") as writer:
        assert ids(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)) == ["s1", "s2", "s3"]
    writer.assert_not_called()


def test_a_build_whose_inputs_changed_during_the_build_is_not_stored(tmp_path):
    w = World(tmp_path)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    real = w.orch.prepare_ingredient

    def ingest_then_the_file_changes(*args, **kwargs):
        lf = real(*args, **kwargs)
        w.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")
        return lf

    with mock.patch.object(w.orch, "prepare_ingredient", side_effect=ingest_then_the_file_changes):
        rows = w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    assert ids(rows)                          # the caller still gets a table
    assert not w.anchor.exists(), "a table built while its inputs changed must not be stored under any key"


# ---------------------------------------------------------------------------------------------------------------------
# A build that sees its inputs change says so (no silent mix) and the check of the inputs is itself checked.
# ---------------------------------------------------------------------------------------------------------------------

NEW_DATA = "sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n"


def change_when_the_tier2_file_is_about_to_be_written(world, change):
    """A `write_anchor` that runs `change()` just before it writes the Tier 2 table: the inputs change during that build."""
    from app.modules import orchestrator as orchestrator_module
    real = orchestrator_module.write_anchor

    def spy(lf, path, **kwargs):
        if TIER2_KEY_META in (kwargs.get("metadata") or {}):
            change()
        return real(lf, path, **kwargs)

    return mock.patch.object(orchestrator_module, "write_anchor", side_effect=spy)


def test_a_tier2_whose_tier1_was_built_just_now_is_not_stored_when_the_data_changes_during_the_tier2_build(tmp_path):
    """MUTATION M6: the check of the Tier 1 inputs is part of the Tier 2 check."""
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    told = []
    # Tier 1 is not stored yet, so it is built in this very call: its inputs are checked again before Tier 2 is stored
    with change_when_the_tier2_file_is_about_to_be_written(w, lambda: w.write_data(NEW_DATA)):
        w.orch.materialize_tier2("tiny", "C", w.anchor, keys=held, on_inputs_changed=told.append)
    assert not tier2_path_for(w.anchor).exists(), "a Tier 2 built on data that changed meanwhile must not be stored"
    assert [c.text for c in told] == ["the data files changed"]


def test_a_tier2_is_not_stored_when_its_own_steps_change_during_its_build(tmp_path):
    """MUTATION M7: the tier-2 steps are compared after the build. The Tier 1 is served from the store, so only the steps can change."""
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    first = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier2("tiny", "C", w.anchor, keys=first)
    tier2_path_for(w.anchor).unlink()                                     # only Tier 2 is missing
    told = []
    with change_when_the_tier2_file_is_about_to_be_written(w, lambda: w.write_data_analysis_recipe(steps_tier2=[FILTER_B])):
        rows = ids(w.orch.materialize_tier2("tiny", "C", w.anchor, keys=first, on_inputs_changed=told.append))
    assert not tier2_path_for(w.anchor).exists()
    assert rows == ["s1", "s2"]                                           # the table is still returned
    assert [c.text for c in told] == ["the tier-2 steps of this table changed"]


def test_a_tier1_built_from_changed_inputs_makes_its_tier2_unstorable_too(tmp_path):
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    real = w.orch.prepare_ingredient

    def ingest_then_the_file_changes(*args, **kwargs):
        lf = real(*args, **kwargs)
        w.write_data(NEW_DATA)
        return lf

    told = []
    with mock.patch.object(w.orch, "prepare_ingredient", side_effect=ingest_then_the_file_changes):
        w.orch.materialize_tier2("tiny", "C", w.anchor, keys=held, on_inputs_changed=told.append)
    assert not w.anchor.exists() and not tier2_path_for(w.anchor).exists()
    assert len(told) == 1, "one notice, not one per tier"


def test_a_build_tells_its_caller_that_the_inputs_changed_during_the_build(tmp_path):
    w = World(tmp_path)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    real = w.orch.prepare_ingredient

    def ingest_then_the_file_changes(*args, **kwargs):
        lf = real(*args, **kwargs)
        w.write_data(NEW_DATA)
        return lf

    told = []
    with mock.patch.object(w.orch, "prepare_ingredient", side_effect=ingest_then_the_file_changes):
        table = w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys, on_inputs_changed=told.append)
    assert ids(table) and not w.anchor.exists()
    assert [c.text for c in told] == ["the data files changed"]


def test_a_build_whose_inputs_did_not_change_tells_nothing_and_stores(tmp_path):
    w = World(tmp_path)
    told = []
    w.orch.materialize_tier1("tiny", "C", w.anchor, keys=w.orch.compute_data_analysis_recipe_keys("tiny"), on_inputs_changed=told.append)
    assert told == [] and w.anchor.exists()


def test_a_recipe_that_changed_during_the_build_is_named_as_the_recipe(tmp_path):
    w = World(tmp_path)
    built_from = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert w.orch.inputs_changed("tiny", built_from) is None
    w.write_data_analysis_recipe(plot_label="another label")                   # the recipe text changes
    assert w.orch.inputs_changed("tiny", built_from).text == "the data analysis recipe changed"


def test_a_recipe_that_can_no_longer_be_read_is_a_change_named_as_such_not_silence(tmp_path):
    """MUTATION M9: an unreadable recipe or a missing file must never read as "nothing changed"."""
    w = World(tmp_path)
    built_from = w.orch.compute_data_analysis_recipe_keys("tiny")
    (w.data_analysis_recipes_dir / "tiny.yaml").write_text("id: tiny\ndata_schemas: [unclosed\n")
    change = w.orch.inputs_changed("tiny", built_from)
    assert change is not None and change.text.startswith("the data analysis recipe can no longer be read")
    (w.data_analysis_recipes_dir / "tiny.yaml").unlink()
    assert w.orch.inputs_changed("tiny", built_from).text == "the data analysis recipe file is gone"


def test_a_data_file_that_is_gone_is_a_change_of_the_data(tmp_path):
    w = World(tmp_path)
    built_from = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.data_file.unlink()
    assert w.orch.inputs_changed("tiny", built_from).text == "the data files changed"


def test_a_tier1_built_from_a_mix_makes_its_tier2_unstorable_even_if_the_data_is_back_by_then(tmp_path):
    """MUTATION M6b: the Tier 1 saw the data change; if the file is restored before Tier 2 is written, the Tier 2 check alone would pass."""
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    original = w.data_file.read_text()
    real = w.orch.prepare_ingredient

    def ingest_then_the_file_changes(*args, **kwargs):
        lf = real(*args, **kwargs)
        w.write_data(NEW_DATA)
        return lf

    told = []
    with mock.patch.object(w.orch, "prepare_ingredient", side_effect=ingest_then_the_file_changes), \
            change_when_the_tier2_file_is_about_to_be_written(w, lambda: w.write_data(original)):
        w.orch.materialize_tier2("tiny", "C", w.anchor, keys=held, on_inputs_changed=told.append)
    assert not tier2_path_for(w.anchor).exists()
    assert [c.text for c in told] == ["the data files changed"]


def test_a_recipe_that_cannot_be_read_when_tier2_is_about_to_be_stored_is_told_and_nothing_is_stored(tmp_path):
    """MUTATION M9c: the Tier 2 check turns an unreadable recipe into "nothing changed"."""
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    first = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier2("tiny", "C", w.anchor, keys=first)
    tier2_path_for(w.anchor).unlink()
    told = []
    breaker = lambda: (w.data_analysis_recipes_dir / "tiny.yaml").write_text("id: tiny\ndata_schemas: [unclosed\n")  # noqa: E731
    with change_when_the_tier2_file_is_about_to_be_written(w, breaker):
        w.orch.materialize_tier2("tiny", "C", w.anchor, keys=first, on_inputs_changed=told.append)
    assert not tier2_path_for(w.anchor).exists()
    assert len(told) == 1 and told[0].text.startswith("the data analysis recipe can no longer be read")


def test_a_stored_table_is_served_through_the_one_read_that_pairs_its_key_with_its_content(tmp_path):
    """Both tiers read the key and the content from the same open file (`read_anchor_if_key`), never key by name, then scan by name."""
    from app.modules import orchestrator as orchestrator_module
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier2("tiny", "C", w.anchor, keys=keys)
    with mock.patch.object(orchestrator_module, "read_anchor_if_key", wraps=orchestrator_module.read_anchor_if_key) as read:
        assert ids(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)) == ["s1", "s2", "s3"]
        assert ids(w.orch.materialize_tier2("tiny", "C", w.anchor, keys=keys)) == ["s1", "s2"]
    assert [c.args[1] for c in read.call_args_list] == [TIER1_KEY_META, TIER2_KEY_META]
    assert all(c.args[2] for c in read.call_args_list)
