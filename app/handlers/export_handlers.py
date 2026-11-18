"""app/handlers/export_handlers.py
Export pipeline: results bundle (.zip) + audit report (HTML/DOCX) +
system tools sidebar UI.

Extracted from home_theater.py in Phase 24-C (ADR-051).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: constant:EXPORT_READY_TEXTS, constant:EXPORT_PANEL_FIELDS, function:define_export_server, output:system_tools_ui, output:export_bundle_download, output:import_bundle_report, function:_build_methods_section
# consumes: app/src/www/export_ready.js (D-0270: greys the Export button until the echo of _confirm_export_inputs matches the screen), app/modules/error_notice.py (notice — VERIF-FIX-2), app/modules/session_manager.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py, libs/blueprint_arch/src/blueprint_arch/t3_translator.py (build_mode2_recipe — REPRO-EXPORT-MODES-1), app/modules/cache_keys.py (canonical_hash, engine_fingerprint — REPRO-PROV-1), app/modules/bundle_importer.py (import_bundle, BundleImportError — REPRO-IMPORT-1), app/modules/plot_seeds.py (SEED-HOLDS-1), app/modules/plot_issue_reporter.py (plot_warning_text — D-0269), libs/viz_factory/src/viz_factory/checked_plot.py (plot_warnings — D-0269), polars, shiny
#            reactive.Value:session_processing_issues (DIAG-RUNTIME-AUDIT-1 — included in report.qmd Processing Issues section)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-094 (plot-render error stub now includes the library's fix text), .claude/knowledge/architecture_decisions.md#ADR-097, .claude/design/export_specification.md, .claude/design/reproducible_export_design.md
# @end_deps

import io
import json
import zipfile
from pathlib import Path

from shiny import reactive, render, ui

from app.modules.error_notice import notice, what_failed
from app.modules.plot_issue_reporter import plot_warning_text
from viz_factory.checked_plot import plot_warnings
from app.modules.export_refusal import export_refusal
from app.modules.data_analysis_recipe_validator import export_contact_readme_line, export_contact_record
from app.modules.t3_audit_engine import _op_label, audit_failures, audited_frame, between_prose
from utils.fix_text import fix_label
from app.modules.qmd_text import code as _qc, mermaid_label as _qm, plain as _qp, yaml_string as _qy
from app.modules.plot_seeds import (
    bake_plot_seeds, export_seed_plan, seed_recipe_note, seed_sources_per_plot, seeds_added_to_recipe,
    seeds_per_layer_record, seeds_per_plot_record, render_seed_args, with_seed_steps,
)


# ---------------------------------------------------------------------------
# Module-level provenance helpers (headless-safe — no Shiny imports)
# ---------------------------------------------------------------------------

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
    active_tier: str,
    scope_label: str,
    all_plots: list,
    tiers_exported: list,
    data_analysis_recipe_sha: str,
    data_sha: str,
    bootloader,
    stage_keys: dict | None = None,
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
        "active_tier": active_tier,
        "export_scope": scope_label,
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


def changed_since_view(view_keys, current_keys) -> list[str]:
    """What changed between the keys the view was built on and the keys now (empty: nothing).

    ADR-089 / EXPORT-KEYCHECK-1. The view is built once per session from the data analysis recipe files and
    the data files; the export recomputes the keys. A difference means a file changed on disk
    after the user opened the view, so what is on screen is not what an export would contain.
    """
    changes: list[str] = []
    if view_keys is None or current_keys is None:
        return changes
    if view_keys.data_analysis_recipe_sha256 != current_keys.data_analysis_recipe_sha256:
        changes.append("the data analysis recipe (the data analysis recipe file or a file it includes)")
    if view_keys.data_batch_hash != current_keys.data_batch_hash:
        changes.append("the data files")
    if not changes and view_keys.tier1_key != current_keys.tier1_key:
        changes.append("the processing rules (the engine version or the Tier 1 parts of the data analysis recipe)")
    return changes


def blocked_export_notice(changes: list[str], view_keys, current_keys, during_build: bool = False) -> str:
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
        f"        tier1    {view_keys.tier1_key}",
        f"  now   data analysis recipe {current_keys.data_analysis_recipe_sha256}",
        f"        data     {current_keys.data_batch_hash}",
        f"        tier1    {current_keys.tier1_key}",
    ]
    return "\n".join(lines)


def blocked_export_zip(text: str) -> bytes:
    """The zip handed to the user in place of an export that is refused: only `EXPORT_NOT_CREATED.txt`."""
    blocked = io.BytesIO()
    with zipfile.ZipFile(blocked, mode="w") as archive:
        archive.writestr("EXPORT_NOT_CREATED.txt", text)
    return blocked.getvalue()


def refusal_for_build_changes(changes: list[str], view_keys, current_keys, notify) -> bytes | None:
    """The refusal (zip with only EXPORT_NOT_CREATED.txt, plus the error notification) when a table of the export was built while
    its recipe or data changed, else None. The same refusal as a change since the view; the tables were returned but not stored,
    and the export records the held keys, so nothing may be exported (D-0005: the export refuses when files changed)."""
    if not changes:
        return None
    view_keys = view_keys if view_keys is not None else current_keys     # no view (a headless caller): the keys of this export
    notify("Export blocked: " + "; ".join(changes) + " while a table of this export was being built. "
           "Reload the page (F5), check the plots, then export again.", type="error", duration=None)
    return blocked_export_zip(blocked_export_notice(changes, view_keys, current_keys, during_build=True))


def blocked_audit_notice(failing: list) -> str:
    """Text of `EXPORT_NOT_CREATED.txt` when the audited steps of plots cannot run in their recorded order: every failing plot, with its reason."""
    lines = ["EXPORT NOT CREATED", "",
             "The audit steps of " + ("this plot" if len(failing) == 1 else f"these {len(failing)} plots")
             + " cannot run in the order they were recorded:", ""]
    for plot_id, error in failing:
        lines += [f"Plot '{plot_id}':", str(error), ""]
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
            (s.get("title") or p_id.replace("_", " ").title()
             for pid, s in all_plots if pid == p_id),
            p_id.replace("_", " ").title(),
        ))
        for n in nodes:
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
                scope = f" (plot: *{plot_label}*)" if p_id != "__all__" else ""
                sentence = f"{verb} {detail}{scope}."
            elif nt == "drop_column":
                col = _qp(params.get("column", "?"))
                scope = f" (plot: *{plot_label}*)" if p_id != "__all__" else ""
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
            (s.get("title") or p_id.replace("_", " ").title()
             for pid, s in all_plots if pid == p_id),
            p_id.replace("_", " ").title(),
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


# The words the Scope radio shows for each value; the radio, its choices and the notices all read them from here.
SCOPE_LABELS = {"global": "Global", "group": "Active group", "plot": "Active plot"}


# D-0270: the Export button is ready only when the server holds the values on the screen.
# Every text the user sees about this is here, in one place (PROVISIONAL until Eve has read them).
EXPORT_READY_TEXTS = {
    "waiting": "Getting ready ...",
    "lost": "Your last change may not have been received. Check the box and the label, then press Export.",
}
# The fields of the Export panel the download reads. The page greys the button when one of them changes; the server
# echoes the values it holds for exactly these ids (app/src/www/export_ready.js).
EXPORT_PANEL_FIELDS = (
    "export_user_name", "export_scope", "export_include_reproducibility", "export_preset",
    "export_plot_format", "export_report_format", "export_plot_width", "export_plot_height",
)
# How long the button waits for the confirmation before it is active again with the notice above (milliseconds).
EXPORT_READY_TIMEOUT_MS = 5000


def export_scope_choices(groups: dict, active_subtab: str) -> dict:
    """The choices of the export Scope radio for the plot tab that is open now.

    Returns {value: {"label": str, "title": str, "dimmed": bool}} with the keys "global", "group" (when the recipe has
    groups) and "plot". A choice that needs an open plot tab is shown dimmed when none is open. Pure: no Shiny state.
    """
    has_groups = bool(groups)
    active_pid = active_subtab.removeprefix("subtab_") if active_subtab.startswith("subtab_") else ""

    active_gid = None
    if active_pid and has_groups:
        for gid, gspec in groups.items():
            if active_pid in gspec.get("plots", {}):
                active_gid = gid
                break

    choices = {"global": {"label": SCOPE_LABELS["global"], "title": "Export everything in the active data analysis recipe",
                          "dimmed": False}}
    if has_groups and active_gid is not None:
        choices["group"] = {"label": f"{SCOPE_LABELS['group']} ({active_gid})",
                            "title": "Export all plots in the current group (e.g. all Quality Control plots)",
                            "dimmed": False}
    elif has_groups and not active_pid:
        choices["group"] = {"label": SCOPE_LABELS["group"], "title": "Switch to a plot tab to enable scoped export.",
                            "dimmed": True}
    if active_pid:
        choices["plot"] = {"label": f"{SCOPE_LABELS['plot']} ({active_pid})",
                           "title": "Export only the plot you are currently viewing", "dimmed": False}
    else:
        choices["plot"] = {"label": SCOPE_LABELS["plot"], "title": "Switch to a plot tab to enable scoped export.",
                           "dimmed": True}
    return choices


def _scope_choice_tags(choices: dict) -> dict:
    """The radio choices of `export_scope_choices` as the labels the panel shows."""
    return {
        value: ui.span(c["label"], title=c["title"],
                       **({"style": "opacity:0.45; cursor:not-allowed;"} if c["dimmed"] else {}))
        for value, c in choices.items()
    }


def define_export_server(input, output, session, *,
                         bootloader, orchestrator, viz_factory,
                         current_app_features, active_cfg,
                         tier1_anchor,
                         tier_toggle,
                         home_state, safe_input,
                         active_home_subtab=None,
                         notification_log=None,
                         session_processing_issues=None,
                         t3_filter_rows=None,
                         t3_drop_columns=None,
                         view_keys=None):
    """Register export-bundle + system-tools handlers.

    Reactive deps (kwargs):
      bootloader         : Path Authority (ADR-031)
      orchestrator       : tier1/tier2 materialiser
      viz_factory        : plot renderer
      current_app_features    : reactive.Value[str]
      active_cfg         : reactive.Calc[ConfigManager]
      tier1_anchor       : reactive.Calc[LazyFrame]
      tier_toggle        : reactive.Value[str]   ("T1"|"T2"|"T3")
      home_state         : reactive.Value[dict] | None
      safe_input         : helper (input, key, default) → value
      active_home_subtab : reactive.Value[str] | None  — current plot subtab id
      t3_filter_rows     : callable(subtab_id) -> list[dict]  audited filter/exclusion rows (HOME's)
      t3_drop_columns    : callable(subtab_id) -> list[str]   audited column drops (HOME's)
      view_keys          : reactive.Calc[DataAnalysisRecipeKeys]  the keys the open view was built on
    """
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    @output
    @render.ui
    def system_tools_ui():
        if not bootloader.is_enabled("export_enabled"):
            return ui.div()

        # Reminder (Eve, 2026-11-06): only steps sent to audit are exported. Anything tried while
        # exploring (filters in T1/T2/My view) is a sandbox and is never part of the bundle.
        audit_reminder = ui.div()
        if bootloader.is_enabled("interactivity_enabled"):
            audit_reminder = ui.tags.small(
                "Only steps sent to audit are exported. Filters you are only exploring with are not.",
                class_="text-muted d-block mb-1",
                style="font-size:0.7em;",
            )

        # 3-way scope toggle. The radio is mounted here once, with the choices of this moment; when the active plot
        # tab or the recipe changes, `_sync_export_scope_choices` below updates its choices and keeps the user's
        # selection. This output never reads the plot tab or the recipe outside `isolate`: a redraw of the whole
        # panel would put every field back to its default (EXPORT-FLAKE-1, rule R4 of ui_implementation_contract.md
        # section 14, "shell stability pattern" of rules_app_structure.md section 8).
        scope_toggle = ui.div()
        if active_home_subtab is not None:
            with reactive.isolate():
                try:
                    _first_choices = _scope_choice_tags(export_scope_choices(
                        active_cfg().raw_config.get("analysis_groups", {}), active_home_subtab.get() or ""))
                except Exception:
                    # the choices are brought up to date by the effect below, which tells the user why it cannot
                    _first_choices = _scope_choice_tags(export_scope_choices({}, ""))
            scope_toggle = ui.div(
                ui.input_radio_buttons(
                    "export_scope",
                    label="Scope",
                    choices=_first_choices,
                    selected="global",
                    inline=True,
                ),
                class_="mb-1",
            )

        # Mode 2 add-on (ADR-097 decision 1/#45): opt-in, forces global scope when
        # checked — the scope radio above still renders but is overridden server-side
        # (safe_input(input, "export_include_reproducibility", ...)), so the note below
        # explains the override rather than disabling the radio itself.
        mode2_toggle = ui.div(
            ui.input_checkbox(
                "export_include_reproducibility",
                "Also include a reproducibility/reimport bundle",
                value=False,
            ),
            ui.tags.small(
                "The verification record (effective_run.yaml — hashes, seeds, "
                "environment) is always included. Checking this also adds the full "
                "recipe (your audited steps baked in as real wrangling actions) and "
                "the actual data files, so someone can re-run this, not just verify "
                "it. Forces Scope to Global — you can't partially reconstruct a recipe. "
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
                    value="",
                ),
                scope_toggle,
                mode2_toggle,
                ui.input_radio_buttons(
                    "export_preset",
                    label="Quality",
                    choices={"web": "Web / Presentation", "publication": "Publication (≥600 DPI)"},
                    selected="web",
                    inline=False,
                ),
                ui.input_radio_buttons(
                    "export_plot_format",
                    label="Plot format",
                    choices={"png": "PNG", "svg": "SVG", "pdf": "PDF"},
                    selected="png",
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
                    selected="html",
                    inline=True,
                ),
                ui.div(
                    ui.tags.label("Plot size (inches)", class_="d-block mb-1"),
                    ui.div(
                        ui.input_numeric("export_plot_width",  "W", value=8,  min=2, max=30, step=0.5),
                        ui.input_numeric("export_plot_height", "H", value=5,  min=2, max=30, step=0.5),
                        class_="d-flex gap-2",
                    ),
                    class_="mb-1",
                ),
                audit_reminder,
                ui.download_button(
                    "export_bundle_download",
                    "💾 Export Bundle",
                    class_="btn-success btn-sm w-100 mt-1",
                ),
                class_="mb-2 px-2",
                style="font-size:0.8em;",
                id="export_ready_panel",
                **{
                    "data-ready-fields": json.dumps(list(EXPORT_PANEL_FIELDS)),
                    "data-text-waiting": EXPORT_READY_TEXTS["waiting"],
                    "data-text-lost": EXPORT_READY_TEXTS["lost"],
                    "data-timeout-ms": str(EXPORT_READY_TIMEOUT_MS),
                },
            ),
            class_="px-2",
            style="font-size:0.8em;"
        )

    @reactive.Effect
    async def _confirm_export_inputs():
        """Tell the page which values of the Export panel the server holds (D-0270).

        Runs after every change of a field and after every ping of the page (`export_client_ping`, sent at each change,
        so that a change that leaves the values as they were is confirmed too). It reads every field the download reads
        and sends them back with the last ping it has seen; the page opens the Export button when they equal what is on
        the screen. This effect runs after the input messages were applied, so a download pressed after the echo reads
        the same values (the race of question 20: input messages are applied under the reactive lock, a download request
        is handled without it).
        """
        if not bootloader.is_enabled("export_enabled"):
            return
        ping = safe_input(input, "export_client_ping", 0)
        held = {}
        for field in EXPORT_PANEL_FIELDS:
            try:
                held[field] = getattr(input, field)()
            except Exception:
                continue    # a field that is not on the page (Scope without a plot tab): the page skips it too
        await session.send_custom_message("export_ready_echo", {"ping": ping, "values": held})

    @reactive.Effect
    def _sync_export_scope_choices():
        """Follow the plot tab and the recipe with the choices of the Scope radio, and keep what the user chose.

        Updates the radio in place (`update_radio_buttons`) instead of drawing the panel again, so no other field of the
        panel goes back to its default (EXPORT-FLAKE-1). When the chosen scope is no longer offered the scope goes back
        to Global and the user is told.
        """
        if not bootloader.is_enabled("export_enabled") or active_home_subtab is None:
            return
        try:
            choices = export_scope_choices(active_cfg().raw_config.get("analysis_groups", {}),
                                           active_home_subtab.get() or "")
        except Exception as e:
            with reactive.isolate():
                _notify(what_failed("The Scope choices of the Export panel could not be brought up to date; they stay as "
                                           "they were", e), type="warning", duration=10)
            return
        with reactive.isolate():
            current = safe_input(input, "export_scope", "global")
            selected = current if current in choices else "global"
            ui.update_radio_buttons("export_scope", choices=_scope_choice_tags(choices), selected=selected)
            if selected != current:
                _shown = SCOPE_LABELS.get(current, current)
                _notify(f"The export scope '{_shown}' is not available on this plot tab, so the scope was set back "
                        "to Global.", type="warning", duration=10)

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
        - plots/          SVG (web preset) or high-DPI PNG (publication preset) per plot
        - data/           T1 TSV for each dataset referenced by active plots
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
        preset = safe_input(input, "export_preset", "web")
        plot_fmt = safe_input(input, "export_plot_format", "png")
        report_fmt = safe_input(input, "export_report_format", "html")
        plot_width  = float(safe_input(input, "export_plot_width",  8))
        plot_height = float(safe_input(input, "export_plot_height", 5))
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
        _changes = changed_since_view(_view, export_keys)
        if _changes:
            _text = blocked_export_notice(_changes, _view, export_keys)
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
        top_plots = cfg.raw_config.get("plots", {})

        # Collect all (plot_id, spec) pairs for this export
        all_plots: list[tuple[str, dict]] = []
        for _gid, gspec in groups.items():
            for p_id, pentry in gspec.get("plots", {}).items():
                spec = pentry.get("spec")
                if spec:
                    all_plots.append((p_id, spec))
        if not all_plots:
            for p_id, spec in top_plots.items():
                all_plots.append((p_id, spec))

        # ── Mode 2 add-on (ADR-097 decision 1, #45): Publication content (plots,
        # report, T3 justification) is always built, unchanged — this is additive, not
        # a second, separate "reproducibility-only" bundle that suppresses it. That
        # stricter split (and whether Mode 1 keeps its current full recipe copy once
        # this exists) stays an open question, not resolved here. Checking the box
        # forces global scope — you cannot partially reconstruct a recipe from one
        # plot's data alone — regardless of the scope radio's current value.
        wants_mode2 = bool(safe_input(input, "export_include_reproducibility", False))

        # ── Apply export scope (Global / Active group / Active plot) ──────
        export_scope = "global" if wants_mode2 else safe_input(input, "export_scope", "global")
        scope_label = "global"
        _subtab = (active_home_subtab.get() or "") if active_home_subtab is not None else ""
        active_pid = _subtab.removeprefix("subtab_") if _subtab.startswith("subtab_") else ""

        if export_scope == "plot" and active_pid:
            _filtered = [(p, s) for p, s in all_plots if p == active_pid]
            if _filtered:
                all_plots = _filtered
                scope_label = active_pid
        elif export_scope == "group" and active_pid and groups:
            _active_gid = None
            for _gid, _gspec in groups.items():
                if active_pid in _gspec.get("plots", {}):
                    _active_gid = _gid
                    break
            if _active_gid:
                _gplot_ids = set(groups[_active_gid].get("plots", {}).keys())
                _filtered = [(p, s) for p, s in all_plots if p in _gplot_ids]
                if _filtered:
                    all_plots = _filtered
                    scope_label = _active_gid

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

        # ── Collect T3 audit data (per-plot active nodes) ─────────────────
        _t3_by_plot: dict[str, list[dict]] = {}
        _t3_aesthetic_overrides: dict[str, dict] = {}
        if home_state is not None and bootloader.is_enabled("t3_sandbox_enabled"):
            _state = home_state.get()
            _rbp = _state.get("t3_audit_steps_by_plot", {}) or {}
            for _pid, _ in all_plots:
                _nodes = [n for n in _rbp.get(f"subtab_{_pid}", []) if n.get("active", True)]
                if _nodes:
                    _t3_by_plot[_pid] = _nodes
            # t3_plot_overrides: resolved aesthetic state per plot (separate from audit step)
            _overrides_all = _state.get("t3_plot_overrides", {}) or {}
            for _pid, _ in all_plots:
                _subtab = f"subtab_{_pid}"
                if _subtab in _overrides_all and _overrides_all[_subtab]:
                    _t3_aesthetic_overrides[_pid] = _overrides_all[_subtab]

        # The audit pin of a plot (Reshuffle, or an audit override) is a step of the audit trail too, whatever the
        # audit-trail flag: listed in t3_steps.yaml, the Methods text and the report's audit table, and hashed.
        _t3_listed = with_seed_steps(_t3_by_plot, _plot_seeds)

        # The export is the Result (T2) plus the AUDITED T3 steps (committed with a reason, e.g.
        # removing poor quality data): the user's decision for the publication, always applied.
        # Exploration (filters tried in T1/T2/My view, not sent to audit) is a sandbox and is never
        # exported, from any view (Eve, 2026-11-06).
        active_tier = tier_toggle.get()

        def _audited_nodes(p_id: str) -> list[dict]:
            """The plot's audited steps, in the recorded order: the input of `audited_frame` (exploration is not part of it)."""
            by_plot = (home_state.get().get("t3_audit_steps_by_plot") or {}) if home_state is not None else {}
            return list(by_plot.get(f"subtab_{p_id}", []))

        def _has_audited_steps(p_id: str) -> bool:
            audited_rows = t3_filter_rows(f"subtab_{p_id}") if t3_filter_rows is not None else []
            audited_drops = t3_drop_columns(f"subtab_{p_id}") if t3_drop_columns is not None else []
            return bool(audited_rows or audited_drops)

        audited_plots = {p for p, _ in all_plots if _has_audited_steps(p)}

        # PLOT-TABLE-ORDER-1: check before anything is written. If the audited steps of a plot in scope cannot run in their
        # recorded order, the table, the plot and the exported recipe would differ or fail: nothing is exported for this scope.
        def _base_frame(spec: dict):
            """The base of a plot's My view: the stored Tier 2 (Tier 1 without tier2 steps), as the data and plot sections read it."""
            target = spec.get("target_dataset")
            if not target:
                return tier1_anchor()
            return orchestrator.materialize_tier2(
                data_analysis_recipe_id=data_analysis_recipe_id, collection_id=target,
                tier1_path=bootloader.get_location("user_data") / "anchors" / f"{target}.parquet", keys=export_keys,
                on_inputs_changed=_on_build_change)

        _failing = audit_failures([(_p, (lambda _s=_s: _base_frame(_s)), _audited_nodes(_p)) for _p, _s in all_plots])
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
            from app.modules.cache_keys import tier2_key as _tier2_key, tier2_steps as _tier2_steps
            data_analysis_recipe_sha = export_keys.data_analysis_recipe_sha256
            data_sha = export_keys.data_batch_hash
            stage_keys: dict[str, dict[str, str]] = {}
            for _p, _spec in all_plots:
                _ds = _spec.get("target_dataset")
                if _ds and _ds not in stage_keys:
                    _steps = _tier2_steps(cfg.raw_config, _ds)
                    stage_keys[_ds] = {
                        "tier1_key": export_keys.tier1_key,
                        "tier2_key": _tier2_key(export_keys.tier1_key, _steps) if _steps else "",
                    }

            tiers_exported = ["T1"] + (["T3"] if audited_plots else [])
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
                active_tier=active_tier,
                scope_label=scope_label,
                all_plots=all_plots,
                tiers_exported=tiers_exported,
                data_analysis_recipe_sha=data_analysis_recipe_sha,
                data_sha=data_sha,
                bootloader=bootloader,
                stage_keys=stage_keys,
                orchestrator=orchestrator,
                anchor_dir=anchor_dir,
                t3_by_plot=_t3_listed,
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
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)

                for p_id, spec in all_plots:
                    _ds_key = spec.get("target_dataset") or "__anchor__"
                    _safe_ds = _safe_ds_name(_ds_key)
                    try:
                        # Build synthetic data analysis recipe with applied filters
                        plot_spec = copy.deepcopy(spec)
                        synthetic_data_analysis_recipe = {
                            "plots": {p_id: plot_spec},
                            "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
                        }

                        # Resolve dataset
                        target_ds = spec.get("target_dataset")
                        if target_ds:
                            anchor_dir = bootloader.get_location("user_data") / "anchors"
                            out_path = anchor_dir / f"{target_ds}.parquet"
                            # Plots never show T1 (ADR-086): same base as HOME, the stored
                            # Tier 2 (equal to T1 when the table has no tier2 steps).
                            lf = orchestrator.materialize_tier2(
                                data_analysis_recipe_id=data_analysis_recipe_id,
                                collection_id=target_ds,
                                tier1_path=out_path,
                                keys=export_keys,
                                on_inputs_changed=_on_build_change,
                            )
                        else:
                            lf = tier1_anchor()

                        # the same call as HOME's table and plot: audited steps in the recorded order
                        lf = audited_frame(lf, _audited_nodes(p_id), p_id)

                        # VIZFAC-T3-EXPORT-1: pass L5 aesthetic_override so
                        # exported plots reflect analyst T3 overrides.
                        _plot_override = _t3_aesthetic_overrides.get(p_id)
                        fig = viz_factory.render(lf, synthetic_data_analysis_recipe, p_id,
                                                 **render_seed_args(_plot_seeds[p_id], _plot_override))
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
                # T3: only for advanced+ app features files, and only when tier_toggle == "T3".

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

                    # ── T2 (exported when tier2 steps exist) ───────
                    try:
                        from app.modules.cache_keys import tier2_steps
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

                    # ── T3 / My view data, one file per plot (audit nodes are per plot) ──
                    # Build rule T3 > T2 > T1: the base is the stored Tier 2, which is Tier 1
                    # when the table has no tier2 steps; the plot's filters and drops go on top.
                    # Written for every plot that has audited steps: its plot is built from this data,
                    # so the file must be there. Plots without audited steps have no T3 file.
                    if audited_plots:
                        for _t3_pid, _t3_spec in all_plots:
                            if (_t3_spec.get("target_dataset") or "__tier1_anchor__") != ds_key:
                                continue
                            if _t3_pid not in audited_plots:
                                continue
                            try:
                                if target_ds:
                                    lf_t3 = orchestrator.materialize_tier2(
                                        data_analysis_recipe_id=data_analysis_recipe_id,
                                        collection_id=target_ds,
                                        tier1_path=bootloader.get_location("user_data") / "anchors" / f"{target_ds}.parquet",
                                        keys=export_keys,
                                        on_inputs_changed=_on_build_change,
                                    )
                                else:
                                    lf_t3 = tier1_anchor()
                                lf_t3 = audited_frame(lf_t3, _audited_nodes(_t3_pid), _t3_pid)
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

                # ── t3_steps.yaml (when T3 has committed changes) — Mode 1 content: the
                # human-readable audit record backing the Methods prose, not the recipe. ──
                if _t3_listed or _t3_aesthetic_overrides:
                    try:
                        import yaml as _yaml
                        t3_steps_data = {
                            "generated": now.isoformat(),
                            "export_scope": scope_label,
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

            # ── Mode 2 add-on: the heavy, Mode-2-exclusive content (ADR-097, #45) ──
            # Recipe + actual data files. Additive to everything above, never a
            # replacement — Mode 1's content is unchanged regardless of this checkbox.
            # effective_run.yaml itself is NOT here — it is written unconditionally
            # below, since both modes need the exact same file to be comparable
            # (Eve, 2026-11-09): "if they differ means mode 1 and mode 2 not equal".
            mode2_skipped: dict[str, str] | None = None
            # What the README says about the reproducibility part (D-0050): "built", "failed" (ERROR.txt only) or
            # "incomplete" (built, but data files that could not be copied are `*_ERROR.txt` files).
            repro_status = "built"
            repro_missing_files: list[str] = []
            if wants_mode2:
                try:
                    from blueprint_arch.t3_translator import build_mode2_recipe
                    import yaml as _yaml

                    mode2_cfg, mode2_skipped = build_mode2_recipe(cfg.raw_config, _t3_by_plot)
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
                    if mode2_skipped:
                        with reactive.isolate():
                            _notify(
                                f"{len(mode2_skipped)} plot(s)' T3 steps could not be fully "
                                "baked into the reproducibility recipe (see "
                                "t3_translation_skipped in effective_run.yaml) — they are "
                                "still in the Publication content, just not engine-replayable "
                                "yet.",
                                type="warning", duration=10,
                            )
                except Exception as e:
                    zf.writestr(
                        f"{bundle_dir}/data_analysis_recipes_reproducibility/ERROR.txt", str(e)
                    )
                    mode2_skipped = {"_error": str(e)}
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
                "seeds_per_plot": seeds_per_plot_record(_plot_seeds),
                "seed_source_per_plot": seed_sources_per_plot(_plot_seeds),
                "seeds_per_layer": seeds_per_layer_record(_plot_seeds),
                "seeds_added_to_recipe": seeds_added_to_recipe(_plot_seeds, dict(all_plots)),
                "plot_warnings": _plot_warning_rows,
                "plot_warnings_unreadable": list(_warnings_unreadable),
                "t3_translation_skipped": (
                    mode2_skipped if wants_mode2 else
                    "not attempted — check 'Also include a reproducibility/reimport "
                    "bundle' to translate T3 steps into replayable recipe actions"
                ),
            }
            zf.writestr(
                f"{bundle_dir}/effective_run.yaml",
                _yaml.safe_dump(effective_run, sort_keys=False, allow_unicode=True),
            )

            # data_analysis_recipe_sha, data_sha, tiers_exported, prov — all computed before tmpdir block.

            # ── Lineage graph (ADR-074) ───────────────────────────────────
            # Shared-node DAG: one lineage_graph.json per export scope.
            # Nodes are deduplicated by schema_id+type so datasets shared
            # across multiple plots appear only once.
            _lineage_nodes: dict[str, dict] = {}
            _lineage_edges: set[tuple[str, str]] = set()
            _lineage_per_plot: dict[str, list[str]] = {}
            _lineage_ok = False
            try:
                from blueprint_arch.data_analysis_recipe_navigator import (
                    build_plot_lineage as _bpl,
                )
                _mnf_path_obj = bootloader.available_data_analysis_recipes.get(data_analysis_recipe_id)
                if _mnf_path_obj:
                    _mnf_str = str(_mnf_path_obj)
                    for _pid, _pspec in all_plots:
                        _steps = _bpl(_pid, _mnf_str)
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
                            "export_scope": scope_label,
                            "nodes": list(_lineage_nodes.values()),
                            "edges": [
                                {"from": _f, "to": _t}
                                for _f, _t in sorted(_lineage_edges)
                            ],
                            "plot_ids": [_p for _p, _ in all_plots],
                            "lineage_per_plot": _lineage_per_plot,
                            "description": (
                                "Shared-node directed acyclic graph (DAG) of the data "
                                "lineage for this export scope. "
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
                    "Chained key of the Tier 1 parquet: engine version, resolved data analysis recipe, data |"
                )
                _dh_qmd_rows.append(
                    f"| Tier 2 key ({_qp(_ds_k)}) | {_qc(_k['tier2_key'] or 'none (T2 equals T1)', True)} | "
                    "Chained key of the Tier 2 parquet: Tier 1 key and the tier2 steps of the table (a join, or a table a plot reads directly) |"
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
                "| **T3 — Audited data** | The Result with the steps the analyst sent to audit, each with a reason (for example excluding a sample that failed QC). Only audited steps are exported: filters tried while exploring are never included. The audited data of a plot is saved as `T3_data_<plot>.tsv` and its steps are listed under *T3 Audit Trail*. |",
                "",
            ]
            # ── Methods section (auto-generated from the audited T3 steps) ───
            _methods_lines = _build_methods_section(
                all_plots=all_plots,
                t3_by_plot=_t3_listed,
                ds_to_plots=ds_to_plots,
                tiers_exported=tiers_exported,
                t3_aesthetic_overrides=_t3_aesthetic_overrides,
            )
            qmd_lines += _methods_lines

            # QMD image paths point to _render/ (Quarto-compatible copies).
            # _render/ is written into the Quarto temp dir alongside report.qmd.
            # The user-facing plots/ folder in the zip keeps the chosen format.
            qmd_lines += ["## Plots", ""]
            for p_id, spec in all_plots:
                label = spec.get("title") or p_id.replace("_", " ").title()
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
                # steps, and one T3 file per plot that has audited steps and whose file was written.
                # (A plot with no target table has its plots in `__anchor__/` and its data under the key `__tier1_anchor__`.)
                _data_key = "__tier1_anchor__" if ds_key == "__anchor__" else ds_key
                _data_folder = _quote(_safe_ds_name(_data_key))
                if _data_key in exported_dfs:
                    qmd_lines.append(f"[Raw data (T1)]({_data_folder}/T1_data.tsv)")
                if _data_key in exported_t2:
                    qmd_lines.append(f"[Result data (T2)]({_data_folder}/T2_data.tsv)")
                for _plot in plot_list:
                    if (_data_key, _plot) in _t3_written:
                        qmd_lines.append(f"[Analyst-filtered data (T3) of {_qp(_plot)}]({_data_folder}/T3_data_{_quote(_plot)}.tsv)")
                qmd_lines.append("")

            # ── T3 Audit Trail section ────────────────────────────────────
            if _t3_listed:
                qmd_lines += ["## T3 Audit Trail", ""]
                for _pid, _nodes in _t3_listed.items():
                    _spec_title = next(
                        (s.get("title") for p, s in all_plots if p == _pid), None
                    )
                    _section_label = _qp(_spec_title or _pid.replace("_", " ").title())
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
            # Dataset → plots mapping block for README
            mapping_block = ["Dataset → Plots", "-" * 20]
            for ds_key, safe_ds, plot_list in mapping_rows:
                mapping_block.append(f"  {ds_key}/")
                tier_files = ["T1_data.tsv"] \
                    + (["T2_data.tsv"] if ds_key in exported_t2 else []) \
                    + ([f"T3_data_{_p}.tsv" for _p in plot_list if _p in audited_plots])
                mapping_block.append(f"    data : {', '.join(tier_files)}")
                mapping_block.append(f"    plots: {', '.join(plot_list)}")

            # Decision hashes block for README
            _dh = prov.get("decision_hashes", {})
            _dsp = prov.get("data_source_paths", {})
            _sw = prov.get("software_versions", {})
            _sw_str = ", ".join(f"{k}={v}" for k, v in _sw.items()) if _sw else "n/a"
            _dh_lines = []
            for _ds_k, _k in prov.get("stage_keys", {}).items():
                _dh_lines.append(f"  {_ds_k}: tier1_key={_k['tier1_key']}")
                _dh_lines.append(f"  {_ds_k}: tier2_key={_k['tier2_key'] or 'none (T2 equals T1)'}")
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
                f"Active tier      : {prov['active_tier']}",
                f"Export scope     : {prov['export_scope']}",
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
                f"Plots            : {prov['plot_count']}",
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
                "Stage keys (per dataset; Tier 1 and Tier 2 chained keys):",
                *_dh_lines,
                "",
                "Data source paths:",
                *(_dsp_lines if _dsp_lines else ["  n/a"]),
                "",
                *mapping_block,
                "",
                "Audited T3 steps (always applied to the plot and its data):",
                *([f"  {_p}: {len(_t3_by_plot.get(_p, []))} step(s), see t3_steps.yaml and the T3 Audit Trail in report.qmd"
                   for _p in sorted(audited_plots)] or ["  none"]),
                "",
                "Contents:",
                "  <dataset>/plots/  — rendered figures, grouped by source dataset",
                "  <dataset>/T1_data.tsv — raw assembled data (T1)",
                "  <dataset>/T2_data.tsv — processed data (T2, when steps defined)",
                "  <dataset>/T3_data_<plot>.tsv — My view data of each plot (T3, when exported): T2 (T1 when there",
                "                     are no tier2 steps) plus that plot's filters and column drops",
                "  t3_steps.yaml     — human-readable audit record (when T3 has steps)",
                "  effective_run.yaml — the full verification record: recipe/data/T3-steps/engine",
                "                     hashes, per-plot seeds. Written the same way either way (ADR-097).",
                "  lineage/          — lineage_graph.json (shared-node DAG, ADR-074)",
                "  report.qmd        — Quarto source (re-render: quarto render report.qmd)",
                rendered_note,
                "  README.txt        — this file",
                *([
                    "  data_analysis_recipes_reproducibility/<id>.yaml — frozen recipe copy with",
                    "       your audited T3 steps baked in as real wrangling actions, per plot.",
                    "       Any plot whose steps couldn't be fully baked in is named in",
                    "       effective_run.yaml's t3_translation_skipped.",
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
                "  T3 = T2 (or T1 without tier2 steps) with the steps the analyst sent to audit",
                "       (rows/columns removed, each with a reason). Only audited steps are",
                "       exported; exploration filters never are. One file per plot with",
                "       audited steps: T3_data_<plot>.tsv.",
            ]
            zf.writestr(f"{bundle_dir}/README.txt", "\n".join(readme_lines))

        with reactive.isolate():
            _build_refusal = refusal_for_build_changes(_build_changes, _view, export_keys, _notify)
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
