"""Every export of a recipe whose tables take part in the completion of the ids holds the log of the ids, and README.txt names it (D-0575, D-0582, D-0592, D-0613).

The real export generator is run headless (as `test_export_unread_tables.py` does) on the small recipe `Wide` of that file: three source tables `T`, `U`, `V` that declare an entity
id and have different ids, so each of them gets the lines of the others. The bundle holds `id_log.yaml` (the checks of THIS export's recipe and data, and the entries of the log of
the user folder), README.txt says in one line what it is, and the export writes nothing into the user folder. A recipe with no table that takes part has no such file and no such line.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_id_log.py -q
"""
import pytest
import yaml

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.id_check_run import ID_LOG_FOLDER
from app.tests.test_export_unread_tables import Wide, _export, _members, _zip


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def test_the_bundle_holds_the_log_of_the_ids_and_the_readme_names_it(tmp_path, monkeypatch):
    world = Wide(tmp_path)
    members = _members(_zip(_export(world, monkeypatch)[0]))
    assert "EXPORT_NOT_CREATED.txt" not in members and "id_log.yaml" in members
    log = yaml.safe_load(members["id_log.yaml"])
    assert log["format"] == 1 and "must read it" in log["about"]
    (entry,) = log["entries"]
    assert entry["who"] == "automatic, no user" and entry["ids"]["check_3"] == "passed"
    tables = {t["table"]: t for t in entry["ids"]["tables"]}
    assert set(tables) == {"T", "U", "V"} and tables["U"]["ids_added"]["count"] > 0
    assert tables["U"]["marker"] == "U_not_in_original_data" and tables["U"]["meaning"] == "no result for this entity"
    # the app's own fixed words for an added line, beside the sentence of the recipe maker (the owner, 2026-11-24)
    assert tables["U"]["added_line_words"] == "missing in original table"
    readme = members["README.txt"].decode()
    assert "  id_log.yaml       — the log of the ids" in readme and "read it before you rely on the results" in readme
    assert '"missing in original table"' in readme and "sentence of the recipe maker" in readme


def test_the_entry_of_the_export_carries_the_fingerprints_of_the_export(tmp_path, monkeypatch):
    world = Wide(tmp_path)
    yielded, view = _export(world, monkeypatch)
    entry = yaml.safe_load(_members(_zip(yielded))["id_log.yaml"])["entries"][0]
    assert entry["recipe_sha256"] == view.data_analysis_recipe_sha256 and entry["data_batch_hash"] == view.data_batch_hash


def test_the_export_writes_nothing_into_the_user_folder(tmp_path, monkeypatch):
    world = Wide(tmp_path)
    _export(world, monkeypatch)
    assert not (world.root / "user" / ID_LOG_FOLDER).exists()


def test_the_entries_of_the_user_folder_are_in_the_export_log(tmp_path, monkeypatch):
    from app.modules.id_check_run import id_log_folder
    from utils.id_log import record_read
    world = Wide(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    record_read(id_log_folder(world.root / "user"), "tiny", view.data_analysis_recipe_sha256, view.data_batch_hash, who="EZ")
    log = yaml.safe_load(_members(_zip(_export(world, monkeypatch)[0]))["id_log.yaml"])
    assert [e["kind"] for e in log["entries"]] == ["read", "checks"], "the click of the user folder, then the entry of this export"


def test_a_recipe_where_no_table_takes_part_has_no_log_and_no_line(tmp_path, monkeypatch):
    world = Wide(tmp_path)
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    text = recipe.read_text()
    import re
    recipe.write_text(re.sub(r"\n    completion: \{[^\n]*\}", "", text).replace(", is_entity_id: true", ""))
    clear_data_analysis_recipe_cache()
    members = _members(_zip(_export(world, monkeypatch)[0]))
    assert "id_log.yaml" not in members and "id_log" not in members["README.txt"].decode()
