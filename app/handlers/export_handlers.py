"""app/handlers/export_handlers.py
Export pipeline: results bundle (.zip) + audit report (HTML/DOCX) +
system tools sidebar UI.

Extracted from home_theater.py in Phase 24-C (ADR-051).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: constant:EXPORT_READY_TEXTS, constant:EXPORT_PANEL_FIELDS, constant:EXPORT_WATCHED_FIELDS, function:define_export_server, function:tables_no_plot_reads, output:system_tools_ui, output:export_bundle_download, output:import_bundle_report, function:_build_methods_section
# consumes: app/src/www/export_ready.js (D-0270: greys the Export button until the echo of _confirm_export_inputs matches the screen), app/modules/export_fields_store.py (D-0288, D-0291, D-0296: the Export fields remembered per session, in memory only; defaults D-0294), app/modules/error_notice.py (notice — VERIF-FIX-2), app/modules/session_manager.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py, app/modules/audit_places.py (bake_place_steps: the audit steps baked into the reproducibility recipe, place_step_records, place_words, plots_below), libs/utils/src/utils/recipe_tiers.py (plot_targets, schema_bodies: the tables no plot reads, D-0457), app/modules/cache_keys.py (canonical_hash, engine_fingerprint — REPRO-PROV-1; collection_tier2_key: the tier-2 key recorded per table, the same function the orchestrator uses, D-0240; tier2_steps, tier3_steps: which tables and plots have steps; DataAnalysisRecipeKeys.plot_key_of: the key of the table a plot reads), app/modules/bundle_importer.py (import_bundle, BundleImportError — REPRO-IMPORT-1), app/modules/plot_seeds.py (SEED-HOLDS-1), app/modules/plot_issue_reporter.py (plot_warning_text — D-0269), libs/viz_factory/src/viz_factory/checked_plot.py (plot_warnings — D-0269), polars, shiny
# consumes: app/modules/id_check_run.py (run_id_checks, export_log_text: id_log.yaml of the bundle, D-0575, D-0582), libs/utils/src/utils/engines.py (plot_engine_slot — the engine handed to the plot library, D-0237), app/modules/engine_record.py (engine_record, failed_plot_record: the `engines` part of effective_run.yaml, D-0248)
#            reactive.Value:session_processing_issues (DIAG-RUNTIME-AUDIT-1 — included in report.qmd Processing Issues section)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-094 (plot-render error stub now includes the library's fix text), .claude/knowledge/architecture_decisions.md#ADR-097, .claude/design/export_specification.md, .claude/design/reproducible_export_design.md
# @end_deps

import io
import json
import zipfile
from pathlib import Path

from shiny import reactive, render, ui

from app.modules.cache_keys import tier2_steps, tier3_steps
from utils.recipe_tiers import plot_targets, schema_bodies
from app.modules.error_notice import notice, what_failed
from app.modules.export_fields_store import (
    EXPORT_FIELD_DEFAULTS as _FIELD_DEFAULTS, EXPORT_LABEL_DEFAULT, EXPORT_LABEL_FIELD, REMEMBERED_EXPORT_FIELDS,
    ExportFieldsStore,
)
from app.modules.plot_issue_reporter import plot_warning_text
from viz_factory.checked_plot import plot_warnings
from app.modules.export_refusal import export_refusal
from app.modules.id_check_run import export_log_text, id_log_folder, run_id_checks
from app.modules.id_warning import export_sentences, read_status
from utils.id_completion import added_line_words
from app.modules.data_analysis_recipe_validator import export_contact_readme_line, export_contact_record
from app.modules.t3_audit_engine import _op_label, between_prose
from app.modules.audit_view import AUDIT_ERRORS
from app.modules.audit_places import PLACES_BUCKET, audit_recipe_of, audit_recipe_sentence, bake_place_steps, t3_file_sentence, place_step_records, place_words, plots_below, steps_changing_table, place_nodes as _committed_place_nodes_of
from utils.recipe_graph import build_graph
from utils.engines import plot_engine_slot
from app.modules.engine_record import engine_record, failed_plot_record
from utils.fix_text import fix_label
from app.modules.qmd_text import code as _qc, mermaid_label as _qm, plain as _qp, yaml_string as _qy
from app.modules.plot_seeds import (
    bake_plot_seeds, export_seed_plan, seed_recipe_note, seed_sources_per_plot, seeds_added_to_recipe,
    seeds_per_layer_record, seeds_per_plot_record, render_seed_args, with_seed_steps,
)


# ---------------------------------------------------------------------------
# Module-level provenance helpers (headless-safe — no Shiny imports)
# ---------------------------------------------------------------------------

def exported_tiers(*, has_t2: bool, has_t3: bool) -> list:
    """The tiers whose tables are in the bundle, for the README and the report (HOME-WALK F): T1 always, T2 when a dataset of the plots has tier-2 steps
    (the same condition that writes its T2 file), T3 when a plot has audited or tier-3 steps (the same condition that writes its T3 file)."""
    return ["T1"] + (["T2"] if has_t2 else []) + (["T3"] if has_t3 else [])


def tables_no_plot_reads(raw: dict) -> list[str]:
    """The tables of the recipe that no plot reads, in the order of the recipe: its source tables, then its joins (D-0457).

    D-0457, her words: "Must be and yes must be viewabøenin the data preview", to her remark that the export should maybe export all the
    tables included in a recipe even if no plot reads them. The export writes the Tier 1 file of each of these. Only Tier 1 can exist for them:
    the recipe check refuses tier-2 steps on a table or join no plot reads (S07, J14), and a tier 3 is a plot.

    PROVISIONAL (not decided, D-0457 reading to be confirmed): "a table of the recipe" is read as every source table (data schema, metadata,
    additional dataset) and every join that no plot targets directly; a source that a join reads and no plot targets is one of them. The
    narrower readings (joins and unlinked sources only) change this one function and nothing else."""
    targets = plot_targets(raw)
    joins = raw.get("joins") if isinstance(raw, dict) else None
    ids = list(schema_bodies(raw)) + (list(joins) if isinstance(joins, dict) else [])
    return [t for t in dict.fromkeys(ids) if t not in targets]


def build_export_provenance(
    *,
    now,
    data_analysis_recipe_id: str,
    safe_name: str,
    app_features: str,
    preset: str,
    dpi: int,
    plot_width: float = 8.0,
    plot_height: float = 5.0,
    screen_view: str,
    all_plots: list,
    tiers_exported: list,
    data_analysis_recipe_sha: str,
    data_sha: str,
    bootloader,
    stage_keys: dict | None = None,
    plot_keys: dict | None = None,
    orchestrator=None,
    anchor_dir=None,
    t3_by_plot: dict | None = None,
    t3_aesthetic_overrides: dict | None = None,
) -> dict:
    """Collect all export provenance fields for README, QMD, and image metadata.

    ADR-069: all 8 required provenance fields + git info + software versions.
    ADR-097 (REPRO-PROV-1, issue #39): adds the fourth verification leg
    (``t3_audit_steps_sha256``) and an environment-aware engine fingerprint
    (``containerized``/``image_ref`` vs. ``git_commit``/``uv_lock_sha256`` — detected
    automatically, never asked of the user, decision 3). Field names checked against
    RO-Crate's Provenance Run Crate profile (arXiv:2312.07852, W3C-PROV-aligned) where they
    naturally overlap — not full adoption, just aligned naming, so a future move to full
    adoption starts from something traceable.
    Headless-safe: takes plain Python objects, no Shiny imports.
    """
    import hashlib
    import os
    import subprocess as _sp
    import sys

    from app.modules.cache_keys import canonical_hash, engine_fingerprint

    # Git info (EXPORT-VERSION-1)
    git_commit = "n/a"
    release_version = "n/a"
    try:
        git_commit = _sp.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=_sp.DEVNULL, text=True,
        ).strip()
    except Exception:
        pass
    try:
        release_version = _sp.check_output(
            ["git", "describe", "--tags", "--always"],
            stderr=_sp.DEVNULL, text=True,
        ).strip()
    except Exception:
        pass

    # Software versions (EXPORT-AUDIT-COMPLETE-1)
    sw_versions: dict[str, str] = {"python": sys.version.split()[0]}
    for _pkg in ("polars", "shiny", "plotnine"):
        try:
            _mod = __import__(_pkg)
            sw_versions[_pkg] = getattr(_mod, "__version__", "unknown")
        except Exception:
            pass

    # Data analysis recipe info (EXPORT-AUDIT-COMPLETE-1)
    data_analysis_recipe_path_str = "n/a"
    data_analysis_recipe_name = "n/a"
    try:
        _mp = bootloader.available_data_analysis_recipes.get(data_analysis_recipe_id)
        if _mp:
            data_analysis_recipe_path_str = str(_mp)
            data_analysis_recipe_name = Path(str(_mp)).stem
    except Exception:
        pass

    # Data source paths (EXPORT-AUDIT-COMPLETE-1)
    data_source_paths: dict[str, str] = {}
    problems: list[str] = []     # what could not be recorded, in plain words: the caller shows them (D-0050)
    if orchestrator is not None:
        try:
            _src = orchestrator.get_source_files(data_analysis_recipe_id)
            data_source_paths = {k: str(v) for k, v in (_src or {}).items()}
        except Exception as exc:
            problems.append(notice(
                "The paths of the data files could not be read, so this export records no data file paths (and a "
                "reproducibility bundle holds no data files)",
                "reload the page (F5), check that the data folder of the recipe can be read and export again", exc))

    # Decision hashes per dataset from Parquet metadata (EXPORT-HASH-2)
    decision_hashes: dict[str, str] = {}
    if stage_keys:
        # ADR-089: the keys the export itself used (checked against every stored stage), not
        # whatever a parquet file on disk happened to carry before this export refreshed it.
        decision_hashes = {ds: k["tier1_key"] for ds, k in stage_keys.items()}
    elif anchor_dir is not None:
        try:
            from utils.hashing import get_parquet_metadata_hash
            _seen: set[str] = set()
            for _pid, _spec in all_plots:
                _ds = _spec.get("target_dataset")
                if _ds and _ds not in _seen:
                    _seen.add(_ds)
                    _pq = Path(str(anchor_dir)) / f"{_ds}.parquet"
                    if _pq.exists():
                        _h = get_parquet_metadata_hash(str(_pq))
                        if _h:
                            decision_hashes[_ds] = _h
        except Exception:
            pass

    # T3-steps hash — the fourth verification leg (ADR-097 decision 3). Confirmed missing
    # before this: the original ui_implementation_contract.md §12f spec named this exact
    # field and it was never computed anywhere. A snapshot, not a seal — recomputed fresh
    # here every export; T3 itself stays fully editable in the live session (§6d).
    t3_audit_steps_sha256 = canonical_hash({
        "t3_audit_steps_by_plot": t3_by_plot or {},
        "t3_plot_overrides": t3_aesthetic_overrides or {},
    })

    # Engine/environment leg, detected automatically (ADR-097 decision 3 / §6b): a
    # containerized run is identified by the usual Docker/Podman/OCI markers; the
    # SPARMVET_IMAGE_REF env var (set by the image build, not by the app) is the only real
    # pin (a tag is mutable) — recorded as "not set" rather than fabricated when absent, so
    # the gap is visible instead of a false pin. A source-clone run falls back to
    # git_commit (already captured above) plus uv.lock's own content hash, when the file
    # exists — this project has no uv.lock committed yet (checked directly, not assumed),
    # so that field is None today; not a bug, a real limitation to close later (external
    # research: "plan for later, not blocking", ADR-097 §6f).
    containerized = Path("/.dockerenv").exists() or bool(os.environ.get("container"))
    image_ref = os.environ.get("SPARMVET_IMAGE_REF") if containerized else None
    uv_lock_path = Path(__file__).resolve().parents[2] / "uv.lock"
    uv_lock_sha256 = (
        hashlib.sha256(uv_lock_path.read_bytes()).hexdigest() if uv_lock_path.exists() else None
    )

    return {
        "created_at": now.isoformat(),
        "data_analysis_recipe_id": data_analysis_recipe_id,
        "data_analysis_recipe_name": data_analysis_recipe_name,
        "data_analysis_recipe_path": data_analysis_recipe_path_str,
        "app_features": app_features,
        "screen_view": screen_view,
        "bundle_label": safe_name,
        "preset": preset,
        "dpi": dpi,
        "plot_width": plot_width,
        "plot_height": plot_height,
        "plot_count": len(all_plots),
        "tiers_exported": tiers_exported,
        "data_analysis_recipe_sha256": data_analysis_recipe_sha,
        "data_batch_hash": data_sha,
        "decision_hashes": decision_hashes,
        "stage_keys": stage_keys or {},
        # {plot id: key of the table the plot reads}, only for a plot with tier-3 steps in the recipe (its table is not its target's Tier 2)
        "plot_keys": plot_keys or {},
        "git_commit": git_commit,
        "release_version": release_version,
        "software_versions": sw_versions,
        "data_source_paths": data_source_paths,
        "problems": problems,
        # ADR-097 decision 3 — the four verification legs (recipe/data above; engine + T3 here):
        "t3_audit_steps_sha256": t3_audit_steps_sha256,
        "engine_fingerprint": engine_fingerprint(),
        "containerized": containerized,
        "image_ref": image_ref,
        "uv_lock_sha256": uv_lock_sha256,
    }


def changed_since_view(view_keys, current_keys, tables=None) -> list[str]:
    """What changed between the keys the view was built on and the keys now (empty: nothing).

    ADR-089 / EXPORT-KEYCHECK-1. The view is built once per session from the data analysis recipe files and
    the data files; the export recomputes the keys. A difference means a file changed on disk
    after the user opened the view, so what is on screen is not what an export would contain.

    The identity hashes (the recipe file set, all the data files) are compared as before. The third check compares the Tier 1 key of
    each table IN SCOPE (`tables`: the tables the export reads; every table of the view when None), ADR-101.
    """
    changes: list[str] = []
    if view_keys is None or current_keys is None:
        return changes
    if view_keys.data_analysis_recipe_sha256 != current_keys.data_analysis_recipe_sha256:
        changes.append("the data analysis recipe (the data analysis recipe file or a file it includes)")
    if view_keys.data_batch_hash != current_keys.data_batch_hash:
        changes.append("the data files")
    if not changes and any(view_keys.tier1_key_of(t) != current_keys.tier1_key_of(t) for t in _scope_tables(view_keys, tables)):
        changes.append("the processing rules (the engine version or the Tier 1 parts of the data analysis recipe)")
    return changes


def _scope_tables(keys, tables) -> list[str]:
    """The tables whose keys are compared and recorded: those named, else every table the keys hold."""
    return sorted(set(tables)) if tables is not None else sorted(keys.tier1_keys)


def blocked_export_notice(changes: list[str], view_keys, current_keys, during_build: bool = False, tables=None) -> str:
    """Plain-language explanation shown (and written in the bundle) when an export is refused.

    `during_build`: the change was seen while a table of the export was being built (STALE-KEY-STORE-1), so a table of the
    export may mix the files from before and after it."""
    lines = [
        "EXPORT NOT CREATED",
        "",
        "Something changed on disk " + ("while a table of this export was being built: " if during_build
                                        else "after this view was opened: ") + "; ".join(changes) + ".",
        "",
        *(["A table built while its files change can mix the old and the new state, and an export must never hold that without a word.",
           ""] if during_build else []),
        "What it means: the plots and tables on your screen were built from the earlier files. An export",
        "made now would be built from the new files, so it could differ from what you looked at. In a",
        "scientific export that must never happen silently, so nothing was exported.",
        "",
        "What to do:",
        "  1. Reload the page (F5). The view is rebuilt from the current files.",
        "  2. Look at the plots and tables again.",
        "  3. Export again.",
        "",
        "If you did not change any file yourself, find out what did (a pipeline writing new results, a",
        "data analysis recipe edit, a data import) before you trust either version.",
        "",
        "Keys (for the record)",
        f"  view  data analysis recipe {view_keys.data_analysis_recipe_sha256}",
        f"        data     {view_keys.data_batch_hash}",
        *(f"        tier1    {t}: {view_keys.tier1_key_of(t)}" for t in _scope_tables(view_keys, tables)),
        f"  now   data analysis recipe {current_keys.data_analysis_recipe_sha256}",
        f"        data     {current_keys.data_batch_hash}",
        *(f"        tier1    {t}: {current_keys.tier1_key_of(t)}" for t in _scope_tables(current_keys, tables)),
    ]
    return "\n".join(lines)


def blocked_export_zip(text: str) -> bytes:
    """The zip handed to the user in place of an export that is refused: only `EXPORT_NOT_CREATED.txt`."""
    blocked = io.BytesIO()
    with zipfile.ZipFile(blocked, mode="w") as archive:
        archive.writestr("EXPORT_NOT_CREATED.txt", text)
    return blocked.getvalue()


def refusal_for_build_changes(changes: list[str], view_keys, current_keys, notify, tables=None) -> bytes | None:
    """The refusal (zip with only EXPORT_NOT_CREATED.txt, plus the error notification) when a table of the export was built while
    its recipe or data changed, else None. The same refusal as a change since the view; the tables were returned but not stored,
    and the export records the held keys, so nothing may be exported (D-0005: the export refuses when files changed)."""
    if not changes:
        return None
    view_keys = view_keys if view_keys is not None else current_keys     # no view (a headless caller): the keys of this export
    notify("Export blocked: " + "; ".join(changes) + " while a table of this export was being built. "
           "Reload the page (F5), check the plots, then export again.", type="error", duration=None)
    return blocked_export_zip(blocked_export_notice(changes, view_keys, current_keys, during_build=True, tables=tables))


def blocked_audit_notice(failing: list) -> str:
    """Text of `EXPORT_NOT_CREATED.txt` when the audit steps cannot run in their recorded order: the reason of the failure (the audit copy names the step and its place), and the
    plot whose table showed it."""
    lines = ["EXPORT NOT CREATED", "",
             "The audit steps cannot run in the order they were recorded:", ""]
    for plot_id, error in failing:
        lines += [f"Found when the table of the plot '{plot_id}' was built:", str(error), ""]
    lines += ["What it means: the table, the plot and the recipe that the export writes would not agree, or the recipe would stop.",
              "In a scientific export that must never happen silently, so nothing was exported.",
              "",
              "What to do: remove the step named for each plot in its audit list (right panel), check the plots, export again."]
    return "\n".join(lines)


# What is true for a user who has a bundle and wants the figures of its report (VERIF-FIX-2): the pictures are in the folders
# `<table>/plots/`; report.qmd links its figures as `_render/<plot>.<ext>`, a folder that only exists while Quarto renders and is not
# in the bundle. The layout is not changed here (a choice for Eve), the text says what is there.
_NO_FIGURES_REMEDY = (
    "look at the plots in the folders <table>/plots/ of the bundle: report.qmd links its figures to a _render/ folder that is "
    "not in the bundle, so a report rendered by hand from the bundle shows no figures")


def failed_plot_stub(exc: Exception) -> str:
    """The text of `plots/<id>_ERROR.txt`: the message once. The one error form (VIZ-STANDARD-1) already holds the fix, so the
    fix line is added only for an error whose message does not say it."""
    stub = f"Plot render failed:\n{exc}"
    pipeline_error = getattr(exc, "pipeline_error", None)
    if pipeline_error is not None and pipeline_error.fix and pipeline_error.fix not in str(exc):
        stub += f"\n\n{fix_label(pipeline_error.fix, pipeline_error.who)}"
    return stub


def _quote(name) -> str:
    """A file name inside a Markdown link target (a space or a bracket would end the link)."""
    from urllib.parse import quote
    return quote(str(name), safe="")


def export_plot_entries(raw_config: dict) -> list[tuple[str, dict]]:
    """[(plot_id, plot entry)] of the recipe, in the order of its groups: the plots an export draws.

    The entry IS the plot content (D-0237): `target_dataset`, `mapping` and `layers` are written in it, with the app-side keys
    (`ui_label`, `plot_engine`, ...) beside them. An empty entry is not a plot. A recipe with no group falls back to a
    root `plots` mirror (the loader's)."""
    found = [(p_id, entry)
             for gspec in (raw_config.get("analysis_groups") or {}).values()
             for p_id, entry in (gspec.get("plots") or {}).items() if entry]
    return found or list((raw_config.get("plots") or {}).items())


def export_plot_groups(raw_config: dict) -> list[tuple[str | None, list[tuple[str, dict]]]]:
    """[(group ui_label, [(plot_id, plot entry)])] in the order of the groups: the report is built by group (D-0484).

    The label of a group is its `ui_label`, the same text as its tab in HOME (D-0409); the recipe check requires it (G01), so none is invented.
    A group with no plot keeps its place with an empty list, so that the report says it has none. A recipe with no group falls back to the
    root `plots` mirror, which has no group: its label is None."""
    groups = [(g["ui_label"], [(p_id, entry) for p_id, entry in (g.get("plots") or {}).items() if entry])
              for g in (raw_config.get("analysis_groups") or {}).values()]
    if groups:
        return groups
    mirror = list((raw_config.get("plots") or {}).items())
    return [(None, mirror)] if mirror else []


def plot_report_name(entry, p_id: str) -> str:
    """The name of a plot in the report (headings, captions, audit prose): its `ui_label`, the same text as its tab in HOME (D-0409).

    The recipe check requires `ui_label` (P01); a plot that is not in the recipe (an audit step of a plot the recipe no longer has) is
    named by its id as written, never by a text made from it. The text of the figure is not read here: it is written only in the `labs` layer."""
    entry = entry if isinstance(entry, dict) else {}
    return entry.get("ui_label") or p_id


def plot_report_lines(p_id: str, label: str, caption: str, fig_id: str, plot_ext: str, failure: str | None) -> list:
    """The lines of one plot in `report.qmd`: the figure, or, when the plot was not drawn, a note that says so and why.

    A failed plot has no picture in the bundle, so a figure link would be a broken one (VIZ-STANDARD-1)."""
    if failure is None:
        return [f"### {_qp(label)}", "", f"![{caption}](_render/{_quote(p_id)}.{plot_ext}){{#{fig_id} width=95%}}", ""]
    reason = " ".join(str(failure).split())
    return [f"### {_qp(label)}", "", f"> **This plot was not drawn.** {_qp(reason)}  ",
            f"> The same text is in {_qc(f'plots/{p_id}_ERROR.txt')} of its dataset folder.", ""]


def _embed_png_provenance(
    png_bytes: bytes, prov: dict, plot_id: str, dataset_key: str = "", on_problem=None
) -> bytes:
    """Embed provenance as iTXt chunks in PNG bytes (EXPORT-IMG-META-1).

    When the keys cannot be written the picture is returned as it was and `on_problem(exc)` is called (D-0050)."""
    try:
        from PIL import Image, PngImagePlugin
        import io as _io
        img = Image.open(_io.BytesIO(png_bytes))
        info = PngImagePlugin.PngInfo()
        fields = {
            "sparmvet:plot_id": plot_id,
            "sparmvet:data_analysis_recipe_id": prov.get("data_analysis_recipe_id", ""),
            "sparmvet:app_features": prov.get("app_features", ""),
            "sparmvet:data_analysis_recipe_sha256": prov.get("data_analysis_recipe_sha256", ""),
            "sparmvet:data_batch_hash": prov.get("data_batch_hash", ""),
            "sparmvet:decision_hash": prov.get("decision_hashes", {}).get(dataset_key, ""),
            "sparmvet:tier1_key": prov.get("stage_keys", {}).get(dataset_key, {}).get("tier1_key", ""),
            "sparmvet:tier2_key": prov.get("stage_keys", {}).get(dataset_key, {}).get("tier2_key", ""),
            "sparmvet:tier3_key": prov.get("plot_keys", {}).get(plot_id, ""),
            "sparmvet:git_commit": prov.get("git_commit", ""),
            "sparmvet:created_at": prov.get("created_at", ""),
        }
        for k, v in fields.items():
            if v:
                info.add_itxt(k, v)
        out = _io.BytesIO()
        img.save(out, format="PNG", pnginfo=info)
        return out.getvalue()
    except Exception as exc:
        if on_problem is not None:
            on_problem(exc)
        return png_bytes


def _embed_svg_provenance(
    svg_bytes: bytes, prov: dict, plot_id: str, dataset_key: str = "", on_problem=None
) -> bytes:
    """Embed provenance as SVG <metadata> XML block (EXPORT-IMG-META-1).

    When the keys cannot be written the picture is returned as it was and `on_problem(exc)` is called (D-0050)."""
    try:
        import xml.etree.ElementTree as _ET
        _ET.register_namespace("", "http://www.w3.org/2000/svg")
        root = _ET.fromstring(svg_bytes)
        meta_el = _ET.SubElement(root, "metadata")
        meta_el.text = "\n".join([
            f"sparmvet:plot_id={plot_id}",
            f"sparmvet:data_analysis_recipe_id={prov.get('data_analysis_recipe_id', '')}",
            f"sparmvet:app_features={prov.get('app_features', '')}",
            f"sparmvet:data_analysis_recipe_sha256={prov.get('data_analysis_recipe_sha256', '')}",
            f"sparmvet:data_batch_hash={prov.get('data_batch_hash', '')}",
            f"sparmvet:decision_hash={prov.get('decision_hashes', {}).get(dataset_key, '')}",
            f"sparmvet:tier1_key={prov.get('stage_keys', {}).get(dataset_key, {}).get('tier1_key', '')}",
            f"sparmvet:tier2_key={prov.get('stage_keys', {}).get(dataset_key, {}).get('tier2_key', '')}",
            *([f"sparmvet:tier3_key={prov['plot_keys'][plot_id]}"] if plot_id in prov.get("plot_keys", {}) else []),
            f"sparmvet:git_commit={prov.get('git_commit', '')}",
            f"sparmvet:created_at={prov.get('created_at', '')}",
        ])
        return _ET.tostring(root, encoding="unicode").encode("utf-8")
    except Exception as exc:
        if on_problem is not None:
            on_problem(exc)
        return svg_bytes


def _build_methods_section(
    all_plots: list,
    t3_by_plot: dict,
    ds_to_plots: dict,
    tiers_exported: list,
    t3_aesthetic_overrides: dict | None = None,
) -> list[str]:
    """Return QMD lines for the auto-generated Methods section.

    Produces human-readable prose from the audited T3 steps (exploration filters are never exported).
    Returns an empty list when nothing actionable exists so the section is
    omitted rather than appearing empty.
    """
    _op_prose = {
        "eq": "equal to", "ne": "not equal to",
        "gt": "greater than", "ge": "at least",
        "lt": "less than", "le": "at most",
        "in": "one of", "not_in": "not one of",
    }
    _node_verb = {
        "filter_row": "Rows were filtered",
        "exclusion_row": "Rows were explicitly excluded",
        "drop_column": "Column was permanently removed",
        "aesthetic_override": "Plot aesthetics were adjusted",
        "random_seed": "The arrangement of the random points was fixed",
    }

    prose_items: list[str] = []

    # T3 node prose
    for p_id, nodes in (t3_by_plot or {}).items():
        plot_label = _qp(next(
            (plot_report_name(s, p_id) for pid, s in all_plots if pid == p_id),
            p_id,
        ))
        for n in nodes:
            # a step written at a table (bucket `__places__`) says where, and applies to every plot built from there; a step written at a plot's own tier 3 says the plot
            place = n.get("place", "") if p_id == PLACES_BUCKET else ""
            own_plot = place.removeprefix("T3:") if place.startswith("T3:") else None
            at_table = bool(place) and own_plot is None
            if own_plot is not None:
                plot_label = _qp(next((plot_report_name(s, own_plot) for pid, s in all_plots if pid == own_plot), own_plot))
            where = f" (written at {_qp(place_words(n.get('place', '')))}; it applies to every plot built from there)"
            nt = n.get("node_type", "")
            params = n.get("params", {})
            reason = n.get("reason", "").strip()
            verb = _node_verb.get(nt, "An adjustment was applied")

            if nt in ("filter_row", "exclusion_row"):
                col = _qp(params.get("column", "?"))
                op = _qp(_op_prose.get(params.get("op", "eq"), params.get("op", "")))
                val = params.get("value", "")
                val_str = (
                    ", ".join(f'"{_qp(v)}"' for v in val) if isinstance(val, list)
                    else f'"{_qp(val)}"'
                )
                if params.get("op") == "between" and isinstance(val, list) and len(val) == 2:
                    # ADR-104 point 8: the report says which ends of the range were included (an old step: both)
                    detail = f"where **{col}** is " + _qp(between_prose(val, params.get("closed", "both")))
                else:
                    detail = f"where **{col}** is {op} {val_str}"
                # NA-RULE-63: the choice made for the rows with no value in the column (an old step removed them)
                detail += (", keeping the rows with no value in **" + col + "**"
                           if params.get("na") == "keep"
                           else ", removing the rows with no value in **" + col + "**")
                scope = where if at_table else (f" (plot: *{plot_label}*)" if p_id != "__all__" else "")
                sentence = f"{verb} {detail}{scope}."
            elif nt == "drop_column":
                col = _qp(params.get("column", "?"))
                scope = where if at_table else (f" (plot: *{plot_label}*)" if p_id != "__all__" else "")
                sentence = f"Column **{col}** was permanently removed from the exported data{scope}."
            elif nt == "aesthetic_override":
                scope = f" for plot *{plot_label}*"
                sentence = f"Plot aesthetics were adjusted{scope}."
            elif nt == "random_seed":
                sentence = (f"The arrangement of the random points of plot *{plot_label}* was fixed with the seed "
                            f"**{_qp(params.get('seed'))}**.")
            else:
                scope = f" (plot: *{plot_label}*)" if p_id != "__all__" else ""
                sentence = f"{verb}{scope}."

            if reason:
                sentence += f" *Reason: {_qp(reason)}*"
            prose_items.append(sentence)

    # Aesthetic overrides prose (from t3_plot_overrides — stored separately per §12c)
    for p_id, overrides in (t3_aesthetic_overrides or {}).items():
        plot_label = _qp(next(
            (plot_report_name(s, p_id) for pid, s in all_plots if pid == p_id),
            p_id,
        ))
        if overrides:
            keys = [k for k in ("fill", "colour", "alpha", "shape", "size", "theme") if k in overrides]
            if keys:
                detail = _qp(", ".join(keys))
                prose_items.append(
                    f"Plot visual properties ({detail}) were overridden for plot *{plot_label}*."
                )

    if not prose_items:
        return []

    lines = ["## Methods", ""]
    lines.append(
        "The following data preparation and analyst adjustments were applied "
        "prior to export:"
    )
    lines.append("")
    for item in prose_items:
        lines.append(f"- {item}")
    lines.append("")
    return lines


# D-0270: the Export button is ready only when the server holds the values on the screen.
# Every text the user sees about this is here, in one place (PROVISIONAL until Eve has read them).
EXPORT_READY_TEXTS = {
    "waiting": "Getting ready ...",
    "lost": "Your last change may not have been received. Check the box and the label, then press Export.",
}
# The fields of the Export panel the download reads. The page greys the button when one of them changes; the server
# echoes the values it holds for exactly these ids (app/src/www/export_ready.js).
EXPORT_PANEL_FIELDS = (
    "export_user_name", "export_include_reproducibility", "export_preset",
    "export_plot_format", "export_report_format", "export_plot_width", "export_plot_height",
)
# The recipe selector is watched with the Export fields: a change of recipe greys the button at once, and the button opens
# only when the server holds the selector the page shows (F1 of the review: a press right after a switch exported the new
# recipe with the old recipe's field values).
EXPORT_RECIPE_SELECTOR = "data_analysis_recipe_id"
EXPORT_WATCHED_FIELDS = EXPORT_PANEL_FIELDS + (EXPORT_RECIPE_SELECTOR,)
# How long the button waits for the confirmation before it is active again with the notice above (milliseconds).
EXPORT_READY_TIMEOUT_MS = 5000


def define_export_server(input, output, session, *,
                         bootloader, orchestrator, viz_factory,
                         current_app_features, active_cfg,
                         tier1_anchor,
                         screen_view,
                         home_state, safe_input,
                         notification_log=None,
                         session_processing_issues=None,
                         view_keys=None,
                         audited_plot_table=None,
                         in_audit=None,
                         audit_run=None):
    """Register export-bundle + system-tools handlers.

    Reactive deps (kwargs):
      bootloader         : Path Authority (ADR-031)
      orchestrator       : tier1/tier2 materialiser
      viz_factory        : plot renderer
      current_app_features    : reactive.Value[str]
      active_cfg         : reactive.Calc[ConfigManager]
      tier1_anchor       : reactive.Calc[LazyFrame]
      screen_view        : callable() -> str   the mode and the data choice on screen, in words (slice B, P-B6): recorded in README.txt only;
                           the content of the bundle does not depend on it
      home_state         : reactive.Value[dict] | None
      safe_input         : helper (input, key, default) → value
      view_keys          : reactive.Calc[DataAnalysisRecipeKeys]  the keys the open view was built on
      audited_plot_table : callable(plot_id, told) -> LazyFrame | None  the table a plot reads in the audit copy made from the audit steps (any tier)
      in_audit           : callable() -> bool  True in Audit mode (HOME's `_in_audit`): only then the table files also come audited (`audited_table_files`)
      audit_run          : callable(told) -> AuditRun | None  the run of the audit copy (the tables it built); None when no audit step is committed
                           (HOME's `_audited_t3_lf`); None for a plot that lies below no such step. Read whatever the mode on screen is: the export is the Result plus the audit.
    """
    from app.modules.notification_utils import make_notifier
    from app.modules.session_manager import SessionManager
    _notify = make_notifier(notification_log)

    # D-0288, D-0291, D-0296: the Export fields belong to the loaded recipe and its session (recipe plus data batch). They are
    # remembered here while the app runs, one set per session key, in memory only: nothing is written to disk, and a session
    # Restore or import does not touch them. One store per page session, like home_state.
    _fields_store = ExportFieldsStore()
    _shown = {"key": None}      # the session key whose fields the panel was last set to show

    def _session_key() -> str:
        """The session key of the loaded recipe and data (the same rule as the session files); empty until both are known.
        A reactive read of home_state: call it inside `reactive.isolate()` unless the caller wants to follow the session."""
        state = home_state.get() if home_state is not None else {}
        msig = state.get("data_analysis_recipe_sha256") or ""
        dbh = state.get("data_batch_hash") or ""
        return SessionManager.compute_session_key(msig, dbh) if msig and dbh else ""

    @output
    @render.ui
    def system_tools_ui():
        if not bootloader.is_enabled("export_enabled"):
            return ui.div()

        # What the panel shows when it is drawn (first time, or again after a user-space switch): the remembered fields of the
        # session that is loaded now. A switch of user space is the only thing that draws it again (the user space is read
        # here on purpose: Shiny sends an output that is not drawn again as it was last drawn, which would bring back old
        # values the fields were not holding any more). A recipe switch or a plot tab change never draws it again, the
        # effects below set the fields in place (EXPORT-FLAKE-1). The label always starts empty (D-0296).
        safe_input(input, "sidebar_nav", "Home")
        with reactive.isolate():
            remembered = _fields_store.fields_for(_session_key())

        # Reminder (Eve, 2026-11-06): only steps sent to audit are exported. Anything tried while
        # exploring (filters on Source, T1, T2 or T3) is a sandbox and is never part of the bundle.
        audit_reminder = ui.div()
        if bootloader.is_enabled("interactivity_enabled"):
            audit_reminder = ui.tags.small(
                "Only steps sent to audit are exported. Filters you are only exploring with are not.",
                class_="text-muted d-block mb-1",
                style="font-size:0.7em;",
            )

        # Mode 2 add-on (ADR-097 decision 1/#45): opt-in. Every export holds all plots of the recipe (D-0292, D-0295), so
        # the tick changes only what is added to the bundle, never which plots.
        # This output never reads the recipe or the plot tab outside `isolate`: a redraw of the whole panel would put every
        # field back to its default (EXPORT-FLAKE-1, rule R4 of ui_implementation_contract.md section 14, "shell stability
        # pattern" of rules_app_structure.md section 8).
        mode2_toggle = ui.div(
            ui.input_checkbox(
                "export_include_reproducibility",
                "Also include a reproducibility/reimport bundle",
                value=remembered["export_include_reproducibility"],
            ),
            ui.tags.small(
                "The verification record (effective_run.yaml — hashes, seeds, "
                "environment) is always included. Checking this also adds the full "
                "recipe (your audited steps baked in as real wrangling actions) and "
                "the actual data files, so someone can re-run this, not just verify "
                "it. "
                "Check this now if you'll want to Import this bundle later — a bundle "
                "exported without this box checked cannot be imported, only verified "
                "against its effective_run.yaml.",
                class_="text-muted d-block mb-1",
                style="font-size:0.7em;",
            ),
            class_="mb-1",
        )

        return ui.div(
            # REPRO-IMPORT-1 (#48, ADR-097): put Import first and give it its own
            # bold heading — Eve, 2026-11-10, still couldn't find it after it was given
            # a visible label but left buried below ~10 export form fields and an <hr>.
            # This is a different action from configuring an export, so it gets its own
            # clearly-headed block at the top of the panel, not a line at the bottom.
            # GUARDED: test_shiny_smoke.py::TestPhase25Panels::
            # test_import_a_bundle_block_is_findable_above_export_form asserts this Import
            # block renders ABOVE the "Bundle label / name" Export field by actual pixel
            # position, not just DOM presence — mutation-tested against exactly this ordering
            # regressing. If you reorder these two blocks, that test will fail; update it
            # deliberately, don't just delete it.
            ui.div(
                ui.tags.div(
                    "⬇ Import a bundle",
                    style="font-weight:700;font-size:0.85em;margin-bottom:4px;",
                ),
                ui.input_file(
                    "import_bundle_upload", "Reproducibility bundle (.zip)",
                    accept=[".zip"], multiple=False,
                ),
                ui.tags.small(
                    "Only a bundle exported with 'Also include a reproducibility/reimport "
                    "bundle' checked (below) can be imported. Verifies what it can against "
                    "this machine, per leg, and writes a new recipe + session (never into "
                    "the live app, ADR-093). Reload (F5) afterwards to see it in the Data "
                    "analysis recipe selector.",
                    class_="text-muted d-block mb-1",
                    style="font-size:0.7em;",
                ),
                ui.output_ui("import_bundle_report"),
                class_="upload-row",
                style="background:#f8f9fa;border-radius:4px;padding:6px 8px;margin-bottom:8px;",
            ),
            ui.hr(class_="my-2"),
            ui.div(
                ui.tags.div(
                    "⬆ Export",
                    style="font-weight:700;font-size:0.85em;margin-bottom:4px;",
                ),
                ui.input_text(
                    "export_user_name", label="Bundle label / name",
                    placeholder="label (no spaces, no special characters)…",
                    value=EXPORT_LABEL_DEFAULT,
                ),
                mode2_toggle,
                ui.input_radio_buttons(
                    "export_preset",
                    label="Quality",
                    choices={"web": "Web / Presentation", "publication": "Publication (≥600 DPI)"},
                    selected=remembered["export_preset"],
                    inline=False,
                ),
                ui.input_radio_buttons(
                    "export_plot_format",
                    label="Plot format",
                    choices={"png": "PNG", "svg": "SVG", "pdf": "PDF"},
                    selected=remembered["export_plot_format"],
                    inline=True,
                ),
                ui.tags.small(
                    "SVG is resolution-independent — rescale or convert to any dimension or format without quality loss.",
                    class_="text-muted d-block mb-1",
                    style="font-size:0.7em;",
                ),
                ui.input_radio_buttons(
                    "export_report_format",
                    label="Report format",
                    choices={"html": "HTML", "pdf": "PDF", "docx": "DOCX"},
                    selected=remembered["export_report_format"],
                    inline=True,
                ),
                ui.div(
                    ui.tags.label("Plot size (inches)", class_="d-block mb-1"),
                    ui.div(
                        ui.input_numeric("export_plot_width",  "W", value=remembered["export_plot_width"],  min=2, max=30, step=0.5),
                        ui.input_numeric("export_plot_height", "H", value=remembered["export_plot_height"], min=2, max=30, step=0.5),
                        class_="d-flex gap-2",
                    ),
                    class_="mb-1",
                ),
                audit_reminder,
                # The one line about the log of the ids (D-0582): a slot of its own, so that a change of the warning never draws this panel's fields again (R4).
                ui.output_ui("export_id_warning_ui"),
                ui.download_button(
                    "export_bundle_download",
                    "💾 Export Bundle",
                    class_="btn-success btn-sm w-100 mt-1",
                ),
                class_="mb-2 px-2",
                style="font-size:0.8em;",
                id="export_ready_panel",
                **{
                    "data-ready-fields": json.dumps(list(EXPORT_WATCHED_FIELDS)),
                    "data-remember-fields": json.dumps(list(REMEMBERED_EXPORT_FIELDS)),
                    "data-text-waiting": EXPORT_READY_TEXTS["waiting"],
                    "data-text-lost": EXPORT_READY_TEXTS["lost"],
                    "data-timeout-ms": str(EXPORT_READY_TIMEOUT_MS),
                },
            ),
            class_="px-2",
            style="font-size:0.8em;"
        )

    # The session key as a value of its own, so that what follows it runs when the KEY changes and not at every other change of
    # home_state (a filter, a tab): each run tells the page and greys the button.
    _key_now = reactive.Value("")

    @reactive.Effect
    def _follow_the_session_key():
        key = _session_key()
        with reactive.isolate():
            if _key_now.get() != key:
                _key_now.set(key)

    @reactive.effect(priority=-50)
    async def _tell_the_page_its_session():
        """Tell the page which session its Export fields belong to, and with the fields when the session changed (D-0288, D-0296).

        Runs when the session key changes, after every change of the recipe selector (after the work of that change, which has
        priority 0, so the key it sets is final), and when the page asks (it missed the message at load). The message carries
        the key and, when the session changed, the session's remembered fields with an empty label; the page puts them in the
        panel and takes the key in one step, so the key and the values it shows never part. The panel is not drawn again for
        this (EXPORT-FLAKE-1). Nothing here reads the Export inputs: the server's copy of them is whatever the page last sent,
        which is what the echo below compares with the screen (D-0270)."""
        if not bootloader.is_enabled("export_enabled"):
            return
        safe_input(input, EXPORT_RECIPE_SELECTOR, None)     # a dependency: the work of a recipe switch is done when this runs
        safe_input(input, "export_page_ready", 0)           # a dependency: the page asks again after its handlers exist
        key = _key_now.get()
        with reactive.isolate():
            changed = key != _shown["key"]
            _shown["key"] = key
            message = {"key": key}
            if changed and key:
                _fields_store.begin_session(key)
                message["values"] = {**_fields_store.fields_for(key), EXPORT_LABEL_FIELD: EXPORT_LABEL_DEFAULT}
        await session.send_custom_message("export_session", message)

    @reactive.effect(priority=-100)
    async def _confirm_export_inputs():
        """Tell the page which values of the Export panel the server holds, and for which session (D-0270).

        Runs after every change of a field and after every ping of the page (`export_client_ping`, sent at each change,
        so that a change that leaves the values as they were is confirmed too). It reads every field the download reads, and
        the recipe selector, and sends them back with the last ping it has seen and the session the server shows; the page
        opens the Export button when the key is the one the page was told last and the values equal what is on the screen.
        Its priority is below the effect that tells the page its session, so in one round of work the page is told first.
        This effect runs after the input messages were applied, so a download pressed after the echo reads the same values
        (the race of question 20: input messages are applied under the reactive lock, a download request is handled without
        it)."""
        if not bootloader.is_enabled("export_enabled"):
            return
        ping = safe_input(input, "export_client_ping", 0)
        held = {}
        for field in EXPORT_WATCHED_FIELDS:
            try:
                held[field] = getattr(input, field)()
            except Exception:
                continue    # a field that is not on the page: the page skips it too
        with reactive.isolate():
            key = _shown["key"] or ""
        await session.send_custom_message("export_ready_echo", {"ping": ping, "key": key, "values": held})

    @reactive.Effect
    @reactive.event(input.export_field_change)
    def _remember_what_the_page_shows():
        """Remember a choice the user made, under the session the PAGE says it was showing when the user made it (D-0288).

        The page sends the key it was last told with each change. The key that is current when the report arrives may be another
        one (two quick recipe switches), and writing the value there would store one session's choice under the other (F2 of the
        review). A report for a key the server never announced is dropped; the page then gets the fields of the real session
        from the message above, so the user sees what the server holds and nothing is lost unseen (D-0050)."""
        if not bootloader.is_enabled("export_enabled"):
            return
        report = input.export_field_change() or {}
        key = str(report.get("key") or "")
        value = report.get("value")
        if value is None:
            return          # an empty number box is not a choice
        try:
            stored = _fields_store.remember(key, report.get("field"), value)
        except ValueError as error:
            _notify(f"An Export choice could not be remembered: {error}", type="error", duration=10)
            return
        if not stored and key:
            _notify("An Export choice was made for a session this app did not announce and was not remembered: check the Export "
                    "fields before you export.", type="warning", duration=10)

    # ── REPRO-IMPORT-1 (#48, ADR-097): import + per-leg verification ────────────
    _import_bundle_state = reactive.Value(None)   # ("error", str) | ("ok", ImportResult) | None

    @reactive.Effect
    @reactive.event(input.import_bundle_upload)
    def _handle_import_bundle_upload():
        file_info = input.import_bundle_upload()
        if not file_info:
            return
        from app.modules.bundle_importer import BundleImportError, import_bundle
        try:
            zip_bytes = Path(file_info[0]["datapath"]).read_bytes()
            result = import_bundle(zip_bytes, bootloader=bootloader)
        except BundleImportError as e:
            _import_bundle_state.set(("error", str(e)))
            _notify(f"❌ Import failed: {e}", type="error", duration=10)
            return
        except Exception as e:
            _import_bundle_state.set(("error", str(e)))
            _notify(f"❌ Import failed unexpectedly: {e}", type="error", duration=10)
            return
        _import_bundle_state.set(("ok", result))
        n_mismatch = sum(1 for leg in result.legs.values() if leg.status == "mismatch")
        problems = list(getattr(result, "problems", None) or [])
        _notify(
            f"✅ Imported as '{result.recipe_id}'. "
            + (f"{n_mismatch} leg(s) mismatch — see the report below." if n_mismatch
               else "A leg could not be checked — see the next message." if problems
               else "All checked legs match.")
            + " Reload the app (F5) to see it in the Data analysis recipe selector.",
            type="warning" if (n_mismatch or problems) else "message", duration=12,
        )
        for problem in problems:
            _notify("⚠️ " + problem, type="warning", duration=12)

    @output
    @render.ui
    def import_bundle_report():
        state = _import_bundle_state.get()
        if state is None:
            return ui.div()
        kind, payload = state
        if kind == "error":
            return ui.div(
                ui.tags.b("Import failed", style="color:#d62828;"),
                ui.tags.div(payload, style="font-size:0.85em;"),
                style=(
                    "background:#ffe0e0;color:#d62828;border-radius:4px;"
                    "padding:6px 8px;margin-top:4px;"
                ),
            )

        result = payload
        _leg_color = {"match": "#0b6358", "mismatch": "#d62828", "not_checked": "#6c757d"}
        rows = [
            ui.div(
                ui.tags.b(leg_name.replace("_", " "), style=f"color:{_leg_color[leg.status]};"),
                f": {leg.status.replace('_', ' ')}",
                ui.tags.br(),
                ui.tags.span(leg.detail, class_="text-muted", style="font-size:0.95em;"),
                class_="mb-1",
            )
            for leg_name, leg in result.legs.items()
        ]
        skipped_note = (
            ui.tags.small(
                f"{len(result.skipped_t3_plots)} plot(s)' T3 steps were not translated into "
                "replayable actions when this bundle was exported (see the plot names in "
                "effective_run.yaml's t3_translation_skipped).",
                class_="text-muted d-block mt-1",
            )
            if result.skipped_t3_plots else ui.div()
        )
        return ui.div(
            ui.tags.small(
                f"Imported as '{result.recipe_id}' — reload (F5) to see it in the selector.",
                class_="d-block mb-1", style="font-weight:600;",
            ),
            *rows,
            skipped_note,
            class_="mt-1",
        )

    @render.download(filename=lambda: _export_bundle_filename())
    async def export_bundle_download():
        """
        Phase 21-I: Export Results Bundle.

        Produces a zip file containing (ADR-097, #45 — Publication content, never the
        recipe or raw data; see effective_run.yaml below for the shared verification
        record, and the optional Mode 2 add-on for the recipe/data themselves):
        - plots/          one picture per plot, in the plot format of the panel (SVG by default, D-0294)
        - data/           T1 TSV for each dataset referenced by active plots, and for each table that no plot reads (D-0457)
        - t3_steps.yaml   human-readable audit record backing the Methods prose (when T3 has steps)
        - effective_run.yaml   the four verification hashes, per-plot seeds, environment —
                          written identically whether or not Mode 2 is checked
        - report.qmd      Quarto source report embedding all plots and datasets
        - README.txt      Bundle data analysis recipe (timestamp, data analysis recipe, app features, preset)
        - data_analysis_recipes_reproducibility/, data_reproducibility/  — only when the
          "Also include a reproducibility/reimport bundle" box is checked: the frozen
          recipe (T3 baked in) and the actual data files
        """
        import io
        import zipfile
        import tempfile
        import datetime
        import copy

        now = datetime.datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        raw_name = safe_input(input, "export_user_name", "user").strip() or "user"
        # Sanitize: replace spaces/special chars with underscore, lowercase
        import re
        safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", raw_name)[:40]
        preset = safe_input(input, "export_preset", _FIELD_DEFAULTS["export_preset"])
        plot_fmt = safe_input(input, "export_plot_format", _FIELD_DEFAULTS["export_plot_format"])
        report_fmt = safe_input(input, "export_report_format", _FIELD_DEFAULTS["export_report_format"])
        plot_width  = float(safe_input(input, "export_plot_width",  _FIELD_DEFAULTS["export_plot_width"]))
        plot_height = float(safe_input(input, "export_plot_height", _FIELD_DEFAULTS["export_plot_height"]))
        app_features = current_app_features.get()
        dpi = 300 if preset == "web" else 600

        data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
        try:
            cfg = active_cfg()
            # ADR-089: one set of chained keys for the whole export; every stored stage is checked
            # against it instead of being reused by file name.
            export_keys = orchestrator.compute_data_analysis_recipe_keys(data_analysis_recipe_id)
            _unreadable = None
        except (ValueError, FileNotFoundError) as _error:  # GATE-GAP-1: the recipe cannot be read any more
            _unreadable = _error
        with reactive.isolate():
            _refusal = export_refusal(bootloader, data_analysis_recipe_id, _unreadable, _notify)
        if _refusal is not None:
            yield _refusal
            return

        # EXPORT-KEYCHECK-1: the keys of the open view must equal the keys now. If a data analysis recipe or
        # data file changed after the view was opened, refuse: what is exported must be what the
        # user looked at.
        with reactive.isolate():
            _view = view_keys() if view_keys is not None else None
        # The tables in scope: the collections the plots of this export read (every export holds all plots of the recipe), and the tables no plot reads.
        # D-0457: it also reads the tables no plot reads (their Tier 1 file is in the bundle), so their keys are checked too.
        _unread_tables = tables_no_plot_reads(cfg.raw_config)
        _scope_tables_now = sorted({_s.get("target_dataset") for _, _s in export_plot_entries(cfg.raw_config) if _s.get("target_dataset")}
                                   | set(_unread_tables))
        _changes = changed_since_view(_view, export_keys, _scope_tables_now)
        if _changes:
            _text = blocked_export_notice(_changes, _view, export_keys, tables=_scope_tables_now)
            with reactive.isolate():
                _notify("Export blocked: " + "; ".join(_changes) + " changed since this view was opened. "
                        "Reload the page (F5), check the plots, then export again.",
                        type="error", duration=None)
            yield blocked_export_zip(_text)
            return

        # A table of this export built while its recipe or data changed is returned but not stored: the orchestrator tells
        # through this list, and the export is refused at the end (STALE-KEY-STORE-1, D-0005, D-0050).
        _build_changes: list[str] = []

        def _on_build_change(change):
            if change.text not in _build_changes:
                _build_changes.append(change.text)

        groups = cfg.raw_config.get("analysis_groups", {})

        # Collect all (plot_id, entry) pairs for this export
        all_plots = export_plot_entries(cfg.raw_config)

        # ── Mode 2 add-on (ADR-097 decision 1, #45): Publication content (plots,
        # report, T3 justification) is always built, unchanged — this is additive, not
        # a second, separate "reproducibility-only" bundle that suppresses it. That
        # stricter split (and whether Mode 1 keeps its current full recipe copy once
        # this exists) stays an open question, not resolved here. Every export holds
        # ALL plots of the recipe, with or without the box (D-0292, D-0295).
        wants_mode2 = bool(safe_input(input, "export_include_reproducibility", False))

        # ── SEED-HOLDS-1 (ADR-104 point 3, ADR-097 decision 2): one seed per random layer of each plot ──
        # audit pin > the number the recipe writes on that layer > the factory's seed (0) when it writes none.
        # HOME draws no seed and a recipe cannot ask for a random one (S1).
        # The plot is rendered with these seeds, the record holds them, and the reproducibility recipe carries them.
        # The pin is read from home_state with no audit-trail flag in between (plot_seeds.export_seed_plan):
        # Reshuffle is not gated by it, so the export holds what the user saw.
        with reactive.isolate():
            _home_state_now = home_state.get() if home_state is not None else None
        _plot_seeds = export_seed_plan(
            dict(all_plots), _home_state_now, default=viz_factory.default_random_state,
            recipe_default=(cfg.raw_config.get("plot_defaults") or {}).get("random_state"),
        )

        # ── Collect the audit data: every audit step at every tier is one node written at a place (`T1:<table>`, `T2:<table>`, `T3:<plot>`) ──────────
        # t3_plot_overrides: resolved aesthetic state per plot (separate from the audit steps: it is a plot's own style and seed pin, not a step on data)
        _t3_aesthetic_overrides: dict[str, dict] = {}
        if home_state is not None and bootloader.is_enabled("t3_sandbox_enabled"):
            _overrides_all = home_state.get().get("t3_plot_overrides", {}) or {}
            for _pid, _ in all_plots:
                _subtab = f"subtab_{_pid}"
                if _subtab in _overrides_all and _overrides_all[_subtab]:
                    _t3_aesthetic_overrides[_pid] = _overrides_all[_subtab]

        # The audit steps (demo steps 4 and 7): one step is one record, always applied to every plot built from its place (its own tier 3 or a table above it).
        _place_nodes_all: list[dict] = []
        _place_records: list[dict] = []
        _place_plot_ids: set[str] = set()
        if home_state is not None and bootloader.is_enabled("t3_sandbox_enabled"):
            _place_nodes_all = _committed_place_nodes_of(home_state.get().get("t3_audit_steps_by_plot", {}) or {})
            if _place_nodes_all:
                _graph = build_graph(cfg.raw_config)
                _place_records = place_step_records(_graph, _place_nodes_all)
                _place_plot_ids = {p for rec in _place_records for p in rec["plots"]}

        def _read_plot_table(p_id: str):
            """The table a plot reads, lazy: the audited one when an audit step is written at a table upstream of it, else its own table (`materialize_tier3`). The ONE read of the
            export: the plot, its data file and the check before the export read it, as HOME's plot and T3 table do."""
            if _place_nodes_all and audited_plot_table is not None:
                with reactive.isolate():
                    audited = audited_plot_table(p_id, _on_build_change)   # a build whose inputs changed refuses the export, as for every other table
                if audited is not None:
                    return audited
            return orchestrator.materialize_tier3(
                data_analysis_recipe_id=data_analysis_recipe_id, plot_id=p_id,
                anchors_dir=bootloader.get_location("user_data") / "anchors", keys=export_keys,
                on_inputs_changed=_on_build_change)

        # AUDITED TABLE FILES (owner, 2026-11-24; PROVISIONAL form): an export made in Audit mode also writes, for every table an audit step changes (the table of the place and
        # every table built from it), the audited table at each tier beside the original: `T1_data_audited.tsv`, `T2_data_audited.tsv`. A table no step changes has only its
        # original file. In Exploration mode the table files stay the originals, as before (the steps still change the plots and `T3_data_<plot>.tsv`, never these files).
        _audited_table_files: dict[str, dict] = {}     # table -> {"T1": DataFrame, "T2": DataFrame (a tier the table is not changed at is absent), "changed_by": {"T1": [nodes], "T2": [nodes]}}
        _audit_now = False
        if _place_nodes_all and in_audit is not None and audit_run is not None:
            with reactive.isolate():
                _audit_now = bool(in_audit())
            if _audit_now:
                try:
                    with reactive.isolate():
                        _run = audit_run(lambda change: _on_build_change(change))
                except AUDIT_ERRORS:
                    _run = None        # the audit steps cannot run: the check before anything is written (below) refuses the export with the reason; nothing is written here
                if _run is not None:
                    for _table, _frames in _run.audited_frames().items():
                        _audited_table_files[_table] = {
                            **_frames, "changed_by": {_tier: steps_changing_table(_graph, _place_nodes_all, _table, _tier) for _tier in ("T1", "T2")}}

        def _audited_file_sentences(written: dict, original_t2: set) -> list[str]:
            """One sentence per audited table file that is in the bundle: which file is which and which steps made the difference (PROVISIONAL words). `original_t2`: the tables
            whose original tier 2 is a file of its own (a table with no tier-2 steps has none: its tier 2 is its tier 1)."""
            out: list[str] = []
            for (table, tier), folder in written.items():
                ids = ", ".join(f"{n.get('id')} (at {place_words(n.get('place', ''))})" for n in _audited_table_files[table]["changed_by"][tier]) or "none listed"
                original = (f"{folder}/{tier}_data.tsv is the original, as the recipe builds it" if tier == "T1" or table in original_t2
                            else f"the original tier 2 of this table is its tier 1 ({folder}/T1_data.tsv: the recipe has no tier-2 step for it)")
                out.append(f"{folder}/{tier}_data_audited.tsv is the {tier} table of '{table}' with the audit steps applied; {original}. Steps that made the difference: {ids}.")
            return out

        # The audit pin of a plot (Reshuffle, or an audit override) is a step of the audit trail too, whatever the
        # audit-trail flag: listed in t3_steps.yaml, the Methods text and the report's audit table, and hashed.
        _t3_listed = with_seed_steps({}, _plot_seeds)

        # The export is the Result (T2) plus the AUDITED T3 steps (committed with a reason, e.g.
        # removing poor quality data): the user's decision for the publication, always applied.
        # Exploration (filters tried on any table of the view, not sent to audit) is a sandbox and is never
        # exported, from any view (Eve, 2026-11-06). What was on screen (the mode and the data choice) is recorded in README.txt
        # and decides nothing in the bundle: the content below never reads it.
        screen_view_text = screen_view()

        # The plots an audit step reaches (at their own tier 3 or at a table above them). The plots whose table is not their target's Tier 2 as it is: the user
        # audited them, or the recipe writes tier-3 steps for them. Each has its own T3 data file in the bundle (the plot is drawn from it).
        audited_plots = {p for p, _ in all_plots if p in _place_plot_ids}
        recipe_t3_plots = {p for p, _ in all_plots if tier3_steps(cfg.raw_config, p)}      # the plots whose recipe writes tier-3 steps of its own (the table of such a plot is part of the Result)
        t3_table_plots = audited_plots | recipe_t3_plots

        # PLOT-TABLE-ORDER-1: check before anything is written. If the audit steps cannot run (in their recorded order, tier 1, tier 2, tier 3), the table, the plot
        # and the exported recipe would differ or fail: nothing is exported. The one read of the export builds the audit copy, which names the step and its place.
        def _base_frame(p_id: str, spec: dict):
            """The table a plot reads: `_read_plot_table` (the table of the audit copy when an audit step reaches it, else `materialize_tier3`), as the data and plot sections read it."""
            if not spec.get("target_dataset"):
                return tier1_anchor()
            return _read_plot_table(p_id)

        # The audit copy is built and run once for the whole recipe, so the first plot an audit step reaches shows the failure of the run (a step that cannot be applied
        # names itself and its place): there is one error to tell, not one per plot.
        _failing: list[tuple[str, Exception]] = []
        for _p, _s in all_plots:
            if _p not in audited_plots:
                continue
            try:
                _base_frame(_p, _s).collect_schema()
            except AUDIT_ERRORS as _error:
                _failing.append((_p, _error))
                break
        if _failing:
            with reactive.isolate():
                _notify("Export blocked: the audit steps cannot run for " + ", ".join(f"'{_p}'" for _p, _ in _failing)
                        + ". " + " ".join(str(_e) for _, _e in _failing), type="error", duration=None)
            _blocked = io.BytesIO()
            with zipfile.ZipFile(_blocked, mode="w") as _bz:
                _bz.writestr("EXPORT_NOT_CREATED.txt", blocked_audit_notice(_failing))
            yield _blocked.getvalue()
            return

        # Dataset → plots mapping (used for folder structure + README + report)
        import re as _re
        def _safe_ds_name(ds_key: str) -> str:
            return _re.sub(r"[^A-Za-z0-9_-]", "_", ds_key)

        ds_to_plots: dict[str, list[str]] = {}
        for p_id, spec in all_plots:
            ds_key = spec.get("target_dataset") or "__anchor__"
            ds_to_plots.setdefault(ds_key, []).append(p_id)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            bundle_dir = f"{ts}_{safe_name}"

            # ── Hashes + Provenance (before tmpdir so image embedding can use it) ──
            # The keys of this export (ADR-089): the file-set hash of the data analysis recipe, the content
            # hash of the data, and the chained key of every stored stage the export reads.
            data_analysis_recipe_sha = export_keys.data_analysis_recipe_sha256
            data_sha = export_keys.data_batch_hash
            stage_keys: dict[str, dict[str, str]] = {}
            for _p, _spec in all_plots:
                _ds = _spec.get("target_dataset")
                if _ds and _ds not in stage_keys:
                    stage_keys[_ds] = {
                        "tier1_key": export_keys.tier1_key_of(_ds),
                        # the key of the Tier 2 table (the keys object makes it with the one function that makes a tier-2 key from a
                        # recipe: steps and engine); the record keeps its words for a table with no tier-2 steps: empty, "none (T2 equals T1)"
                        "tier2_key": export_keys.tier2_key_of(_ds) if tier2_steps(cfg.raw_config, _ds) else "",
                    }
            # D-0457: the tables no plot reads are recorded the same way (their Tier 1 file is in the bundle); their Tier 2 key is empty because
            # the recipe check refuses tier-2 steps on a table no plot reads (S07, J14)
            for _ds in _unread_tables:
                stage_keys.setdefault(_ds, {
                    "tier1_key": export_keys.tier1_key_of(_ds),
                    "tier2_key": export_keys.tier2_key_of(_ds) if tier2_steps(cfg.raw_config, _ds) else "",
                })
            # the key of the table a plot reads, only for a plot that has tier-3 steps (a plot with none reads its table: that is the key above)
            plot_keys = {_p: export_keys.plot_key_of(_p) for _p, _spec in all_plots
                         if _spec.get("target_dataset") and tier3_steps(cfg.raw_config, _p)}

            tiers_exported = exported_tiers(has_t2=any(_k["tier2_key"] for _k in stage_keys.values()), has_t3=bool(t3_table_plots))
            anchor_dir = bootloader.get_location("user_data") / "anchors"

            prov = build_export_provenance(
                now=now,
                data_analysis_recipe_id=data_analysis_recipe_id,
                safe_name=safe_name,
                app_features=app_features,
                preset=preset,
                dpi=dpi,
                plot_width=plot_width,
                plot_height=plot_height,
                screen_view=screen_view_text,
                all_plots=all_plots,
                tiers_exported=tiers_exported,
                data_analysis_recipe_sha=data_analysis_recipe_sha,
                data_sha=data_sha,
                bootloader=bootloader,
                stage_keys=stage_keys,
                plot_keys=plot_keys,
                orchestrator=orchestrator,
                anchor_dir=anchor_dir,
                t3_by_plot={**_t3_listed, PLACES_BUCKET: _place_nodes_all} if _place_nodes_all else _t3_listed,
                t3_aesthetic_overrides=_t3_aesthetic_overrides,
            )
            # The notices of the build are held and shown only when the bundle is handed over: an export that is refused
            # (the files changed) hands over a zip with the refusal only, and a text about a bundle nobody receives would mislead.
            _deferred: list[tuple[str, str, int]] = []

            def _later(text: str, type_: str = "warning", duration: int = 12) -> None:
                _deferred.append((text, type_, duration))

            for _prov_problem in prov.get("problems", []):
                _later("⚠️ " + _prov_problem)

            # Parts of this export that are replaced by a `*_ERROR.txt` file inside the zip (D-0050: the user is told on
            # screen too, once, when the export is finished) and pictures that could not take the keys.
            _unwritten: list[tuple[str, str, str]] = []
            _t3_written: set[tuple[str, str]] = set()      # (dataset key, plot) of every T3_data_<plot>.tsv that is in the zip
            _picture_failures: list[tuple[str, Exception]] = []

            def _lost(what: str, exc) -> None:
                """Remember a part that was replaced by a `*_ERROR.txt`. The library's own error carries its remedy apart from
                its problem (`pipeline_error`): the reason is the problem only, the remedy is kept for the Suggestion: list."""
                record = getattr(exc, "pipeline_error", None)
                if record is not None and getattr(record, "problem", ""):
                    reason, fix = f"{type(exc).__name__}: {' '.join(record.problem.split())}", (record.fix or "")
                else:
                    reason, fix = f"{type(exc).__name__}: {' '.join(str(exc).split()) or 'no message'}", ""
                _unwritten.append((what, reason, fix))

            # ── Render and save plots ─────────────────────────────────────
            # plot_bytes  → zip's plots/   in the user's chosen format (always).
            # qmd_plot_bytes → _render/    in a Quarto-compatible format.
            #
            # _QUARTO_NATIVE_PLOT_FMTS is the extension point: when adding a new
            # output format (epub, revealjs, …) add one entry here.
            # SVG in PDF output depends on rsvg-convert being available at runtime.
            import shutil as _shutil
            _has_rsvg = _shutil.which("rsvg-convert") is not None
            _QUARTO_NATIVE_PLOT_FMTS: dict[str, set[str]] = {
                # report_fmt → plot formats Quarto can embed natively
                "html":  {"png", "svg", "jpg", "gif", "webp"},
                "pdf":   {"png", "jpg", "pdf"} | ({"svg"} if _has_rsvg else set()),
                "docx":  {"png", "svg", "jpg", "emf"},
            }
            # Per-output fallback format when the user's plot format isn't native.
            # DOCX uses SVG (vector, crisp at any zoom) instead of PNG.
            # PDF and HTML fall back to PNG.
            _QUARTO_PLOT_FALLBACK: dict[str, str] = {
                "html": "png",
                "pdf":  "png",
                "docx": "svg",
            }
            _native = _QUARTO_NATIVE_PLOT_FMTS.get(report_fmt, {plot_fmt})
            _fallback = _QUARTO_PLOT_FALLBACK.get(report_fmt, "png")
            qmd_plot_fmt = plot_fmt if plot_fmt in _native else _fallback
            plot_bytes: dict[str, bytes] = {}      # p_id → bytes (user format)
            qmd_plot_bytes: dict[str, bytes] = {}  # p_id → bytes for Quarto (_render/)
            # D-0269: the warnings of every picture this export draws (a missing font ...), per plot, whether or not the plot
            # was shown in HOME. The same words as HOME's Alerts panel (plot_warning_text).
            _plot_warning_rows: dict[str, list[dict]] = {}
            _warnings_unreadable: list[str] = []
            failed_plots: dict[str, str] = {}      # p_id → why it was not drawn (the report says so, no figure link)
            drawn_records: dict[str, dict] = {}    # p_id → the engine and the theme of the plot as it was drawn (effective_run.yaml, D-0248)
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                _audited_written: dict[tuple[str, str], str] = {}     # (table, "T1"/"T2") -> the folder of the audited file that is in the zip

                def _write_audited(table: str, folder: str, tier: str) -> None:
                    """The audited table of `table` at `tier` beside its original (only in an export made in Audit mode, only for a table an audit step changes)."""
                    frame = (_audited_table_files.get(table) or {}).get(tier)
                    if frame is None:
                        return
                    try:
                        path = tmpdir_path / f"{folder}_{tier}_audited.tsv"
                        frame.write_csv(str(path), separator="\t")
                        with open(path, "rb") as f:
                            zf.writestr(f"{bundle_dir}/{folder}/{tier}_data_audited.tsv", f.read())
                        _audited_written[(table, tier)] = folder
                    except Exception as e:
                        _lost(f"the audited {tier} data of '{table}'", e)
                        zf.writestr(f"{bundle_dir}/{folder}/{tier}_data_audited_ERROR.txt", f"Audited {tier} data export failed:\n{e}")

                for p_id, spec in all_plots:
                    _ds_key = spec.get("target_dataset") or "__anchor__"
                    _safe_ds = _safe_ds_name(_ds_key)
                    try:
                        # Build synthetic data analysis recipe with applied filters
                        plot_spec = copy.deepcopy(spec)
                        synthetic_data_analysis_recipe = {
                            "plots": {p_id: plot_spec},
                            "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
                            # the recipe's default engine; the dispatcher reads the plot's own (D-0237)
                            **plot_engine_slot(cfg.raw_config),
                        }

                        # Resolve dataset
                        target_ds = spec.get("target_dataset")
                        if target_ds:
                            anchor_dir = bootloader.get_location("user_data") / "anchors"
                            out_path = anchor_dir / f"{target_ds}.parquet"
                            # Plots never show T1 (ADR-086): same base as HOME, the table the plot reads: the stored
                            # Tier 2 (equal to T1 when the table has no tier2 steps) plus the plot's own tier-3 steps.
                            lf = _read_plot_table(p_id)
                        else:
                            lf = tier1_anchor()

                        # lf is the table of the audit copy when an audit step reaches the plot: the same table as HOME's table and plot

                        # VIZFAC-T3-EXPORT-1: pass L5 aesthetic_override so
                        # exported plots reflect analyst T3 overrides.
                        _plot_override = _t3_aesthetic_overrides.get(p_id)
                        fig = viz_factory.render(lf, synthetic_data_analysis_recipe, p_id,
                                                 **render_seed_args(_plot_seeds[p_id], _plot_override))
                        # the record comes from the plot that was just drawn, by the dispatcher that drew it (D-0248)
                        drawn_records[p_id] = viz_factory.record_of(fig, synthetic_data_analysis_recipe, p_id)
                        # WHY: a failure to read the warnings must not lose the picture; it is named in the bundle
                        try:
                            _found = plot_warnings(fig)
                        except Exception:
                            _found = []
                            _warnings_unreadable.append(p_id)
                        if _found:
                            _plot_warning_rows[p_id] = [
                                {"text": plot_warning_text(w), "problem": w.problem, "fix": w.fix,
                                 "component": w.component, "location": w.location} for w in _found]

                        # Save user-chosen format → zip under {dataset}/plots/
                        plot_path = tmpdir_path / f"{p_id}.{plot_fmt}"
                        fig.save(str(plot_path), verbose=False,
                                 format=plot_fmt, dpi=dpi,
                                 width=plot_width, height=plot_height)

                        with open(plot_path, "rb") as f:
                            raw = f.read()
                        # EXPORT-IMG-META-1: embed provenance in image bytes
                        _no_keys = lambda exc, _p=p_id: _picture_failures.append((_p, exc))   # noqa: E731
                        if plot_fmt == "png":
                            raw = _embed_png_provenance(raw, prov, p_id, _ds_key, on_problem=_no_keys)
                        elif plot_fmt == "svg":
                            raw = _embed_svg_provenance(raw, prov, p_id, _ds_key, on_problem=_no_keys)
                        plot_bytes[p_id] = raw
                        zf.writestr(f"{bundle_dir}/{_safe_ds}/plots/{p_id}.{plot_fmt}", raw)

                        # When SVG plots + PDF report: also render PNG for Quarto
                        # (LuaLaTeX cannot embed SVGs without rsvg-convert)
                        if qmd_plot_fmt != plot_fmt:
                            qmd_path = tmpdir_path / f"{p_id}.{qmd_plot_fmt}"
                            fig.save(str(qmd_path), verbose=False,
                                     format=qmd_plot_fmt, dpi=dpi,
                                     width=plot_width, height=plot_height)
                            with open(qmd_path, "rb") as f:
                                qmd_plot_bytes[p_id] = f.read()
                        else:
                            qmd_plot_bytes[p_id] = raw

                    except Exception as e:
                        # Write error stub so bundle is still complete. ADR-094/
                        # PIPELINE-ERROR-WIRE-2: include the library's real fix text when
                        # the exception carries one (errors.py pipeline_error= kwarg) --
                        # detection without guidance in a file nobody can ask a follow-up
                        # question about is worse than in a live UI.
                        failed_plots[p_id] = str(e)
                        drawn_records[p_id] = failed_plot_record(cfg.raw_config, spec, e)
                        _lost(f"the plot '{p_id}'", e)
                        zf.writestr(
                            f"{bundle_dir}/{_safe_ds}/plots/{p_id}_ERROR.txt",
                            failed_plot_stub(e),
                        )

                if _picture_failures:
                    _names = ", ".join(f"'{_p}'" for _p, _ in _picture_failures[:8]) + (
                        f" and {len(_picture_failures) - 8} more" if len(_picture_failures) > 8 else "")
                    _later("⚠️ " + notice(
                        f"The recipe and data keys could not be written into {len(_picture_failures)} picture(s) ({_names}), "
                        "so those files carry no keys",
                        "the keys of this export are in README.txt, report.qmd and effective_run.yaml of the bundle; export "
                        "again if you need them inside the pictures", _picture_failures[0][1]))

                # ── Export data by tier ───────────────────────────────────
                # T1: always exported.
                # T2: exported when the table has tier2 steps (a join, or a table a plot reads directly), read from the stored Tier 2
                #     parquet (issue #10). Without tier2 steps T2 equals T1: no duplicate TSV.
                # T3: one file per plot that has audited steps or tier-3 steps in the recipe (its plot is built from that data);
                #     whatever the mode and the data choice on screen when Export was pressed (they decide nothing here).

                exported_datasets: set[str] = set()
                exported_t2: set[str] = set()
                exported_dfs: dict[str, "pl.DataFrame"] = {}  # ds_key → T1 DataFrame for report
                for p_id, spec in all_plots:
                    target_ds = spec.get("target_dataset")
                    ds_key = target_ds or "__tier1_anchor__"
                    if ds_key in exported_datasets:
                        continue
                    exported_datasets.add(ds_key)

                    safe_ds = _safe_ds_name(ds_key)

                    # ── T1 ────────────────────────────────────────────────
                    try:
                        if target_ds:
                            anchor_dir = bootloader.get_location("user_data") / "anchors"
                            out_path = anchor_dir / f"{target_ds}.parquet"
                            lf_t1 = orchestrator.materialize_tier1(
                                data_analysis_recipe_id=data_analysis_recipe_id,
                                collection_id=target_ds,
                                output_path=out_path,
                                keys=export_keys,
                                on_inputs_changed=_on_build_change,
                            )
                        else:
                            lf_t1 = tier1_anchor()
                        df_t1 = lf_t1.collect()
                        exported_dfs[ds_key] = df_t1
                        tsv_path = tmpdir_path / f"{safe_ds}_T1.tsv"
                        df_t1.write_csv(str(tsv_path), separator="\t")
                        with open(tsv_path, "rb") as f:
                            zf.writestr(f"{bundle_dir}/{safe_ds}/T1_data.tsv", f.read())
                    except Exception as e:
                        _lost(f"the T1 data of '{ds_key}'", e)
                        zf.writestr(
                            f"{bundle_dir}/{safe_ds}/T1_data_ERROR.txt",
                            f"T1 data export failed:\n{e}"
                        )
                    _write_audited(ds_key, safe_ds, "T1")

                    # ── T2 (exported when tier2 steps exist) ───────
                    try:
                        if target_ds and tier2_steps(active_cfg().raw_config, target_ds):
                            lf_t2 = orchestrator.materialize_tier2(
                                data_analysis_recipe_id=data_analysis_recipe_id,
                                collection_id=target_ds,
                                tier1_path=bootloader.get_location("user_data") / "anchors" / f"{target_ds}.parquet",
                                keys=export_keys,
                                on_inputs_changed=_on_build_change,
                            )
                            df_t2 = lf_t2.collect()
                            tsv_path = tmpdir_path / f"{safe_ds}_T2.tsv"
                            df_t2.write_csv(str(tsv_path), separator="\t")
                            with open(tsv_path, "rb") as f:
                                zf.writestr(f"{bundle_dir}/{safe_ds}/T2_data.tsv", f.read())
                            exported_t2.add(ds_key)
                    except Exception as e:
                        _lost(f"the T2 data of '{ds_key}'", e)
                        zf.writestr(
                            f"{bundle_dir}/{safe_ds}/T2_data_ERROR.txt",
                            f"T2 data export failed:\n{e}"
                        )
                    _write_audited(ds_key, safe_ds, "T2")

                    # ── T3 data (the audited table), one file per plot (audit nodes are per plot) ──
                    # Build rule T3 > T2 > T1: the base is the table the plot reads (`materialize_tier3`: the stored Tier 2, which
                    # is Tier 1 when the table has no tier2 steps, plus the plot's own tier-3 steps of the recipe); the plot's
                    # audited filters and drops go on top.
                    # Written for every plot that has audited steps or tier-3 steps in the recipe: its plot is built from this
                    # data, so the file must be there. Other plots have no T3 file (their plot reads T2).
                    if t3_table_plots:
                        for _t3_pid, _t3_spec in all_plots:
                            if (_t3_spec.get("target_dataset") or "__tier1_anchor__") != ds_key:
                                continue
                            if _t3_pid not in t3_table_plots:
                                continue
                            try:
                                if target_ds:
                                    lf_t3 = _read_plot_table(_t3_pid)
                                else:
                                    lf_t3 = tier1_anchor()
                                tsv_path = tmpdir_path / f"{safe_ds}_T3_{_t3_pid}.tsv"
                                lf_t3.collect().write_csv(str(tsv_path), separator="\t")
                                with open(tsv_path, "rb") as f:
                                    zf.writestr(f"{bundle_dir}/{safe_ds}/T3_data_{_t3_pid}.tsv", f.read())
                                _t3_written.add((ds_key, _t3_pid))
                            except Exception as e:
                                _lost(f"the audited data of the plot '{_t3_pid}'", e)
                                zf.writestr(
                                    f"{bundle_dir}/{safe_ds}/T3_data_{_t3_pid}_ERROR.txt",
                                    f"T3 data export failed:\n{e}"
                                )

                # ── Tables that no plot reads (D-0457): their Tier 1 file, read as the others are read (the orchestrator, the keys of
                # this export), and nothing else: no Tier 2 and no Tier 3 can exist for a table no plot reads (S07, J14), no audit step is
                # written at such a table here (HOME writes audit steps only at a plot's table), exploration is never exported (D-0327).
                # PROVISIONAL (not decided, D-0457 reading to be confirmed): which tables these are is `tables_no_plot_reads`.
                unread_rows: dict[str, dict] = {}          # table -> {"folder", "rows", "columns", "error"} for README and report
                _folders_used = {_safe_ds_name(_k) for _k in exported_datasets}
                for ds_key in _unread_tables:
                    safe_ds = _safe_ds_name(ds_key)
                    _n = 2
                    while safe_ds in _folders_used:       # two table ids that give one folder name stay two folders
                        safe_ds = f"{_safe_ds_name(ds_key)}_{_n}"
                        _n += 1
                    _folders_used.add(safe_ds)
                    try:
                        lf_t1 = orchestrator.materialize_tier1(
                            data_analysis_recipe_id=data_analysis_recipe_id,
                            collection_id=ds_key,
                            output_path=bootloader.get_location("user_data") / "anchors" / f"{ds_key}.parquet",
                            keys=export_keys,
                            on_inputs_changed=_on_build_change,
                        )
                        df_t1 = lf_t1.collect()
                        tsv_path = tmpdir_path / f"{safe_ds}_T1.tsv"
                        df_t1.write_csv(str(tsv_path), separator="\t")
                        with open(tsv_path, "rb") as f:
                            zf.writestr(f"{bundle_dir}/{safe_ds}/T1_data.tsv", f.read())
                        unread_rows[ds_key] = {"folder": safe_ds, "rows": df_t1.height, "columns": len(df_t1.columns), "error": None}
                        _write_audited(ds_key, safe_ds, "T1")
                    except Exception as e:
                        _lost(f"the T1 data of '{ds_key}' (a table no plot reads)", e)
                        zf.writestr(
                            f"{bundle_dir}/{safe_ds}/T1_data_ERROR.txt",
                            f"T1 data export failed:\n{e}"
                        )
                        unread_rows[ds_key] = {"folder": safe_ds, "rows": None, "columns": None, "error": str(e)}

                # ── t3_steps.yaml (when T3 has committed changes) — Mode 1 content: the
                # human-readable audit record backing the Methods prose, not the recipe. ──
                if _t3_listed or _t3_aesthetic_overrides or _place_records:
                    try:
                        import yaml as _yaml
                        t3_steps_data = {
                            "generated": now.isoformat(),
                            "t3_steps": {
                                _pid: [
                                    {
                                        "action": n.get("node_type", "unknown"),
                                        **n.get("params", {}),
                                        "reason": n.get("reason", ""),
                                        "committed_at": n.get("created_at", ""),
                                    }
                                    for n in _nodes
                                ]
                                for _pid, _nodes in _t3_listed.items()
                            },
                        }
                        # the audit steps, at every tier: where each is written (a table's tier 1 or tier 2, a plot's tier 3), its reason and the plots built from there
                        if _place_records:
                            t3_steps_data["steps_by_place"] = [
                                {"id": r["id"], "written_at": r["place"], "written_at_words": r["place_words"], "started_from_plot": r["started_from"],
                                 "action": r["action"], **r["params"], "reason": r["reason"], "committed_at": r["committed_at"],
                                 "plots_built_from_it": r["plots"]}
                                for r in _place_records
                            ]
                        # Aesthetic overrides are stored separately from audit step (§12c)
                        # the seed is listed as a step above, not a second time here
                        _overrides_listed = {
                            _pid: {k: v for k, v in _ov.items() if k != "random_state"}
                            for _pid, _ov in _t3_aesthetic_overrides.items()
                        }
                        _overrides_listed = {_pid: _ov for _pid, _ov in _overrides_listed.items() if _ov}
                        if _overrides_listed:
                            t3_steps_data["t3_aesthetic_overrides"] = _overrides_listed
                        zf.writestr(
                            f"{bundle_dir}/t3_steps.yaml",
                            _yaml.safe_dump(t3_steps_data, sort_keys=False, allow_unicode=True),
                        )
                    except Exception as e:
                        _lost("t3_steps.yaml (the audit steps with their reasons)", e)
                        zf.writestr(f"{bundle_dir}/t3_steps_ERROR.txt", str(e))

            # ── The AUDIT RECIPE (D-0622, D-0535; PROVISIONAL form): an export made in Audit mode holds the original recipe with every audit step at its place and its reason, as an ordinary
            # recipe that the app opens and runs on its own (`audit_recipe/<id>_audited.yaml`, one file with the includes resolved, the same data references as the original). Written with no tick,
            # as the audited table files are (D-0619). A step that cannot be written as an action stops this part with a notice and an ERROR.txt, never left out.
            audit_recipe_file = ""
            audit_recipe_failed = False
            if _audit_now and _place_nodes_all:
                try:
                    import yaml as _yaml_audit
                    _audit_recipe = audit_recipe_of(cfg.raw_config, _place_nodes_all, data_analysis_recipe_id, now.strftime("%Y-%m-%d"))
                    _audit_recipe = bake_plot_seeds(_audit_recipe, _plot_seeds)
                    audit_recipe_file = f"audit_recipe/{_audit_recipe['id']}.yaml"
                    zf.writestr(f"{bundle_dir}/{audit_recipe_file}", _yaml_audit.safe_dump(_audit_recipe, sort_keys=False, allow_unicode=True))
                except Exception as e:
                    audit_recipe_failed = True
                    zf.writestr(f"{bundle_dir}/audit_recipe/ERROR.txt", str(e))
                    _lost("the audit recipe (the recipe with the audit steps at their places)", e)
                    _later("⚠️ " + notice(
                        "The audit recipe of this export could not be written, so the bundle holds no recipe that gives the audited tables again (its reason is in audit_recipe/ERROR.txt)",
                        "the rest of the bundle is complete; fix the cause and export again", e), duration=15)

            # ── Mode 2 add-on: the heavy, Mode-2-exclusive content (ADR-097, #45) ──
            # Recipe + actual data files. Additive to everything above, never a
            # replacement — Mode 1's content is unchanged regardless of this checkbox.
            # effective_run.yaml itself is NOT here — it is written unconditionally
            # below, since both modes need the exact same file to be comparable
            # (Eve, 2026-11-09): "if they differ means mode 1 and mode 2 not equal".
            # What the README says about the reproducibility part (D-0050): "built", "failed" (ERROR.txt only) or
            # "incomplete" (built, but data files that could not be copied are `*_ERROR.txt` files).
            repro_status = "built"
            repro_missing_files: list[str] = []
            if wants_mode2:
                try:
                    import yaml as _yaml

                    # every audit step goes into the steps of its own place (the tier 1 or tier 2 of a table, the tier 3 of a plot), so that the recipe alone, run by the engine
                    # with no audit machinery, builds the audited tables and plots; a step that cannot be written as an action stops the part (below), it is never left out
                    mode2_cfg = bake_place_steps(cfg.raw_config, _place_nodes_all)
                    # SEED-HOLDS-1: the seed each plot was exported with is written into this recipe, so the
                    # re-run draws the same arrangement (the recipe is the scientific document).
                    mode2_cfg = bake_plot_seeds(mode2_cfg, _plot_seeds)
                    zf.writestr(
                        f"{bundle_dir}/data_analysis_recipes_reproducibility/{data_analysis_recipe_id}.yaml",
                        _yaml.safe_dump(mode2_cfg, sort_keys=False, allow_unicode=True),
                    )

                    # Actual data files, not just a hash reference — Eve: "needs all to be
                    # fully reproducible". Sensitive-data handling is #46, not built here.
                    for _ds_id, _src_path in prov.get("data_source_paths", {}).items():
                        try:
                            _src = Path(_src_path)
                            with open(_src, "rb") as f:
                                zf.writestr(
                                    f"{bundle_dir}/data_reproducibility/{_ds_id}{_src.suffix}",
                                    f.read(),
                                )
                        except Exception as e:
                            _lost(f"the data file '{_ds_id}' of the reproducibility bundle", e)
                            repro_missing_files.append(str(_ds_id))
                            zf.writestr(
                                f"{bundle_dir}/data_reproducibility/{_ds_id}_ERROR.txt", str(e)
                            )
                    # REPRO-SENSITIVE-1 (#46): this bundle now carries the actual raw data
                    # files, not just hashes of them — it is meant to be shared/moved (e.g.
                    # attached to a paper submission or handed to a collaborator). Say so
                    # every time, non-blocking (the user may have already anonymised the
                    # data before loading it, in which case this is a no-op reminder).
                    if repro_missing_files:
                        repro_status = "incomplete"
                        _repro_head = (
                            "Reproducibility part: included, but INCOMPLETE (the recipe is there; the data file(s) "
                            f"{', '.join(repro_missing_files)} could not be copied, see the *_ERROR.txt files in "
                            "data_reproducibility/). "
                        )
                    else:
                        _repro_head = "Reproducibility part: included (the full recipe and the data files). "
                    with reactive.isolate():
                        _notify(
                            _repro_head +
                            "This reproducibility bundle includes your actual raw data "
                            "files, not just hashes — anyone who gets the bundle gets the "
                            "data. If it contains sensitive information, anonymise it "
                            "before sharing or archiving (see the user guide: "
                            "Understanding Your Export).",
                            type="warning", duration=12,
                        )
                except Exception as e:
                    zf.writestr(
                        f"{bundle_dir}/data_analysis_recipes_reproducibility/ERROR.txt", str(e)
                    )
                    repro_status = "failed"
                    _later("⚠️ " + notice(
                        "The reproducibility part of this export could not be built, so the bundle holds no recipe and no "
                        "data files for a re-run (its reason is in data_analysis_recipes_reproducibility/ERROR.txt)",
                        "the rest of the bundle is complete, but do not use it to re-run the analysis; fix the cause and "
                        "export again with the reproducibility box ticked", e), duration=15)

            # ── effective_run.yaml — written UNCONDITIONALLY, identical content either
            # way, bundle root (ADR-097, #45 corrected scope, Eve 2026-11-09): the single
            # shared, machine-comparable file both modes carry, so two bundles exported
            # SEPARATELY (Mode 1 today, Mode 2 next week) can be proven to match — or, if
            # they differ, show exactly which field differs (recipe/data/T3-steps changed
            # vs. only engine_fingerprint/git_commit changed, i.e. a software update
            # explains a result difference, not a problem with the analysis). Comparison
            # is per-field, not a single collapsed code and not eyeball-only — #48's
            # per-leg verify logic is the actual comparison tool.
            import yaml as _yaml
            _contact = export_contact_record(
                (cfg.raw_config.get("info") if isinstance(cfg.raw_config.get("info"), dict) else None),
                bootloader.get_contact(),
            )
            effective_run = {
                "_about": (
                    "Retrospective provenance for this export (field names checked "
                    "against RO-Crate's Provenance Run Crate profile, arXiv:2312.07852, "
                    "where they naturally overlap) — what was actually used, not just "
                    "what the recipe declares as its default. Written identically by "
                    "Publication and Reproducibility exports — compare two separately "
                    "exported copies field by field to confirm they're the same analysis."
                ),
                "generated": now.isoformat(),
                "data_analysis_recipe_sha256": prov["data_analysis_recipe_sha256"],
                "data_batch_hash": prov["data_batch_hash"],
                "t3_audit_steps_sha256": prov["t3_audit_steps_sha256"],
                "engine_fingerprint": prov["engine_fingerprint"],
                "containerized": prov["containerized"],
                "image_ref": prov["image_ref"],
                "uv_lock_sha256": prov["uv_lock_sha256"],
                "git_commit": prov["git_commit"],
                "release_version": prov["release_version"],
                "contact": _contact["contact"],
                "contact_source": _contact["contact_source"],
                "software_versions": prov["software_versions"],
                "data_source_paths": prov["data_source_paths"],
                # the engine of each tier and plot, the theme as applied, the versions of the libraries behind them (D-0248):
                # the Publication export carries no recipe, so this is the only place the engine of the export is written
                "engines": engine_record(cfg.raw_config, all_plots, drawn_records),
                "seeds_per_plot": seeds_per_plot_record(_plot_seeds),
                "seed_source_per_plot": seed_sources_per_plot(_plot_seeds),
                "seeds_per_layer": seeds_per_layer_record(_plot_seeds),
                "seeds_added_to_recipe": seeds_added_to_recipe(_plot_seeds, dict(all_plots)),
                "plot_warnings": _plot_warning_rows,
                "plot_warnings_unreadable": list(_warnings_unreadable),
            }
            zf.writestr(
                f"{bundle_dir}/effective_run.yaml",
                _yaml.safe_dump(effective_run, sort_keys=False, allow_unicode=True),
            )

            # data_analysis_recipe_sha, data_sha, tiers_exported, prov — all computed before tmpdir block.

            # ── Lineage graph (ADR-074) ───────────────────────────────────
            # Shared-node DAG: one lineage_graph.json per export.
            # Nodes are deduplicated by schema_id+type so datasets shared
            # across multiple plots appear only once.
            _lineage_nodes: dict[str, dict] = {}
            _lineage_edges: set[tuple[str, str]] = set()
            _lineage_per_plot: dict[str, list[str]] = {}
            _lineage_ok = False
            try:
                from blueprint_arch.data_analysis_recipe_navigator import (
                    build_plot_lineage as _bpl,
                    recipe_structure_of_file as _rsf,
                )
                _mnf_path_obj = bootloader.available_data_analysis_recipes.get(data_analysis_recipe_id)
                if _mnf_path_obj:
                    _mnf_str = str(_mnf_path_obj)
                    _mnf_structure = _rsf(_mnf_str)  # the recipe is loaded once for all plots
                    for _pid, _pspec in all_plots:
                        _steps = _bpl(_pid, _mnf_str, _mnf_structure)
                        if not _steps:
                            continue
                        _plot_nids: list[str] = []
                        for _s in _steps:
                            _nid = f"{_s['schema_id']}__{_s['type']}"
                            if _nid not in _lineage_nodes:
                                _lineage_nodes[_nid] = {
                                    "id": _nid,
                                    "type": _s["type"],
                                    "schema_id": _s["schema_id"],
                                    "label": _s["label"],
                                    "rel": _s.get("rel", ""),
                                }
                            _plot_nids.append(_nid)
                        _lineage_per_plot[_pid] = _plot_nids
                        # Derive DAG edges from step sequence.
                        # Gateway = first join node (if present) else plot_spec.
                        # All data_source / wrangling nodes connect into the gateway.
                        _join_s = next(
                            (_s for _s in _steps if _s["type"] == "join"), None
                        )
                        _plot_s = next(
                            (_s for _s in _steps if _s["type"] == "plot_spec"), None
                        )
                        _gw = _join_s or _plot_s
                        _ei = 0
                        while _ei < len(_steps):
                            _es = _steps[_ei]
                            _en = f"{_es['schema_id']}__{_es['type']}"
                            if _es["type"] == "data_source":
                                _nxt = _steps[_ei + 1] if _ei + 1 < len(_steps) else None
                                if (
                                    _nxt
                                    and _nxt["type"] == "wrangling"
                                    and _nxt["schema_id"] == _es["schema_id"]
                                ):
                                    _wn = f"{_nxt['schema_id']}__{_nxt['type']}"
                                    _lineage_edges.add((_en, _wn))
                                    if _gw:
                                        _gwn = f"{_gw['schema_id']}__{_gw['type']}"
                                        if _wn != _gwn:
                                            _lineage_edges.add((_wn, _gwn))
                                    _ei += 2
                                else:
                                    if _gw:
                                        _gwn = f"{_gw['schema_id']}__{_gw['type']}"
                                        if _en != _gwn:
                                            _lineage_edges.add((_en, _gwn))
                                    _ei += 1
                            elif _es["type"] == "join" and _plot_s:
                                _lineage_edges.add(
                                    (_en, f"{_plot_s['schema_id']}__{_plot_s['type']}")
                                )
                                _ei += 1
                            else:
                                _ei += 1

                    if _lineage_nodes:
                        import json as _json
                        _graph_payload = {
                            "generated": now.isoformat(),
                            "nodes": list(_lineage_nodes.values()),
                            "edges": [
                                {"from": _f, "to": _t}
                                for _f, _t in sorted(_lineage_edges)
                            ],
                            "plot_ids": [_p for _p, _ in all_plots],
                            "lineage_per_plot": _lineage_per_plot,
                            "description": (
                                "Shared-node directed acyclic graph (DAG) of the data "
                                "lineage for this export. "
                                "Nodes are deduplicated by schema_id+type — a dataset "
                                "shared by multiple plots appears only once. "
                                "Edge direction: upstream → downstream "
                                "(data_source → wrangling → join → plot_spec)."
                            ),
                        }
                        zf.writestr(
                            f"{bundle_dir}/lineage/lineage_graph.json",
                            _json.dumps(_graph_payload, indent=2),
                        )
                        _lineage_ok = True
            except Exception as _le:
                _lost("the lineage graph", _le)
                zf.writestr(
                    f"{bundle_dir}/lineage/lineage_graph_ERROR.txt",
                    f"Lineage graph generation failed:\n{_le}",
                )

            # ── The log of the ids (D-0575, D-0576, D-0582, D-0592) ────────────────────────────────────────────────
            # What the checks of the ids found for the recipe and the data of THIS export, with the log of the user folder (the entries that say a person
            # read it too). Always in the bundle when a table takes part: "the person utilizing the results MUST read that log" (D-0582).
            _user_data = bootloader.get_location("user_data")
            _id_run = run_id_checks(orchestrator, data_analysis_recipe_id, cfg.raw_config, export_keys, _user_data, write=False)
            _id_log = export_log_text(_user_data, data_analysis_recipe_id, _id_run, export_keys.data_analysis_recipe_sha256, export_keys.data_batch_hash)
            if _id_log is not None:
                zf.writestr(f"{bundle_dir}/id_log.yaml", _id_log)
                id_log_line = ("  id_log.yaml       — the log of the ids: the ids that tables lack, the lines added for them (the app's words for such a line: "
                               f"\"{added_line_words()}\"; what it means for each table is the sentence of the recipe maker, given beside) and the lines with no usable id; "
                               "read it before you rely on the results" + (" (the ids are equal in every table)" if not _id_run.lines else ""))
            elif _id_run.error:
                zf.writestr(f"{bundle_dir}/id_log_ERROR.txt", _id_run.error)
                id_log_line = f"  id_log_ERROR.txt  — the log of the ids could not be made: {_id_run.error}"
            else:
                id_log_line = None   # no table of the recipe takes part in the completion of the ids: there is no log
            # What the README and the report say about the ids (D-0582): what was found, in the app's words with the sentence of the recipe maker, and whether
            # the warning was read in the app or the log is "automatic, no user". Never a reason to refuse the export.
            _id_sentences = export_sentences(_id_run, read_status(id_log_folder(_user_data), data_analysis_recipe_id,
                                                                   export_keys.data_analysis_recipe_sha256, export_keys.data_batch_hash))

            # ── Generate Quarto .qmd report ───────────────────────────────
            # QMD image refs use qmd_plot_fmt (PNG when PDF+SVG mismatch)
            plot_ext = qmd_plot_fmt

            # Build mapping table rows for QMD and README
            mapping_rows = [
                (ds_key, _safe_ds_name(ds_key), plot_list)
                for ds_key, plot_list in ds_to_plots.items()
            ]

            qmd_lines = [
                "---",
                f"title: {_qy('Results Report — ' + str(data_analysis_recipe_id))}",
                f"date: {_qy(now.strftime('%Y-%m-%d'))}",
                f"author: {_qy(safe_name)}",
                'format:',
                '  html:',
                '    self-contained: true',
                '    toc: true',
                '    toc-depth: 3',
                '    toc-title: "Contents"',
                '    number-sections: true',
                '    theme: cosmo',
                '    fontsize: 11pt',
                '  pdf:',
                '    documentclass: article',
                '    toc: true',
                '    number-sections: true',
                '    fontsize: 11pt',
                '  docx:',
                '    toc: true',
                '    number-sections: true',
                "---",
                "",
                "## Overview",
                "",
                f"Data analysis recipe: **{_qp(data_analysis_recipe_id)}**  ",
                f"App features: **{_qp(app_features)}**  ",
                f"Export preset: **{_qp(preset)}**  ",
                f"Generated: {_qp(now.strftime('%Y-%m-%d %H:%M:%S'))}  ",
                "",
                "## Dataset → Plot Mapping",
                "",
                "| Dataset | Plots |",
                "|---------|-------|",
            ]
            for ds_key, safe_ds, plot_list in mapping_rows:
                plots_str = ", ".join(_qc(p, True) for p in plot_list)
                qmd_lines.append(f"| {_qc(ds_key, True)} | {plots_str} |")
            qmd_lines.append("")

            # Decision hash rows for QMD provenance table
            _prov_dh = prov.get("decision_hashes", {})
            _dh_qmd_rows = []
            for _ds_k, _k in prov.get("stage_keys", {}).items():
                _dh_qmd_rows.append(
                    f"| Tier 1 key ({_qp(_ds_k)}) | {_qc(_k['tier1_key'], True)} | "
                    "Key of the Tier 1 parquet of this table: engine and version, the definition of the table and of what it reads, the data files it reads |"
                )
                _dh_qmd_rows.append(
                    f"| Tier 2 key ({_qp(_ds_k)}) | {_qc(_k['tier2_key'] or 'none (T2 equals T1)', True)} | "
                    "Key of the Tier 2 parquet: Tier 1 key and the tier2 steps of the table (a join, or a table a plot reads directly) |"
                )
            for _pk, _pkey in prov.get("plot_keys", {}).items():
                _dh_qmd_rows.append(
                    f"| Tier 3 key ({_qp(_pk)}) | {_qc(_pkey, True)} | "
                    "Key of the table this plot reads: the key of its Tier 2 table and the tier3 steps of the plot (written only for a plot that has tier3 steps) |"
                )
            if _dh_qmd_rows:
                pass
            elif _prov_dh:
                for _ds_k, _ds_h in _prov_dh.items():
                    _dh_qmd_rows.append(
                        f"| Decision hash ({_qp(_ds_k)}) | {_qc(_ds_h, True)} | "
                        f"SHA256 of wrangling steps for {_qc(_ds_k, True)} — read from Parquet metadata key `sparmvet_decision_hash` |"
                    )
            else:
                _dh_qmd_rows.append(
                    "| Decision hash | see Parquet metadata | "
                    "SHA256 of wrangling steps dict — one per T1/T2 Parquet file |"
                )
            # Software version row
            _sw_qmd = prov.get("software_versions", {})
            _sw_qmd_str = _qp("; ".join(f"{k}={v}" for k, v in _sw_qmd.items()) if _sw_qmd else "n/a")

            qmd_lines += [
                "## Provenance",
                "",
                f"**Git commit:** {_qc(prov['git_commit'])}  ",
                f"**Release:** {_qc(prov['release_version'])}  ",
                f"**Software:** {_sw_qmd_str}  ",
                f"**Data analysis recipe:** {_qc(prov['data_analysis_recipe_name'])} — {_qc(prov['data_analysis_recipe_path'])}  ",
                "",
                "> The full verification record — recipe/data/T3-steps/engine hashes, per-plot",
                "> seeds, environment — is in **`effective_run.yaml`**, included in this bundle.",
                "> It is written identically whether or not the reproducibility bundle (the",
                "> recipe + actual data files) was also requested, so a copy from a separately",
                "> exported bundle can be diffed against this one, field by field, to confirm",
                "> they are the same analysis (ADR-097).",
                "",
                "| Hash | Value | Meaning |",
                "|------|-------|---------|",
                *_dh_qmd_rows,
                "",
                "## About the data in this report",
                "",
                "The data behind these results exists in up to three versions, called **tiers**:",
                "",
                "| Tier | What it is |",
                "|------|------------|",
                "| **T1 — Raw data** | The original assembled dataset exactly as it came out of the analysis pipeline. Nothing has been changed. This is what you find in the `data/` folder. |",
                "| **T2 — Result** | T1 with the processing steps of the data analysis recipe (tier 2) applied. The figures show the Result. A T2 file is included only when the dataset has tier 2 steps; without them T2 equals T1. |",
                "| **T3 — The table of a plot** | The table a plot is drawn from: the Result (T2) plus the plot's own tier-3 steps of the recipe, when it has some, plus the steps the analyst sent to audit, each with a reason (for example excluding a sample that failed QC). Only audited steps are exported: filters tried while exploring are never included. The table of a plot is saved as `T3_data_<plot>.tsv`; the sentence under each plot says whether it holds the recipe's own steps, the audit steps or both, and the audit steps are listed under *T3 Audit Trail*. |",
                "",
            ]
            if _id_sentences:
                qmd_lines += ["## The ids of the tables", ""]
                _after_bullet = False
                for _sentence in _id_sentences:
                    _bullet = _sentence.startswith("- ")
                    if _after_bullet and not _bullet:
                        qmd_lines.append("")
                    qmd_lines.append(("- " if _bullet else "") + _qp(_sentence[2:] if _bullet else _sentence))
                    if not _bullet:
                        qmd_lines.append("")
                    _after_bullet = _bullet
                qmd_lines.append("")
            # ── Methods section (auto-generated from the audited T3 steps) ───
            _methods_lines = _build_methods_section(
                all_plots=all_plots,
                t3_by_plot={**_t3_listed, PLACES_BUCKET: _place_nodes_all} if _place_nodes_all else _t3_listed,
                ds_to_plots=ds_to_plots,
                tiers_exported=tiers_exported,
                t3_aesthetic_overrides=_t3_aesthetic_overrides,
            )
            qmd_lines += _methods_lines

            # QMD image paths point to _render/ (Quarto-compatible copies).
            # _render/ is written into the Quarto temp dir alongside report.qmd.
            # The user-facing plots/ folder in the zip keeps the chosen format.
            # The report is built by group (D-0484): the `ui_label` of a group is a `##` heading, the `ui_label` of each of its plots a `###`.
            # PROVISIONAL (heading levels not decided by D-0484 alone; D-0491 adds two parts, `# Results` and `# Technical`, and is not built here).
            for _group_label, _group_plots in export_plot_groups(cfg.raw_config):
                qmd_lines += [f"## {_qp(_group_label) if _group_label is not None else 'Plots'}", ""]
                if not _group_plots:
                    qmd_lines += ["This group has no plot.", ""]   # PROVISIONAL wording (D-0491 leaves it open)
                for p_id, spec in _group_plots:
                    label = plot_report_name(spec, p_id)
                    ds_note = spec.get("target_dataset") or "—"
                    fig_id = f"fig-{_re.sub(r'[^A-Za-z0-9]', '-', p_id)}"
                    caption = f"{_qp(label)} — dataset: {_qc(ds_note)}"
                    qmd_lines += plot_report_lines(p_id, label, caption, fig_id, plot_ext, failed_plots.get(p_id))

            qmd_lines += [
                "## Data files",
                "",
                "> **Keep the folder structure intact.**  ",
                "> Data files live under `<dataset>/` subfolders alongside their plots.",
                "> The links below are relative paths from the report file location.",
                "",
            ]
            for ds_key, safe_ds, plot_list in mapping_rows:
                df_preview = exported_dfs.get(ds_key)
                shape_note = (
                    f"{df_preview.height} rows × {len(df_preview.columns)} columns"
                    if df_preview is not None else ""
                )
                plots_str = ", ".join(_qc(p) for p in plot_list)
                qmd_lines += [f"### {_qp(ds_key)}", ""]
                qmd_lines.append(f"*Used by: {plots_str}*  ")
                if shape_note:
                    qmd_lines.append(f"*{shape_note}*  ")
                qmd_lines.append("")
                # Only files that are in the bundle (VERIF-FIX-2, E4): T1 when it was written, T2 when the table has tier 2
                # steps, and one T3 file per plot that has audited steps or tier3 steps of the recipe and whose file was written.
                # (A plot with no target table has its plots in `__anchor__/` and its data under the key `__tier1_anchor__`.)
                _data_key = "__tier1_anchor__" if ds_key == "__anchor__" else ds_key
                _data_folder = _quote(_safe_ds_name(_data_key))
                if _data_key in exported_dfs:
                    qmd_lines.append(f"[Raw data (T1)]({_data_folder}/T1_data.tsv)")
                if _data_key in exported_t2:
                    qmd_lines.append(f"[Result data (T2)]({_data_folder}/T2_data.tsv)")
                if (_data_key, "T1") in _audited_written:
                    qmd_lines.append(f"[Audited raw data (T1)]({_data_folder}/T1_data_audited.tsv)")
                if (_data_key, "T2") in _audited_written:
                    qmd_lines.append(f"[Audited result data (T2)]({_data_folder}/T2_data_audited.tsv)")
                for _plot in plot_list:
                    if (_data_key, _plot) in _t3_written:
                        _t3_label = "Data of the plot after the audit steps (T3)" if _plot in audited_plots else "Data of the plot (T3)"
                        qmd_lines.append(f"[{_t3_label} of {_qp(_plot)}]({_data_folder}/T3_data_{_quote(_plot)}.tsv)  ")
                        qmd_lines.append(f"*{_qp(t3_file_sentence(_data_folder, _plot, _plot in audited_plots, _plot in recipe_t3_plots))}*  ")
                qmd_lines.append("")

            # Tables that no plot reads (D-0457). PROVISIONAL wording (not decided).
            if unread_rows:
                qmd_lines += [
                    "### Tables that no plot reads", "",
                    "These tables are read by no plot of this recipe: their Tier 1 data is in the bundle, no figure is drawn from them.", "",
                ]
                for _t, _r in unread_rows.items():
                    if _r["error"] is None:
                        qmd_lines.append(f"- {_qp(_t)}: [Raw data (T1)]({_quote(_r['folder'])}/T1_data.tsv), "
                                         f"{_qp(str(_r['rows']))} rows × {_qp(str(_r['columns']))} columns"
                                         + (f"; [audited data (T1)]({_quote(_r['folder'])}/T1_data_audited.tsv)" if (_t, "T1") in _audited_written else ""))
                    else:
                        qmd_lines.append(f"- {_qp(_t)}: not written, see `{_quote(_r['folder'])}/T1_data_ERROR.txt`")
                qmd_lines.append("")

            # ── The audit steps, at every tier (demo steps 4 and 7) ──────────
            if _place_records:
                qmd_lines += ["## Audit steps", "",
                              "Each step below was written at the table or plot named; every table and plot built from that place is built again from it, and the figures and data files of this bundle are those.", "",
                              "| Step | Written at | Action | Details | Justification | Plots built from it |",
                              "|------|------------|--------|---------|---------------|---------------------|"]
                for _i, _r in enumerate(_place_records, 1):
                    _details = _qp("; ".join(f"{k}={v}" for k, v in _r["params"].items())) if _r["params"] else "—"
                    _plots = _qp(", ".join(_r["plots"]) or "none")
                    qmd_lines.append(f"| {_i} | {_qp(_r['place_words'])} | {_qc(_r['action'], True)} | {_details} | {_qp(_r['reason'] or '—')} | {_plots} |")
                qmd_lines.append("")
                # which table file is which (PROVISIONAL words): in an export made in Audit mode the audited table is written beside its original
                if _audited_written:
                    qmd_lines += ["This export was made in Audit mode, so the table files of every table that a step changes come twice, the original and the audited one:", ""]
                    qmd_lines += [f"- {_qp(_l)}" for _l in _audited_file_sentences(_audited_written, exported_t2)]
                else:
                    qmd_lines += ["The table files `T1_data.tsv` and `T2_data.tsv` are the tables as the recipe builds them, without these steps; "
                                  + ("this export was made in Exploration mode." if not _audit_now else "no step changes a table here, steps at a plot change only the T3 files and the plot."), ""]
                if audit_recipe_file:
                    qmd_lines += [_qp(audit_recipe_sentence(audit_recipe_file, data_analysis_recipe_id)), ""]
                elif audit_recipe_failed:
                    qmd_lines += ["The audit recipe could not be written: see `audit_recipe/ERROR.txt`.", ""]
                qmd_lines.append("")

            # ── T3 Audit Trail section ────────────────────────────────────
            if _t3_listed:
                qmd_lines += ["## T3 Audit Trail", ""]
                for _pid, _nodes in _t3_listed.items():
                    _section_label = _qp(next(
                        (plot_report_name(s, _pid) for p, s in all_plots if p == _pid), _pid
                    ))
                    qmd_lines += [
                        f"### {_section_label}",
                        "",
                        "| Step | Action | Details | Justification |",
                        "|------|--------|---------|---------------|",
                    ]
                    for _i, _n in enumerate(_nodes, 1):
                        _action = _n.get("node_type", "?")
                        _params = _n.get("params", {})
                        _details = _qp("; ".join(
                            f"{k}={v}" for k, v in _params.items()
                        )) if _params else "—"
                        _reason = _qp(_n.get("reason") or "—")
                        qmd_lines.append(
                            f"| {_i} | {_qc(_action, True)} | {_details} | {_reason} |"
                        )
                    qmd_lines.append("")

            # ── Processing Issues section ───────────────────────────────────
            _pe_entries = (
                session_processing_issues.get()
                if session_processing_issues is not None else []
            )
            if _pe_entries:
                qmd_lines += ["## Processing Issues During Session", ""]
                qmd_lines.append(
                    "> The following runtime errors or warnings occurred during this session. "
                    "Review these before publishing results."
                )
                qmd_lines.append("")
                qmd_lines += [
                    "| Time | Component | Severity | Problem |",
                    "|------|-----------|----------|---------|",
                ]
                for _pe in _pe_entries:
                    _ts = _qp((_pe.get("timestamp") or "")[:19].replace("T", " "))
                    _comp = _pe.get("component", "?")
                    _sev = _qp(_pe.get("severity", "error").upper())
                    _prob = _qp((_pe.get("problem") or "Unknown error")[:120])
                    qmd_lines.append(f"| {_ts} | {_qc(_comp, True)} | {_sev} | {_prob} |")
                qmd_lines.append("")

            # ── Data Lineage section ──────────────────────────────────────
            if _lineage_ok and _lineage_nodes:
                qmd_lines += ["## Data Lineage", ""]
                # Mermaid flowchart — cylinder=source, rounded=wrangling,
                # rhombus=join, rectangle=plot.
                _mmd_shapes = {
                    "data_source": ('[("', '")]'),
                    "wrangling": ('("', '")'),
                    "join": ('{"', '"}'),
                    "plot_spec": ('["', '"]'),
                }
                _mmd_type_labels = {
                    "data_source": "source",
                    "wrangling": "wrangling",
                    "join": "join",
                    "plot_spec": "plot",
                }

                def _mmd_id(nid: str) -> str:
                    return _re.sub(r"[^A-Za-z0-9_]", "_", nid)

                qmd_lines += ["```{mermaid}", "flowchart LR"]
                for _nid, _nd in _lineage_nodes.items():
                    _t = _nd["type"]
                    _lbl = _qm(_nd["label"])
                    _tlbl = _mmd_type_labels.get(_t, _t)
                    _open, _close = _mmd_shapes.get(_t, ('["', '"]'))
                    qmd_lines.append(
                        f"    {_mmd_id(_nid)}{_open}{_lbl} / {_tlbl}{_close}"
                    )
                for _ef, _et in sorted(_lineage_edges):
                    qmd_lines.append(f"    {_mmd_id(_ef)} --> {_mmd_id(_et)}")
                qmd_lines += ["```", ""]

                # Step summary table
                _ln_type_order = {
                    "data_source": 0, "wrangling": 1, "join": 2, "plot_spec": 3
                }
                qmd_lines += [
                    "### Lineage Step Summary",
                    "",
                    "| Type | Schema ID | Label | Path |",
                    "|------|-----------|-------|------|",
                ]
                for _nd in sorted(
                    _lineage_nodes.values(),
                    key=lambda x: (_ln_type_order.get(x["type"], 9), x["schema_id"]),
                ):
                    _nd_rel = _nd.get("rel") or "—"
                    qmd_lines.append(
                        f"| {_qc(_nd['type'], True)} | {_qc(_nd['schema_id'], True)} "
                        f"| {_qp(_nd['label'])} | {_qc(_nd_rel, True)} |"
                    )
                qmd_lines += [
                    "",
                    "> **`lineage/lineage_graph.json`** contains the full machine-readable DAG.",
                    "> Nodes are deduplicated — a dataset shared by multiple plots appears only once.",
                    "> Edge direction: upstream → downstream (source → wrangling → join → plot).",
                    "",
                ]

            if wants_mode2:
                _seed_note = seed_recipe_note(_plot_seeds, dict(all_plots))
                if _seed_note:
                    qmd_lines += ["## Random scatter seeds", ""] + [f"> {_qp(_l)}" if _l else ">" for _l in _seed_note] + [""]
            qmd_lines += [
                "---",
                "",
                "> Report generated by SPARMVET-VIZ.",
                "> Full verification record — recipe/data/T3-steps/engine hashes, per-plot",
                "> seeds — in `effective_run.yaml`, written the same way whether or not the",
                "> reproducibility bundle (recipe + actual data files) was also requested.",
                "> Decision hashes (wrangling steps): see `sparmvet_decision_hash` in each Parquet metadata block.",
            ]

            qmd_source = "\n".join(qmd_lines)
            zf.writestr(f"{bundle_dir}/report.qmd", qmd_source)

            # ── Render report with Quarto ─────────────────────────────────
            import subprocess as _sp
            out_ext = {"html": "html", "pdf": "pdf", "docx": "docx"}.get(report_fmt, "html")
            rendered_report_bytes = None
            render_stderr = ""
            with tempfile.TemporaryDirectory() as report_tmp:
                report_tmp_path = Path(report_tmp)
                qmd_tmp = report_tmp_path / "report.qmd"
                qmd_tmp.write_text(qmd_source, encoding="utf-8")
                # Write Quarto-compatible plot copies to _render/ inside the temp dir.
                # _render/ is separate from the user-facing plots/ in the zip so
                # format conversions (e.g. SVG→PNG for PDF output) stay internal.
                render_tmp = report_tmp_path / "_render"
                render_tmp.mkdir()
                for p_id, raw in qmd_plot_bytes.items():
                    (render_tmp / f"{p_id}.{qmd_plot_fmt}").write_bytes(raw)
                try:
                    result = _sp.run(
                        ["quarto", "render", str(qmd_tmp), "--no-execute",
                         "--to", out_ext,
                         "--output", f"report.{out_ext}"],
                        capture_output=True, text=True, timeout=120,
                        cwd=str(report_tmp_path),
                    )
                    render_stderr = result.stderr or ""
                    candidate = report_tmp_path / f"report.{out_ext}"
                    if candidate.exists():
                        rendered_report_bytes = candidate.read_bytes()
                except Exception as exc:
                    render_stderr = str(exc)

            if rendered_report_bytes:
                zf.writestr(f"{bundle_dir}/report.{out_ext}", rendered_report_bytes)
            else:
                _quarto_words = " ".join((render_stderr or "").split())[:240] or "it produced no output file"
                _later("⚠️ " + notice(
                    f"Quarto could not render report.{out_ext}, so the bundle holds the report source report.qmd and "
                    f"no rendered report ({_quarto_words})",
                    ["install Quarto (quarto.org) if it is missing", _NO_FIGURES_REMEDY]), duration=15)
                zf.writestr(
                    f"{bundle_dir}/report_RENDER_FAILED.txt",
                    f"Quarto could not render report.{out_ext}.\n\n"
                    f"stderr:\n{render_stderr}\n\n"
                    "The report.qmd source is still included. Install Quarto (quarto.org) if it is missing.\n"
                    f"{_NO_FIGURES_REMEDY[0].upper()}{_NO_FIGURES_REMEDY[1:]}.\n",
                )

            # ── README.txt ────────────────────────────────────────────────
            rendered_note = (
                f"  report.{out_ext} — rendered report ({out_ext.upper()})"
                if rendered_report_bytes
                else "  (report rendering failed — see report_RENDER_FAILED.txt)"
            )
            # Tables that no plot reads (D-0457), for README. PROVISIONAL wording (not decided).
            unread_block = ([
                "Tables that no plot reads", "-" * 20,
                "These tables are read by no plot of this recipe: their Tier 1 data is in the bundle, no figure is drawn from them.",
                *[f"  {_t}: " + (f"{_r['folder']}/T1_data.tsv ({_r['rows']} rows x {_r['columns']} columns)" if _r["error"] is None
                                  else f"NOT WRITTEN, see {_r['folder']}/T1_data_ERROR.txt")
                  for _t, _r in unread_rows.items()],
                "",
            ] if unread_rows else [])
            # Dataset → plots mapping block for README
            mapping_block = ["Dataset → Plots", "-" * 20]
            for ds_key, safe_ds, plot_list in mapping_rows:
                mapping_block.append(f"  {ds_key}/")
                tier_files = ["T1_data.tsv"] \
                    + (["T2_data.tsv"] if ds_key in exported_t2 else []) \
                    + ([f"T3_data_{_p}.tsv" for _p in plot_list if _p in t3_table_plots])
                mapping_block.append(f"    data : {', '.join(tier_files)}")
                mapping_block.append(f"    plots: {', '.join(plot_list)}")
                for _p in plot_list:
                    if _p in t3_table_plots:
                        mapping_block.append("    " + t3_file_sentence(safe_ds, _p, _p in audited_plots, _p in recipe_t3_plots))

            # Decision hashes block for README
            _dh = prov.get("decision_hashes", {})
            _dsp = prov.get("data_source_paths", {})
            _sw = prov.get("software_versions", {})
            _sw_str = ", ".join(f"{k}={v}" for k, v in _sw.items()) if _sw else "n/a"
            _dh_lines = []
            for _ds_k, _k in prov.get("stage_keys", {}).items():
                _dh_lines.append(f"  {_ds_k}: tier1_key={_k['tier1_key']}")
                _dh_lines.append(f"  {_ds_k}: tier2_key={_k['tier2_key'] or 'none (T2 equals T1)'}")
            for _pk, _pkey in prov.get("plot_keys", {}).items():
                _dh_lines.append(f"  plot {_pk}: tier3_key={_pkey}")
            if _dh_lines:
                pass
            elif _dh:
                for _ds_k, _ds_h in _dh.items():
                    _dh_lines.append(f"  {_ds_k}: {_ds_h}")
            else:
                _dh_lines.append("  n/a (see Parquet metadata key 'sparmvet_decision_hash')")
            _dsp_lines = []
            for _ds_k, _ds_p in _dsp.items():
                _dsp_lines.append(f"  {_ds_k}: {_ds_p}")

            readme_lines = [
                "SPARMVET-VIZ Export Bundle",
                "=" * 40,
                f"Timestamp        : {prov['created_at']}",
                f"Data analysis recipe: {prov['data_analysis_recipe_id']}",
                f"Data analysis recipe name    : {prov['data_analysis_recipe_name']}",
                f"Data analysis recipe path    : {prov['data_analysis_recipe_path']}",
                f"User             : {prov['bundle_label']}",
                f"App features     : {prov['app_features']}",
                f"Preset           : {prov['preset']} (DPI={prov['dpi']}, {prov['plot_width']}×{prov['plot_height']} in)",
                f"Screen view      : {prov['screen_view']}",
                f"Plot format      : {plot_fmt}",
                # D-0050: the choice that decides whether the recipe and the data files are in the bundle, as the server read
                # it when Export was pressed (a box that went back to unticked would show here, not only as a missing folder).
                (("Reproducibility  : requested (the box 'Also include a reproducibility/reimport bundle' was ticked) "
                  "but NOT built; the reason is in data_analysis_recipes_reproducibility/ERROR.txt")
                 if wants_mode2 and repro_status == "failed" else
                 ("Reproducibility  : included but INCOMPLETE (the box 'Also include a reproducibility/reimport bundle' "
                  "was ticked); the data file(s) that could not be copied are listed as *_ERROR.txt files in "
                  "data_reproducibility/: " + ", ".join(repro_missing_files))
                 if wants_mode2 and repro_status == "incomplete" else
                 "Reproducibility  : included (the box 'Also include a reproducibility/reimport bundle' was ticked)"
                 if wants_mode2 else
                 "Reproducibility  : not included (the box 'Also include a reproducibility/reimport bundle' was not "
                 "ticked when Export was pressed)"),
                f"Plots            : {prov['plot_count']} (all plots of the recipe are exported)",
                (f"Plot warnings    : {sum(len(v) for v in _plot_warning_rows.values())} (listed under 'Plot warnings' below)"
                 if _plot_warning_rows else "Plot warnings    : none"),
                f"Tiers            : {', '.join(prov['tiers_exported'])}",
                "",
                "Software",
                "-" * 40,
                f"Versions         : {_sw_str}",
                f"Git commit       : {prov['git_commit']}",
                f"Release version  : {prov['release_version']}",
                export_contact_readme_line(_contact),
                "",
                "Reproducibility",
                "-" * 40,
                "See effective_run.yaml (included in this bundle) for the full verification",
                "record: recipe/data/T3-steps/engine hashes, per-plot seeds, environment.",
                "Written identically whether or not the reproducibility bundle (recipe +",
                "actual data files) was also requested — diff a copy from a separately",
                "exported bundle against this one, field by field, to confirm they are the",
                "same analysis (ADR-097).",
                "",
                *([f"Plot warnings could not be read for: {', '.join(_warnings_unreadable)}", ""]
                  if _warnings_unreadable else []),
                *(["Plot warnings (these plots were drawn; read each warning before you rely on the plot):",
                   *[f"  {_pid}: {_row['text']}" for _pid, _rows in _plot_warning_rows.items() for _row in _rows],
                   ""] if _plot_warning_rows else []),
                "Stage keys (per dataset; the Tier 1 key of each table, then its Tier 2 key):",
                *_dh_lines,
                "",
                "Data source paths:",
                *(_dsp_lines if _dsp_lines else ["  n/a"]),
                "",
                *mapping_block,
                "",
                *unread_block,
                "Plots reached by audit steps (the steps are always applied to the plot and its data):",
                *([f"  {_p}: {sum(1 for _r in _place_records if _p in _r['plots'])} step(s), see t3_steps.yaml (steps_by_place) and the report"
                   for _p in sorted(audited_plots)] or ["  none"]),
                *(["", "Audit steps, each at the place it is written (every table and plot built from that place is built again from it; always applied):",
                   *[f"  {_r['place_words']}: {_r['action']} {', '.join(f'{k}={v}' for k, v in _r['params'].items())} -- reason: {_r['reason']} -- plots built from it: "
                     f"{', '.join(_r['plots']) or 'none'}" for _r in _place_records],
                   "  The T3 file of every plot built from a place holds the audited table, and the figures are drawn from it. (see t3_steps.yaml, steps_by_place, and the report)",
                   *(["  This export was made in Audit mode: the audited table of every table a step changes is written BESIDE its original (a table no step changes has only its original):",
                      *[f"    {_l}" for _l in _audited_file_sentences(_audited_written, exported_t2)]]
                     if _audited_written else
                     ["  The T1 and T2 files of every table are the tables as the recipe builds them, without these steps: "
                      + ("this export was made in Exploration mode, where the table files are not audited."
                         if not _audit_now else "no audit step changes a table here (steps at a plot change only the T3 files and the plot).")]),
                   *([f"  {audit_recipe_sentence(audit_recipe_file, data_analysis_recipe_id)}"] if audit_recipe_file else
                     (["  The audit recipe could not be written: see audit_recipe/ERROR.txt."] if audit_recipe_failed else []))] if _place_records else []),
                "",
                "Contents:",
                "  <dataset>/plots/  — rendered figures, grouped by source dataset",
                "  <dataset>/T1_data.tsv — raw assembled data (T1)",
                "  <dataset>/T2_data.tsv — processed data (T2, when steps defined)",
                *(["  audit_recipe/<id>_audited.yaml — the audit recipe: the original recipe with every audit step at its place and its reason (only in an export made in Audit mode)"]
                  if audit_recipe_file else []),
                *(["  <dataset>/T1_data_audited.tsv, T2_data_audited.tsv — the same tables with the audit steps applied (only in an export made in Audit mode, only for a",
                   "                     table an audit step changes; the original file beside it is unchanged)"] if _audited_written else []),
                "  <dataset>/T3_data_<plot>.tsv — the table a plot is drawn from (T3), written for a plot that has tier3 steps of the recipe or audit steps: T2 (T1 when",
                "                     there are no tier2 steps) plus that plot's own tier3 steps of the recipe plus the audit steps that reach it; the line of each plot under",
                "                     'Dataset -> Plots' says which of these it holds (the recipe's own steps are not audit steps)",
                "  t3_steps.yaml     — human-readable audit record (when T3 has steps)",
                *([id_log_line] if id_log_line else []),
                *([f"      {_s}" for _s in _id_sentences]),
                "  effective_run.yaml — the full verification record: recipe/data/T3-steps/engine",
                "                     hashes, per-plot seeds, the engine of each tier and plot, the theme as",
                "                     applied and the library versions (`engines`). Written the same way either way (ADR-097).",
                "  lineage/          — lineage_graph.json (shared-node DAG, ADR-074)",
                "  report.qmd        — Quarto source (re-render: quarto render report.qmd)",
                rendered_note,
                "  README.txt        — this file",
                *([
                    "  data_analysis_recipes_reproducibility/<id>.yaml — frozen recipe copy with",
                    "       your audit steps baked in as real wrangling actions, each at its own place",
                    "       (the tier 1 or tier 2 of a table, the tier 3 of a plot).",
                    "       The random scatter (jitter) seeds the export wrote into it are listed below and in",
                    "       effective_run.yaml (seeds_added_to_recipe, seeds_per_layer); a number the recipe",
                    "       already wrote on a layer is kept.",
                    *[f"       {_l}" for _l in seed_recipe_note(_plot_seeds, dict(all_plots))],
                    "  data_reproducibility/<dataset>.<ext> — the actual data files used.",
                ] if wants_mode2 else []),
                "",
                "IMPORTANT — keep the folder structure intact.",
                "  The report contains relative links to the dataset subfolders.",
                "  Always share or archive the full export folder.",
                "",
                "About data tiers:",
                "  T1 = raw assembled data, unchanged from the pipeline output.",
                "  T2 = T1 with pipeline processing steps applied (range filters,",
                "       derived columns, etc.). Exported when T2 steps are defined.",
                "  T3 = the table a plot is drawn from: T2 (or T1 without tier2 steps) with the",
                "       plot's own tier3 steps of the recipe, if it has some, and with the steps the",
                "       analyst sent to audit (rows/columns removed, each with a reason). Only audited",
                "       steps are exported; exploration filters never are. One file per plot that has",
                "       tier3 steps in the recipe or audit steps: T3_data_<plot>.tsv; each is named in",
                "       'Dataset -> Plots' as after the recipe's own steps, after the audit steps, or both.",
            ]
            zf.writestr(f"{bundle_dir}/README.txt", "\n".join(readme_lines))

        with reactive.isolate():
            _build_refusal = refusal_for_build_changes(_build_changes, _view, export_keys, _notify, tables=_scope_tables_now)
        if _build_refusal is not None:
            yield _build_refusal
            return

        # The bundle is handed over: now the notices of its build are shown (D-0050).
        with reactive.isolate():
            for _text, _type, _duration in _deferred:
                _notify(_text, type=_type, duration=_duration)

        if _unwritten:
            _listed = "; ".join(f"{_what} ({_why})" for _what, _why, _ in _unwritten[:6]) + (
                f"; and {len(_unwritten) - 6} more" if len(_unwritten) > 6 else "")
            # what happened, with the reason only; then one Suggestion: per remedy (the libraries' own remedies first)
            _remedies = list(dict.fromkeys(_fix for _, _, _fix in _unwritten if _fix)) + [
                "open the *_ERROR.txt files of the bundle for the reason of each, fix the cause and export again; do not "
                "publish this bundle as complete"]
            with reactive.isolate():
                _notify("⚠️ " + notice(
                    f"{len(_unwritten)} part(s) of this export could not be written and are replaced by *_ERROR.txt files "
                    f"inside the bundle: {_listed}", _remedies), type="error", duration=None)

        buf.seek(0)
        yield buf.read()

    def _export_bundle_filename() -> str:
        """Generate timestamped zip filename for the export bundle."""
        import datetime, re
        now = datetime.datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        raw_name = safe_input(input, "export_user_name", "user").strip() or "user"
        safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", raw_name)[:40]
        return f"{ts}_{safe_name}_results.zip"
