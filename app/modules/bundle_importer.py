"""app/modules/bundle_importer.py

# @deps
# provides: function:import_bundle, function:read_effective_run, class:ImportResult, class:LegResult, class:BundleImportError
# consumes: app/modules/error_notice.py (notice — VERIF-FIX-2), app/modules/cache_keys.py (engine_fingerprint), app/modules/data_analysis_recipe_validator.py (engine_load_problems — safe ConfigManager probe, ADR-077), app/modules/session_manager.py (SessionManager, LegacySessionError), app/modules/orchestrator.py (DataOrchestrator.get_source_files — the file read is the file hashed), app/src/bootloader.py (get_imports_dir)
# consumed_by: app/handlers/export_handlers.py (define_export_server — Import control in the Export panel), app/tests/test_bundle_importer.py
# note: SessionManager.write_assembly_ghost refuses a record of another format number (LegacySessionError, D-0312); the import is then refused and its files removed
# doc: .claude/knowledge/architecture_decisions.md#ADR-097, .claude/design/reproducible_export_design.md
# @end_deps

Import a reproducibility/reimport bundle (ADR-097, #48/REPRO-IMPORT-1).

Two-Category Law (ADR-045): Pure Python — no Shiny imports. Safe to use from tests,
CLI scripts, and server code.

File-based only (ADR-093): this writes a new recipe file into the recipes directory,
the data files of the bundle into a folder of their own (`<user_data>/_imports/<recipe id>/data/<dataset id>.<ext>`,
found there by dataset id like production data, IMPORT-PATH-1: the recipe's own paths are not touched) and a new
session ghost under _sessions/ — it never injects bundle content into a live
wrangle_studio/home_state object. The imported recipe only becomes selectable after the
app is reloaded (Bootloader resolves available_data_analysis_recipes once per process,
ADR-094) — Import is honest about that rather than pretending to update it live.

Verification is part of import, not a separate step (design doc §4E), and is always
non-blocking: every leg is reported match/mismatch/not_checked, a mismatch never refuses
the import. Four legs (design doc §6d folded the T3-steps leg in after the original
three-leg draft):

  - data        : always checkable — hashed from the files the imported recipe reads, which are the
                  files this bundle carries in data_reproducibility/ (a file the recipe does not name is
                  listed, not hashed; a dataset the recipe names and the bundle lacks is listed as missing).
  - engine      : this machine's installed versions/commit vs. what the bundle recorded.
  - recipe      : only checkable when the ORIGINAL (untranslated) recipe is still
                  available locally by id — the frozen copy inside the bundle has T3
                  baked in by design (and the jitter seeds the export used written on its layers),
                  so it will never hash the same as the original; comparing against it would be
                  a false alarm, not a real check.
  - t3_steps    : not independently re-derivable on import (T3 only ever existed in the
                  exporting session) — recorded for a field-by-field comparison against
                  another effective_run.yaml of the same session (the ADR-097 use case).
"""
from __future__ import annotations

import io
import shutil
import subprocess as _sp
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.modules.cache_keys import engine_fingerprint
from app.modules.data_analysis_recipe_validator import engine_load_problems
from app.modules.error_notice import notice
from app.modules.orchestrator import IMPORT_DATA_FOLDER, DataOrchestrator
from app.modules.session_manager import LegacySessionError, SessionManager


class BundleImportError(ValueError):
    """The zip is not a reproducibility bundle, or lacks what Import needs to proceed."""


@dataclass
class LegResult:
    status: str                 # "match" | "mismatch" | "not_checked"
    recorded: Any = None
    actual: Any = None
    detail: str = ""


@dataclass
class ImportResult:
    recipe_id: str
    imported_recipe_path: Path
    session_key: str
    legs: dict[str, LegResult]
    problems: list[str] = field(default_factory=list)    # what could not be checked because of an error, in plain words (D-0050)


def _find_in_zip(names: list[str], suffix: str) -> str | None:
    matches = [n for n in names if n.endswith(suffix)]
    return matches[0] if matches else None


def _current_git_commit() -> str:
    try:
        return _sp.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=_sp.DEVNULL, text=True,
        ).strip()
    except Exception:
        return "n/a"


def read_effective_run(zip_bytes: bytes) -> dict:
    """Parse effective_run.yaml out of any SPARMVET_VIZ export bundle (Mode 1 or Mode 2)."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        name = _find_in_zip(zf.namelist(), "effective_run.yaml")
        if not name:
            raise BundleImportError(
                "No effective_run.yaml found — this is not a SPARMVET_VIZ export bundle."
            )
        return yaml.safe_load(zf.read(name).decode())


def _data_detail(read: set[str], named: set[str], carried: set[str]) -> str:
    detail = "Hash of the files the imported recipe reads, taken from this bundle's data_reproducibility/ folder."
    missing = sorted(named - read)
    unused = sorted(carried - named)
    if missing:
        detail += f" Missing from the bundle (the recipe names them): {', '.join(missing)}."
    if unused:
        detail += f" Carried by the bundle but not named by the recipe, not hashed: {', '.join(unused)}."
    return detail


def _verify(
    effective_run: dict,
    local_data_batch_hash: str,
    local_recipe_sha256: str | None,
    data_detail: str,
    recipe_problem: str | None = None,
) -> dict[str, LegResult]:
    legs: dict[str, LegResult] = {}

    recorded_data = effective_run.get("data_batch_hash")
    legs["data"] = LegResult(
        status="match" if local_data_batch_hash == recorded_data else "mismatch",
        recorded=recorded_data,
        actual=local_data_batch_hash,
        detail=data_detail,
    )

    recorded_engine = effective_run.get("engine_fingerprint")
    current_engine = engine_fingerprint()
    recorded_commit = effective_run.get("git_commit")
    current_commit = _current_git_commit()
    engine_match = current_engine == recorded_engine and (
        recorded_commit in ("n/a", None) or current_commit == recorded_commit
    )
    legs["engine"] = LegResult(
        status="match" if engine_match else "mismatch",
        recorded=f"{recorded_engine} @ {recorded_commit}",
        actual=f"{current_engine} @ {current_commit}",
        detail=(
            "This machine's installed library versions and commit match the bundle."
            if engine_match else
            "This machine's installed library versions or commit differ from the bundle. "
            "If recipe/data/T3-steps all otherwise match, a results difference is more "
            "likely a software change than an analysis change (ADR-097)."
        ),
    )

    if local_recipe_sha256 is not None:
        recorded_recipe = effective_run.get("data_analysis_recipe_sha256")
        legs["recipe"] = LegResult(
            status="match" if local_recipe_sha256 == recorded_recipe else "mismatch",
            recorded=recorded_recipe,
            actual=local_recipe_sha256,
            detail="Compared against the original (untranslated) recipe found locally by id.",
        )
    elif recipe_problem:
        # a local recipe with this id exists but could not be hashed: the leg is not checked, and the reason is the real one
        legs["recipe"] = LegResult(
            status="not_checked",
            recorded=effective_run.get("data_analysis_recipe_sha256"),
            detail=recipe_problem,
        )
    else:
        legs["recipe"] = LegResult(
            status="not_checked",
            recorded=effective_run.get("data_analysis_recipe_sha256"),
            detail=(
                "Not independently re-checked: the bundle's recipe copy has your audited "
                "T3 steps baked in as real actions and the random scatter (jitter) seeds the "
                "export used written on its layers (listed in effective_run.yaml: "
                "seeds_added_to_recipe), so it never hashes the same as the "
                "original recipe by design, and no original recipe with this id was found "
                "locally to compare against instead."
            ),
        )

    if "audit_steps_sha256" not in effective_run and "t3_audit_steps_sha256" in effective_run:
        # the old key is NOT read as the new one: the hash covers another structure (one list with places, not one list per plot)
        steps_detail = (
            "This bundle was exported by an older version: its audit steps were recorded under another name "
            "and are not compared."
        )
    else:
        steps_detail = (
            "Not independently re-checked on import: T3 audit steps exist only in the "
            "exporting session. Compare this value against another effective_run.yaml of "
            "the same session to confirm the same audited decisions were applied."
        )
    legs["t3_steps"] = LegResult(
        status="not_checked",
        recorded=effective_run.get("audit_steps_sha256"),
        detail=steps_detail,
    )

    return legs


def import_bundle(zip_bytes: bytes, *, bootloader) -> ImportResult:
    """Unpack a Mode 2 bundle: write a new recipe + session ghost, verify what can be
    verified. Never touches live app state (ADR-093)."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        run_name = _find_in_zip(names, "effective_run.yaml")
        if not run_name:
            raise BundleImportError(
                "No effective_run.yaml found — this is not a SPARMVET_VIZ export bundle."
            )
        effective_run = yaml.safe_load(zf.read(run_name).decode())

        # AUDIT-RAWYAML-REMOVE-1: a bundle whose audit record holds a step the app cannot apply is refused before anything is written.
        from app.modules.renamed_keys import refused_audit_step_problem
        for steps_name in (n for n in names if n.endswith("/t3_steps.yaml") or n == "t3_steps.yaml"):
            record = yaml.safe_load(zf.read(steps_name).decode()) or {}
            problem = refused_audit_step_problem(record.get("steps_by_place") or [], f"The bundle's {steps_name}", type_key="action", flat=True, list_name="steps_by_place")
            if problem:
                raise BundleImportError(problem)

        recipe_name = next(
            (n for n in names
             if "/data_analysis_recipes_reproducibility/" in n and n.endswith(".yaml")),
            None,
        )
        if not recipe_name:
            raise BundleImportError(
                "This bundle has no reproducibility recipe "
                "(data_analysis_recipes_reproducibility/) — it was exported without "
                "'Also include a reproducibility/reimport bundle' checked. There is "
                "nothing here that can be re-run; use effective_run.yaml to verify "
                "instead (see Understanding Your Export)."
            )
        frozen_recipe = yaml.safe_load(zf.read(recipe_name).decode())
        original_recipe_id = Path(recipe_name).stem

        data_names: dict[str, str] = {}
        for n in names:
            if "/data_reproducibility/" not in n or n.endswith("_ERROR.txt") or n.endswith("/"):
                continue
            ds_id = Path(n).stem
            if ds_id in data_names:
                raise BundleImportError(
                    f"The bundle carries two files for dataset '{ds_id}' "
                    f"({Path(data_names[ds_id]).name} and {Path(n).name}); one dataset needs one file."
                )
            data_names[ds_id] = n
        if not data_names:
            raise BundleImportError(
                "This bundle's data_reproducibility/ folder is empty or missing — the "
                "recipe copy exists but there is no data to run it against."
            )

        recipes_dir = Path(bootloader.data_analysis_recipes_dir)
        imports_dir = Path(bootloader.get_imports_dir())
        # WHY the counter: two imports of one bundle in the same second must not share an id, a folder or a file.
        now = datetime.now(timezone.utc)
        base_id = f"{original_recipe_id}_imported_{now.strftime('%Y%m%dT%H%M%S')}"
        imported_id, counter = base_id, 2
        while (imports_dir / imported_id).exists() or (recipes_dir / f"{imported_id}.yaml").exists():
            imported_id, counter = f"{base_id}_{counter}", counter + 1

        dest_data_dir = imports_dir / imported_id / IMPORT_DATA_FOLDER
        dest_data_dir.mkdir(parents=True)
        dest_recipe_path = recipes_dir / f"{imported_id}.yaml"
        carried: set[str] = set()
        for ds_id, zname in data_names.items():
            (dest_data_dir / Path(zname).name).write_bytes(zf.read(zname))
            carried.add(ds_id)

    try:
        # The recipe is written as the bundle carried it, only its id follows the file name (ADR-092). Its data paths
        # are not touched: the data is found by dataset id in the folder of this import (DataOrchestrator).
        frozen_recipe["id"] = imported_id
        dest_recipe_path.write_text(
            yaml.safe_dump(frozen_recipe, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

        # Validate before trusting ConfigManager with it: ConfigManager.load() calls
        # sys.exit(1) on a contradictory recipe (ADR-077) — fine at app startup, fatal if it
        # reached a running Shiny process from Import's own call. engine_load_problems()
        # is this project's own established safe wrapper (ADR-094's HOME load gate uses the
        # same pattern) — it intercepts SystemExit and returns problems instead of exiting.
        problems = engine_load_problems(dest_recipe_path)
        if problems:
            raise BundleImportError(
                "The reproducibility recipe inside this bundle could not be loaded: "
                + "; ".join(str(p) for p in problems)
            )
    except BaseException:
        # A refused import leaves nothing behind: no data folder, no recipe file.
        shutil.rmtree(imports_dir / imported_id, ignore_errors=True)
        dest_recipe_path.unlink(missing_ok=True)
        raise

    sm = SessionManager(Path(bootloader.get_location("user_data")))
    if not sm.writable:
        # PROVISIONAL wording: the import must not report a session record that was never stored.
        shutil.rmtree(imports_dir / imported_id, ignore_errors=True)
        dest_recipe_path.unlink(missing_ok=True)
        raise BundleImportError(
            f"The bundle was not imported and nothing was written. {sm.not_writable_text()}")
    local_recipe_sha256_this = sm.compute_data_analysis_recipe_sha256(dest_recipe_path)
    # The files the engine will read for this recipe, found by the one function that also reads them: the hash,
    # the session key and the stored keys of the imported run cover exactly these.
    orchestrator = DataOrchestrator(
        recipes_dir, Path(bootloader.get_location("raw_data")), imports_dir=imports_dir,
    )
    source_files = orchestrator.get_source_files(imported_id)
    named = set(orchestrator.dataset_schemas(imported_id))
    data_batch_hash = sm.compute_data_batch_hash(source_files)
    session_key = sm.compute_session_key(local_recipe_sha256_this, data_batch_hash)
    try:
        sm.write_assembly_ghost(
            session_key=session_key,
            data_analysis_recipe_id=imported_id,
            data_analysis_recipe_sha256=local_recipe_sha256_this,
            data_batch_hash=data_batch_hash,
            source_files={k: str(v) for k, v in source_files.items()},
            parquet_paths={},
        )
    except LegacySessionError as exc:
        # A stored session of another format number under the same key is never written over (D-0312): the import is refused
        # and leaves nothing behind.
        shutil.rmtree(imports_dir / imported_id, ignore_errors=True)
        dest_recipe_path.unlink(missing_ok=True)
        raise BundleImportError(f"The bundle was not imported and nothing was written. {exc}") from exc

    # Recipe leg: only meaningful against the ORIGINAL recipe (not the frozen copy we
    # just wrote, which differs from it by design) — check whether the importing user
    # already has one locally under the same id (e.g. the same repo/recipe set).
    local_recipe_sha256_original: str | None = None
    recipe_problem: str | None = None
    original_path = None
    try:
        original_path = bootloader.available_data_analysis_recipes.get(original_recipe_id)
        if original_path:
            local_recipe_sha256_original = sm.compute_data_analysis_recipe_sha256(Path(original_path))
    except (Exception, SystemExit) as exc:
        # Already startup-vetted (ADR-094) in the normal case; guarded anyway in case the file changed on disk since then
        # (SystemExit: ConfigManager exits on a contradictory recipe). The leg is still "not checked", but the reason is
        # the real one, not "not found" (D-0050).
        local_recipe_sha256_original = None
        reason = f"SystemExit: the recipe loader stopped (code {exc.code})" if isinstance(exc, SystemExit) else exc
        recipe_problem = notice(
            f"The recipe with the id '{original_recipe_id}' on this machine ({original_path}) could not be read, so the "
            "recipe leg was not checked",
            "repair or remove that recipe (Blueprint shows what is wrong with it) and import the bundle again", reason)

    legs = _verify(effective_run, data_batch_hash, local_recipe_sha256_original,
                   _data_detail(set(source_files), named, carried), recipe_problem)

    return ImportResult(
        recipe_id=imported_id,
        imported_recipe_path=dest_recipe_path,
        session_key=session_key,
        legs=legs,
        problems=[recipe_problem] if recipe_problem else [],
    )
