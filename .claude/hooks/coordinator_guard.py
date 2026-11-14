#!/usr/bin/env python3
"""Keeps a session in coordinator mode to its role; worker agents are not affected.

Why: in the VS Code extension the model is chosen in a drop-down and a session cannot
be started as a custom agent, so the coordinator role cannot remove tools. This
PreToolUse hook enforces it. It acts only while the marker file
tmpAI/coordinator/<session_id> exists and only for the session itself (a call from a
subagent carries an agent_id and passes). Three rules:

1. Edit, Write, MultiEdit, NotebookEdit are refused, except under tmpAI/ (agent channel,
   progress notes).
2. Bash is refused when the command runs a test suite, an audit, the app, a render or a
   script (the work belongs to the reviewer or a builder). git, gh, ls, grep and similar
   stay allowed.
3. Agent is refused when it would run on Fable or on a model the coordinator picked
   freely: allowed are the named workers (model fixed in .claude/agents/, or haiku/sonnet
   passed in the call) and any other agent whose call names model haiku or sonnet.

Fails open: any error, a missing marker or a call from a worker lets the tool run.
Marker: created by the trigger -coordinate, removed by -solo (CLAUDE.md section 2.1).
"""

import json
import os
import re
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
WORKERS = {
    "scout", "scribe", "builder", "builder-opus", "reviewer",
    "panel-scientist", "panel-architect", "panel-developer", "panel-user",
}
CHEAP_MODELS = {"haiku", "sonnet"}
# Work that belongs to a worker: suites, audits, the app, renders, scripts, installs.
WORK_COMMAND = re.compile(
    r"(pytest|run_audits|audit_[a-z_]+\.py|debug_[a-z_]+\.py|playwright|quarto\s+render"
    r"|shiny\s+run|build_dep_graph|generate_previews|refresh_gallery|ruff|pip\s+install"
    r"|uv\s+(pip|sync|run)|\.venv/bin/python|python3?\s+-m\s|python3?\s+\S+\.py)"
)


def refuse(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("agent_id"):
        return 0

    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
    session_id = str(data.get("session_id") or "")
    if not session_id or not (project / "tmpAI" / "coordinator" / session_id).exists():
        return 0

    tool = data.get("tool_name")
    tool_input = data.get("tool_input") or {}

    if tool in EDIT_TOOLS:
        target = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        try:
            Path(target).resolve().relative_to((project / "tmpAI").resolve())
            return 0
        except Exception:
            pass
        return refuse(
            "Coordinator mode: this session only coordinates. Hand this edit to a worker "
            "(builder for code and tests, scribe for records) with the Agent tool. "
            "Eve leaves coordinator mode with -solo."
        )

    if tool == "Bash":
        command = str(tool_input.get("command") or "")
        if WORK_COMMAND.search(command):
            return refuse(
                "Coordinator mode: tests, audits, scripts and renders are run by a worker "
                "(reviewer for suites and audits, builder for scripts). Bash here is for git. "
                "Eve leaves coordinator mode with -solo."
            )
        return 0

    if tool in {"Agent", "Task"}:
        kind = str(tool_input.get("subagent_type") or "")
        model = str(tool_input.get("model") or "").lower()
        # A named worker has its model fixed in .claude/agents/. Any other agent (a
        # generic or built-in one) takes the coordinator's model, Fable, unless the call
        # names a cheap model. A fork always runs on the caller's model.
        # A named worker may be given haiku or sonnet in the call (haiku for a mechanical
        # edit); opus only comes from the builder-opus definition, never from a parameter.
        if kind != "fork" and (model in CHEAP_MODELS or (kind in WORKERS and model == "")):
            return 0
        return refuse(
            "Coordinator mode: this agent would run on Fable. Use a named worker (scout, "
            "scribe, builder, builder-opus, reviewer, panel-*), or any other agent with "
            "model haiku (search, read-only) or sonnet (work). Use the cheapest agent that "
            "can do the task. See .claude/workflows/agent_dispatch_howto.md."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
