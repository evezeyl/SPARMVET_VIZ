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

5. Agent that would run (a named worker or any agent on haiku or sonnet) is refused when its brief has neither a
   "Decisions" block whose numbers are all lines of the decision ledger that are DECIDED and taken by EVE nor a
   line "NONE-CHECKED: <path>" whose path is a regular file inside the project folder, not the ledger itself
   (Eve, 2026-11-16: M150 point 4, D-0125; every agent but scout, scribe and the panel agents is gated, D-0156;
   empty lines right after the heading are skipped, D-0157; a RELAYED, PROVISIONAL or NOT-STATED number is
   refused with its status, D-0159). Only the form is checked: the reviewer checks the content. A ledger
   that is missing, unreadable, malformed or empty refuses the call too, also when the brief has a valid NONE-CHECKED line (D-0158: a
   check that cannot run must not pass); a Decisions block that cites a number that is not DECIDED by EVE refuses the call also
   when a valid NONE-CHECKED line is present; numbers are read without regard to case (fix round of DECISION-RULES-2, the
   coordinator's instruction, not Eve's words). Each number must be followed, in the same list item, by quoted words that appear
   in THAT ledger line: a contiguous piece of its decision or evidence field, "..." marks a cut, case, quotation marks and runs
   of spaces are ignored, a quote of fewer than 12 characters does not count (D-0166; the exact definition is in
   .claude/workflows/decision_compliance.md section 6). The ledger is read with
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
# Agents that need no Decisions block (D-0156): read-only search, the records, and the panel viewpoints (they only
# recommend). Every other agent that may run, general ones included, must quote decisions. A panel name is listed one
# by one: a name that only starts with "panel-" is not exempt.
DECISION_EXEMPT = {"scout", "scribe", "panel-scientist", "panel-architect", "panel-developer", "panel-user"}
LEDGER_RELATIVE = Path(".claude/knowledge/decision_ledger.md")
LEDGER_SCRIPT = Path(__file__).resolve().parents[2] / "assets" / "scripts" / "decision_ledger.py"
DECISIONS_HEADING = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?decisions(?:\*\*)?\s*(?::.*|\(.*)?$", re.IGNORECASE)
NONE_CHECKED = re.compile(r"^\s*(?:[-*]\s*)?NONE-CHECKED:\s*(\S+)", re.MULTILINE)
DECISION_TOKEN = re.compile(r"\bD-\d+\b", re.IGNORECASE)
# One list item of the Decisions block starts with a decision number (after an optional list marker and bold or code marks).
LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
ITEM_START = re.compile(r"^\s*(?:(?:[-*+]|\d+[.)])\s+)?(?:\*\*|`)?(D-\d+)\b", re.IGNORECASE)
QUOTE = re.compile(r'"([^"]*)"|\u201c([^\u201d]*)\u201d')
QUOTATION_MARKS = '"\u201c\u201d\u201e\u00ab\u00bb'
# What counts as quoted words of a ledger line (D-0166, point 6 option C; the numbers are the builder's proposal):
# a quote counts when its pieces, joined, hold at least MIN_QUOTE characters (the shortest words of hers that a brief quotes,
# "ok - decided", are 12; shorter ones such as "yes", "a)" or "4. B." occur in many lines and do not show that the
# writer read the line) and every piece between two cuts ("..." or the ellipsis character) holds at least MIN_PIECE.
MIN_QUOTE = 12
MIN_PIECE = 4
HOW_TO_WRITE = (
    "Write it in the brief: a line `Decisions`, then one list item per decision: its number, then her words (or the words of the decision) from THAT ledger line between quotation marks, e.g. "
    '`- D-0112: "yes - if same identity favor the one that has higest overlap/coverage."` (only a line that is DECIDED and taken by EVE counts; numbers: ./.venv/bin/python assets/scripts/decision_ledger.py list --status DECIDED; '
    "file .claude/knowledge/decision_ledger.md). A quote is a contiguous piece of the decision or of the evidence (her words) of that line, at least 12 characters, `...` marks a cut, case and quotation marks and runs of spaces do not matter (decision_compliance.md section 6). When a scout checked that no decision applies and none is needed, write instead a line "
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
    """Return the text of the "Decisions" block of a brief: its heading line to the next blank line or heading.

    Empty lines directly after the heading are skipped (D-0157): the writer who leaves one is read, not refused.
    """
    lines = brief.split("\n")
    for start, text in enumerate(lines):
        if DECISIONS_HEADING.match(text):
            block = [text]
            rest = lines[start + 1:]
            while rest and not rest[0].strip():
                rest = rest[1:]
            for more in rest:
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


def _normalise(text: str) -> str:
    """Lower case, quotation marks removed, curly apostrophes made straight, runs of spaces made one."""
    for mark in QUOTATION_MARKS:
        text = text.replace(mark, "")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    return " ".join(text.casefold().split())


def _quote_pieces(quote: str) -> list:
    """Split a quote at its cuts ("..." or the ellipsis character) into normalised pieces; empty pieces are dropped."""
    return [p for p in (_normalise(x) for x in re.split(r"\.\.\.|\u2026", quote)) if p]


def _counts_as_quote(pieces: list) -> bool:
    return sum(len(p) for p in pieces) >= MIN_QUOTE and all(len(p) >= MIN_PIECE for p in pieces)


def _appears(pieces: list, entry: dict) -> bool:
    """True when every piece is found, in order and without overlap, in the decision field or in the evidence field."""
    for field in ("decision", "evidence"):
        haystack, at = _normalise(entry[field]), 0
        for piece in pieces:
            at = haystack.find(piece, at)
            if at < 0:
                break
            at += len(piece)
        else:
            return True
    return False


def _line_start(number: str, entry: dict) -> str:
    return f"{number} | {entry['date']} | {entry['area']} | {entry['decision'][:110]}" + ("..." if len(entry["decision"]) > 110 else "")


def _example(number: str, entry: dict) -> str:
    """A list item that the hook would accept for this line: its number and the first words of its decision field."""
    words = _normalise(entry["decision"])[:60]
    if " " in words and len(entry["decision"]) > 60:
        words = words.rsplit(" ", 1)[0]
    return f'- {number}: "{words}"'


def _items(block: str) -> tuple:
    """Return (numbers of the block outside quotes that start no item, [(number, text of the item), ...]).

    An item starts at a line that begins (after an optional list marker) with a decision number; the lines that follow and
    are not themselves a list item belong to it. The heading line is no item: a number there has no quoted words.
    """
    lines = block.split("\n")
    items, current = [], None
    for line in lines[1:]:
        start = ITEM_START.match(line)
        if start:
            current = [start.group(1).upper(), line]
            items.append(current)
        elif LIST_MARKER.match(line):
            current = None
        elif current is not None:
            current[1] += "\n" + line
    starts = {n for n, _ in items}
    outside = QUOTE.sub("", block)
    bare = [n.upper() for n in DECISION_TOKEN.findall(outside) if n.upper() not in starts]
    return bare, items


def _quote_problems(block: str, entries: dict) -> list:
    """What is wrong with the quoted words of each decided number of the block (D-0166)."""
    bare, items = _items(block)
    problems = []
    seen = set()
    for number in bare:
        if number in seen or number not in entries:
            continue
        seen.add(number)
        problems.append(f"{number} stands outside a list item of its own (on the heading line, or inside another item), so it has no quoted words: write it as a new line "
                        f"that starts with a dash and the number, then words from that ledger line between quotation marks, at least {MIN_QUOTE} characters, for example "
                        f"{_example(number, entries[number])} (the line starts: {_line_start(number, entries[number])})")
    for number, text in items:
        entry = entries.get(number)
        if entry is None:
            continue
        quotes = [(a or b) for a, b in QUOTE.findall(text)]
        counted = [q for q in quotes if _counts_as_quote(_quote_pieces(q))]
        start = _line_start(number, entry)
        if not counted:
            problems.append(f"{number} has no quoted words of its ledger line (a bare number is refused): add, in the same list item, words from that line between quotation marks, "
                            f"at least {MIN_QUOTE} characters, for example {_example(number, entry)}. The line starts: {start}")
            continue
        for quote in counted:
            if not _appears(_quote_pieces(quote), entry):
                problems.append(f"the words quoted after {number}, \"{quote.strip()[:80]}\", do not appear in that ledger line (a contiguous piece of its decision or of its evidence): "
                                f"quote that line, not another. The line starts: {start}")
    return problems


def brief_problem(brief: str, project: Path) -> str:
    """Return what is missing in the brief of a gated agent (an empty string when the form is right).

    The ledger is always read first: a ledger that is missing, unreadable or malformed refuses the call even when the brief
    has a valid NONE-CHECKED line (D-0158). Every number cited in a Decisions block must be a line that is DECIDED and taken
    by EVE, also when a valid NONE-CHECKED line is present (D-0159); numbers are read without regard to case. Each number must
    be followed, in the same list item, by quoted words that appear in THAT ledger line (D-0166, point 6 option C).
    """
    found = NONE_CHECKED.search(brief)
    missing_file = _none_checked_problem(found.group(1), project) if found else ""
    ledger = project / LEDGER_RELATIVE
    try:
        reader = _load_ledger_reader()
    except Exception as error:
        return f"the ledger reader {LEDGER_SCRIPT} cannot be loaded ({error}), so no decision number can be checked."
    try:
        entries = reader.read_ledger(ledger)
    except FileNotFoundError:
        return f"the decision ledger {LEDGER_RELATIVE} does not exist, so no decision number can be checked."
    except (OSError, ValueError) as error:
        return f"the decision ledger cannot be read ({error}); fix it first."
    if not entries:
        return f"the decision ledger {LEDGER_RELATIVE} holds no decision line, so no decision number can be checked (D-0158: a check that cannot run must not pass)."
    block = _decisions_block(brief)
    cited = [n.upper() for n in DECISION_TOKEN.findall(QUOTE.sub("", block))]
    not_in_ledger = [n for n in cited if n not in entries]
    undecided = reader.not_decided(cited, entries)
    reasons = []
    if not_in_ledger:
        reasons.append("the Decisions block cites " + ", ".join(not_in_ledger) + ", not in the ledger")
    if undecided:
        reasons.append("the Decisions block cites " + ", ".join(f"{n} (status {s})" for n, s in undecided)
                       + ", which Eve has not decided: only a line that is DECIDED and taken by EVE can be quoted (D-0159)")
    if not reasons:
        if cited:
            reasons.extend(_quote_problems(block, entries))
            if not reasons:
                return ""
        elif found and not missing_file:
            return ""
        elif block:
            reasons.append("the Decisions block holds no decision number (D-0001 form)")
        else:
            reasons.append("the brief has no Decisions block" + ("" if found else " and no NONE-CHECKED line"))
    return "; ".join(x for x in (*reasons, missing_file) if x) + "."


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
            if kind not in DECISION_EXEMPT:
                problem = brief_problem(str(tool_input.get("prompt") or ""), project)
                who = kind or "this agent"
                if problem:
                    return refuse(
                        f"Coordinator mode: the brief for {who} must quote the decisions it depends on (M150, D-0156): "
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
