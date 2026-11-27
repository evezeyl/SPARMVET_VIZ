"""Tests for app/modules/bundle_importer.py (ADR-097, #48/REPRO-IMPORT-1).

Builds a tiny, real recipe on disk (same minimal shape test_cache_keys.py uses), runs it
through the real bake_place_steps() recipe baking, zips it exactly as export_handlers.py
does, then feeds that zip into import_bundle() against a fake bootloader pointed at a
temp "deployment". No Shiny involved — bundle_importer.py is pure (Two-Category Law).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_bundle_importer.py -q
"""
import io
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from app.modules.bundle_importer import BundleImportError, import_bundle, read_effective_run
from app.modules.cache_keys import clear_data_analysis_recipe_cache, engine_fingerprint, load_data_analysis_recipe
from app.modules.session_manager import SessionManager
from app.modules.audit_places import bake_place_steps


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _make_recipe(root: Path, recipe_id: str, data_path: Path) -> Path:
    """A minimal, real recipe — same shape as test_cache_keys.py's make_data_analysis_recipe."""
    entry = root / f"{recipe_id}.yaml"
    entry.write_text(f"""id: {recipe_id}
info: {{ui_label: Tiny}}
data_engine: python-polars
plot_engine: python-plotnine
data_schemas:
  T:
    source: {{type: local_tsv, path: {data_path}}}
    null_values: []
    strip: false
    completion: {{marker: T_not_in_original_data, meaning: no result for this entity}}
    input_fields:
      sample_id: {{original_name: sample_id, type: Categorical, ui_label: Sample, is_entity_id: true}}
      group: {{original_name: group, type: Categorical, ui_label: Group}}
    tier1: {{steps: []}}
    tier2: {{steps: []}}
joins:
  C:
    ingredients:
      - dataset_id: T
    tier1: {{steps: []}}
    tier2: {{steps: []}}
analysis_groups:
  g:
    ui_label: G
    plots:
      p:
        ui_label: P
        target_dataset: C
        mapping: {{x: group}}
        layers:
          - name: geom_bar
            params: {{}}
""")
    return entry


class _FakeBootloader:
    def __init__(self, *, raw_data_dir: Path, recipes_dir: Path, user_data_dir: Path,
                 available: dict[str, Path] | None = None):
        self._raw_data_dir = raw_data_dir
        self.data_analysis_recipes_dir = recipes_dir
        self._user_data_dir = user_data_dir
        self.available_data_analysis_recipes = available or {}

    def get_location(self, key: str) -> Path:
        return {"raw_data": self._raw_data_dir, "user_data": self._user_data_dir}[key]

    def get_imports_dir(self) -> Path:
        return self._user_data_dir / "_imports"


def _build_bundle(tmp_path: Path, *, recipe_id="tiny", tamper_data=False,
                   ) -> tuple[bytes, dict, Path]:
    """Build a real Mode 2 bundle zip in memory. Returns (zip_bytes, effective_run, original_recipe_path)."""
    src_dir = tmp_path / "source"
    data_path = src_dir / "T.tsv"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text("sample_id\tgroup\nS1\tA\nS2\tB\n")

    original_recipe_path = _make_recipe(src_dir, recipe_id, data_path)
    loaded = load_data_analysis_recipe(original_recipe_path)

    mode2_cfg = bake_place_steps(loaded.raw, [])

    data_bytes = data_path.read_bytes()
    if tamper_data:
        data_bytes += b"\nTAMPERED\n"

    sm = SessionManager(tmp_path / "user_data")
    data_batch_hash = sm.compute_data_batch_hash({"T": data_path})

    effective_run = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "data_analysis_recipe_sha256": loaded.data_analysis_recipe_sha256,
        "data_batch_hash": data_batch_hash,
        "audit_steps_sha256": "0" * 64,
        "engine_fingerprint": engine_fingerprint(),
        "containerized": False,
        "image_ref": None,
        "uv_lock_sha256": None,
        "git_commit": "n/a",
        "release_version": "n/a",
        "software_versions": {"python": "3.14"},
        "data_source_paths": {"T": str(data_path)},
        "seeds_per_plot": {},
    }

    buf = io.BytesIO()
    bundle_dir = "20261109_120000_autotest"
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{bundle_dir}/effective_run.yaml", yaml.safe_dump(effective_run, sort_keys=False))
        zf.writestr(
            f"{bundle_dir}/data_analysis_recipes_reproducibility/{recipe_id}.yaml",
            yaml.safe_dump(mode2_cfg, sort_keys=False, allow_unicode=True),
        )
        zf.writestr(f"{bundle_dir}/data_reproducibility/T.tsv", data_bytes)
    return buf.getvalue(), effective_run, original_recipe_path


def _rewrite_effective_run(zip_bytes: bytes, run: dict) -> bytes:
    """The same bundle with another effective_run.yaml."""
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith("effective_run.yaml"):
                data = yaml.safe_dump(run, sort_keys=False).encode()
            zout.writestr(item.filename, data)
    return out.getvalue()


def _fresh_bootloader(tmp_path: Path, **kw) -> _FakeBootloader:
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / "raw_data").mkdir(exist_ok=True)       # the deployment's data folder exists (the ingestor needs it)
    return _FakeBootloader(
        raw_data_dir=tmp_path / "raw_data",
        recipes_dir=recipes_dir,
        user_data_dir=tmp_path / "user_data",
        **kw,
    )


# ---------------------------------------------------------------------------

def test_missing_effective_run_raises(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("bundle/README.txt", "nothing here")
    with pytest.raises(BundleImportError, match="effective_run.yaml"):
        import_bundle(buf.getvalue(), bootloader=_fresh_bootloader(tmp_path))


def test_mode1_only_bundle_refuses_with_a_clear_reason(tmp_path):
    """A bundle exported without the reproducibility checkbox has no recipe to import."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("bundle/effective_run.yaml", yaml.safe_dump({"data_batch_hash": "x"}))
    with pytest.raises(BundleImportError, match="reproducibility/reimport bundle"):
        import_bundle(buf.getvalue(), bootloader=_fresh_bootloader(tmp_path))


def test_missing_data_folder_raises(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    # Strip the data_reproducibility entries out of an otherwise valid bundle.
    with zipfile.ZipFile(io.BytesIO(zb)) as zf:
        keep = [n for n in zf.namelist() if "/data_reproducibility/" not in n]
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as out:
            for n in keep:
                out.writestr(n, zf.read(n))
    with pytest.raises(BundleImportError, match="data_reproducibility"):
        import_bundle(buf.getvalue(), bootloader=_fresh_bootloader(tmp_path))


def test_read_effective_run_standalone(tmp_path):
    zb, run, _orig = _build_bundle(tmp_path)
    assert read_effective_run(zb)["data_batch_hash"] == run["data_batch_hash"]


def test_import_writes_recipe_and_session(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    result = import_bundle(zb, bootloader=bl)

    assert result.imported_recipe_path.exists()
    written = yaml.safe_load(result.imported_recipe_path.read_text())
    assert written["id"] == result.recipe_id
    assert result.recipe_id.startswith("tiny_imported_")
    assert "plots" not in written      # ConfigManager-internal mirror never persisted
    assert "joins" in written

    session_dir = bl.get_location("user_data") / "_sessions" / result.session_key
    assert (session_dir / "assembly.json").exists()

    assert set(result.legs.keys()) == {"data", "engine", "recipe", "t3_steps"}


def _rewrite_zip(zb: bytes, *, drop=(), add=None) -> bytes:
    """The same bundle without the entries whose name contains one of `drop`, plus the entries in `add`."""
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(zb)) as zf, zipfile.ZipFile(buf, "w") as out:
        for n in zf.namelist():
            if not any(d in n for d in drop):
                out.writestr(n, zf.read(n))
        for n, content in (add or {}).items():
            out.writestr(n, content)
    return buf.getvalue()


def _tree(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()} if root.exists() else set()


def test_the_data_of_an_import_is_stored_by_dataset_id_in_its_own_folder(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    result = import_bundle(zb, bootloader=bl)
    data_dir = tmp_path / "user_data" / "_imports" / result.recipe_id / "data"
    assert [p.name for p in data_dir.iterdir()] == ["T.tsv"]
    assert (data_dir / "T.tsv").read_text().startswith("sample_id\tgroup")


def test_the_recipe_path_is_not_touched_and_nothing_is_written_to_raw_data(tmp_path):
    zb, _run, orig = _build_bundle(tmp_path)
    original_path = yaml.safe_load(orig.read_text())["data_schemas"]["T"]["source"]["path"]
    bl = _fresh_bootloader(tmp_path)
    result = import_bundle(zb, bootloader=bl)
    written = yaml.safe_load(result.imported_recipe_path.read_text())
    assert str(written["data_schemas"]["T"]["source"]["path"]) == str(original_path)
    assert list((tmp_path / "raw_data").iterdir()) == []


def test_the_orchestrator_reads_the_rows_of_the_import_not_the_exporting_machines_file(tmp_path):
    from app.modules.orchestrator import DataOrchestrator
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    (tmp_path / "raw_data" / "T.tsv").write_text("sample_id\tgroup\nOTHER\tZ\n")
    result = import_bundle(zb, bootloader=bl)
    # the file the recipe still names (the exporting machine's path) now holds other rows
    (tmp_path / "source" / "T.tsv").write_text("sample_id\tgroup\nELSEWHERE\tZ\n")
    orch = DataOrchestrator(bl.data_analysis_recipes_dir, tmp_path / "raw_data", data_lookup="data_analysis_recipe_paths",
                            imports_dir=bl.get_imports_dir())
    frame = orch.materialize_tier1(result.recipe_id, "C", tmp_path / "anchor.parquet")
    assert sorted(frame.collect()["sample_id"].to_list()) == ["S1", "S2"]


def test_the_imported_recipe_passes_the_gate_of_home(tmp_path):
    """HOME's load gate on reload (ADR-094): structure and data, with the data folder of the import."""
    from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe_data
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    result = import_bundle(zb, bootloader=bl)
    for mode in ("data_analysis_recipe_paths", "by_dataset_id"):
        problems = validate_data_analysis_recipe_data(result.imported_recipe_path, tmp_path / "raw_data",
                                                       data_lookup=mode, imports_dir=bl.get_imports_dir())
        assert problems == [], (mode, problems)


def test_the_session_key_and_hash_cover_the_files_the_engine_reads(tmp_path):
    from app.modules.orchestrator import DataOrchestrator
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    result = import_bundle(zb, bootloader=bl)
    orch = DataOrchestrator(bl.data_analysis_recipes_dir, tmp_path / "raw_data", imports_dir=bl.get_imports_dir())
    keys = orch.compute_data_analysis_recipe_keys(result.recipe_id)
    assert result.legs["data"].actual == keys.data_batch_hash
    sm = SessionManager(tmp_path / "user_data")
    assert result.session_key == sm.compute_session_key(keys.data_analysis_recipe_sha256, keys.data_batch_hash)


def test_two_imports_of_the_same_bundle_stay_apart(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    first = import_bundle(zb, bootloader=bl)
    second = import_bundle(zb, bootloader=bl)       # same second: the timestamp alone would collide
    assert first.recipe_id != second.recipe_id
    assert first.imported_recipe_path != second.imported_recipe_path
    for r in (first, second):
        assert (tmp_path / "user_data" / "_imports" / r.recipe_id / "data" / "T.tsv").read_text().startswith("sample_id")
    assert first.legs["data"].status == second.legs["data"].status == "match"


def test_a_dataset_that_the_recipe_does_not_name_is_kept_apart_and_reported_not_hashed(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    zb = _rewrite_zip(zb, add={"20261109_120000_autotest/data_reproducibility/EXTRA.tsv": b"x\n1\n"})
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["data"].status == "match"                 # the hash covers the files the recipe reads
    assert "EXTRA" in result.legs["data"].detail                 # and the file that is not read is named


def test_a_dataset_named_by_the_recipe_but_missing_in_the_bundle_is_a_data_mismatch_that_names_it(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    zb = _rewrite_zip(zb, drop=("data_reproducibility/T.tsv",),
                      add={"20261109_120000_autotest/data_reproducibility/T_ERROR.txt": b"could not copy",
                           "20261109_120000_autotest/data_reproducibility/OTHER.tsv": b"x\n1\n"})
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["data"].status == "mismatch"
    assert "T" in result.legs["data"].detail and "missing" in result.legs["data"].detail.lower()


def test_one_dataset_with_a_tsv_and_a_parquet_in_the_bundle_refuses_the_import_and_leaves_nothing(tmp_path):
    import polars as pl
    zb, _run, _orig = _build_bundle(tmp_path)
    pq = io.BytesIO()
    pl.DataFrame({"sample_id": ["S9"], "group": ["Q"]}).write_parquet(pq)
    zb = _rewrite_zip(zb, add={"20261109_120000_autotest/data_reproducibility/T.parquet": pq.getvalue()})
    bl = _fresh_bootloader(tmp_path)
    with pytest.raises(BundleImportError, match="T"):
        import_bundle(zb, bootloader=bl)
    assert _tree(tmp_path / "user_data") == set()
    assert list((tmp_path / "recipes").iterdir()) == []


def test_a_parquet_dataset_is_imported_and_read(tmp_path):
    import polars as pl
    from app.modules.orchestrator import DataOrchestrator
    zb, _run, _orig = _build_bundle(tmp_path)
    pq = io.BytesIO()
    pl.DataFrame({"sample_id": ["S1", "S2"], "group": ["A", "B"]}).write_parquet(pq)
    zb = _rewrite_zip(zb, drop=("data_reproducibility/T.tsv",),
                      add={"20261109_120000_autotest/data_reproducibility/T.parquet": pq.getvalue()})
    bl = _fresh_bootloader(tmp_path)
    result = import_bundle(zb, bootloader=bl)
    orch = DataOrchestrator(bl.data_analysis_recipes_dir, tmp_path / "raw_data", imports_dir=bl.get_imports_dir())
    assert orch.get_source_files(result.recipe_id)["T"].name == "T.parquet"
    assert sorted(orch.materialize_tier1(result.recipe_id, "C", tmp_path / "a.parquet").collect()["sample_id"].to_list()) == ["S1", "S2"]


def test_data_leg_matches_on_an_intact_bundle(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["data"].status == "match"


def test_data_leg_mismatches_when_the_bundle_was_tampered_with(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path, tamper_data=True)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["data"].status == "mismatch"


def test_engine_leg_matches_when_run_on_the_same_machine(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    # The bundle was built with this same process's engine_fingerprint(); git_commit is
    # "n/a" (no git subprocess assumed in a test sandbox) which the verifier treats as
    # unknown rather than a forced mismatch.
    assert result.legs["engine"].status == "match"


def test_engine_leg_mismatches_when_fingerprint_differs(tmp_path, monkeypatch):
    zb, _run, _orig = _build_bundle(tmp_path)
    import app.modules.bundle_importer as bi
    monkeypatch.setattr(bi, "engine_fingerprint", lambda: "different-fingerprint")
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["engine"].status == "mismatch"


def test_recipe_leg_not_checked_when_original_not_available_locally(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["recipe"].status == "not_checked"
    # the wording names both things written into the frozen copy: the audited steps and the jitter seeds
    assert "T3 steps" in result.legs["recipe"].detail
    assert "seeds" in result.legs["recipe"].detail and "seeds_added_to_recipe" in result.legs["recipe"].detail


def test_recipe_leg_checked_and_matches_when_original_available_locally(tmp_path):
    zb, _run, original_recipe_path = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path, available={"tiny": original_recipe_path})
    result = import_bundle(zb, bootloader=bl)
    assert result.legs["recipe"].status == "match"


def test_recipe_leg_mismatches_when_the_local_original_was_edited(tmp_path):
    zb, _run, original_recipe_path = _build_bundle(tmp_path)
    # Edit the local original after the bundle was built — its hash now differs.
    original_recipe_path.write_text(
        original_recipe_path.read_text().replace("group: {original_name", "team: {original_name")
    )
    clear_data_analysis_recipe_cache()
    bl = _fresh_bootloader(tmp_path, available={"tiny": original_recipe_path})
    result = import_bundle(zb, bootloader=bl)
    assert result.legs["recipe"].status == "mismatch"


def test_t3_steps_leg_is_always_not_checked(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["t3_steps"].status == "not_checked"
    assert result.legs["t3_steps"].recorded == "0" * 64


def test_a_bundle_with_the_old_steps_hash_name_says_so_and_does_not_read_it_as_the_new_one(tmp_path):
    zb, run, _orig = _build_bundle(tmp_path)
    old = dict(run)
    old["t3_audit_steps_sha256"] = old.pop("audit_steps_sha256")
    zb = _rewrite_effective_run(zb, old)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    leg = result.legs["t3_steps"]
    assert leg.recorded is None
    assert "older version" in leg.detail and "not compared" in leg.detail


def test_a_broken_frozen_recipe_raises_loudly_not_silently(tmp_path):
    """If the frozen copy can't even load, import must fail, not produce an unusable recipe."""
    zb, _run, _orig = _build_bundle(tmp_path)
    with zipfile.ZipFile(io.BytesIO(zb)) as zf:
        names = zf.namelist()
        recipe_name = next(n for n in names if n.endswith("tiny.yaml"))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as out:
            for n in names:
                if n == recipe_name:
                    out.writestr(n, "analysis_groups: {}\n")  # structurally invalid
                else:
                    out.writestr(n, zf.read(n))
    with pytest.raises(BundleImportError, match="could not be loaded"):
        import_bundle(buf.getvalue(), bootloader=_fresh_bootloader(tmp_path))
    assert _tree(tmp_path / "user_data") == set()          # a refused import leaves no data folder and no ghost
    assert list((tmp_path / "recipes").iterdir()) == []    # and no recipe file


def test_an_older_record_under_the_same_session_key_refuses_the_import_and_leaves_nothing(tmp_path, monkeypatch):
    """D-0312: a record of an older format is never written over; the import is refused with the plain line and the files
    the import wrote are removed, and nothing that existed before is touched."""
    import json
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    monkeypatch.setattr(SessionManager, "compute_session_key", staticmethod(lambda msig, dbh: key))
    sessions = bl.get_location("user_data") / "_sessions" / key
    sessions.mkdir(parents=True)
    old = sessions / "assembly.json"
    old.write_text(json.dumps({"session_key": key, "data_analysis_recipe_id": "x", "label": "mine"}))   # no format number
    old_bytes = old.read_bytes()
    # things that exist BEFORE the import
    kept_import = bl.get_imports_dir() / "earlier_import" / "data" / "keep.tsv"
    kept_import.parent.mkdir(parents=True)
    kept_import.write_text("a\n")
    kept_recipe = bl.data_analysis_recipes_dir / "earlier.yaml"
    kept_recipe.write_text("id: earlier\n")
    recipes_before, imports_before = _tree(bl.data_analysis_recipes_dir), _tree(bl.get_imports_dir())

    with pytest.raises(BundleImportError) as exc:
        import_bundle(zb, bootloader=bl)

    assert str(exc.value) == ("The bundle was not imported and nothing was written. "
                              f"Session {key} (assembly.json) was saved by an older version of the app and cannot be opened. "
                              "Delete it and start a new session.")
    assert _tree(bl.data_analysis_recipes_dir) == recipes_before and not list(bl.data_analysis_recipes_dir.glob("*_imported_*"))
    assert _tree(bl.get_imports_dir()) == imports_before
    assert kept_import.read_text() == "a\n" and kept_recipe.read_text() == "id: earlier\n"
    assert old.read_bytes() == old_bytes
