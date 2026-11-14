"""app/modules/bundle_importer.py

# @deps
# provides: function:import_bundle, function:read_effective_run, class:ImportResult, class:LegResult, class:BundleImportError
# consumes: app/modules/cache_keys.py (engine_fingerprint), app/modules/data_analysis_recipe_validator.py (engine_load_problems — safe ConfigManager probe, ADR-077), app/modules/session_manager.py (SessionManager)
# consumed_by: app/handlers/export_handlers.py (define_export_server — Import control in the Export panel)
# doc: .claude/knowledge/architecture_decisions.md#ADR-097, .claude/design/reproducible_export_design.md
# @end_deps

Import a reproducibility/reimport bundle (ADR-097, #48/REPRO-IMPORT-1).

Two-Category Law (ADR-045): Pure Python — no Shiny imports. Safe to use from tests,
CLI scripts, and server code.

File-based only (ADR-093): this writes a new recipe file into the recipes directory
and a new session ghost under _sessions/ — it never injects bundle content into a live
wrangle_studio/home_state object. The imported recipe only becomes selectable after the
app is reloaded (Bootloader resolves available_data_analysis_recipes once per process,
ADR-094) — Import is honest about that rather than pretending to update it live.

Verification is part of import, not a separate step (design doc §4E), and is always
non-blocking: every leg is reported match/mismatch/not_checked, a mismatch never refuses
the import. Four legs (design doc §6d folded the T3-steps leg in after the original
three-leg draft):

  - data        : always checkable — hashed straight from the files this bundle itself
                  carries in data_reproducibility/.
  - engine      : this machine's installed versions/commit vs. what the bundle recorded.
  - recipe      : only checkable when the ORIGINAL (untranslated) recipe is still
                  available locally by id — the frozen copy inside the bundle has T3
                  baked in by design and will never hash the same as the original, so
                  comparing against it would be a false alarm, not a real check.
  - t3_steps    : not independently re-derivable on import (T3 only ever existed in the
                  exporting session) — recorded for a field-by-field comparison against
                  another effective_run.yaml of the same session (the ADR-097 use case).
"""
from __future__ import annotations

import io
import subprocess as _sp
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.modules.cache_keys import engine_fingerprint
from app.modules.data_analysis_recipe_validator import engine_load_problems
from app.modules.session_manager import SessionManager


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
    skipped_t3_plots: dict[str, str] = field(default_factory=dict)


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


def _repoint_sources(recipe: dict, extracted_paths: dict[str, Path]) -> None:
    """Point every data schema's source.path at the file extracted from this bundle.

    The frozen recipe copy still carries the exporting machine's original paths, which
    do not exist here.
    """
    schema_dicts: list[dict] = [recipe.get("data_schemas", {}) or {}]
    if "metadata_schema" in recipe:
        schema_dicts.append({"metadata_schema": recipe["metadata_schema"]})
    schema_dicts.append(recipe.get("additional_datasets_schemas", {}) or {})
    for schemas in schema_dicts:
        for ds_id, schema in schemas.items():
            if ds_id in extracted_paths and isinstance(schema, dict):
                source = schema.setdefault("source", {})
                source["path"] = str(extracted_paths[ds_id])


def _verify(
    effective_run: dict,
    local_data_batch_hash: str,
    local_recipe_sha256: str | None,
) -> dict[str, LegResult]:
    legs: dict[str, LegResult] = {}

    recorded_data = effective_run.get("data_batch_hash")
    legs["data"] = LegResult(
        status="match" if local_data_batch_hash == recorded_data else "mismatch",
        recorded=recorded_data,
        actual=local_data_batch_hash,
        detail="Hash of the data files found inside this bundle's data_reproducibility/ folder.",
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
    else:
        legs["recipe"] = LegResult(
            status="not_checked",
            recorded=effective_run.get("data_analysis_recipe_sha256"),
            detail=(
                "Not independently re-checked: the bundle's recipe copy has your audited "
                "T3 steps baked in as real actions, so it never hashes the same as the "
                "original recipe by design, and no original recipe with this id was found "
                "locally to compare against instead."
            ),
        )

    legs["t3_steps"] = LegResult(
        status="not_checked",
        recorded=effective_run.get("t3_audit_steps_sha256"),
        detail=(
            "Not independently re-checked on import: T3 audit steps exist only in the "
            "exporting session. Compare this value against another effective_run.yaml of "
            "the same session to confirm the same audited decisions were applied."
        ),
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

        data_names = {
            Path(n).stem: n
            for n in names
            if "/data_reproducibility/" in n and not n.endswith("_ERROR.txt")
        }
        if not data_names:
            raise BundleImportError(
                "This bundle's data_reproducibility/ folder is empty or missing — the "
                "recipe copy exists but there is no data to run it against."
            )

        now = datetime.now(timezone.utc)
        imported_id = f"{original_recipe_id}_imported_{now.strftime('%Y%m%dT%H%M%S')}"

        raw_data_dir = Path(bootloader.get_location("raw_data"))
        dest_data_dir = raw_data_dir / "_imported" / imported_id
        dest_data_dir.mkdir(parents=True, exist_ok=True)
        extracted_paths: dict[str, Path] = {}
        for ds_id, zname in data_names.items():
            dest = dest_data_dir / Path(zname).name
            dest.write_bytes(zf.read(zname))
            extracted_paths[ds_id] = dest

    _repoint_sources(frozen_recipe, extracted_paths)
    frozen_recipe["id"] = imported_id

    recipes_dir = Path(bootloader.data_analysis_recipes_dir)
    dest_recipe_path = recipes_dir / f"{imported_id}.yaml"
    dest_recipe_path.write_text(
        yaml.safe_dump(frozen_recipe, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    # Validate before trusting ConfigManager with it: ConfigManager.load() calls
    # sys.exit(1) on a contradictory recipe (ADR-077) — fine at app startup, fatal if it
    # reached a running Shiny process from Import's own call. engine_load_problems()
    # is this project's own established safe wrapper (ADR-094's HOME load gate uses the
    # same pattern) — it intercepts SystemExit and returns problems instead of exiting.
    # IMPORT-PATH-1 (open, a decision of Eve): only the engine's load is checked here, not the strict checker of
    # recipe format 1. `_repoint_sources` writes the ABSOLUTE path of the extracted data into the recipe, and format 1
    # refuses an absolute data path (PA01, DEC30). How the data of an imported bundle is found must be decided first.
    problems = engine_load_problems(dest_recipe_path)
    if problems:
        raise BundleImportError(
            "The reproducibility recipe inside this bundle could not be loaded: "
            + "; ".join(str(p) for p in problems)
        )

    sm = SessionManager(Path(bootloader.get_location("user_data")))
    local_recipe_sha256_this = sm.compute_data_analysis_recipe_sha256(dest_recipe_path)
    data_batch_hash = sm.compute_data_batch_hash(extracted_paths)
    session_key = sm.compute_session_key(local_recipe_sha256_this, data_batch_hash)
    sm.write_assembly_ghost(
        session_key=session_key,
        data_analysis_recipe_id=imported_id,
        data_analysis_recipe_sha256=local_recipe_sha256_this,
        data_batch_hash=data_batch_hash,
        source_files={k: str(v) for k, v in extracted_paths.items()},
        parquet_paths={},
    )

    # Recipe leg: only meaningful against the ORIGINAL recipe (not the frozen copy we
    # just wrote, which differs from it by design) — check whether the importing user
    # already has one locally under the same id (e.g. the same repo/recipe set).
    local_recipe_sha256_original: str | None = None
    try:
        original_path = bootloader.available_data_analysis_recipes.get(original_recipe_id)
        if original_path:
            local_recipe_sha256_original = sm.compute_data_analysis_recipe_sha256(Path(original_path))
    except (Exception, SystemExit):
        # Already startup-vetted (ADR-094) in the normal case; guarded anyway in case the
        # file changed on disk since then — same SystemExit risk as above, never let it
        # reach the caller.
        local_recipe_sha256_original = None

    legs = _verify(effective_run, data_batch_hash, local_recipe_sha256_original)

    skipped = effective_run.get("t3_translation_skipped")
    skipped = skipped if isinstance(skipped, dict) else {}

    return ImportResult(
        recipe_id=imported_id,
        imported_recipe_path=dest_recipe_path,
        session_key=session_key,
        legs=legs,
        skipped_t3_plots=skipped,
    )
