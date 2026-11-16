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

4. Bash that WRITES files is refused (Eve, 2026-11-14: the coordinator must delegate every
   edit): sed -i, tee, redirections to a file outside tmpAI/, rm/mv/cp/ln/patch outside
   tmpAI/, git apply/restore/checkout --, and python used inline. git commit, merge, log,
   diff, status, worktree stay allowed.

5. Agent that starts a builder, builder-opus or reviewer is refused when its brief has neither a
   "Decisions" block whose numbers all exist in the decision ledger nor a line "NONE-CHECKED: <path>"
   whose path is a regular file inside the project folder, not the ledger itself (Eve, 2026-11-16,
   M150 point 4; ledger D-0125). Only the form is
   checked: the reviewer checks the content. Scouts, scribes and panel agents are not gated. A ledger
   that is missing or malformed refuses the call too (a check that cannot run must not pass). The ledger is read with
   assets/scripts/decision_ledger.py; the form of the block is in .claude/workflows/decision_compliance.md.

There is no exception inside the hook: when a refusal is a real minor case (a one-line
fix), the coordinator STOPS its coordination work and tells Eve, who answers or runs -solo.

Fails open: any error, a missing marker or a call from a worker lets the tool run.
Marker: created by the trigger -coordinate, removed by -solo (CLAUDE.md section 2.1).
"""

import importlib.util
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
# Workers whose brief must quote decisions (M150 point 4); scouts and scribes are exempt.
DECISION_GATED = {"builder", "builder-opus", "reviewer"}
LEDGER_RELATIVE = Path(".claude/knowledge/decision_ledger.md")
LEDGER_SCRIPT = Path(__file__).resolve().parents[2] / "assets" / "scripts" / "decision_ledger.py"
DECISIONS_HEADING = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?decisions(?:\*\*)?\s*(?::.*|\(.*)?$", re.IGNORECASE)
NONE_CHECKED = re.compile(r"^\s*(?:[-*]\s*)?NONE-CHECKED:\s*(\S+)", re.MULTILINE)
DECISION_TOKEN = re.compile(r"\bD-\d+\b")
HOW_TO_WRITE = (
    "Write it in the brief: a line `Decisions`, then one line per decision, each with its number and her words, e.g. "
    '`- D-0112: "Best hit = highest identity first; ..."` (numbers: ./.venv/bin/python assets/scripts/decision_ledger.py list; '
    "file .claude/knowledge/decision_ledger.md). When a scout checked that no decision applies, write instead a line "
    "`NONE-CHECKED: <path of the saved scout report>` (a regular file inside the project folder; not the ledger). See .claude/workflows/decision_compliance.md section 6."
)
# Work that belongs to a worker: suites, audits, the app, renders, scripts, installs.
WORK_COMMAND = re.compile(
    r"(pytest|run_audits|audit_[a-z_]+\.py|debug_[a-z_]+\.py|playwright|quarto\s+render"
    r"|shiny\s+run|build_dep_graph|generate_previews|refresh_gallery|ruff|pip\s+install"
    r"|uv\s+(pip|sync|run)|\.venv/bin/python|python3?\s+-m\s|python3?\s+\S+\.py)"
)


def _strip_quotes_and_heredocs(command: str) -> str:
    """Remove heredoc bodies and quoted text so a message such as 'a -> b' is not read as a redirect."""
    command = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\b", " ", command, flags=re.S)
    command = re.sub(r"'[^']*'", "''", command)
    command = re.sub(r'"[^"]*"', '""', command)
    return command


def _inside_tmpai(path: str) -> bool:
    path = path.strip().strip("'\"")
    return (path in ("/dev/null", "/dev/stderr", "/dev/stdout") or path.startswith(("tmpAI/", "./tmpAI/", "/tmp/"))
            or "/tmpAI/" in path)


def bash_writes_files(command: str) -> str:
    """Return a short reason when the command writes a file outside tmpAI/, else an empty string."""
    text = _strip_quotes_and_heredocs(command)
    if re.search(r"\bsed\s+(-[A-Za-z]*i|--in-place)", text) or re.search(r"\bperl\s+-[A-Za-z]*i", text):
        return "an in-place edit (sed -i, perl -i)"
    if re.search(r"\b(git\s+(apply|restore)|git\s+checkout\s+--)", text):
        return "a git command that rewrites files"
    if re.search(r"\bpython3?\b\s*(-c\b|-\s|-$|<<)", text) or re.search(r"\bpython3?\b\s*$", text):
        return "inline Python (it can write any file)"
    for match in re.finditer(r"(?<![0-9&<>])>>?(?!&)\s*([^\s&|;<>]+)", text):
        if not _inside_tmpai(match.group(1)):
            return "a redirection to " + match.group(1)
    for match in re.finditer(r"\btee\b((?:\s+-[A-Za-z]+)*)\s+([^\s&|;]+)", text):
        if not _inside_tmpai(match.group(2)):
            return "tee to " + match.group(2)
    for match in re.finditer(r"(?:^|[;&|]\s*|\n\s*)(rm|mv|cp|ln|patch|truncate|install)\b([^;&|\n]*)", text):
        paths = [t for t in match.group(2).split() if not t.startswith("-")]
        if any(not _inside_tmpai(t) for t in paths):
            return match.group(1) + " on a path outside tmpAI/"
    return ""


def _decisions_block(brief: str) -> str:
    """Return the text of the "Decisions" block of a brief: its heading line to the next blank line or heading."""
    lines = brief.split("\n")
    for start, text in enumerate(lines):
        if DECISIONS_HEADING.match(text):
            block = [text]
            for more in lines[start + 1:]:
                if not more.strip() or more.lstrip().startswith("#"):
                    break
                block.append(more)
            return "\n".join(block)
    return ""


def _load_ledger_reader():
    spec = importlib.util.spec_from_file_location("decision_ledger", LEDGER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _none_checked_problem(written: str, project: Path) -> str:
    """Return why a NONE-CHECKED path is not accepted, or an empty string.

    Accepted: a regular file INSIDE the project folder (the saved scout report), other than the ledger itself.
    Only surrounding quotes and trailing punctuation are removed from the written path: a leading dot is part of it.
    """
    text = written.strip("`'\"").rstrip("`'\".,;")
    path = Path(text)
    resolved = (path if path.is_absolute() else project / path).resolve()
    try:
        resolved.relative_to(project.resolve())
    except ValueError:
        return f"NONE-CHECKED names {text}, which is outside the project folder (it must be the saved scout report, inside the project)"
    if resolved == (project / LEDGER_RELATIVE).resolve():
        return "NONE-CHECKED names the ledger itself, which is not a scout report"
    if not resolved.is_file():
        return f"NONE-CHECKED names {text}, which is not a regular file that exists (a directory or a device does not count)"
    return ""


def brief_problem(brief: str, project: Path) -> str:
    """Return what is missing in the brief of a builder or reviewer (an empty string when the form is right)."""
    missing_file = ""
    found = NONE_CHECKED.search(brief)
    if found:
        missing_file = _none_checked_problem(found.group(1), project)
        if not missing_file:
            return ""
    ledger = project / LEDGER_RELATIVE
    try:
        reader = _load_ledger_reader()
    except Exception as error:
        return f"the ledger reader {LEDGER_SCRIPT} cannot be loaded ({error}), so no decision number can be checked."
    cited = DECISION_TOKEN.findall(_decisions_block(brief))
    try:
        not_in_ledger = reader.missing_numbers(cited, ledger)
    except FileNotFoundError:
        return f"the decision ledger {LEDGER_RELATIVE} does not exist, so no decision number can be checked."
    except ValueError as error:
        return f"the decision ledger cannot be read ({error}); fix it first."
    if cited and not not_in_ledger:
        return ""
    if not_in_ledger:
        reason = "the Decisions block cites " + ", ".join(not_in_ledger) + ", not in the ledger"
    elif _decisions_block(brief):
        reason = "the Decisions block holds no decision number (D-0001 form)"
    else:
        reason = "the brief has no Decisions block" + ("" if found else " and no NONE-CHECKED line")
    return "; ".join(x for x in (reason, missing_file) if x) + "."


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
            "If it is a real minor case, stop your coordination and tell Eve. "
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
        reason = bash_writes_files(command)
        if reason:
            return refuse(
                "Coordinator mode: " + reason + " writes files, and the coordinator does not edit. "
                "Hand it to a worker (builder, scribe) with the Agent tool. If it is a real minor "
                "case, stop and tell Eve. Eve leaves coordinator mode with -solo."
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
            if kind in DECISION_GATED:
                problem = brief_problem(str(tool_input.get("prompt") or ""), project)
                if problem:
                    return refuse(
                        f"Coordinator mode: the brief for a {kind} must quote the decisions it depends on (M150): "
                        + problem + " " + HOW_TO_WRITE
                    )
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
