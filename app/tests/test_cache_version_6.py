"""The cache version 6 (the mechanism arrived with version 5): a table stored with another version is never served, is removed when the mismatch is found, and the user is
told once (D-0240, D-0285 reading: the notice wording is PROVISIONAL, not approved by Eve).

What is tested:
  - a stored table whose key was made with version 5 is not served and is removed at the moment the mismatch is detected, also
    when the rebuild then fails (nothing that should be gone is left behind, rules_verification_testing.md section 9);
  - the sweep at the start of the app removes every stored table that carries no version 6 mark (a table of version 5 has none),
    leaves what is not a stored table, and says so in one sentence, once;
  - the session key and the recipe hash do not depend on the cache version;
  - a session of version 5 (a record with no table keys) and a bundle of version 5 are read, never half-read: the tables are
    rebuilt and the bundle's engine leg says plainly that it does not match.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_cache_version_6.py -q
"""
import io
import json
import os
import zipfile
from pathlib import Path

import polars as pl
import pytest
import yaml

from app.modules import cache_keys
from app.modules.bundle_importer import import_bundle
from app.modules.cache_keys import CACHE_VERSION_META, STORED_TABLES_REBUILT_NOTICE, clear_data_analysis_recipe_cache
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, tier2_path_for
from app.modules.session_manager import SessionManager
from app.tests.test_bundle_importer import _build_bundle, _fresh_bootloader, _rewrite_zip
from app.tests.test_cache_chain import FILTER_A, OLD_MTIME_NS, World, bump
from app.tests.test_stale_key_store import change_when_the_tier2_file_is_about_to_be_written
from transformer.anchor import remove_tables_of_other_version, write_anchor
from utils.hashing import get_parquet_metadata_hash

NOTICE = ("The tables of your recipes are rebuilt once because the app changed how it names what it stored. "
          "Your results do not change.")


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _store(path: Path, key: str, meta_key: str, version: str | None) -> None:
    """A stored table as an older or the current app wrote it: with `version` None it carries no mark (a table of version 5)."""
    metadata = {meta_key: key}
    if version is not None:
        metadata[CACHE_VERSION_META] = version
    write_anchor(pl.DataFrame({"sample_id": ["old"]}).lazy(), str(path), decision_hash=key, metadata=metadata)


# --- the wording ---------------------------------------------------------------------------------------------------------------


def test_the_notice_is_the_one_sentence_the_review_session_proposed_PROVISIONAL():
    assert STORED_TABLES_REBUILT_NOTICE == NOTICE


# --- a stored table of another version is not served and is removed when it is found -----------------------------------------


def test_a_table_stored_under_version_5_is_not_served_and_is_rebuilt_with_the_mark_of_version_6(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_keys, "ENGINE_CACHE_VERSION", "5")
    w = World(tmp_path)
    assert len(w.build()) == 3
    old_key = w.stored_key()
    monkeypatch.undo()                          # the app is now version 6
    clear_data_analysis_recipe_cache()
    assert w.anchor.exists()
    rows = w.build()
    assert len(rows) == 3
    assert w.stored_key() != old_key, "the table of version 5 was served"
    assert get_parquet_metadata_hash(str(w.anchor), CACHE_VERSION_META) == "6"


def test_a_table_written_by_version_5_with_no_version_mark_is_rebuilt_not_served(tmp_path, monkeypatch):
    """What an old file really is: the key of version 5 and no version mark at all."""
    w = World(tmp_path)
    monkeypatch.setattr(cache_keys, "ENGINE_CACHE_VERSION", "5")
    key_4 = w.orch.compute_data_analysis_recipe_keys("tiny").tier1_key_of("C")
    monkeypatch.undo()
    clear_data_analysis_recipe_cache()
    _store(w.anchor, key_4, TIER1_KEY_META, None)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert keys.tier1_key_of("C") != key_4
    lf = w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    assert sorted(lf.collect()["sample_id"].to_list()) == ["s1", "s2", "s3"], "the table of version 5 was served"
    assert get_parquet_metadata_hash(str(w.anchor), CACHE_VERSION_META) == "6"


def test_a_table_of_another_version_is_removed_at_the_moment_it_is_found_even_when_the_rebuild_fails(tmp_path, monkeypatch):
    w = World(tmp_path)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    _store(w.anchor, "a-key-of-version-4", TIER1_KEY_META, None)
    monkeypatch.setattr(type(w.orch), "prepare_ingredient", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("cannot read")))
    with pytest.raises(Exception):
        w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    assert not w.anchor.exists(), "MUTATION 'no removal at detection': the table that cannot be served is still on disk"


def test_a_tier2_of_another_version_is_removed_when_it_is_found_and_rebuilt(tmp_path):
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    t2 = tier2_path_for(w.anchor)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    _store(t2, "a-key-of-version-4", TIER2_KEY_META, None)
    lf = w.orch.materialize_tier2("tiny", "C", w.anchor, keys=keys)
    assert sorted(lf.collect()["sample_id"].to_list()) == ["s1", "s2"], "the Tier 2 of version 5 was served"
    assert get_parquet_metadata_hash(str(t2), CACHE_VERSION_META) == "6"


def test_a_tier2_of_another_version_is_removed_at_the_moment_it_is_found_even_when_its_rebuild_fails(tmp_path):
    from unittest import mock
    from transformer.data_wrangler import DataWrangler
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    t2 = tier2_path_for(w.anchor)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    _store(t2, "a-key-of-version-4", TIER2_KEY_META, None)
    with mock.patch.object(DataWrangler, "run", side_effect=RuntimeError("the step fails")), pytest.raises(RuntimeError):
        w.orch.materialize_tier2("tiny", "C", w.anchor, keys=keys)
    assert not t2.exists(), "MUTATION 'no removal at detection (Tier 2)': the table that cannot be served is still on disk"


def test_a_tier2_is_not_stored_when_its_engine_changes_during_its_build(tmp_path):
    """The engine of the tier is part of the key it is stored under, so a change of it while the table is built means the key no
    longer says what the file holds: the table is returned, not stored, and the caller is told (as for a change of the steps)."""
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    first = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier2("tiny", "C", w.anchor, keys=first)
    tier2_path_for(w.anchor).unlink()

    def the_author_names_another_engine_on_tier2():
        file = w.data_analysis_recipes_dir / "tiny" / "wrangling" / "C_tier2.yaml"
        file.write_text(json.dumps({"data_engine": "engine-x", "steps": [FILTER_A]}))
        bump(file)

    told = []
    with change_when_the_tier2_file_is_about_to_be_written(w, the_author_names_another_engine_on_tier2):
        w.orch.materialize_tier2("tiny", "C", w.anchor, keys=first, on_inputs_changed=told.append)
    assert not tier2_path_for(w.anchor).exists()
    assert [c.text for c in told] == ["the tier-2 steps of this table changed"]


def test_a_table_of_the_current_version_and_key_is_still_served_not_rebuilt(tmp_path):
    w = World(tmp_path)
    w.build()
    w.pin_mtime()
    w.build()
    assert not w.was_rewritten()


def test_the_stored_tables_carry_the_mark_of_the_version_that_wrote_them(tmp_path):
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier2("tiny", "C", w.anchor, keys=keys)
    for table in (w.anchor, tier2_path_for(w.anchor)):
        assert get_parquet_metadata_hash(str(table), CACHE_VERSION_META) == cache_keys.ENGINE_CACHE_VERSION


# --- the sweep at the start of the app -----------------------------------------------------------------------------------------


def test_the_sweep_removes_every_stored_table_that_is_not_of_this_version_and_names_them(tmp_path):
    _store(tmp_path / "old.parquet", "k", TIER1_KEY_META, None)
    _store(tmp_path / "older_T2.parquet", "k", TIER2_KEY_META, "5")
    _store(tmp_path / "current.parquet", "k", TIER1_KEY_META, "6")
    removed = remove_tables_of_other_version(tmp_path, CACHE_VERSION_META, "6")
    assert sorted(removed) == ["old.parquet", "older_T2.parquet"]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["current.parquet"]


def test_the_sweep_leaves_a_file_that_is_not_a_stored_table_and_a_file_it_cannot_read(tmp_path):
    pl.DataFrame({"a": [1]}).write_parquet(tmp_path / "not_ours.parquet")          # no key in the footer: not a stored table
    (tmp_path / "broken.parquet").write_bytes(b"not a parquet file")
    (tmp_path / ".C.parquet.abc.tmp").write_bytes(b"temporary")                      # the temporary file of a writer
    (tmp_path / "notes.txt").write_text("keep")
    assert remove_tables_of_other_version(tmp_path, CACHE_VERSION_META, "6") == []
    assert sorted(p.name for p in tmp_path.iterdir()) == [".C.parquet.abc.tmp", "broken.parquet", "not_ours.parquet", "notes.txt"]


def test_the_sweep_of_an_empty_or_missing_folder_does_nothing(tmp_path):
    assert remove_tables_of_other_version(tmp_path, CACHE_VERSION_META, "6") == []
    assert remove_tables_of_other_version(tmp_path / "nowhere", CACHE_VERSION_META, "6") == []


def test_a_second_sweep_finds_nothing_so_the_notice_cannot_come_twice(tmp_path):
    _store(tmp_path / "old.parquet", "k", TIER1_KEY_META, None)
    assert remove_tables_of_other_version(tmp_path, CACHE_VERSION_META, "6") == ["old.parquet"]
    assert remove_tables_of_other_version(tmp_path, CACHE_VERSION_META, "6") == []


# --- the start of the app: the notice, once ------------------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[2]


def _deployment(tmp_path):
    root = tmp_path / "dep_data"
    locations = {}
    for key in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    path = tmp_path / "dep.yaml"
    path.write_text(yaml.safe_dump({"deployment_type": "filesystem", "default_app_features": "qa",
                                    "locations": locations}))
    return path, root / "user_data" / "anchors"


@pytest.fixture
def launch(tmp_path, monkeypatch):
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE", "SPARMVET_CONNECTOR",
                "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)
    dep, anchors = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    return anchors


def test_the_start_removes_the_old_tables_and_the_user_gets_the_notice_once(launch):
    from app.src.bootloader import Bootloader
    launch.mkdir(parents=True, exist_ok=True)
    _store(launch / "C.parquet", "k", TIER1_KEY_META, None)
    boot = Bootloader()
    assert not (launch / "C.parquet").exists()
    assert boot.take_stored_tables_notice() == NOTICE
    assert boot.take_stored_tables_notice() is None, "the notice came twice in the same run"
    assert Bootloader().take_stored_tables_notice() is None, "the notice came again at the next start, with nothing stored"


def test_a_start_with_nothing_stored_shows_no_notice(launch):
    from app.src.bootloader import Bootloader
    assert Bootloader().take_stored_tables_notice() is None
    launch.mkdir(parents=True, exist_ok=True)
    _store(launch / "C.parquet", "k", TIER1_KEY_META, cache_keys.ENGINE_CACHE_VERSION)
    assert Bootloader().take_stored_tables_notice() is None
    assert (launch / "C.parquet").exists()


def test_the_handler_tells_the_notice_once_through_the_alerts_notifier():
    from types import SimpleNamespace
    from app.handlers.recipe_gate_handlers import tell_tables_rebuilt
    told = []
    boot = SimpleNamespace(take_stored_tables_notice=iter([NOTICE, None, None]).__next__)
    assert tell_tables_rebuilt(boot, lambda text, **kw: told.append((text, kw))) is True
    assert tell_tables_rebuilt(boot, lambda text, **kw: told.append(text)) is False
    assert told == [(NOTICE, {"type": "message", "duration": 20})]


def test_the_session_of_the_app_runs_that_handler_when_it_starts():
    import inspect
    from app.handlers import recipe_gate_handlers
    assert "tell_tables_rebuilt(bootloader" in inspect.getsource(recipe_gate_handlers.define_server)


# --- the session key and the recipe hash are not changed by the version -------------------------------------------------------


def test_the_recipe_hash_and_the_session_key_do_not_depend_on_the_cache_version(tmp_path, monkeypatch):
    w = World(tmp_path)
    entry = w.data_analysis_recipes_dir / "tiny.yaml"
    sha_5 = SessionManager.compute_data_analysis_recipe_sha256(entry)
    key_5 = SessionManager.compute_session_key(sha_5, "d" * 64)
    monkeypatch.setattr(cache_keys, "ENGINE_CACHE_VERSION", "5")
    clear_data_analysis_recipe_cache()
    sha_4 = SessionManager.compute_data_analysis_recipe_sha256(entry)
    assert sha_4 == sha_5 and SessionManager.compute_session_key(sha_4, "d" * 64) == key_5


def test_the_recipe_hash_is_the_hash_of_the_files_so_an_engine_written_in_the_recipe_changes_it_as_any_edit_does(tmp_path):
    w = World(tmp_path)
    entry = w.data_analysis_recipes_dir / "tiny.yaml"
    before = SessionManager.compute_data_analysis_recipe_sha256(entry)
    entry.write_text(entry.read_text().replace("plot_engine: python-plotnine", "plot_engine: python-plotnine-2"))
    clear_data_analysis_recipe_cache()
    assert SessionManager.compute_data_analysis_recipe_sha256(entry) != before


# --- a session and a bundle written under version 5 -----------------------------------------------------------------------------


def test_a_session_of_version_5_restores_and_its_tables_are_rebuilt_from_the_recipe_and_data(tmp_path, monkeypatch):
    """A session record holds no table key and no table path (the app writes `parquet_paths: {}`): restoring it brings back the
    audit steps; the tables are read through the orchestrator's key check, which rebuilds what carries another version."""
    monkeypatch.setattr(cache_keys, "ENGINE_CACHE_VERSION", "5")
    w = World(tmp_path)
    w.build()
    old_key = w.stored_key()
    sm = SessionManager(tmp_path / "user")
    entry = w.data_analysis_recipes_dir / "tiny.yaml"
    sha = SessionManager.compute_data_analysis_recipe_sha256(entry)
    batch = SessionManager.compute_data_batch_hash({"T": w.data_file})
    key = SessionManager.compute_session_key(sha, batch)
    sm.write_assembly_ghost(key, "tiny", sha, batch, {"T": str(w.data_file)}, parquet_paths={})
    monkeypatch.undo()                                    # now version 6
    clear_data_analysis_recipe_cache()
    restored = sm.restore_t1t2(entry, {"T": w.data_file})
    assert restored["session_key"] == key and restored["status"] in ("fast_path", "reassemble")
    assert len(w.build()) == 3 and w.stored_key() != old_key


def test_a_bundle_of_version_5_is_imported_and_its_engine_leg_says_plainly_that_it_does_not_match(tmp_path):
    zb, run, _orig = _build_bundle(tmp_path)
    old = dict(run, engine_fingerprint=run["engine_fingerprint"].replace("6|", "5|", 1))
    assert old["engine_fingerprint"].startswith("5|")
    zb = _rewrite_zip(zb, drop=("effective_run.yaml",), add={"20261109_120000_autotest/effective_run.yaml": yaml.safe_dump(old)})
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    engine = result.legs["engine"]
    assert engine.status == "mismatch" and engine.recorded.startswith("5|") and engine.actual.startswith("6|")
    assert "software change" in engine.detail
    assert result.legs["data"].status == "match"


def test_a_bundle_whose_record_has_no_engines_key_is_imported_as_before(tmp_path):
    zb, run, _orig = _build_bundle(tmp_path)
    assert "engines" not in run
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert set(result.legs) == {"data", "engine", "recipe", "t3_steps"}


def test_a_bundle_whose_record_has_the_new_engines_key_is_imported_and_reports_the_same_legs(tmp_path):
    zb, run, _orig = _build_bundle(tmp_path)
    new = dict(run, engines={"recipe_default": {"data_engine": "python-polars", "plot_engine": "python-plotnine"},
                             "tables": {}, "plots": {}, "library_versions": {}})
    zb = _rewrite_zip(zb, drop=("effective_run.yaml",), add={"20261109_120000_autotest/effective_run.yaml": yaml.safe_dump(new)})
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert set(result.legs) == {"data", "engine", "recipe", "t3_steps"}
    assert result.legs["data"].status == "match" and result.legs["engine"].status == "match"
