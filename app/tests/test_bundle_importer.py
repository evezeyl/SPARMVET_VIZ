"""Tests for app/modules/bundle_importer.py (ADR-097, #48/REPRO-IMPORT-1).

Builds a tiny, real recipe on disk (same minimal shape test_cache_keys.py uses), runs it
through the real build_mode2_recipe() translator, zips it exactly as export_handlers.py
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
from blueprint_arch.t3_translator import build_mode2_recipe


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _make_recipe(root: Path, recipe_id: str, data_path: Path) -> Path:
    """A minimal, real recipe — same shape as test_cache_keys.py's make_data_analysis_recipe."""
    entry = root / f"{recipe_id}.yaml"
    entry.write_text(f"""id: {recipe_id}
info: {{display_name: Tiny}}
data_schemas:
  T:
    source: {{type: local_tsv, path: {data_path}}}
    input_fields:
      sample_id: {{original_name: sample_id, type: categorical, label: Sample, is_primary_key: true}}
      group: {{original_name: group, type: categorical, label: Group}}
    wrangling: {{tier1: [], tier2: []}}
joins:
  C:
    ingredients:
      - dataset_id: T
    steps: {{tier1: [], tier2: []}}
analysis_groups:
  g:
    label: G
    plots:
      p:
        label: P
        spec:
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


def _build_bundle(tmp_path: Path, *, recipe_id="tiny", tamper_data=False,
                   t3_translation_skipped=None) -> tuple[bytes, dict, Path]:
    """Build a real Mode 2 bundle zip in memory. Returns (zip_bytes, effective_run, original_recipe_path)."""
    src_dir = tmp_path / "source"
    data_path = src_dir / "T.tsv"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text("sample_id\tgroup\nS1\tA\nS2\tB\n")

    original_recipe_path = _make_recipe(src_dir, recipe_id, data_path)
    loaded = load_data_analysis_recipe(original_recipe_path)

    mode2_cfg, skipped = build_mode2_recipe(loaded.raw, {})
    if t3_translation_skipped is not None:
        skipped = t3_translation_skipped

    data_bytes = data_path.read_bytes()
    if tamper_data:
        data_bytes += b"\nTAMPERED\n"

    sm = SessionManager(tmp_path / "user_data")
    data_batch_hash = sm.compute_data_batch_hash({"T": data_path})

    effective_run = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "data_analysis_recipe_sha256": loaded.data_analysis_recipe_sha256,
        "data_batch_hash": data_batch_hash,
        "t3_audit_steps_sha256": "0" * 64,
        "engine_fingerprint": engine_fingerprint(),
        "containerized": False,
        "image_ref": None,
        "uv_lock_sha256": None,
        "git_commit": "n/a",
        "release_version": "n/a",
        "software_versions": {"python": "3.14"},
        "data_source_paths": {"T": str(data_path)},
        "seeds_per_plot": {},
        "t3_translation_skipped": skipped,
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


def _fresh_bootloader(tmp_path: Path, **kw) -> _FakeBootloader:
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir(parents=True, exist_ok=True)
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


def test_sources_are_repointed_to_extracted_files(tmp_path):
    zb, _run, _orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path)
    result = import_bundle(zb, bootloader=bl)
    written = yaml.safe_load(result.imported_recipe_path.read_text())
    new_path = Path(written["data_schemas"]["T"]["source"]["path"])
    assert new_path.exists()
    assert "_imported" in new_path.parts
    assert new_path.read_text().startswith("sample_id\tgroup")


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


def test_skipped_t3_plots_pass_through(tmp_path):
    zb, _run, _orig = _build_bundle(
        tmp_path, t3_translation_skipped={"p": "untranslatable op"}
    )
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.skipped_t3_plots == {"p": "untranslatable op"}


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
