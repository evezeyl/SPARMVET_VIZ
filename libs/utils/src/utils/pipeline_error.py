# @deps
# provides: class:PipelineError, function:make_render_payload
# consumes: -
# consumed_by: app/src/render/pipeline_error_renderers.py, app/src/server.py, libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/data_wrangler.py, libs/viz_factory/src/viz_factory/viz_factory.py, app/handlers/audit_stack.py, app/handlers/blueprint_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#adr-079
# @end_deps
"""
Runtime Error Discipline (ADR-079).

Canonical home: libs/utils/ — importable by any domain lib or app layer.
No Shiny imports here; rendering is done by app/src/render/pipeline_error_renderers.py.

A `PipelineError` is a structured record for any failure that occurs *inside a running
session* (as opposed to startup failures, which are `DeploymentError` / ADR-078).

The five mandatory fields (component, problem, location, fix, who) follow the same
operator-readable shape as `DeploymentError`. Three runtime-specific mandatory fields
(category, surface) add what the runtime context demands: where in the pipeline the
failure occurred and where in the UI it should appear.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Allowed value sets — validated in __post_init__
# ---------------------------------------------------------------------------

_VALID_WHO = frozenset({"analyst", "data_provider", "manifest_author", "developer", "operator"})
_VALID_CATEGORY = frozenset({"ingestion", "wrangling", "assembly", "visualization", "t3_apply", "blueprint_edit"})
_VALID_SURFACE = frozenset({"plot_overlay", "notification", "audit_panel", "data_import_panel", "blueprint_inline"})
_VALID_SEVERITY = frozenset({"error", "warning"})

# Evidence size caps (ADR-079 §Evidence)
_MAX_SAMPLE_ROWS = 5
_MAX_SCHEMA_COLUMNS = 50


@dataclass(frozen=True)
class PipelineError:
    """Structured error record for runtime pipeline failures (ADR-079).

    Sits alongside DeploymentError (ADR-078). Does not subclass it — the audience
    model and render machinery are intentionally different.

    Mandatory fields answer five questions in the order the affected user asks them:
    WHAT broke, WHERE, HOW to fix, WHO fixes it, plus runtime-specific: WHICH stage
    failed and WHERE in the UI should this appear.
    """

    # ── ADR-078 shared shape (mandatory) ─────────────────────────────────
    component: str
    """Raising class: 'DataIngestor', 'DataAssembler', 'DataWrangler',
    'VizFactory', 'T3ApplyHandler', 'BlueprintEditor'."""

    problem: str
    """One-sentence, concrete. Names the column, action, or value that failed."""

    location: str
    """Manifest path + slug, plot_id, action step index, or uploaded-file name."""

    fix: str
    """Concrete remediation routed to the `who` audience."""

    who: str
    """'analyst' | 'data_provider' | 'manifest_author' | 'developer' | 'operator'."""

    # ── Runtime-specific (mandatory) ─────────────────────────────────────
    category: str
    """Pipeline stage: 'ingestion' | 'wrangling' | 'assembly' | 'visualization'
    | 't3_apply' | 'blueprint_edit'."""

    surface: str
    """UI render target: 'plot_overlay' | 'notification' | 'audit_panel'
    | 'data_import_panel' | 'blueprint_inline'."""

    # ── Runtime-specific (optional) ───────────────────────────────────────
    evidence: dict | None = None
    """Diagnostic payload. Conventional keys (all optional):
      'sample_rows': list[dict]  — up to 5 rows showing the problem
      'offending_value': Any     — the single value that triggered the failure
      'expected_schema': dict    — column → dtype expected
      'actual_schema':   dict    — column → dtype seen
      'row_count_before': int    — pre-step row count
      'row_count_after':  int    — post-step row count (0 = filter removed all)
      'near_match':      str     — typo suggestion ("did you mean …")
      'file_path':       str     — uploaded file name (ingestion errors)
    Unknown keys are rendered as generic key-value rows."""

    severity: str = "error"
    """'error' (operation aborted) | 'warning' (succeeded with caveat)."""

    plot_scope: tuple[str, ...] = field(default_factory=tuple)
    """plot_ids whose card should show a plot_overlay. Empty = session-wide."""

    reference: str = ""
    """ADR / rule-file pointer (same semantics as DeploymentError)."""

    timestamp: str = ""
    """ISO-8601 string. Populated by the UI boundary that catches the error
    so ordering is preserved across concurrent renders."""

    related: tuple[str, ...] = field(default_factory=tuple)
    """Other field IDs / step IDs that contributed to the failure."""

    def __post_init__(self) -> None:
        if self.who not in _VALID_WHO:
            raise ValueError(f"PipelineError.who must be one of {sorted(_VALID_WHO)}, got {self.who!r}")
        if self.category not in _VALID_CATEGORY:
            raise ValueError(f"PipelineError.category must be one of {sorted(_VALID_CATEGORY)}, got {self.category!r}")
        if self.surface not in _VALID_SURFACE:
            raise ValueError(f"PipelineError.surface must be one of {sorted(_VALID_SURFACE)}, got {self.surface!r}")
        if self.severity not in _VALID_SEVERITY:
            raise ValueError(f"PipelineError.severity must be one of {sorted(_VALID_SEVERITY)}, got {self.severity!r}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def format(self) -> str:
        """Render as a labelled block for test output / server logs.

        Parallels DeploymentError.format() so both classes produce the same
        grep-friendly output in CI and headless runs.
        """
        severity_tag = "[ERROR]" if self.severity == "error" else "[WARN]"
        lines = [
            f"{severity_tag} {self.problem}",
            f"  Component:  {self.component}",
            f"  Category:   {self.category}",
            f"  Location:   {self.location}",
            f"  Fix ({self.who}): {self.fix}",
            f"  Surface:    {self.surface}",
        ]
        if self.timestamp:
            lines.append(f"  Timestamp:  {self.timestamp}")
        if self.reference:
            lines.append(f"  See:        {self.reference}")
        if self.plot_scope:
            lines.append(f"  Plots:      {', '.join(self.plot_scope)}")
        if self.related:
            lines.append(f"  Related:    {', '.join(self.related)}")
        if self.evidence:
            lines.append("  Evidence:")
            for k, v in self.evidence.items():
                v_repr = repr(v)[:80] + ("…" if len(repr(v)) > 80 else "")
                lines.append(f"    {k}: {v_repr}")
        return "\n".join(lines)

    def to_audit_row(self) -> dict:
        """Return a compact dict for the export-bundle audit appendix (ADR-069).

        Keys are stable across versions — downstream formatters depend on them.
        """
        return {
            "timestamp": self.timestamp,
            "severity": self.severity,
            "category": self.category,
            "component": self.component,
            "problem": self.problem,
            "location": self.location,
            "who": self.who,
            "fix": self.fix,
            "surface": self.surface,
            "plot_scope": list(self.plot_scope),
            "reference": self.reference,
            "has_evidence": self.evidence is not None,
        }

    def with_timestamp(self) -> "PipelineError":
        """Return a copy of this error with `timestamp` set to now (ISO-8601).

        Intended for use at the UI boundary where the error is caught and appended
        to `session_pipeline_errors`. Library code raises without a timestamp;
        the handler adds it on receipt.
        """
        return PipelineError(
            component=self.component,
            problem=self.problem,
            location=self.location,
            fix=self.fix,
            who=self.who,
            category=self.category,
            surface=self.surface,
            evidence=self.evidence,
            severity=self.severity,
            plot_scope=self.plot_scope,
            reference=self.reference,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            related=self.related,
        )


# ---------------------------------------------------------------------------
# Render payload converter — the single Shiny-free conversion point
# ---------------------------------------------------------------------------

def make_render_payload(error: PipelineError) -> dict:
    """Convert a PipelineError to a UI-render payload dict.

    This is the only place where PipelineError data is shaped for display.
    UI renderers (app/src/render/pipeline_error_renderers.py) receive this
    dict and never import PipelineError directly — surface decoupling per ADR-079.

    Returned keys:
      title      str   — short display heading
      body_md    str   — Markdown paragraph with problem + location
      evidence_md str  — Markdown table from evidence dict (empty string if None)
      fix_md     str   — Markdown blockquote with fix + who chip
      severity   str   — "error" | "warning"
      surface    str   — routing key for the caller
      plot_scope list  — plot_ids (may be empty)
      timestamp  str
    """
    evidence_md = _format_evidence_md(error.evidence) if error.evidence else ""

    who_label = {
        "analyst": "Analyst",
        "data_provider": "Data Provider",
        "manifest_author": "Manifest Author",
        "developer": "Developer",
        "operator": "Operator",
    }.get(error.who, error.who.title())

    body_md = f"**{error.problem}**"
    if error.location:
        body_md += f"\n\n*Location:* `{error.location}`"

    fix_md = f"> **Fix ({who_label}):** {error.fix}"
    if error.reference:
        fix_md += f"\n> *See:* {error.reference}"

    return {
        "title": f"{error.component} — {error.category}",
        "body_md": body_md,
        "evidence_md": evidence_md,
        "fix_md": fix_md,
        "severity": error.severity,
        "surface": error.surface,
        "plot_scope": list(error.plot_scope),
        "timestamp": error.timestamp,
        "who": error.who,
        "who_label": who_label,
        "category": error.category,
        "component": error.component,
    }


def _format_evidence_md(evidence: dict) -> str:
    """Render evidence dict as a Markdown table / list for display."""
    if not evidence:
        return ""

    parts: list[str] = []

    # sample_rows → Markdown table (capped at _MAX_SAMPLE_ROWS)
    sample_rows = evidence.get("sample_rows")
    if sample_rows and isinstance(sample_rows, list):
        rows = sample_rows[:_MAX_SAMPLE_ROWS]
        if rows and isinstance(rows[0], dict):
            cols = list(rows[0].keys())
            header = "| " + " | ".join(cols) + " |"
            sep = "| " + " | ".join("---" for _ in cols) + " |"
            body_rows = ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
            parts.append("\n".join([header, sep] + body_rows))
            if len(sample_rows) > _MAX_SAMPLE_ROWS:
                parts.append(f"*…{len(sample_rows) - _MAX_SAMPLE_ROWS} more rows truncated*")

    # schema diff → two-column table
    expected = evidence.get("expected_schema", {})
    actual = evidence.get("actual_schema", {})
    if expected or actual:
        all_cols = sorted(set(list(expected.keys())[:_MAX_SCHEMA_COLUMNS] + list(actual.keys())[:_MAX_SCHEMA_COLUMNS]))
        schema_rows = [f"| `{c}` | {expected.get(c, '—')} | {actual.get(c, '—')} |" for c in all_cols]
        parts.append(
            "| Column | Expected | Actual |\n|---|---|---|\n" + "\n".join(schema_rows)
        )

    # scalar keys → key-value list
    scalar_keys = [k for k in evidence if k not in ("sample_rows", "expected_schema", "actual_schema")]
    for k in scalar_keys:
        v = evidence[k]
        parts.append(f"**{k}:** `{v}`")

    return "\n\n".join(parts)
