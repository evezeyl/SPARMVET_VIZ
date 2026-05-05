# app/modules/exporter.py
# @deps
# provides: class:SubmissionExporter, function:generate_methods_text, function:render_audit_report
# consumed_by: app/handlers/gallery_handlers.py, app/src/server.py, app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-033, .claude/rules/ui_implementation_contract.md#12f
# @end_deps
import zipfile
import pandas as pd
import yaml
import subprocess
from pathlib import Path
from datetime import datetime


class SubmissionExporter:
    """Handles the creation of the SPARMVET Submission Package (.zip)."""

    def __init__(self, export_dir: str = "tmp/exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def create_audit_log(self, narrative: list, project_id: str = "ABROMICS_DEMO") -> str:
        """Converts the narrative log into a human-readable audit trace via Pandoc."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        md_path = self.export_dir / "audit_log.md"
        txt_path = self.export_dir / "audit_log.txt"

        # 1. Draft the Markdown trace
        with open(md_path, "w") as f:
            f.write(f"# SPARMVET AUDIT LOG: {project_id}\n")
            f.write(f"Generated: {ts}\n\n")
            f.write("## 📜 Narrative Trace (ADR-026)\n")
            for entry in narrative:
                f.write(f"- {entry}\n")

        # 2. Convert to Text/Docx via Pandoc
        try:
            subprocess.run(["pandoc", str(md_path), "-o",
                           str(txt_path)], check=True)
            return str(txt_path)
        except Exception:
            return str(md_path)  # Fallback to markdown if pandoc fails

    def bundle_package(self, plot_path: str, data_df: pd.DataFrame, manifest: dict, audit_trail: list) -> str:
        """Creates the final .zip Submission Package."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = self.export_dir / f"submission_{ts}.zip"

        # 1. Prep individual files
        audit_path = self.create_audit_log(audit_trail)
        data_path = self.export_dir / "data_subset.csv"
        data_df.to_csv(data_path, index=False)

        manifest_path = self.export_dir / "active_recipe.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest, f)

        # 2. Build the Zip
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(audit_path, arcname="audit_log.txt")
            zipf.write(data_path, arcname="data_subset.csv")
            zipf.write(manifest_path, arcname="active_recipe.yaml")
            if plot_path and Path(plot_path).exists():
                zipf.write(plot_path, arcname="high_dpi_plot.png")

        return str(zip_path)

    def bundle_global_export(self, project_id: str, plot_path: str, tiers: dict, manifest: dict, audit_trail: list) -> str:
        """
        Bundles the full session state (Phase 14-C).
        Format: SPARMVET_EXPORT_{ISO_DATE}_{PROJECT_ID}.zip
        """
        iso_date = datetime.now().strftime("%Y-%m-%d")
        zip_name = f"SPARMVET_EXPORT_{iso_date}_{project_id}.zip"
        zip_path = self.export_dir / zip_name

        # 1. Prep individual files
        audit_path = self.create_audit_log(audit_trail, project_id)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(audit_path, arcname="audit_log.txt")

            # YAML Manifest
            manifest_path = self.export_dir / "session_manifest.yaml"
            with open(manifest_path, "w") as f:
                yaml.dump(manifest, f)
            zipf.write(manifest_path, arcname="session_manifest.yaml")

            # Tiers 1-3 Data
            for tier_name, df in tiers.items():
                if df is not None:
                    t_path = self.export_dir / f"{tier_name}.csv"
                    df.to_csv(t_path, index=False)
                    zipf.write(t_path, arcname=f"data/{tier_name}.csv")

            # Plot
            if plot_path and Path(plot_path).exists():
                zipf.write(plot_path, arcname="preview_plot.png")

            # Educational Metadata Template (ADR-033/Phase 14-C)
            meta_template = f"""# Recipe Metadata: {project_id}
## Family (Purpose): [Distribution | Correlation | Comparison | Ranking]
## Data Pattern: [1 Numeric | 2 Numeric | 1 Numeric, 1 Categorical]
## Difficulty: [Simple | Intermediate | Advanced]

## Suitability
- [Describe when this visualization is most useful]

## Data Schema (Tier 1)
- [List required columns and types]

## Transformation Logic (Tier 2)
- [Describe essential reshapes]

## Interpretations
- [Assumptions, limitations, and comments]

## Inspiration & Resources
- [Link to community resource or R Graph Gallery](https://r-graph-gallery.com/)
"""
            meta_path = self.export_dir / "recipe_meta.md"
            with open(meta_path, "w") as f:
                f.write(meta_template)
            zipf.write(meta_path, arcname="recipe_meta.md")

        return str(zip_path)


# ---------------------------------------------------------------------------
# Phase 22-E: Audit Report generation (§12f)
# ---------------------------------------------------------------------------

def generate_methods_text(t3_recipe: list) -> tuple:
    """Convert active T3 RecipeNodes into plain-English Methods lines.

    Phase 22-J / ADR-049: handles propagated nodes (multiple copies sharing
    `id`) by deduplicating on `id` and listing all target plot scopes in
    one Methods line. Nodes with `primary_key_warning: true` are prefixed
    with ⚠️ [Primary key affected] (§12g.11) — the marker persists into
    HTML/PDF/DOCX outputs.

    Returns:
        (methods_lines, discarded_nodes)
        methods_lines  — list of strings for active nodes only
        discarded_nodes — list of node dicts with active=False (legacy)
    """
    methods: list = []
    discarded: list = []

    # Dedupe propagated copies: group by id, collect all plot_scopes.
    seen: dict = {}
    order: list[str] = []
    for node in t3_recipe:
        if not node.get("active", True):
            discarded.append(node)
            continue
        nid = node.get("id", "")
        if not nid:
            # Anonymous node (shouldn't happen in current code) — render once.
            nid = f"_anon_{len(seen)}"
        if nid not in seen:
            seen[nid] = {**node, "_plot_scopes": []}
            order.append(nid)
        scope = node.get("plot_scope", "")
        if scope and scope not in seen[nid]["_plot_scopes"]:
            seen[nid]["_plot_scopes"].append(scope)

    for nid in order:
        node = seen[nid]
        p = node.get("params", {})
        nt = node.get("node_type", "")
        reason = node.get("reason", "—")
        scopes = node.get("_plot_scopes", []) or []
        if len(scopes) == 0:
            scope_str = ""
        elif len(scopes) == 1:
            scope_str = f" (plot: {scopes[0]})"
        else:
            scope_str = f" (plots: {', '.join(scopes)})"
        prefix = "⚠️ [Primary key affected] " if node.get("primary_key_warning") else ""

        if nt == "filter_row":
            col = p.get("column", "?")
            op = p.get("op", "?")
            val = p.get("value", "?")
            methods.append(
                f"{prefix}Rows were filtered to include only `{col}` {op} `{val}`{scope_str}. "
                f"Reason: {reason}."
            )
        elif nt == "exclusion_row":
            col = p.get("column", "?")
            val = p.get("value", "?")
            methods.append(
                f"{prefix}The following `{col}` values were explicitly excluded: `{val}`{scope_str}. "
                f"Reason: {reason}."
            )
        elif nt == "drop_column":
            col = p.get("column", "?")
            methods.append(
                f"{prefix}Column `{col}` was permanently removed from the exported dataset{scope_str}. "
                f"Reason: {reason}."
            )
        elif nt == "aesthetic_override":
            keys = [k for k in ("fill", "colour", "alpha", "shape") if k in p]
            methods.append(
                f"Plot aesthetics were adjusted{scope_str}: {', '.join(keys) or 'overrides'}."
            )
        elif nt == "developer_raw_yaml":
            methods.append(
                f"{prefix}A custom manifest fragment was applied{scope_str}. "
                f"Reason: {reason}."
            )

    return methods, discarded


def render_audit_report(
    home_state: dict,
    session_key: str,
    output_dir,
    manifest_id: str = "",
    deployment_profile: str = "local",
    figure_paths=None,
    dataset_summaries=None,
    fmt: str = "html",
):
    """Render the audit report into output_dir via Quarto.

    Phase 25-K (ADR-052-FOLLOWUP-1): Quarto renders HTML, PDF, and DOCX
    natively. Pandoc is no longer a runtime dependency for this path.

    Parameters
    ----------
    fmt : {"html", "pdf", "docx"}
        Output format. Quarto is invoked with `--to <fmt>`.

    Returns
    -------
    Path
        Path to the rendered file. If Quarto is unavailable or fails for the
        requested format, returns the rendered `.qmd` source so the caller
        can surface the failure to the user.
    """
    import json
    import hashlib
    from datetime import datetime, timezone

    fmt = (fmt or "html").lower()
    if fmt not in ("html", "pdf", "docx"):
        raise ValueError(f"Unsupported audit-report format: {fmt!r}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Phase 22-J: per-plot stacks. Flatten for the report — generate_methods_text
    # dedupes propagated copies (linked id) and lists all target scopes in one
    # Methods line.
    by_plot = home_state.get("t3_recipe_by_plot", {}) or {}
    t3_recipe = [n for nodes in by_plot.values() for n in nodes]
    manifest_sha256 = home_state.get("manifest_sha256") or ""
    tier_toggle = home_state.get("tier_toggle", "T2")

    active_recipe = [n for n in t3_recipe if n.get("active", True)]
    t3_recipe_sha256 = hashlib.sha256(
        json.dumps(active_recipe, sort_keys=True).encode()
    ).hexdigest()

    methods_lines, discarded_nodes = generate_methods_text(t3_recipe)
    now = datetime.now(timezone.utc)
    export_ts = now.strftime("%Y-%m-%dT%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")

    report_data = {
        "manifest_id": manifest_id,
        "manifest_sha256": manifest_sha256,
        "t3_recipe_sha256": t3_recipe_sha256,
        "session_key": session_key,
        "tier_toggle": tier_toggle,
        "methods_text": methods_lines,
        "discarded_nodes": discarded_nodes,
        "active_recipe": active_recipe,
        "figures": figure_paths or [],
        "datasets": dataset_summaries or [],
    }
    (output_dir / "report_data.json").write_text(json.dumps(report_data, indent=2))

    template_path = Path(__file__).parent.parent / "assets" / "report_template.qmd"
    if not template_path.exists():
        template_path = Path("app/assets/report_template.qmd")

    template = template_path.read_text() if template_path.exists() else _FALLBACK_TEMPLATE
    filled = template
    for key, val in {
        "{{date}}": date_str,
        "{{manifest_id}}": manifest_id or "—",
        "{{manifest_sha256}}": (manifest_sha256[:16] + "…") if manifest_sha256 else "—",
        "{{t3_recipe_sha256}}": t3_recipe_sha256[:16] + "…",
        "{{deployment_profile}}": deployment_profile,
        "{{export_timestamp}}": export_ts,
    }.items():
        filled = filled.replace(key, val)

    qmd_path = output_dir / "report.qmd"
    qmd_path.write_text(filled)

    out_path = output_dir / f"report.{fmt}"
    try:
        result = subprocess.run(
            ["quarto", "render", str(qmd_path), "--to", fmt,
             "--output", out_path.name],
            capture_output=True, text=True, timeout=180,
            cwd=str(output_dir),
        )
        if result.returncode == 0 and out_path.exists():
            return out_path
    except Exception:
        pass

    return qmd_path


_FALLBACK_TEMPLATE = """---
title: "SPARMVET Audit Report"
date: "{{date}}"
---

## Study Context

Manifest: {{manifest_id}} | SHA256: {{manifest_sha256}}
Exported: {{export_timestamp}}

## Methods

*(Quarto template not found — see report_data.json for full detail)*
"""
