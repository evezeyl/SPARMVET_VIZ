"""libs/blueprint_arch/src/blueprint_arch/agent_context.py
System prompt builder and per-turn context builder for the BLUEPRINT AI Agent (ADR-076 §3).

Three knowledge layers:
  Layer 1 — build_system_prompt(): compressed system prompt, built once per session.
             Injected via ClaudeCliAdapter --system flag on the first turn.
  Layer 3 — build_turn_context(): small dict appended to each user turn so the
             agent reasons about what the user is currently doing.

Layer 2 (agent tools) is in agent_tools.py.
Tool-call fenced-block format is described in the system prompt — see §10.1 of ADR-076.

Constraints (Two-Category Law — ADR-045):
  Zero Shiny imports. Pure functions. Importable from headless scripts and tests.
"""

from __future__ import annotations

# @deps
# provides: function:build_system_prompt, function:build_turn_context
# consumed_by: app/handlers/blueprint_handlers.py, app/src/bootloader.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-076
# @end_deps

import textwrap
from pathlib import Path

import yaml


# ── Layer 1 — System Prompt Builder ─────────────────────────────────────────


def build_system_prompt(
    manifest_path: str | Path | None = None,
    *,
    instructions_file: str | Path | None = None,
    project_root: str | Path | None = None,
) -> str:
    """Build the compressed Layer 1 system prompt for a BLUEPRINT agent session.

    Assembles three sections:
    1. Custom instructions (from instructions_file, if provided and exists)
    2. Compressed action registry summary (from transformer ACTION_SCHEMAS)
    3. Current project context (manifest path + declared data schemas + analysis groups)

    Returns a single string ready to pass as the --system argument to claude -p.
    """
    sections: list[str] = []

    # 1. Custom instructions (operator/deployment-specific system prompt)
    instr = _load_instructions(instructions_file, project_root)
    if instr:
        sections.append(instr)

    # 2. Compressed action registry
    sections.append(_build_action_summary())

    # 3. Current project context
    if manifest_path:
        sections.append(_build_project_context(Path(manifest_path)))

    # 4. Tool-call protocol instructions (fenced-block format, ADR-076 §10.1)
    sections.append(_TOOL_CALL_PROTOCOL)

    return "\n\n---\n\n".join(s for s in sections if s.strip())


def _load_instructions(
    instructions_file: str | Path | None,
    project_root: str | Path | None,
) -> str:
    """Load the operator system prompt from instructions_file."""
    if not instructions_file:
        return ""
    path = Path(instructions_file)
    if not path.is_absolute() and project_root:
        path = Path(project_root) / path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _build_action_summary() -> str:
    """Build a compressed summary of registered transformer actions.

    Groups actions by category and emits one line per action: name + one-line doc.
    Defers import so this module is importable even without transformer installed.
    """
    try:
        from blueprint_arch.schema_registry import get_action_catalog, get_component_catalog
        actions = get_action_catalog()
        components = get_component_catalog()
    except ImportError:
        return "## Action Registry\n(transformer not installed — registry unavailable)"

    if not actions and not components:
        return "## Action Registry\n(empty — no actions or components registered)"

    by_category: dict[str, list[str]] = {}
    for name, schema in actions.items():
        cat = schema.get("category", "other")
        by_category.setdefault(cat, [])
        doc = schema.get("doc", "")
        contexts = schema.get("context", [])
        ctx_str = f" [{', '.join(contexts)}]" if contexts else ""
        by_category[cat].append(f"  {name}{ctx_str}: {doc}")

    lines = ["## Registered Transformer Actions (use only these in wrangling/assembly steps)"]
    for cat in sorted(by_category):
        lines.append(f"\n### {cat.title()}")
        lines.extend(sorted(by_category[cat]))

    if components:
        lines.append("\n## Registered VizFactory Components (use only these in plot layers)")
        for name, schema in sorted(components.items()):
            doc = schema.get("doc", "")
            lines.append(f"  {name}: {doc}")

    return "\n".join(lines)


def _build_project_context(manifest_path: Path) -> str:
    """Build a concise project context block from the active manifest."""
    if not manifest_path.exists():
        return f"## Active Manifest\nPath: {manifest_path}\n(file not found)"

    try:
        with open(manifest_path, "r") as f:
            raw = yaml.safe_load(f) or {}
    except Exception as exc:
        return f"## Active Manifest\nPath: {manifest_path}\n(parse error: {exc})"

    lines = [
        "## Active Manifest",
        f"Path: {manifest_path}",
    ]

    data_schemas = raw.get("data_schemas", {})
    if data_schemas:
        lines.append(f"\nData schemas ({len(data_schemas)}):")
        for ds_id in sorted(data_schemas.keys()):
            ds = data_schemas[ds_id]
            source = ds.get("source", {}).get("path", "(no path)")
            lines.append(f"  {ds_id}: {source}")

    if "metadata_schema" in raw:
        ms = raw["metadata_schema"]
        source = ms.get("source", {}).get("path", "(no path)")
        lines.append(f"  metadata_schema: {source}")

    groups = raw.get("analysis_groups", {})
    if groups:
        lines.append(f"\nAnalysis groups ({len(groups)}):")
        for gid, gdata in groups.items():
            label = gdata.get("label", gid)
            plots = list(gdata.get("plots", {}).keys())
            lines.append(f"  {gid} ({label}): {len(plots)} plot(s) — {', '.join(plots)}")

    return "\n".join(lines)


# Fenced-block tool-call protocol instructions (ADR-076 §10.1)
_TOOL_CALL_PROTOCOL = textwrap.dedent("""\
    ## Tool-Call Protocol (MANDATORY — read carefully)

    You have access to tools. You MUST invoke tools using this exact format — no exceptions:

    <!-- AGENT_TOOL_CALL -->
    ```json
    {
      "tool": "<tool_name>",
      "arguments": { ... }
    }
    ```
    <!-- /AGENT_TOOL_CALL -->

    Rules:
    - The marker pair <!-- AGENT_TOOL_CALL --> and <!-- /AGENT_TOOL_CALL --> MUST wrap every tool call.
    - The JSON block MUST be valid JSON (not YAML, not pseudocode).
    - Tool calls MUST use the exact tool names listed below.
    - Do NOT include free-text "here is your manifest, paste this in" output.
      ALL manifest changes go through the propose_manifest_diff tool — the user clicks Apply.
    - You may include conversational text before or after a tool call block.
    - If a tool call JSON is malformed, the server will send you an error turn to retry.

    Available tools:
      get_available_actions    — list registered actions; args: {"context": "t1|t2|assembly"}
      get_available_components — list registered viz_factory components
      get_field_contract       — get input_fields/output_fields for a schema; args: {"schema_id": "..."}
      get_data_schema_summary  — privacy-preserving column stats; args: {"schema_id": "..."}
      get_current_manifest_section — read a manifest section; args: {"section_path": "data_schemas.amr_results"}
      validate_manifest_fragment — validate candidate YAML; args: {"yaml_fragment": "..."}
      propose_manifest_diff    — THE ONLY PATH to propose changes; args: {"target": "...", "operations": [...]}

    propose_manifest_diff format:
    {
      "tool": "propose_manifest_diff",
      "arguments": {
        "target": "config/manifests/pipelines/my_pipeline.yaml",
        "operations": [
          {"op": "add", "path": "/data_schemas/amr_results/wrangling/tier1/-",
           "value": {"action": "filter_range", "columns": ["identity"], "min": 90}}
        ]
      }
    }

    IMPORTANT manifest rules (violations cause silent failures in the engine):
    - Always use "action:" key — NEVER shorthand like "- join: {...}" or "- mutate: [...]"
    - Join right-side dataset: "right_ingredient:" not "dataset_id:"
    - Quote "on" in joins: "'on':" (bare `on` is YAML boolean True)
    - One column per mutate step: separate action block for each column
    - Two-step cast for Float64→String: cast to Int64 first, then to String
    - tier1: is mandatory in wrangling blocks (even if empty)
""")


# ── Layer 3 — Per-Turn Context Builder ───────────────────────────────────────


def build_turn_context(
    *,
    active_workspace: str = "blueprint",
    active_plot_subtab: str | None = None,
    current_manifest_section: str | None = None,
    last_validation_error: dict | None = None,
    row_counts: dict | None = None,
    data_visibility: str = "schema_summary",
) -> dict:
    """Build the Layer 3 per-turn context dict appended to each user turn.

    This dict is serialised as JSON and prepended to the first turn's message,
    then omitted from subsequent turns (the conversation history carries it).

    Args:
        active_workspace: the workspace the user is in ("blueprint", "home", etc.)
        active_plot_subtab: the active plot sub-tab id (if any)
        current_manifest_section: the manifest section currently visible in the IDE
        last_validation_error: the most recent validate_manifest_fragment error dict
        row_counts: {"t1_anchor": int, "t2_branch": int} from the orchestrator
        data_visibility: "off" | "schema_summary" | "full_sample" (ADR-076 §4)
    """
    ctx: dict = {
        "active_workspace": active_workspace,
        "data_visibility": data_visibility,
    }
    if active_plot_subtab:
        ctx["active_plot_subtab"] = active_plot_subtab
    if current_manifest_section:
        ctx["current_manifest_section"] = current_manifest_section
    if last_validation_error:
        ctx["last_validation_error"] = last_validation_error
    if row_counts:
        ctx["row_counts"] = row_counts
    return ctx
