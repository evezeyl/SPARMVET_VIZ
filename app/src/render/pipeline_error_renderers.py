# @deps
# provides: function:render_notification, function:render_plot_overlay,
#           function:render_audit_panel_row, function:render_data_import_panel,
#           function:render_blueprint_inline, function:dispatch_pipeline_error
# consumes: shiny.ui
# consumed_by: app/src/server.py, app/handlers/home_theater.py,
#              app/handlers/audit_stack.py, app/handlers/blueprint_handlers.py,
#              app/handlers/ingestion_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#adr-079
# @end_deps
"""
Shiny UI renderers for PipelineError payloads (ADR-079).

Receives dicts produced by `make_render_payload()` (libs/utils) and never
imports PipelineError directly — surface decoupling per ADR-079 §Render.

Each renderer handles one surface value:
  plot_overlay       — overlaid card on a failed plot
  notification       — transient toast (ui.notification_show, side-effect only)
  audit_panel        — row card in the Pipeline Issues panel (notification_log)
  data_import_panel  — inline banner in the Data Import panel
  blueprint_inline   — inline message in the Blueprint IDE

Entry point: dispatch_pipeline_error(payload) routes to the correct renderer.

CSS references:
  Error banner:  background #ffe0e0 / text #d62828  (rules_css_style_spec.md §1e)
  Warning banner: background #fff3cd / text #856404 (same §)
"""
from __future__ import annotations

from shiny import ui


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _severity_classes(severity: str) -> tuple[str, str]:
    """Return (bg_color, text_color) for the given severity token."""
    if severity == "warning":
        return "#fff3cd", "#856404"
    return "#ffe0e0", "#d62828"


def _severity_label(severity: str) -> str:
    return "Warning" if severity == "warning" else "Error"


def _header_div(payload: dict) -> ui.Tag:
    bg, fg = _severity_classes(payload["severity"])
    label = _severity_label(payload["severity"])
    return ui.div(
        ui.span(f"[{label}]", style=f"color: {fg}; font-weight: 700; margin-right: 6px;"),
        ui.span(payload["title"], style="font-size: 0.85rem; font-weight: 600;"),
        style=(
            f"background: {bg}; border-left: 4px solid {fg}; "
            "padding: 6px 10px; border-radius: 4px; margin-bottom: 4px;"
        ),
    )


def _body_div(payload: dict) -> ui.Tag:
    parts = [ui.markdown(payload["body_md"])]
    if payload.get("evidence_md"):
        parts.append(ui.markdown(payload["evidence_md"]))
    if payload.get("fix_md"):
        parts.append(ui.markdown(payload["fix_md"]))
    return ui.div(*parts, style="font-size: 0.80rem; padding: 4px 10px;")


# ---------------------------------------------------------------------------
# Surface renderers
# ---------------------------------------------------------------------------

def render_notification(payload: dict) -> None:
    """Toast notification via ui.notification_show (side-effect, no return value).

    Called at any UI boundary that catches a PipelineError with
    surface='notification'. Duration is longer for errors (10 s) than warnings (6 s)
    to give the user time to read the fix hint.
    """
    _, fg = _severity_classes(payload["severity"])
    label = _severity_label(payload["severity"])
    msg = f"[{label}] {payload['title']}: {payload['body_md'].split(chr(10))[0]}"
    shiny_type = "error" if payload["severity"] == "error" else "warning"
    duration = 10 if payload["severity"] == "error" else 6
    ui.notification_show(msg, type=shiny_type, duration=duration)


def render_plot_overlay(payload: dict) -> ui.Tag:
    """Overlay card shown where a plot failed to render (surface='plot_overlay').

    The caller is responsible for positioning this over the plot card
    (e.g., replacing the plot output div with this element).
    """
    return ui.div(
        _header_div(payload),
        _body_div(payload),
        style=(
            "background: #ffffff; border: 1px solid #e9ecef; border-radius: 8px; "
            "box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 10px; "
            "max-width: 600px; margin: auto;"
        ),
    )


def render_audit_panel_row(payload: dict) -> ui.Tag:
    """Card row for the Pipeline Issues section in the notification log
    (surface='audit_panel').

    Returns a self-contained div suitable for appending to a list of
    session_pipeline_errors rendered in the right sidebar.
    """
    bg, fg = _severity_classes(payload["severity"])
    ts = payload.get("timestamp", "")
    ts_span = ui.span(ts, style="font-size: 0.65rem; color: #6c757d; float: right;") if ts else ui.span()
    return ui.div(
        ui.div(
            ts_span,
            ui.span(
                _severity_label(payload["severity"]),
                style=f"color: {fg}; font-weight: 700; font-size: 0.75rem;",
            ),
            ui.span(
                f" — {payload['title']}",
                style="font-size: 0.78rem; font-weight: 600;",
            ),
            style="margin-bottom: 2px;",
        ),
        ui.div(
            ui.markdown(payload["body_md"]),
            style="font-size: 0.78rem;",
        ),
        ui.div(
            ui.markdown(payload["fix_md"]),
            style="font-size: 0.75rem; color: #6c757d;",
        ) if payload.get("fix_md") else ui.span(),
        style=(
            f"background: {bg}; border-left: 3px solid {fg}; border-radius: 4px; "
            "padding: 6px 8px; margin-bottom: 6px;"
        ),
    )


def render_data_import_panel(payload: dict) -> ui.Tag:
    """Inline banner shown in the Data Import panel (surface='data_import_panel').

    Displayed below the file upload control when ingestion validation fails.
    """
    return ui.div(
        _header_div(payload),
        _body_div(payload),
        style="margin-top: 6px;",
    )


def render_blueprint_inline(payload: dict) -> ui.Tag:
    """Inline message in the Blueprint IDE (surface='blueprint_inline').

    Displayed below the affected YAML form section or node card.
    """
    bg, fg = _severity_classes(payload["severity"])
    return ui.div(
        ui.span(
            f"{_severity_label(payload['severity'])}: ",
            style=f"color: {fg}; font-weight: 700; font-size: 0.78rem;",
        ),
        ui.span(
            payload["body_md"].split("\n")[0],
            style="font-size: 0.78rem;",
        ),
        style=(
            f"background: {bg}; border-left: 3px solid {fg}; border-radius: 3px; "
            "padding: 4px 8px; margin-top: 4px;"
        ),
    )


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_SURFACE_RENDERERS: dict[str, object] = {
    "notification": render_notification,
    "plot_overlay": render_plot_overlay,
    "audit_panel": render_audit_panel_row,
    "data_import_panel": render_data_import_panel,
    "blueprint_inline": render_blueprint_inline,
}


def dispatch_pipeline_error(payload: dict):
    """Route a make_render_payload() dict to the correct surface renderer.

    Returns the renderer's return value (a ui.Tag for all surfaces except
    'notification', which returns None after calling ui.notification_show).

    Raises KeyError if payload['surface'] is not a known surface value —
    this should never happen if the PipelineError was constructed correctly.
    """
    surface = payload["surface"]
    renderer = _SURFACE_RENDERERS[surface]
    return renderer(payload)
